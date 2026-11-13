# Reed sweep rig controller

One ESP32 dev board steps the [reed sweep rig](/hardware/assembly/reed-sweep-rig.md)'s slide
through a TMC2209, finds the rig's home switch, and prints every reed change with the step the
sled stood at. It decides nothing about what the reeds mean: its lines are the record a host
reads.

The wiring is the table in the [build guide](/hardware/assembly/reed-sweep-rig.md#wiring), and
the pins are the constants at the top of [`main.cpp`](main.cpp).
[`lib/reed_rig_policy`](../lib/reed_rig_policy/reed_rig_policy.h) holds every decision, tested on
the build host. The rig's numbers reach it in
[`reed-sweep-rig-datums.h`](/hardware/printed-parts/fixtures/reed-sweep-rig/reed-sweep-rig-datums.h),
which the rig's fixture program writes.

## Build and flash

    pio run -e reed_rig -t upload --upload-port <port>

`hsm-peripheral boards` names the ports. The console is the board's own USB at 115200 baud.

## Positions

The controller counts steps from the home switch's trip, positive into the tube. To a person it
names a position as the sled's near face in millimetres from the comb's tab. The tab stands a
little behind home: by a bank card's thickness when the striker is set as the build guide sets
it, which is the distance the controller starts with. `tab <mm>` keeps a measured one in flash.

A commanded position never lies behind home. The tab is there, and the switch's lever has
little travel left once it has tripped.

## Commands

| Command | What it does |
|---|---|
| `status` | Where the sled stands and what the home switch and every reed read |
| `home` | Backs off a pressed switch, seeks it, creeps onto it and counts how far back it lets go |
| `goto <mm>` | Puts the sled's near face that far from the tab |
| `jog <mm>` | Moves by that much, positive into the tube; before homing, only into the tube |
| `sweep <from> <to> [mm/s] [cycles]` | Reads the reeds from the nearer end out to the farther and back, at one speed |
| `tab <mm>` | Keeps a measured distance from the tab to the sled's face at home |
| `dirinvert on` / `off` | For a motor that turns the other way |
| `homelevel high` / `low` | The home switch's pin when it is pressed |
| `release` | Lets the motor go |

Any line sent while the sled moves stops it. A move stopped from speed, or a homing stopped
partway, leaves the sled unhomed.

`home` refuses a switch that reads free and has not been seen to change since power-up: press
its lever once by hand first. A lead that is unplugged reads pressed at the delivered level, so
homing backs away from it and gives up without going near the tab.

## Lines a program reads

Every command ends in one line that begins `OK` or `ERR`. Lines that begin with a letter and a
comma carry the record:

| Line | Meaning |
|---|---|
| `I,key=value,...` | What the controller is, its steps to a millimetre, the tab's distance behind home, and where it stands |
| `P,<leg>,<+ or ->,<step>,<reeds>` | A read leg begins: its number, its direction, where the sled stands and every reed, station 1 first |
| `R,<station>,<0 or 1>,<step>,<microseconds>` | A reed opened or closed, at the step the sled stood at when it first read differently |
| `E,<leg>,<step>,<reeds>` | The leg ended |

`R` lines print whenever a reed changes, sweep or no sweep, so a float moved by hand shows on
the console.
