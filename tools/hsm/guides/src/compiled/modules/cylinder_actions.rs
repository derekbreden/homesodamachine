//! Guide recipe: `tools/install-guide/cylinder_actions.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod1 = rt.import_module("PIL")?;
    e.set("Image", rt.member("PIL", "Image")?)?;
    e.set("scenes", rt.import_module("scenes")?)?;
    e.set("startup", rt.import_module("startup")?)?;
    let assigned2 = binary(
        "truediv",
        e.get("scenes")?.attr("HARDWARE")?,
        Val::Str("install-guide/out/cylinder-actions".into()),
    )?;
    e.set("OUT", assigned2.clone())?;
    let assigned3 = binary(
        "truediv",
        e.get("scenes")?.attr("HARDWARE")?,
        Val::Str("install-guide/art/cylinder-actions".into()),
    )?;
    e.set("ART", assigned3.clone())?;
    let assigned4 = Val::Float(30.0f64);
    e.set("READY_STANDOFF", assigned4.clone())?;
    let assigned5 = {
        let fun8 = e.get("dict")?;
        let mut args6 = Vec::new();
        let mut kw7 = Vec::new();
        kw7.push(("cam".into(), {
            let mut s = Vec::new();
            s.push(Val::Float(0.12f64));
            s.push(Val::Int(1i64));
            s.push(Val::Float(0.15f64));
            Val::tuple(s)
        }));
        kw7.push(("target".into(), {
            let mut s = Vec::new();
            s.push(unary("neg", Val::Int(34i64))?);
            s.push(Val::Int(0i64));
            s.push(unary("neg", Val::Int(50i64))?);
            Val::tuple(s)
        }));
        kw7.push(("span".into(), Val::Int(150i64)));
        kw7.push(("size".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(1600i64));
            s.push(Val::Int(1500i64));
            Val::tuple(s)
        }));
        fun8.call(args6, kw7)?
    };
    e.set("CONNECTION_POSE", assigned5.clone())?;
    let assigned9 = Val::Int(300i64);
    e.set("STARTUP_EXTRA_HEIGHT", assigned9.clone())?;
    let assigned10 = e.get("scenes")?.attr("reg")?;
    e.set("reg", assigned10.clone())?;
    let assigned11 = e.get("scenes")?.attr("install")?;
    e.set("install", assigned11.clone())?;
    // unit
    e.set("unit", {
        let params = vec![("vector".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned12 = {
                let fun15 = e.get("math")?.attr("sqrt")?;
                let mut args13 = Vec::new();
                let mut kw14 = Vec::new();
                args13.push({
                    let fun18 = e.get("sum")?;
                    let mut args16 = Vec::new();
                    let mut kw17 = Vec::new();
                    args16.push({
                        let e = e.child();
                        let out19 = Val::list(vec![]);
                        for item20 in e.get("vector")?.iter()? {
                            e.set("value", item20)?;
                            out19.attr("append")?.call(
                                vec![binary("mul", e.get("value")?, e.get("value")?)?],
                                vec![],
                            )?;
                        }
                        out19
                    });
                    fun18.call(args16, kw17)?
                });
                fun15.call(args13, kw14)?
            };
            e.set("length", assigned12.clone())?;
            return Ok({
                let fun23 = e.get("tuple")?;
                let mut args21 = Vec::new();
                let mut kw22 = Vec::new();
                args21.push({
                    let e = e.child();
                    let out24 = Val::list(vec![]);
                    for item25 in e.get("vector")?.iter()? {
                        e.set("value", item25)?;
                        out24.attr("append")?.call(
                            vec![binary("truediv", e.get("value")?, e.get("length")?)?],
                            vec![],
                        )?;
                    }
                    out24
                });
                fun23.call(args21, kw22)?
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
    // camera_axes
    e.set("camera_axes", {
        let params = vec![("cam".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned26 = {
                let fun29 = e.get("unit")?;
                let mut args27 = Vec::new();
                let mut kw28 = Vec::new();
                args27.push(e.get("cam")?);
                fun29.call(args27, kw28)?
            };
            e.set("direction", assigned26.clone())?;
            let assigned30 = {
                let fun33 = e.get("unit")?;
                let mut args31 = Vec::new();
                let mut kw32 = Vec::new();
                args31.push({
                    let fun36 = e.get("cross")?;
                    let mut args34 = Vec::new();
                    let mut kw35 = Vec::new();
                    args34.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    });
                    args34.push(e.get("direction")?);
                    fun36.call(args34, kw35)?
                });
                fun33.call(args31, kw32)?
            };
            e.set("right", assigned30.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("right")?);
                s.push({
                    let fun39 = e.get("cross")?;
                    let mut args37 = Vec::new();
                    let mut kw38 = Vec::new();
                    args37.push(e.get("direction")?);
                    args37.push(e.get("right")?);
                    fun39.call(args37, kw38)?
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // startup_pose
    e.set("startup_pose", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned40 = {
                let fun43 = e.get("camera_axes")?;
                let mut args41 = Vec::new();
                let mut kw42 = Vec::new();
                args41.push(e.get("startup")?.attr("CAM")?);
                fun43.call(args41, kw42)?
            };
            let unpack44 = unpack(assigned40.clone(), 2)?;
            e.set("_", unpack44[0].clone())?;
            e.set("up", unpack44[1].clone())?;
            let assigned45 = binary(
                "truediv",
                e.get("startup")?.attr("SIZE")?.get(Val::Int(1i64))?,
                binary("mul", Val::Int(2i64), e.get("startup")?.attr("SPAN")?)?,
            )?;
            e.set("scale", assigned45.clone())?;
            let assigned46 = binary(
                "truediv",
                e.get("STARTUP_EXTRA_HEIGHT")?,
                binary("mul", Val::Int(2i64), e.get("scale")?)?,
            )?;
            e.set("shift", assigned46.clone())?;
            let assigned47 = binary(
                "add",
                e.get("startup")?.attr("SIZE")?.get(Val::Int(1i64))?,
                e.get("STARTUP_EXTRA_HEIGHT")?,
            )?;
            e.set("height", assigned47.clone())?;
            return Ok({
                let fun50 = e.get("dict")?;
                let mut args48 = Vec::new();
                let mut kw49 = Vec::new();
                kw49.push(("cam".into(), e.get("startup")?.attr("CAM")?));
                kw49.push(("target".into(), {
                    let fun53 = e.get("tuple")?;
                    let mut args51 = Vec::new();
                    let mut kw52 = Vec::new();
                    args51.push({
                        let e = e.child();
                        let out54 = Val::list(vec![]);
                        for item55 in {
                            let fun58 = e.get("zip")?;
                            let mut args56 = Vec::new();
                            let mut kw57 = Vec::new();
                            args56.push(e.get("startup")?.attr("TARGET")?);
                            args56.push(e.get("up")?);
                            fun58.call(args56, kw57)?
                        }
                        .iter()?
                        {
                            let unpack59 = unpack(item55, 2)?;
                            e.set("value", unpack59[0].clone())?;
                            e.set("axis", unpack59[1].clone())?;
                            out54.attr("append")?.call(
                                vec![binary(
                                    "sub",
                                    e.get("value")?,
                                    binary("mul", e.get("shift")?, e.get("axis")?)?,
                                )?],
                                vec![],
                            )?;
                        }
                        out54
                    });
                    fun53.call(args51, kw52)?
                }));
                kw49.push((
                    "span".into(),
                    binary(
                        "truediv",
                        binary("mul", e.get("startup")?.attr("SPAN")?, e.get("height")?)?,
                        e.get("startup")?.attr("SIZE")?.get(Val::Int(1i64))?,
                    )?,
                ));
                kw49.push(("size".into(), {
                    let mut s = Vec::new();
                    s.push(e.get("startup")?.attr("SIZE")?.get(Val::Int(0i64))?);
                    s.push(e.get("height")?);
                    Val::tuple(s)
                }));
                fun50.call(args48, kw49)?
            });
            Ok(Val::None)
        })
    })?;
    // pixel
    e.set("pixel", {
        let params = vec![("point".into(), None, false), ("pose".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned60 = {
                let fun63 = e.get("camera_axes")?;
                let mut args61 = Vec::new();
                let mut kw62 = Vec::new();
                args61.push(e.get("pose")?.get(Val::Str("cam".into()))?);
                fun63.call(args61, kw62)?
            };
            let unpack64 = unpack(assigned60.clone(), 2)?;
            e.set("right", unpack64[0].clone())?;
            e.set("up", unpack64[1].clone())?;
            let assigned65 = {
                let fun68 = e.get("tuple")?;
                let mut args66 = Vec::new();
                let mut kw67 = Vec::new();
                args66.push({
                    let e = e.child();
                    let out69 = Val::list(vec![]);
                    for item70 in {
                        let fun73 = e.get("zip")?;
                        let mut args71 = Vec::new();
                        let mut kw72 = Vec::new();
                        args71.push(e.get("point")?);
                        args71.push(e.get("pose")?.get(Val::Str("target".into()))?);
                        fun73.call(args71, kw72)?
                    }
                    .iter()?
                    {
                        let unpack74 = unpack(item70, 2)?;
                        e.set("value", unpack74[0].clone())?;
                        e.set("target", unpack74[1].clone())?;
                        out69.attr("append")?.call(
                            vec![binary("sub", e.get("value")?, e.get("target")?)?],
                            vec![],
                        )?;
                    }
                    out69
                });
                fun68.call(args66, kw67)?
            };
            e.set("delta", assigned65.clone())?;
            let assigned75 = e.get("pose")?.get(Val::Str("size".into()))?;
            let unpack76 = unpack(assigned75.clone(), 2)?;
            e.set("width", unpack76[0].clone())?;
            e.set("height", unpack76[1].clone())?;
            let assigned77 = binary(
                "truediv",
                e.get("height")?,
                binary(
                    "mul",
                    Val::Int(2i64),
                    e.get("pose")?.get(Val::Str("span".into()))?,
                )?,
            )?;
            e.set("scale", assigned77.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    binary("truediv", e.get("width")?, Val::Int(2i64))?,
                    binary(
                        "mul",
                        {
                            let fun80 = e.get("sum")?;
                            let mut args78 = Vec::new();
                            let mut kw79 = Vec::new();
                            args78.push({
                                let e = e.child();
                                let out81 = Val::list(vec![]);
                                for item82 in {
                                    let fun85 = e.get("zip")?;
                                    let mut args83 = Vec::new();
                                    let mut kw84 = Vec::new();
                                    args83.push(e.get("delta")?);
                                    args83.push(e.get("right")?);
                                    fun85.call(args83, kw84)?
                                }
                                .iter()?
                                {
                                    let unpack86 = unpack(item82, 2)?;
                                    e.set("value", unpack86[0].clone())?;
                                    e.set("axis", unpack86[1].clone())?;
                                    out81.attr("append")?.call(
                                        vec![binary("mul", e.get("value")?, e.get("axis")?)?],
                                        vec![],
                                    )?;
                                }
                                out81
                            });
                            fun80.call(args78, kw79)?
                        },
                        e.get("scale")?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary("truediv", e.get("height")?, Val::Int(2i64))?,
                    binary(
                        "mul",
                        {
                            let fun89 = e.get("sum")?;
                            let mut args87 = Vec::new();
                            let mut kw88 = Vec::new();
                            args87.push({
                                let e = e.child();
                                let out90 = Val::list(vec![]);
                                for item91 in {
                                    let fun94 = e.get("zip")?;
                                    let mut args92 = Vec::new();
                                    let mut kw93 = Vec::new();
                                    args92.push(e.get("delta")?);
                                    args92.push(e.get("up")?);
                                    fun94.call(args92, kw93)?
                                }
                                .iter()?
                                {
                                    let unpack95 = unpack(item91, 2)?;
                                    e.set("value", unpack95[0].clone())?;
                                    e.set("axis", unpack95[1].clone())?;
                                    out90.attr("append")?.call(
                                        vec![binary("mul", e.get("value")?, e.get("axis")?)?],
                                        vec![],
                                    )?;
                                }
                                out90
                            });
                            fun89.call(args87, kw88)?
                        },
                        e.get("scale")?,
                    )?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // outlet_stations
    e.set("outlet_stations", {
        let params = vec![("stand_off".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned96 = {
                let fun99 = e.get("reg")?.attr("outlet")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                fun99.call(args97, kw98)?
            }
            .get(Val::Int(0i64))?;
            let unpack100 = unpack(assigned96.clone(), 3)?;
            e.set("x", unpack100[0].clone())?;
            e.set("y", unpack100[1].clone())?;
            e.set("mouth_z", unpack100[2].clone())?;
            e.set("x", binary("add", e.get("x")?, e.get("stand_off")?)?)?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("outlet-connector".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(binary(
                        "add",
                        e.get("y")?,
                        binary(
                            "truediv",
                            e.get("reg")?.attr("PTC_COLLET_D")?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    s.push(binary(
                        "truediv",
                        binary(
                            "add",
                            e.get("reg")?.attr("OUTLET_HEX_Z")?,
                            e.get("mouth_z")?,
                        )?,
                        Val::Int(2i64),
                    )?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("red-tube-exit".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(e.get("mouth_z")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("cga-nut".into()), {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        {
                            let fun103 = e.get("reg")?.attr("inlet")?;
                            let mut args101 = Vec::new();
                            let mut kw102 = Vec::new();
                            fun103.call(args101, kw102)?
                        }
                        .get(Val::Int(0i64))?
                        .get(Val::Int(0i64))?,
                        e.get("stand_off")?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("y")?,
                        binary(
                            "truediv",
                            e.get("reg")?.attr("CGA320_NUT_FLATS")?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // assembly
    e.set("assembly", {
        let params = vec![
            ("stand_off".into(), Some(Val::Int(0i64)), false),
            ("pressurised".into(), Some(Val::Bool(false)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(if e.get("pressurised")?.truthy()? {
                {
                    let fun106 = e.get("startup")?.attr("assembly")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    fun106.call(args104, kw105)?
                }
            } else {
                {
                    let fun109 = e.get("scenes")?.attr("cylinder")?;
                    let mut args107 = Vec::new();
                    let mut kw108 = Vec::new();
                    args107.push(e.get("stand_off")?);
                    fun109.call(args107, kw108)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // points
    e.set("points", {
        let params = vec![
            ("stand_off".into(), None, false),
            ("pressurised".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer); // held
            e.set("held", {
                let params = vec![("point".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("point")?.get(Val::Int(0i64))?,
                            e.get("stand_off")?,
                        )?);
                        s.push(e.get("point")?.get(Val::Int(1i64))?);
                        s.push(e.get("point")?.get(Val::Int(2i64))?);
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned110 = {
                let fun113 = e.get("outlet_stations")?;
                let mut args111 = Vec::new();
                let mut kw112 = Vec::new();
                args111.push(e.get("stand_off")?);
                fun113.call(args111, kw112)?
            };
            e.set("result", assigned110.clone())?;
            {
                let fun116 = e.get("result")?.attr("update")?;
                let mut args114 = Vec::new();
                let mut kw115 = Vec::new();
                args114.push({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("upper-gauge".into()), {
                        let fun119 = e.get("held")?;
                        let mut args117 = Vec::new();
                        let mut kw118 = Vec::new();
                        args117.push(
                            {
                                let fun122 = e.get("reg")?.attr("outlet_dial")?;
                                let mut args120 = Vec::new();
                                let mut kw121 = Vec::new();
                                fun122.call(args120, kw121)?
                            }
                            .get(Val::Int(0i64))?,
                        );
                        fun119.call(args117, kw118)?
                    })?;
                    d.set(Val::Str("cylinder-gauge".into()), {
                        let fun125 = e.get("held")?;
                        let mut args123 = Vec::new();
                        let mut kw124 = Vec::new();
                        args123.push(
                            {
                                let fun128 = e.get("reg")?.attr("tank_dial")?;
                                let mut args126 = Vec::new();
                                let mut kw127 = Vec::new();
                                fun128.call(args126, kw127)?
                            }
                            .get(Val::Int(0i64))?,
                        );
                        fun125.call(args123, kw124)?
                    })?;
                    d.set(Val::Str("factory-screw".into()), {
                        let fun131 = e.get("held")?;
                        let mut args129 = Vec::new();
                        let mut kw130 = Vec::new();
                        args129.push(
                            {
                                let fun134 = e.get("reg")?.attr("adjustment")?;
                                let mut args132 = Vec::new();
                                let mut kw133 = Vec::new();
                                fun134.call(args132, kw133)?
                            }
                            .get(Val::Int(0i64))?,
                        );
                        fun131.call(args129, kw130)?
                    })?;
                    d.set(Val::Str("cylinder-handwheel".into()), {
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(115i64))?);
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(33i64));
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("cylinder-valve".into()), {
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(115i64))?);
                        s.push(Val::Int(12i64));
                        s.push(unary("neg", Val::Float(7.5f64))?);
                        Val::tuple(s)
                    })?;
                    d
                });
                fun116.call(args114, kw115)?
            };
            if e.get("pressurised")?.truthy()? {
                let assigned135 = {
                    let fun138 = e.get("startup")?.attr("points")?;
                    let mut args136 = Vec::new();
                    let mut kw137 = Vec::new();
                    fun138.call(args136, kw137)?
                }
                .get(Val::Str("upper-needle-tip".into()))?;
                e.get("result")?
                    .set(Val::Str("upper-needle-tip".into()), assigned135.clone())?;
            }
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // anchor_metadata
    e.set("anchor_metadata",{let params=vec![("stand_off".into(),None,false),("pressurised".into(),None,false),("pose".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned139={let e=e.child();let out140=Val::dict(vec![]);for item141 in {let fun144={let fun147=e.get("points")?;let mut args145=Vec::new();let mut kw146=Vec::new();args145.push(e.get("stand_off")?);args145.push(e.get("pressurised")?);fun147.call(args145,kw146)?}.attr("items")?;let mut args142=Vec::new();let mut kw143=Vec::new();fun144.call(args142,kw143)?}.iter()? {let unpack148=unpack(item141,2)?;e.set("name",unpack148[0].clone())?;e.set("point",unpack148[1].clone())?;out140.set(e.get("name")?,{let fun151=e.get("dict")?;let mut args149=Vec::new();let mut kw150=Vec::new();kw150.push(("world".into(),e.get("point")?));kw150.push(("pixel".into(),{let fun154=e.get("pixel")?;let mut args152=Vec::new();let mut kw153=Vec::new();args152.push(e.get("point")?);args152.push(e.get("pose")?);fun154.call(args152,kw153)?}));fun151.call(args149,kw150)?})?;}out140};e.set("anchors",assigned139.clone())?;
for item155 in {let fun165=e.get("anchors")?.attr("items")?;let mut args163=Vec::new();let mut kw164=Vec::new();fun165.call(args163,kw164)?}.iter()? {
let unpack166=unpack(item155,2)?;e.set("name",unpack166[0].clone())?;e.set("anchor",unpack166[1].clone())?;if {let v156=e.get("name")?;let v157={let mut s=Vec::new();s.push(Val::Str("cylinder-handwheel".into()));s.push(Val::Str("cylinder-valve".into()));Val::set_values(s)};Val::Bool(compare("in",v156.clone(),v157.clone())?.truthy()?)}.truthy()? {
let assigned158=Val::Str("tools/install-guide/scenes.py:cylinder".into());e.get("anchor")?.set(Val::Str("source".into()),assigned158.clone())?;
}else{
if {let v159=e.get("name")?;let v160=Val::Str("upper-needle-tip".into());Val::Bool(compare("eq",v159.clone(),v160.clone())?.truthy()?)}.truthy()? {
let assigned161=Val::Str("tools/install-guide/startup.py:points".into());e.get("anchor")?.set(Val::Str("source".into()),assigned161.clone())?;
}else{
let assigned162=Val::Str("hardware/reference/taprite-3741-regulator/taprite_3741_regulator.py:stations".into());e.get("anchor")?.set(Val::Str("source".into()),assigned162.clone())?;
}
}
}
let assigned167={let fun170=e.get("outlet_stations")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push(e.get("stand_off")?);fun170.call(args168,kw169)?}.get(Val::Str("cga-nut".into()))?;e.set("nut",assigned167.clone())?;
let assigned171={let fun174=e.get("outlet_stations")?;let mut args172=Vec::new();let mut kw173=Vec::new();args172.push(Val::Int(0i64));fun174.call(args172,kw173)?}.get(Val::Str("cga-nut".into()))?;e.set("seated_nut",assigned171.clone())?;
return Ok({let fun177=e.get("dict")?;let mut args175=Vec::new();let mut kw176=Vec::new();kw176.push(("cam".into(),e.get("pose")?.get(Val::Str("cam".into()))?));kw176.push(("target".into(),e.get("pose")?.get(Val::Str("target".into()))?));kw176.push(("span".into(),e.get("pose")?.get(Val::Str("span".into()))?));kw176.push(("size".into(),e.get("pose")?.get(Val::Str("size".into()))?));kw176.push(("projection".into(),Val::Str("orthographic".into())));kw176.push(("up".into(),{let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(1i64));Val::tuple(s)}));kw176.push(("trim".into(),Val::Bool(false)));kw176.push(("pixel_origin".into(),Val::Str("top-left".into())));kw176.push(("pixels_per_mm".into(),binary("truediv",e.get("pose")?.get(Val::Str("size".into()))?.get(Val::Int(1i64))?,binary("mul",Val::Int(2i64),e.get("pose")?.get(Val::Str("span".into()))?)?)?));kw176.push(("crops".into(),if e.get("pressurised")?.truthy()? {{let fun180=e.get("dict")?;let mut args178=Vec::new();let mut kw179=Vec::new();kw179.push(("overview".into(),{let mut s=Vec::new();s.push(Val::Int(173i64));s.push(Val::Int(53i64));s.push(Val::Int(1752i64));s.push(Val::Int(1360i64));Val::tuple(s)}));kw179.push(("upper_gauge".into(),{let mut s=Vec::new();s.push(Val::Int(533i64));s.push(Val::Int(48i64));s.push(Val::Int(873i64));s.push(Val::Int(388i64));Val::tuple(s)}));kw179.push(("connector_detail".into(),{let mut s=Vec::new();s.push(Val::Int(485i64));s.push(Val::Int(950i64));s.push(Val::Int(905i64));s.push(Val::Int(1360i64));Val::tuple(s)}));fun180.call(args178,kw179)?}} else {{let fun183=e.get("dict")?;let mut args181=Vec::new();let mut kw182=Vec::new();kw182.push(("overview".into(),{let mut s=Vec::new();s.push(Val::Int(80i64));s.push(Val::Int(0i64));s.push(Val::Int(1600i64));s.push(Val::Int(1500i64));Val::tuple(s)}));kw182.push(("connector_detail".into(),{let mut s=Vec::new();s.push(Val::Int(420i64));s.push(Val::Int(775i64));s.push(Val::Int(830i64));s.push(Val::Int(1335i64));Val::tuple(s)}));fun183.call(args181,kw182)?}}));kw176.push(("stand_off_mm".into(),e.get("stand_off")?));kw176.push(("outlet_psi".into(),if e.get("pressurised")?.truthy()? {e.get("startup")?.attr("OUTLET_PSI")?} else {Val::Int(0i64)}));kw176.push(("cylinder_psi".into(),if e.get("pressurised")?.truthy()? {e.get("startup")?.attr("CYLINDER_PSI")?} else {Val::Int(0i64)}));kw176.push(("points".into(),e.get("anchors")?));kw176.push(("approach".into(),{let fun186=e.get("dict")?;let mut args184=Vec::new();let mut kw185=Vec::new();kw185.push(("axis".into(),{let mut s=Vec::new();s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)}));kw185.push(("distance_mm".into(),e.get("stand_off")?));kw185.push(("from_world".into(),e.get("nut")?));kw185.push(("to_world".into(),e.get("seated_nut")?));kw185.push(("from_pixel".into(),{let fun189=e.get("pixel")?;let mut args187=Vec::new();let mut kw188=Vec::new();args187.push(e.get("nut")?);args187.push(e.get("pose")?);fun189.call(args187,kw188)?}));kw185.push(("to_pixel".into(),{let fun192=e.get("pixel")?;let mut args190=Vec::new();let mut kw191=Vec::new();args190.push(e.get("seated_nut")?);args190.push(e.get("pose")?);fun192.call(args190,kw191)?}));fun186.call(args184,kw185)?}));kw176.push(("turn_axes".into(),{let d=Val::dict(vec![]);d.set(Val::Str("cylinder-handwheel".into()),{let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(1i64));Val::tuple(s)})?;d}));fun177.call(args175,kw176)?});
Ok(Val::None)})})?;
    // main
    e.set("main", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned193 = {
                let fun196 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args194 = Vec::new();
                let mut kw195 = Vec::new();
                kw195.push(("description".into(), e.get("__doc__")?));
                fun196.call(args194, kw195)?
            };
            e.set("parser", assigned193.clone())?;
            {
                let fun199 = e.get("parser")?.attr("add_argument")?;
                let mut args197 = Vec::new();
                let mut kw198 = Vec::new();
                args197.push(Val::Str("scenes".into()));
                kw198.push(("nargs".into(), Val::Str("*".into())));
                kw198.push(("choices".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Str("co2-ready".into()));
                    s.push(Val::Str("co2-connected".into()));
                    s.push(Val::Str("startup-gas".into()));
                    Val::list(s)
                }));
                fun199.call(args197, kw198)?
            };
            {
                let fun202 = e.get("parser")?.attr("add_argument")?;
                let mut args200 = Vec::new();
                let mut kw201 = Vec::new();
                args200.push(Val::Str("--stage-only".into()));
                kw201.push(("action".into(), Val::Str("store_true".into())));
                fun202.call(args200, kw201)?
            };
            let assigned203 = {
                let fun206 = e.get("parser")?.attr("parse_args")?;
                let mut args204 = Vec::new();
                let mut kw205 = Vec::new();
                fun206.call(args204, kw205)?
            };
            e.set("args", assigned203.clone())?;
            let assigned207 = {
                let fun210 = e.get("set")?;
                let mut args208 = Vec::new();
                let mut kw209 = Vec::new();
                args208.push(e.get("args")?.attr("scenes")?);
                fun210.call(args208, kw209)?
            };
            e.set("wanted", assigned207.clone())?;
            {
                let fun213 = e.get("OUT")?.attr("mkdir")?;
                let mut args211 = Vec::new();
                let mut kw212 = Vec::new();
                kw212.push(("parents".into(), Val::Bool(true)));
                kw212.push(("exist_ok".into(), Val::Bool(true)));
                fun213.call(args211, kw212)?
            };
            {
                let fun216 = e.get("ART")?.attr("mkdir")?;
                let mut args214 = Vec::new();
                let mut kw215 = Vec::new();
                kw215.push(("parents".into(), Val::Bool(true)));
                kw215.push(("exist_ok".into(), Val::Bool(true)));
                fun216.call(args214, kw215)?
            };
            let assigned217 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("jobs", assigned217.clone())?;
            let assigned218 = {
                let fun221 = e.get("dict")?;
                let mut args219 = Vec::new();
                let mut kw220 = Vec::new();
                kw220.push(("geometry_sources".into(), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("regulator".into()),
                        Val::Str(
                            "hardware/reference/taprite-3741-regulator/taprite_3741_regulator.py"
                                .into(),
                        ),
                    )?;
                    d.set(
                        Val::Str("cylinder".into()),
                        Val::Str("tools/install-guide/scenes.py:cylinder".into()),
                    )?;
                    d.set(
                        Val::Str("tether".into()),
                        Val::Str("hardware/install-guide/_install_art.py:_co2_tether".into()),
                    )?;
                    d.set(
                        Val::Str("startup-dials".into()),
                        Val::Str("tools/install-guide/startup.py:assembly".into()),
                    )?;
                    d
                }));
                kw220.push(("fittings".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Str("PI010822S".into()));
                    Val::list(s)
                }));
                kw220.push((
                    "tether_seating".into(),
                    Val::Str(
                        "Pushed in at the factory; the drawn depth past the mouth is illustrative."
                            .into(),
                    ),
                ));
                kw220.push(("scenes".into(), {
                    let d = Val::dict(vec![]);
                    d
                }));
                fun221.call(args219, kw220)?
            };
            e.set("metadata", assigned218.clone())?;
            let assigned222 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("co2-ready".into()));
                    s.push(e.get("READY_STANDOFF")?);
                    s.push(Val::Bool(false));
                    s.push(e.get("CONNECTION_POSE")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("co2-connected".into()));
                    s.push(Val::Int(0i64));
                    s.push(Val::Bool(false));
                    s.push(e.get("CONNECTION_POSE")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("startup-gas".into()));
                    s.push(Val::Int(0i64));
                    s.push(Val::Bool(true));
                    s.push({
                        let fun225 = e.get("startup_pose")?;
                        let mut args223 = Vec::new();
                        let mut kw224 = Vec::new();
                        fun225.call(args223, kw224)?
                    });
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("states", assigned222.clone())?;
            for item226 in e.get("states")?.iter()? {
                let unpack269 = unpack(item226, 4)?;
                e.set("name", unpack269[0].clone())?;
                e.set("stand_off", unpack269[1].clone())?;
                e.set("pressurised", unpack269[2].clone())?;
                e.set("pose", unpack269[3].clone())?;
                if {
                    let v229 = e.get("wanted")?;
                    if v229.truthy()? {
                        {
                            let v227 = e.get("name")?;
                            let v228 = e.get("wanted")?;
                            Val::Bool(compare("not_in", v227.clone(), v228.clone())?.truthy()?)
                        }
                    } else {
                        v229
                    }
                }
                .truthy()?
                {
                    continue;
                }
                let assigned230 = binary("truediv", e.get("OUT")?, {
                    let mut str231 = String::new();
                    str231.push_str(&format(&e.get("name")?, &String::new())?);
                    str231.push_str(".step");
                    Val::Str(str231)
                })?;
                e.set("path", assigned230.clone())?;
                {
                    let fun234 = e.get("scenes")?.attr("original")?.attr("_export_colored")?;
                    let mut args232 = Vec::new();
                    let mut kw233 = Vec::new();
                    args232.push({
                        let fun237 = e.get("assembly")?;
                        let mut args235 = Vec::new();
                        let mut kw236 = Vec::new();
                        args235.push(e.get("stand_off")?);
                        args235.push(e.get("pressurised")?);
                        fun237.call(args235, kw236)?
                    });
                    args232.push(e.get("path")?);
                    kw233.push(("mesh".into(), Val::Bool(true)));
                    fun234.call(args232, kw233)?
                };
                {
                    let fun240 = e.get("jobs")?.attr("append")?;
                    let mut args238 = Vec::new();
                    let mut kw239 = Vec::new();
                    args238.push({
                        let fun243 = e.get("dict")?;
                        let mut args241 = Vec::new();
                        let mut kw242 = Vec::new();
                        kw242.push(("step".into(), {
                            let fun246 = e.get("str")?;
                            let mut args244 = Vec::new();
                            let mut kw245 = Vec::new();
                            args244.push({
                                let fun249 = e.get("path")?.attr("relative_to")?;
                                let mut args247 = Vec::new();
                                let mut kw248 = Vec::new();
                                args247.push(e.get("scenes")?.attr("HARDWARE")?);
                                fun249.call(args247, kw248)?
                            });
                            fun246.call(args244, kw245)?
                        }));
                        kw242.push(("out".into(), {
                            let fun252 = e.get("str")?;
                            let mut args250 = Vec::new();
                            let mut kw251 = Vec::new();
                            args250.push(binary("truediv", e.get("ART")?, {
                                let mut str253 = String::new();
                                str253.push_str(&format(&e.get("name")?, &String::new())?);
                                str253.push_str(".png");
                                Val::Str(str253)
                            })?);
                            fun252.call(args250, kw251)?
                        }));
                        kw242.push(("cam".into(), e.get("pose")?.get(Val::Str("cam".into()))?));
                        kw242.push((
                            "target".into(),
                            e.get("pose")?.get(Val::Str("target".into()))?,
                        ));
                        kw242.push(("span".into(), e.get("pose")?.get(Val::Str("span".into()))?));
                        kw242.push(("size".into(), {
                            let mut str254 = String::new();
                            str254.push_str(&format(
                                &e.get("pose")?
                                    .get(Val::Str("size".into()))?
                                    .get(Val::Int(0i64))?,
                                &String::new(),
                            )?);
                            str254.push_str("x");
                            str254.push_str(&format(
                                &e.get("pose")?
                                    .get(Val::Str("size".into()))?
                                    .get(Val::Int(1i64))?,
                                &String::new(),
                            )?);
                            Val::Str(str254)
                        }));
                        kw242.push(("up".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        }));
                        kw242.push(("bg".into(), Val::Str("#f2eee8".into())));
                        kw242.push(("transparent".into(), Val::Bool(true)));
                        kw242.push(("solid".into(), Val::Bool(true)));
                        kw242.push(("ortho".into(), Val::Bool(true)));
                        kw242.push(("trim".into(), Val::Bool(false)));
                        kw242.push(("ground".into(), Val::Bool(false)));
                        kw242.push(("fog".into(), Val::Bool(false)));
                        fun243.call(args241, kw242)?
                    });
                    fun240.call(args238, kw239)?
                };
                let assigned255 = {
                    let fun258 = e.get("anchor_metadata")?;
                    let mut args256 = Vec::new();
                    let mut kw257 = Vec::new();
                    args256.push(e.get("stand_off")?);
                    args256.push(e.get("pressurised")?);
                    args256.push(e.get("pose")?);
                    fun258.call(args256, kw257)?
                };
                e.get("metadata")?
                    .get(Val::Str("scenes".into()))?
                    .set(e.get("name")?, assigned255.clone())?;
                if {
                    let v259 = e.get("name")?;
                    let v260 = Val::Str("startup-gas".into());
                    Val::Bool(compare("eq", v259.clone(), v260.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned261 = {
                        let fun264 = e.get("dict")?;
                        let mut args262 = Vec::new();
                        let mut kw263 = Vec::new();
                        kw263.push(("cam".into(), e.get("startup")?.attr("CAM")?));
                        kw263.push(("target".into(), e.get("startup")?.attr("TARGET")?));
                        kw263.push(("span".into(), e.get("startup")?.attr("SPAN")?));
                        kw263.push(("size".into(), e.get("startup")?.attr("SIZE")?));
                        kw263.push(("same_pixel_coordinates".into(), Val::Bool(true)));
                        kw263.push(("extra_canvas_below".into(), e.get("STARTUP_EXTRA_HEIGHT")?));
                        fun264.call(args262, kw263)?
                    };
                    e.get("metadata")?
                        .get(Val::Str("scenes".into()))?
                        .get(e.get("name")?)?
                        .set(
                            Val::Str("registered_source_pose".into()),
                            assigned261.clone(),
                        )?;
                }
                {
                    let fun267 = e.get("print")?;
                    let mut args265 = Vec::new();
                    let mut kw266 = Vec::new();
                    args265.push({
                        let mut str268 = String::new();
                        str268.push_str("Staged ");
                        str268.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str268)
                    });
                    kw266.push(("flush".into(), Val::Bool(true)));
                    fun267.call(args265, kw266)?
                };
            }
            let assigned270 = binary("truediv", e.get("OUT")?, Val::Str("scenes.json".into()))?;
            e.set("manifest", assigned270.clone())?;
            {
                let fun273 = e.get("manifest")?.attr("write_text")?;
                let mut args271 = Vec::new();
                let mut kw272 = Vec::new();
                args271.push(binary(
                    "add",
                    {
                        let fun276 = e.get("json")?.attr("dumps")?;
                        let mut args274 = Vec::new();
                        let mut kw275 = Vec::new();
                        args274.push(e.get("jobs")?);
                        kw275.push(("indent".into(), Val::Int(2i64)));
                        fun276.call(args274, kw275)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun273.call(args271, kw272)?
            };
            if unary("not", e.get("args")?.attr("stage_only")?)?.truthy()? {
                {
                    let fun279 = e.get("scenes")?.attr("_hsm_render")?.attr("render")?;
                    let mut args277 = Vec::new();
                    let mut kw278 = Vec::new();
                    args277.push(e.get("jobs")?);
                    fun279.call(args277, kw278)?
                };
                for item280 in {
                    let fun301 = e
                        .get("metadata")?
                        .get(Val::Str("scenes".into()))?
                        .attr("items")?;
                    let mut args299 = Vec::new();
                    let mut kw300 = Vec::new();
                    fun301.call(args299, kw300)?
                }
                .iter()?
                {
                    let unpack302 = unpack(item280, 2)?;
                    e.set("name", unpack302[0].clone())?;
                    e.set("entry", unpack302[1].clone())?;
                    let context281 = {
                        let fun284 = e.get("Image")?.attr("open")?;
                        let mut args282 = Vec::new();
                        let mut kw283 = Vec::new();
                        args282.push(binary("truediv", e.get("ART")?, {
                            let mut str285 = String::new();
                            str285.push_str(&format(&e.get("name")?, &String::new())?);
                            str285.push_str(".png");
                            Val::Str(str285)
                        })?);
                        fun284.call(args282, kw283)?
                    };
                    e.set(
                        "rendered",
                        context281.attr("__enter__")?.call(vec![], vec![])?,
                    )?;
                    let context_result298 = (|| -> Result<Flow> {
                        if !{
                            let v289 = e.get("rendered")?.attr("size")?;
                            let v290 = {
                                let fun288 = e.get("tuple")?;
                                let mut args286 = Vec::new();
                                let mut kw287 = Vec::new();
                                args286.push(e.get("entry")?.get(Val::Str("size".into()))?);
                                fun288.call(args286, kw287)?
                            };
                            Val::Bool(compare("eq", v289.clone(), v290.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            anyhow::bail!("{}", val_string(Val::Str("assertion failed".into()))?);
                        }
                        let assigned291 = {
                            let fun294 = {
                                let fun297 = e.get("rendered")?.attr("getchannel")?;
                                let mut args295 = Vec::new();
                                let mut kw296 = Vec::new();
                                args295.push(Val::Str("A".into()));
                                fun297.call(args295, kw296)?
                            }
                            .attr("getbbox")?;
                            let mut args292 = Vec::new();
                            let mut kw293 = Vec::new();
                            fun294.call(args292, kw293)?
                        };
                        e.get("entry")?
                            .set(Val::Str("alpha_bounds".into()), assigned291.clone())?;
                        Ok(Flow::Continue)
                    })();
                    context281
                        .attr("__exit__")?
                        .call(vec![Val::None, Val::None, Val::None], vec![])?;
                    match context_result298? {
                        Flow::Continue => {}
                        Flow::Return(value) => return Ok(value),
                        Flow::Break => break,
                        Flow::Next => continue,
                    }
                }
            }
            {
                let fun305 = binary("truediv", e.get("OUT")?, Val::Str("anchors.json".into()))?
                    .attr("write_text")?;
                let mut args303 = Vec::new();
                let mut kw304 = Vec::new();
                args303.push(binary(
                    "add",
                    {
                        let fun308 = e.get("json")?.attr("dumps")?;
                        let mut args306 = Vec::new();
                        let mut kw307 = Vec::new();
                        args306.push(e.get("metadata")?);
                        kw307.push(("indent".into(), Val::Int(2i64)));
                        fun308.call(args306, kw307)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun305.call(args303, kw304)?
            };
            {
                let fun311 = e.get("print")?;
                let mut args309 = Vec::new();
                let mut kw310 = Vec::new();
                args309.push(binary(
                    "truediv",
                    e.get("OUT")?,
                    Val::Str("anchors.json".into()),
                )?);
                fun311.call(args309, kw310)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun314 = e.get("main")?;
        let mut args312 = Vec::new();
        let mut kw313 = Vec::new();
        fun314.call(args312, kw313)?
    };
    Ok(Val::None)
}
