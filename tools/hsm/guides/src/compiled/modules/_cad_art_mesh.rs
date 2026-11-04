//! Guide recipe: `hardware/install-guide/_cad_art_mesh.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("_mesh_payload", rt.import_module("_mesh_payload")?)?;
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    let mod2 = rt.import_module("_occt_color")?;
    e.set("rgba", rt.member("_occt_color", "rgba")?)?;
    let mod3 = rt.import_module("_install_art_mesh")?;
    e.set("_read", rt.member("_install_art_mesh", "_read")?)?;
    // _select
    e.set("_select", {
        let params = vec![
            ("meshes".into(), None, false),
            (
                "keep".into(),
                Some({
                    let params = vec![("name".into(), None, false)];
                    let outer = e.clone();
                    let runtime = rt.clone();
                    Val::function(move |args, kwargs| {
                        let rt = runtime.clone();
                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                        let _frame = rt.frame(&outer);
                        return Ok(Val::Bool(true));
                        Ok(Val::None)
                    })
                }),
                false,
            ),
            ("move".into(), Some(Val::None), true),
            ("colors".into(), Some(Val::None), true),
            ("rename".into(), Some(Val::None), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned4 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("out", assigned4.clone())?;
            for item5 in e.get("meshes")?.iter()? {
                e.set("original", item5)?;
                let assigned6 = {
                    let fun9 = e
                        .get("original")?
                        .get(Val::Str("name".into()))?
                        .attr("split")?;
                    let mut args7 = Vec::new();
                    let mut kw8 = Vec::new();
                    args7.push(Val::Str("/".into()));
                    fun9.call(args7, kw8)?
                }
                .get(Val::Int(0i64))?;
                e.set("name", assigned6.clone())?;
                if unary("not", {
                    let fun12 = e.get("keep")?;
                    let mut args10 = Vec::new();
                    let mut kw11 = Vec::new();
                    args10.push(e.get("name")?);
                    fun12.call(args10, kw11)?
                })?
                .truthy()?
                {
                    continue;
                }
                let assigned13 = {
                    let fun16 = e.get("dict")?;
                    let mut args14 = Vec::new();
                    let mut kw15 = Vec::new();
                    args14.push(e.get("original")?);
                    fun16.call(args14, kw15)?
                };
                e.set("mesh", assigned13.clone())?;
                if {
                    let v17 = e.get("move")?;
                    let v18 = Val::None;
                    Val::Bool(compare("is_not", v17.clone(), v18.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned19 = {
                        let e = e.child();
                        let out20 = Val::list(vec![]);
                        for item21 in {
                            let fun24 = e.get("enumerate")?;
                            let mut args22 = Vec::new();
                            let mut kw23 = Vec::new();
                            args22.push(e.get("mesh")?.get(Val::Str("pos".into()))?);
                            fun24.call(args22, kw23)?
                        }
                        .iter()?
                        {
                            let unpack25 = unpack(item21, 2)?;
                            e.set("i", unpack25[0].clone())?;
                            e.set("v", unpack25[1].clone())?;
                            out20.attr("append")?.call(
                                vec![binary(
                                    "add",
                                    {
                                        let fun28 = e.get("float")?;
                                        let mut args26 = Vec::new();
                                        let mut kw27 = Vec::new();
                                        args26.push(e.get("v")?);
                                        fun28.call(args26, kw27)?
                                    },
                                    e.get("move")?.get(binary(
                                        "mod",
                                        e.get("i")?,
                                        Val::Int(3i64),
                                    )?)?,
                                )?],
                                vec![],
                            )?;
                        }
                        out20
                    };
                    e.get("mesh")?
                        .set(Val::Str("pos".into()), assigned19.clone())?;
                }
                if {
                    let v31 = e.get("colors")?;
                    if v31.truthy()? {
                        {
                            let v29 = e.get("name")?;
                            let v30 = e.get("colors")?;
                            Val::Bool(compare("in", v29.clone(), v30.clone())?.truthy()?)
                        }
                    } else {
                        v31
                    }
                }
                .truthy()?
                {
                    let assigned32 = e.get("colors")?.get(e.get("name")?)?;
                    e.get("mesh")?
                        .set(Val::Str("color".into()), assigned32.clone())?;
                }
                if {
                    let v35 = e.get("rename")?;
                    if v35.truthy()? {
                        {
                            let v33 = e.get("name")?;
                            let v34 = e.get("rename")?;
                            Val::Bool(compare("in", v33.clone(), v34.clone())?.truthy()?)
                        }
                    } else {
                        v35
                    }
                }
                .truthy()?
                {
                    let assigned36 = binary(
                        "add",
                        e.get("rename")?.get(e.get("name")?)?,
                        e.get("original")?
                            .get(Val::Str("name".into()))?
                            .get(Val::Slice {
                                start: Some(
                                    {
                                        let fun39 = e.get("len")?;
                                        let mut args37 = Vec::new();
                                        let mut kw38 = Vec::new();
                                        args37.push(e.get("name")?);
                                        fun39.call(args37, kw38)?
                                    }
                                    .integer()?,
                                ),
                                stop: None,
                                step: 1,
                            })?,
                    )?;
                    e.get("mesh")?
                        .set(Val::Str("name".into()), assigned36.clone())?;
                }
                {
                    let fun42 = e.get("out")?.attr("append")?;
                    let mut args40 = Vec::new();
                    let mut kw41 = Vec::new();
                    args40.push(e.get("mesh")?);
                    fun42.call(args40, kw41)?
                };
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // _color
    e.set("_color", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, Some("values"), None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun45 = e.get("list")?;
                let mut args43 = Vec::new();
                let mut kw44 = Vec::new();
                args43.push(
                    {
                        let fun48 = e.get("rgba")?;
                        let mut args46 = Vec::new();
                        let mut kw47 = Vec::new();
                        args46.push({
                            let mut s = Vec::new();
                            s.extend(e.get("values")?.iter()?);
                            s.push(Val::Float(1.0f64));
                            Val::tuple(s)
                        });
                        args46.push({
                            let d = Val::dict(vec![]);
                            d
                        });
                        fun48.call(args46, kw47)?
                    }
                    .get(Val::Slice {
                        start: None,
                        stop: Some(Val::Int(3i64).integer()?),
                        step: 1,
                    })?,
                );
                fun45.call(args43, kw44)?
            });
            Ok(Val::None)
        })
    })?;
    // _props
    e.set("_props", {
        let params = vec![
            ("numbers".into(), None, false),
            ("colors".into(), None, false),
            ("work".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned49 = binary(
                "truediv",
                e.get("work")?,
                Val::Str("cad-art.numbers.json".into()),
            )?;
            e.set("path", assigned49.clone())?;
            {
                let fun52 = e.get("path")?.attr("write_text")?;
                let mut args50 = Vec::new();
                let mut kw51 = Vec::new();
                args50.push(binary(
                    "add",
                    {
                        let fun55 = e.get("json")?.attr("dumps")?;
                        let mut args53 = Vec::new();
                        let mut kw54 = Vec::new();
                        args53.push({
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("cad_art".into()), e.get("numbers")?)?;
                            d.set(Val::Str("colors".into()), e.get("colors")?)?;
                            d
                        });
                        kw54.push(("sort_keys".into(), Val::Bool(true)));
                        fun55.call(args53, kw54)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun52.call(args50, kw51)?
            };
            {
                let fun58 = e.get("_rust_part")?.attr("run")?;
                let mut args56 = Vec::new();
                let mut kw57 = Vec::new();
                args56.push(Val::Str("tooling".into()));
                args56.push(Val::Str("install-art-props".into()));
                args56.push(e.get("path")?);
                args56.push(e.get("work")?);
                fun58.call(args56, kw57)?
            };
            Ok(Val::None)
        })
    })?;
    // _write
    e.set("_write", {
        let params = vec![
            ("work".into(), None, false),
            ("name".into(), None, false),
            ("meshes".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned59 = binary("truediv", e.get("work")?, {
                let mut str60 = String::new();
                str60.push_str(&format(&e.get("name")?, &String::new())?);
                str60.push_str(".step");
                Val::Str(str60)
            })?;
            e.set("step", assigned59.clone())?;
            {
                let fun63 = e.get("_mesh_payload")?.attr("write")?;
                let mut args61 = Vec::new();
                let mut kw62 = Vec::new();
                args61.push(e.get("meshes")?);
                args61.push({
                    let fun66 = e.get("Path")?;
                    let mut args64 = Vec::new();
                    let mut kw65 = Vec::new();
                    args64.push({
                        let mut str67 = String::new();
                        str67.push_str(&format(&e.get("step")?, &String::new())?);
                        str67.push_str(".mesh");
                        Val::Str(str67)
                    });
                    fun66.call(args64, kw65)?
                });
                fun63.call(args61, kw62)?
            };
            return Ok(e.get("step")?);
            Ok(Val::None)
        })
    })?;
    // _anchors
    e.set("_anchors", {
        let params = vec![
            ("camera".into(), None, false),
            ("target".into(), None, false),
            ("across".into(), None, false),
            ("rise".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer); // unit
            e.set("unit", {
                let params = vec![("v".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned68 = {
                        let fun71 = e.get("math")?.attr("sqrt")?;
                        let mut args69 = Vec::new();
                        let mut kw70 = Vec::new();
                        args69.push({
                            let fun74 = e.get("sum")?;
                            let mut args72 = Vec::new();
                            let mut kw73 = Vec::new();
                            args72.push({
                                let e = e.child();
                                let out75 = Val::list(vec![]);
                                for item76 in e.get("v")?.iter()? {
                                    e.set("x", item76)?;
                                    out75.attr("append")?.call(
                                        vec![binary("mul", e.get("x")?, e.get("x")?)?],
                                        vec![],
                                    )?;
                                }
                                out75
                            });
                            fun74.call(args72, kw73)?
                        });
                        fun71.call(args69, kw70)?
                    };
                    e.set("length", assigned68.clone())?;
                    return Ok({
                        let e = e.child();
                        let out77 = Val::list(vec![]);
                        for item78 in e.get("v")?.iter()? {
                            e.set("x", item78)?;
                            out77.attr("append")?.call(
                                vec![binary("truediv", e.get("x")?, e.get("length")?)?],
                                vec![],
                            )?;
                        }
                        out77
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
                        Val::list(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned79 = {
                let fun82 = e.get("unit")?;
                let mut args80 = Vec::new();
                let mut kw81 = Vec::new();
                args80.push(e.get("camera")?);
                fun82.call(args80, kw81)?
            };
            e.set("view", assigned79.clone())?;
            let assigned83 = {
                let fun86 = e.get("unit")?;
                let mut args84 = Vec::new();
                let mut kw85 = Vec::new();
                args84.push({
                    let fun89 = e.get("cross")?;
                    let mut args87 = Vec::new();
                    let mut kw88 = Vec::new();
                    args87.push(e.get("view")?);
                    args87.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        Val::tuple(s)
                    });
                    fun89.call(args87, kw88)?
                });
                fun86.call(args84, kw85)?
            };
            e.set("right", assigned83.clone())?;
            let assigned90 = {
                let fun93 = e.get("unit")?;
                let mut args91 = Vec::new();
                let mut kw92 = Vec::new();
                args91.push({
                    let fun96 = e.get("cross")?;
                    let mut args94 = Vec::new();
                    let mut kw95 = Vec::new();
                    args94.push(e.get("right")?);
                    args94.push(e.get("view")?);
                    fun96.call(args94, kw95)?
                });
                fun93.call(args91, kw92)?
            };
            e.set("up", assigned90.clone())?;
            return Ok({
                let e = e.child();
                let out97 = Val::list(vec![]);
                for item98 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        s.push(Val::Float(1.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(1.0f64));
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(1.0f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                }
                .iter()?
                {
                    let unpack99 = unpack(item98, 2)?;
                    e.set("a", unpack99[0].clone())?;
                    e.set("b", unpack99[1].clone())?;
                    out97.attr("append")?.call(
                        vec![{
                            let e = e.child();
                            let out100 = Val::list(vec![]);
                            for item101 in {
                                let fun104 = e.get("range")?;
                                let mut args102 = Vec::new();
                                let mut kw103 = Vec::new();
                                args102.push(Val::Int(3i64));
                                fun104.call(args102, kw103)?
                            }
                            .iter()?
                            {
                                e.set("k", item101)?;
                                out100.attr("append")?.call(
                                    vec![binary(
                                        "add",
                                        binary(
                                            "add",
                                            e.get("target")?.get(e.get("k")?)?,
                                            binary(
                                                "mul",
                                                binary("mul", e.get("a")?, e.get("across")?)?,
                                                e.get("right")?.get(e.get("k")?)?,
                                            )?,
                                        )?,
                                        binary(
                                            "mul",
                                            binary("mul", e.get("b")?, e.get("rise")?)?,
                                            e.get("up")?.get(e.get("k")?)?,
                                        )?,
                                    )?],
                                    vec![],
                                )?;
                            }
                            out100
                        }],
                        vec![],
                    )?;
                }
                out97
            });
            Ok(Val::None)
        })
    })?;
    // build_steps
    e.set("build_steps", {
        let params = vec![("art".into(), None, false), ("work".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned105 = {
                let fun108 = e.get("art")?.attr("_load_faucet_module")?;
                let mut args106 = Vec::new();
                let mut kw107 = Vec::new();
                fun108.call(args106, kw107)?
            };
            e.set("fa", assigned105.clone())?;
            let assigned109 = {
                let fun112 = e.get("_read")?;
                let mut args110 = Vec::new();
                let mut kw111 = Vec::new();
                args110.push(binary(
                    "truediv",
                    e.get("art")?.attr("HARDWARE")?,
                    Val::Str("faucet-layout/faucet-assembly.step.mesh".into()),
                )?);
                fun112.call(args110, kw111)?
            };
            e.set("source", assigned109.clone())?;
            let assigned113 = {
                let mut s = Vec::new();
                s.push(Val::Str("westbrass".into()));
                s.push(Val::Str("drain_tube".into()));
                s.push(Val::Str("soda_faucet_tube".into()));
                s.push(Val::Str("tpu_o_ring".into()));
                s.push(Val::Str("flavor_tube_pos_x".into()));
                s.push(Val::Str("flavor_tube_neg_x".into()));
                s.push(Val::Str("lever".into()));
                s.push(Val::Str("above_counter_plate".into()));
                s.push(Val::Str("above_counter_gasket".into()));
                s.push(Val::Str("shell_base".into()));
                s.push(Val::Str("shell_tip".into()));
                s.push(Val::Str("faucet-display-cover-seated".into()));
                s.push(Val::Str("faucet_display".into()));
                s.push(Val::Str("faucet_display_screen".into()));
                Val::set_values(s)
            };
            e.set("above", assigned113.clone())?;
            let assigned114 = {
                let mut s = Vec::new();
                s.push(Val::Str("westbrass".into()));
                s.push(Val::Str("drain_tube".into()));
                s.push(Val::Str("flavor_tube_pos_x".into()));
                s.push(Val::Str("flavor_tube_neg_x".into()));
                Val::set_values(s)
            };
            e.set("clipped_above", assigned114.clone())?;
            let assigned115 = {
                let e = e.child();
                let out116 = Val::dict(vec![]);
                for item117 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("flavor_tube".into()));
                    s.push(Val::Str("flavor_umbilical_tube".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("body", item117)?;
                    for item118 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("pos_x".into()));
                        s.push(Val::Str("neg_x".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("side", item118)?;
                        out116.set(
                            {
                                let mut str119 = String::new();
                                str119.push_str(&format(&e.get("body")?, &String::new())?);
                                str119.push_str("_");
                                str119.push_str(&format(&e.get("side")?, &String::new())?);
                                Val::Str(str119)
                            },
                            e.get("side")?,
                        )?;
                    }
                }
                out116
            };
            e.set("flavors", assigned115.clone())?;
            let assigned120 = {
                let mut s = Vec::new();
                s.extend(e.get("flavors")?.iter()?);
                s.push(Val::Str("soda_umbilical_tube".into()));
                s.push(Val::Str("drain_tube".into()));
                Val::set_values(s)
            };
            e.set("tails", assigned120.clone())?;
            let assigned121 = binary(
                "or",
                binary("or", e.get("above")?, {
                    let fun124 = e.get("set")?;
                    let mut args122 = Vec::new();
                    let mut kw123 = Vec::new();
                    args122.push(e.get("flavors")?);
                    fun124.call(args122, kw123)?
                })?,
                {
                    let mut s = Vec::new();
                    s.push(Val::Str("soda_umbilical_tube".into()));
                    Val::set_values(s)
                },
            )?;
            e.set("mounted", assigned121.clone())?;
            let assigned125 = binary(
                "or",
                binary("or", e.get("tails")?, e.get("clipped_above")?)?,
                {
                    let mut s = Vec::new();
                    s.push(Val::Str("display_signal_ribbon".into()));
                    Val::set_values(s)
                },
            )?;
            e.set("input_names", assigned125.clone())?;
            {
                let fun128 = e.get("_mesh_payload")?.attr("write")?;
                let mut args126 = Vec::new();
                let mut kw127 = Vec::new();
                args126.push({
                    let fun131 = e.get("_select")?;
                    let mut args129 = Vec::new();
                    let mut kw130 = Vec::new();
                    args129.push(e.get("source")?);
                    args129.push(e.get("input_names")?.attr("__contains__")?);
                    fun131.call(args129, kw130)?
                });
                args126.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("faucet-crops.mesh".into()),
                )?);
                fun128.call(args126, kw127)?
            };
            let assigned132 = {
                let e = e.child();
                let out133 = Val::dict(vec![]);
                for item134 in e.get("source")?.iter()? {
                    e.set("m", item134)?;
                    out133.set(
                        {
                            let fun137 = e.get("m")?.get(Val::Str("name".into()))?.attr("split")?;
                            let mut args135 = Vec::new();
                            let mut kw136 = Vec::new();
                            args135.push(Val::Str("/".into()));
                            fun137.call(args135, kw136)?
                        }
                        .get(Val::Int(0i64))?,
                        e.get("m")?.get(Val::Str("color".into()))?,
                    )?;
                }
                out133
            };
            e.set("inherited", assigned132.clone())?;
            let assigned138 = {
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("lever".into()),
                    e.get("inherited")?.get(Val::Str("lever".into()))?,
                )?;
                d.set(Val::Str("counter".into()), {
                    let fun141 = e.get("_color")?;
                    let mut args139 = Vec::new();
                    let mut kw140 = Vec::new();
                    args139.push(Val::Float(0.55f64));
                    args139.push(Val::Float(0.55f64));
                    args139.push(Val::Float(0.58f64));
                    fun141.call(args139, kw140)?
                })?;
                d.set(Val::Str("plate".into()), {
                    let fun144 = e.get("_color")?;
                    let mut args142 = Vec::new();
                    let mut kw143 = Vec::new();
                    args142.push(Val::Float(0.91f64));
                    args142.push(Val::Float(0.92f64));
                    args142.push(Val::Float(0.94f64));
                    fun144.call(args142, kw143)?
                })?;
                d.set(Val::Str("washer".into()), {
                    let fun147 = e.get("_color")?;
                    let mut args145 = Vec::new();
                    let mut kw146 = Vec::new();
                    args145.push(Val::Float(0.82f64));
                    args145.push(Val::Float(0.83f64));
                    args145.push(Val::Float(0.84f64));
                    fun147.call(args145, kw146)?
                })?;
                d.set(Val::Str("nut".into()), {
                    let fun150 = e.get("_color")?;
                    let mut args148 = Vec::new();
                    let mut kw149 = Vec::new();
                    args148.push(Val::Float(0.43f64));
                    args148.push(Val::Float(0.45f64));
                    args148.push(Val::Float(0.48f64));
                    fun150.call(args148, kw149)?
                })?;
                d.set(Val::Str("flavor_a".into()), {
                    let fun153 = e.get("_color")?;
                    let mut args151 = Vec::new();
                    let mut kw152 = Vec::new();
                    args151.push(Val::Float(0.025f64));
                    args151.push(Val::Float(0.027f64));
                    args151.push(Val::Float(0.031f64));
                    fun153.call(args151, kw152)?
                })?;
                d.set(Val::Str("flavor_b".into()), {
                    let fun156 = e.get("_color")?;
                    let mut args154 = Vec::new();
                    let mut kw155 = Vec::new();
                    args154.push(Val::Float(0.2f64));
                    args154.push(Val::Float(0.205f64));
                    args154.push(Val::Float(0.215f64));
                    fun156.call(args154, kw155)?
                })?;
                d.set(Val::Str("signal".into()), {
                    let fun159 = e.get("_color")?;
                    let mut args157 = Vec::new();
                    let mut kw158 = Vec::new();
                    args157.push(Val::Float(0.035f64));
                    args157.push(Val::Float(0.038f64));
                    args157.push(Val::Float(0.043f64));
                    fun159.call(args157, kw158)?
                })?;
                d.set(Val::Str("stripe".into()), {
                    let fun162 = e.get("_color")?;
                    let mut args160 = Vec::new();
                    let mut kw161 = Vec::new();
                    args160.push(Val::Float(0.16f64));
                    args160.push(Val::Float(0.17f64));
                    args160.push(Val::Float(0.19f64));
                    fun162.call(args160, kw161)?
                })?;
                d.set(Val::Str("anchor".into()), {
                    let fun165 = e.get("_color")?;
                    let mut args163 = Vec::new();
                    let mut kw164 = Vec::new();
                    args163.push(Val::Float(0.95f64));
                    args163.push(Val::Float(0.04f64));
                    args163.push(Val::Float(0.82f64));
                    fun165.call(args163, kw164)?
                })?;
                d
            };
            e.set("colors", assigned138.clone())?;
            let assigned166 = {
                let e = e.child();
                let out167 = Val::dict(vec![]);
                for item168 in {
                    let fun171 = e.get("flavors")?.attr("items")?;
                    let mut args169 = Vec::new();
                    let mut kw170 = Vec::new();
                    fun171.call(args169, kw170)?
                }
                .iter()?
                {
                    let unpack172 = unpack(item168, 2)?;
                    e.set("name", unpack172[0].clone())?;
                    e.set("side", unpack172[1].clone())?;
                    out167.set(
                        e.get("name")?,
                        e.get("colors")?.get(
                            if {
                                let v173 = e.get("side")?;
                                let v174 = Val::Str("pos_x".into());
                                Val::Bool(compare("eq", v173.clone(), v174.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                Val::Str("flavor_a".into())
                            } else {
                                Val::Str("flavor_b".into())
                            },
                        )?,
                    )?;
                }
                out167
            };
            e.set("flavor_colors", assigned166.clone())?;
            let assigned175 = binary(
                "add",
                binary(
                    "add",
                    unary("neg", e.get("fa")?.attr("shank_length")?)?,
                    Val::Float(5.0f64),
                )?,
                Val::Float(1.5f64),
            )?;
            e.set("captive", assigned175.clone())?;
            let assigned176 = binary(
                "sub",
                e.get("fa")?.attr("countertop_bottom_z")?,
                e.get("fa")?.attr("under_counter_plate_thickness")?,
            )?;
            e.set("final", assigned176.clone())?;
            let assigned177 = {
                let mut s = Vec::new();
                s.push({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("name".into()), Val::Str("faucet-user".into()))?;
                    d.set(Val::Str("kind".into()), Val::Str("user".into()))?;
                    d.set(Val::Str("pressed".into()), Val::Bool(false))?;
                    d
                });
                s.push({
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("name".into()),
                        Val::Str("faucet-user-pressed".into()),
                    )?;
                    d.set(Val::Str("kind".into()), Val::Str("user".into()))?;
                    d.set(Val::Str("pressed".into()), Val::Bool(true))?;
                    d
                });
                s.push({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("name".into()), Val::Str("faucet-full".into()))?;
                    d.set(Val::Str("kind".into()), Val::Str("full".into()))?;
                    d
                });
                s.push({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("name".into()), Val::Str("mount-drop".into()))?;
                    d.set(Val::Str("kind".into()), Val::Str("mount".into()))?;
                    d.set(Val::Str("lift".into()), Val::Float(35.0f64))?;
                    d.set(
                        Val::Str("washer".into()),
                        binary("add", e.get("captive")?, Val::Float(35.0f64))?,
                    )?;
                    d
                });
                s.extend(
                    {
                        let e = e.child();
                        let out178 = Val::list(vec![]);
                        for item179 in {
                            let mut s = Vec::new();
                            s.push(Val::Str("mount-seated".into()));
                            s.push(Val::Str("mount-lowered-clean".into()));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("name", item179)?;
                            out178.attr("append")?.call(
                                vec![{
                                    let d = Val::dict(vec![]);
                                    d.set(Val::Str("name".into()), e.get("name")?)?;
                                    d.set(Val::Str("kind".into()), Val::Str("mount".into()))?;
                                    d.set(Val::Str("lift".into()), Val::Float(0.0f64))?;
                                    d.set(Val::Str("washer".into()), e.get("captive")?)?;
                                    d
                                }],
                                vec![],
                            )?;
                        }
                        out178
                    }
                    .iter()?,
                );
                s.extend(
                    {
                        let e = e.child();
                        let out180 = Val::list(vec![]);
                        for item181 in {
                            let mut s = Vec::new();
                            s.push(Val::Str("mount-slide".into()));
                            s.push(Val::Str("mount-slide-clean".into()));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("name", item181)?;
                            out180.attr("append")?.call(
                                vec![{
                                    let d = Val::dict(vec![]);
                                    d.set(Val::Str("name".into()), e.get("name")?)?;
                                    d.set(Val::Str("kind".into()), Val::Str("mount".into()))?;
                                    d.set(Val::Str("lift".into()), Val::Float(0.0f64))?;
                                    d.set(Val::Str("washer".into()), e.get("captive")?)?;
                                    d.set(
                                        Val::Str("plate".into()),
                                        e.get("art")?.attr("PLATE_APPROACH_X")?,
                                    )?;
                                    d
                                }],
                                vec![],
                            )?;
                        }
                        out180
                    }
                    .iter()?,
                );
                s.extend(
                    {
                        let e = e.child();
                        let out182 = Val::list(vec![]);
                        for item183 in {
                            let mut s = Vec::new();
                            s.push(Val::Str("mount-tighten".into()));
                            s.push(Val::Str("mount-final-clean".into()));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("name", item183)?;
                            out182.attr("append")?.call(
                                vec![{
                                    let d = Val::dict(vec![]);
                                    d.set(Val::Str("name".into()), e.get("name")?)?;
                                    d.set(Val::Str("kind".into()), Val::Str("mount".into()))?;
                                    d.set(Val::Str("lift".into()), Val::Float(0.0f64))?;
                                    d.set(Val::Str("washer".into()), e.get("final")?)?;
                                    d.set(Val::Str("plate".into()), Val::Float(0.0f64))?;
                                    d
                                }],
                                vec![],
                            )?;
                        }
                        out182
                    }
                    .iter()?,
                );
                s.push({
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("name".into()),
                        Val::Str("mount-under-slide-clean".into()),
                    )?;
                    d.set(Val::Str("kind".into()), Val::Str("under".into()))?;
                    d.set(Val::Str("washer".into()), e.get("captive")?)?;
                    d.set(
                        Val::Str("plate".into()),
                        e.get("art")?.attr("PLATE_APPROACH_X")?,
                    )?;
                    d
                });
                s.push({
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("name".into()),
                        Val::Str("mount-under-tighten-clean".into()),
                    )?;
                    d.set(Val::Str("kind".into()), Val::Str("under".into()))?;
                    d.set(Val::Str("washer".into()), e.get("final")?)?;
                    d.set(Val::Str("plate".into()), Val::Float(0.0f64))?;
                    d
                });
                Val::list(s)
            };
            e.set("scenes", assigned177.clone())?;
            let assigned184 = e.get("fa")?.attr("faucet_shell")?;
            e.set("shell", assigned184.clone())?;
            let assigned185 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("kind".into()), Val::Str("faucet".into()))?;
                d.set(Val::Str("scenes".into()), e.get("scenes")?)?;
                d.set(Val::Str("input".into()), {
                    let fun188 = e.get("str")?;
                    let mut args186 = Vec::new();
                    let mut kw187 = Vec::new();
                    args186.push(binary(
                        "truediv",
                        e.get("work")?,
                        Val::Str("faucet-crops.mesh".into()),
                    )?);
                    fun188.call(args186, kw187)?
                })?;
                d.set(Val::Str("counter".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("fa")?.attr("countertop_bottom_z")?);
                    s.push(e.get("fa")?.attr("countertop_thickness")?);
                    s.push(e.get("fa")?.attr("countertop_hole_center_y")?);
                    s.push(e.get("fa")?.attr("hole_radius")?);
                    s.push(e.get("art")?.attr("UNDER_COUNTERTOP_X")?);
                    s.push(e.get("art")?.attr("UNDER_COUNTERTOP_Y")?);
                    Val::list(s)
                })?;
                d.set(
                    Val::Str("top_z".into()),
                    e.get("fa")?.attr("countertop_top_z")?,
                )?;
                d.set(Val::Str("lever".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("fa")?.attr("plateau_z")?);
                    s.push(e.get("fa")?.attr("port_center_depth")?);
                    s.push(e.get("fa")?.attr("soda_faucet_tube_r")?);
                    s.push(e.get("fa")?.attr("lever_pivot_y")?);
                    s.push(e.get("fa")?.attr("lever_pivot_z")?);
                    s.push(e.get("fa")?.attr("lever_press_angle_deg")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("signal_legs".into()), {
                    let e = e.child();
                    let out189 = Val::list(vec![]);
                    for item190 in {
                        let fun193 = e.get("fa")?.attr("_step_legs")?;
                        let mut args191 = Vec::new();
                        let mut kw192 = Vec::new();
                        args191.push(unary("pos", Val::Int(1i64))?);
                        args191.push(unary("neg", Val::Float(123.0f64))?);
                        fun193.call(args191, kw192)?
                    }
                    .iter()?
                    {
                        let unpack194 = item190.iter()?;
                        ensure!(unpack194.len() >= 1, "not enough values to unpack");
                        e.set("kind", unpack194[0].clone())?;
                        e.set(
                            "points",
                            Val::list(unpack194[1..unpack194.len() - 0].to_vec()),
                        )?;
                        out189.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(e.get("kind")?, {
                                    let fun197 = e.get("list")?;
                                    let mut args195 = Vec::new();
                                    let mut kw196 = Vec::new();
                                    args195.push(e.get("points")?);
                                    fun197.call(args195, kw196)?
                                })?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out189
                })?;
                d.set(Val::Str("signal_origin".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("shell")?.attr("signal_lower_exit_x")?);
                    s.push(e.get("shell")?.attr("signal_lower_exit_y")?);
                    s.push(e.get("fa")?.attr("under_counter_plate_bottom_z")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("signal_size".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("shell")?.attr("signal_ribbon_max_width")?);
                    s.push(e.get("shell")?.attr("signal_ribbon_max_depth")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("frame".into()), {
                    let fun200 = e.get("_anchors")?;
                    let mut args198 = Vec::new();
                    let mut kw199 = Vec::new();
                    args198.push(e.get("art")?.attr("MOUNT_CAM")?);
                    args198.push(e.get("art")?.attr("MOUNT_TARGET")?);
                    args198.push(Val::Float(118.0f64));
                    args198.push(Val::Float(235.0f64));
                    fun200.call(args198, kw199)?
                })?;
                d.set(Val::Str("under_frame".into()), {
                    let fun203 = e.get("_anchors")?;
                    let mut args201 = Vec::new();
                    let mut kw202 = Vec::new();
                    args201.push(e.get("art")?.attr("UNDER_MOUNT_CAM")?);
                    args201.push(e.get("art")?.attr("UNDER_MOUNT_TARGET")?);
                    args201.push(Val::Float(137.0f64));
                    args201.push(Val::Float(58.0f64));
                    fun203.call(args201, kw202)?
                })?;
                d
            };
            e.set("numbers", assigned185.clone())?;
            {
                let fun206 = e.get("_props")?;
                let mut args204 = Vec::new();
                let mut kw205 = Vec::new();
                args204.push(e.get("numbers")?);
                args204.push(e.get("colors")?);
                args204.push(e.get("work")?);
                fun206.call(args204, kw205)?
            };
            let assigned207 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("out", assigned207.clone())?;
            for item208 in e.get("scenes")?.iter()? {
                e.set("row", item208)?;
                let assigned209 = {
                    let mut s = Vec::new();
                    s.push(e.get("row")?.get(Val::Str("name".into()))?);
                    s.push(e.get("row")?.get(Val::Str("kind".into()))?);
                    Val::tuple(s)
                };
                let unpack210 = unpack(assigned209.clone(), 2)?;
                e.set("name", unpack210[0].clone())?;
                e.set("kind", unpack210[1].clone())?;
                let assigned211 = {
                    let fun214 = e.get("_read")?;
                    let mut args212 = Vec::new();
                    let mut kw213 = Vec::new();
                    args212.push(binary("truediv", e.get("work")?, {
                        let mut str215 = String::new();
                        str215.push_str(&format(&e.get("name")?, &String::new())?);
                        str215.push_str(".props.mesh");
                        Val::Str(str215)
                    })?);
                    fun214.call(args212, kw213)?
                };
                e.set("meshes", assigned211.clone())?;
                if {
                    let v216 = e.get("kind")?;
                    let v217 = Val::Str("full".into());
                    Val::Bool(compare("eq", v216.clone(), v217.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.set("meshes", binary("add", e.get("meshes")?, e.get("source")?)?)?;
                } else {
                    if {
                        let v218 = e.get("kind")?;
                        let v219 = Val::Str("user".into());
                        Val::Bool(compare("eq", v218.clone(), v219.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.set(
                            "meshes",
                            binary("add", e.get("meshes")?, {
                                let fun222 = e.get("_select")?;
                                let mut args220 = Vec::new();
                                let mut kw221 = Vec::new();
                                args220.push(e.get("source")?);
                                args220.push({
                                    let params = vec![("body".into(), None, false)];
                                    let outer = e.clone();
                                    let runtime = rt.clone();
                                    Val::function(move |args, kwargs| {
                                        let rt = runtime.clone();
                                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                                        let _frame = rt.frame(&outer);
                                        return Ok({
                                            let v223 = e.get("body")?;
                                            let v224 = binary(
                                                "sub",
                                                binary(
                                                    "sub",
                                                    e.get("above")?,
                                                    e.get("clipped_above")?,
                                                )?,
                                                {
                                                    let mut s = Vec::new();
                                                    s.push(Val::Str("lever".into()));
                                                    Val::set_values(s)
                                                },
                                            )?;
                                            Val::Bool(
                                                compare("in", v223.clone(), v224.clone())?
                                                    .truthy()?,
                                            )
                                        });
                                        Ok(Val::None)
                                    })
                                });
                                fun222.call(args220, kw221)?
                            })?,
                        )?;
                    } else {
                        if {
                            let v225 = e.get("kind")?;
                            let v226 = Val::Str("mount".into());
                            Val::Bool(compare("eq", v225.clone(), v226.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            e.set(
                                "meshes",
                                binary("add", e.get("meshes")?, {
                                    let fun229 = e.get("_select")?;
                                    let mut args227 = Vec::new();
                                    let mut kw228 = Vec::new();
                                    args227.push(e.get("source")?);
                                    args227.push({
                                        let params = vec![("body".into(), None, false)];
                                        let outer = e.clone();
                                        let runtime = rt.clone();
                                        Val::function(move |args, kwargs| {
                                            let rt = runtime.clone();
                                            let e =
                                                bind(&outer, &params, args, kwargs, None, None)?;
                                            let _frame = rt.frame(&outer);
                                            return Ok({
                                                let v230 = e.get("body")?;
                                                let v231 = binary(
                                                    "sub",
                                                    binary(
                                                        "sub",
                                                        e.get("mounted")?,
                                                        e.get("tails")?,
                                                    )?,
                                                    {
                                                        let mut s = Vec::new();
                                                        s.push(Val::Str("lever".into()));
                                                        Val::set_values(s)
                                                    },
                                                )?;
                                                Val::Bool(
                                                    compare("in", v230.clone(), v231.clone())?
                                                        .truthy()?,
                                                )
                                            });
                                            Ok(Val::None)
                                        })
                                    });
                                    kw228.push(("move".into(), {
                                        let mut s = Vec::new();
                                        s.push(Val::Float(0.0f64));
                                        s.push(Val::Float(0.0f64));
                                        s.push(e.get("row")?.get(Val::Str("lift".into()))?);
                                        Val::tuple(s)
                                    }));
                                    kw228.push(("colors".into(), e.get("flavor_colors")?));
                                    fun229.call(args227, kw228)?
                                })?,
                            )?;
                        }
                    }
                }
                if {
                    let v232 = Val::Str("plate".into());
                    let v233 = e.get("row")?;
                    Val::Bool(compare("in", v232.clone(), v233.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned234 = if {
                        let v235 = e.get("kind")?;
                        let v236 = Val::Str("under".into());
                        Val::Bool(compare("eq", v235.clone(), v236.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        if e.get("row")?.get(Val::Str("plate".into()))?.truthy()? {
                            Val::Str("under-open-plate".into())
                        } else {
                            Val::Str("under-seated-plate".into())
                        }
                    } else {
                        Val::Str("under_counter_plate".into())
                    };
                    e.set("plate_name", assigned234.clone())?;
                    e.set(
                        "meshes",
                        binary("add", e.get("meshes")?, {
                            let fun239 = e.get("_select")?;
                            let mut args237 = Vec::new();
                            let mut kw238 = Vec::new();
                            args237.push(e.get("source")?);
                            args237.push({
                                let params = vec![("body".into(), None, false)];
                                let outer = e.clone();
                                let runtime = rt.clone();
                                Val::function(move |args, kwargs| {
                                    let rt = runtime.clone();
                                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                                    let _frame = rt.frame(&outer);
                                    return Ok({
                                        let v240 = e.get("body")?;
                                        let v241 = Val::Str("under_counter_plate".into());
                                        Val::Bool(
                                            compare("eq", v240.clone(), v241.clone())?.truthy()?,
                                        )
                                    });
                                    Ok(Val::None)
                                })
                            });
                            kw238.push(("move".into(), {
                                let mut s = Vec::new();
                                s.push(e.get("row")?.get(Val::Str("plate".into()))?);
                                s.push(Val::Float(0.0f64));
                                s.push(Val::Float(0.0f64));
                                Val::tuple(s)
                            }));
                            kw238.push(("colors".into(), {
                                let d = Val::dict(vec![]);
                                d.set(
                                    Val::Str("under_counter_plate".into()),
                                    e.get("colors")?.get(Val::Str("plate".into()))?,
                                )?;
                                d
                            }));
                            kw238.push(("rename".into(), {
                                let d = Val::dict(vec![]);
                                d.set(
                                    Val::Str("under_counter_plate".into()),
                                    e.get("plate_name")?,
                                )?;
                                d
                            }));
                            fun239.call(args237, kw238)?
                        })?,
                    )?;
                }
                let assigned242 = {
                    let fun245 = e.get("_write")?;
                    let mut args243 = Vec::new();
                    let mut kw244 = Vec::new();
                    args243.push(e.get("work")?);
                    args243.push(e.get("name")?);
                    args243.push(e.get("meshes")?);
                    fun245.call(args243, kw244)?
                };
                e.get("out")?.set(e.get("name")?, assigned242.clone())?;
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // build_connection_steps
    e.set("build_connection_steps", {
        let params = vec![("art".into(), None, false), ("work".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned246 = {
                let fun249 = e.get("json")?.attr("loads")?;
                let mut args247 = Vec::new();
                let mut kw248 = Vec::new();
                args247.push({
                    let fun252 = e.get("art")?.attr("MACHINE_FACTS")?.attr("read_text")?;
                    let mut args250 = Vec::new();
                    let mut kw251 = Vec::new();
                    fun252.call(args250, kw251)?
                });
                fun249.call(args247, kw248)?
            };
            e.set("facts", assigned246.clone())?;
            let assigned253 = {
                let mut s = Vec::new();
                s.push(Val::Str("c14-inlet".into()));
                s.push(Val::Str("keystone-jack".into()));
                s.push(Val::Str("co2-inlet".into()));
                s.push(Val::Str("bulkhead-water".into()));
                s.push(Val::Str("bulkhead-flavor-a".into()));
                s.push(Val::Str("bulkhead-flavor-b".into()));
                s.push(Val::Str("bulkhead-carb".into()));
                s.push(Val::Str("bulkhead-drain".into()));
                s.push(Val::Str("funnel".into()));
                s.push(Val::Str("nameplate".into()));
                s.push(Val::Str("nameplate-ink".into()));
                s.push(Val::Str("enclosure-back-bottom".into()));
                s.push(Val::Str("enclosure-back-top".into()));
                Val::set_values(s)
            };
            e.set("keep", assigned253.clone())?;
            let assigned254 = {
                let fun257 = e.get("_select")?;
                let mut args255 = Vec::new();
                let mut kw256 = Vec::new();
                args255.push({
                    let fun260 = e.get("_read")?;
                    let mut args258 = Vec::new();
                    let mut kw259 = Vec::new();
                    args258.push(e.get("art")?.attr("MACHINE_MESH")?);
                    fun260.call(args258, kw259)?
                });
                args255.push({
                    let params = vec![("name".into(), None, false)];
                    let outer = e.clone();
                    let runtime = rt.clone();
                    Val::function(move |args, kwargs| {
                        let rt = runtime.clone();
                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                        let _frame = rt.frame(&outer);
                        return Ok({
                            let v264 = {
                                let v265 = e.get("name")?;
                                let v266 = e.get("keep")?;
                                Val::Bool(compare("in", v265.clone(), v266.clone())?.truthy()?)
                            };
                            if v264.truthy()? {
                                v264
                            } else {
                                {
                                    let fun263 = e.get("name")?.attr("startswith")?;
                                    let mut args261 = Vec::new();
                                    let mut kw262 = Vec::new();
                                    args261.push(Val::Str("bulkhead-ring-".into()));
                                    fun263.call(args261, kw262)?
                                }
                            }
                        });
                        Ok(Val::None)
                    })
                });
                fun257.call(args255, kw256)?
            };
            e.set("rear", assigned254.clone())?;
            let assigned267 = binary("sub", e.get("keep")?, {
                let e = e.child();
                let out268 = Val::set_values(vec![]);
                for item269 in e.get("rear")?.iter()? {
                    e.set("entry", item269)?;
                    out268.attr("add")?.call(
                        vec![
                            {
                                let fun272 = e
                                    .get("entry")?
                                    .get(Val::Str("name".into()))?
                                    .attr("split")?;
                                let mut args270 = Vec::new();
                                let mut kw271 = Vec::new();
                                args270.push(Val::Str("/".into()));
                                fun272.call(args270, kw271)?
                            }
                            .get(Val::Int(0i64))?,
                        ],
                        vec![],
                    )?;
                }
                out268
            })?;
            e.set("missing", assigned267.clone())?;
            if e.get("missing")?.truthy()? {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun275 = e.get("RuntimeError")?;
                        let mut args273 = Vec::new();
                        let mut kw274 = Vec::new();
                        args273.push({
                            let mut str276 = String::new();
                            str276.push_str(&format(
                                &e.get("art")?.attr("MACHINE_MESH")?.attr("name")?,
                                &String::new(),
                            )?);
                            str276.push_str(" has no ");
                            str276.push_str(&format(
                                &{
                                    let fun279 = e.get("sorted")?;
                                    let mut args277 = Vec::new();
                                    let mut kw278 = Vec::new();
                                    args277.push(e.get("missing")?);
                                    fun279.call(args277, kw278)?
                                },
                                &String::new(),
                            )?);
                            str276.push_str(" for the rear scene");
                            Val::Str(str276)
                        });
                        fun275.call(args273, kw274)?
                    })?
                );
            }
            let assigned280 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("tap".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Str("bulkhead-water".into()));
                    s.push(Val::Str("outboard".into()));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("carb".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Str("bulkhead-carb".into()));
                    s.push(Val::Str("tube-out".into()));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("co2".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Str("gas-regulator".into()));
                    s.push(Val::Str("outboard".into()));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("flavor-a".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Str("bulkhead-flavor-a".into()));
                    s.push(Val::Str("tube-out".into()));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("flavor-b".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Str("bulkhead-flavor-b".into()));
                    s.push(Val::Str("tube-out".into()));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("drain".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Str("bulkhead-drain".into()));
                    s.push(Val::Str("outboard".into()));
                    Val::tuple(s)
                })?;
                d
            };
            e.set("keys", assigned280.clone())?;
            let assigned281 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("tap".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(60.0f64))?);
                    s.push(Val::Float(322.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("co2".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(40.0f64))?);
                    s.push(Val::Float(322.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("carb".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(50.0f64))?);
                    s.push(Val::Float(312.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("flavor-a".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(40.0f64))?);
                    s.push(Val::Float(302.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("flavor-b".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(60.0f64))?);
                    s.push(Val::Float(302.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("drain".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(50.0f64))?);
                    s.push(Val::Float(292.0f64));
                    Val::tuple(s)
                })?;
                d
            };
            e.set("pack", assigned281.clone())?;
            let assigned282 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("tap".into()), Val::Str("water".into()))?;
                d.set(Val::Str("carb".into()), Val::Str("carb".into()))?;
                d.set(Val::Str("co2".into()), Val::Str("co2".into()))?;
                d.set(Val::Str("flavor-a".into()), Val::Str("flavor".into()))?;
                d.set(Val::Str("flavor-b".into()), Val::Str("flavor".into()))?;
                d.set(Val::Str("drain".into()), Val::Str("drain".into()))?;
                d
            };
            e.set("fluids", assigned282.clone())?;
            let assigned283 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("tap".into()), {
                    let fun286 = e.get("_color")?;
                    let mut args284 = Vec::new();
                    let mut kw285 = Vec::new();
                    args284.push(Val::Float(0.82f64));
                    args284.push(Val::Float(0.84f64));
                    args284.push(Val::Float(0.87f64));
                    fun286.call(args284, kw285)?
                })?;
                d.set(Val::Str("drain".into()), {
                    let fun289 = e.get("_color")?;
                    let mut args287 = Vec::new();
                    let mut kw288 = Vec::new();
                    args287.push(Val::Float(0.82f64));
                    args287.push(Val::Float(0.84f64));
                    args287.push(Val::Float(0.87f64));
                    fun289.call(args287, kw288)?
                })?;
                d.set(Val::Str("carb".into()), {
                    let fun292 = e.get("_color")?;
                    let mut args290 = Vec::new();
                    let mut kw291 = Vec::new();
                    args290.push(Val::Float(0.035f64));
                    args290.push(Val::Float(0.31f64));
                    args290.push(Val::Float(0.82f64));
                    fun292.call(args290, kw291)?
                })?;
                d.set(Val::Str("co2".into()), {
                    let fun295 = e.get("_color")?;
                    let mut args293 = Vec::new();
                    let mut kw294 = Vec::new();
                    args293.push(Val::Float(0.67f64));
                    args293.push(Val::Float(0.042f64));
                    args293.push(Val::Float(0.042f64));
                    fun295.call(args293, kw294)?
                })?;
                d.set(Val::Str("flavor-a".into()), {
                    let fun298 = e.get("_color")?;
                    let mut args296 = Vec::new();
                    let mut kw297 = Vec::new();
                    args296.push(Val::Float(0.025f64));
                    args296.push(Val::Float(0.027f64));
                    args296.push(Val::Float(0.031f64));
                    fun298.call(args296, kw297)?
                })?;
                d.set(Val::Str("flavor-b".into()), {
                    let fun301 = e.get("_color")?;
                    let mut args299 = Vec::new();
                    let mut kw300 = Vec::new();
                    args299.push(Val::Float(0.115f64));
                    args299.push(Val::Float(0.12f64));
                    args299.push(Val::Float(0.13f64));
                    fun301.call(args299, kw300)?
                })?;
                d.set(Val::Str("signal".into()), {
                    let fun304 = e.get("_color")?;
                    let mut args302 = Vec::new();
                    let mut kw303 = Vec::new();
                    args302.push(Val::Float(0.035f64));
                    args302.push(Val::Float(0.038f64));
                    args302.push(Val::Float(0.043f64));
                    fun304.call(args302, kw303)?
                })?;
                d.set(Val::Str("stripe".into()), {
                    let fun307 = e.get("_color")?;
                    let mut args305 = Vec::new();
                    let mut kw306 = Vec::new();
                    args305.push(Val::Float(0.16f64));
                    args305.push(Val::Float(0.17f64));
                    args305.push(Val::Float(0.19f64));
                    fun307.call(args305, kw306)?
                })?;
                d.set(Val::Str("plug".into()), {
                    let fun310 = e.get("_color")?;
                    let mut args308 = Vec::new();
                    let mut kw309 = Vec::new();
                    args308.push(Val::Float(0.72f64));
                    args308.push(Val::Float(0.74f64));
                    args308.push(Val::Float(0.78f64));
                    fun310.call(args308, kw309)?
                })?;
                d.set(Val::Str("latch".into()), {
                    let fun313 = e.get("_color")?;
                    let mut args311 = Vec::new();
                    let mut kw312 = Vec::new();
                    args311.push(Val::Float(0.86f64));
                    args311.push(Val::Float(0.87f64));
                    args311.push(Val::Float(0.89f64));
                    fun313.call(args311, kw312)?
                })?;
                d.set(Val::Str("gold".into()), {
                    let fun316 = e.get("_color")?;
                    let mut args314 = Vec::new();
                    let mut kw315 = Vec::new();
                    args314.push(Val::Float(0.73f64));
                    args314.push(Val::Float(0.49f64));
                    args314.push(Val::Float(0.14f64));
                    fun316.call(args314, kw315)?
                })?;
                d
            };
            e.set("colors", assigned283.clone())?;
            let assigned317 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                Val::tuple(s)
            };
            let unpack318 = unpack(assigned317.clone(), 2)?;
            e.set("tubes", unpack318[0].clone())?;
            e.set("collars", unpack318[1].clone())?;
            for item319 in {
                let fun362 = e.get("keys")?.attr("items")?;
                let mut args360 = Vec::new();
                let mut kw361 = Vec::new();
                fun362.call(args360, kw361)?
            }
            .iter()?
            {
                let unpack363 = unpack(item319, 2)?;
                e.set("which", unpack363[0].clone())?;
                let unpack364 = unpack(unpack363[1].clone(), 2)?;
                e.set("body", unpack364[0].clone())?;
                e.set("port", unpack364[1].clone())?;
                let assigned320 = e
                    .get("facts")?
                    .get(Val::Str("card_ports".into()))?
                    .get(e.get("body")?)?
                    .get(e.get("port")?)?;
                e.set("station", assigned320.clone())?;
                let assigned321 = e.get("station")?.get(Val::Str("pos".into()))?;
                let unpack322 = unpack(assigned321.clone(), 3)?;
                e.set("x", unpack322[0].clone())?;
                e.set("y", unpack322[1].clone())?;
                e.set("z", unpack322[2].clone())?;
                let assigned323 = e.get("pack")?.get(e.get("which")?)?;
                let unpack324 = unpack(assigned323.clone(), 2)?;
                e.set("px", unpack324[0].clone())?;
                e.set("pz", unpack324[1].clone())?;
                {
                    let fun327 = e.get("tubes")?.attr("append")?;
                    let mut args325 = Vec::new();
                    let mut kw326 = Vec::new();
                    args325.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("name".into()), e.get("which")?)?;
                        d.set(
                            Val::Str("diameter".into()),
                            e.get("station")?.get(Val::Str("diam".into()))?,
                        )?;
                        d.set(Val::Str("points".into()), {
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("x")?);
                                s.push(e.get("y")?);
                                s.push(e.get("z")?);
                                Val::list(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("x")?);
                                s.push(Val::Float(560.0f64));
                                s.push(e.get("z")?);
                                Val::list(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("x")?);
                                s.push(Val::Float(578.0f64));
                                s.push(e.get("z")?);
                                Val::list(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary(
                                    "truediv",
                                    binary(
                                        "add",
                                        binary("mul", Val::Int(2i64), e.get("x")?)?,
                                        e.get("px")?,
                                    )?,
                                    Val::Float(3.0f64),
                                )?);
                                s.push(Val::Float(598.0f64));
                                s.push(binary(
                                    "truediv",
                                    binary(
                                        "add",
                                        binary("mul", Val::Int(2i64), e.get("z")?)?,
                                        e.get("pz")?,
                                    )?,
                                    Val::Float(3.0f64),
                                )?);
                                Val::list(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("px")?);
                                s.push(Val::Float(626.0f64));
                                s.push(e.get("pz")?);
                                Val::list(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("px")?);
                                s.push(Val::Float(940.0f64));
                                s.push(e.get("pz")?);
                                Val::list(s)
                            });
                            Val::list(s)
                        })?;
                        d
                    });
                    fun327.call(args325, kw326)?
                };
                let assigned328 = if {
                    let v329 = e.get("which")?;
                    let v330 = Val::Str("tap".into());
                    Val::Bool(compare("eq", v329.clone(), v330.clone())?.truthy()?)
                }
                .truthy()?
                {
                    Val::Str("water".into())
                } else {
                    e.get("which")?
                };
                e.set("station_name", assigned328.clone())?;
                let assigned331 = {
                    let mut str332 = String::new();
                    str332.push_str("tube-collar-");
                    str332.push_str(&format(&e.get("station_name")?, &String::new())?);
                    Val::Str(str332)
                };
                e.set("original", assigned331.clone())?;
                let assigned333 = e.get("fluids")?.get(e.get("which")?)?;
                e.set("fluid", assigned333.clone())?;
                let assigned334 = {
                    let d = Val::dict(vec![]);
                    d.set(e.get("original")?, {
                        let fun337 = e.get("_color")?;
                        let mut args335 = Vec::new();
                        let mut kw336 = Vec::new();
                        args335.extend(
                            {
                                let e = e.child();
                                let out338 = Val::list(vec![]);
                                for item339 in {
                                    let fun342 = e.get("art")?.attr("_rear")?.attr("chip_color")?;
                                    let mut args340 = Vec::new();
                                    let mut kw341 = Vec::new();
                                    args340.push(e.get("fluid")?);
                                    fun342.call(args340, kw341)?
                                }
                                .iter()?
                                {
                                    e.set("c", item339)?;
                                    out338.attr("append")?.call(
                                        vec![binary("truediv", e.get("c")?, Val::Float(255.0f64))?],
                                        vec![],
                                    )?;
                                }
                                out338
                            }
                            .iter()?,
                        );
                        fun337.call(args335, kw336)?
                    })?;
                    d.set(
                        binary("add", e.get("original")?, Val::Str("-word".into()))?,
                        {
                            let fun345 = e.get("_color")?;
                            let mut args343 = Vec::new();
                            let mut kw344 = Vec::new();
                            args343.extend(
                                {
                                    let e = e.child();
                                    let out346 = Val::list(vec![]);
                                    for item347 in {
                                        let fun350 =
                                            e.get("art")?.attr("_rear")?.attr("word_color")?;
                                        let mut args348 = Vec::new();
                                        let mut kw349 = Vec::new();
                                        args348.push(e.get("fluid")?);
                                        fun350.call(args348, kw349)?
                                    }
                                    .iter()?
                                    {
                                        e.set("c", item347)?;
                                        out346.attr("append")?.call(
                                            vec![binary(
                                                "truediv",
                                                e.get("c")?,
                                                Val::Float(255.0f64),
                                            )?],
                                            vec![],
                                        )?;
                                    }
                                    out346
                                }
                                .iter()?,
                            );
                            fun345.call(args343, kw344)?
                        },
                    )?;
                    d
                };
                e.set("collar_colors", assigned334.clone())?;
                e.set(
                    "collars",
                    binary("add", e.get("collars")?, {
                        let fun353 = e.get("_select")?;
                        let mut args351 = Vec::new();
                        let mut kw352 = Vec::new();
                        args351.push({
                            let fun356 = e.get("_read")?;
                            let mut args354 = Vec::new();
                            let mut kw355 = Vec::new();
                            args354.push(binary(
                                "truediv",
                                e.get("art")?.attr("TUBE_COLLAR_DIR")?,
                                {
                                    let mut str357 = String::new();
                                    str357.push_str(&format(&e.get("original")?, &String::new())?);
                                    str357.push_str(".step.mesh");
                                    Val::Str(str357)
                                },
                            )?);
                            fun356.call(args354, kw355)?
                        });
                        kw352.push(("move".into(), {
                            let mut s = Vec::new();
                            s.push(e.get("x")?);
                            s.push(binary("add", e.get("y")?, Val::Float(47.5f64))?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        }));
                        kw352.push(("colors".into(), e.get("collar_colors")?));
                        kw352.push(("rename".into(), {
                            let d = Val::dict(vec![]);
                            d.set(e.get("original")?, {
                                let mut str358 = String::new();
                                str358.push_str("wall-end-collar-");
                                str358.push_str(&format(&e.get("which")?, &String::new())?);
                                Val::Str(str358)
                            })?;
                            d.set(
                                binary("add", e.get("original")?, Val::Str("-word".into()))?,
                                {
                                    let mut str359 = String::new();
                                    str359.push_str("wall-end-collar-");
                                    str359.push_str(&format(&e.get("which")?, &String::new())?);
                                    str359.push_str("-word");
                                    Val::Str(str359)
                                },
                            )?;
                            d
                        }));
                        fun353.call(args351, kw352)?
                    })?,
                )?;
            }
            let assigned365 = e
                .get("facts")?
                .get(Val::Str("constants".into()))?
                .get(Val::Str("KEYSTONE_STATION".into()))?;
            let unpack366 = unpack(assigned365.clone(), 2)?;
            e.set("jack_x", unpack366[0].clone())?;
            e.set("station_z", unpack366[1].clone())?;
            let assigned367 = binary("sub", e.get("station_z")?, Val::Float(1.0f64))?;
            e.set("jack_z", assigned367.clone())?;
            let assigned368 = binary(
                "sub",
                e.get("facts")?
                    .get(Val::Str("bodies".into()))?
                    .get(Val::Str("keystone-jack".into()))?
                    .get(Val::Int(4i64))?,
                Val::Float(6.2f64),
            )?;
            e.set("y0", assigned368.clone())?;
            let assigned369 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("kind".into()), Val::Str("rear".into()))?;
                d.set(Val::Str("tubes".into()), e.get("tubes")?)?;
                d.set(Val::Str("plug".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("jack_x")?);
                    s.push(e.get("y0")?);
                    s.push(e.get("jack_z")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("ribbon_points".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("jack_x")?);
                        s.push(binary("add", e.get("y0")?, Val::Float(26.5f64))?);
                        s.push(e.get("jack_z")?);
                        Val::list(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("jack_x")?);
                        s.push(Val::Float(548.0f64));
                        s.push(e.get("jack_z")?);
                        Val::list(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Float(42.0f64))?);
                        s.push(Val::Float(590.0f64));
                        s.push(Val::Float(298.0f64));
                        Val::list(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Float(48.5f64))?);
                        s.push(Val::Float(626.0f64));
                        s.push(Val::Float(294.0f64));
                        Val::list(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Float(48.5f64))?);
                        s.push(Val::Float(940.0f64));
                        s.push(Val::Float(294.0f64));
                        Val::list(s)
                    });
                    Val::list(s)
                })?;
                d
            };
            e.set("numbers", assigned369.clone())?;
            {
                let fun372 = e.get("_props")?;
                let mut args370 = Vec::new();
                let mut kw371 = Vec::new();
                args370.push(e.get("numbers")?);
                args370.push(e.get("colors")?);
                args370.push(e.get("work")?);
                fun372.call(args370, kw371)?
            };
            let assigned373 = binary(
                "add",
                {
                    let fun376 = e.get("_read")?;
                    let mut args374 = Vec::new();
                    let mut kw375 = Vec::new();
                    args374.push(binary(
                        "truediv",
                        e.get("work")?,
                        Val::Str("rear-leads.props.mesh".into()),
                    )?);
                    fun376.call(args374, kw375)?
                },
                e.get("collars")?,
            )?;
            e.set("leads", assigned373.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("the-back-face".into()), {
                    let fun379 = e.get("_write")?;
                    let mut args377 = Vec::new();
                    let mut kw378 = Vec::new();
                    args377.push(e.get("work")?);
                    args377.push(Val::Str("the-back-face".into()));
                    args377.push(e.get("rear")?);
                    fun379.call(args377, kw378)?
                })?;
                dict_extend(&d, {
                    let e = e.child();
                    let out380 = Val::dict(vec![]);
                    for item381 in {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Str("connect-rear-open".into()));
                            s.push(e.get("art")?.attr("CONNECT_OPEN_GAP")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Str("connect-rear-connected".into()));
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        let unpack382 = unpack(item381, 2)?;
                        e.set("name", unpack382[0].clone())?;
                        e.set("y", unpack382[1].clone())?;
                        out380.set(e.get("name")?, {
                            let fun385 = e.get("_write")?;
                            let mut args383 = Vec::new();
                            let mut kw384 = Vec::new();
                            args383.push(e.get("work")?);
                            args383.push(e.get("name")?);
                            args383.push(binary("add", e.get("rear")?, {
                                let fun388 = e.get("_select")?;
                                let mut args386 = Vec::new();
                                let mut kw387 = Vec::new();
                                args386.push(e.get("leads")?);
                                kw387.push(("move".into(), {
                                    let mut s = Vec::new();
                                    s.push(Val::Float(0.0f64));
                                    s.push(e.get("y")?);
                                    s.push(Val::Float(0.0f64));
                                    Val::tuple(s)
                                }));
                                fun388.call(args386, kw387)?
                            })?);
                            fun385.call(args383, kw384)?
                        })?;
                    }
                    out380
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
