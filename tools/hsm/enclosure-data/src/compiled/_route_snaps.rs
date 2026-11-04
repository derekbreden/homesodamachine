//! Integral tube and cable restraints on their owning enclosure quadrant.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
            line!(),
        );
        {
            let fun5 = e.get("next")?;
            let mut args3 = Vec::new();
            let mut kw4 = Vec::new();
            args3.push({
                let e = e.child();
                let out6 = Val::list(vec![]);
                for item7 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun10 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                                line!(),
                            );
                            {
                                let fun13 = e.get("Path")?;
                                let mut args11 = Vec::new();
                                let mut kw12 = Vec::new();
                                args11.push(e.get("__file__")?);
                                fun13.call(args11, kw12)?
                            }
                        }
                        .attr("resolve")?;
                        let mut args8 = Vec::new();
                        let mut kw9 = Vec::new();
                        fun10.call(args8, kw9)?
                    }
                }
                .attr("parents")?
                .iter()?
                {
                    e.set("p", item7)?;
                    if {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                            line!(),
                        );
                        {
                            let fun16 = binary(
                                "truediv",
                                binary("truediv", e.get("p")?, Val::Str("hardware".into()))?,
                                Val::Str("wiring".into()),
                            )?
                            .attr("is_dir")?;
                            let mut args14 = Vec::new();
                            let mut kw15 = Vec::new();
                            fun16.call(args14, kw15)?
                        }
                    }
                    .truthy()?
                    {
                        out6.attr("append")?.call(vec![e.get("p")?], vec![])?;
                    }
                }
                out6
            });
            fun5.call(args3, kw4)?
        }
    };
    e.set("_ROOT", assigned2.clone())?;
    for item17 in {
        let mut s = Vec::new();
        s.push(e.get("_ROOT")?);
        s.push(binary(
            "truediv",
            binary(
                "truediv",
                binary("truediv", e.get("_ROOT")?, Val::Str("hardware".into()))?,
                Val::Str("printed-parts".into()),
            )?,
            Val::Str("cadlib".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("directory", item17)?;
        if {
            let v21 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                    line!(),
                );
                {
                    let fun20 = e.get("str")?;
                    let mut args18 = Vec::new();
                    let mut kw19 = Vec::new();
                    args18.push(e.get("directory")?);
                    fun20.call(args18, kw19)?
                }
            };
            let v22 = e.get("sys")?.attr("path")?;
            Val::Bool(compare("not_in", v21.clone(), v22.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                    line!(),
                );
                {
                    let fun25 = e.get("sys")?.attr("path")?.attr("insert")?;
                    let mut args23 = Vec::new();
                    let mut kw24 = Vec::new();
                    args23.push(Val::Int(0i64));
                    args23.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                            line!(),
                        );
                        {
                            let fun28 = e.get("str")?;
                            let mut args26 = Vec::new();
                            let mut kw27 = Vec::new();
                            args26.push(e.get("directory")?);
                            fun28.call(args26, kw27)?
                        }
                    });
                    fun25.call(args23, kw24)?
                }
            };
        }
    }
    e.set("route_snap", rt.import_module("route_snap")?)?;
    // features
    e.set("features", {
        let params = vec![("host".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod29 = rt.import_module("hardware.wiring.installed.retainers")?;
            e.set(
                "cable_sites",
                rt.member("hardware.wiring.installed.retainers", "cable_sites")?,
            )?;
            let mod30 = rt.import_module("_tube_snap_sites")?;
            e.set("tube_sites", rt.member("_tube_snap_sites", "tube_sites")?)?;
            let assigned31 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("result", assigned31.clone())?;
            for item32 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                    line!(),
                );
                {
                    let fun35 = e.get("cable_sites")?;
                    let mut args33 = Vec::new();
                    let mut kw34 = Vec::new();
                    fun35.call(args33, kw34)?
                }
            }
            .iter()?
            {
                e.set("site", item32)?;
                if {
                    let v36 = e.get("site")?.get(Val::Str("host".into()))?;
                    let v37 = e.get("host")?;
                    Val::Bool(compare("ne", v36.clone(), v37.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned38 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun41 = e.get("route_snap")?.attr("cable_hook")?;
                        let mut args39 = Vec::new();
                        let mut kw40 = Vec::new();
                        args39.push(e.get("site")?.get(Val::Str("origin".into()))?);
                        args39.push(e.get("site")?.get(Val::Str("outward".into()))?);
                        args39.push(e.get("site")?.get(Val::Str("profile_up".into()))?);
                        kw40.push((
                            "seat_depth".into(),
                            e.get("site")?.get(Val::Str("seat_depth".into()))?,
                        ));
                        kw40.push((
                            "seat_height".into(),
                            e.get("site")?.get(Val::Str("seat_height".into()))?,
                        ));
                        kw40.push(("span".into(), e.get("site")?.get(Val::Str("span".into()))?));
                        kw40.push((
                            "stock".into(),
                            e.get("site")?.get(Val::Str("stock".into()))?,
                        ));
                        kw40.push(("beak".into(), e.get("site")?.get(Val::Str("beak".into()))?));
                        fun41.call(args39, kw40)?
                    }
                };
                e.set("body", assigned38.clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun44 = e.get("result")?.attr("append")?;
                        let mut args42 = Vec::new();
                        let mut kw43 = Vec::new();
                        args42.push({
                            let mut s = Vec::new();
                            s.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                                    line!(),
                                );
                                {
                                    let fun47 = e.get("dict")?;
                                    let mut args45 = Vec::new();
                                    let mut kw46 = Vec::new();
                                    args45.push(e.get("site")?);
                                    kw46.push(("kind".into(), Val::Str("cable".into())));
                                    fun47.call(args45, kw46)?
                                }
                            });
                            s.push(e.get("body")?);
                            Val::tuple(s)
                        });
                        fun44.call(args42, kw43)?
                    }
                };
            }
            let assigned48 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("groups", assigned48.clone())?;
            for item49 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                    line!(),
                );
                {
                    let fun52 = e.get("tube_sites")?;
                    let mut args50 = Vec::new();
                    let mut kw51 = Vec::new();
                    fun52.call(args50, kw51)?
                }
            }
            .iter()?
            {
                e.set("site", item49)?;
                if {
                    let v53 = e.get("site")?.get(Val::Str("host".into()))?;
                    let v54 = e.get("host")?;
                    Val::Bool(compare("ne", v53.clone(), v54.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned55 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun58 = e.get("route_snap")?.attr("tube_clip")?;
                        let mut args56 = Vec::new();
                        let mut kw57 = Vec::new();
                        args56.push(e.get("site")?.get(Val::Str("centre".into()))?);
                        args56.push(e.get("site")?.get(Val::Str("along".into()))?);
                        args56.push(e.get("site")?.get(Val::Str("outward".into()))?);
                        args56.push(e.get("site")?.get(Val::Str("root_distance".into()))?);
                        kw57.push((
                            "tube_od".into(),
                            e.get("site")?.get(Val::Str("tube_od".into()))?,
                        ));
                        kw57.push((
                            "bore_diameter".into(),
                            e.get("site")?.get(Val::Str("bore_diameter".into()))?,
                        ));
                        kw57.push(("span".into(), e.get("site")?.get(Val::Str("span".into()))?));
                        kw57.push(("wing".into(), e.get("site")?.get(Val::Str("wing".into()))?));
                        kw57.push((
                            "print_up".into(),
                            e.get("site")?.get(Val::Str("print_up".into()))?,
                        ));
                        fun58.call(args56, kw57)?
                    }
                };
                e.set("body", assigned55.clone())?;
                let assigned59 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun62 = e.get("site")?.attr("get")?;
                        let mut args60 = Vec::new();
                        let mut kw61 = Vec::new();
                        args60.push(Val::Str("group".into()));
                        fun62.call(args60, kw61)?
                    }
                };
                e.set("group", assigned59.clone())?;
                if {
                    let v63 = e.get("group")?;
                    let v64 = Val::None;
                    Val::Bool(compare("is", v63.clone(), v64.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                            line!(),
                        );
                        {
                            let fun67 = e.get("result")?.attr("append")?;
                            let mut args65 = Vec::new();
                            let mut kw66 = Vec::new();
                            args65.push({
                                let mut s = Vec::new();
                                s.push({
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                                        line!(),
                                    );
                                    {
                                        let fun70 = e.get("dict")?;
                                        let mut args68 = Vec::new();
                                        let mut kw69 = Vec::new();
                                        args68.push(e.get("site")?);
                                        kw69.push(("kind".into(), Val::Str("tube".into())));
                                        fun70.call(args68, kw69)?
                                    }
                                });
                                s.push(e.get("body")?);
                                Val::tuple(s)
                            });
                            fun67.call(args65, kw66)?
                        }
                    };
                } else {
                    let assigned71 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                            line!(),
                        );
                        {
                            let fun74 = e.get("groups")?.attr("setdefault")?;
                            let mut args72 = Vec::new();
                            let mut kw73 = Vec::new();
                            args72.push(e.get("group")?.get(Val::Str("id".into()))?);
                            args72.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                                    line!(),
                                );
                                {
                                    let fun77 = e.get("dict")?;
                                    let mut args75 = Vec::new();
                                    let mut kw76 = Vec::new();
                                    kw76.push(("root".into(), e.get("group")?));
                                    kw76.push(("members".into(), {
                                        let mut s = Vec::new();
                                        Val::list(s)
                                    }));
                                    kw76.push(("bodies".into(), {
                                        let mut s = Vec::new();
                                        Val::list(s)
                                    }));
                                    fun77.call(args75, kw76)?
                                }
                            });
                            fun74.call(args72, kw73)?
                        }
                    };
                    e.set("entry", assigned71.clone())?;
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                            line!(),
                        );
                        {
                            let fun80 = e
                                .get("entry")?
                                .get(Val::Str("members".into()))?
                                .attr("append")?;
                            let mut args78 = Vec::new();
                            let mut kw79 = Vec::new();
                            args78.push(e.get("site")?);
                            fun80.call(args78, kw79)?
                        }
                    };
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                            line!(),
                        );
                        {
                            let fun83 = e
                                .get("entry")?
                                .get(Val::Str("bodies".into()))?
                                .attr("append")?;
                            let mut args81 = Vec::new();
                            let mut kw82 = Vec::new();
                            args81.push(e.get("body")?);
                            fun83.call(args81, kw82)?
                        }
                    };
                }
            }
            for item84 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                    line!(),
                );
                {
                    let fun87 = e.get("groups")?.attr("values")?;
                    let mut args85 = Vec::new();
                    let mut kw86 = Vec::new();
                    fun87.call(args85, kw86)?
                }
            }
            .iter()?
            {
                e.set("entry", item84)?;
                let assigned88 = e.get("entry")?.get(Val::Str("root".into()))?;
                e.set("root", assigned88.clone())?;
                let assigned89 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun92 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                        let mut args90 = Vec::new();
                        let mut kw91 = Vec::new();
                        args90.extend(e.get("root")?.get(Val::Str("bridge_size".into()))?.iter()?);
                        args90.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                                line!(),
                            );
                            {
                                let fun95 = e.get("cq")?.attr("Vector")?;
                                let mut args93 = Vec::new();
                                let mut kw94 = Vec::new();
                                args93.extend(
                                    e.get("root")?
                                        .get(Val::Str("bridge_origin".into()))?
                                        .iter()?,
                                );
                                fun95.call(args93, kw94)?
                            }
                        });
                        fun92.call(args90, kw91)?
                    }
                };
                e.set("bridge", assigned89.clone())?;
                let assigned96 = e.get("entry")?.get(Val::Str("bodies".into()))?;
                let unpack97 = assigned96.clone().iter()?;
                anyhow::ensure!(unpack97.len() >= 1, "not enough values to unpack");
                e.set("first", unpack97[0].clone())?;
                e.set(
                    "others",
                    Val::list(unpack97[1..unpack97.len() - 0].to_vec()),
                )?;
                let assigned98 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun101 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                                line!(),
                            );
                            {
                                let fun104 = e.get("first")?.attr("fuse")?;
                                let mut args102 = Vec::new();
                                let mut kw103 = Vec::new();
                                args102.push(e.get("bridge")?);
                                args102.extend(e.get("others")?.iter()?);
                                fun104.call(args102, kw103)?
                            }
                        }
                        .attr("clean")?;
                        let mut args99 = Vec::new();
                        let mut kw100 = Vec::new();
                        fun101.call(args99, kw100)?
                    }
                };
                e.set("body", assigned98.clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun107 = e.get("result")?.attr("append")?;
                        let mut args105 = Vec::new();
                        let mut kw106 = Vec::new();
                        args105.push({
                            let mut s = Vec::new();
                            s.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                                    line!(),
                                );
                                {
                                    let fun110 = e.get("dict")?;
                                    let mut args108 = Vec::new();
                                    let mut kw109 = Vec::new();
                                    kw109.push((
                                        "id".into(),
                                        e.get("root")?.get(Val::Str("id".into()))?,
                                    ));
                                    kw109.push(("kind".into(), Val::Str("tube-group".into())));
                                    kw109.push(("host".into(), e.get("host")?));
                                    kw109.push(("members".into(), {
                                        let _site = rt.source_at(
                                            "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                                            line!(),
                                        );
                                        {
                                            let fun113 = e.get("tuple")?;
                                            let mut args111 = Vec::new();
                                            let mut kw112 = Vec::new();
                                            args111.push(
                                                e.get("entry")?.get(Val::Str("members".into()))?,
                                            );
                                            fun113.call(args111, kw112)?
                                        }
                                    }));
                                    kw109.push(("shared_root".into(), e.get("root")?));
                                    fun110.call(args108, kw109)?
                                }
                            });
                            s.push(e.get("body")?);
                            Val::tuple(s)
                        });
                        fun107.call(args105, kw106)?
                    }
                };
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                    line!(),
                );
                {
                    let fun116 = e.get("tuple")?;
                    let mut args114 = Vec::new();
                    let mut kw115 = Vec::new();
                    args114.push(e.get("result")?);
                    fun116.call(args114, kw115)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // apply
    e.set("apply", {
        let params = vec![
            ("piece".into(), None, false),
            ("y_side".into(), None, false),
            ("z_side".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned117 = {
                let e = e.child();
                let out118 = Val::list(vec![]);
                for item119 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun122 = e.get("features")?;
                        let mut args120 = Vec::new();
                        let mut kw121 = Vec::new();
                        args120.push({
                            let mut str123 = String::new();
                            str123.push_str("enclosure-");
                            str123.push_str(&format(&e.get("y_side")?, &String::new())?);
                            str123.push_str("-");
                            str123.push_str(&format(&e.get("z_side")?, &String::new())?);
                            Val::Str(str123)
                        });
                        fun122.call(args120, kw121)?
                    }
                }
                .iter()?
                {
                    let unpack124 = unpack(item119, 2)?;
                    e.set("_site", unpack124[0].clone())?;
                    e.set("shape", unpack124[1].clone())?;
                    out118.attr("append")?.call(vec![e.get("shape")?], vec![])?;
                }
                out118
            };
            e.set("additions", assigned117.clone())?;
            return Ok(if e.get("additions")?.truthy()? {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_route_snaps.rs",
                        line!(),
                    );
                    {
                        let fun127 = e.get("piece")?.attr("fuse")?;
                        let mut args125 = Vec::new();
                        let mut kw126 = Vec::new();
                        args125.extend(e.get("additions")?.iter()?);
                        fun127.call(args125, kw126)?
                    }
                }
            } else {
                e.get("piece")?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
