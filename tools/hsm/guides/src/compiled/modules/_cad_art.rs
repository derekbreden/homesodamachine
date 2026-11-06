//! Guide recipe: `hardware/install-guide/_cad_art.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    rt.import_module("importlib.util")?;
    e.set("importlib", rt.import_module("importlib")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("os", rt.import_module("os")?)?;
    e.set("shutil", rt.import_module("shutil")?)?;
    e.set("subprocess", rt.import_module("subprocess")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("tempfile", rt.import_module("tempfile")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod2 = rt.import_module("PIL")?;
    e.set("Image", rt.member("PIL", "Image")?)?;
    let assigned3 = {
        let fun6 = {
            let fun9 = e.get("Path")?;
            let mut args7 = Vec::new();
            let mut kw8 = Vec::new();
            args7.push(e.get("__file__")?);
            fun9.call(args7, kw8)?
        }
        .attr("resolve")?;
        let mut args4 = Vec::new();
        let mut kw5 = Vec::new();
        fun6.call(args4, kw5)?
    }
    .attr("parent")?;
    e.set("HERE", assigned3.clone())?;
    let assigned10 = {
        let fun13 = e.get("next")?;
        let mut args11 = Vec::new();
        let mut kw12 = Vec::new();
        args11.push({
            let e = e.child();
            let out14 = Val::list(vec![]);
            for item15 in e.get("HERE")?.attr("parents")?.iter()? {
                e.set("p", item15)?;
                if {
                    let v16 = e.get("p")?.attr("name")?;
                    let v17 = Val::Str("hardware".into());
                    Val::Bool(compare("eq", v16.clone(), v17.clone())?.truthy()?)
                }
                .truthy()?
                {
                    out14.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out14
        });
        fun13.call(args11, kw12)?
    };
    e.set("HARDWARE", assigned10.clone())?;
    let assigned18 = e.get("HARDWARE")?.attr("parent")?;
    e.set("ROOT", assigned18.clone())?;
    let assigned19 = binary("truediv", e.get("HERE")?, Val::Str("art".into()))?;
    e.set("ART", assigned19.clone())?;
    let assigned20 = binary("truediv", e.get("HERE")?, Val::Str("out".into()))?;
    e.set("OUT", assigned20.clone())?;
    let assigned21 = binary(
        "truediv",
        binary(
            "truediv",
            e.get("HARDWARE")?,
            Val::Str("faucet-layout".into()),
        )?,
        Val::Str("faucet_assembly.py".into()),
    )?;
    e.set("FAUCET_SOURCE", assigned21.clone())?;
    let assigned22 = binary(
        "truediv",
        binary(
            "truediv",
            e.get("HARDWARE")?,
            Val::Str("manifold-layout".into()),
        )?,
        Val::Str("enclosure-assembly.step".into()),
    )?;
    e.set("MACHINE_STEP", assigned22.clone())?;
    let assigned23 = binary(
        "truediv",
        binary(
            "truediv",
            e.get("HARDWARE")?,
            Val::Str("manifold-layout".into()),
        )?,
        Val::Str("enclosure-assembly.step.mesh".into()),
    )?;
    e.set("MACHINE_MESH", assigned23.clone())?;
    let assigned24 = binary(
        "truediv",
        binary(
            "truediv",
            e.get("HARDWARE")?,
            Val::Str("manifold-layout".into()),
        )?,
        Val::Str("enclosure-assembly.facts.json".into()),
    )?;
    e.set("MACHINE_FACTS", assigned24.clone())?;
    let assigned25 = binary(
        "truediv",
        binary(
            "truediv",
            binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("printed-parts".into()),
            )?,
            Val::Str("faucet".into()),
        )?,
        Val::Str("tube-collar".into()),
    )?;
    e.set("TUBE_COLLAR_DIR", assigned25.clone())?;
    let assigned26 = {
        let mut s = Vec::new();
        s.push(Val::Float(1.0f64));
        s.push(unary("neg", Val::Float(1.45f64))?);
        s.push(unary("neg", Val::Float(0.38f64))?);
        Val::tuple(s)
    };
    e.set("MOUNT_CAM", assigned26.clone())?;
    let assigned27 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.0f64));
        s.push(Val::Float(0.0f64));
        s.push(Val::Float(110.0f64));
        Val::tuple(s)
    };
    e.set("MOUNT_TARGET", assigned27.clone())?;
    let assigned28 = Val::Int(18i64);
    e.set("MOUNT_FRAME_SHAVE", assigned28.clone())?;
    let assigned29 = Val::Int(200i64);
    e.set("MOUNT_FRAME_TRIM_TOP", assigned29.clone())?;
    let assigned30 = Val::Int(120i64);
    e.set("MOUNT_DROP_TRIM_TOP", assigned30.clone())?;
    let assigned31 = Val::Int(40i64);
    e.set("MOUNT_FRAME_TRIM_BOTTOM", assigned31.clone())?;
    let assigned32 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.58f64));
        s.push(unary("neg", Val::Float(1.6f64))?);
        s.push(unary("neg", Val::Float(0.72f64))?);
        Val::tuple(s)
    };
    e.set("UNDER_MOUNT_CAM", assigned32.clone())?;
    let assigned33 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.0f64));
        s.push(Val::Float(0.0f64));
        s.push(unary("neg", Val::Float(34.0f64))?);
        Val::tuple(s)
    };
    e.set("UNDER_MOUNT_TARGET", assigned33.clone())?;
    let assigned34 = Val::Int(18i64);
    e.set("UNDER_MOUNT_FRAME_SHAVE", assigned34.clone())?;
    let assigned35 = unary("neg", Val::Float(72.0f64))?;
    e.set("PLATE_APPROACH_X", assigned35.clone())?;
    let assigned36 = Val::Float(220.0f64);
    e.set("UNDER_COUNTERTOP_X", assigned36.clone())?;
    let assigned37 = Val::Float(72.0f64);
    e.set("UNDER_COUNTERTOP_Y", assigned37.clone())?;
    let assigned38 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.7f64));
        s.push(Val::Float(1.0f64));
        s.push(Val::Float(0.16f64));
        Val::tuple(s)
    };
    e.set("CONNECT_CAM", assigned38.clone())?;
    let assigned39 = {
        let mut s = Vec::new();
        s.push(Val::Float(44.0f64));
        s.push(Val::Float(630.0f64));
        s.push(Val::Float(370.0f64));
        Val::tuple(s)
    };
    e.set("CONNECT_TARGET", assigned39.clone())?;
    let assigned40 = Val::Float(180.0f64);
    e.set("CONNECT_ORTHO_SPAN", assigned40.clone())?;
    let assigned41 = Val::Str("1600x1800".into());
    e.set("CONNECT_RENDER_SIZE", assigned41.clone())?;
    let assigned42 = Val::Float(160.0f64);
    e.set("CONNECT_OPEN_GAP", assigned42.clone())?;
    let assigned43 = {
        let mut s = Vec::new();
        s.push(Val::Int(0i64));
        s.push(Val::Int(650i64));
        s.push(Val::Int(1350i64));
        s.push(Val::Int(1800i64));
        Val::tuple(s)
    };
    e.set("CONNECT_CROP", assigned43.clone())?;
    {
        let fun46 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args44 = Vec::new();
        let mut kw45 = Vec::new();
        args44.push(Val::Int(0i64));
        args44.push({
            let fun49 = e.get("str")?;
            let mut args47 = Vec::new();
            let mut kw48 = Vec::new();
            args47.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("scripts".into()),
            )?);
            fun49.call(args47, kw48)?
        });
        fun46.call(args44, kw45)?
    };
    {
        let fun52 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args50 = Vec::new();
        let mut kw51 = Vec::new();
        args50.push(Val::Int(0i64));
        args50.push({
            let fun55 = e.get("str")?;
            let mut args53 = Vec::new();
            let mut kw54 = Vec::new();
            args53.push(binary(
                "truediv",
                binary(
                    "truediv",
                    binary(
                        "truediv",
                        e.get("HARDWARE")?,
                        Val::Str("printed-parts".into()),
                    )?,
                    Val::Str("enclosure".into()),
                )?,
                Val::Str("y-wall-of-back-top".into()),
            )?);
            fun55.call(args53, kw54)?
        });
        fun52.call(args50, kw51)?
    };
    let mod56 = rt.import_module("_cadq_export")?;
    e.set(
        "_per_solid_color",
        rt.member("_cadq_export", "_per_solid_color")?,
    )?;
    e.set(
        "_write_mesh_payload",
        rt.member("_cadq_export", "_write_mesh_payload")?,
    )?;
    e.set("note_read", rt.member("_cadq_export", "note_read")?)?;
    e.set("note_write", rt.member("_cadq_export", "note_write")?)?;
    e.set("_hsm_render", rt.import_module("_hsm_render")?)?;
    e.set("_materials", rt.import_module("_materials")?)?;
    // _load_faucet_module
    e.set("_load_faucet_module", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun59 = e.get("note_read")?;
                let mut args57 = Vec::new();
                let mut kw58 = Vec::new();
                args57.push(e.get("FAUCET_SOURCE")?);
                fun59.call(args57, kw58)?
            };
            let assigned60 = {
                let fun63 = e
                    .get("importlib")?
                    .attr("util")?
                    .attr("spec_from_file_location")?;
                let mut args61 = Vec::new();
                let mut kw62 = Vec::new();
                args61.push(Val::Str("installation_faucet".into()));
                args61.push(e.get("FAUCET_SOURCE")?);
                fun63.call(args61, kw62)?
            };
            e.set("spec", assigned60.clone())?;
            if {
                let v66 = {
                    let v67 = e.get("spec")?;
                    let v68 = Val::None;
                    Val::Bool(compare("is", v67.clone(), v68.clone())?.truthy()?)
                };
                if v66.truthy()? {
                    v66
                } else {
                    {
                        let v64 = e.get("spec")?.attr("loader")?;
                        let v65 = Val::None;
                        Val::Bool(compare("is", v64.clone(), v65.clone())?.truthy()?)
                    }
                }
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun71 = e.get("RuntimeError")?;
                        let mut args69 = Vec::new();
                        let mut kw70 = Vec::new();
                        args69.push({
                            let mut str72 = String::new();
                            str72.push_str("cannot import ");
                            str72.push_str(&format(&e.get("FAUCET_SOURCE")?, &String::new())?);
                            Val::Str(str72)
                        });
                        fun71.call(args69, kw70)?
                    })?
                );
            }
            let assigned73 = {
                let fun76 = e.get("importlib")?.attr("util")?.attr("module_from_spec")?;
                let mut args74 = Vec::new();
                let mut kw75 = Vec::new();
                args74.push(e.get("spec")?);
                fun76.call(args74, kw75)?
            };
            e.set("module", assigned73.clone())?;
            {
                let fun79 = e.get("spec")?.attr("loader")?.attr("exec_module")?;
                let mut args77 = Vec::new();
                let mut kw78 = Vec::new();
                args77.push(e.get("module")?);
                fun79.call(args77, kw78)?
            };
            return Ok(e.get("module")?);
            Ok(Val::None)
        })
    })?;
    // machine_bodies
    e.set("machine_bodies", {
        let params = vec![(
            "keep".into(),
            Some({
                let params = vec![("name".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok(Val::Bool(true));
                    Ok(Val::None)
                })
            }),
            false,
        )];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("flute_payload", rt.import_module("flute_payload")?)?;
            return Ok({
                let e = e.child();
                let out80 = Val::list(vec![]);
                for item81 in {
                    let v82 = {
                        let fun85 = e.get("flute_payload")?.attr("read_payload")?;
                        let mut args83 = Vec::new();
                        let mut kw84 = Vec::new();
                        args83.push(e.get("MACHINE_MESH")?);
                        fun85.call(args83, kw84)?
                    };
                    if v82.truthy()? {
                        v82
                    } else {
                        {
                            let mut s = Vec::new();
                            Val::list(s)
                        }
                    }
                }
                .iter()?
                {
                    e.set("entry", item81)?;
                    if {
                        let fun88 = e.get("keep")?;
                        let mut args86 = Vec::new();
                        let mut kw87 = Vec::new();
                        args86.push(
                            {
                                let fun91 = e
                                    .get("entry")?
                                    .get(Val::Str("name".into()))?
                                    .attr("split")?;
                                let mut args89 = Vec::new();
                                let mut kw90 = Vec::new();
                                args89.push(Val::Str("/".into()));
                                fun91.call(args89, kw90)?
                            }
                            .get(Val::Int(0i64))?,
                        );
                        fun88.call(args86, kw87)?
                    }
                    .truthy()?
                    {
                        out80.attr("append")?.call(vec![e.get("entry")?], vec![])?;
                    }
                }
                out80
            });
            Ok(Val::None)
        })
    })?;
    // borrow
    e.set("borrow", {
        let params = vec![
            ("assembly".into(), None, false),
            ("bodies".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned92 = {
                let mut s = Vec::new();
                s.extend(
                    {
                        let fun95 = e.get("getattr")?;
                        let mut args93 = Vec::new();
                        let mut kw94 = Vec::new();
                        args93.push(e.get("assembly")?);
                        args93.push(Val::Str("machine".into()));
                        args93.push({
                            let mut s = Vec::new();
                            Val::tuple(s)
                        });
                        fun95.call(args93, kw94)?
                    }
                    .iter()?,
                );
                s.extend(e.get("bodies")?.iter()?);
                Val::list(s)
            };
            e.get("assembly")?.setattr("machine", assigned92.clone())?;
            return Ok(e.get("assembly")?);
            Ok(Val::None)
        })
    })?;
    // _export_colored
    e.set("_export_colored", {
        let params = vec![
            ("assembly".into(), None, false),
            ("target".into(), None, false),
            ("mesh".into(), Some(Val::Bool(false)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned96 = {
                let fun99 = e.get("getattr")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                args97.push(e.get("assembly")?);
                args97.push(Val::Str("machine".into()));
                args97.push({
                    let mut s = Vec::new();
                    Val::tuple(s)
                });
                fun99.call(args97, kw98)?
            };
            e.set("machine", assigned96.clone())?;
            let assigned100 = if e.get("assembly")?.attr("children")?.truthy()? {
                {
                    let fun103 = e.get("_per_solid_color")?;
                    let mut args101 = Vec::new();
                    let mut kw102 = Vec::new();
                    args101.push(e.get("assembly")?);
                    fun103.call(args101, kw102)?
                }
            } else {
                Val::None
            };
            e.set("colored", assigned100.clone())?;
            if unary("not", e.get("machine")?)?.truthy()? {
                {
                    let fun106 = e.get("colored")?.attr("export")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    args104.push({
                        let fun109 = e.get("str")?;
                        let mut args107 = Vec::new();
                        let mut kw108 = Vec::new();
                        args107.push(e.get("target")?);
                        fun109.call(args107, kw108)?
                    });
                    fun106.call(args104, kw105)?
                };
                if e.get("mesh")?.truthy()? {
                    {
                        let fun112 = e.get("_write_mesh_payload")?;
                        let mut args110 = Vec::new();
                        let mut kw111 = Vec::new();
                        args110.push(e.get("target")?);
                        args110.push(e.get("colored")?);
                        fun112.call(args110, kw111)?
                    };
                }
                return Ok(e.get("target")?);
            }
            e.set("_mesh_payload", rt.import_module("_mesh_payload")?)?;
            e.set("np", rt.import_module("numpy")?)?;
            let mod113 = rt.import_module("meshcad")?;
            e.set("mesh_write", rt.member("meshcad", "write")?)?;
            let assigned114 = {
                let mut s = Vec::new();
                s.extend(
                    if {
                        let v115 = e.get("colored")?;
                        let v116 = Val::None;
                        Val::Bool(compare("is_not", v115.clone(), v116.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun119 = e.get("_mesh_payload")?.attr("from_assembly")?;
                            let mut args117 = Vec::new();
                            let mut kw118 = Vec::new();
                            args117.push(e.get("colored")?);
                            fun119.call(args117, kw118)?
                        }
                    } else {
                        {
                            let mut s = Vec::new();
                            Val::tuple(s)
                        }
                    }
                    .iter()?,
                );
                s.extend(e.get("machine")?.iter()?);
                Val::list(s)
            };
            e.set("meshes", assigned114.clone())?;
            {
                let fun122 = e.get("mesh_write")?.attr("write_step")?;
                let mut args120 = Vec::new();
                let mut kw121 = Vec::new();
                args120.push({
                    let e = e.child();
                    let out123 = Val::list(vec![]);
                    for item124 in e.get("meshes")?.iter()? {
                        e.set("m", item124)?;
                        out123.attr("append")?.call(
                            vec![{
                                let mut s = Vec::new();
                                s.push(e.get("m")?.get(Val::Str("name".into()))?);
                                s.push({
                                    let mut s = Vec::new();
                                    s.push({
                                        let fun127 = {
                                            let fun130 = e.get("np")?.attr("asarray")?;
                                            let mut args128 = Vec::new();
                                            let mut kw129 = Vec::new();
                                            args128.push(e.get("m")?.get(Val::Str("pos".into()))?);
                                            args128.push(e.get("float")?);
                                            fun130.call(args128, kw129)?
                                        }
                                        .attr("reshape")?;
                                        let mut args125 = Vec::new();
                                        let mut kw126 = Vec::new();
                                        args125.push(unary("neg", Val::Int(1i64))?);
                                        args125.push(Val::Int(3i64));
                                        fun127.call(args125, kw126)?
                                    });
                                    s.push({
                                        let fun133 = {
                                            let fun136 = e.get("np")?.attr("asarray")?;
                                            let mut args134 = Vec::new();
                                            let mut kw135 = Vec::new();
                                            args134.push(e.get("m")?.get(Val::Str("idx".into()))?);
                                            args134.push(e.get("np")?.attr("int64")?);
                                            fun136.call(args134, kw135)?
                                        }
                                        .attr("reshape")?;
                                        let mut args131 = Vec::new();
                                        let mut kw132 = Vec::new();
                                        args131.push(unary("neg", Val::Int(1i64))?);
                                        args131.push(Val::Int(3i64));
                                        fun133.call(args131, kw132)?
                                    });
                                    Val::tuple(s)
                                });
                                s.push(e.get("m")?.get(Val::Str("color".into()))?);
                                Val::tuple(s)
                            }],
                            vec![],
                        )?;
                    }
                    out123
                });
                args120.push(e.get("target")?);
                kw121.push(("root_name".into(), e.get("assembly")?.attr("name")?));
                fun122.call(args120, kw121)?
            };
            {
                let fun139 = e.get("_mesh_payload")?.attr("write")?;
                let mut args137 = Vec::new();
                let mut kw138 = Vec::new();
                args137.push(e.get("meshes")?);
                args137.push(binary(
                    "add",
                    {
                        let fun142 = e.get("str")?;
                        let mut args140 = Vec::new();
                        let mut kw141 = Vec::new();
                        args140.push(e.get("target")?);
                        fun142.call(args140, kw141)?
                    },
                    Val::Str(".mesh".into()),
                )?);
                kw138.push(("src".into(), {
                    let fun145 = e.get("_mesh_payload")?.attr("source_digest")?;
                    let mut args143 = Vec::new();
                    let mut kw144 = Vec::new();
                    args143.push(e.get("target")?);
                    fun145.call(args143, kw144)?
                }));
                fun139.call(args137, kw138)?
            };
            return Ok(e.get("target")?);
            Ok(Val::None)
        })
    })?;
    // _clip_z
    e.set("_clip_z", {
        let params = vec![
            ("obj".into(), None, false),
            ("z_min".into(), None, false),
            ("z_max".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned146 = {
                let fun149 = {
                    let fun152 = {
                        let fun155 = e.get("cq")?.attr("Workplane")?;
                        let mut args153 = Vec::new();
                        let mut kw154 = Vec::new();
                        args153.push(Val::Str("XY".into()));
                        fun155.call(args153, kw154)?
                    }
                    .attr("workplane")?;
                    let mut args150 = Vec::new();
                    let mut kw151 = Vec::new();
                    kw151.push(("offset".into(), e.get("z_min")?));
                    fun152.call(args150, kw151)?
                }
                .attr("box")?;
                let mut args147 = Vec::new();
                let mut kw148 = Vec::new();
                args147.push(Val::Float(600.0f64));
                args147.push(Val::Float(600.0f64));
                args147.push(binary("sub", e.get("z_max")?, e.get("z_min")?)?);
                kw148.push(("centered".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Bool(true));
                    s.push(Val::Bool(true));
                    s.push(Val::Bool(false));
                    Val::tuple(s)
                }));
                fun149.call(args147, kw148)?
            };
            e.set("clip", assigned146.clone())?;
            if unary("not", {
                let fun158 = e.get("hasattr")?;
                let mut args156 = Vec::new();
                let mut kw157 = Vec::new();
                args156.push(e.get("obj")?);
                args156.push(Val::Str("intersect".into()));
                fun158.call(args156, kw157)?
            })?
            .truthy()?
            {
                let assigned159 = {
                    let fun162 = {
                        let fun165 = e.get("cq")?.attr("Workplane")?;
                        let mut args163 = Vec::new();
                        let mut kw164 = Vec::new();
                        args163.push(Val::Str("XY".into()));
                        fun165.call(args163, kw164)?
                    }
                    .attr("newObject")?;
                    let mut args160 = Vec::new();
                    let mut kw161 = Vec::new();
                    args160.push({
                        let mut s = Vec::new();
                        s.push(e.get("obj")?);
                        Val::list(s)
                    });
                    fun162.call(args160, kw161)?
                };
                e.set("obj", assigned159.clone())?;
            }
            return Ok({
                let fun168 = e.get("obj")?.attr("intersect")?;
                let mut args166 = Vec::new();
                let mut kw167 = Vec::new();
                args166.push(e.get("clip")?);
                fun168.call(args166, kw167)?
            });
            Ok(Val::None)
        })
    })?;
    // _moved
    e.set("_moved", {
        let params = vec![("obj".into(), None, false), ("xyz".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let fun171 = e.get("hasattr")?;
                let mut args169 = Vec::new();
                let mut kw170 = Vec::new();
                args169.push(e.get("obj")?);
                args169.push(Val::Str("translate".into()));
                fun171.call(args169, kw170)?
            }
            .truthy()?
            {
                return Ok({
                    let fun174 = e.get("obj")?.attr("translate")?;
                    let mut args172 = Vec::new();
                    let mut kw173 = Vec::new();
                    args172.push(e.get("xyz")?);
                    fun174.call(args172, kw173)?
                });
            }
            return Ok({
                let fun177 = e.get("obj")?.attr("moved")?;
                let mut args175 = Vec::new();
                let mut kw176 = Vec::new();
                args175.push({
                    let fun180 = e.get("cq")?.attr("Location")?;
                    let mut args178 = Vec::new();
                    let mut kw179 = Vec::new();
                    args178.push({
                        let fun183 = e.get("cq")?.attr("Vector")?;
                        let mut args181 = Vec::new();
                        let mut kw182 = Vec::new();
                        args181.extend(e.get("xyz")?.iter()?);
                        fun183.call(args181, kw182)?
                    });
                    fun180.call(args178, kw179)?
                });
                fun177.call(args175, kw176)?
            });
            Ok(Val::None)
        })
    })?;
    // _children_by_name
    e.set("_children_by_name", {
        let params = vec![("assembly".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out184 = Val::dict(vec![]);
                for item185 in e.get("assembly")?.attr("children")?.iter()? {
                    e.set("child", item185)?;
                    out184.set(e.get("child")?.attr("name")?, e.get("child")?)?;
                }
                out184
            });
            Ok(Val::None)
        })
    })?;
    // _add_child
    e.set("_add_child", {
        let params = vec![
            ("out".into(), None, false),
            ("child".into(), None, false),
            ("name".into(), Some(Val::None), true),
            ("obj".into(), Some(Val::None), true),
            ("color".into(), Some(Val::None), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun188 = e.get("out")?.attr("add")?;
                let mut args186 = Vec::new();
                let mut kw187 = Vec::new();
                args186.push(
                    if {
                        let v189 = e.get("obj")?;
                        let v190 = Val::None;
                        Val::Bool(compare("is", v189.clone(), v190.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.get("child")?.attr("obj")?
                    } else {
                        e.get("obj")?
                    },
                );
                kw187.push(("name".into(), {
                    let v191 = e.get("name")?;
                    if v191.truthy()? {
                        v191
                    } else {
                        e.get("child")?.attr("name")?
                    }
                }));
                kw187.push((
                    "color".into(),
                    if {
                        let v192 = e.get("color")?;
                        let v193 = Val::None;
                        Val::Bool(compare("is", v192.clone(), v193.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.get("child")?.attr("color")?
                    } else {
                        e.get("color")?
                    },
                ));
                fun188.call(args186, kw187)?
            };
            Ok(Val::None)
        })
    })?;
    // _physical_levers
    e.set("_physical_levers", {
        let params = vec![("fa".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned194 = {
                let fun197 = {
                    let fun200 = {
                        let fun203 = {
                            let fun206 = {
                                let fun209 = {
                                    let fun212 = e.get("fa")?.attr("WorldWorkplane")?;
                                    let mut args210 = Vec::new();
                                    let mut kw211 = Vec::new();
                                    args210.push(e.get("fa")?.attr("xy_plane_z_up")?);
                                    fun212.call(args210, kw211)?
                                }
                                .attr("workplane")?;
                                let mut args207 = Vec::new();
                                let mut kw208 = Vec::new();
                                kw208.push((
                                    "offset".into(),
                                    binary("add", e.get("fa")?.attr("plateau_z")?, Val::Int(1i64))?,
                                ));
                                fun209.call(args207, kw208)?
                            }
                            .attr("moveTo")?;
                            let mut args204 = Vec::new();
                            let mut kw205 = Vec::new();
                            args204.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(unary(
                                    "pos",
                                    binary(
                                        "add",
                                        e.get("fa")?.attr("port_center_depth")?,
                                        Val::Float(0.125f64),
                                    )?,
                                )?);
                                Val::tuple(s)
                            });
                            fun206.call(args204, kw205)?
                        }
                        .attr("circle")?;
                        let mut args201 = Vec::new();
                        let mut kw202 = Vec::new();
                        args201.push(binary(
                            "add",
                            e.get("fa")?.attr("soda_faucet_tube_r")?,
                            Val::Int(1i64),
                        )?);
                        fun203.call(args201, kw202)?
                    }
                    .attr("extrude")?;
                    let mut args198 = Vec::new();
                    let mut kw199 = Vec::new();
                    args198.push(Val::Int(50i64));
                    fun200.call(args198, kw199)?
                }
                .attr("unwrap")?;
                let mut args195 = Vec::new();
                let mut kw196 = Vec::new();
                fun197.call(args195, kw196)?
            };
            e.set("cut_cylinder", assigned194.clone())?;
            let assigned213 = {
                let fun216 = e.get("cq")?.attr("Plane")?;
                let mut args214 = Vec::new();
                let mut kw215 = Vec::new();
                kw215.push(("origin".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }));
                kw215.push(("xDir".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Int(1i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }));
                kw215.push(("normal".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(unary("neg", Val::Int(1i64))?);
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }));
                fun216.call(args214, kw215)?
            };
            e.set("taper_plane", assigned213.clone())?;
            let assigned217 = {
                let fun220 = {
                    let fun223 = {
                        let fun226 = {
                            let fun229 = {
                                let fun232 = {
                                    let fun235 = {
                                        let fun238 = {
                                            let fun241 = e.get("cq")?.attr("Workplane")?;
                                            let mut args239 = Vec::new();
                                            let mut kw240 = Vec::new();
                                            args239.push(e.get("taper_plane")?);
                                            fun241.call(args239, kw240)?
                                        }
                                        .attr("workplane")?;
                                        let mut args236 = Vec::new();
                                        let mut kw237 = Vec::new();
                                        kw237.push(("offset".into(), Val::Int(6i64)));
                                        fun238.call(args236, kw237)?
                                    }
                                    .attr("moveTo")?;
                                    let mut args233 = Vec::new();
                                    let mut kw234 = Vec::new();
                                    args233.push(Val::Int(0i64));
                                    args233.push(binary(
                                        "add",
                                        e.get("fa")?.attr("plateau_z")?,
                                        Val::Float(4.5f64),
                                    )?);
                                    fun235.call(args233, kw234)?
                                }
                                .attr("rect")?;
                                let mut args230 = Vec::new();
                                let mut kw231 = Vec::new();
                                args230.push(Val::Int(13i64));
                                args230.push(Val::Float(8.5f64));
                                kw231.push(("centered".into(), {
                                    let mut s = Vec::new();
                                    s.push(Val::Bool(true));
                                    s.push(Val::Bool(false));
                                    Val::tuple(s)
                                }));
                                fun232.call(args230, kw231)?
                            }
                            .attr("workplane")?;
                            let mut args227 = Vec::new();
                            let mut kw228 = Vec::new();
                            kw228.push(("offset".into(), Val::Int(36i64)));
                            fun229.call(args227, kw228)?
                        }
                        .attr("moveTo")?;
                        let mut args224 = Vec::new();
                        let mut kw225 = Vec::new();
                        args224.push(Val::Int(0i64));
                        args224.push(binary(
                            "add",
                            e.get("fa")?.attr("plateau_z")?,
                            Val::Int(10i64),
                        )?);
                        fun226.call(args224, kw225)?
                    }
                    .attr("rect")?;
                    let mut args221 = Vec::new();
                    let mut kw222 = Vec::new();
                    args221.push(Val::Int(13i64));
                    args221.push(Val::Int(3i64));
                    kw222.push(("centered".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Bool(true));
                        s.push(Val::Bool(false));
                        Val::tuple(s)
                    }));
                    fun223.call(args221, kw222)?
                }
                .attr("loft")?;
                let mut args218 = Vec::new();
                let mut kw219 = Vec::new();
                kw219.push(("combine".into(), Val::Bool(true)));
                fun220.call(args218, kw219)?
            };
            e.set("taper", assigned217.clone())?;
            let assigned242 = {
                let fun245 = {
                    let fun248 = {
                        let fun251 = {
                            let fun254 = {
                                let fun257 = {
                                    let fun260 = {
                                        let fun263 = {
                                            let fun266 = e.get("fa")?.attr("WorldWorkplane")?;
                                            let mut args264 = Vec::new();
                                            let mut kw265 = Vec::new();
                                            args264.push(e.get("fa")?.attr("xy_plane_z_up")?);
                                            fun266.call(args264, kw265)?
                                        }
                                        .attr("workplane")?;
                                        let mut args261 = Vec::new();
                                        let mut kw262 = Vec::new();
                                        kw262.push((
                                            "offset".into(),
                                            binary(
                                                "add",
                                                e.get("fa")?.attr("plateau_z")?,
                                                Val::Int(1i64),
                                            )?,
                                        ));
                                        fun263.call(args261, kw262)?
                                    }
                                    .attr("moveTo")?;
                                    let mut args258 = Vec::new();
                                    let mut kw259 = Vec::new();
                                    args258.push({
                                        let mut s = Vec::new();
                                        s.push(Val::Int(0i64));
                                        s.push(unary("pos", Val::Float(1.5f64))?);
                                        Val::tuple(s)
                                    });
                                    fun260.call(args258, kw259)?
                                }
                                .attr("rect")?;
                                let mut args255 = Vec::new();
                                let mut kw256 = Vec::new();
                                args255.push(Val::Int(13i64));
                                args255.push(Val::Int(15i64));
                                fun257.call(args255, kw256)?
                            }
                            .attr("extrude")?;
                            let mut args252 = Vec::new();
                            let mut kw253 = Vec::new();
                            args252.push(Val::Int(12i64));
                            fun254.call(args252, kw253)?
                        }
                        .attr("unwrap")?;
                        let mut args249 = Vec::new();
                        let mut kw250 = Vec::new();
                        fun251.call(args249, kw250)?
                    }
                    .attr("union")?;
                    let mut args246 = Vec::new();
                    let mut kw247 = Vec::new();
                    args246.push(e.get("taper")?);
                    fun248.call(args246, kw247)?
                }
                .attr("cut")?;
                let mut args243 = Vec::new();
                let mut kw244 = Vec::new();
                args243.push(e.get("cut_cylinder")?);
                fun245.call(args243, kw244)?
            };
            e.set("rest", assigned242.clone())?;
            let assigned267 = {
                let mut s = Vec::new();
                s.push(Val::Int(0i64));
                s.push(e.get("fa")?.attr("lever_pivot_y")?);
                s.push(e.get("fa")?.attr("lever_pivot_z")?);
                Val::tuple(s)
            };
            e.set("pivot_a", assigned267.clone())?;
            let assigned268 = {
                let mut s = Vec::new();
                s.push(Val::Int(1i64));
                s.push(e.get("fa")?.attr("lever_pivot_y")?);
                s.push(e.get("fa")?.attr("lever_pivot_z")?);
                Val::tuple(s)
            };
            e.set("pivot_b", assigned268.clone())?;
            let assigned269 = {
                let fun272 = {
                    let fun275 = e.get("rest")?.attr("rotate")?;
                    let mut args273 = Vec::new();
                    let mut kw274 = Vec::new();
                    args273.push(e.get("pivot_a")?);
                    args273.push(e.get("pivot_b")?);
                    args273.push(unary("pos", e.get("fa")?.attr("lever_press_angle_deg")?)?);
                    fun275.call(args273, kw274)?
                }
                .attr("cut")?;
                let mut args270 = Vec::new();
                let mut kw271 = Vec::new();
                args270.push(e.get("cut_cylinder")?);
                fun272.call(args270, kw271)?
            };
            e.set("pressed", assigned269.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("rest")?);
                s.push(e.get("pressed")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // _build_steps
    e.set("_build_steps", {
        let params = vec![("work".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned276 = {
                let fun279 = e.get("_load_faucet_module")?;
                let mut args277 = Vec::new();
                let mut kw278 = Vec::new();
                fun279.call(args277, kw278)?
            };
            e.set("fa", assigned276.clone())?;
            let assigned280 = {
                let fun283 = e.get("fa")?.attr("build_assembly")?;
                let mut args281 = Vec::new();
                let mut kw282 = Vec::new();
                fun283.call(args281, kw282)?
            };
            e.set("faucet", assigned280.clone())?;
            let assigned284 = {
                let fun287 = e.get("_children_by_name")?;
                let mut args285 = Vec::new();
                let mut kw286 = Vec::new();
                args285.push(e.get("faucet")?);
                fun287.call(args285, kw286)?
            };
            e.set("parts", assigned284.clone())?;
            let assigned288 = {
                let fun291 = e.get("_physical_levers")?;
                let mut args289 = Vec::new();
                let mut kw290 = Vec::new();
                args289.push(e.get("fa")?);
                fun291.call(args289, kw290)?
            };
            let unpack292 = unpack(assigned288.clone(), 2)?;
            e.set("lever_rest", unpack292[0].clone())?;
            e.set("lever_pressed", unpack292[1].clone())?;
            let assigned293 = {
                let mut s = Vec::new();
                s.push(Val::Str("westbrass".into()));
                s.push(Val::Str("drain_tube".into()));
                s.push(Val::Str("soda_faucet_tube".into()));
                s.push(Val::Str("tpu_o_ring".into()));
                s.push(Val::Str("flavor_tube_pos_x".into()));
                s.push(Val::Str("flavor_tube_neg_x".into()));
                s.push(Val::Str("lever".into()));
                s.push(Val::Str("above_counter_plate".into()));
                s.push(Val::Str("above_counter_gasket".into()));
                s.push(Val::Str("shell_base".into()));
                s.push(Val::Str("shell_tip".into()));
                s.push(Val::Str("faucet-display-cover-seated".into()));
                s.push(Val::Str("faucet_display".into()));
                s.push(Val::Str("faucet_display_screen".into()));
                Val::tuple(s)
            };
            e.set("above_counter_names", assigned293.clone())?;
            // above_counter_with
            e.set("above_counter_with", {
                let params = vec![("lever".into(), None, false), ("name".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned294 = {
                        let fun297 = e.get("cq")?.attr("Assembly")?;
                        let mut args295 = Vec::new();
                        let mut kw296 = Vec::new();
                        kw296.push(("name".into(), e.get("name")?));
                        fun297.call(args295, kw296)?
                    };
                    e.set("above", assigned294.clone())?;
                    for item298 in e.get("above_counter_names")?.iter()? {
                        e.set("part_name", item298)?;
                        let assigned299 = e.get("parts")?.get(e.get("part_name")?)?;
                        e.set("child", assigned299.clone())?;
                        let assigned300 = if {
                            let v301 = e.get("part_name")?;
                            let v302 = Val::Str("lever".into());
                            Val::Bool(compare("eq", v301.clone(), v302.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            e.get("lever")?
                        } else {
                            e.get("child")?.attr("obj")?
                        };
                        e.set("obj", assigned300.clone())?;
                        if {
                            let v303 = e.get("part_name")?;
                            let v304 = {
                                let mut s = Vec::new();
                                s.push(Val::Str("westbrass".into()));
                                s.push(Val::Str("drain_tube".into()));
                                s.push(Val::Str("flavor_tube_pos_x".into()));
                                s.push(Val::Str("flavor_tube_neg_x".into()));
                                Val::set_values(s)
                            };
                            Val::Bool(compare("in", v303.clone(), v304.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            let assigned305 = {
                                let fun308 = e.get("_clip_z")?;
                                let mut args306 = Vec::new();
                                let mut kw307 = Vec::new();
                                args306.push(e.get("obj")?);
                                args306.push(e.get("fa")?.attr("countertop_top_z")?);
                                args306.push(Val::Float(260.0f64));
                                fun308.call(args306, kw307)?
                            };
                            e.set("obj", assigned305.clone())?;
                        }
                        {
                            let fun311 = e.get("_add_child")?;
                            let mut args309 = Vec::new();
                            let mut kw310 = Vec::new();
                            args309.push(e.get("above")?);
                            args309.push(e.get("child")?);
                            kw310.push(("obj".into(), e.get("obj")?));
                            fun311.call(args309, kw310)?
                        };
                    }
                    return Ok(e.get("above")?);
                    Ok(Val::None)
                })
            })?;
            let assigned312 = {
                let fun315 = e.get("_export_colored")?;
                let mut args313 = Vec::new();
                let mut kw314 = Vec::new();
                args313.push({
                    let fun318 = e.get("above_counter_with")?;
                    let mut args316 = Vec::new();
                    let mut kw317 = Vec::new();
                    args316.push(e.get("lever_rest")?);
                    args316.push(Val::Str("faucet-user".into()));
                    fun318.call(args316, kw317)?
                });
                args313.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("faucet-user.step".into()),
                )?);
                kw314.push(("mesh".into(), Val::Bool(true)));
                fun315.call(args313, kw314)?
            };
            e.set("user_step", assigned312.clone())?;
            let assigned319 = {
                let fun322 = e.get("_export_colored")?;
                let mut args320 = Vec::new();
                let mut kw321 = Vec::new();
                args320.push({
                    let fun325 = e.get("above_counter_with")?;
                    let mut args323 = Vec::new();
                    let mut kw324 = Vec::new();
                    args323.push(e.get("lever_pressed")?);
                    args323.push(Val::Str("faucet-user-pressed".into()));
                    fun325.call(args323, kw324)?
                });
                args320.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("faucet-user-pressed.step".into()),
                )?);
                kw321.push(("mesh".into(), Val::Bool(true)));
                fun322.call(args320, kw321)?
            };
            e.set("pressed_step", assigned319.clone())?;
            let assigned326 = {
                let fun329 = e.get("_export_colored")?;
                let mut args327 = Vec::new();
                let mut kw328 = Vec::new();
                args327.push(e.get("faucet")?);
                args327.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("faucet-full.step".into()),
                )?);
                kw328.push(("mesh".into(), Val::Bool(true)));
                fun329.call(args327, kw328)?
            };
            e.set("faucet_full_step", assigned326.clone())?;
            let assigned330 = {
                let fun333 = {
                    let fun336 = {
                        let fun339 = {
                            let fun342 = e.get("cq")?.attr("Workplane")?;
                            let mut args340 = Vec::new();
                            let mut kw341 = Vec::new();
                            args340.push(Val::Str("XY".into()));
                            fun342.call(args340, kw341)?
                        }
                        .attr("workplane")?;
                        let mut args337 = Vec::new();
                        let mut kw338 = Vec::new();
                        kw338.push(("offset".into(), e.get("fa")?.attr("countertop_bottom_z")?));
                        fun339.call(args337, kw338)?
                    }
                    .attr("box")?;
                    let mut args334 = Vec::new();
                    let mut kw335 = Vec::new();
                    args334.push(e.get("UNDER_COUNTERTOP_X")?);
                    args334.push(e.get("UNDER_COUNTERTOP_Y")?);
                    args334.push(e.get("fa")?.attr("countertop_thickness")?);
                    kw335.push(("centered".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Bool(true));
                        s.push(Val::Bool(true));
                        s.push(Val::Bool(false));
                        Val::tuple(s)
                    }));
                    fun336.call(args334, kw335)?
                }
                .attr("cut")?;
                let mut args331 = Vec::new();
                let mut kw332 = Vec::new();
                args331.push({
                    let fun345 = {
                        let fun348 = {
                            let fun351 = {
                                let fun354 = {
                                    let fun357 = e.get("cq")?.attr("Workplane")?;
                                    let mut args355 = Vec::new();
                                    let mut kw356 = Vec::new();
                                    args355.push(Val::Str("XY".into()));
                                    fun357.call(args355, kw356)?
                                }
                                .attr("workplane")?;
                                let mut args352 = Vec::new();
                                let mut kw353 = Vec::new();
                                kw353.push((
                                    "offset".into(),
                                    binary(
                                        "sub",
                                        e.get("fa")?.attr("countertop_bottom_z")?,
                                        Val::Float(1.0f64),
                                    )?,
                                ));
                                fun354.call(args352, kw353)?
                            }
                            .attr("center")?;
                            let mut args349 = Vec::new();
                            let mut kw350 = Vec::new();
                            args349.push(Val::Float(0.0f64));
                            args349.push(e.get("fa")?.attr("countertop_hole_center_y")?);
                            fun351.call(args349, kw350)?
                        }
                        .attr("circle")?;
                        let mut args346 = Vec::new();
                        let mut kw347 = Vec::new();
                        args346.push(e.get("fa")?.attr("hole_radius")?);
                        fun348.call(args346, kw347)?
                    }
                    .attr("extrude")?;
                    let mut args343 = Vec::new();
                    let mut kw344 = Vec::new();
                    args343.push(binary(
                        "add",
                        e.get("fa")?.attr("countertop_thickness")?,
                        Val::Float(2.0f64),
                    )?);
                    fun345.call(args343, kw344)?
                });
                fun333.call(args331, kw332)?
            };
            e.set("countertop_window", assigned330.clone())?;
            let assigned358 = {
                let mut s = Vec::new();
                s.push(Val::Str("westbrass".into()));
                s.push(Val::Str("drain_tube".into()));
                s.push(Val::Str("soda_faucet_tube".into()));
                s.push(Val::Str("tpu_o_ring".into()));
                s.push(Val::Str("flavor_tube_pos_x".into()));
                s.push(Val::Str("flavor_tube_neg_x".into()));
                s.push(Val::Str("flavor_umbilical_tube_pos_x".into()));
                s.push(Val::Str("flavor_umbilical_tube_neg_x".into()));
                s.push(Val::Str("soda_umbilical_tube".into()));
                s.push(Val::Str("lever".into()));
                s.push(Val::Str("above_counter_plate".into()));
                s.push(Val::Str("above_counter_gasket".into()));
                s.push(Val::Str("shell_base".into()));
                s.push(Val::Str("shell_tip".into()));
                s.push(Val::Str("faucet-display-cover-seated".into()));
                s.push(Val::Str("faucet_display".into()));
                s.push(Val::Str("faucet_display_screen".into()));
                Val::tuple(s)
            };
            e.set("mount_names", assigned358.clone())?;
            let assigned359 = {
                let e = e.child();
                let out360 = Val::dict(vec![]);
                for item361 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("flavor_tube".into()));
                    s.push(Val::Str("flavor_umbilical_tube".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("body", item361)?;
                    for item362 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("pos_x".into()));
                        s.push(Val::Str("neg_x".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("side", item362)?;
                        out360.set(
                            {
                                let mut str363 = String::new();
                                str363.push_str(&format(&e.get("body")?, &String::new())?);
                                str363.push_str("_");
                                str363.push_str(&format(&e.get("side")?, &String::new())?);
                                Val::Str(str363)
                            },
                            e.get("side")?,
                        )?;
                    }
                }
                out360
            };
            e.set("flavor_lengths", assigned359.clone())?;
            let assigned364 = {
                let mut s = Vec::new();
                s.extend(e.get("flavor_lengths")?.iter()?);
                s.push(Val::Str("soda_umbilical_tube".into()));
                s.push(Val::Str("drain_tube".into()));
                Val::set_values(s)
            };
            e.set("mount_tails", assigned364.clone())?;
            let assigned365 = {
                let mut s = Vec::new();
                s.push(unary("neg", Val::Float(88.0f64))?);
                s.push(Val::Float(380.0f64));
                Val::tuple(s)
            };
            e.set("mount_clip", assigned365.clone())?;
            let assigned366 = Val::Float(1.5f64);
            e.set("washer_thickness", assigned366.clone())?;
            let assigned367 = Val::Float(5.0f64);
            e.set("nut_height", assigned367.clone())?;
            let assigned368 = binary(
                "add",
                binary(
                    "add",
                    unary("neg", e.get("fa")?.attr("shank_length")?)?,
                    e.get("nut_height")?,
                )?,
                e.get("washer_thickness")?,
            )?;
            e.set("captive_washer_top_z", assigned368.clone())?;
            let assigned369 = binary(
                "sub",
                e.get("fa")?.attr("countertop_bottom_z")?,
                e.get("fa")?.attr("under_counter_plate_thickness")?,
            )?;
            e.set("final_washer_top_z", assigned369.clone())?;
            let assigned370 = {
                let fun373 = e.get("cq")?.attr("Color")?;
                let mut args371 = Vec::new();
                let mut kw372 = Vec::new();
                args371.push(Val::Float(0.91f64));
                args371.push(Val::Float(0.92f64));
                args371.push(Val::Float(0.94f64));
                args371.push(Val::Float(1.0f64));
                fun373.call(args371, kw372)?
            };
            e.set("plate_steel", assigned370.clone())?;
            let assigned374 = {
                let fun377 = e.get("cq")?.attr("Color")?;
                let mut args375 = Vec::new();
                let mut kw376 = Vec::new();
                args375.push(Val::Float(0.82f64));
                args375.push(Val::Float(0.83f64));
                args375.push(Val::Float(0.84f64));
                args375.push(Val::Float(1.0f64));
                fun377.call(args375, kw376)?
            };
            e.set("washer_steel", assigned374.clone())?;
            let assigned378 = {
                let fun381 = e.get("cq")?.attr("Color")?;
                let mut args379 = Vec::new();
                let mut kw380 = Vec::new();
                args379.push(Val::Float(0.43f64));
                args379.push(Val::Float(0.45f64));
                args379.push(Val::Float(0.48f64));
                args379.push(Val::Float(1.0f64));
                fun381.call(args379, kw380)?
            };
            e.set("nut_steel", assigned378.clone())?;
            let assigned382 = {
                let fun385 = e.get("cq")?.attr("Color")?;
                let mut args383 = Vec::new();
                let mut kw384 = Vec::new();
                args383.push(Val::Float(0.55f64));
                args383.push(Val::Float(0.55f64));
                args383.push(Val::Float(0.58f64));
                args383.push(Val::Float(1.0f64));
                fun385.call(args383, kw384)?
            };
            e.set("countertop_stone", assigned382.clone())?;
            let assigned386 = {
                let fun389 = e.get("cq")?.attr("Color")?;
                let mut args387 = Vec::new();
                let mut kw388 = Vec::new();
                args387.push(Val::Float(0.025f64));
                args387.push(Val::Float(0.027f64));
                args387.push(Val::Float(0.031f64));
                args387.push(Val::Float(1.0f64));
                fun389.call(args387, kw388)?
            };
            e.set("flavor_black_a", assigned386.clone())?;
            let assigned390 = {
                let fun393 = e.get("cq")?.attr("Color")?;
                let mut args391 = Vec::new();
                let mut kw392 = Vec::new();
                args391.push(Val::Float(0.2f64));
                args391.push(Val::Float(0.205f64));
                args391.push(Val::Float(0.215f64));
                args391.push(Val::Float(1.0f64));
                fun393.call(args391, kw392)?
            };
            e.set("flavor_black_b", assigned390.clone())?;
            let assigned394 = {
                let e = e.child();
                let out395 = Val::dict(vec![]);
                for item396 in {
                    let fun399 = e.get("flavor_lengths")?.attr("items")?;
                    let mut args397 = Vec::new();
                    let mut kw398 = Vec::new();
                    fun399.call(args397, kw398)?
                }
                .iter()?
                {
                    let unpack400 = unpack(item396, 2)?;
                    e.set("name", unpack400[0].clone())?;
                    e.set("side", unpack400[1].clone())?;
                    out395.set(
                        e.get("name")?,
                        if {
                            let v401 = e.get("side")?;
                            let v402 = Val::Str("pos_x".into());
                            Val::Bool(compare("eq", v401.clone(), v402.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            e.get("flavor_black_a")?
                        } else {
                            e.get("flavor_black_b")?
                        },
                    )?;
                }
                out395
            };
            e.set("flavor_colors", assigned394.clone())?;
            let assigned403 = {
                let fun406 = e.get("cq")?.attr("Color")?;
                let mut args404 = Vec::new();
                let mut kw405 = Vec::new();
                args404.push(Val::Float(0.035f64));
                args404.push(Val::Float(0.038f64));
                args404.push(Val::Float(0.043f64));
                args404.push(Val::Float(1.0f64));
                fun406.call(args404, kw405)?
            };
            e.set("signal_black", assigned403.clone())?;
            let assigned407 = {
                let fun410 = e.get("cq")?.attr("Color")?;
                let mut args408 = Vec::new();
                let mut kw409 = Vec::new();
                args408.push(Val::Float(0.16f64));
                args408.push(Val::Float(0.17f64));
                args408.push(Val::Float(0.19f64));
                args408.push(Val::Float(1.0f64));
                fun410.call(args408, kw409)?
            };
            e.set("signal_stripe_black", assigned407.clone())?;
            let assigned411 = {
                let fun414 = e.get("cq")?.attr("Color")?;
                let mut args412 = Vec::new();
                let mut kw413 = Vec::new();
                args412.push(Val::Float(0.95f64));
                args412.push(Val::Float(0.04f64));
                args412.push(Val::Float(0.82f64));
                args412.push(Val::Float(1.0f64));
                fun414.call(args412, kw413)?
            };
            e.set("frame_anchor_color", assigned411.clone())?;
            // donor_hardware
            e.set("donor_hardware", {
                let params = vec![("washer_top_z".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned415 =
                        binary("sub", e.get("washer_top_z")?, e.get("washer_thickness")?)?;
                    e.set("washer_bottom_z", assigned415.clone())?;
                    let assigned416 = {
                        let fun419 = {
                            let fun422 = {
                                let fun425 = {
                                    let fun428 = {
                                        let fun431 = e.get("cq")?.attr("Workplane")?;
                                        let mut args429 = Vec::new();
                                        let mut kw430 = Vec::new();
                                        args429.push(Val::Str("XY".into()));
                                        fun431.call(args429, kw430)?
                                    }
                                    .attr("workplane")?;
                                    let mut args426 = Vec::new();
                                    let mut kw427 = Vec::new();
                                    kw427.push(("offset".into(), e.get("washer_bottom_z")?));
                                    fun428.call(args426, kw427)?
                                }
                                .attr("circle")?;
                                let mut args423 = Vec::new();
                                let mut kw424 = Vec::new();
                                args423.push(Val::Float(12.0f64));
                                fun425.call(args423, kw424)?
                            }
                            .attr("circle")?;
                            let mut args420 = Vec::new();
                            let mut kw421 = Vec::new();
                            args420.push(Val::Float(6.1f64));
                            fun422.call(args420, kw421)?
                        }
                        .attr("extrude")?;
                        let mut args417 = Vec::new();
                        let mut kw418 = Vec::new();
                        args417.push(e.get("washer_thickness")?);
                        fun419.call(args417, kw418)?
                    };
                    e.set("washer", assigned416.clone())?;
                    let assigned432 = {
                        let fun435 = {
                            let fun438 = {
                                let fun441 = {
                                    let fun444 = {
                                        let fun447 = e.get("cq")?.attr("Workplane")?;
                                        let mut args445 = Vec::new();
                                        let mut kw446 = Vec::new();
                                        args445.push(Val::Str("XY".into()));
                                        fun447.call(args445, kw446)?
                                    }
                                    .attr("workplane")?;
                                    let mut args442 = Vec::new();
                                    let mut kw443 = Vec::new();
                                    kw443.push((
                                        "offset".into(),
                                        binary(
                                            "sub",
                                            e.get("washer_bottom_z")?,
                                            e.get("nut_height")?,
                                        )?,
                                    ));
                                    fun444.call(args442, kw443)?
                                }
                                .attr("polygon")?;
                                let mut args439 = Vec::new();
                                let mut kw440 = Vec::new();
                                args439.push(Val::Int(6i64));
                                args439.push(Val::Float(22.0f64));
                                fun441.call(args439, kw440)?
                            }
                            .attr("circle")?;
                            let mut args436 = Vec::new();
                            let mut kw437 = Vec::new();
                            args436.push(Val::Float(6.1f64));
                            fun438.call(args436, kw437)?
                        }
                        .attr("extrude")?;
                        let mut args433 = Vec::new();
                        let mut kw434 = Vec::new();
                        args433.push(e.get("nut_height")?);
                        fun435.call(args433, kw434)?
                    };
                    e.set("nut", assigned432.clone())?;
                    return Ok({
                        let mut s = Vec::new();
                        s.push(e.get("washer")?);
                        s.push(e.get("nut")?);
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned448 = Val::None;
            e.set("signal_geometry", assigned448.clone())?;
            // signal_ribbon
            e.set("signal_ribbon", {
                let params = vec![("lift_z".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    if {
                        let v449 = e.get("signal_geometry")?;
                        let v450 = Val::None;
                        Val::Bool(compare("is", v449.clone(), v450.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned451 = e.get("fa")?.attr("faucet_shell")?;
                        e.set("shell", assigned451.clone())?;
                        let assigned452 = {
                            let fun455 = e.get("fa")?.attr("_step_path")?;
                            let mut args453 = Vec::new();
                            let mut kw454 = Vec::new();
                            args453.push(unary("pos", Val::Int(1i64))?);
                            args453.push(unary("neg", Val::Float(123.0f64))?);
                            fun455.call(args453, kw454)?
                        };
                        e.set("path", assigned452.clone())?;
                        let assigned456 = {
                            let mut s = Vec::new();
                            s.push(e.get("shell")?.attr("signal_lower_exit_x")?);
                            s.push(e.get("shell")?.attr("signal_lower_exit_y")?);
                            s.push(e.get("fa")?.attr("under_counter_plate_bottom_z")?);
                            Val::tuple(s)
                        };
                        e.set("origin", assigned456.clone())?;
                        let assigned457 = {
                            let fun460 = {
                                let fun463 = {
                                    let fun466 = {
                                        let fun469 = e.get("cq")?.attr("Workplane")?;
                                        let mut args467 = Vec::new();
                                        let mut kw468 = Vec::new();
                                        args467.push(Val::Str("XY".into()));
                                        fun469.call(args467, kw468)?
                                    }
                                    .attr("rect")?;
                                    let mut args464 = Vec::new();
                                    let mut kw465 = Vec::new();
                                    args464.push(e.get("shell")?.attr("signal_ribbon_max_width")?);
                                    args464.push(e.get("shell")?.attr("signal_ribbon_max_depth")?);
                                    fun466.call(args464, kw465)?
                                }
                                .attr("sweep")?;
                                let mut args461 = Vec::new();
                                let mut kw462 = Vec::new();
                                args461.push(e.get("path")?);
                                kw462.push(("transition".into(), Val::Str("round".into())));
                                fun463.call(args461, kw462)?
                            }
                            .attr("translate")?;
                            let mut args458 = Vec::new();
                            let mut kw459 = Vec::new();
                            args458.push(e.get("origin")?);
                            fun460.call(args458, kw459)?
                        };
                        e.set("tail", assigned457.clone())?;
                        let assigned470 = {
                            let fun473 = e
                                .get("parts")?
                                .get(Val::Str("display_signal_ribbon".into()))?
                                .attr("obj")?
                                .attr("union")?;
                            let mut args471 = Vec::new();
                            let mut kw472 = Vec::new();
                            args471.push(e.get("tail")?);
                            fun473.call(args471, kw472)?
                        };
                        e.set("ribbon", assigned470.clone())?;
                        let assigned474 = {
                            let fun477 = {
                                let fun480 = {
                                    let fun483 = {
                                        let fun486 = {
                                            let fun489 = e.get("cq")?.attr("Workplane")?;
                                            let mut args487 = Vec::new();
                                            let mut kw488 = Vec::new();
                                            args487.push(Val::Str("XY".into()));
                                            fun489.call(args487, kw488)?
                                        }
                                        .attr("pushPoints")?;
                                        let mut args484 = Vec::new();
                                        let mut kw485 = Vec::new();
                                        args484.push({
                                            let mut s = Vec::new();
                                            s.push({
                                                let mut s = Vec::new();
                                                s.push(unary("neg", Val::Float(1.05f64))?);
                                                s.push(Val::Float(0.0f64));
                                                Val::tuple(s)
                                            });
                                            s.push({
                                                let mut s = Vec::new();
                                                s.push(Val::Float(0.0f64));
                                                s.push(Val::Float(0.0f64));
                                                Val::tuple(s)
                                            });
                                            s.push({
                                                let mut s = Vec::new();
                                                s.push(Val::Float(1.05f64));
                                                s.push(Val::Float(0.0f64));
                                                Val::tuple(s)
                                            });
                                            Val::list(s)
                                        });
                                        fun486.call(args484, kw485)?
                                    }
                                    .attr("rect")?;
                                    let mut args481 = Vec::new();
                                    let mut kw482 = Vec::new();
                                    args481.push(Val::Float(0.24f64));
                                    args481.push(Val::Float(0.08f64));
                                    fun483.call(args481, kw482)?
                                }
                                .attr("sweep")?;
                                let mut args478 = Vec::new();
                                let mut kw479 = Vec::new();
                                args478.push(e.get("path")?);
                                kw479.push(("transition".into(), Val::Str("round".into())));
                                fun480.call(args478, kw479)?
                            }
                            .attr("translate")?;
                            let mut args475 = Vec::new();
                            let mut kw476 = Vec::new();
                            args475.push({
                                let mut s = Vec::new();
                                s.push(e.get("origin")?.get(Val::Int(0i64))?);
                                s.push(binary(
                                    "sub",
                                    binary(
                                        "sub",
                                        e.get("origin")?.get(Val::Int(1i64))?,
                                        binary(
                                            "truediv",
                                            e.get("shell")?.attr("signal_ribbon_max_depth")?,
                                            Val::Float(2.0f64),
                                        )?,
                                    )?,
                                    Val::Float(0.04f64),
                                )?);
                                s.push(e.get("origin")?.get(Val::Int(2i64))?);
                                Val::tuple(s)
                            });
                            fun477.call(args475, kw476)?
                        };
                        e.set("stripes", assigned474.clone())?;
                        let assigned490 = {
                            let mut s = Vec::new();
                            s.push(e.get("ribbon")?);
                            s.push(e.get("stripes")?);
                            Val::tuple(s)
                        };
                        e.set_nonlocal("signal_geometry", assigned490.clone())?;
                    }
                    let assigned491 = {
                        let e = e.child();
                        let out492 = Val::list(vec![]);
                        for item493 in e.get("signal_geometry")?.iter()? {
                            e.set("obj", item493)?;
                            out492.attr("append")?.call(
                                vec![{
                                    let fun496 = e.get("_moved")?;
                                    let mut args494 = Vec::new();
                                    let mut kw495 = Vec::new();
                                    args494.push(e.get("obj")?);
                                    args494.push({
                                        let mut s = Vec::new();
                                        s.push(Val::Float(0.0f64));
                                        s.push(Val::Float(0.0f64));
                                        s.push(e.get("lift_z")?);
                                        Val::tuple(s)
                                    });
                                    fun496.call(args494, kw495)?
                                }],
                                vec![],
                            )?;
                        }
                        out492
                    };
                    let unpack497 = unpack(assigned491.clone(), 2)?;
                    e.set("ribbon", unpack497[0].clone())?;
                    e.set("stripes", unpack497[1].clone())?;
                    return Ok({
                        let mut s = Vec::new();
                        s.push({
                            let fun500 = e.get("_clip_z")?;
                            let mut args498 = Vec::new();
                            let mut kw499 = Vec::new();
                            args498.push(e.get("ribbon")?);
                            args498.extend(e.get("mount_clip")?.iter()?);
                            fun500.call(args498, kw499)?
                        });
                        s.push({
                            let fun503 = e.get("_clip_z")?;
                            let mut args501 = Vec::new();
                            let mut kw502 = Vec::new();
                            args501.push(e.get("stripes")?);
                            args501.extend(e.get("mount_clip")?.iter()?);
                            fun503.call(args501, kw502)?
                        });
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            })?;
            // add_render_frame
            e.set("add_render_frame", {
                let params = vec![("out".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned504 = {
                        let fun507 = e.get("cq")?.attr("Vector")?;
                        let mut args505 = Vec::new();
                        let mut kw506 = Vec::new();
                        args505.extend(e.get("MOUNT_CAM")?.iter()?);
                        fun507.call(args505, kw506)?
                    };
                    e.set("view", assigned504.clone())?;
                    let assigned508 = {
                        let fun511 = e.get("view")?.attr("multiply")?;
                        let mut args509 = Vec::new();
                        let mut kw510 = Vec::new();
                        args509.push(binary(
                            "truediv",
                            Val::Float(1.0f64),
                            e.get("view")?.attr("Length")?,
                        )?);
                        fun511.call(args509, kw510)?
                    };
                    e.set("view", assigned508.clone())?;
                    let assigned512 = {
                        let fun515 = e.get("cq")?.attr("Vector")?;
                        let mut args513 = Vec::new();
                        let mut kw514 = Vec::new();
                        args513.push(Val::Float(0.0f64));
                        args513.push(Val::Float(0.0f64));
                        args513.push(Val::Float(1.0f64));
                        fun515.call(args513, kw514)?
                    };
                    e.set("world_up", assigned512.clone())?;
                    let assigned516 = {
                        let fun519 = e.get("view")?.attr("cross")?;
                        let mut args517 = Vec::new();
                        let mut kw518 = Vec::new();
                        args517.push(e.get("world_up")?);
                        fun519.call(args517, kw518)?
                    };
                    e.set("right", assigned516.clone())?;
                    let assigned520 = {
                        let fun523 = e.get("right")?.attr("multiply")?;
                        let mut args521 = Vec::new();
                        let mut kw522 = Vec::new();
                        args521.push(binary(
                            "truediv",
                            Val::Float(1.0f64),
                            e.get("right")?.attr("Length")?,
                        )?);
                        fun523.call(args521, kw522)?
                    };
                    e.set("right", assigned520.clone())?;
                    let assigned524 = {
                        let fun527 = e.get("right")?.attr("cross")?;
                        let mut args525 = Vec::new();
                        let mut kw526 = Vec::new();
                        args525.push(e.get("view")?);
                        fun527.call(args525, kw526)?
                    };
                    e.set("screen_up", assigned524.clone())?;
                    let assigned528 = {
                        let fun531 = e.get("screen_up")?.attr("multiply")?;
                        let mut args529 = Vec::new();
                        let mut kw530 = Vec::new();
                        args529.push(binary(
                            "truediv",
                            Val::Float(1.0f64),
                            e.get("screen_up")?.attr("Length")?,
                        )?);
                        fun531.call(args529, kw530)?
                    };
                    e.set("screen_up", assigned528.clone())?;
                    let assigned532 = {
                        let fun535 = e.get("cq")?.attr("Vector")?;
                        let mut args533 = Vec::new();
                        let mut kw534 = Vec::new();
                        args533.extend(e.get("MOUNT_TARGET")?.iter()?);
                        fun535.call(args533, kw534)?
                    };
                    e.set("target", assigned532.clone())?;
                    for item536 in {
                        let fun569 = e.get("enumerate")?;
                        let mut args567 = Vec::new();
                        let mut kw568 = Vec::new();
                        args567.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                s.push(Val::Float(1.0f64));
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(1.0f64));
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(1.0f64));
                                s.push(Val::Float(1.0f64));
                                Val::tuple(s)
                            });
                            Val::tuple(s)
                        });
                        kw568.push(("start".into(), Val::Int(1i64)));
                        fun569.call(args567, kw568)?
                    }
                    .iter()?
                    {
                        let unpack570 = unpack(item536, 2)?;
                        e.set("index", unpack570[0].clone())?;
                        let unpack571 = unpack(unpack570[1].clone(), 2)?;
                        e.set("across", unpack571[0].clone())?;
                        e.set("rise", unpack571[1].clone())?;
                        let assigned537 = {
                            let fun540 = {
                                let fun543 = e.get("target")?.attr("add")?;
                                let mut args541 = Vec::new();
                                let mut kw542 = Vec::new();
                                args541.push({
                                    let fun546 = e.get("right")?.attr("multiply")?;
                                    let mut args544 = Vec::new();
                                    let mut kw545 = Vec::new();
                                    args544.push(binary(
                                        "mul",
                                        e.get("across")?,
                                        Val::Float(118.0f64),
                                    )?);
                                    fun546.call(args544, kw545)?
                                });
                                fun543.call(args541, kw542)?
                            }
                            .attr("add")?;
                            let mut args538 = Vec::new();
                            let mut kw539 = Vec::new();
                            args538.push({
                                let fun549 = e.get("screen_up")?.attr("multiply")?;
                                let mut args547 = Vec::new();
                                let mut kw548 = Vec::new();
                                args547.push(binary("mul", e.get("rise")?, Val::Float(235.0f64))?);
                                fun549.call(args547, kw548)?
                            });
                            fun540.call(args538, kw539)?
                        };
                        e.set("point", assigned537.clone())?;
                        let assigned550 = {
                            let fun553 = {
                                let fun556 = {
                                    let fun559 = {
                                        let fun562 = e.get("cq")?.attr("Workplane")?;
                                        let mut args560 = Vec::new();
                                        let mut kw561 = Vec::new();
                                        args560.push(Val::Str("XY".into()));
                                        fun562.call(args560, kw561)?
                                    }
                                    .attr("workplane")?;
                                    let mut args557 = Vec::new();
                                    let mut kw558 = Vec::new();
                                    kw558.push((
                                        "offset".into(),
                                        binary(
                                            "sub",
                                            e.get("point")?.attr("z")?,
                                            Val::Float(0.75f64),
                                        )?,
                                    ));
                                    fun559.call(args557, kw558)?
                                }
                                .attr("center")?;
                                let mut args554 = Vec::new();
                                let mut kw555 = Vec::new();
                                args554.push(e.get("point")?.attr("x")?);
                                args554.push(e.get("point")?.attr("y")?);
                                fun556.call(args554, kw555)?
                            }
                            .attr("box")?;
                            let mut args551 = Vec::new();
                            let mut kw552 = Vec::new();
                            args551.push(Val::Float(1.5f64));
                            args551.push(Val::Float(1.5f64));
                            args551.push(Val::Float(1.5f64));
                            kw552.push(("centered".into(), {
                                let mut s = Vec::new();
                                s.push(Val::Bool(true));
                                s.push(Val::Bool(true));
                                s.push(Val::Bool(false));
                                Val::tuple(s)
                            }));
                            fun553.call(args551, kw552)?
                        };
                        e.set("anchor", assigned550.clone())?;
                        {
                            let fun565 = e.get("out")?.attr("add")?;
                            let mut args563 = Vec::new();
                            let mut kw564 = Vec::new();
                            args563.push(e.get("anchor")?);
                            kw564.push(("name".into(), {
                                let mut str566 = String::new();
                                str566.push_str("render-frame-anchor-");
                                str566.push_str(&format(&e.get("index")?, &String::new())?);
                                Val::Str(str566)
                            }));
                            kw564.push(("color".into(), e.get("frame_anchor_color")?));
                            fun565.call(args563, kw564)?
                        };
                    }
                    Ok(Val::None)
                })
            })?;
            // add_under_render_frame
            e.set("add_under_render_frame", {
                let params = vec![("out".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned572 = {
                        let fun575 = e.get("cq")?.attr("Vector")?;
                        let mut args573 = Vec::new();
                        let mut kw574 = Vec::new();
                        args573.extend(e.get("UNDER_MOUNT_CAM")?.iter()?);
                        fun575.call(args573, kw574)?
                    };
                    e.set("view", assigned572.clone())?;
                    let assigned576 = {
                        let fun579 = e.get("view")?.attr("multiply")?;
                        let mut args577 = Vec::new();
                        let mut kw578 = Vec::new();
                        args577.push(binary(
                            "truediv",
                            Val::Float(1.0f64),
                            e.get("view")?.attr("Length")?,
                        )?);
                        fun579.call(args577, kw578)?
                    };
                    e.set("view", assigned576.clone())?;
                    let assigned580 = {
                        let fun583 = e.get("cq")?.attr("Vector")?;
                        let mut args581 = Vec::new();
                        let mut kw582 = Vec::new();
                        args581.push(Val::Float(0.0f64));
                        args581.push(Val::Float(0.0f64));
                        args581.push(Val::Float(1.0f64));
                        fun583.call(args581, kw582)?
                    };
                    e.set("world_up", assigned580.clone())?;
                    let assigned584 = {
                        let fun587 = e.get("view")?.attr("cross")?;
                        let mut args585 = Vec::new();
                        let mut kw586 = Vec::new();
                        args585.push(e.get("world_up")?);
                        fun587.call(args585, kw586)?
                    };
                    e.set("right", assigned584.clone())?;
                    let assigned588 = {
                        let fun591 = e.get("right")?.attr("multiply")?;
                        let mut args589 = Vec::new();
                        let mut kw590 = Vec::new();
                        args589.push(binary(
                            "truediv",
                            Val::Float(1.0f64),
                            e.get("right")?.attr("Length")?,
                        )?);
                        fun591.call(args589, kw590)?
                    };
                    e.set("right", assigned588.clone())?;
                    let assigned592 = {
                        let fun595 = e.get("right")?.attr("cross")?;
                        let mut args593 = Vec::new();
                        let mut kw594 = Vec::new();
                        args593.push(e.get("view")?);
                        fun595.call(args593, kw594)?
                    };
                    e.set("screen_up", assigned592.clone())?;
                    let assigned596 = {
                        let fun599 = e.get("screen_up")?.attr("multiply")?;
                        let mut args597 = Vec::new();
                        let mut kw598 = Vec::new();
                        args597.push(binary(
                            "truediv",
                            Val::Float(1.0f64),
                            e.get("screen_up")?.attr("Length")?,
                        )?);
                        fun599.call(args597, kw598)?
                    };
                    e.set("screen_up", assigned596.clone())?;
                    let assigned600 = {
                        let fun603 = e.get("cq")?.attr("Vector")?;
                        let mut args601 = Vec::new();
                        let mut kw602 = Vec::new();
                        args601.extend(e.get("UNDER_MOUNT_TARGET")?.iter()?);
                        fun603.call(args601, kw602)?
                    };
                    e.set("target", assigned600.clone())?;
                    for item604 in {
                        let fun637 = e.get("enumerate")?;
                        let mut args635 = Vec::new();
                        let mut kw636 = Vec::new();
                        args635.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                s.push(Val::Float(1.0f64));
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(1.0f64));
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(1.0f64));
                                s.push(Val::Float(1.0f64));
                                Val::tuple(s)
                            });
                            Val::tuple(s)
                        });
                        kw636.push(("start".into(), Val::Int(1i64)));
                        fun637.call(args635, kw636)?
                    }
                    .iter()?
                    {
                        let unpack638 = unpack(item604, 2)?;
                        e.set("index", unpack638[0].clone())?;
                        let unpack639 = unpack(unpack638[1].clone(), 2)?;
                        e.set("across", unpack639[0].clone())?;
                        e.set("rise", unpack639[1].clone())?;
                        let assigned605 = {
                            let fun608 = {
                                let fun611 = e.get("target")?.attr("add")?;
                                let mut args609 = Vec::new();
                                let mut kw610 = Vec::new();
                                args609.push({
                                    let fun614 = e.get("right")?.attr("multiply")?;
                                    let mut args612 = Vec::new();
                                    let mut kw613 = Vec::new();
                                    args612.push(binary(
                                        "mul",
                                        e.get("across")?,
                                        Val::Float(137.0f64),
                                    )?);
                                    fun614.call(args612, kw613)?
                                });
                                fun611.call(args609, kw610)?
                            }
                            .attr("add")?;
                            let mut args606 = Vec::new();
                            let mut kw607 = Vec::new();
                            args606.push({
                                let fun617 = e.get("screen_up")?.attr("multiply")?;
                                let mut args615 = Vec::new();
                                let mut kw616 = Vec::new();
                                args615.push(binary("mul", e.get("rise")?, Val::Float(58.0f64))?);
                                fun617.call(args615, kw616)?
                            });
                            fun608.call(args606, kw607)?
                        };
                        e.set("point", assigned605.clone())?;
                        let assigned618 = {
                            let fun621 = {
                                let fun624 = {
                                    let fun627 = {
                                        let fun630 = e.get("cq")?.attr("Workplane")?;
                                        let mut args628 = Vec::new();
                                        let mut kw629 = Vec::new();
                                        args628.push(Val::Str("XY".into()));
                                        fun630.call(args628, kw629)?
                                    }
                                    .attr("workplane")?;
                                    let mut args625 = Vec::new();
                                    let mut kw626 = Vec::new();
                                    kw626.push((
                                        "offset".into(),
                                        binary(
                                            "sub",
                                            e.get("point")?.attr("z")?,
                                            Val::Float(0.75f64),
                                        )?,
                                    ));
                                    fun627.call(args625, kw626)?
                                }
                                .attr("center")?;
                                let mut args622 = Vec::new();
                                let mut kw623 = Vec::new();
                                args622.push(e.get("point")?.attr("x")?);
                                args622.push(e.get("point")?.attr("y")?);
                                fun624.call(args622, kw623)?
                            }
                            .attr("box")?;
                            let mut args619 = Vec::new();
                            let mut kw620 = Vec::new();
                            args619.push(Val::Float(1.5f64));
                            args619.push(Val::Float(1.5f64));
                            args619.push(Val::Float(1.5f64));
                            kw620.push(("centered".into(), {
                                let mut s = Vec::new();
                                s.push(Val::Bool(true));
                                s.push(Val::Bool(true));
                                s.push(Val::Bool(false));
                                Val::tuple(s)
                            }));
                            fun621.call(args619, kw620)?
                        };
                        e.set("anchor", assigned618.clone())?;
                        {
                            let fun633 = e.get("out")?.attr("add")?;
                            let mut args631 = Vec::new();
                            let mut kw632 = Vec::new();
                            args631.push(e.get("anchor")?);
                            kw632.push(("name".into(), {
                                let mut str634 = String::new();
                                str634.push_str("under-render-frame-anchor-");
                                str634.push_str(&format(&e.get("index")?, &String::new())?);
                                Val::Str(str634)
                            }));
                            kw632.push(("color".into(), e.get("frame_anchor_color")?));
                            fun633.call(args631, kw632)?
                        };
                    }
                    Ok(Val::None)
                })
            })?;
            // add_mount_product
            e.set("add_mount_product", {
                let params = vec![
                    ("out".into(), None, false),
                    ("lift_z".into(), None, false),
                    ("washer_top_z".into(), Some(Val::None), true),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned640 = {
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("lift_z")?);
                        Val::tuple(s)
                    };
                    e.set("move", assigned640.clone())?;
                    for item641 in e.get("mount_names")?.iter()? {
                        e.set("part_name", item641)?;
                        let assigned642 = e.get("parts")?.get(e.get("part_name")?)?;
                        e.set("child", assigned642.clone())?;
                        let assigned643 = if {
                            let v644 = e.get("part_name")?;
                            let v645 = Val::Str("lever".into());
                            Val::Bool(compare("eq", v644.clone(), v645.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            e.get("lever_rest")?
                        } else {
                            e.get("child")?.attr("obj")?
                        };
                        e.set("obj", assigned643.clone())?;
                        let assigned646 = {
                            let fun649 = e.get("_moved")?;
                            let mut args647 = Vec::new();
                            let mut kw648 = Vec::new();
                            args647.push(e.get("obj")?);
                            args647.push(e.get("move")?);
                            fun649.call(args647, kw648)?
                        };
                        e.set("obj", assigned646.clone())?;
                        if {
                            let v650 = e.get("part_name")?;
                            let v651 = e.get("mount_tails")?;
                            Val::Bool(compare("in", v650.clone(), v651.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            let assigned652 = {
                                let fun655 = e.get("_clip_z")?;
                                let mut args653 = Vec::new();
                                let mut kw654 = Vec::new();
                                args653.push(e.get("obj")?);
                                args653.extend(e.get("mount_clip")?.iter()?);
                                fun655.call(args653, kw654)?
                            };
                            e.set("obj", assigned652.clone())?;
                            if unary("not", {
                                let fun658 = {
                                    let fun661 = e.get("obj")?.attr("solids")?;
                                    let mut args659 = Vec::new();
                                    let mut kw660 = Vec::new();
                                    fun661.call(args659, kw660)?
                                }
                                .attr("size")?;
                                let mut args656 = Vec::new();
                                let mut kw657 = Vec::new();
                                fun658.call(args656, kw657)?
                            })?
                            .truthy()?
                            {
                                continue;
                            }
                        }
                        {
                            let fun664 = e.get("_add_child")?;
                            let mut args662 = Vec::new();
                            let mut kw663 = Vec::new();
                            args662.push(e.get("out")?);
                            args662.push(e.get("child")?);
                            kw663.push(("obj".into(), e.get("obj")?));
                            kw663.push(("color".into(), {
                                let fun667 = e.get("flavor_colors")?.attr("get")?;
                                let mut args665 = Vec::new();
                                let mut kw666 = Vec::new();
                                args665.push(e.get("part_name")?);
                                fun667.call(args665, kw666)?
                            }));
                            fun664.call(args662, kw663)?
                        };
                    }
                    let assigned668 = {
                        let fun671 = e.get("signal_ribbon")?;
                        let mut args669 = Vec::new();
                        let mut kw670 = Vec::new();
                        args669.push(e.get("lift_z")?);
                        fun671.call(args669, kw670)?
                    };
                    let unpack672 = unpack(assigned668.clone(), 2)?;
                    e.set("ribbon", unpack672[0].clone())?;
                    e.set("ribbon_stripes", unpack672[1].clone())?;
                    {
                        let fun675 = e.get("out")?.attr("add")?;
                        let mut args673 = Vec::new();
                        let mut kw674 = Vec::new();
                        args673.push(e.get("ribbon")?);
                        kw674.push(("name".into(), Val::Str("sig6-flat-ribbon".into())));
                        kw674.push(("color".into(), e.get("signal_black")?));
                        fun675.call(args673, kw674)?
                    };
                    {
                        let fun678 = e.get("out")?.attr("add")?;
                        let mut args676 = Vec::new();
                        let mut kw677 = Vec::new();
                        args676.push(e.get("ribbon_stripes")?);
                        kw677.push(("name".into(), Val::Str("sig6-ribbon-face-stripes".into())));
                        kw677.push(("color".into(), e.get("signal_stripe_black")?));
                        fun678.call(args676, kw677)?
                    };
                    if {
                        let v679 = e.get("washer_top_z")?;
                        let v680 = Val::None;
                        Val::Bool(compare("is", v679.clone(), v680.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned681 =
                            binary("add", e.get("captive_washer_top_z")?, e.get("lift_z")?)?;
                        e.set("washer_top_z", assigned681.clone())?;
                    }
                    let assigned682 = {
                        let fun685 = e.get("donor_hardware")?;
                        let mut args683 = Vec::new();
                        let mut kw684 = Vec::new();
                        args683.push(e.get("washer_top_z")?);
                        fun685.call(args683, kw684)?
                    };
                    let unpack686 = unpack(assigned682.clone(), 2)?;
                    e.set("washer", unpack686[0].clone())?;
                    e.set("nut", unpack686[1].clone())?;
                    {
                        let fun689 = e.get("out")?.attr("add")?;
                        let mut args687 = Vec::new();
                        let mut kw688 = Vec::new();
                        args687.push(e.get("washer")?);
                        kw688.push(("name".into(), Val::Str("retained-donor-washer".into())));
                        kw688.push(("color".into(), e.get("washer_steel")?));
                        fun689.call(args687, kw688)?
                    };
                    {
                        let fun692 = e.get("out")?.attr("add")?;
                        let mut args690 = Vec::new();
                        let mut kw691 = Vec::new();
                        args690.push(e.get("nut")?);
                        kw691.push(("name".into(), Val::Str("retained-donor-nut".into())));
                        kw691.push(("color".into(), e.get("nut_steel")?));
                        fun692.call(args690, kw691)?
                    };
                    Ok(Val::None)
                })
            })?;
            // add_countertop_section
            e.set("add_countertop_section", {
                let params = vec![("out".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    {
                        let fun695 = e.get("out")?.attr("add")?;
                        let mut args693 = Vec::new();
                        let mut kw694 = Vec::new();
                        args693.push(e.get("countertop_window")?);
                        kw694.push(("name".into(), Val::Str("countertop-window".into())));
                        kw694.push(("color".into(), e.get("countertop_stone")?));
                        fun695.call(args693, kw694)?
                    };
                    Ok(Val::None)
                })
            })?;
            // add_under_countertop
            e.set("add_under_countertop", {
                let params = vec![("out".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    {
                        let fun698 = e.get("out")?.attr("add")?;
                        let mut args696 = Vec::new();
                        let mut kw697 = Vec::new();
                        args696.push(e.get("countertop_window")?);
                        kw697.push(("name".into(), Val::Str("under-countertop-window".into())));
                        kw697.push(("color".into(), e.get("countertop_stone")?));
                        fun698.call(args696, kw697)?
                    };
                    Ok(Val::None)
                })
            })?;
            // add_under_mount_product
            e.set("add_under_mount_product", {
                let params = vec![
                    ("out".into(), None, false),
                    ("washer_top_z".into(), None, true),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned699 = {
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Float(86.0f64))?);
                        s.push(unary("neg", Val::Float(2.0f64))?);
                        Val::tuple(s)
                    };
                    e.set("under_clip", assigned699.clone())?;
                    for item700 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("westbrass".into()));
                        s.extend(e.get("flavor_lengths")?.iter()?);
                        s.push(Val::Str("soda_umbilical_tube".into()));
                        s.push(Val::Str("drain_tube".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("part_name", item700)?;
                        let assigned701 = e.get("parts")?.get(e.get("part_name")?)?;
                        e.set("child", assigned701.clone())?;
                        let assigned702 = {
                            let fun705 = e.get("_clip_z")?;
                            let mut args703 = Vec::new();
                            let mut kw704 = Vec::new();
                            args703.push(e.get("child")?.attr("obj")?);
                            args703.extend(e.get("under_clip")?.iter()?);
                            fun705.call(args703, kw704)?
                        };
                        e.set("obj", assigned702.clone())?;
                        if unary("not", {
                            let fun708 = {
                                let fun711 = e.get("obj")?.attr("solids")?;
                                let mut args709 = Vec::new();
                                let mut kw710 = Vec::new();
                                fun711.call(args709, kw710)?
                            }
                            .attr("size")?;
                            let mut args706 = Vec::new();
                            let mut kw707 = Vec::new();
                            fun708.call(args706, kw707)?
                        })?
                        .truthy()?
                        {
                            continue;
                        }
                        {
                            let fun714 = e.get("_add_child")?;
                            let mut args712 = Vec::new();
                            let mut kw713 = Vec::new();
                            args712.push(e.get("out")?);
                            args712.push(e.get("child")?);
                            kw713.push(("name".into(), {
                                let mut str715 = String::new();
                                str715.push_str("under-");
                                str715.push_str(&format(&e.get("part_name")?, &String::new())?);
                                Val::Str(str715)
                            }));
                            kw713.push(("obj".into(), e.get("obj")?));
                            kw713.push(("color".into(), {
                                let fun718 = e.get("flavor_colors")?.attr("get")?;
                                let mut args716 = Vec::new();
                                let mut kw717 = Vec::new();
                                args716.push(e.get("part_name")?);
                                fun718.call(args716, kw717)?
                            }));
                            fun714.call(args712, kw713)?
                        };
                    }
                    let assigned719 = {
                        let fun722 = e.get("signal_ribbon")?;
                        let mut args720 = Vec::new();
                        let mut kw721 = Vec::new();
                        args720.push(Val::Float(0.0f64));
                        fun722.call(args720, kw721)?
                    };
                    let unpack723 = unpack(assigned719.clone(), 2)?;
                    e.set("ribbon", unpack723[0].clone())?;
                    e.set("ribbon_stripes", unpack723[1].clone())?;
                    {
                        let fun726 = e.get("out")?.attr("add")?;
                        let mut args724 = Vec::new();
                        let mut kw725 = Vec::new();
                        args724.push({
                            let fun729 = e.get("_clip_z")?;
                            let mut args727 = Vec::new();
                            let mut kw728 = Vec::new();
                            args727.push(e.get("ribbon")?);
                            args727.extend(e.get("under_clip")?.iter()?);
                            fun729.call(args727, kw728)?
                        });
                        kw725.push(("name".into(), Val::Str("under-sig6-flat-ribbon".into())));
                        kw725.push(("color".into(), e.get("signal_black")?));
                        fun726.call(args724, kw725)?
                    };
                    {
                        let fun732 = e.get("out")?.attr("add")?;
                        let mut args730 = Vec::new();
                        let mut kw731 = Vec::new();
                        args730.push({
                            let fun735 = e.get("_clip_z")?;
                            let mut args733 = Vec::new();
                            let mut kw734 = Vec::new();
                            args733.push(e.get("ribbon_stripes")?);
                            args733.extend(e.get("under_clip")?.iter()?);
                            fun735.call(args733, kw734)?
                        });
                        kw731.push((
                            "name".into(),
                            Val::Str("under-sig6-ribbon-face-stripes".into()),
                        ));
                        kw731.push(("color".into(), e.get("signal_stripe_black")?));
                        fun732.call(args730, kw731)?
                    };
                    let assigned736 = {
                        let fun739 = e.get("donor_hardware")?;
                        let mut args737 = Vec::new();
                        let mut kw738 = Vec::new();
                        args737.push(e.get("washer_top_z")?);
                        fun739.call(args737, kw738)?
                    };
                    let unpack740 = unpack(assigned736.clone(), 2)?;
                    e.set("washer", unpack740[0].clone())?;
                    e.set("nut", unpack740[1].clone())?;
                    {
                        let fun743 = e.get("out")?.attr("add")?;
                        let mut args741 = Vec::new();
                        let mut kw742 = Vec::new();
                        args741.push(e.get("washer")?);
                        kw742.push((
                            "name".into(),
                            Val::Str("under-retained-donor-washer".into()),
                        ));
                        kw742.push(("color".into(), e.get("washer_steel")?));
                        fun743.call(args741, kw742)?
                    };
                    {
                        let fun746 = e.get("out")?.attr("add")?;
                        let mut args744 = Vec::new();
                        let mut kw745 = Vec::new();
                        args744.push(e.get("nut")?);
                        kw745.push(("name".into(), Val::Str("under-retained-donor-nut".into())));
                        kw745.push(("color".into(), e.get("nut_steel")?));
                        fun746.call(args744, kw745)?
                    };
                    Ok(Val::None)
                })
            })?;
            let assigned747 = {
                let fun750 = e.get("cq")?.attr("Assembly")?;
                let mut args748 = Vec::new();
                let mut kw749 = Vec::new();
                kw749.push((
                    "name".into(),
                    Val::Str("faucet-mount-factory-captive".into()),
                ));
                fun750.call(args748, kw749)?
            };
            e.set("factory", assigned747.clone())?;
            {
                let fun753 = e.get("add_countertop_section")?;
                let mut args751 = Vec::new();
                let mut kw752 = Vec::new();
                args751.push(e.get("factory")?);
                fun753.call(args751, kw752)?
            };
            {
                let fun756 = e.get("add_mount_product")?;
                let mut args754 = Vec::new();
                let mut kw755 = Vec::new();
                args754.push(e.get("factory")?);
                args754.push(Val::Float(35.0f64));
                fun756.call(args754, kw755)?
            };
            {
                let fun759 = e.get("add_render_frame")?;
                let mut args757 = Vec::new();
                let mut kw758 = Vec::new();
                args757.push(e.get("factory")?);
                fun759.call(args757, kw758)?
            };
            let assigned760 = {
                let fun763 = e.get("_export_colored")?;
                let mut args761 = Vec::new();
                let mut kw762 = Vec::new();
                args761.push(e.get("factory")?);
                args761.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("mount-drop.step".into()),
                )?);
                kw762.push(("mesh".into(), Val::Bool(true)));
                fun763.call(args761, kw762)?
            };
            e.set("drop_step", assigned760.clone())?;
            let assigned764 = {
                let fun767 = e.get("cq")?.attr("Assembly")?;
                let mut args765 = Vec::new();
                let mut kw766 = Vec::new();
                kw766.push(("name".into(), Val::Str("faucet-mount-lowered".into())));
                fun767.call(args765, kw766)?
            };
            e.set("lowered", assigned764.clone())?;
            {
                let fun770 = e.get("add_countertop_section")?;
                let mut args768 = Vec::new();
                let mut kw769 = Vec::new();
                args768.push(e.get("lowered")?);
                fun770.call(args768, kw769)?
            };
            {
                let fun773 = e.get("add_mount_product")?;
                let mut args771 = Vec::new();
                let mut kw772 = Vec::new();
                args771.push(e.get("lowered")?);
                args771.push(Val::Float(0.0f64));
                fun773.call(args771, kw772)?
            };
            {
                let fun776 = e.get("add_render_frame")?;
                let mut args774 = Vec::new();
                let mut kw775 = Vec::new();
                args774.push(e.get("lowered")?);
                fun776.call(args774, kw775)?
            };
            let assigned777 = {
                let fun780 = e.get("_export_colored")?;
                let mut args778 = Vec::new();
                let mut kw779 = Vec::new();
                args778.push(e.get("lowered")?);
                args778.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("mount-lowered-clean.step".into()),
                )?);
                kw779.push(("mesh".into(), Val::Bool(true)));
                fun780.call(args778, kw779)?
            };
            e.set("lowered_clean_step", assigned777.clone())?;
            let assigned781 = {
                let fun784 = e.get("_export_colored")?;
                let mut args782 = Vec::new();
                let mut kw783 = Vec::new();
                args782.push(e.get("lowered")?);
                args782.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("mount-seated.step".into()),
                )?);
                kw783.push(("mesh".into(), Val::Bool(true)));
                fun784.call(args782, kw783)?
            };
            e.set("seated_step", assigned781.clone())?;
            let assigned785 = {
                let fun788 = e.get("cq")?.attr("Assembly")?;
                let mut args786 = Vec::new();
                let mut kw787 = Vec::new();
                kw787.push(("name".into(), Val::Str("faucet-mount-slide-plate".into())));
                fun788.call(args786, kw787)?
            };
            e.set("slide", assigned785.clone())?;
            {
                let fun791 = e.get("add_countertop_section")?;
                let mut args789 = Vec::new();
                let mut kw790 = Vec::new();
                args789.push(e.get("slide")?);
                fun791.call(args789, kw790)?
            };
            {
                let fun794 = e.get("add_mount_product")?;
                let mut args792 = Vec::new();
                let mut kw793 = Vec::new();
                args792.push(e.get("slide")?);
                args792.push(Val::Float(0.0f64));
                fun794.call(args792, kw793)?
            };
            {
                let fun797 = e.get("_add_child")?;
                let mut args795 = Vec::new();
                let mut kw796 = Vec::new();
                args795.push(e.get("slide")?);
                args795.push(
                    e.get("parts")?
                        .get(Val::Str("under_counter_plate".into()))?,
                );
                kw796.push(("obj".into(), {
                    let fun800 = e.get("_moved")?;
                    let mut args798 = Vec::new();
                    let mut kw799 = Vec::new();
                    args798.push(
                        e.get("parts")?
                            .get(Val::Str("under_counter_plate".into()))?
                            .attr("obj")?,
                    );
                    args798.push({
                        let mut s = Vec::new();
                        s.push(e.get("PLATE_APPROACH_X")?);
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun800.call(args798, kw799)?
                }));
                kw796.push(("color".into(), e.get("plate_steel")?));
                fun797.call(args795, kw796)?
            };
            {
                let fun803 = e.get("add_render_frame")?;
                let mut args801 = Vec::new();
                let mut kw802 = Vec::new();
                args801.push(e.get("slide")?);
                fun803.call(args801, kw802)?
            };
            let assigned804 = {
                let fun807 = e.get("_export_colored")?;
                let mut args805 = Vec::new();
                let mut kw806 = Vec::new();
                args805.push(e.get("slide")?);
                args805.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("mount-slide-clean.step".into()),
                )?);
                kw806.push(("mesh".into(), Val::Bool(true)));
                fun807.call(args805, kw806)?
            };
            e.set("slide_clean_step", assigned804.clone())?;
            let assigned808 = {
                let fun811 = e.get("_export_colored")?;
                let mut args809 = Vec::new();
                let mut kw810 = Vec::new();
                args809.push(e.get("slide")?);
                args809.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("mount-slide.step".into()),
                )?);
                kw810.push(("mesh".into(), Val::Bool(true)));
                fun811.call(args809, kw810)?
            };
            e.set("slide_step", assigned808.clone())?;
            let assigned812 = {
                let fun815 = e.get("cq")?.attr("Assembly")?;
                let mut args813 = Vec::new();
                let mut kw814 = Vec::new();
                kw814.push(("name".into(), Val::Str("faucet-mount-tighten".into())));
                fun815.call(args813, kw814)?
            };
            e.set("tight", assigned812.clone())?;
            {
                let fun818 = e.get("add_countertop_section")?;
                let mut args816 = Vec::new();
                let mut kw817 = Vec::new();
                args816.push(e.get("tight")?);
                fun818.call(args816, kw817)?
            };
            {
                let fun821 = e.get("add_mount_product")?;
                let mut args819 = Vec::new();
                let mut kw820 = Vec::new();
                args819.push(e.get("tight")?);
                args819.push(Val::Float(0.0f64));
                kw820.push(("washer_top_z".into(), e.get("final_washer_top_z")?));
                fun821.call(args819, kw820)?
            };
            {
                let fun824 = e.get("_add_child")?;
                let mut args822 = Vec::new();
                let mut kw823 = Vec::new();
                args822.push(e.get("tight")?);
                args822.push(
                    e.get("parts")?
                        .get(Val::Str("under_counter_plate".into()))?,
                );
                kw823.push(("color".into(), e.get("plate_steel")?));
                fun824.call(args822, kw823)?
            };
            {
                let fun827 = e.get("add_render_frame")?;
                let mut args825 = Vec::new();
                let mut kw826 = Vec::new();
                args825.push(e.get("tight")?);
                fun827.call(args825, kw826)?
            };
            let assigned828 = {
                let fun831 = e.get("_export_colored")?;
                let mut args829 = Vec::new();
                let mut kw830 = Vec::new();
                args829.push(e.get("tight")?);
                args829.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("mount-final-clean.step".into()),
                )?);
                kw830.push(("mesh".into(), Val::Bool(true)));
                fun831.call(args829, kw830)?
            };
            e.set("final_clean_step", assigned828.clone())?;
            let assigned832 = {
                let fun835 = e.get("_export_colored")?;
                let mut args833 = Vec::new();
                let mut kw834 = Vec::new();
                args833.push(e.get("tight")?);
                args833.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("mount-tighten.step".into()),
                )?);
                kw834.push(("mesh".into(), Val::Bool(true)));
                fun835.call(args833, kw834)?
            };
            e.set("tight_step", assigned832.clone())?;
            let assigned836 = {
                let fun839 = e.get("cq")?.attr("Assembly")?;
                let mut args837 = Vec::new();
                let mut kw838 = Vec::new();
                kw838.push(("name".into(), Val::Str("faucet-mount-under-slide".into())));
                fun839.call(args837, kw838)?
            };
            e.set("under_slide", assigned836.clone())?;
            {
                let fun842 = e.get("add_under_countertop")?;
                let mut args840 = Vec::new();
                let mut kw841 = Vec::new();
                args840.push(e.get("under_slide")?);
                fun842.call(args840, kw841)?
            };
            {
                let fun845 = e.get("add_under_mount_product")?;
                let mut args843 = Vec::new();
                let mut kw844 = Vec::new();
                args843.push(e.get("under_slide")?);
                kw844.push(("washer_top_z".into(), e.get("captive_washer_top_z")?));
                fun845.call(args843, kw844)?
            };
            {
                let fun848 = e.get("_add_child")?;
                let mut args846 = Vec::new();
                let mut kw847 = Vec::new();
                args846.push(e.get("under_slide")?);
                args846.push(
                    e.get("parts")?
                        .get(Val::Str("under_counter_plate".into()))?,
                );
                kw847.push(("name".into(), Val::Str("under-open-plate".into())));
                kw847.push(("obj".into(), {
                    let fun851 = e.get("_moved")?;
                    let mut args849 = Vec::new();
                    let mut kw850 = Vec::new();
                    args849.push(
                        e.get("parts")?
                            .get(Val::Str("under_counter_plate".into()))?
                            .attr("obj")?,
                    );
                    args849.push({
                        let mut s = Vec::new();
                        s.push(e.get("PLATE_APPROACH_X")?);
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun851.call(args849, kw850)?
                }));
                kw847.push(("color".into(), e.get("plate_steel")?));
                fun848.call(args846, kw847)?
            };
            {
                let fun854 = e.get("add_under_render_frame")?;
                let mut args852 = Vec::new();
                let mut kw853 = Vec::new();
                args852.push(e.get("under_slide")?);
                fun854.call(args852, kw853)?
            };
            let assigned855 = {
                let fun858 = e.get("_export_colored")?;
                let mut args856 = Vec::new();
                let mut kw857 = Vec::new();
                args856.push(e.get("under_slide")?);
                args856.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("mount-under-slide-clean.step".into()),
                )?);
                kw857.push(("mesh".into(), Val::Bool(true)));
                fun858.call(args856, kw857)?
            };
            e.set("under_slide_step", assigned855.clone())?;
            let assigned859 = {
                let fun862 = e.get("cq")?.attr("Assembly")?;
                let mut args860 = Vec::new();
                let mut kw861 = Vec::new();
                kw861.push(("name".into(), Val::Str("faucet-mount-under-tighten".into())));
                fun862.call(args860, kw861)?
            };
            e.set("under_tight", assigned859.clone())?;
            {
                let fun865 = e.get("add_under_countertop")?;
                let mut args863 = Vec::new();
                let mut kw864 = Vec::new();
                args863.push(e.get("under_tight")?);
                fun865.call(args863, kw864)?
            };
            {
                let fun868 = e.get("add_under_mount_product")?;
                let mut args866 = Vec::new();
                let mut kw867 = Vec::new();
                args866.push(e.get("under_tight")?);
                kw867.push(("washer_top_z".into(), e.get("final_washer_top_z")?));
                fun868.call(args866, kw867)?
            };
            {
                let fun871 = e.get("_add_child")?;
                let mut args869 = Vec::new();
                let mut kw870 = Vec::new();
                args869.push(e.get("under_tight")?);
                args869.push(
                    e.get("parts")?
                        .get(Val::Str("under_counter_plate".into()))?,
                );
                kw870.push(("name".into(), Val::Str("under-seated-plate".into())));
                kw870.push(("color".into(), e.get("plate_steel")?));
                fun871.call(args869, kw870)?
            };
            {
                let fun874 = e.get("add_under_render_frame")?;
                let mut args872 = Vec::new();
                let mut kw873 = Vec::new();
                args872.push(e.get("under_tight")?);
                fun874.call(args872, kw873)?
            };
            let assigned875 = {
                let fun878 = e.get("_export_colored")?;
                let mut args876 = Vec::new();
                let mut kw877 = Vec::new();
                args876.push(e.get("under_tight")?);
                args876.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("mount-under-tighten-clean.step".into()),
                )?);
                kw877.push(("mesh".into(), Val::Bool(true)));
                fun878.call(args876, kw877)?
            };
            e.set("under_tight_step", assigned875.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("faucet-user".into()), e.get("user_step")?)?;
                d.set(
                    Val::Str("faucet-user-pressed".into()),
                    e.get("pressed_step")?,
                )?;
                d.set(Val::Str("faucet-full".into()), e.get("faucet_full_step")?)?;
                d.set(Val::Str("mount-drop".into()), e.get("drop_step")?)?;
                d.set(Val::Str("mount-seated".into()), e.get("seated_step")?)?;
                d.set(Val::Str("mount-slide".into()), e.get("slide_step")?)?;
                d.set(Val::Str("mount-tighten".into()), e.get("tight_step")?)?;
                d.set(
                    Val::Str("mount-lowered-clean".into()),
                    e.get("lowered_clean_step")?,
                )?;
                d.set(
                    Val::Str("mount-slide-clean".into()),
                    e.get("slide_clean_step")?,
                )?;
                d.set(
                    Val::Str("mount-final-clean".into()),
                    e.get("final_clean_step")?,
                )?;
                d.set(
                    Val::Str("mount-under-slide-clean".into()),
                    e.get("under_slide_step")?,
                )?;
                d.set(
                    Val::Str("mount-under-tighten-clean".into()),
                    e.get("under_tight_step")?,
                )?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // _build_connection_steps
    e.set("_build_connection_steps", {
        let params = vec![("work".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun881 = e.get("note_read")?;
                let mut args879 = Vec::new();
                let mut kw880 = Vec::new();
                args879.push(e.get("MACHINE_FACTS")?);
                fun881.call(args879, kw880)?
            };
            let assigned882 = {
                let fun885 = e.get("json")?.attr("loads")?;
                let mut args883 = Vec::new();
                let mut kw884 = Vec::new();
                args883.push({
                    let fun888 = e.get("MACHINE_FACTS")?.attr("read_text")?;
                    let mut args886 = Vec::new();
                    let mut kw887 = Vec::new();
                    fun888.call(args886, kw887)?
                });
                fun885.call(args883, kw884)?
            };
            e.set("facts", assigned882.clone())?;
            let assigned889 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("tap".into()), Val::Str("water".into()))?;
                d.set(Val::Str("co2".into()), Val::Str("co2".into()))?;
                d.set(Val::Str("carb".into()), Val::Str("carb".into()))?;
                d.set(Val::Str("flavor-a".into()), Val::Str("flavor-a".into()))?;
                d.set(Val::Str("flavor-b".into()), Val::Str("flavor-b".into()))?;
                d.set(Val::Str("drain".into()), Val::Str("drain".into()))?;
                d
            };
            e.set("collar_steps", assigned889.clone())?;
            {
                let fun892 = e.get("note_read")?;
                let mut args890 = Vec::new();
                let mut kw891 = Vec::new();
                args890.push(binary(
                    "truediv",
                    e.get("TUBE_COLLAR_DIR")?,
                    Val::Str("tube_collar.py".into()),
                )?);
                fun892.call(args890, kw891)?
            };
            let assigned893 = {
                let mut s = Vec::new();
                s.push(Val::Str("c14-inlet".into()));
                s.push(Val::Str("keystone-jack".into()));
                s.push(Val::Str("co2-inlet".into()));
                s.push(Val::Str("bulkhead-water".into()));
                s.push(Val::Str("bulkhead-flavor-a".into()));
                s.push(Val::Str("bulkhead-flavor-b".into()));
                s.push(Val::Str("bulkhead-carb".into()));
                s.push(Val::Str("bulkhead-drain".into()));
                s.push(Val::Str("funnel".into()));
                s.push(Val::Str("nameplate".into()));
                s.push(Val::Str("nameplate-ink".into()));
                s.push(Val::Str("nameplate-screw-1".into()));
                s.push(Val::Str("nameplate-insert-1".into()));
                s.push(Val::Str("nameplate-screw-2".into()));
                s.push(Val::Str("nameplate-insert-2".into()));
                s.push(Val::Str("nameplate-screw-3".into()));
                s.push(Val::Str("nameplate-insert-3".into()));
                s.push(Val::Str("nameplate-screw-4".into()));
                s.push(Val::Str("nameplate-insert-4".into()));

                s.push(Val::Str("enclosure-back-bottom".into()));
                s.push(Val::Str("enclosure-back-top".into()));
                Val::set_values(s)
            };
            e.set("exact_names", assigned893.clone())?;
            let assigned894 = {
                let mut s = Vec::new();
                s.push(Val::Str("bulkhead-ring-".into()));
                Val::tuple(s)
            };
            e.set("exact_prefixes", assigned894.clone())?;
            let assigned895 = {
                let fun898 = e.get("machine_bodies")?;
                let mut args896 = Vec::new();
                let mut kw897 = Vec::new();
                args896.push({
                    let params = vec![("name".into(), None, false)];
                    let outer = e.clone();
                    let runtime = rt.clone();
                    Val::function(move |args, kwargs| {
                        let rt = runtime.clone();
                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                        let _frame = rt.frame(&outer);
                        return Ok({
                            let v902 = {
                                let v903 = e.get("name")?;
                                let v904 = e.get("exact_names")?;
                                Val::Bool(compare("in", v903.clone(), v904.clone())?.truthy()?)
                            };
                            if v902.truthy()? {
                                v902
                            } else {
                                {
                                    let fun901 = e.get("name")?.attr("startswith")?;
                                    let mut args899 = Vec::new();
                                    let mut kw900 = Vec::new();
                                    args899.push(e.get("exact_prefixes")?);
                                    fun901.call(args899, kw900)?
                                }
                            }
                        });
                        Ok(Val::None)
                    })
                });
                fun898.call(args896, kw897)?
            };
            e.set("rear_bodies", assigned895.clone())?;
            let assigned905 = binary("sub", e.get("exact_names")?, {
                let e = e.child();
                let out906 = Val::set_values(vec![]);
                for item907 in e.get("rear_bodies")?.iter()? {
                    e.set("entry", item907)?;
                    out906.attr("add")?.call(
                        vec![
                            {
                                let fun910 = e
                                    .get("entry")?
                                    .get(Val::Str("name".into()))?
                                    .attr("split")?;
                                let mut args908 = Vec::new();
                                let mut kw909 = Vec::new();
                                args908.push(Val::Str("/".into()));
                                fun910.call(args908, kw909)?
                            }
                            .get(Val::Int(0i64))?,
                        ],
                        vec![],
                    )?;
                }
                out906
            })?;
            e.set("missing", assigned905.clone())?;
            if e.get("missing")?.truthy()? {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun913 = e.get("RuntimeError")?;
                        let mut args911 = Vec::new();
                        let mut kw912 = Vec::new();
                        args911.push({
                            let mut str914 = String::new();
                            str914.push_str(&format(
                                &e.get("MACHINE_MESH")?.attr("name")?,
                                &String::new(),
                            )?);
                            str914.push_str(" has no ");
                            str914.push_str(&format(
                                &{
                                    let fun917 = e.get("sorted")?;
                                    let mut args915 = Vec::new();
                                    let mut kw916 = Vec::new();
                                    args915.push(e.get("missing")?);
                                    fun917.call(args915, kw916)?
                                },
                                &String::new(),
                            )?);
                            str914.push_str(" for the rear scene");
                            Val::Str(str914)
                        });
                        fun913.call(args911, kw912)?
                    })?
                );
            }
            let assigned918 = {
                let fun921 = e.get("cq")?.attr("Color")?;
                let mut args919 = Vec::new();
                let mut kw920 = Vec::new();
                args919.push(Val::Float(0.035f64));
                args919.push(Val::Float(0.31f64));
                args919.push(Val::Float(0.82f64));
                args919.push(Val::Float(1.0f64));
                fun921.call(args919, kw920)?
            };
            e.set("tube_blue", assigned918.clone())?;
            let assigned922 = {
                let fun925 = e.get("cq")?.attr("Color")?;
                let mut args923 = Vec::new();
                let mut kw924 = Vec::new();
                args923.push(Val::Float(0.67f64));
                args923.push(Val::Float(0.042f64));
                args923.push(Val::Float(0.042f64));
                args923.push(Val::Float(1.0f64));
                fun925.call(args923, kw924)?
            };
            e.set("tube_red", assigned922.clone())?;
            let assigned926 = {
                let fun929 = e.get("cq")?.attr("Color")?;
                let mut args927 = Vec::new();
                let mut kw928 = Vec::new();
                args927.push(Val::Float(0.82f64));
                args927.push(Val::Float(0.84f64));
                args927.push(Val::Float(0.87f64));
                args927.push(Val::Float(1.0f64));
                fun929.call(args927, kw928)?
            };
            e.set("tube_white", assigned926.clone())?;
            let assigned930 = {
                let fun933 = e.get("cq")?.attr("Color")?;
                let mut args931 = Vec::new();
                let mut kw932 = Vec::new();
                args931.push(Val::Float(0.025f64));
                args931.push(Val::Float(0.027f64));
                args931.push(Val::Float(0.031f64));
                args931.push(Val::Float(1.0f64));
                fun933.call(args931, kw932)?
            };
            e.set("tube_black_a", assigned930.clone())?;
            let assigned934 = {
                let fun937 = e.get("cq")?.attr("Color")?;
                let mut args935 = Vec::new();
                let mut kw936 = Vec::new();
                args935.push(Val::Float(0.115f64));
                args935.push(Val::Float(0.12f64));
                args935.push(Val::Float(0.13f64));
                args935.push(Val::Float(1.0f64));
                fun937.call(args935, kw936)?
            };
            e.set("tube_black_b", assigned934.clone())?;
            let assigned938 = {
                let fun941 = e.get("cq")?.attr("Color")?;
                let mut args939 = Vec::new();
                let mut kw940 = Vec::new();
                args939.push(Val::Float(0.035f64));
                args939.push(Val::Float(0.038f64));
                args939.push(Val::Float(0.043f64));
                args939.push(Val::Float(1.0f64));
                fun941.call(args939, kw940)?
            };
            e.set("ribbon_black", assigned938.clone())?;
            let assigned942 = {
                let fun945 = e.get("cq")?.attr("Color")?;
                let mut args943 = Vec::new();
                let mut kw944 = Vec::new();
                args943.push(Val::Float(0.16f64));
                args943.push(Val::Float(0.17f64));
                args943.push(Val::Float(0.19f64));
                args943.push(Val::Float(1.0f64));
                fun945.call(args943, kw944)?
            };
            e.set("ribbon_edge", assigned942.clone())?;
            let assigned946 = {
                let fun949 = e.get("cq")?.attr("Color")?;
                let mut args947 = Vec::new();
                let mut kw948 = Vec::new();
                args947.push(Val::Float(0.72f64));
                args947.push(Val::Float(0.74f64));
                args947.push(Val::Float(0.78f64));
                args947.push(Val::Float(1.0f64));
                fun949.call(args947, kw948)?
            };
            e.set("plug_body", assigned946.clone())?;
            let assigned950 = {
                let fun953 = e.get("cq")?.attr("Color")?;
                let mut args951 = Vec::new();
                let mut kw952 = Vec::new();
                args951.push(Val::Float(0.86f64));
                args951.push(Val::Float(0.87f64));
                args951.push(Val::Float(0.89f64));
                args951.push(Val::Float(1.0f64));
                fun953.call(args951, kw952)?
            };
            e.set("plug_latch", assigned950.clone())?;
            let assigned954 = {
                let fun957 = e.get("cq")?.attr("Color")?;
                let mut args955 = Vec::new();
                let mut kw956 = Vec::new();
                args955.push(Val::Float(0.73f64));
                args955.push(Val::Float(0.49f64));
                args955.push(Val::Float(0.14f64));
                args955.push(Val::Float(1.0f64));
                fun957.call(args955, kw956)?
            };
            e.set("contact_gold", assigned954.clone())?;
            // round_sweep
            e.set("round_sweep", {
                let params = vec![
                    ("points".into(), None, false),
                    ("radius".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned958 = {
                        let e = e.child();
                        let out959 = Val::list(vec![]);
                        for item960 in e.get("points")?.iter()? {
                            e.set("point", item960)?;
                            out959.attr("append")?.call(
                                vec![{
                                    let fun963 = e.get("cq")?.attr("Vector")?;
                                    let mut args961 = Vec::new();
                                    let mut kw962 = Vec::new();
                                    args961.extend(e.get("point")?.iter()?);
                                    fun963.call(args961, kw962)?
                                }],
                                vec![],
                            )?;
                        }
                        out959
                    };
                    e.set("vectors", assigned958.clone())?;
                    let assigned964 = {
                        let fun967 = e.get("cq")?.attr("Vector")?;
                        let mut args965 = Vec::new();
                        let mut kw966 = Vec::new();
                        args965.push(Val::Float(0.0f64));
                        args965.push(Val::Float(1.0f64));
                        args965.push(Val::Float(0.0f64));
                        fun967.call(args965, kw966)?
                    };
                    e.set("tangent", assigned964.clone())?;
                    let assigned968 = {
                        let fun971 = e.get("cq")?.attr("Edge")?.attr("makeSpline")?;
                        let mut args969 = Vec::new();
                        let mut kw970 = Vec::new();
                        args969.push(e.get("vectors")?);
                        kw970.push(("tangents".into(), {
                            let mut s = Vec::new();
                            s.push(e.get("tangent")?);
                            s.push(e.get("tangent")?);
                            Val::tuple(s)
                        }));
                        kw970.push(("scale".into(), Val::Bool(false)));
                        fun971.call(args969, kw970)?
                    };
                    e.set("path", assigned968.clone())?;
                    let assigned972 = {
                        let fun975 = e.get("cq")?.attr("Wire")?.attr("makeCircle")?;
                        let mut args973 = Vec::new();
                        let mut kw974 = Vec::new();
                        args973.push(e.get("radius")?);
                        args973.push(e.get("vectors")?.get(Val::Int(0i64))?);
                        args973.push(e.get("tangent")?);
                        fun975.call(args973, kw974)?
                    };
                    e.set("profile", assigned972.clone())?;
                    return Ok({
                        let fun978 = e.get("cq")?.attr("Solid")?.attr("sweep")?;
                        let mut args976 = Vec::new();
                        let mut kw977 = Vec::new();
                        args976.push(e.get("profile")?);
                        args976.push({
                            let mut s = Vec::new();
                            Val::list(s)
                        });
                        args976.push(e.get("path")?);
                        kw977.push(("makeSolid".into(), Val::Bool(true)));
                        kw977.push(("isFrenet".into(), Val::Bool(false)));
                        fun978.call(args976, kw977)?
                    });
                    Ok(Val::None)
                })
            })?;
            // ribbon_sweep
            e.set("ribbon_sweep", {
                let params = vec![
                    ("points".into(), None, false),
                    ("width".into(), None, false),
                    ("thickness".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned979 = {
                        let e = e.child();
                        let out980 = Val::list(vec![]);
                        for item981 in e.get("points")?.iter()? {
                            e.set("point", item981)?;
                            out980.attr("append")?.call(
                                vec![{
                                    let fun984 = e.get("cq")?.attr("Vector")?;
                                    let mut args982 = Vec::new();
                                    let mut kw983 = Vec::new();
                                    args982.extend(e.get("point")?.iter()?);
                                    fun984.call(args982, kw983)?
                                }],
                                vec![],
                            )?;
                        }
                        out980
                    };
                    e.set("vectors", assigned979.clone())?;
                    let assigned985 = {
                        let fun988 = e.get("cq")?.attr("Vector")?;
                        let mut args986 = Vec::new();
                        let mut kw987 = Vec::new();
                        args986.push(Val::Float(0.0f64));
                        args986.push(Val::Float(1.0f64));
                        args986.push(Val::Float(0.0f64));
                        fun988.call(args986, kw987)?
                    };
                    e.set("tangent", assigned985.clone())?;
                    let assigned989 = {
                        let fun992 = e.get("cq")?.attr("Edge")?.attr("makeSpline")?;
                        let mut args990 = Vec::new();
                        let mut kw991 = Vec::new();
                        args990.push(e.get("vectors")?);
                        kw991.push(("tangents".into(), {
                            let mut s = Vec::new();
                            s.push(e.get("tangent")?);
                            s.push(e.get("tangent")?);
                            Val::tuple(s)
                        }));
                        kw991.push(("scale".into(), Val::Bool(false)));
                        fun992.call(args990, kw991)?
                    };
                    e.set("path", assigned989.clone())?;
                    let assigned993 = e.get("vectors")?.get(Val::Int(0i64))?;
                    e.set("p", assigned993.clone())?;
                    let assigned994 = {
                        let fun997 = e.get("cq")?.attr("Wire")?.attr("makePolygon")?;
                        let mut args995 = Vec::new();
                        let mut kw996 = Vec::new();
                        args995.push({
                            let mut s = Vec::new();
                            s.push({
                                let fun1000 = e.get("cq")?.attr("Vector")?;
                                let mut args998 = Vec::new();
                                let mut kw999 = Vec::new();
                                args998.push(binary(
                                    "sub",
                                    e.get("p")?.attr("x")?,
                                    binary("truediv", e.get("width")?, Val::Float(2.0f64))?,
                                )?);
                                args998.push(e.get("p")?.attr("y")?);
                                args998.push(binary(
                                    "sub",
                                    e.get("p")?.attr("z")?,
                                    binary("truediv", e.get("thickness")?, Val::Float(2.0f64))?,
                                )?);
                                fun1000.call(args998, kw999)?
                            });
                            s.push({
                                let fun1003 = e.get("cq")?.attr("Vector")?;
                                let mut args1001 = Vec::new();
                                let mut kw1002 = Vec::new();
                                args1001.push(binary(
                                    "add",
                                    e.get("p")?.attr("x")?,
                                    binary("truediv", e.get("width")?, Val::Float(2.0f64))?,
                                )?);
                                args1001.push(e.get("p")?.attr("y")?);
                                args1001.push(binary(
                                    "sub",
                                    e.get("p")?.attr("z")?,
                                    binary("truediv", e.get("thickness")?, Val::Float(2.0f64))?,
                                )?);
                                fun1003.call(args1001, kw1002)?
                            });
                            s.push({
                                let fun1006 = e.get("cq")?.attr("Vector")?;
                                let mut args1004 = Vec::new();
                                let mut kw1005 = Vec::new();
                                args1004.push(binary(
                                    "add",
                                    e.get("p")?.attr("x")?,
                                    binary("truediv", e.get("width")?, Val::Float(2.0f64))?,
                                )?);
                                args1004.push(e.get("p")?.attr("y")?);
                                args1004.push(binary(
                                    "add",
                                    e.get("p")?.attr("z")?,
                                    binary("truediv", e.get("thickness")?, Val::Float(2.0f64))?,
                                )?);
                                fun1006.call(args1004, kw1005)?
                            });
                            s.push({
                                let fun1009 = e.get("cq")?.attr("Vector")?;
                                let mut args1007 = Vec::new();
                                let mut kw1008 = Vec::new();
                                args1007.push(binary(
                                    "sub",
                                    e.get("p")?.attr("x")?,
                                    binary("truediv", e.get("width")?, Val::Float(2.0f64))?,
                                )?);
                                args1007.push(e.get("p")?.attr("y")?);
                                args1007.push(binary(
                                    "add",
                                    e.get("p")?.attr("z")?,
                                    binary("truediv", e.get("thickness")?, Val::Float(2.0f64))?,
                                )?);
                                fun1009.call(args1007, kw1008)?
                            });
                            Val::list(s)
                        });
                        kw996.push(("close".into(), Val::Bool(true)));
                        fun997.call(args995, kw996)?
                    };
                    e.set("profile", assigned994.clone())?;
                    return Ok({
                        let fun1012 = e.get("cq")?.attr("Solid")?.attr("sweep")?;
                        let mut args1010 = Vec::new();
                        let mut kw1011 = Vec::new();
                        args1010.push(e.get("profile")?);
                        args1010.push({
                            let mut s = Vec::new();
                            Val::list(s)
                        });
                        args1010.push(e.get("path")?);
                        kw1011.push(("makeSolid".into(), Val::Bool(true)));
                        kw1011.push(("isFrenet".into(), Val::Bool(true)));
                        fun1012.call(args1010, kw1011)?
                    });
                    Ok(Val::None)
                })
            })?;
            // split_collar
            e.set("split_collar", {
                let params = vec![("which".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    {
                        let fun1015 = e.get("sys")?.attr("path")?.attr("insert")?;
                        let mut args1013 = Vec::new();
                        let mut kw1014 = Vec::new();
                        args1013.push(Val::Int(0i64));
                        args1013.push({
                            let fun1018 = e.get("str")?;
                            let mut args1016 = Vec::new();
                            let mut kw1017 = Vec::new();
                            args1016.push(e.get("TUBE_COLLAR_DIR")?);
                            fun1018.call(args1016, kw1017)?
                        });
                        fun1015.call(args1013, kw1014)?
                    };
                    e.set("tube_collar", rt.import_module("tube_collar")?)?;
                    let assigned1019 = e.get("collar_steps")?.get(e.get("which")?)?;
                    e.set("collar_step", assigned1019.clone())?;
                    return Ok({
                        let mut s = Vec::new();
                        s.push({
                            let fun1022 = e.get("tube_collar")?.attr("build_collar")?;
                            let mut args1020 = Vec::new();
                            let mut kw1021 = Vec::new();
                            args1020.push(e.get("collar_step")?);
                            fun1022.call(args1020, kw1021)?
                        });
                        s.push({
                            let fun1025 = e.get("tube_collar")?.attr("build_word")?;
                            let mut args1023 = Vec::new();
                            let mut kw1024 = Vec::new();
                            args1023.push(e.get("collar_step")?);
                            fun1025.call(args1023, kw1024)?
                        });
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned1026 = e.get("facts")?.get(Val::Str("card_ports".into()))?;
            e.set("card_ports", assigned1026.clone())?;
            let assigned1027 = {
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("tap".into()),
                    e.get("card_ports")?
                        .get(Val::Str("bulkhead-water".into()))?
                        .get(Val::Str("outboard".into()))?,
                )?;
                d.set(
                    Val::Str("carb".into()),
                    e.get("card_ports")?
                        .get(Val::Str("bulkhead-carb".into()))?
                        .get(Val::Str("tube-out".into()))?,
                )?;
                d.set(
                    Val::Str("co2".into()),
                    e.get("card_ports")?
                        .get(Val::Str("gas-regulator".into()))?
                        .get(Val::Str("outboard".into()))?,
                )?;
                d.set(
                    Val::Str("flavor-a".into()),
                    e.get("card_ports")?
                        .get(Val::Str("bulkhead-flavor-a".into()))?
                        .get(Val::Str("tube-out".into()))?,
                )?;
                d.set(
                    Val::Str("flavor-b".into()),
                    e.get("card_ports")?
                        .get(Val::Str("bulkhead-flavor-b".into()))?
                        .get(Val::Str("tube-out".into()))?,
                )?;
                d.set(
                    Val::Str("drain".into()),
                    e.get("card_ports")?
                        .get(Val::Str("bulkhead-drain".into()))?
                        .get(Val::Str("outboard".into()))?,
                )?;
                d
            };
            e.set("ports", assigned1027.clone())?;
            let assigned1028 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("tap".into()), e.get("tube_white")?)?;
                d.set(Val::Str("carb".into()), e.get("tube_blue")?)?;
                d.set(Val::Str("co2".into()), e.get("tube_red")?)?;
                d.set(Val::Str("flavor-a".into()), e.get("tube_black_a")?)?;
                d.set(Val::Str("flavor-b".into()), e.get("tube_black_b")?)?;
                d.set(Val::Str("drain".into()), e.get("tube_white")?)?;
                d
            };
            e.set("tube_colors", assigned1028.clone())?;
            let assigned1029 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("tap".into()), Val::Str("water".into()))?;
                d.set(Val::Str("carb".into()), Val::Str("carb".into()))?;
                d.set(Val::Str("co2".into()), Val::Str("co2".into()))?;
                d.set(Val::Str("flavor-a".into()), Val::Str("flavor".into()))?;
                d.set(Val::Str("flavor-b".into()), Val::Str("flavor".into()))?;
                d.set(Val::Str("drain".into()), Val::Str("drain".into()))?;
                d
            };
            e.set("collar_fluids", assigned1029.clone())?;
            let assigned1030 = {
                let e = e.child();
                let out1031 = Val::dict(vec![]);
                for item1032 in {
                    let fun1035 = e.get("collar_fluids")?.attr("items")?;
                    let mut args1033 = Vec::new();
                    let mut kw1034 = Vec::new();
                    fun1035.call(args1033, kw1034)?
                }
                .iter()?
                {
                    let unpack1036 = unpack(item1032, 2)?;
                    e.set("which", unpack1036[0].clone())?;
                    e.set("fluid", unpack1036[1].clone())?;
                    out1031.set(e.get("which")?, {
                        let fun1039 = e.get("cq")?.attr("Color")?;
                        let mut args1037 = Vec::new();
                        let mut kw1038 = Vec::new();
                        args1037.extend(
                            {
                                let e = e.child();
                                let out1040 = Val::list(vec![]);
                                for item1041 in {
                                    let fun1044 = e.get("_materials")?.attr("chip_color")?;
                                    let mut args1042 = Vec::new();
                                    let mut kw1043 = Vec::new();
                                    args1042.push(e.get("fluid")?);
                                    fun1044.call(args1042, kw1043)?
                                }
                                .iter()?
                                {
                                    e.set("c", item1041)?;
                                    out1040.attr("append")?.call(
                                        vec![binary("truediv", e.get("c")?, Val::Float(255.0f64))?],
                                        vec![],
                                    )?;
                                }
                                out1040
                            }
                            .iter()?,
                        );
                        args1037.push(Val::Float(1.0f64));
                        fun1039.call(args1037, kw1038)?
                    })?;
                }
                out1031
            };
            e.set("collar_colors", assigned1030.clone())?;
            let assigned1045 = {
                let e = e.child();
                let out1046 = Val::dict(vec![]);
                for item1047 in {
                    let fun1050 = e.get("collar_fluids")?.attr("items")?;
                    let mut args1048 = Vec::new();
                    let mut kw1049 = Vec::new();
                    fun1050.call(args1048, kw1049)?
                }
                .iter()?
                {
                    let unpack1051 = unpack(item1047, 2)?;
                    e.set("which", unpack1051[0].clone())?;
                    e.set("fluid", unpack1051[1].clone())?;
                    out1046.set(e.get("which")?, {
                        let fun1054 = e.get("cq")?.attr("Color")?;
                        let mut args1052 = Vec::new();
                        let mut kw1053 = Vec::new();
                        args1052.extend(
                            {
                                let e = e.child();
                                let out1055 = Val::list(vec![]);
                                for item1056 in {
                                    let fun1059 = e.get("_materials")?.attr("word_color")?;
                                    let mut args1057 = Vec::new();
                                    let mut kw1058 = Vec::new();
                                    args1057.push(e.get("fluid")?);
                                    fun1059.call(args1057, kw1058)?
                                }
                                .iter()?
                                {
                                    e.set("c", item1056)?;
                                    out1055.attr("append")?.call(
                                        vec![binary("truediv", e.get("c")?, Val::Float(255.0f64))?],
                                        vec![],
                                    )?;
                                }
                                out1055
                            }
                            .iter()?,
                        );
                        args1052.push(Val::Float(1.0f64));
                        fun1054.call(args1052, kw1053)?
                    })?;
                }
                out1046
            };
            e.set("collar_word_colors", assigned1045.clone())?;
            let assigned1060 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("tap".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(60.0f64))?);
                    s.push(Val::Float(322.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("co2".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(40.0f64))?);
                    s.push(Val::Float(322.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("carb".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(50.0f64))?);
                    s.push(Val::Float(312.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("flavor-a".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(40.0f64))?);
                    s.push(Val::Float(302.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("flavor-b".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(60.0f64))?);
                    s.push(Val::Float(302.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("drain".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(50.0f64))?);
                    s.push(Val::Float(292.0f64));
                    Val::tuple(s)
                })?;
                d
            };
            e.set("pack_stations", assigned1060.clone())?;
            let assigned1061 = {
                let fun1064 = e.get("cq")?.attr("Assembly")?;
                let mut args1062 = Vec::new();
                let mut kw1063 = Vec::new();
                kw1063.push((
                    "name".into(),
                    Val::Str("customer-field-leads-wall-end".into()),
                ));
                fun1064.call(args1062, kw1063)?
            };
            e.set("umbilical", assigned1061.clone())?;
            let assigned1065 = Val::Float(560.0f64);
            e.set("straight_end_y", assigned1065.clone())?;
            let assigned1066 = Val::Float(626.0f64);
            e.set("pack_y", assigned1066.clone())?;
            let assigned1067 = Val::Float(940.0f64);
            e.set("tail_y", assigned1067.clone())?;
            let assigned1068 = Val::Float(47.5f64);
            e.set("collar_tip_setback", assigned1068.clone())?;
            for item1069 in {
                let mut s = Vec::new();
                s.push(Val::Str("tap".into()));
                s.push(Val::Str("co2".into()));
                s.push(Val::Str("carb".into()));
                s.push(Val::Str("flavor-a".into()));
                s.push(Val::Str("flavor-b".into()));
                s.push(Val::Str("drain".into()));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("which", item1069)?;
                let assigned1070 = e
                    .get("ports")?
                    .get(e.get("which")?)?
                    .get(Val::Str("pos".into()))?;
                let unpack1071 = unpack(assigned1070.clone(), 3)?;
                e.set("x", unpack1071[0].clone())?;
                e.set("tube_start_y", unpack1071[1].clone())?;
                e.set("z", unpack1071[2].clone())?;
                let assigned1072 = e.get("pack_stations")?.get(e.get("which")?)?;
                let unpack1073 = unpack(assigned1072.clone(), 2)?;
                e.set("pack_x", unpack1073[0].clone())?;
                e.set("pack_z", unpack1073[1].clone())?;
                let assigned1074 = {
                    let fun1077 = e.get("round_sweep")?;
                    let mut args1075 = Vec::new();
                    let mut kw1076 = Vec::new();
                    args1075.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("x")?);
                            s.push(e.get("tube_start_y")?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("x")?);
                            s.push(e.get("straight_end_y")?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("x")?);
                            s.push(Val::Float(578.0f64));
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "truediv",
                                binary(
                                    "add",
                                    binary("mul", Val::Float(2.0f64), e.get("x")?)?,
                                    e.get("pack_x")?,
                                )?,
                                Val::Float(3.0f64),
                            )?);
                            s.push(Val::Float(598.0f64));
                            s.push(binary(
                                "truediv",
                                binary(
                                    "add",
                                    binary("mul", Val::Float(2.0f64), e.get("z")?)?,
                                    e.get("pack_z")?,
                                )?,
                                Val::Float(3.0f64),
                            )?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("pack_x")?);
                            s.push(e.get("pack_y")?);
                            s.push(e.get("pack_z")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("pack_x")?);
                            s.push(e.get("tail_y")?);
                            s.push(e.get("pack_z")?);
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    });
                    args1075.push(binary(
                        "truediv",
                        e.get("ports")?
                            .get(e.get("which")?)?
                            .get(Val::Str("diam".into()))?,
                        Val::Float(2.0f64),
                    )?);
                    fun1077.call(args1075, kw1076)?
                };
                e.set("tube", assigned1074.clone())?;
                {
                    let fun1080 = e.get("umbilical")?.attr("add")?;
                    let mut args1078 = Vec::new();
                    let mut kw1079 = Vec::new();
                    args1078.push(e.get("tube")?);
                    kw1079.push(("name".into(), {
                        let mut str1081 = String::new();
                        str1081.push_str("wall-end-tube-");
                        str1081.push_str(&format(&e.get("which")?, &String::new())?);
                        Val::Str(str1081)
                    }));
                    kw1079.push(("color".into(), e.get("tube_colors")?.get(e.get("which")?)?));
                    fun1080.call(args1078, kw1079)?
                };
                let assigned1082 = {
                    let fun1085 = e.get("split_collar")?;
                    let mut args1083 = Vec::new();
                    let mut kw1084 = Vec::new();
                    args1083.push(e.get("which")?);
                    fun1085.call(args1083, kw1084)?
                };
                let unpack1086 = unpack(assigned1082.clone(), 2)?;
                e.set("collar", unpack1086[0].clone())?;
                e.set("words", unpack1086[1].clone())?;
                let assigned1087 = {
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(binary(
                        "add",
                        e.get("tube_start_y")?,
                        e.get("collar_tip_setback")?,
                    )?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                };
                e.set("move", assigned1087.clone())?;
                {
                    let fun1090 = e.get("umbilical")?.attr("add")?;
                    let mut args1088 = Vec::new();
                    let mut kw1089 = Vec::new();
                    args1088.push({
                        let fun1093 = e.get("collar")?.attr("translate")?;
                        let mut args1091 = Vec::new();
                        let mut kw1092 = Vec::new();
                        args1091.push(e.get("move")?);
                        fun1093.call(args1091, kw1092)?
                    });
                    kw1089.push(("name".into(), {
                        let mut str1094 = String::new();
                        str1094.push_str("wall-end-collar-");
                        str1094.push_str(&format(&e.get("which")?, &String::new())?);
                        Val::Str(str1094)
                    }));
                    kw1089.push((
                        "color".into(),
                        e.get("collar_colors")?.get(e.get("which")?)?,
                    ));
                    fun1090.call(args1088, kw1089)?
                };
                {
                    let fun1097 = e.get("umbilical")?.attr("add")?;
                    let mut args1095 = Vec::new();
                    let mut kw1096 = Vec::new();
                    args1095.push({
                        let fun1100 = e.get("words")?.attr("translate")?;
                        let mut args1098 = Vec::new();
                        let mut kw1099 = Vec::new();
                        args1098.push(e.get("move")?);
                        fun1100.call(args1098, kw1099)?
                    });
                    kw1096.push(("name".into(), {
                        let mut str1101 = String::new();
                        str1101.push_str("wall-end-collar-");
                        str1101.push_str(&format(&e.get("which")?, &String::new())?);
                        str1101.push_str("-word");
                        Val::Str(str1101)
                    }));
                    kw1096.push((
                        "color".into(),
                        e.get("collar_word_colors")?.get(e.get("which")?)?,
                    ));
                    fun1097.call(args1095, kw1096)?
                };
            }
            let assigned1102 = e
                .get("facts")?
                .get(Val::Str("constants".into()))?
                .get(Val::Str("KEYSTONE_STATION".into()))?;
            let unpack1103 = unpack(assigned1102.clone(), 2)?;
            e.set("jack_x", unpack1103[0].clone())?;
            e.set("jack_station_z", unpack1103[1].clone())?;
            let assigned1104 = e
                .get("facts")?
                .get(Val::Str("bodies".into()))?
                .get(Val::Str("keystone-jack".into()))?
                .get(Val::Int(4i64))?;
            e.set("jack_face_y", assigned1104.clone())?;
            let assigned1105 = binary("sub", e.get("jack_station_z")?, Val::Float(1.0f64))?;
            e.set("jack_port_z", assigned1105.clone())?;
            let assigned1106 = Val::Float(9.0f64);
            e.set("plug_w", assigned1106.clone())?;
            let assigned1107 = Val::Float(6.45f64);
            e.set("plug_h", assigned1107.clone())?;
            let assigned1108 = binary("sub", e.get("jack_face_y")?, Val::Float(6.2f64))?;
            e.set("plug_y0", assigned1108.clone())?;
            let assigned1109 = Val::Float(21.0f64);
            e.set("plug_depth", assigned1109.clone())?;
            let assigned1110 = {
                let fun1113 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args1111 = Vec::new();
                let mut kw1112 = Vec::new();
                args1111.push(e.get("plug_w")?);
                args1111.push(e.get("plug_depth")?);
                args1111.push(e.get("plug_h")?);
                args1111.push({
                    let fun1116 = e.get("cq")?.attr("Vector")?;
                    let mut args1114 = Vec::new();
                    let mut kw1115 = Vec::new();
                    args1114.push(binary(
                        "sub",
                        e.get("jack_x")?,
                        binary("truediv", e.get("plug_w")?, Val::Float(2.0f64))?,
                    )?);
                    args1114.push(e.get("plug_y0")?);
                    args1114.push(binary(
                        "sub",
                        e.get("jack_port_z")?,
                        binary("truediv", e.get("plug_h")?, Val::Float(2.0f64))?,
                    )?);
                    fun1116.call(args1114, kw1115)?
                });
                fun1113.call(args1111, kw1112)?
            };
            e.set("plug", assigned1110.clone())?;
            let assigned1117 = {
                let fun1120 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args1118 = Vec::new();
                let mut kw1119 = Vec::new();
                args1118.push(Val::Float(7.8f64));
                args1118.push(Val::Float(5.5f64));
                args1118.push(Val::Float(5.5f64));
                args1118.push({
                    let fun1123 = e.get("cq")?.attr("Vector")?;
                    let mut args1121 = Vec::new();
                    let mut kw1122 = Vec::new();
                    args1121.push(binary("sub", e.get("jack_x")?, Val::Float(3.9f64))?);
                    args1121.push(binary("add", e.get("plug_y0")?, e.get("plug_depth")?)?);
                    args1121.push(binary("sub", e.get("jack_port_z")?, Val::Float(2.75f64))?);
                    fun1123.call(args1121, kw1122)?
                });
                fun1120.call(args1118, kw1119)?
            };
            e.set("boot", assigned1117.clone())?;
            {
                let fun1126 = e.get("umbilical")?.attr("add")?;
                let mut args1124 = Vec::new();
                let mut kw1125 = Vec::new();
                args1124.push({
                    let fun1129 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                    let mut args1127 = Vec::new();
                    let mut kw1128 = Vec::new();
                    args1127.push({
                        let mut s = Vec::new();
                        s.push(e.get("plug")?);
                        s.push(e.get("boot")?);
                        Val::list(s)
                    });
                    fun1129.call(args1127, kw1128)?
                });
                kw1125.push(("name".into(), Val::Str("wall-end-rj11-plug-body".into())));
                kw1125.push(("color".into(), e.get("plug_body")?));
                fun1126.call(args1124, kw1125)?
            };
            let assigned1130 = binary(
                "sub",
                e.get("jack_port_z")?,
                binary("truediv", e.get("plug_h")?, Val::Float(2.0f64))?,
            )?;
            e.set("latch_z", assigned1130.clone())?;
            let assigned1131 = {
                let fun1134 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args1132 = Vec::new();
                let mut kw1133 = Vec::new();
                args1132.push(Val::Float(3.4f64));
                args1132.push(Val::Float(12.0f64));
                args1132.push(Val::Float(0.75f64));
                args1132.push({
                    let fun1137 = e.get("cq")?.attr("Vector")?;
                    let mut args1135 = Vec::new();
                    let mut kw1136 = Vec::new();
                    args1135.push(binary("sub", e.get("jack_x")?, Val::Float(1.7f64))?);
                    args1135.push(binary("add", e.get("plug_y0")?, Val::Float(4.0f64))?);
                    args1135.push(binary("sub", e.get("latch_z")?, Val::Float(0.75f64))?);
                    fun1137.call(args1135, kw1136)?
                });
                fun1134.call(args1132, kw1133)?
            };
            e.set("latch_tongue", assigned1131.clone())?;
            let assigned1138 = {
                let fun1141 = {
                    let fun1144 = {
                        let fun1147 = {
                            let fun1150 = {
                                let fun1153 = {
                                    let fun1156 = e.get("cq")?.attr("Workplane")?;
                                    let mut args1154 = Vec::new();
                                    let mut kw1155 = Vec::new();
                                    args1154.push(Val::Str("YZ".into()));
                                    fun1156.call(args1154, kw1155)?
                                }
                                .attr("polyline")?;
                                let mut args1151 = Vec::new();
                                let mut kw1152 = Vec::new();
                                args1151.push({
                                    let mut s = Vec::new();
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(binary(
                                            "add",
                                            e.get("plug_y0")?,
                                            Val::Float(10.0f64),
                                        )?);
                                        s.push(binary(
                                            "sub",
                                            e.get("latch_z")?,
                                            Val::Float(0.75f64),
                                        )?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(binary(
                                            "add",
                                            e.get("plug_y0")?,
                                            Val::Float(16.0f64),
                                        )?);
                                        s.push(binary(
                                            "sub",
                                            e.get("latch_z")?,
                                            Val::Float(0.75f64),
                                        )?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(binary(
                                            "add",
                                            e.get("plug_y0")?,
                                            Val::Float(16.0f64),
                                        )?);
                                        s.push(binary(
                                            "sub",
                                            e.get("latch_z")?,
                                            Val::Float(2.35f64),
                                        )?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(binary(
                                            "add",
                                            e.get("plug_y0")?,
                                            Val::Float(10.0f64),
                                        )?);
                                        s.push(binary(
                                            "sub",
                                            e.get("latch_z")?,
                                            Val::Float(0.75f64),
                                        )?);
                                        Val::tuple(s)
                                    });
                                    Val::list(s)
                                });
                                fun1153.call(args1151, kw1152)?
                            }
                            .attr("wire")?;
                            let mut args1148 = Vec::new();
                            let mut kw1149 = Vec::new();
                            fun1150.call(args1148, kw1149)?
                        }
                        .attr("extrude")?;
                        let mut args1145 = Vec::new();
                        let mut kw1146 = Vec::new();
                        args1145.push(Val::Float(3.4f64));
                        fun1147.call(args1145, kw1146)?
                    }
                    .attr("translate")?;
                    let mut args1142 = Vec::new();
                    let mut kw1143 = Vec::new();
                    args1142.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("jack_x")?, Val::Float(1.7f64))?);
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun1144.call(args1142, kw1143)?
                }
                .attr("val")?;
                let mut args1139 = Vec::new();
                let mut kw1140 = Vec::new();
                fun1141.call(args1139, kw1140)?
            };
            e.set("latch_ramp", assigned1138.clone())?;
            {
                let fun1159 = e.get("umbilical")?.attr("add")?;
                let mut args1157 = Vec::new();
                let mut kw1158 = Vec::new();
                args1157.push({
                    let fun1162 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                    let mut args1160 = Vec::new();
                    let mut kw1161 = Vec::new();
                    args1160.push({
                        let mut s = Vec::new();
                        s.push(e.get("latch_tongue")?);
                        s.push(e.get("latch_ramp")?);
                        Val::list(s)
                    });
                    fun1162.call(args1160, kw1161)?
                });
                kw1158.push(("name".into(), Val::Str("wall-end-rj11-latch".into())));
                kw1158.push(("color".into(), e.get("plug_latch")?));
                fun1159.call(args1157, kw1158)?
            };
            for item1163 in {
                let fun1177 = e.get("enumerate")?;
                let mut args1175 = Vec::new();
                let mut kw1176 = Vec::new();
                args1175.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(2.7f64))?);
                    s.push(unary("neg", Val::Float(0.9f64))?);
                    s.push(Val::Float(0.9f64));
                    s.push(Val::Float(2.7f64));
                    Val::tuple(s)
                });
                kw1176.push(("start".into(), Val::Int(1i64)));
                fun1177.call(args1175, kw1176)?
            }
            .iter()?
            {
                let unpack1178 = unpack(item1163, 2)?;
                e.set("index", unpack1178[0].clone())?;
                e.set("contact_x", unpack1178[1].clone())?;
                let assigned1164 = {
                    let fun1167 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                    let mut args1165 = Vec::new();
                    let mut kw1166 = Vec::new();
                    args1165.push(Val::Float(0.48f64));
                    args1165.push(Val::Float(7.0f64));
                    args1165.push(Val::Float(0.18f64));
                    args1165.push({
                        let fun1170 = e.get("cq")?.attr("Vector")?;
                        let mut args1168 = Vec::new();
                        let mut kw1169 = Vec::new();
                        args1168.push(binary(
                            "sub",
                            binary("add", e.get("jack_x")?, e.get("contact_x")?)?,
                            Val::Float(0.24f64),
                        )?);
                        args1168.push(binary("add", e.get("plug_y0")?, Val::Float(0.4f64))?);
                        args1168.push(binary(
                            "sub",
                            binary(
                                "add",
                                e.get("jack_port_z")?,
                                binary("truediv", e.get("plug_h")?, Val::Float(2.0f64))?,
                            )?,
                            Val::Float(0.18f64),
                        )?);
                        fun1170.call(args1168, kw1169)?
                    });
                    fun1167.call(args1165, kw1166)?
                };
                e.set("contact", assigned1164.clone())?;
                {
                    let fun1173 = e.get("umbilical")?.attr("add")?;
                    let mut args1171 = Vec::new();
                    let mut kw1172 = Vec::new();
                    args1171.push(e.get("contact")?);
                    kw1172.push(("name".into(), {
                        let mut str1174 = String::new();
                        str1174.push_str("wall-end-rj11-contact-");
                        str1174.push_str(&format(&e.get("index")?, &String::new())?);
                        Val::Str(str1174)
                    }));
                    kw1172.push(("color".into(), e.get("contact_gold")?));
                    fun1173.call(args1171, kw1172)?
                };
            }
            let assigned1179 = binary(
                "add",
                binary("add", e.get("plug_y0")?, e.get("plug_depth")?)?,
                Val::Float(5.5f64),
            )?;
            e.set("ribbon_start_y", assigned1179.clone())?;
            let assigned1180 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("jack_x")?);
                    s.push(e.get("ribbon_start_y")?);
                    s.push(e.get("jack_port_z")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("jack_x")?);
                    s.push(Val::Float(548.0f64));
                    s.push(e.get("jack_port_z")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(42.0f64))?);
                    s.push(Val::Float(590.0f64));
                    s.push(Val::Float(298.0f64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(48.5f64))?);
                    s.push(e.get("pack_y")?);
                    s.push(Val::Float(294.0f64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(48.5f64))?);
                    s.push(e.get("tail_y")?);
                    s.push(Val::Float(294.0f64));
                    Val::tuple(s)
                });
                Val::tuple(s)
            };
            e.set("ribbon_points", assigned1180.clone())?;
            let assigned1181 = {
                let fun1184 = e.get("ribbon_sweep")?;
                let mut args1182 = Vec::new();
                let mut kw1183 = Vec::new();
                args1182.push(e.get("ribbon_points")?);
                args1182.push(Val::Float(4.0f64));
                args1182.push(Val::Float(1.2f64));
                fun1184.call(args1182, kw1183)?
            };
            e.set("ribbon", assigned1181.clone())?;
            let assigned1185 = {
                let fun1188 = e.get("ribbon_sweep")?;
                let mut args1186 = Vec::new();
                let mut kw1187 = Vec::new();
                args1186.push({
                    let fun1191 = e.get("tuple")?;
                    let mut args1189 = Vec::new();
                    let mut kw1190 = Vec::new();
                    args1189.push({
                        let e = e.child();
                        let out1192 = Val::list(vec![]);
                        for item1193 in e.get("ribbon_points")?.iter()? {
                            let unpack1194 = unpack(item1193, 3)?;
                            e.set("x", unpack1194[0].clone())?;
                            e.set("y", unpack1194[1].clone())?;
                            e.set("z", unpack1194[2].clone())?;
                            out1192.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary("add", e.get("x")?, Val::Float(1.55f64))?);
                                    s.push(e.get("y")?);
                                    s.push(binary("add", e.get("z")?, Val::Float(0.63f64))?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                        out1192
                    });
                    fun1191.call(args1189, kw1190)?
                });
                args1186.push(Val::Float(0.28f64));
                args1186.push(Val::Float(0.08f64));
                fun1188.call(args1186, kw1187)?
            };
            e.set("ribbon_mark", assigned1185.clone())?;
            {
                let fun1197 = e.get("umbilical")?.attr("add")?;
                let mut args1195 = Vec::new();
                let mut kw1196 = Vec::new();
                args1195.push(e.get("ribbon")?);
                kw1196.push(("name".into(), Val::Str("wall-end-sig6-ribbon".into())));
                kw1196.push(("color".into(), e.get("ribbon_black")?));
                fun1197.call(args1195, kw1196)?
            };
            {
                let fun1200 = e.get("umbilical")?.attr("add")?;
                let mut args1198 = Vec::new();
                let mut kw1199 = Vec::new();
                args1198.push(e.get("ribbon_mark")?);
                kw1199.push(("name".into(), Val::Str("wall-end-sig6-ribbon-mark".into())));
                kw1199.push(("color".into(), e.get("ribbon_edge")?));
                fun1200.call(args1198, kw1199)?
            };
            // state
            e.set("state", {
                let params = vec![
                    ("name".into(), None, false),
                    ("shift_y".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned1201 = {
                        let fun1204 = e.get("borrow")?;
                        let mut args1202 = Vec::new();
                        let mut kw1203 = Vec::new();
                        args1202.push({
                            let fun1207 = e.get("cq")?.attr("Assembly")?;
                            let mut args1205 = Vec::new();
                            let mut kw1206 = Vec::new();
                            kw1206.push(("name".into(), e.get("name")?));
                            fun1207.call(args1205, kw1206)?
                        });
                        args1202.push(e.get("rear_bodies")?);
                        fun1204.call(args1202, kw1203)?
                    };
                    e.set("scene", assigned1201.clone())?;
                    {
                        let fun1210 = e.get("scene")?.attr("add")?;
                        let mut args1208 = Vec::new();
                        let mut kw1209 = Vec::new();
                        args1208.push(e.get("umbilical")?);
                        kw1209.push(("name".into(), {
                            let mut str1211 = String::new();
                            str1211.push_str(&format(&e.get("name")?, &String::new())?);
                            str1211.push_str("-umbilical");
                            Val::Str(str1211)
                        }));
                        kw1209.push(("loc".into(), {
                            let fun1214 = e.get("cq")?.attr("Location")?;
                            let mut args1212 = Vec::new();
                            let mut kw1213 = Vec::new();
                            args1212.push({
                                let fun1217 = e.get("cq")?.attr("Vector")?;
                                let mut args1215 = Vec::new();
                                let mut kw1216 = Vec::new();
                                args1215.push(Val::Float(0.0f64));
                                args1215.push(e.get("shift_y")?);
                                args1215.push(Val::Float(0.0f64));
                                fun1217.call(args1215, kw1216)?
                            });
                            fun1214.call(args1212, kw1213)?
                        }));
                        fun1210.call(args1208, kw1209)?
                    };
                    return Ok({
                        let fun1220 = e.get("_export_colored")?;
                        let mut args1218 = Vec::new();
                        let mut kw1219 = Vec::new();
                        args1218.push(e.get("scene")?);
                        args1218.push(binary("truediv", e.get("work")?, {
                            let mut str1221 = String::new();
                            str1221.push_str(&format(&e.get("name")?, &String::new())?);
                            str1221.push_str(".step");
                            Val::Str(str1221)
                        })?);
                        kw1219.push(("mesh".into(), Val::Bool(true)));
                        fun1220.call(args1218, kw1219)?
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned1222 = {
                let fun1225 = e.get("borrow")?;
                let mut args1223 = Vec::new();
                let mut kw1224 = Vec::new();
                args1223.push({
                    let fun1228 = e.get("cq")?.attr("Assembly")?;
                    let mut args1226 = Vec::new();
                    let mut kw1227 = Vec::new();
                    kw1227.push(("name".into(), Val::Str("the-back-face".into())));
                    fun1228.call(args1226, kw1227)?
                });
                args1223.push(e.get("rear_bodies")?);
                fun1225.call(args1223, kw1224)?
            };
            e.set("rear", assigned1222.clone())?;
            let assigned1229 = {
                let fun1232 = e.get("_export_colored")?;
                let mut args1230 = Vec::new();
                let mut kw1231 = Vec::new();
                args1230.push(e.get("rear")?);
                args1230.push(binary(
                    "truediv",
                    e.get("work")?,
                    Val::Str("the-back-face.step".into()),
                )?);
                kw1231.push(("mesh".into(), Val::Bool(true)));
                fun1232.call(args1230, kw1231)?
            };
            e.set("rear_step", assigned1229.clone())?;
            let assigned1233 = {
                let fun1236 = e.get("state")?;
                let mut args1234 = Vec::new();
                let mut kw1235 = Vec::new();
                args1234.push(Val::Str("connect-rear-open".into()));
                args1234.push(e.get("CONNECT_OPEN_GAP")?);
                fun1236.call(args1234, kw1235)?
            };
            e.set("open_step", assigned1233.clone())?;
            let assigned1237 = {
                let fun1240 = e.get("state")?;
                let mut args1238 = Vec::new();
                let mut kw1239 = Vec::new();
                args1238.push(Val::Str("connect-rear-connected".into()));
                args1238.push(Val::Float(0.0f64));
                fun1240.call(args1238, kw1239)?
            };
            e.set("connected_step", assigned1237.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("the-back-face".into()), e.get("rear_step")?)?;
                d.set(Val::Str("connect-rear-open".into()), e.get("open_step")?)?;
                d.set(
                    Val::Str("connect-rear-connected".into()),
                    e.get("connected_step")?,
                )?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // _job
    e.set("_job", {
        let params = vec![
            ("step".into(), None, false),
            ("out".into(), None, false),
            ("cam".into(), None, false),
            ("target".into(), Some(Val::None), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1241 = {
                let fun1244 = e.get("Path")?;
                let mut args1242 = Vec::new();
                let mut kw1243 = Vec::new();
                args1242.push(e.get("out")?);
                fun1244.call(args1242, kw1243)?
            };
            e.set("output", assigned1241.clone())?;
            if unary("not", {
                let fun1247 = e.get("output")?.attr("is_absolute")?;
                let mut args1245 = Vec::new();
                let mut kw1246 = Vec::new();
                fun1247.call(args1245, kw1246)?
            })?
            .truthy()?
            {
                let assigned1248 = binary("truediv", e.get("ART")?, e.get("output")?)?;
                e.set("output", assigned1248.clone())?;
            }
            let assigned1249 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("step".into()), {
                    let fun1252 = e.get("str")?;
                    let mut args1250 = Vec::new();
                    let mut kw1251 = Vec::new();
                    args1250.push({
                        let fun1255 = e.get("step")?.attr("relative_to")?;
                        let mut args1253 = Vec::new();
                        let mut kw1254 = Vec::new();
                        args1253.push(e.get("HARDWARE")?);
                        fun1255.call(args1253, kw1254)?
                    });
                    fun1252.call(args1250, kw1251)?
                })?;
                d.set(Val::Str("payload".into()), {
                    let fun1258 = e.get("str")?;
                    let mut args1256 = Vec::new();
                    let mut kw1257 = Vec::new();
                    args1256.push({
                        let fun1261 = e.get("Path")?;
                        let mut args1259 = Vec::new();
                        let mut kw1260 = Vec::new();
                        args1259.push({
                            let mut str1262 = String::new();
                            str1262.push_str(&format(&e.get("step")?, &String::new())?);
                            str1262.push_str(".mesh");
                            Val::Str(str1262)
                        });
                        fun1261.call(args1259, kw1260)?
                    });
                    fun1258.call(args1256, kw1257)?
                })?;
                d.set(Val::Str("out".into()), {
                    let fun1265 = e.get("str")?;
                    let mut args1263 = Vec::new();
                    let mut kw1264 = Vec::new();
                    args1263.push(e.get("output")?);
                    fun1265.call(args1263, kw1264)?
                })?;
                d.set(Val::Str("cam".into()), e.get("cam")?)?;
                d.set(Val::Str("up".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("size".into()), Val::Str("2400x2400".into()))?;
                d.set(Val::Str("bg".into()), Val::Str("#ffffff".into()))?;
                d.set(Val::Str("trim".into()), Val::Bool(true))?;
                d.set(Val::Str("solid".into()), Val::Bool(true))?;
                d.set(Val::Str("ortho".into()), Val::Bool(true))?;
                d
            };
            e.set("job", assigned1249.clone())?;
            if {
                let v1266 = e.get("target")?;
                let v1267 = Val::None;
                Val::Bool(compare("is_not", v1266.clone(), v1267.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned1268 = e.get("target")?;
                e.get("job")?
                    .set(Val::Str("target".into()), assigned1268.clone())?;
            }
            return Ok(e.get("job")?);
            Ok(Val::None)
        })
    })?;
    // _canonicalize_png
    e.set("_canonicalize_png", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let context1269 = {
                let fun1272 = e.get("Image")?.attr("open")?;
                let mut args1270 = Vec::new();
                let mut kw1271 = Vec::new();
                args1270.push(e.get("path")?);
                fun1272.call(args1270, kw1271)?
            };
            e.set(
                "image",
                context1269.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result1280 = (|| -> Result<Flow> {
                let assigned1273 = {
                    let fun1276 = e.get("image")?.attr("convert")?;
                    let mut args1274 = Vec::new();
                    let mut kw1275 = Vec::new();
                    args1274.push(Val::Str("RGBA".into()));
                    fun1276.call(args1274, kw1275)?
                };
                e.set("pixels", assigned1273.clone())?;
                {
                    let fun1279 = e.get("pixels")?.attr("save")?;
                    let mut args1277 = Vec::new();
                    let mut kw1278 = Vec::new();
                    args1277.push(e.get("path")?);
                    kw1278.push(("format".into(), Val::Str("PNG".into())));
                    kw1278.push(("compress_level".into(), Val::Int(9i64)));
                    kw1278.push(("optimize".into(), Val::Bool(false)));
                    fun1279.call(args1277, kw1278)?
                };
                Ok(Flow::Continue)
            })();
            context1269
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result1280? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            Ok(Val::None)
        })
    })?;
    // _crop
    e.set("_crop", {
        let params = vec![
            ("source".into(), None, false),
            ("geometry".into(), None, false),
            ("target".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1281 = {
                let v1285 = {
                    let fun1288 = e.get("shutil")?.attr("which")?;
                    let mut args1286 = Vec::new();
                    let mut kw1287 = Vec::new();
                    args1286.push(Val::Str("magick".into()));
                    fun1288.call(args1286, kw1287)?
                };
                if v1285.truthy()? {
                    v1285
                } else {
                    {
                        let fun1284 = e.get("shutil")?.attr("which")?;
                        let mut args1282 = Vec::new();
                        let mut kw1283 = Vec::new();
                        args1282.push(Val::Str("convert".into()));
                        fun1284.call(args1282, kw1283)?
                    }
                }
            };
            e.set("magick", assigned1281.clone())?;
            if unary("not", e.get("magick")?)?.truthy()? {
                return Ok(Val::None);
            }
            let assigned1289 = {
                let fun1292 = e.get("Path")?;
                let mut args1290 = Vec::new();
                let mut kw1291 = Vec::new();
                args1290.push(e.get("source")?);
                fun1292.call(args1290, kw1291)?
            };
            e.set("source_path", assigned1289.clone())?;
            let assigned1293 = {
                let fun1296 = e.get("Path")?;
                let mut args1294 = Vec::new();
                let mut kw1295 = Vec::new();
                args1294.push(e.get("target")?);
                fun1296.call(args1294, kw1295)?
            };
            e.set("target_path", assigned1293.clone())?;
            if unary("not", {
                let fun1299 = e.get("source_path")?.attr("is_absolute")?;
                let mut args1297 = Vec::new();
                let mut kw1298 = Vec::new();
                fun1299.call(args1297, kw1298)?
            })?
            .truthy()?
            {
                let assigned1300 = binary("truediv", e.get("ART")?, e.get("source_path")?)?;
                e.set("source_path", assigned1300.clone())?;
            }
            if unary("not", {
                let fun1303 = e.get("target_path")?.attr("is_absolute")?;
                let mut args1301 = Vec::new();
                let mut kw1302 = Vec::new();
                fun1303.call(args1301, kw1302)?
            })?
            .truthy()?
            {
                let assigned1304 = binary("truediv", e.get("ART")?, e.get("target_path")?)?;
                e.set("target_path", assigned1304.clone())?;
            }
            {
                let fun1307 = e.get("subprocess")?.attr("run")?;
                let mut args1305 = Vec::new();
                let mut kw1306 = Vec::new();
                args1305.push({
                    let mut s = Vec::new();
                    s.push(e.get("magick")?);
                    s.push({
                        let fun1310 = e.get("str")?;
                        let mut args1308 = Vec::new();
                        let mut kw1309 = Vec::new();
                        args1308.push(e.get("source_path")?);
                        fun1310.call(args1308, kw1309)?
                    });
                    s.push(Val::Str("-crop".into()));
                    s.push(e.get("geometry")?);
                    s.push(Val::Str("+repage".into()));
                    s.push(Val::Str("-strip".into()));
                    s.push({
                        let fun1313 = e.get("str")?;
                        let mut args1311 = Vec::new();
                        let mut kw1312 = Vec::new();
                        args1311.push(e.get("target_path")?);
                        fun1313.call(args1311, kw1312)?
                    });
                    Val::list(s)
                });
                kw1306.push(("check".into(), Val::Bool(true)));
                fun1307.call(args1305, kw1306)?
            };
            {
                let fun1316 = e.get("_canonicalize_png")?;
                let mut args1314 = Vec::new();
                let mut kw1315 = Vec::new();
                args1314.push(e.get("target_path")?);
                fun1316.call(args1314, kw1315)?
            };
            {
                let fun1319 = e.get("note_write")?;
                let mut args1317 = Vec::new();
                let mut kw1318 = Vec::new();
                args1317.push(e.get("target_path")?);
                fun1319.call(args1317, kw1318)?
            };
            Ok(Val::None)
        })
    })?;
    // _clear_connected_background
    e.set("_clear_connected_background", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1320 = {
                let v1324 = {
                    let fun1327 = e.get("shutil")?.attr("which")?;
                    let mut args1325 = Vec::new();
                    let mut kw1326 = Vec::new();
                    args1325.push(Val::Str("magick".into()));
                    fun1327.call(args1325, kw1326)?
                };
                if v1324.truthy()? {
                    v1324
                } else {
                    {
                        let fun1323 = e.get("shutil")?.attr("which")?;
                        let mut args1321 = Vec::new();
                        let mut kw1322 = Vec::new();
                        args1321.push(Val::Str("convert".into()));
                        fun1323.call(args1321, kw1322)?
                    }
                }
            };
            e.set("magick", assigned1320.clone())?;
            if unary("not", e.get("magick")?)?.truthy()? {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun1330 = e.get("RuntimeError")?;
                        let mut args1328 = Vec::new();
                        let mut kw1329 = Vec::new();
                        args1328.push(Val::Str(
                            "ImageMagick is required to clear CAD picture backgrounds".into(),
                        ));
                        fun1330.call(args1328, kw1329)?
                    })?
                );
            }
            let assigned1331 = if {
                let v1335 = {
                    let fun1334 = e.get("Path")?;
                    let mut args1332 = Vec::new();
                    let mut kw1333 = Vec::new();
                    args1332.push(e.get("magick")?);
                    fun1334.call(args1332, kw1333)?
                }
                .attr("name")?;
                let v1336 = Val::Str("magick".into());
                Val::Bool(compare("eq", v1335.clone(), v1336.clone())?.truthy()?)
            }
            .truthy()?
            {
                Val::Str("alpha".into())
            } else {
                Val::Str("matte".into())
            };
            e.set("primitive", assigned1331.clone())?;
            {
                let fun1339 = e.get("subprocess")?.attr("run")?;
                let mut args1337 = Vec::new();
                let mut kw1338 = Vec::new();
                args1337.push({
                    let mut s = Vec::new();
                    s.push(e.get("magick")?);
                    s.push({
                        let fun1342 = e.get("str")?;
                        let mut args1340 = Vec::new();
                        let mut kw1341 = Vec::new();
                        args1340.push(e.get("path")?);
                        fun1342.call(args1340, kw1341)?
                    });
                    s.push(Val::Str("-bordercolor".into()));
                    s.push(Val::Str("white".into()));
                    s.push(Val::Str("-border".into()));
                    s.push(Val::Str("1".into()));
                    s.push(Val::Str("-alpha".into()));
                    s.push(Val::Str("set".into()));
                    s.push(Val::Str("-channel".into()));
                    s.push(Val::Str("RGBA".into()));
                    s.push(Val::Str("-fuzz".into()));
                    s.push(Val::Str("3%".into()));
                    s.push(Val::Str("-fill".into()));
                    s.push(Val::Str("none".into()));
                    s.push(Val::Str("-draw".into()));
                    s.push({
                        let mut str1343 = String::new();
                        str1343.push_str(&format(&e.get("primitive")?, &String::new())?);
                        str1343.push_str(" 0,0 floodfill");
                        Val::Str(str1343)
                    });
                    s.push(Val::Str("-shave".into()));
                    s.push(Val::Str("1x1".into()));
                    s.push(Val::Str("-strip".into()));
                    s.push({
                        let fun1346 = e.get("str")?;
                        let mut args1344 = Vec::new();
                        let mut kw1345 = Vec::new();
                        args1344.push(e.get("path")?);
                        fun1346.call(args1344, kw1345)?
                    });
                    Val::list(s)
                });
                kw1338.push(("check".into(), Val::Bool(true)));
                fun1339.call(args1337, kw1338)?
            };
            {
                let fun1349 = e.get("_canonicalize_png")?;
                let mut args1347 = Vec::new();
                let mut kw1348 = Vec::new();
                args1347.push(e.get("path")?);
                fun1349.call(args1347, kw1348)?
            };
            {
                let fun1352 = e.get("note_write")?;
                let mut args1350 = Vec::new();
                let mut kw1351 = Vec::new();
                args1350.push(e.get("path")?);
                fun1352.call(args1350, kw1351)?
            };
            Ok(Val::None)
        })
    })?;
    // _shave_render_frame
    e.set("_shave_render_frame", {
        let params = vec![("path".into(), None, false), ("margin".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let context1353 = {
                let fun1356 = e.get("Image")?.attr("open")?;
                let mut args1354 = Vec::new();
                let mut kw1355 = Vec::new();
                args1354.push(e.get("path")?);
                fun1356.call(args1354, kw1355)?
            };
            e.set(
                "image",
                context1353.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result1378 = (|| -> Result<Flow> {
                let assigned1357 = if {
                    let v1358 = e.get("path")?.attr("name")?;
                    let v1359 = Val::Str("mount-drop.png".into());
                    Val::Bool(compare("eq", v1358.clone(), v1359.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("MOUNT_DROP_TRIM_TOP")?
                } else {
                    e.get("MOUNT_FRAME_TRIM_TOP")?
                };
                e.set("trim_top", assigned1357.clone())?;
                let assigned1360 = binary("add", e.get("margin")?, e.get("trim_top")?)?;
                e.set("top", assigned1360.clone())?;
                let assigned1361 = binary(
                    "sub",
                    binary("sub", e.get("image")?.attr("height")?, e.get("margin")?)?,
                    e.get("MOUNT_FRAME_TRIM_BOTTOM")?,
                )?;
                e.set("bottom", assigned1361.clone())?;
                if {
                    let v1364 = {
                        let v1365 = e.get("image")?.attr("width")?;
                        let v1366 = binary("mul", Val::Int(2i64), e.get("margin")?)?;
                        Val::Bool(compare("le", v1365.clone(), v1366.clone())?.truthy()?)
                    };
                    if v1364.truthy()? {
                        v1364
                    } else {
                        {
                            let v1362 = e.get("bottom")?;
                            let v1363 = e.get("top")?;
                            Val::Bool(compare("le", v1362.clone(), v1363.clone())?.truthy()?)
                        }
                    }
                }
                .truthy()?
                {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let fun1369 = e.get("ValueError")?;
                            let mut args1367 = Vec::new();
                            let mut kw1368 = Vec::new();
                            args1367.push({
                                let mut str1370 = String::new();
                                str1370.push_str("cannot shave ");
                                str1370.push_str(&format(&e.get("margin")?, &String::new())?);
                                str1370.push_str("px from ");
                                str1370.push_str(&format(
                                    &e.get("image")?.attr("width")?,
                                    &String::new(),
                                )?);
                                str1370.push_str("x");
                                str1370.push_str(&format(
                                    &e.get("image")?.attr("height")?,
                                    &String::new(),
                                )?);
                                str1370.push_str(": ");
                                str1370.push_str(&format(&e.get("path")?, &String::new())?);
                                Val::Str(str1370)
                            });
                            fun1369.call(args1367, kw1368)?
                        })?
                    );
                }
                let assigned1371 = {
                    let fun1374 = e.get("image")?.attr("crop")?;
                    let mut args1372 = Vec::new();
                    let mut kw1373 = Vec::new();
                    args1372.push({
                        let mut s = Vec::new();
                        s.push(e.get("margin")?);
                        s.push(e.get("top")?);
                        s.push(binary(
                            "sub",
                            e.get("image")?.attr("width")?,
                            e.get("margin")?,
                        )?);
                        s.push(e.get("bottom")?);
                        Val::tuple(s)
                    });
                    fun1374.call(args1372, kw1373)?
                };
                e.set("cropped", assigned1371.clone())?;
                {
                    let fun1377 = e.get("cropped")?.attr("save")?;
                    let mut args1375 = Vec::new();
                    let mut kw1376 = Vec::new();
                    args1375.push(e.get("path")?);
                    kw1376.push(("format".into(), Val::Str("PNG".into())));
                    kw1376.push(("compress_level".into(), Val::Int(9i64)));
                    kw1376.push(("optimize".into(), Val::Bool(false)));
                    fun1377.call(args1375, kw1376)?
                };
                Ok(Flow::Continue)
            })();
            context1353
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result1378? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            {
                let fun1381 = e.get("_canonicalize_png")?;
                let mut args1379 = Vec::new();
                let mut kw1380 = Vec::new();
                args1379.push(e.get("path")?);
                fun1381.call(args1379, kw1380)?
            };
            {
                let fun1384 = e.get("note_write")?;
                let mut args1382 = Vec::new();
                let mut kw1383 = Vec::new();
                args1382.push(e.get("path")?);
                fun1384.call(args1382, kw1383)?
            };
            Ok(Val::None)
        })
    })?;
    // _shave_under_render_frame
    e.set("_shave_under_render_frame", {
        let params = vec![("path".into(), None, false), ("margin".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let context1385 = {
                let fun1388 = e.get("Image")?.attr("open")?;
                let mut args1386 = Vec::new();
                let mut kw1387 = Vec::new();
                args1386.push(e.get("path")?);
                fun1388.call(args1386, kw1387)?
            };
            e.set(
                "image",
                context1385.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result1405 = (|| -> Result<Flow> {
                if {
                    let v1391 = {
                        let v1392 = e.get("image")?.attr("width")?;
                        let v1393 = binary("mul", Val::Int(2i64), e.get("margin")?)?;
                        Val::Bool(compare("le", v1392.clone(), v1393.clone())?.truthy()?)
                    };
                    if v1391.truthy()? {
                        v1391
                    } else {
                        {
                            let v1389 = e.get("image")?.attr("height")?;
                            let v1390 = binary("mul", Val::Int(2i64), e.get("margin")?)?;
                            Val::Bool(compare("le", v1389.clone(), v1390.clone())?.truthy()?)
                        }
                    }
                }
                .truthy()?
                {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let fun1396 = e.get("ValueError")?;
                            let mut args1394 = Vec::new();
                            let mut kw1395 = Vec::new();
                            args1394.push({
                                let mut str1397 = String::new();
                                str1397.push_str("cannot shave ");
                                str1397.push_str(&format(&e.get("margin")?, &String::new())?);
                                str1397.push_str("px from ");
                                str1397.push_str(&format(
                                    &e.get("image")?.attr("width")?,
                                    &String::new(),
                                )?);
                                str1397.push_str("x");
                                str1397.push_str(&format(
                                    &e.get("image")?.attr("height")?,
                                    &String::new(),
                                )?);
                                str1397.push_str(": ");
                                str1397.push_str(&format(&e.get("path")?, &String::new())?);
                                Val::Str(str1397)
                            });
                            fun1396.call(args1394, kw1395)?
                        })?
                    );
                }
                let assigned1398 = {
                    let fun1401 = e.get("image")?.attr("crop")?;
                    let mut args1399 = Vec::new();
                    let mut kw1400 = Vec::new();
                    args1399.push({
                        let mut s = Vec::new();
                        s.push(e.get("margin")?);
                        s.push(e.get("margin")?);
                        s.push(binary(
                            "sub",
                            e.get("image")?.attr("width")?,
                            e.get("margin")?,
                        )?);
                        s.push(binary(
                            "sub",
                            e.get("image")?.attr("height")?,
                            e.get("margin")?,
                        )?);
                        Val::tuple(s)
                    });
                    fun1401.call(args1399, kw1400)?
                };
                e.set("cropped", assigned1398.clone())?;
                {
                    let fun1404 = e.get("cropped")?.attr("save")?;
                    let mut args1402 = Vec::new();
                    let mut kw1403 = Vec::new();
                    args1402.push(e.get("path")?);
                    kw1403.push(("format".into(), Val::Str("PNG".into())));
                    kw1403.push(("compress_level".into(), Val::Int(9i64)));
                    kw1403.push(("optimize".into(), Val::Bool(false)));
                    fun1404.call(args1402, kw1403)?
                };
                Ok(Flow::Continue)
            })();
            context1385
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result1405? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            {
                let fun1408 = e.get("_canonicalize_png")?;
                let mut args1406 = Vec::new();
                let mut kw1407 = Vec::new();
                args1406.push(e.get("path")?);
                fun1408.call(args1406, kw1407)?
            };
            {
                let fun1411 = e.get("note_write")?;
                let mut args1409 = Vec::new();
                let mut kw1410 = Vec::new();
                args1409.push(e.get("path")?);
                fun1411.call(args1409, kw1410)?
            };
            Ok(Val::None)
        })
    })?;
    // _crop_registered_connection
    e.set("_crop_registered_connection", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let context1412 = {
                let fun1415 = e.get("Image")?.attr("open")?;
                let mut args1413 = Vec::new();
                let mut kw1414 = Vec::new();
                args1413.push(e.get("path")?);
                fun1415.call(args1413, kw1414)?
            };
            e.set(
                "image",
                context1412.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result1438 = (|| -> Result<Flow> {
                if {
                    let v1425 = e.get("image")?.attr("size")?;
                    let v1426 = {
                        let fun1418 = e.get("tuple")?;
                        let mut args1416 = Vec::new();
                        let mut kw1417 = Vec::new();
                        args1416.push({
                            let fun1421 = e.get("map")?;
                            let mut args1419 = Vec::new();
                            let mut kw1420 = Vec::new();
                            args1419.push(e.get("int")?);
                            args1419.push({
                                let fun1424 = e.get("CONNECT_RENDER_SIZE")?.attr("split")?;
                                let mut args1422 = Vec::new();
                                let mut kw1423 = Vec::new();
                                args1422.push(Val::Str("x".into()));
                                fun1424.call(args1422, kw1423)?
                            });
                            fun1421.call(args1419, kw1420)?
                        });
                        fun1418.call(args1416, kw1417)?
                    };
                    Val::Bool(compare("ne", v1425.clone(), v1426.clone())?.truthy()?)
                }
                .truthy()?
                {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let fun1429 = e.get("ValueError")?;
                            let mut args1427 = Vec::new();
                            let mut kw1428 = Vec::new();
                            args1427.push({
                                let mut str1430 = String::new();
                                str1430.push_str("expected ");
                                str1430.push_str(&format(
                                    &e.get("CONNECT_RENDER_SIZE")?,
                                    &String::new(),
                                )?);
                                str1430.push_str(" rear render, found ");
                                str1430.push_str(&format(
                                    &e.get("image")?.attr("width")?,
                                    &String::new(),
                                )?);
                                str1430.push_str("x");
                                str1430.push_str(&format(
                                    &e.get("image")?.attr("height")?,
                                    &String::new(),
                                )?);
                                str1430.push_str(": ");
                                str1430.push_str(&format(&e.get("path")?, &String::new())?);
                                Val::Str(str1430)
                            });
                            fun1429.call(args1427, kw1428)?
                        })?
                    );
                }
                let assigned1431 = {
                    let fun1434 = e.get("image")?.attr("crop")?;
                    let mut args1432 = Vec::new();
                    let mut kw1433 = Vec::new();
                    args1432.push(e.get("CONNECT_CROP")?);
                    fun1434.call(args1432, kw1433)?
                };
                e.set("cropped", assigned1431.clone())?;
                {
                    let fun1437 = e.get("cropped")?.attr("save")?;
                    let mut args1435 = Vec::new();
                    let mut kw1436 = Vec::new();
                    args1435.push(e.get("path")?);
                    kw1436.push(("format".into(), Val::Str("PNG".into())));
                    kw1436.push(("compress_level".into(), Val::Int(9i64)));
                    kw1436.push(("optimize".into(), Val::Bool(false)));
                    fun1437.call(args1435, kw1436)?
                };
                Ok(Flow::Continue)
            })();
            context1412
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result1438? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            {
                let fun1441 = e.get("_canonicalize_png")?;
                let mut args1439 = Vec::new();
                let mut kw1440 = Vec::new();
                args1439.push(e.get("path")?);
                fun1441.call(args1439, kw1440)?
            };
            {
                let fun1444 = e.get("note_write")?;
                let mut args1442 = Vec::new();
                let mut kw1443 = Vec::new();
                args1442.push(e.get("path")?);
                fun1444.call(args1442, kw1443)?
            };
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![("mount_studies".into(), Some(Val::Bool(false)), true)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun1447 = e.get("ART")?.attr("mkdir")?;
                let mut args1445 = Vec::new();
                let mut kw1446 = Vec::new();
                kw1446.push(("parents".into(), Val::Bool(true)));
                kw1446.push(("exist_ok".into(), Val::Bool(true)));
                fun1447.call(args1445, kw1446)?
            };
            {
                let fun1450 = e.get("OUT")?.attr("mkdir")?;
                let mut args1448 = Vec::new();
                let mut kw1449 = Vec::new();
                kw1449.push(("parents".into(), Val::Bool(true)));
                kw1449.push(("exist_ok".into(), Val::Bool(true)));
                fun1450.call(args1448, kw1449)?
            };
            if unary("not", e.get("mount_studies")?)?.truthy()? {
                {
                    let fun1453 = e.get("note_read")?;
                    let mut args1451 = Vec::new();
                    let mut kw1452 = Vec::new();
                    args1451.push(e.get("MACHINE_MESH")?);
                    fun1453.call(args1451, kw1452)?
                };
            }
            let context1454 = {
                let fun1457 = e.get("tempfile")?.attr("TemporaryDirectory")?;
                let mut args1455 = Vec::new();
                let mut kw1456 = Vec::new();
                kw1456.push(("prefix".into(), Val::Str("installation-cad-".into())));
                kw1456.push(("dir".into(), e.get("OUT")?));
                fun1457.call(args1455, kw1456)?
            };
            e.set(
                "directory",
                context1454.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result1607 = (|| -> Result<Flow> {
                let assigned1458 = {
                    let fun1461 = e.get("Path")?;
                    let mut args1459 = Vec::new();
                    let mut kw1460 = Vec::new();
                    args1459.push(e.get("directory")?);
                    fun1461.call(args1459, kw1460)?
                };
                e.set("work", assigned1458.clone())?;
                let mod1462 = rt.import_module("_cad_art_mesh")?;
                e.set("build_steps", rt.member("_cad_art_mesh", "build_steps")?)?;
                e.set(
                    "build_connection_steps",
                    rt.member("_cad_art_mesh", "build_connection_steps")?,
                )?;
                let assigned1463 = e.namespace();
                e.set("this", assigned1463.clone())?;
                let assigned1464 = {
                    let fun1467 = e.get("build_steps")?;
                    let mut args1465 = Vec::new();
                    let mut kw1466 = Vec::new();
                    args1465.push(e.get("this")?);
                    args1465.push(e.get("work")?);
                    fun1467.call(args1465, kw1466)?
                };
                e.set("steps", assigned1464.clone())?;
                if unary("not", e.get("mount_studies")?)?.truthy()? {
                    {
                        let fun1470 = e.get("steps")?.attr("update")?;
                        let mut args1468 = Vec::new();
                        let mut kw1469 = Vec::new();
                        args1468.push({
                            let fun1473 = e.get("build_connection_steps")?;
                            let mut args1471 = Vec::new();
                            let mut kw1472 = Vec::new();
                            args1471.push(e.get("this")?);
                            args1471.push(e.get("work")?);
                            fun1473.call(args1471, kw1472)?
                        });
                        fun1470.call(args1468, kw1469)?
                    };
                }
                let assigned1474 = {
                    let mut s = Vec::new();
                    s.push({
                        let fun1477 = e.get("_job")?;
                        let mut args1475 = Vec::new();
                        let mut kw1476 = Vec::new();
                        args1475.push(e.get("steps")?.get(Val::Str("mount-drop".into()))?);
                        args1475.push(Val::Str("mount-drop.png".into()));
                        args1475.push(e.get("MOUNT_CAM")?);
                        kw1476.push(("target".into(), e.get("MOUNT_TARGET")?));
                        fun1477.call(args1475, kw1476)?
                    });
                    s.push({
                        let fun1480 = e.get("_job")?;
                        let mut args1478 = Vec::new();
                        let mut kw1479 = Vec::new();
                        args1478.push(e.get("steps")?.get(Val::Str("mount-seated".into()))?);
                        args1478.push(Val::Str("mount-seated.png".into()));
                        args1478.push(e.get("MOUNT_CAM")?);
                        kw1479.push(("target".into(), e.get("MOUNT_TARGET")?));
                        fun1480.call(args1478, kw1479)?
                    });
                    s.push({
                        let fun1483 = e.get("_job")?;
                        let mut args1481 = Vec::new();
                        let mut kw1482 = Vec::new();
                        args1481.push(e.get("steps")?.get(Val::Str("mount-slide".into()))?);
                        args1481.push(Val::Str("mount-slide.png".into()));
                        args1481.push(e.get("MOUNT_CAM")?);
                        kw1482.push(("target".into(), e.get("MOUNT_TARGET")?));
                        fun1483.call(args1481, kw1482)?
                    });
                    s.push({
                        let fun1486 = e.get("_job")?;
                        let mut args1484 = Vec::new();
                        let mut kw1485 = Vec::new();
                        args1484.push(e.get("steps")?.get(Val::Str("mount-tighten".into()))?);
                        args1484.push(Val::Str("mount-tighten.png".into()));
                        args1484.push(e.get("MOUNT_CAM")?);
                        kw1485.push(("target".into(), e.get("MOUNT_TARGET")?));
                        fun1486.call(args1484, kw1485)?
                    });
                    Val::list(s)
                };
                e.set("mount_jobs", assigned1474.clone())?;
                let assigned1487 = {
                    let mut s = Vec::new();
                    s.push({
                        let fun1490 = e.get("_job")?;
                        let mut args1488 = Vec::new();
                        let mut kw1489 = Vec::new();
                        args1488.push(
                            e.get("steps")?
                                .get(Val::Str("mount-lowered-clean".into()))?,
                        );
                        args1488.push(Val::Str("mount-lowered-clean.png".into()));
                        args1488.push(e.get("MOUNT_CAM")?);
                        kw1489.push(("target".into(), e.get("MOUNT_TARGET")?));
                        fun1490.call(args1488, kw1489)?
                    });
                    s.push({
                        let fun1493 = e.get("_job")?;
                        let mut args1491 = Vec::new();
                        let mut kw1492 = Vec::new();
                        args1491.push(e.get("steps")?.get(Val::Str("mount-slide-clean".into()))?);
                        args1491.push(Val::Str("mount-slide-clean.png".into()));
                        args1491.push(e.get("MOUNT_CAM")?);
                        kw1492.push(("target".into(), e.get("MOUNT_TARGET")?));
                        fun1493.call(args1491, kw1492)?
                    });
                    s.push({
                        let fun1496 = e.get("_job")?;
                        let mut args1494 = Vec::new();
                        let mut kw1495 = Vec::new();
                        args1494.push(e.get("steps")?.get(Val::Str("mount-final-clean".into()))?);
                        args1494.push(Val::Str("mount-final-clean.png".into()));
                        args1494.push(e.get("MOUNT_CAM")?);
                        kw1495.push(("target".into(), e.get("MOUNT_TARGET")?));
                        fun1496.call(args1494, kw1495)?
                    });
                    Val::list(s)
                };
                e.set("mount_clean_jobs", assigned1487.clone())?;
                let assigned1497 = {
                    let mut s = Vec::new();
                    s.push({
                        let fun1500 = e.get("_job")?;
                        let mut args1498 = Vec::new();
                        let mut kw1499 = Vec::new();
                        args1498.push(
                            e.get("steps")?
                                .get(Val::Str("mount-under-slide-clean".into()))?,
                        );
                        args1498.push(Val::Str("mount-under-slide-clean.png".into()));
                        args1498.push(e.get("UNDER_MOUNT_CAM")?);
                        kw1499.push(("target".into(), e.get("UNDER_MOUNT_TARGET")?));
                        fun1500.call(args1498, kw1499)?
                    });
                    s.push({
                        let fun1503 = e.get("_job")?;
                        let mut args1501 = Vec::new();
                        let mut kw1502 = Vec::new();
                        args1501.push(
                            e.get("steps")?
                                .get(Val::Str("mount-under-tighten-clean".into()))?,
                        );
                        args1501.push(Val::Str("mount-under-tighten-clean.png".into()));
                        args1501.push(e.get("UNDER_MOUNT_CAM")?);
                        kw1502.push(("target".into(), e.get("UNDER_MOUNT_TARGET")?));
                        fun1503.call(args1501, kw1502)?
                    });
                    Val::list(s)
                };
                e.set("under_mount_jobs", assigned1497.clone())?;
                let assigned1504 = {
                    let mut s = Vec::new();
                    s.extend(e.get("mount_jobs")?.iter()?);
                    s.extend(e.get("mount_clean_jobs")?.iter()?);
                    Val::list(s)
                };
                e.set("mount_frame_jobs", assigned1504.clone())?;
                let assigned1505 = {
                    let mut s = Vec::new();
                    s.extend(e.get("mount_frame_jobs")?.iter()?);
                    s.extend(e.get("under_mount_jobs")?.iter()?);
                    Val::list(s)
                };
                e.set("mount_render_jobs", assigned1505.clone())?;
                let assigned1506 = if e.get("mount_studies")?.truthy()? {
                    {
                        let mut s = Vec::new();
                        Val::list(s)
                    }
                } else {
                    {
                        let mut s = Vec::new();
                        s.push({
                            let fun1509 = e.get("_job")?;
                            let mut args1507 = Vec::new();
                            let mut kw1508 = Vec::new();
                            args1507
                                .push(e.get("steps")?.get(Val::Str("connect-rear-open".into()))?);
                            args1507.push(Val::Str("connect-rear-open.png".into()));
                            args1507.push(e.get("CONNECT_CAM")?);
                            kw1508.push(("target".into(), e.get("CONNECT_TARGET")?));
                            fun1509.call(args1507, kw1508)?
                        });
                        s.push({
                            let fun1512 = e.get("_job")?;
                            let mut args1510 = Vec::new();
                            let mut kw1511 = Vec::new();
                            args1510.push(
                                e.get("steps")?
                                    .get(Val::Str("connect-rear-connected".into()))?,
                            );
                            args1510.push(Val::Str("connect-rear-connected.png".into()));
                            args1510.push(e.get("CONNECT_CAM")?);
                            kw1511.push(("target".into(), e.get("CONNECT_TARGET")?));
                            fun1512.call(args1510, kw1511)?
                        });
                        Val::list(s)
                    }
                };
                e.set("connect_jobs", assigned1506.clone())?;
                for item1513 in e.get("connect_jobs")?.iter()? {
                    e.set("job", item1513)?;
                    let assigned1514 = e.get("CONNECT_RENDER_SIZE")?;
                    e.get("job")?
                        .set(Val::Str("size".into()), assigned1514.clone())?;
                    let assigned1515 = e.get("CONNECT_ORTHO_SPAN")?;
                    e.get("job")?
                        .set(Val::Str("span".into()), assigned1515.clone())?;
                    let assigned1516 = Val::Bool(false);
                    e.get("job")?
                        .set(Val::Str("trim".into()), assigned1516.clone())?;
                    let assigned1517 = Val::Bool(false);
                    e.get("job")?
                        .set(Val::Str("ground".into()), assigned1517.clone())?;
                    let assigned1518 = Val::Bool(false);
                    e.get("job")?
                        .set(Val::Str("fog".into()), assigned1518.clone())?;
                    let assigned1519 = Val::Bool(true);
                    e.get("job")?
                        .set(Val::Str("transparent".into()), assigned1519.clone())?;
                }
                if e.get("mount_studies")?.truthy()? {
                    let assigned1520 =
                        binary("truediv", e.get("OUT")?, Val::Str("mount-studies".into()))?;
                    e.set("study_dir", assigned1520.clone())?;
                    {
                        let fun1523 = e.get("study_dir")?.attr("mkdir")?;
                        let mut args1521 = Vec::new();
                        let mut kw1522 = Vec::new();
                        kw1522.push(("parents".into(), Val::Bool(true)));
                        kw1522.push(("exist_ok".into(), Val::Bool(true)));
                        fun1523.call(args1521, kw1522)?
                    };
                    for item1524 in e.get("mount_render_jobs")?.iter()? {
                        e.set("job", item1524)?;
                        let assigned1525 = {
                            let fun1528 = e.get("str")?;
                            let mut args1526 = Vec::new();
                            let mut kw1527 = Vec::new();
                            args1526.push(binary(
                                "truediv",
                                e.get("study_dir")?,
                                {
                                    let fun1531 = e.get("Path")?;
                                    let mut args1529 = Vec::new();
                                    let mut kw1530 = Vec::new();
                                    args1529.push(e.get("job")?.get(Val::Str("out".into()))?);
                                    fun1531.call(args1529, kw1530)?
                                }
                                .attr("name")?,
                            )?);
                            fun1528.call(args1526, kw1527)?
                        };
                        e.get("job")?
                            .set(Val::Str("out".into()), assigned1525.clone())?;
                    }
                    let assigned1532 = e.get("mount_render_jobs")?;
                    e.set("jobs", assigned1532.clone())?;
                } else {
                    let assigned1533 = {
                        let mut s = Vec::new();
                        s.push({
                            let fun1536 = e.get("_job")?;
                            let mut args1534 = Vec::new();
                            let mut kw1535 = Vec::new();
                            args1534.push(e.get("steps")?.get(Val::Str("faucet-user".into()))?);
                            args1534.push(Val::Str("faucet-front.png".into()));
                            args1534.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(0.18f64));
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                s.push(Val::Float(0.18f64));
                                Val::tuple(s)
                            });
                            fun1536.call(args1534, kw1535)?
                        });
                        s.push({
                            let fun1539 = e.get("_job")?;
                            let mut args1537 = Vec::new();
                            let mut kw1538 = Vec::new();
                            args1537.push(e.get("steps")?.get(Val::Str("faucet-user".into()))?);
                            args1537.push(Val::Str("faucet-side.png".into()));
                            args1537.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(1.0f64));
                                s.push(unary("neg", Val::Float(1.4f64))?);
                                s.push(Val::Float(0.75f64));
                                Val::tuple(s)
                            });
                            fun1539.call(args1537, kw1538)?
                        });
                        s.push({
                            let fun1542 = e.get("_job")?;
                            let mut args1540 = Vec::new();
                            let mut kw1541 = Vec::new();
                            args1540.push(
                                e.get("steps")?
                                    .get(Val::Str("faucet-user-pressed".into()))?,
                            );
                            args1540.push(Val::Str("faucet-side-pressed.png".into()));
                            args1540.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(1.0f64));
                                s.push(unary("neg", Val::Float(1.4f64))?);
                                s.push(Val::Float(0.75f64));
                                Val::tuple(s)
                            });
                            fun1542.call(args1540, kw1541)?
                        });
                        s.push({
                            let fun1545 = e.get("_job")?;
                            let mut args1543 = Vec::new();
                            let mut kw1544 = Vec::new();
                            args1543.push(e.get("steps")?.get(Val::Str("faucet-full".into()))?);
                            args1543.push(binary(
                                "truediv",
                                e.get("work")?,
                                Val::Str("faucet-full-front.png".into()),
                            )?);
                            args1543.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(0.0f64));
                                s.push(unary("neg", Val::Float(1.0f64))?);
                                s.push(Val::Float(0.28f64));
                                Val::tuple(s)
                            });
                            fun1545.call(args1543, kw1544)?
                        });
                        s.extend(e.get("mount_render_jobs")?.iter()?);
                        s.extend(e.get("connect_jobs")?.iter()?);
                        s.push({
                            let fun1548 = e.get("_job")?;
                            let mut args1546 = Vec::new();
                            let mut kw1547 = Vec::new();
                            args1546.push(e.get("MACHINE_STEP")?);
                            args1546.push(Val::Str("machine-front.png".into()));
                            args1546.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(1.0f64));
                                s.push(unary("neg", Val::Float(1.25f64))?);
                                s.push(Val::Float(0.72f64));
                                Val::tuple(s)
                            });
                            fun1548.call(args1546, kw1547)?
                        });
                        s.push({
                            let fun1551 = e.get("_job")?;
                            let mut args1549 = Vec::new();
                            let mut kw1550 = Vec::new();
                            args1549.push(e.get("MACHINE_STEP")?);
                            args1549.push(binary(
                                "truediv",
                                e.get("work")?,
                                Val::Str("machine-back.png".into()),
                            )?);
                            args1549.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(0.12f64));
                                s.push(Val::Float(1.0f64));
                                s.push(Val::Float(0.32f64));
                                Val::tuple(s)
                            });
                            fun1551.call(args1549, kw1550)?
                        });
                        s.push({
                            let fun1554 = e.get("_job")?;
                            let mut args1552 = Vec::new();
                            let mut kw1553 = Vec::new();
                            args1552.push(e.get("MACHINE_STEP")?);
                            args1552.push(Val::Str("machine-back-iso.png".into()));
                            args1552.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(1.0f64));
                                s.push(Val::Float(1.0f64));
                                s.push(Val::Float(1.0f64));
                                Val::tuple(s)
                            });
                            fun1554.call(args1552, kw1553)?
                        });
                        Val::list(s)
                    };
                    e.set("jobs", assigned1533.clone())?;
                }
                {
                    let fun1557 = e.get("_hsm_render")?.attr("render")?;
                    let mut args1555 = Vec::new();
                    let mut kw1556 = Vec::new();
                    args1555.push(e.get("jobs")?);
                    fun1557.call(args1555, kw1556)?
                };
                for item1558 in e.get("jobs")?.iter()? {
                    e.set("job", item1558)?;
                    let assigned1559 = {
                        let fun1562 = e.get("Path")?;
                        let mut args1560 = Vec::new();
                        let mut kw1561 = Vec::new();
                        args1560.push(e.get("job")?.get(Val::Str("out".into()))?);
                        fun1562.call(args1560, kw1561)?
                    };
                    e.set("output", assigned1559.clone())?;
                    if {
                        let v1563 = e.get("job")?;
                        let v1564 = e.get("connect_jobs")?;
                        Val::Bool(compare("not_in", v1563.clone(), v1564.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun1567 = e.get("_clear_connected_background")?;
                            let mut args1565 = Vec::new();
                            let mut kw1566 = Vec::new();
                            args1565.push(e.get("output")?);
                            fun1567.call(args1565, kw1566)?
                        };
                    }
                    if {
                        let v1568 = e.get("job")?;
                        let v1569 = e.get("mount_frame_jobs")?;
                        Val::Bool(compare("in", v1568.clone(), v1569.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun1572 = e.get("_shave_render_frame")?;
                            let mut args1570 = Vec::new();
                            let mut kw1571 = Vec::new();
                            args1570.push(e.get("output")?);
                            args1570.push(e.get("MOUNT_FRAME_SHAVE")?);
                            fun1572.call(args1570, kw1571)?
                        };
                    } else {
                        if {
                            let v1573 = e.get("job")?;
                            let v1574 = e.get("under_mount_jobs")?;
                            Val::Bool(compare("in", v1573.clone(), v1574.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            {
                                let fun1577 = e.get("_shave_under_render_frame")?;
                                let mut args1575 = Vec::new();
                                let mut kw1576 = Vec::new();
                                args1575.push(e.get("output")?);
                                args1575.push(e.get("UNDER_MOUNT_FRAME_SHAVE")?);
                                fun1577.call(args1575, kw1576)?
                            };
                        } else {
                            if {
                                let v1578 = e.get("job")?;
                                let v1579 = e.get("connect_jobs")?;
                                Val::Bool(compare("in", v1578.clone(), v1579.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                {
                                    let fun1582 = e.get("_crop_registered_connection")?;
                                    let mut args1580 = Vec::new();
                                    let mut kw1581 = Vec::new();
                                    args1580.push(e.get("output")?);
                                    fun1582.call(args1580, kw1581)?
                                };
                            }
                        }
                    }
                    {
                        let fun1585 = e.get("note_write")?;
                        let mut args1583 = Vec::new();
                        let mut kw1584 = Vec::new();
                        args1583.push(e.get("output")?);
                        fun1585.call(args1583, kw1584)?
                    };
                }
                if unary("not", e.get("mount_studies")?)?.truthy()? {
                    {
                        let fun1588 = e.get("_crop")?;
                        let mut args1586 = Vec::new();
                        let mut kw1587 = Vec::new();
                        args1586.push(Val::Str("machine-front.png".into()));
                        args1586.push(Val::Str("960x660+0+100".into()));
                        args1586.push(Val::Str("machine-funnel-close.png".into()));
                        fun1588.call(args1586, kw1587)?
                    };
                    {
                        let fun1591 = e.get("_crop")?;
                        let mut args1589 = Vec::new();
                        let mut kw1590 = Vec::new();
                        args1589.push(binary(
                            "truediv",
                            e.get("work")?,
                            Val::Str("machine-back.png".into()),
                        )?);
                        args1589.push(Val::Str("720x560+180+300".into()));
                        args1589.push(Val::Str("machine-back-close.png".into()));
                        fun1591.call(args1589, kw1590)?
                    };
                    {
                        let fun1594 = e.get("_crop")?;
                        let mut args1592 = Vec::new();
                        let mut kw1593 = Vec::new();
                        args1592.push(Val::Str("machine-back-iso.png".into()));
                        args1592.push(Val::Str("617x720+850+220".into()));
                        args1592.push(Val::Str("machine-ports-iso.png".into()));
                        fun1594.call(args1592, kw1593)?
                    };
                    {
                        let fun1597 = e.get("_crop")?;
                        let mut args1595 = Vec::new();
                        let mut kw1596 = Vec::new();
                        args1595.push(Val::Str("machine-ports-iso.png".into()));
                        args1595.push(Val::Str("617x612+0+72".into()));
                        args1595.push(Val::Str("machine-ports-action.png".into()));
                        fun1597.call(args1595, kw1596)?
                    };
                    {
                        let fun1600 = e.get("_crop")?;
                        let mut args1598 = Vec::new();
                        let mut kw1599 = Vec::new();
                        args1598.push(Val::Str("machine-ports-iso.png".into()));
                        args1598.push(Val::Str("594x393+23+293".into()));
                        args1598.push(Val::Str("machine-signal-iso.png".into()));
                        fun1600.call(args1598, kw1599)?
                    };
                    {
                        let fun1603 = e.get("_crop")?;
                        let mut args1601 = Vec::new();
                        let mut kw1602 = Vec::new();
                        args1601.push(binary(
                            "truediv",
                            e.get("work")?,
                            Val::Str("faucet-full-front.png".into()),
                        )?);
                        args1601.push(Val::Str("410x540+0+1060".into()));
                        args1601.push(Val::Str("faucet-tails-front.png".into()));
                        fun1603.call(args1601, kw1602)?
                    };
                    {
                        let fun1606 = e.get("_crop")?;
                        let mut args1604 = Vec::new();
                        let mut kw1605 = Vec::new();
                        args1604.push(Val::Str("mount-tighten.png".into()));
                        args1604.push(Val::Str("772x560+0+700".into()));
                        args1604.push(Val::Str("mount-tighten-close.png".into()));
                        fun1606.call(args1604, kw1605)?
                    };
                }
                Ok(Flow::Continue)
            })();
            context1454
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result1607? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun1610 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args1608 = Vec::new();
        let mut kw1609 = Vec::new();
        args1608.push(Val::Int(0i64));
        args1608.push({
            let fun1613 = e.get("str")?;
            let mut args1611 = Vec::new();
            let mut kw1612 = Vec::new();
            args1611.push(binary(
                "truediv",
                {
                    let fun1616 = {
                        let fun1619 = e.get("Path")?;
                        let mut args1617 = Vec::new();
                        let mut kw1618 = Vec::new();
                        args1617.push(e.get("__file__")?);
                        fun1619.call(args1617, kw1618)?
                    }
                    .attr("resolve")?;
                    let mut args1614 = Vec::new();
                    let mut kw1615 = Vec::new();
                    fun1616.call(args1614, kw1615)?
                }
                .attr("parents")?
                .get(Val::Int(1i64))?,
                Val::Str("scripts".into()),
            )?);
            fun1613.call(args1611, kw1612)?
        });
        fun1610.call(args1608, kw1609)?
    };
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun1622 = e.get("_rust_part")?.attr("start")?;
        let mut args1620 = Vec::new();
        let mut kw1621 = Vec::new();
        fun1622.call(args1620, kw1621)?
    };
    {
        let fun1625 = e.get("main")?;
        let mut args1623 = Vec::new();
        let mut kw1624 = Vec::new();
        kw1624.push(("mount_studies".into(), {
            let v1626 = Val::Str("--mount-studies".into());
            let v1627 = e.get("sys")?.attr("argv")?.get(Val::Slice {
                start: Some(Val::Int(1i64).integer()?),
                stop: None,
                step: 1,
            })?;
            Val::Bool(compare("in", v1626.clone(), v1627.clone())?.truthy()?)
        }));
        fun1625.call(args1623, kw1624)?
    };
    Ok(Val::None)
}
