# Shared-circuit startup trial

H2C and Mark2 share a circuit. Derek reports repeated breaker trips when both printers
start close together, including during his own manual operation. His requested trial
is a minimum **three-minute interval**, measured from the first printer's accepted job
to sending the second. Electrical load and the exact breaker-trip time are unmeasured.

The original cover-trial launch receipts are **54.421746 seconds apart**:

| Printer | Task | Launch receipt, UTC |
| --- | --- | --- |
| Mark2 | 1289348260 | 2026-09-28 04:38:34.195922 |
| H2C | 1289349395 | 2026-09-28 04:39:28.617668 |

Derek reports the breaker restored. Both machines report FAILED at layer 0, with zero
print error and no HMS entries. Neither has an automatically resumed print. The restart
uses the same reviewed archives, verified by SHA-256, with the same geometry and settings.

The [observation record](observation.json) binds the original receipts, the post-restoration
readings and the staggered restart receipts. Print completion and physical fit are separate
observations from successful startup.

The restart launches were accepted **236.083844 seconds (3 min 56 sec) apart**. The
H2C sender was invoked 209.095952 seconds after Mark2's accepted launch, passing the
180-second minimum before any second Send click. Both receipts report RUNNING, zero
print error and no HMS entries.

| Printer | Restart task | Launch receipt, UTC |
| --- | --- | --- |
| Mark2 | 1289413482 | 2026-09-28 05:28:54.123406 |
| H2C | 1289418578 | 2026-09-28 05:32:50.207250 |

At 05:39:17 UTC, both beds reached **80°C** and both jobs remained RUNNING with no
print errors or HMS entries. Mark2 was printing layer 1/58; H2C was still in its startup
checks at layer 0/60. Mark2 held its bed at 80°C before H2C began heating its bed. No
power loss was observed during these [warm-up readings](warmup-readings.json).

This trial records a 3 min 56 sec separation. The three-minute minimum remains the
operating trial; full print completion and physical fit are still pending.
