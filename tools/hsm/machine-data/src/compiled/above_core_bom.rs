#![allow(unused_variables,unused_mut,unreachable_code)]
use super::*;

pub fn initialize(rt:Runtime,e:Env)->Result<()> {
e.set("__doc__",Val::Str("Selected above-core fitting names without native CAD imports.".into()))?;
let imported=rt.import_module("above_core")?;e.set("layout",imported)?;
e.set("_data",rt.member("_layout_data","data")?)?;
// hardware/manifold-layout/above_core_bom.py:8 reservoir_gate_elbow_hosts
e.set("reservoir_gate_elbow_hosts",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let e=e.child();let out1=Val::dict(vec![]);for item2 in {let fun5={let fun8=e.get("_data")?;let mut args6=Vec::new();let mut kw7=Vec::new();args6.push(Val::Str("reservoir-gates".into()));fun8.call(args6,kw7)?}.attr("items")?;let mut args3=Vec::new();let mut kw4=Vec::new();fun5.call(args3,kw4)?}.iter()? {let unpack9=unpack(item2,2)?;e.set("name",unpack9[0].clone())?;e.set("row",unpack9[1].clone())?;out1.set(e.get("name")?,{let fun12=e.get("tuple")?;let mut args10=Vec::new();let mut kw11=Vec::new();args10.push(e.get("row")?);fun12.call(args10,kw11)?})?;}out1});
Ok(Val::None)})})?;
// hardware/manifold-layout/above_core_bom.py:12 stem_elbow_names
e.set("stem_elbow_names",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let fun15=e.get("tuple")?;let mut args13=Vec::new();let mut kw14=Vec::new();args13.push({let fun18=e.get("_data")?;let mut args16=Vec::new();let mut kw17=Vec::new();args16.push(Val::Str("stem-elbow-names".into()));kw17.push(("spec".into(),{let fun21=e.get("layout")?.attr("specification")?;let mut args19=Vec::new();let mut kw20=Vec::new();fun21.call(args19,kw20)?}));fun18.call(args16,kw17)?});fun15.call(args13,kw14)?});
Ok(Val::None)})})?;
// hardware/manifold-layout/above_core_bom.py:16 core_stem_elbow_names
e.set("core_stem_elbow_names",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let mut s=Vec::new();Val::tuple(s)});
Ok(Val::None)})})?;
// hardware/manifold-layout/above_core_bom.py:21 union_elbow_names
e.set("union_elbow_names",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let fun24=e.get("tuple")?;let mut args22=Vec::new();let mut kw23=Vec::new();args22.push({let fun27=e.get("_data")?;let mut args25=Vec::new();let mut kw26=Vec::new();args25.push(Val::Str("union-elbow-names".into()));kw26.push(("spec".into(),{let fun30=e.get("layout")?.attr("specification")?;let mut args28=Vec::new();let mut kw29=Vec::new();fun30.call(args28,kw29)?}));fun27.call(args25,kw26)?});fun24.call(args22,kw23)?});
Ok(Val::None)})})?;
// hardware/manifold-layout/above_core_bom.py:25 core_union_elbow_names
e.set("core_union_elbow_names",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let mut s=Vec::new();Val::tuple(s)});
Ok(Val::None)})})?;
Ok(())
}
pub fn entrypoint(rt:Runtime,e:Env)->Result<Val>{
Ok(Val::None)
}
