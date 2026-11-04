//! Enclosure-private numeric construction for the structural back-bottom panel.
//!
//! The native seam helpers keep ownership of their stations. This module records their
//! simple solid operations; Rust builds the solids and releases each intermediate after
//! its last use. Native builders and their cached geometry remain available to callers.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("contextlib")?;
    e.set("contextmanager", rt.member("contextlib", "contextmanager")?)?;
    let mod2 = rt.import_module("functools")?;
    e.set("cache", rt.member("functools", "cache")?)?;
    let mod3 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set(
        "_enclosure_structure",
        rt.import_module("_enclosure_structure")?,
    )?;
    e.set("_Shape.__init__", {
        let params = vec![
            ("self".into(), None, false),
            ("graph".into(), None, false),
            ("index".into(), None, false),
            ("bounds".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned4 = {
                let mut s = Vec::new();
                s.push(e.get("graph")?);
                s.push(e.get("index")?);
                s.push(e.get("bounds")?);
                Val::tuple(s)
            };
            let unpack5 = unpack(assigned4.clone(), 3)?;
            e.get("self")?.setattr("graph", unpack5[0].clone())?;
            e.get("self")?.setattr("index", unpack5[1].clone())?;
            e.get("self")?.setattr("bounds", unpack5[2].clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("_Shape._boolean",{let params=vec![("self".into(),None,false),("op".into(),None,false),("others".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned6={let mut s=Vec::new();s.push(e.get("self")?);s.extend(e.get("others")?.iter()?);Val::list(s)};e.set("nodes",assigned6.clone())?;
if {let v9={let v10=e.get("op")?;let v11=Val::Str("cut".into());Val::Bool(compare("eq",v10.clone(),v11.clone())?.truthy()?)};if v9.truthy()? {{let v7=e.get("self")?.attr("bounds")?;let v8=Val::None;Val::Bool(compare("is_not",v7.clone(),v8.clone())?.truthy()?)}} else {v9}}.truthy()? {
let assigned12={let mut s=Vec::new();s.push(e.get("self")?);s.extend({let e=e.child();let out13=Val::list(vec![]);for item14 in e.get("others")?.iter()? {e.set("other",item14)?;if {let v28={let v29=e.get("other")?.attr("bounds")?;let v30=Val::None;Val::Bool(compare("is",v29.clone(),v30.clone())?.truthy()?)};if v28.truthy()? {v28} else {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun17=e.get("all")?;let mut args15=Vec::new();let mut kw16=Vec::new();args15.push({let e=e.child();let out18=Val::list(vec![]);for item19 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun22=e.get("range")?;let mut args20=Vec::new();let mut kw21=Vec::new();args20.push(Val::Int(3i64));fun22.call(args20,kw21)?}}.iter()? {e.set("k",item19)?;out18.attr("append")?.call(vec![{let v25={let v26=e.get("self")?.attr("bounds")?.get(binary("mul",Val::Int(2i64),e.get("k")?)?)?;let v27=e.get("other")?.attr("bounds")?.get(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(1i64))?)?;Val::Bool(compare("lt",v26.clone(),v27.clone())?.truthy()?)};if v25.truthy()? {{let v23=e.get("other")?.attr("bounds")?.get(binary("mul",Val::Int(2i64),e.get("k")?)?)?;let v24=e.get("self")?.attr("bounds")?.get(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(1i64))?)?;Val::Bool(compare("lt",v23.clone(),v24.clone())?.truthy()?)}} else {v25}}],vec![])?;}out18});fun17.call(args15,kw16)?}}}}.truthy()? {out13.attr("append")?.call(vec![e.get("other")?],vec![])?;}}out13}.iter()?);Val::list(s)};e.set("nodes",assigned12.clone())?;
}
if {let v34={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun33=e.get("len")?;let mut args31=Vec::new();let mut kw32=Vec::new();args31.push(e.get("nodes")?);fun33.call(args31,kw32)?}};let v35=Val::Int(1i64);Val::Bool(compare("eq",v34.clone(),v35.clone())?.truthy()?)}.truthy()? {
return Ok(e.get("self")?);
}
let assigned36=e.get("self")?.attr("bounds")?;e.set("bounds",assigned36.clone())?;
if {let v37=e.get("op")?;let v38=Val::Str("union".into());Val::Bool(compare("eq",v37.clone(),v38.clone())?.truthy()?)}.truthy()? {
let assigned39=if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun42=e.get("all")?;let mut args40=Vec::new();let mut kw41=Vec::new();args40.push({let e=e.child();let out43=Val::list(vec![]);for item44 in e.get("nodes")?.iter()? {e.set("n",item44)?;out43.attr("append")?.call(vec![{let v45=e.get("n")?.attr("bounds")?;let v46=Val::None;Val::Bool(compare("is_not",v45.clone(),v46.clone())?.truthy()?)}],vec![])?;}out43});fun42.call(args40,kw41)?}}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun49=e.get("tuple")?;let mut args47=Vec::new();let mut kw48=Vec::new();args47.push({let e=e.child();let out50=Val::list(vec![]);for item51 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun54=e.get("range")?;let mut args52=Vec::new();let mut kw53=Vec::new();args52.push(Val::Int(3i64));fun54.call(args52,kw53)?}}.iter()? {e.set("k",item51)?;for item55 in {let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun58=e.get("min")?;let mut args56=Vec::new();let mut kw57=Vec::new();args56.push({let e=e.child();let out59=Val::list(vec![]);for item60 in e.get("nodes")?.iter()? {e.set("n",item60)?;out59.attr("append")?.call(vec![e.get("n")?.attr("bounds")?.get(binary("mul",Val::Int(2i64),e.get("k")?)?)?],vec![])?;}out59});fun58.call(args56,kw57)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun63=e.get("max")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push({let e=e.child();let out64=Val::list(vec![]);for item65 in e.get("nodes")?.iter()? {e.set("n",item65)?;out64.attr("append")?.call(vec![e.get("n")?.attr("bounds")?.get(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(1i64))?)?],vec![])?;}out64});fun63.call(args61,kw62)?}});Val::tuple(s)}.iter()? {e.set("v",item55)?;out50.attr("append")?.call(vec![e.get("v")?],vec![])?;}}out50});fun49.call(args47,kw48)?}}} else {Val::None};e.set("bounds",assigned39.clone())?;
}else{
if {let v73={let v74=e.get("op")?;let v75=Val::Str("intersect".into());Val::Bool(compare("eq",v74.clone(),v75.clone())?.truthy()?)};if v73.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun68=e.get("all")?;let mut args66=Vec::new();let mut kw67=Vec::new();args66.push({let e=e.child();let out69=Val::list(vec![]);for item70 in e.get("nodes")?.iter()? {e.set("n",item70)?;out69.attr("append")?.call(vec![{let v71=e.get("n")?.attr("bounds")?;let v72=Val::None;Val::Bool(compare("is_not",v71.clone(),v72.clone())?.truthy()?)}],vec![])?;}out69});fun68.call(args66,kw67)?}}} else {v73}}.truthy()? {
let assigned76={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun79=e.get("tuple")?;let mut args77=Vec::new();let mut kw78=Vec::new();args77.push({let e=e.child();let out80=Val::list(vec![]);for item81 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun84=e.get("range")?;let mut args82=Vec::new();let mut kw83=Vec::new();args82.push(Val::Int(3i64));fun84.call(args82,kw83)?}}.iter()? {e.set("k",item81)?;for item85 in {let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun88=e.get("max")?;let mut args86=Vec::new();let mut kw87=Vec::new();args86.push({let e=e.child();let out89=Val::list(vec![]);for item90 in e.get("nodes")?.iter()? {e.set("n",item90)?;out89.attr("append")?.call(vec![e.get("n")?.attr("bounds")?.get(binary("mul",Val::Int(2i64),e.get("k")?)?)?],vec![])?;}out89});fun88.call(args86,kw87)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun93=e.get("min")?;let mut args91=Vec::new();let mut kw92=Vec::new();args91.push({let e=e.child();let out94=Val::list(vec![]);for item95 in e.get("nodes")?.iter()? {e.set("n",item95)?;out94.attr("append")?.call(vec![e.get("n")?.attr("bounds")?.get(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(1i64))?)?],vec![])?;}out94});fun93.call(args91,kw92)?}});Val::tuple(s)}.iter()? {e.set("v",item85)?;out80.attr("append")?.call(vec![e.get("v")?],vec![])?;}}out80});fun79.call(args77,kw78)?}};e.set("bounds",assigned76.clone())?;
}
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun98=e.get("self")?.attr("graph")?.attr("add")?;let mut args96=Vec::new();let mut kw97=Vec::new();args96.push(e.get("op")?);args96.push({let e=e.child();let out99=Val::list(vec![]);for item100 in e.get("nodes")?.iter()? {e.set("n",item100)?;out99.attr("append")?.call(vec![e.get("n")?.attr("index")?],vec![])?;}out99});kw97.push(("bounds".into(),e.get("bounds")?));fun98.call(args96,kw97)?}});
Ok(Val::None)})})?;
    e.set("_Shape.fuse", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(
                &outer,
                &params,
                args,
                kwargs,
                Some("others"),
                Some("_kwargs"),
            )?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun103 = e.get("self")?.attr("_boolean")?;
                    let mut args101 = Vec::new();
                    let mut kw102 = Vec::new();
                    args101.push(Val::Str("union".into()));
                    args101.push(e.get("others")?);
                    fun103.call(args101, kw102)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Shape.cut", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(
                &outer,
                &params,
                args,
                kwargs,
                Some("others"),
                Some("_kwargs"),
            )?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun106 = e.get("self")?.attr("_boolean")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    args104.push(Val::Str("cut".into()));
                    args104.push(e.get("others")?);
                    fun106.call(args104, kw105)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Shape.intersect", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(
                &outer,
                &params,
                args,
                kwargs,
                Some("others"),
                Some("_kwargs"),
            )?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun109 = e.get("self")?.attr("_boolean")?;
                    let mut args107 = Vec::new();
                    let mut kw108 = Vec::new();
                    args107.push(Val::Str("intersect".into()));
                    args107.push(e.get("others")?);
                    fun109.call(args107, kw108)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Shape.translate", {
        let params = vec![("self".into(), None, false), ("delta".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned110 = if {
                let v111 = e.get("self")?.attr("bounds")?;
                let v112 = Val::None;
                Val::Bool(compare("is_not", v111.clone(), v112.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                        line!(),
                    );
                    {
                        let fun115 = e.get("tuple")?;
                        let mut args113 = Vec::new();
                        let mut kw114 = Vec::new();
                        args113.push({
                            let e = e.child();
                            let out116 = Val::list(vec![]);
                            for item117 in {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                                    line!(),
                                );
                                {
                                    let fun120 = e.get("range")?;
                                    let mut args118 = Vec::new();
                                    let mut kw119 = Vec::new();
                                    args118.push(Val::Int(3i64));
                                    fun120.call(args118, kw119)?
                                }
                            }
                            .iter()?
                            {
                                e.set("k", item117)?;
                                for item121 in e
                                    .get("self")?
                                    .attr("bounds")?
                                    .get(Val::Slice {
                                        start: Some(
                                            binary("mul", Val::Int(2i64), e.get("k")?)?
                                                .integer()?,
                                        ),
                                        stop: Some(
                                            binary(
                                                "add",
                                                binary("mul", Val::Int(2i64), e.get("k")?)?,
                                                Val::Int(2i64),
                                            )?
                                            .integer()?,
                                        ),
                                        step: 1,
                                    })?
                                    .iter()?
                                {
                                    e.set("v", item121)?;
                                    out116.attr("append")?.call(
                                        vec![binary(
                                            "add",
                                            e.get("v")?,
                                            e.get("delta")?.get(e.get("k")?)?,
                                        )?],
                                        vec![],
                                    )?;
                                }
                            }
                            out116
                        });
                        fun115.call(args113, kw114)?
                    }
                }
            } else {
                Val::None
            };
            e.set("bounds", assigned110.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun124 = e.get("self")?.attr("graph")?.attr("add")?;
                    let mut args122 = Vec::new();
                    let mut kw123 = Vec::new();
                    args122.push(Val::Str("translate".into()));
                    args122.push({
                        let mut s = Vec::new();
                        s.push(e.get("self")?.attr("index")?);
                        Val::list(s)
                    });
                    kw123.push(("delta".into(), e.get("delta")?));
                    kw123.push(("bounds".into(), e.get("bounds")?));
                    fun124.call(args122, kw123)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Shape.rotate",{let params=vec![("self".into(),None,false),("origin".into(),None,false),("end".into(),None,false),("angle".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("math",rt.import_module("math")?)?;
let mod125=rt.import_module("itertools")?;e.set("product",rt.member("itertools","product")?)?;
let assigned126={let e=e.child();let out127=Val::list(vec![]);for item128 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun131=e.get("zip")?;let mut args129=Vec::new();let mut kw130=Vec::new();args129.push(e.get("origin")?);args129.push(e.get("end")?);fun131.call(args129,kw130)?}}.iter()? {let unpack132=unpack(item128,2)?;e.set("a",unpack132[0].clone())?;e.set("b",unpack132[1].clone())?;out127.attr("append")?.call(vec![binary("sub",e.get("b")?,e.get("a")?)?],vec![])?;}out127};e.set("axis",assigned126.clone())?;
let assigned133={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun136=e.get("math")?.attr("sqrt")?;let mut args134=Vec::new();let mut kw135=Vec::new();args134.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun139=e.get("sum")?;let mut args137=Vec::new();let mut kw138=Vec::new();args137.push({let e=e.child();let out140=Val::list(vec![]);for item141 in e.get("axis")?.iter()? {e.set("a",item141)?;out140.attr("append")?.call(vec![binary("mul",e.get("a")?,e.get("a")?)?],vec![])?;}out140});fun139.call(args137,kw138)?}});fun136.call(args134,kw135)?}};e.set("length",assigned133.clone())?;
let assigned142={let e=e.child();let out143=Val::list(vec![]);for item144 in e.get("axis")?.iter()? {e.set("a",item144)?;out143.attr("append")?.call(vec![binary("truediv",e.get("a")?,e.get("length")?)?],vec![])?;}out143};e.set("axis",assigned142.clone())?;
let assigned145={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun148=e.get("math")?.attr("cos")?;let mut args146=Vec::new();let mut kw147=Vec::new();args146.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun151=e.get("math")?.attr("radians")?;let mut args149=Vec::new();let mut kw150=Vec::new();args149.push(e.get("angle")?);fun151.call(args149,kw150)?}});fun148.call(args146,kw147)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun154=e.get("math")?.attr("sin")?;let mut args152=Vec::new();let mut kw153=Vec::new();args152.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun157=e.get("math")?.attr("radians")?;let mut args155=Vec::new();let mut kw156=Vec::new();args155.push(e.get("angle")?);fun157.call(args155,kw156)?}});fun154.call(args152,kw153)?}});Val::tuple(s)};let unpack158=unpack(assigned145.clone(),2)?;e.set("c",unpack158[0].clone())?;e.set("s",unpack158[1].clone())?;
// point
e.set("point",{let params=vec![("p".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned159={let e=e.child();let out160=Val::list(vec![]);for item161 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun164=e.get("zip")?;let mut args162=Vec::new();let mut kw163=Vec::new();args162.push(e.get("p")?);args162.push(e.get("origin")?);fun164.call(args162,kw163)?}}.iter()? {let unpack165=unpack(item161,2)?;e.set("a",unpack165[0].clone())?;e.set("b",unpack165[1].clone())?;out160.attr("append")?.call(vec![binary("sub",e.get("a")?,e.get("b")?)?],vec![])?;}out160};e.set("q",assigned159.clone())?;
let assigned166={let mut s=Vec::new();s.push(binary("sub",binary("mul",e.get("axis")?.get(Val::Int(1i64))?,e.get("q")?.get(Val::Int(2i64))?)?,binary("mul",e.get("axis")?.get(Val::Int(2i64))?,e.get("q")?.get(Val::Int(1i64))?)?)?);s.push(binary("sub",binary("mul",e.get("axis")?.get(Val::Int(2i64))?,e.get("q")?.get(Val::Int(0i64))?)?,binary("mul",e.get("axis")?.get(Val::Int(0i64))?,e.get("q")?.get(Val::Int(2i64))?)?)?);s.push(binary("sub",binary("mul",e.get("axis")?.get(Val::Int(0i64))?,e.get("q")?.get(Val::Int(1i64))?)?,binary("mul",e.get("axis")?.get(Val::Int(1i64))?,e.get("q")?.get(Val::Int(0i64))?)?)?);Val::tuple(s)};e.set("cross",assigned166.clone())?;
let assigned167={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun170=e.get("sum")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push({let e=e.child();let out171=Val::list(vec![]);for item172 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun175=e.get("zip")?;let mut args173=Vec::new();let mut kw174=Vec::new();args173.push(e.get("axis")?);args173.push(e.get("q")?);fun175.call(args173,kw174)?}}.iter()? {let unpack176=unpack(item172,2)?;e.set("a",unpack176[0].clone())?;e.set("b",unpack176[1].clone())?;out171.attr("append")?.call(vec![binary("mul",e.get("a")?,e.get("b")?)?],vec![])?;}out171});fun170.call(args168,kw169)?}};e.set("dot",assigned167.clone())?;
return Ok({let e=e.child();let out177=Val::list(vec![]);for item178 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun181=e.get("range")?;let mut args179=Vec::new();let mut kw180=Vec::new();args179.push(Val::Int(3i64));fun181.call(args179,kw180)?}}.iter()? {e.set("k",item178)?;out177.attr("append")?.call(vec![binary("add",binary("add",binary("add",e.get("origin")?.get(e.get("k")?)?,binary("mul",e.get("c")?,e.get("q")?.get(e.get("k")?)?)?)?,binary("mul",e.get("s")?,e.get("cross")?.get(e.get("k")?)?)?)?,binary("mul",binary("mul",binary("sub",Val::Int(1i64),e.get("c")?)?,e.get("dot")?)?,e.get("axis")?.get(e.get("k")?)?)?)?],vec![])?;}out177});
Ok(Val::None)})})?;
let assigned182=if {let v183=e.get("self")?.attr("bounds")?;let v184=Val::None;Val::Bool(compare("is_not",v183.clone(),v184.clone())?.truthy()?)}.truthy()? {{let e=e.child();let out185=Val::list(vec![]);for item186 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun189=e.get("product")?;let mut args187=Vec::new();let mut kw188=Vec::new();args187.extend({let e=e.child();let out190=Val::list(vec![]);for item191 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun194=e.get("range")?;let mut args192=Vec::new();let mut kw193=Vec::new();args192.push(Val::Int(3i64));fun194.call(args192,kw193)?}}.iter()? {e.set("k",item191)?;out190.attr("append")?.call(vec![e.get("self")?.attr("bounds")?.get(Val::Slice{start:Some(binary("mul",Val::Int(2i64),e.get("k")?)?.integer()?),stop:Some(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(2i64))?.integer()?),step:1})?],vec![])?;}out190}.iter()?);fun189.call(args187,kw188)?}}.iter()? {e.set("p",item186)?;out185.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun197=e.get("point")?;let mut args195=Vec::new();let mut kw196=Vec::new();args195.push(e.get("p")?);fun197.call(args195,kw196)?}}],vec![])?;}out185}} else {Val::None};e.set("corners",assigned182.clone())?;
let assigned198=if {let v199=e.get("corners")?;let v200=Val::None;Val::Bool(compare("is_not",v199.clone(),v200.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun203=e.get("tuple")?;let mut args201=Vec::new();let mut kw202=Vec::new();args201.push({let e=e.child();let out204=Val::list(vec![]);for item205 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun208=e.get("range")?;let mut args206=Vec::new();let mut kw207=Vec::new();args206.push(Val::Int(3i64));fun208.call(args206,kw207)?}}.iter()? {e.set("k",item205)?;for item209 in {let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun212=e.get("min")?;let mut args210=Vec::new();let mut kw211=Vec::new();args210.push({let e=e.child();let out213=Val::list(vec![]);for item214 in e.get("corners")?.iter()? {e.set("p",item214)?;out213.attr("append")?.call(vec![e.get("p")?.get(e.get("k")?)?],vec![])?;}out213});fun212.call(args210,kw211)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun217=e.get("max")?;let mut args215=Vec::new();let mut kw216=Vec::new();args215.push({let e=e.child();let out218=Val::list(vec![]);for item219 in e.get("corners")?.iter()? {e.set("p",item219)?;out218.attr("append")?.call(vec![e.get("p")?.get(e.get("k")?)?],vec![])?;}out218});fun217.call(args215,kw216)?}});Val::tuple(s)}.iter()? {e.set("v",item209)?;out204.attr("append")?.call(vec![e.get("v")?],vec![])?;}}out204});fun203.call(args201,kw202)?}}} else {Val::None};e.set("bounds",assigned198.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun222=e.get("self")?.attr("graph")?.attr("add")?;let mut args220=Vec::new();let mut kw221=Vec::new();args220.push(Val::Str("rotate".into()));args220.push({let mut s=Vec::new();s.push(e.get("self")?.attr("index")?);Val::list(s)});kw221.push(("origin".into(),e.get("origin")?));kw221.push(("end".into(),e.get("end")?));kw221.push(("angle".into(),e.get("angle")?));kw221.push(("bounds".into(),e.get("bounds")?));fun222.call(args220,kw221)?}});
Ok(Val::None)})})?;
    e.set("_Shape.mirror", {
        let params = vec![("self".into(), None, false), ("plane".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned223 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("YZ".into()), Val::Int(0i64))?;
                d.set(Val::Str("XZ".into()), Val::Int(1i64))?;
                d.set(Val::Str("XY".into()), Val::Int(2i64))?;
                d
            }
            .get(e.get("plane")?)?;
            e.set("axis", assigned223.clone())?;
            let assigned224 = if {
                let v225 = e.get("self")?.attr("bounds")?;
                let v226 = Val::None;
                Val::Bool(compare("is_not", v225.clone(), v226.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                        line!(),
                    );
                    {
                        let fun229 = e.get("list")?;
                        let mut args227 = Vec::new();
                        let mut kw228 = Vec::new();
                        args227.push(e.get("self")?.attr("bounds")?);
                        fun229.call(args227, kw228)?
                    }
                }
            } else {
                Val::None
            };
            e.set("bounds", assigned224.clone())?;
            if {
                let v230 = e.get("bounds")?;
                let v231 = Val::None;
                Val::Bool(compare("is_not", v230.clone(), v231.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned232 = {
                    let mut s = Vec::new();
                    s.push(unary(
                        "neg",
                        e.get("bounds")?.get(binary(
                            "add",
                            binary("mul", Val::Int(2i64), e.get("axis")?)?,
                            Val::Int(1i64),
                        )?)?,
                    )?);
                    s.push(unary(
                        "neg",
                        e.get("bounds")?
                            .get(binary("mul", Val::Int(2i64), e.get("axis")?)?)?,
                    )?);
                    Val::list(s)
                };
                e.get("bounds")?.set(
                    Val::Slice {
                        start: Some(binary("mul", Val::Int(2i64), e.get("axis")?)?.integer()?),
                        stop: Some(
                            binary(
                                "add",
                                binary("mul", Val::Int(2i64), e.get("axis")?)?,
                                Val::Int(2i64),
                            )?
                            .integer()?,
                        ),
                        step: 1,
                    },
                    assigned232.clone(),
                )?;
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun235 = e.get("self")?.attr("graph")?.attr("add")?;
                    let mut args233 = Vec::new();
                    let mut kw234 = Vec::new();
                    args233.push(Val::Str("mirror".into()));
                    args233.push({
                        let mut s = Vec::new();
                        s.push(e.get("self")?.attr("index")?);
                        Val::list(s)
                    });
                    kw234.push(("axis".into(), e.get("axis")?));
                    kw234.push(("bounds".into(), e.get("bounds")?));
                    fun235.call(args233, kw234)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Shape.clean", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("self")?);
            Ok(Val::None)
        })
    })?;
    e.set("_Shape.val", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("self")?);
            Ok(Val::None)
        })
    })?;
    e.set("_Shape.BoundingBox", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod236 = rt.import_module("types")?;
            e.set("SimpleNamespace", rt.member("types", "SimpleNamespace")?)?;
            if {
                let v237 = e.get("self")?.attr("bounds")?;
                let v238 = Val::None;
                Val::Bool(compare("is", v237.clone(), v238.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun241 = e.get("ValueError")?;
                            let mut args239 = Vec::new();
                            let mut kw240 = Vec::new();
                            args239.push(Val::Str(
                                "this private feature has no conservative numeric bounds".into(),
                            ));
                            fun241.call(args239, kw240)?
                        }
                    })?
                );
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun244 = e.get("SimpleNamespace")?;
                    let mut args242 = Vec::new();
                    let mut kw243 = Vec::new();
                    kw243.extend(keyword_items({
                        let e = e.child();
                        let out245 = Val::dict(vec![]);
                        for item246 in {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                                line!(),
                            );
                            {
                                let fun249 = e.get("enumerate")?;
                                let mut args247 = Vec::new();
                                let mut kw248 = Vec::new();
                                args247.push(Val::Str("xyz".into()));
                                fun249.call(args247, kw248)?
                            }
                        }
                        .iter()?
                        {
                            let unpack250 = unpack(item246, 2)?;
                            e.set("k", unpack250[0].clone())?;
                            e.set("axis", unpack250[1].clone())?;
                            for item251 in {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                                    line!(),
                                );
                                {
                                    let fun254 = e.get("enumerate")?;
                                    let mut args252 = Vec::new();
                                    let mut kw253 = Vec::new();
                                    args252.push({
                                        let mut s = Vec::new();
                                        s.push(binary(
                                            "add",
                                            e.get("axis")?,
                                            Val::Str("min".into()),
                                        )?);
                                        s.push(binary(
                                            "add",
                                            e.get("axis")?,
                                            Val::Str("max".into()),
                                        )?);
                                        Val::tuple(s)
                                    });
                                    fun254.call(args252, kw253)?
                                }
                            }
                            .iter()?
                            {
                                let unpack255 = unpack(item251, 2)?;
                                e.set("i", unpack255[0].clone())?;
                                e.set("key", unpack255[1].clone())?;
                                out245.set(
                                    e.get("key")?,
                                    e.get("self")?.attr("bounds")?.get(binary(
                                        "add",
                                        binary("mul", Val::Int(2i64), e.get("k")?)?,
                                        e.get("i")?,
                                    )?)?,
                                )?;
                            }
                        }
                        out245
                    })?);
                    fun244.call(args242, kw243)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Shape.Solids", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("self")?);
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Shape", rt.python_type("_enclosure_panel", "_Shape")?)?;
    e.set("_Graph.__init__", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned256 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.get("self")?.setattr("nodes", assigned256.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("_Graph.add", {
        let params = vec![
            ("self".into(), None, false),
            ("op".into(), None, false),
            (
                "inputs".into(),
                Some({
                    let mut s = Vec::new();
                    Val::tuple(s)
                }),
                false,
            ),
            ("bounds".into(), Some(Val::None), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, Some("numbers"))?;
            let _frame = rt.frame(&outer);
            let assigned257 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun260 = e.get("len")?;
                    let mut args258 = Vec::new();
                    let mut kw259 = Vec::new();
                    args258.push(e.get("self")?.attr("nodes")?);
                    fun260.call(args258, kw259)?
                }
            };
            e.set("index", assigned257.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun263 = e.get("self")?.attr("nodes")?.attr("append")?;
                    let mut args261 = Vec::new();
                    let mut kw262 = Vec::new();
                    args261.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun266 = e.get("dict")?;
                            let mut args264 = Vec::new();
                            let mut kw265 = Vec::new();
                            kw265.push(("op".into(), e.get("op")?));
                            kw265.push(("inputs".into(), {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                                    line!(),
                                );
                                {
                                    let fun269 = e.get("list")?;
                                    let mut args267 = Vec::new();
                                    let mut kw268 = Vec::new();
                                    args267.push(e.get("inputs")?);
                                    fun269.call(args267, kw268)?
                                }
                            }));
                            kw265.push(("source".into(), {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                                    line!(),
                                );
                                {
                                    let fun272 = e.get("_source_info")?;
                                    let mut args270 = Vec::new();
                                    let mut kw271 = Vec::new();
                                    fun272.call(args270, kw271)?
                                }
                            }));
                            kw265.extend(keyword_items(e.get("numbers")?)?);
                            fun266.call(args264, kw265)?
                        }
                    });
                    fun263.call(args261, kw262)?
                }
            };
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun275 = e.get("_Shape")?;
                    let mut args273 = Vec::new();
                    let mut kw274 = Vec::new();
                    args273.push(e.get("self")?);
                    args273.push(e.get("index")?);
                    args273.push(e.get("bounds")?);
                    fun275.call(args273, kw274)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Graph.box", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, Some("bounds"), None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun278 = e.get("self")?.attr("add")?;
                    let mut args276 = Vec::new();
                    let mut kw277 = Vec::new();
                    args276.push(Val::Str("box".into()));
                    kw277.push(("bounds".into(), e.get("bounds")?));
                    kw277.push(("box".into(), e.get("bounds")?));
                    fun278.call(args276, kw277)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Graph.cylinder", {
        let params = vec![
            ("self".into(), None, false),
            ("axis".into(), None, false),
            ("radius".into(), None, false),
            ("a".into(), None, false),
            ("b".into(), None, false),
            ("lo".into(), None, false),
            ("hi".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned279 = {
                let e = e.child();
                let out280 = Val::list(vec![]);
                for item281 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                        line!(),
                    );
                    {
                        let fun284 = e.get("range")?;
                        let mut args282 = Vec::new();
                        let mut kw283 = Vec::new();
                        args282.push(Val::Int(3i64));
                        fun284.call(args282, kw283)?
                    }
                }
                .iter()?
                {
                    e.set("k", item281)?;
                    if {
                        let v285 = e.get("k")?;
                        let v286 = e.get("axis")?;
                        Val::Bool(compare("ne", v285.clone(), v286.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out280.attr("append")?.call(vec![e.get("k")?], vec![])?;
                    }
                }
                out280
            };
            e.set("other", assigned279.clone())?;
            let assigned287 = binary(
                "mul",
                {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    Val::list(s)
                },
                Val::Int(6i64),
            )?;
            e.set("bounds", assigned287.clone())?;
            let assigned288 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun291 = e.get("sorted")?;
                    let mut args289 = Vec::new();
                    let mut kw290 = Vec::new();
                    args289.push({
                        let mut s = Vec::new();
                        s.push(e.get("lo")?);
                        s.push(e.get("hi")?);
                        Val::tuple(s)
                    });
                    fun291.call(args289, kw290)?
                }
            };
            e.get("bounds")?.set(
                Val::Slice {
                    start: Some(binary("mul", Val::Int(2i64), e.get("axis")?)?.integer()?),
                    stop: Some(
                        binary(
                            "add",
                            binary("mul", Val::Int(2i64), e.get("axis")?)?,
                            Val::Int(2i64),
                        )?
                        .integer()?,
                    ),
                    step: 1,
                },
                assigned288.clone(),
            )?;
            for item292 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun295 = e.get("zip")?;
                    let mut args293 = Vec::new();
                    let mut kw294 = Vec::new();
                    args293.push(e.get("other")?);
                    args293.push({
                        let mut s = Vec::new();
                        s.push(e.get("a")?);
                        s.push(e.get("b")?);
                        Val::tuple(s)
                    });
                    fun295.call(args293, kw294)?
                }
            }
            .iter()?
            {
                let unpack296 = unpack(item292, 2)?;
                e.set("k", unpack296[0].clone())?;
                e.set("centre", unpack296[1].clone())?;
                let assigned297 = {
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("centre")?, e.get("radius")?)?);
                    s.push(binary("add", e.get("centre")?, e.get("radius")?)?);
                    Val::list(s)
                };
                e.get("bounds")?.set(
                    Val::Slice {
                        start: Some(binary("mul", Val::Int(2i64), e.get("k")?)?.integer()?),
                        stop: Some(
                            binary(
                                "add",
                                binary("mul", Val::Int(2i64), e.get("k")?)?,
                                Val::Int(2i64),
                            )?
                            .integer()?,
                        ),
                        step: 1,
                    },
                    assigned297.clone(),
                )?;
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun300 = e.get("self")?.attr("add")?;
                    let mut args298 = Vec::new();
                    let mut kw299 = Vec::new();
                    args298.push(Val::Str("cylinder".into()));
                    kw299.push(("axis".into(), e.get("axis")?));
                    kw299.push(("radius".into(), e.get("radius")?));
                    kw299.push(("centre".into(), {
                        let mut s = Vec::new();
                        s.push(e.get("a")?);
                        s.push(e.get("b")?);
                        Val::tuple(s)
                    }));
                    kw299.push(("span".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun303 = e.get("sorted")?;
                            let mut args301 = Vec::new();
                            let mut kw302 = Vec::new();
                            args301.push({
                                let mut s = Vec::new();
                                s.push(e.get("lo")?);
                                s.push(e.get("hi")?);
                                Val::tuple(s)
                            });
                            fun303.call(args301, kw302)?
                        }
                    }));
                    kw299.push(("bounds".into(), e.get("bounds")?));
                    fun300.call(args298, kw299)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Graph.prism", {
        let params = vec![
            ("self".into(), None, false),
            ("axis".into(), None, false),
            ("lo".into(), None, false),
            ("hi".into(), None, false),
            ("section".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned304 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun307 = e.get("tuple")?;
                    let mut args305 = Vec::new();
                    let mut kw306 = Vec::new();
                    args305.push(e.get("section")?);
                    fun307.call(args305, kw306)?
                }
            };
            e.set("section", assigned304.clone())?;
            let assigned308 = {
                let e = e.child();
                let out309 = Val::list(vec![]);
                for item310 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                        line!(),
                    );
                    {
                        let fun313 = e.get("range")?;
                        let mut args311 = Vec::new();
                        let mut kw312 = Vec::new();
                        args311.push(Val::Int(3i64));
                        fun313.call(args311, kw312)?
                    }
                }
                .iter()?
                {
                    e.set("k", item310)?;
                    if {
                        let v314 = e.get("k")?;
                        let v315 = e.get("axis")?;
                        Val::Bool(compare("ne", v314.clone(), v315.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out309.attr("append")?.call(vec![e.get("k")?], vec![])?;
                    }
                }
                out309
            };
            e.set("other", assigned308.clone())?;
            let assigned316 = binary(
                "mul",
                {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    Val::list(s)
                },
                Val::Int(6i64),
            )?;
            e.set("bounds", assigned316.clone())?;
            let assigned317 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun320 = e.get("sorted")?;
                    let mut args318 = Vec::new();
                    let mut kw319 = Vec::new();
                    args318.push({
                        let mut s = Vec::new();
                        s.push(e.get("lo")?);
                        s.push(e.get("hi")?);
                        Val::tuple(s)
                    });
                    fun320.call(args318, kw319)?
                }
            };
            e.get("bounds")?.set(
                Val::Slice {
                    start: Some(binary("mul", Val::Int(2i64), e.get("axis")?)?.integer()?),
                    stop: Some(
                        binary(
                            "add",
                            binary("mul", Val::Int(2i64), e.get("axis")?)?,
                            Val::Int(2i64),
                        )?
                        .integer()?,
                    ),
                    step: 1,
                },
                assigned317.clone(),
            )?;
            for item321 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun324 = e.get("enumerate")?;
                    let mut args322 = Vec::new();
                    let mut kw323 = Vec::new();
                    args322.push(e.get("other")?);
                    fun324.call(args322, kw323)?
                }
            }
            .iter()?
            {
                let unpack325 = unpack(item321, 2)?;
                e.set("i", unpack325[0].clone())?;
                e.set("k", unpack325[1].clone())?;
                let assigned326 = {
                    let mut s = Vec::new();
                    s.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun329 = e.get("min")?;
                            let mut args327 = Vec::new();
                            let mut kw328 = Vec::new();
                            args327.push({
                                let e = e.child();
                                let out330 = Val::list(vec![]);
                                for item331 in e.get("section")?.iter()? {
                                    e.set("p", item331)?;
                                    out330
                                        .attr("append")?
                                        .call(vec![e.get("p")?.get(e.get("i")?)?], vec![])?;
                                }
                                out330
                            });
                            fun329.call(args327, kw328)?
                        }
                    });
                    s.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun334 = e.get("max")?;
                            let mut args332 = Vec::new();
                            let mut kw333 = Vec::new();
                            args332.push({
                                let e = e.child();
                                let out335 = Val::list(vec![]);
                                for item336 in e.get("section")?.iter()? {
                                    e.set("p", item336)?;
                                    out335
                                        .attr("append")?
                                        .call(vec![e.get("p")?.get(e.get("i")?)?], vec![])?;
                                }
                                out335
                            });
                            fun334.call(args332, kw333)?
                        }
                    });
                    Val::list(s)
                };
                e.get("bounds")?.set(
                    Val::Slice {
                        start: Some(binary("mul", Val::Int(2i64), e.get("k")?)?.integer()?),
                        stop: Some(
                            binary(
                                "add",
                                binary("mul", Val::Int(2i64), e.get("k")?)?,
                                Val::Int(2i64),
                            )?
                            .integer()?,
                        ),
                        step: 1,
                    },
                    assigned326.clone(),
                )?;
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun339 = e.get("self")?.attr("add")?;
                    let mut args337 = Vec::new();
                    let mut kw338 = Vec::new();
                    args337.push(Val::Str("prism".into()));
                    kw338.push(("axis".into(), e.get("axis")?));
                    kw338.push(("span".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun342 = e.get("sorted")?;
                            let mut args340 = Vec::new();
                            let mut kw341 = Vec::new();
                            args340.push({
                                let mut s = Vec::new();
                                s.push(e.get("lo")?);
                                s.push(e.get("hi")?);
                                Val::tuple(s)
                            });
                            fun342.call(args340, kw341)?
                        }
                    }));
                    kw338.push(("section".into(), e.get("section")?));
                    kw338.push(("bounds".into(), e.get("bounds")?));
                    fun339.call(args337, kw338)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Graph.rounded", {
        let params = vec![
            ("self".into(), None, false),
            ("shape".into(), None, false),
            ("radius".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v343 = e.get("radius")?;
                let v344 = Val::Int(0i64);
                Val::Bool(compare("le", v343.clone(), v344.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("shape")?);
            }
            if {
                let v345 = e
                    .get("self")?
                    .attr("nodes")?
                    .get(e.get("shape")?.attr("index")?)?
                    .get(Val::Str("op".into()))?;
                let v346 = Val::Str("box".into());
                Val::Bool(compare("ne", v345.clone(), v346.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun349 = e.get("ValueError")?;
                            let mut args347 = Vec::new();
                            let mut kw348 = Vec::new();
                            args347.push(Val::Str(
                                "the enclosure standing round belongs to rectangular stock".into(),
                            ));
                            fun349.call(args347, kw348)?
                        }
                    })?
                );
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun352 = e.get("self")?.attr("add")?;
                    let mut args350 = Vec::new();
                    let mut kw351 = Vec::new();
                    args350.push(Val::Str("rounded-box".into()));
                    kw351.push(("box".into(), e.get("shape")?.attr("bounds")?));
                    kw351.push(("radius".into(), e.get("radius")?));
                    kw351.push(("bounds".into(), e.get("shape")?.attr("bounds")?));
                    fun352.call(args350, kw351)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Graph.document", {
        let params = vec![
            ("self".into(), None, false),
            ("result".into(), None, false),
            ("extras".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned353 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun356 = e.get("set")?;
                    let mut args354 = Vec::new();
                    let mut kw355 = Vec::new();
                    fun356.call(args354, kw355)?
                }
            };
            e.set("reachable", assigned353.clone())?;
            // visit
            e.set("visit", {
                let params = vec![("index".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    if {
                        let v357 = e.get("index")?;
                        let v358 = e.get("reachable")?;
                        Val::Bool(compare("in", v357.clone(), v358.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        return Ok(Val::None);
                    }
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun361 = e.get("reachable")?.attr("add")?;
                            let mut args359 = Vec::new();
                            let mut kw360 = Vec::new();
                            args359.push(e.get("index")?);
                            fun361.call(args359, kw360)?
                        }
                    };
                    for item362 in e
                        .get("self")?
                        .attr("nodes")?
                        .get(e.get("index")?)?
                        .get(Val::Str("inputs".into()))?
                        .iter()?
                    {
                        e.set("child", item362)?;
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                                line!(),
                            );
                            {
                                let fun365 = e.get("visit")?;
                                let mut args363 = Vec::new();
                                let mut kw364 = Vec::new();
                                args363.push(e.get("child")?);
                                fun365.call(args363, kw364)?
                            }
                        };
                    }
                    Ok(Val::None)
                })
            })?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun368 = e.get("visit")?;
                    let mut args366 = Vec::new();
                    let mut kw367 = Vec::new();
                    args366.push(e.get("result")?.attr("index")?);
                    fun368.call(args366, kw367)?
                }
            };
            for item369 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun372 = {
                        let v373 = e.get("extras")?;
                        if v373.truthy()? {
                            v373
                        } else {
                            {
                                let d = Val::dict(vec![]);
                                d
                            }
                        }
                    }
                    .attr("values")?;
                    let mut args370 = Vec::new();
                    let mut kw371 = Vec::new();
                    fun372.call(args370, kw371)?
                }
            }
            .iter()?
            {
                e.set("shape", item369)?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                        line!(),
                    );
                    {
                        let fun376 = e.get("visit")?;
                        let mut args374 = Vec::new();
                        let mut kw375 = Vec::new();
                        args374.push(e.get("shape")?.attr("index")?);
                        fun376.call(args374, kw375)?
                    }
                };
            }
            let assigned377 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun380 = e.get("sorted")?;
                    let mut args378 = Vec::new();
                    let mut kw379 = Vec::new();
                    args378.push(e.get("reachable")?);
                    fun380.call(args378, kw379)?
                }
            };
            e.set("order", assigned377.clone())?;
            let assigned381 = {
                let e = e.child();
                let out382 = Val::dict(vec![]);
                for item383 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                        line!(),
                    );
                    {
                        let fun386 = e.get("enumerate")?;
                        let mut args384 = Vec::new();
                        let mut kw385 = Vec::new();
                        args384.push(e.get("order")?);
                        fun386.call(args384, kw385)?
                    }
                }
                .iter()?
                {
                    let unpack387 = unpack(item383, 2)?;
                    e.set("new", unpack387[0].clone())?;
                    e.set("old", unpack387[1].clone())?;
                    out382.set(e.get("old")?, e.get("new")?)?;
                }
                out382
            };
            e.set("remap", assigned381.clone())?;
            let assigned388 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun391 = e.get("dict")?;
                    let mut args389 = Vec::new();
                    let mut kw390 = Vec::new();
                    kw390.push(("nodes".into(), {
                        let e = e.child();
                        let out392 = Val::list(vec![]);
                        for item393 in e.get("order")?.iter()? {
                            e.set("i", item393)?;
                            out392.attr("append")?.call(
                                vec![{
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                                        line!(),
                                    );
                                    {
                                        let fun396 = e.get("dict")?;
                                        let mut args394 = Vec::new();
                                        let mut kw395 = Vec::new();
                                        args394
                                            .push(e.get("self")?.attr("nodes")?.get(e.get("i")?)?);
                                        kw395.push(("inputs".into(), {
                                            let e = e.child();
                                            let out397 = Val::list(vec![]);
                                            for item398 in e
                                                .get("self")?
                                                .attr("nodes")?
                                                .get(e.get("i")?)?
                                                .get(Val::Str("inputs".into()))?
                                                .iter()?
                                            {
                                                e.set("k", item398)?;
                                                out397.attr("append")?.call(
                                                    vec![e.get("remap")?.get(e.get("k")?)?],
                                                    vec![],
                                                )?;
                                            }
                                            out397
                                        }));
                                        fun396.call(args394, kw395)?
                                    }
                                }],
                                vec![],
                            )?;
                        }
                        out392
                    }));
                    kw390.push((
                        "result".into(),
                        e.get("remap")?.get(e.get("result")?.attr("index")?)?,
                    ));
                    fun391.call(args389, kw390)?
                }
            };
            e.set("out", assigned388.clone())?;
            if e.get("extras")?.truthy()? {
                let assigned399 = {
                    let e = e.child();
                    let out400 = Val::dict(vec![]);
                    for item401 in {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun404 = e.get("extras")?.attr("items")?;
                            let mut args402 = Vec::new();
                            let mut kw403 = Vec::new();
                            fun404.call(args402, kw403)?
                        }
                    }
                    .iter()?
                    {
                        let unpack405 = unpack(item401, 2)?;
                        e.set("key", unpack405[0].clone())?;
                        e.set("shape", unpack405[1].clone())?;
                        out400.set(
                            e.get("key")?,
                            e.get("remap")?.get(e.get("shape")?.attr("index")?)?,
                        )?;
                    }
                    out400
                };
                e.get("out")?
                    .set(Val::Str("extras".into()), assigned399.clone())?;
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    e.set("_Graph", rt.python_type("_enclosure_panel", "_Graph")?)?;
    e.set("_record",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("structure".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;
            let enter_e=e.clone();let enter_rt=rt.clone();
            let enter=Val::function(move|_,_|{let e=enter_e.clone();let rt=enter_rt.clone();let _frame=rt.frame(&e);
        // teardrop_y
e.set("teardrop_y",{let params=vec![("radius".into(),None,false),("x".into(),None,false),("z".into(),None,false),("y0".into(),None,false),("y1".into(),None,false),("up".into(),Some(Val::Float(1.0f64)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("math",rt.import_module("math")?)?;
let assigned406={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun409=e.get("math")?.attr("radians")?;let mut args407=Vec::new();let mut kw408=Vec::new();args407.push(e.get("shell")?.attr("teardrop_roof_angle")?);fun409.call(args407,kw408)?}};e.set("angle",assigned406.clone())?;
let assigned410=binary("mul",e.get("radius")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun413=e.get("math")?.attr("sin")?;let mut args411=Vec::new();let mut kw412=Vec::new();args411.push(e.get("angle")?);fun413.call(args411,kw412)?}})?;e.set("half",assigned410.clone())?;
let assigned414=binary("add",e.get("z")?,binary("mul",binary("mul",e.get("up")?,e.get("radius")?)?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun417=e.get("math")?.attr("cos")?;let mut args415=Vec::new();let mut kw416=Vec::new();args415.push(e.get("angle")?);fun417.call(args415,kw416)?}})?)?;e.set("tangent",assigned414.clone())?;
let assigned418=binary("add",e.get("z")?,binary("truediv",binary("mul",e.get("up")?,e.get("radius")?)?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun421=e.get("math")?.attr("cos")?;let mut args419=Vec::new();let mut kw420=Vec::new();args419.push(e.get("angle")?);fun421.call(args419,kw420)?}})?)?;e.set("apex",assigned418.clone())?;
let assigned422={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun425=e.get("graph")?.attr("add")?;let mut args423=Vec::new();let mut kw424=Vec::new();args423.push(Val::Str("cylinder".into()));kw424.push(("axis".into(),Val::Int(1i64)));kw424.push(("radius".into(),e.get("radius")?));kw424.push(("centre".into(),{let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("z")?);Val::tuple(s)}));kw424.push(("span".into(),{let mut s=Vec::new();s.push(e.get("y0")?);s.push(e.get("y1")?);Val::tuple(s)}));kw424.push(("stations".into(),{let mut s=Vec::new();s.push(binary("sub",binary("truediv",binary("mul",e.get("up")?,e.get("math")?.attr("pi")?)?,Val::Int(2i64))?,e.get("angle")?)?);s.push(binary("add",binary("truediv",binary("mul",e.get("up")?,e.get("math")?.attr("pi")?)?,Val::Int(2i64))?,e.get("angle")?)?);Val::tuple(s)}));kw424.push(("bounds".into(),{let mut s=Vec::new();s.push(binary("sub",e.get("x")?,e.get("radius")?)?);s.push(binary("add",e.get("x")?,e.get("radius")?)?);s.push(e.get("y0")?);s.push(e.get("y1")?);s.push(binary("sub",e.get("z")?,e.get("radius")?)?);s.push(binary("add",e.get("z")?,e.get("radius")?)?);Val::tuple(s)}));fun425.call(args423,kw424)?}};e.set("circle",assigned422.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun428=e.get("circle")?.attr("fuse")?;let mut args426=Vec::new();let mut kw427=Vec::new();args426.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun431=e.get("graph")?.attr("prism")?;let mut args429=Vec::new();let mut kw430=Vec::new();args429.push(Val::Int(1i64));args429.push(e.get("y0")?);args429.push(e.get("y1")?);args429.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("sub",e.get("x")?,e.get("half")?)?);s.push(e.get("tangent")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",e.get("x")?,e.get("half")?)?);s.push(e.get("tangent")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("apex")?);Val::tuple(s)});Val::tuple(s)});fun431.call(args429,kw430)?}});fun428.call(args426,kw427)?}});
Ok(Val::None)})})?;
// handhold_cutter
e.set("handhold_cutter",{let params=vec![("inner".into(),None,false),("x_ext".into(),None,false),("sx".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned432={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun435=e.get("shell")?.attr("_handhold_levels")?;let mut args433=Vec::new();let mut kw434=Vec::new();args433.push(e.get("inner")?);fun435.call(args433,kw434)?}};let unpack436=unpack(assigned432.clone(),3)?;e.set("bed",unpack436[0].clone())?;e.set("roof",unpack436[1].clone())?;e.set("_crown",unpack436[2].clone())?;
let assigned437={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun440=e.get("shell")?.attr("_handhold_y")?;let mut args438=Vec::new();let mut kw439=Vec::new();fun440.call(args438,kw439)?}};let unpack441=unpack(assigned437.clone(),2)?;e.set("y0",unpack441[0].clone())?;e.set("y1",unpack441[1].clone())?;
let assigned442={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun445=e.get("shell")?.attr("_band_x")?;let mut args443=Vec::new();let mut kw444=Vec::new();args443.push(e.get("x_ext")?);args443.push(e.get("sx")?);fun445.call(args443,kw444)?}};let unpack446=unpack(assigned442.clone(),2)?;e.set("_flank",unpack446[0].clone())?;e.set("cap",unpack446[1].clone())?;
let assigned447={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun450=e.get("sorted")?;let mut args448=Vec::new();let mut kw449=Vec::new();args448.push({let mut s=Vec::new();s.push(binary("sub",e.get("cap")?,binary("mul",e.get("sx")?,e.get("shell")?.attr("handhold_wall")?)?)?);s.push(binary("sub",e.get("x_ext")?,e.get("sx")?)?);Val::tuple(s)});fun450.call(args448,kw449)?}};let unpack451=unpack(assigned447.clone(),2)?;e.set("xa",unpack451[0].clone())?;e.set("xb",unpack451[1].clone())?;
let assigned452={let mut s=Vec::new();s.push(e.get("xa")?);s.push(e.get("xb")?);s.push(e.get("y0")?);s.push(e.get("y1")?);s.push(binary("sub",e.get("bed")?,Val::Float(1.0f64))?);s.push(e.get("roof")?);Val::tuple(s)};e.set("bounds",assigned452.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun455=e.get("graph")?.attr("add")?;let mut args453=Vec::new();let mut kw454=Vec::new();args453.push(Val::Str("handhold-cutter".into()));kw454.push(("box".into(),e.get("bounds")?));kw454.push(("radius".into(),e.get("shell")?.attr("handhold_corner_r")?));kw454.push(("bounds".into(),e.get("bounds")?));fun455.call(args453,kw454)?}});
Ok(Val::None)})})?;
e.set("handhold_finish",memoize({let params=vec![("inner".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned456={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun459=e.get("shell")?.attr("_handhold_levels")?;let mut args457=Vec::new();let mut kw458=Vec::new();args457.push(e.get("inner")?);fun459.call(args457,kw458)?}};let unpack460=unpack(assigned456.clone(),3)?;e.set("bed",unpack460[0].clone())?;e.set("roof",unpack460[1].clone())?;e.set("crown",unpack460[2].clone())?;
let assigned461={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun464=e.get("shell")?.attr("_handhold_y")?;let mut args462=Vec::new();let mut kw463=Vec::new();fun464.call(args462,kw463)?}};let unpack465=unpack(assigned461.clone(),2)?;e.set("y0",unpack465[0].clone())?;e.set("y1",unpack465[1].clone())?;
let assigned466=binary("add",e.get("shell")?.attr("wall")?,e.get("shell")?.attr("y_stack_low_depth")?)?;e.set("depth",assigned466.clone())?;
let assigned467=binary("add",binary("add",e.get("shell")?.attr("handhold_corner_r")?,e.get("shell")?.attr("handhold_edge_r")?)?,e.get("shell")?.attr("handhold_wall")?)?;e.set("end",assigned467.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun470=e.get("graph")?.attr("add")?;let mut args468=Vec::new();let mut kw469=Vec::new();args468.push(Val::Str("handhold-finish-air".into()));kw469.push(("bed".into(),e.get("bed")?));kw469.push(("roof".into(),e.get("roof")?));kw469.push(("crown".into(),e.get("crown")?));kw469.push(("y".into(),{let mut s=Vec::new();s.push(e.get("y0")?);s.push(e.get("y1")?);Val::list(s)}));kw469.push(("depth".into(),e.get("depth")?));kw469.push(("corner".into(),e.get("shell")?.attr("handhold_corner_r")?));kw469.push(("radius".into(),e.get("shell")?.attr("handhold_edge_r")?));kw469.push(("end_stock".into(),e.get("end")?));kw469.push(("cutter_depth".into(),binary("sub",e.get("depth")?,e.get("shell")?.attr("handhold_wall")?)?));kw469.push(("slope".into(),e.get("_enclosure_structure")?.attr("OUTWARD_PER_HEIGHT")?));kw469.push(("bounds".into(),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(e.get("depth")?);s.push(binary("sub",e.get("y0")?,e.get("end")?)?);s.push(binary("add",e.get("y1")?,e.get("end")?)?);s.push(e.get("bed")?);s.push(e.get("crown")?);Val::tuple(s)}));fun470.call(args468,kw469)?}});
Ok(Val::None)})},None))?;let mod471=rt.import_module("_disposal_artwork")?;e.set("warning_artwork",rt.member("_disposal_artwork","numbers")?)?;
let assigned472={let d=Val::dict(vec![]);d.set(Val::Str("_ybox".into()),e.get("graph")?.attr("box")?)?;d.set(Val::Str("_xcyl".into()),{let params=vec![("r".into(),None,false),("y".into(),None,false),("z".into(),None,false),("x0".into(),None,false),("x1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun475=e.get("graph")?.attr("cylinder")?;let mut args473=Vec::new();let mut kw474=Vec::new();args473.push(Val::Int(0i64));args473.push(e.get("r")?);args473.push(e.get("y")?);args473.push(e.get("z")?);args473.push(e.get("x0")?);args473.push(e.get("x1")?);fun475.call(args473,kw474)?}});
Ok(Val::None)})})?;d.set(Val::Str("_ycyl".into()),{let params=vec![("r".into(),None,false),("x".into(),None,false),("z".into(),None,false),("y0".into(),None,false),("y1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun478=e.get("graph")?.attr("cylinder")?;let mut args476=Vec::new();let mut kw477=Vec::new();args476.push(Val::Int(1i64));args476.push(e.get("r")?);args476.push(e.get("x")?);args476.push(e.get("z")?);args476.push(e.get("y0")?);args476.push(e.get("y1")?);fun478.call(args476,kw477)?}});
Ok(Val::None)})})?;d.set(Val::Str("_teardrop_y".into()),e.get("teardrop_y")?)?;d.set(Val::Str("_zcyl".into()),{let params=vec![("r".into(),None,false),("x".into(),None,false),("y".into(),None,false),("z0".into(),None,false),("z1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun481=e.get("graph")?.attr("cylinder")?;let mut args479=Vec::new();let mut kw480=Vec::new();args479.push(Val::Int(2i64));args479.push(e.get("r")?);args479.push(e.get("x")?);args479.push(e.get("y")?);args479.push(e.get("z0")?);args479.push(e.get("z1")?);fun481.call(args479,kw480)?}});
Ok(Val::None)})})?;d.set(Val::Str("_yz_prism".into()),{let params=vec![("x0".into(),None,false),("x1".into(),None,false),("section".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun484=e.get("graph")?.attr("prism")?;let mut args482=Vec::new();let mut kw483=Vec::new();args482.push(Val::Int(0i64));args482.push(e.get("x0")?);args482.push(e.get("x1")?);args482.push(e.get("section")?);fun484.call(args482,kw483)?}});
Ok(Val::None)})})?;d.set(Val::Str("_xz_prism".into()),{let params=vec![("y0".into(),None,false),("y1".into(),None,false),("section".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun487=e.get("graph")?.attr("prism")?;let mut args485=Vec::new();let mut kw486=Vec::new();args485.push(Val::Int(1i64));args485.push(e.get("y0")?);args485.push(e.get("y1")?);args485.push(e.get("section")?);fun487.call(args485,kw486)?}});
Ok(Val::None)})})?;d.set(Val::Str("_xy_prism".into()),{let params=vec![("z0".into(),None,false),("z1".into(),None,false),("section".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun490=e.get("graph")?.attr("prism")?;let mut args488=Vec::new();let mut kw489=Vec::new();args488.push(Val::Int(2i64));args488.push(e.get("z0")?);args488.push(e.get("z1")?);args488.push(e.get("section")?);fun490.call(args488,kw489)?}});
Ok(Val::None)})})?;d.set(Val::Str("_round_z".into()),e.get("graph")?.attr("rounded")?)?;d.set(Val::Str("_rounded_outer".into()),{let params=vec![("outer".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok(e.get("structure")?);
Ok(Val::None)})})?;d.set(Val::Str("_handhold_cutter".into()),e.get("handhold_cutter")?)?;d.set(Val::Str("_handhold_finish_air".into()),e.get("handhold_finish")?)?;d.set(Val::Str("disposal_letters".into()),{let params=vec![("outer".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun493=e.get("graph")?.attr("add")?;let mut args491=Vec::new();let mut kw492=Vec::new();args491.push(Val::Str("disposal-letters".into()));kw492.push(("outer".into(),e.get("outer")?));kw492.push(("lines".into(),e.get("shell")?.attr("disposal_lines")?));kw492.push(("family".into(),e.get("shell")?.attr("disposal_font")?));kw492.push(("artwork".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun496=e.get("warning_artwork")?;let mut args494=Vec::new();let mut kw495=Vec::new();args494.push(e.get("shell")?.attr("disposal_font")?);args494.push(e.get("shell")?.attr("disposal_kind")?);fun496.call(args494,kw495)?}}));kw492.push(("cap_height".into(),e.get("shell")?.attr("disposal_cap_height")?));kw492.push(("depth".into(),binary("add",e.get("shell")?.attr("disposal_raise")?,e.get("shell")?.attr("disposal_embed")?)?));kw492.push(("embed".into(),e.get("shell")?.attr("disposal_embed")?));kw492.push(("line_gap".into(),e.get("shell")?.attr("disposal_line_gap")?));kw492.push(("bottom".into(),e.get("shell")?.attr("disposal_bottom")?));fun493.call(args491,kw492)?}});
Ok(Val::None)})})?;d.set(Val::Str("_unified".into()),{let params=vec![("shape".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok(e.get("shape")?);
Ok(Val::None)})})?;d};e.set("replacements",assigned472.clone())?;
let assigned497={let e=e.child();let out498=Val::dict(vec![]);for item499 in e.get("replacements")?.iter()? {e.set("name",item499)?;out498.set(e.get("name")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun502=e.get("getattr")?;let mut args500=Vec::new();let mut kw501=Vec::new();args500.push(e.get("shell")?);args500.push(e.get("name")?);fun502.call(args500,kw501)?}})?;}out498};e.set("originals",assigned497.clone())?;
for item503 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun506=e.get("replacements")?.attr("items")?;let mut args504=Vec::new();let mut kw505=Vec::new();fun506.call(args504,kw505)?}}.iter()? {
let unpack507=unpack(item503,2)?;e.set("name",unpack507[0].clone())?;e.set("replacement",unpack507[1].clone())?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun510=e.get("setattr")?;let mut args508=Vec::new();let mut kw509=Vec::new();args508.push(e.get("shell")?);args508.push(e.get("name")?);args508.push(e.get("replacement")?);fun510.call(args508,kw509)?}};
}
Ok(Val::None)});
            let exit_e=e.clone();let exit_rt=rt.clone();
            let exit=Val::function(move|_,_|{let e=exit_e.clone();let rt=exit_rt.clone();let _frame=rt.frame(&e);
        for item511 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun514=e.get("originals")?.attr("items")?;let mut args512=Vec::new();let mut kw513=Vec::new();fun514.call(args512,kw513)?}}.iter()? {
let unpack515=unpack(item511,2)?;e.set("name",unpack515[0].clone())?;e.set("original",unpack515[1].clone())?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun518=e.get("setattr")?;let mut args516=Vec::new();let mut kw517=Vec::new();args516.push(e.get("shell")?);args516.push(e.get("name")?);args516.push(e.get("original")?);fun518.call(args516,kw517)?}};
}
Ok(Val::None)});Ok(context(enter,exit))})})?; // numbers
    e.set("numbers",{let params=vec![("shell".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned519={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun522=e.get("_Graph")?;let mut args520=Vec::new();let mut kw521=Vec::new();fun522.call(args520,kw521)?}};e.set("graph",assigned519.clone())?;
let assigned523={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun526=e.get("_enclosure_structure")?.attr("numbers")?;let mut args524=Vec::new();let mut kw525=Vec::new();args524.push(e.get("box")?.attr("outer")?);fun526.call(args524,kw525)?}};e.set("structure_numbers",assigned523.clone())?;
let assigned527={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun530=e.get("graph")?.attr("add")?;let mut args528=Vec::new();let mut kw529=Vec::new();args528.push(Val::Str("silhouette".into()));kw529.push(("bounds".into(),e.get("box")?.attr("outer")?));fun530.call(args528,kw529)?}};e.set("structure",assigned527.clone())?;
let context531={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun534=e.get("_record")?;let mut args532=Vec::new();let mut kw533=Vec::new();args532.push(e.get("shell")?);args532.push(e.get("graph")?);args532.push(e.get("structure")?);fun534.call(args532,kw533)?}};context531.attr("__enter__")?.call(vec![],vec![])?;let context_result606=(||->Result<Flow>{let assigned535=e.get("box")?.attr("splits")?.get(Val::Int(1i64))?;e.set("top",assigned535.clone())?;
if {let v536=e.get("structure_numbers")?.get(Val::Str("profile".into()))?.get(Val::Str("foot".into()))?.get(Val::Int(1i64))?;let v537=e.get("top")?;Val::Bool(compare("le",v536.clone(),v537.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun540=e.get("ValueError")?;let mut args538=Vec::new();let mut kw539=Vec::new();args538.push(Val::Str("the display keepout reaches the structural back-bottom boundary".into()));fun540.call(args538,kw539)?}})?);
}
if {let v544={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun543=e.get("shell")?.attr("housing_back_y")?;let mut args541=Vec::new();let mut kw542=Vec::new();args541.push(e.get("box")?.attr("outer")?);fun543.call(args541,kw542)?}};let v545=e.get("box")?.attr("y_joint")?;Val::Bool(compare("ge",v544.clone(),v545.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun548=e.get("ValueError")?;let mut args546=Vec::new();let mut kw547=Vec::new();args546.push(Val::Str("the display keepout reaches the back column".into()));fun548.call(args546,kw547)?}})?);
}
if e.get("box")?.attr("pack")?.attr("funnel")?.truthy()? {
let assigned549={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun552=e.get("shell")?.attr("funnel_seat_z")?;let mut args550=Vec::new();let mut kw551=Vec::new();args550.push(e.get("box")?.attr("outer")?);fun552.call(args550,kw551)?}};e.set("seat",assigned549.clone())?;
let assigned553=binary("sub",binary("sub",binary("sub",binary("sub",e.get("seat")?,e.get("shell")?.attr("_funnel")?.attr("drop")?)?,e.get("shell")?.attr("_funnel_frame_part")?.attr("web")?)?,e.get("shell")?.attr("funnel_collar_air")?)?,Val::Float(1.0f64))?;e.set("lower",assigned553.clone())?;
if {let v554=e.get("lower")?;let v555=e.get("top")?;Val::Bool(compare("le",v554.clone(),v555.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun558=e.get("ValueError")?;let mut args556=Vec::new();let mut kw557=Vec::new();args556.push(Val::Str("the funnel clearance reaches the structural back-bottom boundary".into()));fun558.call(args556,kw557)?}})?);
}
}
let assigned559=e.get("box")?.attr("outer")?;e.set("o",assigned559.clone())?;
let assigned560={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun563={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun566=e.get("structure")?.attr("cut")?;let mut args564=Vec::new();let mut kw565=Vec::new();args564.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun569=e.get("shell")?.attr("_cavity")?;let mut args567=Vec::new();let mut kw568=Vec::new();args567.push(e.get("box")?.attr("inner")?);fun569.call(args567,kw568)?}});fun566.call(args564,kw565)?}}.attr("intersect")?;let mut args561=Vec::new();let mut kw562=Vec::new();args561.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun572=e.get("graph")?.attr("box")?;let mut args570=Vec::new();let mut kw571=Vec::new();args570.push(e.get("o")?.get(Val::Int(0i64))?);args570.push(e.get("o")?.get(Val::Int(1i64))?);args570.push(e.get("box")?.attr("y_joint")?);args570.push(e.get("o")?.get(Val::Int(3i64))?);args570.push(e.get("o")?.get(Val::Int(4i64))?);args570.push(e.get("top")?);fun572.call(args570,kw571)?}});fun563.call(args561,kw562)?}};e.set("half",assigned560.clone())?;
let assigned573={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun576=e.get("half")?.attr("cut")?;let mut args574=Vec::new();let mut kw575=Vec::new();args574.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun579=e.get("shell")?.attr("_floor_tongue")?;let mut args577=Vec::new();let mut kw578=Vec::new();args577.push(e.get("box")?.attr("inner")?);args577.push(e.get("box")?.attr("y_joint")?);fun579.call(args577,kw578)?}}.get(Val::Int(1i64))?);fun576.call(args574,kw575)?}};e.set("half",assigned573.clone())?;
for item580 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(e.get("box")?.attr("pack")?.attr("back_ports")?);s.push(e.get("shell")?.attr("_port_cuts")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("box")?.attr("pack")?.attr("west_ports")?);s.push(e.get("shell")?.attr("_x_port_cuts")?);Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack581=unpack(item580,2)?;e.set("ports",unpack581[0].clone())?;e.set("cutter",unpack581[1].clone())?;let assigned582={let e=e.child();let out583=Val::list(vec![]);for item584 in e.get("ports")?.iter()? {e.set("p",item584)?;if {let v585=e.get("p")?.get(Val::Int(2i64))?;let v586=e.get("top")?;Val::Bool(compare("le",v585.clone(),v586.clone())?.truthy()?)}.truthy()? {out583.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out583};e.set("selected",assigned582.clone())?;
if {let v587=e.get("cutter")?;let v588=e.get("shell")?.attr("_port_cuts")?;Val::Bool(compare("is",v587.clone(),v588.clone())?.truthy()?)}.truthy()? {
let assigned589={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun592=e.get("cutter")?;let mut args590=Vec::new();let mut kw591=Vec::new();args590.push(e.get("selected")?);args590.push(binary("sub",e.get("box")?.attr("inner")?.get(Val::Int(3i64))?,Val::Float(5.0f64))?);args590.push(binary("add",e.get("o")?.get(Val::Int(3i64))?,Val::Float(5.0f64))?);fun592.call(args590,kw591)?}};e.set("cuts",assigned589.clone())?;
}else{
let assigned593={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun596=e.get("cutter")?;let mut args594=Vec::new();let mut kw595=Vec::new();args594.push(e.get("selected")?);args594.push(binary("sub",e.get("o")?.get(Val::Int(0i64))?,Val::Float(5.0f64))?);args594.push(binary("add",e.get("box")?.attr("inner")?.get(Val::Int(0i64))?,Val::Float(5.0f64))?);fun596.call(args594,kw595)?}};e.set("cuts",assigned593.clone())?;
}
for item597 in e.get("cuts")?.iter()? {
e.set("air",item597)?;let assigned598={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun601=e.get("half")?.attr("cut")?;let mut args599=Vec::new();let mut kw600=Vec::new();args599.push(e.get("air")?);fun601.call(args599,kw600)?}};e.set("half",assigned598.clone())?;
}
}
let assigned602={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun605=e.get("shell")?.attr("build_piece")?;let mut args603=Vec::new();let mut kw604=Vec::new();args603.push(e.get("box")?);args603.push(Val::Str("back".into()));args603.push(Val::Str("bottom".into()));kw604.push(("halves_cache".into(),{let d=Val::dict(vec![]);d.set(Val::Str("back".into()),e.get("half")?)?;d}));fun605.call(args603,kw604)?}};e.set("result",assigned602.clone())?;
Ok(Flow::Continue)})();context531.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result606? {Flow::Continue=>{},Flow::Return(value)=>return Ok(value)}
let mod607=rt.import_module("_materials")?;e.set("linear",rt.member("_materials","linear")?)?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun610=e.get("dict")?;let mut args608=Vec::new();let mut kw609=Vec::new();args608.push(e.get("structure_numbers")?);kw609.push(("color".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun613=e.get("linear")?;let mut args611=Vec::new();let mut kw612=Vec::new();args611.push(e.get("shell")?.attr("PIECE_COLORS")?.get(Val::Str("back-bottom".into()))?);fun613.call(args611,kw612)?}}));kw609.push(("panel".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",line!());{let fun616=e.get("graph")?.attr("document")?;let mut args614=Vec::new();let mut kw615=Vec::new();args614.push(e.get("result")?);fun616.call(args614,kw615)?}}));fun610.call(args608,kw609)?}});
Ok(Val::None)})})?;
// print_numbers
e.set("print_numbers",{let params=vec![("shell".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("_enclosure_skin",rt.import_module("_enclosure_skin")?)?;
let assigned1={let fun4=e.get("shell")?.attr("_above_core_shell")?.attr("rear_identification")?;let mut args2=Vec::new();let mut kw3=Vec::new();fun4.call(args2,kw3)?};e.set("identification",assigned1.clone())?;
let assigned5={let fun8=e.get("identification")?.attr("nameplate_station")?;let mut args6=Vec::new();let mut kw7=Vec::new();fun8.call(args6,kw7)?};e.set("station",assigned5.clone())?;
let assigned9=e.get("identification")?.attr("nameplate")?.attr("wing_interface")?;e.set("wing",assigned9.clone())?;
let assigned10={let fun13=e.get("identification")?.attr("nameplate_plan")?;let mut args11=Vec::new();let mut kw12=Vec::new();fun13.call(args11,kw12)?};e.set("plan",assigned10.clone())?;
let assigned14={let fun17=e.get("max")?;let mut args15=Vec::new();let mut kw16=Vec::new();args15.push(Val::Float(2.0f64));args15.push(binary("add",e.get("wing")?.attr("FLOOR_STOCK")?,e.get("wing")?.attr("RUNOUT_LEAD")?)?);fun17.call(args15,kw16)?};e.set("runout",assigned14.clone())?;
let assigned18=binary("add",e.get("shell")?.attr("wall")?,e.get("shell")?.attr("fits")?.attr("supported_surface")?)?;e.set("end_margin",assigned18.clone())?;
let assigned19=binary("sub",binary("sub",binary("sub",e.get("station")?.attr("z")?,binary("truediv",e.get("wing")?.attr("HEIGHT")?,Val::Int(2i64))?)?,e.get("wing")?.attr("FACE_SLIP")?)?,{let fun22=e.get("max")?;let mut args20=Vec::new();let mut kw21=Vec::new();args20.push(e.get("runout")?);args20.push(e.get("end_margin")?);fun22.call(args20,kw21)?})?;e.set("pad_floor",assigned19.clone())?;
let assigned23={let mut s=Vec::new();s.extend({let fun26=e.get("identification")?.attr("rail_bounds")?;let mut args24=Vec::new();let mut kw25=Vec::new();fun26.call(args24,kw25)?}.iter()?);s.extend({let fun29=e.get("wing")?.attr("plain_lips")?;let mut args27=Vec::new();let mut kw28=Vec::new();args27.push(e.get("station")?);args27.push(e.get("plan")?.get(Val::Str("face_y_mm".into()))?);fun29.call(args27,kw28)?}.iter()?);s.push({let fun32=e.get("shell")?.attr("_above_core_shell")?.attr("keystone_land")?;let mut args30=Vec::new();let mut kw31=Vec::new();fun32.call(args30,kw31)?});Val::list(s)};e.set("other",assigned23.clone())?;
if e.get("box")?.attr("pack")?.attr("nameplate")?.truthy()? {
{let fun35=e.get("other")?.attr("extend")?;let mut args33=Vec::new();let mut kw34=Vec::new();args33.push({let fun38=e.get("shell")?.attr("_nameplate_fit")?.attr("plain_lips")?;let mut args36=Vec::new();let mut kw37=Vec::new();args36.push(e.get("box")?.attr("pack")?.attr("nameplate")?);args36.push(e.get("box")?.attr("outer")?.get(Val::Int(3i64))?);fun38.call(args36,kw37)?});fun35.call(args33,kw34)?};
}
if e.get("box")?.attr("pack")?.attr("keystone")?.truthy()? {
{let fun41=e.get("other")?.attr("extend")?;let mut args39=Vec::new();let mut kw40=Vec::new();args39.push({let fun44=e.get("shell")?.attr("_data_fit")?.attr("plain_lips")?;let mut args42=Vec::new();let mut kw43=Vec::new();args42.push(e.get("box")?.attr("pack")?.attr("keystone")?);args42.push(e.get("box")?.attr("outer")?.get(Val::Int(3i64))?);fun44.call(args42,kw43)?});fun41.call(args39,kw40)?};
}
let assigned45={let fun48=e.get("shell")?.attr("_z_rail_runs")?;let mut args46=Vec::new();let mut kw47=Vec::new();args46.push(e.get("box")?.attr("inner")?);args46.push(e.get("box")?.attr("y_joint")?);args46.push(Val::Str("back".into()));args46.push(e.get("box")?.attr("pack")?.attr("collet_plate")?);fun48.call(args46,kw47)?};e.set("runs",assigned45.clone())?;
let assigned49={let fun52=e.get("max")?;let mut args50=Vec::new();let mut kw51=Vec::new();args50.push({let e=e.child();let out53=Val::list(vec![]);for item54 in e.get("runs")?.iter()? {e.set("run",item54)?;out53.attr("append")?.call(vec![{let fun57=e.get("max")?;let mut args55=Vec::new();let mut kw56=Vec::new();args55.push(e.get("run")?.get(Val::Int(2i64))?);args55.push(e.get("run")?.get(Val::Int(3i64))?);fun57.call(args55,kw56)?}],vec![])?;}out53});fun52.call(args50,kw51)?};e.set("rail_end_y",assigned49.clone())?;
let assigned58=binary("sub",binary("sub",binary("sub",e.get("plan")?.get(Val::Str("face_y_mm".into()))?,e.get("wing")?.attr("THICK")?)?,e.get("wing")?.attr("BACK_AIR")?)?,e.get("wing")?.attr("FLOOR_STOCK")?)?;e.set("pad_y",assigned58.clone())?;
let assigned59={let v65={let fun62=e.get("min")?;let mut args60=Vec::new();let mut kw61=Vec::new();args60.push(e.get("pad_y")?);args60.extend({let e=e.child();let out63=Val::list(vec![]);for item64 in e.get("other")?.iter()? {e.set("land",item64)?;out63.attr("append")?.call(vec![e.get("land")?.get(Val::Int(2i64))?],vec![])?;}out63}.iter()?);fun62.call(args60,kw61)?};let v66=e.get("rail_end_y")?;Val::Bool(compare("gt",v65.clone(),v66.clone())?.truthy()?)};e.set("behind_rails",assigned59.clone())?;
let assigned67={let fun70=e.get("max")?;let mut args68=Vec::new();let mut kw69=Vec::new();args68.push(binary("add",e.get("box")?.attr("splits")?.get(Val::Int(1i64))?,if e.get("behind_rails")?.truthy()? {Val::Int(0i64)} else {e.get("shell")?.attr("z_rise")?})?);args68.push({let fun73=e.get("shell")?.attr("_handhold_levels")?;let mut args71=Vec::new();let mut kw72=Vec::new();args71.push(e.get("box")?.attr("inner")?);fun73.call(args71,kw72)?}.get(Val::Int(2i64))?);fun70.call(args68,kw69)?};e.set("panel_top",assigned67.clone())?;
if {let v79={let fun76=e.get("min")?;let mut args74=Vec::new();let mut kw75=Vec::new();args74.push(e.get("pad_floor")?);args74.extend({let e=e.child();let out77=Val::list(vec![]);for item78 in e.get("other")?.iter()? {e.set("land",item78)?;out77.attr("append")?.call(vec![e.get("land")?.get(Val::Int(4i64))?],vec![])?;}out77}.iter()?);fun76.call(args74,kw75)?};let v80=e.get("panel_top")?;Val::Bool(compare("le",v79.clone(),v80.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let fun83=e.get("ValueError")?;let mut args81=Vec::new();let mut kw82=Vec::new();args81.push(Val::Str("a rear plain land reaches the back-bottom print boundary".into()));fun83.call(args81,kw82)?})?);
}
let assigned84={let fun87=e.get("shell")?.attr("_flute_skin")?.attr("Rail")?;let mut args85=Vec::new();let mut kw86=Vec::new();kw86.push(("at".into(),{let params=vec![("s".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let fun90=e.get("shell")?.attr("plan_at")?;let mut args88=Vec::new();let mut kw89=Vec::new();args88.push(e.get("s")?);args88.push(e.get("box")?.attr("outer")?);fun90.call(args88,kw89)?});
Ok(Val::None)})}));kw86.push(("length".into(),{let fun93=e.get("shell")?.attr("plan_perimeter")?;let mut args91=Vec::new();let mut kw92=Vec::new();args91.push(e.get("box")?.attr("outer")?);fun93.call(args91,kw92)?}));fun87.call(args85,kw86)?};e.set("rail",assigned84.clone())?;
let assigned94={let fun97=e.get("numbers")?;let mut args95=Vec::new();let mut kw96=Vec::new();args95.push(e.get("shell")?);args95.push(e.get("box")?);fun97.call(args95,kw96)?};e.set("out",assigned94.clone())?;
{let fun100=e.get("out")?.attr("update")?;let mut args98=Vec::new();let mut kw99=Vec::new();args98.push({let fun103=e.get("_enclosure_skin")?.attr("field_numbers")?;let mut args101=Vec::new();let mut kw102=Vec::new();args101.push({let mut s=Vec::new();s.push(e.get("rail")?);Val::list(s)});args101.push({let fun106=e.get("shell")?.attr("flute_pitch")?;let mut args104=Vec::new();let mut kw105=Vec::new();args104.push(e.get("box")?.attr("outer")?);fun106.call(args104,kw105)?});args101.push(e.get("shell")?.attr("flute_depth")?);args101.push(e.get("shell")?.attr("flute_rise")?);fun103.call(args101,kw102)?});fun100.call(args98,kw99)?};
let assigned107={let d=Val::dict(vec![]);d.set(Val::Str("warning_margin".into()),e.get("shell")?.attr("disposal_margin")?)?;d.set(Val::Str("warning_raise".into()),e.get("shell")?.attr("disposal_raise")?)?;d.set(Val::Str("wall".into()),e.get("shell")?.attr("wall")?)?;d};e.get("out")?.set(Val::Str("print".into()),assigned107.clone())?;
let assigned108={let d=Val::dict(vec![]);d.set(Val::Str("panel_top".into()),e.get("panel_top")?)?;d.set(Val::Str("receiver_pad_floor".into()),e.get("pad_floor")?)?;d.set(Val::Str("other_bounds".into()),e.get("other")?)?;d};e.get("out")?.set(Val::Str("disjoint_lands".into()),assigned108.clone())?;
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
            let mod703 = rt.import_module("_enclosure_presentation")?;
            e.set(
                "print_payload",
                rt.member("_enclosure_presentation", "print_payload")?,
            )?;
            let assigned704 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun707 = e.get("_rust_part")?.attr("cut")?;
                    let mut args705 = Vec::new();
                    let mut kw706 = Vec::new();
                    args705.push(Val::Str("enclosure-shell".into()));
                    args705.push(Val::Str("enclosure-panel".into()));
                    args705.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                            line!(),
                        );
                        {
                            let fun710 = e.get("print_numbers")?;
                            let mut args708 = Vec::new();
                            let mut kw709 = Vec::new();
                            args708.push(e.get("shell")?);
                            args708.push(e.get("box")?);
                            fun710.call(args708, kw709)?
                        }
                    });
                    args705.push(e.get("directory")?);
                    fun707.call(args705, kw706)?
                }
            };
            e.set("said", assigned704.clone())?;
            let assigned711 = binary(
                "truediv",
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                        line!(),
                    );
                    {
                        let fun714 = e.get("Path")?;
                        let mut args712 = Vec::new();
                        let mut kw713 = Vec::new();
                        args712.push(e.get("directory")?);
                        fun714.call(args712, kw713)?
                    }
                },
                Val::Str("enclosure-back-bottom.step".into()),
            )?;
            e.set("step", assigned711.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_panel.rs",
                    line!(),
                );
                {
                    let fun717 = e.get("print_payload")?;
                    let mut args715 = Vec::new();
                    let mut kw716 = Vec::new();
                    args715.push(e.get("step")?);
                    kw716.push(("check_print".into(), Val::Bool(true)));
                    fun717.call(args715, kw716)?
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
