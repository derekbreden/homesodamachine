"""Bind the shop purchase lists to the coordinator's verified Prime rows.

This is a document build. It opens no shopping cart and orders nothing.
Run after the mechanical stock/fastener manifests and verified rows are final.
"""
from __future__ import annotations

import json
import hashlib
import math
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "hardware/gun-positioner"
SOURCE = PLAN / "sourcing/prime-verified.json"


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def inline(value):
    return str(value).replace("|", " / ").replace("\n", " ")


def build():
    source = json.loads(SOURCE.read_text())
    rows = source["rows"]
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate purchase row IDs")
    unresolved = []
    paid_asins = {r.get("asin") for r in rows if (r.get("packs") or 0) > 0}
    for row in rows:
        if row.get("on_hand") or row.get("excluded"):
            continue
        if not row.get("prime") or not row.get("evidence_date"):
            unresolved.append(row["id"] + ": Prime evidence missing")
        if any(row.get(k) is None for k in ("pack", "need", "packs", "price", "line_total")):
            unresolved.append(row["id"] + ": quantity or price unresolved")
            continue
        if row["packs"] == 0:
            if money(row["line_total"]) != 0 or row.get("asin") not in paid_asins:
                unresolved.append(row["id"] + ": shared purchase is not covered")
            continue
        if row["packs"] * row["pack"] < row["need"]:
            unresolved.append(row["id"] + ": insufficient pack quantity")
        if row["pack"] <= 0 or row["packs"] != math.ceil(row["need"] / row["pack"]):
            unresolved.append(row["id"] + ": purchase does not use the minimum required packs")
        if money(row["price"]) * row["packs"] != money(row["line_total"]):
            unresolved.append(row["id"] + ": inconsistent total")
        if "product page not yet read" in str(row.get("gaps", "")).lower():
            unresolved.append(row["id"] + ": product page verification pending")
    if unresolved:
        raise ValueError("Purchase release is incomplete:\n" + "\n".join(unresolved))
    # Shared allocations consume the same purchased pack. Their combined
    # requirement must fit the total purchased quantity, not just each row.
    by_asin = defaultdict(list)
    for row in rows:
        if not row.get("on_hand") and not row.get("excluded"):
            by_asin[row["asin"]].append(row)
    for asin, shared in by_asin.items():
        needed = sum(row["need"] for row in shared)
        supplied = sum(row["packs"] * row["pack"] for row in shared)
        if supplied < needed:
            raise ValueError(f"Shared purchase {asin} supplies {supplied} pieces for {needed} required")
    active = [r for r in rows if not r.get("on_hand") and not r.get("excluded") and r["packs"] > 0]
    groups = defaultdict(list)
    for row in active:
        groups[row["category"]].append(row)
    totals = {k: sum((money(r["line_total"]) for r in v), Decimal(0)) for k,v in groups.items()}
    total = sum(totals.values(), Decimal(0))
    lines = [
        "# Gun-positioner purchases", "",
        f"**Complete new-purchase total: ${total:,.2f} before tax.** Prime status, prices and stock were observed on {source['observed']}. Pack totals include required fabrication stock, both camera stages, tools and the controller. No part is counted twice across the mechanical and optical assemblies.", "",
        "Use the exact model, length, thread lead and variant named in each row. The camera is the FoMaKo K20UH **Classic Black** variant. A screw described as T8 is insufficient: these drives require a verified **2 mm lead**, one-start TR8×2.", "",
        "## Buying sequence", "",
        "Buy the mechanism, shop tools and controller first. Build and qualify one complete drive, then duplicate it and complete the loaded fixture. Buy the camera equipment and optical-only mounting items when loaded retention and signed motion pass commissioning. The shared stock layouts include the camera blanks: keep marked offcuts for their later operations.", "",
        "The category tables below describe one complete build. Splitting a shared pack across stages changes when it is bought, not how many packs the complete build needs. Follow the stock nest rather than buying an additional sheet or fastener pack for each individual part.", "",
        "## Totals", "", "| Category | Subtotal |", "|---|---:|",
    ]
    for category in groups:
        lines.append(f"| {inline(category)} | ${totals[category]:,.2f} |")
    lines.extend([f"| **Total** | **${total:,.2f}** |", ""])
    for category, items in groups.items():
        lines += ["## " + category, "", "| Purchase link and exact specification | Needed | Pieces per pack | Buy packs | Pack price | Subtotal |", "|---|---:|---:|---:|---:|---:|"]
        for row in items:
            label = row.get("requirement") or row["title"]
            variant = f"; variant: {row['variant']}" if row.get("variant") else ""
            lines.append(f"| [{inline(label+variant)}]({row['url']}) | {row['need']} | {row['pack']} | **{row['packs']}** | ${money(row['price']):,.2f} | **${money(row['line_total']):,.2f}** |")
        lines.append("")
    lines += [
        "## Already available", "",
        "Use the reconciled [inventory](sourcing/inventory-reconciliation.md) for owned equipment and its assigned work. Existing rotator motors, drivers, power supplies and electronics remain assigned to that fixture. A ledger entry does not establish a spare part. The purchase tables omit reusable equipment that the inventory audit identifies.", "",
        "## Receipt and assembly checks", "",
        "The [verified source rows](sourcing/prime-verified.json) retain observed pack contents, seller, stock, dimensions and unresolved fit properties. The [assembly guide](../gun-positioner-guide/README.md) places receipt checks at the operations that depend on them. Verify screw lead, motor label, rail holes, driver pin names, spring dimensions, bolt grip and camera socket depth before cutting or applying power.", "",
        "Spring color is not a force calibration. Grade the assembled overload links on the specified force gauge; set passive drag with weighed masses and the balanced lever. These acceptance procedures are in the mechanical requirements and [commissioning](commissioning.md).", "",
        "This list funds fabrication and dry development. Live-laser containment, the welder's emission-veto interface and live observation have separate engineering and acceptance gates in the plan; this purchase total carries no unselected live-welding protection components.", "",
        "Sources: the Prime verification record, mechanism requirements/fasteners/stock nest, camera-stage manifest and controller purchase requirements. Rebuild this list with `python3 tools/gun-positioner-release/purchases.py` after updating the verified rows.", "",
    ]
    (PLAN/"purchases.md").write_text("\n".join(lines))
    result = {
        "schema":1, "observed":source["observed"], "currency":"USD", "before_tax":True,
        "verification_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "rows":active, "category_totals":{k:float(v) for k,v in totals.items()}, "total":float(total),
        "scope":"One fabricated six-axis fixture, dry-development controller and two dry-observation camera stages, with missing shop tools; no accepted physical performance claim."
    }
    (PLAN/"purchases.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"rows":len(active), "total_before_tax":float(total)}))


if __name__ == "__main__":
    build()
