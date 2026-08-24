#!/usr/bin/env python3
"""The targets a `--keep_going` build did not complete, off its build event log.

    bazel build --keep_going --build_event_json_file=bep.json //:everything
    tools/cad-venv/bin/python tools/bazel/failed_targets.py bep.json

`--keep_going` builds every target whose inputs are ready and leaves the rest, so a run with
one red target has every other target's fresh output sitting in `bazel-bin`. `sync_tree.py` and
`cut_vs_lock.py` both take `--failed` and carry the rest; this is what names them.

WHY THE EVENT LOG AND NOT THE CONSOLE. The failure text bazel prints is for a person — it wraps,
it interleaves with the output of whatever was running beside it, and the label sits inside a
sentence. `targetCompleted` is one event per target carrying its label and whether it completed,
which is the same question this asks.

A TARGET NOBODY ANALYZED HAS NO EVENT. A pattern that does not resolve stops the build before
analysis, and then there are no target events at all — an empty answer from a build that did
nothing is the same text as an empty answer from a build where everything passed, so the caller
reads bazel's own exit status for that and this speaks only about targets it saw.
"""
import json
import sys
from pathlib import Path


def failed(lines) -> list:
    """Every label whose `targetCompleted` event does not say it completed."""
    out = []
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        label = event.get("id", {}).get("targetCompleted", {}).get("label")
        if label and not event.get("completed", {}).get("success"):
            out.append(label)
    return sorted(set(out))


def selftest() -> int:
    holds = 0

    def hold(label, got, want):
        nonlocal holds
        ok = got == want
        holds += ok
        print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else f" — {got!r} != {want!r}"))

    ok = '{"id":{"targetCompleted":{"label":"//:a"}},"completed":{"success":true}}'
    bad = '{"id":{"targetCompleted":{"label":"//:b"}},"completed":{"failureDetail":{}}}'
    other = '{"id":{"progress":{"opaqueCount":1}},"progress":{}}'

    hold("a completed target is not named", failed([ok]), [])
    hold("a target that did not complete is named", failed([bad]), ["//:b"])
    hold("the good ones come back clean beside a bad one", failed([ok, bad]), ["//:b"])
    hold("an event that is not a target is skipped", failed([other]), [])
    hold("a line that is not json is skipped", failed(["not json", bad]), ["//:b"])
    hold("a label named twice is named once", failed([bad, bad]), ["//:b"])
    hold("no events at all is empty", failed([]), [])
    print(f"failed_targets selftest {holds}/7")
    return 0 if holds == 7 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    if not argv:
        print("usage: failed_targets.py <build_event_json_file>", file=sys.stderr)
        return 2
    path = Path(argv[0])
    if not path.is_file():
        return 0
    print(",".join(failed(path.read_text().splitlines())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
