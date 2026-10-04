#!/usr/bin/env python3
"""Exact purchase totals and project-only evidence reports.

Markdown owns purchase amounts. An explicit trailing "ea" (or "ea.") alone
multiplies price by quantity; already-totaled orders and bundles never do.
Fulfillment and payment evidence are independent.

  python3 hardware/scripts/_ledger_totals.py --write        # regenerate
  python3 hardware/scripts/_ledger_totals.py --check        # read-only integrity
  python3 hardware/scripts/_ledger_totals.py --report       # read-only summary
  python3 hardware/scripts/_ledger_totals.py --audit        # read-only gaps
  python3 hardware/scripts/_ledger_totals.py --export-json  # read-only stdout
  python3 hardware/scripts/_ledger_totals.py --export-csv   # read-only stdout

A bare run retains the docgen caller's regeneration behavior. Every named
inspection/export mode is nonmutating. Missing historical evidence warns;
inconsistent amounts, broken relationships and stale generated values fail.
"""
import argparse
import datetime
import json
import os
import re
import sys
from decimal import Decimal
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "ledger", "purchases.md")
ORDERS = os.path.join(HERE, "..", "ledger", "purchases.orders.json")
EVIDENCE = os.path.join(HERE, "..", "ledger", "purchases.evidence.json")

sys.path.insert(0, HERE)
sys.path.insert(0, str(next(p for p in Path(HERE).resolve().parents
                           if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import cells, note_rewritten, substitute_md  # noqa: E402
from _ledger_analysis import (analyze, export_csv, export_json, format_minor,
                              input_fingerprint, load_evidence, plain_text,
                              render_report)  # noqa: E402

EXCLUDE_SECTIONS = {"Totals"}
STATUS_KEYWORDS = (
    "LIKELY-TO-BUY", "NOT NEEDED", "alt option", "ON-ORDER", "ACQUIRED",
    "MISSING", "PARTIAL", "CANCELLED", "RETURNED", "REPLACEMENT", "REPLACED",
    "UNRESOLVED",
)
PRICE = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)")
ORDER_NO = re.compile(r"\b\d{3}-\d{7}-\d{7}\b")
PURCHASE_ID = re.compile(r"<!--\s*purchase:([^\s<>]+)\s*-->")
ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
EM = "—"
STALE_ON_ORDER_DAYS = 45
RECONCILE_TOLERANCE = Decimal("0.01")
ZERO = Decimal("0")


def first_price(cell):
    match = PRICE.search(cell)
    return Decimal(match.group(1).replace(",", "")) if match else None


def lead_int(cell):
    match = re.match(r"\s*([0-9]+)", plain_text(cell))
    return int(match.group(1)) if match else None


def parse(path):
    """Keep the existing five-value interface, with exact Decimal money.

    The row list additionally includes unpriced/zero rows and section 18
    service records. Labor is separately tallied in the legacy summary.
    """
    status_totals, section_acq, labor = {}, {}, ZERO
    ambiguous, section, rows, colmap = [], "(preamble)", [], {}
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("## "):
            section, colmap = line[3:].strip(), {}
            continue
        if not line.startswith("|") or section in EXCLUDE_SECTIONS:
            continue
        columns = cells(line)
        if len(columns) < 2 or set("".join(columns)) <= set("-: "):
            continue
        clean = [plain_text(column) for column in columns]
        if ("$" in clean and any(name in clean for name in
                                ("Status", "Type", "Item", "Contents", "Part"))):
            colmap = {name: i for i, name in enumerate(clean)}
            continue
        if not colmap or re.match(r"^(?:§\d+\s+)?subtotal\b", clean[0], re.I):
            continue

        def col(*names):
            for name in names:
                index = colmap.get(name)
                if index is not None and index < len(columns) and clean[index] not in ("", EM):
                    return clean[index]
            return ""

        labor_row = bool(re.match(r"18\.", section))
        status_text = col("Status")
        status = next((key for key in STATUS_KEYWORDS
                       if re.search(r"(?<![\w-])" + re.escape(key) + r"(?![\w-])",
                                    status_text)), None)
        if status is None and labor_row and "Type" in colmap:
            status, status_text = "ACQUIRED", "ACQUIRED"
        if status is None:
            continue
        price_text = col("$")
        price, cost = first_price(price_text), first_price(price_text)
        quantity_text = col("Qty", "Quantity", "# of receipts")
        quantity = lead_int(quantity_text)
        price_basis = "unit" if re.search(r"(?:\s|^)ea\.?\s*$", price_text) else "row_total"
        if price is None:
            ambiguous.append((status, "unknown-price", " | ".join(clean)[:88]))
        elif price_basis == "unit":
            if quantity is None:
                cost = None
                ambiguous.append((status, f"ea-no-qty ({price})", " | ".join(clean)[:70]))
            else:
                cost = price * quantity
                ambiguous.append((status, f"ea {quantity}×{price}={cost:.2f}",
                                  " | ".join(clean)[:60]))
        if cost is not None:
            if labor_row:
                if status in ("ACQUIRED", "ON-ORDER", "MISSING", "PARTIAL", "RETURNED", "REPLACED"):
                    labor += cost
            else:
                status_totals[status] = status_totals.get(status, ZERO) + cost
                if status in ("ACQUIRED", "REPLACED", "RETURNED", "REPLACEMENT"):
                    section_acq[section] = section_acq.get(section, ZERO) + cost
        description = col("Part", "Item", "Contents", "Type") or clean[0]
        identity = PURCHASE_ID.search(columns[0])
        ordered = col("Ordered", "Order date", "Date range")
        date_basis = ("coverage_period" if "Date range" in colmap else
                      "invoice_date" if "Invoice date" in colmap else
                      "receipt_date" if "Receipt date" in colmap else "order_date")
        rows.append({
            "purchase_id": identity.group(1) if identity else None,
            "line": line_no, "section": section, "status": status,
            "status_text": status_text, "cost": cost,
            "orders": ORDER_NO.findall(col("Order #")),
            "ordered": ordered, "invoice_date": col("Invoice date"),
            "receipt_date": col("Receipt date"), "row_date_basis": date_basis,
            "delivered": col("Delivered"), "part": description[:64],
            "description": description, "quantity": quantity,
            "quantity_text": quantity_text, "price_basis": price_basis,
            "unit_price": price if price_basis == "unit" else None,
            "currency": col("Currency") or "USD", "labor": labor_row,
        })
    return status_totals, section_acq, labor, ambiguous, rows


def load_orders(path=ORDERS):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle, parse_float=Decimal)["orders"]


def days_since(iso_date, today):
    match = ISO.match(iso_date or "")
    if not match:
        return None
    try:
        date = datetime.date(*(int(group) for group in match.groups()))
    except ValueError:
        return None
    return (today - date).days


def reconcile_orders(rows, orders, tolerance=RECONCILE_TOLERANCE):
    """Legacy project invoice allocations; not evidence of merchant payment."""
    grouped = {}
    for row in rows:
        if row["status"] in ("ACQUIRED", "ON-ORDER", "MISSING", "PARTIAL", "RETURNED", "REPLACED"):
            for order in set(row["orders"]):
                grouped.setdefault(order, []).append(row)
    mismatch, unverifiable, split = [], [], []
    for order_no, group in sorted(grouped.items()):
        if any(len(set(row["orders"])) > 1 for row in group):
            split.append(order_no)
            continue
        invoice = orders.get(order_no)
        allocated = sum((row["cost"] for row in group if row["cost"] is not None), ZERO)
        if invoice is None or invoice.get("total") is None or any(row["cost"] is None for row in group):
            unverifiable.append((order_no, allocated))
            continue
        invoice_project = Decimal(str(invoice["total"])) - Decimal(str(invoice.get("nonproject_amount") or 0))
        if abs(allocated - invoice_project) > tolerance:
            mismatch.append((order_no, allocated, invoice_project, len(group)))
    return mismatch, unverifiable, split


def stale_on_order(rows, today):
    aged, undated = [], []
    for row in rows:
        if row["status"] != "ON-ORDER":
            continue
        age = days_since(row["ordered"], today)
        if age is None:
            undated.append(row)
        elif age >= STALE_ON_ORDER_DAYS:
            aged.append((age, row))
    aged.sort(key=lambda item: (-item[0], item[1].get("purchase_id") or item[1]["part"]))
    return aged, undated


def unrecorded_orders(rows, orders):
    named = {order for row in rows for order in row["orders"]}
    return sorted((key, value) for key, value in orders.items()
                  if value.get("project") is not False and key not in named)


def variables_from_totals(status_totals, sections, labor, analysis=None):
    money = lambda value: "$" + f"{value:,.2f}"
    acquired = status_totals.get("ACQUIRED", ZERO)
    on_order = status_totals.get("ON-ORDER", ZERO)
    missing = status_totals.get("MISSING", ZERO)
    acquired += sum((status_totals.get(key, ZERO)
                     for key in ("REPLACED", "RETURNED", "REPLACEMENT")), ZERO)
    on_order += sum((status_totals.get(key, ZERO) for key in ("PARTIAL", "UNRESOLVED")), ZERO)
    variables = {
        "LEDGER_ACQUIRED_HW": money(acquired), "LEDGER_LABOR": money(labor),
        "LEDGER_ACQUIRED_COMBINED": money(acquired + labor),
        "LEDGER_ON_ORDER": money(on_order), "LEDGER_MISSING": money(missing),
        "LEDGER_GRAND_TOTAL": money(acquired + labor + on_order + missing),
    }
    for title, value in sections.items():
        match = re.match(r"(\d+)", title)
        if match:
            variables[f"LEDGER_SEC{match.group(1)}"] = money(value)
    if analysis and "summary" in analysis:
        summary = analysis["summary"]
        procurement = next((row for row in summary["procurement"]["totals"]
                            if row["currency"] == "USD"), None)
        payments = next((row for row in summary["merchant_payments"]["totals"]
                         if row["currency"] == "USD"), None)
        if procurement:
            for marker, field in (
                    ("LEDGER_FINAL_VENDOR", "final_vendor_amount_minor"),
                    ("LEDGER_ESTIMATES", "estimate_minor"),
                    ("LEDGER_LEGACY_UNVERIFIED", "legacy_unverified_minor")):
                variables[marker] = format_minor(procurement[field])
        if payments:
            for marker, field in (
                    ("LEDGER_MERCHANT_CHARGES", "charges_minor"),
                    ("LEDGER_MERCHANT_REFUNDS", "refunds_minor"),
                    ("LEDGER_MERCHANT_NET", "net_minor")):
                variables[marker] = format_minor(payments[field])
    return variables


def stale_markers(path, variables):
    text = Path(path).read_text(encoding="utf-8")
    return [f"[{match.group(1)}]({name}) should be [{value}]({name})"
            for name, value in variables.items()
            for match in [re.search(r"\[([^\]]*)\]\(" + re.escape(name) + r"\)", text)]
            if match and match.group(1) != value]


def generated_paths(path):
    path = Path(path)
    return path.with_suffix(".export.json"), path.with_suffix(".export.csv")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    modes = parser.add_mutually_exclusive_group()
    for mode in ("write", "check", "report", "audit", "export-json", "export-csv"):
        modes.add_argument("--" + mode, action="store_true")
    parser.add_argument("--ledger", default=LEDGER, help="canonical purchase Markdown")
    parser.add_argument("--orders", default=ORDERS, help="preserved legacy order evidence")
    parser.add_argument("--evidence", default=EVIDENCE, help="project-safe evidence sidecar")
    args = parser.parse_args(argv)
    try:
        totals, sections, labor, ambiguous, rows = parse(args.ledger)
        evidence = load_evidence(args.evidence)
        analysis = analyze(rows, evidence, input_fingerprint(args.ledger, evidence))
        orders = load_orders(args.orders)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Ledger integrity error: {error}", file=sys.stderr)
        return 1
    mismatch, unverifiable, split = reconcile_orders(rows, orders)
    exact_mismatches = reconcile_orders(rows, orders, tolerance=ZERO)[0]
    for order_no, allocated, invoice_project, _ in exact_mismatches:
        if abs(allocated - invoice_project) <= RECONCILE_TOLERANCE:
            analysis["validation"]["warnings"].append(
                f"Legacy order {order_no}: row valuation USD {allocated:,.2f}, "
                f"preserved project invoice USD {invoice_project:,.2f}; "
                f"historical allocation residual USD {invoice_project - allocated:+.2f}. "
                "Original prices retained; no balancing payment invented.")
    try:
        aged, undated = stale_on_order(rows, datetime.date.fromisoformat(evidence["as_of"]))
    except (ValueError, TypeError, KeyError):
        aged, undated = [], []
    # Account-order metadata never enters project exports or diagnostics.
    for order_no, allocated, invoice_project, count in mismatch:
        analysis["validation"]["errors"].append(
            f"Order {order_no}: {count} project rows allocate USD {allocated:,.2f}; "
            f"preserved project invoice amount USD {invoice_project:,.2f}")
    if unverifiable:
        analysis["validation"]["warnings"].append(
            f"{len(unverifiable)} legacy named order(s) lack an exact invoice allocation check")
    if split:
        analysis["validation"]["warnings"].append(
            f"{len(split)} legacy order(s) belong to rows covering multiple orders")
    if aged:
        analysis["validation"]["warnings"].append(
            f"{len(aged)} ON-ORDER purchase(s) older than {STALE_ON_ORDER_DAYS} days require fulfillment evidence")
    if undated:
        analysis["validation"]["warnings"].append(
            f"{len(undated)} ON-ORDER purchase(s) have unknown order dates")
    unrecorded = unrecorded_orders(rows, orders)
    if unrecorded:
        analysis["validation"]["warnings"].append(
            f"{len(unrecorded)} preserved potentially project order(s) have no named Markdown row")
    variables = variables_from_totals(totals, sections, labor, analysis)
    if args.export_json:
        sys.stdout.write(export_json(analysis))
        return bool(analysis["validation"]["errors"])
    if args.export_csv:
        sys.stdout.write(export_csv(analysis))
        return bool(analysis["validation"]["errors"])
    if args.check:
        errors = analysis["validation"]["errors"] + stale_markers(args.ledger, variables)
        figure_path = Path(args.ledger).with_suffix(".figures.json")
        if figure_path.exists():
            try:
                figures = json.loads(figure_path.read_text()).get("/hardware/scripts/_ledger_totals.py", {})
                expected = {key: value for key, value in variables.items()
                            if re.search(r"\]\(" + re.escape(key) + r"\)",
                                         Path(args.ledger).read_text())}
                if figures != expected:
                    errors.append("purchases.figures.json is stale; run --write")
            except ValueError:
                errors.append("purchases.figures.json is invalid")
        for path, content in zip(generated_paths(args.ledger),
                                 (export_json(analysis), export_csv(analysis))):
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                errors.append(path.name + " is missing or stale; run --write")
        for error in errors:
            print("ERROR: " + error)
        for warning in analysis["validation"]["warnings"]:
            print("WARNING: " + warning)
        print("Project ledger integrity " + ("FAILED" if errors else "✓") +
              "; historical evidence coverage is reported separately.")
        return bool(errors)
    if args.report or args.audit:
        sys.stdout.write(render_report(analysis, audit=args.audit))
        if args.audit:
            print("Legacy unit-price and unknown-price rows:")
            for status, kind, text in ambiguous:
                print(f"  [{status}] {kind} | {text}")
            for age, row in aged:
                print(f"  Fulfillment evidence gap: {row['purchase_id']} "
                      f"ON-ORDER {age} days (ordered {row['ordered']})")
        return bool(analysis["validation"]["errors"])
    if analysis["validation"]["errors"]:
        sys.stdout.write(render_report(analysis))
        return 1
    substitute_md(args.ledger, variables)
    analysis["input_fingerprint"] = input_fingerprint(args.ledger, evidence)
    for path, content in zip(generated_paths(args.ledger),
                             (export_json(analysis), export_csv(analysis))):
        note_rewritten(path)
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
    sys.stdout.write(render_report(analysis))
    return 0


if __name__ == "__main__":
    sys.exit(main())
