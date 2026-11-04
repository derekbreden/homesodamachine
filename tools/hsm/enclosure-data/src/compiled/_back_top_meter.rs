//! Plain roof piers for the meter's two fixed collars.
//!
//! Each pier has an open west-facing bearing and a straight strap passage.
//! Three millimetres of stock back the seats and passages. One broad fore
//! column carries both the meter and ASSE; their strap openings remain open.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("importlib", rt.import_module("importlib")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",
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
    e.set("HERE", assigned2.clone())?;
    let assigned9 = e.get("HERE")?.attr("parents")?.get(Val::Int(2i64))?;
    e.set("HW", assigned9.clone())?;
    let assigned10 = {
        let mut s = Vec::new();
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",
                line!(),
            );
            {
                let fun13 = e.get("str")?;
                let mut args11 = Vec::new();
                let mut kw12 = Vec::new();
                args11.push(binary(
                    "truediv",
                    e.get("HW")?,
                    Val::Str("manifold-layout".into()),
                )?);
                fun13.call(args11, kw12)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",
                line!(),
            );
            {
                let fun16 = e.get("str")?;
                let mut args14 = Vec::new();
                let mut kw15 = Vec::new();
                args14.push(binary("truediv", e.get("HW")?, Val::Str("scripts".into()))?);
                fun16.call(args14, kw15)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",
                line!(),
            );
            {
                let fun19 = e.get("str")?;
                let mut args17 = Vec::new();
                let mut kw18 = Vec::new();
                args17.push(binary(
                    "truediv",
                    e.get("HW")?,
                    Val::Str("reference/digiten-flow-sensor".into()),
                )?);
                fun19.call(args17, kw18)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",
                line!(),
            );
            {
                let fun22 = e.get("str")?;
                let mut args20 = Vec::new();
                let mut kw21 = Vec::new();
                args20.push(binary(
                    "truediv",
                    e.get("HW")?,
                    Val::Str("printed-parts/cadlib".into()),
                )?);
                fun22.call(args20, kw21)?
            }
        });
        Val::list(s)
    };
    e.get("sys")?.attr("path")?.set(
        Val::Slice {
            start: None,
            stop: Some(Val::Int(0i64).integer()?),
            step: 1,
        },
        assigned10.clone(),
    )?;
    e.set("layout", rt.import_module("above_core")?)?;
    // meter_support_datums
    e.set("meter_support_datums",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("fits",rt.import_module("fits")?)?;
let assigned23={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun26=e.get("importlib")?.attr("import_module")?;let mut args24=Vec::new();let mut kw25=Vec::new();args24.push(Val::Str("digiten_flow_sensor".into()));fun26.call(args24,kw25)?}};e.set("meter",assigned23.clone())?;
let assigned27={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun30=e.get("meter")?.attr("mounting_profile")?;let mut args28=Vec::new();let mut kw29=Vec::new();args28.push(Val::Int(1i64));fun30.call(args28,kw29)?}}.get(unary("neg",Val::Int(1i64))?)?;let unpack31=unpack(assigned27.clone(),4)?;e.set("first",unpack31[0].clone())?;e.set("last",unpack31[1].clone())?;e.set("r0",unpack31[2].clone())?;e.set("r1",unpack31[3].clone())?;
let assigned32={let mut s=Vec::new();s.push(binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun35=e.get("max")?;let mut args33=Vec::new();let mut kw34=Vec::new();args33.push(e.get("r0")?);args33.push(e.get("r1")?);fun35.call(args33,kw34)?}},e.get("fits")?.attr("slip")?)?);s.push(Val::Float(3.0f64));Val::tuple(s)};let unpack36=unpack(assigned32.clone(),2)?;e.set("radius",unpack36[0].clone())?;e.set("wall",unpack36[1].clone())?;
let assigned37={let mut s=Vec::new();Val::list(s)};e.set("result",assigned37.clone())?;
for item38 in {let mut s=Vec::new();s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Int(1i64));Val::tuple(s)}.iter()? {
e.set("side",item38)?;let assigned39=if {let v40=e.get("side")?;let v41=unary("neg",Val::Int(1i64))?;Val::Bool(compare("eq",v40.clone(),v41.clone())?.truthy()?)}.truthy()? {binary("truediv",unary("neg",binary("add",e.get("first")?,e.get("last")?)?)?,Val::Float(2.0f64))?} else {Val::Float(21.5f64)};e.set("station",assigned39.clone())?;
let assigned42={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun45=e.get("layout")?.attr("point")?;let mut args43=Vec::new();let mut kw44=Vec::new();args43.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun48=e.get("layout")?.attr("pose")?;let mut args46=Vec::new();let mut kw47=Vec::new();args46.push(Val::Str("digiten-flow".into()));fun48.call(args46,kw47)?}});args43.push({let mut s=Vec::new();s.push(e.get("station")?);s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)});fun45.call(args43,kw44)?}};let unpack49=unpack(assigned42.clone(),3)?;e.set("x",unpack49[0].clone())?;e.set("y",unpack49[1].clone())?;e.set("z",unpack49[2].clone())?;
let assigned50=if {let v51=e.get("side")?;let v52=unary("neg",Val::Int(1i64))?;Val::Bool(compare("eq",v51.clone(),v52.clone())?.truthy()?)}.truthy()? {{let mut s=Vec::new();s.push(Val::Float(44.5f64));s.push(Val::Float(361.0f64));s.push(binary("sub",binary("sub",e.get("z")?,e.get("radius")?)?,e.get("wall")?)?);Val::tuple(s)}} else {{let mut s=Vec::new();s.push(binary("add",e.get("x")?,Val::Float(2.5f64))?);s.push(binary("sub",e.get("y")?,Val::Float(4.5f64))?);s.push(binary("sub",binary("sub",e.get("z")?,e.get("radius")?)?,e.get("wall")?)?);Val::tuple(s)}};e.set("low",assigned50.clone())?;
let assigned53={let mut s=Vec::new();s.push(Val::Float(63.0f64));s.push(binary("add",e.get("y")?,Val::Float(4.5f64))?);s.push(Val::Float(355.0f64));Val::tuple(s)};e.set("high",assigned53.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun56=e.get("result")?.attr("append")?;let mut args54=Vec::new();let mut kw55=Vec::new();args54.push({let d=Val::dict(vec![]);d.set(Val::Str("parent".into()),Val::Str("enclosure-back-top".into()))?;d.set(Val::Str("centre_world_mm".into()),{let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);s.push(e.get("z")?);Val::tuple(s)})?;d.set(Val::Str("width_mm".into()),binary("sub",e.get("high")?.get(Val::Int(1i64))?,e.get("low")?.get(Val::Int(1i64))?)?)?;d.set(Val::Str("seat_radius_mm".into()),e.get("radius")?)?;d.set(Val::Str("wall_mm".into()),e.get("wall")?)?;d.set(Val::Str("native_bearing_band_mm".into()),if {let v57=e.get("side")?;let v58=unary("neg",Val::Int(1i64))?;Val::Bool(compare("eq",v57.clone(),v58.clone())?.truthy()?)}.truthy()? {{let mut s=Vec::new();s.push(binary("sub",e.get("station")?,Val::Float(3.0f64))?);s.push(binary("add",e.get("station")?,Val::Float(3.0f64))?);Val::tuple(s)}} else {{let mut s=Vec::new();s.push(binary("sub",e.get("station")?,Val::Float(1.5f64))?);s.push(binary("add",e.get("station")?,Val::Float(4.5f64))?);Val::tuple(s)}})?;d.set(Val::Str("stock_min_world_mm".into()),e.get("low")?)?;d.set(Val::Str("stock_max_world_mm".into()),e.get("high")?)?;d.set(Val::Str("seat_bottom_world_z_mm".into()),e.get("low")?.get(Val::Int(2i64))?)?;d.set(Val::Str("roof_root_world_z_mm".into()),Val::Float(346.0f64))?;d.set(Val::Str("tie_plane_world_y_mm".into()),e.get("y")?)?;d.set(Val::Str("tie_slot_min_world_mm".into()),{let mut s=Vec::new();s.push(binary("sub",e.get("low")?.get(Val::Int(0i64))?,Val::Float(0.1f64))?);s.push(binary("sub",e.get("y")?,Val::Float(1.5f64))?);s.push(binary("add",binary("add",e.get("z")?,e.get("radius")?)?,e.get("wall")?)?);Val::tuple(s)})?;d.set(Val::Str("tie_slot_max_world_mm".into()),{let mut s=Vec::new();s.push(binary("add",e.get("high")?.get(Val::Int(0i64))?,Val::Float(0.1f64))?);s.push(binary("add",e.get("y")?,Val::Float(1.5f64))?);s.push(binary("add",binary("add",e.get("z")?,e.get("radius")?)?,binary("mul",Val::Float(2.0f64),e.get("wall")?)?)?);Val::tuple(s)})?;d.set(Val::Str("tie_backing_x_mm".into()),Val::Float(52.5f64))?;d.set(Val::Str("asse_bore".into()),if {let v59=e.get("side")?;let v60=unary("neg",Val::Int(1i64))?;Val::Bool(compare("eq",v59.clone(),v60.clone())?.truthy()?)}.truthy()? {{let d=Val::dict(vec![]);d.set(Val::Str("centre_xz_mm".into()),{let mut s=Vec::new();s.push(Val::Float(37.25f64));s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun63=e.get("layout")?.attr("pose")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push(Val::Str("asse1022-assembly".into()));fun63.call(args61,kw62)?}}.get(Val::Str("translation_mm".into()))?.get(Val::Int(2i64))?);Val::tuple(s)})?;d.set(Val::Str("radius_mm".into()),Val::Float(16.75f64))?;d}} else {Val::None})?;d.set(Val::Str("body_setback".into()),if {let v64=e.get("side")?;let v65=Val::Int(1i64);Val::Bool(compare("eq",v64.clone(),v65.clone())?.truthy()?)}.truthy()? {{let d=Val::dict(vec![]);d.set(Val::Str("fore_face_y_mm".into()),binary("sub",e.get("y")?,Val::Float(1.5f64))?)?;d.set(Val::Str("top_z_mm".into()),Val::Float(315.0f64))?;d}} else {Val::None})?;d});fun56.call(args54,kw55)?}};
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun68=e.get("tuple")?;let mut args66=Vec::new();let mut kw67=Vec::new();args66.push(e.get("result")?);fun68.call(args66,kw67)?}});
Ok(Val::None)})})?;
    // meter_tie_routes
    e.set("meter_tie_routes",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned69={let d=Val::dict(vec![]);d};e.set("result",assigned69.clone())?;
for item70 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun73=e.get("enumerate")?;let mut args71=Vec::new();let mut kw72=Vec::new();args71.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun76=e.get("meter_support_datums")?;let mut args74=Vec::new();let mut kw75=Vec::new();fun76.call(args74,kw75)?}});fun73.call(args71,kw72)?}}.iter()? {
let unpack77=unpack(item70,2)?;e.set("number",unpack77[0].clone())?;e.set("data",unpack77[1].clone())?;let assigned78=e.get("data")?.get(Val::Str("centre_world_mm".into()))?;let unpack79=unpack(assigned78.clone(),3)?;e.set("x",unpack79[0].clone())?;e.set("y",unpack79[1].clone())?;e.set("z",unpack79[2].clone())?;
let assigned80={let mut s=Vec::new();s.push(e.get("data")?.get(Val::Str("stock_min_world_mm".into()))?);s.push(e.get("data")?.get(Val::Str("stock_max_world_mm".into()))?);Val::tuple(s)};let unpack81=unpack(assigned80.clone(),2)?;e.set("low",unpack81[0].clone())?;e.set("high",unpack81[1].clone())?;
let assigned82=binary("add",e.get("data")?.get(Val::Str("seat_radius_mm".into()))?,Val::Float(0.6f64))?;e.set("radius",assigned82.clone())?;
let assigned83={let mut s=Vec::new();s.push(e.get("data")?.get(Val::Str("tie_slot_min_world_mm".into()))?);s.push(e.get("data")?.get(Val::Str("tie_slot_max_world_mm".into()))?);Val::tuple(s)};let unpack84=unpack(assigned83.clone(),2)?;e.set("a",unpack84[0].clone())?;e.set("b",unpack84[1].clone())?;
let assigned85=binary("truediv",binary("add",e.get("a")?.get(Val::Int(2i64))?,e.get("b")?.get(Val::Int(2i64))?)?,Val::Float(2.0f64))?;e.set("upper_z",assigned85.clone())?;
let assigned86=binary("sub",e.get("low")?.get(Val::Int(2i64))?,Val::Float(0.6f64))?;e.set("lower_z",assigned86.clone())?;
let assigned87={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("sub",e.get("low")?.get(Val::Int(0i64))?,Val::Float(0.6f64))?);s.push(e.get("y")?);s.push(e.get("upper_z")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",e.get("low")?.get(Val::Int(0i64))?,Val::Float(0.6f64))?);s.push(e.get("y")?);s.push(e.get("lower_z")?);Val::tuple(s)});Val::tuple(s)};let unpack88=unpack(assigned87.clone(),2)?;e.set("upper_west",unpack88[0].clone())?;e.set("lower_west",unpack88[1].clone())?;
let assigned89={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("add",e.get("high")?.get(Val::Int(0i64))?,Val::Float(0.6f64))?);s.push(e.get("y")?);s.push(e.get("upper_z")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",e.get("high")?.get(Val::Int(0i64))?,Val::Float(0.6f64))?);s.push(e.get("y")?);s.push(e.get("lower_z")?);Val::tuple(s)});Val::tuple(s)};let unpack90=unpack(assigned89.clone(),2)?;e.set("upper_east",unpack90[0].clone())?;e.set("lower_east",unpack90[1].clone())?;
// tangent
e.set("tangent",{let params=vec![("point".into(),None,false),("sign".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned91={let mut s=Vec::new();s.push(binary("sub",e.get("point")?.get(Val::Int(0i64))?,e.get("x")?)?);s.push(binary("sub",e.get("point")?.get(Val::Int(2i64))?,e.get("z")?)?);Val::tuple(s)};let unpack92=unpack(assigned91.clone(),2)?;e.set("dx",unpack92[0].clone())?;e.set("dz",unpack92[1].clone())?;
return Ok(binary("mod",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun95=e.get("math")?.attr("degrees")?;let mut args93=Vec::new();let mut kw94=Vec::new();args93.push(binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun98=e.get("math")?.attr("atan2")?;let mut args96=Vec::new();let mut kw97=Vec::new();args96.push(e.get("dz")?);args96.push(e.get("dx")?);fun98.call(args96,kw97)?}},binary("mul",e.get("sign")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun101=e.get("math")?.attr("acos")?;let mut args99=Vec::new();let mut kw100=Vec::new();args99.push(binary("truediv",e.get("radius")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun104=e.get("math")?.attr("hypot")?;let mut args102=Vec::new();let mut kw103=Vec::new();args102.push(e.get("dx")?);args102.push(e.get("dz")?);fun104.call(args102,kw103)?}})?);fun101.call(args99,kw100)?}})?)?);fun95.call(args93,kw94)?}},Val::Float(360.0f64))?);
Ok(Val::None)})})?;
let assigned105={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun108=e.get("tangent")?;let mut args106=Vec::new();let mut kw107=Vec::new();args106.push(e.get("lower_west")?);args106.push(unary("neg",Val::Int(1i64))?);fun108.call(args106,kw107)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun111=e.get("tangent")?;let mut args109=Vec::new();let mut kw110=Vec::new();args109.push(e.get("upper_west")?);args109.push(Val::Int(1i64));fun111.call(args109,kw110)?}});Val::tuple(s)};let unpack112=unpack(assigned105.clone(),2)?;e.set("lower_angle",unpack112[0].clone())?;e.set("upper_angle",unpack112[1].clone())?;
// point
e.set("point",{let params=vec![("angle".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned113={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun116=e.get("math")?.attr("radians")?;let mut args114=Vec::new();let mut kw115=Vec::new();args114.push(e.get("angle")?);fun116.call(args114,kw115)?}};e.set("theta",assigned113.clone())?;
return Ok({let mut s=Vec::new();s.push(binary("add",e.get("x")?,binary("mul",e.get("radius")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun119=e.get("math")?.attr("cos")?;let mut args117=Vec::new();let mut kw118=Vec::new();args117.push(e.get("theta")?);fun119.call(args117,kw118)?}})?)?);s.push(e.get("y")?);s.push(binary("add",e.get("z")?,binary("mul",e.get("radius")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun122=e.get("math")?.attr("sin")?;let mut args120=Vec::new();let mut kw121=Vec::new();args120.push(e.get("theta")?);fun122.call(args120,kw121)?}})?)?);Val::tuple(s)});
Ok(Val::None)})})?;
// line
e.set("line",{let params=vec![("a".into(),None,false),("b".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let d=Val::dict(vec![]);d.set(Val::Str("kind".into()),Val::Str("line".into()))?;d.set(Val::Str("points_mm".into()),{let mut s=Vec::new();s.push(e.get("a")?);s.push(e.get("b")?);Val::list(s)})?;d.set(Val::Str("wide_axis".into()),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)})?;d});
Ok(Val::None)})})?;
let assigned123={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun126=e.get("point")?;let mut args124=Vec::new();let mut kw125=Vec::new();args124.push(e.get("lower_angle")?);fun126.call(args124,kw125)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun129=e.get("point")?;let mut args127=Vec::new();let mut kw128=Vec::new();args127.push(e.get("upper_angle")?);fun129.call(args127,kw128)?}});Val::tuple(s)};let unpack130=unpack(assigned123.clone(),2)?;e.set("lower",unpack130[0].clone())?;e.set("upper",unpack130[1].clone())?;
let assigned131={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun134=e.get("line")?;let mut args132=Vec::new();let mut kw133=Vec::new();args132.push(e.get("upper_west")?);args132.push(e.get("upper_east")?);fun134.call(args132,kw133)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun137=e.get("line")?;let mut args135=Vec::new();let mut kw136=Vec::new();args135.push(e.get("upper_east")?);args135.push(e.get("lower_east")?);fun137.call(args135,kw136)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun140=e.get("line")?;let mut args138=Vec::new();let mut kw139=Vec::new();args138.push(e.get("lower_east")?);args138.push(e.get("lower_west")?);fun140.call(args138,kw139)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun143=e.get("line")?;let mut args141=Vec::new();let mut kw142=Vec::new();args141.push(e.get("lower_west")?);args141.push(e.get("lower")?);fun143.call(args141,kw142)?}});s.push({let d=Val::dict(vec![]);d.set(Val::Str("kind".into()),Val::Str("arc".into()))?;d.set(Val::Str("points_mm".into()),{let mut s=Vec::new();s.push(e.get("lower")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun146=e.get("point")?;let mut args144=Vec::new();let mut kw145=Vec::new();args144.push(binary("truediv",binary("add",e.get("lower_angle")?,e.get("upper_angle")?)?,Val::Float(2.0f64))?);fun146.call(args144,kw145)?}});s.push(e.get("upper")?);Val::list(s)})?;d.set(Val::Str("radius_mm".into()),e.get("radius")?)?;d.set(Val::Str("sweep_degrees".into()),binary("sub",e.get("upper_angle")?,e.get("lower_angle")?)?)?;d.set(Val::Str("wide_axis".into()),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)})?;d});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun149=e.get("line")?;let mut args147=Vec::new();let mut kw148=Vec::new();args147.push(e.get("upper")?);args147.push(e.get("upper_west")?);fun149.call(args147,kw148)?}});Val::list(s)};e.set("segments",assigned131.clone())?;
let assigned150={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun153=e.get("sum")?;let mut args151=Vec::new();let mut kw152=Vec::new();args151.push({let e=e.child();let out154=Val::list(vec![]);for item155 in e.get("segments")?.iter()? {e.set("row",item155)?;out154.attr("append")?.call(vec![if {let v156=e.get("row")?.get(Val::Str("kind".into()))?;let v157=Val::Str("line".into());Val::Bool(compare("eq",v156.clone(),v157.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun160=e.get("math")?.attr("dist")?;let mut args158=Vec::new();let mut kw159=Vec::new();args158.extend(e.get("row")?.get(Val::Str("points_mm".into()))?.iter()?);fun160.call(args158,kw159)?}}} else {binary("mul",e.get("radius")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun163=e.get("abs")?;let mut args161=Vec::new();let mut kw162=Vec::new();args161.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_back_top_meter.rs",line!());{let fun166=e.get("math")?.attr("radians")?;let mut args164=Vec::new();let mut kw165=Vec::new();args164.push(e.get("row")?.get(Val::Str("sweep_degrees".into()))?);fun166.call(args164,kw165)?}});fun163.call(args161,kw162)?}})?}],vec![])?;}out154});fun153.call(args151,kw152)?}};e.set("length",assigned150.clone())?;
let assigned167={let d=Val::dict(vec![]);d.set(Val::Str("parent".into()),Val::Str("enclosure-back-top".into()))?;d.set(Val::Str("segments".into()),e.get("segments")?)?;d.set(Val::Str("length_mm".into()),e.get("length")?)?;d.set(Val::Str("stock".into()),Val::Str("6-inch narrow nylon tie".into()))?;d.set(Val::Str("stock_length_mm".into()),Val::Float(152.4f64))?;d.set(Val::Str("width_mm".into()),Val::Float(2.5f64))?;d.set(Val::Str("thickness_mm".into()),Val::Float(0.8f64))?;d.set(Val::Str("collar_plane_world_y_mm".into()),e.get("y")?)?;d.set(Val::Str("strip_basis".into()),Val::Str("Nominal layout section; purchased strap/head dimensions unmeasured".into()))?;d};e.get("result")?.set(binary("add",Val::Str("meter-".into()),if {let v168=e.get("number")?;let v169=Val::Int(0i64);Val::Bool(compare("eq",v168.clone(),v169.clone())?.truthy()?)}.truthy()? {Val::Str("fore".into())} else {Val::Str("aft".into())})?,assigned167.clone())?;
}
return Ok(e.get("result")?);
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
