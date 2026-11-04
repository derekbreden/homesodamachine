#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod1 = rt.import_module("world_workplane")?;
    e.set(
        "WorldWorkplane",
        rt.member("world_workplane", "WorldWorkplane")?,
    )?;
    e.set(
        "xy_plane_z_up",
        rt.member("world_workplane", "xy_plane_z_up")?,
    )?;
    e.set("fits", rt.import_module("fits")?)?;
    let mod2 = rt.import_module("_cold_core_interface")?;
    e.set(
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
    )?;
    e.set(
        "wall_thickness",
        rt.member("_cold_core_interface", "wall_thickness")?,
    )?;
    e.set(
        "outer_shell_wall",
        rt.member("_cold_core_interface", "outer_shell_wall")?,
    )?;
    e.set(
        "outer_shell_x_length",
        rt.member("_cold_core_interface", "outer_shell_x_length")?,
    )?;
    e.set(
        "outer_shell_y_length",
        rt.member("_cold_core_interface", "outer_shell_y_length")?,
    )?;
    e.set(
        "corner_round_radius",
        rt.member("_cold_core_interface", "corner_round_radius")?,
    )?;
    e.set(
        "screw_boss_size",
        rt.member("_cold_core_interface", "screw_boss_size")?,
    )?;
    e.set(
        "cap_conduits",
        rt.member("_cold_core_interface", "cap_conduits")?,
    )?;
    e.set(
        "cap_conduit_floor_xy",
        rt.member("_cold_core_interface", "cap_conduit_floor_xy")?,
    )?;
    e.set(
        "cap_passive_guides",
        rt.member("_cold_core_interface", "cap_passive_guides")?,
    )?;
    e.set(
        "cap_cable_guides",
        rt.member("_cold_core_interface", "cap_cable_guides")?,
    )?;
    e.set(
        "cap_conduit_bore_radius",
        rt.member("_cold_core_interface", "cap_conduit_bore_radius")?,
    )?;
    e.set(
        "cap_conduit_bore_radii",
        rt.member("_cold_core_interface", "cap_conduit_bore_radii")?,
    )?;
    e.set(
        "cap_conduit_boss_radius",
        rt.member("_cold_core_interface", "cap_conduit_boss_radius")?,
    )?;
    e.set(
        "cap_conduit_links",
        rt.member("_cold_core_interface", "cap_conduit_links")?,
    )?;
    e.set(
        "cap_conduit_link_width",
        rt.member("_cold_core_interface", "cap_conduit_link_width")?,
    )?;
    e.set(
        "cap_conduit_entry_relief_radius",
        rt.member("_cold_core_interface", "cap_conduit_entry_relief_radius")?,
    )?;
    e.set(
        "foam_cap_height",
        rt.member("_cold_core_interface", "foam_cap_height")?,
    )?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    e.set(
        "foam_cap_lid_pour_radius",
        rt.member("_cold_core_interface", "foam_cap_lid_pour_radius")?,
    )?;
    e.set(
        "foam_cap_lid_vent_radius",
        rt.member("_cold_core_interface", "foam_cap_lid_vent_radius")?,
    )?;
    e.set(
        "foam_cap_lid_pour_xy",
        rt.member("_cold_core_interface", "foam_cap_lid_pour_xy")?,
    )?;
    e.set(
        "foam_cap_lid_vent_xy",
        rt.member("_cold_core_interface", "foam_cap_lid_vent_xy")?,
    )?;
    e.set(
        "attachment_xy_positions",
        rt.member("_cold_core_interface", "attachment_xy_positions")?,
    )?;
    e.set(
        "attachment_stations",
        rt.member("_cold_core_interface", "attachment_stations")?,
    )?;
    e.set(
        "lid_attachment_stations",
        rt.member("_cold_core_interface", "lid_attachment_stations")?,
    )?;
    e.set(
        "lid_attachment_xy_positions",
        rt.member("_cold_core_interface", "lid_attachment_xy_positions")?,
    )?;
    e.set(
        "cap_shell_clearance",
        rt.member("_cold_core_interface", "cap_shell_clearance")?,
    )?;
    e.set(
        "cap_lid_clearance",
        rt.member("_cold_core_interface", "cap_lid_clearance")?,
    )?;
    e.set(
        "screw_clearance_radius",
        rt.member("_cold_core_interface", "screw_clearance_radius")?,
    )?;
    e.set(
        "head_cbore_radius",
        rt.member("_cold_core_interface", "head_cbore_radius")?,
    )?;
    e.set(
        "head_cbore_depth",
        rt.member("_cold_core_interface", "head_cbore_depth")?,
    )?;
    e.set(
        "head_pad_height",
        rt.member("_cold_core_interface", "head_pad_height")?,
    )?;
    e.set(
        "head_pad_slip",
        rt.member("_cold_core_interface", "head_pad_slip")?,
    )?;
    e.set(
        "foam_cap_lid_height",
        rt.member("_cold_core_interface", "foam_cap_lid_height")?,
    )?;
    e.set(
        "bottom_cap_height",
        rt.member("_cold_core_interface", "bottom_cap_height")?,
    )?;
    e.set(
        "bottom_pour_positions",
        rt.member("_cold_core_interface", "bottom_pour_positions")?,
    )?;
    e.set(
        "bottom_pour_radius",
        rt.member("_cold_core_interface", "bottom_pour_radius")?,
    )?;
    let mod3 = rt.import_module("_outer_shell")?;
    e.set(
        "build_attachment_bosses",
        rt.member("_outer_shell", "build_attachment_bosses")?,
    )?;
    e.set(
        "trim_cup_floor",
        rt.member("_outer_shell", "trim_cup_floor")?,
    )?;
    e.set("_above_mounts", rt.import_module("_above_core_mounts")?)?;
    let assigned4 = e.get("foam_cap_lid_height")?;
    e.set("lid_total_height", assigned4.clone())?;
    let assigned5 = binary(
        "add",
        e.get("lid_total_height")?,
        e.get("wall_and_floor_thickness")?,
    )?;
    e.set("lid_cut_through_depth", assigned5.clone())?;
    let assigned6 = {
        let fun9 = e.get("max")?;
        let mut args7 = Vec::new();
        let mut kw8 = Vec::new();
        args7.push(Val::Float(0.0f64));
        args7.push(binary(
            "sub",
            binary("add", e.get("head_cbore_radius")?, e.get("wall_thickness")?)?,
            binary("truediv", e.get("screw_boss_size")?, Val::Int(2i64))?,
        )?);
        fun9.call(args7, kw8)?
    };
    e.set("head_pad_growth", assigned6.clone())?;
    let assigned10 = binary("sub", e.get("foam_cap_height")?, e.get("head_pad_height")?)?;
    e.set("top_cap_height", assigned10.clone())?;
    let assigned11 = unary(
        "neg",
        binary(
            "add",
            e.get("foam_cap_height")?,
            e.get("wall_and_floor_thickness")?,
        )?,
    )?;
    e.set("stack_floor_z", assigned11.clone())?;
    let assigned12 = binary(
        "add",
        binary(
            "add",
            e.get("foam_shell_outer_height")?,
            e.get("top_cap_height")?,
        )?,
        e.get("lid_total_height")?,
    )?;
    e.set("cap_face_z", assigned12.clone())?;
    // attachment_clearances_extrude
    e.set("attachment_clearances_extrude", {
        let params = vec![
            ("height".into(), None, false),
            ("top".into(), Some(Val::Bool(false)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun15 = {
                    let fun18 = {
                        let fun21 = {
                            let fun24 = {
                                let fun27 = e.get("WorldWorkplane")?;
                                let mut args25 = Vec::new();
                                let mut kw26 = Vec::new();
                                args25.push(e.get("xy_plane_z_up")?);
                                fun27.call(args25, kw26)?
                            }
                            .attr("workplane")?;
                            let mut args22 = Vec::new();
                            let mut kw23 = Vec::new();
                            kw23.push(("offset".into(), Val::Int(0i64)));
                            fun24.call(args22, kw23)?
                        }
                        .attr("pushPoints")?;
                        let mut args19 = Vec::new();
                        let mut kw20 = Vec::new();
                        args19.push(if e.get("top")?.truthy()? {
                            e.get("lid_attachment_xy_positions")?
                        } else {
                            e.get("attachment_xy_positions")?
                        });
                        fun21.call(args19, kw20)?
                    }
                    .attr("circle")?;
                    let mut args16 = Vec::new();
                    let mut kw17 = Vec::new();
                    args16.push(e.get("screw_clearance_radius")?);
                    fun18.call(args16, kw17)?
                }
                .attr("extrude")?;
                let mut args13 = Vec::new();
                let mut kw14 = Vec::new();
                args13.push(e.get("height")?);
                fun15.call(args13, kw14)?
            });
            Ok(Val::None)
        })
    })?;
    // build_conduit_bores
    e.set("build_conduit_bores", {
        let params = vec![
            ("height".into(), None, false),
            (
                "radius".into(),
                Some(e.get("cap_conduit_bore_radius")?),
                false,
            ),
            ("overshoot".into(), Some(Val::Float(0.0f64)), false),
            ("frame".into(), Some(Val::Str("cup".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned28 = {
                let e = e.child();
                let out29 = Val::list(vec![]);
                for item30 in {
                    let fun33 = e.get("cap_conduits")?.attr("items")?;
                    let mut args31 = Vec::new();
                    let mut kw32 = Vec::new();
                    fun33.call(args31, kw32)?
                }
                .iter()?
                {
                    let unpack34 = unpack(item30, 2)?;
                    e.set("name", unpack34[0].clone())?;
                    e.set("xy", unpack34[1].clone())?;
                    if {
                        let v46 = {
                            let v47 = e.get("name")?;
                            let v48 = {
                                let mut s = Vec::new();
                                s.push(Val::Str("reservoir-b-fill".into()));
                                s.push(Val::Str("water-in".into()));
                                s.push(Val::Str("carb-water-out".into()));
                                Val::tuple(s)
                            };
                            Val::Bool(compare("not_in", v47.clone(), v48.clone())?.truthy()?)
                        };
                        if v46.truthy()? {
                            {
                                let v40 = unary("not", {
                                    let v43 = {
                                        let v44 = e.get("frame")?;
                                        let v45 = Val::Str("lid".into());
                                        Val::Bool(
                                            compare("eq", v44.clone(), v45.clone())?.truthy()?,
                                        )
                                    };
                                    if v43.truthy()? {
                                        {
                                            let v41 = e.get("name")?;
                                            let v42 = e.get("cap_conduit_bore_radii")?;
                                            Val::Bool(
                                                compare("in", v41.clone(), v42.clone())?
                                                    .truthy()?,
                                            )
                                        }
                                    } else {
                                        v43
                                    }
                                })?;
                                if v40.truthy()? {
                                    {
                                        let v37 = {
                                            let v38 = e.get("frame")?;
                                            let v39 = Val::Str("lid".into());
                                            Val::Bool(
                                                compare("eq", v38.clone(), v39.clone())?
                                                    .truthy()?,
                                            )
                                        };
                                        if v37.truthy()? {
                                            v37
                                        } else {
                                            {
                                                let v35 = e.get("name")?;
                                                let v36 = {
                                                    let mut s = Vec::new();
                                                    s.extend(e.get("cap_passive_guides")?.iter()?);
                                                    s.extend(e.get("cap_cable_guides")?.iter()?);
                                                    Val::tuple(s)
                                                };
                                                Val::Bool(
                                                    compare("not_in", v35.clone(), v36.clone())?
                                                        .truthy()?,
                                                )
                                            }
                                        }
                                    }
                                } else {
                                    v40
                                }
                            }
                        } else {
                            v46
                        }
                    }
                    .truthy()?
                    {
                        out29.attr("append")?.call(vec![e.get("xy")?], vec![])?;
                    }
                }
                out29
            };
            e.set("ordinary", assigned28.clone())?;
            let assigned49 = {
                let fun52 = {
                    let fun55 = {
                        let fun58 = {
                            let fun61 = {
                                let fun64 = e.get("WorldWorkplane")?;
                                let mut args62 = Vec::new();
                                let mut kw63 = Vec::new();
                                args62.push(e.get("xy_plane_z_up")?);
                                fun64.call(args62, kw63)?
                            }
                            .attr("workplane")?;
                            let mut args59 = Vec::new();
                            let mut kw60 = Vec::new();
                            kw60.push(("offset".into(), unary("neg", e.get("overshoot")?)?));
                            fun61.call(args59, kw60)?
                        }
                        .attr("pushPoints")?;
                        let mut args56 = Vec::new();
                        let mut kw57 = Vec::new();
                        args56.push(e.get("ordinary")?);
                        fun58.call(args56, kw57)?
                    }
                    .attr("circle")?;
                    let mut args53 = Vec::new();
                    let mut kw54 = Vec::new();
                    args53.push(e.get("radius")?);
                    fun55.call(args53, kw54)?
                }
                .attr("extrude")?;
                let mut args50 = Vec::new();
                let mut kw51 = Vec::new();
                args50.push(binary("add", e.get("height")?, e.get("overshoot")?)?);
                fun52.call(args50, kw51)?
            };
            e.set("bores", assigned49.clone())?;
            if {
                let v65 = e.get("frame")?;
                let v66 = Val::Str("lid".into());
                Val::Bool(compare("eq", v65.clone(), v66.clone())?.truthy()?)
            }
            .truthy()?
            {
                for item67 in {
                    let fun89 = e.get("cap_conduit_bore_radii")?.attr("items")?;
                    let mut args87 = Vec::new();
                    let mut kw88 = Vec::new();
                    fun89.call(args87, kw88)?
                }
                .iter()?
                {
                    let unpack90 = unpack(item67, 2)?;
                    e.set("name", unpack90[0].clone())?;
                    e.set("bore_radius", unpack90[1].clone())?;
                    let assigned68 = {
                        let fun71 = e.get("bores")?.attr("union")?;
                        let mut args69 = Vec::new();
                        let mut kw70 = Vec::new();
                        args69.push({
                            let fun74 = {
                                let fun77 = {
                                    let fun80 = {
                                        let fun83 = {
                                            let fun86 = e.get("WorldWorkplane")?;
                                            let mut args84 = Vec::new();
                                            let mut kw85 = Vec::new();
                                            args84.push(e.get("xy_plane_z_up")?);
                                            fun86.call(args84, kw85)?
                                        }
                                        .attr("workplane")?;
                                        let mut args81 = Vec::new();
                                        let mut kw82 = Vec::new();
                                        kw82.push((
                                            "offset".into(),
                                            unary("neg", e.get("overshoot")?)?,
                                        ));
                                        fun83.call(args81, kw82)?
                                    }
                                    .attr("pushPoints")?;
                                    let mut args78 = Vec::new();
                                    let mut kw79 = Vec::new();
                                    args78.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("cap_conduits")?.get(e.get("name")?)?);
                                        Val::list(s)
                                    });
                                    fun80.call(args78, kw79)?
                                }
                                .attr("circle")?;
                                let mut args75 = Vec::new();
                                let mut kw76 = Vec::new();
                                args75.push(e.get("bore_radius")?);
                                fun77.call(args75, kw76)?
                            }
                            .attr("extrude")?;
                            let mut args72 = Vec::new();
                            let mut kw73 = Vec::new();
                            args72.push(binary("add", e.get("height")?, e.get("overshoot")?)?);
                            fun74.call(args72, kw73)?
                        });
                        fun71.call(args69, kw70)?
                    };
                    e.set("bores", assigned68.clone())?;
                }
            }
            let assigned91 = {
                let fun94 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args92 = Vec::new();
                let mut kw93 = Vec::new();
                args92.push(binary(
                    "add",
                    e.get("outer_shell_x_length")?,
                    Val::Float(40.0f64),
                )?);
                args92.push(binary(
                    "add",
                    e.get("outer_shell_y_length")?,
                    Val::Float(40.0f64),
                )?);
                args92.push(binary(
                    "add",
                    binary("add", e.get("height")?, e.get("overshoot")?)?,
                    Val::Float(1.0f64),
                )?);
                args92.push({
                    let fun97 = e.get("cq")?.attr("Vector")?;
                    let mut args95 = Vec::new();
                    let mut kw96 = Vec::new();
                    args95.push(binary(
                        "sub",
                        binary(
                            "truediv",
                            unary("neg", e.get("outer_shell_x_length")?)?,
                            Val::Float(2.0f64),
                        )?,
                        Val::Float(20.0f64),
                    )?);
                    args95.push(binary(
                        "sub",
                        binary(
                            "truediv",
                            unary("neg", e.get("outer_shell_y_length")?)?,
                            Val::Float(2.0f64),
                        )?,
                        Val::Float(20.0f64),
                    )?);
                    args95.push(unary("neg", e.get("overshoot")?)?);
                    fun97.call(args95, kw96)?
                });
                fun94.call(args92, kw93)?
            };
            e.set("band", assigned91.clone())?;
            if {
                let v98 = e.get("frame")?;
                let v99 = Val::Str("cup".into());
                Val::Bool(compare("eq", v98.clone(), v99.clone())?.truthy()?)
            }
            .truthy()?
            {
                let mod100 = rt.import_module("_internal_routes")?;
                e.set("routes", rt.member("_internal_routes", "routes")?)?;
                e.set("build_route", rt.member("_internal_routes", "build_route")?)?;
                e.set(
                    "route_bend_radius",
                    rt.member("_internal_routes", "route_bend_radius")?,
                )?;
                for item101 in e.get("cap_passive_guides")?.iter()? {
                    e.set("name", item101)?;
                    let assigned102 = {
                        let fun105 = e.get("build_route")?;
                        let mut args103 = Vec::new();
                        let mut kw104 = Vec::new();
                        args103.push(e.get("routes")?.get(e.get("name")?)?);
                        args103.push(e.get("route_bend_radius")?);
                        args103.push(e.get("radius")?);
                        fun105.call(args103, kw104)?
                    };
                    e.set("passage", assigned102.clone())?;
                    let assigned106 = {
                        let fun109 = {
                            let fun112 = e.get("passage")?.attr("rotate")?;
                            let mut args110 = Vec::new();
                            let mut kw111 = Vec::new();
                            args110.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(0.0f64));
                                s.push(Val::Float(0.0f64));
                                s.push(Val::Float(0.0f64));
                                Val::tuple(s)
                            });
                            args110.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(0.0f64));
                                s.push(Val::Float(0.0f64));
                                s.push(Val::Float(1.0f64));
                                Val::tuple(s)
                            });
                            args110.push(Val::Float(180.0f64));
                            fun112.call(args110, kw111)?
                        }
                        .attr("translate")?;
                        let mut args107 = Vec::new();
                        let mut kw108 = Vec::new();
                        args107.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(unary("neg", e.get("foam_shell_outer_height")?)?);
                            Val::tuple(s)
                        });
                        fun109.call(args107, kw108)?
                    };
                    e.set("passage", assigned106.clone())?;
                    let assigned113 = {
                        let fun116 = e.get("bores")?.attr("union")?;
                        let mut args114 = Vec::new();
                        let mut kw115 = Vec::new();
                        args114.push({
                            let fun119 = e.get("passage")?.attr("intersect")?;
                            let mut args117 = Vec::new();
                            let mut kw118 = Vec::new();
                            args117.push(e.get("band")?);
                            fun119.call(args117, kw118)?
                        });
                        fun116.call(args114, kw115)?
                    };
                    e.set("bores", assigned113.clone())?;
                }
                for item120 in e.get("cap_cable_guides")?.iter()? {
                    e.set("name", item120)?;
                    let assigned121 = {
                        let fun124 = e.get("_above_mounts")?.attr("cable_guide_points")?;
                        let mut args122 = Vec::new();
                        let mut kw123 = Vec::new();
                        args122.push(e.get("name")?);
                        fun124.call(args122, kw123)?
                    };
                    e.set("route", assigned121.clone())?;
                    let assigned125 = {
                        let fun128 = e.get("build_route")?;
                        let mut args126 = Vec::new();
                        let mut kw127 = Vec::new();
                        args126.push(e.get("route")?.get(Val::Str("points_mm".into()))?);
                        args126.push(e.get("route")?.get(Val::Str("bend_radius_mm".into()))?);
                        args126.push(e.get("radius")?);
                        fun128.call(args126, kw127)?
                    };
                    e.set("passage", assigned125.clone())?;
                    let assigned129 = {
                        let fun132 = {
                            let fun135 = e.get("_above_mounts")?.attr("world_shape_in_cap")?;
                            let mut args133 = Vec::new();
                            let mut kw134 = Vec::new();
                            args133.push(e.get("passage")?);
                            fun135.call(args133, kw134)?
                        }
                        .attr("translate")?;
                        let mut args130 = Vec::new();
                        let mut kw131 = Vec::new();
                        args130.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(e.get("top_cap_height")?);
                            Val::tuple(s)
                        });
                        fun132.call(args130, kw131)?
                    };
                    e.set("passage", assigned129.clone())?;
                    let assigned136 = {
                        let fun139 = e.get("bores")?.attr("union")?;
                        let mut args137 = Vec::new();
                        let mut kw138 = Vec::new();
                        args137.push({
                            let fun142 = e.get("passage")?.attr("intersect")?;
                            let mut args140 = Vec::new();
                            let mut kw141 = Vec::new();
                            args140.push(e.get("band")?);
                            fun142.call(args140, kw141)?
                        });
                        fun139.call(args137, kw138)?
                    };
                    e.set("bores", assigned136.clone())?;
                }
            }
            let assigned143 = {
                let fun146 = e.get("_above_mounts")?.attr("world_shape_in_cap")?;
                let mut args144 = Vec::new();
                let mut kw145 = Vec::new();
                args144.push(
                    {
                        let fun149 = e.get("_above_mounts")?.attr("water_in_features")?;
                        let mut args147 = Vec::new();
                        let mut kw148 = Vec::new();
                        fun149.call(args147, kw148)?
                    }
                    .get(Val::Str("cut".into()))?,
                );
                fun146.call(args144, kw145)?
            };
            e.set("water_air", assigned143.clone())?;
            if {
                let v150 = e.get("frame")?;
                let v151 = Val::Str("cup".into());
                Val::Bool(compare("eq", v150.clone(), v151.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned152 = {
                    let fun155 = e.get("water_air")?.attr("translate")?;
                    let mut args153 = Vec::new();
                    let mut kw154 = Vec::new();
                    args153.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("top_cap_height")?);
                        Val::tuple(s)
                    });
                    fun155.call(args153, kw154)?
                };
                e.set("water_air", assigned152.clone())?;
            }
            let assigned156 = {
                let fun159 = e.get("bores")?.attr("union")?;
                let mut args157 = Vec::new();
                let mut kw158 = Vec::new();
                args157.push({
                    let fun162 = e.get("water_air")?.attr("intersect")?;
                    let mut args160 = Vec::new();
                    let mut kw161 = Vec::new();
                    args160.push(e.get("band")?);
                    fun162.call(args160, kw161)?
                });
                fun159.call(args157, kw158)?
            };
            e.set("bores", assigned156.clone())?;
            let assigned163 = {
                let fun166 = e.get("_above_mounts")?.attr("world_shape_in_cap")?;
                let mut args164 = Vec::new();
                let mut kw165 = Vec::new();
                args164.push(
                    {
                        let fun169 = e.get("_above_mounts")?.attr("soda_out_features")?;
                        let mut args167 = Vec::new();
                        let mut kw168 = Vec::new();
                        fun169.call(args167, kw168)?
                    }
                    .get(Val::Str("cut".into()))?,
                );
                fun166.call(args164, kw165)?
            };
            e.set("soda_air", assigned163.clone())?;
            if {
                let v170 = e.get("frame")?;
                let v171 = Val::Str("cup".into());
                Val::Bool(compare("eq", v170.clone(), v171.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned172 = {
                    let fun175 = e.get("soda_air")?.attr("translate")?;
                    let mut args173 = Vec::new();
                    let mut kw174 = Vec::new();
                    args173.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("top_cap_height")?);
                        Val::tuple(s)
                    });
                    fun175.call(args173, kw174)?
                };
                e.set("soda_air", assigned172.clone())?;
            }
            let assigned176 = {
                let fun179 = e.get("bores")?.attr("union")?;
                let mut args177 = Vec::new();
                let mut kw178 = Vec::new();
                args177.push({
                    let fun182 = e.get("soda_air")?.attr("intersect")?;
                    let mut args180 = Vec::new();
                    let mut kw181 = Vec::new();
                    args180.push(e.get("band")?);
                    fun182.call(args180, kw181)?
                });
                fun179.call(args177, kw178)?
            };
            e.set("bores", assigned176.clone())?;
            e.set("_reservoir_b_fill", rt.import_module("_reservoir_b_fill")?)?;
            let assigned183 = {
                let fun186 = e.get("_reservoir_b_fill")?.attr("channel_air")?;
                let mut args184 = Vec::new();
                let mut kw185 = Vec::new();
                fun186.call(args184, kw185)?
            };
            e.set("fitting_air", assigned183.clone())?;
            let assigned187 = {
                let fun190 = e.get("_above_mounts")?.attr("world_shape_in_cap")?;
                let mut args188 = Vec::new();
                let mut kw189 = Vec::new();
                args188.push(e.get("fitting_air")?);
                fun190.call(args188, kw189)?
            };
            e.set("fitting_air", assigned187.clone())?;
            if {
                let v191 = e.get("frame")?;
                let v192 = Val::Str("cup".into());
                Val::Bool(compare("eq", v191.clone(), v192.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned193 = {
                    let fun196 = e.get("fitting_air")?.attr("translate")?;
                    let mut args194 = Vec::new();
                    let mut kw195 = Vec::new();
                    args194.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("top_cap_height")?);
                        Val::tuple(s)
                    });
                    fun196.call(args194, kw195)?
                };
                e.set("fitting_air", assigned193.clone())?;
            }
            return Ok({
                let fun199 = e.get("bores")?.attr("union")?;
                let mut args197 = Vec::new();
                let mut kw198 = Vec::new();
                args197.push({
                    let fun202 = e.get("fitting_air")?.attr("intersect")?;
                    let mut args200 = Vec::new();
                    let mut kw201 = Vec::new();
                    args200.push(e.get("band")?);
                    fun202.call(args200, kw201)?
                });
                fun199.call(args197, kw198)?
            });
            Ok(Val::None)
        })
    })?;
    // build_conduit_entry_reliefs
    e.set("build_conduit_entry_reliefs", {
        let params = vec![("z_inner".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned203 = Val::None;
            e.set("cones", assigned203.clone())?;
            for item204 in {
                let fun240 = e.get("cap_conduits")?.attr("items")?;
                let mut args238 = Vec::new();
                let mut kw239 = Vec::new();
                fun240.call(args238, kw239)?
            }
            .iter()?
            {
                let unpack241 = unpack(item204, 2)?;
                e.set("name", unpack241[0].clone())?;
                e.set("centre", unpack241[1].clone())?;
                if {
                    let v205 = e.get("name")?;
                    let v206 = {
                        let mut s = Vec::new();
                        s.push(Val::Str("reservoir-b-fill".into()));
                        s.push(Val::Str("water-in".into()));
                        s.push(Val::Str("sensor-cable".into()));
                        s.extend(e.get("cap_conduit_bore_radii")?.iter()?);
                        Val::tuple(s)
                    };
                    Val::Bool(compare("in", v205.clone(), v206.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned207 = {
                    let fun210 = {
                        let fun213 = {
                            let fun216 = {
                                let fun219 = {
                                    let fun222 = {
                                        let fun225 = {
                                            let fun228 = {
                                                let fun231 = e.get("WorldWorkplane")?;
                                                let mut args229 = Vec::new();
                                                let mut kw230 = Vec::new();
                                                args229.push(e.get("xy_plane_z_up")?);
                                                fun231.call(args229, kw230)?
                                            }
                                            .attr("workplane")?;
                                            let mut args226 = Vec::new();
                                            let mut kw227 = Vec::new();
                                            kw227.push(("offset".into(), e.get("z_inner")?));
                                            fun228.call(args226, kw227)?
                                        }
                                        .attr("moveTo")?;
                                        let mut args223 = Vec::new();
                                        let mut kw224 = Vec::new();
                                        args223.push(e.get("centre")?);
                                        fun225.call(args223, kw224)?
                                    }
                                    .attr("circle")?;
                                    let mut args220 = Vec::new();
                                    let mut kw221 = Vec::new();
                                    args220.push(e.get("cap_conduit_bore_radius")?);
                                    fun222.call(args220, kw221)?
                                }
                                .attr("workplane")?;
                                let mut args217 = Vec::new();
                                let mut kw218 = Vec::new();
                                kw218.push(("offset".into(), e.get("wall_and_floor_thickness")?));
                                fun219.call(args217, kw218)?
                            }
                            .attr("moveTo")?;
                            let mut args214 = Vec::new();
                            let mut kw215 = Vec::new();
                            args214.push(e.get("centre")?);
                            fun216.call(args214, kw215)?
                        }
                        .attr("circle")?;
                        let mut args211 = Vec::new();
                        let mut kw212 = Vec::new();
                        args211.push(e.get("cap_conduit_entry_relief_radius")?);
                        fun213.call(args211, kw212)?
                    }
                    .attr("loft")?;
                    let mut args208 = Vec::new();
                    let mut kw209 = Vec::new();
                    kw209.push(("ruled".into(), Val::Bool(true)));
                    fun210.call(args208, kw209)?
                };
                e.set("cone", assigned207.clone())?;
                let assigned232 = if {
                    let v233 = e.get("cones")?;
                    let v234 = Val::None;
                    Val::Bool(compare("is", v233.clone(), v234.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("cone")?
                } else {
                    {
                        let fun237 = e.get("cones")?.attr("union")?;
                        let mut args235 = Vec::new();
                        let mut kw236 = Vec::new();
                        args235.push(e.get("cone")?);
                        fun237.call(args235, kw236)?
                    }
                };
                e.set("cones", assigned232.clone())?;
            }
            return Ok(e.get("cones")?);
            Ok(Val::None)
        })
    })?;
    // head_access_pockets
    e.set("head_access_pockets", {
        let params = vec![
            ("z0".into(), None, false),
            ("depth".into(), None, false),
            ("top".into(), Some(Val::Bool(false)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned242 = if e.get("top")?.truthy()? {
                e.get("lid_attachment_stations")?
            } else {
                e.get("attachment_stations")?
            };
            e.set("stations", assigned242.clone())?;
            let assigned243 = {
                let fun246 = {
                    let fun249 = {
                        let fun252 = {
                            let fun255 = {
                                let fun258 = e.get("WorldWorkplane")?;
                                let mut args256 = Vec::new();
                                let mut kw257 = Vec::new();
                                args256.push(e.get("xy_plane_z_up")?);
                                fun258.call(args256, kw257)?
                            }
                            .attr("workplane")?;
                            let mut args253 = Vec::new();
                            let mut kw254 = Vec::new();
                            kw254.push(("offset".into(), e.get("z0")?));
                            fun255.call(args253, kw254)?
                        }
                        .attr("pushPoints")?;
                        let mut args250 = Vec::new();
                        let mut kw251 = Vec::new();
                        args250.push({
                            let e = e.child();
                            let out259 = Val::list(vec![]);
                            for item260 in e.get("stations")?.iter()? {
                                let unpack261 = unpack(item260, 2)?;
                                e.set("xy", unpack261[0].clone())?;
                                e.set("wall", unpack261[1].clone())?;
                                out259.attr("append")?.call(vec![e.get("xy")?], vec![])?;
                            }
                            out259
                        });
                        fun252.call(args250, kw251)?
                    }
                    .attr("circle")?;
                    let mut args247 = Vec::new();
                    let mut kw248 = Vec::new();
                    args247.push(e.get("head_cbore_radius")?);
                    fun249.call(args247, kw248)?
                }
                .attr("extrude")?;
                let mut args244 = Vec::new();
                let mut kw245 = Vec::new();
                args244.push(e.get("depth")?);
                fun246.call(args244, kw245)?
            };
            e.set("pockets", assigned243.clone())?;
            let assigned262 = e.get("head_cbore_radius")?;
            e.set("r", assigned262.clone())?;
            for item263 in e.get("stations")?.iter()? {
                let unpack330 = unpack(item263, 2)?;
                let unpack331 = unpack(unpack330[0].clone(), 2)?;
                e.set("x", unpack331[0].clone())?;
                e.set("y", unpack331[1].clone())?;
                e.set("wall", unpack330[1].clone())?;
                if {
                    let v264 = e.get("wall")?;
                    let v265 = Val::Str("corner".into());
                    Val::Bool(compare("eq", v264.clone(), v265.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned266 = binary(
                        "sub",
                        e.get("x")?,
                        binary(
                            "mul",
                            if {
                                let v267 = e.get("x")?;
                                let v268 = Val::Int(0i64);
                                Val::Bool(compare("gt", v267.clone(), v268.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                Val::Int(1i64)
                            } else {
                                unary("neg", Val::Int(1i64))?
                            },
                            binary(
                                "sub",
                                binary("truediv", e.get("outer_shell_x_length")?, Val::Int(2i64))?,
                                e.get("corner_round_radius")?,
                            )?,
                        )?,
                    )?;
                    e.set("ox", assigned266.clone())?;
                    let assigned269 = binary(
                        "sub",
                        e.get("y")?,
                        binary(
                            "mul",
                            if {
                                let v270 = e.get("y")?;
                                let v271 = Val::Int(0i64);
                                Val::Bool(compare("gt", v270.clone(), v271.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                Val::Int(1i64)
                            } else {
                                unary("neg", Val::Int(1i64))?
                            },
                            binary(
                                "sub",
                                binary("truediv", e.get("outer_shell_y_length")?, Val::Int(2i64))?,
                                e.get("corner_round_radius")?,
                            )?,
                        )?,
                    )?;
                    e.set("oy", assigned269.clone())?;
                    let assigned272 = binary(
                        "sub",
                        {
                            let fun275 = e.get("math")?.attr("degrees")?;
                            let mut args273 = Vec::new();
                            let mut kw274 = Vec::new();
                            args273.push({
                                let fun278 = e.get("math")?.attr("atan2")?;
                                let mut args276 = Vec::new();
                                let mut kw277 = Vec::new();
                                args276.push(e.get("oy")?);
                                args276.push(e.get("ox")?);
                                fun278.call(args276, kw277)?
                            });
                            fun275.call(args273, kw274)?
                        },
                        Val::Float(90.0f64),
                    )?;
                    e.set("angle", assigned272.clone())?;
                    let assigned279 = {
                        let fun282 = {
                            let fun285 = {
                                let fun288 = {
                                    let fun291 = e.get("cq")?.attr("Workplane")?;
                                    let mut args289 = Vec::new();
                                    let mut kw290 = Vec::new();
                                    args289.push(Val::Str("XY".into()));
                                    fun291.call(args289, kw290)?
                                }
                                .attr("box")?;
                                let mut args286 = Vec::new();
                                let mut kw287 = Vec::new();
                                args286.push(binary("mul", Val::Int(2i64), e.get("r")?)?);
                                args286.push(binary(
                                    "add",
                                    binary("mul", Val::Int(2i64), e.get("corner_round_radius")?)?,
                                    Val::Int(2i64),
                                )?);
                                args286.push(e.get("depth")?);
                                kw287.push(("centered".into(), {
                                    let mut s = Vec::new();
                                    s.push(Val::Bool(true));
                                    s.push(Val::Bool(false));
                                    s.push(Val::Bool(false));
                                    Val::tuple(s)
                                }));
                                fun288.call(args286, kw287)?
                            }
                            .attr("rotate")?;
                            let mut args283 = Vec::new();
                            let mut kw284 = Vec::new();
                            args283.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                Val::tuple(s)
                            });
                            args283.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(1i64));
                                Val::tuple(s)
                            });
                            args283.push(e.get("angle")?);
                            fun285.call(args283, kw284)?
                        }
                        .attr("translate")?;
                        let mut args280 = Vec::new();
                        let mut kw281 = Vec::new();
                        args280.push({
                            let mut s = Vec::new();
                            s.push(e.get("x")?);
                            s.push(e.get("y")?);
                            s.push(e.get("z0")?);
                            Val::tuple(s)
                        });
                        fun282.call(args280, kw281)?
                    };
                    e.set("slot", assigned279.clone())?;
                } else {
                    if {
                        let v292 = e.get("wall")?;
                        let v293 = Val::Str("x".into());
                        Val::Bool(compare("eq", v292.clone(), v293.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned294 = binary(
                            "mul",
                            if {
                                let v295 = e.get("x")?;
                                let v296 = Val::Int(0i64);
                                Val::Bool(compare("gt", v295.clone(), v296.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                Val::Int(1i64)
                            } else {
                                unary("neg", Val::Int(1i64))?
                            },
                            binary(
                                "add",
                                binary("truediv", e.get("outer_shell_x_length")?, Val::Int(2i64))?,
                                Val::Int(1i64),
                            )?,
                        )?;
                        e.set("end", assigned294.clone())?;
                        let assigned297 = {
                            let fun300 = {
                                let fun303 = {
                                    let fun306 = e.get("cq")?.attr("Workplane")?;
                                    let mut args304 = Vec::new();
                                    let mut kw305 = Vec::new();
                                    args304.push(Val::Str("XY".into()));
                                    fun306.call(args304, kw305)?
                                }
                                .attr("box")?;
                                let mut args301 = Vec::new();
                                let mut kw302 = Vec::new();
                                args301.push({
                                    let fun309 = e.get("abs")?;
                                    let mut args307 = Vec::new();
                                    let mut kw308 = Vec::new();
                                    args307.push(binary("sub", e.get("end")?, e.get("x")?)?);
                                    fun309.call(args307, kw308)?
                                });
                                args301.push(binary("mul", Val::Int(2i64), e.get("r")?)?);
                                args301.push(e.get("depth")?);
                                kw302.push(("centered".into(), {
                                    let mut s = Vec::new();
                                    s.push(Val::Bool(true));
                                    s.push(Val::Bool(true));
                                    s.push(Val::Bool(false));
                                    Val::tuple(s)
                                }));
                                fun303.call(args301, kw302)?
                            }
                            .attr("translate")?;
                            let mut args298 = Vec::new();
                            let mut kw299 = Vec::new();
                            args298.push({
                                let mut s = Vec::new();
                                s.push(binary(
                                    "truediv",
                                    binary("add", e.get("x")?, e.get("end")?)?,
                                    Val::Int(2i64),
                                )?);
                                s.push(e.get("y")?);
                                s.push(e.get("z0")?);
                                Val::tuple(s)
                            });
                            fun300.call(args298, kw299)?
                        };
                        e.set("slot", assigned297.clone())?;
                    } else {
                        let assigned310 = binary(
                            "mul",
                            if {
                                let v311 = e.get("y")?;
                                let v312 = Val::Int(0i64);
                                Val::Bool(compare("gt", v311.clone(), v312.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                Val::Int(1i64)
                            } else {
                                unary("neg", Val::Int(1i64))?
                            },
                            binary(
                                "add",
                                binary("truediv", e.get("outer_shell_y_length")?, Val::Int(2i64))?,
                                Val::Int(1i64),
                            )?,
                        )?;
                        e.set("end", assigned310.clone())?;
                        let assigned313 = {
                            let fun316 = {
                                let fun319 = {
                                    let fun322 = e.get("cq")?.attr("Workplane")?;
                                    let mut args320 = Vec::new();
                                    let mut kw321 = Vec::new();
                                    args320.push(Val::Str("XY".into()));
                                    fun322.call(args320, kw321)?
                                }
                                .attr("box")?;
                                let mut args317 = Vec::new();
                                let mut kw318 = Vec::new();
                                args317.push(binary("mul", Val::Int(2i64), e.get("r")?)?);
                                args317.push({
                                    let fun325 = e.get("abs")?;
                                    let mut args323 = Vec::new();
                                    let mut kw324 = Vec::new();
                                    args323.push(binary("sub", e.get("end")?, e.get("y")?)?);
                                    fun325.call(args323, kw324)?
                                });
                                args317.push(e.get("depth")?);
                                kw318.push(("centered".into(), {
                                    let mut s = Vec::new();
                                    s.push(Val::Bool(true));
                                    s.push(Val::Bool(true));
                                    s.push(Val::Bool(false));
                                    Val::tuple(s)
                                }));
                                fun319.call(args317, kw318)?
                            }
                            .attr("translate")?;
                            let mut args314 = Vec::new();
                            let mut kw315 = Vec::new();
                            args314.push({
                                let mut s = Vec::new();
                                s.push(e.get("x")?);
                                s.push(binary(
                                    "truediv",
                                    binary("add", e.get("y")?, e.get("end")?)?,
                                    Val::Int(2i64),
                                )?);
                                s.push(e.get("z0")?);
                                Val::tuple(s)
                            });
                            fun316.call(args314, kw315)?
                        };
                        e.set("slot", assigned313.clone())?;
                    }
                }
                let assigned326 = {
                    let fun329 = e.get("pockets")?.attr("union")?;
                    let mut args327 = Vec::new();
                    let mut kw328 = Vec::new();
                    args327.push(e.get("slot")?);
                    fun329.call(args327, kw328)?
                };
                e.set("pockets", assigned326.clone())?;
            }
            return Ok(e.get("pockets")?);
            Ok(Val::None)
        })
    })?;
    // build_foam_cap_lid
    e.set("build_foam_cap_lid", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned332 = {
                let fun335 = {
                    let fun338 = {
                        let fun341 = {
                            let fun344 = {
                                let fun347 = e.get("WorldWorkplane")?;
                                let mut args345 = Vec::new();
                                let mut kw346 = Vec::new();
                                args345.push(e.get("xy_plane_z_up")?);
                                fun347.call(args345, kw346)?
                            }
                            .attr("rect")?;
                            let mut args342 = Vec::new();
                            let mut kw343 = Vec::new();
                            args342.push(e.get("outer_shell_x_length")?);
                            args342.push(e.get("outer_shell_y_length")?);
                            fun344.call(args342, kw343)?
                        }
                        .attr("extrude")?;
                        let mut args339 = Vec::new();
                        let mut kw340 = Vec::new();
                        args339.push(e.get("lid_total_height")?);
                        fun341.call(args339, kw340)?
                    }
                    .attr("edges")?;
                    let mut args336 = Vec::new();
                    let mut kw337 = Vec::new();
                    args336.push(Val::Str("|Z".into()));
                    fun338.call(args336, kw337)?
                }
                .attr("fillet")?;
                let mut args333 = Vec::new();
                let mut kw334 = Vec::new();
                args333.push(e.get("corner_round_radius")?);
                fun335.call(args333, kw334)?
            };
            e.set("lid", assigned332.clone())?;
            let assigned348 = {
                let fun351 = e.get("lid")?.attr("cut")?;
                let mut args349 = Vec::new();
                let mut kw350 = Vec::new();
                args349.push({
                    let fun354 = e.get("head_access_pockets")?;
                    let mut args352 = Vec::new();
                    let mut kw353 = Vec::new();
                    args352.push(binary(
                        "sub",
                        e.get("lid_total_height")?,
                        e.get("head_cbore_depth")?,
                    )?);
                    args352.push(e.get("head_cbore_depth")?);
                    kw353.push(("top".into(), Val::Bool(true)));
                    fun354.call(args352, kw353)?
                });
                fun351.call(args349, kw350)?
            };
            e.set("lid", assigned348.clone())?;
            let assigned355 = {
                let fun358 = e.get("lid")?.attr("cut")?;
                let mut args356 = Vec::new();
                let mut kw357 = Vec::new();
                args356.push({
                    let fun361 = e.get("attachment_clearances_extrude")?;
                    let mut args359 = Vec::new();
                    let mut kw360 = Vec::new();
                    args359.push(e.get("lid_cut_through_depth")?);
                    kw360.push(("top".into(), Val::Bool(true)));
                    fun361.call(args359, kw360)?
                });
                fun358.call(args356, kw357)?
            };
            e.set("lid", assigned355.clone())?;
            let assigned362 = {
                let fun365 = e.get("lid")?.attr("cut")?;
                let mut args363 = Vec::new();
                let mut kw364 = Vec::new();
                args363.push({
                    let fun368 = e.get("build_conduit_bores")?;
                    let mut args366 = Vec::new();
                    let mut kw367 = Vec::new();
                    args366.push(e.get("lid_cut_through_depth")?);
                    kw367.push(("frame".into(), Val::Str("lid".into())));
                    fun368.call(args366, kw367)?
                });
                fun365.call(args363, kw364)?
            };
            e.set("lid", assigned362.clone())?;
            let assigned369 = {
                let fun372 = {
                    let fun375 = e.get("lid")?.attr("cut")?;
                    let mut args373 = Vec::new();
                    let mut kw374 = Vec::new();
                    args373.push({
                        let fun378 = e.get("build_conduit_entry_reliefs")?;
                        let mut args376 = Vec::new();
                        let mut kw377 = Vec::new();
                        args376.push(binary(
                            "sub",
                            e.get("lid_total_height")?,
                            e.get("wall_and_floor_thickness")?,
                        )?);
                        fun378.call(args376, kw377)?
                    });
                    fun375.call(args373, kw374)?
                }
                .attr("unwrap")?;
                let mut args370 = Vec::new();
                let mut kw371 = Vec::new();
                fun372.call(args370, kw371)?
            };
            e.set("lid", assigned369.clone())?;
            for item379 in {
                let mut s = Vec::new();
                s.push(Val::Str("water_in_features".into()));
                s.push(Val::Str("soda_out_features".into()));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("name", item379)?;
                let assigned380 = {
                    let fun383 = {
                        let fun386 = e.get("getattr")?;
                        let mut args384 = Vec::new();
                        let mut kw385 = Vec::new();
                        args384.push(e.get("_above_mounts")?);
                        args384.push(e.get("name")?);
                        fun386.call(args384, kw385)?
                    };
                    let mut args381 = Vec::new();
                    let mut kw382 = Vec::new();
                    fun383.call(args381, kw382)?
                };
                e.set("features", assigned380.clone())?;
                let assigned387 = {
                    let fun390 = e.get("lid")?.attr("union")?;
                    let mut args388 = Vec::new();
                    let mut kw389 = Vec::new();
                    args388.push({
                        let fun393 = e.get("_above_mounts")?.attr("world_shape_in_cap")?;
                        let mut args391 = Vec::new();
                        let mut kw392 = Vec::new();
                        args391.push(e.get("features")?.get(Val::Str("lid_add".into()))?);
                        fun393.call(args391, kw392)?
                    });
                    fun390.call(args388, kw389)?
                };
                e.set("lid", assigned387.clone())?;
                let assigned394 = {
                    let fun397 = e.get("lid")?.attr("cut")?;
                    let mut args395 = Vec::new();
                    let mut kw396 = Vec::new();
                    args395.push({
                        let fun400 = e.get("_above_mounts")?.attr("world_shape_in_cap")?;
                        let mut args398 = Vec::new();
                        let mut kw399 = Vec::new();
                        args398.push(e.get("features")?.get(Val::Str("cut".into()))?);
                        fun400.call(args398, kw399)?
                    });
                    fun397.call(args395, kw396)?
                };
                e.set("lid", assigned394.clone())?;
            }
            e.set("_reservoir_b_fill", rt.import_module("_reservoir_b_fill")?)?;
            let assigned401 = {
                let fun404 = e.get("_above_mounts")?.attr("world_shape_in_cap")?;
                let mut args402 = Vec::new();
                let mut kw403 = Vec::new();
                args402.push({
                    let fun407 = e.get("_reservoir_b_fill")?.attr("guide_world")?;
                    let mut args405 = Vec::new();
                    let mut kw406 = Vec::new();
                    fun407.call(args405, kw406)?
                });
                fun404.call(args402, kw403)?
            };
            e.set("guide", assigned401.clone())?;
            let assigned408 = {
                let fun411 = e.get("guide")?.attr("BoundingBox")?;
                let mut args409 = Vec::new();
                let mut kw410 = Vec::new();
                fun411.call(args409, kw410)?
            };
            e.set("b", assigned408.clone())?;
            let assigned412 = {
                let fun415 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args413 = Vec::new();
                let mut kw414 = Vec::new();
                args413.push(binary(
                    "add",
                    e.get("b")?.attr("xlen")?,
                    Val::Float(0.3f64),
                )?);
                args413.push(binary(
                    "add",
                    e.get("b")?.attr("ylen")?,
                    Val::Float(0.3f64),
                )?);
                args413.push(binary(
                    "add",
                    e.get("lid_total_height")?,
                    Val::Float(0.2f64),
                )?);
                args413.push({
                    let fun418 = e.get("cq")?.attr("Vector")?;
                    let mut args416 = Vec::new();
                    let mut kw417 = Vec::new();
                    args416.push(binary(
                        "sub",
                        e.get("b")?.attr("xmin")?,
                        Val::Float(0.15f64),
                    )?);
                    args416.push(binary(
                        "sub",
                        e.get("b")?.attr("ymin")?,
                        Val::Float(0.15f64),
                    )?);
                    args416.push(unary("neg", Val::Float(0.1f64))?);
                    fun418.call(args416, kw417)?
                });
                fun415.call(args413, kw414)?
            };
            e.set("window", assigned412.clone())?;
            let assigned419 = {
                let fun422 = e.get("lid")?.attr("cut")?;
                let mut args420 = Vec::new();
                let mut kw421 = Vec::new();
                args420.push(e.get("window")?);
                fun422.call(args420, kw421)?
            };
            e.set("lid", assigned419.clone())?;
            return Ok(e.get("lid")?);
            Ok(Val::None)
        })
    })?;
    // build_bottom_cap
    e.set("build_bottom_cap", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned423 = e.get("bottom_cap_height")?;
            e.set("height", assigned423.clone())?;
            let assigned424 = {
                let fun427 = {
                    let fun430 = {
                        let fun433 = {
                            let fun436 = {
                                let fun439 = {
                                    let fun442 = {
                                        let fun445 = e.get("WorldWorkplane")?;
                                        let mut args443 = Vec::new();
                                        let mut kw444 = Vec::new();
                                        args443.push(e.get("xy_plane_z_up")?);
                                        fun445.call(args443, kw444)?
                                    }
                                    .attr("rect")?;
                                    let mut args440 = Vec::new();
                                    let mut kw441 = Vec::new();
                                    args440.push(e.get("outer_shell_x_length")?);
                                    args440.push(e.get("outer_shell_y_length")?);
                                    fun442.call(args440, kw441)?
                                }
                                .attr("extrude")?;
                                let mut args437 = Vec::new();
                                let mut kw438 = Vec::new();
                                args437.push(e.get("height")?);
                                fun439.call(args437, kw438)?
                            }
                            .attr("edges")?;
                            let mut args434 = Vec::new();
                            let mut kw435 = Vec::new();
                            args434.push(Val::Str("|Z".into()));
                            fun436.call(args434, kw435)?
                        }
                        .attr("fillet")?;
                        let mut args431 = Vec::new();
                        let mut kw432 = Vec::new();
                        args431.push(e.get("corner_round_radius")?);
                        fun433.call(args431, kw432)?
                    }
                    .attr("faces")?;
                    let mut args428 = Vec::new();
                    let mut kw429 = Vec::new();
                    args428.push(Val::Str(">Z".into()));
                    fun430.call(args428, kw429)?
                }
                .attr("shell")?;
                let mut args425 = Vec::new();
                let mut kw426 = Vec::new();
                args425.push(unary("neg", e.get("outer_shell_wall")?)?);
                fun427.call(args425, kw426)?
            };
            e.set("cap", assigned424.clone())?;
            let assigned446 = {
                let fun449 = e.get("trim_cup_floor")?;
                let mut args447 = Vec::new();
                let mut kw448 = Vec::new();
                args447.push(e.get("cap")?);
                args447.push(e.get("wall_and_floor_thickness")?);
                args447.push(e.get("outer_shell_wall")?);
                fun449.call(args447, kw448)?
            };
            e.set("cap", assigned446.clone())?;
            let assigned450 = {
                let fun453 = e.get("cap")?.attr("union")?;
                let mut args451 = Vec::new();
                let mut kw452 = Vec::new();
                args451.push({
                    let fun456 = e.get("build_attachment_bosses")?;
                    let mut args454 = Vec::new();
                    let mut kw455 = Vec::new();
                    args454.push(e.get("height")?);
                    fun456.call(args454, kw455)?
                });
                fun453.call(args451, kw452)?
            };
            e.set("cap", assigned450.clone())?;
            let assigned457 = {
                let fun460 = e.get("cap")?.attr("union")?;
                let mut args458 = Vec::new();
                let mut kw459 = Vec::new();
                args458.push({
                    let fun463 = e.get("build_attachment_bosses")?;
                    let mut args461 = Vec::new();
                    let mut kw462 = Vec::new();
                    args461.push(e.get("lid_total_height")?);
                    kw462.push(("oversize".into(), e.get("head_pad_growth")?));
                    fun463.call(args461, kw462)?
                });
                fun460.call(args458, kw459)?
            };
            e.set("cap", assigned457.clone())?;
            let assigned464 = {
                let fun467 = e.get("cap")?.attr("cut")?;
                let mut args465 = Vec::new();
                let mut kw466 = Vec::new();
                args465.push({
                    let fun470 = e.get("head_access_pockets")?;
                    let mut args468 = Vec::new();
                    let mut kw469 = Vec::new();
                    args468.push(Val::Float(0.0f64));
                    args468.push(binary(
                        "add",
                        e.get("head_cbore_depth")?,
                        e.get("fits")?.attr("supported_surface")?,
                    )?);
                    fun470.call(args468, kw469)?
                });
                fun467.call(args465, kw466)?
            };
            e.set("cap", assigned464.clone())?;
            let assigned471 = {
                let fun474 = e.get("cap")?.attr("cut")?;
                let mut args472 = Vec::new();
                let mut kw473 = Vec::new();
                args472.push({
                    let fun477 = e.get("attachment_clearances_extrude")?;
                    let mut args475 = Vec::new();
                    let mut kw476 = Vec::new();
                    args475.push(binary("add", e.get("height")?, Val::Float(0.1f64))?);
                    fun477.call(args475, kw476)?
                });
                fun474.call(args472, kw473)?
            };
            e.set("cap", assigned471.clone())?;
            let assigned478 = {
                let e = e.child();
                let out479 = Val::list(vec![]);
                for item480 in e.get("bottom_pour_positions")?.iter()? {
                    e.set("xy", item480)?;
                    out479.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(e.get("xy")?);
                            s.push(e.get("bottom_pour_radius")?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out479
            };
            e.set("holes", assigned478.clone())?;
            e.set(
                "holes",
                binary("add", e.get("holes")?, {
                    let e = e.child();
                    let out481 = Val::list(vec![]);
                    for item482 in {
                        let fun485 = e.get("foam_cap_lid_vent_xy")?;
                        let mut args483 = Vec::new();
                        let mut kw484 = Vec::new();
                        kw484.push(("top".into(), Val::Bool(false)));
                        fun485.call(args483, kw484)?
                    }
                    .iter()?
                    {
                        e.set("xy", item482)?;
                        out481.attr("append")?.call(
                            vec![{
                                let mut s = Vec::new();
                                s.push(e.get("xy")?);
                                s.push(e.get("foam_cap_lid_vent_radius")?);
                                Val::tuple(s)
                            }],
                            vec![],
                        )?;
                    }
                    out481
                })?,
            )?;
            for item486 in e.get("holes")?.iter()? {
                let unpack497 = unpack(item486, 2)?;
                e.set("xy", unpack497[0].clone())?;
                e.set("radius", unpack497[1].clone())?;
                let assigned487 = {
                    let fun490 = e.get("cap")?.attr("cut")?;
                    let mut args488 = Vec::new();
                    let mut kw489 = Vec::new();
                    args488.push({
                        let fun493 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                        let mut args491 = Vec::new();
                        let mut kw492 = Vec::new();
                        args491.push(e.get("radius")?);
                        args491.push(binary("add", e.get("height")?, Val::Float(0.2f64))?);
                        args491.push({
                            let fun496 = e.get("cq")?.attr("Vector")?;
                            let mut args494 = Vec::new();
                            let mut kw495 = Vec::new();
                            args494.extend(e.get("xy")?.iter()?);
                            args494.push(unary("neg", Val::Float(0.1f64))?);
                            fun496.call(args494, kw495)?
                        });
                        fun493.call(args491, kw492)?
                    });
                    fun490.call(args488, kw489)?
                };
                e.set("cap", assigned487.clone())?;
            }
            return Ok({
                let fun500 = {
                    let fun503 = e.get("cap")?.attr("clean")?;
                    let mut args501 = Vec::new();
                    let mut kw502 = Vec::new();
                    fun503.call(args501, kw502)?
                }
                .attr("unwrap")?;
                let mut args498 = Vec::new();
                let mut kw499 = Vec::new();
                fun500.call(args498, kw499)?
            });
            Ok(Val::None)
        })
    })?;
    // import_cap_part
    e.set("import_cap_part", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod504 = rt.import_module("pathlib")?;
            e.set("Path", rt.member("pathlib", "Path")?)?;
            let mod505 = rt.import_module("_cadq_export")?;
            e.set("import_step", rt.member("_cadq_export", "import_step")?)?;
            let assigned506 = {
                let fun509 = e.get("Path")?;
                let mut args507 = Vec::new();
                let mut kw508 = Vec::new();
                args507.push(e.get("path")?);
                fun509.call(args507, kw508)?
            };
            e.set("path", assigned506.clone())?;
            if unary("not", {
                let fun512 = e.get("getattr")?;
                let mut args510 = Vec::new();
                let mut kw511 = Vec::new();
                args510.push(e.get("cq")?);
                args510.push(Val::Str("MESH".into()));
                args510.push(Val::Bool(false));
                fun512.call(args510, kw511)?
            })?
            .truthy()?
            {
                let context513 = {
                    let fun516 = e.get("path")?.attr("open")?;
                    let mut args514 = Vec::new();
                    let mut kw515 = Vec::new();
                    args514.push(Val::Str("rb".into()));
                    fun516.call(args514, kw515)?
                };
                e.set(
                    "stream",
                    context513.attr("__enter__")?.call(vec![], vec![])?,
                )?;
                let context_result523 = (|| -> Result<Flow> {
                    let assigned517 = {
                        let v521 = Val::Bytes(vec![
                            109, 101, 115, 104, 99, 97, 100, 32, 116, 101, 115, 115, 101, 108, 108,
                            97, 116, 101, 100,
                        ]);
                        let v522 = {
                            let fun520 = e.get("stream")?.attr("read")?;
                            let mut args518 = Vec::new();
                            let mut kw519 = Vec::new();
                            args518.push(Val::Int(200i64));
                            fun520.call(args518, kw519)?
                        };
                        Val::Bool(compare("in", v521.clone(), v522.clone())?.truthy()?)
                    };
                    e.set("triangles", assigned517.clone())?;
                    Ok(Flow::Continue)
                })();
                context513
                    .attr("__exit__")?
                    .call(vec![Val::None, Val::None, Val::None], vec![])?;
                match context_result523? {
                    Flow::Continue => {}
                    Flow::Return(value) => return Ok(value),
                    Flow::Break => anyhow::bail!("break outside a loop"),
                    Flow::Next => anyhow::bail!("continue outside a loop"),
                }
                if e.get("triangles")?.truthy()? {
                    if {
                        let v524 = e.get("path")?.attr("stem")?;
                        let v525 = Val::Str("foam-cap-bottom".into());
                        Val::Bool(compare("eq", v524.clone(), v525.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        return Ok({
                            let fun528 = {
                                let fun531 = e.get("build_bottom_cap")?;
                                let mut args529 = Vec::new();
                                let mut kw530 = Vec::new();
                                fun531.call(args529, kw530)?
                            }
                            .attr("val")?;
                            let mut args526 = Vec::new();
                            let mut kw527 = Vec::new();
                            fun528.call(args526, kw527)?
                        });
                    }
                    if {
                        let v532 = e.get("path")?.attr("stem")?;
                        let v533 = Val::Str("foam-cap-lid-top".into());
                        Val::Bool(compare("eq", v532.clone(), v533.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        rt.import_module("importlib.util")?;
                        e.set("importlib", rt.import_module("importlib")?)?;
                        let assigned534 = binary(
                            "truediv",
                            binary(
                                "truediv",
                                {
                                    let fun537 = e.get("Path")?;
                                    let mut args535 = Vec::new();
                                    let mut kw536 = Vec::new();
                                    args535.push(e.get("__file__")?);
                                    fun537.call(args535, kw536)?
                                }
                                .attr("parent")?,
                                Val::Str("foam-cap".into()),
                            )?,
                            Val::Str("foam_cap.py".into()),
                        )?;
                        e.set("source", assigned534.clone())?;
                        let assigned538 = {
                            let fun541 = e
                                .get("importlib")?
                                .attr("util")?
                                .attr("spec_from_file_location")?;
                            let mut args539 = Vec::new();
                            let mut kw540 = Vec::new();
                            args539.push(Val::Str("_native_foam_cap".into()));
                            args539.push(e.get("source")?);
                            fun541.call(args539, kw540)?
                        };
                        e.set("spec", assigned538.clone())?;
                        let assigned542 = {
                            let fun545 =
                                e.get("importlib")?.attr("util")?.attr("module_from_spec")?;
                            let mut args543 = Vec::new();
                            let mut kw544 = Vec::new();
                            args543.push(e.get("spec")?);
                            fun545.call(args543, kw544)?
                        };
                        e.set("module", assigned542.clone())?;
                        {
                            let fun548 = e.get("spec")?.attr("loader")?.attr("exec_module")?;
                            let mut args546 = Vec::new();
                            let mut kw547 = Vec::new();
                            args546.push(e.get("module")?);
                            fun548.call(args546, kw547)?
                        };
                        return Ok({
                            let fun551 = {
                                let fun554 = e.get("module")?.attr("build_top_lid")?;
                                let mut args552 = Vec::new();
                                let mut kw553 = Vec::new();
                                fun554.call(args552, kw553)?
                            }
                            .attr("val")?;
                            let mut args549 = Vec::new();
                            let mut kw550 = Vec::new();
                            fun551.call(args549, kw550)?
                        });
                    }
                    if {
                        let v555 = e.get("path")?.attr("stem")?;
                        let v556 = Val::Str("reservoir-b-fill-guide".into());
                        Val::Bool(compare("eq", v555.clone(), v556.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.set("_reservoir_b_fill", rt.import_module("_reservoir_b_fill")?)?;
                        return Ok({
                            let fun559 = e.get("_reservoir_b_fill")?.attr("guide_native")?;
                            let mut args557 = Vec::new();
                            let mut kw558 = Vec::new();
                            fun559.call(args557, kw558)?
                        });
                    }
                    if {
                        let v560 = e.get("path")?.attr("stem")?;
                        let v561 = Val::Str("pump-snap-cap".into());
                        Val::Bool(compare("eq", v560.clone(), v561.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        return Ok({
                            let fun564 = e.get("_above_mounts")?.attr("pump_snap_printable")?;
                            let mut args562 = Vec::new();
                            let mut kw563 = Vec::new();
                            fun564.call(args562, kw563)?
                        });
                    }
                }
            }
            return Ok({
                let fun567 = {
                    let fun570 = e.get("import_step")?;
                    let mut args568 = Vec::new();
                    let mut kw569 = Vec::new();
                    args568.push({
                        let fun573 = e.get("str")?;
                        let mut args571 = Vec::new();
                        let mut kw572 = Vec::new();
                        args571.push(e.get("path")?);
                        fun573.call(args571, kw572)?
                    });
                    fun570.call(args568, kw569)?
                }
                .attr("val")?;
                let mut args565 = Vec::new();
                let mut kw566 = Vec::new();
                fun567.call(args565, kw566)?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
