//! The enclosure print field's numeric handoff to its Rust producer.
//!
//! The smooth structural solid remains the enclosure builder's. One print mesh is handed to
//! the field at a time, with the same sampled rails and plain lands as ``flute_skin``.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    e.set("struct", rt.import_module("struct")?)?;
    e.set("tempfile", rt.import_module("tempfile")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("np", rt.import_module("numpy")?)?;
    e.set("trimesh", rt.import_module("trimesh")?)?;
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    e.set("flute_skin", rt.import_module("flute_skin")?)?;
    e.set("reeding", rt.import_module("reeding")?)?;
    // _write_mesh
    e.set("_write_mesh", {
        let params = vec![("path".into(), None, false), ("mesh".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let context2 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                    line!(),
                );
                {
                    let fun5 = e.get("path")?.attr("open")?;
                    let mut args3 = Vec::new();
                    let mut kw4 = Vec::new();
                    args3.push(Val::Str("wb".into()));
                    fun5.call(args3, kw4)?
                }
            };
            e.set("stream", context2.attr("__enter__")?.call(vec![], vec![])?)?;
            let context_result33 = (|| -> Result<Flow> {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                        line!(),
                    );
                    {
                        let fun8 = e.get("stream")?.attr("write")?;
                        let mut args6 = Vec::new();
                        let mut kw7 = Vec::new();
                        args6.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                line!(),
                            );
                            {
                                let fun11 = e.get("struct")?.attr("pack")?;
                                let mut args9 = Vec::new();
                                let mut kw10 = Vec::new();
                                args9.push(Val::Str("<QQ".into()));
                                args9.push({
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                        line!(),
                                    );
                                    {
                                        let fun14 = e.get("len")?;
                                        let mut args12 = Vec::new();
                                        let mut kw13 = Vec::new();
                                        args12.push(e.get("mesh")?.attr("vertices")?);
                                        fun14.call(args12, kw13)?
                                    }
                                });
                                args9.push({
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                        line!(),
                                    );
                                    {
                                        let fun17 = e.get("len")?;
                                        let mut args15 = Vec::new();
                                        let mut kw16 = Vec::new();
                                        args15.push(e.get("mesh")?.attr("faces")?);
                                        fun17.call(args15, kw16)?
                                    }
                                });
                                fun11.call(args9, kw10)?
                            }
                        });
                        fun8.call(args6, kw7)?
                    }
                };
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                        line!(),
                    );
                    {
                        let fun20 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                line!(),
                            );
                            {
                                let fun23 = e.get("np")?.attr("asarray")?;
                                let mut args21 = Vec::new();
                                let mut kw22 = Vec::new();
                                args21.push(e.get("mesh")?.attr("vertices")?);
                                kw22.push(("dtype".into(), Val::Str("<f8".into())));
                                fun23.call(args21, kw22)?
                            }
                        }
                        .attr("tofile")?;
                        let mut args18 = Vec::new();
                        let mut kw19 = Vec::new();
                        args18.push(e.get("stream")?);
                        fun20.call(args18, kw19)?
                    }
                };
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                        line!(),
                    );
                    {
                        let fun26 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                line!(),
                            );
                            {
                                let fun29 = {
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                        line!(),
                                    );
                                    {
                                        let fun32 = e.get("np")?.attr("asarray")?;
                                        let mut args30 = Vec::new();
                                        let mut kw31 = Vec::new();
                                        args30.push(e.get("mesh")?.attr("faces")?);
                                        kw31.push(("dtype".into(), Val::Str("<i8".into())));
                                        fun32.call(args30, kw31)?
                                    }
                                }
                                .attr("view")?;
                                let mut args27 = Vec::new();
                                let mut kw28 = Vec::new();
                                args27.push(Val::Str("<u8".into()));
                                fun29.call(args27, kw28)?
                            }
                        }
                        .attr("tofile")?;
                        let mut args24 = Vec::new();
                        let mut kw25 = Vec::new();
                        args24.push(e.get("stream")?);
                        fun26.call(args24, kw25)?
                    }
                };
                Ok(Flow::Continue)
            })();
            context2
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result33? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
            }
            Ok(Val::None)
        })
    })?;
    // _read_mesh
    e.set("_read_mesh", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let context34 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                    line!(),
                );
                {
                    let fun37 = e.get("path")?.attr("open")?;
                    let mut args35 = Vec::new();
                    let mut kw36 = Vec::new();
                    args35.push(Val::Str("rb".into()));
                    fun37.call(args35, kw36)?
                }
            };
            e.set("stream", context34.attr("__enter__")?.call(vec![], vec![])?)?;
            let context_result78 = (|| -> Result<Flow> {
                let assigned38 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                        line!(),
                    );
                    {
                        let fun41 = e.get("struct")?.attr("unpack")?;
                        let mut args39 = Vec::new();
                        let mut kw40 = Vec::new();
                        args39.push(Val::Str("<QQ".into()));
                        args39.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                line!(),
                            );
                            {
                                let fun44 = e.get("stream")?.attr("read")?;
                                let mut args42 = Vec::new();
                                let mut kw43 = Vec::new();
                                args42.push(Val::Int(16i64));
                                fun44.call(args42, kw43)?
                            }
                        });
                        fun41.call(args39, kw40)?
                    }
                };
                let unpack45 = unpack(assigned38.clone(), 2)?;
                e.set("vertices", unpack45[0].clone())?;
                e.set("triangles", unpack45[1].clone())?;
                let assigned46 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                        line!(),
                    );
                    {
                        let fun49 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                line!(),
                            );
                            {
                                let fun52 = e.get("np")?.attr("fromfile")?;
                                let mut args50 = Vec::new();
                                let mut kw51 = Vec::new();
                                args50.push(e.get("stream")?);
                                kw51.push(("dtype".into(), Val::Str("<f8".into())));
                                kw51.push((
                                    "count".into(),
                                    binary("mul", Val::Int(3i64), e.get("vertices")?)?,
                                ));
                                fun52.call(args50, kw51)?
                            }
                        }
                        .attr("reshape")?;
                        let mut args47 = Vec::new();
                        let mut kw48 = Vec::new();
                        args47.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Int(1i64))?);
                            s.push(Val::Int(3i64));
                            Val::tuple(s)
                        });
                        fun49.call(args47, kw48)?
                    }
                };
                e.set("points", assigned46.clone())?;
                let assigned53 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                        line!(),
                    );
                    {
                        let fun56 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                line!(),
                            );
                            {
                                let fun59 = e.get("np")?.attr("fromfile")?;
                                let mut args57 = Vec::new();
                                let mut kw58 = Vec::new();
                                args57.push(e.get("stream")?);
                                kw58.push(("dtype".into(), Val::Str("<i8".into())));
                                kw58.push((
                                    "count".into(),
                                    binary("mul", Val::Int(3i64), e.get("triangles")?)?,
                                ));
                                fun59.call(args57, kw58)?
                            }
                        }
                        .attr("reshape")?;
                        let mut args54 = Vec::new();
                        let mut kw55 = Vec::new();
                        args54.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Int(1i64))?);
                            s.push(Val::Int(3i64));
                            Val::tuple(s)
                        });
                        fun56.call(args54, kw55)?
                    }
                };
                e.set("faces", assigned53.clone())?;
                if {
                    let v69 = {
                        let v73 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                line!(),
                            );
                            {
                                let fun72 = e.get("len")?;
                                let mut args70 = Vec::new();
                                let mut kw71 = Vec::new();
                                args70.push(e.get("points")?);
                                fun72.call(args70, kw71)?
                            }
                        };
                        let v74 = e.get("vertices")?;
                        Val::Bool(compare("ne", v73.clone(), v74.clone())?.truthy()?)
                    };
                    if v69.truthy()? {
                        v69
                    } else {
                        {
                            let v63 = {
                                let v67 = {
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                        line!(),
                                    );
                                    {
                                        let fun66 = e.get("len")?;
                                        let mut args64 = Vec::new();
                                        let mut kw65 = Vec::new();
                                        args64.push(e.get("faces")?);
                                        fun66.call(args64, kw65)?
                                    }
                                };
                                let v68 = e.get("triangles")?;
                                Val::Bool(compare("ne", v67.clone(), v68.clone())?.truthy()?)
                            };
                            if v63.truthy()? {
                                v63
                            } else {
                                {
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                        line!(),
                                    );
                                    {
                                        let fun62 = e.get("stream")?.attr("read")?;
                                        let mut args60 = Vec::new();
                                        let mut kw61 = Vec::new();
                                        args60.push(Val::Int(1i64));
                                        fun62.call(args60, kw61)?
                                    }
                                }
                            }
                        }
                    }
                }
                .truthy()?
                {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                line!(),
                            );
                            {
                                let fun77 = e.get("ValueError")?;
                                let mut args75 = Vec::new();
                                let mut kw76 = Vec::new();
                                args75.push(Val::Str(
                                    "enclosure-skin did not write the mesh arrays it named".into(),
                                ));
                                fun77.call(args75, kw76)?
                            }
                        })?
                    );
                }
                Ok(Flow::Continue)
            })();
            context34
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result78? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                    line!(),
                );
                {
                    let fun81 = e.get("trimesh")?.attr("Trimesh")?;
                    let mut args79 = Vec::new();
                    let mut kw80 = Vec::new();
                    kw80.push(("vertices".into(), e.get("points")?));
                    kw80.push(("faces".into(), e.get("faces")?));
                    kw80.push(("process".into(), Val::Bool(false)));
                    fun81.call(args79, kw80)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // field_numbers
    e.set("field_numbers", {
        let params = vec![
            ("rails".into(), None, false),
            ("pitch".into(), None, false),
            ("depth".into(), None, false),
            ("rise".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned82 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("frames", assigned82.clone())?;
            for item83 in e.get("rails")?.iter()? {
                e.set("rail", item83)?;
                if e.get("rail")?.attr("berthed")?.truthy()? {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                line!(),
                            );
                            {
                                let fun86 = e.get("ValueError")?;
                                let mut args84 = Vec::new();
                                let mut kw85 = Vec::new();
                                args84.push(Val::Str(
                                    "the enclosure's exterior print rail has no berthed bodies"
                                        .into(),
                                ));
                                fun86.call(args84, kw85)?
                            }
                        })?
                    );
                }
                let assigned87 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                        line!(),
                    );
                    {
                        let fun90 = e.get("flute_skin")?.attr("_rail_frames")?;
                        let mut args88 = Vec::new();
                        let mut kw89 = Vec::new();
                        args88.push(e.get("rail")?);
                        fun90.call(args88, kw89)?
                    }
                };
                let unpack91 = unpack(assigned87.clone(), 3)?;
                e.set("s", unpack91[0].clone())?;
                e.set("point", unpack91[1].clone())?;
                e.set("normal", unpack91[2].clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                        line!(),
                    );
                    {
                        let fun94 = e.get("frames")?.attr("append")?;
                        let mut args92 = Vec::new();
                        let mut kw93 = Vec::new();
                        args92.push({
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("s".into()), {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                    line!(),
                                );
                                {
                                    let fun97 = e.get("s")?.attr("tolist")?;
                                    let mut args95 = Vec::new();
                                    let mut kw96 = Vec::new();
                                    fun97.call(args95, kw96)?
                                }
                            })?;
                            d.set(Val::Str("point".into()), {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                    line!(),
                                );
                                {
                                    let fun100 = e.get("point")?.attr("tolist")?;
                                    let mut args98 = Vec::new();
                                    let mut kw99 = Vec::new();
                                    fun100.call(args98, kw99)?
                                }
                            })?;
                            d.set(Val::Str("normal".into()), {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                                    line!(),
                                );
                                {
                                    let fun103 = e.get("normal")?.attr("tolist")?;
                                    let mut args101 = Vec::new();
                                    let mut kw102 = Vec::new();
                                    fun103.call(args101, kw102)?
                                }
                            })?;
                            d.set(Val::Str("closed".into()), e.get("rail")?.attr("closed")?)?;
                            d.set(Val::Str("band".into()), e.get("rail")?.attr("band")?)?;
                            d.set(Val::Str("plain".into()), e.get("rail")?.attr("plain")?)?;
                            d
                        });
                        fun94.call(args92, kw93)?
                    }
                };
            }
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("field".into()), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("across".into()),
                        e.get("flute_skin")?.attr("grid_across")?,
                    )?;
                    d.set(
                        Val::Str("along".into()),
                        e.get("flute_skin")?.attr("grid_along")?,
                    )?;
                    d.set(
                        Val::Str("margin".into()),
                        e.get("flute_skin")?.attr("cut_margin")?,
                    )?;
                    d.set(
                        Val::Str("overrun".into()),
                        e.get("flute_skin")?.attr("cut_overrun")?,
                    )?;
                    d.set(
                        Val::Str("plan_tol".into()),
                        e.get("flute_skin")?.attr("plan_tol")?,
                    )?;
                    d.set(
                        Val::Str("face_tol".into()),
                        e.get("flute_skin")?.attr("face_tol")?,
                    )?;
                    d.set(Val::Str("pitch".into()), e.get("pitch")?)?;
                    d.set(
                        Val::Str("width".into()),
                        e.get("reeding")?.attr("flute_width")?,
                    )?;
                    d.set(Val::Str("depth".into()), e.get("depth")?)?;
                    d.set(Val::Str("rise".into()), e.get("rise")?)?;
                    d
                })?;
                d.set(Val::Str("rails".into()), e.get("frames")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // numbers
    e.set("numbers", {
        let params = vec![
            ("mesh_path".into(), None, false),
            ("rails".into(), None, false),
            ("pitch".into(), None, false),
            ("depth".into(), None, false),
            ("rise".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                    line!(),
                );
                {
                    let fun106 = e.get("dict")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    args104.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                            line!(),
                        );
                        {
                            let fun109 = e.get("field_numbers")?;
                            let mut args107 = Vec::new();
                            let mut kw108 = Vec::new();
                            args107.push(e.get("rails")?);
                            args107.push(e.get("pitch")?);
                            args107.push(e.get("depth")?);
                            args107.push(e.get("rise")?);
                            fun109.call(args107, kw108)?
                        }
                    });
                    kw105.push(("mesh".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",
                            line!(),
                        );
                        {
                            let fun112 = e.get("str")?;
                            let mut args110 = Vec::new();
                            let mut kw111 = Vec::new();
                            args110.push(e.get("mesh_path")?);
                            fun112.call(args110, kw111)?
                        }
                    }));
                    fun106.call(args104, kw105)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // flute
    e.set("flute",{let params=vec![("mesh".into(),None,false),("rails".into(),None,false),("pitch".into(),None,false),("depth".into(),None,false),("rise".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if unary("not",e.get("rails")?)?.truthy()? {
return Ok(e.get("mesh")?);
}
let context113={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",line!());{let fun116=e.get("tempfile")?.attr("TemporaryDirectory")?;let mut args114=Vec::new();let mut kw115=Vec::new();kw115.push(("prefix".into(),Val::Str("hsm-enclosure-skin-".into())));fun116.call(args114,kw115)?}};e.set("directory",context113.attr("__enter__")?.call(vec![],vec![])?)?;let context_result141=(||->Result<Flow>{let assigned117={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",line!());{let fun120=e.get("Path")?;let mut args118=Vec::new();let mut kw119=Vec::new();args118.push(e.get("directory")?);fun120.call(args118,kw119)?}};e.set("directory",assigned117.clone())?;
let assigned121=binary("truediv",e.get("directory")?,Val::Str("smooth.bin".into()))?;e.set("mesh_path",assigned121.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",line!());{let fun124=e.get("_write_mesh")?;let mut args122=Vec::new();let mut kw123=Vec::new();args122.push(e.get("mesh_path")?);args122.push(e.get("mesh")?);fun124.call(args122,kw123)?}};
let assigned125=binary("truediv",e.get("directory")?,Val::Str("enclosure-skin.numbers.json".into()))?;e.set("description",assigned125.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",line!());{let fun128=e.get("description")?.attr("write_text")?;let mut args126=Vec::new();let mut kw127=Vec::new();args126.push(binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",line!());{let fun131=e.get("json")?.attr("dumps")?;let mut args129=Vec::new();let mut kw130=Vec::new();args129.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",line!());{let fun134=e.get("numbers")?;let mut args132=Vec::new();let mut kw133=Vec::new();args132.push(e.get("mesh_path")?);args132.push(e.get("rails")?);args132.push(e.get("pitch")?);args132.push(e.get("depth")?);args132.push(e.get("rise")?);fun134.call(args132,kw133)?}});kw130.push(("separators".into(),{let mut s=Vec::new();s.push(Val::Str(",".into()));s.push(Val::Str(":".into()));Val::tuple(s)}));fun131.call(args129,kw130)?}},Val::Str("\n".into()))?);fun128.call(args126,kw127)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",line!());{let fun137=e.get("_rust_part")?.attr("run")?;let mut args135=Vec::new();let mut kw136=Vec::new();args135.push(Val::Str("enclosure-shell".into()));args135.push(Val::Str("enclosure-skin".into()));args135.push(e.get("description")?);args135.push(e.get("directory")?);fun137.call(args135,kw136)?}};
return Ok(Flow::Return({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_skin.rs",line!());{let fun140=e.get("_read_mesh")?;let mut args138=Vec::new();let mut kw139=Vec::new();args138.push(binary("truediv",e.get("directory")?,Val::Str("enclosure-skin.bin".into()))?);fun140.call(args138,kw139)?}}));
Ok(Flow::Continue)})();context113.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result141? {Flow::Continue=>{},Flow::Return(value)=>return Ok(value)}
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
