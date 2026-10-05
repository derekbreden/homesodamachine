# Tighter Beduan valve socket samples

Five small panels compare the four valve posts together in the enclosure-front-top
print orientation. Every panel retains the 24.4 × 24.85 mm post pattern, 6.2 mm
blind socket depth, 5.2 mm nominal post engagement, body bearing face, open port
channel and production teardrop crowns. The hole diameter is printed on each
panel's rear foot.

| Label on panel | Record label | Socket diameter | Clearance to nominal 6.90 mm post |
| --- | --- | --- | --- |
| 7.20 | V72 | 7.20 mm | +0.30 mm |
| 7.10 | V71 | 7.10 mm | +0.20 mm |
| 7.00 | V70 | 7.00 mm | +0.10 mm |
| 6.90 | V69 | 6.90 mm | 0.00 mm |
| 6.80 | V68 | 6.80 mm | −0.10 mm |

The 7.20 mm control retains the dimensions of the [accepted socket
coupon](../physical-acceptance.json). That acceptance covers easy valve location
with zip ties providing positive retention. That acceptance retains its scope.

The current [physical fit selection](../../../enclosure/enclosure/magnet-retention/fit-coupons/physical-fit-selection.json)
selects **V69 / 6.90 mm** as the preferred socket diameter.
**V70 / 7.00 mm** is a conditional alternative to try if a valve or print
orientation does not fit V69 well. Selection does not automatically substitute
V70, qualify every valve or mounting orientation, or establish retention load
and lifetime. The selected panels came from completed H2C centered task
**1310172582**.

[The physical request](physical-request.json) records the tighter-fit trial and
the scope of the earlier socket acceptance.

The upright panel is 43.6 mm wide, 44.05 mm tall and 9.2 mm thick. Its rear label
foot extends the bed footprint to 16.2 mm deep. The actual valve enters along
horizontal −Y, with its port aligned to the open vertical channel. All four posts
engage together and the valve body sets the final seating plane. No print pause
or internal socket support is required.

Compare the same valve across the panels, starting at 7.20 and working toward
the smaller holes. Press by hand until the broad body bearing sits fully against
the panel. Check for rocking, unwanted play and whether the valve stays seated
when the panel faces down. Pull it back along the socket axes for the next
sample. Skip a size that requires forcing. Report the preferred printed diameter
and whether it inserts and removes comfortably. Try the preferred sample on the
other valves to check part-to-part fit.

[Geometry and source bindings](geometry.json) record the four-post pattern,
socket diameters, blind floors and intentional nominal interference in 6.80.
[The fixture source check](fixture-source-verification.json) binds the frozen
exports to the current socket functions and dimensions.
Native toolpaths establish the commanded openings; cooled dimensions, retention
force and endurance require physical evidence from the printed samples.
