# weldkit - scene authoring cheat sheet

Classic scripts only (`window.WK`, THREE r147). A scene page must work opened directly from `file://`: no modules, no fetch, no CDN.
Everything drawn is EXPLANATORY geometry (mm, +Z up, tube axis = Z, weld station on +X); the gun is a proxy, never measured.

## 1. Page contract
- File: `scenes/<id>/index.html` (+ assets beside it). `<id>` = `<explorer-code>-<slug>`, lowercase-hyphen. `00-*` is the coordinator's.
- `<head>`: `<link rel="stylesheet" href="../../kit/weldkit.css">` and the scene-meta block. End of `<body>`: `../../kit/vendor/three.min.js`, `../../kit/vendor/OrbitControls.js`, `../../kit/weldkit.js`, then your inline script.
- Links in a scene are relative to the page: index `../../index.html`, notes `../../explorers/<code>/ideas/x.md`, other scenes `../<id>/index.html`.
- `?thumb=1` shows the stage only (thumbnails). The kit sets `__sceneReady` after the first frame, `__sceneErrors`, `__controls`, `__setControl(id,v)`, `__resetAll()`; `tools/check-scene.mjs` uses them.
- Missing meta or sections never throw; empty sections are hidden. `WK.version` is the kit version.

### scene-meta (`<script type="application/json" id="scene-meta">`, shared with the index builder; WK.app reads it)
`id`, `title`, `by` (explorer name), `origin` (`derek-example|swarm|branch|combination|reference`), `summary`, `status` (`rough|developed|deep`, depth only, not a rank), `tags[]`, `branchOf[]`, `combines[]` (scene ids, shown as links), `transferable[]` (mechanisms others could borrow).
- `how`: `{motion, load, reference, observe, use}`, each <= 15 words. Shown under the title as Moves / Carries / Locates / Observed by / Used by.
- `software`: `{commands[], observes[], manual[]}` short strings, listed in the Software section (the live I/O panel is separate, `app.io`).
- `notes[]`, `sources[]`: relative paths to idea/exchange and sourcing `.md` files, rendered as links in Notes & sources.
- `WK.app({...})` options override meta. `sections:{proposes, carries, software, tried, unresolved, assumptions, sources}` are HTML strings (plain text is wrapped in `<p>`); `links:[{label,href}]`; `open:['proposes']` (sections open at start).

## 2. Complete minimal 3D example (a slide carrying a pointer across the joint; runs as-is)
```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Slide with pointer</title>
<link rel="stylesheet" href="../../kit/weldkit.css">
<script type="application/json" id="scene-meta">
{ "id": "xx-slide-pointer", "title": "Slide carrying a pointer", "by": "xx", "origin": "swarm", "status": "rough",
  "summary": "A small linear slide carries a pointer tip across the joint so reach and seam offset can be seen.",
  "tags": ["slide"], "how": { "motion": "one motor drives a carriage along a rail parallel to the seam tangent",
  "load": "rail on two posts to the bench", "reference": "rail height set by hand", "observe": "camera on a post sees the tip", "use": "dry run" } }
</script>
</head>
<body>
<script src="../../kit/vendor/three.min.js"></script>
<script src="../../kit/vendor/OrbitControls.js"></script>
<script src="../../kit/weldkit.js"></script>
<script>
const V = (x, y, z) => new THREE.Vector3(x, y, z), P = WK.prim, J = WK.JOINT;
const app = WK.app({ gun: false, sections: { proposes: '<p>A carriage on a rail parallel to the seam tangent carries a pointer.</p>',
  unresolved: '<p>How the rail is aligned to the tangent is not shown.</p>' } });
const ws = app.workstation, railZ = J.z + 60;
const rail = P.rail(V(J.x, -110, railZ), V(J.x, 110, railZ), { width: 14, role: 'fixed' });
const carriage = P.carriage([22, 30, 16], 'actuated', { rail: rail, t: 0.5 });
const pointer = P.rod(V(0, 0, 0), V(0, 0, 1), 2, 'locate'), tip = P.sphere(3, 'laser');
[-110, 110].forEach(y => app.add(P.rod(V(J.x, y, ws.benchZ), V(J.x, y, railZ - 4), 5, 'fixed')));
[rail, carriage, pointer, tip, P.rod(V(-40, 190, ws.benchZ), V(-40, 190, 255), 4, 'fixed')].forEach(o => app.add(o));
const tipObj = { dotOffset: () => ws.offsetOf(tip.position), beamDir: () => V(0, 0, -1) };   // anything with these two methods
app.cornerInset({ gun: tipObj });
app.inset.add({ id: 'post', label: 'Camera on a post (proposed)', position: V(-40, 190, 260), target: tip, fov: 35 });
app.label(tip, 'pointer tip', { cls: 'laser' });

function update(t, len) {
  carriage.setT(t);
  const c = carriage.position, end = V(c.x, c.y, railZ - len);
  pointer.setEnds(V(c.x, c.y, railZ + 6), end); tip.position.copy(end);
  const off = tipObj.dotOffset(), seen = app.inset.markVisibility('post', end, { ignore: [pointer, tip] });
  app.io.set({ commands: [{ name: 'Carriage', value: t.toFixed(2), unit: 't' }],
    observes: [{ name: 'Tip visible to post camera', value: seen.visible ? 'yes' : 'no', status: seen.visible ? 'seen' : 'blind' },
               { name: 'Tip vs seam (r, z)', value: off.radial.toFixed(1) + ', ' + off.vertical.toFixed(1), unit: 'mm', status: 'partly', note: 'exact here; a sensor would estimate it' }] });
  app.badge('reach', off.total > 25 ? 'tip is ' + off.total.toFixed(0) + ' mm from the seam' : null, 'warn');
}
app.ui.slider({ id: 'pos', label: 'Carriage position', min: 0, max: 1, step: 0.01, value: 0.5, kind: 'actuator', visual: () => carriage, onChange: v => update(v, app.ui.get('len')) });
app.ui.slider({ id: 'len', label: 'Pointer length', min: 40, max: 90, step: 1, value: 60, unit: 'mm', kind: 'scene', visual: () => pointer, onChange: v => update(app.ui.get('pos'), v) });
</script>
</body>
</html>
```
WK.app builds the page, the 3D stage, the rotator/tube/endcap (`workstation`) and, unless `gun:false`, the gun. Every control's `onChange(initial)` runs once before the first frame, so create objects first or in the same script.

## 3. r147 gotchas
- Colours: r147 colour management is legacy. Build material colours with `WK.color(hex)` or use `WK.mat(role)`; a raw `new THREE.Color(hex)` looks washed out. Output is `renderer.outputEncoding = THREE.sRGBEncoding` (no `outputColorSpace`).
- Shared materials: `WK.mat(role,{shade,opacity})` is cached; never mutate it. Recolour with `WK.setRole(obj, role)`.
- `camera.up.set(0,0,1)` must precede `new OrbitControls` (the kit does this). Do not call `renderer.render`; call `app.invalidate()`.
- `Object3D.lookAt` aims +Z for meshes but -Z for cameras. Use `prim.camera().aimAt(p)`; camera bodies look along -Z, +Y up.
- Geometry axes: Cylinder is Y (prims fix it: `cyl` default axis Z), Torus lies in XY, Plane normal +Z.
- `LatheGeometry` / `CylinderGeometry` partial sweeps: once `rotateX(pi/2)` puts the axis on Z, `phiStart` / `thetaStart` 0 points along -Y, so an angle `a` from +X needs `a + pi/2`.
- `prim.cyl` bakes its axis into the geometry: scale a `cyl` mesh's radius on x,y (axis `'z'`), y,z (`'x'`) or x,z (`'y'`), never along its axis.
- `WK.JOINT`, `GRIP_BASE_LOCAL`, `LOCAL_ROLL_AXIS` are frozen: `.clone()` first. Mutating throws (on purpose).
- Helper layer: `app.addHelper(obj)` puts obj (and children present NOW) on layer 1: visible in the main view only, ignored by insets and raycasts.
- Transparent parts do not write depth (sorting artefacts are expected). Meshes raycast by their `material.side`.
- Render is on demand. Controls invalidate for you; if something animates, `app.onFrame(fn)` (return `false` when idle) or `app.animate(true)`.

## 4. Roles, colours, control kinds
Colour parts by ROLE (`WK.ROLE`): `fixed` slate, `load` amber (carries load), `locate` teal (reference), `actuated` purple (moved by an actuator software could command), `compliant` green (free/springy), `sensor` blue, `gun` dark steel, `work` light steel, `cable`, `wire` gold, `laser` red, `ghost` translucent grey. The legend lists the roles actually used. Consistent colour is how a reader tells fixed from carrying from locating from actuated from compliant.
Control `kind`: `'actuator'` (a proposed motor/axis; purple, gear badge), `'scene'` (edits the explanatory scene, e.g. where a support is placed; pencil), `'state'` (setup/operating/welding mode; clock), `'branch'` (compare variants), `'view'`. Sliders are `scene` by default, toggles `state`, radios/selects `branch`. Never label a scene edit as an actuator. `visual:` (Object3D | array | fn) makes the affected part glow on hover; a string is shown as "watch: ...".
`noVisual:true` (or `visual:false`) on a control says it is not expected to change the stage: a readout, an animation speed, an effect that depends on another control's state. The checker still drives it for errors but does not warn "no visible effect". `app.ui.enable(id,false)` greys a control out; the checker skips its warning too (it looks at the state when it reaches the control).

## 5. Observers, line of sight, seam offset (be honest)
- `app.inset.add({id,label,position|object3D,target,fov,size,corner})` renders a sensor view in a corner and draws its frustum in the main view. `target` may be a point, Object3D or function; `position` may be a function. Up: a camera carried by an `object3D` rolls with it (its +Y, read every frame; `upFromObject:false` opts out); otherwise `up` (Vector3 | fn, default +Z). `inset.setPose(pos, target, up?)` moves a free camera and may change `up`.
- `app.inset.markVisibility(id, point, {ignore:[parts that carry the target], eps})` colours the frame green / red (blocked) / amber (outside FOV) and returns `{visible, inFov, blocked, hitObject}`. It is DRAWN-SCENE geometry, not a measurement: no optics, lighting or fume. Say so in the scene, list what the sensor cannot see as `blind` in `app.io`.
- `eps` (mm, default 0.8; also `WK.lineOfSight`): the last `eps` mm of the ray at the TARGET end are not tested, so a target that sits ON a surface is not blocked by that surface. Keep it below the 1.65 mm wall: a larger value lets a dot behind the wall look visible from outside. A dot or the corner is ON the wall/plate, so for those pass a point nudged 0.3-0.5 mm toward the observer (inside the recess for a camera above the tube), not a larger `eps`. Grazing rays at the curved wall can still clip a facet; nudge the point rather than widening `eps`. A point on the axis of a thin part, such as `gun.local('nozzleTip')`, is hidden behind that part's own surface when seen from the side: pass `eps: 3` (about the part's radius) for such a point.
- `gun.beamSurfacePoint()` / `WK.beamSurfacePoint(origin, dir)` -> `{point, viewPoint, normal, object, part:'tube'|'cap', distance}` or `null`: the first drawn surface (tube, cap) the beam lands on, unlike the dot, which is a point in space. Test `viewPoint` (0.3 mm off the surface, toward the gun) with `markVisibility` to ask "can this camera see the spot".
- `WK.occluders(app,{ignore})` lists solid visible meshes; a mesh or group with `userData.occludes=false` never blocks (children too). `prim.camera` sets it, so a camera you add does not block its own view.
- `app.cornerInset({gun})` shows the exact dot-vs-seam cross-section ("scene geometry, not a sensor reading"); `.setEstimate({radial,vertical}|null)` draws what a proposed sensor would report; `.addMarker(id,{radial,vertical,label,role})` / `.removeMarker(id)` draw extra points (a sweep of spots, a probe stylus); `.setBeam(dir|null)` overrides the drawn beam direction. `gun` may be any object with `dotOffset()` and `beamDir()`.
- `ws.offsetOf(point)` / `WK.seamOffset(point)` -> `{radial, along, vertical, total, joint}`: radial + = into the wall, along = arc length from the +X station, vertical + = above the plate. It follows the seam circle (a straight slide parallel to the tangent leaves the seam), the illustrative runout and the work pose. Without a `seam` argument `WK.seamOffset` uses the page's workstation (`WK.workstation`).
- Work that MOVES (a stage under the rotator, a tilted rotator): `ws.setWorkPose(position, quaternion, {about})` moves rotator, turntable, tube and cap as one rigid body (bench and grid stay; pose is relative to `ws.group`; `about` = pivot for the rotation); `ws.workPose()` reads it back. `ws.offsetOf`, `ws.seam()`, `ws.jointNow()` (the work's +X station), `gun.dotOffset()` and `WK.seamOffset` all use the pose, spin and runout, so do not invert `tubeGroup.matrixWorld` yourself.

## 5b. Custom stage, panels, overlays
`WK.app({stage:'custom', minWidth: 820})`: `app.stageEl` is an empty scrolling area for your SVG / DOM; below `minWidth` px it scrolls sideways instead of shrinking the drawing. Badges are a strip above it and the legend a strip below it, so neither covers the drawing. `app.onFrame(fn(dt,t))` runs your simulation on both stage types (custom stages have nothing to render; the return value is ignored there).
```js
const svgEl = WK.svg('svg', { viewBox: '0 0 200 100', width: '100%' });                          // your own drawing
const p = app.ui.panel({ id: 'trace', title: 'Trace', open: true, node: svgEl });                 // card in the controls column; p = its body, p.card = the card
const hud = app.stageOverlay('<b>err</b> -', { corner: 'tr' });                                   // HUD card on the stage (3D: stacks with the insets); hud.remove() drops it
app.legend([{ role: 'sensor', label: 'proposed camera' }, { color: '#f59e0b', label: 'spot' }]);   // your legend, kept until app.legend(null)
app.onFrame(function (dt) { hud.innerHTML = '<b>err</b> ' + errMm(dt).toFixed(2) + ' mm'; });     // your simulation: same call on 3D and custom stages
app.ui.slider({ id: 'rate', label: 'Sim speed', min: 0.1, max: 4, step: 0.1, value: 1, kind: 'view', noVisual: true, onChange: v => { speed = v; } });   // a rate, not a picture: no checker warning
```

## 6. Rigid links: stop and say so, never stretch
Do not stretch a rigid link or move a fixed anchor to make an animation work. Compute, and when a link cannot follow, hold the last valid pose and show a badge:
```js
const r = WK.kin.twoLinkIK(shoulder, target, L1, L2, {bend:[0,0,1]});   // never stretches
link1.setEnds(shoulder, r.elbow); link2.setEnds(r.elbow, r.end);       // r.end = target only when r.ok
app.badge('reach', r.ok ? null : 'target out of reach by ' + r.over.toFixed(0) + ' mm', 'limit');
```
`WK.kin.clampLength(p0,p1,L)` (p1 stops at L from p0), `projectToLength(p0,target,L)` (exact-length rod swinging about p0), `attachAtOffset(obj, localPoint, worldPoint)` (translate so a local point lands on a world point; returns the residual). For a cable use `WK.curveMinRadius` + `WK.cableBadge`: the manual's 350 mm (emitting) / 240 mm (stored) minimum bend radii are manufacturer values, the badge is an illustrative check on the drawn curve. Bend radius of a Bezier is set by its handles: `stiffness` is handle / chord, not "wider = bigger radius" (a quarter turn is widest near 0.4); `stiffness:'auto'` picks the best. `curveMinRadius(pts, {detail:true})` says where the tightest bend is.

## 7. Anti-patterns
- Colouring by taste instead of role; an unbadged or mis-badged control (scene edit shown as actuator).
- Silently stretching links, moving fixed anchors, or letting parts pass through each other. Show a `limit` badge instead.
- Presenting scene-perfect knowledge as a sensor reading; using the corner inset or `dotOffset` as the "measurement".
- Presenting proxy gun geometry, pitch, clearance, runout numbers or made-up sensor error as measured. Put them under Assumptions.
- Your own `requestAnimationFrame` loop or `renderer.render` calls; ES modules, fetch, CDN scripts (they break `file://`).
- Building parts with raw `THREE.Color(hex)` or mutating shared materials; leaving controls with no visible effect (the checker warns).
- Hiding a serious problem to keep an idea alive, or using it as a reason to drop the idea: record it under Tried / Unresolved.

## 8. Public API (one line each)
**World constants and maths**
- `WK.DIM` tube / cap / port / gun dimensions (mm); `WK.INNER_RADIUS` 61.85; `WK.CAP_TOP` 146.05; `WK.PITCH`; `WK.CLEARANCE` 16.
- `WK.JOINT` Vector3 (frozen); `WK.GRIP_BASE_LOCAL`, `WK.WIRE_TIP_LOCAL`, `WK.LOCAL_ROLL_AXIS` (frozen local-frame points).
- `WK.OPENING` roll 45 / hole dial 30 / vertical -15: the reference scene's opening pose, illustrative. `WK.RIG` documented rotator numbers. `WK.CABLE` 350 / 240 mm.
- `WK.posePoint(p, roll, holeRoll, vertical)` port of pose.js (holeRoll = dial - 35).
- `WK.dialsToPose(roll, holeDial, vertical)` -> `{position, quaternion}` of the gun group (same as `updatePose` in the site scene).
- `WK.seamOffset(p, seam?)` -> `{radial, along, vertical, total, joint}` (see section 5); `WK.NOMINAL_SEAM` the ideal seam; `WK.workstation` the page's workstation.
**Roles and materials**
- `WK.ROLE`, `WK.role(name)`, `WK.roleHex(name)`: the palette, canonical role name (aliases accepted), CSS hex.
- `WK.color(hex)` linear colour for r147; `WK.mat(role,{shade,opacity,side:'double',flat,basic})`; `WK.lineMat(role,{dashed,dash,gap,opacity,onTop})`.
- `WK.setRole(obj, role)` recolour (e.g. a link that locks); `WK.highlight(objs, on)` hover glow.
**Workstation** `WK.addWorkstation(app,{rotator,bench,tube,cap,benchZ,ghostTube,benchSize,benchCenter,grid,indexDeg})` (automatic with `workstation:true|{options}`)
- Returns `ws` with `tube`, `cap`, `turntable`, `tubeGroup`, `bench`, `benchZ`, `parts`. Layout of the rotator's towers is a proxy from documented dimensions.
- `ws.setSpin(deg)`; `ws.spinAngle`; `ws.spin = {on, speedDegPerSec}` (default 7.4 deg/s = 8 mm/s bead travel at the weld radius).
- `ws.setWorkPose(position, quaternion, {about})` / `ws.workPose()` move rotator + turntable + tube + cap as one rigid body (`ws.work` is the group; bench and grid stay); identity by default.
- `ws.setRunout(radialTIR, faceTIR, exaggeration)` illustrative wobble (rig-doc limits 0.25 / 0.30 mm; exaggeration 1..40 makes it visible; 0,0 turns it off).
- `ws.setGhost(bool)` see-through tube and cap; `ws.seam()`, `ws.offsetOf(p)`, `ws.jointNow()` current seam including work pose, spin and runout.
**Gun** `WK.addGun(app,{shell,umbilical,wire,dotMarker,pose:'opening'|'none'|{roll,holeDial,vertical}})` (automatic with `gun:true|{options}`)
- `gun.group` local frame: origin nozzle tip, +Z toward the back, -Y grip side, dot at (0,0,-16). Proxy geometry, not measured.
- `gun.anchors`, `gun.anchor(name)`, `gun.anchorNames()`: `nozzleTip dot barrelMid collar housingTop housingBack gripTop gripMid gripBase cableExit cablePair umbilicalMid wireGuide wireGuideEnd wireBracket trigger`.
- `gun.setDials(roll, holeDial, vertical)` the three ideal rotations; `gun.setTransform(position, quaternion)` free 6-DoF placement; `gun.dials`.
- `gun.local(nameOrPoint)` -> world point; `gun.dotWorld()`; `gun.dir(localDir)`; `gun.beamDir()`; `gun.frame()` -> `{origin,x,y,z,beamDir,dot}`.
- `gun.dotOffset()` -> `{radial, along, vertical, total, joint}` exact scene geometry; `gun.cableExit()` / `gun.wireExit()` -> `{point, dir}` (world) for routing cables.
- `gun.umbilical`, `gun.wire` (groups; hide with `.visible=false`); `gun.setLaser(bool, {sweepMm:2, offsetMm:0})` beam, fan and sweep against the drawn tube/cap (sweep along the gun's local X, centred `offsetMm` from the dot; options persist).
- `gun.beamSurfacePoint(opts?)` first tube/cap surface the beam lands on (see section 5); `WK.beamSurfacePoint(origin, dir, {targets,lift,maxDistance})` the same for any ray.
- `gun.addShell({style:'sleeve'|'frame', from, to, clearance, role, opacity})` printed-sleeve proxy over the zones nozzle < barrel < housing < grip between two anchors.
- `shell.attachPoint(nameOrPoint,{side:'top|grip|left|right|back|front'|[x,y,z], role, size})` -> `{lug, local, normal, world()}`: a lug marker anywhere on the shell.
- `gun.addRing(nameOrPoint,{radius,tube,openGap,axis,role})` open-able loop around the gun that follows it; `ring.setCenter(p)`. (`WK.prim.ring` is the free-standing version.)
**App** `WK.app({title,by,origin,summary,how,software,sections,links,notes,sources,open,view,views,viewButtons,fov,stage,minWidth,workstation,gun})`
- Fields: `app.scene`, `camera`, `renderer`, `controls`, `workstation`, `gun`, `stageEl` (custom stage: the scrolling content), `stageFrame`, `ui`, `io`, `inset`, `cornerInset`.
- `app.add(obj, role?)`; `app.addHelper(obj)` main-view-only layer; `app.frameObject(obj)`; `app.setView(name | {target, position|dir, dist})`; `app.getView()`.
- `app.onFrame(fn(dt,t))` returns an unsubscribe (return `false` when idle); `app.onReady(fn)`; `app.animate(bool)`; `app.invalidate()`; `app.render()`.
- `app.label(pointOrObject3D|fn, text, {cls: role, local})` -> `{set, show, remove}` DOM leader label, hidden off-screen or under an inset, de-overlapped.
- `app.badge(id, text|null, 'ok'|'warn'|'limit'|'info')` stage badge (limit = red); `app.toast(text)`; `app.legend()` re-scan roles, `app.legend([{role|color,label}])` your entries (kept until `app.legend(null)`).
- `app.stageOverlay(nodeOrHtml, {corner:'tl|tr|bl|br', w})` HUD card on either stage, returns the element (`.remove()`).
**UI** (`kind`: `actuator|scene|state|branch|view`; every control is in `__controls` and settable through `__setControl`)
- `app.ui.slider({id,label,min,max,step,value,unit,kind,help,visual,noVisual,format,onChange(v)})`; `.toggle({... onChange(bool)})`. `noVisual:true` / `visual:false`: the checker does not expect a visible effect.
- `.select` / `.radio({id,label,options:[v|{value,label,help}],value,kind,onChange})`; `.button({id,label,kind,onClick})`.
- `.readout(id,label)` -> `set(text|number, unit)`; `.group(title,{help,open})` returns the same API scoped to a group.
- `app.ui.get(id)`, `.set(id,v,{silent})`, `.enable(id,bool)`, `.reset()`. "Reset all", "Reset view" and the badge legend are automatic.
- `app.ui.panel({id,title,node|html,open})` -> body element of a card in the controls column (`.card` = the card).
**I/O panel**
- `app.io.set({commands:[{name,value,unit,note}], observes:[{name,value,unit,status,note}], manual:[text]})` status = `seen|partly|blind|manual|unresolved`; cheap to call every frame.
- `app.io.manual(text|[text])` the steps that stay manual.
**Observers**
- `app.inset.add({id,label,object3D|position,target,fov,near,far,size:[w,h],corner:'br|bl|tr|tl',frustum,noise,up,upFromObject})` -> `{camera, setPose(pos,target,up?), setFov, setLabel, remove}`; click an inset to enlarge it.
- `app.inset.markVisibility(id, point, {ignore, occluders, eps=0.8})` -> `{visible, inFov, blocked, hitObject}`; `app.inset.get/remove/list`.
- `WK.lineOfSight(from, to, occluders[], {eps=0.8})` -> `{visible, hitObject, hitDistance}`; `WK.occluders(app,{ignore})` solid visible meshes (`userData.occludes=false` opts out).
- `app.cornerInset({gun, corner})`; `.setEstimate({radial,vertical}|null)`, `.addMarker(id,{radial,vertical,label,role})`, `.removeMarker(id)`, `.setBeam(dir|null)`.
**Primitives** `WK.prim.*` (all set `userData.role`; setEnds-style methods keep lengths rigid)
- `box(w,d,h,role)`, `cyl(r,h,role,{axis})`, `sphere(r,role)`, `plane(w,h,role)`, `pulley(r,w,role)`, `magnet(size,role)`, `groundHatch(size,role)`, `axes(size)`.
- `rod(p0,p1,r,role)`, `rail(p0,p1,{width,height,role})` with `.setEnds(p0,p1)`; `carriage([w,l,h],role,{rail,t})` with `.setT(t)` / `.onRail(rail,t)`.
- `motor(size,role)` shaft +Z, body -Z, origin at the mounting face; `ring(radius,tube,{openGap,gapDeg,axis,role})` in the XY plane.
- `spring(p0,p1,{coils,radius,wire,role})`, `elastic(p0,p1,{role,radius,rest})` (thins as it stretches), both `.setEnds`; elastic `.strain()`.
- `cable(points|curve,{radius,role})` `.setPoints`, `.minRadius()`; `arrow(origin,dir,len,role)` `.set`; `dashed(points,role,{dash,gap})` `.setPoints`.
- `camera({role,fov,size})` body looks along -Z, `.aimAt(target, up)`, never occludes; `frustum({fov,aspect,near,far,role})` `.set({...})`.
**Kinematics and cables**
- `WK.kin.twoLinkIK(base, target, L1, L2, {bend})` -> `{ok, limited:'far|near'|null, over, end, elbow, reach, angles}`; `WK.kin.clampLength(p0,p1,L)`; `WK.kin.projectToLength(p0,target,L)`; `WK.kin.attachAtOffset(obj, localPoint, worldPoint)`.
- `WK.curveMinRadius(curveOrPoints,{samples,detail})` smallest radius (mm; dense points are measured as given, coarse ones smoothed first); `WK.cableBadge(minR)` -> `{level,text}` vs the manual's 350 / 240 mm (illustrative); `WK.bezierCable(p0,dir0,p1,dir1,{stiffness|'auto'})` -> Bezier curve with `.minRadius()`, `.stiffness`.
**Custom stage and DOM** `WK.app({stage:'custom', minWidth})` same chrome and controls with an empty scrolling `app.stageEl` for SVG/canvas (section 5b); `WK.svg(tag,attrs,...kids)`; `WK.h(tag,attrs,...kids)`; `WK.esc(text)`.

## 9. Check your scene
`node tools/check-scene.mjs <id>... [--all] [--shot] [--exercise] [--page] [--size=1280x800]` (own headless Chrome per run, safe to run in parallel). `--shot` writes `thumbs/<id>.png`; `--exercise` drives every control and warns about ones with no visible effect (disabled controls and `noVisual` controls are skipped; custom panels count as output); check `--size=390x844 --page` once for phones. Exit 1 only for exceptions, missing ready, blank canvas or failed loads. Look at the PNGs.
