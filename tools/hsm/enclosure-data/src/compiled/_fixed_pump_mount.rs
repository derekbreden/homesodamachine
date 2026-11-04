//! Integral pump inverse, roof stock and underside-installed lower retainer.
//!
//! The enclosure module supplies the machine frame and the fitted pump profiles.
//! This module reads its declared Box without realizing another enclosure piece.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let assigned1 = Val::Float(2.0f64);
    e.set("WING_THICK", assigned1.clone())?;
    let assigned2 = Val::Float(22.25f64);
    e.set("WING_LENGTH", assigned2.clone())?;
    let assigned3 = Val::Float(1.5f64);
    e.set("ROOT_RADIUS", assigned3.clone())?;
    let assigned4 = Val::Float(2.6f64);
    e.set("CATCH_OVERLAP", assigned4.clone())?;
    let assigned5 = Val::Float(0.4f64);
    e.set("CATCH_AIR", assigned5.clone())?;
    let assigned6 = Val::Float(4.6f64);
    e.set("LEAD_RISE", assigned6.clone())?;
    let assigned7 = Val::Float(5.0f64);
    e.set("PRY_WIDTH", assigned7.clone())?;
    let assigned8 = Val::Float(0.35f64);
    e.set("RELAXED_SPREAD", assigned8.clone())?;
    let assigned9 = Val::Float(0.1f64);
    e.set("SEATED_SPREAD", assigned9.clone())?;
    let assigned10 = Val::Float(11.0f64);
    e.set("SHARED_HALF_SPAN", assigned10.clone())?;
    let assigned11 = Val::Float(6.0f64);
    e.set("INTERNAL_WIRE_HALF_SPAN", assigned11.clone())?;
    let assigned12 = Val::Float(9.0f64);
    e.set("DISPLAY_LINK_HALF_SPAN", assigned12.clone())?;
    let assigned13 = binary(
        "add",
        Val::Float(6.35f64),
        binary("mul", Val::Float(2.0f64), Val::Float(0.25f64))?,
    )?;
    e.set("TUBE_GATE_WIDTH", assigned13.clone())?;
    // datums
    e.set("datums",{let params=vec![("e".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned14=e.get("box")?.attr("pack")?.attr("pump_trays")?;e.set("trays",assigned14.clone())?;
let assigned15=binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun18=e.get("min")?;let mut args16=Vec::new();let mut kw17=Vec::new();args16.push({let e=e.child();let out19=Val::list(vec![]);for item20 in e.get("trays")?.iter()? {let unpack21=unpack(item20,3)?;e.set("_cx",unpack21[0].clone())?;e.set("_cy",unpack21[1].clone())?;e.set("cz",unpack21[2].clone())?;out19.attr("append")?.call(vec![e.get("cz")?],vec![])?;}out19});fun18.call(args16,kw17)?}},e.get("e")?.attr("_interface")?.attr("pump_seated_drop")?)?;e.set("flange",assigned15.clone())?;
let assigned22=binary("sub",e.get("e")?.attr("front_top_flank_t")?,e.get("e")?.attr("wall")?)?;e.set("grown",assigned22.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun25=e.get("dict")?;let mut args23=Vec::new();let mut kw24=Vec::new();kw24.push(("flange_z".into(),e.get("flange")?));kw24.push(("bearing_z".into(),binary("add",e.get("flange")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun28=e.get("e")?.attr("fits")?.attr("clearance")?;let mut args26=Vec::new();let mut kw27=Vec::new();kw27.push(("supported".into(),Val::Bool(true)));fun28.call(args26,kw27)?}})?));kw24.push(("retainer_top_z".into(),binary("sub",e.get("flange")?,e.get("e")?.attr("fits")?.attr("running")?)?));kw24.push(("bottom_z".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun31=e.get("e")?.attr("bay_floor_z")?;let mut args29=Vec::new();let mut kw30=Vec::new();args29.push(e.get("trays")?);fun31.call(args29,kw30)?}}.get(Val::Int(1i64))?));kw24.push(("x0".into(),binary("add",binary("add",e.get("box")?.attr("inner")?.get(Val::Int(0i64))?,e.get("grown")?)?,e.get("e")?.attr("fits")?.attr("running")?)?));kw24.push(("x1".into(),binary("sub",binary("sub",e.get("box")?.attr("inner")?.get(Val::Int(1i64))?,e.get("grown")?)?,e.get("e")?.attr("fits")?.attr("running")?)?));kw24.push(("y0".into(),binary("add",e.get("e")?.attr("front_plane_y")?,e.get("e")?.attr("fits")?.attr("running")?)?));kw24.push(("y1".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun34=e.get("e")?.attr("pump_cartridge_aft_y")?;let mut args32=Vec::new();let mut kw33=Vec::new();args32.push(e.get("trays")?);args32.push(e.get("box")?.attr("pack")?.attr("collet_plate")?);fun34.call(args32,kw33)?}}));kw24.push(("head_y".into(),binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun37=e.get("sum")?;let mut args35=Vec::new();let mut kw36=Vec::new();args35.push({let e=e.child();let out38=Val::list(vec![]);for item39 in e.get("trays")?.iter()? {let unpack40=unpack(item39,3)?;e.set("_cx",unpack40[0].clone())?;e.set("cy",unpack40[1].clone())?;e.set("_cz",unpack40[2].clone())?;out38.attr("append")?.call(vec![e.get("cy")?],vec![])?;}out38});fun37.call(args35,kw36)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun43=e.get("len")?;let mut args41=Vec::new();let mut kw42=Vec::new();args41.push(e.get("trays")?);fun43.call(args41,kw42)?}})?));kw24.push(("motor_y".into(),binary("add",binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun46=e.get("sum")?;let mut args44=Vec::new();let mut kw45=Vec::new();args44.push({let e=e.child();let out47=Val::list(vec![]);for item48 in e.get("trays")?.iter()? {let unpack49=unpack(item48,3)?;e.set("_cx",unpack49[0].clone())?;e.set("cy",unpack49[1].clone())?;e.set("_cz",unpack49[2].clone())?;out47.attr("append")?.call(vec![e.get("cy")?],vec![])?;}out47});fun46.call(args44,kw45)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun52=e.get("len")?;let mut args50=Vec::new();let mut kw51=Vec::new();args50.push(e.get("trays")?);fun52.call(args50,kw51)?}})?,e.get("e")?.attr("_tray")?.attr("rear_axis_y_shift")?)?));fun25.call(args23,kw24)?}});
Ok(Val::None)})})?;
    // fasteners
    e.set("fasteners", {
        let params = vec![("e".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // hardware
    e.set("hardware", {
        let params = vec![("e".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // snap_datums
    e.set("snap_datums", {
        let params = vec![("e".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned53 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun56 = e.get("datums")?;
                    let mut args54 = Vec::new();
                    let mut kw55 = Vec::new();
                    args54.push(e.get("e")?);
                    args54.push(e.get("box")?);
                    fun56.call(args54, kw55)?
                }
            };
            e.set("d", assigned53.clone())?;
            let assigned57 = e.get("d")?.get(Val::Str("x1".into()))?;
            e.set("outer", assigned57.clone())?;
            let assigned58 = e.get("d")?.get(Val::Str("bottom_z".into()))?;
            e.set("floor", assigned58.clone())?;
            let assigned59 = binary(
                "truediv",
                binary(
                    "add",
                    e.get("d")?.get(Val::Str("y0".into()))?,
                    e.get("d")?.get(Val::Str("y1".into()))?,
                )?,
                Val::Float(2.0f64),
            )?;
            e.set("cy", assigned59.clone())?;
            let assigned60 = binary(
                "add",
                e.get("outer")?,
                e.get("e")?.attr("fits")?.attr("running")?,
            )?;
            e.set("edge", assigned60.clone())?;
            let assigned61 = binary(
                "sub",
                binary("add", e.get("edge")?, e.get("CATCH_OVERLAP")?)?,
                e.get("SEATED_SPREAD")?,
            )?;
            e.set("hook", assigned61.clone())?;
            let assigned62 = binary(
                "add",
                binary(
                    "sub",
                    binary("add", e.get("hook")?, e.get("RELAXED_SPREAD")?)?,
                    e.get("edge")?,
                )?,
                Val::Float(0.5f64),
            )?;
            e.set("inward", assigned62.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun65 = e.get("dict")?;
                    let mut args63 = Vec::new();
                    let mut kw64 = Vec::new();
                    kw64.push((
                        "carrier_inner_x".into(),
                        binary(
                            "sub",
                            binary("sub", e.get("outer")?, e.get("WING_THICK")?)?,
                            e.get("inward")?,
                        )?,
                    ));
                    kw64.push((
                        "wing_inner_x".into(),
                        binary("sub", e.get("outer")?, e.get("WING_THICK")?)?,
                    ));
                    kw64.push(("wing_outer_x".into(), e.get("outer")?));
                    kw64.push(("hook_outer_x".into(), e.get("hook")?));
                    kw64.push((
                        "hook_ramp_z".into(),
                        binary("add", e.get("floor")?, e.get("LEAD_RISE")?)?,
                    ));
                    kw64.push((
                        "root_z".into(),
                        binary("add", e.get("floor")?, e.get("WING_LENGTH")?)?,
                    ));
                    kw64.push(("floor_z".into(), e.get("floor")?));
                    kw64.push((
                        "receiver_floor_z".into(),
                        binary("sub", e.get("floor")?, e.get("CATCH_AIR")?)?,
                    ));
                    kw64.push(("receiver_inner_x".into(), e.get("edge")?));
                    kw64.push((
                        "receiver_back_x".into(),
                        binary("add", e.get("hook")?, e.get("SEATED_SPREAD")?)?,
                    ));
                    kw64.push((
                        "receiver_outer_x".into(),
                        e.get("box")?.attr("outer")?.get(Val::Int(1i64))?,
                    ));
                    kw64.push((
                        "receiver_y0".into(),
                        binary(
                            "sub",
                            e.get("d")?.get(Val::Str("y0".into()))?,
                            e.get("e")?.attr("fits")?.attr("running")?,
                        )?,
                    ));
                    kw64.push((
                        "receiver_y1".into(),
                        binary(
                            "add",
                            e.get("d")?.get(Val::Str("y1".into()))?,
                            e.get("e")?.attr("fits")?.attr("running")?,
                        )?,
                    ));
                    kw64.push((
                        "receiver_z0".into(),
                        binary(
                            "add",
                            e.get("e")?.attr("z_seam")?,
                            e.get("e")?.attr("fits")?.attr("running")?,
                        )?,
                    ));
                    kw64.push((
                        "receiver_z1".into(),
                        binary(
                            "add",
                            binary("add", e.get("floor")?, e.get("WING_LENGTH")?)?,
                            binary("mul", Val::Float(3.0f64), e.get("e")?.attr("wall")?)?,
                        )?,
                    ));
                    kw64.push((
                        "receiver_roof_z".into(),
                        binary(
                            "add",
                            binary("add", e.get("floor")?, e.get("LEAD_RISE")?)?,
                            binary(
                                "mul",
                                Val::Float(2.0f64),
                                e.get("e")?.attr("fits")?.attr("running")?,
                            )?,
                        )?,
                    ));
                    kw64.push((
                        "port_inner_x".into(),
                        binary(
                            "add",
                            e.get("outer")?,
                            e.get("e")?.attr("fits")?.attr("running")?,
                        )?,
                    ));
                    kw64.push((
                        "port_outer_x".into(),
                        binary(
                            "sub",
                            e.get("box")?.attr("outer")?.get(Val::Int(1i64))?,
                            e.get("e")?.attr("wall")?,
                        )?,
                    ));
                    kw64.push((
                        "port_y0".into(),
                        binary(
                            "sub",
                            e.get("cy")?,
                            binary("truediv", e.get("PRY_WIDTH")?, Val::Float(2.0f64))?,
                        )?,
                    ));
                    kw64.push((
                        "port_y1".into(),
                        binary(
                            "add",
                            e.get("cy")?,
                            binary("truediv", e.get("PRY_WIDTH")?, Val::Float(2.0f64))?,
                        )?,
                    ));
                    kw64.push((
                        "port_z0".into(),
                        binary("sub", e.get("floor")?, Val::Float(5.0f64))?,
                    ));
                    fun65.call(args63, kw64)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // snap_receivers
    e.set("snap_receivers",{let params=vec![("e".into(),None,false),("box".into(),None,false),("piece".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned66={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun69=e.get("snap_datums")?;let mut args67=Vec::new();let mut kw68=Vec::new();args67.push(e.get("e")?);args67.push(e.get("box")?);fun69.call(args67,kw68)?}};e.set("d",assigned66.clone())?;
for item70 in {let mut s=Vec::new();s.push(unary("neg",Val::Float(1.0f64))?);s.push(Val::Float(1.0f64));Val::tuple(s)}.iter()? {
e.set("side",item70)?;let assigned71={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun74=e.get("sorted")?;let mut args72=Vec::new();let mut kw73=Vec::new();args72.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("receiver_inner_x".into()))?)?);s.push(binary("mul",e.get("side")?,binary("add",e.get("d")?.get(Val::Str("receiver_outer_x".into()))?,Val::Float(0.5f64))?)?);Val::tuple(s)});fun74.call(args72,kw73)?}};let unpack75=unpack(assigned71.clone(),2)?;e.set("x0",unpack75[0].clone())?;e.set("x1",unpack75[1].clone())?;
let assigned76={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun79=e.get("e")?.attr("_ybox")?;let mut args77=Vec::new();let mut kw78=Vec::new();args77.push(e.get("x0")?);args77.push(e.get("x1")?);args77.push(e.get("d")?.get(Val::Str("receiver_y0".into()))?);args77.push(e.get("d")?.get(Val::Str("receiver_y1".into()))?);args77.push(e.get("d")?.get(Val::Str("receiver_z0".into()))?);args77.push(e.get("d")?.get(Val::Str("receiver_z1".into()))?);fun79.call(args77,kw78)?}};e.set("band",assigned76.clone())?;
let assigned80={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun83=e.get("band")?.attr("intersect")?;let mut args81=Vec::new();let mut kw82=Vec::new();args81.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun86=e.get("e")?.attr("_rounded_outer")?;let mut args84=Vec::new();let mut kw85=Vec::new();args84.push(e.get("box")?.attr("outer")?);fun86.call(args84,kw85)?}});fun83.call(args81,kw82)?}};e.set("stock",assigned80.clone())?;
let assigned87=binary("sub",e.get("d")?.get(Val::Str("receiver_back_x".into()))?,e.get("d")?.get(Val::Str("receiver_inner_x".into()))?)?;e.set("reach",assigned87.clone())?;
let assigned88={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun91=e.get("e")?.attr("_xz_prism")?;let mut args89=Vec::new();let mut kw90=Vec::new();args89.push(e.get("d")?.get(Val::Str("receiver_y0".into()))?);args89.push(e.get("d")?.get(Val::Str("receiver_y1".into()))?);args89.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("receiver_inner_x".into()))?)?);s.push(e.get("d")?.get(Val::Str("receiver_floor_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("receiver_back_x".into()))?)?);s.push(e.get("d")?.get(Val::Str("receiver_floor_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("receiver_back_x".into()))?)?);s.push(e.get("d")?.get(Val::Str("receiver_roof_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("receiver_inner_x".into()))?)?);s.push(binary("add",e.get("d")?.get(Val::Str("receiver_roof_z".into()))?,e.get("reach")?)?);Val::tuple(s)});Val::list(s)});fun91.call(args89,kw90)?}};e.set("pocket",assigned88.clone())?;
let assigned92={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun95=e.get("sorted")?;let mut args93=Vec::new();let mut kw94=Vec::new();args93.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("port_inner_x".into()))?)?);s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("port_outer_x".into()))?)?);Val::tuple(s)});fun95.call(args93,kw94)?}};let unpack96=unpack(assigned92.clone(),2)?;e.set("x0",unpack96[0].clone())?;e.set("x1",unpack96[1].clone())?;
let assigned97={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun100=e.get("e")?.attr("_ybox")?;let mut args98=Vec::new();let mut kw99=Vec::new();args98.push(e.get("x0")?);args98.push(e.get("x1")?);args98.push(e.get("d")?.get(Val::Str("port_y0".into()))?);args98.push(e.get("d")?.get(Val::Str("port_y1".into()))?);args98.push(e.get("d")?.get(Val::Str("port_z0".into()))?);args98.push(e.get("d")?.get(Val::Str("receiver_roof_z".into()))?);fun100.call(args98,kw99)?}};e.set("port",assigned97.clone())?;
let assigned101=binary("sub",e.get("d")?.get(Val::Str("port_outer_x".into()))?,e.get("d")?.get(Val::Str("receiver_back_x".into()))?)?;e.set("roof_drop",assigned101.clone())?;
let assigned102={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun105=e.get("e")?.attr("_xz_prism")?;let mut args103=Vec::new();let mut kw104=Vec::new();args103.push(e.get("d")?.get(Val::Str("port_y0".into()))?);args103.push(e.get("d")?.get(Val::Str("port_y1".into()))?);args103.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("receiver_back_x".into()))?)?);s.push(e.get("d")?.get(Val::Str("receiver_roof_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("port_outer_x".into()))?)?);s.push(e.get("d")?.get(Val::Str("receiver_roof_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("d")?.get(Val::Str("port_outer_x".into()))?)?);s.push(binary("sub",e.get("d")?.get(Val::Str("receiver_roof_z".into()))?,e.get("roof_drop")?)?);Val::tuple(s)});Val::list(s)});fun105.call(args103,kw104)?}};e.set("corbel",assigned102.clone())?;
let assigned106={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun109={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun112={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun115={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun118=e.get("stock")?.attr("cut")?;let mut args116=Vec::new();let mut kw117=Vec::new();args116.push(e.get("pocket")?);fun118.call(args116,kw117)?}}.attr("cut")?;let mut args113=Vec::new();let mut kw114=Vec::new();args113.push(e.get("port")?);fun115.call(args113,kw114)?}}.attr("fuse")?;let mut args110=Vec::new();let mut kw111=Vec::new();args110.push(e.get("corbel")?);fun112.call(args110,kw111)?}}.attr("clean")?;let mut args107=Vec::new();let mut kw108=Vec::new();fun109.call(args107,kw108)?}};e.set("receiver",assigned106.clone())?;
let assigned119={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun122={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun125=e.get("piece")?.attr("cut")?;let mut args123=Vec::new();let mut kw124=Vec::new();args123.push(e.get("band")?);fun125.call(args123,kw124)?}}.attr("fuse")?;let mut args120=Vec::new();let mut kw121=Vec::new();args120.push(e.get("receiver")?);fun122.call(args120,kw121)?}};e.set("piece",assigned119.clone())?;
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun128=e.get("piece")?.attr("clean")?;let mut args126=Vec::new();let mut kw127=Vec::new();fun128.call(args126,kw127)?}});
Ok(Val::None)})})?;
    // stock
    e.set("stock", {
        let params = vec![("e".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned129 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun132 = e.get("datums")?;
                    let mut args130 = Vec::new();
                    let mut kw131 = Vec::new();
                    args130.push(e.get("e")?);
                    args130.push(e.get("box")?);
                    fun132.call(args130, kw131)?
                }
            };
            e.set("d", assigned129.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun135 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun138 = e.get("e")?.attr("_ybox")?;
                            let mut args136 = Vec::new();
                            let mut kw137 = Vec::new();
                            args136.push(binary(
                                "sub",
                                e.get("box")?.attr("inner")?.get(Val::Int(0i64))?,
                                Val::Float(1.0f64),
                            )?);
                            args136.push(binary(
                                "add",
                                e.get("box")?.attr("inner")?.get(Val::Int(1i64))?,
                                Val::Float(1.0f64),
                            )?);
                            args136.push(binary(
                                "sub",
                                e.get("e")?.attr("front_plane_y")?,
                                Val::Float(1.0f64),
                            )?);
                            args136.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                    line!(),
                                );
                                {
                                    let fun141 = e.get("e")?.attr("housing_back_y")?;
                                    let mut args139 = Vec::new();
                                    let mut kw140 = Vec::new();
                                    args139.push(e.get("box")?.attr("outer")?);
                                    fun141.call(args139, kw140)?
                                }
                            });
                            args136.push(e.get("d")?.get(Val::Str("bearing_z".into()))?);
                            args136.push(binary(
                                "add",
                                e.get("box")?.attr("outer")?.get(Val::Int(5i64))?,
                                Val::Float(1.0f64),
                            )?);
                            fun138.call(args136, kw137)?
                        }
                    }
                    .attr("intersect")?;
                    let mut args133 = Vec::new();
                    let mut kw134 = Vec::new();
                    args133.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun144 = e.get("e")?.attr("_rounded_outer")?;
                            let mut args142 = Vec::new();
                            let mut kw143 = Vec::new();
                            args142.push(e.get("box")?.attr("outer")?);
                            fun144.call(args142, kw143)?
                        }
                    });
                    fun135.call(args133, kw134)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // loading_opening
    e.set("loading_opening", {
        let params = vec![("e".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned145 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun148 = e.get("datums")?;
                    let mut args146 = Vec::new();
                    let mut kw147 = Vec::new();
                    args146.push(e.get("e")?);
                    args146.push(e.get("box")?);
                    fun148.call(args146, kw147)?
                }
            };
            e.set("d", assigned145.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun151 = e.get("e")?.attr("_ybox")?;
                    let mut args149 = Vec::new();
                    let mut kw150 = Vec::new();
                    args149.push(binary(
                        "sub",
                        e.get("d")?.get(Val::Str("x0".into()))?,
                        e.get("e")?.attr("fits")?.attr("running")?,
                    )?);
                    args149.push(binary(
                        "add",
                        e.get("d")?.get(Val::Str("x1".into()))?,
                        e.get("e")?.attr("fits")?.attr("running")?,
                    )?);
                    args149.push(binary(
                        "sub",
                        e.get("d")?.get(Val::Str("y0".into()))?,
                        e.get("e")?.attr("fits")?.attr("running")?,
                    )?);
                    args149.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun154 = e.get("e")?.attr("bay_back_y")?;
                            let mut args152 = Vec::new();
                            let mut kw153 = Vec::new();
                            args152.push(e.get("box")?.attr("pack")?.attr("collet_plate")?);
                            fun154.call(args152, kw153)?
                        }
                    });
                    args149.push(binary(
                        "sub",
                        e.get("e")?.attr("z_seam")?,
                        Val::Float(20.0f64),
                    )?);
                    args149.push(e.get("d")?.get(Val::Str("bearing_z".into()))?);
                    fun151.call(args149, kw150)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // wiring_passages
    e.set("wiring_passages",{let params=vec![("e".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned155={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun158=e.get("datums")?;let mut args156=Vec::new();let mut kw157=Vec::new();args156.push(e.get("e")?);args156.push(e.get("box")?);fun158.call(args156,kw157)?}};e.set("d",assigned155.clone())?;
let assigned159=e.get("d")?.get(Val::Str("motor_y".into()))?;e.set("cy",assigned159.clone())?;
let assigned160=binary("add",e.get("d")?.get(Val::Str("flange_z".into()))?,e.get("e")?.attr("_tray")?.attr("motor_crown")?)?;e.set("motor_end",assigned160.clone())?;
let assigned161=binary("add",e.get("motor_end")?,Val::Float(2.776f64))?;e.set("rear_z",assigned161.clone())?;
let assigned162=binary("add",e.get("rear_z")?,Val::Float(4.0f64))?;e.set("cross_z",assigned162.clone())?;
let assigned163=binary("add",e.get("box")?.attr("pack")?.attr("collet_plate")?.get(Val::Str("wall_aft_y".into()))?,Val::Float(0.664f64))?;e.set("rear_y",assigned163.clone())?;
let assigned164={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun167=e.get("e")?.attr("_display_point")?;let mut args165=Vec::new();let mut kw166=Vec::new();args165.push(e.get("box")?.attr("outer")?);args165.push({let mut s=Vec::new();s.push(Val::Float(0.5f64));s.push(unary("neg",Val::Float(1.0f64))?);s.push(unary("neg",binary("sub",binary("add",e.get("e")?.attr("display_facet_thickness")?,e.get("e")?.attr("display_pcb_cut_through")?)?,Val::Float(1.0f64))?)?);Val::tuple(s)});fun167.call(args165,kw166)?}};e.set("back",assigned164.clone())?;
let assigned168={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun171=e.get("e")?.attr("_facet_geom")?;let mut args169=Vec::new();let mut kw170=Vec::new();args169.push(e.get("box")?.attr("outer")?);fun171.call(args169,kw170)?}}.get(Val::Int(1i64))?;e.set("normal",assigned168.clone())?;
let assigned172={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun175=e.get("tuple")?;let mut args173=Vec::new();let mut kw174=Vec::new();args173.push({let e=e.child();let out176=Val::list(vec![]);for item177 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun180=e.get("zip")?;let mut args178=Vec::new();let mut kw179=Vec::new();args178.push(e.get("back")?);args178.push(e.get("normal")?);fun180.call(args178,kw179)?}}.iter()? {let unpack181=unpack(item177,2)?;e.set("p",unpack181[0].clone())?;e.set("n",unpack181[1].clone())?;out176.attr("append")?.call(vec![binary("sub",e.get("p")?,binary("mul",e.get("n")?,Val::Float(6.0f64))?)?],vec![])?;}out176});fun175.call(args173,kw174)?}};e.set("link",assigned172.clone())?;
return Ok({let d=Val::dict(vec![]);d.set(Val::Str("front-top-electrical".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun184=e.get("dict")?;let mut args182=Vec::new();let mut kw183=Vec::new();kw183.push(("points_mm".into(),{let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(e.get("rear_y")?);s.push(e.get("rear_z")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(e.get("cy")?);s.push(e.get("rear_z")?);Val::tuple(s)});Val::list(s)}));kw183.push(("diamond_half_span_mm".into(),e.get("SHARED_HALF_SPAN")?));fun184.call(args182,kw183)?}})?;d.set(Val::Str("front-top-pump-cross".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun187=e.get("dict")?;let mut args185=Vec::new();let mut kw186=Vec::new();kw186.push(("points_mm".into(),{let mut s=Vec::new();s.push({let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun190=e.get("min")?;let mut args188=Vec::new();let mut kw189=Vec::new();args188.push({let e=e.child();let out191=Val::list(vec![]);for item192 in e.get("box")?.attr("pack")?.attr("pump_trays")?.iter()? {let unpack193=unpack(item192,3)?;e.set("x",unpack193[0].clone())?;e.set("_y",unpack193[1].clone())?;e.set("_z",unpack193[2].clone())?;out191.attr("append")?.call(vec![e.get("x")?],vec![])?;}out191});fun190.call(args188,kw189)?}});s.push(e.get("cy")?);s.push(e.get("cross_z")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(e.get("cy")?);s.push(e.get("cross_z")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun196=e.get("max")?;let mut args194=Vec::new();let mut kw195=Vec::new();args194.push({let e=e.child();let out197=Val::list(vec![]);for item198 in e.get("box")?.attr("pack")?.attr("pump_trays")?.iter()? {let unpack199=unpack(item198,3)?;e.set("x",unpack199[0].clone())?;e.set("_y",unpack199[1].clone())?;e.set("_z",unpack199[2].clone())?;out197.attr("append")?.call(vec![e.get("x")?],vec![])?;}out197});fun196.call(args194,kw195)?}});s.push(e.get("cy")?);s.push(e.get("cross_z")?);Val::tuple(s)});Val::list(s)}));kw186.push(("roof_half_span_mm".into(),e.get("INTERNAL_WIRE_HALF_SPAN")?));kw186.push(("floor_z_mm".into(),binary("sub",e.get("motor_end")?,e.get("e")?.attr("wall")?)?));fun187.call(args185,kw186)?}})?;d.set(Val::Str("front-top-display-chimney".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun202=e.get("dict")?;let mut args200=Vec::new();let mut kw201=Vec::new();kw201.push(("points_mm".into(),{let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(79.0f64));s.push(e.get("cross_z")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(78.0f64));s.push(Val::Float(321.0f64));Val::tuple(s)});Val::list(s)}));kw201.push(("bounds_mm".into(),{let mut s=Vec::new();s.push(unary("neg",Val::Float(10.0f64))?);s.push(Val::Float(10.0f64));s.push(Val::Float(72.0f64));s.push(Val::Float(84.0f64));s.push(e.get("rear_z")?);s.push(Val::Float(334.0f64));Val::list(s)}));fun202.call(args200,kw201)?}})?;d.set(Val::Str("front-top-display-link".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun205=e.get("dict")?;let mut args203=Vec::new();let mut kw204=Vec::new();kw204.push(("points_mm".into(),{let mut s=Vec::new();s.push(e.get("link")?);s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(78.0f64));s.push(Val::Float(321.0f64));Val::tuple(s)});Val::list(s)}));kw204.push(("terminal_entry_mm".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun208=e.get("tuple")?;let mut args206=Vec::new();let mut kw207=Vec::new();args206.push({let e=e.child();let out209=Val::list(vec![]);for item210 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun213=e.get("zip")?;let mut args211=Vec::new();let mut kw212=Vec::new();args211.push(e.get("back")?);args211.push(e.get("normal")?);fun213.call(args211,kw212)?}}.iter()? {let unpack214=unpack(item210,2)?;e.set("p",unpack214[0].clone())?;e.set("n",unpack214[1].clone())?;out209.attr("append")?.call(vec![binary("add",e.get("p")?,binary("mul",e.get("n")?,Val::Float(2.0f64))?)?],vec![])?;}out209});fun208.call(args206,kw207)?}}));kw204.push(("diamond_half_span_mm".into(),e.get("DISPLAY_LINK_HALF_SPAN")?));fun205.call(args203,kw204)?}})?;d});
Ok(Val::None)})})?;
    // _diamond_y
    e.set("_diamond_y", {
        let params = vec![
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("z".into(), None, false),
            ("r".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun217 = e.get("cq")?.attr("Wire")?.attr("makePolygon")?;
                    let mut args215 = Vec::new();
                    let mut kw216 = Vec::new();
                    args215.push({
                        let mut s = Vec::new();
                        s.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                line!(),
                            );
                            {
                                let fun220 = e.get("cq")?.attr("Vector")?;
                                let mut args218 = Vec::new();
                                let mut kw219 = Vec::new();
                                args218.push(binary("sub", e.get("x")?, e.get("r")?)?);
                                args218.push(e.get("y")?);
                                args218.push(e.get("z")?);
                                fun220.call(args218, kw219)?
                            }
                        });
                        s.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                line!(),
                            );
                            {
                                let fun223 = e.get("cq")?.attr("Vector")?;
                                let mut args221 = Vec::new();
                                let mut kw222 = Vec::new();
                                args221.push(e.get("x")?);
                                args221.push(e.get("y")?);
                                args221.push(binary("add", e.get("z")?, e.get("r")?)?);
                                fun223.call(args221, kw222)?
                            }
                        });
                        s.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                line!(),
                            );
                            {
                                let fun226 = e.get("cq")?.attr("Vector")?;
                                let mut args224 = Vec::new();
                                let mut kw225 = Vec::new();
                                args224.push(binary("add", e.get("x")?, e.get("r")?)?);
                                args224.push(e.get("y")?);
                                args224.push(e.get("z")?);
                                fun226.call(args224, kw225)?
                            }
                        });
                        s.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                line!(),
                            );
                            {
                                let fun229 = e.get("cq")?.attr("Vector")?;
                                let mut args227 = Vec::new();
                                let mut kw228 = Vec::new();
                                args227.push(e.get("x")?);
                                args227.push(e.get("y")?);
                                args227.push(binary("sub", e.get("z")?, e.get("r")?)?);
                                fun229.call(args227, kw228)?
                            }
                        });
                        Val::list(s)
                    });
                    kw216.push(("close".into(), Val::Bool(true)));
                    fun217.call(args215, kw216)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _corridor_profile
    e.set("_corridor_profile",{let params=vec![("vertices".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned230={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun233=e.get("sorted")?;let mut args231=Vec::new();let mut kw232=Vec::new();args231.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun236=e.get("set")?;let mut args234=Vec::new();let mut kw235=Vec::new();args234.push({let e=e.child();let out237=Val::list(vec![]);for item238 in e.get("vertices")?.iter()? {e.set("p",item238)?;out237.attr("append")?.call(vec![{let mut s=Vec::new();s.push(e.get("p")?.get(Val::Int(1i64))?);s.push(e.get("p")?.get(Val::Int(2i64))?);Val::tuple(s)}],vec![])?;}out237});fun236.call(args234,kw235)?}});fun233.call(args231,kw232)?}};e.set("points",assigned230.clone())?;
// turn
e.set("turn",{let params=vec![("a".into(),None,false),("b".into(),None,false),("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok(binary("sub",binary("mul",binary("sub",e.get("b")?.get(Val::Int(0i64))?,e.get("a")?.get(Val::Int(0i64))?)?,binary("sub",e.get("c")?.get(Val::Int(1i64))?,e.get("a")?.get(Val::Int(1i64))?)?)?,binary("mul",binary("sub",e.get("b")?.get(Val::Int(1i64))?,e.get("a")?.get(Val::Int(1i64))?)?,binary("sub",e.get("c")?.get(Val::Int(0i64))?,e.get("a")?.get(Val::Int(0i64))?)?)?)?);
Ok(Val::None)})})?;
// chain
e.set("chain",{let params=vec![("sequence".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned239={let mut s=Vec::new();Val::list(s)};e.set("result",assigned239.clone())?;
for item240 in e.get("sequence")?.iter()? {
e.set("point",item240)?;while {let v246={let v250={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun249=e.get("len")?;let mut args247=Vec::new();let mut kw248=Vec::new();args247.push(e.get("result")?);fun249.call(args247,kw248)?}};let v251=Val::Int(1i64);Val::Bool(compare("gt",v250.clone(),v251.clone())?.truthy()?)};if v246.truthy()? {{let v244={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun243=e.get("turn")?;let mut args241=Vec::new();let mut kw242=Vec::new();args241.push(e.get("result")?.get(unary("neg",Val::Int(2i64))?)?);args241.push(e.get("result")?.get(unary("neg",Val::Int(1i64))?)?);args241.push(e.get("point")?);fun243.call(args241,kw242)?}};let v245=Val::Float(1e-09f64);Val::Bool(compare("le",v244.clone(),v245.clone())?.truthy()?)}} else {v246}}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun254=e.get("result")?.attr("pop")?;let mut args252=Vec::new();let mut kw253=Vec::new();fun254.call(args252,kw253)?}};
}
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun257=e.get("result")?.attr("append")?;let mut args255=Vec::new();let mut kw256=Vec::new();args255.push(e.get("point")?);fun257.call(args255,kw256)?}};
}
return Ok(e.get("result")?);
Ok(Val::None)})})?;
let assigned258=binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun261=e.get("chain")?;let mut args259=Vec::new();let mut kw260=Vec::new();args259.push(e.get("points")?);fun261.call(args259,kw260)?}}.get(Val::Slice{start:None,stop:Some(unary("neg",Val::Int(1i64))?.integer()?),step:1})?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun264=e.get("chain")?;let mut args262=Vec::new();let mut kw263=Vec::new();args262.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun267=e.get("reversed")?;let mut args265=Vec::new();let mut kw266=Vec::new();args265.push(e.get("points")?);fun267.call(args265,kw266)?}});fun264.call(args262,kw263)?}}.get(Val::Slice{start:None,stop:Some(unary("neg",Val::Int(1i64))?.integer()?),step:1})?)?;e.set("outline",assigned258.clone())?;
return Ok({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun270=e.get("min")?;let mut args268=Vec::new();let mut kw269=Vec::new();args268.push({let e=e.child();let out271=Val::list(vec![]);for item272 in e.get("vertices")?.iter()? {e.set("p",item272)?;out271.attr("append")?.call(vec![e.get("p")?.get(Val::Int(0i64))?],vec![])?;}out271});fun270.call(args268,kw269)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun275=e.get("max")?;let mut args273=Vec::new();let mut kw274=Vec::new();args273.push({let e=e.child();let out276=Val::list(vec![]);for item277 in e.get("vertices")?.iter()? {e.set("p",item277)?;out276.attr("append")?.call(vec![e.get("p")?.get(Val::Int(0i64))?],vec![])?;}out276});fun275.call(args273,kw274)?}});Val::tuple(s)});s.push(e.get("outline")?);Val::tuple(s)});
Ok(Val::None)})})?;
    // _convex_corridor
    e.set("_convex_corridor",{let params=vec![("e".into(),None,false),("shapes".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned278={let e=e.child();let out279=Val::list(vec![]);for item280 in e.get("shapes")?.iter()? {e.set("shape",item280)?;for item281 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun284=e.get("shape")?.attr("Vertices")?;let mut args282=Vec::new();let mut kw283=Vec::new();fun284.call(args282,kw283)?}}.iter()? {e.set("vertex",item281)?;out279.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun287={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun290=e.get("vertex")?.attr("Center")?;let mut args288=Vec::new();let mut kw289=Vec::new();fun290.call(args288,kw289)?}}.attr("toTuple")?;let mut args285=Vec::new();let mut kw286=Vec::new();fun287.call(args285,kw286)?}}],vec![])?;}}out279};e.set("vertices",assigned278.clone())?;
let assigned291={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun294=e.get("_corridor_profile")?;let mut args292=Vec::new();let mut kw293=Vec::new();args292.push(e.get("vertices")?);fun294.call(args292,kw293)?}};let unpack295=unpack(assigned291.clone(),2)?;e.set("span",unpack295[0].clone())?;e.set("outline",unpack295[1].clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun298=e.get("e")?.attr("_yz_prism")?;let mut args296=Vec::new();let mut kw297=Vec::new();args296.extend(e.get("span")?.iter()?);args296.push(e.get("outline")?);fun298.call(args296,kw297)?}});
Ok(Val::None)})})?;
    // wire_cuts
    e.set("wire_cuts",{let params=vec![("e".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned299={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun302=e.get("wiring_passages")?;let mut args300=Vec::new();let mut kw301=Vec::new();args300.push(e.get("e")?);args300.push(e.get("box")?);fun302.call(args300,kw301)?}};e.set("p",assigned299.clone())?;
let assigned303=e.get("p")?.get(Val::Str("front-top-electrical".into()))?;e.set("shared",assigned303.clone())?;
let assigned304=e.get("shared")?.get(Val::Str("points_mm".into()))?;let unpack305=unpack(assigned304.clone(),2)?;e.set("rear",unpack305[0].clone())?;e.set("fore",unpack305[1].clone())?;
let assigned306=e.get("shared")?.get(Val::Str("diamond_half_span_mm".into()))?;e.set("r",assigned306.clone())?;
let assigned307={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun310=e.get("cq")?.attr("Solid")?.attr("makeLoft")?;let mut args308=Vec::new();let mut kw309=Vec::new();args308.push({let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun313=e.get("_diamond_y")?;let mut args311=Vec::new();let mut kw312=Vec::new();args311.push(Val::Float(0.0f64));args311.push(e.get("fore")?.get(Val::Int(1i64))?);args311.push(e.get("rear")?.get(Val::Int(2i64))?);args311.push(e.get("r")?);fun313.call(args311,kw312)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun316=e.get("_diamond_y")?;let mut args314=Vec::new();let mut kw315=Vec::new();args314.push(Val::Float(0.0f64));args314.push(e.get("rear")?.get(Val::Int(1i64))?);args314.push(e.get("rear")?.get(Val::Int(2i64))?);args314.push(e.get("r")?);fun316.call(args314,kw315)?}});Val::list(s)});args308.push(Val::Bool(true));fun310.call(args308,kw309)?}});Val::list(s)};e.set("out",assigned307.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun319=e.get("out")?.attr("append")?;let mut args317=Vec::new();let mut kw318=Vec::new();args317.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun322=e.get("e")?.attr("_ybox")?;let mut args320=Vec::new();let mut kw321=Vec::new();args320.push(unary("neg",e.get("r")?)?);args320.push(e.get("r")?);args320.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun325=e.get("e")?.attr("housing_back_y")?;let mut args323=Vec::new();let mut kw324=Vec::new();args323.push(e.get("box")?.attr("outer")?);fun325.call(args323,kw324)?}});args320.push(e.get("rear")?.get(Val::Int(1i64))?);args320.push(e.get("rear")?.get(Val::Int(2i64))?);args320.push(binary("add",e.get("box")?.attr("pump_bay")?.get(Val::Int(2i64))?,Val::Float(0.01f64))?);fun322.call(args320,kw321)?}});fun319.call(args317,kw318)?}};
let assigned326=e.get("p")?.get(Val::Str("front-top-pump-cross".into()))?;e.set("cross",assigned326.clone())?;
let assigned327=e.get("cross")?.get(Val::Str("points_mm".into()))?;let unpack328=unpack(assigned327.clone(),3)?;e.set("a",unpack328[0].clone())?;e.set("_mid",unpack328[1].clone())?;e.set("b",unpack328[2].clone())?;
let assigned329=e.get("cross")?.get(Val::Str("roof_half_span_mm".into()))?;e.set("r",assigned329.clone())?;
let assigned330=e.get("cross")?.get(Val::Str("floor_z_mm".into()))?;e.set("floor",assigned330.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun333=e.get("out")?.attr("append")?;let mut args331=Vec::new();let mut kw332=Vec::new();args331.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun336=e.get("e")?.attr("_yz_prism")?;let mut args334=Vec::new();let mut kw335=Vec::new();args334.push(e.get("a")?.get(Val::Int(0i64))?);args334.push(e.get("b")?.get(Val::Int(0i64))?);args334.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("sub",e.get("a")?.get(Val::Int(1i64))?,e.get("r")?)?);s.push(e.get("floor")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",e.get("a")?.get(Val::Int(1i64))?,e.get("r")?)?);s.push(e.get("floor")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",e.get("a")?.get(Val::Int(1i64))?,e.get("r")?)?);s.push(e.get("a")?.get(Val::Int(2i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("a")?.get(Val::Int(1i64))?);s.push(binary("add",e.get("a")?.get(Val::Int(2i64))?,e.get("r")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",e.get("a")?.get(Val::Int(1i64))?,e.get("r")?)?);s.push(e.get("a")?.get(Val::Int(2i64))?);Val::tuple(s)});Val::list(s)});fun336.call(args334,kw335)?}});fun333.call(args331,kw332)?}};
let assigned337={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun340=e.get("e")?.attr("_ybox")?;let mut args338=Vec::new();let mut kw339=Vec::new();args338.extend(e.get("p")?.get(Val::Str("front-top-display-chimney".into()))?.get(Val::Str("bounds_mm".into()))?.iter()?);fun340.call(args338,kw339)?}};e.set("chimney",assigned337.clone())?;
let assigned341=e.get("p")?.get(Val::Str("front-top-display-link".into()))?;e.set("link",assigned341.clone())?;
let assigned342=e.get("link")?.get(Val::Str("points_mm".into()))?;let unpack343=unpack(assigned342.clone(),2)?;e.set("a",unpack343[0].clone())?;e.set("b",unpack343[1].clone())?;
let assigned344=e.get("link")?.get(Val::Str("diamond_half_span_mm".into()))?;e.set("r",assigned344.clone())?;
let assigned345={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun348=e.get("e")?.attr("display_plane")?;let mut args346=Vec::new();let mut kw347=Vec::new();args346.push(e.get("box")?.attr("outer")?);fun348.call(args346,kw347)?}};e.set("plane",assigned345.clone())?;
let assigned349={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun352=e.get("_diamond_y")?;let mut args350=Vec::new();let mut kw351=Vec::new();args350.extend(e.get("link")?.get(Val::Str("terminal_entry_mm".into()))?.iter()?);args350.push(e.get("r")?);fun352.call(args350,kw351)?}};e.set("first",assigned349.clone())?;
let assigned353={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun356=e.get("_diamond_y")?;let mut args354=Vec::new();let mut kw355=Vec::new();args354.extend(e.get("a")?.iter()?);args354.push(e.get("r")?);fun356.call(args354,kw355)?}};e.set("inner",assigned353.clone())?;
let assigned357={let e=e.child();let out358=Val::list(vec![]);for item359 in {let mut s=Vec::new();s.push(e.get("first")?);s.push(e.get("inner")?);Val::tuple(s)}.iter()? {e.set("section",item359)?;for item360 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun363=e.get("section")?.attr("Vertices")?;let mut args361=Vec::new();let mut kw362=Vec::new();fun363.call(args361,kw362)?}}.iter()? {e.set("vertex",item360)?;out358.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun366={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun369=e.get("plane")?.attr("toLocalCoords")?;let mut args367=Vec::new();let mut kw368=Vec::new();args367.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun372=e.get("vertex")?.attr("Center")?;let mut args370=Vec::new();let mut kw371=Vec::new();fun372.call(args370,kw371)?}});fun369.call(args367,kw368)?}}.attr("toTuple")?;let mut args364=Vec::new();let mut kw365=Vec::new();fun366.call(args364,kw365)?}}],vec![])?;}}out358};e.set("points",assigned357.clone())?;
let assigned373={let e=e.child();let out374=Val::list(vec![]);for item375 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun378=e.get("range")?;let mut args376=Vec::new();let mut kw377=Vec::new();args376.push(Val::Int(3i64));fun378.call(args376,kw377)?}}.iter()? {e.set("axis",item375)?;for item379 in {let mut s=Vec::new();s.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun382=e.get("min")?;let mut args380=Vec::new();let mut kw381=Vec::new();args380.push({let e=e.child();let out383=Val::list(vec![]);for item384 in e.get("points")?.iter()? {e.set("point",item384)?;out383.attr("append")?.call(vec![e.get("point")?.get(e.get("axis")?)?],vec![])?;}out383});fun382.call(args380,kw381)?}},Val::Float(1.0f64))?);s.push(binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun387=e.get("max")?;let mut args385=Vec::new();let mut kw386=Vec::new();args385.push({let e=e.child();let out388=Val::list(vec![]);for item389 in e.get("points")?.iter()? {e.set("point",item389)?;out388.attr("append")?.call(vec![e.get("point")?.get(e.get("axis")?)?],vec![])?;}out388});fun387.call(args385,kw386)?}},Val::Float(1.0f64))?);Val::tuple(s)}.iter()? {e.set("value",item379)?;out374.attr("append")?.call(vec![e.get("value")?],vec![])?;}}out374};e.set("bounds",assigned373.clone())?;
let assigned390={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun393={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun396=e.get("e")?.attr("_ybox")?;let mut args394=Vec::new();let mut kw395=Vec::new();args394.extend(e.get("bounds")?.iter()?);fun396.call(args394,kw395)?}}.attr("moved")?;let mut args391=Vec::new();let mut kw392=Vec::new();args391.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun399=e.get("cq")?.attr("Location")?;let mut args397=Vec::new();let mut kw398=Vec::new();args397.push(e.get("plane")?);fun399.call(args397,kw398)?}});fun393.call(args391,kw392)?}};e.set("entry",assigned390.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun402=e.get("out")?.attr("append")?;let mut args400=Vec::new();let mut kw401=Vec::new();args400.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun405=e.get("_convex_corridor")?;let mut args403=Vec::new();let mut kw404=Vec::new();args403.push(e.get("e")?);args403.push({let mut s=Vec::new();s.push(e.get("entry")?);s.push(e.get("inner")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun408=e.get("_diamond_y")?;let mut args406=Vec::new();let mut kw407=Vec::new();args406.extend(e.get("b")?.iter()?);args406.push(e.get("r")?);fun408.call(args406,kw407)?}});s.push(e.get("chimney")?);Val::list(s)});fun405.call(args403,kw404)?}});fun402.call(args400,kw401)?}};
return Ok(e.get("out")?);
Ok(Val::None)})})?;
    // inverse_cuts
    e.set("inverse_cuts",{let params=vec![("e".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned409={let mut s=Vec::new();Val::list(s)};e.set("out",assigned409.clone())?;
for item410 in e.get("box")?.attr("pack")?.attr("pump_trays")?.iter()? {
let unpack411=unpack(item410,3)?;e.set("cx",unpack411[0].clone())?;e.set("cy",unpack411[1].clone())?;e.set("cz",unpack411[2].clone())?;let assigned412=binary("sub",e.get("cz")?,e.get("e")?.attr("_interface")?.attr("pump_seated_drop")?)?;e.set("flange",assigned412.clone())?;
let assigned413=binary("add",e.get("cy")?,e.get("e")?.attr("_tray")?.attr("rear_axis_y_shift")?)?;e.set("y",assigned413.clone())?;
let assigned414={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun417=e.get("e")?.attr("fits")?.attr("clearance")?;let mut args415=Vec::new();let mut kw416=Vec::new();kw416.push(("supported".into(),Val::Bool(true)));fun417.call(args415,kw416)?}};e.set("finish",assigned414.clone())?;
let assigned418={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun421=e.get("e")?.attr("_tray")?.attr("boss_room")?;let mut args419=Vec::new();let mut kw420=Vec::new();args419.push(e.get("e")?.attr("cap_boss_air")?);fun421.call(args419,kw420)?}};e.set("room",assigned418.clone())?;
let assigned422={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun425=e.get("room")?.attr("fuse")?;let mut args423=Vec::new();let mut kw424=Vec::new();args423.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun428=e.get("room")?.attr("translate")?;let mut args426=Vec::new();let mut kw427=Vec::new();args426.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(e.get("finish")?);Val::tuple(s)});fun428.call(args426,kw427)?}});fun425.call(args423,kw424)?}};e.set("room",assigned422.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun431=e.get("out")?.attr("append")?;let mut args429=Vec::new();let mut kw430=Vec::new();args429.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun434=e.get("room")?.attr("translate")?;let mut args432=Vec::new();let mut kw433=Vec::new();args432.push({let mut s=Vec::new();s.push(e.get("cx")?);s.push(e.get("y")?);s.push(e.get("flange")?);Val::tuple(s)});fun434.call(args432,kw433)?}});fun431.call(args429,kw430)?}};
let assigned435=binary("add",e.get("flange")?,e.get("e")?.attr("_tray")?.attr("motor_crown")?)?;e.set("motor_end",assigned435.clone())?;
let assigned436={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun439=e.get("e")?.attr("cap_terminal_crown_r")?;let mut args437=Vec::new();let mut kw438=Vec::new();args437.push(e.get("box")?);fun439.call(args437,kw438)?}};e.set("terminal_r",assigned436.clone())?;
let assigned440=binary("sub",e.get("motor_end")?,e.get("e")?.attr("wall")?)?;e.set("start",assigned440.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun443=e.get("out")?.attr("append")?;let mut args441=Vec::new();let mut kw442=Vec::new();args441.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun446=e.get("e")?.attr("_zcyl")?;let mut args444=Vec::new();let mut kw445=Vec::new();args444.push(e.get("e")?.attr("_tray")?.attr("can_half")?);args444.push(e.get("cx")?);args444.push(e.get("y")?);args444.push(binary("sub",binary("add",binary("add",e.get("flange")?,e.get("e")?.attr("_tray")?.attr("boss_depth")?)?,e.get("finish")?)?,Val::Float(0.01f64))?);args444.push(binary("add",e.get("start")?,Val::Float(0.01f64))?);fun446.call(args444,kw445)?}});fun443.call(args441,kw442)?}};
let assigned447=binary("sub",e.get("terminal_r")?,e.get("e")?.attr("_tray")?.attr("can_half")?)?;e.set("rise",assigned447.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun450=e.get("out")?.attr("append")?;let mut args448=Vec::new();let mut kw449=Vec::new();args448.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun453=e.get("cq")?.attr("Solid")?.attr("makeCone")?;let mut args451=Vec::new();let mut kw452=Vec::new();args451.push(e.get("e")?.attr("_tray")?.attr("can_half")?);args451.push(e.get("terminal_r")?);args451.push(e.get("rise")?);args451.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun456=e.get("cq")?.attr("Vector")?;let mut args454=Vec::new();let mut kw455=Vec::new();args454.push(e.get("cx")?);args454.push(e.get("y")?);args454.push(e.get("start")?);fun456.call(args454,kw455)?}});args451.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun459=e.get("cq")?.attr("Vector")?;let mut args457=Vec::new();let mut kw458=Vec::new();args457.push(Val::Int(0i64));args457.push(Val::Int(0i64));args457.push(Val::Int(1i64));fun459.call(args457,kw458)?}});fun453.call(args451,kw452)?}});fun450.call(args448,kw449)?}};
let assigned460=binary("mul",e.get("terminal_r")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun463=e.get("math")?.attr("tan")?;let mut args461=Vec::new();let mut kw462=Vec::new();args461.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun466=e.get("math")?.attr("radians")?;let mut args464=Vec::new();let mut kw465=Vec::new();args464.push(e.get("e")?.attr("teardrop_roof_angle")?);fun466.call(args464,kw465)?}});fun463.call(args461,kw462)?}})?;e.set("roof_rise",assigned460.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun469=e.get("out")?.attr("append")?;let mut args467=Vec::new();let mut kw468=Vec::new();args467.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun472=e.get("cq")?.attr("Solid")?.attr("makeCone")?;let mut args470=Vec::new();let mut kw471=Vec::new();args470.push(e.get("terminal_r")?);args470.push(Val::Float(0.0f64));args470.push(e.get("roof_rise")?);args470.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun475=e.get("cq")?.attr("Vector")?;let mut args473=Vec::new();let mut kw474=Vec::new();args473.push(e.get("cx")?);args473.push(e.get("y")?);args473.push(binary("add",e.get("start")?,e.get("rise")?)?);fun475.call(args473,kw474)?}});args470.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun478=e.get("cq")?.attr("Vector")?;let mut args476=Vec::new();let mut kw477=Vec::new();args476.push(Val::Int(0i64));args476.push(Val::Int(0i64));args476.push(Val::Int(1i64));fun478.call(args476,kw477)?}});fun472.call(args470,kw471)?}});fun469.call(args467,kw468)?}};
}
return Ok(e.get("out")?);
Ok(Val::None)})})?;
    // upper_wire_room
    e.set("upper_wire_room", {
        let params = vec![("e".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned479 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun482 = e.get("datums")?;
                    let mut args480 = Vec::new();
                    let mut kw481 = Vec::new();
                    args480.push(e.get("e")?);
                    args480.push(e.get("box")?);
                    fun482.call(args480, kw481)?
                }
            };
            e.set("d", assigned479.clone())?;
            let assigned483 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun486 = e.get("e")?.attr("cap_terminal_crown_r")?;
                    let mut args484 = Vec::new();
                    let mut kw485 = Vec::new();
                    args484.push(e.get("box")?);
                    fun486.call(args484, kw485)?
                }
            };
            e.set("radius", assigned483.clone())?;
            let assigned487 = binary(
                "sub",
                binary(
                    "add",
                    binary(
                        "sub",
                        binary(
                            "add",
                            e.get("d")?.get(Val::Str("flange_z".into()))?,
                            e.get("e")?.attr("_tray")?.attr("motor_crown")?,
                        )?,
                        e.get("e")?.attr("wall")?,
                    )?,
                    e.get("radius")?,
                )?,
                e.get("e")?.attr("_tray")?.attr("can_half")?,
            )?;
            e.set("base", assigned487.clone())?;
            let assigned488 = binary(
                "add",
                e.get("base")?,
                binary("mul", e.get("radius")?, {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                        line!(),
                    );
                    {
                        let fun491 = e.get("math")?.attr("tan")?;
                        let mut args489 = Vec::new();
                        let mut kw490 = Vec::new();
                        args489.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                line!(),
                            );
                            {
                                let fun494 = e.get("math")?.attr("radians")?;
                                let mut args492 = Vec::new();
                                let mut kw493 = Vec::new();
                                args492.push(e.get("e")?.attr("teardrop_roof_angle")?);
                                fun494.call(args492, kw493)?
                            }
                        });
                        fun491.call(args489, kw490)?
                    }
                })?,
            )?;
            e.set("peak", assigned488.clone())?;
            let assigned495 = binary(
                "sub",
                e.get("e")?.attr("display_body_offset_x")?,
                binary(
                    "truediv",
                    e.get("e")?.attr("display_pcb_x")?,
                    Val::Float(2.0f64),
                )?,
            )?;
            e.set("x0", assigned495.clone())?;
            let assigned496 = binary(
                "add",
                e.get("e")?.attr("display_body_offset_x")?,
                binary(
                    "truediv",
                    e.get("e")?.attr("display_pcb_x")?,
                    Val::Float(2.0f64),
                )?,
            )?;
            e.set("x1", assigned496.clone())?;
            let assigned497 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun500 = e.get("e")?.attr("_yz_prism")?;
                    let mut args498 = Vec::new();
                    let mut kw499 = Vec::new();
                    args498.push(e.get("x0")?);
                    args498.push(e.get("x1")?);
                    args498.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "sub",
                                e.get("d")?.get(Val::Str("motor_y".into()))?,
                                e.get("radius")?,
                            )?);
                            s.push(e.get("base")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "add",
                                e.get("d")?.get(Val::Str("motor_y".into()))?,
                                e.get("radius")?,
                            )?);
                            s.push(e.get("base")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("d")?.get(Val::Str("motor_y".into()))?);
                            s.push(e.get("peak")?);
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    fun500.call(args498, kw499)?
                }
            };
            e.set("motor", assigned497.clone())?;
            let assigned501 = binary(
                "add",
                e.get("e")?.attr("display_facet_thickness")?,
                e.get("e")?.attr("display_pcb_cut_through")?,
            )?;
            e.set("depth", assigned501.clone())?;
            let assigned502 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun505 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun508 = e.get("e")?.attr("_ybox")?;
                            let mut args506 = Vec::new();
                            let mut kw507 = Vec::new();
                            args506.push(e.get("x0")?);
                            args506.push(e.get("x1")?);
                            args506.push(binary(
                                "sub",
                                e.get("e")?.attr("display_body_offset_slope")?,
                                binary(
                                    "truediv",
                                    e.get("e")?.attr("display_pcb_slope")?,
                                    Val::Float(2.0f64),
                                )?,
                            )?);
                            args506.push(binary(
                                "add",
                                e.get("e")?.attr("display_body_offset_slope")?,
                                binary(
                                    "truediv",
                                    e.get("e")?.attr("display_pcb_slope")?,
                                    Val::Float(2.0f64),
                                )?,
                            )?);
                            args506.push(unary("neg", e.get("depth")?)?);
                            args506.push(e.get("e")?.attr("_display_wings")?.attr("GLASS_SEAT")?);
                            fun508.call(args506, kw507)?
                        }
                    }
                    .attr("moved")?;
                    let mut args503 = Vec::new();
                    let mut kw504 = Vec::new();
                    args503.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun511 = e.get("cq")?.attr("Location")?;
                            let mut args509 = Vec::new();
                            let mut kw510 = Vec::new();
                            args509.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                    line!(),
                                );
                                {
                                    let fun514 = e.get("e")?.attr("display_plane")?;
                                    let mut args512 = Vec::new();
                                    let mut kw513 = Vec::new();
                                    args512.push(e.get("box")?.attr("outer")?);
                                    fun514.call(args512, kw513)?
                                }
                            });
                            fun511.call(args509, kw510)?
                        }
                    });
                    fun505.call(args503, kw504)?
                }
            };
            e.set("pcb", assigned502.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun517 = e.get("_convex_corridor")?;
                    let mut args515 = Vec::new();
                    let mut kw516 = Vec::new();
                    args515.push(e.get("e")?);
                    args515.push({
                        let mut s = Vec::new();
                        s.push(e.get("motor")?);
                        s.push(e.get("pcb")?);
                        s.extend(
                            {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                    line!(),
                                );
                                {
                                    let fun520 = e.get("wire_cuts")?;
                                    let mut args518 = Vec::new();
                                    let mut kw519 = Vec::new();
                                    args518.push(e.get("e")?);
                                    args518.push(e.get("box")?);
                                    fun520.call(args518, kw519)?
                                }
                            }
                            .get(Val::Slice {
                                start: Some(Val::Int(2i64).integer()?),
                                stop: None,
                                step: 1,
                            })?
                            .iter()?,
                        );
                        Val::list(s)
                    });
                    fun517.call(args515, kw516)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // display_cleanouts
    e.set("display_cleanouts",{let params=vec![("e".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned521=e.get("e")?.attr("_display_wings")?;e.set("wings",assigned521.clone())?;
let assigned522=binary("add",binary("add",binary("truediv",e.get("wings")?.attr("COVER_X")?,Val::Float(2.0f64))?,e.get("wings")?.attr("WING_REACH")?)?,e.get("wings")?.attr("TIP_AIR")?)?;e.set("reach",assigned522.clone())?;
let assigned523={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun526=e.get("e")?.attr("_display_cut_exit_depth")?;let mut args524=Vec::new();let mut kw525=Vec::new();fun526.call(args524,kw525)?}};e.set("depth",assigned523.clone())?;
let assigned527=binary("sub",e.get("wings")?.attr("GLASS_SEAT")?,e.get("e")?.attr("wall")?)?;e.set("roof",assigned527.clone())?;
let assigned528=binary("sub",binary("add",binary("add",e.get("wings")?.attr("BACK")?,e.get("wings")?.attr("WING_THICK")?)?,e.get("wings")?.attr("BEARING_AIR")?)?,e.get("depth")?)?;e.set("floor",assigned528.clone())?;
let assigned529=binary("sub",binary("sub",binary("truediv",unary("neg",e.get("wings")?.attr("WING_SPAN")?)?,Val::Float(2.0f64))?,e.get("wings")?.attr("END_AIR")?)?,binary("mul",e.get("depth")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun532=e.get("math")?.attr("tan")?;let mut args530=Vec::new();let mut kw531=Vec::new();args530.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun535=e.get("math")?.attr("radians")?;let mut args533=Vec::new();let mut kw534=Vec::new();args533.push(e.get("wings")?.attr("ANGLE")?);fun535.call(args533,kw534)?}});fun532.call(args530,kw531)?}})?)?;e.set("y0",assigned529.clone())?;
let assigned536=binary("add",binary("truediv",e.get("wings")?.attr("WING_SPAN")?,Val::Float(2.0f64))?,e.get("wings")?.attr("END_AIR")?)?;e.set("y1",assigned536.clone())?;
let assigned537=binary("sub",e.get("e")?.attr("display_body_offset_x")?,binary("truediv",e.get("e")?.attr("display_pcb_x")?,Val::Float(2.0f64))?)?;e.set("pcb0",assigned537.clone())?;
let assigned538=binary("add",e.get("e")?.attr("display_body_offset_x")?,binary("truediv",e.get("e")?.attr("display_pcb_x")?,Val::Float(2.0f64))?)?;e.set("pcb1",assigned538.clone())?;
let assigned539={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun542=e.get("cq")?.attr("Location")?;let mut args540=Vec::new();let mut kw541=Vec::new();args540.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun545=e.get("e")?.attr("display_plane")?;let mut args543=Vec::new();let mut kw544=Vec::new();args543.push(e.get("box")?.attr("outer")?);fun545.call(args543,kw544)?}});fun542.call(args540,kw541)?}};e.set("place",assigned539.clone())?;
return Ok({let e=e.child();let out546=Val::list(vec![]);for item547 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(unary("neg",e.get("reach")?)?);s.push(binary("add",e.get("pcb0")?,Val::Float(0.01f64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",e.get("pcb1")?,Val::Float(0.01f64))?);s.push(e.get("reach")?);Val::tuple(s)});Val::tuple(s)}.iter()? {let unpack548=unpack(item547,2)?;e.set("x0",unpack548[0].clone())?;e.set("x1",unpack548[1].clone())?;out546.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun551={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun554=e.get("e")?.attr("_ybox")?;let mut args552=Vec::new();let mut kw553=Vec::new();args552.push(e.get("x0")?);args552.push(e.get("x1")?);args552.push(e.get("y0")?);args552.push(e.get("y1")?);args552.push(e.get("floor")?);args552.push(e.get("roof")?);fun554.call(args552,kw553)?}}.attr("moved")?;let mut args549=Vec::new();let mut kw550=Vec::new();args549.push(e.get("place")?);fun551.call(args549,kw550)?}}],vec![])?;}out546});
Ok(Val::None)})})?;
    // fixed_cuts
    e.set("fixed_cuts", {
        let params = vec![("e".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned555 = {
                let mut s = Vec::new();
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                        line!(),
                    );
                    {
                        let fun558 = e.get("loading_opening")?;
                        let mut args556 = Vec::new();
                        let mut kw557 = Vec::new();
                        args556.push(e.get("e")?);
                        args556.push(e.get("box")?);
                        fun558.call(args556, kw557)?
                    }
                });
                s.extend(
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun561 = e.get("inverse_cuts")?;
                            let mut args559 = Vec::new();
                            let mut kw560 = Vec::new();
                            args559.push(e.get("e")?);
                            args559.push(e.get("box")?);
                            fun561.call(args559, kw560)?
                        }
                    }
                    .iter()?,
                );
                s.extend(
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun564 = e.get("wire_cuts")?;
                            let mut args562 = Vec::new();
                            let mut kw563 = Vec::new();
                            args562.push(e.get("e")?);
                            args562.push(e.get("box")?);
                            fun564.call(args562, kw563)?
                        }
                    }
                    .iter()?,
                );
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                        line!(),
                    );
                    {
                        let fun567 = e.get("upper_wire_room")?;
                        let mut args565 = Vec::new();
                        let mut kw566 = Vec::new();
                        args565.push(e.get("e")?);
                        args565.push(e.get("box")?);
                        fun567.call(args565, kw566)?
                    }
                });
                s.extend(
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun570 = e.get("display_cleanouts")?;
                            let mut args568 = Vec::new();
                            let mut kw569 = Vec::new();
                            args568.push(e.get("e")?);
                            args568.push(e.get("box")?);
                            fun570.call(args568, kw569)?
                        }
                    }
                    .iter()?,
                );
                Val::list(s)
            };
            e.set("out", assigned555.clone())?;
            let assigned571 = e.get("box")?.attr("pack")?.attr("collet_plate")?;
            e.set("plate", assigned571.clone())?;
            for item572 in e.get("plate")?.get(Val::Str("holes".into()))?.iter()? {
                let unpack573 = unpack(item572, 2)?;
                e.set("x", unpack573[0].clone())?;
                e.set("z", unpack573[1].clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                        line!(),
                    );
                    {
                        let fun576 = e.get("out")?.attr("append")?;
                        let mut args574 = Vec::new();
                        let mut kw575 = Vec::new();
                        args574.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                line!(),
                            );
                            {
                                let fun579 = e.get("e")?.attr("_ybox")?;
                                let mut args577 = Vec::new();
                                let mut kw578 = Vec::new();
                                args577.push(binary(
                                    "sub",
                                    e.get("x")?,
                                    binary(
                                        "truediv",
                                        e.get("TUBE_GATE_WIDTH")?,
                                        Val::Float(2.0f64),
                                    )?,
                                )?);
                                args577.push(binary(
                                    "add",
                                    e.get("x")?,
                                    binary(
                                        "truediv",
                                        e.get("TUBE_GATE_WIDTH")?,
                                        Val::Float(2.0f64),
                                    )?,
                                )?);
                                args577.push(binary(
                                    "sub",
                                    e.get("plate")?.get(Val::Str("fore_y".into()))?,
                                    Val::Float(0.01f64),
                                )?);
                                args577.push(binary(
                                    "add",
                                    e.get("plate")?.get(Val::Str("wall_aft_y".into()))?,
                                    Val::Float(0.01f64),
                                )?);
                                args577.push(binary(
                                    "sub",
                                    e.get("e")?.attr("z_seam")?,
                                    Val::Float(20.0f64),
                                )?);
                                args577.push(binary("add", e.get("z")?, Val::Float(0.01f64))?);
                                fun579.call(args577, kw578)?
                            }
                        });
                        fun576.call(args574, kw575)?
                    }
                };
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // lower_voids
    e.set("lower_voids", {
        let params = vec![("e".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned580 = {
                let mut s = Vec::new();
                s.push(e.get("box")?.attr("pack")?.attr("pump_trays")?);
                s.push(e.get("box")?.attr("pack")?.attr("collet_plate")?);
                Val::tuple(s)
            };
            let unpack581 = unpack(assigned580.clone(), 2)?;
            e.set("trays", unpack581[0].clone())?;
            e.set("plate", unpack581[1].clone())?;
            let assigned582 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun585 = e.get("datums")?;
                    let mut args583 = Vec::new();
                    let mut kw584 = Vec::new();
                    args583.push(e.get("e")?);
                    args583.push(e.get("box")?);
                    fun585.call(args583, kw584)?
                }
            };
            e.set("d", assigned582.clone())?;
            let assigned586 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun589 = e.get("e")?.attr("_pump_lower_well")?;
                    let mut args587 = Vec::new();
                    let mut kw588 = Vec::new();
                    args587.push(e.get("trays")?);
                    fun589.call(args587, kw588)?
                }
            };
            e.set("source", assigned586.clone())?;
            let assigned590 = binary(
                "sub",
                e.get("e")?.attr("_tray")?.attr("_pc")?.attr("skirt_wall")?,
                e.get("e")?.attr("cap_pump_air")?,
            )?;
            e.set("wall_offset", assigned590.clone())?;
            let assigned591 = binary(
                "sub",
                e.get("e")?
                    .attr("_tray")?
                    .attr("_pc")?
                    .attr("skirt_base_half_extent")?,
                e.get("wall_offset")?,
            )?;
            e.set("upper_half", assigned591.clone())?;
            let assigned592 = binary(
                "sub",
                e.get("e")?.attr("_tray")?.attr("_pc")?.attr("corner_r")?,
                e.get("wall_offset")?,
            )?;
            e.set("corner_r", assigned592.clone())?;
            let assigned593 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun596 = e.get("e")?.attr("pump_skirt_support_z")?;
                    let mut args594 = Vec::new();
                    let mut kw595 = Vec::new();
                    args594.push(e.get("trays")?);
                    fun596.call(args594, kw595)?
                }
            };
            e.set("support", assigned593.clone())?;
            let assigned597 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("out", assigned597.clone())?;
            for item598 in e.get("trays")?.iter()? {
                let unpack599 = unpack(item598, 3)?;
                e.set("cx", unpack599[0].clone())?;
                e.set("cy", unpack599[1].clone())?;
                e.set("cz", unpack599[2].clone())?;
                let assigned600 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                        line!(),
                    );
                    {
                        let fun603 = e.get("source")?.attr("translate")?;
                        let mut args601 = Vec::new();
                        let mut kw602 = Vec::new();
                        args601.push({
                            let mut s = Vec::new();
                            s.push(e.get("cx")?);
                            s.push(e.get("cy")?);
                            s.push(e.get("cz")?);
                            Val::tuple(s)
                        });
                        fun603.call(args601, kw602)?
                    }
                };
                e.set("body", assigned600.clone())?;
                for item604 in {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(1.0f64))?);
                    s.push(Val::Float(1.0f64));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("sx", item604)?;
                    let assigned605 = binary(
                        "add",
                        e.get("cx")?,
                        binary(
                            "truediv",
                            binary(
                                "mul",
                                e.get("sx")?,
                                e.get("e")?.attr("_tray")?.attr("outlet_pitch")?,
                            )?,
                            Val::Float(2.0f64),
                        )?,
                    )?;
                    e.set("x", assigned605.clone())?;
                    let assigned606 = binary(
                        "add",
                        e.get("cz")?,
                        e.get("e")?.attr("_tray")?.attr("outlet_axis_z")?,
                    )?;
                    e.set("z", assigned606.clone())?;
                    let assigned607 = binary("add", e.get("cy")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun610 =
                                e.get("e")?.attr("_tray")?.attr("outlet_passage_start_y")?;
                            let mut args608 = Vec::new();
                            let mut kw609 = Vec::new();
                            args608.push(e.get("e")?.attr("cap_pump_air")?);
                            fun610.call(args608, kw609)?
                        }
                    })?;
                    e.set("y0", assigned607.clone())?;
                    let assigned611 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun614 = e.get("body")?.attr("fuse")?;
                            let mut args612 = Vec::new();
                            let mut kw613 = Vec::new();
                            args612.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                    line!(),
                                );
                                {
                                    let fun617 = e.get("e")?.attr("_ycyl")?;
                                    let mut args615 = Vec::new();
                                    let mut kw616 = Vec::new();
                                    args615.push(e.get("e")?.attr("cap_fitting_half")?);
                                    args615.push(e.get("x")?);
                                    args615.push(e.get("z")?);
                                    args615.push(e.get("y0")?);
                                    args615.push(binary(
                                        "add",
                                        e.get("d")?.get(Val::Str("y1".into()))?,
                                        Val::Float(1.0f64),
                                    )?);
                                    fun617.call(args615, kw616)?
                                }
                            });
                            args612.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                    line!(),
                                );
                                {
                                    let fun620 = e.get("e")?.attr("_ybox")?;
                                    let mut args618 = Vec::new();
                                    let mut kw619 = Vec::new();
                                    args618.push(binary(
                                        "sub",
                                        e.get("x")?,
                                        e.get("e")?.attr("cap_fitting_half")?,
                                    )?);
                                    args618.push(binary(
                                        "add",
                                        e.get("x")?,
                                        e.get("e")?.attr("cap_fitting_half")?,
                                    )?);
                                    args618.push(e.get("y0")?);
                                    args618.push(binary(
                                        "add",
                                        e.get("d")?.get(Val::Str("y1".into()))?,
                                        Val::Float(1.0f64),
                                    )?);
                                    args618.push(e.get("z")?);
                                    args618.push(binary(
                                        "add",
                                        e.get("d")?.get(Val::Str("retainer_top_z".into()))?,
                                        Val::Float(1.0f64),
                                    )?);
                                    fun620.call(args618, kw619)?
                                }
                            });
                            fun614.call(args612, kw613)?
                        }
                    };
                    e.set("body", assigned611.clone())?;
                }
                for item621 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                        line!(),
                    );
                    {
                        let fun624 = e.get("e")?.attr("_outlet_under_tangent_wedges")?;
                        let mut args622 = Vec::new();
                        let mut kw623 = Vec::new();
                        args622.push(e.get("cx")?);
                        args622.push(e.get("cy")?);
                        args622.push(e.get("cz")?);
                        fun624.call(args622, kw623)?
                    }
                }
                .iter()?
                {
                    e.set("wedge", item621)?;
                    let assigned625 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun628 = e.get("body")?.attr("fuse")?;
                            let mut args626 = Vec::new();
                            let mut kw627 = Vec::new();
                            args626.push(e.get("wedge")?);
                            fun628.call(args626, kw627)?
                        }
                    };
                    e.set("body", assigned625.clone())?;
                }
                for item629 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                        line!(),
                    );
                    {
                        let fun632 = e.get("e")?.attr("_outlet_fore_miter_wedges")?;
                        let mut args630 = Vec::new();
                        let mut kw631 = Vec::new();
                        args630.push(e.get("cx")?);
                        args630.push(e.get("cy")?);
                        args630.push(e.get("cz")?);
                        fun632.call(args630, kw631)?
                    }
                }
                .iter()?
                {
                    e.set("wedge", item629)?;
                    let assigned633 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                            line!(),
                        );
                        {
                            let fun636 = e.get("body")?.attr("cut")?;
                            let mut args634 = Vec::new();
                            let mut kw635 = Vec::new();
                            args634.push(e.get("wedge")?);
                            fun636.call(args634, kw635)?
                        }
                    };
                    e.set("body", assigned633.clone())?;
                }
                let assigned637 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                        line!(),
                    );
                    {
                        let fun640 = e.get("body")?.attr("fuse")?;
                        let mut args638 = Vec::new();
                        let mut kw639 = Vec::new();
                        args638.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                line!(),
                            );
                            {
                                let fun643 = e.get("e")?.attr("_ybox")?;
                                let mut args641 = Vec::new();
                                let mut kw642 = Vec::new();
                                args641.push(binary("sub", e.get("cx")?, e.get("upper_half")?)?);
                                args641.push(binary("add", e.get("cx")?, e.get("upper_half")?)?);
                                args641.push(binary(
                                    "sub",
                                    e.get("d")?.get(Val::Str("y0".into()))?,
                                    Val::Float(1.0f64),
                                )?);
                                args641.push(binary(
                                    "add",
                                    binary(
                                        "add",
                                        binary("sub", e.get("cy")?, e.get("upper_half")?)?,
                                        e.get("corner_r")?,
                                    )?,
                                    Val::Float(0.01f64),
                                )?);
                                args641.push(e.get("support")?);
                                args641.push(binary(
                                    "add",
                                    e.get("d")?.get(Val::Str("retainer_top_z".into()))?,
                                    Val::Float(1.0f64),
                                )?);
                                fun643.call(args641, kw642)?
                            }
                        });
                        fun640.call(args638, kw639)?
                    }
                };
                e.set("body", assigned637.clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                        line!(),
                    );
                    {
                        let fun646 = e.get("out")?.attr("append")?;
                        let mut args644 = Vec::new();
                        let mut kw645 = Vec::new();
                        args644.push(e.get("body")?);
                        fun646.call(args644, kw645)?
                    }
                };
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // wing_profile
    e.set("wing_profile",{let params=vec![("e".into(),None,false),("box".into(),None,false),("side".into(),None,false),("spread".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned647={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun650=e.get("datums")?;let mut args648=Vec::new();let mut kw649=Vec::new();args648.push(e.get("e")?);args648.push(e.get("box")?);fun650.call(args648,kw649)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun653=e.get("snap_datums")?;let mut args651=Vec::new();let mut kw652=Vec::new();args651.push(e.get("e")?);args651.push(e.get("box")?);fun653.call(args651,kw652)?}});Val::tuple(s)};let unpack654=unpack(assigned647.clone(),2)?;e.set("d",unpack654[0].clone())?;e.set("s",unpack654[1].clone())?;
let assigned655={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(e.get("s")?.get(Val::Str("wing_inner_x".into()))?);s.push(e.get("s")?.get(Val::Str("floor_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("s")?.get(Val::Str("hook_outer_x".into()))?);s.push(e.get("s")?.get(Val::Str("floor_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("s")?.get(Val::Str("wing_outer_x".into()))?);s.push(e.get("s")?.get(Val::Str("hook_ramp_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("s")?.get(Val::Str("wing_outer_x".into()))?);s.push(e.get("s")?.get(Val::Str("root_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",e.get("s")?.get(Val::Str("wing_inner_x".into()))?,e.get("ROOT_RADIUS")?)?);s.push(e.get("s")?.get(Val::Str("root_z".into()))?);Val::tuple(s)});Val::list(s)};e.set("points",assigned655.clone())?;
let assigned656=binary("sub",e.get("s")?.get(Val::Str("root_z".into()))?,e.get("s")?.get(Val::Str("floor_z".into()))?)?;e.set("length",assigned656.clone())?;
// deflection
e.set("deflection",{let params=vec![("z".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned657=binary("truediv",binary("sub",e.get("s")?.get(Val::Str("root_z".into()))?,e.get("z")?)?,e.get("length")?)?;e.set("t",assigned657.clone())?;
return Ok(binary("truediv",binary("mul",binary("mul",binary("mul",e.get("spread")?,e.get("t")?)?,e.get("t")?)?,binary("sub",Val::Float(3.0f64),e.get("t")?)?)?,Val::Float(2.0f64))?);
Ok(Val::None)})})?;
// slope
e.set("slope",{let params=vec![("z".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned658=binary("truediv",binary("sub",e.get("s")?.get(Val::Str("root_z".into()))?,e.get("z")?)?,e.get("length")?)?;e.set("t",assigned658.clone())?;
return Ok(binary("truediv",binary("mul",unary("neg",e.get("spread")?)?,binary("sub",binary("mul",Val::Float(3.0f64),e.get("t")?)?,binary("mul",binary("mul",Val::Float(1.5f64),e.get("t")?)?,e.get("t")?)?)?)?,e.get("length")?)?);
Ok(Val::None)})})?;
let assigned659={let mut s=Vec::new();Val::list(s)};e.set("segments",assigned659.clone())?;
for item660 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun663=e.get("zip")?;let mut args661=Vec::new();let mut kw662=Vec::new();args661.push(e.get("points")?);args661.push(e.get("points")?.get(Val::Slice{start:Some(Val::Int(1i64).integer()?),stop:None,step:1})?);fun663.call(args661,kw662)?}}.iter()? {
let unpack664=unpack(item660,2)?;e.set("a",unpack664[0].clone())?;e.set("b",unpack664[1].clone())?;let assigned665=e.get("a")?;let unpack666=unpack(assigned665.clone(),2)?;e.set("xa",unpack666[0].clone())?;e.set("za",unpack666[1].clone())?;
let assigned667=e.get("b")?;let unpack668=unpack(assigned667.clone(),2)?;e.set("xb",unpack668[0].clone())?;e.set("zb",unpack668[1].clone())?;
let assigned669={let mut s=Vec::new();s.push(binary("mul",e.get("side")?,binary("add",e.get("xa")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun672=e.get("deflection")?;let mut args670=Vec::new();let mut kw671=Vec::new();args670.push(e.get("za")?);fun672.call(args670,kw671)?}})?)?);s.push(e.get("za")?);Val::tuple(s)};e.set("pa",assigned669.clone())?;
let assigned673={let mut s=Vec::new();s.push(binary("mul",e.get("side")?,binary("add",e.get("xb")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun676=e.get("deflection")?;let mut args674=Vec::new();let mut kw675=Vec::new();args674.push(e.get("zb")?);fun676.call(args674,kw675)?}})?)?);s.push(e.get("zb")?);Val::tuple(s)};e.set("pb",assigned673.clone())?;
if {let v683={let v687={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun686=e.get("abs")?;let mut args684=Vec::new();let mut kw685=Vec::new();args684.push(binary("sub",e.get("zb")?,e.get("za")?)?);fun686.call(args684,kw685)?}};let v688=Val::Float(1e-09f64);Val::Bool(compare("lt",v687.clone(),v688.clone())?.truthy()?)};if v683.truthy()? {v683} else {{let v677={let v681={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun680=e.get("abs")?;let mut args678=Vec::new();let mut kw679=Vec::new();args678.push(binary("sub",e.get("xb")?,e.get("xa")?)?);fun680.call(args678,kw679)?}};let v682=Val::Float(1e-09f64);Val::Bool(compare("gt",v681.clone(),v682.clone())?.truthy()?)};if v677.truthy()? {v677} else {unary("not",e.get("spread")?)?}}}}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun691=e.get("segments")?.attr("append")?;let mut args689=Vec::new();let mut kw690=Vec::new();args689.push({let d=Val::dict(vec![]);d.set(Val::Str("line".into()),{let mut s=Vec::new();s.push(e.get("pa")?);s.push(e.get("pb")?);Val::tuple(s)})?;d});fun691.call(args689,kw690)?}};
}else{
let assigned692={let mut s=Vec::new();s.push(binary("mul",e.get("side")?,binary("add",binary("sub",e.get("xb")?,e.get("xa")?)?,binary("mul",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun695=e.get("slope")?;let mut args693=Vec::new();let mut kw694=Vec::new();args693.push(e.get("za")?);fun695.call(args693,kw694)?}},binary("sub",e.get("zb")?,e.get("za")?)?)?)?)?);s.push(binary("sub",e.get("zb")?,e.get("za")?)?);Val::tuple(s)};e.set("da",assigned692.clone())?;
let assigned696={let mut s=Vec::new();s.push(binary("mul",e.get("side")?,binary("add",binary("sub",e.get("xb")?,e.get("xa")?)?,binary("mul",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun699=e.get("slope")?;let mut args697=Vec::new();let mut kw698=Vec::new();args697.push(e.get("zb")?);fun699.call(args697,kw698)?}},binary("sub",e.get("zb")?,e.get("za")?)?)?)?)?);s.push(binary("sub",e.get("zb")?,e.get("za")?)?);Val::tuple(s)};e.set("db",assigned696.clone())?;
let assigned700=binary("truediv",Val::Float(1.0f64),Val::Float(3.0f64))?;e.set("third",assigned700.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun703=e.get("segments")?.attr("append")?;let mut args701=Vec::new();let mut kw702=Vec::new();args701.push({let d=Val::dict(vec![]);d.set(Val::Str("cubic".into()),{let mut s=Vec::new();s.push(e.get("pa")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun706=e.get("tuple")?;let mut args704=Vec::new();let mut kw705=Vec::new();args704.push({let e=e.child();let out707=Val::list(vec![]);for item708 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun711=e.get("zip")?;let mut args709=Vec::new();let mut kw710=Vec::new();args709.push(e.get("pa")?);args709.push(e.get("da")?);fun711.call(args709,kw710)?}}.iter()? {let unpack712=unpack(item708,2)?;e.set("a",unpack712[0].clone())?;e.set("b",unpack712[1].clone())?;out707.attr("append")?.call(vec![binary("add",e.get("a")?,binary("mul",e.get("b")?,e.get("third")?)?)?],vec![])?;}out707});fun706.call(args704,kw705)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun715=e.get("tuple")?;let mut args713=Vec::new();let mut kw714=Vec::new();args713.push({let e=e.child();let out716=Val::list(vec![]);for item717 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun720=e.get("zip")?;let mut args718=Vec::new();let mut kw719=Vec::new();args718.push(e.get("pb")?);args718.push(e.get("db")?);fun720.call(args718,kw719)?}}.iter()? {let unpack721=unpack(item717,2)?;e.set("a",unpack721[0].clone())?;e.set("b",unpack721[1].clone())?;out716.attr("append")?.call(vec![binary("sub",e.get("a")?,binary("mul",e.get("b")?,e.get("third")?)?)?],vec![])?;}out716});fun715.call(args713,kw714)?}});s.push(e.get("pb")?);Val::tuple(s)})?;d});fun703.call(args701,kw702)?}};
}
}
let assigned722=binary("mul",binary("mul",binary("truediv",Val::Float(4.0f64),Val::Float(3.0f64))?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun725=e.get("math")?.attr("tan")?;let mut args723=Vec::new();let mut kw724=Vec::new();args723.push(binary("truediv",e.get("math")?.attr("pi")?,Val::Float(8.0f64))?);fun725.call(args723,kw724)?}})?,e.get("ROOT_RADIUS")?)?;e.set("k",assigned722.clone())?;
let assigned726=e.get("points")?.get(unary("neg",Val::Int(1i64))?)?;e.set("a",assigned726.clone())?;
let assigned727={let mut s=Vec::new();s.push(e.get("s")?.get(Val::Str("wing_inner_x".into()))?);s.push(binary("sub",e.get("s")?.get(Val::Str("root_z".into()))?,e.get("ROOT_RADIUS")?)?);Val::tuple(s)};e.set("b",assigned727.clone())?;
let assigned728={let mut s=Vec::new();s.push(e.get("a")?);s.push({let mut s=Vec::new();s.push(binary("add",e.get("a")?.get(Val::Int(0i64))?,e.get("k")?)?);s.push(e.get("a")?.get(Val::Int(1i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("b")?.get(Val::Int(0i64))?);s.push(binary("add",e.get("b")?.get(Val::Int(1i64))?,e.get("k")?)?);Val::tuple(s)});s.push(e.get("b")?);Val::tuple(s)};e.set("controls",assigned728.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun731=e.get("segments")?.attr("append")?;let mut args729=Vec::new();let mut kw730=Vec::new();args729.push({let d=Val::dict(vec![]);d.set(Val::Str("cubic".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun734=e.get("tuple")?;let mut args732=Vec::new();let mut kw733=Vec::new();args732.push({let e=e.child();let out735=Val::list(vec![]);for item736 in e.get("controls")?.iter()? {let unpack737=unpack(item736,2)?;e.set("x",unpack737[0].clone())?;e.set("z",unpack737[1].clone())?;out735.attr("append")?.call(vec![{let mut s=Vec::new();s.push(binary("mul",e.get("side")?,binary("add",e.get("x")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun740=e.get("deflection")?;let mut args738=Vec::new();let mut kw739=Vec::new();args738.push(e.get("z")?);fun740.call(args738,kw739)?}})?)?);s.push(e.get("z")?);Val::tuple(s)}],vec![])?;}out735});fun734.call(args732,kw733)?}})?;d});fun731.call(args729,kw730)?}};
let assigned741={let mut s=Vec::new();s.push(e.get("b")?);s.push(e.get("points")?.get(Val::Int(0i64))?);Val::tuple(s)};let unpack742=unpack(assigned741.clone(),2)?;e.set("a",unpack742[0].clone())?;e.set("b",unpack742[1].clone())?;
let assigned743={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,binary("add",e.get("a")?.get(Val::Int(0i64))?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun746=e.get("deflection")?;let mut args744=Vec::new();let mut kw745=Vec::new();args744.push(e.get("a")?.get(Val::Int(1i64))?);fun746.call(args744,kw745)?}})?)?);s.push(e.get("a")?.get(Val::Int(1i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,binary("add",e.get("b")?.get(Val::Int(0i64))?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun749=e.get("deflection")?;let mut args747=Vec::new();let mut kw748=Vec::new();args747.push(e.get("b")?.get(Val::Int(1i64))?);fun749.call(args747,kw748)?}})?)?);s.push(e.get("b")?.get(Val::Int(1i64))?);Val::tuple(s)});Val::tuple(s)};let unpack750=unpack(assigned743.clone(),2)?;e.set("pa",unpack750[0].clone())?;e.set("pb",unpack750[1].clone())?;
let assigned751=binary("sub",e.get("b")?.get(Val::Int(1i64))?,e.get("a")?.get(Val::Int(1i64))?)?;e.set("dz",assigned751.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun754=e.get("segments")?.attr("append")?;let mut args752=Vec::new();let mut kw753=Vec::new();args752.push({let d=Val::dict(vec![]);d.set(Val::Str("cubic".into()),{let mut s=Vec::new();s.push(e.get("pa")?);s.push({let mut s=Vec::new();s.push(binary("add",e.get("pa")?.get(Val::Int(0i64))?,binary("truediv",binary("mul",binary("mul",e.get("side")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun757=e.get("slope")?;let mut args755=Vec::new();let mut kw756=Vec::new();args755.push(e.get("a")?.get(Val::Int(1i64))?);fun757.call(args755,kw756)?}})?,e.get("dz")?)?,Val::Float(3.0f64))?)?);s.push(binary("add",e.get("a")?.get(Val::Int(1i64))?,binary("truediv",e.get("dz")?,Val::Float(3.0f64))?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",e.get("pb")?.get(Val::Int(0i64))?,binary("truediv",binary("mul",binary("mul",e.get("side")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun760=e.get("slope")?;let mut args758=Vec::new();let mut kw759=Vec::new();args758.push(e.get("b")?.get(Val::Int(1i64))?);fun760.call(args758,kw759)?}})?,e.get("dz")?)?,Val::Float(3.0f64))?)?);s.push(binary("sub",e.get("b")?.get(Val::Int(1i64))?,binary("truediv",e.get("dz")?,Val::Float(3.0f64))?)?);Val::tuple(s)});s.push(e.get("pb")?);Val::tuple(s)})?;d});fun754.call(args752,kw753)?}};
return Ok({let d=Val::dict(vec![]);d.set(Val::Str("span".into()),{let mut s=Vec::new();s.push(e.get("d")?.get(Val::Str("y0".into()))?);s.push(e.get("d")?.get(Val::Str("y1".into()))?);Val::tuple(s)})?;d.set(Val::Str("segments".into()),e.get("segments")?)?;d});
Ok(Val::None)})})?;
    // _wing
    e.set("_wing",{let params=vec![("e".into(),None,false),("box".into(),None,false),("side".into(),None,false),("spread".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned761={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun764=e.get("wing_profile")?;let mut args762=Vec::new();let mut kw763=Vec::new();args762.push(e.get("e")?);args762.push(e.get("box")?);args762.push(e.get("side")?);args762.push(e.get("spread")?);fun764.call(args762,kw763)?}};e.set("profile",assigned761.clone())?;
let assigned765=e.get("profile")?.get(Val::Str("span".into()))?;let unpack766=unpack(assigned765.clone(),2)?;e.set("y0",unpack766[0].clone())?;e.set("y1",unpack766[1].clone())?;
let assigned767={let params=vec![("p".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun770=e.get("cq")?.attr("Vector")?;let mut args768=Vec::new();let mut kw769=Vec::new();args768.push(e.get("p")?.get(Val::Int(0i64))?);args768.push(e.get("y0")?);args768.push(e.get("p")?.get(Val::Int(1i64))?);fun770.call(args768,kw769)?}});
Ok(Val::None)})};e.set("vector",assigned767.clone())?;
let assigned771={let mut s=Vec::new();Val::list(s)};e.set("edges",assigned771.clone())?;
for item772 in e.get("profile")?.get(Val::Str("segments".into()))?.iter()? {
e.set("segment",item772)?;if {let v773=Val::Str("line".into());let v774=e.get("segment")?;Val::Bool(compare("in",v773.clone(),v774.clone())?.truthy()?)}.truthy()? {
let assigned775=e.get("segment")?.get(Val::Str("line".into()))?;let unpack776=unpack(assigned775.clone(),2)?;e.set("a",unpack776[0].clone())?;e.set("b",unpack776[1].clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun779=e.get("edges")?.attr("append")?;let mut args777=Vec::new();let mut kw778=Vec::new();args777.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun782=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args780=Vec::new();let mut kw781=Vec::new();args780.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun785=e.get("vector")?;let mut args783=Vec::new();let mut kw784=Vec::new();args783.push(e.get("a")?);fun785.call(args783,kw784)?}});args780.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun788=e.get("vector")?;let mut args786=Vec::new();let mut kw787=Vec::new();args786.push(e.get("b")?);fun788.call(args786,kw787)?}});fun782.call(args780,kw781)?}});fun779.call(args777,kw778)?}};
}else{
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun791=e.get("edges")?.attr("append")?;let mut args789=Vec::new();let mut kw790=Vec::new();args789.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun794=e.get("cq")?.attr("Edge")?.attr("makeBezier")?;let mut args792=Vec::new();let mut kw793=Vec::new();args792.push({let e=e.child();let out795=Val::list(vec![]);for item796 in e.get("segment")?.get(Val::Str("cubic".into()))?.iter()? {e.set("p",item796)?;out795.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun799=e.get("vector")?;let mut args797=Vec::new();let mut kw798=Vec::new();args797.push(e.get("p")?);fun799.call(args797,kw798)?}}],vec![])?;}out795});fun794.call(args792,kw793)?}});fun791.call(args789,kw790)?}};
}
}
let assigned800={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun803=e.get("cq")?.attr("Wire")?.attr("assembleEdges")?;let mut args801=Vec::new();let mut kw802=Vec::new();args801.push(e.get("edges")?);fun803.call(args801,kw802)?}};e.set("wire",assigned800.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun806=e.get("cq")?.attr("Solid")?.attr("extrudeLinear")?;let mut args804=Vec::new();let mut kw805=Vec::new();args804.push(e.get("wire")?);args804.push({let mut s=Vec::new();Val::list(s)});args804.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun809=e.get("cq")?.attr("Vector")?;let mut args807=Vec::new();let mut kw808=Vec::new();args807.push(Val::Float(0.0f64));args807.push(binary("sub",e.get("y1")?,e.get("y0")?)?);args807.push(Val::Float(0.0f64));fun809.call(args807,kw808)?}});fun806.call(args804,kw805)?}});
Ok(Val::None)})})?;
    // retainer
    e.set("retainer",{let params=vec![("e".into(),None,false),("box".into(),None,false),("seated".into(),Some(Val::Bool(false)),true)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned810={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun813=e.get("datums")?;let mut args811=Vec::new();let mut kw812=Vec::new();args811.push(e.get("e")?);args811.push(e.get("box")?);fun813.call(args811,kw812)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun816=e.get("snap_datums")?;let mut args814=Vec::new();let mut kw815=Vec::new();args814.push(e.get("e")?);args814.push(e.get("box")?);fun816.call(args814,kw815)?}});Val::tuple(s)};let unpack817=unpack(assigned810.clone(),2)?;e.set("d",unpack817[0].clone())?;e.set("s",unpack817[1].clone())?;
let assigned818={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun821=e.get("e")?.attr("_xz_prism")?;let mut args819=Vec::new();let mut kw820=Vec::new();args819.push(e.get("d")?.get(Val::Str("y0".into()))?);args819.push(e.get("d")?.get(Val::Str("y1".into()))?);args819.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(e.get("d")?.get(Val::Str("x0".into()))?);s.push(e.get("d")?.get(Val::Str("retainer_top_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("d")?.get(Val::Str("x1".into()))?);s.push(e.get("d")?.get(Val::Str("retainer_top_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("d")?.get(Val::Str("x1".into()))?);s.push(e.get("s")?.get(Val::Str("root_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("s")?.get(Val::Str("carrier_inner_x".into()))?);s.push(e.get("s")?.get(Val::Str("root_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("s")?.get(Val::Str("carrier_inner_x".into()))?);s.push(e.get("d")?.get(Val::Str("bottom_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(unary("neg",e.get("s")?.get(Val::Str("carrier_inner_x".into()))?)?);s.push(e.get("d")?.get(Val::Str("bottom_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(unary("neg",e.get("s")?.get(Val::Str("carrier_inner_x".into()))?)?);s.push(e.get("s")?.get(Val::Str("root_z".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("d")?.get(Val::Str("x0".into()))?);s.push(e.get("s")?.get(Val::Str("root_z".into()))?);Val::tuple(s)});Val::list(s)});fun821.call(args819,kw820)?}};e.set("body",assigned818.clone())?;
for item822 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun825=e.get("lower_voids")?;let mut args823=Vec::new();let mut kw824=Vec::new();args823.push(e.get("e")?);args823.push(e.get("box")?);fun825.call(args823,kw824)?}}.iter()? {
e.set("cutter",item822)?;let assigned826={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun829=e.get("body")?.attr("cut")?;let mut args827=Vec::new();let mut kw828=Vec::new();args827.push(e.get("cutter")?);fun829.call(args827,kw828)?}};e.set("body",assigned826.clone())?;
}
let assigned830=if e.get("seated")?.truthy()? {e.get("SEATED_SPREAD")?} else {e.get("RELAXED_SPREAD")?};e.set("spread",assigned830.clone())?;
let assigned831={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun834=e.get("body")?.attr("fuse")?;let mut args832=Vec::new();let mut kw833=Vec::new();args832.extend({let e=e.child();let out835=Val::list(vec![]);for item836 in {let mut s=Vec::new();s.push(unary("neg",Val::Float(1.0f64))?);s.push(Val::Float(1.0f64));Val::tuple(s)}.iter()? {e.set("side",item836)?;out835.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun839=e.get("_wing")?;let mut args837=Vec::new();let mut kw838=Vec::new();args837.push(e.get("e")?);args837.push(e.get("box")?);args837.push(e.get("side")?);args837.push(e.get("spread")?);fun839.call(args837,kw838)?}}],vec![])?;}out835}.iter()?);fun834.call(args832,kw833)?}};e.set("body",assigned831.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",line!());{let fun842=e.get("e")?.attr("_unified")?;let mut args840=Vec::new();let mut kw841=Vec::new();args840.push(e.get("body")?);fun842.call(args840,kw841)?}});
Ok(Val::None)})})?;
    // figures
    e.set("figures", {
        let params = vec![("e".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if unary("not", {
                let v843 = e.get("box")?.attr("pump_bay")?;
                if v843.truthy()? {
                    e.get("box")?.attr("pack")?.attr("pump_trays")?
                } else {
                    v843
                }
            })?
            .truthy()?
            {
                return Ok({
                    let d = Val::dict(vec![]);
                    d
                });
            }
            let assigned844 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun847 = e.get("datums")?;
                    let mut args845 = Vec::new();
                    let mut kw846 = Vec::new();
                    args845.push(e.get("e")?);
                    args845.push(e.get("box")?);
                    fun847.call(args845, kw846)?
                }
            };
            e.set("d", assigned844.clone())?;
            let assigned848 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                    line!(),
                );
                {
                    let fun851 = e.get("snap_datums")?;
                    let mut args849 = Vec::new();
                    let mut kw850 = Vec::new();
                    args849.push(e.get("e")?);
                    args849.push(e.get("box")?);
                    fun851.call(args849, kw850)?
                }
            };
            e.set("s", assigned848.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("PUMP_RETAINER_W".into()), {
                    let mut str852 = String::new();
                    str852.push_str(&format(
                        &binary(
                            "sub",
                            e.get("d")?.get(Val::Str("x1".into()))?,
                            e.get("d")?.get(Val::Str("x0".into()))?,
                        )?,
                        &val_string({
                            let mut str853 = String::new();
                            str853.push_str(".6g");
                            Val::Str(str853)
                        })?,
                    )?);
                    str852.push_str(" mm");
                    Val::Str(str852)
                })?;
                d.set(Val::Str("PUMP_RETAINER_D".into()), {
                    let mut str854 = String::new();
                    str854.push_str(&format(
                        &binary(
                            "sub",
                            e.get("d")?.get(Val::Str("y1".into()))?,
                            e.get("d")?.get(Val::Str("y0".into()))?,
                        )?,
                        &val_string({
                            let mut str855 = String::new();
                            str855.push_str(".6g");
                            Val::Str(str855)
                        })?,
                    )?);
                    str854.push_str(" mm");
                    Val::Str(str854)
                })?;
                d.set(Val::Str("PUMP_RETAINER_H".into()), {
                    let mut str856 = String::new();
                    str856.push_str(&format(
                        &binary(
                            "sub",
                            e.get("d")?.get(Val::Str("retainer_top_z".into()))?,
                            e.get("d")?.get(Val::Str("bottom_z".into()))?,
                        )?,
                        &val_string({
                            let mut str857 = String::new();
                            str857.push_str(".6g");
                            Val::Str(str857)
                        })?,
                    )?);
                    str856.push_str(" mm");
                    Val::Str(str856)
                })?;
                d.set(Val::Str("PUMP_RETAINER_BOTTOM_Z".into()), {
                    let mut str858 = String::new();
                    str858.push_str(&format(
                        &e.get("d")?.get(Val::Str("bottom_z".into()))?,
                        &val_string({
                            let mut str859 = String::new();
                            str859.push_str(".6g");
                            Val::Str(str859)
                        })?,
                    )?);
                    str858.push_str(" mm");
                    Val::Str(str858)
                })?;
                d.set(Val::Str("PUMP_RETAINER_TOP_Z".into()), {
                    let mut str860 = String::new();
                    str860.push_str(&format(
                        &e.get("d")?.get(Val::Str("retainer_top_z".into()))?,
                        &val_string({
                            let mut str861 = String::new();
                            str861.push_str(".6g");
                            Val::Str(str861)
                        })?,
                    )?);
                    str860.push_str(" mm");
                    Val::Str(str860)
                })?;
                d.set(Val::Str("PUMP_FLANGE_Z".into()), {
                    let mut str862 = String::new();
                    str862.push_str(&format(
                        &e.get("d")?.get(Val::Str("flange_z".into()))?,
                        &val_string({
                            let mut str863 = String::new();
                            str863.push_str(".6g");
                            Val::Str(str863)
                        })?,
                    )?);
                    str862.push_str(" mm");
                    Val::Str(str862)
                })?;
                d.set(Val::Str("PUMP_FIXED_BEARING_Z".into()), {
                    let mut str864 = String::new();
                    str864.push_str(&format(
                        &e.get("d")?.get(Val::Str("bearing_z".into()))?,
                        &val_string({
                            let mut str865 = String::new();
                            str865.push_str(".6g");
                            Val::Str(str865)
                        })?,
                    )?);
                    str864.push_str(" mm");
                    Val::Str(str864)
                })?;
                d.set(Val::Str("PUMP_SKIRT_SUPPORT_Z".into()), {
                    let mut str866 = String::new();
                    str866.push_str(&format(
                        &{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_fixed_pump_mount.rs",
                                line!(),
                            );
                            {
                                let fun869 = e.get("e")?.attr("pump_skirt_support_z")?;
                                let mut args867 = Vec::new();
                                let mut kw868 = Vec::new();
                                args867.push(e.get("box")?.attr("pack")?.attr("pump_trays")?);
                                fun869.call(args867, kw868)?
                            }
                        },
                        &val_string({
                            let mut str870 = String::new();
                            str870.push_str(".6g");
                            Val::Str(str870)
                        })?,
                    )?);
                    str866.push_str(" mm");
                    Val::Str(str866)
                })?;
                d.set(
                    Val::Str("PUMP_RETAINER_SCREW_COUNT".into()),
                    Val::Str("0".into()),
                )?;
                d.set(Val::Str("PUMP_SNAP_ROOT_Z".into()), {
                    let mut str871 = String::new();
                    str871.push_str(&format(
                        &e.get("s")?.get(Val::Str("root_z".into()))?,
                        &val_string({
                            let mut str872 = String::new();
                            str872.push_str(".6g");
                            Val::Str(str872)
                        })?,
                    )?);
                    str871.push_str(" mm");
                    Val::Str(str871)
                })?;
                d.set(Val::Str("PUMP_SNAP_WING_THICK".into()), {
                    let mut str873 = String::new();
                    str873.push_str(&format(
                        &e.get("WING_THICK")?,
                        &val_string({
                            let mut str874 = String::new();
                            str874.push_str("g");
                            Val::Str(str874)
                        })?,
                    )?);
                    str873.push_str(" mm");
                    Val::Str(str873)
                })?;
                d.set(Val::Str("PUMP_SNAP_LENGTH".into()), {
                    let mut str875 = String::new();
                    str875.push_str(&format(
                        &e.get("WING_LENGTH")?,
                        &val_string({
                            let mut str876 = String::new();
                            str876.push_str("g");
                            Val::Str(str876)
                        })?,
                    )?);
                    str875.push_str(" mm");
                    Val::Str(str875)
                })?;
                d.set(Val::Str("PUMP_SNAP_RECEIVER_FLOOR_Z".into()), {
                    let mut str877 = String::new();
                    str877.push_str(&format(
                        &e.get("s")?.get(Val::Str("receiver_floor_z".into()))?,
                        &val_string({
                            let mut str878 = String::new();
                            str878.push_str(".6g");
                            Val::Str(str878)
                        })?,
                    )?);
                    str877.push_str(" mm");
                    Val::Str(str877)
                })?;
                d.set(Val::Str("PUMP_SNAP_PORT_WIDTH".into()), {
                    let mut str879 = String::new();
                    str879.push_str(&format(
                        &binary(
                            "sub",
                            e.get("s")?.get(Val::Str("port_y1".into()))?,
                            e.get("s")?.get(Val::Str("port_y0".into()))?,
                        )?,
                        &val_string({
                            let mut str880 = String::new();
                            str880.push_str("g");
                            Val::Str(str880)
                        })?,
                    )?);
                    str879.push_str(" mm");
                    Val::Str(str879)
                })?;
                d.set(Val::Str("CAP_TUBE_OPEN".into()), {
                    let mut str881 = String::new();
                    str881.push_str(&format(
                        &binary("mul", Val::Int(2i64), e.get("e")?.attr("cap_fitting_half")?)?,
                        &val_string({
                            let mut str882 = String::new();
                            str882.push_str("g");
                            Val::Str(str882)
                        })?,
                    )?);
                    str881.push_str(" mm");
                    Val::Str(str881)
                })?;
                d.set(Val::Str("CAP_TUBE_PART".into()), {
                    let mut str883 = String::new();
                    str883.push_str(&format(
                        &e.get("e")?.attr("_tray")?.attr("fitting_w")?,
                        &val_string({
                            let mut str884 = String::new();
                            str884.push_str("g");
                            Val::Str(str884)
                        })?,
                    )?);
                    str883.push_str(" mm");
                    Val::Str(str883)
                })?;
                d.set(Val::Str("CAP_TUBE_PITCH".into()), {
                    let mut str885 = String::new();
                    str885.push_str(&format(
                        &e.get("e")?.attr("_tray")?.attr("outlet_pitch")?,
                        &val_string({
                            let mut str886 = String::new();
                            str886.push_str("g");
                            Val::Str(str886)
                        })?,
                    )?);
                    str885.push_str(" mm");
                    Val::Str(str885)
                })?;
                d.set(Val::Str("PUMP_SEATED_DROP".into()), {
                    let mut str887 = String::new();
                    str887.push_str(&format(
                        &e.get("e")?.attr("_interface")?.attr("pump_seated_drop")?,
                        &val_string({
                            let mut str888 = String::new();
                            str888.push_str("g");
                            Val::Str(str888)
                        })?,
                    )?);
                    str887.push_str(" mm");
                    Val::Str(str887)
                })?;
                d.set(Val::Str("PUMP_SKIRT_DEPTH".into()), {
                    let mut str889 = String::new();
                    str889.push_str(&format(
                        &e.get("e")?.attr("_tray")?.attr("skirt_depth")?,
                        &val_string({
                            let mut str890 = String::new();
                            str890.push_str("g");
                            Val::Str(str890)
                        })?,
                    )?);
                    str889.push_str(" mm");
                    Val::Str(str889)
                })?;
                d.set(Val::Str("PLATE_FOOT_X".into()), {
                    let mut str891 = String::new();
                    str891.push_str(&format(
                        &e.get("e")?.attr("plate_foot_reach")?,
                        &val_string({
                            let mut str892 = String::new();
                            str892.push_str("g");
                            Val::Str(str892)
                        })?,
                    )?);
                    str891.push_str(" mm");
                    Val::Str(str891)
                })?;
                d.set(Val::Str("PLATE_FOOT_Y".into()), {
                    let mut str893 = String::new();
                    str893.push_str(&format(
                        &e.get("e")?.attr("plate_foot_y")?,
                        &val_string({
                            let mut str894 = String::new();
                            str894.push_str("g");
                            Val::Str(str894)
                        })?,
                    )?);
                    str893.push_str(" mm");
                    Val::Str(str893)
                })?;
                d.set(Val::Str("PLATE_FOOT_T".into()), {
                    let mut str895 = String::new();
                    str895.push_str(&format(
                        &e.get("e")?.attr("plate_foot_t")?,
                        &val_string({
                            let mut str896 = String::new();
                            str896.push_str("g");
                            Val::Str(str896)
                        })?,
                    )?);
                    str895.push_str(" mm");
                    Val::Str(str895)
                })?;
                d.set(Val::Str("PLATE_FOOT_ANGLE".into()), {
                    let mut str897 = String::new();
                    str897.push_str(&format(
                        &e.get("e")?.attr("plate_foot_corbel_angle")?,
                        &val_string({
                            let mut str898 = String::new();
                            str898.push_str("g");
                            Val::Str(str898)
                        })?,
                    )?);
                    str897.push_str("°");
                    Val::Str(str897)
                })?;
                d.set(Val::Str("PUMP_TUBE_GATE_WIDTH".into()), {
                    let mut str899 = String::new();
                    str899.push_str(&format(
                        &e.get("TUBE_GATE_WIDTH")?,
                        &val_string({
                            let mut str900 = String::new();
                            str900.push_str("g");
                            Val::Str(str900)
                        })?,
                    )?);
                    str899.push_str(" mm");
                    Val::Str(str899)
                })?;
                d.set(Val::Str("PUMP_SHARED_WIRE_SPAN".into()), {
                    let mut str901 = String::new();
                    str901.push_str(&format(
                        &binary("mul", Val::Int(2i64), e.get("SHARED_HALF_SPAN")?)?,
                        &val_string({
                            let mut str902 = String::new();
                            str902.push_str("g");
                            Val::Str(str902)
                        })?,
                    )?);
                    str901.push_str(" mm");
                    Val::Str(str901)
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
