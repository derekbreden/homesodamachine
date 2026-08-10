# Several bodies finding room against each other at once.
#
# `fit.search` moves one body against a frozen world and `arrange.rank` turns a chain, so a
# question about how a SET of parts goes together comes back as a column of clearances. Here the
# named bodies are free at the same time, every other body is the world they land in, and what
# comes out is an arrangement — where each one ended up, and how far that is from where its rule
# put it.
#
#   godot --path hardware/godot res://settle.tscn -- \
#       --scene <path.glb> --free "pump-*" --steps 600 --out settled.json
#
# THE BODIES START WHERE THEIR RULES PUT THEM AND NOTHING PULLS ON THEM. What moves a body is
# another body already inside it, so a pack that closes comes back unmoved and a pack that does
# not comes back with the smallest rearrangement that opens it. `--gravity 9806.65` instead lets
# them fall, which answers a question about a shelf rather than about a machine whose parts are
# mounted: a tube routed between two ports, set free, lands on the floor.
#
# The reading is a proposal. `_settled.py` carries it back to the layout, where a rule is what
# seats a body and the card is what grades it.

extends Node3D

const DENSITY := 1.0e-6          # kg per mm³ — a body's own box, so heavy things fall heavy
const SETTLED := 0.05            # mm per step under which a body is standing still
const WARMUP := 60               # steps before stillness means settled rather than not yet moving

var _DECOMPOSE := MeshConvexDecompositionSettings.new()
var _root: Node3D
var _free: Array[RigidBody3D] = []
var _from := {}
var _steps := 600
var _taken := 0
var _out := ""


func _ready() -> void:
	_DECOMPOSE.max_convex_hulls = 16
	_DECOMPOSE.resolution = 20000
	_DECOMPOSE.max_concavity = 0.001
	var args := _arguments()
	var path: String = args.get("scene", "")
	var pattern: String = args.get("free", "")
	_out = args.get("out", "")
	_steps = int(args.get("steps", "600"))
	if path == "" or pattern == "":
		push_error("--scene and --free are both wanted; --free takes a name pattern")
		get_tree().quit(2)
		return

	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file(path, state) != OK:
		push_error("%s did not read as glTF" % path)
		get_tree().quit(2)
		return
	_root = doc.generate_scene(state) as Node3D
	add_child(_root)

	# Down is -Y once the scene's root has stood the machine up, and the machine is millimetres.
	var pull := float(args.get("gravity", "0"))
	var space := get_viewport().find_world_3d().space
	PhysicsServer3D.area_set_param(space, PhysicsServer3D.AREA_PARAM_GRAVITY_VECTOR, Vector3.DOWN)
	PhysicsServer3D.area_set_param(space, PhysicsServer3D.AREA_PARAM_GRAVITY, pull)

	var held := 0
	for mesh in _meshes(_root):
		if mesh.name.match(pattern):
			_release(mesh)
		else:
			_hold(mesh)
			held += 1
	if _free.is_empty():
		push_error("no body's name matched %s" % pattern)
		get_tree().quit(2)
		return
	print("%d free against %d held, %d steps, gravity %.0f mm/s²" %
		[_free.size(), held, _steps, pull])


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


func _meshes(node: Node) -> Array:
	var out := []
	if node is MeshInstance3D:
		out.append(node)
	for child in node.get_children():
		out.append_array(_meshes(child))
	return out


func _hold(mesh: MeshInstance3D) -> void:
	# A body that is not moving collides on its own triangles, so a free body lands in the shape
	# of the thing it lands on rather than in that thing's hull.
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	shape.shape = mesh.mesh.create_trimesh_shape()
	body.add_child(shape)
	mesh.add_child(body)


func _release(mesh: MeshInstance3D) -> void:
	# A MOVING BODY IS CARRIED AS SEVERAL CONVEX PIECES, NOT AS ONE HULL. A hull of a bent tube
	# spans the bend, and a hull of a valve's coil spans the gap under it, so two bodies standing
	# clear of each other read as deeply inside each other and the whole pack flies apart. The
	# decomposition follows the concavities the pack is built out of.
	var body := RigidBody3D.new()
	body.name = "free-" + mesh.name
	mesh.create_multiple_convex_collisions(_DECOMPOSE)
	var pieces: StaticBody3D = null
	for child in mesh.get_children():
		if child is StaticBody3D:
			pieces = child
	for child in pieces.get_children():
		pieces.remove_child(child)
		body.add_child(child)
	mesh.remove_child(pieces)
	pieces.free()

	var box := mesh.get_aabb()
	body.mass = maxf(box.size.x * box.size.y * box.size.z * DENSITY, 0.001)
	body.continuous_cd = true
	body.linear_damp = 1.5
	body.angular_damp = 4.0

	var stood := mesh.global_transform
	var parent := mesh.get_parent()
	parent.remove_child(mesh)
	_root.add_child(body)
	body.global_transform = stood
	body.add_child(mesh)
	mesh.transform = Transform3D.IDENTITY

	_from[body.name] = _local(stood)
	_free.append(body)


func _local(stood: Transform3D) -> Transform3D:
	"""Where a body stands, in the frame the layout uses rather than the one glTF stood it in."""
	return _root.global_transform.affine_inverse() * stood


func _physics_process(_delta: float) -> void:
	_taken += 1
	if _taken < _steps and (_taken < WARMUP or not _still()):
		return
	_write()
	get_tree().quit(0)


func _still() -> bool:
	for body in _free:
		if body.linear_velocity.length() * get_physics_process_delta_time() > SETTLED:
			return false
	return true


func _write() -> void:
	var rows := []
	for body in _free:
		var was: Transform3D = _from[body.name]
		var now := _local(body.global_transform)
		var turn := (was.basis.inverse() * now.basis).get_euler()
		rows.append({
			"name": String(body.name).trim_prefix("free-"),
			"from": _columns(was),
			"to": _columns(now),
			"moved": (now.origin - was.origin).length(),
			"turned": rad_to_deg(maxf(maxf(absf(turn.x), absf(turn.y)), absf(turn.z))),
		})
	rows.sort_custom(func(a, b): return a["moved"] > b["moved"])
	var report := {"steps": _taken, "settled": _still(), "bodies": rows}
	if _out == "":
		print(JSON.stringify(report, "  "))
	else:
		var f := FileAccess.open(_out, FileAccess.WRITE)
		f.store_string(JSON.stringify(report, "  "))
		f.close()
		print("-> %s  %d bodies, %d steps, %s" %
			[_out, rows.size(), _taken, "settled" if _still() else "still moving"])
	for row in rows.slice(0, 8):
		print("   %-26s moved %7.2f mm, turned %6.2f°" % [row["name"], row["moved"], row["turned"]])


func _columns(t: Transform3D) -> Array:
	var b := t.basis
	return [b.x.x, b.x.y, b.x.z, 0.0,
			b.y.x, b.y.y, b.y.z, 0.0,
			b.z.x, b.z.y, b.z.z, 0.0,
			t.origin.x, t.origin.y, t.origin.z, 1.0]
