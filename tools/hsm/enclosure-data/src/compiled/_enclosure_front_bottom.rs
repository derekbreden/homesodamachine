//! Live front-bottom construction and its independent exterior print field.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    // _vents
    e.set("_vents",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("solid".into(),None,false),("inner".into(),None,false),("outer".into(),None,false),("airway".into(),None,false),("y0".into(),None,false),("y1".into(),None,false),("z0".into(),None,false),("z1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if unary("not",e.get("airway")?)?.truthy()? {
return Ok(e.get("solid")?);
}
let assigned2=e.get("airway")?;let unpack3=unpack(assigned2.clone(),4)?;e.set("ay0",unpack3[0].clone())?;e.set("ay1",unpack3[1].clone())?;e.set("az0",unpack3[2].clone())?;e.set("az1",unpack3[3].clone())?;
if unary("not",{let v7={let v8=e.get("y0")?;let v9=binary("truediv",binary("add",e.get("ay0")?,e.get("ay1")?)?,Val::Int(2i64))?;let v10=e.get("y1")?;Val::Bool(compare("le",v8.clone(),v9.clone())?.truthy()? && compare("le",v9.clone(),v10.clone())?.truthy()?)};if v7.truthy()? {{let v4=e.get("z0")?;let v5=binary("truediv",binary("add",e.get("az0")?,e.get("az1")?)?,Val::Int(2i64))?;let v6=e.get("z1")?;Val::Bool(compare("le",v4.clone(),v5.clone())?.truthy()? && compare("le",v5.clone(),v6.clone())?.truthy()?)}} else {v7}})?.truthy()? {
return Ok(e.get("solid")?);
}
let assigned11={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun14=e.get("shell")?.attr("vent_segments")?;let mut args12=Vec::new();let mut kw13=Vec::new();args12.push(e.get("airway")?);fun14.call(args12,kw13)?}};e.set("courses",assigned11.clone())?;
let assigned15={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun18=e.get("shell")?.attr("vent_band")?;let mut args16=Vec::new();let mut kw17=Vec::new();args16.push(e.get("airway")?);fun18.call(args16,kw17)?}};e.set("band",assigned15.clone())?;
let assigned19=binary("truediv",e.get("shell")?.attr("reeding")?.attr("pierce_width")?,Val::Int(2i64))?;e.set("half",assigned19.clone())?;
let assigned20={let mut s=Vec::new();s.push({let mut s=Vec::new();Val::list(s)});s.push({let mut s=Vec::new();Val::list(s)});Val::tuple(s)};let unpack21=unpack(assigned20.clone(),2)?;e.set("columns",unpack21[0].clone())?;e.set("cutters",unpack21[1].clone())?;
for item22 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun25=e.get("shell")?.attr("vent_grooves")?;let mut args23=Vec::new();let mut kw24=Vec::new();args23.push(e.get("outer")?);args23.push(e.get("airway")?);fun25.call(args23,kw24)?}}.iter()? {
let unpack26=unpack(item22,2)?;e.set("side",unpack26[0].clone())?;e.set("y",unpack26[1].clone())?;let assigned27={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun30=e.get("shell")?.attr("vent_flank_face")?;let mut args28=Vec::new();let mut kw29=Vec::new();args28.push(e.get("side")?);fun30.call(args28,kw29)?}};e.set("face",assigned27.clone())?;
let assigned31={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun34=e.get("sorted")?;let mut args32=Vec::new();let mut kw33=Vec::new();args32.push({let mut s=Vec::new();s.push(binary("sub",e.get("face")?,binary("mul",e.get("side")?,e.get("shell")?.attr("cond_vent_probe")?)?)?);s.push(binary("sub",e.get("face")?,binary("mul",e.get("side")?,e.get("shell")?.attr("stated_bound_tol")?)?)?);Val::tuple(s)});fun34.call(args32,kw33)?}};let unpack35=unpack(assigned31.clone(),2)?;e.set("xa",unpack35[0].clone())?;e.set("xb",unpack35[1].clone())?;
let assigned36={let mut s=Vec::new();Val::list(s)};e.set("indices",assigned36.clone())?;
for item37 in e.get("courses")?.iter()? {
let unpack38=unpack(item37,2)?;e.set("lo",unpack38[0].clone())?;e.set("hi",unpack38[1].clone())?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun41=e.get("indices")?.attr("append")?;let mut args39=Vec::new();let mut kw40=Vec::new();args39.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun44=e.get("len")?;let mut args42=Vec::new();let mut kw43=Vec::new();args42.push(e.get("cutters")?);fun44.call(args42,kw43)?}});fun41.call(args39,kw40)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun47=e.get("cutters")?.attr("append")?;let mut args45=Vec::new();let mut kw46=Vec::new();args45.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun50=e.get("shell")?.attr("_vent_cutter")?;let mut args48=Vec::new();let mut kw49=Vec::new();args48.push(e.get("outer")?);args48.push(e.get("side")?);args48.push(e.get("y")?);args48.push(e.get("lo")?);args48.push(e.get("hi")?);fun50.call(args48,kw49)?}});fun47.call(args45,kw46)?}};
}
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun53=e.get("columns")?.attr("append")?;let mut args51=Vec::new();let mut kw52=Vec::new();args51.push({let d=Val::dict(vec![]);d.set(Val::Str("side".into()),e.get("side")?)?;d.set(Val::Str("probe".into()),{let mut s=Vec::new();s.push(e.get("xa")?);s.push(e.get("xb")?);s.push(binary("sub",binary("sub",e.get("y")?,e.get("half")?)?,e.get("shell")?.attr("cond_vent_clear")?)?);s.push(binary("add",binary("add",e.get("y")?,e.get("half")?)?,e.get("shell")?.attr("cond_vent_clear")?)?);s.push(binary("sub",e.get("band")?.get(Val::Int(0i64))?,e.get("shell")?.attr("cond_vent_clear")?)?);s.push(binary("add",e.get("band")?.get(Val::Int(1i64))?,e.get("shell")?.attr("cond_vent_clear")?)?);Val::tuple(s)})?;d.set(Val::Str("cutters".into()),e.get("indices")?)?;d});fun53.call(args51,kw52)?}};
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun56=e.get("graph")?.attr("add")?;let mut args54=Vec::new();let mut kw55=Vec::new();args54.push(Val::Str("flank-vents".into()));args54.push({let mut s=Vec::new();s.push(e.get("solid")?.attr("index")?);s.extend({let e=e.child();let out57=Val::list(vec![]);for item58 in e.get("cutters")?.iter()? {e.set("shape",item58)?;out57.attr("append")?.call(vec![e.get("shape")?.attr("index")?],vec![])?;}out57}.iter()?);Val::list(s)});kw55.push(("columns".into(),e.get("columns")?));kw55.push(("courses".into(),e.get("courses")?));kw55.push(("clearance".into(),e.get("shell")?.attr("cond_vent_clear")?));kw55.push(("tolerance".into(),e.get("shell")?.attr("stated_bound_tol")?));kw55.push(("island_min".into(),e.get("shell")?.attr("cond_vent_island_min")?));kw55.push(("bounds".into(),e.get("solid")?.attr("bounds")?));fun56.call(args54,kw55)?}});
Ok(Val::None)})})?;
    // numbers
    e.set("numbers",{let params=vec![("shell".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let mod59=rt.import_module("_enclosure_panel")?;e.set("_Graph",rt.member("_enclosure_panel","_Graph")?)?;e.set("_record",rt.member("_enclosure_panel","_record")?)?;
let mod60=rt.import_module("_enclosure_front_top")?;e.set("_front_half",rt.member("_enclosure_front_top","_front_half")?)?;e.set("_leaves",rt.member("_enclosure_front_top","_leaves")?)?;
let mod61=rt.import_module("_enclosure_back_top")?;e.set("_replace",rt.member("_enclosure_back_top","_replace")?)?;
e.set("_enclosure_structure",rt.import_module("_enclosure_structure")?)?;
let mod62=rt.import_module("_materials")?;e.set("linear",rt.member("_materials","linear")?)?;
let assigned63={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun66=e.get("_Graph")?;let mut args64=Vec::new();let mut kw65=Vec::new();fun66.call(args64,kw65)?}};e.set("graph",assigned63.clone())?;
let assigned67={let d=Val::dict(vec![]);d};e.get("graph")?.setattr("extras",assigned67.clone())?;
let assigned68={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun71=e.get("graph")?.attr("add")?;let mut args69=Vec::new();let mut kw70=Vec::new();args69.push(Val::Str("silhouette".into()));kw70.push(("bounds".into(),e.get("box")?.attr("outer")?));fun71.call(args69,kw70)?}};e.set("structure",assigned68.clone())?;
let context72={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun75=e.get("_record")?;let mut args73=Vec::new();let mut kw74=Vec::new();args73.push(e.get("shell")?);args73.push(e.get("graph")?);args73.push(e.get("structure")?);fun75.call(args73,kw74)?}};context72.attr("__enter__")?.call(vec![],vec![])?;let context76={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun79=e.get("_leaves")?;let mut args77=Vec::new();let mut kw78=Vec::new();args77.push(e.get("shell")?);args77.push(e.get("graph")?);args77.push(e.get("box")?);fun79.call(args77,kw78)?}};context76.attr("__enter__")?.call(vec![],vec![])?;let context80={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun83=e.get("_replace")?;let mut args81=Vec::new();let mut kw82=Vec::new();args81.push(e.get("shell")?);args81.push({let d=Val::dict(vec![]);d.set(Val::Str("_flank_vents".into()),{let params=vec![("solid".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,Some("args"),None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun86=e.get("_vents")?;let mut args84=Vec::new();let mut kw85=Vec::new();args84.push(e.get("shell")?);args84.push(e.get("graph")?);args84.push(e.get("solid")?);args84.extend(e.get("args")?.iter()?);fun86.call(args84,kw85)?}});
Ok(Val::None)})})?;d});fun83.call(args81,kw82)?}};context80.attr("__enter__")?.call(vec![],vec![])?;let context_result95=(||->Result<Flow>{let assigned87={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun90=e.get("_front_half")?;let mut args88=Vec::new();let mut kw89=Vec::new();args88.push(e.get("shell")?);args88.push(e.get("graph")?);args88.push(e.get("box")?);args88.push(e.get("structure")?);fun90.call(args88,kw89)?}};e.set("half",assigned87.clone())?;
let assigned91={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun94=e.get("shell")?.attr("build_piece")?;let mut args92=Vec::new();let mut kw93=Vec::new();args92.push(e.get("box")?);args92.push(Val::Str("front".into()));args92.push(Val::Str("bottom".into()));kw93.push(("halves_cache".into(),{let d=Val::dict(vec![]);d.set(Val::Str("front".into()),e.get("half")?)?;d}));fun94.call(args92,kw93)?}};e.set("result",assigned91.clone())?;
Ok(Flow::Continue)})();context80.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;context76.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;context72.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result95? {Flow::Continue=>{},Flow::Return(value)=>return Ok(value)}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun98=e.get("dict")?;let mut args96=Vec::new();let mut kw97=Vec::new();args96.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun101=e.get("_enclosure_structure")?.attr("numbers")?;let mut args99=Vec::new();let mut kw100=Vec::new();args99.push(e.get("box")?.attr("outer")?);fun101.call(args99,kw100)?}});kw97.push(("color".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun104=e.get("linear")?;let mut args102=Vec::new();let mut kw103=Vec::new();args102.push(e.get("shell")?.attr("PIECE_COLORS")?.get(Val::Str("front-bottom".into()))?);fun104.call(args102,kw103)?}}));kw97.push(("panel".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun107=e.get("graph")?.attr("document")?;let mut args105=Vec::new();let mut kw106=Vec::new();args105.push(e.get("result")?);args105.push(e.get("graph")?.attr("extras")?);fun107.call(args105,kw106)?}}));kw97.push(("panel_bounds".into(),e.get("result")?.attr("bounds")?));fun98.call(args96,kw97)?}});
Ok(Val::None)})})?;
    // print_numbers
    e.set("print_numbers",{let params=vec![("shell".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("_enclosure_skin",rt.import_module("_enclosure_skin")?)?;
let assigned108={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun111=e.get("shell")?.attr("_above_core_shell")?.attr("rear_identification")?;let mut args109=Vec::new();let mut kw110=Vec::new();fun111.call(args109,kw110)?}};e.set("identification",assigned108.clone())?;
let assigned112={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun115=e.get("identification")?.attr("nameplate_station")?;let mut args113=Vec::new();let mut kw114=Vec::new();fun115.call(args113,kw114)?}};e.set("station",assigned112.clone())?;
let assigned116={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun119=e.get("identification")?.attr("nameplate_plan")?;let mut args117=Vec::new();let mut kw118=Vec::new();fun119.call(args117,kw118)?}};e.set("plan",assigned116.clone())?;
let assigned120=e.get("identification")?.attr("nameplate")?.attr("wing_interface")?;e.set("wing",assigned120.clone())?;
let assigned121={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun124=e.get("shell")?.attr("disposal_field")?;let mut args122=Vec::new();let mut kw123=Vec::new();args122.push(e.get("box")?.attr("outer")?);fun124.call(args122,kw123)?}});s.extend({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun127=e.get("wing")?.attr("plain_lips")?;let mut args125=Vec::new();let mut kw126=Vec::new();args125.push(e.get("station")?);args125.push(e.get("plan")?.get(Val::Str("face_y_mm".into()))?);fun127.call(args125,kw126)?}}.iter()?);s.extend({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun130=e.get("identification")?.attr("rail_bounds")?;let mut args128=Vec::new();let mut kw129=Vec::new();fun130.call(args128,kw129)?}}.iter()?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun133=e.get("shell")?.attr("_above_core_shell")?.attr("keystone_land")?;let mut args131=Vec::new();let mut kw132=Vec::new();fun133.call(args131,kw132)?}});Val::tuple(s)};e.set("plain",assigned121.clone())?;
if e.get("box")?.attr("pack")?.attr("nameplate")?.truthy()? {
e.set("plain",binary("add",e.get("plain")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun136=e.get("shell")?.attr("_nameplate_fit")?.attr("plain_lips")?;let mut args134=Vec::new();let mut kw135=Vec::new();args134.push(e.get("box")?.attr("pack")?.attr("nameplate")?);args134.push(e.get("box")?.attr("outer")?.get(Val::Int(3i64))?);fun136.call(args134,kw135)?}})?)?;
}
if e.get("box")?.attr("pack")?.attr("keystone")?.truthy()? {
e.set("plain",binary("add",e.get("plain")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun139=e.get("shell")?.attr("_data_fit")?.attr("plain_lips")?;let mut args137=Vec::new();let mut kw138=Vec::new();args137.push(e.get("box")?.attr("pack")?.attr("keystone")?);args137.push(e.get("box")?.attr("outer")?.get(Val::Int(3i64))?);fun139.call(args137,kw138)?}})?)?;
}
let assigned140={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun143=e.get("numbers")?;let mut args141=Vec::new();let mut kw142=Vec::new();args141.push(e.get("shell")?);args141.push(e.get("box")?);fun143.call(args141,kw142)?}};e.set("out",assigned140.clone())?;
e.set("layout",rt.import_module("above_core")?)?;
let assigned144={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun147=e.get("layout")?.attr("specification")?;let mut args145=Vec::new();let mut kw146=Vec::new();fun147.call(args145,kw146)?}}.get(Val::Str("rear_wall".into()))?.get(Val::Str("rear_wall".into()))?.get(Val::Str("ymax".into()))?;e.set("rear",assigned144.clone())?;
let assigned148=binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun151=e.get("max")?;let mut args149=Vec::new();let mut kw150=Vec::new();args149.push(e.get("shell")?.attr("flute_rise")?);args149.push(e.get("_enclosure_skin")?.attr("reeding")?.attr("flute_width")?);fun151.call(args149,kw150)?}},e.get("shell")?.attr("_flute_skin")?.attr("face_tol")?)?;e.set("reach",assigned148.clone())?;
let assigned152=e.get("out")?.get(Val::Str("panel_bounds".into()))?;e.set("bounds",assigned152.clone())?;
if {let v155={let v156=e.get("bounds")?;let v157=Val::None;Val::Bool(compare("is",v156.clone(),v157.clone())?.truthy()?)};if v155.truthy()? {v155} else {{let v153=binary("add",e.get("bounds")?.get(Val::Int(3i64))?,e.get("reach")?)?;let v154=binary("sub",e.get("rear")?,Val::Float(3.0f64))?;Val::Bool(compare("ge",v153.clone(),v154.clone())?.truthy()?)}}}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun160=e.get("ValueError")?;let mut args158=Vec::new();let mut kw159=Vec::new();args158.push(Val::Str("the rear receiver land reaches the front-bottom print boundary".into()));fun160.call(args158,kw159)?}})?);
}
let assigned161={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun164=e.get("shell")?.attr("_flute_skin")?.attr("Rail")?;let mut args162=Vec::new();let mut kw163=Vec::new();kw163.push(("at".into(),{let params=vec![("s".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun167=e.get("shell")?.attr("plan_at")?;let mut args165=Vec::new();let mut kw166=Vec::new();args165.push(e.get("s")?);args165.push(e.get("box")?.attr("outer")?);fun167.call(args165,kw166)?}});
Ok(Val::None)})}));kw163.push(("length".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun170=e.get("shell")?.attr("plan_perimeter")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push(e.get("box")?.attr("outer")?);fun170.call(args168,kw169)?}}));kw163.push(("plain".into(),e.get("plain")?));fun164.call(args162,kw163)?}};e.set("rail",assigned161.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun173=e.get("out")?.attr("update")?;let mut args171=Vec::new();let mut kw172=Vec::new();args171.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun176=e.get("_enclosure_skin")?.attr("field_numbers")?;let mut args174=Vec::new();let mut kw175=Vec::new();args174.push({let mut s=Vec::new();s.push(e.get("rail")?);Val::list(s)});args174.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",line!());{let fun179=e.get("shell")?.attr("flute_pitch")?;let mut args177=Vec::new();let mut kw178=Vec::new();args177.push(e.get("box")?.attr("outer")?);fun179.call(args177,kw178)?}});args174.push(e.get("shell")?.attr("flute_depth")?);args174.push(e.get("shell")?.attr("flute_rise")?);fun176.call(args174,kw175)?}});fun173.call(args171,kw172)?}};
let assigned180={let d=Val::dict(vec![]);d.set(Val::Str("front_panel_ymax_mm".into()),e.get("bounds")?.get(Val::Int(3i64))?)?;d.set(Val::Str("field_reach_mm".into()),e.get("reach")?)?;d.set(Val::Str("rear_land_ymin_mm".into()),binary("sub",e.get("rear")?,Val::Float(3.0f64))?)?;d};e.get("out")?.set(Val::Str("disjoint_receiver_land".into()),assigned180.clone())?;
return Ok(e.get("out")?);
Ok(Val::None)})})?;
    // cut
    e.set("cut", {
        let params = vec![
            ("shell".into(), None, false),
            ("box".into(), None, false),
            ("directory".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            let mod181 = rt.import_module("_enclosure_presentation")?;
            e.set(
                "print_payload",
                rt.member("_enclosure_presentation", "print_payload")?,
            )?;
            let assigned182 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",
                    line!(),
                );
                {
                    let fun185 = e.get("_rust_part")?.attr("cut")?;
                    let mut args183 = Vec::new();
                    let mut kw184 = Vec::new();
                    args183.push(Val::Str("enclosure-shell".into()));
                    args183.push(Val::Str("enclosure-front-bottom".into()));
                    args183.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",
                            line!(),
                        );
                        {
                            let fun188 = e.get("print_numbers")?;
                            let mut args186 = Vec::new();
                            let mut kw187 = Vec::new();
                            args186.push(e.get("shell")?);
                            args186.push(e.get("box")?);
                            fun188.call(args186, kw187)?
                        }
                    });
                    args183.push(e.get("directory")?);
                    fun185.call(args183, kw184)?
                }
            };
            e.set("said", assigned182.clone())?;
            let assigned189 = binary(
                "truediv",
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",
                        line!(),
                    );
                    {
                        let fun192 = e.get("Path")?;
                        let mut args190 = Vec::new();
                        let mut kw191 = Vec::new();
                        args190.push(e.get("directory")?);
                        fun192.call(args190, kw191)?
                    }
                },
                Val::Str("enclosure-front-bottom.step".into()),
            )?;
            e.set("step", assigned189.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_bottom.rs",
                    line!(),
                );
                {
                    let fun195 = e.get("print_payload")?;
                    let mut args193 = Vec::new();
                    let mut kw194 = Vec::new();
                    args193.push(e.get("step")?);
                    kw194.push(("check_print".into(), Val::Bool(true)));
                    fun195.call(args193, kw194)?
                }
            };
            return Ok(e.get("said")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
