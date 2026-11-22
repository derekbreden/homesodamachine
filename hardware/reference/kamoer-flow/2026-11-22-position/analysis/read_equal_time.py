"""Compare equal-on-time motor commands against their photographed, settled changes in syrup level."""
import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def stats(values):
    values = list(values)
    if not values:
        return {"n": 0}
    return {"n": len(values), "mean": statistics.mean(values), "median":statistics.median(values),
            "min":min(values), "max":max(values),
            "sample_sd":statistics.stdev(values) if len(values)>1 else None}


def summarize(record):
    design=json.loads((record/"rewired-pauses.json").read_text())
    rows=[]; skipped=[]
    for journal in sorted((record/"logs").glob("pulse-r*.jsonl")):
        events=[json.loads(line) for line in journal.read_text().splitlines()]
        endpoints={e["label"]:e["readings"] for e in events if e["event"]=="endpoint"}
        gates=defaultdict(list)
        for e in events:
            if e["event"]=="pulse_gate":gates[e["label"]].append(e)
        predictions={e["label"]:e for e in events if e["event"]=="pulse_prediction"}
        scored={e["label"]:e for e in events if e["event"]=="pulse_score"}
        reviewed_path=record/"pulse-image-review.json"
        reviewed=json.loads(reviewed_path.read_text())["observation"] if reviewed_path.exists() else {}
        if reviewed.get("label") in predictions:
            scored[reviewed["label"]]=reviewed
        for label,p in predictions.items():
            receipts=gates[label]
            if label not in scored:
                skipped.append({"label":label,"receipts":len(receipts),"expected":p["count"],
                                "recorded_errors":[e["reason"] for e in events if e["event"]=="halt"]})
                continue
            obs=scored[label]
            if len(receipts)!=p["count"] or sum(g["board_ms"] for g in receipts)!=400:
                raise ValueError(label)
            if p["mono_ns"]>=receipts[0]["tx_ns"] or obs["mono_ns"]<=receipts[-1]["done_ack_ns"]:
                raise ValueError("Trial timestamps out of order "+label)
            before=endpoints[p["pre_endpoint"]]; after=endpoints[obs["observed_endpoint"]]
            sign=1 if p["head"]=="A" else -1
            row={"label":label,"endpoint_review":"offline" if label==reviewed.get("label") else "at_capture","block":p["block"],"head":p["head"],"condition":p["condition"],
                 "count":p["count"],"width_ms":p["width_ms"],"gap_ms":p["gap_ms"],
                 "board_total_ms":sum(r["board_ms"] for r in receipts),"first_start_px":p["pre_px"],
                 "observed_end_px":obs["post_px"],"positive_dose_px":obs["positive_dose_px"],
                 "null_dose_px":sign*p["null_delta_px"],
                 "mean_intergate_off_ms":None if len(receipts)==1 else statistics.mean(
                     (n["tx_ns"]-g["tx_ns"])/1e6-g["board_ms"] for g,n in zip(receipts,receipts[1:])),
                 "right_ml":None,"projected_left_ml":None}
            for site,col in (("right","right_ml"),("projected_left","projected_left_ml")):
                if all("nominal_ml" in x.get(site,{}) for x in (before,after)):
                    row[col]=sign*(before[site]["nominal_ml"]-after[site]["nominal_ml"])
            rows.append(row)
    by_setting=[]
    contrasts=[]
    held=[]
    for head in ("A","B"):
        for cond in design["conditions"]:
            group=[r for r in rows if r["head"]==head and r["condition"]==cond]
            fields=["positive_dose_px","right_ml","projected_left_ml","first_start_px","mean_intergate_off_ms"]
            value={k:stats(r[k] for r in group if r[k] is not None) for k in fields}
            by_setting.append(dict(head=head,condition=cond,**value))
            train=[r["positive_dose_px"] for r in group if r["block"]<=2]
            if not train:continue
            for r in group:
                if r["block"]<=2:continue
                held.append(dict(label=r["label"],head=head,condition=cond,block=r["block"],
                                 training_n=len(train),observed_px=r["positive_dose_px"],
                                 setting_prediction_px=statistics.mean(train),null_prediction_px=r["null_dose_px"],
                                 setting_error_px=statistics.mean(train)-r["positive_dose_px"],
                                 null_error_px=r["null_dose_px"]-r["positive_dose_px"]))
        for c,d in (("close","single"),("medium","single"),("long","single"),("close","medium"),("close","long"),("medium","long")):
            pairs=[]
            for block in sorted(set(z["block"] for z in rows)):
                part={r["condition"]:r for r in rows if r["block"]==block and r["head"]==head}
                if c not in part or d not in part:continue
                a,b=part[c],part[d]
                items={"block":block,"labels":[a["label"],b["label"]]}
                for k in ("positive_dose_px","right_ml","projected_left_ml","first_start_px"):
                    items[k]=None if a[k] is None or b[k] is None else a[k]-b[k]
                pairs.append(items)
            contrasts.append({"head":head,"first_condition":c,"second_condition":d,"matched_blocks":pairs,
               "first_minus_second":{k:stats(z[k] for z in pairs if z[k] is not None) for k in
                                     ("positive_dose_px","right_ml","projected_left_ml","first_start_px")}})
    return rows,dict(scope="Restored tube ends and electrical connections. Positive dose means cup emptying on A or filling on B. Optical-volume units are nominal. The two printed scales share the same cup.",
        design="Matched comparisons subtract dose within head and block. The conditional model fits separate means on the first two blocks and is evaluated on the later two. This secondary split is retrospective; the equal-on-time null and ordering were frozen before any trains ran.",
        complete=len(rows),unscored=skipped,settings=by_setting,paired_contrasts=contrasts,
        heldout_errors_px={h:{k:stats(abs(r[k]) for r in held if r["head"]==h) for k in ("setting_error_px","null_error_px")} for h in ("A","B")},
        heldout=held)


def plot(rows, destination):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    order=["single","close","medium","long"]
    names=["Continuous","50 ms","250 ms","900 ms"]
    fig,axs=plt.subplots(1,2,figsize=(9,4.7),sharey=True,layout="constrained")
    for ax,head,col in zip(axs,"AB",["#116a71","#9c4827"]):
        part=[r for r in rows if r["head"]==head]
        for block in sorted(set(r["block"] for r in part)):
            block_rows=[r for r in part if r["block"]==block]
            keep=sorted(block_rows,key=lambda r:order.index(r["condition"]))
            ax.plot([order.index(r["condition"]) for r in keep],[r["positive_dose_px"] for r in keep],
                color=col,alpha=.38,marker="o",lw=1)
        means=[statistics.mean(g) if (g:=[r["positive_dose_px"] for r in part if r["condition"]==cond]) else np.nan for cond in order]
        ax.plot(range(4),means,color=col,lw=2.5,marker="D",label="Block mean")
        if part:ax.axhline(part[0]["null_dose_px"],ls="--",color="#585858",lw=1,label="Single-shot prediction")
        ax.set_title("A  ·  draws from cup" if head=="A" else "B  ·  refills cup")
        ax.set_xticks(range(4),names,rotation=12);ax.grid(axis="y",alpha=.22);ax.set_xlabel("Pause between 100 ms pulses")
        ax.spines[["right","top"]].set_visible(False)
    axs[0].set_ylabel("Settled liquid movement (camera pixels)");axs[1].legend(fontsize=8,loc="best")
    fig.suptitle("Equal total drive time, different pulse spacing",fontsize=15)
    fig.savefig(destination,dpi=170);plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("record",type=Path);p.add_argument("--out",type=Path,required=True);p.add_argument("--plot",action="store_true")
    a=p.parse_args();a.out.mkdir(exist_ok=True,parents=True)
    rows,summary=summarize(a.record)
    if not rows:raise RuntimeError("No completed equal-time trial")
    with (a.out/"equal-time-trials.csv").open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    (a.out/"equal-time-results.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
    if a.plot:plot(rows,a.out/"equal-time-doses.png")
    print(len(rows),"completed equal-time schedules")

if __name__=="__main__":main()
