# _enclosure_back_top: observed signatures (56 live compiled functions)

## _replace  (python _replace:11; compiled line 26)
- `module`: NS | R:Surface | R:module
- `replacements`: D{_flank_vents:Fn} | D{_funnel_plumb:Fn,_funnel_keepout:Fn,_rect_cut_y:Fn,_rect_cut_x:Fn} | D{_halfspace:Fn,_display_cuts:Fn,_valve_tray_placed:Fn,_z_rail_crossing:Fn} | D{apply:Fn,receiver_field:Fn} | D{apply:Fn} | D{body_blank:Fn,roof_blank:Fn,receivers:Fn,shell_screw_cuts:Fn} | D{boss_room:Fn} | D{box:R:method,prism_x:Fn,section_solid:Fn} | D{box:R:method,rectangle:Fn,ycylinder:Fn,zcylinder:Fn,rear_well_tower:Fn,wall_bosses:Fn,valve_seats:Fn,c14_rear_cutters:Fn,keystone_rear_geometry:Fn,fluid_supports:Fn} | D{box:R:method,rounded_prism:Fn,support_exits:Fn} | D{box:R:method} | D{brim_plan:Fn} | D{build_body_clearance:Fn,build_port_channel:Fn} | D{inverse_cuts:Fn,wire_cuts:Fn,upper_wire_room:Fn,display_cleanouts:Fn} | D{return_clearances:Fn,box:R:method,ycyl:Fn,teardrop_y:Fn} | D{rounded_prism:Fn} | D{section_solid:Fn} | D{shell_features:Fn} | D{stacked_well_towers:Fn}
- returns: NS
- steps: enclosure

## _union  (python _union:22; compiled line 141)
- `shapes`: L[R:_ReadingShape] | L[R:_Shape]
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## _funnel_containment  (python _funnel_containment:27; compiled line 186)
- `shell`: NS
- `box`: R:Box
- returns: D{S:F}
- steps: enclosure

## _corner_prism  (python _corner_prism:86; compiled line 244)
- `graph`: R:_Graph | R:_Questions
- `axis`: I
- `lo`: F
- `hi`: F | I
- `section`: L[T(F,F)] | T(T(F,F),T(F,F),T(F,F),T(F,F),T(F,F),T(F,F))
- `radius`: F | I
- `corners`: T(I,I) | T(I,I,I,I)
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## _rounded  (python _rounded:92; compiled line 322)
- `graph`: R:_Graph | R:_Questions
- `axis`: I
- `bounds`: T(F,F,F,F,F,F) | T(F,F,F,F,F,I)
- `radius`: F | I
- `corners`: T(I,I) | T(I,I,I,I)
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## _frame_leaves  (python _frame_leaves:100; compiled line 456)
- `shell`: NS
- `graph`: R:_Graph | R:_Questions
- returns: D{body_blank:Fn,roof_blank:Fn,receivers:Fn,shell_screw_cuts:Fn}
- steps: enclosure

## blank  (python _frame_leaves.<locals>.blank:103; compiled line 458)
- `w`: F
- `front`: F
- `back`: F
- `z0`: F
- `z1`: F
- `cx`: F
- `radius`: F
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `air`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## roof  (python _frame_leaves.<locals>.roof:119; compiled line 471)
- `inner`: T(F,F,F,F,F,F)
- `centre`: T(F,F)
- `seat`: F
- `air`: F
- `y_joint`: F
- `full_front_opening`: B
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## body  (python _frame_leaves.<locals>.body:125; compiled line 475)
- `centre`: T(F,F)
- `seat`: F
- `air`: F
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## receivers  (python _frame_leaves.<locals>.receivers:149; compiled line 497)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `y_joint`: F
- `centre`: T(F,F)
- `seat`: F
- `col`: S
- `up`: F | N
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## screws  (python _frame_leaves.<locals>.screws:167; compiled line 516)
- `inner`: T(F,F,F,F,F,F)
- `centre`: T(F,F)
- `seat`: F
- `col`: S
- `y_joint`: F
- returns: R:_Shape
- steps: enclosure

## _placed  (python _placed:177; compiled line 521)
- `graph`: R:_Graph
- `shape`: R:_Shape
- `frame`: D{rotation:T(T(F,F,F),T(F,F,F),T(F,F,F)),translation_mm:T(F,F,F)} | D{size:S,parent:S,rotation:T(T(F,F,F),T(F,F,F),T(F,F,F)),translation_mm:T(F,F,F),purpose:S} | R:dict
- returns: R:_Shape
- steps: enclosure

## _rear_well_roofs  (python _rear_well_roofs:250; compiled line 583)
- `wiring`: R:Surface
- returns: T(D{wago-h:T(F,F,F,F,F,F),wago-n:N},D{wago-h:T(F,F,F,F,F,F),wago-g:T(F,F,F,F,F,F),wago-n:T(F,F,F,F,F,F)})
- steps: enclosure

## _wiring_features  (python _wiring_features:301; compiled line 639)
- `shell`: NS
- `graph`: R:_Graph
- `parent`: S
- returns: D{add:R:_Shape,cut:R:_Shape,stations:L[D{name:S,size:S,parent:S,rotation:T(~,~,~),translation_mm:T(~,~,~),purpose:S}]}
- steps: enclosure

## _above_leaves  (python _above_leaves:345; compiled line 682)
- `shell`: NS
- `graph`: R:_Graph | R:_Questions
- returns: L[T(NS,D{apply:Fn,receiver_field:Fn})|T(NS,D{box:R:method,rectangle:Fn,ycylinder:Fn,zcylinder:Fn,rear_well_tower:Fn,wall_bosses:Fn,valve_seats:Fn,c14_rear_cutters:Fn,keystone_rear_geometry:Fn,fluid_supports:Fn})|T(R:Surface,D{shell_features:Fn})]
- steps: enclosure

## wires  (python _above_leaves.<locals>.wires:352; compiled line 688)
- `parent`: S
- returns: D{add:R:_Shape,cut:R:_Shape,stations:L[D{name:S,size:S,parent:S,rotation:T(~,~,~),translation_mm:T(~,~,~),purpose:S}]}
- steps: enclosure

## hosts  (python _above_leaves.<locals>.hosts:355; compiled line 691)
- returns: T(T14[R:_Shape],T(R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape))
- steps: enclosure

## cyl  (python _above_leaves.<locals>.hosts.<locals>.cyl:358; compiled line 694)
- `radius`: F
- `root`: T(F,F,F)
- `axis`: T(F,F,F)
- `length`: F
- returns: R:_Shape
- steps: enclosure

## identify  (python _above_leaves.<locals>.identify:400; compiled line 738)
- `piece`: R:_Shape
- returns: R:_Shape
- steps: enclosure

## receiver_field  (python _above_leaves.<locals>.receiver_field:407; compiled line 747)
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## valve_seats  (python _above_leaves.<locals>.valve_seats:412; compiled line 752)
- returns: D{valve-v-a:R:_Shape,vk-solenoid:R:_Shape}
- steps: enclosure

## sockets  (python _above_leaves.<locals>.valve_seats.<locals>.sockets:415; compiled line 755)
- returns: R:_Shape
- steps: enclosure

## c14  (python _above_leaves.<locals>.c14:433; compiled line 769)
- returns: T(R:_Shape,R:_Shape)
- steps: enclosure

## keystone  (python _above_leaves.<locals>.keystone:450; compiled line 782)
- `holds`: T(T(F,F,F,F),T(F,F,F,F))
- `keep_clear`: R:_Shape
- returns: T(R:_Shape,R:_Shape,R:_Shape)
- steps: enclosure

## <lambda>  (python ?; compiled line 817)
- `b`: R:dict
- `radius`: I
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 818)
- `r`: F
- `x`: F
- `z`: F
- `y0`: F
- `y1`: F
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 820)
- `stock`: R:_Shape
- `_ceiling`: F
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 821)
- returns: D{asse-seat:R:_Shape,pisco-seat:R:_Shape,meter-seat:R:_Shape,regulator-seat:R:_Shape}
- steps: enclosure

## _fluid_supports  (python _fluid_supports:495; compiled line 825)
- `graph`: R:_Graph
- returns: D{asse-seat:R:_Shape,pisco-seat:R:_Shape,meter-seat:R:_Shape,regulator-seat:R:_Shape}
- steps: enclosure

## runs  (python _fluid_supports.<locals>.runs:511; compiled line 839)
- `which`: S
- `frame`: R:dict
- `axis`: T(F,F)
- `air`: F | N
- returns: L[T(F,F,F)]
- steps: enclosure

## turned  (python _fluid_supports.<locals>.turned:520; compiled line 848)
- `profile`: L[T(F,F,F)] | R:list
- `axis`: T(F,F)
- returns: R:_Shape
- steps: enclosure

## hex_prism  (python _fluid_supports.<locals>.hex_prism:526; compiled line 852)
- `axis`: T(F,F)
- `apothem`: F
- `clock`: F
- `y0`: F
- `y1`: F
- `corner`: F
- returns: R:_Shape
- steps: enclosure

## pockets  (python _fluid_supports.<locals>.pockets:533; compiled line 857)
- `st`: R:dict
- returns: R:list
- steps: enclosure

## service_cuts  (python _fluid_supports.<locals>.service_cuts:540; compiled line 863)
- `st`: R:dict
- returns: R:list
- steps: enclosure

## <lambda>  (python ?; compiled line 885)
- `section`: D{span:T(F,F),segments:L[D{line:T(~,~)}]}
- returns: R:_Shape
- steps: enclosure

## at  (python _fluid_supports.<locals>.at:588; compiled line 902)
- `point`: T(F,F,F)
- returns: T(F,F,F)
- steps: enclosure

## wx  (python _fluid_supports.<locals>.wx:594; compiled line 909)
- `y`: F
- returns: F
- steps: enclosure

## wy  (python _fluid_supports.<locals>.wy:596; compiled line 912)
- `x`: F
- returns: F
- steps: enclosure

## stadium  (python _fluid_supports.<locals>.stadium:607; compiled line 923)
- `y`: F
- `z`: F
- `r`: F
- `span`: T(F,F)
- returns: R:_Shape
- steps: enclosure

## _route_features  (python _route_features:650; compiled line 959)
- `graph`: R:_Graph
- `host`: S
- returns: L[R:_Shape]
- steps: enclosure

## unit  (python _route_features.<locals>.unit:654; compiled line 963)
- `v`: L[F] | T(F,F,F)
- returns: T(F,F,F)
- steps: enclosure

## cross  (python _route_features.<locals>.cross:657; compiled line 967)
- `a`: T(F,F,F)
- `b`: T(F,F,F)
- returns: T(F,F,F)
- steps: enclosure

## place  (python _route_features.<locals>.place:659; compiled line 970)
- `shape`: R:_Shape
- `origin`: T(F,F,F)
- `x`: T(F,F,F)
- `y`: T(F,F,F)
- `z`: T(F,F,F)
- returns: R:_Shape
- steps: enclosure

## point  (python _route_features.<locals>.point:688; compiled line 1001)
- `r`: F
- `a`: F
- returns: T(F,F)
- steps: enclosure

## add  (python _route_features.<locals>.add:689; compiled line 1004)
- `a`: T(F,F)
- `b`: T(F,F)
- returns: T(F,F)
- steps: enclosure

## _leaves  (python _leaves:723; compiled line 1036)
- `shell`: NS
- `graph`: R:_Graph | R:_Questions
- `box`: R:Box
- returns: NS
- steps: enclosure

## rounded  (python _leaves.<locals>.rounded:726; compiled line 1042)
- `w`: F
- `d`: F
- `r`: F
- `z0`: F
- `z1`: F
- `cx`: F
- `cy`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## brim  (python _leaves.<locals>.brim:728; compiled line 1045)
- `grow`: F
- `z0`: F
- `z1`: F
- `cx`: F
- `cy`: F
- `front`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## plumb  (python _leaves.<locals>.plumb:733; compiled line 1050)
- `half`: F
- `front`: F
- `back`: F
- `seat`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## keepout  (python _leaves.<locals>.keepout:737; compiled line 1053)
- `outer`: T(F,F,F,F,F,F)
- `centre`: T(F,F)
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1059)
- `x`: I
- `z`: F
- `w`: F
- `h`: F
- `r`: F
- `y0`: F
- `y1`: F
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1065)
- `piece`: R:_Shape
- `y`: S
- `z`: S
- returns: R:_Shape
- steps: enclosure

## numbers  (python numbers:759; compiled line 1071)
- `shell`: NS
- `box`: R:Box
- returns: D{angle:F,outer:T(F,F,F,F,F,F),profile:D{end:T(F,F),foot:T(F,F),front_mid:T(F,F),normal:T(F,F,F),origin:T(F,F,F),roof:T(F,F),start:T(F,F),top_mid:T(F,F)},roof_fill_sections:T(T34[D{~:~}],T34[D{~:~}]),roof_transition:D{foot:F,height:F,outward_per_height:F},side_radius:F,standing_radius:F,color:T(F,F,F),panel:R:dict,funnel_containment:D{S:F}}
- steps: enclosure

## print_numbers  (python print_numbers:815; compiled line 1125)
- `shell`: NS
- `box`: R:Box
- returns: D{S:D{S:F}|D{across:F,along:F,margin:F,overrun:F,plan_tol:F,face_tol:F,pitch:F,width:F,depth:F,rise:F}|D{embed:F,raised_bounds:T(T(~,~,~,~,~,~),T(~,~,~,~,~,~),T(~,~,~,~,~,~),T(~,~,~,~,~,~),T(~,~,~,~,~,~),T(~,~,~,~,~,~)),label_channels:T(T(~,~,~,~,~,~),T(~,~,~,~,~,~))}|D{end:T(F,F),foot:T(F,F),front_mid:T(F,F),normal:T(F,F,F),origin:T(F,F,F),roof:T(F,F),start:T(F,F),top_mid:T(F,F)}|..}
- steps: enclosure

## <lambda>  (python ?; compiled line 1138)
- `s`: F
- returns: T(T(F,F),T(F,F))
- steps: enclosure

## cut  (python cut:839; compiled line 1156)
- `shell`: NS
- `box`: R:Box
- `directory`: P
- returns: R:dict
- steps: enclosure

