#!/usr/bin/env python3
"""Emit a cable assembly from the harness RFQ as a MiniProto harness spec, and price it.

The spec object is theirs — schema at https://www.miniproto.com/docs/api/schema.json — and the
same JSON is what their quote intake takes as an upload. Their API is anonymous, no key:

    POST /api/v1/validations     crimp-compatibility check, no side effects
    POST /api/v1/price-snapshots priced snapshot, connectors given by MPN

Usage:
    python3 _harness_quote.py                    # write j2-manifold-b.harness.json
    python3 _harness_quote.py --gauge "24 AWG"   # the variant that passes their crimp check
    python3 _harness_quote.py --price            # validate + price at 1 / 10 / 25 / 100

`--gauge` exists because the gauge is Open question 1 in `harness-rfq.md`: 22 AWG silicone does not
pass a crimp check into JST XH, and silicone passes from 24 AWG down. The default emits the schedule
as written so the conflict is visible to whoever reads the file.
"""

import argparse
import json
import urllib.error
import urllib.request

API = "https://www.miniproto.com/api/v1/"

XHP6 = "XHP-6"        # JST XH 6-way female housing, the MANIFOLD B board wafer
FASTON_250 = "2178438-1"  # TE FASTON 250, 6.3 mm female receptacle, 20-24 AWG

# J2 MANIFOLD B. Connector 0 is the board wafer; 1..8 are the eight device tabs, in the order
# below. Splice 0 is the WAGO 221-415 at the manifold. Contact 3 (OUT4) is never referenced.
DEVICES = ["V-I +", "V-J +", "fan +", "V-K +", "fan -", "V-K -", "V-J -", "V-I -"]

# (from-pin | None for the splice, to-connector index, length mm)
BRANCHES = [(0, 1, 150), (0, 2, 150), (0, 3, 100), (0, 4, 200)]
RETURNS = [(2, 5, 400), (4, 6, 500), (5, 7, 450), (6, 8, 450)]

NOTES = """J2 "MANIFOLD B", one of ten low-voltage assemblies in the appliance. Full RFQ package:
hardware/wiring/harness-rfq.md.

Contact 3 (OUT4) of the XHP-6 is a routed spare and is deliberately left EMPTY - crimp five contacts
in their labelled positions and do not close the gap. Contact 3 is mid-housing, so a loom filling
1-5 consecutively lands every conductor one position off and puts the shared 12 V rail on a driver
output. Please verify the open cavity at final test.

Splice 0 is a WAGO 221-415 five-way lever nut at the manifold, not a butt splice: its body
press-fits into a well printed in our enclosure wall.

All conductors black. Identify by assembly name on a heat-shrink marker at the housing, not
per-conductor.

Sleeve: black PET expandable braided, 1/2 inch, over the trunk from the housing to the fan-out,
both cut ends finished with black heat-shrink.

Workmanship IPC/WHMA-A-620 Class 2, 100% continuity and isolation test."""


def spec(gauge="22 AWG", quantity=1):
    wire = {"gauge": gauge, "color": "Black", "wireFamily": "Silicone"}
    connectors = [{"ref": {"mpn": XHP6}, "side": "left"}]
    connectors += [{"ref": {"mpn": FASTON_250}, "side": "right"} for _ in DEVICES]

    wires = [{"sourceConnector": 0, "sourcePin": 1, "targetSplice": 0, "lengthMm": 300, **wire}]
    wires += [{"sourceSplice": 0, "targetConnector": t, "targetPin": 1, "lengthMm": mm, **wire}
              for _, t, mm in BRANCHES]
    wires += [{"sourceConnector": 0, "sourcePin": p, "targetConnector": t, "targetPin": 1,
               "lengthMm": mm, **wire} for p, t, mm in RETURNS]

    return {
        "projectName": "J2 MANIFOLD B - Home Soda Machine",
        "quantity": quantity,
        "connectors": connectors,
        "splices": [{"method": "crimp"}],
        "wires": wires,
        "designNotes": NOTES,
    }


def post(route, payload):
    req = urllib.request.Request(API + route, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req)), None
    except urllib.error.HTTPError as e:
        return None, json.loads(e.read().decode() or "{}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gauge", default="22 AWG")
    ap.add_argument("--price", action="store_true")
    ap.add_argument("-o", default="j2-manifold-b.harness.json")
    args = ap.parse_args()

    s = spec(args.gauge)
    with open(args.o, "w") as f:
        json.dump(s, f, indent=2)
    print(f"-> {args.o}  ({len(s['wires'])} wires, {len(s['connectors'])} connectors, 1 splice)")

    if not args.price:
        return

    ok, err = post("validations", {"spec": s})
    if err:
        print(f"\nvalidate: {err.get('title')}\n  {err.get('detail')}")
        return
    print("\nvalidate: OK")

    ok, err = post("price-snapshots", {"spec": s})
    if err:
        print(f"price: {err.get('detail')}")
        return
    print(f"price   ({ok['priceVersion']}, expires {ok['expiresAt'][:10]})")
    for b in ok["priceBreaks"]:
        print(f"  qty {b['quantity']:>4}   "
              f"${b['unitPriceCents']/100:>7.2f}/ea   ${b['totalCents']/100:>9.2f} total")
    print(f"  setup fee ${ok['setupFeeCents']/100:.2f}, charged once per design")


if __name__ == "__main__":
    main()
