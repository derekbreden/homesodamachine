//! Reference curved grip receiver and flat-wing cover geometry.
//!
//! The recorded coupon and cover trials use these reliefs, slots and placement.
//! The production enclosure has integral exposed handholds.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod1 = rt.import_module("overhang_round")?;
    e.set("transition", rt.member("overhang_round", "transition")?)?;
    e.set("GripInterface.__init__", {
        let params = vec![
            ("self".into(), None, false),
            ("shell".into(), None, false),
            ("floor_z".into(), Some(Val::Float(0.0f64)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned2 = e.get("shell")?;
            e.get("self")?.setattr("shell", assigned2.clone())?;
            let assigned3 = e.get("self")?.attr("shell")?.attr("fits")?.attr("slip")?;
            e.get("self")?.setattr("BODY_AIR", assigned3.clone())?;
            let assigned4 = binary(
                "sub",
                e.get("self")?.attr("shell")?.attr("handhold_length")?,
                binary("mul", Val::Int(2i64), e.get("self")?.attr("BODY_AIR")?)?,
            )?;
            e.get("self")?.setattr("LENGTH", assigned4.clone())?;
            let assigned5 = binary(
                "truediv",
                e.get("self")?.attr("shell")?.attr("appliance_width")?,
                Val::Int(2i64),
            )?;
            e.get("self")?.setattr("X_EXT", assigned5.clone())?;
            let assigned6 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                    line!(),
                );
                {
                    let fun9 = e.get("self")?.attr("shell")?.attr("_band_x")?;
                    let mut args7 = Vec::new();
                    let mut kw8 = Vec::new();
                    args7.push(e.get("self")?.attr("X_EXT")?);
                    args7.push(unary("neg", Val::Int(1i64))?);
                    fun9.call(args7, kw8)?
                }
            };
            let unpack10 = unpack(assigned6.clone(), 2)?;
            e.set("_flank", unpack10[0].clone())?;
            e.set("_cap", unpack10[1].clone())?;
            let assigned11 = binary(
                "add",
                e.get("_cap")?,
                e.get("self")?.attr("shell")?.attr("handhold_wall")?,
            )?;
            e.get("self")?.setattr("INNER_FACE", assigned11.clone())?;
            let assigned12 = binary(
                "sub",
                e.get("self")?.attr("X_EXT")?,
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                        line!(),
                    );
                    {
                        let fun15 = e.get("transition")?;
                        let mut args13 = Vec::new();
                        let mut kw14 = Vec::new();
                        args13.push(e.get("self")?.attr("shell")?.attr("handhold_edge_r")?);
                        fun15.call(args13, kw14)?
                    }
                }
                .get(Val::Int(1i64))?,
            )?;
            e.get("self")?.setattr("OUTER_FLAT", assigned12.clone())?;
            let assigned16 = binary(
                "sub",
                binary(
                    "sub",
                    e.get("self")?.attr("OUTER_FLAT")?,
                    e.get("self")?.attr("INNER_FACE")?,
                )?,
                e.get("self")?.attr("BODY_AIR")?,
            )?;
            e.get("self")?.setattr("WIDTH", assigned16.clone())?;
            let assigned17 = binary(
                "truediv",
                binary(
                    "add",
                    binary(
                        "add",
                        e.get("self")?.attr("OUTER_FLAT")?,
                        e.get("self")?.attr("INNER_FACE")?,
                    )?,
                    e.get("self")?.attr("BODY_AIR")?,
                )?,
                Val::Int(2i64),
            )?;
            e.get("self")?.setattr("X_CENTER", assigned17.clone())?;
            let assigned18 = binary(
                "add",
                binary(
                    "add",
                    binary(
                        "sub",
                        e.get("floor_z")?,
                        e.get("self")?.attr("shell")?.attr("floor_t")?,
                    )?,
                    e.get("self")?.attr("shell")?.attr("handhold_height")?,
                )?,
                e.get("self")?
                    .attr("shell")?
                    .attr("fits")?
                    .attr("supported_surface")?,
            )?;
            e.get("self")?.setattr("ROOF", assigned18.clone())?;
            let assigned19 = binary(
                "add",
                e.get("self")?.attr("ROOF")?,
                e.get("self")?.attr("shell")?.attr("handhold_roof")?,
            )?;
            e.get("self")?.setattr("CROWN", assigned19.clone())?;
            let assigned20 = Val::Float(3.36f64);
            e.get("self")?.setattr("THICK", assigned20.clone())?;
            let assigned21 = Val::Float(1.68f64);
            e.get("self")?.setattr("WING_THICK", assigned21.clone())?;
            let assigned22 = Val::Float(2.4f64);
            e.get("self")?.setattr("WING_REACH", assigned22.clone())?;
            let assigned23 = Val::Float(5.0f64);
            e.get("self")?.setattr("WING_SPAN", assigned23.clone())?;
            let assigned24 = Val::Float(0.6f64);
            e.get("self")?.setattr("WING_END_R", assigned24.clone())?;
            let assigned25 = Val::Float(0.6f64);
            e.get("self")?.setattr("CORNER_R", assigned25.clone())?;
            let assigned26 = Val::Float(0.6f64);
            e.get("self")?.setattr("TOUCH_R", assigned26.clone())?;
            let assigned27 = e.get("self")?.attr("shell")?.attr("fits")?.attr("slip")?;
            e.get("self")?.setattr("WING_END_AIR", assigned27.clone())?;
            let assigned28 = Val::Float(0.45f64);
            e.get("self")?.setattr("BEARING_AIR", assigned28.clone())?;
            let assigned29 = e
                .get("self")?
                .attr("shell")?
                .attr("fits")?
                .attr("supported_surface")?;
            e.get("self")?.setattr("BACK_AIR", assigned29.clone())?;
            let assigned30 = Val::Float(1.1f64);
            e.get("self")?.setattr("ENTRY_WIDTH", assigned30.clone())?;
            let assigned31 = Val::Float(0.4f64);
            e.get("self")?.setattr("ENTRY_DEPTH", assigned31.clone())?;
            let assigned32 = binary(
                "sub",
                e.get("self")?.attr("ROOF")?,
                e.get("self")?.attr("BACK_AIR")?,
            )?;
            e.get("self")?.setattr("BACK", assigned32.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("GripInterface.box", {
        let params = vec![
            ("self".into(), None, false),
            ("x0".into(), None, false),
            ("x1".into(), None, false),
            ("y0".into(), None, false),
            ("y1".into(), None, false),
            ("z0".into(), None, false),
            ("z1".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                    line!(),
                );
                {
                    let fun35 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                    let mut args33 = Vec::new();
                    let mut kw34 = Vec::new();
                    args33.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                    args33.push(binary("sub", e.get("y1")?, e.get("y0")?)?);
                    args33.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                    args33.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                            line!(),
                        );
                        {
                            let fun38 = e.get("cq")?.attr("Vector")?;
                            let mut args36 = Vec::new();
                            let mut kw37 = Vec::new();
                            args36.push(e.get("x0")?);
                            args36.push(e.get("y0")?);
                            args36.push(e.get("z0")?);
                            fun38.call(args36, kw37)?
                        }
                    });
                    fun35.call(args33, kw34)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("GripInterface.rounded",{let params=vec![("self".into(),None,false),("width".into(),None,false),("height".into(),None,false),("z0".into(),None,false),("z1".into(),None,false),("radius".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun41={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun44={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun47={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun50={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun53={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun56={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun59=e.get("cq")?.attr("Workplane")?;let mut args57=Vec::new();let mut kw58=Vec::new();args57.push(Val::Str("XY".into()));fun59.call(args57,kw58)?}}.attr("workplane")?;let mut args54=Vec::new();let mut kw55=Vec::new();kw55.push(("offset".into(),e.get("z0")?));fun56.call(args54,kw55)?}}.attr("rect")?;let mut args51=Vec::new();let mut kw52=Vec::new();args51.push(e.get("width")?);args51.push(e.get("height")?);fun53.call(args51,kw52)?}}.attr("extrude")?;let mut args48=Vec::new();let mut kw49=Vec::new();args48.push(binary("sub",e.get("z1")?,e.get("z0")?)?);fun50.call(args48,kw49)?}}.attr("edges")?;let mut args45=Vec::new();let mut kw46=Vec::new();args45.push(Val::Str("|Z".into()));fun47.call(args45,kw46)?}}.attr("fillet")?;let mut args42=Vec::new();let mut kw43=Vec::new();args42.push(e.get("radius")?);fun44.call(args42,kw43)?}}.attr("val")?;let mut args39=Vec::new();let mut kw40=Vec::new();fun41.call(args39,kw40)?}});
Ok(Val::None)})})?;
    e.set("GripInterface.wing", {
        let params = vec![("self".into(), None, false), ("end".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                    line!(),
                );
                {
                    let fun62 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                            line!(),
                        );
                        {
                            let fun65 = e.get("self")?.attr("rounded")?;
                            let mut args63 = Vec::new();
                            let mut kw64 = Vec::new();
                            args63.push(binary(
                                "add",
                                e.get("self")?.attr("WING_REACH")?,
                                Val::Int(1i64),
                            )?);
                            args63.push(e.get("self")?.attr("WING_SPAN")?);
                            args63.push(Val::Int(0i64));
                            args63.push(e.get("self")?.attr("WING_THICK")?);
                            args63.push(e.get("self")?.attr("WING_END_R")?);
                            fun65.call(args63, kw64)?
                        }
                    }
                    .attr("translate")?;
                    let mut args60 = Vec::new();
                    let mut kw61 = Vec::new();
                    args60.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "mul",
                            e.get("end")?,
                            binary(
                                "add",
                                binary("truediv", e.get("self")?.attr("LENGTH")?, Val::Int(2i64))?,
                                binary(
                                    "truediv",
                                    binary(
                                        "sub",
                                        e.get("self")?.attr("WING_REACH")?,
                                        Val::Int(1i64),
                                    )?,
                                    Val::Int(2i64),
                                )?,
                            )?,
                        )?);
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    fun62.call(args60, kw61)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("GripInterface.cover",{let params=vec![("self".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned66={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun69=e.get("self")?.attr("rounded")?;let mut args67=Vec::new();let mut kw68=Vec::new();args67.push(e.get("self")?.attr("LENGTH")?);args67.push(e.get("self")?.attr("WIDTH")?);args67.push(Val::Int(0i64));args67.push(e.get("self")?.attr("THICK")?);args67.push(e.get("self")?.attr("CORNER_R")?);fun69.call(args67,kw68)?}};e.set("body",assigned66.clone())?;
let assigned70={let e=e.child();let out71=Val::list(vec![]);for item72 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun75=e.get("body")?.attr("Edges")?;let mut args73=Vec::new();let mut kw74=Vec::new();fun75.call(args73,kw74)?}}.iter()? {e.set("e",item72)?;if {let v82={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun78=e.get("abs")?;let mut args76=Vec::new();let mut kw77=Vec::new();args76.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun81=e.get("e")?.attr("BoundingBox")?;let mut args79=Vec::new();let mut kw80=Vec::new();fun81.call(args79,kw80)?}}.attr("zmin")?,e.get("self")?.attr("THICK")?)?);fun78.call(args76,kw77)?}};let v83=Val::Float(1e-06f64);Val::Bool(compare("lt",v82.clone(),v83.clone())?.truthy()?)}.truthy()? {out71.attr("append")?.call(vec![e.get("e")?],vec![])?;}}out71};e.set("edges",assigned70.clone())?;
let assigned84={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun87=e.get("body")?.attr("fillet")?;let mut args85=Vec::new();let mut kw86=Vec::new();args85.push(e.get("self")?.attr("TOUCH_R")?);args85.push(e.get("edges")?);fun87.call(args85,kw86)?}};e.set("body",assigned84.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun90={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun93=e.get("body")?.attr("fuse")?;let mut args91=Vec::new();let mut kw92=Vec::new();args91.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun96=e.get("self")?.attr("wing")?;let mut args94=Vec::new();let mut kw95=Vec::new();args94.push(unary("neg",Val::Int(1i64))?);fun96.call(args94,kw95)?}});args91.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun99=e.get("self")?.attr("wing")?;let mut args97=Vec::new();let mut kw98=Vec::new();args97.push(Val::Int(1i64));fun99.call(args97,kw98)?}});fun93.call(args91,kw92)?}}.attr("clean")?;let mut args88=Vec::new();let mut kw89=Vec::new();fun90.call(args88,kw89)?}});
Ok(Val::None)})})?;
    e.set("GripInterface.placed", {
        let params = vec![
            ("self".into(), None, false),
            ("shape".into(), None, false),
            ("side".into(), Some(Val::Int(1i64)), false),
            ("drop".into(), Some(Val::Int(0i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned100 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                    line!(),
                );
                {
                    let fun103 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                            line!(),
                        );
                        {
                            let fun106 = e.get("shape")?.attr("rotate")?;
                            let mut args104 = Vec::new();
                            let mut kw105 = Vec::new();
                            args104.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                Val::tuple(s)
                            });
                            args104.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(1i64));
                                s.push(Val::Int(1i64));
                                s.push(Val::Int(0i64));
                                Val::tuple(s)
                            });
                            args104.push(Val::Int(180i64));
                            fun106.call(args104, kw105)?
                        }
                    }
                    .attr("translate")?;
                    let mut args101 = Vec::new();
                    let mut kw102 = Vec::new();
                    args101.push({
                        let mut s = Vec::new();
                        s.push(e.get("self")?.attr("X_CENTER")?);
                        s.push(e.get("self")?.attr("shell")?.attr("handhold_y")?);
                        s.push(binary("sub", e.get("self")?.attr("BACK")?, e.get("drop")?)?);
                        Val::tuple(s)
                    });
                    fun103.call(args101, kw102)?
                }
            };
            e.set("east", assigned100.clone())?;
            return Ok(
                if {
                    let v107 = e.get("side")?;
                    let v108 = Val::Int(1i64);
                    Val::Bool(compare("eq", v107.clone(), v108.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("east")?
                } else {
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                            line!(),
                        );
                        {
                            let fun111 = e.get("east")?.attr("mirror")?;
                            let mut args109 = Vec::new();
                            let mut kw110 = Vec::new();
                            args109.push(Val::Str("YZ".into()));
                            fun111.call(args109, kw110)?
                        }
                    }
                },
            );
            Ok(Val::None)
        })
    })?;
    e.set("GripInterface.receiver_reliefs", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned112 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("reliefs", assigned112.clone())?;
            let assigned113 = binary(
                "truediv",
                e.get("self")?.attr("shell")?.attr("handhold_length")?,
                Val::Int(2i64),
            )?;
            e.set("mouth", assigned113.clone())?;
            for item114 in {
                let mut s = Vec::new();
                s.push(unary("neg", Val::Int(1i64))?);
                s.push(Val::Int(1i64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("end", item114)?;
                let assigned115 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                        line!(),
                    );
                    {
                        let fun118 = e.get("sorted")?;
                        let mut args116 = Vec::new();
                        let mut kw117 = Vec::new();
                        args116.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "mul",
                                e.get("end")?,
                                binary(
                                    "sub",
                                    e.get("mouth")?,
                                    e.get("self")?.attr("shell")?.attr("handhold_corner_r")?,
                                )?,
                            )?);
                            s.push(binary("mul", e.get("end")?, e.get("mouth")?)?);
                            Val::tuple(s)
                        });
                        fun118.call(args116, kw117)?
                    }
                };
                let unpack119 = unpack(assigned115.clone(), 2)?;
                e.set("x0", unpack119[0].clone())?;
                e.set("x1", unpack119[1].clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                        line!(),
                    );
                    {
                        let fun122 = e.get("reliefs")?.attr("append")?;
                        let mut args120 = Vec::new();
                        let mut kw121 = Vec::new();
                        args120.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",
                                line!(),
                            );
                            {
                                let fun125 = e.get("self")?.attr("box")?;
                                let mut args123 = Vec::new();
                                let mut kw124 = Vec::new();
                                args123.push(e.get("x0")?);
                                args123.push(e.get("x1")?);
                                args123.push(binary(
                                    "sub",
                                    binary(
                                        "truediv",
                                        unary("neg", e.get("self")?.attr("WIDTH")?)?,
                                        Val::Int(2i64),
                                    )?,
                                    e.get("self")?.attr("BODY_AIR")?,
                                )?);
                                args123.push(binary(
                                    "add",
                                    binary(
                                        "sub",
                                        e.get("self")?.attr("X_EXT")?,
                                        e.get("self")?.attr("X_CENTER")?,
                                    )?,
                                    Val::Int(1i64),
                                )?);
                                args123.push(unary("neg", e.get("self")?.attr("BACK_AIR")?)?);
                                args123.push(binary(
                                    "add",
                                    binary(
                                        "sub",
                                        e.get("self")?.attr("shell")?.attr("handhold_corner_r")?,
                                        e.get("self")?.attr("BACK_AIR")?,
                                    )?,
                                    Val::Float(0.01f64),
                                )?);
                                fun125.call(args123, kw124)?
                            }
                        });
                        fun122.call(args120, kw121)?
                    }
                };
            }
            return Ok(e.get("reliefs")?);
            Ok(Val::None)
        })
    })?;
    e.set("GripInterface.receiver_slots",{let params=vec![("self".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned126={let mut s=Vec::new();Val::list(s)};e.set("slots",assigned126.clone())?;
for item127 in {let mut s=Vec::new();s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Int(1i64));Val::tuple(s)}.iter()? {
e.set("end",item127)?;let assigned128=binary("truediv",e.get("self")?.attr("shell")?.attr("handhold_length")?,Val::Int(2i64))?;e.set("mouth",assigned128.clone())?;
let assigned129={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun132=e.get("sorted")?;let mut args130=Vec::new();let mut kw131=Vec::new();args130.push({let mut s=Vec::new();s.push(binary("mul",e.get("end")?,binary("sub",binary("truediv",e.get("self")?.attr("LENGTH")?,Val::Int(2i64))?,Val::Float(0.1f64))?)?);s.push(binary("mul",e.get("end")?,binary("add",binary("add",e.get("mouth")?,e.get("self")?.attr("shell")?.attr("handhold_wall")?)?,Val::Float(0.1f64))?)?);Val::tuple(s)});fun132.call(args130,kw131)?}};let unpack133=unpack(assigned129.clone(),2)?;e.set("x0",unpack133[0].clone())?;e.set("x1",unpack133[1].clone())?;
let assigned134={let mut s=Vec::new();s.push(binary("sub",binary("truediv",unary("neg",e.get("self")?.attr("WING_SPAN")?)?,Val::Int(2i64))?,e.get("self")?.attr("WING_END_AIR")?)?);s.push(binary("add",binary("truediv",e.get("self")?.attr("WING_SPAN")?,Val::Int(2i64))?,e.get("self")?.attr("WING_END_AIR")?)?);Val::tuple(s)};let unpack135=unpack(assigned134.clone(),2)?;e.set("y0",unpack135[0].clone())?;e.set("y1",unpack135[1].clone())?;
let assigned136=binary("add",e.get("self")?.attr("WING_THICK")?,e.get("self")?.attr("BEARING_AIR")?)?;e.set("roof",assigned136.clone())?;
let assigned137={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun140=e.get("self")?.attr("box")?;let mut args138=Vec::new();let mut kw139=Vec::new();args138.push(e.get("x0")?);args138.push(e.get("x1")?);args138.push(e.get("y0")?);args138.push(e.get("y1")?);args138.push(unary("neg",e.get("self")?.attr("BACK_AIR")?)?);args138.push(e.get("roof")?);fun140.call(args138,kw139)?}};e.set("slot",assigned137.clone())?;
let assigned141={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun144={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun147={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun150={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun153={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun156=e.get("cq")?.attr("Workplane")?;let mut args154=Vec::new();let mut kw155=Vec::new();args154.push(Val::Str("XZ".into()));kw155.push(("origin".into(),{let mut s=Vec::new();s.push(Val::Int(0i64));s.push(e.get("y1")?);s.push(Val::Int(0i64));Val::tuple(s)}));fun156.call(args154,kw155)?}}.attr("polyline")?;let mut args151=Vec::new();let mut kw152=Vec::new();args151.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("mul",e.get("end")?,e.get("mouth")?)?);s.push(e.get("roof")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("mul",e.get("end")?,binary("add",e.get("mouth")?,e.get("self")?.attr("ENTRY_WIDTH")?)?)?);s.push(e.get("roof")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("mul",e.get("end")?,e.get("mouth")?)?);s.push(binary("add",e.get("roof")?,e.get("self")?.attr("ENTRY_DEPTH")?)?);Val::tuple(s)});Val::list(s)});fun153.call(args151,kw152)?}}.attr("close")?;let mut args148=Vec::new();let mut kw149=Vec::new();fun150.call(args148,kw149)?}}.attr("extrude")?;let mut args145=Vec::new();let mut kw146=Vec::new();args145.push(binary("sub",e.get("y1")?,e.get("y0")?)?);fun147.call(args145,kw146)?}}.attr("val")?;let mut args142=Vec::new();let mut kw143=Vec::new();fun144.call(args142,kw143)?}};e.set("lead",assigned141.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun159=e.get("slots")?.attr("append")?;let mut args157=Vec::new();let mut kw158=Vec::new();args157.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun162=e.get("slot")?.attr("fuse")?;let mut args160=Vec::new();let mut kw161=Vec::new();args160.push(e.get("lead")?);fun162.call(args160,kw161)?}});fun159.call(args157,kw158)?}};
}
return Ok(e.get("slots")?);
Ok(Val::None)})})?;
    e.set("GripInterface.apply_receiver",{let params=vec![("self".into(),None,false),("solid".into(),None,false),("piece".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let v163=e.get("piece")?;let v164={let mut s=Vec::new();s.push(Val::Str("front".into()));s.push(Val::Str("back".into()));Val::tuple(s)};Val::Bool(compare("not_in",v163.clone(),v164.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun167=e.get("ValueError")?;let mut args165=Vec::new();let mut kw166=Vec::new();args165.push(e.get("piece")?);fun167.call(args165,kw166)?}})?);
}
let assigned168=if {let v169=e.get("piece")?;let v170=Val::Str("front".into());Val::Bool(compare("eq",v169.clone(),v170.clone())?.truthy()?)}.truthy()? {Val::Int(0i64)} else {Val::Int(1i64)};e.set("end_index",assigned168.clone())?;
let assigned171={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun174=e.get("self")?.attr("receiver_reliefs")?;let mut args172=Vec::new();let mut kw173=Vec::new();fun174.call(args172,kw173)?}}.get(e.get("end_index")?)?;e.set("relief",assigned171.clone())?;
let assigned175={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun178=e.get("self")?.attr("receiver_slots")?;let mut args176=Vec::new();let mut kw177=Vec::new();fun178.call(args176,kw177)?}}.get(e.get("end_index")?)?;e.set("slot",assigned175.clone())?;
for item179 in {let mut s=Vec::new();s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Int(1i64));Val::tuple(s)}.iter()? {
e.set("side",item179)?;let assigned180={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun183={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun186={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun189=e.get("solid")?.attr("cut")?;let mut args187=Vec::new();let mut kw188=Vec::new();args187.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun192=e.get("self")?.attr("placed")?;let mut args190=Vec::new();let mut kw191=Vec::new();args190.push(e.get("relief")?);args190.push(e.get("side")?);fun192.call(args190,kw191)?}});fun189.call(args187,kw188)?}}.attr("cut")?;let mut args184=Vec::new();let mut kw185=Vec::new();args184.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_grip_interface.rs",line!());{let fun195=e.get("self")?.attr("placed")?;let mut args193=Vec::new();let mut kw194=Vec::new();args193.push(e.get("slot")?);args193.push(e.get("side")?);fun195.call(args193,kw194)?}});fun186.call(args184,kw185)?}}.attr("clean")?;let mut args181=Vec::new();let mut kw182=Vec::new();fun183.call(args181,kw182)?}};e.set("solid",assigned180.clone())?;
}
return Ok(e.get("solid")?);
Ok(Val::None)})})?;
    e.set(
        "GripInterface",
        rt.python_type("_grip_interface", "GripInterface")?,
    )?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
