"""Measure equal-on-time pulse schedules from matched cup levels on each restored pump channel."""
import argparse
import json
import re
import time
from pathlib import Path

import numpy as np
from PIL import Image

from position_after_reset import CAMERA, CONFIG, HERE, drive, endpoint, wait_from
from board import Board, Journal

DESIGN = json.loads((HERE / "rewired-pauses.json").read_text())
REFERENCE = np.asarray(Image.open(CAMERA / "windows/after-user-reset-inspect/average.png"), dtype=float)[::6, ::6]
RIMS = [(966, 986), (984, 988), (1002, 990), (1422, 894), (1476, 890),
        (1860, 873), (1896, 870), (1944, 870), (1986, 933), (2004, 928)]


def rim_guards():
    raw = (CAMERA / "live.pgm").read_bytes().split(b"\n", 4)
    seq, pts, _ = map(int, re.findall(rb"\d+", raw[1]))
    age = (time.monotonic_ns() - pts) / 1e9
    w, h = map(int, raw[2].split())
    if raw[0] != b"P5" or not 0 <= age < .48:
        raise RuntimeError("Missing or stale live camera guard")
    image = np.frombuffer(raw[4], dtype=np.uint8).reshape(h, w)
    checks = []
    for x, y in RIMS:
        xx, yy = round(x / 6), round(y / 6)
        roi = slice(xx-1, xx+2)
        pattern = REFERENCE[yy-3:yy+4, roi].mean(axis=1)
        pattern -= pattern.mean()
        scan = image[yy-12:yy+13, roi].mean(axis=1)
        segments = np.lib.stride_tricks.sliding_window_view(scan, len(pattern))
        segments = segments - segments.mean(axis=1, keepdims=True)
        scores = segments @ pattern / (np.linalg.norm(segments, axis=1)*np.linalg.norm(pattern) + 1e-9)
        best = int(np.argmax(scores))
        checks.append([x, 6*(best-9), round(float(scores[best]), 3)])
    good = [z for z in checks if abs(z[1]) <= 42 and z[2] > .82]
    # A wave can distort a single rim while separate portions of the cup remain readable.
    zones={int(x>=1250)+int(x>=1800) for x,_,_ in good}
    if len(good) < 3 or len(zones) < 2:
        raise RuntimeError(f"Liquid rim outside the live guard: {checks}")
    return {"seq":seq,"pts_ns":pts,"age_s":round(age,3),"rim":checks}


def set_level(board, journal, label, head):
    aim = DESIGN["start_px"][head]
    value, sample = endpoint(label + "-entry", journal, independent_ink=True)
    for k in range(2):
        if abs(value-aim) <= DESIGN["preferred_start_tolerance_px"]:
            break
        _, receipt = drive(board, journal, label, aim, "set_start", value, sample, "setup")
        wait_from(receipt, 3.5)
        value, sample = endpoint(f"{label}-set{k+1}", journal, independent_ink=True)
    if abs(value-aim) > DESIGN["maximum_start_tolerance_px"]:
        raise RuntimeError(f"Could not establish comparable starting level: {value}")
    return value, sample


def run(tag, start, end):
    path = HERE / (tag+".jsonl")
    if path.exists():
        raise FileExistsError(path)
    journal = Journal(path)
    board = Board("/dev/cu.usbserial-120", journal)
    try:
        for i, trial in enumerate(DESIGN["trials"]):
            if not start <= i <= end:
                continue
            block, condition, head = trial
            count, ms, gap = DESIGN["conditions"][condition]
            label = f"{tag}-{i:02d}"
            pre, sample = set_level(board,journal,label,head)
            null = CONFIG["pixels_per_second"][head] * count * ms / 1000
            journal.append("pulse_prediction", label=label, block=block, condition=condition, head=head,
                           count=count, width_ms=ms, gap_ms=gap, pre_endpoint=sample["label"],
                           pre_px=pre, null_delta_px=null, null_predicted_px=pre+null)
            receipts = []
            for j in range(count):
                if j:
                    due = receipts[0]["tx_ns"]/1e9 + j*(ms+gap)/1000
                    time.sleep(max(0, due-time.monotonic()))
                before = rim_guards()
                receipt = board.gate(head, ms)
                after = rim_guards()
                receipts.append(receipt)
                journal.append("pulse_gate", label=label, pulse=j+1, head=head, before=before,
                               after=after, **receipt)
            wait_from(receipts[-1], 4.0)
            post, observed = endpoint(label+"-observed", journal, independent_ink=True)
            sign = 1 if head=="A" else -1
            dose = (post-pre)*sign
            if dose <= 1:
                raise RuntimeError("No measurable transfer in the commanded direction")
            journal.append("pulse_score", label=label, block=block, condition=condition, head=head,
                           pre_px=pre, post_px=post, delta_px=post-pre, positive_dose_px=dose,
                           observed_endpoint=observed["label"], null_error_px=(post-pre)-null)
            print(label,block,head,condition,"from",round(pre,2),"to",round(post,2),"transfer px",round(dose,2),flush=True)
    except Exception as err:
        journal.append("halt", reason=str(err))
        raise
    finally:
        board.close()
        journal.append("session_end")


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tag");ap.add_argument("start",type=int);ap.add_argument("end",type=int)
    args=ap.parse_args()
    run(args.tag,args.start,args.end)
