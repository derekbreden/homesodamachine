#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let assigned2 = {
        let mut s = Vec::new();
        s.push(Val::Float(57.25f64));
        s.push(Val::Float(209.75f64));
        s.push(Val::Float(258.5f64));
        Val::tuple(s)
    };
    e.set("CENTRE", assigned2.clone())?;
    let assigned3 = Val::Float(13.5f64);
    e.set("PITCH", assigned3.clone())?;
    let assigned4 = Val::Float(6.35f64);
    e.set("TUBE_OD", assigned4.clone())?;
    let assigned5 = Val::Float(6.35f64);
    e.set("BORE", assigned5.clone())?;
    let assigned6 = Val::Float(2.4f64);
    e.set("WING", assigned6.clone())?;
    let assigned7 = Val::Float(125.42102606277044f64);
    e.set("TIP_DEGREES", assigned7.clone())?;
    let assigned8 = Val::Float(8.0f64);
    e.set("SPAN", assigned8.clone())?;
    let assigned9 = Val::Float(253.4f64);
    e.set("LID_FACE", assigned9.clone())?;
    let assigned10 = Val::Float(3.0f64);
    e.set("FLOOR", assigned10.clone())?;
    // specification
    e.set("specification",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned11=binary("truediv",e.get("BORE")?,Val::Int(2i64))?;e.set("radius",assigned11.clone())?;
let assigned12=binary("add",e.get("radius")?,e.get("WING")?)?;e.set("outer",assigned12.clone())?;
let assigned13=e.get("CENTRE")?;let unpack14=unpack(assigned13.clone(),3)?;e.set("x",unpack14[0].clone())?;e.set("y",unpack14[1].clone())?;e.set("z",unpack14[2].clone())?;
let assigned15={let e=e.child();let out16=Val::list(vec![]);for item17 in {let mut s=Vec::new();s.push(unary("neg",Val::Float(1.0f64))?);s.push(Val::Float(1.0f64));Val::tuple(s)}.iter()? {e.set("side",item17)?;out16.attr("append")?.call(vec![{let mut s=Vec::new();s.push(binary("add",e.get("x")?,binary("truediv",binary("mul",e.get("side")?,e.get("PITCH")?)?,Val::Int(2i64))?)?);s.push(e.get("y")?);s.push(e.get("z")?);Val::list(s)}],vec![])?;}out16};e.set("centres",assigned15.clone())?;
let assigned18={let mut s=Vec::new();s.push(binary("sub",e.get("centres")?.get(Val::Int(0i64))?.get(Val::Int(0i64))?,e.get("outer")?)?);s.push(binary("sub",e.get("y")?,binary("truediv",e.get("SPAN")?,Val::Int(2i64))?)?);s.push(binary("sub",e.get("LID_FACE")?,e.get("FLOOR")?)?);Val::list(s)};e.set("low",assigned18.clone())?;
let assigned19={let mut s=Vec::new();s.push(binary("add",e.get("centres")?.get(unary("neg",Val::Int(1i64))?)?.get(Val::Int(0i64))?,e.get("outer")?)?);s.push(binary("add",e.get("y")?,binary("truediv",e.get("SPAN")?,Val::Int(2i64))?)?);s.push(e.get("z")?);Val::list(s)};e.set("high",assigned19.clone())?;
let assigned20=binary("truediv",e.get("WING")?,Val::Int(2i64))?;e.set("nose",assigned20.clone())?;
let assigned21=binary("add",e.get("radius")?,e.get("nose")?)?;e.set("middle",assigned21.clone())?;
let assigned22=binary("sub",binary("add",binary("truediv",e.get("TUBE_OD")?,Val::Int(2i64))?,e.get("nose")?)?,binary("mul",e.get("middle")?,{let fun25=e.get("math")?.attr("sin")?;let mut args23=Vec::new();let mut kw24=Vec::new();args23.push({let fun28=e.get("math")?.attr("radians")?;let mut args26=Vec::new();let mut kw27=Vec::new();args26.push(e.get("TIP_DEGREES")?);fun28.call(args26,kw27)?});fun25.call(args23,kw24)?})?)?;e.set("spread",assigned22.clone())?;
return Ok({let fun31=e.get("dict")?;let mut args29=Vec::new();let mut kw30=Vec::new();kw30.push(("closure".into(),Val::Str("direct-snap".into())));kw30.push(("centre_world_mm".into(),{let fun34=e.get("list")?;let mut args32=Vec::new();let mut kw33=Vec::new();args32.push(e.get("CENTRE")?);fun34.call(args32,kw33)?}));kw30.push(("tube_centers_world_mm".into(),e.get("centres")?));kw30.push(("tube_axis_world".into(),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));Val::list(s)}));kw30.push(("tube_axis_worlds".into(),binary("mul",{let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));Val::list(s)});Val::list(s)},Val::Int(2i64))?));kw30.push(("tube_od_mm".into(),e.get("TUBE_OD")?));kw30.push(("bore_diameter_mm".into(),e.get("BORE")?));kw30.push(("seat_radius_mm".into(),e.get("radius")?));kw30.push(("tube_pitch_mm".into(),e.get("PITCH")?));kw30.push(("station_length_mm".into(),e.get("SPAN")?));kw30.push(("spring_thickness_mm".into(),e.get("WING")?));kw30.push(("tip_degrees".into(),e.get("TIP_DEGREES")?));kw30.push(("lid_face_z_mm".into(),e.get("LID_FACE")?));kw30.push(("base_floor_world_z_mm".into(),binary("sub",e.get("LID_FACE")?,e.get("FLOOR")?)?));kw30.push(("base_top_world_z_mm".into(),e.get("z")?));kw30.push(("base_bounds_mm".into(),{let mut s=Vec::new();s.push(e.get("low")?);s.push(e.get("high")?);Val::list(s)}));kw30.push(("body_bounds_mm".into(),{let mut s=Vec::new();s.push(e.get("low")?);s.push({let mut s=Vec::new();s.push(e.get("high")?.get(Val::Int(0i64))?);s.push(e.get("high")?.get(Val::Int(1i64))?);s.push(binary("add",binary("sub",e.get("z")?,binary("mul",e.get("middle")?,{let fun37=e.get("math")?.attr("cos")?;let mut args35=Vec::new();let mut kw36=Vec::new();args35.push({let fun40=e.get("math")?.attr("radians")?;let mut args38=Vec::new();let mut kw39=Vec::new();args38.push(e.get("TIP_DEGREES")?);fun40.call(args38,kw39)?});fun37.call(args35,kw36)?})?)?,e.get("nose")?)?);Val::list(s)});Val::list(s)}));kw30.push(("floor_stock_mm".into(),e.get("FLOOR")?));kw30.push(("outer_radius_mm".into(),e.get("outer")?));kw30.push(("outer_width_mm".into(),binary("add",e.get("PITCH")?,binary("mul",Val::Int(2i64),e.get("outer")?)?)?));kw30.push(("central_land_mm".into(),binary("sub",e.get("PITCH")?,e.get("BORE")?)?));kw30.push(("static_outer_gap_mm".into(),binary("sub",e.get("PITCH")?,binary("mul",Val::Int(2i64),e.get("outer")?)?)?));kw30.push(("nominal_nose_spread_per_jaw_mm".into(),e.get("spread")?));kw30.push(("clearance_spread_per_jaw_mm".into(),Val::Float(1.0f64)));kw30.push(("opposing_jaw_envelope_gap_mm".into(),binary("sub",binary("sub",e.get("PITCH")?,binary("mul",Val::Int(2i64),e.get("outer")?)?)?,Val::Float(2.0f64))?));kw30.push(("insertion_direction_world".into(),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(unary("neg",Val::Float(1.0f64))?);Val::list(s)}));kw30.push(("print_up_world".into(),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));Val::list(s)}));kw30.push(("print_basis".into(),Val::Str("Lid flat underside on bed; C2 mouths grow upward, matching the floor-rooted trial orientation.".into())));kw30.push(("spring_basis".into(),Val::Str("Accepted C2 bore6.35, wing2.4 and tip125.421 degrees; no load or lifetime claim.".into())));fun31.call(args29,kw30)?});
Ok(Val::None)})})?;
    // clips
    e.set("clips", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun43 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args41 = Vec::new();
                let mut kw42 = Vec::new();
                args41.push(Val::Int(0i64));
                args41.push({
                    let fun46 = e.get("str")?;
                    let mut args44 = Vec::new();
                    let mut kw45 = Vec::new();
                    args44.push(binary(
                        "truediv",
                        {
                            let fun49 = {
                                let fun52 = e.get("Path")?;
                                let mut args50 = Vec::new();
                                let mut kw51 = Vec::new();
                                args50.push(e.get("__file__")?);
                                fun52.call(args50, kw51)?
                            }
                            .attr("resolve")?;
                            let mut args47 = Vec::new();
                            let mut kw48 = Vec::new();
                            fun49.call(args47, kw48)?
                        }
                        .attr("parents")?
                        .get(Val::Int(1i64))?,
                        Val::Str("cadlib".into()),
                    )?);
                    fun46.call(args44, kw45)?
                });
                fun43.call(args41, kw42)?
            };
            let mod53 = rt.import_module("route_snap")?;
            e.set("tube_clip", rt.member("route_snap", "tube_clip")?)?;
            return Ok({
                let fun56 = e.get("tuple")?;
                let mut args54 = Vec::new();
                let mut kw55 = Vec::new();
                args54.push({
                    let e = e.child();
                    let out57 = Val::list(vec![]);
                    for item58 in {
                        let fun61 = e.get("specification")?;
                        let mut args59 = Vec::new();
                        let mut kw60 = Vec::new();
                        fun61.call(args59, kw60)?
                    }
                    .get(Val::Str("tube_centers_world_mm".into()))?
                    .iter()?
                    {
                        e.set("point", item58)?;
                        out57.attr("append")?.call(
                            vec![{
                                let fun64 = e.get("tube_clip")?;
                                let mut args62 = Vec::new();
                                let mut kw63 = Vec::new();
                                args62.push(e.get("point")?);
                                args62.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Float(0.0f64));
                                    s.push(Val::Float(1.0f64));
                                    s.push(Val::Float(0.0f64));
                                    Val::tuple(s)
                                });
                                args62.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Float(0.0f64));
                                    s.push(Val::Float(0.0f64));
                                    s.push(Val::Float(1.0f64));
                                    Val::tuple(s)
                                });
                                args62.push(binary(
                                    "sub",
                                    e.get("CENTRE")?.get(Val::Int(2i64))?,
                                    e.get("LID_FACE")?,
                                )?);
                                kw63.push(("tube_od".into(), e.get("TUBE_OD")?));
                                kw63.push(("bore_diameter".into(), e.get("BORE")?));
                                kw63.push(("wing".into(), e.get("WING")?));
                                kw63.push(("span".into(), e.get("SPAN")?));
                                kw63.push(("tip_degrees".into(), e.get("TIP_DEGREES")?));
                                kw63.push(("print_up".into(), {
                                    let mut s = Vec::new();
                                    s.push(Val::Float(0.0f64));
                                    s.push(Val::Float(0.0f64));
                                    s.push(Val::Float(1.0f64));
                                    Val::tuple(s)
                                }));
                                fun64.call(args62, kw63)?
                            }],
                            vec![],
                        )?;
                    }
                    out57
                });
                fun56.call(args54, kw55)?
            });
            Ok(Val::None)
        })
    })?;
    // base
    e.set("base", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned65 = {
                let fun68 = e.get("specification")?;
                let mut args66 = Vec::new();
                let mut kw67 = Vec::new();
                fun68.call(args66, kw67)?
            };
            e.set("s", assigned65.clone())?;
            let assigned69 = e.get("s")?.get(Val::Str("base_bounds_mm".into()))?;
            let unpack70 = unpack(assigned69.clone(), 2)?;
            e.set("lo", unpack70[0].clone())?;
            e.set("hi", unpack70[1].clone())?;
            let assigned71 = {
                let fun74 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args72 = Vec::new();
                let mut kw73 = Vec::new();
                args72.extend(
                    {
                        let e = e.child();
                        let out75 = Val::list(vec![]);
                        for item76 in {
                            let fun79 = e.get("zip")?;
                            let mut args77 = Vec::new();
                            let mut kw78 = Vec::new();
                            args77.push(e.get("lo")?);
                            args77.push(e.get("hi")?);
                            fun79.call(args77, kw78)?
                        }
                        .iter()?
                        {
                            let unpack80 = unpack(item76, 2)?;
                            e.set("a", unpack80[0].clone())?;
                            e.set("b", unpack80[1].clone())?;
                            out75
                                .attr("append")?
                                .call(vec![binary("sub", e.get("b")?, e.get("a")?)?], vec![])?;
                        }
                        out75
                    }
                    .iter()?,
                );
                args72.push({
                    let fun83 = e.get("cq")?.attr("Vector")?;
                    let mut args81 = Vec::new();
                    let mut kw82 = Vec::new();
                    args81.extend(e.get("lo")?.iter()?);
                    fun83.call(args81, kw82)?
                });
                fun74.call(args72, kw73)?
            };
            e.set("stock", assigned71.clone())?;
            let assigned84 = {
                let fun87 = e.get("clips")?;
                let mut args85 = Vec::new();
                let mut kw86 = Vec::new();
                fun87.call(args85, kw86)?
            };
            let unpack88 = unpack(assigned84.clone(), 2)?;
            e.set("first", unpack88[0].clone())?;
            e.set("second", unpack88[1].clone())?;
            let assigned89 = {
                let fun92 = e.get("stock")?.attr("fuse")?;
                let mut args90 = Vec::new();
                let mut kw91 = Vec::new();
                args90.push(e.get("first")?);
                args90.push(e.get("second")?);
                fun92.call(args90, kw91)?
            };
            e.set("body", assigned89.clone())?;
            for item93 in e
                .get("s")?
                .get(Val::Str("tube_centers_world_mm".into()))?
                .iter()?
            {
                let unpack108 = unpack(item93, 3)?;
                e.set("x", unpack108[0].clone())?;
                e.set("y", unpack108[1].clone())?;
                e.set("z", unpack108[2].clone())?;
                let assigned94 = {
                    let fun97 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                    let mut args95 = Vec::new();
                    let mut kw96 = Vec::new();
                    args95.push(binary("truediv", e.get("BORE")?, Val::Int(2i64))?);
                    args95.push(binary("add", e.get("SPAN")?, Val::Float(0.2f64))?);
                    args95.push({
                        let fun100 = e.get("cq")?.attr("Vector")?;
                        let mut args98 = Vec::new();
                        let mut kw99 = Vec::new();
                        args98.push(e.get("x")?);
                        args98.push(binary(
                            "sub",
                            binary(
                                "sub",
                                e.get("y")?,
                                binary("truediv", e.get("SPAN")?, Val::Int(2i64))?,
                            )?,
                            Val::Float(0.1f64),
                        )?);
                        args98.push(e.get("z")?);
                        fun100.call(args98, kw99)?
                    });
                    args95.push({
                        let fun103 = e.get("cq")?.attr("Vector")?;
                        let mut args101 = Vec::new();
                        let mut kw102 = Vec::new();
                        args101.push(Val::Float(0.0f64));
                        args101.push(Val::Float(1.0f64));
                        args101.push(Val::Float(0.0f64));
                        fun103.call(args101, kw102)?
                    });
                    fun97.call(args95, kw96)?
                };
                e.set("bore", assigned94.clone())?;
                let assigned104 = {
                    let fun107 = e.get("body")?.attr("cut")?;
                    let mut args105 = Vec::new();
                    let mut kw106 = Vec::new();
                    args105.push(e.get("bore")?);
                    fun107.call(args105, kw106)?
                };
                e.set("body", assigned104.clone())?;
            }
            return Ok({
                let fun111 = e.get("body")?.attr("clean")?;
                let mut args109 = Vec::new();
                let mut kw110 = Vec::new();
                fun111.call(args109, kw110)?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
