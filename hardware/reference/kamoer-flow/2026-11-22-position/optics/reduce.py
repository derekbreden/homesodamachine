#!/usr/bin/env python3
"""Replay settled optical endpoints and score held-out target forecasts without feeding them into the image reader."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

import independent
import register_cup

HERE = Path(__file__).resolve().parent


def write_table(path, records):
    if not records:
        return
    fields = list(dict.fromkeys(k for row in records for k in row))
    with path.open("w",newline="") as stream:
        writer = csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def round_row(row):
    return {k:round(float(v),5) if isinstance(v,(float,np.floating)) else v for k,v in row.items()}


def input_paths(name, args):
    if args.windows is not None:
        return args.windows/name/"average.png", args.windows/name/"color.png"
    return args.frames/(name+".png"), args.ink/(name+".png")


def read_endpoints(labels, args, reference, metadata):
    endpoints, data = [], {}
    for name in sorted(labels):
        gray, color = input_paths(name,args)
        if not (gray.is_file() and color.is_file()):
            continue
        result = independent.read_image(gray,reference,metadata,color)
        compact = {"endpoint":name}
        for side, sight in result["sightlines"].items():
            checks=result["registration"]["checks"][side]
            withheld=checks["withheld_marks_minus_dry_px"]
            compact.update({
                side+"_raw_y":sight["raw_row"], side+"_cup_y":sight["row"],
                side+"_nominal_ml":sight["nominal_ml"], side+"_ink_dy":sight["print_dy"],
                side+"_dry_max_residual_px":checks["dry_fit_max_residual_px"],
                side+"_onecup_check_px":withheld.get(964 if side=="right" else 979),
                side+"_patches":sight["patches"], side+"_interpolated_x":sight["interpolates_fixed_x"],
                side+"_station_median_abs_residual_px":sight["median_patch_residual_px"],
                side+"_edge_dark_fraction_y":sight["rows_at_brightness_fractions"][0],
                side+"_edge_light_fraction_y":sight["rows_at_brightness_fractions"][2],
            })
        data[name]=compact
        endpoints.append(round_row(compact))
    return data, endpoints


def read_events(directory, prefixes):
    episodes, targets = {}, []
    for path in sorted(directory.glob("*.jsonl")):
        if prefixes and not any(path.name.startswith(s) for s in prefixes):
            continue
        for line in path.read_text().splitlines():
            event = json.loads(line)
            name, kind = event.get("label"), event["event"]
            if kind == "target_score":
                targets.append(event)
            if name and kind in ("prediction","position_prediction","observation","position_observation","optical_rejection"):
                episode=episodes.setdefault(name,{"log":path.name,"label":name})
                episode[kind]=event
    return episodes,targets


def pre_spec(episode):
    return episode.get("position_prediction",episode.get("prediction",{}))


def trial_records(episodes, data):
    records=[]
    for label,episode in sorted(episodes.items()):
        before,after=data.get(label+"-pre"),data.get(label+"-post")
        if before is None or after is None:
            continue
        spec=pre_spec(episode)
        coordinate=spec.get("coordinate","raw")
        basis="cup" if coordinate=="registered" else "raw"
        target=spec.get("requested_y",spec.get("requested_right_y"))
        predicted=spec.get("predicted_y",spec.get("predicted_right_y"))
        obs=episode.get("position_observation",episode.get("observation",episode.get("optical_rejection",{})))
        pre,post=spec.get("pre",{}),obs.get("post",{})
        row={"label":label,"log":episode['log'],"kind":spec.get("kind"),"head":spec.get("head"),
             "gate_ms":spec.get("gate_ms"),"count":spec.get("count"),"off_ms":spec.get("off_ms"),
             "pair":spec.get("pair"),"coordinate":coordinate,"target_y":target,"predicted_y":predicted}
        for side in independent.SITES:
            for system in ("raw","cup"):
                field=f"{side}_{system}_y"
                row[f"before_{field}"]=before[field]
                row[f"after_{field}"]=after[field]
                row[f"delta_{field}"]=after[field]-before[field]
            row[f"{side}_signed_change_ml"]=after[f"{side}_nominal_ml"]-before[f"{side}_nominal_ml"]
            row[f"{side}_operational_pre_y"]=pre.get(side+"_y")
            row[f"{side}_operational_post_y"]=post.get(side+"_y")
            if pre.get(side+"_y") is not None and post.get(side+"_y") is not None:
                row[f"{side}_operational_minus_independent_delta_px"]=(post[side+"_y"]-pre[side+"_y"])-row[f"delta_{side}_raw_y"]
        row["signed_cup_change_ml"]=np.mean([row[f"{s}_signed_change_ml"] for s in independent.SITES])
        row["two_scale_change_difference_ml"]=row["right_signed_change_ml"]-row["left_signed_change_ml"]
        if target is not None:
            row["independent_target_error_px"]=after[f"right_{basis}_y"]-target
        if predicted is not None:
            row["independent_prediction_error_px"]=after[f"right_{basis}_y"]-predicted
            if pre.get("right_y") is not None:
                op_pre=pre["right_y"] if basis=="raw" else pre.get("ink",{}).get("right",{}).get("cup_y")
                if op_pre is not None:
                    row["independent_delta_prediction_error_px"]=row[f"delta_right_{basis}_y"]-(predicted-op_pre)
        records.append(round_row(row))
    return records


def destination_scores(targets, data, episodes):
    rows=[]
    for t in targets:
        basis="cup" if t["coordinate"]=="registered" else "raw"
        first=t["first_label"];last=t["final_label"]
        a=data.get(first+"-post");b=data.get(last+"-post")
        if a is None or b is None:
            continue
        # A small fixed estimator offset can affect an absolute target. The differential scores carry each reader's measured origin.
        initial=data.get(first+"-pre");spec=pre_spec(episodes[first])
        op_before=spec["pre"]["right_y"] if basis=="raw" else spec["pre"]["ink"]["right"]["cup_y"]
        common_offset=initial[f"right_{basis}_y"]-op_before
        want=t["requested_y"]
        opfirst=t["first"]["right_y"] if basis=="raw" else t["first"]["ink"]["right"]["cup_y"]
        opfinal=t["final"]["right_y"] if basis=="raw" else t["final"]["ink"]["right"]["cup_y"]
        rows.append(round_row({"pair":t["pair"],"coordinate":t["coordinate"],"target_y":want,"first":first,"final":last,
                              "corrections":t["corrections"],"operational_first_error_px":opfirst-want,"operational_final_error_px":opfinal-want,
                              "independent_first_error_px":a[f"right_{basis}_y"]-want,
                              "independent_final_error_px":b[f"right_{basis}_y"]-want,
                              "independent_first_error_from_own_origin_px":a[f"right_{basis}_y"]-want-common_offset,
                              "independent_final_error_from_own_origin_px":b[f"right_{basis}_y"]-want-common_offset}))
    return rows


def stats(values):
    values=np.array([v for v in values if v is not None],dtype=float)
    if not values.size:return {"n":0}
    return {"n":int(values.size),"min":float(values.min()),"max":float(values.max()),"median":float(np.median(values)),
            "mean_absolute":float(np.abs(values).mean()),"p90_absolute":float(np.percentile(abs(values),90)),"max_absolute":float(abs(values).max())}


def summarize(endpoints,trials,scores):
    blanks=[r for r in trials if r["kind"]=="blank"]
    projected=[r for r in trials if r.get("label","").startswith("destination-")]
    drift={s:{key:stats(v.get(s+key) for v in endpoints) for key in ("_ink_dy","_dry_max_residual_px","_onecup_check_px")} for s in independent.SITES}
    return {
        "settled_endpoints":len(endpoints),"trial_pairs":len(trials),"target_pairs":len(scores),
        "nominal_absolute_right_minus_left_ml":stats(z["right_nominal_ml"]-z["left_nominal_ml"] for z in endpoints),
        "mark_registration":drift,
        "explicit_no_drive_changes":{
            "right_raw_px":stats(z['delta_right_raw_y'] for z in blanks),"left_raw_px":stats(z["delta_left_raw_y"] for z in blanks),
            "right_cup_px":stats(z['delta_right_cup_y'] for z in blanks),"left_cup_px":stats(z["delta_left_cup_y"] for z in blanks),
            "nominal_ml":stats(z['signed_cup_change_ml'] for z in blanks)},
        "disjoint_right_raw_vs_operational_delta_px":stats(z.get("right_operational_minus_independent_delta_px") for z in trials),
        "different_front_scales_signed_change_difference_ml":stats(z['two_scale_change_difference_ml'] for z in trials),
        "held_out_disjoint_right_raw_vs_operational_delta_px":stats(z.get("right_operational_minus_independent_delta_px") for z in projected),
        "destination":{coordinate:{k:stats(s[k] for s in scores if s['coordinate']==coordinate) for k in [
            "independent_first_error_px","independent_final_error_px","independent_first_error_from_own_origin_px","independent_final_error_from_own_origin_px"]}
            for coordinate in ["raw","registered"]},
        "interpretation":"All patches in one exposure observe the same cup. Separate command pairs are the repeat unit. Side-to-side agreement tests regional sensitivity. Every nominal volume shares the cup's unknown calibration and perspective; observed idle variation is local to these conditions."
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument("--windows",type=Path,help="original window directories")
    source.add_argument("--frames",type=Path,help="packed grayscale endpoint PNGs")
    p.add_argument("--ink",type=Path,help="packed RGB ink PNGs named like the grayscale frames")
    p.add_argument("--logs",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--log-prefix",action="append",default=[],help="select trials belonging to the reference arrangement")
    p.add_argument("--reference",type=Path,default=HERE/"registration.npz")
    args=p.parse_args()
    if args.frames is not None and args.ink is None:
        p.error("--frames needs --ink")
    episodes,targets=read_events(args.logs,args.log_prefix)
    labels={k+s for k in episodes for s in ("-pre","-post")}
    metadata=json.loads(args.reference.with_suffix(".json").read_text())
    with np.load(args.reference) as saved:
        data,ends=read_endpoints(labels,args,dict(saved),metadata)
    trials=trial_records(episodes,data)
    scores=destination_scores(targets,data,episodes)
    args.output.mkdir(parents=True,exist_ok=True)
    write_table(args.output/"optical-endpoints.csv",ends)
    write_table(args.output/"optical-trials.csv",trials)
    write_table(args.output/"optical-targets.csv",scores)
    (args.output/"optical-summary.json").write_text(json.dumps(summarize(ends,trials,scores),indent=2)+"\n")


if __name__=="__main__":
    main()
