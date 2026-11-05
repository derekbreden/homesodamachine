//! Pump case — two-piece enclosure for a peristaltic pump.
//!
//! Base: base plate with octagon-to-footprint ramp, octagon pump bore,
//!       and a cylindrical tower below.
//! Cap:  asymmetric flared skirt (wide on +Y, narrow on -Y) with a lower
//!       extension that tapers to uniform width.
//!
//! The two parts mate at a stepped split surface and lock together with
//! snap-fit ramps on four interior walls.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
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
    }
    .attr("parent")?;
    e.set("_here", assigned2.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
            line!(),
        );
        {
            let fun11 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args9 = Vec::new();
            let mut kw10 = Vec::new();
            args9.push(Val::Int(0i64));
            args9.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun14 = e.get("str")?;
                    let mut args12 = Vec::new();
                    let mut kw13 = Vec::new();
                    args12.push(binary(
                        "truediv",
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun17 = e.get("next")?;
                                let mut args15 = Vec::new();
                                let mut kw16 = Vec::new();
                                args15.push({
                                    let e = e.child();
                                    let out18 = Val::list(vec![]);
                                    for item19 in e.get("_here")?.attr("parents")?.iter()? {
                                        e.set("p", item19)?;
                                        if {
                                            let v20 = e.get("p")?.attr("name")?;
                                            let v21 = Val::Str("printed-parts".into());
                                            Val::Bool(
                                                compare("eq", v20.clone(), v21.clone())?
                                                    .truthy()?,
                                            )
                                        }
                                        .truthy()?
                                        {
                                            out18
                                                .attr("append")?
                                                .call(vec![e.get("p")?], vec![])?;
                                        }
                                    }
                                    out18
                                });
                                fun17.call(args15, kw16)?
                            }
                        },
                        Val::Str("cadlib".into()),
                    )?);
                    fun14.call(args12, kw13)?
                }
            });
            fun11.call(args9, kw10)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
            line!(),
        );
        {
            let fun24 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args22 = Vec::new();
            let mut kw23 = Vec::new();
            args22.push(Val::Int(0i64));
            args22.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun27 = e.get("str")?;
                    let mut args25 = Vec::new();
                    let mut kw26 = Vec::new();
                    args25.push(binary(
                        "truediv",
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun30 = e.get("next")?;
                                let mut args28 = Vec::new();
                                let mut kw29 = Vec::new();
                                args28.push({
                                    let e = e.child();
                                    let out31 = Val::list(vec![]);
                                    for item32 in e.get("_here")?.attr("parents")?.iter()? {
                                        e.set("p", item32)?;
                                        if {
                                            let v33 = e.get("p")?.attr("name")?;
                                            let v34 = Val::Str("hardware".into());
                                            Val::Bool(
                                                compare("eq", v33.clone(), v34.clone())?
                                                    .truthy()?,
                                            )
                                        }
                                        .truthy()?
                                        {
                                            out31
                                                .attr("append")?
                                                .call(vec![e.get("p")?], vec![])?;
                                        }
                                    }
                                    out31
                                });
                                fun30.call(args28, kw29)?
                            }
                        },
                        Val::Str("scripts".into()),
                    )?);
                    fun27.call(args25, kw26)?
                }
            });
            fun24.call(args22, kw23)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
            line!(),
        );
        {
            let fun37 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args35 = Vec::new();
            let mut kw36 = Vec::new();
            args35.push(Val::Int(0i64));
            args35.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun40=e.get("str")?;let mut args38=Vec::new();let mut kw39=Vec::new();args38.push(binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun43=e.get("next")?;let mut args41=Vec::new();let mut kw42=Vec::new();args41.push({let e=e.child();let out44=Val::list(vec![]);for item45 in e.get("_here")?.attr("parents")?.iter()? {e.set("p",item45)?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun48=binary("truediv",binary("truediv",e.get("p")?,Val::Str("tools".into()))?,Val::Str("docgen".into()))?.attr("is_dir")?;let mut args46=Vec::new();let mut kw47=Vec::new();fun48.call(args46,kw47)?}}.truthy()? {out44.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out44});fun43.call(args41,kw42)?}},Val::Str("tools".into()))?);fun40.call(args38,kw39)?}});
            fun37.call(args35, kw36)?
        }
    };
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod49 = rt.import_module("world_workplane")?;
    e.set(
        "WorldWorkplane",
        rt.member("world_workplane", "WorldWorkplane")?,
    )?;
    e.set(
        "xy_plane_z_up",
        rt.member("world_workplane", "xy_plane_z_up")?,
    )?;
    e.set(
        "xz_plane_y_up",
        rt.member("world_workplane", "xz_plane_y_up")?,
    )?;
    let mod50 = rt.import_module("snap")?;
    e.set("Frame", rt.member("snap", "Frame")?)?;
    e.set(
        "apply_ramp_out_first",
        rt.member("snap", "apply_ramp_out_first")?,
    )?;
    e.set(
        "apply_ramp_in_first",
        rt.member("snap", "apply_ramp_in_first")?,
    )?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
            line!(),
        );
        {
            let fun54 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args52 = Vec::new();
            let mut kw53 = Vec::new();
            args52.push(Val::Int(0i64));
            args52.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun57 = e.get("str")?;
                    let mut args55 = Vec::new();
                    let mut kw56 = Vec::new();
                    args55.push(binary(
                        "truediv",
                        e.get("_here")?.attr("parent")?,
                        Val::Str("enclosure".into()),
                    )?);
                    fun57.call(args55, kw56)?
                }
            });
            fun54.call(args52, kw53)?
        }
    };
    let mod58 = rt.import_module("_enclosure_data")?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    let assigned59 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
            line!(),
        );
        {
            let fun62 = e.get("_read")?;
            let mut args60 = Vec::new();
            let mut kw61 = Vec::new();
            args60.push(Val::Str("pump-case-defaults".into()));
            fun62.call(args60, kw61)?
        }
    };
    e.set("_case", assigned59.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
            line!(),
        );
        {
            let fun65 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun68 = e.get("globals")?;
                    let mut args66 = Vec::new();
                    let mut kw67 = Vec::new();
                    fun68.call(args66, kw67)?
                }
            }
            .attr("update")?;
            let mut args63 = Vec::new();
            let mut kw64 = Vec::new();
            args63.push(e.get("_case")?);
            fun65.call(args63, kw64)?
        }
    };
    // bore_octagon_profile
    e.set("bore_octagon_profile", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out69 = Val::list(vec![]);
                for item70 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun73 = e.get("_read")?;
                        let mut args71 = Vec::new();
                        let mut kw72 = Vec::new();
                        args71.push(Val::Str("pump-case-bore".into()));
                        kw72.push(("case".into(), e.get("_case")?));
                        fun73.call(args71, kw72)?
                    }
                }
                .iter()?
                {
                    e.set("p", item70)?;
                    out69.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun76 = e.get("tuple")?;
                                let mut args74 = Vec::new();
                                let mut kw75 = Vec::new();
                                args74.push(e.get("p")?);
                                fun76.call(args74, kw75)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out69
            });
            Ok(Val::None)
        })
    })?;
    // _ring
    e.set("_ring", {
        let params = vec![("section".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out77 = Val::list(vec![]);
                for item78 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun81 = e.get("_read")?;
                        let mut args79 = Vec::new();
                        let mut kw80 = Vec::new();
                        args79.push(Val::Str("pump-case-ring".into()));
                        kw80.push(("points".into(), {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun84 = e.get("list")?;
                                let mut args82 = Vec::new();
                                let mut kw83 = Vec::new();
                                args82.push(e.get("section")?);
                                fun84.call(args82, kw83)?
                            }
                        }));
                        fun81.call(args79, kw80)?
                    }
                }
                .iter()?
                {
                    e.set("p", item78)?;
                    out77.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun87 = e.get("tuple")?;
                                let mut args85 = Vec::new();
                                let mut kw86 = Vec::new();
                                args85.push(e.get("p")?);
                                fun87.call(args85, kw86)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out77
            });
            Ok(Val::None)
        })
    })?;
    // offset_polygon
    e.set("offset_polygon", {
        let params = vec![
            ("pts".into(), None, false),
            ("distance".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out88 = Val::list(vec![]);
                for item89 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun92 = e.get("_read")?;
                        let mut args90 = Vec::new();
                        let mut kw91 = Vec::new();
                        args90.push(Val::Str("pump-case-offset".into()));
                        kw91.push(("points".into(), e.get("pts")?));
                        kw91.push(("distance".into(), e.get("distance")?));
                        fun92.call(args90, kw91)?
                    }
                }
                .iter()?
                {
                    e.set("p", item89)?;
                    out88.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun95 = e.get("tuple")?;
                                let mut args93 = Vec::new();
                                let mut kw94 = Vec::new();
                                args93.push(e.get("p")?);
                                fun95.call(args93, kw94)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out88
            });
            Ok(Val::None)
        })
    })?;
    // rounded_rect_profile
    e.set("rounded_rect_profile", {
        let params = vec![
            ("width".into(), None, false),
            ("height".into(), None, false),
            ("radius".into(), None, false),
            ("n".into(), Some(e.get("arc_segments")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out96 = Val::list(vec![]);
                for item97 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun100 = e.get("_read")?;
                        let mut args98 = Vec::new();
                        let mut kw99 = Vec::new();
                        args98.push(Val::Str("pump-case-rounded".into()));
                        kw99.push(("width".into(), e.get("width")?));
                        kw99.push(("height".into(), e.get("height")?));
                        kw99.push(("radius".into(), e.get("radius")?));
                        kw99.push(("n".into(), e.get("n")?));
                        fun100.call(args98, kw99)?
                    }
                }
                .iter()?
                {
                    e.set("p", item97)?;
                    out96.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun103 = e.get("tuple")?;
                                let mut args101 = Vec::new();
                                let mut kw102 = Vec::new();
                                args101.push(e.get("p")?);
                                fun103.call(args101, kw102)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out96
            });
            Ok(Val::None)
        })
    })?;
    // split_skirt_profile
    e.set("split_skirt_profile", {
        let params = vec![
            ("wide_half_extent".into(), None, false),
            ("wide_radius".into(), None, false),
            ("narrow_half_extent".into(), None, false),
            ("narrow_radius".into(), None, false),
            ("transition_y_plus".into(), Some(Val::None), false),
            ("transition_y_minus".into(), Some(Val::None), false),
            ("wide_half_extent_y".into(), Some(Val::None), false),
            ("narrow_half_extent_y".into(), Some(Val::None), false),
            ("n".into(), Some(e.get("arc_segments")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out104 = Val::list(vec![]);
                for item105 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun108 = e.get("_read")?;
                        let mut args106 = Vec::new();
                        let mut kw107 = Vec::new();
                        args106.push(Val::Str("pump-case-split".into()));
                        kw107.push(("wide_half_extent".into(), e.get("wide_half_extent")?));
                        kw107.push(("wide_radius".into(), e.get("wide_radius")?));
                        kw107.push(("narrow_half_extent".into(), e.get("narrow_half_extent")?));
                        kw107.push(("narrow_radius".into(), e.get("narrow_radius")?));
                        kw107.push(("transition_y_plus".into(), e.get("transition_y_plus")?));
                        kw107.push(("transition_y_minus".into(), e.get("transition_y_minus")?));
                        kw107.push(("wide_half_extent_y".into(), e.get("wide_half_extent_y")?));
                        kw107.push((
                            "narrow_half_extent_y".into(),
                            e.get("narrow_half_extent_y")?,
                        ));
                        kw107.push(("n".into(), e.get("n")?));
                        fun108.call(args106, kw107)?
                    }
                }
                .iter()?
                {
                    e.set("p", item105)?;
                    out104.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun111 = e.get("tuple")?;
                                let mut args109 = Vec::new();
                                let mut kw110 = Vec::new();
                                args109.push(e.get("p")?);
                                fun111.call(args109, kw110)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out104
            });
            Ok(Val::None)
        })
    })?;
    // _skirt_profile_set
    e.set("_skirt_profile_set", {
        let params = vec![("wall_offset".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out112 = Val::list(vec![]);
                for item113 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun116 = e.get("_read")?;
                        let mut args114 = Vec::new();
                        let mut kw115 = Vec::new();
                        args114.push(Val::Str("pump-case-skirt-set".into()));
                        kw115.push(("case".into(), e.get("_case")?));
                        kw115.push(("wall_offset".into(), e.get("wall_offset")?));
                        fun116.call(args114, kw115)?
                    }
                }
                .iter()?
                {
                    e.set("section", item113)?;
                    out112.attr("append")?.call(
                        vec![{
                            let e = e.child();
                            let out117 = Val::list(vec![]);
                            for item118 in e.get("section")?.iter()? {
                                e.set("p", item118)?;
                                out117.attr("append")?.call(
                                    vec![{
                                        let _site = rt.source_at(
                                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                            line!(),
                                        );
                                        {
                                            let fun121 = e.get("tuple")?;
                                            let mut args119 = Vec::new();
                                            let mut kw120 = Vec::new();
                                            args119.push(e.get("p")?);
                                            fun121.call(args119, kw120)?
                                        }
                                    }],
                                    vec![],
                                )?;
                            }
                            out117
                        }],
                        vec![],
                    )?;
                }
                out112
            });
            Ok(Val::None)
        })
    })?;
    // build_base_plate_with_ramp
    e.set("build_base_plate_with_ramp",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned122={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun125=e.get("rounded_rect_profile")?;let mut args123=Vec::new();let mut kw124=Vec::new();args123.push(e.get("footprint_x")?);args123.push(e.get("footprint_y")?);args123.push(e.get("corner_r")?);fun125.call(args123,kw124)?}};e.set("footprint",assigned122.clone())?;
let assigned126={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun129=e.get("rounded_rect_profile")?;let mut args127=Vec::new();let mut kw128=Vec::new();args127.push(binary("sub",e.get("footprint_x")?,binary("mul",Val::Int(2i64),e.get("ramp_from_skirt_to_octagon_height")?)?)?);args127.push(binary("sub",e.get("footprint_y")?,binary("mul",Val::Int(2i64),e.get("ramp_from_skirt_to_octagon_height")?)?)?);args127.push(e.get("corner_r")?);fun129.call(args127,kw128)?}};e.set("footprint_at_ramp_bottom",assigned126.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun132={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun135={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun138={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun141={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun144={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun147={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun150={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun153={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun156={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun159={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun162={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun165=e.get("WorldWorkplane")?;let mut args163=Vec::new();let mut kw164=Vec::new();args163.push(e.get("xy_plane_z_up")?);fun165.call(args163,kw164)?}}.attr("workplane")?;let mut args160=Vec::new();let mut kw161=Vec::new();kw161.push(("offset".into(),Val::Int(0i64)));fun162.call(args160,kw161)?}}.attr("center")?;let mut args157=Vec::new();let mut kw158=Vec::new();args157.push(e.get("center_x")?);args157.push(e.get("center_y")?);fun159.call(args157,kw158)?}}.attr("polyline")?;let mut args154=Vec::new();let mut kw155=Vec::new();args154.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun168=e.get("_ring")?;let mut args166=Vec::new();let mut kw167=Vec::new();args166.push(e.get("footprint")?);fun168.call(args166,kw167)?}});fun156.call(args154,kw155)?}}.attr("wire")?;let mut args151=Vec::new();let mut kw152=Vec::new();fun153.call(args151,kw152)?}}.attr("workplane")?;let mut args148=Vec::new();let mut kw149=Vec::new();kw149.push(("offset".into(),e.get("base_thickness")?));fun150.call(args148,kw149)?}}.attr("polyline")?;let mut args145=Vec::new();let mut kw146=Vec::new();args145.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun171=e.get("_ring")?;let mut args169=Vec::new();let mut kw170=Vec::new();args169.push(e.get("footprint")?);fun171.call(args169,kw170)?}});fun147.call(args145,kw146)?}}.attr("wire")?;let mut args142=Vec::new();let mut kw143=Vec::new();fun144.call(args142,kw143)?}}.attr("workplane")?;let mut args139=Vec::new();let mut kw140=Vec::new();kw140.push(("offset".into(),e.get("ramp_from_skirt_to_octagon_height")?));fun141.call(args139,kw140)?}}.attr("polyline")?;let mut args136=Vec::new();let mut kw137=Vec::new();args136.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun174=e.get("_ring")?;let mut args172=Vec::new();let mut kw173=Vec::new();args172.push(e.get("footprint_at_ramp_bottom")?);fun174.call(args172,kw173)?}});fun138.call(args136,kw137)?}}.attr("wire")?;let mut args133=Vec::new();let mut kw134=Vec::new();fun135.call(args133,kw134)?}}.attr("loft")?;let mut args130=Vec::new();let mut kw131=Vec::new();kw131.push(("ruled".into(),Val::Bool(true)));fun132.call(args130,kw131)?}});
Ok(Val::None)})})?;
    // add_bore_wall
    e.set("add_bore_wall",{let params=vec![("solid".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned175={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun178={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun181={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun184={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun187={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun190={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun193=e.get("WorldWorkplane")?;let mut args191=Vec::new();let mut kw192=Vec::new();args191.push(e.get("xy_plane_z_up")?);fun193.call(args191,kw192)?}}.attr("workplane")?;let mut args188=Vec::new();let mut kw189=Vec::new();kw189.push(("offset".into(),Val::Int(0i64)));fun190.call(args188,kw189)?}}.attr("center")?;let mut args185=Vec::new();let mut kw186=Vec::new();args185.push(e.get("center_x")?);args185.push(e.get("center_y")?);fun187.call(args185,kw186)?}}.attr("polyline")?;let mut args182=Vec::new();let mut kw183=Vec::new();args182.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun196=e.get("_ring")?;let mut args194=Vec::new();let mut kw195=Vec::new();args194.push(e.get("bore_wall_profile")?);fun196.call(args194,kw195)?}});fun184.call(args182,kw183)?}}.attr("wire")?;let mut args179=Vec::new();let mut kw180=Vec::new();fun181.call(args179,kw180)?}}.attr("extrude")?;let mut args176=Vec::new();let mut kw177=Vec::new();args176.push(e.get("bore_depth")?);fun178.call(args176,kw177)?}};e.set("bore_wall",assigned175.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun199=e.get("solid")?.attr("union")?;let mut args197=Vec::new();let mut kw198=Vec::new();args197.push(e.get("bore_wall")?);fun199.call(args197,kw198)?}});
Ok(Val::None)})})?;
    // cut_bore_cavity
    e.set("cut_bore_cavity",{let params=vec![("solid".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned200={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun203={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun206={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun209={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun212={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun215={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun218=e.get("WorldWorkplane")?;let mut args216=Vec::new();let mut kw217=Vec::new();args216.push(e.get("xy_plane_z_up")?);fun218.call(args216,kw217)?}}.attr("workplane")?;let mut args213=Vec::new();let mut kw214=Vec::new();kw214.push(("offset".into(),Val::Int(0i64)));fun215.call(args213,kw214)?}}.attr("center")?;let mut args210=Vec::new();let mut kw211=Vec::new();args210.push(e.get("center_x")?);args210.push(e.get("center_y")?);fun212.call(args210,kw211)?}}.attr("polyline")?;let mut args207=Vec::new();let mut kw208=Vec::new();args207.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun221=e.get("_ring")?;let mut args219=Vec::new();let mut kw220=Vec::new();args219.push(e.get("bore_profile")?);fun221.call(args219,kw220)?}});fun209.call(args207,kw208)?}}.attr("wire")?;let mut args204=Vec::new();let mut kw205=Vec::new();fun206.call(args204,kw205)?}}.attr("extrude")?;let mut args201=Vec::new();let mut kw202=Vec::new();args201.push(binary("add",e.get("bore_depth")?,e.get("overcut")?)?);fun203.call(args201,kw202)?}};e.set("bore_cavity",assigned200.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun224=e.get("solid")?.attr("cut")?;let mut args222=Vec::new();let mut kw223=Vec::new();args222.push(e.get("bore_cavity")?);fun224.call(args222,kw223)?}});
Ok(Val::None)})})?;
    // loft_profile_stack
    e.set("loft_profile_stack",{let params=vec![("start_world_z".into(),None,false),("z_steps".into(),None,false),("profiles".into(),None,false),("overcut_last_step".into(),Some(Val::Bool(false)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let v231={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun227=e.get("len")?;let mut args225=Vec::new();let mut kw226=Vec::new();args225.push(e.get("profiles")?);fun227.call(args225,kw226)?}};let v232=binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun230=e.get("len")?;let mut args228=Vec::new();let mut kw229=Vec::new();args228.push(e.get("z_steps")?);fun230.call(args228,kw229)?}},Val::Int(1i64))?;Val::Bool(compare("ne",v231.clone(),v232.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun235=e.get("ValueError")?;let mut args233=Vec::new();let mut kw234=Vec::new();args233.push(Val::Str("a profile stack needs one more outline than Z steps".into()));fun235.call(args233,kw234)?}})?);
}
let assigned236={let mut s=Vec::new();Val::list(s)};e.set("levels",assigned236.clone())?;
let assigned237=e.get("start_world_z")?;e.set("z",assigned237.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun240=e.get("levels")?.attr("append")?;let mut args238=Vec::new();let mut kw239=Vec::new();args238.push({let e=e.child();let out241=Val::list(vec![]);for item242 in e.get("profiles")?.get(Val::Int(0i64))?.iter()? {let unpack243=unpack(item242,2)?;e.set("x",unpack243[0].clone())?;e.set("y",unpack243[1].clone())?;out241.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun246=e.get("cq")?.attr("Vector")?;let mut args244=Vec::new();let mut kw245=Vec::new();args244.push(binary("add",e.get("center_x")?,e.get("x")?)?);args244.push(binary("add",e.get("center_y")?,e.get("y")?)?);args244.push(e.get("z")?);fun246.call(args244,kw245)?}}],vec![])?;}out241});fun240.call(args238,kw239)?}};
for item247 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun250=e.get("enumerate")?;let mut args248=Vec::new();let mut kw249=Vec::new();args248.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun253=e.get("zip")?;let mut args251=Vec::new();let mut kw252=Vec::new();args251.push(e.get("z_steps")?);args251.push(e.get("profiles")?.get(Val::Slice{start:Some(Val::Int(1i64).integer()?),stop:None,step:1})?);fun253.call(args251,kw252)?}});fun250.call(args248,kw249)?}}.iter()? {
let unpack254=unpack(item247,2)?;e.set("i",unpack254[0].clone())?;let unpack255=unpack(unpack254[1].clone(),2)?;e.set("step",unpack255[0].clone())?;e.set("profile",unpack255[1].clone())?;let assigned256={let v260=e.get("i")?;let v261=binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun259=e.get("len")?;let mut args257=Vec::new();let mut kw258=Vec::new();args257.push(e.get("z_steps")?);fun259.call(args257,kw258)?}},Val::Int(1i64))?;Val::Bool(compare("eq",v260.clone(),v261.clone())?.truthy()?)};e.set("is_last",assigned256.clone())?;
let assigned262=if {let v263=e.get("overcut_last_step")?;if v263.truthy()? {e.get("is_last")?} else {v263}}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun266=e.get("math")?.attr("copysign")?;let mut args264=Vec::new();let mut kw265=Vec::new();args264.push(e.get("overcut")?);args264.push(e.get("step")?);fun266.call(args264,kw265)?}}} else {Val::Int(0i64)};e.set("extra",assigned262.clone())?;
e.set("z",binary("add",e.get("z")?,binary("add",e.get("step")?,e.get("extra")?)?)?)?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun269=e.get("levels")?.attr("append")?;let mut args267=Vec::new();let mut kw268=Vec::new();args267.push({let e=e.child();let out270=Val::list(vec![]);for item271 in e.get("profile")?.iter()? {let unpack272=unpack(item271,2)?;e.set("x",unpack272[0].clone())?;e.set("y",unpack272[1].clone())?;out270.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun275=e.get("cq")?.attr("Vector")?;let mut args273=Vec::new();let mut kw274=Vec::new();args273.push(binary("add",e.get("center_x")?,e.get("x")?)?);args273.push(binary("add",e.get("center_y")?,e.get("y")?)?);args273.push(e.get("z")?);fun275.call(args273,kw274)?}}],vec![])?;}out270});fun269.call(args267,kw268)?}};
}
// closed_wire
e.set("closed_wire",{let params=vec![("points".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun278=e.get("cq")?.attr("Wire")?.attr("makePolygon")?;let mut args276=Vec::new();let mut kw277=Vec::new();args276.push(e.get("points")?);kw277.push(("close".into(),Val::Bool(true)));fun278.call(args276,kw277)?}});
Ok(Val::None)})})?;
let assigned279={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun282=e.get("cq")?.attr("Face")?.attr("makeFromWires")?;let mut args280=Vec::new();let mut kw281=Vec::new();args280.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun285=e.get("closed_wire")?;let mut args283=Vec::new();let mut kw284=Vec::new();args283.push(e.get("levels")?.get(Val::Int(0i64))?);fun285.call(args283,kw284)?}});fun282.call(args280,kw281)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun288=e.get("cq")?.attr("Face")?.attr("makeFromWires")?;let mut args286=Vec::new();let mut kw287=Vec::new();args286.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun291=e.get("closed_wire")?;let mut args289=Vec::new();let mut kw290=Vec::new();args289.push(e.get("levels")?.get(unary("neg",Val::Int(1i64))?)?);fun291.call(args289,kw290)?}});fun288.call(args286,kw287)?}});Val::list(s)};e.set("faces",assigned279.clone())?;
let assigned292=binary("add",binary("mul",Val::Int(4i64),binary("add",e.get("arc_segments")?,Val::Int(1i64))?)?,Val::Int(2i64))?;e.set("collapsed_count",assigned292.clone())?;
let assigned293=binary("add",e.get("collapsed_count")?,Val::Int(2i64))?;e.set("split_count",assigned293.clone())?;
let assigned294=binary("mul",Val::Int(2i64),binary("add",e.get("arc_segments")?,Val::Int(1i64))?)?;e.set("collapse_i",assigned294.clone())?;
// aligned
e.set("aligned",{let params=vec![("points".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let v298={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun297=e.get("len")?;let mut args295=Vec::new();let mut kw296=Vec::new();args295.push(e.get("points")?);fun297.call(args295,kw296)?}};let v299=e.get("split_count")?;Val::Bool(compare("eq",v298.clone(),v299.clone())?.truthy()?)}.truthy()? {
return Ok(e.get("points")?);
}
if {let v303={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun302=e.get("len")?;let mut args300=Vec::new();let mut kw301=Vec::new();args300.push(e.get("points")?);fun302.call(args300,kw301)?}};let v304=e.get("collapsed_count")?;Val::Bool(compare("ne",v303.clone(),v304.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun307=e.get("ValueError")?;let mut args305=Vec::new();let mut kw306=Vec::new();args305.push({let mut str308=String::new();str308.push_str("a skirt outline has ");str308.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun311=e.get("len")?;let mut args309=Vec::new();let mut kw310=Vec::new();args309.push(e.get("points")?);fun311.call(args309,kw310)?}},&String::new())?);str308.push_str(" vertices, expected ");str308.push_str(&format(&e.get("collapsed_count")?,&String::new())?);str308.push_str(" collapsed or ");str308.push_str(&format(&e.get("split_count")?,&String::new())?);str308.push_str(" split");Val::Str(str308)});fun307.call(args305,kw306)?}})?);
}
return Ok(binary("add",binary("add",binary("add",e.get("points")?.get(Val::Slice{start:None,stop:Some(binary("add",e.get("collapse_i")?,Val::Int(1i64))?.integer()?),step:1})?,{let mut s=Vec::new();s.push(e.get("points")?.get(e.get("collapse_i")?)?);Val::list(s)})?,e.get("points")?.get(Val::Slice{start:Some(binary("add",e.get("collapse_i")?,Val::Int(1i64))?.integer()?),stop:None,step:1})?)?,{let mut s=Vec::new();s.push(e.get("points")?.get(unary("neg",Val::Int(1i64))?)?);Val::list(s)})?);
Ok(Val::None)})})?;
// side_face
e.set("side_face",{let params=vec![("a0".into(),None,false),("a1".into(),None,false),("b0".into(),None,false),("b1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let v312=binary("sub",e.get("a1")?,e.get("a0")?)?.attr("Length")?;let v313=Val::Float(1e-10f64);Val::Bool(compare("lt",v312.clone(),v313.clone())?.truthy()?)}.truthy()? {
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun316=e.get("cq")?.attr("Face")?.attr("makeFromWires")?;let mut args314=Vec::new();let mut kw315=Vec::new();args314.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun319=e.get("closed_wire")?;let mut args317=Vec::new();let mut kw318=Vec::new();args317.push({let mut s=Vec::new();s.push(e.get("a0")?);s.push(e.get("b0")?);s.push(e.get("b1")?);Val::tuple(s)});fun319.call(args317,kw318)?}});fun316.call(args314,kw315)?}});
}
if {let v320=binary("sub",e.get("b1")?,e.get("b0")?)?.attr("Length")?;let v321=Val::Float(1e-10f64);Val::Bool(compare("lt",v320.clone(),v321.clone())?.truthy()?)}.truthy()? {
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun324=e.get("cq")?.attr("Face")?.attr("makeFromWires")?;let mut args322=Vec::new();let mut kw323=Vec::new();args322.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun327=e.get("closed_wire")?;let mut args325=Vec::new();let mut kw326=Vec::new();args325.push({let mut s=Vec::new();s.push(e.get("a0")?);s.push(e.get("a1")?);s.push(e.get("b0")?);Val::tuple(s)});fun327.call(args325,kw326)?}});fun324.call(args322,kw323)?}});
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun330=e.get("cq")?.attr("Face")?.attr("makeRuledSurface")?;let mut args328=Vec::new();let mut kw329=Vec::new();args328.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun333=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args331=Vec::new();let mut kw332=Vec::new();args331.push(e.get("a0")?);args331.push(e.get("a1")?);fun333.call(args331,kw332)?}});args328.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun336=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args334=Vec::new();let mut kw335=Vec::new();args334.push(e.get("b0")?);args334.push(e.get("b1")?);fun336.call(args334,kw335)?}});fun330.call(args328,kw329)?}});
Ok(Val::None)})})?;
for item337 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun340=e.get("zip")?;let mut args338=Vec::new();let mut kw339=Vec::new();args338.push(e.get("levels")?);args338.push(e.get("levels")?.get(Val::Slice{start:Some(Val::Int(1i64).integer()?),stop:None,step:1})?);fun340.call(args338,kw339)?}}.iter()? {
let unpack341=unpack(item337,2)?;e.set("upper",unpack341[0].clone())?;e.set("lower",unpack341[1].clone())?;let assigned342={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun345=e.get("aligned")?;let mut args343=Vec::new();let mut kw344=Vec::new();args343.push(e.get("upper")?);fun345.call(args343,kw344)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun348=e.get("aligned")?;let mut args346=Vec::new();let mut kw347=Vec::new();args346.push(e.get("lower")?);fun348.call(args346,kw347)?}});Val::tuple(s)};let unpack349=unpack(assigned342.clone(),2)?;e.set("a",unpack349[0].clone())?;e.set("b",unpack349[1].clone())?;
for item350 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun353=e.get("range")?;let mut args351=Vec::new();let mut kw352=Vec::new();args351.push(e.get("split_count")?);fun353.call(args351,kw352)?}}.iter()? {
e.set("i",item350)?;let assigned354=binary("mod",binary("add",e.get("i")?,Val::Int(1i64))?,e.get("split_count")?)?;e.set("j",assigned354.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun357=e.get("faces")?.attr("append")?;let mut args355=Vec::new();let mut kw356=Vec::new();args355.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun360=e.get("side_face")?;let mut args358=Vec::new();let mut kw359=Vec::new();args358.push(e.get("a")?.get(e.get("i")?)?);args358.push(e.get("a")?.get(e.get("j")?)?);args358.push(e.get("b")?.get(e.get("i")?)?);args358.push(e.get("b")?.get(e.get("j")?)?);fun360.call(args358,kw359)?}});fun357.call(args355,kw356)?}};
}
}
let assigned361={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun364={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun367=e.get("cq")?.attr("Solid")?.attr("makeSolid")?;let mut args365=Vec::new();let mut kw366=Vec::new();args365.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun370=e.get("cq")?.attr("Shell")?.attr("makeShell")?;let mut args368=Vec::new();let mut kw369=Vec::new();args368.push(e.get("faces")?);fun370.call(args368,kw369)?}});fun367.call(args365,kw366)?}}.attr("fix")?;let mut args362=Vec::new();let mut kw363=Vec::new();fun364.call(args362,kw363)?}};e.set("solid",assigned361.clone())?;
if {let v379=unary("not",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun382=e.get("solid")?.attr("isValid")?;let mut args380=Vec::new();let mut kw381=Vec::new();fun382.call(args380,kw381)?}})?;if v379.truthy()? {v379} else {{let v377={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun373=e.get("len")?;let mut args371=Vec::new();let mut kw372=Vec::new();args371.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun376=e.get("solid")?.attr("Solids")?;let mut args374=Vec::new();let mut kw375=Vec::new();fun376.call(args374,kw375)?}});fun373.call(args371,kw372)?}};let v378=Val::Int(1i64);Val::Bool(compare("ne",v377.clone(),v378.clone())?.truthy()?)}}}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun385=e.get("ValueError")?;let mut args383=Vec::new();let mut kw384=Vec::new();args383.push(Val::Str("the exact skirt loft did not make one valid solid".into()));fun385.call(args383,kw384)?}})?);
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun388=e.get("WorldWorkplane")?;let mut args386=Vec::new();let mut kw387=Vec::new();args386.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun391=e.get("cq")?.attr("Workplane")?;let mut args389=Vec::new();let mut kw390=Vec::new();kw390.push(("obj".into(),e.get("solid")?));fun391.call(args389,kw390)?}});fun388.call(args386,kw387)?}});
Ok(Val::None)})})?;
    // build_skirt
    e.set("build_skirt", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned392 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun395 = e.get("loft_profile_stack")?;
                    let mut args393 = Vec::new();
                    let mut kw394 = Vec::new();
                    args393.push(Val::Int(0i64));
                    args393.push(e.get("skirt_z_steps")?);
                    args393.push(e.get("skirt_outer_profiles")?);
                    fun395.call(args393, kw394)?
                }
            };
            e.set("skirt_outer", assigned392.clone())?;
            let assigned396 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun399 = e.get("loft_profile_stack")?;
                    let mut args397 = Vec::new();
                    let mut kw398 = Vec::new();
                    args397.push(Val::Int(0i64));
                    args397.push(e.get("skirt_z_steps")?);
                    args397.push(e.get("skirt_inner_profiles")?);
                    kw398.push(("overcut_last_step".into(), Val::Bool(true)));
                    fun399.call(args397, kw398)?
                }
            };
            e.set("skirt_cavity", assigned396.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun402 = e.get("skirt_outer")?.attr("cut")?;
                    let mut args400 = Vec::new();
                    let mut kw401 = Vec::new();
                    args400.push(e.get("skirt_cavity")?);
                    fun402.call(args400, kw401)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // build_tower
    e.set("build_tower",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned403={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun406={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun409={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun412={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun415={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun418=e.get("WorldWorkplane")?;let mut args416=Vec::new();let mut kw417=Vec::new();args416.push(e.get("xy_plane_z_up")?);fun418.call(args416,kw417)?}}.attr("workplane")?;let mut args413=Vec::new();let mut kw414=Vec::new();kw414.push(("offset".into(),e.get("cylinder_top_z")?));fun415.call(args413,kw414)?}}.attr("center")?;let mut args410=Vec::new();let mut kw411=Vec::new();args410.push(e.get("center_x")?);args410.push(e.get("center_y")?);fun412.call(args410,kw411)?}}.attr("circle")?;let mut args407=Vec::new();let mut kw408=Vec::new();args407.push(e.get("cylinder_r_outer")?);fun409.call(args407,kw408)?}}.attr("extrude")?;let mut args404=Vec::new();let mut kw405=Vec::new();args404.push(binary("sub",e.get("cylinder_bottom_z")?,e.get("cylinder_top_z")?)?);fun406.call(args404,kw405)?}};e.set("tower_cylinder",assigned403.clone())?;
let assigned419=binary("sub",e.get("tower_height")?,e.get("tower_cap_thickness")?)?;e.set("tower_bore_depth",assigned419.clone())?;
let assigned420={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun423={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun426={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun429={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun432={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun435=e.get("WorldWorkplane")?;let mut args433=Vec::new();let mut kw434=Vec::new();args433.push(e.get("xy_plane_z_up")?);fun435.call(args433,kw434)?}}.attr("workplane")?;let mut args430=Vec::new();let mut kw431=Vec::new();kw431.push(("offset".into(),binary("sub",e.get("bore_bottom_z")?,e.get("overcut")?)?));fun432.call(args430,kw431)?}}.attr("center")?;let mut args427=Vec::new();let mut kw428=Vec::new();args427.push(e.get("center_x")?);args427.push(e.get("center_y")?);fun429.call(args427,kw428)?}}.attr("circle")?;let mut args424=Vec::new();let mut kw425=Vec::new();args424.push(e.get("cylinder_r_inner")?);fun426.call(args424,kw425)?}}.attr("extrude")?;let mut args421=Vec::new();let mut kw422=Vec::new();args421.push(binary("add",e.get("tower_bore_depth")?,e.get("overcut")?)?);fun423.call(args421,kw422)?}};e.set("tower_bore",assigned420.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun438=e.get("tower_cylinder")?.attr("cut")?;let mut args436=Vec::new();let mut kw437=Vec::new();args436.push(e.get("tower_bore")?);fun438.call(args436,kw437)?}});
Ok(Val::None)})})?;
    // _lower_profile_set
    e.set("_lower_profile_set", {
        let params = vec![("wall_offset".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned439 = binary(
                "mul",
                e.get("wall_offset")?,
                binary(
                    "sub",
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun442 = e.get("math")?.attr("sqrt")?;
                            let mut args440 = Vec::new();
                            let mut kw441 = Vec::new();
                            args440.push(Val::Int(2i64));
                            fun442.call(args440, kw441)?
                        }
                    },
                    Val::Int(1i64),
                )?,
            )?;
            e.set("seam_y_shift", assigned439.clone())?;
            let assigned443 = binary(
                "sub",
                e.get("skirt_narrow_half_extent")?,
                e.get("wall_offset")?,
            )?;
            e.set("narrow_he", assigned443.clone())?;
            let assigned444 = binary(
                "sub",
                e.get("skirt_base_half_extent")?,
                e.get("wall_offset")?,
            )?;
            e.set("base_he", assigned444.clone())?;
            let assigned445 = binary("sub", e.get("corner_r")?, e.get("wall_offset")?)?;
            e.set("radius", assigned445.clone())?;
            let assigned446 = binary(
                "add",
                e.get("skirt_transition_y_end")?.get(Val::Int(1i64))?,
                e.get("seam_y_shift")?,
            )?;
            e.set("ty_end_minus", assigned446.clone())?;
            let assigned447 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun450 = e.get("split_skirt_profile")?;
                    let mut args448 = Vec::new();
                    let mut kw449 = Vec::new();
                    args448.push(e.get("narrow_he")?);
                    args448.push(e.get("radius")?);
                    args448.push(e.get("narrow_he")?);
                    args448.push(e.get("radius")?);
                    args448.push(e.get("ty_end_minus")?);
                    args448.push(e.get("ty_end_minus")?);
                    kw449.push(("wide_half_extent_y".into(), e.get("base_he")?));
                    kw449.push(("narrow_half_extent_y".into(), e.get("base_he")?));
                    fun450.call(args448, kw449)?
                }
            };
            e.set("narrow_symmetric", assigned447.clone())?;
            let assigned451 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun454 = e.get("_skirt_profile_set")?;
                    let mut args452 = Vec::new();
                    let mut kw453 = Vec::new();
                    args452.push(e.get("wall_offset")?);
                    fun454.call(args452, kw453)?
                }
            }
            .get(unary("neg", Val::Int(1i64))?)?;
            e.set("top", assigned451.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("top")?);
                s.push(e.get("top")?);
                s.push(e.get("narrow_symmetric")?);
                s.push(e.get("narrow_symmetric")?);
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    // lower_z_steps
    e.set("lower_z_steps", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned455 = binary(
                "sub",
                binary("sub", e.get("lower_height")?, e.get("lower_ramp_height")?)?,
                e.get("lower_footprint_straight")?,
            )?;
            e.set("uniform", assigned455.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(unary("neg", e.get("lower_footprint_straight")?)?);
                s.push(unary("neg", e.get("lower_ramp_height")?)?);
                s.push(unary("neg", e.get("uniform")?)?);
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    // flank_ramp_bands
    e.set("flank_ramp_bands", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned456 = binary(
                "sub",
                e.get("skirt_bottom_z")?,
                e.get("lower_footprint_straight")?,
            )?;
            e.set("aft_top", assigned456.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun459 = e.get("sum")?;
                            let mut args457 = Vec::new();
                            let mut kw458 = Vec::new();
                            args457.push(e.get("skirt_z_steps")?.get(Val::Slice {
                                start: None,
                                stop: Some(Val::Int(1i64).integer()?),
                                step: 1,
                            })?);
                            fun459.call(args457, kw458)?
                        }
                    });
                    s.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun462 = e.get("sum")?;
                            let mut args460 = Vec::new();
                            let mut kw461 = Vec::new();
                            args460.push(e.get("skirt_z_steps")?.get(Val::Slice {
                                start: None,
                                stop: Some(Val::Int(3i64).integer()?),
                                step: 1,
                            })?);
                            fun462.call(args460, kw461)?
                        }
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("aft_top")?);
                    s.push(binary(
                        "sub",
                        e.get("aft_top")?,
                        e.get("lower_ramp_height")?,
                    )?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // _profile_prism
    e.set("_profile_prism",{let params=vec![("profile".into(),None,false),("z0".into(),None,false),("z1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun465={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun468={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun471={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun474={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun477={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun480=e.get("WorldWorkplane")?;let mut args478=Vec::new();let mut kw479=Vec::new();args478.push(e.get("xy_plane_z_up")?);fun480.call(args478,kw479)?}}.attr("workplane")?;let mut args475=Vec::new();let mut kw476=Vec::new();kw476.push(("offset".into(),e.get("z0")?));fun477.call(args475,kw476)?}}.attr("center")?;let mut args472=Vec::new();let mut kw473=Vec::new();args472.push(e.get("center_x")?);args472.push(e.get("center_y")?);fun474.call(args472,kw473)?}}.attr("polyline")?;let mut args469=Vec::new();let mut kw470=Vec::new();args469.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun483=e.get("_ring")?;let mut args481=Vec::new();let mut kw482=Vec::new();args481.push(e.get("profile")?);fun483.call(args481,kw482)?}});fun471.call(args469,kw470)?}}.attr("wire")?;let mut args466=Vec::new();let mut kw467=Vec::new();fun468.call(args466,kw467)?}}.attr("extrude")?;let mut args463=Vec::new();let mut kw464=Vec::new();args463.push(binary("sub",e.get("z1")?,e.get("z0")?)?);fun465.call(args463,kw464)?}});
Ok(Val::None)})})?;
    // _stepped_skirt_y_mask
    e.set("_stepped_skirt_y_mask", {
        let params = vec![
            ("z0".into(), None, false),
            ("z1".into(), None, false),
            ("body_y_bounds".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned484 = e.get("body_y_bounds")?;
            let unpack485 = unpack(assigned484.clone(), 2)?;
            e.set("y_min", unpack485[0].clone())?;
            e.set("y_max", unpack485[1].clone())?;
            if unary("not", {
                let v486 = e.get("y_min")?;
                let v487 = e.get("y_max")?;
                Val::Bool(compare("lt", v486.clone(), v487.clone())?.truthy()?)
            })?
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun490 = e.get("ValueError")?;
                            let mut args488 = Vec::new();
                            let mut kw489 = Vec::new();
                            args488.push({
                                let mut str491 = String::new();
                                str491.push_str("bad skirt-body Y interval ");
                                str491.push_str(&format(&e.get("body_y_bounds")?, &String::new())?);
                                Val::Str(str491)
                            });
                            fun490.call(args488, kw489)?
                        }
                    })?
                );
            }
            let assigned492 = binary("sub", e.get("center_x")?, e.get("cutter_half_extent")?)?;
            e.set("x0", assigned492.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun495 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun498 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                    line!(),
                                );
                                {
                                    let fun501 = e.get("cq")?.attr("Workplane")?;
                                    let mut args499 = Vec::new();
                                    let mut kw500 = Vec::new();
                                    args499.push(Val::Str("XY".into()));
                                    fun501.call(args499, kw500)?
                                }
                            }
                            .attr("box")?;
                            let mut args496 = Vec::new();
                            let mut kw497 = Vec::new();
                            args496.push(binary(
                                "mul",
                                Val::Float(2.0f64),
                                e.get("cutter_half_extent")?,
                            )?);
                            args496.push(binary("sub", e.get("y_max")?, e.get("y_min")?)?);
                            args496.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                            kw497.push(("centered".into(), Val::Bool(false)));
                            fun498.call(args496, kw497)?
                        }
                    }
                    .attr("translate")?;
                    let mut args493 = Vec::new();
                    let mut kw494 = Vec::new();
                    args493.push({
                        let mut s = Vec::new();
                        s.push(e.get("x0")?);
                        s.push(binary("add", e.get("center_y")?, e.get("y_min")?)?);
                        s.push(e.get("z0")?);
                        Val::tuple(s)
                    });
                    fun495.call(args493, kw494)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // stepped_skirt_cavity
    e.set("stepped_skirt_cavity", {
        let params = vec![
            ("air".into(), None, false),
            ("support_z".into(), None, false),
            ("body_y_bounds".into(), None, false),
            ("skirt_y_max".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if unary("not", {
                let v502 = e.get("skirt_bottom_z")?;
                let v503 = e.get("support_z")?;
                let v504 = Val::Float(0.0f64);
                Val::Bool(
                    compare("lt", v502.clone(), v503.clone())?.truthy()?
                        && compare("lt", v503.clone(), v504.clone())?.truthy()?,
                )
            })?
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun507 = e.get("ValueError")?;
                            let mut args505 = Vec::new();
                            let mut kw506 = Vec::new();
                            args505.push({
                                let mut str508 = String::new();
                                str508.push_str("a skirt support at ");
                                str508.push_str(&format(
                                    &e.get("support_z")?,
                                    &val_string({
                                        let mut str509 = String::new();
                                        str509.push_str("g");
                                        Val::Str(str509)
                                    })?,
                                )?);
                                str508.push_str(" must lie between ");
                                str508.push_str(&format(
                                    &e.get("skirt_bottom_z")?,
                                    &val_string({
                                        let mut str510 = String::new();
                                        str510.push_str("g");
                                        Val::Str(str510)
                                    })?,
                                )?);
                                str508.push_str(" and 0 mm");
                                Val::Str(str508)
                            });
                            fun507.call(args505, kw506)?
                        }
                    })?
                );
            }
            let assigned511 = binary("sub", e.get("skirt_wall")?, e.get("air")?)?;
            e.set("offset", assigned511.clone())?;
            let assigned512 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun515 = e.get("_skirt_profile_set")?;
                    let mut args513 = Vec::new();
                    let mut kw514 = Vec::new();
                    args513.push(e.get("offset")?);
                    fun515.call(args513, kw514)?
                }
            }
            .get(Val::Int(1i64))?;
            e.set("upper", assigned512.clone())?;
            let assigned516 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun519 = e.get("_skirt_profile_set")?;
                    let mut args517 = Vec::new();
                    let mut kw518 = Vec::new();
                    args517.push(e.get("offset")?);
                    fun519.call(args517, kw518)?
                }
            }
            .get(Val::Int(3i64))?;
            e.set("lower", assigned516.clone())?;
            let assigned520 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun523 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun526 = e.get("cavity")?;
                            let mut args524 = Vec::new();
                            let mut kw525 = Vec::new();
                            args524.push(e.get("air")?);
                            fun526.call(args524, kw525)?
                        }
                    }
                    .attr("val")?;
                    let mut args521 = Vec::new();
                    let mut kw522 = Vec::new();
                    fun523.call(args521, kw522)?
                }
            };
            e.set("room", assigned520.clone())?;
            let assigned527 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun530 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun533 = e.get("_profile_prism")?;
                            let mut args531 = Vec::new();
                            let mut kw532 = Vec::new();
                            args531.push(e.get("lower")?);
                            args531.push(binary(
                                "sub",
                                e.get("lower_cap_top_z")?,
                                e.get("overcut")?,
                            )?);
                            args531.push(e.get("support_z")?);
                            fun533.call(args531, kw532)?
                        }
                    }
                    .attr("val")?;
                    let mut args528 = Vec::new();
                    let mut kw529 = Vec::new();
                    fun530.call(args528, kw529)?
                }
            };
            e.set("lower_mask", assigned527.clone())?;
            let assigned534 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun537 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun540 = e.get("_stepped_skirt_y_mask")?;
                            let mut args538 = Vec::new();
                            let mut kw539 = Vec::new();
                            args538.push(binary(
                                "sub",
                                e.get("lower_cap_top_z")?,
                                e.get("overcut")?,
                            )?);
                            args538.push(e.get("support_z")?);
                            args538.push(e.get("body_y_bounds")?);
                            fun540.call(args538, kw539)?
                        }
                    }
                    .attr("val")?;
                    let mut args535 = Vec::new();
                    let mut kw536 = Vec::new();
                    fun537.call(args535, kw536)?
                }
            };
            e.set("y_mask", assigned534.clone())?;
            let assigned541 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun544 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun547 = e.get("room")?.attr("intersect")?;
                            let mut args545 = Vec::new();
                            let mut kw546 = Vec::new();
                            args545.push(e.get("lower_mask")?);
                            fun547.call(args545, kw546)?
                        }
                    }
                    .attr("intersect")?;
                    let mut args542 = Vec::new();
                    let mut kw543 = Vec::new();
                    args542.push(e.get("y_mask")?);
                    fun544.call(args542, kw543)?
                }
            };
            e.set("lower_room", assigned541.clone())?;
            let assigned548 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun551 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun554 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                    line!(),
                                );
                                {
                                    let fun557 = e.get("_profile_prism")?;
                                    let mut args555 = Vec::new();
                                    let mut kw556 = Vec::new();
                                    args555.push(e.get("upper")?);
                                    args555.push(e.get("support_z")?);
                                    args555.push(Val::Float(0.0f64));
                                    fun557.call(args555, kw556)?
                                }
                            }
                            .attr("val")?;
                            let mut args552 = Vec::new();
                            let mut kw553 = Vec::new();
                            fun554.call(args552, kw553)?
                        }
                    }
                    .attr("intersect")?;
                    let mut args549 = Vec::new();
                    let mut kw550 = Vec::new();
                    args549.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun560 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                    line!(),
                                );
                                {
                                    let fun563 = e.get("_stepped_skirt_y_mask")?;
                                    let mut args561 = Vec::new();
                                    let mut kw562 = Vec::new();
                                    args561.push(e.get("support_z")?);
                                    args561.push(Val::Float(0.0f64));
                                    args561.push({
                                        let mut s = Vec::new();
                                        s.push(unary("neg", e.get("cutter_half_extent")?)?);
                                        s.push(e.get("skirt_y_max")?);
                                        Val::tuple(s)
                                    });
                                    fun563.call(args561, kw562)?
                                }
                            }
                            .attr("val")?;
                            let mut args558 = Vec::new();
                            let mut kw559 = Vec::new();
                            fun560.call(args558, kw559)?
                        }
                    });
                    fun551.call(args549, kw550)?
                }
            };
            e.set("upper_room", assigned548.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun566 = e.get("cq")?.attr("Workplane")?;
                    let mut args564 = Vec::new();
                    let mut kw565 = Vec::new();
                    kw565.push(("obj".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun569 = e.get("upper_room")?.attr("fuse")?;
                            let mut args567 = Vec::new();
                            let mut kw568 = Vec::new();
                            args567.push(e.get("lower_room")?);
                            fun569.call(args567, kw568)?
                        }
                    }));
                    fun566.call(args564, kw565)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // stepped_skirt_drop_well
    e.set("stepped_skirt_drop_well", {
        let params = vec![
            ("air".into(), None, false),
            ("support_z".into(), None, false),
            ("body_y_bounds".into(), None, false),
            ("skirt_y_max".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned570 = binary("sub", e.get("skirt_wall")?, e.get("air")?)?;
            e.set("offset", assigned570.clone())?;
            let assigned571 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun574 = e.get("_skirt_profile_set")?;
                    let mut args572 = Vec::new();
                    let mut kw573 = Vec::new();
                    args572.push(e.get("offset")?);
                    fun574.call(args572, kw573)?
                }
            }
            .get(Val::Int(1i64))?;
            e.set("upper", assigned571.clone())?;
            let assigned575 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun578 = e.get("_skirt_profile_set")?;
                    let mut args576 = Vec::new();
                    let mut kw577 = Vec::new();
                    args576.push(e.get("offset")?);
                    fun578.call(args576, kw577)?
                }
            }
            .get(Val::Int(3i64))?;
            e.set("lower", assigned575.clone())?;
            let assigned579 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun582 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun585 = e.get("drop_well")?;
                            let mut args583 = Vec::new();
                            let mut kw584 = Vec::new();
                            args583.push(e.get("air")?);
                            fun585.call(args583, kw584)?
                        }
                    }
                    .attr("val")?;
                    let mut args580 = Vec::new();
                    let mut kw581 = Vec::new();
                    fun582.call(args580, kw581)?
                }
            };
            e.set("swept", assigned579.clone())?;
            let assigned586 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun589 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun592 = e.get("_profile_prism")?;
                            let mut args590 = Vec::new();
                            let mut kw591 = Vec::new();
                            args590.push(e.get("lower")?);
                            args590.push(binary(
                                "sub",
                                e.get("lower_cap_top_z")?,
                                e.get("overcut")?,
                            )?);
                            args590.push(e.get("support_z")?);
                            fun592.call(args590, kw591)?
                        }
                    }
                    .attr("val")?;
                    let mut args587 = Vec::new();
                    let mut kw588 = Vec::new();
                    fun589.call(args587, kw588)?
                }
            };
            e.set("lower_mask", assigned586.clone())?;
            let assigned593 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun596 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun599 = e.get("_stepped_skirt_y_mask")?;
                            let mut args597 = Vec::new();
                            let mut kw598 = Vec::new();
                            args597.push(binary(
                                "sub",
                                e.get("lower_cap_top_z")?,
                                e.get("overcut")?,
                            )?);
                            args597.push(e.get("support_z")?);
                            args597.push(e.get("body_y_bounds")?);
                            fun599.call(args597, kw598)?
                        }
                    }
                    .attr("val")?;
                    let mut args594 = Vec::new();
                    let mut kw595 = Vec::new();
                    fun596.call(args594, kw595)?
                }
            };
            e.set("y_mask", assigned593.clone())?;
            let assigned600 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun603 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun606 = e.get("swept")?.attr("intersect")?;
                            let mut args604 = Vec::new();
                            let mut kw605 = Vec::new();
                            args604.push(e.get("lower_mask")?);
                            fun606.call(args604, kw605)?
                        }
                    }
                    .attr("intersect")?;
                    let mut args601 = Vec::new();
                    let mut kw602 = Vec::new();
                    args601.push(e.get("y_mask")?);
                    fun603.call(args601, kw602)?
                }
            };
            e.set("lower_room", assigned600.clone())?;
            let assigned607 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun610 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun613 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                    line!(),
                                );
                                {
                                    let fun616 = {
                                        let _site = rt.source_at(
                                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                            line!(),
                                        );
                                        {
                                            let fun619 = e.get("_profile_prism")?;
                                            let mut args617 = Vec::new();
                                            let mut kw618 = Vec::new();
                                            args617.push(e.get("upper")?);
                                            args617.push(e.get("support_z")?);
                                            args617.push(Val::Float(0.0f64));
                                            fun619.call(args617, kw618)?
                                        }
                                    }
                                    .attr("union")?;
                                    let mut args614 = Vec::new();
                                    let mut kw615 = Vec::new();
                                    args614.push({
                                        let _site = rt.source_at(
                                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                            line!(),
                                        );
                                        {
                                            let fun622 = e.get("_profile_prism")?;
                                            let mut args620 = Vec::new();
                                            let mut kw621 = Vec::new();
                                            args620.push(e.get("lower")?);
                                            args620.push(e.get("support_z")?);
                                            args620.push(Val::Float(0.0f64));
                                            fun622.call(args620, kw621)?
                                        }
                                    });
                                    fun616.call(args614, kw615)?
                                }
                            }
                            .attr("val")?;
                            let mut args611 = Vec::new();
                            let mut kw612 = Vec::new();
                            fun613.call(args611, kw612)?
                        }
                    }
                    .attr("intersect")?;
                    let mut args608 = Vec::new();
                    let mut kw609 = Vec::new();
                    args608.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun625 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                    line!(),
                                );
                                {
                                    let fun628 = e.get("_stepped_skirt_y_mask")?;
                                    let mut args626 = Vec::new();
                                    let mut kw627 = Vec::new();
                                    args626.push(e.get("support_z")?);
                                    args626.push(Val::Float(0.0f64));
                                    args626.push({
                                        let mut s = Vec::new();
                                        s.push(unary("neg", e.get("cutter_half_extent")?)?);
                                        s.push(e.get("skirt_y_max")?);
                                        Val::tuple(s)
                                    });
                                    fun628.call(args626, kw627)?
                                }
                            }
                            .attr("val")?;
                            let mut args623 = Vec::new();
                            let mut kw624 = Vec::new();
                            fun625.call(args623, kw624)?
                        }
                    });
                    fun610.call(args608, kw609)?
                }
            };
            e.set("upper_room", assigned607.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun631 = e.get("cq")?.attr("Workplane")?;
                    let mut args629 = Vec::new();
                    let mut kw630 = Vec::new();
                    kw630.push(("obj".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun634 = e.get("upper_room")?.attr("fuse")?;
                            let mut args632 = Vec::new();
                            let mut kw633 = Vec::new();
                            args632.push(e.get("lower_room")?);
                            fun634.call(args632, kw633)?
                        }
                    }));
                    fun631.call(args629, kw630)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // cavity
    e.set("cavity", {
        let params = vec![("air".into(), Some(Val::Float(0.0f64)), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned635 = binary("sub", e.get("skirt_wall")?, e.get("air")?)?;
            e.set("offset", assigned635.clone())?;
            let assigned636 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun639 = e.get("loft_profile_stack")?;
                    let mut args637 = Vec::new();
                    let mut kw638 = Vec::new();
                    args637.push(Val::Int(0i64));
                    args637.push(e.get("skirt_z_steps")?);
                    args637.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun642 = e.get("_skirt_profile_set")?;
                            let mut args640 = Vec::new();
                            let mut kw641 = Vec::new();
                            args640.push(e.get("offset")?);
                            fun642.call(args640, kw641)?
                        }
                    });
                    fun639.call(args637, kw638)?
                }
            };
            e.set("skirt", assigned636.clone())?;
            let assigned643 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun646 = e.get("loft_profile_stack")?;
                    let mut args644 = Vec::new();
                    let mut kw645 = Vec::new();
                    args644.push(e.get("skirt_bottom_z")?);
                    args644.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun649 = e.get("lower_z_steps")?;
                            let mut args647 = Vec::new();
                            let mut kw648 = Vec::new();
                            fun649.call(args647, kw648)?
                        }
                    });
                    args644.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun652 = e.get("_lower_profile_set")?;
                            let mut args650 = Vec::new();
                            let mut kw651 = Vec::new();
                            args650.push(e.get("offset")?);
                            fun652.call(args650, kw651)?
                        }
                    });
                    fun646.call(args644, kw645)?
                }
            };
            e.set("lower", assigned643.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun655 = e.get("skirt")?.attr("union")?;
                    let mut args653 = Vec::new();
                    let mut kw654 = Vec::new();
                    args653.push(e.get("lower")?);
                    fun655.call(args653, kw654)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // drop_well
    e.set("drop_well",{let params=vec![("air".into(),Some(Val::Float(0.0f64)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned656={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun659=e.get("cavity")?;let mut args657=Vec::new();let mut kw658=Vec::new();args657.push(e.get("air")?);fun659.call(args657,kw658)?}};e.set("solid",assigned656.clone())?;
for item660 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun663=e.get("zip")?;let mut args661=Vec::new();let mut kw662=Vec::new();args661.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun666=e.get("_stack_levels")?;let mut args664=Vec::new();let mut kw665=Vec::new();fun666.call(args664,kw665)?}});args661.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun669=e.get("_stack_profiles")?;let mut args667=Vec::new();let mut kw668=Vec::new();args667.push(binary("sub",e.get("skirt_wall")?,e.get("air")?)?);fun669.call(args667,kw668)?}});fun663.call(args661,kw662)?}}.iter()? {
let unpack670=unpack(item660,2)?;e.set("z",unpack670[0].clone())?;e.set("profile",unpack670[1].clone())?;if {let v671=e.get("z")?;let v672=unary("neg",Val::Float(1e-09f64))?;Val::Bool(compare("ge",v671.clone(),v672.clone())?.truthy()?)}.truthy()? {
continue;
}
let assigned673={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun676=e.get("solid")?.attr("union")?;let mut args674=Vec::new();let mut kw675=Vec::new();args674.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun679={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun682={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun685={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun688={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun691={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun694=e.get("WorldWorkplane")?;let mut args692=Vec::new();let mut kw693=Vec::new();args692.push(e.get("xy_plane_z_up")?);fun694.call(args692,kw693)?}}.attr("workplane")?;let mut args689=Vec::new();let mut kw690=Vec::new();kw690.push(("offset".into(),e.get("z")?));fun691.call(args689,kw690)?}}.attr("center")?;let mut args686=Vec::new();let mut kw687=Vec::new();args686.push(e.get("center_x")?);args686.push(e.get("center_y")?);fun688.call(args686,kw687)?}}.attr("polyline")?;let mut args683=Vec::new();let mut kw684=Vec::new();args683.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun697=e.get("_ring")?;let mut args695=Vec::new();let mut kw696=Vec::new();args695.push(e.get("profile")?);fun697.call(args695,kw696)?}});fun685.call(args683,kw684)?}}.attr("wire")?;let mut args680=Vec::new();let mut kw681=Vec::new();fun682.call(args680,kw681)?}}.attr("extrude")?;let mut args677=Vec::new();let mut kw678=Vec::new();args677.push(unary("neg",e.get("z")?)?);fun679.call(args677,kw678)?}});fun676.call(args674,kw675)?}};e.set("solid",assigned673.clone())?;
}
return Ok(e.get("solid")?);
Ok(Val::None)})})?;
    // _stack_levels
    e.set("_stack_levels", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned698 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    Val::list(s)
                });
                s.push(Val::Float(0.0f64));
                Val::tuple(s)
            };
            let unpack699 = unpack(assigned698.clone(), 2)?;
            e.set("out", unpack699[0].clone())?;
            e.set("z", unpack699[1].clone())?;
            for item700 in e.get("skirt_z_steps")?.iter()? {
                e.set("dz", item700)?;
                e.set("z", binary("add", e.get("z")?, e.get("dz")?)?)?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun703 = e.get("out")?.attr("append")?;
                        let mut args701 = Vec::new();
                        let mut kw702 = Vec::new();
                        args701.push(e.get("z")?);
                        fun703.call(args701, kw702)?
                    }
                };
            }
            for item704 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun707 = e.get("lower_z_steps")?;
                    let mut args705 = Vec::new();
                    let mut kw706 = Vec::new();
                    fun707.call(args705, kw706)?
                }
            }
            .iter()?
            {
                e.set("dz", item704)?;
                e.set("z", binary("add", e.get("z")?, e.get("dz")?)?)?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun710 = e.get("out")?.attr("append")?;
                        let mut args708 = Vec::new();
                        let mut kw709 = Vec::new();
                        args708.push(e.get("z")?);
                        fun710.call(args708, kw709)?
                    }
                };
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // _stack_profiles
    e.set("_stack_profiles", {
        let params = vec![("offset".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "add",
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun713 = e.get("list")?;
                        let mut args711 = Vec::new();
                        let mut kw712 = Vec::new();
                        args711.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun716 = e.get("_skirt_profile_set")?;
                                let mut args714 = Vec::new();
                                let mut kw715 = Vec::new();
                                args714.push(e.get("offset")?);
                                fun716.call(args714, kw715)?
                            }
                        });
                        fun713.call(args711, kw712)?
                    }
                },
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun719 = e.get("list")?;
                        let mut args717 = Vec::new();
                        let mut kw718 = Vec::new();
                        args717.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                                line!(),
                            );
                            {
                                let fun722 = e.get("_lower_profile_set")?;
                                let mut args720 = Vec::new();
                                let mut kw721 = Vec::new();
                                args720.push(e.get("offset")?);
                                fun722.call(args720, kw721)?
                            }
                        });
                        fun719.call(args717, kw718)?
                    }
                }
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: None,
                    step: 1,
                })?,
            )?);
            Ok(Val::None)
        })
    })?;
    // build_lower_extension
    e.set("build_lower_extension",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned723={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun726=e.get("_lower_profile_set")?;let mut args724=Vec::new();let mut kw725=Vec::new();args724.push(Val::Int(0i64));fun726.call(args724,kw725)?}};e.set("lower_outer_profiles",assigned723.clone())?;
let assigned727={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun730=e.get("_lower_profile_set")?;let mut args728=Vec::new();let mut kw729=Vec::new();args728.push(e.get("skirt_wall")?);fun730.call(args728,kw729)?}};e.set("lower_inner_profiles",assigned727.clone())?;
let assigned731={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun734=e.get("lower_z_steps")?;let mut args732=Vec::new();let mut kw733=Vec::new();fun734.call(args732,kw733)?}};e.set("steps",assigned731.clone())?;
let assigned735={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun738=e.get("loft_profile_stack")?;let mut args736=Vec::new();let mut kw737=Vec::new();args736.push(e.get("skirt_bottom_z")?);args736.push(e.get("steps")?);args736.push(e.get("lower_outer_profiles")?);fun738.call(args736,kw737)?}};e.set("lower_outer",assigned735.clone())?;
let assigned739={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun742=e.get("loft_profile_stack")?;let mut args740=Vec::new();let mut kw741=Vec::new();args740.push(e.get("skirt_bottom_z")?);args740.push(e.get("steps")?);args740.push(e.get("lower_inner_profiles")?);kw741.push(("overcut_last_step".into(),Val::Bool(true)));fun742.call(args740,kw741)?}};e.set("lower_inner",assigned739.clone())?;
let assigned743={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun746=e.get("lower_outer")?.attr("cut")?;let mut args744=Vec::new();let mut kw745=Vec::new();args744.push(e.get("lower_inner")?);fun746.call(args744,kw745)?}};e.set("lower_shell",assigned743.clone())?;
let assigned747={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun750={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun753={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun756={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun759={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun762={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun765=e.get("WorldWorkplane")?;let mut args763=Vec::new();let mut kw764=Vec::new();args763.push(e.get("xy_plane_z_up")?);fun765.call(args763,kw764)?}}.attr("workplane")?;let mut args760=Vec::new();let mut kw761=Vec::new();kw761.push(("offset".into(),e.get("lower_cap_top_z")?));fun762.call(args760,kw761)?}}.attr("center")?;let mut args757=Vec::new();let mut kw758=Vec::new();args757.push(e.get("center_x")?);args757.push(e.get("center_y")?);fun759.call(args757,kw758)?}}.attr("polyline")?;let mut args754=Vec::new();let mut kw755=Vec::new();args754.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun768=e.get("_ring")?;let mut args766=Vec::new();let mut kw767=Vec::new();args766.push(e.get("lower_outer_profiles")?.get(unary("neg",Val::Int(1i64))?)?);fun768.call(args766,kw767)?}});fun756.call(args754,kw755)?}}.attr("wire")?;let mut args751=Vec::new();let mut kw752=Vec::new();fun753.call(args751,kw752)?}}.attr("extrude")?;let mut args748=Vec::new();let mut kw749=Vec::new();args748.push(unary("neg",e.get("lower_cap_thickness")?)?);fun750.call(args748,kw749)?}};e.set("lower_cap",assigned747.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun771=e.get("lower_shell")?.attr("union")?;let mut args769=Vec::new();let mut kw770=Vec::new();args769.push(e.get("lower_cap")?);fun771.call(args769,kw770)?}});
Ok(Val::None)})})?;
    // cut_arch_notches
    e.set("cut_arch_notches",{let params=vec![("combined".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned772=binary("add",e.get("skirt_wall")?,e.get("wall_thickness")?)?;e.set("arch_cut_depth",assigned772.clone())?;
for item773 in e.get("arch_hole_xs")?.iter()? {
e.set("ax",item773)?;let assigned774={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun777={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun780={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun783={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun786={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun789=e.get("WorldWorkplane")?;let mut args787=Vec::new();let mut kw788=Vec::new();args787.push(e.get("xz_plane_y_up")?);fun789.call(args787,kw788)?}}.attr("workplane")?;let mut args784=Vec::new();let mut kw785=Vec::new();kw785.push(("offset".into(),binary("add",e.get("pos_y_face_y")?,e.get("overcut")?)?));fun786.call(args784,kw785)?}}.attr("center")?;let mut args781=Vec::new();let mut kw782=Vec::new();args781.push(e.get("ax")?);args781.push(e.get("skirt_bottom_z")?);fun783.call(args781,kw782)?}}.attr("circle")?;let mut args778=Vec::new();let mut kw779=Vec::new();args778.push(e.get("arch_radius")?);fun780.call(args778,kw779)?}}.attr("extrude")?;let mut args775=Vec::new();let mut kw776=Vec::new();args775.push(unary("neg",binary("add",e.get("arch_cut_depth")?,e.get("overcut")?)?)?);fun777.call(args775,kw776)?}};e.set("arch_cutter",assigned774.clone())?;
let assigned790={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun793=e.get("combined")?.attr("cut")?;let mut args791=Vec::new();let mut kw792=Vec::new();args791.push(e.get("arch_cutter")?);fun793.call(args791,kw792)?}};e.set("combined",assigned790.clone())?;
}
return Ok(e.get("combined")?);
Ok(Val::None)})})?;
    // split_into_base_and_cap
    e.set("split_into_base_and_cap",{let params=vec![("combined".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned794=binary("sub",e.get("lower_cap_bottom_z")?,e.get("overcut")?)?;e.set("lower_end_z",assigned794.clone())?;
let assigned795={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun798={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun801={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun804={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun807={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun810=e.get("WorldWorkplane")?;let mut args808=Vec::new();let mut kw809=Vec::new();args808.push(e.get("xy_plane_z_up")?);fun810.call(args808,kw809)?}}.attr("workplane")?;let mut args805=Vec::new();let mut kw806=Vec::new();kw806.push(("offset".into(),e.get("skirt_bottom_z")?));fun807.call(args805,kw806)?}}.attr("center")?;let mut args802=Vec::new();let mut kw803=Vec::new();args802.push(e.get("center_x")?);args802.push(e.get("center_y")?);fun804.call(args802,kw803)?}}.attr("rect")?;let mut args799=Vec::new();let mut kw800=Vec::new();args799.push(binary("mul",Val::Int(2i64),e.get("cutter_half_extent")?)?);args799.push(binary("mul",Val::Int(2i64),e.get("cutter_half_extent")?)?);fun801.call(args799,kw800)?}}.attr("extrude")?;let mut args796=Vec::new();let mut kw797=Vec::new();args796.push(binary("sub",e.get("lower_end_z")?,e.get("skirt_bottom_z")?)?);fun798.call(args796,kw797)?}};e.set("full_slab",assigned795.clone())?;
let assigned811=binary("add",e.get("skirt_transition_y_end_plus")?,e.get("step_y_clearance")?)?;e.set("step_y",assigned811.clone())?;
let assigned812={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(unary("neg",e.get("cutter_half_extent")?)?);s.push(unary("neg",e.get("cutter_half_extent")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("cutter_half_extent")?);s.push(unary("neg",e.get("cutter_half_extent")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("cutter_half_extent")?);s.push(binary("add",e.get("step_y")?,e.get("overcut")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(unary("neg",e.get("cutter_half_extent")?)?);s.push(binary("add",e.get("step_y")?,e.get("overcut")?)?);Val::tuple(s)});Val::list(s)};e.set("narrow_box",assigned812.clone())?;
let assigned813={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun816={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun819={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun822={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun825={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun828={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun831=e.get("WorldWorkplane")?;let mut args829=Vec::new();let mut kw830=Vec::new();args829.push(e.get("xy_plane_z_up")?);fun831.call(args829,kw830)?}}.attr("workplane")?;let mut args826=Vec::new();let mut kw827=Vec::new();kw827.push(("offset".into(),e.get("narrow_split_z")?));fun828.call(args826,kw827)?}}.attr("center")?;let mut args823=Vec::new();let mut kw824=Vec::new();args823.push(e.get("center_x")?);args823.push(e.get("center_y")?);fun825.call(args823,kw824)?}}.attr("polyline")?;let mut args820=Vec::new();let mut kw821=Vec::new();args820.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun834=e.get("_ring")?;let mut args832=Vec::new();let mut kw833=Vec::new();args832.push(e.get("narrow_box")?);fun834.call(args832,kw833)?}});fun822.call(args820,kw821)?}}.attr("wire")?;let mut args817=Vec::new();let mut kw818=Vec::new();fun819.call(args817,kw818)?}}.attr("extrude")?;let mut args814=Vec::new();let mut kw815=Vec::new();args814.push(binary("sub",e.get("skirt_bottom_z")?,e.get("narrow_split_z")?)?);fun816.call(args814,kw815)?}};e.set("narrow_step",assigned813.clone())?;
let assigned835={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun838=e.get("full_slab")?.attr("union")?;let mut args836=Vec::new();let mut kw837=Vec::new();args836.push(e.get("narrow_step")?);fun838.call(args836,kw837)?}};e.set("step_cutter",assigned835.clone())?;
let assigned839={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun842=e.get("combined")?.attr("cut")?;let mut args840=Vec::new();let mut kw841=Vec::new();args840.push(e.get("step_cutter")?);fun842.call(args840,kw841)?}};e.set("base",assigned839.clone())?;
let assigned843={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/pump_case.rs",line!());{let fun846=e.get("combined")?.attr("intersect")?;let mut args844=Vec::new();let mut kw845=Vec::new();args844.push(e.get("step_cutter")?);fun846.call(args844,kw845)?}};e.set("cap",assigned843.clone())?;
return Ok({let mut s=Vec::new();s.push(e.get("base")?);s.push(e.get("cap")?);Val::tuple(s)});
Ok(Val::None)})})?;
    // add_snap_fits
    e.set("add_snap_fits", {
        let params = vec![("base".into(), None, false), ("cap".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned847 = binary("sub", e.get("pos_y_face_y")?, e.get("wall_thickness")?)?;
            e.set("snap_plus_y_inner", assigned847.clone())?;
            let assigned848 = binary(
                "add",
                binary("sub", e.get("center_y")?, e.get("footprint_half_extent")?)?,
                e.get("wall_thickness")?,
            )?;
            e.set("snap_minus_y_inner", assigned848.clone())?;
            let assigned849 = binary(
                "sub",
                binary("add", e.get("center_x")?, e.get("footprint_half_extent")?)?,
                e.get("wall_thickness")?,
            )?;
            e.set("snap_plus_x_inner", assigned849.clone())?;
            let assigned850 = binary(
                "add",
                binary("sub", e.get("center_x")?, e.get("footprint_half_extent")?)?,
                e.get("wall_thickness")?,
            )?;
            e.set("snap_minus_x_inner", assigned850.clone())?;
            let assigned851 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("center_x")?,
                    binary("truediv", e.get("snap_zone_width")?, Val::Int(2i64))?,
                )?);
                s.push(binary(
                    "add",
                    e.get("center_x")?,
                    binary("truediv", e.get("snap_zone_width")?, Val::Int(2i64))?,
                )?);
                Val::tuple(s)
            };
            e.set("yz_zone_range", assigned851.clone())?;
            let assigned852 = binary(
                "add",
                binary(
                    "add",
                    binary(
                        "sub",
                        e.get("center_y")?,
                        e.get("skirt_narrow_half_extent")?,
                    )?,
                    e.get("corner_r")?,
                )?,
                Val::Float(0.5f64),
            )?;
            e.set("zx_zone_start", assigned852.clone())?;
            let assigned853 = {
                let mut s = Vec::new();
                s.push(e.get("zx_zone_start")?);
                s.push(binary(
                    "add",
                    e.get("zx_zone_start")?,
                    e.get("snap_zone_width")?,
                )?);
                Val::tuple(s)
            };
            e.set("zx_zone_range", assigned853.clone())?;
            let assigned854 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("snap_plus_y_inner")?);
                    s.push(unary("pos", Val::Int(1i64))?);
                    s.push(e.get("skirt_bottom_z")?);
                    s.push(Val::Str("YZ".into()));
                    s.push(e.get("yz_zone_range")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("snap_minus_y_inner")?);
                    s.push(unary("neg", Val::Int(1i64))?);
                    s.push(e.get("narrow_split_z")?);
                    s.push(Val::Str("YZ".into()));
                    s.push(e.get("yz_zone_range")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("snap_plus_x_inner")?);
                    s.push(unary("pos", Val::Int(1i64))?);
                    s.push(e.get("narrow_split_z")?);
                    s.push(Val::Str("ZX".into()));
                    s.push(e.get("zx_zone_range")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("snap_minus_x_inner")?);
                    s.push(unary("neg", Val::Int(1i64))?);
                    s.push(e.get("narrow_split_z")?);
                    s.push(Val::Str("ZX".into()));
                    s.push(e.get("zx_zone_range")?);
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("snap_faces", assigned854.clone())?;
            for item855 in e.get("snap_faces")?.iter()? {
                let unpack856 = unpack(item855, 5)?;
                e.set("inner_face", unpack856[0].clone())?;
                e.set("sign", unpack856[1].clone())?;
                e.set("split_z", unpack856[2].clone())?;
                e.set("plane", unpack856[3].clone())?;
                e.set("zone_range", unpack856[4].clone())?;
                let assigned857 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun860 = e.get("Frame")?;
                        let mut args858 = Vec::new();
                        let mut kw859 = Vec::new();
                        kw859.push(("extrusion_plane".into(), e.get("plane")?));
                        kw859.push(("outward_sign".into(), e.get("sign")?));
                        kw859.push(("up_axis".into(), Val::Str("Z".into())));
                        kw859.push(("up_sign".into(), unary("neg", Val::Int(1i64))?));
                        fun860.call(args858, kw859)?
                    }
                };
                e.set("base_frame", assigned857.clone())?;
                let assigned861 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun864 = e.get("Frame")?;
                        let mut args862 = Vec::new();
                        let mut kw863 = Vec::new();
                        kw863.push(("extrusion_plane".into(), e.get("plane")?));
                        kw863.push(("outward_sign".into(), e.get("sign")?));
                        kw863.push(("up_axis".into(), Val::Str("Z".into())));
                        kw863.push(("up_sign".into(), unary("pos", Val::Int(1i64))?));
                        fun864.call(args862, kw863)?
                    }
                };
                e.set("cap_frame", assigned861.clone())?;
                let assigned865 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun868 = e.get("apply_ramp_out_first")?;
                        let mut args866 = Vec::new();
                        let mut kw867 = Vec::new();
                        args866.push(e.get("base")?);
                        kw867.push(("frame".into(), e.get("base_frame")?));
                        kw867.push(("inner_wall_at".into(), e.get("inner_face")?));
                        kw867.push(("wall_top_at".into(), e.get("split_z")?));
                        kw867.push(("wall_height".into(), e.get("snap_wall_height")?));
                        kw867.push(("zone_range".into(), e.get("zone_range")?));
                        kw867.push(("deflection_distance".into(), e.get("snap_deflection")?));
                        fun868.call(args866, kw867)?
                    }
                };
                e.set("base", assigned865.clone())?;
                let assigned869 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                        line!(),
                    );
                    {
                        let fun872 = e.get("apply_ramp_in_first")?;
                        let mut args870 = Vec::new();
                        let mut kw871 = Vec::new();
                        args870.push(e.get("cap")?);
                        kw871.push(("frame".into(), e.get("cap_frame")?));
                        kw871.push(("inner_wall_at".into(), e.get("inner_face")?));
                        kw871.push(("wall_top_at".into(), e.get("split_z")?));
                        kw871.push(("wall_height".into(), e.get("snap_wall_height")?));
                        kw871.push(("zone_range".into(), e.get("zone_range")?));
                        kw871.push(("deflection_distance".into(), e.get("snap_deflection")?));
                        fun872.call(args870, kw871)?
                    }
                };
                e.set("cap", assigned869.clone())?;
            }
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("base")?);
                s.push(e.get("cap")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // build_pump_case
    e.set("build_pump_case", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned873 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun876 = e.get("build_base_plate_with_ramp")?;
                    let mut args874 = Vec::new();
                    let mut kw875 = Vec::new();
                    fun876.call(args874, kw875)?
                }
            };
            e.set("solid", assigned873.clone())?;
            let assigned877 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun880 = e.get("solid")?.attr("union")?;
                    let mut args878 = Vec::new();
                    let mut kw879 = Vec::new();
                    args878.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun883 = e.get("build_skirt")?;
                            let mut args881 = Vec::new();
                            let mut kw882 = Vec::new();
                            fun883.call(args881, kw882)?
                        }
                    });
                    fun880.call(args878, kw879)?
                }
            };
            e.set("solid", assigned877.clone())?;
            let assigned884 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun887 = e.get("add_bore_wall")?;
                    let mut args885 = Vec::new();
                    let mut kw886 = Vec::new();
                    args885.push(e.get("solid")?);
                    fun887.call(args885, kw886)?
                }
            };
            e.set("solid", assigned884.clone())?;
            let assigned888 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun891 = e.get("solid")?.attr("union")?;
                    let mut args889 = Vec::new();
                    let mut kw890 = Vec::new();
                    args889.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun894 = e.get("build_tower")?;
                            let mut args892 = Vec::new();
                            let mut kw893 = Vec::new();
                            fun894.call(args892, kw893)?
                        }
                    });
                    fun891.call(args889, kw890)?
                }
            };
            e.set("solid", assigned888.clone())?;
            let assigned895 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun898 = e.get("cut_bore_cavity")?;
                    let mut args896 = Vec::new();
                    let mut kw897 = Vec::new();
                    args896.push(e.get("solid")?);
                    fun898.call(args896, kw897)?
                }
            };
            e.set("solid", assigned895.clone())?;
            let assigned899 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun902 = e.get("solid")?.attr("union")?;
                    let mut args900 = Vec::new();
                    let mut kw901 = Vec::new();
                    args900.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                            line!(),
                        );
                        {
                            let fun905 = e.get("build_lower_extension")?;
                            let mut args903 = Vec::new();
                            let mut kw904 = Vec::new();
                            fun905.call(args903, kw904)?
                        }
                    });
                    fun902.call(args900, kw901)?
                }
            };
            e.set("combined", assigned899.clone())?;
            let assigned906 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun909 = e.get("cut_arch_notches")?;
                    let mut args907 = Vec::new();
                    let mut kw908 = Vec::new();
                    args907.push(e.get("combined")?);
                    fun909.call(args907, kw908)?
                }
            };
            e.set("combined", assigned906.clone())?;
            let assigned910 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun913 = e.get("split_into_base_and_cap")?;
                    let mut args911 = Vec::new();
                    let mut kw912 = Vec::new();
                    args911.push(e.get("combined")?);
                    fun913.call(args911, kw912)?
                }
            };
            let unpack914 = unpack(assigned910.clone(), 2)?;
            e.set("base", unpack914[0].clone())?;
            e.set("cap", unpack914[1].clone())?;
            let assigned915 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun918 = e.get("add_snap_fits")?;
                    let mut args916 = Vec::new();
                    let mut kw917 = Vec::new();
                    args916.push(e.get("base")?);
                    args916.push(e.get("cap")?);
                    fun918.call(args916, kw917)?
                }
            };
            let unpack919 = unpack(assigned915.clone(), 2)?;
            e.set("base", unpack919[0].clone())?;
            e.set("cap", unpack919[1].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("base")?);
                s.push(e.get("cap")?);
                Val::tuple(s)
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
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
                    line!(),
                );
                {
                    let fun928 = e.get("print")?;
                    let mut args926 = Vec::new();
                    let mut kw927 = Vec::new();
                    args926.push(Val::Str("-> updated comments in pump_case.py".into()));
                    fun928.call(args926, kw927)?
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
            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
            line!(),
        );
        {
            let fun931 = e.get("_rust_part")?.attr("start")?;
            let mut args929 = Vec::new();
            let mut kw930 = Vec::new();
            fun931.call(args929, kw930)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/pump_case.rs",
            line!(),
        );
        {
            let fun934 = e.get("main")?;
            let mut args932 = Vec::new();
            let mut kw933 = Vec::new();
            fun934.call(args932, kw933)?
        }
    };
    Ok(Val::None)
}
