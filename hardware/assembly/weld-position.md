# Gun at the joint

The [3D orientation scene](https://homesodamachine.com/weld-position)
shows the carbonator tube, one recessed endcap, the X1 Pro gun, wire and laser.
The camera has overall, top and joint views. Dragging orbits the camera.
Two rotation controls share the laser dot as their pivot.

At zero roll, the gun's barrel and wire approach follow the tangent in plan
view. The grip axis is the line through the precise laser dot and the cable
exit at the bottom of the grip. Its plan projection follows the tangent.
Both endpoints stay fixed as the gun rolls and tips the laser between the
endcap and tube wall. The final wire guide lies on this axis, pointing at the
dot, so its straight approach remains fixed too.

The hole axis runs through the laser dot and both endcap hole centers, along
the diameter at the cap's outer face. Its control tilts the entire gun and
grip axis around that fixed line. The dot, tube and cap stay fixed. Positive
angles raise the grip; zero preserves the reference inclination. At each
hole-axis setting, grip-axis roll still fixes both the dot and grip base.

The umbilical exits the grip. The wire feed is external and runs beside it
before reaching the guide. Keeping them together and the base on the tangent
limits the bend demanded of the wire feed. Their short modeled paths show
their arrangement; cable routing, guide mounting and clearances are schematic.

The tube dimensions come from
[`_rotator_interface.py`](../printed-parts/fixtures/weld-rotator/_rotator_interface.py).
The disc and port dimensions come from
[`endcap_circular_dxf.py`](../cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py).
The scene's dimension check holds those values against the fabrication sources.

The gun is a geometric proxy based on the X1 Pro manual's section 3.4 drawing
(253 × 143 × 34 mm overall). Its housing sections, grip, wire guide, 60° initial
pitch and 16 mm nozzle clearance are illustrative. The opening grip-axis roll
is 35° and hole-axis roll is 0°.
The straight 2 mm laser sweep intersects the modeled surfaces at their first
hit; it illustrates orientation, without calculating wall/cap energy percentages
or establishing a welding setup. Gun scanning and measured optical geometry
can supply the next level of detail.

The scene source is [`web/public/js/weld-position/`](../../web/public/js/weld-position/).
