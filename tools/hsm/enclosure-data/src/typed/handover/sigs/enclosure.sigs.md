# enclosure: observed signatures (221 live compiled functions)

## print_up  (python print_up:221; compiled line 831)
- `y_side`: S
- `z_side`: S
- returns: F
- steps: enclosure, enclosure-assembly

## flute_backed_sections  (python flute_backed_sections:339; compiled line 852)
- returns: T12[T(S,F)]
- steps: enclosure-box

## cond_slot_half  (python cond_slot_half:695; compiled line 1094)
- `sheet`: F
- returns: F
- steps: enclosure

## cond_slot_mouth  (python cond_slot_mouth:700; compiled line 1107)
- `face`: F
- returns: F
- steps: enclosure

## interior_x  (python interior_x:862; compiled line 1124)
- returns: T(F,F)
- steps: enclosure, enclosure-assembly, enclosure-box

## back_top_wall_face  (python back_top_wall_face:869; compiled line 1153)
- returns: F
- steps: enclosure, enclosure-assembly

## back_wall_t_at  (python back_wall_t_at:879; compiled line 1170)
- `x`: F
- `z`: F
- returns: F
- steps: enclosure-assembly

## back_top_flank_face  (python back_top_flank_face:897; compiled line 1292)
- returns: T(F,F)
- steps: enclosure, enclosure-assembly, enclosure-box

## back_bottom_flank_face  (python back_bottom_flank_face:915; compiled line 1327)
- returns: T(F,F)
- steps: enclosure

## front_bottom_flank_face  (python front_bottom_flank_face:928; compiled line 1362)
- returns: T(F,F)
- steps: enclosure, enclosure-assembly, enclosure-box

## vent_flank_face  (python vent_flank_face:940; compiled line 1397)
- `sx`: F
- returns: F
- steps: enclosure

## front_top_flank_face  (python front_top_flank_face:953; compiled line 1437)
- returns: T(F,F)
- steps: enclosure, enclosure-assembly, enclosure-box

## lip_face_x  (python lip_face_x:987; compiled line 1674)
- returns: T(F,F)
- steps: enclosure, enclosure-assembly, enclosure-box

## piece_root_faces  (python piece_root_faces:997; compiled line 1711)
- `inner`: T(F,F,F,F,F,F)
- `y_side`: S
- `z_side`: S
- returns: T(F,F,F,F,F,F)
- steps: enclosure, enclosure-assembly

## back_top_ceiling_face  (python back_top_ceiling_face:1210; compiled line 2221)
- returns: F
- steps: enclosure

## back_top_ceiling_stock  (python back_top_ceiling_stock:1218; compiled line 2241)
- `y_joint`: F
- `lane`: F
- returns: R:_Shape
- steps: enclosure

## back_flank_start  (python back_flank_start:1317; compiled line 2348)
- `y_joint`: F
- returns: F
- steps: enclosure, enclosure-box

## documented  (python documented:1461; compiled line 2406)
- `box`: R:Box
- returns: R:Box
- steps: enclosure-box

## record_bound  (python record_bound:1620; compiled line 2598)
- `bound`: R:Bound
- returns: R:Bound
- steps: enclosure, enclosure-box

## _supported_cut  (python _supported_cut:1626; compiled line 2647)
- `cutter`: R:_Shape
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _column_arc  (python _column_arc:1647; compiled line 2741)
- `inner`: T(F,F,F,F,F,F)
- `sx`: I
- `sy`: I
- returns: T(F,F)
- steps: enclosure, enclosure-box

## _corner_column  (python _corner_column:1659; compiled line 2797)
- `inner`: T(F,F,F,F,F,F)
- `sx`: I
- `sy`: I
- `grow`: F
- `z`: T(F,F)
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-box

## _column_pillar  (python _column_pillar:1674; compiled line 2853)
- `inner`: T(F,F,F,F,F,F)
- `sx`: I
- `sy`: I
- `zj`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-box

## _column_along  (python _column_along:1693; compiled line 2960)
- returns: F
- steps: enclosure

## _column_depth  (python _column_depth:1716; compiled line 3016)
- returns: F
- steps: enclosure

## _cavity  (python _cavity:1724; compiled line 3057)
- `inner`: T(F,F,F,F,F,F)
- `inset`: F
- `z`: N | T(F,F)
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-box

## _cradle_relief  (python _cradle_relief:1750; compiled line 3178)
- `room`: T(F,F,F,F,F,F)
- `station`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## _column_relief  (python _column_relief:1767; compiled line 3325)
- `inner`: T(F,F,F,F,F,F)
- `sx`: I
- `sy`: I
- `room`: T(F,F,F,F,F,F)
- `zj`: F
- `cradle`: T(T(F,F,F,F,F,F),T(F,F,F,F,F,F))
- returns: R:_Shape
- steps: enclosure

## _column_relief_rise  (python _column_relief_rise:1785; compiled line 3511)
- `inner`: T(F,F,F,F,F,F)
- `sx`: I
- `sy`: I
- `room`: T(F,F,F,F,F,F)
- `zj`: F
- `up`: F
- `cradle`: T(T(F,F,F,F,F,F),T(F,F,F,F,F,F))
- returns: R:_Shape
- steps: enclosure

## seam_bosses  (python seam_bosses:1905; compiled line 4001)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `splits`: T(F,F)
- returns: L[T(F,F,F,F)]
- steps: enclosure-box

## _in_a_boss  (python _in_a_boss:1932; compiled line 4168)
- `b`: R:_ReadingBounds
- `bosses`: L[T(F,F,F,F)]
- returns: B
- steps: enclosure-box

## _open_bands  (python _open_bands:1938; compiled line 4269)
- `spans`: L[T(F,F)] | L[]
- `z0`: F
- `z1`: F
- `clear`: F
- returns: L[T(F,F)] | L[]
- steps: enclosure-box

## _clipped  (python _clipped:1955; compiled line 4403)
- `bands`: L[T(F,F)] | L[]
- `lo`: F
- `hi`: F
- returns: L[T(F,F)] | L[]
- steps: enclosure-box

## _bed_band  (python _bed_band:1961; compiled line 4488)
- `inner`: T(F,F,F,F,F,F)
- returns: T(F,F)
- steps: enclosure, enclosure-box

## _lip_band  (python _lip_band:1972; compiled line 4531)
- `inner`: T(F,F,F,F,F,F)
- `z`: T(F,F)
- `inset`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-box

## _lip_denied  (python _lip_denied:1995; compiled line 4606)
- `placed`: R:dict
- `inner`: T(F,F,F,F,F,F)
- `y_span`: T(F,F)
- `plate`: R:dict
- `y_joint`: F
- `commons`: R:dict
- returns: L[T(F,F)] | L[]
- steps: enclosure-box

## _z_joints  (python _z_joints:2032; compiled line 4785)
- `placed`: R:dict
- `inner`: T(F,F,F,F,F,F)
- `stated`: F
- `plate`: R:dict
- `y_joint`: F
- `readings`: R:BoxReadings
- returns: T(F,F)
- steps: enclosure-box

## back_top_flank_bound  (python back_top_flank_bound:2079; compiled line 4818)
- `placed`: R:dict
- `pack`: R:Pack
- `y_joint`: F
- `splits`: T(F,F)
- `bounds`: R:dict
- returns: R:Bound
- steps: enclosure-box

## _dims  (python _dims:2117; compiled line 5285)
- `pack`: R:Pack
- `readings`: R:BoxReadings
- returns: R:Box
- steps: enclosure-box

## _facet_geom  (python _facet_geom:2436; compiled line 5410)
- `outer`: T(F,F,F,F,F,F)
- returns: T(F,T(F,F,F),T(F,F,F),F,F)
- steps: enclosure, enclosure-assembly

## housing_back_y  (python housing_back_y:2444; compiled line 5487)
- `outer`: T(F,F,F,F,F,F)
- returns: F
- steps: enclosure, enclosure-box

## _seat_back  (python _seat_back:2480; compiled line 5650)
- `depth`: F
- `half_slope`: F
- returns: F
- steps: enclosure-box

## display_centre_x  (python display_centre_x:2487; compiled line 5734)
- `outer`: T(F,F,F,F,F,F)
- returns: F
- steps: enclosure, enclosure-assembly

## _facet_wedge  (python _facet_wedge:2495; compiled line 5755)
- `outer`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## _plan_segments  (python _plan_segments:2523; compiled line 5934)
- `outer`: T(F,F,F,F,F,F)
- returns: T9[T(S,F,T(T(~,~),F,F))|T(S,F,T(T(~,~),T(~,~),T(~,~)))]
- steps: enclosure, enclosure-box

## plan_perimeter  (python plan_perimeter:2575; compiled line 6275)
- `outer`: T(F,F,F,F,F,F)
- returns: F
- steps: enclosure, enclosure-box

## flute_pitch  (python flute_pitch:2580; compiled line 6327)
- `outer`: T(F,F,F,F,F,F)
- returns: F
- steps: enclosure, enclosure-box

## plan_at  (python plan_at:2588; compiled line 6356)
- `s`: F
- `outer`: T(F,F,F,F,F,F)
- returns: T(T(F,F),T(F,F))
- steps: enclosure

## flute_centres  (python flute_centres:2615; compiled line 6427)
- `outer`: T(F,F,F,F,F,F)
- returns: T272[F]
- steps: enclosure

## housing_fill  (python housing_fill:2622; compiled line 6490)
- `box`: R:Box
- returns: R:_Shape
- steps: enclosure

## _display_point  (python _display_point:2629; compiled line 6528)
- `outer`: T(F,F,F,F,F,F)
- `point`: T(F,F,F)
- returns: T(F,F,F)
- steps: enclosure, enclosure-assembly

## display_plane  (python display_plane:2637; compiled line 6603)
- `outer`: T(F,F,F,F,F,F)
- returns: R:Plane
- steps: enclosure-assembly

## _display_cut_exit_depth  (python _display_cut_exit_depth:2647; compiled line 6707)
- returns: F
- steps: enclosure

## _port_cuts  (python _port_cuts:2662; compiled line 6727)
- `ports`: L[] | T()
- `y0`: F
- `y1`: F
- `up`: F
- returns: L[]
- steps: enclosure

## disposal_field  (python disposal_field:2685; compiled line 6856)
- `outer`: T(F,F,F,F,F,F)
- returns: T(F,F,F,F,F,F)
- steps: enclosure

## disposal_figures  (python disposal_figures:2698; compiled line 6957)
- `outer`: T(F,F,F,F,F,F)
- returns: D{DISPOSAL_CAP_HEIGHT:S,DISPOSAL_RELIEF:S,DISPOSAL_BOTTOM:S,DISPOSAL_FIELD_WIDTH:S,DISPOSAL_FIELD_HEIGHT:S,DISPOSAL_MARGIN:S}
- steps: enclosure

## _nameplate  (python _nameplate:2710; compiled line 7081)
- `solid`: R:_Shape
- `plate`: N
- `outer`: T(F,F,F,F,F,F)
- `y_outer`: F
- `zlo`: F
- `zhi`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _port_field  (python _port_field:2731; compiled line 7276)
- `solid`: R:_Shape
- `field`: N
- `ports`: T()
- `y_outer`: F
- `wall_at`: Fn | N
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _x_port_cuts  (python _x_port_cuts:2762; compiled line 7494)
- `ports`: L[] | T()
- `x0`: F
- `x1`: F
- `up`: F
- returns: L[]
- steps: enclosure

## _funnel_frame  (python _funnel_frame:2779; compiled line 7635)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- returns: T(F,F,F,F)
- steps: enclosure-box

## _funnel_hole  (python _funnel_hole:2795; compiled line 7683)
- `centre`: T(F,F)
- returns: T(F,F,F,F)
- steps: enclosure, enclosure-box

## _funnel_cut_plan  (python _funnel_cut_plan:2811; compiled line 7739)
- `centre`: T(F,F)
- returns: T(F,F,F,F)
- steps: enclosure

## funnel_seat_z  (python funnel_seat_z:2818; compiled line 7777)
- `outer`: T(F,F,F,F,F,F)
- returns: F
- steps: enclosure, enclosure-assembly

## with_funnel  (python with_funnel:2823; compiled line 7794)
- `box`: R:Box
- `centre`: T(F,F)
- returns: R:Box
- steps: enclosure-box

## _funnel_cut  (python _funnel_cut:2852; compiled line 8130)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `centre`: T(F,F)
- `wells`: T()
- `up`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## _seat_ledge_corbels  (python _seat_ledge_corbels:2908; compiled line 8651)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `centre`: T(F,F)
- `y_joint`: F
- returns: R:_Shape
- steps: enclosure

## _ceiling_tongue_air  (python _ceiling_tongue_air:2933; compiled line 8674)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- returns: R:_Shape
- steps: enclosure

## _handhold_levels  (python _handhold_levels:2966; compiled line 8730)
- `inner`: R:list | T(F,F,F,F,F,F)
- returns: T(F,F,F)
- steps: bom-masses, enclosure, enclosure-assembly, enclosure-box, enclosure-mechanical-sync

## _band_x  (python _band_x:2973; compiled line 8761)
- `x_ext`: F
- `sx`: F
- returns: T(F,F)
- steps: enclosure, enclosure-assembly

## y_stack_y  (python y_stack_y:2979; compiled line 8791)
- `y_joint`: F
- returns: T(F,F)
- steps: enclosure-box

## _y_stack_gap  (python _y_stack_gap:2985; compiled line 8828)
- `down_supported`: B
- `up_supported`: B
- returns: F
- steps: bom-masses, enclosure, enclosure-assembly, enclosure-box, enclosure-mechanical-sync

## _y_knuckle_faces  (python _y_knuckle_faces:2990; compiled line 8881)
- `piece`: S
- `gap_below`: F
- `gap_above`: F
- returns: T(S,S)
- steps: enclosure

## y_stack  (python y_stack:3010; compiled line 8953)
- `inner`: R:list | T(F,F,F,F,F,F)
- returns: T(T(T(S,F,F,F,F),T(S,F,F,F,F),T(S,F,F,F,F)),T(T(S,F,F,F,F),T(S,F,F,F,F),T(S,F,F,F,F)))
- steps: bom-masses, enclosure, enclosure-assembly, enclosure-box, enclosure-mechanical-sync

## y_stack_axis  (python y_stack_axis:3052; compiled line 9186)
- `x_in`: F
- `sx`: F
- `y_joint`: F
- `rod`: S
- returns: T(F,F)
- steps: enclosure, enclosure-assembly

## y_stack_rods  (python y_stack_rods:3058; compiled line 9224)
- `inner`: R:list | T(F,F,F,F,F,F)
- returns: T(T(S,F,F,F,S,F,F),T(S,F,F,F,S,F,F))
- steps: bom-masses, enclosure, enclosure-assembly, enclosure-mechanical-sync

## _y_face_z  (python _y_face_z:3078; compiled line 9354)
- `kind`: S
- `level`: F
- `x_in`: F
- `sx`: F
- `y_joint`: F
- `x`: F
- `y`: F
- returns: F
- steps: enclosure

## _y_under_face  (python _y_under_face:3087; compiled line 9408)
- `kind`: S
- `level`: F
- `x_in`: F
- `sx`: F
- `y_joint`: F
- `xa`: F
- `xb`: F
- `ya`: F
- `yb`: F
- `z_floor`: F
- returns: R:_Shape
- steps: enclosure

## _y_between_faces  (python _y_between_faces:3098; compiled line 9575)
- `bottom`: S
- `z0`: F
- `top`: S
- `z1`: F
- `x_in`: F
- `sx`: F
- `y_joint`: F
- `xa`: F
- `xb`: F
- `ya`: F
- `yb`: F
- `cap`: F | N
- returns: R:_Shape
- steps: enclosure

## _y_top_cap  (python _y_top_cap:3107; compiled line 9778)
- `top`: S
- `z1`: F
- `depth`: F
- returns: F | N
- steps: enclosure

## _y_knuckle  (python _y_knuckle:3117; compiled line 9811)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `x_in`: F
- `sx`: F
- `y_joint`: F
- `piece`: S
- `z0`: F
- `z1`: F
- `depth`: F
- returns: R:_Shape
- steps: enclosure

## xs  (python _y_knuckle.<locals>.xs:3127; compiled line 9814)
- `d0`: F
- `d1`: F
- returns: L[F]
- steps: enclosure

## _y_knuckle_air  (python _y_knuckle_air:3190; compiled line 9869)
- `x_in`: F
- `sx`: F
- `y_joint`: F
- `piece`: S
- `z0`: F
- `z1`: F
- `gap_below`: F
- `gap_above`: F
- `depth`: F
- returns: R:_Shape
- steps: enclosure

## _y_stack_bores  (python _y_stack_bores:3204; compiled line 10067)
- `x_in`: F
- `sx`: F
- `y_joint`: F
- `inner`: T(F,F,F,F,F,F)
- returns: T(R:_ReadingShape,R:_ReadingShape,R:_ReadingShape,R:_ReadingShape,R:_ReadingShape,R:_ReadingShape) | T(R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape)
- steps: enclosure, enclosure-assembly

## head_access  (python _y_stack_bores.<locals>.head_access:3215; compiled line 10202)
- `ax`: F
- `ay`: F
- `z0`: F
- `z1`: F
- `x_end`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly

## _y_bore_reliefs  (python _y_bore_reliefs:3243; compiled line 10528)
- `x_in`: F
- `sx`: F
- `y_joint`: F
- `inner`: T(F,F,F,F,F,F)
- `name`: S
- returns: L[R:_Shape]
- steps: enclosure

## _y_stacks  (python _y_stacks:3293; compiled line 11064)
- `piece`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `y_joint`: F
- `name`: S
- `funnel`: T(F,F)
- returns: R:_Shape
- steps: enclosure

## _front_lip  (python _front_lip:3318; compiled line 11416)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- returns: R:_Shape
- steps: enclosure

## _y_lip_channel  (python _y_lip_channel:3360; compiled line 11557)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- returns: R:_Shape
- steps: enclosure

## _floor_tongue  (python _floor_tongue:3376; compiled line 11701)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- returns: T(R:_ReadingShape,R:_ReadingShape) | T(R:_Shape,R:_Shape)
- steps: enclosure, enclosure-assembly

## _handhold_y  (python _handhold_y:3412; compiled line 11803)
- returns: T(F,F)
- steps: enclosure, enclosure-assembly

## _handhold_backing_end  (python _handhold_backing_end:3422; compiled line 11871)
- `y_joint`: F
- `y_side`: S
- returns: F
- steps: enclosure, enclosure-assembly

## _handhold_backing_joint  (python _handhold_backing_joint:3429; compiled line 11937)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `x_ext`: F
- `sx`: F
- `y_side`: S
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly

## _handhold_frame  (python _handhold_frame:3445; compiled line 12065)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `x_ext`: F
- `sx`: F
- `y_side`: S
- returns: R:_Shape
- steps: enclosure

## _handholds  (python _handholds:3470; compiled line 12373)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `y_side`: S
- returns: R:_Shape
- steps: enclosure

## _finish_handholds  (python _finish_handholds:3481; compiled line 12521)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## _z_rail_runs  (python _z_rail_runs:3501; compiled line 12666)
- `inner`: R:list | T(F,F,F,F,F,F)
- `y_joint`: F
- `col`: S
- `plate`: N | R:dict
- `chase`: R:list | T() | T(T(F,F,F))
- returns: L[T(F,F,F,F,F)]
- steps: enclosure, enclosure-box, enclosure-mechanical-sync

## _z_rail_travel  (python _z_rail_travel:3544; compiled line 12771)
- `inner`: R:list | T(F,F,F,F,F,F)
- `y_joint`: F
- `col`: S
- `plate`: R:dict
- `chase`: R:list | T(T(F,F,F))
- returns: F
- steps: enclosure, enclosure-mechanical-sync

## _rail_nominal_foot_face  (python _rail_nominal_foot_face:3552; compiled line 12781)
- `col`: S
- `sx`: F
- returns: F
- steps: enclosure, enclosure-box

## _rail_foot_face  (python _rail_foot_face:3563; compiled line 12904)
- `x_in`: F
- `sx`: F
- `col`: S
- returns: F
- steps: enclosure, enclosure-box

## _rail_hook_lap  (python _rail_hook_lap:3572; compiled line 12930)
- `col`: S
- returns: F
- steps: enclosure, enclosure-box

## _rail_x  (python _rail_x:3577; compiled line 12959)
- `x_in`: F
- `sx`: F
- `col`: S
- returns: T(F,F,F,F)
- steps: enclosure, enclosure-box

## _rail_channel_span  (python _rail_channel_span:3588; compiled line 13029)
- `x_in`: F
- `sx`: F
- `col`: S
- returns: T(F,F,F)
- steps: enclosure

## rail_catch_air  (python rail_catch_air:3604; compiled line 13135)
- `col`: S
- returns: F
- steps: enclosure

## _z_rail_heads  (python _z_rail_heads:3610; compiled line 13183)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `zj`: F
- `col`: S
- `plate`: R:dict
- `chase`: T(T(F,F,F))
- `runs`: N
- returns: R:_Shape
- steps: enclosure

## _z_rail_feet  (python _z_rail_feet:3670; compiled line 13628)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `zj`: F
- `col`: S
- `plate`: R:dict
- `chase`: T(T(F,F,F))
- returns: R:_Shape
- steps: enclosure

## _rail_keep  (python _rail_keep:3717; compiled line 13656)
- `inner`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## _z_rail_channels  (python _z_rail_channels:3730; compiled line 13734)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `zj`: F
- `col`: S
- `plate`: R:dict
- `chase`: T(T(F,F,F))
- `runs`: N
- returns: R:_Shape
- steps: enclosure

## _lip_ring  (python _lip_ring:3810; compiled line 14124)
- `inner`: T(F,F,F,F,F,F)
- `gap`: T(F,F)
- `z0`: F
- `z1`: F
- `inset`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-box

## _lip_underwall  (python _lip_underwall:3823; compiled line 14200)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `zj`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-box

## _front_bottom_flank_skin  (python _front_bottom_flank_skin:3858; compiled line 14241)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `zj`: F
- returns: R:_Shape
- steps: enclosure

## _plate_foot  (python _plate_foot:3869; compiled line 14335)
- `inner`: T(F,F,F,F,F,F)
- `plate`: R:dict
- `zj`: F
- returns: R:_Shape
- steps: enclosure

## _plate_foot_clearance  (python _plate_foot_clearance:3899; compiled line 14547)
- `plate`: R:dict
- `zj`: F
- `xmin`: F
- `xmax`: F
- `ymin`: F
- `ymax`: F
- `zmax`: F
- returns: F
- steps: enclosure-box

## plate_foot_envelope_clearance  (python plate_foot_envelope_clearance:3919; compiled line 14832)
- `plate`: R:dict
- `zj`: F
- `envelope`: R:_ReadingBounds
- returns: F
- steps: enclosure-box

## _back_bottom_flank_skin  (python _back_bottom_flank_skin:3954; compiled line 14881)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `zj`: F
- returns: R:_Shape
- steps: enclosure

## bay_x_span  (python bay_x_span:3975; compiled line 14985)
- `inner`: T(F,F,F,F,F,F)
- returns: T(F,F)
- steps: enclosure, enclosure-box

## _pump_relief_regions  (python _pump_relief_regions:3983; compiled line 15003)
- `pump_trays`: R:list | T(T(F,F,F),T(F,F,F))
- returns: L[T(F,F,F,F,F)]
- steps: enclosure, enclosure-assembly, enclosure-box

## _front_relief_regions  (python _front_relief_regions:4000; compiled line 15084)
- `pump_trays`: T(T(F,F,F),T(F,F,F))
- returns: L[T(F,F,F,F,F)]
- steps: enclosure-box

## _front_relief_cuts  (python _front_relief_cuts:4006; compiled line 15129)
- `inner`: T(F,F,F,F,F,F)
- `regions`: T(T(F,F,F,F,F),T(F,F,F,F,F))
- `slip`: F
- returns: L[R:_Shape]
- steps: enclosure

## _front_floor  (python _front_floor:4041; compiled line 15366)
- `regions`: L[T(F,F,F,F,F)]
- `b`: R:_ReadingBounds
- `name`: S
- returns: F
- steps: enclosure-box

## _front_flat_lip_drop  (python _front_flat_lip_drop:4056; compiled line 15494)
- `inner`: T(F,F,F,F,F,F)
- `zj`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-box

## bay_back_y  (python bay_back_y:4089; compiled line 15592)
- `plate`: R:dict
- returns: F
- steps: enclosure, enclosure-assembly, internal-plumbing-sync

## _front_top_flank_bedding_cut  (python _front_top_flank_bedding_cut:4094; compiled line 15610)
- `inner`: T(F,F,F,F,F,F)
- `y0`: F
- `y1`: F
- `zj`: F
- returns: R:_Shape
- steps: enclosure

## _front_top_flanks  (python _front_top_flanks:4117; compiled line 15762)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `box`: R:Box
- `y_joint`: F
- `zj`: F
- returns: R:_Shape
- steps: enclosure

## _back_top_wall  (python _back_top_wall:4158; compiled line 16046)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `box`: R:Box
- `zj`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _back_top_wall_relief_cut  (python _back_top_wall_relief_cut:4190; compiled line 16059)
- `field`: N
- `up`: F
- `ceiling`: F
- returns: N
- steps: enclosure

## _back_top_flank_tie_cut  (python _back_top_flank_tie_cut:4230; compiled line 16085)
- `box`: R:Box
- returns: N
- steps: enclosure

## _flank_body_pockets  (python _flank_body_pockets:4246; compiled line 16216)
- `piece`: R:_Shape
- `pockets`: T()
- returns: R:_Shape
- steps: enclosure

## _front_top_flank_pockets  (python _front_top_flank_pockets:4260; compiled line 16303)
- `piece`: R:_Shape
- `pockets`: T(T(S,F,F,F,F,F,F),T(S,F,F,F,F,F,F))
- returns: R:_Shape
- steps: enclosure

## _back_top_flanks  (python _back_top_flanks:4276; compiled line 16507)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `box`: R:Box
- `y_joint`: F
- `zj`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _ceiling_tie_reliefs  (python _ceiling_tie_reliefs:4323; compiled line 16795)
- `box`: R:Box
- `lane`: F
- returns: L[]
- steps: enclosure

## _ceiling_cap_reliefs  (python _ceiling_cap_reliefs:4357; compiled line 16820)
- `box`: R:Box
- `lane`: F
- returns: L[]
- steps: enclosure

## _ceiling_tie_channel_relief  (python _ceiling_tie_channel_relief:4380; compiled line 16841)
- `box`: R:Box
- `lane`: F
- returns: N
- steps: enclosure

## _back_top_ceiling  (python _back_top_ceiling:4403; compiled line 17056)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `box`: R:Box
- returns: R:_Shape
- steps: enclosure

## cap_split_z  (python cap_split_z:4458; compiled line 17111)
- `pump_trays`: T(T(F,F,F),T(F,F,F))
- returns: F
- steps: enclosure

## cap_terminal_opening_z  (python cap_terminal_opening_z:4463; compiled line 17147)
- `box`: R:Box
- returns: F
- steps: enclosure

## cap_crown_z  (python cap_crown_z:4469; compiled line 17197)
- `box`: R:Box
- returns: F
- steps: enclosure

## cap_terminal_crown_r  (python cap_terminal_crown_r:4474; compiled line 17214)
- `box`: R:Box
- returns: F
- steps: enclosure

## pump_skirt_support_z  (python pump_skirt_support_z:4479; compiled line 17255)
- `pump_trays`: T(T(F,F,F),T(F,F,F))
- returns: F
- steps: enclosure

## pump_skirt_band_aft_y  (python pump_skirt_band_aft_y:4484; compiled line 17288)
- `pump_trays`: R:list | T(T(F,F,F),T(F,F,F))
- returns: F
- steps: enclosure, enclosure-assembly, internal-plumbing-sync

## pump_cartridge_aft_y  (python pump_cartridge_aft_y:4490; compiled line 17329)
- `pump_trays`: R:list | T(T(F,F,F),T(F,F,F))
- `plate`: R:dict
- returns: F
- steps: enclosure, enclosure-assembly, internal-plumbing-sync

## _outlet_fore_miter_wedges  (python _outlet_fore_miter_wedges:4509; compiled line 17349)
- `cx`: F
- `cy`: F
- `cz`: F
- returns: L[R:_Shape]
- steps: enclosure

## _outlet_under_tangent_wedges  (python _outlet_under_tangent_wedges:4528; compiled line 17493)
- `cx`: F
- `cy`: F
- `cz`: F
- returns: L[R:_Shape]
- steps: enclosure

## pump_cartridge_figures  (python pump_cartridge_figures:4550; compiled line 17643)
- `box`: R:Box
- returns: D{S:S}
- steps: enclosure

## bay_floor_z  (python bay_floor_z:4555; compiled line 17663)
- `pump_trays`: R:list | T(T(F,F,F),T(F,F,F))
- returns: T(F,F)
- steps: enclosure, enclosure-assembly, enclosure-box

## _flank_lip_drop  (python _flank_lip_drop:4575; compiled line 17677)
- `inner`: T(F,F,F,F,F,F)
- `plate`: R:dict
- `y_joint`: F
- `zj`: F
- returns: R:_Shape
- steps: enclosure

## _flank_lip_run  (python _flank_lip_run:4591; compiled line 17723)
- `inner`: T(F,F,F,F,F,F)
- `plate`: R:dict
- `y_joint`: F
- `z`: T(F,F)
- returns: R:_Shape
- steps: enclosure

## _bay_floor  (python _bay_floor:4608; compiled line 17774)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `plate`: R:dict
- `pump_trays`: T(T(F,F,F),T(F,F,F))
- returns: R:_Shape
- steps: enclosure

## _bulkhead  (python _bulkhead:4626; compiled line 17946)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `plate`: R:dict
- `bay`: T(F,F,F)
- returns: R:_Shape
- steps: enclosure

## _ridge_wall  (python _ridge_wall:4638; compiled line 17994)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `plate`: R:dict
- `bay`: T(F,F,F)
- `funnel`: T(F,F)
- returns: R:_Shape
- steps: enclosure

## build_pump_retainer  (python build_pump_retainer:4685; compiled line 18331)
- `box`: R:Box
- `halves_cache`: N
- `seated`: B
- returns: R:_Shape
- steps: enclosure

## pump_dock_figures  (python pump_dock_figures:4690; compiled line 18358)
- `box`: R:Box
- returns: D{S:S}
- steps: enclosure

## <lambda>  (python ?; compiled line 18484)
- `p`: R:dict
- returns: F
- steps: enclosure

## <lambda>  (python ?; compiled line 18536)
- `r`: D{elbows:T(D{crossing:T(~,~,~),socket:T(~,~,~),stem:F,showing:F},D{crossing:T(~,~,~),socket:T(~,~,~),stem:F,showing:F}),tube:T(D{kind:S,start_mm:T(~,~,~),midpoint_mm:T(~,~,~),end_mm:T(~,~,~),radius_mm:F,sweep_degrees:F,start_tangent:T(~,~,~),end_tangent:T(~,~,~),length_mm:F},D{kind:S,start_mm:T(~,~,~),midpoint_mm:T(~,~,~),end_mm:T(~,~,~),radius_mm:F,sweep_degrees:F,start_tangent:T(~,~,~),end_tangent:T(~,~,~),length_mm:F}),exposed_mm:F,cut_mm:F,floor_z:F}
- returns: F
- steps: enclosure

## _floor_bosses  (python _floor_bosses:4743; compiled line 19241)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `stations`: T(T(F,F,F,F),T(F,F,F,F),T(F,F,F,F),T(F,F,F,F))
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- returns: R:_Shape
- steps: enclosure

## east_boss_pairs  (python east_boss_pairs:4886; compiled line 19667)
- `stations`: L[]
- returns: L[]
- steps: enclosure

## _east_bosses  (python _east_bosses:4994; compiled line 20342)
- `solid`: R:_Shape
- `roots`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `stations`: T()
- `fills`: T()
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _side_wells  (python _side_wells:5192; compiled line 20643)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `stations`: T()
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _vent_chase  (python _vent_chase:5336; compiled line 20721)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `stations`: T(T(F,F,F))
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _west_cradle  (python _west_cradle:5514; compiled line 21655)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `stations`: T(T(F,F,F))
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- returns: R:_Shape
- steps: enclosure

## _cond_cradle_corbel  (python _cond_cradle_corbel:5581; compiled line 22066)
- `inner`: T(F,F,F,F,F,F)
- `station`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## _cond_cradle  (python _cond_cradle:5593; compiled line 22232)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `stations`: T(T(F,F,F,F,F,F),T(F,F,F,F,F,F))
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- returns: R:_Shape
- steps: enclosure

## _cond_mount_corbel  (python _cond_mount_corbel:5653; compiled line 22587)
- `inner`: T(F,F,F,F,F,F)
- `station`: T(F,F,F,T(T(F,F,F),T(F,F,F)))
- returns: R:_Shape
- steps: enclosure

## _cond_mount  (python _cond_mount:5663; compiled line 22709)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `station`: T(F,F,F,T(T(F,F,F),T(F,F,F)))
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- returns: R:_Shape
- steps: enclosure

## vent_band  (python vent_band:5699; compiled line 23044)
- `airway`: T(F,F,F,F)
- returns: T(F,F)
- steps: enclosure

## vent_transoms  (python vent_transoms:5711; compiled line 23070)
- `airway`: T(F,F,F,F)
- returns: T(T(F,F),T(F,F),T(F,F))
- steps: enclosure

## vent_segment  (python vent_segment:5725; compiled line 23183)
- `airway`: T(F,F,F,F)
- returns: F
- steps: enclosure

## vent_segments  (python vent_segments:5731; compiled line 23224)
- `airway`: T(F,F,F,F)
- returns: T(T(F,F),T(F,F),T(F,F),T(F,F))
- steps: enclosure

## vent_grooves  (python vent_grooves:5742; compiled line 23337)
- `outer`: T(F,F,F,F,F,F)
- `airway`: T(F,F,F,F)
- returns: T46[T(F,F)]
- steps: enclosure

## _vent_cutter  (python _vent_cutter:5800; compiled line 23547)
- `outer`: T(F,F,F,F,F,F)
- `sx`: F
- `y`: F
- `z0`: F
- `z1`: F
- returns: R:_Shape
- steps: enclosure

## vent_measure  (python vent_measure:5819; compiled line 23684)
- `solid`: R:_ReadingShape
- `outer`: T(F,F,F,F,F,F)
- `airway`: T(F,F,F,F)
- `sx`: F
- returns: D{slots:L[F],mullions:L[F],runs:L[F],tallest:F,open_mm2:F,band:T(F,F)} | D{slots:L[],mullions:L[],runs:L[],tallest:F,open_mm2:F,band:T(F,F)}
- steps: enclosure

## _flank_vents  (python _flank_vents:5867; compiled line 24122)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `airway`: T(F,F,F,F)
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- returns: R:_Shape
- steps: enclosure

## vent_readings  (python vent_readings:5917; compiled line 24535)
- `pieces`: D{front-bottom:R:_ReadingShape,front-top:R:_ReadingShape,back-bottom:R:_ReadingShape,back-top:R:_ReadingShape,pump-retainer:R:_ReadingShape}
- `box`: R:Box
- returns: D{F:D{slots:L[F],mullions:L[F],runs:L[F],tallest:F,open_mm2:F,band:T(F,F)}} | D{F:D{slots:L[],mullions:L[],runs:L[],tallest:F,open_mm2:F,band:T(F,F)}}
- steps: enclosure

## _core_stop_handhold_air  (python _core_stop_handhold_air:5937; compiled line 24723)
- `inner`: T(F,F,F,F,F,F)
- `station`: T(F,F,F)
- `band_end_y`: F
- returns: N
- steps: enclosure

## _core_stops  (python _core_stops:5957; compiled line 24909)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `stations`: T(T(F,F,F),T(F,F,F))
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- returns: R:_Shape
- steps: enclosure

## _core_holds  (python _core_holds:6002; compiled line 25199)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `stations`: T(T(F,F,F,F),T(F,F,F,F))
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- `face`: F | N
- returns: R:_Shape
- steps: enclosure

## _core_fit_pocket  (python _core_fit_pocket:6043; compiled line 25331)
- `box`: R:Box
- returns: R:_Shape
- steps: enclosure

## _asse_cradle  (python _asse_cradle:6165; compiled line 25639)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `station`: T()
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _valve_socket_cutters  (python _valve_socket_cutters:6330; compiled line 25799)
- `plane`: F
- `sign`: I
- `seat_x`: F
- `seat_z`: F
- returns: T(R:_Shape,R:_Shape,R:_Shape,R:_Shape)
- steps: enclosure

## _valve_trays  (python _valve_trays:6350; compiled line 25909)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `stations`: T(T(F,I,T(T(~,~),T(~,~),T(~,~),T(~,~))),T(F,I,T(T(~,~),T(~,~),T(~,~),T(~,~))))
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- `wall_aft_y`: F
- `flank_bed_z`: F | N
- `flank_runs`: L[T(F,F,F,F,F)] | T()
- `wells`: T()
- returns: R:_Shape
- steps: enclosure

## _flow_meter_anchors  (python _flow_meter_anchors:6488; compiled line 25980)
- `solid`: R:_Shape
- `roots`: T(F,F,F,F,F,F)
- `station`: T()
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## back_top_frames  (python back_top_frames:6703; compiled line 26318)
- returns: T(T(F,F,F,F,F,F),T(F,F,F,F,F,F))
- steps: enclosure-assembly

## _tube_anchors  (python _tube_anchors:6717; compiled line 26402)
- `solid`: R:_Shape
- `roots`: T(F,F,F,F,F,F)
- `lane`: T(F,F,F,F,F,F)
- `stations`: T()
- `y0`: F
- `y1`: F
- `z0`: F
- `z1`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _c14_tunnel_geometry  (python _c14_tunnel_geometry:6989; compiled line 26574)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `stations`: T()
- `ports`: T()
- `z0`: F
- `z1`: F
- `up`: F
- returns: N
- steps: enclosure

## keystone_pocket_width  (python keystone_pocket_width:7078; compiled line 26612)
- returns: F
- steps: enclosure

## _keystone_pocket_cut  (python _keystone_pocket_cut:7084; compiled line 26638)
- `x`: I
- `z`: F
- `y_face`: F
- `back`: F
- returns: T(R:_Shape,T(F,F))
- steps: enclosure

## _keystone_receptacle_geometry  (python _keystone_receptacle_geometry:7133; compiled line 27149)
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `station`: N
- `z0`: F
- `z1`: F
- `up`: F
- returns: N
- steps: enclosure

## _keystone_receptacle  (python _keystone_receptacle:7219; compiled line 28009)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `station`: N
- `z0`: F
- `z1`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _c14_tunnel  (python _c14_tunnel:7247; compiled line 28122)
- `solid`: R:_Shape
- `inner`: T(F,F,F,F,F,F)
- `outer`: T(F,F,F,F,F,F)
- `stations`: T()
- `ports`: T()
- `z0`: F
- `z1`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## _piece_bands  (python _piece_bands:7265; compiled line 28214)
- `box`: R:Box
- `name`: S
- returns: T(F,F,F,F)
- steps: enclosure

## _seam_fit_reliefs  (python _seam_fit_reliefs:7279; compiled line 28320)
- `piece`: R:_Shape
- `box`: R:Box
- `y_side`: S
- `z_side`: S
- returns: R:_Shape
- steps: enclosure

## build_piece  (python build_piece:7300; compiled line 28338)
- `box`: R:Box
- `y_side`: S
- `z_side`: S
- `halves_cache`: D{back:R:_Shape} | D{front:R:_Shape}
- returns: R:_Shape
- steps: enclosure

## _report_facet  (python _report_facet:7635; compiled line 28528)
- `half`: R:_ReadingShape
- `box`: R:Box
- returns: N
- steps: enclosure

## _report_split  (python _report_split:7666; compiled line 29013)
- `pieces`: D{front-bottom:R:_ReadingShape,front-top:R:_ReadingShape,back-bottom:R:_ReadingShape,back-top:R:_ReadingShape,pump-retainer:R:_ReadingShape}
- `core`: N
- `box`: R:Box
- `installed_retainer`: R:_ReadingShape
- returns: N
- steps: enclosure

## _report_seams  (python _report_seams:7689; compiled line 29042)
- `box`: R:Box
- returns: N
- steps: enclosure

## y_stack_figures  (python y_stack_figures:7699; compiled line 29158)
- `inner`: R:list | T(F,F,F,F,F,F)
- returns: D{S:S}
- steps: enclosure, enclosure-mechanical-sync

## _report_stacks  (python _report_stacks:7725; compiled line 29455)
- `box`: R:Box
- returns: N
- steps: enclosure

## _report_slide  (python _report_slide:7737; compiled line 29664)
- `pieces`: D{front-bottom:R:_ReadingShape,front-top:R:_ReadingShape,back-bottom:R:_ReadingShape,back-top:R:_ReadingShape,pump-retainer:R:_ReadingShape}
- `box`: R:Box
- returns: D{front:T(T(F,F),F,I,F),back:T(T(F,F),F,I,F)}
- steps: enclosure

## flat_bearing_area  (python _report_slide.<locals>.flat_bearing_area:7859; compiled line 29711)
- `solid`: R:_ReadingShape
- `z`: F
- `normal_z`: F
- `top_side`: B
- returns: F
- steps: enclosure

## _handhold_bound  (python _handhold_bound:7953; compiled line 29785)
- `pieces`: D{front-bottom:R:_ReadingShape,front-top:R:_ReadingShape,back-bottom:R:_ReadingShape,back-top:R:_ReadingShape,pump-retainer:R:_ReadingShape} | R:dict
- `box`: R:Box
- returns: R:Bound
- steps: enclosure, enclosure-assembly

## missing  (python _handhold_bound.<locals>.missing:7962; compiled line 29792)
- `shape`: R:_ReadingShape
- returns: R:_ReadingShape
- steps: enclosure, enclosure-assembly

## _ceiling_show_cap_bound  (python _ceiling_show_cap_bound:8015; compiled line 29823)
- `back_top`: R:_ReadingShape
- `box`: R:Box
- returns: R:Bound
- steps: enclosure

## _silhouette_bound  (python _silhouette_bound:8040; compiled line 29835)
- `pieces`: D{front-bottom:R:_ReadingShape,front-top:R:_ReadingShape,back-bottom:R:_ReadingShape,back-top:R:_ReadingShape,pump-retainer:R:_ReadingShape}
- `box`: R:Box
- returns: R:Bound
- steps: enclosure

## stated_box  (python stated_box:8098; compiled line 29886)
- `pack`: R:Pack
- `readings`: R:BoxReadings
- returns: R:Box
- steps: enclosure-box

## _report_columns  (python _report_columns:8109; compiled line 29912)
- `box`: R:Box
- returns: N
- steps: enclosure

## _report_bounds  (python _report_bounds:8124; compiled line 30093)
- returns: N
- steps: enclosure

## _write_docs  (python _write_docs:8141; compiled line 30107)
- `box`: R:Box
- `vent_read`: D{F:D{slots:L[F],mullions:L[F],runs:L[F],tallest:F,open_mm2:F,band:T(F,F)}}
- returns: N
- steps: enclosure

## _borne  (python _write_docs.<locals>._borne:8173; compiled line 30118)
- `run`: T(F,F,F,F,F)
- returns: F
- steps: enclosure

## r  (python ?; compiled line 30131)
- `seg`: F
- returns: S
- steps: enclosure

## <lambda>  (python ?; compiled line 30132)
- `v`: F
- returns: S
- steps: enclosure

## r  (python ?; compiled line 30133)
- `tall`: F
- `thin`: F
- returns: S
- steps: enclosure

## r  (python ?; compiled line 30134)
- `tall`: F
- `thin`: F
- returns: S
- steps: enclosure

## r  (python ?; compiled line 30135)
- `arc`: F
- `pitch`: F
- returns: S
- steps: enclosure

## _reading_bounds  (python _reading_bounds:8399; compiled line 30184)
- `lower`: R:list
- `upper`: R:list
- returns: R:_ReadingBounds
- steps: enclosure-box

## _box_bound_rows  (python _box_bound_rows:8404; compiled line 30217)
- `placed`: R:dict
- `bounds`: R:dict
- returns: L[R:_ReadingBounds]
- steps: enclosure-box

## _box_question_frame  (python _box_question_frame:8411; compiled line 30301)
- `bounds`: D{S:R:list} | D{S:T(T(F,F,F),T(F,F,F))}
- returns: T(T(F,F,F,F,F,F),F,T(F,F))
- steps: enclosure-box

## _lip_lane_boxes  (python _lip_lane_boxes:8420; compiled line 30422)
- `inner`: T(F,F,F,F,F,F)
- `y_span`: T(F,F)
- `plate`: R:dict
- `y_joint`: F
- returns: L[T(F,F,F,F,F,F)] | L[]
- steps: enclosure-box

## _lip_lane_tool  (python _lip_lane_tool:8436; compiled line 30612)
- `inner`: T(F,F,F,F,F,F)
- `y_span`: T(F,F)
- `plate`: R:dict
- `y_joint`: F
- returns: N | R:_ReadingShape
- steps: enclosure-box

## _floor_section_tool  (python _floor_section_tool:8444; compiled line 30685)
- `bounds`: R:_ReadingBounds
- `boss`: T(F,F,F,F)
- returns: R:_ReadingShape
- steps: enclosure-box

## _under_lip_tool  (python _under_lip_tool:8449; compiled line 30735)
- `inner`: T(F,F,F,F,F,F)
- `y_joint`: F
- `splits`: T(F,F)
- `pump_trays`: T(T(F,F,F),T(F,F,F))
- `column`: I
- returns: R:_ReadingShape
- steps: enclosure-box

## box_question_tools  (python box_question_tools:8463; compiled line 30925)
- `pack`: R:Pack
- `bounds`: D{S:R:list}
- returns: T(D{S:N|R:_ReadingShape},L[D{family:S,key:T(~,~),tool:S,body:S,body_first:B,positive_components:B}])
- steps: enclosure-box

## add  (python box_question_tools.<locals>.add:8474; compiled line 31005)
- `family`: S
- `key`: T(I,I,S) | T(I,S) | T(S,I) | T(S,S)
- `tool_name`: S
- `body`: S
- `body_first`: B
- `components`: B
- returns: N
- steps: enclosure-box

