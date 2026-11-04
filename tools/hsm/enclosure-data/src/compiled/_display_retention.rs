//! The display cover's two skirts and the slots and catches the housing holds them with.
//!
//! Coordinates follow the machine display: X across, Y up the screen, Z out of the face.
//!
//! EACH SKIRT IS THE NAMEPLATE'S SNAP TAB RUN BROAD. Its thickness, reach, square lip, land and
//! bearing slip are `_nameplate_interface`'s, and it runs `LENGTH` along the display instead of
//! the tab's width. The housing's side of it is the nameplate receiver's too: a slot with a flex
//! lane to one side, and under the catch nothing at all. The catch is the ceiling of the storey
//! cavity beside the display (`enclosure.display_storey_cavities`), one a side from the flex lane
//! out to the side wall, open into the pump bay.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("_tab", rt.import_module("_nameplate_interface")?)?;
    let mod1 = rt.import_module("_enclosure_interface")?;
    e.set(
        "display_inset_x",
        rt.member("_enclosure_interface", "display_inset_x")?,
    )?;
    e.set(
        "display_cover_slip",
        rt.member("_enclosure_interface", "display_cover_slip")?,
    )?;
    e.set(
        "display_cover_thickness",
        rt.member("_enclosure_interface", "display_cover_thickness")?,
    )?;
    let assigned2 = e.get("_tab")?.attr("TAB_THICK")?;
    e.set("WALL", assigned2.clone())?;
    let assigned3 = Val::Float(24.0f64);
    e.set("LENGTH", assigned3.clone())?;
    let assigned4 = e.get("_tab")?.attr("LIP")?;
    e.set("LIP", assigned4.clone())?;
    let assigned5 = e.get("_tab")?.attr("LIP_START")?;
    e.set("LIP_START", assigned5.clone())?;
    let assigned6 = e.get("_tab")?.attr("LIP_LAND")?;
    e.set("LIP_LAND", assigned6.clone())?;
    let assigned7 = e.get("_tab")?.attr("BEARING_SLIP")?;
    e.set("BEARING_SLIP", assigned7.clone())?;
    let assigned8 = e.get("_tab")?.attr("END_SLIP")?;
    e.set("END_SLIP", assigned8.clone())?;
    let assigned9 = e.get("display_cover_thickness")?;
    e.set("ROOT", assigned9.clone())?;
    let assigned10 = binary("add", e.get("ROOT")?, e.get("_tab")?.attr("TAB_LENGTH")?)?;
    e.set("DEPTH", assigned10.clone())?;
    let assigned11 = binary(
        "sub",
        binary("truediv", e.get("display_inset_x")?, Val::Float(2.0f64))?,
        e.get("display_cover_slip")?,
    )?;
    e.set("OUTER_X", assigned11.clone())?;
    let assigned12 = binary(
        "sub",
        binary("add", e.get("ROOT")?, e.get("LIP_START")?)?,
        e.get("BEARING_SLIP")?,
    )?;
    e.set("CATCH", assigned12.clone())?;
    let assigned13 = binary("add", e.get("OUTER_X")?, e.get("display_cover_slip")?)?;
    e.set("NECK_X", assigned13.clone())?;
    let assigned14 = binary(
        "sub",
        binary("sub", e.get("OUTER_X")?, e.get("WALL")?)?,
        e.get("LIP")?,
    )?;
    e.set("FLEX_X", assigned14.clone())?;
    let assigned15 = binary(
        "add",
        e.get("LENGTH")?,
        binary("mul", Val::Float(2.0f64), e.get("END_SLIP")?)?,
    )?;
    e.set("RUN", assigned15.clone())?;
    // _prism
    e.set("_prism",{let params=vec![("profile".into(),None,false),("length".into(),Some(e.get("LENGTH")?),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned16={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_retention.rs",line!());{let fun19=e.get("cq")?.attr("Wire")?.attr("makePolygon")?;let mut args17=Vec::new();let mut kw18=Vec::new();args17.push({let e=e.child();let out20=Val::list(vec![]);for item21 in {let mut s=Vec::new();s.extend(e.get("profile")?.iter()?);s.push(e.get("profile")?.get(Val::Int(0i64))?);Val::list(s)}.iter()? {let unpack22=unpack(item21,2)?;e.set("x",unpack22[0].clone())?;e.set("z",unpack22[1].clone())?;out20.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_retention.rs",line!());{let fun25=e.get("cq")?.attr("Vector")?;let mut args23=Vec::new();let mut kw24=Vec::new();args23.push(e.get("x")?);args23.push(binary("truediv",unary("neg",e.get("length")?)?,Val::Float(2.0f64))?);args23.push(e.get("z")?);fun25.call(args23,kw24)?}}],vec![])?;}out20});fun19.call(args17,kw18)?}};e.set("wire",assigned16.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_retention.rs",line!());{let fun28=e.get("cq")?.attr("Solid")?.attr("extrudeLinear")?;let mut args26=Vec::new();let mut kw27=Vec::new();args26.push(e.get("wire")?);args26.push({let mut s=Vec::new();Val::list(s)});args26.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_retention.rs",line!());{let fun31=e.get("cq")?.attr("Vector")?;let mut args29=Vec::new();let mut kw30=Vec::new();args29.push(Val::Int(0i64));args29.push(e.get("length")?);args29.push(Val::Int(0i64));fun31.call(args29,kw30)?}});fun28.call(args26,kw27)?}});
Ok(Val::None)})})?;
    // skirt
    e.set("skirt", {
        let params = vec![("side".into(), Some(Val::Int(1i64)), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned32 = {
                let mut s = Vec::new();
                s.push(e.get("OUTER_X")?);
                s.push(e.get("ROOT")?);
                Val::tuple(s)
            };
            let unpack33 = unpack(assigned32.clone(), 2)?;
            e.set("x", unpack33[0].clone())?;
            e.set("r", unpack33[1].clone())?;
            let assigned34 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, e.get("WALL")?)?);
                    s.push(unary("neg", e.get("r")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(unary("neg", e.get("r")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(binary(
                        "sub",
                        unary("neg", e.get("r")?)?,
                        e.get("LIP_START")?,
                    )?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("LIP")?)?);
                    s.push(binary(
                        "sub",
                        unary("neg", e.get("r")?)?,
                        e.get("LIP_START")?,
                    )?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("LIP")?)?);
                    s.push(binary(
                        "sub",
                        binary("sub", unary("neg", e.get("r")?)?, e.get("LIP_START")?)?,
                        e.get("LIP_LAND")?,
                    )?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(unary("neg", e.get("DEPTH")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, e.get("WALL")?)?);
                    s.push(unary("neg", e.get("DEPTH")?)?);
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("profile", assigned34.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_display_retention.rs",
                    line!(),
                );
                {
                    let fun37 = e.get("_prism")?;
                    let mut args35 = Vec::new();
                    let mut kw36 = Vec::new();
                    args35.push({
                        let e = e.child();
                        let out38 = Val::list(vec![]);
                        for item39 in e.get("profile")?.iter()? {
                            let unpack40 = unpack(item39, 2)?;
                            e.set("px", unpack40[0].clone())?;
                            e.set("z", unpack40[1].clone())?;
                            out38.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary("mul", e.get("side")?, e.get("px")?)?);
                                    s.push(e.get("z")?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                        out38
                    });
                    fun37.call(args35, kw36)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // pocket
    e.set("pocket", {
        let params = vec![("side".into(), Some(Val::Int(1i64)), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned41 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_display_retention.rs",
                    line!(),
                );
                {
                    let fun44 = e.get("_prism")?;
                    let mut args42 = Vec::new();
                    let mut kw43 = Vec::new();
                    args42.push({
                        let e = e.child();
                        let out45 = Val::list(vec![]);
                        for item46 in {
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("FLEX_X")?);
                                s.push(Val::Float(1.0f64));
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("NECK_X")?);
                                s.push(Val::Float(1.0f64));
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("NECK_X")?);
                                s.push(unary("neg", e.get("CATCH")?)?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("FLEX_X")?);
                                s.push(unary("neg", e.get("CATCH")?)?);
                                Val::tuple(s)
                            });
                            Val::list(s)
                        }
                        .iter()?
                        {
                            let unpack47 = unpack(item46, 2)?;
                            e.set("px", unpack47[0].clone())?;
                            e.set("z", unpack47[1].clone())?;
                            out45.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary("mul", e.get("side")?, e.get("px")?)?);
                                    s.push(e.get("z")?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                        out45
                    });
                    args42.push(e.get("RUN")?);
                    fun44.call(args42, kw43)?
                }
            };
            e.set("slot", assigned41.clone())?;
            let assigned48 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_display_retention.rs",
                    line!(),
                );
                {
                    let fun51 = e.get("_prism")?;
                    let mut args49 = Vec::new();
                    let mut kw50 = Vec::new();
                    args49.push({
                        let e = e.child();
                        let out52 = Val::list(vec![]);
                        for item53 in {
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("FLEX_X")?);
                                s.push(unary("neg", e.get("CATCH")?)?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary(
                                    "add",
                                    e.get("OUTER_X")?,
                                    binary("mul", Val::Float(2.0f64), e.get("LIP")?)?,
                                )?);
                                s.push(unary("neg", e.get("CATCH")?)?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary(
                                    "add",
                                    e.get("OUTER_X")?,
                                    binary("mul", Val::Float(2.0f64), e.get("LIP")?)?,
                                )?);
                                s.push(binary(
                                    "sub",
                                    unary("neg", e.get("DEPTH")?)?,
                                    e.get("END_SLIP")?,
                                )?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("FLEX_X")?);
                                s.push(binary(
                                    "sub",
                                    unary("neg", e.get("DEPTH")?)?,
                                    e.get("END_SLIP")?,
                                )?);
                                Val::tuple(s)
                            });
                            Val::list(s)
                        }
                        .iter()?
                        {
                            let unpack54 = unpack(item53, 2)?;
                            e.set("px", unpack54[0].clone())?;
                            e.set("z", unpack54[1].clone())?;
                            out52.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary("mul", e.get("side")?, e.get("px")?)?);
                                    s.push(e.get("z")?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                        out52
                    });
                    args49.push(e.get("RUN")?);
                    fun51.call(args49, kw50)?
                }
            };
            e.set("under", assigned48.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_display_retention.rs",
                    line!(),
                );
                {
                    let fun57 = e.get("slot")?.attr("fuse")?;
                    let mut args55 = Vec::new();
                    let mut kw56 = Vec::new();
                    args55.push(e.get("under")?);
                    fun57.call(args55, kw56)?
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
