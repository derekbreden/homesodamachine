#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
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
                        Val::Str("hardware/scripts/_rust_part.py".into()),
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
    let assigned17 = {
        let fun20 = {
            let fun23 = e.get("Path")?;
            let mut args21 = Vec::new();
            let mut kw22 = Vec::new();
            args21.push(e.get("__file__")?);
            fun23.call(args21, kw22)?
        }
        .attr("resolve")?;
        let mut args18 = Vec::new();
        let mut kw19 = Vec::new();
        fun20.call(args18, kw19)?
    }
    .attr("parent")?;
    e.set("HERE", assigned17.clone())?;
    {
        let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args24 = Vec::new();
        let mut kw25 = Vec::new();
        args24.push(Val::Int(0i64));
        args24.push({
            let fun29 = e.get("str")?;
            let mut args27 = Vec::new();
            let mut kw28 = Vec::new();
            args27.push(binary(
                "truediv",
                e.get("ROOT")?,
                Val::Str("hardware/scripts".into()),
            )?);
            fun29.call(args27, kw28)?
        });
        fun26.call(args24, kw25)?
    };
    {
        let fun32 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args30 = Vec::new();
        let mut kw31 = Vec::new();
        args30.push(Val::Int(0i64));
        args30.push({
            let fun35 = e.get("str")?;
            let mut args33 = Vec::new();
            let mut kw34 = Vec::new();
            args33.push(e.get("HERE")?.attr("parents")?.get(Val::Int(1i64))?);
            fun35.call(args33, kw34)?
        });
        fun32.call(args30, kw31)?
    };
    let mod36 = rt.import_module("_float_interface")?;
    e.set("diameter", rt.member("_float_interface", "diameter")?)?;
    e.set(
        "bore_diameter",
        rt.member("_float_interface", "bore_diameter")?,
    )?;
    e.set(
        "guide_diameter",
        rt.member("_float_interface", "guide_diameter")?,
    )?;
    e.set("magnet_od", rt.member("_float_interface", "magnet_od")?)?;
    e.set("magnet_id", rt.member("_float_interface", "magnet_id")?)?;
    e.set(
        "magnet_thickness",
        rt.member("_float_interface", "magnet_thickness")?,
    )?;
    e.set(
        "magnet_tolerance",
        rt.member("_float_interface", "magnet_tolerance")?,
    )?;
    e.set("magnet_mass", rt.member("_float_interface", "magnet_mass")?)?;
    e.set("pocket_od", rt.member("_float_interface", "pocket_od")?)?;
    e.set("pocket_id", rt.member("_float_interface", "pocket_id")?)?;
    e.set(
        "pocket_depth",
        rt.member("_float_interface", "pocket_depth")?,
    )?;
    e.set(
        "water_density",
        rt.member("_float_interface", "water_density")?,
    )?;
    e.set(
        "design_foam_density",
        rt.member("_float_interface", "design_foam_density")?,
    )?;
    e.set(
        "minimum_reserve_lift_g",
        rt.member("_float_interface", "minimum_reserve_lift_g")?,
    )?;
    e.set(
        "height_increment",
        rt.member("_float_interface", "height_increment")?,
    )?;
    e.set(
        "layer_height",
        rt.member("_float_interface", "layer_height")?,
    )?;
    e.set(
        "xy_contour_compensation",
        rt.member("_float_interface", "xy_contour_compensation")?,
    )?;
    e.set(
        "xy_hole_compensation",
        rt.member("_float_interface", "xy_hole_compensation")?,
    )?;
    e.set(
        "annular_area",
        rt.member("_float_interface", "annular_area")?,
    )?;
    e.set(
        "pocket_volume",
        rt.member("_float_interface", "pocket_volume")?,
    )?;
    e.set(
        "minimum_height",
        rt.member("_float_interface", "minimum_height")?,
    )?;
    e.set("height", rt.member("_float_interface", "height")?)?;
    e.set(
        "magnet_midplane",
        rt.member("_float_interface", "magnet_midplane")?,
    )?;
    e.set("magnet_seat", rt.member("_float_interface", "magnet_seat")?)?;
    e.set("pocket_roof", rt.member("_float_interface", "pocket_roof")?)?;
    e.set(
        "pause_before_z",
        rt.member("_float_interface", "pause_before_z")?,
    )?;
    e.set(
        "rod_axis_from_inner_wall",
        rt.member("_float_interface", "rod_axis_from_inner_wall")?,
    )?;
    e.set(
        "minimum_wall_clearance",
        rt.member("_float_interface", "minimum_wall_clearance")?,
    )?;
    e.set(
        "maximum_wall_clearance",
        rt.member("_float_interface", "maximum_wall_clearance")?,
    )?;
    e.set(
        "magnet_above_waterline",
        rt.member("_float_interface", "magnet_above_waterline")?,
    )?;
    // measurements
    e.set("measurements", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod37 = rt.import_module("_cold_core_data")?;
            e.set("read", rt.member("_cold_core_data", "read")?)?;
            return Ok({
                let fun40 = e.get("read")?;
                let mut args38 = Vec::new();
                let mut kw39 = Vec::new();
                args38.push(Val::Str("aero-measurements".into()));
                fun40.call(args38, kw39)?
            });
            Ok(Val::None)
        })
    })?;
    // numbers
    e.set("numbers", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod41 = rt.import_module("_cold_core_data")?;
            e.set("read", rt.member("_cold_core_data", "read")?)?;
            let mod42 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            return Ok({
                let fun45 = e.get("read")?;
                let mut args43 = Vec::new();
                let mut kw44 = Vec::new();
                args43.push(Val::Str("aero-numbers".into()));
                kw44.push(("colors".into(), {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("aero".into()), {
                        let fun48 = e.get("list")?;
                        let mut args46 = Vec::new();
                        let mut kw47 = Vec::new();
                        args46.push({
                            let fun51 = e.get("linear")?;
                            let mut args49 = Vec::new();
                            let mut kw50 = Vec::new();
                            args49.push(Val::Str("#EEE4C4".into()));
                            fun51.call(args49, kw50)?
                        });
                        fun48.call(args46, kw47)?
                    })?;
                    d.set(Val::Str("magnet".into()), {
                        let fun54 = e.get("list")?;
                        let mut args52 = Vec::new();
                        let mut kw53 = Vec::new();
                        args52.push({
                            let fun57 = e.get("linear")?;
                            let mut args55 = Vec::new();
                            let mut kw56 = Vec::new();
                            args55.push(Val::Str("#737D88".into()));
                            fun57.call(args55, kw56)?
                        });
                        fun54.call(args52, kw53)?
                    })?;
                    d
                }));
                fun45.call(args43, kw44)?
            });
            Ok(Val::None)
        })
    })?;
    // write
    e.set("write", {
        let params = vec![("output".into(), Some(e.get("HERE")?), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            let mod58 = rt.import_module("flute_payload")?;
            e.set("write_print_payload", rt.member("flute_payload", "cut")?)?;
            let assigned59 = {
                let fun62 = e.get("Path")?;
                let mut args60 = Vec::new();
                let mut kw61 = Vec::new();
                args60.push(e.get("output")?);
                fun62.call(args60, kw61)?
            };
            e.set("output", assigned59.clone())?;
            {
                let fun65 = e.get("output")?.attr("mkdir")?;
                let mut args63 = Vec::new();
                let mut kw64 = Vec::new();
                kw64.push(("parents".into(), Val::Bool(true)));
                kw64.push(("exist_ok".into(), Val::Bool(true)));
                fun65.call(args63, kw64)?
            };
            {
                let fun68 = e.get("_rust_part")?.attr("cut")?;
                let mut args66 = Vec::new();
                let mut kw67 = Vec::new();
                args66.push(Val::Str("cold-core".into()));
                args66.push(Val::Str("all-aero-float".into()));
                args66.push({
                    let fun71 = e.get("numbers")?;
                    let mut args69 = Vec::new();
                    let mut kw70 = Vec::new();
                    fun71.call(args69, kw70)?
                });
                args66.push(e.get("output")?);
                fun68.call(args66, kw67)?
            };
            {
                let fun74 = e.get("write_print_payload")?;
                let mut args72 = Vec::new();
                let mut kw73 = Vec::new();
                args72.push(binary(
                    "truediv",
                    e.get("output")?,
                    Val::Str("float-aero.step".into()),
                )?);
                args72.push(binary(
                    "truediv",
                    e.get("output")?,
                    Val::Str("float-aero.stl".into()),
                )?);
                fun74.call(args72, kw73)?
            };
            let assigned75 = {
                let fun78 = e.get("measurements")?;
                let mut args76 = Vec::new();
                let mut kw77 = Vec::new();
                fun78.call(args76, kw77)?
            };
            e.set("info", assigned75.clone())?;
            {
                let fun81 = binary("truediv", e.get("output")?, Val::Str("design.json".into()))?
                    .attr("write_text")?;
                let mut args79 = Vec::new();
                let mut kw80 = Vec::new();
                args79.push(binary(
                    "add",
                    {
                        let fun84 = e.get("json")?.attr("dumps")?;
                        let mut args82 = Vec::new();
                        let mut kw83 = Vec::new();
                        args82.push(e.get("info")?);
                        kw83.push(("indent".into(), Val::Int(2i64)));
                        fun84.call(args82, kw83)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun81.call(args79, kw80)?
            };
            {
                let fun87 = e.get("print")?;
                let mut args85 = Vec::new();
                let mut kw86 = Vec::new();
                args85.push({
                    let fun90 = e.get("json")?.attr("dumps")?;
                    let mut args88 = Vec::new();
                    let mut kw89 = Vec::new();
                    args88.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("height_mm".into()), e.get("height")?)?;
                        d.set(
                            Val::Str("minimum_height_mm".into()),
                            e.get("minimum_height")?,
                        )?;
                        d.set(Val::Str("midplane_mm".into()), e.get("magnet_midplane")?)?;
                        d.set(
                            Val::Str("buoyancy".into()),
                            e.get("info")?.get(Val::Str("buoyancy".into()))?,
                        )?;
                        d
                    });
                    kw89.push(("indent".into(), Val::Int(2i64)));
                    fun90.call(args88, kw89)?
                });
                fun87.call(args85, kw86)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun93 = e.get("_rust_part")?.attr("start")?;
        let mut args91 = Vec::new();
        let mut kw92 = Vec::new();
        fun93.call(args91, kw92)?
    };
    let assigned94 = {
        let fun97 = e.get("argparse")?.attr("ArgumentParser")?;
        let mut args95 = Vec::new();
        let mut kw96 = Vec::new();
        kw96.push(("description".into(), e.get("__doc__")?));
        fun97.call(args95, kw96)?
    };
    e.set("parser", assigned94.clone())?;
    {
        let fun100 = e.get("parser")?.attr("add_argument")?;
        let mut args98 = Vec::new();
        let mut kw99 = Vec::new();
        args98.push(Val::Str("--output".into()));
        kw99.push(("type".into(), e.get("Path")?));
        kw99.push(("default".into(), e.get("HERE")?));
        fun100.call(args98, kw99)?
    };
    let assigned101 = {
        let fun104 = e.get("parser")?.attr("parse_args")?;
        let mut args102 = Vec::new();
        let mut kw103 = Vec::new();
        fun104.call(args102, kw103)?
    };
    e.set("args", assigned101.clone())?;
    {
        let fun107 = e.get("write")?;
        let mut args105 = Vec::new();
        let mut kw106 = Vec::new();
        args105.push(e.get("args")?.attr("output")?);
        fun107.call(args105, kw106)?
    };
    Ok(Val::None)
}
