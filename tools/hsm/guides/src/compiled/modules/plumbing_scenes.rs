//! Guide recipe: `hardware/install-guide/plumbing/plumbing_scenes.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let fun5 = {
            let fun8 = e.get("Path")?;
            let mut args6 = Vec::new();
            let mut kw7 = Vec::new();
            args6.push(e.get("__file__")?);
            fun8.call(args6, kw7)?
        }
        .attr("resolve")?;
        let mut args3 = Vec::new();
        let mut kw4 = Vec::new();
        fun5.call(args3, kw4)?
    }
    .attr("parent")?;
    e.set("HERE", assigned2.clone())?;
    let assigned9 = {
        let fun12 = e.get("next")?;
        let mut args10 = Vec::new();
        let mut kw11 = Vec::new();
        args10.push({
            let e = e.child();
            let out13 = Val::list(vec![]);
            for item14 in e.get("HERE")?.attr("parents")?.iter()? {
                e.set("parent", item14)?;
                if {
                    let v15 = e.get("parent")?.attr("name")?;
                    let v16 = Val::Str("hardware".into());
                    Val::Bool(compare("eq", v15.clone(), v16.clone())?.truthy()?)
                }
                .truthy()?
                {
                    out13.attr("append")?.call(vec![e.get("parent")?], vec![])?;
                }
            }
            out13
        });
        fun12.call(args10, kw11)?
    };
    e.set("HARDWARE", assigned9.clone())?;
    let assigned17 = e.get("HARDWARE")?.attr("parent")?;
    e.set("ROOT", assigned17.clone())?;
    let assigned18 = binary("truediv", e.get("HERE")?, Val::Str("out".into()))?;
    e.set("OUT", assigned18.clone())?;
    let assigned19 = binary("truediv", e.get("HERE")?, Val::Str("art".into()))?;
    e.set("ART", assigned19.clone())?;
    {
        let fun22 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args20 = Vec::new();
        let mut kw21 = Vec::new();
        args20.push(Val::Int(0i64));
        args20.push({
            let fun25 = e.get("str")?;
            let mut args23 = Vec::new();
            let mut kw24 = Vec::new();
            args23.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("scripts".into()),
            )?);
            fun25.call(args23, kw24)?
        });
        fun22.call(args20, kw21)?
    };
    {
        let fun28 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args26 = Vec::new();
        let mut kw27 = Vec::new();
        args26.push(Val::Int(0i64));
        args26.push({
            let fun31 = e.get("str")?;
            let mut args29 = Vec::new();
            let mut kw30 = Vec::new();
            args29.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("install-guide".into()),
            )?);
            fun31.call(args29, kw30)?
        });
        fun28.call(args26, kw27)?
    };
    e.set("_hsm_render", rt.import_module("_hsm_render")?)?;
    let mod32 = rt.import_module("_rust_data")?;
    e.set("_data_request", rt.member("_rust_data", "request")?)?;
    // _plumbing_data
    e.set("_plumbing_data", {
        let params = vec![("fn".into(), Some(Val::Str("datums".into())), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, Some("values"))?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun35 = e.get("_data_request")?;
                let mut args33 = Vec::new();
                let mut kw34 = Vec::new();
                args33.push(Val::Str("faucet-data".into()));
                args33.push(Val::Str("faucet-data".into()));
                args33.push({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("op".into()), Val::Str("plumbing".into()))?;
                    d.set(Val::Str("fn".into()), e.get("fn")?)?;
                    d.set(Val::Str("root".into()), {
                        let fun38 = e.get("str")?;
                        let mut args36 = Vec::new();
                        let mut kw37 = Vec::new();
                        args36.push(e.get("ROOT")?);
                        fun38.call(args36, kw37)?
                    })?;
                    d.set(Val::Str("modern".into()), Val::Bool(false))?;
                    dict_extend(&d, e.get("values")?)?;
                    d
                });
                fun35.call(args33, kw34)?
            });
            Ok(Val::None)
        })
    })?;
    {
        let fun41 = {
            let fun44 = e.get("globals")?;
            let mut args42 = Vec::new();
            let mut kw43 = Vec::new();
            fun44.call(args42, kw43)?
        }
        .attr("update")?;
        let mut args39 = Vec::new();
        let mut kw40 = Vec::new();
        args39.push({
            let fun47 = e.get("_plumbing_data")?;
            let mut args45 = Vec::new();
            let mut kw46 = Vec::new();
            fun47.call(args45, kw46)?
        });
        fun41.call(args39, kw40)?
    };
    let assigned48 = {
        let fun51 = e.get("tuple")?;
        let mut args49 = Vec::new();
        let mut kw50 = Vec::new();
        args49.push(e.get("SCENE_NAMES")?);
        fun51.call(args49, kw50)?
    };
    e.set("SCENE_NAMES", assigned48.clone())?;
    // _render
    e.set("_render", {
        let params = vec![
            ("step_paths".into(), None, false),
            ("art_dir".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned52 = {
                let fun55 = e.get("_plumbing_data")?;
                let mut args53 = Vec::new();
                let mut kw54 = Vec::new();
                args53.push(Val::Str("legacy-jobs".into()));
                kw54.push(("steps".into(), {
                    let e = e.child();
                    let out56 = Val::dict(vec![]);
                    for item57 in {
                        let fun60 = e.get("step_paths")?.attr("items")?;
                        let mut args58 = Vec::new();
                        let mut kw59 = Vec::new();
                        fun60.call(args58, kw59)?
                    }
                    .iter()?
                    {
                        let unpack61 = unpack(item57, 2)?;
                        e.set("name", unpack61[0].clone())?;
                        e.set("path", unpack61[1].clone())?;
                        out56.set(e.get("name")?, {
                            let fun64 = e.get("str")?;
                            let mut args62 = Vec::new();
                            let mut kw63 = Vec::new();
                            args62.push(e.get("path")?);
                            fun64.call(args62, kw63)?
                        })?;
                    }
                    out56
                }));
                kw54.push(("directory".into(), {
                    let fun67 = e.get("str")?;
                    let mut args65 = Vec::new();
                    let mut kw66 = Vec::new();
                    args65.push(e.get("art_dir")?);
                    fun67.call(args65, kw66)?
                }));
                fun55.call(args53, kw54)?
            };
            e.set("jobs", assigned52.clone())?;
            {
                let fun70 = e.get("_hsm_render")?.attr("render")?;
                let mut args68 = Vec::new();
                let mut kw69 = Vec::new();
                args68.push(e.get("jobs")?);
                fun70.call(args68, kw69)?
            };
            for item71 in e.get("jobs")?.iter()? {
                e.set("row", item71)?;
                {
                    let fun74 = e.get("_plumbing_data")?;
                    let mut args72 = Vec::new();
                    let mut kw73 = Vec::new();
                    args72.push(Val::Str("canonicalize-png".into()));
                    kw73.push(("path".into(), e.get("row")?.get(Val::Str("out".into()))?));
                    fun74.call(args72, kw73)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned75 = {
                let fun78 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args76 = Vec::new();
                let mut kw77 = Vec::new();
                kw77.push(("description".into(), e.get("__doc__")?));
                fun78.call(args76, kw77)?
            };
            e.set("parser", assigned75.clone())?;
            {
                let fun81 = e.get("parser")?.attr("add_argument")?;
                let mut args79 = Vec::new();
                let mut kw80 = Vec::new();
                args79.push(Val::Str("--out-dir".into()));
                kw80.push(("type".into(), e.get("Path")?));
                kw80.push(("default".into(), e.get("OUT")?));
                kw80.push(("help".into(), {
                    let mut str82 = String::new();
                    str82.push_str("STEP/PNG output directory (default: ");
                    str82.push_str(&format(
                        &{
                            let fun85 = e.get("OUT")?.attr("relative_to")?;
                            let mut args83 = Vec::new();
                            let mut kw84 = Vec::new();
                            args83.push(e.get("ROOT")?);
                            fun85.call(args83, kw84)?
                        },
                        &String::new(),
                    )?);
                    str82.push_str(")");
                    Val::Str(str82)
                }));
                fun81.call(args79, kw80)?
            };
            {
                let fun88 = e.get("parser")?.attr("add_argument")?;
                let mut args86 = Vec::new();
                let mut kw87 = Vec::new();
                args86.push(Val::Str("--render".into()));
                kw87.push(("dest".into(), Val::Str("render".into())));
                kw87.push(("action".into(), Val::Str("store_true".into())));
                kw87.push((
                    "help".into(),
                    Val::Str(
                        "render the four registered 2000x1100 instruction PNGs (the default)"
                            .into(),
                    ),
                ));
                fun88.call(args86, kw87)?
            };
            {
                let fun91 = e.get("parser")?.attr("add_argument")?;
                let mut args89 = Vec::new();
                let mut kw90 = Vec::new();
                args89.push(Val::Str("--steps-only".into()));
                kw90.push(("dest".into(), Val::Str("render".into())));
                kw90.push(("action".into(), Val::Str("store_false".into())));
                kw90.push((
                    "help".into(),
                    Val::Str("export only the STEP and mesh intermediates".into()),
                ));
                fun91.call(args89, kw90)?
            };
            {
                let fun94 = e.get("parser")?.attr("add_argument")?;
                let mut args92 = Vec::new();
                let mut kw93 = Vec::new();
                args92.push(Val::Str("--art-dir".into()));
                kw93.push(("type".into(), e.get("Path")?));
                kw93.push(("default".into(), e.get("ART")?));
                kw93.push(("help".into(), {
                    let mut str95 = String::new();
                    str95.push_str("PNG output directory (default: ");
                    str95.push_str(&format(
                        &{
                            let fun98 = e.get("ART")?.attr("relative_to")?;
                            let mut args96 = Vec::new();
                            let mut kw97 = Vec::new();
                            args96.push(e.get("ROOT")?);
                            fun98.call(args96, kw97)?
                        },
                        &String::new(),
                    )?);
                    str95.push_str(")");
                    Val::Str(str95)
                }));
                fun94.call(args92, kw93)?
            };
            {
                let fun101 = e.get("parser")?.attr("set_defaults")?;
                let mut args99 = Vec::new();
                let mut kw100 = Vec::new();
                kw100.push(("render".into(), Val::Bool(true)));
                fun101.call(args99, kw100)?
            };
            let assigned102 = {
                let fun105 = e.get("parser")?.attr("parse_args")?;
                let mut args103 = Vec::new();
                let mut kw104 = Vec::new();
                fun105.call(args103, kw104)?
            };
            e.set("args", assigned102.clone())?;
            let assigned106 = {
                let fun109 = e.get("args")?.attr("out_dir")?.attr("resolve")?;
                let mut args107 = Vec::new();
                let mut kw108 = Vec::new();
                fun109.call(args107, kw108)?
            };
            e.set("output_dir", assigned106.clone())?;
            {
                let fun112 = e.get("output_dir")?.attr("mkdir")?;
                let mut args110 = Vec::new();
                let mut kw111 = Vec::new();
                kw111.push(("parents".into(), Val::Bool(true)));
                kw111.push(("exist_ok".into(), Val::Bool(true)));
                fun112.call(args110, kw111)?
            };
            let mod113 = rt.import_module("_plumbing_art_mesh")?;
            e.set("export", rt.member("_plumbing_art_mesh", "export")?)?;
            let assigned114 = {
                let fun117 = e.get("export")?;
                let mut args115 = Vec::new();
                let mut kw116 = Vec::new();
                args115.push(e.namespace());
                args115.push(e.get("SCENE_NAMES")?);
                args115.push(e.get("output_dir")?);
                fun117.call(args115, kw116)?
            };
            e.set("step_paths", assigned114.clone())?;
            if e.get("args")?.attr("render")?.truthy()? {
                let assigned118 = {
                    let fun121 = e.get("args")?.attr("art_dir")?.attr("resolve")?;
                    let mut args119 = Vec::new();
                    let mut kw120 = Vec::new();
                    fun121.call(args119, kw120)?
                };
                e.set("art_dir", assigned118.clone())?;
                {
                    let fun124 = e.get("art_dir")?.attr("mkdir")?;
                    let mut args122 = Vec::new();
                    let mut kw123 = Vec::new();
                    kw123.push(("parents".into(), Val::Bool(true)));
                    kw123.push(("exist_ok".into(), Val::Bool(true)));
                    fun124.call(args122, kw123)?
                };
                {
                    let fun127 = e.get("_render")?;
                    let mut args125 = Vec::new();
                    let mut kw126 = Vec::new();
                    args125.push(e.get("step_paths")?);
                    args125.push(e.get("art_dir")?);
                    fun127.call(args125, kw126)?
                };
                for item128 in e.get("SCENE_NAMES")?.iter()? {
                    e.set("name", item128)?;
                    {
                        let fun131 = e.get("print")?;
                        let mut args129 = Vec::new();
                        let mut kw130 = Vec::new();
                        args129.push({
                            let mut str132 = String::new();
                            str132.push_str("rendered -> ");
                            str132.push_str(&format(
                                &binary("truediv", e.get("art_dir")?, {
                                    let mut str133 = String::new();
                                    str133.push_str(&format(&e.get("name")?, &String::new())?);
                                    str133.push_str(".png");
                                    Val::Str(str133)
                                })?,
                                &String::new(),
                            )?);
                            Val::Str(str132)
                        });
                        fun131.call(args129, kw130)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun136 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args134 = Vec::new();
        let mut kw135 = Vec::new();
        args134.push(Val::Int(0i64));
        args134.push({
            let fun139 = e.get("str")?;
            let mut args137 = Vec::new();
            let mut kw138 = Vec::new();
            args137.push(binary(
                "truediv",
                {
                    let fun142 = {
                        let fun145 = e.get("Path")?;
                        let mut args143 = Vec::new();
                        let mut kw144 = Vec::new();
                        args143.push(e.get("__file__")?);
                        fun145.call(args143, kw144)?
                    }
                    .attr("resolve")?;
                    let mut args140 = Vec::new();
                    let mut kw141 = Vec::new();
                    fun142.call(args140, kw141)?
                }
                .attr("parents")?
                .get(Val::Int(2i64))?,
                Val::Str("scripts".into()),
            )?);
            fun139.call(args137, kw138)?
        });
        fun136.call(args134, kw135)?
    };
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun148 = e.get("_rust_part")?.attr("start")?;
        let mut args146 = Vec::new();
        let mut kw147 = Vec::new();
        fun148.call(args146, kw147)?
    };
    {
        let fun151 = e.get("main")?;
        let mut args149 = Vec::new();
        let mut kw150 = Vec::new();
        fun151.call(args149, kw150)?
    };
    Ok(Val::None)
}
