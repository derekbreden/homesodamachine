# The bench state

`hsm-peripheral bench` keeps the notices a machine with no water rightly shows off its
displays while the machine is on this laptop's USB, so the bench shows the pages someone is
working on.

A machine on the bench runs the production firmware. With no supply, no tank and no gas it
has things to say: the tank did not fill, the first start has not been done. In a kitchen
those are right. On the bench they cover the displays. Which of them to keep off is this
laptop's to say, and the machine keeps none of it.

## What holds what

| | |
|---|---|
| `~/.config/hsm-bench/hold` | The bench state: the names of the notices to keep off, on one line. No file, or no names, holds nothing. |
| `hsm-peripheral bench-watch` | The watcher. It finds every main board on USB and says the state to its console, again every few seconds, for as long as the board is there. launchd runs it from `~/Library/LaunchAgents/com.homesodamachine.bench.plist` and its log is `~/.config/hsm-bench/watch.log`. |
| `notice hold <name>…` | What the watcher says. The main board keeps those notices off both displays for `kNoticeHoldLeaseMs` ([`machine.h`](/firmware/src_appliance/machine.h)) and then stops by itself, so a machine that leaves the bench is a production machine again without being told. |

Only what the displays say is held. A refill that stands latched still stands, and its pump
stays off. A board that restarts starts with nothing held, and the watcher says it again
within a few seconds: a board that powers up re-enumerates on USB, and one that restarts
without leaving USB is caught by the next renewal.

A name the firmware has no notice for costs nothing: the board says so and holds the rest.
The state can name a notice before the firmware that shows it exists.

## Use

```sh
hsm-peripheral bench                         # the state, the watcher, and what each board answers
hsm-peripheral bench hold no-water welcome   # keep these off, from now on
hsm-peripheral bench off                     # hold nothing: the displays say what a kitchen's would
hsm-peripheral bench agent install           # start the watcher now and at every login
hsm-peripheral bench agent remove
```

`bench hold` and `bench off` write the state and say it to the boards at once; the watcher
follows the file within its next pass.

To see or test a notice on the bench, run `hsm-peripheral bench off` first, and put the hold
back when done. `status` on the main board's console says which notice stands and whether a
host is holding it off.

## Beside the other tools

The watcher has a board's port only for the fraction of a second one exchange takes, and it
opens it without restarting the board and with neither strapping line held
([`open_quiet`](/tools/hsm/peripheral/src/serials.rs)). A port another program has open to
itself is left alone until it is free. `hsm-peripheral`'s own tools wait out an exchange they
land on. A program that opens the port without taking it for itself is talked over: bench
scripts open it exclusively, as `hsm-peripheral console-session` does.
