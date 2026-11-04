#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
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
                    let fun17 = binary(
                        "truediv",
                        binary(
                            "truediv",
                            binary("truediv", e.get("p")?, Val::Str("hardware".into()))?,
                            Val::Str("scripts".into()),
                        )?,
                        Val::Str("_cadq_export.py".into()),
                    )?
                    .attr("is_file")?;
                    let mut args15 = Vec::new();
                    let mut kw16 = Vec::new();
                    fun17.call(args15, kw16)?
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
    e.set("_repo", assigned9.clone())?;
    let assigned18 = binary("truediv", e.get("_repo")?, Val::Str("hardware".into()))?;
    e.set("_hw", assigned18.clone())?;
    let assigned19 = binary(
        "truediv",
        binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
        Val::Str("cold-core".into()),
    )?;
    e.set("_cold_core", assigned19.clone())?;
    {
        let fun22 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args20 = Vec::new();
        let mut kw21 = Vec::new();
        args20.push(Val::Int(0i64));
        args20.push({
            let fun25 = e.get("str")?;
            let mut args23 = Vec::new();
            let mut kw24 = Vec::new();
            args23.push(binary(
                "truediv",
                e.get("_hw")?,
                Val::Str("scripts".into()),
            )?);
            fun25.call(args23, kw24)?
        });
        fun22.call(args20, kw21)?
    };
    {
        let fun28 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args26 = Vec::new();
        let mut kw27 = Vec::new();
        args26.push(Val::Int(0i64));
        args26.push({
            let fun31 = e.get("str")?;
            let mut args29 = Vec::new();
            let mut kw30 = Vec::new();
            args29.push(e.get("_cold_core")?);
            fun31.call(args29, kw30)?
        });
        fun28.call(args26, kw27)?
    };
    {
        let fun34 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args32 = Vec::new();
        let mut kw33 = Vec::new();
        args32.push(Val::Int(0i64));
        args32.push({
            let fun37 = e.get("str")?;
            let mut args35 = Vec::new();
            let mut kw36 = Vec::new();
            args35.push(binary(
                "truediv",
                binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
                Val::Str("cadlib".into()),
            )?);
            fun37.call(args35, kw36)?
        });
        fun34.call(args32, kw33)?
    };
    let mod38 = rt.import_module("_cold_core_interface")?;
    e.set(
        "cap_side_anchors",
        rt.member("_cold_core_interface", "cap_side_anchors")?,
    )?;
    e.set(
        "attachment_xy_positions",
        rt.member("_cold_core_interface", "attachment_xy_positions")?,
    )?;
    e.set(
        "cap_shell_clearance",
        rt.member("_cold_core_interface", "cap_shell_clearance")?,
    )?;
    e.set(
        "foam_cap_height",
        rt.member("_cold_core_interface", "foam_cap_height")?,
    )?;
    e.set(
        "cap_anchors",
        rt.member("_cold_core_interface", "cap_anchors")?,
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
        "cap_conduit_axis",
        rt.member("_cold_core_interface", "cap_conduit_axis")?,
    )?;
    e.set(
        "cap_conduit_bore_radius",
        rt.member("_cold_core_interface", "cap_conduit_bore_radius")?,
    )?;
    e.set(
        "co2_inlet_tube_radius",
        rt.member("_cold_core_interface", "co2_inlet_tube_radius")?,
    )?;
    e.set(
        "screw_clearance_radius",
        rt.member("_cold_core_interface", "screw_clearance_radius")?,
    )?;
    e.set(
        "deck_mount_xy",
        rt.member("_cold_core_interface", "deck_mount_xy")?,
    )?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    e.set(
        "head_pad_height",
        rt.member("_cold_core_interface", "head_pad_height")?,
    )?;
    let mod39 = rt.import_module("_foam_cap")?;
    e.set("cap_face_z", rt.member("_foam_cap", "cap_face_z")?)?;
    e.set(
        "lid_total_height",
        rt.member("_foam_cap", "lid_total_height")?,
    )?;
    e.set("stack_floor_z", rt.member("_foam_cap", "stack_floor_z")?)?;
    e.set("top_cap_height", rt.member("_foam_cap", "top_cap_height")?)?;
    let mod40 = rt.import_module("_port_cuts")?;
    e.set("co2_inlet_xyz", rt.member("_port_cuts", "co2_inlet_xyz")?)?;
    e.set("routes", rt.import_module("_internal_routes")?)?;
    e.set("_routing", rt.import_module("_routing")?)?;
    e.set("_mat", rt.import_module("_materials")?)?;
    e.set("_above_mounts", rt.import_module("_above_core_mounts")?)?;
    let assigned41 = binary("sub", e.get("cap_face_z")?, e.get("stack_floor_z")?)?;
    e.set("cap_face_over_floor", assigned41.clone())?;
    let assigned42 = binary(
        "truediv",
        binary(
            "truediv",
            e.get("_cold_core")?,
            Val::Str("foam-shell".into()),
        )?,
        Val::Str("foam-shell.step".into()),
    )?;
    e.set("SHELL_STEP", assigned42.clone())?;
    let assigned43 = binary("truediv", e.get("_cold_core")?, Val::Str("foam-cap".into()))?;
    e.set("CAP_DIR", assigned43.clone())?;
    let assigned44 = binary(
        "truediv",
        e.get("_cold_core")?,
        Val::Str("reservoir".into()),
    )?;
    e.set("RESERVOIR_DIR", assigned44.clone())?;
    let assigned45 = {
        let d = Val::dict(vec![]);
        d.set(
            Val::Str("reservoir A".into()),
            Val::Str("reservoir-right".into()),
        )?;
        d.set(
            Val::Str("reservoir B".into()),
            Val::Str("reservoir-left".into()),
        )?;
        d
    };
    e.set("RESERVOIRS", assigned45.clone())?;
    let assigned46 = e.get("routes")?.attr("reservoir_cap_z")?;
    e.set("RESERVOIR_CAP_Z", assigned46.clone())?;
    let assigned47 = e.get("_mat")?.attr("C_FOAM_SHELL")?;
    e.set("SHELL_COLOR", assigned47.clone())?;
    let assigned48 = {
        let d = Val::dict(vec![]);
        d.set(
            Val::Str("foam-cap-lid-top".into()),
            e.get("_mat")?.attr("C_CAP_LID_TOP")?,
        )?;
        d.set(
            Val::Str("foam-cap-bottom".into()),
            e.get("_mat")?.attr("C_CAP_BOTTOM")?,
        )?;
        d
    };
    e.set("COLORS", assigned48.clone())?;
    let assigned49 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("water-in".into()), Val::Str("white".into()))?;
        d.set(Val::Str("carb-water-out".into()), Val::Str("blue".into()))?;
        d.set(Val::Str("co2-in".into()), Val::Str("red".into()))?;
        d.set(Val::Str("prv-vent".into()), Val::Str("black".into()))?;
        d.set(Val::Str("reservoir-a".into()), Val::Str("black".into()))?;
        d.set(
            Val::Str("reservoir-a-fill".into()),
            Val::Str("black".into()),
        )?;
        d.set(Val::Str("reservoir-b".into()), Val::Str("black".into()))?;
        d.set(
            Val::Str("reservoir-b-fill".into()),
            Val::Str("black".into()),
        )?;
        d
    };
    e.set("ROUTE_SPOOLS", assigned49.clone())?;
    let assigned50 = {
        let e = e.child();
        let out51 = Val::dict(vec![]);
        for item52 in {
            let fun55 = e.get("ROUTE_SPOOLS")?.attr("items")?;
            let mut args53 = Vec::new();
            let mut kw54 = Vec::new();
            fun55.call(args53, kw54)?
        }
        .iter()?
        {
            let unpack56 = unpack(item52, 2)?;
            e.set("name", unpack56[0].clone())?;
            e.set("key", unpack56[1].clone())?;
            out51.set(e.get("name")?, {
                let fun59 = e.get("_routing")?.attr("color")?;
                let mut args57 = Vec::new();
                let mut kw58 = Vec::new();
                args57.push(e.get("key")?);
                fun59.call(args57, kw58)?
            })?;
        }
        out51
    };
    e.set("ROUTE_COLORS", assigned50.clone())?;
    // spin_xy
    e.set("spin_xy", {
        let params = vec![("p".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(unary("neg", e.get("p")?.get(Val::Int(0i64))?)?);
                s.push(unary("neg", e.get("p")?.get(Val::Int(1i64))?)?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // cap_conduit_station
    e.set("cap_conduit_station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun62 = e.get("spin_xy")?;
                let mut args60 = Vec::new();
                let mut kw61 = Vec::new();
                args60.push(e.get("cap_conduits")?.get(e.get("name")?)?);
                fun62.call(args60, kw61)?
            });
            Ok(Val::None)
        })
    })?;
    // cap_conduit_axis_out
    e.set("cap_conduit_axis_out", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("cap_conduit_axis")?);
            Ok(Val::None)
        })
    })?;
    // cap_conduit_mouth
    e.set("cap_conduit_mouth", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v63 = e.get("name")?;
                let v64 = Val::Str("reservoir-b-fill".into());
                Val::Bool(compare("eq", v63.clone(), v64.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned65 = {
                    let fun68 = e.get("_above_mounts")?.attr("reservoir_b_fill_passage")?;
                    let mut args66 = Vec::new();
                    let mut kw67 = Vec::new();
                    fun68.call(args66, kw67)?
                };
                e.set("passage", assigned65.clone())?;
                let assigned69 = e.get("passage")?.get(Val::Str("entry_world_mm".into()))?;
                e.set("point", assigned69.clone())?;
                let assigned70 = {
                    let fun73 = e.get("routes")?.attr("world_point_in_shell")?;
                    let mut args71 = Vec::new();
                    let mut kw72 = Vec::new();
                    args71.push(e.get("point")?);
                    fun73.call(args71, kw72)?
                };
                e.set("mouth", assigned70.clone())?;
                let assigned74 = {
                    let fun77 = e.get("routes")?.attr("world_point_in_shell")?;
                    let mut args75 = Vec::new();
                    let mut kw76 = Vec::new();
                    args75.push({
                        let fun80 = e.get("tuple")?;
                        let mut args78 = Vec::new();
                        let mut kw79 = Vec::new();
                        args78.push({
                            let e = e.child();
                            let out81 = Val::list(vec![]);
                            for item82 in {
                                let fun85 = e.get("zip")?;
                                let mut args83 = Vec::new();
                                let mut kw84 = Vec::new();
                                args83.push(e.get("point")?);
                                args83.push(
                                    e.get("passage")?
                                        .get(Val::Str("outward_axis_world".into()))?,
                                );
                                fun85.call(args83, kw84)?
                            }
                            .iter()?
                            {
                                let unpack86 = unpack(item82, 2)?;
                                e.set("p", unpack86[0].clone())?;
                                e.set("a", unpack86[1].clone())?;
                                out81
                                    .attr("append")?
                                    .call(vec![binary("add", e.get("p")?, e.get("a")?)?], vec![])?;
                            }
                            out81
                        });
                        fun80.call(args78, kw79)?
                    });
                    fun77.call(args75, kw76)?
                };
                e.set("outside", assigned74.clone())?;
                return Ok({
                    let mut s = Vec::new();
                    s.push(e.get("mouth")?);
                    s.push({
                        let fun89 = e.get("tuple")?;
                        let mut args87 = Vec::new();
                        let mut kw88 = Vec::new();
                        args87.push({
                            let e = e.child();
                            let out90 = Val::list(vec![]);
                            for item91 in {
                                let fun94 = e.get("zip")?;
                                let mut args92 = Vec::new();
                                let mut kw93 = Vec::new();
                                args92.push(e.get("mouth")?);
                                args92.push(e.get("outside")?);
                                fun94.call(args92, kw93)?
                            }
                            .iter()?
                            {
                                let unpack95 = unpack(item91, 2)?;
                                e.set("a", unpack95[0].clone())?;
                                e.set("b", unpack95[1].clone())?;
                                out90
                                    .attr("append")?
                                    .call(vec![binary("sub", e.get("b")?, e.get("a")?)?], vec![])?;
                            }
                            out90
                        });
                        fun89.call(args87, kw88)?
                    });
                    Val::tuple(s)
                });
            }
            let assigned96 = {
                let fun99 = e.get("cap_conduit_station")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                args97.push(e.get("name")?);
                fun99.call(args97, kw98)?
            };
            let unpack100 = unpack(assigned96.clone(), 2)?;
            e.set("x", unpack100[0].clone())?;
            e.set("y", unpack100[1].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(e.get("cap_face_z")?);
                    Val::tuple(s)
                });
                s.push(e.get("cap_conduit_axis")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // cap_anchor_station
    e.set("cap_anchor_station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun103 = e.get("spin_xy")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                args101.push(e.get("cap_anchors")?.get(e.get("name")?)?.attr("centre")?);
                fun103.call(args101, kw102)?
            });
            Ok(Val::None)
        })
    })?;
    // cap_side_anchor_station
    e.set("cap_side_anchor_station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned104 = e.get("cap_side_anchors")?.get(e.get("name")?)?;
            e.set("a", assigned104.clone())?;
            return Ok({
                let fun107 = e.get("spin_xy")?;
                let mut args105 = Vec::new();
                let mut kw106 = Vec::new();
                args105.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("a")?.attr("centre")?.get(Val::Int(0i64))?,
                        e.get("a")?.attr("axis_off")?,
                    )?);
                    s.push(e.get("a")?.attr("centre")?.get(Val::Int(1i64))?);
                    Val::tuple(s)
                });
                fun107.call(args105, kw106)?
            });
            Ok(Val::None)
        })
    })?;
    // deck_mount_station
    e.set("deck_mount_station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun110 = e.get("tuple")?;
                let mut args108 = Vec::new();
                let mut kw109 = Vec::new();
                args108.push({
                    let e = e.child();
                    let out111 = Val::list(vec![]);
                    for item112 in {
                        let fun115 = e.get("deck_mount_xy")?;
                        let mut args113 = Vec::new();
                        let mut kw114 = Vec::new();
                        args113.push(e.get("name")?);
                        fun115.call(args113, kw114)?
                    }
                    .iter()?
                    {
                        e.set("p", item112)?;
                        out111.attr("append")?.call(
                            vec![{
                                let fun118 = e.get("spin_xy")?;
                                let mut args116 = Vec::new();
                                let mut kw117 = Vec::new();
                                args116.push(e.get("p")?);
                                fun118.call(args116, kw117)?
                            }],
                            vec![],
                        )?;
                    }
                    out111
                });
                fun110.call(args108, kw109)?
            });
            Ok(Val::None)
        })
    })?;
    // _report
    e.set("_report",{let params=vec![("placed".into(),None,false),("measurements".into(),None,true)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);// bounds
e.set("bounds",{let params=vec![("name".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let mod119=rt.import_module("types")?;e.set("SimpleNamespace",rt.member("types","SimpleNamespace")?)?;
let assigned120=e.get("measurements")?.get(Val::Str("bounds".into()))?.get(e.get("name")?)?;let unpack121=unpack(assigned120.clone(),2)?;e.set("low",unpack121[0].clone())?;e.set("high",unpack121[1].clone())?;
return Ok({let fun124=e.get("SimpleNamespace")?;let mut args122=Vec::new();let mut kw123=Vec::new();kw123.push(("xmin".into(),e.get("low")?.get(Val::Int(0i64))?));kw123.push(("ymin".into(),e.get("low")?.get(Val::Int(1i64))?));kw123.push(("zmin".into(),e.get("low")?.get(Val::Int(2i64))?));kw123.push(("xmax".into(),e.get("high")?.get(Val::Int(0i64))?));kw123.push(("ymax".into(),e.get("high")?.get(Val::Int(1i64))?));kw123.push(("zmax".into(),e.get("high")?.get(Val::Int(2i64))?));kw123.push(("xlen".into(),binary("sub",e.get("high")?.get(Val::Int(0i64))?,e.get("low")?.get(Val::Int(0i64))?)?));kw123.push(("ylen".into(),binary("sub",e.get("high")?.get(Val::Int(1i64))?,e.get("low")?.get(Val::Int(1i64))?)?));kw123.push(("zlen".into(),binary("sub",e.get("high")?.get(Val::Int(2i64))?,e.get("low")?.get(Val::Int(2i64))?)?));fun124.call(args122,kw123)?});
Ok(Val::None)})})?;
{let fun127=e.get("print")?;let mut args125=Vec::new();let mut kw126=Vec::new();args125.push(Val::Str("  part                  X range            Y range            Z range".into()));fun127.call(args125,kw126)?};
for item128 in {let fun138=e.get("placed")?.attr("items")?;let mut args136=Vec::new();let mut kw137=Vec::new();fun138.call(args136,kw137)?}.iter()? {
let unpack139=unpack(item128,2)?;e.set("name",unpack139[0].clone())?;let unpack140=unpack(unpack139[1].clone(),2)?;e.set("shape",unpack140[0].clone())?;e.set("_c",unpack140[1].clone())?;let assigned129={let fun132=e.get("bounds")?;let mut args130=Vec::new();let mut kw131=Vec::new();args130.push(e.get("name")?);fun132.call(args130,kw131)?};e.set("b",assigned129.clone())?;
{let fun135=e.get("print")?;let mut args133=Vec::new();let mut kw134=Vec::new();args133.push(binary("mod",Val::Str("  %-19s [%7.1f,%7.1f]  [%7.1f,%7.1f]  [%7.1f,%7.1f]".into()),{let mut s=Vec::new();s.push(e.get("name")?);s.push(e.get("b")?.attr("xmin")?);s.push(e.get("b")?.attr("xmax")?);s.push(e.get("b")?.attr("ymin")?);s.push(e.get("b")?.attr("ymax")?);s.push(e.get("b")?.attr("zmin")?);s.push(e.get("b")?.attr("zmax")?);Val::tuple(s)})?);fun135.call(args133,kw134)?};
}
let assigned141={let e=e.child();let out142=Val::list(vec![]);for item143 in e.get("attachment_xy_positions")?.iter()? {let unpack144=unpack(item143,2)?;e.set("x",unpack144[0].clone())?;e.set("y",unpack144[1].clone())?;out142.attr("append")?.call(vec![{let mut s=Vec::new();s.push({let fun147=e.get("round")?;let mut args145=Vec::new();let mut kw146=Vec::new();args145.push(e.get("x")?);args145.push(Val::Int(6i64));fun147.call(args145,kw146)?});s.push({let fun150=e.get("round")?;let mut args148=Vec::new();let mut kw149=Vec::new();args148.push(e.get("y")?);args148.push(Val::Int(6i64));fun150.call(args148,kw149)?});Val::tuple(s)}],vec![])?;}out142};e.set("P",assigned141.clone())?;
let assigned151={let fun154=e.get("bounds")?;let mut args152=Vec::new();let mut kw153=Vec::new();args152.push(Val::Str("foam-cap-bottom".into()));fun154.call(args152,kw153)?}.attr("zmin")?;e.set("floor",assigned151.clone())?;
let assigned155=binary("add",{let fun158=e.get("bounds")?;let mut args156=Vec::new();let mut kw157=Vec::new();args156.push(Val::Str("foam-cap-lid-top".into()));fun158.call(args156,kw157)?}.attr("zmin")?,e.get("lid_total_height")?)?;e.set("face",assigned155.clone())?;
if !{let v164={let v168={let fun167=e.get("abs")?;let mut args165=Vec::new();let mut kw166=Vec::new();args165.push(binary("sub",e.get("floor")?,e.get("stack_floor_z")?)?);fun167.call(args165,kw166)?};let v169=Val::Float(1e-06f64);Val::Bool(compare("lt",v168.clone(),v169.clone())?.truthy()?)};if v164.truthy()? {{let v162={let fun161=e.get("abs")?;let mut args159=Vec::new();let mut kw160=Vec::new();args159.push(binary("sub",e.get("face")?,e.get("cap_face_z")?)?);fun161.call(args159,kw160)?};let v163=Val::Float(1e-06f64);Val::Bool(compare("lt",v162.clone(),v163.clone())?.truthy()?)}} else {v164}}.truthy()? {anyhow::bail!("{}",val_string({let mut str170=String::new();str170.push_str("the stack stands on ");str170.push_str(&format(&e.get("floor")?,&val_string({let mut str171=String::new();str171.push_str(".4f");Val::Str(str171)})?)?);str170.push_str(" and presents its cap face at ");str170.push_str(&format(&e.get("face")?,&val_string({let mut str172=String::new();str172.push_str(".4f");Val::Str(str172)})?)?);str170.push_str(", against the ");str170.push_str(&format(&e.get("stack_floor_z")?,&val_string({let mut str173=String::new();str173.push_str(".4f");Val::Str(str173)})?)?);str170.push_str(" / ");str170.push_str(&format(&e.get("cap_face_z")?,&val_string({let mut str174=String::new();str174.push_str(".4f");Val::Str(str174)})?)?);str170.push_str(" this module tells the machine to expect");Val::Str(str170)})?);}
{let fun177=e.get("print")?;let mut args175=Vec::new();let mut kw176=Vec::new();args175.push(binary("mod",Val::Str("  cap face %.1f, %.1f mm over the stack's own floor — what stands on the core is placed off this, not off the box's top  OK".into()),{let mut s=Vec::new();s.push(e.get("face")?);s.push(e.get("cap_face_over_floor")?);Val::tuple(s)})?);fun177.call(args175,kw176)?};
let assigned178=binary("sub",e.get("co2_inlet_tube_radius")?,Val::Float(0.3f64))?;e.set("probe_r",assigned178.clone())?;
let assigned179=e.get("placed")?.get(Val::Str("foam-shell".into()))?.get(Val::Int(0i64))?;e.set("shell_solid",assigned179.clone())?;
let assigned180=e.get("measurements")?.get(Val::Str("co2".into()))?;e.set("reading",assigned180.clone())?;
let assigned181={let mut s=Vec::new();s.extend(e.get("reading")?.get(Val::Str("start".into()))?.get(Val::Slice{start:None,stop:Some(Val::Int(2i64).integer()?),step:1})?.iter()?);s.extend(e.get("reading")?.get(Val::Str("end".into()))?.get(Val::Slice{start:None,stop:Some(Val::Int(2i64).integer()?),step:1})?.iter()?);Val::tuple(s)};e.set("reach_xy",assigned181.clone())?;
let assigned182={let mut s=Vec::new();s.push(e.get("reading")?.get(Val::Str("length".into()))?);s.push(e.get("reading")?.get(Val::Str("blocked".into()))?);Val::tuple(s)};let unpack183=unpack(assigned182.clone(),2)?;e.set("reach_length",unpack183[0].clone())?;e.set("blocked",unpack183[1].clone())?;
{let fun186=e.get("print")?;let mut args184=Vec::new();let mut kw185=Vec::new();args184.push(binary("mod",Val::Str("  CO2 reach in: (%.2f, %.2f) .. (%.2f, %.2f) at z %.2f, %.1f mm straight — %s".into()),{let mut s=Vec::new();s.extend(e.get("reach_xy")?.iter()?);s.push(e.get("co2_inlet_xyz")?.get(Val::Int(2i64))?);s.push(e.get("reach_length")?);s.push(if {let v187=e.get("blocked")?;let v188=Val::Float(1e-06f64);Val::Bool(compare("le",v187.clone(),v188.clone())?.truthy()?)}.truthy()? {Val::Str("clear  OK".into())} else {binary("mod",Val::Str("** BLOCKED by %.3f mm^3".into()),e.get("blocked")?)?});Val::tuple(s)})?);fun186.call(args184,kw185)?};
let assigned189=binary("sub",e.get("cap_conduit_bore_radius")?,Val::Float(0.3f64))?;e.set("probe_r",assigned189.clone())?;
for item190 in e.get("cap_conduits")?.iter()? {
e.set("cname",item190)?;let assigned191=if {let v192=e.get("cname")?;let v193=Val::Str("reservoir-b-fill".into());Val::Bool(compare("eq",v192.clone(),v193.clone())?.truthy()?)}.truthy()? {e.get("routes")?.attr("line_radius")?} else {e.get("probe_r")?};e.set("radius",assigned191.clone())?;
let assigned194={let fun197=e.get("next")?;let mut args195=Vec::new();let mut kw196=Vec::new();args195.push({let e=e.child();let out198=Val::list(vec![]);for item199 in e.get("measurements")?.get(Val::Str("passages".into()))?.iter()? {e.set("row",item199)?;if {let v200=e.get("row")?.get(Val::Str("name".into()))?;let v201=e.get("cname")?;Val::Bool(compare("eq",v200.clone(),v201.clone())?.truthy()?)}.truthy()? {out198.attr("append")?.call(vec![e.get("row")?],vec![])?;}}out198});fun197.call(args195,kw196)?};e.set("reading",assigned194.clone())?;
let assigned202={let e=e.child();let out203=Val::dict(vec![]);for item204 in e.get("reading")?.get(Val::Str("blocked".into()))?.iter()? {e.set("row",item204)?;out203.set(e.get("row")?.get(Val::Str("name".into()))?,e.get("row")?.get(Val::Str("volume".into()))?)?;}out203};e.set("blocked",assigned202.clone())?;
let assigned205=e.get("reading")?.get(Val::Str("bottom_open".into()))?;e.set("bottom_open",assigned205.clone())?;
if e.get("bottom_open")?.truthy()? {
{let fun208=e.get("print")?;let mut args206=Vec::new();let mut kw207=Vec::new();args206.push({let mut str209=String::new();str209.push_str("  ** foam-cap-bottom is open on ");str209.push_str(&format(&e.get("cname")?,&String::new())?);str209.push_str("'s lower entry");Val::Str(str209)});fun208.call(args206,kw207)?};
}
for item210 in {let fun220=e.get("blocked")?.attr("items")?;let mut args218=Vec::new();let mut kw219=Vec::new();fun220.call(args218,kw219)?}.iter()? {
let unpack221=unpack(item210,2)?;e.set("name",unpack221[0].clone())?;e.set("volume",unpack221[1].clone())?;if {let v211=e.get("volume")?;let v212=Val::Float(1e-06f64);Val::Bool(compare("gt",v211.clone(),v212.clone())?.truthy()?)}.truthy()? {
{let fun215=e.get("print")?;let mut args213=Vec::new();let mut kw214=Vec::new();args213.push({let mut str216=String::new();str216.push_str("  ** ");str216.push_str(&format(&e.get("name")?,&String::new())?);str216.push_str(" blocks ");str216.push_str(&format(&e.get("cname")?,&String::new())?);str216.push_str("'s actual passage by ");str216.push_str(&format(&e.get("volume")?,&val_string({let mut str217=String::new();str217.push_str(".3f");Val::Str(str217)})?)?);str216.push_str(" mm^3");Val::Str(str216)});fun215.call(args213,kw214)?};
}
}
let assigned222={let fun225=e.get("cap_conduit_mouth")?;let mut args223=Vec::new();let mut kw224=Vec::new();args223.push(e.get("cname")?);fun225.call(args223,kw224)?};let unpack226=unpack(assigned222.clone(),2)?;e.set("mouth",unpack226[0].clone())?;e.set("_axis",unpack226[1].clone())?;
let assigned227=if {let v234={let fun230=e.get("max")?;let mut args228=Vec::new();let mut kw229=Vec::new();args228.push({let fun233=e.get("blocked")?.attr("values")?;let mut args231=Vec::new();let mut kw232=Vec::new();fun233.call(args231,kw232)?});fun230.call(args228,kw229)?};let v235=Val::Float(1e-06f64);Val::Bool(compare("le",v234.clone(),v235.clone())?.truthy()?)}.truthy()? {Val::Str("clear  OK".into())} else {Val::Str("** BLOCKED".into())};e.set("verdict",assigned227.clone())?;
{let fun238=e.get("print")?;let mut args236=Vec::new();let mut kw237=Vec::new();args236.push(binary("mod",Val::Str("  cap conduit %-16s mouth (%+7.2f,%+7.2f,%+7.2f): %s".into()),{let mut s=Vec::new();s.push(e.get("cname")?);s.extend(e.get("mouth")?.iter()?);s.push(e.get("verdict")?);Val::tuple(s)})?);fun238.call(args236,kw237)?};
}
let assigned239=binary("sub",e.get("screw_clearance_radius")?,Val::Float(0.3f64))?;e.set("probe_r",assigned239.clone())?;
let assigned240=Val::Bool(true);e.set("clear",assigned240.clone())?;
for item241 in {let mut s=Vec::new();s.push(Val::Str("foam-cap-lid-top".into()));s.push(Val::Str("foam-cap-bottom".into()));Val::tuple(s)}.iter()? {
e.set("name",item241)?;let assigned242=e.get("placed")?.get(e.get("name")?)?.get(Val::Int(0i64))?;e.set("solid",assigned242.clone())?;
let assigned243={let fun246=e.get("bounds")?;let mut args244=Vec::new();let mut kw245=Vec::new();args244.push(e.get("name")?);fun246.call(args244,kw245)?};e.set("b",assigned243.clone())?;
for item247 in e.get("P")?.iter()? {
let unpack268=unpack(item247,2)?;e.set("x",unpack268[0].clone())?;e.set("y",unpack268[1].clone())?;let assigned248={let fun251=e.get("next")?;let mut args249=Vec::new();let mut kw250=Vec::new();args249.push({let e=e.child();let out252=Val::list(vec![]);for item253 in e.get("measurements")?.get(Val::Str("screw_paths".into()))?.iter()? {e.set("row",item253)?;if {let v259={let v260=e.get("row")?.get(Val::Str("name".into()))?;let v261=e.get("name")?;Val::Bool(compare("eq",v260.clone(),v261.clone())?.truthy()?)};if v259.truthy()? {{let v257={let fun256=e.get("tuple")?;let mut args254=Vec::new();let mut kw255=Vec::new();args254.push(e.get("row")?.get(Val::Str("xy".into()))?);fun256.call(args254,kw255)?};let v258={let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);Val::tuple(s)};Val::Bool(compare("eq",v257.clone(),v258.clone())?.truthy()?)}} else {v259}}.truthy()? {out252.attr("append")?.call(vec![e.get("row")?.get(Val::Str("blocked".into()))?],vec![])?;}}out252});fun251.call(args249,kw250)?};e.set("blocked",assigned248.clone())?;
if {let v262=e.get("blocked")?;let v263=Val::Float(1e-06f64);Val::Bool(compare("gt",v262.clone(),v263.clone())?.truthy()?)}.truthy()? {
let assigned264=Val::Bool(false);e.set("clear",assigned264.clone())?;
{let fun267=e.get("print")?;let mut args265=Vec::new();let mut kw266=Vec::new();args265.push(binary("mod",Val::Str("  ** screw path BLOCKED in %s at (%.1f, %.1f)".into()),{let mut s=Vec::new();s.push(e.get("name")?);s.push(e.get("x")?);s.push(e.get("y")?);Val::tuple(s)})?);fun267.call(args265,kw266)?};
}
}
}
{let fun271=e.get("print")?;let mut args269=Vec::new();let mut kw270=Vec::new();args269.push(if e.get("clear")?.truthy()? {{let mut str272=String::new();str272.push_str("  screw paths: all ");str272.push_str(&format(&{let fun275=e.get("len")?;let mut args273=Vec::new();let mut kw274=Vec::new();args273.push(e.get("attachment_xy_positions")?);fun275.call(args273,kw274)?},&String::new())?);str272.push_str(" clear through every cap + lid (top + bottom)  OK");Val::Str(str272)}} else {Val::Str("  ** SCREW PATHS BLOCKED **".into())});fun271.call(args269,kw270)?};
let assigned276={let fun279=e.get("list")?;let mut args277=Vec::new();let mut kw278=Vec::new();args277.push(e.get("placed")?);fun279.call(args277,kw278)?};e.set("names",assigned276.clone())?;
let assigned280=Val::Bool(false);e.set("clash",assigned280.clone())?;
for item281 in {let fun310=e.get("range")?;let mut args308=Vec::new();let mut kw309=Vec::new();args308.push({let fun313=e.get("len")?;let mut args311=Vec::new();let mut kw312=Vec::new();args311.push(e.get("names")?);fun313.call(args311,kw312)?});fun310.call(args308,kw309)?}.iter()? {
e.set("i",item281)?;for item282 in {let fun304=e.get("range")?;let mut args302=Vec::new();let mut kw303=Vec::new();args302.push(binary("add",e.get("i")?,Val::Int(1i64))?);args302.push({let fun307=e.get("len")?;let mut args305=Vec::new();let mut kw306=Vec::new();args305.push(e.get("names")?);fun307.call(args305,kw306)?});fun304.call(args302,kw303)?}.iter()? {
e.set("j",item282)?;let assigned283={let mut s=Vec::new();s.push(e.get("placed")?.get(e.get("names")?.get(e.get("i")?)?)?.get(Val::Int(0i64))?);s.push(e.get("placed")?.get(e.get("names")?.get(e.get("j")?)?)?.get(Val::Int(0i64))?);Val::tuple(s)};let unpack284=unpack(assigned283.clone(),2)?;e.set("a",unpack284[0].clone())?;e.set("b",unpack284[1].clone())?;
let assigned285={let fun288=e.get("next")?;let mut args286=Vec::new();let mut kw287=Vec::new();args286.push({let e=e.child();let out289=Val::list(vec![]);for item290 in e.get("measurements")?.get(Val::Str("clashes".into()))?.iter()? {e.set("row",item290)?;if {let v293={let v294=e.get("row")?.get(Val::Str("a".into()))?;let v295=e.get("names")?.get(e.get("i")?)?;Val::Bool(compare("eq",v294.clone(),v295.clone())?.truthy()?)};if v293.truthy()? {{let v291=e.get("row")?.get(Val::Str("b".into()))?;let v292=e.get("names")?.get(e.get("j")?)?;Val::Bool(compare("eq",v291.clone(),v292.clone())?.truthy()?)}} else {v293}}.truthy()? {out289.attr("append")?.call(vec![e.get("row")?.get(Val::Str("volume".into()))?],vec![])?;}}out289});fun288.call(args286,kw287)?};e.set("vol",assigned285.clone())?;
if {let v296=e.get("vol")?;let v297=Val::Float(0.001f64);Val::Bool(compare("gt",v296.clone(),v297.clone())?.truthy()?)}.truthy()? {
let assigned298=Val::Bool(true);e.set("clash",assigned298.clone())?;
{let fun301=e.get("print")?;let mut args299=Vec::new();let mut kw300=Vec::new();args299.push(binary("mod",Val::Str("  ** SOLID clash %s / %s = %.2f mm^3".into()),{let mut s=Vec::new();s.push(e.get("names")?.get(e.get("i")?)?);s.push(e.get("names")?.get(e.get("j")?)?);s.push(e.get("vol")?);Val::tuple(s)})?);fun301.call(args299,kw300)?};
}
}
}
{let fun316=e.get("print")?;let mut args314=Vec::new();let mut kw315=Vec::new();args314.push(if unary("not",e.get("clash")?)?.truthy()? {Val::Str("  no solid collisions".into())} else {Val::Str("  ** CLASHES PRESENT **".into())});fun316.call(args314,kw315)?};
Ok(Val::None)})})?;
    // rust_main
    e.set("rust_main", {
        let params = vec![("output".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            e.set("foam_numbers", rt.import_module("foam_numbers")?)?;
            let assigned317 = if {
                let v318 = e.get("output")?;
                let v319 = Val::None;
                Val::Bool(compare("is_not", v318.clone(), v319.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun322 = e.get("Path")?;
                    let mut args320 = Vec::new();
                    let mut kw321 = Vec::new();
                    args320.push(e.get("output")?);
                    fun322.call(args320, kw321)?
                }
            } else {
                e.get("_here")?.attr("parent")?
            };
            e.set("output", assigned317.clone())?;
            {
                let fun325 = e.get("output")?.attr("mkdir")?;
                let mut args323 = Vec::new();
                let mut kw324 = Vec::new();
                kw324.push(("parents".into(), Val::Bool(true)));
                kw324.push(("exist_ok".into(), Val::Bool(true)));
                fun325.call(args323, kw324)?
            };
            let assigned326 = {
                let fun329 = e.get("foam_numbers")?.attr("numbers")?;
                let mut args327 = Vec::new();
                let mut kw328 = Vec::new();
                fun329.call(args327, kw328)?
            };
            e.set("numbers", assigned326.clone())?;
            let assigned330 = {
                let fun333 = e.get("_rust_part")?.attr("cut")?;
                let mut args331 = Vec::new();
                let mut kw332 = Vec::new();
                args331.push(Val::Str("cold-core".into()));
                args331.push(Val::Str("foam-assembly".into()));
                args331.push(e.get("numbers")?);
                args331.push(e.get("output")?);
                fun333.call(args331, kw332)?
            };
            e.set("result", assigned330.clone())?;
            let assigned334 = {
                let e = e.child();
                let out335 = Val::list(vec![]);
                for item336 in e.get("result")?.get(Val::Str("bodies".into()))?.iter()? {
                    e.set("row", item336)?;
                    if {
                        let v339 = {
                            let v340 = e.get("row")?.get(Val::Str("name".into()))?;
                            let v341 = e.get("COLORS")?;
                            Val::Bool(compare("in", v340.clone(), v341.clone())?.truthy()?)
                        };
                        if v339.truthy()? {
                            v339
                        } else {
                            {
                                let v337 = e.get("row")?.get(Val::Str("name".into()))?;
                                let v338 = Val::Str("foam-shell".into());
                                Val::Bool(compare("eq", v337.clone(), v338.clone())?.truthy()?)
                            }
                        }
                    }
                    .truthy()?
                    {
                        out335.attr("append")?.call(vec![e.get("row")?], vec![])?;
                    }
                }
                out335
            };
            e.set("casing", assigned334.clone())?;
            let assigned342 = e
                .get("casing")?
                .get(Val::Int(0i64))?
                .get(Val::Str("assembly_report".into()))?;
            e.set("measurements", assigned342.clone())?;
            let assigned343 = {
                let e = e.child();
                let out344 = Val::dict(vec![]);
                for item345 in e.get("casing")?.iter()? {
                    e.set("row", item345)?;
                    out344.set(e.get("row")?.get(Val::Str("name".into()))?, {
                        let mut s = Vec::new();
                        s.push(e.get("row")?.get(Val::Str("min".into()))?);
                        s.push(e.get("row")?.get(Val::Str("max".into()))?);
                        Val::tuple(s)
                    })?;
                }
                out344
            };
            e.get("measurements")?
                .set(Val::Str("bounds".into()), assigned343.clone())?;
            {
                let fun348 = e.get("_report")?;
                let mut args346 = Vec::new();
                let mut kw347 = Vec::new();
                args346.push({
                    let e = e.child();
                    let out349 = Val::dict(vec![]);
                    for item350 in e.get("casing")?.iter()? {
                        e.set("row", item350)?;
                        out349.set(e.get("row")?.get(Val::Str("name".into()))?, {
                            let mut s = Vec::new();
                            s.push(Val::None);
                            s.push(Val::None);
                            Val::tuple(s)
                        })?;
                    }
                    out349
                });
                kw347.push(("measurements".into(), e.get("measurements")?));
                fun348.call(args346, kw347)?
            };
            let assigned351 = {
                let fun354 = e.get("next")?;
                let mut args352 = Vec::new();
                let mut kw353 = Vec::new();
                args352.push({
                    let e = e.child();
                    let out355 = Val::list(vec![]);
                    for item356 in e.get("result")?.get(Val::Str("bodies".into()))?.iter()? {
                        e.set("row", item356)?;
                        if {
                            let v357 = Val::Str("route_report".into());
                            let v358 = e.get("row")?;
                            Val::Bool(compare("in", v357.clone(), v358.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out355.attr("append")?.call(
                                vec![e.get("row")?.get(Val::Str("route_report".into()))?],
                                vec![],
                            )?;
                        }
                    }
                    out355
                });
                fun354.call(args352, kw353)?
            };
            e.set("routes_reading", assigned351.clone())?;
            let assigned359 = {
                let e = e.child();
                let out360 = Val::dict(vec![]);
                for item361 in e
                    .get("routes_reading")?
                    .get(Val::Str("routes".into()))?
                    .iter()?
                {
                    e.set("row", item361)?;
                    out360.set(e.get("row")?.get(Val::Str("name".into()))?, {
                        let mut s = Vec::new();
                        s.push(e.get("row")?.get(Val::Str("bend".into()))?);
                        s.push(Val::None);
                        Val::tuple(s)
                    })?;
                }
                out360
            };
            e.set("fitted", assigned359.clone())?;
            let assigned362 = {
                let e = e.child();
                let out363 = Val::dict(vec![]);
                for item364 in e
                    .get("routes_reading")?
                    .get(Val::Str("routes".into()))?
                    .get(Val::Int(0i64))?
                    .get(Val::Str("blocked".into()))?
                    .iter()?
                {
                    e.set("row", item364)?;
                    out363.set(e.get("row")?.get(Val::Str("name".into()))?, Val::None)?;
                }
                out363
            };
            e.set("obstacles", assigned362.clone())?;
            {
                let fun367 = e.get("routes")?.attr("report_routes")?;
                let mut args365 = Vec::new();
                let mut kw366 = Vec::new();
                args365.push(e.get("fitted")?);
                args365.push(e.get("obstacles")?);
                kw366.push(("measurements".into(), e.get("routes_reading")?));
                fun367.call(args365, kw366)?
            };
            {
                let fun370 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args368 = Vec::new();
                let mut kw369 = Vec::new();
                args368.push(Val::Int(0i64));
                args368.push({
                    let fun373 = e.get("str")?;
                    let mut args371 = Vec::new();
                    let mut kw372 = Vec::new();
                    args371.push(binary(
                        "truediv",
                        e.get("_hw")?,
                        Val::Str("cold-core-layout".into()),
                    )?);
                    fun373.call(args371, kw372)?
                });
                fun370.call(args368, kw369)?
            };
            let mod374 = rt.import_module("_core_presentation")?;
            e.set("finish", rt.member("_core_presentation", "finish")?)?;
            {
                let fun377 = e.get("finish")?;
                let mut args375 = Vec::new();
                let mut kw376 = Vec::new();
                args375.push(binary(
                    "truediv",
                    e.get("output")?,
                    Val::Str("foam-assembly.step".into()),
                )?);
                args375.push(e.get("numbers")?.get(Val::Str("models".into()))?);
                fun377.call(args375, kw376)?
            };
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![("argv".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("argparse", rt.import_module("argparse")?)?;
            let assigned378 = {
                let fun381 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args379 = Vec::new();
                let mut kw380 = Vec::new();
                kw380.push(("description".into(), e.get("__doc__")?));
                fun381.call(args379, kw380)?
            };
            e.set("parser", assigned378.clone())?;
            {
                let fun384 = e.get("parser")?.attr("add_argument")?;
                let mut args382 = Vec::new();
                let mut kw383 = Vec::new();
                args382.push(Val::Str("--output".into()));
                kw383.push(("type".into(), e.get("Path")?));
                kw383.push((
                    "help".into(),
                    Val::Str("directory for generated assembly files".into()),
                ));
                fun384.call(args382, kw383)?
            };
            let assigned385 = {
                let fun388 = e.get("parser")?.attr("parse_args")?;
                let mut args386 = Vec::new();
                let mut kw387 = Vec::new();
                args386.push(e.get("argv")?);
                fun388.call(args386, kw387)?
            };
            e.set("args", assigned385.clone())?;
            {
                let fun391 = e.get("rust_main")?;
                let mut args389 = Vec::new();
                let mut kw390 = Vec::new();
                args389.push(e.get("args")?.attr("output")?);
                fun391.call(args389, kw390)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun394 = e.get("_rust_part")?.attr("start")?;
        let mut args392 = Vec::new();
        let mut kw393 = Vec::new();
        fun394.call(args392, kw393)?
    };
    {
        let fun397 = e.get("main")?;
        let mut args395 = Vec::new();
        let mut kw396 = Vec::new();
        fun397.call(args395, kw396)?
    };
    Ok(Val::None)
}
