//! Enclosure fit/readings on fine model references, without Python CAD objects.
//!
//! The enclosure's scalar station functions supply numeric tool recipes. Rust owns
//! their geometry and all model, volume, face and connected-component readings. The
//! existing report functions consume those readings, keeping their labels, units,
//! limits and document variables in one place with the mechanical dimensions.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("contextlib")?;
    e.set("ExitStack", rt.member("contextlib", "ExitStack")?)?;
    e.set("contextmanager", rt.member("contextlib", "contextmanager")?)?;
    e.set(
        "redirect_stdout",
        rt.member("contextlib", "redirect_stdout")?,
    )?;
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("io", rt.import_module("io")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let mod3 = rt.import_module("types")?;
    e.set("SimpleNamespace", rt.member("types", "SimpleNamespace")?)?;
    let mod4 = rt.import_module("_enclosure_panel")?;
    e.set("_Graph", rt.member("_enclosure_panel", "_Graph")?)?;
    e.set("_Shape", rt.member("_enclosure_panel", "_Shape")?)?;
    e.set("_record", rt.member("_enclosure_panel", "_record")?)?;
    e.set("_Vector.__init__", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, Some("coordinates"), None)?;
            let _frame = rt.frame(&outer);
            let assigned5 = if {
                let v9 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                        line!(),
                    );
                    {
                        let fun8 = e.get("len")?;
                        let mut args6 = Vec::new();
                        let mut kw7 = Vec::new();
                        args6.push(e.get("coordinates")?);
                        fun8.call(args6, kw7)?
                    }
                };
                let v10 = Val::Int(1i64);
                Val::Bool(compare("eq", v9.clone(), v10.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                        line!(),
                    );
                    {
                        let fun13 = e.get("tuple")?;
                        let mut args11 = Vec::new();
                        let mut kw12 = Vec::new();
                        args11.push(e.get("coordinates")?.get(Val::Int(0i64))?);
                        fun13.call(args11, kw12)?
                    }
                }
            } else {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                        line!(),
                    );
                    {
                        let fun16 = e.get("tuple")?;
                        let mut args14 = Vec::new();
                        let mut kw15 = Vec::new();
                        args14.push(e.get("coordinates")?);
                        fun16.call(args14, kw15)?
                    }
                }
            };
            e.get("self")?.setattr("xyz", assigned5.clone())?;
            let assigned17 = e.get("self")?.attr("xyz")?;
            let unpack18 = unpack(assigned17.clone(), 3)?;
            e.get("self")?.setattr("x", unpack18[0].clone())?;
            e.get("self")?.setattr("y", unpack18[1].clone())?;
            e.get("self")?.setattr("z", unpack18[2].clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("_Vector.__iter__", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("self")?.attr("xyz")?);
            Ok(Val::None)
        })
    })?;
    e.set("_Vector.__getitem__", {
        let params = vec![("self".into(), None, false), ("index".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("self")?.attr("xyz")?.get(e.get("index")?)?);
            Ok(Val::None)
        })
    })?;
    e.set("_Vector.__add__",{let params=vec![("self".into(),None,false),("other".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun21=e.get("_Vector")?;let mut args19=Vec::new();let mut kw20=Vec::new();args19.extend({let e=e.child();let out22=Val::list(vec![]);for item23 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun26=e.get("zip")?;let mut args24=Vec::new();let mut kw25=Vec::new();args24.push(e.get("self")?);args24.push(e.get("other")?);fun26.call(args24,kw25)?}}.iter()? {let unpack27=unpack(item23,2)?;e.set("a",unpack27[0].clone())?;e.set("b",unpack27[1].clone())?;out22.attr("append")?.call(vec![binary("add",e.get("a")?,e.get("b")?)?],vec![])?;}out22}.iter()?);fun21.call(args19,kw20)?}});
Ok(Val::None)})})?;
    e.set("_Vector.__sub__",{let params=vec![("self".into(),None,false),("other".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun30=e.get("_Vector")?;let mut args28=Vec::new();let mut kw29=Vec::new();args28.extend({let e=e.child();let out31=Val::list(vec![]);for item32 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun35=e.get("zip")?;let mut args33=Vec::new();let mut kw34=Vec::new();args33.push(e.get("self")?);args33.push(e.get("other")?);fun35.call(args33,kw34)?}}.iter()? {let unpack36=unpack(item32,2)?;e.set("a",unpack36[0].clone())?;e.set("b",unpack36[1].clone())?;out31.attr("append")?.call(vec![binary("sub",e.get("a")?,e.get("b")?)?],vec![])?;}out31}.iter()?);fun30.call(args28,kw29)?}});
Ok(Val::None)})})?;
    e.set("_Vector.dot", {
        let params = vec![("self".into(), None, false), ("other".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun39 = e.get("sum")?;
                    let mut args37 = Vec::new();
                    let mut kw38 = Vec::new();
                    args37.push({
                        let e = e.child();
                        let out40 = Val::list(vec![]);
                        for item41 in {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                                line!(),
                            );
                            {
                                let fun44 = e.get("zip")?;
                                let mut args42 = Vec::new();
                                let mut kw43 = Vec::new();
                                args42.push(e.get("self")?);
                                args42.push(e.get("other")?);
                                fun44.call(args42, kw43)?
                            }
                        }
                        .iter()?
                        {
                            let unpack45 = unpack(item41, 2)?;
                            e.set("a", unpack45[0].clone())?;
                            e.set("b", unpack45[1].clone())?;
                            out40
                                .attr("append")?
                                .call(vec![binary("mul", e.get("a")?, e.get("b")?)?], vec![])?;
                        }
                        out40
                    });
                    fun39.call(args37, kw38)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Vector.Length", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun48 = e.get("math")?.attr("sqrt")?;
                    let mut args46 = Vec::new();
                    let mut kw47 = Vec::new();
                    args46.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun51 = e.get("self")?.attr("dot")?;
                            let mut args49 = Vec::new();
                            let mut kw50 = Vec::new();
                            args49.push(e.get("self")?);
                            fun51.call(args49, kw50)?
                        }
                    });
                    fun48.call(args46, kw47)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set(
        "_Vector",
        rt.python_type("_rust_enclosure_checks", "_Vector")?,
    )?;
    // _bounds
    e.set("_bounds",{let params=vec![("lower".into(),None,false),("upper".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned52={let mut s=Vec::new();s.push({let v53=e.get("lower")?;if v53.truthy()? {v53} else {{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)}}});s.push({let v54=e.get("upper")?;if v54.truthy()? {v54} else {{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)}}});Val::tuple(s)};let unpack55=unpack(assigned52.clone(),2)?;e.set("lower",unpack55[0].clone())?;e.set("upper",unpack55[1].clone())?;
let assigned56={let e=e.child();let out57=Val::dict(vec![]);for item58 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun61=e.get("enumerate")?;let mut args59=Vec::new();let mut kw60=Vec::new();args59.push(Val::Str("xyz".into()));fun61.call(args59,kw60)?}}.iter()? {let unpack62=unpack(item58,2)?;e.set("k",unpack62[0].clone())?;e.set("axis",unpack62[1].clone())?;for item63 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("min".into()));s.push(e.get("lower")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("max".into()));s.push(e.get("upper")?);Val::tuple(s)});Val::tuple(s)}.iter()? {let unpack64=unpack(item63,2)?;e.set("suffix",unpack64[0].clone())?;e.set("values",unpack64[1].clone())?;out57.set(binary("add",e.get("axis")?,e.get("suffix")?)?,e.get("values")?.get(e.get("k")?)?)?;}}out57};e.set("row",assigned56.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun67=e.get("row")?.attr("update")?;let mut args65=Vec::new();let mut kw66=Vec::new();args65.push({let e=e.child();let out68=Val::dict(vec![]);for item69 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun72=e.get("enumerate")?;let mut args70=Vec::new();let mut kw71=Vec::new();args70.push(Val::Str("xyz".into()));fun72.call(args70,kw71)?}}.iter()? {let unpack73=unpack(item69,2)?;e.set("k",unpack73[0].clone())?;e.set("axis",unpack73[1].clone())?;out68.set(binary("add",e.get("axis")?,Val::Str("len".into()))?,binary("sub",e.get("upper")?.get(e.get("k")?)?,e.get("lower")?.get(e.get("k")?)?)?)?;}out68});fun67.call(args65,kw66)?}};
let assigned74={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun77=e.get("_Vector")?;let mut args75=Vec::new();let mut kw76=Vec::new();args75.extend({let e=e.child();let out78=Val::list(vec![]);for item79 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun82=e.get("zip")?;let mut args80=Vec::new();let mut kw81=Vec::new();args80.push(e.get("lower")?);args80.push(e.get("upper")?);fun82.call(args80,kw81)?}}.iter()? {let unpack83=unpack(item79,2)?;e.set("a",unpack83[0].clone())?;e.set("b",unpack83[1].clone())?;out78.attr("append")?.call(vec![binary("truediv",binary("add",e.get("a")?,e.get("b")?)?,Val::Int(2i64))?],vec![])?;}out78}.iter()?);fun77.call(args75,kw76)?}};e.get("row")?.set(Val::Str("center".into()),assigned74.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun86=e.get("SimpleNamespace")?;let mut args84=Vec::new();let mut kw85=Vec::new();kw85.extend(keyword_items(e.get("row")?)?);fun86.call(args84,kw85)?}});
Ok(Val::None)})})?;
    e.set("_ScalarFace.__init__", {
        let params = vec![("self".into(), None, false), ("row".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned87 = e.get("row")?;
            e.get("self")?.setattr("row", assigned87.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("_ScalarFace.Area", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("self")?.attr("row")?.get(Val::Str("area".into()))?);
            Ok(Val::None)
        })
    })?;
    e.set("_ScalarFace.Center", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun90 = e.get("_Vector")?;
                    let mut args88 = Vec::new();
                    let mut kw89 = Vec::new();
                    args88.extend(
                        e.get("self")?
                            .attr("row")?
                            .get(Val::Str("centre".into()))?
                            .iter()?,
                    );
                    fun90.call(args88, kw89)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_ScalarFace.normalAt", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun93 = e.get("_Vector")?;
                    let mut args91 = Vec::new();
                    let mut kw92 = Vec::new();
                    args91.extend(
                        e.get("self")?
                            .attr("row")?
                            .get(Val::Str("normal".into()))?
                            .iter()?,
                    );
                    fun93.call(args91, kw92)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_ScalarFace.BoundingBox", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun96 = e.get("_bounds")?;
                    let mut args94 = Vec::new();
                    let mut kw95 = Vec::new();
                    args94.push(e.get("self")?.attr("row")?.get(Val::Str("min".into()))?);
                    args94.push(e.get("self")?.attr("row")?.get(Val::Str("max".into()))?);
                    fun96.call(args94, kw95)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_ScalarFace.geomType", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("self")?.attr("row")?.get(Val::Str("kind".into()))?);
            Ok(Val::None)
        })
    })?;
    e.set(
        "_ScalarFace",
        rt.python_type("_rust_enclosure_checks", "_ScalarFace")?,
    )?;
    e.set("_ScalarComponent.__init__", {
        let params = vec![("self".into(), None, false), ("row".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned97 = e.get("row")?;
            e.get("self")?.setattr("row", assigned97.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("_ScalarComponent.BoundingBox", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun100 = e.get("_bounds")?;
                    let mut args98 = Vec::new();
                    let mut kw99 = Vec::new();
                    args98.push(e.get("self")?.attr("row")?.get(Val::Str("min".into()))?);
                    args98.push(e.get("self")?.attr("row")?.get(Val::Str("max".into()))?);
                    fun100.call(args98, kw99)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_ScalarComponent.Volume", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e
                .get("self")?
                .attr("row")?
                .get(Val::Str("volume_mm3".into()))?);
            Ok(Val::None)
        })
    })?;
    e.set(
        "_ScalarComponent",
        rt.python_type("_rust_enclosure_checks", "_ScalarComponent")?,
    )?;
    e.set("_ReadingShape.translate", {
        let params = vec![("self".into(), None, false), ("delta".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun103 = builtin_call(
                        "super",
                        vec![
                            rt.python_type("_rust_enclosure_checks", "_ReadingShape")?,
                            e.get("self")?,
                        ],
                        vec![],
                    )?
                    .attr("translate")?;
                    let mut args101 = Vec::new();
                    let mut kw102 = Vec::new();
                    args101.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun106 = e.get("tuple")?;
                            let mut args104 = Vec::new();
                            let mut kw105 = Vec::new();
                            args104.push(e.get("delta")?);
                            fun106.call(args104, kw105)?
                        }
                    });
                    fun103.call(args101, kw102)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_ReadingShape.Volume", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun109 = e.get("self")?.attr("graph")?.attr("reading")?;
                    let mut args107 = Vec::new();
                    let mut kw108 = Vec::new();
                    args107.push(e.get("self")?);
                    fun109.call(args107, kw108)?
                }
            }
            .get(Val::Str("volume_mm3".into()))?);
            Ok(Val::None)
        })
    })?;
    e.set("_ReadingShape.BoundingBox", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v112 = {
                    let v116 = e.get("self")?;
                    let v117 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun115 =
                                e.get("self")?.attr("graph")?.attr("extras")?.attr("get")?;
                            let mut args113 = Vec::new();
                            let mut kw114 = Vec::new();
                            args113.push(Val::Str("receiver_field".into()));
                            fun115.call(args113, kw114)?
                        }
                    };
                    Val::Bool(compare("is", v116.clone(), v117.clone())?.truthy()?)
                };
                if v112.truthy()? {
                    {
                        let v110 = e.get("self")?.attr("bounds")?;
                        let v111 = Val::None;
                        Val::Bool(compare("is_not", v110.clone(), v111.clone())?.truthy()?)
                    }
                } else {
                    v112
                }
            }
            .truthy()?
            {
                return Ok({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                        line!(),
                    );
                    {
                        let fun120 = e.get("_bounds")?;
                        let mut args118 = Vec::new();
                        let mut kw119 = Vec::new();
                        args118.push(e.get("self")?.attr("bounds")?.get(Val::Slice {
                            start: None,
                            stop: None,
                            step: Val::Int(2i64).integer()?,
                        })?);
                        args118.push(e.get("self")?.attr("bounds")?.get(Val::Slice {
                            start: Some(Val::Int(1i64).integer()?),
                            stop: None,
                            step: Val::Int(2i64).integer()?,
                        })?);
                        fun120.call(args118, kw119)?
                    }
                });
            }
            let assigned121 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun124 = e.get("self")?.attr("graph")?.attr("reading")?;
                    let mut args122 = Vec::new();
                    let mut kw123 = Vec::new();
                    args122.push(e.get("self")?);
                    fun124.call(args122, kw123)?
                }
            };
            e.set("row", assigned121.clone())?;
            if {
                let v127 = {
                    let v128 = e.get("self")?.attr("graph")?.attr("answers")?;
                    let v129 = Val::None;
                    Val::Bool(compare("is", v128.clone(), v129.clone())?.truthy()?)
                };
                if v127.truthy()? {
                    {
                        let v125 = e.get("self")?.attr("bounds")?;
                        let v126 = Val::None;
                        Val::Bool(compare("is_not", v125.clone(), v126.clone())?.truthy()?)
                    }
                } else {
                    v127
                }
            }
            .truthy()?
            {
                return Ok({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                        line!(),
                    );
                    {
                        let fun132 = e.get("_bounds")?;
                        let mut args130 = Vec::new();
                        let mut kw131 = Vec::new();
                        args130.push(e.get("self")?.attr("bounds")?.get(Val::Slice {
                            start: None,
                            stop: None,
                            step: Val::Int(2i64).integer()?,
                        })?);
                        args130.push(e.get("self")?.attr("bounds")?.get(Val::Slice {
                            start: Some(Val::Int(1i64).integer()?),
                            stop: None,
                            step: Val::Int(2i64).integer()?,
                        })?);
                        fun132.call(args130, kw131)?
                    }
                });
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun135 = e.get("_bounds")?;
                    let mut args133 = Vec::new();
                    let mut kw134 = Vec::new();
                    args133.push(e.get("row")?.get(Val::Str("min".into()))?);
                    args133.push(e.get("row")?.get(Val::Str("max".into()))?);
                    fun135.call(args133, kw134)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_ReadingShape.Solids", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned136 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun139 = e.get("self")?.attr("graph")?.attr("reading")?;
                    let mut args137 = Vec::new();
                    let mut kw138 = Vec::new();
                    args137.push(e.get("self")?);
                    kw138.push(("components".into(), Val::Bool(true)));
                    kw138.push(("valid".into(), Val::Bool(true)));
                    fun139.call(args137, kw138)?
                }
            };
            e.set("row", assigned136.clone())?;
            return Ok({
                let e = e.child();
                let out140 = Val::list(vec![]);
                for item141 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                        line!(),
                    );
                    {
                        let fun144 = e.get("row")?.attr("get")?;
                        let mut args142 = Vec::new();
                        let mut kw143 = Vec::new();
                        args142.push(Val::Str("components".into()));
                        args142.push({
                            let mut s = Vec::new();
                            Val::tuple(s)
                        });
                        fun144.call(args142, kw143)?
                    }
                }
                .iter()?
                {
                    e.set("part", item141)?;
                    out140.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                                line!(),
                            );
                            {
                                let fun147 = e.get("_ScalarComponent")?;
                                let mut args145 = Vec::new();
                                let mut kw146 = Vec::new();
                                args145.push(e.get("part")?);
                                fun147.call(args145, kw146)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out140
            });
            Ok(Val::None)
        })
    })?;
    e.set("_ReadingShape.isValid", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun150 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun153 = e.get("self")?.attr("graph")?.attr("reading")?;
                            let mut args151 = Vec::new();
                            let mut kw152 = Vec::new();
                            args151.push(e.get("self")?);
                            kw152.push(("valid".into(), Val::Bool(true)));
                            fun153.call(args151, kw152)?
                        }
                    }
                    .attr("get")?;
                    let mut args148 = Vec::new();
                    let mut kw149 = Vec::new();
                    args148.push(Val::Str("valid".into()));
                    args148.push(Val::Bool(true));
                    fun150.call(args148, kw149)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_ReadingShape.Faces", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned154 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun157 = e.get("self")?.attr("graph")?.attr("reading")?;
                    let mut args155 = Vec::new();
                    let mut kw156 = Vec::new();
                    args155.push(e.get("self")?);
                    kw156.push(("kind".into(), Val::Str("faces".into())));
                    fun157.call(args155, kw156)?
                }
            };
            e.set("rows", assigned154.clone())?;
            return Ok({
                let e = e.child();
                let out158 = Val::list(vec![]);
                for item159 in e.get("rows")?.iter()? {
                    e.set("row", item159)?;
                    out158.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                                line!(),
                            );
                            {
                                let fun162 = e.get("_ScalarFace")?;
                                let mut args160 = Vec::new();
                                let mut kw161 = Vec::new();
                                args160.push(e.get("row")?);
                                fun162.call(args160, kw161)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out158
            });
            Ok(Val::None)
        })
    })?;
    e.set(
        "_ReadingShape",
        rt.python_type("_rust_enclosure_checks", "_ReadingShape")?,
    )?;
    e.set("_Questions.__init__", {
        let params = vec![
            ("self".into(), None, false),
            ("answers".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun165 = builtin_call(
                        "super",
                        vec![
                            rt.python_type("_rust_enclosure_checks", "_Questions")?,
                            e.get("self")?,
                        ],
                        vec![],
                    )?
                    .attr("__init__")?;
                    let mut args163 = Vec::new();
                    let mut kw164 = Vec::new();
                    fun165.call(args163, kw164)?
                }
            };
            let assigned166 = e.get("answers")?;
            e.get("self")?.setattr("answers", assigned166.clone())?;
            let assigned167 = {
                let d = Val::dict(vec![]);
                d
            };
            e.get("self")?.setattr("queries", assigned167.clone())?;
            let assigned168 = {
                let d = Val::dict(vec![]);
                d
            };
            e.get("self")?.setattr("extras", assigned168.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("_Questions.add", {
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
            if {
                let v169 = e.get("op")?;
                let v170 = Val::Str("empty".into());
                Val::Bool(compare("eq", v169.clone(), v170.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned171 = binary(
                    "mul",
                    {
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    },
                    Val::Int(6i64),
                )?;
                e.set("bounds", assigned171.clone())?;
            }
            let assigned172 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun175 = builtin_call(
                        "super",
                        vec![
                            rt.python_type("_rust_enclosure_checks", "_Questions")?,
                            e.get("self")?,
                        ],
                        vec![],
                    )?
                    .attr("add")?;
                    let mut args173 = Vec::new();
                    let mut kw174 = Vec::new();
                    args173.push(e.get("op")?);
                    args173.push(e.get("inputs")?);
                    kw174.push(("bounds".into(), e.get("bounds")?));
                    kw174.extend(keyword_items(e.get("numbers")?)?);
                    fun175.call(args173, kw174)?
                }
            };
            e.set("shape", assigned172.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun178 = e.get("_ReadingShape")?;
                    let mut args176 = Vec::new();
                    let mut kw177 = Vec::new();
                    args176.push(e.get("self")?);
                    args176.push(e.get("shape")?.attr("index")?);
                    args176.push(e.get("shape")?.attr("bounds")?);
                    fun178.call(args176, kw177)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_Questions.model",{let params=vec![("self".into(),None,false),("value".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun181=e.get("isinstance")?;let mut args179=Vec::new();let mut kw180=Vec::new();args179.push(e.get("value")?);args179.push({let mut s=Vec::new();s.push(e.get("list")?);s.push(e.get("tuple")?);Val::tuple(s)});fun181.call(args179,kw180)?}}.truthy()? {
let assigned182={let e=e.child();let out183=Val::list(vec![]);for item184 in e.get("value")?.iter()? {e.set("reference",item184)?;out183.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun187=e.get("self")?.attr("model")?;let mut args185=Vec::new();let mut kw186=Vec::new();args185.push(e.get("reference")?);fun187.call(args185,kw186)?}}],vec![])?;}out183};e.set("parts",assigned182.clone())?;
return Ok(if e.get("parts")?.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun190=e.get("parts")?.get(Val::Int(0i64))?.attr("fuse")?;let mut args188=Vec::new();let mut kw189=Vec::new();args188.extend(e.get("parts")?.get(Val::Slice{start:Some(Val::Int(1i64).integer()?),stop:None,step:1})?.iter()?);fun190.call(args188,kw189)?}}} else {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun193=e.get("self")?.attr("add")?;let mut args191=Vec::new();let mut kw192=Vec::new();args191.push(Val::Str("empty".into()));fun193.call(args191,kw192)?}}});
}
let assigned194=if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun197=e.get("isinstance")?;let mut args195=Vec::new();let mut kw196=Vec::new();args195.push(e.get("value")?);args195.push({let mut s=Vec::new();s.push(e.get("str")?);s.push(e.get("Path")?);Val::tuple(s)});fun197.call(args195,kw196)?}}.truthy()? {{let d=Val::dict(vec![]);d.set(Val::Str("model".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun200=e.get("str")?;let mut args198=Vec::new();let mut kw199=Vec::new();args198.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun203={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun206=e.get("Path")?;let mut args204=Vec::new();let mut kw205=Vec::new();args204.push(e.get("value")?);fun206.call(args204,kw205)?}}.attr("resolve")?;let mut args201=Vec::new();let mut kw202=Vec::new();fun203.call(args201,kw202)?}});fun200.call(args198,kw199)?}})?;d}} else {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun209=e.get("dict")?;let mut args207=Vec::new();let mut kw208=Vec::new();args207.push(e.get("value")?);fun209.call(args207,kw208)?}}};e.set("reference",assigned194.clone())?;
let assigned210={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun213=e.get("str")?;let mut args211=Vec::new();let mut kw212=Vec::new();args211.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun216={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun219=e.get("Path")?;let mut args217=Vec::new();let mut kw218=Vec::new();args217.push(e.get("reference")?.get(Val::Str("model".into()))?);fun219.call(args217,kw218)?}}.attr("resolve")?;let mut args214=Vec::new();let mut kw215=Vec::new();fun216.call(args214,kw215)?}});fun213.call(args211,kw212)?}};e.get("reference")?.set(Val::Str("model".into()),assigned210.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun222=e.get("self")?.attr("add")?;let mut args220=Vec::new();let mut kw221=Vec::new();args220.push(Val::Str("model".into()));kw221.push(("reference".into(),e.get("reference")?));fun222.call(args220,kw221)?}});
Ok(Val::None)})})?;
    e.set("_Questions.identity",{let params=vec![("self".into(),None,false),("index".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned223={let mut s=Vec::new();Val::list(s)};e.set("keys",assigned223.clone())?;
for item224 in e.get("self")?.attr("nodes")?.get(Val::Slice{start:None,stop:Some(binary("add",e.get("index")?,Val::Int(1i64))?.integer()?),step:1})?.iter()? {
e.set("node",item224)?;let assigned225={let e=e.child();let out226=Val::dict(vec![]);for item227 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun230=e.get("node")?.attr("items")?;let mut args228=Vec::new();let mut kw229=Vec::new();fun230.call(args228,kw229)?}}.iter()? {let unpack231=unpack(item227,2)?;e.set("key",unpack231[0].clone())?;e.set("value",unpack231[1].clone())?;if {let v232=e.get("key")?;let v233={let mut s=Vec::new();s.push(Val::Str("inputs".into()));s.push(Val::Str("source".into()));Val::tuple(s)};Val::Bool(compare("not_in",v232.clone(),v233.clone())?.truthy()?)}.truthy()? {out226.set(e.get("key")?,e.get("value")?)?;}}out226};e.set("row",assigned225.clone())?;
let assigned234={let e=e.child();let out235=Val::list(vec![]);for item236 in e.get("node")?.get(Val::Str("inputs".into()))?.iter()? {e.set("k",item236)?;out235.attr("append")?.call(vec![e.get("keys")?.get(e.get("k")?)?],vec![])?;}out235};e.get("row")?.set(Val::Str("inputs".into()),assigned234.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun239=e.get("keys")?.attr("append")?;let mut args237=Vec::new();let mut kw238=Vec::new();args237.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun242={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun245=e.get("hashlib")?.attr("sha256")?;let mut args243=Vec::new();let mut kw244=Vec::new();args243.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun248={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun251=e.get("json")?.attr("dumps")?;let mut args249=Vec::new();let mut kw250=Vec::new();args249.push(e.get("row")?);kw250.push(("sort_keys".into(),Val::Bool(true)));kw250.push(("separators".into(),{let mut s=Vec::new();s.push(Val::Str(",".into()));s.push(Val::Str(":".into()));Val::tuple(s)}));fun251.call(args249,kw250)?}}.attr("encode")?;let mut args246=Vec::new();let mut kw247=Vec::new();fun248.call(args246,kw247)?}});fun245.call(args243,kw244)?}}.attr("hexdigest")?;let mut args240=Vec::new();let mut kw241=Vec::new();fun242.call(args240,kw241)?}});fun239.call(args237,kw238)?}};
}
return Ok(e.get("keys")?.get(e.get("index")?)?);
Ok(Val::None)})})?;
    e.set("_Questions.reading", {
        let params = vec![
            ("self".into(), None, false),
            ("shape".into(), None, false),
            ("kind".into(), Some(Val::Str("stats".into())), true),
            ("components".into(), Some(Val::Bool(false)), true),
            ("valid".into(), Some(Val::Bool(false)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned252 = binary(
                "add",
                binary(
                    "add",
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun255 = e.get("self")?.attr("identity")?;
                            let mut args253 = Vec::new();
                            let mut kw254 = Vec::new();
                            args253.push(e.get("shape")?.attr("index")?);
                            fun255.call(args253, kw254)?
                        }
                    },
                    Val::Str(":".into()),
                )?,
                e.get("kind")?,
            )?;
            e.set("key", assigned252.clone())?;
            if {
                let v256 = e.get("self")?.attr("answers")?;
                let v257 = Val::None;
                Val::Bool(compare("is_not", v256.clone(), v257.clone())?.truthy()?)
            }
            .truthy()?
            {
                if {
                    let v258 = e.get("key")?;
                    let v259 = e.get("self")?.attr("answers")?;
                    Val::Bool(compare("not_in", v258.clone(), v259.clone())?.truthy()?)
                }
                .truthy()?
                {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                                line!(),
                            );
                            {
                                let fun262 = e.get("ValueError")?;
                                let mut args260 = Vec::new();
                                let mut kw261 = Vec::new();
                                args260.push(binary(
                                    "add",
                                    Val::Str(
                                        "an enclosure report asked an unmeasured question: ".into(),
                                    ),
                                    e.get("key")?,
                                )?);
                                fun262.call(args260, kw261)?
                            }
                        })?
                    );
                }
                let assigned263 = e.get("self")?.attr("answers")?.get(e.get("key")?)?;
                e.set("row", assigned263.clone())?;
                if {
                    let v266 = e.get("components")?;
                    if v266.truthy()? {
                        {
                            let v264 = Val::Str("components".into());
                            let v265 = e.get("row")?;
                            Val::Bool(compare("not_in", v264.clone(), v265.clone())?.truthy()?)
                        }
                    } else {
                        v266
                    }
                }
                .truthy()?
                {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                                line!(),
                            );
                            {
                                let fun269 = e.get("ValueError")?;
                                let mut args267 = Vec::new();
                                let mut kw268 = Vec::new();
                                args267.push(binary(
                                    "add",
                                    Val::Str(
                                        "an enclosure report asked unmeasured components: ".into(),
                                    ),
                                    e.get("key")?,
                                )?);
                                fun269.call(args267, kw268)?
                            }
                        })?
                    );
                }
                return Ok(e.get("row")?);
            }
            let assigned270 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun273 = e.get("self")?.attr("queries")?.attr("setdefault")?;
                    let mut args271 = Vec::new();
                    let mut kw272 = Vec::new();
                    args271.push(e.get("key")?);
                    args271.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun276 = e.get("dict")?;
                            let mut args274 = Vec::new();
                            let mut kw275 = Vec::new();
                            kw275.push(("key".into(), e.get("key")?));
                            kw275.push(("node".into(), e.get("shape")?.attr("index")?));
                            kw275.push(("kind".into(), e.get("kind")?));
                            fun276.call(args274, kw275)?
                        }
                    });
                    fun273.call(args271, kw272)?
                }
            };
            e.set("query", assigned270.clone())?;
            if e.get("components")?.truthy()? {
                let assigned277 = Val::Bool(true);
                e.get("query")?
                    .set(Val::Str("components".into()), assigned277.clone())?;
            }
            if e.get("valid")?.truthy()? {
                let assigned278 = Val::Bool(true);
                e.get("query")?
                    .set(Val::Str("valid".into()), assigned278.clone())?;
            }
            return Ok(
                if {
                    let v279 = e.get("kind")?;
                    let v280 = Val::Str("faces".into());
                    Val::Bool(compare("eq", v279.clone(), v280.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let mut s = Vec::new();
                        Val::list(s)
                    }
                } else {
                    {
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("volume_mm3".into()), Val::Float(0.0f64))?;
                        d.set(Val::Str("min".into()), Val::None)?;
                        d.set(Val::Str("max".into()), Val::None)?;
                        d.set(Val::Str("components".into()), {
                            let mut s = Vec::new();
                            Val::list(s)
                        })?;
                        d.set(Val::Str("valid".into()), Val::Bool(true))?;
                        d
                    }
                },
            );
            Ok(Val::None)
        })
    })?;
    e.set("_Questions.document",{let params=vec![("self".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned281={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun284=e.get("set")?;let mut args282=Vec::new();let mut kw283=Vec::new();fun284.call(args282,kw283)?}};e.set("needed",assigned281.clone())?;
// visit
e.set("visit",{let params=vec![("k".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let v285=e.get("k")?;let v286=e.get("needed")?;Val::Bool(compare("in",v285.clone(),v286.clone())?.truthy()?)}.truthy()? {
return Ok(Val::None);
}
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun289=e.get("needed")?.attr("add")?;let mut args287=Vec::new();let mut kw288=Vec::new();args287.push(e.get("k")?);fun289.call(args287,kw288)?}};
for item290 in e.get("self")?.attr("nodes")?.get(e.get("k")?)?.get(Val::Str("inputs".into()))?.iter()? {
e.set("child",item290)?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun293=e.get("visit")?;let mut args291=Vec::new();let mut kw292=Vec::new();args291.push(e.get("child")?);fun293.call(args291,kw292)?}};
}
Ok(Val::None)})})?;
for item294 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun297=e.get("self")?.attr("queries")?.attr("values")?;let mut args295=Vec::new();let mut kw296=Vec::new();fun297.call(args295,kw296)?}}.iter()? {
e.set("question",item294)?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun300=e.get("visit")?;let mut args298=Vec::new();let mut kw299=Vec::new();args298.push(e.get("question")?.get(Val::Str("node".into()))?);fun300.call(args298,kw299)?}};
}
let assigned301={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun304=e.get("sorted")?;let mut args302=Vec::new();let mut kw303=Vec::new();args302.push(e.get("needed")?);fun304.call(args302,kw303)?}};e.set("order",assigned301.clone())?;
let assigned305={let e=e.child();let out306=Val::dict(vec![]);for item307 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun310=e.get("enumerate")?;let mut args308=Vec::new();let mut kw309=Vec::new();args308.push(e.get("order")?);fun310.call(args308,kw309)?}}.iter()? {let unpack311=unpack(item307,2)?;e.set("new",unpack311[0].clone())?;e.set("old",unpack311[1].clone())?;out306.set(e.get("old")?,e.get("new")?)?;}out306};e.set("remap",assigned305.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun314=e.get("dict")?;let mut args312=Vec::new();let mut kw313=Vec::new();kw313.push(("nodes".into(),{let e=e.child();let out315=Val::list(vec![]);for item316 in e.get("order")?.iter()? {e.set("k",item316)?;out315.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun319=e.get("dict")?;let mut args317=Vec::new();let mut kw318=Vec::new();args317.push(e.get("self")?.attr("nodes")?.get(e.get("k")?)?);kw318.push(("inputs".into(),{let e=e.child();let out320=Val::list(vec![]);for item321 in e.get("self")?.attr("nodes")?.get(e.get("k")?)?.get(Val::Str("inputs".into()))?.iter()? {e.set("i",item321)?;out320.attr("append")?.call(vec![e.get("remap")?.get(e.get("i")?)?],vec![])?;}out320}));fun319.call(args317,kw318)?}}],vec![])?;}out315}));kw313.push(("queries".into(),{let e=e.child();let out322=Val::list(vec![]);for item323 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun326=e.get("self")?.attr("queries")?.attr("values")?;let mut args324=Vec::new();let mut kw325=Vec::new();fun326.call(args324,kw325)?}}.iter()? {e.set("row",item323)?;out322.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun329=e.get("dict")?;let mut args327=Vec::new();let mut kw328=Vec::new();args327.push(e.get("row")?);kw328.push(("node".into(),e.get("remap")?.get(e.get("row")?.get(Val::Str("node".into()))?)?));fun329.call(args327,kw328)?}}],vec![])?;}out322}));fun314.call(args312,kw313)?}});
Ok(Val::None)})})?;
    e.set(
        "_Questions",
        rt.python_type("_rust_enclosure_checks", "_Questions")?,
    )?;
    e.set("_numeric",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("box".into(),Some(Val::None),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;
            let enter_e=e.clone();let enter_rt=rt.clone();
            let enter=Val::function(move|_,_|{let e=enter_e.clone();let rt=enter_rt.clone();let _frame=rt.frame(&e);
        let assigned330=e.get("shell")?.attr("cq")?;e.set("original_cq",assigned330.clone())?;
let assigned331={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun334=e.get("SimpleNamespace")?;let mut args332=Vec::new();let mut kw333=Vec::new();kw333.push(("Vector".into(),e.get("_Vector")?));fun334.call(args332,kw333)?}};e.get("shell")?.setattr("cq",assigned331.clone())?;
e.set("context335",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun338=e.get("ExitStack")?;let mut args336=Vec::new();let mut kw337=Vec::new();fun338.call(args336,kw337)?}})?;e.set("stack",e.get("context335")?.attr("__enter__")?.call(vec![],vec![])?)?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun341=e.get("stack")?.attr("enter_context")?;let mut args339=Vec::new();let mut kw340=Vec::new();args339.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun344=e.get("_record")?;let mut args342=Vec::new();let mut kw343=Vec::new();args342.push(e.get("shell")?);args342.push(e.get("graph")?);args342.push(Val::None);fun344.call(args342,kw343)?}});fun341.call(args339,kw340)?}};
if {let v345=e.get("box")?;let v346=Val::None;Val::Bool(compare("is_not",v345.clone(),v346.clone())?.truthy()?)}.truthy()? {
e.set("_enclosure_back_top",rt.import_module("_enclosure_back_top")?)?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun349=e.get("stack")?.attr("enter_context")?;let mut args347=Vec::new();let mut kw348=Vec::new();args347.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun352=e.get("_enclosure_back_top")?.attr("_leaves")?;let mut args350=Vec::new();let mut kw351=Vec::new();args350.push(e.get("shell")?);args350.push(e.get("graph")?);args350.push(e.get("box")?);fun352.call(args350,kw351)?}});fun349.call(args347,kw348)?}};
}
Ok(Val::None)});
            let exit_e=e.clone();let exit_rt=rt.clone();
            let exit=Val::function(move|_,_|{let e=exit_e.clone();let rt=exit_rt.clone();let _frame=rt.frame(&e);
        e.get("context335")?.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;let assigned353=e.get("original_cq")?;e.get("shell")?.setattr("cq",assigned353.clone())?;
Ok(Val::None)});Ok(context(enter,exit))})})?; // _measure
    e.set("_measure", {
        let params = vec![("graph".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun356 = e.get("_rust_part")?.attr("check")?;
                    let mut args354 = Vec::new();
                    let mut kw355 = Vec::new();
                    args354.push(Val::Str("enclosure-shell".into()));
                    args354.push(Val::Str("enclosure-checks".into()));
                    args354.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun359 = e.get("graph")?.attr("document")?;
                            let mut args357 = Vec::new();
                            let mut kw358 = Vec::new();
                            fun359.call(args357, kw358)?
                        }
                    });
                    fun356.call(args354, kw355)?
                }
            }
            .get(Val::Str("answers".into()))?);
            Ok(Val::None)
        })
    })?;
    // check_rows
    e.set("check_rows", {
        let params = vec![("bounds".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out360 = Val::list(vec![]);
                for item361 in e.get("bounds")?.iter()? {
                    e.set("row", item361)?;
                    out360.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                                line!(),
                            );
                            {
                                let fun364 = e.get("dict")?;
                                let mut args362 = Vec::new();
                                let mut kw363 = Vec::new();
                                kw363.push(("id".into(), e.get("row")?.attr("id")?));
                                kw363.push(("label".into(), e.get("row")?.attr("label")?));
                                kw363.push(("kind".into(), Val::Str("gate".into())));
                                kw363.push((
                                    "status".into(),
                                    if e.get("row")?.attr("ok")?.truthy()? {
                                        Val::Str("pass".into())
                                    } else {
                                        Val::Str("fail".into())
                                    },
                                ));
                                kw363.push(("value".into(), e.get("row")?.attr("value")?));
                                kw363.push(("target".into(), e.get("row")?.attr("target")?));
                                kw363.push(("detail".into(), e.get("row")?.attr("detail")?));
                                kw363.push(("active".into(), Val::Bool(true)));
                                fun364.call(args362, kw363)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out360
            });
            Ok(Val::None)
        })
    })?;
    // _piece_reports
    e.set("_piece_reports",{let params=vec![("shell".into(),None,false),("box".into(),None,false),("models".into(),None,false),("installed_retainer".into(),None,false),("core".into(),None,false),("graph".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned365={let e=e.child();let out366=Val::dict(vec![]);for item367 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun370=e.get("models")?.attr("items")?;let mut args368=Vec::new();let mut kw369=Vec::new();fun370.call(args368,kw369)?}}.iter()? {let unpack371=unpack(item367,2)?;e.set("name",unpack371[0].clone())?;e.set("model",unpack371[1].clone())?;out366.set(e.get("name")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun374=e.get("graph")?.attr("model")?;let mut args372=Vec::new();let mut kw373=Vec::new();args372.push(e.get("model")?);fun374.call(args372,kw373)?}})?;}out366};e.set("pieces",assigned365.clone())?;
let assigned375=if {let v376=e.get("installed_retainer")?;let v377=Val::None;Val::Bool(compare("is_not",v376.clone(),v377.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun380=e.get("graph")?.attr("model")?;let mut args378=Vec::new();let mut kw379=Vec::new();args378.push(e.get("installed_retainer")?);fun380.call(args378,kw379)?}}} else {Val::None};e.set("seated",assigned375.clone())?;
let assigned381=if {let v382=e.get("core")?;let v383=Val::None;Val::Bool(compare("is_not",v382.clone(),v383.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun386=e.get("graph")?.attr("model")?;let mut args384=Vec::new();let mut kw385=Vec::new();args384.push(e.get("core")?);fun386.call(args384,kw385)?}}} else {Val::None};e.set("cold_core",assigned381.clone())?;
let assigned387={let mut s=Vec::new();Val::list(s)};e.set("collected",assigned387.clone())?;
let assigned388=e.get("shell")?.attr("record_bound")?;e.set("original_record",assigned388.clone())?;
// record
e.set("record",{let params=vec![("row".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun391=e.get("collected")?.attr("append")?;let mut args389=Vec::new();let mut kw390=Vec::new();args389.push(e.get("row")?);fun391.call(args389,kw390)?}};
if {let v392=e.get("graph")?.attr("answers")?;let v393=Val::None;Val::Bool(compare("is_not",v392.clone(),v393.clone())?.truthy()?)}.truthy()? {
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun396=e.get("original_record")?;let mut args394=Vec::new();let mut kw395=Vec::new();args394.push(e.get("row")?);fun396.call(args394,kw395)?}});
}
return Ok(e.get("row")?);
Ok(Val::None)})})?;
let assigned397=e.get("record")?;e.get("shell")?.setattr("record_bound",assigned397.clone())?;
let try_result398=(||->Result<Flow>{let context399={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun402=e.get("_numeric")?;let mut args400=Vec::new();let mut kw401=Vec::new();args400.push(e.get("shell")?);args400.push(e.get("graph")?);args400.push(e.get("box")?);fun402.call(args400,kw401)?}};context399.attr("__enter__")?.call(vec![],vec![])?;let context_result484=(||->Result<Flow>{let assigned403={let mut s=Vec::new();Val::list(s)};e.set("disconnected",assigned403.clone())?;
for item404 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun407=e.get("pieces")?.attr("items")?;let mut args405=Vec::new();let mut kw406=Vec::new();fun407.call(args405,kw406)?}}.iter()? {
let unpack408=unpack(item404,2)?;e.set("name",unpack408[0].clone())?;e.set("piece",unpack408[1].clone())?;let assigned409={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun412=e.get("len")?;let mut args410=Vec::new();let mut kw411=Vec::new();args410.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun415=e.get("piece")?.attr("Solids")?;let mut args413=Vec::new();let mut kw414=Vec::new();fun415.call(args413,kw414)?}});fun412.call(args410,kw411)?}};e.set("count",assigned409.clone())?;
let assigned416={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun419=e.get("piece")?.attr("isValid")?;let mut args417=Vec::new();let mut kw418=Vec::new();fun419.call(args417,kw418)?}};e.set("valid",assigned416.clone())?;
if {let v420={let v421=e.get("count")?;let v422=Val::Int(1i64);Val::Bool(compare("ne",v421.clone(),v422.clone())?.truthy()?)};if v420.truthy()? {v420} else {unary("not",e.get("valid")?)?}}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun425=e.get("disconnected")?.attr("append")?;let mut args423=Vec::new();let mut kw424=Vec::new();args423.push({let mut str426=String::new();str426.push_str(&format(&e.get("name")?,&String::new())?);str426.push_str(": ");str426.push_str(&format(&e.get("count")?,&String::new())?);str426.push_str(" solids");Val::Str(str426)});fun425.call(args423,kw424)?}};
}
}
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun429=e.get("record")?;let mut args427=Vec::new();let mut kw428=Vec::new();args427.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun432=e.get("shell")?.attr("Bound")?;let mut args430=Vec::new();let mut kw431=Vec::new();args430.push(Val::Str("connected-pieces".into()));args430.push(Val::Str("Each printed enclosure piece is one valid connected solid".into()));args430.push(unary("not",e.get("disconnected")?)?);args430.push(if e.get("disconnected")?.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun435=Val::Str("; ".into()).attr("join")?;let mut args433=Vec::new();let mut kw434=Vec::new();args433.push(e.get("disconnected")?);fun435.call(args433,kw434)?}}} else {{let mut str436=String::new();str436.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun439=e.get("len")?;let mut args437=Vec::new();let mut kw438=Vec::new();args437.push(e.get("pieces")?);fun439.call(args437,kw438)?}},&String::new())?);str436.push_str(" connected pieces");Val::Str(str436)}});args430.push(Val::Str("one valid solid per printed piece".into()));args430.push(e.get("disconnected")?);fun432.call(args430,kw431)?}});fun429.call(args427,kw428)?}};
if {let v440=Val::Str("back-top".into());let v441=e.get("pieces")?;Val::Bool(compare("in",v440.clone(),v441.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun444=e.get("shell")?.attr("_ceiling_show_cap_bound")?;let mut args442=Vec::new();let mut kw443=Vec::new();args442.push(e.get("pieces")?.get(Val::Str("back-top".into()))?);args442.push(e.get("box")?);fun444.call(args442,kw443)?}};
}
if {let v447={let v448=Val::Str("front-bottom".into());let v449=e.get("pieces")?;Val::Bool(compare("in",v448.clone(),v449.clone())?.truthy()?)};if v447.truthy()? {{let v445=Val::Str("back-bottom".into());let v446=e.get("pieces")?;Val::Bool(compare("in",v445.clone(),v446.clone())?.truthy()?)}} else {v447}}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun452=e.get("shell")?.attr("_handhold_bound")?;let mut args450=Vec::new();let mut kw451=Vec::new();args450.push(e.get("pieces")?);args450.push(e.get("box")?);fun452.call(args450,kw451)?}};
}
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun455=e.get("shell")?.attr("_silhouette_bound")?;let mut args453=Vec::new();let mut kw454=Vec::new();args453.push(e.get("pieces")?);args453.push(e.get("box")?);fun455.call(args453,kw454)?}};
let attempt456=(||->Result<Flow>{let assigned458={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun461=e.get("shell")?.attr("_report_slide")?;let mut args459=Vec::new();let mut kw460=Vec::new();args459.push(e.get("pieces")?);args459.push(e.get("box")?);fun461.call(args459,kw460)?}};e.set("slides",assigned458.clone())?;
Ok(Flow::Continue)})();let outcome457=(||->Result<Flow>{match attempt456{Ok(Flow::Return(value))=>Ok(Flow::Return(value)),Ok(Flow::Continue)=>{Ok(Flow::Continue)},Err(error)=>{e.set("error",Val::Str(error.to_string()))?;if {let v468={let v469=e.get("graph")?.attr("answers")?;let v470=Val::None;Val::Bool(compare("is_not",v469.clone(),v470.clone())?.truthy()?)};if v468.truthy()? {v468} else {unary("not",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun464={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun467=e.get("str")?;let mut args465=Vec::new();let mut kw466=Vec::new();args465.push(e.get("error")?);fun467.call(args465,kw466)?}}.attr("startswith")?;let mut args462=Vec::new();let mut kw463=Vec::new();args462.push(Val::Str("the back Z-slide catch is not two broad horizontal bearing planes:".into()));fun464.call(args462,kw463)?}})?}}.truthy()? {
anyhow::bail!("{}",val_string(Val::Str("re-raised error".into()))?);
}
let assigned471={let d=Val::dict(vec![]);d};e.set("slides",assigned471.clone())?;
Ok(Flow::Continue)}}})();match outcome457?{Flow::Continue=>{},Flow::Return(value)=>return Ok(Flow::Return(value))}
if {let v472=Val::Str("front-top".into());let v473=e.get("pieces")?;Val::Bool(compare("in",v472.clone(),v473.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun476=e.get("shell")?.attr("_report_facet")?;let mut args474=Vec::new();let mut kw475=Vec::new();args474.push(e.get("pieces")?.get(Val::Str("front-top".into()))?);args474.push(e.get("box")?);fun476.call(args474,kw475)?}};
}
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun479=e.get("shell")?.attr("_report_split")?;let mut args477=Vec::new();let mut kw478=Vec::new();args477.push(e.get("pieces")?);args477.push(e.get("cold_core")?);args477.push(e.get("box")?);kw478.push(("installed_retainer".into(),e.get("seated")?));fun479.call(args477,kw478)?}};
let assigned480={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun483=e.get("shell")?.attr("vent_readings")?;let mut args481=Vec::new();let mut kw482=Vec::new();args481.push(e.get("pieces")?);args481.push(e.get("box")?);fun483.call(args481,kw482)?}};e.set("vents",assigned480.clone())?;
Ok(Flow::Continue)})();context399.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result484? {Flow::Continue=>{},Flow::Return(value)=>return Ok(Flow::Return(value))}
Ok(Flow::Continue)})();
                let handled=match try_result398 {
                    Ok(Flow::Continue)=>(||->Result<Flow>{Ok(Flow::Continue)})(),
                    Ok(flow)=>Ok(flow),Err(error)=>Err(error)};
                let finalized=(||->Result<Flow>{let assigned485=e.get("original_record")?;e.get("shell")?.setattr("record_bound",assigned485.clone())?;
Ok(Flow::Continue)})();
                match finalized? {Flow::Return(value)=>return Ok(value),Flow::Continue=>{}}
                match handled? {Flow::Return(value)=>return Ok(value),Flow::Continue=>{}}
            let assigned486={let d=Val::dict(vec![]);d};e.set("piece_bounds",assigned486.clone())?;
if {let v487=e.get("graph")?.attr("answers")?;let v488=Val::None;Val::Bool(compare("is_not",v487.clone(),v488.clone())?.truthy()?)}.truthy()? {
for item489 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun492=e.get("pieces")?.attr("items")?;let mut args490=Vec::new();let mut kw491=Vec::new();fun492.call(args490,kw491)?}}.iter()? {
let unpack493=unpack(item489,2)?;e.set("name",unpack493[0].clone())?;e.set("piece",unpack493[1].clone())?;let assigned494={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun497=e.get("graph")?.attr("reading")?;let mut args495=Vec::new();let mut kw496=Vec::new();args495.push(e.get("piece")?);fun497.call(args495,kw496)?}};e.set("row",assigned494.clone())?;
let assigned498={let mut s=Vec::new();s.extend(e.get("row")?.get(Val::Str("min".into()))?.iter()?);s.extend(e.get("row")?.get(Val::Str("max".into()))?.iter()?);Val::list(s)};e.get("piece_bounds")?.set(e.get("name")?,assigned498.clone())?;
}
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun501=e.get("dict")?;let mut args499=Vec::new();let mut kw500=Vec::new();kw500.push(("bounds".into(),e.get("collected")?));kw500.push(("checks".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun504=e.get("check_rows")?;let mut args502=Vec::new();let mut kw503=Vec::new();args502.push(e.get("collected")?);fun504.call(args502,kw503)?}}));kw500.push(("slides".into(),e.get("slides")?));kw500.push(("vents".into(),e.get("vents")?));kw500.push(("piece_bounds".into(),e.get("piece_bounds")?));fun501.call(args499,kw500)?}});
Ok(Val::None)})})?;
    // check_pieces
    e.set("check_pieces", {
        let params = vec![
            ("shell".into(), None, false),
            ("box".into(), None, false),
            ("models".into(), None, false),
            ("installed_retainer".into(), Some(Val::None), false),
            ("core".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v507 = {
                    let v508 = Val::Str("pump-retainer".into());
                    let v509 = e.get("models")?;
                    Val::Bool(compare("in", v508.clone(), v509.clone())?.truthy()?)
                };
                if v507.truthy()? {
                    {
                        let v505 = e.get("installed_retainer")?;
                        let v506 = Val::None;
                        Val::Bool(compare("is", v505.clone(), v506.clone())?.truthy()?)
                    }
                } else {
                    v507
                }
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun512 = e.get("ValueError")?;
                            let mut args510 = Vec::new();
                            let mut kw511 = Vec::new();
                            args510.push(Val::Str(
                                "enclosure checks need the explicit installed retainer model"
                                    .into(),
                            ));
                            fun512.call(args510, kw511)?
                        }
                    })?
                );
            }
            let assigned513 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun516 = e.get("_Questions")?;
                    let mut args514 = Vec::new();
                    let mut kw515 = Vec::new();
                    fun516.call(args514, kw515)?
                }
            };
            e.set("graph", assigned513.clone())?;
            let context517 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun520 = e.get("redirect_stdout")?;
                    let mut args518 = Vec::new();
                    let mut kw519 = Vec::new();
                    args518.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun523 = e.get("io")?.attr("StringIO")?;
                            let mut args521 = Vec::new();
                            let mut kw522 = Vec::new();
                            fun523.call(args521, kw522)?
                        }
                    });
                    fun520.call(args518, kw519)?
                }
            };
            context517.attr("__enter__")?.call(vec![], vec![])?;
            let context_result527 = (|| -> Result<Flow> {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                        line!(),
                    );
                    {
                        let fun526 = e.get("_piece_reports")?;
                        let mut args524 = Vec::new();
                        let mut kw525 = Vec::new();
                        args524.push(e.get("shell")?);
                        args524.push(e.get("box")?);
                        args524.push(e.get("models")?);
                        args524.push(e.get("installed_retainer")?);
                        args524.push(e.get("core")?);
                        args524.push(e.get("graph")?);
                        fun526.call(args524, kw525)?
                    }
                };
                Ok(Flow::Continue)
            })();
            context517
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result527? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
            }
            let assigned528 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun531 = e.get("_measure")?;
                    let mut args529 = Vec::new();
                    let mut kw530 = Vec::new();
                    args529.push(e.get("graph")?);
                    fun531.call(args529, kw530)?
                }
            };
            e.set("answers", assigned528.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                    line!(),
                );
                {
                    let fun534 = e.get("_piece_reports")?;
                    let mut args532 = Vec::new();
                    let mut kw533 = Vec::new();
                    args532.push(e.get("shell")?);
                    args532.push(e.get("box")?);
                    args532.push(e.get("models")?);
                    args532.push(e.get("installed_retainer")?);
                    args532.push(e.get("core")?);
                    args532.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",
                            line!(),
                        );
                        {
                            let fun537 = e.get("_Questions")?;
                            let mut args535 = Vec::new();
                            let mut kw536 = Vec::new();
                            args535.push(e.get("answers")?);
                            fun537.call(args535, kw536)?
                        }
                    });
                    fun534.call(args532, kw533)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // box_readings
    e.set("box_readings",{let params=vec![("shell".into(),None,false),("pack".into(),None,false),("bounds".into(),None,false),("references".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);// ask
e.set("ask",{let params=vec![("graph".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let context538={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun541=e.get("_numeric")?;let mut args539=Vec::new();let mut kw540=Vec::new();args539.push(e.get("shell")?);args539.push(e.get("graph")?);fun541.call(args539,kw540)?}};context538.attr("__enter__")?.call(vec![],vec![])?;let context_result655=(||->Result<Flow>{let assigned542={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun545=e.get("shell")?.attr("box_question_tools")?;let mut args543=Vec::new();let mut kw544=Vec::new();args543.push(e.get("pack")?);args543.push(e.get("bounds")?);fun545.call(args543,kw544)?}};let unpack546=unpack(assigned542.clone(),2)?;e.set("tools",unpack546[0].clone())?;e.set("questions",unpack546[1].clone())?;
let assigned547={let e=e.child();let out548=Val::dict(vec![]);for item549 in e.get("pack")?.attr("placed")?.iter()? {e.set("name",item549)?;out548.set(e.get("name")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun552=e.get("graph")?.attr("model")?;let mut args550=Vec::new();let mut kw551=Vec::new();args550.push(e.get("references")?.get(e.get("name")?)?);fun552.call(args550,kw551)?}})?;}out548};e.set("bodies",assigned547.clone())?;
let assigned553={let e=e.child();let out554=Val::dict(vec![]);for item555 in {let mut s=Vec::new();s.push(Val::Str("floor".into()));s.push(Val::Str("under".into()));s.push(Val::Str("pillars".into()));Val::tuple(s)}.iter()? {e.set("family",item555)?;out554.set(e.get("family")?,{let d=Val::dict(vec![]);d})?;}out554};e.set("tables",assigned553.clone())?;
let assigned556={let d=Val::dict(vec![]);d.set(Val::Str("front".into()),{let d=Val::dict(vec![]);d})?;d.set(Val::Str("back".into()),{let d=Val::dict(vec![]);d})?;d};e.get("tables")?.set(Val::Str("lip".into()),assigned556.clone())?;
for item557 in e.get("questions")?.iter()? {
e.set("question",item557)?;let assigned558=e.get("tools")?.get(e.get("question")?.get(Val::Str("tool".into()))?)?;e.set("tool",assigned558.clone())?;
let assigned559={let d=Val::dict(vec![]);d.set(Val::Str("volume_mm3".into()),Val::Float(0.0f64))?;d.set(Val::Str("min".into()),Val::None)?;d.set(Val::Str("max".into()),Val::None)?;d};e.set("raw",assigned559.clone())?;
if e.get("question")?.get(Val::Str("positive_components".into()))?.truthy()? {
let assigned560={let mut s=Vec::new();Val::list(s)};e.get("raw")?.set(Val::Str("components".into()),assigned560.clone())?;
}
let assigned561={let v562=e.get("tool")?;let v563=Val::None;Val::Bool(compare("is_not",v562.clone(),v563.clone())?.truthy()?)};e.set("overlaps",assigned561.clone())?;
if {let v566=e.get("overlaps")?;if v566.truthy()? {{let v564=e.get("tool")?.attr("bounds")?;let v565=Val::None;Val::Bool(compare("is_not",v564.clone(),v565.clone())?.truthy()?)}} else {v566}}.truthy()? {
let assigned567=e.get("bounds")?.get(e.get("question")?.get(Val::Str("body".into()))?)?;let unpack568=unpack(assigned567.clone(),2)?;e.set("lower",unpack568[0].clone())?;e.set("upper",unpack568[1].clone())?;
let assigned569={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun572=e.get("all")?;let mut args570=Vec::new();let mut kw571=Vec::new();args570.push({let e=e.child();let out573=Val::list(vec![]);for item574 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun577=e.get("range")?;let mut args575=Vec::new();let mut kw576=Vec::new();args575.push(Val::Int(3i64));fun577.call(args575,kw576)?}}.iter()? {e.set("k",item574)?;out573.attr("append")?.call(vec![{let v580={let v581=e.get("upper")?.get(e.get("k")?)?;let v582=e.get("tool")?.attr("bounds")?.get(binary("mul",Val::Int(2i64),e.get("k")?)?)?;Val::Bool(compare("gt",v581.clone(),v582.clone())?.truthy()?)};if v580.truthy()? {{let v578=e.get("tool")?.attr("bounds")?.get(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(1i64))?)?;let v579=e.get("lower")?.get(e.get("k")?)?;Val::Bool(compare("gt",v578.clone(),v579.clone())?.truthy()?)}} else {v580}}],vec![])?;}out573});fun572.call(args570,kw571)?}};e.set("overlaps",assigned569.clone())?;
}
if e.get("overlaps")?.truthy()? {
let assigned583=e.get("references")?.get(e.get("question")?.get(Val::Str("body".into()))?)?;e.set("reference",assigned583.clone())?;
let assigned584=if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun587=e.get("isinstance")?;let mut args585=Vec::new();let mut kw586=Vec::new();args585.push(e.get("reference")?);args585.push({let mut s=Vec::new();s.push(e.get("list")?);s.push(e.get("tuple")?);Val::tuple(s)});fun587.call(args585,kw586)?}}.truthy()? {e.get("reference")?} else {{let mut s=Vec::new();s.push(e.get("reference")?);Val::list(s)}};e.set("instances",assigned584.clone())?;
let assigned588={let e=e.child();let out589=Val::list(vec![]);for item590 in e.get("instances")?.iter()? {e.set("ref",item590)?;for item591 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun594=e.get("ref")?.attr("get")?;let mut args592=Vec::new();let mut kw593=Vec::new();args592.push(Val::Str("indices".into()));args592.push({let mut s=Vec::new();Val::tuple(s)});fun594.call(args592,kw593)?}}.iter()? {e.set("i",item591)?;out589.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun597=e.get("dict")?;let mut args595=Vec::new();let mut kw596=Vec::new();args595.push(e.get("ref")?);kw596.push(("indices".into(),{let mut s=Vec::new();s.push(e.get("i")?);Val::list(s)}));fun597.call(args595,kw596)?}}],vec![])?;}}out589};e.set("sections",assigned588.clone())?;
if {let v603=e.get("question")?.get(Val::Str("body_first".into()))?;if v603.truthy()? {{let v601={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun600=e.get("len")?;let mut args598=Vec::new();let mut kw599=Vec::new();args598.push(e.get("sections")?);fun600.call(args598,kw599)?}};let v602=Val::Int(1i64);Val::Bool(compare("gt",v601.clone(),v602.clone())?.truthy()?)}} else {v603}}.truthy()? {
let assigned604={let e=e.child();let out605=Val::list(vec![]);for item606 in e.get("sections")?.iter()? {e.set("ref",item606)?;out605.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun609={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun612=e.get("graph")?.attr("model")?;let mut args610=Vec::new();let mut kw611=Vec::new();args610.push(e.get("ref")?);fun612.call(args610,kw611)?}}.attr("intersect")?;let mut args607=Vec::new();let mut kw608=Vec::new();args607.push(e.get("tool")?);fun609.call(args607,kw608)?}}],vec![])?;}out605};e.set("hits",assigned604.clone())?;
let assigned613={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun616=e.get("graph")?.attr("add")?;let mut args614=Vec::new();let mut kw615=Vec::new();args614.push(Val::Str("compose".into()));args614.push({let e=e.child();let out617=Val::list(vec![]);for item618 in e.get("hits")?.iter()? {e.set("shape",item618)?;out617.attr("append")?.call(vec![e.get("shape")?.attr("index")?],vec![])?;}out617});fun616.call(args614,kw615)?}};e.set("hit",assigned613.clone())?;
}else{
let assigned619=e.get("bodies")?.get(e.get("question")?.get(Val::Str("body".into()))?)?;e.set("body",assigned619.clone())?;
let assigned620=if e.get("question")?.get(Val::Str("body_first".into()))?.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun623=e.get("body")?.attr("intersect")?;let mut args621=Vec::new();let mut kw622=Vec::new();args621.push(e.get("tool")?);fun623.call(args621,kw622)?}}} else {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun626=e.get("tool")?.attr("intersect")?;let mut args624=Vec::new();let mut kw625=Vec::new();args624.push(e.get("body")?);fun626.call(args624,kw625)?}}};e.set("hit",assigned620.clone())?;
}
let assigned627={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun630=e.get("graph")?.attr("reading")?;let mut args628=Vec::new();let mut kw629=Vec::new();args628.push(e.get("hit")?);kw629.push(("components".into(),e.get("question")?.get(Val::Str("positive_components".into()))?));fun630.call(args628,kw629)?}};e.set("raw",assigned627.clone())?;
let assigned631={let e=e.child();let out632=Val::dict(vec![]);for item633 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun636=e.get("raw")?.attr("items")?;let mut args634=Vec::new();let mut kw635=Vec::new();fun636.call(args634,kw635)?}}.iter()? {let unpack637=unpack(item633,2)?;e.set("key",unpack637[0].clone())?;e.set("value",unpack637[1].clone())?;if {let v638=e.get("key")?;let v639=Val::Str("valid".into());Val::Bool(compare("ne",v638.clone(),v639.clone())?.truthy()?)}.truthy()? {out632.set(e.get("key")?,e.get("value")?)?;}}out632};e.set("raw",assigned631.clone())?;
}
let assigned640={let mut s=Vec::new();s.push(e.get("question")?.get(Val::Str("family".into()))?);s.push(e.get("question")?.get(Val::Str("key".into()))?);Val::tuple(s)};let unpack641=unpack(assigned640.clone(),2)?;e.set("family",unpack641[0].clone())?;e.set("key",unpack641[1].clone())?;
if {let v642=e.get("family")?;let v643=Val::Str("lip".into());Val::Bool(compare("eq",v642.clone(),v643.clone())?.truthy()?)}.truthy()? {
let assigned644=e.get("raw")?;e.get("tables")?.get(e.get("family")?)?.get(e.get("key")?.get(Val::Int(0i64))?)?.set(e.get("key")?.get(Val::Int(1i64))?,assigned644.clone())?;
}else{
let assigned645=e.get("raw")?;e.get("tables")?.get(e.get("family")?)?.set({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun648=e.get("tuple")?;let mut args646=Vec::new();let mut kw647=Vec::new();args646.push(e.get("key")?);fun648.call(args646,kw647)?}},assigned645.clone())?;
}
}
return Ok(Flow::Return({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun651=e.get("shell")?.attr("BoxReadings")?;let mut args649=Vec::new();let mut kw650=Vec::new();args649.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun654=e.get("dict")?;let mut args652=Vec::new();let mut kw653=Vec::new();args652.push(e.get("bounds")?);fun654.call(args652,kw653)?}});args649.push(e.get("tables")?.get(Val::Str("lip".into()))?);args649.push(e.get("tables")?.get(Val::Str("floor".into()))?);args649.push(e.get("tables")?.get(Val::Str("under".into()))?);args649.push(e.get("tables")?.get(Val::Str("pillars".into()))?);fun651.call(args649,kw650)?}}));
Ok(Flow::Continue)})();context538.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result655? {Flow::Continue=>{},Flow::Return(value)=>return Ok(value)}
Ok(Val::None)})})?;
let assigned656={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun659=e.get("_Questions")?;let mut args657=Vec::new();let mut kw658=Vec::new();fun659.call(args657,kw658)?}};e.set("graph",assigned656.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun662=e.get("ask")?;let mut args660=Vec::new();let mut kw661=Vec::new();args660.push(e.get("graph")?);fun662.call(args660,kw661)?}};
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun665=e.get("ask")?;let mut args663=Vec::new();let mut kw664=Vec::new();args663.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun668=e.get("_Questions")?;let mut args666=Vec::new();let mut kw667=Vec::new();args666.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_rust_enclosure_checks.rs",line!());{let fun671=e.get("_measure")?;let mut args669=Vec::new();let mut kw670=Vec::new();args669.push(e.get("graph")?);fun671.call(args669,kw670)?}});fun668.call(args666,kw667)?}});fun665.call(args663,kw664)?}});
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
