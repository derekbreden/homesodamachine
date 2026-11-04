#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let assigned1 = Val::Float(4.0f64);
    e.set("plate_thickness", assigned1.clone())?;
    let assigned2 = {
        let fun5 = e.get("dict")?;
        let mut args3 = Vec::new();
        let mut kw4 = Vec::new();
        kw4.push(("waist_d".into(), Val::Float(9.0f64)));
        kw4.push(("flare_d".into(), Val::Float(11.0f64)));
        kw4.push(("bore_d".into(), Val::Float(6.2f64)));
        kw4.push(("lead_d".into(), Val::Float(7.0f64)));
        kw4.push(("lead_h".into(), Val::Float(0.4f64)));
        fun5.call(args3, kw4)?
    };
    e.set("liquid_grip", assigned2.clone())?;
    let assigned6 = {
        let fun9 = e.get("dict")?;
        let mut args7 = Vec::new();
        let mut kw8 = Vec::new();
        kw8.push(("waist_d".into(), Val::Float(6.0f64)));
        kw8.push(("flare_d".into(), Val::Float(8.0f64)));
        kw8.push(("bore_d".into(), Val::Float(3.9f64)));
        kw8.push(("lead_d".into(), Val::Float(4.5f64)));
        kw8.push(("lead_h".into(), Val::Float(0.3f64)));
        fun9.call(args7, kw8)?
    };
    e.set("air_grip", assigned6.clone())?;
    let assigned10 = {
        let d = Val::dict(vec![]);
        d.set(unary("pos", Val::Int(1i64))?, {
            let mut s = Vec::new();
            s.push(Val::Float(120.0f64));
            s.push(unary("neg", Val::Float(26.0f64))?);
            Val::tuple(s)
        })?;
        d.set(unary("neg", Val::Int(1i64))?, {
            let mut s = Vec::new();
            s.push(unary("neg", Val::Float(109.0f64))?);
            s.push(unary("neg", Val::Float(32.5f64))?);
            Val::tuple(s)
        })?;
        d
    };
    e.set("air_position", assigned10.clone())?;
    let assigned11 = Val::Float(4.0f64);
    e.set("air_tube_od", assigned11.clone())?;
    let assigned12 = Val::Float(2.5f64);
    e.set("air_tube_id", assigned12.clone())?;
    let assigned13 = Val::Float(6.0f64);
    e.set("air_tube_above_casing", assigned13.clone())?;
    let assigned14 = Val::Float(1.0f64);
    e.set("air_tube_below_lid", assigned14.clone())?;
    let assigned15 = Val::Float(5.2f64);
    e.set("air_passage_diameter", assigned15.clone())?;
    let assigned16 = Val::Float(3.0f64);
    e.set("air_passage_wall", assigned16.clone())?;
    // __getattr__
    e.set("__getattr__", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v17 = e.get("name")?;
                let v18 = Val::Str("cq".into());
                Val::Bool(compare("eq", v17.clone(), v18.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.set("cadquery", rt.import_module("cadquery")?)?;
                return Ok(e.get("cadquery")?);
            }
            anyhow::bail!(
                "{}",
                val_string({
                    let fun21 = e.get("AttributeError")?;
                    let mut args19 = Vec::new();
                    let mut kw20 = Vec::new();
                    args19.push(e.get("name")?);
                    fun21.call(args19, kw20)?
                })?
            );
            Ok(Val::None)
        })
    })?;
    // cylinder
    e.set("cylinder", {
        let params = vec![
            ("xy".into(), None, false),
            ("z0".into(), None, false),
            ("z1".into(), None, false),
            ("diameter".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            return Ok({
                let fun24 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args22 = Vec::new();
                let mut kw23 = Vec::new();
                args22.push(binary("truediv", e.get("diameter")?, Val::Int(2i64))?);
                args22.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                args22.push({
                    let fun27 = e.get("cq")?.attr("Vector")?;
                    let mut args25 = Vec::new();
                    let mut kw26 = Vec::new();
                    args25.extend(e.get("xy")?.iter()?);
                    args25.push(e.get("z0")?);
                    fun27.call(args25, kw26)?
                });
                fun24.call(args22, kw23)?
            });
            Ok(Val::None)
        })
    })?;
    // spool_envelope
    e.set("spool_envelope", {
        let params = vec![
            ("xy".into(), None, false),
            ("z0".into(), None, false),
            ("specification".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned28 = binary("add", e.get("z0")?, e.get("plate_thickness")?)?;
            e.set("z1", assigned28.clone())?;
            let assigned29 = binary(
                "truediv",
                e.get("specification")?.get(Val::Str("waist_d".into()))?,
                Val::Int(2i64),
            )?;
            e.set("waist", assigned29.clone())?;
            let assigned30 = binary(
                "truediv",
                e.get("specification")?.get(Val::Str("flare_d".into()))?,
                Val::Int(2i64),
            )?;
            e.set("flare", assigned30.clone())?;
            let assigned31 = binary("sub", e.get("flare")?, e.get("waist")?)?;
            e.set("depth", assigned31.clone())?;
            return Ok({
                let fun34 = {
                    let fun37 = {
                        let fun40 = e.get("cylinder")?;
                        let mut args38 = Vec::new();
                        let mut kw39 = Vec::new();
                        args38.push(e.get("xy")?);
                        args38.push(e.get("z0")?);
                        args38.push(e.get("z1")?);
                        args38.push(binary("mul", Val::Int(2i64), e.get("waist")?)?);
                        fun40.call(args38, kw39)?
                    }
                    .attr("fuse")?;
                    let mut args35 = Vec::new();
                    let mut kw36 = Vec::new();
                    args35.push({
                        let fun43 = e.get("cq")?.attr("Solid")?.attr("makeCone")?;
                        let mut args41 = Vec::new();
                        let mut kw42 = Vec::new();
                        args41.push(e.get("flare")?);
                        args41.push(e.get("waist")?);
                        args41.push(e.get("depth")?);
                        args41.push({
                            let fun46 = e.get("cq")?.attr("Vector")?;
                            let mut args44 = Vec::new();
                            let mut kw45 = Vec::new();
                            args44.extend(e.get("xy")?.iter()?);
                            args44.push(e.get("z0")?);
                            fun46.call(args44, kw45)?
                        });
                        fun43.call(args41, kw42)?
                    });
                    args35.push({
                        let fun49 = e.get("cq")?.attr("Solid")?.attr("makeCone")?;
                        let mut args47 = Vec::new();
                        let mut kw48 = Vec::new();
                        args47.push(e.get("waist")?);
                        args47.push(e.get("flare")?);
                        args47.push(e.get("depth")?);
                        args47.push({
                            let fun52 = e.get("cq")?.attr("Vector")?;
                            let mut args50 = Vec::new();
                            let mut kw51 = Vec::new();
                            args50.extend(e.get("xy")?.iter()?);
                            args50.push(binary("sub", e.get("z1")?, e.get("depth")?)?);
                            fun52.call(args50, kw51)?
                        });
                        fun49.call(args47, kw48)?
                    });
                    fun37.call(args35, kw36)?
                }
                .attr("clean")?;
                let mut args32 = Vec::new();
                let mut kw33 = Vec::new();
                fun34.call(args32, kw33)?
            });
            Ok(Val::None)
        })
    })?;
    // seat_tool
    e.set("seat_tool", {
        let params = vec![
            ("xy".into(), None, false),
            ("z0".into(), None, false),
            ("specification".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned53 = binary("add", e.get("z0")?, e.get("plate_thickness")?)?;
            e.set("z1", assigned53.clone())?;
            return Ok({
                let fun56 = {
                    let fun59 = e.get("spool_envelope")?;
                    let mut args57 = Vec::new();
                    let mut kw58 = Vec::new();
                    args57.push(e.get("xy")?);
                    args57.push(e.get("z0")?);
                    args57.push(e.get("specification")?);
                    fun59.call(args57, kw58)?
                }
                .attr("fuse")?;
                let mut args54 = Vec::new();
                let mut kw55 = Vec::new();
                args54.push({
                    let fun62 = e.get("cylinder")?;
                    let mut args60 = Vec::new();
                    let mut kw61 = Vec::new();
                    args60.push(e.get("xy")?);
                    args60.push(e.get("z1")?);
                    args60.push(binary("add", e.get("z1")?, Val::Float(0.1f64))?);
                    args60.push(e.get("specification")?.get(Val::Str("flare_d".into()))?);
                    fun62.call(args60, kw61)?
                });
                fun56.call(args54, kw55)?
            });
            Ok(Val::None)
        })
    })?;
    // build_grommet
    e.set("build_grommet", {
        let params = vec![
            ("specification".into(), None, false),
            (
                "xy".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                }),
                false,
            ),
            ("z0".into(), Some(Val::Float(0.0f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned63 = binary("add", e.get("z0")?, e.get("plate_thickness")?)?;
            e.set("z1", assigned63.clone())?;
            let assigned64 = binary(
                "truediv",
                e.get("specification")?.get(Val::Str("bore_d".into()))?,
                Val::Int(2i64),
            )?;
            e.set("radius", assigned64.clone())?;
            let assigned65 = binary(
                "truediv",
                e.get("specification")?.get(Val::Str("lead_d".into()))?,
                Val::Int(2i64),
            )?;
            e.set("lead_radius", assigned65.clone())?;
            let assigned66 = e.get("specification")?.get(Val::Str("lead_h".into()))?;
            e.set("lead_height", assigned66.clone())?;
            let assigned67 = {
                let fun70 = {
                    let fun73 = e.get("cylinder")?;
                    let mut args71 = Vec::new();
                    let mut kw72 = Vec::new();
                    args71.push(e.get("xy")?);
                    args71.push(binary("sub", e.get("z0")?, Val::Float(0.1f64))?);
                    args71.push(binary("add", e.get("z1")?, Val::Float(0.1f64))?);
                    args71.push(binary("mul", Val::Int(2i64), e.get("radius")?)?);
                    fun73.call(args71, kw72)?
                }
                .attr("fuse")?;
                let mut args68 = Vec::new();
                let mut kw69 = Vec::new();
                args68.push({
                    let fun76 = e.get("cq")?.attr("Solid")?.attr("makeCone")?;
                    let mut args74 = Vec::new();
                    let mut kw75 = Vec::new();
                    args74.push(e.get("lead_radius")?);
                    args74.push(e.get("radius")?);
                    args74.push(e.get("lead_height")?);
                    args74.push({
                        let fun79 = e.get("cq")?.attr("Vector")?;
                        let mut args77 = Vec::new();
                        let mut kw78 = Vec::new();
                        args77.extend(e.get("xy")?.iter()?);
                        args77.push(e.get("z0")?);
                        fun79.call(args77, kw78)?
                    });
                    fun76.call(args74, kw75)?
                });
                args68.push({
                    let fun82 = e.get("cq")?.attr("Solid")?.attr("makeCone")?;
                    let mut args80 = Vec::new();
                    let mut kw81 = Vec::new();
                    args80.push(e.get("radius")?);
                    args80.push(e.get("lead_radius")?);
                    args80.push(e.get("lead_height")?);
                    args80.push({
                        let fun85 = e.get("cq")?.attr("Vector")?;
                        let mut args83 = Vec::new();
                        let mut kw84 = Vec::new();
                        args83.extend(e.get("xy")?.iter()?);
                        args83.push(binary("sub", e.get("z1")?, e.get("lead_height")?)?);
                        fun85.call(args83, kw84)?
                    });
                    fun82.call(args80, kw81)?
                });
                fun70.call(args68, kw69)?
            };
            e.set("opening", assigned67.clone())?;
            return Ok({
                let fun88 = {
                    let fun91 = {
                        let fun94 = e.get("spool_envelope")?;
                        let mut args92 = Vec::new();
                        let mut kw93 = Vec::new();
                        args92.push(e.get("xy")?);
                        args92.push(e.get("z0")?);
                        args92.push(e.get("specification")?);
                        fun94.call(args92, kw93)?
                    }
                    .attr("cut")?;
                    let mut args89 = Vec::new();
                    let mut kw90 = Vec::new();
                    args89.push(e.get("opening")?);
                    fun91.call(args89, kw90)?
                }
                .attr("clean")?;
                let mut args86 = Vec::new();
                let mut kw87 = Vec::new();
                fun88.call(args86, kw87)?
            });
            Ok(Val::None)
        })
    })?;
    // build_air_tube
    e.set("build_air_tube", {
        let params = vec![
            ("side".into(), None, false),
            ("lid_underside_z".into(), None, false),
            ("casing_face_z".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned95 = e.get("air_position")?.get(e.get("side")?)?;
            e.set("xy", assigned95.clone())?;
            let assigned96 = binary(
                "sub",
                e.get("lid_underside_z")?,
                e.get("air_tube_below_lid")?,
            )?;
            e.set("z0", assigned96.clone())?;
            let assigned97 = binary(
                "add",
                e.get("casing_face_z")?,
                e.get("air_tube_above_casing")?,
            )?;
            e.set("z1", assigned97.clone())?;
            return Ok({
                let fun100 = {
                    let fun103 = {
                        let fun106 = e.get("cylinder")?;
                        let mut args104 = Vec::new();
                        let mut kw105 = Vec::new();
                        args104.push(e.get("xy")?);
                        args104.push(e.get("z0")?);
                        args104.push(e.get("z1")?);
                        args104.push(e.get("air_tube_od")?);
                        fun106.call(args104, kw105)?
                    }
                    .attr("cut")?;
                    let mut args101 = Vec::new();
                    let mut kw102 = Vec::new();
                    args101.push({
                        let fun109 = e.get("cylinder")?;
                        let mut args107 = Vec::new();
                        let mut kw108 = Vec::new();
                        args107.push(e.get("xy")?);
                        args107.push(binary("sub", e.get("z0")?, Val::Float(0.1f64))?);
                        args107.push(binary("add", e.get("z1")?, Val::Float(0.1f64))?);
                        args107.push(e.get("air_tube_id")?);
                        fun109.call(args107, kw108)?
                    });
                    fun103.call(args101, kw102)?
                }
                .attr("clean")?;
                let mut args98 = Vec::new();
                let mut kw99 = Vec::new();
                fun100.call(args98, kw99)?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
