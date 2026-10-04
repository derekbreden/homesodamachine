#!/usr/bin/env python3
"""Project-only analysis of the Markdown ledger and its evidence sidecar.

Amounts in exports are integer currency minor units. No merchant amount or
fulfillment status creates a payment event. Legacy merchant-account exports
are deliberately not an input to this module.
"""

import calendar
import copy
import csv
import datetime as dt
import hashlib
import io
import json
import re
from collections import defaultdict
from decimal import Decimal

SCHEMA_VERSION = 1
PURPOSES = {
    "equipment_tooling", "components", "consumables_materials",
    "engineering_software_services", "hosting_domains",
    "documentation_marketing", "unclassified",
}
AMOUNT_EVIDENCE = {"estimate", "final_vendor_amount", "legacy_unverified"}
ALLOCATION_STATUS = {"all_project", "mixed_partial", "unresolved"}
EVENT_TYPES = {"charge", "refund", "authorization", "noncash_credit"}
PROVES = {
    "price", "order_date", "delivery", "charge", "refund", "authorization",
    "noncash_credit", "service_period", "no_charge", "receipt_date", "invoice_date",
    "merchant_event_date",
}
ACTIVE_STATUSES = {"ACQUIRED", "ON-ORDER", "MISSING", "PARTIAL", "RETURNED",
                   "REPLACEMENT", "REPLACED", "UNRESOLVED"}
OUTSTANDING_STATUSES = {"ON-ORDER", "MISSING", "PARTIAL", "UNRESOLVED"}
PURCHASE_META_FIELDS = {
    "vendor", "purpose", "amount_evidence", "order_ids", "allocation_status",
    "source_ids", "invoice_date", "service_period", "replacement_for",
    "price_history", "contributes", "currency", "row_date_basis", "delivery_dates",
    "receipt_date", "stream",
}
SOURCE_FIELDS = {
    "vendor", "document_type", "reference", "document_date", "proves",
    "verified_at", "note", "receipt_date", "service_period", "invoice_reference",
    "merchant_event_date", "notification_date",
}
ORDER_FIELDS = {"vendor", "reference", "order_date", "allocation_status",
                "source_ids", "replaces", "replaced_by"}
EVENT_FIELDS = {
    "event_id", "vendor", "event_type", "confirmation", "event_date",
    "amount_minor", "currency", "allocation_status", "source_ids",
    "verified_at", "original_event_id", "reference", "receipt_date",
    "invoice_date", "service_period", "order_ids",
}
ALLOCATION_FIELDS = {
    "allocation_id", "event_id", "purchase_id", "order_id", "amount_minor",
    "currency",
}
COVERAGE_FIELDS = {
    "coverage_id", "vendor", "stream", "evidence_type", "checked_at",
    "examined_period", "complete_period", "coverage", "source_ids", "order_ids",
    "note",
}
GAP_FIELDS = {
    "gap_id", "purchase_ids", "order_ids", "event_ids", "source_ids",
    "missing_fact", "sources_checked",
}
HISTORY_FIELDS = {
    "amount_minor", "currency", "amount_evidence", "verified_at", "source_ids",
    "note",
}


def plain_text(value):
    """Keep link labels, never mailbox/receipt locators or HTML annotations."""
    value = re.sub(r"<!--.*?-->", "", str(value), flags=re.S)
    value = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"<[^>]*>", "", value)
    return re.sub(r"[*~\x60]", "", value).strip()


def parse_date(value):
    """Calendar dates remain calendar dates, without timezone conversion."""
    if not value or plain_text(value) in {"—", "-", "unknown"}:
        return None
    if isinstance(value, dict):
        return copy.deepcopy(value)
    text = plain_text(value)
    days = re.findall(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)", text)
    if len(days) > 1:
        return {"precision": "range", "start": days[0], "end": days[-1]}
    if len(days) == 1:
        return {"precision": "day", "value": days[0]}
    if re.fullmatch(r"\d{4}-\d{2}", text):
        return {"precision": "month", "value": text}
    return None


def date_bounds(value):
    if value is None:
        return None
    precision = value["precision"]
    if precision == "day":
        day = dt.date.fromisoformat(value["value"])
        return day, day
    if precision == "month":
        year, month = map(int, value["value"].split("-"))
        return dt.date(year, month, 1), dt.date(
            year, month, calendar.monthrange(year, month)[1])
    return dt.date.fromisoformat(value["start"]), dt.date.fromisoformat(value["end"])


def date_month(value):
    bounds = date_bounds(value)
    if bounds and bounds[0].strftime("%Y-%m") == bounds[1].strftime("%Y-%m"):
        return bounds[0].strftime("%Y-%m")
    return "undated_unallocated"


def to_minor(amount, currency, scales):
    if amount is None:
        return None
    scaled = Decimal(str(amount)) * (Decimal(10) ** scales[currency])
    if not scaled.is_finite() or scaled != scaled.to_integral_value():
        raise ValueError(f"amount is not an exact {currency} minor-unit value")
    return int(scaled)


def format_minor(amount, currency="USD", scales=None):
    if amount is None:
        return "unknown"
    scale = (scales or {"USD": 2})[currency]
    number = Decimal(amount) / (Decimal(10) ** scale)
    return f"{'$' if currency == 'USD' else currency + ' '}{number:,.{scale}f}"


def _select(record, fields):
    return {key: copy.deepcopy(value) for key, value in record.items()
            if key in fields}


def _ids(record):
    for name in ("source_ids", "order_ids", "purchase_ids", "event_ids"):
        if name in record and isinstance(record[name], list):
            record[name] = sorted(set(record[name]))
    return record


def load_evidence(path):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    with open(path, encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=unique_keys)


def input_fingerprint(ledger_path, evidence):
    """Hash project inputs; exclude generated markers so writes are idempotent."""
    with open(ledger_path, encoding="utf-8") as handle:
        ledger = handle.read()
    ledger = re.sub(r"\[[^\]]*\]\((LEDGER_[A-Z0-9_]+)\)",
                    r"[generated](\1)", ledger)
    payload = ledger.encode() + b"\0" + json.dumps(
        evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def analyze(rows, evidence, fingerprint=None):
    """Build deterministic safe records, summaries, and integrity findings.

    Markdown owns parent purchase quantities, dates, current prices and status.
    A reconstructed group exports its parent as a noncontributing summary,
    detailed purchase records, and any exact remaining legacy amount.
    """
    errors, warnings = [], []
    if evidence.get("schema_version") != SCHEMA_VERSION:
        errors.append("unsupported evidence schema_version")
    scales = evidence.get("currency_scales", {"USD": 2})
    if (not isinstance(scales, dict) or not scales or
            any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= 6
                for v in scales.values())):
        raise ValueError("currency_scales must map currencies to integer scales 0..6")
    metadata = evidence.get("purchases", {})
    sources = [_ids(dict(source_id=key, **_select(value, SOURCE_FIELDS)))
               for key, value in sorted(evidence.get("sources", {}).items())]
    orders = [_ids(dict(order_id=key, **_select(value, ORDER_FIELDS)))
              for key, value in sorted(evidence.get("orders", {}).items())]
    purchases = []
    seen = set()
    for row in rows:
        purchase_id = row.get("purchase_id")
        if not purchase_id:
            errors.append(f"purchase row lacks persistent ID (line {row.get('line', '?')})")
            continue
        if purchase_id in seen:
            errors.append(f"duplicate purchase_id: {purchase_id}")
        seen.add(purchase_id)
        meta = metadata.get(purchase_id, {})
        if not meta:
            errors.append(f"purchase lacks metadata: {purchase_id}")
        currency = meta.get("currency", row.get("currency", "USD"))
        if currency not in scales:
            errors.append(f"{purchase_id}: undeclared currency {currency}")
            amount = None
        else:
            try:
                amount = to_minor(row["cost"], currency, scales)
            except ValueError as exc:
                errors.append(f"{purchase_id}: {exc}")
                amount = None
        record = {
            "purchase_id": purchase_id, "ledger_purchase_id": purchase_id,
            "vendor": meta.get("vendor", "Unknown"),
            "description": plain_text(row.get("description", row["part"])),
            "section": row["section"], "quantity": row.get("quantity"),
            "quantity_text": plain_text(row.get("quantity_text", "")),
            "price_basis": row.get("price_basis", "row_total"),
            "unit_amount_minor": None,
            "amount_minor": amount, "currency": currency,
            "amount_evidence": meta.get("amount_evidence", "legacy_unverified"),
            "row_date": parse_date(row.get("ordered") or row.get("invoice_date")
                                   or row.get("receipt_date") or ""),
            "row_date_basis": meta.get("row_date_basis", row.get("row_date_basis", "order_date")),
            "order_date": parse_date(row.get("ordered", "")),
            "delivery_date": parse_date(row.get("delivered", "")),
            "fulfillment": row["status"],
            "purpose": meta.get("purpose", "unclassified"),
            "stream": meta.get("stream", "purchase"),
            "order_ids": sorted(set(meta.get("order_ids", []))),
            "source_ids": sorted(set(meta.get("source_ids", []))),
            "allocation_status": meta.get("allocation_status", "unresolved"),
            "contributes": meta.get("contributes", True),
            "invoice_date": parse_date(row.get("invoice_date") or meta.get("invoice_date")),
            "receipt_date": parse_date(row.get("receipt_date") or meta.get("receipt_date")),
            "service_period": parse_date(meta.get("service_period")),
        }
        if currency in scales:
            try:
                record["unit_amount_minor"] = to_minor(row.get("unit_price"), currency, scales)
            except ValueError as exc:
                errors.append(f"{purchase_id}: unit price {exc}")
        if "delivery_dates" in meta:
            record["delivery_dates"] = [parse_date(value) for value in meta["delivery_dates"]]
        if record["row_date_basis"] != "order_date":
            record["order_date"] = None
            if record["row_date_basis"] == "invoice_date":
                record["invoice_date"] = record["row_date"]
            elif record["row_date_basis"] == "receipt_date":
                record["receipt_date"] = record["row_date"]
        if "replacement_for" in meta:
            record["replacement_for"] = meta["replacement_for"]
        if "price_history" in meta:
            record["price_history"] = [
                _ids(_select(item, HISTORY_FIELDS)) for item in meta["price_history"]]
        if row.get("price_basis") == "unit" and row.get("quantity") is None:
            errors.append(f"{purchase_id}: explicit unit price has no usable quantity")
        children = evidence.get("details", {}).get(purchase_id)
        if children:
            record["contributes"] = False
            record["record_role"] = "group_summary"
        else:
            record["record_role"] = "purchase"
        purchases.append(record)
        if not children:
            continue
        if amount is None:
            errors.append(f"{purchase_id}: cannot reconstruct an unknown grouped amount")
            continue
        child_total = 0
        for child in children:
            child_record = copy.deepcopy(record)
            child_record.update(_select(child, {
                "purchase_id", "vendor", "description", "quantity", "amount_minor",
                "currency", "amount_evidence", "purpose", "order_ids", "order_date",
                "invoice_date", "receipt_date", "service_period", "source_ids", "allocation_status",
                "contributes", "replacement_for", "stream",
            }))
            child_record.update({
                "ledger_purchase_id": purchase_id, "record_role": "detail",
                "price_basis": "row_total", "unit_amount_minor": None,
                "quantity_text": "", "contributes": child.get("contributes", True),
                "order_date": parse_date(child.get("order_date")),
                "invoice_date": parse_date(child.get("invoice_date")),
                "receipt_date": parse_date(child.get("receipt_date")),
                "service_period": parse_date(child.get("service_period")),
            })
            child_record.pop("price_history", None)
            child_record["description"] = plain_text(child_record["description"])
            if (child_record["currency"] != currency or
                    not isinstance(child_record.get("amount_minor"), int) or
                    isinstance(child_record.get("amount_minor"), bool)):
                errors.append(f"{purchase_id}: detail needs same-currency exact amount")
                continue
            if child_record["contributes"]:
                child_total += child_record["amount_minor"]
            purchases.append(_ids(child_record))
        if child_total > amount:
            errors.append(f"{purchase_id}: detail exceeds canonical group by "
                          f"{child_total - amount} minor units")
        elif child_total < amount:
            remainder = copy.deepcopy(record)
            remainder.update({
                "purchase_id": purchase_id + ":legacy-remainder",
                "description": "Unresolved remainder — " + record["description"],
                "record_role": "legacy_remainder", "amount_minor": amount - child_total,
                "amount_evidence": "legacy_unverified", "contributes": True,
                "order_ids": [], "source_ids": [], "quantity": None,
                "quantity_text": "", "price_basis": "row_total",
                "unit_amount_minor": None,
            })
            remainder.pop("price_history", None)
            purchases.append(remainder)
    unused = set(metadata) - seen
    if unused:
        errors.append("metadata names missing Markdown purchases: " + ", ".join(sorted(unused)))
    unused_groups = set(evidence.get("details", {})) - seen
    if unused_groups:
        errors.append("details name missing Markdown purchases: " +
                      ", ".join(sorted(unused_groups)))
    events = [_ids(_select(event, EVENT_FIELDS)) for event in evidence.get("events", [])]
    allocations = [_select(item, ALLOCATION_FIELDS)
                   for item in evidence.get("allocations", [])]
    coverage = [_ids(_select(item, COVERAGE_FIELDS))
                for item in evidence.get("coverage", [])]
    gaps = [_ids(_select(item, GAP_FIELDS)) for item in evidence.get("gaps", [])]
    export = {
        "schema_version": SCHEMA_VERSION, "as_of": evidence.get("as_of"),
        "reporting_period": copy.deepcopy(evidence.get("reporting_period")),
        "currency_scales": copy.deepcopy(scales), "input_fingerprint": fingerprint,
        "purchases": sorted(purchases, key=lambda item: item["purchase_id"]),
        "orders": orders, "sources": sources,
        "events": sorted(events, key=lambda item: item.get("event_id", "")),
        "allocations": sorted(allocations, key=lambda item: item.get("allocation_id", "")),
        "coverage": sorted(coverage, key=lambda item: item.get("coverage_id", "")),
        "gaps": sorted(gaps, key=lambda item: item.get("gap_id", "")),
    }
    validate(export, errors, warnings)
    export["validation"] = {"errors": sorted(set(errors)), "warnings": sorted(set(warnings))}
    if not errors:
        _relationships(export)
        export["summary"] = summaries(export)
    return export


def validate(data, errors, warnings):
    """Integrity errors fail checks; absence of historical evidence is a warning."""
    scales = data["currency_scales"]

    def fail(message):
        errors.append(message)

    def valid_date(value, context):
        if value is None:
            return
        try:
            if not isinstance(value, dict) or value.get("precision") not in {"day", "month", "range"}:
                raise ValueError()
            keys = {"precision", "start", "end"} if value["precision"] == "range" else {"precision", "value"}
            if set(value) != keys:
                raise ValueError()
            if value["precision"] == "month" and not re.fullmatch(r"\d{4}-\d{2}", value["value"]):
                raise ValueError()
            if value["precision"] == "day" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value["value"]):
                raise ValueError()
            if value["precision"] == "range" and any(
                    not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value[name])
                    for name in ("start", "end")):
                raise ValueError()
            bounds = date_bounds(value)
            if bounds[0] > bounds[1]:
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            fail(f"{context}: invalid precision-preserving date")

    def valid_period(value, context, optional=False):
        if value is None and optional:
            return
        try:
            if set(value) != {"start", "end"}:
                raise ValueError()
            if any(not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value[name])
                   for name in ("start", "end")):
                raise ValueError()
            if dt.date.fromisoformat(value["start"]) > dt.date.fromisoformat(value["end"]):
                raise ValueError()
        except (TypeError, ValueError):
            fail(f"{context}: invalid calendar period")

    def valid_amount(record, context, optional=True):
        amount = record.get("amount_minor")
        if amount is None and optional:
            return
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
            fail(f"{context}: amount_minor must be a nonnegative integer"
                 + (" or null" if optional else ""))
        if record.get("currency") not in scales:
            fail(f"{context}: undeclared currency")

    def index(records, key):
        result = {}
        for record in records:
            identity = record.get(key)
            if not isinstance(identity, str) or not identity or re.search(r"\s", identity):
                fail(f"{key}: missing or invalid stable identity")
                continue
            if identity in result:
                fail(f"duplicate {key}: {identity}")
            result[identity] = record
        return result

    def references(record, field, targets, context):
        values = record.get(field, [])
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            fail(f"{context}: {field} must be an ID list")
            return
        for value in values:
            if value not in targets:
                fail(f"{context}: missing {field} reference {value}")

    purchases = index(data["purchases"], "purchase_id")
    orders = index(data["orders"], "order_id")
    sources = index(data["sources"], "source_id")
    events = index(data["events"], "event_id")
    allocations = index(data["allocations"], "allocation_id")
    index(data["coverage"], "coverage_id")
    index(data["gaps"], "gap_id")
    valid_period(data.get("reporting_period"), "reporting_period")
    valid_date({"precision": "day", "value": data.get("as_of")}, "as_of")
    for source_id, source in sources.items():
        if not source.get("vendor") or not source.get("document_type"):
            fail(f"{source_id}: source needs vendor and document_type")
        if (not isinstance(source.get("proves", []), list) or
                set(source.get("proves", [])) - PROVES):
            fail(f"{source_id}: unsupported evidence capability")
        valid_date(source.get("document_date"), source_id + " document_date")
        for name in ("receipt_date", "service_period", "merchant_event_date", "notification_date"):
            valid_date(source.get(name), source_id + " " + name)
        valid_date({"precision": "day", "value": source.get("verified_at")}, source_id + " verified_at")
    for order_id, order in orders.items():
        if ":" not in order_id:
            fail(f"{order_id}: order_id must be vendor-namespaced")
        if not order.get("vendor"):
            fail(f"{order_id}: vendor missing")
        if order.get("allocation_status") not in ALLOCATION_STATUS:
            fail(f"{order_id}: invalid allocation_status")
        references(order, "source_ids", sources, order_id)
        valid_date(order.get("order_date"), order_id + " order_date")
        for name in ("replaces", "replaced_by"):
            other = order.get(name)
            if other and (other not in orders or other == order_id):
                fail(f"{order_id}: invalid {name}")
    for purchase_id, purchase in purchases.items():
        valid_amount(purchase, purchase_id)
        if purchase.get("amount_evidence") not in AMOUNT_EVIDENCE:
            fail(f"{purchase_id}: invalid amount_evidence")
        if purchase.get("purpose") not in PURPOSES:
            fail(f"{purchase_id}: invalid purpose")
        if purchase.get("allocation_status") not in ALLOCATION_STATUS:
            fail(f"{purchase_id}: invalid allocation_status")
        if not isinstance(purchase.get("contributes"), bool):
            fail(f"{purchase_id}: contributes must be boolean")
        references(purchase, "order_ids", orders, purchase_id)
        references(purchase, "source_ids", sources, purchase_id)
        if purchase.get("row_date_basis") not in {
                "order_date", "invoice_date", "receipt_date", "coverage_period"}:
            fail(f"{purchase_id}: invalid row_date_basis")
        for name in ("row_date", "order_date", "delivery_date", "invoice_date",
                     "receipt_date", "service_period"):
            valid_date(purchase.get(name), purchase_id + " " + name)
        for date in purchase.get("delivery_dates", []):
            valid_date(date, purchase_id + " delivery_dates")
        replacement = purchase.get("replacement_for")
        replacements = replacement if isinstance(replacement, list) else ([replacement] if replacement else [])
        if any(other == purchase_id or other not in purchases for other in replacements):
            fail(f"{purchase_id}: invalid replacement_for")
        if purchase.get("amount_evidence") == "final_vendor_amount":
            if not any("price" in sources.get(source_id, {}).get("proves", [])
                       for source_id in purchase.get("source_ids", [])):
                fail(f"{purchase_id}: final vendor amount lacks price evidence")
        for item in purchase.get("price_history", []):
            valid_amount(item, purchase_id + " price_history", optional=False)
            if item.get("amount_evidence") not in AMOUNT_EVIDENCE:
                fail(f"{purchase_id}: price_history invalid amount_evidence")
            references(item, "source_ids", sources, purchase_id + " price_history")
            valid_date({"precision": "day", "value": item.get("verified_at")},
                       purchase_id + " price_history verified_at")
    for event_id, event in events.items():
        valid_amount(event, event_id)
        if event.get("event_type") not in EVENT_TYPES:
            fail(f"{event_id}: invalid event_type")
        if event.get("confirmation") not in {"confirmed", "expected"}:
            fail(f"{event_id}: invalid confirmation")
        if event.get("allocation_status") not in ALLOCATION_STATUS:
            fail(f"{event_id}: invalid allocation_status")
        references(event, "source_ids", sources, event_id)
        references(event, "order_ids", orders, event_id)
        valid_date(event.get("event_date"), event_id + " event_date")
        for name in ("receipt_date", "invoice_date", "service_period"):
            valid_date(event.get(name), event_id + " " + name)
        valid_date({"precision": "day", "value": event.get("verified_at")},
                   event_id + " verified_at")
        if event.get("confirmation") == "confirmed":
            if not any(event.get("event_type") in sources.get(source_id, {}).get("proves", [])
                       for source_id in event.get("source_ids", [])):
                fail(f"{event_id}: confirmed event lacks matching source capability")
            if event.get("event_date") is not None and not any(
                    "merchant_event_date" in sources.get(source_id, {}).get("proves", [])
                    and sources[source_id].get("merchant_event_date") == event["event_date"]
                    for source_id in event.get("source_ids", []) if source_id in sources):
                fail(f"{event_id}: merchant event date lacks matching date evidence")
        original = event.get("original_event_id")
        if original and (original not in events or original == event_id):
            fail(f"{event_id}: invalid original_event_id")
        elif original and event.get("event_type") == "refund":
            if (events[original].get("event_type") != "charge" or
                    events[original].get("currency") != event.get("currency")):
                fail(f"{event_id}: refund original must be a same-currency charge")
    allocated = defaultdict(int)
    signatures = set()
    for allocation_id, allocation in allocations.items():
        valid_amount(allocation, allocation_id, optional=False)
        event = events.get(allocation.get("event_id"))
        purchase_id = allocation.get("purchase_id")
        purchase = purchases.get(purchase_id)
        order_id = allocation.get("order_id")
        if not event or (purchase_id is not None and not purchase) or (not purchase and not order_id):
            fail(f"{allocation_id}: allocation needs existing event and purchase or order")
            continue
        if (event.get("currency") != allocation.get("currency") or
                (purchase and purchase.get("currency") != allocation.get("currency"))):
            fail(f"{allocation_id}: allocation currencies disagree")
        if order_id and (order_id not in orders or
                         (purchase and order_id not in purchase.get("order_ids", []))):
            fail(f"{allocation_id}: order must exist and belong to purchase")
        if order_id and event.get("order_ids") and order_id not in event["order_ids"]:
            fail(f"{allocation_id}: order conflicts with evidenced event order relationship")
        signature = (allocation.get("event_id"), allocation.get("purchase_id"), order_id)
        if signature in signatures:
            fail(f"{allocation_id}: duplicate event/purchase/order allocation")
        signatures.add(signature)
        amount = allocation.get("amount_minor")
        if isinstance(amount, int) and not isinstance(amount, bool):
            allocated[allocation["event_id"]] += amount
    for event_id, event in events.items():
        amount = event.get("amount_minor")
        if isinstance(amount, int) and not isinstance(amount, bool):
            if event.get("allocation_status") in {"all_project", "mixed_partial"}:
                if allocated[event_id] != amount:
                    fail(f"{event_id}: allocations {allocated[event_id]} do not equal "
                         f"published project amount {amount}")
            elif allocated[event_id] > amount:
                fail(f"{event_id}: unresolved allocations exceed published event amount")
    # Corroborating receipt and invoice documents belong to one event. Catch a
    # second copy of that event without merging conflicting records silently.
    seen_documents, seen_references = {}, {}
    for event_id, event in events.items():
        signature = (event.get("vendor"), event.get("event_type"),
                     json.dumps(event.get("event_date"), sort_keys=True),
                     event.get("currency"), event.get("amount_minor"))
        reference = event.get("reference")
        if reference:
            key = (event.get("vendor"), event.get("event_type"), reference)
            if key in seen_references:
                fail(f"{event_id}: duplicate merchant event reference with {seen_references[key]}")
            seen_references[key] = event_id
        for source_id in event.get("source_ids", []):
            source = sources.get(source_id, {})
            if event.get("event_type") not in source.get("proves", []):
                continue
            key = signature + (source.get("vendor"), source.get("document_type"),
                               source.get("reference", source_id))
            if key in seen_documents and seen_documents[key] != event_id:
                fail(f"{event_id}: duplicate payment document with {seen_documents[key]}")
            seen_documents[key] = event_id
    for record in data["coverage"]:
        context = record.get("coverage_id", "coverage")
        references(record, "source_ids", sources, context)
        references(record, "order_ids", orders, context)
        if record.get("coverage") not in {"partial", "unknown", "complete"}:
            fail(f"{context}: invalid coverage classification")
        valid_period(record.get("examined_period"), context + " examined_period", optional=True)
        valid_period(record.get("complete_period"), context + " complete_period", optional=True)
        valid_date({"precision": "day", "value": record.get("checked_at")}, context + " checked_at")
        if record.get("coverage") == "complete" and not record.get("complete_period"):
            fail(f"{context}: complete coverage requires a stated complete_period")
        if record.get("coverage") != "complete" or not record.get("complete_period"):
            warnings.append(f"{context}: evidence coverage is {record.get('coverage', 'unknown')}")
    for gap in data["gaps"]:
        context = gap.get("gap_id", "gap")
        for name, targets in (("purchase_ids", purchases), ("order_ids", orders),
                              ("event_ids", events), ("source_ids", sources)):
            references(gap, name, targets, context)
        if not gap.get("missing_fact"):
            fail(f"{context}: missing_fact is required")
    if data["gaps"]:
        warnings.append(f"{len(data['gaps'])} authored evidence gap(s) remain")
    # Replacement chains cannot loop, even when several paid purchases supply
    # one replacement. Their cost is never erased by the relationship.
    def visit(identity, active, complete):
        if identity in active:
            fail(f"{identity}: replacement relationship cycle")
            return
        if identity in complete:
            return
        active.add(identity)
        value = purchases[identity].get("replacement_for", [])
        for original in (value if isinstance(value, list) else [value]):
            if original in purchases:
                visit(original, active, complete)
        active.remove(identity)
        complete.add(identity)
    complete = set()
    for identity in purchases:
        visit(identity, set(), complete)


def _relationships(data):
    purchases = {item["purchase_id"]: item for item in data["purchases"]}
    orders = {item["order_id"]: item for item in data["orders"]}
    events = {item["event_id"]: item for item in data["events"]}
    for purchase in purchases.values():
        purchase["event_ids"] = []
    for order in orders.values():
        order["purchase_ids"] = sorted(purchase["purchase_id"] for purchase in purchases.values()
                                       if order["order_id"] in purchase["order_ids"])
        order["event_ids"] = []
    for event in events.values():
        related = [item for item in data["allocations"] if item["event_id"] == event["event_id"]]
        event["purchase_ids"] = sorted({item["purchase_id"] for item in related
                                        if item.get("purchase_id")})
        event["order_ids"] = sorted(set(event.get("order_ids", [])) |
                                    {item["order_id"] for item in related if item.get("order_id")})
        event["unallocated_to_purchase_minor"] = sum(
            item["amount_minor"] for item in related if not item.get("purchase_id"))
        event["allocation_ids"] = sorted(item["allocation_id"] for item in related)
        for purchase_id in event["purchase_ids"]:
            purchases[purchase_id]["event_ids"].append(event["event_id"])
        for order_id in event["order_ids"]:
            orders[order_id]["event_ids"].append(event["event_id"])
    for purchase in purchases.values():
        related = [events[key] for key in purchase["event_ids"]]
        charges = [item for item in related if item["event_type"] == "charge"
                   and item["confirmation"] == "confirmed"
                   and item["allocation_status"] != "unresolved"]
        refunds = [item for item in related if item["event_type"] == "refund"
                   and item["confirmation"] == "confirmed"
                   and item["allocation_status"] != "unresolved"]
        purchase["merchant_charge_allocated_minor"] = sum(
            allocation["amount_minor"] for allocation in data["allocations"]
            if allocation.get("purchase_id") == purchase["purchase_id"]
            and events[allocation["event_id"]]["event_type"] == "charge"
            and events[allocation["event_id"]]["confirmation"] == "confirmed"
            and events[allocation["event_id"]]["allocation_status"] != "unresolved")
        purchase["merchant_refund_allocated_minor"] = sum(
            allocation["amount_minor"] for allocation in data["allocations"]
            if allocation.get("purchase_id") == purchase["purchase_id"]
            and events[allocation["event_id"]]["event_type"] == "refund"
            and events[allocation["event_id"]]["confirmation"] == "confirmed"
            and events[allocation["event_id"]]["allocation_status"] != "unresolved")
        if charges:
            purchase["payment_evidence"] = ("merchant_charge_and_refund" if refunds
                                            else "merchant_charge")
            if (purchase["amount_minor"] is not None and
                    purchase["merchant_charge_allocated_minor"] < purchase["amount_minor"]):
                purchase["payment_evidence"] = ("merchant_charge_partial_and_refund" if refunds
                                                else "merchant_charge_partial")
        elif refunds:
            purchase["payment_evidence"] = "merchant_refund_only"
        elif (purchase["amount_minor"] == 0 and purchase.get("replacement_for")
              and purchase["amount_evidence"] == "final_vendor_amount"):
            purchase["payment_evidence"] = "zero_price_replacement"
        else:
            purchase["payment_evidence"] = "unknown"
        purchase["split_charge"] = len(charges) > 1
    for order in orders.values():
        order["event_ids"] = sorted(set(order["event_ids"]))


def _months(period):
    start = dt.date.fromisoformat(period["start"]).replace(day=1)
    end = dt.date.fromisoformat(period["end"]).replace(day=1)
    result = []
    while start <= end:
        result.append(start.strftime("%Y-%m"))
        start = dt.date(start.year + (start.month == 12), start.month % 12 + 1, 1)
    return result


def summaries(data):
    currencies = sorted(data["currency_scales"])
    procurement_fields = ("final_vendor_amount_minor", "estimate_minor",
                          "legacy_unverified_minor", "total_minor")
    payment_fields = ("charges_minor", "refunds_minor", "net_minor",
                      "authorizations_minor", "noncash_credits_minor",
                      "unresolved_project_share_minor")

    def view(fields, id_field):
        monthly, undated, totals = {}, {}, {}
        for currency in currencies:
            totals[currency] = dict(currency=currency, **{name: 0 for name in fields})
            undated[currency] = dict(currency=currency, **{name: 0 for name in fields},
                                     **{id_field: [], "unknown_amount_ids": []})
            for month in _months(data["reporting_period"]):
                monthly[(month, currency)] = dict(
                    month=month, currency=currency, **{name: 0 for name in fields},
                    **{id_field: [], "unknown_amount_ids": [],
                       "evidence_scope": "retrieved_records_only"})
        return monthly, undated, totals

    def bucket(monthly, undated, date, currency, fields, id_field):
        month = date_month(date)
        if month == "undated_unallocated":
            return undated[currency]
        key = (month, currency)
        if key not in monthly:
            monthly[key] = dict(month=month, currency=currency, **{name: 0 for name in fields},
                                **{id_field: [], "unknown_amount_ids": [],
                                   "evidence_scope": "retrieved_records_only"})
        return monthly[key]

    pm, pu, pt = view(procurement_fields, "purchase_ids")
    em, eu, et = view(payment_fields, "event_ids")
    active, excluded, cancelled = [], [], []
    purpose_totals = defaultdict(int)
    for purchase in data["purchases"]:
        if not purchase["contributes"]:
            excluded.append(purchase["purchase_id"])
            continue
        if purchase["fulfillment"] == "CANCELLED":
            cancelled.append(purchase["purchase_id"])
            continue
        if purchase["fulfillment"] not in ACTIVE_STATUSES:
            excluded.append(purchase["purchase_id"])
            continue
        active.append(purchase)
        currency, amount = purchase["currency"], purchase["amount_minor"]
        target = bucket(pm, pu, purchase["order_date"], currency, procurement_fields, "purchase_ids")
        target["purchase_ids"].append(purchase["purchase_id"])
        if amount is None:
            target["unknown_amount_ids"].append(purchase["purchase_id"])
            continue
        field = purchase["amount_evidence"] + "_minor"
        target[field] += amount
        target["total_minor"] += amount
        pt[currency][field] += amount
        pt[currency]["total_minor"] += amount
        purpose_totals[(currency, purchase["purpose"])] += amount
    expected = []
    for event in data["events"]:
        currency, amount = event["currency"], event["amount_minor"]
        target = bucket(em, eu, event["event_date"], currency, payment_fields, "event_ids")
        target["event_ids"].append(event["event_id"])
        if event["confirmation"] != "confirmed":
            expected.append(event["event_id"])
            continue
        if amount is None:
            target["unknown_amount_ids"].append(event["event_id"])
            continue
        if event["allocation_status"] == "unresolved":
            target["unresolved_project_share_minor"] += amount
            et[currency]["unresolved_project_share_minor"] += amount
            continue
        field = {"charge": "charges_minor", "refund": "refunds_minor",
                 "authorization": "authorizations_minor",
                 "noncash_credit": "noncash_credits_minor"}[event["event_type"]]
        target[field] += amount
        et[currency][field] += amount
        if event["event_type"] in {"charge", "refund"}:
            signed = amount if event["event_type"] == "charge" else -amount
            target["net_minor"] += signed
            et[currency]["net_minor"] += signed
    for value in list(pm.values()) + list(pu.values()):
        value["purchase_ids"].sort()
        value["unknown_amount_ids"].sort()
    for value in list(em.values()) + list(eu.values()):
        value["event_ids"].sort()
        value["unknown_amount_ids"].sort()
    status_totals = defaultdict(lambda: {"amount_minor": 0, "unknown_amount_ids": [],
                                        "purchase_ids": []})
    for purchase in data["purchases"]:
        if not purchase["contributes"]:
            continue
        target = status_totals[(purchase["currency"], purchase["fulfillment"])]
        target["purchase_ids"].append(purchase["purchase_id"])
        if purchase["amount_minor"] is None:
            target["unknown_amount_ids"].append(purchase["purchase_id"])
        else:
            target["amount_minor"] += purchase["amount_minor"]
    uncertainty_amounts = []
    for currency in currencies:
        currency_purchases = [purchase for purchase in active if purchase["currency"] == currency]
        currency_events = [event for event in data["events"] if event["currency"] == currency]
        known_sum = lambda group: sum(item["amount_minor"] for item in group
                                      if item["amount_minor"] is not None)
        uncertainty_amounts.append({
            "currency": currency,
            "estimated_purchase_minor": known_sum(p for p in currency_purchases if p["amount_evidence"] == "estimate"),
            "legacy_unverified_purchase_minor": known_sum(p for p in currency_purchases if p["amount_evidence"] == "legacy_unverified"),
            "undated_unallocated_purchase_minor": known_sum(p for p in currency_purchases if date_month(p["order_date"]) == "undated_unallocated"),
            "purchases_without_merchant_charge_minor": known_sum(p for p in currency_purchases if p["payment_evidence"] in {"unknown", "merchant_refund_only"}),
            "partial_charge_purchase_minor": known_sum(p for p in currency_purchases if p["payment_evidence"].startswith("merchant_charge_partial")),
            "unresolved_allocation_purchase_minor": known_sum(p for p in currency_purchases if p["allocation_status"] == "unresolved"),
            "unknown_amount_purchase_count": sum(p["amount_minor"] is None for p in currency_purchases),
            "unknown_amount_event_count": sum(e["amount_minor"] is None for e in currency_events),
            "undated_charge_minor": eu[currency]["charges_minor"],
            "undated_refund_minor": eu[currency]["refunds_minor"],
            "unresolved_event_minor": et[currency]["unresolved_project_share_minor"],
            "order_only_charge_allocation_minor": sum(
                e["unallocated_to_purchase_minor"] for e in currency_events
                if e["event_type"] == "charge" and e["confirmation"] == "confirmed"),
        })
    return {
        "procurement": {
            "basis": "Current project purchase amount by order calendar month; "
                     "cancellations and noncontributing summaries excluded; returns "
                     "retain original acquisition amount; refunds are separate events.",
            "monthly": [pm[key] for key in sorted(pm)],
            "undated_unallocated": [pu[key] for key in sorted(pu)],
            "totals": [pt[key] for key in sorted(pt)],
            "cancelled_purchase_ids": sorted(cancelled),
            "excluded_purchase_ids": sorted(excluded),
            "purpose_totals": [dict(currency=key[0], purpose=key[1], amount_minor=value)
                               for key, value in sorted(purpose_totals.items())],
        },
        "merchant_payments": {
            "basis": "Confirmed merchant-evidenced project charges and issued monetary "
                     "refunds by merchant event calendar month; bank posting is outside "
                     "this ledger. Expected events, authorizations, noncash credits and "
                     "unresolved project shares are excluded from charges/refunds/net.",
            "monthly": [em[key] for key in sorted(em)],
            "undated_unallocated": [eu[key] for key in sorted(eu)],
            "totals": [et[key] for key in sorted(et)],
            "expected_event_ids": sorted(expected),
        },
        "fulfillment": {
            "basis": "Current procurement status, independently of payment evidence.",
            "outstanding_purchase_ids": sorted(purchase["purchase_id"] for purchase in active
                                               if purchase["fulfillment"] in OUTSTANDING_STATUSES),
            "returned_without_evidenced_refund_purchase_ids": sorted(
                p["purchase_id"] for p in data["purchases"]
                if p["fulfillment"] == "RETURNED" and p["contributes"]
                and p["merchant_refund_allocated_minor"] == 0),
            "cancelled_with_evidenced_charge_purchase_ids": sorted(
                p["purchase_id"] for p in data["purchases"]
                if p["fulfillment"] == "CANCELLED" and p["contributes"]
                and p["merchant_charge_allocated_minor"] > 0),
            "expected_refund_event_ids": sorted(e["event_id"] for e in data["events"]
                                               if e["event_type"] == "refund"
                                               and e["confirmation"] == "expected"),
            "by_status": [dict(currency=key[0], fulfillment=key[1], **value)
                          for key, value in sorted(status_totals.items())],
        },
        "uncertainty": {
            "basis": "Zero numeric activity means no retrieved records contributed; "
                     "it does not establish complete source coverage or zero actual spending. "
                     "Uncertainty categories overlap; purchase amounts without charge evidence "
                     "and partially evidenced purchase amounts are not unpaid obligations.",
            "by_currency": uncertainty_amounts,
            "unknown_amount_purchase_ids": sorted(p["purchase_id"] for p in active if p["amount_minor"] is None),
            "undated_unallocated_purchase_ids": sorted(p["purchase_id"] for p in active if date_month(p["order_date"]) == "undated_unallocated"),
            "purchases_without_merchant_charge": sorted(p["purchase_id"] for p in active if p["payment_evidence"] in {"unknown", "merchant_refund_only"} and p["amount_minor"] != 0),
            "partial_merchant_charge_purchase_ids": sorted(p["purchase_id"] for p in active if p["payment_evidence"].startswith("merchant_charge_partial")),
            "estimated_purchase_ids": sorted(p["purchase_id"] for p in active if p["amount_evidence"] == "estimate"),
            "legacy_unverified_purchase_ids": sorted(p["purchase_id"] for p in active if p["amount_evidence"] == "legacy_unverified"),
            "unresolved_allocation_purchase_ids": sorted(p["purchase_id"] for p in active if p["allocation_status"] == "unresolved"),
            "unknown_amount_event_ids": sorted(e["event_id"] for e in data["events"] if e["amount_minor"] is None),
            "undated_unallocated_event_ids": sorted(e["event_id"] for e in data["events"] if date_month(e["event_date"]) == "undated_unallocated"),
            "unresolved_allocation_event_ids": sorted(e["event_id"] for e in data["events"] if e["allocation_status"] == "unresolved"),
            "order_only_allocation_event_ids": sorted(e["event_id"] for e in data["events"] if e["unallocated_to_purchase_minor"]),
            "incomplete_coverage_ids": sorted(c["coverage_id"] for c in data["coverage"] if c["coverage"] != "complete"),
            "authored_gap_ids": sorted(g["gap_id"] for g in data["gaps"]),
        },
    }


def export_json(data):
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def export_csv(data):
    """A typed rectangular table; arrays and precision dates are JSON cells."""
    records = [("metadata", {key: value for key, value in data.items()
                             if key in {"schema_version", "as_of", "reporting_period",
                                        "currency_scales", "input_fingerprint"}})]
    if "summary" in data:
        records[0][1].update({name + "_basis": summary["basis"]
                              for name, summary in data["summary"].items()})
    for table in ("purchases", "orders", "events", "allocations", "sources", "coverage", "gaps"):
        records.extend((table[:-1] if table != "coverage" else table, row)
                       for row in data[table])
    for name in ("procurement", "merchant_payments"):
        summary = data.get("summary", {}).get(name, {})
        for part in ("monthly", "undated_unallocated", "totals"):
            records.extend((name + "_" + part, row) for row in summary.get(part, []))
    if "summary" in data:
        records.append(("fulfillment", data["summary"]["fulfillment"]))
        records.append(("uncertainty", data["summary"]["uncertainty"]))
    records.append(("validation", data["validation"]))
    fields = sorted({key for _, row in records for key in row})
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["record_type"] + fields, lineterminator="\n")
    writer.writeheader()
    for kind, row in records:
        flat = {"record_type": kind}
        for key, value in row.items():
            if isinstance(value, (dict, list)):
                flat[key] = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            elif isinstance(value, bool):
                flat[key] = "true" if value else "false"
            elif value is None:
                flat[key] = ""
            else:
                flat[key] = value
        writer.writerow(flat)
    return output.getvalue()


def render_report(data, audit=False):
    lines = [f"Project ledger as of {data.get('as_of')} ({data.get('input_fingerprint')})"]
    if data["validation"]["errors"]:
        lines.append("Integrity errors:")
        lines.extend("  " + error for error in data["validation"]["errors"])
        return "\n".join(lines) + "\n"
    summary, scales = data["summary"], data["currency_scales"]
    lines.append("Procurement by order month — current project amounts:")
    lines.append("Month | Currency | Final vendor amount | Estimate | Legacy unverified | Total | Payment-evidence gaps")
    missing = set(summary["uncertainty"]["purchases_without_merchant_charge"])
    for row in summary["procurement"]["monthly"] + summary["procurement"]["undated_unallocated"]:
        amounts = [format_minor(row[key], row["currency"], scales)
                   for key in ("final_vendor_amount_minor", "estimate_minor",
                               "legacy_unverified_minor", "total_minor")]
        lines.append(" | ".join([row.get("month", "undated/unallocated"), row["currency"]]
                                + amounts + [str(len(missing & set(row["purchase_ids"])))]))
    for row in summary["procurement"]["totals"]:
        lines.append(f"Procurement total ({row['currency']}): "
                     f"{format_minor(row['total_minor'], row['currency'], scales)}")
    lines.append("Merchant-evidenced payments by merchant event month:")
    lines.append("Month | Currency | Charges | Issued refunds | Net | Authorizations | Noncash credits")
    for row in summary["merchant_payments"]["monthly"] + summary["merchant_payments"]["undated_unallocated"]:
        lines.append(" | ".join([row.get("month", "undated/unallocated"), row["currency"]]
                                + [format_minor(row[key], row["currency"], scales)
                                   for key in ("charges_minor", "refunds_minor", "net_minor",
                                               "authorizations_minor", "noncash_credits_minor")]))
    for row in summary["merchant_payments"]["totals"]:
        lines.append(f"Merchant evidence total ({row['currency']}): charges "
                     f"{format_minor(row['charges_minor'], row['currency'], scales)}, "
                     f"refunds {format_minor(row['refunds_minor'], row['currency'], scales)}, "
                     f"net {format_minor(row['net_minor'], row['currency'], scales)}")
    lines.append("Fulfillment amounts do not establish unpaid obligations:")
    for row in summary["fulfillment"]["by_status"]:
        lines.append(f"  {row['fulfillment']}: {format_minor(row['amount_minor'], row['currency'], scales)} "
                     f"({len(row['purchase_ids'])} records; {len(row['unknown_amount_ids'])} unknown amounts)")
    lines.append(summary["uncertainty"]["basis"])
    lines.append("Evidence limitations:")
    for amounts in summary["uncertainty"]["by_currency"]:
        lines.append(f"  Known purchase valuation without merchant charge evidence "
                     f"({amounts['currency']}): "
                     f"{format_minor(amounts['purchases_without_merchant_charge_minor'], amounts['currency'], scales)}")
        lines.append(f"  Undated/unallocated procurement ({amounts['currency']}): "
                     f"{format_minor(amounts['undated_unallocated_purchase_minor'], amounts['currency'], scales)}")
    for key, value in summary["uncertainty"].items():
        if isinstance(value, list) and key != "by_currency":
            lines.append(f"  {key}: {len(value)}")
    lines.extend("  " + warning for warning in data["validation"]["warnings"])
    if audit:
        for coverage in data["coverage"]:
            lines.append(f"  Coverage {coverage['coverage_id']}: {coverage['vendor']} / "
                         f"{coverage['stream']} / {coverage['evidence_type']}; "
                         f"checked {coverage['checked_at']}; examined {coverage.get('examined_period')}; "
                         f"complete {coverage.get('complete_period')}; {coverage['coverage']}")
        for gap in data["gaps"]:
            lines.append(f"  Gap {gap['gap_id']}: {gap['missing_fact']}; "
                         f"sources checked: {gap.get('sources_checked', [])}")
    return "\n".join(lines) + "\n"
