#!/usr/bin/env python3
"""Submit a sliced .gcode.3mf to H2C or Mark2 through Bambu Connect and verify the printer took it.

The steps are the ones a hand performs in the application, each one read back before
the next: the target's device page (which is what the send dialog offers as its
printer), the import, the dialog, the filament mapping, the print options, Send, and
the printer's own report over MQTT. `tools/bambu-ax` presses the controls in place;
the one popover the accessibility tree cannot show is clicked by position and judged
by the tile it fills in.
"""

import argparse
import json
import queue
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bambu_printer  # noqa: E402

AX = Path(__file__).resolve().parent / "bambu-ax" / "bambu-ax"
PRINTERS = ("H2C", "Mark2")
STANDING_OPTIONS = {
    "Timelapse": "On",
    "Auto bed leveling": "On",
    "Flow dynamic calibration": "Auto",
    "Nozzle Offset Calibration": "Auto",
}
# The filament tile's centre, and the External spool tile in the popover that opens
# under it, both from the tile's own origin. H2C's popover: one AMS unit's trays
# above the External spool.
TILE_CENTRE = (47, 30)
EXTERNAL_SPOOL = (-245, 282)
# The dialog's printer selector, from its own origin: its name text, then the first row of
# the popover that opens under it and the pitch to the rows below, one per printer in
# PRINTERS order. Both clicks share one front borrow: the popover does not survive a
# separate activation, so an AXPress that opens it is undone by the click that follows.
SELECTOR_TEXT = (70, 32)
#: The dialog is in the tree before it takes a click; a click at once misses the popover.
DIALOG_SETTLE = 2.0
#: A send the printer never receives, or one a filament load swallows, is made again, each one
#: a whole pass through the application from a fresh dialog.
SEND_ROUNDS = 3
#: Seconds between a send that did not arrive and the next round.
RESEND_PAUSE = 30
#: A click borrows the front for a second or two. A keystroke in another app can
#: dismiss either popover; each miss starts again from a closed, fresh dialog.
POPOVER_TRIES = 3
PRINTER_ROW = (81, 91)
PRINTER_ROW_PITCH = 36
BUSY = ("PREPARE", "RUNNING", "PAUSE")

NODE = re.compile(
    r'^#(?P<idx>\d+) (?P<indent> *)(?P<role>\S+)(?: "(?P<label>.*?)")?'
    r"(?: \[(?P<acts>[^\]]*)\])?(?: @(?P<x>-?\d+),(?P<y>-?\d+) (?P<w>\d+)x(?P<h>\d+))?"
    r"(?P<disabled> \(disabled\))?$"
)


def fail(message):
    sys.exit(f"bambu_send: {message}")


def ax(*args, check=True):
    result = subprocess.run([str(AX), *args], capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    if check and result.returncode != 0:
        fail(f"bambu-ax {' '.join(args)} failed:\n{output}")
    return output


def tree():
    nodes = []
    for line in ax("tree").splitlines():
        match = NODE.match(line)
        if not match:
            continue
        node = match.groupdict()
        node["idx"] = int(node["idx"])
        node["depth"] = len(node["indent"]) // 2
        node["acts"] = (node["acts"] or "").split(",") if node["acts"] else []
        node["enabled"] = node.pop("disabled") is None
        for key in ("x", "y", "w", "h"):
            node[key] = int(node[key]) if node[key] is not None else None
        nodes.append(node)
    return nodes


def find(nodes, role=None, label=None, starts=None, ends=None):
    return [
        n for n in nodes
        if (role is None or n["role"] == role)
        and (label is None or n["label"] == label)
        and (starts is None or (n["label"] or "").startswith(starts))
        and (ends is None or (n["label"] or "").endswith(ends))
    ]


def wait_for(seconds, predicate):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        nodes = tree()
        found = predicate(nodes)
        if found:
            return found
        time.sleep(0.5)
    return None


def dialog(nodes):
    return find(nodes, role="AXGroup", label="Send to print")


def selector(nodes):
    groups = find(nodes, role="AXGroup", ends=" chevron_down")
    names = [g["label"].rsplit(" ", 1)[0] for g in groups if g["label"].rsplit(" ", 1)[0] in PRINTERS]
    return names[0] if names else None


def tile(nodes):
    for n in find(nodes, role="AXGroup"):
        if n["label"] == "? ?" or (n["label"] or "").startswith("Ext "):
            return n
    return None


def options(nodes):
    """Each option row is a label and a run of radio buttons; the chosen one carries an
    AXImage "radio" as its first child. Two options share a row, so a button belongs
    to the nearest label on its left."""
    by_idx = {n["idx"]: n for n in nodes}
    labels = {}
    for name in STANDING_OPTIONS:
        found = find(nodes, role="AXStaticText", label=name)
        if found and found[0]["x"] is not None:
            labels[name] = found[0]
    owned = {name: [] for name in labels}
    for b in find(nodes, role="AXRadioButton"):
        if b["x"] is None:
            continue
        left = [(row["x"], name) for name, row in labels.items()
                if abs(b["y"] - row["y"]) <= 12 and row["x"] < b["x"]]
        if left:
            owned[max(left)[1]].append(b)
    chosen = {}
    for name, buttons in owned.items():
        buttons.sort(key=lambda n: n["x"])
        picked = None
        for b in buttons:
            child = by_idx.get(b["idx"] + 1)
            if child and child["role"] == "AXImage" and child["label"] == "radio":
                picked = b
        chosen[name] = (picked["label"] if picked else None, buttons)
    return chosen


def status(printer, timeout=12):
    with bambu_printer.Connection(printer, timeout) as connection:
        return connection.status()


def manual_heat(reading):
    """What the printer is doing with its heaters when it has no job: a filament load or a
    purge holds a nozzle target, and a print sent during one starts nothing and says nothing."""
    if reading.get("gcode_state") in BUSY:
        return None
    nozzle = float(reading.get("nozzle_target_temper") or 0)
    bed = float(reading.get("bed_target_temper") or 0)
    if nozzle > 0 or bed > 0:
        return f"nozzle target {nozzle:g} C, bed target {bed:g} C with no job: a filament load or purge in progress"
    return None


def wait_out_heat(printer, name, seconds):
    """Wait for the manual heat to end, reading the printer every 10 s."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        time.sleep(10)
        reading = status(printer)
        heat = manual_heat(reading)
        if not heat:
            print(f"{name}: heaters idle; sending")
            return reading
        print(f"{name}: waiting; {heat}")
    fail(f"{name} kept a manual heat for {seconds:g}s; nothing was sent")


class Refused(Exception):
    """The application took the job and the printer did not start it."""

    def __init__(self, message, reading, heard=()):
        super().__init__(message)
        self.reading = reading
        self.heard = list(heard)


class Listener:
    """The printer's own report topic, held open across Send. A print command that reaches
    the printer is answered on it (`project_file` with a result and a reason), and an
    upload, an error or an HMS shows there too; a send that never reached the printer
    leaves it silent. Only those lines are kept, not the once-a-second status."""

    def __init__(self, printer):
        self.connection = bambu_printer.Connection(printer, 15)
        self.heard = []
        self.last = {}

    def __enter__(self):
        self.connection.__enter__()
        return self

    def __exit__(self, *exception):
        self.drain()
        self.connection.__exit__(*exception)

    def drain(self):
        while True:
            try:
                message = self.connection.messages.get_nowait()
            except queue.Empty:
                return self.heard
            if not isinstance(message, dict):
                continue
            for section, body in message.items():
                if not isinstance(body, dict):
                    continue
                command = body.get("command")
                if command and command != "push_status":
                    self.heard.append({"section": section, **{k: v for k, v in body.items()
                                       if k in ("command", "result", "reason", "subtask_name", "url",
                                                "param", "err_code", "sequence_id", "file")}})
                    continue
                # The status repeats every second; each of these is kept when it changes.
                upload = body.get("upload")
                if isinstance(upload, dict):
                    upload = {k: upload.get(k) for k in ("status", "progress", "message", "task_id")}
                seen = {"upload": upload if upload and upload.get("status") not in (None, "idle") else None,
                        "print_error": body.get("print_error") or None,
                        "hms": body.get("hms") or None,
                        "gcode_state": (body.get("gcode_state"), body.get("subtask_name"))
                        if "gcode_state" in body else None}
                for key, value in seen.items():
                    if value is not None and self.last.get(key) != value:
                        self.last[key] = value
                        self.heard.append({"section": section, key: value})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("archive", help="a sliced .gcode.3mf")
    parser.add_argument("printer", choices=PRINTERS)
    parser.add_argument("--dry-run", action="store_true", help="stop at the Send button and cancel the dialog")
    parser.add_argument("--timelapse", choices=("On", "Off"), default=STANDING_OPTIONS["Timelapse"])
    parser.add_argument("--accept-timeout", type=float, default=120, help="seconds to wait for PREPARE or RUNNING")
    parser.add_argument("--busy-wait", type=float, default=900, help="seconds to wait out a filament load before sending")
    args = parser.parse_args()

    archive = Path(args.archive).expanduser().resolve()
    if not archive.is_file() or not archive.name.endswith(".gcode.3mf"):
        fail(f"{archive} is not a sliced .gcode.3mf")
    wanted = dict(STANDING_OPTIONS, Timelapse=args.timelapse)
    printer = bambu_printer.configured_printers()[args.printer]

    before = status(printer)
    if before.get("gcode_state") in BUSY:
        note = f"{args.printer} is {before['gcode_state']} on {before.get('subtask_name')}; Send is disabled while it runs"
        if not args.dry_run:
            fail(note)
        print(note + " (dry run continues to the dialog)")
    spools = {t["id"]: t["tray_type"] for t in before.get("vir_slot", [])}
    print(f"{args.printer}: {before.get('gcode_state')} after {before.get('subtask_name')} "
          f"(job {before.get('job_id')}); external spools {spools}")
    heat = manual_heat(before)
    if heat and not args.dry_run:
        print(f"{args.printer}: {heat}")
        before = wait_out_heat(printer, args.printer, args.busy_wait)

    def send_once(before):
        # 1. The send dialog offers the device page last viewed as its printer.
        ax("press", "Devices", "--role", "AXLink")
        time.sleep(1.5)
        ax("press", args.printer, "--role", "AXLink")
        if not wait_for(8, lambda n: find(n, role="AXStaticText", label="Printing Progress")
                        and find(n, role="AXStaticText", label=args.printer)):
            fail(f"could not open {args.printer}'s device page")
        print(f"device page: {args.printer}")

        # 2. Import, and read the file summary back.
        output = ax("import", str(archive))
        if "-> loaded" not in output:
            fail(f"import did not load {archive.name}:\n{output}")
        summary = ax("state")
        if archive.name not in summary or "Compatible Printer" not in summary:
            fail(f"the Print tab does not show {archive.name}:\n{summary}")
        print("import: " + summary.split("Import Gcode 3MF | ", 1)[-1][:160])

        # 3. The dialog.
        ax("press", "Print", "--role", "AXButton")
        nodes = wait_for(10, lambda n: dialog(n) and selector(n) and n)
        if not nodes:
            fail("the Send to print dialog did not open")
        name = selector(nodes)
        if name != args.printer:
            # The printer popover is out of the tree, like the filament one: clicked by position
            # from the selector's own origin, and judged by what the selector reads afterwards.
            row = PRINTERS.index(args.printer)
            tries = []
            for attempt in range(POPOVER_TRIES):
                time.sleep(DIALOG_SETTLE)
                sel = [g for g in find(nodes, role="AXGroup", ends=" chevron_down")
                       if g["label"].rsplit(" ", 1)[0] in PRINTERS][0]
                x, y = sel["x"], sel["y"]
                clicked = ax("click", str(x + SELECTOR_TEXT[0]), str(y + SELECTOR_TEXT[1]),
                             str(x + PRINTER_ROW[0]), str(y + PRINTER_ROW[1] + PRINTER_ROW_PITCH * row))
                taken = wait_for(5, lambda n: dialog(n) and selector(n) == args.printer and n)
                if taken:
                    nodes = taken
                    break
                nodes = wait_for(3, lambda n: dialog(n) and selector(n) and n)
                tries.append(f"@{x},{y} {clicked.splitlines()[0] if clicked else 'no click output'} -> "
                             f"{selector(nodes) if nodes else 'no dialog'}")
                if not nodes:
                    break
            else:
                ax("press", "cancel", "--role", "AXButton", check=False)
                fail(f"the dialog offers {name}, not {args.printer}, and the printer popover did not "
                     f"take it in {POPOVER_TRIES} tries: " + "; ".join(tries))
            if not nodes:
                fail(f"the dialog closed under the printer popover clicks: " + "; ".join(tries))
            print(f"dialog: offered {name}; chose {args.printer} in the printer popover")
            name = selector(nodes)
        print(f"dialog: printer {name}")

        # 4. The filament mapping, by the tile it fills in.
        t = tile(nodes)
        if t is None:
            ax("press", "cancel", "--role", "AXButton", check=False)
            fail("no filament tile in the dialog")
        if t["label"] == "? ?":
            tries = []
            for attempt in range(POPOVER_TRIES):
                time.sleep(DIALOG_SETTLE)
                nodes = tree()
                t = tile(nodes) if dialog(nodes) else None
                if t is None or t["label"] != "? ?":
                    fail(f"filament tile changed before click {attempt + 1}: "
                         f"{t['label'] if t else 'dialog closed'}")
                x, y = t["x"], t["y"]
                click = ax("click", str(x + TILE_CENTRE[0]), str(y + TILE_CENTRE[1]),
                           str(x + EXTERNAL_SPOOL[0]), str(y + EXTERNAL_SPOOL[1]))
                time.sleep(1.0)
                nodes = tree()
                t = tile(nodes) if dialog(nodes) else None
                if t is not None and t["label"].startswith("Ext "):
                    print(f"mapping: external spool selected on attempt {attempt + 1}")
                    break
                result = t["label"] if t is not None else "dialog closed"
                tries.append(f"attempt {attempt + 1}: {click.splitlines()[-1]} -> {result}")
                if attempt == POPOVER_TRIES - 1:
                    if dialog(nodes):
                        ax("press", "cancel", "--role", "AXButton", check=False)
                    fail("external spool did not take: " + "; ".join(tries))
                # The tile toggles its popover. Reusing this dialog could close an
                # open popover, so every retry begins with a new dialog.
                if dialog(nodes):
                    ax("press", "cancel", "--role", "AXButton", check=False)
                    if not wait_for(5, lambda n: not dialog(n) and n):
                        fail("could not close the send dialog after a missed filament mapping: "
                             + "; ".join(tries))
                ax("press", "Print", "--role", "AXButton")
                nodes = wait_for(10, lambda n: dialog(n) and selector(n) == args.printer and n)
                if not nodes:
                    fail("could not reopen the send dialog for a fresh mapping attempt: "
                         + "; ".join(tries))
                print(f"mapping: retrying from a fresh {args.printer} dialog")
        if t is None or not t["label"].startswith("Ext "):
            ax("press", "cancel", "--role", "AXButton", check=False)
            fail(f"the filament tile reads {t['label'] if t else 'nothing'}; it must read the external spool")
        print(f"mapping: {t['label']}")

        # 5. The print options, read by which button carries the radio mark. The rows
        # render a moment after the dialog's frame, so wait for every label.
        nodes = wait_for(10, lambda n: len(options(n)) == len(STANDING_OPTIONS) and n)
        if not nodes:
            ax("press", "cancel", "--role", "AXButton", check=False)
            fail("the dialog's print options did not appear")
        for name, want in wanted.items():
            current, buttons = options(nodes).get(name, (None, []))
            if current == want:
                continue
            target = next((b for b in buttons if b["label"] == want), None)
            if target is None:
                ax("press", "cancel", "--role", "AXButton", check=False)
                fail(f"{name}: no {want} button")
            ax("press", f"#{target['idx']}", "--expect", want)
            time.sleep(0.6)
            nodes = tree()
        settled = {name: chosen for name, (chosen, _) in options(nodes).items()}
        if settled != wanted:
            ax("press", "cancel", "--role", "AXButton", check=False)
            fail(f"print options read {settled}, wanted {wanted}")
        print("options: " + ", ".join(f"{k} {v}" for k, v in settled.items()))

        # The Send button is disabled until the dialog has finished loading the printer,
        # and a disabled button takes an AXPress that does nothing; `tree` marks it.
        def send_button(n):
            buttons = find(n, role="AXButton", label="confirm")
            return buttons[0] if buttons else None
        ready = wait_for(15, lambda n: (b := send_button(n)) is not None and b["enabled"] and n)
        if args.dry_run:
            state = "enabled" if ready else "disabled"
            ax("press", "cancel", "--role", "AXButton")
            print(f"send: {state}; dry run: dialog cancelled, nothing sent")
            return None
        if not ready:
            ax("press", "cancel", "--role", "AXButton", check=False)
            fail("Send stayed disabled for 15 s: the printer is busy, or the dialog never finished loading it")

        # 6. Send, with the printer's report topic open to hear what reaches it. The dialog
        # closes when the application has taken the job; press again if it has not, and give
        # up rather than leave a dialog open.
        with Listener(printer) as listener:
            closed = False
            for attempt in range(3):
                ax("press", "confirm", "--role", "AXButton")
                if wait_for(8, lambda n: not dialog(n) and n):
                    closed = True
                    break
                print(f"send: dialog still open after press {attempt + 1}")
            if not closed:
                ax("press", "cancel", "--role", "AXButton", check=False)
                fail("the Send press did not close the dialog three times; nothing was sent")
            print("send: dialog closed")
            # What the application shows after Send: its device page reads Downloading while
            # the printer fetches the file, and a failed send leaves a toast that fades, so the
            # page is read at once, a second later and five seconds later.
            closed_at = time.monotonic()
            for mark in (0, 1, 5):
                time.sleep(max(0.0, closed_at + mark - time.monotonic()))
                page = ax("state", check=False).split("\n", 1)[0]
                print(f"send: page +{mark}s " + page[:260])

            # 7. The printer's own word: PREPARE or RUNNING under this name. The name alone
            # is not it; the earlier job can carry the same one.
            deadline = time.monotonic() + args.accept_timeout
            reading = None
            while time.monotonic() < deadline:
                time.sleep(5)
                reading = status(printer)
                if reading.get("subtask_name") == archive.name and reading.get("gcode_state") in ("PREPARE", "RUNNING"):
                    break
            else:
                heard = listener.drain()
                same_job = reading is not None and reading.get("job_id") == before.get("job_id")
                raise Refused(
                    f"{args.printer} did not report {archive.name} as PREPARE or RUNNING within {args.accept_timeout:g}s; "
                    f"before the send it was {before.get('gcode_state')} on {before.get('subtask_name')} (job {before.get('job_id')}), "
                    f"and the last reading is {reading.get('gcode_state') if reading else None} on "
                    f"{reading.get('subtask_name') if reading else None} (job {reading.get('job_id') if reading else None})"
                    + ("; the job id has not moved, so no new job reached the printer" if same_job else "")
                    + ("; the printer reported: " + json.dumps(heard) if heard
                       else "; the printer's report topic carried no command reply, upload or error"),
                    reading, heard)
            heard = listener.drain()
            if heard:
                print("send: printer reported " + json.dumps(heard)[:600])
        return reading

    # A send the printer drops is sent again from a fresh dialog: after a filament load that
    # began after the first reading, once the heaters are idle; after a send that never
    # reached it (the application closed its dialog and the job id did not move), after a
    # pause. Each round reads the printer first and sends only to an idle one, so a first
    # send that arrives late makes the printer busy and the next round stops there.
    reading = None
    for round_ in range(SEND_ROUNDS):
        try:
            reading = send_once(before)
            break
        except Refused as refused:
            reading = refused.reading
            print(f"send: {refused}")
            if round_ == SEND_ROUNDS - 1:
                fail(str(refused))
            heat = manual_heat(reading) if reading else None
            if heat:
                print(f"{args.printer}: {heat}; sending again when the heaters are idle")
                before = wait_out_heat(printer, args.printer, args.busy_wait)
                continue
            if any(h.get("command") == "project_file" for h in refused.heard):
                fail(str(refused) + "; the printer answered the command, so it is not sent again")
            time.sleep(RESEND_PAUSE)
            before = status(printer)
            upload = (before.get("upload") or {}).get("status")
            if upload not in (None, "idle"):
                fail(f"{args.printer} shows an upload ({upload}) after the send; not sending again")
            if manual_heat(before):
                before = wait_out_heat(printer, args.printer, args.busy_wait)
            if before.get("gcode_state") in BUSY:
                if before.get("subtask_name") == archive.name:
                    reading = before
                    print(f"send: {archive.name} arrived late; {args.printer} is {before['gcode_state']}")
                    break
                fail(f"{args.printer} became {before['gcode_state']} on {before.get('subtask_name')}; nothing more was sent")
            print(f"send: round {round_ + 2} of {SEND_ROUNDS}: nothing reached {args.printer}; sending again")
    if args.dry_run:
        return
    fields = ("gcode_state", "subtask_name", "layer_num", "total_layer_num", "mc_percent", "mc_remaining_time", "print_error")
    print(json.dumps({"printer": args.printer, "observed_at": bambu_printer.datetime.now(bambu_printer.timezone.utc).isoformat(),
                      "before_send": {k: before.get(k) for k in ("gcode_state", "subtask_name", "layer_num", "mc_percent")},
                      **{k: reading.get(k) for k in fields}}, indent=2))


if __name__ == "__main__":
    main()
