# Firmware tests

The native suite holds machine policy that does not need, open, reset, or drive a board:

```bash
pio test -e native
```

`test_front_ui_policy` checks Stop-only operation locks from queued Start through completion,
prime cancellation exits, remote flavor changes on flavor versus machine pages, and stale
sensor readings including clock wrap.
`test_flavor_selection` checks first-install adoption, established-main-board authority,
absolute/idempotent selection, corrupt storage, and failed-write retry state.
`test_machine_policy` checks the canonical V-A–V-K operation plans, the three-valve ceiling,
the dispense/refill exclusion, every possible off-before-on valve-mask transition, the
prime/timed-pump deadlines shared with the J9 protocol, the funnel fill's plan, its
draw-time budget against the slowest rated head, and its full-reed-before-clock ending, and
the clean cycle's opening funnel step — the Through state, timed to empty a full funnel at the
slowest rated head and draw the line clear — and its two steps a round per channel, its
full-reed and empty-reed-plus-tail endings, the sum of what is left of a cycle, and its wire
contract, the reservoir gauge's reading of one float passing four reeds up through a fill and
down through a draw, and the air cycles' steps — the dry
sweep of both channels that draws on no reservoir, and the purge that airs one and draws it
out. It also checks that Prime queries renew the main-board lease while giving queued J9
announcements a turn, that snapshots stay fresh through a full queue at dark-display polling
speed, and that discovery queries and direct hold/stop/cancel replies retain priority.
`test_machine_prime` runs the production machine arbiter and expander driver with host
GPIO, clock and I2C fakes. It checks wet Prime's reservoir dispense pairs, pump-before-valve
stop ordering including expander faults, token/session retries and competing displays,
cancel/disconnect/heartbeat/lease/ceiling endings, gas and I/O admission, the falling
reservoir gauge, refill/pour exclusion and fan preservation. Console motor checks and the
self-test remain individual motor loads. Cleaning checks cover both channels pumping tap
water into their reservoirs, stopping on the full reed or deadline, restarting on the flush
path, cutting tap pressure at each stop while leaving the outlet open for coast-down,
skipping a full reservoir, and stopping motors before emergency valve closure on reed and
health-read faults in every cleaning step. They cover inlet-close failures and gas stops.
These tests do not establish
physical wet operation.
`test_machine_log` keeps the machine's record in a flash region made of RAM that can only
clear bits and can lose power part-way through a write. It checks that an entry survives its
round trip and that any damaged byte is seen, that a restart finds the head and carries the
count on, that a full ring asks for one erase and loses only its oldest sector, that power
lost in a write costs one slot wherever in the entry it fell — a sector's first slot
included — that a region holding other bytes starts clean, that an entry is found by its number past
spoiled slots, round the ring and after a restart, and the line an entry reads as. The update
trial itself is the bootloader's and has no host test: a board taking an update is its check.
`test_machine_prime` holds what the production machine code notes: a pour with its length
and bursts, a refill draw ending full, taken down by a pour, or timing out with the fault
sounded once, a compressor run with its coldest coil, probes that never answer, a probe that
chatters and the gas alarm inside the note gap, and a prime and a fill as they end. It
checks that the compressor is not started when its fan's write fails, that a running one
stops when the valve drivers stop answering, that a bus glitch is verified away once the
machine is idle and a pour injects again, and that nothing is re-verified under a running
operation. A refill owed when the power went is resumed by the boot after with the pumping
time it had spent, a board that restarts over and over cannot buy the pump more than its
ceiling, a timed-out refill stays stopped through time and restarts until it is asked to try
again, a fill asked for at the console runs to the high reed, and a refill a pretend reading
asked for is not kept. A bench's hold keeps a notice off the glasses and changes nothing
else, and ends with its lease, a release or a restart. The loop watchdog has no host test:
`hang` on a bench board is its check.
`test_machine_month` lives a month at a kitchen sink on the build host: the production machine
code against a carbonator that drains and fills, a cooling loop that warms and cools, and a
household that pours, with the clock crossing its wrap on the way. An ordinary month must
make every glass a soda with no fault sounded. A month of trouble shuts the water off for a
morning, cuts the power four times — once mid-refill and once just after a pitcher has taken
the water below the low reed — loses a probe, glitches the bus twice, trips the gas alarm and
runs the suction line to its freeze cutoff; every poor glass must fall inside a trouble, and
the month must end with every glass a soda and nothing latched. Both hold the machine to what
it must never do at every step: more than three valves, the refill pump during a dispense or
against a closed V-K, the compressor inside its minimum off-time or without its fan, and one
refill pumped past its ceiling, through every restart, with nobody asking for it.
`MONTH_FLASH_FORGETS=1` and `MONTH_NOBODY_ASKS=1` run the same month with what the flash keeps
taken away, or with nobody at the machine asking it to try the water again after a poor
glass, to see what each is for. The kitchen's numbers are a plausible kitchen, not a
measured one.
`test_pour_policy` checks the pour's cycle timing at 1:20, 1:6 and 1:24, the clamps either
side of the flow reading and the floor and ceiling on the two phases, the sequence one pour
walks — valves and pump opening on the first reading, each cycle's timing taken from the
average over the last, a cooldown that holds the path open when flow returns inside it and
closes it when nothing does — the 120 s ceiling a meter that never stops pulsing runs into, and
the sample period and pulse counts the meter is read through. `test_pcba_expanders` checks the
logical-to-physical valve map, safe MCP23017 initialization, active-low reed decoding,
cross-expander break-before-make writes, and fail-park behavior. `test_sound_policy` walks
every volume against every quiet ceiling at every hour including no clock at all, and holds
the gas alarm at full through all of them; it also checks the quiet window's midnight wrap,
its empty case, and that the duty conversion is linear in amplitude rather than in duty.
`test_echo_policy` checks that a frame the main board sent comes back and is swallowed whole,
that a collision abandons the outstanding echo instead of eating the far end's next frame,
and that the ring wraps under sustained traffic and holds a whole stuffed J9 frame.
`test_phone_trust_policy` checks the faucet's Trust request: its window closes on time however
often the request is repeated, declines back off across new connections and rotating
identities, a refused request extends nothing, and its deadlines survive the clock's wrap. They run on the build host
and are safe with every USB device connected. `test_weld_rotator_policy` checks the purchased
20T:90T drive ratio, speed envelope, exact 380-degree lap count, boot-held pedal lockout,
deadman release, and jog/lap state transitions.

Board builds remain separate because they compile different source trees:

```bash
pio run -e appliance
pio run -e esp32s3_front
pio run -e esp32s3_faucet
pio run -e pcba_bench
pio run -e weld_rotator
```

Building does not open a serial port. Uploading and monitoring do; name the port whenever
more than one board is connected (`hsm-peripheral boards` prints the exact commands).

With the working main board and enclosure display connected, the default live check only observes
the display, touch controller, J9 link, and synchronized/durable flavor state through the
display's native USB port. The optional checks are deliberately explicit: `--animation`
opens the reusable operation lock long enough to measure it; `--toggle` selects the other
flavor, proves main board synchronization and persistence, and restores it; `--prime a|b`
actuates that pump for about one second through the same handlers the glass uses and always
posts a stop request. Each check restores the page, idle rung and lock state it found.

```bash
hsm-peripheral firmware-live-check
hsm-peripheral firmware-live-check --animation
hsm-peripheral firmware-live-check --toggle
hsm-peripheral firmware-live-check --prime b
```

With the faucet display connected to J3 and its native USB connected, the faucet check never
drives an actuator. Its default mode proves convergence, both persistence states, request
latency and loop/link-service high-water marks. `--toggle` explicitly selects the other
flavor, waits for both stores, and restores the original selection; the main board makes one
tick for each of those two user-path selections.

```bash
hsm-peripheral firmware-faucet-check
hsm-peripheral firmware-faucet-check --toggle
```
