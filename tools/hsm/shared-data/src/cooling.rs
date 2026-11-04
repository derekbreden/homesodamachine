//! PET-GF filament slot selection and settings updates.
use anyhow::{Context,Result,bail};
use hsm_shared_data::common::*;
use serde_json::{Value,json};

const ORDER:[&str;10]=["fan_min_speed","fan_max_speed","additional_cooling_fan_speed","first_x_layer_fan_speed","first_x_layer_part_fan_speed","enable_overhang_bridge_fan","overhang_fan_speed","overhang_fan_threshold","reduce_fan_stop_start_freq","pre_start_fan_time"];
fn values()->Value{let data:Value=serde_json::from_str(include_str!("../catalog/scalars.json")).unwrap();data["petgf_cooling"]["VALUES"].clone()}
fn truthy(v:&Value)->bool{match v{Value::Null=>false,Value::Bool(v)=>*v,Value::String(s)=>!s.is_empty(),Value::Number(n)=>n.as_f64()!=Some(0.),Value::Array(a)=>!a.is_empty(),Value::Object(m)=>!m.is_empty()}}
fn string(v:&Value)->String{match v{Value::Null=>"None".into(),Value::Bool(b)=>if *b{"True"}else{"False"}.into(),Value::String(s)=>s.clone(),v=>v.to_string()}}
pub fn dispatch(op:&str,r:&Value)->Result<Value>{Ok(match op{
    "values"=>{let values=values();json!(ORDER.map(|name|json!([name,values[name]])))},
    "member_names"=>json!(array(&r["names"]).iter().filter(|name|{let s=text(name);s=="Metadata/project_settings.config"||(s.starts_with("Metadata/filament_settings_")&&s.ends_with(".config"))}).collect::<Vec<_>>()),
    "apply"=>{
        let mut settings=r["settings"].clone();let map=settings.as_object_mut().context("filament settings must be an object")?;
        let mut identities=map.get("filament_settings_id").cloned().unwrap_or(json!([]));
        if !truthy(&identities){identities=json!([map.get("name").cloned().unwrap_or(json!(""))]);}
        if identities.is_string(){identities=json!([identities]);}
        let identities=identities.as_array().context("filament settings ids must be a list or string")?;
        let indices=identities.iter().enumerate().filter_map(|(i,name)|{let name=text(name).to_lowercase();(name.contains("pet-gf")||name.contains("petgf")).then_some(i)}).collect::<Vec<_>>();
        let values=values();let mut changes=serde_json::Map::new();let mut updates=vec![];
        if !indices.is_empty(){for key in ORDER{
            let old=map.get(key).cloned().unwrap_or(Value::Null);
            let fill=if truthy(&old){string(&old)}else{"0".into()};
            let mut new=old.as_array().cloned().unwrap_or_else(||vec![json!(fill);identities.len()]);
            for i in &indices{while *i>=new.len(){new.push(new.last().cloned().unwrap_or(json!("0")));}new[*i]=values[key].clone();}
            let new=json!(new);if new!=old{let change=json!({"from":old,"to":new});changes.insert(key.into(),change.clone());updates.push(json!([key,change]));map.insert(key.into(),new);}
        }}
        json!({"settings":settings,"changes":changes,"updates":updates})
    },
    _=>bail!("unknown cooling operation {op}")
})}
