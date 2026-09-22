#!/usr/bin/env python3
"""The targets a `--keep_going` build did not complete, off its build event log.

    bazel build --keep_going --build_event_json_file=bep.json //:everything
    tools/cad-venv/bin/python tools/bazel/failed_targets.py bep.json

`--keep_going` builds every target whose inputs are ready and leaves the rest, so a run with
one red target has every other target's fresh output sitting in `bazel-bin`. `sync_tree.py` and
`cut_vs_pointers.py` both take `--failed` and carry the rest; this is what names them.

WHY THE EVENT LOG AND NOT THE CONSOLE. The failure text bazel prints is for a person — it wraps,
it interleaves with the output of whatever was running beside it, and the label sits inside a
sentence. The event stream carries one event per thing that ran, with its label beside whether
it completed, which is the same question this asks.

TWO EVENTS ANSWER IT, AND ONLY ONE OF THEM IS ENOUGH. `targetCompleted` is emitted for the
targets the command REQUESTED. `//:everything` is a filegroup over every sync rule, so a build
of it requests exactly one target and that event names the umbrella — the genrule that actually
died is a dependency and never gets one. Reading `targetCompleted` alone, this returned the
single string `//:everything`, which resolves to no output directory, so the callers held back
nothing and excused nothing: every red run reported all 320 solids against an umbrella and the
carry never ran. `actionCompleted` is the per-action event and carries the label of the rule
whose command failed, which is the name a caller can hold an output against. Both are read and
the union is returned.

A FAILED ACTION IS THE ONLY ACTION PUBLISHED. Bazel emits `ActionExecuted` for failures always
and for successes only under `--build_event_publish_all_actions`, so an action event is read as
a failure unless it says otherwise.

A TARGET NOBODY ANALYZED HAS NO EVENT. A pattern that does not resolve stops the build before
analysis, and then there are no events at all — an empty answer from a build that did nothing is
the same text as an empty answer from a build where everything passed, so the caller reads
bazel's own exit status for that and this speaks only about what it saw.
"""
import json
import sys
from pathlib import Path


def failed(lines) -> list:
    """Every label whose target or action event does not say it succeeded."""
    out = []
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        ident = event.get("id", {})
        label = ident.get("targetCompleted", {}).get("label")
        if label and not event.get("completed", {}).get("success"):
            out.append(label)
        label = ident.get("actionCompleted", {}).get("label")
        if label and not event.get("action", {}).get("success"):
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
    act = ('{"id":{"actionCompleted":{"label":"//:enclosure","primaryOutput":"x"}},'
           '"action":{"exitCode":1,"type":"Genrule"}}')
    act_ok = ('{"id":{"actionCompleted":{"label":"//:c"}},'
              '"action":{"success":true,"type":"Genrule"}}')
    umbrella = ('{"id":{"targetCompleted":{"label":"//:everything"}},'
                '"completed":{"failureDetail":{}}}')

    hold("a completed target is not named", failed([ok]), [])
    hold("a target that did not complete is named", failed([bad]), ["//:b"])
    hold("the good ones come back clean beside a bad one", failed([ok, bad]), ["//:b"])
    hold("an event that is not a target is skipped", failed([other]), [])
    hold("a line that is not json is skipped", failed(["not json", bad]), ["//:b"])
    hold("a label named twice is named once", failed([bad, bad]), ["//:b"])
    hold("no events at all is empty", failed([]), [])
    hold("a failed action names its own rule", failed([act]), ["//:enclosure"])
    hold("an action that succeeded is not named", failed([act_ok]), [])
    hold("the rule under the umbrella is named beside it",
         failed([umbrella, act]), ["//:enclosure", "//:everything"])
    hold("one label from both events is named once",
         failed([bad, '{"id":{"actionCompleted":{"label":"//:b"}},"action":{"exitCode":1}}']),
         ["//:b"])
    print(f"failed_targets selftest {holds}/11")
    return 0 if holds == 11 else 1


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
