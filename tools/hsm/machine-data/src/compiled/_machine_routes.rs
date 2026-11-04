#![allow(unused_variables,unused_mut,unreachable_code)]
use super::*;

pub fn initialize(rt:Runtime,e:Env)->Result<()> {
e.set("__doc__",Val::Str("Scalar requests for Rust's installed warm-tube and insulation geometry.".into()))?;
e.set("deepcopy",rt.member("copy","deepcopy")?)?;
let imported=rt.import_module("json")?;e.set("json",imported)?;
e.set("Path",rt.member("pathlib","Path")?)?;
// hardware/scripts/_machine_routes.py:9 numbers
e.set("numbers",{let params=vec![("routes".into(),None,false),("insulation".into(),Some(Val::None),true),("components".into(),Some(Val::None),true),("name".into(),Some(Val::Str("machine-routes".into())),true)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let d=Val::dict(vec![]);d.set(Val::Str("name".into()),e.get("name")?)?;d.set(Val::Str("routes".into()),{let fun3=e.get("deepcopy")?;let mut args1=Vec::new();let mut kw2=Vec::new();args1.push(e.get("routes")?);fun3.call(args1,kw2)?})?;d.set(Val::Str("route_order".into()),{let fun6=e.get("list")?;let mut args4=Vec::new();let mut kw5=Vec::new();args4.push(e.get("routes")?);fun6.call(args4,kw5)?})?;d.set(Val::Str("insulation".into()),{let fun9=e.get("deepcopy")?;let mut args7=Vec::new();let mut kw8=Vec::new();args7.push(e.get("insulation")?);fun9.call(args7,kw8)?})?;d.set(Val::Str("components".into()),{let fun12=e.get("deepcopy")?;let mut args10=Vec::new();let mut kw11=Vec::new();args10.push({let v13=e.get("components")?;if v13.truthy()? {v13} else {{let d=Val::dict(vec![]);d}}});fun12.call(args10,kw11)?})?;d});
Ok(Val::None)})})?;
// hardware/scripts/_machine_routes.py:20 equipment_inputs
e.set("equipment_inputs",{let params=vec![("request".into(),None,false),("model".into(),None,false),("groups".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned14={let fun17=e.get("request")?.attr("get")?;let mut args15=Vec::new();let mut kw16=Vec::new();args15.push(Val::Str("insulation".into()));fun17.call(args15,kw16)?};e.set("insulation",assigned14.clone())?;
if {let v18=e.get("insulation")?;let v19=Val::None;Val::Bool(compare("is",v18.clone(),v19.clone())?.truthy()?)}.truthy()? {
let assigned20={let fun23=e.get("next")?;let mut args21=Vec::new();let mut kw22=Vec::new();args21.push({let e=e.child();let out24=Val::list(vec![]);for item25 in {let fun28=e.get("request")?.attr("get")?;let mut args26=Vec::new();let mut kw27=Vec::new();args26.push(Val::Str("items".into()));args26.push({let mut s=Vec::new();Val::tuple(s)});fun28.call(args26,kw27)?}.iter()? {e.set("row",item25)?;if {let v32={let fun31=e.get("row")?.attr("get")?;let mut args29=Vec::new();let mut kw30=Vec::new();args29.push(Val::Str("op".into()));fun31.call(args29,kw30)?};let v33=Val::Str("insulation".into());Val::Bool(compare("eq",v32.clone(),v33.clone())?.truthy()?)}.truthy()? {out24.attr("append")?.call(vec![e.get("row")?],vec![])?;}}out24});args21.push(Val::None);fun23.call(args21,kw22)?};e.set("insulation",assigned20.clone())?;
}
let assigned34={let d=Val::dict(vec![]);d};e.set("components",assigned34.clone())?;
if {let v35=e.get("insulation")?;let v36=Val::None;Val::Bool(compare("is_not",v35.clone(),v36.clone())?.truthy()?)}.truthy()? {
for item37 in {let mut s=Vec::new();s.push(Val::Str("soda-bend-holder".into()));s.extend(e.get("insulation")?.get(Val::Str("neighbors".into()))?.iter()?);Val::tuple(s)}.iter()? {
e.set("name",item37)?;let assigned38={let d=Val::dict(vec![]);d.set(Val::Str("model".into()),{let fun41=e.get("str")?;let mut args39=Vec::new();let mut kw40=Vec::new();args39.push({let fun44=e.get("Path")?;let mut args42=Vec::new();let mut kw43=Vec::new();args42.push(e.get("model")?);fun44.call(args42,kw43)?});fun41.call(args39,kw40)?})?;d.set(Val::Str("indices".into()),{let fun47=e.get("list")?;let mut args45=Vec::new();let mut kw46=Vec::new();args45.push(e.get("groups")?.get(e.get("name")?)?);fun47.call(args45,kw46)?})?;d};e.get("components")?.set(e.get("name")?,assigned38.clone())?;
}
}
return Ok({let d=Val::dict(vec![]);d.set(Val::Str("routes".into()),e.get("request")?.get(Val::Str("routes".into()))?)?;d.set(Val::Str("insulation".into()),e.get("insulation")?)?;d.set(Val::Str("components".into()),e.get("components")?)?;d});
Ok(Val::None)})})?;
// hardware/scripts/_machine_routes.py:34 build
e.set("build",{let params=vec![("output".into(),None,false),("routes".into(),None,false),("insulation".into(),Some(Val::None),true),("components".into(),Some(Val::None),true),("name".into(),Some(Val::Str("machine-routes".into())),true)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let imported=rt.import_module("_rust_part")?;e.set("_rust_part",imported)?;
let assigned48={let fun51={let fun54=e.get("Path")?;let mut args52=Vec::new();let mut kw53=Vec::new();args52.push(e.get("output")?);fun54.call(args52,kw53)?}.attr("resolve")?;let mut args49=Vec::new();let mut kw50=Vec::new();fun51.call(args49,kw50)?};e.set("output",assigned48.clone())?;
{let fun57=e.get("output")?.attr("mkdir")?;let mut args55=Vec::new();let mut kw56=Vec::new();kw56.push(("parents".into(),Val::Bool(true)));kw56.push(("exist_ok".into(),Val::Bool(true)));fun57.call(args55,kw56)?};
{let fun60=e.get("_rust_part")?.attr("cut")?;let mut args58=Vec::new();let mut kw59=Vec::new();args58.push(Val::Str("machine".into()));args58.push(Val::Str("machine-routes".into()));args58.push({let fun63=e.get("numbers")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push(e.get("routes")?);kw62.push(("insulation".into(),e.get("insulation")?));kw62.push(("components".into(),e.get("components")?));kw62.push(("name".into(),e.get("name")?));fun63.call(args61,kw62)?});args58.push(e.get("output")?);fun60.call(args58,kw59)?};
let assigned64={let fun67=e.get("json")?.attr("loads")?;let mut args65=Vec::new();let mut kw66=Vec::new();args65.push({let fun70=binary("truediv",e.get("output")?,{let mut str71=String::new();str71.push_str(&format(&e.get("name")?,&String::new())?);str71.push_str(".json");Val::Str(str71)})?.attr("read_text")?;let mut args68=Vec::new();let mut kw69=Vec::new();fun70.call(args68,kw69)?});fun67.call(args65,kw66)?};e.set("result",assigned64.clone())?;
let assigned72={let fun75=e.get("str")?;let mut args73=Vec::new();let mut kw74=Vec::new();args73.push(binary("truediv",e.get("output")?,{let mut str76=String::new();str76.push_str(&format(&e.get("name")?,&String::new())?);str76.push_str(".step.npz");Val::Str(str76)})?);fun75.call(args73,kw74)?};e.set("model",assigned72.clone())?;
for item77 in e.get("result")?.get(Val::Str("instances".into()))?.iter()? {
e.set("instance",item77)?;let assigned78=e.get("model")?;e.get("instance")?.set(Val::Str("model".into()),assigned78.clone())?;
}
let assigned79=e.get("model")?;e.get("result")?.set(Val::Str("model".into()),assigned79.clone())?;
return Ok(e.get("result")?);
Ok(Val::None)})})?;
Ok(())
}
pub fn entrypoint(rt:Runtime,e:Env)->Result<Val>{
Ok(Val::None)
}
