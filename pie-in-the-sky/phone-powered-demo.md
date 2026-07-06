# Phone-powered live demo

*Pie-in-the-sky, not roadmap. Captured 2026-07-06.*

A pocketable demonstration prop — the actual controller PCB and the 4.3" front
display in a small case — that runs entirely from a phone over one USB-C cable,
drives the display, and physically clicks a valve on the manifold in response to
touch on that display. It exists to prove, in person, that the designed board is
real and controls hardware. The actuation has to be genuine — the board itself
switching a real solenoid — not an animation, and not a hidden battery faking
the moment.

## The goal

The controller board draws its power from an iPhone 15 Pro's USB-C port — 5 V, a
few watts — and from that alone brings up its logic, powers and drives the 4.3B
display over the RS485 display link on J9, and actuates a manifold solenoid on
command from the display. The envelope is *click, not run*: it actuates valves,
it does not sustain fluid movement or turn pumps, which exceed what a phone can
source. Draining the phone is acceptable; the display losing power is not; and
the valve click being real is the whole point.

## What it needs

Three capabilities the board lacks today, plus one guard:

1. **The phone's 5 V reaching the board's 5 V rail.** The USB-C port is
   data-only right now — VBUS powers nothing. VBUS has to feed the logic rail
   through reverse isolation (an ideal-diode or power-mux), so it coexists with
   the normal 12 V-derived 5 V without contention and without back-feeding the
   phone.

2. **A 12 V rail synthesized from that 5 V.** The board makes no 12 V of its own
   when USB-powered; its regulator only steps 12 V down. Both the display
   (7–36 V on J9) and the solenoid (12 V coil) run on 12 V, so a boost stage
   from the 5 V rail is necessary to recreate the rail they share.

3. **The valve's actuation buffered locally.** A solenoid click is a brief, high
   current draw on the same 12 V the display depends on, and the phone cannot
   source that peak and hold the display up at the same time. A local energy
   reservoir on the valve's 12 V — isolated from the display's — lets the click
   draw from the reservoir and refill slowly, so it never collapses the
   display's supply. This is why the actuation is pulsed rather than held.

4. **The synthesized 12 V kept off the real 12 V inlet.** Run normally on an
   external 12 V supply, the boost output and the real rail must not contend —
   so either arbitration between the two, or the boost present only on a
   demonstration build of the board.

## Where the build stands

None of this is on the board. The USB-C port is the data-only programming port:
VBUS lands only on the ESD clamp, the CC lines carry the 5.1 k sink pulldowns,
and everything above the logic rails depends on an external 12 V supply —
including the display, which is fed 12 V and RS485 over J9
([`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx)) only while that
supply is present. This doc holds the phone-powered live demo as a want for a
later pass.
