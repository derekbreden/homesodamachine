# room-16: which way is down (a lens on the work's orientation)

**Origin:** wave 3 new direction (the work in another orientation; the station around it). **Scene:** `scenes/room-16-which-way-is-down` (a lens, tagged so). **Depth:** developed as a lens; the arrangement that uses it is `room-17`.

## Picture it

A slider tips the tube about the seam's tangent through the dot: 0 is today's standing tube, 30 leans it over the station, 90 lays it horizontal with the station at the bottom, 180 inverts it. The gun stays where it is on the work and turns with it. Three views follow the slider: a section across the seam, the same seen from the side, and a table of numbers; below them five small plots show each number over the whole range, and a map shows in which directions a camera could stand in the room and still see the corner.

## The proposal

Ask what gravity does at the corner in each orientation, before anyone builds one. The rows (all [derived] from the kit's proxy gun and the repo's tube; `explorers/room/calc/orientation-family.mjs`):

| tilt | pool: onto plate / wall | barrel from vertical, A / B | weight lever, A / B (mm) | argon pond (mm) | cable exit above horizontal (A) | tube weight across its axis (N) |
|---|---|---|---|---|---|---|
| 0 (today) | 1.00 / 0.00 | 45 / 30 | 148 / 118 | 6.3 | 30 | 0 |
| 30 | 0.87 / 0.50 | 33 / 0 | 125 / 23 | 5.5 | 33 | 6.9 |
| 45 | 0.71 / 0.71 | 35 / 15 | 130 / 29 | 4.5 | 31 | 9.7 |
| 90 (horizontal) | 0.00 / 1.00 | 63 / 60 | 182 / 159 | 0 | 13 | 13.7 |
| 180 (inverted) | -1.00 / 0.00 | 135 / 150 | 148 / 118 | 0 | -30 | 0 |

Attitude A is the reference opening pose (wire on the gun); B is travel-16's radial-plane attitude (no wire on the gun).

## What carries, what locates, what is free

Not an arrangement, so nothing carries or moves. What the lens locates: the seam's tangent at the station stays horizontal for any tilt about it, so the pool never runs along the seam; the *bisector* of the corner is vertical at 45 degrees of tilt (a symmetric trough); the gun's weight lever depends on how far the barrel is from plumb and on the centre of mass's offset from the barrel axis.

## What software could command, observe, and what stays manual

Nothing is commanded or observed in the lens. What it says for software: the **map** of camera stations in room coordinates (the visible cone turns with the work; 43 % of the room's upper hemisphere sees the corner from 0 to 90 degrees of tilt toward the station, 0 at -90 and at 180), and that a tilt is a state an inclinometer can read. Manual: welding a coupon on a slope, weighing the gun, measuring the printed race's tip-over.

## What was tried to break it

1. **"Tipping about the tangent plumbs the gun."** *Variant:* the reference gun. *Assumption:* the barrel's lean is a matter of the tilt. *Finding:* the barrel leans 45 degrees in the section and 32 out of it along the seam; tipping about the tangent removes the first only. At best 32.4 degrees from vertical at 32.5 degrees of tilt; the lever falls by a sixth. *Change:* take the wire off the gun (attitude B or B2): exactly plumb at 30 degrees, lever 23 mm. Tipping about a radial axis would plumb the reference gun too, but slopes the seam by 32 degrees: pool downhill or uphill depending on the direction of rotation; a process question. *Leaves:* the wire's alignment (room-17).
2. **"Tipping opens the view for cameras."** *Finding:* the cone (toward the bore, over the far rim: tan(elevation) at least 6.35 / (123.7 cos azimuth) in the work's frame) is turned, not enlarged. Toward the station it lifts the plate's far edge: a bench-height far-side camera 12 degrees up loses the corner by about 9 degrees of tilt (elevation minus 2.9 degrees), a 20-degree one by 17, a 30-degree one by 27, overhead at 70 degrees by about 65. At 90 degrees the cone points out of the mouth: overhead sees the tube's outside. *Leaves:* the gun, cords, the operator and glare are not in the map.
3. **"The pocket is a bucket."** *Finding:* the argon pond at the station is set by the lowest point of the rim: 6.35 mm at 0, 5.5 at 30, 4.5 at 45, none by 90 (a chute); tipping away loses it at once. The only orientation that holds a bucket is today's.
4. **"Inverted or horizontal is a different rotator."** *Finding:* the printed race is gravity-seated and lifts on its uphill side at about 29 to 35 degrees for a rotating centre of mass 118 to 151 mm over it; at 90 degrees the tube's weight is a 13.7 N side load, a bearing problem; a bought positioner (sourcing 26) is thin on volume evidence and stated repeatability.
5. **"The cable route changes."** *Finding:* the exit line climbs 30 to 33 degrees for A at 0 to 45 degrees, 65 degrees for B at 30, 13 degrees at 90 and falls at 120 degrees and beyond; the route to a hook is short only where it climbs steeply.

## Branches and combinations

`room-17` is the arrangement that uses the finding (B at 30 degrees). Combines travel-16's attitudes and travel-03's idea of tilting the work. The lens could take a second axis (tilt about the radial line, the seam slope) and a spread of gun masses; not built.

## Unresolved problems, and questions that need Derek's observation

- Does the melt care about a symmetric trough (about 45 degrees of tilt) or a slope? A hand-welded coupon on an incline, a phone photo of each bead.
- Gun mass, centre of mass, umbilical pull (weigh-in of room-02); the real wire bracket's geometry.
- The rotating centre of mass's height over the race.

## Assumptions

Proxy gun, 1.47 kg, centre of mass local (0, -23, 181): **[illustrative]**. Tube dimensions, rotating mass 1.40 kg, race 165 mm pitch circle: **[repo]**. Argon 1.78 kg/m3 against air 1.20 (ordinary gas data). Everything in the table **[derived]**.

## Sourcing pointers

`sourcing/room.md` entries 22 (IMU for a tilt reading) and 26 (bought positioners and roller stands).

## Scene

`scenes/room-16-which-way-is-down`
