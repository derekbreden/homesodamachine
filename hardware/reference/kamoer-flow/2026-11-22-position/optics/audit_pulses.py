#!/usr/bin/env python3
"""Measure equal-on-time schedules with the held-out liquid strip and pair conditions within the physical block and head."""
import argparse
import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import t

import outer_check
import reset_check
from audit_reset import BASE, STRETCH
from reduce import round_row, stats, write_table

CONDITIONS=("single","close","medium","long")


def trial_records(logs,review):
    accepted_review=review.get("observation",{})
    trials={}
    for path in sorted(logs.glob("*.jsonl")):
        phase=None
        for line in path.read_text().splitlines():
            ev=json.loads(line);kind=ev['event']
            if kind=="pulse_prediction":
                phase={"prediction":ev,"source_log":path.name,"gates":[],"done":[]};trials[ev["label"]]=phase
            elif phase is not None and kind=="pulse_gate" and ev.get("label")==phase["prediction"]["label"]:
                phase["gates"].append(ev)
            elif phase is not None and kind=="rx" and f"pump {phase['prediction']['head']} done after " in ev.get("line",""):
                phase["done"].append(ev["line"])
            elif phase is not None and kind=="pulse_score" and ev["label"]==phase["prediction"]["label"]:
                phase["score"]=ev;phase=None
            elif kind in ("halt","session_end"):
                phase=None
    if accepted_review:
        trial=trials.get(accepted_review["label"])
        if trial is not None and "score" not in trial:
            trial["score"]=accepted_review;trial["reviewed"]=True
    return trials


def summary(values):
    a=np.asarray(values,dtype=float);n=len(a)
    if not n:return {"n":0}
    out={"n":n,"mean_px":float(np.mean(a)),"median_px":float(np.median(a)),"min_px":float(a.min()),"max_px":float(a.max())}
    if n>=2:
        sd=float(np.std(a,ddof=1));half=float(t.ppf(.975,n-1)*sd/np.sqrt(n))
        out["sample_sd_px"]=sd;out["paired_or_condition_mean_t95_px"]=[out["mean_px"]-half,out["mean_px"]+half]
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("record",type=Path);p.add_argument("--windows",type=Path);p.add_argument("--logs",type=Path);p.add_argument("--review",type=Path)
    p.add_argument("--output",type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    raw_path=lambda name:args.windows/name/"average.png" if args.windows else args.record/"frames"/(name+".png")
    base=reset_check.luma(raw_path(BASE));review_path=args.review or args.record/"pulse-image-review.json"
    review=json.loads(review_path.read_text()) if review_path.exists() else {}
    trials=trial_records(args.logs or args.record/"logs",review);rows=[];cells=defaultdict(list)
    scale=STRETCH["heldout_shoulder"]
    for name,current in trials.items():
        spec=current["prediction"];score=current.get("score");gates=current['gates'];count=spec["count"]
        expected=set(range(1,count+1));logged={v["pulse"] for v in gates}
        row={"trial":name,"block":spec["block"],"head":spec["head"],"condition":spec["condition"],"expected_gates":count,
             "recorded_gates":len(logged),"board_done_messages":len(current['done']),"total_logged_on_ms":sum(v["board_ms"] for v in gates),
             "width_ms":spec["width_ms"],"gap_ms":spec["gap_ms"],"start_endpoint":spec["pre_endpoint"],"start_operational_px":spec["pre_px"]}
        if logged!=expected or len(current['done'])!=count:
            row["status"]="incomplete gate train";rows.append(row);continue
        if score is None:
            row["status"]="complete train without accepted settled observation";rows.append(row);continue
        row["end_endpoint"]=score["observed_endpoint"]
        if not raw_path(row["start_endpoint"]).is_file() or not raw_path(row["end_endpoint"]).is_file():
            row["status"]="settled photograph not yet archived";rows.append(row);continue
        pre=outer_check.displacement(reset_check.luma(raw_path(row["start_endpoint"])),base)
        post=outer_check.displacement(reset_check.luma(raw_path(row["end_endpoint"])),base)
        row["operational_dose_px"]=score["positive_dose_px"]
        row["pre_mad_px"]=pre.get("mad_px");row["post_mad_px"]=post.get("mad_px")
        if not pre.get("ok") or not post.get("ok"):
            row["status"]="held-out surface ambiguous";rows.append(row);continue
        a=dict(pre["samples"]);b=dict(post["samples"]);common=sorted(a.keys()&b.keys())
        sign=1 if spec["head"]=="A" else -1
        paired=np.array([sign*(b[x]-a[x])/scale for x in common])
        dose=sign*(post["shoulder_delta_px"]-pre["shoulder_delta_px"])/scale
        row.update({"status":"complete after image review" if current.get("reviewed") else "complete",
                    "heldout_start_px":pre["shoulder_delta_px"]/scale,"heldout_end_px":post["shoulder_delta_px"]/scale,
                    "heldout_directional_dose_px":dose,"matching_patches":len(common),"matched_patch_dose_median_px":float(np.median(paired)),
                    "matched_patch_dose_mad_px":float(np.median(abs(paired-np.median(paired)))),"heldout_minus_operational_px":dose-score["positive_dose_px"]})
        cells[row["head"],row["block"],row["condition"]].append(row)
        rows.append(round_row(row))
    # A partial attempt has no accepted dose. Two completed entries in one cell require explicit adjudication.
    if any(len(v)>1 for v in cells.values()):
        raise ValueError(f"Duplicate completed trial cells: {[key for key,v in cells.items() if len(v)>1]}")
    conditions=[];contrasts=[];overall=[]
    for head in ("A","B"):
        blocks=sorted({b for h,b,c in cells if h==head})
        for condition in CONDITIONS:
            selected=[cells[head,b,condition][0] for b in blocks if (head,b,condition) in cells]
            for metric in ("heldout_directional_dose_px","operational_dose_px"):
                conditions.append({"head":head,"condition":condition,"readout":metric,**summary([r[metric] for r in selected])})
        for low,high in itertools.combinations(CONDITIONS,2):
            # Relative to single, report train minus single. Between trains, report the shorter pause minus the longer pause.
            a,b=(high,low) if low=="single" else (low,high)
            collected=[]
            for block in blocks:
                if (head,block,a) not in cells or (head,block,b) not in cells:continue
                first=cells[head,block,a][0];second=cells[head,block,b][0]
                rec={"head":head,"block":block,"condition":a,"minus":b,"first_trial":first["trial"],"second_trial":second["trial"],
                     "heldout_contrast_px":first["heldout_directional_dose_px"]-second["heldout_directional_dose_px"],
                     "operational_contrast_px":first["operational_dose_px"]-second["operational_dose_px"],
                     "heldout_start_difference_px":first["heldout_start_px"]-second["heldout_start_px"]}
                collected.append(rec);contrasts.append(round_row(rec))
            for metric in ("heldout_contrast_px","operational_contrast_px"):
                overall.append({"head":head,"condition":a,"minus":b,"readout":metric,**summary([r[metric] for r in collected])})
    write_table(args.output/"reset-pulse-trials.csv",rows)
    write_table(args.output/"reset-pulse-block-contrasts.csv",contrasts)
    result={"coordinate":"Held-out left-shoulder camera pixels divided by the frozen qualification stretch, matching the x980 operating coordinate.",
            "qualification_stretch":scale,"analyzed_trains":sum(len(v) for v in cells.values()),"status":[{"trial":r['trial'],"status":r['status']} for r in rows if r['status']!="complete"],
            "conditions":conditions,"within_block_differences":overall,
            "spatial_diagnostics":{
                "heldout_minus_operational_per_train_px":stats(r.get("heldout_minus_operational_px") for r in rows),
                "absolute_difference_between_readers_for_paired_contrasts_px":stats(abs(r["heldout_contrast_px"]-r["operational_contrast_px"]) for r in contrasts),
                "within_train_matched_patch_mad_px":stats(r.get("matched_patch_dose_mad_px") for r in rows)},
            "uncertainty":"The independent observation is one completed train. Intervals are descriptive Student-t intervals for the mean of the observed blocks or paired block contrasts. Repeated photographs and neighboring patches do not add experimental replicates. Start-level differences are retained in the paired table."}
    (args.output/"reset-pulse-summary.json").write_text(json.dumps(result,indent=2)+"\n")


if __name__=="__main__":main()
