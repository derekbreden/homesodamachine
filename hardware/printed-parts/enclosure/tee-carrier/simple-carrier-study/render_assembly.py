"""Actual final carrier seating poses; preceding hand sequence stays explicit."""
from pathlib import Path
import json
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from render_concept import body,setup,BLUE,ORANGE
from build_concept import box,STAGING_Y

HERE=Path(__file__).resolve().parent


def main():
    I=json.loads((HERE/"inputs/manifest.json").read_text())["interface"]
    I["half_entry_staging_y"]=STAGING_Y
    L=cq.importers.importStep(str(HERE/"left-concept.step")).val()
    R=cq.importers.importStep(str(HERE/"right-concept.step")).val()
    flex=cq.importers.importStep(str(HERE/"right-deflected-clearance-witness.step")).val()
    cut=box((-40,40),(99,149),(165,231))
    aft=I["aft_limit_offset_y"]
    left=L.intersect(cut).translate((0,aft,0))
    fig=plt.figure(figsize=(15,8),facecolor="#faf9f6")
    fig.text(.04,.95,"Assembly sequence · left half first, right half second",fontsize=21)
    fig.text(.04,.902,"Open rear; valves absent. Hold each spring at 12.15 mm with a temporary flat pusher. Actual hand force is unmeasured.",fontsize=11)
    labels=["4 · Slide fore 28.5 mm", "At the stop · retaining wall deflected", "5 · Seat outward 3.25 mm"]
    pieces=[R.intersect(cut).translate((-3.25,I["half_entry_staging_y"],0)),
            flex.intersect(cut).translate((-3.25,aft,0)),R.intersect(cut).translate((0,aft,0))]
    for n,(label,right) in enumerate(zip(labels,pieces)):
        ax=fig.add_axes((.015+n*.328,.34,.325,.51),projection="3d")
        body(ax,left,BLUE);body(ax,right,ORANGE)
        setup(ax,(-42,42),(100,189 if n==0 else 157),(163,233),31,-60)
        ax.set_title(label,fontsize=12,loc="left",pad=0)
    fig.text(.04,.297,"The broad shelf passes through a matching opening in the right web. It does not require lifting, tilting or a separate alignment move.",fontsize=11)
    fig.text(.04,.235,"Preceding rigid motions for each half",fontsize=13,weight="bold")
    fig.text(.04,.197,"1  Carry in through the open rear, above the outer well.\n2  Lower 70 mm.\n3  Shift outward 13.90 mm, stopping 3.25 mm inboard of the final position.",fontsize=12,linespacing=1.5,va="top")
    fig.text(.56,.235,"After seating",fontsize=13,weight="bold")
    fig.text(.56,.197,"6  Withdraw the spring pusher inboard, then lift it out.\nRepeat for the other half; its final outward seat engages the joint.\nInstall the valves and their existing retention ties afterward.",fontsize=12,linespacing=1.5,va="top")
    fig.text(.04,.044,"Native routes clear on the frozen wall. Full-enclosure trial supplies support-removal, whole-span bending, snap-fit and real spring-retention readings.",fontsize=10,color="#7b3b2b")
    fig.savefig(HERE/"assembly-sequence.png",dpi=160,facecolor=fig.get_facecolor())
    fig.savefig(HERE/"assembly-sequence.svg",facecolor=fig.get_facecolor())


if __name__=="__main__":main()
