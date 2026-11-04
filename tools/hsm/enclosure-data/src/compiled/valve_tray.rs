//! A VALVE TRAY IS A PLATE OF VALVE SEATS, and it is a wall of the enclosure.
//!
//! One `valve_seat` per valve — four blind sockets a corner post presses into — SUNK into a flat
//! plate that runs from side wall to side wall of `enclosure-front-top`. The plate is one socket
//! and one wall thick, so it is the boss: nothing stands off it, the valve lands on its face, and
//! the only thing it opens for is each valve's own port, on a channel out both ends. It is
//! that piece's own material, fused in the way the ASSE anchor, the flow-meter anchors and every
//! tube rib are: `enclosure._valve_trays` stands one per deck, off the stations
//! `enclosure_assembly.valve_tray_stations` reads off the placed valves. NO TRAY SHIPS AS A PART,
//! nothing bolts a valve to one and nothing is bonded — the posts in their sockets are the whole of
//! the retention, the same bargain the cold core's cap lid strikes under its three valves
//! (`_cold_core_interface.cap_cradles`).
//!
//!     ACROSS  wall to wall. The plate is the piece, so it takes no slip and ends on the two
//!             interior faces
//!     ALONG   the seats' own reach off their valves' centres, and one `MARGIN` past that. The
//!             plate ends where the last boss does; the valves' collets and the tube butted into
//!             them hang past it
//!
//! This module states the tray's own figures and draws one in its own frame; `enclosure` turns it
//! onto a deck and fuses it. The frame is `valve_seat`'s carried onto a plate:
//!   Z = out of the valve-side face, the direction a valve's own +Z runs. `z = 0` IS THAT FACE, so
//!       the plate spans z = −`THICK` to 0 and every seat is sunk from zero. That face is the plane
//!       the valve's own round body boss lands on, so a valve stands ON the plate and not on four
//!       boss tops — `SEAT` is negative here, and that is the whole of the difference.
//!   X = across the plate. Y = along it. Origin is the plate's centre in both.
//!
//! The rectangular socket pattern follows the valve: X across the plate and the port axis on Y.
//!
//! In the piece's own print orientation the plate stands vertical, wall to wall, and NOTHING
//! stands off it: the port channel is a notch that runs up the plate's own section, while
//! `enclosure._valve_socket_cutters` carries each horizontal socket's complete round post room into
//! a tangent teardrop roof. There is no unsupported crown and no support in the thirty-two sockets
//! to pick out — which is what the thickness and roof buy, a boss on a standing plate being a
//! cylinder cantilevered into air.
//!
//! Run:
//!     tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-tray/valve_tray.py
//!     tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-tray/valve_tray.py selftest
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun8 = e.get("Path")?;
                    let mut args6 = Vec::new();
                    let mut kw7 = Vec::new();
                    args6.push(e.get("__file__")?);
                    fun8.call(args6, kw7)?
                }
            }
            .attr("resolve")?;
            let mut args3 = Vec::new();
            let mut kw4 = Vec::new();
            fun5.call(args3, kw4)?
        }
    };
    e.set("_here", assigned2.clone())?;
    let assigned9 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
            line!(),
        );
        {
            let fun12 = e.get("next")?;
            let mut args10 = Vec::new();
            let mut kw11 = Vec::new();
            args10.push({
                let e = e.child();
                let out13 = Val::list(vec![]);
                for item14 in e.get("_here")?.attr("parents")?.iter()? {
                    e.set("p", item14)?;
                    if {
                        let v15 = e.get("p")?.attr("name")?;
                        let v16 = Val::Str("hardware".into());
                        Val::Bool(compare("eq", v15.clone(), v16.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out13.attr("append")?.call(vec![e.get("p")?], vec![])?;
                    }
                }
                out13
            });
            fun12.call(args10, kw11)?
        }
    };
    e.set("_hw", assigned9.clone())?;
    for item17 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            e.get("_hw")?,
            Val::Str("scripts".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
            Val::Str("valve-seat".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("reference".into()))?,
            Val::Str("beduan-solenoid".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_p", item17)?;
        {
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                line!(),
            );
            {
                let fun20 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args18 = Vec::new();
                let mut kw19 = Vec::new();
                args18.push(Val::Int(0i64));
                args18.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                        line!(),
                    );
                    {
                        let fun23 = e.get("str")?;
                        let mut args21 = Vec::new();
                        let mut kw22 = Vec::new();
                        args21.push(e.get("_p")?);
                        fun23.call(args21, kw22)?
                    }
                });
                fun20.call(args18, kw19)?
            }
        };
    }
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
            line!(),
        );
        {
            let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args24 = Vec::new();
            let mut kw25 = Vec::new();
            args24.push(Val::Int(0i64));
            args24.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun29=e.get("str")?;let mut args27=Vec::new();let mut kw28=Vec::new();args27.push(binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun32=e.get("next")?;let mut args30=Vec::new();let mut kw31=Vec::new();args30.push({let e=e.child();let out33=Val::list(vec![]);for item34 in e.get("_here")?.attr("parents")?.iter()? {e.set("p",item34)?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun37=binary("truediv",binary("truediv",e.get("p")?,Val::Str("tools".into()))?,Val::Str("docgen".into()))?.attr("is_dir")?;let mut args35=Vec::new();let mut kw36=Vec::new();fun37.call(args35,kw36)?}}.truthy()? {out33.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out33});fun32.call(args30,kw31)?}},Val::Str("tools".into()))?);fun29.call(args27,kw28)?}});
            fun26.call(args24, kw25)?
        }
    };
    e.set("_valve", rt.import_module("beduan_solenoid")?)?;
    e.set("_seat", rt.import_module("valve_seat")?)?;
    let mod38 = rt.import_module("docgen")?;
    e.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    // __getattr__
    e.set("__getattr__", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v39 = e.get("name")?;
                let v40 = Val::Str("cq".into());
                Val::Bool(compare("eq", v39.clone(), v40.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.set("cadquery", rt.import_module("cadquery")?)?;
                return Ok(e.get("cadquery")?);
            }
            anyhow::bail!(
                "{}",
                val_string({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                        line!(),
                    );
                    {
                        let fun43 = e.get("AttributeError")?;
                        let mut args41 = Vec::new();
                        let mut kw42 = Vec::new();
                        args41.push({
                            let mut str44 = String::new();
                            str44.push_str("module ");
                            str44.push_str(&format(
                                &builtin_call("repr", vec![e.get("__name__")?], vec![])?,
                                &String::new(),
                            )?);
                            str44.push_str(" has no attribute ");
                            str44.push_str(&format(
                                &builtin_call("repr", vec![e.get("name")?], vec![])?,
                                &String::new(),
                            )?);
                            Val::Str(str44)
                        });
                        fun43.call(args41, kw42)?
                    }
                })?
            );
            Ok(Val::None)
        })
    })?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
            line!(),
        );
        {
            let fun47 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args45 = Vec::new();
            let mut kw46 = Vec::new();
            args45.push(Val::Int(0i64));
            args45.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun50 = e.get("str")?;
                    let mut args48 = Vec::new();
                    let mut kw49 = Vec::new();
                    args48.push(binary(
                        "truediv",
                        e.get("_hw")?,
                        Val::Str("printed-parts/enclosure/enclosure".into()),
                    )?);
                    fun50.call(args48, kw49)?
                }
            });
            fun47.call(args45, kw46)?
        }
    };
    let mod51 = rt.import_module("_enclosure_data")?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    // _source
    e.set("_source", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned52 = {
                let e = e.child();
                let out53 = Val::dict(vec![]);
                for item54 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("wall".into()));
                    s.push(Val::Str("socket_floor_z".into()));
                    s.push(Val::Str("socket_radius".into()));
                    s.push(Val::Str("seat_half_y".into()));
                    s.push(Val::Str("seat_top_z".into()));
                    s.push(Val::Str("port_air".into()));
                    s.push(Val::Str("corner_inset_x".into()));
                    s.push(Val::Str("corner_inset_y".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("name", item54)?;
                    out53.set(e.get("name")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun57 = e.get("getattr")?;
                            let mut args55 = Vec::new();
                            let mut kw56 = Vec::new();
                            args55.push(e.get("_seat")?);
                            args55.push(e.get("name")?);
                            fun57.call(args55, kw56)?
                        }
                    })?;
                }
                out53
            };
            e.set("values", assigned52.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun60 = e.get("values")?.attr("update")?;
                    let mut args58 = Vec::new();
                    let mut kw59 = Vec::new();
                    kw59.push(("socket_depth".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun63 = e.get("_seat")?.attr("socket_depth")?;
                            let mut args61 = Vec::new();
                            let mut kw62 = Vec::new();
                            fun63.call(args61, kw62)?
                        }
                    }));
                    kw59.push((
                        "port_center_z".into(),
                        e.get("_valve")?.attr("port_center_z")?,
                    ));
                    kw59.push(("port_radius".into(), e.get("_valve")?.attr("port_radius")?));
                    fun60.call(args58, kw59)?
                }
            };
            return Ok(e.get("values")?);
            Ok(Val::None)
        })
    })?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
            line!(),
        );
        {
            let fun66 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun69 = e.get("globals")?;
                    let mut args67 = Vec::new();
                    let mut kw68 = Vec::new();
                    fun69.call(args67, kw68)?
                }
            }
            .attr("update")?;
            let mut args64 = Vec::new();
            let mut kw65 = Vec::new();
            args64.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun72 = e.get("_read")?;
                    let mut args70 = Vec::new();
                    let mut kw71 = Vec::new();
                    args70.push(Val::Str("valve-tray-defaults".into()));
                    kw71.push(("source".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun75 = e.get("_source")?;
                            let mut args73 = Vec::new();
                            let mut kw74 = Vec::new();
                            fun75.call(args73, kw74)?
                        }
                    }));
                    fun72.call(args70, kw71)?
                }
            });
            fun66.call(args64, kw65)?
        }
    };
    // _data
    e.set("_data", {
        let params = vec![("op".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, Some("values"))?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun78 = e.get("_read")?;
                    let mut args76 = Vec::new();
                    let mut kw77 = Vec::new();
                    args76.push(binary("add", Val::Str("valve-tray-".into()), e.get("op")?)?);
                    kw77.push(("source".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun81 = e.get("_source")?;
                            let mut args79 = Vec::new();
                            let mut kw80 = Vec::new();
                            fun81.call(args79, kw80)?
                        }
                    }));
                    kw77.push(("stock".into(), {
                        let e = e.child();
                        let out82 = Val::dict(vec![]);
                        for item83 in {
                            let mut s = Vec::new();
                            s.push(Val::Str("THICK".into()));
                            s.push(Val::Str("MARGIN".into()));
                            s.push(Val::Str("SEAT".into()));
                            s.push(Val::Str("PORT_SLIP".into()));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("name", item83)?;
                            out82.set(
                                e.get("name")?,
                                {
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                                        line!(),
                                    );
                                    {
                                        let fun86 = e.get("globals")?;
                                        let mut args84 = Vec::new();
                                        let mut kw85 = Vec::new();
                                        fun86.call(args84, kw85)?
                                    }
                                }
                                .get(e.get("name")?)?,
                            )?;
                        }
                        out82
                    }));
                    kw77.extend(keyword_items(e.get("values")?)?);
                    fun78.call(args76, kw77)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // reach
    e.set("reach", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun89 = e.get("_data")?;
                    let mut args87 = Vec::new();
                    let mut kw88 = Vec::new();
                    args87.push(Val::Str("reach".into()));
                    fun89.call(args87, kw88)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // height
    e.set("height", {
        let params = vec![(
            "seats".into(),
            Some({
                let mut s = Vec::new();
                Val::tuple(s)
            }),
            false,
        )];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun92 = e.get("_data")?;
                    let mut args90 = Vec::new();
                    let mut kw91 = Vec::new();
                    args90.push(Val::Str("height".into()));
                    kw91.push(("seats".into(), e.get("seats")?));
                    fun92.call(args90, kw91)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // wall_root_floors
    e.set("wall_root_floors", {
        let params = vec![("seats".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun95 = e.get("tuple")?;
                    let mut args93 = Vec::new();
                    let mut kw94 = Vec::new();
                    args93.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun98 = e.get("_data")?;
                            let mut args96 = Vec::new();
                            let mut kw97 = Vec::new();
                            args96.push(Val::Str("wall-root-floors".into()));
                            kw97.push(("seats".into(), e.get("seats")?));
                            fun98.call(args96, kw97)?
                        }
                    });
                    fun95.call(args93, kw94)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // port_drop
    e.set("port_drop", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun101 = e.get("_data")?;
                    let mut args99 = Vec::new();
                    let mut kw100 = Vec::new();
                    args99.push(Val::Str("port-drop".into()));
                    fun101.call(args99, kw100)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // port_channel_depth
    e.set("port_channel_depth", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun104 = e.get("_data")?;
                    let mut args102 = Vec::new();
                    let mut kw103 = Vec::new();
                    args102.push(Val::Str("channel-depth".into()));
                    fun104.call(args102, kw103)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // extrusion
    e.set("extrusion", {
        let params = vec![("width".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("width")?);
            Ok(Val::None)
        })
    })?;
    // web
    e.set("web", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned105 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun108 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun111 = e.get("_seat")?.attr("build_sockets")?;
                            let mut args109 = Vec::new();
                            let mut kw110 = Vec::new();
                            fun111.call(args109, kw110)?
                        }
                    }
                    .attr("val")?;
                    let mut args106 = Vec::new();
                    let mut kw107 = Vec::new();
                    fun108.call(args106, kw107)?
                }
            };
            e.set("sockets", assigned105.clone())?;
            let assigned112 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun115 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun118 = e.get("build_port_channel")?;
                            let mut args116 = Vec::new();
                            let mut kw117 = Vec::new();
                            args116.push(binary(
                                "add",
                                {
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                                        line!(),
                                    );
                                    {
                                        let fun121 = e.get("height")?;
                                        let mut args119 = Vec::new();
                                        let mut kw120 = Vec::new();
                                        fun121.call(args119, kw120)?
                                    }
                                },
                                Val::Float(2.0f64),
                            )?);
                            fun118.call(args116, kw117)?
                        }
                    }
                    .attr("val")?;
                    let mut args113 = Vec::new();
                    let mut kw114 = Vec::new();
                    fun115.call(args113, kw114)?
                }
            };
            e.set("channel", assigned112.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun124 = e.get("sockets")?.attr("distance")?;
                    let mut args122 = Vec::new();
                    let mut kw123 = Vec::new();
                    args122.push(e.get("channel")?);
                    fun124.call(args122, kw123)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // grip
    e.set("grip", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun127 = e.get("_data")?;
                    let mut args125 = Vec::new();
                    let mut kw126 = Vec::new();
                    args125.push(Val::Str("grip".into()));
                    fun127.call(args125, kw126)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // build_port_channel
    e.set("build_port_channel", {
        let params = vec![("length".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun130 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun133 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                                    line!(),
                                );
                                {
                                    let fun136 = {
                                        let _site = rt.source_at(
                                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                                            line!(),
                                        );
                                        {
                                            let fun139 = e.get("cq")?.attr("Workplane")?;
                                            let mut args137 = Vec::new();
                                            let mut kw138 = Vec::new();
                                            args137.push(Val::Str("XZ".into()));
                                            fun139.call(args137, kw138)?
                                        }
                                    }
                                    .attr("center")?;
                                    let mut args134 = Vec::new();
                                    let mut kw135 = Vec::new();
                                    args134.push(Val::Float(0.0f64));
                                    args134.push(e.get("_valve")?.attr("port_center_z")?);
                                    fun136.call(args134, kw135)?
                                }
                            }
                            .attr("circle")?;
                            let mut args131 = Vec::new();
                            let mut kw132 = Vec::new();
                            args131.push(binary(
                                "add",
                                e.get("_valve")?.attr("port_radius")?,
                                e.get("PORT_SLIP")?,
                            )?);
                            fun133.call(args131, kw132)?
                        }
                    }
                    .attr("extrude")?;
                    let mut args128 = Vec::new();
                    let mut kw129 = Vec::new();
                    args128.push(binary("truediv", e.get("length")?, Val::Float(2.0f64))?);
                    kw129.push(("both".into(), Val::Bool(true)));
                    fun130.call(args128, kw129)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // build_body_clearance
    e.set("build_body_clearance",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("cq",rt.import_module("cadquery")?)?;
let assigned140=e.get("PORT_SLIP")?;e.set("slip",assigned140.clone())?;
// cylinder
e.set("cylinder",{let params=vec![("radius".into(),None,false),("z0".into(),None,false),("z1".into(),None,false),("x".into(),Some(Val::Float(0.0f64)),false),("y".into(),Some(Val::Float(0.0f64)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun143={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun146={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun149={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun152={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun155=e.get("cq")?.attr("Workplane")?;let mut args153=Vec::new();let mut kw154=Vec::new();args153.push(Val::Str("XY".into()));fun155.call(args153,kw154)?}}.attr("workplane")?;let mut args150=Vec::new();let mut kw151=Vec::new();kw151.push(("offset".into(),e.get("z0")?));fun152.call(args150,kw151)?}}.attr("center")?;let mut args147=Vec::new();let mut kw148=Vec::new();args147.push(e.get("x")?);args147.push(e.get("y")?);fun149.call(args147,kw148)?}}.attr("circle")?;let mut args144=Vec::new();let mut kw145=Vec::new();args144.push(e.get("radius")?);fun146.call(args144,kw145)?}}.attr("extrude")?;let mut args141=Vec::new();let mut kw142=Vec::new();args141.push(binary("sub",e.get("z1")?,e.get("z0")?)?);fun143.call(args141,kw142)?}});
Ok(Val::None)})})?;
let assigned156={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun159=e.get("cylinder")?;let mut args157=Vec::new();let mut kw158=Vec::new();args157.push(binary("add",e.get("_valve")?.attr("bearing_radius")?,e.get("slip")?)?);args157.push(e.get("_seat")?.attr("seat_top_z")?);args157.push(binary("add",e.get("_valve")?.attr("bearing_z_range")?.get(Val::Int(1i64))?,e.get("slip")?)?);fun159.call(args157,kw158)?}};e.set("body",assigned156.clone())?;
let assigned160={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun163=e.get("body")?.attr("union")?;let mut args161=Vec::new();let mut kw162=Vec::new();args161.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun166=e.get("cylinder")?;let mut args164=Vec::new();let mut kw165=Vec::new();args164.push(binary("add",e.get("_valve")?.attr("body_radius")?,e.get("slip")?)?);args164.push(binary("sub",e.get("_valve")?.attr("body_main_z_range")?.get(Val::Int(0i64))?,e.get("slip")?)?);args164.push(binary("add",e.get("_valve")?.attr("body_main_z_range")?.get(Val::Int(1i64))?,e.get("slip")?)?);fun166.call(args164,kw165)?}});fun163.call(args161,kw162)?}};e.set("body",assigned160.clone())?;
for item167 in {let mut s=Vec::new();s.push(unary("neg",Val::Float(1.0f64))?);s.push(Val::Float(1.0f64));Val::tuple(s)}.iter()? {
e.set("sx",item167)?;for item168 in {let mut s=Vec::new();s.push(unary("neg",Val::Float(1.0f64))?);s.push(Val::Float(1.0f64));Val::tuple(s)}.iter()? {
e.set("sy",item168)?;let assigned169={let mut s=Vec::new();s.push(binary("mul",e.get("sx")?,e.get("_seat")?.attr("corner_inset_x")?)?);s.push(binary("mul",e.get("sy")?,e.get("_seat")?.attr("corner_inset_y")?)?);Val::tuple(s)};let unpack170=unpack(assigned169.clone(),2)?;e.set("x",unpack170[0].clone())?;e.set("y",unpack170[1].clone())?;
let assigned171={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun174=e.get("body")?.attr("union")?;let mut args172=Vec::new();let mut kw173=Vec::new();args172.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun177=e.get("cylinder")?;let mut args175=Vec::new();let mut kw176=Vec::new();args175.push(binary("add",e.get("_valve")?.attr("corner_boss_radius")?,e.get("slip")?)?);args175.push(e.get("_seat")?.attr("seat_top_z")?);args175.push(binary("add",e.get("_valve")?.attr("post_shoulder_z")?,e.get("slip")?)?);args175.push(e.get("x")?);args175.push(e.get("y")?);fun177.call(args175,kw176)?}});fun174.call(args172,kw173)?}};e.set("body",assigned171.clone())?;
let assigned178={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun181=e.get("body")?.attr("union")?;let mut args179=Vec::new();let mut kw180=Vec::new();args179.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun184=e.get("cylinder")?;let mut args182=Vec::new();let mut kw183=Vec::new();args182.push(binary("add",e.get("_valve")?.attr("upper_corner_radius")?,e.get("slip")?)?);args182.push(binary("sub",e.get("_valve")?.attr("post_shoulder_z")?,e.get("slip")?)?);args182.push(binary("add",e.get("_valve")?.attr("body_top_z")?,e.get("slip")?)?);args182.push(e.get("x")?);args182.push(e.get("y")?);fun184.call(args182,kw183)?}});fun181.call(args179,kw180)?}};e.set("body",assigned178.clone())?;
}
}
let assigned185={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun188={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun191={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun194={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun197={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun200={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun203=e.get("cq")?.attr("Workplane")?;let mut args201=Vec::new();let mut kw202=Vec::new();args201.push(Val::Str("XY".into()));fun203.call(args201,kw202)?}}.attr("workplane")?;let mut args198=Vec::new();let mut kw199=Vec::new();kw199.push(("offset".into(),binary("sub",e.get("_valve")?.attr("top_box_z_range")?.get(Val::Int(0i64))?,e.get("slip")?)?));fun200.call(args198,kw199)?}}.attr("rect")?;let mut args195=Vec::new();let mut kw196=Vec::new();args195.push(binary("add",e.get("_valve")?.attr("cap_width_x")?,binary("mul",Val::Float(2.0f64),e.get("slip")?)?)?);args195.push(binary("add",e.get("_valve")?.attr("cap_depth_y")?,binary("mul",Val::Float(2.0f64),e.get("slip")?)?)?);fun197.call(args195,kw196)?}}.attr("extrude")?;let mut args192=Vec::new();let mut kw193=Vec::new();args192.push(binary("add",e.get("_valve")?.attr("top_box_height")?,binary("mul",Val::Float(2.0f64),e.get("slip")?)?)?);fun194.call(args192,kw193)?}}.attr("edges")?;let mut args189=Vec::new();let mut kw190=Vec::new();args189.push(Val::Str("|Z".into()));fun191.call(args189,kw190)?}}.attr("fillet")?;let mut args186=Vec::new();let mut kw187=Vec::new();args186.push(binary("add",e.get("_valve")?.attr("cap_corner_radius")?,e.get("slip")?)?);fun188.call(args186,kw187)?}};e.set("cap",assigned185.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun206=e.get("body")?.attr("union")?;let mut args204=Vec::new();let mut kw205=Vec::new();args204.push(e.get("cap")?);fun206.call(args204,kw205)?}});
Ok(Val::None)})})?;
    // build_valve_tray
    e.set("build_valve_tray",{let params=vec![("width".into(),None,false),("seats".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("cq",rt.import_module("cadquery")?)?;
if unary("not",e.get("seats")?)?.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun209=e.get("ValueError")?;let mut args207=Vec::new();let mut kw208=Vec::new();args207.push(Val::Str("a valve tray with no seats is a plate, and this machine prints none".into()));fun209.call(args207,kw208)?}})?);
}
let assigned210={let e=e.child();let out211=Val::list(vec![]);for item212 in e.get("seats")?.iter()? {let unpack213=unpack(item212,2)?;e.set("_x",unpack213[0].clone())?;e.set("y",unpack213[1].clone())?;out211.attr("append")?.call(vec![e.get("y")?],vec![])?;}out211};e.set("ys",assigned210.clone())?;
let assigned214=binary("truediv",binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun217=e.get("min")?;let mut args215=Vec::new();let mut kw216=Vec::new();args215.push(e.get("ys")?);fun217.call(args215,kw216)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun220=e.get("max")?;let mut args218=Vec::new();let mut kw219=Vec::new();args218.push(e.get("ys")?);fun220.call(args218,kw219)?}})?,Val::Float(2.0f64))?;e.set("mid_y",assigned214.clone())?;
let assigned221={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun224=e.get("height")?;let mut args222=Vec::new();let mut kw223=Vec::new();args222.push(e.get("seats")?);fun224.call(args222,kw223)?}};e.set("tray_height",assigned221.clone())?;
let assigned225={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun228={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun231={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun234={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun237=e.get("cq")?.attr("Workplane")?;let mut args235=Vec::new();let mut kw236=Vec::new();args235.push(Val::Str("XY".into()));fun237.call(args235,kw236)?}}.attr("workplane")?;let mut args232=Vec::new();let mut kw233=Vec::new();kw233.push(("offset".into(),unary("neg",e.get("THICK")?)?));fun234.call(args232,kw233)?}}.attr("box")?;let mut args229=Vec::new();let mut kw230=Vec::new();args229.push(e.get("width")?);args229.push(e.get("tray_height")?);args229.push(e.get("THICK")?);kw230.push(("centered".into(),{let mut s=Vec::new();s.push(Val::Bool(true));s.push(Val::Bool(true));s.push(Val::Bool(false));Val::tuple(s)}));fun231.call(args229,kw230)?}}.attr("translate")?;let mut args226=Vec::new();let mut kw227=Vec::new();args226.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(e.get("mid_y")?);s.push(Val::Float(0.0f64));Val::tuple(s)});fun228.call(args226,kw227)?}};e.set("tray",assigned225.clone())?;
for item238 in e.get("seats")?.iter()? {
let unpack239=unpack(item238,2)?;e.set("x",unpack239[0].clone())?;e.set("y",unpack239[1].clone())?;let assigned240={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun243=e.get("tray")?.attr("cut")?;let mut args241=Vec::new();let mut kw242=Vec::new();args241.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun246={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun249=e.get("_seat")?.attr("build_sockets")?;let mut args247=Vec::new();let mut kw248=Vec::new();fun249.call(args247,kw248)?}}.attr("translate")?;let mut args244=Vec::new();let mut kw245=Vec::new();args244.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);s.push(e.get("SEAT")?);Val::tuple(s)});fun246.call(args244,kw245)?}});fun243.call(args241,kw242)?}};e.set("tray",assigned240.clone())?;
let assigned250=binary("add",binary("add",e.get("tray_height")?,binary("mul",Val::Float(2.0f64),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun253=e.get("abs")?;let mut args251=Vec::new();let mut kw252=Vec::new();args251.push(binary("sub",e.get("y")?,e.get("mid_y")?)?);fun253.call(args251,kw252)?}})?)?,Val::Float(2.0f64))?;e.set("channel_length",assigned250.clone())?;
let assigned254={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun257=e.get("tray")?.attr("cut")?;let mut args255=Vec::new();let mut kw256=Vec::new();args255.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun260={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun263=e.get("build_port_channel")?;let mut args261=Vec::new();let mut kw262=Vec::new();args261.push(e.get("channel_length")?);fun263.call(args261,kw262)?}}.attr("translate")?;let mut args258=Vec::new();let mut kw259=Vec::new();args258.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);s.push(e.get("SEAT")?);Val::tuple(s)});fun260.call(args258,kw259)?}});fun257.call(args255,kw256)?}};e.set("tray",assigned254.clone())?;
}
return Ok(e.get("tray")?);
Ok(Val::None)})})?;
    // _segment_area
    e.set("_segment_area", {
        let params = vec![("radius".into(), None, false), ("over".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun266 = e.get("_data")?;
                    let mut args264 = Vec::new();
                    let mut kw265 = Vec::new();
                    args264.push(Val::Str("segment".into()));
                    kw265.push(("radius".into(), e.get("radius")?));
                    kw265.push(("over".into(), e.get("over")?));
                    fun266.call(args264, kw265)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // tray_volume
    e.set("tray_volume", {
        let params = vec![("width".into(), None, false), ("seats".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun269 = e.get("_data")?;
                    let mut args267 = Vec::new();
                    let mut kw268 = Vec::new();
                    args267.push(Val::Str("volume".into()));
                    kw268.push(("width".into(), e.get("width")?));
                    kw268.push(("seats".into(), e.get("seats")?));
                    fun269.call(args267, kw268)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // channel_floor
    e.set("channel_floor", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun272 = e.get("_data")?;
                    let mut args270 = Vec::new();
                    let mut kw271 = Vec::new();
                    args270.push(Val::Str("channel-floor".into()));
                    fun272.call(args270, kw271)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // depth
    e.set("depth", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("THICK")?);
            Ok(Val::None)
        })
    })?;
    // selftest
    e.set("selftest",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned273={let mut s=Vec::new();Val::list(s)};e.set("fails",assigned273.clone())?;
if {let v277=binary("sub",e.get("THICK")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun276=e.get("_seat")?.attr("socket_depth")?;let mut args274=Vec::new();let mut kw275=Vec::new();fun276.call(args274,kw275)?}})?;let v278=binary("sub",e.get("_seat")?.attr("wall")?,Val::Float(1e-09f64))?;Val::Bool(compare("lt",v277.clone(),v278.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun281=e.get("fails")?.attr("append")?;let mut args279=Vec::new();let mut kw280=Vec::new();args279.push({let mut str282=String::new();str282.push_str("a plate ");str282.push_str(&format(&e.get("THICK")?,&val_string({let mut str283=String::new();str283.push_str("g");Val::Str(str283)})?)?);str282.push_str(" mm thick keeps ");str282.push_str(&format(&binary("sub",e.get("THICK")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun286=e.get("_seat")?.attr("socket_depth")?;let mut args284=Vec::new();let mut kw285=Vec::new();fun286.call(args284,kw285)?}})?,&val_string({let mut str287=String::new();str287.push_str(".3f");Val::Str(str287)})?)?);str282.push_str(" mm behind a socket ");str282.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun290=e.get("_seat")?.attr("socket_depth")?;let mut args288=Vec::new();let mut kw289=Vec::new();fun290.call(args288,kw289)?}},&val_string({let mut str291=String::new();str291.push_str("g");Val::Str(str291)})?)?);str282.push_str(" deep, under the ");str282.push_str(&format(&e.get("_seat")?.attr("wall")?,&val_string({let mut str292=String::new();str292.push_str("g");Val::Str(str292)})?)?);str282.push_str(" mm wall every socket in this machine is floored on");Val::Str(str282)});fun281.call(args279,kw280)?}};
}
if {let v296={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun295=e.get("channel_floor")?;let mut args293=Vec::new();let mut kw294=Vec::new();fun295.call(args293,kw294)?}};let v297=binary("sub",e.get("_seat")?.attr("wall")?,Val::Float(1e-09f64))?;Val::Bool(compare("le",v296.clone(),v297.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun300=e.get("fails")?.attr("append")?;let mut args298=Vec::new();let mut kw299=Vec::new();args298.push({let mut str301=String::new();str301.push_str("a port channel ");str301.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun304=e.get("port_channel_depth")?;let mut args302=Vec::new();let mut kw303=Vec::new();fun304.call(args302,kw303)?}},&val_string({let mut str305=String::new();str305.push_str(".3f");Val::Str(str305)})?)?);str301.push_str(" mm deep leaves ");str301.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun308=e.get("channel_floor")?;let mut args306=Vec::new();let mut kw307=Vec::new();fun308.call(args306,kw307)?}},&val_string({let mut str309=String::new();str309.push_str(".3f");Val::Str(str309)})?)?);str301.push_str(" mm of plate under it, under one ");str301.push_str(&format(&e.get("_seat")?.attr("wall")?,&val_string({let mut str310=String::new();str310.push_str("g");Val::Str(str310)})?)?);str301.push_str(" mm wall — the channel is what sets the plate's thinnest section and it has outrun the sockets");Val::Str(str301)});fun300.call(args298,kw299)?}};
}
if {let v314={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun313=e.get("port_drop")?;let mut args311=Vec::new();let mut kw312=Vec::new();fun313.call(args311,kw312)?}};let v315=Val::Float(0.0f64);Val::Bool(compare("le",v314.clone(),v315.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun318=e.get("fails")?.attr("append")?;let mut args316=Vec::new();let mut kw317=Vec::new();args316.push({let mut str319=String::new();str319.push_str("the valve's port stands ");str319.push_str(&format(&unary("neg",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun322=e.get("port_drop")?;let mut args320=Vec::new();let mut kw321=Vec::new();fun322.call(args320,kw321)?}})?,&val_string({let mut str323=String::new();str323.push_str(".3f");Val::Str(str323)})?)?);str319.push_str(" mm CLEAR of the face it lands on, so the plate needs no channel and this one cuts a groove for air");Val::Str(str319)});fun318.call(args316,kw317)?}};
}
let assigned324={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun327=e.get("math")?.attr("sqrt")?;let mut args325=Vec::new();let mut kw326=Vec::new();args325.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun330=e.get("max")?;let mut args328=Vec::new();let mut kw329=Vec::new();args328.push(binary("sub",binary("pow",binary("add",e.get("_valve")?.attr("port_radius")?,e.get("PORT_SLIP")?)?,Val::Int(2i64))?,binary("pow",binary("sub",e.get("_valve")?.attr("port_center_z")?,e.get("_seat")?.attr("seat_top_z")?)?,Val::Int(2i64))?)?);args328.push(Val::Float(0.0f64));fun330.call(args328,kw329)?}});fun327.call(args325,kw326)?}};e.set("open_half",assigned324.clone())?;
if {let v331=e.get("open_half")?;let v332=binary("sub",binary("sub",e.get("_seat")?.attr("corner_inset_x")?,e.get("_seat")?.attr("socket_radius")?)?,Val::Float(1e-09f64))?;Val::Bool(compare("ge",v331.clone(),v332.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun335=e.get("fails")?.attr("append")?;let mut args333=Vec::new();let mut kw334=Vec::new();args333.push({let mut str336=String::new();str336.push_str("the port channel opens ");str336.push_str(&format(&e.get("open_half")?,&val_string({let mut str337=String::new();str337.push_str(".3f");Val::Str(str337)})?)?);str336.push_str(" mm either side of the valve's centre and the nearest socket wall stands at ");str336.push_str(&format(&binary("sub",e.get("_seat")?.attr("corner_inset_x")?,e.get("_seat")?.attr("socket_radius")?)?,&val_string({let mut str338=String::new();str338.push_str(".3f");Val::Str(str338)})?)?);str336.push_str(" — the channel is in the socket, and a socket open down its side holds no post");Val::Str(str336)});fun335.call(args333,kw334)?}};
}
let assigned339=binary("add",binary("mul",Val::Float(2.0f64),e.get("_seat")?.attr("seat_half_x")?)?,Val::Float(1.0f64))?;e.set("pitch",assigned339.clone())?;
let assigned340={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun343=e.get("tuple")?;let mut args341=Vec::new();let mut kw342=Vec::new();args341.push({let e=e.child();let out344=Val::list(vec![]);for item345 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(unary("neg",Val::Float(1.5f64))?);s.push(unary("neg",Val::Float(3.0f64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(unary("neg",Val::Float(0.5f64))?);s.push(Val::Float(3.0f64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.5f64));s.push(unary("neg",Val::Float(3.0f64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(1.5f64));s.push(Val::Float(3.0f64));Val::tuple(s)});Val::tuple(s)}.iter()? {let unpack346=unpack(item345,2)?;e.set("i",unpack346[0].clone())?;e.set("y",unpack346[1].clone())?;out344.attr("append")?.call(vec![{let mut s=Vec::new();s.push(binary("mul",e.get("i")?,e.get("pitch")?)?);s.push(e.get("y")?);Val::tuple(s)}],vec![])?;}out344});fun343.call(args341,kw342)?}};e.set("seats",assigned340.clone())?;
let assigned347=binary("mul",e.get("pitch")?,Val::Float(4.0f64))?;e.set("width",assigned347.clone())?;
let attempt348=(||->Result<Flow>{let assigned350={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun353={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun356=e.get("build_valve_tray")?;let mut args354=Vec::new();let mut kw355=Vec::new();args354.push(e.get("width")?);args354.push(e.get("seats")?);fun356.call(args354,kw355)?}}.attr("val")?;let mut args351=Vec::new();let mut kw352=Vec::new();fun353.call(args351,kw352)?}};e.set("built",assigned350.clone())?;
let assigned357={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun360=e.get("tray_volume")?;let mut args358=Vec::new();let mut kw359=Vec::new();args358.push(e.get("width")?);args358.push(e.get("seats")?);fun360.call(args358,kw359)?}};e.set("closed",assigned357.clone())?;
if {let v367={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun363=e.get("abs")?;let mut args361=Vec::new();let mut kw362=Vec::new();args361.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun366=e.get("built")?.attr("Volume")?;let mut args364=Vec::new();let mut kw365=Vec::new();fun366.call(args364,kw365)?}},e.get("closed")?)?);fun363.call(args361,kw362)?}};let v368=binary("mul",Val::Float(1e-06f64),e.get("closed")?)?;Val::Bool(compare("gt",v367.clone(),v368.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun371=e.get("fails")?.attr("append")?;let mut args369=Vec::new();let mut kw370=Vec::new();args369.push({let mut str372=String::new();str372.push_str("a four-seat tray measures ");str372.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun375=e.get("built")?.attr("Volume")?;let mut args373=Vec::new();let mut kw374=Vec::new();fun375.call(args373,kw374)?}},&val_string({let mut str376=String::new();str376.push_str(".3f");Val::Str(str376)})?)?);str372.push_str(" mm^3 against the ");str372.push_str(&format(&e.get("closed")?,&val_string({let mut str377=String::new();str377.push_str(".3f");Val::Str(str377)})?)?);str372.push_str(" its closed form says — a boss has met its neighbour or run off the plate");Val::Str(str372)});fun371.call(args369,kw370)?}};
}
let assigned378={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun381=e.get("built")?.attr("BoundingBox")?;let mut args379=Vec::new();let mut kw380=Vec::new();fun381.call(args379,kw380)?}};e.set("bb",assigned378.clone())?;
if {let v388={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun384=e.get("abs")?;let mut args382=Vec::new();let mut kw383=Vec::new();args382.push(binary("sub",e.get("bb")?.attr("ylen")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun387=e.get("height")?;let mut args385=Vec::new();let mut kw386=Vec::new();args385.push(e.get("seats")?);fun387.call(args385,kw386)?}})?);fun384.call(args382,kw383)?}};let v389=Val::Float(1e-06f64);Val::Bool(compare("gt",v388.clone(),v389.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun392=e.get("fails")?.attr("append")?;let mut args390=Vec::new();let mut kw391=Vec::new();args390.push({let mut str393=String::new();str393.push_str("a tray stands ");str393.push_str(&format(&e.get("bb")?.attr("ylen")?,&val_string({let mut str394=String::new();str394.push_str(".4f");Val::Str(str394)})?)?);str393.push_str(" mm high against the ");str393.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun397=e.get("height")?;let mut args395=Vec::new();let mut kw396=Vec::new();args395.push(e.get("seats")?);fun397.call(args395,kw396)?}},&val_string({let mut str398=String::new();str398.push_str(".4f");Val::Str(str398)})?)?);str393.push_str(" `height` declares");Val::Str(str393)});fun392.call(args390,kw391)?}};
}
Ok(Flow::Continue)})();let outcome349=(||->Result<Flow>{match attempt348{Ok(Flow::Return(value))=>Ok(Flow::Return(value)),Ok(Flow::Continue)=>{Ok(Flow::Continue)},Err(error)=>{e.set("exc",Val::Str(error.to_string()))?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun401=e.get("fails")?.attr("append")?;let mut args399=Vec::new();let mut kw400=Vec::new();args399.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun404=e.get("str")?;let mut args402=Vec::new();let mut kw403=Vec::new();args402.push(e.get("exc")?);fun404.call(args402,kw403)?}});fun401.call(args399,kw400)?}};
Ok(Flow::Continue)}}})();match outcome349?{Flow::Continue=>{},Flow::Return(value)=>return Ok(value)}
for item405 in e.get("fails")?.iter()? {
e.set("line",item405)?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun408=e.get("print")?;let mut args406=Vec::new();let mut kw407=Vec::new();args406.push({let mut str409=String::new();str409.push_str("FAIL ");str409.push_str(&format(&e.get("line")?,&String::new())?);Val::Str(str409)});fun408.call(args406,kw407)?}};
}
if unary("not",e.get("fails")?)?.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun412=e.get("print")?;let mut args410=Vec::new();let mut kw411=Vec::new();args410.push({let mut str413=String::new();str413.push_str("ok  valve-tray  ");str413.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun416=e.get("height")?;let mut args414=Vec::new();let mut kw415=Vec::new();args414.push(e.get("seats")?);fun416.call(args414,kw415)?}},&val_string({let mut str417=String::new();str417.push_str("g");Val::Str(str417)})?)?);str413.push_str(" mm high x ");str413.push_str(&format(&e.get("THICK")?,&val_string({let mut str418=String::new();str418.push_str("g");Val::Str(str418)})?)?);str413.push_str(" thick, seat ");str413.push_str(&format(&e.get("SEAT")?,&val_string({let mut str419=String::new();str419.push_str("g");Val::Str(str419)})?)?);str413.push_str(" (sunk), reach ");str413.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun422=e.get("reach")?;let mut args420=Vec::new();let mut kw421=Vec::new();fun422.call(args420,kw421)?}},&val_string({let mut str423=String::new();str423.push_str("g");Val::Str(str423)})?)?);str413.push_str(", port channel ");str413.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun426=e.get("port_channel_depth")?;let mut args424=Vec::new();let mut kw425=Vec::new();fun426.call(args424,kw425)?}},&val_string({let mut str427=String::new();str427.push_str(".3f");Val::Str(str427)})?)?);str413.push_str(" deep on ");str413.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/valve_tray.rs",line!());{let fun430=e.get("channel_floor")?;let mut args428=Vec::new();let mut kw429=Vec::new();fun430.call(args428,kw429)?}},&val_string({let mut str431=String::new();str431.push_str(".3f");Val::Str(str431)})?)?);str413.push_str(" of floor");Val::Str(str413)});fun412.call(args410,kw411)?}};
}
return Ok(if e.get("fails")?.truthy()? {Val::Int(1i64)} else {Val::Int(0i64)});
Ok(Val::None)})})?;
    // trays_of_machine
    e.set("trays_of_machine", {
        let params = vec![("facts".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("facts")?.attr("valve_trays")?);
            Ok(Val::None)
        })
    })?;
    // _socket_numbers
    e.set("_socket_numbers", {
        let params = vec![
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("shift".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun434 = e.get("_data")?;
                    let mut args432 = Vec::new();
                    let mut kw433 = Vec::new();
                    args432.push(Val::Str("sockets".into()));
                    kw433.push(("x".into(), e.get("x")?));
                    kw433.push(("y".into(), e.get("y")?));
                    kw433.push(("shift".into(), e.get("shift")?));
                    fun434.call(args432, kw433)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // tray_stock_numbers
    e.set("tray_stock_numbers", {
        let params = vec![("width".into(), None, false), ("seats".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun437 = e.get("_data")?;
                    let mut args435 = Vec::new();
                    let mut kw436 = Vec::new();
                    args435.push(Val::Str("stock".into()));
                    kw436.push(("width".into(), e.get("width")?));
                    kw436.push(("seats".into(), e.get("seats")?));
                    fun437.call(args435, kw436)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // numbers
    e.set("numbers", {
        let params = vec![("trays".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("interface", rt.import_module("_enclosure_interface")?)?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun440 = e.get("_data")?;
                    let mut args438 = Vec::new();
                    let mut kw439 = Vec::new();
                    args438.push(Val::Str("recipe".into()));
                    kw439.push(("trays".into(), e.get("trays")?));
                    kw439.push((
                        "extrusion_w".into(),
                        e.get("interface")?.attr("extrusion_w")?,
                    ));
                    fun440.call(args438, kw439)?
                }
            });
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
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            e.set("_facts", rt.import_module("_facts")?)?;
            let assigned441 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun444 = e.get("trays_of_machine")?;
                    let mut args442 = Vec::new();
                    let mut kw443 = Vec::new();
                    args442.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun447 = e.get("_facts")?.attr("read")?;
                            let mut args445 = Vec::new();
                            let mut kw446 = Vec::new();
                            fun447.call(args445, kw446)?
                        }
                    });
                    fun444.call(args442, kw443)?
                }
            };
            e.set("trays", assigned441.clone())?;
            let assigned448 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun451 = e.get("_rust_part")?.attr("check")?;
                    let mut args449 = Vec::new();
                    let mut kw450 = Vec::new();
                    args449.push(Val::Str("enclosure-components".into()));
                    args449.push(Val::Str("valve-tray".into()));
                    args449.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun454 = e.get("numbers")?;
                            let mut args452 = Vec::new();
                            let mut kw453 = Vec::new();
                            args452.push(e.get("trays")?);
                            fun454.call(args452, kw453)?
                        }
                    });
                    fun451.call(args449, kw450)?
                }
            };
            e.set("measured", assigned448.clone())?;
            let assigned455 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun458 = e.get("_data")?;
                    let mut args456 = Vec::new();
                    let mut kw457 = Vec::new();
                    args456.push(Val::Str("report".into()));
                    kw457.push(("trays".into(), e.get("trays")?));
                    kw457.push(("measured".into(), e.get("measured")?));
                    fun458.call(args456, kw457)?
                }
            };
            e.set("report", assigned455.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun461 = e.get("print")?;
                    let mut args459 = Vec::new();
                    let mut kw460 = Vec::new();
                    args459.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                            line!(),
                        );
                        {
                            let fun464 = Val::Str("\n".into()).attr("join")?;
                            let mut args462 = Vec::new();
                            let mut kw463 = Vec::new();
                            args462.push(e.get("report")?.get(Val::Str("lines".into()))?);
                            fun464.call(args462, kw463)?
                        }
                    });
                    fun461.call(args459, kw460)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun467 = e.get("substitute_md")?;
                    let mut args465 = Vec::new();
                    let mut kw466 = Vec::new();
                    args465.push(binary(
                        "truediv",
                        e.get("_here")?.attr("parent")?,
                        Val::Str("README.md".into()),
                    )?);
                    kw466.push((
                        "variables".into(),
                        e.get("report")?.get(Val::Str("variables".into()))?,
                    ));
                    fun467.call(args465, kw466)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun470 = e.get("print")?;
                    let mut args468 = Vec::new();
                    let mut kw469 = Vec::new();
                    args468.push(Val::Str("-> README.md".into()));
                    fun470.call(args468, kw469)?
                }
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
            line!(),
        );
        {
            let fun473 = e.get("_rust_part")?.attr("start")?;
            let mut args471 = Vec::new();
            let mut kw472 = Vec::new();
            fun473.call(args471, kw472)?
        }
    };
    if {
        let v476 = {
            let v480 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                    line!(),
                );
                {
                    let fun479 = e.get("len")?;
                    let mut args477 = Vec::new();
                    let mut kw478 = Vec::new();
                    args477.push(e.get("sys")?.attr("argv")?);
                    fun479.call(args477, kw478)?
                }
            };
            let v481 = Val::Int(1i64);
            Val::Bool(compare("gt", v480.clone(), v481.clone())?.truthy()?)
        };
        if v476.truthy()? {
            {
                let v474 = e.get("sys")?.attr("argv")?.get(Val::Int(1i64))?;
                let v475 = Val::Str("selftest".into());
                Val::Bool(compare("eq", v474.clone(), v475.clone())?.truthy()?)
            }
        } else {
            v476
        }
    }
    .truthy()?
    {
        {
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                line!(),
            );
            {
                let fun484 = e.get("sys")?.attr("exit")?;
                let mut args482 = Vec::new();
                let mut kw483 = Vec::new();
                args482.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
                        line!(),
                    );
                    {
                        let fun487 = e.get("selftest")?;
                        let mut args485 = Vec::new();
                        let mut kw486 = Vec::new();
                        fun487.call(args485, kw486)?
                    }
                });
                fun484.call(args482, kw483)?
            }
        };
    }
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/valve_tray.rs",
            line!(),
        );
        {
            let fun490 = e.get("main")?;
            let mut args488 = Vec::new();
            let mut kw489 = Vec::new();
            fun490.call(args488, kw489)?
        }
    };
    Ok(Val::None)
}
