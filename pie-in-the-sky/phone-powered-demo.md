# Phone-powered live demo

*Pie-in-the-sky, not roadmap. Captured 2026-07-06.*

A pocketable demonstration prop — the actual controller PCB and the 4.3" front
display in a small case — that runs entirely from a phone over one USB-C cable,
drives the display, and physically clicks a valve on the manifold in response to
touch on that display. It exists to prove, in person, that the designed board is
real and controls hardware. The click is genuine: the board itself switching a
real solenoid.

## The goal

The controller board draws its power from an iPhone 15 Pro's USB-C port — 5 V, a
few watts — and from that alone brings up its logic, powers and drives the 4.3B
display over the RS485 link on J9
([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx)), and actuates a manifold solenoid on
command from the display. The envelope is *click, not run* — it actuates valves,
it does not run pumps or sustain fluid movement. Draining the phone is
acceptable; the display losing power is not.

## What it needs

Three capabilities and one guard:

1. **The phone's 5 V reaching the 5 V rail.** VBUS reaches the rail through
   reverse isolation — an ideal-diode or power-mux — coexisting with the board's
   own 5 V supply without contention or back-feeding the phone.

2. **A 12 V rail synthesized from that 5 V.** The display (7–36 V on J9) and the
   solenoid (12 V coil) both run on 12 V; a boost stage from the 5 V rail
   recreates the rail they share.

3. **The valve's actuation buffered locally.** A solenoid click is a brief,
   high-current draw on the same 12 V the display runs on — more than the phone
   can source while holding the display up. A local energy reservoir on the
   valve's 12 V, isolated from the display's, sources the click and refills
   slowly, so it never collapses the display's supply.

4. **The synthesized 12 V kept off the real 12 V inlet.** On an external 12 V
   supply the boost output and that rail must not contend — arbitration between
   them, or the boost populated only on a demonstration build.
