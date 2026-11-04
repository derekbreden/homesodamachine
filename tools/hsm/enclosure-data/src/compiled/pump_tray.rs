//! Case-derived locating profiles for the integral pump inverse and lower retainer.
//!
//! The lower retainer has flat lands around the rigid eight-millimetre molded skirt.
//! Front-top's integral upper inverse locates the rear boss and clears the motor can.
//! The production geometry consumes these profiles in enclosure._fixed_pump_mount.
//!
//! The accepted earlier cradle/cap assembly held both physical pumps firmly without observed
//! vertical play; hardware/reference/kamoer-kphm400/physical-fit.json binds that identified
//! article. It does not qualify the integral upper/lower skirt capture. This module's collar
//! builder is a source solid, not a separate printed part. The physical reference is
//! hardware/reference/kamoer-kphm400/scan-review.md; case-derived geometry alone does not
//! independently establish physical contact.
//!
//! Run:
//!     tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-tray/pump_tray.py selftest
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
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
            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
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
            binary("truediv", e.get("_hw")?, Val::Str("reference".into()))?,
            Val::Str("kamoer-kphm400".into()),
        )?);
        s.push(e.get("_here")?.attr("parent")?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_p", item17)?;
        {
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                line!(),
            );
            {
                let fun20 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args18 = Vec::new();
                let mut kw19 = Vec::new();
                args18.push(Val::Int(0i64));
                args18.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
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
            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
            line!(),
        );
        {
            let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args24 = Vec::new();
            let mut kw25 = Vec::new();
            args24.push(Val::Int(0i64));
            args24.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun29=e.get("str")?;let mut args27=Vec::new();let mut kw28=Vec::new();args27.push(binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun32=e.get("next")?;let mut args30=Vec::new();let mut kw31=Vec::new();args30.push({let e=e.child();let out33=Val::list(vec![]);for item34 in e.get("_here")?.attr("parents")?.iter()? {e.set("p",item34)?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun37=binary("truediv",binary("truediv",e.get("p")?,Val::Str("tools".into()))?,Val::Str("docgen".into()))?.attr("is_dir")?;let mut args35=Vec::new();let mut kw36=Vec::new();fun37.call(args35,kw36)?}}.truthy()? {out33.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out33});fun32.call(args30,kw31)?}},Val::Str("tools".into()))?);fun29.call(args27,kw28)?}});
            fun26.call(args24, kw25)?
        }
    };
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("_kp", rt.import_module("kamoer_kphm400")?)?;
    e.set("_pc", rt.import_module("pump_case")?)?;
    e.set("fits", rt.import_module("fits")?)?;
    let mod38 = rt.import_module("docgen")?;
    e.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
            line!(),
        );
        {
            let fun41 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args39 = Vec::new();
            let mut kw40 = Vec::new();
            args39.push(Val::Int(0i64));
            args39.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun44 = e.get("str")?;
                    let mut args42 = Vec::new();
                    let mut kw43 = Vec::new();
                    args42.push(binary(
                        "truediv",
                        e.get("_hw")?,
                        Val::Str("printed-parts/enclosure/enclosure".into()),
                    )?);
                    fun44.call(args42, kw43)?
                }
            });
            fun41.call(args39, kw40)?
        }
    };
    let mod45 = rt.import_module("_enclosure_data")?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    // _pump_source
    e.set("_pump_source", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out46 = Val::dict(vec![]);
                for item47 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("barb_pitch".into()));
                    s.push(Val::Str("base_plane_z".into()));
                    s.push(Val::Str("bracket_t".into()));
                    s.push(Val::Str("bracket_w".into()));
                    s.push(Val::Str("head_depth".into()));
                    s.push(Val::Str("head_front_below_skirt".into()));
                    s.push(Val::Str("head_front_z".into()));
                    s.push(Val::Str("head_w".into()));
                    s.push(Val::Str("motor_dia".into()));
                    s.push(Val::Str("motor_end_z".into()));
                    s.push(Val::Str("outlet_relief".into()));
                    s.push(Val::Str("outlet_relief_run".into()));
                    s.push(Val::Str("outlet_span_x".into()));
                    s.push(Val::Str("rear_axis_y_shift".into()));
                    s.push(Val::Str("skirt_body_y".into()));
                    s.push(Val::Str("skirt_body_y_max".into()));
                    s.push(Val::Str("skirt_body_y_min".into()));
                    s.push(Val::Str("skirt_depth".into()));
                    s.push(Val::Str("skirt_support_xy_air".into()));
                    s.push(Val::Str("skirt_support_y_minus".into()));
                    s.push(Val::Str("skirt_upper_band".into()));
                    s.push(Val::Str("skirt_y".into()));
                    s.push(Val::Str("skirt_y_max".into()));
                    s.push(Val::Str("skirt_y_plus_air".into()));
                    s.push(Val::Str("tube_casing_w".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("name", item47)?;
                    out46.set(e.get("name")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun50 = e.get("getattr")?;
                            let mut args48 = Vec::new();
                            let mut kw49 = Vec::new();
                            args48.push(e.get("_kp")?);
                            args48.push(e.get("name")?);
                            fun50.call(args48, kw49)?
                        }
                    })?;
                }
                out46
            });
            Ok(Val::None)
        })
    })?;
    let assigned51 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
            line!(),
        );
        {
            let fun54 = e.get("_read")?;
            let mut args52 = Vec::new();
            let mut kw53 = Vec::new();
            args52.push(Val::Str("pump-tray-defaults".into()));
            kw53.push(("pump".into(), {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun57 = e.get("_pump_source")?;
                    let mut args55 = Vec::new();
                    let mut kw56 = Vec::new();
                    fun57.call(args55, kw56)?
                }
            }));
            kw53.push(("case".into(), e.get("_pc")?.attr("_case")?));
            kw53.push(("fits".into(), {
                let d = Val::dict(vec![]);
                d.set(Val::Str("running".into()), e.get("fits")?.attr("running")?)?;
                d
            }));
            fun54.call(args52, kw53)?
        }
    };
    e.set("_stock", assigned51.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
            line!(),
        );
        {
            let fun60 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun63 = e.get("globals")?;
                    let mut args61 = Vec::new();
                    let mut kw62 = Vec::new();
                    fun63.call(args61, kw62)?
                }
            }
            .attr("update")?;
            let mut args58 = Vec::new();
            let mut kw59 = Vec::new();
            args58.push(e.get("_stock")?);
            fun60.call(args58, kw59)?
        }
    };
    let assigned64 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
            line!(),
        );
        {
            let fun67 = e.get("tuple")?;
            let mut args65 = Vec::new();
            let mut kw66 = Vec::new();
            args65.push(e.get("_stock")?);
            fun67.call(args65, kw66)?
        }
    };
    e.set("_stock_names", assigned64.clone())?;
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
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun70 = e.get("_read")?;
                    let mut args68 = Vec::new();
                    let mut kw69 = Vec::new();
                    args68.push(binary("add", Val::Str("pump-tray-".into()), e.get("op")?)?);
                    kw69.push(("pump".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun73 = e.get("_pump_source")?;
                            let mut args71 = Vec::new();
                            let mut kw72 = Vec::new();
                            fun73.call(args71, kw72)?
                        }
                    }));
                    kw69.push(("case".into(), e.get("_pc")?.attr("_case")?));
                    kw69.push(("stock".into(), {
                        let e = e.child();
                        let out74 = Val::dict(vec![]);
                        for item75 in e.get("_stock_names")?.iter()? {
                            e.set("name", item75)?;
                            out74.set(
                                e.get("name")?,
                                {
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                                        line!(),
                                    );
                                    {
                                        let fun78 = e.get("globals")?;
                                        let mut args76 = Vec::new();
                                        let mut kw77 = Vec::new();
                                        fun78.call(args76, kw77)?
                                    }
                                }
                                .get(e.get("name")?)?,
                            )?;
                        }
                        out74
                    }));
                    kw69.extend(keyword_items(e.get("values")?)?);
                    fun70.call(args68, kw69)?
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
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun81 = e.get("_data")?;
                    let mut args79 = Vec::new();
                    let mut kw80 = Vec::new();
                    args79.push(Val::Str("depth".into()));
                    fun81.call(args79, kw80)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // half_width
    e.set("half_width", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("case_half")?);
            Ok(Val::None)
        })
    })?;
    // far_reach
    e.set("far_reach", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("case_half")?);
            Ok(Val::None)
        })
    })?;
    // _in_pump_frame
    e.set("_in_pump_frame", {
        let params = vec![("solid".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun84 = e.get("solid")?.attr("translate")?;
                    let mut args82 = Vec::new();
                    let mut kw83 = Vec::new();
                    args82.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", e.get("_pc")?.attr("center_x")?)?);
                        s.push(unary("neg", e.get("_pc")?.attr("center_y")?)?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun84.call(args82, kw83)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // head_room
    e.set("head_room", {
        let params = vec![("air".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun87 = e.get("_in_pump_frame")?;
                    let mut args85 = Vec::new();
                    let mut kw86 = Vec::new();
                    args85.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun90 = e.get("_pc")?.attr("stepped_skirt_cavity")?;
                            let mut args88 = Vec::new();
                            let mut kw89 = Vec::new();
                            args88.push(e.get("air")?);
                            args88.push(unary("neg", e.get("skirt_depth")?)?);
                            args88.push(e.get("skirt_body_open_y_bounds")?);
                            args88.push(e.get("skirt_open_y_max")?);
                            fun90.call(args88, kw89)?
                        }
                    });
                    fun87.call(args85, kw86)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // outlet_fore_miter
    e.set("outlet_fore_miter", {
        let params = vec![("air".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun93 = e.get("tuple")?;
                    let mut args91 = Vec::new();
                    let mut kw92 = Vec::new();
                    args91.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun96 = e.get("_data")?;
                            let mut args94 = Vec::new();
                            let mut kw95 = Vec::new();
                            args94.push(Val::Str("miter".into()));
                            kw95.push(("air".into(), e.get("air")?));
                            fun96.call(args94, kw95)?
                        }
                    });
                    fun93.call(args91, kw92)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // outlet_under_tangent
    e.set("outlet_under_tangent", {
        let params = vec![("air".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun99 = e.get("tuple")?;
                    let mut args97 = Vec::new();
                    let mut kw98 = Vec::new();
                    args97.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun102 = e.get("_data")?;
                            let mut args100 = Vec::new();
                            let mut kw101 = Vec::new();
                            args100.push(Val::Str("tangent".into()));
                            kw101.push(("air".into(), e.get("air")?));
                            fun102.call(args100, kw101)?
                        }
                    });
                    fun99.call(args97, kw98)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _outlet_span_extensions
    e.set("_outlet_span_extensions", {
        let params = vec![("air".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned103 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun106 = e.get("outlet_fore_miter")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    args104.push(e.get("air")?);
                    fun106.call(args104, kw105)?
                }
            };
            let unpack107 = unpack(assigned103.clone(), 4)?;
            e.set("body_half", unpack107[0].clone())?;
            e.set("y0", unpack107[1].clone())?;
            e.set("open_half", unpack107[2].clone())?;
            e.set("_y_open", unpack107[3].clone())?;
            if {
                let v108 = e.get("open_half")?;
                let v109 = binary("add", e.get("body_half")?, Val::Float(1e-09f64))?;
                Val::Bool(compare("le", v108.clone(), v109.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(Val::None);
            }
            let assigned110 = e.get("body_half")?;
            e.set("y1", assigned110.clone())?;
            let assigned111 = {
                let mut s = Vec::new();
                s.push(e.get("outlet_axis_z")?);
                s.push(Val::Float(0.0f64));
                Val::tuple(s)
            };
            let unpack112 = unpack(assigned111.clone(), 2)?;
            e.set("z0", unpack112[0].clone())?;
            e.set("z1", unpack112[1].clone())?;
            // slab
            e.set("slab", {
                let params = vec![("x0".into(), None, false), ("x1".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun115 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                                    line!(),
                                );
                                {
                                    let fun118 = {
                                        let _site = rt.source_at(
                                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                                            line!(),
                                        );
                                        {
                                            let fun121 = e.get("cq")?.attr("Workplane")?;
                                            let mut args119 = Vec::new();
                                            let mut kw120 = Vec::new();
                                            args119.push(Val::Str("XY".into()));
                                            fun121.call(args119, kw120)?
                                        }
                                    }
                                    .attr("box")?;
                                    let mut args116 = Vec::new();
                                    let mut kw117 = Vec::new();
                                    args116.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                                    args116.push(binary("sub", e.get("y1")?, e.get("y0")?)?);
                                    args116.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                                    kw117.push(("centered".into(), Val::Bool(false)));
                                    fun118.call(args116, kw117)?
                                }
                            }
                            .attr("translate")?;
                            let mut args113 = Vec::new();
                            let mut kw114 = Vec::new();
                            args113.push({
                                let mut s = Vec::new();
                                s.push(e.get("x0")?);
                                s.push(e.get("y0")?);
                                s.push(e.get("z0")?);
                                Val::tuple(s)
                            });
                            fun115.call(args113, kw114)?
                        }
                    });
                    Ok(Val::None)
                })
            })?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun124 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun127 = e.get("slab")?;
                            let mut args125 = Vec::new();
                            let mut kw126 = Vec::new();
                            args125.push(unary("neg", e.get("open_half")?)?);
                            args125.push(unary("neg", e.get("body_half")?)?);
                            fun127.call(args125, kw126)?
                        }
                    }
                    .attr("union")?;
                    let mut args122 = Vec::new();
                    let mut kw123 = Vec::new();
                    args122.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun130 = e.get("slab")?;
                            let mut args128 = Vec::new();
                            let mut kw129 = Vec::new();
                            args128.push(e.get("body_half")?);
                            args128.push(e.get("open_half")?);
                            fun130.call(args128, kw129)?
                        }
                    });
                    fun124.call(args122, kw123)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // outlet_passage_start_y
    e.set("outlet_passage_start_y", {
        let params = vec![("air".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun133 = e.get("_data")?;
                    let mut args131 = Vec::new();
                    let mut kw132 = Vec::new();
                    args131.push(Val::Str("passage".into()));
                    kw132.push(("air".into(), e.get("air")?));
                    fun133.call(args131, kw132)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // drop_well
    e.set("drop_well", {
        let params = vec![
            ("air".into(), None, false),
            ("support_top".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v134 = e.get("support_top")?;
                let v135 = Val::None;
                Val::Bool(compare("is", v134.clone(), v135.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned136 = unary(
                    "neg",
                    binary("add", e.get("skirt_depth")?, e.get("skirt_support_air")?)?,
                )?;
                e.set("support_top", assigned136.clone())?;
            }
            let assigned137 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun140 = e.get("_in_pump_frame")?;
                    let mut args138 = Vec::new();
                    let mut kw139 = Vec::new();
                    args138.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun143 = e.get("_pc")?.attr("stepped_skirt_drop_well")?;
                            let mut args141 = Vec::new();
                            let mut kw142 = Vec::new();
                            args141.push(e.get("air")?);
                            args141.push(e.get("support_top")?);
                            args141.push(e.get("skirt_body_open_y_bounds")?);
                            args141.push(e.get("skirt_open_y_max")?);
                            fun143.call(args141, kw142)?
                        }
                    });
                    fun140.call(args138, kw139)?
                }
            };
            e.set("room", assigned137.clone())?;
            let assigned144 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun147 = e.get("_outlet_span_extensions")?;
                    let mut args145 = Vec::new();
                    let mut kw146 = Vec::new();
                    args145.push(e.get("air")?);
                    fun147.call(args145, kw146)?
                }
            };
            e.set("extensions", assigned144.clone())?;
            return Ok(
                if {
                    let v148 = e.get("extensions")?;
                    let v149 = Val::None;
                    Val::Bool(compare("is", v148.clone(), v149.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("room")?
                } else {
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun152 = e.get("room")?.attr("union")?;
                            let mut args150 = Vec::new();
                            let mut kw151 = Vec::new();
                            args150.push(e.get("extensions")?);
                            fun152.call(args150, kw151)?
                        }
                    }
                },
            );
            Ok(Val::None)
        })
    })?;
    // boss_room
    e.set("boss_room",{let params=vec![("air".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun155={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun158={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun161={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun164={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun167=e.get("cq")?.attr("Workplane")?;let mut args165=Vec::new();let mut kw166=Vec::new();args165.push(Val::Str("XY".into()));fun167.call(args165,kw166)?}}.attr("polyline")?;let mut args162=Vec::new();let mut kw163=Vec::new();args162.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun170=e.get("_pc")?.attr("_ring")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun173=e.get("_pc")?.attr("offset_polygon")?;let mut args171=Vec::new();let mut kw172=Vec::new();args171.push(e.get("_pc")?.attr("bore_profile")?);args171.push(e.get("air")?);fun173.call(args171,kw172)?}});fun170.call(args168,kw169)?}});fun164.call(args162,kw163)?}}.attr("wire")?;let mut args159=Vec::new();let mut kw160=Vec::new();fun161.call(args159,kw160)?}}.attr("extrude")?;let mut args156=Vec::new();let mut kw157=Vec::new();args156.push(e.get("boss_depth")?);fun158.call(args156,kw157)?}}.attr("val")?;let mut args153=Vec::new();let mut kw154=Vec::new();fun155.call(args153,kw154)?}});
Ok(Val::None)})})?;
    // _case_base
    e.set("_case_base", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned174 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun177 = e.get("_pc")?.attr("build_base_plate_with_ramp")?;
                    let mut args175 = Vec::new();
                    let mut kw176 = Vec::new();
                    fun177.call(args175, kw176)?
                }
            };
            e.set("solid", assigned174.clone())?;
            let assigned178 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun181 = e.get("_pc")?.attr("add_bore_wall")?;
                    let mut args179 = Vec::new();
                    let mut kw180 = Vec::new();
                    args179.push(e.get("solid")?);
                    fun181.call(args179, kw180)?
                }
            };
            e.set("solid", assigned178.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun184 = e.get("solid")?.attr("union")?;
                    let mut args182 = Vec::new();
                    let mut kw183 = Vec::new();
                    args182.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun187 = e.get("_pc")?.attr("build_tower")?;
                            let mut args185 = Vec::new();
                            let mut kw186 = Vec::new();
                            fun187.call(args185, kw186)?
                        }
                    });
                    fun184.call(args182, kw183)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _slab
    e.set("_slab", {
        let params = vec![
            ("x0".into(), None, false),
            ("x1".into(), None, false),
            ("y0".into(), None, false),
            ("y1".into(), None, false),
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
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun190 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun193 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                                    line!(),
                                );
                                {
                                    let fun196 = e.get("cq")?.attr("Workplane")?;
                                    let mut args194 = Vec::new();
                                    let mut kw195 = Vec::new();
                                    args194.push(Val::Str("XY".into()));
                                    fun196.call(args194, kw195)?
                                }
                            }
                            .attr("box")?;
                            let mut args191 = Vec::new();
                            let mut kw192 = Vec::new();
                            args191.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                            args191.push(binary("sub", e.get("y1")?, e.get("y0")?)?);
                            args191.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                            kw192.push(("centered".into(), Val::Bool(false)));
                            fun193.call(args191, kw192)?
                        }
                    }
                    .attr("translate")?;
                    let mut args188 = Vec::new();
                    let mut kw189 = Vec::new();
                    args188.push({
                        let mut s = Vec::new();
                        s.push(e.get("x0")?);
                        s.push(e.get("y0")?);
                        s.push(e.get("z0")?);
                        Val::tuple(s)
                    });
                    fun190.call(args188, kw189)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // build_pump_tray
    e.set("build_pump_tray",{let params=vec![("root".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned197={let mut s=Vec::new();s.push(e.get("_pc")?.attr("center_x")?);s.push(e.get("_pc")?.attr("center_y")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun200=e.get("half_width")?;let mut args198=Vec::new();let mut kw199=Vec::new();fun200.call(args198,kw199)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun203=e.get("far_reach")?;let mut args201=Vec::new();let mut kw202=Vec::new();fun203.call(args201,kw202)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun206=e.get("depth")?;let mut args204=Vec::new();let mut kw205=Vec::new();fun206.call(args204,kw205)?}});Val::tuple(s)};let unpack207=unpack(assigned197.clone(),5)?;e.set("cx",unpack207[0].clone())?;e.set("cy",unpack207[1].clone())?;e.set("hw",unpack207[2].clone())?;e.set("fr",unpack207[3].clone())?;e.set("d",unpack207[4].clone())?;
let assigned208=binary("add",binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun211=e.get("max")?;let mut args209=Vec::new();let mut kw210=Vec::new();args209.push(e.get("hw")?);args209.push(e.get("fr")?);args209.push(e.get("root")?);fun211.call(args209,kw210)?}},e.get("case_half")?)?,Val::Float(10.0f64))?;e.set("big",assigned208.clone())?;
let assigned212={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun215={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun218=e.get("_case_base")?;let mut args216=Vec::new();let mut kw217=Vec::new();fun218.call(args216,kw217)?}}.attr("translate")?;let mut args213=Vec::new();let mut kw214=Vec::new();args213.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(e.get("rear_axis_y_shift")?);s.push(Val::Float(0.0f64));Val::tuple(s)});fun215.call(args213,kw214)?}};e.set("tray",assigned212.clone())?;
let assigned219={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun222=e.get("tray")?.attr("cut")?;let mut args220=Vec::new();let mut kw221=Vec::new();args220.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun225=e.get("_slab")?;let mut args223=Vec::new();let mut kw224=Vec::new();args223.push(binary("sub",e.get("cx")?,e.get("big")?)?);args223.push(binary("add",e.get("cx")?,e.get("big")?)?);args223.push(binary("sub",e.get("cy")?,e.get("big")?)?);args223.push(binary("add",e.get("cy")?,e.get("big")?)?);args223.push(e.get("d")?);args223.push(binary("add",e.get("d")?,e.get("big")?)?);fun225.call(args223,kw224)?}});fun222.call(args220,kw221)?}};e.set("tray",assigned219.clone())?;
let assigned226={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun229=e.get("tray")?.attr("union")?;let mut args227=Vec::new();let mut kw228=Vec::new();args227.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun232=e.get("_slab")?;let mut args230=Vec::new();let mut kw231=Vec::new();args230.push(binary("sub",e.get("cx")?,e.get("hw")?)?);args230.push(binary("add",e.get("cx")?,e.get("hw")?)?);args230.push(binary("sub",e.get("cy")?,e.get("root")?)?);args230.push(binary("add",e.get("cy")?,e.get("fr")?)?);args230.push(Val::Float(0.0f64));args230.push(e.get("_pc")?.attr("base_thickness")?);fun232.call(args230,kw231)?}});fun229.call(args227,kw228)?}};e.set("tray",assigned226.clone())?;
let assigned233={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun236=e.get("tray")?.attr("cut")?;let mut args234=Vec::new();let mut kw235=Vec::new();args234.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun239={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun242={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun245={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun248={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun251={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun254=e.get("cq")?.attr("Workplane")?;let mut args252=Vec::new();let mut kw253=Vec::new();args252.push(Val::Str("XY".into()));fun254.call(args252,kw253)?}}.attr("workplane")?;let mut args249=Vec::new();let mut kw250=Vec::new();kw250.push(("offset".into(),unary("neg",Val::Float(1.0f64))?));fun251.call(args249,kw250)?}}.attr("center")?;let mut args246=Vec::new();let mut kw247=Vec::new();args246.push(e.get("cx")?);args246.push(binary("add",e.get("cy")?,e.get("rear_axis_y_shift")?)?);fun248.call(args246,kw247)?}}.attr("polyline")?;let mut args243=Vec::new();let mut kw244=Vec::new();args243.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun257=e.get("_pc")?.attr("_ring")?;let mut args255=Vec::new();let mut kw256=Vec::new();args255.push(e.get("_pc")?.attr("bore_profile")?);fun257.call(args255,kw256)?}});fun245.call(args243,kw244)?}}.attr("wire")?;let mut args240=Vec::new();let mut kw241=Vec::new();fun242.call(args240,kw241)?}}.attr("extrude")?;let mut args237=Vec::new();let mut kw238=Vec::new();args237.push(binary("add",e.get("boss_depth")?,Val::Float(1.0f64))?);fun239.call(args237,kw238)?}});fun236.call(args234,kw235)?}};e.set("tray",assigned233.clone())?;
let assigned258={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun261=e.get("tray")?.attr("cut")?;let mut args259=Vec::new();let mut kw260=Vec::new();args259.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun264=e.get("_slab")?;let mut args262=Vec::new();let mut kw263=Vec::new();args262.push(binary("sub",e.get("cx")?,e.get("big")?)?);args262.push(binary("add",e.get("cx")?,e.get("big")?)?);args262.push(binary("sub",binary("sub",e.get("cy")?,e.get("root")?)?,e.get("big")?)?);args262.push(binary("sub",e.get("cy")?,e.get("root")?)?);args262.push(unary("neg",Val::Float(1.0f64))?);args262.push(binary("add",e.get("d")?,Val::Float(1.0f64))?);fun264.call(args262,kw263)?}});fun261.call(args259,kw260)?}};e.set("tray",assigned258.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun267=e.get("tray")?.attr("translate")?;let mut args265=Vec::new();let mut kw266=Vec::new();args265.push({let mut s=Vec::new();s.push(unary("neg",e.get("cx")?)?);s.push(unary("neg",e.get("cy")?)?);s.push(Val::Float(0.0f64));Val::tuple(s)});fun267.call(args265,kw266)?}});
Ok(Val::None)})})?;
    // pump_bodies
    e.set("pump_bodies",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun270=e.get("tuple")?;let mut args268=Vec::new();let mut kw269=Vec::new();args268.push({let e=e.child();let out271=Val::list(vec![]);for item272 in e.get("_kp")?.attr("BODY_PARTS")?.iter()? {let unpack273=unpack(item272,3)?;e.set("_name",unpack273[0].clone())?;e.set("part",unpack273[1].clone())?;e.set("_colour",unpack273[2].clone())?;out271.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun276={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun279={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun282=e.get("part")?;let mut args280=Vec::new();let mut kw281=Vec::new();fun282.call(args280,kw281)?}}.attr("val")?;let mut args277=Vec::new();let mut kw278=Vec::new();fun279.call(args277,kw278)?}}.attr("translate")?;let mut args274=Vec::new();let mut kw275=Vec::new();args274.push({let mut s=Vec::new();s.push(unary("neg",e.get("_kp")?.attr("cx")?)?);s.push(unary("neg",e.get("_kp")?.attr("cy")?)?);s.push(Val::Float(0.0f64));Val::tuple(s)});fun276.call(args274,kw275)?}}],vec![])?;}out271});fun270.call(args268,kw269)?}});
Ok(Val::None)})})?;
    // fouled_volume
    e.set("fouled_volume",{let params=vec![("root".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned283={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun286={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun289=e.get("build_pump_tray")?;let mut args287=Vec::new();let mut kw288=Vec::new();args287.push(e.get("root")?);fun289.call(args287,kw288)?}}.attr("val")?;let mut args284=Vec::new();let mut kw285=Vec::new();fun286.call(args284,kw285)?}};e.set("tray",assigned283.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun292=e.get("sum")?;let mut args290=Vec::new();let mut kw291=Vec::new();args290.push({let e=e.child();let out293=Val::list(vec![]);for item294 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun297=e.get("pump_bodies")?;let mut args295=Vec::new();let mut kw296=Vec::new();fun297.call(args295,kw296)?}}.iter()? {e.set("body",item294)?;out293.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun300={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun303=e.get("tray")?.attr("intersect")?;let mut args301=Vec::new();let mut kw302=Vec::new();args301.push(e.get("body")?);fun303.call(args301,kw302)?}}.attr("Volume")?;let mut args298=Vec::new();let mut kw299=Vec::new();fun300.call(args298,kw299)?}}],vec![])?;}out293});fun292.call(args290,kw291)?}});
Ok(Val::None)})})?;
    // storeys
    e.set("storeys",{let params=vec![("root".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned304={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun307={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun310=e.get("build_pump_tray")?;let mut args308=Vec::new();let mut kw309=Vec::new();args308.push(e.get("root")?);fun310.call(args308,kw309)?}}.attr("val")?;let mut args305=Vec::new();let mut kw306=Vec::new();fun307.call(args305,kw306)?}};e.set("tray",assigned304.clone())?;
let assigned311={let mut s=Vec::new();Val::list(s)};e.set("out",assigned311.clone())?;
for item312 in {let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(e.get("boss_depth")?);Val::tuple(s)}.iter()? {
e.set("z",item312)?;let assigned313={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun316=e.get("tray")?.attr("intersect")?;let mut args314=Vec::new();let mut kw315=Vec::new();args314.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun319={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun322={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun325={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun328=e.get("cq")?.attr("Workplane")?;let mut args326=Vec::new();let mut kw327=Vec::new();args326.push(Val::Str("XY".into()));fun328.call(args326,kw327)?}}.attr("box")?;let mut args323=Vec::new();let mut kw324=Vec::new();args323.push(Val::Float(1000.0f64));args323.push(Val::Float(1000.0f64));args323.push(Val::Float(0.02f64));kw324.push(("centered".into(),Val::Bool(true)));fun325.call(args323,kw324)?}}.attr("translate")?;let mut args320=Vec::new();let mut kw321=Vec::new();args320.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(binary("add",e.get("z")?,Val::Float(0.05f64))?);Val::tuple(s)});fun322.call(args320,kw321)?}}.attr("val")?;let mut args317=Vec::new();let mut kw318=Vec::new();fun319.call(args317,kw318)?}});fun316.call(args314,kw315)?}};e.set("cut",assigned313.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun331=e.get("out")?.attr("append")?;let mut args329=Vec::new();let mut kw330=Vec::new();args329.push(binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun334=e.get("cut")?.attr("Volume")?;let mut args332=Vec::new();let mut kw333=Vec::new();fun334.call(args332,kw333)?}},Val::Float(0.02f64))?);fun331.call(args329,kw330)?}};
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun337=e.get("tuple")?;let mut args335=Vec::new();let mut kw336=Vec::new();args335.push(e.get("out")?);fun337.call(args335,kw336)?}});
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
            return Ok(e.get("facts")?.attr("pump_trays")?);
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
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun340 = e.get("_data")?;
                    let mut args338 = Vec::new();
                    let mut kw339 = Vec::new();
                    args338.push(Val::Str("recipe".into()));
                    kw339.push(("trays".into(), e.get("trays")?));
                    fun340.call(args338, kw339)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // selftest
    e.set("selftest",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned341={let mut s=Vec::new();Val::list(s)};e.set("fails",assigned341.clone())?;
if {let v345={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun344=e.get("half_width")?;let mut args342=Vec::new();let mut kw343=Vec::new();fun344.call(args342,kw343)?}};let v346=e.get("bracket_half")?;Val::Bool(compare("lt",v345.clone(),v346.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun349=e.get("fails")?.attr("append")?;let mut args347=Vec::new();let mut kw348=Vec::new();args347.push({let mut str350=String::new();str350.push_str("the collar runs ");str350.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun353=e.get("half_width")?;let mut args351=Vec::new();let mut kw352=Vec::new();fun353.call(args351,kw352)?}},&val_string({let mut str354=String::new();str354.push_str(".3f");Val::Str(str354)})?)?);str350.push_str(" mm off the axis and the bracket reaches ");str350.push_str(&format(&e.get("bracket_half")?,&val_string({let mut str355=String::new();str355.push_str(".3f");Val::Str(str355)})?)?);str350.push_str(" — the pressing annulus cannot cover it");Val::Str(str350)});fun349.call(args347,kw348)?}};
}
if {let v356=e.get("can_half")?;let v357=e.get("boss_half")?;Val::Bool(compare("ge",v356.clone(),v357.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun360=e.get("fails")?.attr("append")?;let mut args358=Vec::new();let mut kw359=Vec::new();args358.push({let mut str361=String::new();str361.push_str("the can's bore reaches ");str361.push_str(&format(&e.get("can_half")?,&val_string({let mut str362=String::new();str362.push_str("g");Val::Str(str362)})?)?);str361.push_str(" mm and the boss's octagon ");str361.push_str(&format(&e.get("boss_half")?,&val_string({let mut str363=String::new();str363.push_str("g");Val::Str(str363)})?)?);str361.push_str(" — the shoulder lands on nothing");Val::Str(str361)});fun360.call(args358,kw359)?}};
}
let assigned364=binary("add",e.get("head_half")?,Val::Float(3.0f64))?;e.set("root",assigned364.clone())?;
let attempt365=(||->Result<Flow>{let assigned367={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun370={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun373=e.get("build_pump_tray")?;let mut args371=Vec::new();let mut kw372=Vec::new();args371.push(e.get("root")?);fun373.call(args371,kw372)?}}.attr("val")?;let mut args368=Vec::new();let mut kw369=Vec::new();fun370.call(args368,kw369)?}};e.set("built",assigned367.clone())?;
if unary("not",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun376=e.get("built")?.attr("isValid")?;let mut args374=Vec::new();let mut kw375=Vec::new();fun376.call(args374,kw375)?}})?.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun379=e.get("fails")?.attr("append")?;let mut args377=Vec::new();let mut kw378=Vec::new();args377.push(Val::Str("the tray is not a valid solid".into()));fun379.call(args377,kw378)?}};
}
if {let v386={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun382=e.get("len")?;let mut args380=Vec::new();let mut kw381=Vec::new();args380.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun385=e.get("built")?.attr("Solids")?;let mut args383=Vec::new();let mut kw384=Vec::new();fun385.call(args383,kw384)?}});fun382.call(args380,kw381)?}};let v387=Val::Int(1i64);Val::Bool(compare("ne",v386.clone(),v387.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun390=e.get("fails")?.attr("append")?;let mut args388=Vec::new();let mut kw389=Vec::new();args388.push({let mut str391=String::new();str391.push_str("the tray comes out ");str391.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun394=e.get("len")?;let mut args392=Vec::new();let mut kw393=Vec::new();args392.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun397=e.get("built")?.attr("Solids")?;let mut args395=Vec::new();let mut kw396=Vec::new();fun397.call(args395,kw396)?}});fun394.call(args392,kw393)?}},&String::new())?);str391.push_str(" solids, not one — the plate carried out has parted from the case's own");Val::Str(str391)});fun390.call(args388,kw389)?}};
}
let assigned398={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun401=e.get("built")?.attr("BoundingBox")?;let mut args399=Vec::new();let mut kw400=Vec::new();fun401.call(args399,kw400)?}};e.set("bb",assigned398.clone())?;
if {let v408={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun404=e.get("abs")?;let mut args402=Vec::new();let mut kw403=Vec::new();args402.push(binary("sub",e.get("bb")?.attr("zlen")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun407=e.get("depth")?;let mut args405=Vec::new();let mut kw406=Vec::new();fun407.call(args405,kw406)?}})?);fun404.call(args402,kw403)?}};let v409=Val::Float(1e-06f64);Val::Bool(compare("gt",v408.clone(),v409.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun412=e.get("fails")?.attr("append")?;let mut args410=Vec::new();let mut kw411=Vec::new();args410.push({let mut str413=String::new();str413.push_str("a tray runs ");str413.push_str(&format(&e.get("bb")?.attr("zlen")?,&val_string({let mut str414=String::new();str414.push_str(".4f");Val::Str(str414)})?)?);str413.push_str(" mm along the pump's axis against the ");str413.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun417=e.get("depth")?;let mut args415=Vec::new();let mut kw416=Vec::new();fun417.call(args415,kw416)?}},&val_string({let mut str418=String::new();str418.push_str("g");Val::Str(str418)})?)?);str413.push_str(" it declares");Val::Str(str413)});fun412.call(args410,kw411)?}};
}
let assigned419={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun422=e.get("fouled_volume")?;let mut args420=Vec::new();let mut kw421=Vec::new();args420.push(e.get("root")?);fun422.call(args420,kw421)?}};e.set("foul",assigned419.clone())?;
if {let v423=e.get("foul")?;let v424=Val::Float(1e-06f64);Val::Bool(compare("gt",v423.clone(),v424.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun427=e.get("fails")?.attr("append")?;let mut args425=Vec::new();let mut kw426=Vec::new();args425.push({let mut str428=String::new();str428.push_str("the tray stands ");str428.push_str(&format(&e.get("foul")?,&val_string({let mut str429=String::new();str429.push_str(".6f");Val::Str(str429)})?)?);str428.push_str(" mm^3 inside the pump it holds");Val::Str(str428)});fun427.call(args425,kw426)?}};
}
let assigned430={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun433=e.get("storeys")?;let mut args431=Vec::new();let mut kw432=Vec::new();args431.push(e.get("root")?);fun433.call(args431,kw432)?}};let unpack434=unpack(assigned430.clone(),2)?;e.set("on_head",unpack434[0].clone())?;e.set("on_crown",unpack434[1].clone())?;
if {let v435=e.get("on_head")?;let v436=Val::Float(0.0f64);Val::Bool(compare("le",v435.clone(),v436.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun439=e.get("fails")?.attr("append")?;let mut args437=Vec::new();let mut kw438=Vec::new();args437.push(Val::Str("the tray carries no material on the head's own crown".into()));fun439.call(args437,kw438)?}};
}
if {let v440=e.get("on_crown")?;let v441=Val::Float(0.0f64);Val::Bool(compare("le",v440.clone(),v441.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun444=e.get("fails")?.attr("append")?;let mut args442=Vec::new();let mut kw443=Vec::new();args442.push(Val::Str("the tray carries no material on the boss's crown — the cut took the shoulder with the cylinder".into()));fun444.call(args442,kw443)?}};
}
Ok(Flow::Continue)})();let outcome366=(||->Result<Flow>{match attempt365{Ok(Flow::Return(value))=>Ok(Flow::Return(value)),Ok(Flow::Continue)=>{Ok(Flow::Continue)},Err(error)=>{e.set("exc",Val::Str(error.to_string()))?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun447=e.get("fails")?.attr("append")?;let mut args445=Vec::new();let mut kw446=Vec::new();args445.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun450=e.get("str")?;let mut args448=Vec::new();let mut kw449=Vec::new();args448.push(e.get("exc")?);fun450.call(args448,kw449)?}});fun447.call(args445,kw446)?}};
Ok(Flow::Continue)}}})();match outcome366?{Flow::Continue=>{},Flow::Return(value)=>return Ok(value)}
let attempt451=(||->Result<Flow>{let assigned453={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun456={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun459=e.get("_in_pump_frame")?;let mut args457=Vec::new();let mut kw458=Vec::new();args457.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun462=e.get("_kp")?.attr("build_head")?;let mut args460=Vec::new();let mut kw461=Vec::new();fun462.call(args460,kw461)?}});fun459.call(args457,kw458)?}}.attr("val")?;let mut args454=Vec::new();let mut kw455=Vec::new();fun456.call(args454,kw455)?}};e.set("head",assigned453.clone())?;
let assigned463=Val::Float(0.4f64);e.set("fitted_air",assigned463.clone())?;
let assigned464={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun467={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun470=e.get("drop_well")?;let mut args468=Vec::new();let mut kw469=Vec::new();args468.push(e.get("fitted_air")?);fun470.call(args468,kw469)?}}.attr("val")?;let mut args465=Vec::new();let mut kw466=Vec::new();fun467.call(args465,kw466)?}};e.set("well",assigned464.clone())?;
if {let v479=unary("not",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun482=e.get("well")?.attr("isValid")?;let mut args480=Vec::new();let mut kw481=Vec::new();fun482.call(args480,kw481)?}})?;if v479.truthy()? {v479} else {{let v477={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun473=e.get("len")?;let mut args471=Vec::new();let mut kw472=Vec::new();args471.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun476=e.get("well")?.attr("Solids")?;let mut args474=Vec::new();let mut kw475=Vec::new();fun476.call(args474,kw475)?}});fun473.call(args471,kw472)?}};let v478=Val::Int(1i64);Val::Bool(compare("ne",v477.clone(),v478.clone())?.truthy()?)}}}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun485=e.get("fails")?.attr("append")?;let mut args483=Vec::new();let mut kw484=Vec::new();args483.push(Val::Str("the fitted drop well is not one valid solid".into()));fun485.call(args483,kw484)?}};
}
let assigned486={let e=e.child();let out487=Val::list(vec![]);for item488 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun491=e.get("head")?.attr("Faces")?;let mut args489=Vec::new();let mut kw490=Vec::new();fun491.call(args489,kw490)?}}.iter()? {e.set("face",item488)?;if {let v500={let v507={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun503=e.get("abs")?;let mut args501=Vec::new();let mut kw502=Vec::new();args501.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun506=e.get("face")?.attr("normalAt")?;let mut args504=Vec::new();let mut kw505=Vec::new();fun506.call(args504,kw505)?}}.attr("x")?);fun503.call(args501,kw502)?}};let v508=Val::Float(0.6f64);Val::Bool(compare("gt",v507.clone(),v508.clone())?.truthy()?)};if v500.truthy()? {{let v498={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun494=e.get("abs")?;let mut args492=Vec::new();let mut kw493=Vec::new();args492.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun497=e.get("face")?.attr("normalAt")?;let mut args495=Vec::new();let mut kw496=Vec::new();fun497.call(args495,kw496)?}}.attr("z")?);fun494.call(args492,kw493)?}};let v499=Val::Float(0.6f64);Val::Bool(compare("gt",v498.clone(),v499.clone())?.truthy()?)}} else {v500}}.truthy()? {out487.attr("append")?.call(vec![e.get("face")?],vec![])?;}}out487};e.set("ramps",assigned486.clone())?;
if unary("not",e.get("ramps")?)?.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun511=e.get("fails")?.attr("append")?;let mut args509=Vec::new();let mut kw510=Vec::new();args509.push(Val::Str("the pump reference has no lower flank ramps to verify".into()));fun511.call(args509,kw510)?}};
}
for item512 in e.get("ramps")?.iter()? {
e.set("face",item512)?;let assigned513={let e=e.child();let out514=Val::list(vec![]);for item515 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun518=e.get("well")?.attr("Faces")?;let mut args516=Vec::new();let mut kw517=Vec::new();fun518.call(args516,kw517)?}}.iter()? {e.set("mate",item515)?;if {let v528={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun521={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun524=e.get("mate")?.attr("normalAt")?;let mut args522=Vec::new();let mut kw523=Vec::new();fun524.call(args522,kw523)?}}.attr("dot")?;let mut args519=Vec::new();let mut kw520=Vec::new();args519.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun527=e.get("face")?.attr("normalAt")?;let mut args525=Vec::new();let mut kw526=Vec::new();fun527.call(args525,kw526)?}});fun521.call(args519,kw520)?}};let v529=binary("sub",Val::Float(1.0f64),Val::Float(1e-06f64))?;Val::Bool(compare("gt",v528.clone(),v529.clone())?.truthy()?)}.truthy()? {out514.attr("append")?.call(vec![e.get("mate")?],vec![])?;}}out514};e.set("mates",assigned513.clone())?;
let assigned530={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun533=e.get("min")?;let mut args531=Vec::new();let mut kw532=Vec::new();args531.push({let e=e.child();let out534=Val::list(vec![]);for item535 in e.get("mates")?.iter()? {e.set("mate",item535)?;out534.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun538=e.get("face")?.attr("distance")?;let mut args536=Vec::new();let mut kw537=Vec::new();args536.push(e.get("mate")?);fun538.call(args536,kw537)?}}],vec![])?;}out534});kw532.push(("default".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun541=e.get("float")?;let mut args539=Vec::new();let mut kw540=Vec::new();args539.push(Val::Str("inf".into()));fun541.call(args539,kw540)?}}));fun533.call(args531,kw532)?}};e.set("gap",assigned530.clone())?;
let assigned542=binary("truediv",e.get("fitted_air")?,binary("pow",Val::Float(2.0f64),Val::Float(0.5f64))?)?;e.set("expected_gap",assigned542.clone())?;
if {let v546={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun545=e.get("abs")?;let mut args543=Vec::new();let mut kw544=Vec::new();args543.push(binary("sub",e.get("gap")?,e.get("expected_gap")?)?);fun545.call(args543,kw544)?}};let v547=Val::Float(1e-06f64);Val::Bool(compare("gt",v546.clone(),v547.clone())?.truthy()?)}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun550=e.get("fails")?.attr("append")?;let mut args548=Vec::new();let mut kw549=Vec::new();args548.push({let mut str551=String::new();str551.push_str("the lower pump flank has ");str551.push_str(&format(&e.get("gap")?,&val_string({let mut str552=String::new();str552.push_str(".6f");Val::Str(str552)})?)?);str551.push_str(" mm normal air, expected the fitted profile's ");str551.push_str(&format(&e.get("expected_gap")?,&val_string({let mut str553=String::new();str553.push_str(".6f");Val::Str(str553)})?)?);Val::Str(str551)});fun550.call(args548,kw549)?}};
}
}
Ok(Flow::Continue)})();let outcome452=(||->Result<Flow>{match attempt451{Ok(Flow::Return(value))=>Ok(Flow::Return(value)),Ok(Flow::Continue)=>{Ok(Flow::Continue)},Err(error)=>{e.set("exc",Val::Str(error.to_string()))?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun556=e.get("fails")?.attr("append")?;let mut args554=Vec::new();let mut kw555=Vec::new();args554.push({let mut str557=String::new();str557.push_str("lower pump flank clearance: ");str557.push_str(&format(&e.get("exc")?,&String::new())?);Val::Str(str557)});fun556.call(args554,kw555)?}};
Ok(Flow::Continue)}}})();match outcome452?{Flow::Continue=>{},Flow::Return(value)=>return Ok(value)}
for item558 in e.get("fails")?.iter()? {
e.set("line",item558)?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun561=e.get("print")?;let mut args559=Vec::new();let mut kw560=Vec::new();args559.push({let mut str562=String::new();str562.push_str("FAIL ");str562.push_str(&format(&e.get("line")?,&String::new())?);Val::Str(str562)});fun561.call(args559,kw560)?}};
}
if unary("not",e.get("fails")?)?.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun565=e.get("print")?;let mut args563=Vec::new();let mut kw564=Vec::new();args563.push({let mut str566=String::new();str566.push_str("ok  pump-tray  ");str566.push_str(&format(&binary("mul",Val::Int(2i64),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_tray.rs",line!());{let fun569=e.get("half_width")?;let mut args567=Vec::new();let mut kw568=Vec::new();fun569.call(args567,kw568)?}})?,&val_string({let mut str570=String::new();str570.push_str("g");Val::Str(str570)})?)?);str566.push_str(" across, ");str566.push_str(&format(&e.get("SHOULDER")?,&val_string({let mut str571=String::new();str571.push_str("g");Val::Str(str571)})?)?);str566.push_str(" of shoulder over ");str566.push_str(&format(&e.get("boss_depth")?,&val_string({let mut str572=String::new();str572.push_str("g");Val::Str(str572)})?)?);str566.push_str(" of bore, octagon ");str566.push_str(&format(&binary("mul",Val::Int(2i64),e.get("boss_half")?)?,&val_string({let mut str573=String::new();str573.push_str("g");Val::Str(str573)})?)?);str566.push_str(" at the flats, can bore ");str566.push_str(&format(&binary("mul",Val::Int(2i64),e.get("can_half")?)?,&val_string({let mut str574=String::new();str574.push_str("g");Val::Str(str574)})?)?);str566.push_str(", clear of a ");str566.push_str(&format(&binary("mul",Val::Int(2i64),e.get("bracket_half")?)?,&val_string({let mut str575=String::new();str575.push_str("g");Val::Str(str575)})?)?);str566.push_str(" bracket, ");str566.push_str(&format(&e.get("on_head")?,&val_string({let mut str576=String::new();str576.push_str(".0f");Val::Str(str576)})?)?);str566.push_str(" mm² on the head and ");str566.push_str(&format(&e.get("on_crown")?,&val_string({let mut str577=String::new();str577.push_str(".0f");Val::Str(str577)})?)?);str566.push_str(" on the crown");Val::Str(str566)});fun565.call(args563,kw564)?}};
}
return Ok(if e.get("fails")?.truthy()? {Val::Int(1i64)} else {Val::Int(0i64)});
Ok(Val::None)})})?;
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
            let assigned578 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun581 = e.get("trays_of_machine")?;
                    let mut args579 = Vec::new();
                    let mut kw580 = Vec::new();
                    args579.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun584 = e.get("_facts")?.attr("read")?;
                            let mut args582 = Vec::new();
                            let mut kw583 = Vec::new();
                            fun584.call(args582, kw583)?
                        }
                    });
                    fun581.call(args579, kw580)?
                }
            };
            e.set("trays", assigned578.clone())?;
            let assigned585 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun588 = e.get("_rust_part")?.attr("check")?;
                    let mut args586 = Vec::new();
                    let mut kw587 = Vec::new();
                    args586.push(Val::Str("enclosure-components".into()));
                    args586.push(Val::Str("pump-tray".into()));
                    args586.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun591 = e.get("numbers")?;
                            let mut args589 = Vec::new();
                            let mut kw590 = Vec::new();
                            args589.push(e.get("trays")?);
                            fun591.call(args589, kw590)?
                        }
                    });
                    fun588.call(args586, kw587)?
                }
            };
            e.set("measured", assigned585.clone())?;
            let assigned592 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun595 = e.get("_data")?;
                    let mut args593 = Vec::new();
                    let mut kw594 = Vec::new();
                    args593.push(Val::Str("report".into()));
                    kw594.push(("trays".into(), e.get("trays")?));
                    kw594.push(("measured".into(), e.get("measured")?));
                    fun595.call(args593, kw594)?
                }
            };
            e.set("report", assigned592.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun598 = e.get("print")?;
                    let mut args596 = Vec::new();
                    let mut kw597 = Vec::new();
                    args596.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                            line!(),
                        );
                        {
                            let fun601 = Val::Str("\n".into()).attr("join")?;
                            let mut args599 = Vec::new();
                            let mut kw600 = Vec::new();
                            args599.push(e.get("report")?.get(Val::Str("lines".into()))?);
                            fun601.call(args599, kw600)?
                        }
                    });
                    fun598.call(args596, kw597)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun604 = e.get("substitute_md")?;
                    let mut args602 = Vec::new();
                    let mut kw603 = Vec::new();
                    args602.push(binary(
                        "truediv",
                        e.get("_here")?.attr("parent")?,
                        Val::Str("README.md".into()),
                    )?);
                    kw603.push((
                        "variables".into(),
                        e.get("report")?.get(Val::Str("variables".into()))?,
                    ));
                    fun604.call(args602, kw603)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun607 = e.get("print")?;
                    let mut args605 = Vec::new();
                    let mut kw606 = Vec::new();
                    args605.push(Val::Str("-> README.md".into()));
                    fun607.call(args605, kw606)?
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
            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
            line!(),
        );
        {
            let fun610 = e.get("_rust_part")?.attr("start")?;
            let mut args608 = Vec::new();
            let mut kw609 = Vec::new();
            fun610.call(args608, kw609)?
        }
    };
    if {
        let v613 = {
            let v617 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                    line!(),
                );
                {
                    let fun616 = e.get("len")?;
                    let mut args614 = Vec::new();
                    let mut kw615 = Vec::new();
                    args614.push(e.get("sys")?.attr("argv")?);
                    fun616.call(args614, kw615)?
                }
            };
            let v618 = Val::Int(1i64);
            Val::Bool(compare("gt", v617.clone(), v618.clone())?.truthy()?)
        };
        if v613.truthy()? {
            {
                let v611 = e.get("sys")?.attr("argv")?.get(Val::Int(1i64))?;
                let v612 = Val::Str("selftest".into());
                Val::Bool(compare("eq", v611.clone(), v612.clone())?.truthy()?)
            }
        } else {
            v613
        }
    }
    .truthy()?
    {
        {
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                line!(),
            );
            {
                let fun621 = e.get("sys")?.attr("exit")?;
                let mut args619 = Vec::new();
                let mut kw620 = Vec::new();
                args619.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
                        line!(),
                    );
                    {
                        let fun624 = e.get("selftest")?;
                        let mut args622 = Vec::new();
                        let mut kw623 = Vec::new();
                        fun624.call(args622, kw623)?
                    }
                });
                fun621.call(args619, kw620)?
            }
        };
    }
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_tray.rs",
            line!(),
        );
        {
            let fun627 = e.get("main")?;
            let mut args625 = Vec::new();
            let mut kw626 = Vec::new();
            fun627.call(args625, kw626)?
        }
    };
    Ok(Val::None)
}
