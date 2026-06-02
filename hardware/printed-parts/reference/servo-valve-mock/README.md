# servo-valve-mock

Keep-out mock of a servo-actuated ball-valve cell: a Neo-Pure NeoFit 1/4"
quarter-turn ball valve (the all-plastic wetted path) with an MG90S micro servo
(the dry external actuator) coupled on a shared +Z stem axis. A thin back-plate
stands in for a printed bracket.

`servo_valve_mock.py` builds the envelope and writes `servo-valve-mock.step`.
Run it with the project venv:

    tools/cad-venv/bin/python hardware/printed-parts/reference/servo-valve-mock/servo_valve_mock.py

Envelope: 44 mm along the flow axis x 18 mm x 62 mm tall. The servo body, its
offset output spline, the mounting ears, the coupler, and the bracket plate are
catalog-nominal approximations, not manufacturing geometry.
