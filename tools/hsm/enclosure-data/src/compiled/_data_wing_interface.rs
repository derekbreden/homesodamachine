//! DATA is the accepted nameplate construction with a narrower, wing-thick face.
//!
//! The centred jack opening is cut through the continuous plate. Broad wings and
//! matching receiving slots use the nameplate geometry and its seating datum.
//! Y=0 is the flat print-bed back; +Y is the customer-facing direction.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("collections")?;
    e.set("namedtuple", rt.member("collections", "namedtuple")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("nameplate", rt.import_module("_nameplate_wing_interface")?)?;
    e.set("port_chip", rt.import_module("port_chip")?)?;
    let mod2 = rt.import_module("_enclosure_data")?;
    e.set("_dimensions", rt.member("_enclosure_data", "dimensions")?)?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                    line!(),
                );
                {
                    let fun8 = e.get("globals")?;
                    let mut args6 = Vec::new();
                    let mut kw7 = Vec::new();
                    fun8.call(args6, kw7)?
                }
            }
            .attr("update")?;
            let mut args3 = Vec::new();
            let mut kw4 = Vec::new();
            args3.push(
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                        line!(),
                    );
                    {
                        let fun11 = e.get("_dimensions")?;
                        let mut args9 = Vec::new();
                        let mut kw10 = Vec::new();
                        fun11.call(args9, kw10)?
                    }
                }
                .get(Val::Str("data".into()))?,
            );
            fun5.call(args3, kw4)?
        }
    };
    let assigned12 = e.get("nameplate")?.attr("box")?;
    e.set("box", assigned12.clone())?;
    let assigned13 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
            line!(),
        );
        {
            let fun16 = e.get("namedtuple")?;
            let mut args14 = Vec::new();
            let mut kw15 = Vec::new();
            args14.push(Val::Str("Station".into()));
            args14.push(Val::Str("x z".into()));
            kw15.push(("module".into(), Val::Str("_data_wing_interface".into())));
            fun16.call(args14, kw15)?
        }
    };
    e.set("Station", assigned13.clone())?;
    // jack_face_y
    e.set("jack_face_y", {
        let params = vec![("y_outer".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                    line!(),
                );
                {
                    let fun19 = e.get("_read")?;
                    let mut args17 = Vec::new();
                    let mut kw18 = Vec::new();
                    args17.push(Val::Str("data-jack-face".into()));
                    kw18.push((
                        "data".into(),
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                                line!(),
                            );
                            {
                                let fun22 = e.get("_dimensions")?;
                                let mut args20 = Vec::new();
                                let mut kw21 = Vec::new();
                                fun22.call(args20, kw21)?
                            }
                        }
                        .get(Val::Str("data".into()))?,
                    ));
                    kw18.push(("y_outer".into(), e.get("y_outer")?));
                    fun19.call(args17, kw18)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // pad_runout
    e.set("pad_runout",{let params=vec![("station".into(),None,false),("y_outer".into(),None,false),("up".into(),Some(unary("neg",Val::Int(1i64))?),true)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun25=e.get("tuple")?;let mut args23=Vec::new();let mut kw24=Vec::new();args23.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun28=e.get("_read")?;let mut args26=Vec::new();let mut kw27=Vec::new();args26.push(Val::Str("data-pad-runout".into()));kw27.push(("data".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun31=e.get("_dimensions")?;let mut args29=Vec::new();let mut kw30=Vec::new();fun31.call(args29,kw30)?}}.get(Val::Str("data".into()))?));kw27.push(("nameplate".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun34=e.get("_dimensions")?;let mut args32=Vec::new();let mut kw33=Vec::new();fun34.call(args32,kw33)?}}.get(Val::Str("nameplate".into()))?));kw27.push(("z".into(),e.get("station")?.get(Val::Int(1i64))?));kw27.push(("y_outer".into(),e.get("y_outer")?));kw27.push(("up".into(),e.get("up")?));fun28.call(args26,kw27)?}});fun25.call(args23,kw24)?}});
Ok(Val::None)})})?;
    // aperture
    e.set("aperture",{let params=vec![("y0".into(),None,false),("y1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun37={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun40={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun43={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun46={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun49={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun52={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun55={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",line!());{let fun58=e.get("cq")?.attr("Workplane")?;let mut args56=Vec::new();let mut kw57=Vec::new();args56.push(Val::Str("XY".into()));fun58.call(args56,kw57)?}}.attr("rect")?;let mut args53=Vec::new();let mut kw54=Vec::new();args53.push(e.get("OPENING_W")?);args53.push(e.get("OPENING_H")?);fun55.call(args53,kw54)?}}.attr("extrude")?;let mut args50=Vec::new();let mut kw51=Vec::new();args50.push(binary("sub",e.get("y1")?,e.get("y0")?)?);fun52.call(args50,kw51)?}}.attr("edges")?;let mut args47=Vec::new();let mut kw48=Vec::new();args47.push(Val::Str("|Z".into()));fun49.call(args47,kw48)?}}.attr("fillet")?;let mut args44=Vec::new();let mut kw45=Vec::new();args44.push(e.get("OPENING_R")?);fun46.call(args44,kw45)?}}.attr("val")?;let mut args41=Vec::new();let mut kw42=Vec::new();fun43.call(args41,kw42)?}}.attr("rotate")?;let mut args38=Vec::new();let mut kw39=Vec::new();args38.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)});args38.push({let mut s=Vec::new();s.push(Val::Int(1i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)});args38.push(unary("neg",Val::Int(90i64))?);fun40.call(args38,kw39)?}}.attr("translate")?;let mut args35=Vec::new();let mut kw36=Vec::new();args35.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(e.get("y0")?);s.push(Val::Int(0i64));Val::tuple(s)});fun37.call(args35,kw36)?}});
Ok(Val::None)})})?;
    // blank
    e.set("blank", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned59 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                    line!(),
                );
                {
                    let fun62 = e.get("port_chip")?.attr("outline")?;
                    let mut args60 = Vec::new();
                    let mut kw61 = Vec::new();
                    args60.push(e.get("WIDTH")?);
                    args60.push(e.get("TOP")?);
                    args60.push(e.get("BOTTOM")?);
                    args60.push(e.get("THICK")?);
                    fun62.call(args60, kw61)?
                }
            };
            e.set("plate", assigned59.clone())?;
            let assigned63 = {
                let e = e.child();
                let out64 = Val::list(vec![]);
                for item65 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                        line!(),
                    );
                    {
                        let fun68 = e.get("nameplate")?.attr("wings")?;
                        let mut args66 = Vec::new();
                        let mut kw67 = Vec::new();
                        kw67.push(("width".into(), e.get("WIDTH")?));
                        kw67.push(("span".into(), e.get("WING_SPAN")?));
                        fun68.call(args66, kw67)?
                    }
                }
                .iter()?
                {
                    e.set("wing", item65)?;
                    out64.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                                line!(),
                            );
                            {
                                let fun71 = e.get("wing")?.attr("translate")?;
                                let mut args69 = Vec::new();
                                let mut kw70 = Vec::new();
                                args69.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Int(0i64));
                                    s.push(Val::Int(0i64));
                                    s.push(e.get("CENTER_Z")?);
                                    Val::tuple(s)
                                });
                                fun71.call(args69, kw70)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out64
            };
            e.set("wings", assigned63.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                    line!(),
                );
                {
                    let fun74 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                            line!(),
                        );
                        {
                            let fun77 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                                    line!(),
                                );
                                {
                                    let fun80 = e.get("plate")?.attr("fuse")?;
                                    let mut args78 = Vec::new();
                                    let mut kw79 = Vec::new();
                                    args78.extend(e.get("wings")?.iter()?);
                                    fun80.call(args78, kw79)?
                                }
                            }
                            .attr("cut")?;
                            let mut args75 = Vec::new();
                            let mut kw76 = Vec::new();
                            args75.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                                    line!(),
                                );
                                {
                                    let fun83 = e.get("aperture")?;
                                    let mut args81 = Vec::new();
                                    let mut kw82 = Vec::new();
                                    args81.push(unary("neg", Val::Float(0.01f64))?);
                                    args81.push(binary(
                                        "add",
                                        e.get("THICK")?,
                                        Val::Float(0.01f64),
                                    )?);
                                    fun83.call(args81, kw82)?
                                }
                            });
                            fun77.call(args75, kw76)?
                        }
                    }
                    .attr("clean")?;
                    let mut args72 = Vec::new();
                    let mut kw73 = Vec::new();
                    fun74.call(args72, kw73)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // apply
    e.set("apply", {
        let params = vec![
            ("solid".into(), None, false),
            ("station".into(), None, false),
            ("y_outer".into(), None, false),
            ("up".into(), Some(unary("neg", Val::Int(1i64))?), true),
            ("supported".into(), Some(e.get("SUPPORTED_AIR")?), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned84 = e.get("station")?;
            let unpack85 = unpack(assigned84.clone(), 2)?;
            e.set("x", unpack85[0].clone())?;
            e.set("z", unpack85[1].clone())?;
            let assigned86 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                    line!(),
                );
                {
                    let fun89 = e.get("nameplate")?.attr("apply")?;
                    let mut args87 = Vec::new();
                    let mut kw88 = Vec::new();
                    args87.push(e.get("solid")?);
                    args87.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                            line!(),
                        );
                        {
                            let fun92 = e.get("Station")?;
                            let mut args90 = Vec::new();
                            let mut kw91 = Vec::new();
                            args90.push(e.get("x")?);
                            args90.push(binary("add", e.get("z")?, e.get("CENTER_Z")?)?);
                            fun92.call(args90, kw91)?
                        }
                    });
                    args87.push(e.get("y_outer")?);
                    kw88.push(("up".into(), e.get("up")?));
                    kw88.push(("supported".into(), e.get("supported")?));
                    kw88.push(("width".into(), e.get("WIDTH")?));
                    kw88.push(("height".into(), e.get("HEIGHT")?));
                    kw88.push(("wing_span".into(), e.get("WING_SPAN")?));
                    kw88.push(("access".into(), Val::Bool(false)));
                    kw88.push((
                        "runout_lead".into(),
                        e.get("nameplate")?.attr("RUNOUT_LEAD")?,
                    ));
                    fun89.call(args87, kw88)?
                }
            };
            e.set("solid", assigned86.clone())?;
            let assigned93 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                    line!(),
                );
                {
                    let fun96 = e.get("port_chip")?.attr("outline")?;
                    let mut args94 = Vec::new();
                    let mut kw95 = Vec::new();
                    args94.push(binary(
                        "add",
                        e.get("WIDTH")?,
                        binary("mul", Val::Int(2i64), e.get("FACE_AIR")?)?,
                    )?);
                    args94.push(binary("add", e.get("TOP")?, e.get("FACE_AIR")?)?);
                    args94.push(binary("add", e.get("BOTTOM")?, e.get("FACE_AIR")?)?);
                    args94.push(binary(
                        "add",
                        binary("add", e.get("POCKET_DEPTH")?, Val::Int(1i64))?,
                        e.get("BACK_AIR")?,
                    )?);
                    kw95.push((
                        "radius".into(),
                        binary("add", e.get("CORNER_R")?, e.get("FACE_AIR")?)?,
                    ));
                    fun96.call(args94, kw95)?
                }
            };
            e.set("mouth", assigned93.clone())?;
            let assigned97 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                    line!(),
                );
                {
                    let fun100 = e.get("mouth")?.attr("fuse")?;
                    let mut args98 = Vec::new();
                    let mut kw99 = Vec::new();
                    args98.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                            line!(),
                        );
                        {
                            let fun103 = e.get("mouth")?.attr("translate")?;
                            let mut args101 = Vec::new();
                            let mut kw102 = Vec::new();
                            args101.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(binary("mul", e.get("up")?, e.get("supported")?)?);
                                Val::tuple(s)
                            });
                            fun103.call(args101, kw102)?
                        }
                    });
                    fun100.call(args98, kw99)?
                }
            };
            e.set("mouth", assigned97.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                    line!(),
                );
                {
                    let fun106 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                            line!(),
                        );
                        {
                            let fun109 = e.get("solid")?.attr("cut")?;
                            let mut args107 = Vec::new();
                            let mut kw108 = Vec::new();
                            args107.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                                    line!(),
                                );
                                {
                                    let fun112 = e.get("mouth")?.attr("translate")?;
                                    let mut args110 = Vec::new();
                                    let mut kw111 = Vec::new();
                                    args110.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("x")?);
                                        s.push(binary(
                                            "sub",
                                            binary(
                                                "sub",
                                                e.get("y_outer")?,
                                                e.get("POCKET_DEPTH")?,
                                            )?,
                                            e.get("BACK_AIR")?,
                                        )?);
                                        s.push(e.get("z")?);
                                        Val::tuple(s)
                                    });
                                    fun112.call(args110, kw111)?
                                }
                            });
                            fun109.call(args107, kw108)?
                        }
                    }
                    .attr("clean")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    fun106.call(args104, kw105)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // plain_lips
    e.set("plain_lips", {
        let params = vec![
            ("station".into(), None, false),
            ("y_outer".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned113 = e.get("station")?;
            let unpack114 = unpack(assigned113.clone(), 2)?;
            e.set("x", unpack114[0].clone())?;
            e.set("z", unpack114[1].clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                    line!(),
                );
                {
                    let fun117 = e.get("nameplate")?.attr("plain_lips")?;
                    let mut args115 = Vec::new();
                    let mut kw116 = Vec::new();
                    args115.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_data_wing_interface.rs",
                            line!(),
                        );
                        {
                            let fun120 = e.get("Station")?;
                            let mut args118 = Vec::new();
                            let mut kw119 = Vec::new();
                            args118.push(e.get("x")?);
                            args118.push(binary("add", e.get("z")?, e.get("CENTER_Z")?)?);
                            fun120.call(args118, kw119)?
                        }
                    });
                    args115.push(e.get("y_outer")?);
                    kw116.push(("width".into(), e.get("WIDTH")?));
                    kw116.push(("wing_span".into(), e.get("WING_SPAN")?));
                    fun117.call(args115, kw116)?
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
