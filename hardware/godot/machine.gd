# The pack in the engine: a scene read at run time, lit, and framed on its own extents.
#
# `_scene.py` writes one glTF per assembly — a node per placement over the triangles a part
# module drew. `GLTFDocument` reads it here rather than the editor importing it, so a rebuilt
# scene is picked up by running again and the project carries no copy of the machine.
#
#   godot --path hardware/godot -- --scene <path.glb> --shot <out.png> --view iso
#
# `--hide enclosure*` drops bodies by name, the way the elevations drop the shell to read the
# pack inside it. `--card <scorecard.json>` puts the card on the view and paints the bodies its
# failing rows name, so a row and the metal it is about are the same picture. With no `--shot`
# the window stays open and the mouse orbits.

extends Node3D

const VIEWS := {
	"iso": Vector3(0.62, 0.45, 0.65),
	"front": Vector3(0.0, 0.08, 1.0),
	"right": Vector3(1.0, 0.08, 0.0),
	"top": Vector3(0.0, 1.0, 0.06),
}

const FOV := 38.0
const MARGIN := 1.06

var _camera: Camera3D
var _target := Vector3.ZERO
var _reach := 1.0
var _orbit := Vector3(0.62, 0.45, 0.65)
var _dragging := false
var _shot := ""
var _only := ""
var _settle := 0


func _ready() -> void:
	var args := _arguments()
	var path: String = args.get("scene", "")
	if path == "":
		push_error("no --scene given; _scene.py writes one beside each layout's STEP")
		get_tree().quit(2)
		return
	var pack := _read(path)
	if pack == null:
		get_tree().quit(2)
		return
	add_child(pack)
	var dropped := _hide(pack, args.get("hide", ""))

	var box := _extents(pack)
	_target = box.get_center()
	_reach = box.size.length()
	_orbit = VIEWS.get(args.get("view", "iso"), VIEWS["iso"]).normalized()
	_shot = args.get("shot", "")

	_light()
	_environment()
	_look()
	_only = args.get("check", "")
	_card(pack, args.get("card", ""))
	print("%d bodies over %.0f × %.0f × %.0f mm, %d hidden" %
		[_bodies(pack), box.size.x, box.size.y, box.size.z, dropped])


func _arguments() -> Dictionary:
	var out := {}
	var argv := OS.get_cmdline_user_args()
	var i := 0
	while i < argv.size():
		if argv[i].begins_with("--") and i + 1 < argv.size():
			out[argv[i].substr(2)] = argv[i + 1]
			i += 2
		else:
			i += 1
	return out


func _read(path: String) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(path, state)
	if err != OK:
		push_error("%s did not read as glTF (%d)" % [path, err])
		return null
	return doc.generate_scene(state) as Node3D


func _extents(root: Node) -> AABB:
	# A body's own box, stood up by the matrix its node carries — the scene's extents are the
	# union, and nothing here re-measures geometry the layout already measured.
	var box := AABB()
	var first := true
	for node in _meshes(root):
		var own: AABB = node.get_aabb()
		var world: AABB = node.global_transform * own
		box = world if first else box.merge(world)
		first = false
	return box


func _meshes(node: Node) -> Array:
	var out := []
	if node is MeshInstance3D:
		out.append(node)
	for child in node.get_children():
		out.append_array(_meshes(child))
	return out


func _bodies(root: Node) -> int:
	return _meshes(root).size()


func _hide(root: Node, pattern: String) -> int:
	# A hidden body is out of the picture and out of the extents, so what is left frames itself.
	if pattern == "":
		return 0
	var gone := 0
	for node in _meshes(root):
		if node.name.match(pattern):
			node.queue_free()
			node.get_parent().remove_child(node)
			gone += 1
	return gone


func _card(pack: Node, path: String) -> void:
	if path == "":
		return
	var text := FileAccess.get_file_as_string(path)
	var card = JSON.parse_string(text)
	if card == null or not card.has("checks"):
		push_error("%s does not read as a scorecard" % path)
		return

	var only: String = _only
	var failing := []
	for check in card["checks"]:
		if check.get("status", "pass") != "fail":
			continue
		if only == "" or check.get("id", "") == only:
			failing.append(check)
	if failing.is_empty():
		push_error("no failing row%s" % ("" if only == "" else " with id %s" % only))
		return

	# A row names its bodies in its own prose, so the bodies are the scene's own names that turn
	# up in it — no second list to fall out of step with the card.
	var names := {}
	for mesh in _meshes(pack):
		for check in failing:
			for line in check.get("detail", []):
				if String(line).contains(mesh.name):
					names[mesh] = true
	# What a row is about is solid and everything else is a ghost, so a body named by a failing
	# row is readable through the machine it sits inside.
	for mesh in _meshes(pack):
		mesh.material_override = _flagged() if names.has(mesh) else _ghost(mesh)

	_panel(failing, card["checks"].size(), names.size())
	print("%d of %d checks failing, %d bodies painted" %
		[failing.size(), card["checks"].size(), names.size()])


func _flagged() -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.92, 0.20, 0.14)
	mat.emission_enabled = true
	mat.emission = Color(0.55, 0.06, 0.03)
	mat.emission_energy_multiplier = 0.9
	mat.render_priority = 2
	return mat


func _ghost(mesh: MeshInstance3D) -> StandardMaterial3D:
	# The body's own colour, thin enough to see past. Depth stays written so the ghost keeps the
	# shape of the machine rather than washing to a haze.
	var base := mesh.mesh.surface_get_material(0) as StandardMaterial3D
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(base.albedo_color if base else Color(0.6, 0.6, 0.6), 0.10)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	return mat


func _panel(failing: Array, total: int, painted: int) -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var box := PanelContainer.new()
	box.position = Vector2(28, 28)
	box.custom_minimum_size = Vector2(600, 0)
	var skin := StyleBoxFlat.new()
	skin.bg_color = Color(0.055, 0.060, 0.082, 0.96)
	skin.border_color = Color(0.18, 0.20, 0.26)
	skin.set_border_width_all(1)
	skin.set_corner_radius_all(6)
	skin.set_content_margin_all(16)
	box.add_theme_stylebox_override("panel", skin)
	layer.add_child(box)
	var label := RichTextLabel.new()
	label.bbcode_enabled = true
	label.fit_content = true
	label.custom_minimum_size = Vector2(568, 0)
	box.add_child(label)

	var lines := PackedStringArray()
	for check in failing:
		lines.append("[color=#ff6b5a]✗[/color]  %s" % check.get("label", check.get("id", "")))
		lines.append("      [color=#9aa3b2]%s  ·  wants %s[/color]" %
			[check.get("value", ""), check.get("target", "")])
		for line in check.get("detail", []).slice(0, 3):
			lines.append("      [color=#7d8494]— %s[/color]" % line)
	lines.append("")
	lines.append("[color=#8fbf7f]%d holding[/color]   ·   %d bodies painted" %
		[total - failing.size(), painted])
	label.text = "\n".join(lines)


func _light() -> void:
	# A key that throws the pack's own shadows, and a fill from the opposite quarter so a body
	# behind another is still read rather than lost.
	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-42.0, -35.0, 0.0)
	key.light_energy = 1.6
	key.shadow_enabled = true
	key.directional_shadow_max_distance = _reach * 4.0
	add_child(key)

	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-18.0, 140.0, 0.0)
	fill.light_energy = 0.35
	add_child(fill)


func _environment() -> void:
	# What two sessions could not land in three.js: occlusion in the tight interstices, bounced
	# light, and a filmic curve over the whole of it.
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.086, 0.090, 0.118)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.42, 0.45, 0.52)
	env.ambient_light_energy = 0.55

	env.ssao_enabled = true
	env.ssao_radius = 4.0
	env.ssao_intensity = 3.0
	env.ssao_detail = 1.0

	env.ssil_enabled = true
	env.ssil_intensity = 0.9

	env.sdfgi_enabled = true
	env.sdfgi_cascades = 4
	env.sdfgi_min_cell_size = _reach / 128.0

	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.tonemap_exposure = 1.15
	env.tonemap_white = 6.0

	var world := WorldEnvironment.new()
	world.environment = env
	add_child(world)

	_camera = Camera3D.new()
	_camera.fov = FOV
	_camera.near = 1.0
	_camera.far = _reach * 12.0
	add_child(_camera)
	get_viewport().use_taa = true


func _look() -> void:
	# Far enough back that the scene's own sphere fills the frame, so a pack and a coupon are
	# each framed on themselves rather than on a distance picked for one of them.
	var half := deg_to_rad(FOV) * 0.5
	var aspect := float(get_viewport().size.x) / float(get_viewport().size.y)
	if aspect < 1.0:
		half = atan(tan(half) * aspect)
	_camera.global_position = _target + _orbit * (_reach * 0.5 / sin(half)) * MARGIN
	_camera.look_at(_target, Vector3.UP)


func _process(_delta: float) -> void:
	if _shot == "":
		return
	# TAA and SDFGI converge over frames, so the shot is taken once the image has settled
	# rather than on the first one drawn.
	_settle += 1
	if _settle < 32:
		return
	var image := get_viewport().get_texture().get_image()
	var err := image.save_png(_shot)
	print("-> %s (%d × %d)" % [_shot, image.get_width(), image.get_height()] if err == OK
		else "%s did not write (%d)" % [_shot, err])
	get_tree().quit(0 if err == OK else 1)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		_dragging = event.pressed and event.button_index == MOUSE_BUTTON_LEFT
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_reach *= 0.92
			_look()
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_reach /= 0.92
			_look()
	elif event is InputEventMouseMotion and _dragging:
		var yaw: float = -event.relative.x * 0.008
		var pitch: float = -event.relative.y * 0.008
		_orbit = _orbit.rotated(Vector3.UP, yaw)
		_orbit = _orbit.rotated(_orbit.cross(Vector3.UP).normalized(), pitch).normalized()
		_look()
	elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		get_tree().quit()
