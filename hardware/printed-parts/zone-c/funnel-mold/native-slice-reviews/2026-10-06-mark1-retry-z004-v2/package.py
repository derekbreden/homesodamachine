"""Package the reviewed cavity plate; preserve every native G-code byte."""
from pathlib import Path
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "tools").is_dir())
PUBLIC = Path(__file__).resolve().parent
CACHE = ROOT / ".cache/funnel-retry-mark1-z004-20261006"
NAME = "2026-10-06-funnel-cavity-mark1-right-z004-retry-v2.gcode.3mf"
SOURCE = CACHE / "slice" / NAME
SINGLE = CACHE / "cavity-native-only.gcode.3mf"
DESTINATION = CACHE / "ready" / NAME
sys.path.insert(0, str(ROOT / "tools"))
from bambu_print_archive import package


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


review = json.loads((PUBLIC / "readiness-review.json").read_text())
assert sha(SOURCE) == review["native_slice"]["slice_sha256"]
assert not SINGLE.exists() and not DESTINATION.exists()
with zipfile.ZipFile(SOURCE) as z:
    assert z.testzip() is None
    payloads = {n: z.read(n) for n in z.namelist()}
gcode = payloads["Metadata/plate_1.gcode"]
assert hashlib.sha256(gcode).hexdigest() == review["native_slice"]["plates"][0]["gcode_sha256"]
assert hashlib.md5(gcode).hexdigest() == payloads["Metadata/plate_1.gcode.md5"].decode().strip().lower()
omitted = []
for name in list(payloads):
    if re.search(r"(?:plate(?:_no_light)?|top|pick|thumbnail)_2(?:\.|_)", name):
        omitted.append(name)
        del payloads[name]
for name in ("Metadata/slice_info.config", "Metadata/model_settings.config"):
    node = ET.fromstring(payloads[name])
    for plate in node.findall("plate")[1:]:
        node.remove(plate)
    payloads[name] = ET.tostring(node, xml_declaration=True, encoding="UTF-8")
with zipfile.ZipFile(SINGLE, "x", zipfile.ZIP_DEFLATED) as z:
    for name, body in payloads.items():
        z.writestr(name, body)
DESTINATION.parent.mkdir(exist_ok=True)
record = package(SINGLE, DESTINATION)
record.update({
    "native_two_plate_archive": str(SOURCE.relative_to(ROOT)),
    "native_two_plate_archive_sha256": sha(SOURCE),
    "submitted_plate": 1, "other_plates_omitted": True,
    "omitted_second_plate_entries": omitted,
    "scope": "Prepared print-only cavity archive. No import or Send performed by this script.",
})
for key in ("source_archive", "print_only_archive"):
    record[key] = str(Path(record[key]).relative_to(ROOT))
with zipfile.ZipFile(DESTINATION) as z:
    assert z.testzip() is None
    assert z.read("Metadata/plate_1.gcode") == gcode
    assert [n for n in z.namelist() if n.endswith(".gcode")] == ["Metadata/plate_1.gcode"]
    assert len(ET.fromstring(z.read("Metadata/slice_info.config")).findall("plate")) == 1
    assert len(ET.fromstring(z.read("Metadata/model_settings.config")).findall("plate")) == 1
    assert not ET.fromstring(z.read("Metadata/model_settings.config")).findall("object")
(PUBLIC / "packaging.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
