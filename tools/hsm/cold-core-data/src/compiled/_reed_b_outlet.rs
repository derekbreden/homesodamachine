#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("importlib", rt.import_module("importlib")?)?;
    let assigned1 = Val::Float(6.0f64);
    e.set("depth", assigned1.clone())?;
    // datums
    e.set("datums", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned2 = {
                let fun5 = e.get("importlib")?.attr("import_module")?;
                let mut args3 = Vec::new();
                let mut kw4 = Vec::new();
                args3.push(Val::Str("_cold_core_interface".into()));
                fun5.call(args3, kw4)?
            };
            e.set("core", assigned2.clone())?;
            let assigned6 = binary(
                "truediv",
                unary("neg", e.get("core")?.attr("outer_shell_x_length")?)?,
                Val::Float(2.0f64),
            )?;
            e.set("front", assigned6.clone())?;
            let assigned7 = unary("neg", e.get("core")?.attr("reed_column_axis_x")?)?;
            e.set("axis", assigned7.clone())?;
            let assigned8 = e.get("core")?.attr("level_rod_y")?;
            e.set("y", assigned8.clone())?;
            let assigned9 = e.get("core")?.attr("reed_y_half_w")?;
            e.set("half", assigned9.clone())?;
            let assigned10 = e.get("core")?.attr("foam_shell_outer_height")?;
            e.set("top", assigned10.clone())?;
            let assigned11 = binary("sub", e.get("top")?, e.get("depth")?)?;
            e.set("bottom", assigned11.clone())?;
            let assigned12 = binary("add", e.get("top")?, Val::Float(0.25f64))?;
            e.set("shoulder", assigned12.clone())?;
            let assigned13 = binary(
                "add",
                e.get("shoulder")?,
                binary("mul", Val::Float(2.0f64), e.get("half")?)?,
            )?;
            e.set("peak", assigned13.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("axis_xy_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("axis")?);
                    s.push(e.get("y")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("front_x_mm".into()), e.get("front")?)?;
                d.set(
                    Val::Str("width_mm".into()),
                    binary("mul", Val::Float(2.0f64), e.get("half")?)?,
                )?;
                d.set(Val::Str("depth_mm".into()), e.get("depth")?)?;
                d.set(Val::Str("top_z_mm".into()), e.get("top")?)?;
                d.set(Val::Str("bottom_z_mm".into()), e.get("bottom")?)?;
                d.set(Val::Str("roof_shoulder_z_mm".into()), e.get("shoulder")?)?;
                d.set(Val::Str("roof_peak_z_mm".into()), e.get("peak")?)?;
                d.set(Val::Str("notch_min_mm".into()), {
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("front")?, Val::Float(1.0f64))?);
                    s.push(binary("sub", e.get("y")?, e.get("half")?)?);
                    s.push(e.get("bottom")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("notch_max_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("axis")?);
                    s.push(binary("add", e.get("y")?, e.get("half")?)?);
                    s.push(e.get("peak")?);
                    Val::tuple(s)
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // apply
    e.set("apply", {
        let params = vec![("shell".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned14 = {
                let fun17 = e.get("datums")?;
                let mut args15 = Vec::new();
                let mut kw16 = Vec::new();
                fun17.call(args15, kw16)?
            };
            e.set("d", assigned14.clone())?;
            let assigned18 = {
                let mut s = Vec::new();
                s.push(e.get("d")?.get(Val::Str("notch_min_mm".into()))?);
                s.push(e.get("d")?.get(Val::Str("notch_max_mm".into()))?);
                Val::tuple(s)
            };
            let unpack19 = unpack(assigned18.clone(), 2)?;
            e.set("lo", unpack19[0].clone())?;
            e.set("hi", unpack19[1].clone())?;
            let assigned20 = {
                let fun23 = e.get("cq")?.attr("Plane")?;
                let mut args21 = Vec::new();
                let mut kw22 = Vec::new();
                kw22.push(("origin".into(), {
                    let mut s = Vec::new();
                    s.push(e.get("lo")?.get(Val::Int(0i64))?);
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                }));
                kw22.push(("xDir".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                }));
                kw22.push(("normal".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                }));
                fun23.call(args21, kw22)?
            };
            e.set("plane", assigned20.clone())?;
            let assigned24 = e.get("d")?.get(Val::Str("roof_shoulder_z_mm".into()))?;
            e.set("shoulder", assigned24.clone())?;
            let assigned25 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("lo")?.get(Val::Int(1i64))?);
                    s.push(e.get("lo")?.get(Val::Int(2i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("hi")?.get(Val::Int(1i64))?);
                    s.push(e.get("lo")?.get(Val::Int(2i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("hi")?.get(Val::Int(1i64))?);
                    s.push(e.get("shoulder")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(
                        e.get("d")?
                            .get(Val::Str("axis_xy_mm".into()))?
                            .get(Val::Int(1i64))?,
                    );
                    s.push(e.get("d")?.get(Val::Str("roof_peak_z_mm".into()))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("lo")?.get(Val::Int(1i64))?);
                    s.push(e.get("shoulder")?);
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("profile", assigned25.clone())?;
            let assigned26 = {
                let fun29 = {
                    let fun32 = {
                        let fun35 = {
                            let fun38 = {
                                let fun41 = e.get("cq")?.attr("Workplane")?;
                                let mut args39 = Vec::new();
                                let mut kw40 = Vec::new();
                                args39.push(e.get("plane")?);
                                fun41.call(args39, kw40)?
                            }
                            .attr("polyline")?;
                            let mut args36 = Vec::new();
                            let mut kw37 = Vec::new();
                            args36.push(e.get("profile")?);
                            fun38.call(args36, kw37)?
                        }
                        .attr("close")?;
                        let mut args33 = Vec::new();
                        let mut kw34 = Vec::new();
                        fun35.call(args33, kw34)?
                    }
                    .attr("extrude")?;
                    let mut args30 = Vec::new();
                    let mut kw31 = Vec::new();
                    args30.push(binary(
                        "sub",
                        e.get("hi")?.get(Val::Int(0i64))?,
                        e.get("lo")?.get(Val::Int(0i64))?,
                    )?);
                    fun32.call(args30, kw31)?
                }
                .attr("val")?;
                let mut args27 = Vec::new();
                let mut kw28 = Vec::new();
                fun29.call(args27, kw28)?
            };
            e.set("opening", assigned26.clone())?;
            return Ok({
                let fun44 = e.get("shell")?.attr("cut")?;
                let mut args42 = Vec::new();
                let mut kw43 = Vec::new();
                args42.push(e.get("opening")?);
                fun44.call(args42, kw43)?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
