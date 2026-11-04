#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
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
            Val::Str("cold-core".into()),
        )?);
        s.push(binary(
            "truediv",
            binary(
                "truediv",
                binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
                Val::Str("cold-core".into()),
            )?,
            Val::Str("reed-bridge".into()),
        )?);
        s.push(e.get("_here")?.attr("parent")?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_p", item17)?;
        if {
            let v21 = {
                let fun20 = e.get("str")?;
                let mut args18 = Vec::new();
                let mut kw19 = Vec::new();
                args18.push(e.get("_p")?);
                fun20.call(args18, kw19)?
            };
            let v22 = e.get("sys")?.attr("path")?;
            Val::Bool(compare("not_in", v21.clone(), v22.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let fun25 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args23 = Vec::new();
                let mut kw24 = Vec::new();
                args23.push(Val::Int(0i64));
                args23.push({
                    let fun28 = e.get("str")?;
                    let mut args26 = Vec::new();
                    let mut kw27 = Vec::new();
                    args26.push(e.get("_p")?);
                    fun28.call(args26, kw27)?
                });
                fun25.call(args23, kw24)?
            };
        }
    }
    e.set("F", rt.import_module("_fittings")?)?;
    let mod29 = rt.import_module("_cold_core_interface")?;
    e.set(
        "co2_inlet_y",
        rt.member("_cold_core_interface", "co2_inlet_y")?,
    )?;
    e.set(
        "hole_shift_from_edge",
        rt.member("_cold_core_interface", "hole_shift_from_edge")?,
    )?;
    e.set(
        "prv_port_y",
        rt.member("_cold_core_interface", "prv_port_y")?,
    )?;
    e.set(
        "carbonator_height",
        rt.member("_cold_core_interface", "carbonator_height")?,
    )?;
    e.set(
        "carbonator_outer_radius",
        rt.member("_cold_core_interface", "carbonator_outer_radius")?,
    )?;
    e.set(
        "carbonator_support_ring_height",
        rt.member("_cold_core_interface", "carbonator_support_ring_height")?,
    )?;
    e.set(
        "carbonator_top_plate_z",
        rt.member("_cold_core_interface", "carbonator_top_plate_z")?,
    )?;
    e.set(
        "carbonator_port_offset",
        rt.member("_cold_core_interface", "carbonator_port_offset")?,
    )?;
    e.set(
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
    )?;
    e.set(
        "water_inlet_port_y",
        rt.member("_cold_core_interface", "water_inlet_port_y")?,
    )?;
    e.set(
        "carbonator_sensor_axis",
        rt.member("_cold_core_interface", "carbonator_sensor_axis")?,
    )?;
    e.set(
        "carbonator_float_top_stop_height",
        rt.member("_cold_core_interface", "carbonator_float_top_stop_height")?,
    )?;
    e.set(
        "carbonator_float_top_stop_diameter",
        rt.member("_cold_core_interface", "carbonator_float_top_stop_diameter")?,
    )?;
    let mod30 = rt.import_module("_port_cuts")?;
    e.set(
        "front_face_port_z",
        rt.member("_port_cuts", "front_face_port_z")?,
    )?;
    e.set("_R", rt.import_module("_internal_routes")?)?;
    e.set("_bond", rt.import_module("_carbonator_bond")?)?;
    let assigned31 = binary(
        "truediv",
        binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("cut-parts".into()))?,
            Val::Str("carbonation".into()),
        )?,
        Val::Str("endcaps-circular".into()),
    )?;
    e.set("_cut", assigned31.clone())?;
    {
        let fun34 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args32 = Vec::new();
        let mut kw33 = Vec::new();
        args32.push(Val::Int(0i64));
        args32.push({
            let fun37 = e.get("str")?;
            let mut args35 = Vec::new();
            let mut kw36 = Vec::new();
            args35.push(e.get("_cut")?);
            fun37.call(args35, kw36)?
        });
        fun34.call(args32, kw33)?
    };
    e.set("_endcap", rt.import_module("endcap_circular_dxf")?)?;
    let assigned38 = Val::Float(25.4f64);
    e.set("IN", assigned38.clone())?;
    let mod39 = rt.import_module("_carbonator_stock")?;
    e.set("TUBE_OD", rt.member("_carbonator_stock", "TUBE_OD")?)?;
    e.set("TUBE_WALL", rt.member("_carbonator_stock", "TUBE_WALL")?)?;
    e.set("TUBE_ID", rt.member("_carbonator_stock", "TUBE_ID")?)?;
    let assigned40 = binary(
        "add",
        e.get("wall_and_floor_thickness")?,
        e.get("carbonator_support_ring_height")?,
    )?;
    e.set("carbonator_bottom_z", assigned40.clone())?;
    let assigned41 = e.get("carbonator_top_plate_z")?;
    e.set("carbonator_top_z", assigned41.clone())?;
    let assigned42 = binary(
        "mul",
        e.get("_endcap")?.attr("disc_diameter")?,
        e.get("IN")?,
    )?;
    e.set("PLATE_D", assigned42.clone())?;
    let assigned43 = binary(
        "mul",
        e.get("_endcap")?.attr("disc_thickness")?,
        e.get("IN")?,
    )?;
    e.set("PLATE_T", assigned43.clone())?;
    let assigned44 = e.get("PLATE_T")?;
    e.set("PLATE_RECESS", assigned44.clone())?;
    let assigned45 = {
        let mut s = Vec::new();
        s.push(binary(
            "add",
            e.get("carbonator_bottom_z")?,
            e.get("PLATE_RECESS")?,
        )?);
        s.push(binary(
            "add",
            binary("add", e.get("carbonator_bottom_z")?, e.get("PLATE_RECESS")?)?,
            e.get("PLATE_T")?,
        )?);
        Val::tuple(s)
    };
    e.set("bottom_plate_z", assigned45.clone())?;
    let assigned46 = {
        let mut s = Vec::new();
        s.push(binary(
            "sub",
            binary("sub", e.get("carbonator_top_z")?, e.get("PLATE_RECESS")?)?,
            e.get("PLATE_T")?,
        )?);
        s.push(binary(
            "sub",
            e.get("carbonator_top_z")?,
            e.get("PLATE_RECESS")?,
        )?);
        Val::tuple(s)
    };
    e.set("top_plate_z", assigned46.clone())?;
    let assigned47 = {
        let mut s = Vec::new();
        s.push(e.get("bottom_plate_z")?.get(Val::Int(1i64))?);
        s.push(e.get("top_plate_z")?.get(Val::Int(0i64))?);
        Val::tuple(s)
    };
    e.set("interior_z", assigned47.clone())?;
    let assigned48 = binary(
        "mul",
        e.get("_endcap")?.attr("hole_diameter")?,
        e.get("IN")?,
    )?;
    e.set("PORT_TAP_D", assigned48.clone())?;
    let assigned49 = binary("mul", Val::Float(0.125f64), e.get("IN")?)?;
    e.set("ROD_D", assigned49.clone())?;
    let assigned50 = binary(
        "mul",
        e.get("_endcap")?.attr("register_radius")?,
        e.get("IN")?,
    )?;
    e.set("ROD_RADIUS", assigned50.clone())?;
    let assigned51 = {
        let fun54 = e.get("tuple")?;
        let mut args52 = Vec::new();
        let mut kw53 = Vec::new();
        args52.push({
            let e = e.child();
            let out55 = Val::list(vec![]);
            for item56 in e.get("carbonator_sensor_axis")?.iter()? {
                e.set("v", item56)?;
                out55.attr("append")?.call(
                    vec![binary("mul", e.get("ROD_RADIUS")?, e.get("v")?)?],
                    vec![],
                )?;
            }
            out55
        });
        fun54.call(args52, kw53)?
    };
    e.set("ROD_XY", assigned51.clone())?;
    let assigned57 = binary(
        "mul",
        e.get("_endcap")?.attr("register_depth")?,
        e.get("IN")?,
    )?;
    e.set("REGISTER_DEPTH", assigned57.clone())?;
    let assigned58 = e.get("carbonator_float_top_stop_height")?;
    e.set("UPPER_STOP_H", assigned58.clone())?;
    let assigned59 = e.get("carbonator_float_top_stop_diameter")?;
    e.set("UPPER_STOP_D", assigned59.clone())?;
    let assigned60 = binary(
        "mul",
        e.get("_endcap")?.attr("register_drill_diameter")?,
        e.get("IN")?,
    )?;
    e.set("UPPER_STOP_BORE", assigned60.clone())?;
    let assigned61 = binary(
        "add",
        e.get("hole_shift_from_edge")?,
        e.get("PLATE_RECESS")?,
    )?;
    e.set("ELBOW_AXIS_OFFSET", assigned61.clone())?;
    let assigned62 = binary(
        "sub",
        e.get("bottom_plate_z")?.get(Val::Int(0i64))?,
        e.get("front_face_port_z")?,
    )?;
    e.set("BOTTOM_AXIS_OFFSET", assigned62.clone())?;
    let assigned63 = binary(
        "add",
        binary(
            "sub",
            e.get("F")?.attr("MALE_ELBOW_THREAD")?,
            e.get("F")?.attr("ELBOW_MALE_LEN")?,
        )?,
        e.get("F")?.attr("MALE_ELBOW_AXIS_REACH")?,
    )?;
    e.set("BOTTOM_CATALOG_OFFSET", assigned63.clone())?;
    let assigned64 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("co2-in".into()), {
            let d = Val::dict(vec![]);
            d.set(Val::Str("y".into()), e.get("co2_inlet_y")?)?;
            d.set(Val::Str("plate".into()), Val::Str("bottom".into()))?;
            d
        })?;
        d.set(Val::Str("carb-water-out".into()), {
            let d = Val::dict(vec![]);
            d.set(Val::Str("y".into()), unary("neg", e.get("co2_inlet_y")?)?)?;
            d.set(Val::Str("plate".into()), Val::Str("bottom".into()))?;
            d
        })?;
        d.set(Val::Str("water-in".into()), {
            let d = Val::dict(vec![]);
            d.set(Val::Str("y".into()), e.get("water_inlet_port_y")?)?;
            d.set(Val::Str("plate".into()), Val::Str("top".into()))?;
            d
        })?;
        d.set(Val::Str("prv".into()), {
            let d = Val::dict(vec![]);
            d.set(Val::Str("y".into()), e.get("prv_port_y")?)?;
            d.set(Val::Str("plate".into()), Val::Str("top".into()))?;
            d
        })?;
        d
    };
    e.set("PORTS", assigned64.clone())?;
    // axis_offset
    e.set("axis_offset", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(
                if {
                    let v65 = e
                        .get("PORTS")?
                        .get(e.get("name")?)?
                        .get(Val::Str("plate".into()))?;
                    let v66 = Val::Str("bottom".into());
                    Val::Bool(compare("eq", v65.clone(), v66.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("BOTTOM_AXIS_OFFSET")?
                } else {
                    e.get("ELBOW_AXIS_OFFSET")?
                },
            );
            Ok(Val::None)
        })
    })?;
    // port_corner
    e.set("port_corner", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned67 = e.get("PORTS")?.get(e.get("name")?)?;
            e.set("spec", assigned67.clone())?;
            if {
                let v68 = e.get("spec")?.get(Val::Str("plate".into()))?;
                let v69 = Val::Str("bottom".into());
                Val::Bool(compare("eq", v68.clone(), v69.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned70 = binary("sub", e.get("bottom_plate_z")?.get(Val::Int(0i64))?, {
                    let fun73 = e.get("axis_offset")?;
                    let mut args71 = Vec::new();
                    let mut kw72 = Vec::new();
                    args71.push(e.get("name")?);
                    fun73.call(args71, kw72)?
                })?;
                e.set("z", assigned70.clone())?;
            } else {
                let assigned74 = binary("add", e.get("top_plate_z")?.get(Val::Int(1i64))?, {
                    let fun77 = e.get("axis_offset")?;
                    let mut args75 = Vec::new();
                    let mut kw76 = Vec::new();
                    args75.push(e.get("name")?);
                    fun77.call(args75, kw76)?
                })?;
                e.set("z", assigned74.clone())?;
            }
            return Ok({
                let mut s = Vec::new();
                s.push(Val::Float(0.0f64));
                s.push(e.get("spec")?.get(Val::Str("y".into()))?);
                s.push(e.get("z")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // port_up
    e.set("port_up", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(
                if {
                    let v78 = e
                        .get("PORTS")?
                        .get(e.get("name")?)?
                        .get(Val::Str("plate".into()))?;
                    let v79 = Val::Str("bottom".into());
                    Val::Bool(compare("eq", v78.clone(), v79.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        Val::tuple(s)
                    }
                } else {
                    {
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        Val::tuple(s)
                    }
                },
            );
            Ok(Val::None)
        })
    })?;
    let assigned80 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("co2-in".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("co2-in".into()));
            s.push(Val::Str("end".into()));
            Val::tuple(s)
        })?;
        d.set(Val::Str("carb-water-out".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("carb-water-out".into()));
            s.push(Val::Str("start".into()));
            Val::tuple(s)
        })?;
        d.set(Val::Str("water-in".into()), {
            let mut s = Vec::new();
            s.push(Val::Str("water-in".into()));
            s.push(Val::Str("start".into()));
            Val::tuple(s)
        })?;
        d
    };
    e.set("PORT_LINES", assigned80.clone())?;
    let assigned81 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.0f64));
        s.push(
            if {
                let v82 = e.get("prv_port_y")?;
                let v83 = Val::Int(0i64);
                Val::Bool(compare("gt", v82.clone(), v83.clone())?.truthy()?)
            }
            .truthy()?
            {
                Val::Float(1.0f64)
            } else {
                unary("neg", Val::Float(1.0f64))?
            },
        );
        s.push(Val::Float(0.0f64));
        Val::tuple(s)
    };
    e.set("PRV_OUT", assigned81.clone())?;
    // port_out
    e.set("port_out", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned84 = {
                let fun87 = e.get("PORT_LINES")?.attr("get")?;
                let mut args85 = Vec::new();
                let mut kw86 = Vec::new();
                args85.push(e.get("name")?);
                fun87.call(args85, kw86)?
            };
            e.set("spec", assigned84.clone())?;
            if {
                let v88 = e.get("spec")?;
                let v89 = Val::None;
                Val::Bool(compare("is", v88.clone(), v89.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("PRV_OUT")?);
            }
            let assigned90 = e.get("spec")?;
            let unpack91 = unpack(assigned90.clone(), 2)?;
            e.set("line", unpack91[0].clone())?;
            e.set("which", unpack91[1].clone())?;
            let assigned92 = e.get("_R")?.attr("routes")?.get(e.get("line")?)?;
            e.set("pts", assigned92.clone())?;
            let assigned93 = if {
                let v94 = e.get("which")?;
                let v95 = Val::Str("start".into());
                Val::Bool(compare("eq", v94.clone(), v95.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let mut s = Vec::new();
                    s.push(e.get("pts")?.get(Val::Int(0i64))?);
                    s.push(e.get("pts")?.get(Val::Int(1i64))?);
                    Val::tuple(s)
                }
            } else {
                {
                    let mut s = Vec::new();
                    s.push(e.get("pts")?.get(unary("neg", Val::Int(1i64))?)?);
                    s.push(e.get("pts")?.get(unary("neg", Val::Int(2i64))?)?);
                    Val::tuple(s)
                }
            };
            let unpack96 = unpack(assigned93.clone(), 2)?;
            e.set("a", unpack96[0].clone())?;
            e.set("b", unpack96[1].clone())?;
            return Ok({
                let fun99 = e.get("tuple")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                args97.push({
                    let fun102 = {
                        let fun105 = {
                            let fun108 = {
                                let fun111 = e.get("cq")?.attr("Vector")?;
                                let mut args109 = Vec::new();
                                let mut kw110 = Vec::new();
                                args109.extend(e.get("b")?.iter()?);
                                fun111.call(args109, kw110)?
                            }
                            .attr("sub")?;
                            let mut args106 = Vec::new();
                            let mut kw107 = Vec::new();
                            args106.push({
                                let fun114 = e.get("cq")?.attr("Vector")?;
                                let mut args112 = Vec::new();
                                let mut kw113 = Vec::new();
                                args112.extend(e.get("a")?.iter()?);
                                fun114.call(args112, kw113)?
                            });
                            fun108.call(args106, kw107)?
                        }
                        .attr("normalized")?;
                        let mut args103 = Vec::new();
                        let mut kw104 = Vec::new();
                        fun105.call(args103, kw104)?
                    }
                    .attr("toTuple")?;
                    let mut args100 = Vec::new();
                    let mut kw101 = Vec::new();
                    fun102.call(args100, kw101)?
                });
                fun99.call(args97, kw98)?
            });
            Ok(Val::None)
        })
    })?;
    // build_tube
    e.set("build_tube", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned115 = {
                let fun118 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args116 = Vec::new();
                let mut kw117 = Vec::new();
                args116.push(binary("truediv", e.get("TUBE_OD")?, Val::Int(2i64))?);
                args116.push(e.get("carbonator_height")?);
                args116.push({
                    let fun121 = e.get("cq")?.attr("Vector")?;
                    let mut args119 = Vec::new();
                    let mut kw120 = Vec::new();
                    args119.push(Val::Int(0i64));
                    args119.push(Val::Int(0i64));
                    args119.push(e.get("carbonator_bottom_z")?);
                    fun121.call(args119, kw120)?
                });
                args116.push({
                    let fun124 = e.get("cq")?.attr("Vector")?;
                    let mut args122 = Vec::new();
                    let mut kw123 = Vec::new();
                    args122.push(Val::Int(0i64));
                    args122.push(Val::Int(0i64));
                    args122.push(Val::Int(1i64));
                    fun124.call(args122, kw123)?
                });
                fun118.call(args116, kw117)?
            };
            e.set("outer", assigned115.clone())?;
            let assigned125 = {
                let fun128 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args126 = Vec::new();
                let mut kw127 = Vec::new();
                args126.push(binary("truediv", e.get("TUBE_ID")?, Val::Int(2i64))?);
                args126.push(binary("add", e.get("carbonator_height")?, Val::Int(2i64))?);
                args126.push({
                    let fun131 = e.get("cq")?.attr("Vector")?;
                    let mut args129 = Vec::new();
                    let mut kw130 = Vec::new();
                    args129.push(Val::Int(0i64));
                    args129.push(Val::Int(0i64));
                    args129.push(binary(
                        "sub",
                        e.get("carbonator_bottom_z")?,
                        Val::Int(1i64),
                    )?);
                    fun131.call(args129, kw130)?
                });
                args126.push({
                    let fun134 = e.get("cq")?.attr("Vector")?;
                    let mut args132 = Vec::new();
                    let mut kw133 = Vec::new();
                    args132.push(Val::Int(0i64));
                    args132.push(Val::Int(0i64));
                    args132.push(Val::Int(1i64));
                    fun134.call(args132, kw133)?
                });
                fun128.call(args126, kw127)?
            };
            e.set("bore", assigned125.clone())?;
            return Ok({
                let fun137 = e.get("_bond")?.attr("cut_tube")?;
                let mut args135 = Vec::new();
                let mut kw136 = Vec::new();
                args135.push({
                    let fun140 = e.get("outer")?.attr("cut")?;
                    let mut args138 = Vec::new();
                    let mut kw139 = Vec::new();
                    args138.push(e.get("bore")?);
                    fun140.call(args138, kw139)?
                });
                args135.push(e.get("top_plate_z")?.get(Val::Int(1i64))?);
                fun137.call(args135, kw136)?
            });
            Ok(Val::None)
        })
    })?;
    // build_plate
    e.set("build_plate", {
        let params = vec![("which".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned141 = if {
                let v142 = e.get("which")?;
                let v143 = Val::Str("bottom".into());
                Val::Bool(compare("eq", v142.clone(), v143.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.get("bottom_plate_z")?
            } else {
                e.get("top_plate_z")?
            };
            let unpack144 = unpack(assigned141.clone(), 2)?;
            e.set("z0", unpack144[0].clone())?;
            e.set("z1", unpack144[1].clone())?;
            let assigned145 = {
                let fun148 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args146 = Vec::new();
                let mut kw147 = Vec::new();
                args146.push(binary("truediv", e.get("PLATE_D")?, Val::Int(2i64))?);
                args146.push(e.get("PLATE_T")?);
                args146.push({
                    let fun151 = e.get("cq")?.attr("Vector")?;
                    let mut args149 = Vec::new();
                    let mut kw150 = Vec::new();
                    args149.push(Val::Int(0i64));
                    args149.push(Val::Int(0i64));
                    args149.push(e.get("z0")?);
                    fun151.call(args149, kw150)?
                });
                args146.push({
                    let fun154 = e.get("cq")?.attr("Vector")?;
                    let mut args152 = Vec::new();
                    let mut kw153 = Vec::new();
                    args152.push(Val::Int(0i64));
                    args152.push(Val::Int(0i64));
                    args152.push(Val::Int(1i64));
                    fun154.call(args152, kw153)?
                });
                fun148.call(args146, kw147)?
            };
            e.set("plate", assigned145.clone())?;
            for item155 in {
                let fun173 = e.get("PORTS")?.attr("values")?;
                let mut args171 = Vec::new();
                let mut kw172 = Vec::new();
                fun173.call(args171, kw172)?
            }
            .iter()?
            {
                e.set("spec", item155)?;
                if {
                    let v156 = e.get("spec")?.get(Val::Str("plate".into()))?;
                    let v157 = e.get("which")?;
                    Val::Bool(compare("ne", v156.clone(), v157.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned158 = {
                    let fun161 = e.get("plate")?.attr("cut")?;
                    let mut args159 = Vec::new();
                    let mut kw160 = Vec::new();
                    args159.push({
                        let fun164 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                        let mut args162 = Vec::new();
                        let mut kw163 = Vec::new();
                        args162.push(binary("truediv", e.get("PORT_TAP_D")?, Val::Int(2i64))?);
                        args162.push(binary("add", e.get("PLATE_T")?, Val::Int(2i64))?);
                        args162.push({
                            let fun167 = e.get("cq")?.attr("Vector")?;
                            let mut args165 = Vec::new();
                            let mut kw166 = Vec::new();
                            args165.push(Val::Int(0i64));
                            args165.push(e.get("spec")?.get(Val::Str("y".into()))?);
                            args165.push(binary("sub", e.get("z0")?, Val::Int(1i64))?);
                            fun167.call(args165, kw166)?
                        });
                        args162.push({
                            let fun170 = e.get("cq")?.attr("Vector")?;
                            let mut args168 = Vec::new();
                            let mut kw169 = Vec::new();
                            args168.push(Val::Int(0i64));
                            args168.push(Val::Int(0i64));
                            args168.push(Val::Int(1i64));
                            fun170.call(args168, kw169)?
                        });
                        fun164.call(args162, kw163)?
                    });
                    fun161.call(args159, kw160)?
                };
                e.set("plate", assigned158.clone())?;
            }
            let assigned174 = if {
                let v175 = e.get("which")?;
                let v176 = Val::Str("bottom".into());
                Val::Bool(compare("eq", v175.clone(), v176.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.get("z1")?
            } else {
                e.get("z0")?
            };
            e.set("inside_z", assigned174.clone())?;
            let assigned177 = if {
                let v178 = e.get("which")?;
                let v179 = Val::Str("bottom".into());
                Val::Bool(compare("eq", v178.clone(), v179.clone())?.truthy()?)
            }
            .truthy()?
            {
                unary("neg", Val::Float(1.0f64))?
            } else {
                unary("pos", Val::Float(1.0f64))?
            };
            e.set("direction", assigned177.clone())?;
            let assigned180 = {
                let fun183 = e.get("plate")?.attr("cut")?;
                let mut args181 = Vec::new();
                let mut kw182 = Vec::new();
                args181.push({
                    let fun186 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                    let mut args184 = Vec::new();
                    let mut kw185 = Vec::new();
                    args184.push(binary(
                        "truediv",
                        binary(
                            "mul",
                            e.get("_endcap")?.attr("register_drill_diameter")?,
                            e.get("IN")?,
                        )?,
                        Val::Int(2i64),
                    )?);
                    args184.push(e.get("REGISTER_DEPTH")?);
                    args184.push({
                        let fun189 = e.get("cq")?.attr("Vector")?;
                        let mut args187 = Vec::new();
                        let mut kw188 = Vec::new();
                        args187.extend(e.get("ROD_XY")?.iter()?);
                        args187.push(e.get("inside_z")?);
                        fun189.call(args187, kw188)?
                    });
                    args184.push({
                        let fun192 = e.get("cq")?.attr("Vector")?;
                        let mut args190 = Vec::new();
                        let mut kw191 = Vec::new();
                        args190.push(Val::Int(0i64));
                        args190.push(Val::Int(0i64));
                        args190.push(e.get("direction")?);
                        fun192.call(args190, kw191)?
                    });
                    fun186.call(args184, kw185)?
                });
                fun183.call(args181, kw182)?
            };
            e.set("plate", assigned180.clone())?;
            return Ok(e.get("plate")?);
            Ok(Val::None)
        })
    })?;
    // build_rod
    e.set("build_rod", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned193 = binary(
                "sub",
                e.get("interior_z")?.get(Val::Int(0i64))?,
                e.get("REGISTER_DEPTH")?,
            )?;
            e.set("z0", assigned193.clone())?;
            let assigned194 = binary(
                "add",
                e.get("interior_z")?.get(Val::Int(1i64))?,
                e.get("REGISTER_DEPTH")?,
            )?;
            e.set("z1", assigned194.clone())?;
            return Ok({
                let fun197 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args195 = Vec::new();
                let mut kw196 = Vec::new();
                args195.push(binary("truediv", e.get("ROD_D")?, Val::Int(2i64))?);
                args195.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                args195.push({
                    let fun200 = e.get("cq")?.attr("Vector")?;
                    let mut args198 = Vec::new();
                    let mut kw199 = Vec::new();
                    args198.extend(e.get("ROD_XY")?.iter()?);
                    args198.push(e.get("z0")?);
                    fun200.call(args198, kw199)?
                });
                args195.push({
                    let fun203 = e.get("cq")?.attr("Vector")?;
                    let mut args201 = Vec::new();
                    let mut kw202 = Vec::new();
                    args201.push(Val::Int(0i64));
                    args201.push(Val::Int(0i64));
                    args201.push(Val::Int(1i64));
                    fun203.call(args201, kw202)?
                });
                fun197.call(args195, kw196)?
            });
            Ok(Val::None)
        })
    })?;
    // build_upper_float_stop
    e.set("build_upper_float_stop", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned204 = {
                let fun207 = e.get("cq")?.attr("Vector")?;
                let mut args205 = Vec::new();
                let mut kw206 = Vec::new();
                args205.extend(e.get("ROD_XY")?.iter()?);
                args205.push(binary(
                    "sub",
                    e.get("interior_z")?.get(Val::Int(1i64))?,
                    e.get("UPPER_STOP_H")?,
                )?);
                fun207.call(args205, kw206)?
            };
            e.set("base", assigned204.clone())?;
            let assigned208 = {
                let fun211 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args209 = Vec::new();
                let mut kw210 = Vec::new();
                args209.push(binary("truediv", e.get("UPPER_STOP_D")?, Val::Int(2i64))?);
                args209.push(e.get("UPPER_STOP_H")?);
                args209.push(e.get("base")?);
                fun211.call(args209, kw210)?
            };
            e.set("outer", assigned208.clone())?;
            let assigned212 = {
                let fun215 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args213 = Vec::new();
                let mut kw214 = Vec::new();
                args213.push(binary(
                    "truediv",
                    e.get("UPPER_STOP_BORE")?,
                    Val::Int(2i64),
                )?);
                args213.push(binary("add", e.get("UPPER_STOP_H")?, Val::Int(2i64))?);
                args213.push(binary("sub", e.get("base")?, {
                    let fun218 = e.get("cq")?.attr("Vector")?;
                    let mut args216 = Vec::new();
                    let mut kw217 = Vec::new();
                    args216.push(Val::Int(0i64));
                    args216.push(Val::Int(0i64));
                    args216.push(Val::Int(1i64));
                    fun218.call(args216, kw217)?
                })?);
                fun215.call(args213, kw214)?
            };
            e.set("bore", assigned212.clone())?;
            return Ok({
                let fun221 = e.get("outer")?.attr("cut")?;
                let mut args219 = Vec::new();
                let mut kw220 = Vec::new();
                args219.push(e.get("bore")?);
                fun221.call(args219, kw220)?
            });
            Ok(Val::None)
        })
    })?;
    // rod_length
    e.set("rod_length", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "sub",
                binary(
                    "add",
                    e.get("interior_z")?.get(Val::Int(1i64))?,
                    e.get("REGISTER_DEPTH")?,
                )?,
                binary(
                    "sub",
                    e.get("interior_z")?.get(Val::Int(0i64))?,
                    e.get("REGISTER_DEPTH")?,
                )?,
            )?);
            Ok(Val::None)
        })
    })?;
    // build_elbows
    e.set("build_elbows", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned222 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("out", assigned222.clone())?;
            for item223 in e.get("PORTS")?.iter()? {
                e.set("name", item223)?;
                if {
                    let v224 = e
                        .get("PORTS")?
                        .get(e.get("name")?)?
                        .get(Val::Str("plate".into()))?;
                    let v225 = Val::Str("bottom".into());
                    Val::Bool(compare("eq", v224.clone(), v225.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned226 = {
                        let fun229 = e.get("F")?.attr("male_elbow")?;
                        let mut args227 = Vec::new();
                        let mut kw228 = Vec::new();
                        kw228.push(("corner".into(), {
                            let fun232 = e.get("port_corner")?;
                            let mut args230 = Vec::new();
                            let mut kw231 = Vec::new();
                            args230.push(e.get("name")?);
                            fun232.call(args230, kw231)?
                        }));
                        kw228.push(("up".into(), {
                            let fun235 = e.get("port_up")?;
                            let mut args233 = Vec::new();
                            let mut kw234 = Vec::new();
                            args233.push(e.get("name")?);
                            fun235.call(args233, kw234)?
                        }));
                        kw228.push(("out".into(), {
                            let fun238 = e.get("port_out")?;
                            let mut args236 = Vec::new();
                            let mut kw237 = Vec::new();
                            args236.push(e.get("name")?);
                            fun238.call(args236, kw237)?
                        }));
                        fun229.call(args227, kw228)?
                    };
                    e.get("out")?.set(e.get("name")?, assigned226.clone())?;
                } else {
                    let assigned239 = {
                        let fun242 = e.get("F")?.attr("street_elbow")?;
                        let mut args240 = Vec::new();
                        let mut kw241 = Vec::new();
                        kw241.push(("corner".into(), {
                            let fun245 = e.get("port_corner")?;
                            let mut args243 = Vec::new();
                            let mut kw244 = Vec::new();
                            args243.push(e.get("name")?);
                            fun245.call(args243, kw244)?
                        }));
                        kw241.push(("up".into(), {
                            let fun248 = e.get("port_up")?;
                            let mut args246 = Vec::new();
                            let mut kw247 = Vec::new();
                            args246.push(e.get("name")?);
                            fun248.call(args246, kw247)?
                        }));
                        kw241.push(("out".into(), {
                            let fun251 = e.get("port_out")?;
                            let mut args249 = Vec::new();
                            let mut kw250 = Vec::new();
                            args249.push(e.get("name")?);
                            fun251.call(args249, kw250)?
                        }));
                        kw241.push(("up_leg".into(), e.get("ELBOW_AXIS_OFFSET")?));
                        kw241.push(("male_len".into(), {
                            let fun254 = e.get("male_len")?;
                            let mut args252 = Vec::new();
                            let mut kw253 = Vec::new();
                            args252.push(e.get("name")?);
                            fun254.call(args252, kw253)?
                        }));
                        fun242.call(args240, kw241)?
                    };
                    e.get("out")?.set(e.get("name")?, assigned239.clone())?;
                }
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // male_len
    e.set("male_len", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v255 = e
                    .get("PORTS")?
                    .get(e.get("name")?)?
                    .get(Val::Str("plate".into()))?;
                let v256 = Val::Str("bottom".into());
                Val::Bool(compare("eq", v255.clone(), v256.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(binary(
                    "sub",
                    e.get("F")?.attr("MALE_ELBOW_THREAD")?,
                    binary(
                        "sub",
                        e.get("BOTTOM_AXIS_OFFSET")?,
                        e.get("F")?.attr("MALE_ELBOW_AXIS_REACH")?,
                    )?,
                )?);
            }
            return Ok(e.get("F")?.attr("ELBOW_MALE_LEN")?);
            Ok(Val::None)
        })
    })?;
    // port_male_tip
    e.set("port_male_tip", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun259 = e.get("tuple")?;
                let mut args257 = Vec::new();
                let mut kw258 = Vec::new();
                args257.push(binary(
                    "add",
                    {
                        let fun262 = e.get("cq")?.attr("Vector")?;
                        let mut args260 = Vec::new();
                        let mut kw261 = Vec::new();
                        args260.extend(
                            {
                                let fun265 = e.get("port_corner")?;
                                let mut args263 = Vec::new();
                                let mut kw264 = Vec::new();
                                args263.push(e.get("name")?);
                                fun265.call(args263, kw264)?
                            }
                            .iter()?,
                        );
                        fun262.call(args260, kw261)?
                    },
                    {
                        let fun268 = {
                            let fun271 = e.get("cq")?.attr("Vector")?;
                            let mut args269 = Vec::new();
                            let mut kw270 = Vec::new();
                            args269.extend(
                                {
                                    let fun274 = e.get("port_up")?;
                                    let mut args272 = Vec::new();
                                    let mut kw273 = Vec::new();
                                    args272.push(e.get("name")?);
                                    fun274.call(args272, kw273)?
                                }
                                .iter()?,
                            );
                            fun271.call(args269, kw270)?
                        }
                        .attr("multiply")?;
                        let mut args266 = Vec::new();
                        let mut kw267 = Vec::new();
                        args266.push(binary(
                            "add",
                            {
                                let fun277 = e.get("axis_offset")?;
                                let mut args275 = Vec::new();
                                let mut kw276 = Vec::new();
                                args275.push(e.get("name")?);
                                fun277.call(args275, kw276)?
                            },
                            {
                                let fun280 = e.get("male_len")?;
                                let mut args278 = Vec::new();
                                let mut kw279 = Vec::new();
                                args278.push(e.get("name")?);
                                fun280.call(args278, kw279)?
                            },
                        )?);
                        fun268.call(args266, kw267)?
                    },
                )?);
                fun259.call(args257, kw258)?
            });
            Ok(Val::None)
        })
    })?;
    // bodies
    e.set("bodies", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned281 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("carbonator-tube".into()), {
                    let fun284 = e.get("build_tube")?;
                    let mut args282 = Vec::new();
                    let mut kw283 = Vec::new();
                    fun284.call(args282, kw283)?
                })?;
                d.set(Val::Str("endcap-bottom".into()), {
                    let fun287 = e.get("build_plate")?;
                    let mut args285 = Vec::new();
                    let mut kw286 = Vec::new();
                    args285.push(Val::Str("bottom".into()));
                    fun287.call(args285, kw286)?
                })?;
                d.set(Val::Str("endcap-top".into()), {
                    let fun290 = e.get("build_plate")?;
                    let mut args288 = Vec::new();
                    let mut kw289 = Vec::new();
                    args288.push(Val::Str("top".into()));
                    fun290.call(args288, kw289)?
                })?;
                d.set(Val::Str("float-rod-carb".into()), {
                    let fun293 = e.get("build_rod")?;
                    let mut args291 = Vec::new();
                    let mut kw292 = Vec::new();
                    fun293.call(args291, kw292)?
                })?;
                d.set(Val::Str("float-stop-carb-top".into()), {
                    let fun296 = e.get("build_upper_float_stop")?;
                    let mut args294 = Vec::new();
                    let mut kw295 = Vec::new();
                    fun296.call(args294, kw295)?
                })?;
                d
            };
            e.set("out", assigned281.clone())?;
            {
                let fun299 = e.get("out")?.attr("update")?;
                let mut args297 = Vec::new();
                let mut kw298 = Vec::new();
                args297.push({
                    let fun302 = e.get("_bond")?.attr("build_hardware")?;
                    let mut args300 = Vec::new();
                    let mut kw301 = Vec::new();
                    args300.push(e.get("top_plate_z")?.get(Val::Int(1i64))?);
                    fun302.call(args300, kw301)?
                });
                fun299.call(args297, kw298)?
            };
            for item303 in {
                let fun308 = {
                    let fun311 = e.get("build_elbows")?;
                    let mut args309 = Vec::new();
                    let mut kw310 = Vec::new();
                    fun311.call(args309, kw310)?
                }
                .attr("items")?;
                let mut args306 = Vec::new();
                let mut kw307 = Vec::new();
                fun308.call(args306, kw307)?
            }
            .iter()?
            {
                let unpack312 = unpack(item303, 2)?;
                e.set("name", unpack312[0].clone())?;
                let unpack313 = unpack(unpack312[1].clone(), 2)?;
                e.set("solid", unpack313[0].clone())?;
                e.set("_mouth", unpack313[1].clone())?;
                let assigned304 = e.get("solid")?;
                e.get("out")?.set(
                    {
                        let mut str305 = String::new();
                        str305.push_str("carbonator-elbow-");
                        str305.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str305)
                    },
                    assigned304.clone(),
                )?;
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // mouths
    e.set("mouths", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out314 = Val::dict(vec![]);
                for item315 in {
                    let fun318 = {
                        let fun321 = e.get("build_elbows")?;
                        let mut args319 = Vec::new();
                        let mut kw320 = Vec::new();
                        fun321.call(args319, kw320)?
                    }
                    .attr("items")?;
                    let mut args316 = Vec::new();
                    let mut kw317 = Vec::new();
                    fun318.call(args316, kw317)?
                }
                .iter()?
                {
                    let unpack322 = unpack(item315, 2)?;
                    e.set("name", unpack322[0].clone())?;
                    let unpack323 = unpack(unpack322[1].clone(), 2)?;
                    e.set("_solid", unpack323[0].clone())?;
                    e.set("mouth", unpack323[1].clone())?;
                    out314.set(e.get("name")?, e.get("mouth")?)?;
                }
                out314
            });
            Ok(Val::None)
        })
    })?;
    // report
    e.set("report", {
        let params = vec![("port_mouths".into(), Some(Val::None), true)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun326 = e.get("print")?;
                let mut args324 = Vec::new();
                let mut kw325 = Vec::new();
                args324.push(Val::Str("  carbonator".into()));
                fun326.call(args324, kw325)?
            };
            {
                let fun329 = e.get("print")?;
                let mut args327 = Vec::new();
                let mut kw328 = Vec::new();
                args327.push({
                    let mut str330 = String::new();
                    str330.push_str("    tube            ⌀");
                    str330.push_str(&format(
                        &e.get("TUBE_OD")?,
                        &val_string({
                            let mut str331 = String::new();
                            str331.push_str(".1f");
                            Val::Str(str331)
                        })?,
                    )?);
                    str330.push_str(" × ");
                    str330.push_str(&format(
                        &e.get("TUBE_WALL")?,
                        &val_string({
                            let mut str332 = String::new();
                            str332.push_str(".3f");
                            Val::Str(str332)
                        })?,
                    )?);
                    str330.push_str(" wall × ");
                    str330.push_str(&format(
                        &e.get("carbonator_height")?,
                        &val_string({
                            let mut str333 = String::new();
                            str333.push_str(".1f");
                            Val::Str(str333)
                        })?,
                    )?);
                    str330.push_str(", z ");
                    str330.push_str(&format(
                        &e.get("carbonator_bottom_z")?,
                        &val_string({
                            let mut str334 = String::new();
                            str334.push_str(".2f");
                            Val::Str(str334)
                        })?,
                    )?);
                    str330.push_str("..");
                    str330.push_str(&format(
                        &e.get("carbonator_top_z")?,
                        &val_string({
                            let mut str335 = String::new();
                            str335.push_str(".2f");
                            Val::Str(str335)
                        })?,
                    )?);
                    Val::Str(str330)
                });
                fun329.call(args327, kw328)?
            };
            {
                let fun338 = e.get("print")?;
                let mut args336 = Vec::new();
                let mut kw337 = Vec::new();
                args336.push({
                    let mut str339 = String::new();
                    str339.push_str("    plates          ⌀");
                    str339.push_str(&format(
                        &e.get("PLATE_D")?,
                        &val_string({
                            let mut str340 = String::new();
                            str340.push_str(".2f");
                            Val::Str(str340)
                        })?,
                    )?);
                    str339.push_str(" × ");
                    str339.push_str(&format(
                        &e.get("PLATE_T")?,
                        &val_string({
                            let mut str341 = String::new();
                            str341.push_str(".2f");
                            Val::Str(str341)
                        })?,
                    )?);
                    str339.push_str(", bottom z ");
                    str339.push_str(&format(
                        &e.get("bottom_plate_z")?.get(Val::Int(0i64))?,
                        &val_string({
                            let mut str342 = String::new();
                            str342.push_str(".2f");
                            Val::Str(str342)
                        })?,
                    )?);
                    str339.push_str("..");
                    str339.push_str(&format(
                        &e.get("bottom_plate_z")?.get(Val::Int(1i64))?,
                        &val_string({
                            let mut str343 = String::new();
                            str343.push_str(".2f");
                            Val::Str(str343)
                        })?,
                    )?);
                    str339.push_str(", top z ");
                    str339.push_str(&format(
                        &e.get("top_plate_z")?.get(Val::Int(0i64))?,
                        &val_string({
                            let mut str344 = String::new();
                            str344.push_str(".2f");
                            Val::Str(str344)
                        })?,
                    )?);
                    str339.push_str("..");
                    str339.push_str(&format(
                        &e.get("top_plate_z")?.get(Val::Int(1i64))?,
                        &val_string({
                            let mut str345 = String::new();
                            str345.push_str(".2f");
                            Val::Str(str345)
                        })?,
                    )?);
                    Val::Str(str339)
                });
                fun338.call(args336, kw337)?
            };
            let assigned346 = binary("sub", e.get("TUBE_ID")?, e.get("PLATE_D")?)?;
            e.set("slip", assigned346.clone())?;
            {
                let fun349 = e.get("print")?;
                let mut args347 = Vec::new();
                let mut kw348 = Vec::new();
                args347.push({
                    let mut str350 = String::new();
                    str350.push_str("    plate-to-bore   ");
                    str350.push_str(&format(
                        &e.get("slip")?,
                        &val_string({
                            let mut str351 = String::new();
                            str351.push_str(".3f");
                            Val::Str(str351)
                        })?,
                    )?);
                    str350.push_str(" mm slip on ⌀");
                    str350.push_str(&format(
                        &e.get("TUBE_ID")?,
                        &val_string({
                            let mut str352 = String::new();
                            str352.push_str(".3f");
                            Val::Str(str352)
                        })?,
                    )?);
                    str350.push_str(" bore");
                    Val::Str(str350)
                });
                fun349.call(args347, kw348)?
            };
            {
                let fun355 = e.get("print")?;
                let mut args353 = Vec::new();
                let mut kw354 = Vec::new();
                args353.push({
                    let mut str356 = String::new();
                    str356.push_str("    interior        z ");
                    str356.push_str(&format(
                        &e.get("interior_z")?.get(Val::Int(0i64))?,
                        &val_string({
                            let mut str357 = String::new();
                            str357.push_str(".2f");
                            Val::Str(str357)
                        })?,
                    )?);
                    str356.push_str("..");
                    str356.push_str(&format(
                        &e.get("interior_z")?.get(Val::Int(1i64))?,
                        &val_string({
                            let mut str358 = String::new();
                            str358.push_str(".2f");
                            Val::Str(str358)
                        })?,
                    )?);
                    str356.push_str(" (");
                    str356.push_str(&format(
                        &binary(
                            "sub",
                            e.get("interior_z")?.get(Val::Int(1i64))?,
                            e.get("interior_z")?.get(Val::Int(0i64))?,
                        )?,
                        &val_string({
                            let mut str359 = String::new();
                            str359.push_str(".1f");
                            Val::Str(str359)
                        })?,
                    )?);
                    str356.push_str(" mm of column)");
                    Val::Str(str356)
                });
                fun355.call(args353, kw354)?
            };
            {
                let fun362 = e.get("print")?;
                let mut args360 = Vec::new();
                let mut kw361 = Vec::new();
                args360.push({
                    let mut str363 = String::new();
                    str363.push_str("    float rod       ⌀");
                    str363.push_str(&format(
                        &e.get("ROD_D")?,
                        &val_string({
                            let mut str364 = String::new();
                            str364.push_str(".3f");
                            Val::Str(str364)
                        })?,
                    )?);
                    str363.push_str(" × ");
                    str363.push_str(&format(
                        &{
                            let fun367 = e.get("rod_length")?;
                            let mut args365 = Vec::new();
                            let mut kw366 = Vec::new();
                            fun367.call(args365, kw366)?
                        },
                        &val_string({
                            let mut str368 = String::new();
                            str368.push_str(".1f");
                            Val::Str(str368)
                        })?,
                    )?);
                    str363.push_str(" at XY ");
                    str363.push_str(&format(&e.get("ROD_XY")?, &String::new())?);
                    Val::Str(str363)
                });
                fun362.call(args360, kw361)?
            };
            {
                let fun371 = e.get("print")?;
                let mut args369 = Vec::new();
                let mut kw370 = Vec::new();
                args369.push({
                    let mut str372 = String::new();
                    str372.push_str("    upper stop      ⌀");
                    str372.push_str(&format(
                        &e.get("UPPER_STOP_D")?,
                        &val_string({
                            let mut str373 = String::new();
                            str373.push_str("g");
                            Val::Str(str373)
                        })?,
                    )?);
                    str372.push_str(" × ");
                    str372.push_str(&format(
                        &e.get("UPPER_STOP_H")?,
                        &val_string({
                            let mut str374 = String::new();
                            str374.push_str("g");
                            Val::Str(str374)
                        })?,
                    )?);
                    str372.push_str(", bore ");
                    str372.push_str(&format(
                        &e.get("UPPER_STOP_BORE")?,
                        &val_string({
                            let mut str375 = String::new();
                            str375.push_str(".4f");
                            Val::Str(str375)
                        })?,
                    )?);
                    Val::Str(str372)
                });
                fun371.call(args369, kw370)?
            };
            {
                let fun378 = e.get("print")?;
                let mut args376 = Vec::new();
                let mut kw377 = Vec::new();
                args376.push({
                    let mut str379 = String::new();
                    str379.push_str("    elbow standoff  ");
                    str379.push_str(&format(
                        &e.get("ELBOW_AXIS_OFFSET")?,
                        &val_string({
                            let mut str380 = String::new();
                            str380.push_str(".2f");
                            Val::Str(str380)
                        })?,
                    )?);
                    str379.push_str(" off the plate face (shell storeys) vs ");
                    str379.push_str(&format(
                        &e.get("F")?.attr("ELBOW_LEG")?,
                        &val_string({
                            let mut str381 = String::new();
                            str381.push_str(".2f");
                            Val::Str(str381)
                        })?,
                    )?);
                    str379.push_str(" (catalog leg) — Δ");
                    str379.push_str(&format(
                        &binary(
                            "sub",
                            e.get("F")?.attr("ELBOW_LEG")?,
                            e.get("ELBOW_AXIS_OFFSET")?,
                        )?,
                        &val_string({
                            let mut str382 = String::new();
                            str382.push_str("+.2f");
                            Val::Str(str382)
                        })?,
                    )?);
                    Val::Str(str379)
                });
                fun378.call(args376, kw377)?
            };
            {
                let fun385 = e.get("print")?;
                let mut args383 = Vec::new();
                let mut kw384 = Vec::new();
                args383.push({
                    let mut str386 = String::new();
                    str386.push_str("    bottom standoff ");
                    str386.push_str(&format(
                        &e.get("BOTTOM_AXIS_OFFSET")?,
                        &val_string({
                            let mut str387 = String::new();
                            str387.push_str(".2f");
                            Val::Str(str387)
                        })?,
                    )?);
                    str386.push_str(" off the plate face (shell storeys) vs ");
                    str386.push_str(&format(
                        &e.get("BOTTOM_CATALOG_OFFSET")?,
                        &val_string({
                            let mut str388 = String::new();
                            str388.push_str(".2f");
                            Val::Str(str388)
                        })?,
                    )?);
                    str386.push_str(" (catalog reach at the nominal engagement) — Δ");
                    str386.push_str(&format(
                        &binary(
                            "sub",
                            e.get("BOTTOM_CATALOG_OFFSET")?,
                            e.get("BOTTOM_AXIS_OFFSET")?,
                        )?,
                        &val_string({
                            let mut str389 = String::new();
                            str389.push_str("+.2f");
                            Val::Str(str389)
                        })?,
                    )?);
                    Val::Str(str386)
                });
                fun385.call(args383, kw384)?
            };
            for item390 in e.get("PORTS")?.iter()? {
                e.set("name", item390)?;
                let assigned391 = {
                    let fun394 = e.get("port_corner")?;
                    let mut args392 = Vec::new();
                    let mut kw393 = Vec::new();
                    args392.push(e.get("name")?);
                    fun394.call(args392, kw393)?
                };
                e.set("c", assigned391.clone())?;
                let assigned395 = if {
                    let v396 = e.get("port_mouths")?;
                    let v397 = Val::None;
                    Val::Bool(compare("is", v396.clone(), v397.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun400 = e.get("mouths")?;
                        let mut args398 = Vec::new();
                        let mut kw399 = Vec::new();
                        fun400.call(args398, kw399)?
                    }
                    .get(e.get("name")?)?
                    .attr("pos")?
                } else {
                    e.get("port_mouths")?
                        .get(e.get("name")?)?
                        .get(Val::Str("position".into()))?
                };
                e.set("pos", assigned395.clone())?;
                {
                    let fun403 = e.get("print")?;
                    let mut args401 = Vec::new();
                    let mut kw402 = Vec::new();
                    args401.push({
                        let mut str404 = String::new();
                        str404.push_str("    ");
                        str404.push_str(&format(
                            &e.get("name")?,
                            &val_string({
                                let mut str405 = String::new();
                                str405.push_str("15");
                                Val::Str(str405)
                            })?,
                        )?);
                        str404.push_str(" corner (");
                        str404.push_str(&format(
                            &e.get("c")?.get(Val::Int(0i64))?,
                            &val_string({
                                let mut str406 = String::new();
                                str406.push_str("+.1f");
                                Val::Str(str406)
                            })?,
                        )?);
                        str404.push_str(", ");
                        str404.push_str(&format(
                            &e.get("c")?.get(Val::Int(1i64))?,
                            &val_string({
                                let mut str407 = String::new();
                                str407.push_str("+.2f");
                                Val::Str(str407)
                            })?,
                        )?);
                        str404.push_str(", ");
                        str404.push_str(&format(
                            &e.get("c")?.get(Val::Int(2i64))?,
                            &val_string({
                                let mut str408 = String::new();
                                str408.push_str(".2f");
                                Val::Str(str408)
                            })?,
                        )?);
                        str404.push_str(")  mouth (");
                        str404.push_str(&format(
                            &e.get("pos")?.get(Val::Int(0i64))?,
                            &val_string({
                                let mut str409 = String::new();
                                str409.push_str("+.1f");
                                Val::Str(str409)
                            })?,
                        )?);
                        str404.push_str(", ");
                        str404.push_str(&format(
                            &e.get("pos")?.get(Val::Int(1i64))?,
                            &val_string({
                                let mut str410 = String::new();
                                str410.push_str("+.2f");
                                Val::Str(str410)
                            })?,
                        )?);
                        str404.push_str(", ");
                        str404.push_str(&format(
                            &e.get("pos")?.get(Val::Int(2i64))?,
                            &val_string({
                                let mut str411 = String::new();
                                str411.push_str(".2f");
                                Val::Str(str411)
                            })?,
                        )?);
                        str404.push_str(")");
                        Val::Str(str404)
                    });
                    fun403.call(args401, kw402)?
                };
            }
            for item412 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("front_face_port_z")?);
                    s.push(Val::Str("co2-in".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("carbonator_top_plate_z")?,
                        e.get("hole_shift_from_edge")?,
                    )?);
                    s.push(Val::Str("water-in".into()));
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack430 = unpack(item412, 2)?;
                e.set("band", unpack430[0].clone())?;
                e.set("name", unpack430[1].clone())?;
                let assigned413 = {
                    let fun416 = e.get("port_corner")?;
                    let mut args414 = Vec::new();
                    let mut kw415 = Vec::new();
                    args414.push(e.get("name")?);
                    fun416.call(args414, kw415)?
                }
                .get(Val::Int(2i64))?;
                e.set("got", assigned413.clone())?;
                {
                    let fun419 = e.get("print")?;
                    let mut args417 = Vec::new();
                    let mut kw418 = Vec::new();
                    args417.push({
                        let mut str420 = String::new();
                        str420.push_str("    band ");
                        str420.push_str(&format(
                            &e.get("band")?,
                            &val_string({
                                let mut str421 = String::new();
                                str421.push_str("7.2f");
                                Val::Str(str421)
                            })?,
                        )?);
                        str420.push_str("    ");
                        str420.push_str(&format(&e.get("name")?, &String::new())?);
                        str420.push_str(" corner at ");
                        str420.push_str(&format(
                            &e.get("got")?,
                            &val_string({
                                let mut str422 = String::new();
                                str422.push_str(".2f");
                                Val::Str(str422)
                            })?,
                        )?);
                        str420.push_str(" — ");
                        str420.push_str(&format(
                            &if {
                                let v426 = {
                                    let fun425 = e.get("abs")?;
                                    let mut args423 = Vec::new();
                                    let mut kw424 = Vec::new();
                                    args423.push(binary("sub", e.get("band")?, e.get("got")?)?);
                                    fun425.call(args423, kw424)?
                                };
                                let v427 = Val::Float(1e-06f64);
                                Val::Bool(compare("lt", v426.clone(), v427.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                Val::Str("on it".into())
                            } else {
                                {
                                    let mut str428 = String::new();
                                    str428.push_str("OFF by ");
                                    str428.push_str(&format(
                                        &binary("sub", e.get("got")?, e.get("band")?)?,
                                        &val_string({
                                            let mut str429 = String::new();
                                            str429.push_str("+.3f");
                                            Val::Str(str429)
                                        })?,
                                    )?);
                                    Val::Str(str428)
                                }
                            },
                            &String::new(),
                        )?);
                        Val::Str(str420)
                    });
                    fun419.call(args417, kw418)?
                };
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun433 = e.get("report")?;
        let mut args431 = Vec::new();
        let mut kw432 = Vec::new();
        fun433.call(args431, kw432)?
    };
    Ok(Val::None)
}
