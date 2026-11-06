//! Normal enclosure construction from scalar recipes and ordered fine-model references.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("contextlib")?;
    e.set("contextmanager", rt.member("contextlib", "contextmanager")?)?;
    e.set("json", rt.import_module("json")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let assigned3 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
            line!(),
        );
        {
            let fun6 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                    line!(),
                );
                {
                    let fun9 = e.get("Path")?;
                    let mut args7 = Vec::new();
                    let mut kw8 = Vec::new();
                    args7.push(e.get("__file__")?);
                    fun9.call(args7, kw8)?
                }
            }
            .attr("resolve")?;
            let mut args4 = Vec::new();
            let mut kw5 = Vec::new();
            fun6.call(args4, kw5)?
        }
    }
    .attr("parent")?;
    e.set("HERE", assigned3.clone())?;
    let assigned10 = e.get("HERE")?.attr("parents")?.get(Val::Int(3i64))?;
    e.set("ROOT", assigned10.clone())?;
    // load
    e.set("load", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod11 = rt.import_module("_enclosure_datums")?;
            e.set("scalar_source", rt.member("_enclosure_datums", "load")?)?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                    line!(),
                );
                {
                    let fun14 = e.get("scalar_source")?;
                    let mut args12 = Vec::new();
                    let mut kw13 = Vec::new();
                    fun14.call(args12, kw13)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // box_from_document
    e.set("box_from_document",{let params=vec![("document".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned15={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun18=e.get("load")?;let mut args16=Vec::new();let mut kw17=Vec::new();fun18.call(args16,kw17)?}};e.set("shell",assigned15.clone())?;
e.set("_box_spec",rt.import_module("_box_spec")?)?;
let assigned19={let e=e.child();let out20=Val::dict(vec![]);for item21 in {let mut s=Vec::new();s.push(e.get("shell")?.attr("Pack")?);s.push(e.get("shell")?.attr("PortField")?);s.push(e.get("shell")?.attr("Nameplate")?);Val::tuple(s)}.iter()? {e.set("kind",item21)?;out20.set(e.get("kind")?.attr("__name__")?,e.get("kind")?)?;}out20};e.set("types",assigned19.clone())?;
let assigned22={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun25=e.get("shell")?.attr("Box")?;let mut args23=Vec::new();let mut kw24=Vec::new();args23.extend({let e=e.child();let out26=Val::list(vec![]);for item27 in e.get("shell")?.attr("Box")?.attr("_fields")?.iter()? {e.set("name",item27)?;out26.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun30=e.get("_box_spec")?.attr("_tupled")?;let mut args28=Vec::new();let mut kw29=Vec::new();args28.push(e.get("document")?.get(Val::Str("box".into()))?.get(e.get("name")?)?);args28.push(e.get("types")?);fun30.call(args28,kw29)?}}],vec![])?;}out26}.iter()?);fun25.call(args23,kw24)?}};e.set("box",assigned22.clone())?;
let assigned31={let e=e.child();let out32=Val::list(vec![]);for item33 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun36=e.get("document")?.attr("get")?;let mut args34=Vec::new();let mut kw35=Vec::new();args34.push(Val::Str("bounds".into()));args34.push({let mut s=Vec::new();Val::tuple(s)});fun36.call(args34,kw35)?}}.iter()? {e.set("row",item33)?;out32.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun39=e.get("shell")?.attr("Bound")?;let mut args37=Vec::new();let mut kw38=Vec::new();args37.extend({let e=e.child();let out40=Val::list(vec![]);for item41 in e.get("shell")?.attr("Bound")?.attr("_fields")?.iter()? {e.set("name",item41)?;out40.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun44=e.get("_box_spec")?.attr("_tupled")?;let mut args42=Vec::new();let mut kw43=Vec::new();args42.push(e.get("row")?.get(e.get("name")?)?);args42.push(e.get("types")?);fun44.call(args42,kw43)?}}],vec![])?;}out40}.iter()?);fun39.call(args37,kw38)?}}],vec![])?;}out32};e.set("bounds",assigned31.clone())?;
return Ok({let mut s=Vec::new();s.push(e.get("shell")?);s.push(e.get("box")?);s.push(e.get("bounds")?);Val::tuple(s)});
Ok(Val::None)})})?;
    // _model_instance
    e.set("_model_instance",{let params=vec![("model".into(),None,false),("name".into(),Some(Val::None),false),("transform".into(),Some(Val::None),true),("indices".into(),Some(Val::None),true),("color".into(),Some(Val::None),true),("split_components".into(),Some(Val::Bool(false)),true)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned45={let d=Val::dict(vec![]);d.set(Val::Str("model".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun48=e.get("str")?;let mut args46=Vec::new();let mut kw47=Vec::new();args46.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun51={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun54=e.get("Path")?;let mut args52=Vec::new();let mut kw53=Vec::new();args52.push(e.get("model")?);fun54.call(args52,kw53)?}}.attr("resolve")?;let mut args49=Vec::new();let mut kw50=Vec::new();fun51.call(args49,kw50)?}});fun48.call(args46,kw47)?}})?;d};e.set("row",assigned45.clone())?;
if {let v55=e.get("name")?;let v56=Val::None;Val::Bool(compare("is_not",v55.clone(),v56.clone())?.truthy()?)}.truthy()? {
let assigned57=e.get("name")?;e.get("row")?.set(Val::Str("name".into()),assigned57.clone())?;
}
if {let v58=e.get("transform")?;let v59=Val::None;Val::Bool(compare("is_not",v58.clone(),v59.clone())?.truthy()?)}.truthy()? {
let assigned60=e.get("transform")?;e.get("row")?.set(Val::Str("transform".into()),assigned60.clone())?;
}
if {let v61=e.get("indices")?;let v62=Val::None;Val::Bool(compare("is_not",v61.clone(),v62.clone())?.truthy()?)}.truthy()? {
let assigned63=e.get("indices")?;e.get("row")?.set(Val::Str("indices".into()),assigned63.clone())?;
}
if {let v64=e.get("color")?;let v65=Val::None;Val::Bool(compare("is_not",v64.clone(),v65.clone())?.truthy()?)}.truthy()? {
let assigned66={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun69=e.get("list")?;let mut args67=Vec::new();let mut kw68=Vec::new();args67.push(e.get("color")?);fun69.call(args67,kw68)?}};e.get("row")?.set(Val::Str("color".into()),assigned66.clone())?;
}
if e.get("split_components")?.truthy()? {
let assigned70=Val::Bool(true);e.get("row")?.set(Val::Str("split_components".into()),assigned70.clone())?;
}
return Ok(e.get("row")?);
Ok(Val::None)})})?;
    // _translation
    e.set("_translation", {
        let params = vec![("point".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned71 = e.get("point")?;
            let unpack72 = unpack(assigned71.clone(), 3)?;
            e.set("x", unpack72[0].clone())?;
            e.set("y", unpack72[1].clone())?;
            e.set("z", unpack72[2].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(e.get("x")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(e.get("y")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // installed_instances
    e.set("installed_instances",{let params=vec![("box_document".into(),None,false),("directory".into(),Some(Val::None),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned158={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun161=e.get("box_from_document")?;let mut args159=Vec::new();let mut kw160=Vec::new();args159.push(e.get("box_document")?);fun161.call(args159,kw160)?}};let unpack162=unpack(assigned158.clone(),3)?;e.set("shell",unpack162[0].clone())?;e.set("box",unpack162[1].clone())?;e.set("_bounds",unpack162[2].clone())?;
e.set("_rust_part",rt.import_module("_rust_part")?)?;
let mod163=rt.import_module("_materials")?;e.set("linear",rt.member("_materials","linear")?)?;e.set("M_PETGF_BLACK",rt.member("_materials","M_PETGF_BLACK")?)?;
let assigned164=if {let v165=e.get("directory")?;let v166=Val::None;Val::Bool(compare("is_not",v165.clone(),v166.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun169=e.get("Path")?;let mut args167=Vec::new();let mut kw168=Vec::new();args167.push(e.get("directory")?);fun169.call(args167,kw168)?}}} else {binary("truediv",e.get("HERE")?,Val::Str("installed".into()))?};e.set("directory",assigned164.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun172=e.get("directory")?.attr("mkdir")?;let mut args170=Vec::new();let mut kw171=Vec::new();kw171.push(("parents".into(),Val::Bool(true)));kw171.push(("exist_ok".into(),Val::Bool(true)));fun172.call(args170,kw171)?}};
let assigned173={let mut s=Vec::new();Val::list(s)};e.set("instances",assigned173.clone())?;
if {let v174=e.get("box")?.attr("pump_bay")?;if v174.truthy()? {e.get("box")?.attr("pack")?.attr("collet_plate")?} else {v174}}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun177=e.get("instances")?.attr("append")?;let mut args175=Vec::new();let mut kw176=Vec::new();args175.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun180=e.get("_model_instance")?;let mut args178=Vec::new();let mut kw179=Vec::new();args178.push(binary("truediv",e.get("HERE")?,Val::Str("enclosure-pump-retainer-seated.step.npz".into()))?);args178.push(Val::Str("enclosure-pump-retainer".into()));fun180.call(args178,kw179)?}});fun177.call(args175,kw176)?}};
}
let assigned181=e.get("shell")?.attr("_funnel_frame_part")?;e.set("frame",assigned181.clone())?;
let assigned182={let mut s=Vec::new();s.push(binary("truediv",binary("add",e.get("box")?.attr("inner")?.get(Val::Int(0i64))?,e.get("box")?.attr("inner")?.get(Val::Int(1i64))?)?,Val::Float(2.0f64))?);s.push(e.get("frame")?.attr("center_y")?);Val::tuple(s)};e.set("centre",assigned182.clone())?;
let assigned183={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun186=e.get("shell")?.attr("funnel_seat_z")?;let mut args184=Vec::new();let mut kw185=Vec::new();args184.push(e.get("box")?.attr("outer")?);fun186.call(args184,kw185)?}};e.set("seat",assigned183.clone())?;
let assigned187={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun190=e.get("frame")?.attr("datums")?;let mut args188=Vec::new();let mut kw189=Vec::new();args188.push(e.get("seat")?);fun190.call(args188,kw189)?}}.get(Val::Int(0i64))?;e.set("floor",assigned187.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun193=e.get("_rust_part")?.attr("cut")?;let mut args191=Vec::new();let mut kw192=Vec::new();args191.push(Val::Str("funnel".into()));args191.push(Val::Str("funnel-frame".into()));args191.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun196=e.get("frame")?.attr("numbers")?;let mut args194=Vec::new();let mut kw195=Vec::new();args194.push(e.get("box")?.attr("inner")?);args194.push(e.get("box")?.attr("y_joint")?);args194.push(e.get("centre")?);args194.push(e.get("seat")?);fun196.call(args194,kw195)?}});args191.push(e.get("directory")?);kw192.push(("numbers_name".into(),Val::Str("enclosure-funnel-frame".into())));fun193.call(args191,kw192)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun199=e.get("instances")?.attr("append")?;let mut args197=Vec::new();let mut kw198=Vec::new();args197.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun202=e.get("_model_instance")?;let mut args200=Vec::new();let mut kw201=Vec::new();args200.push(binary("truediv",e.get("directory")?,Val::Str("funnel-frame.step.npz".into()))?);args200.push(Val::Str("funnel-frame".into()));kw201.push(("transform".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun205=e.get("_translation")?;let mut args203=Vec::new();let mut kw204=Vec::new();args203.push({let mut s=Vec::new();s.extend(e.get("centre")?.iter()?);s.push(e.get("floor")?);Val::tuple(s)});fun205.call(args203,kw204)?}}));kw201.push(("color".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun208=e.get("linear")?;let mut args206=Vec::new();let mut kw207=Vec::new();args206.push(e.get("M_PETGF_BLACK")?);fun208.call(args206,kw207)?}}));fun202.call(args200,kw201)?}});fun199.call(args197,kw198)?}};
let assigned209={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun212=e.get("shell")?.attr("_above_core_shell")?.attr("rear_identification")?;let mut args210=Vec::new();let mut kw211=Vec::new();fun212.call(args210,kw211)?}};e.set("identification",assigned209.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun215=e.get("_rust_part")?.attr("cut")?;let mut args213=Vec::new();let mut kw214=Vec::new();args213.push(Val::Str("enclosure-components".into()));args213.push(Val::Str("rear-identification".into()));args213.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun218=e.get("identification")?.attr("numbers")?;let mut args216=Vec::new();let mut kw217=Vec::new();fun218.call(args216,kw217)?}});args213.push(e.get("directory")?);fun215.call(args213,kw214)?}};
for item219 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun222=e.get("identification")?.attr("stations")?;let mut args220=Vec::new();let mut kw221=Vec::new();fun222.call(args220,kw221)?}}.iter()? {
e.set("station",item219)?;let assigned223=e.get("station")?.get(Val::Str("which".into()))?;e.set("which",assigned223.clone())?;
let assigned224=binary("truediv",e.get("directory")?,{let mut str225=String::new();str225.push_str("rear-label-");str225.push_str(&format(&e.get("which")?,&String::new())?);str225.push_str(".step.npz");Val::Str(str225)})?;e.set("model",assigned224.clone())?;
let assigned226={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun229=e.get("_translation")?;let mut args227=Vec::new();let mut kw228=Vec::new();args227.push({let mut s=Vec::new();s.push(e.get("station")?.get(Val::Str("center_x_mm".into()))?);s.push(e.get("station")?.get(Val::Str("floor_y_mm".into()))?);s.push(e.get("station")?.get(Val::Str("center_z_mm".into()))?);Val::tuple(s)});fun229.call(args227,kw228)?}};e.set("transform",assigned226.clone())?;
for item230 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun233=e.get("enumerate")?;let mut args231=Vec::new();let mut kw232=Vec::new();args231.push({let mut s=Vec::new();s.push(Val::Str("".into()));s.push(Val::Str("-word".into()));Val::tuple(s)});fun233.call(args231,kw232)?}}.iter()? {
let unpack234=unpack(item230,2)?;e.set("index",unpack234[0].clone())?;e.set("suffix",unpack234[1].clone())?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun237=e.get("instances")?.attr("append")?;let mut args235=Vec::new();let mut kw236=Vec::new();args235.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun240=e.get("_model_instance")?;let mut args238=Vec::new();let mut kw239=Vec::new();args238.push(e.get("model")?);args238.push({let mut str241=String::new();str241.push_str("bulkhead-ring-");str241.push_str(&format(&e.get("which")?,&String::new())?);str241.push_str(&format(&e.get("suffix")?,&String::new())?);Val::Str(str241)});kw239.push(("indices".into(),{let mut s=Vec::new();s.push(e.get("index")?);Val::list(s)}));kw239.push(("transform".into(),e.get("transform")?));kw239.push(("split_components".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun244=e.get("bool")?;let mut args242=Vec::new();let mut kw243=Vec::new();args242.push(e.get("index")?);fun244.call(args242,kw243)?}}));fun240.call(args238,kw239)?}});fun237.call(args235,kw236)?}};
}
}
let assigned245=e.get("identification")?.attr("nameplate")?;e.set("plate",assigned245.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun248=e.get("_rust_part")?.attr("cut")?;let mut args246=Vec::new();let mut kw247=Vec::new();args246.push(Val::Str("enclosure-components".into()));args246.push(Val::Str("nameplate".into()));args246.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun251=e.get("plate")?.attr("numbers")?;let mut args249=Vec::new();let mut kw250=Vec::new();args249.push(Val::Int(1i64));fun251.call(args249,kw250)?}});args246.push(e.get("directory")?);kw247.push(("numbers_name".into(),Val::Str("enclosure-nameplate".into())));fun248.call(args246,kw247)?}};
let assigned252={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun255=e.get("identification")?.attr("nameplate_plan")?;let mut args253=Vec::new();let mut kw254=Vec::new();fun255.call(args253,kw254)?}};e.set("plan",assigned252.clone())?;
let assigned256={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun259=e.get("_translation")?;let mut args257=Vec::new();let mut kw258=Vec::new();args257.push({let mut s=Vec::new();s.push(e.get("plan")?.get(Val::Str("center_x_mm".into()))?);s.push(binary("sub",e.get("plan")?.get(Val::Str("face_y_mm".into()))?,e.get("plate")?.attr("THICK")?)?);s.push(e.get("plan")?.get(Val::Str("center_z_mm".into()))?);Val::tuple(s)});fun259.call(args257,kw258)?}};e.set("transform",assigned256.clone())?;
for item260 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun263=e.get("enumerate")?;let mut args261=Vec::new();let mut kw262=Vec::new();args261.push({let mut s=Vec::new();s.push(Val::Str("nameplate".into()));s.push(Val::Str("nameplate-ink".into()));Val::tuple(s)});fun263.call(args261,kw262)?}}.iter()? {
let unpack264=unpack(item260,2)?;e.set("index",unpack264[0].clone())?;e.set("name",unpack264[1].clone())?;let assigned265=if e.get("index")?.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun268=e.get("identification")?.attr("colours")?.attr("word_color")?;let mut args266=Vec::new();let mut kw267=Vec::new();args266.push(Val::Str("flavor".into()));fun268.call(args266,kw267)?}}} else {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun271=e.get("identification")?.attr("colours")?.attr("chip_color")?;let mut args269=Vec::new();let mut kw270=Vec::new();args269.push(Val::Str("flavor".into()));fun271.call(args269,kw270)?}}};e.set("colour",assigned265.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun274=e.get("instances")?.attr("append")?;let mut args272=Vec::new();let mut kw273=Vec::new();args272.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun277=e.get("_model_instance")?;let mut args275=Vec::new();let mut kw276=Vec::new();args275.push(binary("truediv",e.get("directory")?,Val::Str("nameplate-001.step.npz".into()))?);args275.push(e.get("name")?);kw276.push(("indices".into(),{let mut s=Vec::new();s.push(e.get("index")?);Val::list(s)}));kw276.push(("transform".into(),e.get("transform")?));kw276.push(("color".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun280=e.get("linear")?;let mut args278=Vec::new();let mut kw279=Vec::new();args278.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun283=e.get("identification")?.attr("_colour")?;let mut args281=Vec::new();let mut kw282=Vec::new();args281.push(e.get("colour")?);fun283.call(args281,kw282)?}});fun280.call(args278,kw279)?}}));kw276.push(("split_components".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun286=e.get("bool")?;let mut args284=Vec::new();let mut kw285=Vec::new();args284.push(e.get("index")?);fun286.call(args284,kw285)?}}));fun277.call(args275,kw276)?}});fun274.call(args272,kw273)?}};
}
crate::nameplate_snap::append_hardware(&e)?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun289=e.get("dict")?;let mut args287=Vec::new();let mut kw288=Vec::new();kw288.push(("instances".into(),e.get("instances")?));kw288.push(("datums".into(),{let d=Val::dict(vec![]);d.set(Val::Str("funnel_frame_fasteners".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun292=e.get("frame")?.attr("fastener_datums")?;let mut args290=Vec::new();let mut kw291=Vec::new();args290.push(e.get("box")?.attr("inner")?);args290.push(e.get("box")?.attr("y_joint")?);args290.push(e.get("centre")?);args290.push(e.get("seat")?);fun292.call(args290,kw291)?}})?;d.set(Val::Str("funnel_centre".into()),e.get("centre")?)?;d.set(Val::Str("funnel_seat".into()),e.get("seat")?)?;d.set(Val::Str("funnel_frame_floor".into()),e.get("floor")?)?;d.set(Val::Str("y_stack_rods".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun295=e.get("shell")?.attr("y_stack_rods")?;let mut args293=Vec::new();let mut kw294=Vec::new();args293.push(e.get("box")?.attr("inner")?);fun295.call(args293,kw294)?}})?;d}));fun289.call(args287,kw288)?}});
Ok(Val::None)})})?;
    // box_from_plan
    e.set("box_from_plan",{let params=vec![("plan".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned296={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun299=e.get("load")?;let mut args297=Vec::new();let mut kw298=Vec::new();fun299.call(args297,kw298)?}};e.set("shell",assigned296.clone())?;
e.set("_box_spec",rt.import_module("_box_spec")?)?;
let mod300=rt.import_module("_rust_enclosure_checks")?;e.set("box_readings",rt.member("_rust_enclosure_checks","box_readings")?)?;
let assigned301=e.get("plan")?.get(Val::Str("metadata".into()))?;e.set("metadata",assigned301.clone())?;
let assigned302=e.get("metadata")?.get(Val::Str("pack".into()))?;e.set("raw",assigned302.clone())?;
let assigned303={let e=e.child();let out304=Val::dict(vec![]);for item305 in {let mut s=Vec::new();s.push(e.get("shell")?.attr("Pack")?);s.push(e.get("shell")?.attr("PortField")?);s.push(e.get("shell")?.attr("Nameplate")?);Val::tuple(s)}.iter()? {e.set("kind",item305)?;out304.set(e.get("kind")?.attr("__name__")?,e.get("kind")?)?;}out304};e.set("types",assigned303.clone())?;
if {let v306=Val::Str("__hsm_namedtuple__".into());let v307=e.get("raw")?;Val::Bool(compare("in",v306.clone(),v307.clone())?.truthy()?)}.truthy()? {
let assigned308={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun311=e.get("_box_spec")?.attr("_tupled")?;let mut args309=Vec::new();let mut kw310=Vec::new();args309.push(e.get("raw")?);args309.push(e.get("types")?);fun311.call(args309,kw310)?}};e.set("pack",assigned308.clone())?;
let assigned312=e.get("pack")?.attr("placed")?;e.set("placed",assigned312.clone())?;
}else{
// stations
e.set("stations",{let params=vec![("value".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun315=e.get("isinstance")?;let mut args313=Vec::new();let mut kw314=Vec::new();args313.push(e.get("value")?);args313.push(e.get("list")?);fun315.call(args313,kw314)?}}.truthy()? {
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun318=e.get("tuple")?;let mut args316=Vec::new();let mut kw317=Vec::new();args316.push({let e=e.child();let out319=Val::list(vec![]);for item320 in e.get("value")?.iter()? {e.set("item",item320)?;out319.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun323=e.get("stations")?;let mut args321=Vec::new();let mut kw322=Vec::new();args321.push(e.get("item")?);fun323.call(args321,kw322)?}}],vec![])?;}out319});fun318.call(args316,kw317)?}});
}
if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun326=e.get("isinstance")?;let mut args324=Vec::new();let mut kw325=Vec::new();args324.push(e.get("value")?);args324.push(e.get("dict")?);fun326.call(args324,kw325)?}}.truthy()? {
if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun329=e.get("any")?;let mut args327=Vec::new();let mut kw328=Vec::new();args327.push({let e=e.child();let out330=Val::list(vec![]);for item331 in e.get("value")?.iter()? {e.set("name",item331)?;out330.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun334=e.get("name")?.attr("startswith")?;let mut args332=Vec::new();let mut kw333=Vec::new();args332.push(Val::Str("__hsm_".into()));fun334.call(args332,kw333)?}}],vec![])?;}out330});fun329.call(args327,kw328)?}}.truthy()? {
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun337=e.get("_box_spec")?.attr("_tupled")?;let mut args335=Vec::new();let mut kw336=Vec::new();args335.push(e.get("value")?);args335.push(e.get("types")?);fun337.call(args335,kw336)?}});
}
return Ok({let e=e.child();let out338=Val::dict(vec![]);for item339 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun342=e.get("value")?.attr("items")?;let mut args340=Vec::new();let mut kw341=Vec::new();fun342.call(args340,kw341)?}}.iter()? {let unpack343=unpack(item339,2)?;e.set("name",unpack343[0].clone())?;e.set("item",unpack343[1].clone())?;out338.set(e.get("name")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun346=e.get("stations")?;let mut args344=Vec::new();let mut kw345=Vec::new();args344.push(e.get("item")?);fun346.call(args344,kw345)?}})?;}out338});
}
return Ok(e.get("value")?);
Ok(Val::None)})})?;
let assigned347={let e=e.child();let out348=Val::dict(vec![]);for item349 in e.get("shell")?.attr("Pack")?.attr("_fields")?.iter()? {e.set("name",item349)?;if {let v350=e.get("name")?;let v351=e.get("raw")?;Val::Bool(compare("in",v350.clone(),v351.clone())?.truthy()?)}.truthy()? {out348.set(e.get("name")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun354=e.get("stations")?;let mut args352=Vec::new();let mut kw353=Vec::new();args352.push(e.get("raw")?.get(e.get("name")?)?);fun354.call(args352,kw353)?}})?;}}out348};e.set("values",assigned347.clone())?;
for item355 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("port_field".into()));s.push(e.get("shell")?.attr("PortField")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("nameplate".into()));s.push(e.get("shell")?.attr("Nameplate")?);Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack356=unpack(item355,2)?;e.set("name",unpack356[0].clone())?;e.set("record",unpack356[1].clone())?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun359=e.get("isinstance")?;let mut args357=Vec::new();let mut kw358=Vec::new();args357.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun362=e.get("values")?.attr("get")?;let mut args360=Vec::new();let mut kw361=Vec::new();args360.push(e.get("name")?);fun362.call(args360,kw361)?}});args357.push(e.get("dict")?);fun359.call(args357,kw358)?}}.truthy()? {
let assigned363={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun366=e.get("record")?;let mut args364=Vec::new();let mut kw365=Vec::new();kw365.extend(keyword_items(e.get("values")?.get(e.get("name")?)?)?);fun366.call(args364,kw365)?}};e.get("values")?.set(e.get("name")?,assigned363.clone())?;
}
}
let assigned367={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun370=e.get("values")?.attr("pop")?;let mut args368=Vec::new();let mut kw369=Vec::new();args368.push(Val::Str("placed".into()));fun370.call(args368,kw369)?}};e.set("placed",assigned367.clone())?;
let assigned371={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun374=e.get("shell")?.attr("Pack")?;let mut args372=Vec::new();let mut kw373=Vec::new();kw373.push(("placed".into(),{let d=Val::dict(vec![]);d}));kw373.extend(keyword_items(e.get("values")?)?);fun374.call(args372,kw373)?}};e.set("pack",assigned371.clone())?;
}
let assigned375={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun378=e.get("metadata")?.attr("get")?;let mut args376=Vec::new();let mut kw377=Vec::new();args376.push(Val::Str("raw_bounds".into()));args376.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun381=e.get("metadata")?.attr("get")?;let mut args379=Vec::new();let mut kw380=Vec::new();args379.push(Val::Str("bounds".into()));fun381.call(args379,kw380)?}});fun378.call(args376,kw377)?}};e.set("raw_bounds",assigned375.clone())?;
let assigned382={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun385=e.get("metadata")?.attr("get")?;let mut args383=Vec::new();let mut kw384=Vec::new();args383.push(Val::Str("pack_order".into()));args383.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun388=e.get("tuple")?;let mut args386=Vec::new();let mut kw387=Vec::new();args386.push(e.get("placed")?);fun388.call(args386,kw387)?}});fun385.call(args383,kw384)?}};e.set("order",assigned382.clone())?;
let assigned389={let e=e.child();let out390=Val::dict(vec![]);for item391 in e.get("order")?.iter()? {e.set("name",item391)?;if {let v392=e.get("name")?;let v393=e.get("placed")?;Val::Bool(compare("in",v392.clone(),v393.clone())?.truthy()?)}.truthy()? {out390.set(e.get("name")?,e.get("raw_bounds")?.get(e.get("name")?)?)?;}}out390};e.set("bounds",assigned389.clone())?;
let assigned394={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun397=e.get("metadata")?.attr("get")?;let mut args395=Vec::new();let mut kw396=Vec::new();args395.push(Val::Str("pack_references".into()));args395.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun400=e.get("metadata")?.attr("get")?;let mut args398=Vec::new();let mut kw399=Vec::new();args398.push(Val::Str("references".into()));fun400.call(args398,kw399)?}});fun397.call(args395,kw396)?}};e.set("references",assigned394.clone())?;
if {let v401=e.get("references")?;let v402=Val::None;Val::Bool(compare("is",v401.clone(),v402.clone())?.truthy()?)}.truthy()? {
let assigned403={let e=e.child();let out404=Val::dict(vec![]);for item405 in e.get("plan")?.get(Val::Str("instances".into()))?.iter()? {e.set("row",item405)?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun408=e.get("row")?.attr("get")?;let mut args406=Vec::new();let mut kw407=Vec::new();args406.push(Val::Str("name".into()));fun408.call(args406,kw407)?}}.truthy()? {out404.set(e.get("row")?.get(Val::Str("name".into()))?,e.get("row")?)?;}}out404};e.set("references",assigned403.clone())?;
}
let assigned409={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun412=e.get("pack")?.attr("_replace")?;let mut args410=Vec::new();let mut kw411=Vec::new();kw411.push(("placed".into(),{let e=e.child();let out413=Val::dict(vec![]);for item414 in e.get("bounds")?.iter()? {e.set("name",item414)?;out413.set(e.get("name")?,{let mut s=Vec::new();s.push(Val::None);s.push(Val::None);Val::tuple(s)})?;}out413}));fun412.call(args410,kw411)?}};e.set("pack",assigned409.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun417=e.get("shell")?.attr("BOUNDS")?.attr("clear")?;let mut args415=Vec::new();let mut kw416=Vec::new();fun417.call(args415,kw416)?}};
let assigned418={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun421=e.get("box_readings")?;let mut args419=Vec::new();let mut kw420=Vec::new();args419.push(e.get("shell")?);args419.push(e.get("pack")?);args419.push(e.get("bounds")?);args419.push(e.get("references")?);fun421.call(args419,kw420)?}};e.set("readings",assigned418.clone())?;
let assigned422={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun425=e.get("shell")?.attr("stated_box")?;let mut args423=Vec::new();let mut kw424=Vec::new();args423.push(e.get("pack")?);kw424.push(("readings".into(),e.get("readings")?));fun425.call(args423,kw424)?}};e.set("box",assigned422.clone())?;
let assigned426={let mut s=Vec::new();s.push(binary("truediv",binary("add",e.get("box")?.attr("inner")?.get(Val::Int(0i64))?,e.get("box")?.attr("inner")?.get(Val::Int(1i64))?)?,Val::Float(2.0f64))?);s.push(e.get("shell")?.attr("_funnel_frame_part")?.attr("center_y")?);Val::tuple(s)};e.set("centre",assigned426.clone())?;
let assigned427={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun430=e.get("shell")?.attr("with_funnel")?;let mut args428=Vec::new();let mut kw429=Vec::new();args428.push(e.get("box")?);args428.push(e.get("centre")?);fun430.call(args428,kw429)?}};e.set("box",assigned427.clone())?;
return Ok({let mut s=Vec::new();s.push(e.get("shell")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun433=e.get("shell")?.attr("documented")?;let mut args431=Vec::new();let mut kw432=Vec::new();args431.push(e.get("box")?);fun433.call(args431,kw432)?}});Val::tuple(s)});
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
