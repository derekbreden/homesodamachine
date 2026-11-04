//! Live numeric construction of the relaxed and installed lower pump retainer.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("contextlib")?;
    e.set("contextmanager", rt.member("contextlib", "contextmanager")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    // _stack
    e.set("_stack",{let params=vec![("graph".into(),None,false),("case".into(),None,false),("start".into(),None,false),("steps".into(),None,false),("profiles".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned3=binary("add",binary("mul",Val::Int(4i64),binary("add",e.get("case")?.attr("arc_segments")?,Val::Int(1i64))?)?,Val::Int(2i64))?;e.set("collapsed",assigned3.clone())?;
let assigned4=binary("add",e.get("collapsed")?,Val::Int(2i64))?;e.set("split",assigned4.clone())?;
let assigned5=binary("mul",Val::Int(2i64),binary("add",e.get("case")?.attr("arc_segments")?,Val::Int(1i64))?)?;e.set("at",assigned5.clone())?;
// aligned
e.set("aligned",{let params=vec![("profile".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned6={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun9=e.get("list")?;let mut args7=Vec::new();let mut kw8=Vec::new();args7.push(e.get("profile")?);fun9.call(args7,kw8)?}};e.set("profile",assigned6.clone())?;
if {let v13={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun12=e.get("len")?;let mut args10=Vec::new();let mut kw11=Vec::new();args10.push(e.get("profile")?);fun12.call(args10,kw11)?}};let v14=e.get("split")?;Val::Bool(compare("eq",v13.clone(),v14.clone())?.truthy()?)}.truthy()? {
return Ok(e.get("profile")?);
}
if {let v18={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun17=e.get("len")?;let mut args15=Vec::new();let mut kw16=Vec::new();args15.push(e.get("profile")?);fun17.call(args15,kw16)?}};let v19=e.get("collapsed")?;Val::Bool(compare("ne",v18.clone(),v19.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun22=e.get("ValueError")?;let mut args20=Vec::new();let mut kw21=Vec::new();args20.push(Val::Str("the native pump skirt has an unknown correspondence".into()));fun22.call(args20,kw21)?}})?);
}
return Ok(binary("add",binary("add",binary("add",e.get("profile")?.get(Val::Slice{start:None,stop:Some(binary("add",e.get("at")?,Val::Int(1i64))?.integer()?),step:1})?,{let mut s=Vec::new();s.push(e.get("profile")?.get(e.get("at")?)?);Val::list(s)})?,e.get("profile")?.get(Val::Slice{start:Some(binary("add",e.get("at")?,Val::Int(1i64))?.integer()?),stop:None,step:1})?)?,{let mut s=Vec::new();s.push(e.get("profile")?.get(unary("neg",Val::Int(1i64))?)?);Val::list(s)})?);
Ok(Val::None)})})?;
let assigned23=e.get("start")?;e.set("z",assigned23.clone())?;
let assigned24={let mut s=Vec::new();s.push({let e=e.child();let out25=Val::list(vec![]);for item26 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun29=e.get("aligned")?;let mut args27=Vec::new();let mut kw28=Vec::new();args27.push(e.get("profiles")?.get(Val::Int(0i64))?);fun29.call(args27,kw28)?}}.iter()? {let unpack30=unpack(item26,2)?;e.set("x",unpack30[0].clone())?;e.set("y",unpack30[1].clone())?;out25.attr("append")?.call(vec![{let mut s=Vec::new();s.push(binary("add",e.get("case")?.attr("center_x")?,e.get("x")?)?);s.push(binary("add",e.get("case")?.attr("center_y")?,e.get("y")?)?);s.push(e.get("z")?);Val::tuple(s)}],vec![])?;}out25});Val::list(s)};e.set("sections",assigned24.clone())?;
for item31 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun34=e.get("zip")?;let mut args32=Vec::new();let mut kw33=Vec::new();args32.push(e.get("steps")?);args32.push(e.get("profiles")?.get(Val::Slice{start:Some(Val::Int(1i64).integer()?),stop:None,step:1})?);fun34.call(args32,kw33)?}}.iter()? {
let unpack35=unpack(item31,2)?;e.set("dz",unpack35[0].clone())?;e.set("profile",unpack35[1].clone())?;e.set("z",binary("add",e.get("z")?,e.get("dz")?)?)?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun38=e.get("sections")?.attr("append")?;let mut args36=Vec::new();let mut kw37=Vec::new();args36.push({let e=e.child();let out39=Val::list(vec![]);for item40 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun43=e.get("aligned")?;let mut args41=Vec::new();let mut kw42=Vec::new();args41.push(e.get("profile")?);fun43.call(args41,kw42)?}}.iter()? {let unpack44=unpack(item40,2)?;e.set("x",unpack44[0].clone())?;e.set("y",unpack44[1].clone())?;out39.attr("append")?.call(vec![{let mut s=Vec::new();s.push(binary("add",e.get("case")?.attr("center_x")?,e.get("x")?)?);s.push(binary("add",e.get("case")?.attr("center_y")?,e.get("y")?)?);s.push(e.get("z")?);Val::tuple(s)}],vec![])?;}out39});fun38.call(args36,kw37)?}};
}
let assigned45={let e=e.child();let out46=Val::list(vec![]);for item47 in e.get("sections")?.iter()? {e.set("section",item47)?;for item48 in e.get("section")?.iter()? {e.set("p",item48)?;out46.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out46};e.set("points",assigned45.clone())?;
let assigned49={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun52=e.get("tuple")?;let mut args50=Vec::new();let mut kw51=Vec::new();args50.push({let e=e.child();let out53=Val::list(vec![]);for item54 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun57=e.get("range")?;let mut args55=Vec::new();let mut kw56=Vec::new();args55.push(Val::Int(3i64));fun57.call(args55,kw56)?}}.iter()? {e.set("axis",item54)?;for item58 in {let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun61=e.get("min")?;let mut args59=Vec::new();let mut kw60=Vec::new();args59.push({let e=e.child();let out62=Val::list(vec![]);for item63 in e.get("points")?.iter()? {e.set("p",item63)?;out62.attr("append")?.call(vec![e.get("p")?.get(e.get("axis")?)?],vec![])?;}out62});fun61.call(args59,kw60)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun66=e.get("max")?;let mut args64=Vec::new();let mut kw65=Vec::new();args64.push({let e=e.child();let out67=Val::list(vec![]);for item68 in e.get("points")?.iter()? {e.set("p",item68)?;out67.attr("append")?.call(vec![e.get("p")?.get(e.get("axis")?)?],vec![])?;}out67});fun66.call(args64,kw65)?}});Val::tuple(s)}.iter()? {e.set("v",item58)?;out53.attr("append")?.call(vec![e.get("v")?],vec![])?;}}out53});fun52.call(args50,kw51)?}};e.set("bounds",assigned49.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun71=e.get("graph")?.attr("add")?;let mut args69=Vec::new();let mut kw70=Vec::new();args69.push(Val::Str("ruled-stack".into()));kw70.push(("sections".into(),e.get("sections")?));kw70.push(("bounds".into(),e.get("bounds")?));fun71.call(args69,kw70)?}});
Ok(Val::None)})})?;
    // _profile_prism
    e.set("_profile_prism", {
        let params = vec![
            ("graph".into(), None, false),
            ("case".into(), None, false),
            ("profile".into(), None, false),
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
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                    line!(),
                );
                {
                    let fun74 = e.get("graph")?.attr("prism")?;
                    let mut args72 = Vec::new();
                    let mut kw73 = Vec::new();
                    args72.push(Val::Int(2i64));
                    args72.push(e.get("z0")?);
                    args72.push(e.get("z1")?);
                    args72.push({
                        let e = e.child();
                        let out75 = Val::list(vec![]);
                        for item76 in e.get("profile")?.iter()? {
                            let unpack77 = unpack(item76, 2)?;
                            e.set("x", unpack77[0].clone())?;
                            e.set("y", unpack77[1].clone())?;
                            out75.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "add",
                                        e.get("case")?.attr("center_x")?,
                                        e.get("x")?,
                                    )?);
                                    s.push(binary(
                                        "add",
                                        e.get("case")?.attr("center_y")?,
                                        e.get("y")?,
                                    )?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                        out75
                    });
                    fun74.call(args72, kw73)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _case_drop_well
    e.set("_case_drop_well",{let params=vec![("graph".into(),None,false),("case".into(),None,false),("air".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned78=binary("sub",e.get("case")?.attr("skirt_wall")?,e.get("air")?)?;e.set("offset",assigned78.clone())?;
let assigned79={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun82=e.get("_stack")?;let mut args80=Vec::new();let mut kw81=Vec::new();args80.push(e.get("graph")?);args80.push(e.get("case")?);args80.push(Val::Float(0.0f64));args80.push(e.get("case")?.attr("skirt_z_steps")?);args80.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun85=e.get("case")?.attr("_skirt_profile_set")?;let mut args83=Vec::new();let mut kw84=Vec::new();args83.push(e.get("offset")?);fun85.call(args83,kw84)?}});fun82.call(args80,kw81)?}};e.set("skirt",assigned79.clone())?;
let assigned86={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun89=e.get("_stack")?;let mut args87=Vec::new();let mut kw88=Vec::new();args87.push(e.get("graph")?);args87.push(e.get("case")?);args87.push(e.get("case")?.attr("skirt_bottom_z")?);args87.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun92=e.get("case")?.attr("lower_z_steps")?;let mut args90=Vec::new();let mut kw91=Vec::new();fun92.call(args90,kw91)?}});args87.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun95=e.get("case")?.attr("_lower_profile_set")?;let mut args93=Vec::new();let mut kw94=Vec::new();args93.push(e.get("offset")?);fun95.call(args93,kw94)?}});fun89.call(args87,kw88)?}};e.set("lower",assigned86.clone())?;
let assigned96={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun99=e.get("skirt")?.attr("fuse")?;let mut args97=Vec::new();let mut kw98=Vec::new();args97.push(e.get("lower")?);fun99.call(args97,kw98)?}};e.set("solid",assigned96.clone())?;
for item100 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun103=e.get("zip")?;let mut args101=Vec::new();let mut kw102=Vec::new();args101.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun106=e.get("case")?.attr("_stack_levels")?;let mut args104=Vec::new();let mut kw105=Vec::new();fun106.call(args104,kw105)?}});args101.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun109=e.get("case")?.attr("_stack_profiles")?;let mut args107=Vec::new();let mut kw108=Vec::new();args107.push(e.get("offset")?);fun109.call(args107,kw108)?}});fun103.call(args101,kw102)?}}.iter()? {
let unpack110=unpack(item100,2)?;e.set("z",unpack110[0].clone())?;e.set("profile",unpack110[1].clone())?;if {let v111=e.get("z")?;let v112=unary("neg",Val::Float(1e-09f64))?;Val::Bool(compare("lt",v111.clone(),v112.clone())?.truthy()?)}.truthy()? {
let assigned113={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun116=e.get("solid")?.attr("fuse")?;let mut args114=Vec::new();let mut kw115=Vec::new();args114.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun119=e.get("_profile_prism")?;let mut args117=Vec::new();let mut kw118=Vec::new();args117.push(e.get("graph")?);args117.push(e.get("case")?);args117.push(e.get("profile")?);args117.push(e.get("z")?);args117.push(Val::Float(0.0f64));fun119.call(args117,kw118)?}});fun116.call(args114,kw115)?}};e.set("solid",assigned113.clone())?;
}
}
return Ok(e.get("solid")?);
Ok(Val::None)})})?;
    // _lower_well
    e.set("_lower_well",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("pump_trays".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned120={let mut s=Vec::new();s.push(e.get("shell")?.attr("_tray")?);s.push(e.get("shell")?.attr("_tray")?.attr("_pc")?);Val::tuple(s)};let unpack121=unpack(assigned120.clone(),2)?;e.set("tray",unpack121[0].clone())?;e.set("case",unpack121[1].clone())?;
let assigned122=e.get("shell")?.attr("cap_pump_air")?;e.set("air",assigned122.clone())?;
let assigned123=binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun126=e.get("shell")?.attr("pump_skirt_support_z")?;let mut args124=Vec::new();let mut kw125=Vec::new();args124.push(e.get("pump_trays")?);fun126.call(args124,kw125)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun129=e.get("min")?;let mut args127=Vec::new();let mut kw128=Vec::new();args127.push({let e=e.child();let out130=Val::list(vec![]);for item131 in e.get("pump_trays")?.iter()? {let unpack132=unpack(item131,3)?;e.set("_x",unpack132[0].clone())?;e.set("_y",unpack132[1].clone())?;e.set("z",unpack132[2].clone())?;out130.attr("append")?.call(vec![e.get("z")?],vec![])?;}out130});fun129.call(args127,kw128)?}})?;e.set("support",assigned123.clone())?;
let assigned133=binary("sub",e.get("case")?.attr("skirt_wall")?,e.get("air")?)?;e.set("offset",assigned133.clone())?;
let assigned134={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun137=e.get("case")?.attr("_skirt_profile_set")?;let mut args135=Vec::new();let mut kw136=Vec::new();args135.push(e.get("offset")?);fun137.call(args135,kw136)?}}.get(Val::Int(1i64))?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun140=e.get("case")?.attr("_skirt_profile_set")?;let mut args138=Vec::new();let mut kw139=Vec::new();args138.push(e.get("offset")?);fun140.call(args138,kw139)?}}.get(Val::Int(3i64))?);Val::tuple(s)};let unpack141=unpack(assigned134.clone(),2)?;e.set("upper",unpack141[0].clone())?;e.set("lower",unpack141[1].clone())?;
let assigned142=binary("sub",e.get("case")?.attr("lower_cap_top_z")?,e.get("case")?.attr("overcut")?)?;e.set("bottom",assigned142.clone())?;
// mask
e.set("mask",{let params=vec![("z0".into(),None,false),("z1".into(),None,false),("y0".into(),None,false),("y1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun145=e.get("graph")?.attr("box")?;let mut args143=Vec::new();let mut kw144=Vec::new();args143.push(binary("sub",e.get("case")?.attr("center_x")?,e.get("case")?.attr("cutter_half_extent")?)?);args143.push(binary("add",e.get("case")?.attr("center_x")?,e.get("case")?.attr("cutter_half_extent")?)?);args143.push(binary("add",e.get("case")?.attr("center_y")?,e.get("y0")?)?);args143.push(binary("add",e.get("case")?.attr("center_y")?,e.get("y1")?)?);args143.push(e.get("z0")?);args143.push(e.get("z1")?);fun145.call(args143,kw144)?}});
Ok(Val::None)})})?;
let assigned146={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun149={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun152={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun155=e.get("_case_drop_well")?;let mut args153=Vec::new();let mut kw154=Vec::new();args153.push(e.get("graph")?);args153.push(e.get("case")?);args153.push(e.get("air")?);fun155.call(args153,kw154)?}}.attr("intersect")?;let mut args150=Vec::new();let mut kw151=Vec::new();args150.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun158=e.get("_profile_prism")?;let mut args156=Vec::new();let mut kw157=Vec::new();args156.push(e.get("graph")?);args156.push(e.get("case")?);args156.push(e.get("lower")?);args156.push(e.get("bottom")?);args156.push(e.get("support")?);fun158.call(args156,kw157)?}});fun152.call(args150,kw151)?}}.attr("intersect")?;let mut args147=Vec::new();let mut kw148=Vec::new();args147.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun161=e.get("mask")?;let mut args159=Vec::new();let mut kw160=Vec::new();args159.push(e.get("bottom")?);args159.push(e.get("support")?);args159.extend(e.get("tray")?.attr("skirt_body_open_y_bounds")?.iter()?);fun161.call(args159,kw160)?}});fun149.call(args147,kw148)?}};e.set("lower_room",assigned146.clone())?;
let assigned162={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun165={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun168={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun171=e.get("_profile_prism")?;let mut args169=Vec::new();let mut kw170=Vec::new();args169.push(e.get("graph")?);args169.push(e.get("case")?);args169.push(e.get("upper")?);args169.push(e.get("support")?);args169.push(Val::Float(0.0f64));fun171.call(args169,kw170)?}}.attr("fuse")?;let mut args166=Vec::new();let mut kw167=Vec::new();args166.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun174=e.get("_profile_prism")?;let mut args172=Vec::new();let mut kw173=Vec::new();args172.push(e.get("graph")?);args172.push(e.get("case")?);args172.push(e.get("lower")?);args172.push(e.get("support")?);args172.push(Val::Float(0.0f64));fun174.call(args172,kw173)?}});fun168.call(args166,kw167)?}}.attr("intersect")?;let mut args163=Vec::new();let mut kw164=Vec::new();args163.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun177=e.get("mask")?;let mut args175=Vec::new();let mut kw176=Vec::new();args175.push(e.get("support")?);args175.push(Val::Float(0.0f64));args175.push(unary("neg",e.get("case")?.attr("cutter_half_extent")?)?);args175.push(e.get("tray")?.attr("skirt_open_y_max")?);fun177.call(args175,kw176)?}});fun165.call(args163,kw164)?}};e.set("upper_room",assigned162.clone())?;
let assigned178={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun181={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun184=e.get("upper_room")?.attr("fuse")?;let mut args182=Vec::new();let mut kw183=Vec::new();args182.push(e.get("lower_room")?);fun184.call(args182,kw183)?}}.attr("translate")?;let mut args179=Vec::new();let mut kw180=Vec::new();args179.push({let mut s=Vec::new();s.push(unary("neg",e.get("case")?.attr("center_x")?)?);s.push(unary("neg",e.get("case")?.attr("center_y")?)?);s.push(Val::Float(0.0f64));Val::tuple(s)});fun181.call(args179,kw180)?}};e.set("room",assigned178.clone())?;
let assigned185={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun188=e.get("tray")?.attr("outlet_fore_miter")?;let mut args186=Vec::new();let mut kw187=Vec::new();args186.push(e.get("air")?);fun188.call(args186,kw187)?}};let unpack189=unpack(assigned185.clone(),4)?;e.set("body_half",unpack189[0].clone())?;e.set("y0",unpack189[1].clone())?;e.set("open_half",unpack189[2].clone())?;e.set("_",unpack189[3].clone())?;
if {let v190=e.get("open_half")?;let v191=binary("add",e.get("body_half")?,Val::Float(1e-09f64))?;Val::Bool(compare("gt",v190.clone(),v191.clone())?.truthy()?)}.truthy()? {
let assigned192={let mut s=Vec::new();s.push(e.get("body_half")?);s.push(e.get("tray")?.attr("outlet_axis_z")?);Val::tuple(s)};let unpack193=unpack(assigned192.clone(),2)?;e.set("y1",unpack193[0].clone())?;e.set("z0",unpack193[1].clone())?;
let assigned194={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun197=e.get("room")?.attr("fuse")?;let mut args195=Vec::new();let mut kw196=Vec::new();args195.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun200=e.get("graph")?.attr("box")?;let mut args198=Vec::new();let mut kw199=Vec::new();args198.push(unary("neg",e.get("open_half")?)?);args198.push(unary("neg",e.get("body_half")?)?);args198.push(e.get("y0")?);args198.push(e.get("y1")?);args198.push(e.get("z0")?);args198.push(Val::Float(0.0f64));fun200.call(args198,kw199)?}});args195.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun203=e.get("graph")?.attr("box")?;let mut args201=Vec::new();let mut kw202=Vec::new();args201.push(e.get("body_half")?);args201.push(e.get("open_half")?);args201.push(e.get("y0")?);args201.push(e.get("y1")?);args201.push(e.get("z0")?);args201.push(Val::Float(0.0f64));fun203.call(args201,kw202)?}});fun197.call(args195,kw196)?}};e.set("room",assigned194.clone())?;
}
return Ok(e.get("room")?);
Ok(Val::None)})})?;
    // _wing
    e.set("_wing", {
        let params = vec![
            ("shell".into(), None, false),
            ("graph".into(), None, false),
            ("box".into(), None, false),
            ("side".into(), None, false),
            ("spread".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned204 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                    line!(),
                );
                {
                    let fun207 = e
                        .get("shell")?
                        .attr("_fixed_pump_mount")?
                        .attr("wing_profile")?;
                    let mut args205 = Vec::new();
                    let mut kw206 = Vec::new();
                    args205.push(e.get("shell")?);
                    args205.push(e.get("box")?);
                    args205.push(e.get("side")?);
                    args205.push(e.get("spread")?);
                    fun207.call(args205, kw206)?
                }
            };
            e.set("profile", assigned204.clone())?;
            let assigned208 = {
                let e = e.child();
                let out209 = Val::list(vec![]);
                for item210 in e.get("profile")?.get(Val::Str("segments".into()))?.iter()? {
                    e.set("segment", item210)?;
                    for item211 in {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                            line!(),
                        );
                        {
                            let fun214 = e.get("segment")?.attr("values")?;
                            let mut args212 = Vec::new();
                            let mut kw213 = Vec::new();
                            fun214.call(args212, kw213)?
                        }
                    }
                    .iter()?
                    {
                        e.set("controls", item211)?;
                        for item215 in e.get("controls")?.iter()? {
                            e.set("p", item215)?;
                            out209.attr("append")?.call(vec![e.get("p")?], vec![])?;
                        }
                    }
                }
                out209
            };
            e.set("points", assigned208.clone())?;
            let assigned216 = {
                let mut s = Vec::new();
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                        line!(),
                    );
                    {
                        let fun219 = e.get("min")?;
                        let mut args217 = Vec::new();
                        let mut kw218 = Vec::new();
                        args217.push({
                            let e = e.child();
                            let out220 = Val::list(vec![]);
                            for item221 in e.get("points")?.iter()? {
                                e.set("p", item221)?;
                                out220
                                    .attr("append")?
                                    .call(vec![e.get("p")?.get(Val::Int(0i64))?], vec![])?;
                            }
                            out220
                        });
                        fun219.call(args217, kw218)?
                    }
                });
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                        line!(),
                    );
                    {
                        let fun224 = e.get("max")?;
                        let mut args222 = Vec::new();
                        let mut kw223 = Vec::new();
                        args222.push({
                            let e = e.child();
                            let out225 = Val::list(vec![]);
                            for item226 in e.get("points")?.iter()? {
                                e.set("p", item226)?;
                                out225
                                    .attr("append")?
                                    .call(vec![e.get("p")?.get(Val::Int(0i64))?], vec![])?;
                            }
                            out225
                        });
                        fun224.call(args222, kw223)?
                    }
                });
                s.extend(e.get("profile")?.get(Val::Str("span".into()))?.iter()?);
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                        line!(),
                    );
                    {
                        let fun229 = e.get("min")?;
                        let mut args227 = Vec::new();
                        let mut kw228 = Vec::new();
                        args227.push({
                            let e = e.child();
                            let out230 = Val::list(vec![]);
                            for item231 in e.get("points")?.iter()? {
                                e.set("p", item231)?;
                                out230
                                    .attr("append")?
                                    .call(vec![e.get("p")?.get(Val::Int(1i64))?], vec![])?;
                            }
                            out230
                        });
                        fun229.call(args227, kw228)?
                    }
                });
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                        line!(),
                    );
                    {
                        let fun234 = e.get("max")?;
                        let mut args232 = Vec::new();
                        let mut kw233 = Vec::new();
                        args232.push({
                            let e = e.child();
                            let out235 = Val::list(vec![]);
                            for item236 in e.get("points")?.iter()? {
                                e.set("p", item236)?;
                                out235
                                    .attr("append")?
                                    .call(vec![e.get("p")?.get(Val::Int(1i64))?], vec![])?;
                            }
                            out235
                        });
                        fun234.call(args232, kw233)?
                    }
                });
                Val::tuple(s)
            };
            e.set("bounds", assigned216.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                    line!(),
                );
                {
                    let fun239 = e.get("graph")?.attr("add")?;
                    let mut args237 = Vec::new();
                    let mut kw238 = Vec::new();
                    args237.push(Val::Str("bezier-prism".into()));
                    kw238.push(("axis".into(), Val::Int(1i64)));
                    kw238.extend(keyword_items(e.get("profile")?)?);
                    kw238.push(("bounds".into(), e.get("bounds")?));
                    fun239.call(args237, kw238)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_leaves",{let params=vec![("shell".into(),None,false),("graph".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;
            let enter_e=e.clone();let enter_rt=rt.clone();
            let enter=Val::function(move|_,_|{let e=enter_e.clone();let rt=enter_rt.clone();let _frame=rt.frame(&e);
        let assigned240=e.get("shell")?.attr("_fixed_pump_mount")?;e.set("fixed",assigned240.clone())?;
let assigned241={let mut s=Vec::new();s.push(e.get("shell")?.attr("_pump_lower_well")?);s.push(e.get("fixed")?.attr("_wing")?);Val::tuple(s)};let unpack242=unpack(assigned241.clone(),2)?;e.set("original_well",unpack242[0].clone())?;e.set("original_wing",unpack242[1].clone())?;
let assigned243=e.get("shell")?.attr("_ycyl")?;e.set("original_cylinder",assigned243.clone())?;
let assigned244={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun247=e.get("shell")?.attr("_tray")?.attr("outlet_under_tangent")?;let mut args245=Vec::new();let mut kw246=Vec::new();args245.push(e.get("shell")?.attr("cap_pump_air")?);fun247.call(args245,kw246)?}};let unpack248=unpack(assigned244.clone(),4)?;e.set("_seam",unpack248[0].clone())?;e.set("_wall",unpack248[1].clone())?;e.set("tangent_x",unpack248[2].clone())?;e.set("tangent_z",unpack248[3].clone())?;
let assigned249=binary("sub",e.get("tangent_z")?,e.get("shell")?.attr("_tray")?.attr("outlet_axis_z")?)?;e.set("dz",assigned249.clone())?;
let assigned250={let e=e.child();let out251=Val::list(vec![]);for item252 in {let mut s=Vec::new();s.push(unary("neg",Val::Float(1.0f64))?);s.push(Val::Float(1.0f64));Val::tuple(s)}.iter()? {e.set("side",item252)?;out251.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun255=e.get("math")?.attr("atan2")?;let mut args253=Vec::new();let mut kw254=Vec::new();args253.push(e.get("dz")?);args253.push(binary("mul",e.get("side")?,e.get("tangent_x")?)?);fun255.call(args253,kw254)?}}],vec![])?;}out251};e.set("stations",assigned250.clone())?;
// outlet_cylinder
e.set("outlet_cylinder",{let params=vec![("radius".into(),None,false),("x".into(),None,false),("z".into(),None,false),("y0".into(),None,false),("y1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun258=e.get("graph")?.attr("add")?;let mut args256=Vec::new();let mut kw257=Vec::new();args256.push(Val::Str("cylinder".into()));kw257.push(("axis".into(),Val::Int(1i64)));kw257.push(("radius".into(),e.get("radius")?));kw257.push(("centre".into(),{let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("z")?);Val::tuple(s)}));kw257.push(("span".into(),{let mut s=Vec::new();s.push(e.get("y0")?);s.push(e.get("y1")?);Val::tuple(s)}));kw257.push(("stations".into(),e.get("stations")?));kw257.push(("bounds".into(),{let mut s=Vec::new();s.push(binary("sub",e.get("x")?,e.get("radius")?)?);s.push(binary("add",e.get("x")?,e.get("radius")?)?);s.push(e.get("y0")?);s.push(e.get("y1")?);s.push(binary("sub",e.get("z")?,e.get("radius")?)?);s.push(binary("add",e.get("z")?,e.get("radius")?)?);Val::tuple(s)}));fun258.call(args256,kw257)?}});
Ok(Val::None)})})?;
let assigned259={let params=vec![("trays".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun262=e.get("_lower_well")?;let mut args260=Vec::new();let mut kw261=Vec::new();args260.push(e.get("shell")?);args260.push(e.get("graph")?);args260.push(e.get("trays")?);fun262.call(args260,kw261)?}});
Ok(Val::None)})};e.get("shell")?.setattr("_pump_lower_well",assigned259.clone())?;
let assigned263={let params=vec![("e".into(),None,false),("box".into(),None,false),("side".into(),None,false),("spread".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",line!());{let fun266=e.get("_wing")?;let mut args264=Vec::new();let mut kw265=Vec::new();args264.push(e.get("e")?);args264.push(e.get("graph")?);args264.push(e.get("box")?);args264.push(e.get("side")?);args264.push(e.get("spread")?);fun266.call(args264,kw265)?}});
Ok(Val::None)})};e.get("fixed")?.setattr("_wing",assigned263.clone())?;
let assigned267=e.get("outlet_cylinder")?;e.get("shell")?.setattr("_ycyl",assigned267.clone())?;
Ok(Val::None)});
            let exit_e=e.clone();let exit_rt=rt.clone();
            let exit=Val::function(move|_,_|{let e=exit_e.clone();let rt=exit_rt.clone();let _frame=rt.frame(&e);
        let assigned268={let mut s=Vec::new();s.push(e.get("original_well")?);s.push(e.get("original_wing")?);Val::tuple(s)};let unpack269=unpack(assigned268.clone(),2)?;e.get("shell")?.setattr("_pump_lower_well",unpack269[0].clone())?;e.get("fixed")?.setattr("_wing",unpack269[1].clone())?;
let assigned270=e.get("original_cylinder")?;e.get("shell")?.setattr("_ycyl",assigned270.clone())?;
Ok(Val::None)});Ok(context(enter,exit))})})?; // numbers
    e.set("numbers", {
        let params = vec![
            ("shell".into(), None, false),
            ("box".into(), None, false),
            ("seated".into(), Some(Val::Bool(false)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod271 = rt.import_module("_enclosure_panel")?;
            e.set("_Graph", rt.member("_enclosure_panel", "_Graph")?)?;
            e.set("_record", rt.member("_enclosure_panel", "_record")?)?;
            let mod272 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            let assigned273 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                    line!(),
                );
                {
                    let fun276 = e.get("_Graph")?;
                    let mut args274 = Vec::new();
                    let mut kw275 = Vec::new();
                    fun276.call(args274, kw275)?
                }
            };
            e.set("graph", assigned273.clone())?;
            let context277 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                    line!(),
                );
                {
                    let fun280 = e.get("_record")?;
                    let mut args278 = Vec::new();
                    let mut kw279 = Vec::new();
                    args278.push(e.get("shell")?);
                    args278.push(e.get("graph")?);
                    args278.push(Val::None);
                    fun280.call(args278, kw279)?
                }
            };
            context277.attr("__enter__")?.call(vec![], vec![])?;
            let context281 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                    line!(),
                );
                {
                    let fun284 = e.get("_leaves")?;
                    let mut args282 = Vec::new();
                    let mut kw283 = Vec::new();
                    args282.push(e.get("shell")?);
                    args282.push(e.get("graph")?);
                    fun284.call(args282, kw283)?
                }
            };
            context281.attr("__enter__")?.call(vec![], vec![])?;
            let context_result289 = (|| -> Result<Flow> {
                let assigned285 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                        line!(),
                    );
                    {
                        let fun288 = e.get("shell")?.attr("build_pump_retainer")?;
                        let mut args286 = Vec::new();
                        let mut kw287 = Vec::new();
                        args286.push(e.get("box")?);
                        kw287.push(("seated".into(), e.get("seated")?));
                        fun288.call(args286, kw287)?
                    }
                };
                e.set("result", assigned285.clone())?;
                Ok(Flow::Continue)
            })();
            context281
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            context277
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result289? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
            }
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("panel".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                        line!(),
                    );
                    {
                        let fun292 = e.get("graph")?.attr("document")?;
                        let mut args290 = Vec::new();
                        let mut kw291 = Vec::new();
                        args290.push(e.get("result")?);
                        fun292.call(args290, kw291)?
                    }
                })?;
                d.set(Val::Str("color".into()), {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                        line!(),
                    );
                    {
                        let fun295 = e.get("linear")?;
                        let mut args293 = Vec::new();
                        let mut kw294 = Vec::new();
                        args293.push(
                            e.get("shell")?
                                .attr("PIECE_COLORS")?
                                .get(Val::Str("pump-retainer".into()))?,
                        );
                        fun295.call(args293, kw294)?
                    }
                })?;
                d.set(
                    Val::Str("name".into()),
                    if e.get("seated")?.truthy()? {
                        Val::Str("enclosure-pump-retainer-seated".into())
                    } else {
                        Val::Str("enclosure-pump-retainer".into())
                    },
                )?;
                d.set(Val::Str("seated".into()), e.get("seated")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // cut
    e.set("cut", {
        let params = vec![
            ("shell".into(), None, false),
            ("box".into(), None, false),
            ("directory".into(), None, false),
            ("seated".into(), Some(Val::Bool(false)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            let assigned296 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                    line!(),
                );
                {
                    let fun299 = e.get("Path")?;
                    let mut args297 = Vec::new();
                    let mut kw298 = Vec::new();
                    args297.push(e.get("directory")?);
                    fun299.call(args297, kw298)?
                }
            };
            e.set("directory", assigned296.clone())?;
            let assigned300 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                    line!(),
                );
                {
                    let fun303 = e.get("_rust_part")?.attr("cut")?;
                    let mut args301 = Vec::new();
                    let mut kw302 = Vec::new();
                    args301.push(Val::Str("enclosure-shell".into()));
                    args301.push(Val::Str("enclosure-pump-retainer".into()));
                    args301.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                            line!(),
                        );
                        {
                            let fun306 = e.get("numbers")?;
                            let mut args304 = Vec::new();
                            let mut kw305 = Vec::new();
                            args304.push(e.get("shell")?);
                            args304.push(e.get("box")?);
                            kw305.push(("seated".into(), e.get("seated")?));
                            fun306.call(args304, kw305)?
                        }
                    });
                    args301.push(e.get("directory")?);
                    kw302.push((
                        "numbers_name".into(),
                        if e.get("seated")?.truthy()? {
                            Val::Str("enclosure-pump-retainer-seated".into())
                        } else {
                            Val::None
                        },
                    ));
                    fun303.call(args301, kw302)?
                }
            };
            e.set("said", assigned300.clone())?;
            if unary("not", e.get("seated")?)?.truthy()? {
                let mod307 = rt.import_module("_enclosure_presentation")?;
                e.set(
                    "print_payload",
                    rt.member("_enclosure_presentation", "print_payload")?,
                )?;
                let assigned308 = binary(
                    "truediv",
                    e.get("directory")?,
                    Val::Str("enclosure-pump-retainer.step".into()),
                )?;
                e.set("step", assigned308.clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_pump_retainer.rs",
                        line!(),
                    );
                    {
                        let fun311 = e.get("print_payload")?;
                        let mut args309 = Vec::new();
                        let mut kw310 = Vec::new();
                        args309.push(e.get("step")?);
                        kw310.push(("check_print".into(), Val::Bool(false)));
                        fun311.call(args309, kw310)?
                    }
                };
            }
            return Ok(e.get("said")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
