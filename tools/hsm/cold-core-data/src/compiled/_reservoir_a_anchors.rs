#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("copy")?;
    e.set("deepcopy", rt.member("copy", "deepcopy")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("snap", rt.import_module("_reservoir_a_c2")?)?;
    let assigned2 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("units".into()), Val::Str("mm".into()))?;
        d.set(
            Val::Str("assembly_owner".into()),
            Val::Str("back-bottom".into()),
        )?;
        d.set(
            Val::Str("mounting_parent".into()),
            Val::Str("cold-core top lid".into()),
        )?;
        d.set(Val::Str("tube_od_mm".into()), Val::Float(6.35f64))?;
        d.set(Val::Str("tube_axis_world".into()), {
            let mut s = Vec::new();
            s.push(Val::Float(0.0f64));
            s.push(Val::Float(1.0f64));
            s.push(Val::Float(0.0f64));
            Val::list(s)
        })?;
        d.set(Val::Str("lid_face_z_mm".into()), Val::Float(253.4f64))?;
        d.set(Val::Str("root_z_mm".into()), Val::Float(248.0f64))?;
        d.set(Val::Str("seat_top_z_mm".into()), Val::Float(257.0f64))?;
        d.set(Val::Str("seat_radius_mm".into()), Val::Float(3.325f64))?;
        d.set(Val::Str("seat_floor_stock_mm".into()), Val::Float(3.0f64))?;
        d.set(Val::Str("station_length_mm".into()), Val::Float(10.0f64))?;
        d.set(
            Val::Str("stock_west_of_first_tube_mm".into()),
            Val::Float(6.325f64),
        )?;
        d.set(
            Val::Str("stock_east_of_last_tube_mm".into()),
            Val::Float(6.325f64),
        )?;
        d.set(Val::Str("tie_slot_width_y_mm".into()), Val::Float(3.2f64))?;
        d.set(
            Val::Str("tie_slot_bottom_z_mm".into()),
            Val::Float(251.6f64),
        )?;
        d.set(
            Val::Str("tie_slot_floor_stock_mm".into()),
            Val::Float(3.0f64),
        )?;
        d.set(
            Val::Str("tie_access_inner_offset_mm".into()),
            Val::Float(0.0f64),
        )?;
        d.set(Val::Str("tie_witness_width_mm".into()), Val::Float(2.5f64))?;
        d.set(
            Val::Str("tie_witness_thickness_mm".into()),
            Val::Float(0.8f64),
        )?;
        d.set(
            Val::Str("tie_witness_outer_bend_radius_mm".into()),
            Val::Float(3.75f64),
        )?;
        d.set(
            Val::Str("tie_witness_bottom_center_z_mm".into()),
            Val::Float(252.4f64),
        )?;
        d.set(Val::Str("stations".into()), {
            let mut s = Vec::new();
            s.push({
                let d = Val::dict(vec![]);
                d.set(Val::Str("id".into()), Val::Str("a-pair-fore-anchor".into()))?;
                d.set(
                    Val::Str("label".into()),
                    Val::Str("Reservoir A fore paired anchor".into()),
                )?;
                d.set(Val::Str("routes_west_to_east".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Str("fluid-16".into()));
                    s.push(Val::Str("fluid-14".into()));
                    Val::list(s)
                })?;
                d
            });
            s.push({
                let d = Val::dict(vec![]);
                d.set(Val::Str("id".into()), Val::Str("a-pair-aft-anchor".into()))?;
                d.set(
                    Val::Str("label".into()),
                    Val::Str("Reservoir A aft paired anchor".into()),
                )?;
                d.set(Val::Str("world_y_mm".into()), Val::Float(390.5f64))?;
                d.set(Val::Str("station_length_mm".into()), Val::Float(9.2f64))?;
                d.set(Val::Str("curved_seats".into()), Val::Bool(true))?;
                d.set(
                    Val::Str("seat_lip_below_axis_mm".into()),
                    Val::Float(1.2f64),
                )?;
                d.set(Val::Str("routes_west_to_east".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Str("fluid-16".into()));
                    s.push(Val::Str("fluid-14".into()));
                    Val::list(s)
                })?;
                d
            });
            Val::list(s)
        })?;
        d
    };
    e.set("_SPECIFICATION", assigned2.clone())?;
    // specification
    e.set("specification", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned3 = {
                let fun6 = e.get("deepcopy")?;
                let mut args4 = Vec::new();
                let mut kw5 = Vec::new();
                args4.push(e.get("_SPECIFICATION")?);
                fun6.call(args4, kw5)?
            };
            e.set("result", assigned3.clone())?;
            let assigned7 = e
                .get("result")?
                .get(Val::Str("stations".into()))?
                .get(Val::Int(0i64))?;
            e.set("fore", assigned7.clone())?;
            {
                let fun10 = e.get("fore")?.attr("update")?;
                let mut args8 = Vec::new();
                let mut kw9 = Vec::new();
                args8.push({
                    let fun13 = e.get("snap")?.attr("specification")?;
                    let mut args11 = Vec::new();
                    let mut kw12 = Vec::new();
                    fun13.call(args11, kw12)?
                });
                fun10.call(args8, kw9)?
            };
            let assigned14 = e
                .get("result")?
                .get(Val::Str("stations".into()))?
                .get(Val::Int(1i64))?;
            e.set("aft", assigned14.clone())?;
            let assigned15 = Val::Str("tie".into());
            e.get("aft")?
                .set(Val::Str("closure".into()), assigned15.clone())?;
            let assigned16 = {
                let e = e.child();
                let out17 = Val::list(vec![]);
                for item18 in e
                    .get("aft")?
                    .get(Val::Str("routes_west_to_east".into()))?
                    .iter()?
                {
                    e.set("route", item18)?;
                    out17.attr("append")?.call(
                        vec![
                            {
                                let fun21 = e.get("_route_station")?;
                                let mut args19 = Vec::new();
                                let mut kw20 = Vec::new();
                                args19.push(e.get("route")?);
                                args19.push(e.get("aft")?.get(Val::Str("world_y_mm".into()))?);
                                fun21.call(args19, kw20)?
                            }
                            .get(Val::Int(0i64))?,
                        ],
                        vec![],
                    )?;
                }
                out17
            };
            e.get("aft")?
                .set(Val::Str("tube_centers_world_mm".into()), assigned16.clone())?;
            let assigned22 = binary(
                "sub",
                binary(
                    "sub",
                    {
                        let fun25 = e.get("min")?;
                        let mut args23 = Vec::new();
                        let mut kw24 = Vec::new();
                        args23.push({
                            let e = e.child();
                            let out26 = Val::list(vec![]);
                            for item27 in
                                e.get("result")?.get(Val::Str("stations".into()))?.iter()?
                            {
                                e.set("row", item27)?;
                                if {
                                    let v28 = e.get("row")?.get(Val::Str("closure".into()))?;
                                    let v29 = Val::Str("tie".into());
                                    Val::Bool(compare("eq", v28.clone(), v29.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    for item30 in e
                                        .get("row")?
                                        .get(Val::Str("tube_centers_world_mm".into()))?
                                        .iter()?
                                    {
                                        e.set("point", item30)?;
                                        out26.attr("append")?.call(
                                            vec![e.get("point")?.get(Val::Int(2i64))?],
                                            vec![],
                                        )?;
                                    }
                                }
                            }
                            out26
                        });
                        fun25.call(args23, kw24)?
                    },
                    e.get("result")?.get(Val::Str("seat_radius_mm".into()))?,
                )?,
                e.get("result")?
                    .get(Val::Str("seat_floor_stock_mm".into()))?,
            )?;
            e.get("result")?
                .set(Val::Str("tie_slot_top_z_mm".into()), assigned22.clone())?;
            let assigned31 = {
                let fun34 = e.get("max")?;
                let mut args32 = Vec::new();
                let mut kw33 = Vec::new();
                args32.push(
                    e.get("result")?
                        .get(Val::Str("stock_west_of_first_tube_mm".into()))?,
                );
                args32.push(
                    e.get("result")?
                        .get(Val::Str("stock_east_of_last_tube_mm".into()))?,
                );
                fun34.call(args32, kw33)?
            };
            e.get("result")?.set(
                Val::Str("tie_access_outer_offset_mm".into()),
                assigned31.clone(),
            )?;
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // datums
    e.set("datums", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned35 = {
                let fun38 = e.get("specification")?;
                let mut args36 = Vec::new();
                let mut kw37 = Vec::new();
                fun38.call(args36, kw37)?
            };
            e.set("spec", assigned35.clone())?;
            let assigned39 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("result", assigned39.clone())?;
            for item40 in e.get("spec")?.get(Val::Str("stations".into()))?.iter()? {
                e.set("station", item40)?;
                let assigned41 = e
                    .get("station")?
                    .get(Val::Str("tube_centers_world_mm".into()))?;
                let unpack42 = unpack(assigned41.clone(), 2)?;
                e.set("first", unpack42[0].clone())?;
                e.set("last", unpack42[1].clone())?;
                let assigned43 = {
                    let mut s = Vec::new();
                    s.push(e.get("first")?.get(Val::Int(0i64))?);
                    s.push(e.get("last")?.get(Val::Int(0i64))?);
                    Val::tuple(s)
                };
                let unpack44 = unpack(assigned43.clone(), 2)?;
                e.set("x0", unpack44[0].clone())?;
                e.set("x1", unpack44[1].clone())?;
                let assigned45 = e.get("first")?.get(Val::Int(1i64))?;
                e.set("y", assigned45.clone())?;
                let assigned46 = binary(
                    "truediv",
                    {
                        let fun49 = e.get("station")?.attr("get")?;
                        let mut args47 = Vec::new();
                        let mut kw48 = Vec::new();
                        args47.push(Val::Str("station_length_mm".into()));
                        args47.push(e.get("spec")?.get(Val::Str("station_length_mm".into()))?);
                        fun49.call(args47, kw48)?
                    },
                    Val::Int(2i64),
                )?;
                e.set("half", assigned46.clone())?;
                if {
                    let v50 = e.get("station")?.get(Val::Str("closure".into()))?;
                    let v51 = Val::Str("direct-snap".into());
                    Val::Bool(compare("eq", v50.clone(), v51.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned52 = {
                        let d = Val::dict(vec![]);
                        dict_extend(&d, e.get("station")?)?;
                        d.set(
                            Val::Str("stock_bounds_mm".into()),
                            e.get("station")?.get(Val::Str("body_bounds_mm".into()))?,
                        )?;
                        d.set(
                            Val::Str("tube_axes_world".into()),
                            binary(
                                "mul",
                                {
                                    let mut s = Vec::new();
                                    s.push(
                                        e.get("station")?
                                            .get(Val::Str("tube_axis_world".into()))?,
                                    );
                                    Val::list(s)
                                },
                                Val::Int(2i64),
                            )?,
                        )?;
                        d
                    };
                    e.get("result")?.set(
                        e.get("station")?.get(Val::Str("id".into()))?,
                        assigned52.clone(),
                    )?;
                    continue;
                }
                let assigned53 = {
                    let fun56 = e.get("station")?.attr("get")?;
                    let mut args54 = Vec::new();
                    let mut kw55 = Vec::new();
                    args54.push(Val::Str("seat_top_z_mm".into()));
                    args54.push(e.get("spec")?.get(Val::Str("seat_top_z_mm".into()))?);
                    fun56.call(args54, kw55)?
                };
                e.set("top", assigned53.clone())?;
                let assigned57 = binary(
                    "truediv",
                    e.get("spec")?.get(Val::Str("tie_slot_width_y_mm".into()))?,
                    Val::Int(2i64),
                )?;
                e.set("slot_half", assigned57.clone())?;
                let assigned58 = e
                    .get("spec")?
                    .get(Val::Str("tie_access_inner_offset_mm".into()))?;
                e.set("inner", assigned58.clone())?;
                let assigned59 = {
                    let fun62 = e.get("station")?.attr("get")?;
                    let mut args60 = Vec::new();
                    let mut kw61 = Vec::new();
                    args60.push(Val::Str("base_east_of_last_tube_mm".into()));
                    args60.push(
                        e.get("spec")?
                            .get(Val::Str("stock_east_of_last_tube_mm".into()))?,
                    );
                    fun62.call(args60, kw61)?
                };
                e.set("east", assigned59.clone())?;
                let assigned63 = binary(
                    "sub",
                    e.get("x0")?,
                    e.get("spec")?
                        .get(Val::Str("stock_west_of_first_tube_mm".into()))?,
                )?;
                e.set("west_edge", assigned63.clone())?;
                let assigned64 = binary("add", e.get("x1")?, e.get("east")?)?;
                e.set("east_edge", assigned64.clone())?;
                let assigned65 = {
                    let d = Val::dict(vec![]);
                    dict_extend(&d, e.get("station")?)?;
                    d.set(Val::Str("stock_bounds_mm".into()), {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("west_edge")?);
                            s.push(binary("sub", e.get("y")?, e.get("half")?)?);
                            s.push(e.get("spec")?.get(Val::Str("root_z_mm".into()))?);
                            Val::list(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("east_edge")?);
                            s.push(binary("add", e.get("y")?, e.get("half")?)?);
                            s.push(e.get("top")?);
                            Val::list(s)
                        });
                        Val::list(s)
                    })?;
                    d.set(Val::Str("tie_slot_bounds_mm".into()), {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("west_edge")?);
                            s.push(binary("sub", e.get("y")?, e.get("slot_half")?)?);
                            s.push(
                                e.get("spec")?
                                    .get(Val::Str("tie_slot_bottom_z_mm".into()))?,
                            );
                            Val::list(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("east_edge")?);
                            s.push(binary("add", e.get("y")?, e.get("slot_half")?)?);
                            s.push(e.get("spec")?.get(Val::Str("tie_slot_top_z_mm".into()))?);
                            Val::list(s)
                        });
                        Val::list(s)
                    })?;
                    d.set(Val::Str("access_bounds_mm".into()), {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("west_edge")?);
                                s.push(binary("sub", e.get("y")?, e.get("slot_half")?)?);
                                s.push(
                                    e.get("spec")?
                                        .get(Val::Str("tie_slot_bottom_z_mm".into()))?,
                                );
                                Val::list(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("sub", e.get("x0")?, e.get("inner")?)?);
                                s.push(binary("add", e.get("y")?, e.get("slot_half")?)?);
                                s.push(binary("add", e.get("top")?, Val::Float(0.1f64))?);
                                Val::list(s)
                            });
                            Val::list(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("add", e.get("x1")?, e.get("inner")?)?);
                                s.push(binary("sub", e.get("y")?, e.get("slot_half")?)?);
                                s.push(
                                    e.get("spec")?
                                        .get(Val::Str("tie_slot_bottom_z_mm".into()))?,
                                );
                                Val::list(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("east_edge")?);
                                s.push(binary("add", e.get("y")?, e.get("slot_half")?)?);
                                s.push(binary("add", e.get("top")?, Val::Float(0.1f64))?);
                                Val::list(s)
                            });
                            Val::list(s)
                        });
                        Val::list(s)
                    })?;
                    d
                };
                e.get("result")?.set(
                    e.get("station")?.get(Val::Str("id".into()))?,
                    assigned65.clone(),
                )?;
                if {
                    let v69 = {
                        let fun68 = e.get("station")?.attr("get")?;
                        let mut args66 = Vec::new();
                        let mut kw67 = Vec::new();
                        args66.push(Val::Str("open_quarter_side".into()));
                        fun68.call(args66, kw67)?
                    };
                    let v70 = Val::Str("east".into());
                    Val::Bool(compare("eq", v69.clone(), v70.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned71 = {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("x1")?);
                            s.push(binary("sub", e.get("y")?, e.get("half")?)?);
                            s.push(e.get("spec")?.get(Val::Str("tie_slot_top_z_mm".into()))?);
                            Val::list(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "add",
                                binary("add", e.get("x1")?, e.get("east")?)?,
                                Val::Float(0.1f64),
                            )?);
                            s.push(binary("add", e.get("y")?, e.get("half")?)?);
                            s.push(binary("add", e.get("top")?, Val::Float(0.1f64))?);
                            Val::list(s)
                        });
                        Val::list(s)
                    };
                    e.get("result")?
                        .get(e.get("station")?.get(Val::Str("id".into()))?)?
                        .set(
                            Val::Str("open_quarter_bounds_mm".into()),
                            assigned71.clone(),
                        )?;
                }
                if {
                    let v72 = Val::Str("west_ramp_top_west_of_first_tube_mm".into());
                    let v73 = e.get("station")?;
                    Val::Bool(compare("in", v72.clone(), v73.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned74 = {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("west_edge")?);
                            s.push(e.get("spec")?.get(Val::Str("lid_face_z_mm".into()))?);
                            Val::list(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "sub",
                                e.get("x0")?,
                                e.get("station")?
                                    .get(Val::Str("west_ramp_top_west_of_first_tube_mm".into()))?,
                            )?);
                            s.push(e.get("top")?);
                            Val::list(s)
                        });
                        Val::list(s)
                    };
                    e.get("result")?
                        .get(e.get("station")?.get(Val::Str("id".into()))?)?
                        .set(Val::Str("west_ramp_xz_mm".into()), assigned74.clone())?;
                }
                if {
                    let fun77 = e.get("station")?.attr("get")?;
                    let mut args75 = Vec::new();
                    let mut kw76 = Vec::new();
                    args75.push(Val::Str("curved_seats".into()));
                    fun77.call(args75, kw76)?
                }
                .truthy()?
                {
                    let assigned78 = {
                        let e = e.child();
                        let out79 = Val::list(vec![]);
                        for item80 in e
                            .get("station")?
                            .get(Val::Str("routes_west_to_east".into()))?
                            .iter()?
                        {
                            e.set("route", item80)?;
                            out79.attr("append")?.call(
                                vec![{
                                    let fun83 = e.get("_route_station")?;
                                    let mut args81 = Vec::new();
                                    let mut kw82 = Vec::new();
                                    args81.push(e.get("route")?);
                                    args81.push(e.get("y")?);
                                    fun83.call(args81, kw82)?
                                }],
                                vec![],
                            )?;
                        }
                        out79
                    };
                    e.set("held", assigned78.clone())?;
                    let assigned84 = e
                        .get("result")?
                        .get(e.get("station")?.get(Val::Str("id".into()))?)?;
                    e.set("row", assigned84.clone())?;
                    {
                        let fun87 = e.get("row")?.attr("update")?;
                        let mut args85 = Vec::new();
                        let mut kw86 = Vec::new();
                        kw86.push((
                            "nominal_tube_centers_world_mm".into(),
                            e.get("station")?
                                .get(Val::Str("tube_centers_world_mm".into()))?,
                        ));
                        kw86.push(("tube_centers_world_mm".into(), {
                            let e = e.child();
                            let out88 = Val::list(vec![]);
                            for item89 in e.get("held")?.iter()? {
                                let unpack90 = unpack(item89, 2)?;
                                e.set("p", unpack90[0].clone())?;
                                e.set("_axis", unpack90[1].clone())?;
                                out88.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                            out88
                        }));
                        kw86.push(("tube_axes_world".into(), {
                            let e = e.child();
                            let out91 = Val::list(vec![]);
                            for item92 in e.get("held")?.iter()? {
                                let unpack93 = unpack(item92, 2)?;
                                e.set("_p", unpack93[0].clone())?;
                                e.set("axis", unpack93[1].clone())?;
                                out91.attr("append")?.call(vec![e.get("axis")?], vec![])?;
                            }
                            out91
                        }));
                        fun87.call(args85, kw86)?
                    };
                    let assigned94 = {
                        let e = e.child();
                        let out95 = Val::list(vec![]);
                        for item96 in e
                            .get("station")?
                            .get(Val::Str("routes_west_to_east".into()))?
                            .iter()?
                        {
                            e.set("route", item96)?;
                            out95.attr("append")?.call(
                                vec![{
                                    let e = e.child();
                                    let out97 = Val::list(vec![]);
                                    for item98 in {
                                        let fun101 = e.get("range")?;
                                        let mut args99 = Vec::new();
                                        let mut kw100 = Vec::new();
                                        args99.push(Val::Int(65i64));
                                        fun101.call(args99, kw100)?
                                    }
                                    .iter()?
                                    {
                                        e.set("i", item98)?;
                                        out97.attr("append")?.call(
                                            vec![{
                                                let fun104 = e.get("_route_station")?;
                                                let mut args102 = Vec::new();
                                                let mut kw103 = Vec::new();
                                                args102.push(e.get("route")?);
                                                args102.push(binary(
                                                    "add",
                                                    binary("sub", e.get("y")?, e.get("half")?)?,
                                                    binary(
                                                        "truediv",
                                                        binary(
                                                            "mul",
                                                            binary(
                                                                "mul",
                                                                e.get("i")?,
                                                                Val::Int(2i64),
                                                            )?,
                                                            e.get("half")?,
                                                        )?,
                                                        Val::Int(64i64),
                                                    )?,
                                                )?);
                                                fun104.call(args102, kw103)?
                                            }],
                                            vec![],
                                        )?;
                                    }
                                    out97
                                }],
                                vec![],
                            )?;
                        }
                        out95
                    };
                    e.set("lanes", assigned94.clone())?;
                    let assigned105 = {
                        let e = e.child();
                        let out106 = Val::list(vec![]);
                        for item107 in e.get("lanes")?.iter()? {
                            e.set("lane", item107)?;
                            out106.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push({
                                        let fun110 = e.get("min")?;
                                        let mut args108 = Vec::new();
                                        let mut kw109 = Vec::new();
                                        args108.push({
                                            let e = e.child();
                                            let out111 = Val::list(vec![]);
                                            for item112 in e.get("lane")?.iter()? {
                                                let unpack113 = unpack(item112, 2)?;
                                                e.set("p", unpack113[0].clone())?;
                                                e.set("u", unpack113[1].clone())?;
                                                out111.attr("append")?.call(
                                                    vec![binary(
                                                        "sub",
                                                        e.get("p")?.get(Val::Int(0i64))?,
                                                        binary(
                                                            "truediv",
                                                            e.get("spec")?.get(Val::Str(
                                                                "seat_radius_mm".into(),
                                                            ))?,
                                                            {
                                                                let fun116 = e.get("abs")?;
                                                                let mut args114 = Vec::new();
                                                                let mut kw115 = Vec::new();
                                                                args114.push(
                                                                    e.get("u")?
                                                                        .get(Val::Int(1i64))?,
                                                                );
                                                                fun116.call(args114, kw115)?
                                                            },
                                                        )?,
                                                    )?],
                                                    vec![],
                                                )?;
                                            }
                                            out111
                                        });
                                        fun110.call(args108, kw109)?
                                    });
                                    s.push({
                                        let fun119 = e.get("max")?;
                                        let mut args117 = Vec::new();
                                        let mut kw118 = Vec::new();
                                        args117.push({
                                            let e = e.child();
                                            let out120 = Val::list(vec![]);
                                            for item121 in e.get("lane")?.iter()? {
                                                let unpack122 = unpack(item121, 2)?;
                                                e.set("p", unpack122[0].clone())?;
                                                e.set("u", unpack122[1].clone())?;
                                                out120.attr("append")?.call(
                                                    vec![binary(
                                                        "add",
                                                        e.get("p")?.get(Val::Int(0i64))?,
                                                        binary(
                                                            "truediv",
                                                            e.get("spec")?.get(Val::Str(
                                                                "seat_radius_mm".into(),
                                                            ))?,
                                                            {
                                                                let fun125 = e.get("abs")?;
                                                                let mut args123 = Vec::new();
                                                                let mut kw124 = Vec::new();
                                                                args123.push(
                                                                    e.get("u")?
                                                                        .get(Val::Int(1i64))?,
                                                                );
                                                                fun125.call(args123, kw124)?
                                                            },
                                                        )?,
                                                    )?],
                                                    vec![],
                                                )?;
                                            }
                                            out120
                                        });
                                        fun119.call(args117, kw118)?
                                    });
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                        out106
                    };
                    e.set("edges", assigned105.clone())?;
                    let assigned126 = {
                        let e = e.child();
                        let out127 = Val::list(vec![]);
                        for item128 in e.get("lanes")?.iter()? {
                            e.set("lane", item128)?;
                            out127.attr("append")?.call(
                                vec![binary(
                                    "sub",
                                    {
                                        let fun131 = e.get("min")?;
                                        let mut args129 = Vec::new();
                                        let mut kw130 = Vec::new();
                                        args129.push({
                                            let e = e.child();
                                            let out132 = Val::list(vec![]);
                                            for item133 in e.get("lane")?.iter()? {
                                                let unpack134 = unpack(item133, 2)?;
                                                e.set("p", unpack134[0].clone())?;
                                                e.set("_u", unpack134[1].clone())?;
                                                out132.attr("append")?.call(
                                                    vec![e.get("p")?.get(Val::Int(2i64))?],
                                                    vec![],
                                                )?;
                                            }
                                            out132
                                        });
                                        fun131.call(args129, kw130)?
                                    },
                                    e.get("station")?
                                        .get(Val::Str("seat_lip_below_axis_mm".into()))?,
                                )?],
                                vec![],
                            )?;
                        }
                        out127
                    };
                    e.set("tops", assigned126.clone())?;
                    let assigned135 = {
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("edges")?.get(Val::Int(0i64))?.get(Val::Int(0i64))?,
                            Val::Float(3.0f64),
                        )?);
                        s.push(binary(
                            "add",
                            e.get("edges")?
                                .get(unary("neg", Val::Int(1i64))?)?
                                .get(Val::Int(1i64))?,
                            Val::Float(3.0f64),
                        )?);
                        Val::tuple(s)
                    };
                    let unpack136 = unpack(assigned135.clone(), 2)?;
                    e.set("west_edge", unpack136[0].clone())?;
                    e.set("east_edge", unpack136[1].clone())?;
                    let assigned137 = {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("west_edge")?);
                            s.push(binary("sub", e.get("y")?, e.get("half")?)?);
                            s.push(e.get("spec")?.get(Val::Str("root_z_mm".into()))?);
                            Val::list(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("east_edge")?);
                            s.push(binary("add", e.get("y")?, e.get("half")?)?);
                            s.push({
                                let fun140 = e.get("max")?;
                                let mut args138 = Vec::new();
                                let mut kw139 = Vec::new();
                                args138.push(e.get("tops")?);
                                fun140.call(args138, kw139)?
                            });
                            Val::list(s)
                        });
                        Val::list(s)
                    };
                    e.get("row")?
                        .set(Val::Str("stock_bounds_mm".into()), assigned137.clone())?;
                    let assigned141 = e.get("spec")?.get(Val::Str("seat_floor_stock_mm".into()))?;
                    e.set("reach", assigned141.clone())?;
                    let assigned142 = {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("west_edge")?);
                            s.push(e.get("tops")?.get(Val::Int(0i64))?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "sub",
                                e.get("edges")?.get(Val::Int(0i64))?.get(Val::Int(1i64))?,
                                e.get("reach")?,
                            )?);
                            s.push(e.get("tops")?.get(Val::Int(0i64))?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "add",
                                e.get("edges")?
                                    .get(unary("neg", Val::Int(1i64))?)?
                                    .get(Val::Int(0i64))?,
                                e.get("reach")?,
                            )?);
                            s.push(e.get("tops")?.get(unary("neg", Val::Int(1i64))?)?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("east_edge")?);
                            s.push(e.get("tops")?.get(unary("neg", Val::Int(1i64))?)?);
                            Val::tuple(s)
                        });
                        Val::list(s)
                    };
                    e.get("row")?
                        .set(Val::Str("seat_roof_xz_mm".into()), assigned142.clone())?;
                    let assigned143 = e.get("west_edge")?;
                    e.get("row")?
                        .get(Val::Str("tie_slot_bounds_mm".into()))?
                        .get(Val::Int(0i64))?
                        .set(Val::Int(0i64), assigned143.clone())?;
                    let assigned144 = e.get("east_edge")?;
                    e.get("row")?
                        .get(Val::Str("tie_slot_bounds_mm".into()))?
                        .get(Val::Int(1i64))?
                        .set(Val::Int(0i64), assigned144.clone())?;
                    for item145 in {
                        let fun153 = e.get("zip")?;
                        let mut args151 = Vec::new();
                        let mut kw152 = Vec::new();
                        args151.push(e.get("row")?.get(Val::Str("access_bounds_mm".into()))?);
                        args151.push({
                            let mut s = Vec::new();
                            s.push(e.get("west_edge")?);
                            s.push(e.get("x1")?);
                            Val::tuple(s)
                        });
                        args151.push({
                            let mut s = Vec::new();
                            s.push(e.get("x0")?);
                            s.push(e.get("east_edge")?);
                            Val::tuple(s)
                        });
                        fun153.call(args151, kw152)?
                    }
                    .iter()?
                    {
                        let unpack154 = unpack(item145, 3)?;
                        e.set("mouth", unpack154[0].clone())?;
                        e.set("xa", unpack154[1].clone())?;
                        e.set("xb", unpack154[2].clone())?;
                        let assigned146 = {
                            let mut s = Vec::new();
                            s.push(e.get("xa")?);
                            s.push(e.get("xb")?);
                            s.push(binary(
                                "add",
                                {
                                    let fun149 = e.get("max")?;
                                    let mut args147 = Vec::new();
                                    let mut kw148 = Vec::new();
                                    args147.push(e.get("tops")?);
                                    fun149.call(args147, kw148)?
                                },
                                Val::Float(0.1f64),
                            )?);
                            Val::tuple(s)
                        };
                        let unpack150 = unpack(assigned146.clone(), 3)?;
                        e.get("mouth")?
                            .get(Val::Int(0i64))?
                            .set(Val::Int(0i64), unpack150[0].clone())?;
                        e.get("mouth")?
                            .get(Val::Int(1i64))?
                            .set(Val::Int(0i64), unpack150[1].clone())?;
                        e.get("mouth")?
                            .get(Val::Int(1i64))?
                            .set(Val::Int(2i64), unpack150[2].clone())?;
                    }
                }
            }
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // _route_station
    e.set("_route_station", {
        let params = vec![
            ("identifier".into(), None, false),
            ("y".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("routes", rt.import_module("above_core_routes")?)?;
            for item155 in {
                let fun252 = e.get("routes")?.attr("reservoir_a_route_specs")?;
                let mut args250 = Vec::new();
                let mut kw251 = Vec::new();
                fun252.call(args250, kw251)?
            }
            .get(e.get("identifier")?)?
            .get(Val::Str("segments".into()))?
            .iter()?
            {
                e.set("segment", item155)?;
                let assigned156 = {
                    let mut s = Vec::new();
                    s.push(
                        e.get("segment")?
                            .get(Val::Str("points_mm".into()))?
                            .get(Val::Int(0i64))?,
                    );
                    s.push(
                        e.get("segment")?
                            .get(Val::Str("points_mm".into()))?
                            .get(unary("neg", Val::Int(1i64))?)?,
                    );
                    Val::tuple(s)
                };
                let unpack157 = unpack(assigned156.clone(), 2)?;
                e.set("first", unpack157[0].clone())?;
                e.set("last", unpack157[1].clone())?;
                if unary("not", {
                    let v164 = binary(
                        "sub",
                        {
                            let fun160 = e.get("min")?;
                            let mut args158 = Vec::new();
                            let mut kw159 = Vec::new();
                            args158.push(e.get("first")?.get(Val::Int(1i64))?);
                            args158.push(e.get("last")?.get(Val::Int(1i64))?);
                            fun160.call(args158, kw159)?
                        },
                        Val::Float(1e-08f64),
                    )?;
                    let v165 = e.get("y")?;
                    let v166 = binary(
                        "add",
                        {
                            let fun163 = e.get("max")?;
                            let mut args161 = Vec::new();
                            let mut kw162 = Vec::new();
                            args161.push(e.get("first")?.get(Val::Int(1i64))?);
                            args161.push(e.get("last")?.get(Val::Int(1i64))?);
                            fun163.call(args161, kw162)?
                        },
                        Val::Float(1e-08f64),
                    )?;
                    Val::Bool(
                        compare("le", v164.clone(), v165.clone())?.truthy()?
                            && compare("le", v165.clone(), v166.clone())?.truthy()?,
                    )
                })?
                .truthy()?
                {
                    continue;
                }
                if {
                    let v167 = e.get("segment")?.get(Val::Str("kind".into()))?;
                    let v168 = Val::Str("line".into());
                    Val::Bool(compare("eq", v167.clone(), v168.clone())?.truthy()?)
                }
                .truthy()?
                {
                    if {
                        let v172 = {
                            let fun171 = e.get("abs")?;
                            let mut args169 = Vec::new();
                            let mut kw170 = Vec::new();
                            args169.push(binary(
                                "sub",
                                e.get("last")?.get(Val::Int(1i64))?,
                                e.get("first")?.get(Val::Int(1i64))?,
                            )?);
                            fun171.call(args169, kw170)?
                        };
                        let v173 = Val::Float(1e-09f64);
                        Val::Bool(compare("lt", v172.clone(), v173.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        continue;
                    }
                    let assigned174 = binary(
                        "truediv",
                        binary("sub", e.get("y")?, e.get("first")?.get(Val::Int(1i64))?)?,
                        binary(
                            "sub",
                            e.get("last")?.get(Val::Int(1i64))?,
                            e.get("first")?.get(Val::Int(1i64))?,
                        )?,
                    )?;
                    e.set("t", assigned174.clone())?;
                    return Ok({
                        let mut s = Vec::new();
                        s.push({
                            let fun177 = e.get("routes")?.attr("_add")?;
                            let mut args175 = Vec::new();
                            let mut kw176 = Vec::new();
                            args175.push(e.get("first")?);
                            args175.push({
                                let fun180 = e.get("routes")?.attr("_mul")?;
                                let mut args178 = Vec::new();
                                let mut kw179 = Vec::new();
                                args178.push({
                                    let fun183 = e.get("routes")?.attr("_sub")?;
                                    let mut args181 = Vec::new();
                                    let mut kw182 = Vec::new();
                                    args181.push(e.get("last")?);
                                    args181.push(e.get("first")?);
                                    fun183.call(args181, kw182)?
                                });
                                args178.push(e.get("t")?);
                                fun180.call(args178, kw179)?
                            });
                            fun177.call(args175, kw176)?
                        });
                        s.push({
                            let fun186 = e.get("routes")?.attr("_unit")?;
                            let mut args184 = Vec::new();
                            let mut kw185 = Vec::new();
                            args184.push({
                                let fun189 = e.get("routes")?.attr("_sub")?;
                                let mut args187 = Vec::new();
                                let mut kw188 = Vec::new();
                                args187.push(e.get("last")?);
                                args187.push(e.get("first")?);
                                fun189.call(args187, kw188)?
                            });
                            fun186.call(args184, kw185)?
                        });
                        Val::tuple(s)
                    });
                }
                let assigned190 = {
                    let mut s = Vec::new();
                    s.push(e.get("segment")?.get(Val::Str("center_mm".into()))?);
                    s.push(e.get("segment")?.get(Val::Str("axis".into()))?);
                    Val::tuple(s)
                };
                let unpack191 = unpack(assigned190.clone(), 2)?;
                e.set("center", unpack191[0].clone())?;
                e.set("axis", unpack191[1].clone())?;
                let assigned192 = {
                    let fun195 = e.get("routes")?.attr("_sub")?;
                    let mut args193 = Vec::new();
                    let mut kw194 = Vec::new();
                    args193.push(e.get("first")?);
                    args193.push(e.get("center")?);
                    fun195.call(args193, kw194)?
                };
                e.set("radial", assigned192.clone())?;
                let assigned196 = {
                    let fun199 = e.get("routes")?.attr("_cross")?;
                    let mut args197 = Vec::new();
                    let mut kw198 = Vec::new();
                    args197.push(e.get("axis")?);
                    args197.push(e.get("radial")?);
                    fun199.call(args197, kw198)?
                };
                e.set("sideways", assigned196.clone())?;
                // point
                e.set("point", {
                    let params = vec![("angle".into(), None, false)];
                    let outer = e.clone();
                    let runtime = rt.clone();
                    Val::function(move |args, kwargs| {
                        let rt = runtime.clone();
                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                        let _frame = rt.frame(&outer);
                        return Ok({
                            let fun202 = e.get("routes")?.attr("_add")?;
                            let mut args200 = Vec::new();
                            let mut kw201 = Vec::new();
                            args200.push(e.get("center")?);
                            args200.push({
                                let fun205 = e.get("routes")?.attr("_add")?;
                                let mut args203 = Vec::new();
                                let mut kw204 = Vec::new();
                                args203.push({
                                    let fun208 = e.get("routes")?.attr("_mul")?;
                                    let mut args206 = Vec::new();
                                    let mut kw207 = Vec::new();
                                    args206.push(e.get("radial")?);
                                    args206.push({
                                        let fun211 = e.get("math")?.attr("cos")?;
                                        let mut args209 = Vec::new();
                                        let mut kw210 = Vec::new();
                                        args209.push(e.get("angle")?);
                                        fun211.call(args209, kw210)?
                                    });
                                    fun208.call(args206, kw207)?
                                });
                                args203.push({
                                    let fun214 = e.get("routes")?.attr("_mul")?;
                                    let mut args212 = Vec::new();
                                    let mut kw213 = Vec::new();
                                    args212.push(e.get("sideways")?);
                                    args212.push({
                                        let fun217 = e.get("math")?.attr("sin")?;
                                        let mut args215 = Vec::new();
                                        let mut kw216 = Vec::new();
                                        args215.push(e.get("angle")?);
                                        fun217.call(args215, kw216)?
                                    });
                                    fun214.call(args212, kw213)?
                                });
                                fun205.call(args203, kw204)?
                            });
                            fun202.call(args200, kw201)?
                        });
                        Ok(Val::None)
                    })
                })?;
                let assigned218 = {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(e.get("segment")?.get(Val::Str("angle_rad".into()))?);
                    Val::tuple(s)
                };
                let unpack219 = unpack(assigned218.clone(), 2)?;
                e.set("lo", unpack219[0].clone())?;
                e.set("hi", unpack219[1].clone())?;
                let assigned220 = {
                    let v221 = e.get("last")?.get(Val::Int(1i64))?;
                    let v222 = e.get("first")?.get(Val::Int(1i64))?;
                    Val::Bool(compare("gt", v221.clone(), v222.clone())?.truthy()?)
                };
                e.set("increasing", assigned220.clone())?;
                for item223 in {
                    let fun236 = e.get("range")?;
                    let mut args234 = Vec::new();
                    let mut kw235 = Vec::new();
                    args234.push(Val::Int(48i64));
                    fun236.call(args234, kw235)?
                }
                .iter()?
                {
                    e.set("_", item223)?;
                    let assigned224 = binary(
                        "truediv",
                        binary("add", e.get("lo")?, e.get("hi")?)?,
                        Val::Int(2i64),
                    )?;
                    e.set("mid", assigned224.clone())?;
                    if {
                        let v230 = {
                            let v228 = {
                                let fun227 = e.get("point")?;
                                let mut args225 = Vec::new();
                                let mut kw226 = Vec::new();
                                args225.push(e.get("mid")?);
                                fun227.call(args225, kw226)?
                            }
                            .get(Val::Int(1i64))?;
                            let v229 = e.get("y")?;
                            Val::Bool(compare("lt", v228.clone(), v229.clone())?.truthy()?)
                        };
                        let v231 = e.get("increasing")?;
                        Val::Bool(compare("eq", v230.clone(), v231.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned232 = e.get("mid")?;
                        e.set("lo", assigned232.clone())?;
                    } else {
                        let assigned233 = e.get("mid")?;
                        e.set("hi", assigned233.clone())?;
                    }
                }
                let assigned237 = {
                    let fun240 = e.get("point")?;
                    let mut args238 = Vec::new();
                    let mut kw239 = Vec::new();
                    args238.push(binary(
                        "truediv",
                        binary("add", e.get("lo")?, e.get("hi")?)?,
                        Val::Int(2i64),
                    )?);
                    fun240.call(args238, kw239)?
                };
                e.set("station", assigned237.clone())?;
                return Ok({
                    let mut s = Vec::new();
                    s.push(e.get("station")?);
                    s.push({
                        let fun243 = e.get("routes")?.attr("_unit")?;
                        let mut args241 = Vec::new();
                        let mut kw242 = Vec::new();
                        args241.push({
                            let fun246 = e.get("routes")?.attr("_cross")?;
                            let mut args244 = Vec::new();
                            let mut kw245 = Vec::new();
                            args244.push(e.get("axis")?);
                            args244.push({
                                let fun249 = e.get("routes")?.attr("_sub")?;
                                let mut args247 = Vec::new();
                                let mut kw248 = Vec::new();
                                args247.push(e.get("station")?);
                                args247.push(e.get("center")?);
                                fun249.call(args247, kw248)?
                            });
                            fun246.call(args244, kw245)?
                        });
                        fun243.call(args241, kw242)?
                    });
                    Val::tuple(s)
                });
            }
            anyhow::bail!(
                "{}",
                val_string({
                    let fun255 = e.get("ValueError")?;
                    let mut args253 = Vec::new();
                    let mut kw254 = Vec::new();
                    args253.push({
                        let mut str256 = String::new();
                        str256.push_str(&format(&e.get("identifier")?, &String::new())?);
                        str256.push_str(" has no restraint crossing at Y");
                        str256.push_str(&format(
                            &e.get("y")?,
                            &val_string({
                                let mut str257 = String::new();
                                str257.push_str("g");
                                Val::Str(str257)
                            })?,
                        )?);
                        Val::Str(str256)
                    });
                    fun255.call(args253, kw254)?
                })?
            );
            Ok(Val::None)
        })
    })?;
    // tie_profile
    e.set("tie_profile", {
        let params = vec![("row".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned258 = {
                let fun261 = e.get("specification")?;
                let mut args259 = Vec::new();
                let mut kw260 = Vec::new();
                fun261.call(args259, kw260)?
            };
            e.set("spec", assigned258.clone())?;
            let assigned262 = e
                .get("row")?
                .get(Val::Str("tube_centers_world_mm".into()))?;
            let unpack263 = unpack(assigned262.clone(), 2)?;
            e.set("first", unpack263[0].clone())?;
            e.set("last", unpack263[1].clone())?;
            let assigned264 = {
                let mut s = Vec::new();
                s.push(e.get("first")?.get(Val::Int(0i64))?);
                s.push(e.get("last")?.get(Val::Int(0i64))?);
                s.push(e.get("first")?.get(Val::Int(2i64))?);
                Val::tuple(s)
            };
            let unpack265 = unpack(assigned264.clone(), 3)?;
            e.set("x0", unpack265[0].clone())?;
            e.set("x1", unpack265[1].clone())?;
            e.set("z", unpack265[2].clone())?;
            let assigned266 = e
                .get("spec")?
                .get(Val::Str("tie_witness_outer_bend_radius_mm".into()))?;
            e.set("radius", assigned266.clone())?;
            let assigned267 = e
                .get("spec")?
                .get(Val::Str("tie_witness_bottom_center_z_mm".into()))?;
            e.set("bottom", assigned267.clone())?;
            let assigned268 = Val::Float(1.5f64);
            e.set("turn", assigned268.clone())?;
            let assigned269 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("points", assigned269.clone())?;
            // arc
            e.set("arc", {
                let params = vec![
                    ("x".into(), None, false),
                    ("zz".into(), None, false),
                    ("r".into(), None, false),
                    ("start".into(), None, false),
                    ("end".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    for item270 in {
                        let fun283 = e.get("range")?;
                        let mut args281 = Vec::new();
                        let mut kw282 = Vec::new();
                        args281.push(Val::Int(13i64));
                        fun283.call(args281, kw282)?
                    }
                    .iter()?
                    {
                        e.set("i", item270)?;
                        let assigned271 = binary(
                            "add",
                            e.get("start")?,
                            binary(
                                "truediv",
                                binary(
                                    "mul",
                                    binary("sub", e.get("end")?, e.get("start")?)?,
                                    e.get("i")?,
                                )?,
                                Val::Int(12i64),
                            )?,
                        )?;
                        e.set("angle", assigned271.clone())?;
                        {
                            let fun274 = e.get("points")?.attr("append")?;
                            let mut args272 = Vec::new();
                            let mut kw273 = Vec::new();
                            args272.push({
                                let mut s = Vec::new();
                                s.push(binary(
                                    "add",
                                    e.get("x")?,
                                    binary("mul", e.get("r")?, {
                                        let fun277 = e.get("math")?.attr("cos")?;
                                        let mut args275 = Vec::new();
                                        let mut kw276 = Vec::new();
                                        args275.push(e.get("angle")?);
                                        fun277.call(args275, kw276)?
                                    })?,
                                )?);
                                s.push(binary(
                                    "add",
                                    e.get("zz")?,
                                    binary("mul", e.get("r")?, {
                                        let fun280 = e.get("math")?.attr("sin")?;
                                        let mut args278 = Vec::new();
                                        let mut kw279 = Vec::new();
                                        args278.push(e.get("angle")?);
                                        fun280.call(args278, kw279)?
                                    })?,
                                )?);
                                Val::tuple(s)
                            });
                            fun274.call(args272, kw273)?
                        };
                    }
                    Ok(Val::None)
                })
            })?;
            let assigned284 = binary(
                "add",
                {
                    let fun287 = e.get("math")?.attr("atan2")?;
                    let mut args285 = Vec::new();
                    let mut kw286 = Vec::new();
                    args285.push(binary(
                        "sub",
                        e.get("last")?.get(Val::Int(2i64))?,
                        e.get("first")?.get(Val::Int(2i64))?,
                    )?);
                    args285.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                    fun287.call(args285, kw286)?
                },
                binary("truediv", e.get("math")?.attr("pi")?, Val::Int(2i64))?,
            )?;
            e.set("tangent", assigned284.clone())?;
            {
                let fun290 = e.get("arc")?;
                let mut args288 = Vec::new();
                let mut kw289 = Vec::new();
                args288.push(e.get("x0")?);
                args288.push(e.get("z")?);
                args288.push(e.get("radius")?);
                args288.push(e.get("math")?.attr("pi")?);
                args288.push(e.get("tangent")?);
                fun290.call(args288, kw289)?
            };
            {
                let fun293 = e.get("arc")?;
                let mut args291 = Vec::new();
                let mut kw292 = Vec::new();
                args291.push(e.get("x1")?);
                args291.push(e.get("last")?.get(Val::Int(2i64))?);
                args291.push(e.get("radius")?);
                args291.push(e.get("tangent")?);
                args291.push(Val::Int(0i64));
                fun293.call(args291, kw292)?
            };
            {
                let fun296 = e.get("arc")?;
                let mut args294 = Vec::new();
                let mut kw295 = Vec::new();
                args294.push(binary(
                    "sub",
                    binary("add", e.get("x1")?, e.get("radius")?)?,
                    e.get("turn")?,
                )?);
                args294.push(binary("add", e.get("bottom")?, e.get("turn")?)?);
                args294.push(e.get("turn")?);
                args294.push(Val::Int(0i64));
                args294.push(binary(
                    "truediv",
                    unary("neg", e.get("math")?.attr("pi")?)?,
                    Val::Int(2i64),
                )?);
                fun296.call(args294, kw295)?
            };
            {
                let fun299 = e.get("arc")?;
                let mut args297 = Vec::new();
                let mut kw298 = Vec::new();
                args297.push(binary(
                    "add",
                    binary("sub", e.get("x0")?, e.get("radius")?)?,
                    e.get("turn")?,
                )?);
                args297.push(binary("add", e.get("bottom")?, e.get("turn")?)?);
                args297.push(e.get("turn")?);
                args297.push(binary(
                    "truediv",
                    unary("neg", e.get("math")?.attr("pi")?)?,
                    Val::Int(2i64),
                )?);
                args297.push(unary("neg", e.get("math")?.attr("pi")?)?);
                fun299.call(args297, kw298)?
            };
            return Ok(e.get("points")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
