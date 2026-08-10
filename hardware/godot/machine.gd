# The pack in the engine: a scene read at run time, lit, and framed on its own extents.
#
# `_scene.py` writes one glTF per assembly — a node per placement over the triangles a part
# module drew. `GLTFDocument` reads it here rather than the editor importing it, so a rebuilt
# scene is picked up by running again and the project carries no copy of the machine.
#
#   godot --path hardware/godot -- --scene <path.glb> --shot <out.png> --view iso
#
# `--hide enclosure*` drops bodies by name, the way the elevations drop the shell to read the
# pack inside it. With no `--shot` the window stays open and the mouse orbits.

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
