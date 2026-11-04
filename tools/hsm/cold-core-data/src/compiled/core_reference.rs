#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let assigned2 = {
        let fun5 = e.get("next")?;
        let mut args3 = Vec::new();
        let mut kw4 = Vec::new();
        args3.push({
            let e = e.child();
            let out6 = Val::list(vec![]);
            for item7 in {
                let fun10 = {
                    let fun13 = e.get("Path")?;
                    let mut args11 = Vec::new();
                    let mut kw12 = Vec::new();
                    args11.push(e.get("__file__")?);
                    fun13.call(args11, kw12)?
                }
                .attr("resolve")?;
                let mut args8 = Vec::new();
                let mut kw9 = Vec::new();
                fun10.call(args8, kw9)?
            }
            .attr("parents")?
            .iter()?
            {
                e.set("p", item7)?;
                if {
                    let fun16 = binary(
                        "truediv",
                        e.get("p")?,
                        Val::Str("hardware/scripts/_assembly_model.py".into()),
                    )?
                    .attr("is_file")?;
                    let mut args14 = Vec::new();
                    let mut kw15 = Vec::new();
                    fun16.call(args14, kw15)?
                }
                .truthy()?
                {
                    out6.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out6
        });
        fun5.call(args3, kw4)?
    };
    e.set("ROOT", assigned2.clone())?;
    let assigned17 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str("hardware/printed-parts/cold-core".into()),
    )?;
    e.set("COLD", assigned17.clone())?;
    for item18 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            e.get("ROOT")?,
            Val::Str("hardware/scripts".into()),
        )?);
        s.push(e.get("COLD")?);
        s.push(binary(
            "truediv",
            e.get("COLD")?,
            Val::Str("foam-assembly".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("ROOT")?,
            Val::Str("hardware/cold-core-layout".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("path", item18)?;
        if {
            let v22 = {
                let fun21 = e.get("str")?;
                let mut args19 = Vec::new();
                let mut kw20 = Vec::new();
                args19.push(e.get("path")?);
                fun21.call(args19, kw20)?
            };
            let v23 = e.get("sys")?.attr("path")?;
            Val::Bool(compare("not_in", v22.clone(), v23.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args24 = Vec::new();
                let mut kw25 = Vec::new();
                args24.push(Val::Int(0i64));
                args24.push({
                    let fun29 = e.get("str")?;
                    let mut args27 = Vec::new();
                    let mut kw28 = Vec::new();
                    args27.push(e.get("path")?);
                    fun29.call(args27, kw28)?
                });
                fun26.call(args24, kw25)?
            };
        }
    }
    let assigned30 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str("hardware/cold-core-layout/cold-core-assembly.scene.npz".into()),
    )?;
    e.set("CORE_MODEL", assigned30.clone())?;
    let assigned31 = binary(
        "truediv",
        e.get("COLD")?,
        Val::Str("foam-assembly/foam-assembly.step.npz".into()),
    )?;
    e.set("CASING_MODEL", assigned31.clone())?;
    // datums
    e.set("datums", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            {
                let fun34 = e.get("_rust_part")?.attr("start")?;
                let mut args32 = Vec::new();
                let mut kw33 = Vec::new();
                fun34.call(args32, kw33)?
            };
            e.set("core", rt.import_module("_cold_core_interface")?)?;
            e.set("_copper_ports", rt.import_module("_copper_ports")?)?;
            e.set("casing", rt.import_module("foam_assembly")?)?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("front_wall_x".into()),
                    e.get("core")?.attr("front_wall_x")?,
                )?;
                d.set(
                    Val::Str("stack_floor_z".into()),
                    e.get("casing")?.attr("stack_floor_z")?,
                )?;
                d.set(
                    Val::Str("cap_face_z".into()),
                    e.get("casing")?.attr("cap_face_z")?,
                )?;
                d.set(
                    Val::Str("cap_face_over_floor".into()),
                    e.get("casing")?.attr("cap_face_over_floor")?,
                )?;
                d.set(
                    Val::Str("casing_foil_allowance".into()),
                    e.get("core")?.attr("casing_foil_allowance")?,
                )?;
                d.set(Val::Str("seat".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("core")?.attr("front_wall_x")?);
                    s.push(Val::Float(0.0f64));
                    s.push(e.get("casing")?.attr("stack_floor_z")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("copper_mouths".into()), {
                    let fun37 = e.get("_copper_ports")?.attr("stations")?;
                    let mut args35 = Vec::new();
                    let mut kw36 = Vec::new();
                    fun37.call(args35, kw36)?
                })?;
                d.set(
                    Val::Str("prv_vent_tip".into()),
                    e.get("casing")?
                        .attr("routes")?
                        .attr("routes")?
                        .get(Val::Str("prv-vent".into()))?
                        .get(unary("neg", Val::Int(1i64))?)?,
                )?;
                d.set(Val::Str("conduit_mouths".into()), {
                    let e = e.child();
                    let out38 = Val::dict(vec![]);
                    for item39 in e.get("casing")?.attr("cap_conduits")?.iter()? {
                        e.set("name", item39)?;
                        out38.set(e.get("name")?, {
                            let fun42 = e.get("casing")?.attr("cap_conduit_mouth")?;
                            let mut args40 = Vec::new();
                            let mut kw41 = Vec::new();
                            args40.push(e.get("name")?);
                            fun42.call(args40, kw41)?
                        })?;
                    }
                    out38
                })?;
                d.set(Val::Str("lid_anchor_xy".into()), {
                    let e = e.child();
                    let out43 = Val::dict(vec![]);
                    for item44 in e.get("casing")?.attr("cap_anchors")?.iter()? {
                        e.set("name", item44)?;
                        out43.set(e.get("name")?, {
                            let fun47 = e.get("casing")?.attr("cap_anchor_station")?;
                            let mut args45 = Vec::new();
                            let mut kw46 = Vec::new();
                            args45.push(e.get("name")?);
                            fun47.call(args45, kw46)?
                        })?;
                    }
                    out43
                })?;
                d.set(Val::Str("side_anchor_xy".into()), {
                    let e = e.child();
                    let out48 = Val::dict(vec![]);
                    for item49 in e.get("casing")?.attr("cap_side_anchors")?.iter()? {
                        e.set("name", item49)?;
                        out48.set(e.get("name")?, {
                            let fun52 = e.get("casing")?.attr("cap_side_anchor_station")?;
                            let mut args50 = Vec::new();
                            let mut kw51 = Vec::new();
                            args50.push(e.get("name")?);
                            fun52.call(args50, kw51)?
                        })?;
                    }
                    out48
                })?;
                d.set(Val::Str("deck_mount_xy".into()), {
                    let e = e.child();
                    let out53 = Val::dict(vec![]);
                    for item54 in e.get("core")?.attr("deck_mounts")?.iter()? {
                        e.set("name", item54)?;
                        out53.set(e.get("name")?, {
                            let fun57 = e.get("casing")?.attr("deck_mount_station")?;
                            let mut args55 = Vec::new();
                            let mut kw56 = Vec::new();
                            args55.push(e.get("name")?);
                            fun57.call(args55, kw56)?
                        })?;
                    }
                    out53
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // casing_bounds
    e.set("casing_bounds", {
        let params = vec![("model".into(), Some(e.get("CASING_MODEL")?), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_assembly_model", rt.import_module("_assembly_model")?)?;
            let assigned58 = {
                let fun61 = e.get("Path")?;
                let mut args59 = Vec::new();
                let mut kw60 = Vec::new();
                args59.push(e.get("model")?);
                fun61.call(args59, kw60)?
            };
            e.set("model", assigned58.clone())?;
            let assigned62 = {
                let fun65 = e.get("_assembly_model")?.attr("identity")?;
                let mut args63 = Vec::new();
                let mut kw64 = Vec::new();
                args63.push(e.get("model")?);
                fun65.call(args63, kw64)?
            };
            e.set("entries", assigned62.clone())?;
            let assigned66 = {
                let fun69 = e.get("_assembly_model")?.attr("instance")?;
                let mut args67 = Vec::new();
                let mut kw68 = Vec::new();
                args67.push(e.get("model")?);
                kw68.push(("indices".into(), {
                    let fun72 = e.get("range")?;
                    let mut args70 = Vec::new();
                    let mut kw71 = Vec::new();
                    args70.push({
                        let fun75 = e.get("len")?;
                        let mut args73 = Vec::new();
                        let mut kw74 = Vec::new();
                        args73.push(e.get("entries")?);
                        fun75.call(args73, kw74)?
                    });
                    fun72.call(args70, kw71)?
                }));
                fun69.call(args67, kw68)?
            };
            e.set("reference", assigned66.clone())?;
            let assigned76 = {
                let fun79 = e.get("_assembly_model")?.attr("measure")?;
                let mut args77 = Vec::new();
                let mut kw78 = Vec::new();
                args77.push({
                    let mut s = Vec::new();
                    s.push(e.get("reference")?);
                    Val::list(s)
                });
                args77.push({
                    let mut s = Vec::new();
                    Val::tuple(s)
                });
                fun79.call(args77, kw78)?
            }
            .get(Val::Str("bodies".into()))?;
            e.set("bodies", assigned76.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("min".into()), {
                    let e = e.child();
                    let out80 = Val::list(vec![]);
                    for item81 in {
                        let fun84 = e.get("range")?;
                        let mut args82 = Vec::new();
                        let mut kw83 = Vec::new();
                        args82.push(Val::Int(3i64));
                        fun84.call(args82, kw83)?
                    }
                    .iter()?
                    {
                        e.set("axis", item81)?;
                        out80.attr("append")?.call(
                            vec![{
                                let fun87 = e.get("min")?;
                                let mut args85 = Vec::new();
                                let mut kw86 = Vec::new();
                                args85.push({
                                    let e = e.child();
                                    let out88 = Val::list(vec![]);
                                    for item89 in e.get("bodies")?.iter()? {
                                        e.set("row", item89)?;
                                        out88.attr("append")?.call(
                                            vec![
                                                e.get("row")?
                                                    .get(Val::Str("min".into()))?
                                                    .get(e.get("axis")?)?,
                                            ],
                                            vec![],
                                        )?;
                                    }
                                    out88
                                });
                                fun87.call(args85, kw86)?
                            }],
                            vec![],
                        )?;
                    }
                    out80
                })?;
                d.set(Val::Str("max".into()), {
                    let e = e.child();
                    let out90 = Val::list(vec![]);
                    for item91 in {
                        let fun94 = e.get("range")?;
                        let mut args92 = Vec::new();
                        let mut kw93 = Vec::new();
                        args92.push(Val::Int(3i64));
                        fun94.call(args92, kw93)?
                    }
                    .iter()?
                    {
                        e.set("axis", item91)?;
                        out90.attr("append")?.call(
                            vec![{
                                let fun97 = e.get("max")?;
                                let mut args95 = Vec::new();
                                let mut kw96 = Vec::new();
                                args95.push({
                                    let e = e.child();
                                    let out98 = Val::list(vec![]);
                                    for item99 in e.get("bodies")?.iter()? {
                                        e.set("row", item99)?;
                                        out98.attr("append")?.call(
                                            vec![
                                                e.get("row")?
                                                    .get(Val::Str("max".into()))?
                                                    .get(e.get("axis")?)?,
                                            ],
                                            vec![],
                                        )?;
                                    }
                                    out98
                                });
                                fun97.call(args95, kw96)?
                            }],
                            vec![],
                        )?;
                    }
                    out90
                })?;
                d.set(Val::Str("bodies".into()), e.get("bodies")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // instance
    e.set("instance", {
        let params = vec![
            ("transform".into(), None, false),
            ("model".into(), Some(e.get("CORE_MODEL")?), true),
            ("prefix".into(), Some(Val::Str("cold-core/".into())), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_assembly_model", rt.import_module("_assembly_model")?)?;
            let assigned100 = {
                let fun103 = e.get("Path")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                args101.push(e.get("model")?);
                fun103.call(args101, kw102)?
            };
            e.set("model", assigned100.clone())?;
            let assigned104 = {
                let fun107 = e.get("_assembly_model")?.attr("identity")?;
                let mut args105 = Vec::new();
                let mut kw106 = Vec::new();
                args105.push(e.get("model")?);
                fun107.call(args105, kw106)?
            };
            e.set("identities", assigned104.clone())?;
            let assigned108 = {
                let fun111 = {
                    let fun114 = e.get("_assembly_model")?.attr("document")?;
                    let mut args112 = Vec::new();
                    let mut kw113 = Vec::new();
                    args112.push(e.get("model")?);
                    fun114.call(args112, kw113)?
                }
                .attr("get")?;
                let mut args109 = Vec::new();
                let mut kw110 = Vec::new();
                args109.push(Val::Str("alpha_by_name".into()));
                args109.push({
                    let d = Val::dict(vec![]);
                    d
                });
                fun111.call(args109, kw110)?
            };
            e.set("alpha", assigned108.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("reference".into()), {
                    let fun117 = e.get("_assembly_model")?.attr("instance")?;
                    let mut args115 = Vec::new();
                    let mut kw116 = Vec::new();
                    args115.push(e.get("model")?);
                    kw116.push(("indices".into(), {
                        let fun120 = e.get("range")?;
                        let mut args118 = Vec::new();
                        let mut kw119 = Vec::new();
                        args118.push({
                            let fun123 = e.get("len")?;
                            let mut args121 = Vec::new();
                            let mut kw122 = Vec::new();
                            args121.push(e.get("identities")?);
                            fun123.call(args121, kw122)?
                        });
                        fun120.call(args118, kw119)?
                    }));
                    kw116.push(("transform".into(), e.get("transform")?));
                    kw116.push(("prefix".into(), e.get("prefix")?));
                    fun117.call(args115, kw116)?
                })?;
                d.set(Val::Str("identities".into()), e.get("identities")?)?;
                d.set(Val::Str("alpha_by_name".into()), e.get("alpha")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
