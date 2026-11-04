//! Guide recipe: `tools/install-guide/opening_scene.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("os", rt.import_module("os")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod2 = rt.import_module("PIL")?;
    e.set("Image", rt.member("PIL", "Image")?)?;
    let assigned3 = {
        let fun6 = {
            let fun9 = e.get("Path")?;
            let mut args7 = Vec::new();
            let mut kw8 = Vec::new();
            args7.push(e.get("__file__")?);
            fun9.call(args7, kw8)?
        }
        .attr("resolve")?;
        let mut args4 = Vec::new();
        let mut kw5 = Vec::new();
        fun6.call(args4, kw5)?
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned3.clone())?;
    let assigned10 = binary("truediv", e.get("ROOT")?, Val::Str("hardware".into()))?;
    e.set("HARDWARE", assigned10.clone())?;
    let assigned11 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide/out/opening".into()),
    )?;
    e.set("OUT", assigned11.clone())?;
    let assigned12 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide/assets".into()),
    )?;
    e.set("ASSETS", assigned12.clone())?;
    let assigned13 = {
        let mut s = Vec::new();
        s.push({
            let fun16 = e.get("str")?;
            let mut args14 = Vec::new();
            let mut kw15 = Vec::new();
            args14.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("install-guide".into()),
            )?);
            fun16.call(args14, kw15)?
        });
        s.push({
            let fun19 = e.get("str")?;
            let mut args17 = Vec::new();
            let mut kw18 = Vec::new();
            args17.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("scripts".into()),
            )?);
            fun19.call(args17, kw18)?
        });
        s.push({
            let fun22 = e.get("str")?;
            let mut args20 = Vec::new();
            let mut kw21 = Vec::new();
            args20.push(binary("truediv", e.get("ROOT")?, Val::Str("tools".into()))?);
            fun22.call(args20, kw21)?
        });
        Val::list(s)
    };
    e.get("sys")?.attr("path")?.set(
        Val::Slice {
            start: None,
            stop: Some(Val::Int(0i64).integer()?),
            step: 1,
        },
        assigned13.clone(),
    )?;
    // outlines
    e.set("outlines", {
        let params = vec![("mask".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod23 = rt.import_module("_guide_native")?;
            e.set("contour", rt.member("_guide_native", "outlines")?)?;
            return Ok({
                let fun26 = e.get("contour")?;
                let mut args24 = Vec::new();
                let mut kw25 = Vec::new();
                args24.push(e.get("mask")?);
                fun26.call(args24, kw25)?
            });
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("_rust_part",rt.import_module("_rust_part")?)?;
{let fun29=e.get("_rust_part")?.attr("start")?;let mut args27=Vec::new();let mut kw28=Vec::new();fun29.call(args27,kw28)?};
e.set("docgen",rt.import_module("docgen")?)?;
e.set("_hsm_render",rt.import_module("_hsm_render")?)?;
e.set("_install_art",rt.import_module("_install_art")?)?;
e.set("_mesh_payload",rt.import_module("_mesh_payload")?)?;
let mod30=rt.import_module("_install_art_mesh")?;e.set("payloads",rt.member("_install_art_mesh","payloads")?)?;e.set("_read",rt.member("_install_art_mesh","_read")?)?;
{let fun33=e.get("OUT")?.attr("mkdir")?;let mut args31=Vec::new();let mut kw32=Vec::new();kw32.push(("parents".into(),Val::Bool(true)));kw32.push(("exist_ok".into(),Val::Bool(true)));fun33.call(args31,kw32)?};
{let fun36=e.get("ASSETS")?.attr("mkdir")?;let mut args34=Vec::new();let mut kw35=Vec::new();kw35.push(("parents".into(),Val::Bool(true)));kw35.push(("exist_ok".into(),Val::Bool(true)));fun36.call(args34,kw35)?};
let assigned37={let fun40=e.get("payloads")?;let mut args38=Vec::new();let mut kw39=Vec::new();args38.push(e.get("_install_art")?);args38.push({let mut s=Vec::new();s.push(Val::Str("opening".into()));Val::list(s)});args38.push(e.get("OUT")?);fun40.call(args38,kw39)?};e.set("staged",assigned37.clone())?;
let assigned41={let fun44=e.get("_read")?;let mut args42=Vec::new();let mut kw43=Vec::new();args42.push(e.get("staged")?.get(Val::Str("opening".into()))?);fun44.call(args42,kw43)?};e.set("scene",assigned41.clone())?;
let assigned45={let e=e.child();let out46=Val::list(vec![]);for item47 in e.get("scene")?.iter()? {e.set("mesh",item47)?;if {let v51={let fun50=e.get("mesh")?.get(Val::Str("name".into()))?.attr("split")?;let mut args48=Vec::new();let mut kw49=Vec::new();args48.push(Val::Str("/".into()));fun50.call(args48,kw49)?}.get(Val::Int(0i64))?;let v52=Val::Str("countertop".into());Val::Bool(compare("ne",v51.clone(),v52.clone())?.truthy()?)}.truthy()? {out46.attr("append")?.call(vec![e.get("mesh")?],vec![])?;}}out46};e.set("component",assigned45.clone())?;
let assigned53={let d=Val::dict(vec![]);d.set(Val::Str("scene".into()),binary("truediv",e.get("OUT")?,Val::Str("opening.step".into()))?)?;d.set(Val::Str("components".into()),binary("truediv",e.get("OUT")?,Val::Str("components.step".into()))?)?;d};e.set("paths",assigned53.clone())?;
let assigned54={let mut s=Vec::new();Val::list(s)};e.set("scenes",assigned54.clone())?;
for item55 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("scene".into()));s.push(e.get("scene")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("components".into()));s.push(e.get("component")?);Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack67=unpack(item55,2)?;e.set("name",unpack67[0].clone())?;e.set("meshes",unpack67[1].clone())?;let assigned56=binary("truediv",e.get("OUT")?,{let mut str57=String::new();str57.push_str("opening-");str57.push_str(&format(&e.get("name")?,&String::new())?);str57.push_str(".mesh");Val::Str(str57)})?;e.set("source",assigned56.clone())?;
{let fun60=e.get("_mesh_payload")?.attr("write")?;let mut args58=Vec::new();let mut kw59=Vec::new();args58.push(e.get("meshes")?);args58.push(e.get("source")?);fun60.call(args58,kw59)?};
{let fun63=e.get("scenes")?.attr("append")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push({let d=Val::dict(vec![]);d.set(Val::Str("name".into()),e.get("paths")?.get(e.get("name")?)?.attr("stem")?)?;d.set(Val::Str("payload".into()),{let fun66=e.get("str")?;let mut args64=Vec::new();let mut kw65=Vec::new();args64.push(e.get("source")?);fun66.call(args64,kw65)?})?;d});fun63.call(args61,kw62)?};
}
let assigned68=binary("truediv",e.get("OUT")?,Val::Str("opening-export.numbers.json".into()))?;e.set("numbers",assigned68.clone())?;
{let fun71=e.get("numbers")?.attr("write_text")?;let mut args69=Vec::new();let mut kw70=Vec::new();args69.push(binary("add",{let fun74=e.get("json")?.attr("dumps")?;let mut args72=Vec::new();let mut kw73=Vec::new();args72.push({let d=Val::dict(vec![]);d.set(Val::Str("surface_scenes".into()),e.get("scenes")?)?;d});kw73.push(("sort_keys".into(),Val::Bool(true)));fun74.call(args72,kw73)?},Val::Str("\n".into()))?);fun71.call(args69,kw70)?};
{let fun77=e.get("_rust_part")?.attr("run")?;let mut args75=Vec::new();let mut kw76=Vec::new();args75.push(Val::Str("tooling".into()));args75.push(Val::Str("install-art-props".into()));args75.push(e.get("numbers")?);args75.push(e.get("OUT")?);fun77.call(args75,kw76)?};
let assigned78={let fun81=e.get("dict")?;let mut args79=Vec::new();let mut kw80=Vec::new();kw80.push(("cam".into(),{let mut s=Vec::new();s.push(Val::Float(0.42f64));s.push(unary("neg",Val::Float(0.8f64))?);s.push(Val::Float(0.95f64));Val::tuple(s)}));kw80.push(("target".into(),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(24.0f64));Val::tuple(s)}));kw80.push(("span".into(),Val::Float(120.0f64)));kw80.push(("size".into(),Val::Str("3800x3200".into())));kw80.push(("up".into(),{let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(1i64));Val::tuple(s)}));kw80.push(("bg".into(),Val::Str("#f2eee8".into())));kw80.push(("transparent".into(),Val::Bool(true)));kw80.push(("solid".into(),Val::Bool(true)));kw80.push(("ortho".into(),Val::Bool(true)));kw80.push(("trim".into(),Val::Bool(false)));kw80.push(("ground".into(),Val::Bool(false)));kw80.push(("fog".into(),Val::Bool(false)));fun81.call(args79,kw80)?};e.set("pose",assigned78.clone())?;
let assigned82={let e=e.child();let out83=Val::list(vec![]);for item84 in {let fun87=e.get("paths")?.attr("items")?;let mut args85=Vec::new();let mut kw86=Vec::new();fun87.call(args85,kw86)?}.iter()? {let unpack88=unpack(item84,2)?;e.set("name",unpack88[0].clone())?;e.set("path",unpack88[1].clone())?;out83.attr("append")?.call(vec![{let d=Val::dict(vec![]);dict_extend(&d,e.get("pose")?)?;d.set(Val::Str("step".into()),{let fun91=e.get("str")?;let mut args89=Vec::new();let mut kw90=Vec::new();args89.push({let fun94=e.get("path")?.attr("relative_to")?;let mut args92=Vec::new();let mut kw93=Vec::new();args92.push(e.get("HARDWARE")?);fun94.call(args92,kw93)?});fun91.call(args89,kw90)?})?;d.set(Val::Str("out".into()),{let fun97=e.get("str")?;let mut args95=Vec::new();let mut kw96=Vec::new();args95.push(binary("truediv",e.get("OUT")?,{let mut str98=String::new();str98.push_str(&format(&e.get("name")?,&String::new())?);str98.push_str(".png");Val::Str(str98)})?);fun97.call(args95,kw96)?})?;d.set(Val::Str("zoom".into()),Val::Float(10.0f64))?;d}],vec![])?;}out83};e.set("jobs",assigned82.clone())?;
{let fun101=e.get("_hsm_render")?.attr("render")?;let mut args99=Vec::new();let mut kw100=Vec::new();args99.push(e.get("jobs")?);fun101.call(args99,kw100)?};
let assigned102={let fun105={let fun108=e.get("Image")?.attr("open")?;let mut args106=Vec::new();let mut kw107=Vec::new();args106.push(binary("truediv",e.get("OUT")?,Val::Str("scene.png".into()))?);fun108.call(args106,kw107)?}.attr("convert")?;let mut args103=Vec::new();let mut kw104=Vec::new();args103.push(Val::Str("RGBA".into()));fun105.call(args103,kw104)?};e.set("image",assigned102.clone())?;
let assigned109={let fun112={let fun115={let fun118=e.get("image")?.attr("getchannel")?;let mut args116=Vec::new();let mut kw117=Vec::new();args116.push(Val::Str("A".into()));fun118.call(args116,kw117)?}.attr("point")?;let mut args113=Vec::new();let mut kw114=Vec::new();args113.push({let params=vec![("a".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok(if {let v119=e.get("a")?;let v120=Val::Int(12i64);Val::Bool(compare("ge",v119.clone(),v120.clone())?.truthy()?)}.truthy()? {Val::Int(255i64)} else {Val::Int(0i64)});
Ok(Val::None)})});fun115.call(args113,kw114)?}.attr("getbbox")?;let mut args110=Vec::new();let mut kw111=Vec::new();fun112.call(args110,kw111)?};e.set("crop",assigned109.clone())?;
if !{let v121=e.get("crop")?;let v122=Val::None;Val::Bool(compare("is_not",v121.clone(),v122.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
let assigned123={let fun126=e.get("image")?.attr("crop")?;let mut args124=Vec::new();let mut kw125=Vec::new();args124.push(e.get("crop")?);fun126.call(args124,kw125)?};e.set("image",assigned123.clone())?;
let assigned127=binary("truediv",e.get("ASSETS")?,Val::Str("opening.png".into()))?;e.set("target",assigned127.clone())?;
{let fun130=e.get("image")?.attr("save")?;let mut args128=Vec::new();let mut kw129=Vec::new();args128.push(e.get("target")?);fun130.call(args128,kw129)?};
let mod131=rt.import_module("_guide_native")?;e.set("alpha_outlines",rt.member("_guide_native","alpha_outlines")?)?;
let assigned132={let fun135={let fun138={let fun141={let fun144=e.get("Image")?.attr("open")?;let mut args142=Vec::new();let mut kw143=Vec::new();args142.push(binary("truediv",e.get("OUT")?,Val::Str("components.png".into()))?);fun144.call(args142,kw143)?}.attr("convert")?;let mut args139=Vec::new();let mut kw140=Vec::new();args139.push(Val::Str("RGBA".into()));fun141.call(args139,kw140)?}.attr("crop")?;let mut args136=Vec::new();let mut kw137=Vec::new();args136.push(e.get("crop")?);fun138.call(args136,kw137)?}.attr("getchannel")?;let mut args133=Vec::new();let mut kw134=Vec::new();args133.push(Val::Str("A".into()));fun135.call(args133,kw134)?};e.set("alpha",assigned132.clone())?;
let assigned145={let fun148=e.get("alpha_outlines")?;let mut args146=Vec::new();let mut kw147=Vec::new();args146.push(e.get("alpha")?);args146.push(Val::Int(128i64));fun148.call(args146,kw147)?};e.set("loops",assigned145.clone())?;
if !e.get("loops")?.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
let assigned149=e.get("image")?.attr("size")?;let unpack150=unpack(assigned149.clone(),2)?;e.set("width",unpack150[0].clone())?;e.set("height",unpack150[1].clone())?;
let assigned151={let fun154={let fun157=e.get("hashlib")?.attr("sha256")?;let mut args155=Vec::new();let mut kw156=Vec::new();args155.push({let fun160=e.get("target")?.attr("read_bytes")?;let mut args158=Vec::new();let mut kw159=Vec::new();fun160.call(args158,kw159)?});fun157.call(args155,kw156)?}.attr("hexdigest")?;let mut args152=Vec::new();let mut kw153=Vec::new();fun154.call(args152,kw153)?};e.set("digest",assigned151.clone())?;
let assigned161={let mut s=Vec::new();s.push({let mut str162=String::new();str162.push_str("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"");str162.push_str(&format(&e.get("width")?,&String::new())?);str162.push_str("\" height=\"");str162.push_str(&format(&e.get("height")?,&String::new())?);str162.push_str("\" viewBox=\"0 0 ");str162.push_str(&format(&e.get("width")?,&String::new())?);str162.push_str(" ");str162.push_str(&format(&e.get("height")?,&String::new())?);str162.push_str("\" data-source-sha256=\"");str162.push_str(&format(&e.get("digest")?,&String::new())?);str162.push_str("\">");Val::Str(str162)});s.push(Val::Str("<title>Current faucet shank, four tubes and display cable</title>".into()));Val::list(s)};e.set("lines",assigned161.clone())?;
for item163 in e.get("loops")?.iter()? {
e.set("loop",item163)?;let assigned164=binary("add",binary("add",Val::Str("M".into()),{let fun167=Val::Str(" L".into()).attr("join")?;let mut args165=Vec::new();let mut kw166=Vec::new();args165.push({let e=e.child();let out168=Val::list(vec![]);for item169 in e.get("loop")?.iter()? {let unpack170=unpack(item169,2)?;e.set("x",unpack170[0].clone())?;e.set("y",unpack170[1].clone())?;out168.attr("append")?.call(vec![{let mut str171=String::new();str171.push_str(&format(&e.get("x")?,&String::new())?);str171.push_str(" ");str171.push_str(&format(&e.get("y")?,&String::new())?);Val::Str(str171)}],vec![])?;}out168});fun167.call(args165,kw166)?})?,Val::Str(" Z".into()))?;e.set("data",assigned164.clone())?;
{let fun174=e.get("lines")?.attr("append")?;let mut args172=Vec::new();let mut kw173=Vec::new();args172.push({let mut str175=String::new();str175.push_str("<path fill=\"none\" stroke=\"#46515b\" stroke-width=\"8.72\" d=\"");str175.push_str(&format(&e.get("data")?,&String::new())?);str175.push_str("\"/>");Val::Str(str175)});fun174.call(args172,kw173)?};
}
{let fun178=e.get("lines")?.attr("append")?;let mut args176=Vec::new();let mut kw177=Vec::new();args176.push(Val::Str("</svg>".into()));fun178.call(args176,kw177)?};
{let fun181=binary("truediv",e.get("ASSETS")?,Val::Str("opening-faucet-outline.svg".into()))?.attr("write_text")?;let mut args179=Vec::new();let mut kw180=Vec::new();args179.push(binary("add",{let fun184=Val::Str("\n".into()).attr("join")?;let mut args182=Vec::new();let mut kw183=Vec::new();args182.push(e.get("lines")?);fun184.call(args182,kw183)?},Val::Str("\n".into()))?);fun181.call(args179,kw180)?};
{let fun187=binary("truediv",e.get("OUT")?,Val::Str("registration.json".into()))?.attr("write_text")?;let mut args185=Vec::new();let mut kw186=Vec::new();args185.push(binary("add",{let fun190=e.get("json")?.attr("dumps")?;let mut args188=Vec::new();let mut kw189=Vec::new();args188.push({let d=Val::dict(vec![]);d.set(Val::Str("render_sha256".into()),e.get("digest")?)?;d.set(Val::Str("render_size".into()),{let mut s=Vec::new();s.push(e.get("width")?);s.push(e.get("height")?);Val::list(s)})?;d.set(Val::Str("native_crop".into()),e.get("crop")?)?;d.set(Val::Str("scene_step_sha256".into()),{let fun193={let fun196=e.get("hashlib")?.attr("sha256")?;let mut args194=Vec::new();let mut kw195=Vec::new();args194.push({let fun199=e.get("paths")?.get(Val::Str("scene".into()))?.attr("read_bytes")?;let mut args197=Vec::new();let mut kw198=Vec::new();fun199.call(args197,kw198)?});fun196.call(args194,kw195)?}.attr("hexdigest")?;let mut args191=Vec::new();let mut kw192=Vec::new();fun193.call(args191,kw192)?})?;d.set(Val::Str("component_step_sha256".into()),{let fun202={let fun205=e.get("hashlib")?.attr("sha256")?;let mut args203=Vec::new();let mut kw204=Vec::new();args203.push({let fun208=e.get("paths")?.get(Val::Str("components".into()))?.attr("read_bytes")?;let mut args206=Vec::new();let mut kw207=Vec::new();fun208.call(args206,kw207)?});fun205.call(args203,kw204)?}.attr("hexdigest")?;let mut args200=Vec::new();let mut kw201=Vec::new();fun202.call(args200,kw201)?})?;d.set(Val::Str("source_sha256".into()),{let e=e.child();let out209=Val::dict(vec![]);for item210 in {let mut s=Vec::new();s.push({let fun213=e.get("Path")?;let mut args211=Vec::new();let mut kw212=Vec::new();args211.push(e.get("__file__")?);fun213.call(args211,kw212)?});s.push(binary("truediv",e.get("HARDWARE")?,Val::Str("install-guide/_install_art.py".into()))?);s.push(binary("truediv",e.get("HARDWARE")?,Val::Str("install-guide/_install_art_mesh.py".into()))?);s.push(binary("truediv",e.get("HARDWARE")?,Val::Str("install-guide/install_art_props.rs".into()))?);s.push(binary("truediv",e.get("HARDWARE")?,Val::Str("faucet-layout/faucet-assembly.step.mesh".into()))?);s.push(binary("truediv",e.get("HARDWARE")?,Val::Str("faucet-layout/faucet_assembly.py".into()))?);Val::tuple(s)}.iter()? {e.set("p",item210)?;out209.set({let fun216=e.get("str")?;let mut args214=Vec::new();let mut kw215=Vec::new();args214.push({let fun219=e.get("p")?.attr("relative_to")?;let mut args217=Vec::new();let mut kw218=Vec::new();args217.push(e.get("ROOT")?);fun219.call(args217,kw218)?});fun216.call(args214,kw215)?},{let fun222={let fun225=e.get("hashlib")?.attr("sha256")?;let mut args223=Vec::new();let mut kw224=Vec::new();args223.push({let fun228=e.get("p")?.attr("read_bytes")?;let mut args226=Vec::new();let mut kw227=Vec::new();fun228.call(args226,kw227)?});fun225.call(args223,kw224)?}.attr("hexdigest")?;let mut args220=Vec::new();let mut kw221=Vec::new();fun222.call(args220,kw221)?})?;}out209})?;d.set(Val::Str("silhouette_scope".into()),Val::Str("Same orthographic pose and native viewport; outer component-alpha contours.".into()))?;d});kw189.push(("indent".into(),Val::Int(2i64)));fun190.call(args188,kw189)?},Val::Str("\n".into()))?);fun187.call(args185,kw186)?};
let assigned229=binary("truediv",e.get("ASSETS")?,Val::Str("print-resolution.json".into()))?;e.set("resolution_path",assigned229.clone())?;
let assigned230={let fun233=e.get("json")?.attr("loads")?;let mut args231=Vec::new();let mut kw232=Vec::new();args231.push({let fun236=e.get("resolution_path")?.attr("read_text")?;let mut args234=Vec::new();let mut kw235=Vec::new();fun236.call(args234,kw235)?});fun233.call(args231,kw232)?};e.set("resolution",assigned230.clone())?;
let assigned237={let d=Val::dict(vec![]);d.set(Val::Str("reference_size".into()),{let mut s=Vec::new();s.push(e.get("width")?);s.push(e.get("height")?);Val::list(s)})?;d.set(Val::Str("render_size".into()),{let mut s=Vec::new();s.push(e.get("width")?);s.push(e.get("height")?);Val::list(s)})?;d.set(Val::Str("scale".into()),{let mut s=Vec::new();s.push(Val::Float(1.0f64));s.push(Val::Float(1.0f64));Val::list(s)})?;d.set(Val::Str("render_sha256".into()),e.get("digest")?)?;d.set(Val::Str("source_sha256".into()),{let fun240={let fun243=e.get("hashlib")?.attr("sha256")?;let mut args241=Vec::new();let mut kw242=Vec::new();args241.push({let fun246={let fun249=e.get("Path")?;let mut args247=Vec::new();let mut kw248=Vec::new();args247.push(e.get("__file__")?);fun249.call(args247,kw248)?}.attr("read_bytes")?;let mut args244=Vec::new();let mut kw245=Vec::new();fun246.call(args244,kw245)?});fun243.call(args241,kw242)?}.attr("hexdigest")?;let mut args238=Vec::new();let mut kw239=Vec::new();fun240.call(args238,kw239)?})?;d.set(Val::Str("scene_step_sha256".into()),{let fun252={let fun255=e.get("hashlib")?.attr("sha256")?;let mut args253=Vec::new();let mut kw254=Vec::new();args253.push({let fun258=e.get("paths")?.get(Val::Str("scene".into()))?.attr("read_bytes")?;let mut args256=Vec::new();let mut kw257=Vec::new();fun258.call(args256,kw257)?});fun255.call(args253,kw254)?}.attr("hexdigest")?;let mut args250=Vec::new();let mut kw251=Vec::new();fun252.call(args250,kw251)?})?;d.set(Val::Str("fixed_native_crop".into()),e.get("crop")?)?;d.set(Val::Str("silhouette".into()),Val::Str("opening-faucet-outline.svg".into()))?;d};e.get("resolution")?.get(Val::Str("assets".into()))?.set(Val::Str("opening.png".into()),assigned237.clone())?;
{let fun261=e.get("resolution_path")?.attr("write_text")?;let mut args259=Vec::new();let mut kw260=Vec::new();args259.push(binary("add",{let fun264=e.get("json")?.attr("dumps")?;let mut args262=Vec::new();let mut kw263=Vec::new();args262.push(e.get("resolution")?);kw263.push(("indent".into(),Val::Int(2i64)));fun264.call(args262,kw263)?},Val::Str("\n".into()))?);fun261.call(args259,kw260)?};
{let fun267=e.get("docgen")?.attr("note_rewritten")?;let mut args265=Vec::new();let mut kw266=Vec::new();args265.push(e.get("resolution_path")?);fun267.call(args265,kw266)?};
{let fun270=e.get("print")?;let mut args268=Vec::new();let mut kw269=Vec::new();args268.push(Val::Str("Current opening artwork and component outline registered".into()));kw269.push(("flush".into(),Val::Bool(true)));fun270.call(args268,kw269)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun273 = e.get("main")?;
        let mut args271 = Vec::new();
        let mut kw272 = Vec::new();
        fun273.call(args271, kw272)?
    };
    Ok(Val::None)
}
