use super::*;
pub fn export_json(data:&Value)->Result<String>{Ok(serde_json::to_string_pretty(data)?+"\n")}
fn csv_cell(value:&str)->String{if value.contains([',','\n','\r','"']){format!("\"{}\"",value.replace('"',"\"\""))}else{value.into()}}
pub fn export_csv(data:&Value)->Result<String>{
    let mut metadata=selected(data,&json!(["schema_version","as_of","reporting_period","currency_scales","input_fingerprint"]));
    if let Some(summaries)=data["summary"].as_object(){for(name,summary)in summaries{metadata[format!("{name}_basis")]=summary["basis"].clone();}}
    let mut records=vec![("metadata".to_owned(),metadata)];
    for table in ["purchases","orders","events","allocations","sources","coverage","gaps"]{
        let kind=if table=="coverage"{table}else{&table[..table.len()-1]};
        records.extend(array(&data[table]).iter().cloned().map(|row|(kind.to_owned(),row)));
    }
    for name in ["procurement","merchant_payments"]{for part in ["monthly","undated_unallocated","totals"]{records.extend(array(&data["summary"][name][part]).iter().cloned().map(|row|(format!("{name}_{part}"),row)));}}
    if data.get("summary").is_some(){for name in ["fulfillment","uncertainty"]{records.push((name.into(),data["summary"][name].clone()));}}
    records.push(("validation".into(),data["validation"].clone()));
    let fields=records.iter().flat_map(|(_,v)|v.as_object().into_iter().flatten().map(|(k,_)|k.clone())).collect::<BTreeSet<_>>();
    let mut out=std::iter::once("record_type".to_owned()).chain(fields.iter().cloned()).map(|s|csv_cell(&s)).collect::<Vec<_>>().join(",")+"\n";
    for(kind,row)in records{
        let cells=std::iter::once(kind).chain(fields.iter().map(|key|match &row[key]{Value::Null=>String::new(),Value::String(s)=>s.clone(),v=>serde_json::to_string(v).unwrap()})).map(|s|csv_cell(&s)).collect::<Vec<_>>();
        out+=&cells.join(",");out.push('\n');
    }Ok(out)
}
fn display(v:&Value)->String{v.as_str().map(str::to_owned).unwrap_or_else(||py_repr(v))}
fn period_repr(v:&Value)->String{if v.is_object()&&v.get("start").is_some()&&v.get("end").is_some(){format!("{{'start': {}, 'end': {}}}",py_repr(&v["start"]),py_repr(&v["end"]))}else{py_repr(v)}}
pub fn render_report(data:&Value,audit:bool)->Result<String>{
    let mut lines=vec![format!("Project ledger as of {} ({})",display(&data["as_of"]),display(&data["input_fingerprint"]))];
    if !array(&data["validation"]["errors"]).is_empty(){lines.push("Integrity errors:".into());lines.extend(array(&data["validation"]["errors"]).iter().map(|e|format!("  {}",text(e))));return Ok(lines.join("\n")+"\n")}
    let summary=&data["summary"];let scales=&data["currency_scales"];
    let amount=|row:&Value,key:&str|format_minor(&row[key],text(&row["currency"]),scales);
    lines.push("Procurement by order month — current project amounts:".into());
    lines.push("Month | Currency | Final vendor amount | Estimate | Legacy unverified | Total | Payment-evidence gaps".into());
    let missing=ids(&summary["uncertainty"]["purchases_without_merchant_charge"]).into_iter().collect::<BTreeSet<_>>();
    for row in array(&summary["procurement"]["monthly"]).iter().chain(array(&summary["procurement"]["undated_unallocated"])){
        let mut cells=vec![row["month"].as_str().unwrap_or("undated/unallocated").to_owned(),text(&row["currency"]).to_owned()];
        for key in ["final_vendor_amount_minor","estimate_minor","legacy_unverified_minor","total_minor"]{cells.push(amount(row,key)?);}
        cells.push(ids(&row["purchase_ids"]).iter().filter(|id|missing.contains(*id)).count().to_string());lines.push(cells.join(" | "));
    }
    for row in array(&summary["procurement"]["totals"]){lines.push(format!("Procurement total ({}): {}",text(&row["currency"]),amount(row,"total_minor")?));}
    lines.push("Merchant-evidenced payments by merchant event month:".into());lines.push("Month | Currency | Charges | Issued refunds | Net | Authorizations | Noncash credits".into());
    for row in array(&summary["merchant_payments"]["monthly"]).iter().chain(array(&summary["merchant_payments"]["undated_unallocated"])){
        let mut cells=vec![row["month"].as_str().unwrap_or("undated/unallocated").to_owned(),text(&row["currency"]).to_owned()];
        for key in ["charges_minor","refunds_minor","net_minor","authorizations_minor","noncash_credits_minor"]{cells.push(amount(row,key)?);}lines.push(cells.join(" | "));
    }
    for row in array(&summary["merchant_payments"]["totals"]){lines.push(format!("Merchant evidence total ({}): charges {}, refunds {}, net {}",text(&row["currency"]),amount(row,"charges_minor")?,amount(row,"refunds_minor")?,amount(row,"net_minor")?));}
    lines.push("Fulfillment amounts do not establish unpaid obligations:".into());
    for row in array(&summary["fulfillment"]["by_status"]){lines.push(format!("  {}: {} ({} records; {} unknown amounts)",text(&row["fulfillment"]),amount(row,"amount_minor")?,array(&row["purchase_ids"]).len(),array(&row["unknown_amount_ids"]).len()));}
    lines.push(text(&summary["uncertainty"]["basis"]).into());lines.push("Evidence limitations:".into());
    for row in array(&summary["uncertainty"]["by_currency"]){lines.push(format!("  Known purchase valuation without merchant charge evidence ({}): {}",text(&row["currency"]),amount(row,"purchases_without_merchant_charge_minor")?));lines.push(format!("  Undated/unallocated procurement ({}): {}",text(&row["currency"]),amount(row,"undated_unallocated_purchase_minor")?));}
    for key in ["unknown_amount_purchase_ids","undated_unallocated_purchase_ids","purchases_without_merchant_charge","partial_merchant_charge_purchase_ids","estimated_purchase_ids","legacy_unverified_purchase_ids","unresolved_allocation_purchase_ids","unknown_amount_event_ids","undated_unallocated_event_ids","unresolved_allocation_event_ids","order_only_allocation_event_ids","incomplete_coverage_ids","authored_gap_ids"]{
        if let Some(rows)=summary["uncertainty"][key].as_array(){lines.push(format!("  {key}: {}",rows.len()));}
    }
    lines.extend(array(&data["validation"]["warnings"]).iter().map(|v|format!("  {}",text(v))));
    if audit{
        for row in array(&data["coverage"]){lines.push(format!("  Coverage {}: {} / {} / {}; checked {}; examined {}; complete {}; {}",text(&row["coverage_id"]),text(&row["vendor"]),text(&row["stream"]),text(&row["evidence_type"]),text(&row["checked_at"]),period_repr(&row["examined_period"]),period_repr(&row["complete_period"]),text(&row["coverage"])));}
        for row in array(&data["gaps"]){lines.push(format!("  Gap {}: {}; sources checked: {}",text(&row["gap_id"]),text(&row["missing_fact"]),py_repr(row.get("sources_checked").unwrap_or(&json!([])))));}
    }
    Ok(lines.join("\n")+"\n")
}
