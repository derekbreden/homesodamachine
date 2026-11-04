//! Above-core shell datums and composition of numeric panel recipes.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("functools", rt.import_module("functools")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("_enclosure_datums", rt.import_module("_enclosure_datums")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
            line!(),
        );
        {
            let fun4 = e.get("_enclosure_datums")?.attr("install")?;
            let mut args2 = Vec::new();
            let mut kw3 = Vec::new();
            fun4.call(args2, kw3)?
        }
    };
    let assigned5 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
            line!(),
        );
        {
            let fun8 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun11 = e.get("Path")?;
                    let mut args9 = Vec::new();
                    let mut kw10 = Vec::new();
                    args9.push(e.get("__file__")?);
                    fun11.call(args9, kw10)?
                }
            }
            .attr("resolve")?;
            let mut args6 = Vec::new();
            let mut kw7 = Vec::new();
            fun8.call(args6, kw7)?
        }
    }
    .attr("parent")?;
    e.set("HERE", assigned5.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
            line!(),
        );
        {
            let fun14 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args12 = Vec::new();
            let mut kw13 = Vec::new();
            args12.push(Val::Int(0i64));
            args12.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun17 = e.get("str")?;
                    let mut args15 = Vec::new();
                    let mut kw16 = Vec::new();
                    args15.push(binary(
                        "truediv",
                        e.get("HERE")?.attr("parents")?.get(Val::Int(2i64))?,
                        Val::Str("manifold-layout".into()),
                    )?);
                    fun17.call(args15, kw16)?
                }
            });
            fun14.call(args12, kw13)?
        }
    };
    e.set("layout", rt.import_module("above_core")?)?;
    let mod18 = rt.import_module("_enclosure_interface")?;
    e.set(
        "flute_depth",
        rt.member("_enclosure_interface", "flute_depth")?,
    )?;
    e.set(
        "rear_identification",
        memoize(
            {
                let params = vec![];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun21 = e.get("sys")?.attr("path")?.attr("insert")?;
                            let mut args19 = Vec::new();
                            let mut kw20 = Vec::new();
                            args19.push(Val::Int(0i64));
                            args19.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                    line!(),
                                );
                                {
                                    let fun24 = e.get("str")?;
                                    let mut args22 = Vec::new();
                                    let mut kw23 = Vec::new();
                                    args22.push(binary(
                                        "truediv",
                                        e.get("HERE")?.attr("parent")?,
                                        Val::Str("rear-identification".into()),
                                    )?);
                                    fun24.call(args22, kw23)?
                                }
                            });
                            fun21.call(args19, kw20)?
                        }
                    };
                    e.set("identification", rt.import_module("rear_identification")?)?;
                    return Ok(e.get("identification")?);
                    Ok(Val::None)
                })
            },
            None,
        ),
    )?; // psu_fastener_plan
    e.set("psu_fastener_plan", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned25 = {
                let mut s = Vec::new();
                s.push(binary("sub", Val::Float(10.0f64), Val::Float(7.7f64))?);
                s.push(binary("sub", Val::Float(10.0f64), Val::Float(5.7f64))?);
                Val::tuple(s)
            };
            e.set("reach", assigned25.clone())?;
            let assigned26 = Val::Float(5.0f64);
            e.set("pilot", assigned26.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("count".into()), Val::Int(4i64))?;
                d.set(Val::Str("screw".into()), Val::Str("M3x10 SHCS".into()))?;
                d.set(Val::Str("screw_length_mm".into()), Val::Float(10.0f64))?;
                d.set(Val::Str("insert".into()), Val::Str("RX-M3Sx4".into()))?;
                d.set(Val::Str("insert_length_mm".into()), Val::Float(4.0f64))?;
                d.set(Val::Str("ear_thickness_range_mm".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Float(5.7f64));
                    s.push(Val::Float(7.7f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("receiving_range_mm".into()), e.get("reach")?)?;
                d.set(Val::Str("pilot_depth_mm".into()), e.get("pilot")?)?;
                d.set(
                    Val::Str("minimum_tip_air_mm".into()),
                    binary("sub", e.get("pilot")?, e.get("reach")?.get(Val::Int(1i64))?)?,
                )?;
                d.set(
                    Val::Str("minimum_blind_backing_mm".into()),
                    binary(
                        "sub",
                        binary(
                            "sub",
                            Val::Float(355.0f64),
                            {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                    line!(),
                                );
                                {
                                    let fun29 = e.get("layout")?.attr("pose")?;
                                    let mut args27 = Vec::new();
                                    let mut kw28 = Vec::new();
                                    args27.push(Val::Str("psu".into()));
                                    fun29.call(args27, kw28)?
                                }
                            }
                            .get(Val::Str("translation_mm".into()))?
                            .get(Val::Int(2i64))?,
                        )?,
                        e.get("pilot")?,
                    )?,
                )?;
                d.set(
                    Val::Str("minimum_fluted_backing_mm".into()),
                    binary(
                        "sub",
                        binary(
                            "sub",
                            Val::Float(355.0f64),
                            {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                    line!(),
                                );
                                {
                                    let fun32 = e.get("layout")?.attr("pose")?;
                                    let mut args30 = Vec::new();
                                    let mut kw31 = Vec::new();
                                    args30.push(Val::Str("psu".into()));
                                    fun32.call(args30, kw31)?
                                }
                            }
                            .get(Val::Str("translation_mm".into()))?
                            .get(Val::Int(2i64))?,
                        )?,
                        e.get("pilot")?,
                    )?,
                )?;
                d.set(
                    Val::Str("maximum_flute_depth_mm".into()),
                    e.get("flute_depth")?,
                )?;
                d.set(Val::Str("boss_radius_mm".into()), Val::Float(5.0f64))?;
                d.set(Val::Str("pilot_radius_mm".into()), Val::Float(2.0f64))?;
                d.set(
                    Val::Str("parent".into()),
                    Val::Str("enclosure-back-top".into()),
                )?;
                d.set(
                    Val::Str("load_retention_qualified".into()),
                    Val::Bool(false),
                )?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // relay_fastener_plan
    e.set("relay_fastener_plan",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned33=Val::Float(2.5f64);e.set("setback",assigned33.clone())?;
let assigned34=binary("sub",binary("sub",Val::Float(8.0f64),Val::Float(1.5f64))?,e.get("setback")?)?;e.set("reach",assigned34.clone())?;
let assigned35=binary("add",e.get("reach")?,Val::Float(1.0f64))?;e.set("pilot",assigned35.clone())?;
return Ok({let d=Val::dict(vec![]);d.set(Val::Str("count".into()),Val::Int(2i64))?;d.set(Val::Str("active_hole_indices".into()),{let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(1i64));Val::tuple(s)})?;d.set(Val::Str("screw".into()),Val::Str("M3x8 SHCS".into()))?;d.set(Val::Str("screw_length_mm".into()),Val::Float(8.0f64))?;d.set(Val::Str("insert".into()),Val::Str("RX-M3Sx4".into()))?;d.set(Val::Str("insert_length_mm".into()),Val::Float(4.0f64))?;d.set(Val::Str("pcb_thickness_mm".into()),Val::Float(1.5f64))?;d.set(Val::Str("receiving_range_mm".into()),{let mut s=Vec::new();s.push(e.get("reach")?);s.push(e.get("reach")?);Val::tuple(s)})?;d.set(Val::Str("pilot_depth_mm".into()),e.get("pilot")?)?;d.set(Val::Str("minimum_tip_air_mm".into()),Val::Float(1.0f64))?;d.set(Val::Str("minimum_blind_backing_mm".into()),binary("add",binary("sub",binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun38=e.get("min")?;let mut args36=Vec::new();let mut kw37=Vec::new();args36.push({let e=e.child();let out39=Val::list(vec![]);for item40 in {let mut s=Vec::new();s.push(Val::Str("relay-1".into()));s.push(Val::Str("relay-2".into()));Val::tuple(s)}.iter()? {e.set("n",item40)?;out39.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun43=e.get("layout")?.attr("pose")?;let mut args41=Vec::new();let mut kw42=Vec::new();args41.push(e.get("n")?);fun43.call(args41,kw42)?}}.get(Val::Str("translation_mm".into()))?.get(Val::Int(0i64))?],vec![])?;}out39});fun38.call(args36,kw37)?}},e.get("setback")?)?,e.get("pilot")?)?,Val::Float(107.5f64))?)?;d.set(Val::Str("minimum_fluted_backing_mm".into()),binary("sub",binary("add",binary("sub",binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun46=e.get("min")?;let mut args44=Vec::new();let mut kw45=Vec::new();args44.push({let e=e.child();let out47=Val::list(vec![]);for item48 in {let mut s=Vec::new();s.push(Val::Str("relay-1".into()));s.push(Val::Str("relay-2".into()));Val::tuple(s)}.iter()? {e.set("n",item48)?;out47.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun51=e.get("layout")?.attr("pose")?;let mut args49=Vec::new();let mut kw50=Vec::new();args49.push(e.get("n")?);fun51.call(args49,kw50)?}}.get(Val::Str("translation_mm".into()))?.get(Val::Int(0i64))?],vec![])?;}out47});fun46.call(args44,kw45)?}},e.get("setback")?)?,e.get("pilot")?)?,Val::Float(107.5f64))?,e.get("flute_depth")?)?)?;d.set(Val::Str("maximum_flute_depth_mm".into()),e.get("flute_depth")?)?;d.set(Val::Str("boss_radius_mm".into()),Val::Float(5.0f64))?;d.set(Val::Str("pilot_radius_mm".into()),Val::Float(2.0f64))?;d.set(Val::Str("insert_face_setback_mm".into()),e.get("setback")?)?;d.set(Val::Str("screw_clearance_radius_mm".into()),Val::Float(1.7f64))?;d.set(Val::Str("pcb_support".into()),Val::Str("Four 3 mm edge ledges support the PCB; the terminal pair captures its top edges. The insert faces stand behind the pin envelope.".into()))?;d.set(Val::Str("parent".into()),Val::Str("enclosure-back-top".into()))?;d.set(Val::Str("load_retention_qualified".into()),Val::Bool(false))?;d});
Ok(Val::None)})})?;
    // wall_mount_datums
    e.set("wall_mount_datums",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned52={let e=e.child();let out53=Val::list(vec![]);for item54 in {let mut s=Vec::new();s.push(Val::Str("meanwell-irm90".into()));s.push(Val::Str("teyleten-relay".into()));Val::tuple(s)}.iter()? {e.set("name",item54)?;out53.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun57=e.get("str")?;let mut args55=Vec::new();let mut kw56=Vec::new();args55.push(binary("truediv",binary("truediv",e.get("HERE")?.attr("parents")?.get(Val::Int(2i64))?,Val::Str("reference".into()))?,e.get("name")?)?);fun57.call(args55,kw56)?}}],vec![])?;}out53};e.get("sys")?.attr("path")?.set(Val::Slice{start:None,stop:Some(Val::Int(0i64).integer()?),step:1},assigned52.clone())?;
e.set("meanwell_irm90",rt.import_module("meanwell_irm90")?)?;
e.set("teyleten_relay",rt.import_module("teyleten_relay")?)?;
let assigned58={let d=Val::dict(vec![]);d};e.set("result",assigned58.clone())?;
for item59 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("psu".into()));s.push(e.get("meanwell_irm90")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun62=e.get("psu_fastener_plan")?;let mut args60=Vec::new();let mut kw61=Vec::new();fun62.call(args60,kw61)?}});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("relay-1".into()));s.push(e.get("teyleten_relay")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun65=e.get("relay_fastener_plan")?;let mut args63=Vec::new();let mut kw64=Vec::new();fun65.call(args63,kw64)?}});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("relay-2".into()));s.push(e.get("teyleten_relay")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun68=e.get("relay_fastener_plan")?;let mut args66=Vec::new();let mut kw67=Vec::new();fun68.call(args66,kw67)?}});Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack69=unpack(item59,3)?;e.set("name",unpack69[0].clone())?;e.set("source",unpack69[1].clone())?;e.set("plan",unpack69[2].clone())?;let assigned70={let mut s=Vec::new();Val::list(s)};e.set("stations",assigned70.clone())?;
let assigned71={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun74=e.get("layout")?.attr("vector")?;let mut args72=Vec::new();let mut kw73=Vec::new();args72.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun77=e.get("layout")?.attr("pose")?;let mut args75=Vec::new();let mut kw76=Vec::new();args75.push(e.get("name")?);fun77.call(args75,kw76)?}}.get(Val::Str("rotation".into()))?);args72.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));Val::tuple(s)});fun74.call(args72,kw73)?}};e.set("axis",assigned71.clone())?;
for item78 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun81=e.get("enumerate")?;let mut args79=Vec::new();let mut kw80=Vec::new();args79.push(e.get("source")?.attr("holes")?);fun81.call(args79,kw80)?}}.iter()? {
let unpack82=unpack(item78,2)?;e.set("index",unpack82[0].clone())?;let unpack83=unpack(unpack82[1].clone(),2)?;e.set("hx",unpack83[0].clone())?;e.set("hy",unpack83[1].clone())?;let assigned84={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun87=e.get("layout")?.attr("point")?;let mut args85=Vec::new();let mut kw86=Vec::new();args85.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun90=e.get("layout")?.attr("pose")?;let mut args88=Vec::new();let mut kw89=Vec::new();args88.push(e.get("name")?);fun90.call(args88,kw89)?}});args85.push({let mut s=Vec::new();s.push(e.get("hx")?);s.push(e.get("hy")?);s.push(Val::Float(0.0f64));Val::tuple(s)});fun87.call(args85,kw86)?}};e.set("point",assigned84.clone())?;
let assigned91={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun94=e.get("tuple")?;let mut args92=Vec::new();let mut kw93=Vec::new();args92.push({let e=e.child();let out95=Val::list(vec![]);for item96 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun99=e.get("zip")?;let mut args97=Vec::new();let mut kw98=Vec::new();args97.push(e.get("point")?);args97.push(e.get("axis")?);fun99.call(args97,kw98)?}}.iter()? {let unpack100=unpack(item96,2)?;e.set("p",unpack100[0].clone())?;e.set("u",unpack100[1].clone())?;out95.attr("append")?.call(vec![binary("sub",e.get("p")?,binary("mul",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun103=e.get("plan")?.attr("get")?;let mut args101=Vec::new();let mut kw102=Vec::new();args101.push(Val::Str("insert_face_setback_mm".into()));args101.push(Val::Float(0.0f64));fun103.call(args101,kw102)?}},e.get("u")?)?)?],vec![])?;}out95});fun94.call(args92,kw93)?}};e.set("face",assigned91.clone())?;
let assigned104=if {let v105=e.get("name")?;let v106=Val::Str("psu".into());Val::Bool(compare("eq",v105.clone(),v106.clone())?.truthy()?)}.truthy()? {{let mut s=Vec::new();s.push(e.get("point")?.get(Val::Int(0i64))?);s.push(e.get("point")?.get(Val::Int(1i64))?);s.push(Val::Float(349.25f64));Val::tuple(s)}} else {{let mut s=Vec::new();s.push(unary("neg",Val::Float(98.52f64))?);s.push(e.get("point")?.get(Val::Int(1i64))?);s.push(e.get("point")?.get(Val::Int(2i64))?);Val::tuple(s)}};e.set("root",assigned104.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun109=e.get("stations")?.attr("append")?;let mut args107=Vec::new();let mut kw108=Vec::new();args107.push({let d=Val::dict(vec![]);d.set(Val::Str("native_hole_index".into()),e.get("index")?)?;d.set(Val::Str("position_world_mm".into()),e.get("point")?)?;d.set(Val::Str("insert_face_world_mm".into()),e.get("face")?)?;d.set(Val::Str("axis_world".into()),e.get("axis")?)?;d.set(Val::Str("threaded".into()),{let v112={let v113=e.get("name")?;let v114=Val::Str("psu".into());Val::Bool(compare("eq",v113.clone(),v114.clone())?.truthy()?)};if v112.truthy()? {v112} else {{let v110=e.get("index")?;let v111=e.get("plan")?.get(Val::Str("active_hole_indices".into()))?;Val::Bool(compare("in",v110.clone(),v111.clone())?.truthy()?)}}})?;d.set(Val::Str("stock_root_world_mm".into()),e.get("root")?)?;d.set(Val::Str("stock_root_world_x_mm".into()),e.get("root")?.get(Val::Int(0i64))?)?;d.set(Val::Str("standoff_mm".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun117=e.get("sum")?;let mut args115=Vec::new();let mut kw116=Vec::new();args115.push({let e=e.child();let out118=Val::list(vec![]);for item119 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun122=e.get("zip")?;let mut args120=Vec::new();let mut kw121=Vec::new();args120.push(e.get("point")?);args120.push(e.get("root")?);args120.push(e.get("axis")?);fun122.call(args120,kw121)?}}.iter()? {let unpack123=unpack(item119,3)?;e.set("p",unpack123[0].clone())?;e.set("r",unpack123[1].clone())?;e.set("u",unpack123[2].clone())?;out118.attr("append")?.call(vec![binary("mul",binary("sub",e.get("p")?,e.get("r")?)?,e.get("u")?)?],vec![])?;}out118});fun117.call(args115,kw116)?}})?;d});fun109.call(args107,kw108)?}};
}
let assigned124={let d=Val::dict(vec![]);dict_extend(&d,e.get("plan")?)?;d.set(Val::Str("stations".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun127=e.get("tuple")?;let mut args125=Vec::new();let mut kw126=Vec::new();args125.push(e.get("stations")?);fun127.call(args125,kw126)?}})?;d};e.get("result")?.set(e.get("name")?,assigned124.clone())?;
}
return Ok(e.get("result")?);
Ok(Val::None)})})?;
    // wall_fastener_bounds
    e.set("wall_fastener_bounds",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned128={let d=Val::dict(vec![]);d};e.set("result",assigned128.clone())?;
for item129 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun132={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun135=e.get("wall_mount_datums")?;let mut args133=Vec::new();let mut kw134=Vec::new();fun135.call(args133,kw134)?}}.attr("items")?;let mut args130=Vec::new();let mut kw131=Vec::new();fun132.call(args130,kw131)?}}.iter()? {
let unpack136=unpack(item129,2)?;e.set("component",unpack136[0].clone())?;e.set("plan",unpack136[1].clone())?;for item137 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun140=e.get("enumerate")?;let mut args138=Vec::new();let mut kw139=Vec::new();args138.push(e.get("plan")?.get(Val::Str("stations".into()))?);args138.push(Val::Int(1i64));fun140.call(args138,kw139)?}}.iter()? {
let unpack141=unpack(item137,2)?;e.set("number",unpack141[0].clone())?;e.set("station",unpack141[1].clone())?;if unary("not",e.get("station")?.get(Val::Str("threaded".into()))?)?.truthy()? {
continue;
}
let assigned142=e.get("station")?.get(Val::Str("axis_world".into()))?;e.set("axis",assigned142.clone())?;
let assigned143={let mut s=Vec::new();s.push(e.get("station")?.get(Val::Str("position_world_mm".into()))?);s.push(e.get("station")?.get(Val::Str("insert_face_world_mm".into()))?);Val::tuple(s)};let unpack144=unpack(assigned143.clone(),2)?;e.set("point",unpack144[0].clone())?;e.set("face",unpack144[1].clone())?;
let assigned145={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun148=e.get("tuple")?;let mut args146=Vec::new();let mut kw147=Vec::new();args146.push({let e=e.child();let out149=Val::list(vec![]);for item150 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun153=e.get("zip")?;let mut args151=Vec::new();let mut kw152=Vec::new();args151.push(e.get("point")?);args151.push(e.get("axis")?);fun153.call(args151,kw152)?}}.iter()? {let unpack154=unpack(item150,2)?;e.set("p",unpack154[0].clone())?;e.set("u",unpack154[1].clone())?;out149.attr("append")?.call(vec![binary("add",e.get("p")?,binary("mul",e.get("u")?,if {let v155=e.get("component")?;let v156=Val::Str("psu".into());Val::Bool(compare("eq",v155.clone(),v156.clone())?.truthy()?)}.truthy()? {Val::Float(6.7f64)} else {Val::Float(1.5f64)})?)?],vec![])?;}out149});fun148.call(args146,kw147)?}};e.set("head",assigned145.clone())?;
for item157 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("screw".into()));s.push(e.get("head")?);s.push(unary("neg",e.get("plan")?.get(Val::Str("screw_length_mm".into()))?)?);s.push(Val::Float(3.0f64));s.push(Val::Float(2.75f64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("insert".into()));s.push(e.get("face")?);s.push(unary("neg",e.get("plan")?.get(Val::Str("insert_length_mm".into()))?)?);s.push(Val::Float(0.0f64));s.push(Val::Float(2.3f64));Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack158=unpack(item157,5)?;e.set("kind",unpack158[0].clone())?;e.set("origin",unpack158[1].clone())?;e.set("lo",unpack158[2].clone())?;e.set("hi",unpack158[3].clone())?;e.set("radius",unpack158[4].clone())?;let assigned159={let e=e.child();let out160=Val::list(vec![]);for item161 in {let mut s=Vec::new();s.push(e.get("lo")?);s.push(e.get("hi")?);Val::tuple(s)}.iter()? {e.set("t",item161)?;out160.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun164=e.get("tuple")?;let mut args162=Vec::new();let mut kw163=Vec::new();args162.push({let e=e.child();let out165=Val::list(vec![]);for item166 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun169=e.get("zip")?;let mut args167=Vec::new();let mut kw168=Vec::new();args167.push(e.get("origin")?);args167.push(e.get("axis")?);fun169.call(args167,kw168)?}}.iter()? {let unpack170=unpack(item166,2)?;e.set("p",unpack170[0].clone())?;e.set("u",unpack170[1].clone())?;out165.attr("append")?.call(vec![binary("add",e.get("p")?,binary("mul",e.get("u")?,e.get("t")?)?)?],vec![])?;}out165});fun164.call(args162,kw163)?}}],vec![])?;}out160};e.set("ends",assigned159.clone())?;
let assigned171={let e=e.child();let out172=Val::list(vec![]);for item173 in e.get("axis")?.iter()? {e.set("u",item173)?;out172.attr("append")?.call(vec![binary("mul",e.get("radius")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun176=e.get("math")?.attr("sqrt")?;let mut args174=Vec::new();let mut kw175=Vec::new();args174.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun179=e.get("max")?;let mut args177=Vec::new();let mut kw178=Vec::new();args177.push(Val::Float(0.0f64));args177.push(binary("sub",Val::Float(1.0f64),binary("mul",e.get("u")?,e.get("u")?)?)?);fun179.call(args177,kw178)?}});fun176.call(args174,kw175)?}})?],vec![])?;}out172};e.set("radial",assigned171.clone())?;
let assigned180={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun183=e.get("tuple")?;let mut args181=Vec::new();let mut kw182=Vec::new();args181.push({let e=e.child();let out184=Val::list(vec![]);for item185 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun188=e.get("range")?;let mut args186=Vec::new();let mut kw187=Vec::new();args186.push(Val::Int(3i64));fun188.call(args186,kw187)?}}.iter()? {e.set("i",item185)?;out184.attr("append")?.call(vec![binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun191=e.get("min")?;let mut args189=Vec::new();let mut kw190=Vec::new();args189.push({let e=e.child();let out192=Val::list(vec![]);for item193 in e.get("ends")?.iter()? {e.set("p",item193)?;out192.attr("append")?.call(vec![e.get("p")?.get(e.get("i")?)?],vec![])?;}out192});fun191.call(args189,kw190)?}},e.get("radial")?.get(e.get("i")?)?)?],vec![])?;}out184});fun183.call(args181,kw182)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun196=e.get("tuple")?;let mut args194=Vec::new();let mut kw195=Vec::new();args194.push({let e=e.child();let out197=Val::list(vec![]);for item198 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun201=e.get("range")?;let mut args199=Vec::new();let mut kw200=Vec::new();args199.push(Val::Int(3i64));fun201.call(args199,kw200)?}}.iter()? {e.set("i",item198)?;out197.attr("append")?.call(vec![binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",line!());{let fun204=e.get("max")?;let mut args202=Vec::new();let mut kw203=Vec::new();args202.push({let e=e.child();let out205=Val::list(vec![]);for item206 in e.get("ends")?.iter()? {e.set("p",item206)?;out205.attr("append")?.call(vec![e.get("p")?.get(e.get("i")?)?],vec![])?;}out205});fun204.call(args202,kw203)?}},e.get("radial")?.get(e.get("i")?)?)?],vec![])?;}out197});fun196.call(args194,kw195)?}});Val::tuple(s)};e.set("bounds",assigned180.clone())?;
let assigned207={let d=Val::dict(vec![]);d.set(Val::Str("component".into()),e.get("component")?)?;d.set(Val::Str("parent".into()),e.get("plan")?.get(Val::Str("parent".into()))?)?;d.set(Val::Str("kind".into()),e.get("kind")?)?;d.set(Val::Str("station".into()),e.get("station")?)?;d.set(Val::Str("plan".into()),e.get("plan")?)?;d.set(Val::Str("bounds_mm".into()),e.get("bounds")?)?;d};e.get("result")?.set({let mut str208=String::new();str208.push_str(&format(&e.get("component")?,&String::new())?);str208.push_str("-");str208.push_str(&format(&e.get("kind")?,&String::new())?);str208.push_str("-");str208.push_str(&format(&e.get("number")?,&String::new())?);Val::Str(str208)},assigned207.clone())?;
}
}
}
return Ok(e.get("result")?);
Ok(Val::None)})})?;
    // in_wall_fastener_lane
    e.set("in_wall_fastener_lane", {
        let params = vec![
            ("name".into(), None, false),
            ("bounds".into(), None, false),
            ("tolerance".into(), Some(Val::Float(1e-05f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned209 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun212 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun215 = e.get("wall_fastener_bounds")?;
                            let mut args213 = Vec::new();
                            let mut kw214 = Vec::new();
                            fun215.call(args213, kw214)?
                        }
                    }
                    .attr("get")?;
                    let mut args210 = Vec::new();
                    let mut kw211 = Vec::new();
                    args210.push(e.get("name")?);
                    fun212.call(args210, kw211)?
                }
            };
            e.set("row", assigned209.clone())?;
            if {
                let v216 = e.get("row")?;
                let v217 = Val::None;
                Val::Bool(compare("is", v216.clone(), v217.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(Val::Bool(false));
            }
            let assigned218 = e.get("row")?.get(Val::Str("bounds_mm".into()))?;
            let unpack219 = unpack(assigned218.clone(), 2)?;
            e.set("lo", unpack219[0].clone())?;
            e.set("hi", unpack219[1].clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun222 = e.get("all")?;
                    let mut args220 = Vec::new();
                    let mut kw221 = Vec::new();
                    args220.push({
                        let e = e.child();
                        let out223 = Val::list(vec![]);
                        for item224 in {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                line!(),
                            );
                            {
                                let fun227 = e.get("range")?;
                                let mut args225 = Vec::new();
                                let mut kw226 = Vec::new();
                                args225.push(Val::Int(3i64));
                                fun227.call(args225, kw226)?
                            }
                        }
                        .iter()?
                        {
                            e.set("i", item224)?;
                            out223.attr("append")?.call(
                                vec![{
                                    let v230 = {
                                        let v231 = e.get("bounds")?.get(e.get("i")?)?;
                                        let v232 = binary(
                                            "sub",
                                            e.get("lo")?.get(e.get("i")?)?,
                                            e.get("tolerance")?,
                                        )?;
                                        Val::Bool(
                                            compare("ge", v231.clone(), v232.clone())?.truthy()?,
                                        )
                                    };
                                    if v230.truthy()? {
                                        {
                                            let v228 = e.get("bounds")?.get(binary(
                                                "add",
                                                e.get("i")?,
                                                Val::Int(3i64),
                                            )?)?;
                                            let v229 = binary(
                                                "add",
                                                e.get("hi")?.get(e.get("i")?)?,
                                                e.get("tolerance")?,
                                            )?;
                                            Val::Bool(
                                                compare("le", v228.clone(), v229.clone())?
                                                    .truthy()?,
                                            )
                                        }
                                    } else {
                                        v230
                                    }
                                }],
                                vec![],
                            )?;
                        }
                        out223
                    });
                    fun222.call(args220, kw221)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // c14_fastener_plan
    e.set("c14_fastener_plan", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("screw_length_mm".into()), Val::Float(10.0f64))?;
                d.set(Val::Str("washer_od_mm".into()), Val::Float(7.0f64))?;
                d.set(Val::Str("washer_thickness_mm".into()), Val::Float(0.5f64))?;
                d.set(Val::Str("flange_thickness_mm".into()), Val::Float(3.25f64))?;
                d.set(Val::Str("insert_length_mm".into()), Val::Float(4.0f64))?;
                d.set(Val::Str("screw_reach_mm".into()), Val::Float(6.25f64))?;
                d.set(Val::Str("pilot_depth_mm".into()), Val::Float(7.25f64))?;
                d.set(Val::Str("boss_depth_mm".into()), Val::Float(10.25f64))?;
                d.set(Val::Str("tip_air_mm".into()), Val::Float(1.0f64))?;
                d.set(Val::Str("backing_mm".into()), Val::Float(3.0f64))?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // keystone_land
    e.set("keystone_land", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("enclosure", rt.import_module("enclosure")?)?;
            let assigned233 = e.get("enclosure")?.attr("_keystone")?;
            e.set("jack", assigned233.clone())?;
            let assigned234 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun237 = e.get("layout")?.attr("specification")?;
                    let mut args235 = Vec::new();
                    let mut kw236 = Vec::new();
                    fun237.call(args235, kw236)?
                }
            }
            .get(Val::Str("rear_wall".into()))?
            .get(Val::Str("dry_openings".into()))?
            .get(Val::Str("keystone".into()))?
            .get(Val::Str("face_center_mm".into()))?;
            let unpack238 = unpack(assigned234.clone(), 3)?;
            e.set("x", unpack238[0].clone())?;
            e.set("y", unpack238[1].clone())?;
            e.set("z", unpack238[2].clone())?;
            let assigned239 = binary(
                "add",
                binary(
                    "add",
                    binary(
                        "truediv",
                        e.get("jack")?.attr("FACE_W")?,
                        Val::Float(2.0f64),
                    )?,
                    e.get("enclosure")?.attr("fits")?.attr("slip")?,
                )?,
                e.get("enclosure")?.attr("wall")?,
            )?;
            e.set("half_w", assigned239.clone())?;
            let assigned240 = binary(
                "add",
                binary(
                    "add",
                    binary(
                        "truediv",
                        e.get("jack")?.attr("FACE_H")?,
                        Val::Float(2.0f64),
                    )?,
                    e.get("enclosure")?.attr("fits")?.attr("slip")?,
                )?,
                e.get("enclosure")?.attr("wall")?,
            )?;
            e.set("half_h", assigned240.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(binary("sub", e.get("x")?, e.get("half_w")?)?);
                s.push(binary("add", e.get("x")?, e.get("half_w")?)?);
                s.push(binary("sub", e.get("y")?, Val::Float(3.0f64))?);
                s.push(binary("add", e.get("y")?, Val::Float(1.0f64))?);
                s.push(binary("sub", e.get("z")?, e.get("half_h")?)?);
                s.push(binary(
                    "add",
                    binary("add", e.get("z")?, e.get("half_h")?)?,
                    e.get("enclosure")?.attr("keystone_ease_shoulder")?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // gas_check_support_datums
    e.set("gas_check_support_datums", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun243 = e.get("sys")?.attr("path")?.attr("insert")?;
                    let mut args241 = Vec::new();
                    let mut kw242 = Vec::new();
                    args241.push(Val::Int(0i64));
                    args241.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun246 = e.get("str")?;
                            let mut args244 = Vec::new();
                            let mut kw245 = Vec::new();
                            args244.push(binary(
                                "truediv",
                                e.get("HERE")?.attr("parents")?.get(Val::Int(2i64))?,
                                Val::Str("reference/neofit-achv44-check".into()),
                            )?);
                            fun246.call(args244, kw245)?
                        }
                    });
                    fun243.call(args241, kw242)?
                }
            };
            e.set("check", rt.import_module("neofit_achv44_check")?)?;
            let assigned247 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun250 = e.get("check")?.attr("bearing_band")?;
                    let mut args248 = Vec::new();
                    let mut kw249 = Vec::new();
                    fun250.call(args248, kw249)?
                }
            };
            let unpack251 = unpack(assigned247.clone(), 3)?;
            e.set("first", unpack251[0].clone())?;
            e.set("last", unpack251[1].clone())?;
            e.set("body_radius", unpack251[2].clone())?;
            let assigned252 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun255 = e.get("check")?.attr("inlet")?;
                    let mut args253 = Vec::new();
                    let mut kw254 = Vec::new();
                    fun255.call(args253, kw254)?
                }
            };
            let unpack256 = unpack(assigned252.clone(), 2)?;
            e.set("inlet", unpack256[0].clone())?;
            e.set("_", unpack256[1].clone())?;
            let assigned257 = {
                let mut s = Vec::new();
                s.push(Val::Float(0.0f64));
                s.push(binary(
                    "add",
                    e.get("inlet")?.get(Val::Int(1i64))?,
                    binary(
                        "truediv",
                        binary("add", e.get("first")?, e.get("last")?)?,
                        Val::Float(2.0f64),
                    )?,
                )?);
                s.push(Val::Float(0.0f64));
                Val::tuple(s)
            };
            e.set("native_centre", assigned257.clone())?;
            let assigned258 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun261 = e.get("layout")?.attr("snapshot_pose")?;
                    let mut args259 = Vec::new();
                    let mut kw260 = Vec::new();
                    args259.push(Val::Str("gas-check".into()));
                    fun261.call(args259, kw260)?
                }
            };
            e.set("frame", assigned258.clone())?;
            let assigned262 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun265 = e.get("layout")?.attr("point")?;
                    let mut args263 = Vec::new();
                    let mut kw264 = Vec::new();
                    args263.push(e.get("frame")?);
                    args263.push(e.get("native_centre")?);
                    fun265.call(args263, kw264)?
                }
            };
            let unpack266 = unpack(assigned262.clone(), 3)?;
            e.set("x", unpack266[0].clone())?;
            e.set("y", unpack266[1].clone())?;
            e.set("_z", unpack266[2].clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("centre_world_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(Val::Float(297.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("axis_world".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun269 = e.get("layout")?.attr("vector")?;
                        let mut args267 = Vec::new();
                        let mut kw268 = Vec::new();
                        args267.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                        args267.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(1.0f64));
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        });
                        fun269.call(args267, kw268)?
                    }
                })?;
                d.set(Val::Str("fixed_band_from_inlet_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("first")?);
                    s.push(e.get("last")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("body_radius_mm".into()), e.get("body_radius")?)?;
                d.set(
                    Val::Str("seat_radius_mm".into()),
                    binary("add", e.get("body_radius")?, Val::Float(0.25f64))?,
                )?;
                d.set(Val::Str("bearing_width_mm".into()), Val::Float(8.0f64))?;
                d.set(Val::Str("outer_half_y_mm".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun272 = e.get("max")?;
                        let mut args270 = Vec::new();
                        let mut kw271 = Vec::new();
                        args270.push(Val::Float(11.0f64));
                        args270.push(binary(
                            "add",
                            binary("add", e.get("body_radius")?, Val::Float(0.25f64))?,
                            Val::Float(3.0f64),
                        )?);
                        fun272.call(args270, kw271)?
                    }
                })?;
                d.set(Val::Str("wall_root_x_mm".into()), Val::Float(98.51f64))?;
                d.set(
                    Val::Str("nominal_radial_air_mm".into()),
                    Val::Float(0.25f64),
                )?;
                d.set(Val::Str("ordinary_wall_mm".into()), Val::Float(3.0f64))?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // valve_seat_datums
    e.set("valve_seat_datums", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("itertools", rt.import_module("itertools")?)?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun275 = e.get("sys")?.attr("path")?.attr("insert")?;
                    let mut args273 = Vec::new();
                    let mut kw274 = Vec::new();
                    args273.push(Val::Int(0i64));
                    args273.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun278 = e.get("str")?;
                            let mut args276 = Vec::new();
                            let mut kw277 = Vec::new();
                            args276.push(binary(
                                "truediv",
                                e.get("HERE")?.attr("parents")?.get(Val::Int(2i64))?,
                                Val::Str("printed-parts/valve-seat".into()),
                            )?);
                            fun278.call(args276, kw277)?
                        }
                    });
                    fun275.call(args273, kw274)?
                }
            };
            e.set("seat", rt.import_module("valve_seat")?)?;
            let assigned279 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("result", assigned279.clone())?;
            for item280 in {
                let mut s = Vec::new();
                s.push(Val::Str("valve-v-a".into()));
                s.push(Val::Str("vk-solenoid".into()));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("name", item280)?;
                let assigned281 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun284 = e.get("layout")?.attr("pose")?;
                        let mut args282 = Vec::new();
                        let mut kw283 = Vec::new();
                        args282.push(e.get("name")?);
                        fun284.call(args282, kw283)?
                    }
                };
                e.set("frame", assigned281.clone())?;
                let assigned285 = {
                    let e = e.child();
                    let out286 = Val::list(vec![]);
                    for item287 in {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun290 = e.get("itertools")?.attr("product")?;
                            let mut args288 = Vec::new();
                            let mut kw289 = Vec::new();
                            args288.push({
                                let mut s = Vec::new();
                                s.push(unary("neg", e.get("seat")?.attr("seat_half_x")?)?);
                                s.push(e.get("seat")?.attr("seat_half_x")?);
                                Val::tuple(s)
                            });
                            args288.push({
                                let mut s = Vec::new();
                                s.push(unary("neg", e.get("seat")?.attr("seat_half_y")?)?);
                                s.push(e.get("seat")?.attr("seat_half_y")?);
                                Val::tuple(s)
                            });
                            args288.push({
                                let mut s = Vec::new();
                                s.push(binary(
                                    "sub",
                                    e.get("seat")?.attr("socket_floor_z")?,
                                    e.get("seat")?.attr("wall")?,
                                )?);
                                s.push(e.get("seat")?.attr("seat_top_z")?);
                                Val::tuple(s)
                            });
                            fun290.call(args288, kw289)?
                        }
                    }
                    .iter()?
                    {
                        e.set("point", item287)?;
                        out286.attr("append")?.call(
                            vec![{
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                    line!(),
                                );
                                {
                                    let fun293 = e.get("layout")?.attr("point")?;
                                    let mut args291 = Vec::new();
                                    let mut kw292 = Vec::new();
                                    args291.push(e.get("frame")?);
                                    args291.push(e.get("point")?);
                                    fun293.call(args291, kw292)?
                                }
                            }],
                            vec![],
                        )?;
                    }
                    out286
                };
                e.set("corners", assigned285.clone())?;
                let assigned294 = {
                    let e = e.child();
                    let out295 = Val::list(vec![]);
                    for item296 in {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun299 = e.get("range")?;
                            let mut args297 = Vec::new();
                            let mut kw298 = Vec::new();
                            args297.push(Val::Int(3i64));
                            fun299.call(args297, kw298)?
                        }
                    }
                    .iter()?
                    {
                        e.set("i", item296)?;
                        out295.attr("append")?.call(
                            vec![{
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                    line!(),
                                );
                                {
                                    let fun302 = e.get("min")?;
                                    let mut args300 = Vec::new();
                                    let mut kw301 = Vec::new();
                                    args300.push({
                                        let e = e.child();
                                        let out303 = Val::list(vec![]);
                                        for item304 in e.get("corners")?.iter()? {
                                            e.set("point", item304)?;
                                            out303.attr("append")?.call(
                                                vec![e.get("point")?.get(e.get("i")?)?],
                                                vec![],
                                            )?;
                                        }
                                        out303
                                    });
                                    fun302.call(args300, kw301)?
                                }
                            }],
                            vec![],
                        )?;
                    }
                    out295
                };
                e.set("low", assigned294.clone())?;
                let assigned305 = {
                    let e = e.child();
                    let out306 = Val::list(vec![]);
                    for item307 in {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun310 = e.get("range")?;
                            let mut args308 = Vec::new();
                            let mut kw309 = Vec::new();
                            args308.push(Val::Int(3i64));
                            fun310.call(args308, kw309)?
                        }
                    }
                    .iter()?
                    {
                        e.set("i", item307)?;
                        out306.attr("append")?.call(
                            vec![{
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                    line!(),
                                );
                                {
                                    let fun313 = e.get("max")?;
                                    let mut args311 = Vec::new();
                                    let mut kw312 = Vec::new();
                                    args311.push({
                                        let e = e.child();
                                        let out314 = Val::list(vec![]);
                                        for item315 in e.get("corners")?.iter()? {
                                            e.set("point", item315)?;
                                            out314.attr("append")?.call(
                                                vec![e.get("point")?.get(e.get("i")?)?],
                                                vec![],
                                            )?;
                                        }
                                        out314
                                    });
                                    fun313.call(args311, kw312)?
                                }
                            }],
                            vec![],
                        )?;
                    }
                    out306
                };
                e.set("high", assigned305.clone())?;
                if {
                    let v316 = e
                        .get("frame")?
                        .get(Val::Str("translation_mm".into()))?
                        .get(Val::Int(0i64))?;
                    let v317 = Val::Float(0.0f64);
                    Val::Bool(compare("lt", v316.clone(), v317.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned318 = unary("neg", Val::Float(98.51f64))?;
                    e.get("low")?.set(Val::Int(0i64), assigned318.clone())?;
                } else {
                    let assigned319 = Val::Float(98.51f64);
                    e.get("high")?.set(Val::Int(0i64), assigned319.clone())?;
                }
                let assigned320 = {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("parent".into()),
                        Val::Str("enclosure-back-top".into()),
                    )?;
                    d.set(Val::Str("stock_min_world_mm".into()), e.get("low")?)?;
                    d.set(Val::Str("stock_max_world_mm".into()), e.get("high")?)?;
                    d.set(
                        Val::Str("socket_diameter_mm".into()),
                        e.get("seat")?.attr("socket_diameter")?,
                    )?;
                    d.set(
                        Val::Str("socket_floor_backing_mm".into()),
                        e.get("seat")?.attr("wall")?,
                    )?;
                    d.set(Val::Str("frame".into()), e.get("frame")?)?;
                    d.set(
                        Val::Str("interface".into()),
                        Val::Str(
                            "Shared valve_seat V69 four blind sockets and open port channel".into(),
                        ),
                    )?;
                    d
                };
                e.get("result")?.set(e.get("name")?, assigned320.clone())?;
            }
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    let assigned321 = Val::None;
    e.set("box", assigned321.clone())?;
    e.set("rectangle", assigned321.clone())?;
    e.set("ycylinder", assigned321.clone())?;
    e.set("zcylinder", assigned321.clone())?;
    e.set("rear_well_tower", assigned321.clone())?;
    e.set("wall_bosses", assigned321.clone())?;
    e.set("valve_seats", assigned321.clone())?;
    e.set("c14_rear_cutters", assigned321.clone())?;
    e.set("keystone_rear_geometry", assigned321.clone())?;
    e.set("fluid_supports", assigned321.clone())?;
    e.set("stacked_well_towers", assigned321.clone())?;
    // rear_geometry
    e.set("rear_geometry", {
        let params = vec![
            ("piece".into(), None, false),
            (
                "holds".into(),
                Some({
                    let mut s = Vec::new();
                    Val::tuple(s)
                }),
                false,
            ),
            ("keep_clear".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned322 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun325 = e.get("layout")?.attr("specification")?;
                    let mut args323 = Vec::new();
                    let mut kw324 = Vec::new();
                    fun325.call(args323, kw324)?
                }
            }
            .get(Val::Str("rear_wall".into()))?;
            e.set("plan", assigned322.clone())?;
            let assigned326 = e
                .get("plan")?
                .get(Val::Str("interior_panel_relief".into()))?;
            e.set("relief", assigned326.clone())?;
            let assigned327 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun330 = e.get("piece")?.attr("cut")?;
                    let mut args328 = Vec::new();
                    let mut kw329 = Vec::new();
                    args328.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun333 = e.get("rectangle")?;
                            let mut args331 = Vec::new();
                            let mut kw332 = Vec::new();
                            args331.push(e.get("relief")?);
                            fun333.call(args331, kw332)?
                        }
                    });
                    fun330.call(args328, kw329)?
                }
            };
            e.set("piece", assigned327.clone())?;
            for item334 in e.get("plan")?.get(Val::Str("wet_ports".into()))?.iter()? {
                e.set("port", item334)?;
                let assigned335 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun338 = e.get("piece")?.attr("cut")?;
                        let mut args336 = Vec::new();
                        let mut kw337 = Vec::new();
                        args336.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                line!(),
                            );
                            {
                                let fun341 = e.get("ycylinder")?;
                                let mut args339 = Vec::new();
                                let mut kw340 = Vec::new();
                                args339.push(binary(
                                    "truediv",
                                    e.get("port")?.get(Val::Str("bore_diameter_mm".into()))?,
                                    Val::Int(2i64),
                                )?);
                                args339.push(e.get("port")?.get(Val::Str("center_x_mm".into()))?);
                                args339.push(e.get("port")?.get(Val::Str("center_z_mm".into()))?);
                                args339.push(Val::Float(458.0f64));
                                args339.push(Val::Float(472.3f64));
                                fun341.call(args339, kw340)?
                            }
                        });
                        fun338.call(args336, kw337)?
                    }
                };
                e.set("piece", assigned335.clone())?;
            }
            let assigned342 = e
                .get("plan")?
                .get(Val::Str("dry_openings".into()))?
                .get(Val::Str("c14".into()))?;
            e.set("c14", assigned342.clone())?;
            let assigned343 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun346 = e.get("layout")?.attr("pose")?;
                    let mut args344 = Vec::new();
                    let mut kw345 = Vec::new();
                    args344.push(Val::Str("c14-inlet".into()));
                    fun346.call(args344, kw345)?
                }
            }
            .get(Val::Str("translation_mm".into()))?;
            let unpack347 = unpack(assigned343.clone(), 3)?;
            e.set("x", unpack347[0].clone())?;
            e.set("y", unpack347[1].clone())?;
            e.set("z", unpack347[2].clone())?;
            let assigned348 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun351 = e.get("piece")?.attr("cut")?;
                    let mut args349 = Vec::new();
                    let mut kw350 = Vec::new();
                    args349.extend(
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                line!(),
                            );
                            {
                                let fun354 = e.get("c14_rear_cutters")?;
                                let mut args352 = Vec::new();
                                let mut kw353 = Vec::new();
                                fun354.call(args352, kw353)?
                            }
                        }
                        .iter()?,
                    );
                    fun351.call(args349, kw350)?
                }
            };
            e.set("piece", assigned348.clone())?;
            let assigned355 = binary("sub", e.get("y")?, Val::Float(3.25f64))?;
            e.set("seat_y", assigned355.clone())?;
            let assigned356 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun359 = e.get("c14_fastener_plan")?;
                    let mut args357 = Vec::new();
                    let mut kw358 = Vec::new();
                    fun359.call(args357, kw358)?
                }
            };
            e.set("fasteners", assigned356.clone())?;
            for item360 in {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    unary("neg", e.get("c14")?.get(Val::Str("mount_pitch_mm".into()))?)?,
                    Val::Int(2i64),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("c14")?.get(Val::Str("mount_pitch_mm".into()))?,
                    Val::Int(2i64),
                )?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("dx", item360)?;
                let assigned361 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun364 = e.get("piece")?.attr("fuse")?;
                        let mut args362 = Vec::new();
                        let mut kw363 = Vec::new();
                        args362.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                line!(),
                            );
                            {
                                let fun367 = e.get("ycylinder")?;
                                let mut args365 = Vec::new();
                                let mut kw366 = Vec::new();
                                args365.push(Val::Float(5.0f64));
                                args365.push(binary("add", e.get("x")?, e.get("dx")?)?);
                                args365.push(e.get("z")?);
                                args365.push(binary(
                                    "sub",
                                    e.get("seat_y")?,
                                    e.get("fasteners")?.get(Val::Str("boss_depth_mm".into()))?,
                                )?);
                                args365.push(e.get("seat_y")?);
                                fun367.call(args365, kw366)?
                            }
                        });
                        fun364.call(args362, kw363)?
                    }
                };
                e.set("piece", assigned361.clone())?;
                let assigned368 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun371 = e.get("piece")?.attr("cut")?;
                        let mut args369 = Vec::new();
                        let mut kw370 = Vec::new();
                        args369.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                line!(),
                            );
                            {
                                let fun374 = e.get("ycylinder")?;
                                let mut args372 = Vec::new();
                                let mut kw373 = Vec::new();
                                args372.push(Val::Float(2.0f64));
                                args372.push(binary("add", e.get("x")?, e.get("dx")?)?);
                                args372.push(e.get("z")?);
                                args372.push(binary(
                                    "sub",
                                    e.get("seat_y")?,
                                    e.get("fasteners")?.get(Val::Str("pilot_depth_mm".into()))?,
                                )?);
                                args372.push(binary("add", e.get("seat_y")?, Val::Float(0.01f64))?);
                                fun374.call(args372, kw373)?
                            }
                        });
                        fun371.call(args369, kw370)?
                    }
                };
                e.set("piece", assigned368.clone())?;
            }
            let assigned375 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun378 = e.get("keystone_rear_geometry")?;
                    let mut args376 = Vec::new();
                    let mut kw377 = Vec::new();
                    args376.push(e.get("holds")?);
                    args376.push(e.get("keep_clear")?);
                    fun378.call(args376, kw377)?
                }
            };
            let unpack379 = unpack(assigned375.clone(), 3)?;
            e.set("stock", unpack379[0].clone())?;
            e.set("cutter", unpack379[1].clone())?;
            e.set("catches", unpack379[2].clone())?;
            let assigned380 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun383 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun386 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                    line!(),
                                );
                                {
                                    let fun389 = e.get("piece")?.attr("fuse")?;
                                    let mut args387 = Vec::new();
                                    let mut kw388 = Vec::new();
                                    args387.push(e.get("stock")?);
                                    fun389.call(args387, kw388)?
                                }
                            }
                            .attr("cut")?;
                            let mut args384 = Vec::new();
                            let mut kw385 = Vec::new();
                            args384.push(e.get("cutter")?);
                            fun386.call(args384, kw385)?
                        }
                    }
                    .attr("fuse")?;
                    let mut args381 = Vec::new();
                    let mut kw382 = Vec::new();
                    args381.push(e.get("catches")?);
                    fun383.call(args381, kw382)?
                }
            };
            e.set("piece", assigned380.clone())?;
            return Ok(e.get("piece")?);
            Ok(Val::None)
        })
    })?;
    // apply
    e.set("apply", {
        let params = vec![
            ("piece".into(), None, false),
            ("box_spec".into(), None, false),
            ("y_side".into(), None, false),
            ("z_side".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v390 = e.get("z_side")?;
                let v391 = Val::Str("top".into());
                Val::Bool(compare("ne", v390.clone(), v391.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("piece")?);
            }
            e.set("above_core_wiring", rt.import_module("above_core_wiring")?)?;
            let assigned392 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun395 = e.get("above_core_wiring")?.attr("shell_features")?;
                    let mut args393 = Vec::new();
                    let mut kw394 = Vec::new();
                    args393.push(binary("add", e.get("y_side")?, Val::Str("-top".into()))?);
                    fun395.call(args393, kw394)?
                }
            };
            e.set("wiring", assigned392.clone())?;
            let assigned396 = e.get("wiring")?.get(Val::Str("add".into()))?;
            e.set("stock", assigned396.clone())?;
            if {
                let v399 = {
                    let v400 = e.get("stock")?;
                    let v401 = Val::None;
                    Val::Bool(compare("is_not", v400.clone(), v401.clone())?.truthy()?)
                };
                if v399.truthy()? {
                    {
                        let v397 = e.get("y_side")?;
                        let v398 = Val::Str("front".into());
                        Val::Bool(compare("eq", v397.clone(), v398.clone())?.truthy()?)
                    }
                } else {
                    v399
                }
            }
            .truthy()?
            {
                let assigned402 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun405 = e.get("stacked_well_towers")?;
                        let mut args403 = Vec::new();
                        let mut kw404 = Vec::new();
                        args403.push(e.get("stock")?);
                        args403.push(e.get("box_spec")?.attr("inner")?);
                        fun405.call(args403, kw404)?
                    }
                };
                e.set("stock", assigned402.clone())?;
            }
            if {
                let v408 = {
                    let v409 = e.get("stock")?;
                    let v410 = Val::None;
                    Val::Bool(compare("is_not", v409.clone(), v410.clone())?.truthy()?)
                };
                if v408.truthy()? {
                    {
                        let v406 = e.get("y_side")?;
                        let v407 = Val::Str("back".into());
                        Val::Bool(compare("eq", v406.clone(), v407.clone())?.truthy()?)
                    }
                } else {
                    v408
                }
            }
            .truthy()?
            {
                e.set("enclosure", rt.import_module("enclosure")?)?;
                let assigned411 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun414 = e.get("rear_well_tower")?;
                        let mut args412 = Vec::new();
                        let mut kw413 = Vec::new();
                        args412.push(e.get("stock")?);
                        args412.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                line!(),
                            );
                            {
                                let fun417 = e.get("enclosure")?.attr("back_top_ceiling_face")?;
                                let mut args415 = Vec::new();
                                let mut kw416 = Vec::new();
                                fun417.call(args415, kw416)?
                            }
                        });
                        fun414.call(args412, kw413)?
                    }
                };
                e.set("stock", assigned411.clone())?;
            }
            if {
                let v418 = e.get("stock")?;
                let v419 = Val::None;
                Val::Bool(compare("is_not", v418.clone(), v419.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned420 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun423 = e.get("piece")?.attr("fuse")?;
                        let mut args421 = Vec::new();
                        let mut kw422 = Vec::new();
                        args421.push(e.get("stock")?);
                        fun423.call(args421, kw422)?
                    }
                };
                e.set("piece", assigned420.clone())?;
            }
            if {
                let v424 = e.get("wiring")?.get(Val::Str("cut".into()))?;
                let v425 = Val::None;
                Val::Bool(compare("is_not", v424.clone(), v425.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned426 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun429 = e.get("piece")?.attr("cut")?;
                        let mut args427 = Vec::new();
                        let mut kw428 = Vec::new();
                        args427.push(e.get("wiring")?.get(Val::Str("cut".into()))?);
                        fun429.call(args427, kw428)?
                    }
                };
                e.set("piece", assigned426.clone())?;
            }
            if {
                let v430 = e.get("y_side")?;
                let v431 = Val::Str("back".into());
                Val::Bool(compare("ne", v430.clone(), v431.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("piece")?);
            }
            let assigned432 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun435 = e.get("rear_geometry")?;
                    let mut args433 = Vec::new();
                    let mut kw434 = Vec::new();
                    args433.push(e.get("piece")?);
                    args433.push({
                        let v436 = e.get("box_spec")?.attr("pack")?.attr("core_holds")?;
                        if v436.truthy()? {
                            v436
                        } else {
                            {
                                let mut s = Vec::new();
                                Val::tuple(s)
                            }
                        }
                    });
                    args433.push(e.get("wiring")?.get(Val::Str("cut".into()))?);
                    fun435.call(args433, kw434)?
                }
            };
            e.set("piece", assigned432.clone())?;
            let assigned437 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun440 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun443 = e.get("rear_identification")?;
                            let mut args441 = Vec::new();
                            let mut kw442 = Vec::new();
                            fun443.call(args441, kw442)?
                        }
                    }
                    .attr("apply")?;
                    let mut args438 = Vec::new();
                    let mut kw439 = Vec::new();
                    args438.push(e.get("piece")?);
                    fun440.call(args438, kw439)?
                }
            };
            e.set("piece", assigned437.clone())?;
            let assigned444 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun447 = e.get("wall_bosses")?;
                    let mut args445 = Vec::new();
                    let mut kw446 = Vec::new();
                    fun447.call(args445, kw446)?
                }
            };
            let unpack448 = unpack(assigned444.clone(), 2)?;
            e.set("bosses", unpack448[0].clone())?;
            e.set("holes", unpack448[1].clone())?;
            for item449 in e.get("bosses")?.iter()? {
                e.set("feature", item449)?;
                let assigned450 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun453 = e.get("piece")?.attr("fuse")?;
                        let mut args451 = Vec::new();
                        let mut kw452 = Vec::new();
                        args451.push(e.get("feature")?);
                        fun453.call(args451, kw452)?
                    }
                };
                e.set("piece", assigned450.clone())?;
            }
            for item454 in e.get("holes")?.iter()? {
                e.set("hole", item454)?;
                let assigned455 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun458 = e.get("piece")?.attr("cut")?;
                        let mut args456 = Vec::new();
                        let mut kw457 = Vec::new();
                        args456.push(e.get("hole")?);
                        fun458.call(args456, kw457)?
                    }
                };
                e.set("piece", assigned455.clone())?;
            }
            for item459 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun462 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun465 = e.get("valve_seats")?;
                            let mut args463 = Vec::new();
                            let mut kw464 = Vec::new();
                            fun465.call(args463, kw464)?
                        }
                    }
                    .attr("values")?;
                    let mut args460 = Vec::new();
                    let mut kw461 = Vec::new();
                    fun462.call(args460, kw461)?
                }
            }
            .iter()?
            {
                e.set("feature", item459)?;
                let assigned466 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun469 = e.get("piece")?.attr("fuse")?;
                        let mut args467 = Vec::new();
                        let mut kw468 = Vec::new();
                        args467.push(e.get("feature")?);
                        fun469.call(args467, kw468)?
                    }
                };
                e.set("piece", assigned466.clone())?;
            }
            for item470 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun473 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                            line!(),
                        );
                        {
                            let fun476 = e.get("fluid_supports")?;
                            let mut args474 = Vec::new();
                            let mut kw475 = Vec::new();
                            fun476.call(args474, kw475)?
                        }
                    }
                    .attr("values")?;
                    let mut args471 = Vec::new();
                    let mut kw472 = Vec::new();
                    fun473.call(args471, kw472)?
                }
            }
            .iter()?
            {
                e.set("feature", item470)?;
                let assigned477 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                        line!(),
                    );
                    {
                        let fun480 = e.get("piece")?.attr("fuse")?;
                        let mut args478 = Vec::new();
                        let mut kw479 = Vec::new();
                        args478.push(e.get("feature")?);
                        fun480.call(args478, kw479)?
                    }
                };
                e.set("piece", assigned477.clone())?;
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                    line!(),
                );
                {
                    let fun483 = e.get("piece")?.attr("cut")?;
                    let mut args481 = Vec::new();
                    let mut kw482 = Vec::new();
                    args481.extend(
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_above_core_shell.rs",
                                line!(),
                            );
                            {
                                let fun486 = e.get("c14_rear_cutters")?;
                                let mut args484 = Vec::new();
                                let mut kw485 = Vec::new();
                                fun486.call(args484, kw485)?
                            }
                        }
                        .iter()?,
                    );
                    fun483.call(args481, kw482)?
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
