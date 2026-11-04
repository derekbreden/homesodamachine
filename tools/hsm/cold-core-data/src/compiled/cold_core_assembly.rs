#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
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
    let assigned17 = binary(
        "truediv",
        binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
        Val::Str("cold-core".into()),
    )?;
    e.set("_cold", assigned17.clone())?;
    for item18 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            e.get("_hw")?,
            Val::Str("scripts".into()),
        )?);
        s.push(e.get("_cold")?);
        s.push(binary(
            "truediv",
            e.get("_cold")?,
            Val::Str("foam-assembly".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("_cold")?,
            Val::Str("reservoir".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("_cold")?,
            Val::Str("prv-shroud".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
            Val::Str("cadlib".into()),
        )?);
        s.push(e.get("_here")?.attr("parent")?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_p", item18)?;
        if {
            let v22 = {
                let fun21 = e.get("str")?;
                let mut args19 = Vec::new();
                let mut kw20 = Vec::new();
                args19.push(e.get("_p")?);
                fun21.call(args19, kw20)?
            };
            let v23 = e.get("sys")?.attr("path")?;
            Val::Bool(compare("not_in", v22.clone(), v23.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args24 = Vec::new();
                let mut kw25 = Vec::new();
                args24.push(Val::Int(0i64));
                args24.push({
                    let fun29 = e.get("str")?;
                    let mut args27 = Vec::new();
                    let mut kw28 = Vec::new();
                    args27.push(e.get("_p")?);
                    fun29.call(args27, kw28)?
                });
                fun26.call(args24, kw25)?
            };
        }
    }
    e.set("_foam", rt.import_module("foam_assembly")?)?;
    e.set("_routes", rt.import_module("_internal_routes")?)?;
    let mod30 = rt.import_module("_cold_core_interface")?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    e.set(
        "carbonator_sensor_azimuth",
        rt.member("_cold_core_interface", "carbonator_sensor_azimuth")?,
    )?;
    e.set("_V", rt.import_module("_carbonator")?)?;
    e.set("_C", rt.import_module("_coil")?)?;
    e.set("_F", rt.import_module("_fittings")?)?;
    e.set("_I", rt.import_module("_internals")?)?;
    e.set("_bom_check", rt.import_module("_bom")?)?;
    e.set("_shroud", rt.import_module("prv_shroud")?)?;
    e.set("_card", rt.import_module("_cold_scorecard")?)?;
    e.set("_style", rt.import_module("_cold_core_style")?)?;
    e.set("_tube_ports", rt.import_module("_reservoir_ports")?)?;
    e.set("_above_mounts", rt.import_module("_above_core_mounts")?)?;
    let mod31 = rt.import_module("_card")?;
    e.set("Check", rt.member("_card", "Check")?)?;
    e.set("grade_of", rt.member("_card", "grade_of")?)?;
    e.set("verdict", rt.member("_card", "verdict")?)?;
    let mod32 = rt.import_module("_cold_scorecard")?;
    e.set("Scorecard", rt.member("_cold_scorecard", "Scorecard")?)?;
    let assigned33 = binary(
        "truediv",
        e.get("_here")?.attr("parent")?,
        Val::Str("cold-core-assembly.step".into()),
    )?;
    e.set("STEP_OUT", assigned33.clone())?;
    let assigned34 = binary(
        "truediv",
        e.get("_here")?.attr("parent")?,
        Val::Str("cold-core-assembly.scene.npz".into()),
    )?;
    e.set("MODEL_OUT", assigned34.clone())?;
    let assigned35 = binary(
        "truediv",
        binary("truediv", e.get("_cold")?, Val::Str("foam-assembly".into()))?,
        Val::Str("foam-assembly.step".into()),
    )?;
    e.set("FOAM_STEP", assigned35.clone())?;
    let assigned36 = {
        let d = Val::dict(vec![]);
        d.set(
            Val::Str("reservoir-a".into()),
            Val::Str("reservoir-right".into()),
        )?;
        d.set(
            Val::Str("reservoir-b".into()),
            Val::Str("reservoir-left".into()),
        )?;
        d
    };
    e.set("RESERVOIRS", assigned36.clone())?;
    let assigned37 = {
        let fun40 = e.get("dict")?;
        let mut args38 = Vec::new();
        let mut kw39 = Vec::new();
        kw39.push(("shaft_radius".into(), Val::Float(2.5f64)));
        kw39.push(("shaft_length".into(), Val::Float(100.0f64)));
        kw39.push(("head_radius".into(), Val::Float(4.25f64)));
        kw39.push(("head_height".into(), Val::Float(5.0f64)));
        kw39.push(("socket_af".into(), Val::Float(4.0f64)));
        kw39.push(("socket_depth".into(), Val::Float(2.5f64)));
        kw39.push(("tool_overrun".into(), Val::Float(0.1f64)));
        fun40.call(args38, kw39)?
    };
    e.set("CAP_CLAMP", assigned37.clone())?;
    let assigned41 = {
        let d = Val::dict(vec![]);
        d.set(
            Val::Str("foam-shell".into()),
            Val::Str("the enclosure floor".into()),
        )?;
        d.set(
            Val::Str("foam-cap-lid-top".into()),
            Val::Str("M5 shell-face inserts".into()),
        )?;
        d.set(
            Val::Str("reservoir-b-fill-guide".into()),
            Val::Str("B-fill tube and cured foam".into()),
        )?;
        d.set(
            Val::Str("foam-cap-bottom".into()),
            Val::Str("shell floor".into()),
        )?;
        d.set(
            Val::Str("carbonator-tube".into()),
            Val::Str("support ring".into()),
        )?;
        d.set(
            Val::Str("endcap-bottom".into()),
            Val::Str("tube bore".into()),
        )?;
        d.set(Val::Str("endcap-top".into()), Val::Str("tube bore".into()))?;
        d.set(
            Val::Str("float-rod-carb".into()),
            Val::Str("plate registers".into()),
        )?;
        d.set(
            Val::Str("float-stop-carb-top".into()),
            Val::Str("top plate inside face".into()),
        )?;
        d.set(
            Val::Str("carbonator-earth-screw".into()),
            Val::Str("tapped upper tube rim".into()),
        )?;
        d.set(
            Val::Str("carbonator-earth-lockwasher".into()),
            Val::Str("rim screw/ring clamp".into()),
        )?;
        d.set(Val::Str("reservoir-a".into()), Val::Str("pocket".into()))?;
        d.set(Val::Str("reservoir-b".into()), Val::Str("pocket".into()))?;
        d.set(
            Val::Str("reservoir-a-gasket".into()),
            Val::Str("body rim".into()),
        )?;
        d.set(
            Val::Str("reservoir-b-gasket".into()),
            Val::Str("body rim".into()),
        )?;
        d.set(
            Val::Str("reservoir-a-cap".into()),
            Val::Str("the gasket on the body rim".into()),
        )?;
        d.set(
            Val::Str("reservoir-b-cap".into()),
            Val::Str("the gasket on the body rim".into()),
        )?;
        d.set(
            Val::Str("prv-shroud".into()),
            Val::Str("the PRV it caps".into()),
        )?;
        d.set(
            Val::Str("prv-sv125".into()),
            Val::Str("elbow socket".into()),
        )?;
        d.set(
            Val::Str("reed-bridge".into()),
            Val::Str("support ring".into()),
        )?;
        d.set(
            Val::Str("evap-coil".into()),
            Val::Str("the carbonator it clamps".into()),
        )?;
        d.set(
            Val::Str("evap-tail-inlet".into()),
            Val::Str("copper feed-through".into()),
        )?;
        d.set(
            Val::Str("evap-tail-outlet".into()),
            Val::Str("copper feed-through".into()),
        )?;
        d.set(
            Val::Str("water-inlet-jet-cap-nominal".into()),
            Val::Str("water elbow tip weld (unqualified)".into()),
        )?;
        d
    };
    e.set("HELD_BY", assigned41.clone())?;
    for item42 in e.get("_V")?.attr("PORTS")?.iter()? {
        e.set("_n", item42)?;
        let assigned43 = Val::Str("plate thread".into());
        e.get("HELD_BY")?.set(
            {
                let mut str44 = String::new();
                str44.push_str("carbonator-elbow-");
                str44.push_str(&format(&e.get("_n")?, &String::new())?);
                Val::Str(str44)
            },
            assigned43.clone(),
        )?;
    }
    let assigned45 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("cap-clamp-".into()));
            s.push(Val::Str("M5 shell-face insert".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("collet-".into()));
            s.push(Val::Str("elbow socket".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reservoir-grip-".into()));
            s.push(Val::Str(
                "matching double countersink in reservoir lid".into(),
            ));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("tube-reservoir-air-".into()));
            s.push(Val::Str("reservoir TPU air grip".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("float-rod-".into()));
            s.push(Val::Str("body boss".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("float-".into()));
            s.push(Val::Str("the rod it rides".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reed-carb-".into()));
            s.push(Val::Str("bridge pocket".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reed-".into()));
            s.push(Val::Str("shell channel".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("probe-".into()));
            s.push(Val::Str("foil tape".into()));
            Val::tuple(s)
        });
        Val::tuple(s)
    };
    e.set("HELD_BY_PREFIX", assigned45.clone())?;
    let assigned46 = {
        let mut s = Vec::new();
        s.push(Val::Str("the pour".into()));
        s.push(Val::Str("foil tape".into()));
        Val::tuple(s)
    };
    e.set("NOT_A_FEATURE", assigned46.clone())?;
    // held_for
    e.set("held_for", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v47 = e.get("name")?;
                let v48 = e.get("HELD_BY")?;
                Val::Bool(compare("in", v47.clone(), v48.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("HELD_BY")?.get(e.get("name")?)?);
            }
            for item49 in e.get("HELD_BY_PREFIX")?.iter()? {
                let unpack53 = unpack(item49, 2)?;
                e.set("prefix", unpack53[0].clone())?;
                e.set("held", unpack53[1].clone())?;
                if {
                    let fun52 = e.get("name")?.attr("startswith")?;
                    let mut args50 = Vec::new();
                    let mut kw51 = Vec::new();
                    args50.push(e.get("prefix")?);
                    fun52.call(args50, kw51)?
                }
                .truthy()?
                {
                    return Ok(e.get("held")?);
                }
            }
            return Ok(Val::Str("the pour".into()));
            Ok(Val::None)
        })
    })?;
    let assigned54 = {
        let e = e.child();
        let out55 = Val::set_values(vec![]);
        for item56 in {
            let mut s = Vec::new();
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("evap-coil".into()));
                s.push(Val::Str("evap-tail-inlet".into()));
                Val::tuple(s)
            });
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("evap-coil".into()));
                s.push(Val::Str("evap-tail-outlet".into()));
                Val::tuple(s)
            });
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("tube-reservoir-air-a".into()));
                s.push(Val::Str("reservoir-grip-a-air".into()));
                Val::tuple(s)
            });
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("tube-reservoir-air-b".into()));
                s.push(Val::Str("reservoir-grip-b-air".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        }
        .iter()?
        {
            e.set("p", item56)?;
            out55.attr("add")?.call(
                vec![{
                    let fun59 = e.get("frozenset")?;
                    let mut args57 = Vec::new();
                    let mut kw58 = Vec::new();
                    args57.push(e.get("p")?);
                    fun59.call(args57, kw58)?
                }],
                vec![],
            )?;
        }
        out55
    };
    e.set("JOINED", assigned54.clone())?;
    let assigned60 = {
        let e = e.child();
        let out61 = Val::set_values(vec![]);
        for item62 in {
            let mut s = Vec::new();
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("evap-coil".into()));
                s.push(Val::Str("carbonator-tube".into()));
                Val::tuple(s)
            });
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("evap-coil".into()));
                s.push(Val::Str("reed-bridge".into()));
                Val::tuple(s)
            });
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("evap-coil".into()));
                s.push(Val::Str("reed-carb-1".into()));
                Val::tuple(s)
            });
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("evap-coil".into()));
                s.push(Val::Str("reed-carb-2".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        }
        .iter()?
        {
            e.set("p", item62)?;
            out61.attr("add")?.call(
                vec![{
                    let fun65 = e.get("frozenset")?;
                    let mut args63 = Vec::new();
                    let mut kw64 = Vec::new();
                    args63.push(e.get("p")?);
                    fun65.call(args63, kw64)?
                }],
                vec![],
            )?;
        }
        out61
    };
    e.set("RIDES_ON", assigned60.clone())?;
    let assigned66 = {
        let mut s = Vec::new();
        s.push(Val::Str("evap-tail-inlet".into()));
        s.push(Val::Str("evap-tail-outlet".into()));
        Val::tuple(s)
    };
    e.set("TAIL_LINES", assigned66.clone())?;
    let assigned67 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("co2-in".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("carbonator-elbow-co2-in".into()));
            Val::tuple(s)
        })?;
        d.set(Val::Str("carb-water-out".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("carbonator-elbow-carb-water-out".into()));
            Val::tuple(s)
        })?;
        d.set(Val::Str("water-in".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("collet-water-in".into()));
            s.push(Val::Str("carbonator-elbow-water-in".into()));
            Val::tuple(s)
        })?;
        d.set(Val::Str("prv-vent".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("prv-shroud".into()));
            Val::tuple(s)
        })?;
        d.set(Val::Str("reservoir-b-fill".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("reservoir-grip-b-fill".into()));
            Val::tuple(s)
        })?;
        d.set(Val::Str("reservoir-a".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("reservoir-grip-a-draw".into()));
            Val::tuple(s)
        })?;
        d.set(Val::Str("reservoir-b".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("reservoir-grip-b-draw".into()));
            Val::tuple(s)
        })?;
        d.set(Val::Str("reservoir-a-fill".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("reservoir-grip-a-fill".into()));
            Val::tuple(s)
        })?;
        d
    };
    e.set("MADE_UP_ON", assigned67.clone())?;
    let assigned68 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.0f64));
        s.push(unary("neg", Val::Float(1.0f64))?);
        s.push(Val::Float(0.0f64));
        Val::tuple(s)
    };
    e.set("VENT_LOCAL", assigned68.clone())?;
    let assigned69 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.0f64));
        s.push(Val::Float(0.0f64));
        s.push(unary("neg", Val::Float(1.0f64))?);
        Val::tuple(s)
    };
    e.set("VENT_WORLD", assigned69.clone())?;
    // _bodies_clear
    e.set("_bodies_clear", {
        let params = vec![
            ("placed".into(), None, false),
            ("volumes".into(), None, true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned70 = {
                let fun73 = e.get("sorted")?;
                let mut args71 = Vec::new();
                let mut kw72 = Vec::new();
                args71.push(e.get("placed")?);
                fun73.call(args71, kw72)?
            };
            e.set("names", assigned70.clone())?;
            let assigned74 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("detail", assigned74.clone())?;
            for item75 in {
                let fun101 = e.get("enumerate")?;
                let mut args99 = Vec::new();
                let mut kw100 = Vec::new();
                args99.push(e.get("names")?);
                fun101.call(args99, kw100)?
            }
            .iter()?
            {
                let unpack102 = unpack(item75, 2)?;
                e.set("i", unpack102[0].clone())?;
                e.set("a", unpack102[1].clone())?;
                for item76 in e
                    .get("names")?
                    .get(Val::Slice {
                        start: Some(binary("add", e.get("i")?, Val::Int(1i64))?.integer()?),
                        stop: None,
                        step: 1,
                    })?
                    .iter()?
                {
                    e.set("b", item76)?;
                    if {
                        let v82 = {
                            let v86 = {
                                let fun85 = e.get("frozenset")?;
                                let mut args83 = Vec::new();
                                let mut kw84 = Vec::new();
                                args83.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("a")?);
                                    s.push(e.get("b")?);
                                    Val::tuple(s)
                                });
                                fun85.call(args83, kw84)?
                            };
                            let v87 = e.get("JOINED")?;
                            Val::Bool(compare("in", v86.clone(), v87.clone())?.truthy()?)
                        };
                        if v82.truthy()? {
                            v82
                        } else {
                            {
                                let v80 = {
                                    let fun79 = e.get("frozenset")?;
                                    let mut args77 = Vec::new();
                                    let mut kw78 = Vec::new();
                                    args77.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("a")?);
                                        s.push(e.get("b")?);
                                        Val::tuple(s)
                                    });
                                    fun79.call(args77, kw78)?
                                };
                                let v81 = e.get("RIDES_ON")?;
                                Val::Bool(compare("in", v80.clone(), v81.clone())?.truthy()?)
                            }
                        }
                    }
                    .truthy()?
                    {
                        continue;
                    }
                    let assigned88 = {
                        let fun91 = e.get("volumes")?;
                        let mut args89 = Vec::new();
                        let mut kw90 = Vec::new();
                        args89.push(e.get("a")?);
                        args89.push(e.get("b")?);
                        fun91.call(args89, kw90)?
                    };
                    e.set("vol", assigned88.clone())?;
                    if {
                        let v92 = e.get("vol")?;
                        let v93 = e.get("_card")?.attr("TOUCH_VOLUME")?;
                        Val::Bool(compare("gt", v92.clone(), v93.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun96 = e.get("detail")?.attr("append")?;
                            let mut args94 = Vec::new();
                            let mut kw95 = Vec::new();
                            args94.push({
                                let mut str97 = String::new();
                                str97.push_str(&format(&e.get("a")?, &String::new())?);
                                str97.push_str(" ∩ ");
                                str97.push_str(&format(&e.get("b")?, &String::new())?);
                                str97.push_str(" = ");
                                str97.push_str(&format(
                                    &e.get("vol")?,
                                    &val_string({
                                        let mut str98 = String::new();
                                        str98.push_str(".2f");
                                        Val::Str(str98)
                                    })?,
                                )?);
                                str97.push_str(" mm³");
                                Val::Str(str97)
                            });
                            fun96.call(args94, kw95)?
                        };
                    }
                }
            }
            {
                let fun105 = e.get("detail")?.attr("sort")?;
                let mut args103 = Vec::new();
                let mut kw104 = Vec::new();
                kw104.push(("key".into(), {
                    let params = vec![("s".into(), None, false)];
                    let outer = e.clone();
                    let runtime = rt.clone();
                    Val::function(move |args, kwargs| {
                        let rt = runtime.clone();
                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                        let _frame = rt.frame(&outer);
                        return Ok(unary("neg", {
                            let fun108 = e.get("float")?;
                            let mut args106 = Vec::new();
                            let mut kw107 = Vec::new();
                            args106.push(
                                {
                                    let fun111 = {
                                        let fun114 = e.get("s")?.attr("split")?;
                                        let mut args112 = Vec::new();
                                        let mut kw113 = Vec::new();
                                        args112.push(Val::Str("= ".into()));
                                        fun114.call(args112, kw113)?
                                    }
                                    .get(Val::Int(1i64))?
                                    .attr("split")?;
                                    let mut args109 = Vec::new();
                                    let mut kw110 = Vec::new();
                                    args109.push(Val::Str(" ".into()));
                                    fun111.call(args109, kw110)?
                                }
                                .get(Val::Int(0i64))?,
                            );
                            fun108.call(args106, kw107)?
                        })?);
                        Ok(Val::None)
                    })
                }));
                fun105.call(args103, kw104)?
            };
            e.set(
                "detail",
                binary("add", e.get("detail")?, {
                    let e = e.child();
                    let out115 = Val::list(vec![]);
                    for item116 in {
                        let fun119 = e.get("sorted")?;
                        let mut args117 = Vec::new();
                        let mut kw118 = Vec::new();
                        args117.push(e.get("RIDES_ON")?);
                        kw118.push(("key".into(), {
                            let params = vec![("q".into(), None, false)];
                            let outer = e.clone();
                            let runtime = rt.clone();
                            Val::function(move |args, kwargs| {
                                let rt = runtime.clone();
                                let e = bind(&outer, &params, args, kwargs, None, None)?;
                                let _frame = rt.frame(&outer);
                                return Ok({
                                    let fun122 = e.get("sorted")?;
                                    let mut args120 = Vec::new();
                                    let mut kw121 = Vec::new();
                                    args120.push(e.get("q")?);
                                    fun122.call(args120, kw121)?
                                });
                                Ok(Val::None)
                            })
                        }));
                        fun119.call(args117, kw118)?
                    }
                    .iter()?
                    {
                        e.set("p", item116)?;
                        out115.attr("append")?.call(
                            vec![{
                                let mut str123 = String::new();
                                str123.push_str(&format(
                                    &{
                                        let fun126 = Val::Str(" ∩ ".into()).attr("join")?;
                                        let mut args124 = Vec::new();
                                        let mut kw125 = Vec::new();
                                        args124.push({
                                            let fun129 = e.get("sorted")?;
                                            let mut args127 = Vec::new();
                                            let mut kw128 = Vec::new();
                                            args127.push(e.get("p")?);
                                            fun129.call(args127, kw128)?
                                        });
                                        fun126.call(args124, kw125)?
                                    },
                                    &String::new(),
                                )?);
                                str123.push_str(": the wrap rides it — see RIDES_ON");
                                Val::Str(str123)
                            }],
                            vec![],
                        )?;
                    }
                    out115
                })?,
            )?;
            return Ok({
                let fun132 = e.get("Check")?;
                let mut args130 = Vec::new();
                let mut kw131 = Vec::new();
                args130.push(Val::Str("bodies-clear".into()));
                args130.push(Val::Str("No two placed solids share volume".into()));
                args130.push(Val::Str("gate".into()));
                args130.push({
                    let fun135 = e.get("verdict")?;
                    let mut args133 = Vec::new();
                    let mut kw134 = Vec::new();
                    args133.push(unary("not", {
                        let e = e.child();
                        let out136 = Val::list(vec![]);
                        for item137 in e.get("detail")?.iter()? {
                            e.set("d", item137)?;
                            if {
                                let v138 = Val::Str("RIDES_ON".into());
                                let v139 = e.get("d")?;
                                Val::Bool(compare("not_in", v138.clone(), v139.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out136.attr("append")?.call(vec![e.get("d")?], vec![])?;
                            }
                        }
                        out136
                    })?);
                    fun135.call(args133, kw134)?
                });
                args130.push({
                    let mut str140 = String::new();
                    str140.push_str(&format(
                        &{
                            let fun143 = e.get("len")?;
                            let mut args141 = Vec::new();
                            let mut kw142 = Vec::new();
                            args141.push({
                                let e = e.child();
                                let out144 = Val::list(vec![]);
                                for item145 in e.get("detail")?.iter()? {
                                    e.set("d", item145)?;
                                    if {
                                        let v146 = Val::Str("RIDES_ON".into());
                                        let v147 = e.get("d")?;
                                        Val::Bool(
                                            compare("not_in", v146.clone(), v147.clone())?
                                                .truthy()?,
                                        )
                                    }
                                    .truthy()?
                                    {
                                        out144.attr("append")?.call(vec![e.get("d")?], vec![])?;
                                    }
                                }
                                out144
                            });
                            fun143.call(args141, kw142)?
                        },
                        &String::new(),
                    )?);
                    str140.push_str(" clash");
                    Val::Str(str140)
                });
                args130.push(Val::Str("0 clash".into()));
                args130.push(e.get("detail")?);
                fun132.call(args130, kw131)?
            });
            Ok(Val::None)
        })
    })?;
    // _routes_fit
    e.set("_routes_fit", {
        let params = vec![
            ("placed".into(), None, false),
            ("fitted".into(), None, false),
            ("volumes".into(), None, true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned148 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("detail", assigned148.clone())?;
            for item149 in {
                let fun184 = e.get("sorted")?;
                let mut args182 = Vec::new();
                let mut kw183 = Vec::new();
                args182.push(e.get("fitted")?);
                fun184.call(args182, kw183)?
            }
            .iter()?
            {
                e.set("name", item149)?;
                let assigned150 = e.get("fitted")?.get(e.get("name")?)?.get(Val::Int(1i64))?;
                e.set("tube", assigned150.clone())?;
                let assigned151 = {
                    let fun154 = e.get("set")?;
                    let mut args152 = Vec::new();
                    let mut kw153 = Vec::new();
                    args152.push({
                        let fun157 = e.get("MADE_UP_ON")?.attr("get")?;
                        let mut args155 = Vec::new();
                        let mut kw156 = Vec::new();
                        args155.push(e.get("name")?);
                        args155.push({
                            let mut s = Vec::new();
                            Val::tuple(s)
                        });
                        fun157.call(args155, kw156)?
                    });
                    fun154.call(args152, kw153)?
                };
                e.set("exempt", assigned151.clone())?;
                for item158 in {
                    let fun177 = e.get("sorted")?;
                    let mut args175 = Vec::new();
                    let mut kw176 = Vec::new();
                    args175.push({
                        let fun180 = e.get("placed")?.attr("items")?;
                        let mut args178 = Vec::new();
                        let mut kw179 = Vec::new();
                        fun180.call(args178, kw179)?
                    });
                    fun177.call(args175, kw176)?
                }
                .iter()?
                {
                    let unpack181 = unpack(item158, 2)?;
                    e.set("other", unpack181[0].clone())?;
                    e.set("solid", unpack181[1].clone())?;
                    if {
                        let v161 = {
                            let v162 = e.get("other")?;
                            let v163 = e.get("TAIL_LINES")?;
                            Val::Bool(compare("in", v162.clone(), v163.clone())?.truthy()?)
                        };
                        if v161.truthy()? {
                            v161
                        } else {
                            {
                                let v159 = e.get("other")?;
                                let v160 = e.get("exempt")?;
                                Val::Bool(compare("in", v159.clone(), v160.clone())?.truthy()?)
                            }
                        }
                    }
                    .truthy()?
                    {
                        continue;
                    }
                    let assigned164 = {
                        let fun167 = e.get("volumes")?;
                        let mut args165 = Vec::new();
                        let mut kw166 = Vec::new();
                        args165.push(e.get("name")?);
                        args165.push(e.get("other")?);
                        fun167.call(args165, kw166)?
                    };
                    e.set("vol", assigned164.clone())?;
                    if {
                        let v168 = e.get("vol")?;
                        let v169 = e.get("_card")?.attr("TOUCH_VOLUME")?;
                        Val::Bool(compare("gt", v168.clone(), v169.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun172 = e.get("detail")?.attr("append")?;
                            let mut args170 = Vec::new();
                            let mut kw171 = Vec::new();
                            args170.push({
                                let mut str173 = String::new();
                                str173.push_str(&format(&e.get("name")?, &String::new())?);
                                str173.push_str(" meets ");
                                str173.push_str(&format(&e.get("other")?, &String::new())?);
                                str173.push_str(" by ");
                                str173.push_str(&format(
                                    &e.get("vol")?,
                                    &val_string({
                                        let mut str174 = String::new();
                                        str174.push_str(".2f");
                                        Val::Str(str174)
                                    })?,
                                )?);
                                str173.push_str(" mm³");
                                Val::Str(str173)
                            });
                            fun172.call(args170, kw171)?
                        };
                    }
                }
            }
            return Ok({
                let fun187 = e.get("Check")?;
                let mut args185 = Vec::new();
                let mut kw186 = Vec::new();
                args185.push(Val::Str("routes-fit".into()));
                args185.push(Val::Str("No line meets a solid".into()));
                args185.push(Val::Str("gate".into()));
                args185.push({
                    let fun190 = e.get("verdict")?;
                    let mut args188 = Vec::new();
                    let mut kw189 = Vec::new();
                    args188.push(unary("not", e.get("detail")?)?);
                    fun190.call(args188, kw189)?
                });
                args185.push({
                    let mut str191 = String::new();
                    str191.push_str(&format(
                        &binary(
                            "sub",
                            {
                                let fun194 = e.get("len")?;
                                let mut args192 = Vec::new();
                                let mut kw193 = Vec::new();
                                args192.push(e.get("fitted")?);
                                fun194.call(args192, kw193)?
                            },
                            {
                                let fun197 = e.get("len")?;
                                let mut args195 = Vec::new();
                                let mut kw196 = Vec::new();
                                args195.push({
                                    let e = e.child();
                                    let out198 = Val::set_values(vec![]);
                                    for item199 in e.get("detail")?.iter()? {
                                        e.set("d", item199)?;
                                        out198.attr("add")?.call(
                                            vec![
                                                {
                                                    let fun202 = e.get("d")?.attr("split")?;
                                                    let mut args200 = Vec::new();
                                                    let mut kw201 = Vec::new();
                                                    fun202.call(args200, kw201)?
                                                }
                                                .get(Val::Int(0i64))?,
                                            ],
                                            vec![],
                                        )?;
                                    }
                                    out198
                                });
                                fun197.call(args195, kw196)?
                            },
                        )?,
                        &String::new(),
                    )?);
                    str191.push_str("/");
                    str191.push_str(&format(
                        &{
                            let fun205 = e.get("len")?;
                            let mut args203 = Vec::new();
                            let mut kw204 = Vec::new();
                            args203.push(e.get("fitted")?);
                            fun205.call(args203, kw204)?
                        },
                        &String::new(),
                    )?);
                    str191.push_str(" clear");
                    Val::Str(str191)
                });
                args185.push(Val::Str("every line clear".into()));
                args185.push(e.get("detail")?);
                fun187.call(args185, kw186)?
            });
            Ok(Val::None)
        })
    })?;
    // _lines_apart
    e.set("_lines_apart", {
        let params = vec![
            ("fitted".into(), None, false),
            ("placed".into(), None, false),
            ("volumes".into(), None, true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned206 = {
                let e = e.child();
                let out207 = Val::dict(vec![]);
                for item208 in {
                    let fun211 = e.get("fitted")?.attr("items")?;
                    let mut args209 = Vec::new();
                    let mut kw210 = Vec::new();
                    fun211.call(args209, kw210)?
                }
                .iter()?
                {
                    let unpack212 = unpack(item208, 2)?;
                    e.set("n", unpack212[0].clone())?;
                    let unpack213 = unpack(unpack212[1].clone(), 2)?;
                    e.set("_b", unpack213[0].clone())?;
                    e.set("t", unpack213[1].clone())?;
                    out207.set(e.get("n")?, e.get("t")?)?;
                }
                out207
            };
            e.set("runs", assigned206.clone())?;
            {
                let fun216 = e.get("runs")?.attr("update")?;
                let mut args214 = Vec::new();
                let mut kw215 = Vec::new();
                args214.push({
                    let e = e.child();
                    let out217 = Val::dict(vec![]);
                    for item218 in e.get("TAIL_LINES")?.iter()? {
                        e.set("n", item218)?;
                        if {
                            let v219 = e.get("n")?;
                            let v220 = e.get("placed")?;
                            Val::Bool(compare("in", v219.clone(), v220.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out217.set(e.get("n")?, e.get("placed")?.get(e.get("n")?)?)?;
                        }
                    }
                    out217
                });
                fun216.call(args214, kw215)?
            };
            {
                let fun223 = e.get("runs")?.attr("update")?;
                let mut args221 = Vec::new();
                let mut kw222 = Vec::new();
                args221.push({
                    let e = e.child();
                    let out224 = Val::dict(vec![]);
                    for item225 in {
                        let fun228 = e.get("placed")?.attr("items")?;
                        let mut args226 = Vec::new();
                        let mut kw227 = Vec::new();
                        fun228.call(args226, kw227)?
                    }
                    .iter()?
                    {
                        let unpack229 = unpack(item225, 2)?;
                        e.set("n", unpack229[0].clone())?;
                        e.set("s", unpack229[1].clone())?;
                        if {
                            let fun232 = e.get("n")?.attr("startswith")?;
                            let mut args230 = Vec::new();
                            let mut kw231 = Vec::new();
                            args230.push(Val::Str("tube-soda-core-".into()));
                            fun232.call(args230, kw231)?
                        }
                        .truthy()?
                        {
                            out224.set(e.get("n")?, e.get("s")?)?;
                        }
                    }
                    out224
                });
                fun223.call(args221, kw222)?
            };
            let assigned233 = {
                let fun236 = e.get("sorted")?;
                let mut args234 = Vec::new();
                let mut kw235 = Vec::new();
                args234.push(e.get("runs")?);
                fun236.call(args234, kw235)?
            };
            e.set("names", assigned233.clone())?;
            let assigned237 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("detail", assigned237.clone())?;
            for item238 in {
                let fun253 = e.get("enumerate")?;
                let mut args251 = Vec::new();
                let mut kw252 = Vec::new();
                args251.push(e.get("names")?);
                fun253.call(args251, kw252)?
            }
            .iter()?
            {
                let unpack254 = unpack(item238, 2)?;
                e.set("i", unpack254[0].clone())?;
                e.set("a", unpack254[1].clone())?;
                for item239 in e
                    .get("names")?
                    .get(Val::Slice {
                        start: Some(binary("add", e.get("i")?, Val::Int(1i64))?.integer()?),
                        stop: None,
                        step: 1,
                    })?
                    .iter()?
                {
                    e.set("b", item239)?;
                    let assigned240 = {
                        let fun243 = e.get("volumes")?;
                        let mut args241 = Vec::new();
                        let mut kw242 = Vec::new();
                        args241.push(e.get("a")?);
                        args241.push(e.get("b")?);
                        fun243.call(args241, kw242)?
                    };
                    e.set("vol", assigned240.clone())?;
                    if {
                        let v244 = e.get("vol")?;
                        let v245 = e.get("_card")?.attr("TOUCH_VOLUME")?;
                        Val::Bool(compare("gt", v244.clone(), v245.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun248 = e.get("detail")?.attr("append")?;
                            let mut args246 = Vec::new();
                            let mut kw247 = Vec::new();
                            args246.push({
                                let mut str249 = String::new();
                                str249.push_str(&format(&e.get("a")?, &String::new())?);
                                str249.push_str(" and ");
                                str249.push_str(&format(&e.get("b")?, &String::new())?);
                                str249.push_str(" share ");
                                str249.push_str(&format(
                                    &e.get("vol")?,
                                    &val_string({
                                        let mut str250 = String::new();
                                        str250.push_str(".2f");
                                        Val::Str(str250)
                                    })?,
                                )?);
                                str249.push_str(" mm³ — two runs in one corridor");
                                Val::Str(str249)
                            });
                            fun248.call(args246, kw247)?
                        };
                    }
                }
            }
            return Ok({
                let fun257 = e.get("Check")?;
                let mut args255 = Vec::new();
                let mut kw256 = Vec::new();
                args255.push(Val::Str("lines-apart".into()));
                args255.push(Val::Str("No two runs want the same corridor".into()));
                args255.push(Val::Str("gate".into()));
                args255.push({
                    let fun260 = e.get("verdict")?;
                    let mut args258 = Vec::new();
                    let mut kw259 = Vec::new();
                    args258.push(unary("not", e.get("detail")?)?);
                    fun260.call(args258, kw259)?
                });
                args255.push({
                    let mut str261 = String::new();
                    str261.push_str(&format(
                        &{
                            let fun264 = e.get("len")?;
                            let mut args262 = Vec::new();
                            let mut kw263 = Vec::new();
                            args262.push(e.get("detail")?);
                            fun264.call(args262, kw263)?
                        },
                        &String::new(),
                    )?);
                    str261.push_str(" crossing");
                    Val::Str(str261)
                });
                args255.push(Val::Str("0 crossing".into()));
                args255.push(e.get("detail")?);
                fun257.call(args255, kw256)?
            });
            Ok(Val::None)
        })
    })?;
    // _floats_couple
    e.set("_floats_couple", {
        let params = vec![("placed".into(), None, false), ("seats".into(), None, true)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned265 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("detail", assigned265.clone())?;
            let assigned266 = Val::Int(0i64);
            e.set("good", assigned266.clone())?;
            for item267 in {
                let fun298 = e.get("sorted")?;
                let mut args296 = Vec::new();
                let mut kw297 = Vec::new();
                args296.push({
                    let fun301 = e.get("seats")?.attr("items")?;
                    let mut args299 = Vec::new();
                    let mut kw300 = Vec::new();
                    fun301.call(args299, kw300)?
                });
                fun298.call(args296, kw297)?
            }
            .iter()?
            {
                let unpack302 = unpack(item267, 2)?;
                e.set("name", unpack302[0].clone())?;
                let unpack303 = unpack(unpack302[1].clone(), 4)?;
                e.set("park", unpack303[0].clone())?;
                e.set("wall", unpack303[1].clone())?;
                e.set("_centre", unpack303[2].clone())?;
                e.set("standoff", unpack303[3].clone())?;
                let assigned268 = binary(
                    "sub",
                    e.get("standoff")?,
                    binary("mul", Val::Int(2i64), e.get("_I")?.attr("FLOAT_SLOP")?)?,
                )?;
                e.set("minimum_gap", assigned268.clone())?;
                let assigned269 = if {
                    let v270 = e.get("name")?;
                    let v271 = Val::Str("float-carb".into());
                    Val::Bool(compare("eq", v270.clone(), v271.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun274 = e.get("_I")?.attr("carbonator_reed_radius")?;
                        let mut args272 = Vec::new();
                        let mut kw273 = Vec::new();
                        fun274.call(args272, kw273)?
                    }
                } else {
                    e.get("_I")?.attr("REED_COLUMN_X")?
                };
                e.set("reed_axis", assigned269.clone())?;
                let assigned275 = {
                    let fun278 = e.get("_I")?.attr("_float")?.attr("reed_edge_distance")?;
                    let mut args276 = Vec::new();
                    let mut kw277 = Vec::new();
                    args276.push(e.get("park")?);
                    args276.push(e.get("reed_axis")?);
                    fun278.call(args276, kw277)?
                };
                e.set("edge_path", assigned275.clone())?;
                let assigned279 = {
                    let fun282 = e
                        .get("_I")?
                        .attr("_float")?
                        .attr("reed_float_edge_distance")?;
                    let mut args280 = Vec::new();
                    let mut kw281 = Vec::new();
                    args280.push(e.get("park")?);
                    args280.push(e.get("reed_axis")?);
                    fun282.call(args280, kw281)?
                };
                e.set("float_path", assigned279.clone())?;
                e.set(
                    "good",
                    binary("add", e.get("good")?, {
                        let v285 = {
                            let v286 = e.get("minimum_gap")?;
                            let v287 = Val::Float(1.0f64);
                            Val::Bool(compare("ge", v286.clone(), v287.clone())?.truthy()?)
                        };
                        if v285.truthy()? {
                            {
                                let v283 = e.get("float_path")?;
                                let v284 = e.get("_I")?.attr("FLOAT_EDGE_DESIGN_MAXIMUM")?;
                                Val::Bool(compare("le", v283.clone(), v284.clone())?.truthy()?)
                            }
                        } else {
                            v285
                        }
                    })?,
                )?;
                {
                    let fun290 = e.get("detail")?.attr("append")?;
                    let mut args288 = Vec::new();
                    let mut kw289 = Vec::new();
                    args288.push({
                        let mut str291 = String::new();
                        str291.push_str(&format(&e.get("name")?, &String::new())?);
                        str291.push_str(": body/wet-wall gap ");
                        str291.push_str(&format(
                            &e.get("minimum_gap")?,
                            &val_string({
                                let mut str292 = String::new();
                                str292.push_str(".3f");
                                Val::Str(str292)
                            })?,
                        )?);
                        str291.push_str("..");
                        str291.push_str(&format(
                            &e.get("standoff")?,
                            &val_string({
                                let mut str293 = String::new();
                                str293.push_str(".3f");
                                Val::Str(str293)
                            })?,
                        )?);
                        str291.push_str(" mm; float-edge to reed-centre at most ");
                        str291.push_str(&format(
                            &e.get("float_path")?,
                            &val_string({
                                let mut str294 = String::new();
                                str294.push_str(".3f");
                                Val::Str(str294)
                            })?,
                        )?);
                        str291.push_str(" mm; reed-centre to RC62 edge at most ");
                        str291.push_str(&format(
                            &e.get("edge_path")?,
                            &val_string({
                                let mut str295 = String::new();
                                str295.push_str(".3f");
                                Val::Str(str295)
                            })?,
                        )?);
                        str291.push_str(" mm; installed switching height unmeasured");
                        Val::Str(str291)
                    });
                    fun290.call(args288, kw289)?
                };
            }
            return Ok({
                let fun306 = e.get("Check")?;
                let mut args304 = Vec::new();
                let mut kw305 = Vec::new();
                args304.push(Val::Str("floats-couple".into()));
                args304.push(Val::Str(
                    "Aero floats clear their walls within the float-edge reed distance limit"
                        .into(),
                ));
                args304.push(Val::Str("gate".into()));
                args304.push({
                    let fun309 = e.get("verdict")?;
                    let mut args307 = Vec::new();
                    let mut kw308 = Vec::new();
                    args307.push({
                        let v313 = e.get("good")?;
                        let v314 = {
                            let fun312 = e.get("len")?;
                            let mut args310 = Vec::new();
                            let mut kw311 = Vec::new();
                            args310.push(e.get("seats")?);
                            fun312.call(args310, kw311)?
                        };
                        Val::Bool(compare("eq", v313.clone(), v314.clone())?.truthy()?)
                    });
                    fun309.call(args307, kw308)?
                });
                args304.push({
                    let mut str315 = String::new();
                    str315.push_str(&format(&e.get("good")?, &String::new())?);
                    str315.push_str("/");
                    str315.push_str(&format(
                        &{
                            let fun318 = e.get("len")?;
                            let mut args316 = Vec::new();
                            let mut kw317 = Vec::new();
                            args316.push(e.get("seats")?);
                            fun318.call(args316, kw317)?
                        },
                        &String::new(),
                    )?);
                    str315.push_str(" floats");
                    Val::Str(str315)
                });
                args304.push({
                    let mut str319 = String::new();
                    str319.push_str(">=1 mm body clearance, <=");
                    str319.push_str(&format(
                        &e.get("_I")?.attr("FLOAT_EDGE_DESIGN_MAXIMUM")?,
                        &val_string({
                            let mut str320 = String::new();
                            str320.push_str("g");
                            Val::Str(str320)
                        })?,
                    )?);
                    str319.push_str(" mm float-edge to reed-centre; geometry only");
                    Val::Str(str319)
                });
                args304.push(e.get("detail")?);
                fun306.call(args304, kw305)?
            });
            Ok(Val::None)
        })
    })?;
    // _arcs_hold
    e.set("_arcs_hold", {
        let params = vec![
            ("fitted".into(), None, false),
            ("points".into(), None, false),
            ("corner_data".into(), None, true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned321 = e.get("_routes")?.attr("route_bend_radius")?;
            e.set("stock", assigned321.clone())?;
            let assigned322 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("detail", assigned322.clone())?;
            let assigned323 = Val::Int(0i64);
            e.set("total", assigned323.clone())?;
            for item324 in {
                let fun347 = e.get("sorted")?;
                let mut args345 = Vec::new();
                let mut kw346 = Vec::new();
                args345.push(e.get("fitted")?);
                fun347.call(args345, kw346)?
            }
            .iter()?
            {
                e.set("name", item324)?;
                let assigned325 = e.get("fitted")?.get(e.get("name")?)?;
                let unpack326 = unpack(assigned325.clone(), 2)?;
                e.set("bend", unpack326[0].clone())?;
                e.set("_tube", unpack326[1].clone())?;
                let assigned327 = e.get("corner_data")?.get(e.get("name")?)?;
                let unpack328 = unpack(assigned327.clone(), 2)?;
                e.set("v", unpack328[0].clone())?;
                e.set("radii", unpack328[1].clone())?;
                for item329 in {
                    let fun343 = e.get("enumerate")?;
                    let mut args341 = Vec::new();
                    let mut kw342 = Vec::new();
                    args341.push(e.get("radii")?.get(Val::Slice {
                        start: Some(Val::Int(1i64).integer()?),
                        stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                        step: 1,
                    })?);
                    kw342.push(("start".into(), Val::Int(1i64)));
                    fun343.call(args341, kw342)?
                }
                .iter()?
                {
                    let unpack344 = unpack(item329, 2)?;
                    e.set("i", unpack344[0].clone())?;
                    e.set("r", unpack344[1].clone())?;
                    e.set("total", binary("add", e.get("total")?, Val::Int(1i64))?)?;
                    if {
                        let v330 = e.get("r")?;
                        let v331 = binary("sub", e.get("stock")?, Val::Float(1e-09f64))?;
                        Val::Bool(compare("lt", v330.clone(), v331.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun334 = e.get("detail")?.attr("append")?;
                            let mut args332 = Vec::new();
                            let mut kw333 = Vec::new();
                            args332.push({
                                let mut str335 = String::new();
                                str335.push_str(&format(&e.get("name")?, &String::new())?);
                                str335.push_str(" corner ");
                                str335.push_str(&format(&e.get("i")?, &String::new())?);
                                str335.push_str(" at (");
                                str335.push_str(&format(
                                    &e.get("v")?.get(e.get("i")?)?.attr("x")?,
                                    &val_string({
                                        let mut str336 = String::new();
                                        str336.push_str(".1f");
                                        Val::Str(str336)
                                    })?,
                                )?);
                                str335.push_str(", ");
                                str335.push_str(&format(
                                    &e.get("v")?.get(e.get("i")?)?.attr("y")?,
                                    &val_string({
                                        let mut str337 = String::new();
                                        str337.push_str(".1f");
                                        Val::Str(str337)
                                    })?,
                                )?);
                                str335.push_str(", ");
                                str335.push_str(&format(
                                    &e.get("v")?.get(e.get("i")?)?.attr("z")?,
                                    &val_string({
                                        let mut str338 = String::new();
                                        str338.push_str(".1f");
                                        Val::Str(str338)
                                    })?,
                                )?);
                                str335.push_str(") turns at ");
                                str335.push_str(&format(
                                    &e.get("r")?,
                                    &val_string({
                                        let mut str339 = String::new();
                                        str339.push_str(".2f");
                                        Val::Str(str339)
                                    })?,
                                )?);
                                str335.push_str(" mm against the ");
                                str335.push_str(&format(
                                    &e.get("stock")?,
                                    &val_string({
                                        let mut str340 = String::new();
                                        str340.push_str(".2f");
                                        Val::Str(str340)
                                    })?,
                                )?);
                                str335.push_str(" mm stock arc");
                                Val::Str(str335)
                            });
                            fun334.call(args332, kw333)?
                        };
                    }
                }
            }
            return Ok({
                let fun350 = e.get("Check")?;
                let mut args348 = Vec::new();
                let mut kw349 = Vec::new();
                args348.push(Val::Str("arcs-hold".into()));
                args348.push(Val::Str("Every corner turns at the stock arc".into()));
                args348.push(Val::Str("gate".into()));
                args348.push({
                    let fun353 = e.get("verdict")?;
                    let mut args351 = Vec::new();
                    let mut kw352 = Vec::new();
                    args351.push(unary("not", e.get("detail")?)?);
                    fun353.call(args351, kw352)?
                });
                args348.push({
                    let mut str354 = String::new();
                    str354.push_str(&format(
                        &binary("sub", e.get("total")?, {
                            let fun357 = e.get("len")?;
                            let mut args355 = Vec::new();
                            let mut kw356 = Vec::new();
                            args355.push(e.get("detail")?);
                            fun357.call(args355, kw356)?
                        })?,
                        &String::new(),
                    )?);
                    str354.push_str("/");
                    str354.push_str(&format(&e.get("total")?, &String::new())?);
                    str354.push_str(" corners at stock");
                    Val::Str(str354)
                });
                args348.push({
                    let mut str358 = String::new();
                    str358.push_str(&format(
                        &e.get("stock")?,
                        &val_string({
                            let mut str359 = String::new();
                            str359.push_str(".2f");
                            Val::Str(str359)
                        })?,
                    )?);
                    str358.push_str(" mm");
                    Val::Str(str358)
                });
                args348.push(e.get("detail")?);
                fun350.call(args348, kw349)?
            });
            Ok(Val::None)
        })
    })?;
    // _bend_rows
    e.set("_bend_rows", {
        let params = vec![
            ("fitted".into(), None, false),
            ("points".into(), None, false),
            ("route_data".into(), None, true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned360 = e.get("_routes")?.attr("route_bend_radius")?;
            e.set("stock", assigned360.clone())?;
            let assigned361 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("rows", assigned361.clone())?;
            for item362 in {
                let fun444 = e.get("sorted")?;
                let mut args442 = Vec::new();
                let mut kw443 = Vec::new();
                args442.push(e.get("fitted")?);
                fun444.call(args442, kw443)?
            }
            .iter()?
            {
                e.set("name", item362)?;
                let assigned363 = e.get("fitted")?.get(e.get("name")?)?;
                let unpack364 = unpack(assigned363.clone(), 2)?;
                e.set("bend", unpack364[0].clone())?;
                e.set("_tube", unpack364[1].clone())?;
                let assigned365 = e.get("points")?.get(e.get("name")?)?;
                e.set("pts", assigned365.clone())?;
                let assigned366 = e
                    .get("route_data")?
                    .get(e.get("name")?)?
                    .get(Val::Str("corners".into()))?;
                let unpack367 = unpack(assigned366.clone(), 2)?;
                e.set("v", unpack367[0].clone())?;
                e.set("radii", unpack367[1].clone())?;
                let assigned368 = {
                    let e = e.child();
                    let out369 = Val::list(vec![]);
                    for item370 in e
                        .get("radii")?
                        .get(Val::Slice {
                            start: Some(Val::Int(1i64).integer()?),
                            stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                            step: 1,
                        })?
                        .iter()?
                    {
                        e.set("r", item370)?;
                        if {
                            let v371 = e.get("r")?;
                            let v372 = Val::Float(0.0f64);
                            Val::Bool(compare("gt", v371.clone(), v372.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out369.attr("append")?.call(vec![e.get("r")?], vec![])?;
                        }
                    }
                    out369
                };
                e.set("corners", assigned368.clone())?;
                let assigned373 = if e.get("corners")?.truthy()? {
                    {
                        let fun376 = e.get("min")?;
                        let mut args374 = Vec::new();
                        let mut kw375 = Vec::new();
                        args374.push(e.get("corners")?);
                        fun376.call(args374, kw375)?
                    }
                } else {
                    e.get("bend")?
                };
                e.set("tightest", assigned373.clone())?;
                let assigned377 = e
                    .get("route_data")?
                    .get(e.get("name")?)?
                    .get(Val::Str("length".into()))?;
                e.set("length", assigned377.clone())?;
                let assigned378 = e
                    .get("route_data")?
                    .get(e.get("name")?)?
                    .get(Val::Str("reach".into()))?;
                e.set("reach", assigned378.clone())?;
                let assigned379 = binary("truediv", e.get("tightest")?, e.get("stock")?)?;
                e.set("ratio", assigned379.clone())?;
                {
                    let fun382 = e.get("rows")?.attr("append")?;
                    let mut args380 = Vec::new();
                    let mut kw381 = Vec::new();
                    args380.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("id".into()), e.get("name")?)?;
                        d.set(Val::Str("kind".into()), Val::Str("fluid".into()))?;
                        d.set(Val::Str("frm".into()), {
                            let fun385 = e.get("_endpoint_label")?;
                            let mut args383 = Vec::new();
                            let mut kw384 = Vec::new();
                            args383.push(e.get("name")?);
                            args383.push(Val::Str("start".into()));
                            fun385.call(args383, kw384)?
                        })?;
                        d.set(Val::Str("to".into()), {
                            let fun388 = e.get("_endpoint_label")?;
                            let mut args386 = Vec::new();
                            let mut kw387 = Vec::new();
                            args386.push(e.get("name")?);
                            args386.push(Val::Str("end".into()));
                            fun388.call(args386, kw387)?
                        })?;
                        d.set(
                            Val::Str("stock".into()),
                            e.get("_routes")?.attr("route_stock")?.attr("name")?,
                        )?;
                        d.set(
                            Val::Str("od".into()),
                            e.get("_routes")?.attr("lldpe_tube_od")?,
                        )?;
                        d.set(Val::Str("length".into()), {
                            let fun391 = e.get("round")?;
                            let mut args389 = Vec::new();
                            let mut kw390 = Vec::new();
                            args389.push(e.get("length")?);
                            args389.push(Val::Int(2i64));
                            fun391.call(args389, kw390)?
                        })?;
                        d.set(Val::Str("bend".into()), {
                            let fun394 = e.get("round")?;
                            let mut args392 = Vec::new();
                            let mut kw393 = Vec::new();
                            args392.push(e.get("bend")?);
                            args392.push(Val::Int(3i64));
                            fun394.call(args392, kw393)?
                        })?;
                        d.set(Val::Str("radius".into()), {
                            let fun397 = e.get("round")?;
                            let mut args395 = Vec::new();
                            let mut kw396 = Vec::new();
                            args395.push(e.get("tightest")?);
                            args395.push(Val::Int(3i64));
                            fun397.call(args395, kw396)?
                        })?;
                        d.set(Val::Str("minBend".into()), {
                            let fun400 = e.get("round")?;
                            let mut args398 = Vec::new();
                            let mut kw399 = Vec::new();
                            args398.push(e.get("stock")?);
                            args398.push(Val::Int(3i64));
                            fun400.call(args398, kw399)?
                        })?;
                        d.set(Val::Str("ratio".into()), {
                            let fun403 = e.get("round")?;
                            let mut args401 = Vec::new();
                            let mut kw402 = Vec::new();
                            args401.push(e.get("ratio")?);
                            args401.push(Val::Int(3i64));
                            fun403.call(args401, kw402)?
                        })?;
                        d.set(
                            Val::Str("grade".into()),
                            if e.get("corners")?.truthy()? {
                                {
                                    let fun406 = e.get("grade_of")?;
                                    let mut args404 = Vec::new();
                                    let mut kw405 = Vec::new();
                                    args404.push(e.get("ratio")?);
                                    fun406.call(args404, kw405)?
                                }
                            } else {
                                Val::None
                            },
                        )?;
                        d.set(
                            Val::Str("reach".into()),
                            if {
                                let v407 = e.get("reach")?;
                                let v408 = Val::Float(1e-09f64);
                                Val::Bool(compare("gt", v407.clone(), v408.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                {
                                    let fun411 = e.get("round")?;
                                    let mut args409 = Vec::new();
                                    let mut kw410 = Vec::new();
                                    args409.push(e.get("reach")?);
                                    args409.push(Val::Int(2i64));
                                    fun411.call(args409, kw410)?
                                }
                            } else {
                                Val::None
                            },
                        )?;
                        d.set(
                            Val::Str("reachGrade".into()),
                            if {
                                let v412 = e.get("reach")?;
                                let v413 = Val::Float(1e-09f64);
                                Val::Bool(compare("le", v412.clone(), v413.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                Val::None
                            } else {
                                {
                                    let fun416 = e.get("grade_of")?;
                                    let mut args414 = Vec::new();
                                    let mut kw415 = Vec::new();
                                    args414.push({
                                        let fun419 = e.get("min")?;
                                        let mut args417 = Vec::new();
                                        let mut kw418 = Vec::new();
                                        args417.push(Val::Float(1.5f64));
                                        args417.push(binary(
                                            "truediv",
                                            e.get("reach")?,
                                            e.get("length")?,
                                        )?);
                                        fun419.call(args417, kw418)?
                                    });
                                    fun416.call(args414, kw415)?
                                }
                            },
                        )?;
                        d.set(Val::Str("binding".into()), Val::None)?;
                        d.set(Val::Str("corners".into()), {
                            let e = e.child();
                            let out420 = Val::list(vec![]);
                            for item421 in {
                                let fun424 = e.get("enumerate")?;
                                let mut args422 = Vec::new();
                                let mut kw423 = Vec::new();
                                args422.push(e.get("radii")?.get(Val::Slice {
                                    start: Some(Val::Int(1i64).integer()?),
                                    stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                                    step: 1,
                                })?);
                                kw423.push(("start".into(), Val::Int(1i64)));
                                fun424.call(args422, kw423)?
                            }
                            .iter()?
                            {
                                let unpack425 = unpack(item421, 2)?;
                                e.set("i", unpack425[0].clone())?;
                                e.set("r", unpack425[1].clone())?;
                                if {
                                    let v426 = e.get("r")?;
                                    let v427 = Val::Float(0.0f64);
                                    Val::Bool(compare("gt", v426.clone(), v427.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    out420.attr("append")?.call(
                                        vec![{
                                            let d = Val::dict(vec![]);
                                            d.set(Val::Str("at".into()), e.get("i")?)?;
                                            d.set(Val::Str("radius".into()), {
                                                let fun430 = e.get("round")?;
                                                let mut args428 = Vec::new();
                                                let mut kw429 = Vec::new();
                                                args428.push(e.get("r")?);
                                                args428.push(Val::Int(3i64));
                                                fun430.call(args428, kw429)?
                                            })?;
                                            d.set(Val::Str("ratio".into()), {
                                                let fun433 = e.get("round")?;
                                                let mut args431 = Vec::new();
                                                let mut kw432 = Vec::new();
                                                args431.push(binary(
                                                    "truediv",
                                                    e.get("r")?,
                                                    e.get("stock")?,
                                                )?);
                                                args431.push(Val::Int(3i64));
                                                fun433.call(args431, kw432)?
                                            })?;
                                            d.set(Val::Str("grade".into()), {
                                                let fun436 = e.get("grade_of")?;
                                                let mut args434 = Vec::new();
                                                let mut kw435 = Vec::new();
                                                args434.push(binary(
                                                    "truediv",
                                                    e.get("r")?,
                                                    e.get("stock")?,
                                                )?);
                                                fun436.call(args434, kw435)?
                                            })?;
                                            d
                                        }],
                                        vec![],
                                    )?;
                                }
                            }
                            out420
                        })?;
                        d.set(Val::Str("need".into()), {
                            let d = Val::dict(vec![]);
                            d.set(
                                Val::Str("detour".into()),
                                if {
                                    let v437 = e.get("reach")?;
                                    let v438 = Val::Float(1e-09f64);
                                    Val::Bool(compare("gt", v437.clone(), v438.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    {
                                        let fun441 = e.get("round")?;
                                        let mut args439 = Vec::new();
                                        let mut kw440 = Vec::new();
                                        args439.push(binary(
                                            "truediv",
                                            e.get("length")?,
                                            e.get("reach")?,
                                        )?);
                                        args439.push(Val::Int(3i64));
                                        fun441.call(args439, kw440)?
                                    }
                                } else {
                                    Val::None
                                },
                            )?;
                            d
                        })?;
                        d
                    });
                    fun382.call(args380, kw381)?
                };
            }
            return Ok(e.get("rows")?);
            Ok(Val::None)
        })
    })?;
    // _endpoint_label
    e.set("_endpoint_label", {
        let params = vec![("line".into(), None, false), ("which".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            for item445 in {
                let fun454 = e.get("_V")?.attr("PORT_LINES")?.attr("items")?;
                let mut args452 = Vec::new();
                let mut kw453 = Vec::new();
                fun454.call(args452, kw453)?
            }
            .iter()?
            {
                let unpack455 = unpack(item445, 2)?;
                e.set("port", unpack455[0].clone())?;
                let unpack456 = unpack(unpack455[1].clone(), 2)?;
                e.set("name", unpack456[0].clone())?;
                e.set("side", unpack456[1].clone())?;
                if {
                    let v448 = {
                        let v449 = e.get("name")?;
                        let v450 = e.get("line")?;
                        Val::Bool(compare("eq", v449.clone(), v450.clone())?.truthy()?)
                    };
                    if v448.truthy()? {
                        {
                            let v446 = e.get("side")?;
                            let v447 = e.get("which")?;
                            Val::Bool(compare("eq", v446.clone(), v447.clone())?.truthy()?)
                        }
                    } else {
                        v448
                    }
                }
                .truthy()?
                {
                    return Ok({
                        let mut str451 = String::new();
                        str451.push_str("carbonator.");
                        str451.push_str(&format(&e.get("port")?, &String::new())?);
                        Val::Str(str451)
                    });
                }
            }
            return Ok({
                let mut str457 = String::new();
                str457.push_str(&format(&e.get("line")?, &String::new())?);
                str457.push_str(".");
                str457.push_str(&format(&e.get("which")?, &String::new())?);
                Val::Str(str457)
            });
            Ok(Val::None)
        })
    })?;
    // _goal
    e.set("_goal", {
        let params = vec![
            ("cid".into(), None, false),
            ("label".into(), None, false),
            ("done".into(), None, false),
            ("total".into(), None, false),
            ("target".into(), None, false),
            (
                "detail".into(),
                Some({
                    let mut s = Vec::new();
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
            return Ok({
                let fun460 = e.get("Check")?;
                let mut args458 = Vec::new();
                let mut kw459 = Vec::new();
                args458.push(e.get("cid")?);
                args458.push(e.get("label")?);
                args458.push(Val::Str("goal".into()));
                args458.push({
                    let fun463 = e.get("verdict")?;
                    let mut args461 = Vec::new();
                    let mut kw462 = Vec::new();
                    args461.push({
                        let v464 = e.get("done")?;
                        let v465 = e.get("total")?;
                        Val::Bool(compare("eq", v464.clone(), v465.clone())?.truthy()?)
                    });
                    fun463.call(args461, kw462)?
                });
                args458.push({
                    let mut str466 = String::new();
                    str466.push_str(&format(&e.get("done")?, &String::new())?);
                    str466.push_str("/");
                    str466.push_str(&format(&e.get("total")?, &String::new())?);
                    Val::Str(str466)
                });
                args458.push(e.get("target")?);
                args458.push({
                    let fun469 = e.get("list")?;
                    let mut args467 = Vec::new();
                    let mut kw468 = Vec::new();
                    args467.push(e.get("detail")?);
                    fun469.call(args467, kw468)?
                });
                fun460.call(args458, kw459)?
            });
            Ok(Val::None)
        })
    })?;
    // build_card
    e.set("build_card",{let params=vec![("a".into(),None,false),("measurements".into(),None,true)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned470={let mut s=Vec::new();s.push(e.get("a")?.attr("placed")?);s.push(e.get("a")?.attr("fitted")?);Val::tuple(s)};let unpack471=unpack(assigned470.clone(),2)?;e.set("placed",unpack471[0].clone())?;e.set("fitted",unpack471[1].clone())?;
let assigned472=e.get("measurements")?.get(Val::Str("mouths".into()))?;e.set("mouths",assigned472.clone())?;
// volumes
e.set("volumes",{let params=vec![("key".into(),None,false),("symmetric".into(),Some(Val::Bool(false)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned473={let e=e.child();let out474=Val::dict(vec![]);for item475 in e.get("measurements")?.get(e.get("key")?)?.iter()? {e.set("row",item475)?;out474.set({let mut s=Vec::new();s.push(e.get("row")?.get(Val::Str("a".into()))?);s.push(e.get("row")?.get(Val::Str("b".into()))?);Val::tuple(s)},e.get("row")?.get(Val::Str("volume".into()))?)?;}out474};e.set("table",assigned473.clone())?;
return Ok({let params=vec![("a".into(),None,false),("b".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let fun478=e.get("table")?.attr("get")?;let mut args476=Vec::new();let mut kw477=Vec::new();args476.push(if e.get("symmetric")?.truthy()? {{let fun481=e.get("tuple")?;let mut args479=Vec::new();let mut kw480=Vec::new();args479.push({let fun484=e.get("sorted")?;let mut args482=Vec::new();let mut kw483=Vec::new();args482.push({let mut s=Vec::new();s.push(e.get("a")?);s.push(e.get("b")?);Val::tuple(s)});fun484.call(args482,kw483)?});fun481.call(args479,kw480)?}} else {{let mut s=Vec::new();s.push(e.get("a")?);s.push(e.get("b")?);Val::tuple(s)}});args476.push(Val::Float(0.0f64));fun478.call(args476,kw477)?});
Ok(Val::None)})});
Ok(Val::None)})})?;
let mod485=rt.import_module("collections")?;e.set("namedtuple",rt.member("collections","namedtuple")?)?;
let assigned486={let fun489=e.get("namedtuple")?;let mut args487=Vec::new();let mut kw488=Vec::new();args487.push(Val::Str("Point".into()));args487.push(Val::Str("x y z".into()));fun489.call(args487,kw488)?};e.set("Point",assigned486.clone())?;
let assigned490={let e=e.child();let out491=Val::dict(vec![]);for item492 in e.get("measurements")?.get(Val::Str("routes".into()))?.iter()? {e.set("row",item492)?;out491.set(e.get("row")?.get(Val::Str("name".into()))?,{let d=Val::dict(vec![]);dict_extend(&d,e.get("row")?)?;d.set(Val::Str("corners".into()),{let mut s=Vec::new();s.push({let e=e.child();let out493=Val::list(vec![]);for item494 in e.get("row")?.get(Val::Str("corner_points".into()))?.iter()? {e.set("p",item494)?;out493.attr("append")?.call(vec![{let fun497=e.get("Point")?;let mut args495=Vec::new();let mut kw496=Vec::new();args495.extend(e.get("p")?.iter()?);fun497.call(args495,kw496)?}],vec![])?;}out493});s.push(e.get("row")?.get(Val::Str("radii".into()))?);Val::tuple(s)})?;d})?;}out491};e.set("route_data",assigned490.clone())?;
let assigned498={let d=Val::dict(vec![]);d};e.set("seats",assigned498.clone())?;
for item499 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("float-carb".into()));s.push(e.get("_V")?.attr("ROD_RADIUS")?);s.push(binary("truediv",e.get("_V")?.attr("TUBE_ID")?,Val::Float(2.0f64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("float-a".into()));s.push(e.get("_I")?.attr("RES_ROD_X")?);s.push(e.get("measurements")?.get(Val::Str("reservoir_walls".into()))?.get(Val::Str("a".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("float-b".into()));s.push(e.get("_I")?.attr("RES_ROD_X")?);s.push(e.get("measurements")?.get(Val::Str("reservoir_walls".into()))?.get(Val::Str("b".into()))?);Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack504=unpack(item499,3)?;e.set("name",unpack504[0].clone())?;e.set("park",unpack504[1].clone())?;e.set("wall",unpack504[2].clone())?;let assigned500={let mut s=Vec::new();s.push(e.get("park")?);s.push(e.get("wall")?);s.extend({let fun503=e.get("_I")?.attr("float_ride")?;let mut args501=Vec::new();let mut kw502=Vec::new();args501.push(e.get("park")?);args501.push(e.get("wall")?);fun503.call(args501,kw502)?}.iter()?);Val::tuple(s)};e.get("seats")?.set(e.get("name")?,assigned500.clone())?;
}
let assigned505={let e=e.child();let out506=Val::list(vec![]);for item507 in {let fun510=e.get("sorted")?;let mut args508=Vec::new();let mut kw509=Vec::new();args508.push(e.get("placed")?);fun510.call(args508,kw509)?}.iter()? {e.set("n",item507)?;out506.attr("append")?.call(vec![{let mut s=Vec::new();s.push(e.get("n")?);s.push(if {let v514={let fun513=e.get("held_for")?;let mut args511=Vec::new();let mut kw512=Vec::new();args511.push(e.get("n")?);fun513.call(args511,kw512)?};let v515=e.get("NOT_A_FEATURE")?;Val::Bool(compare("in",v514.clone(),v515.clone())?.truthy()?)}.truthy()? {Val::None} else {{let fun518=e.get("held_for")?;let mut args516=Vec::new();let mut kw517=Vec::new();args516.push(e.get("n")?);fun518.call(args516,kw517)?}});s.push({let fun521=e.get("held_for")?;let mut args519=Vec::new();let mut kw520=Vec::new();args519.push(e.get("n")?);fun521.call(args519,kw520)?});Val::tuple(s)}],vec![])?;}out506};e.set("mounts",assigned505.clone())?;
let assigned522={let mut s=Vec::new();s.push({let fun525=e.get("_bodies_clear")?;let mut args523=Vec::new();let mut kw524=Vec::new();args523.push(e.get("placed")?);kw524.push(("volumes".into(),{let fun528=e.get("volumes")?;let mut args526=Vec::new();let mut kw527=Vec::new();args526.push(Val::Str("body_overlaps".into()));args526.push(Val::Bool(true));fun528.call(args526,kw527)?}));fun525.call(args523,kw524)?});s.push({let fun531=e.get("_routes_fit")?;let mut args529=Vec::new();let mut kw530=Vec::new();args529.push(e.get("placed")?);args529.push(e.get("fitted")?);kw530.push(("volumes".into(),{let fun534=e.get("volumes")?;let mut args532=Vec::new();let mut kw533=Vec::new();args532.push(Val::Str("route_overlaps".into()));fun534.call(args532,kw533)?}));fun531.call(args529,kw530)?});s.push({let fun537=e.get("_lines_apart")?;let mut args535=Vec::new();let mut kw536=Vec::new();args535.push(e.get("fitted")?);args535.push(e.get("placed")?);kw536.push(("volumes".into(),{let fun540=e.get("volumes")?;let mut args538=Vec::new();let mut kw539=Vec::new();args538.push(Val::Str("run_overlaps".into()));args538.push(Val::Bool(true));fun540.call(args538,kw539)?}));fun537.call(args535,kw536)?});s.push({let fun543=e.get("_bom_check")?.attr("check")?;let mut args541=Vec::new();let mut kw542=Vec::new();args541.push(e.get("placed")?);fun543.call(args541,kw542)?});s.push({let fun546=e.get("_arcs_hold")?;let mut args544=Vec::new();let mut kw545=Vec::new();args544.push(e.get("fitted")?);args544.push(e.get("a")?.attr("points")?);kw545.push(("corner_data".into(),{let e=e.child();let out547=Val::dict(vec![]);for item548 in {let fun551=e.get("route_data")?.attr("items")?;let mut args549=Vec::new();let mut kw550=Vec::new();fun551.call(args549,kw550)?}.iter()? {let unpack552=unpack(item548,2)?;e.set("name",unpack552[0].clone())?;e.set("row",unpack552[1].clone())?;out547.set(e.get("name")?,e.get("row")?.get(Val::Str("corners".into()))?)?;}out547}));fun546.call(args544,kw545)?});s.push({let fun555=e.get("_floats_couple")?;let mut args553=Vec::new();let mut kw554=Vec::new();args553.push(e.get("placed")?);kw554.push(("seats".into(),e.get("seats")?));fun555.call(args553,kw554)?});s.push({let fun558=e.get("Check")?;let mut args556=Vec::new();let mut kw557=Vec::new();args556.push(Val::Str("inlet-jet-qualified".into()));args556.push(Val::Str("The inlet jet's actual joint and fit are qualified".into()));args556.push(Val::Str("goal".into()));args556.push(Val::Str("warn".into()));args556.push(Val::Str("nominal layout only".into()));args556.push(Val::Str("measured fit and qualified weld".into()));args556.push({let mut s=Vec::new();s.push(Val::Str("The cap is drawn at nominal 9.5 mm diameter, 2 mm thickness and a 1/16-inch passage.".into()));s.push(Val::Str("The elbow bore and installed tip projection are unmeasured layout assumptions; the model does not establish the weld land, penetration or pressure integrity.".into()));s.push(Val::Str("Qualify the coupon, passage and made-up port using assembly/water-inlet-jet.md.".into()));Val::list(s)});fun558.call(args556,kw557)?});s.push({let fun561=e.get("_goal")?;let mut args559=Vec::new();let mut kw560=Vec::new();args559.push(Val::Str("placed".into()));args559.push(Val::Str("Every body the core carries is placed".into()));args559.push({let fun564=e.get("len")?;let mut args562=Vec::new();let mut kw563=Vec::new();args562.push(e.get("placed")?);fun564.call(args562,kw563)?});args559.push({let fun567=e.get("len")?;let mut args565=Vec::new();let mut kw566=Vec::new();args565.push(e.get("placed")?);fun567.call(args565,kw566)?});args559.push(Val::Str("a solid per body".into()));fun561.call(args559,kw560)?});s.push({let fun570=e.get("_goal")?;let mut args568=Vec::new();let mut kw569=Vec::new();args568.push(Val::Str("located".into()));args568.push(Val::Str("Every port a placed body declares is positioned".into()));args568.push({let fun573=e.get("len")?;let mut args571=Vec::new();let mut kw572=Vec::new();args571.push(e.get("mouths")?);fun573.call(args571,kw572)?});args568.push({let fun576=e.get("len")?;let mut args574=Vec::new();let mut kw575=Vec::new();args574.push(e.get("mouths")?);fun576.call(args574,kw575)?});args568.push(Val::Str("every mouth located".into()));fun570.call(args568,kw569)?});s.push({let fun579=e.get("_goal")?;let mut args577=Vec::new();let mut kw578=Vec::new();args577.push(Val::Str("routed".into()));args577.push(Val::Str("Every line the core owes is drawn".into()));args577.push({let fun582=e.get("len")?;let mut args580=Vec::new();let mut kw581=Vec::new();args580.push(e.get("fitted")?);fun582.call(args580,kw581)?});args577.push({let fun585=e.get("len")?;let mut args583=Vec::new();let mut kw584=Vec::new();args583.push(e.get("fitted")?);fun585.call(args583,kw584)?});args577.push(Val::Str("a line per connection".into()));fun579.call(args577,kw578)?});s.push({let fun588=e.get("_goal")?;let mut args586=Vec::new();let mut kw587=Vec::new();args586.push(Val::Str("mounted".into()));args586.push(Val::Str("A feature of another placed part locates every body".into()));args586.push({let fun591=e.get("sum")?;let mut args589=Vec::new();let mut kw590=Vec::new();args589.push({let e=e.child();let out592=Val::list(vec![]);for item593 in e.get("mounts")?.iter()? {let unpack594=unpack(item593,3)?;e.set("_n",unpack594[0].clone())?;e.set("by",unpack594[1].clone())?;e.set("_j",unpack594[2].clone())?;if {let v595=e.get("by")?;let v596=Val::None;Val::Bool(compare("is_not",v595.clone(),v596.clone())?.truthy()?)}.truthy()? {out592.attr("append")?.call(vec![Val::Int(1i64)],vec![])?;}}out592});fun591.call(args589,kw590)?});args586.push({let fun599=e.get("len")?;let mut args597=Vec::new();let mut kw598=Vec::new();args597.push(e.get("mounts")?);fun599.call(args597,kw598)?});args586.push(Val::Str("a located joint per body".into()));args586.push({let e=e.child();let out600=Val::list(vec![]);for item601 in e.get("mounts")?.iter()? {let unpack602=unpack(item601,3)?;e.set("n",unpack602[0].clone())?;e.set("by",unpack602[1].clone())?;e.set("j",unpack602[2].clone())?;if {let v603=e.get("by")?;let v604=Val::None;Val::Bool(compare("is",v603.clone(),v604.clone())?.truthy()?)}.truthy()? {out600.attr("append")?.call(vec![{let mut str605=String::new();str605.push_str(&format(&e.get("n")?,&String::new())?);str605.push_str(": ");str605.push_str(&format(&e.get("j")?,&String::new())?);Val::Str(str605)}],vec![])?;}}out600});fun588.call(args586,kw587)?});Val::list(s)};e.set("checks",assigned522.clone())?;
return Ok({let fun608=e.get("Scorecard")?;let mut args606=Vec::new();let mut kw607=Vec::new();args606.push(e.get("checks")?);args606.push({let fun611=e.get("_bend_rows")?;let mut args609=Vec::new();let mut kw610=Vec::new();args609.push(e.get("fitted")?);args609.push(e.get("a")?.attr("points")?);kw610.push(("route_data".into(),e.get("route_data")?));fun611.call(args609,kw610)?});args606.push({let fun614=e.get("sorted")?;let mut args612=Vec::new();let mut kw613=Vec::new();args612.push(e.get("placed")?);fun614.call(args612,kw613)?});fun608.call(args606,kw607)?});
Ok(Val::None)})})?;
    // report
    e.set("report", {
        let params = vec![
            ("a".into(), None, false),
            ("measurements".into(), None, true),
            ("body_bounds".into(), None, true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun617 = e.get("print")?;
                let mut args615 = Vec::new();
                let mut kw616 = Vec::new();
                args615.push(Val::Str("\ncold core".into()));
                fun617.call(args615, kw616)?
            };
            for item618 in {
                let fun639 = e.get("sorted")?;
                let mut args637 = Vec::new();
                let mut kw638 = Vec::new();
                args637.push({
                    let fun642 = e.get("a")?.attr("placed")?.attr("items")?;
                    let mut args640 = Vec::new();
                    let mut kw641 = Vec::new();
                    fun642.call(args640, kw641)?
                });
                fun639.call(args637, kw638)?
            }
            .iter()?
            {
                let unpack643 = unpack(item618, 2)?;
                e.set("name", unpack643[0].clone())?;
                e.set("solid", unpack643[1].clone())?;
                let mod619 = rt.import_module("types")?;
                e.set("SimpleNamespace", rt.member("types", "SimpleNamespace")?)?;
                let assigned620 = e.get("body_bounds")?.get(e.get("name")?)?;
                let unpack621 = unpack(assigned620.clone(), 2)?;
                e.set("low", unpack621[0].clone())?;
                e.set("high", unpack621[1].clone())?;
                let assigned622 = {
                    let fun625 = e.get("SimpleNamespace")?;
                    let mut args623 = Vec::new();
                    let mut kw624 = Vec::new();
                    kw624.push(("xmin".into(), e.get("low")?.get(Val::Int(0i64))?));
                    kw624.push(("ymin".into(), e.get("low")?.get(Val::Int(1i64))?));
                    kw624.push(("zmin".into(), e.get("low")?.get(Val::Int(2i64))?));
                    kw624.push(("xmax".into(), e.get("high")?.get(Val::Int(0i64))?));
                    kw624.push(("ymax".into(), e.get("high")?.get(Val::Int(1i64))?));
                    kw624.push(("zmax".into(), e.get("high")?.get(Val::Int(2i64))?));
                    fun625.call(args623, kw624)?
                };
                e.set("bb", assigned622.clone())?;
                {
                    let fun628 = e.get("print")?;
                    let mut args626 = Vec::new();
                    let mut kw627 = Vec::new();
                    args626.push({
                        let mut str629 = String::new();
                        str629.push_str("  ");
                        str629.push_str(&format(
                            &e.get("name")?,
                            &val_string({
                                let mut str630 = String::new();
                                str630.push_str("24");
                                Val::Str(str630)
                            })?,
                        )?);
                        str629.push_str(" [");
                        str629.push_str(&format(
                            &e.get("bb")?.attr("xmin")?,
                            &val_string({
                                let mut str631 = String::new();
                                str631.push_str("7.1f");
                                Val::Str(str631)
                            })?,
                        )?);
                        str629.push_str(",");
                        str629.push_str(&format(
                            &e.get("bb")?.attr("xmax")?,
                            &val_string({
                                let mut str632 = String::new();
                                str632.push_str("7.1f");
                                Val::Str(str632)
                            })?,
                        )?);
                        str629.push_str("] [");
                        str629.push_str(&format(
                            &e.get("bb")?.attr("ymin")?,
                            &val_string({
                                let mut str633 = String::new();
                                str633.push_str("7.1f");
                                Val::Str(str633)
                            })?,
                        )?);
                        str629.push_str(",");
                        str629.push_str(&format(
                            &e.get("bb")?.attr("ymax")?,
                            &val_string({
                                let mut str634 = String::new();
                                str634.push_str("7.1f");
                                Val::Str(str634)
                            })?,
                        )?);
                        str629.push_str("] [");
                        str629.push_str(&format(
                            &e.get("bb")?.attr("zmin")?,
                            &val_string({
                                let mut str635 = String::new();
                                str635.push_str("7.1f");
                                Val::Str(str635)
                            })?,
                        )?);
                        str629.push_str(",");
                        str629.push_str(&format(
                            &e.get("bb")?.attr("zmax")?,
                            &val_string({
                                let mut str636 = String::new();
                                str636.push_str("7.1f");
                                Val::Str(str636)
                            })?,
                        )?);
                        str629.push_str("]");
                        Val::Str(str629)
                    });
                    fun628.call(args626, kw627)?
                };
            }
            {
                let fun646 = e.get("print")?;
                let mut args644 = Vec::new();
                let mut kw645 = Vec::new();
                args644.push({
                    let mut str647 = String::new();
                    str647.push_str("\n  ");
                    str647.push_str(&format(
                        &{
                            let fun650 = e.get("len")?;
                            let mut args648 = Vec::new();
                            let mut kw649 = Vec::new();
                            args648.push(e.get("a")?.attr("placed")?);
                            fun650.call(args648, kw649)?
                        },
                        &String::new(),
                    )?);
                    str647.push_str(" bodies, ");
                    str647.push_str(&format(
                        &{
                            let fun653 = e.get("len")?;
                            let mut args651 = Vec::new();
                            let mut kw652 = Vec::new();
                            args651.push(e.get("a")?.attr("fitted")?);
                            fun653.call(args651, kw652)?
                        },
                        &String::new(),
                    )?);
                    str647.push_str(" lines, shell z 0..");
                    str647.push_str(&format(
                        &e.get("foam_shell_outer_height")?,
                        &val_string({
                            let mut str654 = String::new();
                            str654.push_str(".1f");
                            Val::Str(str654)
                        })?,
                    )?);
                    str647.push_str(", stack floor ");
                    str647.push_str(&format(
                        &e.get("_foam")?.attr("stack_floor_z")?,
                        &val_string({
                            let mut str655 = String::new();
                            str655.push_str(".1f");
                            Val::Str(str655)
                        })?,
                    )?);
                    str647.push_str(", cap face ");
                    str647.push_str(&format(
                        &e.get("_foam")?.attr("cap_face_z")?,
                        &val_string({
                            let mut str656 = String::new();
                            str656.push_str(".1f");
                            Val::Str(str656)
                        })?,
                    )?);
                    Val::Str(str647)
                });
                fun646.call(args644, kw645)?
            };
            {
                let fun659 = e.get("_V")?.attr("report")?;
                let mut args657 = Vec::new();
                let mut kw658 = Vec::new();
                kw658.push((
                    "port_mouths".into(),
                    e.get("measurements")?.get(Val::Str("mouths".into()))?,
                ));
                fun659.call(args657, kw658)?
            };
            let assigned660 = {
                let fun663 = e.get("_C")?.attr("wrap_points_xyz")?;
                let mut args661 = Vec::new();
                let mut kw662 = Vec::new();
                fun663.call(args661, kw662)?
            };
            e.set("points", assigned660.clone())?;
            {
                let fun666 = e.get("_C")?.attr("report")?;
                let mut args664 = Vec::new();
                let mut kw665 = Vec::new();
                kw665.push(("laid_length".into(), {
                    let fun669 = e.get("sum")?;
                    let mut args667 = Vec::new();
                    let mut kw668 = Vec::new();
                    args667.push({
                        let e = e.child();
                        let out670 = Val::list(vec![]);
                        for item671 in {
                            let fun674 = e.get("zip")?;
                            let mut args672 = Vec::new();
                            let mut kw673 = Vec::new();
                            args672.push(e.get("points")?);
                            args672.push(e.get("points")?.get(Val::Slice {
                                start: Some(Val::Int(1i64).integer()?),
                                stop: None,
                                step: 1,
                            })?);
                            fun674.call(args672, kw673)?
                        }
                        .iter()?
                        {
                            let unpack675 = unpack(item671, 2)?;
                            e.set("a", unpack675[0].clone())?;
                            e.set("b", unpack675[1].clone())?;
                            out670.attr("append")?.call(
                                vec![{
                                    let fun678 = e.get("math")?.attr("dist")?;
                                    let mut args676 = Vec::new();
                                    let mut kw677 = Vec::new();
                                    args676.push(e.get("a")?);
                                    args676.push(e.get("b")?);
                                    fun678.call(args676, kw677)?
                                }],
                                vec![],
                            )?;
                        }
                        out670
                    });
                    fun669.call(args667, kw668)?
                }));
                kw665.push(("tail_lengths".into(), {
                    let e = e.child();
                    let out679 = Val::dict(vec![]);
                    for item680 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("inlet".into()));
                        s.push(Val::Str("outlet".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("end", item680)?;
                        out679.set(e.get("end")?, {
                            let fun683 = e.get("_C")?.attr("tail_layout_length")?;
                            let mut args681 = Vec::new();
                            let mut kw682 = Vec::new();
                            args681.push(e.get("end")?);
                            fun683.call(args681, kw682)?
                        })?;
                    }
                    out679
                }));
                fun666.call(args664, kw665)?
            };
            let assigned684 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("seats", assigned684.clone())?;
            for item685 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("float-carb".into()));
                    s.push(e.get("_V")?.attr("ROD_RADIUS")?);
                    s.push(binary(
                        "truediv",
                        e.get("_V")?.attr("TUBE_ID")?,
                        Val::Float(2.0f64),
                    )?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("float-a".into()));
                    s.push(e.get("_I")?.attr("RES_ROD_X")?);
                    s.push(
                        e.get("measurements")?
                            .get(Val::Str("reservoir_walls".into()))?
                            .get(Val::Str("a".into()))?,
                    );
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("float-b".into()));
                    s.push(e.get("_I")?.attr("RES_ROD_X")?);
                    s.push(
                        e.get("measurements")?
                            .get(Val::Str("reservoir_walls".into()))?
                            .get(Val::Str("b".into()))?,
                    );
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack690 = unpack(item685, 3)?;
                e.set("name", unpack690[0].clone())?;
                e.set("park", unpack690[1].clone())?;
                e.set("wall", unpack690[2].clone())?;
                let assigned686 = {
                    let mut s = Vec::new();
                    s.push(e.get("park")?);
                    s.push(e.get("wall")?);
                    s.extend(
                        {
                            let fun689 = e.get("_I")?.attr("float_ride")?;
                            let mut args687 = Vec::new();
                            let mut kw688 = Vec::new();
                            args687.push(e.get("park")?);
                            args687.push(e.get("wall")?);
                            fun689.call(args687, kw688)?
                        }
                        .iter()?,
                    );
                    Val::tuple(s)
                };
                e.get("seats")?.set(e.get("name")?, assigned686.clone())?;
            }
            {
                let fun693 = e.get("_I")?.attr("report")?;
                let mut args691 = Vec::new();
                let mut kw692 = Vec::new();
                kw692.push(("rod_seats".into(), {
                    let e = e.child();
                    let out694 = Val::dict(vec![]);
                    for item695 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("a".into()));
                        s.push(Val::Str("b".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("letter", item695)?;
                        out694.set(
                            e.get("letter")?,
                            e.get("body_bounds")?
                                .get({
                                    let mut str696 = String::new();
                                    str696.push_str("float-rod-");
                                    str696.push_str(&format(&e.get("letter")?, &String::new())?);
                                    Val::Str(str696)
                                })?
                                .get(Val::Int(0i64))?
                                .get(Val::Int(2i64))?,
                        )?;
                    }
                    out694
                }));
                kw692.push(("seats".into(), e.get("seats")?));
                fun693.call(args691, kw692)?
            };
            Ok(Val::None)
        })
    })?;
    // rust_main
    e.set("rust_main", {
        let params = vec![("output".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("filecmp", rt.import_module("filecmp")?)?;
            e.set("os", rt.import_module("os")?)?;
            e.set("shutil", rt.import_module("shutil")?)?;
            let mod697 = rt.import_module("types")?;
            e.set("SimpleNamespace", rt.member("types", "SimpleNamespace")?)?;
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            e.set("core_numbers", rt.import_module("core_numbers")?)?;
            let mod698 = rt.import_module("_cadq_export")?;
            e.set("note_read", rt.member("_cadq_export", "note_read")?)?;
            e.set("note_write", rt.member("_cadq_export", "note_write")?)?;
            let assigned699 = if {
                let v700 = e.get("output")?;
                let v701 = Val::None;
                Val::Bool(compare("is_not", v700.clone(), v701.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun704 = e.get("Path")?;
                    let mut args702 = Vec::new();
                    let mut kw703 = Vec::new();
                    args702.push(e.get("output")?);
                    fun704.call(args702, kw703)?
                }
            } else {
                e.get("_here")?.attr("parent")?
            };
            e.set("output", assigned699.clone())?;
            {
                let fun707 = e.get("output")?.attr("mkdir")?;
                let mut args705 = Vec::new();
                let mut kw706 = Vec::new();
                kw706.push(("parents".into(), Val::Bool(true)));
                kw706.push(("exist_ok".into(), Val::Bool(true)));
                fun707.call(args705, kw706)?
            };
            let assigned708 = {
                let fun711 = e.get("core_numbers")?.attr("numbers")?;
                let mut args709 = Vec::new();
                let mut kw710 = Vec::new();
                fun711.call(args709, kw710)?
            };
            e.set("numbers", assigned708.clone())?;
            let assigned712 = {
                let fun715 = e.get("_rust_part")?.attr("cut")?;
                let mut args713 = Vec::new();
                let mut kw714 = Vec::new();
                args713.push(Val::Str("cold-core".into()));
                args713.push(Val::Str("cold-core-assembly".into()));
                args713.push(e.get("numbers")?);
                args713.push(e.get("output")?);
                fun715.call(args713, kw714)?
            };
            e.set("result", assigned712.clone())?;
            let assigned716 = e
                .get("result")?
                .get(Val::Str("bodies".into()))?
                .get(Val::Int(0i64))?
                .get(Val::Str("measurements".into()))?;
            e.set("measurements", assigned716.clone())?;
            let assigned717 = {
                let e = e.child();
                let out718 = Val::dict(vec![]);
                for item719 in e.get("numbers")?.get(Val::Str("bodies".into()))?.iter()? {
                    e.set("row", item719)?;
                    out718.set(e.get("row")?.get(Val::Str("name".into()))?, e.get("row")?)?;
                }
                out718
            };
            e.set("placed", assigned717.clone())?;
            let assigned720 = {
                let e = e.child();
                let out721 = Val::dict(vec![]);
                for item722 in e
                    .get("measurements")?
                    .get(Val::Str("routes".into()))?
                    .iter()?
                {
                    e.set("row", item722)?;
                    out721.set(e.get("row")?.get(Val::Str("name".into()))?, {
                        let mut s = Vec::new();
                        s.push(e.get("row")?.get(Val::Str("bend".into()))?);
                        s.push(Val::None);
                        Val::tuple(s)
                    })?;
                }
                out721
            };
            e.set("fitted", assigned720.clone())?;
            let assigned723 = {
                let fun726 = e.get("SimpleNamespace")?;
                let mut args724 = Vec::new();
                let mut kw725 = Vec::new();
                kw725.push(("placed".into(), e.get("placed")?));
                kw725.push(("fitted".into(), e.get("fitted")?));
                kw725.push(("points".into(), {
                    let e = e.child();
                    let out727 = Val::dict(vec![]);
                    for item728 in e
                        .get("measurements")?
                        .get(Val::Str("routes".into()))?
                        .iter()?
                    {
                        e.set("row", item728)?;
                        out727.set(
                            e.get("row")?.get(Val::Str("name".into()))?,
                            e.get("row")?.get(Val::Str("points".into()))?,
                        )?;
                    }
                    out727
                }));
                fun726.call(args724, kw725)?
            };
            e.set("a", assigned723.clone())?;
            let assigned729 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("bounds", assigned729.clone())?;
            for item730 in e.get("result")?.get(Val::Str("bodies".into()))?.iter()? {
                e.set("row", item730)?;
                let assigned731 = {
                    let fun734 = e.get("bounds")?.attr("setdefault")?;
                    let mut args732 = Vec::new();
                    let mut kw733 = Vec::new();
                    args732.push(e.get("row")?.get(Val::Str("name".into()))?);
                    args732.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun737 = e.get("list")?;
                            let mut args735 = Vec::new();
                            let mut kw736 = Vec::new();
                            args735.push(e.get("row")?.get(Val::Str("min".into()))?);
                            fun737.call(args735, kw736)?
                        });
                        s.push({
                            let fun740 = e.get("list")?;
                            let mut args738 = Vec::new();
                            let mut kw739 = Vec::new();
                            args738.push(e.get("row")?.get(Val::Str("max".into()))?);
                            fun740.call(args738, kw739)?
                        });
                        Val::tuple(s)
                    });
                    fun734.call(args732, kw733)?
                };
                let unpack741 = unpack(assigned731.clone(), 2)?;
                e.set("low", unpack741[0].clone())?;
                e.set("high", unpack741[1].clone())?;
                let assigned742 = {
                    let e = e.child();
                    let out743 = Val::list(vec![]);
                    for item744 in {
                        let fun747 = e.get("zip")?;
                        let mut args745 = Vec::new();
                        let mut kw746 = Vec::new();
                        args745.push(e.get("low")?);
                        args745.push(e.get("row")?.get(Val::Str("min".into()))?);
                        fun747.call(args745, kw746)?
                    }
                    .iter()?
                    {
                        let unpack748 = unpack(item744, 2)?;
                        e.set("a", unpack748[0].clone())?;
                        e.set("b", unpack748[1].clone())?;
                        out743.attr("append")?.call(
                            vec![{
                                let fun751 = e.get("min")?;
                                let mut args749 = Vec::new();
                                let mut kw750 = Vec::new();
                                args749.push(e.get("a")?);
                                args749.push(e.get("b")?);
                                fun751.call(args749, kw750)?
                            }],
                            vec![],
                        )?;
                    }
                    out743
                };
                e.get("low")?.set(
                    Val::Slice {
                        start: None,
                        stop: None,
                        step: 1,
                    },
                    assigned742.clone(),
                )?;
                let assigned752 = {
                    let e = e.child();
                    let out753 = Val::list(vec![]);
                    for item754 in {
                        let fun757 = e.get("zip")?;
                        let mut args755 = Vec::new();
                        let mut kw756 = Vec::new();
                        args755.push(e.get("high")?);
                        args755.push(e.get("row")?.get(Val::Str("max".into()))?);
                        fun757.call(args755, kw756)?
                    }
                    .iter()?
                    {
                        let unpack758 = unpack(item754, 2)?;
                        e.set("a", unpack758[0].clone())?;
                        e.set("b", unpack758[1].clone())?;
                        out753.attr("append")?.call(
                            vec![{
                                let fun761 = e.get("max")?;
                                let mut args759 = Vec::new();
                                let mut kw760 = Vec::new();
                                args759.push(e.get("a")?);
                                args759.push(e.get("b")?);
                                fun761.call(args759, kw760)?
                            }],
                            vec![],
                        )?;
                    }
                    out753
                };
                e.get("high")?.set(
                    Val::Slice {
                        start: None,
                        stop: None,
                        step: 1,
                    },
                    assigned752.clone(),
                )?;
            }
            {
                let fun764 = e.get("report")?;
                let mut args762 = Vec::new();
                let mut kw763 = Vec::new();
                args762.push(e.get("a")?);
                kw763.push(("measurements".into(), e.get("measurements")?));
                kw763.push(("body_bounds".into(), e.get("bounds")?));
                fun764.call(args762, kw763)?
            };
            let assigned765 = {
                let fun768 = e.get("build_card")?;
                let mut args766 = Vec::new();
                let mut kw767 = Vec::new();
                args766.push(e.get("a")?);
                kw767.push(("measurements".into(), e.get("measurements")?));
                fun768.call(args766, kw767)?
            };
            e.set("scorecard", assigned765.clone())?;
            {
                let fun771 = e.get("_card")?.attr("report")?;
                let mut args769 = Vec::new();
                let mut kw770 = Vec::new();
                args769.push(e.get("scorecard")?);
                fun771.call(args769, kw770)?
            };
            let assigned772 = binary(
                "truediv",
                e.get("output")?,
                Val::Str("cold-core-assembly.step".into()),
            )?;
            e.set("core_step", assigned772.clone())?;
            let assigned773 = if {
                let v780 = {
                    let fun776 = e.get("output")?.attr("resolve")?;
                    let mut args774 = Vec::new();
                    let mut kw775 = Vec::new();
                    fun776.call(args774, kw775)?
                };
                let v781 = {
                    let fun779 = e.get("_here")?.attr("parent")?.attr("resolve")?;
                    let mut args777 = Vec::new();
                    let mut kw778 = Vec::new();
                    fun779.call(args777, kw778)?
                };
                Val::Bool(compare("eq", v780.clone(), v781.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.get("FOAM_STEP")?
            } else {
                binary(
                    "truediv",
                    e.get("output")?,
                    Val::Str("foam-assembly.step".into()),
                )?
            };
            e.set("foam_step", assigned773.clone())?;
            for item782 in {
                let mut s = Vec::new();
                s.push(e.get("core_step")?);
                s.push(e.get("foam_step")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("step", item782)?;
                {
                    let fun785 = e.get("step")?.attr("parent")?.attr("mkdir")?;
                    let mut args783 = Vec::new();
                    let mut kw784 = Vec::new();
                    kw784.push(("parents".into(), Val::Bool(true)));
                    kw784.push(("exist_ok".into(), Val::Bool(true)));
                    fun785.call(args783, kw784)?
                };
                {
                    let fun788 = e.get("note_write")?;
                    let mut args786 = Vec::new();
                    let mut kw787 = Vec::new();
                    args786.push({
                        let fun791 = e.get("_card")?.attr("write")?;
                        let mut args789 = Vec::new();
                        let mut kw790 = Vec::new();
                        args789.push(e.get("scorecard")?);
                        args789.push(e.get("step")?);
                        fun791.call(args789, kw790)?
                    });
                    fun788.call(args786, kw787)?
                };
            }
            let mod792 = rt.import_module("_core_presentation")?;
            e.set("finish", rt.member("_core_presentation", "finish")?)?;
            {
                let fun795 = e.get("finish")?;
                let mut args793 = Vec::new();
                let mut kw794 = Vec::new();
                args793.push(e.get("core_step")?);
                args793.push(e.get("numbers")?.get(Val::Str("bodies".into()))?);
                fun795.call(args793, kw794)?
            };
            let assigned796 = binary(
                "truediv",
                e.get("output")?,
                Val::Str("cold-core-assembly.step.npz".into()),
            )?;
            e.set("fine", assigned796.clone())?;
            let assigned797 = binary(
                "truediv",
                e.get("output")?,
                e.get("MODEL_OUT")?.attr("name")?,
            )?;
            e.set("model", assigned797.clone())?;
            {
                let fun800 = e.get("note_read")?;
                let mut args798 = Vec::new();
                let mut kw799 = Vec::new();
                args798.push(e.get("fine")?);
                fun800.call(args798, kw799)?
            };
            if {
                let v804 = unary("not", {
                    let fun807 = e.get("model")?.attr("is_file")?;
                    let mut args805 = Vec::new();
                    let mut kw806 = Vec::new();
                    fun807.call(args805, kw806)?
                })?;
                if v804.truthy()? {
                    v804
                } else {
                    unary("not", {
                        let fun803 = e.get("filecmp")?.attr("cmp")?;
                        let mut args801 = Vec::new();
                        let mut kw802 = Vec::new();
                        args801.push(e.get("fine")?);
                        args801.push(e.get("model")?);
                        kw802.push(("shallow".into(), Val::Bool(false)));
                        fun803.call(args801, kw802)?
                    })?
                }
            }
            .truthy()?
            {
                let assigned808 = {
                    let fun811 = e.get("model")?.attr("with_name")?;
                    let mut args809 = Vec::new();
                    let mut kw810 = Vec::new();
                    args809.push({
                        let mut str812 = String::new();
                        str812.push_str(".");
                        str812.push_str(&format(&e.get("model")?.attr("name")?, &String::new())?);
                        str812.push_str(".");
                        str812.push_str(&format(
                            &{
                                let fun815 = e.get("os")?.attr("getpid")?;
                                let mut args813 = Vec::new();
                                let mut kw814 = Vec::new();
                                fun815.call(args813, kw814)?
                            },
                            &String::new(),
                        )?);
                        str812.push_str(".tmp");
                        Val::Str(str812)
                    });
                    fun811.call(args809, kw810)?
                };
                e.set("temporary", assigned808.clone())?;
                {
                    let fun818 = e.get("shutil")?.attr("copyfile")?;
                    let mut args816 = Vec::new();
                    let mut kw817 = Vec::new();
                    args816.push(e.get("fine")?);
                    args816.push(e.get("temporary")?);
                    fun818.call(args816, kw817)?
                };
                {
                    let fun821 = e.get("temporary")?.attr("replace")?;
                    let mut args819 = Vec::new();
                    let mut kw820 = Vec::new();
                    args819.push(e.get("model")?);
                    fun821.call(args819, kw820)?
                };
            }
            {
                let fun824 = e.get("note_write")?;
                let mut args822 = Vec::new();
                let mut kw823 = Vec::new();
                args822.push(e.get("model")?);
                fun824.call(args822, kw823)?
            };
            {
                let fun827 = e.get("print")?;
                let mut args825 = Vec::new();
                let mut kw826 = Vec::new();
                args825.push({
                    let mut str828 = String::new();
                    str828.push_str("-> ");
                    str828.push_str(&format(&e.get("model")?.attr("name")?, &String::new())?);
                    Val::Str(str828)
                });
                fun827.call(args825, kw826)?
            };
            return Ok(e.get("model")?);
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![("argv".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("argparse", rt.import_module("argparse")?)?;
            let assigned829 = {
                let fun832 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args830 = Vec::new();
                let mut kw831 = Vec::new();
                kw831.push(("description".into(), e.get("__doc__")?));
                fun832.call(args830, kw831)?
            };
            e.set("parser", assigned829.clone())?;
            {
                let fun835 = e.get("parser")?.attr("add_argument")?;
                let mut args833 = Vec::new();
                let mut kw834 = Vec::new();
                args833.push(Val::Str("--output".into()));
                kw834.push(("type".into(), e.get("Path")?));
                kw834.push((
                    "help".into(),
                    Val::Str("directory for generated assembly files".into()),
                ));
                fun835.call(args833, kw834)?
            };
            let assigned836 = {
                let fun839 = e.get("parser")?.attr("parse_args")?;
                let mut args837 = Vec::new();
                let mut kw838 = Vec::new();
                args837.push(e.get("argv")?);
                fun839.call(args837, kw838)?
            };
            e.set("args", assigned836.clone())?;
            {
                let fun842 = e.get("rust_main")?;
                let mut args840 = Vec::new();
                let mut kw841 = Vec::new();
                args840.push(e.get("args")?.attr("output")?);
                fun842.call(args840, kw841)?
            };
            return Ok(Val::Int(0i64));
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun845 = e.get("_rust_part")?.attr("start")?;
        let mut args843 = Vec::new();
        let mut kw844 = Vec::new();
        fun845.call(args843, kw844)?
    };
    {
        let fun848 = e.get("sys")?.attr("exit")?;
        let mut args846 = Vec::new();
        let mut kw847 = Vec::new();
        args846.push({
            let fun851 = e.get("main")?;
            let mut args849 = Vec::new();
            let mut kw850 = Vec::new();
            fun851.call(args849, kw850)?
        });
        fun848.call(args846, kw847)?
    };
    Ok(Val::None)
}
