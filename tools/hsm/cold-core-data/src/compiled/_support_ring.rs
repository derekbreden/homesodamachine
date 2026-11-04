#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod1 = rt.import_module("_cold_core_interface")?;
    e.set(
        "xz_plane_y_down",
        rt.member("_cold_core_interface", "xz_plane_y_down")?,
    )?;
    e.set(
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
    )?;
    e.set(
        "carbonator_coil_envelope_radius",
        rt.member("_cold_core_interface", "carbonator_coil_envelope_radius")?,
    )?;
    e.set(
        "carbonator_support_ring_height",
        rt.member("_cold_core_interface", "carbonator_support_ring_height")?,
    )?;
    e.set(
        "support_ring_radial_width",
        rt.member("_cold_core_interface", "support_ring_radial_width")?,
    )?;
    let assigned2 = Val::Int(4i64);
    e.set("slot_count", assigned2.clone())?;
    let assigned3 = Val::Float(30.0f64);
    e.set("slot_angular_width", assigned3.clone())?;
    let assigned4 = unary("neg", Val::Float(8.0f64))?;
    e.set("slot_clock", assigned4.clone())?;
    let assigned5 = Val::Float(1.0f64);
    e.set("slot_radial_margin", assigned5.clone())?;
    // revolve_rect
    e.set("revolve_rect", {
        let params = vec![
            ("r_range".into(), None, false),
            ("z_range".into(), None, false),
            ("angle".into(), Some(Val::Int(360i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned6 = {
                let mut s = Vec::new();
                s.push({
                    let fun9 = e.get("min")?;
                    let mut args7 = Vec::new();
                    let mut kw8 = Vec::new();
                    args7.push(e.get("r_range")?);
                    fun9.call(args7, kw8)?
                });
                s.push({
                    let fun12 = e.get("max")?;
                    let mut args10 = Vec::new();
                    let mut kw11 = Vec::new();
                    args10.push(e.get("r_range")?);
                    fun12.call(args10, kw11)?
                });
                Val::tuple(s)
            };
            let unpack13 = unpack(assigned6.clone(), 2)?;
            e.set("r_min", unpack13[0].clone())?;
            e.set("r_max", unpack13[1].clone())?;
            let assigned14 = {
                let mut s = Vec::new();
                s.push({
                    let fun17 = e.get("min")?;
                    let mut args15 = Vec::new();
                    let mut kw16 = Vec::new();
                    args15.push(e.get("z_range")?);
                    fun17.call(args15, kw16)?
                });
                s.push({
                    let fun20 = e.get("max")?;
                    let mut args18 = Vec::new();
                    let mut kw19 = Vec::new();
                    args18.push(e.get("z_range")?);
                    fun20.call(args18, kw19)?
                });
                Val::tuple(s)
            };
            let unpack21 = unpack(assigned14.clone(), 2)?;
            e.set("z_min", unpack21[0].clone())?;
            e.set("z_max", unpack21[1].clone())?;
            return Ok({
                let fun24 = {
                    let fun27 = {
                        let fun30 = {
                            let fun33 = {
                                let fun36 = {
                                    let fun39 = {
                                        let fun42 = {
                                            let fun45 = e.get("cq")?.attr("Workplane")?;
                                            let mut args43 = Vec::new();
                                            let mut kw44 = Vec::new();
                                            args43.push(e.get("xz_plane_y_down")?);
                                            fun45.call(args43, kw44)?
                                        }
                                        .attr("moveTo")?;
                                        let mut args40 = Vec::new();
                                        let mut kw41 = Vec::new();
                                        args40.push(e.get("r_min")?);
                                        args40.push(e.get("z_min")?);
                                        fun42.call(args40, kw41)?
                                    }
                                    .attr("lineTo")?;
                                    let mut args37 = Vec::new();
                                    let mut kw38 = Vec::new();
                                    args37.push(e.get("r_max")?);
                                    args37.push(e.get("z_min")?);
                                    fun39.call(args37, kw38)?
                                }
                                .attr("lineTo")?;
                                let mut args34 = Vec::new();
                                let mut kw35 = Vec::new();
                                args34.push(e.get("r_max")?);
                                args34.push(e.get("z_max")?);
                                fun36.call(args34, kw35)?
                            }
                            .attr("lineTo")?;
                            let mut args31 = Vec::new();
                            let mut kw32 = Vec::new();
                            args31.push(e.get("r_min")?);
                            args31.push(e.get("z_max")?);
                            fun33.call(args31, kw32)?
                        }
                        .attr("lineTo")?;
                        let mut args28 = Vec::new();
                        let mut kw29 = Vec::new();
                        args28.push(e.get("r_min")?);
                        args28.push(e.get("z_min")?);
                        fun30.call(args28, kw29)?
                    }
                    .attr("wire")?;
                    let mut args25 = Vec::new();
                    let mut kw26 = Vec::new();
                    fun27.call(args25, kw26)?
                }
                .attr("revolve")?;
                let mut args22 = Vec::new();
                let mut kw23 = Vec::new();
                args22.push(e.get("angle")?);
                fun24.call(args22, kw23)?
            });
            Ok(Val::None)
        })
    })?;
    // build_carbonator_support_ring
    e.set("build_carbonator_support_ring", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned46 = e.get("carbonator_coil_envelope_radius")?;
            e.set("r_outer", assigned46.clone())?;
            let assigned47 = binary(
                "sub",
                e.get("r_outer")?,
                e.get("support_ring_radial_width")?,
            )?;
            e.set("r_inner", assigned47.clone())?;
            let assigned48 = e.get("wall_and_floor_thickness")?;
            e.set("z_bottom", assigned48.clone())?;
            let assigned49 = binary(
                "add",
                e.get("z_bottom")?,
                e.get("carbonator_support_ring_height")?,
            )?;
            e.set("z_top", assigned49.clone())?;
            let assigned50 = {
                let mut s = Vec::new();
                s.push(e.get("r_inner")?);
                s.push(e.get("r_outer")?);
                Val::tuple(s)
            };
            e.set("ring_r_range", assigned50.clone())?;
            let assigned51 = {
                let mut s = Vec::new();
                s.push(e.get("z_bottom")?);
                s.push(e.get("z_top")?);
                Val::tuple(s)
            };
            e.set("ring_z_range", assigned51.clone())?;
            let assigned52 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("r_inner")?,
                    e.get("slot_radial_margin")?,
                )?);
                s.push(binary(
                    "add",
                    e.get("r_outer")?,
                    e.get("slot_radial_margin")?,
                )?);
                Val::tuple(s)
            };
            e.set("slot_r_range", assigned52.clone())?;
            let assigned53 = {
                let fun56 = e.get("revolve_rect")?;
                let mut args54 = Vec::new();
                let mut kw55 = Vec::new();
                args54.push(e.get("ring_r_range")?);
                args54.push(e.get("ring_z_range")?);
                fun56.call(args54, kw55)?
            };
            e.set("ring", assigned53.clone())?;
            let assigned57 = binary("truediv", Val::Int(360i64), e.get("slot_count")?)?;
            e.set("slot_spacing_angle", assigned57.clone())?;
            let assigned58 = {
                let fun61 = e.get("revolve_rect")?;
                let mut args59 = Vec::new();
                let mut kw60 = Vec::new();
                args59.push(e.get("slot_r_range")?);
                args59.push(e.get("ring_z_range")?);
                args59.push(e.get("slot_angular_width")?);
                fun61.call(args59, kw60)?
            };
            e.set("slot_template", assigned58.clone())?;
            for item62 in {
                let fun75 = e.get("range")?;
                let mut args73 = Vec::new();
                let mut kw74 = Vec::new();
                args73.push(e.get("slot_count")?);
                fun75.call(args73, kw74)?
            }
            .iter()?
            {
                e.set("i", item62)?;
                let assigned63 = binary(
                    "add",
                    binary(
                        "mul",
                        e.get("slot_spacing_angle")?,
                        binary("add", e.get("i")?, Val::Float(0.5f64))?,
                    )?,
                    e.get("slot_clock")?,
                )?;
                e.set("slot_center_angle", assigned63.clone())?;
                let assigned64 = binary(
                    "sub",
                    e.get("slot_center_angle")?,
                    binary("truediv", e.get("slot_angular_width")?, Val::Int(2i64))?,
                )?;
                e.set("slot_start_angle", assigned64.clone())?;
                let assigned65 = {
                    let fun68 = e.get("slot_template")?.attr("rotate")?;
                    let mut args66 = Vec::new();
                    let mut kw67 = Vec::new();
                    args66.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    args66.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    });
                    args66.push(e.get("slot_start_angle")?);
                    fun68.call(args66, kw67)?
                };
                e.set("slot", assigned65.clone())?;
                let assigned69 = {
                    let fun72 = e.get("ring")?.attr("cut")?;
                    let mut args70 = Vec::new();
                    let mut kw71 = Vec::new();
                    args70.push(e.get("slot")?);
                    fun72.call(args70, kw71)?
                };
                e.set("ring", assigned69.clone())?;
            }
            return Ok(e.get("ring")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
