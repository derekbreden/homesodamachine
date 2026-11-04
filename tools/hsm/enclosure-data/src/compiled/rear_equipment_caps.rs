//! Four removable snap caps for the rear inlet equipment.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
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
    let assigned9 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
            line!(),
        );
        {
            let fun12 = e.get("next")?;
            let mut args10 = Vec::new();
            let mut kw11 = Vec::new();
            args10.push({
                let e = e.child();
                let out13 = Val::list(vec![]);
                for item14 in e.get("HERE")?.attr("parents")?.iter()? {
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
        }
    };
    e.set("HW", assigned9.clone())?;
    let assigned17 = {
        let mut s = Vec::new();
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
                line!(),
            );
            {
                let fun20 = e.get("str")?;
                let mut args18 = Vec::new();
                let mut kw19 = Vec::new();
                args18.push(binary(
                    "truediv",
                    e.get("HW")?,
                    Val::Str("manifold-layout".into()),
                )?);
                fun20.call(args18, kw19)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
                line!(),
            );
            {
                let fun23 = e.get("str")?;
                let mut args21 = Vec::new();
                let mut kw22 = Vec::new();
                args21.push(binary("truediv", e.get("HW")?, Val::Str("scripts".into()))?);
                fun23.call(args21, kw22)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
                line!(),
            );
            {
                let fun26 = e.get("str")?;
                let mut args24 = Vec::new();
                let mut kw25 = Vec::new();
                args24.push(binary(
                    "truediv",
                    e.get("HW")?,
                    Val::Str("printed-parts/cadlib".into()),
                )?);
                fun26.call(args24, kw25)?
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
        assigned17.clone(),
    )?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
            line!(),
        );
        {
            let fun29 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args27 = Vec::new();
            let mut kw28 = Vec::new();
            args27.push(Val::Int(0i64));
            args27.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
                    line!(),
                );
                {
                    let fun32 = e.get("str")?;
                    let mut args30 = Vec::new();
                    let mut kw31 = Vec::new();
                    args30.push(binary(
                        "truediv",
                        e.get("HW")?,
                        Val::Str("printed-parts/cold-core".into()),
                    )?);
                    fun32.call(args30, kw31)?
                }
            });
            fun29.call(args27, kw28)?
        }
    };
    e.set("rear_plumbing", rt.import_module("rear_plumbing")?)?;
    let mod33 = rt.import_module("_materials")?;
    e.set("M_PETGF_BLACK", rt.member("_materials", "M_PETGF_BLACK")?)?;
    e.set("linear", rt.member("_materials", "linear")?)?;
    let assigned34 = {
        let mut s = Vec::new();
        s.push(Val::Str("asse-snap-cap".into()));
        s.push(Val::Str("pisco-snap-cap".into()));
        s.push(Val::Str("meter-snap-cap".into()));
        s.push(Val::Str("regulator-snap-cap".into()));
        Val::tuple(s)
    };
    e.set("NAMES", assigned34.clone())?;
    // _world_bounds
    e.set("_world_bounds",{let params=vec![("frame".into(),None,false),("lo".into(),None,false),("hi".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("layout",rt.import_module("above_core")?)?;
let assigned35={let e=e.child();let out36=Val::list(vec![]);for item37 in {let mut s=Vec::new();s.push(e.get("lo")?.get(Val::Int(0i64))?);s.push(e.get("hi")?.get(Val::Int(0i64))?);Val::tuple(s)}.iter()? {e.set("x",item37)?;for item38 in {let mut s=Vec::new();s.push(e.get("lo")?.get(Val::Int(1i64))?);s.push(e.get("hi")?.get(Val::Int(1i64))?);Val::tuple(s)}.iter()? {e.set("y",item38)?;for item39 in {let mut s=Vec::new();s.push(e.get("lo")?.get(Val::Int(2i64))?);s.push(e.get("hi")?.get(Val::Int(2i64))?);Val::tuple(s)}.iter()? {e.set("z",item39)?;out36.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun42=e.get("layout")?.attr("point")?;let mut args40=Vec::new();let mut kw41=Vec::new();args40.push(e.get("frame")?);args40.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);s.push(e.get("z")?);Val::tuple(s)});fun42.call(args40,kw41)?}}],vec![])?;}}}out36};e.set("points",assigned35.clone())?;
return Ok({let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun45=e.get("tuple")?;let mut args43=Vec::new();let mut kw44=Vec::new();args43.push({let e=e.child();let out46=Val::list(vec![]);for item47 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun50=e.get("range")?;let mut args48=Vec::new();let mut kw49=Vec::new();args48.push(Val::Int(3i64));fun50.call(args48,kw49)?}}.iter()? {e.set("k",item47)?;out46.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun53=e.get("min")?;let mut args51=Vec::new();let mut kw52=Vec::new();args51.push({let e=e.child();let out54=Val::list(vec![]);for item55 in e.get("points")?.iter()? {e.set("p",item55)?;out54.attr("append")?.call(vec![e.get("p")?.get(e.get("k")?)?],vec![])?;}out54});fun53.call(args51,kw52)?}}],vec![])?;}out46});fun45.call(args43,kw44)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun58=e.get("tuple")?;let mut args56=Vec::new();let mut kw57=Vec::new();args56.push({let e=e.child();let out59=Val::list(vec![]);for item60 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun63=e.get("range")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push(Val::Int(3i64));fun63.call(args61,kw62)?}}.iter()? {e.set("k",item60)?;out59.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun66=e.get("max")?;let mut args64=Vec::new();let mut kw65=Vec::new();args64.push({let e=e.child();let out67=Val::list(vec![]);for item68 in e.get("points")?.iter()? {e.set("p",item68)?;out67.attr("append")?.call(vec![e.get("p")?.get(e.get("k")?)?],vec![])?;}out67});fun66.call(args64,kw65)?}}],vec![])?;}out59});fun58.call(args56,kw57)?}});Val::tuple(s)});
Ok(Val::None)})})?;
    // numbers
    e.set("numbers",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("layout",rt.import_module("above_core")?)?;
e.set("parts",rt.import_module("above_core_parts")?)?;
e.set("snaps",rt.import_module("rear_snaps")?)?;
e.set("fits",rt.import_module("fits")?)?;
let assigned69={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun72=e.get("json")?.attr("loads")?;let mut args70=Vec::new();let mut kw71=Vec::new();args70.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun75=binary("truediv",e.get("HW")?,Val::Str("printed-parts/enclosure/enclosure/rear-seat-profiles.json".into()))?.attr("read_text")?;let mut args73=Vec::new();let mut kw74=Vec::new();fun75.call(args73,kw74)?}});fun72.call(args70,kw71)?}};e.set("profiles",assigned69.clone())?;
let assigned76={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun79=e.get("json")?.attr("loads")?;let mut args77=Vec::new();let mut kw78=Vec::new();args77.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun82=binary("truediv",e.get("HERE")?,Val::Str("rear-cap-profiles.json".into()))?.attr("read_text")?;let mut args80=Vec::new();let mut kw81=Vec::new();fun82.call(args80,kw81)?}});fun79.call(args77,kw78)?}};e.set("cap_profiles",assigned76.clone())?;
let assigned83={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun86=e.get("rear_plumbing")?.attr("snap_datums")?;let mut args84=Vec::new();let mut kw85=Vec::new();fun86.call(args84,kw85)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun89=e.get("rear_plumbing")?.attr("plan")?;let mut args87=Vec::new();let mut kw88=Vec::new();fun89.call(args87,kw88)?}});Val::tuple(s)};let unpack90=unpack(assigned83.clone(),2)?;e.set("datums",unpack90[0].clone())?;e.set("plan",unpack90[1].clone())?;
let assigned91={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun94=e.get("rear_plumbing")?.attr("chain")?;let mut args92=Vec::new();let mut kw93=Vec::new();fun94.call(args92,kw93)?}}.attr("bfp")?;e.set("bfp",assigned91.clone())?;
let assigned95={let mut s=Vec::new();s.push(e.get("fits")?.attr("running")?);s.push(e.get("fits")?.attr("slip")?);Val::tuple(s)};let unpack96=unpack(assigned95.clone(),2)?;e.set("c",unpack96[0].clone())?;e.set("s",unpack96[1].clone())?;
// runs
e.set("runs",{let params=vec![("rows".into(),None,false),("frame".into(),None,false),("air".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned97=e.get("frame")?.get(Val::Str("translation_mm".into()))?.get(Val::Int(1i64))?;e.set("t",assigned97.clone())?;
return Ok({let e=e.child();let out98=Val::list(vec![]);for item99 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun102=e.get("reversed")?;let mut args100=Vec::new();let mut kw101=Vec::new();args100.push(e.get("rows")?);fun102.call(args100,kw101)?}}.iter()? {let unpack103=unpack(item99,3)?;e.set("lo",unpack103[0].clone())?;e.set("hi",unpack103[1].clone())?;e.set("r",unpack103[2].clone())?;out98.attr("append")?.call(vec![{let mut s=Vec::new();s.push(binary("sub",e.get("t")?,e.get("hi")?)?);s.push(binary("sub",e.get("t")?,e.get("lo")?)?);s.push(binary("add",e.get("r")?,e.get("air")?)?);Val::tuple(s)}],vec![])?;}out98});
Ok(Val::None)})})?;
// box
e.set("box",{let params=vec![("x0".into(),None,false),("x1".into(),None,false),("y0".into(),None,false),("y1".into(),None,false),("z0".into(),None,false),("z1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let d=Val::dict(vec![]);d.set(Val::Str("op".into()),Val::Str("box".into()))?;d.set(Val::Str("bounds".into()),{let mut s=Vec::new();s.push(e.get("x0")?);s.push(e.get("x1")?);s.push(e.get("y0")?);s.push(e.get("y1")?);s.push(e.get("z0")?);s.push(e.get("z1")?);Val::tuple(s)})?;d});
Ok(Val::None)})})?;
// turned
e.set("turned",{let params=vec![("rows".into(),None,false),("axis".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let d=Val::dict(vec![]);d.set(Val::Str("op".into()),Val::Str("turned".into()))?;d.set(Val::Str("profile".into()),e.get("rows")?)?;d.set(Val::Str("axis".into()),e.get("axis")?)?;d});
Ok(Val::None)})})?;
let assigned104={let mut s=Vec::new();s.push(e.get("datums")?.get(Val::Str("asse_axis".into()))?);s.push(e.get("plan")?.get(Val::Str("chain_frame".into()))?);Val::tuple(s)};let unpack105=unpack(assigned104.clone(),2)?;e.set("axis",unpack105[0].clone())?;e.set("frame",unpack105[1].clone())?;
let assigned106={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun109=e.get("runs")?;let mut args107=Vec::new();let mut kw108=Vec::new();args107.push(e.get("profiles")?.get(Val::Str("asse".into()))?.get(Val::Str("seat_runs".into()))?);args107.push(e.get("frame")?);args107.push(e.get("c")?);fun109.call(args107,kw108)?}};e.set("seat",assigned106.clone())?;
let assigned110={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun113=e.get("max")?;let mut args111=Vec::new();let mut kw112=Vec::new();args111.push({let e=e.child();let out114=Val::list(vec![]);for item115 in e.get("bfp")?.attr("CAP_PROFILE")?.iter()? {let unpack116=unpack(item115,2)?;e.set("x",unpack116[0].clone())?;e.set("r",unpack116[1].clone())?;if {let v123=e.get("r")?;let v124={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun119=e.get("max")?;let mut args117=Vec::new();let mut kw118=Vec::new();args117.push({let e=e.child();let out120=Val::list(vec![]);for item121 in e.get("bfp")?.attr("CAP_PROFILE")?.iter()? {let unpack122=unpack(item121,2)?;e.set("_",unpack122[0].clone())?;e.set("r",unpack122[1].clone())?;out120.attr("append")?.call(vec![e.get("r")?],vec![])?;}out120});fun119.call(args117,kw118)?}};Val::Bool(compare("eq",v123.clone(),v124.clone())?.truthy()?)}.truthy()? {out114.attr("append")?.call(vec![e.get("x")?],vec![])?;}}out114});fun113.call(args111,kw112)?}};e.set("bonnet",assigned110.clone())?;
let assigned125={let mut s=Vec::new();s.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun128=e.get("layout")?.attr("point")?;let mut args126=Vec::new();let mut kw127=Vec::new();args126.push(e.get("frame")?);args126.push({let mut s=Vec::new();s.push(e.get("bonnet")?);s.push(Val::Float(0.0f64));s.push(e.get("bfp")?.attr("BODY_CENTER_Z")?);Val::tuple(s)});fun128.call(args126,kw127)?}}.get(Val::Int(1i64))?,e.get("s")?)?);s.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun131=e.get("layout")?.attr("point")?;let mut args129=Vec::new();let mut kw130=Vec::new();args129.push(e.get("frame")?);args129.push({let mut s=Vec::new();s.push(e.get("cap_profiles")?.get(Val::Str("asse".into()))?.get(Val::Str("gagira_fore_x".into()))?);s.push(Val::Float(0.0f64));s.push(e.get("bfp")?.attr("BODY_CENTER_Z")?);Val::tuple(s)});fun131.call(args129,kw130)?}}.get(Val::Int(1i64))?,e.get("s")?)?);Val::tuple(s)};e.set("cap_y",assigned125.clone())?;
let assigned132={let mut s=Vec::new();Val::list(s)};e.set("wrenches",assigned132.clone())?;
for item133 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(e.get("bfp")?.attr("BODY_PROFILE")?);s.push(e.get("bfp")?.attr("HEX_ACROSS_FLATS")?);s.push(Val::Float(0.3f64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("bfp")?.attr("CAP_PROFILE")?);s.push(e.get("bfp")?.attr("CAP_ACROSS_FLATS")?);s.push(Val::Float(0.9f64));Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack134=unpack(item133,3)?;e.set("profile",unpack134[0].clone())?;e.set("across",unpack134[1].clone())?;e.set("clock",unpack134[2].clone())?;let assigned135={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun138=e.get("sorted")?;let mut args136=Vec::new();let mut kw137=Vec::new();args136.push({let e=e.child();let out139=Val::list(vec![]);for item140 in {let mut s=Vec::new();s.push(e.get("profile")?.get(Val::Int(0i64))?.get(Val::Int(0i64))?);s.push(e.get("profile")?.get(unary("neg",Val::Int(1i64))?)?.get(Val::Int(0i64))?);Val::tuple(s)}.iter()? {e.set("x",item140)?;out139.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun143=e.get("layout")?.attr("point")?;let mut args141=Vec::new();let mut kw142=Vec::new();args141.push(e.get("frame")?);args141.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(Val::Float(0.0f64));s.push(e.get("bfp")?.attr("BODY_CENTER_Z")?);Val::tuple(s)});fun143.call(args141,kw142)?}}.get(Val::Int(1i64))?],vec![])?;}out139});fun138.call(args136,kw137)?}};e.set("y",assigned135.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun146=e.get("wrenches")?.attr("append")?;let mut args144=Vec::new();let mut kw145=Vec::new();args144.push({let mut s=Vec::new();s.push(e.get("y")?);s.push(binary("truediv",e.get("across")?,Val::Float(2.0f64))?);s.push(binary("add",e.get("clock")?,e.get("datums")?.get(Val::Str("asse_turn".into()))?)?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun149=e.get("max")?;let mut args147=Vec::new();let mut kw148=Vec::new();args147.push({let e=e.child();let out150=Val::list(vec![]);for item151 in e.get("profile")?.iter()? {let unpack152=unpack(item151,2)?;e.set("_",unpack152[0].clone())?;e.set("r",unpack152[1].clone())?;out150.attr("append")?.call(vec![e.get("r")?],vec![])?;}out150});fun149.call(args147,kw148)?}});Val::tuple(s)});fun146.call(args144,kw145)?}};
}
let assigned153={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun156=e.get("max")?;let mut args154=Vec::new();let mut kw155=Vec::new();args154.extend({let e=e.child();let out157=Val::list(vec![]);for item158 in e.get("seat")?.iter()? {let unpack159=unpack(item158,3)?;e.set("y0",unpack159[0].clone())?;e.set("y1",unpack159[1].clone())?;e.set("r",unpack159[2].clone())?;if {let v162={let v163=e.get("y1")?;let v164=binary("sub",e.get("cap_y")?.get(Val::Int(0i64))?,Val::Float(0.25f64))?;Val::Bool(compare("ge",v163.clone(),v164.clone())?.truthy()?)};if v162.truthy()? {{let v160=e.get("y0")?;let v161=binary("add",e.get("cap_y")?.get(Val::Int(1i64))?,Val::Float(0.25f64))?;Val::Bool(compare("le",v160.clone(),v161.clone())?.truthy()?)}} else {v162}}.truthy()? {out157.attr("append")?.call(vec![e.get("r")?],vec![])?;}}out157}.iter()?);args154.extend({let e=e.child();let out165=Val::list(vec![]);for item166 in e.get("wrenches")?.iter()? {let unpack167=item166.iter()?;anyhow::ensure!(unpack167.len()>=1,"not enough values to unpack");e.set("_",Val::list(unpack167[0..unpack167.len()-1].to_vec()))?;e.set("corner",unpack167[unpack167.len()-1].clone())?;out165.attr("append")?.call(vec![binary("add",e.get("corner")?,e.get("c")?)?],vec![])?;}out165}.iter()?);fun156.call(args154,kw155)?}};e.set("widest",assigned153.clone())?;
let assigned168=binary("add",e.get("axis")?.get(Val::Int(1i64))?,e.get("c")?)?;e.set("split",assigned168.clone())?;
let assigned169={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun172=e.get("snaps")?.attr("station")?;let mut args170=Vec::new();let mut kw171=Vec::new();args170.push(e.get("axis")?.get(Val::Int(0i64))?);args170.push(binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun175=e.get("snaps")?.attr("half_width")?;let mut args173=Vec::new();let mut kw174=Vec::new();args173.push(e.get("widest")?);args173.push(e.get("split")?);args173.push(e.get("axis")?.get(Val::Int(1i64))?);fun175.call(args173,kw174)?}},e.get("snaps")?.attr("WALL")?)?);args170.extend(e.get("cap_y")?.iter()?);kw171.push(("split".into(),e.get("split")?));kw171.push(("wing_root".into(),binary("sub",e.get("axis")?.get(Val::Int(1i64))?,e.get("snaps")?.attr("REAR_ROOT_DROP")?)?));fun172.call(args170,kw171)?}};e.set("st",assigned169.clone())?;
let assigned176={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun179=e.get("snaps")?.attr("asse_cap_profile")?;let mut args177=Vec::new();let mut kw178=Vec::new();args177.push(e.get("wrenches")?);args177.push(e.get("s")?);fun179.call(args177,kw178)?}};e.set("profile",assigned176.clone())?;
let assigned180={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun183=e.get("snaps")?.attr("asse_adapter_capture")?;let mut args181=Vec::new();let mut kw182=Vec::new();args181.push(e.get("frame")?);args181.push(e.get("st")?);args181.push(e.get("axis")?);fun183.call(args181,kw182)?}};let unpack184=unpack(assigned180.clone(),2)?;e.set("adapter_stock",unpack184[0].clone())?;e.set("adapter_cut",unpack184[1].clone())?;
let assigned185={let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("op".into()),Val::Str("section".into()))?;dict_extend(&d,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun188=e.get("snaps")?.attr("asse_cap_room")?;let mut args186=Vec::new();let mut kw187=Vec::new();args186.push(e.get("axis")?);args186.push(e.get("profile")?);args186.push({let mut s=Vec::new();s.push(e.get("cap_y")?.get(Val::Int(0i64))?);s.push(binary("add",e.get("cap_y")?.get(Val::Int(1i64))?,Val::Float(0.5f64))?);Val::tuple(s)});fun188.call(args186,kw187)?}})?;d});s.push(e.get("adapter_cut")?);Val::list(s)};e.set("cuts",assigned185.clone())?;
let assigned189={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun192=e.get("_world_bounds")?;let mut args190=Vec::new();let mut kw191=Vec::new();args190.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun195=e.get("layout")?.attr("pose")?;let mut args193=Vec::new();let mut kw194=Vec::new();args193.push(Val::Str("asse1022-assembly".into()));fun195.call(args193,kw194)?}});args190.extend(e.get("cap_profiles")?.get(Val::Str("asse".into()))?.get(Val::Str("vent_bounds".into()))?.iter()?);fun192.call(args190,kw191)?}};let unpack196=unpack(assigned189.clone(),2)?;e.set("lo",unpack196[0].clone())?;e.set("hi",unpack196[1].clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun199=e.get("cuts")?.attr("append")?;let mut args197=Vec::new();let mut kw198=Vec::new();args197.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun202=e.get("box")?;let mut args200=Vec::new();let mut kw201=Vec::new();args200.push(binary("sub",e.get("lo")?.get(Val::Int(0i64))?,e.get("c")?)?);args200.push(binary("add",e.get("hi")?.get(Val::Int(0i64))?,e.get("c")?)?);args200.push(binary("sub",binary("sub",e.get("lo")?.get(Val::Int(1i64))?,e.get("snaps")?.attr("THREAD")?)?,e.get("c")?)?);args200.push(binary("add",binary("add",e.get("hi")?.get(Val::Int(1i64))?,e.get("snaps")?.attr("THREAD")?)?,e.get("c")?)?);args200.push(binary("sub",e.get("lo")?.get(Val::Int(2i64))?,Val::Float(1.0f64))?);args200.push(e.get("axis")?.get(Val::Int(1i64))?);fun202.call(args200,kw201)?}});fun199.call(args197,kw198)?}};
let assigned203={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun206=e.get("parts")?.attr("_module")?;let mut args204=Vec::new();let mut kw205=Vec::new();args204.push(Val::Str("rear_cap_vent_adapter".into()));args204.push(Val::Str("printed-parts/asse-drain-adapter/asse_drain_adapter.py".into()));fun206.call(args204,kw205)?}};e.set("adapter",assigned203.clone())?;
let assigned207=binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun210=e.get("math")?.attr("sqrt")?;let mut args208=Vec::new();let mut kw209=Vec::new();args208.push(binary("sub",binary("add",binary("pow",e.get("adapter")?.attr("BARB_OD")?,Val::Int(2i64))?,binary("pow",e.get("bfp")?.attr("VENT_D")?,Val::Int(2i64))?)?,binary("pow",e.get("adapter")?.attr("BARB_BORE")?,Val::Int(2i64))?)?);fun210.call(args208,kw209)?}},Val::Float(2.0f64))?;e.set("rb",assigned207.clone())?;
let assigned211=binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun214=e.get("math")?.attr("sqrt")?;let mut args212=Vec::new();let mut kw213=Vec::new();args212.push(binary("sub",binary("add",binary("pow",e.get("adapter")?.attr("TUBE_OD")?,Val::Int(2i64))?,binary("pow",Val::Float(4.0f64),Val::Int(2i64))?)?,binary("pow",e.get("adapter")?.attr("TUBE_BORE")?,Val::Int(2i64))?)?);fun214.call(args212,kw213)?}},Val::Float(2.0f64))?;e.set("rt",assigned211.clone())?;
let assigned215={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun218=e.get("bfp")?.attr("vent")?;let mut args216=Vec::new();let mut kw217=Vec::new();fun218.call(args216,kw217)?}}.get(Val::Int(0i64))?;e.set("tip",assigned215.clone())?;
let assigned219={let mut s=Vec::new();s.push(binary("sub",e.get("tip")?.get(Val::Int(0i64))?,e.get("adapter")?.attr("ELBOW_REACH")?)?);s.push(binary("sub",e.get("tip")?.get(Val::Int(1i64))?,e.get("rb")?)?);s.push(binary("sub",binary("sub",e.get("tip")?.get(Val::Int(2i64))?,e.get("adapter")?.attr("SOCKET_DROP")?)?,e.get("rt")?)?);Val::tuple(s)};e.set("sleeve_lo",assigned219.clone())?;
let assigned220={let mut s=Vec::new();s.push(binary("add",e.get("tip")?.get(Val::Int(0i64))?,e.get("rb")?)?);s.push(binary("add",e.get("tip")?.get(Val::Int(1i64))?,e.get("rb")?)?);s.push(binary("add",e.get("tip")?.get(Val::Int(2i64))?,e.get("adapter")?.attr("INSTALLED_REACH")?)?);Val::tuple(s)};e.set("sleeve_hi",assigned220.clone())?;
let assigned221={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun224=e.get("_world_bounds")?;let mut args222=Vec::new();let mut kw223=Vec::new();args222.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun227=e.get("layout")?.attr("pose")?;let mut args225=Vec::new();let mut kw226=Vec::new();args225.push(Val::Str("asse1022-assembly".into()));fun227.call(args225,kw226)?}});args222.push(e.get("sleeve_lo")?);args222.push(e.get("sleeve_hi")?);fun224.call(args222,kw223)?}};let unpack228=unpack(assigned221.clone(),2)?;e.set("lower",unpack228[0].clone())?;e.set("upper",unpack228[1].clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun231=e.get("cuts")?.attr("append")?;let mut args229=Vec::new();let mut kw230=Vec::new();args229.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun234=e.get("box")?;let mut args232=Vec::new();let mut kw233=Vec::new();args232.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun237=e.get("min")?;let mut args235=Vec::new();let mut kw236=Vec::new();args235.push(e.get("lower")?.get(Val::Int(0i64))?);args235.push(e.get("lo")?.get(Val::Int(0i64))?);fun237.call(args235,kw236)?}},e.get("c")?)?);args232.push(binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun240=e.get("max")?;let mut args238=Vec::new();let mut kw239=Vec::new();args238.push(e.get("upper")?.get(Val::Int(0i64))?);args238.push(e.get("hi")?.get(Val::Int(0i64))?);fun240.call(args238,kw239)?}},e.get("c")?)?);args232.push(binary("sub",binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun243=e.get("min")?;let mut args241=Vec::new();let mut kw242=Vec::new();args241.push(e.get("lower")?.get(Val::Int(1i64))?);args241.push(e.get("lo")?.get(Val::Int(1i64))?);fun243.call(args241,kw242)?}},e.get("snaps")?.attr("THREAD")?)?,e.get("c")?)?);args232.push(binary("add",binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun246=e.get("max")?;let mut args244=Vec::new();let mut kw245=Vec::new();args244.push(e.get("upper")?.get(Val::Int(1i64))?);args244.push(e.get("hi")?.get(Val::Int(1i64))?);fun246.call(args244,kw245)?}},e.get("snaps")?.attr("THREAD")?)?,e.get("c")?)?);args232.push(binary("sub",e.get("lower")?.get(Val::Int(2i64))?,Val::Float(1.0f64))?);args232.push(binary("add",e.get("upper")?.get(Val::Int(2i64))?,e.get("c")?)?);fun234.call(args232,kw233)?}});fun231.call(args229,kw230)?}};
let assigned247={let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("name".into()),Val::Str("asse-snap-cap".into()))?;d.set(Val::Str("section".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun250=e.get("snaps")?.attr("cap_section")?;let mut args248=Vec::new();let mut kw249=Vec::new();args248.push(e.get("st")?);args248.push(e.get("axis")?.get(Val::Int(1i64))?);args248.push(Val::None);args248.push(e.get("axis")?.get(Val::Int(1i64))?);args248.push(Val::Bool(true));fun250.call(args248,kw249)?}})?;d.set(Val::Str("stock".into()),{let mut s=Vec::new();s.push(e.get("adapter_stock")?);Val::list(s)})?;d.set(Val::Str("cuts".into()),e.get("cuts")?)?;d.set(Val::Str("print_rotate_x".into()),Val::Float(90.0f64))?;d});Val::list(s)};e.set("caps",assigned247.clone())?;
let assigned251={let mut s=Vec::new();s.push(e.get("datums")?.get(Val::Str("pisco_axis".into()))?);s.push(e.get("plan")?.get(Val::Str("gas_frame".into()))?);Val::tuple(s)};let unpack252=unpack(assigned251.clone(),2)?;e.set("axis",unpack252[0].clone())?;e.set("frame",unpack252[1].clone())?;
let assigned253={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun256=e.get("runs")?;let mut args254=Vec::new();let mut kw255=Vec::new();args254.push(e.get("profiles")?.get(Val::Str("pisco".into()))?.get(Val::Str("seat_runs".into()))?);args254.push(e.get("frame")?);args254.push(binary("add",e.get("c")?,e.get("snaps")?.attr("PISCO_RADIAL_RELIEF")?)?);fun256.call(args254,kw255)?}};e.set("seat",assigned253.clone())?;
let assigned257={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun260=e.get("json")?.attr("loads")?;let mut args258=Vec::new();let mut kw259=Vec::new();args258.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun263=binary("truediv",e.get("HW")?,Val::Str("reference/compact-inline-candidates/dimensions.json".into()))?.attr("read_text")?;let mut args261=Vec::new();let mut kw262=Vec::new();fun263.call(args261,kw262)?}});fun260.call(args258,kw259)?}}.get(Val::Str("pisco_rvfup_quarter".into()))?;e.set("dims",assigned257.clone())?;
let assigned264={let mut s=Vec::new();s.push(e.get("dims")?.get(Val::Str("fitted_exterior".into()))?.get(Val::Str("component_ranges_mm".into()))?);s.push(e.get("dims")?.get(Val::Str("fitted_exterior".into()))?.get(Val::Str("profile_z_radius_mm".into()))?);Val::tuple(s)};let unpack265=unpack(assigned264.clone(),2)?;e.set("ranges",unpack265[0].clone())?;e.set("profile",unpack265[1].clone())?;
let assigned266={let mut s=Vec::new();s.push(e.get("ranges")?.get(Val::Str("outlet_fitting".into()))?);s.push(e.get("ranges")?.get(Val::Str("outlet_collet".into()))?);Val::tuple(s)};let unpack267=unpack(assigned266.clone(),2)?;e.set("fitting",unpack267[0].clone())?;e.set("collet",unpack267[1].clone())?;
let assigned268={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun271=e.get("next")?;let mut args269=Vec::new();let mut kw270=Vec::new();args269.push({let e=e.child();let out272=Val::list(vec![]);for item273 in e.get("profile")?.iter()? {let unpack274=unpack(item273,2)?;e.set("z",unpack274[0].clone())?;e.set("r",unpack274[1].clone())?;if {let v277={let v278=e.get("z")?;let v279=e.get("fitting")?.get(Val::Int(0i64))?;Val::Bool(compare("gt",v278.clone(),v279.clone())?.truthy()?)};if v277.truthy()? {{let v275=e.get("r")?;let v276=Val::Float(6.5f64);Val::Bool(compare("lt",v275.clone(),v276.clone())?.truthy()?)}} else {v277}}.truthy()? {out272.attr("append")?.call(vec![e.get("z")?],vec![])?;}}out272});fun271.call(args269,kw270)?}};e.set("neck_z",assigned268.clone())?;
let assigned280={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun283=e.get("snaps")?.attr("pisco_cap_span")?;let mut args281=Vec::new();let mut kw282=Vec::new();args281.push(e.get("datums")?.get(Val::Str("mouth_y".into()))?);args281.push(e.get("collet")?.get(Val::Int(0i64))?);args281.push(e.get("datums")?.get(Val::Str("rear".into()))?);fun283.call(args281,kw282)?}};e.set("cap_y",assigned280.clone())?;
let assigned284={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun287=e.get("max")?;let mut args285=Vec::new();let mut kw286=Vec::new();args285.push({let e=e.child();let out288=Val::list(vec![]);for item289 in e.get("seat")?.iter()? {let unpack290=unpack(item289,3)?;e.set("y0",unpack290[0].clone())?;e.set("y1",unpack290[1].clone())?;e.set("r",unpack290[2].clone())?;if {let v293={let v294=e.get("y1")?;let v295=binary("sub",e.get("cap_y")?.get(Val::Int(0i64))?,Val::Float(0.25f64))?;Val::Bool(compare("ge",v294.clone(),v295.clone())?.truthy()?)};if v293.truthy()? {{let v291=e.get("y0")?;let v292=binary("add",e.get("cap_y")?.get(Val::Int(1i64))?,Val::Float(0.25f64))?;Val::Bool(compare("le",v291.clone(),v292.clone())?.truthy()?)}} else {v293}}.truthy()? {out288.attr("append")?.call(vec![e.get("r")?],vec![])?;}}out288});fun287.call(args285,kw286)?}};e.set("widest",assigned284.clone())?;
let assigned296={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun299=e.get("snaps")?.attr("pisco_station")?;let mut args297=Vec::new();let mut kw298=Vec::new();args297.push(e.get("axis")?.get(Val::Int(0i64))?);args297.push(e.get("widest")?);args297.push(e.get("axis")?.get(Val::Int(1i64))?);args297.extend(e.get("cap_y")?.iter()?);fun299.call(args297,kw298)?}};e.set("st",assigned296.clone())?;
let assigned300=binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun303=e.get("max")?;let mut args301=Vec::new();let mut kw302=Vec::new();args301.push({let e=e.child();let out304=Val::list(vec![]);for item305 in e.get("profile")?.iter()? {let unpack306=unpack(item305,2)?;e.set("z",unpack306[0].clone())?;e.set("r",unpack306[1].clone())?;if {let v307=binary("sub",binary("sub",e.get("datums")?.get(Val::Str("mouth_y".into()))?,e.get("cap_y")?.get(Val::Int(1i64))?)?,Val::Float(1.0f64))?;let v308=e.get("z")?;let v309=e.get("neck_z")?;Val::Bool(compare("le",v307.clone(),v308.clone())?.truthy()? && compare("le",v308.clone(),v309.clone())?.truthy()?)}.truthy()? {out304.attr("append")?.call(vec![e.get("r")?],vec![])?;}}out304});fun303.call(args301,kw302)?}},e.get("snaps")?.attr("PISCO_CAP_AIR")?)?;e.set("body_r",assigned300.clone())?;
let assigned310=binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun313=e.get("max")?;let mut args311=Vec::new();let mut kw312=Vec::new();args311.push({let e=e.child();let out314=Val::list(vec![]);for item315 in e.get("profile")?.iter()? {let unpack316=unpack(item315,2)?;e.set("z",unpack316[0].clone())?;e.set("r",unpack316[1].clone())?;if {let v317=e.get("neck_z")?;let v318=e.get("z")?;let v319=e.get("collet")?.get(Val::Int(0i64))?;Val::Bool(compare("le",v317.clone(),v318.clone())?.truthy()? && compare("le",v318.clone(),v319.clone())?.truthy()?)}.truthy()? {out314.attr("append")?.call(vec![e.get("r")?],vec![])?;}}out314});fun313.call(args311,kw312)?}},e.get("snaps")?.attr("PISCO_CAP_AIR")?)?;e.set("neck_r",assigned310.clone())?;
let assigned320=binary("sub",binary("sub",e.get("datums")?.get(Val::Str("mouth_y".into()))?,e.get("neck_z")?)?,e.get("s")?)?;e.set("lip",assigned320.clone())?;
let assigned321={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun324=e.get("snaps")?.attr("pisco_cap_fit")?;let mut args322=Vec::new();let mut kw323=Vec::new();args322.push(e.get("profile")?);args322.push(e.get("datums")?.get(Val::Str("mouth_y".into()))?);args322.push(e.get("cap_y")?);args322.push(e.get("axis")?);args322.push(e.get("neck_z")?);fun324.call(args322,kw323)?}};e.set("fit",assigned321.clone())?;
let assigned325={let e=e.child();let out326=Val::list(vec![]);for item327 in {let mut s=Vec::new();s.push(Val::Str("body".into()));s.push(Val::Str("neck".into()));Val::tuple(s)}.iter()? {e.set("name",item327)?;out326.attr("append")?.call(vec![{let d=Val::dict(vec![]);d.set(Val::Str("op".into()),Val::Str("radial-profile".into()))?;d.set(Val::Str("points".into()),e.get("fit")?.get(e.get("name")?)?)?;d.set(Val::Str("frame".into()),e.get("fit")?.get(Val::Str("frame".into()))?)?;d}],vec![])?;}out326};e.set("cuts",assigned325.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun330=e.get("caps")?.attr("append")?;let mut args328=Vec::new();let mut kw329=Vec::new();args328.push({let d=Val::dict(vec![]);d.set(Val::Str("name".into()),Val::Str("pisco-snap-cap".into()))?;d.set(Val::Str("section".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun333=e.get("snaps")?.attr("cap_section")?;let mut args331=Vec::new();let mut kw332=Vec::new();args331.push(e.get("st")?);args331.push(e.get("st")?.get(Val::Str("root".into()))?);args331.push(binary("sub",binary("sub",e.get("axis")?.get(Val::Int(1i64))?,e.get("body_r")?)?,e.get("snaps")?.attr("WALL")?)?);fun333.call(args331,kw332)?}})?;d.set(Val::Str("stock".into()),{let e=e.child();let out334=Val::list(vec![]);for item335 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun338=e.get("snaps")?.attr("pisco_grip_stock")?;let mut args336=Vec::new();let mut kw337=Vec::new();args336.push(e.get("st")?);args336.push(e.get("axis")?.get(Val::Int(1i64))?);args336.push(e.get("body_r")?);args336.push(e.get("neck_r")?);args336.push(e.get("lip")?);fun338.call(args336,kw337)?}}.iter()? {e.set("b",item335)?;out334.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun341=e.get("box")?;let mut args339=Vec::new();let mut kw340=Vec::new();args339.extend(e.get("b")?.iter()?);fun341.call(args339,kw340)?}}],vec![])?;}out334})?;d.set(Val::Str("cuts".into()),e.get("cuts")?)?;d.set(Val::Str("print_rotate_x".into()),Val::Float(90.0f64))?;d});fun330.call(args328,kw329)?}};
let assigned342={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun345=e.get("rear_plumbing")?.attr("reference")?;let mut args343=Vec::new();let mut kw344=Vec::new();args343.push(Val::Str("cap_digiten".into()));args343.push(Val::Str("reference/digiten-flow-sensor/digiten_flow_sensor.py".into()));fun345.call(args343,kw344)?}};e.set("meter",assigned342.clone())?;
let assigned346={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun349=e.get("layout")?.attr("pose")?;let mut args347=Vec::new();let mut kw348=Vec::new();args347.push(Val::Str("digiten-flow".into()));fun349.call(args347,kw348)?}};e.set("frame",assigned346.clone())?;
// at
e.set("at",{let params=vec![("point".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun352=e.get("layout")?.attr("point")?;let mut args350=Vec::new();let mut kw351=Vec::new();args350.push(e.get("frame")?);args350.push(e.get("point")?);fun352.call(args350,kw351)?}});
Ok(Val::None)})})?;
let assigned353={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun356=e.get("at")?;let mut args354=Vec::new();let mut kw355=Vec::new();args354.push({let mut s=Vec::new();s.push(e.get("meter")?.attr("body_center_x")?);s.push(Val::Float(0.0f64));s.push(e.get("meter")?.attr("body_center_z")?);Val::tuple(s)});fun356.call(args354,kw355)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun359=e.get("at")?;let mut args357=Vec::new();let mut kw358=Vec::new();args357.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)});fun359.call(args357,kw358)?}});Val::tuple(s)};let unpack360=unpack(assigned353.clone(),2)?;e.set("centre",unpack360[0].clone())?;e.set("port",unpack360[1].clone())?;
let assigned361={let mut s=Vec::new();s.push(e.get("centre")?.get(Val::Int(1i64))?);s.push(e.get("centre")?.get(Val::Int(2i64))?);Val::tuple(s)};let unpack362=unpack(assigned361.clone(),2)?;e.set("my",unpack362[0].clone())?;e.set("mz",unpack362[1].clone())?;
let assigned363={let mut s=Vec::new();s.push(e.get("port")?.get(Val::Int(0i64))?);s.push(e.get("port")?.get(Val::Int(2i64))?);Val::tuple(s)};e.set("soda",assigned363.clone())?;
// wx
e.set("wx",{let params=vec![("y".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun366=e.get("at")?;let mut args364=Vec::new();let mut kw365=Vec::new();args364.push({let mut s=Vec::new();s.push(e.get("meter")?.attr("body_center_x")?);s.push(e.get("y")?);s.push(e.get("meter")?.attr("body_center_z")?);Val::tuple(s)});fun366.call(args364,kw365)?}}.get(Val::Int(0i64))?);
Ok(Val::None)})})?;
// wy
e.set("wy",{let params=vec![("x".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun369=e.get("at")?;let mut args367=Vec::new();let mut kw368=Vec::new();args367.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)});fun369.call(args367,kw368)?}}.get(Val::Int(1i64))?);
Ok(Val::None)})})?;
let assigned370=e.get("snaps")?.attr("METER_AIR")?;e.set("air",assigned370.clone())?;
let assigned371=binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun374=e.get("wx")?;let mut args372=Vec::new();let mut kw373=Vec::new();args372.push(Val::Float(7.3f64));fun374.call(args372,kw373)?}},e.get("air")?)?;e.set("mx",assigned371.clone())?;
let assigned375={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun378=e.get("rear_plumbing")?.attr("meter_spans")?;let mut args376=Vec::new();let mut kw377=Vec::new();fun378.call(args376,kw377)?}};let unpack379=unpack(assigned375.clone(),2)?;e.set("seat_y",unpack379[0].clone())?;e.set("cap_y",unpack379[1].clone())?;
let assigned380={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun383=e.get("max")?;let mut args381=Vec::new();let mut kw382=Vec::new();args381.push(e.get("meter")?.attr("port_collar_radii")?);fun383.call(args381,kw382)?}};e.set("collar",assigned380.clone())?;
let assigned384={let mut s=Vec::new();s.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun387=e.get("wx")?;let mut args385=Vec::new();let mut kw386=Vec::new();args385.push(e.get("meter")?.attr("boss_y_range")?.get(Val::Int(0i64))?);fun387.call(args385,kw386)?}},e.get("air")?)?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun390=e.get("wx")?;let mut args388=Vec::new();let mut kw389=Vec::new();args388.push(e.get("meter")?.attr("underside_y")?);fun390.call(args388,kw389)?}});Val::tuple(s)};let unpack391=unpack(assigned384.clone(),2)?;e.set("core",unpack391[0].clone())?;e.set("west",unpack391[1].clone())?;
let assigned392={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun395=e.get("snaps")?.attr("station")?;let mut args393=Vec::new();let mut kw394=Vec::new();args393.push(Val::Float(0.0f64));args393.push(binary("add",binary("sub",binary("add",binary("add",e.get("soda")?.get(Val::Int(1i64))?,e.get("collar")?)?,e.get("air")?)?,e.get("mz")?)?,e.get("snaps")?.attr("WALL")?)?);args393.extend(e.get("cap_y")?.iter()?);kw394.push(("split".into(),Val::Float(0.0f64)));kw394.push(("wing_root".into(),binary("sub",binary("sub",e.get("west")?,e.get("air")?)?,e.get("mx")?)?));fun395.call(args393,kw394)?}};e.set("st",assigned392.clone())?;
let assigned396=e.get("snaps")?.attr("METER_HOUSING_FIT")?;e.set("cap_air",assigned396.clone())?;
let assigned397={let e=e.child();let out398=Val::list(vec![]);for item399 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun402=e.get("snaps")?.attr("clearance_profile")?;let mut args400=Vec::new();let mut kw401=Vec::new();args400.push(e.get("meter")?.attr("housing_profile")?);args400.push(e.get("cap_air")?);args400.push(e.get("cap_air")?);fun402.call(args400,kw401)?}}.iter()? {let unpack403=unpack(item399,2)?;e.set("y",unpack403[0].clone())?;e.set("r",unpack403[1].clone())?;out398.attr("append")?.call(vec![{let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun406=e.get("wx")?;let mut args404=Vec::new();let mut kw405=Vec::new();args404.push(e.get("y")?);fun406.call(args404,kw405)?}});s.push(e.get("r")?);Val::tuple(s)}],vec![])?;}out398};e.set("housing",assigned397.clone())?;
let assigned407={let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("op".into()),Val::Str("radial-profile".into()))?;d.set(Val::Str("points".into()),e.get("housing")?)?;d.set(Val::Str("frame".into()),{let d=Val::dict(vec![]);d.set(Val::Str("rotation".into()),{let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));Val::tuple(s)});Val::tuple(s)})?;d.set(Val::Str("translation_mm".into()),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(e.get("my")?);s.push(e.get("mz")?);Val::tuple(s)})?;d})?;d});s.push({let d=Val::dict(vec![]);d.set(Val::Str("op".into()),Val::Str("cylinder-y".into()))?;d.set(Val::Str("centre".into()),e.get("soda")?)?;d.set(Val::Str("radius".into()),binary("add",e.get("meter")?.attr("port_neck_radius")?,e.get("cap_air")?)?)?;d.set(Val::Str("span".into()),e.get("seat_y")?)?;d});Val::list(s)};e.set("cuts",assigned407.clone())?;
let assigned408=binary("sub",binary("sub",binary("sub",e.get("west")?,e.get("air")?)?,e.get("snaps")?.attr("METER_BACK")?)?,e.get("mx")?)?;e.set("bottom",assigned408.clone())?;
let assigned409=binary("sub",binary("sub",e.get("st")?.get(Val::Str("inner".into()))?,e.get("snaps")?.attr("ROOT_RADIUS")?)?,Val::Float(0.5f64))?;e.set("half",assigned409.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun412=e.get("cuts")?.attr("append")?;let mut args410=Vec::new();let mut kw411=Vec::new();args410.push({let d=Val::dict(vec![]);d.set(Val::Str("op".into()),Val::Str("section".into()))?;dict_extend(&d,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun415=e.get("snaps")?.attr("meter_cap_corner_room")?;let mut args413=Vec::new();let mut kw414=Vec::new();args413.push(binary("add",e.get("mx")?,e.get("bottom")?)?);args413.push(e.get("mz")?);args413.push(e.get("cap_y")?);fun415.call(args413,kw414)?}})?;d});fun412.call(args410,kw411)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun418=e.get("caps")?.attr("append")?;let mut args416=Vec::new();let mut kw417=Vec::new();args416.push({let d=Val::dict(vec![]);d.set(Val::Str("name".into()),Val::Str("meter-snap-cap".into()))?;d.set(Val::Str("section".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun421=e.get("snaps")?.attr("cap_section")?;let mut args419=Vec::new();let mut kw420=Vec::new();args419.push(e.get("st")?);args419.push(e.get("st")?.get(Val::Str("root".into()))?);args419.push(e.get("bottom")?);fun421.call(args419,kw420)?}})?;d.set(Val::Str("stock".into()),{let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun424=e.get("box")?;let mut args422=Vec::new();let mut kw423=Vec::new();args422.push(unary("neg",e.get("half")?)?);args422.push(e.get("half")?);args422.extend(e.get("cap_y")?.iter()?);args422.push(e.get("bottom")?);args422.push(binary("add",e.get("st")?.get(Val::Str("root".into()))?,e.get("snaps")?.attr("METER_BEARING_DEPTH")?)?);fun424.call(args422,kw423)?}});Val::list(s)})?;d.set(Val::Str("placement".into()),{let d=Val::dict(vec![]);d.set(Val::Str("rotate_y".into()),Val::Float(90.0f64))?;d.set(Val::Str("translation".into()),{let mut s=Vec::new();s.push(e.get("mx")?);s.push(Val::Float(0.0f64));s.push(e.get("mz")?);Val::tuple(s)})?;d})?;d.set(Val::Str("cuts".into()),e.get("cuts")?)?;d.set(Val::Str("print_rotate_x".into()),Val::Float(90.0f64))?;d});fun418.call(args416,kw417)?}};
let assigned425={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun428=e.get("rear_plumbing")?.attr("regulator_datums")?;let mut args426=Vec::new();let mut kw427=Vec::new();fun428.call(args426,kw427)?}};e.set("mount",assigned425.clone())?;
let assigned429={let mut s=Vec::new();s.push(e.get("mount")?.get(Val::Str("station".into()))?);s.push(e.get("mount")?.get(Val::Str("axis".into()))?);Val::tuple(s)};let unpack430=unpack(assigned429.clone(),2)?;e.set("st",unpack430[0].clone())?;e.set("axis",unpack430[1].clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun433=e.get("caps")?.attr("append")?;let mut args431=Vec::new();let mut kw432=Vec::new();args431.push({let d=Val::dict(vec![]);d.set(Val::Str("name".into()),Val::Str("regulator-snap-cap".into()))?;d.set(Val::Str("section".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun436=e.get("snaps")?.attr("cap_section")?;let mut args434=Vec::new();let mut kw435=Vec::new();args434.push(e.get("st")?);args434.push(e.get("st")?.get(Val::Str("root".into()))?);args434.push(e.get("mount")?.get(Val::Str("cap_bottom".into()))?);fun436.call(args434,kw435)?}})?;d.set(Val::Str("stock".into()),{let e=e.child();let out437=Val::list(vec![]);for item438 in e.get("mount")?.get(Val::Str("cap_stock".into()))?.iter()? {e.set("b",item438)?;out437.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun441=e.get("box")?;let mut args439=Vec::new();let mut kw440=Vec::new();args439.extend(e.get("b")?.iter()?);fun441.call(args439,kw440)?}}],vec![])?;}out437})?;d.set(Val::Str("cuts".into()),{let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("op".into()),Val::Str("radial-profile".into()))?;d.set(Val::Str("points".into()),e.get("mount")?.get(Val::Str("cap_profile".into()))?)?;d.set(Val::Str("frame".into()),e.get("mount")?.get(Val::Str("profile_frame".into()))?)?;d});Val::list(s)})?;d.set(Val::Str("rotate_z".into()),Val::Float(90.0f64))?;d.set(Val::Str("print_rotate_y".into()),Val::Float(90.0f64))?;d});fun433.call(args431,kw432)?}};
return Ok({let d=Val::dict(vec![]);d.set(Val::Str("caps".into()),e.get("caps")?)?;d.set(Val::Str("color".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",line!());{let fun444=e.get("linear")?;let mut args442=Vec::new();let mut kw443=Vec::new();args442.push(e.get("M_PETGF_BLACK")?);fun444.call(args442,kw443)?}})?;d});
Ok(Val::None)})})?;
    // main
    e.set("main", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            let assigned445 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
                    line!(),
                );
                {
                    let fun448 = e.get("_rust_part")?.attr("cut")?;
                    let mut args446 = Vec::new();
                    let mut kw447 = Vec::new();
                    args446.push(Val::Str("enclosure-components".into()));
                    args446.push(Val::Str("rear-equipment-caps".into()));
                    args446.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
                            line!(),
                        );
                        {
                            let fun451 = e.get("numbers")?;
                            let mut args449 = Vec::new();
                            let mut kw450 = Vec::new();
                            fun451.call(args449, kw450)?
                        }
                    });
                    args446.push(e.get("HERE")?);
                    fun448.call(args446, kw447)?
                }
            };
            e.set("result", assigned445.clone())?;
            for item452 in e.get("result")?.get(Val::Str("files".into()))?.iter()? {
                e.set("file", item452)?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
                        line!(),
                    );
                    {
                        let fun455 = e.get("print")?;
                        let mut args453 = Vec::new();
                        let mut kw454 = Vec::new();
                        args453.push({
                            let mut str456 = String::new();
                            str456.push_str("-> ");
                            str456.push_str(&format(&e.get("file")?, &String::new())?);
                            Val::Str(str456)
                        });
                        kw454.push(("flush".into(), Val::Bool(true)));
                        fun455.call(args453, kw454)?
                    }
                };
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
            line!(),
        );
        {
            let fun459 = e.get("_rust_part")?.attr("start")?;
            let mut args457 = Vec::new();
            let mut kw458 = Vec::new();
            fun459.call(args457, kw458)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/rear_equipment_caps.rs",
            line!(),
        );
        {
            let fun462 = e.get("main")?;
            let mut args460 = Vec::new();
            let mut kw461 = Vec::new();
            fun462.call(args460, kw461)?
        }
    };
    Ok(Val::None)
}
