#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("math", rt.import_module("math")?)?;
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
    };
    e.set("_here", assigned2.clone())?;
    let assigned9 = {
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
    };
    e.set("_hardware", assigned9.clone())?;
    {
        let fun19 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args17 = Vec::new();
        let mut kw18 = Vec::new();
        args17.push(Val::Int(0i64));
        args17.push({
            let fun22 = e.get("str")?;
            let mut args20 = Vec::new();
            let mut kw21 = Vec::new();
            args20.push(binary(
                "truediv",
                e.get("_hardware")?,
                Val::Str("scripts".into()),
            )?);
            fun22.call(args20, kw21)?
        });
        fun19.call(args17, kw18)?
    };
    {
        let fun25 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args23 = Vec::new();
        let mut kw24 = Vec::new();
        args23.push(Val::Int(0i64));
        args23.push({
            let fun28 = e.get("str")?;
            let mut args26 = Vec::new();
            let mut kw27 = Vec::new();
            args26.push(binary(
                "truediv",
                {
                    let fun31 = e.get("next")?;
                    let mut args29 = Vec::new();
                    let mut kw30 = Vec::new();
                    args29.push({
                        let e = e.child();
                        let out32 = Val::list(vec![]);
                        for item33 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item33)?;
                            if {
                                let fun36 = binary(
                                    "truediv",
                                    binary("truediv", e.get("p")?, Val::Str("tools".into()))?,
                                    Val::Str("docgen".into()),
                                )?
                                .attr("is_dir")?;
                                let mut args34 = Vec::new();
                                let mut kw35 = Vec::new();
                                fun36.call(args34, kw35)?
                            }
                            .truthy()?
                            {
                                out32.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out32
                    });
                    fun31.call(args29, kw30)?
                },
                Val::Str("tools".into()),
            )?);
            fun28.call(args26, kw27)?
        });
        fun25.call(args23, kw24)?
    };
    {
        let fun39 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args37 = Vec::new();
        let mut kw38 = Vec::new();
        args37.push(Val::Int(0i64));
        args37.push({
            let fun42 = e.get("str")?;
            let mut args40 = Vec::new();
            let mut kw41 = Vec::new();
            args40.push(e.get("_here")?.attr("parents")?.get(Val::Int(1i64))?);
            fun42.call(args40, kw41)?
        });
        fun39.call(args37, kw38)?
    };
    {
        let fun45 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args43 = Vec::new();
        let mut kw44 = Vec::new();
        args43.push(Val::Int(0i64));
        args43.push({
            let fun48 = e.get("str")?;
            let mut args46 = Vec::new();
            let mut kw47 = Vec::new();
            args46.push(binary(
                "truediv",
                e.get("_here")?.attr("parents")?.get(Val::Int(1i64))?,
                Val::Str("coil-mandrel".into()),
            )?);
            fun48.call(args46, kw47)?
        });
        fun45.call(args43, kw44)?
    };
    {
        let fun51 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args49 = Vec::new();
        let mut kw50 = Vec::new();
        args49.push(Val::Int(0i64));
        args49.push({
            let fun54 = e.get("str")?;
            let mut args52 = Vec::new();
            let mut kw53 = Vec::new();
            args52.push(binary(
                "truediv",
                binary(
                    "truediv",
                    binary("truediv", e.get("_hardware")?, Val::Str("cut-parts".into()))?,
                    Val::Str("carbonation".into()),
                )?,
                Val::Str("endcaps-circular".into()),
            )?);
            fun54.call(args52, kw53)?
        });
        fun51.call(args49, kw50)?
    };
    let mod55 = rt.import_module("docgen")?;
    e.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    e.set(
        "substitute_py_comments",
        rt.member("docgen", "substitute_py_comments")?,
    )?;
    let mod56 = rt.import_module("_cold_core_interface")?;
    e.set(
        "carbonator_outer_radius",
        rt.member("_cold_core_interface", "carbonator_outer_radius")?,
    )?;
    e.set(
        "carbonator_height",
        rt.member("_cold_core_interface", "carbonator_height")?,
    )?;
    e.set(
        "carbonator_support_ring_height",
        rt.member("_cold_core_interface", "carbonator_support_ring_height")?,
    )?;
    e.set(
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
    )?;
    e.set(
        "carbonator_float_top_stop_height",
        rt.member("_cold_core_interface", "carbonator_float_top_stop_height")?,
    )?;
    e.set(
        "carbonator_float_top_stop_diameter",
        rt.member("_cold_core_interface", "carbonator_float_top_stop_diameter")?,
    )?;
    let mod57 = rt.import_module("_cold_core_interface")?;
    e.set(
        "evap_tail_low_z",
        rt.member("_cold_core_interface", "evap_tail_low_z")?,
    )?;
    e.set(
        "evap_tail_high_z",
        rt.member("_cold_core_interface", "evap_tail_high_z")?,
    )?;
    let mod58 = rt.import_module("_materials")?;
    e.set("M_PETG_BLACK", rt.member("_materials", "M_PETG_BLACK")?)?;
    e.set("_fits", rt.import_module("fits")?)?;
    let mod59 = rt.import_module("coil_mandrel")?;
    e.set("pitch", rt.member("coil_mandrel", "pitch")?)?;
    e.set("tube_radius", rt.member("coil_mandrel", "tube_radius")?)?;
    e.set("wrap_length", rt.member("coil_mandrel", "wrap_length")?)?;
    let mod60 = rt.import_module("endcap_circular_dxf")?;
    e.set("tube_id", rt.member("endcap_circular_dxf", "tube_id")?)?;
    e.set(
        "register_radius",
        rt.member("endcap_circular_dxf", "register_radius")?,
    )?;
    e.set(
        "register_drill_diameter",
        rt.member("endcap_circular_dxf", "register_drill_diameter")?,
    )?;
    e.set(
        "disc_thickness",
        rt.member("endcap_circular_dxf", "disc_thickness")?,
    )?;
    e.set("_float", rt.import_module("_float_interface")?)?;
    let assigned61 = binary(
        "add",
        e.get("wall_and_floor_thickness")?,
        e.get("carbonator_support_ring_height")?,
    )?;
    e.set("tube_bottom_z_in_shell", assigned61.clone())?;
    let assigned62 = binary(
        "sub",
        e.get("evap_tail_low_z")?,
        e.get("tube_bottom_z_in_shell")?,
    )?;
    e.set("band_bottom_z", assigned62.clone())?;
    let assigned63 = binary(
        "sub",
        e.get("evap_tail_high_z")?,
        e.get("tube_bottom_z_in_shell")?,
    )?;
    e.set("band_top_z", assigned63.clone())?;
    let assigned64 = binary("mul", Val::Int(2i64), e.get("tube_radius")?)?;
    e.set("copper_od", assigned64.clone())?;
    let assigned65 = binary("sub", e.get("pitch")?, e.get("copper_od")?)?;
    e.set("inter_wrap_clear", assigned65.clone())?;
    let assigned66 = binary("mul", e.get("disc_thickness")?, Val::Float(25.4f64))?;
    e.set("plate_recess", assigned66.clone())?;
    let assigned67 = binary("mul", e.get("disc_thickness")?, Val::Float(25.4f64))?;
    e.set("plate_thickness", assigned67.clone())?;
    let assigned68 = binary("add", e.get("plate_recess")?, e.get("plate_thickness")?)?;
    e.set("interior_floor_z", assigned68.clone())?;
    let assigned69 = binary(
        "sub",
        binary("sub", e.get("carbonator_height")?, e.get("plate_recess")?)?,
        e.get("plate_thickness")?,
    )?;
    e.set("interior_ceiling_z", assigned69.clone())?;
    let assigned70 = binary(
        "sub",
        e.get("interior_ceiling_z")?,
        e.get("interior_floor_z")?,
    )?;
    e.set("interior_height", assigned70.clone())?;
    let assigned71 = binary("mul", e.get("tube_id")?, Val::Float(25.4f64))?;
    e.set("tube_id_mm", assigned71.clone())?;
    let assigned72 = binary(
        "mul",
        binary("truediv", e.get("math")?.attr("pi")?, Val::Int(4i64))?,
        binary(
            "sub",
            binary("pow", e.get("tube_id_mm")?, Val::Int(2i64))?,
            binary(
                "pow",
                e.get("_float")?.attr("guide_diameter")?,
                Val::Int(2i64),
            )?,
        )?,
    )?;
    e.set("interior_area", assigned72.clone())?;
    let assigned73 = binary("truediv", e.get("interior_area")?, Val::Int(1000i64))?;
    e.set("volume_per_mm", assigned73.clone())?;
    let assigned74 = binary(
        "truediv",
        binary(
            "mul",
            binary(
                "mul",
                binary("truediv", e.get("math")?.attr("pi")?, Val::Int(4i64))?,
                binary(
                    "sub",
                    binary(
                        "pow",
                        e.get("carbonator_float_top_stop_diameter")?,
                        Val::Int(2i64),
                    )?,
                    binary(
                        "pow",
                        binary(
                            "mul",
                            e.get("register_drill_diameter")?,
                            Val::Float(25.4f64),
                        )?,
                        Val::Int(2i64),
                    )?,
                )?,
            )?,
            e.get("carbonator_float_top_stop_height")?,
        )?,
        Val::Int(1000i64),
    )?;
    e.set("upper_stop_volume_ml", assigned74.clone())?;
    let assigned75 = binary(
        "sub",
        binary(
            "sub",
            binary("mul", e.get("volume_per_mm")?, e.get("interior_height")?)?,
            e.get("_float")?.attr("displacement_cc")?,
        )?,
        e.get("upper_stop_volume_ml")?,
    )?;
    e.set("interior_volume_ml", assigned75.clone())?;
    let assigned76 = Val::Float(355.0f64);
    e.set("serving_volume_ml", assigned76.clone())?;
    let assigned77 = Val::Float(20.0f64);
    e.set("syrup_dilution", assigned77.clone())?;
    let assigned78 = binary(
        "truediv",
        binary("mul", e.get("serving_volume_ml")?, e.get("syrup_dilution")?)?,
        binary("add", e.get("syrup_dilution")?, Val::Int(1i64))?,
    )?;
    e.set("carbonated_water_per_serving", assigned78.clone())?;
    let assigned79 = binary(
        "truediv",
        e.get("carbonated_water_per_serving")?,
        e.get("volume_per_mm")?,
    )?;
    e.set("serving_level_rise", assigned79.clone())?;
    let assigned80 = Val::Float(0.65f64);
    e.set("high_fill_fraction", assigned80.clone())?;
    let assigned81 = binary(
        "add",
        e.get("interior_floor_z")?,
        binary(
            "mul",
            e.get("high_fill_fraction")?,
            e.get("interior_height")?,
        )?,
    )?;
    e.set("high_level_z", assigned81.clone())?;
    let assigned82 = binary("sub", e.get("high_level_z")?, e.get("serving_level_rise")?)?;
    e.set("low_level_z", assigned82.clone())?;
    let assigned83 = binary("sub", e.get("interior_ceiling_z")?, e.get("high_level_z")?)?;
    e.set("headspace_height", assigned83.clone())?;
    let assigned84 = binary(
        "truediv",
        e.get("_float")?.attr("design_mass_g")?,
        e.get("_float")?.attr("water_density")?,
    )?;
    e.set("_immersed_float_cc", assigned84.clone())?;
    let assigned85 = binary(
        "sub",
        binary(
            "sub",
            binary("mul", e.get("headspace_height")?, e.get("volume_per_mm")?)?,
            binary(
                "sub",
                e.get("_float")?.attr("displacement_cc")?,
                e.get("_immersed_float_cc")?,
            )?,
        )?,
        e.get("upper_stop_volume_ml")?,
    )?;
    e.set("headspace_ml", assigned85.clone())?;
    let assigned86 = binary("sub", e.get("low_level_z")?, e.get("interior_floor_z")?)?;
    e.set("reserve_height", assigned86.clone())?;
    let assigned87 = binary(
        "sub",
        binary("mul", e.get("reserve_height")?, e.get("volume_per_mm")?)?,
        e.get("_immersed_float_cc")?,
    )?;
    e.set("reserve_ml", assigned87.clone())?;
    let assigned88 = binary(
        "sub",
        binary(
            "mul",
            binary("sub", e.get("high_level_z")?, e.get("interior_floor_z")?)?,
            e.get("volume_per_mm")?,
        )?,
        e.get("_immersed_float_cc")?,
    )?;
    e.set("stored_ml", assigned88.clone())?;
    let assigned89 = {
        let fun92 = e.get("_float")?.attr("magnet_above_waterline")?;
        let mut args90 = Vec::new();
        let mut kw91 = Vec::new();
        fun92.call(args90, kw91)?
    };
    e.set("magnet_lead_above_surface", assigned89.clone())?;
    let assigned93 = binary(
        "add",
        e.get("low_level_z")?,
        e.get("magnet_lead_above_surface")?,
    )?;
    e.set("reed_low_z", assigned93.clone())?;
    let assigned94 = binary(
        "add",
        e.get("high_level_z")?,
        e.get("magnet_lead_above_surface")?,
    )?;
    e.set("reed_high_z", assigned94.clone())?;
    let assigned95 = e.get("_float")?.attr("height")?;
    e.set("float_height", assigned95.clone())?;
    let assigned96 = Val::Float(1.5f64);
    e.set("rod_tack_fillet", assigned96.clone())?;
    let assigned97 = binary(
        "add",
        binary("add", e.get("interior_floor_z")?, e.get("rod_tack_fillet")?)?,
        binary("truediv", e.get("float_height")?, Val::Int(2i64))?,
    )?;
    e.set("magnet_lowest_z", assigned97.clone())?;
    let assigned98 = binary(
        "sub",
        binary(
            "sub",
            e.get("interior_ceiling_z")?,
            e.get("carbonator_float_top_stop_height")?,
        )?,
        binary("truediv", e.get("float_height")?, Val::Int(2i64))?,
    )?;
    e.set("magnet_highest_z", assigned98.clone())?;
    let assigned99 = binary(
        "sub",
        binary(
            "mul",
            binary(
                "sub",
                binary("truediv", e.get("tube_id")?, Val::Int(2i64))?,
                e.get("register_radius")?,
            )?,
            Val::Float(25.4f64),
        )?,
        binary(
            "truediv",
            e.get("_float")?.attr("diameter")?,
            Val::Int(2i64),
        )?,
    )?;
    e.set("float_wall_clearance", assigned99.clone())?;
    let assigned100 = e.get("_float")?.attr("reed_mount_length")?;
    e.set("reed_glass_length", assigned100.clone())?;
    let assigned101 = e.get("_float")?.attr("reed_mount_diameter")?;
    e.set("reed_glass_diameter", assigned101.clone())?;
    let assigned102 = e.get("_fits")?.attr("slip")?;
    e.set("seat_clearance", assigned102.clone())?;
    let assigned103 = binary(
        "add",
        e.get("carbonator_outer_radius")?,
        e.get("seat_clearance")?,
    )?;
    e.set("inner_radius", assigned103.clone())?;
    let assigned104 = Val::Float(0.8f64);
    e.set("skirt_thickness", assigned104.clone())?;
    let assigned105 = binary(
        "add",
        Val::Float(0.5f64),
        e.get("_fits")?.attr("supported_surface")?,
    )?;
    e.set("copper_clearance_over_glass", assigned105.clone())?;
    let assigned106 = binary(
        "add",
        e.get("reed_glass_diameter")?,
        e.get("copper_clearance_over_glass")?,
    )?;
    e.set("pocket_depth", assigned106.clone())?;
    let assigned107 = binary(
        "add",
        e.get("carbonator_outer_radius")?,
        e.get("pocket_depth")?,
    )?;
    e.set("plateau_radius", assigned107.clone())?;
    let assigned108 = binary("add", e.get("inner_radius")?, e.get("skirt_thickness")?)?;
    e.set("skirt_radius", assigned108.clone())?;
    let assigned109 = binary(
        "add",
        e.get("reed_glass_length")?,
        binary("mul", Val::Float(2.0f64), e.get("_fits")?.attr("slip")?)?,
    )?;
    e.set("pocket_length", assigned109.clone())?;
    let assigned110 = binary(
        "add",
        e.get("reed_glass_diameter")?,
        binary("mul", Val::Float(2.0f64), e.get("_fits")?.attr("slip")?)?,
    )?;
    e.set("pocket_width", assigned110.clone())?;
    let assigned111 = Val::Float(3.0f64);
    e.set("pocket_end_wall", assigned111.clone())?;
    let assigned112 = binary(
        "sub",
        binary(
            "sub",
            e.get("reed_low_z")?,
            binary("truediv", e.get("pocket_length")?, Val::Int(2i64))?,
        )?,
        e.get("pocket_end_wall")?,
    )?;
    e.set("plateau_z_bottom", assigned112.clone())?;
    let assigned113 = binary(
        "add",
        binary(
            "add",
            e.get("reed_high_z")?,
            binary("truediv", e.get("pocket_length")?, Val::Int(2i64))?,
        )?,
        e.get("pocket_end_wall")?,
    )?;
    e.set("plateau_z_top", assigned113.clone())?;
    let assigned114 = Val::Float(10.0f64);
    e.set("axial_ramp_length", assigned114.clone())?;
    let assigned115 = Val::Float(16.0f64);
    e.set("arc_ramp_width", assigned115.clone())?;
    let assigned116 = binary(
        "sub",
        e.get("plateau_z_bottom")?,
        e.get("axial_ramp_length")?,
    )?;
    e.set("bridge_z_bottom", assigned116.clone())?;
    let assigned117 = binary("add", e.get("plateau_z_top")?, e.get("axial_ramp_length")?)?;
    e.set("bridge_z_top", assigned117.clone())?;
    let assigned118 = binary("sub", e.get("bridge_z_top")?, e.get("bridge_z_bottom")?)?;
    e.set("bridge_height", assigned118.clone())?;
    let assigned119 = Val::Float(5.6f64);
    e.set("lead_groove_width", assigned119.clone())?;
    let assigned120 = binary("sub", e.get("plateau_radius")?, e.get("skirt_radius")?)?;
    e.set("lead_groove_depth", assigned120.clone())?;
    let assigned121 = Val::Float(5.4f64);
    e.set("lead_groove_y", assigned121.clone())?;
    let assigned122 = Val::Float(2.0f64);
    e.set("lead_notch_length", assigned122.clone())?;
    let assigned123 = binary(
        "add",
        binary(
            "add",
            e.get("lead_groove_y")?,
            binary("truediv", e.get("lead_groove_width")?, Val::Int(2i64))?,
        )?,
        Val::Float(1.5f64),
    )?;
    e.set("plateau_half_width", assigned123.clone())?;
    let assigned124 = binary(
        "add",
        e.get("plateau_half_width")?,
        e.get("arc_ramp_width")?,
    )?;
    e.set("bridge_half_width", assigned124.clone())?;
    let assigned125 = binary(
        "sub",
        e.get("plateau_radius")?,
        e.get("_fits")?.attr("supported_surface")?,
    )?;
    e.set("nominal_plateau_radius", assigned125.clone())?;
    let assigned126 = {
        let fun129 = e.get("math")?.attr("asin")?;
        let mut args127 = Vec::new();
        let mut kw128 = Vec::new();
        args127.push(binary(
            "truediv",
            e.get("plateau_half_width")?,
            e.get("nominal_plateau_radius")?,
        )?);
        fun129.call(args127, kw128)?
    };
    e.set("plateau_half_angle", assigned126.clone())?;
    let assigned130 = {
        let fun133 = e.get("math")?.attr("asin")?;
        let mut args131 = Vec::new();
        let mut kw132 = Vec::new();
        args131.push(binary(
            "truediv",
            e.get("bridge_half_width")?,
            e.get("nominal_plateau_radius")?,
        )?);
        fun133.call(args131, kw132)?
    };
    e.set("bridge_half_angle", assigned130.clone())?;
    let assigned134 = binary("truediv", e.get("bridge_height")?, e.get("pitch")?)?;
    e.set("wraps_carried", assigned134.clone())?;
    let assigned135 = binary(
        "add",
        binary("mul", Val::Int(2i64), e.get("plateau_half_width")?)?,
        e.get("arc_ramp_width")?,
    )?;
    e.set("effective_lift_arc", assigned135.clone())?;
    let assigned136 = binary("mul", e.get("wraps_carried")?, e.get("effective_lift_arc")?)?;
    e.set("carried_copper", assigned136.clone())?;
    let assigned137 = Val::Float(1.0f64);
    e.set("overcut", assigned137.clone())?;
    // _plan_outline_radius
    e.set("_plan_outline_radius", {
        let params = vec![("angle".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v141 = {
                    let fun140 = e.get("abs")?;
                    let mut args138 = Vec::new();
                    let mut kw139 = Vec::new();
                    args138.push(e.get("angle")?);
                    fun140.call(args138, kw139)?
                };
                let v142 = e.get("plateau_half_angle")?;
                Val::Bool(compare("le", v141.clone(), v142.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("plateau_radius")?);
            }
            let assigned143 = binary(
                "truediv",
                binary(
                    "sub",
                    {
                        let fun146 = e.get("abs")?;
                        let mut args144 = Vec::new();
                        let mut kw145 = Vec::new();
                        args144.push(e.get("angle")?);
                        fun146.call(args144, kw145)?
                    },
                    e.get("plateau_half_angle")?,
                )?,
                binary(
                    "sub",
                    e.get("bridge_half_angle")?,
                    e.get("plateau_half_angle")?,
                )?,
            )?;
            e.set("fraction", assigned143.clone())?;
            return Ok(binary(
                "sub",
                e.get("plateau_radius")?,
                binary(
                    "mul",
                    e.get("fraction")?,
                    binary("sub", e.get("plateau_radius")?, e.get("skirt_radius")?)?,
                )?,
            )?);
            Ok(Val::None)
        })
    })?;
    let assigned147 = Val::Float(60.0f64);
    e.set("gauge_arc_degrees", assigned147.clone())?;
    let assigned148 = Val::Float(3.0f64);
    e.set("gauge_wall", assigned148.clone())?;
    let assigned149 = Val::Float(3.5f64);
    e.set("gauge_hook_depth", assigned149.clone())?;
    let assigned150 = Val::Float(4.0f64);
    e.set("gauge_hook_height", assigned150.clone())?;
    // numbers
    e.set("numbers", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod151 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            // box
            e.set("box", {
                let params = vec![
                    ("x".into(), None, false),
                    ("y".into(), None, false),
                    ("z".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let mut s = Vec::new();
                        s.push({
                            let fun154 = e.get("list")?;
                            let mut args152 = Vec::new();
                            let mut kw153 = Vec::new();
                            args152.push(e.get("x")?);
                            fun154.call(args152, kw153)?
                        });
                        s.push({
                            let fun157 = e.get("list")?;
                            let mut args155 = Vec::new();
                            let mut kw156 = Vec::new();
                            args155.push(e.get("y")?);
                            fun157.call(args155, kw156)?
                        });
                        s.push({
                            let fun160 = e.get("list")?;
                            let mut args158 = Vec::new();
                            let mut kw159 = Vec::new();
                            args158.push(e.get("z")?);
                            fun160.call(args158, kw159)?
                        });
                        Val::list(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned161 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("outline", assigned161.clone())?;
            for item162 in {
                let fun179 = e.get("range")?;
                let mut args177 = Vec::new();
                let mut kw178 = Vec::new();
                args177.push(Val::Int(49i64));
                fun179.call(args177, kw178)?
            }
            .iter()?
            {
                e.set("i", item162)?;
                let assigned163 = binary(
                    "add",
                    unary("neg", e.get("bridge_half_angle")?)?,
                    binary(
                        "truediv",
                        binary(
                            "mul",
                            binary("mul", Val::Int(2i64), e.get("bridge_half_angle")?)?,
                            e.get("i")?,
                        )?,
                        Val::Int(48i64),
                    )?,
                )?;
                e.set("angle", assigned163.clone())?;
                let assigned164 = {
                    let fun167 = e.get("_plan_outline_radius")?;
                    let mut args165 = Vec::new();
                    let mut kw166 = Vec::new();
                    args165.push(e.get("angle")?);
                    fun167.call(args165, kw166)?
                };
                e.set("radius", assigned164.clone())?;
                {
                    let fun170 = e.get("outline")?.attr("append")?;
                    let mut args168 = Vec::new();
                    let mut kw169 = Vec::new();
                    args168.push({
                        let mut s = Vec::new();
                        s.push(binary("mul", e.get("radius")?, {
                            let fun173 = e.get("math")?.attr("cos")?;
                            let mut args171 = Vec::new();
                            let mut kw172 = Vec::new();
                            args171.push(e.get("angle")?);
                            fun173.call(args171, kw172)?
                        })?);
                        s.push(binary("mul", e.get("radius")?, {
                            let fun176 = e.get("math")?.attr("sin")?;
                            let mut args174 = Vec::new();
                            let mut kw175 = Vec::new();
                            args174.push(e.get("angle")?);
                            fun176.call(args174, kw175)?
                        })?);
                        Val::tuple(s)
                    });
                    fun170.call(args168, kw169)?
                };
            }
            let assigned180 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                Val::tuple(s)
            };
            let unpack181 = unpack(assigned180.clone(), 2)?;
            e.set("pockets", unpack181[0].clone())?;
            e.set("notches", unpack181[1].clone())?;
            for item182 in {
                let mut s = Vec::new();
                s.push(e.get("reed_low_z")?);
                s.push(e.get("reed_high_z")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("reed_z", item182)?;
                {
                    let fun185 = e.get("pockets")?.attr("append")?;
                    let mut args183 = Vec::new();
                    let mut kw184 = Vec::new();
                    args183.push({
                        let fun188 = e.get("box")?;
                        let mut args186 = Vec::new();
                        let mut kw187 = Vec::new();
                        args186.push({
                            let mut s = Vec::new();
                            s.push(binary("sub", e.get("inner_radius")?, e.get("overcut")?)?);
                            s.push(binary("add", e.get("plateau_radius")?, e.get("overcut")?)?);
                            Val::tuple(s)
                        });
                        args186.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "truediv",
                                unary("neg", e.get("pocket_width")?)?,
                                Val::Int(2i64),
                            )?);
                            s.push(binary("truediv", e.get("pocket_width")?, Val::Int(2i64))?);
                            Val::tuple(s)
                        });
                        args186.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "sub",
                                e.get("reed_z")?,
                                binary("truediv", e.get("pocket_length")?, Val::Int(2i64))?,
                            )?);
                            s.push(binary(
                                "add",
                                e.get("reed_z")?,
                                binary("truediv", e.get("pocket_length")?, Val::Int(2i64))?,
                            )?);
                            Val::tuple(s)
                        });
                        fun188.call(args186, kw187)?
                    });
                    fun185.call(args183, kw184)?
                };
                for item189 in {
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("reed_z")?,
                        binary("truediv", e.get("pocket_length")?, Val::Int(2i64))?,
                    )?);
                    s.push(binary(
                        "sub",
                        binary(
                            "add",
                            e.get("reed_z")?,
                            binary("truediv", e.get("pocket_length")?, Val::Int(2i64))?,
                        )?,
                        e.get("lead_notch_length")?,
                    )?);
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("z", item189)?;
                    {
                        let fun192 = e.get("notches")?.attr("append")?;
                        let mut args190 = Vec::new();
                        let mut kw191 = Vec::new();
                        args190.push({
                            let fun195 = e.get("box")?;
                            let mut args193 = Vec::new();
                            let mut kw194 = Vec::new();
                            args193.push({
                                let mut s = Vec::new();
                                s.push(e.get("skirt_radius")?);
                                s.push(binary("add", e.get("plateau_radius")?, e.get("overcut")?)?);
                                Val::tuple(s)
                            });
                            args193.push({
                                let mut s = Vec::new();
                                s.push(binary(
                                    "truediv",
                                    unary("neg", e.get("pocket_width")?)?,
                                    Val::Int(2i64),
                                )?);
                                s.push(binary(
                                    "add",
                                    e.get("lead_groove_y")?,
                                    binary("truediv", e.get("lead_groove_width")?, Val::Int(2i64))?,
                                )?);
                                Val::tuple(s)
                            });
                            args193.push({
                                let mut s = Vec::new();
                                s.push(e.get("z")?);
                                s.push(binary("add", e.get("z")?, e.get("lead_notch_length")?)?);
                                Val::tuple(s)
                            });
                            fun195.call(args193, kw194)?
                        });
                        fun192.call(args190, kw191)?
                    };
                }
            }
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("ridge_section".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("inner_radius")?);
                        s.push(e.get("bridge_z_bottom")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("skirt_radius")?);
                        s.push(e.get("bridge_z_bottom")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("plateau_radius")?);
                        s.push(e.get("plateau_z_bottom")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("plateau_radius")?);
                        s.push(e.get("plateau_z_top")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("skirt_radius")?);
                        s.push(e.get("bridge_z_top")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("inner_radius")?);
                        s.push(e.get("bridge_z_top")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                })?;
                d.set(Val::Str("plan_outline".into()), e.get("outline")?)?;
                d.set(
                    Val::Str("plan_bottom".into()),
                    binary("sub", e.get("bridge_z_bottom")?, e.get("overcut")?)?,
                )?;
                d.set(
                    Val::Str("plan_height".into()),
                    binary(
                        "add",
                        e.get("bridge_height")?,
                        binary("mul", Val::Int(2i64), e.get("overcut")?)?,
                    )?,
                )?;
                d.set(Val::Str("pockets".into()), e.get("pockets")?)?;
                d.set(Val::Str("notches".into()), e.get("notches")?)?;
                d.set(Val::Str("lead_groove".into()), {
                    let fun198 = e.get("box")?;
                    let mut args196 = Vec::new();
                    let mut kw197 = Vec::new();
                    args196.push({
                        let mut s = Vec::new();
                        s.push(e.get("skirt_radius")?);
                        s.push(binary("add", e.get("plateau_radius")?, e.get("overcut")?)?);
                        Val::tuple(s)
                    });
                    args196.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("lead_groove_y")?,
                            binary("truediv", e.get("lead_groove_width")?, Val::Int(2i64))?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("lead_groove_y")?,
                            binary("truediv", e.get("lead_groove_width")?, Val::Int(2i64))?,
                        )?);
                        Val::tuple(s)
                    });
                    args196.push({
                        let mut s = Vec::new();
                        s.push(e.get("plateau_z_bottom")?);
                        s.push(binary("add", e.get("bridge_z_top")?, e.get("overcut")?)?);
                        Val::tuple(s)
                    });
                    fun198.call(args196, kw197)?
                })?;
                d.set(Val::Str("gauge_section".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("inner_radius")?,
                            e.get("gauge_hook_depth")?,
                        )?);
                        s.push(unary("neg", e.get("gauge_hook_height")?)?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("inner_radius")?, e.get("gauge_wall")?)?);
                        s.push(unary("neg", e.get("gauge_hook_height")?)?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("inner_radius")?, e.get("gauge_wall")?)?);
                        s.push(e.get("bridge_z_bottom")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("inner_radius")?);
                        s.push(e.get("bridge_z_bottom")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("inner_radius")?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("inner_radius")?,
                            e.get("gauge_hook_depth")?,
                        )?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                })?;
                d.set(
                    Val::Str("gauge_arc_degrees".into()),
                    e.get("gauge_arc_degrees")?,
                )?;
                d.set(Val::Str("color".into()), {
                    let fun201 = e.get("list")?;
                    let mut args199 = Vec::new();
                    let mut kw200 = Vec::new();
                    args199.push({
                        let fun204 = e.get("linear")?;
                        let mut args202 = Vec::new();
                        let mut kw203 = Vec::new();
                        args202.push(e.get("M_PETG_BLACK")?);
                        fun204.call(args202, kw203)?
                    });
                    fun201.call(args199, kw200)?
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![("output".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if !{
                let v205 = e.get("reed_low_z")?;
                let v206 = e.get("magnet_lowest_z")?;
                Val::Bool(compare("gt", v205.clone(), v206.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string(Val::Str("low reed below the donut's reach".into()))?
                );
            }
            if !{
                let v207 = e.get("reed_high_z")?;
                let v208 = e.get("magnet_highest_z")?;
                Val::Bool(compare("lt", v207.clone(), v208.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string(Val::Str("high reed above the donut's reach".into()))?
                );
            }
            {
                let fun211 = e.get("print")?;
                let mut args209 = Vec::new();
                let mut kw210 = Vec::new();
                args209.push({
                    let mut str212 = String::new();
                    str212.push_str("Wind band on the tube:  ");
                    str212.push_str(&format(
                        &e.get("band_bottom_z")?,
                        &val_string({
                            let mut str213 = String::new();
                            str213.push_str(".1f");
                            Val::Str(str213)
                        })?,
                    )?);
                    str212.push_str(" .. ");
                    str212.push_str(&format(
                        &e.get("band_top_z")?,
                        &val_string({
                            let mut str214 = String::new();
                            str214.push_str(".1f");
                            Val::Str(str214)
                        })?,
                    )?);
                    str212.push_str(" mm (pitch ");
                    str212.push_str(&format(
                        &e.get("pitch")?,
                        &val_string({
                            let mut str215 = String::new();
                            str215.push_str(".3f");
                            Val::Str(str215)
                        })?,
                    )?);
                    str212.push_str(", clear channel ");
                    str212.push_str(&format(
                        &e.get("inter_wrap_clear")?,
                        &val_string({
                            let mut str216 = String::new();
                            str216.push_str(".3f");
                            Val::Str(str216)
                        })?,
                    )?);
                    str212.push_str(")");
                    Val::Str(str212)
                });
                fun211.call(args209, kw210)?
            };
            {
                let fun219 = e.get("print")?;
                let mut args217 = Vec::new();
                let mut kw218 = Vec::new();
                args217.push({
                    let mut str220 = String::new();
                    str220.push_str("Wetted column:          ");
                    str220.push_str(&format(
                        &e.get("interior_floor_z")?,
                        &val_string({
                            let mut str221 = String::new();
                            str221.push_str(".2f");
                            Val::Str(str221)
                        })?,
                    )?);
                    str220.push_str(" .. ");
                    str220.push_str(&format(
                        &e.get("interior_ceiling_z")?,
                        &val_string({
                            let mut str222 = String::new();
                            str222.push_str(".2f");
                            Val::Str(str222)
                        })?,
                    )?);
                    str220.push_str(" mm = ");
                    str220.push_str(&format(
                        &e.get("interior_height")?,
                        &val_string({
                            let mut str223 = String::new();
                            str223.push_str(".2f");
                            Val::Str(str223)
                        })?,
                    )?);
                    str220.push_str(" mm, ");
                    str220.push_str(&format(
                        &e.get("volume_per_mm")?,
                        &val_string({
                            let mut str224 = String::new();
                            str224.push_str(".3f");
                            Val::Str(str224)
                        })?,
                    )?);
                    str220.push_str(" mL/mm, ");
                    str220.push_str(&format(
                        &e.get("interior_volume_ml")?,
                        &val_string({
                            let mut str225 = String::new();
                            str225.push_str(".0f");
                            Val::Str(str225)
                        })?,
                    )?);
                    str220.push_str(" mL");
                    Val::Str(str220)
                });
                fun219.call(args217, kw218)?
            };
            {
                let fun228 = e.get("print")?;
                let mut args226 = Vec::new();
                let mut kw227 = Vec::new();
                args226.push({
                    let mut str229 = String::new();
                    str229.push_str("Serving:                ");
                    str229.push_str(&format(
                        &e.get("carbonated_water_per_serving")?,
                        &val_string({
                            let mut str230 = String::new();
                            str230.push_str(".1f");
                            Val::Str(str230)
                        })?,
                    )?);
                    str229.push_str(" mL water = ");
                    str229.push_str(&format(
                        &e.get("serving_level_rise")?,
                        &val_string({
                            let mut str231 = String::new();
                            str231.push_str(".2f");
                            Val::Str(str231)
                        })?,
                    )?);
                    str229.push_str(" mm of level");
                    Val::Str(str229)
                });
                fun228.call(args226, kw227)?
            };
            {
                let fun234 = e.get("print")?;
                let mut args232 = Vec::new();
                let mut kw233 = Vec::new();
                args232.push({
                    let mut str235 = String::new();
                    str235.push_str("CHI (pump off):         level ");
                    str235.push_str(&format(
                        &e.get("high_level_z")?,
                        &val_string({
                            let mut str236 = String::new();
                            str236.push_str(".2f");
                            Val::Str(str236)
                        })?,
                    )?);
                    str235.push_str(" mm  stored ");
                    str235.push_str(&format(
                        &e.get("stored_ml")?,
                        &val_string({
                            let mut str237 = String::new();
                            str237.push_str(".0f");
                            Val::Str(str237)
                        })?,
                    )?);
                    str235.push_str(" mL = ");
                    str235.push_str(&format(
                        &binary(
                            "truediv",
                            e.get("stored_ml")?,
                            e.get("carbonated_water_per_serving")?,
                        )?,
                        &val_string({
                            let mut str238 = String::new();
                            str238.push_str(".2f");
                            Val::Str(str238)
                        })?,
                    )?);
                    str235.push_str(" servings, headspace ");
                    str235.push_str(&format(
                        &e.get("headspace_ml")?,
                        &val_string({
                            let mut str239 = String::new();
                            str239.push_str(".0f");
                            Val::Str(str239)
                        })?,
                    )?);
                    str235.push_str(" mL (");
                    str235.push_str(&format(
                        &binary(
                            "sub",
                            Val::Int(100i64),
                            binary("mul", Val::Int(100i64), e.get("high_fill_fraction")?)?,
                        )?,
                        &val_string({
                            let mut str240 = String::new();
                            str240.push_str(".0f");
                            Val::Str(str240)
                        })?,
                    )?);
                    str235.push_str(" %)");
                    Val::Str(str235)
                });
                fun234.call(args232, kw233)?
            };
            {
                let fun243 = e.get("print")?;
                let mut args241 = Vec::new();
                let mut kw242 = Vec::new();
                args241.push({
                    let mut str244 = String::new();
                    str244.push_str("CLO (pump on):          level ");
                    str244.push_str(&format(
                        &e.get("low_level_z")?,
                        &val_string({
                            let mut str245 = String::new();
                            str245.push_str(".2f");
                            Val::Str(str245)
                        })?,
                    )?);
                    str244.push_str(" mm  reserve ");
                    str244.push_str(&format(
                        &e.get("reserve_ml")?,
                        &val_string({
                            let mut str246 = String::new();
                            str246.push_str(".0f");
                            Val::Str(str246)
                        })?,
                    )?);
                    str244.push_str(" mL = ");
                    str244.push_str(&format(
                        &binary(
                            "truediv",
                            e.get("reserve_ml")?,
                            e.get("carbonated_water_per_serving")?,
                        )?,
                        &val_string({
                            let mut str247 = String::new();
                            str247.push_str(".2f");
                            Val::Str(str247)
                        })?,
                    )?);
                    str244.push_str(" servings, band ");
                    str244.push_str(&format(
                        &e.get("serving_level_rise")?,
                        &val_string({
                            let mut str248 = String::new();
                            str248.push_str(".2f");
                            Val::Str(str248)
                        })?,
                    )?);
                    str244.push_str(" mm = 1.00 serving");
                    Val::Str(str244)
                });
                fun243.call(args241, kw242)?
            };
            {
                let fun251 = e.get("print")?;
                let mut args249 = Vec::new();
                let mut kw250 = Vec::new();
                args249.push({
                    let mut str252 = String::new();
                    str252.push_str("RC62 midplane reach:    ");
                    str252.push_str(&format(
                        &e.get("magnet_lowest_z")?,
                        &val_string({
                            let mut str253 = String::new();
                            str253.push_str(".1f");
                            Val::Str(str253)
                        })?,
                    )?);
                    str252.push_str(" .. ");
                    str252.push_str(&format(
                        &e.get("magnet_highest_z")?,
                        &val_string({
                            let mut str254 = String::new();
                            str254.push_str(".1f");
                            Val::Str(str254)
                        })?,
                    )?);
                    str252.push_str(" mm (nominal body/wall clearance ");
                    str252.push_str(&format(
                        &e.get("float_wall_clearance")?,
                        &val_string({
                            let mut str255 = String::new();
                            str255.push_str(".2f");
                            Val::Str(str255)
                        })?,
                    )?);
                    str252.push_str(" mm)");
                    Val::Str(str252)
                });
                fun251.call(args249, kw250)?
            };
            {
                let fun258 = e.get("print")?;
                let mut args256 = Vec::new();
                let mut kw257 = Vec::new();
                args256.push({
                    let mut str259 = String::new();
                    str259.push_str("Bridge:                 Z ");
                    str259.push_str(&format(
                        &e.get("bridge_z_bottom")?,
                        &val_string({
                            let mut str260 = String::new();
                            str260.push_str(".2f");
                            Val::Str(str260)
                        })?,
                    )?);
                    str259.push_str(" .. ");
                    str259.push_str(&format(
                        &e.get("bridge_z_top")?,
                        &val_string({
                            let mut str261 = String::new();
                            str261.push_str(".2f");
                            Val::Str(str261)
                        })?,
                    )?);
                    str259.push_str(" (");
                    str259.push_str(&format(
                        &e.get("bridge_height")?,
                        &val_string({
                            let mut str262 = String::new();
                            str262.push_str(".2f");
                            Val::Str(str262)
                        })?,
                    )?);
                    str259.push_str(" mm), arc ");
                    str259.push_str(&format(
                        &binary("mul", Val::Int(2i64), e.get("bridge_half_width")?)?,
                        &val_string({
                            let mut str263 = String::new();
                            str263.push_str(".1f");
                            Val::Str(str263)
                        })?,
                    )?);
                    str259.push_str(" mm, ");
                    str259.push_str(&format(
                        &e.get("pocket_depth")?,
                        &val_string({
                            let mut str264 = String::new();
                            str264.push_str(".1f");
                            Val::Str(str264)
                        })?,
                    )?);
                    str259.push_str(" mm proud");
                    Val::Str(str259)
                });
                fun258.call(args256, kw257)?
            };
            {
                let fun267 = e.get("print")?;
                let mut args265 = Vec::new();
                let mut kw266 = Vec::new();
                args265.push({
                    let mut str268 = String::new();
                    str268.push_str("Copper carried:         ");
                    str268.push_str(&format(
                        &e.get("wraps_carried")?,
                        &val_string({
                            let mut str269 = String::new();
                            str269.push_str(".2f");
                            Val::Str(str269)
                        })?,
                    )?);
                    str268.push_str(" wraps x ");
                    str268.push_str(&format(
                        &e.get("effective_lift_arc")?,
                        &val_string({
                            let mut str270 = String::new();
                            str270.push_str(".1f");
                            Val::Str(str270)
                        })?,
                    )?);
                    str268.push_str(" mm = ");
                    str268.push_str(&format(
                        &e.get("carried_copper")?,
                        &val_string({
                            let mut str271 = String::new();
                            str271.push_str(".0f");
                            Val::Str(str271)
                        })?,
                    )?);
                    str268.push_str(" mm");
                    Val::Str(str268)
                });
                fun267.call(args265, kw266)?
            };
            let assigned272 = if {
                let v273 = e.get("output")?;
                let v274 = Val::None;
                Val::Bool(compare("is_not", v273.clone(), v274.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun277 = e.get("Path")?;
                    let mut args275 = Vec::new();
                    let mut kw276 = Vec::new();
                    args275.push(e.get("output")?);
                    fun277.call(args275, kw276)?
                }
            } else {
                e.get("_here")?.attr("parent")?
            };
            e.set("out_dir", assigned272.clone())?;
            {
                let fun280 = e.get("out_dir")?.attr("mkdir")?;
                let mut args278 = Vec::new();
                let mut kw279 = Vec::new();
                kw279.push(("parents".into(), Val::Bool(true)));
                kw279.push(("exist_ok".into(), Val::Bool(true)));
                fun280.call(args278, kw279)?
            };
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            let assigned281 = {
                let fun284 = e.get("_rust_part")?.attr("cut")?;
                let mut args282 = Vec::new();
                let mut kw283 = Vec::new();
                args282.push(Val::Str("cold-core".into()));
                args282.push(Val::Str("reed-bridge".into()));
                args282.push({
                    let fun287 = e.get("numbers")?;
                    let mut args285 = Vec::new();
                    let mut kw286 = Vec::new();
                    fun287.call(args285, kw286)?
                });
                args282.push(e.get("out_dir")?);
                fun284.call(args282, kw283)?
            }
            .get(Val::Str("bodies".into()))?;
            e.set("bodies", assigned281.clone())?;
            let assigned288 = {
                let e = e.child();
                let out289 = Val::list(vec![]);
                for item290 in e.get("bodies")?.iter()? {
                    e.set("body", item290)?;
                    out289
                        .attr("append")?
                        .call(vec![e.get("body")?.get(Val::Str("volume".into()))?], vec![])?;
                }
                out289
            };
            let unpack291 = unpack(assigned288.clone(), 2)?;
            e.set("bridge_volume", unpack291[0].clone())?;
            e.set("gauge_volume", unpack291[1].clone())?;
            {
                let fun294 = e.get("document")?;
                let mut args292 = Vec::new();
                let mut kw293 = Vec::new();
                args292.push(e.get("bridge_volume")?);
                args292.push(e.get("gauge_volume")?);
                fun294.call(args292, kw293)?
            };
            Ok(Val::None)
        })
    })?;
    // document
    e.set("document", {
        let params = vec![
            ("bridge_volume".into(), None, false),
            ("gauge_volume".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned295 = e.get("_here")?.attr("parent")?;
            e.set("out_dir", assigned295.clone())?;
            let assigned296 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("BAND_BOTTOM".into()), {
                    let mut str297 = String::new();
                    str297.push_str(&format(
                        &e.get("band_bottom_z")?,
                        &val_string({
                            let mut str298 = String::new();
                            str298.push_str(".4g");
                            Val::Str(str298)
                        })?,
                    )?);
                    str297.push_str(" mm");
                    Val::Str(str297)
                })?;
                d.set(Val::Str("BAND_TOP".into()), {
                    let mut str299 = String::new();
                    str299.push_str(&format(
                        &e.get("band_top_z")?,
                        &val_string({
                            let mut str300 = String::new();
                            str300.push_str(".4g");
                            Val::Str(str300)
                        })?,
                    )?);
                    str299.push_str(" mm");
                    Val::Str(str299)
                })?;
                d.set(Val::Str("WRAP_PITCH".into()), {
                    let mut str301 = String::new();
                    str301.push_str(&format(
                        &e.get("pitch")?,
                        &val_string({
                            let mut str302 = String::new();
                            str302.push_str(".4g");
                            Val::Str(str302)
                        })?,
                    )?);
                    str301.push_str(" mm");
                    Val::Str(str301)
                })?;
                d.set(Val::Str("COPPER_OD".into()), {
                    let mut str303 = String::new();
                    str303.push_str(&format(
                        &e.get("copper_od")?,
                        &val_string({
                            let mut str304 = String::new();
                            str304.push_str(".4g");
                            Val::Str(str304)
                        })?,
                    )?);
                    str303.push_str(" mm");
                    Val::Str(str303)
                })?;
                d.set(Val::Str("INTER_WRAP_CLEAR".into()), {
                    let mut str305 = String::new();
                    str305.push_str(&format(
                        &e.get("inter_wrap_clear")?,
                        &val_string({
                            let mut str306 = String::new();
                            str306.push_str(".4g");
                            Val::Str(str306)
                        })?,
                    )?);
                    str305.push_str(" mm");
                    Val::Str(str305)
                })?;
                d.set(Val::Str("INTERIOR_FLOOR".into()), {
                    let mut str307 = String::new();
                    str307.push_str(&format(
                        &e.get("interior_floor_z")?,
                        &val_string({
                            let mut str308 = String::new();
                            str308.push_str(".4g");
                            Val::Str(str308)
                        })?,
                    )?);
                    str307.push_str(" mm");
                    Val::Str(str307)
                })?;
                d.set(Val::Str("INTERIOR_CEILING".into()), {
                    let mut str309 = String::new();
                    str309.push_str(&format(
                        &e.get("interior_ceiling_z")?,
                        &val_string({
                            let mut str310 = String::new();
                            str310.push_str(".4g");
                            Val::Str(str310)
                        })?,
                    )?);
                    str309.push_str(" mm");
                    Val::Str(str309)
                })?;
                d.set(Val::Str("INTERIOR_H".into()), {
                    let mut str311 = String::new();
                    str311.push_str(&format(
                        &e.get("interior_height")?,
                        &val_string({
                            let mut str312 = String::new();
                            str312.push_str(".4g");
                            Val::Str(str312)
                        })?,
                    )?);
                    str311.push_str(" mm");
                    Val::Str(str311)
                })?;
                d.set(Val::Str("TUBE_ID_MM".into()), {
                    let mut str313 = String::new();
                    str313.push_str(&format(
                        &e.get("tube_id_mm")?,
                        &val_string({
                            let mut str314 = String::new();
                            str314.push_str(".4g");
                            Val::Str(str314)
                        })?,
                    )?);
                    str313.push_str(" mm");
                    Val::Str(str313)
                })?;
                d.set(Val::Str("ML_PER_MM".into()), {
                    let mut str315 = String::new();
                    str315.push_str(&format(
                        &e.get("volume_per_mm")?,
                        &val_string({
                            let mut str316 = String::new();
                            str316.push_str(".4g");
                            Val::Str(str316)
                        })?,
                    )?);
                    str315.push_str(" mL");
                    Val::Str(str315)
                })?;
                d.set(Val::Str("INTERIOR_ML".into()), {
                    let mut str317 = String::new();
                    str317.push_str(&format(
                        &e.get("interior_volume_ml")?,
                        &val_string({
                            let mut str318 = String::new();
                            str318.push_str(".4g");
                            Val::Str(str318)
                        })?,
                    )?);
                    str317.push_str(" mL");
                    Val::Str(str317)
                })?;
                d.set(Val::Str("WATER_PER_SERVING".into()), {
                    let mut str319 = String::new();
                    str319.push_str(&format(
                        &e.get("carbonated_water_per_serving")?,
                        &val_string({
                            let mut str320 = String::new();
                            str320.push_str(".4g");
                            Val::Str(str320)
                        })?,
                    )?);
                    str319.push_str(" mL");
                    Val::Str(str319)
                })?;
                d.set(Val::Str("SERVING_RISE".into()), {
                    let mut str321 = String::new();
                    str321.push_str(&format(
                        &e.get("serving_level_rise")?,
                        &val_string({
                            let mut str322 = String::new();
                            str322.push_str(".4g");
                            Val::Str(str322)
                        })?,
                    )?);
                    str321.push_str(" mm");
                    Val::Str(str321)
                })?;
                d.set(Val::Str("HIGH_LEVEL".into()), {
                    let mut str323 = String::new();
                    str323.push_str(&format(
                        &e.get("high_level_z")?,
                        &val_string({
                            let mut str324 = String::new();
                            str324.push_str(".4g");
                            Val::Str(str324)
                        })?,
                    )?);
                    str323.push_str(" mm");
                    Val::Str(str323)
                })?;
                d.set(Val::Str("LOW_LEVEL".into()), {
                    let mut str325 = String::new();
                    str325.push_str(&format(
                        &e.get("low_level_z")?,
                        &val_string({
                            let mut str326 = String::new();
                            str326.push_str(".4g");
                            Val::Str(str326)
                        })?,
                    )?);
                    str325.push_str(" mm");
                    Val::Str(str325)
                })?;
                d.set(Val::Str("HEADSPACE_ML".into()), {
                    let mut str327 = String::new();
                    str327.push_str(&format(
                        &e.get("headspace_ml")?,
                        &val_string({
                            let mut str328 = String::new();
                            str328.push_str(".4g");
                            Val::Str(str328)
                        })?,
                    )?);
                    str327.push_str(" mL");
                    Val::Str(str327)
                })?;
                d.set(Val::Str("RESERVE_ML".into()), {
                    let mut str329 = String::new();
                    str329.push_str(&format(
                        &e.get("reserve_ml")?,
                        &val_string({
                            let mut str330 = String::new();
                            str330.push_str(".4g");
                            Val::Str(str330)
                        })?,
                    )?);
                    str329.push_str(" mL");
                    Val::Str(str329)
                })?;
                d.set(Val::Str("RESERVE_SERVINGS".into()), {
                    let mut str331 = String::new();
                    str331.push_str(&format(
                        &binary(
                            "truediv",
                            e.get("reserve_ml")?,
                            e.get("carbonated_water_per_serving")?,
                        )?,
                        &val_string({
                            let mut str332 = String::new();
                            str332.push_str(".3g");
                            Val::Str(str332)
                        })?,
                    )?);
                    Val::Str(str331)
                })?;
                d.set(Val::Str("STORED_ML".into()), {
                    let mut str333 = String::new();
                    str333.push_str(&format(
                        &e.get("stored_ml")?,
                        &val_string({
                            let mut str334 = String::new();
                            str334.push_str(".4g");
                            Val::Str(str334)
                        })?,
                    )?);
                    str333.push_str(" mL");
                    Val::Str(str333)
                })?;
                d.set(Val::Str("STORED_SERVINGS".into()), {
                    let mut str335 = String::new();
                    str335.push_str(&format(
                        &binary(
                            "truediv",
                            e.get("stored_ml")?,
                            e.get("carbonated_water_per_serving")?,
                        )?,
                        &val_string({
                            let mut str336 = String::new();
                            str336.push_str(".3g");
                            Val::Str(str336)
                        })?,
                    )?);
                    Val::Str(str335)
                })?;
                d.set(Val::Str("MAGNET_LOWEST".into()), {
                    let mut str337 = String::new();
                    str337.push_str(&format(
                        &e.get("magnet_lowest_z")?,
                        &val_string({
                            let mut str338 = String::new();
                            str338.push_str(".4g");
                            Val::Str(str338)
                        })?,
                    )?);
                    str337.push_str(" mm");
                    Val::Str(str337)
                })?;
                d.set(Val::Str("MAGNET_HIGHEST".into()), {
                    let mut str339 = String::new();
                    str339.push_str(&format(
                        &e.get("magnet_highest_z")?,
                        &val_string({
                            let mut str340 = String::new();
                            str340.push_str(".4g");
                            Val::Str(str340)
                        })?,
                    )?);
                    str339.push_str(" mm");
                    Val::Str(str339)
                })?;
                d.set(Val::Str("FLOAT_WALL_CLEARANCE".into()), {
                    let mut str341 = String::new();
                    str341.push_str(&format(
                        &e.get("float_wall_clearance")?,
                        &val_string({
                            let mut str342 = String::new();
                            str342.push_str(".3g");
                            Val::Str(str342)
                        })?,
                    )?);
                    str341.push_str(" mm");
                    Val::Str(str341)
                })?;
                d.set(Val::Str("MAGNET_LEAD".into()), {
                    let mut str343 = String::new();
                    str343.push_str(&format(
                        &e.get("magnet_lead_above_surface")?,
                        &val_string({
                            let mut str344 = String::new();
                            str344.push_str(".3f");
                            Val::Str(str344)
                        })?,
                    )?);
                    str343.push_str(" mm");
                    Val::Str(str343)
                })?;
                d.set(Val::Str("REED_LOW_Z".into()), {
                    let mut str345 = String::new();
                    str345.push_str(&format(
                        &e.get("reed_low_z")?,
                        &val_string({
                            let mut str346 = String::new();
                            str346.push_str(".3f");
                            Val::Str(str346)
                        })?,
                    )?);
                    str345.push_str(" mm");
                    Val::Str(str345)
                })?;
                d.set(Val::Str("REED_HIGH_Z".into()), {
                    let mut str347 = String::new();
                    str347.push_str(&format(
                        &e.get("reed_high_z")?,
                        &val_string({
                            let mut str348 = String::new();
                            str348.push_str(".3f");
                            Val::Str(str348)
                        })?,
                    )?);
                    str347.push_str(" mm");
                    Val::Str(str347)
                })?;
                d.set(Val::Str("REED_GLASS_L".into()), {
                    let mut str349 = String::new();
                    str349.push_str(&format(
                        &e.get("reed_glass_length")?,
                        &val_string({
                            let mut str350 = String::new();
                            str350.push_str(".4g");
                            Val::Str(str350)
                        })?,
                    )?);
                    str349.push_str(" mm");
                    Val::Str(str349)
                })?;
                d.set(Val::Str("REED_GLASS_D".into()), {
                    let mut str351 = String::new();
                    str351.push_str(&format(
                        &e.get("reed_glass_diameter")?,
                        &val_string({
                            let mut str352 = String::new();
                            str352.push_str(".4g");
                            Val::Str(str352)
                        })?,
                    )?);
                    str351.push_str(" mm");
                    Val::Str(str351)
                })?;
                d.set(Val::Str("POCKET_DEPTH".into()), {
                    let mut str353 = String::new();
                    str353.push_str(&format(
                        &e.get("pocket_depth")?,
                        &val_string({
                            let mut str354 = String::new();
                            str354.push_str(".4g");
                            Val::Str(str354)
                        })?,
                    )?);
                    str353.push_str(" mm");
                    Val::Str(str353)
                })?;
                d.set(Val::Str("POCKET_L".into()), {
                    let mut str355 = String::new();
                    str355.push_str(&format(
                        &e.get("pocket_length")?,
                        &val_string({
                            let mut str356 = String::new();
                            str356.push_str(".4g");
                            Val::Str(str356)
                        })?,
                    )?);
                    str355.push_str(" mm");
                    Val::Str(str355)
                })?;
                d.set(Val::Str("POCKET_W".into()), {
                    let mut str357 = String::new();
                    str357.push_str(&format(
                        &e.get("pocket_width")?,
                        &val_string({
                            let mut str358 = String::new();
                            str358.push_str(".4g");
                            Val::Str(str358)
                        })?,
                    )?);
                    str357.push_str(" mm");
                    Val::Str(str357)
                })?;
                d.set(Val::Str("SKIRT_T".into()), {
                    let mut str359 = String::new();
                    str359.push_str(&format(
                        &e.get("skirt_thickness")?,
                        &val_string({
                            let mut str360 = String::new();
                            str360.push_str(".4g");
                            Val::Str(str360)
                        })?,
                    )?);
                    str359.push_str(" mm");
                    Val::Str(str359)
                })?;
                d.set(Val::Str("AXIAL_RAMP".into()), {
                    let mut str361 = String::new();
                    str361.push_str(&format(
                        &e.get("axial_ramp_length")?,
                        &val_string({
                            let mut str362 = String::new();
                            str362.push_str(".4g");
                            Val::Str(str362)
                        })?,
                    )?);
                    str361.push_str(" mm");
                    Val::Str(str361)
                })?;
                d.set(Val::Str("ARC_RAMP".into()), {
                    let mut str363 = String::new();
                    str363.push_str(&format(
                        &e.get("arc_ramp_width")?,
                        &val_string({
                            let mut str364 = String::new();
                            str364.push_str(".4g");
                            Val::Str(str364)
                        })?,
                    )?);
                    str363.push_str(" mm");
                    Val::Str(str363)
                })?;
                d.set(Val::Str("BRIDGE_Z_BOTTOM".into()), {
                    let mut str365 = String::new();
                    str365.push_str(&format(
                        &e.get("bridge_z_bottom")?,
                        &val_string({
                            let mut str366 = String::new();
                            str366.push_str(".4g");
                            Val::Str(str366)
                        })?,
                    )?);
                    str365.push_str(" mm");
                    Val::Str(str365)
                })?;
                d.set(Val::Str("BRIDGE_Z_TOP".into()), {
                    let mut str367 = String::new();
                    str367.push_str(&format(
                        &e.get("bridge_z_top")?,
                        &val_string({
                            let mut str368 = String::new();
                            str368.push_str(".4g");
                            Val::Str(str368)
                        })?,
                    )?);
                    str367.push_str(" mm");
                    Val::Str(str367)
                })?;
                d.set(Val::Str("BRIDGE_H".into()), {
                    let mut str369 = String::new();
                    str369.push_str(&format(
                        &e.get("bridge_height")?,
                        &val_string({
                            let mut str370 = String::new();
                            str370.push_str(".4g");
                            Val::Str(str370)
                        })?,
                    )?);
                    str369.push_str(" mm");
                    Val::Str(str369)
                })?;
                d.set(Val::Str("BRIDGE_ARC".into()), {
                    let mut str371 = String::new();
                    str371.push_str(&format(
                        &binary("mul", Val::Int(2i64), e.get("bridge_half_width")?)?,
                        &val_string({
                            let mut str372 = String::new();
                            str372.push_str(".4g");
                            Val::Str(str372)
                        })?,
                    )?);
                    str371.push_str(" mm");
                    Val::Str(str371)
                })?;
                d.set(Val::Str("EFFECTIVE_ARC".into()), {
                    let mut str373 = String::new();
                    str373.push_str(&format(
                        &e.get("effective_lift_arc")?,
                        &val_string({
                            let mut str374 = String::new();
                            str374.push_str(".4g");
                            Val::Str(str374)
                        })?,
                    )?);
                    str373.push_str(" mm");
                    Val::Str(str373)
                })?;
                d.set(Val::Str("CARRIED_FRACTION".into()), {
                    let mut str375 = String::new();
                    str375.push_str(&format(
                        &binary(
                            "truediv",
                            binary("mul", Val::Int(100i64), e.get("carried_copper")?)?,
                            e.get("wrap_length")?,
                        )?,
                        &val_string({
                            let mut str376 = String::new();
                            str376.push_str(".2g");
                            Val::Str(str376)
                        })?,
                    )?);
                    str375.push_str(" %");
                    Val::Str(str375)
                })?;
                d.set(Val::Str("LEAD_GROOVE_W".into()), {
                    let mut str377 = String::new();
                    str377.push_str(&format(
                        &e.get("lead_groove_width")?,
                        &val_string({
                            let mut str378 = String::new();
                            str378.push_str(".4g");
                            Val::Str(str378)
                        })?,
                    )?);
                    str377.push_str(" mm");
                    Val::Str(str377)
                })?;
                d.set(Val::Str("LEAD_GROOVE_D".into()), {
                    let mut str379 = String::new();
                    str379.push_str(&format(
                        &e.get("lead_groove_depth")?,
                        &val_string({
                            let mut str380 = String::new();
                            str380.push_str(".4g");
                            Val::Str(str380)
                        })?,
                    )?);
                    str379.push_str(" mm");
                    Val::Str(str379)
                })?;
                d.set(Val::Str("WRAPS_CARRIED".into()), {
                    let mut str381 = String::new();
                    str381.push_str(&format(
                        &e.get("wraps_carried")?,
                        &val_string({
                            let mut str382 = String::new();
                            str382.push_str(".3g");
                            Val::Str(str382)
                        })?,
                    )?);
                    Val::Str(str381)
                })?;
                d.set(Val::Str("CARRIED_COPPER".into()), {
                    let mut str383 = String::new();
                    str383.push_str(&format(
                        &e.get("carried_copper")?,
                        &val_string({
                            let mut str384 = String::new();
                            str384.push_str(".0f");
                            Val::Str(str384)
                        })?,
                    )?);
                    str383.push_str(" mm");
                    Val::Str(str383)
                })?;
                d.set(Val::Str("BRIDGE_VOL".into()), {
                    let mut str385 = String::new();
                    str385.push_str(&format(
                        &binary("truediv", e.get("bridge_volume")?, Val::Int(1000i64))?,
                        &val_string({
                            let mut str386 = String::new();
                            str386.push_str(".3g");
                            Val::Str(str386)
                        })?,
                    )?);
                    str385.push_str(" cm³");
                    Val::Str(str385)
                })?;
                d.set(Val::Str("GAUGE_VOL".into()), {
                    let mut str387 = String::new();
                    str387.push_str(&format(
                        &binary("truediv", e.get("gauge_volume")?, Val::Int(1000i64))?,
                        &val_string({
                            let mut str388 = String::new();
                            str388.push_str(".3g");
                            Val::Str(str388)
                        })?,
                    )?);
                    str387.push_str(" cm³");
                    Val::Str(str387)
                })?;
                d.set(Val::Str("GAUGE_ARC_DEG".into()), {
                    let mut str389 = String::new();
                    str389.push_str(&format(
                        &e.get("gauge_arc_degrees")?,
                        &val_string({
                            let mut str390 = String::new();
                            str390.push_str(".3g");
                            Val::Str(str390)
                        })?,
                    )?);
                    str389.push_str("°");
                    Val::Str(str389)
                })?;
                d
            };
            e.set("variables", assigned296.clone())?;
            {
                let fun393 = e.get("substitute_md")?;
                let mut args391 = Vec::new();
                let mut kw392 = Vec::new();
                args391.push(binary(
                    "truediv",
                    e.get("out_dir")?,
                    Val::Str("README.md".into()),
                )?);
                kw392.push(("variables".into(), e.get("variables")?));
                fun393.call(args391, kw392)?
            };
            {
                let fun396 = e.get("print")?;
                let mut args394 = Vec::new();
                let mut kw395 = Vec::new();
                args394.push(Val::Str("-> README.md".into()));
                fun396.call(args394, kw395)?
            };
            {
                let fun399 = e.get("substitute_md")?;
                let mut args397 = Vec::new();
                let mut kw398 = Vec::new();
                args397.push(binary(
                    "truediv",
                    binary(
                        "truediv",
                        e.get("out_dir")?.attr("parent")?,
                        Val::Str("reservoir".into()),
                    )?,
                    Val::Str("level-sensing.md".into()),
                )?);
                kw398.push(("variables".into(), e.get("variables")?));
                fun399.call(args397, kw398)?
            };
            {
                let fun402 = e.get("print")?;
                let mut args400 = Vec::new();
                let mut kw401 = Vec::new();
                args400.push(Val::Str("-> ../reservoir/level-sensing.md".into()));
                fun402.call(args400, kw401)?
            };
            {
                let fun405 = e.get("substitute_py_comments")?;
                let mut args403 = Vec::new();
                let mut kw404 = Vec::new();
                args403.push({
                    let fun408 = e.get("Path")?;
                    let mut args406 = Vec::new();
                    let mut kw407 = Vec::new();
                    args406.push(e.get("__file__")?);
                    fun408.call(args406, kw407)?
                });
                kw404.push(("variables".into(), e.get("variables")?));
                fun405.call(args403, kw404)?
            };
            {
                let fun411 = e.get("print")?;
                let mut args409 = Vec::new();
                let mut kw410 = Vec::new();
                args409.push({
                    let mut str412 = String::new();
                    str412.push_str("-> ");
                    str412.push_str(&format(
                        &{
                            let fun415 = e.get("Path")?;
                            let mut args413 = Vec::new();
                            let mut kw414 = Vec::new();
                            args413.push(e.get("__file__")?);
                            fun415.call(args413, kw414)?
                        }
                        .attr("name")?,
                        &String::new(),
                    )?);
                    str412.push_str(" (self)");
                    Val::Str(str412)
                });
                fun411.call(args409, kw410)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun418 = e.get("_rust_part")?.attr("start")?;
        let mut args416 = Vec::new();
        let mut kw417 = Vec::new();
        fun418.call(args416, kw417)?
    };
    let assigned419 = {
        let fun422 = e.get("argparse")?.attr("ArgumentParser")?;
        let mut args420 = Vec::new();
        let mut kw421 = Vec::new();
        kw421.push(("description".into(), e.get("__doc__")?));
        fun422.call(args420, kw421)?
    };
    e.set("parser", assigned419.clone())?;
    {
        let fun425 = e.get("parser")?.attr("add_argument")?;
        let mut args423 = Vec::new();
        let mut kw424 = Vec::new();
        args423.push(Val::Str("--output".into()));
        kw424.push(("type".into(), e.get("Path")?));
        kw424.push(("default".into(), e.get("_here")?.attr("parent")?));
        fun425.call(args423, kw424)?
    };
    let assigned426 = {
        let fun429 = e.get("parser")?.attr("parse_args")?;
        let mut args427 = Vec::new();
        let mut kw428 = Vec::new();
        fun429.call(args427, kw428)?
    };
    e.set("args", assigned426.clone())?;
    {
        let fun432 = e.get("main")?;
        let mut args430 = Vec::new();
        let mut kw431 = Vec::new();
        args430.push(e.get("args")?.attr("output")?);
        fun432.call(args430, kw431)?
    };
    Ok(Val::None)
}
