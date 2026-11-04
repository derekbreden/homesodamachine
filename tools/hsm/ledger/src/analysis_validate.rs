use super::*;

fn valid_date(value:&Value,context:&str,errors:&mut Vec<String>){
    if value.is_null(){return}
    let keys=match text(&value["precision"]){"day"|"month"=>vec!["precision","value"],"range"=>vec!["precision","start","end"],_=>vec![]};
    let valid=!keys.is_empty()&&value.as_object().is_some_and(|v|v.len()==keys.len()&&keys.iter().all(|k|v.contains_key(*k)))
        &&date_bounds(value).ok().flatten().is_some_and(|(a,b)|a<=b);
    if !valid{errors.push(format!("{context}: invalid precision-preserving date"));}
}
fn valid_period(value:&Value,context:&str,optional:bool,errors:&mut Vec<String>){
    if optional&&value.is_null(){return}
    let valid=value.as_object().is_some_and(|v|v.len()==2&&v.contains_key("start")&&v.contains_key("end"))
        &&calendar_day(text(&value["start"])).is_some()&&calendar_day(text(&value["end"])).is_some()&&text(&value["start"])<=text(&value["end"]);
    if !valid{errors.push(format!("{context}: invalid calendar period"));}
}
fn valid_amount(record:&Value,context:&str,optional:bool,scales:&Value,errors:&mut Vec<String>){
    let amount=&record["amount_minor"];if amount.is_null()&&optional{return}
    if amount.as_i64().is_none_or(|n|n<0){errors.push(format!("{context}: amount_minor must be a nonnegative integer{}",if optional{" or null"}else{""}));}
    if scales.get(text(&record["currency"])).is_none(){errors.push(format!("{context}: undeclared currency"));}
}
fn index<'a>(records:&'a Value,key:&str,errors:&mut Vec<String>)->BTreeMap<String,&'a Value>{
    let mut result=BTreeMap::new();
    for record in array(records){
        let Some(id)=record[key].as_str().filter(|s|!s.is_empty()&&!s.chars().any(char::is_whitespace))else{errors.push(format!("{key}: missing or invalid stable identity"));continue};
        if result.insert(id.to_owned(),record).is_some(){errors.push(format!("duplicate {key}: {id}"));}
    }result
}
fn references(record:&Value,field:&str,targets:&BTreeMap<String,&Value>,context:&str,errors:&mut Vec<String>){
    let Some(values)=record.get(field)else{return};
    if !values.as_array().is_some_and(|a|a.iter().all(Value::is_string)){errors.push(format!("{context}: {field} must be an ID list"));return}
    for value in array(values){let id=text(value);if !targets.contains_key(id){errors.push(format!("{context}: missing {field} reference {id}"));}}
}
fn source_proves(sources:&BTreeMap<String,&Value>,ids:&Value,capability:&str)->bool{array(ids).iter().any(|id|sources.get(text(id)).is_some_and(|s|contains(&s["proves"],capability)))}
fn replacements(p:&Value)->Vec<String>{if p["replacement_for"].is_array(){ids(&p["replacement_for"])}else{p["replacement_for"].as_str().filter(|s|!s.is_empty()).map(|s|vec![s.to_owned()]).unwrap_or_default()}}

pub fn validate(data:&Value,errors:&mut Vec<String>,warnings:&mut Vec<String>){
    let scales=&data["currency_scales"];
    let purchases=index(&data["purchases"],"purchase_id",errors);let orders=index(&data["orders"],"order_id",errors);let sources=index(&data["sources"],"source_id",errors);let events=index(&data["events"],"event_id",errors);let allocations=index(&data["allocations"],"allocation_id",errors);
    index(&data["coverage"],"coverage_id",errors);index(&data["gaps"],"gap_id",errors);
    valid_period(&data["reporting_period"],"reporting_period",false,errors);valid_date(&json!({"precision":"day","value":data["as_of"]}),"as_of",errors);
    for(id,source)in &sources{
        if !truth(&source["vendor"])||!truth(&source["document_type"]){errors.push(format!("{id}: source needs vendor and document_type"));}
        if source.get("proves").is_some_and(|v|!v.is_array())||array(&source["proves"]).iter().any(|v|!allowed("PROVES",v)){errors.push(format!("{id}: unsupported evidence capability"));}
        for name in ["document_date","receipt_date","service_period","merchant_event_date","notification_date"]{valid_date(&source[name],&format!("{id} {name}"),errors);}
        valid_date(&json!({"precision":"day","value":source["verified_at"]}),&format!("{id} verified_at"),errors);
    }
    for(id,order)in &orders{
        if !id.contains(':'){errors.push(format!("{id}: order_id must be vendor-namespaced"));}
        if !truth(&order["vendor"]){errors.push(format!("{id}: vendor missing"));}
        if !allowed("ALLOCATION_STATUS",&order["allocation_status"]){errors.push(format!("{id}: invalid allocation_status"));}
        references(order,"source_ids",&sources,id,errors);valid_date(&order["order_date"],&format!("{id} order_date"),errors);
        for name in ["replaces","replaced_by"]{let other=&order[name];if truth(other)&&(!orders.contains_key(text(other))||text(other)==id){errors.push(format!("{id}: invalid {name}"));}}
    }
    for(id,purchase)in &purchases{
        valid_amount(purchase,id,true,scales,errors);
        for(name,allowed_name)in [("amount_evidence","AMOUNT_EVIDENCE"),("purpose","PURPOSES"),("allocation_status","ALLOCATION_STATUS")]{if !allowed(allowed_name,&purchase[name]){errors.push(format!("{id}: invalid {name}"));}}
        if !purchase["contributes"].is_boolean(){errors.push(format!("{id}: contributes must be boolean"));}
        references(purchase,"order_ids",&orders,id,errors);references(purchase,"source_ids",&sources,id,errors);
        if !["order_date","invoice_date","receipt_date","coverage_period"].contains(&text(&purchase["row_date_basis"])){errors.push(format!("{id}: invalid row_date_basis"));}
        for name in ["row_date","order_date","delivery_date","invoice_date","receipt_date","service_period"]{valid_date(&purchase[name],&format!("{id} {name}"),errors);}
        for date in array(&purchase["delivery_dates"]){valid_date(date,&format!("{id} delivery_dates"),errors);}
        if replacements(purchase).iter().any(|other|other==id||!purchases.contains_key(other)){errors.push(format!("{id}: invalid replacement_for"));}
        if text(&purchase["amount_evidence"])=="final_vendor_amount"&&!source_proves(&sources,&purchase["source_ids"],"price"){errors.push(format!("{id}: final vendor amount lacks price evidence"));}
        for item in array(&purchase["price_history"]){
            valid_amount(item,&format!("{id} price_history"),false,scales,errors);
            if !allowed("AMOUNT_EVIDENCE",&item["amount_evidence"]){errors.push(format!("{id}: price_history invalid amount_evidence"));}
            references(item,"source_ids",&sources,&format!("{id} price_history"),errors);
            valid_date(&json!({"precision":"day","value":item["verified_at"]}),&format!("{id} price_history verified_at"),errors);
        }
    }
    for(id,event)in &events{
        valid_amount(event,id,true,scales,errors);
        if !allowed("EVENT_TYPES",&event["event_type"]){errors.push(format!("{id}: invalid event_type"));}
        if !["confirmed","expected"].contains(&text(&event["confirmation"])){errors.push(format!("{id}: invalid confirmation"));}
        if !allowed("ALLOCATION_STATUS",&event["allocation_status"]){errors.push(format!("{id}: invalid allocation_status"));}
        references(event,"source_ids",&sources,id,errors);references(event,"order_ids",&orders,id,errors);
        for name in ["event_date","receipt_date","invoice_date","service_period"]{valid_date(&event[name],&format!("{id} {name}"),errors);}
        valid_date(&json!({"precision":"day","value":event["verified_at"]}),&format!("{id} verified_at"),errors);
        if text(&event["confirmation"])=="confirmed"{
            if !source_proves(&sources,&event["source_ids"],text(&event["event_type"])){errors.push(format!("{id}: confirmed event lacks matching source capability"));}
            if !event["event_date"].is_null()&&!array(&event["source_ids"]).iter().any(|id|sources.get(text(id)).is_some_and(|source|contains(&source["proves"],"merchant_event_date")&&source["merchant_event_date"]==event["event_date"])){
                errors.push(format!("{id}: merchant event date lacks matching date evidence"));
            }
        }
        let original=&event["original_event_id"];
        if truth(original){
            if text(original)==id||!events.contains_key(text(original)){errors.push(format!("{id}: invalid original_event_id"));}
            else if text(&event["event_type"])=="refund"{
                let original=events[text(original)];if text(&original["event_type"])!="charge"||original["currency"]!=event["currency"]{errors.push(format!("{id}: refund original must be a same-currency charge"));}
            }
        }
    }
    let mut allocated=BTreeMap::<String,i64>::new();let mut signatures=BTreeSet::new();
    for(id,allocation)in &allocations{
        valid_amount(allocation,id,false,scales,errors);
        let event=events.get(text(&allocation["event_id"]));let purchase=purchases.get(text(&allocation["purchase_id"]));let order=&allocation["order_id"];
        if event.is_none()||(!allocation["purchase_id"].is_null()&&purchase.is_none())||(purchase.is_none()&&!truth(order)){
            errors.push(format!("{id}: allocation needs existing event and purchase or order"));continue
        }
        let event=*event.unwrap();
        if event["currency"]!=allocation["currency"]||purchase.is_some_and(|p|p["currency"]!=allocation["currency"]){errors.push(format!("{id}: allocation currencies disagree"));}
        if truth(order)&&(!orders.contains_key(text(order))||purchase.is_some_and(|p|!contains(&p["order_ids"],text(order)))){errors.push(format!("{id}: order must exist and belong to purchase"));}
        if truth(order)&&truth(&event["order_ids"])&&!contains(&event["order_ids"],text(order)){errors.push(format!("{id}: order conflicts with evidenced event order relationship"));}
        let signature=(allocation["event_id"].to_string(),allocation["purchase_id"].to_string(),order.to_string());
        if !signatures.insert(signature){errors.push(format!("{id}: duplicate event/purchase/order allocation"));}
        if let Some(amount)=allocation["amount_minor"].as_i64(){*allocated.entry(text(&allocation["event_id"]).to_owned()).or_insert(0)+=amount;}
    }
    for(id,event)in &events{if let Some(amount)=event["amount_minor"].as_i64(){let total=allocated.get(id).copied().unwrap_or(0);
        if ["all_project","mixed_partial"].contains(&text(&event["allocation_status"])){if total!=amount{errors.push(format!("{id}: allocations {total} do not equal published project amount {amount}"));}}
        else if total>amount{errors.push(format!("{id}: unresolved allocations exceed published event amount"));}
    }}
    let mut seen_documents=BTreeMap::new();let mut seen_references=BTreeMap::new();
    for(id,event)in &events{
        let signature=json!([event["vendor"],event["event_type"],event["event_date"],event["currency"],event["amount_minor"]]);
        let reference=&event["reference"];
        if truth(reference){let key=json!([event["vendor"],event["event_type"],reference]).to_string();if let Some(prior)=seen_references.insert(key,id){errors.push(format!("{id}: duplicate merchant event reference with {prior}"));}}
        for source_id in array(&event["source_ids"]){let empty=Value::Null;let source=sources.get(text(source_id)).copied().unwrap_or(&empty);if !contains(&source["proves"],text(&event["event_type"])){continue}
            let key=json!([signature,source["vendor"],source["document_type"],source.get("reference").unwrap_or(source_id)]).to_string();
            if let Some(prior)=seen_documents.insert(key,id){if prior!=id{errors.push(format!("{id}: duplicate payment document with {prior}"));}}
        }
    }
    for record in array(&data["coverage"]){let context=record["coverage_id"].as_str().unwrap_or("coverage");
        references(record,"source_ids",&sources,context,errors);references(record,"order_ids",&orders,context,errors);
        if !["partial","unknown","complete"].contains(&text(&record["coverage"])){errors.push(format!("{context}: invalid coverage classification"));}
        for name in ["examined_period","complete_period"]{valid_period(&record[name],&format!("{context} {name}"),true,errors);}
        valid_date(&json!({"precision":"day","value":record["checked_at"]}),&format!("{context} checked_at"),errors);
        if text(&record["coverage"])=="complete"&&!truth(&record["complete_period"]){errors.push(format!("{context}: complete coverage requires a stated complete_period"));}
        if text(&record["coverage"])!="complete"||!truth(&record["complete_period"]){warnings.push(format!("{context}: evidence coverage is {}",record["coverage"].as_str().unwrap_or("unknown")));}
    }
    for gap in array(&data["gaps"]){let context=gap["gap_id"].as_str().unwrap_or("gap");
        for(field,targets)in [("purchase_ids",&purchases),("order_ids",&orders),("event_ids",&events),("source_ids",&sources)]{references(gap,field,targets,context,errors);}
        if !truth(&gap["missing_fact"]){errors.push(format!("{context}: missing_fact is required"));}
    }
    if !array(&data["gaps"]).is_empty(){warnings.push(format!("{} authored evidence gap(s) remain",array(&data["gaps"]).len()));}
    fn visit(id:&str,purchases:&BTreeMap<String,&Value>,active:&mut BTreeSet<String>,complete:&mut BTreeSet<String>,errors:&mut Vec<String>){
        if active.contains(id){errors.push(format!("{id}: replacement relationship cycle"));return}
        if complete.contains(id){return}active.insert(id.to_owned());
        for original in replacements(purchases[id]){if purchases.contains_key(&original){visit(&original,purchases,active,complete,errors);}}
        active.remove(id);complete.insert(id.to_owned());
    }
    let mut complete=BTreeSet::new();for id in purchases.keys(){visit(id,&purchases,&mut BTreeSet::new(),&mut complete,errors);}
}
