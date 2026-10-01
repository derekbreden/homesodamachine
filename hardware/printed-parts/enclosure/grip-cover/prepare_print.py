"""Create a native PET-GF slice of one cover and the two full-size grip coupons.

This prepares files only. The printer profile, supports, speeds and wall order
come from the shared PET-GF project. Receiver coupons stand floor-down; the
cover has its back and both wings on the bed.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import grip_cover as g

sys.path.insert(0,str(g.ROOT/"hardware/printed-parts/faucet"))
import refresh_print_project as writer

JOB=g.ROOT/".cache/prints/grip-cover-v4"
PROFILE=g.ROOT/"hardware/printed-parts/petgf.3mf"
STEM="grip-cover-and-receiver-v4"


def main():
    JOB.mkdir(parents=True,exist_ok=True)
    project=JOB/f"{STEM}-input.3mf"
    if project.exists():
        raise FileExistsError("Keep the reviewed native slice immutable; use another job directory.")
    names=("grip-cover","grip-receiver-front","grip-receiver-back")
    report=writer.refresh(PROFILE,project,
                          parts=tuple((n,g.HERE/f"{n}.stl",0.) for n in names),
                          offsets=((0.,-65.),(-45.,0.),(45.,0.)),
                          title="Grip liner and full-size split receiver; fit candidate")
    with zipfile.ZipFile(project) as z:
        members={n:z.read(n) for n in z.namelist()}
    settings=json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(layer_height="0.24",initial_layer_print_height="0.2",
                    support_filament="1",support_interface_filament="1",flush_into_support="0",
                    brim_type="no_brim",brim_width="0",elefant_foot_compensation="0")
    assert settings["wall_sequence"]=="inner wall/outer wall"
    assert settings["is_infill_first"]=="0"
    assert settings["infill_wall_overlap"]=="15%"
    members[writer.SETTINGS_MEMBER]=json.dumps(settings,indent=2).encode()
    ranges=ET.Element("objects")
    for index in (1,2,3):
        obj=ET.SubElement(ranges,"object",id=str(index))
        if index==1:
            # Fine layers cover the inward top rounding of the finger face.
            band=ET.SubElement(obj,"range",min_z="2.64",max_z=str(g.THICK))
            ET.SubElement(band,"option",opt_key="layer_height").text="0.08"
        else:
            # Same print-down R6 transition and production pose as the bottom.
            band=ET.SubElement(obj,"range",min_z="35.0",max_z="41.5")
            ET.SubElement(band,"option",opt_key="layer_height").text="0.24"
            ET.SubElement(band,"option",opt_key="wall_loops").text="6"
    members["Metadata/layer_config_ranges.xml"]=ET.tostring(ranges,encoding="utf-8",xml_declaration=True)
    writer.archive_write(project,members)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report.update(project_sha256=sha(project),settings_sha256=sha_bytes(members[writer.SETTINGS_MEMBER]),
                  submitted=False,source_sha256={str(p.relative_to(g.ROOT)):sha(p) for p in
                      (PROFILE,Path(__file__),*(g.HERE/f"{n}.stl" for n in names))})
    (JOB/"preparation.json").write_text(json.dumps(report,indent=2)+"\n")
    ready=JOB/"ready";ready.mkdir()
    command=["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio","--slice","0",
             "--arrange","0","--orient","0","--outputdir",str(ready),
             "--export-3mf",f"{STEM}.gcode.3mf",str(project)]
    (JOB/"slice-command.json").write_text(json.dumps(command,indent=2)+"\n")
    with (ready/"slice.log").open("w") as log:
        result=subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT)
    print("SLICE_EXIT",result.returncode,flush=True)
    return result.returncode


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


if __name__=="__main__":
    raise SystemExit(main())
