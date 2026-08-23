#!/usr/bin/env python3
"""Render harness-rfq.md as the vendor-facing PDF that goes out with an RFQ.

The markdown is written for this repo — it links to sibling files and names paths a supplier
cannot open. This strips those, swaps the preamble for one that stands on its own, appends what
we want back, and lays it out for A4.

    /opt/homebrew/bin/python3 hardware/wiring/_harness_rfq_pdf.py

Needs `markdown` and `weasyprint`, neither of which is in the CAD venv — this runs on the system
python that has them.
"""

import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
SRC = HERE / "harness-rfq.md"
OUT = HERE / "homesodamachine-harness-rfq.pdf"

PREAMBLE = """# Harness RFQ

Ten low-voltage cable assemblies for a domestic kitchen appliance (a countertop soda dispenser),
currently at prototype. Every assembly lands on the main board at one end and on a valve, motor,
sensor or display at the other. This document is the complete build package: materials, workmanship,
board-side contact order, and a pin-level wire list for each of the ten.

Nothing here is proprietary; ask about anything that is ambiguous rather than assuming.

## Scope"""

TAIL = """
## What we need back

1. **Unit price at 25, 50 and 100 sets**, and any NRE / setup charged per assembly design.
2. **Lead time** for the first article and for a production run.
3. **Your answer to Open question 1** — the wire gauge into the JST XH housings. This is the one
   open engineering item and we would rather take your recommendation than impose ours.
4. Whether you will build to **IPC/WHMA-A-620 Class 2** and provide continuity + isolation test
   records per assembly.
5. Anything in the wire lists you would change to make the part cheaper or more manufacturable.

We are quoting several suppliers on the identical package.
"""

CSS = """<!doctype html><meta charset="utf-8"><style>
@page { size: A4; margin: 16mm 14mm;
  @bottom-right { content: "Home Soda Machine - Harness RFQ - p" counter(page);
                  font: 8pt Helvetica; color:#666 } }
body { font: 9.5pt/1.45 Helvetica, Arial, sans-serif; color:#111 }
h1 { font-size: 19pt; margin:0 0 2mm; border-bottom:2px solid #111; padding-bottom:2mm }
h2 { font-size: 12.5pt; margin:6mm 0 2mm; border-bottom:1px solid #bbb; padding-bottom:1mm;
     page-break-after:avoid }
h3 { font-size: 10.5pt; margin:4mm 0 1.5mm; page-break-after:avoid }
table { border-collapse:collapse; width:100%; margin:2mm 0 3mm; font-size:8.5pt }
th,td { border:1px solid #ccc; padding:1.3mm 2mm; text-align:left; vertical-align:top }
th { background:#f0f0f0; font-weight:600 }
code { font-family:"SF Mono",Menlo,monospace; font-size:8.5pt; background:#f4f4f4;
       padding:0 1mm; border-radius:2px }
p { margin:1.5mm 0 } ol,ul { margin:1.5mm 0 1.5mm 5mm; padding:0 } li { margin:1mm 0 }
</style>"""


def main():
    import markdown

    src = SRC.read_text()
    src = re.sub(r"\[([^\]]+)\]\(/[^)]+\)", r"\1", src)      # repo-absolute links
    src = re.sub(r"\[`([^`]+)`\]\([^)]+\)", r"\1", src)      # code-span links
    src = src.split("## Sources")[0]                          # points only at repo paths
    src = re.sub(r"^# Harness RFQ\n\n.*?\n\n## Scope", PREAMBLE, src, flags=re.S)
    src = re.sub(r"Branch geometry is[^\n]*\n[^\n]*\n\n", "", src)
    src += TAIL

    html = CSS + markdown.markdown(src, extensions=["tables", "fenced_code"])
    tmp = OUT.with_suffix(".html")
    tmp.write_text(html)
    subprocess.run(["weasyprint", str(tmp), str(OUT)], check=True)
    tmp.unlink()
    print(f"-> {OUT}  ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        sys.exit(f"{e}. Run with a python that has `markdown` and `weasyprint`.")
