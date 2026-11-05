# fixed_returns: observed signatures (15 live compiled functions)

## _add  (python _add:51; compiled line 184)
- `a`: T(F,F,F)
- `b`: T(F,F,F)
- returns: T(F,F,F)
- steps: acceptance-and-burn-in-sync, bom-masses, enclosure, enclosure-assembly, enclosure-box, firmware-and-commissioning-sync, fluid-topology-sync, internal-plumbing-sync …

## _scale  (python _scale:55; compiled line 238)
- `a`: T(F,F,F)
- `k`: F
- returns: T(F,F,F)
- steps: acceptance-and-burn-in-sync, bom-masses, enclosure, enclosure-assembly, enclosure-box, firmware-and-commissioning-sync, fluid-topology-sync, internal-plumbing-sync …

## _unit  (python _unit:59; compiled line 273)
- `v`: T(F,F,F)
- returns: T(F,F,F)
- steps: acceptance-and-burn-in-sync, bom-masses, enclosure, enclosure-assembly, enclosure-box, firmware-and-commissioning-sync, fluid-topology-sync, internal-plumbing-sync …

## _line  (python _line:64; compiled line 340)
- `start`: T(F,F,F)
- `direction`: T(F,F,F)
- `length`: F
- returns: D{kind:S,start_mm:T(F,F,F),end_mm:T(F,F,F),start_tangent:T(F,F,F),end_tangent:T(F,F,F),length_mm:F}
- steps: acceptance-and-burn-in-sync, bom-masses, enclosure, enclosure-assembly, enclosure-box, firmware-and-commissioning-sync, fluid-topology-sync, internal-plumbing-sync …

## plate_aft_y  (python plate_aft_y:71; compiled line 436)
- `fore_y`: F
- returns: F
- steps: acceptance-and-burn-in-sync, bom-masses, enclosure, enclosure-assembly, enclosure-box, firmware-and-commissioning-sync, fluid-topology-sync, internal-plumbing-sync …

## tee_axis_y  (python tee_axis_y:76; compiled line 449)
- `fore_y`: F
- returns: F
- steps: acceptance-and-burn-in-sync, bom-masses, enclosure, enclosure-assembly, enclosure-box, firmware-and-commissioning-sync, fluid-topology-sync, internal-plumbing-sync …

## fore_valve_axis_y  (python fore_valve_axis_y:81; compiled line 478)
- `fore_y`: F
- returns: F
- steps: acceptance-and-burn-in-sync, bom-masses, enclosure-assembly, enclosure-box, firmware-and-commissioning-sync, fluid-topology-sync, internal-plumbing-sync, manifold-layout

## tip_y  (python tip_y:86; compiled line 503)
- `fore_y`: F
- returns: F
- steps: enclosure, enclosure-assembly, enclosure-box

## tee_ports  (python tee_ports:91; compiled line 520)
- `fore_y`: F
- `x`: F
- `z`: F
- returns: D{centre:T(F,F,F),branch:D{point:T(F,F,F),axis:T(F,F,F)},upper:D{point:T(F,F,F),axis:T(F,F,F)},lower:D{point:T(F,F,F),axis:T(F,F,F)}}
- steps: acceptance-and-burn-in-sync, bom-masses, enclosure, enclosure-assembly, enclosure-box, firmware-and-commissioning-sync, fluid-topology-sync, internal-plumbing-sync …

## elbow_return  (python elbow_return:100; compiled line 623)
- `start`: T(F,F,F)
- `end`: T(F,F,F)
- returns: D{elbows:T(D{crossing:T(~,~,~),socket:T(~,~,~),stem:F,showing:F},D{crossing:T(~,~,~),socket:T(~,~,~),stem:F,showing:F}),tube:T(D{kind:S,start_mm:T(~,~,~),midpoint_mm:T(~,~,~),end_mm:T(~,~,~),radius_mm:F,sweep_degrees:F,start_tangent:T(~,~,~),end_tangent:T(~,~,~),length_mm:F},D{kind:S,start_mm:T(~,~,~),midpoint_mm:T(~,~,~),end_mm:T(~,~,~),radius_mm:F,sweep_degrees:F,start_tangent:T(~,~,~),end_tangent:T(~,~,~),length_mm:F}),exposed_mm:F,cut_mm:F,floor_z:F}
- steps: enclosure, enclosure-assembly, enclosure-box, fluid-topology-sync, internal-plumbing-sync, manifold-layout

## s_bend  (python s_bend:140; compiled line 989)
- `start`: T(F,F,F)
- `end`: T(F,F,F)
- `direction`: T(F,F,F)
- returns: T(D{kind:S,start_mm:T(F,F,F),end_mm:T(F,F,F),start_tangent:T(F,F,F),end_tangent:T(F,F,F),length_mm:F}) | T(D{kind:S,start_mm:T(F,F,F),midpoint_mm:T(F,F,F),end_mm:T(F,F,F),radius_mm:F,sweep_degrees:F,start_tangent:T(F,F,F),end_tangent:T(F,F,F),length_mm:F},D{kind:S,start_mm:T(F,F,F),midpoint_mm:T(F,F,F),end_mm:T(F,F,F),radius_mm:F,sweep_degrees:F,start_tangent:T(F,F,F),end_tangent:T(F,F,F),length_mm:F})
- steps: acceptance-and-burn-in-sync, bom-masses, enclosure, enclosure-assembly, enclosure-box, firmware-and-commissioning-sync, fluid-topology-sync, internal-plumbing-sync …

## at  (python s_bend.<locals>.at:154; compiled line 1002)
- `phi`: F
- returns: T(F,F,F)
- steps: enclosure, enclosure-assembly, enclosure-box, fluid-topology-sync, internal-plumbing-sync, manifold-layout

## <lambda>  (python ?; compiled line 1007)
- `p`: T(F,F,F)
- returns: T(F,F,F)
- steps: enclosure, enclosure-assembly, enclosure-box, fluid-topology-sync, internal-plumbing-sync, manifold-layout

## station  (python station:169; compiled line 1025)
- `fore_y`: F
- `x`: F
- `z`: F
- `upper_port`: R:dict
- `return_port`: R:dict
- returns: D{tee:D{centre:T(F,F,F),branch:D{point:T(~,~,~),axis:T(~,~,~)},upper:D{point:T(~,~,~),axis:T(~,~,~)},lower:D{point:T(~,~,~),axis:T(~,~,~)}},upper_target:D{axis:T(F,F,F),point:T(F,F,F),valve:S},return_target:D{axis:T(F,F,F),point:T(F,F,F),valve:S},upper_tube:T(D{kind:S,start_mm:T(~,~,~),end_mm:T(~,~,~),start_tangent:T(~,~,~),end_tangent:T(~,~,~),length_mm:F}),return:D{elbows:T(D{crossing:~,socket:~,stem:~,showing:~},D{crossing:~,socket:~,stem:~,showing:~}),tube:T(D{kind:~,start_mm:~,midpoint_mm:~,end_mm:~,radius_mm:~,sweep_degrees:~,start_tangent:~,end_tangent:~,length_mm:~},D{kind:~,start_mm:~,midpoint_mm:~,end_mm:~,radius_mm:~,sweep_degrees:~,start_tangent:~,end_tangent:~,length_mm:~}),exposed_mm:F,cut_mm:F,floor_z:F},upper_exposed_mm:F} | D{tee:D{centre:T(F,F,F),branch:D{point:T(~,~,~),axis:T(~,~,~)},upper:D{point:T(~,~,~),axis:T(~,~,~)},lower:D{point:T(~,~,~),axis:T(~,~,~)}},upper_target:D{point:T(F,F,F),axis:T(F,F,F)},return_target:D{point:T(F,F,F),axis:T(F,F,F)},upper_tube:T(D{kind:S,start_mm:T(~,~,~),end_mm:T(~,~,~),start_tangent:T(~,~,~),end_tangent:T(~,~,~),length_mm:F}),return:D{elbows:T(D{crossing:~,socket:~,stem:~,showing:~},D{crossing:~,socket:~,stem:~,showing:~}),tube:T(D{kind:~,start_mm:~,midpoint_mm:~,end_mm:~,radius_mm:~,sweep_degrees:~,start_tangent:~,end_tangent:~,length_mm:~},D{kind:~,start_mm:~,midpoint_mm:~,end_mm:~,radius_mm:~,sweep_degrees:~,start_tangent:~,end_tangent:~,length_mm:~}),exposed_mm:F,cut_mm:F,floor_z:F},upper_exposed_mm:F}
- steps: enclosure, enclosure-assembly, enclosure-box, fluid-topology-sync, internal-plumbing-sync, manifold-layout

## layouts  (python layouts:179; compiled line 1166)
- `plate`: R:dict
- returns: D{-82.1:D{tee:D{centre:T(~,~,~),branch:D{point:~,axis:~},upper:D{point:~,axis:~},lower:D{point:~,axis:~}},upper_target:D{axis:T(~,~,~),point:T(~,~,~),valve:S},return_target:D{axis:T(~,~,~),point:T(~,~,~),valve:S},upper_tube:T(D{kind:~,start_mm:~,end_mm:~,start_tangent:~,end_tangent:~,length_mm:~}),return:D{elbows:T(~,~),tube:T(~,~),exposed_mm:F,cut_mm:F,floor_z:F},upper_exposed_mm:F},-22.35:D{tee:D{centre:T(~,~,~),branch:D{point:~,axis:~},upper:D{point:~,axis:~},lower:D{point:~,axis:~}},upper_target:D{axis:T(~,~,~),point:T(~,~,~),valve:S},return_target:D{axis:T(~,~,~),point:T(~,~,~),valve:S},upper_tube:T(D{kind:~,start_mm:~,end_mm:~,start_tangent:~,end_tangent:~,length_mm:~}),return:D{elbows:T(~,~),tube:T(~,~),exposed_mm:F,cut_mm:F,floor_z:F},upper_exposed_mm:F},22.35:D{tee:D{centre:T(~,~,~),branch:D{point:~,axis:~},upper:D{point:~,axis:~},lower:D{point:~,axis:~}},upper_target:D{axis:T(~,~,~),point:T(~,~,~),valve:S},return_target:D{axis:T(~,~,~),point:T(~,~,~),valve:S},upper_tube:T(D{kind:~,start_mm:~,end_mm:~,start_tangent:~,end_tangent:~,length_mm:~}),return:D{elbows:T(~,~),tube:T(~,~),exposed_mm:F,cut_mm:F,floor_z:F},upper_exposed_mm:F},82.1:D{tee:D{centre:T(~,~,~),branch:D{point:~,axis:~},upper:D{point:~,axis:~},lower:D{point:~,axis:~}},upper_target:D{axis:T(~,~,~),point:T(~,~,~),valve:S},return_target:D{axis:T(~,~,~),point:T(~,~,~),valve:S},upper_tube:T(D{kind:~,start_mm:~,end_mm:~,start_tangent:~,end_tangent:~,length_mm:~}),return:D{elbows:T(~,~),tube:T(~,~),exposed_mm:F,cut_mm:F,floor_z:F},upper_exposed_mm:F}}
- steps: enclosure, enclosure-assembly

