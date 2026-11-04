#![allow(unused_variables,unused_mut,unreachable_code)]
use super::*;

pub fn initialize(rt:Runtime,e:Env)->Result<()> {
e.set("__doc__",Val::Str("_stated_bounds — the bounds a module states about its own constants, read at import.\n\nA generator's constants carry claims about each other: a screw is long enough for its insert, a\nband is wide enough for the bore it carries. Those\nclaims are settled the moment the module is read, before any solid exists — so they have no\nassembly to hang a reading on and no build to be measured during. This is the ledger they record\ninto instead. `enclosure_assembly.carry_stated_bounds` drains it onto the assembly beside the\nbounds the machine measures at every build, and `_scorecard._bounds` renders one gate row apiece.\n\nA VIOLATED BOUND IS A THING TO LOOK AT, and what a reader looks at is the STEP, the three\nelevations and the scorecard a run writes. A guard that raises at import destroys all four\nbefore the build starts, leaving the only account of the fault in a terminal nobody commits.\nSo a bound here never stops the module: the constants stand as written, the geometry comes out\nas those constants describe it, and the fault is a red row on the committed card carrying the\nmessage the bound wrote — beside the clashes and the open leads the same geometry produces in\n`pack-closes` and the rest. Two bodies packed nearer than they are wide come out overlapping,\nwhich the card can show a volume and a location for; a raise can only say so.\n\nAn `assert` is the same fault twice over, because `python -O` strips it: build-killing under\none interpreter and absent under another, which is the pair of failure modes a check must not\nhave. A bound recorded here reads the same either way.\n\nTwo entry points, both thin:\n\n    _bounds.state(\"id\", \"label\", \"target\", ok, \"what went wrong\")\n\nfor a bound with one reading, and\n\n    room = _bounds.bound(\"id\", \"label\", \"target\")\n    for name in stations:\n        room(clear(name) >= gap, f\"{name} stands {clear(name):.2f} mm off its neighbour\")\n\nfor a bound stated once over a population — one card row, its value the tally, its detail the\nnotes the failing readings wrote. Both hand back the reading, so a caller whose next line\ncannot run on a violated bound can branch on it rather than proceeding into a lookup that\nis not there.\n".into()))?;
e.set("namedtuple",rt.member("collections","namedtuple")?)?;
let assigned1={let fun4=e.get("namedtuple")?;let mut args2=Vec::new();let mut kw3=Vec::new();args2.push(Val::Str("Bound".into()));args2.push(Val::Str("id label ok value target detail".into()));kw3.push(("module".into(),e.get("__name__")?));fun4.call(args2,kw3)?};e.set("Bound",assigned1.clone())?;
e.set("BOUNDS",{let mut s=Vec::new();Val::list(s)})?;
e.set("StatedBound.__init__",{let params=vec![("self".into(),None,false),("id".into(),None,false),("label".into(),None,false),("target".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned5={let mut s=Vec::new();s.push(e.get("id")?);s.push(e.get("label")?);s.push(e.get("target")?);Val::tuple(s)};let unpack6=unpack(assigned5.clone(),3)?;e.get("self")?.setattr("id",unpack6[0].clone())?;e.get("self")?.setattr("label",unpack6[1].clone())?;e.get("self")?.setattr("target",unpack6[2].clone())?;
let assigned7=Val::Int(0i64);e.get("self")?.setattr("held",assigned7.clone())?;e.get("self")?.setattr("total",assigned7.clone())?;
e.get("self")?.setattr("detail",{let mut s=Vec::new();Val::list(s)})?;
Ok(Val::None)})})?;
e.set("StatedBound.__call__",{let params=vec![("self".into(),None,false),("ok".into(),None,false),("note".into(),Some(Val::Str("".into())),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned8={let fun11=e.get("bool")?;let mut args9=Vec::new();let mut kw10=Vec::new();args9.push(e.get("ok")?);fun11.call(args9,kw10)?};e.set("ok",assigned8.clone())?;
e.get("self")?.setattr("total",binary("add",e.get("self")?.attr("total")?,Val::Int(1i64))?)?;
if e.get("ok")?.truthy()? {
e.get("self")?.setattr("held",binary("add",e.get("self")?.attr("held")?,Val::Int(1i64))?)?;
}else{
if e.get("note")?.truthy()? {
{let fun14=e.get("self")?.attr("detail")?.attr("append")?;let mut args12=Vec::new();let mut kw13=Vec::new();args12.push(e.get("note")?);fun14.call(args12,kw13)?};
}
}
return Ok(e.get("ok")?);
Ok(Val::None)})})?;
e.set("StatedBound.ok",{let params=vec![("self".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let v15=e.get("self")?.attr("held")?;let v16=e.get("self")?.attr("total")?;Val::Bool(compare("eq",v15.clone(),v16.clone())?.truthy()?)});
Ok(Val::None)})})?;
e.set("StatedBound.value",{let params=vec![("self".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let v17=e.get("self")?.attr("total")?;let v18=Val::Int(1i64);Val::Bool(compare("eq",v17.clone(),v18.clone())?.truthy()?)}.truthy()? {
return Ok(if e.get("self")?.attr("ok")?.truthy()? {Val::Str("holds".into())} else {Val::Str("open".into())});
}
return Ok({let mut str19=String::new();str19.push_str(&format(&e.get("self")?.attr("held")?,&String::new())?);str19.push_str("/");str19.push_str(&format(&e.get("self")?.attr("total")?,&String::new())?);str19.push_str(" hold");Val::Str(str19)});
Ok(Val::None)})})?;
e.set("StatedBound.record",{let params=vec![("self".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let fun22=e.get("Bound")?;let mut args20=Vec::new();let mut kw21=Vec::new();args20.push(e.get("self")?.attr("id")?);args20.push(e.get("self")?.attr("label")?);args20.push(e.get("self")?.attr("ok")?);args20.push(e.get("self")?.attr("value")?);args20.push(e.get("self")?.attr("target")?);args20.push({let fun25=e.get("list")?;let mut args23=Vec::new();let mut kw24=Vec::new();args23.push(e.get("self")?.attr("detail")?);fun25.call(args23,kw24)?});fun22.call(args20,kw21)?});
Ok(Val::None)})})?;
e.set("StatedBound",rt.python_type("_stated_bounds","StatedBound")?)?;
// hardware/scripts/_stated_bounds.py:86 bound
e.set("bound",{let params=vec![("id".into(),None,false),("label".into(),None,false),("target".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned26={let fun29=e.get("StatedBound")?;let mut args27=Vec::new();let mut kw28=Vec::new();args27.push(e.get("id")?);args27.push(e.get("label")?);args27.push(e.get("target")?);fun29.call(args27,kw28)?};e.set("b",assigned26.clone())?;
let assigned30=binary("add",{let e=e.child();let out31=Val::list(vec![]);for item32 in e.get("BOUNDS")?.iter()? {e.set("x",item32)?;if {let v33=e.get("x")?.attr("id")?;let v34=e.get("id")?;Val::Bool(compare("ne",v33.clone(),v34.clone())?.truthy()?)}.truthy()? {out31.attr("append")?.call(vec![e.get("x")?],vec![])?;}}out31},{let mut s=Vec::new();s.push(e.get("b")?);Val::list(s)})?;e.get("BOUNDS")?.set(Val::Slice{start:None,stop:None,step:1},assigned30.clone())?;
return Ok(e.get("b")?);
Ok(Val::None)})})?;
// hardware/scripts/_stated_bounds.py:93 state
e.set("state",{let params=vec![("id".into(),None,false),("label".into(),None,false),("target".into(),None,false),("ok".into(),None,false),("note".into(),Some(Val::Str("".into())),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let fun37={let fun40=e.get("bound")?;let mut args38=Vec::new();let mut kw39=Vec::new();args38.push(e.get("id")?);args38.push(e.get("label")?);args38.push(e.get("target")?);fun40.call(args38,kw39)?};let mut args35=Vec::new();let mut kw36=Vec::new();args35.push(e.get("ok")?);args35.push(e.get("note")?);fun37.call(args35,kw36)?});
Ok(Val::None)})})?;
// hardware/scripts/_stated_bounds.py:98 records
e.set("records",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let e=e.child();let out41=Val::list(vec![]);for item42 in e.get("BOUNDS")?.iter()? {e.set("b",item42)?;out41.attr("append")?.call(vec![{let fun45=e.get("b")?.attr("record")?;let mut args43=Vec::new();let mut kw44=Vec::new();fun45.call(args43,kw44)?}],vec![])?;}out41});
Ok(Val::None)})})?;
// hardware/scripts/_stated_bounds.py:103 report
e.set("report",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned46={let e=e.child();let out47=Val::list(vec![]);for item48 in e.get("BOUNDS")?.iter()? {e.set("b",item48)?;if unary("not",e.get("b")?.attr("ok")?)?.truthy()? {out47.attr("append")?.call(vec![e.get("b")?],vec![])?;}}out47};e.set("open_",assigned46.clone())?;
for item49 in e.get("BOUNDS")?.iter()? {
e.set("b",item49)?;{let fun52=e.get("print")?;let mut args50=Vec::new();let mut kw51=Vec::new();args50.push({let mut str53=String::new();str53.push_str("  ");str53.push_str(&format(&if e.get("b")?.attr("ok")?.truthy()? {Val::Str("OK  ".into())} else {Val::Str("OPEN".into())},&String::new())?);str53.push_str(" ");str53.push_str(&format(&e.get("b")?.attr("id")?,&val_string({let mut str54=String::new();str54.push_str("28");Val::Str(str54)})?)?);str53.push_str(" ");str53.push_str(&format(&e.get("b")?.attr("value")?,&val_string({let mut str55=String::new();str55.push_str("12");Val::Str(str55)})?)?);str53.push_str(" ");str53.push_str(&format(&e.get("b")?.attr("label")?,&String::new())?);Val::Str(str53)});fun52.call(args50,kw51)?};
for item56 in e.get("b")?.attr("detail")?.iter()? {
e.set("line",item56)?;{let fun59=e.get("print")?;let mut args57=Vec::new();let mut kw58=Vec::new();args57.push({let mut str60=String::new();str60.push_str("         ");str60.push_str(&format(&e.get("line")?,&String::new())?);Val::Str(str60)});fun59.call(args57,kw58)?};
}
}
{let fun63=e.get("print")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push({let mut str64=String::new();str64.push_str("\n");str64.push_str(&format(&binary("sub",{let fun67=e.get("len")?;let mut args65=Vec::new();let mut kw66=Vec::new();args65.push(e.get("BOUNDS")?);fun67.call(args65,kw66)?},{let fun70=e.get("len")?;let mut args68=Vec::new();let mut kw69=Vec::new();args68.push(e.get("open_")?);fun70.call(args68,kw69)?})?,&String::new())?);str64.push_str("/");str64.push_str(&format(&{let fun73=e.get("len")?;let mut args71=Vec::new();let mut kw72=Vec::new();args71.push(e.get("BOUNDS")?);fun73.call(args71,kw72)?},&String::new())?);str64.push_str(" stated bounds hold");Val::Str(str64)});fun63.call(args61,kw62)?};
return Ok(if e.get("open_")?.truthy()? {Val::Int(1i64)} else {Val::Int(0i64)});
Ok(Val::None)})})?;
Ok(())
}
pub fn entrypoint(rt:Runtime,e:Env)->Result<Val>{
Ok(Val::None)
}
