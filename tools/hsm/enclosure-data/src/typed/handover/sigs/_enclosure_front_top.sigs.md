# _enclosure_front_top: observed signatures (41 live compiled functions)

## _corner_numbers  (python _corner_numbers:11; compiled line 30)
- `shell`: NS
- `outer`: T(F,F,F,F,F,F)
- returns: D{surfaces:L[D{source_step_entity:I,degree:L[~],poles:L[~],weights:L[~],multiplicities:L[~],knots:L[~]}],scale_mm:F,frames:L[D{origin:T(~,~,~),x_sign:F}]}
- steps: enclosure

## _halfspace  (python _halfspace:36; compiled line 97)
- `graph`: R:_Graph
- `origin`: T(F,F,F)
- `normal`: T(F,F,F)
- `extent`: F
- returns: R:_Shape
- steps: enclosure

## _display_frame  (python _display_frame:47; compiled line 299)
- `shell`: NS
- `outer`: T(F,F,F,F,F,F)
- returns: D{rotation:T(T(F,F,F),T(F,F,F),T(F,F,F)),translation_mm:T(F,F,F)}
- steps: enclosure

## _display_exits  (python _display_exits:56; compiled line 428)
- `graph`: R:_Graph
- `wing`: NS
- `depth`: F
- `inset`: F
- `roof_drop`: F
- returns: L[R:_Shape]
- steps: enclosure

## _display_cut  (python _display_cut:68; compiled line 623)
- `shell`: NS
- `graph`: R:_Graph
- `outer`: T(F,F,F,F,F,F)
- `support_floor`: F
- `support_fore`: F
- `extend_wing_exits`: B
- returns: R:_Shape
- steps: enclosure

## _valve_body  (python _valve_body:97; compiled line 655)
- `shell`: NS
- `graph`: R:_Graph
- returns: R:_Shape
- steps: enclosure

## cylinder  (python _valve_body.<locals>.cylinder:100; compiled line 683)
- `radius`: F
- `z0`: F
- `z1`: F
- `x`: F
- `y`: F
- returns: R:_Shape
- steps: enclosure

## _teardrop  (python _teardrop:119; compiled line 1002)
- `graph`: R:_Graph
- `radius`: F
- `x`: F
- `z`: F
- `y0`: F
- `y1`: F
- `angle`: F
- returns: R:_Shape
- steps: enclosure

## _stacked_towers  (python _stacked_towers:130; compiled line 1178)
- `graph`: R:_Graph
- `stock`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## visit  (python _stacked_towers.<locals>.visit:135; compiled line 1182)
- `index`: I
- returns: N
- steps: enclosure

## _pump_inverse  (python _pump_inverse:177; compiled line 1232)
- `shell`: NS
- `graph`: R:_Graph
- `box`: R:Box
- returns: L[R:_Shape]
- steps: enclosure

## cone  (python _pump_inverse.<locals>.cone:190; compiled line 1244)
- `r0`: F
- `r1`: F
- `z0`: F
- `height`: F
- returns: R:_Shape
- steps: enclosure

## _box_points  (python _box_points:201; compiled line 1255)
- `bounds`: L[F] | T(F,F,F,F,F,F)
- returns: L[T(F,F,F)]
- steps: enclosure

## _diamond  (python _diamond:206; compiled line 1270)
- `x`: F
- `y`: F
- `z`: F
- `radius`: F
- returns: L[T(F,F,F)]
- steps: enclosure

## _corridor  (python _corridor:210; compiled line 1318)
- `shell`: NS
- `graph`: R:_Graph
- `clouds`: L[L[T(F,F,F)]]
- returns: T(R:_Shape,L[T(F,F,F)])
- steps: enclosure

## _pump_wires  (python _pump_wires:216; compiled line 1398)
- `shell`: NS
- `graph`: R:_Graph
- `box`: R:Box
- returns: L[T(R:_Shape,L[T(~,~,~)])]
- steps: enclosure

## _upper_wire_room  (python _upper_wire_room:248; compiled line 1440)
- `shell`: NS
- `graph`: R:_Graph
- `box`: R:Box
- `wire_rooms`: L[T(R:_Shape,L[T(~,~,~)])]
- returns: R:_Shape
- steps: enclosure

## _display_cleanouts  (python _display_cleanouts:267; compiled line 1739)
- `shell`: NS
- `graph`: R:_Graph
- `box`: R:Box
- returns: L[R:_Shape]
- steps: enclosure

## _leaves  (python _leaves:283; compiled line 1751)
- `shell`: NS
- `graph`: R:_Graph
- `box`: R:Box
- returns: NS
- steps: enclosure

## rounded  (python _leaves.<locals>.rounded:285; compiled line 1756)
- `w`: F
- `d`: F
- `r`: F
- `z0`: F
- `z1`: I
- `cx`: F
- `cy`: F
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1759)
- `depth`: F
- `inset`: F
- `roof_drop`: F
- returns: L[R:_Shape]
- steps: enclosure

## <lambda>  (python ?; compiled line 1761)
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1762)
- `length`: F
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1764)
- `plate`: R:dict
- returns: L[R:_Shape]
- steps: enclosure

## <lambda>  (python ?; compiled line 1766)
- `r`: F
- `x`: F
- `z`: F
- `y0`: F
- `y1`: F
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1768)
- `stock`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1770)
- `air`: F
- returns: R:_Shape
- steps: enclosure

## wires  (python _leaves.<locals>.wires:310; compiled line 1774)
- returns: L[T(R:_Shape,L[T(~,~,~)])]
- steps: enclosure

## <lambda>  (python ?; compiled line 1779)
- `e`: NS
- `box`: R:Box
- returns: L[R:_Shape]
- steps: enclosure

## <lambda>  (python ?; compiled line 1780)
- `e`: NS
- `box`: R:Box
- returns: L[R:_Shape]
- steps: enclosure

## <lambda>  (python ?; compiled line 1781)
- `e`: NS
- `box`: R:Box
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1782)
- `e`: NS
- `box`: R:Box
- returns: L[R:_Shape]
- steps: enclosure

## <lambda>  (python ?; compiled line 1784)
- `origin`: T(F,F,F)
- `normal`: T(F,F,F)
- `extent`: F
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1785)
- `outer`: T(F,F,F,F,F,F)
- `support_floor`: F
- `support_fore`: F
- `extend_wing_exits`: B
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1786)
- `shape`: R:_Shape
- `plane`: F
- `sign`: I
- `x`: F
- `z`: F
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1787)
- `face`: F
- `inside`: F
- `joint`: F
- `aft`: F
- `floor`: F
- `peak`: F
- returns: R:_Shape
- steps: enclosure

## _front_half  (python _front_half:333; compiled line 1793)
- `shell`: NS
- `graph`: R:_Graph
- `box`: R:Box
- `structure`: R:_Shape
- returns: R:_Shape
- steps: enclosure

## numbers  (python numbers:369; compiled line 1836)
- `shell`: NS
- `box`: R:Box
- `graph`: N
- returns: D{angle:F,outer:T(F,F,F,F,F,F),profile:D{end:T(F,F),foot:T(F,F),front_mid:T(F,F),normal:T(F,F,F),origin:T(F,F,F),roof:T(F,F),start:T(F,F),top_mid:T(F,F)},roof_fill_sections:T(T34[D{~:~}],T34[D{~:~}]),roof_transition:D{foot:F,height:F,outward_per_height:F},side_radius:F,standing_radius:F,color:T(F,F,F),panel:R:dict,panel_bounds:T(F,F,F,F,F,F),front_corners:D{surfaces:L[D{source_step_entity:~,degree:~,poles:~,weights:~,multiplicities:~,knots:~}],scale_mm:F,frames:L[D{origin:~,x_sign:~}]}}
- steps: enclosure

## print_numbers  (python print_numbers:384; compiled line 2060)
- `shell`: NS
- `box`: R:Box
- returns: D{S:D{across:F,along:F,margin:F,overrun:F,plan_tol:F,face_tol:F,pitch:F,width:F,depth:F,rise:F}|D{end:T(F,F),foot:T(F,F),front_mid:T(F,F),normal:T(F,F,F),origin:T(F,F,F),roof:T(F,F),start:T(F,F),top_mid:T(F,F)}|D{foot:F,height:F,outward_per_height:F}|D{front_panel_ymax_mm:F,field_reach_mm:F,rear_land_ymin_mm:F}|..}
- steps: enclosure

## <lambda>  (python ?; compiled line 2328)
- `s`: F
- returns: T(T(F,F),T(F,F))
- steps: enclosure

## cut  (python cut:417; compiled line 2441)
- `shell`: NS
- `box`: R:Box
- `directory`: P
- returns: R:dict
- steps: enclosure

