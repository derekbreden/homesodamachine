#!/usr/bin/env python3
"""Audit the fresh electrical-direction checks and the subsequently requested destinations from the saved photographs."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import independent
import outer_check
import reset_check
from reduce import round_row, stats, write_table

HERE=Path(__file__).resolve().parent
BASE="after-user-reset-inspect"
IDENTIFIERS=["rewired-a-00-idle","rewired-a-01-A","rewired-a-02-B"]
RETURN_LABELS=["return-to-reference-before","return-to-reference-after1","return-to-reference-at-rest"]
# The design froze these ratios on the qualification strokes before the destination block.
STRETCH={"center":.82,"right":.91,"outer_right":1.31,"heldout_shoulder":1.0027992727774695}


def paths(name,args):
    if args.windows is not None:
        return args.windows/name/"average.png",args.windows/name/"color.png"
    return args.record/"frames"/(name+".png"),args.record/"ink"/(name+".png")


def plot_direction(readings,args,out):
    width,height=1100,685
    image=Image.new("RGB",(width,height),"#f5f3ef");draw=ImageDraw.Draw(image)
    def text(pos,words,size,fill="#182724"):
        draw.text(pos,words,fill=fill,font=ImageFont.load_default(size=size))
    text((28,18),"The liquid level fell on A and rose on B",33)
    text((29,61),"Separate clear areas of the cup, before and after each settled 600 ms shot",17,"#41534b")
    ref,_=paths(BASE,args);overview=reset_check.luma(args.reference_luma or ref)
    x0,y0=independent.CROP[:2]
    def visible(part):
        return Image.fromarray(np.uint8(np.clip((np.asarray(part).astype(float)-18)*2.24,0,255))).convert("RGB")
    context=visible(overview[840-y0:1050-y0,950-x0:2050-x0])
    context=context.resize((1028,171),Image.Resampling.BOX)
    image.paste(context,(36,94));draw=ImageDraw.Draw(image)
    for x,y,caption in [(980,988,"Left clear glass"),(1990,931,"Outer right glass")]:
        px=36+(x-950)*1028/1100;py=94+(y-840)*171/210
        draw.rectangle((px-15,py-10,px+16,py+11),outline="#69f2c8",width=2)
        label_x=max(52,min(px-8,850));draw.rectangle((label_x-3,103,label_x+139,123),fill="#172521")
        text((label_x,104),caption,15,"#dcfff4")
    panel_x=[154,385,652,883];pw,ph=196,123
    for x,lab in zip(panel_x,["Left before","Left after","Right before","Right after"]):text((x,281),lab,18)
    for ri,(sid,head,word) in enumerate([(IDENTIFIERS[1],"A","down"),(IDENTIFIERS[2],"B","up")]):
        py=311+ri*171
        text((28,py+18),"Head "+head,22);text((28,py+50),"600 ms",16,"#53605b")
        for group,x,base_y,idx in [("left_clear",980,994,0),("outer_right",1990,940,2)]:
            pre=readings[sid+"-pre"][group];post=readings[sid+"-post"][group]
            for j,phase in enumerate(("pre","post")):
                name=sid+"-"+phase;gray,_=paths(name,args);a=reset_check.luma(gray)
                xl=x-28;yt=base_y-25
                panel=visible(a[yt-y0:yt-y0+50,xl-x0:xl-x0+80]).resize((pw,ph),Image.Resampling.BICUBIC)
                px=panel_x[idx+j];image.paste(panel,(px,py));d=ImageDraw.Draw(image)
                y=py+((pre if j==0 else post)['raw_row']-yt)*ph/50.
                cx=px+(x-xl)*pw/80.
                if j:
                    yprev=py+(pre['raw_row']-yt)*ph/50.
                    for xx in range(px+5,px+pw-4,13):d.line((xx,yprev,min(xx+6,px+pw-4),yprev),fill="#eeca66",width=1)
                d.line((cx-18,y,cx-4,y),fill="#66ffc5",width=2);d.line((cx+4,y,cx+18,y),fill="#66ffc5",width=2)
                d.ellipse((cx-3,y-3,cx+3,y+3),outline="#66ffc5",width=1)
            change=post["raw_row"]-pre["raw_row"]
            text((panel_x[idx],py+128),f"{abs(change):.1f} camera pixels {word}",17,"#126449")
        draw=ImageDraw.Draw(image)
    draw.line((30,651,1071,651),fill="#b5b9ac",width=1)
    text((31,659),"Green marks the measured contact. Gold marks its previous row. Each pair uses the same fixed crop and brightness scale.",14,"#41534b")
    image.save(out,quality=93,subsampling=0)


def target_events(logdir):
    labels=set();events=[]
    for file in sorted(logdir.glob("*.jsonl")):
        rows=[json.loads(x) for x in file.read_text().splitlines()]
        accepted=[v for v in rows if v["event"]=="endpoint" and "left_clear" in v.get("readings",{})]
        if not accepted or not any(v["event"] in ("first_score","final_score","blank") for v in rows):continue
        labels.update(v["label"] for v in accepted)
        events.extend(v for v in rows if v["event"] in ("first_score","final_score","blank"))
    return labels,events


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("record",type=Path,help="record containing frames, ink and logs")
    p.add_argument("--windows",type=Path,help="read original camera windows instead of archived crops")
    p.add_argument("--logs",type=Path)
    p.add_argument("--reference-luma",type=Path,help="explicit path to the post-reset mean reference photograph")
    p.add_argument("--reference-color",type=Path,help="explicit path to the post-reset color photograph")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    labels,events=target_events(args.logs or args.record/"logs")
    labels.update(name+"-"+phase for name in IDENTIFIERS for phase in ("pre","post"));labels.add(BASE)
    labels.update(name for name in RETURN_LABELS if all(path.is_file() for path in paths(name,args)))
    refsource,cc=paths(BASE,args);refgray=reset_check.luma(args.reference_luma or refsource)
    endpoints=[];readings={};primary={};held={}
    for name in sorted(labels):
        gray,color=paths(name,args)
        if name==BASE:
            gray=args.reference_luma or gray;color=args.reference_color or color
        result=reset_check.read(gray,color=color)
        shoulder=outer_check.displacement(reset_check.luma(gray),refgray);result["heldout_shoulder"]=shoulder
        readings[name]=result;out={"endpoint":name}
        estimates=[]
        for s in ("left_clear","center","right","outer_right"):
            r=result[s]
            out[s+"_ok"]=r.get("ok",False);out[s+"_raw_y"]=r.get("raw_row")
            out[s+"_delta_px"]=r.get("delta_from_reference_px");out[s+"_patch_mad_px"]=r.get("patch_mad_px")
            if s!="left_clear" and r.get("ok"):
                v=r["delta_from_reference_px"]/STRETCH[s]
                out[s+"_x980_equivalent_px"]=v;estimates.append(v)
        if len(estimates)>=2:out["median_other_regions_x980_px"]=float(np.median(estimates))
        out["heldout_shoulder_ok"]=shoulder.get("ok",False)
        out["heldout_shoulder_mad_px"]=shoulder.get("mad_px")
        if shoulder.get("ok"):
            held[name]=shoulder["shoulder_delta_px"]/STRETCH["heldout_shoulder"];out["heldout_shoulder_x980_equivalent_px"]=held[name]
        out["right_registered_row"]=result["right"].get("cup_row")
        out["right_nominal_ml"]=result["right"].get("nominal_ml")
        endpoints.append(round_row(out));primary[name]=out
    write_table(args.output/"reset-endpoints.csv",endpoints)
    direction=[]
    for ident in IDENTIFIERS:
        a=primary[ident+"-pre"];b=primary[ident+"-post"]
        out={"trial":ident}
        for s in ("left_clear","center","right","outer_right"):
            if a[s+"_ok"] and b[s+"_ok"]:out[s+"_delta_px"]=b[s+"_raw_y"]-a[s+"_raw_y"]
        out["right_registered_delta_px"]=b["right_registered_row"]-a["right_registered_row"]
        out["right_signed_nominal_ml"]=b["right_nominal_ml"]-a["right_nominal_ml"]
        if ident+"-pre" in held and ident+"-post" in held:
            out["heldout_shoulder_delta_px"]=held[ident+"-post"]-held[ident+"-pre"]
        direction.append(round_row(out))
    write_table(args.output/"reset-direction.csv",direction)
    scores=[];blank=[]
    for ev in events:
        name=ev["label"]
        if ev["event"]=="blank":
            before=name+"-pre";after=name+"-hold"
            blank.append(round_row({"trial":name,"operational_drift_px":ev["drift_px"],"heldout_shoulder_drift_px":held[after]-held[before] if before in held and after in held else None}))
            continue
        phase="first" if ev["event"]=="first_score" else "final"
        end=name+"-"+phase
        if end not in primary:continue
        r=primary[end];target=ev["target_px"]
        row={"trial":name,"phase":phase,"policy":ev.get("policy"),"target_px":target,"operational_error_px":ev["error_px"],
             "other_regions_in_corroboration_error_px":r["median_other_regions_x980_px"]-target if "median_other_regions_x980_px" in r else None,
             "heldout_shoulder_error_px":held[end]-target if end in held else None}
        for s in ("center","right","outer_right"):
            k=s+"_x980_equivalent_px";row[s+"_equivalent_error_px"]=r[k]-target if k in r else None
        scores.append(round_row(row))
    write_table(args.output/"reset-targets.csv",scores);write_table(args.output/"reset-idles.csv",blank)
    return_rows=[{"endpoint":name,"operating_x980_px":primary[name]["left_clear_delta_px"],
                  "heldout_x980_equivalent_px":held.get(name),"heldout_patch_mad_px":readings[name]["heldout_shoulder"].get("mad_px"),
                  "heldout_patches":readings[name]["heldout_shoulder"].get("patches")} for name in RETURN_LABELS if name in primary]
    summary={"reference":BASE,"return_to_reference":return_rows,"unreadable_target_scores":[r["trial"]+" "+r["phase"] for r in scores if r["heldout_shoulder_error_px"] is None],
             "baseline_right_nominal_ml":readings[BASE]["right"]["nominal_ml"],"baseline_left_projected_nominal_ml":readings[BASE]["projected_left"]["nominal_ml"],
             "direction":direction,"target_errors":{},"idle_drift_px":stats(r["heldout_shoulder_drift_px"] for r in blank)}
    for phase in ("first","final"):
        rv=[r for r in scores if r["phase"]==phase];summary["target_errors"][phase]={}
        for policy in ("all","hold","correct"):
            rows=[r for r in rv if policy=="all" or r["policy"]==policy]
            summary["target_errors"][phase][policy]={k:stats(r[k] for r in rows) for k in ("operational_error_px","heldout_shoulder_error_px","other_regions_in_corroboration_error_px")}
    (args.output/"reset-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    plot_direction(readings,args,args.output/"reset-direction.jpg")


if __name__=="__main__":main()
