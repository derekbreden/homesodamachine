# HLGHLG POM check valve

One HLGHLG B0FSSZS6HH POM check valve accepts 1/4-inch OD tube at both ends.
It is not part of the appliance, and its acquisition is not recorded in the
purchase ledger. The pump-discharge water check is the
[neoFit ACHV44-E](../neofit-achv44-check/README.md); the assembly's
`discharge-chain` key names that part.

The envelope uses the listing's dimensioned photograph: **51 mm end to end,
Ø14 mm maximum**. Intermediate sections are photograph-scaled estimates, and
the 10 mm tube insertion is an estimate. The poppet, spring, seals and internal
flow passages are not modeled. Pressure rating, cracking pressure and
reverse-sealing performance are not established by this reference.

Local inlet is `(0, 0, 0)`, outlet `(0, 0, −51)`, flow along −Z.

```sh
tools/cad-venv/bin/python hardware/reference/hlghlg-check-valve/hlghlg_check_valve.py
```

[Listing](https://www.amazon.com/dp/B0FSSZS6HH)
