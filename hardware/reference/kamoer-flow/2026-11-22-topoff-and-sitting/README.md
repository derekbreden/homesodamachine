# Pump A's slow top-off, and the first pour after sitting

Codex's overnight record left two questions that only the sink bench could answer. Pump A moved more concentrate than the frozen model allowed on the low, steady top-off, and nobody knew which part of that program carried the extra. Every pour in that record also began from a conditioned head, while a real pour begins after the machine has sat. This record runs both on the same bench, cup, camera sightlines and frozen model, the next morning. Pump A withdraws concentrate from the graduated cup; pump B returns it from the dish.

## What came out

**The slow top-off's excess did not come back.** On A the same top-off program moved less concentrate than the frozen model forecast, on both sightlines, in every repeat. Varying one ingredient at a time showed what A did instead: a nearly fixed amount per short burst. The shortfall grew in proportion to the burst count, with no per-pour part to speak of, and it did not change with the gap between bursts or with the starting level in the cup. A slightly wider burst at the shortest gap moved no more per burst, where the model credits the extra motor time. By the registered rules, the per-burst excess, the gap and the level are each ruled out as carriers of Codex's excess, and the excess itself did not reproduce. What the record shows instead is that A's yield per short burst differs between sessions: this morning it matched A's slowest training pours, overnight it was well above them. [Rulings, contrasts and per-burst doses](results/topoff.json) · [Every pour](results/pours.csv)

**B switched between two yields on the same short bursts.** Most of B's top-offs moved a steady amount per burst. A run of them in the middle of the experiment moved clearly more per burst, then B went back. The higher yield is close to what A delivered on Codex's top-offs. A head whose short-burst yield has two states, set by something that persists between pours, would explain both A's overnight excess and B's jumps. This record does not identify that something. [Every pour](results/pours.csv)

**Sitting did not change the first pour beyond the model's start term.** After every sit, short, medium and long, the first top-off on each head landed inside the tolerance of its frozen forecast on the primary sightline, and the miss did not grow with sitting time. The registered claim stands on both heads. The first pour after a sit tended to move slightly less than the conditioned pour right after it, by much less than the tolerance, and that difference did not grow with the sit either. Both heads' doses on this program crept up over the session. [Sat and conditioned pours by sitting time](results/sitting.csv) · [Summary and registered verdict](results/sitting.json)

**A run of full glasses: unresolved, with one striking pour.** By the registered rule the test is unresolved: the mean of A's top-offs after the glasses rose by more than the ruling-out difference and less than the supporting one, on the primary sightline only. The mean hides what happened. The first top-off after the glasses moved, on both heads and both sightlines, about what Codex's overnight top-offs moved on A. The next two went straight back to the session's usual yield. A camera reading lost to a lighting change halted the run once, between the glasses and that first top-off; the resumed run began with a short positioning gate on A. [Before and after doses](results/history.json) · [Every pour](results/pours.csv)

**Full glasses.** A full glass on each head early in the session and another late landed inside the tolerance of Codex's frozen forecasts on both sightlines, as did the two further glass pairs of the history test. A ran a little under its forecast each time and did not drift; B ran under its forecast early and over it late, so B's yield rose during the session. [Glass checks](results/glasses.json)

## What was tested

The design, the programs with their motor schedules and the frozen forecasts were committed before the first pump ran: [design](design.json), [programs and forecasts](programs.json), [registration commit](https://github.com/derekbreden/homesodamachine/commit/3e67b1bdb80623de05edfe778cb9ab3911241317). The model is Codex's, unchanged ([model-used.json](model-used.json), [`dose_model.py`](analysis/dose_model.py)). Each program's motor schedule comes from replaying the firmware pour policy on its meter signals ([`policy_trace.cpp`](acquisition/policy_trace.cpp), [`make_design.py`](analysis/make_design.py)), and every pour's controller receipt matched its replayed burst count.

The top-off test varied Codex's top-off on A one ingredient at a time: fewer and more bursts at the same pulse and gap, the training gap and a shorter one, and a start high and low in the cup. Three randomized blocks ran each variant once on A, each from its registered starting level, with the same program on B as the return stroke. B's doses are a control on the same programs.

The sitting test used the two-burst training top-off, which the model fits on both heads, so a miss reflects the sit rather than A's top-off. The cup was set with single gates, then neither head moved for the sitting time and no conditioning pulse ran. A then B poured the top-off, and at once A then B poured it again as the conditioned comparison. The sits ran in mixed order.

The history test was registered after the top-off test came back, and before it ran: [design](design-history.json), [registration commit](https://github.com/derekbreden/homesodamachine/commit/f02902f5cfec2477ded0aaa15fb9038f6d96866d).

The controller ran its installed firmware, with the laptop supplying water-meter signals over the console and the controller driving the pumps at full power ([`run.py`](acquisition/run.py), Codex's unchanged [`board.py`](acquisition/board.py) and [`meter.py`](acquisition/meter.py)). Before any program, one short gate per head confirmed that A lowers the cup and B raises it.

## How the cup was read

Codex's reader and cup calibration read the photographs, through a different capture path ([camera evidence](camera/README.md)). Before any pump ran, the resting cup was read through ten separately opened camera streams. The primary sightline repeated to a small fraction of the dose tolerance across reopened streams; the far sightline jumps between two nearby readings. The resting level sat below Codex's parked level on both sightlines by the same volume, and the printed marks had not moved in the frame. Evaporation over the hours between is the likely cause; the sits did not give a clean evaporation rate, because the cup keeps settling after positioning gates. [Reader validation](results/reader-validation.json)

## Bench state at the end

The cup was returned to the level found at the start of the session, the controller read back idle pumps, all valves closed, volume at zero, flavor A and both ratios as found, and the camera controls read back exactly as found. No process from this session was left running. [Final journal](logs/)

## Reproduce

From this directory with Python, NumPy and Pillow (SciPy optional), and a C++ compiler for the policy replay:

```sh
python3 optics/replay_endpoints.py .
python3 analysis/score.py logs
c++ -std=c++17 -I ../../../../firmware/lib/machine_policy acquisition/policy_trace.cpp ../../../../firmware/lib/machine_policy/pour_policy.cpp -o /tmp/policy_trace && python3 analysis/make_design.py /tmp/policy_trace
```

The first replays every photograph from its archived pixels; the second rebuilds the results tables from the journals; the third rebuilds the programs and forecasts.
