//! Selected integral tube snaps on back-top's roof and east wall.
//!
//! The listed world-space line endpoints and parameters are explicit routing
//! datums; this registry does not infer clearance or follow an unrelated route
//! edit. Back-top builds in machine -Z. Each flavor station shares one filled
//! root bridge while its two seats remain individual routing records.
//!
//! Quarter-inch tube retains the selected C2 section: diameter 6.35, wing 2.40.
//! The 4 mm tube uses diameter 4.10 and a 1.52 mm functional spring section scaled
//! from C2's proportions. That smaller section is a modeled fit estimate.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    let assigned1 = {
        let mut s = Vec::new();
        s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun4=e.get("dict")?;let mut args2=Vec::new();let mut kw3=Vec::new();kw3.push(("id".into(),Val::Str("tube-snap-reservoir-a-fill-east".into())));kw3.push(("route_id".into(),Val::Str("fluid-14".into())));kw3.push(("endpoints".into(),{let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Float(94.31f64));s.push(Val::Float(244.0f64));s.push(Val::Float(258.5f64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(94.31f64));s.push(Val::Float(286.0f64));s.push(Val::Float(258.5f64));Val::tuple(s)});Val::tuple(s)}));kw3.push(("face_axis".into(),Val::Int(0i64)));kw3.push(("face".into(),Val::Float(98.5f64)));kw3.push(("outward".into(),{let mut s=Vec::new();s.push(unary("neg",Val::Float(1.0f64))?);s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)}));kw3.push(("tube_od".into(),Val::Float(6.35f64)));kw3.push(("bore_diameter".into(),Val::Float(6.35f64)));kw3.push(("wing".into(),Val::Float(2.4f64)));kw3.push(("source".into(),Val::Str("hardware/manifold-layout/reservoir-a-routes.json".into())));kw3.push(("source_function".into(),Val::Str("fluid-14.segments".into())));kw3.push(("source_segment".into(),Val::Int(12i64)));kw3.push(("install_before".into(),{let mut s=Vec::new();s.push(Val::Str("fluid-16".into()));Val::tuple(s)}));kw3.push(("basis".into(),Val::Str("East-wall fill straight; seat fill before draw and use the integral fore C2 seats on the cold-core lid.".into())));fun4.call(args2,kw3)?}});
        Val::tuple(s)
    };
    e.set("_SITES", assigned1.clone())?;
    let assigned5 = {
        let e = e.child();
        let out6 = Val::dict(vec![]);
        for item7 in {
            let mut s = Vec::new();
            s.push(Val::Int(354i64));
            s.push(Val::Int(390i64));
            Val::tuple(s)
        }
        .iter()?
        {
            e.set("y", item7)?;
            out6.set(
                {
                    let mut str8 = String::new();
                    str8.push_str("tube-snap-flavor-roof-");
                    str8.push_str(&format(&e.get("y")?, &String::new())?);
                    Val::Str(str8)
                },
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",
                        line!(),
                    );
                    {
                        let fun11 = e.get("dict")?;
                        let mut args9 = Vec::new();
                        let mut kw10 = Vec::new();
                        kw10.push(("id".into(), {
                            let mut str12 = String::new();
                            str12.push_str("tube-snap-flavor-roof-");
                            str12.push_str(&format(&e.get("y")?, &String::new())?);
                            Val::Str(str12)
                        }));
                        kw10.push(("bridge_origin".into(), {
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Float(51.53f64))?);
                            s.push(binary("sub", e.get("y")?, Val::Float(4.0f64))?);
                            s.push(Val::Float(343.0f64));
                            Val::tuple(s)
                        }));
                        kw10.push(("bridge_size".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Float(3.06f64));
                            s.push(Val::Float(8.0f64));
                            s.push(Val::Float(3.1f64));
                            Val::tuple(s)
                        }));
                        fun11.call(args9, kw10)?
                    }
                },
            )?;
        }
        out6
    };
    e.set("_SHARED_ROOTS", assigned5.clone())?;
    // tube_sites
    e.set("tube_sites",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned13={let mut s=Vec::new();Val::list(s)};e.set("result",assigned13.clone())?;
for item14 in e.get("_SITES")?.iter()? {
e.set("row",item14)?;let assigned15=e.get("row")?.get(Val::Str("endpoints".into()))?;let unpack16=unpack(assigned15.clone(),2)?;e.set("first",unpack16[0].clone())?;e.set("last",unpack16[1].clone())?;
let assigned17={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun20=e.get("row")?.attr("get")?;let mut args18=Vec::new();let mut kw19=Vec::new();args18.push(Val::Str("line_parameter".into()));args18.push(Val::Float(0.5f64));fun20.call(args18,kw19)?}};e.set("parameter",assigned17.clone())?;
let assigned21={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun24=e.get("tuple")?;let mut args22=Vec::new();let mut kw23=Vec::new();args22.push({let e=e.child();let out25=Val::list(vec![]);for item26 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun29=e.get("zip")?;let mut args27=Vec::new();let mut kw28=Vec::new();args27.push(e.get("first")?);args27.push(e.get("last")?);fun29.call(args27,kw28)?}}.iter()? {let unpack30=unpack(item26,2)?;e.set("a",unpack30[0].clone())?;e.set("b",unpack30[1].clone())?;out25.attr("append")?.call(vec![binary("add",e.get("a")?,binary("mul",binary("sub",e.get("b")?,e.get("a")?)?,e.get("parameter")?)?)?],vec![])?;}out25});fun24.call(args22,kw23)?}};e.set("centre",assigned21.clone())?;
let assigned31={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun34=e.get("math")?.attr("dist")?;let mut args32=Vec::new();let mut kw33=Vec::new();args32.push(e.get("first")?);args32.push(e.get("last")?);fun34.call(args32,kw33)?}};e.set("length",assigned31.clone())?;
let assigned35={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun38=e.get("tuple")?;let mut args36=Vec::new();let mut kw37=Vec::new();args36.push({let e=e.child();let out39=Val::list(vec![]);for item40 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun43=e.get("zip")?;let mut args41=Vec::new();let mut kw42=Vec::new();args41.push(e.get("first")?);args41.push(e.get("last")?);fun43.call(args41,kw42)?}}.iter()? {let unpack44=unpack(item40,2)?;e.set("a",unpack44[0].clone())?;e.set("b",unpack44[1].clone())?;out39.attr("append")?.call(vec![binary("truediv",binary("sub",e.get("b")?,e.get("a")?)?,e.get("length")?)?],vec![])?;}out39});fun38.call(args36,kw37)?}};e.set("along",assigned35.clone())?;
let assigned45={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun48=e.get("abs")?;let mut args46=Vec::new();let mut kw47=Vec::new();args46.push(binary("sub",e.get("row")?.get(Val::Str("face".into()))?,e.get("centre")?.get(e.get("row")?.get(Val::Str("face_axis".into()))?)?)?);fun48.call(args46,kw47)?}};e.set("root_distance",assigned45.clone())?;
let assigned49={let mut s=Vec::new();s.push(binary("sub",binary("mul",e.get("length")?,e.get("parameter")?)?,Val::Float(4.0f64))?);s.push(binary("sub",binary("mul",e.get("length")?,binary("sub",Val::Float(1.0f64),e.get("parameter")?)?)?,Val::Float(4.0f64))?);Val::tuple(s)};e.set("end_clearances",assigned49.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun52=e.get("result")?.attr("append")?;let mut args50=Vec::new();let mut kw51=Vec::new();args50.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun55=e.get("dict")?;let mut args53=Vec::new();let mut kw54=Vec::new();kw54.push(("id".into(),e.get("row")?.get(Val::Str("id".into()))?));kw54.push(("route_id".into(),e.get("row")?.get(Val::Str("route_id".into()))?));kw54.push(("host".into(),Val::Str("enclosure-back-top".into())));kw54.push(("centre".into(),e.get("centre")?));kw54.push(("along".into(),e.get("along")?));kw54.push(("outward".into(),e.get("row")?.get(Val::Str("outward".into()))?));kw54.push(("root_distance".into(),e.get("root_distance")?));kw54.push(("tube_od".into(),e.get("row")?.get(Val::Str("tube_od".into()))?));kw54.push(("bore_diameter".into(),e.get("row")?.get(Val::Str("bore_diameter".into()))?));kw54.push(("wing".into(),e.get("row")?.get(Val::Str("wing".into()))?));kw54.push(("span".into(),Val::Float(8.0f64)));kw54.push(("print_up".into(),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(unary("neg",Val::Float(1.0f64))?);Val::tuple(s)}));kw54.push(("basis".into(),e.get("row")?.get(Val::Str("basis".into()))?));kw54.push(("install_before".into(),e.get("row")?.get(Val::Str("install_before".into()))?));kw54.extend(keyword_items(if {let v56=Val::Str("group".into());let v57=e.get("row")?;Val::Bool(compare("in",v56.clone(),v57.clone())?.truthy()?)}.truthy()? {{let d=Val::dict(vec![]);d.set(Val::Str("group".into()),e.get("_SHARED_ROOTS")?.get(e.get("row")?.get(Val::Str("group".into()))?)?)?;d}} else {{let d=Val::dict(vec![]);d}})?);kw54.push(("source_parameter".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun60=e.get("dict")?;let mut args58=Vec::new();let mut kw59=Vec::new();kw59.push(("file".into(),e.get("row")?.get(Val::Str("source".into()))?));kw59.push(("function".into(),e.get("row")?.get(Val::Str("source_function".into()))?));kw59.push(("native_segment_index".into(),e.get("row")?.get(Val::Str("source_segment".into()))?));kw59.push(("line_endpoints_world_mm".into(),e.get("row")?.get(Val::Str("endpoints".into()))?));kw59.push(("line_parameter".into(),e.get("parameter")?));kw59.push(("straight_end_clearance_mm".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun63=e.get("min")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push(e.get("end_clearances")?);fun63.call(args61,kw62)?}}));kw59.push(("straight_end_clearances_mm".into(),e.get("end_clearances")?));kw59.push(("host_face_axis".into(),Val::Str("XYZ".into()).get(e.get("row")?.get(Val::Str("face_axis".into()))?)?));kw59.push(("host_face_coordinate_mm".into(),e.get("row")?.get(Val::Str("face".into()))?));fun60.call(args58,kw59)?}}));fun55.call(args53,kw54)?}});fun52.call(args50,kw51)?}};
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_tube_snap_sites.rs",line!());{let fun66=e.get("tuple")?;let mut args64=Vec::new();let mut kw65=Vec::new();args64.push(e.get("result")?);fun66.call(args64,kw65)?}});
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
