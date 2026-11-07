//! Keep newly bridged foundations cool while the neighboring ordinary paths retain their native recipe.
use anyhow::{Context, Result};
use serde_json::{json, Value};
use std::collections::{HashMap, HashSet, VecDeque};
use std::f64::consts::TAU;
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Read, Seek, SeekFrom, Write};

const MARKER: &str = "; HSM bridge-foundation cooling";
const RESULT: &str = "; HSM bridge-foundation result: ";
type Key = (i64, i32, i32);
type Pending = (String, Option<f64>);

fn words(line: &str) -> HashMap<char, f64> {
    line.split_whitespace().skip(1).filter_map(|s| {
        let key = s.chars().next()?;
        let number = s[1..].trim_end_matches(|c: char| c.is_ascii_alphabetic()).parse().ok()?;
        Some((key, number))
    }).collect()
}

fn scalar(settings: &Value, key: &str, slot: usize, default: f64) -> f64 {
    let v = &settings[key];
    let v = v.as_array().and_then(|a| a.get(slot).or_else(|| a.first())).unwrap_or(v);
    v.as_f64().or_else(|| v.as_str().and_then(|s| s.parse().ok())).unwrap_or(default)
}

fn part_fan(command: &str, w: &HashMap<char, f64>) -> Option<f64> {
    ((command == "M106" || command == "M107") && w.get(&'P').copied().unwrap_or(1.) == 1.)
        .then(|| if command == "M107" { 0. } else { w.get(&'S').copied().unwrap_or(255.) })
}

fn model(feature: &str) -> bool {
    matches!(feature, "Outer wall" | "Inner wall" | "Overhang wall" | "Bottom surface" |
        "Top surface" | "Internal solid infill" | "Sparse infill" | "Bridge" | "Gap infill" |
        "Internal Bridge" | "Floating vertical shell")
}

fn samples(a: [f64; 2], b: [f64; 2], w: &HashMap<char, f64>, command: &str, step: f64)
    -> (Vec<[f64; 2]>, f64) {
    if matches!(command, "G2" | "G3") && (w.contains_key(&'I') || w.contains_key(&'J')) {
        let c = [a[0] + w.get(&'I').copied().unwrap_or(0.), a[1] + w.get(&'J').copied().unwrap_or(0.)];
        let radius = (a[0]-c[0]).hypot(a[1]-c[1]);
        let start = (a[1]-c[1]).atan2(a[0]-c[0]);
        let mut sweep = (b[1]-c[1]).atan2(b[0]-c[0]) - start;
        if command == "G2" { if sweep >= -1e-9 { sweep -= TAU; } }
        else if sweep <= 1e-9 { sweep += TAU; }
        let length = radius * sweep.abs();
        let n = (length / step).ceil().max(1.) as usize;
        let mut points: Vec<_> = (0..=n).map(|i| {
            let angle = start + sweep * i as f64 / n as f64;
            [c[0] + radius * angle.cos(), c[1] + radius * angle.sin()]
        }).collect();
        *points.last_mut().unwrap() = b;
        (points, length)
    } else {
        let length = (b[0]-a[0]).hypot(b[1]-a[1]);
        let n = (length / step).ceil().max(1.) as usize;
        ((0..=n).map(|i| {
            let t = i as f64 / n as f64;
            [a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t]
        }).collect(), length)
    }
}

fn feed_line(line: &str, feed: f64) -> String {
    let (code, comment) = line.split_once(';').map(|(a,b)| (a,format!(";{b}")))
        .unwrap_or((line,String::new()));
    let mut changed = false;
    let mut parts: Vec<String> = code.split_whitespace().map(|s| {
        if s.starts_with('F') && s[1..].parse::<f64>().is_ok() {
            changed = true; format!("F{feed:.5}")
        } else { s.into() }
    }).collect();
    if !changed { parts.push(format!("F{feed:.5}")); }
    format!("{}{}",parts.join(" "),if comment.is_empty() { comment } else { format!(" {comment}") })
}

fn flush_pending(out: &mut impl Write, pending: &mut Vec<Pending>, recovery: bool,
    fan: &mut f64, feed: &mut f64) -> Result<()> {
    for (line, native_feed) in pending.drain(..) {
        let code=line.split(';').next().unwrap_or("").trim();
        let command=code.split_whitespace().next().unwrap_or("");
        if let Some(value)=part_fan(command,&words(code)) {
            if recovery {continue;} *fan=value;
        }
        if let Some(value)=native_feed {
            if (*feed-value).abs()>1e-6 {
                writeln!(out,"{}",feed_line(&line,value))?;
            } else {writeln!(out,"{line}")?;}
            *feed=value;
        } else {writeln!(out,"{line}")?;}
    }
    Ok(())
}

pub fn process(r: &Value) -> Result<Value> {
    let input = r["input"].as_str().context("cooling input path")?;
    let output = r["output"].as_str().context("cooling output path")?;
    let settings = &r["settings"];
    let policy = &r["policy"];
    let depth = policy["height_mm"].as_f64().context("foundation height")?;
    let grid = policy["grid_mm"].as_f64().context("foundation footprint resolution")?;
    let names = settings["filament_settings_id"].as_array().cloned().unwrap_or_default();
    let selected: HashSet<usize> = names.iter().enumerate().filter_map(|(i,n)| {
        let s=n.as_str().unwrap_or("").to_lowercase();
        (s.contains("pet-gf") || s.contains("petgf")).then_some(i)
    }).collect();
    let mut source = BufReader::new(File::open(input)?);
    let mut first = String::new(); source.read_line(&mut first)?;
    if first.trim_end() == MARKER {
        let length=source.get_ref().metadata()?.len();
        source.seek(SeekFrom::Start(length.saturating_sub(65536)))?;
        let mut bytes=Vec::new();source.read_to_end(&mut bytes)?;
        let tail=String::from_utf8_lossy(&bytes);
        let report=tail.lines().rev().find_map(|line| line.strip_prefix(RESULT))
            .context("processed cooling report")?;
        let mut report:Value=serde_json::from_str(report)?;
        report["changed"]=json!(false);report["already_processed"]=json!(true);
        return Ok(report);
    }
    if selected.is_empty() {return Ok(json!({"changed":false,"petgf_slots":[]}));}
    let mut out = BufWriter::new(File::create(output)?);
    writeln!(out,"{MARKER}")?;
    let mut source = std::iter::once(Ok(first)).chain(source.lines());
    let mut pos=[0.;2]; let mut e=0.; let mut absolute=true; let mut relative=true;
    let mut z=f64::NEG_INFINITY; let mut feature=String::new(); let mut object=-1;
    let mut filament=0; let mut native_fan=0.; let mut emitted_fan=0.;
    let mut native_feed=0.; let mut emitted_feed=0.; let mut width=0.42;
    let mut pending: Vec<Pending>=Vec::new(); let mut pending_fan=0.;
    let mut active:HashMap<Key,f64>=HashMap::new();
    let mut expiry:VecDeque<(f64,Key)>=VecDeque::new();
    let mut seeds:HashSet<Key>=HashSet::new();
    let mut counts:HashMap<String,[f64;3]>=HashMap::new();
    let mut changed_moves=0u64; let mut limited_moves=0u64; let mut added_seconds=0.;
    let mut seed_moves=0u64; let mut ordinary_moves=0u64;
    while let Some(line)=source.next() {
        let line=line?; let line=line.trim_end_matches(['\r','\n']);
        if pending.is_empty() { pending_fan=native_fan; }
        if let Some(comment)=line.strip_prefix(';').map(str::trim) {
            if let Some(value)=comment.strip_prefix("Z_HEIGHT:") {
                let next:f64=value.trim().parse()?;
                if next<z-1e-6 { active.clear();expiry.clear();seeds.clear(); }
                for key in seeds.drain() { active.insert(key,z+depth);expiry.push_back((z+depth,key)); }
                z=next;
                while expiry.front().is_some_and(|(end,_)| *end<z-1e-6) {
                    let (end,key)=expiry.pop_front().unwrap();
                    if active.get(&key).is_some_and(|v| *v<=end) {active.remove(&key);}
                }
            } else if let Some(value)=comment.strip_prefix("FEATURE:") {feature=value.trim().into();}
            else if let Some(value)=comment.strip_prefix("LINE_WIDTH:") {width=value.trim().parse()?;}
            else if let Some(value)=comment.strip_prefix("OBJECT_ID:") {object=value.trim().parse()?;}
            else if let Some(value)=comment.strip_prefix("start printing object, unique label id:") {object=value.trim().parse()?;}
            else if comment.starts_with("stop printing object") {object=-1;}
            pending.push((line.into(),None));continue;
        }
        let code=line.split(';').next().unwrap_or("").trim();
        let command=code.split_whitespace().next().unwrap_or(""); let w=words(code);
        if let Some(fan)=part_fan(command,&w) {native_fan=fan;}
        if command=="M620" { if let Some(f)=w.get(&'S') {filament=*f as usize;} }
        if matches!(command,"G90"|"G91") {absolute=command=="G90";}
        if matches!(command,"M82"|"M83") {relative=command=="M83";}
        if command=="G92" {pos=[w.get(&'X').copied().unwrap_or(pos[0]),w.get(&'Y').copied().unwrap_or(pos[1])];e=w.get(&'E').copied().unwrap_or(e);}
        if !matches!(command,"G0"|"G1"|"G2"|"G3") {pending.push((line.into(),None));continue;}
        if let Some(f)=w.get(&'F') {native_feed=*f;}
        let next=[if absolute {w.get(&'X').copied().unwrap_or(pos[0])} else {pos[0]+w.get(&'X').copied().unwrap_or(0.)},
                  if absolute {w.get(&'Y').copied().unwrap_or(pos[1])} else {pos[1]+w.get(&'Y').copied().unwrap_or(0.)}];
        let de=if relative {w.get(&'E').copied().unwrap_or(0.)} else {w.get(&'E').copied().unwrap_or(e)-e};
        if let Some(v)=w.get(&'E') {if relative {e+=v;} else {e=*v;}}
        let moving=(next[0]-pos[0]).hypot(next[1]-pos[1])>1e-9 || matches!(command,"G2"|"G3");
        if de<=0. || !moving {pos=next;pending.push((line.into(),Some(native_feed)));continue;}
        let wanted=object>=0 && model(&feature) && selected.contains(&filament);
        let cooling = scalar(settings,"overhang_fan_speed",filament,70.) * 255. / 100.;
        let speed = scalar(settings,"filament_bridge_speed",filament,
            scalar(settings,"bridge_speed",filament,25.));
        let (points,length)=if wanted && (native_fan>0. || !active.is_empty()) {
            samples(pos,next,&w,command,grid/2.)
        } else {(Vec::new(),(next[0]-pos[0]).hypot(next[1]-pos[1]))};
        let recovery=wanted && !points.is_empty() && points.iter().all(|p| {
            active.get(&(object,(p[0]/grid).floor() as i32,(p[1]/grid).floor() as i32))
                .is_some_and(|end| *end>=z-1e-6)
        });
        let target_fan=if recovery {native_fan.max(cooling)} else {pending_fan};
        if (emitted_fan-target_fan).abs()>1e-6 {writeln!(out,"M106 P1 S{target_fan:.3}")?;emitted_fan=target_fan;}
        flush_pending(&mut out,&mut pending,recovery,&mut emitted_fan,&mut emitted_feed)?;
        let target_feed=if recovery {native_feed.min(speed*60.)} else {native_feed};
        if recovery {
            changed_moves+=1;
            let row=counts.entry(feature.clone()).or_insert([0.;3]);row[0]+=1.;row[1]+=length;
            if native_feed>target_feed+1e-6 {
                limited_moves+=1;let seconds=length*60.*(1./target_feed-1./native_feed);
                added_seconds+=seconds;row[2]+=seconds;
            }
        } else if wanted {ordinary_moves+=1;}
        let rewritten=if (target_feed-emitted_feed).abs()>1e-6 || w.get(&'F').is_some_and(|f| (*f-target_feed).abs()>1e-6) {
            feed_line(line,target_feed)
        } else {line.into()};
        writeln!(out,"{rewritten}")?;emitted_feed=target_feed;
        if wanted && native_fan>0. {
            seed_moves+=1;
            let reach=(width/2.+grid*2f64.sqrt()/2.)/grid;let cells=reach.ceil() as i32;
            for p in &points {
                let x=(p[0]/grid).floor() as i32;let y=(p[1]/grid).floor() as i32;
                for dx in -cells..=cells {for dy in -cells..=cells {
                    let cx=(x+dx) as f64*grid+grid/2.;let cy=(y+dy) as f64*grid+grid/2.;
                    if (cx-p[0]).hypot(cy-p[1])<=reach*grid {seeds.insert((object,x+dx,y+dy));}
                }}
            }
        }
        pos=next;
    }
    if (emitted_fan-pending_fan).abs()>1e-6 {writeln!(out,"M106 P1 S{pending_fan:.3}")?;}
    flush_pending(&mut out,&mut pending,false,&mut emitted_fan,&mut emitted_feed)?;
    let mut slots:Vec<_>=selected.into_iter().collect();slots.sort_unstable();
    let report=json!({"changed":changed_moves>0,"policy":policy,"petgf_slots":slots,
        "native_cooled_seed_moves":seed_moves,"recovery_moves":changed_moves,"speed_limited_moves":limited_moves,
        "ordinary_model_moves":ordinary_moves,"recovery_fan_percent":settings["overhang_fan_speed"],
        "recovery_speed_limit_mm_s":settings["filament_bridge_speed"],"added_commanded_motion_seconds":added_seconds,
        "recovery_by_feature":counts,"scope":"The complete centerline lies in a recent native-cooled model footprint. Motion coordinates and extrusion words are retained; only local part cooling and recovery feed rates change."});
    writeln!(out,"{RESULT}{report}")?;out.flush()?;
    Ok(report)
}
