//! OCCT-compatible color storage and the appliance's authored material catalog.
use crate::common::*;
use anyhow::{Context,Result,bail,ensure};
use serde_json::{Value,json};
use std::collections::{BTreeMap,BTreeSet};

pub fn curve(v:f64)->f64{if v<=0.04045{v/12.92}else{((v+0.055)/1.055).powf(2.4)}}
pub fn curve32(v:f32)->f32{if v<=0.04045_f32{v/12.92_f32}else{((v+0.055_f32)/1.055_f32).powf(2.4_f32)}}
fn curve32_input(v:f64)->f64{if v<=0.04045_f32 as f64{(v/(12.92_f32 as f64))as f32 as f64}else{(((v+0.055_f32 as f64)as f32)/1.055_f32).powf(2.4_f32)as f64}}
pub fn inverse(v:f64)->f64{if v<=0.0031308{v*12.92}else{v.powf(1./2.4).mul_add(1.055,-0.055)}}
pub fn srgb(linear:[f64;3])->[f64;3]{linear.map(|c|inverse(c as f32 as f64))}
pub fn rgba(args:&Value,kwargs:&Value)->Result<Option<[f64;4]>>{
    let a=array(args);
    if a.len()==1&&a[0].is_string(){
        let s=text(&a[0]);if s.len()!=7||!s.starts_with('#')||!s[1..].bytes().all(|c|c.is_ascii_hexdigit()){return Ok(None)}
        let mut out=[0.,0.,0.,1.];for(i,start)in [1,3,5].into_iter().enumerate(){let byte=u8::from_str_radix(&s[start..start+2],16)?;out[i]=curve32(byte as f32/255_f32)as f64;}return Ok(Some(out))
    }
    let alpha=match a.len(){3=>kwargs["a"].as_f64().filter(|n|*n!=0.).unwrap_or(1.),4|5=>number(&a[3])?,_=>return Ok(None)};
    let mut out=[number(&a[0])?,number(&a[1])?,number(&a[2])?,alpha];if out.iter().any(|c|!(0.0..=1.0).contains(c)){return Ok(None)}
    let srgb_in=a.len()<5||a[4].as_bool().unwrap_or_else(||a[4].as_f64().is_some_and(|n|n!=0.));
    for c in &mut out[..3]{*c=if srgb_in{curve(*c)}else{*c}as f32 as f64;}out[3]=alpha as f32 as f64;Ok(Some(out))
}
pub fn rgb8_linear(rgb:&Value,step_safe:bool)->Result<[f64;3]>{
    let args=json!([number(&rgb[0])?/255.,number(&rgb[1])?/255.,number(&rgb[2])?/255.]);
    let mut linear=rgba(&args,&json!({}))?.context("RGB8 out of range")?;
    if step_safe{let s=srgb([linear[0],linear[1],linear[2]]);if s.iter().all(|v|*v>=254./255.){linear=rgba(&json!([254./255.,254./255.,254./255.,linear[3]]),&json!({}))?.unwrap();}}
    Ok([linear[0],linear[1],linear[2]])
}
fn stock()->Value{serde_json::from_str(include_str!("../catalog/materials.json")).unwrap()}
fn stock_srgb(name:&str)->Result<[f64;3]>{let args=constructor(&stock()["colors"][name])?;let c=rgba(&args,&json!({}))?.context("stock color")?;Ok(srgb([c[0],c[1],c[2]]))}
/// The machine's port colours: each port's own colour, the filament its chip on the wall prints
/// in, and the colour of the word on that chip. The wall's chips, the faucet's tube collars, the
/// routes and the palette all take them from here.
pub fn chips()->Result<Value>{
    let colors=json!({"carb":[31,111,235],"drain":[255,255,255],"water":[255,255,255],"co2":[214,58,58],"flavor":[38,38,41]});
    let black=stock_srgb("M_PETGF_BLACK")?.map(|c|c*255.);
    let white=json!([235,236,234]);
    let filaments=json!({"drain":["Fiberon PET-GF15 White",white],"water":["Fiberon PET-GF15 White",white],
        "carb":["Fiberon PET-GF15 Blue",[105,180,247]],"co2":["Fiberon PET-GF15 Red",[228,83,87]],"flavor":["Fiberon PET-GF15 Black",black]});
    let words=json!({"drain":black,"water":black,"carb":white,"co2":white,"flavor":white});
    let(mut hex,mut svg)=(serde_json::Map::new(),serde_json::Map::new());
    for(name,color)in colors.as_object().unwrap(){
        let c=array(color);let(r,g,b)=(c[0].as_u64().unwrap(),c[1].as_u64().unwrap(),c[2].as_u64().unwrap());
        hex.insert(name.clone(),json!(format!("#{r:02x}{g:02x}{b:02x}")));svg.insert(name.clone(),json!(format!("rgb({r}, {g}, {b})")));
    }
    Ok(json!({"port_order":["carb","drain","water","co2","flavor"],"filament_order":["drain","water","carb","co2","flavor"],
        "port_colors":colors,"chip_filaments":filaments,"chip_word_colors":words,"hex":hex,"svg":svg}))
}
fn constructor(v:&Value)->Result<Value>{
    if let Some(bytes)=v["bytes"].as_array(){return Ok(json!(bytes.iter().map(|v|number(v).map(|v|v/255.)).collect::<Result<Vec<_>>>()?))}
    Ok(v["args"].clone())
}
fn raw_linear(v:&Value)->Result<[f64;3]>{
    if v["linear"].is_array(){return Ok([number(&v["linear"][0])?,number(&v["linear"][1])?,number(&v["linear"][2])?])}
    let linear=rgba(&v["args"],v.get("kwargs").unwrap_or(&json!({})))?.context("color requires its native linear record")?;Ok([linear[0],linear[1],linear[2]])
}
fn safe_linear(v:&Value)->Result<[f64;3]>{
    let linear=raw_linear(v)?;let s=if v["srgb"].is_array(){[number(&v["srgb"][0])?,number(&v["srgb"][1])?,number(&v["srgb"][2])?]}else{srgb(linear)};
    if s.iter().all(|v|*v>=254./255.){Ok(rgba(&json!([254./255.,254./255.,254./255.]),&json!({}))?.unwrap()[..3].try_into().unwrap())}else{Ok(linear)}
}
fn key(rgb:[f64;3])->[u64;3]{rgb.map(|v|if v==0.{0}else{v.to_bits()})}
pub fn finish_rows(finishes:&Value,named:&Value)->Result<Vec<Value>>{
    let mut out=vec![];let mut seen=BTreeMap::<[u64;3],BTreeSet<(u64,u64)>>::new();
    for entry in array(finishes){let rough=number(&entry[1])?;let metal=number(&entry[2])?;
        for rgb in [raw_linear(&entry[0])?,safe_linear(&entry[0])?]{let k=key(rgb);let pair=(rough.to_bits(),metal.to_bits());if let Some(row)=seen.get_mut(&k){row.insert(pair);continue}seen.insert(k,BTreeSet::from([pair]));out.push(json!({"rgb":rgb,"roughness":rough,"metalness":metal}));}
    }
    for(k,values)in &seen{ensure!(values.len()==1,"_materials: linear {:?} is given {} finishes. Two substances at one colour cannot both be drawn — give one of them its own.",k.map(f64::from_bits),values.len());}
    let mut missing=vec![];for(name,v)in named.as_object().into_iter().flatten(){if !seen.contains_key(&key(raw_linear(v)?)){missing.push(name.clone());}}
    ensure!(missing.is_empty(),"_materials: {} name a colour with no finish. Add each to FINISHES — a material cannot be drawn without saying how it takes the light.",missing.join(", "));
    Ok(out)
}
fn all_finishes(r:&Value)->Result<Vec<Value>>{
    let mut out=finish_rows(&r["finishes"],&r["named"])?;
    for(name,spool)in r["spools"].as_object().into_iter().flatten(){
        let raw=json!({"args":[number(&spool["rgb"][0])?/255.,number(&spool["rgb"][1])?/255.,number(&spool["rgb"][2])?/255.,spool["alpha"]]});
        for rgb in [raw_linear(&raw)?,safe_linear(&raw)?]{
            if let Some(held)=out.iter().find(|v|array(&v["rgb"]).iter().zip(rgb).all(|(a,b)|a.as_f64()==Some(b))){
                if held["roughness"]==spool["roughness"]&&held["metalness"]==spool["metalness"]{continue}
                ensure!(r["shared"].get(name).is_some(),"check_finishes: spool {name:?} and a material share the colour {rgb:?} but ask for different finishes");
            }else{out.push(json!({"rgb":rgb,"roughness":spool["roughness"],"metalness":spool["metalness"]}));}
        }
    }
    out.sort_by(|a,b|{for i in 0..3{let c=a["rgb"][i].as_f64().unwrap().total_cmp(&b["rgb"][i].as_f64().unwrap());if !c.is_eq(){return c}}std::cmp::Ordering::Equal});Ok(out)
}
fn petgf(r:&Value)->Result<Value>{
    let normalized=text(&r["name"]).replace('_',"-");let mut parts=normalized.split('/').collect::<Vec<_>>();
    if parts.last().is_some_and(|s|!s.is_empty()&&s.bytes().all(|c|c.is_ascii_digit())){parts.pop();}
    let name=parts.last().copied().unwrap_or("");let data=stock();
    if array(&data["petgf_black_parts"]).iter().any(|v|text(v)==name)||array(&data["wall_names"]).iter().any(|v|format!("enclosure-{}",text(v))==name){return Ok(json!({"symbol":"M_PETGF_BLACK"}))}
    let (base,word)=name.strip_suffix("-ink").map(|s|(s,true)).unwrap_or((name,false));
    let nameplate=base=="nameplate"||base.strip_prefix("nameplate-").is_some_and(|s|!s.is_empty()&&s.bytes().all(|c|c.is_ascii_digit()));
    let mut fluid=None;let mut is_word=word;
    if nameplate{fluid=Some("flavor")}else{
        for prefix in ["bulkhead-ring-","tube-collar-","collar-"]{if let Some(rest)=name.strip_prefix(prefix){let(rest,word)=rest.strip_suffix("-word").map(|s|(s,true)).unwrap_or((rest,false));is_word=word;
            fluid=match rest{"water"=>Some("water"),"carb"=>Some("carb"),"co2"=>Some("co2"),"flavor"|"flavor-a"|"flavor-b"=>Some("flavor"),_=>None};break
        }}
    }
    let Some(fluid)=fluid else{return Ok(Value::Null)};
    let rgb=&r[if is_word{"word_colors"}else{"chip_colors"}][fluid];let mut args=json!([number(&rgb[0])?/255.,number(&rgb[1])?/255.,number(&rgb[2])?/255.]);
    let linear=rgba(&args,&json!({}))?.context("PET-GF palette")?;
    if srgb([linear[0],linear[1],linear[2]]).iter().all(|v|*v>=254./255.){args=json!([254./255.,254./255.,254./255.,linear[3]]);}
    Ok(json!({"args":args}))
}
pub fn dispatch(op:&str,r:&Value)->Result<Value>{
    Ok(match op{
        "rgba"=>json!(rgba(&r["args"],&r["kwargs"])?),"srgb"=>json!(srgb([number(&r["rgb"][0])?,number(&r["rgb"][1])?,number(&r["rgb"][2])?])),
        "f32"=>json!(number(&r["value"])?as f32 as f64),"curve"=>json!(curve(number(&r["value"])?)),"curve32"=>json!(curve32_input(number(&r["value"])?)),"inverse"=>json!(inverse(number(&r["value"])?)),
        "rgb8_linear"=>json!(rgb8_linear(&r["rgb"],r["step_safe"].as_bool().unwrap_or(false))?),
        "catalog"=>{let mut data=stock();data["whitest"]=json!(254./255.);let colors=data["colors"].as_object().unwrap().iter().map(|(k,v)|Ok((k.clone(),constructor(v)?))).collect::<Result<serde_json::Map<String,Value>>>()?;data["colors"]=json!(colors);let mut parts=array(&data["petgf_black_parts"]).to_vec();parts.extend(array(&data["wall_names"]).iter().map(|n|json!(format!("enclosure-{}",text(n)))));data["petgf_black_parts"]=json!(parts);data},
        "palette_constructors"=>{let mut seen=BTreeSet::new();let mut out=vec![];for rgb in array(&r["rgbs"]){if seen.insert(rgb.to_string()){out.push(constructor(&json!({"bytes":rgb}))?);}}json!(out)},
        "stock_srgb"=>json!(stock_srgb(text(&r["name"]))?),
        "chips"=>chips()?,
        "linear"=>json!(raw_linear(&r["color"])?),
        "petgf"=>petgf(r)?,
        "step_safe"=>{let a=array(&r["srgb"]);if a.len()>=3&&a[..3].iter().all(|v|v.as_f64().is_some_and(|n|n>=254./255.)){json!([254./255.,254./255.,254./255.,a.get(3).cloned().unwrap_or(json!(1.))])}else{Value::Null}},
        "place_finish"=>{let mut out=array(&r["rows"]).to_vec();let rgb=&r["rgb"];let spool=&r["spool"];if let Some(held)=out.iter().find(|v|v["rgb"]==*rgb){ensure!((held["roughness"]==spool["roughness"]&&held["metalness"]==spool["metalness"])||r["shared"].get(text(&r["name"])).is_some(),"check_finishes: spool and material share a colour with different finishes");}else{out.push(json!({"rgb":rgb,"roughness":spool["roughness"],"metalness":spool["metalness"]}));}json!(out)},
        "finish_rows"=>json!(finish_rows(&r["finishes"],&r["named"])?),"all_finishes"=>json!(all_finishes(r)?),
        "find_finish"=>{let rows=all_finishes(r)?;let rgb=[number(&r["rgb"][0])?,number(&r["rgb"][1])?,number(&r["rgb"][2])?];let mut distance=r["tol"].as_f64().unwrap_or(4e-4).powi(2);let mut best=Value::Null;
            for row in rows{let d=(0..3).map(|i|(row["rgb"][i].as_f64().unwrap()-rgb[i]).powi(2)).sum::<f64>();if d<=distance{distance=d;best=row;}}best},
        _=>bail!("unknown color operation: {op}")
    })
}
