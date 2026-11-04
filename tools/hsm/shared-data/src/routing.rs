//! Port frames and variable-radius line routing from authored scalar records.
use anyhow::{Context,Result,bail,ensure};
use hsm_shared_data::common::*;
use hsm_kernel::V3;
use serde_json::{Value,json};
use std::collections::{BTreeMap,BTreeSet};
type Bends=Vec<(usize,f64,f64,f64)>;
type Radii=BTreeMap<usize,f64>;
fn catalog()->Value{serde_json::from_str(include_str!("../catalog/routing.json")).unwrap()}
fn normal(face:&Value)->Result<V3>{if face.is_string(){return point(&catalog()["face_normal"][text(face)])}let v=point(face)?;ensure!(v.norm()!=0.,"zero port direction");Ok(v/v.norm())}
fn face_name(face:&Value)->Result<String>{if let Some(s)=face.as_str(){return Ok(s.into())}let p=normal(face)?;Ok(format!("({})",[p.x,p.y,p.z].map(|v|format(v,"+.3f")).join(", ")))}
fn skew(a:V3,b:V3,d:V3)->f64{let v=b-a;let n=v.norm();if n<1e-9{0.}else{(v.dot(d)/n).clamp(-1.,1.).acos().to_degrees()}}
fn blocked(out:&mut Value,id:&str,why:String){let prior=out[id].as_str();out[id]=json!(if let Some(prior)=prior{format!("{prior}; {why}")}else{why});}
fn port<'a>(frames:&'a Value,anchor:&str)->Result<(&'a Value,&'a Value)>{
    let(name,key)=anchor.split_once('.').unwrap_or((anchor,""));let frame=&frames[name];
    if frame.is_null(){let have=frames.as_object().into_iter().flatten().map(|(k,_)|k.as_str()).collect::<Vec<_>>().join(", ");bail!("KeyError: no frame {name} (have: {have})")}
    let p=&frame["ports"][key];if p.is_null(){let have=frame["ports"].as_object().into_iter().flatten().map(|(k,_)|k.as_str()).collect::<Vec<_>>().join(", ");bail!("KeyError: {name}: no port {key} (have: {have})")}Ok((frame,p))
}
fn dedupe(p:&[V3])->Result<Vec<V3>>{ensure!(!p.is_empty(),"empty centreline");let mut out=vec![p[0]];for v in &p[1..]{if (*v-*out.last().unwrap()).norm()>1e-9{out.push(*v)}}Ok(out)}
fn unit(a:V3,b:V3)->Result<V3>{let v=b-a;ensure!(v.norm()!=0.,"zero leg");Ok(v/v.norm())}
fn straighten(p:&[V3])->Result<Vec<V3>>{ensure!(!p.is_empty(),"empty centreline");let tol=2_f64.to_radians().cos();let mut out=vec![p[0]];for i in 1..p.len()-1{if unit(*out.last().unwrap(),p[i])?.dot(unit(p[i],p[i+1])?)<tol{out.push(p[i])}}out.push(*p.last().unwrap());Ok(out)}
fn bends(p:&[V3])->Result<Bends>{let mut out=vec![];for i in 1..p.len()-1{let t=unit(p[i-1],p[i])?.dot(unit(p[i],p[i+1])?).clamp(-1.,1.).acos().to_degrees();if t>=1e-6{out.push((i,t,(p[i]-p[i-1]).norm(),(p[i+1]-p[i]).norm()));}}Ok(out)}
fn radii(v:&Value)->Result<Radii>{v.as_object().context("corner radii")?.iter().map(|(k,v)|Ok((k.parse()?,number(v)?))).collect()}
fn radius_json(v:&Radii)->Value{json!(v.iter().map(|(k,v)|(k.to_string(),fvalue(*v))).collect::<BTreeMap<_,_>>())}
fn caps(corners:&Bends,bend:&Value,id:&str)->Result<Radii>{
    let idx=corners.iter().map(|(i,_,_,_)|*i).collect::<BTreeSet<_>>();
    if !bend.is_object()||bend.get("_hsm_float").is_some(){let value=number(bend)?;return Ok(idx.into_iter().map(|i|(i,value)).collect())}
    let given=radii(bend)?;let stray=given.keys().copied().filter(|i|!idx.contains(i)).collect::<Vec<_>>();
    if !stray.is_empty(){bail!("{id}: bend={{...}} caps corner{} {}, which {} not a corner — this run turns at {}.",if stray.len()>1{"s"}else{""},stray.iter().map(ToString::to_string).collect::<Vec<_>>().join(", "),if stray.len()>1{"are"}else{"is"},if idx.is_empty(){"no waypoint at all".into()}else{format!("{idx:?}").replace('{',"[").replace('}',"]")})}
    Ok(idx.into_iter().map(|i|(i,given.get(&i).copied().unwrap_or(f64::INFINITY))).collect())
}
fn seat(p:&[V3],corners:&Bends,caps:&Radii,id:&str,blocked_out:&mut Value)->Radii{
    let tang=corners.iter().map(|(i,t,_,_)|(*i,(t.to_radians()/2.).tan())).collect::<BTreeMap<_,_>>();let legs=p.windows(2).map(|w|(w[1]-w[0]).norm()).collect::<Vec<_>>();let mut out=tang.keys().map(|i|(*i,0.)).collect::<Radii>();let mut free=tang.keys().copied().collect::<BTreeSet<_>>();
    while !free.is_empty(){let mut step=free.iter().map(|i|caps[i]-out[i]).fold(f64::INFINITY,f64::min);
        for(j,leg)in legs.iter().enumerate(){let on=[j,j+1].into_iter().filter(|i|tang.contains_key(i)).collect::<Vec<_>>();let rising=on.iter().copied().filter(|i|free.contains(i)).collect::<Vec<_>>();if rising.is_empty(){continue}let spent=on.iter().map(|i|out[i]*tang[i]).sum::<f64>();step=step.min((leg-spent).max(0.)/rising.iter().map(|i|tang[i]).sum::<f64>());}
        for i in &free{*out.get_mut(i).unwrap()+=step;}let mut done=free.iter().copied().filter(|i|caps[i]-out[i]<=1e-9).collect::<BTreeSet<_>>();
        for(j,leg)in legs.iter().enumerate(){let on=[j,j+1].into_iter().filter(|i|tang.contains_key(i)).collect::<Vec<_>>();if !on.is_empty()&&leg-on.iter().map(|i|out[i]*tang[i]).sum::<f64>()<=1e-9{done.extend(on.into_iter().filter(|i|free.contains(i)));}}
        if done.is_empty(){break}free.retain(|i|!done.contains(i));
    }
    let tight=out.iter().filter(|(_,v)|**v<1e-6-1e-9).map(|(i,_)|*i).collect::<Vec<_>>();for i in &tight{out.insert(*i,0.);}
    if let Some(i)=tight.first(){let turn=corners.iter().find(|(k,_,_,_)|k==i).unwrap().1;blocked(blocked_out,id,format!("corner {i} turns {}° between legs of {} mm and {} mm and seats no radius at all — its legs are wholly spent on the corners either side of them. Drawn square. Lengthen a leg, or move what the legs run between.",format(turn,".0f"),format(legs[i-1],".2f"),format(legs[*i],".2f")));}out
}
fn stock_of(kind:&str,od:f64)->Result<Value>{let data=catalog();for s in array(&data["stocks"]){if array(&s["kinds"]).iter().any(|v|text(v)==kind)&&(number(&s["od"])?-od).abs()<0.05{return Ok(s.clone())}}
    let have=array(&data["stocks"]).iter().map(|s|format!("{} Ø{} for {}",text(&s["name"]),format(number(&s["od"]).unwrap(),"g"),array(&s["kinds"]).iter().map(text).collect::<Vec<_>>().join("/"))).collect::<Vec<_>>().join("; ");bail!("KeyError: no stock declared for a {kind} run at Ø{} — add it to STOCKS with the minimum bend radius its datasheet gives (have: {have})",format(od,"g"))
}
fn pair(v:&Value,default:f64)->Result<(f64,f64)>{if v.is_null(){Ok((default,default))}else if v.is_array(){Ok((number(&v[0])?,number(&v[1])?))}else{let n=number(v)?;Ok((n,n))}}
fn record(id:&str,kind:&str,from:&str,to:&str,p:&[V3],diam:f64,bend:f64,note:&Value,min_bend:&Value,corners:&Bends,radii:&Radii,caps:&Radii)->Value{json!({"id":id,"kind":kind,"frm":from,"to":to,"pts":rows(p),"diam":diam,"bend":bend,"note":note.as_str().unwrap_or(""),"min_bend":min_bend,"bends":corners,"radii":radius_json(radii),"caps":radius_json(caps)})}
fn solve(r:&Value,is_route:bool,blocked_out:&mut Value)->Result<Value>{
    let(id,from)=(text(&r["cid"]),text(&r["frm"]));let rest=array(&r["rest"]);let last=rest.last().context("destination anchor is required")?;let to=last.as_str().with_context(||format!("TypeError: {id}: the last argument must be the destination anchor, got {last}"))?;
    let(_,src)=port(&r["frames"],from)?;let(_,dst)=port(&r["frames"],to)?;let diam=number(&src[2]).with_context(||format!("{id}: {from} has no bore Ø — a line cannot be routed through an unsized port"))?;let kind=r["kind"].as_str().unwrap_or("refrigerant");let bend=if r["bend"].is_null(){stock_of(kind,diam)?["min_bend"].clone()}else{r["bend"].clone()};let ratio=r["bend_ratio"].as_f64().unwrap_or(2.);let nominal=if bend.is_object(){ratio*diam}else{number(&bend)?};let(src_pos,dst_pos)=(point(&src[0])?,point(&dst[0])?);let(n_from,n_to)=(normal(&src[1])?,normal(&dst[1])?);let skew_default=r["collet_skew"].as_f64().unwrap_or(3.);
    if !is_route&&(src_pos-dst_pos).norm()<=r["butt_max"].as_f64().unwrap_or(0.01){return Ok(record(id,kind,from,to,&[src_pos,dst_pos],diam,nominal,&r["note"],&Value::Null,&vec![],&Radii::new(),&Radii::new()))}
    let mut p=vec![src_pos];
    if is_route{let sk=r["skew"].as_f64().unwrap_or(skew_default);let reach=if r["bend"].is_null()||r["bend"].is_object(){ratio*diam}else{number(&r["bend"])?};let(stub_out,mut stub_in)=if r["stub"].is_array(){let a=&r["stub"][0];let b=&r["stub"][1];(if a.is_null(){reach}else{number(a)?},if b.is_null(){reach}else{number(b)?})}else{pair(&r["stub"],reach)?};let mut cur=src_pos+n_from*stub_out;p.push(cur);
        for c in &rest[..rest.len()-1]{let m=c.as_object().context("axis constraint")?;ensure!(m.len()==1,"constraint must supply one axis");let(axis,value)=m.iter().next().unwrap();let i=match axis.as_str(){"x"=>0,"y"=>1,"z"=>2,_=>bail!("unknown axis {axis}")};let v=number(value)?;if (cur[i]-v).abs()<1e-9{continue}let mut a=[cur.x,cur.y,cur.z];a[i]=v;cur=V3::from(a);p.push(cur);}
        let outward=(cur-dst_pos).dot(n_to);if outward<stub_in-1e-9{blocked(blocked_out,id,format!("the close into {to} folds — the path is {} mm off the port face but its approach stub is {} mm, so the last turn would back out and come straight back. Drawn with the stub at {}; give the lane {} mm more standoff, or shorten the stub to fit it.",format(outward,".2f"),format(stub_in,".2f"),format(outward.max(0.),".2f"),format(stub_in-outward,".2f")));stub_in=outward.max(0.);}
        let approach=dst_pos+n_to*stub_in;let differ=(0..3).filter(|i|(cur[*i]-approach[*i]).abs()>1e-9).map(|i|["x","y","z"][i]).collect::<Vec<_>>();let off=skew(cur,approach,-n_to);
        if differ.len()>1&&off>sk{blocked(blocked_out,id,format!("the path needs another constraint — {} all still differ from the approach to {to} (at {}, approach {}), and the leg runs {}° off the port's axis, past the {}° a collet takes straight. Drawn as one leg across all of them; say which turns first.",differ.join(", "),py_tuple(cur,2),py_tuple(approach,2),format(off,".1f"),format(sk,".1f")));}
        if (cur-approach).norm()>1e-9{p.push(approach)}p.push(dst_pos);p=straighten(&dedupe(&p)?)?;let off=skew(p[0],p[1],n_from);if off>sk{blocked(blocked_out,id,format!("the run leaves {from} {}° off the collet's axis, past the {}° one takes straight — the first leg runs out along the port. Drawn at the {}°; stand the lane off the port, or turn the collet onto the run.",format(off,".1f"),format(sk,".1f"),format(off,".1f")));}
    }else{let(sk_out,sk_in)=pair(&r["skew"],skew_default)?;let(le_out,le_in)=pair(&r["lead"],0.)?;if le_out!=0.{p.push(src_pos+n_from*le_out)}for v in &rest[..rest.len()-1]{p.push(point(v)?)}if le_in!=0.{p.push(dst_pos+n_to*le_in)}p.push(dst_pos);p=straighten(&dedupe(&p)?)?;
        let off=skew(p[0],p[1],n_from);if off>sk_out{blocked(blocked_out,id,format!("leaves {from} {}° off the port's axis (> {}°), and is drawn at it — move the first waypoint onto the port's normal, or pass `lead=` to plant one.",format(off,".1f"),format(sk_out,".1f")));}let off=skew(p[p.len()-2],p[p.len()-1],-n_to);if off>sk_in{blocked(blocked_out,id,format!("enters {to} {}° off the port's axis (> {}°), and is drawn at it — move the last waypoint onto the port's normal, or pass `lead=` to plant one.",format(off,".1f"),format(sk_in,".1f")));}
    }
    let corners=bends(&p)?;let caps=caps(&corners,&bend,id)?;let radii=seat(&p,&corners,&caps,id,blocked_out);Ok(record(id,kind,from,to,&p,diam,nominal,&r["note"],if is_route{&Value::Null}else{&r["min_bend"]},&corners,&radii,&caps))
}
fn parse_bends(v:&Value)->Result<Bends>{array(v).iter().map(|v|Ok((v[0].as_u64().context("corner index")?as usize,number(&v[1])?,number(&v[2])?,number(&v[3])?))).collect()}
fn length(run:&Value)->Result<f64>{let p=points(&run["pts"])?;let r=radii(&run["radii"])?;let mut total=p.windows(2).map(|w|(w[1]-w[0]).norm()).sum::<f64>();for(i,t,_,_)in parse_bends(&run["bends"])?{let tangent=r[&i]*(t.to_radians()/2.).tan();total-=2.*tangent-r[&i]*t.to_radians();}Ok(total)}
fn segments(run:&Value)->Result<Vec<Value>>{
    let p=points(&run["pts"])?;let corners=parse_bends(&run["bends"])?;let radii=radii(&run["radii"])?;let mut need=vec![0.;p.len()];for(i,t,_,_)in &corners{need[*i]=radii[i]*(t.to_radians()/2.).tan();}let mut result=vec![];let mut cur=p[0];
    for i in 1..p.len()-1{if need[i]==0.{continue}let r=radii[&i];let(din,dout)=(unit(p[i-1],p[i])?,unit(p[i],p[i+1])?);let p1=p[i]-din*need[i];let p2=p[i]+dout*need[i];let turn=corners.iter().find(|(k,_,_,_)|*k==i).unwrap().1;let bis=(dout-din).unit();let center=p[i]+bis*(r/(turn.to_radians()/2.).cos());let mid=center+(p[i]-center).unit()*r;if (p1-cur).norm()>1e-9{result.push(json!({"kind":"line","points":[row(cur),row(p1)]}));}result.push(json!({"kind":"arc","points":[row(p1),row(mid),row(p2)]}));cur=p2;}
    if (*p.last().unwrap()-cur).norm()>1e-9{result.push(json!({"kind":"line","points":[row(cur),row(*p.last().unwrap())]}));}Ok(result)
}
fn frame_constraint(r:&Value)->Result<Value>{
    let frame=&r["frame"];let method=text(&r["method"]);let d=r["distance"].as_f64().unwrap_or(0.);
    if method=="face"{let face=text(&r["face"]);let axis=&face[..1];let sign=&face[1..];let key=format!("{axis}{}",if sign=="+"{"max"}else{"min"});return Ok(json!({axis:number(&frame["bb"][&key])?+if sign=="+"{d}else{-d}}))}
    let p=text(&r["port"]);let value=&frame["ports"][p];ensure!(!value.is_null(),"KeyError: {}: no port {p}",text(&frame["name"]));let pos=point(&value[0])?;
    let(i,step)=if method=="out"{let n=normal(&value[1])?;let off=(0..3).filter(|i|n[*i].abs()>1e-9).collect::<Vec<_>>();ensure!(off.len()==1,"{}.{} exits along {}, off the world axes — `out` supplies one coordinate and cannot name that step. Give the plane as x/y/z, or let the run close straight into the port.",text(&frame["name"]),p,py_tuple(n,4));(off[0],d*n[off[0]])}else{(["x","y","z"].iter().position(|s|*s==method).context("axis constraint")?,d)};{let axis=["x","y","z"][i];Ok(json!({axis:pos[i]+step}))}
}
pub fn dispatch(op:&str,r:&Value)->Result<Value>{
    let mut blocked_out=r.get("blocked").cloned().filter(Value::is_object).unwrap_or(json!({}));
    let value=match op{
        "definitions"=>{let mut data=catalog();data["constants"]=json!({"bend_ratio":2.,"butt_max":0.01,"collet_skew":3.,"straight_tol":2_f64.to_radians().cos()});for(_,spool)in data["spools"].as_object_mut().unwrap(){spool["rgb"]=if spool["color"]["bytes"].is_array(){spool["color"]["bytes"].clone()}else{r["palette"][text(&spool["color"]["palette"])].clone()};spool.as_object_mut().unwrap().remove("color");}data},
        "normal"=>row(normal(&r["face"])?),"face_name"=>json!(face_name(&r["face"])?),"skew"=>json!(skew(point(&r["a"])?,point(&r["b"])?,point(&r["direction"])?)),
        "channel"=>{let(a,b,bias)=(number(&r["a"])?,number(&r["b"])?,number(&r["bias"])?);json!((a+b)/2.+bias*((b-a).abs()/2.-0.6))},
        "blocked"=>{blocked(&mut blocked_out,text(&r["cid"]),text(&r["why"]).to_owned());Value::Null},
        "route"=>solve(r,true,&mut blocked_out)?,"bent"=>solve(r,false,&mut blocked_out)?,
        "length"=>json!(length(&r["run"])?),"tightest"=>json!(radii(&r["run"]["radii"])?.values().copied().reduce(f64::min).unwrap_or(number(&r["run"]["bend"])?)),
        "dedupe"=>rows(&dedupe(&points(&r["points"])?)?),"straighten"=>rows(&straighten(&points(&r["points"])?)?),"unit"=>row(unit(point(&r["a"])?,point(&r["b"])?)?),"bends"=>json!(bends(&points(&r["points"])?)?),
        "caps"=>radius_json(&caps(&parse_bends(&r["bends"])?,&r["bend"],text(&r["cid"]))?),"seat_radii"=>radius_json(&seat(&points(&r["points"])?,&parse_bends(&r["bends"])?,&radii(&r["caps"])?,text(&r["cid"]),&mut blocked_out)),
        "stock"=>stock_of(text(&r["kind"]),number(&r["diam"])?)?,
        "spool_key"=>{let data=catalog();let id=text(&r["cid"]);let key=if let Some(key)=data["spool_of"][id].as_str(){key}else{let prefix=id.rsplit_once('-').map(|(a,_)|a).unwrap_or(id);data["by_prefix"][prefix].as_str().with_context(||format!("KeyError: no spool declared for `{id}` — name it in SPOOL_OF, or give its circuit a prefix in _BY_PREFIX (have: carb, co2, fluid, refrig, water)"))?};json!(key)},
        "color"=>{let s=&r["spool"];json!([number(&s["rgb"][0])?/255.,number(&s["rgb"][1])?/255.,number(&s["rgb"][2])?/255.,s["alpha"]])},
        "meet"=>{let(p,u,q,v)=(point(&r["p"])?,point(&r["u"])?,point(&r["q"])?,point(&r["v"])?);let w=p-q;let(a,b,c,d,e)=(u.dot(u),u.dot(v),v.dot(v),u.dot(w),v.dot(w));let den=a*c-b*b;ensure!(den!=0.,"parallel collet axes");let c1=p+u*((b*e-c*d)/den);let c2=q+v*((a*e-b*d)/den);let bias=number(&r["bias"])?;row(c1*(1.-bias)+c2*bias)},
        "segments"=>json!(segments(&r["run"])?),"tube_recipe"=>{let run=&r["run"];let p=points(&run["pts"])?;json!({"radius":number(&run["diam"])?/2.,"origin":row(p[0]),"direction":row(unit(p[0],p[1])?)})},
        "leg_caps"=>{let run=&r["run"];let p=points(&run["pts"])?;let tang=parse_bends(&run["bends"])?.into_iter().map(|(i,t,_,_)|(i,(t.to_radians()/2.).tan())).collect::<Radii>();let mut out=vec![];for i in 0..p.len()-1{let demand=tang.get(&i).copied().unwrap_or(0.)+tang.get(&(i+1)).copied().unwrap_or(0.);if demand<=1e-12{continue}let leg=(p[i+1]-p[i]).norm();out.push(json!([leg/demand,i,leg,demand,if i==0||i==p.len()-2{"lead"}else{"interior"}]));}json!(out)},
        "redrawn"=>{let run=&r["run"];let ceilings=radii(&run["caps"])?;let ceiling=ceilings.values().next().copied().unwrap_or(number(&run["bend"])?);ensure!(ceilings.values().all(|v|*v==ceiling),"{}: this run caps its corners one at a time and a redraw cannot carry those caps onto a new centreline. Redraw it at its call in `_lines.py`.",text(&run["id"]));let p=straighten(&dedupe(&points(&r["points"])?)?)?;let corners=bends(&p)?;let caps=corners.iter().map(|(i,_,_,_)|(*i,ceiling)).collect();let radii=seat(&p,&corners,&caps,text(&run["id"]),&mut blocked_out.clone());record(text(&run["id"]),text(&run["kind"]),text(&run["frm"]),text(&run["to"]),&p,number(&run["diam"])?,number(&run["bend"])?,&run["note"],&run["min_bend"],&corners,&radii,&caps)},
        "frame_port"=>{let frame=&r["frame"];let p=text(&r["port"]);let value=&frame["ports"][p];ensure!(!value.is_null(),"KeyError: {}: no port {p}",text(&frame["name"]));value.clone()},"frame_constraint"=>frame_constraint(r)?,
        _=>bail!("unknown routing operation {op}")
    };Ok(json!({"value":value,"blocked":blocked_out}))
}
