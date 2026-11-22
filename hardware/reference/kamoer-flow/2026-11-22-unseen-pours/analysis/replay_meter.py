"""Check reserved and transmitted meter schedules against the archived appliance policy."""
import argparse
import json
import subprocess
import tempfile
from itertools import accumulate, product
from pathlib import Path


RECORD = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def compile_policy(repo, tmp, revision):
    for name in ("pour_policy.cpp", "pour_policy.h"):
        source = subprocess.check_output(["git", "-C", str(repo), "show",
                                          f"{revision}:firmware/lib/machine_policy/{name}"])
        (tmp/name).write_bytes(source)
    exe = tmp/"policy_trace"
    subprocess.run(["c++", "-std=c++17", "-O2", "-I", str(tmp), str(RECORD/"acquisition/policy_trace.cpp"),
                    str(tmp/"pour_policy.cpp"), "-o", str(exe)], check=True)
    return exe


def replay(exe, ratio, pulses, boundaries):
    times = [0, *boundaries]
    command = [str(exe), str(ratio)]
    for a, b, count in zip(times, times[1:], pulses):
        command.extend((str(count), str(b-a)))
    trace = subprocess.check_output(command, text=True).splitlines()
    gates, closes = [], []
    for line in trace:
        a, b = line.split()
        if a == "stop":
            closes.append(int(b))
        else:
            gates.append([int(a), int(b)])
    if len(closes) != 1:
        raise ValueError(f"Expected one completed pour for {command[1:]}")
    return gates, closes[0]


def verify_design(exe, design, training):
    conditions = {}
    for name, case in design["scenarios"].items():
        pulses, durations = zip(*case["meter"])
        boundaries = list(accumulate(durations))
        expected, stop = replay(exe, case["ratio"], pulses, boundaries)
        if expected != case["ideal_gates_start_ms_width_ms"] or stop != case["ideal_stop_ms"]:
            raise ValueError(f"Policy source differs from registered schedule for {name}")
        if expected in training or len(expected) in {len(g) for g in training}:
            raise ValueError(f"A registered motor schedule or burst count already occurred in training: {name}")
        jitter_counts = {}
        for k, saved in case["boundary_jitter_check"].items():
            delta = int(k)
            variants = [replay(exe, case["ratio"], pulses, [b+j for b,j in zip(boundaries, offsets)])[0]
                        for offsets in product((-delta,0,delta), repeat=len(pulses))]
            counts = {"combinations":len(variants), "same_count":sum(len(v)==len(expected) for v in variants),
                      "identical_gates":sum(v==expected for v in variants)}
            if counts != saved:
                raise ValueError(f"Jitter replay differs at {name} for {delta} ms")
            jitter_counts[k] = counts
        conditions[name] = {"novel_motor_schedule":True, "novel_burst_count":True, "jitter_ms":jitter_counts}
    return conditions


def verify_transmitted(exe, design, journal):
    results, updates = [], []
    p = start = None
    for line in journal.read_text().splitlines():
        r = json.loads(line)
        if r["event"] == "prediction":
            p, start, updates = r, None, []
        elif r["event"] == "board_pour_start":
            start = r
        elif p and r["event"] == "tx" and r["command"].startswith("flow "):
            updates.append(r)
        elif p and start and r["event"] == "trial":
            case = design["scenarios"][p["scenario"]]
            pulses = [int(tx["command"].split()[1]) for tx in updates[:-1]]
            if [v[0] for v in case["meter"]] != pulses or updates[-1]["command"] != "flow 0 0":
                raise ValueError(f"Unexpected meter stages at index {p['index']}")
            boundaries = [round((tx["mono_ns"]/1e9 - start["first_receipt_clock"])*1000) for tx in updates[1:]]
            gates, close = replay(exe, case["ratio"], pulses, boundaries)
            expected = case["ideal_gates_start_ms_width_ms"]
            results.append({"index":p["index"], "boundaries_ms_from_start_receipt":boundaries,
                            "gates_match_registration":gates==expected, "replayed_stop_ms":close,
                            "observed_stop_ms":r["receipt"]["elapsed_ms"],
                            "burst_count_matches_receipt":len(gates)==r["receipt"]["bursts"]})
            p = start = None
    return results


def main(repo, journal, output):
    design = read(RECORD/"design.json")
    training = [r["gates"] for r in read(RECORD/"historical-gates.json")]
    revision = read(RECORD/"model.json")["training_revision"]
    with tempfile.TemporaryDirectory() as work:
        exe = compile_policy(repo, Path(work), revision)
        cases = verify_design(exe, design, training)
        rows = verify_transmitted(exe, design, journal)
    result = {"source_revision":revision, "unique_training_schedules":len(training),
              "scope":"Transmit boundaries relative to the first pour receipt, rounded to milliseconds. "
                      "Intermediate motor transitions are inferred from firmware replay.",
              "registered_programs":cases, "completed_pours":len(rows),
              "exact_replays":sum(r["gates_match_registration"] for r in rows),
              "observed_counts_matched":sum(r["burst_count_matches_receipt"] for r in rows), "pours":rows}
    output.write_text(json.dumps(result,indent=2)+"\n")
    print(f"{result['exact_replays']}/{len(rows)} completed pours replay the entire registered motor schedule.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--journal", type=Path, default=RECORD/"logs/validation.jsonl")
    ap.add_argument("--out", type=Path, default=RECORD/"results/policy-replay.json")
    args = ap.parse_args()
    main(args.repo, args.journal, args.out)
