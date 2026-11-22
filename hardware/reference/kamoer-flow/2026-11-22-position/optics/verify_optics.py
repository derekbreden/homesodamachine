#!/usr/bin/env python3
"""Replay real reference photographs through the compact ink format and measure registration on known digital translations."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image

import independent
import register_cup

HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("record",type=Path);p.add_argument("output",type=Path)
    args=p.parse_args()
    cases=[("pre_reset",args.record/"camera/fixed-reference.png",HERE/"dry-ink.npz"),
           ("restored",args.record/"camera/restored-reference-color.png",HERE/"post-reset/dry-ink.npz")]
    report={"software_translations":[],"native_and_packed":{}}
    with TemporaryDirectory() as scratch:
        temp=Path(scratch)
        for name,image,reference in cases:
            atlas=temp/"ink.png";register_cup.pack_color(image,atlas)
            dense=register_cup.form(image,reference=reference,detail=True)
            compact=register_cup.form(atlas,reference=reference,detail=True)
            assert dense==compact,name
            regenerated=temp/"template.npz";register_cup.build(atlas,regenerated)
            with np.load(reference) as a,np.load(regenerated) as b:
                exact=all(np.array_equal(a[k],b[k]) for k in a)
                assert exact,name
            report["native_and_packed"][name]={"all_registration_fields_identical":True,"regenerated_profiles_identical":True,"packed_bytes":atlas.stat().st_size}
            pic=Image.open(image).convert("RGB")
            for dy in [-39.,-31.5,29.5,40.]:
                shifted=temp/"shift.png"
                pic.transform(pic.size,Image.Transform.AFFINE,(1,0,0,0,1,-dy),Image.Resampling.BICUBIC).save(shifted,compress_level=1)
                result=register_cup.form(shifted,reference=reference)
                diff={s:result[s]["dy"]-dense[s]["dy"]-dy for s in ("left","right")}
                report["software_translations"].append({"source":name,"applied_vertical_px":dy,"recovered_minus_applied_px":diff})
    stem="width-2-008-post"
    with np.load(HERE/"registration.npz") as r:
        meta=json.loads((HERE/"registration.json").read_text())
        z=independent.read_image(args.record/"frames"/(stem+".png"),dict(r),meta,args.record/"ink"/(stem+".png"))
    report["partly_covered_left_surface"]={"endpoint":stem,"independent_left_raw_row":z["sightlines"]["left"]["raw_row"],"independent_right_raw_row":z["sightlines"]["right"]["raw_row"]}
    args.output.write_text(json.dumps(report,indent=2)+"\n")


if __name__=="__main__":main()
