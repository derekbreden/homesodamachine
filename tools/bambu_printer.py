#!/usr/bin/env python3
"""Read Bambu printer status and control chamber lights over the existing LAN connection."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import shlex
import ssl
import time


@dataclass
class Printer:
    name: str
    serial: str
    host: str = field(repr=False)
    access_code: str = field(repr=False)


def configured_printers():
    config = Path.home() / "Library/Application Support/BambuStudio/BambuStudio.conf"
    codes = json.loads(config.read_text())["access_code"]
    runner = Path.home() / ".config/h2c-gc/run.sh"
    printers = {}
    for line in runner.read_text().splitlines():
        if not line.lstrip().startswith(("gc ", "gc\t")):
            continue
        words = shlex.split(line, comments=True)
        if not words or words[0] != "gc":
            continue
        if len(words) != 4:
            raise ValueError("Expected gc <name> <host> <access code> in the printer runner")
        _, name, host, code = words
        serials = [serial for serial, saved in codes.items() if saved == code]
        if len(serials) != 1:
            raise ValueError(f"{name}: expected one matching printer in Bambu Studio")
        if name in printers:
            raise ValueError(f"Duplicate printer name: {name}")
        printers[name] = Printer(name, serials[0], host, code)
    if not printers:
        raise ValueError("No printers configured in the timelapse runner")
    return printers


def merge_status(destination, update):
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(destination.get(key), dict):
            merge_status(destination[key], value)
        else:
            destination[key] = value


class Connection:
    def __init__(self, printer, timeout):
        import paho.mqtt.client as mqtt

        self.printer = printer
        self.timeout = timeout
        self.messages = queue.Queue()
        self.state = {}
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"hsm-{time.time_ns()}",
        )
        self.client.username_pw_set("bblp", printer.access_code)
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)
        self.client.connect_timeout = timeout

        def on_connect(client, userdata, flags, reason, properties):
            if reason.is_failure:
                self.messages.put(RuntimeError(f"{printer.name}: MQTT authentication failed"))
            else:
                client.subscribe(f"device/{printer.serial}/report", qos=1)

        def on_subscribe(client, userdata, message_id, reasons, properties):
            if any(reason.is_failure for reason in reasons):
                self.messages.put(RuntimeError(f"{printer.name}: MQTT subscription failed"))
            else:
                self.messages.put("ready")

        def on_message(client, userdata, message):
            try:
                self.messages.put(json.loads(message.payload))
            except (ValueError, UnicodeDecodeError):
                pass

        self.client.on_connect = on_connect
        self.client.on_subscribe = on_subscribe
        self.client.on_message = on_message

    def __enter__(self):
        try:
            self.client.connect(self.printer.host, 8883, keepalive=30)
            self.client.loop_start()
            self.wait(lambda message: message == "ready")
            return self
        except Exception:
            self.close()
            raise

    def close(self):
        self.client.disconnect()
        self.client.loop_stop()

    def __exit__(self, *exception):
        self.close()

    def wait(self, predicate):
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            try:
                message = self.messages.get(timeout=max(0.001, deadline - time.monotonic()))
            except queue.Empty:
                break
            if isinstance(message, Exception):
                raise message
            if isinstance(message, dict):
                merge_status(self.state, message)
            if predicate(message):
                return message
        raise TimeoutError(f"{self.printer.name}: no matching printer response within {self.timeout:g}s")

    def send(self, section, command, **values):
        sequence = str(time.time_ns() % 1_000_000_000)
        message = {section: {"sequence_id": sequence, "command": command, **values}}
        result = self.client.publish(
            f"device/{self.printer.serial}/request", json.dumps(message), qos=1
        )
        result.wait_for_publish(timeout=self.timeout)
        if not result.is_published():
            raise TimeoutError(f"{self.printer.name}: request was not published")
        return sequence

    def status(self):
        self.send("pushing", "pushall", version=1, push_target=1)
        self.wait(lambda message: isinstance(message, dict)
                  and {"gcode_state", "lights_report"} <= self.state.get("print", {}).keys())
        return self.state["print"]

    def light(self, node, mode):
        self.status()
        sequence = self.send("system", "ledctrl", led_node=node, led_mode=mode,
                             led_on_time=500, led_off_time=500, loop_times=0, interval_time=0)
        response = self.wait(lambda message: isinstance(message, dict)
                             and message.get("system", {}).get("sequence_id") == sequence)["system"]
        if response.get("result") != "success":
            raise RuntimeError(f"{self.printer.name}: light command rejected: {response.get('reason')}")
        self.send("pushing", "pushall", version=1, push_target=1)
        self.wait(lambda message: isinstance(message, dict) and any(
            item.get("node") == node and item.get("mode") == mode
            for item in message.get("print", {}).get("lights_report", [])
        ))
        return {"printer": self.printer.name, "node": node, "mode": mode, "verified": True}


def status_summary(printer, timeout):
    with Connection(printer, timeout) as connection:
        status = connection.status()
    fields = ("gcode_state", "subtask_name", "mc_percent", "layer_num", "total_layer_num",
              "mc_remaining_time", "print_error", "hms", "nozzle_temper", "nozzle_target_temper",
              "bed_temper", "bed_target_temper", "lights_report")
    # vir_slot 254 is the left external spool and 255 the right; the device page shows
    # only the right one. The nozzle list is every nozzle the machine knows, racked or
    # mounted; the top-level nozzle_type names one of them, not necessarily the printing head.
    spools = {tray["id"]: {"type": tray.get("tray_type"), "colour": tray.get("tray_color")}
              for tray in status.get("vir_slot", [])}
    nozzles = [{key: nozzle.get(key) for key in ("id", "type", "diameter", "sn")}
               for nozzle in status.get("device", {}).get("nozzle", {}).get("info", [])]
    return {"printer": printer.name, "observed_at": datetime.now(timezone.utc).isoformat(),
            **{key: status[key] for key in fields if key in status},
            "external_spools": spools, "nozzle_type": status.get("nozzle_type"), "nozzles": nozzles}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=12)
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="Read current status; defaults to both printers")
    status.add_argument("printer", nargs="?", default="all")
    light = commands.add_parser("light", help="Set one chamber light and verify its reported state")
    light.add_argument("printer")
    light.add_argument("mode", choices=("on", "off"))
    light.add_argument("--node", choices=("chamber_light", "chamber_light2"), default="chamber_light")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    printers = configured_printers()
    if args.printer != "all" and args.printer not in printers:
        parser.error("Unknown printer; configured names: " + ", ".join(printers))
    if args.command == "status":
        selected = list(printers.values()) if args.printer == "all" else [printers[args.printer]]
        with ThreadPoolExecutor(max_workers=len(selected)) as pool:
            results = list(pool.map(lambda printer: status_summary(printer, args.timeout), selected))
        print(json.dumps(results, indent=2))
    else:
        if args.printer == "all":
            parser.error("light requires one printer name")
        with Connection(printers[args.printer], args.timeout) as connection:
            print(json.dumps(connection.light(args.node, args.mode), indent=2))


if __name__ == "__main__":
    main()
