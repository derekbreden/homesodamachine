//! Project evidence records, precision-preserving dates and deterministic exports.
use crate::shared::*;
use anyhow::{Context as _,Result,bail,ensure};
use num_bigint::BigInt;
use num_traits::{ToPrimitive,Zero};
use serde_json::{Value,json};
use sha2::{Digest,Sha256};
use std::{collections::{BTreeMap,BTreeSet},path::Path};

#[path="analysis_validate.rs"] mod validation;
#[path="analysis_summary.rs"] mod summary;
#[path="analysis_export.rs"] mod export;
pub use export::{export_csv,export_json,render_report};
pub fn definitions()->Value{serde_json::from_str(include_str!("../catalog/evidence.json")).unwrap()}
pub fn text(v:&Value)->&str{v.as_str().unwrap_or("")}
pub fn truth(v:&Value)->bool{match v{Value::Null=>false,Value::Bool(v)=>*v,Value::Number(v)=>v.as_f64()!=Some(0.),Value::String(v)=>!v.is_empty(),Value::Array(v)=>!v.is_empty(),Value::Object(v)=>!v.is_empty()}}
pub fn array(v:&Value)->&[Value]{v.as_array().map(Vec::as_slice).unwrap_or(&[])}
pub fn integer(v:&Value)->i64{v.as_i64().unwrap_or(0)}
pub fn contains(v:&Value,s:&str)->bool{array(v).iter().any(|v|v.as_str()==Some(s))}
pub fn allowed(name:&str,v:&Value)->bool{definitions()[name].as_array().is_some_and(|a|a.contains(v))}
pub fn ids(v:&Value)->Vec<String>{let set:BTreeSet<_>=array(v).iter().filter_map(Value::as_str).map(str::to_owned).collect();set.into_iter().collect()}
fn selected(record:&Value,fields:&Value)->Value{
    let map=record.as_object().into_iter().flatten().filter(|(k,_)|contains(fields,k)).map(|(k,v)|(k.clone(),v.clone())).collect::<serde_json::Map<_,_>>();json!(map)
}
fn sorted_ids(mut v:Value)->Value{for name in ["source_ids","order_ids","purchase_ids","event_ids"]{if v[name].is_array(){v[name]=json!(ids(&v[name]));}}v}
pub fn plain_text(v:&Value)->String{
    let s=if let Some(s)=v.as_str(){s.to_owned()}else{py_repr(v)};
    let s=re(r"(?s)<!--.*?-->").replace_all(&s,"");
    let s=re(r"\[([^\]]*)\]\([^)]*\)").replace_all(&s,"$1");
    let s=re(r"<[^>]*>").replace_all(&s,"");
    re(r"[*~`]").replace_all(&s,"").trim().to_owned()
}
pub fn py_repr(v:&Value)->String{match v{
    Value::Null=>"None".into(),Value::Bool(v)=>if *v{"True"}else{"False"}.into(),Value::String(v)=>{
        let quote=if v.contains('\'')&&!v.contains('"'){'"'}else{'\''};
        let s=v.replace('\\',"\\\\").replace(quote,&format!("\\{quote}")).replace('\n',"\\n").replace('\r',"\\r");format!("{quote}{s}{quote}")
    },Value::Array(v)=>format!("[{}]",v.iter().map(py_repr).collect::<Vec<_>>().join(", ")),
    Value::Object(v)=>format!("{{{}}}",v.iter().map(|(k,v)|format!("{}: {}",py_repr(&json!(k)),py_repr(v))).collect::<Vec<_>>().join(", ")),
    _=>v.to_string(),
}}
pub fn parse_date(v:&Value)->Value{
    if !truth(v)||["—","-","unknown"].contains(&plain_text(v).as_str()){return Value::Null}
    if v.is_object(){return v.clone()}
    let s=plain_text(v);
    let days=re(r"\d{4}-\d{2}-\d{2}").find_iter(&s).filter(|m|{
        let before=s[..m.start()].chars().last();let after=s[m.end()..].chars().next();
        !before.is_some_and(|c|c.is_ascii_digit())&&!after.is_some_and(|c|c.is_ascii_digit())
    }).map(|m|m.as_str().to_owned()).collect::<Vec<_>>();
    if days.len()>1{json!({"precision":"range","start":days[0],"end":days.last().unwrap()})}
    else if days.len()==1{json!({"precision":"day","value":days[0]})}
    else if re(r"^\d{4}-\d{2}$").is_match(&s){json!({"precision":"month","value":s})}else{Value::Null}
}
pub fn month_days(year:i32,month:i32)->Option<i32>{Some(match month{1|3|5|7|8|10|12=>31,4|6|9|11=>30,2=>if year%4==0&&(year%100!=0||year%400==0){29}else{28},_=>return None})}
pub fn calendar_day(s:&str)->Option<(i32,i32,i32)>{
    if !re(r"^\d{4}-\d{2}-\d{2}$").is_match(s){return None}
    let p=s.split('-').map(str::parse::<i32>).collect::<std::result::Result<Vec<_>,_>>().ok()?;
    if !(1..=9999).contains(&p[0])||p[2]<1||p[2]>month_days(p[0],p[1])?{return None}Some((p[0],p[1],p[2]))
}
pub fn ordinal(s:&str)->Option<i64>{
    let(y,m,d)=calendar_day(s)?;let prior=(y-1)as i64;
    let mut days=365*prior+prior/4-prior/100+prior/400;
    for month in 1..m{days+=month_days(y,month)? as i64;}Some(days+d as i64)
}
pub fn date_bounds(v:&Value)->Result<Option<(String,String)>>{
    if v.is_null(){return Ok(None)}
    let result=match text(&v["precision"]){
        "day"=>{let s=text(&v["value"]);ensure!(calendar_day(s).is_some(),"invalid date");(s.into(),s.into())},
        "month"=>{let s=text(&v["value"]);ensure!(re(r"^\d{4}-\d{2}$").is_match(s),"invalid month");let y=s[..4].parse::<i32>()?;let m=s[5..].parse::<i32>()?;let last=month_days(y,m).context("invalid month")?;ensure!((1..=9999).contains(&y),"invalid year");(format!("{s}-01"),format!("{s}-{last:02}"))},
        _=>{let(a,b)=(text(&v["start"]),text(&v["end"]));ensure!(calendar_day(a).is_some()&&calendar_day(b).is_some(),"invalid range");(a.into(),b.into())}
    };Ok(Some(result))
}
pub fn date_month(v:&Value)->Result<String>{
    if let Some((a,b))=date_bounds(v)?{if a[..7]==b[..7]{return Ok(a[..7].into())}}
    Ok("undated_unallocated".into())
}
fn exact(value:&Value)->Result<(BigInt,BigInt)>{
    let s=value.as_str().map(str::to_owned).unwrap_or_else(||value.to_string());
    let(s,exp)=s.split_once(['e','E']).map(|(a,b)|(a.to_owned(),b.parse::<i32>())).unwrap_or((s.clone(),Ok(0)));
    let places=s.split_once('.').map(|(_,p)|p.len()as i32).unwrap_or(0)-exp?;
    let n=s.replace('.',"").parse::<BigInt>()?;let power=BigInt::from(10).pow(places.unsigned_abs());
    Ok(if places>=0{(n,power)}else{(n*power,BigInt::from(1))})
}
pub fn to_minor(v:&Value,currency:&str,scales:&Value)->Result<Value>{
    if v.is_null(){return Ok(Value::Null)}
    let error=format!("amount is not an exact {currency} minor-unit value");
    let(n,d)=exact(v).with_context(||error.clone())?;let scale=scales[currency].as_u64().context("undeclared currency")?;
    let n=n*BigInt::from(10).pow(scale as u32);ensure!((&n%&d).is_zero(),"{error}");
    Ok(json!((n/d).to_i64().with_context(||error)?))
}
pub fn format_minor(amount:&Value,currency:&str,scales:&Value)->Result<String>{
    if amount.is_null(){return Ok("unknown".into())}
    let scale=scales[currency].as_u64().unwrap_or(2)as usize;
    let amount=amount.as_i64().context("minor-unit integer")?;let sign=if amount<0{"-"}else{""};let digits=amount.unsigned_abs().to_string();
    let padded=format!("{:0>width$}",digits,width=scale+1);let at=padded.len()-scale;let whole=&padded[..at];
    let grouped=whole.chars().enumerate().map(|(i,c)|if i>0&&(whole.len()-i)%3==0{format!(",{c}")}else{c.to_string()}).collect::<String>();
    let frac=if scale>0{format!(".{}",&padded[at..])}else{String::new()};
    Ok(format!("{}{sign}{grouped}{frac}",if currency=="USD"{"$".into()}else{format!("{currency} ")}))
}
pub fn fingerprint(ledger:&str,evidence:&Value)->String{
    let ledger=re(r"\[[^\]]*\]\((LEDGER_[A-Z0-9_]+)\)").replace_all(ledger,"[generated]($1)");
    let mut hash=Sha256::new();hash.update(ledger.as_bytes());hash.update([0]);hash.update(serde_json::to_vec(evidence).unwrap());format!("sha256:{:x}",hash.finalize())
}

pub fn analyze(rows:&Value,evidence:&Value,fingerprint:&Value)->Result<Value>{
    let defs=definitions();let mut errors=vec![];let mut warnings=vec![];
    if evidence["schema_version"]!=json!(1){errors.push("unsupported evidence schema_version".into());}
    let scales=evidence.get("currency_scales").cloned().unwrap_or_else(||json!({"USD":2}));
    ensure!(scales.as_object().is_some_and(|s|!s.is_empty()&&s.values().all(|v|v.as_u64().is_some_and(|n|n<=6))),"currency_scales must map currencies to integer scales 0..6");
    let metadata=&evidence["purchases"];
    let mut sources=vec![];let mut orders=vec![];
    for(kind,field,dest)in [("sources","SOURCE_FIELDS",&mut sources),("orders","ORDER_FIELDS",&mut orders)]{
        for(key,value)in evidence[kind].as_object().into_iter().flatten(){
            let mut row=selected(value,&defs[field]);row[if kind=="sources"{"source_id"}else{"order_id"}]=json!(key);dest.push(sorted_ids(row));
        }
    }
    let mut purchases=vec![];let mut seen=BTreeSet::new();
    for row in array(rows){
        let id=text(&row["purchase_id"]);
        if id.is_empty(){errors.push(format!("purchase row lacks persistent ID (line {})",row.get("line").map(|v|v.to_string()).unwrap_or_else(||"?".into())));continue}
        if !seen.insert(id.to_owned()){errors.push(format!("duplicate purchase_id: {id}"));}
        let meta=&metadata[id];if !truth(meta){errors.push(format!("purchase lacks metadata: {id}"));}
        let currency=meta.get("currency").or_else(||row.get("currency")).and_then(Value::as_str).unwrap_or("USD");
        let amount=if scales[currency].is_null(){errors.push(format!("{id}: undeclared currency {currency}"));Value::Null}else{
            match to_minor(&row["cost"],currency,&scales){Ok(v)=>v,Err(e)=>{errors.push(format!("{id}: {e}"));Value::Null}}
        };
        let date_value=["ordered","invoice_date","receipt_date"].into_iter().find_map(|k|row.get(k).filter(|v|truth(v))).cloned().unwrap_or(json!(""));
        let mut record=json!({
            "purchase_id":id,"ledger_purchase_id":id,"vendor":meta.get("vendor").unwrap_or(&json!("Unknown")),
            "description":plain_text(row.get("description").unwrap_or(&row["part"])),"section":row["section"],"quantity":row["quantity"],
            "quantity_text":plain_text(row.get("quantity_text").unwrap_or(&json!(""))),"price_basis":row.get("price_basis").unwrap_or(&json!("row_total")),
            "unit_amount_minor":null,"amount_minor":amount,"currency":currency,"amount_evidence":meta.get("amount_evidence").unwrap_or(&json!("legacy_unverified")),
            "row_date":parse_date(&date_value),"row_date_basis":meta.get("row_date_basis").or_else(||row.get("row_date_basis")).unwrap_or(&json!("order_date")),
            "order_date":parse_date(row.get("ordered").unwrap_or(&json!(""))),"delivery_date":parse_date(row.get("delivered").unwrap_or(&json!(""))),
            "fulfillment":row["status"],"purpose":meta.get("purpose").unwrap_or(&json!("unclassified")),"stream":meta.get("stream").unwrap_or(&json!("purchase")),
            "order_ids":ids(&meta["order_ids"]),"source_ids":ids(&meta["source_ids"]),"allocation_status":meta.get("allocation_status").unwrap_or(&json!("unresolved")),
            "contributes":meta.get("contributes").unwrap_or(&json!(true)),
            "invoice_date":parse_date(row.get("invoice_date").filter(|v|truth(v)).unwrap_or(&meta["invoice_date"])),
            "receipt_date":parse_date(row.get("receipt_date").filter(|v|truth(v)).unwrap_or(&meta["receipt_date"])),"service_period":parse_date(&meta["service_period"])
        });
        if !scales[currency].is_null(){match to_minor(&row["unit_price"],currency,&scales){Ok(v)=>record["unit_amount_minor"]=v,Err(e)=>errors.push(format!("{id}: unit price {e}"))}}
        if meta.get("delivery_dates").is_some(){record["delivery_dates"]=json!(array(&meta["delivery_dates"]).iter().map(parse_date).collect::<Vec<_>>());}
        if text(&record["row_date_basis"])!="order_date"{record["order_date"]=Value::Null;let key=text(&record["row_date_basis"]);if ["invoice_date","receipt_date"].contains(&key){let key=key.to_owned();record[&key]=record["row_date"].clone();}}
        if let Some(v)=meta.get("replacement_for"){record["replacement_for"]=v.clone();}
        if let Some(v)=meta.get("price_history"){record["price_history"]=json!(array(v).iter().map(|v|sorted_ids(selected(v,&defs["HISTORY_FIELDS"]))).collect::<Vec<_>>());}
        if text(&row["price_basis"])=="unit"&&row["quantity"].is_null(){errors.push(format!("{id}: explicit unit price has no usable quantity"));}
        let children=&evidence["details"][id];let grouped=truth(children);
        if grouped{record["contributes"]=json!(false);record["record_role"]=json!("group_summary");}else{record["record_role"]=json!("purchase");}
        purchases.push(record.clone());
        if !grouped{continue}
        let Some(amount)=record["amount_minor"].as_i64()else{errors.push(format!("{id}: cannot reconstruct an unknown grouped amount"));continue};
        let fields=json!(["purchase_id","vendor","description","quantity","amount_minor","currency","amount_evidence","purpose","order_ids","order_date","invoice_date","receipt_date","service_period","source_ids","allocation_status","contributes","replacement_for","stream"]);
        let mut child_total=0;
        for child in array(children){
            let mut r=record.clone();for(k,v)in selected(child,&fields).as_object().unwrap(){r[k]=v.clone();}
            r["ledger_purchase_id"]=json!(id);r["record_role"]=json!("detail");r["price_basis"]=json!("row_total");r["unit_amount_minor"]=Value::Null;r["quantity_text"]=json!("");r["contributes"]=child.get("contributes").cloned().unwrap_or(json!(true));
            for key in ["order_date","invoice_date","receipt_date","service_period"]{r[key]=parse_date(&child[key]);}
            r.as_object_mut().unwrap().remove("price_history");r["description"]=json!(plain_text(&r["description"]));
            if r["currency"]!=json!(currency)||r["amount_minor"].as_i64().is_none(){errors.push(format!("{id}: detail needs same-currency exact amount"));continue}
            if truth(&r["contributes"]){child_total+=integer(&r["amount_minor"]);}purchases.push(sorted_ids(r));
        }
        if child_total>amount{errors.push(format!("{id}: detail exceeds canonical group by {} minor units",child_total-amount));}
        else if child_total<amount{
            let mut r=record.clone();for(k,v)in json!({"purchase_id":format!("{id}:legacy-remainder"),"description":format!("Unresolved remainder — {}",text(&record["description"])),"record_role":"legacy_remainder","amount_minor":amount-child_total,"amount_evidence":"legacy_unverified","contributes":true,"order_ids":[],"source_ids":[],"quantity":null,"quantity_text":"","price_basis":"row_total","unit_amount_minor":null}).as_object().unwrap(){r[k]=v.clone();}
            r.as_object_mut().unwrap().remove("price_history");purchases.push(r);
        }
    }
    for(kind,label)in [("purchases","metadata names missing Markdown purchases: "),("details","details name missing Markdown purchases: ")]{
        let missing=evidence[kind].as_object().into_iter().flatten().map(|(k,_)|k).filter(|k|!seen.contains(*k)).cloned().collect::<Vec<_>>();if !missing.is_empty(){errors.push(format!("{label}{}",missing.join(", ")));}
    }
    purchases.sort_by(|a,b|text(&a["purchase_id"]).cmp(text(&b["purchase_id"])));
    let mut result=json!({"schema_version":1,"as_of":evidence["as_of"],"reporting_period":evidence["reporting_period"],"currency_scales":scales,"input_fingerprint":fingerprint,"purchases":purchases,"orders":orders,"sources":sources});
    for(kind,field,id,sort)in [("events","EVENT_FIELDS","event_id",true),("allocations","ALLOCATION_FIELDS","allocation_id",false),("coverage","COVERAGE_FIELDS","coverage_id",true),("gaps","GAP_FIELDS","gap_id",true)]{
        let mut rows=array(&evidence[kind]).iter().map(|v|{let v=selected(v,&defs[field]);if sort{sorted_ids(v)}else{v}}).collect::<Vec<_>>();rows.sort_by(|a,b|text(&a[id]).cmp(text(&b[id])));result[kind]=json!(rows);
    }
    validation::validate(&result,&mut errors,&mut warnings);
    let sorted=|items:&Vec<String>|items.iter().cloned().collect::<BTreeSet<_>>().into_iter().collect::<Vec<_>>();
    result["validation"]=json!({"errors":sorted(&errors),"warnings":sorted(&warnings)});
    if errors.is_empty(){relationships(&mut result);result["summary"]=summary::summaries(&result)?;}
    Ok(result)
}

pub fn relationships(data:&mut Value){
    let allocations=array(&data["allocations"]).to_vec();let mut events=array(&data["events"]).to_vec();
    for event in &mut events{
        let id=event["event_id"].clone();let related=allocations.iter().filter(|a|a["event_id"]==id).collect::<Vec<_>>();
        event["purchase_ids"]=json!(related.iter().filter_map(|a|a["purchase_id"].as_str()).collect::<BTreeSet<_>>());
        event["order_ids"]=json!(ids(&event["order_ids"]).into_iter().chain(related.iter().filter_map(|a|a["order_id"].as_str().map(str::to_owned))).collect::<BTreeSet<_>>());
        event["unallocated_to_purchase_minor"]=json!(related.iter().filter(|a|!truth(&a["purchase_id"])).map(|a|integer(&a["amount_minor"])).sum::<i64>());
        let mut ids=related.iter().map(|a|text(&a["allocation_id"]).to_owned()).collect::<Vec<_>>();ids.sort();event["allocation_ids"]=json!(ids);
    }
    let mut purchases=array(&data["purchases"]).to_vec();
    for p in &mut purchases{
        let id=text(&p["purchase_id"]);let related=events.iter().filter(|e|contains(&e["purchase_ids"],id)).collect::<Vec<_>>();
        p["event_ids"]=json!(related.iter().map(|e|e["event_id"].clone()).collect::<Vec<_>>());
        let charged=|event:&&Value,kind:&str|text(&event["event_type"])==kind&&text(&event["confirmation"])=="confirmed"&&text(&event["allocation_status"])!="unresolved";
        let charges=related.iter().filter(|e|charged(e,"charge")).count();let refunds=related.iter().filter(|e|charged(e,"refund")).count();
        let allocated=|kind|allocations.iter().filter(|a|a["purchase_id"]==p["purchase_id"]&&events.iter().find(|e|e["event_id"]==a["event_id"]).is_some_and(|e|charged(&e,kind))).map(|a|integer(&a["amount_minor"])).sum::<i64>();
        let charge=allocated("charge");let refund=allocated("refund");
        p["merchant_charge_allocated_minor"]=json!(charge);p["merchant_refund_allocated_minor"]=json!(refund);
        let payment=if charges>0{if p["amount_minor"].as_i64().is_some_and(|amount|charge<amount){if refunds>0{"merchant_charge_partial_and_refund"}else{"merchant_charge_partial"}}else if refunds>0{"merchant_charge_and_refund"}else{"merchant_charge"}}
            else if refunds>0{"merchant_refund_only"}else if p["amount_minor"]==json!(0)&&truth(&p["replacement_for"])&&text(&p["amount_evidence"])=="final_vendor_amount"{"zero_price_replacement"}else{"unknown"};
        p["payment_evidence"]=json!(payment);p["split_charge"]=json!(charges>1);
    }
    for order in data["orders"].as_array_mut().unwrap(){let id=text(&order["order_id"]);order["purchase_ids"]=json!(purchases.iter().filter(|p|contains(&p["order_ids"],id)).map(|p|p["purchase_id"].clone()).collect::<Vec<_>>());order["event_ids"]=json!(events.iter().filter(|e|contains(&e["order_ids"],text(&order["order_id"]))).map(|e|text(&e["event_id"]).to_owned()).collect::<BTreeSet<_>>());}
    data["events"]=json!(events);data["purchases"]=json!(purchases);
}

pub fn dispatch(op:&str,r:&Value,ctx:&mut Context)->Result<Value>{
    Ok(match op{
        "definitions"=>definitions(),"plain_text"=>json!(plain_text(&r["value"])),"parse_date"=>parse_date(&r["value"]),"date_bounds"=>json!(date_bounds(&r["value"])?),"date_month"=>json!(date_month(&r["value"])?),
        "to_minor"=>to_minor(&r["value"],arg(r,"currency")?,&r["scales"])?,"format_minor"=>json!(format_minor(&r["value"],r["currency"].as_str().unwrap_or("USD"),r.get("scales").unwrap_or(&json!({"USD":2})))?),
        "fingerprint"=>{let ledger=ctx.read(Path::new(arg(r,"path")?))?;json!(fingerprint(&ledger,&r["evidence"]))},
        "analyze"=>analyze(&r["rows"],&r["evidence"],&r["fingerprint"])?,"export_json"=>json!(export_json(&r["data"])?),"export_csv"=>json!(export_csv(&r["data"])?),"report"=>json!(render_report(&r["data"],r["audit"].as_bool().unwrap_or(false))?),
        "summaries"=>summary::summaries(&r["data"])?,"relationships"=>{let mut v=r["data"].clone();relationships(&mut v);v},
        "validate"=>{let(mut errors,mut warnings)=(strings(&r["errors"])?,strings(&r["warnings"])?);validation::validate(&r["data"],&mut errors,&mut warnings);json!([errors,warnings])},
        _=>bail!("unknown ledger analysis operation: {op}")
    })
}
