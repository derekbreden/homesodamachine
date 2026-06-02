# servo-valve-mock

Keep-out mock of a servo-actuated ball-valve cell: a Neo-Pure NeoFit 1/4"
quarter-turn ball valve (the all-plastic wetted path) with an MG90S micro servo
(the dry external actuator) coupled on a shared +Z stem axis.

`servo_valve_mock.py` builds the envelope, writes `servo-valve-mock.step`, and
renders front / end / strip SVGs to `/tmp`. Run it with the project venv:

    tools/cad-venv/bin/python hardware/printed-parts/reference/servo-valve-mock/servo_valve_mock.py

One cell: ~44 mm along the flow axis (ports out one way, servo ears the other)
x ~16 mm across the cross-flow stacking axis x ~53 mm tall. The servo's thin
12.5 mm face lies on the stacking axis, centered on and narrower than the ~16 mm
valve body, so the cross-flow pitch is set by the valve, not the servo. The
servo body, its offset output spline, the mounting ears, and the coupler are
catalog-nominal approximations, not manufacturing geometry.
