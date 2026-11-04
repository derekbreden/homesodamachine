#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("_cold_core_interface")?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    let mod2 = rt.import_module("_reservoir_pocket_walls")?;
    e.set(
        "build_reservoir_pocket_walls",
        rt.member("_reservoir_pocket_walls", "build_reservoir_pocket_walls")?,
    )?;
    let mod3 = rt.import_module("_support_ring")?;
    e.set(
        "build_carbonator_support_ring",
        rt.member("_support_ring", "build_carbonator_support_ring")?,
    )?;
    let mod4 = rt.import_module("_outer_shell")?;
    e.set(
        "build_outer_shell",
        rt.member("_outer_shell", "build_outer_shell")?,
    )?;
    e.set(
        "cut_insert_pockets",
        rt.member("_outer_shell", "cut_insert_pockets")?,
    )?;
    let mod5 = rt.import_module("_port_cuts")?;
    e.set(
        "cut_copper_ports",
        rt.member("_port_cuts", "cut_copper_ports")?,
    )?;
    e.set(
        "cut_prv_vent_port",
        rt.member("_port_cuts", "cut_prv_vent_port")?,
    )?;
    let mod6 = rt.import_module("_reed_channels")?;
    e.set(
        "build_reed_channels",
        rt.member("_reed_channels", "build_reed_channels")?,
    )?;
    e.set(
        "cut_reed_channel_openings",
        rt.member("_reed_channels", "cut_reed_channel_openings")?,
    )?;
    e.set("_reed_b_outlet", rt.import_module("_reed_b_outlet")?)?;
    // build_full_shell
    e.set("build_full_shell", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned7 = {
                let fun10 = {
                    let fun13 = {
                        let fun16 = {
                            let fun19 = {
                                let fun22 = e.get("build_reservoir_pocket_walls")?;
                                let mut args20 = Vec::new();
                                let mut kw21 = Vec::new();
                                fun22.call(args20, kw21)?
                            }
                            .attr("union")?;
                            let mut args17 = Vec::new();
                            let mut kw18 = Vec::new();
                            args17.push({
                                let fun25 = e.get("build_carbonator_support_ring")?;
                                let mut args23 = Vec::new();
                                let mut kw24 = Vec::new();
                                fun25.call(args23, kw24)?
                            });
                            fun19.call(args17, kw18)?
                        }
                        .attr("union")?;
                        let mut args14 = Vec::new();
                        let mut kw15 = Vec::new();
                        args14.push({
                            let fun28 = e.get("build_outer_shell")?;
                            let mut args26 = Vec::new();
                            let mut kw27 = Vec::new();
                            fun28.call(args26, kw27)?
                        });
                        fun16.call(args14, kw15)?
                    }
                    .attr("union")?;
                    let mut args11 = Vec::new();
                    let mut kw12 = Vec::new();
                    args11.push({
                        let fun31 = e.get("build_reed_channels")?;
                        let mut args29 = Vec::new();
                        let mut kw30 = Vec::new();
                        kw30.push(("side".into(), unary("pos", Val::Int(1i64))?));
                        fun31.call(args29, kw30)?
                    });
                    fun13.call(args11, kw12)?
                }
                .attr("union")?;
                let mut args8 = Vec::new();
                let mut kw9 = Vec::new();
                args8.push({
                    let fun34 = e.get("build_reed_channels")?;
                    let mut args32 = Vec::new();
                    let mut kw33 = Vec::new();
                    kw33.push(("side".into(), unary("neg", Val::Int(1i64))?));
                    fun34.call(args32, kw33)?
                });
                fun10.call(args8, kw9)?
            };
            e.set("foam_shell", assigned7.clone())?;
            let assigned35 = {
                let fun38 = e.get("cut_insert_pockets")?;
                let mut args36 = Vec::new();
                let mut kw37 = Vec::new();
                args36.push(e.get("foam_shell")?);
                fun38.call(args36, kw37)?
            };
            e.set("foam_shell", assigned35.clone())?;
            for item39 in {
                let mut s = Vec::new();
                s.push(e.get("cut_prv_vent_port")?);
                s.push(e.get("cut_copper_ports")?);
                s.push(e.get("cut_reed_channel_openings")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("cut", item39)?;
                let assigned40 = {
                    let fun43 = e.get("cut")?;
                    let mut args41 = Vec::new();
                    let mut kw42 = Vec::new();
                    args41.push(e.get("foam_shell")?);
                    fun43.call(args41, kw42)?
                };
                e.set("foam_shell", assigned40.clone())?;
            }
            e.set("_reservoir_b_fill", rt.import_module("_reservoir_b_fill")?)?;
            let mod44 = rt.import_module("_above_core_mounts")?;
            e.set(
                "world_shape_in_cap",
                rt.member("_above_core_mounts", "world_shape_in_cap")?,
            )?;
            let mod45 = rt.import_module("_foam_cap")?;
            e.set("top_cap_height", rt.member("_foam_cap", "top_cap_height")?)?;
            let assigned46 = {
                let fun49 = {
                    let fun52 = {
                        let fun55 = e.get("world_shape_in_cap")?;
                        let mut args53 = Vec::new();
                        let mut kw54 = Vec::new();
                        args53.push({
                            let fun58 = e.get("_reservoir_b_fill")?.attr("channel_air")?;
                            let mut args56 = Vec::new();
                            let mut kw57 = Vec::new();
                            fun58.call(args56, kw57)?
                        });
                        fun55.call(args53, kw54)?
                    }
                    .attr("rotate")?;
                    let mut args50 = Vec::new();
                    let mut kw51 = Vec::new();
                    args50.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    args50.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        Val::tuple(s)
                    });
                    args50.push(Val::Float(180.0f64));
                    fun52.call(args50, kw51)?
                }
                .attr("translate")?;
                let mut args47 = Vec::new();
                let mut kw48 = Vec::new();
                args47.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(binary(
                        "add",
                        e.get("foam_shell_outer_height")?,
                        e.get("top_cap_height")?,
                    )?);
                    Val::tuple(s)
                });
                fun49.call(args47, kw48)?
            };
            e.set("entry_air", assigned46.clone())?;
            return Ok({
                let fun61 = e.get("_reed_b_outlet")?.attr("apply")?;
                let mut args59 = Vec::new();
                let mut kw60 = Vec::new();
                args59.push({
                    let fun64 = e.get("foam_shell")?.attr("cut")?;
                    let mut args62 = Vec::new();
                    let mut kw63 = Vec::new();
                    args62.push(e.get("entry_air")?);
                    fun64.call(args62, kw63)?
                });
                fun61.call(args59, kw60)?
            });
            Ok(Val::None)
        })
    })?;
    // import_shell
    e.set("import_shell", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let mod65 = rt.import_module("_cadq_export")?;
            e.set("import_step", rt.member("_cadq_export", "import_step")?)?;
            if unary("not", {
                let fun68 = e.get("getattr")?;
                let mut args66 = Vec::new();
                let mut kw67 = Vec::new();
                args66.push(e.get("cq")?);
                args66.push(Val::Str("MESH".into()));
                args66.push(Val::Bool(false));
                fun68.call(args66, kw67)?
            })?
            .truthy()?
            {
                let context69 = {
                    let fun72 = e.get("open")?;
                    let mut args70 = Vec::new();
                    let mut kw71 = Vec::new();
                    args70.push(e.get("path")?);
                    args70.push(Val::Str("rb".into()));
                    fun72.call(args70, kw71)?
                };
                e.set("stream", context69.attr("__enter__")?.call(vec![], vec![])?)?;
                let context_result79 = (|| -> Result<Flow> {
                    let assigned73 = {
                        let v77 = Val::Bytes(vec![
                            109, 101, 115, 104, 99, 97, 100, 32, 116, 101, 115, 115, 101, 108, 108,
                            97, 116, 101, 100,
                        ]);
                        let v78 = {
                            let fun76 = e.get("stream")?.attr("read")?;
                            let mut args74 = Vec::new();
                            let mut kw75 = Vec::new();
                            args74.push(Val::Int(200i64));
                            fun76.call(args74, kw75)?
                        };
                        Val::Bool(compare("in", v77.clone(), v78.clone())?.truthy()?)
                    };
                    e.set("triangles", assigned73.clone())?;
                    Ok(Flow::Continue)
                })();
                context69
                    .attr("__exit__")?
                    .call(vec![Val::None, Val::None, Val::None], vec![])?;
                match context_result79? {
                    Flow::Continue => {}
                    Flow::Return(value) => return Ok(value),
                    Flow::Break => anyhow::bail!("break outside a loop"),
                    Flow::Next => anyhow::bail!("continue outside a loop"),
                }
                if e.get("triangles")?.truthy()? {
                    return Ok({
                        let fun82 = {
                            let fun85 = e.get("build_full_shell")?;
                            let mut args83 = Vec::new();
                            let mut kw84 = Vec::new();
                            fun85.call(args83, kw84)?
                        }
                        .attr("val")?;
                        let mut args80 = Vec::new();
                        let mut kw81 = Vec::new();
                        fun82.call(args80, kw81)?
                    });
                }
            }
            return Ok({
                let fun88 = {
                    let fun91 = e.get("import_step")?;
                    let mut args89 = Vec::new();
                    let mut kw90 = Vec::new();
                    args89.push({
                        let fun94 = e.get("str")?;
                        let mut args92 = Vec::new();
                        let mut kw93 = Vec::new();
                        args92.push(e.get("path")?);
                        fun94.call(args92, kw93)?
                    });
                    fun91.call(args89, kw90)?
                }
                .attr("val")?;
                let mut args86 = Vec::new();
                let mut kw87 = Vec::new();
                fun88.call(args86, kw87)?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
