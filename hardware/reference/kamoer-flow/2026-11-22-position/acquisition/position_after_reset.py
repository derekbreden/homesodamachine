"""Predict the time needed to reach each photographed destination and measure the first and final miss."""
import argparse
import json
import socket
import time
from pathlib import Path

from board import Board, Journal
import reset_check

HERE = Path(__file__).resolve().parent
CAMERA = HERE.parent / "camera"
CONFIG = json.loads((HERE / "rewired-design.json").read_text())


def endpoint(label, journal, independent_ink=False):
    port = json.loads((CAMERA / "port.json").read_text())["port"]
    with socket.create_connection(("127.0.0.1", port), timeout=12) as sock:
        sock.sendall((json.dumps({"label": label, "samples": 11, "seconds": .6}) + "\n").encode())
        result = json.loads(sock.makefile("rb").readline())
    if "error" in result:
        raise RuntimeError(result["error"])
    if time.monotonic_ns() - result["mid"]["pts_ns"] > 2_000_000_000:
        raise RuntimeError("Camera window was stale")
    readings = reset_check.read(Path(result["directory"]))
    if independent_ink and "dry_ink" not in readings and readings["left_clear"].get("ok"):
        left = readings["left_clear"]["raw_row"]
        # The dry-cup fit uses the upper printing even when liquid hides a lower scale.
        readings["dry_ink"] = reset_check.register_cup.form(
            Path(result["directory"]) / "color.png", 952., left,
            reset_check.REFERENCE / "dry-ink.npz")
    event = journal.append("endpoint", label=label, seq=result["mid"]["seq"],
                           pts_ns=result["mid"]["pts_ns"], readings=readings)
    left = readings["left_clear"]
    if not left["ok"] or left.get("patches", 0) < 5 or left["patch_mad_px"] > 1.6:
        raise RuntimeError("Left contact is unreadable")
    delta = left["delta_from_reference_px"]
    corroborated = [key for key, scale in CONFIG["relative_stretch"].items()
                    if readings[key].get("ok") and
                    abs(readings[key]["delta_from_reference_px"] / scale - delta) <= 4.0]
    if not corroborated or abs(delta) >= 18.7:
        raise RuntimeError(f"Contact outside calibrated band or uncorroborated: {delta:.2f}, {corroborated}")
    for side in ("left", "right"):
        marks = readings["dry_ink"][side]
        if abs(marks["dy"]) > 6 or marks["dry_fit_max_residual_px"] > 1.5:
            raise RuntimeError("Printed cup marks moved beyond their local reference")
    return delta, event


def drive(board, journal, label, target, phase, pre, prev, policy):
    head = "A" if target > pre else "B"
    rate = CONFIG["pixels_per_second"][head]
    ms = round(1000 * abs(target - pre) / abs(rate))
    if not 15 <= ms <= 1250:
        raise RuntimeError(f"Time {ms} is outside this local test")
    if time.monotonic_ns() - prev["pts_ns"] > 2_000_000_000:
        raise RuntimeError("Live endpoint expired before drive")
    journal.append("prediction", label=label, phase=phase, policy=policy, channel=head,
                   pre_endpoint=prev["label"], pre_px=pre, target_px=target, ms=ms,
                   predicted_px=pre + rate * ms / 1000)
    receipt = board.gate(head, ms)
    journal.append("gate", label=label, phase=phase, channel=head, **receipt)
    return head, receipt


def wait_from(receipt, delay):
    time.sleep(max(0, receipt["done_ack_ns"] / 1e9 + delay - time.monotonic()))


def run(tag, first, last):
    path = HERE / (tag + ".jsonl")
    if path.exists():
        raise FileExistsError(path)
    journal = Journal(path)
    board = Board("/dev/cu.usbserial-120", journal)
    try:
        for i in range(first, last + 1):
            label = f"{tag}-{i:02d}"
            target, policy = CONFIG["trials"][i]
            pre, start = endpoint(label + "-pre", journal)
            if policy == "idle":
                journal.append("blank_start", label=label, pre_px=pre)
                time.sleep(4.2)
                end, _ = endpoint(label + "-hold", journal)
                journal.append("blank", label=label, pre_px=pre, end_px=end, drift_px=end-pre)
                print(label, "idle", round(end-pre, 2), flush=True)
                if abs(end-pre) > 1.8:
                    raise RuntimeError("Quiet cup moved")
                continue
            head, receipt = drive(board, journal, label, target, "first", pre, start, policy)
            wait_from(receipt, CONFIG["first_endpoint_delay_s"])
            actual, post = endpoint(label + "-first", journal)
            journal.append("first_score", label=label, head=head, target_px=target, policy=policy,
                           before_px=pre, observed_px=actual, error_px=actual-target)
            direction = (actual-pre) * (1 if head == "A" else -1)
            if direction < -1.0 or (abs(target-pre)>5 and direction < 1.0):
                raise RuntimeError("Photographed transfer disagrees with commanded direction")
            corrected = False
            if policy == "correct" and abs(actual-target) >= CONFIG["correction_deadband_px"]:
                _, receipt = drive(board, journal, label, target, "correct", actual, post, policy)
                corrected = True
                wait_from(receipt, CONFIG["first_endpoint_delay_s"])
                corrected_level, _ = endpoint(label + "-corrected", journal)
                journal.append("correction_score", label=label, observed_px=corrected_level,
                               target_px=target, error_px=corrected_level-target)
            wait_from(receipt, CONFIG["final_endpoint_delay_s"])
            final, _ = endpoint(label + "-final", journal)
            journal.append("final_score", label=label, head=head, policy=policy, corrected=corrected,
                           target_px=target, observed_px=final, error_px=final-target)
            print(label, head, policy, "requested", target, "first error", round(actual-target, 2),
                  "final error", round(final-target, 2), flush=True)
    except Exception as err:
        journal.append("halt", reason=str(err))
        raise
    finally:
        board.close()
        journal.append("session_end")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("first", type=int)
    parser.add_argument("last", type=int)
    args = parser.parse_args()
    run(args.tag, args.first, args.last)
