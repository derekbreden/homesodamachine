//! The anchor cap and the tube anchor it closes, in the anchor's own frame.
//!
//! `u` runs along the tube, `n` from the tube toward the face the rib roots on, and `t = n x u`; a
//! section point (a, b) stands at mid + a*t + b*n, with b = 0 on the tube's axis plane. That is the
//! frame `enclosure._tube_anchors` strikes every rib in, so one station places the rib, its catch
//! windows, the ceiling's wing room and the cap.
//!
//! THE RIB IS THE TIE RIB'S HALF PIPE WITHOUT THE TIE. A solid post, the seat bored into it and its
//! lips flat one `WALL` past the axis plane, with a catch window in each flank. Each window is a
//! closed pocket between the rib's two end webs, so on a piece printed root-down its bearing face
//! prints as a bridge web to web, the way the tie channel's crown did. On a rib rooted on a wall the
//! flank that looks print-down and its window's roof bridge web to web instead, and the two end
//! webs stand on the tied rib's own 45-degree corbels (`enclosure._capped_anchor`).
//!
//! THE CAP IS THE OTHER HALF OF THE PIPE, one section extruded `CAP_LEN` along the tube. Below the
//! axis plane it is solid from the bore out to its round back; two `WING`-thick wings rise up the
//! rib's flanks and each carries a lip that drops into its window. A `CAVITY` gap separates the
//! half pipe from each wing for `CAVITY_DEG` round the pipe, so a wing bends from the gap's round
//! end rather than from the axis plane. That length is what sets its strain going on
//! (`wing_strain`), and the cap's README holds it beside the accepted faucet display cover's.
//!
//! THE CAP IS CUT FOR THE 1/4" TUBE'S SEAT AND PRINTS STANDING ON ITS END. Every layer is the
//! whole section, so the wings bend along their extrusion lines, and no face overhangs.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun8 = e.get("Path")?;
                    let mut args6 = Vec::new();
                    let mut kw7 = Vec::new();
                    args6.push(e.get("__file__")?);
                    fun8.call(args6, kw7)?
                }
            }
            .attr("resolve")?;
            let mut args3 = Vec::new();
            let mut kw4 = Vec::new();
            fun5.call(args3, kw4)?
        }
    }
    .attr("parent")?;
    e.set("_HERE", assigned2.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
            line!(),
        );
        {
            let fun11 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args9 = Vec::new();
            let mut kw10 = Vec::new();
            args9.push(Val::Int(0i64));
            args9.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun14 = e.get("str")?;
                    let mut args12 = Vec::new();
                    let mut kw13 = Vec::new();
                    args12.push(e.get("_HERE")?);
                    fun14.call(args12, kw13)?
                }
            });
            fun11.call(args9, kw10)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
            line!(),
        );
        {
            let fun17 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args15 = Vec::new();
            let mut kw16 = Vec::new();
            args15.push(Val::Int(0i64));
            args15.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun20 = e.get("str")?;
                    let mut args18 = Vec::new();
                    let mut kw19 = Vec::new();
                    args18.push(binary(
                        "truediv",
                        e.get("_HERE")?.attr("parents")?.get(Val::Int(1i64))?,
                        Val::Str("cadlib".into()),
                    )?);
                    fun20.call(args18, kw19)?
                }
            });
            fun17.call(args15, kw16)?
        }
    };
    e.set("dims", rt.import_module("_enclosure_interface")?)?;
    e.set("fits", rt.import_module("fits")?)?;
    let assigned21 = e.get("dims")?.attr("wall")?;
    e.set("WALL", assigned21.clone())?;
    let assigned22 = Val::Float(6.35f64);
    e.set("TUBE_OD", assigned22.clone())?;
    let assigned23 = binary(
        "add",
        binary("truediv", e.get("TUBE_OD")?, Val::Float(2.0f64))?,
        e.get("fits")?.attr("slip")?,
    )?;
    e.set("SEAT_R", assigned23.clone())?;
    let assigned24 = binary("add", e.get("SEAT_R")?, e.get("WALL")?)?;
    e.set("RIB_R", assigned24.clone())?;
    let assigned25 = Val::Float(10.0f64);
    e.set("CAP_LEN", assigned25.clone())?;
    let assigned26 = e.get("fits")?.attr("slip")?;
    e.set("END_AIR", assigned26.clone())?;
    let assigned27 = binary(
        "add",
        e.get("CAP_LEN")?,
        binary("mul", Val::Float(2.0f64), e.get("END_AIR")?)?,
    )?;
    e.set("WINDOW_LEN", assigned27.clone())?;
    let assigned28 = e.get("WALL")?;
    e.set("END_WEB", assigned28.clone())?;
    let assigned29 = binary(
        "add",
        e.get("WINDOW_LEN")?,
        binary("mul", Val::Float(2.0f64), e.get("END_WEB")?)?,
    )?;
    e.set("RIB_LEN", assigned29.clone())?;
    let assigned30 = Val::Float(2.5f64);
    e.set("SADDLE", assigned30.clone())?;
    let assigned31 = Val::Float(1.5f64);
    e.set("WING", assigned31.clone())?;
    let assigned32 = e.get("fits")?.attr("slip")?;
    e.set("WING_AIR", assigned32.clone())?;
    let assigned33 = Val::Float(1.2f64);
    e.set("ENGAGE", assigned33.clone())?;
    let assigned34 = Val::Float(0.9f64);
    e.set("LIP_TIP", assigned34.clone())?;
    let assigned35 = Val::Float(30.0f64);
    e.set("LEAD_IN", assigned35.clone())?;
    let assigned36 = Val::Float(10.3f64);
    e.set("WING_TOP", assigned36.clone())?;
    let assigned37 = Val::Float(36.0f64);
    e.set("CAVITY_DEG", assigned37.clone())?;
    let assigned38 = Val::Float(0.45f64);
    e.set("MOUTH", assigned38.clone())?;
    let assigned39 = Val::Float(10.0f64);
    e.set("MOUTH_DEG", assigned39.clone())?;
    let assigned40 = Val::Float(0.8f64);
    e.set("RIB_CHAMFER", assigned40.clone())?;
    let assigned41 = Val::Float(0.6f64);
    e.set("HEADROOM", assigned41.clone())?;
    let assigned42 = binary("truediv", e.get("ENGAGE")?, {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
            line!(),
        );
        {
            let fun45 = e.get("math")?.attr("tan")?;
            let mut args43 = Vec::new();
            let mut kw44 = Vec::new();
            args43.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun48 = e.get("math")?.attr("radians")?;
                    let mut args46 = Vec::new();
                    let mut kw47 = Vec::new();
                    args46.push(e.get("LEAD_IN")?);
                    fun48.call(args46, kw47)?
                }
            });
            fun45.call(args43, kw44)?
        }
    })?;
    e.set("RAMP_H", assigned42.clone())?;
    let assigned49 = binary("add", e.get("LIP_TIP")?, e.get("RAMP_H")?)?;
    e.set("LIP_H", assigned49.clone())?;
    let assigned50 = binary("sub", e.get("WING_TOP")?, e.get("LIP_H")?)?;
    e.set("LIP_B", assigned50.clone())?;
    let assigned51 = binary("add", e.get("RIB_R")?, e.get("WING_AIR")?)?;
    e.set("WING_IN", assigned51.clone())?;
    let assigned52 = binary("add", e.get("WING_IN")?, e.get("WING")?)?;
    e.set("WING_OUT", assigned52.clone())?;
    let assigned53 = binary("add", e.get("SEAT_R")?, e.get("SADDLE")?)?;
    e.set("SADDLE_R", assigned53.clone())?;
    let assigned54 = binary("sub", e.get("WING_IN")?, e.get("SADDLE_R")?)?;
    e.set("CAVITY", assigned54.clone())?;
    let assigned55 = binary(
        "add",
        e.get("fits")?.attr("slip")?,
        e.get("fits")?.attr("supported_surface")?,
    )?;
    e.set("BEARING_PLAY", assigned55.clone())?;
    let assigned56 = binary(
        "add",
        binary("add", e.get("ENGAGE")?, e.get("fits")?.attr("slip")?)?,
        e.get("fits")?.attr("supported_surface")?,
    )?;
    e.set("WINDOW_DEPTH", assigned56.clone())?;
    let assigned57 = binary("sub", e.get("LIP_B")?, e.get("BEARING_PLAY")?)?;
    e.set("WINDOW_B0", assigned57.clone())?;
    let assigned58 = binary(
        "add",
        binary(
            "add",
            binary("add", e.get("LIP_B")?, e.get("LIP_TIP")?)?,
            binary(
                "mul",
                binary(
                    "truediv",
                    binary("sub", e.get("ENGAGE")?, e.get("WING_AIR")?)?,
                    e.get("ENGAGE")?,
                )?,
                e.get("RAMP_H")?,
            )?,
        )?,
        e.get("fits")?.attr("slip")?,
    )?;
    e.set("WINDOW_B1", assigned58.clone())?;
    let assigned59 = binary(
        "add",
        binary(
            "add",
            binary("add", e.get("WING_AIR")?, e.get("WING")?)?,
            e.get("ENGAGE")?,
        )?,
        binary("mul", Val::Float(2.0f64), e.get("fits")?.attr("slip")?)?,
    )?;
    e.set("SLOT_W", assigned59.clone())?;
    let assigned60 = binary("add", e.get("WING_TOP")?, e.get("HEADROOM")?)?;
    e.set("SLOT_TOP", assigned60.clone())?;
    e.set("Frame.__init__",{let params=vec![("self".into(),None,false),("mid".into(),None,false),("u".into(),None,false),("n".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned61={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun64=e.get("tuple")?;let mut args62=Vec::new();let mut kw63=Vec::new();args62.push({let e=e.child();let out65=Val::list(vec![]);for item66 in e.get("mid")?.iter()? {e.set("c",item66)?;out65.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun69=e.get("float")?;let mut args67=Vec::new();let mut kw68=Vec::new();args67.push(e.get("c")?);fun69.call(args67,kw68)?}}],vec![])?;}out65});fun64.call(args62,kw63)?}};e.get("self")?.setattr("mid",assigned61.clone())?;
let assigned70={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun73=e.get("tuple")?;let mut args71=Vec::new();let mut kw72=Vec::new();args71.push({let e=e.child();let out74=Val::list(vec![]);for item75 in e.get("u")?.iter()? {e.set("c",item75)?;out74.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun78=e.get("float")?;let mut args76=Vec::new();let mut kw77=Vec::new();args76.push(e.get("c")?);fun78.call(args76,kw77)?}}],vec![])?;}out74});fun73.call(args71,kw72)?}};e.get("self")?.setattr("u",assigned70.clone())?;
let assigned79={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun82=e.get("tuple")?;let mut args80=Vec::new();let mut kw81=Vec::new();args80.push({let e=e.child();let out83=Val::list(vec![]);for item84 in e.get("n")?.iter()? {e.set("c",item84)?;out83.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun87=e.get("float")?;let mut args85=Vec::new();let mut kw86=Vec::new();args85.push(e.get("c")?);fun87.call(args85,kw86)?}}],vec![])?;}out83});fun82.call(args80,kw81)?}};e.get("self")?.setattr("n",assigned79.clone())?;
let assigned88={let mut s=Vec::new();s.push(e.get("self")?.attr("u")?);s.push(e.get("self")?.attr("n")?);Val::tuple(s)};let unpack89=unpack(assigned88.clone(),2)?;e.set("u_",unpack89[0].clone())?;e.set("n_",unpack89[1].clone())?;
let assigned90={let mut s=Vec::new();s.push(binary("sub",binary("mul",e.get("n_")?.get(Val::Int(1i64))?,e.get("u_")?.get(Val::Int(2i64))?)?,binary("mul",e.get("n_")?.get(Val::Int(2i64))?,e.get("u_")?.get(Val::Int(1i64))?)?)?);s.push(binary("sub",binary("mul",e.get("n_")?.get(Val::Int(2i64))?,e.get("u_")?.get(Val::Int(0i64))?)?,binary("mul",e.get("n_")?.get(Val::Int(0i64))?,e.get("u_")?.get(Val::Int(2i64))?)?)?);s.push(binary("sub",binary("mul",e.get("n_")?.get(Val::Int(0i64))?,e.get("u_")?.get(Val::Int(1i64))?)?,binary("mul",e.get("n_")?.get(Val::Int(1i64))?,e.get("u_")?.get(Val::Int(0i64))?)?)?);Val::tuple(s)};e.get("self")?.setattr("t",assigned90.clone())?;
Ok(Val::None)})})?;
    e.set("Frame.point", {
        let params = vec![
            ("self".into(), None, false),
            ("a".into(), None, false),
            ("b".into(), None, false),
            ("s".into(), Some(Val::Float(0.0f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun93 = e.get("tuple")?;
                    let mut args91 = Vec::new();
                    let mut kw92 = Vec::new();
                    args91.push({
                        let e = e.child();
                        let out94 = Val::list(vec![]);
                        for item95 in {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun98 = e.get("range")?;
                                let mut args96 = Vec::new();
                                let mut kw97 = Vec::new();
                                args96.push(Val::Int(3i64));
                                fun98.call(args96, kw97)?
                            }
                        }
                        .iter()?
                        {
                            e.set("k", item95)?;
                            out94.attr("append")?.call(
                                vec![binary(
                                    "add",
                                    binary(
                                        "add",
                                        binary(
                                            "add",
                                            e.get("self")?.attr("mid")?.get(e.get("k")?)?,
                                            binary(
                                                "mul",
                                                e.get("a")?,
                                                e.get("self")?.attr("t")?.get(e.get("k")?)?,
                                            )?,
                                        )?,
                                        binary(
                                            "mul",
                                            e.get("b")?,
                                            e.get("self")?.attr("n")?.get(e.get("k")?)?,
                                        )?,
                                    )?,
                                    binary(
                                        "mul",
                                        e.get("s")?,
                                        e.get("self")?.attr("u")?.get(e.get("k")?)?,
                                    )?,
                                )?],
                                vec![],
                            )?;
                        }
                        out94
                    });
                    fun93.call(args91, kw92)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("Frame.plane",{let params=vec![("self".into(),None,false),("s".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("cq",rt.import_module("cadquery")?)?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun101=e.get("cq")?.attr("Plane")?;let mut args99=Vec::new();let mut kw100=Vec::new();kw100.push(("origin".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun104=e.get("cq")?.attr("Vector")?;let mut args102=Vec::new();let mut kw103=Vec::new();args102.extend({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun107=e.get("self")?.attr("point")?;let mut args105=Vec::new();let mut kw106=Vec::new();args105.push(Val::Float(0.0f64));args105.push(Val::Float(0.0f64));args105.push(e.get("s")?);fun107.call(args105,kw106)?}}.iter()?);fun104.call(args102,kw103)?}}));kw100.push(("xDir".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun110=e.get("cq")?.attr("Vector")?;let mut args108=Vec::new();let mut kw109=Vec::new();args108.extend(e.get("self")?.attr("t")?.iter()?);fun110.call(args108,kw109)?}}));kw100.push(("normal".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun113=e.get("cq")?.attr("Vector")?;let mut args111=Vec::new();let mut kw112=Vec::new();args111.extend(e.get("self")?.attr("u")?.iter()?);fun113.call(args111,kw112)?}}));fun101.call(args99,kw100)?}});
Ok(Val::None)})})?;
    e.set("Frame.prism",{let params=vec![("self".into(),None,false),("pts".into(),None,false),("s0".into(),None,false),("s1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("cq",rt.import_module("cadquery")?)?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun116={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun119={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun122={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun125={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun128=e.get("cq")?.attr("Workplane")?;let mut args126=Vec::new();let mut kw127=Vec::new();args126.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun131=e.get("self")?.attr("plane")?;let mut args129=Vec::new();let mut kw130=Vec::new();args129.push(e.get("s0")?);fun131.call(args129,kw130)?}});fun128.call(args126,kw127)?}}.attr("polyline")?;let mut args123=Vec::new();let mut kw124=Vec::new();args123.push(e.get("pts")?);fun125.call(args123,kw124)?}}.attr("close")?;let mut args120=Vec::new();let mut kw121=Vec::new();fun122.call(args120,kw121)?}}.attr("extrude")?;let mut args117=Vec::new();let mut kw118=Vec::new();args117.push(binary("sub",e.get("s1")?,e.get("s0")?)?);fun119.call(args117,kw118)?}}.attr("val")?;let mut args114=Vec::new();let mut kw115=Vec::new();fun116.call(args114,kw115)?}});
Ok(Val::None)})})?;
    e.set("Frame.section",{let params=vec![("self".into(),None,false),("start".into(),None,false),("segments".into(),None,false),("s0".into(),None,false),("s1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("cq",rt.import_module("cadquery")?)?;
let assigned132={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun135={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun138=e.get("cq")?.attr("Workplane")?;let mut args136=Vec::new();let mut kw137=Vec::new();args136.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun141=e.get("self")?.attr("plane")?;let mut args139=Vec::new();let mut kw140=Vec::new();args139.push(e.get("s0")?);fun141.call(args139,kw140)?}});fun138.call(args136,kw137)?}}.attr("moveTo")?;let mut args133=Vec::new();let mut kw134=Vec::new();args133.extend(e.get("start")?.iter()?);fun135.call(args133,kw134)?}};e.set("wp",assigned132.clone())?;
for item142 in e.get("segments")?.iter()? {
e.set("seg",item142)?;let assigned143=if {let v144=e.get("seg")?.get(Val::Int(0i64))?;let v145=Val::Str("L".into());Val::Bool(compare("eq",v144.clone(),v145.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun148=e.get("wp")?.attr("lineTo")?;let mut args146=Vec::new();let mut kw147=Vec::new();args146.extend(e.get("seg")?.get(Val::Int(1i64))?.iter()?);fun148.call(args146,kw147)?}}} else {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun151=e.get("wp")?.attr("threePointArc")?;let mut args149=Vec::new();let mut kw150=Vec::new();args149.push(e.get("seg")?.get(Val::Int(1i64))?);args149.push(e.get("seg")?.get(Val::Int(2i64))?);fun151.call(args149,kw150)?}}};e.set("wp",assigned143.clone())?;
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun154={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun157={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun160=e.get("wp")?.attr("close")?;let mut args158=Vec::new();let mut kw159=Vec::new();fun160.call(args158,kw159)?}}.attr("extrude")?;let mut args155=Vec::new();let mut kw156=Vec::new();args155.push(binary("sub",e.get("s1")?,e.get("s0")?)?);fun157.call(args155,kw156)?}}.attr("val")?;let mut args152=Vec::new();let mut kw153=Vec::new();fun154.call(args152,kw153)?}});
Ok(Val::None)})})?;
    e.set("Frame.bore",{let params=vec![("self".into(),None,false),("r".into(),None,false),("s0".into(),None,false),("s1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("cq",rt.import_module("cadquery")?)?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun163=e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;let mut args161=Vec::new();let mut kw162=Vec::new();args161.push(e.get("r")?);args161.push(binary("sub",e.get("s1")?,e.get("s0")?)?);args161.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun166=e.get("cq")?.attr("Vector")?;let mut args164=Vec::new();let mut kw165=Vec::new();args164.extend({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun169=e.get("self")?.attr("point")?;let mut args167=Vec::new();let mut kw168=Vec::new();args167.push(Val::Float(0.0f64));args167.push(Val::Float(0.0f64));args167.push(e.get("s0")?);fun169.call(args167,kw168)?}}.iter()?);fun166.call(args164,kw165)?}});args161.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun172=e.get("cq")?.attr("Vector")?;let mut args170=Vec::new();let mut kw171=Vec::new();args170.extend(e.get("self")?.attr("u")?.iter()?);fun172.call(args170,kw171)?}});fun163.call(args161,kw162)?}});
Ok(Val::None)})})?;
    e.set("Frame", rt.python_type("_anchor_cap_interface", "Frame")?)?;
    // _lip
    e.set("_lip", {
        let params = vec![("side".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned173 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("WING_IN")?, Val::Float(0.05f64))?);
                    s.push(e.get("LIP_B")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("WING_IN")?, e.get("ENGAGE")?)?);
                    s.push(e.get("LIP_B")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("WING_IN")?, e.get("ENGAGE")?)?);
                    s.push(binary("add", e.get("LIP_B")?, e.get("LIP_TIP")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("WING_IN")?);
                    s.push(binary("add", e.get("LIP_B")?, e.get("LIP_H")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("WING_IN")?, Val::Float(0.05f64))?);
                    s.push(binary("add", e.get("LIP_B")?, e.get("LIP_H")?)?);
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("pts", assigned173.clone())?;
            return Ok({
                let e = e.child();
                let out174 = Val::list(vec![]);
                for item175 in e.get("pts")?.iter()? {
                    let unpack176 = unpack(item175, 2)?;
                    e.set("a", unpack176[0].clone())?;
                    e.set("b", unpack176[1].clone())?;
                    out174.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(binary("mul", e.get("side")?, e.get("a")?)?);
                            s.push(e.get("b")?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out174
            });
            Ok(Val::None)
        })
    })?;
    // _cavity
    e.set("_cavity", {
        let params = vec![
            ("frame".into(), None, false),
            ("side".into(), None, false),
            ("s0".into(), None, false),
            ("s1".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned177 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun180 = e.get("math")?.attr("radians")?;
                    let mut args178 = Vec::new();
                    let mut kw179 = Vec::new();
                    args178.push(e.get("CAVITY_DEG")?);
                    fun180.call(args178, kw179)?
                }
            };
            e.set("t", assigned177.clone())?;
            let assigned181 = {
                let mut s = Vec::new();
                s.push(e.get("SADDLE_R")?);
                s.push(e.get("WING_IN")?);
                Val::tuple(s)
            };
            let unpack182 = unpack(assigned181.clone(), 2)?;
            e.set("r0", unpack182[0].clone())?;
            e.set("r1", unpack182[1].clone())?;
            let assigned183 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    binary("add", e.get("r0")?, e.get("r1")?)?,
                    Val::Float(2.0f64),
                )?);
                s.push(binary(
                    "truediv",
                    binary("sub", e.get("r1")?, e.get("r0")?)?,
                    Val::Float(2.0f64),
                )?);
                Val::tuple(s)
            };
            let unpack184 = unpack(assigned183.clone(), 2)?;
            e.set("rm", unpack184[0].clone())?;
            e.set("rh", unpack184[1].clone())?;
            let assigned185 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    binary("mul", e.get("rm")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                            line!(),
                        );
                        {
                            let fun188 = e.get("math")?.attr("cos")?;
                            let mut args186 = Vec::new();
                            let mut kw187 = Vec::new();
                            args186.push(e.get("t")?);
                            fun188.call(args186, kw187)?
                        }
                    })?,
                    binary("mul", e.get("rh")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                            line!(),
                        );
                        {
                            let fun191 = e.get("math")?.attr("sin")?;
                            let mut args189 = Vec::new();
                            let mut kw190 = Vec::new();
                            args189.push(e.get("t")?);
                            fun191.call(args189, kw190)?
                        }
                    })?,
                )?);
                s.push(binary(
                    "sub",
                    binary("mul", unary("neg", e.get("rm")?)?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                            line!(),
                        );
                        {
                            let fun194 = e.get("math")?.attr("sin")?;
                            let mut args192 = Vec::new();
                            let mut kw193 = Vec::new();
                            args192.push(e.get("t")?);
                            fun194.call(args192, kw193)?
                        }
                    })?,
                    binary("mul", e.get("rh")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                            line!(),
                        );
                        {
                            let fun197 = e.get("math")?.attr("cos")?;
                            let mut args195 = Vec::new();
                            let mut kw196 = Vec::new();
                            args195.push(e.get("t")?);
                            fun197.call(args195, kw196)?
                        }
                    })?,
                )?);
                Val::tuple(s)
            };
            e.set("end", assigned185.clone())?;
            let assigned198 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("L".into()));
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("r1")?);
                        s.push(Val::Float(0.5f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("L".into()));
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("r1")?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("A".into()));
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("mul", e.get("r1")?, {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun201 = e.get("math")?.attr("cos")?;
                                let mut args199 = Vec::new();
                                let mut kw200 = Vec::new();
                                args199.push(binary("truediv", e.get("t")?, Val::Int(2i64))?);
                                fun201.call(args199, kw200)?
                            }
                        })?);
                        s.push(binary("mul", unary("neg", e.get("r1")?)?, {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun204 = e.get("math")?.attr("sin")?;
                                let mut args202 = Vec::new();
                                let mut kw203 = Vec::new();
                                args202.push(binary("truediv", e.get("t")?, Val::Int(2i64))?);
                                fun204.call(args202, kw203)?
                            }
                        })?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("mul", e.get("r1")?, {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun207 = e.get("math")?.attr("cos")?;
                                let mut args205 = Vec::new();
                                let mut kw206 = Vec::new();
                                args205.push(e.get("t")?);
                                fun207.call(args205, kw206)?
                            }
                        })?);
                        s.push(binary("mul", unary("neg", e.get("r1")?)?, {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun210 = e.get("math")?.attr("sin")?;
                                let mut args208 = Vec::new();
                                let mut kw209 = Vec::new();
                                args208.push(e.get("t")?);
                                fun210.call(args208, kw209)?
                            }
                        })?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("A".into()));
                    s.push(e.get("end")?);
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("mul", e.get("r0")?, {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun213 = e.get("math")?.attr("cos")?;
                                let mut args211 = Vec::new();
                                let mut kw212 = Vec::new();
                                args211.push(e.get("t")?);
                                fun213.call(args211, kw212)?
                            }
                        })?);
                        s.push(binary("mul", unary("neg", e.get("r0")?)?, {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun216 = e.get("math")?.attr("sin")?;
                                let mut args214 = Vec::new();
                                let mut kw215 = Vec::new();
                                args214.push(e.get("t")?);
                                fun216.call(args214, kw215)?
                            }
                        })?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("A".into()));
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("mul", e.get("r0")?, {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun219 = e.get("math")?.attr("cos")?;
                                let mut args217 = Vec::new();
                                let mut kw218 = Vec::new();
                                args217.push(binary("truediv", e.get("t")?, Val::Int(2i64))?);
                                fun219.call(args217, kw218)?
                            }
                        })?);
                        s.push(binary("mul", unary("neg", e.get("r0")?)?, {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun222 = e.get("math")?.attr("sin")?;
                                let mut args220 = Vec::new();
                                let mut kw221 = Vec::new();
                                args220.push(binary("truediv", e.get("t")?, Val::Int(2i64))?);
                                fun222.call(args220, kw221)?
                            }
                        })?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("r0")?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("pts", assigned198.clone())?;
            let assigned223 = {
                let e = e.child();
                let out224 = Val::list(vec![]);
                for item225 in e.get("pts")?.iter()? {
                    let unpack226 = item225.iter()?;
                    anyhow::ensure!(unpack226.len() >= 1, "not enough values to unpack");
                    e.set("k", unpack226[0].clone())?;
                    e.set(
                        "rest",
                        Val::list(unpack226[1..unpack226.len() - 0].to_vec()),
                    )?;
                    out224.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(e.get("k")?);
                            s.extend(
                                {
                                    let e = e.child();
                                    let out227 = Val::list(vec![]);
                                    for item228 in e.get("rest")?.iter()? {
                                        e.set("p", item228)?;
                                        out227.attr("append")?.call(
                                            vec![{
                                                let mut s = Vec::new();
                                                s.push(binary(
                                                    "mul",
                                                    e.get("side")?,
                                                    e.get("p")?.get(Val::Int(0i64))?,
                                                )?);
                                                s.push(e.get("p")?.get(Val::Int(1i64))?);
                                                Val::tuple(s)
                                            }],
                                            vec![],
                                        )?;
                                    }
                                    out227
                                }
                                .iter()?,
                            );
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out224
            };
            e.set("mirror", assigned223.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun231 = e.get("frame")?.attr("section")?;
                    let mut args229 = Vec::new();
                    let mut kw230 = Vec::new();
                    args229.push({
                        let mut s = Vec::new();
                        s.push(binary("mul", e.get("side")?, e.get("r0")?)?);
                        s.push(Val::Float(0.5f64));
                        Val::tuple(s)
                    });
                    args229.push(e.get("mirror")?);
                    args229.push(e.get("s0")?);
                    args229.push(e.get("s1")?);
                    fun231.call(args229, kw230)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // cap
    e.set("cap",{let params=vec![("frame".into(),None,false),("seat_r".into(),Some(e.get("SEAT_R")?),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned232={let mut s=Vec::new();s.push(binary("truediv",unary("neg",e.get("CAP_LEN")?)?,Val::Float(2.0f64))?);s.push(binary("truediv",e.get("CAP_LEN")?,Val::Float(2.0f64))?);Val::tuple(s)};let unpack233=unpack(assigned232.clone(),2)?;e.set("s0",unpack233[0].clone())?;e.set("s1",unpack233[1].clone())?;
let assigned234={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun237=e.get("math")?.attr("cos")?;let mut args235=Vec::new();let mut kw236=Vec::new();args235.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun240=e.get("math")?.attr("radians")?;let mut args238=Vec::new();let mut kw239=Vec::new();args238.push(e.get("MOUTH_DEG")?);fun240.call(args238,kw239)?}});fun237.call(args235,kw236)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun243=e.get("math")?.attr("sin")?;let mut args241=Vec::new();let mut kw242=Vec::new();args241.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun246=e.get("math")?.attr("radians")?;let mut args244=Vec::new();let mut kw245=Vec::new();args244.push(e.get("MOUTH_DEG")?);fun246.call(args244,kw245)?}});fun243.call(args241,kw242)?}});Val::tuple(s)};let unpack247=unpack(assigned234.clone(),2)?;e.set("ca",unpack247[0].clone())?;e.set("sa",unpack247[1].clone())?;
let assigned248={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun251=e.get("frame")?.attr("section")?;let mut args249=Vec::new();let mut kw250=Vec::new();args249.push({let mut s=Vec::new();s.push(e.get("WING_IN")?);s.push(e.get("WING_TOP")?);Val::tuple(s)});args249.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("L".into()));s.push({let mut s=Vec::new();s.push(e.get("WING_OUT")?);s.push(e.get("WING_TOP")?);Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("L".into()));s.push({let mut s=Vec::new();s.push(e.get("WING_OUT")?);s.push(Val::Float(0.0f64));Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("A".into()));s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(unary("neg",e.get("WING_OUT")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(unary("neg",e.get("WING_OUT")?)?);s.push(Val::Float(0.0f64));Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("L".into()));s.push({let mut s=Vec::new();s.push(unary("neg",e.get("WING_OUT")?)?);s.push(e.get("WING_TOP")?);Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("L".into()));s.push({let mut s=Vec::new();s.push(unary("neg",e.get("WING_IN")?)?);s.push(e.get("WING_TOP")?);Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("L".into()));s.push({let mut s=Vec::new();s.push(unary("neg",e.get("WING_IN")?)?);s.push(Val::Float(0.0f64));Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("L".into()));s.push({let mut s=Vec::new();s.push(binary("sub",unary("neg",e.get("seat_r")?)?,e.get("MOUTH")?)?);s.push(Val::Float(0.0f64));Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("L".into()));s.push({let mut s=Vec::new();s.push(binary("mul",unary("neg",e.get("seat_r")?)?,e.get("ca")?)?);s.push(binary("mul",unary("neg",e.get("seat_r")?)?,e.get("sa")?)?);Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("A".into()));s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(unary("neg",e.get("seat_r")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("mul",e.get("seat_r")?,e.get("ca")?)?);s.push(binary("mul",unary("neg",e.get("seat_r")?)?,e.get("sa")?)?);Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("L".into()));s.push({let mut s=Vec::new();s.push(binary("add",e.get("seat_r")?,e.get("MOUTH")?)?);s.push(Val::Float(0.0f64));Val::tuple(s)});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("L".into()));s.push({let mut s=Vec::new();s.push(e.get("WING_IN")?);s.push(Val::Float(0.0f64));Val::tuple(s)});Val::tuple(s)});Val::list(s)});args249.push(e.get("s0")?);args249.push(e.get("s1")?);fun251.call(args249,kw250)?}};e.set("body",assigned248.clone())?;
for item252 in {let mut s=Vec::new();s.push(Val::Int(1i64));s.push(unary("neg",Val::Int(1i64))?);Val::tuple(s)}.iter()? {
e.set("side",item252)?;let assigned253={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun256=e.get("body")?.attr("fuse")?;let mut args254=Vec::new();let mut kw255=Vec::new();args254.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun259=e.get("frame")?.attr("prism")?;let mut args257=Vec::new();let mut kw258=Vec::new();args257.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun262=e.get("_lip")?;let mut args260=Vec::new();let mut kw261=Vec::new();args260.push(e.get("side")?);fun262.call(args260,kw261)?}});args257.push(e.get("s0")?);args257.push(e.get("s1")?);fun259.call(args257,kw258)?}});fun256.call(args254,kw255)?}};e.set("body",assigned253.clone())?;
}
for item263 in {let mut s=Vec::new();s.push(Val::Int(1i64));s.push(unary("neg",Val::Int(1i64))?);Val::tuple(s)}.iter()? {
e.set("side",item263)?;let assigned264={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun267=e.get("body")?.attr("cut")?;let mut args265=Vec::new();let mut kw266=Vec::new();args265.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun270=e.get("_cavity")?;let mut args268=Vec::new();let mut kw269=Vec::new();args268.push(e.get("frame")?);args268.push(e.get("side")?);args268.push(binary("sub",e.get("s0")?,Val::Float(1.0f64))?);args268.push(binary("add",e.get("s1")?,Val::Float(1.0f64))?);fun270.call(args268,kw269)?}});fun267.call(args265,kw266)?}};e.set("body",assigned264.clone())?;
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun273=e.get("body")?.attr("clean")?;let mut args271=Vec::new();let mut kw272=Vec::new();fun273.call(args271,kw272)?}});
Ok(Val::None)})})?;
    // rib
    e.set("rib", {
        let params = vec![
            ("frame".into(), None, false),
            ("b_root".into(), None, false),
            ("seat_r".into(), Some(e.get("SEAT_R")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned274 = e.get("RIB_CHAMFER")?;
            e.set("c", assigned274.clone())?;
            let assigned275 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun278 = e.get("frame")?.attr("prism")?;
                    let mut args276 = Vec::new();
                    let mut kw277 = Vec::new();
                    args276.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("add", unary("neg", e.get("RIB_R")?)?, e.get("c")?)?);
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("sub", e.get("RIB_R")?, e.get("c")?)?);
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("RIB_R")?);
                            s.push(e.get("c")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("RIB_R")?);
                            s.push(e.get("b_root")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", e.get("RIB_R")?)?);
                            s.push(e.get("b_root")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", e.get("RIB_R")?)?);
                            s.push(e.get("c")?);
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    args276.push(binary(
                        "truediv",
                        unary("neg", e.get("RIB_LEN")?)?,
                        Val::Float(2.0f64),
                    )?);
                    args276.push(binary("truediv", e.get("RIB_LEN")?, Val::Float(2.0f64))?);
                    fun278.call(args276, kw277)?
                }
            };
            e.set("body", assigned275.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun281 = e.get("body")?.attr("cut")?;
                    let mut args279 = Vec::new();
                    let mut kw280 = Vec::new();
                    args279.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                            line!(),
                        );
                        {
                            let fun284 = e.get("frame")?.attr("bore")?;
                            let mut args282 = Vec::new();
                            let mut kw283 = Vec::new();
                            args282.push(e.get("seat_r")?);
                            args282.push(binary(
                                "sub",
                                binary(
                                    "truediv",
                                    unary("neg", e.get("RIB_LEN")?)?,
                                    Val::Float(2.0f64),
                                )?,
                                Val::Float(1.0f64),
                            )?);
                            args282.push(binary(
                                "add",
                                binary("truediv", e.get("RIB_LEN")?, Val::Float(2.0f64))?,
                                Val::Float(1.0f64),
                            )?);
                            fun284.call(args282, kw283)?
                        }
                    });
                    fun281.call(args279, kw280)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // window_top
    e.set("window_top", {
        let params = vec![("b_face".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(
                if {
                    let v285 = e.get("b_face")?;
                    let v286 = binary(
                        "sub",
                        e.get("SLOT_TOP")?,
                        binary("truediv", e.get("HEADROOM")?, Val::Float(2.0f64))?,
                    )?;
                    Val::Bool(compare("lt", v285.clone(), v286.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("SLOT_TOP")?
                } else {
                    e.get("b_face")?
                },
            );
            Ok(Val::None)
        })
    })?;
    // windows
    e.set("windows", {
        let params = vec![
            ("frame".into(), None, false),
            ("b_face".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned287 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                    line!(),
                );
                {
                    let fun290 = e.get("window_top")?;
                    let mut args288 = Vec::new();
                    let mut kw289 = Vec::new();
                    args288.push(e.get("b_face")?);
                    fun290.call(args288, kw289)?
                }
            };
            e.set("top", assigned287.clone())?;
            let assigned291 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("out", assigned291.clone())?;
            for item292 in {
                let mut s = Vec::new();
                s.push(Val::Int(1i64));
                s.push(unary("neg", Val::Int(1i64))?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("side", item292)?;
                let assigned293 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "mul",
                        e.get("side")?,
                        binary("sub", e.get("RIB_R")?, e.get("WINDOW_DEPTH")?)?,
                    )?);
                    s.push(binary(
                        "mul",
                        e.get("side")?,
                        binary("add", e.get("RIB_R")?, Val::Float(2.0f64))?,
                    )?);
                    Val::tuple(s)
                };
                let unpack294 = unpack(assigned293.clone(), 2)?;
                e.set("a_in", unpack294[0].clone())?;
                e.set("a_out", unpack294[1].clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                        line!(),
                    );
                    {
                        let fun297 = e.get("out")?.attr("append")?;
                        let mut args295 = Vec::new();
                        let mut kw296 = Vec::new();
                        args295.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun300 = e.get("frame")?.attr("prism")?;
                                let mut args298 = Vec::new();
                                let mut kw299 = Vec::new();
                                args298.push({
                                    let mut s = Vec::new();
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("a_in")?);
                                        s.push(e.get("WINDOW_B0")?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("a_out")?);
                                        s.push(e.get("WINDOW_B0")?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("a_out")?);
                                        s.push(e.get("top")?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("a_in")?);
                                        s.push(e.get("top")?);
                                        Val::tuple(s)
                                    });
                                    Val::list(s)
                                });
                                args298.push(binary(
                                    "truediv",
                                    unary("neg", e.get("WINDOW_LEN")?)?,
                                    Val::Float(2.0f64),
                                )?);
                                args298.push(binary(
                                    "truediv",
                                    e.get("WINDOW_LEN")?,
                                    Val::Float(2.0f64),
                                )?);
                                fun300.call(args298, kw299)?
                            }
                        });
                        fun297.call(args295, kw296)?
                    }
                };
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // wing_room
    e.set("wing_room", {
        let params = vec![
            ("frame".into(), None, false),
            ("b_face".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v301 = e.get("b_face")?;
                let v302 = binary(
                    "sub",
                    e.get("SLOT_TOP")?,
                    binary("truediv", e.get("HEADROOM")?, Val::Float(2.0f64))?,
                )?;
                Val::Bool(compare("ge", v301.clone(), v302.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let mut s = Vec::new();
                    Val::list(s)
                });
            }
            let assigned303 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("out", assigned303.clone())?;
            for item304 in {
                let mut s = Vec::new();
                s.push(Val::Int(1i64));
                s.push(unary("neg", Val::Int(1i64))?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("side", item304)?;
                let assigned305 = {
                    let mut s = Vec::new();
                    s.push(binary("mul", e.get("side")?, e.get("RIB_R")?)?);
                    s.push(binary(
                        "mul",
                        e.get("side")?,
                        binary("add", e.get("RIB_R")?, e.get("SLOT_W")?)?,
                    )?);
                    Val::tuple(s)
                };
                let unpack306 = unpack(assigned305.clone(), 2)?;
                e.set("a0", unpack306[0].clone())?;
                e.set("a1", unpack306[1].clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                        line!(),
                    );
                    {
                        let fun309 = e.get("out")?.attr("append")?;
                        let mut args307 = Vec::new();
                        let mut kw308 = Vec::new();
                        args307.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                                line!(),
                            );
                            {
                                let fun312 = e.get("frame")?.attr("prism")?;
                                let mut args310 = Vec::new();
                                let mut kw311 = Vec::new();
                                args310.push({
                                    let mut s = Vec::new();
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("a0")?);
                                        s.push(binary(
                                            "sub",
                                            e.get("b_face")?,
                                            Val::Float(1.0f64),
                                        )?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("a1")?);
                                        s.push(binary(
                                            "sub",
                                            e.get("b_face")?,
                                            Val::Float(1.0f64),
                                        )?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("a1")?);
                                        s.push(e.get("SLOT_TOP")?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("a0")?);
                                        s.push(e.get("SLOT_TOP")?);
                                        Val::tuple(s)
                                    });
                                    Val::list(s)
                                });
                                args310.push(binary(
                                    "truediv",
                                    unary("neg", e.get("WINDOW_LEN")?)?,
                                    Val::Float(2.0f64),
                                )?);
                                args310.push(binary(
                                    "truediv",
                                    e.get("WINDOW_LEN")?,
                                    Val::Float(2.0f64),
                                )?);
                                fun312.call(args310, kw311)?
                            }
                        });
                        fun309.call(args307, kw308)?
                    }
                };
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // wing_strain
    e.set("wing_strain",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned313=binary("truediv",binary("add",e.get("WING_IN")?,e.get("WING_OUT")?)?,Val::Float(2.0f64))?;e.set("rm",assigned313.clone())?;
let assigned314=binary("add",e.get("LIP_B")?,binary("truediv",e.get("LIP_TIP")?,Val::Float(2.0f64))?)?;e.set("load_b",assigned314.clone())?;
let assigned315={let e=e.child();let out316=Val::list(vec![]);for item317 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun320=e.get("range")?;let mut args318=Vec::new();let mut kw319=Vec::new();args318.push(Val::Int(41i64));fun320.call(args318,kw319)?}}.iter()? {e.set("i",item317)?;out316.attr("append")?.call(vec![{let mut s=Vec::new();s.push(binary("mul",e.get("rm")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun323=e.get("math")?.attr("cos")?;let mut args321=Vec::new();let mut kw322=Vec::new();args321.push(binary("mul",unary("neg",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun326=e.get("math")?.attr("radians")?;let mut args324=Vec::new();let mut kw325=Vec::new();args324.push(e.get("CAVITY_DEG")?);fun326.call(args324,kw325)?}})?,binary("sub",Val::Int(1i64),binary("truediv",e.get("i")?,Val::Int(40i64))?)?)?);fun323.call(args321,kw322)?}})?);s.push(binary("mul",e.get("rm")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun329=e.get("math")?.attr("sin")?;let mut args327=Vec::new();let mut kw328=Vec::new();args327.push(binary("mul",unary("neg",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun332=e.get("math")?.attr("radians")?;let mut args330=Vec::new();let mut kw331=Vec::new();args330.push(e.get("CAVITY_DEG")?);fun332.call(args330,kw331)?}})?,binary("sub",Val::Int(1i64),binary("truediv",e.get("i")?,Val::Int(40i64))?)?)?);fun329.call(args327,kw328)?}})?);Val::tuple(s)}],vec![])?;}out316};e.set("pts",assigned315.clone())?;
e.set("pts",binary("add",e.get("pts")?,{let e=e.child();let out333=Val::list(vec![]);for item334 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun337=e.get("range")?;let mut args335=Vec::new();let mut kw336=Vec::new();args335.push(Val::Int(1i64));args335.push(Val::Int(21i64));fun337.call(args335,kw336)?}}.iter()? {e.set("i",item334)?;out333.attr("append")?.call(vec![{let mut s=Vec::new();s.push(e.get("rm")?);s.push(binary("truediv",binary("mul",e.get("load_b")?,e.get("i")?)?,Val::Int(20i64))?);Val::tuple(s)}],vec![])?;}out333})?)?;
let assigned338={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun341=e.get("sum")?;let mut args339=Vec::new();let mut kw340=Vec::new();args339.push({let e=e.child();let out342=Val::list(vec![]);for item343 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun346=e.get("zip")?;let mut args344=Vec::new();let mut kw345=Vec::new();args344.push(e.get("pts")?);args344.push(e.get("pts")?.get(Val::Slice{start:Some(Val::Int(1i64).integer()?),stop:None,step:1})?);fun346.call(args344,kw345)?}}.iter()? {let unpack347=unpack(item343,2)?;e.set("p",unpack347[0].clone())?;e.set("q",unpack347[1].clone())?;out342.attr("append")?.call(vec![binary("mul",binary("pow",binary("sub",e.get("load_b")?,binary("truediv",binary("add",e.get("p")?.get(Val::Int(1i64))?,e.get("q")?.get(Val::Int(1i64))?)?,Val::Float(2.0f64))?)?,Val::Int(2i64))?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun350=e.get("math")?.attr("dist")?;let mut args348=Vec::new();let mut kw349=Vec::new();args348.push(e.get("p")?);args348.push(e.get("q")?);fun350.call(args348,kw349)?}})?],vec![])?;}out342});fun341.call(args339,kw340)?}};e.set("integral",assigned338.clone())?;
let assigned351={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun354=e.get("max")?;let mut args352=Vec::new();let mut kw353=Vec::new();args352.push({let e=e.child();let out355=Val::list(vec![]);for item356 in e.get("pts")?.iter()? {e.set("p",item356)?;out355.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",line!());{let fun359=e.get("abs")?;let mut args357=Vec::new();let mut kw358=Vec::new();args357.push(binary("sub",e.get("load_b")?,e.get("p")?.get(Val::Int(1i64))?)?);fun359.call(args357,kw358)?}}],vec![])?;}out355});fun354.call(args352,kw353)?}};e.set("lever",assigned351.clone())?;
return Ok(binary("truediv",binary("mul",binary("mul",e.get("ENGAGE")?,e.get("lever")?)?,binary("truediv",e.get("WING")?,Val::Float(2.0f64))?)?,e.get("integral")?)?);
Ok(Val::None)})})?;
    // wing_flex_len
    e.set("wing_flex_len", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned360 = binary(
                "truediv",
                binary("add", e.get("WING_IN")?, e.get("WING_OUT")?)?,
                Val::Float(2.0f64),
            )?;
            e.set("rm", assigned360.clone())?;
            return Ok(binary(
                "add",
                binary(
                    "add",
                    binary("mul", e.get("rm")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                            line!(),
                        );
                        {
                            let fun363 = e.get("math")?.attr("radians")?;
                            let mut args361 = Vec::new();
                            let mut kw362 = Vec::new();
                            args361.push(e.get("CAVITY_DEG")?);
                            fun363.call(args361, kw362)?
                        }
                    })?,
                    e.get("LIP_B")?,
                )?,
                binary("truediv", e.get("LIP_TIP")?, Val::Float(2.0f64))?,
            )?);
            Ok(Val::None)
        })
    })?;
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
                let v364 = e.get("name")?;
                let v365 = Val::Str("cq".into());
                Val::Bool(compare("eq", v364.clone(), v365.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.set("cadquery", rt.import_module("cadquery")?)?;
                return Ok(e.get("cadquery")?);
            }
            anyhow::bail!(
                "{}",
                val_string({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_anchor_cap_interface.rs",
                        line!(),
                    );
                    {
                        let fun368 = e.get("AttributeError")?;
                        let mut args366 = Vec::new();
                        let mut kw367 = Vec::new();
                        args366.push({
                            let mut str369 = String::new();
                            str369.push_str("module ");
                            str369.push_str(&format(
                                &builtin_call("repr", vec![e.get("__name__")?], vec![])?,
                                &String::new(),
                            )?);
                            str369.push_str(" has no attribute ");
                            str369.push_str(&format(
                                &builtin_call("repr", vec![e.get("name")?], vec![])?,
                                &String::new(),
                            )?);
                            Val::Str(str369)
                        });
                        fun368.call(args366, kw367)?
                    }
                })?
            );
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
