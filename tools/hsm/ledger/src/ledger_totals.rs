use crate::{analysis as a,ledger_money::Decimal,shared::*};
use anyhow::{Context as _,Result,bail};
use hsm_documents::Variables;
use serde::{Deserialize,de::{Visitor,MapAccess,SeqAccess,Error as _}};
use serde_json::{Value,json};
use std::{collections::BTreeMap,fmt as stdfmt,path::{Path,PathBuf}};

const STATUS:[&str;12]=["LIKELY-TO-BUY","NOT NEEDED","alt option","ON-ORDER","ACQUIRED","MISSING","PARTIAL","CANCELLED","RETURNED","REPLACEMENT","REPLACED","UNRESOLVED"];
type Totals=BTreeMap<String,Decimal>;
type Parsed=(Totals,Totals,Decimal,Vec<Value>,Vec<Value>);
pub fn first_price(cell:&str)->Result<Option<Decimal>>{
    re(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)").captures(cell).map(|c|Decimal::parse(&c[1].replace(',',""))).transpose()
}
fn lead_int(cell:&Value)->Option<i64>{re(r"^\s*([0-9]+)").captures(&a::plain_text(cell)).and_then(|c|c[1].parse().ok())}
fn sum(t:&mut Totals,key:&str,cost:&Decimal){let held=t.entry(key.to_owned()).or_insert_with(Decimal::zero);*held=held.add(cost);}
fn totals_json(t:&Totals)->Value{json!(t.iter().map(|(k,v)|(k.clone(),v.text())).collect::<BTreeMap<_,_>>())}
fn totals_from(v:&Value)->Result<Totals>{v.as_object().context("money totals")?.iter().map(|(k,v)|Ok((k.clone(),Decimal::value(v)?))).collect()}
fn parse_text(text:&str)->Result<Parsed>{
    let(mut status_totals,mut sections,mut labor,mut ambiguous,mut rows)=(Totals::new(),Totals::new(),Decimal::zero(),vec![],vec![]);
    let mut section="(preamble)".to_owned();let mut colmap=BTreeMap::<String,usize>::new();
    for(index,line)in text.lines().enumerate(){
        if let Some(s)=line.strip_prefix("## "){section=s.trim().to_owned();colmap.clear();continue}
        if !line.starts_with('|')||section=="Totals"{continue}
        let columns=cells(line);if columns.len()<2||separator(&columns){continue}
        let clean=columns.iter().map(|s|a::plain_text(&json!(s))).collect::<Vec<_>>();
        if clean.iter().any(|s|s=="$")&&["Status","Type","Item","Contents","Part"].iter().any(|n|clean.iter().any(|s|s==n)){
            colmap=clean.iter().enumerate().map(|(i,s)|(s.clone(),i)).collect();continue
        }
        if colmap.is_empty()||re(r"(?i)^(?:§\d+\s+)?subtotal\b").is_match(&clean[0]){continue}
        let col=|names:&[&str]|names.iter().find_map(|name|colmap.get(*name).and_then(|i|clean.get(*i)).filter(|s|!s.is_empty()&&*s!="—")).cloned().unwrap_or_default();
        let labor_row=section.starts_with("18.");let mut status_text=col(&["Status"]);
        let mut status=STATUS.iter().find(|key|{
            let pattern=format!(r"(?:^|[^\w-]){}(?:$|[^\w-])",regex::escape(key));re(&pattern).is_match(&status_text)
        }).map(|s|s.to_string());
        if status.is_none()&&labor_row&&colmap.contains_key("Type"){status=Some("ACQUIRED".into());status_text="ACQUIRED".into();}
        let Some(status)=status else{continue};let price_text=col(&["$"]);let price=first_price(&price_text)?;let mut cost=price.clone();
        let qty_text=col(&["Qty","Quantity","# of receipts"]);let quantity=lead_int(&json!(qty_text));let unit=re(r"(?:\s|^)ea\.?\s*$").is_match(&price_text);
        let desc=clean.join(" | ");
        if price.is_none(){ambiguous.push(json!([status,"unknown-price",text_prefix(&desc,88)]));}
        else if unit{
            if let Some(q)=quantity{let p=price.as_ref().unwrap();let value=p.mul(q);ambiguous.push(json!([status,format!("ea {q}×{}={}",p.text(),value.fixed(2,false,false)),text_prefix(&desc,60)]));cost=Some(value);}
            else{ambiguous.push(json!([status,format!("ea-no-qty ({})",price.as_ref().unwrap().text()),text_prefix(&desc,70)]));cost=None;}
        }
        if let Some(cost)=&cost{
            if labor_row{if ["ACQUIRED","ON-ORDER","MISSING","PARTIAL","RETURNED","REPLACED"].contains(&status.as_str()){labor=labor.add(cost);}}
            else{sum(&mut status_totals,&status,cost);if ["ACQUIRED","REPLACED","RETURNED","REPLACEMENT"].contains(&status.as_str()){sum(&mut sections,&section,cost);}}
        }
        let description=col(&["Part","Item","Contents","Type"]);let description=if description.is_empty(){clean[0].clone()}else{description};
        let id=re(r"<!--\s*purchase:([^\s<>]+)\s*-->").captures(&columns[0]).map(|c|c[1].to_owned());
        let order_cell=col(&["Order #"]);let orders=re(r"\b\d{3}-\d{7}-\d{7}\b").find_iter(&order_cell).map(|m|m.as_str().to_owned()).collect::<Vec<_>>();
        let basis=if colmap.contains_key("Date range"){"coverage_period"}else if colmap.contains_key("Invoice date"){"invoice_date"}else if colmap.contains_key("Receipt date"){"receipt_date"}else{"order_date"};
        let currency=col(&["Currency"]);
        rows.push(json!({"purchase_id":id,"line":index+1,"section":section,"status":status,"status_text":status_text,"cost":cost.map(|v|v.text()),"orders":orders,
            "ordered":col(&["Ordered","Order date","Date range"]),"invoice_date":col(&["Invoice date"]),"receipt_date":col(&["Receipt date"]),"row_date_basis":basis,
            "delivered":col(&["Delivered"]),"part":text_prefix(&description,64),"description":description,"quantity":quantity,"quantity_text":qty_text,"price_basis":if unit{"unit"}else{"row_total"},
            "unit_price":if unit{price.map(|v|v.text())}else{None},"currency":if currency.is_empty(){"USD"}else{&currency},"labor":labor_row}));
    }
    Ok((status_totals,sections,labor,ambiguous,rows))
}
fn parsed_json(p:&Parsed)->Value{json!([totals_json(&p.0),totals_json(&p.1),p.2.text(),p.3,p.4])}

/// Evidence objects reject repeated keys at every nesting level.
struct Unique(Value);
impl<'de> Deserialize<'de> for Unique{
    fn deserialize<D:serde::Deserializer<'de>>(d:D)->std::result::Result<Self,D::Error>{
        struct V;
        impl<'de> Visitor<'de> for V{
            type Value=Unique;
            fn expecting(&self,f:&mut stdfmt::Formatter)->stdfmt::Result{f.write_str("a JSON value")}
            fn visit_bool<E:serde::de::Error>(self,v:bool)->std::result::Result<Unique,E>{Ok(Unique(json!(v)))}
            fn visit_i64<E:serde::de::Error>(self,v:i64)->std::result::Result<Unique,E>{Ok(Unique(json!(v)))}
            fn visit_u64<E:serde::de::Error>(self,v:u64)->std::result::Result<Unique,E>{Ok(Unique(json!(v)))}
            fn visit_f64<E:serde::de::Error>(self,v:f64)->std::result::Result<Unique,E>{Ok(Unique(json!(v)))}
            fn visit_str<E:serde::de::Error>(self,v:&str)->std::result::Result<Unique,E>{Ok(Unique(json!(v)))}
            fn visit_string<E:serde::de::Error>(self,v:String)->std::result::Result<Unique,E>{Ok(Unique(json!(v)))}
            fn visit_none<E:serde::de::Error>(self)->std::result::Result<Unique,E>{Ok(Unique(Value::Null))}
            fn visit_unit<E:serde::de::Error>(self)->std::result::Result<Unique,E>{Ok(Unique(Value::Null))}
            fn visit_seq<A:SeqAccess<'de>>(self,mut a:A)->std::result::Result<Unique,A::Error>{let mut out=vec![];while let Some(Unique(v))=a.next_element()?{out.push(v);}Ok(Unique(json!(out)))}
            fn visit_map<A:MapAccess<'de>>(self,mut a:A)->std::result::Result<Unique,A::Error>{let mut out=serde_json::Map::new();while let Some(key)=a.next_key::<String>()?{if out.contains_key(&key){return Err(A::Error::custom(format!("duplicate JSON key: {key}")))}let Unique(v)=a.next_value()?;out.insert(key,v);}Ok(Unique(json!(out)))}
        }d.deserialize_any(V)
    }
}
pub fn load_unique(ctx:&mut Context,path:&Path)->Result<Value>{Ok(serde_json::from_str::<Unique>(&ctx.read(path)?)?.0)}
fn days_since(date:&str,today:&str)->Option<i64>{Some(a::ordinal(today)?-a::ordinal(date)?)}
fn reconcile(rows:&Value,orders:&Value,tolerance:&Decimal)->Result<(Vec<Value>,Vec<Value>,Vec<String>)>{
    let mut groups=BTreeMap::<String,Vec<&Value>>::new();for row in a::array(rows){if ["ACQUIRED","ON-ORDER","MISSING","PARTIAL","RETURNED","REPLACED"].contains(&a::text(&row["status"])){for id in a::ids(&row["orders"]){groups.entry(id).or_default().push(row);}}}
    let(mut mismatch,mut unverified,mut split)=(vec![],vec![],vec![]);
    for(id,group)in groups{
        if group.iter().any(|row|a::ids(&row["orders"]).len()>1){split.push(id);continue}
        let invoice=&orders[&id];let mut allocated=Decimal::zero();for row in &group{if !row["cost"].is_null(){allocated=allocated.add(&Decimal::value(&row["cost"])?);}}
        if invoice.is_null()||invoice["total"].is_null()||group.iter().any(|r|r["cost"].is_null()){unverified.push(json!([id,allocated.text()]));continue}
        let nonproject=if a::truth(&invoice["nonproject_amount"]){Decimal::value(&invoice["nonproject_amount"])?}else{Decimal::zero()};
        let project=Decimal::value(&invoice["total"])?.sub(&nonproject);
        if allocated.sub(&project).abs().cmp(tolerance).is_gt(){mismatch.push(json!([id,allocated.text(),project.text(),group.len()]));}
    }Ok((mismatch,unverified,split))
}
fn aged(rows:&Value,today:&str)->(Vec<Value>,Vec<Value>){
    let(mut aged,mut undated)=(vec![],vec![]);for row in a::array(rows){if a::text(&row["status"])!="ON-ORDER"{continue}
        if let Some(age)=days_since(a::text(&row["ordered"]),today){if age>=45{aged.push(json!([age,row]));}}else{undated.push(row.clone());}
    }aged.sort_by(|x,y|a::integer(&y[0]).cmp(&a::integer(&x[0])).then_with(||{
        let id=|v:&Value|v[1]["purchase_id"].as_str().filter(|s|!s.is_empty()).unwrap_or(a::text(&v[1]["part"])).to_owned();id(x).cmp(&id(y))
    }));(aged,undated)
}
fn unrecorded(rows:&Value,orders:&Value)->Vec<Value>{let named=a::array(rows).iter().flat_map(|r|a::ids(&r["orders"])).collect::<std::collections::BTreeSet<_>>();orders.as_object().into_iter().flatten().filter(|(key,v)|v["project"]!=json!(false)&&!named.contains(*key)).map(|(k,v)|json!([k,v])).collect()}
fn variables(statuses:&Totals,sections:&Totals,labor:&Decimal,analysis:&Value)->Result<Variables>{
    let get=|name|statuses.get(name).cloned().unwrap_or_else(Decimal::zero);
    let acquired=get("ACQUIRED").add(&get("REPLACED")).add(&get("RETURNED")).add(&get("REPLACEMENT"));let onorder=get("ON-ORDER").add(&get("PARTIAL")).add(&get("UNRESOLVED"));let missing=get("MISSING");
    let mut out=Variables::from([("LEDGER_ACQUIRED_HW".into(),acquired.money()),("LEDGER_LABOR".into(),labor.money()),("LEDGER_ACQUIRED_COMBINED".into(),acquired.add(labor).money()),("LEDGER_ON_ORDER".into(),onorder.money()),("LEDGER_MISSING".into(),missing.money()),("LEDGER_GRAND_TOTAL".into(),acquired.add(labor).add(&onorder).add(&missing).money())]);
    for(title,cost)in sections{if let Some(m)=re(r"^(\d+)").captures(title){out.insert(format!("LEDGER_SEC{}",&m[1]),cost.money());}}
    for(view,pairs)in [("procurement",vec![("LEDGER_FINAL_VENDOR","final_vendor_amount_minor"),("LEDGER_ESTIMATES","estimate_minor"),("LEDGER_LEGACY_UNVERIFIED","legacy_unverified_minor")]),("merchant_payments",vec![("LEDGER_MERCHANT_CHARGES","charges_minor"),("LEDGER_MERCHANT_REFUNDS","refunds_minor"),("LEDGER_MERCHANT_NET","net_minor")])]{
        if let Some(row)=a::array(&analysis["summary"][view]["totals"]).iter().find(|v|a::text(&v["currency"])=="USD"){for(marker,field)in pairs{out.insert(marker.into(),a::format_minor(&row[field],"USD",&json!({"USD":2}))?);}}
    }Ok(out)
}
fn stale_markers(text:&str,variables:&Variables)->Vec<String>{crate::shared::stale(text,variables).into_iter().map(|s|s.trim_start().to_owned()).collect()}
fn generated(path:&Path)->[PathBuf;2]{[path.with_extension("export.json"),path.with_extension("export.csv")]}

fn main(r:&Value,ctx:&mut Context)->Result<Value>{
    let ledger=ctx.path(r,"ledger","hardware/ledger/purchases.md");let source=ctx.read(&ledger)?;let(totals,sections,labor,ambiguous,rows)=parse_text(&source)?;
    let evidence=load_unique(ctx,&ctx.path(r,"evidence","hardware/ledger/purchases.evidence.json"))?;
    let mut analysis=a::analyze(&json!(rows),&evidence,&json!(a::fingerprint(&source,&evidence)))?;
    let orders=ctx.json(ctx.path(r,"orders","hardware/ledger/purchases.orders.json"))?["orders"].clone();let rows=json!(rows);let tolerance=Decimal::parse("0.01")?;
    let(mismatch,unverified,split)=reconcile(&rows,&orders,&tolerance)?;let exact=reconcile(&rows,&orders,&Decimal::zero())?.0;
    let mut extra_warnings=vec![];
    for row in exact{let allocated=Decimal::value(&row[1])?;let project=Decimal::value(&row[2])?;if allocated.sub(&project).abs().cmp(&tolerance).is_le(){extra_warnings.push(format!("Legacy order {}: row valuation USD {}, preserved project invoice USD {}; historical allocation residual USD {}. Original prices retained; no balancing payment invented.",a::text(&row[0]),allocated.fixed(2,true,false),project.fixed(2,true,false),project.sub(&allocated).fixed(2,false,true)));}}
    let(aged,undated)=if a::ordinal(a::text(&evidence["as_of"])).is_some(){aged(&rows,a::text(&evidence["as_of"]))}else{(vec![],vec![])};
    for row in mismatch{let allocated=Decimal::value(&row[1])?;let project=Decimal::value(&row[2])?;analysis["validation"]["errors"].as_array_mut().unwrap().push(json!(format!("Order {}: {} project rows allocate USD {}; preserved project invoice amount USD {}",a::text(&row[0]),a::integer(&row[3]),allocated.fixed(2,true,false),project.fixed(2,true,false))));}
    if !unverified.is_empty(){extra_warnings.push(format!("{} legacy named order(s) lack an exact invoice allocation check",unverified.len()));}
    if !split.is_empty(){extra_warnings.push(format!("{} legacy order(s) belong to rows covering multiple orders",split.len()));}
    if !aged.is_empty(){extra_warnings.push(format!("{} ON-ORDER purchase(s) older than 45 days require fulfillment evidence",aged.len()));}
    if !undated.is_empty(){extra_warnings.push(format!("{} ON-ORDER purchase(s) have unknown order dates",undated.len()));}
    let missing=unrecorded(&rows,&orders);if !missing.is_empty(){extra_warnings.push(format!("{} preserved potentially project order(s) have no named Markdown row",missing.len()));}
    analysis["validation"]["warnings"].as_array_mut().unwrap().extend(extra_warnings.into_iter().map(Value::String));
    let vars=variables(&totals,&sections,&labor,&analysis)?;let has_errors=!a::array(&analysis["validation"]["errors"]).is_empty();let mode=r["mode"].as_str().unwrap_or("write");
    if mode=="export-json"{return Ok(main_result(i32::from(has_errors),a::export_json(&analysis)?))}
    if mode=="export-csv"{return Ok(main_result(i32::from(has_errors),a::export_csv(&analysis)?))}
    if mode=="check"{
        let mut errors=a::array(&analysis["validation"]["errors"]).iter().map(|v|a::text(v).to_owned()).collect::<Vec<_>>();errors.extend(stale_markers(&source,&vars));let sidecar=ledger.with_extension("figures.json");
        if sidecar.exists(){match ctx.json(&sidecar){
            Ok(figures)=>{let expected=vars.iter().filter(|(key,_)|source.contains(&format!("]({key})"))).map(|(k,v)|(k.clone(),json!(v))).collect::<serde_json::Map<_,_>>();if figures.get(PURCHASES_PROGRAM).cloned().unwrap_or(json!({}))!=json!(expected){errors.push("purchases.figures.json is stale; run --write".into());}},
            Err(_)=>errors.push("purchases.figures.json is invalid".into())
        }}
        for(path,content)in generated(&ledger).into_iter().zip([a::export_json(&analysis)?,a::export_csv(&analysis)?]){if !path.exists()||ctx.read(&path)?!=content{errors.push(format!("{} is missing or stale; run --write",path.file_name().unwrap().to_string_lossy()));}}
        let mut out=errors.iter().map(|s|format!("ERROR: {s}\n")).collect::<String>();for warning in a::array(&analysis["validation"]["warnings"]){out+=&format!("WARNING: {}\n",a::text(warning));}
        out+=&format!("Project ledger integrity {}; historical evidence coverage is reported separately.\n",if errors.is_empty(){"✓"}else{"FAILED"});return Ok(main_result(i32::from(!errors.is_empty()),out))
    }
    if mode=="report"||mode=="audit"{
        let mut out=a::render_report(&analysis,mode=="audit")?;
        if mode=="audit"{out+="Legacy unit-price and unknown-price rows:\n";for row in ambiguous{out+=&format!("  [{}] {} | {}\n",a::text(&row[0]),a::text(&row[1]),a::text(&row[2]));}for row in aged{out+=&format!("  Fulfillment evidence gap: {} ON-ORDER {} days (ordered {})\n",a::text(&row[1]["purchase_id"]),a::integer(&row[0]),a::text(&row[1]["ordered"]));}}
        return Ok(main_result(i32::from(has_errors),out))
    }
    if has_errors{return Ok(main_result(1,a::render_report(&analysis,false)?))}
    ctx.substitute(&ledger,&vars,PURCHASES_PROGRAM)?;analysis["input_fingerprint"]=json!(a::fingerprint(&ctx.read(&ledger)?,&evidence));
    for(path,content)in generated(&ledger).into_iter().zip([a::export_json(&analysis)?,a::export_csv(&analysis)?]){ctx.write(&path,content.as_bytes())?;}
    Ok(main_result(0,a::render_report(&analysis,false)?))
}

pub fn dispatch(op:&str,r:&Value,ctx:&mut Context)->Result<Value>{
    Ok(match op{
        "first_price"=>json!(first_price(arg(r,"cell")?)?.map(|v|v.text())),"lead_int"=>json!(lead_int(&r["cell"])),
        "parse"=>{let source=if let Some(s)=r["text"].as_str(){s.to_owned()}else{ctx.read(Path::new(arg(r,"path")?))?};parsed_json(&parse_text(&source)?)},
        "load_orders"=>ctx.json(Path::new(arg(r,"path")?))?["orders"].clone(),"load_evidence"=>load_unique(ctx,Path::new(arg(r,"path")?))?,
        "days_since"=>json!(days_since(r["date"].as_str().unwrap_or(""),arg(r,"today")?)),"reconcile"=>json!(reconcile(&r["rows"],&r["orders"],&Decimal::value(r.get("tolerance").unwrap_or(&json!("0.01")))?)?),
        "aged"=>json!(aged(&r["rows"],arg(r,"today")?)),"unrecorded"=>json!(unrecorded(&r["rows"],&r["orders"])),
        "variables"=>json!(variables(&totals_from(&r["statuses"])?,&totals_from(&r["sections"])?,&Decimal::value(&r["labor"])?,&r["analysis"])?),
        "stale_markers"=>{let source=ctx.read(Path::new(arg(r,"path")?))?;let vars=r["variables"].as_object().context("variables")?.iter().map(|(k,v)|(k.clone(),a::text(v).to_owned())).collect();json!(stale_markers(&source,&vars))},
        "generated_paths"=>json!(generated(Path::new(arg(r,"path")?)).into_iter().map(|p|p.to_string_lossy().into_owned()).collect::<Vec<_>>()),
        "main"=>match main(r,ctx){Ok(v)=>v,Err(e)=>json!({"status":1,"output":"","stderr":format!("Ledger integrity error: {e}\n")})},
        _=>bail!("unknown ledger-total operation: {op}")
    })
}
