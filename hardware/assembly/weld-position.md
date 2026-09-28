# Gun at the joint

The [3D orientation scene](https://homesodamachine.com/weld-position)
shows the carbonator tube, one recessed endcap, the X1 Pro gun, wire and laser.
The camera has overall, top and joint views. Dragging orbits the camera.
Three rotation controls share the laser dot as their pivot.

At zero grip-axis and vertical-axis rotation, the gun's barrel and wire
approach follow the tangent in plan view. The grip axis is the line through
the precise laser dot and the cable exit at the bottom of the grip.
Both endpoints stay fixed as the gun rolls and tips the laser between the
endcap and tube wall. The straight wire guide rolls with the gun and remains
aimed at the dot.

At zero vertical-axis rotation, the hole axis runs through the laser dot and
both endcap hole centers, along the diameter at the cap's outer face. Its
control tilts the entire gun and grip axis around that line. The dot, tube
and cap stay fixed. Increasing the angle raises the grip. The dial reads 35°
at the reference mounting inclination; zero is 35° below that inclination.
At each hole-axis setting, grip-axis roll still fixes both the dot and grip base.

The vertical axis stays parallel to the tube's centerline and passes through
the laser dot. Its control turns the entire gun in plan, carrying the grip
and hole axes with it. Zero retains the tangent approach; positive angles
turn counterclockwise as seen from above. The laser dot and every point's
height stay fixed during this turn. The control spans −90° to 90°.

The umbilical exits the grip. The external wire feed runs straight beside it
and through the grip-base region. A short support leg holds the straight tip
guide close to the barrel. The unsupported span bends smoothly between the
straight run at the grip and the straight guide aimed at the dot. The modeled
paths show their arrangement; cable routing, guide mounting and clearances
are schematic.

The tube dimensions come from
[`_rotator_interface.py`](../printed-parts/fixtures/weld-rotator/_rotator_interface.py).
The disc and port dimensions come from
[`endcap_circular_dxf.py`](../cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py).
The scene's dimension check holds those values against the fabrication sources.

The gun is a geometric proxy based on the X1 Pro manual's section 3.4 drawing
(253 × 143 × 34 mm overall). Its housing sections, grip, wire guide, 60° initial
pitch and 16 mm nozzle clearance are illustrative. The opening grip-axis roll
is 45°, hole-axis roll is 35°, and vertical-axis rotation is 0°.
The straight 2 mm laser sweep intersects the modeled surfaces at their first
hit; it illustrates orientation, without calculating wall/cap energy percentages
or establishing a welding setup. Gun scanning and measured optical geometry
can supply the next level of detail.

The scene source is [`web/public/js/weld-position/`](../../web/public/js/weld-position/).
