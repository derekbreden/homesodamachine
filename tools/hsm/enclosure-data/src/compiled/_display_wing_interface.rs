//! Accepted face-up display cover and its receiver in display-local coordinates.
//!
//! X is across the display, Y runs up it, and Z points out of the visible face.
//! The cover back and both wings share a bed plane. Pocket exits follow world
//! print-down so supports leave through the empty display storey.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod1 = rt.import_module("_swept_top")?;
    e.set("rounded_prism", rt.member("_swept_top", "rounded_prism")?)?;
    let mod2 = rt.import_module("_enclosure_data")?;
    e.set("_dimensions", rt.member("_enclosure_data", "dimensions")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",
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
                        "tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",
                        line!(),
                    );
                    {
                        let fun11 = e.get("_dimensions")?;
                        let mut args9 = Vec::new();
                        let mut kw10 = Vec::new();
                        fun11.call(args9, kw10)?
                    }
                }
                .get(Val::Str("display".into()))?,
            );
            fun5.call(args3, kw4)?
        }
    };
    // box
    e.set("box", {
        let params = vec![
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
                    "tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",
                    line!(),
                );
                {
                    let fun14 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                    let mut args12 = Vec::new();
                    let mut kw13 = Vec::new();
                    args12.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                    args12.push(binary("sub", e.get("y1")?, e.get("y0")?)?);
                    args12.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                    args12.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",
                            line!(),
                        );
                        {
                            let fun17 = e.get("cq")?.attr("Vector")?;
                            let mut args15 = Vec::new();
                            let mut kw16 = Vec::new();
                            args15.push(e.get("x0")?);
                            args15.push(e.get("y0")?);
                            args15.push(e.get("z0")?);
                            fun17.call(args15, kw16)?
                        }
                    });
                    fun14.call(args12, kw13)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // wing
    e.set("wing", {
        let params = vec![("side".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",
                    line!(),
                );
                {
                    let fun20 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",
                            line!(),
                        );
                        {
                            let fun23 = e.get("rounded_prism")?;
                            let mut args21 = Vec::new();
                            let mut kw22 = Vec::new();
                            args21.push(binary("add", e.get("WING_REACH")?, Val::Int(1i64))?);
                            args21.push(e.get("WING_SPAN")?);
                            args21.push(e.get("WING_END_R")?);
                            args21.push(e.get("BACK")?);
                            args21.push(binary("add", e.get("BACK")?, e.get("WING_THICK")?)?);
                            fun23.call(args21, kw22)?
                        }
                    }
                    .attr("translate")?;
                    let mut args18 = Vec::new();
                    let mut kw19 = Vec::new();
                    args18.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "mul",
                            e.get("side")?,
                            binary(
                                "add",
                                binary("truediv", e.get("COVER_X")?, Val::Int(2i64))?,
                                binary(
                                    "truediv",
                                    binary("sub", e.get("WING_REACH")?, Val::Int(1i64))?,
                                    Val::Int(2i64),
                                )?,
                            )?,
                        )?);
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    fun20.call(args18, kw19)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // cover
    e.set("cover",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned24={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun27=e.get("rounded_prism")?;let mut args25=Vec::new();let mut kw26=Vec::new();args25.push(e.get("COVER_X")?);args25.push(e.get("COVER_Y")?);args25.push(e.get("CORNER_R")?);args25.push(e.get("BACK")?);args25.push(Val::Int(0i64));fun27.call(args25,kw26)?}};e.set("bezel",assigned24.clone())?;
let assigned28={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun31=e.get("rounded_prism")?;let mut args29=Vec::new();let mut kw30=Vec::new();args29.push(e.get("WINDOW_X")?);args29.push(e.get("WINDOW_Y")?);args29.push(e.get("WINDOW_R")?);args29.push(binary("sub",e.get("BACK")?,Val::Int(1i64))?);args29.push(Val::Int(1i64));fun31.call(args29,kw30)?}};e.set("window",assigned28.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun34={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun37={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun40=e.get("bezel")?.attr("fuse")?;let mut args38=Vec::new();let mut kw39=Vec::new();args38.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun43=e.get("wing")?;let mut args41=Vec::new();let mut kw42=Vec::new();args41.push(unary("neg",Val::Int(1i64))?);fun43.call(args41,kw42)?}});args38.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun46=e.get("wing")?;let mut args44=Vec::new();let mut kw45=Vec::new();args44.push(Val::Int(1i64));fun46.call(args44,kw45)?}});fun40.call(args38,kw39)?}}.attr("cut")?;let mut args35=Vec::new();let mut kw36=Vec::new();args35.push(e.get("window")?);fun37.call(args35,kw36)?}}.attr("clean")?;let mut args32=Vec::new();let mut kw33=Vec::new();fun34.call(args32,kw33)?}});
Ok(Val::None)})})?;
    // support_exits
    e.set("support_exits",{let params=vec![("depth".into(),None,false),("inset".into(),Some(Val::Float(0.0f64)),false),("roof_drop".into(),Some(Val::Float(0.0f64)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned47=binary("sub",binary("add",binary("add",e.get("BACK")?,e.get("WING_THICK")?)?,e.get("BEARING_AIR")?)?,e.get("roof_drop")?)?;e.set("roof",assigned47.clone())?;
let assigned48=binary("mul",unary("neg",e.get("depth")?)?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun51=e.get("math")?.attr("tan")?;let mut args49=Vec::new();let mut kw50=Vec::new();args49.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun54=e.get("math")?.attr("radians")?;let mut args52=Vec::new();let mut kw53=Vec::new();args52.push(e.get("ANGLE")?);fun54.call(args52,kw53)?}});fun51.call(args49,kw50)?}})?;e.set("shift_y",assigned48.clone())?;
let assigned55={let mut s=Vec::new();Val::list(s)};e.set("exits",assigned55.clone())?;
for item56 in {let mut s=Vec::new();s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Int(1i64));Val::tuple(s)}.iter()? {
e.set("side",item56)?;let assigned57={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun60=e.get("sorted")?;let mut args58=Vec::new();let mut kw59=Vec::new();args58.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,binary("sub",binary("truediv",e.get("COVER_X")?,Val::Int(2i64))?,Val::Float(0.1f64))?)?);s.push(binary("mul",e.get("side")?,binary("add",binary("add",binary("truediv",e.get("COVER_X")?,Val::Int(2i64))?,e.get("WING_REACH")?)?,e.get("TIP_AIR")?)?)?);Val::tuple(s)});fun60.call(args58,kw59)?}};let unpack61=unpack(assigned57.clone(),2)?;e.set("xa",unpack61[0].clone())?;e.set("xb",unpack61[1].clone())?;
let assigned62={let mut s=Vec::new();s.push(binary("add",e.get("xa")?,e.get("inset")?)?);s.push(binary("sub",e.get("xb")?,e.get("inset")?)?);Val::tuple(s)};let unpack63=unpack(assigned62.clone(),2)?;e.set("xa",unpack63[0].clone())?;e.set("xb",unpack63[1].clone())?;
let assigned64={let mut s=Vec::new();s.push(binary("add",binary("sub",binary("truediv",unary("neg",e.get("WING_SPAN")?)?,Val::Int(2i64))?,e.get("END_AIR")?)?,e.get("inset")?)?);s.push(binary("sub",binary("add",binary("truediv",e.get("WING_SPAN")?,Val::Int(2i64))?,e.get("END_AIR")?)?,e.get("inset")?)?);Val::tuple(s)};let unpack65=unpack(assigned64.clone(),2)?;e.set("y0",unpack65[0].clone())?;e.set("y1",unpack65[1].clone())?;
let assigned66={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun69=e.get("cq")?.attr("Wire")?.attr("makePolygon")?;let mut args67=Vec::new();let mut kw68=Vec::new();args67.push({let e=e.child();let out70=Val::list(vec![]);for item71 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(e.get("xa")?);s.push(e.get("y0")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("xb")?);s.push(e.get("y0")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("xb")?);s.push(e.get("y1")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("xa")?);s.push(e.get("y1")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("xa")?);s.push(e.get("y0")?);Val::tuple(s)});Val::tuple(s)}.iter()? {let unpack72=unpack(item71,2)?;e.set("x",unpack72[0].clone())?;e.set("y",unpack72[1].clone())?;out70.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun75=e.get("cq")?.attr("Vector")?;let mut args73=Vec::new();let mut kw74=Vec::new();args73.push(e.get("x")?);args73.push(e.get("y")?);args73.push(e.get("roof")?);fun75.call(args73,kw74)?}}],vec![])?;}out70});fun69.call(args67,kw68)?}};e.set("wire",assigned66.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun78=e.get("exits")?.attr("append")?;let mut args76=Vec::new();let mut kw77=Vec::new();args76.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun81=e.get("cq")?.attr("Solid")?.attr("extrudeLinear")?;let mut args79=Vec::new();let mut kw80=Vec::new();args79.push(e.get("wire")?);args79.push({let mut s=Vec::new();Val::list(s)});args79.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun84=e.get("cq")?.attr("Vector")?;let mut args82=Vec::new();let mut kw83=Vec::new();args82.push(Val::Int(0i64));args82.push(e.get("shift_y")?);args82.push(unary("neg",e.get("depth")?)?);fun84.call(args82,kw83)?}});fun81.call(args79,kw80)?}});fun78.call(args76,kw77)?}};
}
return Ok(e.get("exits")?);
Ok(Val::None)})})?;
    // cuts
    e.set("cuts",{let params=vec![("pcb_depth".into(),None,false),("exit_depth".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned85={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun88=e.get("rounded_prism")?;let mut args86=Vec::new();let mut kw87=Vec::new();args86.push(binary("add",e.get("COVER_X")?,binary("mul",Val::Int(2i64),e.get("BODY_X_AIR")?)?)?);args86.push(binary("add",e.get("COVER_Y")?,binary("mul",Val::Int(2i64),e.get("BODY_Y_AIR")?)?)?);args86.push(binary("add",e.get("CORNER_R")?,e.get("BODY_Y_AIR")?)?);args86.push(e.get("BACK")?);args86.push(Val::Int(1i64));fun88.call(args86,kw87)?}};e.set("inset",assigned85.clone())?;
let assigned89={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun92=e.get("rounded_prism")?;let mut args90=Vec::new();let mut kw91=Vec::new();args90.push(Val::Float(113.8f64));args90.push(Val::Float(77.3f64));args90.push(Val::Float(2.65f64));args90.push(e.get("GLASS_SEAT")?);args90.push(Val::Int(1i64));fun92.call(args90,kw91)?}};e.set("glass",assigned89.clone())?;
let assigned93={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun96=e.get("box")?;let mut args94=Vec::new();let mut kw95=Vec::new();args94.push(binary("sub",Val::Float(0.5f64),binary("truediv",Val::Float(106.3f64),Val::Int(2i64))?)?);args94.push(binary("add",Val::Float(0.5f64),binary("truediv",Val::Float(106.3f64),Val::Int(2i64))?)?);args94.push(binary("sub",unary("neg",Val::Int(1i64))?,binary("truediv",Val::Float(69.3f64),Val::Int(2i64))?)?);args94.push(binary("add",unary("neg",Val::Int(1i64))?,binary("truediv",Val::Float(69.3f64),Val::Int(2i64))?)?);args94.push(unary("neg",e.get("pcb_depth")?)?);args94.push(Val::Int(1i64));fun96.call(args94,kw95)?}};e.set("pcb",assigned93.clone())?;
let assigned97={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun100=e.get("inset")?.attr("fuse")?;let mut args98=Vec::new();let mut kw99=Vec::new();args98.push(e.get("glass")?);args98.push(e.get("pcb")?);fun100.call(args98,kw99)?}};e.set("result",assigned97.clone())?;
for item101 in {let mut s=Vec::new();s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Int(1i64));Val::tuple(s)}.iter()? {
e.set("side",item101)?;let assigned102={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun105=e.get("sorted")?;let mut args103=Vec::new();let mut kw104=Vec::new();args103.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,binary("sub",binary("truediv",e.get("COVER_X")?,Val::Int(2i64))?,Val::Float(0.1f64))?)?);s.push(binary("mul",e.get("side")?,binary("add",binary("add",binary("truediv",e.get("COVER_X")?,Val::Int(2i64))?,e.get("WING_REACH")?)?,e.get("TIP_AIR")?)?)?);Val::tuple(s)});fun105.call(args103,kw104)?}};let unpack106=unpack(assigned102.clone(),2)?;e.set("xa",unpack106[0].clone())?;e.set("xb",unpack106[1].clone())?;
let assigned107={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun110=e.get("result")?.attr("fuse")?;let mut args108=Vec::new();let mut kw109=Vec::new();args108.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun113=e.get("box")?;let mut args111=Vec::new();let mut kw112=Vec::new();args111.push(e.get("xa")?);args111.push(e.get("xb")?);args111.push(binary("sub",binary("truediv",unary("neg",e.get("WING_SPAN")?)?,Val::Int(2i64))?,e.get("END_AIR")?)?);args111.push(binary("add",binary("truediv",e.get("WING_SPAN")?,Val::Int(2i64))?,e.get("END_AIR")?)?);args111.push(e.get("BACK")?);args111.push(binary("add",binary("add",e.get("BACK")?,e.get("WING_THICK")?)?,e.get("BEARING_AIR")?)?);fun113.call(args111,kw112)?}});fun110.call(args108,kw109)?}};e.set("result",assigned107.clone())?;
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun116={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun119=e.get("result")?.attr("fuse")?;let mut args117=Vec::new();let mut kw118=Vec::new();args117.extend({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_display_wing_interface.rs",line!());{let fun122=e.get("support_exits")?;let mut args120=Vec::new();let mut kw121=Vec::new();args120.push(e.get("exit_depth")?);fun122.call(args120,kw121)?}}.iter()?);fun119.call(args117,kw118)?}}.attr("clean")?;let mut args114=Vec::new();let mut kw115=Vec::new();fun116.call(args114,kw115)?}});
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
