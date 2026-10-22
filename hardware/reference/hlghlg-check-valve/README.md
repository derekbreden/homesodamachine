# Water discharge check

One HLGHLG B0FSSZS6HH POM check valve accepts 1/4-inch OD tube at both ends.
It sits west of the G Ganen pump, inlet aft and outlet forward toward the cold
core's water-in conduit. The flow arrow points away from the pump.

The cap lid's round cradle supports the fixed barrel. One four-inch tie holds
it down, clear of both moving collets. The tie crosses a 2.8 mm wide, 3.25 mm
high tunnel with a flat lid floor and open mouths on both sides. The pump uses its ordinary printed TPU
elbow and two socket clamps. `water-6` connects the elbow to the check inlet;
`water-5` connects the outlet to the core.

The envelope uses the listing's dimensioned photograph: **51 mm end to end,
Ø14 mm maximum**. Intermediate sections are photograph-scaled estimates.
The tube insertion used in the cut schedule is an estimated **10 mm**; mark
actual full insertion before cutting assembly stock. The poppet, spring,
seals and internal flow passages are not modeled. Pressure rating, cracking
pressure and reverse-sealing performance are not established by this reference.
Acquisition is not recorded in the purchase ledger.

Local inlet is `(0, 0, 0)`, outlet `(0, 0, −51)`, flow along −Z. The installed
assembly and topology use the stable `discharge-chain` key for this single valve.

```sh
tools/cad-venv/bin/python hardware/reference/hlghlg-check-valve/hlghlg_check_valve.py
```

[Assembly](../../assembly/internal-plumbing.md) ·
[Selected part](https://www.amazon.com/dp/B0FSSZS6HH)
