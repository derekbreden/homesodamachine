//! Existing machine scorecard decisions over plain construction ledgers.
use super::*;
fn check(
    id: &str,
    label: &str,
    kind: &str,
    ok: bool,
    value: String,
    target: &str,
    detail: Vec<String>,
) -> Value {
    json!({"id":id,"label":label,"kind":kind,"status":if ok{"pass"}else{"fail"},"value":value,"target":target,"detail":detail,"active":kind!="goal"})
}
fn mounts(w: &World, m: &Value, rules: &Value) -> Vec<Value> {
    let have = w.populations[0].iter().cloned().collect::<BTreeSet<_>>();
    let mut rows = array(&rules["mounts"])
        .iter()
        .cloned()
        .chain(geometry::selected_mounts(m, rules))
        .filter(|r| have.contains(&string(&r[0])))
        .collect::<Vec<_>>();
    let typed = rows.iter().map(|r| string(&r[0])).collect::<BTreeSet<_>>();
    for n in have.difference(&typed) {
        rows.push(json!([n, null, "pack"]));
    }
    rows
}
fn coverage(w: &World, rows: &[Value]) -> Value {
    let have = w.populations[0].iter().cloned().collect::<BTreeSet<_>>();
    let declared = rows.iter().map(|r| string(&r[0])).collect::<BTreeSet<_>>();
    let mut detail = have
        .difference(&declared)
        .map(|n| format!("placed, undeclared: {n}"))
        .collect::<Vec<_>>();
    detail.extend(
        declared
            .difference(&have)
            .map(|n| format!("declared, unplaced: {n}")),
    );
    check(
        "coverage",
        "Every placed body is declared in the fastening table",
        "gate",
        detail.is_empty(),
        format!(
            "{}/{} declared",
            have.intersection(&declared).count(),
            have.len()
        ),
        "all declared",
        detail,
    )
}
fn mounted(rows: &[Value], rules: &Value) -> Result<Value> {
    let have = rows
        .iter()
        .map(|r| (string(&r[0]), r))
        .collect::<BTreeMap<_, _>>();
    let never = obj(&rules["never"]);
    let rides = obj(&rules["rides"])
        .into_iter()
        .filter(|(r, h)| have.contains_key(r) && have.contains_key(&string(h)))
        .collect::<BTreeMap<_, _>>();
    for (n, why) in &never {
        let r = have
            .get(n)
            .with_context(|| format!("NEVER names absent body {n}"))?;
        ensure!(r[1].is_null(), "NEVER names fastened body {n}");
        ensure!(
            !string(why).trim().is_empty(),
            "NEVER has no reason for {n}"
        );
    }
    for (r, h) in &rides {
        ensure!(
            !rides.contains_key(&string(h)),
            "rider {r} is held by a rider"
        );
    }
    let mut open = rows
        .iter()
        .filter(|r| {
            !rides.contains_key(&string(&r[0]))
                && r[1].is_null()
                && !never.contains_key(&string(&r[0]))
        })
        .map(|r| (string(&r[0]), string(&r[2])))
        .collect::<Vec<_>>();
    open.sort();
    let mut detail = open
        .iter()
        .map(|(n, j)| format!("{n}: {j}"))
        .collect::<Vec<_>>();
    for (n, r) in &have {
        if !rides.contains_key(n) && never.contains_key(n) {
            detail.push(format!(
                "{n}: {} — nothing fastens it; {}",
                string(&r[2]),
                string(&never[n])
            ));
        }
    }
    let total = rows
        .iter()
        .filter(|r| !rides.contains_key(&string(&r[0])))
        .count()
        - never.len();
    Ok(check(
        "mounted",
        "A printed feature of another placed part fastens every body",
        "gate",
        open.is_empty(),
        format!(
            "{}/{} mounted, {} part of another body, {} nothing fastens",
            total - open.len(),
            total,
            rides.len(),
            never.len()
        ),
        "a printed joint per body",
        detail,
    ))
}
fn seats(w: &World, m: &Value) -> (Value, Value) {
    let seats = obj(&m["seats"]);
    let tol = m["seat_tolerance"].as_f64().unwrap_or(1e-6);
    let bodies = w.populations[0].iter().cloned().collect::<BTreeSet<_>>();
    let mut covered = BTreeSet::new();
    let mut off = Vec::new();
    let mut room = Vec::new();
    for (n, s) in &seats {
        covered.extend(names(&s["members"]).intersection(&bodies).cloned());
        if s["rule"]["station"].is_array() {
            for (i, ax) in ["x", "y", "z"].iter().enumerate() {
                let want = num(&s["rule"]["station"][i]);
                let got = num(&s["got"]["station"][i]);
                if (got - want).abs() > tol {
                    off.push((
                        n.clone(),
                        format!("mouth {ax}"),
                        want,
                        got,
                        (got - want).abs(),
                    ));
                }
            }
        } else {
            for (k, want) in obj(&s["rule"]) {
                if let Some(got) = s["got"].get(&k) {
                    let (want, got) = (num(&want), num(got));
                    if (got - want).abs() > tol {
                        off.push((n.clone(), k, want, got, (got - want).abs()));
                    }
                }
            }
        }
        for r in array(&s["room"]) {
            room.push((n.clone(), string(&r[0]), num(&r[1]), r[2].as_f64()));
        }
    }
    let mut details = bodies
        .difference(&covered)
        .map(|n| format!("{n}: no seat states where it stands"))
        .collect::<Vec<_>>();
    off.sort_by(|a, b| b.4.total_cmp(&a.4));
    details.extend(off.iter().map(|(n, k, w, g, d)| {
        format!("{n}: {k} was asked for {w:.4} and reads {g:.4} — {d:.2e} mm off")
    }));
    let placed = check(
        "placed",
        "Every placement is stated as a rule, and the solid lands on it",
        "goal",
        covered == bodies && off.is_empty(),
        format!("{}/{} stated", covered.len(), bodies.len()),
        "a stated rule per body, each landing on it",
        details,
    );
    let short = room
        .iter()
        .filter(|r| r.3.is_some_and(|g| g < r.2 - 1e-6))
        .count();
    let tightest = room
        .iter()
        .filter_map(|r| r.3.map(|g| g - r.2))
        .min_by(f64::total_cmp);
    room.sort_by(|a, b| {
        a.3.is_none().cmp(&b.3.is_none()).then_with(|| {
            a.3.map(|g| g - a.2)
                .unwrap_or(0.)
                .total_cmp(&b.3.map(|g| g - b.2).unwrap_or(0.))
        })
    });
    let detail = room
        .iter()
        .map(|(n, k, w, g)| {
            format!(
                "{n}: {k} — wants {}, has {}{}",
                pretty(*w),
                g.map(|v| format!("{v:.3}"))
                    .unwrap_or("nothing under it".to_owned()),
                if g.is_some_and(|g| g < *w - 1e-6) {
                    " — ✗ short of its own band"
                } else {
                    ""
                }
            )
        })
        .collect();
    let room = check(
        "room-holds",
        "Every derived pose has the room its own construction states",
        "gate",
        short == 0,
        format!(
            "{}/{} bands held{}",
            room.len() - short,
            room.len(),
            tightest
                .map(|v| format!(", tightest {v:+0.3} mm"))
                .unwrap_or_default()
        ),
        "every band held",
        detail,
    );
    (placed, room)
}
fn bed_fit(w: &World, m: &Value) -> Value {
    let bed = array(&m["bed"]).iter().map(num).collect::<Vec<_>>();
    let bed = if bed.len() == 3 {
        bed
    } else {
        vec![325., 320., 320.]
    };
    let mut detail = Vec::new();
    for n in &w.populations[2] {
        let b = w.g(n).unwrap().bounds;
        let d = [b[3] - b[0], b[4] - b[1], b[5] - b[2]];
        if (0..3).any(|i| d[i] > bed[i]) {
            detail.push(format!(
                "{n}: {:.1} × {:.1} × {:.1} over {} × {} × {}",
                d[0],
                d[1],
                d[2],
                pretty(bed[0]),
                pretty(bed[1]),
                pretty(bed[2])
            ));
        }
    }
    check(
        "bed-fit",
        "Every printed piece fits the bed",
        "gate",
        detail.is_empty(),
        format!(
            "{}/{} on the bed",
            w.populations[2].len() - detail.len(),
            w.populations[2].len()
        ),
        "every piece on the bed",
        detail,
    )
}
fn pack_closes(r: &geometry::Readings) -> Value {
    let mut detail = r
        .clashes
        .iter()
        .map(|c| {
            let wh = &c["where"];
            format!(
                "{} ∩ {}   {:.1} mm³, ({:.1}, {:.1}, {:.1})..({:.1}, {:.1}, {:.1})",
                string(&c["a"]),
                string(&c["b"]),
                num(&c["volume"]),
                num(&wh["min"][0]),
                num(&wh["min"][1]),
                num(&wh["min"][2]),
                num(&wh["max"][0]),
                num(&wh["max"][1]),
                num(&wh["max"][2])
            )
        })
        .collect::<Vec<_>>();
    detail.extend(
        r.unanswered
            .iter()
            .map(|r| format!("{} ? {}   {}", string(&r[0]), string(&r[1]), string(&r[2]))),
    );
    let rows = array(&r.contacts["mates"]["pairs"]);
    if !rows.is_empty() {
        let outside = rows
            .iter()
            .map(|r| num(&r["outside_mate_region_mm3"]))
            .fold(0., f64::max);
        detail.push(format!("Selected nominal mates: {}/{} within finite insertion/thread/heat-set regions at the existing 1 mm³ contact floor; maximum outside {outside:.6} mm³. Physical insertion, sealing and retention remain unqualified.",rows.iter().filter(|r|r["pass"]==true).count(),rows.len()));
    }
    if let Some(p) = r.contacts.get("pump") {
        detail.push(format!("G Ganen cap bearing: {} named free-rubber foot envelopes; {:.3} mm³ contact, {:.6} mm³ rigid interference, {:.6} mm³ outside the contact masks",array(&p["feet"]).len(),num(&p["free_foot_contact_mm3"]),num(&p["rigid_overlap_mm3"]),num(&p["outside_contact_masks_mm3"])));
    }
    for (family, prefix, body) in [
        (
            "reducers",
            "Flavor reducer stems in their valve outlets: ",
            "v-",
        ),
        ("elbows", "Stem elbows in their collets: ", ""),
    ] {
        if r.contacts[family].is_object() {
            let stems = obj(&r.contacts[family]["stems"]);
            detail.push(format!(
                "{prefix}{}",
                stems
                    .iter()
                    .map(|(n, v)| format!(
                        "{body}{n} {:.1} mm³ in the stem, {:.6} mm³ outside it",
                        num(&v[0]),
                        num(&v[1])
                    ))
                    .collect::<Vec<_>>()
                    .join("; ")
            ));
        }
    }
    if let Some(s) = r.contacts.get("seal") {
        detail.push(format!("Elbow stem in the plug's land: {:.2} mm³ in the push-on seal's ring, {:.6} mm³ outside it",num(&s["land_contact_mm3"]),num(&s["outside_land_mm3"])));
    }
    check(
        "pack-closes",
        "No unconnected material overlaps (pack closes)",
        "gate",
        r.clashes.is_empty() && r.unanswered.is_empty(),
        format!(
            "{} clash, {} unanswered",
            r.clashes.len(),
            r.unanswered.len()
        ),
        "0 clash, 0 unanswered",
        detail,
    )
}
fn clearance(r: &geometry::Readings) -> Value {
    let short = r
        .clearances
        .iter()
        .filter(|r| r[3] != true && num(&r[2]) < 1.)
        .collect::<Vec<_>>();
    let mut detail=vec!["every body pair, and every drawn run against what its own line does not join it to — the exact solid distance, with boxes only as a prefilter".to_owned()];
    detail.extend(short.iter().map(|r| {
        format!(
            "{} — {}: {:.3} mm — under the spacing preference",
            string(&r[0]),
            string(&r[1]),
            num(&r[2])
        )
    }));
    detail.extend(r.lanes.iter().cloned());
    for row in &r.clearances {
        if short.contains(&row) {
            continue;
        }
        detail.push(format!(
            "{} — {}: {:.3} mm{}",
            string(&row[0]),
            string(&row[1]),
            num(&row[2]),
            if row[3] == true {
                " — excluded from the global pack floor"
            } else {
                ""
            }
        ));
    }
    detail.push("The 1 mm spacing preference is informational. Fitted parts retain their applicable local allowances; pack-closes measures material outside the finite receiving interfaces. Conductors are excluded from this scene check.".to_owned());
    let tightest = r
        .clearances
        .iter()
        .filter(|r| r[3] != true)
        .map(|r| num(&r[2]))
        .min_by(f64::total_cmp);
    check(
        "clearance-floor",
        "Preferred spacing outside named fitted interfaces",
        "goal",
        short.is_empty(),
        tightest
            .map(|t| format!("{} under, tightest {t:.3} mm", short.len()))
            .unwrap_or("no pair in reach".to_owned()),
        "≥ 1 mm",
        detail,
    )
}
fn size_rows(w: &World) -> Vec<Value> {
    let mut out = Vec::new();
    for (id, label, ns) in [
        (
            "enclosure",
            "the printed box, outside face to outside face",
            w.populations[2].clone(),
        ),
        (
            "assembly",
            "every placed body, the box around them included",
            w.populations.iter().flatten().cloned().collect::<Vec<_>>(),
        ),
    ] {
        if ns.is_empty() {
            continue;
        }
        let mut lo = [f64::INFINITY; 3];
        let mut hi = [f64::NEG_INFINITY; 3];
        for n in ns {
            let b = w.g(&n).unwrap().bounds;
            for i in 0..3 {
                lo[i] = lo[i].min(b[i]);
                hi[i] = hi[i].max(b[i + 3]);
            }
        }
        out.push(json!({"id":id,"label":label,"min":lo.map(|v|round(v,3)),"max":hi.map(|v|round(v,3)),"mm":[round(hi[0]-lo[0],3),round(hi[1]-lo[1],3),round(hi[2]-lo[2],3)]}));
    }
    out
}
fn bend_check(bends: &[Value]) -> Value {
    let graded = bends
        .iter()
        .filter(|r| !r["grade"].is_null())
        .collect::<Vec<_>>();
    let corners = graded
        .iter()
        .map(|r| array(&r["corners"]).len())
        .sum::<usize>();
    let at = graded
        .iter()
        .map(|r| r["atSpec"].as_u64().unwrap_or(0) as usize)
        .sum::<usize>();
    let worst = graded
        .iter()
        .map(|r| routes::grade_index(&r["grade"]))
        .max()
        .unwrap_or(1);
    let bands = ["A", "B", "C", "D", "F"];
    let tally = bands
        .iter()
        .filter_map(|g| {
            let n = graded.iter().filter(|r| r["grade"] == *g).count();
            (n > 0).then(|| format!("{g}:{n}"))
        })
        .collect::<Vec<_>>()
        .join(" ");
    let mut detail=vec!["grade = radius ÷ the stock's minimum — 4 mm LLDPE R25; 1/4\" LLDPE R14; 1/4\" soft ACR copper R12.7".to_owned(),format!("runs by grade: {}",if tally.is_empty(){"none with a corner"}else{&tally}),"each row ends with its need — path ÷ the span its own two ends stand at. Far above 1 is a run riding infrastructure its ends do not ask for, and there the move is the route rather than the corner. Near 1 is not health: a short run can be pinned at both ends and still red".to_owned()];
    for d in bends {
        if d["grade"].is_null() || routes::grade_index(&d["grade"]) <= 1 {
            continue;
        }
        let b = &d["binding"];
        let bound = if b.is_null() {
            String::new()
        } else {
            format!(", bound by leg {} at {:.1} mm", b["leg"], num(&b["length"]))
        };
        detail.push(format!(
            "{}/{} {} ({} → {}): R{:.1} against R{}{}{}",
            string(&d["grade"]),
            if d["reachGrade"].is_null() {
                "None".to_owned()
            } else {
                string(&d["reachGrade"])
            },
            string(&d["id"]),
            string(&d["frm"]),
            string(&d["to"]),
            num(&d["radius"]),
            pretty(num(&d["minBend"])),
            bound,
            routes::need_clause(&d["need"])
        ));
    }
    check(
        "bend-radius",
        "Every routed tube turns at or above its stock's minimum radius",
        "gate",
        worst <= 1,
        format!("{} — {at}/{corners} corners at spec", bands[worst]),
        "every corner ≥ its stock's minimum (B)",
        detail,
    )
}
fn connections(m: &Value, rules: &Value) -> Result<Vec<Value>> {
    let mut out = Vec::new();
    let topo = std::fs::read_to_string(
        m["topology_path"]
            .as_str()
            .unwrap_or("hardware/topology/fluid-topology.md"),
    )?;
    for line in topo.lines() {
        let cells = line.split('|').map(str::trim).collect::<Vec<_>>();
        if cells.len() >= 5 && cells[1].parse::<usize>().is_ok() {
            out.push(json!({"id":format!("fluid-{}",cells[1]),"kind":"fluid","frm":cells[2],"to":cells[3]}));
        }
    }
    for (table, kind) in [
        ("refrigerant_segments", "refrigerant"),
        ("water_segments", "water"),
        ("co2_segments", "co2"),
        ("carb_segments", "water"),
    ] {
        for r in array(&rules[table]) {
            out.push(json!({"id":r[0],"kind":kind,"frm":r[1],"to":r[2]}));
        }
    }
    let drawn = array(&m["runs"])
        .iter()
        .map(|r| string(&r["id"]))
        .collect::<BTreeSet<_>>();
    let mated = array(&m["refrigerant_mates"])
        .iter()
        .map(|r| (string(&r[0]), num(&r[3])))
        .collect::<BTreeMap<_, _>>();
    let interior = obj(&m["manifold_connection_made"]);
    let blocked = obj(&m["blocked_runs"]);
    for c in &mut out {
        let id = string(&c["id"]);
        let made = if drawn.contains(&id) {
            "drawn".to_owned()
        } else if mated.contains_key(&id) {
            "mate".to_owned()
        } else {
            interior
                .get(&id)
                .map(string)
                .unwrap_or("not drawn".to_owned())
        };
        c["made"] = json!(made);
        c["note"] = json!(if made == "mate" {
            format!(", {:.3} mm apart", mated[&id])
        } else {
            String::new()
        });
        c["blocked"] = blocked.get(&id).cloned().unwrap_or(json!(""));
    }
    let native = obj(&m["native_connections"]);
    let mut order = strings(&m["native_connection_order"]);
    for id in native.keys() {
        if !order.contains(id) {
            order.push(id.clone());
        }
    }
    for id in order {
        let Some(g) = native.get(&id) else {
            continue;
        };
        let i = if let Some(i) = out.iter().position(|r| r["id"] == id) {
            i
        } else {
            let kind = if id.starts_with("water-") || id.starts_with("carb-") {
                "water"
            } else {
                id.split('-').next().unwrap()
            };
            out.push(json!({"id":id,"kind":kind}));
            out.len() - 1
        };
        let c = &mut out[i];
        let native = strings(&g["native_routes"]);
        let missing = native
            .iter()
            .filter(|rid| !drawn.contains(*rid))
            .cloned()
            .collect::<Vec<_>>();
        c["frm"] = g["from"].clone();
        c["to"] = g["to"].clone();
        c["made"] = if missing.is_empty() {
            g["made"].clone()
        } else {
            json!("not drawn")
        };
        c["blocked"] = json!(if missing.is_empty() {
            String::new()
        } else {
            format!("missing native tubes: {}", missing.join(", "))
        });
        c["note"] = json!(format!(
            ", {}",
            if native.is_empty() {
                "direct fitting joint".to_owned()
            } else {
                native.join(", ")
            }
        ));
    }
    Ok(out)
}
fn routed(conns: &[Value], rules: &Value) -> Value {
    let missing = conns
        .iter()
        .filter(|c| c["made"] == "not drawn")
        .collect::<Vec<_>>();
    let mut kinds: BTreeMap<String, (usize, usize)> = BTreeMap::new();
    let mut how: BTreeMap<String, usize> = BTreeMap::new();
    for c in conns {
        let k = kinds.entry(string(&c["kind"])).or_default();
        k.1 += 1;
        if c["made"] != "not drawn" {
            k.0 += 1;
            *how.entry(string(&c["made"])).or_default() += 1;
        }
    }
    let mut how = how.into_iter().collect::<Vec<_>>();
    how.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
    let mut detail=vec!["a connection is MADE when the machine holds a path for it: a run `_lines.py` draws, one of the pack's own constructions — a butt between two collets, a fixed TPU return with straight links, a permanent pump dock, or a quarter turn and the step off it — or a joint made up across a plane two bodies already share or on its fittings' threads".to_owned(),format!("{} — {} still to route",how.iter().map(|(h,n)|format!("{h} {n}")).collect::<Vec<_>>().join(", "),missing.len()),format!("by circuit — {}",kinds.iter().map(|(k,(d,t))|format!("{k} {d}/{t}")).collect::<Vec<_>>().join(", "))];
    let row = |c: &&Value| {
        format!(
            "{} ({}): {} → {} — {}{}",
            string(&c["id"]),
            string(&c["kind"]),
            string(&c["frm"]),
            string(&c["to"]),
            string(&rules["made_as"][string(&c["made"])]),
            string(&c["note"])
        )
    };
    detail.extend(missing.iter().map(row));
    detail.extend(
        conns
            .iter()
            .filter(|c| c["made"] == "mate")
            .map(|c| row(&c)),
    );
    detail.extend(
        conns
            .iter()
            .filter(|c| c["made"] != "drawn" && c["made"] != "mate" && c["made"] != "not drawn")
            .map(|c| row(&c)),
    );
    check(
        "routed",
        "Every tube connection the machine owes, made as a real 3-D path",
        "goal",
        missing.is_empty(),
        format!("{}/{} made", conns.len() - missing.len(), conns.len()),
        "every connection made",
        detail,
    )
}
fn located(m: &Value) -> Value {
    let mut total = 0;
    let mut bad = Vec::new();
    for (n, f) in obj(&m["frames"]) {
        let ports = f.get("ports").unwrap_or(&f);
        for (p, v) in obj(ports) {
            total += 1;
            let (pos, diam) = if v.is_object() {
                (&v["pos"], &v["diam"])
            } else {
                (&v[0], &v[2])
            };
            if pos.is_null() || diam.is_null() {
                bad.push(format!("{n}.{p}"));
            }
        }
    }
    check(
        "located",
        "Every port a placed body declares is carried into world",
        "goal",
        bad.is_empty(),
        format!("{}/{} located", total - bad.len(), total),
        "every declared port positioned and sized",
        bad,
    )
}
fn tube_anchored(m: &Value) -> Result<(Value, BTreeMap<String, f64>)> {
    let mut stations = array(&m["tube_anchors"]).to_vec();
    stations.extend(array(&m["cap_tube_anchors"]).iter().cloned());
    let spans = routes::unsupported(
        &m["runs"],
        &json!(stations),
        &m["developed_anchor_stations"],
        m.get("reservoir_a_route_specs")
            .unwrap_or(&m["native_route_specs"]),
    )?;
    let cap = m["tube_anchor_span"]
        .as_f64()
        .context("tube anchor span is the construction's stated scalar")?;
    let mut over = spans
        .iter()
        .filter(|(_, s)| **s > cap)
        .map(|(id, s)| (*s, id.clone()))
        .collect::<Vec<_>>();
    over.sort_by(|a, b| b.0.total_cmp(&a.0).then(b.1.cmp(&a.1)));
    let mut anchored = array(&m["tube_anchor_sites"])
        .iter()
        .map(|r| string(&r[0]))
        .collect::<BTreeSet<_>>();
    let mut paired = names(&m["paired_anchor_runs"]);
    let drawn = array(&m["runs"])
        .iter()
        .map(|r| string(&r["id"]))
        .collect::<BTreeSet<_>>();
    for (_, r) in obj(&m["reservoir_anchor_datums"]) {
        paired.extend(
            strings(&r["routes_west_to_east"])
                .into_iter()
                .filter(|id| drawn.contains(id)),
        );
    }
    anchored.extend(paired.iter().cloned());
    let mut detail = over
        .iter()
        .map(|(s, rid)| {
            format!(
                "{rid}: {s:.1} mm unheld, {:.1} over{}",
                s - cap,
                if anchored.contains(rid) {
                    " — anchored once already"
                } else {
                    ""
                }
            )
        })
        .collect::<Vec<_>>();
    for id in &anchored {
        let s = spans
            .get(id)
            .with_context(|| format!("anchor names undrawn run {id}"))?;
        detail.push(format!(
            "{id}: {s:.1} mm, held at {}",
            if paired.contains(id) {
                "two paired lid seats (nominal restraint geometry)"
            } else {
                "its anchor"
            }
        ));
    }
    Ok((
        check(
            "tube-anchored",
            "No run goes further than one span with nothing holding it",
            "goal",
            over.is_empty(),
            format!(
                "{}/{} within span, 0 left loose",
                spans.len() - over.len(),
                spans.len()
            ),
            &format!("{cap:.0} mm between held points"),
            detail,
        ),
        spans,
    ))
}
pub fn clearance_only(w: &mut World, spec: &Value) -> Result<Value> {
    let rules: Value = serde_json::from_str(include_str!("machine_check_rules.json"))?;
    let m = &spec["metadata"];
    let (clearances, lanes) = geometry::clearance(w, m, &rules)?;
    let reading = geometry::Readings {
        clashes: vec![],
        unanswered: vec![],
        contacts: json!({}),
        clearances,
        lanes,
    };
    let bends = routes::bends(&m["runs"], &m["native_route_specs"])?;
    let conns = connections(m, &rules)?;
    let mounts = mounts(w, m, &rules);
    let (placed, room) = seats(w, m);
    let blocked = obj(&m["blocked_runs"]);
    let short = blocked
        .iter()
        .map(|(n, v)| format!("{n}: {}", string(v)))
        .collect::<Vec<_>>();
    let (anchor, spans) = tube_anchored(m)?;
    let checks = vec![
        coverage(w, &mounts),
        room,
        clearance(&reading),
        bed_fit(w, m),
        check(
            "runs-drawn",
            "Every authored run is drawn as its author asked",
            "gate",
            short.is_empty(),
            format!(
                "{}/{} as drawn",
                array(&m["runs"]).len().saturating_sub(short.len()),
                array(&m["runs"]).len()
            ),
            "0 short",
            short,
        ),
        bend_check(&bends),
        mounted(&mounts, &rules)?,
        placed,
        routed(&conns, &rules),
        located(m),
        anchor,
    ];
    Ok(
        json!({"selected_checks":checks,"bends":bends,"connections":conns,"clearances":reading.clearances,"lanes":reading.lanes,"unsupported_spans":spans,"mounts":mounts,"rides":rules["rides"]}),
    )
}
pub fn build(w: &mut World, spec: &Value) -> Result<Value> {
    let rules: Value = serde_json::from_str(include_str!("machine_check_rules.json"))?;
    let m = &spec["metadata"];
    let readings = geometry::read(w, m, &rules)?;
    if spec["mode"] == "geometry" {
        return Ok(
            json!({"clashes":readings.clashes,"unanswered":readings.unanswered,"contact_readings":readings.contacts,"clearances":readings.clearances,"lanes":readings.lanes}),
        );
    }
    let bends = routes::bends(&m["runs"], &m["native_route_specs"])?;
    let conns = connections(m, &rules)?;
    let mounts = mounts(w, m, &rules);
    let (placed, room) = seats(w, m);
    let blocked = obj(&m["blocked_runs"]);
    let short = blocked
        .iter()
        .map(|(n, v)| format!("{n}: {}", string(v)))
        .collect::<Vec<_>>();
    let mut checks = vec![
        coverage(w, &mounts),
        room,
        pack_closes(&readings),
        clearance(&readings),
        bed_fit(w, m),
    ];
    for b in array(&m["bounds"]) {
        let kind = b["kind"].as_str().unwrap_or("gate");
        let status = b["status"]
            .as_str()
            .unwrap_or(if b["ok"] == true { "pass" } else { "fail" });
        let mut row = b.clone();
        row["kind"] = json!(kind);
        row["status"] = json!(status);
        row["active"] = json!(b["active"].as_bool().unwrap_or(true) && kind != "goal");
        if !b["detail"].is_array() {
            row["detail"] = json!([]);
        }
        row.as_object_mut().unwrap().remove("ok");
        checks.push(row);
    }
    checks.push(check(
        "runs-drawn",
        "Every authored run is drawn as its author asked",
        "gate",
        short.is_empty(),
        format!(
            "{}/{} as drawn",
            array(&m["runs"]).len().saturating_sub(short.len()),
            array(&m["runs"]).len()
        ),
        "0 short",
        short,
    ));
    checks.push(bend_check(&bends));
    checks.push(mounted(&mounts, &rules)?);
    checks.push(placed);
    checks.push(routed(&conns, &rules));
    checks.push(located(m));
    let (anchor, spans) = tube_anchored(m)?;
    checks.push(anchor);
    checks.push(json!({"id":"gas-chain-qualified","label":"Warm gas fitting dimensions and made-up fit qualified","kind":"goal","status":"warn","value":"Compact gas references; physical fit pending","target":"qualify actual compact regulator/check and trimmed insertions","detail":["PISCO is the selected 0.3 MPa regulator; its purchased-body fit remains unqualified.","Both check positions use the purchased neoFit ACHV44-E reference, with published dimensions and explicitly estimated socket details.","Stem insertions retain the receiving-family estimates stated in above-core.json.","Geometry establishes neither sealing, pull-off retention nor pressure suitability."],"active":false}));
    let gates = checks
        .iter()
        .filter(|r| r["kind"] == "gate")
        .all(|r| r["status"] == "pass");
    let sizes = size_rows(w);
    Ok(
        json!({"scorecard":{"gatesPass":gates,"size":sizes,"checks":checks},"bends":bends,"connections":conns,"sizes":sizes,"clashes":readings.clashes,"unanswered":readings.unanswered,"contact_readings":readings.contacts,"clearances":readings.clearances,"lanes":readings.lanes,"unsupported_spans":spans,"mounts":mounts,"rides":rules["rides"]}),
    )
}
