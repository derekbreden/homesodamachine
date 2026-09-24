#!/usr/bin/env python3
"""Print an existing native archive through foreground Bambu Connect mouse input.

    tools/cad-venv/bin/python tools/bambu_print.py file.gcode.3mf Mark2
    tools/cad-venv/bin/python tools/bambu_print.py file.gcode.3mf Mark2 --dry-run

The Swift input process holds the app in front until this transaction ends. The
read-only printer connection supplies the acceptance result and retry evidence.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import queue
import select
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import bambu_printer

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache/printer-control"
PRINTERS = ("H2C", "Mark2")
BUSY = {"PREPARE", "RUNNING", "PAUSE"}
OPTIONS = {"Timelapse": "On", "Auto bed leveling": "On",
           "Flow dynamic calibration": "Auto", "Nozzle Offset Calibration": "Auto"}


class PrintError(RuntimeError):
    pass


def log(message):
    print(message, flush=True)


def archive_details(path):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip():
            raise PrintError("The archive fails its ZIP checksum")
        plates = ET.fromstring(archive.read("Metadata/slice_info.config")).findall("plate")
        if len(plates) != 1:
            raise PrintError("This sender takes a single sliced plate")
        plate = plates[0]
        settings = json.loads(archive.read("Metadata/project_settings.config"))
        if settings.get("printer_model") != "Bambu Lab H2C":
            raise PrintError("The plate must be sliced for the H2C printers")
        gcode = archive.read("Metadata/plate_1.gcode")
        checksum = archive.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        if hashlib.md5(gcode).hexdigest() != checksum:
            raise PrintError("The embedded G-code checksum does not match")
        slots = {}
        for filament in plate.findall("filament"):
            index = int(filament.attrib["id"]) - 1
            nozzle = int(settings["filament_map"][index])
            if nozzle not in (1, 2) or nozzle in slots:
                raise PrintError("Each active nozzle must use one external spool")
            slots[nozzle] = {"type": filament.attrib["type"],
                             "colour": filament.attrib["color"].lstrip("#").upper()[:6]}
        if not slots:
            raise PrintError("The archive has no active filament")
        return {"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "gcode_sha256": hashlib.sha256(gcode).hexdigest(), "slots": slots,
                "objects": [x.attrib["name"] for x in plate.findall("object")
                            if x.attrib.get("skipped") != "true"]}


def verify_spools(details, reading):
    trays = {str(tray["id"]): tray for tray in reading.get("vir_slot", [])}
    for nozzle, expected in details["slots"].items():
        slot = str(253 + nozzle)
        tray = trays.get(slot, {})
        actual = {"type": tray.get("tray_type"),
                  "colour": tray.get("tray_color", "").upper()[:6]}
        if actual != expected:
            raise PrintError(f"External spool {slot} reports {actual}; the slice requires {expected}")


def job_id(reading):
    value = reading.get("job_id")
    return str(value) if value is not None else ""


def accepted(before, reading, name):
    return (bool(job_id(reading)) and job_id(reading) != job_id(before)
            and reading.get("subtask_name") == name
            and reading.get("gcode_state") in {"PREPARE", "RUNNING"}
            and not reading.get("print_error"))


def may_retry(before, reading, observed_activity, page):
    return (not observed_activity and bool(job_id(before)) and job_id(reading) == job_id(before)
            and reading.get("gcode_state") in {"IDLE", "FINISH", "FAILED"}
            and (reading.get("upload") or {}).get("status") in (None, "idle")
            and (reading.get("print_error") or 0) == (before.get("print_error") or 0)
            and (reading.get("hms") or []) == (before.get("hms") or [])
            and not reading.get("nozzle_target_temper") and not reading.get("bed_target_temper")
            and not any(word in page.lower() for word in ("sending", "uploading", "downloading")))


class PrinterWatch:
    def __init__(self, printer):
        self.connection = bambu_printer.Connection(printer, 12)
        self.reading = {}
        self.events = []
        self.activity = False
        self.reply = None
        self.last_event = {}

    def __enter__(self):
        self.connection.__enter__()
        self.reading = self.connection.status()
        self.initial = json.loads(json.dumps(self.reading))
        return self

    def __exit__(self, *args):
        self.connection.__exit__(*args)

    def receive(self, message):
        if isinstance(message, Exception):
            raise message
        if not isinstance(message, dict) or not isinstance(message.get("print"), dict):
            return
        update = message["print"]
        bambu_printer.merge_status(self.reading, update)
        if update.get("command") == "project_file":
            self.reply = {key: update.get(key) for key in ("command", "result", "reason", "err_code")}
            self.events.append(self.reply)
            self.activity = True
            log("Printer reply: " + json.dumps(self.reply))
        if (job_id(self.reading) != job_id(self.initial)
                or self.reading.get("gcode_state") in BUSY
                or (self.reading.get("upload") or {}).get("status") not in (None, "idle")):
            self.activity = True
        event = {key: self.reading.get(key) for key in
                 ("job_id", "subtask_name", "gcode_state", "print_error", "hms", "layer_num")}
        if event != self.last_event:
            self.events.append(event)
            self.last_event = event

    def drain(self, seconds=0):
        deadline = time.monotonic() + seconds
        while True:
            try:
                message = self.connection.messages.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty:
                break
            self.receive(message)
        return self.reading

    def fresh(self):
        self.connection.send("pushing", "pushall", version=1, push_target=1)
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            try:
                message = self.connection.messages.get(timeout=deadline - time.monotonic())
            except queue.Empty:
                break
            self.receive(message)
            if isinstance(message, dict) and "gcode_state" in message.get("print", {}):
                return self.reading
        raise PrintError("No fresh printer status; no further send will be attempted")


class UI:
    def __enter__(self):
        source = ROOT / "tools/bambu-ui/main.swift"
        binary = CACHE / "bambu-ui"
        if not binary.exists() or binary.stat().st_mtime < source.stat().st_mtime:
            subprocess.run(["swiftc", "-O", str(source), "-o", str(binary)], check=True)
        self.process = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        text=True, bufsize=1)
        try:
            self.call("focus")
        except BaseException:
            self.__exit__()
            raise
        return self

    def __exit__(self, *_args):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=5)
        self.process.stdout.close()

    def call(self, command, **args):
        self.process.stdin.write(json.dumps({"command": command, **args}) + "\n")
        self.process.stdin.flush()
        if not select.select([self.process.stdout], [], [], 60)[0]:
            raise PrintError("The UI input process did not respond")
        line = self.process.stdout.readline()
        if not line:
            raise PrintError("The UI input process stopped")
        result = json.loads(line)
        if not result.get("ok"):
            raise PrintError(f"{command} {args.get('label', '')}: " + result.get("error", "Unknown UI error"))
        return result

    def nodes(self):
        return self.call("snapshot")["nodes"]

    def click(self, label, role="AXButton", **args):
        deadline = time.monotonic() + 3
        while True:
            try:
                return self.call("click", label=label, role=role, **args)
            except PrintError as error:
                if "Control is covered" not in str(error) or time.monotonic() >= deadline:
                    raise
                time.sleep(.3)

    def wait(self, predicate, seconds=15):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            nodes = self.nodes()
            if predicate(nodes):
                return nodes
            time.sleep(.2)
        raise PrintError("The expected Bambu Connect control did not appear; page: " + page_text(nodes))

    def settled_dialog(self):
        deadline = time.monotonic() + 15
        previous, stable_since = None, time.monotonic()
        while time.monotonic() < deadline:
            nodes = self.nodes()
            fingerprint = [(n["role"], n["label"], n["rect"], n["enabled"]) for n in nodes]
            if fingerprint != previous:
                previous, stable_since = fingerprint, time.monotonic()
            elif (has_dialog(nodes) and len(selected_options(nodes)) == len(OPTIONS)
                  and matching(nodes, "confirm", "AXButton") and time.monotonic() - stable_since >= .8):
                return nodes
            time.sleep(.2)
        raise PrintError("The print dialog kept changing while loading the printer")


def matching(nodes, label, role=None):
    return [node for node in nodes if node["label"] == label and (role is None or node["role"] == role)]


def page_text(nodes):
    return " | ".join(node["label"] for node in nodes if node["role"] == "AXStaticText")


def has_dialog(nodes):
    return bool(matching(nodes, "Send to print", "AXGroup"))


def close_dialog(ui):
    nodes = ui.nodes()
    if any(node["role"] == "AXSheet" for node in nodes) and matching(nodes, "Close", "AXButton"):
        ui.click("Close")
        nodes = ui.wait(lambda ns: not matching(ns, "Close", "AXButton"))
    if has_dialog(nodes):
        try:
            ui.click("cancel")
        except PrintError:
            if has_dialog(ui.nodes()):
                raise
        ui.wait(lambda ns: not has_dialog(ns))
    elif any(node["role"] == "AXSheet" for node in nodes) and matching(nodes, "Cancel", "AXButton"):
        ui.click("Cancel")


def selected_options(nodes):
    result = {}
    current = None
    for node in nodes:
        if node["label"] in OPTIONS and node["role"] == "AXStaticText":
            current = node["label"]
        if current and node["role"] == "AXRadioButton":
            if any(child["parent"] in (node["id"], node["parent"]) and child["role"] == "AXImage"
                   and child["label"] == "radio" for child in nodes):
                result[current] = node["label"]
    return result


def set_options(ui):
    nodes = ui.wait(lambda ns: len(selected_options(ns)) == len(OPTIONS))
    for label, wanted in OPTIONS.items():
        if selected_options(nodes).get(label) == wanted:
            continue
        # The option row follows its static label in the accessibility tree.
        start = matching(nodes, label, "AXStaticText")[0]["id"]
        later_labels = [node["id"] for node in nodes if node["id"] > start
                        and node["label"] in OPTIONS and node["role"] == "AXStaticText"]
        end = min(later_labels, default=len(nodes))
        candidate = next(node for node in nodes if start < node["id"] < end
                         and node["label"] == wanted and node["role"] == "AXRadioButton")
        occurrence = matching(nodes, wanted, "AXRadioButton").index(candidate)
        ui.click(wanted, "AXRadioButton", nth=occurrence)
        nodes = ui.wait(lambda ns: selected_options(ns).get(label) == wanted)
    if selected_options(nodes) != OPTIONS:
        raise PrintError("Print options do not match the standing settings")


def verify_dialog(nodes, printer, details):
    if not has_dialog(nodes) or len(matching(nodes, printer + " chevron_down")) != 1:
        raise PrintError("The send dialog does not identify the requested printer")
    tiles = [n for n in nodes if n["role"] == "AXGroup" and n["label"].startswith("Ext ")]
    if len(tiles) != len(details["slots"]) or matching(nodes, "? ?", "AXGroup"):
        raise PrintError("An external spool mapping is missing")
    right_labels = [n for n in nodes if n["role"] == "AXStaticText" and n["label"].startswith("Right Nozzle")]
    if len(right_labels) != 1:
        raise PrintError("The nozzle columns could not be identified")
    divider = right_labels[0]["rect"][0]
    for tile in tiles:
        nozzle = 2 if tile["rect"][0] >= divider else 1
        filament = details["slots"].get(nozzle)
        if not filament:
            raise PrintError("The external spool is mapped to the wrong nozzle")
        label = "Ext " + filament["type"]
        if tile["label"] not in (label, label + (" L" if nozzle == 1 else " R")):
            raise PrintError(f"The selected tile reads {tile['label']}, expected {filament['type']}")
    if selected_options(nodes) != OPTIONS:
        raise PrintError("The print options changed")


def prepare_dialog(ui, path, printer, details):
    close_dialog(ui)
    ui.click("Devices", "AXLink")
    def device_links(ns):
        return [node for node in ns if node["role"] == "AXLink"
                and (node["label"] == printer or node["label"].startswith(printer + " "))]
    nodes = ui.wait(lambda ns: len(device_links(ns)) == 1)
    ui.click(device_links(nodes)[0]["label"], "AXLink")
    ui.wait(lambda ns: matching(ns, "Printing Progress", "AXStaticText"))
    ui.click("Print", "AXLink")
    ui.wait(lambda ns: matching(ns, "Import Gcode 3MF", "AXButton"))
    ui.click("Import Gcode 3MF")
    ui.wait(lambda ns: any(node["role"] == "AXSheet" for node in ns))
    ui.call("open_path", path=str(path))
    ui.wait(lambda ns: matching(ns, "Open", "AXButton"))
    ui.click("Open")
    ui.wait(lambda ns: not any(n["role"] == "AXSheet" for n in ns)
            and path.name in page_text(ns) and "Compatible Printer" in page_text(ns), seconds=30)
    log(f"Imported {path.name}: {', '.join(details['objects'])}")
    ui.click("Print")
    nodes = ui.settled_dialog()
    selectors = [node for node in nodes if node["label"] in [name + " chevron_down" for name in PRINTERS]]
    if len(selectors) != 1:
        raise PrintError("The send dialog has no unique printer selector")
    selector = selectors[0]
    if selector["label"] != printer + " chevron_down":
        ui.call("click_offsets", label=selector["label"], role=selector["role"],
                offsets=[[70, 32], [81, 91 + 36 * PRINTERS.index(printer)]])
        nodes = ui.wait(lambda ns: matching(ns, printer + " chevron_down"))
        nodes = ui.settled_dialog()
    # Mark2 maps its external spools automatically. H2C's left AMS can leave
    # the external tile unresolved; the saved machine has one AMS above it.
    if matching(nodes, "? ?", "AXGroup"):
        if printer != "H2C" or set(details["slots"]) != {1}:
            raise PrintError("The external spool mapping is unresolved")
        ui.call("click_offsets", label="? ?", role="AXGroup",
                offsets=[[47, 30], [-245, 282]])
    nodes = ui.wait(lambda ns: not matching(ns, "? ?", "AXGroup")
                    and len([n for n in ns if n["role"] == "AXGroup"
                             and n["label"].startswith("Ext ")]) == len(details["slots"]))
    set_options(ui)
    verify_dialog(ui.nodes(), printer, details)
    log(f"Dialog: {printer}; external spools mapped; " + ", ".join(f"{k} {v}" for k, v in OPTIONS.items()))
    return ui.wait(lambda ns: matching(ns, "confirm", "AXButton"))


def observe_send(ui, watch, before, details, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        reading = watch.drain(1)
        if watch.reply and str(watch.reply.get("result", "")).lower() not in {"success", "ok"}:
            raise PrintError("Printer refused the job: " + json.dumps(watch.reply))
        if accepted(before, reading, details["name"]):
            # Keep reading through the first transition into machine startup.
            watch.drain(3)
            reading = watch.fresh()
            if accepted(before, reading, details["name"]):
                return dict(reading)
        if (reading.get("print_error") or 0) != (before.get("print_error") or 0):
            raise PrintError(f"Printer error {reading.get('print_error')}; no repeat send")
    reading = watch.fresh()
    text = page_text(ui.nodes())
    if may_retry(before, reading, watch.activity, text):
        return None
    raise PrintError("The send has an uncertain or rejected result; no repeat send. "
                     f"Printer: {reading.get('gcode_state')}, job {job_id(reading)}; page: {text}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("printer", choices=PRINTERS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--attempts", type=int, choices=(1, 2, 3), default=3)
    parser.add_argument("--accept-timeout", type=float, default=90)
    args = parser.parse_args()
    path = args.archive.expanduser().resolve()
    if not path.is_file() or not path.name.endswith(".gcode.3mf"):
        raise PrintError("Supply an existing .gcode.3mf archive")
    details = archive_details(path)
    CACHE.mkdir(parents=True, exist_ok=True)
    with (CACHE / "bambu-print.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise PrintError("Another foreground print transaction is active") from None
        # Bambu Connect can rewrite its imported file. Its copy has the same
        # name and initial bytes; the reviewed archive stays at its source path.
        imported = CACHE / "imports" / details["sha256"] / path.name
        imported.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, imported)
        printer = bambu_printer.configured_printers()[args.printer]
        with PrinterWatch(printer) as watch:
            before = watch.initial
            if before.get("gcode_state") in BUSY and not args.dry_run:
                raise PrintError(f"{args.printer} is {before['gcode_state']} on {before.get('subtask_name')}")
            verify_spools(details, before)
            log(f"{args.printer}: {before.get('gcode_state')}, job {job_id(before)}")
            with UI() as ui:
                try:
                    for attempt in range(args.attempts):
                        shutil.copyfile(path, imported)
                        nodes = prepare_dialog(ui, imported, args.printer, details)
                        button = matching(nodes, "confirm", "AXButton")[0]
                        if args.dry_run:
                            log(f"Dry run: Send is {'enabled' if button['enabled'] else 'disabled'}; cancelling without sending")
                            return
                        if not button["enabled"]:
                            raise PrintError("Send is disabled; nothing was sent")
                        current = watch.fresh()
                        if accepted(before, current, details["name"]):
                            result = dict(current)
                            break
                        if not may_retry(before, current, watch.activity, ""):
                            raise PrintError("The printer changed or is heating; nothing more was sent")
                        verify_spools(details, current)
                        if hashlib.sha256(path.read_bytes()).hexdigest() != details["sha256"]:
                            raise PrintError("The archive changed after import")
                        verify_dialog(ui.nodes(), args.printer, details)
                        log(f"Sending attempt {attempt + 1}: one foreground mouse click")
                        try:
                            ui.click("confirm")
                        except PrintError as error:
                            log(f"Send input returned {error}; checking the printer before any further action")
                        result = observe_send(ui, watch, before, details, args.accept_timeout)
                        if result is not None:
                            break
                        log("No printer activity and no transfer in the app; opening a fresh dialog")
                    else:
                        raise PrintError("The printer received no job after the bounded send attempts")
                finally:
                    try:
                        close_dialog(ui)
                    except PrintError as error:
                        log(f"Dialog cleanup: {error}")
            receipt = {"printer": args.printer, "observed_at": datetime.now(timezone.utc).isoformat(),
                       "archive": details, "printer_task_id": job_id(result),
                       **{k: result.get(k) for k in ("gcode_state", "subtask_name", "print_error", "hms",
                                                    "layer_num", "total_layer_num", "mc_remaining_time")}}
            receipt_path = CACHE / f"{args.printer}-{job_id(result)}-launch.json"
            receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
            log(json.dumps(receipt, indent=2))
            log(f"Launch record: {receipt_path}")


if __name__ == "__main__":
    try:
        main()
    except (PrintError, TimeoutError, OSError, subprocess.SubprocessError) as error:
        sys.exit(f"bambu_print: {error}")
