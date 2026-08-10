# The grid, the ticks, the scale bar and the legend, drawn over the frame.
#
# The ticks are what a coordinate is read off, so the projection is orthographic and the grid
# lies in the view plane. Beside them the corner carries what the frame is of: the scene, the
# projection and its span, the target, the millimetres a pixel covers, how many bodies are solid,
# how many are ghosted and how many were dropped.
#
# Every number here is in the machine's own millimetres. The scene stands in glTF's +Y up, so a
# world point comes back through the pack's own transform before it is written down.

extends Control

const STEPS := [1.0, 2.0, 5.0, 10.0, 20.0, 25.0, 50.0, 100.0, 200.0, 500.0, 1000.0]
const WANT_LINES := 9
const AXES := ["x", "y", "z"]

var camera: Camera3D
var pack: Node3D
var legend := PackedStringArray()
var span := 0.0
var target := Vector3.ZERO
var ortho := false

var _font: Font
var _plane := [0, 2]      # which machine axes lie in the screen plane: right, up
var _step := 100.0
var _frame := Vector2(1600, 1200)
var _plate := Rect2()


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_font = ThemeDB.fallback_font


func _machine(world: Vector3) -> Vector3:
	return pack.global_transform.affine_inverse() * world


func _world(machine: Vector3) -> Vector3:
	return pack.global_transform * machine


func _read_plane() -> void:
	# The two machine axes that actually span the frame, found by projecting each one and taking
	# the two that move the most pixels. A view named `top` says which those are; measuring says
	# it for any camera the mouse has dragged to.
	var origin := camera.unproject_position(_world(Vector3.ZERO))
	var reach := []
	for i in 3:
		var axis := Vector3.ZERO
		axis[i] = span if span > 0.0 else 100.0
		reach.append([(camera.unproject_position(_world(axis)) - origin).length(), i])
	reach.sort_custom(func(a, b): return a[0] > b[0])
	var kept := [reach[0][1], reach[1][1]]
	kept.sort()
	# Right is the one running more horizontally; up is the other.
	var a := (camera.unproject_position(_world(_unit(kept[0]))) - origin)
	var b := (camera.unproject_position(_world(_unit(kept[1]))) - origin)
	_plane = [kept[0], kept[1]] if absf(a.x) >= absf(b.x) else [kept[1], kept[0]]


func _unit(i: int) -> Vector3:
	var v := Vector3.ZERO
	v[i] = 100.0
	return v


func _pick_step() -> void:
	# A step that lands about `WANT_LINES` lines across the frame, off the list a drawing uses.
	var across := span * 2.0 * (_frame.x / maxf(_frame.y, 1.0))
	_step = STEPS[STEPS.size() - 1]
	for s in STEPS:
		if across / s <= WANT_LINES:
			_step = s
			break


func _draw() -> void:
	if camera == null or pack == null:
		return
	_frame = get_viewport_rect().size
	_read_plane()
	_pick_step()
	_measure()
	_grid()
	_bar()
	_legend()


func _grid() -> void:
	var line := Color(0.42, 0.48, 0.62, 0.30)
	var text := Color(0.58, 0.64, 0.76, 0.85)
	# Centred on what the camera LOOKS AT. The camera itself sits off the view normal by
	# whatever tilt the view carries, and a grid hung off it reads every tick shifted by that.
	var centre := _machine(target)
	var right: int = _plane[0]
	var up: int = _plane[1]
	var reach := span * 2.5

	for axis in [right, up]:
		var first := floorf((centre[axis] - reach) / _step) * _step
		var at := first
		while at <= centre[axis] + reach:
			var a := centre
			var b := centre
			var other: int = up if axis == right else right
			a[axis] = at
			b[axis] = at
			a[other] = centre[other] - reach
			b[other] = centre[other] + reach
			var pa := camera.unproject_position(_world(a))
			var pb := camera.unproject_position(_world(b))
			if _on_screen(pa) or _on_screen(pb):
				draw_line(pa, pb, line, 1.0, true)
				var label := "%s%s" % [AXES[axis], _mm(at)]
				var edge := pa if pa.distance_to(Vector2(20, _frame.y - 20)) < pb.distance_to(Vector2(20, _frame.y - 20)) else pb
				var put := Vector2(clampf(edge.x + 4.0, 4.0, _frame.x - 60.0),
					clampf(edge.y - 4.0, 16.0, _frame.y - 6.0))
				var on := 0.0
				if axis == up:
					on = _edge_y(pa, pb)
					if on < 14.0 or on > _frame.y - 6.0:
						at += _step
						continue
					put = Vector2(6.0, on)
				else:
					on = _edge_x(pa, pb)
					if on < 2.0 or on > _frame.x - 56.0:
						at += _step
						continue
					put = Vector2(on + 3.0, _frame.y - 8.0)
				if not _plate.grow(6.0).has_point(put):
					draw_string(_font, put, label, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, text)
			at += _step


func _edge_x(a: Vector2, b: Vector2) -> float:
	return a.x if absf(a.y - _frame.y) < absf(b.y - _frame.y) else b.x


func _edge_y(a: Vector2, b: Vector2) -> float:
	return a.y if absf(a.x) < absf(b.x) else b.y


func _mm(v: float) -> String:
	# GDScript's String % has no %g, and a tick reading "100" beats one reading "100.000000".
	return "%d" % int(round(v)) if absf(v - round(v)) < 1e-6 else "%.1f" % v


func _on_screen(p: Vector2) -> bool:
	return p.x > -_frame.x and p.x < _frame.x * 2.0 and p.y > -_frame.y and p.y < _frame.y * 2.0


func _bar() -> void:
	# Measured through the projection actually used: two points a round number of mm apart,
	# projected, and the bar drawn between where they land.
	var centre := _machine(target)
	var right: int = _plane[0]
	var a := centre
	var b := centre
	a[right] = 0.0
	b[right] = _step * 2.0
	var px := absf(camera.unproject_position(_world(b)).x - camera.unproject_position(_world(a)).x)
	if px < 8.0 or px > _frame.x * 0.8:
		return
	var y := _frame.y - 34.0
	var x0 := _frame.x - 40.0 - px
	var ink := Color(0.82, 0.86, 0.94, 0.92)
	draw_line(Vector2(x0, y), Vector2(x0 + px, y), ink, 2.0)
	draw_line(Vector2(x0, y - 5.0), Vector2(x0, y + 5.0), ink, 2.0)
	draw_line(Vector2(x0 + px, y - 5.0), Vector2(x0 + px, y + 5.0), ink, 2.0)
	draw_string(_font, Vector2(x0, y - 10.0), "%s mm" % _mm(_step * 2.0),
		HORIZONTAL_ALIGNMENT_CENTER, px, 14, ink)


func _lines() -> PackedStringArray:
	var lines := legend.duplicate()
	lines.append("grid  %s mm on %s/%s" % [_mm(_step), AXES[_plane[0]], AXES[_plane[1]]])
	return lines


func _measure() -> void:
	# The plate's footprint before anything is drawn, so a tick knows to stay out from under it.
	var wide := 0.0
	for l in _lines():
		wide = maxf(wide, _font.get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, 13).x)
	_plate = Rect2(16, 16, wide + 24.0, _lines().size() * 17.0 + 18.0)


func _legend() -> void:
	var lines := _lines()
	var box := _plate
	draw_rect(box, Color(0.055, 0.060, 0.082, 0.90))
	draw_rect(box, Color(0.20, 0.23, 0.30), false, 1.0)
	var y := box.position.y + 22.0
	for i in lines.size():
		draw_string(_font, Vector2(box.position.x + 12.0, y), lines[i],
			HORIZONTAL_ALIGNMENT_LEFT, -1, 13,
			Color(0.90, 0.93, 0.98) if i == 0 else Color(0.62, 0.68, 0.80))
		y += 17.0
