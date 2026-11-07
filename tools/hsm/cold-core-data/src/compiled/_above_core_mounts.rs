#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("functools")?;
    e.set("lru_cache", rt.member("functools", "lru_cache")?)?;
    e.set("importlib", rt.import_module("importlib")?)?;
    e.set("itertools", rt.import_module("itertools")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod2 = rt.import_module("collections")?;
    e.set("namedtuple", rt.member("collections", "namedtuple")?)?;
    let mod3 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let assigned4 = {
        let fun7 = e.get("next")?;
        let mut args5 = Vec::new();
        let mut kw6 = Vec::new();
        args5.push({
            let e = e.child();
            let out8 = Val::list(vec![]);
            for item9 in {
                let fun12 = {
                    let fun15 = e.get("Path")?;
                    let mut args13 = Vec::new();
                    let mut kw14 = Vec::new();
                    args13.push(e.get("__file__")?);
                    fun15.call(args13, kw14)?
                }
                .attr("resolve")?;
                let mut args10 = Vec::new();
                let mut kw11 = Vec::new();
                fun12.call(args10, kw11)?
            }
            .attr("parents")?
            .iter()?
            {
                e.set("p", item9)?;
                if {
                    let v16 = e.get("p")?.attr("name")?;
                    let v17 = Val::Str("hardware".into());
                    Val::Bool(compare("eq", v16.clone(), v17.clone())?.truthy()?)
                }
                .truthy()?
                {
                    out8.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out8
        });
        fun7.call(args5, kw6)?
    };
    e.set("HW", assigned4.clone())?;
    for item18 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            e.get("HW")?,
            Val::Str("manifold-layout".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
            Val::Str("valve-seat".into()),
        )?);
        s.push(binary(
            "truediv",
            binary(
                "truediv",
                binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
                Val::Str("electronics".into()),
            )?,
            Val::Str("pcba-tray".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("reference".into()))?,
            Val::Str("meanwell-irm90".into()),
        )?);
        s.push(binary(
            "truediv",
            binary(
                "truediv",
                binary("truediv", e.get("HW")?, Val::Str("reference".into()))?,
                Val::Str("g-ganen-pump".into()),
            )?,
            Val::Str("installation".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("reference".into()))?,
            Val::Str("neofit-achv44-check".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("reference".into()))?,
            Val::Str("digiten-flow-sensor".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("reference".into()))?,
            Val::Str("neofit-stem-elbow".into()),
        )?);
        s.push(binary(
            "truediv",
            binary(
                "truediv",
                binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
                Val::Str("cold-core".into()),
            )?,
            Val::Str("reservoir".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("path", item18)?;
        {
            let fun21 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args19 = Vec::new();
            let mut kw20 = Vec::new();
            args19.push(Val::Int(0i64));
            args19.push({
                let fun24 = e.get("str")?;
                let mut args22 = Vec::new();
                let mut kw23 = Vec::new();
                args22.push(e.get("path")?);
                fun24.call(args22, kw23)?
            });
            fun21.call(args19, kw20)?
        };
    }
    e.set("above_core", rt.import_module("above_core")?)?;
    let assigned25 = {
        let fun28 = e.get("namedtuple")?;
        let mut args26 = Vec::new();
        let mut kw27 = Vec::new();
        args26.push(Val::Str("DeckMount".into()));
        args26.push(Val::Str("points standoff seat screw seat_min".into()));
        fun28.call(args26, kw27)?
    };
    e.set("DeckMount", assigned25.clone())?;
    // _multiply
    e.set("_multiply", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun31 = e.get("tuple")?;
                let mut args29 = Vec::new();
                let mut kw30 = Vec::new();
                args29.push({
                    let e = e.child();
                    let out32 = Val::list(vec![]);
                    for item33 in {
                        let fun36 = e.get("range")?;
                        let mut args34 = Vec::new();
                        let mut kw35 = Vec::new();
                        args34.push(Val::Int(3i64));
                        fun36.call(args34, kw35)?
                    }
                    .iter()?
                    {
                        e.set("i", item33)?;
                        out32.attr("append")?.call(
                            vec![{
                                let fun39 = e.get("tuple")?;
                                let mut args37 = Vec::new();
                                let mut kw38 = Vec::new();
                                args37.push({
                                    let e = e.child();
                                    let out40 = Val::list(vec![]);
                                    for item41 in {
                                        let fun44 = e.get("range")?;
                                        let mut args42 = Vec::new();
                                        let mut kw43 = Vec::new();
                                        args42.push(Val::Int(3i64));
                                        fun44.call(args42, kw43)?
                                    }
                                    .iter()?
                                    {
                                        e.set("j", item41)?;
                                        out40.attr("append")?.call(
                                            vec![{
                                                let fun47 = e.get("sum")?;
                                                let mut args45 = Vec::new();
                                                let mut kw46 = Vec::new();
                                                args45.push({
                                                    let e = e.child();
                                                    let out48 = Val::list(vec![]);
                                                    for item49 in {
                                                        let fun52 = e.get("range")?;
                                                        let mut args50 = Vec::new();
                                                        let mut kw51 = Vec::new();
                                                        args50.push(Val::Int(3i64));
                                                        fun52.call(args50, kw51)?
                                                    }
                                                    .iter()?
                                                    {
                                                        e.set("k", item49)?;
                                                        out48.attr("append")?.call(
                                                            vec![binary(
                                                                "mul",
                                                                e.get("a")?
                                                                    .get(e.get("i")?)?
                                                                    .get(e.get("k")?)?,
                                                                e.get("b")?
                                                                    .get(e.get("k")?)?
                                                                    .get(e.get("j")?)?,
                                                            )?],
                                                            vec![],
                                                        )?;
                                                    }
                                                    out48
                                                });
                                                fun47.call(args45, kw46)?
                                            }],
                                            vec![],
                                        )?;
                                    }
                                    out40
                                });
                                fun39.call(args37, kw38)?
                            }],
                            vec![],
                        )?;
                    }
                    out32
                });
                fun31.call(args29, kw30)?
            });
            Ok(Val::None)
        })
    })?;
    // component_in_cap
    e.set("component_in_cap", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned53 = {
                let fun56 = e.get("above_core")?.attr("pose")?;
                let mut args54 = Vec::new();
                let mut kw55 = Vec::new();
                args54.push(e.get("name")?);
                fun56.call(args54, kw55)?
            };
            e.set("frame", assigned53.clone())?;
            let assigned57 = {
                let fun60 = e.get("above_core")?.attr("cap_lid_pose")?;
                let mut args58 = Vec::new();
                let mut kw59 = Vec::new();
                fun60.call(args58, kw59)?
            };
            e.set("cap", assigned57.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("rotation".into()), {
                    let fun63 = e.get("_multiply")?;
                    let mut args61 = Vec::new();
                    let mut kw62 = Vec::new();
                    args61.push({
                        let fun66 = e.get("tuple")?;
                        let mut args64 = Vec::new();
                        let mut kw65 = Vec::new();
                        args64.push({
                            let fun69 = e.get("zip")?;
                            let mut args67 = Vec::new();
                            let mut kw68 = Vec::new();
                            args67.extend(e.get("cap")?.get(Val::Str("rotation".into()))?.iter()?);
                            fun69.call(args67, kw68)?
                        });
                        fun66.call(args64, kw65)?
                    });
                    args61.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                    fun63.call(args61, kw62)?
                })?;
                d.set(Val::Str("translation_mm".into()), {
                    let fun72 = e.get("above_core")?.attr("world_to_cap")?;
                    let mut args70 = Vec::new();
                    let mut kw71 = Vec::new();
                    args70.push(e.get("frame")?.get(Val::Str("translation_mm".into()))?);
                    fun72.call(args70, kw71)?
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // lid_face_z
    e.set("lid_face_z", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned73 = {
                let fun76 = e.get("above_core")?.attr("specification")?;
                let mut args74 = Vec::new();
                let mut kw75 = Vec::new();
                fun76.call(args74, kw75)?
            }
            .get(Val::Str("cap_face_z_mm".into()))?;
            e.set("face", assigned73.clone())?;
            return Ok({
                let fun79 = e.get("above_core")?.attr("world_to_cap")?;
                let mut args77 = Vec::new();
                let mut kw78 = Vec::new();
                args77.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(e.get("face")?);
                    Val::tuple(s)
                });
                fun79.call(args77, kw78)?
            }
            .get(Val::Int(2i64))?);
            Ok(Val::None)
        })
    })?;
    // va_feed_snap
    e.set("va_feed_snap", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun82 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args80 = Vec::new();
                let mut kw81 = Vec::new();
                args80.push(Val::Int(0i64));
                args80.push({
                    let fun85 = e.get("str")?;
                    let mut args83 = Vec::new();
                    let mut kw84 = Vec::new();
                    args83.push(binary(
                        "truediv",
                        binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
                        Val::Str("cadlib".into()),
                    )?);
                    fun85.call(args83, kw84)?
                });
                fun82.call(args80, kw81)?
            };
            let mod86 = rt.import_module("route_snap")?;
            e.set("tube_clip", rt.member("route_snap", "tube_clip")?)?;
            let assigned87 = {
                let fun90 = e.get("above_core")?.attr("specification")?;
                let mut args88 = Vec::new();
                let mut kw89 = Vec::new();
                fun90.call(args88, kw89)?
            }
            .get(Val::Str("fore_routes".into()))?
            .get(Val::Str("va_feed_snap".into()))?;
            e.set("datum", assigned87.clone())?;
            return Ok({
                let fun93 = e.get("tube_clip")?;
                let mut args91 = Vec::new();
                let mut kw92 = Vec::new();
                args91.push(e.get("datum")?.get(Val::Str("centre_world_mm".into()))?);
                args91.push(e.get("datum")?.get(Val::Str("along_world".into()))?);
                args91.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    Val::tuple(s)
                });
                args91.push(binary(
                    "sub",
                    e.get("datum")?
                        .get(Val::Str("centre_world_mm".into()))?
                        .get(Val::Int(2i64))?,
                    {
                        let fun96 = e.get("above_core")?.attr("specification")?;
                        let mut args94 = Vec::new();
                        let mut kw95 = Vec::new();
                        fun96.call(args94, kw95)?
                    }
                    .get(Val::Str("cap_face_z_mm".into()))?,
                )?);
                kw92.push(("tube_od".into(), Val::Float(6.35f64)));
                kw92.push(("bore_diameter".into(), Val::Float(6.35f64)));
                kw92.push(("span".into(), Val::Float(8.0f64)));
                kw92.push(("wing".into(), Val::Float(2.4f64)));
                kw92.push(("print_up".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    Val::tuple(s)
                }));
                fun93.call(args91, kw92)?
            });
            Ok(Val::None)
        })
    })?;
    // flavor_snaps
    e.set("flavor_snaps", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            {
                let fun99 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                args97.push(Val::Int(0i64));
                args97.push({
                    let fun102 = e.get("str")?;
                    let mut args100 = Vec::new();
                    let mut kw101 = Vec::new();
                    args100.push(binary(
                        "truediv",
                        e.get("HW")?,
                        Val::Str("printed-parts/cadlib".into()),
                    )?);
                    fun102.call(args100, kw101)?
                });
                fun99.call(args97, kw98)?
            };
            let mod103 = rt.import_module("route_snap")?;
            e.set("tube_clip", rt.member("route_snap", "tube_clip")?)?;
            let assigned104 = {
                let e = e.child();
                let out105 = Val::dict(vec![]);
                for item106 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("flavor-a".into()));
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(26.5f64));
                            s.push(Val::Float(266.0f64));
                            s.push(Val::Float(296.0f64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(1.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("flavor-b".into()));
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(35.0f64));
                            s.push(Val::Float(414.0f64));
                            s.push(Val::Float(264.0f64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(1.0f64));
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                }
                .iter()?
                {
                    let unpack107 = unpack(item106, 3)?;
                    e.set("name", unpack107[0].clone())?;
                    e.set("centre", unpack107[1].clone())?;
                    e.set("axis", unpack107[2].clone())?;
                    out105.set(e.get("name")?, {
                        let fun110 = e.get("tube_clip")?;
                        let mut args108 = Vec::new();
                        let mut kw109 = Vec::new();
                        args108.push(e.get("centre")?);
                        args108.push(e.get("axis")?);
                        args108.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(1.0f64));
                            Val::tuple(s)
                        });
                        args108.push(binary(
                            "sub",
                            e.get("centre")?.get(Val::Int(2i64))?,
                            {
                                let fun113 = e.get("above_core")?.attr("specification")?;
                                let mut args111 = Vec::new();
                                let mut kw112 = Vec::new();
                                fun113.call(args111, kw112)?
                            }
                            .get(Val::Str("cap_face_z_mm".into()))?,
                        )?);
                        kw109.push(("tube_od".into(), Val::Float(4.0f64)));
                        kw109.push(("bore_diameter".into(), Val::Float(4.1f64)));
                        kw109.push(("span".into(), Val::Float(8.0f64)));
                        kw109.push(("wing".into(), Val::Float(1.52f64)));
                        kw109.push(("print_up".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(1.0f64));
                            Val::tuple(s)
                        }));
                        fun110.call(args108, kw109)?
                    })?;
                }
                out105
            };
            e.set("result", assigned104.clone())?;
            let assigned114 = {
                let fun117 = e.get("valve_support_datums")?;
                let mut args115 = Vec::new();
                let mut kw116 = Vec::new();
                args115.push(Val::Str("valve-v-b".into()));
                fun117.call(args115, kw116)?
            };
            e.set("wall", assigned114.clone())?;
            let assigned118 = {
                let mut s = Vec::new();
                s.push(
                    e.get("wall")?
                        .get(Val::Str("root_min_world_mm".into()))?
                        .get(Val::Int(0i64))?,
                );
                s.push(binary(
                    "sub",
                    e.get("wall")?
                        .get(Val::Str("root_max_world_mm".into()))?
                        .get(Val::Int(1i64))?,
                    Val::Float(0.1f64),
                )?);
                Val::tuple(s)
            };
            let unpack119 = unpack(assigned118.clone(), 2)?;
            e.set("x0", unpack119[0].clone())?;
            e.set("y0", unpack119[1].clone())?;
            let assigned120 = binary(
                "sub",
                {
                    let fun123 = e.get("above_core")?.attr("specification")?;
                    let mut args121 = Vec::new();
                    let mut kw122 = Vec::new();
                    fun123.call(args121, kw122)?
                }
                .get(Val::Str("cap_face_z_mm".into()))?,
                Val::Float(0.1f64),
            )?;
            e.set("z0", assigned120.clone())?;
            let assigned124 = binary(
                "sub",
                Val::Float(266.0f64),
                binary(
                    "add",
                    binary("truediv", Val::Float(4.1f64), Val::Float(2.0f64))?,
                    Val::Float(1.52f64),
                )?,
            )?;
            e.set("root_front", assigned124.clone())?;
            let assigned125 = binary("add", e.get("root_front")?, Val::Float(0.1f64))?;
            e.set("front", assigned125.clone())?;
            let assigned126 = {
                let fun129 = {
                    let fun132 = {
                        let fun135 = {
                            let fun138 = {
                                let fun141 = {
                                    let fun144 = e.get("cq")?.attr("Workplane")?;
                                    let mut args142 = Vec::new();
                                    let mut kw143 = Vec::new();
                                    args142.push(Val::Str("YZ".into()));
                                    fun144.call(args142, kw143)?
                                }
                                .attr("workplane")?;
                                let mut args139 = Vec::new();
                                let mut kw140 = Vec::new();
                                kw140.push(("offset".into(), e.get("x0")?));
                                fun141.call(args139, kw140)?
                            }
                            .attr("polyline")?;
                            let mut args136 = Vec::new();
                            let mut kw137 = Vec::new();
                            args136.push({
                                let mut s = Vec::new();
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("y0")?);
                                    s.push(e.get("z0")?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("front")?);
                                    s.push(e.get("z0")?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("front")?);
                                    s.push(binary(
                                        "sub",
                                        binary("add", Val::Float(296.0f64), e.get("front")?)?,
                                        e.get("root_front")?,
                                    )?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("y0")?);
                                    s.push(binary(
                                        "sub",
                                        binary("add", Val::Float(296.0f64), e.get("y0")?)?,
                                        e.get("root_front")?,
                                    )?);
                                    Val::tuple(s)
                                });
                                Val::list(s)
                            });
                            fun138.call(args136, kw137)?
                        }
                        .attr("close")?;
                        let mut args133 = Vec::new();
                        let mut kw134 = Vec::new();
                        fun135.call(args133, kw134)?
                    }
                    .attr("extrude")?;
                    let mut args130 = Vec::new();
                    let mut kw131 = Vec::new();
                    args130.push(binary("sub", Val::Float(30.5f64), e.get("x0")?)?);
                    fun132.call(args130, kw131)?
                }
                .attr("val")?;
                let mut args127 = Vec::new();
                let mut kw128 = Vec::new();
                fun129.call(args127, kw128)?
            };
            e.set("bridge", assigned126.clone())?;
            let assigned145 = {
                let fun148 = {
                    let fun151 = e
                        .get("result")?
                        .get(Val::Str("flavor-a".into()))?
                        .attr("fuse")?;
                    let mut args149 = Vec::new();
                    let mut kw150 = Vec::new();
                    args149.push(e.get("bridge")?);
                    fun151.call(args149, kw150)?
                }
                .attr("clean")?;
                let mut args146 = Vec::new();
                let mut kw147 = Vec::new();
                fun148.call(args146, kw147)?
            };
            e.get("result")?
                .set(Val::Str("flavor-a".into()), assigned145.clone())?;
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // manifold_cable_bank
    e.set("manifold_cable_bank", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned152 = {
                let mut s = Vec::new();
                s.push({
                    let fun155 = e.get("str")?;
                    let mut args153 = Vec::new();
                    let mut kw154 = Vec::new();
                    args153.push(e.get("HW")?.attr("parent")?);
                    fun155.call(args153, kw154)?
                });
                s.push({
                    let fun158 = e.get("str")?;
                    let mut args156 = Vec::new();
                    let mut kw157 = Vec::new();
                    args156.push(binary(
                        "truediv",
                        binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
                        Val::Str("cadlib".into()),
                    )?);
                    fun158.call(args156, kw157)?
                });
                Val::list(s)
            };
            e.get("sys")?.attr("path")?.set(
                Val::Slice {
                    start: None,
                    stop: Some(Val::Int(0i64).integer()?),
                    step: 1,
                },
                assigned152.clone(),
            )?;
            let mod159 = rt.import_module("hardware.wiring.installed.retainers")?;
            e.set(
                "manifold_bank_site",
                rt.member("hardware.wiring.installed.retainers", "manifold_bank_site")?,
            )?;
            let mod160 = rt.import_module("route_snap")?;
            e.set("cable_bank", rt.member("route_snap", "cable_bank")?)?;
            let assigned161 = {
                let fun164 = e.get("manifold_bank_site")?;
                let mut args162 = Vec::new();
                let mut kw163 = Vec::new();
                fun164.call(args162, kw163)?
            };
            e.set("site", assigned161.clone())?;
            return Ok({
                let fun167 = e.get("cable_bank")?;
                let mut args165 = Vec::new();
                let mut kw166 = Vec::new();
                args165.push(e.get("site")?.get(Val::Str("origin".into()))?);
                kw166.extend(keyword_items({
                    let e = e.child();
                    let out168 = Val::dict(vec![]);
                    for item169 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("seat_depth".into()));
                        s.push(Val::Str("seat_heights".into()));
                        s.push(Val::Str("span".into()));
                        s.push(Val::Str("stock".into()));
                        s.push(Val::Str("beak".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("key", item169)?;
                        out168.set(e.get("key")?, e.get("site")?.get(e.get("key")?)?)?;
                    }
                    out168
                })?);
                fun167.call(args165, kw166)?
            });
            Ok(Val::None)
        })
    })?;
    // rear_level_cable_hook
    e.set("rear_level_cable_hook", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned170 = {
                let mut s = Vec::new();
                s.push({
                    let fun173 = e.get("str")?;
                    let mut args171 = Vec::new();
                    let mut kw172 = Vec::new();
                    args171.push(e.get("HW")?.attr("parent")?);
                    fun173.call(args171, kw172)?
                });
                s.push({
                    let fun176 = e.get("str")?;
                    let mut args174 = Vec::new();
                    let mut kw175 = Vec::new();
                    args174.push(binary(
                        "truediv",
                        binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
                        Val::Str("cadlib".into()),
                    )?);
                    fun176.call(args174, kw175)?
                });
                Val::list(s)
            };
            e.get("sys")?.attr("path")?.set(
                Val::Slice {
                    start: None,
                    stop: Some(Val::Int(0i64).integer()?),
                    step: 1,
                },
                assigned170.clone(),
            )?;
            let mod177 = rt.import_module("hardware.wiring.installed.retainers")?;
            e.set(
                "rear_level_hook_site",
                rt.member(
                    "hardware.wiring.installed.retainers",
                    "rear_level_hook_site",
                )?,
            )?;
            let mod178 = rt.import_module("route_snap")?;
            e.set(
                "floor_cable_hook",
                rt.member("route_snap", "floor_cable_hook")?,
            )?;
            let assigned179 = {
                let fun182 = e.get("rear_level_hook_site")?;
                let mut args180 = Vec::new();
                let mut kw181 = Vec::new();
                fun182.call(args180, kw181)?
            };
            e.set("site", assigned179.clone())?;
            return Ok({
                let fun185 = e.get("floor_cable_hook")?;
                let mut args183 = Vec::new();
                let mut kw184 = Vec::new();
                args183.push(e.get("site")?.get(Val::Str("origin".into()))?);
                kw184.extend(keyword_items({
                    let e = e.child();
                    let out186 = Val::dict(vec![]);
                    for item187 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("seat_depth".into()));
                        s.push(Val::Str("seat_height".into()));
                        s.push(Val::Str("span".into()));
                        s.push(Val::Str("stock".into()));
                        s.push(Val::Str("beak".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("key", item187)?;
                        out186.set(e.get("key")?, e.get("site")?.get(e.get("key")?)?)?;
                    }
                    out186
                })?);
                fun185.call(args183, kw184)?
            });
            Ok(Val::None)
        })
    })?;
    // mounting_points
    e.set("mounting_points", {
        let params = vec![("name".into(), None, false), ("holes".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned188 = {
                let fun191 = e.get("above_core")?.attr("pose")?;
                let mut args189 = Vec::new();
                let mut kw190 = Vec::new();
                args189.push(e.get("name")?);
                fun191.call(args189, kw190)?
            };
            e.set("frame", assigned188.clone())?;
            return Ok({
                let fun194 = e.get("tuple")?;
                let mut args192 = Vec::new();
                let mut kw193 = Vec::new();
                args192.push({
                    let e = e.child();
                    let out195 = Val::list(vec![]);
                    for item196 in e.get("holes")?.iter()? {
                        let unpack197 = unpack(item196, 2)?;
                        e.set("x", unpack197[0].clone())?;
                        e.set("y", unpack197[1].clone())?;
                        out195.attr("append")?.call(
                            vec![
                                {
                                    let fun200 = e.get("above_core")?.attr("world_to_cap")?;
                                    let mut args198 = Vec::new();
                                    let mut kw199 = Vec::new();
                                    args198.push({
                                        let fun203 = e.get("above_core")?.attr("point")?;
                                        let mut args201 = Vec::new();
                                        let mut kw202 = Vec::new();
                                        args201.push(e.get("frame")?);
                                        args201.push({
                                            let mut s = Vec::new();
                                            s.push(e.get("x")?);
                                            s.push(e.get("y")?);
                                            s.push(Val::Float(0.0f64));
                                            Val::tuple(s)
                                        });
                                        fun203.call(args201, kw202)?
                                    });
                                    fun200.call(args198, kw199)?
                                }
                                .get(Val::Slice {
                                    start: None,
                                    stop: Some(Val::Int(2i64).integer()?),
                                    step: 1,
                                })?,
                            ],
                            vec![],
                        )?;
                    }
                    out195
                });
                fun194.call(args192, kw193)?
            });
            Ok(Val::None)
        })
    })?;
    // _standoff
    e.set("_standoff", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let v204 = {
                    let fun207 = e.get("round")?;
                    let mut args205 = Vec::new();
                    let mut kw206 = Vec::new();
                    args205.push(binary(
                        "sub",
                        {
                            let fun210 = e.get("component_in_cap")?;
                            let mut args208 = Vec::new();
                            let mut kw209 = Vec::new();
                            args208.push(e.get("name")?);
                            fun210.call(args208, kw209)?
                        }
                        .get(Val::Str("translation_mm".into()))?
                        .get(Val::Int(2i64))?,
                        {
                            let fun213 = e.get("lid_face_z")?;
                            let mut args211 = Vec::new();
                            let mut kw212 = Vec::new();
                            fun213.call(args211, kw212)?
                        },
                    )?);
                    args205.push(Val::Int(4i64));
                    fun207.call(args205, kw206)?
                };
                if v204.truthy()? {
                    v204
                } else {
                    Val::Float(0.0f64)
                }
            });
            Ok(Val::None)
        })
    })?;
    // deck_mounts
    e.set("deck_mounts", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            // The main board's mounting holes about its centre, and its thickness, from its numbers.
            let centre = hsm_pcba_numbers::centre();
            let holes = Val::tuple(hsm_pcba_numbers::HOLES.iter()
                .map(|p| Val::tuple(vec![Val::Float(p[0] - centre[0]), Val::Float(p[1] - centre[1])])).collect());
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("pcba".into()), {
                    let fun220 = e.get("DeckMount")?;
                    let mut args218 = Vec::new();
                    let mut kw219 = Vec::new();
                    args218.push({
                        let fun223 = e.get("mounting_points")?;
                        let mut args221 = Vec::new();
                        let mut kw222 = Vec::new();
                        args221.push(Val::Str("pcba".into()));
                        args221.push(holes.clone());
                        fun223.call(args221, kw222)?
                    });
                    args218.push({
                        let fun226 = e.get("_standoff")?;
                        let mut args224 = Vec::new();
                        let mut kw225 = Vec::new();
                        args224.push(Val::Str("pcba".into()));
                        fun226.call(args224, kw225)?
                    });
                    args218.push(Val::Float(hsm_pcba_numbers::THICKNESS));
                    args218.push(Val::Float(8.0f64));
                    args218.push(Val::Float(hsm_pcba_numbers::THICKNESS));
                    fun220.call(args218, kw219)?
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // _pump_section_points
    e.set("_pump_section_points", {
        let params = vec![
            ("pump".into(), None, false),
            ("first".into(), None, false),
            ("last".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned227 = e.get("pump")?.get(Val::Str("casing_sections".into()))?;
            e.set("sections", assigned227.clone())?;
            let assigned228 = {
                let e = e.child();
                let out229 = Val::list(vec![]);
                for item230 in e.get("sections")?.iter()? {
                    e.set("row", item230)?;
                    if {
                        let v231 = e.get("first")?;
                        let v232 = e.get("row")?.get(Val::Str("x_mm".into()))?;
                        let v233 = e.get("last")?;
                        Val::Bool(
                            compare("le", v231.clone(), v232.clone())?.truthy()?
                                && compare("le", v232.clone(), v233.clone())?.truthy()?,
                        )
                    }
                    .truthy()?
                    {
                        out229.attr("append")?.call(vec![e.get("row")?], vec![])?;
                    }
                }
                out229
            };
            e.set("rows", assigned228.clone())?;
            let assigned234 = {
                let e = e.child();
                let out235 = Val::list(vec![]);
                for item236 in e.get("rows")?.iter()? {
                    e.set("row", item236)?;
                    for item237 in e.get("row")?.get(Val::Str("vertices_mm".into()))?.iter()? {
                        e.set("point", item237)?;
                        out235.attr("append")?.call(vec![e.get("point")?], vec![])?;
                    }
                }
                out235
            };
            e.set("points", assigned234.clone())?;
            for item238 in {
                let mut s = Vec::new();
                s.push(e.get("first")?);
                s.push(e.get("last")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("end", item238)?;
                let assigned239 = {
                    let fun242 = e.get("next")?;
                    let mut args240 = Vec::new();
                    let mut kw241 = Vec::new();
                    args240.push({
                        let e = e.child();
                        let out243 = Val::list(vec![]);
                        for item244 in {
                            let fun247 = e.get("zip")?;
                            let mut args245 = Vec::new();
                            let mut kw246 = Vec::new();
                            args245.push(e.get("sections")?);
                            args245.push(e.get("sections")?.get(Val::Slice {
                                start: Some(Val::Int(1i64).integer()?),
                                stop: None,
                                step: 1,
                            })?);
                            fun247.call(args245, kw246)?
                        }
                        .iter()?
                        {
                            let unpack248 = unpack(item244, 2)?;
                            e.set("a", unpack248[0].clone())?;
                            e.set("b", unpack248[1].clone())?;
                            if {
                                let v249 = e.get("a")?.get(Val::Str("x_mm".into()))?;
                                let v250 = e.get("end")?;
                                let v251 = e.get("b")?.get(Val::Str("x_mm".into()))?;
                                Val::Bool(
                                    compare("le", v249.clone(), v250.clone())?.truthy()?
                                        && compare("le", v250.clone(), v251.clone())?.truthy()?,
                                )
                            }
                            .truthy()?
                            {
                                out243.attr("append")?.call(
                                    vec![{
                                        let mut s = Vec::new();
                                        s.push(e.get("a")?);
                                        s.push(e.get("b")?);
                                        Val::tuple(s)
                                    }],
                                    vec![],
                                )?;
                            }
                        }
                        out243
                    });
                    fun242.call(args240, kw241)?
                };
                let unpack252 = unpack(assigned239.clone(), 2)?;
                e.set("a", unpack252[0].clone())?;
                e.set("b", unpack252[1].clone())?;
                let assigned253 = binary(
                    "truediv",
                    binary(
                        "sub",
                        e.get("end")?,
                        e.get("a")?.get(Val::Str("x_mm".into()))?,
                    )?,
                    binary(
                        "sub",
                        e.get("b")?.get(Val::Str("x_mm".into()))?,
                        e.get("a")?.get(Val::Str("x_mm".into()))?,
                    )?,
                )?;
                e.set("share", assigned253.clone())?;
                {
                    let fun256 = e.get("points")?.attr("extend")?;
                    let mut args254 = Vec::new();
                    let mut kw255 = Vec::new();
                    args254.push({
                        let e = e.child();
                        let out257 = Val::list(vec![]);
                        for item258 in {
                            let fun261 = e.get("zip")?;
                            let mut args259 = Vec::new();
                            let mut kw260 = Vec::new();
                            args259.push(e.get("a")?.get(Val::Str("vertices_mm".into()))?);
                            args259.push(e.get("b")?.get(Val::Str("vertices_mm".into()))?);
                            fun261.call(args259, kw260)?
                        }
                        .iter()?
                        {
                            let unpack262 = unpack(item258, 2)?;
                            e.set("p", unpack262[0].clone())?;
                            e.set("q", unpack262[1].clone())?;
                            out257.attr("append")?.call(
                                vec![{
                                    let e = e.child();
                                    let out263 = Val::list(vec![]);
                                    for item264 in {
                                        let fun267 = e.get("zip")?;
                                        let mut args265 = Vec::new();
                                        let mut kw266 = Vec::new();
                                        args265.push(e.get("p")?);
                                        args265.push(e.get("q")?);
                                        fun267.call(args265, kw266)?
                                    }
                                    .iter()?
                                    {
                                        let unpack268 = unpack(item264, 2)?;
                                        e.set("v", unpack268[0].clone())?;
                                        e.set("w", unpack268[1].clone())?;
                                        out263.attr("append")?.call(
                                            vec![binary(
                                                "add",
                                                e.get("v")?,
                                                binary(
                                                    "mul",
                                                    binary("sub", e.get("w")?, e.get("v")?)?,
                                                    e.get("share")?,
                                                )?,
                                            )?],
                                            vec![],
                                        )?;
                                    }
                                    out263
                                }],
                                vec![],
                            )?;
                        }
                        out257
                    });
                    fun256.call(args254, kw255)?
                };
            }
            return Ok(e.get("points")?);
            Ok(Val::None)
        })
    })?;
    // pump_cradle_datums
    e.set("pump_cradle_datums", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("above_core_parts", rt.import_module("above_core_parts")?)?;
            e.set("fits", rt.import_module("fits")?)?;
            e.set("rear_snaps", rt.import_module("rear_snaps")?)?;
            let assigned269 = {
                let fun272 = {
                    let fun275 = e.get("above_core_parts")?.attr("_module")?;
                    let mut args273 = Vec::new();
                    let mut kw274 = Vec::new();
                    args273.push(Val::Str("bearing_pump".into()));
                    args273.push(Val::Str("reference/g-ganen-pump/g_ganen_pump.py".into()));
                    fun275.call(args273, kw274)?
                }
                .attr("parameters")?;
                let mut args270 = Vec::new();
                let mut kw271 = Vec::new();
                fun272.call(args270, kw271)?
            };
            e.set("pump", assigned269.clone())?;
            let assigned276 = {
                let fun279 = e.get("above_core")?.attr("specification")?;
                let mut args277 = Vec::new();
                let mut kw278 = Vec::new();
                fun279.call(args277, kw278)?
            }
            .get(Val::Str("pump_mount".into()))?;
            e.set("selected", assigned276.clone())?;
            let assigned280 = e
                .get("selected")?
                .get(Val::Str("motor_band_native_x_mm".into()))?;
            let unpack281 = unpack(assigned280.clone(), 2)?;
            e.set("first", unpack281[0].clone())?;
            e.set("last", unpack281[1].clone())?;
            let assigned282 = {
                let fun285 = e.get("_pump_section_points")?;
                let mut args283 = Vec::new();
                let mut kw284 = Vec::new();
                args283.push(e.get("pump")?);
                args283.push(e.get("first")?);
                args283.push(e.get("last")?);
                fun285.call(args283, kw284)?
            };
            e.set("points", assigned282.clone())?;
            let assigned286 = e.get("pump")?.get(Val::Str("motor_can_envelope".into()))?;
            e.set("can", assigned286.clone())?;
            let assigned287 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("cover_sides", assigned287.clone())?;
            for item288 in e
                .get("pump")?
                .get(Val::Str("rigid_underside".into()))?
                .get(Val::Str("wire_cover_side_profiles".into()))?
                .iter()?
            {
                e.set("side", item288)?;
                let assigned289 = e
                    .get("side")?
                    .get(Val::Str("side_plane".into()))?
                    .get(Val::Str("coefficients".into()))?;
                let unpack290 = unpack(assigned289.clone(), 3)?;
                e.set("a", unpack290[0].clone())?;
                e.set("b", unpack290[1].clone())?;
                e.set("c", unpack290[2].clone())?;
                {
                    let fun293 = e.get("cover_sides")?.attr("append")?;
                    let mut args291 = Vec::new();
                    let mut kw292 = Vec::new();
                    args291.push({
                        let e = e.child();
                        let out294 = Val::list(vec![]);
                        for item295 in {
                            let mut s = Vec::new();
                            s.push(e.get("first")?);
                            s.push(e.get("last")?);
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("x", item295)?;
                            for item296 in {
                                let mut s = Vec::new();
                                s.push({
                                    let fun299 = e.get("min")?;
                                    let mut args297 = Vec::new();
                                    let mut kw298 = Vec::new();
                                    args297.push({
                                        let e = e.child();
                                        let out300 = Val::list(vec![]);
                                        for item301 in e.get("points")?.iter()? {
                                            e.set("p", item301)?;
                                            out300.attr("append")?.call(
                                                vec![e.get("p")?.get(Val::Int(2i64))?],
                                                vec![],
                                            )?;
                                        }
                                        out300
                                    });
                                    fun299.call(args297, kw298)?
                                });
                                s.push(binary(
                                    "add",
                                    e.get("can")?
                                        .get(Val::Str("axis_point_mm".into()))?
                                        .get(Val::Int(2i64))?,
                                    e.get("can")?.get(Val::Str("radius_mm".into()))?,
                                )?);
                                Val::tuple(s)
                            }
                            .iter()?
                            {
                                e.set("z", item296)?;
                                out294.attr("append")?.call(
                                    vec![binary(
                                        "add",
                                        binary(
                                            "add",
                                            binary("mul", e.get("a")?, e.get("x")?)?,
                                            binary("mul", e.get("b")?, e.get("z")?)?,
                                        )?,
                                        e.get("c")?,
                                    )?],
                                    vec![],
                                )?;
                            }
                        }
                        out294
                    });
                    fun293.call(args291, kw292)?
                };
            }
            let assigned302 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    {
                        let fun305 = e.get("min")?;
                        let mut args303 = Vec::new();
                        let mut kw304 = Vec::new();
                        args303.push({
                            let e = e.child();
                            let out306 = Val::list(vec![]);
                            for item307 in e.get("cover_sides")?.iter()? {
                                e.set("side", item307)?;
                                for item308 in e.get("side")?.iter()? {
                                    e.set("v", item308)?;
                                    out306.attr("append")?.call(vec![e.get("v")?], vec![])?;
                                }
                            }
                            out306
                        });
                        fun305.call(args303, kw304)?
                    },
                    binary("mul", Val::Int(2i64), e.get("fits")?.attr("running")?)?,
                )?);
                s.push(binary(
                    "add",
                    {
                        let fun311 = e.get("max")?;
                        let mut args309 = Vec::new();
                        let mut kw310 = Vec::new();
                        args309.push({
                            let e = e.child();
                            let out312 = Val::list(vec![]);
                            for item313 in e.get("cover_sides")?.iter()? {
                                e.set("side", item313)?;
                                for item314 in e.get("side")?.iter()? {
                                    e.set("v", item314)?;
                                    out312.attr("append")?.call(vec![e.get("v")?], vec![])?;
                                }
                            }
                            out312
                        });
                        fun311.call(args309, kw310)?
                    },
                    binary("mul", Val::Int(2i64), e.get("fits")?.attr("running")?)?,
                )?);
                Val::tuple(s)
            };
            e.set("cover_room", assigned302.clone())?;
            let assigned315 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("rails", assigned315.clone())?;
            for item316 in e
                .get("pump")?
                .get(Val::Str("rigid_underside".into()))?
                .get(Val::Str("rail_face_planes".into()))?
                .iter()?
            {
                e.set("rail", item316)?;
                let assigned317 = {
                    let e = e.child();
                    let out318 = Val::list(vec![]);
                    for item319 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("outer_upper".into()));
                        s.push(Val::Str("outer_lower".into()));
                        s.push(Val::Str("inner_return".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("name", item319)?;
                        out318.attr("append")?.call(
                            vec![
                                e.get("rail")?
                                    .get(Val::Str("planes".into()))?
                                    .get(e.get("name")?)?
                                    .get(Val::Str("z_ax_plus_by_plus_c".into()))?,
                            ],
                            vec![],
                        )?;
                    }
                    out318
                };
                let unpack320 = unpack(assigned317.clone(), 3)?;
                e.set("a", unpack320[0].clone())?;
                e.set("b", unpack320[1].clone())?;
                e.set("c", unpack320[2].clone())?;
                let assigned321 = {
                    let e = e.child();
                    let out322 = Val::list(vec![]);
                    for item323 in {
                        let mut s = Vec::new();
                        s.push(e.get("first")?);
                        s.push(e.get("last")?);
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("x", item323)?;
                        out322.attr("append")?.call(
                            vec![binary(
                                "truediv",
                                binary(
                                    "sub",
                                    binary(
                                        "add",
                                        binary(
                                            "mul",
                                            binary(
                                                "sub",
                                                e.get("b")?.get(Val::Int(0i64))?,
                                                e.get("a")?.get(Val::Int(0i64))?,
                                            )?,
                                            e.get("x")?,
                                        )?,
                                        e.get("b")?.get(Val::Int(2i64))?,
                                    )?,
                                    e.get("a")?.get(Val::Int(2i64))?,
                                )?,
                                binary(
                                    "sub",
                                    e.get("a")?.get(Val::Int(1i64))?,
                                    e.get("b")?.get(Val::Int(1i64))?,
                                )?,
                            )?],
                            vec![],
                        )?;
                    }
                    out322
                };
                e.set("corners", assigned321.clone())?;
                let assigned324 = if {
                    let v325 = e.get("rail")?.get(Val::Str("side".into()))?;
                    let v326 = Val::Int(0i64);
                    Val::Bool(compare("gt", v325.clone(), v326.clone())?.truthy()?)
                }
                .truthy()?
                {
                    binary(
                        "add",
                        {
                            let fun329 = e.get("max")?;
                            let mut args327 = Vec::new();
                            let mut kw328 = Vec::new();
                            args327.push(e.get("corners")?);
                            fun329.call(args327, kw328)?
                        },
                        e.get("fits")?.attr("running")?,
                    )?
                } else {
                    binary(
                        "sub",
                        {
                            let fun332 = e.get("min")?;
                            let mut args330 = Vec::new();
                            let mut kw331 = Vec::new();
                            args330.push(e.get("corners")?);
                            fun332.call(args330, kw331)?
                        },
                        e.get("fits")?.attr("running")?,
                    )?
                };
                e.set("outer", assigned324.clone())?;
                {
                    let fun335 = e.get("rails")?.attr("append")?;
                    let mut args333 = Vec::new();
                    let mut kw334 = Vec::new();
                    args333.push({
                        let fun338 = e.get("dict")?;
                        let mut args336 = Vec::new();
                        let mut kw337 = Vec::new();
                        kw337.push(("side".into(), e.get("rail")?.get(Val::Str("side".into()))?));
                        kw337.push(("outer_y_mm".into(), e.get("outer")?));
                        kw337.push(("floor_planes".into(), {
                            let mut s = Vec::new();
                            s.push(e.get("b")?);
                            s.push(e.get("c")?);
                            Val::tuple(s)
                        }));
                        fun338.call(args336, kw337)?
                    });
                    fun335.call(args333, kw334)?
                };
            }
            let assigned339 = {
                let mut s = Vec::new();
                s.push(e.get("can")?.get(Val::Str("axis_point_mm".into()))?);
                s.push(e.get("can")?.get(Val::Str("axis_direction".into()))?);
                Val::tuple(s)
            };
            let unpack340 = unpack(assigned339.clone(), 2)?;
            e.set("origin", unpack340[0].clone())?;
            e.set("axis", unpack340[1].clone())?;
            let assigned341 = {
                let fun344 = e.get("max")?;
                let mut args342 = Vec::new();
                let mut kw343 = Vec::new();
                args342.push(e.get("can")?.get(Val::Str("radius_mm".into()))?);
                args342.extend(
                    {
                        let e = e.child();
                        let out345 = Val::list(vec![]);
                        for item346 in e.get("points")?.iter()? {
                            e.set("p", item346)?;
                            if {
                                let v347 = e.get("p")?.get(Val::Int(2i64))?;
                                let v348 = binary(
                                    "add",
                                    e.get("origin")?.get(Val::Int(2i64))?,
                                    binary(
                                        "truediv",
                                        binary(
                                            "mul",
                                            e.get("axis")?.get(Val::Int(2i64))?,
                                            binary(
                                                "sub",
                                                e.get("p")?.get(Val::Int(0i64))?,
                                                e.get("origin")?.get(Val::Int(0i64))?,
                                            )?,
                                        )?,
                                        e.get("axis")?.get(Val::Int(0i64))?,
                                    )?,
                                )?;
                                Val::Bool(compare("ge", v347.clone(), v348.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out345.attr("append")?.call(
                                    vec![{
                                        let fun351 = e.get("math")?.attr("hypot")?;
                                        let mut args349 = Vec::new();
                                        let mut kw350 = Vec::new();
                                        args349.push(binary(
                                            "sub",
                                            e.get("p")?.get(Val::Int(1i64))?,
                                            e.get("origin")?.get(Val::Int(1i64))?,
                                        )?);
                                        args349.push(binary(
                                            "sub",
                                            e.get("p")?.get(Val::Int(2i64))?,
                                            binary(
                                                "add",
                                                e.get("origin")?.get(Val::Int(2i64))?,
                                                binary(
                                                    "truediv",
                                                    binary(
                                                        "mul",
                                                        e.get("axis")?.get(Val::Int(2i64))?,
                                                        binary(
                                                            "sub",
                                                            e.get("p")?.get(Val::Int(0i64))?,
                                                            e.get("origin")?.get(Val::Int(0i64))?,
                                                        )?,
                                                    )?,
                                                    e.get("axis")?.get(Val::Int(0i64))?,
                                                )?,
                                            )?,
                                        )?);
                                        fun351.call(args349, kw350)?
                                    }],
                                    vec![],
                                )?;
                            }
                        }
                        out345
                    }
                    .iter()?,
                );
                fun344.call(args342, kw343)?
            };
            e.set("barrel_radius", assigned341.clone())?;
            // in_open_room
            e.set("in_open_room", {
                let params = vec![("p".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    if {
                        let v352 = e.get("cover_room")?.get(Val::Int(0i64))?;
                        let v353 = e.get("p")?.get(Val::Int(1i64))?;
                        let v354 = e.get("cover_room")?.get(Val::Int(1i64))?;
                        Val::Bool(
                            compare("le", v352.clone(), v353.clone())?.truthy()?
                                && compare("le", v353.clone(), v354.clone())?.truthy()?,
                        )
                    }
                    .truthy()?
                    {
                        return Ok(Val::Bool(true));
                    }
                    for item355 in e.get("rails")?.iter()? {
                        e.set("rail", item355)?;
                        if unary("not", {
                            let v356 = Val::Float(0.0f64);
                            let v357 = binary(
                                "mul",
                                e.get("p")?.get(Val::Int(1i64))?,
                                e.get("rail")?.get(Val::Str("side".into()))?,
                            )?;
                            let v358 = binary(
                                "mul",
                                e.get("rail")?.get(Val::Str("outer_y_mm".into()))?,
                                e.get("rail")?.get(Val::Str("side".into()))?,
                            )?;
                            Val::Bool(
                                compare("le", v356.clone(), v357.clone())?.truthy()?
                                    && compare("le", v357.clone(), v358.clone())?.truthy()?,
                            )
                        })?
                        .truthy()?
                        {
                            continue;
                        }
                        if {
                            let fun361 = e.get("all")?;
                            let mut args359 = Vec::new();
                            let mut kw360 = Vec::new();
                            args359.push({
                                let e = e.child();
                                let out362 = Val::list(vec![]);
                                for item363 in e
                                    .get("rail")?
                                    .get(Val::Str("floor_planes".into()))?
                                    .iter()?
                                {
                                    let unpack364 = unpack(item363, 3)?;
                                    e.set("a", unpack364[0].clone())?;
                                    e.set("b", unpack364[1].clone())?;
                                    e.set("c", unpack364[2].clone())?;
                                    out362.attr("append")?.call(
                                        vec![{
                                            let v368 = e.get("p")?.get(Val::Int(2i64))?;
                                            let v369 = binary(
                                                "sub",
                                                binary(
                                                    "sub",
                                                    binary(
                                                        "add",
                                                        binary(
                                                            "add",
                                                            binary(
                                                                "mul",
                                                                e.get("a")?,
                                                                e.get("p")?.get(Val::Int(0i64))?,
                                                            )?,
                                                            binary(
                                                                "mul",
                                                                e.get("b")?,
                                                                e.get("p")?.get(Val::Int(1i64))?,
                                                            )?,
                                                        )?,
                                                        e.get("c")?,
                                                    )?,
                                                    binary(
                                                        "mul",
                                                        e.get("fits")?.attr("running")?,
                                                        {
                                                            let fun367 =
                                                                e.get("math")?.attr("sqrt")?;
                                                            let mut args365 = Vec::new();
                                                            let mut kw366 = Vec::new();
                                                            args365.push(binary(
                                                                "add",
                                                                binary(
                                                                    "add",
                                                                    Val::Float(1.0f64),
                                                                    binary(
                                                                        "mul",
                                                                        e.get("a")?,
                                                                        e.get("a")?,
                                                                    )?,
                                                                )?,
                                                                binary(
                                                                    "mul",
                                                                    e.get("b")?,
                                                                    e.get("b")?,
                                                                )?,
                                                            )?);
                                                            fun367.call(args365, kw366)?
                                                        },
                                                    )?,
                                                )?,
                                                Val::Float(1e-08f64),
                                            )?;
                                            Val::Bool(
                                                compare("ge", v368.clone(), v369.clone())?
                                                    .truthy()?,
                                            )
                                        }],
                                        vec![],
                                    )?;
                                }
                                out362
                            });
                            fun361.call(args359, kw360)?
                        }
                        .truthy()?
                        {
                            return Ok(Val::Bool(true));
                        }
                    }
                    return Ok(Val::Bool(false));
                    Ok(Val::None)
                })
            })?;
            let assigned370 = binary(
                "add",
                {
                    let fun373 = e.get("max")?;
                    let mut args371 = Vec::new();
                    let mut kw372 = Vec::new();
                    args371.push(e.get("barrel_radius")?);
                    args371.extend(
                        {
                            let e = e.child();
                            let out374 = Val::list(vec![]);
                            for item375 in e.get("points")?.iter()? {
                                e.set("p", item375)?;
                                if unary("not", {
                                    let fun378 = e.get("in_open_room")?;
                                    let mut args376 = Vec::new();
                                    let mut kw377 = Vec::new();
                                    args376.push(e.get("p")?);
                                    fun378.call(args376, kw377)?
                                })?
                                .truthy()?
                                {
                                    out374.attr("append")?.call(
                                        vec![{
                                            let fun381 = e.get("math")?.attr("hypot")?;
                                            let mut args379 = Vec::new();
                                            let mut kw380 = Vec::new();
                                            args379.push(binary(
                                                "sub",
                                                e.get("p")?.get(Val::Int(1i64))?,
                                                e.get("origin")?.get(Val::Int(1i64))?,
                                            )?);
                                            args379.push(binary(
                                                "sub",
                                                e.get("p")?.get(Val::Int(2i64))?,
                                                binary(
                                                    "add",
                                                    e.get("origin")?.get(Val::Int(2i64))?,
                                                    binary(
                                                        "truediv",
                                                        binary(
                                                            "mul",
                                                            e.get("axis")?.get(Val::Int(2i64))?,
                                                            binary(
                                                                "sub",
                                                                e.get("p")?.get(Val::Int(0i64))?,
                                                                e.get("origin")?
                                                                    .get(Val::Int(0i64))?,
                                                            )?,
                                                        )?,
                                                        e.get("axis")?.get(Val::Int(0i64))?,
                                                    )?,
                                                )?,
                                            )?);
                                            fun381.call(args379, kw380)?
                                        }],
                                        vec![],
                                    )?;
                                }
                            }
                            out374
                        }
                        .iter()?,
                    );
                    fun373.call(args371, kw372)?
                },
                e.get("fits")?.attr("running")?,
            )?;
            e.set("seat_radius", assigned370.clone())?;
            let assigned382 = binary(
                "truediv",
                binary("add", e.get("first")?, e.get("last")?)?,
                Val::Float(2.0f64),
            )?;
            e.set("middle", assigned382.clone())?;
            let assigned383 = {
                let mut s = Vec::new();
                s.push(e.get("middle")?);
                s.push(e.get("origin")?.get(Val::Int(1i64))?);
                s.push(binary(
                    "add",
                    e.get("origin")?.get(Val::Int(2i64))?,
                    binary(
                        "truediv",
                        binary(
                            "mul",
                            e.get("axis")?.get(Val::Int(2i64))?,
                            binary(
                                "sub",
                                e.get("middle")?,
                                e.get("origin")?.get(Val::Int(0i64))?,
                            )?,
                        )?,
                        e.get("axis")?.get(Val::Int(0i64))?,
                    )?,
                )?);
                Val::tuple(s)
            };
            e.set("centre", assigned383.clone())?;
            let assigned384 = {
                let fun387 = e.get("above_core")?.attr("pose")?;
                let mut args385 = Vec::new();
                let mut kw386 = Vec::new();
                args385.push(Val::Str("g-ganen-pump".into()));
                fun387.call(args385, kw386)?
            };
            e.set("frame", assigned384.clone())?;
            let assigned388 = {
                let fun391 = e.get("above_core")?.attr("point")?;
                let mut args389 = Vec::new();
                let mut kw390 = Vec::new();
                args389.push(e.get("frame")?);
                args389.push(e.get("centre")?);
                fun391.call(args389, kw390)?
            };
            let unpack392 = unpack(assigned388.clone(), 3)?;
            e.set("cx", unpack392[0].clone())?;
            e.set("cy", unpack392[1].clone())?;
            e.set("cz", unpack392[2].clone())?;
            let assigned393 = {
                let mut s = Vec::new();
                s.push(
                    e.get("selected")?
                        .get(Val::Str("snap_band_native_x_mm".into()))?,
                );
                Val::tuple(s)
            };
            e.set("bands", assigned393.clone())?;
            let assigned394 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("radii", assigned394.clone())?;
            for item395 in e.get("bands")?.iter()? {
                let unpack413 = unpack(item395, 2)?;
                e.set("lo", unpack413[0].clone())?;
                e.set("hi", unpack413[1].clone())?;
                let assigned396 = {
                    let fun399 = e.get("_pump_section_points")?;
                    let mut args397 = Vec::new();
                    let mut kw398 = Vec::new();
                    args397.push(e.get("pump")?);
                    args397.push(e.get("lo")?);
                    args397.push(e.get("hi")?);
                    fun399.call(args397, kw398)?
                };
                e.set("upper", assigned396.clone())?;
                {
                    let fun402 = e.get("radii")?.attr("append")?;
                    let mut args400 = Vec::new();
                    let mut kw401 = Vec::new();
                    args400.push(binary(
                        "add",
                        {
                            let fun405 = e.get("max")?;
                            let mut args403 = Vec::new();
                            let mut kw404 = Vec::new();
                            args403.push(e.get("can")?.get(Val::Str("radius_mm".into()))?);
                            args403.extend(
                                {
                                    let e = e.child();
                                    let out406 = Val::list(vec![]);
                                    for item407 in e.get("upper")?.iter()? {
                                        e.set("p", item407)?;
                                        if {
                                            let v408 = e.get("p")?.get(Val::Int(2i64))?;
                                            let v409 = binary(
                                                "add",
                                                e.get("origin")?.get(Val::Int(2i64))?,
                                                binary(
                                                    "truediv",
                                                    binary(
                                                        "mul",
                                                        e.get("axis")?.get(Val::Int(2i64))?,
                                                        binary(
                                                            "sub",
                                                            e.get("p")?.get(Val::Int(0i64))?,
                                                            e.get("origin")?.get(Val::Int(0i64))?,
                                                        )?,
                                                    )?,
                                                    e.get("axis")?.get(Val::Int(0i64))?,
                                                )?,
                                            )?;
                                            Val::Bool(
                                                compare("ge", v408.clone(), v409.clone())?
                                                    .truthy()?,
                                            )
                                        }
                                        .truthy()?
                                        {
                                            out406.attr("append")?.call(
                                                vec![{
                                                    let fun412 = e.get("math")?.attr("hypot")?;
                                                    let mut args410 = Vec::new();
                                                    let mut kw411 = Vec::new();
                                                    args410.push(binary(
                                                        "sub",
                                                        e.get("p")?.get(Val::Int(1i64))?,
                                                        e.get("origin")?.get(Val::Int(1i64))?,
                                                    )?);
                                                    args410.push(binary(
                                                        "sub",
                                                        e.get("p")?.get(Val::Int(2i64))?,
                                                        binary(
                                                            "add",
                                                            e.get("origin")?.get(Val::Int(2i64))?,
                                                            binary(
                                                                "truediv",
                                                                binary(
                                                                    "mul",
                                                                    e.get("axis")?
                                                                        .get(Val::Int(2i64))?,
                                                                    binary(
                                                                        "sub",
                                                                        e.get("p")?
                                                                            .get(Val::Int(0i64))?,
                                                                        e.get("origin")?
                                                                            .get(Val::Int(0i64))?,
                                                                    )?,
                                                                )?,
                                                                e.get("axis")?
                                                                    .get(Val::Int(0i64))?,
                                                            )?,
                                                        )?,
                                                    )?);
                                                    fun412.call(args410, kw411)?
                                                }],
                                                vec![],
                                            )?;
                                        }
                                    }
                                    out406
                                }
                                .iter()?,
                            );
                            fun405.call(args403, kw404)?
                        },
                        e.get("fits")?.attr("slip")?,
                    )?);
                    fun402.call(args400, kw401)?
                };
            }
            let assigned414 = binary(
                "add",
                {
                    let fun417 = e.get("max")?;
                    let mut args415 = Vec::new();
                    let mut kw416 = Vec::new();
                    args415.extend(e.get("radii")?.iter()?);
                    args415.extend(
                        {
                            let e = e.child();
                            let out418 = Val::list(vec![]);
                            for item419 in e.get("rails")?.iter()? {
                                e.set("r", item419)?;
                                out418.attr("append")?.call(
                                    vec![{
                                        let fun422 = e.get("abs")?;
                                        let mut args420 = Vec::new();
                                        let mut kw421 = Vec::new();
                                        args420
                                            .push(e.get("r")?.get(Val::Str("outer_y_mm".into()))?);
                                        fun422.call(args420, kw421)?
                                    }],
                                    vec![],
                                )?;
                            }
                            out418
                        }
                        .iter()?,
                    );
                    fun417.call(args415, kw416)?
                },
                e.get("rear_snaps")?.attr("WALL")?,
            )?;
            e.set("neck", assigned414.clone())?;
            let assigned423 = {
                let fun426 = e.get("dict")?;
                let mut args424 = Vec::new();
                let mut kw425 = Vec::new();
                kw425.push(("centre_world_mm".into(), {
                    let mut s = Vec::new();
                    s.push(e.get("cx")?);
                    s.push(e.get("cy")?);
                    s.push(e.get("cz")?);
                    Val::tuple(s)
                }));
                kw425.push(("can".into(), e.get("can")?));
                kw425.push(("frame".into(), e.get("frame")?));
                kw425.push(("seat_bore_radius_mm".into(), e.get("seat_radius")?));
                kw425.push(("band_native_x_mm".into(), {
                    let mut s = Vec::new();
                    s.push(e.get("first")?);
                    s.push(e.get("last")?);
                    Val::tuple(s)
                }));
                kw425.push(("cover_room_native_y_mm".into(), e.get("cover_room")?));
                kw425.push(("rail_rooms".into(), e.get("rails")?));
                kw425.push(("selected".into(), e.get("selected")?));
                fun426.call(args424, kw425)?
            };
            e.set("common", assigned423.clone())?;
            let assigned427 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("caps", assigned427.clone())?;
            for item428 in {
                let fun446 = e.get("zip")?;
                let mut args444 = Vec::new();
                let mut kw445 = Vec::new();
                args444.push(e.get("bands")?);
                args444.push(e.get("radii")?);
                fun446.call(args444, kw445)?
            }
            .iter()?
            {
                let unpack447 = unpack(item428, 2)?;
                let unpack448 = unpack(unpack447[0].clone(), 2)?;
                e.set("lo", unpack448[0].clone())?;
                e.set("hi", unpack448[1].clone())?;
                e.set("radius", unpack447[1].clone())?;
                let assigned429 = {
                    let fun432 = e.get("rear_snaps")?.attr("station")?;
                    let mut args430 = Vec::new();
                    let mut kw431 = Vec::new();
                    args430.push(e.get("cx")?);
                    args430.push(e.get("neck")?);
                    args430.push(binary(
                        "add",
                        e.get("frame")?
                            .get(Val::Str("translation_mm".into()))?
                            .get(Val::Int(1i64))?,
                        e.get("lo")?,
                    )?);
                    args430.push(binary(
                        "add",
                        e.get("frame")?
                            .get(Val::Str("translation_mm".into()))?
                            .get(Val::Int(1i64))?,
                        e.get("hi")?,
                    )?);
                    kw431.push(("split".into(), Val::Float(0.0f64)));
                    kw431.push((
                        "tool_angle_degrees".into(),
                        unary("neg", Val::Float(65.0f64))?,
                    ));
                    kw431.push(("tool_end_stock".into(), Val::Float(10.0f64)));
                    fun432.call(args430, kw431)?
                };
                e.set("station", assigned429.clone())?;
                let assigned433 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("cx")?,
                        e.get("station")?.get(Val::Str("outer".into()))?,
                    )?);
                    s.push(Val::None);
                    Val::tuple(s)
                };
                e.get("station")?
                    .set(Val::Str("tool_outer_edges".into()), assigned433.clone())?;
                let assigned434 = {
                    let fun437 = e.get("rear_snaps")?.attr("receiver_tool_ports")?;
                    let mut args435 = Vec::new();
                    let mut kw436 = Vec::new();
                    args435.push(e.get("station")?);
                    fun437.call(args435, kw436)?
                };
                e.get("station")?
                    .set(Val::Str("tool_ports".into()), assigned434.clone())?;
                {
                    let fun440 = e.get("caps")?.attr("append")?;
                    let mut args438 = Vec::new();
                    let mut kw439 = Vec::new();
                    args438.push({
                        let fun443 = e.get("dict")?;
                        let mut args441 = Vec::new();
                        let mut kw442 = Vec::new();
                        args441.push(e.get("common")?);
                        kw442.push(("bore_radius_mm".into(), e.get("radius")?));
                        kw442.push(("snap_station".into(), e.get("station")?));
                        kw442.push(("cap_band_native_x_mm".into(), {
                            let mut s = Vec::new();
                            s.push(e.get("lo")?);
                            s.push(e.get("hi")?);
                            Val::tuple(s)
                        }));
                        kw442.push(("pocket_band_native_x_mm".into(), {
                            let mut s = Vec::new();
                            s.push(binary(
                                "sub",
                                e.get("lo")?,
                                e.get("fits")?.attr("running")?,
                            )?);
                            s.push(binary(
                                "add",
                                e.get("hi")?,
                                e.get("fits")?.attr("running")?,
                            )?);
                            Val::tuple(s)
                        }));
                        kw442.push((
                            "stock_half_width_mm".into(),
                            e.get("station")?.get(Val::Str("outer".into()))?,
                        ));
                        fun443.call(args441, kw442)?
                    });
                    fun440.call(args438, kw439)?
                };
            }
            return Ok({
                let fun451 = e.get("dict")?;
                let mut args449 = Vec::new();
                let mut kw450 = Vec::new();
                args449.push(e.get("caps")?.get(Val::Int(0i64))?);
                kw450.push(("caps".into(), e.get("caps")?));
                kw450.push(("end_stock_mm".into(), {
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        binary(
                            "sub",
                            e.get("bands")?.get(Val::Int(0i64))?.get(Val::Int(0i64))?,
                            e.get("fits")?.attr("running")?,
                        )?,
                        e.get("first")?,
                    )?);
                    s.push(binary(
                        "sub",
                        binary(
                            "sub",
                            e.get("last")?,
                            e.get("bands")?
                                .get(unary("neg", Val::Int(1i64))?)?
                                .get(Val::Int(1i64))?,
                        )?,
                        e.get("fits")?.attr("running")?,
                    )?);
                    Val::tuple(s)
                }));
                fun451.call(args449, kw450)?
            });
            Ok(Val::None)
        })
    })?;
    // _pump_cap_to_world
    e.set("_pump_cap_to_world", {
        let params = vec![("shape".into(), None, false), ("datum".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned452 = e.get("datum")?.get(Val::Str("centre_world_mm".into()))?;
            let unpack453 = unpack(assigned452.clone(), 3)?;
            e.set("cx", unpack453[0].clone())?;
            e.set("_cy", unpack453[1].clone())?;
            e.set("cz", unpack453[2].clone())?;
            return Ok({
                let fun456 = {
                    let fun459 = e.get("shape")?.attr("rotate")?;
                    let mut args457 = Vec::new();
                    let mut kw458 = Vec::new();
                    args457.push({
                        let mut s = Vec::new();
                        s.push(e.get("cx")?);
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    args457.push({
                        let mut s = Vec::new();
                        s.push(e.get("cx")?);
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    args457.push(Val::Float(180.0f64));
                    fun459.call(args457, kw458)?
                }
                .attr("translate")?;
                let mut args454 = Vec::new();
                let mut kw455 = Vec::new();
                args454.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(e.get("cz")?);
                    Val::tuple(s)
                });
                fun456.call(args454, kw455)?
            });
            Ok(Val::None)
        })
    })?;
    // _pump_motor_room
    e.set("_pump_motor_room", {
        let params = vec![
            ("datum".into(), None, false),
            ("seat".into(), Some(Val::Bool(false)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned460 = {
                let mut s = Vec::new();
                s.push(e.get("datum")?.get(Val::Str("can".into()))?);
                s.push(e.get("datum")?.get(Val::Str("frame".into()))?);
                Val::tuple(s)
            };
            let unpack461 = unpack(assigned460.clone(), 2)?;
            e.set("can", unpack461[0].clone())?;
            e.set("frame", unpack461[1].clone())?;
            let assigned462 = {
                let mut s = Vec::new();
                s.push(e.get("can")?.get(Val::Str("axis_direction".into()))?);
                s.push(e.get("can")?.get(Val::Str("axis_point_mm".into()))?);
                Val::tuple(s)
            };
            let unpack463 = unpack(assigned462.clone(), 2)?;
            e.set("axis", unpack463[0].clone())?;
            e.set("origin", unpack463[1].clone())?;
            let assigned464 = e.get("datum")?.get(Val::Str("band_native_x_mm".into()))?;
            let unpack465 = unpack(assigned464.clone(), 2)?;
            e.set("first", unpack465[0].clone())?;
            e.set("last", unpack465[1].clone())?;
            let assigned466 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("first")?, Val::Float(1.0f64))?);
                s.push(e.get("origin")?.get(Val::Int(1i64))?);
                s.push(binary(
                    "add",
                    e.get("origin")?.get(Val::Int(2i64))?,
                    binary(
                        "truediv",
                        binary(
                            "mul",
                            e.get("axis")?.get(Val::Int(2i64))?,
                            binary(
                                "sub",
                                binary("sub", e.get("first")?, Val::Float(1.0f64))?,
                                e.get("origin")?.get(Val::Int(0i64))?,
                            )?,
                        )?,
                        e.get("axis")?.get(Val::Int(0i64))?,
                    )?,
                )?);
                Val::tuple(s)
            };
            e.set("point", assigned466.clone())?;
            let assigned467 = if e.get("seat")?.truthy()? {
                e.get("datum")?
                    .get(Val::Str("seat_bore_radius_mm".into()))?
            } else {
                e.get("datum")?.get(Val::Str("bore_radius_mm".into()))?
            };
            e.set("radius", assigned467.clone())?;
            return Ok({
                let fun470 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args468 = Vec::new();
                let mut kw469 = Vec::new();
                args468.push(e.get("radius")?);
                args468.push(binary(
                    "truediv",
                    binary(
                        "add",
                        binary("sub", e.get("last")?, e.get("first")?)?,
                        Val::Float(2.0f64),
                    )?,
                    e.get("axis")?.get(Val::Int(0i64))?,
                )?);
                args468.push({
                    let fun473 = e.get("cq")?.attr("Vector")?;
                    let mut args471 = Vec::new();
                    let mut kw472 = Vec::new();
                    args471.extend(
                        {
                            let fun476 = e.get("above_core")?.attr("point")?;
                            let mut args474 = Vec::new();
                            let mut kw475 = Vec::new();
                            args474.push(e.get("frame")?);
                            args474.push(e.get("point")?);
                            fun476.call(args474, kw475)?
                        }
                        .iter()?,
                    );
                    fun473.call(args471, kw472)?
                });
                args468.push({
                    let fun479 = e.get("cq")?.attr("Vector")?;
                    let mut args477 = Vec::new();
                    let mut kw478 = Vec::new();
                    args477.extend(
                        {
                            let fun482 = e.get("above_core")?.attr("vector")?;
                            let mut args480 = Vec::new();
                            let mut kw481 = Vec::new();
                            args480.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                            args480.push(e.get("axis")?);
                            fun482.call(args480, kw481)?
                        }
                        .iter()?,
                    );
                    fun479.call(args477, kw478)?
                });
                fun470.call(args468, kw469)?
            });
            Ok(Val::None)
        })
    })?;
    // pump_snap_cap
    e.set("pump_snap_cap", {
        let params = vec![("index".into(), Some(Val::Int(0i64)), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            e.set("fits", rt.import_module("fits")?)?;
            let assigned483 = {
                let fun486 = e.get("pump_cradle_datums")?;
                let mut args484 = Vec::new();
                let mut kw485 = Vec::new();
                fun486.call(args484, kw485)?
            }
            .get(Val::Str("caps".into()))?
            .get(e.get("index")?)?;
            e.set("d", assigned483.clone())?;
            let assigned487 = e.get("d")?.get(Val::Str("snap_station".into()))?;
            e.set("s", assigned487.clone())?;
            e.set("rear_snaps", rt.import_module("rear_snaps")?)?;
            let assigned488 = {
                let mut s = Vec::new();
                s.push(e.get("s")?.get(Val::Str("axis_x".into()))?);
                s.push(e.get("s")?.get(Val::Str("outer".into()))?);
                Val::tuple(s)
            };
            let unpack489 = unpack(assigned488.clone(), 2)?;
            e.set("c", unpack489[0].clone())?;
            e.set("wide", unpack489[1].clone())?;
            let assigned490 = unary(
                "neg",
                binary(
                    "add",
                    e.get("d")?.get(Val::Str("bore_radius_mm".into()))?,
                    e.get("d")?
                        .get(Val::Str("selected".into()))?
                        .get(Val::Str("cap_arch_wall_mm".into()))?,
                )?,
            )?;
            e.set("roof", assigned490.clone())?;
            let assigned491 = e
                .get("d")?
                .get(Val::Str("selected".into()))?
                .get(Val::Str("cap_east_roof_half_width_mm".into()))?;
            e.set("edge", assigned491.clone())?;
            let assigned492 = {
                let fun495 = e.get("rear_snaps")?.attr("cap_section")?;
                let mut args493 = Vec::new();
                let mut kw494 = Vec::new();
                args493.push(e.get("s")?);
                args493.push(unary("neg", e.get("fits")?.attr("slip")?)?);
                args493.push(e.get("roof")?);
                fun495.call(args493, kw494)?
            };
            e.set("section", assigned492.clone())?;
            let assigned496 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("line".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("c")?, e.get("wide")?)?);
                        s.push(e.get("roof")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("c")?, e.get("edge")?)?);
                        s.push(e.get("roof")?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d
            };
            e.get("section")?
                .get(Val::Str("segments".into()))?
                .set(unary("neg", Val::Int(2i64))?, assigned496.clone())?;
            let assigned497 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("line".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("c")?, e.get("edge")?)?);
                        s.push(e.get("roof")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("c")?, e.get("wide")?)?);
                        s.push(e.get("s")?.get(Val::Str("root".into()))?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d
            };
            e.get("section")?
                .get(Val::Str("segments".into()))?
                .set(unary("neg", Val::Int(1i64))?, assigned497.clone())?;
            let assigned498 = {
                let fun501 = e.get("rear_snaps")?.attr("section_solid")?;
                let mut args499 = Vec::new();
                let mut kw500 = Vec::new();
                args499.push(e.get("section")?);
                fun501.call(args499, kw500)?
            };
            e.set("blank", assigned498.clone())?;
            return Ok({
                let fun504 = {
                    let fun507 = {
                        let fun510 = e.get("_pump_cap_to_world")?;
                        let mut args508 = Vec::new();
                        let mut kw509 = Vec::new();
                        args508.push(e.get("blank")?);
                        args508.push(e.get("d")?);
                        fun510.call(args508, kw509)?
                    }
                    .attr("cut")?;
                    let mut args505 = Vec::new();
                    let mut kw506 = Vec::new();
                    args505.push({
                        let fun513 = e.get("_pump_motor_room")?;
                        let mut args511 = Vec::new();
                        let mut kw512 = Vec::new();
                        args511.push(e.get("d")?);
                        fun513.call(args511, kw512)?
                    });
                    fun507.call(args505, kw506)?
                }
                .attr("clean")?;
                let mut args502 = Vec::new();
                let mut kw503 = Vec::new();
                fun504.call(args502, kw503)?
            });
            Ok(Val::None)
        })
    })?;
    // pump_snap_printable
    e.set("pump_snap_printable", {
        let params = vec![("index".into(), Some(Val::Int(0i64)), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned514 = {
                let fun517 = {
                    let fun520 = e.get("pump_snap_cap")?;
                    let mut args518 = Vec::new();
                    let mut kw519 = Vec::new();
                    args518.push(e.get("index")?);
                    fun520.call(args518, kw519)?
                }
                .attr("rotate")?;
                let mut args515 = Vec::new();
                let mut kw516 = Vec::new();
                args515.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                args515.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                args515.push(Val::Float(90.0f64));
                fun517.call(args515, kw516)?
            };
            e.set("shape", assigned514.clone())?;
            let assigned521 = {
                let fun524 = e.get("shape")?.attr("BoundingBox")?;
                let mut args522 = Vec::new();
                let mut kw523 = Vec::new();
                fun524.call(args522, kw523)?
            };
            e.set("b", assigned521.clone())?;
            return Ok({
                let fun527 = e.get("shape")?.attr("translate")?;
                let mut args525 = Vec::new();
                let mut kw526 = Vec::new();
                args525.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "truediv",
                        unary(
                            "neg",
                            binary("add", e.get("b")?.attr("xmin")?, e.get("b")?.attr("xmax")?)?,
                        )?,
                        Val::Float(2.0f64),
                    )?);
                    s.push(binary(
                        "truediv",
                        unary(
                            "neg",
                            binary("add", e.get("b")?.attr("ymin")?, e.get("b")?.attr("ymax")?)?,
                        )?,
                        Val::Float(2.0f64),
                    )?);
                    s.push(unary("neg", e.get("b")?.attr("zmin")?)?);
                    Val::tuple(s)
                });
                fun527.call(args525, kw526)?
            });
            Ok(Val::None)
        })
    })?;
    // pump_cradle
    e.set("pump_cradle", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            e.set("rear_snaps", rt.import_module("rear_snaps")?)?;
            let assigned528 = {
                let fun531 = e.get("pump_cradle_datums")?;
                let mut args529 = Vec::new();
                let mut kw530 = Vec::new();
                fun531.call(args529, kw530)?
            };
            e.set("d", assigned528.clone())?;
            let assigned532 = e.get("d")?.get(Val::Str("centre_world_mm".into()))?;
            let unpack533 = unpack(assigned532.clone(), 3)?;
            e.set("cx", unpack533[0].clone())?;
            e.set("_cy", unpack533[1].clone())?;
            e.set("cz", unpack533[2].clone())?;
            let assigned534 = e.get("d")?.get(Val::Str("band_native_x_mm".into()))?;
            let unpack535 = unpack(assigned534.clone(), 2)?;
            e.set("first", unpack535[0].clone())?;
            e.set("last", unpack535[1].clone())?;
            let assigned536 = e
                .get("d")?
                .get(Val::Str("frame".into()))?
                .get(Val::Str("translation_mm".into()))?
                .get(Val::Int(1i64))?;
            e.set("fy", assigned536.clone())?;
            let assigned537 = {
                let fun540 = e.get("above_core")?.attr("specification")?;
                let mut args538 = Vec::new();
                let mut kw539 = Vec::new();
                fun540.call(args538, kw539)?
            }
            .get(Val::Str("cap_face_z_mm".into()))?;
            e.set("face", assigned537.clone())?;
            let assigned541 = e.get("d")?.get(Val::Str("selected".into()))?;
            e.set("selected", assigned541.clone())?;
            let assigned542 = e
                .get("selected")?
                .get(Val::Str("rail_stop_native_x_mm".into()))?;
            let unpack543 = unpack(assigned542.clone(), 2)?;
            e.set("fore", unpack543[0].clone())?;
            e.set("rear", unpack543[1].clone())?;
            let assigned544 = binary(
                "add",
                e.get("d")?.get(Val::Str("stock_half_width_mm".into()))?,
                Val::Float(3.0f64),
            )?;
            e.set("wide", assigned544.clone())?;
            let assigned545 = Val::Float(24.81f64);
            e.set("half", assigned545.clone())?;
            let assigned546 = {
                let fun549 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args547 = Vec::new();
                let mut kw548 = Vec::new();
                args547.push(binary("mul", Val::Float(2.0f64), e.get("wide")?)?);
                args547.push(binary(
                    "sub",
                    e.get("rear")?.get(Val::Int(1i64))?,
                    e.get("fore")?.get(Val::Int(0i64))?,
                )?);
                args547.push(binary(
                    "add",
                    binary("sub", e.get("cz")?, e.get("face")?)?,
                    Val::Float(0.1f64),
                )?);
                args547.push({
                    let fun552 = e.get("cq")?.attr("Vector")?;
                    let mut args550 = Vec::new();
                    let mut kw551 = Vec::new();
                    args550.push(binary("sub", e.get("cx")?, e.get("wide")?)?);
                    args550.push(binary(
                        "add",
                        e.get("fy")?,
                        e.get("fore")?.get(Val::Int(0i64))?,
                    )?);
                    args550.push(binary("sub", e.get("face")?, Val::Float(0.1f64))?);
                    fun552.call(args550, kw551)?
                });
                fun549.call(args547, kw548)?
            };
            e.set("body", assigned546.clone())?;
            let assigned553 = {
                let fun556 = e.get("body")?.attr("cut")?;
                let mut args554 = Vec::new();
                let mut kw555 = Vec::new();
                args554.push({
                    let fun559 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                    let mut args557 = Vec::new();
                    let mut kw558 = Vec::new();
                    args557.push(binary("mul", Val::Float(2.0f64), e.get("half")?)?);
                    args557.push(binary(
                        "add",
                        binary(
                            "sub",
                            e.get("rear")?.get(Val::Int(1i64))?,
                            e.get("fore")?.get(Val::Int(0i64))?,
                        )?,
                        Val::Float(0.2f64),
                    )?);
                    args557.push(binary(
                        "add",
                        binary("sub", e.get("cz")?, e.get("face")?)?,
                        Val::Float(1.0f64),
                    )?);
                    args557.push({
                        let fun562 = e.get("cq")?.attr("Vector")?;
                        let mut args560 = Vec::new();
                        let mut kw561 = Vec::new();
                        args560.push(binary("sub", e.get("cx")?, e.get("half")?)?);
                        args560.push(binary(
                            "sub",
                            binary("add", e.get("fy")?, e.get("fore")?.get(Val::Int(0i64))?)?,
                            Val::Float(0.1f64),
                        )?);
                        args560.push(e.get("face")?);
                        fun562.call(args560, kw561)?
                    });
                    fun559.call(args557, kw558)?
                });
                fun556.call(args554, kw555)?
            };
            e.set("body", assigned553.clone())?;
            e.set("fits", rt.import_module("fits")?)?;
            for item563 in e.get("d")?.get(Val::Str("rail_rooms".into()))?.iter()? {
                e.set("rail", item563)?;
                let assigned564 = e
                    .get("rail")?
                    .get(Val::Str("floor_planes".into()))?
                    .get(Val::Int(0i64))?;
                let unpack565 = unpack(assigned564.clone(), 3)?;
                e.set("a", unpack565[0].clone())?;
                e.set("b", unpack565[1].clone())?;
                e.set("c", unpack565[2].clone())?;
                e.set(
                    "c",
                    binary(
                        "sub",
                        e.get("c")?,
                        binary("mul", e.get("fits")?.attr("running")?, {
                            let fun568 = e.get("math")?.attr("sqrt")?;
                            let mut args566 = Vec::new();
                            let mut kw567 = Vec::new();
                            args566.push(binary(
                                "add",
                                binary(
                                    "add",
                                    Val::Float(1.0f64),
                                    binary("mul", e.get("a")?, e.get("a")?)?,
                                )?,
                                binary("mul", e.get("b")?, e.get("b")?)?,
                            )?);
                            fun568.call(args566, kw567)?
                        })?,
                    )?,
                )?;
                let assigned569 = {
                    let mut s = Vec::new();
                    Val::list(s)
                };
                e.set("profiles", assigned569.clone())?;
                for item570 in {
                    let mut s = Vec::new();
                    s.push(e.get("fore")?.get(Val::Int(1i64))?);
                    s.push(e.get("rear")?.get(Val::Int(0i64))?);
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("x", item570)?;
                    let assigned571 = e.get("rail")?.get(Val::Str("outer_y_mm".into()))?;
                    e.set("outer", assigned571.clone())?;
                    let assigned572 = binary(
                        "mul",
                        e.get("rail")?.get(Val::Str("side".into()))?,
                        e.get("half")?,
                    )?;
                    e.set("near", assigned572.clone())?;
                    let assigned573 = {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("outer")?);
                            s.push(binary(
                                "add",
                                binary(
                                    "add",
                                    binary("mul", e.get("a")?, e.get("x")?)?,
                                    binary("mul", e.get("b")?, e.get("outer")?)?,
                                )?,
                                e.get("c")?,
                            )?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("near")?);
                            s.push(binary(
                                "add",
                                binary(
                                    "add",
                                    binary("mul", e.get("a")?, e.get("x")?)?,
                                    binary("mul", e.get("b")?, e.get("near")?)?,
                                )?,
                                e.get("c")?,
                            )?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("near")?);
                            s.push(Val::Float(100.0f64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("outer")?);
                            s.push(Val::Float(100.0f64));
                            Val::tuple(s)
                        });
                        Val::list(s)
                    };
                    e.set("yz", assigned573.clone())?;
                    {
                        let fun576 = e.get("profiles")?.attr("append")?;
                        let mut args574 = Vec::new();
                        let mut kw575 = Vec::new();
                        args574.push({
                            let fun579 = e.get("cq")?.attr("Wire")?.attr("makePolygon")?;
                            let mut args577 = Vec::new();
                            let mut kw578 = Vec::new();
                            args577.push({
                                let e = e.child();
                                let out580 = Val::list(vec![]);
                                for item581 in e.get("yz")?.iter()? {
                                    let unpack582 = unpack(item581, 2)?;
                                    e.set("y", unpack582[0].clone())?;
                                    e.set("z", unpack582[1].clone())?;
                                    out580.attr("append")?.call(
                                        vec![{
                                            let fun585 = e.get("cq")?.attr("Vector")?;
                                            let mut args583 = Vec::new();
                                            let mut kw584 = Vec::new();
                                            args583.push(e.get("x")?);
                                            args583.push(e.get("y")?);
                                            args583.push(e.get("z")?);
                                            fun585.call(args583, kw584)?
                                        }],
                                        vec![],
                                    )?;
                                }
                                out580
                            });
                            kw578.push(("close".into(), Val::Bool(true)));
                            fun579.call(args577, kw578)?
                        });
                        fun576.call(args574, kw575)?
                    };
                }
                let assigned586 = {
                    let fun589 = {
                        let fun592 = e.get("cq")?.attr("Solid")?.attr("makeLoft")?;
                        let mut args590 = Vec::new();
                        let mut kw591 = Vec::new();
                        args590.push(e.get("profiles")?);
                        kw591.push(("ruled".into(), Val::Bool(true)));
                        fun592.call(args590, kw591)?
                    }
                    .attr("moved")?;
                    let mut args587 = Vec::new();
                    let mut kw588 = Vec::new();
                    args587.push({
                        let fun595 = e.get("above_core")?.attr("frame_location")?;
                        let mut args593 = Vec::new();
                        let mut kw594 = Vec::new();
                        args593.push(e.get("d")?.get(Val::Str("frame".into()))?);
                        fun595.call(args593, kw594)?
                    });
                    fun589.call(args587, kw588)?
                };
                e.set("room", assigned586.clone())?;
                let assigned596 = {
                    let fun599 = e.get("body")?.attr("cut")?;
                    let mut args597 = Vec::new();
                    let mut kw598 = Vec::new();
                    args597.push(e.get("room")?);
                    fun599.call(args597, kw598)?
                };
                e.set("body", assigned596.clone())?;
            }
            let assigned600 = e
                .get("d")?
                .get(Val::Str("frame".into()))?
                .get(Val::Str("translation_mm".into()))?
                .get(Val::Int(2i64))?;
            e.set("tz", assigned600.clone())?;
            let assigned601 = e
                .get("selected")?
                .get(Val::Str("rail_stop_native_z_mm".into()))?;
            e.set("head", assigned601.clone())?;
            let assigned602 = binary(
                "truediv",
                binary(
                    "sub",
                    binary("sub", e.get("cz")?, e.get("tz")?)?,
                    e.get("head")?,
                )?,
                e.get("first")?,
            )?;
            e.set("slope", assigned602.clone())?;
            for item603 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("fore")?.get(Val::Int(0i64))?,
                        Val::Float(0.1f64),
                    )?);
                    s.push(e.get("fore")?.get(Val::Int(1i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("fore")?.get(Val::Int(1i64))?);
                    s.push(e.get("first")?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack636 = unpack(item603, 2)?;
                e.set("xa", unpack636[0].clone())?;
                e.set("xb", unpack636[1].clone())?;
                let assigned604 = {
                    let mut s = Vec::new();
                    Val::list(s)
                };
                e.set("profiles", assigned604.clone())?;
                for item605 in {
                    let mut s = Vec::new();
                    s.push(e.get("xa")?);
                    s.push(e.get("xb")?);
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("x", item605)?;
                    let assigned606 = {
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            binary("add", e.get("tz")?, e.get("head")?)?,
                            binary("mul", e.get("slope")?, {
                                let fun609 = e.get("max")?;
                                let mut args607 = Vec::new();
                                let mut kw608 = Vec::new();
                                args607.push(e.get("x")?);
                                args607.push(e.get("fore")?.get(Val::Int(1i64))?);
                                fun609.call(args607, kw608)?
                            })?,
                        )?);
                        s.push(binary("add", e.get("fy")?, e.get("x")?)?);
                        Val::tuple(s)
                    };
                    let unpack610 = unpack(assigned606.clone(), 2)?;
                    e.set("z", unpack610[0].clone())?;
                    e.set("y", unpack610[1].clone())?;
                    {
                        let fun613 = e.get("profiles")?.attr("append")?;
                        let mut args611 = Vec::new();
                        let mut kw612 = Vec::new();
                        args611.push({
                            let fun616 = e.get("cq")?.attr("Wire")?.attr("makePolygon")?;
                            let mut args614 = Vec::new();
                            let mut kw615 = Vec::new();
                            args614.push({
                                let mut s = Vec::new();
                                s.push({
                                    let fun619 = e.get("cq")?.attr("Vector")?;
                                    let mut args617 = Vec::new();
                                    let mut kw618 = Vec::new();
                                    args617.push(binary(
                                        "sub",
                                        binary("sub", e.get("cx")?, e.get("wide")?)?,
                                        Val::Float(0.1f64),
                                    )?);
                                    args617.push(e.get("y")?);
                                    args617.push(e.get("z")?);
                                    fun619.call(args617, kw618)?
                                });
                                s.push({
                                    let fun622 = e.get("cq")?.attr("Vector")?;
                                    let mut args620 = Vec::new();
                                    let mut kw621 = Vec::new();
                                    args620.push(binary(
                                        "add",
                                        binary("add", e.get("cx")?, e.get("wide")?)?,
                                        Val::Float(0.1f64),
                                    )?);
                                    args620.push(e.get("y")?);
                                    args620.push(e.get("z")?);
                                    fun622.call(args620, kw621)?
                                });
                                s.push({
                                    let fun625 = e.get("cq")?.attr("Vector")?;
                                    let mut args623 = Vec::new();
                                    let mut kw624 = Vec::new();
                                    args623.push(binary(
                                        "add",
                                        binary("add", e.get("cx")?, e.get("wide")?)?,
                                        Val::Float(0.1f64),
                                    )?);
                                    args623.push(e.get("y")?);
                                    args623.push(binary("add", e.get("cz")?, Val::Float(1.0f64))?);
                                    fun625.call(args623, kw624)?
                                });
                                s.push({
                                    let fun628 = e.get("cq")?.attr("Vector")?;
                                    let mut args626 = Vec::new();
                                    let mut kw627 = Vec::new();
                                    args626.push(binary(
                                        "sub",
                                        binary("sub", e.get("cx")?, e.get("wide")?)?,
                                        Val::Float(0.1f64),
                                    )?);
                                    args626.push(e.get("y")?);
                                    args626.push(binary("add", e.get("cz")?, Val::Float(1.0f64))?);
                                    fun628.call(args626, kw627)?
                                });
                                Val::list(s)
                            });
                            kw615.push(("close".into(), Val::Bool(true)));
                            fun616.call(args614, kw615)?
                        });
                        fun613.call(args611, kw612)?
                    };
                }
                let assigned629 = {
                    let fun632 = e.get("body")?.attr("cut")?;
                    let mut args630 = Vec::new();
                    let mut kw631 = Vec::new();
                    args630.push({
                        let fun635 = e.get("cq")?.attr("Solid")?.attr("makeLoft")?;
                        let mut args633 = Vec::new();
                        let mut kw634 = Vec::new();
                        args633.push(e.get("profiles")?);
                        kw634.push(("ruled".into(), Val::Bool(true)));
                        fun635.call(args633, kw634)?
                    });
                    fun632.call(args630, kw631)?
                };
                e.set("body", assigned629.clone())?;
            }
            for item637 in e.get("d")?.get(Val::Str("caps".into()))?.iter()? {
                e.set("cap", item637)?;
                for item638 in {
                    let fun648 = e.get("rear_snaps")?.attr("pockets")?;
                    let mut args646 = Vec::new();
                    let mut kw647 = Vec::new();
                    args646.push({
                        let fun651 = e.get("dict")?;
                        let mut args649 = Vec::new();
                        let mut kw650 = Vec::new();
                        args649.push(e.get("cap")?.get(Val::Str("snap_station".into()))?);
                        kw650.push(("outer".into(), e.get("wide")?));
                        fun651.call(args649, kw650)?
                    });
                    fun648.call(args646, kw647)?
                }
                .iter()?
                {
                    e.set("pocket", item638)?;
                    let assigned639 = {
                        let fun642 = e.get("body")?.attr("cut")?;
                        let mut args640 = Vec::new();
                        let mut kw641 = Vec::new();
                        args640.push({
                            let fun645 = e.get("_pump_cap_to_world")?;
                            let mut args643 = Vec::new();
                            let mut kw644 = Vec::new();
                            args643.push(e.get("pocket")?);
                            args643.push(e.get("cap")?);
                            fun645.call(args643, kw644)?
                        });
                        fun642.call(args640, kw641)?
                    };
                    e.set("body", assigned639.clone())?;
                }
            }
            let assigned652 = {
                let mut s = Vec::new();
                s.push(binary("add", e.get("cx")?, e.get("wide")?)?);
                s.push(binary(
                    "add",
                    e.get("fy")?,
                    e.get("rear")?.get(Val::Int(1i64))?,
                )?);
                Val::tuple(s)
            };
            let unpack653 = unpack(assigned652.clone(), 2)?;
            e.set("east", unpack653[0].clone())?;
            e.set("aft", unpack653[1].clone())?;
            let assigned654 = binary(
                "add",
                {
                    let fun657 = e.get("max")?;
                    let mut args655 = Vec::new();
                    let mut kw656 = Vec::new();
                    args655.push({
                        let e = e.child();
                        let out658 = Val::list(vec![]);
                        for item659 in e.get("d")?.get(Val::Str("caps".into()))?.iter()? {
                            e.set("cap", item659)?;
                            out658.attr("append")?.call(
                                vec![
                                    e.get("cap")?
                                        .get(Val::Str("snap_station".into()))?
                                        .get(Val::Str("y1".into()))?,
                                ],
                                vec![],
                            )?;
                        }
                        out658
                    });
                    fun657.call(args655, kw656)?
                },
                e.get("fits")?.attr("running")?,
            )?;
            e.set("cap_end", assigned654.clone())?;
            let assigned660 = {
                let fun663 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args661 = Vec::new();
                let mut kw662 = Vec::new();
                args661.push(binary(
                    "add",
                    binary(
                        "sub",
                        e.get("east")?,
                        binary(
                            "add",
                            e.get("cx")?,
                            e.get("d")?.get(Val::Str("stock_half_width_mm".into()))?,
                        )?,
                    )?,
                    Val::Float(0.1f64),
                )?);
                args661.push(binary(
                    "add",
                    binary("sub", e.get("aft")?, e.get("cap_end")?)?,
                    Val::Float(0.1f64),
                )?);
                args661.push(binary(
                    "add",
                    binary("sub", e.get("cz")?, e.get("face")?)?,
                    Val::Float(0.4f64),
                )?);
                args661.push({
                    let fun666 = e.get("cq")?.attr("Vector")?;
                    let mut args664 = Vec::new();
                    let mut kw665 = Vec::new();
                    args664.push(binary(
                        "add",
                        e.get("cx")?,
                        e.get("d")?.get(Val::Str("stock_half_width_mm".into()))?,
                    )?);
                    args664.push(e.get("cap_end")?);
                    args664.push(binary("sub", e.get("face")?, Val::Float(0.2f64))?);
                    fun666.call(args664, kw665)?
                });
                fun663.call(args661, kw662)?
            };
            e.set("clearance", assigned660.clone())?;
            let assigned667 = {
                let fun670 = e.get("body")?.attr("cut")?;
                let mut args668 = Vec::new();
                let mut kw669 = Vec::new();
                args668.push(e.get("clearance")?);
                fun670.call(args668, kw669)?
            };
            e.set("body", assigned667.clone())?;
            return Ok({
                let fun673 = e.get("body")?.attr("clean")?;
                let mut args671 = Vec::new();
                let mut kw672 = Vec::new();
                fun673.call(args671, kw672)?
            });
            Ok(Val::None)
        })
    })?;
    // pump_lid_clearance
    e.set("pump_lid_clearance", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned674 = {
                let fun677 = e.get("pump_cradle_datums")?;
                let mut args675 = Vec::new();
                let mut kw676 = Vec::new();
                fun677.call(args675, kw676)?
            };
            e.set("d", assigned674.clone())?;
            let assigned678 = e
                .get("d")?
                .get(Val::Str("centre_world_mm".into()))?
                .get(Val::Int(0i64))?;
            e.set("cx", assigned678.clone())?;
            let assigned679 = e
                .get("d")?
                .get(Val::Str("frame".into()))?
                .get(Val::Str("translation_mm".into()))?
                .get(Val::Int(1i64))?;
            e.set("fy", assigned679.clone())?;
            let assigned680 = e.get("d")?.get(Val::Str("selected".into()))?;
            e.set("selected", assigned680.clone())?;
            let assigned681 = e
                .get("selected")?
                .get(Val::Str("cover_channel_fore_native_x_mm".into()))?;
            e.set("fore", assigned681.clone())?;
            let assigned682 = e
                .get("selected")?
                .get(Val::Str("rail_stop_native_x_mm".into()))?
                .get(Val::Int(1i64))?
                .get(Val::Int(1i64))?;
            e.set("aft", assigned682.clone())?;
            let assigned683 = {
                let fun686 = e.get("above_core")?.attr("specification")?;
                let mut args684 = Vec::new();
                let mut kw685 = Vec::new();
                fun686.call(args684, kw685)?
            }
            .get(Val::Str("cap_face_z_mm".into()))?;
            e.set("face", assigned683.clone())?;
            let assigned687 = e
                .get("selected")?
                .get(Val::Str("cover_channel_recess_mm".into()))?;
            e.set("depth", assigned687.clone())?;
            return Ok({
                let fun690 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args688 = Vec::new();
                let mut kw689 = Vec::new();
                args688.push(Val::Float(49.62f64));
                args688.push(binary(
                    "add",
                    binary("sub", e.get("aft")?, e.get("fore")?)?,
                    Val::Float(0.2f64),
                )?);
                args688.push(binary("add", e.get("depth")?, Val::Float(0.1f64))?);
                args688.push({
                    let fun693 = e.get("cq")?.attr("Vector")?;
                    let mut args691 = Vec::new();
                    let mut kw692 = Vec::new();
                    args691.push(binary("sub", e.get("cx")?, Val::Float(24.81f64))?);
                    args691.push(binary(
                        "sub",
                        binary("add", e.get("fy")?, e.get("fore")?)?,
                        Val::Float(0.1f64),
                    )?);
                    args691.push(binary("sub", e.get("face")?, e.get("depth")?)?);
                    fun693.call(args691, kw692)?
                });
                fun690.call(args688, kw689)?
            });
            Ok(Val::None)
        })
    })?;
    // valve_support_datums
    e.set("valve_support_datums", {
        let params = vec![
            ("name".into(), None, false),
            ("face_z".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned694 = {
                let fun697 = e.get("importlib")?.attr("import_module")?;
                let mut args695 = Vec::new();
                let mut kw696 = Vec::new();
                args695.push(Val::Str("valve_seat".into()));
                fun697.call(args695, kw696)?
            };
            e.set("seat", assigned694.clone())?;
            let assigned698 = {
                let fun701 = e.get("importlib")?.attr("import_module")?;
                let mut args699 = Vec::new();
                let mut kw700 = Vec::new();
                args699.push(Val::Str("_cold_core_interface".into()));
                fun701.call(args699, kw700)?
            };
            e.set("core", assigned698.clone())?;
            let assigned702 = {
                let fun705 = e.get("above_core")?.attr("pose")?;
                let mut args703 = Vec::new();
                let mut kw704 = Vec::new();
                args703.push(e.get("name")?);
                fun705.call(args703, kw704)?
            };
            e.set("frame", assigned702.clone())?;
            let assigned706 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", e.get("seat")?.attr("seat_half_x")?)?);
                    s.push(e.get("seat")?.attr("seat_half_x")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", e.get("seat")?.attr("seat_half_y")?)?);
                    s.push(e.get("seat")?.attr("seat_half_y")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("seat")?.attr("socket_floor_z")?,
                        e.get("seat")?.attr("wall")?,
                    )?);
                    s.push(e.get("seat")?.attr("seat_top_z")?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            };
            e.set("limits", assigned706.clone())?;
            let assigned707 = {
                let e = e.child();
                let out708 = Val::list(vec![]);
                for item709 in {
                    let fun712 = e.get("itertools")?.attr("product")?;
                    let mut args710 = Vec::new();
                    let mut kw711 = Vec::new();
                    args710.extend(e.get("limits")?.iter()?);
                    fun712.call(args710, kw711)?
                }
                .iter()?
                {
                    e.set("point", item709)?;
                    out708.attr("append")?.call(
                        vec![{
                            let fun715 = e.get("above_core")?.attr("point")?;
                            let mut args713 = Vec::new();
                            let mut kw714 = Vec::new();
                            args713.push(e.get("frame")?);
                            args713.push(e.get("point")?);
                            fun715.call(args713, kw714)?
                        }],
                        vec![],
                    )?;
                }
                out708
            };
            e.set("corners", assigned707.clone())?;
            let assigned716 = {
                let fun719 = e.get("tuple")?;
                let mut args717 = Vec::new();
                let mut kw718 = Vec::new();
                args717.push({
                    let e = e.child();
                    let out720 = Val::list(vec![]);
                    for item721 in {
                        let fun724 = e.get("range")?;
                        let mut args722 = Vec::new();
                        let mut kw723 = Vec::new();
                        args722.push(Val::Int(3i64));
                        fun724.call(args722, kw723)?
                    }
                    .iter()?
                    {
                        e.set("i", item721)?;
                        out720.attr("append")?.call(
                            vec![{
                                let fun727 = e.get("min")?;
                                let mut args725 = Vec::new();
                                let mut kw726 = Vec::new();
                                args725.push({
                                    let e = e.child();
                                    let out728 = Val::list(vec![]);
                                    for item729 in e.get("corners")?.iter()? {
                                        e.set("point", item729)?;
                                        out728.attr("append")?.call(
                                            vec![e.get("point")?.get(e.get("i")?)?],
                                            vec![],
                                        )?;
                                    }
                                    out728
                                });
                                fun727.call(args725, kw726)?
                            }],
                            vec![],
                        )?;
                    }
                    out720
                });
                fun719.call(args717, kw718)?
            };
            e.set("low", assigned716.clone())?;
            let assigned730 = {
                let fun733 = e.get("tuple")?;
                let mut args731 = Vec::new();
                let mut kw732 = Vec::new();
                args731.push({
                    let e = e.child();
                    let out734 = Val::list(vec![]);
                    for item735 in {
                        let fun738 = e.get("range")?;
                        let mut args736 = Vec::new();
                        let mut kw737 = Vec::new();
                        args736.push(Val::Int(3i64));
                        fun738.call(args736, kw737)?
                    }
                    .iter()?
                    {
                        e.set("i", item735)?;
                        out734.attr("append")?.call(
                            vec![{
                                let fun741 = e.get("max")?;
                                let mut args739 = Vec::new();
                                let mut kw740 = Vec::new();
                                args739.push({
                                    let e = e.child();
                                    let out742 = Val::list(vec![]);
                                    for item743 in e.get("corners")?.iter()? {
                                        e.set("point", item743)?;
                                        out742.attr("append")?.call(
                                            vec![e.get("point")?.get(e.get("i")?)?],
                                            vec![],
                                        )?;
                                    }
                                    out742
                                });
                                fun741.call(args739, kw740)?
                            }],
                            vec![],
                        )?;
                    }
                    out734
                });
                fun733.call(args731, kw732)?
            };
            e.set("high", assigned730.clone())?;
            if {
                let v744 = e.get("name")?;
                let v745 = Val::Str("valve-v-b".into());
                Val::Bool(compare("eq", v744.clone(), v745.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned746 = {
                    let mut s = Vec::new();
                    s.push(
                        {
                            let fun749 = e.get("above_core")?.attr("specification")?;
                            let mut args747 = Vec::new();
                            let mut kw748 = Vec::new();
                            fun749.call(args747, kw748)?
                        }
                        .get(Val::Str("vb_mount".into()))?
                        .get(Val::Str("seat_wall_bounds_mm".into()))?
                        .get(Val::Int(0i64))?
                        .get(Val::Int(0i64))?,
                    );
                    s.push(e.get("low")?.get(Val::Int(1i64))?);
                    s.push(e.get("low")?.get(Val::Int(2i64))?);
                    Val::tuple(s)
                };
                e.set("low", assigned746.clone())?;
                let assigned750 = {
                    let mut s = Vec::new();
                    s.extend(
                        e.get("high")?
                            .get(Val::Slice {
                                start: None,
                                stop: Some(Val::Int(2i64).integer()?),
                                step: 1,
                            })?
                            .iter()?,
                    );
                    s.push({
                        let fun753 = e.get("max")?;
                        let mut args751 = Vec::new();
                        let mut kw752 = Vec::new();
                        args751.push(e.get("high")?.get(Val::Int(2i64))?);
                        args751.push(
                            {
                                let fun756 = e.get("above_core")?.attr("specification")?;
                                let mut args754 = Vec::new();
                                let mut kw755 = Vec::new();
                                fun756.call(args754, kw755)?
                            }
                            .get(Val::Str("vb_mount".into()))?
                            .get(Val::Str("seat_wall_bounds_mm".into()))?
                            .get(Val::Int(1i64))?
                            .get(Val::Int(2i64))?,
                        );
                        fun753.call(args751, kw752)?
                    });
                    Val::tuple(s)
                };
                e.set("high", assigned750.clone())?;
            }
            let assigned757 = if {
                let v758 = e.get("face_z")?;
                let v759 = Val::None;
                Val::Bool(compare("is", v758.clone(), v759.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun762 = e.get("above_core")?.attr("specification")?;
                    let mut args760 = Vec::new();
                    let mut kw761 = Vec::new();
                    fun762.call(args760, kw761)?
                }
                .get(Val::Str("cap_face_z_mm".into()))?
            } else {
                {
                    let fun765 = e.get("above_core")?.attr("point")?;
                    let mut args763 = Vec::new();
                    let mut kw764 = Vec::new();
                    args763.push({
                        let fun768 = e.get("above_core")?.attr("cap_lid_pose")?;
                        let mut args766 = Vec::new();
                        let mut kw767 = Vec::new();
                        fun768.call(args766, kw767)?
                    });
                    args763.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("face_z")?);
                        Val::tuple(s)
                    });
                    fun765.call(args763, kw764)?
                }
                .get(Val::Int(2i64))?
            };
            e.set("face", assigned757.clone())?;
            let assigned769 = binary(
                "truediv",
                e.get("core")?.attr("outer_shell_y_length")?,
                Val::Float(2.0f64),
            )?;
            e.set("half", assigned769.clone())?;
            let assigned770 = {
                let mut s = Vec::new();
                s.push({
                    let fun773 = e.get("min")?;
                    let mut args771 = Vec::new();
                    let mut kw772 = Vec::new();
                    args771.push(e.get("half")?);
                    args771.push(e.get("high")?.get(Val::Int(0i64))?);
                    fun773.call(args771, kw772)?
                });
                s.push(e.get("high")?.get(Val::Int(1i64))?);
                s.push(e.get("low")?.get(Val::Int(2i64))?);
                Val::tuple(s)
            };
            e.set("root_high", assigned770.clone())?;
            let assigned774 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("bearing_min_world_mm".into()), e.get("low")?)?;
                d.set(Val::Str("bearing_max_world_mm".into()), e.get("high")?)?;
                d.set(Val::Str("root_min_world_mm".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let fun777 = e.get("max")?;
                        let mut args775 = Vec::new();
                        let mut kw776 = Vec::new();
                        args775.push(unary("neg", e.get("half")?)?);
                        args775.push(e.get("low")?.get(Val::Int(0i64))?);
                        fun777.call(args775, kw776)?
                    });
                    s.push(e.get("low")?.get(Val::Int(1i64))?);
                    s.push(e.get("face")?);
                    Val::tuple(s)
                })?;
                d.set(
                    Val::Str("socket_backing_mm".into()),
                    e.get("seat")?.attr("wall")?,
                )?;
                d
            };
            e.set("data", assigned774.clone())?;
            if {
                let v778 = e.get("name")?;
                let v779 = {
                    let mut s = Vec::new();
                    s.push(Val::Str("valve-v-a".into()));
                    s.push(Val::Str("vk-solenoid".into()));
                    Val::tuple(s)
                };
                Val::Bool(compare("in", v778.clone(), v779.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned780 = {
                    let fun783 = e.get("importlib")?.attr("import_module")?;
                    let mut args781 = Vec::new();
                    let mut kw782 = Vec::new();
                    args781.push(Val::Str("neofit_stem_elbow".into()));
                    fun783.call(args781, kw782)?
                };
                e.set("elbow", assigned780.clone())?;
                let assigned784 = {
                    let fun787 = e.get("above_core")?.attr("point")?;
                    let mut args785 = Vec::new();
                    let mut kw786 = Vec::new();
                    args785.push(e.get("frame")?);
                    args785.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("seat")?.attr("valve")?.attr("port_center_z")?);
                        Val::tuple(s)
                    });
                    fun787.call(args785, kw786)?
                }
                .get(Val::Int(1i64))?;
                e.set("port_y", assigned784.clone())?;
                let assigned788 = binary(
                    "sub",
                    binary("sub", e.get("port_y")?, {
                        let fun791 = e.get("max")?;
                        let mut args789 = Vec::new();
                        let mut kw790 = Vec::new();
                        args789.push(e.get("seat")?.attr("valve")?.attr("port_radius")?);
                        args789.push(binary(
                            "truediv",
                            e.get("elbow")?.attr("COLLAR_OD")?,
                            Val::Float(2.0f64),
                        )?);
                        fun791.call(args789, kw790)?
                    })?,
                    e.get("seat")?.attr("fits")?.attr("slip")?,
                )?;
                e.set("aft", assigned788.clone())?;
                let assigned792 = {
                    let mut s = Vec::new();
                    s.push(e.get("root_high")?.get(Val::Int(0i64))?);
                    s.push(e.get("aft")?);
                    s.push(e.get("root_high")?.get(Val::Int(2i64))?);
                    Val::tuple(s)
                };
                e.set("root_high", assigned792.clone())?;
                {
                    let fun795 = e.get("data")?.attr("update")?;
                    let mut args793 = Vec::new();
                    let mut kw794 = Vec::new();
                    kw794.push(("port_throat_aft_world_y_mm".into(), e.get("aft")?));
                    kw794.push((
                        "port_throat_clearance_mm".into(),
                        e.get("seat")?.attr("fits")?.attr("slip")?,
                    ));
                    fun795.call(args793, kw794)?
                };
            }
            let assigned796 = e.get("root_high")?;
            e.get("data")?
                .set(Val::Str("root_max_world_mm".into()), assigned796.clone())?;
            let assigned797 = binary(
                "sub",
                e.get("root_high")?.get(Val::Int(1i64))?,
                e.get("low")?.get(Val::Int(1i64))?,
            )?;
            e.get("data")?
                .set(Val::Str("root_depth_mm".into()), assigned797.clone())?;
            return Ok(e.get("data")?);
            Ok(Val::None)
        })
    })?;
    // valve_support
    e.set("valve_support", {
        let params = vec![
            ("name".into(), None, false),
            ("face_z".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned798 = {
                let fun801 = e.get("importlib")?.attr("import_module")?;
                let mut args799 = Vec::new();
                let mut kw800 = Vec::new();
                args799.push(Val::Str("valve_seat".into()));
                fun801.call(args799, kw800)?
            };
            e.set("seat", assigned798.clone())?;
            let assigned802 = {
                let fun805 = e.get("valve_support_datums")?;
                let mut args803 = Vec::new();
                let mut kw804 = Vec::new();
                args803.push(e.get("name")?);
                args803.push(e.get("face_z")?);
                fun805.call(args803, kw804)?
            };
            e.set("data", assigned802.clone())?;
            // block
            e.set("block", {
                let params = vec![("low".into(), None, false), ("high".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let fun808 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                        let mut args806 = Vec::new();
                        let mut kw807 = Vec::new();
                        args806.extend(
                            {
                                let e = e.child();
                                let out809 = Val::list(vec![]);
                                for item810 in {
                                    let fun813 = e.get("range")?;
                                    let mut args811 = Vec::new();
                                    let mut kw812 = Vec::new();
                                    args811.push(Val::Int(3i64));
                                    fun813.call(args811, kw812)?
                                }
                                .iter()?
                                {
                                    e.set("i", item810)?;
                                    out809.attr("append")?.call(
                                        vec![binary(
                                            "sub",
                                            e.get("high")?.get(e.get("i")?)?,
                                            e.get("low")?.get(e.get("i")?)?,
                                        )?],
                                        vec![],
                                    )?;
                                }
                                out809
                            }
                            .iter()?,
                        );
                        args806.push({
                            let fun816 = e.get("cq")?.attr("Vector")?;
                            let mut args814 = Vec::new();
                            let mut kw815 = Vec::new();
                            args814.extend(e.get("low")?.iter()?);
                            fun816.call(args814, kw815)?
                        });
                        fun808.call(args806, kw807)?
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned817 = {
                let fun820 = {
                    let fun823 = e.get("block")?;
                    let mut args821 = Vec::new();
                    let mut kw822 = Vec::new();
                    args821.push(
                        e.get("data")?
                            .get(Val::Str("bearing_min_world_mm".into()))?,
                    );
                    args821.push(
                        e.get("data")?
                            .get(Val::Str("bearing_max_world_mm".into()))?,
                    );
                    fun823.call(args821, kw822)?
                }
                .attr("fuse")?;
                let mut args818 = Vec::new();
                let mut kw819 = Vec::new();
                args818.push({
                    let fun826 = e.get("block")?;
                    let mut args824 = Vec::new();
                    let mut kw825 = Vec::new();
                    args824.push(e.get("data")?.get(Val::Str("root_min_world_mm".into()))?);
                    args824.push(e.get("data")?.get(Val::Str("root_max_world_mm".into()))?);
                    fun826.call(args824, kw825)?
                });
                fun820.call(args818, kw819)?
            };
            e.set("wall", assigned817.clone())?;
            let assigned827 = {
                let fun830 = e.get("above_core")?.attr("location")?;
                let mut args828 = Vec::new();
                let mut kw829 = Vec::new();
                args828.push(e.get("name")?);
                fun830.call(args828, kw829)?
            };
            e.set("location", assigned827.clone())?;
            let assigned831 = {
                let fun834 = {
                    let fun837 = {
                        let fun840 = e.get("seat")?.attr("build_sockets")?;
                        let mut args838 = Vec::new();
                        let mut kw839 = Vec::new();
                        fun840.call(args838, kw839)?
                    }
                    .attr("val")?;
                    let mut args835 = Vec::new();
                    let mut kw836 = Vec::new();
                    fun837.call(args835, kw836)?
                }
                .attr("moved")?;
                let mut args832 = Vec::new();
                let mut kw833 = Vec::new();
                args832.push(e.get("location")?);
                fun834.call(args832, kw833)?
            };
            e.set("sockets", assigned831.clone())?;
            let assigned841 = {
                let fun844 = {
                    let fun847 = {
                        let fun850 = e.get("seat")?.attr("build_port_channel")?;
                        let mut args848 = Vec::new();
                        let mut kw849 = Vec::new();
                        args848.push(binary(
                            "add",
                            binary(
                                "mul",
                                Val::Float(2.0f64),
                                e.get("seat")?.attr("seat_half_y")?,
                            )?,
                            Val::Float(2.0f64),
                        )?);
                        fun850.call(args848, kw849)?
                    }
                    .attr("val")?;
                    let mut args845 = Vec::new();
                    let mut kw846 = Vec::new();
                    fun847.call(args845, kw846)?
                }
                .attr("moved")?;
                let mut args842 = Vec::new();
                let mut kw843 = Vec::new();
                args842.push(e.get("location")?);
                fun844.call(args842, kw843)?
            };
            e.set("channel", assigned841.clone())?;
            return Ok({
                let fun853 = e.get("world_shape_in_cap")?;
                let mut args851 = Vec::new();
                let mut kw852 = Vec::new();
                args851.push({
                    let fun856 = {
                        let fun859 = e.get("wall")?.attr("cut")?;
                        let mut args857 = Vec::new();
                        let mut kw858 = Vec::new();
                        args857.push(e.get("sockets")?);
                        args857.push(e.get("channel")?);
                        fun859.call(args857, kw858)?
                    }
                    .attr("clean")?;
                    let mut args854 = Vec::new();
                    let mut kw855 = Vec::new();
                    fun856.call(args854, kw855)?
                });
                fun853.call(args851, kw852)?
            });
            Ok(Val::None)
        })
    })?;
    // _check_bearing_station
    e.set("_check_bearing_station", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned860 = {
                let fun863 = e.get("importlib")?.attr("import_module")?;
                let mut args861 = Vec::new();
                let mut kw862 = Vec::new();
                args861.push(Val::Str("neofit_achv44_check".into()));
                fun863.call(args861, kw862)?
            };
            e.set("check", assigned860.clone())?;
            let assigned864 = {
                let fun867 = e.get("check")?.attr("bearing_band")?;
                let mut args865 = Vec::new();
                let mut kw866 = Vec::new();
                fun867.call(args865, kw866)?
            };
            let unpack868 = unpack(assigned864.clone(), 3)?;
            e.set("first", unpack868[0].clone())?;
            e.set("last", unpack868[1].clone())?;
            e.set("radius", unpack868[2].clone())?;
            let assigned869 = {
                let fun872 = e.get("check")?.attr("inlet")?;
                let mut args870 = Vec::new();
                let mut kw871 = Vec::new();
                fun872.call(args870, kw871)?
            };
            let unpack873 = unpack(assigned869.clone(), 2)?;
            e.set("inlet", unpack873[0].clone())?;
            e.set("outward", unpack873[1].clone())?;
            let assigned874 = binary(
                "truediv",
                binary("add", e.get("first")?, e.get("last")?)?,
                Val::Float(2.0f64),
            )?;
            e.set("distance", assigned874.clone())?;
            let assigned875 = {
                let fun878 = e.get("tuple")?;
                let mut args876 = Vec::new();
                let mut kw877 = Vec::new();
                args876.push({
                    let e = e.child();
                    let out879 = Val::list(vec![]);
                    for item880 in {
                        let fun883 = e.get("zip")?;
                        let mut args881 = Vec::new();
                        let mut kw882 = Vec::new();
                        args881.push(e.get("inlet")?);
                        args881.push(e.get("outward")?);
                        fun883.call(args881, kw882)?
                    }
                    .iter()?
                    {
                        let unpack884 = unpack(item880, 2)?;
                        e.set("p", unpack884[0].clone())?;
                        e.set("a", unpack884[1].clone())?;
                        out879.attr("append")?.call(
                            vec![binary(
                                "sub",
                                e.get("p")?,
                                binary("mul", e.get("distance")?, e.get("a")?)?,
                            )?],
                            vec![],
                        )?;
                    }
                    out879
                });
                fun878.call(args876, kw877)?
            };
            e.set("point", assigned875.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("point")?);
                s.push(e.get("radius")?);
                s.push(e.get("first")?);
                s.push(e.get("last")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // check_anchor
    e.set("check_anchor", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned885 = {
                let fun888 = e.get("_check_bearing_station")?;
                let mut args886 = Vec::new();
                let mut kw887 = Vec::new();
                fun888.call(args886, kw887)?
            };
            let unpack889 = unpack(assigned885.clone(), 4)?;
            e.set("native", unpack889[0].clone())?;
            e.set("radius", unpack889[1].clone())?;
            e.set("_first", unpack889[2].clone())?;
            e.set("_last", unpack889[3].clone())?;
            let assigned890 = {
                let fun893 = e.get("above_core")?.attr("point")?;
                let mut args891 = Vec::new();
                let mut kw892 = Vec::new();
                args891.push({
                    let fun896 = e.get("component_in_cap")?;
                    let mut args894 = Vec::new();
                    let mut kw895 = Vec::new();
                    args894.push(Val::Str("discharge-chain".into()));
                    fun896.call(args894, kw895)?
                });
                args891.push(e.get("native")?);
                fun893.call(args891, kw892)?
            };
            e.set("point", assigned890.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("point")?.get(Val::Slice {
                    start: None,
                    stop: Some(Val::Int(2i64).integer()?),
                    step: 1,
                })?);
                s.push(e.get("radius")?);
                s.push(binary("sub", e.get("point")?.get(Val::Int(2i64))?, {
                    let fun899 = e.get("lid_face_z")?;
                    let mut args897 = Vec::new();
                    let mut kw898 = Vec::new();
                    fun899.call(args897, kw898)?
                })?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // check_support_datums
    e.set("check_support_datums", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("fits", rt.import_module("fits")?)?;
            let assigned900 = {
                let fun903 = e.get("importlib")?.attr("import_module")?;
                let mut args901 = Vec::new();
                let mut kw902 = Vec::new();
                args901.push(Val::Str("_cold_core_interface".into()));
                fun903.call(args901, kw902)?
            };
            e.set("core", assigned900.clone())?;
            let assigned904 = {
                let fun907 = e.get("importlib")?.attr("import_module")?;
                let mut args905 = Vec::new();
                let mut kw906 = Vec::new();
                args905.push(Val::Str("g_ganen_installation".into()));
                fun907.call(args905, kw906)?
            };
            e.set("pump", assigned904.clone())?;
            let assigned908 = {
                let fun911 = e.get("importlib")?.attr("import_module")?;
                let mut args909 = Vec::new();
                let mut kw910 = Vec::new();
                args909.push(Val::Str("neofit_achv44_check".into()));
                fun911.call(args909, kw910)?
            };
            e.set("check", assigned908.clone())?;
            let assigned912 = {
                let fun915 = e.get("check")?.attr("bearing_band")?;
                let mut args913 = Vec::new();
                let mut kw914 = Vec::new();
                fun915.call(args913, kw914)?
            };
            let unpack916 = unpack(assigned912.clone(), 3)?;
            e.set("first", unpack916[0].clone())?;
            e.set("last", unpack916[1].clone())?;
            e.set("band_radius", unpack916[2].clone())?;
            let assigned917 = binary("add", e.get("first")?, Val::Float(0.5f64))?;
            e.set("bearing_first", assigned917.clone())?;
            let assigned918 = binary(
                "add",
                e.get("bearing_first")?,
                e.get("core")?.attr("cap_anchor_len")?,
            )?;
            e.set("bearing_last", assigned918.clone())?;
            let assigned919 = {
                let fun922 = e.get("check")?.attr("inlet")?;
                let mut args920 = Vec::new();
                let mut kw921 = Vec::new();
                fun922.call(args920, kw921)?
            };
            let unpack923 = unpack(assigned919.clone(), 2)?;
            e.set("inlet", unpack923[0].clone())?;
            e.set("outward", unpack923[1].clone())?;
            let assigned924 = {
                let fun927 = e.get("tuple")?;
                let mut args925 = Vec::new();
                let mut kw926 = Vec::new();
                args925.push({
                    let e = e.child();
                    let out928 = Val::list(vec![]);
                    for item929 in {
                        let fun932 = e.get("zip")?;
                        let mut args930 = Vec::new();
                        let mut kw931 = Vec::new();
                        args930.push(e.get("inlet")?);
                        args930.push(e.get("outward")?);
                        fun932.call(args930, kw931)?
                    }
                    .iter()?
                    {
                        let unpack933 = unpack(item929, 2)?;
                        e.set("p", unpack933[0].clone())?;
                        e.set("a", unpack933[1].clone())?;
                        out928.attr("append")?.call(
                            vec![binary(
                                "sub",
                                e.get("p")?,
                                binary(
                                    "mul",
                                    binary(
                                        "truediv",
                                        binary(
                                            "add",
                                            e.get("bearing_first")?,
                                            e.get("bearing_last")?,
                                        )?,
                                        Val::Float(2.0f64),
                                    )?,
                                    e.get("a")?,
                                )?,
                            )?],
                            vec![],
                        )?;
                    }
                    out928
                });
                fun927.call(args925, kw926)?
            };
            e.set("native", assigned924.clone())?;
            let assigned934 = {
                let fun937 = e.get("above_core")?.attr("point")?;
                let mut args935 = Vec::new();
                let mut kw936 = Vec::new();
                args935.push({
                    let fun940 = e.get("above_core")?.attr("pose")?;
                    let mut args938 = Vec::new();
                    let mut kw939 = Vec::new();
                    args938.push(Val::Str("discharge-chain".into()));
                    fun940.call(args938, kw939)?
                });
                args935.push(e.get("native")?);
                fun937.call(args935, kw936)?
            };
            e.set("centre", assigned934.clone())?;
            let assigned941 = binary("add", e.get("band_radius")?, e.get("fits")?.attr("slip")?)?;
            e.set("radius", assigned941.clone())?;
            let assigned942 = binary(
                "sub",
                e.get("centre")?.get(Val::Int(1i64))?,
                binary(
                    "truediv",
                    e.get("core")?.attr("cap_anchor_len")?,
                    Val::Float(2.0f64),
                )?,
            )?;
            e.set("fore", assigned942.clone())?;
            let assigned943 = binary(
                "add",
                e.get("centre")?.get(Val::Int(1i64))?,
                binary(
                    "truediv",
                    e.get("core")?.attr("cap_anchor_len")?,
                    Val::Float(2.0f64),
                )?,
            )?;
            e.set("aft", assigned943.clone())?;
            let assigned944 = binary(
                "sub",
                binary(
                    "sub",
                    e.get("centre")?.get(Val::Int(2i64))?,
                    e.get("radius")?,
                )?,
                Val::Float(3.0f64),
            )?;
            e.set("slot_top", assigned944.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("centre_world_mm".into()), e.get("centre")?)?;
                d.set(Val::Str("fixed_band_from_inlet_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("first")?);
                    s.push(e.get("last")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("bearing_from_inlet_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("bearing_first")?);
                    s.push(e.get("bearing_last")?);
                    Val::tuple(s)
                })?;
                d.set(
                    Val::Str("fixed_band_radius_mm".into()),
                    e.get("band_radius")?,
                )?;
                d.set(Val::Str("root_fore_y_mm".into()), e.get("fore")?)?;
                d.set(Val::Str("root_aft_y_mm".into()), e.get("aft")?)?;
                d.set(Val::Str("bearing_fore_y_mm".into()), e.get("fore")?)?;
                d.set(Val::Str("seat_radius_mm".into()), e.get("radius")?)?;
                d.set(
                    Val::Str("half_width_mm".into()),
                    binary("add", e.get("radius")?, Val::Float(3.0f64))?,
                )?;
                d.set(Val::Str("stock_x_limits_world_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("centre")?.get(Val::Int(0i64))?);
                    s.push(binary(
                        "add",
                        binary(
                            "add",
                            e.get("centre")?.get(Val::Int(0i64))?,
                            e.get("radius")?,
                        )?,
                        Val::Float(3.0f64),
                    )?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("tie_window_y_mm".into()), {
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("centre")?.get(Val::Int(1i64))?,
                        Val::Float(1.4f64),
                    )?);
                    s.push(binary(
                        "add",
                        e.get("centre")?.get(Val::Int(1i64))?,
                        Val::Float(1.4f64),
                    )?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("tie_window_z_mm".into()), {
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("slot_top")?, Val::Float(3.2f64))?);
                    s.push(e.get("slot_top")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("tie_roof_rise_mm".into()), Val::Float(1.4f64))?;
                d.set(
                    Val::Str("tie_route_z_mm".into()),
                    binary("sub", e.get("slot_top")?, Val::Float(2.0f64))?,
                )?;
                d.set(
                    Val::Str("open_direction".into()),
                    Val::Str("west-and-up".into()),
                )?;
                d.set(Val::Str("wall_mm".into()), Val::Float(3.0f64))?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // check_support
    e.set("check_support", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned945 = {
                let fun948 = e.get("check_support_datums")?;
                let mut args946 = Vec::new();
                let mut kw947 = Vec::new();
                fun948.call(args946, kw947)?
            };
            e.set("data", assigned945.clone())?;
            let assigned949 = e.get("data")?.get(Val::Str("centre_world_mm".into()))?;
            let unpack950 = unpack(assigned949.clone(), 3)?;
            e.set("x", unpack950[0].clone())?;
            e.set("y", unpack950[1].clone())?;
            e.set("z", unpack950[2].clone())?;
            let assigned951 = e
                .get("data")?
                .get(Val::Str("stock_x_limits_world_mm".into()))?;
            let unpack952 = unpack(assigned951.clone(), 2)?;
            e.set("low_x", unpack952[0].clone())?;
            e.set("high_x", unpack952[1].clone())?;
            let assigned953 = {
                let fun956 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args954 = Vec::new();
                let mut kw955 = Vec::new();
                args954.push(binary("sub", e.get("high_x")?, e.get("low_x")?)?);
                args954.push(binary(
                    "sub",
                    e.get("data")?.get(Val::Str("root_aft_y_mm".into()))?,
                    e.get("data")?.get(Val::Str("root_fore_y_mm".into()))?,
                )?);
                args954.push(binary(
                    "add",
                    binary(
                        "sub",
                        e.get("z")?,
                        {
                            let fun959 = e.get("above_core")?.attr("specification")?;
                            let mut args957 = Vec::new();
                            let mut kw958 = Vec::new();
                            fun959.call(args957, kw958)?
                        }
                        .get(Val::Str("cap_face_z_mm".into()))?,
                    )?,
                    Val::Float(0.15f64),
                )?);
                args954.push({
                    let fun962 = e.get("cq")?.attr("Vector")?;
                    let mut args960 = Vec::new();
                    let mut kw961 = Vec::new();
                    args960.push(e.get("low_x")?);
                    args960.push(e.get("data")?.get(Val::Str("root_fore_y_mm".into()))?);
                    args960.push(binary(
                        "sub",
                        {
                            let fun965 = e.get("above_core")?.attr("specification")?;
                            let mut args963 = Vec::new();
                            let mut kw964 = Vec::new();
                            fun965.call(args963, kw964)?
                        }
                        .get(Val::Str("cap_face_z_mm".into()))?,
                        Val::Float(0.15f64),
                    )?);
                    fun962.call(args960, kw961)?
                });
                fun956.call(args954, kw955)?
            };
            e.set("root", assigned953.clone())?;
            let assigned966 = e.get("data")?.get(Val::Str("tie_window_y_mm".into()))?;
            let unpack967 = unpack(assigned966.clone(), 2)?;
            e.set("y0", unpack967[0].clone())?;
            e.set("y1", unpack967[1].clone())?;
            let assigned968 = e.get("data")?.get(Val::Str("tie_window_z_mm".into()))?;
            let unpack969 = unpack(assigned968.clone(), 2)?;
            e.set("z0", unpack969[0].clone())?;
            e.set("z1", unpack969[1].clone())?;
            let assigned970 = {
                let fun973 = e.get("cq")?.attr("Plane")?;
                let mut args971 = Vec::new();
                let mut kw972 = Vec::new();
                kw972.push(("origin".into(), {
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("low_x")?, Val::Float(0.1f64))?);
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                }));
                kw972.push(("xDir".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                }));
                kw972.push(("normal".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                }));
                fun973.call(args971, kw972)?
            };
            e.set("plane", assigned970.clone())?;
            let assigned974 = binary(
                "sub",
                e.get("z1")?,
                e.get("data")?.get(Val::Str("tie_roof_rise_mm".into()))?,
            )?;
            e.set("shoulder", assigned974.clone())?;
            let assigned975 = {
                let fun978 = {
                    let fun981 = {
                        let fun984 = {
                            let fun987 = {
                                let fun990 = e.get("cq")?.attr("Workplane")?;
                                let mut args988 = Vec::new();
                                let mut kw989 = Vec::new();
                                args988.push(e.get("plane")?);
                                fun990.call(args988, kw989)?
                            }
                            .attr("polyline")?;
                            let mut args985 = Vec::new();
                            let mut kw986 = Vec::new();
                            args985.push({
                                let mut s = Vec::new();
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("y0")?);
                                    s.push(e.get("z0")?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("y1")?);
                                    s.push(e.get("z0")?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("y1")?);
                                    s.push(e.get("shoulder")?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "truediv",
                                        binary("add", e.get("y0")?, e.get("y1")?)?,
                                        Val::Float(2.0f64),
                                    )?);
                                    s.push(e.get("z1")?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("y0")?);
                                    s.push(e.get("shoulder")?);
                                    Val::tuple(s)
                                });
                                Val::list(s)
                            });
                            fun987.call(args985, kw986)?
                        }
                        .attr("close")?;
                        let mut args982 = Vec::new();
                        let mut kw983 = Vec::new();
                        fun984.call(args982, kw983)?
                    }
                    .attr("extrude")?;
                    let mut args979 = Vec::new();
                    let mut kw980 = Vec::new();
                    args979.push(binary(
                        "add",
                        binary("sub", e.get("high_x")?, e.get("low_x")?)?,
                        Val::Float(0.2f64),
                    )?);
                    fun981.call(args979, kw980)?
                }
                .attr("val")?;
                let mut args976 = Vec::new();
                let mut kw977 = Vec::new();
                fun978.call(args976, kw977)?
            };
            e.set("passage", assigned975.clone())?;
            let assigned991 = {
                let fun994 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args992 = Vec::new();
                let mut kw993 = Vec::new();
                args992.push(e.get("data")?.get(Val::Str("seat_radius_mm".into()))?);
                args992.push(binary(
                    "add",
                    binary(
                        "sub",
                        e.get("data")?.get(Val::Str("root_aft_y_mm".into()))?,
                        e.get("data")?.get(Val::Str("bearing_fore_y_mm".into()))?,
                    )?,
                    Val::Float(0.2f64),
                )?);
                args992.push({
                    let fun997 = e.get("cq")?.attr("Vector")?;
                    let mut args995 = Vec::new();
                    let mut kw996 = Vec::new();
                    args995.push(e.get("x")?);
                    args995.push(binary(
                        "sub",
                        e.get("data")?.get(Val::Str("bearing_fore_y_mm".into()))?,
                        Val::Float(0.1f64),
                    )?);
                    args995.push(e.get("z")?);
                    fun997.call(args995, kw996)?
                });
                args992.push({
                    let fun1000 = e.get("cq")?.attr("Vector")?;
                    let mut args998 = Vec::new();
                    let mut kw999 = Vec::new();
                    args998.push(Val::Float(0.0f64));
                    args998.push(Val::Float(1.0f64));
                    args998.push(Val::Float(0.0f64));
                    fun1000.call(args998, kw999)?
                });
                fun994.call(args992, kw993)?
            };
            e.set("bore", assigned991.clone())?;
            return Ok({
                let fun1003 = e.get("world_shape_in_cap")?;
                let mut args1001 = Vec::new();
                let mut kw1002 = Vec::new();
                args1001.push({
                    let fun1006 = {
                        let fun1009 = e.get("root")?.attr("cut")?;
                        let mut args1007 = Vec::new();
                        let mut kw1008 = Vec::new();
                        args1007.push(e.get("bore")?);
                        args1007.push(e.get("passage")?);
                        fun1009.call(args1007, kw1008)?
                    }
                    .attr("clean")?;
                    let mut args1004 = Vec::new();
                    let mut kw1005 = Vec::new();
                    fun1006.call(args1004, kw1005)?
                });
                fun1003.call(args1001, kw1002)?
            });
            Ok(Val::None)
        })
    })?;
    // _back_top_meter
    e.set("_back_top_meter", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1010 = binary(
                "truediv",
                e.get("HW")?,
                Val::Str("printed-parts/enclosure/enclosure".into()),
            )?;
            e.set("directory", assigned1010.clone())?;
            if {
                let v1014 = {
                    let fun1013 = e.get("str")?;
                    let mut args1011 = Vec::new();
                    let mut kw1012 = Vec::new();
                    args1011.push(e.get("directory")?);
                    fun1013.call(args1011, kw1012)?
                };
                let v1015 = e.get("sys")?.attr("path")?;
                Val::Bool(compare("not_in", v1014.clone(), v1015.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun1018 = e.get("sys")?.attr("path")?.attr("insert")?;
                    let mut args1016 = Vec::new();
                    let mut kw1017 = Vec::new();
                    args1016.push(Val::Int(0i64));
                    args1016.push({
                        let fun1021 = e.get("str")?;
                        let mut args1019 = Vec::new();
                        let mut kw1020 = Vec::new();
                        args1019.push(e.get("directory")?);
                        fun1021.call(args1019, kw1020)?
                    });
                    fun1018.call(args1016, kw1017)?
                };
            }
            return Ok({
                let fun1024 = e.get("importlib")?.attr("import_module")?;
                let mut args1022 = Vec::new();
                let mut kw1023 = Vec::new();
                args1022.push(Val::Str("_back_top_meter".into()));
                fun1024.call(args1022, kw1023)?
            });
            Ok(Val::None)
        })
    })?;
    // meter_support_datums
    e.set("meter_support_datums", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun1027 = {
                    let fun1030 = e.get("_back_top_meter")?;
                    let mut args1028 = Vec::new();
                    let mut kw1029 = Vec::new();
                    fun1030.call(args1028, kw1029)?
                }
                .attr("meter_support_datums")?;
                let mut args1025 = Vec::new();
                let mut kw1026 = Vec::new();
                fun1027.call(args1025, kw1026)?
            });
            Ok(Val::None)
        })
    })?;
    // _jg_band_radius
    e.set("_jg_band_radius", {
        let params = vec![
            ("leg".into(), None, false),
            ("first".into(), None, false),
            ("last".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("json", rt.import_module("json")?)?;
            let assigned1031 = {
                let fun1034 = e.get("json")?.attr("loads")?;
                let mut args1032 = Vec::new();
                let mut kw1033 = Vec::new();
                args1032.push({
                    let fun1037 = binary(
                        "truediv",
                        binary(
                            "truediv",
                            binary("truediv", e.get("HW")?, Val::Str("reference".into()))?,
                            Val::Str("jg-pp0308e-elbow".into()),
                        )?,
                        Val::Str("scan-measurements.json".into()),
                    )?
                    .attr("read_text")?;
                    let mut args1035 = Vec::new();
                    let mut kw1036 = Vec::new();
                    fun1037.call(args1035, kw1036)?
                });
                fun1034.call(args1032, kw1033)?
            }
            .get(Val::Str("profiles".into()))?
            .get(e.get("leg")?)?
            .get(Val::Str("fixed_body".into()))?;
            e.set("rows", assigned1031.clone())?;
            return Ok({
                let fun1040 = e.get("max")?;
                let mut args1038 = Vec::new();
                let mut kw1039 = Vec::new();
                args1038.push({
                    let e = e.child();
                    let out1041 = Val::list(vec![]);
                    for item1042 in e.get("rows")?.iter()? {
                        let unpack1043 = unpack(item1042, 2)?;
                        e.set("station", unpack1043[0].clone())?;
                        e.set("radius", unpack1043[1].clone())?;
                        if {
                            let v1044 = e.get("first")?;
                            let v1045 = e.get("station")?;
                            let v1046 = e.get("last")?;
                            Val::Bool(
                                compare("le", v1044.clone(), v1045.clone())?.truthy()?
                                    && compare("le", v1045.clone(), v1046.clone())?.truthy()?,
                            )
                        }
                        .truthy()?
                        {
                            out1041
                                .attr("append")?
                                .call(vec![e.get("radius")?], vec![])?;
                        }
                    }
                    out1041
                });
                fun1040.call(args1038, kw1039)?
            });
            Ok(Val::None)
        })
    })?;
    // union_support_datums
    e.set("union_support_datums", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("fits", rt.import_module("fits")?)?;
            let assigned1047 = binary(
                "sub",
                {
                    let fun1050 = e.get("above_core")?.attr("specification")?;
                    let mut args1048 = Vec::new();
                    let mut kw1049 = Vec::new();
                    fun1050.call(args1048, kw1049)?
                }
                .get(Val::Str("cap_face_z_mm".into()))?,
                Val::Float(0.15f64),
            )?;
            e.set("face", assigned1047.clone())?;
            let assigned1051 = {
                let fun1054 = e.get("above_core")?.attr("snapshot_pose")?;
                let mut args1052 = Vec::new();
                let mut kw1053 = Vec::new();
                args1052.push(Val::Str("vb-outlet-return".into()));
                fun1054.call(args1052, kw1053)?
            };
            e.set("frame", assigned1051.clone())?;
            let assigned1055 = {
                let fun1058 = e.get("above_core")?.attr("point")?;
                let mut args1056 = Vec::new();
                let mut kw1057 = Vec::new();
                args1056.push(e.get("frame")?);
                args1056.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(14.5f64));
                    Val::tuple(s)
                });
                fun1058.call(args1056, kw1057)?
            };
            e.set("centre", assigned1055.clone())?;
            let assigned1059 = binary(
                "add",
                {
                    let fun1062 = e.get("_jg_band_radius")?;
                    let mut args1060 = Vec::new();
                    let mut kw1061 = Vec::new();
                    args1060.push(Val::Str("z".into()));
                    args1060.push(Val::Float(13.0f64));
                    args1060.push(Val::Float(16.0f64));
                    fun1062.call(args1060, kw1061)?
                },
                e.get("fits")?.attr("slip")?,
            )?;
            e.set("radius", assigned1059.clone())?;
            let assigned1063 = {
                let fun1066 = e.get("above_core")?.attr("vector")?;
                let mut args1064 = Vec::new();
                let mut kw1065 = Vec::new();
                args1064.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                args1064.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun1066.call(args1064, kw1065)?
            };
            e.set("down", assigned1063.clone())?;
            let assigned1067 = {
                let fun1070 = e.get("above_core")?.attr("vector")?;
                let mut args1068 = Vec::new();
                let mut kw1069 = Vec::new();
                args1068.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                args1068.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun1070.call(args1068, kw1069)?
            };
            e.set("through", assigned1067.clone())?;
            let assigned1071 = {
                let fun1074 = e.get("above_core")?.attr("vector")?;
                let mut args1072 = Vec::new();
                let mut kw1073 = Vec::new();
                args1072.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                args1072.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(unary("neg", Val::Float(1.0f64))?);
                    Val::tuple(s)
                });
                fun1074.call(args1072, kw1073)?
            };
            e.set("wide", assigned1071.clone())?;
            let assigned1075 = {
                let fun1078 = e.get("tuple")?;
                let mut args1076 = Vec::new();
                let mut kw1077 = Vec::new();
                args1076.push({
                    let e = e.child();
                    let out1079 = Val::list(vec![]);
                    for item1080 in {
                        let fun1083 = e.get("zip")?;
                        let mut args1081 = Vec::new();
                        let mut kw1082 = Vec::new();
                        args1081.push(e.get("centre")?);
                        args1081.push(e.get("down")?);
                        fun1083.call(args1081, kw1082)?
                    }
                    .iter()?
                    {
                        let unpack1084 = unpack(item1080, 2)?;
                        e.set("c", unpack1084[0].clone())?;
                        e.set("d", unpack1084[1].clone())?;
                        out1079.attr("append")?.call(
                            vec![binary(
                                "add",
                                e.get("c")?,
                                binary(
                                    "mul",
                                    binary("add", e.get("radius")?, Val::Float(3.0f64))?,
                                    e.get("d")?,
                                )?,
                            )?],
                            vec![],
                        )?;
                    }
                    out1079
                });
                fun1078.call(args1076, kw1077)?
            };
            e.set("peak", assigned1075.clone())?;
            let assigned1085 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    binary(
                        "sub",
                        e.get("centre")?.get(Val::Int(0i64))?,
                        e.get("radius")?,
                    )?,
                    Val::Float(3.0f64),
                )?);
                s.push(binary(
                    "sub",
                    e.get("centre")?.get(Val::Int(1i64))?,
                    Val::Float(5.75f64),
                )?);
                s.push(e.get("face")?);
                Val::tuple(s)
            };
            e.set("low", assigned1085.clone())?;
            let assigned1086 = {
                let mut s = Vec::new();
                s.push(e.get("centre")?.get(Val::Int(0i64))?);
                s.push(binary(
                    "add",
                    e.get("centre")?.get(Val::Int(1i64))?,
                    Val::Float(5.75f64),
                )?);
                s.push(e.get("centre")?.get(Val::Int(2i64))?);
                Val::tuple(s)
            };
            e.set("high", assigned1086.clone())?;
            let assigned1087 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(1.4f64))?);
                    s.push(unary("neg", Val::Float(4.4f64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(1.4f64));
                    s.push(unary("neg", Val::Float(4.4f64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(1.4f64));
                    s.push(unary("neg", Val::Float(2.6f64))?);
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
                    s.push(unary("neg", Val::Float(1.4f64))?);
                    s.push(unary("neg", Val::Float(2.6f64))?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            };
            e.set("profile", assigned1087.clone())?;
            let assigned1088 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("corners", assigned1088.clone())?;
            for item1089 in {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("low")?.get(Val::Int(0i64))?,
                    Val::Float(0.1f64),
                )?);
                s.push(binary(
                    "add",
                    e.get("high")?.get(Val::Int(0i64))?,
                    Val::Float(0.1f64),
                )?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("x", item1089)?;
                for item1090 in e.get("profile")?.iter()? {
                    let unpack1114 = unpack(item1090, 2)?;
                    e.set("u", unpack1114[0].clone())?;
                    e.set("v", unpack1114[1].clone())?;
                    let assigned1091 = {
                        let fun1094 = e.get("tuple")?;
                        let mut args1092 = Vec::new();
                        let mut kw1093 = Vec::new();
                        args1092.push({
                            let e = e.child();
                            let out1095 = Val::list(vec![]);
                            for item1096 in {
                                let fun1099 = e.get("zip")?;
                                let mut args1097 = Vec::new();
                                let mut kw1098 = Vec::new();
                                args1097.push(e.get("peak")?);
                                args1097.push(e.get("wide")?);
                                args1097.push(e.get("down")?);
                                fun1099.call(args1097, kw1098)?
                            }
                            .iter()?
                            {
                                let unpack1100 = unpack(item1096, 3)?;
                                e.set("p", unpack1100[0].clone())?;
                                e.set("w", unpack1100[1].clone())?;
                                e.set("d", unpack1100[2].clone())?;
                                out1095.attr("append")?.call(
                                    vec![binary(
                                        "sub",
                                        binary(
                                            "add",
                                            e.get("p")?,
                                            binary("mul", e.get("u")?, e.get("w")?)?,
                                        )?,
                                        binary("mul", e.get("v")?, e.get("d")?)?,
                                    )?],
                                    vec![],
                                )?;
                            }
                            out1095
                        });
                        fun1094.call(args1092, kw1093)?
                    };
                    e.set("point", assigned1091.clone())?;
                    let assigned1101 = binary(
                        "truediv",
                        binary("sub", e.get("x")?, e.get("point")?.get(Val::Int(0i64))?)?,
                        e.get("through")?.get(Val::Int(0i64))?,
                    )?;
                    e.set("t", assigned1101.clone())?;
                    {
                        let fun1104 = e.get("corners")?.attr("append")?;
                        let mut args1102 = Vec::new();
                        let mut kw1103 = Vec::new();
                        args1102.push({
                            let fun1107 = e.get("tuple")?;
                            let mut args1105 = Vec::new();
                            let mut kw1106 = Vec::new();
                            args1105.push({
                                let e = e.child();
                                let out1108 = Val::list(vec![]);
                                for item1109 in {
                                    let fun1112 = e.get("zip")?;
                                    let mut args1110 = Vec::new();
                                    let mut kw1111 = Vec::new();
                                    args1110.push(e.get("point")?);
                                    args1110.push(e.get("through")?);
                                    fun1112.call(args1110, kw1111)?
                                }
                                .iter()?
                                {
                                    let unpack1113 = unpack(item1109, 2)?;
                                    e.set("p", unpack1113[0].clone())?;
                                    e.set("a", unpack1113[1].clone())?;
                                    out1108.attr("append")?.call(
                                        vec![binary(
                                            "add",
                                            e.get("p")?,
                                            binary("mul", e.get("t")?, e.get("a")?)?,
                                        )?],
                                        vec![],
                                    )?;
                                }
                                out1108
                            });
                            fun1107.call(args1105, kw1106)?
                        });
                        fun1104.call(args1102, kw1103)?
                    };
                }
            }
            let assigned1115 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("stock_min_world_mm".into()), e.get("low")?)?;
                d.set(Val::Str("stock_max_world_mm".into()), e.get("high")?)?;
                d.set(Val::Str("bore_origin_world_mm".into()), {
                    let fun1118 = e.get("above_core")?.attr("point")?;
                    let mut args1116 = Vec::new();
                    let mut kw1117 = Vec::new();
                    args1116.push(e.get("frame")?);
                    args1116.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(unary("neg", Val::Float(5.0f64))?);
                        Val::tuple(s)
                    });
                    fun1118.call(args1116, kw1117)?
                })?;
                d.set(Val::Str("bore_axis_world".into()), {
                    let fun1121 = e.get("above_core")?.attr("vector")?;
                    let mut args1119 = Vec::new();
                    let mut kw1120 = Vec::new();
                    args1119.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                    args1119.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        Val::tuple(s)
                    });
                    fun1121.call(args1119, kw1120)?
                })?;
                d.set(Val::Str("bore_length_mm".into()), Val::Float(50.0f64))?;
                d.set(Val::Str("seat_radius_mm".into()), e.get("radius")?)?;
                d.set(Val::Str("native_leg".into()), Val::Str("z".into()))?;
                d.set(Val::Str("native_band_mm".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Float(13.0f64));
                    s.push(Val::Float(16.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("tie_window_min_world_mm".into()), {
                    let fun1124 = e.get("tuple")?;
                    let mut args1122 = Vec::new();
                    let mut kw1123 = Vec::new();
                    args1122.push({
                        let e = e.child();
                        let out1125 = Val::list(vec![]);
                        for item1126 in {
                            let fun1129 = e.get("range")?;
                            let mut args1127 = Vec::new();
                            let mut kw1128 = Vec::new();
                            args1127.push(Val::Int(3i64));
                            fun1129.call(args1127, kw1128)?
                        }
                        .iter()?
                        {
                            e.set("i", item1126)?;
                            out1125.attr("append")?.call(
                                vec![{
                                    let fun1132 = e.get("min")?;
                                    let mut args1130 = Vec::new();
                                    let mut kw1131 = Vec::new();
                                    args1130.push({
                                        let e = e.child();
                                        let out1133 = Val::list(vec![]);
                                        for item1134 in e.get("corners")?.iter()? {
                                            e.set("p", item1134)?;
                                            out1133.attr("append")?.call(
                                                vec![e.get("p")?.get(e.get("i")?)?],
                                                vec![],
                                            )?;
                                        }
                                        out1133
                                    });
                                    fun1132.call(args1130, kw1131)?
                                }],
                                vec![],
                            )?;
                        }
                        out1125
                    });
                    fun1124.call(args1122, kw1123)?
                })?;
                d.set(Val::Str("tie_window_max_world_mm".into()), {
                    let fun1137 = e.get("tuple")?;
                    let mut args1135 = Vec::new();
                    let mut kw1136 = Vec::new();
                    args1135.push({
                        let e = e.child();
                        let out1138 = Val::list(vec![]);
                        for item1139 in {
                            let fun1142 = e.get("range")?;
                            let mut args1140 = Vec::new();
                            let mut kw1141 = Vec::new();
                            args1140.push(Val::Int(3i64));
                            fun1142.call(args1140, kw1141)?
                        }
                        .iter()?
                        {
                            e.set("i", item1139)?;
                            out1138.attr("append")?.call(
                                vec![{
                                    let fun1145 = e.get("max")?;
                                    let mut args1143 = Vec::new();
                                    let mut kw1144 = Vec::new();
                                    args1143.push({
                                        let e = e.child();
                                        let out1146 = Val::list(vec![]);
                                        for item1147 in e.get("corners")?.iter()? {
                                            e.set("p", item1147)?;
                                            out1146.attr("append")?.call(
                                                vec![e.get("p")?.get(e.get("i")?)?],
                                                vec![],
                                            )?;
                                        }
                                        out1146
                                    });
                                    fun1145.call(args1143, kw1144)?
                                }],
                                vec![],
                            )?;
                        }
                        out1138
                    });
                    fun1137.call(args1135, kw1136)?
                })?;
                d.set(
                    Val::Str("tie_profile_origin_world_mm".into()),
                    e.get("peak")?,
                )?;
                d.set(Val::Str("tie_profile_x_world".into()), e.get("wide")?)?;
                d.set(
                    Val::Str("tie_profile_normal_world".into()),
                    e.get("through")?,
                )?;
                d.set(Val::Str("tie_profile_mm".into()), e.get("profile")?)?;
                d.set(
                    Val::Str("tie_route_native_down_mm".into()),
                    binary("add", e.get("radius")?, Val::Float(6.3f64))?,
                )?;
                d.set(Val::Str("centre_world_mm".into()), e.get("centre")?)?;
                d.set(Val::Str("wall_mm".into()), Val::Float(3.0f64))?;
                d.set(Val::Str("parent".into()), Val::Str("foam-assembly".into()))?;
                d.set(Val::Str("support_implemented".into()), Val::Bool(true))?;
                d
            };
            e.set("vb", assigned1115.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("vb-outlet-return".into()), e.get("vb")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // union_supports
    e.set("union_supports", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned1148 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("result", assigned1148.clone())?;
            for item1149 in {
                let fun1188 = {
                    let fun1191 = e.get("union_support_datums")?;
                    let mut args1189 = Vec::new();
                    let mut kw1190 = Vec::new();
                    fun1191.call(args1189, kw1190)?
                }
                .attr("items")?;
                let mut args1186 = Vec::new();
                let mut kw1187 = Vec::new();
                fun1188.call(args1186, kw1187)?
            }
            .iter()?
            {
                let unpack1192 = unpack(item1149, 2)?;
                e.set("name", unpack1192[0].clone())?;
                e.set("data", unpack1192[1].clone())?;
                if {
                    let v1150 = e.get("data")?.get(Val::Str("parent".into()))?;
                    let v1151 = Val::Str("foam-assembly".into());
                    Val::Bool(compare("ne", v1150.clone(), v1151.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned1152 = {
                    let mut s = Vec::new();
                    s.push(e.get("data")?.get(Val::Str("stock_min_world_mm".into()))?);
                    s.push(e.get("data")?.get(Val::Str("stock_max_world_mm".into()))?);
                    Val::tuple(s)
                };
                let unpack1153 = unpack(assigned1152.clone(), 2)?;
                e.set("low", unpack1153[0].clone())?;
                e.set("high", unpack1153[1].clone())?;
                let assigned1154 = {
                    let fun1157 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                    let mut args1155 = Vec::new();
                    let mut kw1156 = Vec::new();
                    args1155.extend(
                        {
                            let e = e.child();
                            let out1158 = Val::list(vec![]);
                            for item1159 in {
                                let fun1162 = e.get("range")?;
                                let mut args1160 = Vec::new();
                                let mut kw1161 = Vec::new();
                                args1160.push(Val::Int(3i64));
                                fun1162.call(args1160, kw1161)?
                            }
                            .iter()?
                            {
                                e.set("i", item1159)?;
                                out1158.attr("append")?.call(
                                    vec![binary(
                                        "sub",
                                        e.get("high")?.get(e.get("i")?)?,
                                        e.get("low")?.get(e.get("i")?)?,
                                    )?],
                                    vec![],
                                )?;
                            }
                            out1158
                        }
                        .iter()?,
                    );
                    args1155.push({
                        let fun1165 = e.get("cq")?.attr("Vector")?;
                        let mut args1163 = Vec::new();
                        let mut kw1164 = Vec::new();
                        args1163.extend(e.get("low")?.iter()?);
                        fun1165.call(args1163, kw1164)?
                    });
                    fun1157.call(args1155, kw1156)?
                };
                e.set("stock", assigned1154.clone())?;
                let assigned1166 = {
                    let fun1169 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                    let mut args1167 = Vec::new();
                    let mut kw1168 = Vec::new();
                    args1167.push(e.get("data")?.get(Val::Str("seat_radius_mm".into()))?);
                    args1167.push(e.get("data")?.get(Val::Str("bore_length_mm".into()))?);
                    args1167.push({
                        let fun1172 = e.get("cq")?.attr("Vector")?;
                        let mut args1170 = Vec::new();
                        let mut kw1171 = Vec::new();
                        args1170.extend(
                            e.get("data")?
                                .get(Val::Str("bore_origin_world_mm".into()))?
                                .iter()?,
                        );
                        fun1172.call(args1170, kw1171)?
                    });
                    args1167.push({
                        let fun1175 = e.get("cq")?.attr("Vector")?;
                        let mut args1173 = Vec::new();
                        let mut kw1174 = Vec::new();
                        args1173.extend(
                            e.get("data")?
                                .get(Val::Str("bore_axis_world".into()))?
                                .iter()?,
                        );
                        fun1175.call(args1173, kw1174)?
                    });
                    fun1169.call(args1167, kw1168)?
                };
                e.set("bore", assigned1166.clone())?;
                let assigned1176 = {
                    let fun1179 = e.get("world_shape_in_cap")?;
                    let mut args1177 = Vec::new();
                    let mut kw1178 = Vec::new();
                    args1177.push({
                        let fun1182 = {
                            let fun1185 = e.get("stock")?.attr("cut")?;
                            let mut args1183 = Vec::new();
                            let mut kw1184 = Vec::new();
                            args1183.push(e.get("bore")?);
                            fun1185.call(args1183, kw1184)?
                        }
                        .attr("clean")?;
                        let mut args1180 = Vec::new();
                        let mut kw1181 = Vec::new();
                        fun1182.call(args1180, kw1181)?
                    });
                    fun1179.call(args1177, kw1178)?
                };
                e.get("result")?.set(e.get("name")?, assigned1176.clone())?;
            }
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // union_support_cuts
    e.set("union_support_cuts", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned1193 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("result", assigned1193.clone())?;
            for item1194 in {
                let fun1233 = {
                    let fun1236 = e.get("union_support_datums")?;
                    let mut args1234 = Vec::new();
                    let mut kw1235 = Vec::new();
                    fun1236.call(args1234, kw1235)?
                }
                .attr("items")?;
                let mut args1231 = Vec::new();
                let mut kw1232 = Vec::new();
                fun1233.call(args1231, kw1232)?
            }
            .iter()?
            {
                let unpack1237 = unpack(item1194, 2)?;
                e.set("name", unpack1237[0].clone())?;
                e.set("data", unpack1237[1].clone())?;
                if {
                    let v1195 = e.get("data")?.get(Val::Str("parent".into()))?;
                    let v1196 = Val::Str("foam-assembly".into());
                    Val::Bool(compare("ne", v1195.clone(), v1196.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned1197 = {
                    let fun1200 = e.get("tuple")?;
                    let mut args1198 = Vec::new();
                    let mut kw1199 = Vec::new();
                    args1198.push({
                        let e = e.child();
                        let out1201 = Val::list(vec![]);
                        for item1202 in {
                            let fun1205 = e.get("zip")?;
                            let mut args1203 = Vec::new();
                            let mut kw1204 = Vec::new();
                            args1203.push(
                                e.get("data")?
                                    .get(Val::Str("tie_profile_origin_world_mm".into()))?,
                            );
                            args1203.push(
                                e.get("data")?
                                    .get(Val::Str("tie_profile_normal_world".into()))?,
                            );
                            fun1205.call(args1203, kw1204)?
                        }
                        .iter()?
                        {
                            let unpack1206 = unpack(item1202, 2)?;
                            e.set("p", unpack1206[0].clone())?;
                            e.set("a", unpack1206[1].clone())?;
                            out1201.attr("append")?.call(
                                vec![binary(
                                    "sub",
                                    e.get("p")?,
                                    binary("mul", Val::Float(40.0f64), e.get("a")?)?,
                                )?],
                                vec![],
                            )?;
                        }
                        out1201
                    });
                    fun1200.call(args1198, kw1199)?
                };
                e.set("origin", assigned1197.clone())?;
                let assigned1207 = {
                    let fun1210 = e.get("cq")?.attr("Plane")?;
                    let mut args1208 = Vec::new();
                    let mut kw1209 = Vec::new();
                    kw1209.push(("origin".into(), e.get("origin")?));
                    kw1209.push((
                        "xDir".into(),
                        e.get("data")?.get(Val::Str("tie_profile_x_world".into()))?,
                    ));
                    kw1209.push((
                        "normal".into(),
                        e.get("data")?
                            .get(Val::Str("tie_profile_normal_world".into()))?,
                    ));
                    fun1210.call(args1208, kw1209)?
                };
                e.set("plane", assigned1207.clone())?;
                let assigned1211 = {
                    let fun1214 = {
                        let fun1217 = {
                            let fun1220 = {
                                let fun1223 = {
                                    let fun1226 = e.get("cq")?.attr("Workplane")?;
                                    let mut args1224 = Vec::new();
                                    let mut kw1225 = Vec::new();
                                    args1224.push(e.get("plane")?);
                                    fun1226.call(args1224, kw1225)?
                                }
                                .attr("polyline")?;
                                let mut args1221 = Vec::new();
                                let mut kw1222 = Vec::new();
                                args1221
                                    .push(e.get("data")?.get(Val::Str("tie_profile_mm".into()))?);
                                fun1223.call(args1221, kw1222)?
                            }
                            .attr("close")?;
                            let mut args1218 = Vec::new();
                            let mut kw1219 = Vec::new();
                            fun1220.call(args1218, kw1219)?
                        }
                        .attr("extrude")?;
                        let mut args1215 = Vec::new();
                        let mut kw1216 = Vec::new();
                        args1215.push(Val::Float(80.0f64));
                        fun1217.call(args1215, kw1216)?
                    }
                    .attr("val")?;
                    let mut args1212 = Vec::new();
                    let mut kw1213 = Vec::new();
                    fun1214.call(args1212, kw1213)?
                };
                e.set("passage", assigned1211.clone())?;
                let assigned1227 = {
                    let fun1230 = e.get("world_shape_in_cap")?;
                    let mut args1228 = Vec::new();
                    let mut kw1229 = Vec::new();
                    args1228.push(e.get("passage")?);
                    fun1230.call(args1228, kw1229)?
                };
                e.get("result")?.set(e.get("name")?, assigned1227.clone())?;
            }
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // _tie_arc_point
    e.set("_tie_arc_point", {
        let params = vec![
            ("centre".into(), None, false),
            ("u".into(), None, false),
            ("v".into(), None, false),
            ("radius".into(), None, false),
            ("angle".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1238 = {
                let fun1241 = e.get("math")?.attr("radians")?;
                let mut args1239 = Vec::new();
                let mut kw1240 = Vec::new();
                args1239.push(e.get("angle")?);
                fun1241.call(args1239, kw1240)?
            };
            e.set("angle", assigned1238.clone())?;
            return Ok({
                let fun1244 = e.get("tuple")?;
                let mut args1242 = Vec::new();
                let mut kw1243 = Vec::new();
                args1242.push({
                    let e = e.child();
                    let out1245 = Val::list(vec![]);
                    for item1246 in {
                        let fun1249 = e.get("range")?;
                        let mut args1247 = Vec::new();
                        let mut kw1248 = Vec::new();
                        args1247.push(Val::Int(3i64));
                        fun1249.call(args1247, kw1248)?
                    }
                    .iter()?
                    {
                        e.set("i", item1246)?;
                        out1245.attr("append")?.call(
                            vec![binary(
                                "add",
                                e.get("centre")?.get(e.get("i")?)?,
                                binary(
                                    "mul",
                                    e.get("radius")?,
                                    binary(
                                        "add",
                                        binary("mul", e.get("u")?.get(e.get("i")?)?, {
                                            let fun1252 = e.get("math")?.attr("cos")?;
                                            let mut args1250 = Vec::new();
                                            let mut kw1251 = Vec::new();
                                            args1250.push(e.get("angle")?);
                                            fun1252.call(args1250, kw1251)?
                                        })?,
                                        binary("mul", e.get("v")?.get(e.get("i")?)?, {
                                            let fun1255 = e.get("math")?.attr("sin")?;
                                            let mut args1253 = Vec::new();
                                            let mut kw1254 = Vec::new();
                                            args1253.push(e.get("angle")?);
                                            fun1255.call(args1253, kw1254)?
                                        })?,
                                    )?,
                                )?,
                            )?],
                            vec![],
                        )?;
                    }
                    out1245
                });
                fun1244.call(args1242, kw1243)?
            });
            Ok(Val::None)
        })
    })?;
    // _tie_line
    e.set("_tie_line", {
        let params = vec![
            ("first".into(), None, false),
            ("last".into(), None, false),
            (
                "wide_axis".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    Val::tuple(s)
                }),
                false,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("kind".into()), Val::Str("line".into()))?;
                d.set(Val::Str("points_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("first")?);
                    s.push(e.get("last")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("wide_axis".into()), e.get("wide_axis")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // _tie_arc
    e.set("_tie_arc", {
        let params = vec![
            ("centre".into(), None, false),
            ("u".into(), None, false),
            ("v".into(), None, false),
            ("radius".into(), None, false),
            ("first".into(), None, false),
            ("last".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1256 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(1i64))?,
                        e.get("v")?.get(Val::Int(2i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(2i64))?,
                        e.get("v")?.get(Val::Int(1i64))?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(2i64))?,
                        e.get("v")?.get(Val::Int(0i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(0i64))?,
                        e.get("v")?.get(Val::Int(2i64))?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(0i64))?,
                        e.get("v")?.get(Val::Int(1i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("u")?.get(Val::Int(1i64))?,
                        e.get("v")?.get(Val::Int(0i64))?,
                    )?,
                )?);
                Val::tuple(s)
            };
            e.set("normal", assigned1256.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("kind".into()), Val::Str("arc".into()))?;
                d.set(Val::Str("points_mm".into()), {
                    let e = e.child();
                    let out1257 = Val::list(vec![]);
                    for item1258 in {
                        let mut s = Vec::new();
                        s.push(e.get("first")?);
                        s.push(binary(
                            "truediv",
                            binary("add", e.get("first")?, e.get("last")?)?,
                            Val::Float(2.0f64),
                        )?);
                        s.push(e.get("last")?);
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("angle", item1258)?;
                        out1257.attr("append")?.call(
                            vec![{
                                let fun1261 = e.get("_tie_arc_point")?;
                                let mut args1259 = Vec::new();
                                let mut kw1260 = Vec::new();
                                args1259.push(e.get("centre")?);
                                args1259.push(e.get("u")?);
                                args1259.push(e.get("v")?);
                                args1259.push(e.get("radius")?);
                                args1259.push(e.get("angle")?);
                                fun1261.call(args1259, kw1260)?
                            }],
                            vec![],
                        )?;
                    }
                    out1257
                })?;
                d.set(Val::Str("radius_mm".into()), e.get("radius")?)?;
                d.set(
                    Val::Str("sweep_degrees".into()),
                    binary("sub", e.get("last")?, e.get("first")?)?,
                )?;
                d.set(Val::Str("wide_axis".into()), e.get("normal")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // _tie_length
    e.set("_tie_length", {
        let params = vec![("segments".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun1264 = e.get("sum")?;
                let mut args1262 = Vec::new();
                let mut kw1263 = Vec::new();
                args1262.push({
                    let e = e.child();
                    let out1265 = Val::list(vec![]);
                    for item1266 in e.get("segments")?.iter()? {
                        e.set("row", item1266)?;
                        out1265.attr("append")?.call(
                            vec![if {
                                let v1267 = e.get("row")?.get(Val::Str("kind".into()))?;
                                let v1268 = Val::Str("line".into());
                                Val::Bool(compare("eq", v1267.clone(), v1268.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                {
                                    let fun1271 = e.get("math")?.attr("dist")?;
                                    let mut args1269 = Vec::new();
                                    let mut kw1270 = Vec::new();
                                    args1269.extend(
                                        e.get("row")?.get(Val::Str("points_mm".into()))?.iter()?,
                                    );
                                    fun1271.call(args1269, kw1270)?
                                }
                            } else {
                                binary("mul", e.get("row")?.get(Val::Str("radius_mm".into()))?, {
                                    let fun1274 = e.get("abs")?;
                                    let mut args1272 = Vec::new();
                                    let mut kw1273 = Vec::new();
                                    args1272.push({
                                        let fun1277 = e.get("math")?.attr("radians")?;
                                        let mut args1275 = Vec::new();
                                        let mut kw1276 = Vec::new();
                                        args1275.push(
                                            e.get("row")?.get(Val::Str("sweep_degrees".into()))?,
                                        );
                                        fun1277.call(args1275, kw1276)?
                                    });
                                    fun1274.call(args1272, kw1273)?
                                })?
                            }],
                            vec![],
                        )?;
                    }
                    out1265
                });
                fun1264.call(args1262, kw1263)?
            });
            Ok(Val::None)
        })
    })?;
    // check_tie_route
    e.set("check_tie_route", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1278 = {
                let fun1281 = e.get("check_support_datums")?;
                let mut args1279 = Vec::new();
                let mut kw1280 = Vec::new();
                fun1281.call(args1279, kw1280)?
            };
            e.set("data", assigned1278.clone())?;
            let assigned1282 = e.get("data")?.get(Val::Str("centre_world_mm".into()))?;
            let unpack1283 = unpack(assigned1282.clone(), 3)?;
            e.set("x", unpack1283[0].clone())?;
            e.set("y", unpack1283[1].clone())?;
            e.set("z", unpack1283[2].clone())?;
            let assigned1284 = Val::Float(0.55f64);
            e.set("allowance", assigned1284.clone())?;
            let assigned1285 = binary(
                "add",
                e.get("data")?
                    .get(Val::Str("fixed_band_radius_mm".into()))?,
                e.get("allowance")?,
            )?;
            e.set("radius", assigned1285.clone())?;
            let assigned1286 = binary(
                "add",
                binary(
                    "sub",
                    e.get("data")?
                        .get(Val::Str("stock_x_limits_world_mm".into()))?
                        .get(Val::Int(1i64))?,
                    e.get("x")?,
                )?,
                e.get("allowance")?,
            )?;
            e.set("w", assigned1286.clone())?;
            let assigned1287 = binary(
                "sub",
                e.get("z")?,
                e.get("data")?.get(Val::Str("tie_route_z_mm".into()))?,
            )?;
            e.set("h", assigned1287.clone())?;
            let assigned1288 = {
                let mut s = Vec::new();
                s.push(unary("neg", e.get("allowance")?)?);
                s.push(unary("neg", e.get("h")?)?);
                Val::tuple(s)
            };
            e.set("left", assigned1288.clone())?;
            let assigned1289 = binary(
                "sub",
                {
                    let fun1292 = e.get("math")?.attr("atan2")?;
                    let mut args1290 = Vec::new();
                    let mut kw1291 = Vec::new();
                    args1290.push(e.get("left")?.get(Val::Int(1i64))?);
                    args1290.push(e.get("left")?.get(Val::Int(0i64))?);
                    fun1292.call(args1290, kw1291)?
                },
                {
                    let fun1295 = e.get("math")?.attr("acos")?;
                    let mut args1293 = Vec::new();
                    let mut kw1294 = Vec::new();
                    args1293.push(binary("truediv", e.get("radius")?, {
                        let fun1298 = e.get("math")?.attr("hypot")?;
                        let mut args1296 = Vec::new();
                        let mut kw1297 = Vec::new();
                        args1296.extend(e.get("left")?.iter()?);
                        fun1298.call(args1296, kw1297)?
                    })?);
                    fun1295.call(args1293, kw1294)?
                },
            )?;
            e.set("left_angle", assigned1289.clone())?;
            let assigned1299 = {
                let fun1302 = e.get("math")?.attr("acos")?;
                let mut args1300 = Vec::new();
                let mut kw1301 = Vec::new();
                args1300.push(binary("truediv", e.get("radius")?, e.get("w")?)?);
                fun1302.call(args1300, kw1301)?
            };
            e.set("right_angle", assigned1299.clone())?;
            let assigned1303 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    Val::tuple(s)
                });
                Val::tuple(s)
            };
            let unpack1304 = unpack(assigned1303.clone(), 3)?;
            e.set("centre", unpack1304[0].clone())?;
            e.set("u", unpack1304[1].clone())?;
            e.set("v", unpack1304[2].clone())?;
            let assigned1305 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("x")?,
                    e.get("left")?.get(Val::Int(0i64))?,
                )?);
                s.push(e.get("y")?);
                s.push(binary(
                    "add",
                    e.get("z")?,
                    e.get("left")?.get(Val::Int(1i64))?,
                )?);
                Val::tuple(s)
            };
            e.set("first", assigned1305.clone())?;
            let assigned1306 = {
                let mut s = Vec::new();
                s.push(binary("add", e.get("x")?, e.get("w")?)?);
                s.push(e.get("y")?);
                s.push(binary("sub", e.get("z")?, e.get("h")?)?);
                Val::tuple(s)
            };
            e.set("lower_east", assigned1306.clone())?;
            let assigned1307 = {
                let mut s = Vec::new();
                s.push(binary("add", e.get("x")?, e.get("w")?)?);
                s.push(e.get("y")?);
                s.push(e.get("z")?);
                Val::tuple(s)
            };
            e.set("upper_east", assigned1307.clone())?;
            let assigned1308 = {
                let fun1311 = e.get("_tie_arc_point")?;
                let mut args1309 = Vec::new();
                let mut kw1310 = Vec::new();
                args1309.push(e.get("centre")?);
                args1309.push(e.get("u")?);
                args1309.push(e.get("v")?);
                args1309.push(e.get("radius")?);
                args1309.push({
                    let fun1314 = e.get("math")?.attr("degrees")?;
                    let mut args1312 = Vec::new();
                    let mut kw1313 = Vec::new();
                    args1312.push(e.get("right_angle")?);
                    fun1314.call(args1312, kw1313)?
                });
                fun1311.call(args1309, kw1310)?
            };
            e.set("right", assigned1308.clone())?;
            let assigned1315 = {
                let fun1318 = e.get("_tie_arc_point")?;
                let mut args1316 = Vec::new();
                let mut kw1317 = Vec::new();
                args1316.push(e.get("centre")?);
                args1316.push(e.get("u")?);
                args1316.push(e.get("v")?);
                args1316.push(e.get("radius")?);
                args1316.push({
                    let fun1321 = e.get("math")?.attr("degrees")?;
                    let mut args1319 = Vec::new();
                    let mut kw1320 = Vec::new();
                    args1319.push(e.get("left_angle")?);
                    fun1321.call(args1319, kw1320)?
                });
                fun1318.call(args1316, kw1317)?
            };
            e.set("last", assigned1315.clone())?;
            let assigned1322 = {
                let mut s = Vec::new();
                s.push({
                    let fun1325 = e.get("_tie_line")?;
                    let mut args1323 = Vec::new();
                    let mut kw1324 = Vec::new();
                    args1323.push(e.get("first")?);
                    args1323.push(e.get("lower_east")?);
                    args1323.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun1325.call(args1323, kw1324)?
                });
                s.push({
                    let fun1328 = e.get("_tie_line")?;
                    let mut args1326 = Vec::new();
                    let mut kw1327 = Vec::new();
                    args1326.push(e.get("lower_east")?);
                    args1326.push(e.get("upper_east")?);
                    args1326.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun1328.call(args1326, kw1327)?
                });
                s.push({
                    let fun1331 = e.get("_tie_line")?;
                    let mut args1329 = Vec::new();
                    let mut kw1330 = Vec::new();
                    args1329.push(e.get("upper_east")?);
                    args1329.push(e.get("right")?);
                    args1329.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun1331.call(args1329, kw1330)?
                });
                s.push({
                    let fun1334 = e.get("_tie_arc")?;
                    let mut args1332 = Vec::new();
                    let mut kw1333 = Vec::new();
                    args1332.push(e.get("centre")?);
                    args1332.push(e.get("u")?);
                    args1332.push(e.get("v")?);
                    args1332.push(e.get("radius")?);
                    args1332.push({
                        let fun1337 = e.get("math")?.attr("degrees")?;
                        let mut args1335 = Vec::new();
                        let mut kw1336 = Vec::new();
                        args1335.push(e.get("right_angle")?);
                        fun1337.call(args1335, kw1336)?
                    });
                    args1332.push(binary(
                        "add",
                        {
                            let fun1340 = e.get("math")?.attr("degrees")?;
                            let mut args1338 = Vec::new();
                            let mut kw1339 = Vec::new();
                            args1338.push(e.get("left_angle")?);
                            fun1340.call(args1338, kw1339)?
                        },
                        Val::Float(360.0f64),
                    )?);
                    fun1334.call(args1332, kw1333)?
                });
                s.push({
                    let fun1343 = e.get("_tie_line")?;
                    let mut args1341 = Vec::new();
                    let mut kw1342 = Vec::new();
                    args1341.push(e.get("last")?);
                    args1341.push(e.get("first")?);
                    args1341.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun1343.call(args1341, kw1342)?
                });
                Val::list(s)
            };
            e.set("segments", assigned1322.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("segments".into()), e.get("segments")?)?;
                d.set(Val::Str("length_mm".into()), {
                    let fun1346 = e.get("_tie_length")?;
                    let mut args1344 = Vec::new();
                    let mut kw1345 = Vec::new();
                    args1344.push(e.get("segments")?);
                    fun1346.call(args1344, kw1345)?
                })?;
                d.set(
                    Val::Str("stock".into()),
                    Val::Str("6-inch narrow nylon tie".into()),
                )?;
                d.set(Val::Str("stock_length_mm".into()), Val::Float(152.4f64))?;
                d.set(Val::Str("width_mm".into()), Val::Float(2.5f64))?;
                d.set(Val::Str("thickness_mm".into()), Val::Float(0.8f64))?;
                d.set(Val::Str("fixed_band_plane_world_y_mm".into()), e.get("y")?)?;
                d.set(
                    Val::Str("threading_height_mm".into()),
                    binary(
                        "sub",
                        e.get("data")?
                            .get(Val::Str("tie_window_z_mm".into()))?
                            .get(Val::Int(1i64))?,
                        e.get("data")?
                            .get(Val::Str("tie_window_z_mm".into()))?
                            .get(Val::Int(0i64))?,
                    )?,
                )?;
                d.set(
                    Val::Str("strip_basis".into()),
                    Val::Str(
                        "Nominal layout allowance; purchased strap/head dimensions unmeasured"
                            .into(),
                    ),
                )?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // _vb_union_tie
    e.set("_vb_union_tie", {
        let params = vec![("data".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1347 = {
                let fun1350 = e.get("above_core")?.attr("snapshot_pose")?;
                let mut args1348 = Vec::new();
                let mut kw1349 = Vec::new();
                args1348.push(Val::Str("vb-outlet-return".into()));
                fun1350.call(args1348, kw1349)?
            };
            e.set("frame", assigned1347.clone())?;
            let assigned1351 = e.get("data")?.get(Val::Str("centre_world_mm".into()))?;
            e.set("centre", assigned1351.clone())?;
            let assigned1352 = {
                let fun1355 = e.get("above_core")?.attr("vector")?;
                let mut args1353 = Vec::new();
                let mut kw1354 = Vec::new();
                args1353.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                args1353.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun1355.call(args1353, kw1354)?
            };
            e.set("u", assigned1352.clone())?;
            let assigned1356 = {
                let fun1359 = e.get("tuple")?;
                let mut args1357 = Vec::new();
                let mut kw1358 = Vec::new();
                args1357.push({
                    let e = e.child();
                    let out1360 = Val::list(vec![]);
                    for item1361 in {
                        let fun1364 = e.get("above_core")?.attr("vector")?;
                        let mut args1362 = Vec::new();
                        let mut kw1363 = Vec::new();
                        args1362.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                        args1362.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(1.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        });
                        fun1364.call(args1362, kw1363)?
                    }
                    .iter()?
                    {
                        e.set("value", item1361)?;
                        out1360
                            .attr("append")?
                            .call(vec![unary("neg", e.get("value")?)?], vec![])?;
                    }
                    out1360
                });
                fun1359.call(args1357, kw1358)?
            };
            e.set("v", assigned1356.clone())?;
            let assigned1365 = binary(
                "add",
                e.get("data")?.get(Val::Str("seat_radius_mm".into()))?,
                Val::Float(0.55f64),
            )?;
            e.set("radius", assigned1365.clone())?;
            let assigned1366 = {
                let fun1369 = e.get("_tie_arc_point")?;
                let mut args1367 = Vec::new();
                let mut kw1368 = Vec::new();
                args1367.push(e.get("centre")?);
                args1367.push(e.get("u")?);
                args1367.push(e.get("v")?);
                args1367.push(e.get("radius")?);
                args1367.push(unary("neg", Val::Float(20.0f64))?);
                fun1369.call(args1367, kw1368)?
            };
            e.set("lower", assigned1366.clone())?;
            let assigned1370 = {
                let fun1373 = e.get("_tie_arc_point")?;
                let mut args1371 = Vec::new();
                let mut kw1372 = Vec::new();
                args1371.push(e.get("centre")?);
                args1371.push(e.get("u")?);
                args1371.push(e.get("v")?);
                args1371.push(e.get("radius")?);
                args1371.push(Val::Float(170.0f64));
                fun1373.call(args1371, kw1372)?
            };
            e.set("upper", assigned1370.clone())?;
            let assigned1374 = {
                let fun1377 = e.get("above_core")?.attr("vector")?;
                let mut args1375 = Vec::new();
                let mut kw1376 = Vec::new();
                args1375.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                args1375.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun1377.call(args1375, kw1376)?
            };
            e.set("down", assigned1374.clone())?;
            let assigned1378 = {
                let fun1381 = e.get("above_core")?.attr("vector")?;
                let mut args1379 = Vec::new();
                let mut kw1380 = Vec::new();
                args1379.push(e.get("frame")?.get(Val::Str("rotation".into()))?);
                args1379.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    Val::tuple(s)
                });
                fun1381.call(args1379, kw1380)?
            };
            e.set("axis", assigned1378.clone())?;
            let assigned1382 = {
                let fun1385 = e.get("tuple")?;
                let mut args1383 = Vec::new();
                let mut kw1384 = Vec::new();
                args1383.push({
                    let e = e.child();
                    let out1386 = Val::list(vec![]);
                    for item1387 in {
                        let fun1390 = e.get("zip")?;
                        let mut args1388 = Vec::new();
                        let mut kw1389 = Vec::new();
                        args1388.push(e.get("centre")?);
                        args1388.push(e.get("down")?);
                        fun1390.call(args1388, kw1389)?
                    }
                    .iter()?
                    {
                        let unpack1391 = unpack(item1387, 2)?;
                        e.set("c", unpack1391[0].clone())?;
                        e.set("d", unpack1391[1].clone())?;
                        out1386.attr("append")?.call(
                            vec![binary(
                                "add",
                                e.get("c")?,
                                binary(
                                    "mul",
                                    e.get("data")?
                                        .get(Val::Str("tie_route_native_down_mm".into()))?,
                                    e.get("d")?,
                                )?,
                            )?],
                            vec![],
                        )?;
                    }
                    out1386
                });
                fun1385.call(args1383, kw1384)?
            };
            e.set("line_origin", assigned1382.clone())?;
            let assigned1392 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("data")?
                        .get(Val::Str("stock_min_world_mm".into()))?
                        .get(Val::Int(0i64))?,
                    Val::Float(0.8f64),
                )?);
                s.push(binary(
                    "add",
                    e.get("data")?
                        .get(Val::Str("stock_max_world_mm".into()))?
                        .get(Val::Int(0i64))?,
                    Val::Float(0.8f64),
                )?);
                Val::tuple(s)
            };
            let unpack1393 = unpack(assigned1392.clone(), 2)?;
            e.set("west_x", unpack1393[0].clone())?;
            e.set("east_x", unpack1393[1].clone())?;
            // at_x
            e.set("at_x", {
                let params = vec![("x".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned1394 = binary(
                        "truediv",
                        binary(
                            "sub",
                            e.get("x")?,
                            e.get("line_origin")?.get(Val::Int(0i64))?,
                        )?,
                        e.get("u")?.get(Val::Int(0i64))?,
                    )?;
                    e.set("t", assigned1394.clone())?;
                    return Ok({
                        let fun1397 = e.get("tuple")?;
                        let mut args1395 = Vec::new();
                        let mut kw1396 = Vec::new();
                        args1395.push({
                            let e = e.child();
                            let out1398 = Val::list(vec![]);
                            for item1399 in {
                                let fun1402 = e.get("zip")?;
                                let mut args1400 = Vec::new();
                                let mut kw1401 = Vec::new();
                                args1400.push(e.get("line_origin")?);
                                args1400.push(e.get("u")?);
                                fun1402.call(args1400, kw1401)?
                            }
                            .iter()?
                            {
                                let unpack1403 = unpack(item1399, 2)?;
                                e.set("p", unpack1403[0].clone())?;
                                e.set("a", unpack1403[1].clone())?;
                                out1398.attr("append")?.call(
                                    vec![binary(
                                        "add",
                                        e.get("p")?,
                                        binary("mul", e.get("t")?, e.get("a")?)?,
                                    )?],
                                    vec![],
                                )?;
                            }
                            out1398
                        });
                        fun1397.call(args1395, kw1396)?
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned1404 = {
                let mut s = Vec::new();
                s.push({
                    let fun1407 = e.get("at_x")?;
                    let mut args1405 = Vec::new();
                    let mut kw1406 = Vec::new();
                    args1405.push(e.get("west_x")?);
                    fun1407.call(args1405, kw1406)?
                });
                s.push({
                    let fun1410 = e.get("at_x")?;
                    let mut args1408 = Vec::new();
                    let mut kw1409 = Vec::new();
                    args1408.push(e.get("east_x")?);
                    fun1410.call(args1408, kw1409)?
                });
                Val::tuple(s)
            };
            let unpack1411 = unpack(assigned1404.clone(), 2)?;
            e.set("west_lower", unpack1411[0].clone())?;
            e.set("east_lower", unpack1411[1].clone())?;
            let assigned1412 = {
                let mut s = Vec::new();
                s.push(e.get("west_x")?);
                s.push(e.get("centre")?.get(Val::Int(1i64))?);
                s.push({
                    let fun1415 = e.get("max")?;
                    let mut args1413 = Vec::new();
                    let mut kw1414 = Vec::new();
                    args1413.push(binary(
                        "add",
                        e.get("centre")?.get(Val::Int(2i64))?,
                        Val::Float(3.0f64),
                    )?);
                    args1413.push(binary(
                        "add",
                        e.get("upper")?.get(Val::Int(2i64))?,
                        Val::Float(1.0f64),
                    )?);
                    fun1415.call(args1413, kw1414)?
                });
                Val::tuple(s)
            };
            e.set("west_upper", assigned1412.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let fun1418 = e.get("_tie_arc")?;
                    let mut args1416 = Vec::new();
                    let mut kw1417 = Vec::new();
                    args1416.push(e.get("centre")?);
                    args1416.push(e.get("u")?);
                    args1416.push(e.get("v")?);
                    args1416.push(e.get("radius")?);
                    args1416.push(unary("neg", Val::Float(20.0f64))?);
                    args1416.push(Val::Float(170.0f64));
                    fun1418.call(args1416, kw1417)?
                });
                s.push({
                    let fun1421 = e.get("_tie_line")?;
                    let mut args1419 = Vec::new();
                    let mut kw1420 = Vec::new();
                    args1419.push(e.get("upper")?);
                    args1419.push(e.get("west_upper")?);
                    args1419.push(e.get("axis")?);
                    fun1421.call(args1419, kw1420)?
                });
                s.push({
                    let fun1424 = e.get("_tie_line")?;
                    let mut args1422 = Vec::new();
                    let mut kw1423 = Vec::new();
                    args1422.push(e.get("west_upper")?);
                    args1422.push(e.get("west_lower")?);
                    args1422.push(e.get("axis")?);
                    fun1424.call(args1422, kw1423)?
                });
                s.push({
                    let fun1427 = e.get("_tie_line")?;
                    let mut args1425 = Vec::new();
                    let mut kw1426 = Vec::new();
                    args1425.push(e.get("west_lower")?);
                    args1425.push(e.get("east_lower")?);
                    args1425.push(e.get("axis")?);
                    fun1427.call(args1425, kw1426)?
                });
                s.push({
                    let fun1430 = e.get("_tie_line")?;
                    let mut args1428 = Vec::new();
                    let mut kw1429 = Vec::new();
                    args1428.push(e.get("east_lower")?);
                    args1428.push(e.get("lower")?);
                    args1428.push(e.get("axis")?);
                    fun1430.call(args1428, kw1429)?
                });
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    // union_tie_routes
    e.set("union_tie_routes", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1431 = {
                let fun1434 = e.get("union_support_datums")?;
                let mut args1432 = Vec::new();
                let mut kw1433 = Vec::new();
                fun1434.call(args1432, kw1433)?
            };
            e.set("data", assigned1431.clone())?;
            let assigned1435 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("vb-outlet-return".into()), e.get("_vb_union_tie")?)?;
                d
            };
            e.set("builders", assigned1435.clone())?;
            let assigned1436 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("result", assigned1436.clone())?;
            for item1437 in {
                let fun1451 = e.get("builders")?.attr("items")?;
                let mut args1449 = Vec::new();
                let mut kw1450 = Vec::new();
                fun1451.call(args1449, kw1450)?
            }
            .iter()?
            {
                let unpack1452 = unpack(item1437, 2)?;
                e.set("name", unpack1452[0].clone())?;
                e.set("builder", unpack1452[1].clone())?;
                if unary("not", {
                    let fun1440 = e.get("data")?.get(e.get("name")?)?.attr("get")?;
                    let mut args1438 = Vec::new();
                    let mut kw1439 = Vec::new();
                    args1438.push(Val::Str("support_implemented".into()));
                    args1438.push(Val::Bool(true));
                    fun1440.call(args1438, kw1439)?
                })?
                .truthy()?
                {
                    continue;
                }
                let assigned1441 = {
                    let fun1444 = e.get("builder")?;
                    let mut args1442 = Vec::new();
                    let mut kw1443 = Vec::new();
                    args1442.push(e.get("data")?.get(e.get("name")?)?);
                    fun1444.call(args1442, kw1443)?
                };
                e.set("segments", assigned1441.clone())?;
                let assigned1445 = {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("segments".into()), e.get("segments")?)?;
                    d.set(Val::Str("length_mm".into()), {
                        let fun1448 = e.get("_tie_length")?;
                        let mut args1446 = Vec::new();
                        let mut kw1447 = Vec::new();
                        args1446.push(e.get("segments")?);
                        fun1448.call(args1446, kw1447)?
                    })?;
                    d.set(
                        Val::Str("stock".into()),
                        Val::Str("6-inch narrow nylon tie".into()),
                    )?;
                    d.set(Val::Str("stock_length_mm".into()), Val::Float(152.4f64))?;
                    d.set(Val::Str("width_mm".into()), Val::Float(2.5f64))?;
                    d.set(Val::Str("thickness_mm".into()), Val::Float(0.8f64))?;
                    d.set(
                        Val::Str("strip_basis".into()),
                        Val::Str(
                            "Nominal layout allowance; purchased strap dimensions unmeasured"
                                .into(),
                        ),
                    )?;
                    d
                };
                e.get("result")?.set(e.get("name")?, assigned1445.clone())?;
            }
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // meter_tie_routes
    e.set("meter_tie_routes", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let d = Val::dict(vec![]);
                d
            });
            Ok(Val::None)
        })
    })?;
    // nominal_tie_strips
    e.set("nominal_tie_strips", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned1453 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("result", assigned1453.clone())?;
            let assigned1454 = {
                let d = Val::dict(vec![]);
                dict_extend(&d, {
                    let fun1457 = e.get("union_tie_routes")?;
                    let mut args1455 = Vec::new();
                    let mut kw1456 = Vec::new();
                    fun1457.call(args1455, kw1456)?
                })?;
                dict_extend(&d, {
                    let fun1460 = e.get("meter_tie_routes")?;
                    let mut args1458 = Vec::new();
                    let mut kw1459 = Vec::new();
                    fun1460.call(args1458, kw1459)?
                })?;
                d
            };
            e.set("routes", assigned1454.clone())?;
            for item1461 in {
                let fun1559 = e.get("routes")?.attr("items")?;
                let mut args1557 = Vec::new();
                let mut kw1558 = Vec::new();
                fun1559.call(args1557, kw1558)?
            }
            .iter()?
            {
                let unpack1560 = unpack(item1461, 2)?;
                e.set("name", unpack1560[0].clone())?;
                e.set("data", unpack1560[1].clone())?;
                let assigned1462 = {
                    let mut s = Vec::new();
                    Val::list(s)
                };
                e.set("pieces", assigned1462.clone())?;
                for item1463 in e.get("data")?.get(Val::Str("segments".into()))?.iter()? {
                    e.set("segment", item1463)?;
                    if {
                        let v1464 = e.get("segment")?.get(Val::Str("kind".into()))?;
                        let v1465 = Val::Str("arc".into());
                        Val::Bool(compare("eq", v1464.clone(), v1465.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned1466 = {
                            let fun1469 = e.get("cq")?.attr("Edge")?.attr("makeThreePointArc")?;
                            let mut args1467 = Vec::new();
                            let mut kw1468 = Vec::new();
                            args1467.extend(
                                {
                                    let e = e.child();
                                    let out1470 = Val::list(vec![]);
                                    for item1471 in e
                                        .get("segment")?
                                        .get(Val::Str("points_mm".into()))?
                                        .iter()?
                                    {
                                        e.set("point", item1471)?;
                                        out1470.attr("append")?.call(
                                            vec![{
                                                let fun1474 = e.get("cq")?.attr("Vector")?;
                                                let mut args1472 = Vec::new();
                                                let mut kw1473 = Vec::new();
                                                args1472.extend(e.get("point")?.iter()?);
                                                fun1474.call(args1472, kw1473)?
                                            }],
                                            vec![],
                                        )?;
                                    }
                                    out1470
                                }
                                .iter()?,
                            );
                            fun1469.call(args1467, kw1468)?
                        };
                        e.set("edge", assigned1466.clone())?;
                        let assigned1475 = {
                            let fun1478 = e.get("cq")?.attr("Wire")?.attr("assembleEdges")?;
                            let mut args1476 = Vec::new();
                            let mut kw1477 = Vec::new();
                            args1476.push({
                                let mut s = Vec::new();
                                s.push(e.get("edge")?);
                                Val::list(s)
                            });
                            fun1478.call(args1476, kw1477)?
                        };
                        e.set("wire", assigned1475.clone())?;
                        let assigned1479 = {
                            let fun1482 = e.get("cq")?.attr("Plane")?;
                            let mut args1480 = Vec::new();
                            let mut kw1481 = Vec::new();
                            kw1481.push(("origin".into(), {
                                let fun1485 = e.get("edge")?.attr("startPoint")?;
                                let mut args1483 = Vec::new();
                                let mut kw1484 = Vec::new();
                                fun1485.call(args1483, kw1484)?
                            }));
                            kw1481.push(("normal".into(), {
                                let fun1488 = e.get("edge")?.attr("tangentAt")?;
                                let mut args1486 = Vec::new();
                                let mut kw1487 = Vec::new();
                                args1486.push(Val::Int(0i64));
                                fun1488.call(args1486, kw1487)?
                            }));
                            kw1481.push(("xDir".into(), {
                                let fun1491 = e.get("cq")?.attr("Vector")?;
                                let mut args1489 = Vec::new();
                                let mut kw1490 = Vec::new();
                                args1489.extend(
                                    e.get("segment")?
                                        .get(Val::Str("wide_axis".into()))?
                                        .iter()?,
                                );
                                fun1491.call(args1489, kw1490)?
                            }));
                            fun1482.call(args1480, kw1481)?
                        };
                        e.set("plane", assigned1479.clone())?;
                        let assigned1492 = {
                            let fun1495 = {
                                let fun1498 = {
                                    let fun1501 = {
                                        let fun1504 = e.get("cq")?.attr("Workplane")?;
                                        let mut args1502 = Vec::new();
                                        let mut kw1503 = Vec::new();
                                        args1502.push(e.get("plane")?);
                                        fun1504.call(args1502, kw1503)?
                                    }
                                    .attr("rect")?;
                                    let mut args1499 = Vec::new();
                                    let mut kw1500 = Vec::new();
                                    args1499.push(e.get("data")?.get(Val::Str("width_mm".into()))?);
                                    args1499
                                        .push(e.get("data")?.get(Val::Str("thickness_mm".into()))?);
                                    fun1501.call(args1499, kw1500)?
                                }
                                .attr("sweep")?;
                                let mut args1496 = Vec::new();
                                let mut kw1497 = Vec::new();
                                args1496.push(e.get("wire")?);
                                kw1497.push(("isFrenet".into(), Val::Bool(true)));
                                kw1497.push(("transition".into(), Val::Str("round".into())));
                                fun1498.call(args1496, kw1497)?
                            }
                            .attr("val")?;
                            let mut args1493 = Vec::new();
                            let mut kw1494 = Vec::new();
                            fun1495.call(args1493, kw1494)?
                        };
                        e.set("piece", assigned1492.clone())?;
                    } else {
                        let assigned1505 = {
                            let e = e.child();
                            let out1506 = Val::list(vec![]);
                            for item1507 in e
                                .get("segment")?
                                .get(Val::Str("points_mm".into()))?
                                .iter()?
                            {
                                e.set("point", item1507)?;
                                out1506.attr("append")?.call(
                                    vec![{
                                        let fun1510 = e.get("cq")?.attr("Vector")?;
                                        let mut args1508 = Vec::new();
                                        let mut kw1509 = Vec::new();
                                        args1508.extend(e.get("point")?.iter()?);
                                        fun1510.call(args1508, kw1509)?
                                    }],
                                    vec![],
                                )?;
                            }
                            out1506
                        };
                        let unpack1511 = unpack(assigned1505.clone(), 2)?;
                        e.set("first", unpack1511[0].clone())?;
                        e.set("last", unpack1511[1].clone())?;
                        let assigned1512 = {
                            let fun1515 = binary("sub", e.get("last")?, e.get("first")?)?
                                .attr("normalized")?;
                            let mut args1513 = Vec::new();
                            let mut kw1514 = Vec::new();
                            fun1515.call(args1513, kw1514)?
                        };
                        e.set("tangent", assigned1512.clone())?;
                        let assigned1516 = {
                            let fun1519 = e.get("cq")?.attr("Vector")?;
                            let mut args1517 = Vec::new();
                            let mut kw1518 = Vec::new();
                            args1517.extend(
                                e.get("segment")?
                                    .get(Val::Str("wide_axis".into()))?
                                    .iter()?,
                            );
                            fun1519.call(args1517, kw1518)?
                        };
                        e.set("wide", assigned1516.clone())?;
                        let assigned1520 = {
                            let fun1523 = binary(
                                "sub",
                                e.get("wide")?,
                                binary("mul", e.get("tangent")?, {
                                    let fun1526 = e.get("wide")?.attr("dot")?;
                                    let mut args1524 = Vec::new();
                                    let mut kw1525 = Vec::new();
                                    args1524.push(e.get("tangent")?);
                                    fun1526.call(args1524, kw1525)?
                                })?,
                            )?
                            .attr("normalized")?;
                            let mut args1521 = Vec::new();
                            let mut kw1522 = Vec::new();
                            fun1523.call(args1521, kw1522)?
                        };
                        e.set("wide", assigned1520.clone())?;
                        let assigned1527 = {
                            let fun1530 = {
                                let fun1533 = e.get("tangent")?.attr("cross")?;
                                let mut args1531 = Vec::new();
                                let mut kw1532 = Vec::new();
                                args1531.push(e.get("wide")?);
                                fun1533.call(args1531, kw1532)?
                            }
                            .attr("normalized")?;
                            let mut args1528 = Vec::new();
                            let mut kw1529 = Vec::new();
                            fun1530.call(args1528, kw1529)?
                        };
                        e.set("thin", assigned1527.clone())?;
                        // rectangle
                        e.set("rectangle", {
                            let params = vec![("at".into(), None, false)];
                            let outer = e.clone();
                            let runtime = rt.clone();
                            Val::function(move |args, kwargs| {
                                let rt = runtime.clone();
                                let e = bind(&outer, &params, args, kwargs, None, None)?;
                                let _frame = rt.frame(&outer);
                                return Ok({
                                    let fun1536 = e.get("cq")?.attr("Wire")?.attr("makePolygon")?;
                                    let mut args1534 = Vec::new();
                                    let mut kw1535 = Vec::new();
                                    args1534.push({
                                        let e = e.child();
                                        let out1537 = Val::list(vec![]);
                                        for item1538 in {
                                            let mut s = Vec::new();
                                            s.push({
                                                let mut s = Vec::new();
                                                s.push(binary(
                                                    "truediv",
                                                    unary(
                                                        "neg",
                                                        e.get("data")?
                                                            .get(Val::Str("width_mm".into()))?,
                                                    )?,
                                                    Val::Float(2.0f64),
                                                )?);
                                                s.push(binary(
                                                    "truediv",
                                                    unary(
                                                        "neg",
                                                        e.get("data")?
                                                            .get(Val::Str("thickness_mm".into()))?,
                                                    )?,
                                                    Val::Float(2.0f64),
                                                )?);
                                                Val::tuple(s)
                                            });
                                            s.push({
                                                let mut s = Vec::new();
                                                s.push(binary(
                                                    "truediv",
                                                    e.get("data")?
                                                        .get(Val::Str("width_mm".into()))?,
                                                    Val::Float(2.0f64),
                                                )?);
                                                s.push(binary(
                                                    "truediv",
                                                    unary(
                                                        "neg",
                                                        e.get("data")?
                                                            .get(Val::Str("thickness_mm".into()))?,
                                                    )?,
                                                    Val::Float(2.0f64),
                                                )?);
                                                Val::tuple(s)
                                            });
                                            s.push({
                                                let mut s = Vec::new();
                                                s.push(binary(
                                                    "truediv",
                                                    e.get("data")?
                                                        .get(Val::Str("width_mm".into()))?,
                                                    Val::Float(2.0f64),
                                                )?);
                                                s.push(binary(
                                                    "truediv",
                                                    e.get("data")?
                                                        .get(Val::Str("thickness_mm".into()))?,
                                                    Val::Float(2.0f64),
                                                )?);
                                                Val::tuple(s)
                                            });
                                            s.push({
                                                let mut s = Vec::new();
                                                s.push(binary(
                                                    "truediv",
                                                    unary(
                                                        "neg",
                                                        e.get("data")?
                                                            .get(Val::Str("width_mm".into()))?,
                                                    )?,
                                                    Val::Float(2.0f64),
                                                )?);
                                                s.push(binary(
                                                    "truediv",
                                                    e.get("data")?
                                                        .get(Val::Str("thickness_mm".into()))?,
                                                    Val::Float(2.0f64),
                                                )?);
                                                Val::tuple(s)
                                            });
                                            Val::tuple(s)
                                        }
                                        .iter()?
                                        {
                                            let unpack1539 = unpack(item1538, 2)?;
                                            e.set("w", unpack1539[0].clone())?;
                                            e.set("t", unpack1539[1].clone())?;
                                            out1537.attr("append")?.call(
                                                vec![binary(
                                                    "add",
                                                    binary(
                                                        "add",
                                                        e.get("at")?,
                                                        binary("mul", e.get("wide")?, e.get("w")?)?,
                                                    )?,
                                                    binary("mul", e.get("thin")?, e.get("t")?)?,
                                                )?],
                                                vec![],
                                            )?;
                                        }
                                        out1537
                                    });
                                    kw1535.push(("close".into(), Val::Bool(true)));
                                    fun1536.call(args1534, kw1535)?
                                });
                                Ok(Val::None)
                            })
                        })?;
                        let assigned1540 = {
                            let fun1543 = e.get("cq")?.attr("Solid")?.attr("makeLoft")?;
                            let mut args1541 = Vec::new();
                            let mut kw1542 = Vec::new();
                            args1541.push({
                                let mut s = Vec::new();
                                s.push({
                                    let fun1546 = e.get("rectangle")?;
                                    let mut args1544 = Vec::new();
                                    let mut kw1545 = Vec::new();
                                    args1544.push(e.get("first")?);
                                    fun1546.call(args1544, kw1545)?
                                });
                                s.push({
                                    let fun1549 = e.get("rectangle")?;
                                    let mut args1547 = Vec::new();
                                    let mut kw1548 = Vec::new();
                                    args1547.push(e.get("last")?);
                                    fun1549.call(args1547, kw1548)?
                                });
                                Val::list(s)
                            });
                            kw1542.push(("ruled".into(), Val::Bool(true)));
                            fun1543.call(args1541, kw1542)?
                        };
                        e.set("piece", assigned1540.clone())?;
                    }
                    {
                        let fun1552 = e.get("pieces")?.attr("append")?;
                        let mut args1550 = Vec::new();
                        let mut kw1551 = Vec::new();
                        args1550.push(e.get("piece")?);
                        fun1552.call(args1550, kw1551)?
                    };
                }
                let assigned1553 = {
                    let fun1556 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                    let mut args1554 = Vec::new();
                    let mut kw1555 = Vec::new();
                    args1554.push(e.get("pieces")?);
                    fun1556.call(args1554, kw1555)?
                };
                e.get("result")?.set(e.get("name")?, assigned1553.clone())?;
            }
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // gas_guide_xy
    e.set("gas_guide_xy", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun1563 = e.get("above_core")?.attr("world_to_cap")?;
                let mut args1561 = Vec::new();
                let mut kw1562 = Vec::new();
                args1561.push(
                    {
                        let fun1566 = e.get("above_core")?.attr("specification")?;
                        let mut args1564 = Vec::new();
                        let mut kw1565 = Vec::new();
                        fun1566.call(args1564, kw1565)?
                    }
                    .get(Val::Str("gas_guide_world_mm".into()))?,
                );
                fun1563.call(args1561, kw1562)?
            }
            .get(Val::Slice {
                start: None,
                stop: Some(Val::Int(2i64).integer()?),
                step: 1,
            })?);
            Ok(Val::None)
        })
    })?;
    // cap_guide_xy
    e.set("cap_guide_xy", {
        let params = vec![
            ("name".into(), None, false),
            ("fallback".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1567 = {
                let fun1570 = {
                    let fun1573 = e.get("above_core")?.attr("specification")?;
                    let mut args1571 = Vec::new();
                    let mut kw1572 = Vec::new();
                    fun1573.call(args1571, kw1572)?
                }
                .get(Val::Str("cap_guides_world_mm".into()))?
                .attr("get")?;
                let mut args1568 = Vec::new();
                let mut kw1569 = Vec::new();
                args1568.push(e.get("name")?);
                fun1570.call(args1568, kw1569)?
            };
            e.set("point", assigned1567.clone())?;
            return Ok(
                if {
                    let v1574 = e.get("point")?;
                    let v1575 = Val::None;
                    Val::Bool(compare("is", v1574.clone(), v1575.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("fallback")?
                } else {
                    {
                        let fun1578 = e.get("above_core")?.attr("world_to_cap")?;
                        let mut args1576 = Vec::new();
                        let mut kw1577 = Vec::new();
                        args1576.push(e.get("point")?);
                        fun1578.call(args1576, kw1577)?
                    }
                    .get(Val::Slice {
                        start: None,
                        stop: Some(Val::Int(2i64).integer()?),
                        step: 1,
                    })?
                },
            );
            Ok(Val::None)
        })
    })?;
    // world_shape_in_cap
    e.set("world_shape_in_cap", {
        let params = vec![("shape".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1579 = {
                let fun1582 = e.get("above_core")?.attr("cap_lid_pose")?;
                let mut args1580 = Vec::new();
                let mut kw1581 = Vec::new();
                fun1582.call(args1580, kw1581)?
            };
            e.set("frame", assigned1579.clone())?;
            let assigned1583 = {
                let fun1586 = e.get("tuple")?;
                let mut args1584 = Vec::new();
                let mut kw1585 = Vec::new();
                args1584.push({
                    let fun1589 = e.get("zip")?;
                    let mut args1587 = Vec::new();
                    let mut kw1588 = Vec::new();
                    args1587.extend(e.get("frame")?.get(Val::Str("rotation".into()))?.iter()?);
                    fun1589.call(args1587, kw1588)?
                });
                fun1586.call(args1584, kw1585)?
            };
            e.set("rotation", assigned1583.clone())?;
            let assigned1590 = {
                let fun1593 = e.get("above_core")?.attr("vector")?;
                let mut args1591 = Vec::new();
                let mut kw1592 = Vec::new();
                args1591.push(e.get("rotation")?);
                args1591.push({
                    let fun1596 = e.get("tuple")?;
                    let mut args1594 = Vec::new();
                    let mut kw1595 = Vec::new();
                    args1594.push({
                        let e = e.child();
                        let out1597 = Val::list(vec![]);
                        for item1598 in e
                            .get("frame")?
                            .get(Val::Str("translation_mm".into()))?
                            .iter()?
                        {
                            e.set("v", item1598)?;
                            out1597
                                .attr("append")?
                                .call(vec![unary("neg", e.get("v")?)?], vec![])?;
                        }
                        out1597
                    });
                    fun1596.call(args1594, kw1595)?
                });
                fun1593.call(args1591, kw1592)?
            };
            e.set("translation", assigned1590.clone())?;
            return Ok({
                let fun1601 = e.get("shape")?.attr("moved")?;
                let mut args1599 = Vec::new();
                let mut kw1600 = Vec::new();
                args1599.push({
                    let fun1604 = e.get("above_core")?.attr("frame_location")?;
                    let mut args1602 = Vec::new();
                    let mut kw1603 = Vec::new();
                    args1602.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("rotation".into()), e.get("rotation")?)?;
                        d.set(Val::Str("translation_mm".into()), e.get("translation")?)?;
                        d
                    });
                    fun1604.call(args1602, kw1603)?
                });
                fun1601.call(args1599, kw1600)?
            });
            Ok(Val::None)
        })
    })?;
    // passive_guide_points
    e.set("passive_guide_points", {
        let params = vec![
            ("lower_xy".into(), None, false),
            ("upper_xy".into(), None, false),
            ("start_z".into(), None, false),
            ("end_z".into(), None, false),
            ("bend_start_z".into(), None, false),
            ("radius".into(), Some(Val::Float(14.0f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1605 = {
                let fun1608 = e.get("math")?.attr("dist")?;
                let mut args1606 = Vec::new();
                let mut kw1607 = Vec::new();
                args1606.push(e.get("lower_xy")?);
                args1606.push(e.get("upper_xy")?);
                fun1608.call(args1606, kw1607)?
            };
            e.set("distance", assigned1605.clone())?;
            if {
                let v1609 = e.get("distance")?;
                let v1610 = Val::Float(1e-09f64);
                Val::Bool(compare("lt", v1609.clone(), v1610.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.extend(e.get("lower_xy")?.iter()?);
                        s.push(e.get("start_z")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.extend(e.get("upper_xy")?.iter()?);
                        s.push(e.get("end_z")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
            }
            let assigned1611 = {
                let fun1614 = e.get("math")?.attr("acos")?;
                let mut args1612 = Vec::new();
                let mut kw1613 = Vec::new();
                args1612.push(binary(
                    "sub",
                    Val::Float(1.0f64),
                    binary(
                        "truediv",
                        e.get("distance")?,
                        binary("mul", Val::Float(2.0f64), e.get("radius")?)?,
                    )?,
                )?);
                fun1614.call(args1612, kw1613)?
            };
            e.set("theta", assigned1611.clone())?;
            let assigned1615 = binary("mul", e.get("radius")?, {
                let fun1618 = e.get("math")?.attr("tan")?;
                let mut args1616 = Vec::new();
                let mut kw1617 = Vec::new();
                args1616.push(binary("truediv", e.get("theta")?, Val::Float(2.0f64))?);
                fun1618.call(args1616, kw1617)?
            })?;
            e.set("setback", assigned1615.clone())?;
            let assigned1619 = binary(
                "mul",
                binary("mul", Val::Float(2.0f64), e.get("radius")?)?,
                {
                    let fun1622 = e.get("math")?.attr("sin")?;
                    let mut args1620 = Vec::new();
                    let mut kw1621 = Vec::new();
                    args1620.push(e.get("theta")?);
                    fun1622.call(args1620, kw1621)?
                },
            )?;
            e.set("rise", assigned1619.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.extend(e.get("lower_xy")?.iter()?);
                    s.push(e.get("start_z")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.extend(e.get("lower_xy")?.iter()?);
                    s.push(binary("add", e.get("bend_start_z")?, e.get("setback")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.extend(e.get("upper_xy")?.iter()?);
                    s.push(binary(
                        "sub",
                        binary("add", e.get("bend_start_z")?, e.get("rise")?)?,
                        e.get("setback")?,
                    )?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.extend(e.get("upper_xy")?.iter()?);
                    s.push(e.get("end_z")?);
                    Val::tuple(s)
                });
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    // cable_guide_points
    e.set("cable_guide_points", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1623 = {
                let fun1626 = e.get("importlib")?.attr("import_module")?;
                let mut args1624 = Vec::new();
                let mut kw1625 = Vec::new();
                args1624.push(Val::Str("_cold_core_interface".into()));
                fun1626.call(args1624, kw1625)?
            };
            e.set("core", assigned1623.clone())?;
            let assigned1627 = {
                let fun1630 = e.get("above_core")?.attr("specification")?;
                let mut args1628 = Vec::new();
                let mut kw1629 = Vec::new();
                fun1630.call(args1628, kw1629)?
            };
            e.set("spec", assigned1627.clone())?;
            let assigned1631 = {
                let fun1634 = e.get("above_core")?.attr("point")?;
                let mut args1632 = Vec::new();
                let mut kw1633 = Vec::new();
                args1632.push({
                    let fun1637 = e.get("above_core")?.attr("cap_lid_pose")?;
                    let mut args1635 = Vec::new();
                    let mut kw1636 = Vec::new();
                    fun1637.call(args1635, kw1636)?
                });
                args1632.push({
                    let mut s = Vec::new();
                    s.extend(
                        e.get("core")?
                            .attr("cap_conduit_floor_xy")?
                            .get(e.get("name")?)?
                            .iter()?,
                    );
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun1634.call(args1632, kw1633)?
            }
            .get(Val::Slice {
                start: None,
                stop: Some(Val::Int(2i64).integer()?),
                step: 1,
            })?;
            e.set("lower_xy", assigned1631.clone())?;
            let assigned1638 = {
                let fun1641 = e.get("above_core")?.attr("point")?;
                let mut args1639 = Vec::new();
                let mut kw1640 = Vec::new();
                args1639.push({
                    let fun1644 = e.get("above_core")?.attr("cap_lid_pose")?;
                    let mut args1642 = Vec::new();
                    let mut kw1643 = Vec::new();
                    fun1644.call(args1642, kw1643)?
                });
                args1639.push({
                    let mut s = Vec::new();
                    s.extend(
                        e.get("core")?
                            .attr("cap_conduits")?
                            .get(e.get("name")?)?
                            .iter()?,
                    );
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun1641.call(args1639, kw1640)?
            }
            .get(Val::Slice {
                start: None,
                stop: Some(Val::Int(2i64).integer()?),
                step: 1,
            })?;
            e.set("upper_xy", assigned1638.clone())?;
            let assigned1645 = binary(
                "sub",
                e.get("core")?.attr("foam_cap_height")?,
                e.get("core")?.attr("head_pad_height")?,
            )?;
            e.set("cup_height", assigned1645.clone())?;
            let assigned1646 = binary(
                "sub",
                e.get("spec")?
                    .get(Val::Str("cap_lid_pose".into()))?
                    .get(Val::Str("translation_mm".into()))?
                    .get(Val::Int(2i64))?,
                e.get("cup_height")?,
            )?;
            e.set("cup_bottom", assigned1646.clone())?;
            let assigned1647 = binary(
                "sub",
                e.get("spec")?
                    .get(Val::Str("cap_lid_pose".into()))?
                    .get(Val::Str("translation_mm".into()))?
                    .get(Val::Int(2i64))?,
                Val::Float(6.6f64),
            )?;
            e.set("mid_z", assigned1647.clone())?;
            if {
                let v1651 = {
                    let fun1650 = e.get("math")?.attr("dist")?;
                    let mut args1648 = Vec::new();
                    let mut kw1649 = Vec::new();
                    args1648.push(e.get("lower_xy")?);
                    args1648.push(e.get("upper_xy")?);
                    fun1650.call(args1648, kw1649)?
                };
                let v1652 = Val::Float(1e-09f64);
                Val::Bool(compare("lt", v1651.clone(), v1652.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("points_mm".into()), {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.extend(e.get("lower_xy")?.iter()?);
                            s.push(binary("sub", e.get("cup_bottom")?, Val::Float(1.0f64))?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.extend(e.get("upper_xy")?.iter()?);
                            s.push(binary(
                                "add",
                                e.get("spec")?.get(Val::Str("cap_face_z_mm".into()))?,
                                Val::Float(2.0f64),
                            )?);
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("bend_radius_mm".into()), Val::Float(5.5f64))?;
                    d
                });
            }
            if {
                let v1653 = e.get("name")?;
                let v1654 = Val::Str("sensor-cable".into());
                Val::Bool(compare("eq", v1653.clone(), v1654.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned1655 = {
                    let mut s = Vec::new();
                    s.push(e.get("lower_xy")?);
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("lower_xy")?.get(Val::Int(0i64))?);
                        s.push(e.get("upper_xy")?.get(Val::Int(1i64))?);
                        Val::tuple(s)
                    });
                    s.push(e.get("upper_xy")?);
                    Val::tuple(s)
                };
                e.set("plan", assigned1655.clone())?;
            } else {
                let assigned1656 = {
                    let mut s = Vec::new();
                    s.push(e.get("lower_xy")?);
                    s.push(e.get("upper_xy")?);
                    Val::tuple(s)
                };
                e.set("plan", assigned1656.clone())?;
            }
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("points_mm".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.extend(e.get("lower_xy")?.iter()?);
                        s.push(binary("sub", e.get("cup_bottom")?, Val::Float(1.0f64))?);
                        Val::tuple(s)
                    });
                    s.extend(
                        {
                            let e = e.child();
                            let out1657 = Val::list(vec![]);
                            for item1658 in e.get("plan")?.iter()? {
                                e.set("xy", item1658)?;
                                out1657.attr("append")?.call(
                                    vec![{
                                        let mut s = Vec::new();
                                        s.extend(e.get("xy")?.iter()?);
                                        s.push(e.get("mid_z")?);
                                        Val::tuple(s)
                                    }],
                                    vec![],
                                )?;
                            }
                            out1657
                        }
                        .iter()?,
                    );
                    s.push({
                        let mut s = Vec::new();
                        s.extend(e.get("upper_xy")?.iter()?);
                        s.push(binary(
                            "add",
                            e.get("spec")?.get(Val::Str("cap_face_z_mm".into()))?,
                            Val::Float(2.0f64),
                        )?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("bend_radius_mm".into()), Val::Float(5.5f64))?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // water_in_guide_points
    e.set("water_in_guide_points", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1659 = {
                let fun1662 = e.get("importlib")?.attr("import_module")?;
                let mut args1660 = Vec::new();
                let mut kw1661 = Vec::new();
                args1660.push(Val::Str("_cold_core_interface".into()));
                fun1662.call(args1660, kw1661)?
            };
            e.set("core", assigned1659.clone())?;
            let assigned1663 = {
                let fun1666 = e.get("tuple")?;
                let mut args1664 = Vec::new();
                let mut kw1665 = Vec::new();
                args1664.push(
                    {
                        let fun1669 = e.get("above_core")?.attr("specification")?;
                        let mut args1667 = Vec::new();
                        let mut kw1668 = Vec::new();
                        fun1669.call(args1667, kw1668)?
                    }
                    .get(Val::Str("cap_guides_world_mm".into()))?
                    .get(Val::Str("water-in".into()))?,
                );
                fun1666.call(args1664, kw1665)?
            };
            e.set("guide", assigned1663.clone())?;
            let assigned1670 = binary(
                "add",
                binary(
                    "add",
                    binary(
                        "add",
                        e.get("core")?.attr("wall_and_floor_thickness")?,
                        e.get("core")?.attr("carbonator_support_ring_height")?,
                    )?,
                    e.get("core")?.attr("carbonator_height")?,
                )?,
                e.get("core")?.attr("hole_shift_from_edge")?,
            )?;
            e.set("band", assigned1670.clone())?;
            let assigned1671 = binary(
                "sub",
                e.get("core")?.attr("foam_cap_height")?,
                e.get("core")?.attr("head_pad_height")?,
            )?;
            e.set("cup_height", assigned1671.clone())?;
            let assigned1672 = binary(
                "sub",
                binary(
                    "sub",
                    {
                        let fun1675 = e.get("above_core")?.attr("cap_lid_pose")?;
                        let mut args1673 = Vec::new();
                        let mut kw1674 = Vec::new();
                        fun1675.call(args1673, kw1674)?
                    }
                    .get(Val::Str("translation_mm".into()))?
                    .get(Val::Int(2i64))?,
                    e.get("cup_height")?,
                )?,
                e.get("core")?.attr("foam_shell_outer_height")?,
            )?;
            e.set("world_z", assigned1672.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.extend(
                        e.get("guide")?
                            .get(Val::Slice {
                                start: None,
                                stop: Some(Val::Int(2i64).integer()?),
                                step: 1,
                            })?
                            .iter()?,
                    );
                    s.push(binary("add", e.get("band")?, e.get("world_z")?)?);
                    Val::tuple(s)
                });
                s.push(e.get("guide")?);
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    // water_in_floor_xy
    e.set("water_in_floor_xy", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun1678 = e.get("above_core")?.attr("world_to_cap")?;
                let mut args1676 = Vec::new();
                let mut kw1677 = Vec::new();
                args1676.push(
                    {
                        let fun1681 = e.get("water_in_guide_points")?;
                        let mut args1679 = Vec::new();
                        let mut kw1680 = Vec::new();
                        fun1681.call(args1679, kw1680)?
                    }
                    .get(unary("neg", Val::Int(1i64))?)?,
                );
                fun1678.call(args1676, kw1677)?
            }
            .get(Val::Slice {
                start: None,
                stop: Some(Val::Int(2i64).integer()?),
                step: 1,
            })?);
            Ok(Val::None)
        })
    })?;
    // water_in_features
    e.set("water_in_features", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun1684 = e.get("straight_cap_features")?;
                let mut args1682 = Vec::new();
                let mut kw1683 = Vec::new();
                args1682.push(Val::Str("water-in".into()));
                fun1684.call(args1682, kw1683)?
            });
            Ok(Val::None)
        })
    })?;
    // soda_out_guide_points
    e.set("soda_out_guide_points", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1685 = {
                let fun1688 = e.get("tuple")?;
                let mut args1686 = Vec::new();
                let mut kw1687 = Vec::new();
                args1686.push(
                    {
                        let fun1691 = e.get("above_core")?.attr("specification")?;
                        let mut args1689 = Vec::new();
                        let mut kw1690 = Vec::new();
                        fun1691.call(args1689, kw1690)?
                    }
                    .get(Val::Str("cap_guides_world_mm".into()))?
                    .get(Val::Str("carb-water-out".into()))?,
                );
                fun1688.call(args1686, kw1687)?
            };
            e.set("guide", assigned1685.clone())?;
            let assigned1692 = {
                let fun1695 = e.get("importlib")?.attr("import_module")?;
                let mut args1693 = Vec::new();
                let mut kw1694 = Vec::new();
                args1693.push(Val::Str("_cold_core_interface".into()));
                fun1695.call(args1693, kw1694)?
            };
            e.set("core", assigned1692.clone())?;
            let assigned1696 = binary(
                "sub",
                {
                    let fun1699 = e.get("above_core")?.attr("cap_lid_pose")?;
                    let mut args1697 = Vec::new();
                    let mut kw1698 = Vec::new();
                    fun1699.call(args1697, kw1698)?
                }
                .get(Val::Str("translation_mm".into()))?
                .get(Val::Int(2i64))?,
                binary(
                    "sub",
                    e.get("core")?.attr("foam_cap_height")?,
                    e.get("core")?.attr("head_pad_height")?,
                )?,
            )?;
            e.set("floor", assigned1696.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.extend(
                        e.get("guide")?
                            .get(Val::Slice {
                                start: None,
                                stop: Some(Val::Int(2i64).integer()?),
                                step: 1,
                            })?
                            .iter()?,
                    );
                    s.push(binary("sub", e.get("floor")?, Val::Float(1.0f64))?);
                    Val::tuple(s)
                });
                s.push(e.get("guide")?);
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    // soda_out_features
    e.set("soda_out_features", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun1702 = e.get("straight_cap_features")?;
                let mut args1700 = Vec::new();
                let mut kw1701 = Vec::new();
                args1700.push(Val::Str("carb-water-out".into()));
                fun1702.call(args1700, kw1701)?
            });
            Ok(Val::None)
        })
    })?;
    // reservoir_b_fill_passage
    e.set("reservoir_b_fill_passage", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun1705 = {
                    let fun1708 = e.get("importlib")?.attr("import_module")?;
                    let mut args1706 = Vec::new();
                    let mut kw1707 = Vec::new();
                    args1706.push(Val::Str("_reservoir_b_fill".into()));
                    fun1708.call(args1706, kw1707)?
                }
                .attr("passage")?;
                let mut args1703 = Vec::new();
                let mut kw1704 = Vec::new();
                fun1705.call(args1703, kw1704)?
            });
            Ok(Val::None)
        })
    })?;
    // reservoir_b_fill_features
    e.set("reservoir_b_fill_features", {
        let params = vec![("cup_height".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun1711 = {
                    let fun1714 = e.get("importlib")?.attr("import_module")?;
                    let mut args1712 = Vec::new();
                    let mut kw1713 = Vec::new();
                    args1712.push(Val::Str("_reservoir_b_fill".into()));
                    fun1714.call(args1712, kw1713)?
                }
                .attr("features")?;
                let mut args1709 = Vec::new();
                let mut kw1710 = Vec::new();
                args1709.push(e.get("cup_height")?);
                fun1711.call(args1709, kw1710)?
            });
            Ok(Val::None)
        })
    })?;
    // schedule
    e.set("schedule", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1715 = {
                let fun1718 = e.get("importlib")?.attr("import_module")?;
                let mut args1716 = Vec::new();
                let mut kw1717 = Vec::new();
                args1716.push(Val::Str("_cold_core_interface".into()));
                fun1718.call(args1716, kw1717)?
            };
            e.set("core", assigned1715.clone())?;
            let assigned1719 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("modules", assigned1719.clone())?;
            for item1720 in {
                let fun1737 = {
                    let fun1740 = e.get("deck_mounts")?;
                    let mut args1738 = Vec::new();
                    let mut kw1739 = Vec::new();
                    fun1740.call(args1738, kw1739)?
                }
                .attr("items")?;
                let mut args1735 = Vec::new();
                let mut kw1736 = Vec::new();
                fun1737.call(args1735, kw1736)?
            }
            .iter()?
            {
                let unpack1741 = unpack(item1720, 2)?;
                e.set("name", unpack1741[0].clone())?;
                e.set("row", unpack1741[1].clone())?;
                let assigned1721 = if {
                    let v1722 = e.get("row")?.attr("standoff")?;
                    let v1723 = Val::Float(0.0f64);
                    Val::Bool(compare("eq", v1722.clone(), v1723.clone())?.truthy()?)
                }
                .truthy()?
                {
                    binary(
                        "add",
                        e.get("core")?.attr("foam_cap_lid_height")?,
                        e.get("core")?.attr("cap_lid_clearance")?,
                    )?
                } else {
                    Val::Float(0.0f64)
                };
                e.set("lid_stack", assigned1721.clone())?;
                let assigned1724 = binary(
                    "sub",
                    binary(
                        "sub",
                        e.get("row")?.attr("screw")?,
                        e.get("row")?.attr("seat_min")?,
                    )?,
                    e.get("lid_stack")?,
                )?;
                e.set("maximum_reach", assigned1724.clone())?;
                let assigned1725 = {
                    let d = Val::dict(vec![]);
                    dict_extend(&d, {
                        let fun1728 = e.get("row")?.attr("_asdict")?;
                        let mut args1726 = Vec::new();
                        let mut kw1727 = Vec::new();
                        fun1728.call(args1726, kw1727)?
                    })?;
                    d.set(Val::Str("quantity".into()), {
                        let fun1731 = e.get("len")?;
                        let mut args1729 = Vec::new();
                        let mut kw1730 = Vec::new();
                        args1729.push(e.get("row")?.attr("points")?);
                        fun1731.call(args1729, kw1730)?
                    })?;
                    d.set(Val::Str("nominal_threaded_reach_mm".into()), {
                        let fun1734 = e.get("core")?.attr("deck_mount_reach")?;
                        let mut args1732 = Vec::new();
                        let mut kw1733 = Vec::new();
                        args1732.push(e.get("name")?);
                        fun1734.call(args1732, kw1733)?
                    })?;
                    d.set(
                        Val::Str("maximum_threaded_reach_mm".into()),
                        e.get("maximum_reach")?,
                    )?;
                    d.set(
                        Val::Str("minimum_tip_clearance_mm".into()),
                        binary(
                            "sub",
                            e.get("core")?.attr("deck_mount_bore_depth")?,
                            e.get("maximum_reach")?,
                        )?,
                    )?;
                    d
                };
                e.get("modules")?
                    .set(e.get("name")?, assigned1725.clone())?;
            }
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("frame".into()),
                    Val::Str("Top cap/lid native coordinates before installed half turn".into()),
                )?;
                d.set(
                    Val::Str("insert".into()),
                    Val::Str("ruthex RX-M3x5.7".into()),
                )?;
                d.set(Val::Str("lid_face_z_mm".into()), {
                    let fun1744 = e.get("lid_face_z")?;
                    let mut args1742 = Vec::new();
                    let mut kw1743 = Vec::new();
                    fun1744.call(args1742, kw1743)?
                })?;
                d.set(
                    Val::Str("column_diameter_mm".into()),
                    binary(
                        "mul",
                        Val::Float(2.0f64),
                        e.get("core")?.attr("deck_mount_boss_radius")?,
                    )?,
                )?;
                d.set(
                    Val::Str("pilot_diameter_mm".into()),
                    binary(
                        "mul",
                        Val::Float(2.0f64),
                        e.get("core")?.attr("deck_mount_bore_radius")?,
                    )?,
                )?;
                d.set(
                    Val::Str("pilot_depth_mm".into()),
                    e.get("core")?.attr("deck_mount_bore_depth")?,
                )?;
                d.set(
                    Val::Str("insert_length_mm".into()),
                    e.get("core")?.attr("deck_mount_insert_length")?,
                )?;
                d.set(Val::Str("modules".into()), e.get("modules")?)?;
                d.set(Val::Str("valve_supports".into()), {
                    let e = e.child();
                    let out1745 = Val::dict(vec![]);
                    for item1746 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("valve-v-b".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("name", item1746)?;
                        out1745.set(e.get("name")?, {
                            let d = Val::dict(vec![]);
                            d.set(
                                Val::Str("attachment".into()),
                                Val::Str("Integral upright socket wall on the top lid".into()),
                            )?;
                            d.set(Val::Str("native_to_cap".into()), {
                                let fun1749 = e.get("component_in_cap")?;
                                let mut args1747 = Vec::new();
                                let mut kw1748 = Vec::new();
                                args1747.push(e.get("name")?);
                                fun1749.call(args1747, kw1748)?
                            })?;
                            d.set(
                                Val::Str("socket_fit".into()),
                                Val::Str("Shared valve_seat V69".into()),
                            )?;
                            d
                        })?;
                    }
                    out1745
                })?;
                d.set(Val::Str("union_supports".into()), {
                    let fun1752 = e.get("union_support_datums")?;
                    let mut args1750 = Vec::new();
                    let mut kw1751 = Vec::new();
                    fun1752.call(args1750, kw1751)?
                })?;
                d.set(Val::Str("union_tie_allocation".into()), {
                    let e = e.child();
                    let out1753 = Val::dict(vec![]);
                    for item1754 in {
                        let fun1757 = {
                            let fun1760 = e.get("union_tie_routes")?;
                            let mut args1758 = Vec::new();
                            let mut kw1759 = Vec::new();
                            fun1760.call(args1758, kw1759)?
                        }
                        .attr("items")?;
                        let mut args1755 = Vec::new();
                        let mut kw1756 = Vec::new();
                        fun1757.call(args1755, kw1756)?
                    }
                    .iter()?
                    {
                        let unpack1761 = unpack(item1754, 2)?;
                        e.set("name", unpack1761[0].clone())?;
                        e.set("row", unpack1761[1].clone())?;
                        out1753.set(e.get("name")?, {
                            let e = e.child();
                            let out1762 = Val::dict(vec![]);
                            for item1763 in {
                                let mut s = Vec::new();
                                s.push(Val::Str("length_mm".into()));
                                s.push(Val::Str("stock".into()));
                                s.push(Val::Str("stock_length_mm".into()));
                                Val::tuple(s)
                            }
                            .iter()?
                            {
                                e.set("key", item1763)?;
                                out1762.set(e.get("key")?, e.get("row")?.get(e.get("key")?)?)?;
                            }
                            out1762
                        })?;
                    }
                    out1753
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // straight_cap_features
    e.set("straight_cap_features", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned1764 = {
                let fun1767 = e.get("importlib")?.attr("import_module")?;
                let mut args1765 = Vec::new();
                let mut kw1766 = Vec::new();
                args1765.push(Val::Str("_cold_core_interface".into()));
                fun1767.call(args1765, kw1766)?
            };
            e.set("core", assigned1764.clone())?;
            let assigned1768 = {
                let fun1771 = e.get("above_core")?.attr("specification")?;
                let mut args1769 = Vec::new();
                let mut kw1770 = Vec::new();
                fun1771.call(args1769, kw1770)?
            }
            .get(Val::Str("cap_guides_world_mm".into()))?
            .get(e.get("name")?)?;
            e.set("guide", assigned1768.clone())?;
            let assigned1772 = {
                let fun1775 = e.get("above_core")?.attr("cap_lid_pose")?;
                let mut args1773 = Vec::new();
                let mut kw1774 = Vec::new();
                fun1775.call(args1773, kw1774)?
            }
            .get(Val::Str("translation_mm".into()))?
            .get(Val::Int(2i64))?;
            e.set("lid_bottom", assigned1772.clone())?;
            let assigned1776 = binary(
                "sub",
                e.get("lid_bottom")?,
                binary(
                    "sub",
                    e.get("core")?.attr("foam_cap_height")?,
                    e.get("core")?.attr("head_pad_height")?,
                )?,
            )?;
            e.set("floor", assigned1776.clone())?;
            let assigned1777 = e.get("core")?.attr("cap_conduit_bore_radius")?;
            e.set("radius", assigned1777.clone())?;
            // cylinder
            e.set("cylinder", {
                let params = vec![
                    ("r".into(), None, false),
                    ("z0".into(), None, false),
                    ("z1".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let fun1780 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                        let mut args1778 = Vec::new();
                        let mut kw1779 = Vec::new();
                        args1778.push(e.get("r")?);
                        args1778.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                        args1778.push({
                            let fun1783 = e.get("cq")?.attr("Vector")?;
                            let mut args1781 = Vec::new();
                            let mut kw1782 = Vec::new();
                            args1781.extend(
                                e.get("guide")?
                                    .get(Val::Slice {
                                        start: None,
                                        stop: Some(Val::Int(2i64).integer()?),
                                        step: 1,
                                    })?
                                    .iter()?,
                            );
                            args1781.push(e.get("z0")?);
                            fun1783.call(args1781, kw1782)?
                        });
                        fun1780.call(args1778, kw1779)?
                    });
                    Ok(Val::None)
                })
            })?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("cup_add".into()), {
                    let fun1786 = e.get("cylinder")?;
                    let mut args1784 = Vec::new();
                    let mut kw1785 = Vec::new();
                    args1784.push(binary("add", e.get("radius")?, Val::Float(3.0f64))?);
                    args1784.push(binary(
                        "add",
                        e.get("floor")?,
                        e.get("core")?.attr("cap_shell_clearance")?,
                    )?);
                    args1784.push(binary(
                        "sub",
                        e.get("lid_bottom")?,
                        e.get("core")?.attr("cap_lid_clearance")?,
                    )?);
                    fun1786.call(args1784, kw1785)?
                })?;
                d.set(Val::Str("lid_add".into()), {
                    let fun1789 = e.get("cylinder")?;
                    let mut args1787 = Vec::new();
                    let mut kw1788 = Vec::new();
                    args1787.push(binary("add", e.get("radius")?, Val::Float(3.0f64))?);
                    args1787.push(e.get("lid_bottom")?);
                    args1787.push(e.get("guide")?.get(Val::Int(2i64))?);
                    fun1789.call(args1787, kw1788)?
                })?;
                d.set(Val::Str("cut".into()), {
                    let fun1792 = e.get("cylinder")?;
                    let mut args1790 = Vec::new();
                    let mut kw1791 = Vec::new();
                    args1790.push(e.get("radius")?);
                    args1790.push(binary("sub", e.get("floor")?, Val::Float(1.0f64))?);
                    args1790.push(binary(
                        "add",
                        e.get("guide")?.get(Val::Int(2i64))?,
                        Val::Float(1.0f64),
                    )?);
                    fun1792.call(args1790, kw1791)?
                })?;
                d.set(Val::Str("wall_mm".into()), Val::Float(3.0f64))?;
                d.set(Val::Str("horizontal_floor_backing_mm".into()), Val::None)?;
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
