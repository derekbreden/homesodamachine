use super::*;
const PROCUREMENT:[&str;4]=["final_vendor_amount_minor","estimate_minor","legacy_unverified_minor","total_minor"];
const PAYMENT:[&str;6]=["charges_minor","refunds_minor","net_minor","authorizations_minor","noncash_credits_minor","unresolved_project_share_minor"];
type Monthly=BTreeMap<(String,String),Value>;
type Currency=BTreeMap<String,Value>;
fn blank(currency:&str,fields:&[&str],ids:Option<&str>,month:Option<&str>)->Value{
    let mut v=json!({"currency":currency});for field in fields{v[*field]=json!(0);}
    if let Some(ids)=ids{v[ids]=json!([]);v["unknown_amount_ids"]=json!([]);}
    if let Some(month)=month{v["month"]=json!(month);v["evidence_scope"]=json!("retrieved_records_only");}v
}
fn months(period:&Value)->Result<Vec<String>>{
    let(mut y,mut m,_)=calendar_day(text(&period["start"])).context("invalid period")?;
    let(yend,mend,_)=calendar_day(text(&period["end"])).context("invalid period")?;let mut result=vec![];
    while(y,m)<=(yend,mend){result.push(format!("{y:04}-{m:02}"));if m==12{y+=1;m=1}else{m+=1}}
    Ok(result)
}
fn view(currencies:&[String],months:&[String],fields:&[&str],id:&str)->(Monthly,Currency,Currency){
    let(mut monthly,mut undated,mut totals)=(BTreeMap::new(),BTreeMap::new(),BTreeMap::new());
    for currency in currencies{totals.insert(currency.clone(),blank(currency,fields,None,None));undated.insert(currency.clone(),blank(currency,fields,Some(id),None));
        for month in months{monthly.insert((month.clone(),currency.clone()),blank(currency,fields,Some(id),Some(month)));}
    }(monthly,undated,totals)
}
fn bucket<'a>(monthly:&'a mut Monthly,undated:&'a mut Currency,date:&Value,currency:&str,fields:&[&str],id:&str)->Result<&'a mut Value>{
    let month=date_month(date)?;
    Ok(if month=="undated_unallocated"{undated.get_mut(currency).context("unknown currency")?}
        else{monthly.entry((month.clone(),currency.into())).or_insert_with(||blank(currency,fields,Some(id),Some(&month)))})
}
fn add(v:&mut Value,key:&str,n:i64){v[key]=json!(integer(&v[key])+n)}
fn push(v:&mut Value,key:&str,id:&Value){v[key].as_array_mut().unwrap().push(id.clone());}
fn sorted<T:IntoIterator<Item=String>>(v:T)->Value{let mut v=v.into_iter().collect::<Vec<_>>();v.sort();json!(v)}
fn sum_where(group:&[&Value],predicate:impl Fn(&Value)->bool)->i64{group.iter().filter(|v|predicate(v)).filter_map(|v|v["amount_minor"].as_i64()).sum()}

pub fn summaries(data:&Value)->Result<Value>{
    let currencies=data["currency_scales"].as_object().context("currency scales")?.keys().cloned().collect::<Vec<_>>();let months=months(&data["reporting_period"])?;
    let(mut pm,mut pu,mut pt)=view(&currencies,&months,&PROCUREMENT,"purchase_ids");let(mut em,mut eu,mut et)=view(&currencies,&months,&PAYMENT,"event_ids");
    let(mut active,mut excluded,mut cancelled)=(vec![],vec![],vec![]);let mut purposes=BTreeMap::<(String,String),i64>::new();
    for p in array(&data["purchases"]){let id=text(&p["purchase_id"]);
        if !truth(&p["contributes"]){excluded.push(id.to_owned());continue}
        if text(&p["fulfillment"])=="CANCELLED"{cancelled.push(id.to_owned());continue}
        if !allowed("ACTIVE_STATUSES",&p["fulfillment"]){excluded.push(id.to_owned());continue}
        active.push(p);let currency=text(&p["currency"]);let target=bucket(&mut pm,&mut pu,&p["order_date"],currency,&PROCUREMENT,"purchase_ids")?;
        push(target,"purchase_ids",&p["purchase_id"]);
        let Some(amount)=p["amount_minor"].as_i64()else{push(target,"unknown_amount_ids",&p["purchase_id"]);continue};
        let field=format!("{}_minor",text(&p["amount_evidence"]));add(target,&field,amount);add(target,"total_minor",amount);
        add(pt.get_mut(currency).unwrap(),&field,amount);add(pt.get_mut(currency).unwrap(),"total_minor",amount);*purposes.entry((currency.into(),text(&p["purpose"]).into())).or_insert(0)+=amount;
    }
    let mut expected=vec![];
    for e in array(&data["events"]){let currency=text(&e["currency"]);let target=bucket(&mut em,&mut eu,&e["event_date"],currency,&PAYMENT,"event_ids")?;
        push(target,"event_ids",&e["event_id"]);
        if text(&e["confirmation"])!="confirmed"{expected.push(text(&e["event_id"]).to_owned());continue}
        let Some(amount)=e["amount_minor"].as_i64()else{push(target,"unknown_amount_ids",&e["event_id"]);continue};
        if text(&e["allocation_status"])=="unresolved"{add(target,"unresolved_project_share_minor",amount);add(et.get_mut(currency).unwrap(),"unresolved_project_share_minor",amount);continue}
        let field=match text(&e["event_type"]){"charge"=>"charges_minor","refund"=>"refunds_minor","authorization"=>"authorizations_minor","noncash_credit"=>"noncash_credits_minor",_=>bail!("unknown event type")};
        add(target,field,amount);add(et.get_mut(currency).unwrap(),field,amount);
        if ["charge","refund"].contains(&text(&e["event_type"])){let signed=if text(&e["event_type"])=="charge"{amount}else{-amount};add(target,"net_minor",signed);add(et.get_mut(currency).unwrap(),"net_minor",signed);}
    }
    for v in pm.values_mut().chain(pu.values_mut()){for key in ["purchase_ids","unknown_amount_ids"]{v[key].as_array_mut().unwrap().sort_by(|a,b|text(a).cmp(text(b)));}}
    for v in em.values_mut().chain(eu.values_mut()){for key in ["event_ids","unknown_amount_ids"]{v[key].as_array_mut().unwrap().sort_by(|a,b|text(a).cmp(text(b)));}}
    let mut statuses=BTreeMap::new();
    for p in array(&data["purchases"]){if !truth(&p["contributes"]){continue}
        let key=(text(&p["currency"]).to_owned(),text(&p["fulfillment"]).to_owned());
        let target=statuses.entry(key).or_insert_with(||json!({"amount_minor":0,"unknown_amount_ids":[],"purchase_ids":[]}));push(target,"purchase_ids",&p["purchase_id"]);
        if let Some(amount)=p["amount_minor"].as_i64(){add(target,"amount_minor",amount)}else{push(target,"unknown_amount_ids",&p["purchase_id"]);}
    }
    let mut uncertainties=vec![];
    for currency in &currencies{
        let purchases=active.iter().copied().filter(|p|text(&p["currency"])==currency).collect::<Vec<_>>();let events=array(&data["events"]).iter().filter(|e|text(&e["currency"])==currency).collect::<Vec<_>>();
        let unknown_payment=|p:&Value|["unknown","merchant_refund_only"].contains(&text(&p["payment_evidence"]));
        uncertainties.push(json!({"currency":currency,
            "estimated_purchase_minor":sum_where(&purchases,|p|text(&p["amount_evidence"])=="estimate"),
            "legacy_unverified_purchase_minor":sum_where(&purchases,|p|text(&p["amount_evidence"])=="legacy_unverified"),
            "undated_unallocated_purchase_minor":sum_where(&purchases,|p|date_month(&p["order_date"]).ok().as_deref()==Some("undated_unallocated")),
            "purchases_without_merchant_charge_minor":sum_where(&purchases,unknown_payment),
            "partial_charge_purchase_minor":sum_where(&purchases,|p|text(&p["payment_evidence"]).starts_with("merchant_charge_partial")),
            "unresolved_allocation_purchase_minor":sum_where(&purchases,|p|text(&p["allocation_status"])=="unresolved"),
            "unknown_amount_purchase_count":purchases.iter().filter(|p|p["amount_minor"].is_null()).count(),
            "unknown_amount_event_count":events.iter().filter(|e|e["amount_minor"].is_null()).count(),
            "undated_charge_minor":eu[currency]["charges_minor"],"undated_refund_minor":eu[currency]["refunds_minor"],"unresolved_event_minor":et[currency]["unresolved_project_share_minor"],
            "order_only_charge_allocation_minor":events.iter().filter(|e|text(&e["event_type"])=="charge"&&text(&e["confirmation"])=="confirmed").map(|e|integer(&e["unallocated_to_purchase_minor"])).sum::<i64>()
        }));
    }
    let purchase_ids=|predicate:&dyn Fn(&Value)->bool|sorted(active.iter().filter(|p|predicate(p)).map(|p|text(&p["purchase_id"]).to_owned()));
    let event_ids=|predicate:&dyn Fn(&Value)->bool|sorted(array(&data["events"]).iter().filter(|e|predicate(e)).map(|e|text(&e["event_id"]).to_owned()));
    Ok(json!({
        "procurement":{
            "basis":"Current project purchase amount by order calendar month; cancellations and noncontributing summaries excluded; returns retain original acquisition amount; refunds are separate events.",
            "monthly":pm.into_values().collect::<Vec<_>>(),"undated_unallocated":pu.into_values().collect::<Vec<_>>(),"totals":pt.into_values().collect::<Vec<_>>(),
            "cancelled_purchase_ids":sorted(cancelled),"excluded_purchase_ids":sorted(excluded),
            "purpose_totals":purposes.into_iter().map(|((currency,purpose),amount)|json!({"currency":currency,"purpose":purpose,"amount_minor":amount})).collect::<Vec<_>>()
        },
        "merchant_payments":{
            "basis":"Confirmed merchant-evidenced project charges and issued monetary refunds by merchant event calendar month; bank posting is outside this ledger. Expected events, authorizations, noncash credits and unresolved project shares are excluded from charges/refunds/net.",
            "monthly":em.into_values().collect::<Vec<_>>(),"undated_unallocated":eu.into_values().collect::<Vec<_>>(),"totals":et.into_values().collect::<Vec<_>>(),"expected_event_ids":sorted(expected)
        },
        "fulfillment":{
            "basis":"Current procurement status, independently of payment evidence.",
            "outstanding_purchase_ids":purchase_ids(&|p|allowed("OUTSTANDING_STATUSES",&p["fulfillment"])),
            "returned_without_evidenced_refund_purchase_ids":sorted(array(&data["purchases"]).iter().filter(|p|text(&p["fulfillment"])=="RETURNED"&&truth(&p["contributes"])&&integer(&p["merchant_refund_allocated_minor"])==0).map(|p|text(&p["purchase_id"]).to_owned())),
            "cancelled_with_evidenced_charge_purchase_ids":sorted(array(&data["purchases"]).iter().filter(|p|text(&p["fulfillment"])=="CANCELLED"&&truth(&p["contributes"])&&integer(&p["merchant_charge_allocated_minor"])>0).map(|p|text(&p["purchase_id"]).to_owned())),
            "expected_refund_event_ids":event_ids(&|e|text(&e["event_type"])=="refund"&&text(&e["confirmation"])=="expected"),
            "by_status":statuses.into_iter().map(|((currency,status),mut row)|{row["currency"]=json!(currency);row["fulfillment"]=json!(status);row}).collect::<Vec<_>>()
        },
        "uncertainty":{
            "basis":"Zero numeric activity means no retrieved records contributed; it does not establish complete source coverage or zero actual spending. Uncertainty categories overlap; purchase amounts without charge evidence and partially evidenced purchase amounts are not unpaid obligations.",
            "by_currency":uncertainties,
            "unknown_amount_purchase_ids":purchase_ids(&|p|p["amount_minor"].is_null()),
            "undated_unallocated_purchase_ids":purchase_ids(&|p|date_month(&p["order_date"]).ok().as_deref()==Some("undated_unallocated")),
            "purchases_without_merchant_charge":purchase_ids(&|p|["unknown","merchant_refund_only"].contains(&text(&p["payment_evidence"]))&&p["amount_minor"]!=json!(0)),
            "partial_merchant_charge_purchase_ids":purchase_ids(&|p|text(&p["payment_evidence"]).starts_with("merchant_charge_partial")),
            "estimated_purchase_ids":purchase_ids(&|p|text(&p["amount_evidence"])=="estimate"),
            "legacy_unverified_purchase_ids":purchase_ids(&|p|text(&p["amount_evidence"])=="legacy_unverified"),
            "unresolved_allocation_purchase_ids":purchase_ids(&|p|text(&p["allocation_status"])=="unresolved"),
            "unknown_amount_event_ids":event_ids(&|e|e["amount_minor"].is_null()),
            "undated_unallocated_event_ids":event_ids(&|e|date_month(&e["event_date"]).ok().as_deref()==Some("undated_unallocated")),
            "unresolved_allocation_event_ids":event_ids(&|e|text(&e["allocation_status"])=="unresolved"),
            "order_only_allocation_event_ids":event_ids(&|e|truth(&e["unallocated_to_purchase_minor"])),
            "incomplete_coverage_ids":sorted(array(&data["coverage"]).iter().filter(|c|text(&c["coverage"])!="complete").map(|c|text(&c["coverage_id"]).to_owned())),
            "authored_gap_ids":sorted(array(&data["gaps"]).iter().map(|g|text(&g["gap_id"]).to_owned()))
        }
    }))
}
