#!/usr/bin/env python3
"""Synthetic ledger contract tests. Run directly or with unittest discovery."""
import copy
import csv
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from _ledger_analysis import (analyze, date_month, export_csv, export_json,
                              input_fingerprint, parse_date)
from _ledger_totals import parse, reconcile_orders, variables_from_totals

SCRIPT = Path(__file__).with_name("_ledger_totals.py")
TODAY = "2026-10-04"


def day(value):
    return {"precision": "day", "value": value}


def row(identity="pur-a", amount="10.00", status="ACQUIRED", ordered="2026-01-31"):
    return {
        "purchase_id": identity, "cost": Decimal(amount) if amount is not None else None,
        "status": status, "section": "1. Test components", "part": "Test component",
        "description": "Test component", "ordered": ordered, "delivered": "",
        "quantity": 1, "quantity_text": "1", "price_basis": "row_total",
        "unit_price": None, "orders": [], "line": 5,
    }


def fixture(rows):
    return {
        "schema_version": 1, "as_of": TODAY,
        "reporting_period": {"start": "2026-01-01", "end": "2026-10-04"},
        "currency_scales": {"USD": 2},
        "purchases": {
            item["purchase_id"]: {
                "vendor": "Test Vendor", "purpose": "components",
                "amount_evidence": "legacy_unverified", "order_ids": [],
                "allocation_status": "all_project", "source_ids": [],
            } for item in rows
        },
        "orders": {}, "sources": {}, "events": [], "allocations": [],
        "coverage": [], "gaps": [], "details": {},
    }


def add_source(evidence, identity, proves, vendor="Test Vendor", reference=None):
    evidence["sources"][identity] = {
        "vendor": vendor, "document_type": "synthetic_document",
        "reference": reference or identity, "document_date": day("2026-02-01"),
        "proves": proves, "verified_at": TODAY,
    }


def add_order(evidence, identity, purchases):
    evidence["orders"][identity] = {
        "vendor": "Test Vendor", "reference": identity.split(":", 1)[1],
        "order_date": day("2026-01-31"), "allocation_status": "all_project",
        "source_ids": [],
    }
    for purchase_id in purchases:
        evidence["purchases"][purchase_id]["order_ids"].append(identity)


def add_event(evidence, identity, amount, purchases, event_type="charge",
              date="2026-02-01", confirmation="confirmed", allocation_status="all_project",
              source_ids=None):
    if source_ids is None:
        source_ids = ["src-" + identity]
        add_source(evidence, source_ids[0],
                   [event_type] + (["merchant_event_date"] if date else []))
        if date:
            evidence["sources"][source_ids[0]]["merchant_event_date"] = day(date)
    elif date:
        evidence["sources"][source_ids[0]]["proves"].append("merchant_event_date")
        evidence["sources"][source_ids[0]]["merchant_event_date"] = day(date)
    event = {
        "event_id": identity, "vendor": "Test Vendor", "event_type": event_type,
        "confirmation": confirmation, "event_date": day(date) if date else None,
        "amount_minor": amount, "currency": "USD",
        "allocation_status": allocation_status, "source_ids": source_ids,
        "verified_at": TODAY,
    }
    evidence["events"].append(event)
    for number, (purchase_id, allocated) in enumerate(purchases):
        evidence["allocations"].append({
            "allocation_id": f"alloc-{identity}-{number}", "event_id": identity,
            "purchase_id": purchase_id, "amount_minor": allocated, "currency": "USD",
        })
    return event


class AnalysisTest(unittest.TestCase):
    def checked(self, rows, evidence):
        data = analyze(rows, evidence, "sha256:synthetic")
        self.assertEqual([], data["validation"]["errors"])
        return data

    def total(self, data, view, field):
        return data["summary"][view]["totals"][0][field]

    def purchase(self, data, identity):
        return next(item for item in data["purchases"] if item["purchase_id"] == identity)

    def test_estimate_finalization_keeps_identity_and_history(self):
        rows = [row(amount="12.00", status="ON-ORDER")]
        evidence = fixture(rows)
        evidence["purchases"]["pur-a"]["amount_evidence"] = "estimate"
        first = self.checked(rows, evidence)
        self.assertEqual(1200, self.total(first, "procurement", "estimate_minor"))
        add_source(evidence, "final-invoice", ["price"])
        evidence["purchases"]["pur-a"].update({
            "amount_evidence": "final_vendor_amount", "source_ids": ["final-invoice"],
            "price_history": [{"amount_minor": 1200, "currency": "USD",
                               "amount_evidence": "estimate", "verified_at": TODAY,
                               "source_ids": []}],
        })
        rows[0]["cost"] = Decimal("11.37")
        second = self.checked(rows, evidence)
        self.assertEqual("pur-a", second["purchases"][0]["purchase_id"])
        self.assertEqual(1137, self.total(second, "procurement", "final_vendor_amount_minor"))
        self.assertEqual(0, self.total(second, "merchant_payments", "charges_minor"))
        self.assertEqual(1, len(second["purchases"]))

    def test_on_order_can_be_charged_and_acquired_can_have_unknown_payment(self):
        rows = [row(status="ON-ORDER"), row("pur-b", "25", ordered="2026-02-04")]
        evidence = fixture(rows)
        add_event(evidence, "evt-a", 1000, [("pur-a", 1000)])
        data = self.checked(rows, evidence)
        self.assertEqual("merchant_charge", self.purchase(data, "pur-a")["payment_evidence"])
        self.assertEqual("unknown", self.purchase(data, "pur-b")["payment_evidence"])
        self.assertEqual(["pur-a"], data["summary"]["fulfillment"]["outstanding_purchase_ids"])
        self.assertEqual(["pur-b"], data["summary"]["uncertainty"]["purchases_without_merchant_charge"])

    def test_split_and_consolidated_charges(self):
        rows = [row(amount="30"), row("pur-b", "40")]
        evidence = fixture(rows)
        add_order(evidence, "test:order-a", ["pur-a"])
        add_order(evidence, "test:order-b", ["pur-b"])
        add_event(evidence, "evt-split", 1000, [("pur-a", 1000)])
        add_event(evidence, "evt-consolidated", 6000, [("pur-a", 2000), ("pur-b", 4000)])
        evidence["allocations"][0]["order_id"] = "test:order-a"
        evidence["allocations"][1]["order_id"] = "test:order-a"
        evidence["allocations"][2]["order_id"] = "test:order-b"
        data = self.checked(rows, evidence)
        self.assertEqual(7000, self.total(data, "merchant_payments", "charges_minor"))
        self.assertTrue(self.purchase(data, "pur-a")["split_charge"])
        self.assertEqual(["test:order-a", "test:order-b"], data["events"][0]["order_ids"])

    def test_receipt_and_invoice_corroborate_one_payment(self):
        rows = [row()]
        evidence = fixture(rows)
        add_source(evidence, "receipt", ["charge"])
        add_source(evidence, "invoice", ["price", "charge"])
        add_event(evidence, "evt-a", 1000, [("pur-a", 1000)], source_ids=["invoice", "receipt"])
        data = self.checked(rows, evidence)
        self.assertEqual(1000, self.total(data, "merchant_payments", "charges_minor"))
        duplicate = copy.deepcopy(evidence["events"][0])
        duplicate["event_id"] = "evt-duplicate"
        evidence["events"].append(duplicate)
        evidence["allocations"].append({
            "allocation_id": "alloc-copy", "event_id": "evt-duplicate",
            "purchase_id": "pur-a", "amount_minor": 1000, "currency": "USD",
        })
        errors = analyze(rows, evidence)["validation"]["errors"]
        self.assertTrue(any("duplicate payment document" in error for error in errors))

    def test_cancellations_do_not_erase_charge_or_invent_refund(self):
        rows = [row(status="CANCELLED"), row("pur-b", "20", status="CANCELLED")]
        evidence = fixture(rows)
        add_event(evidence, "evt-charged", 2000, [("pur-b", 2000)])
        add_event(evidence, "evt-refund-expected", 2000, [("pur-b", 2000)],
                  event_type="refund", confirmation="expected")
        data = self.checked(rows, evidence)
        self.assertEqual(0, self.total(data, "procurement", "total_minor"))
        self.assertEqual(2000, self.total(data, "merchant_payments", "charges_minor"))
        self.assertEqual(0, self.total(data, "merchant_payments", "refunds_minor"))
        self.assertEqual("unknown", self.purchase(data, "pur-a")["payment_evidence"])
        self.assertEqual(["pur-a", "pur-b"], data["summary"]["procurement"]["cancelled_purchase_ids"])

    def test_partial_refund_and_zero_price_replacement(self):
        rows = [row(amount="30", status="REPLACED"), row("pur-b", "0")]
        evidence = fixture(rows)
        add_event(evidence, "evt-original", 3000, [("pur-a", 3000)])
        refund = add_event(evidence, "evt-refund", 500, [("pur-a", 500)], event_type="refund")
        refund["original_event_id"] = "evt-original"
        add_source(evidence, "replacement", ["price"])
        evidence["purchases"]["pur-b"].update({
            "replacement_for": ["pur-a"], "amount_evidence": "final_vendor_amount",
            "source_ids": ["replacement"],
        })
        data = self.checked(rows, evidence)
        self.assertEqual(3000, self.total(data, "procurement", "total_minor"))
        self.assertEqual(2500, self.total(data, "merchant_payments", "net_minor"))
        self.assertEqual("zero_price_replacement", self.purchase(data, "pur-b")["payment_evidence"])

    def test_authorizations_store_credit_and_expected_events_are_not_cash(self):
        rows = [row()]
        evidence = fixture(rows)
        add_event(evidence, "evt-charge", 600, [("pur-a", 600)])
        add_event(evidence, "evt-credit", 400, [("pur-a", 400)], event_type="noncash_credit")
        add_event(evidence, "evt-authorization", 1000, [("pur-a", 1000)], event_type="authorization")
        add_event(evidence, "evt-expected", 1000, [("pur-a", 1000)], confirmation="expected")
        data = self.checked(rows, evidence)
        self.assertEqual(600, self.total(data, "merchant_payments", "charges_minor"))
        self.assertEqual(400, self.total(data, "merchant_payments", "noncash_credits_minor"))
        self.assertEqual(1000, self.total(data, "merchant_payments", "authorizations_minor"))

    def test_mixed_project_share_uses_allowlists_and_strips_links_and_status(self):
        rows = [row()]
        rows[0]["description"] = "Project part [receipt](https://mail.invalid/private-locator)"
        rows[0]["status_text"] = "ACQUIRED (Tracking SYNTHETIC_PRIVATE_TRACKING)"
        evidence = fixture(rows)
        evidence["purchases"]["pur-a"].update({
            "allocation_status": "mixed_partial",
            "personal_item": "SYNTHETIC_PRIVATE_ITEM", "full_order_total": 99000,
        })
        add_order(evidence, "test:mixed", ["pur-a"])
        evidence["orders"]["test:mixed"]["private_customer_id"] = "SYNTHETIC_PRIVATE_CUSTOMER"
        add_event(evidence, "evt-mixed", 1000, [("pur-a", 1000)], allocation_status="mixed_partial")
        evidence["events"][0]["private_instrument"] = "SYNTHETIC_PRIVATE_INSTRUMENT"
        data = self.checked(rows, evidence)
        for output in (export_json(data), export_csv(data)):
            self.assertNotIn("SYNTHETIC_PRIVATE", output)
            self.assertNotIn("private-locator", output)
            self.assertNotIn("99000", output)
        self.assertEqual("mixed_partial", data["events"][0]["allocation_status"])

    def test_prepaid_topup_and_noncontributing_usage(self):
        rows = [row(amount="50"), row("pur-usage", "35")]
        evidence = fixture(rows)
        evidence["purchases"]["pur-a"]["stream"] = "prepaid_top_up"
        evidence["purchases"]["pur-usage"].update({
            "stream": "prepaid_usage", "contributes": False,
            "service_period": {"precision": "range", "start": "2026-02-01", "end": "2026-02-28"},
        })
        add_event(evidence, "evt-topup", 5000, [("pur-a", 5000)])
        data = self.checked(rows, evidence)
        self.assertEqual(5000, self.total(data, "procurement", "total_minor"))
        self.assertEqual(5000, self.total(data, "merchant_payments", "charges_minor"))
        self.assertEqual("prepaid_top_up", self.purchase(data, "pur-a")["stream"])

    def test_order_month_and_charge_month_are_distinct(self):
        rows = [row(ordered="2026-01-31")]
        evidence = fixture(rows)
        add_event(evidence, "evt-a", 1000, [("pur-a", 1000)], date="2026-02-01")
        data = self.checked(rows, evidence)
        months = data["summary"]["procurement"]["monthly"]
        self.assertEqual(1000, months[0]["total_minor"])
        self.assertEqual(0, months[1]["total_minor"])
        payments = data["summary"]["merchant_payments"]["monthly"]
        self.assertEqual(0, payments[0]["charges_minor"])
        self.assertEqual(1000, payments[1]["charges_minor"])

    def test_date_precision_unknown_amount_and_actual_zero(self):
        rows = [row(ordered="", amount=None), row("pur-zero", "0", ordered="2026-03"),
                row("pur-range", "15", ordered="2026-01-17 → 2026-04-18")]
        evidence = fixture(rows)
        add_event(evidence, "evt-unknown", None, [], date=None)
        add_event(evidence, "evt-zero", 0, [("pur-zero", 0)], date="2026-03-01")
        data = self.checked(rows, evidence)
        self.assertIsNone(self.purchase(data, "pur-a")["amount_minor"])
        self.assertEqual(0, self.purchase(data, "pur-zero")["amount_minor"])
        self.assertEqual("month", self.purchase(data, "pur-zero")["order_date"]["precision"])
        self.assertEqual(1500, data["summary"]["procurement"]["undated_unallocated"][0]["total_minor"])
        self.assertIn("evt-unknown", data["summary"]["uncertainty"]["unknown_amount_event_ids"])
        self.assertNotIn("evt-zero", data["summary"]["uncertainty"]["unknown_amount_event_ids"])
        self.assertEqual("2026-03", date_month(parse_date("2026-03")))
        self.assertEqual("undated_unallocated", date_month(parse_date("2026-01-17 → 2026-04-18")))

    def test_group_reconstruction_exact_remainder_and_full_reconstruction(self):
        rows = [row(amount="100", ordered="2026-01-01 → 2026-04-30")]
        evidence = fixture(rows)
        evidence["details"]["pur-a"] = [{
            "purchase_id": "pur-detail", "description": "One project subscription",
            "amount_minor": 3000, "quantity": 1, "order_date": None,
            "receipt_date": day("2026-02-01"), "amount_evidence": "legacy_unverified",
            "order_ids": [], "source_ids": [],
        }]
        data = self.checked(rows, evidence)
        self.assertFalse(self.purchase(data, "pur-a")["contributes"])
        remainder = self.purchase(data, "pur-a:legacy-remainder")
        self.assertEqual(7000, remainder["amount_minor"])
        self.assertEqual("range", remainder["order_date"]["precision"])
        self.assertEqual(day("2026-02-01"), self.purchase(data, "pur-detail")["receipt_date"])
        self.assertEqual(10000, self.total(data, "procurement", "total_minor"))
        evidence["details"]["pur-a"][0]["amount_minor"] = 10000
        full = self.checked(rows, evidence)
        self.assertNotIn("pur-a:legacy-remainder", [item["purchase_id"] for item in full["purchases"]])
        self.assertEqual(10000, self.total(full, "procurement", "total_minor"))
        evidence["details"]["pur-a"][0]["amount_minor"] = 10001
        self.assertTrue(analyze(rows, evidence)["validation"]["errors"])

    def test_order_only_allocation_does_not_invent_item_allocation(self):
        rows = [row(amount="10"), row("pur-b", "20")]
        evidence = fixture(rows)
        add_order(evidence, "test:order", ["pur-a", "pur-b"])
        add_event(evidence, "evt-order", 1000, [(None, 1000)])
        evidence["allocations"][0]["order_id"] = "test:order"
        data = self.checked(rows, evidence)
        self.assertEqual(1000, self.total(data, "merchant_payments", "charges_minor"))
        self.assertEqual([], data["events"][0]["purchase_ids"])
        self.assertEqual(["test:order"], data["events"][0]["order_ids"])
        self.assertEqual(["evt-order"], data["summary"]["uncertainty"]["order_only_allocation_event_ids"])
        self.assertEqual("unknown", self.purchase(data, "pur-a")["payment_evidence"])

    def test_invoice_receipt_service_and_delivery_dates_are_preserved(self):
        rows = [row(ordered="2026-02-05")]
        evidence = fixture(rows)
        evidence["purchases"]["pur-a"].update({
            "row_date_basis": "invoice_date",
            "delivery_dates": [day("2026-02-07"), day("2026-02-08")],
            "service_period": {"precision": "month", "value": "2026-01"},
        })
        event = add_event(evidence, "evt-a", 1000, [("pur-a", 1000)], date="2026-02-06")
        event["invoice_date"] = day("2026-02-05")
        event["receipt_date"] = day("2026-02-06")
        event["service_period"] = {"precision": "month", "value": "2026-01"}
        data = self.checked(rows, evidence)
        self.assertIsNone(data["purchases"][0]["order_date"])
        self.assertEqual(day("2026-02-05"), data["purchases"][0]["invoice_date"])
        self.assertEqual("2026-01", data["events"][0]["service_period"]["value"])
        self.assertEqual(2, len(data["purchases"][0]["delivery_dates"]))

    def test_receipt_date_does_not_prove_payment_date(self):
        rows = [row()]
        evidence = fixture(rows)
        add_event(evidence, "evt-a", 1000, [("pur-a", 1000)])
        source = evidence["sources"]["src-evt-a"]
        source["proves"] = ["charge", "receipt_date"]
        source.pop("merchant_event_date")
        source["receipt_date"] = day("2026-02-01")
        errors = analyze(rows, evidence)["validation"]["errors"]
        self.assertTrue(any("event date lacks" in error for error in errors))
        evidence["events"][0]["event_date"] = None
        data = self.checked(rows, evidence)
        self.assertEqual(1000, data["summary"]["merchant_payments"]["undated_unallocated"][0]["charges_minor"])

    def test_returned_purchase_and_partial_charge_remain_reviewable(self):
        rows = [row(amount="30", status="RETURNED")]
        evidence = fixture(rows)
        add_event(evidence, "evt-a", 1000, [("pur-a", 1000)])
        data = self.checked(rows, evidence)
        self.assertEqual("merchant_charge_partial", data["purchases"][0]["payment_evidence"])
        self.assertEqual(["pur-a"], data["summary"]["fulfillment"]["returned_without_evidenced_refund_purchase_ids"])
        self.assertEqual(3000, data["summary"]["uncertainty"]["by_currency"][0]["partial_charge_purchase_minor"])

    def test_unresolved_project_share_not_promoted_to_project_cash(self):
        rows = [row()]
        evidence = fixture(rows)
        add_event(evidence, "evt-a", 1000, [("pur-a", 500)], allocation_status="unresolved")
        data = self.checked(rows, evidence)
        self.assertEqual(0, self.total(data, "merchant_payments", "charges_minor"))
        self.assertEqual(1000, self.total(data, "merchant_payments", "unresolved_project_share_minor"))
        self.assertEqual("unknown", data["purchases"][0]["payment_evidence"])

    def test_replacement_cycle_fails(self):
        rows = [row(), row("pur-b")]
        evidence = fixture(rows)
        evidence["purchases"]["pur-a"]["replacement_for"] = "pur-b"
        evidence["purchases"]["pur-b"]["replacement_for"] = "pur-a"
        self.assertTrue(any("relationship cycle" in error
                            for error in analyze(rows, evidence)["validation"]["errors"]))

    def test_no_payment_inferred_from_order_price_source(self):
        rows = [row()]
        evidence = fixture(rows)
        add_source(evidence, "order-confirmation", ["price", "order_date"])
        add_event(evidence, "evt-a", 1000, [("pur-a", 1000)], source_ids=["order-confirmation"])
        errors = analyze(rows, evidence)["validation"]["errors"]
        self.assertTrue(any("matching source capability" in error for error in errors))

    def test_mechanical_allocation_errors_fail_missing_evidence_warns(self):
        rows = [row()]
        evidence = fixture(rows)
        evidence["coverage"] = [{
            "coverage_id": "coverage-a", "vendor": "Test Vendor", "stream": "orders",
            "evidence_type": "charge", "checked_at": TODAY, "examined_period": None,
            "complete_period": None, "coverage": "unknown", "source_ids": [],
        }]
        data = self.checked(rows, evidence)
        self.assertTrue(data["validation"]["warnings"])
        add_event(evidence, "evt-a", 1000, [("pur-a", 999)])
        errors = analyze(rows, evidence)["validation"]["errors"]
        self.assertTrue(any("do not equal" in error for error in errors))

    def test_each_month_plus_undated_reconciles_to_every_total(self):
        rows = [row(), row("pur-b", "21", ordered="")]
        evidence = fixture(rows)
        add_event(evidence, "evt-a", 1000, [("pur-a", 1000)])
        add_event(evidence, "evt-b", 2100, [("pur-b", 2100)], date=None)
        add_event(evidence, "evt-refund", 150, [("pur-a", 150)], event_type="refund")
        data = self.checked(rows, evidence)
        for name in ("procurement", "merchant_payments"):
            summary = data["summary"][name]
            for total in summary["totals"]:
                for key, value in total.items():
                    if key.endswith("_minor"):
                        bucket_total = sum(bucket[key] for bucket in
                                           summary["monthly"] + summary["undated_unallocated"]
                                           if bucket["currency"] == total["currency"])
                        self.assertEqual(value, bucket_total)

    def test_exports_deterministic_and_csv_contains_all_contract_entities(self):
        rows = [row(), row("pur-b", "20")]
        evidence = fixture(rows)
        data = self.checked(rows, evidence)
        reordered = self.checked(list(reversed(rows)), evidence)
        self.assertEqual(export_json(data), export_json(reordered))
        self.assertEqual(export_csv(data), export_csv(reordered))
        parsed = list(csv.DictReader(io.StringIO(export_csv(data))))
        self.assertIn("metadata", {item["record_type"] for item in parsed})
        self.assertIn("procurement_monthly", {item["record_type"] for item in parsed})
        self.assertEqual({"pur-a", "pur-b"},
                         {item["purchase_id"] for item in parsed if item["record_type"] == "purchase"})

    def test_currency_scale_is_exact(self):
        rows = [row(amount="12")]
        evidence = fixture(rows)
        evidence["currency_scales"]["JPY"] = 0
        evidence["purchases"]["pur-a"]["currency"] = "JPY"
        data = self.checked(rows, evidence)
        self.assertEqual(12, data["purchases"][0]["amount_minor"])
        rows[0]["cost"] = Decimal("12.01")
        self.assertTrue(analyze(rows, evidence)["validation"]["errors"])


class ParserAndCommandTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hsm-ledger-synthetic-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "hardware" / "ledger"
        self.directory.mkdir(parents=True)
        self.ledger = self.directory / "purchases.md"
        self.orders = self.directory / "purchases.orders.json"
        self.evidence_path = self.directory / "purchases.evidence.json"
        self.ledger.write_text(
            "# Synthetic purchases\n\n## 1. Test components\n\n"
            "| Part | Qty | $ | Order # | Ordered | Delivered | Status |\n"
            "|---|---|---|---|---|---|---|\n"
            "| <!--purchase:pur-unit--> Unit parts | 3 | $0.10 ea. | — | 2026-01-31 | — | ON-ORDER |\n"
            "| <!--purchase:pur-bundle--> Bundle subtotal included | 3 | $0.30 | — | 2026-02-01 | — | ACQUIRED |\n"
            "| <!--purchase:pur-unknown--> Unknown canceled part | 1 | — | — | — | — | CANCELLED |\n"
            "| <!--purchase:pur-zero--> No charge replacement | 1 | $0.00 | — | — | — | ACQUIRED |\n\n"
            "## 18. Engineering services\n\n"
            "| Date range | Type | # of receipts | $ |\n|---|---|---|---|\n"
            "| <!--purchase:pur-group--> 2026-01-01 → 2026-03-31 | Legacy services | 2 | $5.00 |\n"
            "| **§18 subtotal** | | 2 | **$5.00** |\n\n"
            "## Totals\n\n"
            "| Status | $ |\n|---|---|\n"
            "| Procurement | [$5.60](LEDGER_GRAND_TOTAL) |\n\n"
            "## Sources\n[value](NAME) texts are updated by:\n"
            "- " + chr(96) + "/hardware/scripts/_ledger_totals.py" + chr(96) + "\n",
            encoding="utf-8")
        rows = parse(self.ledger)[-1]
        evidence = fixture(rows)
        evidence["purchases"]["pur-group"]["row_date_basis"] = "coverage_period"
        self.evidence_path.write_text(json.dumps(evidence))
        self.orders.write_text(json.dumps({
            "orders": {"test-private-omitted": {
                "project": False, "private_item": "SYNTHETIC_PERSONAL_ACCOUNT_DATA",
                "total": 99000,
            }},
        }))

    def command(self, *modes):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *modes, "--ledger", str(self.ledger),
             "--orders", str(self.orders), "--evidence", str(self.evidence_path)],
            text=True, capture_output=True, check=False)

    def snapshot(self):
        return {str(path): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.directory.iterdir() if path.is_file()}

    def test_unit_vs_bundle_unknown_zero_and_labor_subtotal(self):
        statuses, sections, labor, _, rows = parse(self.ledger)
        self.assertEqual(Decimal("0.30"), statuses["ON-ORDER"])
        self.assertEqual(Decimal("0.30"), statuses["ACQUIRED"])
        self.assertEqual(Decimal("5.00"), labor)
        self.assertEqual(5, len(rows))
        self.assertIsNone(next(r for r in rows if r["purchase_id"] == "pur-unknown")["cost"])
        self.assertEqual("$5.60", variables_from_totals(statuses, sections, labor)["LEDGER_GRAND_TOTAL"])

    def test_stable_ids_survive_description_changes_and_row_reordering(self):
        before = {r["purchase_id"] for r in parse(self.ledger)[-1]}
        content = self.ledger.read_text().splitlines()
        a, b = content.index(next(x for x in content if "purchase:pur-unit" in x)), content.index(next(x for x in content if "purchase:pur-bundle" in x))
        content[a], content[b] = content[b], content[a].replace("Unit parts", "Renamed project component")
        self.ledger.write_text("\n".join(content) + "\n")
        after = {r["purchase_id"] for r in parse(self.ledger)[-1]}
        self.assertEqual(before, after)

    def test_all_named_inspection_modes_are_nonmutating_even_when_stale(self):
        initial = self.snapshot()
        for mode in ("--report", "--audit", "--export-json", "--export-csv", "--check"):
            result = self.command(mode)
            self.assertEqual(1 if mode == "--check" else 0, result.returncode, result.stderr + result.stdout[:600])
            self.assertEqual(initial, self.snapshot(), mode)
            self.assertNotIn("SYNTHETIC_PERSONAL_ACCOUNT_DATA", result.stdout)
        self.assertIn("stale", self.command("--check").stdout)

    def test_regeneration_idempotent_and_check_detects_stale_exports(self):
        result = self.command("--write")
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        first = self.snapshot()
        result = self.command("--write")
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertEqual(first, self.snapshot())
        checked = self.command("--check")
        self.assertEqual(0, checked.returncode, checked.stderr + checked.stdout)
        before = self.snapshot()
        self.assertEqual(0, self.command("--export-json").returncode)
        self.assertEqual(before, self.snapshot())
        generated = self.directory / "purchases.export.csv"
        generated.write_text("stale synthetic export\n")
        before = self.snapshot()
        result = self.command("--check")
        self.assertEqual(1, result.returncode)
        self.assertIn("purchases.export.csv is missing or stale", result.stdout)
        self.assertEqual(before, self.snapshot())

    def test_bare_run_compatibility_and_fingerprint_ignores_generated_markers(self):
        before = input_fingerprint(self.ledger, json.loads(self.evidence_path.read_text()))
        self.ledger.write_text(self.ledger.read_text().replace("$5.60", "$0.00"))
        after = input_fingerprint(self.ledger, json.loads(self.evidence_path.read_text()))
        self.assertEqual(before, after)
        result = self.command()
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("[$5.60](LEDGER_GRAND_TOTAL)", self.ledger.read_text())
        self.assertEqual(0, self.command("--check").returncode)

    def test_known_legacy_invoice_mismatch_fails_without_exporting_account_data(self):
        rows = [row()]
        rows[0]["orders"] = ["112-1234567-1234567"]
        errors, _, _ = reconcile_orders(rows, {"112-1234567-1234567": {
            "total": Decimal("25"), "nonproject_amount": Decimal("5"),
            "private_item": "SYNTHETIC_PRIVATE_ITEM",
        }})
        self.assertEqual(1, len(errors))
        self.assertEqual(Decimal("20"), errors[0][2])

    def test_historical_cent_residual_warns_and_event_allocations_remain_exact(self):
        self.ledger.write_text(self.ledger.read_text().replace(
            "| $0.30 | — | 2026-02-01", "| $0.30 | 112-1234567-1234567 | 2026-02-01"))
        self.orders.write_text(json.dumps({
            "orders": {"112-1234567-1234567": {"total": 0.31, "project": True}},
        }))
        result = self.command("--write")
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        result = self.command("--check")
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("historical allocation residual USD +0.01", result.stdout)

    def test_invalid_calendar_precision_fails_cleanly(self):
        evidence = json.loads(self.evidence_path.read_text())
        evidence["as_of"] = "20261004"
        self.evidence_path.write_text(json.dumps(evidence))
        result = self.command("--report")
        self.assertEqual(1, result.returncode)
        self.assertIn("invalid precision-preserving date", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


def selftest():
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if not result.wasSuccessful():
        raise AssertionError("ledger synthetic contract tests failed")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
    else:
        unittest.main()
