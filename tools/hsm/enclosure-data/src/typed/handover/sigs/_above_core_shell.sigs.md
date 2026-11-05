# _above_core_shell: observed signatures (11 live compiled functions)

## <lambda>  (python ?; compiled line 96)
- returns: NS
- steps: enclosure, enclosure-assembly

## psu_fastener_plan  (python psu_fastener_plan:24; compiled line 142)
- returns: D{S:B|F|I|S|..}
- steps: bom-masses, enclosure, enclosure-assembly, enclosure-box

## relay_fastener_plan  (python relay_fastener_plan:39; compiled line 244)
- returns: D{S:B|F|I|S|..}
- steps: bom-masses, enclosure, enclosure-assembly, enclosure-box

## wall_mount_datums  (python wall_mount_datums:61; compiled line 250)
- returns: D{psu:D{S:B|F|I|S|..},relay-1:D{S:B|F|I|S|..},relay-2:D{S:B|F|I|S|..}}
- steps: enclosure, enclosure-assembly, enclosure-box

## wall_fastener_bounds  (python wall_fastener_bounds:84; compiled line 268)
- returns: D{S:D{component:S,parent:S,kind:S,station:D{native_hole_index:I,position_world_mm:T(~,~,~),insert_face_world_mm:T(~,~,~),axis_world:T(~,~,~),threaded:B,stock_root_world_mm:T(~,~,~),stock_root_world_x_mm:F,standoff_mm:F},plan:D{S:B|F|I|S|..},bounds_mm:T(T(~,~,~),T(~,~,~))}}
- steps: enclosure-box

## in_wall_fastener_lane  (python in_wall_fastener_lane:112; compiled line 298)
- `name`: S
- `bounds`: T(F,F,F,F,F,F)
- `tolerance`: F
- returns: B
- steps: enclosure-box

## c14_fastener_plan  (python c14_fastener_plan:122; compiled line 419)
- returns: D{screw_length_mm:F,washer_od_mm:F,washer_thickness_mm:F,flange_thickness_mm:F,insert_length_mm:F,screw_reach_mm:F,pilot_depth_mm:F,boss_depth_mm:F,tip_air_mm:F,backing_mm:F}
- steps: bom-masses, enclosure

## keystone_land  (python keystone_land:130; compiled line 445)
- returns: T(F,F,F,F,F,F)
- steps: enclosure

## valve_seat_datums  (python valve_seat_datums:173; compiled line 711)
- returns: D{valve-v-a:D{parent:S,stock_min_world_mm:L[F],stock_max_world_mm:L[F],socket_diameter_mm:F,socket_floor_backing_mm:F,frame:R:dict,interface:S},vk-solenoid:D{parent:S,stock_min_world_mm:L[F],stock_max_world_mm:L[F],socket_diameter_mm:F,socket_floor_backing_mm:F,frame:R:dict,interface:S}}
- steps: enclosure

## rear_geometry  (python rear_geometry:205; compiled line 1011)
- `piece`: R:_Shape
- `holds`: T(T(F,F,F,F),T(F,F,F,F))
- `keep_clear`: R:_Shape
- returns: R:_Shape
- steps: enclosure

## apply  (python apply:231; compiled line 1320)
- `piece`: R:_Shape
- `box_spec`: R:Box
- `y_side`: S
- `z_side`: S
- returns: R:_Shape
- steps: enclosure

