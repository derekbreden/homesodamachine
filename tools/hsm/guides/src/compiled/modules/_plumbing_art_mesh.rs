//! Guide recipe: `hardware/install-guide/_plumbing_art_mesh.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("tempfile", rt.import_module("tempfile")?)?;
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    // note_read
    e.set("note_read", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let attempt2 = (|| -> Result<Flow> {
                {
                    let fun6 = e.get("_rust_part")?.attr("_READ_TARGETS")?.attr("add")?;
                    let mut args4 = Vec::new();
                    let mut kw5 = Vec::new();
                    args4.push({
                        let fun9 = e.get("_rust_part")?.attr("_relative")?;
                        let mut args7 = Vec::new();
                        let mut kw8 = Vec::new();
                        args7.push({
                            let fun12 = e.get("Path")?;
                            let mut args10 = Vec::new();
                            let mut kw11 = Vec::new();
                            args10.push(e.get("path")?);
                            fun12.call(args10, kw11)?
                        });
                        fun9.call(args7, kw8)?
                    });
                    fun6.call(args4, kw5)?
                };
                Ok(Flow::Continue)
            })();
            let outcome3 = (|| -> Result<Flow> {
                match attempt2 {
                    Ok(flow @ (Flow::Return(_) | Flow::Break | Flow::Next)) => Ok(flow),
                    Ok(Flow::Continue) => Ok(Flow::Continue),
                    Err(error) => Ok(Flow::Continue),
                }
            })();
            match outcome3? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            Ok(Val::None)
        })
    })?;
    // note_write
    e.set("note_write", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let attempt13 = (|| -> Result<Flow> {
                {
                    let fun17 = e.get("_rust_part")?.attr("_WRITE_TARGETS")?.attr("add")?;
                    let mut args15 = Vec::new();
                    let mut kw16 = Vec::new();
                    args15.push({
                        let fun20 = e.get("_rust_part")?.attr("_relative")?;
                        let mut args18 = Vec::new();
                        let mut kw19 = Vec::new();
                        args18.push({
                            let fun23 = e.get("Path")?;
                            let mut args21 = Vec::new();
                            let mut kw22 = Vec::new();
                            args21.push(e.get("path")?);
                            fun23.call(args21, kw22)?
                        });
                        fun20.call(args18, kw19)?
                    });
                    fun17.call(args15, kw16)?
                };
                Ok(Flow::Continue)
            })();
            let outcome14 = (|| -> Result<Flow> {
                match attempt13 {
                    Ok(flow @ (Flow::Return(_) | Flow::Break | Flow::Next)) => Ok(flow),
                    Ok(Flow::Continue) => Ok(Flow::Continue),
                    Err(error) => Ok(Flow::Continue),
                }
            })();
            match outcome14? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            Ok(Val::None)
        })
    })?;
    // _plain
    e.set("_plain", {
        let params = vec![("value".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let v36 = {
                    let fun39 = e.get("isinstance")?;
                    let mut args37 = Vec::new();
                    let mut kw38 = Vec::new();
                    args37.push(e.get("value")?);
                    args37.push({
                        let mut s = Vec::new();
                        s.push(e.get("str")?);
                        s.push(e.get("int")?);
                        s.push(e.get("float")?);
                        s.push(e.get("bool")?);
                        s.push({
                            let fun42 = e.get("type")?;
                            let mut args40 = Vec::new();
                            let mut kw41 = Vec::new();
                            args40.push(Val::None);
                            fun42.call(args40, kw41)?
                        });
                        Val::tuple(s)
                    });
                    fun39.call(args37, kw38)?
                };
                if v36.truthy()? {
                    v36
                } else {
                    {
                        let v32 = {
                            let fun35 = e.get("isinstance")?;
                            let mut args33 = Vec::new();
                            let mut kw34 = Vec::new();
                            args33.push(e.get("value")?);
                            args33.push({
                                let mut s = Vec::new();
                                s.push(e.get("tuple")?);
                                s.push(e.get("list")?);
                                Val::tuple(s)
                            });
                            fun35.call(args33, kw34)?
                        };
                        if v32.truthy()? {
                            {
                                let fun26 = e.get("all")?;
                                let mut args24 = Vec::new();
                                let mut kw25 = Vec::new();
                                args24.push({
                                    let e = e.child();
                                    let out27 = Val::list(vec![]);
                                    for item28 in e.get("value")?.iter()? {
                                        e.set("item", item28)?;
                                        out27.attr("append")?.call(
                                            vec![{
                                                let fun31 = e.get("_plain")?;
                                                let mut args29 = Vec::new();
                                                let mut kw30 = Vec::new();
                                                args29.push(e.get("item")?);
                                                fun31.call(args29, kw30)?
                                            }],
                                            vec![],
                                        )?;
                                    }
                                    out27
                                });
                                fun26.call(args24, kw25)?
                            }
                        } else {
                            v32
                        }
                    }
                }
            });
            Ok(Val::None)
        })
    })?;
    // export
    e.set("export", {
        let params = vec![
            ("module".into(), None, false),
            ("names".into(), None, false),
            ("directory".into(), None, false),
            ("modern".into(), Some(Val::Bool(false)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod43 = rt.import_module("_rust_data")?;
            e.set("request", rt.member("_rust_data", "request")?)?;
            let assigned44 = {
                let e = e.child();
                let out45 = Val::dict(vec![]);
                for item46 in {
                    let fun49 = {
                        let fun52 = e.get("vars")?;
                        let mut args50 = Vec::new();
                        let mut kw51 = Vec::new();
                        args50.push(e.get("module")?);
                        fun52.call(args50, kw51)?
                    }
                    .attr("items")?;
                    let mut args47 = Vec::new();
                    let mut kw48 = Vec::new();
                    fun49.call(args47, kw48)?
                }
                .iter()?
                {
                    let unpack53 = unpack(item46, 2)?;
                    e.set("name", unpack53[0].clone())?;
                    e.set("value", unpack53[1].clone())?;
                    if {
                        let fun56 = e.get("_plain")?;
                        let mut args54 = Vec::new();
                        let mut kw55 = Vec::new();
                        args54.push(e.get("value")?);
                        fun56.call(args54, kw55)?
                    }
                    .truthy()?
                    {
                        out45.set(e.get("name")?, e.get("value")?)?;
                    }
                }
                out45
            };
            e.set("values", assigned44.clone())?;
            let assigned57 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("op".into()), Val::Str("plumbing".into()))?;
                d.set(Val::Str("fn".into()), Val::Str("spec".into()))?;
                d.set(Val::Str("modern".into()), e.get("modern")?)?;
                d.set(Val::Str("names".into()), {
                    let fun60 = e.get("list")?;
                    let mut args58 = Vec::new();
                    let mut kw59 = Vec::new();
                    args58.push(e.get("names")?);
                    fun60.call(args58, kw59)?
                })?;
                d.set(Val::Str("facts".into()), e.get("values")?)?;
                d
            };
            e.set("source", assigned57.clone())?;
            if e.get("modern")?.truthy()? {
                let assigned61 = e.get("module")?.attr("union_ref")?;
                e.set("union", assigned61.clone())?;
                {
                    let fun64 = e.get("note_read")?;
                    let mut args62 = Vec::new();
                    let mut kw63 = Vec::new();
                    args62.push(e.get("union")?.attr("PAYLOAD_PATH")?);
                    fun64.call(args62, kw63)?
                };
                let assigned65 = {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("payload".into()), {
                        let fun68 = e.get("str")?;
                        let mut args66 = Vec::new();
                        let mut kw67 = Vec::new();
                        args66.push({
                            let fun71 =
                                e.get("union")?.attr("PAYLOAD_PATH")?.attr("relative_to")?;
                            let mut args69 = Vec::new();
                            let mut kw70 = Vec::new();
                            args69.push(e.get("module")?.attr("ROOT")?);
                            fun71.call(args69, kw70)?
                        });
                        fun68.call(args66, kw67)?
                    })?;
                    d.set(
                        Val::Str("ring_start".into()),
                        e.get("union")?.attr("ring_face_z")?,
                    )?;
                    d.set(
                        Val::Str("ring_end".into()),
                        e.get("union")?.attr("port_face_z")?,
                    )?;
                    d.set(
                        Val::Str("collet_d".into()),
                        e.get("union")?.attr("COLLET_D")?,
                    )?;
                    d.set(
                        Val::Str("collet_bore".into()),
                        e.get("union")?.attr("COLLET_BORE")?,
                    )?;
                    d
                };
                e.get("source")?
                    .set(Val::Str("union".into()), assigned65.clone())?;
            }
            let assigned72 = {
                let fun75 = e.get("Path")?;
                let mut args73 = Vec::new();
                let mut kw74 = Vec::new();
                args73.push(e.get("directory")?);
                fun75.call(args73, kw74)?
            };
            e.set("directory", assigned72.clone())?;
            {
                let fun78 = e.get("directory")?.attr("mkdir")?;
                let mut args76 = Vec::new();
                let mut kw77 = Vec::new();
                kw77.push(("parents".into(), Val::Bool(true)));
                kw77.push(("exist_ok".into(), Val::Bool(true)));
                fun78.call(args76, kw77)?
            };
            let context79 = {
                let fun82 = e.get("tempfile")?.attr("TemporaryDirectory")?;
                let mut args80 = Vec::new();
                let mut kw81 = Vec::new();
                kw81.push(("prefix".into(), Val::Str(".plumbing-props-".into())));
                kw81.push(("dir".into(), e.get("module")?.attr("HERE")?));
                fun82.call(args80, kw81)?
            };
            e.set(
                "temporary",
                context79.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result110 = (|| -> Result<Flow> {
                let assigned83 = binary(
                    "truediv",
                    {
                        let fun86 = e.get("Path")?;
                        let mut args84 = Vec::new();
                        let mut kw85 = Vec::new();
                        args84.push(e.get("temporary")?);
                        fun86.call(args84, kw85)?
                    },
                    Val::Str("numbers.json".into()),
                )?;
                e.set("path", assigned83.clone())?;
                {
                    let fun89 = e.get("request")?;
                    let mut args87 = Vec::new();
                    let mut kw88 = Vec::new();
                    args87.push(Val::Str("faucet-data".into()));
                    args87.push(Val::Str("faucet-data".into()));
                    args87.push({
                        let d = Val::dict(vec![]);
                        dict_extend(&d, e.get("source")?)?;
                        d.set(Val::Str("output".into()), {
                            let fun92 = e.get("str")?;
                            let mut args90 = Vec::new();
                            let mut kw91 = Vec::new();
                            args90.push(e.get("path")?);
                            fun92.call(args90, kw91)?
                        })?;
                        d
                    });
                    fun89.call(args87, kw88)?
                };
                for item93 in {
                    let fun106 = {
                        let fun109 = e.get("_rust_part")?.attr("run")?;
                        let mut args107 = Vec::new();
                        let mut kw108 = Vec::new();
                        args107.push(Val::Str("tooling".into()));
                        args107.push(Val::Str("install-art-props".into()));
                        args107.push(e.get("path")?);
                        args107.push(e.get("directory")?);
                        fun109.call(args107, kw108)?
                    }
                    .attr("splitlines")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    fun106.call(args104, kw105)?
                }
                .iter()?
                {
                    e.set("line", item93)?;
                    if {
                        let fun96 = e.get("line")?.attr("strip")?;
                        let mut args94 = Vec::new();
                        let mut kw95 = Vec::new();
                        fun96.call(args94, kw95)?
                    }
                    .truthy()?
                    {
                        for item97 in {
                            let fun103 = e.get("json")?.attr("loads")?;
                            let mut args101 = Vec::new();
                            let mut kw102 = Vec::new();
                            args101.push(e.get("line")?);
                            fun103.call(args101, kw102)?
                        }
                        .get(Val::Str("files".into()))?
                        .iter()?
                        {
                            e.set("name", item97)?;
                            {
                                let fun100 = e.get("note_write")?;
                                let mut args98 = Vec::new();
                                let mut kw99 = Vec::new();
                                args98.push(binary(
                                    "truediv",
                                    e.get("directory")?,
                                    e.get("name")?,
                                )?);
                                fun100.call(args98, kw99)?
                            };
                        }
                    }
                }
                Ok(Flow::Continue)
            })();
            context79
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result110? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            return Ok({
                let e = e.child();
                let out111 = Val::dict(vec![]);
                for item112 in e.get("names")?.iter()? {
                    e.set("name", item112)?;
                    out111.set(
                        e.get("name")?,
                        binary("truediv", e.get("directory")?, {
                            let mut str113 = String::new();
                            str113.push_str(&format(&e.get("name")?, &String::new())?);
                            str113.push_str(".step");
                            Val::Str(str113)
                        })?,
                    )?;
                }
                out111
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
