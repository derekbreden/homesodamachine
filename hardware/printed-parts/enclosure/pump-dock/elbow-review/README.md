# Purchased pump-dock elbows

Four purchased [John Guest PP0308E elbows](../../../../reference/jg-pp0308e-elbow/README.md) sit below the permanent TPU junctions. Each uses the native three-solid scanned exterior, with its fixed collar supported by an integral front-top U seat. A short gripped stub enters the lower TPU sealing land; a formed black LLDPE run connects the other elbow leg to its aft valve. The assembly contains four wet TPU junctions, three flat PET-GF keepers and four purchased elbows.

![Inner station and the assumed connector envelopes](elbow-layout.png)

The illustration highlights exact assembly meshes. The wall is hidden to show its integral seat. Orange boxes are assumed 8 × 5 × 21.5 mm female-connector envelopes, not measurements of the purchased terminals.

## Geometry and assembly

- [Native fit](native-fit.json): all four junctions, scanned elbows and dry seats are valid native geometry. Junctions and elbows have zero interfering volume with front-top. The inner junctions clear the coil bodies by about 1.91 mm; the outer elbows clear the condenser by about 1.44 mm. The assumed inner connector boxes clear the formed tubes by about 4.32 mm.
- [Factory approach](assembly-motion.json): each elbow clears its aft-open seat at the recorded 0, 1, 3, 6, 12 and 20 mm approach positions. Fit the connected fore-valve/junction/elbow groups before the aft valves. All three keepers clear the shell both seated and parked above the collar path; their plain U openings face down in service.
- [Collar contact](collar-contact.json): the fixed collars contact their seats within 0.2 mm motion along the stub axis. Together with 0.15 mm nominal stub stop room, the rigid geometry consumes less than the 0.5 mm total movement allowance. This is a geometric travel reading, not a loaded-stiffness or retention rating.
- [Shell scope](shell-scope.json): the native front-top has zero added or removed volume outside X ±105, Y 78–188, Z 130–230 mm. Roof, display and other shell geometry match the input part.
- [Aggregate refresh](aggregate-refresh.json): affected native members match their source geometry. Unrelated native bodies retain their geometry and colours; unrelated viewer arrays retain their fingerprints. The four formed tube solids stop at the known release faces. The [front-top service scene](scene-refresh.json) contains the same purchased elbows, junctions and tubing.

The standalone manifold generator reports zero volume clashes. Junction manufacturing exports lie on a broad aft web landing. The inlet/upper lands stand 45 degrees from vertical; lower lands stand 20 degrees (inner) or 45 degrees (outer). Keeper exports lie flat on their wall faces. The [current manufacturing instructions](../README.md#manufacture) define the seven printed pieces and the scope of archived print projects.

The [junction cavity reading](junction-cavity.json) records open socket axes, retained annular bearings, removed native fin witnesses and the flat print landing. The chamber stays within the web's 3 mm inset; circular seal lands remain intact.

## Tube preparation

Nominal short stubs are 23.05 mm. Each formed run uses R14 centerline bends, following the existing spool observation recorded in `_routing.STOCKS`. The elbow's nominal 15.7 mm insertion and valve's nominal 12 mm insertion are stock allowances; the scanned exterior establishes neither internal stop. Fully seated marks and the actual mounted span govern factory cuts and TPU engagement. See the [assembly sequence](../../../../assembly/internal-plumbing.md).

The known native clearances do not establish actual female-connector fit, printed sealing quality, support removal, pressure capacity or lifetime. Existing physical observations keep their recorded geometry and material scope. No print was launched for this review.
