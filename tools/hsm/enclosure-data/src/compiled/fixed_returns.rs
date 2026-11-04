//! Station datums for the four pump tees, the tee wall's fore band and the fittings and tubes
//! that join them.
//!
//! Coordinates are enclosure millimetres: +Y points inward and +Z points up. Each pump port
//! feeds one purchased PP0208E tee, its branch toward the pump and its run upright. The fore
//! valve stands over the run on one short straight tube. The lower return reaches the rear valve's
//! bottom port: a trimmed NeoFit stem elbow in the tee's lower collet, one tube, and a
//! second stem elbow in the valve.
//!
//! THE FORE BAND'S AFT FACE IS THE BORE FACE. Each tee's branch bore opens on it, and the tee
//! stands with its fixed branch barrel just aft of it. The branch collet stands extended in its
//! recess ahead of that face and grips the pump tube like any push-fit; the tube is pushed home
//! once, at the factory, to the tee's stop.
//!
//! This module holds geometry data only; the dock's solids and the manifold read the same
//! figures.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
            line!(),
        );
        {
            let fun5 = e.get("next")?;
            let mut args3 = Vec::new();
            let mut kw4 = Vec::new();
            args3.push({
                let e = e.child();
                let out6 = Val::list(vec![]);
                for item7 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun10 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                                line!(),
                            );
                            {
                                let fun13 = e.get("Path")?;
                                let mut args11 = Vec::new();
                                let mut kw12 = Vec::new();
                                args11.push(e.get("__file__")?);
                                fun13.call(args11, kw12)?
                            }
                        }
                        .attr("resolve")?;
                        let mut args8 = Vec::new();
                        let mut kw9 = Vec::new();
                        fun10.call(args8, kw9)?
                    }
                }
                .attr("parents")?
                .iter()?
                {
                    e.set("p", item7)?;
                    if {
                        let v14 = e.get("p")?.attr("name")?;
                        let v15 = Val::Str("hardware".into());
                        Val::Bool(compare("eq", v14.clone(), v15.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out6.attr("append")?.call(vec![e.get("p")?], vec![])?;
                    }
                }
                out6
            });
            fun5.call(args3, kw4)?
        }
    };
    e.set("_hw", assigned2.clone())?;
    for item16 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("reference".into()))?,
            Val::Str("tee-connector".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("reference".into()))?,
            Val::Str("neofit-stem-elbow".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("_hw")?,
            Val::Str("scripts".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_p", item16)?;
        if {
            let v20 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun19 = e.get("str")?;
                    let mut args17 = Vec::new();
                    let mut kw18 = Vec::new();
                    args17.push(e.get("_p")?);
                    fun19.call(args17, kw18)?
                }
            };
            let v21 = e.get("sys")?.attr("path")?;
            Val::Bool(compare("not_in", v20.clone(), v21.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun24 = e.get("sys")?.attr("path")?.attr("insert")?;
                    let mut args22 = Vec::new();
                    let mut kw23 = Vec::new();
                    args22.push(Val::Int(0i64));
                    args22.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                            line!(),
                        );
                        {
                            let fun27 = e.get("str")?;
                            let mut args25 = Vec::new();
                            let mut kw26 = Vec::new();
                            args25.push(e.get("_p")?);
                            fun27.call(args25, kw26)?
                        }
                    });
                    fun24.call(args22, kw23)?
                }
            };
        }
    }
    e.set("tee", rt.import_module("tee_connector")?)?;
    e.set("elbow", rt.import_module("neofit_stem_elbow")?)?;
    let assigned28 = e.get("tee")?.attr("TUBE_D")?;
    e.set("TUBE_OD", assigned28.clone())?;
    let assigned29 = Val::Float(4.3f64);
    e.set("TUBE_ID", assigned29.clone())?;
    let assigned30 = binary(
        "add",
        Val::Float(3.175f64),
        e.get("tee")?.attr("BRANCH_COLLET_TRAVEL")?,
    )?;
    e.set("PLATE_T", assigned30.clone())?;
    let assigned31 = e.get("tee")?.attr("BRANCH_PRESSED_REACH")?;
    e.set("BORE_FACE_TO_AXIS", assigned31.clone())?;
    let assigned32 = e.get("tee")?.attr("RUN_HALF")?;
    e.set("RUN_FACE", assigned32.clone())?;
    let assigned33 = e.get("tee")?.attr("INSERTION")?;
    e.set("TIP_DEPTH", assigned33.clone())?;
    let assigned34 = binary("add", e.get("PLATE_T")?, e.get("TIP_DEPTH")?)?;
    e.set("TIP_FROM_FORE", assigned34.clone())?;
    let assigned35 = e.get("tee")?.attr("RUN_INSERTION_EXTENDED")?;
    e.set("RUN_INSERTION", assigned35.clone())?;
    let assigned36 = Val::Float(12.0f64);
    e.set("VALVE_INSERTION_NOMINAL", assigned36.clone())?;
    let assigned37 = e.get("elbow")?.attr("HUB_BACK_REACH")?;
    e.set("ELBOW_DROP", assigned37.clone())?;
    // _add
    e.set("_add", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun40 = e.get("tuple")?;
                    let mut args38 = Vec::new();
                    let mut kw39 = Vec::new();
                    args38.push({
                        let e = e.child();
                        let out41 = Val::list(vec![]);
                        for item42 in {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                                line!(),
                            );
                            {
                                let fun45 = e.get("range")?;
                                let mut args43 = Vec::new();
                                let mut kw44 = Vec::new();
                                args43.push(Val::Int(3i64));
                                fun45.call(args43, kw44)?
                            }
                        }
                        .iter()?
                        {
                            e.set("i", item42)?;
                            out41.attr("append")?.call(
                                vec![binary(
                                    "add",
                                    e.get("a")?.get(e.get("i")?)?,
                                    e.get("b")?.get(e.get("i")?)?,
                                )?],
                                vec![],
                            )?;
                        }
                        out41
                    });
                    fun40.call(args38, kw39)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _scale
    e.set("_scale", {
        let params = vec![("a".into(), None, false), ("k".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun48 = e.get("tuple")?;
                    let mut args46 = Vec::new();
                    let mut kw47 = Vec::new();
                    args46.push({
                        let e = e.child();
                        let out49 = Val::list(vec![]);
                        for item50 in e.get("a")?.iter()? {
                            e.set("v", item50)?;
                            out49
                                .attr("append")?
                                .call(vec![binary("mul", e.get("v")?, e.get("k")?)?], vec![])?;
                        }
                        out49
                    });
                    fun48.call(args46, kw47)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _unit
    e.set("_unit", {
        let params = vec![("v".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned51 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun54 = e.get("math")?.attr("sqrt")?;
                    let mut args52 = Vec::new();
                    let mut kw53 = Vec::new();
                    args52.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                            line!(),
                        );
                        {
                            let fun57 = e.get("sum")?;
                            let mut args55 = Vec::new();
                            let mut kw56 = Vec::new();
                            args55.push({
                                let e = e.child();
                                let out58 = Val::list(vec![]);
                                for item59 in e.get("v")?.iter()? {
                                    e.set("c", item59)?;
                                    out58.attr("append")?.call(
                                        vec![binary("mul", e.get("c")?, e.get("c")?)?],
                                        vec![],
                                    )?;
                                }
                                out58
                            });
                            fun57.call(args55, kw56)?
                        }
                    });
                    fun54.call(args52, kw53)?
                }
            };
            e.set("n", assigned51.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun62 = e.get("_scale")?;
                    let mut args60 = Vec::new();
                    let mut kw61 = Vec::new();
                    args60.push(e.get("v")?);
                    args60.push(binary("truediv", Val::Float(1.0f64), e.get("n")?)?);
                    fun62.call(args60, kw61)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _line
    e.set("_line", {
        let params = vec![
            ("start".into(), None, false),
            ("direction".into(), None, false),
            ("length".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("kind".into()), Val::Str("line".into()))?;
                d.set(Val::Str("start_mm".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun65 = e.get("tuple")?;
                        let mut args63 = Vec::new();
                        let mut kw64 = Vec::new();
                        args63.push(e.get("start")?);
                        fun65.call(args63, kw64)?
                    }
                })?;
                d.set(Val::Str("end_mm".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun68 = e.get("_add")?;
                        let mut args66 = Vec::new();
                        let mut kw67 = Vec::new();
                        args66.push(e.get("start")?);
                        args66.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                                line!(),
                            );
                            {
                                let fun71 = e.get("_scale")?;
                                let mut args69 = Vec::new();
                                let mut kw70 = Vec::new();
                                args69.push(e.get("direction")?);
                                args69.push(e.get("length")?);
                                fun71.call(args69, kw70)?
                            }
                        });
                        fun68.call(args66, kw67)?
                    }
                })?;
                d.set(Val::Str("start_tangent".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun74 = e.get("tuple")?;
                        let mut args72 = Vec::new();
                        let mut kw73 = Vec::new();
                        args72.push(e.get("direction")?);
                        fun74.call(args72, kw73)?
                    }
                })?;
                d.set(Val::Str("end_tangent".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun77 = e.get("tuple")?;
                        let mut args75 = Vec::new();
                        let mut kw76 = Vec::new();
                        args75.push(e.get("direction")?);
                        fun77.call(args75, kw76)?
                    }
                })?;
                d.set(Val::Str("length_mm".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun80 = e.get("float")?;
                        let mut args78 = Vec::new();
                        let mut kw79 = Vec::new();
                        args78.push(e.get("length")?);
                        fun80.call(args78, kw79)?
                    }
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // plate_aft_y
    e.set("plate_aft_y", {
        let params = vec![("fore_y".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary("add", e.get("fore_y")?, e.get("PLATE_T")?)?);
            Ok(Val::None)
        })
    })?;
    // tee_axis_y
    e.set("tee_axis_y", {
        let params = vec![("fore_y".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "add",
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun83 = e.get("plate_aft_y")?;
                        let mut args81 = Vec::new();
                        let mut kw82 = Vec::new();
                        args81.push(e.get("fore_y")?);
                        fun83.call(args81, kw82)?
                    }
                },
                e.get("BORE_FACE_TO_AXIS")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // fore_valve_axis_y
    e.set("fore_valve_axis_y", {
        let params = vec![("fore_y".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun86 = e.get("tee_axis_y")?;
                    let mut args84 = Vec::new();
                    let mut kw85 = Vec::new();
                    args84.push(e.get("fore_y")?);
                    fun86.call(args84, kw85)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // tip_y
    e.set("tip_y", {
        let params = vec![("fore_y".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary("add", e.get("fore_y")?, e.get("TIP_FROM_FORE")?)?);
            Ok(Val::None)
        })
    })?;
    // tee_ports
    e.set("tee_ports", {
        let params = vec![
            ("fore_y".into(), None, false),
            ("x".into(), None, false),
            ("z".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned87 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun90 = e.get("tee_axis_y")?;
                    let mut args88 = Vec::new();
                    let mut kw89 = Vec::new();
                    args88.push(e.get("fore_y")?);
                    fun90.call(args88, kw89)?
                }
            };
            e.set("y", assigned87.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("centre".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("branch".into()), {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("point".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                                line!(),
                            );
                            {
                                let fun93 = e.get("plate_aft_y")?;
                                let mut args91 = Vec::new();
                                let mut kw92 = Vec::new();
                                args91.push(e.get("fore_y")?);
                                fun93.call(args91, kw92)?
                            }
                        });
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("axis".into()), {
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    })?;
                    d
                })?;
                d.set(Val::Str("upper".into()), {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("point".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(binary("add", e.get("z")?, e.get("RUN_FACE")?)?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("axis".into()), {
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        Val::tuple(s)
                    })?;
                    d
                })?;
                d.set(Val::Str("lower".into()), {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("point".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(binary("sub", e.get("z")?, e.get("RUN_FACE")?)?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("axis".into()), {
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        Val::tuple(s)
                    })?;
                    d
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // elbow_return
    e.set("elbow_return", {
        let params = vec![("start".into(), None, false), ("end".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned94 = {
                let mut s = Vec::new();
                s.push(e.get("start")?);
                s.push(e.get("end")?);
                Val::tuple(s)
            };
            let unpack95 = unpack(assigned94.clone(), 2)?;
            let unpack96 = unpack(unpack95[0].clone(), 3)?;
            e.set("x0", unpack96[0].clone())?;
            e.set("y0", unpack96[1].clone())?;
            e.set("z0", unpack96[2].clone())?;
            let unpack97 = unpack(unpack95[1].clone(), 3)?;
            e.set("x1", unpack97[0].clone())?;
            e.set("y1", unpack97[1].clone())?;
            e.set("z1", unpack97[2].clone())?;
            let assigned98 = binary("sub", e.get("z0")?, e.get("ELBOW_DROP")?)?;
            e.set("z", assigned98.clone())?;
            let assigned99 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun102 = e.get("max")?;
                    let mut args100 = Vec::new();
                    let mut kw101 = Vec::new();
                    args100.push(Val::Float(0.0f64));
                    args100.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                    fun102.call(args100, kw101)?
                }
            };
            e.set("showing", assigned99.clone())?;
            let assigned103 = binary(
                "sub",
                e.get("elbow")?.attr("STEM_LENGTH")?,
                e.get("VALVE_INSERTION_NOMINAL")?,
            )?;
            e.set("spare", assigned103.clone())?;
            if unary("not", {
                let v104 = unary("neg", Val::Float(1e-09f64))?;
                let v105 = e.get("showing")?;
                let v106 = binary("add", e.get("spare")?, Val::Float(1e-09f64))?;
                Val::Bool(
                    compare("le", v104.clone(), v105.clone())?.truthy()?
                        && compare("le", v105.clone(), v106.clone())?.truthy()?,
                )
            })?
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                            line!(),
                        );
                        {
                            let fun109 = e.get("ValueError")?;
                            let mut args107 = Vec::new();
                            let mut kw108 = Vec::new();
                            args107.push({
                                let mut str110 = String::new();
                                str110.push_str("the valve's collet stands ");
                                str110.push_str(&format(
                                    &binary("sub", e.get("z1")?, e.get("z0")?)?,
                                    &val_string({
                                        let mut str111 = String::new();
                                        str111.push_str("+g");
                                        Val::Str(str111)
                                    })?,
                                )?);
                                str110.push_str(" mm off the tee's, so its elbow would show ");
                                str110.push_str(&format(
                                    &e.get("showing")?,
                                    &val_string({
                                        let mut str112 = String::new();
                                        str112.push_str("g");
                                        Val::Str(str112)
                                    })?,
                                )?);
                                str110.push_str(" mm of stem below it, outside the 0 to ");
                                str110.push_str(&format(
                                    &e.get("spare")?,
                                    &val_string({
                                        let mut str113 = String::new();
                                        str113.push_str("g");
                                        Val::Str(str113)
                                    })?,
                                )?);
                                str110.push_str(" mm its stem has");
                                Val::Str(str110)
                            });
                            fun109.call(args107, kw108)?
                        }
                    })?
                );
            }
            let assigned114 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun117 = e.get("math")?.attr("hypot")?;
                    let mut args115 = Vec::new();
                    let mut kw116 = Vec::new();
                    args115.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                    args115.push(binary("sub", e.get("y1")?, e.get("y0")?)?);
                    fun117.call(args115, kw116)?
                }
            };
            e.set("span", assigned114.clone())?;
            let assigned118 = binary(
                "sub",
                e.get("span")?,
                binary(
                    "mul",
                    Val::Float(2.0f64),
                    e.get("elbow")?.attr("SOCKET_MOUTH_REACH")?,
                )?,
            )?;
            e.set("exposed", assigned118.clone())?;
            if {
                let v119 = e.get("exposed")?;
                let v120 = Val::Float(0.0f64);
                Val::Bool(compare("le", v119.clone(), v120.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                            line!(),
                        );
                        {
                            let fun123 = e.get("ValueError")?;
                            let mut args121 = Vec::new();
                            let mut kw122 = Vec::new();
                            args121.push({
                                let mut str124 = String::new();
                                str124.push_str("the ports stand ");
                                str124.push_str(&format(
                                    &e.get("span")?,
                                    &val_string({
                                        let mut str125 = String::new();
                                        str125.push_str("g");
                                        Val::Str(str125)
                                    })?,
                                )?);
                                str124.push_str(" mm apart, closer than two elbows' sockets");
                                Val::Str(str124)
                            });
                            fun123.call(args121, kw122)?
                        }
                    })?
                );
            }
            let assigned126 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun129 = e.get("_unit")?;
                    let mut args127 = Vec::new();
                    let mut kw128 = Vec::new();
                    args127.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                        s.push(binary("sub", e.get("y1")?, e.get("y0")?)?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun129.call(args127, kw128)?
                }
            };
            e.set("u", assigned126.clone())?;
            let assigned130 = {
                let mut s = Vec::new();
                s.push(unary("neg", e.get("u")?.get(Val::Int(0i64))?)?);
                s.push(unary("neg", e.get("u")?.get(Val::Int(1i64))?)?);
                s.push(Val::Float(0.0f64));
                Val::tuple(s)
            };
            e.set("back", assigned130.clone())?;
            let assigned131 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("x0")?,
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(0i64))?,
                        e.get("elbow")?.attr("SOCKET_MOUTH_REACH")?,
                    )?,
                )?);
                s.push(binary(
                    "add",
                    e.get("y0")?,
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(1i64))?,
                        e.get("elbow")?.attr("SOCKET_MOUTH_REACH")?,
                    )?,
                )?);
                s.push(e.get("z")?);
                Val::tuple(s)
            };
            e.set("mouth", assigned131.clone())?;
            let assigned132 = binary(
                "sub",
                binary("sub", e.get("z1")?, e.get("ELBOW_DROP")?)?,
                e.get("showing")?,
            )?;
            e.set("rear_z", assigned132.clone())?;
            let assigned133 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("x1")?,
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(0i64))?,
                        e.get("elbow")?.attr("SOCKET_MOUTH_REACH")?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("y1")?,
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(1i64))?,
                        e.get("elbow")?.attr("SOCKET_MOUTH_REACH")?,
                    )?,
                )?);
                s.push(e.get("rear_z")?);
                Val::tuple(s)
            };
            e.set("rear_mouth", assigned133.clone())?;
            let assigned134 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun137 = e.get("s_bend")?;
                    let mut args135 = Vec::new();
                    let mut kw136 = Vec::new();
                    args135.push(e.get("mouth")?);
                    args135.push(e.get("rear_mouth")?);
                    args135.push(e.get("u")?);
                    fun137.call(args135, kw136)?
                }
            };
            e.set("segments", assigned134.clone())?;
            let assigned138 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun141 = e.get("sum")?;
                    let mut args139 = Vec::new();
                    let mut kw140 = Vec::new();
                    args139.push({
                        let e = e.child();
                        let out142 = Val::list(vec![]);
                        for item143 in e.get("segments")?.iter()? {
                            e.set("s", item143)?;
                            out142.attr("append")?.call(
                                vec![e.get("s")?.get(Val::Str("length_mm".into()))?],
                                vec![],
                            )?;
                        }
                        out142
                    });
                    fun141.call(args139, kw140)?
                }
            };
            e.set("developed", assigned138.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("elbows".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("crossing".into()), {
                            let mut s = Vec::new();
                            s.push(e.get("x0")?);
                            s.push(e.get("y0")?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        })?;
                        d.set(Val::Str("socket".into()), e.get("u")?)?;
                        d.set(Val::Str("stem".into()), e.get("RUN_INSERTION")?)?;
                        d.set(Val::Str("showing".into()), Val::Float(0.0f64))?;
                        d
                    });
                    s.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("crossing".into()), {
                            let mut s = Vec::new();
                            s.push(e.get("x1")?);
                            s.push(e.get("y1")?);
                            s.push(e.get("rear_z")?);
                            Val::tuple(s)
                        })?;
                        d.set(Val::Str("socket".into()), e.get("back")?)?;
                        d.set(
                            Val::Str("stem".into()),
                            binary("add", e.get("VALVE_INSERTION_NOMINAL")?, e.get("showing")?)?,
                        )?;
                        d.set(Val::Str("showing".into()), e.get("showing")?)?;
                        d
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("tube".into()), e.get("segments")?)?;
                d.set(Val::Str("exposed_mm".into()), e.get("developed")?)?;
                d.set(
                    Val::Str("cut_mm".into()),
                    binary(
                        "add",
                        e.get("developed")?,
                        binary(
                            "mul",
                            Val::Float(2.0f64),
                            e.get("elbow")?.attr("SOCKET_INSERTION")?,
                        )?,
                    )?,
                )?;
                d.set(
                    Val::Str("floor_z".into()),
                    binary(
                        "sub",
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                                line!(),
                            );
                            {
                                let fun146 = e.get("min")?;
                                let mut args144 = Vec::new();
                                let mut kw145 = Vec::new();
                                args144.push(e.get("z")?);
                                args144.push(e.get("rear_z")?);
                                fun146.call(args144, kw145)?
                            }
                        },
                        binary(
                            "truediv",
                            e.get("elbow")?.attr("COLLAR_OD")?,
                            Val::Float(2.0f64),
                        )?,
                    )?,
                )?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // s_bend
    e.set("s_bend",{let params=vec![("start".into(),None,false),("end".into(),None,false),("direction".into(),Some({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));Val::tuple(s)}),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned147={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun150=e.get("_unit")?;let mut args148=Vec::new();let mut kw149=Vec::new();args148.push(e.get("direction")?);fun150.call(args148,kw149)?}};e.set("up",assigned147.clone())?;
let assigned151={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun154=e.get("tuple")?;let mut args152=Vec::new();let mut kw153=Vec::new();args152.push({let e=e.child();let out155=Val::list(vec![]);for item156 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun159=e.get("range")?;let mut args157=Vec::new();let mut kw158=Vec::new();args157.push(Val::Int(3i64));fun159.call(args157,kw158)?}}.iter()? {e.set("i",item156)?;out155.attr("append")?.call(vec![binary("sub",e.get("end")?.get(e.get("i")?)?,e.get("start")?.get(e.get("i")?)?)?],vec![])?;}out155});fun154.call(args152,kw153)?}};e.set("delta",assigned151.clone())?;
let assigned160={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun163=e.get("sum")?;let mut args161=Vec::new();let mut kw162=Vec::new();args161.push({let e=e.child();let out164=Val::list(vec![]);for item165 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun168=e.get("range")?;let mut args166=Vec::new();let mut kw167=Vec::new();args166.push(Val::Int(3i64));fun168.call(args166,kw167)?}}.iter()? {e.set("i",item165)?;out164.attr("append")?.call(vec![binary("mul",e.get("delta")?.get(e.get("i")?)?,e.get("up")?.get(e.get("i")?)?)?],vec![])?;}out164});fun163.call(args161,kw162)?}};e.set("length",assigned160.clone())?;
let assigned169={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun172=e.get("tuple")?;let mut args170=Vec::new();let mut kw171=Vec::new();args170.push({let e=e.child();let out173=Val::list(vec![]);for item174 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun177=e.get("range")?;let mut args175=Vec::new();let mut kw176=Vec::new();args175.push(Val::Int(3i64));fun177.call(args175,kw176)?}}.iter()? {e.set("i",item174)?;out173.attr("append")?.call(vec![binary("sub",e.get("delta")?.get(e.get("i")?)?,binary("mul",e.get("length")?,e.get("up")?.get(e.get("i")?)?)?)?],vec![])?;}out173});fun172.call(args170,kw171)?}};e.set("lateral",assigned169.clone())?;
let assigned178={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun181=e.get("math")?.attr("sqrt")?;let mut args179=Vec::new();let mut kw180=Vec::new();args179.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun184=e.get("sum")?;let mut args182=Vec::new();let mut kw183=Vec::new();args182.push({let e=e.child();let out185=Val::list(vec![]);for item186 in e.get("lateral")?.iter()? {e.set("v",item186)?;out185.attr("append")?.call(vec![binary("mul",e.get("v")?,e.get("v")?)?],vec![])?;}out185});fun184.call(args182,kw183)?}});fun181.call(args179,kw180)?}};e.set("offset",assigned178.clone())?;
if {let v187=e.get("offset")?;let v188=Val::Float(1e-09f64);Val::Bool(compare("lt",v187.clone(),v188.clone())?.truthy()?)}.truthy()? {
return Ok({let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun191=e.get("_line")?;let mut args189=Vec::new();let mut kw190=Vec::new();args189.push(e.get("start")?);args189.push(e.get("up")?);args189.push(e.get("length")?);fun191.call(args189,kw190)?}});Val::tuple(s)});
}
let assigned192={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun195=e.get("_unit")?;let mut args193=Vec::new();let mut kw194=Vec::new();args193.push(e.get("lateral")?);fun195.call(args193,kw194)?}};e.set("side",assigned192.clone())?;
let assigned196=binary("mul",Val::Float(2.0f64),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun199=e.get("math")?.attr("atan2")?;let mut args197=Vec::new();let mut kw198=Vec::new();args197.push(e.get("offset")?);args197.push(e.get("length")?);fun199.call(args197,kw198)?}})?;e.set("theta",assigned196.clone())?;
let assigned200=binary("truediv",e.get("length")?,binary("mul",Val::Float(2.0f64),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun203=e.get("math")?.attr("sin")?;let mut args201=Vec::new();let mut kw202=Vec::new();args201.push(e.get("theta")?);fun203.call(args201,kw202)?}})?)?;e.set("r",assigned200.clone())?;
let assigned204={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun207=e.get("_add")?;let mut args205=Vec::new();let mut kw206=Vec::new();args205.push(e.get("start")?);args205.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun210=e.get("_scale")?;let mut args208=Vec::new();let mut kw209=Vec::new();args208.push(e.get("side")?);args208.push(e.get("r")?);fun210.call(args208,kw209)?}});fun207.call(args205,kw206)?}};e.set("centre",assigned204.clone())?;
// at
e.set("at",{let params=vec![("phi".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun213=e.get("_add")?;let mut args211=Vec::new();let mut kw212=Vec::new();args211.push(e.get("centre")?);args211.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun216=e.get("_add")?;let mut args214=Vec::new();let mut kw215=Vec::new();args214.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun219=e.get("_scale")?;let mut args217=Vec::new();let mut kw218=Vec::new();args217.push(e.get("side")?);args217.push(binary("mul",unary("neg",e.get("r")?)?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun222=e.get("math")?.attr("cos")?;let mut args220=Vec::new();let mut kw221=Vec::new();args220.push(e.get("phi")?);fun222.call(args220,kw221)?}})?);fun219.call(args217,kw218)?}});args214.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun225=e.get("_scale")?;let mut args223=Vec::new();let mut kw224=Vec::new();args223.push(e.get("up")?);args223.push(binary("mul",e.get("r")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun228=e.get("math")?.attr("sin")?;let mut args226=Vec::new();let mut kw227=Vec::new();args226.push(e.get("phi")?);fun228.call(args226,kw227)?}})?);fun225.call(args223,kw224)?}});fun216.call(args214,kw215)?}});fun213.call(args211,kw212)?}});
Ok(Val::None)})})?;
let assigned229={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun232=e.get("at")?;let mut args230=Vec::new();let mut kw231=Vec::new();args230.push(e.get("theta")?);fun232.call(args230,kw231)?}};e.set("mid",assigned229.clone())?;
let assigned233={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun236=e.get("_add")?;let mut args234=Vec::new();let mut kw235=Vec::new();args234.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun239=e.get("_scale")?;let mut args237=Vec::new();let mut kw238=Vec::new();args237.push(e.get("side")?);args237.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun242=e.get("math")?.attr("sin")?;let mut args240=Vec::new();let mut kw241=Vec::new();args240.push(e.get("theta")?);fun242.call(args240,kw241)?}});fun239.call(args237,kw238)?}});args234.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun245=e.get("_scale")?;let mut args243=Vec::new();let mut kw244=Vec::new();args243.push(e.get("up")?);args243.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun248=e.get("math")?.attr("cos")?;let mut args246=Vec::new();let mut kw247=Vec::new();args246.push(e.get("theta")?);fun248.call(args246,kw247)?}});fun245.call(args243,kw244)?}});fun236.call(args234,kw235)?}};e.set("turn",assigned233.clone())?;
let assigned249={let d=Val::dict(vec![]);d.set(Val::Str("kind".into()),Val::Str("arc".into()))?;d.set(Val::Str("start_mm".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun252=e.get("tuple")?;let mut args250=Vec::new();let mut kw251=Vec::new();args250.push(e.get("start")?);fun252.call(args250,kw251)?}})?;d.set(Val::Str("midpoint_mm".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun255=e.get("at")?;let mut args253=Vec::new();let mut kw254=Vec::new();args253.push(binary("truediv",e.get("theta")?,Val::Float(2.0f64))?);fun255.call(args253,kw254)?}})?;d.set(Val::Str("end_mm".into()),e.get("mid")?)?;d.set(Val::Str("radius_mm".into()),e.get("r")?)?;d.set(Val::Str("sweep_degrees".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun258=e.get("math")?.attr("degrees")?;let mut args256=Vec::new();let mut kw257=Vec::new();args256.push(e.get("theta")?);fun258.call(args256,kw257)?}})?;d.set(Val::Str("start_tangent".into()),e.get("up")?)?;d.set(Val::Str("end_tangent".into()),e.get("turn")?)?;d.set(Val::Str("length_mm".into()),binary("mul",e.get("r")?,e.get("theta")?)?)?;d};e.set("first",assigned249.clone())?;
let assigned259={let params=vec![("p".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun262=e.get("tuple")?;let mut args260=Vec::new();let mut kw261=Vec::new();args260.push({let e=e.child();let out263=Val::list(vec![]);for item264 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun267=e.get("range")?;let mut args265=Vec::new();let mut kw266=Vec::new();args265.push(Val::Int(3i64));fun267.call(args265,kw266)?}}.iter()? {e.set("i",item264)?;out263.attr("append")?.call(vec![binary("sub",binary("mul",Val::Float(2.0f64),e.get("mid")?.get(e.get("i")?)?)?,e.get("p")?.get(e.get("i")?)?)?],vec![])?;}out263});fun262.call(args260,kw261)?}});
Ok(Val::None)})};e.set("mirror",assigned259.clone())?;
let assigned268={let d=Val::dict(vec![]);d.set(Val::Str("kind".into()),Val::Str("arc".into()))?;d.set(Val::Str("start_mm".into()),e.get("mid")?)?;d.set(Val::Str("midpoint_mm".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun271=e.get("mirror")?;let mut args269=Vec::new();let mut kw270=Vec::new();args269.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun274=e.get("at")?;let mut args272=Vec::new();let mut kw273=Vec::new();args272.push(binary("truediv",e.get("theta")?,Val::Float(2.0f64))?);fun274.call(args272,kw273)?}});fun271.call(args269,kw270)?}})?;d.set(Val::Str("end_mm".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun277=e.get("tuple")?;let mut args275=Vec::new();let mut kw276=Vec::new();args275.push(e.get("end")?);fun277.call(args275,kw276)?}})?;d.set(Val::Str("radius_mm".into()),e.get("r")?)?;d.set(Val::Str("sweep_degrees".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun280=e.get("math")?.attr("degrees")?;let mut args278=Vec::new();let mut kw279=Vec::new();args278.push(e.get("theta")?);fun280.call(args278,kw279)?}})?;d.set(Val::Str("start_tangent".into()),e.get("turn")?)?;d.set(Val::Str("end_tangent".into()),e.get("up")?)?;d.set(Val::Str("length_mm".into()),binary("mul",e.get("r")?,e.get("theta")?)?)?;d};e.set("second",assigned268.clone())?;
return Ok({let mut s=Vec::new();s.push(e.get("first")?);s.push(e.get("second")?);Val::tuple(s)});
Ok(Val::None)})})?;
    // station
    e.set("station", {
        let params = vec![
            ("fore_y".into(), None, false),
            ("x".into(), None, false),
            ("z".into(), None, false),
            ("upper_port".into(), None, false),
            ("return_port".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned281 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun284 = e.get("tee_ports")?;
                    let mut args282 = Vec::new();
                    let mut kw283 = Vec::new();
                    args282.push(e.get("fore_y")?);
                    args282.push(e.get("x")?);
                    args282.push(e.get("z")?);
                    fun284.call(args282, kw283)?
                }
            };
            e.set("ports", assigned281.clone())?;
            let assigned285 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun288 = e.get("s_bend")?;
                    let mut args286 = Vec::new();
                    let mut kw287 = Vec::new();
                    args286.push(
                        e.get("ports")?
                            .get(Val::Str("upper".into()))?
                            .get(Val::Str("point".into()))?,
                    );
                    args286.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                            line!(),
                        );
                        {
                            let fun291 = e.get("tuple")?;
                            let mut args289 = Vec::new();
                            let mut kw290 = Vec::new();
                            args289.push(e.get("upper_port")?.get(Val::Str("point".into()))?);
                            fun291.call(args289, kw290)?
                        }
                    });
                    fun288.call(args286, kw287)?
                }
            };
            e.set("upper", assigned285.clone())?;
            let assigned292 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun295 = e.get("elbow_return")?;
                    let mut args293 = Vec::new();
                    let mut kw294 = Vec::new();
                    args293.push(
                        e.get("ports")?
                            .get(Val::Str("lower".into()))?
                            .get(Val::Str("point".into()))?,
                    );
                    args293.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                            line!(),
                        );
                        {
                            let fun298 = e.get("tuple")?;
                            let mut args296 = Vec::new();
                            let mut kw297 = Vec::new();
                            args296.push(e.get("return_port")?.get(Val::Str("point".into()))?);
                            fun298.call(args296, kw297)?
                        }
                    });
                    fun295.call(args293, kw294)?
                }
            };
            e.set("lower", assigned292.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("tee".into()), e.get("ports")?)?;
                d.set(Val::Str("upper_target".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun301 = e.get("dict")?;
                        let mut args299 = Vec::new();
                        let mut kw300 = Vec::new();
                        args299.push(e.get("upper_port")?);
                        fun301.call(args299, kw300)?
                    }
                })?;
                d.set(Val::Str("return_target".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun304 = e.get("dict")?;
                        let mut args302 = Vec::new();
                        let mut kw303 = Vec::new();
                        args302.push(e.get("return_port")?);
                        fun304.call(args302, kw303)?
                    }
                })?;
                d.set(Val::Str("upper_tube".into()), e.get("upper")?)?;
                d.set(Val::Str("return".into()), e.get("lower")?)?;
                d.set(Val::Str("upper_exposed_mm".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                        line!(),
                    );
                    {
                        let fun307 = e.get("sum")?;
                        let mut args305 = Vec::new();
                        let mut kw306 = Vec::new();
                        args305.push({
                            let e = e.child();
                            let out308 = Val::list(vec![]);
                            for item309 in e.get("upper")?.iter()? {
                                e.set("s", item309)?;
                                out308.attr("append")?.call(
                                    vec![e.get("s")?.get(Val::Str("length_mm".into()))?],
                                    vec![],
                                )?;
                            }
                            out308
                        });
                        fun307.call(args305, kw306)?
                    }
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // layouts
    e.set("layouts",{let params=vec![("plate".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let e=e.child();let out310=Val::dict(vec![]);for item311 in e.get("plate")?.get(Val::Str("holes".into()))?.iter()? {let unpack312=unpack(item311,2)?;e.set("x",unpack312[0].clone())?;e.set("z",unpack312[1].clone())?;out310.set({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun315=e.get("str")?;let mut args313=Vec::new();let mut kw314=Vec::new();args313.push(e.get("x")?);fun315.call(args313,kw314)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun318=e.get("station")?;let mut args316=Vec::new();let mut kw317=Vec::new();args316.push(e.get("plate")?.get(Val::Str("fore_y".into()))?);args316.push(e.get("x")?);args316.push(e.get("z")?);args316.push(e.get("plate")?.get(Val::Str("upper_ports".into()))?.get({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun321=e.get("str")?;let mut args319=Vec::new();let mut kw320=Vec::new();args319.push(e.get("x")?);fun321.call(args319,kw320)?}})?);args316.push(e.get("plate")?.get(Val::Str("return_ports".into()))?.get({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun324=e.get("str")?;let mut args322=Vec::new();let mut kw323=Vec::new();args322.push(e.get("x")?);fun324.call(args322,kw323)?}})?);fun318.call(args316,kw317)?}})?;}out310});
Ok(Val::None)})})?;
    // sweep
    e.set("sweep",{let params=vec![("diameter".into(),None,false),("segments".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("cq",rt.import_module("cadquery")?)?;
let assigned325={let mut s=Vec::new();Val::list(s)};e.set("edges",assigned325.clone())?;
for item326 in e.get("segments")?.iter()? {
e.set("s",item326)?;let assigned327={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun330=e.get("cq")?.attr("Vector")?;let mut args328=Vec::new();let mut kw329=Vec::new();args328.extend(e.get("s")?.get(Val::Str("start_mm".into()))?.iter()?);fun330.call(args328,kw329)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun333=e.get("cq")?.attr("Vector")?;let mut args331=Vec::new();let mut kw332=Vec::new();args331.extend(e.get("s")?.get(Val::Str("end_mm".into()))?.iter()?);fun333.call(args331,kw332)?}});Val::tuple(s)};let unpack334=unpack(assigned327.clone(),2)?;e.set("a",unpack334[0].clone())?;e.set("b",unpack334[1].clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun337=e.get("edges")?.attr("append")?;let mut args335=Vec::new();let mut kw336=Vec::new();args335.push(if {let v338=e.get("s")?.get(Val::Str("kind".into()))?;let v339=Val::Str("arc".into());Val::Bool(compare("eq",v338.clone(),v339.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun342=e.get("cq")?.attr("Edge")?.attr("makeThreePointArc")?;let mut args340=Vec::new();let mut kw341=Vec::new();args340.push(e.get("a")?);args340.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun345=e.get("cq")?.attr("Vector")?;let mut args343=Vec::new();let mut kw344=Vec::new();args343.extend(e.get("s")?.get(Val::Str("midpoint_mm".into()))?.iter()?);fun345.call(args343,kw344)?}});args340.push(e.get("b")?);fun342.call(args340,kw341)?}}} else {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun348=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args346=Vec::new();let mut kw347=Vec::new();args346.push(e.get("a")?);args346.push(e.get("b")?);fun348.call(args346,kw347)?}}});fun337.call(args335,kw336)?}};
}
let assigned349=e.get("segments")?.get(Val::Int(0i64))?;e.set("first",assigned349.clone())?;
let assigned350={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun353=e.get("cq")?.attr("Wire")?.attr("makeCircle")?;let mut args351=Vec::new();let mut kw352=Vec::new();args351.push(binary("truediv",e.get("diameter")?,Val::Float(2.0f64))?);args351.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun356=e.get("cq")?.attr("Vector")?;let mut args354=Vec::new();let mut kw355=Vec::new();args354.extend(e.get("first")?.get(Val::Str("start_mm".into()))?.iter()?);fun356.call(args354,kw355)?}});args351.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun359=e.get("cq")?.attr("Vector")?;let mut args357=Vec::new();let mut kw358=Vec::new();args357.extend(e.get("first")?.get(Val::Str("start_tangent".into()))?.iter()?);fun359.call(args357,kw358)?}});fun353.call(args351,kw352)?}};e.set("profile",assigned350.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun362=e.get("cq")?.attr("Solid")?.attr("sweep")?;let mut args360=Vec::new();let mut kw361=Vec::new();args360.push(e.get("profile")?);args360.push({let mut s=Vec::new();Val::list(s)});args360.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",line!());{let fun365=e.get("cq")?.attr("Wire")?.attr("assembleEdges")?;let mut args363=Vec::new();let mut kw364=Vec::new();args363.push(e.get("edges")?);fun365.call(args363,kw364)?}});kw361.push(("makeSolid".into(),Val::Bool(true)));kw361.push(("isFrenet".into(),Val::Bool(true)));fun362.call(args360,kw361)?}});
Ok(Val::None)})})?;
    // tube
    e.set("tube", {
        let params = vec![("segments".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                    line!(),
                );
                {
                    let fun368 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                            line!(),
                        );
                        {
                            let fun371 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                                    line!(),
                                );
                                {
                                    let fun374 = e.get("sweep")?;
                                    let mut args372 = Vec::new();
                                    let mut kw373 = Vec::new();
                                    args372.push(e.get("TUBE_OD")?);
                                    args372.push(e.get("segments")?);
                                    fun374.call(args372, kw373)?
                                }
                            }
                            .attr("cut")?;
                            let mut args369 = Vec::new();
                            let mut kw370 = Vec::new();
                            args369.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/fixed_returns.rs",
                                    line!(),
                                );
                                {
                                    let fun377 = e.get("sweep")?;
                                    let mut args375 = Vec::new();
                                    let mut kw376 = Vec::new();
                                    args375.push(e.get("TUBE_ID")?);
                                    args375.push(e.get("segments")?);
                                    fun377.call(args375, kw376)?
                                }
                            });
                            fun371.call(args369, kw370)?
                        }
                    }
                    .attr("clean")?;
                    let mut args366 = Vec::new();
                    let mut kw367 = Vec::new();
                    fun368.call(args366, kw367)?
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
