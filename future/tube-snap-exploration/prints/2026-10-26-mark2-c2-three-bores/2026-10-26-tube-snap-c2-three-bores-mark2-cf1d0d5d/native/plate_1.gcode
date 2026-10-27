; HEADER_BLOCK_START
; BambuStudio 02.08.02.61
; model printing time: 9m 1s; total estimated time: 14m 12s
; total layer number: 47
; total filament length [mm] : 1283.09
; total filament volume [cm^3] : 3086.19
; total filament weight [g] : 3.98
; filament_density: 1.29
; filament_diameter: 1.75
; max_z_height: 11.24
; filament: 1
; support_material_on_wipe_tower: 0
; HEADER_BLOCK_END

; CONFIG_BLOCK_START
; accel_to_decel_enable = 0
; accel_to_decel_factor = 50%
; activate_air_filtration = 0
; additional_cooling_fan_speed = 0
; additional_fan_full_speed_layer = 0
; alternate_extra_wall = 0
; ams_filament_load_time_ams = 0
; ams_filament_load_time_ams_lite = 0
; ams_filament_load_time_n3f_s = 0
; ams_filament_unload_time_ams = 0
; ams_filament_unload_time_ams_lite = 0
; ams_filament_unload_time_n3f_s = 0
; apply_scarf_seam_on_circles = 1
; auxiliary_fan = 1
; avoid_crossing_wall_includes_support = 0
; bed_custom_model = 
; bed_custom_texture = 
; bed_exclude_area = 
; bed_heat_soak_area = 
; bed_temperature_formula = by_highest_temp
; before_layer_change_gcode = 
; best_object_pos = 0.3,0.5
; bottom_color_penetration_layers = 3
; bottom_shell_layers = 3
; bottom_shell_thickness = 0
; bottom_surface_density = 100%
; bottom_surface_pattern = monotonic
; bridge_angle = 0
; bridge_flow = 1
; bridge_no_support = 0
; bridge_speed = 50,50
; brim_object_gap = 0.1
; brim_type = auto_brim
; brim_width = 5
; chamber_temperatures = 0
; change_filament_gcode = ;======== H2C filament_change ========\n;===== 20260413 =====\nM993 A2 B2 C2 ; nozzle cam detection allow status save.\nM993 A0 B0 C0 ; nozzle cam detection not allowed.\n\n{if (filament_type[next_filament_id] == \"PLA\") ||  (filament_type[next_filament_id] == \"PETG\")\n ||  (filament_type[next_filament_id] == \"PLA-CF\")  ||  (filament_type[next_filament_id] == \"PETG-CF\")}\nM1015.4 S1 K0 ;disable E air printing detect\n{else}\nM1015.4 S0 ; disable E air printing detect\n{endif}\n\nM620 S[next_filament_id]A H[next_hotend]\nM1002 gcode_claim_action : 4\nM204 S9000\n\nG1 Z{max_layer_z + 3.0} F1200\n\nM400\nM106 P1 S0\nM106 P2 S0\n\n{if toolchange_count == 2}\n; get travel path for change filament\n;M620.1 X[travel_point_1_x] Y[travel_point_1_y] F21000 P0\n;M620.1 X[travel_point_2_x] Y[travel_point_2_y] F21000 P1\n;M620.1 X[travel_point_3_x] Y[travel_point_3_y] F21000 P2\n{endif}\n\n{if wipe_tower_center_pos_valid}\n    M620.14 X[wipe_tower_center_pos_x] Y[wipe_tower_center_pos_y]\n{else}\n    M620.14 X95.5 Y336\n{endif}\n\n{if ((filament_type[current_filament_id] == \"PLA\") || (filament_type[current_filament_id] == \"PLA-CF\") || (filament_type[current_filament_id] == \"PETG\")) && (nozzle_diameter_at_nozzle_id[current_nozzle_id] == 0.2)}\nM620.10 A0 F74.8347 L[flush_length] H{nozzle_diameter_at_nozzle_id[current_nozzle_id]} T{flush_temperatures[current_filament_id]} P[old_filament_temp] S1\n{else}\nM620.10 A0 F{flush_volumetric_speeds[current_filament_id]/2.4053*60*0.8} L[flush_length] H{nozzle_diameter_at_nozzle_id[current_nozzle_id]} T{flush_temperatures[current_filament_id]} P[old_filament_temp] S1\n{endif}\n\n{if ((filament_type[next_filament_id] == \"PLA\") || (filament_type[next_filament_id] == \"PLA-CF\") || (filament_type[next_filament_id] == \"PETG\")) && (nozzle_diameter_at_nozzle_id[next_nozzle_id] == 0.2)}\nM620.10 A1 F74.8347 L[flush_length] H{nozzle_diameter_at_nozzle_id[next_nozzle_id]} T{flush_temperatures[next_filament_id]} P[new_filament_temp] S1\n{else}\nM620.10 A1 F{flush_volumetric_speeds[next_filament_id]/2.4053*60*0.8} L[flush_length] H{nozzle_diameter_at_nozzle_id[next_nozzle_id]} T{flush_temperatures[next_filament_id]} P[new_filament_temp] S1\n{endif}\n\n{if long_retraction_when_cut}\nM620.11 P1 I[current_filament_id] B[current_hotend] E-{retraction_distance_when_cut} F{max((flush_volumetric_speeds[current_filament_id]/2.4053*60), 200)}\n{else}\nM620.11 P0 I[current_filament_id] B[current_hotend] E0\n{endif}\n\n\nM620.15 P[filament_pre_cooling_temperature_nc[next_filament_id]]\nM620.15 C{new_filament_temp - filament_cooling_before_tower[next_filament_id]}\nM620.11 O1 T[filament_retract_length_nc]\n\n{if long_retraction_when_ec}\nM620.11 K1 I[current_filament_id] B[current_hotend] R{retraction_distance_when_ec} F{max((flush_volumetric_speeds[current_filament_id]/2.4053*60), 200)}\n{else}\nM620.11 K0 I[current_filament_id] B[current_hotend] R0\n{endif}\n\nM620.15 C{new_filament_temp - filament_cooling_before_tower[next_filament_id]}\n\nM628 S1\n{if filament_type[current_filament_id] == \"TPU\"}\nM620.11 S0 L0 I[current_filament_id] B[current_hotend] E-{retraction_distances_when_cut[current_filament_id]} F{max((flush_volumetric_speeds[current_filament_id]/2.4053*60), 200)}\n{else}\n{if (filament_type[current_filament_id] == \"PA\") || (filament_type[current_filament_id] == \"PA-GF\")}\nM620.11 S1 L0 I[current_filament_id] B[current_hotend] R4 D2 E-{retraction_distances_when_cut[current_filament_id]} F{max((flush_volumetric_speeds[current_filament_id]/2.4053*60), 200)}\n{else}\nM620.11 S1 L0 I[current_filament_id] B[current_hotend] R10 D8 E-{retraction_distances_when_cut[current_filament_id]} F{max((flush_volumetric_speeds[current_filament_id]/2.4053*60), 200)}\n{endif}\n{endif}\nM629\n\n{if (filament_type[current_filament_id] == \"TPU\") && (filament_map[current_filament_id] == 2) && (nozzle_volume_types[current_nozzle_id] != \"TPU High Flow\")}\nM620.11 H2 C331\n{else}\nM620.11 H0\n{endif}\n\n{if  (nozzle_volume_types[current_nozzle_id] == \"TPU High Flow\") && (filament_map[current_filament_id] == 2) && (filament_map[next_filament_id] == 1)}\n;sw from R2L&TPU kit, travel run a distance for sketch TPU\nG1 X30 Y30 F5000\nM400\nG1 X300 Y30 F5000\nM400\n{endif}\n\nT[next_filament_id] H[next_hotend]\n\n;deretract\n{if filament_type[next_filament_id] == \"TPU\"}\n{else}\n{if (filament_type[next_filament_id] == \"PA\") || (filament_type[next_filament_id] == \"PA-GF\")}\n;VG1 E1 F{max(new_filament_e_feedrate, 200)}\n;VG1 E1 F{max(new_filament_e_feedrate/2, 100)}\n{else}\n;VG1 E4 F{max(new_filament_e_feedrate, 200)}\n;VG1 E4 F{max(new_filament_e_feedrate/2, 100)}\n{endif}\n{endif}\n\n; VFLUSH_START\n\n{if flush_length>41.5}\n;VG1 E41.5 F{min(old_filament_e_feedrate,new_filament_e_feedrate)}\n;VG1 E{flush_length-41.5} F{new_filament_e_feedrate}\n{else}\n;VG1 E{flush_length} F{min(old_filament_e_feedrate,new_filament_e_feedrate)}\n{endif}\n\nSYNC T{ceil(flush_length / 125) * 5}\n\n; compensate for heating and cooling\n{if flush_length > 0}\n{if flush_temperatures[next_filament_id] > new_filament_temp}\nSYNC T{(flush_temperatures[next_filament_id]-(new_filament_temp - filament_cooling_before_tower[next_filament_id]))/hotend_cooling_rate[filament_map[next_filament_id]-1]}\nSYNC T{(flush_temperatures[next_filament_id]-(new_filament_temp - filament_cooling_before_tower[next_filament_id]))/hotend_heating_rate[filament_map[next_filament_id]-1]}\n{else}\nSYNC T{(new_filament_temp - filament_cooling_before_tower[next_filament_id] -flush_temperatures[next_filament_id])/hotend_cooling_rate[filament_map[next_filament_id]-1]}\nSYNC T{(new_filament_temp - filament_cooling_before_tower[next_filament_id] -flush_temperatures[next_filament_id])/hotend_heating_rate[filament_map[next_filament_id]-1]}\n{endif}\n{endif}\n\n; VFLUSH_END\n\nM1002 set_filament_type:{filament_type[next_filament_id]}\n\nM400\nM83\n{if next_filament_id < 255}\n\n\nM620.10 R{new_extruder_retracted_length}\n\n{if (print_sequence == \"by object\" && !has_wipe_tower)}\nM628 S0 F1 L10.0\n; VFLUSH_START\n;VG1 E10 F[new_filament_e_feedrate]\n; VFLUSH_END\n{else}\nM628 S0\n{endif}\n;VM109 S[new_filament_temp]\n\nM629\nM400\n\n;prime_tower_interface\n{if is_prime_tower_interface && filament_tower_interface_purge_volume !=0}\nG150.1\nM620.13 W0 L{filament_tower_interface_purge_volume} T{filament_tower_interface_print_temp} R0.0\n{endif}\n;prime_tower_interface\n\nM983.3 F{filament_max_volumetric_speed[next_filament_id]/2.4} A0.4 R{new_extruder_retracted_length}\n\n\nM400\n{if wipe_avoid_perimeter}\nG387 Y320 J1 F10000\nG1 X{wipe_avoid_pos_x} F30000\n{endif}\nG387 Y295 J1 F30000\nG387 Y265 J1 F18000\nG1 Z{max_layer_z + 3.0} F3000\n{if layer_z <= (initial_layer_print_height + 0.001)}\nM204 S[initial_layer_acceleration]\n{else}\nM204 S[default_acceleration]\n{endif}\n{else}\nG1 X[x_after_toolchange] Y[y_after_toolchange] Z[z_after_toolchange] F12000\n{endif}\nM621 S[next_filament_id]A\n\nM622.1 S0 ;for prev version, default skip\nM1002 judge_flag powerloss_resume_flag\nM622 J1\nM983.3 F{filament_max_volumetric_speed[next_filament_id]/2.4} A0.4 R{new_extruder_retracted_length}\nM400\n{if wipe_avoid_perimeter}\nG387 Y320 J1 F10000\nG1 X{wipe_avoid_pos_x} F30000\n{endif}\nG387 Y295 J1 F30000\nG387 Y265 J1 F18000\nG1 Z{max_layer_z + 3.0} F3000\n{if layer_z <= (initial_layer_print_height + 0.001)}\nM204 S[initial_layer_acceleration]\n{else}\nM204 S[default_acceleration]\n{endif}\nM1002 set_flag powerloss_resume_flag=0\nM623\n\nM993 A3 B3 C3 ; nozzle cam detection allow status restore.\n\n{if (filament_type[next_filament_id]  == \"TPU\")}\nM1015.3 S1;enable tpu clog detect\n{else}\nM1015.3 S0;disable tpu clog detect\n{endif}\n\n{if (filament_type[next_filament_id] == \"PLA\") ||  (filament_type[next_filament_id] == \"PETG\")\n ||  (filament_type[next_filament_id] == \"PLA-CF\")  ||  (filament_type[next_filament_id] == \"PETG-CF\")}\nM1015.4 S1 K1 H{nozzle_diameter_at_nozzle_id[next_nozzle_id]} ;enable E air printing detect\n{else}\nM1015.4 S0 ; disable E air printing detect\n{endif}\n\nM620.6 I[next_filament_id] H[next_hotend] W1 ;enable ams air printing detect\nM620 O{toolchange_count + 1}\nM1002 gcode_claim_action : 0
; circle_compensation_manual_offset = 0
; circle_compensation_speed = 200
; close_additional_fan_first_x_layers = 3
; close_fan_the_first_x_layers = 3
; complete_print_exhaust_fan_speed = 70
; cool_plate_temp = 0
; cool_plate_temp_initial_layer = 0
; cooling_filter_enabled = 0
; cooling_perimeter_transition_distance = 10
; cooling_slowdown_logic = uniform_cooling
; counter_coef_1 = 0
; counter_coef_2 = -0.0004
; counter_coef_3 = -0.0156
; counter_limit_max = -0.015
; counter_limit_min = -0.025
; counterbore_hole_bridging = none
; curr_bed_type = Textured PEI Plate
; default_acceleration = 8000,8000
; default_ams_type = -1
; default_filament_colour = ""
; default_filament_profile = "Bambu PLA Basic @BBL H2C"
; default_jerk = 0
; default_nozzle_volume_type = Standard,Standard
; default_print_profile = 0.20mm Standard @BBL H2C
; deretraction_speed = 30,30
; detect_floating_vertical_shell = 1
; detect_narrow_internal_solid_infill = 1
; detect_overhang_wall = 1
; detect_thin_wall = 0
; diameter_limit = 50
; different_settings_to_system = enable_arc_fitting;enable_support;support_bottom_z_distance;support_line_width;support_object_xy_distance;support_top_z_distance;chamber_temperatures;compatible_printers;eng_plate_temp;eng_plate_temp_initial_layer;fan_max_speed;fan_min_speed;filament_cost;filament_max_volumetric_speed;hot_plate_temp;hot_plate_temp_initial_layer;nozzle_temperature;nozzle_temperature_initial_layer;nozzle_temperature_range_high;overhang_fan_speed;slow_down_min_speed;supertack_plate_temp;supertack_plate_temp_initial_layer;textured_plate_temp;textured_plate_temp_initial_layer;machine_start_gcode
; draft_shield = disabled
; during_print_exhaust_fan_speed = 70
; elefant_foot_compensation = 0.15
; embedding_wall_into_infill = 0
; enable_arc_fitting = 0
; enable_circle_compensation = 0
; enable_filament_dynamic_map = 0
; enable_height_slowdown = 0,0
; enable_long_retraction_when_cut = 2
; enable_mixed_color_sublayer = 0
; enable_order_independent_overlap_carving = 0
; enable_overhang_bridge_fan = 1
; enable_overhang_speed = 1,1
; enable_pre_heating = 1
; enable_pressure_advance = 0
; enable_prime_tower = 1
; enable_support = 1
; enable_support_ironing = 0
; enable_tower_interface_features = 1
; enable_wrapping_detection = 0
; enforce_support_layers = 0
; eng_plate_temp = 80
; eng_plate_temp_initial_layer = 80
; ensure_vertical_shell_thickness = enabled
; exclude_object = 1
; extruder_ams_count = 1#0|4#1;1#0|4#1
; extruder_clearance_dist_to_rod = 50
; extruder_clearance_height_to_lid = 201
; extruder_clearance_height_to_rod = 47.4
; extruder_clearance_max_radius = 96
; extruder_colour = #018001;#018001
; extruder_max_nozzle_count = 1,6
; extruder_nozzle_stats = Standard#1;Standard#1
; extruder_nozzle_stats_new = Standard#1;Standard#1
; extruder_offset = 0x0,0x0
; extruder_printable_area = 0x0,325x0,325x320,0x320#25x0,330x0,330x320,25x320
; extruder_printable_height = 320,325
; extruder_type = Direct Drive,Direct Drive
; extruder_variant_list = "Direct Drive Standard,Direct Drive High Flow,Direct Drive E3D High Flow";"Direct Drive Standard,Direct Drive High Flow"
; fan_cooling_layer_time = 80
; fan_direction = left
; fan_max_speed = 0
; fan_min_speed = 0
; farthest_point_timelapse = 1
; filament_adaptive_volumetric_speed = 0
; filament_adhesiveness_category = 800
; filament_bridge_speed = 25
; filament_change_length = 4
; filament_change_length_nc = 4
; filament_colour = #161616
; filament_colour_type = 2
; filament_cooling_before_tower = 10
; filament_cost = 44.99
; filament_density = 1.29
; filament_dev_ams_drying_ams_limitations = 1
; filament_dev_ams_drying_heat_distortion_temperature = 165
; filament_dev_ams_drying_temperature = 65,80,65,80
; filament_dev_ams_drying_time = 12,12,12,12
; filament_dev_chamber_drying_bed_temperature = 90
; filament_dev_chamber_drying_time = 12
; filament_dev_drying_cooling_temperature = 150
; filament_dev_drying_softening_temperature = 150
; filament_diameter = 1.75
; filament_enable_overhang_speed = 1
; filament_end_gcode = "; filament end gcode \n"
; filament_extruder_compatibility = 0
; filament_extruder_variant = "Direct Drive Standard"
; filament_flow_ratio = 0.9555
; filament_flush_temp = 0
; filament_flush_temp_fast = 0
; filament_flush_volumetric_speed = 0
; filament_ids = GFT01
; filament_is_mixed = 0
; filament_is_support = 0
; filament_map = 1
; filament_map_2 = 0
; filament_map_mode = Auto For Flush
; filament_max_volumetric_speed = 18
; filament_metal_stickiness = High
; filament_minimal_purge_on_wipe_tower = 15
; filament_mixed_components = ""
; filament_mixed_gradient = 0
; filament_mixed_gradient_curve = ""
; filament_mixed_gradient_per_part = 0
; filament_mixed_gradient_range = ""
; filament_mixed_sublayer_ratios = ""
; filament_multi_colour = #000000
; filament_notes = 
; filament_nozzle_map = 0
; filament_overhang_1_4_speed = 0
; filament_overhang_2_4_speed = 35
; filament_overhang_3_4_speed = 35
; filament_overhang_4_4_speed = 10
; filament_overhang_totally_speed = 10
; filament_pre_cooling_temperature = 0
; filament_pre_cooling_temperature_nc = 230
; filament_preheat_temperature_delta = 20
; filament_prime_volume = 45
; filament_prime_volume_nc = 30
; filament_printable = 1
; filament_ramming_travel_time = 0
; filament_ramming_travel_time_nc = 1
; filament_ramming_volumetric_speed = -1
; filament_ramming_volumetric_speed_nc = -1
; filament_retract_length_nc = 14
; filament_scarf_gap = 0%
; filament_scarf_height = 10%
; filament_scarf_length = 10
; filament_scarf_seam_type = none
; filament_self_index = 1
; filament_settings_id = "Polymaker PET-GF @BBL H2C"
; filament_shrink = 100%
; filament_soluble = 0
; filament_start_gcode = "; filament start gcode\n"
; filament_tower_interface_pre_extrusion_dist = 10
; filament_tower_interface_pre_extrusion_length = 0
; filament_tower_interface_print_temp = -1
; filament_tower_interface_purge_volume = 20
; filament_tower_ironing_area = 4
; filament_type = PET-CF
; filament_velocity_adaptation_factor = 1
; filament_vendor = "Bambu Lab"
; filament_volume_map = 0
; filename_format = {input_filename_base}_{filament_type[0]}_{print_time}.gcode
; fill_multiline = 1
; filter_out_gap_fill = 0
; first_layer_print_sequence = 0
; first_x_layer_fan_speed = 0
; first_x_layer_part_fan_speed = 0
; flush_into_infill = 0
; flush_into_objects = 0
; flush_into_support = 0
; flush_multiplier = 1,1
; flush_multiplier_fast = 1.2,1.2
; flush_volumes_matrix = 0,0
; flush_volumes_vector = 140,140
; full_fan_speed_layer = 0
; fuzzy_skin = none
; fuzzy_skin_first_layer = 0
; fuzzy_skin_mode = displacement
; fuzzy_skin_noise_type = classic
; fuzzy_skin_octaves = 4
; fuzzy_skin_persistence = 0.5
; fuzzy_skin_point_distance = 0.8
; fuzzy_skin_scale = 1
; fuzzy_skin_thickness = 0.3
; gap_infill_speed = 250,250
; gcode_add_line_number = 0
; gcode_flavor = marlin
; grab_length = 0,0
; group_algo_with_time = 0
; has_filament_switcher = 0
; has_scarf_joint_seam = 0
; head_wrap_detect_zone = 
; hole_coef_1 = 0
; hole_coef_2 = -0.0003
; hole_coef_3 = 0.1741
; hole_limit_max = 0.174
; hole_limit_min = 0.167
; host_type = octoprint
; hot_plate_temp = 80
; hot_plate_temp_initial_layer = 80
; hotend_cooling_rate = 1.6,3.4
; hotend_heating_rate = 3.5,13.3
; impact_strength_z = 4.5
; independent_support_layer_height = 1
; infill_combination = 0
; infill_direction = 45
; infill_instead_top_bottom_surfaces = 0
; infill_jerk = 9
; infill_lock_depth = 1
; infill_rotate_step = 0
; infill_shift_step = 0.4
; infill_wall_overlap = 15%
; inherits_group = "0.24mm Standard @BBL H2C";"Bambu PET-CF @BBL H2C";"Bambu Lab H2C 0.4 nozzle"
; initial_layer_acceleration = 500,500
; initial_layer_flow_ratio = 1
; initial_layer_infill_speed = 105,105
; initial_layer_jerk = 9
; initial_layer_line_width = 0.5
; initial_layer_print_height = 0.2
; initial_layer_speed = 50,50
; initial_layer_travel_acceleration = 6000,6000
; inner_wall_acceleration = 0,0
; inner_wall_jerk = 9
; inner_wall_line_width = 0.45
; inner_wall_speed = 300,300
; interface_shells = 0
; interlocking_beam = 0
; interlocking_beam_layer_count = 2
; interlocking_beam_width = 0.8
; interlocking_boundary_avoidance = 2
; interlocking_depth = 2
; interlocking_orientation = 22.5
; internal_bridge_support_thickness = 0.8
; internal_solid_infill_line_width = 0.42
; internal_solid_infill_pattern = zig-zag
; internal_solid_infill_speed = 250,250
; ironing_direction = 45
; ironing_fan_speed = -1
; ironing_flow = 10%
; ironing_inset = 0.21
; ironing_pattern = zig-zag
; ironing_spacing = 0.15
; ironing_speed = 30
; ironing_type = no ironing
; is_infill_first = 0
; layer_change_gcode = ; layer num/total_layer_count: {layer_num+1}/[total_layer_count]\n; update layer progress\nM73 L{layer_num+1}\nM991 S0 P{layer_num} ;notify layer change
; layer_height = 0.24
; line_width = 0.42
; locked_skeleton_infill_pattern = zigzag
; locked_skin_infill_pattern = crosszag
; long_retractions_when_cut = 1,1
; long_retractions_when_ec = 1
; machine_bed_mass_Y = 0
; machine_end_gcode = ;===== machine: H2C end =====\n;====== date: 20260729 ======\n\nM1003 S0\nM73 P100 R0\n\nG392 S0 ;turn off nozzle clog detect\nM993 A0 B0 C0 ; nozzle cam detection not allowed.\n\nM400 ; wait for buffer to clear\nG92 E0 ; zero the extruder\nM211 Z1\nM640.2 R0\n\nG90\nG1 Z{max_layer_z + 0.4} F900 ; lower z a little\nM1002 judge_flag timelapse_record_flag\nM622 J1\n    G150.3\n    M400 ; wait all motion done\n    M991 S0 P-1 ;end smooth timelapse at safe pos\n    M400 S5 ;wait for last picture to be taken\nM623  ;end of \"timelapse_record_flag\"\n\nG90\nG1 Z{max_layer_z + 10} F900 ; lower z a little\n\nG90\nM141 S0 ; turn off chamber heating\nM140 S0 ; turn off bed\nM106 S0 ; turn off fan\nM106 P2 S0 ; turn off remote part cooling fan\nM106 P3 S0 ; turn off chamber cooling fan\nM106 P9 S0 ; turn off ext toodhead cooling fan\n\n; pull back filament to AMS\nM620 S65535\n{if long_retraction_when_cut}\nM620.11 P1 I[current_filament_id] B[current_hotend] E-{retraction_distance_when_cut} F{max((flush_volumetric_speeds[current_filament_id]/2.4053*60), 200)}\n{else}\nM620.11 P0 I[current_filament_id] B[current_hotend] E0\n{endif}\n\n{if long_retraction_when_ec}\nM620.11 K1 I[current_filament_id] B[current_hotend] R{retraction_distance_when_ec} F{max((flush_volumetric_speeds[current_filament_id]/2.4053*60), 200)}\n{else}\nM620.11 K0 I[current_filament_id] B[current_hotend] R0\n{endif}\n\nM620.11 P1 I[current_filament_id] B[current_hotend] E-14\nT65535\nG150.2\nM621 S65535\n\nM620 S65279\nT65279\nG150.2\nM621 S65279\n\nG150.3\n\nM104 S0 T0; turn off hotend\nM104 S0 T1; turn off hotend\n\nM400 ; wait all motion done\nM17 S\nM17 Z0.4 ; lower z motor current to reduce impact if there is something in the bottom\n{if (100.0 - max_layer_z/2) > 0}\n    {if (max_layer_z + 100.0 - max_layer_z/2) < 320}\n        G1 Z{max_layer_z + 100.0 - max_layer_z/2} F600\n        G1 Z{max_layer_z + 98.0 - max_layer_z/2}\n    {else}\n        G1 Z320 F600\n        G1 Z320\n    {endif}\n{else}\n    {if (max_layer_z + 4.0) < 320}\n        G1 Z{max_layer_z + 4.0} F600\n        G1 Z{max_layer_z + 2.0}\n    {else}\n        G1 Z320 F600\n        G1 Z320\n    {endif}\n{endif}\nM400 P100\nM17 R ; restore z current\n\nM220 S100  ; Reset feedrate magnitude\nM201.2 K1.0 ; Reset acc magnitude\nM73.2   R1.0 ;Reset left time magnitude\nM1002 set_gcode_claim_speed_level : 0\n\nM1015.4 S0 K0 ;disable air printing detect\n\n\n;=====printer finish air purification=========\nM622.1 S0\nM1002 judge_flag print_finish_air_filt_flag\n\nM622 J1\nM1002 gcode_claim_action : 66\nM145 P1\nM106 P6 S255\nM400 S180\nM106 P6 S0\nM623\n\nM622 J2\nM1002 gcode_claim_action : 66\nM145 P0\nM106 P3 S127\nM400 S180\nM106 P3 S0\nM623\n;=====printer finish air purification=========\n\n;=====printer finish  sound=========\nM17\nM400 S1\nM1006 S1\nM1006 A53 B10 L99 C53 D10 M99 E53 F10 N99\nM1006 A57 B10 L99 C57 D10 M99 E57 F10 N99\nM1006 A0 B15 L0 C0 D15 M0 E0 F15 N0\nM1006 A53 B10 L99 C53 D10 M99 E53 F10 N99\nM1006 A57 B10 L99 C57 D10 M99 E57 F10 N99\nM1006 A0 B15 L0 C0 D15 M0 E0 F15 N0\nM1006 A48 B10 L99 C48 D10 M99 E48 F10 N99\nM1006 A0 B15 L0 C0 D15 M0 E0 F15 N0\nM1006 A60 B10 L99 C60 D10 M99 E60 F10 N99\nM1006 W\n;=====printer finish  sound=========\nM400\nM18\n\n
; machine_hotend_change_time = 0
; machine_load_filament_time = 15
; machine_max_acceleration_e = 5000,5000,5000,5000
; machine_max_acceleration_extruding = 20000,20000,20000,20000
; machine_max_acceleration_retracting = 5000,5000,5000,5000
; machine_max_acceleration_travel = 9000,9000,9000,9000
; machine_max_acceleration_x = 20000,20000,20000,20000
; machine_max_acceleration_y = 20000,20000,20000,20000
; machine_max_acceleration_z = 500,500,500,500
; machine_max_force_Y = 0
; machine_max_jerk_e = 2.5,2.5,2.5,2.5
; machine_max_jerk_x = 9,9,9,9
; machine_max_jerk_y = 9,9,9,9
; machine_max_jerk_z = 3,3,3,3
; machine_max_printed_mass = 0
; machine_max_speed_e = 50,50,50,50
; machine_max_speed_x = 1000,1000,1000,1000
; machine_max_speed_y = 1000,1000,1000,1000
; machine_max_speed_z = 30,30,30,30
; machine_min_extruding_rate = 0,0
; machine_min_travel_rate = 0,0
; machine_pause_gcode = M400 U1
; machine_prepare_compensation_time = 260
; machine_start_gcode = ;===== machine: H2C =========================\n;===== date: 20260608 =====================\n\n;M1002 set_flag extrude_cali_flag=1\n;M1002 set_flag g29_before_print_flag=1\n;M1002 set_flag auto_cali_toolhead_offset_flag=1\n;M1002 set_flag build_plate_detect_flag=1\n\nM993 A0 B0 C0 ; nozzle cam detection not allowed.\n\nM400\n;M73 P99\n\nM960 S10 P1 ; ext fan led\n\n;=====printer start sound ===================\nM17\nM400 S1\nM1006 S1\nM1006 A53 B9 L99 C53 D9 M99 E53 F9 N99\nM1006 A56 B9 L99 C56 D9 M99 E56 F9 N99\nM1006 A61 B9 L99 C61 D9 M99 E61 F9 N99\nM1006 A53 B9 L99 C53 D9 M99 E53 F9 N99\nM1006 A56 B9 L99 C56 D9 M99 E56 F9 N99\nM1006 A61 B18 L99 C61 D18 M99 E61 F18 N99\nM1006 W\n;=====printer start sound ===================\n\n;===== reset machine status =================\nM204 S10000\nM630 S0 P0\n\nG90\nM17 D ; reset motor current to default\nM960 S5 P1 ; turn on logo lamp\nG90\nM1002 set_gcode_claim_speed_level 5 ;Reset speed level\nM220 S100 ;Reset Feedrate\nM221 S100 ;Reset Flowrate\nM73.2   R1.0 ;Reset left time magnitude\nG29.1 Z{+0.0} ; clear z-trim value first\nM983.1 M1\nM901 D4\nM481 S0 ; turn off cutter pos comp\nG28.140 D0; reset pre-extrude z pos\n;===== reset machine status =================\n\nM620 M ;enable remap\nM620 N ;enable hotend remap\nM620 T0 ;print tmpr\nM620 T1 ;sn -> pos\nM620 T2 ;filament_id\n\n;===== start to heat heatbed & hotend==========\n\n    M104 O-80 A\n    M140 D[bed_temperature_initial_layer_single]\n\n;===== start to heat heatbead & hotend==========\n\n;===== avoid end stop =================\nG91\nG380 S2 Z42 F1200\nG380 S2 Z-12 F1200\nG90\n;===== avoid end stop =================\n\n;==== set airduct mode ====\n\n{if (overall_chamber_temperature >= 40)}\n\n    M145 P1 ; set airduct mode to heating mode for heating\n    M106 P2 S0 ; turn off auxiliary fan\n    M106 P3 S0 ; turn off chamber fan\n\n{else}\n    M145 P0 ; set airduct mode to cooling mode for cooling\n    M106 P2 S178 ; turn on auxiliary fan for cooling\n    M106 P3 S127 ; turn on chamber fan for cooling\n\n    M1002 gcode_claim_action : 29\n    M191 S0 ; wait for chamber temp\n    M106 P2 S0 ; turn off auxiliary fan\n    {if (min_vitrification_temperature <= 50)}\n        {if (nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2)}\n            M142 P1 R30 S35 T40 U0.3 V0.5 W0.8 O40 ; set PLA/TPU ND0.2 chamber autocooling\n        {else}\n            M142 P1 R30 S40 T45 U0.3 V0.5 W0.8 O45; set PLA/TPU ND0.4 chamber autocooling\n        {endif}\n    {else}\n        {if (!is_all_bbl_filament)}\n            M142 P1 R35 S40 T45 U0.3 V0.5 W0.8 O45 L1 ; set third-party PETG chamber autocooling\n        {else}\n            {if (nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2)}\n                M142 P1 R35 S45 T50 U0.3 V0.5 W0.8 O50 L1 ; set PETG ND0.2 chamber autocooling\n            {else}\n                M142 P1 R35 S50 T55 U0.3 V0.5 W0.8 O55 L1 ; set PETG ND0.4 chamber autocooling\n            {endif}\n        {endif}\n    {endif}\n{if(cooling_filter_enabled)}\nM145.2 P0 F0\n{else}\nM145.2 P0 F1\n{endif}\n{endif}\n;==== set airduct mode ====\n\n\n;====== cog noise reduction=================\nM982.2 S1 ; turn on cog noise reduction\n\n;===== first homing start =====\nM1002 gcode_claim_action : 13\n\nM640 S\nM640.1 R\nM641\nG28 X T300\nT1000\n\nG150.3\nM972 S24 P0 T2000 ; live-view camera foolproof\nM972 S46 P0 T5000 ; vortek anti-collision\nM640.1 S\nM640.4\n{if (first_non_support_filaments[0] != -1)}\nM640 S\nM640.8 T A{first_non_support_filaments[0]} H{first_non_support_hotend[0]}\nM640.7 L\nM641\n{endif}\n\n\n{if wipe_tower_center_pos_valid}\n    M620.14 X[wipe_tower_center_pos_x] Y[wipe_tower_center_pos_y]\n{else}\n    M620.14 X95.5 Y336\n{endif}\n\n\nG150.1 F18000 ; wipe mouth to avoid filament stick to heatbed\nG150.3 F18000\nM400 P200\n\nM1002 gcode_claim_action : 74 ; Heatbed surface foreign object detection\nM104 S0\n{if curr_bed_type==\"Textured PEI Plate\"}\nM972 S26 P0 C0\n{else}\nM972 S36 P0 C0 X1\n{endif}\nM972 S35 P0 C0\n\nM972 S41 P0 T5000 ; trash can anti-collision\n\nM1009 Q1 L1\nG91\nG380 S2 Z30 F1200 ; lower heatbed to move toolhead\nG90\nG1 X175 Y160 F30000\nG28 Z P0 T250\nM1009 Q1 L0\n\n\n;===== first homing end =====\n\n;===== detection start =====\n\nM1002 judge_flag build_plate_detect_flag\nM104 S0\nM622 S1\n    ;M1002 gcode_claim_action : 11 ; Indentifying build plate type\n    M972 S19 P0 C0    ; heatbed presence detection\n    M972 S31 P0 T5000 ; toolhead camera dirty detection\n    ;M1002 gcode_claim_action : 73 ; Build plate alignment detection\n    M972 S34 P0 T5000 ; heatbed plate offset detection\nM623\n\nM1002 gcode_claim_action : 72 ; Hotend Type Detection\nT1001\nM972 S14 P0 T5000 ; nozzle type detection\n\nM104 S{nozzle_temperature_initial_layer[initial_no_support_filament_id]} T{filament_map[initial_no_support_filament_id] % 2} ; rise temp in advance\n\nG151 P{filament_map[initial_no_support_filament_id] % 2} M ; plug the heat nozzle\n\n{if max_print_z >= 145}\nM1002 gcode_claim_action : 75 ; Heatbed underside foreign object detection\nG3811 Z{max_print_z}  ; Detect obstacles at the bottom of the heated bed\n{endif}\n\n;===== detection end =====\n\nM400\n;M73 P99\n\n;===== prepare print temperature and material ==========\nM400\nM211 X0 Y0 Z0 ;turn off soft endstop\nM975 S1 ; turn on input shaping\n\nG29.2 S0 ; avoid invalid abl data\n\n{if ((filament_type[initial_no_support_filament_id] == \"PLA\") || (filament_type[initial_no_support_filament_id] == \"PLA-CF\") || (filament_type[initial_no_support_filament_id] == \"PETG\")) && (nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2)}\nM620.10 A0 F74.8347 H{nozzle_diameter_at_nozzle_id[initial_nozzle_id]} T{flush_temperatures[initial_no_support_filament_id]} P{nozzle_temperature_initial_layer[initial_no_support_filament_id]} S1\nM620.10 A1 F74.8347 H{nozzle_diameter_at_nozzle_id[initial_nozzle_id]} T{flush_temperatures[initial_no_support_filament_id]} P{nozzle_temperature_initial_layer[initial_no_support_filament_id]} S1\n{else}\nM620.10 A0 F{flush_volumetric_speeds[initial_no_support_filament_id]/2.4053*60*0.8} H{nozzle_diameter_at_nozzle_id[initial_nozzle_id]} T{flush_temperatures[initial_no_support_filament_id]} P{nozzle_temperature_initial_layer[initial_no_support_filament_id]} S1\nM620.10 A1 F{flush_volumetric_speeds[initial_no_support_filament_id]/2.4053*60*0.8} H{nozzle_diameter_at_nozzle_id[initial_nozzle_id]} T{flush_temperatures[initial_no_support_filament_id]} P{nozzle_temperature_initial_layer[initial_no_support_filament_id]} S1\n{endif}\n\nM620.11 P1 I[initial_no_support_filament_id] B[initial_no_support_hotend] E0\n\n{if long_retraction_when_ec }\nM620.11 K1 I[initial_no_support_filament_id] B[initial_no_support_hotend] R{retraction_distance_when_ec} F{max((flush_volumetric_speeds[initial_no_support_filament_id]/2.4053*60), 200)}\n{else}\nM620.11 K0 I[initial_no_support_filament_id] B[initial_no_support_hotend] R0\n{endif}\n\nM628 S1\n{if filament_type[initial_no_support_filament_id] == \"TPU\"}\n    M620.11 S0 L0 I[initial_no_support_filament_id] B[initial_no_support_hotend] E-{retraction_distances_when_cut[initial_no_support_filament_id]} F{flush_volumetric_speeds[initial_no_support_filament_id]/2.4053*60}\n{else}\n{if (filament_type[initial_no_support_filament_id] == \"PA\") ||  (filament_type[initial_no_support_filament_id] == \"PA-GF\")}\n    M620.11 S1 L0 I[initial_no_support_filament_id] B[initial_no_support_hotend] R4 D2 E-{retraction_distances_when_cut[initial_no_support_filament_id]} F{flush_volumetric_speeds[initial_no_support_filament_id]/2.4053*60}\n{else}\n    M620.11 S1 L0 I[initial_no_support_filament_id] B[initial_no_support_hotend] R10 D8 E-{retraction_distances_when_cut[initial_no_support_filament_id]} F{flush_volumetric_speeds[initial_no_support_filament_id]/2.4053*60}\n{endif}\n{endif}\nM629\n\nM620 S[initial_no_support_filament_id]A H[initial_no_support_hotend] ; switch material if AMS exist\nM1002 gcode_claim_action : 4\nM1002 set_filament_type:UNKNOWN\nM400\nT[initial_no_support_filament_id] H[initial_no_support_hotend]\nM400\nM628 S0\nM629\nM400\nM1002 set_filament_type:{filament_type[initial_no_support_filament_id]}\nM621 S[initial_no_support_filament_id]A\n\nM104 S{nozzle_temperature_initial_layer[initial_no_support_filament_id]}\nM400\nM106 P1 S0\n\nG91\nG1 Y-16 F60000\nG90\n\nG29.2 S1\n;===== prepare print temperature and material ==========\n\n\nM400\n;M73 P99\n\n;===== xy ofst cali start =====\n\nM1002 judge_flag auto_cali_toolhead_offset_flag\n\nM622 J2\n    M1002 gcode_claim_action : 54\n    M190 D[bed_temperature_initial_layer_single]\n\n    M1002 gcode_claim_action : 39\n    M620 D[initial_no_support_hotend]\n    G383.3 U140 L{initial_no_support_filament_id}\nM623\n\nM622 J1\n    M1002 gcode_claim_action : 54\n    M190 D[bed_temperature_initial_layer_single]\n\n    M1002 gcode_claim_action : 39\n    M620 D[initial_no_support_hotend]\n    G383 O2 U140 L{initial_no_support_filament_id}\nM623\n\n;===== xy ofst cali end =====\n\n;===== start to heat heatbed & hotend==========\n\n    M1002 set_filament_type:{filament_type[initial_no_support_filament_id]}\n    G150.3\n    M104 S{nozzle_temperature_initial_layer[initial_no_support_filament_id]}\n    M140 S[bed_temperature_initial_layer_single]\n\n    ;===== set chamber temperature ==========\n    {if (overall_chamber_temperature >= 40)}\n        M145 P1 ; set airduct mode to heating mode\n        M141 S[overall_chamber_temperature] ; Let Chamber begin to heat\n    {endif}\n    ;===== set chamber temperature ==========\n\n;===== start to heat heatbead & hotend==========\n\n\n\nM400\n;M73 P99\n\n;===== auto extrude cali start =========================\nM975 S1\nM1002 judge_flag extrude_cali_flag\n\nM622 J0\n    M983.3 F{filament_max_volumetric_speed[initial_no_support_filament_id]/2.4} A0.4 ; cali dynamic extrusion compensation\nM623\n\nM622 J1\n    M1002 set_filament_type:{filament_type[initial_no_support_filament_id]}\n    M1002 gcode_claim_action : 8\n\n    M109 S{nozzle_temperature[initial_no_support_filament_id]}\n\n    G90\n    M83\n    M983.3 F{filament_max_volumetric_speed[initial_no_support_filament_id]/2.4} A0.4 ; cali dynamic extrusion compensation\n\n    M400\n    M106 P1 S255\n    M400 S5\n    M106 P1 S0\n    G150.3\nM623\n\nM622 J2\n    M1002 set_filament_type:{filament_type[initial_no_support_filament_id]}\n    M1002 gcode_claim_action : 8\n\n    M109 S{nozzle_temperature[initial_no_support_filament_id]}\n\n    G90\n    M83\n    M983.3 F{filament_max_volumetric_speed[initial_no_support_filament_id]/2.4} A0.4 ; cali dynamic extrusion compensation\n\n    M400\n    M106 P1 S255\n    M400 S5\n    M106 P1 S0\n    G150.3\nM623\n\n;===== auto extrude cali end =========================\n\n{if filament_type[initial_no_support_filament_id] == \"TPU\"}\n    G150.2\n    G150.1\n    G150.2\n    G150.1\n    G150.2\n    G150.1\n{else}\n    G150.3\n    M106 P1 S0\n    M400 S2\n    M109 S{nozzle_temperature[initial_no_support_filament_id]} ; wait tmpr to extrude\n    M83\n    {if(nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.8)}\n        G1 E60 F{filament_max_volumetric_speed[initial_no_support_filament_id]/2.4053*60}\n    {else}\n        G1 E45 F{filament_max_volumetric_speed[initial_no_support_filament_id]/2.4053*60}\n    {endif}\n    G1 E-3 F1800\n    M400 P500\n    G150.2\n    G150.1\n{endif}\n\nG91\nG1 Y-16 F12000 ; move away from the trash bin\nG90\n\nM400\n;M73 P99\n\n;===== wipe right nozzle start =====\n\nM1002 gcode_claim_action : 14\n    G150 T{nozzle_temperature_initial_layer[initial_no_support_filament_id]}\n    {if (overall_chamber_temperature >= 40)}\n        G150 T{nozzle_temperature_initial_layer[initial_no_support_filament_id] - 80}\n    {endif}\nM106 S255 ; turn on fan to cool the nozzle\n\n;===== wipe left nozzle end =====\n\nM400\n;M73 P99\n\nM1002 judge_flag auto_cali_toolhead_offset_flag\nM622 J0\n    G91\n    G1 Z5 F1200\n    G90\n    M1012.7\n    G383.7 U140 J0\nM623\n\n{if (overall_chamber_temperature >= 40)}\n    M1002 gcode_claim_action : 49\n    M191 S[overall_chamber_temperature] ; wait for chamber temp\n{endif}\n\nM400\n;M73 P99\n\n;===== bed leveling ==================================\n\nM1002 judge_flag g29_before_print_flag\n\nM190 S[bed_temperature_initial_layer_single]; ensure bed temp\nM109 S140 A\nM106 S0 ; turn off fan , too noisy\n\nG91\nG1 Z10 F1200\n{if (first_non_support_filaments[0] != -1) && filament_type[initial_no_support_filament_id] != \"TPU\"}\nM640 S\nM640.7 U\nM640.7 L\nM640.2 R1\nM641\n{endif}\nG90\nG1 X175 Y160 F30000\n\nM622 J1\n    M1002 gcode_claim_action : 1\n    G29.20 A3\n    G29 A1 O X{first_layer_print_min[0]} Y{first_layer_print_min[1]} I{first_layer_print_size[0]} J{first_layer_print_size[1]} R\n    M400\nM623\n\nM622 J2\n    M1002 gcode_claim_action : 1\n    {if has_tpu_in_first_layer}\n        G29.20 A3\n        G29 A1 O X{first_layer_print_min[0]} Y{first_layer_print_min[1]} I{first_layer_print_size[0]} J{first_layer_print_size[1]} R\n    {else}\n        G29.20 A4\n        G29 A2 O X{first_layer_print_min[0]} Y{first_layer_print_min[1]} I{first_layer_print_size[0]} J{first_layer_print_size[1]} R\n    {endif}\n    M400\nM623\n\nM622 J0\n    G28 R\nM623\n\n;===== bed leveling end ================================\n\nG39.1 ; cali nozzle wrapped detection pos\n\nG90\nG1 Z5 F1200\nG1 X270 Y-0.5 F60000\nG28.140 S0 ; cali pre-extrude z pos\n\n;============switch again==================\nM211 X0 Y0 Z0 ;turn off soft endstop\nG91\nG1 Z6 F1200\nG90\nM1002 set_filament_type:{filament_type[initial_no_support_filament_id]}\nM620 S[initial_no_support_filament_id]A H[initial_no_support_hotend]\nM400\nT[initial_no_support_filament_id] H[initial_no_support_hotend]\nM400\nM628 S0\nM629\nM400\nM621 S[initial_no_support_filament_id]A\n\n;============switch again==================\n\nM400\n;M73 P99\n\nM141 S[overall_chamber_temperature]\n\n;===== mech mode sweep start =====\n    M1002 gcode_claim_action : 3\n\n    G90\n    G1 Z5 F1200\n    G1 X165 Y160 F20000\n    M400 P200\n\n    M970.3 Q1 A5 K0 O1\n    M974 Q1 S2 P0\n\n    M970.3 Q0 A5 K0 O1\n    M974 Q0 S2 P0\n\n    M970.2 Q2 K0 W38 Z0.01\n    M974 Q2 S2 P0\n\n    M975 S1\n;===== mech mode sweep end =====\n\n;===== wait temperature reaching the reference value =======\n\nM140 S[bed_temperature_initial_layer_single]\nM190 S[bed_temperature_initial_layer_single]\n\n    ;========turn off light and fans =============\n    M960 S1 P0 ; turn off laser\n    M960 S2 P0 ; turn off laser\n    M106 S0 ; turn off fan\n    M106 P2 S0 ; turn off big fan\n    ;==== set ext toodhead cooling fan ====\n    {if (min_vitrification_temperature <= 50)}\n    M106 P9 S255\n    {endif}\n    ;============set motor current==================\n    M400 S1\n\n;===== wait temperature reaching the reference value =======\n\nM400\n;M73 P99\n\n;===== plate compensation plus user-calibrated +0.04 mm Z trim =====\n{if curr_bed_type==\"Textured PEI Plate\"}\n    {if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}\n        G29.1 Z{0.04 - 0.01}\n    {else}\n        G29.1 Z{0.04 - 0.02}\n    {endif}\n{else}\n    {if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}\n        G29.1 Z{0.04 + 0.01}\n    {else}\n        G29.1 Z{0.04}\n    {endif}\n{endif}\nG150.1\n\nM975 S1 ; turn on mech mode supression\nM983.4 S1 ; turn on deformation compensation\nG29.2 S1 ; turn on pos comp\nG29.7 S1\n\nG90\nG1 Z5 F1200\nG1 Y295 F30000\nG1 Y265 F18000\n\n;===== nozzle load line ===============================\n    G29.2 S1 ; ensure z comp turn on\n    G90\n    M83\n    G1 Z5 F1200\n    G1 X270 Y-0.5 F60000\n    G28.14 R0\n    G29.2 S0\n    G91\n    G1 Z0.8 F1200\n    G90\n    G1 X250 F60000\n    M104 S{nozzle_temperature_initial_layer[initial_no_support_filament_id]}\n\n    ========== record data ==========\n    M1026\n    M1012.8\n    M1012.9\n    G29.9\n    ========== record data ==========\n\n    M400 P50\n    M500 D1\n    M400 S3\n    M109 S{nozzle_temperature_initial_layer[initial_no_support_filament_id]}\n    M83\n{if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.8}\n    G1 E5 F{filament_max_volumetric_speed[initial_no_support_filament_id]/2.4053*60}\n{endif}\n{if (filament_type[initial_no_support_filament_id] == \"TPU\")}\n    G1 E5 F{filament_max_volumetric_speed[initial_no_support_filament_id]/2.4053*60}\n{endif}\n    G1 E5 F{filament_max_volumetric_speed[initial_no_support_filament_id]/2.4053*60}\n    G1 X290 E10 F{filament_max_volumetric_speed[initial_no_support_filament_id]/2.4053*60}\n    G91\n    G3 Z0.4 I1.217 J0 P1 F60000\n    G90\n    M83\n    G29.2 S1 ; ensure z comp turn on\n;===== noozle load line end ===========================\n\nM400\n;M73 P99\n\nM993 A1 B1 C1 ; nozzle cam detection allowed.\n\n{if (filament_type[initial_no_support_filament_id] == \"TPU\")}\nM1015.3 S1;enable tpu clog detect\n{else}\nM1015.3 S0;disable tpu clog detect\n{endif}\n\n{if (filament_type[initial_no_support_filament_id] == \"PLA\") ||  (filament_type[initial_no_support_filament_id] == \"PETG\")\n ||  (filament_type[initial_no_support_filament_id] == \"PLA-CF\")  ||  (filament_type[initial_no_support_filament_id] == \"PETG-CF\")}\nM1015.4 S1 K1 H{nozzle_diameter_at_nozzle_id[initial_nozzle_id]} ;enable E air printing detect\n{else}\nM1015.4 S0 K0 H{nozzle_diameter_at_nozzle_id[initial_nozzle_id]} ;disable E air printing detect\n{endif}\n\nM620.6 I[initial_no_support_filament_id] H[initial_no_support_hotend] W1 ;enable ams air printing detect\nM620 O1\n\nM211 Z1\nG29.99\nM1002 gcode_claim_action : 0\nM400\n
; machine_switch_extruder_time = 5
; machine_unload_filament_time = 15
; master_extruder_id = 2
; max_bridge_length = 0
; max_layer_height = 0.28,0.28
; max_travel_detour_distance = 0
; min_bead_width = 85%
; min_feature_size = 25%
; min_layer_height = 0.08,0.08
; minimum_sparse_infill_area = 15
; mmu_segmented_region_interlocking_depth = 0
; mmu_segmented_region_max_width = 0
; monotonic_travel_into_wall = 45%
; no_slow_down_for_cooling_on_outwalls = 0
; nozzle_diameter = 0.4,0.4
; nozzle_flush_dataset = 1,1
; nozzle_height = 4
; nozzle_temperature = 280
; nozzle_temperature_initial_layer = 265
; nozzle_temperature_range_high = 300
; nozzle_temperature_range_low = 260
; nozzle_type = hardened_steel,hardened_steel
; nozzle_volume = 130,145
; nozzle_volume_type = Standard,Standard
; only_one_wall_first_layer = 0
; ooze_prevention = 0
; other_layers_print_sequence = 0
; other_layers_print_sequence_nums = 0
; outer_wall_acceleration = 5000,5000
; outer_wall_jerk = 9
; outer_wall_line_width = 0.42
; outer_wall_speed = 200,200
; overhang_1_4_speed = 0,0
; overhang_2_4_speed = 50,50
; overhang_3_4_speed = 30,30
; overhang_4_4_speed = 10,10
; overhang_fan_speed = 70
; overhang_fan_threshold = 50%
; overhang_threshold_participating_cooling = 95%
; overhang_totally_speed = 10,10
; override_filament_scarf_seam_setting = 0
; override_process_overhang_speed = 1
; physical_extruder_map = 1,0
; post_process = 
; pre_start_fan_time = 0
; precise_outer_wall = 0
; precise_z_height = 0
; pressure_advance = 0.02
; prime_tower_brim_width = -1
; prime_tower_enable_framework = 0
; prime_tower_extra_rib_length = 0
; prime_tower_fillet_wall = 1
; prime_tower_flat_ironing = 1
; prime_tower_infill_gap = 150%
; prime_tower_lift_height = -1
; prime_tower_lift_speed = 90
; prime_tower_max_speed = 90
; prime_tower_rib_wall = 1
; prime_tower_rib_width = 8
; prime_tower_skip_points = 1
; prime_tower_width = 60
; prime_volume_mode = Default
; print_compatible_printers = "Bambu Lab H2C 0.4 nozzle";"Bambu Lab H2C 0.4 Standard +0.04 Z trim"
; print_extruder_id = 1,2
; print_extruder_variant = "Direct Drive Standard";"Direct Drive Standard"
; print_flow_ratio = 1
; print_in_clockwise = 0
; print_sequence = by layer
; print_settings_id = 0.24mm PET-GF faucet
; printable_area = 0x0,330x0,330x320,0x320
; printable_height = 325
; printer_extruder_id = 1,2
; printer_extruder_variant = "Direct Drive Standard";"Direct Drive Standard"
; printer_model = Bambu Lab H2C
; printer_notes = 
; printer_settings_id = Bambu Lab H2C 0.4 Standard +0.04 Z trim
; printer_structure = corexy
; printer_technology = FFF
; printer_variant = 0.4
; printhost_authorization_type = key
; printhost_ssl_ignore_revoke = 0
; printing_by_object_gcode = 
; process_notes = 
; raft_contact_distance = 0.1
; raft_expansion = 1.5
; raft_first_layer_density = 90%
; raft_first_layer_expansion = -1
; raft_layers = 0
; reduce_crossing_wall = 0
; reduce_fan_stop_start_freq = 0
; reduce_infill_retraction_mode = Auto
; required_nozzle_HRC = 40
; resolution = 0.012
; retract_before_wipe = 0%,0%
; retract_length_toolchange = 2,2
; retract_lift_above = 0,0
; retract_lift_below = 319,319
; retract_restart_extra = 0,0
; retract_restart_extra_toolchange = 0,0
; retract_when_changing_layer = 1,1
; retraction_distances_when_cut = 14,14
; retraction_distances_when_ec = 10
; retraction_length = 0.8,0.8
; retraction_minimum_travel = 1,1
; retraction_speed = 30,30
; role_base_wipe_speed = 1
; scan_first_layer = 0
; scarf_angle_threshold = 155
; seam_gap = 15%
; seam_placement_away_from_overhangs = 0
; seam_position = aligned
; seam_slope_conditional = 1
; seam_slope_entire_loop = 0
; seam_slope_gap = 0
; seam_slope_inner_walls = 1
; seam_slope_min_length = 10
; seam_slope_start_height = 10%
; seam_slope_steps = 10
; seam_slope_type = none
; silent_mode = 0
; single_extruder_multi_material = 1
; skeleton_infill_density = 15%
; skeleton_infill_line_width = 0.45
; skin_infill_density = 15%
; skin_infill_depth = 2
; skin_infill_line_width = 0.45
; skirt_distance = 2
; skirt_height = 1
; skirt_loops = 0
; skirt_per_object = 1
; slice_closing_radius = 0.049
; slicing_mode = regular
; slow_down_for_layer_cooling = 1
; slow_down_layer_time = 1
; slow_down_min_speed = 10
; slowdown_end_acc = 100000,100000
; slowdown_end_height = 400,400
; slowdown_end_speed = 1000,1000
; slowdown_start_acc = 100000,100000
; slowdown_start_height = 0,0
; slowdown_start_speed = 1000,1000
; small_perimeter_speed = 50%,50%
; small_perimeter_threshold = 0,0
; smooth_coefficient = 4
; smooth_speed_discontinuity_area = 1
; solid_infill_filament = 0
; sparse_infill_acceleration = 100%,100%
; sparse_infill_anchor = 400%
; sparse_infill_anchor_max = 20
; sparse_infill_density = 15%
; sparse_infill_filament = 0
; sparse_infill_lattice_angle_1 = -45
; sparse_infill_lattice_angle_2 = 45
; sparse_infill_line_width = 0.45
; sparse_infill_pattern = gyroid
; sparse_infill_speed = 350,350
; spiral_mode = 0
; spiral_mode_max_xy_smoothing = 200%
; spiral_mode_smooth = 0
; standby_temperature_delta = -5
; start_end_points = 30x-3,54x245
; supertack_plate_temp = 60
; supertack_plate_temp_initial_layer = 60
; support_air_filtration = 0
; support_angle = 0
; support_base_pattern = default
; support_base_pattern_spacing = 2.5
; support_bottom_interface_spacing = 0.5
; support_bottom_z_distance = 0.3
; support_chamber_temp_control = 1
; support_cooling_filter = 1
; support_critical_regions_only = 0
; support_expansion = 0
; support_fast_purge_mode = 0
; support_filament = 1
; support_interface_bottom_layers = 2
; support_interface_filament = 1
; support_interface_loop_pattern = 0
; support_interface_not_for_body = 1
; support_interface_pattern = auto
; support_interface_spacing = 0.5
; support_interface_speed = 80,80
; support_interface_top_layers = 2
; support_ironing_direction = 0
; support_ironing_flow = 10%
; support_ironing_inset = 0
; support_ironing_pattern = zig-zag
; support_ironing_spacing = 0.15
; support_ironing_speed = 30
; support_line_width = 0.62
; support_object_first_layer_gap = 0.2
; support_object_skip_flush = 0
; support_object_xy_distance = 0.4
; support_on_build_plate_only = 0
; support_remove_small_overhang = 1
; support_speed = 150,150
; support_style = default
; support_threshold_angle = 35
; support_top_z_distance = 0.45
; support_type = tree(auto)
; symmetric_infill_y_axis = 0
; temperature_vitrification = 150
; template_custom_gcode = 
; textured_plate_temp = 80
; textured_plate_temp_initial_layer = 80
; thick_bridges = 0
; thumbnail_size = 50x50
; time_lapse_gcode = ;===== machine: H2C timelapse =====\n;======== date: 20260731 ========\n\n; SKIPPABLE_START\n; SKIPTYPE: timelapse\n\nM1002 judge_flag timelapse_record_flag\nM622 J1\n    {if !spiral_mode && !timelapse_inline_photo}\n        M993 A2 B2 C2\n        M993 A0 B0 C0\n    {endif}\n\n    {if !spiral_mode && !(has_timelapse_safe_pos) }\n        {if most_used_physical_extruder_id!= curr_physical_extruder_id || timelapse_type == 1}\n            M83\n            G1 Z{max_layer_z + 0.4} F1200\n            M400\n        {endif}\n    {endif}\n\n    {if timelapse_inline_photo}\n        M971 S11 C10 O0\n        M1004 S5 P1  ; external shutter\n    {elsif has_timelapse_safe_pos && !spiral_mode}\n        M9711 M{timelapse_type} E{most_used_physical_extruder_id} U{timelapse_pos_x} V{timelapse_pos_y} Z{layer_z + (farthest_point_timelapse_enabled ? 0.0 : 0.4)} S11 C10 O0 T3000\n    {else}\n        {if spiral_mode}\n            M971 S11 C10 O0\n            M1004 S5 P1  ; external shutter\n        {else}\n            M9711 M{timelapse_type} E{most_used_physical_extruder_id} Z{layer_z + (farthest_point_timelapse_enabled ? 0.0 : 0.4)} S11 C10 O0 T3000\n        {endif}\n    {endif}\n\n    {if !spiral_mode && !(has_timelapse_safe_pos) }\n        {if most_used_physical_extruder_id!= curr_physical_extruder_id || timelapse_type == 1}\n            G90\n            G1 Z{max_layer_z + 3.0} F1200\n            G1 Y295 F30000\n            G1 Y265 F18000\n            M83\n        {endif}\n    {endif}\n    \n    {if !spiral_mode && !timelapse_inline_photo}\n        M993 A3 B3 C3\n    {endif}\nM623\n; SKIPPABLE_END\n
; timelapse_type = 0
; top_area_threshold = 200%
; top_color_penetration_layers = 4
; top_one_wall_type = all top
; top_shell_layers = 4
; top_shell_thickness = 1
; top_solid_infill_flow_ratio = 1,1
; top_surface_acceleration = 2000,2000
; top_surface_density = 100%
; top_surface_jerk = 9
; top_surface_line_width = 0.45
; top_surface_pattern = monotonicline
; top_surface_speed = 200,200
; top_z_overrides_xy_distance = 0
; travel_acceleration = 10000,10000
; travel_jerk = 9
; travel_short_distance_acceleration = 250,250
; travel_speed = 1000,1000
; travel_speed_z = 0,0
; tree_support_branch_angle = 45
; tree_support_branch_diameter = 2
; tree_support_branch_diameter_angle = 5
; tree_support_branch_distance = 5
; tree_support_wall_count = -1
; upward_compatible_machine = "Bambu Lab H2S 0.4 nozzle";"Bambu Lab H2D 0.4 nozzle";"Bambu Lab H2D Pro 0.4 nozzle";"Bambu Lab A2L 0.4 nozzle"
; use_firmware_retraction = 0
; use_relative_e_distances = 1
; vertical_shell_speed = 80%,80%
; volumetric_speed_coefficients = "0 0 0 0 0 0"
; wall_distribution_count = 1
; wall_filament = 0
; wall_generator = classic
; wall_loops = 2
; wall_sequence = inner wall/outer wall
; wall_transition_angle = 10
; wall_transition_filter_deviation = 25%
; wall_transition_length = 100%
; wipe = 1,1
; wipe_distance = 2,2
; wipe_speed = 80%
; wipe_tower_no_sparse_layers = 0
; wipe_tower_rotation_angle = 0
; wipe_tower_x = 165
; wipe_tower_y = 250
; wrapping_detection_gcode = ;===== machine: H2C =========================\n;===== date: 20251104 =====================\n\n{if !spiral_mode}\n    {if layer_num == 3 || layer_num == 10 || layer_num == 19}\n        M993 A2 B2 C2 ; nozzle cam detection allow status save.\n        M993 A0 B0 C0 ; nozzle cam detection not allowed.\n\n        M400 P100\n\n        G39\n\n        G90\n        G1 Y295 F30000\n        G1 Y265 F18000\n        \n        M993 A3 B3 C3 ; nozzle cam detection allow status restore.\n    {endif}\n{endif}\n
; wrapping_detection_layers = 20
; wrapping_exclude_area = 145x310,251x310,251x326,145x326
; xy_contour_compensation = 0
; xy_hole_compensation = 0
; z_direction_outwall_speed_continuous = 1
; z_hop = 0.4,0.4
; z_hop_types = Auto Lift,Auto Lift
; CONFIG_BLOCK_END

; EXECUTABLE_BLOCK_START
M73 P0 R14
M201 X20000 Y20000 Z500 E5000
M203 X1000 Y1000 Z30 E50
M204 P20000 R5000 T20000
M205 X9.00 Y9.00 Z3.00 E2.50
M106 S0
M106 P2 S0
; FEATURE: Custom
;===== machine: H2C =========================
;===== date: 20260608 =====================

;M1002 set_flag extrude_cali_flag=1
;M1002 set_flag g29_before_print_flag=1
;M1002 set_flag auto_cali_toolhead_offset_flag=1
;M1002 set_flag build_plate_detect_flag=1

M993 A0 B0 C0 ; nozzle cam detection not allowed.

M400
;M73 P99

M960 S10 P1 ; ext fan led

;=====printer start sound ===================
M17
M400 S1
M1006 S1
M1006 A53 B9 L99 C53 D9 M99 E53 F9 N99
M1006 A56 B9 L99 C56 D9 M99 E56 F9 N99
M1006 A61 B9 L99 C61 D9 M99 E61 F9 N99
M1006 A53 B9 L99 C53 D9 M99 E53 F9 N99
M1006 A56 B9 L99 C56 D9 M99 E56 F9 N99
M1006 A61 B18 L99 C61 D18 M99 E61 F18 N99
M1006 W
;=====printer start sound ===================

;===== reset machine status =================
M204 S10000
M630 S0 P0

G90
M17 D ; reset motor current to default
M960 S5 P1 ; turn on logo lamp
G90
M1002 set_gcode_claim_speed_level 5 ;Reset speed level
M220 S100 ;Reset Feedrate
M221 S100 ;Reset Flowrate
M73.2   R1.0 ;Reset left time magnitude
G29.1 Z0 ; clear z-trim value first
M983.1 M1
M901 D4
M481 S0 ; turn off cutter pos comp
G28.140 D0; reset pre-extrude z pos
;===== reset machine status =================

M620 M ;enable remap
M620 N ;enable hotend remap
M620 T0 ;print tmpr
M620 T1 ;sn -> pos
M620 T2 ;filament_id

;===== start to heat heatbed & hotend==========

    M104 O-80 A
    M140 D80

;===== start to heat heatbead & hotend==========

;===== avoid end stop =================
G91
G380 S2 Z42 F1200
G380 S2 Z-12 F1200
G90
;===== avoid end stop =================

;==== set airduct mode ====


    M145 P0 ; set airduct mode to cooling mode for cooling
    M106 P2 S178 ; turn on auxiliary fan for cooling
    M106 P3 S127 ; turn on chamber fan for cooling

    M1002 gcode_claim_action : 29
    M191 S0 ; wait for chamber temp
    M106 P2 S0 ; turn off auxiliary fan
    
        
            
                M142 P1 R35 S50 T55 U0.3 V0.5 W0.8 O55 L1 ; set PETG ND0.4 chamber autocooling
            
        
    

M145.2 P0 F1


;==== set airduct mode ====


;====== cog noise reduction=================
M982.2 S1 ; turn on cog noise reduction

;===== first homing start =====
M1002 gcode_claim_action : 13

M640 S
M640.1 R
M641
G28 X T300
T1000

G150.3
M972 S24 P0 T2000 ; live-view camera foolproof
M972 S46 P0 T5000 ; vortek anti-collision
M640.1 S
M640.4




    M620.14 X95.5 Y336



G150.1 F18000 ; wipe mouth to avoid filament stick to heatbed
G150.3 F18000
M400 P200

M1002 gcode_claim_action : 74 ; Heatbed surface foreign object detection
M104 S0

M972 S26 P0 C0

M972 S35 P0 C0

M972 S41 P0 T5000 ; trash can anti-collision

M1009 Q1 L1
G91
G380 S2 Z30 F1200 ; lower heatbed to move toolhead
G90
G1 X175 Y160 F30000
G28 Z P0 T250
M1009 Q1 L0


;===== first homing end =====

;===== detection start =====

M1002 judge_flag build_plate_detect_flag
M104 S0
M622 S1
    ;M1002 gcode_claim_action : 11 ; Indentifying build plate type
    M972 S19 P0 C0    ; heatbed presence detection
    M972 S31 P0 T5000 ; toolhead camera dirty detection
    ;M1002 gcode_claim_action : 73 ; Build plate alignment detection
    M972 S34 P0 T5000 ; heatbed plate offset detection
M623

M1002 gcode_claim_action : 72 ; Hotend Type Detection
T1001
M972 S14 P0 T5000 ; nozzle type detection

M104 S265 T1 ; rise temp in advance

G151 P1 M ; plug the heat nozzle



;===== detection end =====

M400
;M73 P99

;===== prepare print temperature and material ==========
M400
M211 X0 Y0 Z0 ;turn off soft endstop
M975 S1 ; turn on input shaping

G29.2 S0 ; avoid invalid abl data


M620.10 A0 F359.207 H0.4 T300 P265 S1
M620.10 A1 F359.207 H0.4 T300 P265 S1


M620.11 P1 I0 B-1 E0


M620.11 K1 I0 B-1 R10 F449.008


M628 S1


    M620.11 S1 L0 I0 B-1 R10 D8 E-14 F449.008


M629

M620 S0A H-1 ; switch material if AMS exist
M1002 gcode_claim_action : 4
M1002 set_filament_type:UNKNOWN
M400
T0 H-1
M400
M628 S0
M629
M400
M1002 set_filament_type:PET-CF
M621 S0A

M104 S265
M400
M106 P1 S0

G91
G1 Y-16 F60000
G90

G29.2 S1
;===== prepare print temperature and material ==========


M400
;M73 P99

;===== xy ofst cali start =====

M1002 judge_flag auto_cali_toolhead_offset_flag

M622 J2
    M1002 gcode_claim_action : 54
    M190 D80

    M1002 gcode_claim_action : 39
    M620 D-1
    G383.3 U140 L0
M623

M622 J1
    M1002 gcode_claim_action : 54
    M190 D80

    M1002 gcode_claim_action : 39
    M620 D-1
    G383 O2 U140 L0
M623

;===== xy ofst cali end =====

;===== start to heat heatbed & hotend==========

    M1002 set_filament_type:PET-CF
    G150.3
    M104 S265
    M140 S80

    ;===== set chamber temperature ==========
    
    ;===== set chamber temperature ==========

;===== start to heat heatbead & hotend==========



M400
;M73 P99

;===== auto extrude cali start =========================
M975 S1
M1002 judge_flag extrude_cali_flag

M622 J0
    M983.3 F7.5 A0.4 ; cali dynamic extrusion compensation
M623

M622 J1
    M1002 set_filament_type:PET-CF
    M1002 gcode_claim_action : 8

    M109 S280

    G90
    M83
    M983.3 F7.5 A0.4 ; cali dynamic extrusion compensation

    M400
    M106 P1 S255
    M400 S5
    M106 P1 S0
    G150.3
M623

M622 J2
    M1002 set_filament_type:PET-CF
    M1002 gcode_claim_action : 8

    M109 S280

    G90
    M83
    M983.3 F7.5 A0.4 ; cali dynamic extrusion compensation

    M400
    M106 P1 S255
    M400 S5
    M106 P1 S0
    G150.3
M623

;===== auto extrude cali end =========================


    G150.3
    M106 P1 S0
    M400 S2
    M109 S280 ; wait tmpr to extrude
    M83
    
        G1 E45 F449.008
    
M73 P1 R13
    G1 E-3 F1800
    M400 P500
    G150.2
    G150.1


G91
M73 P3 R13
G1 Y-16 F12000 ; move away from the trash bin
G90

M400
;M73 P99

;===== wipe right nozzle start =====

M1002 gcode_claim_action : 14
    G150 T265
    
M106 S255 ; turn on fan to cool the nozzle

;===== wipe left nozzle end =====

M400
;M73 P99

M1002 judge_flag auto_cali_toolhead_offset_flag
M622 J0
    G91
M73 P4 R13
    G1 Z5 F1200
    G90
    M1012.7
    G383.7 U140 J0
M623



M400
;M73 P99

;===== bed leveling ==================================

M1002 judge_flag g29_before_print_flag

M190 S80; ensure bed temp
M109 S140 A
M106 S0 ; turn off fan , too noisy

G91
G1 Z10 F1200

G90
M73 P34 R9
G1 X175 Y160 F30000

M622 J1
    M1002 gcode_claim_action : 1
    G29.20 A3
    G29 A1 O X132.5 Y152 I60 J16 R
    M400
M623

M622 J2
    M1002 gcode_claim_action : 1
    
        G29.20 A4
        G29 A2 O X132.5 Y152 I60 J16 R
    
    M400
M623

M622 J0
    G28 R
M623

;===== bed leveling end ================================

G39.1 ; cali nozzle wrapped detection pos

G90
G1 Z5 F1200
G1 X270 Y-0.5 F60000
G28.140 S0 ; cali pre-extrude z pos

;============switch again==================
M211 X0 Y0 Z0 ;turn off soft endstop
G91
G1 Z6 F1200
G90
M1002 set_filament_type:PET-CF
M620 S0A H-1
M400
T0 H-1
M400
M628 S0
M629
M400
M621 S0A

;============switch again==================

M400
;M73 P99

M141 S0

;===== mech mode sweep start =====
    M1002 gcode_claim_action : 3

    G90
    G1 Z5 F1200
    G1 X165 Y160 F20000
    M400 P200

    M970.3 Q1 A5 K0 O1
    M974 Q1 S2 P0

    M970.3 Q0 A5 K0 O1
    M974 Q0 S2 P0

    M970.2 Q2 K0 W38 Z0.01
    M974 Q2 S2 P0

    M975 S1
;===== mech mode sweep end =====

;===== wait temperature reaching the reference value =======

M140 S80
M190 S80

    ;========turn off light and fans =============
    M960 S1 P0 ; turn off laser
    M960 S2 P0 ; turn off laser
    M106 S0 ; turn off fan
    M106 P2 S0 ; turn off big fan
    ;==== set ext toodhead cooling fan ====
    
    ;============set motor current==================
    M400 S1

;===== wait temperature reaching the reference value =======

M400
;M73 P99

;===== plate compensation plus user-calibrated +0.04 mm Z trim =====

    
        G29.1 Z0.02
    

G150.1

M975 S1 ; turn on mech mode supression
M983.4 S1 ; turn on deformation compensation
G29.2 S1 ; turn on pos comp
G29.7 S1

G90
G1 Z5 F1200
G1 Y295 F30000
M73 P35 R9
G1 Y265 F18000

;===== nozzle load line ===============================
    G29.2 S1 ; ensure z comp turn on
    G90
    M83
    G1 Z5 F1200
    G1 X270 Y-0.5 F60000
    G28.14 R0
    G29.2 S0
    G91
    G1 Z0.8 F1200
    G90
    G1 X250 F60000
    M104 S265

    ========== record data ==========
    M1026
    M1012.8
    M1012.9
    G29.9
    ========== record data ==========

    M400 P50
    M500 D1
    M400 S3
    M109 S265
    M83


    G1 E5 F449.008
    G1 X290 E10 F449.008
    G91
    G3 Z0.4 I1.217 J0 P1 F60000
    G90
    M83
    G29.2 S1 ; ensure z comp turn on
;===== noozle load line end ===========================

M400
;M73 P99

M993 A1 B1 C1 ; nozzle cam detection allowed.


M1015.3 S0;disable tpu clog detect



M1015.4 S0 K0 H0.4 ;disable E air printing detect


M620.6 I0 H-1 W1 ;enable ams air printing detect
M620 O1

M211 Z1
G29.99
M1002 gcode_claim_action : 0
M400
; MACHINE_START_GCODE_END
; filament start gcode
;VT0 H-1
G90
G21
M83 ; use relative distances for extrusion
M981 S1 P20000 ;open spaghetti detector
; CHANGE_LAYER
; Z_HEIGHT: 0.2
; LAYER_HEIGHT: 0.2
G1 E-.8 F1800
; layer num/total_layer_count: 1/47
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
; OBJECT_ID: 1901
G1 X191.643 Y167.143 F60000
M204 S6000
M73 P36 R9
G1 Z.4
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X133.357 Y167.143 E2.11665
G1 X133.357 Y152.857 E.51879
G1 X191.643 Y152.857 E2.11665
G1 X191.643 Y167.083 E.51661
M204 S6000
G1 X192.1 Y167.6 F60000
; FEATURE: Outer wall
G1 F3000
M204 S500
M73 P36 R8
G1 X132.9 Y167.6 E2.14985
G1 X132.9 Y152.4 E.55199
G1 X192.1 Y152.4 E2.14985
G1 X192.1 Y167.54 E.54981
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
G1 X190.1 Y167.542 E-.76
; WIPE_END
M73 P37 R8
G1 E-.04 F1800
M204 S6000
G1 X190.328 Y159.913 Z.6 F60000
G1 X190.534 Y153.04 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50114
G1 F6300
M204 S500
G1 X191.254 Y153.761 E.03711
G1 X191.254 Y154.409 E.02359
G1 X190.091 Y153.246 E.05988
G1 X189.443 Y153.246 E.02359
G1 X191.254 Y155.057 E.09324
G1 X191.254 Y155.705 E.02359
G1 X188.795 Y153.246 E.12661
G1 X188.147 Y153.246 E.02359
G1 X191.254 Y156.353 E.15997
G1 X191.254 Y157.001 E.02359
G1 X187.499 Y153.246 E.19333
G1 X186.851 Y153.246 E.02359
G1 X191.254 Y157.649 E.2267
G1 X191.254 Y158.297 E.02359
G1 X186.203 Y153.246 E.26006
G1 X185.555 Y153.246 E.02359
G1 X191.254 Y158.945 E.29343
G1 X191.254 Y159.593 E.02359
G1 X184.907 Y153.246 E.32679
G1 X184.259 Y153.246 E.02359
G1 X191.254 Y160.241 E.36015
G1 X191.254 Y160.889 E.02359
G1 X183.611 Y153.246 E.39352
G1 X182.963 Y153.246 E.02359
G1 X191.254 Y161.537 E.42688
G1 X191.254 Y162.185 E.02359
G1 X182.315 Y153.246 E.46024
G1 X181.667 Y153.246 E.02359
G1 X191.254 Y162.833 E.49361
G1 X191.254 Y163.481 E.02359
G1 X181.019 Y153.246 E.52697
G1 X180.371 Y153.246 E.02359
G1 X191.254 Y164.129 E.56033
G1 X191.254 Y164.777 E.02359
G1 X179.723 Y153.246 E.5937
G1 X179.075 Y153.246 E.02359
G1 X191.254 Y165.425 E.62706
G1 X191.254 Y166.073 E.02359
G1 X178.427 Y153.246 E.66042
G1 X177.779 Y153.246 E.02359
G1 X191.254 Y166.721 E.69379
G1 X191.254 Y166.754 E.00122
G1 X190.64 Y166.754 E.02238
G1 X177.131 Y153.246 E.69551
G1 X176.483 Y153.246 E.02359
G1 X189.992 Y166.754 E.69551
G1 X189.344 Y166.754 E.02359
G1 X175.835 Y153.246 E.69551
G1 X175.187 Y153.246 E.02359
M73 P38 R8
G1 X188.696 Y166.754 E.69551
G1 X188.048 Y166.754 E.02359
G1 X174.539 Y153.246 E.69551
G1 X173.891 Y153.246 E.02359
G1 X187.4 Y166.754 E.69551
G1 X186.752 Y166.754 E.02359
G1 X173.243 Y153.246 E.69551
G1 X172.595 Y153.246 E.02359
G1 X186.104 Y166.754 E.69551
G1 X185.456 Y166.754 E.02359
G1 X171.947 Y153.246 E.69551
G1 X171.299 Y153.246 E.02359
G1 X184.808 Y166.754 E.69551
G1 X184.16 Y166.754 E.02359
G1 X170.651 Y153.246 E.69551
G1 X170.003 Y153.246 E.02359
G1 X183.512 Y166.754 E.69551
G1 X182.864 Y166.754 E.02359
G1 X169.355 Y153.246 E.69551
G1 X168.707 Y153.246 E.02359
G1 X182.216 Y166.754 E.69551
G1 X181.568 Y166.754 E.02359
G1 X168.059 Y153.246 E.69551
G1 X167.411 Y153.246 E.02359
G1 X180.919 Y166.754 E.69551
G1 X180.271 Y166.754 E.02359
G1 X166.763 Y153.246 E.69551
G1 X166.115 Y153.246 E.02359
G1 X179.623 Y166.754 E.69551
G1 X178.975 Y166.754 E.02359
G1 X165.467 Y153.246 E.69551
G1 X164.819 Y153.246 E.02359
G1 X178.327 Y166.754 E.69551
G1 X177.679 Y166.754 E.02359
G1 X164.171 Y153.246 E.69551
G1 X163.523 Y153.246 E.02359
G1 X177.031 Y166.754 E.69551
G1 X176.383 Y166.754 E.02359
G1 X162.874 Y153.246 E.69551
G1 X162.226 Y153.246 E.02359
G1 X175.735 Y166.754 E.69551
G1 X175.087 Y166.754 E.02359
M73 P39 R8
G1 X161.578 Y153.246 E.69551
G1 X160.93 Y153.246 E.02359
G1 X174.439 Y166.754 E.69551
G1 X173.791 Y166.754 E.02359
G1 X160.282 Y153.246 E.69551
G1 X159.634 Y153.246 E.02359
G1 X173.143 Y166.754 E.69551
G1 X172.495 Y166.754 E.02359
G1 X158.986 Y153.246 E.69551
G1 X158.338 Y153.246 E.02359
G1 X171.847 Y166.754 E.69551
G1 X171.199 Y166.754 E.02359
G1 X157.69 Y153.246 E.69551
G1 X157.042 Y153.246 E.02359
G1 X170.551 Y166.754 E.69551
G1 X169.903 Y166.754 E.02359
G1 X156.394 Y153.246 E.69551
G1 X155.746 Y153.246 E.02359
G1 X169.255 Y166.754 E.69551
G1 X168.607 Y166.754 E.02359
G1 X155.098 Y153.246 E.69551
G1 X154.45 Y153.246 E.02359
G1 X167.959 Y166.754 E.69551
G1 X167.311 Y166.754 E.02359
G1 X153.802 Y153.246 E.69551
G1 X153.154 Y153.246 E.02359
G1 X166.663 Y166.754 E.69551
G1 X166.015 Y166.754 E.02359
G1 X152.506 Y153.246 E.69551
G1 X151.858 Y153.246 E.02359
G1 X165.367 Y166.754 E.69551
G1 X164.719 Y166.754 E.02359
G1 X151.21 Y153.246 E.69551
G1 X150.562 Y153.246 E.02359
G1 X164.071 Y166.754 E.69551
G1 X163.423 Y166.754 E.02359
G1 X149.914 Y153.246 E.69551
G1 X149.266 Y153.246 E.02359
G1 X162.775 Y166.754 E.69551
G1 X162.127 Y166.754 E.02359
G1 X148.618 Y153.246 E.69551
G1 X147.97 Y153.246 E.02359
M73 P40 R8
G1 X161.479 Y166.754 E.69551
G1 X160.831 Y166.754 E.02359
G1 X147.322 Y153.246 E.69551
G1 X146.674 Y153.246 E.02359
G1 X160.183 Y166.754 E.69551
G1 X159.535 Y166.754 E.02359
G1 X146.026 Y153.246 E.69551
G1 X145.378 Y153.246 E.02359
G1 X158.887 Y166.754 E.69551
G1 X158.239 Y166.754 E.02359
G1 X144.73 Y153.246 E.69551
G1 X144.082 Y153.246 E.02359
G1 X157.591 Y166.754 E.69551
G1 X156.943 Y166.754 E.02359
G1 X143.434 Y153.246 E.69551
G1 X142.786 Y153.246 E.02359
G1 X156.295 Y166.754 E.69551
G1 X155.647 Y166.754 E.02359
G1 X142.138 Y153.246 E.69551
G1 X141.49 Y153.246 E.02359
G1 X154.999 Y166.754 E.69551
G1 X154.351 Y166.754 E.02359
G1 X140.842 Y153.246 E.69551
G1 X140.194 Y153.246 E.02359
G1 X153.703 Y166.754 E.69551
G1 X153.055 Y166.754 E.02359
G1 X139.546 Y153.246 E.69551
G1 X138.898 Y153.246 E.02359
G1 X152.407 Y166.754 E.69551
G1 X151.759 Y166.754 E.02359
G1 X138.25 Y153.246 E.69551
G1 X137.602 Y153.246 E.02359
G1 X151.111 Y166.754 E.69551
G1 X150.463 Y166.754 E.02359
G1 X136.954 Y153.246 E.69551
G1 X136.306 Y153.246 E.02359
G1 X149.814 Y166.754 E.69551
G1 X149.166 Y166.754 E.02359
G1 X135.658 Y153.246 E.69551
G1 X135.01 Y153.246 E.02359
G1 X148.518 Y166.754 E.69551
G1 X147.87 Y166.754 E.02359
M73 P41 R8
G1 X134.362 Y153.246 E.69551
G1 X133.746 Y153.246 E.02243
G1 X133.746 Y153.278 E.00117
G1 X147.222 Y166.754 E.69386
G1 X146.574 Y166.754 E.02359
G1 X133.746 Y153.926 E.6605
G1 X133.746 Y154.574 E.02359
G1 X145.926 Y166.754 E.62713
G1 X145.278 Y166.754 E.02359
G1 X133.746 Y155.222 E.59377
G1 X133.746 Y155.87 E.02359
G1 X144.63 Y166.754 E.56041
G1 X143.982 Y166.754 E.02359
G1 X133.746 Y156.518 E.52704
G1 X133.746 Y157.166 E.02359
G1 X143.334 Y166.754 E.49368
G1 X142.686 Y166.754 E.02359
G1 X133.746 Y157.814 E.46031
G1 X133.746 Y158.462 E.02359
G1 X142.038 Y166.754 E.42695
G1 X141.39 Y166.754 E.02359
G1 X133.746 Y159.11 E.39359
G1 X133.746 Y159.758 E.02359
G1 X140.742 Y166.754 E.36022
G1 X140.094 Y166.754 E.02359
G1 X133.746 Y160.406 E.32686
G1 X133.746 Y161.054 E.02359
G1 X139.446 Y166.754 E.2935
G1 X138.798 Y166.754 E.02359
G1 X133.746 Y161.702 E.26013
G1 X133.746 Y162.35 E.02359
G1 X138.15 Y166.754 E.22677
G1 X137.502 Y166.754 E.02359
G1 X133.746 Y162.998 E.19341
G1 X133.746 Y163.646 E.02359
G1 X136.854 Y166.754 E.16004
G1 X136.206 Y166.754 E.02359
G1 X133.746 Y164.294 E.12668
G1 X133.746 Y164.942 E.02359
G1 X135.558 Y166.754 E.09332
G1 X134.91 Y166.754 E.02359
G1 X133.746 Y165.59 E.05995
G1 X133.746 Y166.238 E.02359
G1 X134.468 Y166.96 E.03718
; CHANGE_LAYER
; Z_HEIGHT: 0.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F6300
G1 X133.746 Y166.238 E-.38806
G1 X133.746 Y165.59 E-.24625
G1 X133.979 Y165.824 E-.1257
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 2/47
; update layer progress
M73 L2
M991 S0 P1 ;notify layer change
; open powerlost recovery
M1003 S1
M104 S280 ; set nozzle temperature
; OBJECT_ID: 1901
M204 S10000
G17
G3 Z.6 I-.033 J1.217 P1  F60000
G1 X191.907 Y167.407 Z.6
G1 Z.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
M204 S250
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
M73 P42 R8
G1 E-.04 F1800
M204 S10000
G1 X191 Y167.246 Z.84 F60000
G1 Z.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X191.581 Y166.666 E.02887
G1 X191.581 Y166.144 E.01836
G1 X190.644 Y167.081 E.04658
G1 X190.123 Y167.081 E.01836
G1 X191.581 Y165.623 E.07254
G1 X191.581 Y165.101 E.01836
G1 X189.601 Y167.081 E.09851
G1 X189.079 Y167.081 E.01836
G1 X191.581 Y164.579 E.12447
G1 X191.581 Y164.057 E.01836
G1 X188.557 Y167.081 E.15043
G1 X188.035 Y167.081 E.01836
G1 X191.581 Y163.535 E.1764
G1 X191.581 Y163.013 E.01836
G1 X187.513 Y167.081 E.20236
G1 X186.991 Y167.081 E.01836
G1 X191.581 Y162.491 E.22832
G1 X191.581 Y161.97 E.01836
G1 X186.47 Y167.081 E.25429
G1 X185.948 Y167.081 E.01836
G1 X191.581 Y161.448 E.28025
G1 X191.581 Y160.926 E.01836
G1 X185.426 Y167.081 E.30621
G1 X184.904 Y167.081 E.01836
G1 X191.581 Y160.404 E.33218
G1 X191.581 Y159.882 E.01836
G1 X184.382 Y167.081 E.35814
G1 X183.86 Y167.081 E.01836
G1 X191.581 Y159.36 E.3841
G1 X191.581 Y158.839 E.01836
G1 X183.339 Y167.081 E.41007
G1 X182.817 Y167.081 E.01836
G1 X191.581 Y158.317 E.43603
G1 X191.581 Y157.795 E.01836
G1 X182.295 Y167.081 E.46199
G1 X181.773 Y167.081 E.01836
G1 X191.581 Y157.273 E.48795
G1 X191.581 Y156.751 E.01836
G1 X181.251 Y167.081 E.51392
G1 X180.729 Y167.081 E.01836
G1 X191.581 Y156.229 E.53988
G1 X191.581 Y155.707 E.01836
G1 X180.207 Y167.081 E.56584
G1 X179.686 Y167.081 E.01836
G1 X191.581 Y155.186 E.59181
G1 X191.581 Y154.664 E.01836
G1 X179.164 Y167.081 E.61777
G1 X178.642 Y167.081 E.01836
G1 X191.581 Y154.142 E.64373
G1 X191.581 Y153.62 E.01836
G1 X178.12 Y167.081 E.6697
G1 X177.598 Y167.081 E.01836
G1 X191.581 Y153.098 E.69566
G1 X191.581 Y152.919 E.00629
G1 X191.238 Y152.919 E.01207
G1 X177.076 Y167.081 E.70456
G1 X176.555 Y167.081 E.01836
G1 X190.716 Y152.919 E.70456
G1 X190.194 Y152.919 E.01836
G1 X176.033 Y167.081 E.70456
G1 X175.511 Y167.081 E.01836
G1 X189.672 Y152.919 E.70456
G1 X189.15 Y152.919 E.01836
G1 X174.989 Y167.081 E.70456
G1 X174.467 Y167.081 E.01836
G1 X188.628 Y152.919 E.70456
G1 X188.107 Y152.919 E.01836
G1 X173.945 Y167.081 E.70456
G1 X173.423 Y167.081 E.01836
G1 X187.585 Y152.919 E.70456
G1 X187.063 Y152.919 E.01836
G1 X172.902 Y167.081 E.70456
G1 X172.38 Y167.081 E.01836
G1 X186.541 Y152.919 E.70456
G1 X186.019 Y152.919 E.01836
G1 X171.858 Y167.081 E.70456
G1 X171.336 Y167.081 E.01836
G1 X185.497 Y152.919 E.70456
G1 X184.975 Y152.919 E.01836
G1 X170.814 Y167.081 E.70456
G1 X170.292 Y167.081 E.01836
G1 X184.454 Y152.919 E.70456
G1 X183.932 Y152.919 E.01836
G1 X169.771 Y167.081 E.70456
G1 X169.249 Y167.081 E.01836
G1 X183.41 Y152.919 E.70456
G1 X182.888 Y152.919 E.01836
G1 X168.727 Y167.081 E.70456
G1 X168.205 Y167.081 E.01836
G1 X182.366 Y152.919 E.70456
G1 X181.844 Y152.919 E.01836
G1 X167.683 Y167.081 E.70456
G1 X167.161 Y167.081 E.01836
G1 X181.323 Y152.919 E.70456
G1 X180.801 Y152.919 E.01836
G1 X166.639 Y167.081 E.70456
G1 X166.118 Y167.081 E.01836
G1 X180.279 Y152.919 E.70456
G1 X179.757 Y152.919 E.01836
G1 X165.596 Y167.081 E.70456
G1 X165.074 Y167.081 E.01836
G1 X179.235 Y152.919 E.70456
G1 X178.713 Y152.919 E.01836
G1 X164.552 Y167.081 E.70456
G1 X164.03 Y167.081 E.01836
G1 X178.191 Y152.919 E.70456
G1 X177.67 Y152.919 E.01836
G1 X163.508 Y167.081 E.70456
G1 X162.987 Y167.081 E.01836
G1 X177.148 Y152.919 E.70456
G1 X176.626 Y152.919 E.01836
G1 X162.465 Y167.081 E.70456
G1 X161.943 Y167.081 E.01836
G1 X176.104 Y152.919 E.70456
G1 X175.582 Y152.919 E.01836
G1 X161.421 Y167.081 E.70456
G1 X160.899 Y167.081 E.01836
G1 X175.06 Y152.919 E.70456
G1 X174.539 Y152.919 E.01836
G1 X160.377 Y167.081 E.70456
G1 X159.856 Y167.081 E.01836
G1 X174.017 Y152.919 E.70456
G1 X173.495 Y152.919 E.01836
G1 X159.334 Y167.081 E.70456
G1 X158.812 Y167.081 E.01836
G1 X172.973 Y152.919 E.70456
G1 X172.451 Y152.919 E.01836
G1 X158.29 Y167.081 E.70456
G1 X157.768 Y167.081 E.01836
G1 X171.929 Y152.919 E.70456
G1 X171.407 Y152.919 E.01836
G1 X157.246 Y167.081 E.70456
G1 X156.724 Y167.081 E.01836
G1 X170.886 Y152.919 E.70456
G1 X170.364 Y152.919 E.01836
G1 X156.203 Y167.081 E.70456
G1 X155.681 Y167.081 E.01836
G1 X169.842 Y152.919 E.70456
G1 X169.32 Y152.919 E.01836
M73 P43 R8
G1 X155.159 Y167.081 E.70456
G1 X154.637 Y167.081 E.01836
G1 X168.798 Y152.919 E.70456
G1 X168.276 Y152.919 E.01836
G1 X154.115 Y167.081 E.70456
G1 X153.593 Y167.081 E.01836
G1 X167.755 Y152.919 E.70456
G1 X167.233 Y152.919 E.01836
G1 X153.072 Y167.081 E.70456
G1 X152.55 Y167.081 E.01836
G1 X166.711 Y152.919 E.70456
G1 X166.189 Y152.919 E.01836
G1 X152.028 Y167.081 E.70456
G1 X151.506 Y167.081 E.01836
G1 X165.667 Y152.919 E.70456
G1 X165.145 Y152.919 E.01836
G1 X150.984 Y167.081 E.70456
G1 X150.462 Y167.081 E.01836
G1 X164.623 Y152.919 E.70456
G1 X164.102 Y152.919 E.01836
G1 X149.94 Y167.081 E.70456
G1 X149.419 Y167.081 E.01836
G1 X163.58 Y152.919 E.70456
G1 X163.058 Y152.919 E.01836
G1 X148.897 Y167.081 E.70456
G1 X148.375 Y167.081 E.01836
G1 X162.536 Y152.919 E.70456
G1 X162.014 Y152.919 E.01836
G1 X147.853 Y167.081 E.70456
G1 X147.331 Y167.081 E.01836
G1 X161.492 Y152.919 E.70456
G1 X160.971 Y152.919 E.01836
G1 X146.809 Y167.081 E.70456
G1 X146.288 Y167.081 E.01836
G1 X160.449 Y152.919 E.70456
G1 X159.927 Y152.919 E.01836
G1 X145.766 Y167.081 E.70456
G1 X145.244 Y167.081 E.01836
G1 X159.405 Y152.919 E.70456
G1 X158.883 Y152.919 E.01836
G1 X144.722 Y167.081 E.70456
G1 X144.2 Y167.081 E.01836
G1 X158.361 Y152.919 E.70456
G1 X157.84 Y152.919 E.01836
G1 X143.678 Y167.081 E.70456
G1 X143.156 Y167.081 E.01836
G1 X157.318 Y152.919 E.70456
G1 X156.796 Y152.919 E.01836
G1 X142.635 Y167.081 E.70456
G1 X142.113 Y167.081 E.01836
G1 X156.274 Y152.919 E.70456
G1 X155.752 Y152.919 E.01836
G1 X141.591 Y167.081 E.70456
G1 X141.069 Y167.081 E.01836
G1 X155.23 Y152.919 E.70456
G1 X154.708 Y152.919 E.01836
G1 X140.547 Y167.081 E.70456
G1 X140.025 Y167.081 E.01836
G1 X154.187 Y152.919 E.70456
G1 X153.665 Y152.919 E.01836
G1 X139.504 Y167.081 E.70456
G1 X138.982 Y167.081 E.01836
G1 X153.143 Y152.919 E.70456
G1 X152.621 Y152.919 E.01836
G1 X138.46 Y167.081 E.70456
G1 X137.938 Y167.081 E.01836
G1 X152.099 Y152.919 E.70456
G1 X151.577 Y152.919 E.01836
G1 X137.416 Y167.081 E.70456
G1 X136.894 Y167.081 E.01836
G1 X151.056 Y152.919 E.70456
G1 X150.534 Y152.919 E.01836
G1 X136.372 Y167.081 E.70456
G1 X135.851 Y167.081 E.01836
G1 X150.012 Y152.919 E.70456
G1 X149.49 Y152.919 E.01836
G1 X135.329 Y167.081 E.70456
G1 X134.807 Y167.081 E.01836
G1 X148.968 Y152.919 E.70456
G1 X148.446 Y152.919 E.01836
G1 X134.285 Y167.081 E.70456
G1 X133.763 Y167.081 E.01836
G1 X147.924 Y152.919 E.70456
G1 X147.403 Y152.919 E.01836
G1 X133.419 Y166.903 E.6957
G1 X133.419 Y166.381 E.01836
G1 X146.881 Y152.919 E.66974
G1 X146.359 Y152.919 E.01836
G1 X133.419 Y165.859 E.64378
G1 X133.419 Y165.337 E.01836
G1 X145.837 Y152.919 E.61781
G1 X145.315 Y152.919 E.01836
G1 X133.419 Y164.815 E.59185
M73 P43 R7
G1 X133.419 Y164.293 E.01836
G1 X144.793 Y152.919 E.56589
G1 X144.272 Y152.919 E.01836
G1 X133.419 Y163.772 E.53992
G1 X133.419 Y163.25 E.01836
G1 X143.75 Y152.919 E.51396
G1 X143.228 Y152.919 E.01836
G1 X133.419 Y162.728 E.488
G1 X133.419 Y162.206 E.01836
G1 X142.706 Y152.919 E.46203
G1 X142.184 Y152.919 E.01836
G1 X133.419 Y161.684 E.43607
G1 X133.419 Y161.162 E.01836
G1 X141.662 Y152.919 E.41011
G1 X141.14 Y152.919 E.01836
G1 X133.419 Y160.64 E.38414
G1 X133.419 Y160.119 E.01836
G1 X140.619 Y152.919 E.35818
G1 X140.097 Y152.919 E.01836
G1 X133.419 Y159.597 E.33222
G1 X133.419 Y159.075 E.01836
G1 X139.575 Y152.919 E.30625
G1 X139.053 Y152.919 E.01836
G1 X133.419 Y158.553 E.28029
G1 X133.419 Y158.031 E.01836
G1 X138.531 Y152.919 E.25433
G1 X138.009 Y152.919 E.01836
G1 X133.419 Y157.509 E.22836
G1 X133.419 Y156.988 E.01836
G1 X137.488 Y152.919 E.2024
G1 X136.966 Y152.919 E.01836
G1 X133.419 Y156.466 E.17644
G1 X133.419 Y155.944 E.01836
G1 X136.444 Y152.919 E.15048
G1 X135.922 Y152.919 E.01836
G1 X133.419 Y155.422 E.12451
G1 X133.419 Y154.9 E.01836
G1 X135.4 Y152.919 E.09855
G1 X134.878 Y152.919 E.01836
G1 X133.419 Y154.378 E.07259
G1 X133.419 Y153.856 E.01836
G1 X134.356 Y152.919 E.04662
G1 X133.835 Y152.919 E.01836
G1 X133.254 Y153.5 E.02891
; CHANGE_LAYER
; Z_HEIGHT: 0.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12195.123
G1 X133.835 Y152.919 E-.31225
G1 X134.356 Y152.919 E-.1983
G1 X133.892 Y153.384 E-.24945
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 3/47
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z.84 I-.286 J1.183 P1  F60000
G1 X191.907 Y167.407 Z.84
G1 Z.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
M73 P44 R7
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X191.067 Y160.139 Z1.08 F60000
G1 X191.746 Y153.5 Z1.08
G1 Z.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X191.166 Y152.919 E.02887
G1 X190.644 Y152.919 E.01836
G1 X191.581 Y153.856 E.04658
G1 X191.581 Y154.377 E.01836
G1 X190.123 Y152.919 E.07254
G1 X189.601 Y152.919 E.01836
G1 X191.581 Y154.899 E.09851
G1 X191.581 Y155.421 E.01836
G1 X189.079 Y152.919 E.12447
G1 X188.557 Y152.919 E.01836
G1 X191.581 Y155.943 E.15043
G1 X191.581 Y156.465 E.01836
G1 X188.035 Y152.919 E.1764
G1 X187.513 Y152.919 E.01836
G1 X191.581 Y156.987 E.20236
G1 X191.581 Y157.509 E.01836
G1 X186.991 Y152.919 E.22832
G1 X186.47 Y152.919 E.01836
G1 X191.581 Y158.03 E.25429
G1 X191.581 Y158.552 E.01836
G1 X185.948 Y152.919 E.28025
G1 X185.426 Y152.919 E.01836
G1 X191.581 Y159.074 E.30621
G1 X191.581 Y159.596 E.01836
G1 X184.904 Y152.919 E.33217
G1 X184.382 Y152.919 E.01836
G1 X191.581 Y160.118 E.35814
G1 X191.581 Y160.64 E.01836
G1 X183.86 Y152.919 E.3841
G1 X183.339 Y152.919 E.01836
G1 X191.581 Y161.161 E.41006
G1 X191.581 Y161.683 E.01836
G1 X182.817 Y152.919 E.43603
G1 X182.295 Y152.919 E.01836
G1 X191.581 Y162.205 E.46199
G1 X191.581 Y162.727 E.01836
G1 X181.773 Y152.919 E.48795
G1 X181.251 Y152.919 E.01836
G1 X191.581 Y163.249 E.51392
G1 X191.581 Y163.771 E.01836
G1 X180.729 Y152.919 E.53988
G1 X180.207 Y152.919 E.01836
G1 X191.581 Y164.293 E.56584
G1 X191.581 Y164.814 E.01836
G1 X179.686 Y152.919 E.59181
G1 X179.164 Y152.919 E.01836
G1 X191.581 Y165.336 E.61777
G1 X191.581 Y165.858 E.01836
G1 X178.642 Y152.919 E.64373
G1 X178.12 Y152.919 E.01836
G1 X191.581 Y166.38 E.6697
G1 X191.581 Y166.902 E.01836
G1 X177.598 Y152.919 E.69566
G1 X177.076 Y152.919 E.01836
G1 X191.238 Y167.081 E.70456
G1 X190.716 Y167.081 E.01836
G1 X176.555 Y152.919 E.70456
G1 X176.033 Y152.919 E.01836
G1 X190.194 Y167.081 E.70456
G1 X189.672 Y167.081 E.01836
G1 X175.511 Y152.919 E.70456
G1 X174.989 Y152.919 E.01836
G1 X189.15 Y167.081 E.70456
G1 X188.628 Y167.081 E.01836
G1 X174.467 Y152.919 E.70456
G1 X173.945 Y152.919 E.01836
G1 X188.107 Y167.081 E.70456
G1 X187.585 Y167.081 E.01836
G1 X173.423 Y152.919 E.70456
G1 X172.902 Y152.919 E.01836
G1 X187.063 Y167.081 E.70456
G1 X186.541 Y167.081 E.01836
G1 X172.38 Y152.919 E.70456
G1 X171.858 Y152.919 E.01836
G1 X186.019 Y167.081 E.70456
G1 X185.497 Y167.081 E.01836
G1 X171.336 Y152.919 E.70456
G1 X170.814 Y152.919 E.01836
G1 X184.975 Y167.081 E.70456
G1 X184.454 Y167.081 E.01836
G1 X170.292 Y152.919 E.70456
G1 X169.771 Y152.919 E.01836
G1 X183.932 Y167.081 E.70456
G1 X183.41 Y167.081 E.01836
G1 X169.249 Y152.919 E.70456
G1 X168.727 Y152.919 E.01836
G1 X182.888 Y167.081 E.70456
G1 X182.366 Y167.081 E.01836
G1 X168.205 Y152.919 E.70456
G1 X167.683 Y152.919 E.01836
G1 X181.844 Y167.081 E.70456
G1 X181.323 Y167.081 E.01836
G1 X167.161 Y152.919 E.70456
G1 X166.64 Y152.919 E.01836
G1 X180.801 Y167.081 E.70456
G1 X180.279 Y167.081 E.01836
G1 X166.118 Y152.919 E.70456
G1 X165.596 Y152.919 E.01836
G1 X179.757 Y167.081 E.70456
G1 X179.235 Y167.081 E.01836
G1 X165.074 Y152.919 E.70456
G1 X164.552 Y152.919 E.01836
G1 X178.713 Y167.081 E.70456
G1 X178.191 Y167.081 E.01836
G1 X164.03 Y152.919 E.70456
G1 X163.508 Y152.919 E.01836
G1 X177.67 Y167.081 E.70456
G1 X177.148 Y167.081 E.01836
G1 X162.987 Y152.919 E.70456
G1 X162.465 Y152.919 E.01836
G1 X176.626 Y167.081 E.70456
G1 X176.104 Y167.081 E.01836
G1 X161.943 Y152.919 E.70456
G1 X161.421 Y152.919 E.01836
G1 X175.582 Y167.081 E.70456
G1 X175.06 Y167.081 E.01836
G1 X160.899 Y152.919 E.70456
G1 X160.377 Y152.919 E.01836
G1 X174.539 Y167.081 E.70456
M73 P45 R7
G1 X174.017 Y167.081 E.01836
G1 X159.856 Y152.919 E.70456
G1 X159.334 Y152.919 E.01836
G1 X173.495 Y167.081 E.70456
G1 X172.973 Y167.081 E.01836
G1 X158.812 Y152.919 E.70456
G1 X158.29 Y152.919 E.01836
G1 X172.451 Y167.081 E.70456
G1 X171.929 Y167.081 E.01836
G1 X157.768 Y152.919 E.70456
G1 X157.246 Y152.919 E.01836
G1 X171.407 Y167.081 E.70456
G1 X170.886 Y167.081 E.01836
G1 X156.724 Y152.919 E.70456
G1 X156.203 Y152.919 E.01836
G1 X170.364 Y167.081 E.70456
G1 X169.842 Y167.081 E.01836
G1 X155.681 Y152.919 E.70456
G1 X155.159 Y152.919 E.01836
G1 X169.32 Y167.081 E.70456
G1 X168.798 Y167.081 E.01836
G1 X154.637 Y152.919 E.70456
G1 X154.115 Y152.919 E.01836
G1 X168.276 Y167.081 E.70456
G1 X167.755 Y167.081 E.01836
G1 X153.593 Y152.919 E.70456
G1 X153.072 Y152.919 E.01836
G1 X167.233 Y167.081 E.70456
G1 X166.711 Y167.081 E.01836
G1 X152.55 Y152.919 E.70456
G1 X152.028 Y152.919 E.01836
G1 X166.189 Y167.081 E.70456
G1 X165.667 Y167.081 E.01836
G1 X151.506 Y152.919 E.70456
G1 X150.984 Y152.919 E.01836
G1 X165.145 Y167.081 E.70456
G1 X164.624 Y167.081 E.01836
G1 X150.462 Y152.919 E.70456
G1 X149.94 Y152.919 E.01836
G1 X164.102 Y167.081 E.70456
G1 X163.58 Y167.081 E.01836
G1 X149.419 Y152.919 E.70456
G1 X148.897 Y152.919 E.01836
G1 X163.058 Y167.081 E.70456
G1 X162.536 Y167.081 E.01836
G1 X148.375 Y152.919 E.70456
G1 X147.853 Y152.919 E.01836
G1 X162.014 Y167.081 E.70456
G1 X161.492 Y167.081 E.01836
G1 X147.331 Y152.919 E.70456
G1 X146.809 Y152.919 E.01836
G1 X160.971 Y167.081 E.70456
G1 X160.449 Y167.081 E.01836
G1 X146.288 Y152.919 E.70456
G1 X145.766 Y152.919 E.01836
G1 X159.927 Y167.081 E.70456
G1 X159.405 Y167.081 E.01836
G1 X145.244 Y152.919 E.70456
G1 X144.722 Y152.919 E.01836
G1 X158.883 Y167.081 E.70456
G1 X158.361 Y167.081 E.01836
G1 X144.2 Y152.919 E.70456
G1 X143.678 Y152.919 E.01836
G1 X157.84 Y167.081 E.70456
G1 X157.318 Y167.081 E.01836
G1 X143.156 Y152.919 E.70456
G1 X142.635 Y152.919 E.01836
G1 X156.796 Y167.081 E.70456
G1 X156.274 Y167.081 E.01836
G1 X142.113 Y152.919 E.70456
G1 X141.591 Y152.919 E.01836
G1 X155.752 Y167.081 E.70456
G1 X155.23 Y167.081 E.01836
G1 X141.069 Y152.919 E.70456
G1 X140.547 Y152.919 E.01836
G1 X154.708 Y167.081 E.70456
G1 X154.187 Y167.081 E.01836
G1 X140.025 Y152.919 E.70456
G1 X139.504 Y152.919 E.01836
G1 X153.665 Y167.081 E.70456
G1 X153.143 Y167.081 E.01836
G1 X138.982 Y152.919 E.70456
G1 X138.46 Y152.919 E.01836
G1 X152.621 Y167.081 E.70456
G1 X152.099 Y167.081 E.01836
G1 X137.938 Y152.919 E.70456
G1 X137.416 Y152.919 E.01836
G1 X151.577 Y167.081 E.70456
G1 X151.056 Y167.081 E.01836
G1 X136.894 Y152.919 E.70456
G1 X136.373 Y152.919 E.01836
G1 X150.534 Y167.081 E.70456
G1 X150.012 Y167.081 E.01836
G1 X135.851 Y152.919 E.70456
G1 X135.329 Y152.919 E.01836
G1 X149.49 Y167.081 E.70456
G1 X148.968 Y167.081 E.01836
G1 X134.807 Y152.919 E.70456
G1 X134.285 Y152.919 E.01836
G1 X148.446 Y167.081 E.70456
G1 X147.924 Y167.081 E.01836
G1 X133.763 Y152.919 E.70456
G1 X133.419 Y152.919 E.0121
G1 X133.419 Y153.097 E.00626
G1 X147.403 Y167.081 E.6957
G1 X146.881 Y167.081 E.01836
G1 X133.419 Y153.619 E.66974
G1 X133.419 Y154.141 E.01836
G1 X146.359 Y167.081 E.64378
G1 X145.837 Y167.081 E.01836
G1 X133.419 Y154.663 E.61781
G1 X133.419 Y155.185 E.01836
G1 X145.315 Y167.081 E.59185
G1 X144.793 Y167.081 E.01836
G1 X133.419 Y155.707 E.56589
G1 X133.419 Y156.228 E.01836
G1 X144.272 Y167.081 E.53992
G1 X143.75 Y167.081 E.01836
G1 X133.419 Y156.75 E.51396
G1 X133.419 Y157.272 E.01836
G1 X143.228 Y167.081 E.488
G1 X142.706 Y167.081 E.01836
G1 X133.419 Y157.794 E.46203
G1 X133.419 Y158.316 E.01836
G1 X142.184 Y167.081 E.43607
G1 X141.662 Y167.081 E.01836
G1 X133.419 Y158.838 E.41011
G1 X133.419 Y159.36 E.01836
G1 X141.14 Y167.081 E.38415
G1 X140.619 Y167.081 E.01836
M73 P46 R7
G1 X133.419 Y159.881 E.35818
G1 X133.419 Y160.403 E.01836
G1 X140.097 Y167.081 E.33222
G1 X139.575 Y167.081 E.01836
G1 X133.419 Y160.925 E.30626
G1 X133.419 Y161.447 E.01836
G1 X139.053 Y167.081 E.28029
G1 X138.531 Y167.081 E.01836
G1 X133.419 Y161.969 E.25433
G1 X133.419 Y162.491 E.01836
G1 X138.009 Y167.081 E.22837
G1 X137.488 Y167.081 E.01836
G1 X133.419 Y163.012 E.2024
G1 X133.419 Y163.534 E.01836
G1 X136.966 Y167.081 E.17644
G1 X136.444 Y167.081 E.01836
G1 X133.419 Y164.056 E.15048
G1 X133.419 Y164.578 E.01836
G1 X135.922 Y167.081 E.12451
G1 X135.4 Y167.081 E.01836
G1 X133.419 Y165.1 E.09855
G1 X133.419 Y165.622 E.01836
G1 X134.878 Y167.081 E.07259
G1 X134.357 Y167.081 E.01836
G1 X133.419 Y166.143 E.04662
G1 X133.419 Y166.665 E.01836
G1 X134 Y167.246 E.02891
; CHANGE_LAYER
; Z_HEIGHT: 0.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12195.123
G1 X133.419 Y166.665 E-.31227
G1 X133.419 Y166.143 E-.1983
G1 X133.884 Y166.608 E-.24943
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 4/47
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.08 I-.017 J1.217 P1  F60000
G1 X191.907 Y167.407 Z1.08
G1 Z.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.658 Y167.641 Z1.32 F60000
G1 X134.287 Y167.066 Z1.32
G1 Z.92
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.434 Y167.066 E.03238
G1 X133.434 Y166.324 E.02818
G1 X133.853 Y166.537 E.01785
G1 X134.281 Y166.471 E.01643
G1 X135.136 Y166.142 E.03481
G1 X135.564 Y165.866 E.01934
G1 X135.991 Y165.44 E.02292
G1 X136.419 Y164.755 E.03068
G1 X136.846 Y163.942 E.03489
G1 X137.274 Y163.725 E.01822
G1 X137.701 Y163.791 E.01643
G1 X138.557 Y164.12 E.03481
G1 X138.984 Y164.396 E.01934
G1 X139.412 Y164.822 E.02292
G1 X139.839 Y165.507 E.03068
G1 X140.267 Y166.319 E.03489
G1 X140.694 Y166.537 E.01822
G1 X141.122 Y166.471 E.01643
G1 X141.977 Y166.142 E.03481
G1 X142.405 Y165.866 E.01934
G1 X142.832 Y165.44 E.02292
G1 X143.26 Y164.755 E.03068
G1 X143.687 Y163.942 E.03489
G1 X144.115 Y163.725 E.01822
G1 X144.542 Y163.791 E.01643
G1 X145.398 Y164.12 E.03481
G1 X145.825 Y164.396 E.01934
G1 X146.253 Y164.822 E.02292
G1 X146.68 Y165.507 E.03068
G1 X147.108 Y166.319 E.03489
G1 X147.535 Y166.537 E.01822
G1 X147.963 Y166.471 E.01643
G1 X148.818 Y166.142 E.03481
G1 X149.246 Y165.866 E.01934
G1 X149.673 Y165.44 E.02292
G1 X150.101 Y164.755 E.03068
G1 X150.528 Y163.942 E.03489
G1 X150.956 Y163.725 E.01822
G1 X151.383 Y163.791 E.01643
G1 X152.239 Y164.12 E.03481
G1 X152.666 Y164.396 E.01934
G1 X153.094 Y164.822 E.02292
G1 X153.521 Y165.507 E.03068
G1 X153.949 Y166.319 E.03489
G1 X154.376 Y166.537 E.01822
G1 X154.804 Y166.471 E.01643
G1 X155.659 Y166.142 E.03481
G1 X156.087 Y165.866 E.01934
G1 X156.514 Y165.44 E.02292
G1 X156.942 Y164.755 E.03068
G1 X157.369 Y163.942 E.03489
G1 X157.797 Y163.725 E.01822
G1 X158.224 Y163.791 E.01643
G1 X159.08 Y164.12 E.03481
G1 X159.507 Y164.396 E.01934
G1 X159.935 Y164.822 E.02292
G1 X160.362 Y165.507 E.03068
G1 X160.79 Y166.319 E.03489
G1 X161.217 Y166.537 E.01822
G1 X161.645 Y166.471 E.01643
G1 X162.5 Y166.142 E.03481
G1 X162.928 Y165.866 E.01934
G1 X163.355 Y165.44 E.02292
G1 X163.783 Y164.755 E.03068
G1 X164.21 Y163.942 E.03489
G1 X164.638 Y163.725 E.01822
G1 X165.066 Y163.791 E.01643
G1 X165.921 Y164.12 E.03481
G1 X166.348 Y164.396 E.01934
G1 X166.776 Y164.822 E.02292
G1 X167.203 Y165.507 E.03068
G1 X167.631 Y166.319 E.03489
G1 X168.058 Y166.537 E.01822
G1 X168.486 Y166.471 E.01643
G1 X169.341 Y166.142 E.03481
G1 X169.769 Y165.866 E.01934
G1 X170.196 Y165.44 E.02292
G1 X170.624 Y164.755 E.03068
G1 X171.051 Y163.942 E.03489
G1 X171.479 Y163.725 E.01822
G1 X171.907 Y163.791 E.01643
G1 X172.762 Y164.12 E.03481
G1 X173.189 Y164.396 E.01934
G1 X173.617 Y164.822 E.02292
G1 X174.044 Y165.507 E.03068
G1 X174.472 Y166.319 E.03489
G1 X174.9 Y166.537 E.01822
G1 X175.327 Y166.471 E.01643
G1 X176.182 Y166.142 E.03481
G1 X176.61 Y165.866 E.01934
G1 X177.037 Y165.44 E.02292
G1 X177.465 Y164.755 E.03068
G1 X177.892 Y163.942 E.03489
G1 X178.32 Y163.725 E.01822
G1 X178.748 Y163.791 E.01643
G1 X179.603 Y164.12 E.03481
G1 X180.03 Y164.396 E.01934
G1 X180.458 Y164.822 E.02292
G1 X180.885 Y165.507 E.03068
G1 X181.313 Y166.319 E.03489
G1 X181.741 Y166.537 E.01822
G1 X182.168 Y166.471 E.01643
G1 X183.023 Y166.142 E.03481
G1 X183.451 Y165.866 E.01934
G1 X183.878 Y165.44 E.02292
G1 X184.306 Y164.755 E.03068
G1 X184.734 Y163.942 E.03489
G1 X185.161 Y163.725 E.01822
G1 X185.589 Y163.791 E.01643
G1 X186.444 Y164.12 E.03481
G1 X186.871 Y164.396 E.01934
G1 X187.299 Y164.822 E.02292
G1 X187.726 Y165.507 E.03068
G1 X188.154 Y166.319 E.03489
G1 X188.582 Y166.537 E.01822
G1 X189.009 Y166.471 E.01643
G1 X189.864 Y166.142 E.03481
G1 X190.292 Y165.866 E.01934
G1 X190.719 Y165.44 E.02292
G1 X191.147 Y164.755 E.03068
G1 X191.566 Y163.959 E.03416
G1 X191.566 Y162.904 E.04011
G1 X191.147 Y163.116 E.01783
G1 X190.719 Y163.05 E.01643
G1 X189.864 Y162.721 E.03481
G1 X189.437 Y162.445 E.01934
G1 X189.009 Y162.019 E.02292
G1 X188.582 Y161.334 E.03068
G1 X188.154 Y160.522 E.03489
G1 X187.726 Y160.305 E.01822
G1 X187.299 Y160.37 E.01643
G1 X186.444 Y160.699 E.03481
G1 X186.016 Y160.975 E.01934
G1 X185.589 Y161.401 E.02292
G1 X185.161 Y162.086 E.03068
G1 X184.734 Y162.899 E.03489
G1 X184.306 Y163.116 E.01822
G1 X183.878 Y163.05 E.01643
G1 X183.023 Y162.721 E.03481
G1 X182.596 Y162.445 E.01934
G1 X182.168 Y162.019 E.02292
G1 X181.741 Y161.334 E.03068
G1 X181.313 Y160.522 E.03489
G1 X180.885 Y160.305 E.01822
G1 X180.458 Y160.37 E.01643
G1 X179.603 Y160.699 E.03481
G1 X179.175 Y160.975 E.01934
G1 X178.748 Y161.401 E.02292
G1 X178.32 Y162.086 E.03068
G1 X177.892 Y162.899 E.03489
G1 X177.465 Y163.116 E.01822
G1 X177.037 Y163.05 E.01643
G1 X176.182 Y162.721 E.03481
G1 X175.755 Y162.445 E.01934
G1 X175.327 Y162.019 E.02292
G1 X174.9 Y161.334 E.03068
G1 X174.472 Y160.522 E.03489
G1 X174.044 Y160.305 E.01822
G1 X173.617 Y160.37 E.01643
G1 X172.762 Y160.699 E.03481
G1 X172.334 Y160.975 E.01934
G1 X171.907 Y161.401 E.02292
G1 X171.479 Y162.086 E.03068
G1 X171.051 Y162.899 E.03489
G1 X170.624 Y163.116 E.01822
G1 X170.196 Y163.05 E.01643
G1 X169.341 Y162.721 E.03481
G1 X168.914 Y162.445 E.01934
G1 X168.486 Y162.019 E.02292
G1 X168.058 Y161.334 E.03068
G1 X167.631 Y160.522 E.03489
G1 X167.203 Y160.305 E.01822
G1 X166.776 Y160.37 E.01643
G1 X165.921 Y160.699 E.03481
G1 X165.493 Y160.975 E.01934
G1 X165.066 Y161.401 E.02292
G1 X164.638 Y162.086 E.03068
G1 X164.21 Y162.899 E.03489
G1 X163.783 Y163.116 E.01822
G1 X163.355 Y163.05 E.01643
G1 X162.5 Y162.721 E.03481
G1 X162.073 Y162.445 E.01934
G1 X161.645 Y162.019 E.02292
G1 X161.217 Y161.334 E.03068
G1 X160.79 Y160.522 E.03489
G1 X160.362 Y160.305 E.01822
G1 X159.935 Y160.37 E.01643
G1 X159.08 Y160.699 E.03481
G1 X158.652 Y160.975 E.01934
G1 X158.224 Y161.401 E.02292
G1 X157.797 Y162.086 E.03068
G1 X157.369 Y162.899 E.03489
G1 X156.942 Y163.116 E.01822
G1 X156.514 Y163.05 E.01643
G1 X155.659 Y162.721 E.03481
G1 X155.232 Y162.445 E.01934
G1 X154.804 Y162.019 E.02292
G1 X154.376 Y161.334 E.03068
G1 X153.949 Y160.522 E.03489
G1 X153.521 Y160.305 E.01822
G1 X153.094 Y160.37 E.01643
G1 X152.239 Y160.699 E.03481
G1 X151.811 Y160.975 E.01934
G1 X151.383 Y161.401 E.02292
G1 X150.956 Y162.086 E.03068
G1 X150.528 Y162.899 E.03489
G1 X150.101 Y163.116 E.01822
G1 X149.673 Y163.05 E.01643
G1 X148.818 Y162.721 E.03481
G1 X148.391 Y162.445 E.01934
G1 X147.963 Y162.019 E.02292
G1 X147.535 Y161.334 E.03068
G1 X147.108 Y160.522 E.03489
G1 X146.68 Y160.305 E.01822
G1 X146.253 Y160.37 E.01643
G1 X145.398 Y160.699 E.03481
G1 X144.97 Y160.975 E.01934
G1 X144.542 Y161.401 E.02292
G1 X144.115 Y162.086 E.03068
G1 X143.687 Y162.899 E.03489
G1 X143.26 Y163.116 E.01822
G1 X142.832 Y163.05 E.01643
G1 X141.977 Y162.721 E.03481
G1 X141.549 Y162.445 E.01934
G1 X141.122 Y162.019 E.02292
G1 X140.694 Y161.334 E.03068
G1 X140.267 Y160.522 E.03489
G1 X139.839 Y160.305 E.01822
G1 X139.412 Y160.37 E.01643
G1 X138.557 Y160.699 E.03481
G1 X138.129 Y160.975 E.01934
G1 X137.701 Y161.401 E.02292
G1 X137.274 Y162.086 E.03068
G1 X136.846 Y162.899 E.03489
G1 X136.419 Y163.116 E.01822
G1 X135.991 Y163.05 E.01643
G1 X135.136 Y162.721 E.03481
G1 X134.708 Y162.445 E.01934
G1 X134.281 Y162.019 E.02292
G1 X133.853 Y161.334 E.03068
G1 X133.434 Y160.538 E.03418
G1 X133.434 Y159.483 E.0401
G1 X133.853 Y159.695 E.01785
G1 X134.281 Y159.63 E.01643
G1 X135.136 Y159.301 E.03481
G1 X135.564 Y159.025 E.01934
G1 X135.991 Y158.599 E.02292
G1 X136.419 Y157.914 E.03068
G1 X136.846 Y157.101 E.03489
G1 X137.274 Y156.884 E.01822
G1 X137.701 Y156.95 E.01643
G1 X138.557 Y157.279 E.03481
G1 X138.984 Y157.555 E.01934
G1 X139.412 Y157.981 E.02292
G1 X139.839 Y158.666 E.03068
G1 X140.267 Y159.478 E.03489
G1 X140.694 Y159.695 E.01822
G1 X141.122 Y159.63 E.01643
G1 X141.977 Y159.301 E.03481
G1 X142.405 Y159.025 E.01934
G1 X142.832 Y158.599 E.02292
G1 X143.26 Y157.914 E.03068
G1 X143.687 Y157.101 E.03489
G1 X144.115 Y156.884 E.01822
G1 X144.542 Y156.95 E.01643
G1 X145.398 Y157.279 E.03481
G1 X145.825 Y157.555 E.01934
G1 X146.253 Y157.981 E.02292
G1 X146.68 Y158.666 E.03068
G1 X147.108 Y159.478 E.03489
G1 X147.535 Y159.695 E.01822
G1 X147.963 Y159.63 E.01643
G1 X148.818 Y159.301 E.03481
G1 X149.246 Y159.025 E.01934
G1 X149.673 Y158.599 E.02292
G1 X150.101 Y157.914 E.03068
G1 X150.528 Y157.101 E.03489
G1 X150.956 Y156.884 E.01822
G1 X151.383 Y156.95 E.01643
G1 X152.239 Y157.279 E.03481
G1 X152.666 Y157.555 E.01934
G1 X153.094 Y157.981 E.02292
G1 X153.521 Y158.666 E.03068
G1 X153.949 Y159.478 E.03489
G1 X154.376 Y159.695 E.01822
G1 X154.804 Y159.63 E.01643
G1 X155.659 Y159.301 E.03481
G1 X156.087 Y159.025 E.01934
G1 X156.514 Y158.599 E.02292
G1 X156.942 Y157.914 E.03068
G1 X157.369 Y157.101 E.03489
G1 X157.797 Y156.884 E.01822
G1 X158.224 Y156.95 E.01643
G1 X159.08 Y157.279 E.03481
G1 X159.507 Y157.555 E.01934
G1 X159.935 Y157.981 E.02292
G1 X160.362 Y158.666 E.03068
G1 X160.79 Y159.478 E.03489
G1 X161.217 Y159.695 E.01822
G1 X161.645 Y159.63 E.01643
G1 X162.5 Y159.301 E.03481
G1 X162.928 Y159.025 E.01934
G1 X163.355 Y158.599 E.02292
G1 X163.783 Y157.914 E.03068
G1 X164.21 Y157.101 E.03489
G1 X164.638 Y156.884 E.01822
G1 X165.066 Y156.95 E.01643
G1 X165.921 Y157.279 E.03481
G1 X166.348 Y157.555 E.01934
G1 X166.776 Y157.981 E.02292
G1 X167.203 Y158.666 E.03068
G1 X167.631 Y159.478 E.03489
G1 X168.058 Y159.695 E.01822
G1 X168.486 Y159.63 E.01643
G1 X169.341 Y159.301 E.03481
G1 X169.769 Y159.025 E.01934
G1 X170.196 Y158.599 E.02292
G1 X170.624 Y157.914 E.03068
G1 X171.051 Y157.101 E.03489
G1 X171.479 Y156.884 E.01822
G1 X171.907 Y156.95 E.01643
G1 X172.762 Y157.279 E.03481
G1 X173.189 Y157.555 E.01934
G1 X173.617 Y157.981 E.02292
G1 X174.044 Y158.666 E.03068
G1 X174.472 Y159.478 E.03489
G1 X174.9 Y159.695 E.01822
G1 X175.327 Y159.63 E.01643
G1 X176.182 Y159.301 E.03481
G1 X176.61 Y159.025 E.01934
G1 X177.037 Y158.599 E.02292
G1 X177.465 Y157.914 E.03068
G1 X177.892 Y157.101 E.03489
G1 X178.32 Y156.884 E.01822
G1 X178.748 Y156.95 E.01643
G1 X179.603 Y157.279 E.03481
G1 X180.03 Y157.555 E.01934
G1 X180.458 Y157.981 E.02292
G1 X180.885 Y158.666 E.03068
G1 X181.313 Y159.478 E.03489
G1 X181.741 Y159.695 E.01822
G1 X182.168 Y159.63 E.01643
G1 X183.023 Y159.301 E.03481
G1 X183.451 Y159.025 E.01934
G1 X183.878 Y158.599 E.02292
G1 X184.306 Y157.914 E.03068
G1 X184.734 Y157.101 E.03489
G1 X185.161 Y156.884 E.01822
G1 X185.589 Y156.95 E.01643
G1 X186.444 Y157.279 E.03481
G1 X186.871 Y157.555 E.01934
G1 X187.299 Y157.981 E.02292
G1 X187.726 Y158.666 E.03068
G1 X188.154 Y159.478 E.03489
G1 X188.582 Y159.695 E.01822
G1 X189.009 Y159.63 E.01643
G1 X189.864 Y159.301 E.03481
G1 X190.292 Y159.025 E.01934
G1 X190.719 Y158.599 E.02292
G1 X191.147 Y157.914 E.03068
G1 X191.566 Y157.118 E.03416
G1 X191.566 Y156.062 E.04011
G1 X191.147 Y156.275 E.01783
G1 X190.719 Y156.209 E.01643
G1 X189.864 Y155.88 E.03481
G1 X189.437 Y155.604 E.01934
G1 X189.009 Y155.178 E.02292
G1 X188.582 Y154.493 E.03068
G1 X188.154 Y153.681 E.03489
G1 X187.726 Y153.464 E.01822
G1 X187.299 Y153.529 E.01643
G1 X186.444 Y153.858 E.03481
G1 X186.016 Y154.134 E.01934
G1 X185.589 Y154.56 E.02292
G1 X185.161 Y155.245 E.03068
G1 X184.734 Y156.058 E.03489
G1 X184.306 Y156.275 E.01822
G1 X183.878 Y156.209 E.01643
G1 X183.023 Y155.88 E.03481
G1 X182.596 Y155.604 E.01934
G1 X182.168 Y155.178 E.02292
G1 X181.741 Y154.493 E.03068
G1 X181.313 Y153.681 E.03489
G1 X180.885 Y153.464 E.01822
G1 X180.458 Y153.529 E.01643
G1 X179.603 Y153.858 E.03481
G1 X179.175 Y154.134 E.01934
G1 X178.748 Y154.56 E.02292
G1 X178.32 Y155.245 E.03068
G1 X177.892 Y156.058 E.03489
G1 X177.465 Y156.275 E.01822
G1 X177.037 Y156.209 E.01643
G1 X176.182 Y155.88 E.03481
G1 X175.755 Y155.604 E.01934
G1 X175.327 Y155.178 E.02292
G1 X174.9 Y154.493 E.03068
G1 X174.472 Y153.681 E.03489
G1 X174.044 Y153.464 E.01822
G1 X173.617 Y153.529 E.01643
G1 X172.762 Y153.858 E.03481
G1 X172.334 Y154.134 E.01934
G1 X171.907 Y154.56 E.02292
G1 X171.479 Y155.245 E.03068
G1 X171.051 Y156.058 E.03489
G1 X170.624 Y156.275 E.01822
G1 X170.196 Y156.209 E.01643
G1 X169.341 Y155.88 E.03481
G1 X168.914 Y155.604 E.01934
G1 X168.486 Y155.178 E.02292
G1 X168.058 Y154.493 E.03068
G1 X167.631 Y153.681 E.03489
G1 X167.203 Y153.464 E.01822
G1 X166.776 Y153.529 E.01643
G1 X165.921 Y153.858 E.03481
G1 X165.493 Y154.134 E.01934
G1 X165.066 Y154.56 E.02292
G1 X164.638 Y155.245 E.03068
G1 X164.21 Y156.058 E.03489
G1 X163.783 Y156.275 E.01822
G1 X163.355 Y156.209 E.01643
G1 X162.5 Y155.88 E.03481
G1 X162.073 Y155.604 E.01934
G1 X161.645 Y155.178 E.02292
G1 X161.217 Y154.493 E.03068
G1 X160.79 Y153.681 E.03489
G1 X160.362 Y153.464 E.01822
G1 X159.935 Y153.529 E.01643
G1 X159.08 Y153.858 E.03481
G1 X158.652 Y154.134 E.01934
G1 X158.224 Y154.56 E.02292
G1 X157.797 Y155.245 E.03068
G1 X157.369 Y156.058 E.03489
G1 X156.942 Y156.275 E.01822
G1 X156.514 Y156.209 E.01643
G1 X155.659 Y155.88 E.03481
G1 X155.232 Y155.604 E.01934
G1 X154.804 Y155.178 E.02292
G1 X154.376 Y154.493 E.03068
G1 X153.949 Y153.681 E.03489
G1 X153.521 Y153.464 E.01822
G1 X153.094 Y153.529 E.01643
G1 X152.239 Y153.858 E.03481
G1 X151.811 Y154.134 E.01934
G1 X151.383 Y154.56 E.02292
G1 X150.956 Y155.245 E.03068
G1 X150.528 Y156.058 E.03489
G1 X150.101 Y156.275 E.01822
G1 X149.673 Y156.209 E.01643
G1 X148.818 Y155.88 E.03481
G1 X148.391 Y155.604 E.01934
G1 X147.963 Y155.178 E.02292
G1 X147.535 Y154.493 E.03068
G1 X147.108 Y153.681 E.03489
G1 X146.68 Y153.464 E.01822
G1 X146.253 Y153.529 E.01643
G1 X145.398 Y153.858 E.03481
G1 X144.97 Y154.134 E.01934
G1 X144.542 Y154.56 E.02292
G1 X144.115 Y155.245 E.03068
G1 X143.687 Y156.058 E.03489
G1 X143.26 Y156.275 E.01822
G1 X142.832 Y156.209 E.01643
G1 X141.977 Y155.88 E.03481
G1 X141.549 Y155.604 E.01934
G1 X141.122 Y155.178 E.02292
G1 X140.694 Y154.493 E.03068
G1 X140.267 Y153.681 E.03489
G1 X139.839 Y153.464 E.01822
G1 X139.412 Y153.529 E.01643
G1 X138.557 Y153.858 E.03481
G1 X138.129 Y154.134 E.01934
G1 X137.701 Y154.56 E.02292
G1 X137.274 Y155.245 E.03068
G1 X136.846 Y156.058 E.03489
G1 X136.419 Y156.275 E.01822
G1 X135.991 Y156.209 E.01643
G1 X135.136 Y155.88 E.03481
G1 X134.708 Y155.604 E.01934
G1 X134.281 Y155.178 E.02292
G1 X133.853 Y154.493 E.03068
G1 X133.434 Y153.697 E.03418
G1 X133.434 Y152.934 E.02898
G1 X134.266 Y152.934 E.03158
; CHANGE_LAYER
; Z_HEIGHT: 1.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X133.434 Y152.934 E-.31587
G1 X133.434 Y153.697 E-.28985
G1 X133.623 Y154.057 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 5/47
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.32 I-.272 J1.186 P1  F60000
G1 X191.907 Y167.407 Z1.32
G1 Z1.16
G1 E.8 F1800
; FEATURE: Inner wall
M73 P47 R7
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.658 Y167.642 Z1.56 F60000
G1 X133.739 Y167.066 Z1.56
G1 Z1.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.434 Y167.066 E.01157
G1 X133.434 Y165.776 E.04899
G1 X133.853 Y166.11 E.02036
G1 X134.281 Y166.208 E.01666
G1 X135.136 Y166.058 E.03298
G1 X135.564 Y165.856 E.01797
G1 X135.991 Y165.534 E.02034
G1 X136.846 Y164.492 E.05121
G1 X137.274 Y164.151 E.02078
G1 X137.701 Y164.054 E.01666
G1 X138.557 Y164.203 E.03298
G1 X138.984 Y164.405 E.01797
G1 X139.412 Y164.727 E.02034
G1 X140.267 Y165.769 E.05121
G1 X140.694 Y166.11 E.02078
G1 X141.122 Y166.208 E.01666
G1 X141.977 Y166.058 E.03298
G1 X142.405 Y165.856 E.01797
G1 X142.832 Y165.534 E.02034
G1 X143.687 Y164.492 E.05121
G1 X144.115 Y164.151 E.02078
G1 X144.542 Y164.054 E.01666
G1 X145.398 Y164.203 E.03298
G1 X145.825 Y164.405 E.01797
G1 X146.253 Y164.727 E.02034
G1 X147.108 Y165.769 E.05121
G1 X147.535 Y166.11 E.02078
G1 X147.963 Y166.208 E.01666
G1 X148.818 Y166.058 E.03298
G1 X149.246 Y165.856 E.01797
G1 X149.673 Y165.534 E.02034
G1 X150.528 Y164.492 E.05121
G1 X150.956 Y164.151 E.02078
G1 X151.383 Y164.054 E.01666
G1 X152.239 Y164.203 E.03298
G1 X152.666 Y164.405 E.01797
G1 X153.094 Y164.727 E.02034
G1 X153.949 Y165.769 E.05121
G1 X154.376 Y166.11 E.02078
G1 X154.804 Y166.208 E.01666
G1 X155.659 Y166.058 E.03298
G1 X156.087 Y165.856 E.01797
G1 X156.514 Y165.534 E.02034
G1 X157.369 Y164.492 E.05121
G1 X157.797 Y164.151 E.02078
G1 X158.224 Y164.054 E.01666
G1 X159.08 Y164.203 E.03298
G1 X159.507 Y164.405 E.01797
G1 X159.935 Y164.727 E.02034
G1 X160.79 Y165.769 E.05121
G1 X161.217 Y166.11 E.02078
G1 X161.645 Y166.208 E.01666
G1 X162.5 Y166.058 E.03298
G1 X162.928 Y165.856 E.01797
G1 X163.355 Y165.534 E.02034
G1 X164.21 Y164.492 E.05121
G1 X164.638 Y164.151 E.02078
G1 X165.066 Y164.054 E.01666
G1 X165.921 Y164.203 E.03298
G1 X166.348 Y164.405 E.01797
G1 X166.776 Y164.727 E.02034
G1 X167.631 Y165.769 E.05121
G1 X168.058 Y166.11 E.02078
G1 X168.486 Y166.208 E.01666
G1 X169.341 Y166.058 E.03298
G1 X169.769 Y165.856 E.01797
G1 X170.196 Y165.534 E.02034
G1 X171.051 Y164.492 E.05121
G1 X171.479 Y164.151 E.02078
G1 X171.907 Y164.054 E.01666
G1 X172.762 Y164.203 E.03298
G1 X173.189 Y164.405 E.01797
G1 X173.617 Y164.727 E.02034
G1 X174.472 Y165.769 E.05121
G1 X174.9 Y166.11 E.02078
G1 X175.327 Y166.208 E.01666
G1 X176.182 Y166.058 E.03298
G1 X176.61 Y165.856 E.01797
G1 X177.037 Y165.534 E.02034
G1 X177.892 Y164.492 E.05121
G1 X178.32 Y164.151 E.02078
G1 X178.748 Y164.054 E.01666
G1 X179.603 Y164.203 E.03298
G1 X180.03 Y164.405 E.01797
G1 X180.458 Y164.727 E.02034
G1 X181.313 Y165.769 E.05121
G1 X181.741 Y166.11 E.02078
G1 X182.168 Y166.208 E.01666
G1 X183.023 Y166.058 E.03298
G1 X183.451 Y165.856 E.01797
G1 X183.878 Y165.534 E.02034
G1 X184.734 Y164.492 E.05121
G1 X185.161 Y164.151 E.02078
G1 X185.589 Y164.054 E.01666
G1 X186.444 Y164.203 E.03298
G1 X186.871 Y164.405 E.01797
G1 X187.299 Y164.727 E.02034
G1 X188.154 Y165.769 E.05121
G1 X188.582 Y166.11 E.02078
G1 X189.009 Y166.208 E.01666
G1 X189.864 Y166.058 E.03298
G1 X190.292 Y165.856 E.01797
G1 X190.719 Y165.534 E.02034
G1 X191.566 Y164.503 E.05067
G1 X191.566 Y162.356 E.08159
G1 X191.147 Y162.69 E.02034
G1 X190.719 Y162.787 E.01666
G1 X189.864 Y162.638 E.03298
G1 X189.437 Y162.436 E.01797
G1 X189.009 Y162.114 E.02034
G1 X188.154 Y161.072 E.05121
G1 X187.726 Y160.731 E.02078
G1 X187.299 Y160.634 E.01666
G1 X186.444 Y160.783 E.03298
G1 X186.016 Y160.985 E.01797
G1 X185.589 Y161.307 E.02034
G1 X184.734 Y162.349 E.05121
G1 X184.306 Y162.69 E.02078
G1 X183.878 Y162.787 E.01666
G1 X183.023 Y162.638 E.03298
G1 X182.596 Y162.436 E.01797
G1 X182.168 Y162.114 E.02034
G1 X181.313 Y161.072 E.05121
G1 X180.885 Y160.731 E.02078
G1 X180.458 Y160.634 E.01666
G1 X179.603 Y160.783 E.03298
G1 X179.175 Y160.985 E.01797
G1 X178.748 Y161.307 E.02034
G1 X177.892 Y162.349 E.05121
G1 X177.465 Y162.69 E.02078
G1 X177.037 Y162.787 E.01666
G1 X176.182 Y162.638 E.03298
G1 X175.755 Y162.436 E.01797
G1 X175.327 Y162.114 E.02034
G1 X174.472 Y161.072 E.05121
G1 X174.044 Y160.731 E.02078
G1 X173.617 Y160.634 E.01666
G1 X172.762 Y160.783 E.03298
G1 X172.334 Y160.985 E.01797
G1 X171.907 Y161.307 E.02034
G1 X171.051 Y162.349 E.05121
G1 X170.624 Y162.69 E.02078
G1 X170.196 Y162.787 E.01666
G1 X169.341 Y162.638 E.03298
G1 X168.914 Y162.436 E.01797
G1 X168.486 Y162.114 E.02034
G1 X167.631 Y161.072 E.05121
G1 X167.203 Y160.731 E.02078
G1 X166.776 Y160.634 E.01666
G1 X165.921 Y160.783 E.03298
G1 X165.493 Y160.985 E.01797
G1 X165.066 Y161.307 E.02034
G1 X164.21 Y162.349 E.05121
G1 X163.783 Y162.69 E.02078
G1 X163.355 Y162.787 E.01666
G1 X162.5 Y162.638 E.03298
G1 X162.073 Y162.436 E.01797
G1 X161.645 Y162.114 E.02034
G1 X160.79 Y161.072 E.05121
G1 X160.362 Y160.731 E.02078
G1 X159.935 Y160.634 E.01666
G1 X159.08 Y160.783 E.03298
G1 X158.652 Y160.985 E.01797
G1 X158.224 Y161.307 E.02034
G1 X157.369 Y162.349 E.05121
G1 X156.942 Y162.69 E.02078
G1 X156.514 Y162.787 E.01666
G1 X155.659 Y162.638 E.03298
G1 X155.232 Y162.436 E.01797
G1 X154.804 Y162.114 E.02034
G1 X153.949 Y161.072 E.05121
G1 X153.521 Y160.731 E.02078
G1 X153.094 Y160.634 E.01666
G1 X152.239 Y160.783 E.03298
G1 X151.811 Y160.985 E.01797
G1 X151.383 Y161.307 E.02034
G1 X150.528 Y162.349 E.05121
G1 X150.101 Y162.69 E.02078
G1 X149.673 Y162.787 E.01666
G1 X148.818 Y162.638 E.03298
G1 X148.391 Y162.436 E.01797
G1 X147.963 Y162.114 E.02034
G1 X147.108 Y161.072 E.05121
G1 X146.68 Y160.731 E.02078
G1 X146.253 Y160.634 E.01666
G1 X145.398 Y160.783 E.03298
G1 X144.97 Y160.985 E.01797
G1 X144.542 Y161.307 E.02034
G1 X143.687 Y162.349 E.05121
G1 X143.26 Y162.69 E.02078
G1 X142.832 Y162.787 E.01666
G1 X141.977 Y162.638 E.03298
G1 X141.549 Y162.436 E.01797
G1 X141.122 Y162.114 E.02034
G1 X140.267 Y161.072 E.05121
G1 X139.839 Y160.731 E.02078
G1 X139.412 Y160.634 E.01666
G1 X138.557 Y160.783 E.03298
G1 X138.129 Y160.985 E.01797
G1 X137.701 Y161.307 E.02034
G1 X136.846 Y162.349 E.05121
G1 X136.419 Y162.69 E.02078
G1 X135.991 Y162.787 E.01666
G1 X135.136 Y162.638 E.03298
G1 X134.708 Y162.436 E.01797
G1 X134.281 Y162.114 E.02034
G1 X133.434 Y161.083 E.05069
G1 X133.434 Y158.935 E.08158
G1 X133.853 Y159.269 E.02036
G1 X134.281 Y159.366 E.01666
G1 X135.136 Y159.217 E.03298
G1 X135.564 Y159.015 E.01797
G1 X135.991 Y158.693 E.02034
G1 X136.846 Y157.651 E.05121
G1 X137.274 Y157.31 E.02078
G1 X137.701 Y157.213 E.01666
G1 X138.557 Y157.362 E.03298
G1 X138.984 Y157.564 E.01797
G1 X139.412 Y157.886 E.02034
G1 X140.267 Y158.928 E.05121
G1 X140.694 Y159.269 E.02078
G1 X141.122 Y159.366 E.01666
G1 X141.977 Y159.217 E.03298
G1 X142.405 Y159.015 E.01797
G1 X142.832 Y158.693 E.02034
G1 X143.687 Y157.651 E.05121
G1 X144.115 Y157.31 E.02078
G1 X144.542 Y157.213 E.01666
G1 X145.398 Y157.362 E.03298
G1 X145.825 Y157.564 E.01797
G1 X146.253 Y157.886 E.02034
G1 X147.108 Y158.928 E.05121
G1 X147.535 Y159.269 E.02078
G1 X147.963 Y159.366 E.01666
G1 X148.818 Y159.217 E.03298
G1 X149.246 Y159.015 E.01797
G1 X149.673 Y158.693 E.02034
G1 X150.528 Y157.651 E.05121
G1 X150.956 Y157.31 E.02078
G1 X151.383 Y157.213 E.01666
G1 X152.239 Y157.362 E.03298
G1 X152.666 Y157.564 E.01797
G1 X153.094 Y157.886 E.02034
G1 X153.949 Y158.928 E.05121
G1 X154.376 Y159.269 E.02078
G1 X154.804 Y159.366 E.01666
G1 X155.659 Y159.217 E.03298
G1 X156.087 Y159.015 E.01797
G1 X156.514 Y158.693 E.02034
G1 X157.369 Y157.651 E.05121
G1 X157.797 Y157.31 E.02078
G1 X158.224 Y157.213 E.01666
G1 X159.08 Y157.362 E.03298
G1 X159.507 Y157.564 E.01797
G1 X159.935 Y157.886 E.02034
G1 X160.79 Y158.928 E.05121
G1 X161.217 Y159.269 E.02078
G1 X161.645 Y159.366 E.01666
G1 X162.5 Y159.217 E.03298
G1 X162.928 Y159.015 E.01797
G1 X163.355 Y158.693 E.02034
G1 X164.21 Y157.651 E.05121
G1 X164.638 Y157.31 E.02078
G1 X165.066 Y157.213 E.01666
G1 X165.921 Y157.362 E.03298
G1 X166.348 Y157.564 E.01797
G1 X166.776 Y157.886 E.02034
G1 X167.631 Y158.928 E.05121
G1 X168.058 Y159.269 E.02078
G1 X168.486 Y159.366 E.01666
G1 X169.341 Y159.217 E.03298
G1 X169.769 Y159.015 E.01797
G1 X170.196 Y158.693 E.02034
G1 X171.051 Y157.651 E.05121
G1 X171.479 Y157.31 E.02078
G1 X171.907 Y157.213 E.01666
G1 X172.762 Y157.362 E.03298
G1 X173.189 Y157.564 E.01797
G1 X173.617 Y157.886 E.02034
G1 X174.472 Y158.928 E.05121
G1 X174.9 Y159.269 E.02078
G1 X175.327 Y159.366 E.01666
G1 X176.182 Y159.217 E.03298
G1 X176.61 Y159.015 E.01797
G1 X177.037 Y158.693 E.02034
G1 X177.892 Y157.651 E.05121
G1 X178.32 Y157.31 E.02078
G1 X178.748 Y157.213 E.01666
G1 X179.603 Y157.362 E.03298
G1 X180.03 Y157.564 E.01797
G1 X180.458 Y157.886 E.02034
G1 X181.313 Y158.928 E.05121
G1 X181.741 Y159.269 E.02078
G1 X182.168 Y159.366 E.01666
G1 X183.023 Y159.217 E.03298
G1 X183.451 Y159.015 E.01797
G1 X183.878 Y158.693 E.02034
G1 X184.734 Y157.651 E.05121
G1 X185.161 Y157.31 E.02078
G1 X185.589 Y157.213 E.01666
G1 X186.444 Y157.362 E.03298
G1 X186.871 Y157.564 E.01797
G1 X187.299 Y157.886 E.02034
G1 X188.154 Y158.928 E.05121
G1 X188.582 Y159.269 E.02078
G1 X189.009 Y159.366 E.01666
G1 X189.864 Y159.217 E.03298
G1 X190.292 Y159.015 E.01797
G1 X190.719 Y158.693 E.02034
G1 X191.566 Y157.662 E.05067
G1 X191.566 Y155.515 E.08159
G1 X191.147 Y155.849 E.02034
G1 X190.719 Y155.946 E.01666
G1 X189.864 Y155.797 E.03298
G1 X189.437 Y155.595 E.01797
G1 X189.009 Y155.273 E.02034
G1 X188.154 Y154.231 E.05121
G1 X187.726 Y153.89 E.02078
G1 X187.299 Y153.793 E.01666
G1 X186.444 Y153.942 E.03298
G1 X186.016 Y154.144 E.01797
G1 X185.589 Y154.466 E.02034
G1 X184.734 Y155.508 E.05121
G1 X184.306 Y155.849 E.02078
G1 X183.878 Y155.946 E.01666
G1 X183.023 Y155.797 E.03298
G1 X182.596 Y155.595 E.01797
G1 X182.168 Y155.273 E.02034
G1 X181.313 Y154.231 E.05121
G1 X180.885 Y153.89 E.02078
G1 X180.458 Y153.793 E.01666
G1 X179.603 Y153.942 E.03298
G1 X179.175 Y154.144 E.01797
G1 X178.748 Y154.466 E.02034
G1 X177.892 Y155.508 E.05121
G1 X177.465 Y155.849 E.02078
G1 X177.037 Y155.946 E.01666
G1 X176.182 Y155.797 E.03298
G1 X175.755 Y155.595 E.01797
G1 X175.327 Y155.273 E.02034
G1 X174.472 Y154.231 E.05121
G1 X174.044 Y153.89 E.02078
G1 X173.617 Y153.793 E.01666
G1 X172.762 Y153.942 E.03298
G1 X172.334 Y154.144 E.01797
G1 X171.907 Y154.466 E.02034
G1 X171.051 Y155.508 E.05121
G1 X170.624 Y155.849 E.02078
G1 X170.196 Y155.946 E.01666
G1 X169.341 Y155.797 E.03298
G1 X168.914 Y155.595 E.01797
G1 X168.486 Y155.273 E.02034
G1 X167.631 Y154.231 E.05121
G1 X167.203 Y153.89 E.02078
G1 X166.776 Y153.793 E.01666
G1 X165.921 Y153.942 E.03298
G1 X165.493 Y154.144 E.01797
G1 X165.066 Y154.466 E.02034
G1 X164.21 Y155.508 E.05121
G1 X163.783 Y155.849 E.02078
G1 X163.355 Y155.946 E.01666
G1 X162.5 Y155.797 E.03298
G1 X162.073 Y155.595 E.01797
G1 X161.645 Y155.273 E.02034
G1 X160.79 Y154.231 E.05121
G1 X160.362 Y153.89 E.02078
G1 X159.935 Y153.793 E.01666
G1 X159.08 Y153.942 E.03298
G1 X158.652 Y154.144 E.01797
G1 X158.224 Y154.466 E.02034
G1 X157.369 Y155.508 E.05121
G1 X156.942 Y155.849 E.02078
G1 X156.514 Y155.946 E.01666
G1 X155.659 Y155.797 E.03298
G1 X155.232 Y155.595 E.01797
G1 X154.804 Y155.273 E.02034
G1 X153.949 Y154.231 E.05121
G1 X153.521 Y153.89 E.02078
G1 X153.094 Y153.793 E.01666
G1 X152.239 Y153.942 E.03298
G1 X151.811 Y154.144 E.01797
G1 X151.383 Y154.466 E.02034
G1 X150.528 Y155.508 E.05121
G1 X150.101 Y155.849 E.02078
G1 X149.673 Y155.946 E.01666
G1 X148.818 Y155.797 E.03298
G1 X148.391 Y155.595 E.01797
G1 X147.963 Y155.273 E.02034
G1 X147.108 Y154.231 E.05121
G1 X146.68 Y153.89 E.02078
G1 X146.253 Y153.793 E.01666
G1 X145.398 Y153.942 E.03298
G1 X144.97 Y154.144 E.01797
G1 X144.542 Y154.466 E.02034
G1 X143.687 Y155.508 E.05121
G1 X143.26 Y155.849 E.02078
G1 X142.832 Y155.946 E.01666
G1 X141.977 Y155.797 E.03298
G1 X141.549 Y155.595 E.01797
G1 X141.122 Y155.273 E.02034
G1 X140.267 Y154.231 E.05121
G1 X139.839 Y153.89 E.02078
G1 X139.412 Y153.793 E.01666
G1 X138.557 Y153.942 E.03298
G1 X138.129 Y154.144 E.01797
G1 X137.701 Y154.466 E.02034
G1 X136.846 Y155.508 E.05121
G1 X136.419 Y155.849 E.02078
G1 X135.991 Y155.946 E.01666
G1 X135.136 Y155.797 E.03298
G1 X134.708 Y155.595 E.01797
G1 X134.281 Y155.273 E.02034
G1 X133.434 Y154.241 E.05069
G1 X133.434 Y152.934 E.04966
G1 X133.721 Y152.934 E.0109
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X133.434 Y152.934 E-.10904
G1 X133.434 Y154.241 E-.49668
G1 X133.692 Y154.555 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 6/47
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.56 I-.262 J1.188 P1  F60000
G1 X191.907 Y167.407 Z1.56
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
M73 P48 R7
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.658 Y167.641 Z1.8 F60000
G1 X133.434 Y167.056 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.434 Y165.462 E.06056
G1 X133.853 Y165.821 E.02095
G1 X134.281 Y166.005 E.01768
G1 X134.708 Y166.053 E.01635
G1 X135.136 Y166.008 E.01633
G1 X135.564 Y165.877 E.01699
G1 X135.991 Y165.64 E.01858
G1 X136.846 Y164.807 E.04535
G1 X137.274 Y164.441 E.02139
G1 X137.701 Y164.257 E.01768
G1 X138.129 Y164.208 E.01635
G1 X138.557 Y164.253 E.01633
G1 X138.984 Y164.384 E.01699
G1 X139.412 Y164.622 E.01858
G1 X140.267 Y165.455 E.04535
G1 X140.694 Y165.821 E.02139
G1 X141.122 Y166.005 E.01768
G1 X141.549 Y166.053 E.01635
G1 X141.977 Y166.008 E.01633
G1 X142.405 Y165.877 E.01699
G1 X142.832 Y165.64 E.01858
G1 X143.687 Y164.807 E.04535
G1 X144.115 Y164.441 E.02139
G1 X144.542 Y164.257 E.01768
G1 X144.97 Y164.208 E.01635
G1 X145.398 Y164.253 E.01633
G1 X145.825 Y164.384 E.01699
G1 X146.253 Y164.622 E.01858
G1 X147.108 Y165.455 E.04535
G1 X147.535 Y165.821 E.02139
G1 X147.963 Y166.005 E.01768
G1 X148.391 Y166.053 E.01635
G1 X148.818 Y166.008 E.01633
G1 X149.246 Y165.877 E.01699
G1 X149.673 Y165.64 E.01858
G1 X150.528 Y164.807 E.04535
G1 X150.956 Y164.441 E.02139
G1 X151.383 Y164.257 E.01768
G1 X151.811 Y164.208 E.01635
G1 X152.239 Y164.253 E.01633
G1 X152.666 Y164.384 E.01699
G1 X153.094 Y164.622 E.01858
G1 X153.949 Y165.455 E.04535
G1 X154.376 Y165.821 E.02139
G1 X154.804 Y166.005 E.01768
G1 X155.232 Y166.053 E.01635
G1 X155.659 Y166.008 E.01633
G1 X156.087 Y165.877 E.01699
G1 X156.514 Y165.64 E.01858
G1 X157.369 Y164.807 E.04535
G1 X157.797 Y164.441 E.02139
G1 X158.224 Y164.257 E.01768
G1 X158.652 Y164.208 E.01635
G1 X159.08 Y164.253 E.01633
G1 X159.507 Y164.384 E.01699
G1 X159.935 Y164.622 E.01858
G1 X160.79 Y165.455 E.04535
G1 X161.217 Y165.821 E.02139
G1 X161.645 Y166.005 E.01768
G1 X162.073 Y166.053 E.01635
G1 X162.5 Y166.008 E.01633
G1 X162.928 Y165.877 E.01699
G1 X163.355 Y165.64 E.01858
G1 X164.21 Y164.807 E.04535
G1 X164.638 Y164.441 E.02139
G1 X165.066 Y164.257 E.01768
G1 X165.493 Y164.208 E.01635
G1 X165.921 Y164.253 E.01633
G1 X166.348 Y164.384 E.01699
G1 X166.776 Y164.622 E.01858
G1 X167.631 Y165.455 E.04535
G1 X168.058 Y165.821 E.02139
G1 X168.486 Y166.005 E.01768
G1 X168.914 Y166.053 E.01635
G1 X169.341 Y166.008 E.01633
G1 X169.769 Y165.877 E.01699
G1 X170.196 Y165.64 E.01858
G1 X171.051 Y164.807 E.04535
G1 X171.479 Y164.441 E.02139
G1 X171.907 Y164.257 E.01768
G1 X172.334 Y164.208 E.01635
G1 X172.762 Y164.253 E.01633
G1 X173.189 Y164.384 E.01699
G1 X173.617 Y164.622 E.01858
G1 X174.472 Y165.455 E.04535
G1 X174.9 Y165.821 E.02139
G1 X175.327 Y166.005 E.01768
G1 X175.755 Y166.053 E.01635
G1 X176.182 Y166.008 E.01633
G1 X176.61 Y165.877 E.01699
G1 X177.037 Y165.64 E.01858
G1 X177.892 Y164.807 E.04535
G1 X178.32 Y164.441 E.02139
G1 X178.748 Y164.257 E.01768
G1 X179.175 Y164.208 E.01635
G1 X179.603 Y164.253 E.01633
G1 X180.03 Y164.384 E.01699
G1 X180.458 Y164.622 E.01858
G1 X181.313 Y165.455 E.04535
G1 X181.741 Y165.821 E.02139
G1 X182.168 Y166.005 E.01768
G1 X182.596 Y166.053 E.01635
G1 X183.023 Y166.008 E.01633
G1 X183.451 Y165.877 E.01699
G1 X183.878 Y165.64 E.01858
G1 X184.734 Y164.807 E.04535
G1 X185.161 Y164.441 E.02139
G1 X185.589 Y164.257 E.01768
G1 X186.016 Y164.208 E.01635
G1 X186.444 Y164.253 E.01633
G1 X186.871 Y164.384 E.01699
G1 X187.299 Y164.622 E.01858
G1 X188.154 Y165.455 E.04535
G1 X188.582 Y165.821 E.02139
G1 X189.009 Y166.005 E.01768
G1 X189.437 Y166.053 E.01635
G1 X189.864 Y166.008 E.01633
G1 X190.292 Y165.877 E.01699
G1 X190.719 Y165.64 E.01858
G1 X191.566 Y164.816 E.04487
G1 X191.566 Y162.042 E.1054
G1 X191.147 Y162.4 E.02093
G1 X190.719 Y162.584 E.01768
G1 X190.292 Y162.633 E.01635
G1 X189.864 Y162.588 E.01633
G1 X189.437 Y162.457 E.01699
G1 X189.009 Y162.219 E.01858
G1 X188.154 Y161.387 E.04535
G1 X187.726 Y161.021 E.02139
G1 X187.299 Y160.837 E.01768
G1 X186.871 Y160.788 E.01635
G1 X186.444 Y160.833 E.01633
G1 X186.016 Y160.964 E.01699
G1 X185.589 Y161.201 E.01858
G1 X184.734 Y162.034 E.04535
G1 X184.306 Y162.4 E.02139
G1 X183.878 Y162.584 E.01768
G1 X183.451 Y162.633 E.01635
G1 X183.023 Y162.588 E.01633
G1 X182.596 Y162.457 E.01699
G1 X182.168 Y162.219 E.01858
G1 X181.313 Y161.387 E.04535
G1 X180.885 Y161.021 E.02139
G1 X180.458 Y160.837 E.01768
G1 X180.03 Y160.788 E.01635
G1 X179.603 Y160.833 E.01633
G1 X179.175 Y160.964 E.01699
G1 X178.748 Y161.201 E.01858
G1 X177.892 Y162.034 E.04535
G1 X177.465 Y162.4 E.02139
G1 X177.037 Y162.584 E.01768
G1 X176.61 Y162.633 E.01635
G1 X176.182 Y162.588 E.01633
G1 X175.755 Y162.457 E.01699
G1 X175.327 Y162.219 E.01858
G1 X174.472 Y161.387 E.04535
G1 X174.044 Y161.021 E.02139
G1 X173.617 Y160.837 E.01768
G1 X173.189 Y160.788 E.01635
G1 X172.762 Y160.833 E.01633
G1 X172.334 Y160.964 E.01699
G1 X171.907 Y161.201 E.01858
G1 X171.051 Y162.034 E.04535
G1 X170.624 Y162.4 E.02139
G1 X170.196 Y162.584 E.01768
G1 X169.769 Y162.633 E.01635
G1 X169.341 Y162.588 E.01633
G1 X168.914 Y162.457 E.01699
G1 X168.486 Y162.219 E.01858
G1 X167.631 Y161.387 E.04535
G1 X167.203 Y161.021 E.02139
G1 X166.776 Y160.837 E.01768
G1 X166.348 Y160.788 E.01635
G1 X165.921 Y160.833 E.01633
G1 X165.493 Y160.964 E.01699
G1 X165.066 Y161.201 E.01858
G1 X164.21 Y162.034 E.04535
G1 X163.783 Y162.4 E.02139
G1 X163.355 Y162.584 E.01768
G1 X162.928 Y162.633 E.01635
G1 X162.5 Y162.588 E.01633
G1 X162.073 Y162.457 E.01699
G1 X161.645 Y162.219 E.01858
G1 X160.79 Y161.387 E.04535
G1 X160.362 Y161.021 E.02139
G1 X159.935 Y160.837 E.01768
G1 X159.507 Y160.788 E.01635
G1 X159.08 Y160.833 E.01633
G1 X158.652 Y160.964 E.01699
G1 X158.224 Y161.201 E.01858
G1 X157.369 Y162.034 E.04535
G1 X156.942 Y162.4 E.02139
G1 X156.514 Y162.584 E.01768
G1 X156.087 Y162.633 E.01635
G1 X155.659 Y162.588 E.01633
G1 X155.232 Y162.457 E.01699
G1 X154.804 Y162.219 E.01858
G1 X153.949 Y161.387 E.04535
G1 X153.521 Y161.021 E.02139
G1 X153.094 Y160.837 E.01768
G1 X152.666 Y160.788 E.01635
G1 X152.239 Y160.833 E.01633
G1 X151.811 Y160.964 E.01699
G1 X151.383 Y161.201 E.01858
G1 X150.528 Y162.034 E.04535
G1 X150.101 Y162.4 E.02139
G1 X149.673 Y162.584 E.01768
G1 X149.246 Y162.633 E.01635
G1 X148.818 Y162.588 E.01633
G1 X148.391 Y162.457 E.01699
G1 X147.963 Y162.219 E.01858
G1 X147.108 Y161.387 E.04535
G1 X146.68 Y161.021 E.02139
G1 X146.253 Y160.837 E.01768
G1 X145.825 Y160.788 E.01635
G1 X145.398 Y160.833 E.01633
G1 X144.97 Y160.964 E.01699
G1 X144.542 Y161.201 E.01858
G1 X143.687 Y162.034 E.04535
G1 X143.26 Y162.4 E.02139
G1 X142.832 Y162.584 E.01768
G1 X142.405 Y162.633 E.01635
G1 X141.977 Y162.588 E.01633
G1 X141.549 Y162.457 E.01699
G1 X141.122 Y162.219 E.01858
G1 X140.267 Y161.387 E.04535
G1 X139.839 Y161.021 E.02139
G1 X139.412 Y160.837 E.01768
G1 X138.984 Y160.788 E.01635
G1 X138.557 Y160.833 E.01633
G1 X138.129 Y160.964 E.01699
G1 X137.701 Y161.201 E.01858
G1 X136.846 Y162.034 E.04535
G1 X136.419 Y162.4 E.02139
G1 X135.991 Y162.584 E.01768
G1 X135.564 Y162.633 E.01635
G1 X135.136 Y162.588 E.01633
G1 X134.708 Y162.457 E.01699
G1 X134.281 Y162.219 E.01858
G1 X133.434 Y161.395 E.04489
G1 X133.434 Y158.621 E.1054
G1 X133.853 Y158.98 E.02095
G1 X134.281 Y159.164 E.01768
G1 X134.708 Y159.212 E.01635
G1 X135.136 Y159.167 E.01633
G1 X135.564 Y159.036 E.01699
G1 X135.991 Y158.799 E.01858
G1 X136.846 Y157.966 E.04535
G1 X137.274 Y157.6 E.02139
G1 X137.701 Y157.416 E.01768
G1 X138.129 Y157.367 E.01635
G1 X138.557 Y157.412 E.01633
G1 X138.984 Y157.543 E.01699
G1 X139.412 Y157.781 E.01858
G1 X140.267 Y158.613 E.04535
G1 X140.694 Y158.98 E.02139
G1 X141.122 Y159.164 E.01768
G1 X141.549 Y159.212 E.01635
G1 X141.977 Y159.167 E.01633
G1 X142.405 Y159.036 E.01699
G1 X142.832 Y158.799 E.01858
G1 X143.687 Y157.966 E.04535
G1 X144.115 Y157.6 E.02139
G1 X144.542 Y157.416 E.01768
G1 X144.97 Y157.367 E.01635
G1 X145.398 Y157.412 E.01633
G1 X145.825 Y157.543 E.01699
G1 X146.253 Y157.781 E.01858
G1 X147.108 Y158.613 E.04535
G1 X147.535 Y158.98 E.02139
G1 X147.963 Y159.164 E.01768
G1 X148.391 Y159.212 E.01635
G1 X148.818 Y159.167 E.01633
G1 X149.246 Y159.036 E.01699
G1 X149.673 Y158.799 E.01858
G1 X150.528 Y157.966 E.04535
G1 X150.956 Y157.6 E.02139
G1 X151.383 Y157.416 E.01768
G1 X151.811 Y157.367 E.01635
G1 X152.239 Y157.412 E.01633
G1 X152.666 Y157.543 E.01699
G1 X153.094 Y157.781 E.01858
G1 X153.949 Y158.613 E.04535
G1 X154.376 Y158.98 E.02139
G1 X154.804 Y159.164 E.01768
G1 X155.232 Y159.212 E.01635
G1 X155.659 Y159.167 E.01633
G1 X156.087 Y159.036 E.01699
G1 X156.514 Y158.799 E.01858
G1 X157.369 Y157.966 E.04535
G1 X157.797 Y157.6 E.02139
G1 X158.224 Y157.416 E.01768
G1 X158.652 Y157.367 E.01635
G1 X159.08 Y157.412 E.01633
G1 X159.507 Y157.543 E.01699
G1 X159.935 Y157.781 E.01858
G1 X160.79 Y158.613 E.04535
G1 X161.217 Y158.98 E.02139
G1 X161.645 Y159.164 E.01768
G1 X162.073 Y159.212 E.01635
G1 X162.5 Y159.167 E.01633
G1 X162.928 Y159.036 E.01699
G1 X163.355 Y158.799 E.01858
G1 X164.21 Y157.966 E.04535
G1 X164.638 Y157.6 E.02139
G1 X165.066 Y157.416 E.01768
G1 X165.493 Y157.367 E.01635
G1 X165.921 Y157.412 E.01633
G1 X166.348 Y157.543 E.01699
G1 X166.776 Y157.781 E.01858
G1 X167.631 Y158.613 E.04535
G1 X168.058 Y158.98 E.02139
G1 X168.486 Y159.164 E.01768
G1 X168.914 Y159.212 E.01635
G1 X169.341 Y159.167 E.01633
G1 X169.769 Y159.036 E.01699
G1 X170.196 Y158.799 E.01858
G1 X171.051 Y157.966 E.04535
G1 X171.479 Y157.6 E.02139
G1 X171.907 Y157.416 E.01768
G1 X172.334 Y157.367 E.01635
G1 X172.762 Y157.412 E.01633
G1 X173.189 Y157.543 E.01699
G1 X173.617 Y157.781 E.01858
G1 X174.472 Y158.613 E.04535
G1 X174.9 Y158.98 E.02139
G1 X175.327 Y159.164 E.01768
G1 X175.755 Y159.212 E.01635
G1 X176.182 Y159.167 E.01633
G1 X176.61 Y159.036 E.01699
G1 X177.037 Y158.799 E.01858
G1 X177.892 Y157.966 E.04535
G1 X178.32 Y157.6 E.02139
G1 X178.748 Y157.416 E.01768
G1 X179.175 Y157.367 E.01635
G1 X179.603 Y157.412 E.01633
G1 X180.03 Y157.543 E.01699
G1 X180.458 Y157.781 E.01858
G1 X181.313 Y158.613 E.04535
G1 X181.741 Y158.98 E.02139
G1 X182.168 Y159.164 E.01768
G1 X182.596 Y159.212 E.01635
G1 X183.023 Y159.167 E.01633
G1 X183.451 Y159.036 E.01699
G1 X183.878 Y158.799 E.01858
G1 X184.734 Y157.966 E.04535
G1 X185.161 Y157.6 E.02139
G1 X185.589 Y157.416 E.01768
G1 X186.016 Y157.367 E.01635
G1 X186.444 Y157.412 E.01633
G1 X186.871 Y157.543 E.01699
G1 X187.299 Y157.781 E.01858
G1 X188.154 Y158.613 E.04535
G1 X188.582 Y158.98 E.02139
G1 X189.009 Y159.164 E.01768
G1 X189.437 Y159.212 E.01635
G1 X189.864 Y159.167 E.01633
G1 X190.292 Y159.036 E.01699
G1 X190.719 Y158.799 E.01858
G1 X191.566 Y157.975 E.04487
G1 X191.566 Y155.201 E.1054
G1 X191.147 Y155.559 E.02094
G1 X190.719 Y155.743 E.01768
G1 X190.292 Y155.792 E.01635
G1 X189.864 Y155.747 E.01633
G1 X189.437 Y155.616 E.01699
G1 X189.009 Y155.378 E.01858
G1 X188.154 Y154.546 E.04535
G1 X187.726 Y154.179 E.02139
G1 X187.299 Y153.995 E.01768
G1 X186.871 Y153.947 E.01635
G1 X186.444 Y153.992 E.01633
G1 X186.016 Y154.123 E.01699
G1 X185.589 Y154.36 E.01858
G1 X184.734 Y155.193 E.04535
G1 X184.306 Y155.559 E.02139
G1 X183.878 Y155.743 E.01768
G1 X183.451 Y155.792 E.01635
G1 X183.023 Y155.747 E.01633
G1 X182.596 Y155.616 E.01699
G1 X182.168 Y155.378 E.01858
G1 X181.313 Y154.546 E.04535
G1 X180.885 Y154.179 E.02139
G1 X180.458 Y153.995 E.01768
G1 X180.03 Y153.947 E.01635
G1 X179.603 Y153.992 E.01633
G1 X179.175 Y154.123 E.01699
G1 X178.748 Y154.36 E.01858
G1 X177.892 Y155.193 E.04535
G1 X177.465 Y155.559 E.02139
G1 X177.037 Y155.743 E.01768
G1 X176.61 Y155.792 E.01635
G1 X176.182 Y155.747 E.01633
G1 X175.755 Y155.616 E.01699
G1 X175.327 Y155.378 E.01858
G1 X174.472 Y154.546 E.04535
G1 X174.044 Y154.179 E.02139
G1 X173.617 Y153.995 E.01768
G1 X173.189 Y153.947 E.01635
G1 X172.762 Y153.992 E.01633
G1 X172.334 Y154.123 E.01699
G1 X171.907 Y154.36 E.01858
G1 X171.051 Y155.193 E.04535
G1 X170.624 Y155.559 E.02139
G1 X170.196 Y155.743 E.01768
G1 X169.769 Y155.792 E.01635
G1 X169.341 Y155.747 E.01633
G1 X168.914 Y155.616 E.01699
G1 X168.486 Y155.378 E.01858
G1 X167.631 Y154.546 E.04535
G1 X167.203 Y154.179 E.02139
G1 X166.776 Y153.995 E.01768
G1 X166.348 Y153.947 E.01635
G1 X165.921 Y153.992 E.01633
G1 X165.493 Y154.123 E.01699
G1 X165.066 Y154.36 E.01858
G1 X164.21 Y155.193 E.04535
G1 X163.783 Y155.559 E.02139
G1 X163.355 Y155.743 E.01768
G1 X162.928 Y155.792 E.01635
G1 X162.5 Y155.747 E.01633
G1 X162.073 Y155.616 E.01699
G1 X161.645 Y155.378 E.01858
G1 X160.79 Y154.546 E.04535
G1 X160.362 Y154.179 E.02139
G1 X159.935 Y153.995 E.01768
G1 X159.507 Y153.947 E.01635
G1 X159.08 Y153.992 E.01633
G1 X158.652 Y154.123 E.01699
G1 X158.224 Y154.36 E.01858
G1 X157.369 Y155.193 E.04535
G1 X156.942 Y155.559 E.02139
G1 X156.514 Y155.743 E.01768
G1 X156.087 Y155.792 E.01635
G1 X155.659 Y155.747 E.01633
G1 X155.232 Y155.616 E.01699
G1 X154.804 Y155.378 E.01858
G1 X153.949 Y154.546 E.04535
G1 X153.521 Y154.179 E.02139
G1 X153.094 Y153.995 E.01768
G1 X152.666 Y153.947 E.01635
G1 X152.239 Y153.992 E.01633
G1 X151.811 Y154.123 E.01699
G1 X151.383 Y154.36 E.01858
G1 X150.528 Y155.193 E.04535
G1 X150.101 Y155.559 E.02139
G1 X149.673 Y155.743 E.01768
G1 X149.246 Y155.792 E.01635
G1 X148.818 Y155.747 E.01633
G1 X148.391 Y155.616 E.01699
G1 X147.963 Y155.378 E.01858
G1 X147.108 Y154.546 E.04535
G1 X146.68 Y154.179 E.02139
G1 X146.253 Y153.995 E.01768
G1 X145.825 Y153.947 E.01635
G1 X145.398 Y153.992 E.01633
G1 X144.97 Y154.123 E.01699
G1 X144.542 Y154.36 E.01858
G1 X143.687 Y155.193 E.04535
G1 X143.26 Y155.559 E.02139
G1 X142.832 Y155.743 E.01768
G1 X142.405 Y155.792 E.01635
G1 X141.977 Y155.747 E.01633
G1 X141.549 Y155.616 E.01699
G1 X141.122 Y155.378 E.01858
G1 X140.267 Y154.546 E.04535
G1 X139.839 Y154.179 E.02139
G1 X139.412 Y153.995 E.01768
G1 X138.984 Y153.947 E.01635
G1 X138.557 Y153.992 E.01633
G1 X138.129 Y154.123 E.01699
G1 X137.701 Y154.36 E.01858
G1 X136.846 Y155.193 E.04535
G1 X136.419 Y155.559 E.02139
G1 X135.991 Y155.743 E.01768
G1 X135.564 Y155.792 E.01635
G1 X135.136 Y155.747 E.01633
G1 X134.708 Y155.616 E.01699
G1 X134.281 Y155.378 E.01858
G1 X133.434 Y154.554 E.04489
G1 X133.434 Y152.96 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X133.434 Y154.554 E-.60571
G1 X133.725 Y154.837 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 7/47
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.8 I-.257 J1.19 P1  F60000
G1 X191.907 Y167.407 Z1.8
G1 Z1.64
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.659 Y167.607 Z2.04 F60000
G1 X133.434 Y166.803 Z2.04
G1 Z1.64
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.434 Y165.209 E.06056
G1 X133.853 Y165.59 E.02151
G1 X134.281 Y165.843 E.01886
G1 X134.708 Y165.964 E.01688
G1 X135.136 Y165.987 E.01627
G1 X135.564 Y165.924 E.01642
G1 X135.991 Y165.761 E.01738
G1 X136.419 Y165.469 E.01968
G1 X137.274 Y164.671 E.04442
G1 X137.701 Y164.419 E.01886
G1 X138.129 Y164.298 E.01688
G1 X138.557 Y164.275 E.01627
G1 X138.984 Y164.337 E.01642
G1 X139.412 Y164.5 E.01738
G1 X139.839 Y164.793 E.01968
G1 X140.694 Y165.59 E.04442
G1 X141.122 Y165.843 E.01886
G1 X141.549 Y165.964 E.01688
G1 X141.977 Y165.987 E.01627
G1 X142.405 Y165.924 E.01642
G1 X142.832 Y165.761 E.01738
G1 X143.26 Y165.469 E.01968
G1 X144.115 Y164.671 E.04442
G1 X144.542 Y164.419 E.01886
G1 X144.97 Y164.298 E.01688
G1 X145.398 Y164.275 E.01627
G1 X145.825 Y164.337 E.01642
G1 X146.253 Y164.5 E.01738
G1 X146.68 Y164.793 E.01968
G1 X147.535 Y165.59 E.04442
G1 X147.963 Y165.843 E.01886
G1 X148.391 Y165.964 E.01688
G1 X148.818 Y165.987 E.01627
G1 X149.246 Y165.924 E.01642
G1 X149.673 Y165.761 E.01738
G1 X150.101 Y165.469 E.01968
G1 X150.956 Y164.671 E.04442
G1 X151.383 Y164.419 E.01886
G1 X151.811 Y164.298 E.01688
G1 X152.239 Y164.275 E.01627
G1 X152.666 Y164.337 E.01642
G1 X153.094 Y164.5 E.01738
G1 X153.521 Y164.793 E.01968
G1 X154.376 Y165.59 E.04442
G1 X154.804 Y165.843 E.01886
G1 X155.232 Y165.964 E.01688
G1 X155.659 Y165.987 E.01627
G1 X156.087 Y165.924 E.01642
G1 X156.514 Y165.761 E.01738
G1 X156.942 Y165.469 E.01968
G1 X157.797 Y164.671 E.04442
G1 X158.224 Y164.419 E.01886
G1 X158.652 Y164.298 E.01688
G1 X159.08 Y164.275 E.01627
G1 X159.507 Y164.337 E.01642
G1 X159.935 Y164.5 E.01738
G1 X160.362 Y164.793 E.01968
G1 X161.217 Y165.59 E.04442
G1 X161.645 Y165.843 E.01886
G1 X162.073 Y165.964 E.01688
G1 X162.5 Y165.987 E.01627
G1 X162.928 Y165.924 E.01642
G1 X163.355 Y165.761 E.01738
G1 X163.783 Y165.469 E.01968
G1 X164.638 Y164.671 E.04442
G1 X165.066 Y164.419 E.01886
G1 X165.493 Y164.298 E.01688
G1 X165.921 Y164.275 E.01627
G1 X166.348 Y164.337 E.01642
G1 X166.776 Y164.5 E.01738
G1 X167.203 Y164.793 E.01968
G1 X168.058 Y165.59 E.04442
G1 X168.486 Y165.843 E.01886
G1 X168.914 Y165.964 E.01688
G1 X169.341 Y165.987 E.01627
G1 X169.769 Y165.924 E.01642
G1 X170.196 Y165.761 E.01738
G1 X170.624 Y165.469 E.01968
G1 X171.479 Y164.671 E.04442
G1 X171.907 Y164.419 E.01886
G1 X172.334 Y164.298 E.01688
G1 X172.762 Y164.275 E.01627
G1 X173.189 Y164.337 E.01642
G1 X173.617 Y164.5 E.01738
G1 X174.044 Y164.793 E.01968
G1 X174.9 Y165.59 E.04442
G1 X175.327 Y165.843 E.01886
G1 X175.755 Y165.964 E.01688
G1 X176.182 Y165.987 E.01627
G1 X176.61 Y165.924 E.01642
G1 X177.037 Y165.761 E.01738
G1 X177.465 Y165.469 E.01968
G1 X178.32 Y164.671 E.04442
G1 X178.748 Y164.419 E.01886
G1 X179.175 Y164.298 E.01688
G1 X179.603 Y164.275 E.01627
G1 X180.03 Y164.337 E.01642
G1 X180.458 Y164.5 E.01738
G1 X180.885 Y164.793 E.01968
G1 X181.741 Y165.59 E.04442
G1 X182.168 Y165.843 E.01886
G1 X182.596 Y165.964 E.01688
G1 X183.023 Y165.987 E.01627
G1 X183.451 Y165.924 E.01642
M73 P49 R7
G1 X183.878 Y165.761 E.01738
G1 X184.306 Y165.469 E.01968
G1 X185.161 Y164.671 E.04442
G1 X185.589 Y164.419 E.01886
G1 X186.016 Y164.298 E.01688
G1 X186.444 Y164.275 E.01627
G1 X186.871 Y164.337 E.01642
G1 X187.299 Y164.5 E.01738
G1 X187.726 Y164.793 E.01968
G1 X188.582 Y165.59 E.04442
G1 X189.009 Y165.843 E.01886
G1 X189.437 Y165.964 E.01688
G1 X189.864 Y165.987 E.01627
G1 X190.292 Y165.924 E.01642
G1 X190.719 Y165.761 E.01738
G1 X191.147 Y165.469 E.01968
G1 X191.566 Y165.069 E.02199
G1 X191.566 Y161.789 E.12462
G1 X191.147 Y162.17 E.0215
G1 X190.719 Y162.422 E.01886
G1 X190.292 Y162.543 E.01688
G1 X189.864 Y162.567 E.01627
G1 X189.437 Y162.504 E.01642
G1 X189.009 Y162.341 E.01738
G1 X188.582 Y162.048 E.01968
G1 X187.726 Y161.251 E.04442
G1 X187.299 Y160.999 E.01886
G1 X186.871 Y160.877 E.01688
G1 X186.444 Y160.854 E.01627
G1 X186.016 Y160.917 E.01642
G1 X185.589 Y161.08 E.01738
G1 X185.161 Y161.372 E.01968
G1 X184.306 Y162.17 E.04442
G1 X183.878 Y162.422 E.01886
G1 X183.451 Y162.543 E.01688
G1 X183.023 Y162.567 E.01627
G1 X182.596 Y162.504 E.01642
G1 X182.168 Y162.341 E.01738
G1 X181.741 Y162.048 E.01968
G1 X180.885 Y161.251 E.04442
G1 X180.458 Y160.999 E.01886
G1 X180.03 Y160.877 E.01688
G1 X179.603 Y160.854 E.01627
G1 X179.175 Y160.917 E.01642
G1 X178.748 Y161.08 E.01738
G1 X178.32 Y161.372 E.01968
G1 X177.465 Y162.17 E.04442
G1 X177.037 Y162.422 E.01886
G1 X176.61 Y162.543 E.01688
G1 X176.182 Y162.567 E.01627
G1 X175.755 Y162.504 E.01642
G1 X175.327 Y162.341 E.01738
G1 X174.9 Y162.048 E.01968
G1 X174.044 Y161.251 E.04442
G1 X173.617 Y160.999 E.01886
G1 X173.189 Y160.877 E.01688
G1 X172.762 Y160.854 E.01627
G1 X172.334 Y160.917 E.01642
G1 X171.907 Y161.08 E.01738
G1 X171.479 Y161.372 E.01968
G1 X170.624 Y162.17 E.04442
G1 X170.196 Y162.422 E.01886
G1 X169.769 Y162.543 E.01688
G1 X169.341 Y162.567 E.01627
G1 X168.914 Y162.504 E.01642
G1 X168.486 Y162.341 E.01738
G1 X168.058 Y162.048 E.01968
G1 X167.203 Y161.251 E.04442
G1 X166.776 Y160.999 E.01886
G1 X166.348 Y160.877 E.01688
G1 X165.921 Y160.854 E.01627
G1 X165.493 Y160.917 E.01642
G1 X165.066 Y161.08 E.01738
G1 X164.638 Y161.372 E.01968
G1 X163.783 Y162.17 E.04442
G1 X163.355 Y162.422 E.01886
G1 X162.928 Y162.543 E.01688
G1 X162.5 Y162.567 E.01627
G1 X162.073 Y162.504 E.01642
G1 X161.645 Y162.341 E.01738
G1 X161.217 Y162.048 E.01968
G1 X160.362 Y161.251 E.04442
G1 X159.935 Y160.999 E.01886
G1 X159.507 Y160.877 E.01688
G1 X159.08 Y160.854 E.01627
G1 X158.652 Y160.917 E.01642
G1 X158.224 Y161.08 E.01738
G1 X157.797 Y161.372 E.01968
G1 X156.942 Y162.17 E.04442
G1 X156.514 Y162.422 E.01886
G1 X156.087 Y162.543 E.01688
G1 X155.659 Y162.567 E.01627
G1 X155.232 Y162.504 E.01642
G1 X154.804 Y162.341 E.01738
G1 X154.376 Y162.048 E.01968
G1 X153.521 Y161.251 E.04442
G1 X153.094 Y160.999 E.01886
G1 X152.666 Y160.877 E.01688
G1 X152.239 Y160.854 E.01627
G1 X151.811 Y160.917 E.01642
G1 X151.383 Y161.08 E.01738
G1 X150.956 Y161.372 E.01968
G1 X150.101 Y162.17 E.04442
G1 X149.673 Y162.422 E.01886
G1 X149.246 Y162.543 E.01688
G1 X148.818 Y162.567 E.01627
G1 X148.391 Y162.504 E.01642
G1 X147.963 Y162.341 E.01738
G1 X147.535 Y162.048 E.01968
G1 X146.68 Y161.251 E.04442
G1 X146.253 Y160.999 E.01886
G1 X145.825 Y160.877 E.01688
G1 X145.398 Y160.854 E.01627
G1 X144.97 Y160.917 E.01642
G1 X144.542 Y161.08 E.01738
G1 X144.115 Y161.372 E.01968
G1 X143.26 Y162.17 E.04442
G1 X142.832 Y162.422 E.01886
G1 X142.405 Y162.543 E.01688
G1 X141.977 Y162.567 E.01627
G1 X141.549 Y162.504 E.01642
G1 X141.122 Y162.341 E.01738
G1 X140.694 Y162.048 E.01968
G1 X139.839 Y161.251 E.04442
G1 X139.412 Y160.999 E.01886
G1 X138.984 Y160.877 E.01688
G1 X138.557 Y160.854 E.01627
G1 X138.129 Y160.917 E.01642
G1 X137.701 Y161.08 E.01738
G1 X137.274 Y161.372 E.01968
G1 X136.419 Y162.17 E.04442
G1 X135.991 Y162.422 E.01886
G1 X135.564 Y162.543 E.01688
G1 X135.136 Y162.567 E.01627
G1 X134.708 Y162.504 E.01642
G1 X134.281 Y162.341 E.01738
G1 X133.853 Y162.048 E.01968
G1 X133.434 Y161.648 E.02201
G1 X133.434 Y158.368 E.12462
G1 X133.853 Y158.749 E.02151
G1 X134.281 Y159.002 E.01886
G1 X134.708 Y159.123 E.01688
G1 X135.136 Y159.146 E.01627
G1 X135.564 Y159.083 E.01642
G1 X135.991 Y158.92 E.01738
G1 X136.419 Y158.628 E.01968
G1 X137.274 Y157.83 E.04442
G1 X137.701 Y157.578 E.01886
G1 X138.129 Y157.457 E.01688
G1 X138.557 Y157.434 E.01627
G1 X138.984 Y157.496 E.01642
G1 X139.412 Y157.659 E.01738
G1 X139.839 Y157.952 E.01968
G1 X140.694 Y158.749 E.04442
G1 X141.122 Y159.002 E.01886
G1 X141.549 Y159.123 E.01688
G1 X141.977 Y159.146 E.01627
G1 X142.405 Y159.083 E.01642
G1 X142.832 Y158.92 E.01738
G1 X143.26 Y158.628 E.01968
G1 X144.115 Y157.83 E.04442
G1 X144.542 Y157.578 E.01886
G1 X144.97 Y157.457 E.01688
G1 X145.398 Y157.434 E.01627
G1 X145.825 Y157.496 E.01642
G1 X146.253 Y157.659 E.01738
G1 X146.68 Y157.952 E.01968
G1 X147.535 Y158.749 E.04442
G1 X147.963 Y159.002 E.01886
G1 X148.391 Y159.123 E.01688
G1 X148.818 Y159.146 E.01627
G1 X149.246 Y159.083 E.01642
G1 X149.673 Y158.92 E.01738
G1 X150.101 Y158.628 E.01968
G1 X150.956 Y157.83 E.04442
G1 X151.383 Y157.578 E.01886
G1 X151.811 Y157.457 E.01688
G1 X152.239 Y157.434 E.01627
G1 X152.666 Y157.496 E.01642
G1 X153.094 Y157.659 E.01738
G1 X153.521 Y157.952 E.01968
G1 X154.376 Y158.749 E.04442
G1 X154.804 Y159.002 E.01886
G1 X155.232 Y159.123 E.01688
G1 X155.659 Y159.146 E.01627
G1 X156.087 Y159.083 E.01642
G1 X156.514 Y158.92 E.01738
G1 X156.942 Y158.628 E.01968
G1 X157.797 Y157.83 E.04442
G1 X158.224 Y157.578 E.01886
G1 X158.652 Y157.457 E.01688
G1 X159.08 Y157.434 E.01627
G1 X159.507 Y157.496 E.01642
G1 X159.935 Y157.659 E.01738
G1 X160.362 Y157.952 E.01968
G1 X161.217 Y158.749 E.04442
G1 X161.645 Y159.002 E.01886
G1 X162.073 Y159.123 E.01688
G1 X162.5 Y159.146 E.01627
G1 X162.928 Y159.083 E.01642
G1 X163.355 Y158.92 E.01738
G1 X163.783 Y158.628 E.01968
G1 X164.638 Y157.83 E.04442
G1 X165.066 Y157.578 E.01886
G1 X165.493 Y157.457 E.01688
G1 X165.921 Y157.434 E.01627
G1 X166.348 Y157.496 E.01642
G1 X166.776 Y157.659 E.01738
G1 X167.203 Y157.952 E.01968
G1 X168.058 Y158.749 E.04442
G1 X168.486 Y159.002 E.01886
G1 X168.914 Y159.123 E.01688
G1 X169.341 Y159.146 E.01627
G1 X169.769 Y159.083 E.01642
G1 X170.196 Y158.92 E.01738
G1 X170.624 Y158.628 E.01968
G1 X171.479 Y157.83 E.04442
G1 X171.907 Y157.578 E.01886
G1 X172.334 Y157.457 E.01688
G1 X172.762 Y157.434 E.01627
G1 X173.189 Y157.496 E.01642
G1 X173.617 Y157.659 E.01738
G1 X174.044 Y157.952 E.01968
G1 X174.9 Y158.749 E.04442
G1 X175.327 Y159.002 E.01886
G1 X175.755 Y159.123 E.01688
G1 X176.182 Y159.146 E.01627
G1 X176.61 Y159.083 E.01642
G1 X177.037 Y158.92 E.01738
G1 X177.465 Y158.628 E.01968
G1 X178.32 Y157.83 E.04442
G1 X178.748 Y157.578 E.01886
G1 X179.175 Y157.457 E.01688
G1 X179.603 Y157.434 E.01627
G1 X180.03 Y157.496 E.01642
G1 X180.458 Y157.659 E.01738
G1 X180.885 Y157.952 E.01968
G1 X181.741 Y158.749 E.04442
G1 X182.168 Y159.002 E.01886
G1 X182.596 Y159.123 E.01688
G1 X183.023 Y159.146 E.01627
G1 X183.451 Y159.083 E.01642
G1 X183.878 Y158.92 E.01738
G1 X184.306 Y158.628 E.01968
G1 X185.161 Y157.83 E.04442
G1 X185.589 Y157.578 E.01886
G1 X186.016 Y157.457 E.01688
G1 X186.444 Y157.434 E.01627
G1 X186.871 Y157.496 E.01642
G1 X187.299 Y157.659 E.01738
G1 X187.726 Y157.952 E.01968
G1 X188.582 Y158.749 E.04442
G1 X189.009 Y159.002 E.01886
G1 X189.437 Y159.123 E.01688
G1 X189.864 Y159.146 E.01627
G1 X190.292 Y159.083 E.01642
G1 X190.719 Y158.92 E.01738
G1 X191.147 Y158.628 E.01968
G1 X191.566 Y158.228 E.02199
G1 X191.566 Y154.948 E.12462
G1 X191.147 Y155.329 E.0215
G1 X190.719 Y155.581 E.01886
G1 X190.292 Y155.702 E.01688
G1 X189.864 Y155.726 E.01627
G1 X189.437 Y155.663 E.01642
G1 X189.009 Y155.5 E.01738
G1 X188.582 Y155.207 E.01968
G1 X187.726 Y154.41 E.04442
G1 X187.299 Y154.157 E.01886
G1 X186.871 Y154.036 E.01688
G1 X186.444 Y154.013 E.01627
G1 X186.016 Y154.076 E.01642
G1 X185.589 Y154.239 E.01738
G1 X185.161 Y154.531 E.01968
G1 X184.306 Y155.329 E.04442
G1 X183.878 Y155.581 E.01886
G1 X183.451 Y155.702 E.01688
G1 X183.023 Y155.726 E.01627
G1 X182.596 Y155.663 E.01642
G1 X182.168 Y155.5 E.01738
G1 X181.741 Y155.207 E.01968
G1 X180.885 Y154.41 E.04442
G1 X180.458 Y154.157 E.01886
G1 X180.03 Y154.036 E.01688
G1 X179.603 Y154.013 E.01627
G1 X179.175 Y154.076 E.01642
G1 X178.748 Y154.239 E.01738
G1 X178.32 Y154.531 E.01968
G1 X177.465 Y155.329 E.04442
G1 X177.037 Y155.581 E.01886
G1 X176.61 Y155.702 E.01688
G1 X176.182 Y155.726 E.01627
G1 X175.755 Y155.663 E.01642
G1 X175.327 Y155.5 E.01738
G1 X174.9 Y155.207 E.01968
G1 X174.044 Y154.41 E.04442
G1 X173.617 Y154.157 E.01886
G1 X173.189 Y154.036 E.01688
G1 X172.762 Y154.013 E.01627
G1 X172.334 Y154.076 E.01642
G1 X171.907 Y154.239 E.01738
G1 X171.479 Y154.531 E.01968
G1 X170.624 Y155.329 E.04442
G1 X170.196 Y155.581 E.01886
G1 X169.769 Y155.702 E.01688
G1 X169.341 Y155.726 E.01627
G1 X168.914 Y155.663 E.01642
G1 X168.486 Y155.5 E.01738
G1 X168.058 Y155.207 E.01968
G1 X167.203 Y154.41 E.04442
G1 X166.776 Y154.157 E.01886
G1 X166.348 Y154.036 E.01688
G1 X165.921 Y154.013 E.01627
G1 X165.493 Y154.076 E.01642
G1 X165.066 Y154.239 E.01738
G1 X164.638 Y154.531 E.01968
G1 X163.783 Y155.329 E.04442
G1 X163.355 Y155.581 E.01886
G1 X162.928 Y155.702 E.01688
G1 X162.5 Y155.726 E.01627
G1 X162.073 Y155.663 E.01642
G1 X161.645 Y155.5 E.01738
G1 X161.217 Y155.207 E.01968
G1 X160.362 Y154.41 E.04442
G1 X159.935 Y154.157 E.01886
G1 X159.507 Y154.036 E.01688
G1 X159.08 Y154.013 E.01627
G1 X158.652 Y154.076 E.01642
G1 X158.224 Y154.239 E.01738
G1 X157.797 Y154.531 E.01968
G1 X156.942 Y155.329 E.04442
G1 X156.514 Y155.581 E.01886
G1 X156.087 Y155.702 E.01688
G1 X155.659 Y155.726 E.01627
G1 X155.232 Y155.663 E.01642
G1 X154.804 Y155.5 E.01738
G1 X154.376 Y155.207 E.01968
G1 X153.521 Y154.41 E.04442
G1 X153.094 Y154.157 E.01886
G1 X152.666 Y154.036 E.01688
G1 X152.239 Y154.013 E.01627
G1 X151.811 Y154.076 E.01642
G1 X151.383 Y154.239 E.01738
G1 X150.956 Y154.531 E.01968
G1 X150.101 Y155.329 E.04442
G1 X149.673 Y155.581 E.01886
G1 X149.246 Y155.702 E.01688
G1 X148.818 Y155.726 E.01627
G1 X148.391 Y155.663 E.01642
G1 X147.963 Y155.5 E.01738
G1 X147.535 Y155.207 E.01968
G1 X146.68 Y154.41 E.04442
G1 X146.253 Y154.157 E.01886
G1 X145.825 Y154.036 E.01688
G1 X145.398 Y154.013 E.01627
G1 X144.97 Y154.076 E.01642
G1 X144.542 Y154.239 E.01738
G1 X144.115 Y154.531 E.01968
G1 X143.26 Y155.329 E.04442
G1 X142.832 Y155.581 E.01886
G1 X142.405 Y155.702 E.01688
G1 X141.977 Y155.726 E.01627
G1 X141.549 Y155.663 E.01642
G1 X141.122 Y155.5 E.01738
G1 X140.694 Y155.207 E.01968
G1 X139.839 Y154.41 E.04442
G1 X139.412 Y154.157 E.01886
G1 X138.984 Y154.036 E.01688
G1 X138.557 Y154.013 E.01627
G1 X138.129 Y154.076 E.01642
G1 X137.701 Y154.239 E.01738
G1 X137.274 Y154.531 E.01968
G1 X136.419 Y155.329 E.04442
G1 X135.991 Y155.581 E.01886
G1 X135.564 Y155.702 E.01688
G1 X135.136 Y155.726 E.01627
G1 X134.708 Y155.663 E.01642
G1 X134.281 Y155.5 E.01738
G1 X133.853 Y155.207 E.01968
G1 X133.434 Y154.807 E.02201
G1 X133.434 Y153.213 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X133.434 Y154.807 E-.60571
G1 X133.728 Y155.088 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 8/47
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.04 I-.252 J1.191 P1  F60000
G1 X191.907 Y167.407 Z2.04
G1 Z1.88
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X190.663 Y166.697 Z2.28 F60000
G1 Z1.88
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X191.197 Y166.697 E.02028
G1 X191.197 Y165.637 E.04028
G1 X191.147 Y165.681 E.00253
G1 X190.719 Y165.906 E.01835
G1 X190.292 Y165.997 E.01661
G1 X189.864 Y165.993 E.01625
G1 X189.437 Y165.902 E.01661
G1 X189.009 Y165.709 E.01782
G1 X188.582 Y165.385 E.02037
G1 X188.154 Y164.959 E.02294
G1 X187.726 Y164.581 E.02169
G1 X187.299 Y164.356 E.01835
G1 X186.871 Y164.264 E.01661
G1 X186.444 Y164.269 E.01625
G1 X186.016 Y164.36 E.01661
G1 X185.589 Y164.553 E.01782
G1 X185.161 Y164.876 E.02037
G1 X184.734 Y165.303 E.02294
G1 X184.306 Y165.681 E.02169
G1 X183.878 Y165.906 E.01835
G1 X183.451 Y165.997 E.01661
G1 X183.023 Y165.993 E.01625
G1 X182.596 Y165.902 E.01661
G1 X182.168 Y165.709 E.01782
G1 X181.741 Y165.385 E.02037
G1 X181.313 Y164.959 E.02294
G1 X180.885 Y164.581 E.02169
G1 X180.458 Y164.356 E.01835
G1 X180.03 Y164.264 E.01661
G1 X179.603 Y164.269 E.01625
G1 X179.175 Y164.36 E.01661
G1 X178.748 Y164.553 E.01782
G1 X178.32 Y164.876 E.02037
G1 X177.892 Y165.303 E.02294
G1 X177.465 Y165.681 E.02169
G1 X177.037 Y165.906 E.01835
G1 X176.61 Y165.997 E.01661
G1 X176.182 Y165.993 E.01625
G1 X175.755 Y165.902 E.01661
G1 X175.327 Y165.709 E.01782
G1 X174.9 Y165.385 E.02037
G1 X174.472 Y164.959 E.02294
G1 X174.044 Y164.581 E.02169
G1 X173.617 Y164.356 E.01835
G1 X173.189 Y164.264 E.01661
G1 X172.762 Y164.269 E.01625
G1 X172.334 Y164.36 E.01661
G1 X171.907 Y164.553 E.01782
G1 X171.479 Y164.876 E.02037
G1 X171.051 Y165.303 E.02294
G1 X170.624 Y165.681 E.02169
G1 X170.196 Y165.906 E.01835
G1 X169.769 Y165.997 E.01661
G1 X169.341 Y165.993 E.01625
G1 X168.914 Y165.902 E.01661
G1 X168.486 Y165.709 E.01782
G1 X168.058 Y165.385 E.02037
G1 X167.631 Y164.959 E.02294
G1 X167.203 Y164.581 E.02169
G1 X166.776 Y164.356 E.01835
G1 X166.348 Y164.264 E.01661
G1 X165.921 Y164.269 E.01625
G1 X165.493 Y164.36 E.01661
G1 X165.066 Y164.553 E.01782
G1 X164.638 Y164.876 E.02037
G1 X164.21 Y165.303 E.02294
G1 X163.783 Y165.681 E.02169
G1 X163.355 Y165.906 E.01835
G1 X162.928 Y165.997 E.01661
G1 X162.5 Y165.993 E.01625
G1 X162.073 Y165.902 E.01661
G1 X161.645 Y165.709 E.01782
G1 X161.217 Y165.385 E.02037
G1 X160.79 Y164.959 E.02294
G1 X160.362 Y164.581 E.02169
G1 X159.935 Y164.356 E.01835
G1 X159.507 Y164.264 E.01661
G1 X159.08 Y164.269 E.01625
G1 X158.652 Y164.36 E.01661
G1 X158.224 Y164.553 E.01782
G1 X157.797 Y164.876 E.02037
G1 X157.369 Y165.303 E.02294
G1 X156.942 Y165.681 E.02169
G1 X156.514 Y165.906 E.01835
G1 X156.087 Y165.997 E.01661
G1 X155.659 Y165.993 E.01625
G1 X155.232 Y165.902 E.01661
G1 X154.804 Y165.709 E.01782
G1 X154.376 Y165.385 E.02037
G1 X153.949 Y164.959 E.02294
G1 X153.521 Y164.581 E.02169
G1 X153.094 Y164.356 E.01835
G1 X152.666 Y164.264 E.01661
G1 X152.239 Y164.269 E.01625
G1 X151.811 Y164.36 E.01661
G1 X151.383 Y164.553 E.01782
G1 X150.956 Y164.876 E.02037
G1 X150.528 Y165.303 E.02294
G1 X150.101 Y165.681 E.02169
G1 X149.673 Y165.906 E.01835
G1 X149.246 Y165.997 E.01661
G1 X148.818 Y165.993 E.01625
G1 X148.391 Y165.902 E.01661
G1 X147.963 Y165.709 E.01782
G1 X147.535 Y165.385 E.02037
G1 X147.108 Y164.959 E.02294
G1 X146.68 Y164.581 E.02169
G1 X146.253 Y164.356 E.01835
G1 X145.825 Y164.264 E.01661
G1 X145.398 Y164.269 E.01625
G1 X144.97 Y164.36 E.01661
G1 X144.542 Y164.553 E.01782
G1 X144.115 Y164.876 E.02037
G1 X143.687 Y165.303 E.02294
G1 X143.26 Y165.681 E.02169
G1 X142.832 Y165.906 E.01835
G1 X142.405 Y165.997 E.01661
G1 X141.977 Y165.993 E.01625
G1 X141.549 Y165.902 E.01661
G1 X141.122 Y165.709 E.01782
G1 X140.694 Y165.385 E.02037
G1 X140.267 Y164.959 E.02294
G1 X139.839 Y164.581 E.02169
G1 X139.412 Y164.356 E.01835
G1 X138.984 Y164.264 E.01661
G1 X138.557 Y164.269 E.01625
G1 X138.129 Y164.36 E.01661
G1 X137.701 Y164.553 E.01782
G1 X137.274 Y164.876 E.02037
G1 X136.846 Y165.303 E.02294
G1 X136.419 Y165.681 E.02169
G1 X135.991 Y165.906 E.01835
G1 X135.564 Y165.997 E.01661
G1 X135.136 Y165.993 E.01625
G1 X134.708 Y165.902 E.01661
G1 X134.281 Y165.709 E.01782
G1 X133.803 Y165.335 E.02304
G1 X133.803 Y162.216 E.1185
G1 X133.853 Y162.261 E.00255
G1 X134.281 Y162.485 E.01835
G1 X134.708 Y162.577 E.01661
G1 X135.136 Y162.572 E.01625
G1 X135.564 Y162.481 E.01661
G1 X135.991 Y162.288 E.01782
G1 X136.419 Y161.965 E.02037
G1 X136.846 Y161.538 E.02294
G1 X137.274 Y161.16 E.02169
G1 X137.701 Y160.935 E.01835
G1 X138.129 Y160.844 E.01661
G1 X138.557 Y160.849 E.01625
G1 X138.984 Y160.939 E.01661
G1 X139.412 Y161.132 E.01782
G1 X139.839 Y161.456 E.02037
G1 X140.267 Y161.882 E.02294
G1 X140.694 Y162.261 E.02169
G1 X141.122 Y162.485 E.01835
G1 X141.549 Y162.577 E.01661
G1 X141.977 Y162.572 E.01625
G1 X142.405 Y162.481 E.01661
G1 X142.832 Y162.288 E.01782
G1 X143.26 Y161.965 E.02037
G1 X143.687 Y161.538 E.02294
G1 X144.115 Y161.16 E.02169
G1 X144.542 Y160.935 E.01835
G1 X144.97 Y160.844 E.01661
G1 X145.398 Y160.849 E.01625
G1 X145.825 Y160.939 E.01661
G1 X146.253 Y161.132 E.01782
G1 X146.68 Y161.456 E.02037
G1 X147.108 Y161.882 E.02294
G1 X147.535 Y162.261 E.02169
G1 X147.963 Y162.485 E.01835
G1 X148.391 Y162.577 E.01661
G1 X148.818 Y162.572 E.01625
G1 X149.246 Y162.481 E.01661
G1 X149.673 Y162.288 E.01782
G1 X150.101 Y161.965 E.02037
G1 X150.528 Y161.538 E.02294
G1 X150.956 Y161.16 E.02169
G1 X151.383 Y160.935 E.01835
G1 X151.811 Y160.844 E.01661
G1 X152.239 Y160.849 E.01625
G1 X152.666 Y160.939 E.01661
G1 X153.094 Y161.132 E.01782
G1 X153.521 Y161.456 E.02037
G1 X153.949 Y161.882 E.02294
G1 X154.376 Y162.261 E.02169
G1 X154.804 Y162.485 E.01835
G1 X155.232 Y162.577 E.01661
G1 X155.659 Y162.572 E.01625
G1 X156.087 Y162.481 E.01661
G1 X156.514 Y162.288 E.01782
G1 X156.942 Y161.965 E.02037
G1 X157.369 Y161.538 E.02294
G1 X157.797 Y161.16 E.02169
G1 X158.224 Y160.935 E.01835
G1 X158.652 Y160.844 E.01661
G1 X159.08 Y160.849 E.01625
G1 X159.507 Y160.939 E.01661
G1 X159.935 Y161.132 E.01782
G1 X160.362 Y161.456 E.02037
G1 X160.79 Y161.882 E.02294
G1 X161.217 Y162.261 E.02169
G1 X161.645 Y162.485 E.01835
G1 X162.073 Y162.577 E.01661
G1 X162.5 Y162.572 E.01625
G1 X162.928 Y162.481 E.01661
G1 X163.355 Y162.288 E.01782
G1 X163.783 Y161.965 E.02037
G1 X164.21 Y161.538 E.02294
G1 X164.638 Y161.16 E.02169
G1 X165.066 Y160.935 E.01835
G1 X165.493 Y160.844 E.01661
G1 X165.921 Y160.849 E.01625
G1 X166.348 Y160.939 E.01661
G1 X166.776 Y161.132 E.01782
G1 X167.203 Y161.456 E.02037
G1 X167.631 Y161.882 E.02294
G1 X168.058 Y162.261 E.02169
G1 X168.486 Y162.485 E.01835
G1 X168.914 Y162.577 E.01661
G1 X169.341 Y162.572 E.01625
G1 X169.769 Y162.481 E.01661
G1 X170.196 Y162.288 E.01782
G1 X170.624 Y161.965 E.02037
G1 X171.051 Y161.538 E.02294
G1 X171.479 Y161.16 E.02169
G1 X171.907 Y160.935 E.01835
G1 X172.334 Y160.844 E.01661
G1 X172.762 Y160.849 E.01625
G1 X173.189 Y160.939 E.01661
G1 X173.617 Y161.132 E.01782
G1 X174.044 Y161.456 E.02037
G1 X174.472 Y161.882 E.02294
G1 X174.9 Y162.261 E.02169
G1 X175.327 Y162.485 E.01835
G1 X175.755 Y162.577 E.01661
G1 X176.182 Y162.572 E.01625
G1 X176.61 Y162.481 E.01661
G1 X177.037 Y162.288 E.01782
G1 X177.465 Y161.965 E.02037
G1 X177.892 Y161.538 E.02294
G1 X178.32 Y161.16 E.02169
G1 X178.748 Y160.935 E.01835
G1 X179.175 Y160.844 E.01661
G1 X179.603 Y160.849 E.01625
G1 X180.03 Y160.939 E.01661
G1 X180.458 Y161.132 E.01782
G1 X180.885 Y161.456 E.02037
G1 X181.313 Y161.882 E.02294
G1 X181.741 Y162.261 E.02169
G1 X182.168 Y162.485 E.01835
G1 X182.596 Y162.577 E.01661
G1 X183.023 Y162.572 E.01625
G1 X183.451 Y162.481 E.01661
G1 X183.878 Y162.288 E.01782
G1 X184.306 Y161.965 E.02037
G1 X184.734 Y161.538 E.02294
G1 X185.161 Y161.16 E.02169
G1 X185.589 Y160.935 E.01835
G1 X186.016 Y160.844 E.01661
G1 X186.444 Y160.849 E.01625
G1 X186.871 Y160.939 E.01661
G1 X187.299 Y161.132 E.01782
G1 X187.726 Y161.456 E.02037
G1 X188.154 Y161.882 E.02294
G1 X188.582 Y162.261 E.02169
G1 X189.009 Y162.485 E.01835
G1 X189.437 Y162.577 E.01661
G1 X189.864 Y162.572 E.01625
G1 X190.292 Y162.481 E.01661
G1 X190.719 Y162.288 E.01782
G1 X191.197 Y161.915 E.02303
G1 X191.197 Y158.796 E.11851
G1 X191.147 Y158.84 E.00253
G1 X190.719 Y159.065 E.01835
G1 X190.292 Y159.156 E.01661
G1 X189.864 Y159.152 E.01625
G1 X189.437 Y159.061 E.01661
G1 X189.009 Y158.868 E.01782
G1 X188.582 Y158.544 E.02037
G1 X188.154 Y158.118 E.02294
G1 X187.726 Y157.739 E.02169
G1 X187.299 Y157.515 E.01835
G1 X186.871 Y157.423 E.01661
G1 X186.444 Y157.428 E.01625
G1 X186.016 Y157.519 E.01661
G1 X185.589 Y157.712 E.01782
G1 X185.161 Y158.035 E.02037
G1 X184.734 Y158.462 E.02294
G1 X184.306 Y158.84 E.02169
G1 X183.878 Y159.065 E.01835
G1 X183.451 Y159.156 E.01661
G1 X183.023 Y159.152 E.01625
G1 X182.596 Y159.061 E.01661
G1 X182.168 Y158.868 E.01782
G1 X181.741 Y158.544 E.02037
G1 X181.313 Y158.118 E.02294
G1 X180.885 Y157.739 E.02169
G1 X180.458 Y157.515 E.01835
G1 X180.03 Y157.423 E.01661
G1 X179.603 Y157.428 E.01625
G1 X179.175 Y157.519 E.01661
G1 X178.748 Y157.712 E.01782
G1 X178.32 Y158.035 E.02037
G1 X177.892 Y158.462 E.02294
G1 X177.465 Y158.84 E.02169
G1 X177.037 Y159.065 E.01835
G1 X176.61 Y159.156 E.01661
G1 X176.182 Y159.152 E.01625
G1 X175.755 Y159.061 E.01661
G1 X175.327 Y158.868 E.01782
G1 X174.9 Y158.544 E.02037
G1 X174.472 Y158.118 E.02294
G1 X174.044 Y157.739 E.02169
G1 X173.617 Y157.515 E.01835
G1 X173.189 Y157.423 E.01661
G1 X172.762 Y157.428 E.01625
G1 X172.334 Y157.519 E.01661
G1 X171.907 Y157.712 E.01782
G1 X171.479 Y158.035 E.02037
G1 X171.051 Y158.462 E.02294
G1 X170.624 Y158.84 E.02169
G1 X170.196 Y159.065 E.01835
G1 X169.769 Y159.156 E.01661
G1 X169.341 Y159.152 E.01625
G1 X168.914 Y159.061 E.01661
G1 X168.486 Y158.868 E.01782
G1 X168.058 Y158.544 E.02037
G1 X167.631 Y158.118 E.02294
G1 X167.203 Y157.739 E.02169
G1 X166.776 Y157.515 E.01835
G1 X166.348 Y157.423 E.01661
G1 X165.921 Y157.428 E.01625
G1 X165.493 Y157.519 E.01661
G1 X165.066 Y157.712 E.01782
G1 X164.638 Y158.035 E.02037
G1 X164.21 Y158.462 E.02294
G1 X163.783 Y158.84 E.02169
G1 X163.355 Y159.065 E.01835
G1 X162.928 Y159.156 E.01661
G1 X162.5 Y159.152 E.01625
G1 X162.073 Y159.061 E.01661
G1 X161.645 Y158.868 E.01782
G1 X161.217 Y158.544 E.02037
G1 X160.79 Y158.118 E.02294
G1 X160.362 Y157.739 E.02169
G1 X159.935 Y157.515 E.01835
G1 X159.507 Y157.423 E.01661
G1 X159.08 Y157.428 E.01625
G1 X158.652 Y157.519 E.01661
G1 X158.224 Y157.712 E.01782
G1 X157.797 Y158.035 E.02037
G1 X157.369 Y158.462 E.02294
G1 X156.942 Y158.84 E.02169
G1 X156.514 Y159.065 E.01835
G1 X156.087 Y159.156 E.01661
G1 X155.659 Y159.152 E.01625
G1 X155.232 Y159.061 E.01661
G1 X154.804 Y158.868 E.01782
G1 X154.376 Y158.544 E.02037
G1 X153.949 Y158.118 E.02294
G1 X153.521 Y157.739 E.02169
G1 X153.094 Y157.515 E.01835
G1 X152.666 Y157.423 E.01661
G1 X152.239 Y157.428 E.01625
G1 X151.811 Y157.519 E.01661
G1 X151.383 Y157.712 E.01782
G1 X150.956 Y158.035 E.02037
G1 X150.528 Y158.462 E.02294
G1 X150.101 Y158.84 E.02169
G1 X149.673 Y159.065 E.01835
G1 X149.246 Y159.156 E.01661
G1 X148.818 Y159.152 E.01625
G1 X148.391 Y159.061 E.01661
G1 X147.963 Y158.868 E.01782
G1 X147.535 Y158.544 E.02037
G1 X147.108 Y158.118 E.02294
G1 X146.68 Y157.739 E.02169
G1 X146.253 Y157.515 E.01835
G1 X145.825 Y157.423 E.01661
G1 X145.398 Y157.428 E.01625
G1 X144.97 Y157.519 E.01661
M73 P50 R7
G1 X144.542 Y157.712 E.01782
G1 X144.115 Y158.035 E.02037
G1 X143.687 Y158.462 E.02294
G1 X143.26 Y158.84 E.02169
G1 X142.832 Y159.065 E.01835
G1 X142.405 Y159.156 E.01661
G1 X141.977 Y159.152 E.01625
G1 X141.549 Y159.061 E.01661
G1 X141.122 Y158.868 E.01782
G1 X140.694 Y158.544 E.02037
G1 X140.267 Y158.118 E.02294
G1 X139.839 Y157.739 E.02169
G1 X139.412 Y157.515 E.01835
G1 X138.984 Y157.423 E.01661
G1 X138.557 Y157.428 E.01625
G1 X138.129 Y157.519 E.01661
G1 X137.701 Y157.712 E.01782
G1 X137.274 Y158.035 E.02037
G1 X136.846 Y158.462 E.02294
G1 X136.419 Y158.84 E.02169
G1 X135.991 Y159.065 E.01835
G1 X135.564 Y159.156 E.01661
G1 X135.136 Y159.152 E.01625
G1 X134.708 Y159.061 E.01661
G1 X134.281 Y158.868 E.01782
G1 X133.803 Y158.494 E.02304
G1 X133.803 Y155.375 E.1185
G1 X133.853 Y155.42 E.00255
G1 X134.281 Y155.644 E.01835
G1 X134.708 Y155.736 E.01661
G1 X135.136 Y155.731 E.01625
G1 X135.564 Y155.64 E.01661
G1 X135.991 Y155.447 E.01782
G1 X136.419 Y155.124 E.02037
G1 X136.846 Y154.697 E.02294
G1 X137.274 Y154.319 E.02169
G1 X137.701 Y154.094 E.01835
G1 X138.129 Y154.003 E.01661
G1 X138.557 Y154.007 E.01625
G1 X138.984 Y154.098 E.01661
G1 X139.412 Y154.291 E.01782
G1 X139.839 Y154.615 E.02037
G1 X140.267 Y155.041 E.02294
G1 X140.694 Y155.42 E.02169
G1 X141.122 Y155.644 E.01835
G1 X141.549 Y155.736 E.01661
G1 X141.977 Y155.731 E.01625
G1 X142.405 Y155.64 E.01661
G1 X142.832 Y155.447 E.01782
G1 X143.26 Y155.124 E.02037
G1 X143.687 Y154.697 E.02294
G1 X144.115 Y154.319 E.02169
G1 X144.542 Y154.094 E.01835
G1 X144.97 Y154.003 E.01661
G1 X145.398 Y154.007 E.01625
G1 X145.825 Y154.098 E.01661
G1 X146.253 Y154.291 E.01782
G1 X146.68 Y154.615 E.02037
G1 X147.108 Y155.041 E.02294
G1 X147.535 Y155.42 E.02169
G1 X147.963 Y155.644 E.01835
G1 X148.391 Y155.736 E.01661
G1 X148.818 Y155.731 E.01625
G1 X149.246 Y155.64 E.01661
G1 X149.673 Y155.447 E.01782
G1 X150.101 Y155.124 E.02037
G1 X150.528 Y154.697 E.02294
G1 X150.956 Y154.319 E.02169
G1 X151.383 Y154.094 E.01835
G1 X151.811 Y154.003 E.01661
G1 X152.239 Y154.007 E.01625
G1 X152.666 Y154.098 E.01661
G1 X153.094 Y154.291 E.01782
G1 X153.521 Y154.615 E.02037
G1 X153.949 Y155.041 E.02294
G1 X154.376 Y155.42 E.02169
G1 X154.804 Y155.644 E.01835
G1 X155.232 Y155.736 E.01661
G1 X155.659 Y155.731 E.01625
G1 X156.087 Y155.64 E.01661
G1 X156.514 Y155.447 E.01782
G1 X156.942 Y155.124 E.02037
G1 X157.369 Y154.697 E.02294
G1 X157.797 Y154.319 E.02169
G1 X158.224 Y154.094 E.01835
G1 X158.652 Y154.003 E.01661
G1 X159.08 Y154.007 E.01625
G1 X159.507 Y154.098 E.01661
G1 X159.935 Y154.291 E.01782
G1 X160.362 Y154.615 E.02037
G1 X160.79 Y155.041 E.02294
G1 X161.217 Y155.42 E.02169
G1 X161.645 Y155.644 E.01835
G1 X162.073 Y155.736 E.01661
G1 X162.5 Y155.731 E.01625
G1 X162.928 Y155.64 E.01661
G1 X163.355 Y155.447 E.01782
G1 X163.783 Y155.124 E.02037
G1 X164.21 Y154.697 E.02294
G1 X164.638 Y154.319 E.02169
G1 X165.066 Y154.094 E.01835
G1 X165.493 Y154.003 E.01661
G1 X165.921 Y154.007 E.01625
G1 X166.348 Y154.098 E.01661
G1 X166.776 Y154.291 E.01782
G1 X167.203 Y154.615 E.02037
G1 X167.631 Y155.041 E.02294
G1 X168.058 Y155.42 E.02169
G1 X168.486 Y155.644 E.01835
G1 X168.914 Y155.736 E.01661
G1 X169.341 Y155.731 E.01625
G1 X169.769 Y155.64 E.01661
G1 X170.196 Y155.447 E.01782
G1 X170.624 Y155.124 E.02037
G1 X171.051 Y154.697 E.02294
G1 X171.479 Y154.319 E.02169
G1 X171.907 Y154.094 E.01835
G1 X172.334 Y154.003 E.01661
G1 X172.762 Y154.007 E.01625
G1 X173.189 Y154.098 E.01661
G1 X173.617 Y154.291 E.01782
G1 X174.044 Y154.615 E.02037
G1 X174.472 Y155.041 E.02294
G1 X174.9 Y155.42 E.02169
G1 X175.327 Y155.644 E.01835
G1 X175.755 Y155.736 E.01661
G1 X176.182 Y155.731 E.01625
G1 X176.61 Y155.64 E.01661
G1 X177.037 Y155.447 E.01782
G1 X177.465 Y155.124 E.02037
G1 X177.892 Y154.697 E.02294
G1 X178.32 Y154.319 E.02169
G1 X178.748 Y154.094 E.01835
G1 X179.175 Y154.003 E.01661
G1 X179.603 Y154.007 E.01625
G1 X180.03 Y154.098 E.01661
G1 X180.458 Y154.291 E.01782
G1 X180.885 Y154.615 E.02037
G1 X181.313 Y155.041 E.02294
G1 X181.741 Y155.42 E.02169
G1 X182.168 Y155.644 E.01835
G1 X182.596 Y155.736 E.01661
G1 X183.023 Y155.731 E.01625
G1 X183.451 Y155.64 E.01661
G1 X183.878 Y155.447 E.01782
G1 X184.306 Y155.124 E.02037
G1 X184.734 Y154.697 E.02294
G1 X185.161 Y154.319 E.02169
G1 X185.589 Y154.094 E.01835
G1 X186.016 Y154.003 E.01661
G1 X186.444 Y154.007 E.01625
G1 X186.871 Y154.098 E.01661
G1 X187.299 Y154.291 E.01782
G1 X187.726 Y154.615 E.02037
G1 X188.154 Y155.041 E.02294
G1 X188.582 Y155.42 E.02169
G1 X189.009 Y155.644 E.01835
G1 X189.437 Y155.736 E.01661
G1 X189.864 Y155.731 E.01625
G1 X190.292 Y155.64 E.01661
G1 X190.719 Y155.447 E.01782
G1 X191.197 Y155.074 E.02303
G1 X191.197 Y153.48 E.06056
M204 S10000
G1 X191.396 Y152.948 F60000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.391589
G1 F12000
M204 S8000
G1 X133.604 Y152.948 E1.87384
G1 X133.475 Y152.975 E.00427
G1 X133.448 Y153.104 E.00427
G1 X133.448 Y166.896 E.4472
G1 X133.475 Y167.025 E.00427
G1 X133.604 Y167.052 E.00427
G1 X191.396 Y167.052 E1.87384
G1 X191.525 Y167.025 E.00427
G1 X191.552 Y166.896 E.00427
G1 X191.552 Y153.104 E.4472
G1 X191.525 Y152.975 E.00427
G1 X191.455 Y152.96 E.00232
; CHANGE_LAYER
; Z_HEIGHT: 2.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
G1 X191.525 Y152.975 E-.0272
G1 X191.552 Y153.104 E-.05
G1 X191.552 Y154.901 E-.6828
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 9/47
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.28 I-1.216 J.035 P1  F60000
G1 X191.907 Y167.407 Z2.28
G1 Z2.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X191.002 Y167.242 Z2.52 F60000
G1 Z2.12
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.40042
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X191.54 Y166.29 E.05474
G1 X191.54 Y165.374 E.0458
G1 X190.599 Y167.04 E.09571
G1 X190.081 Y167.04 E.02588
G1 X191.54 Y164.459 E.14831
G1 X191.54 Y163.543 E.0458
G1 X189.564 Y167.04 E.20092
G1 X189.046 Y167.04 E.02588
G1 X191.54 Y162.628 E.25352
G1 X191.54 Y161.712 E.0458
G1 X188.529 Y167.04 E.30613
G1 X188.012 Y167.04 E.02588
G1 X191.54 Y160.797 E.35873
G1 X191.54 Y159.881 E.0458
G1 X187.494 Y167.04 E.41134
G1 X186.977 Y167.04 E.02588
G1 X191.54 Y158.966 E.46394
G1 X191.54 Y158.05 E.0458
G1 X186.46 Y167.04 E.51654
G1 X185.942 Y167.04 E.02588
G1 X191.54 Y157.135 E.56915
G1 X191.54 Y156.219 E.0458
M73 P50 R6
G1 X185.425 Y167.04 E.62175
G1 X184.908 Y167.04 E.02588
G1 X191.54 Y155.304 E.67436
G1 X191.54 Y154.388 E.0458
G1 X184.39 Y167.04 E.72696
G1 X183.873 Y167.04 E.02588
G1 X191.54 Y153.473 E.77957
G1 X191.54 Y152.96 E.02566
M73 P51 R6
G1 X191.312 Y152.96 E.01138
G1 X183.355 Y167.04 E.80904
G1 X182.838 Y167.04 E.02588
G1 X190.795 Y152.96 E.80904
G1 X190.278 Y152.96 E.02588
G1 X182.321 Y167.04 E.80904
G1 X181.803 Y167.04 E.02588
G1 X184.938 Y161.493 E.31876
G1 X184.398 Y161.98 E.03641
G1 X184.046 Y162.156 E.0197
G1 X181.286 Y167.04 E.28061
G1 X180.769 Y167.04 E.02588
G1 X183.39 Y162.401 E.26654
G1 X182.992 Y162.453 E.02008
G1 X182.853 Y162.436 E.007
G1 X180.251 Y167.04 E.26454
G1 X179.734 Y167.04 E.02588
G1 X182.38 Y162.358 E.26904
G1 X181.964 Y162.179 E.02266
G1 X179.216 Y167.04 E.27932
G1 X178.699 Y167.04 E.02588
G1 X181.598 Y161.91 E.29477
G1 X181.257 Y161.598 E.02313
G1 X178.182 Y167.04 E.31272
G1 X177.664 Y167.04 E.02588
G1 X180.923 Y161.273 E.33136
G1 X180.561 Y160.998 E.02274
G1 X177.147 Y167.04 E.34714
G1 X176.63 Y167.04 E.02588
G1 X180.148 Y160.815 E.35769
G1 X179.802 Y160.731 E.0178
G1 X179.677 Y160.732 E.00623
G1 X176.112 Y167.04 E.36246
G1 X175.595 Y167.04 E.02588
G1 X179.158 Y160.734 E.36232
G1 X178.639 Y160.737 E.02595
G1 X175.077 Y167.04 E.36217
G1 X174.56 Y167.04 E.02588
G1 X182.517 Y152.96 E.80904
G1 X183.034 Y152.96 E.02588
G1 X180.374 Y157.668 E.27054
G1 X180.773 Y157.878 E.02254
G1 X183.552 Y152.96 E.28258
G1 X184.069 Y152.96 E.02588
G1 X181.123 Y158.173 E.29952
G1 X181.46 Y158.493 E.02323
G1 X184.587 Y152.96 E.31793
G1 X185.104 Y152.96 E.02588
G1 X181.803 Y158.801 E.33563
G1 X182.175 Y159.058 E.02262
M73 P52 R6
G1 X185.621 Y152.96 E.3504
G1 X186.139 Y152.96 E.02588
G1 X182.602 Y159.218 E.35961
G1 X182.985 Y159.275 E.01939
G1 X183.093 Y159.264 E.00544
G1 X186.656 Y152.96 E.36223
G1 X187.173 Y152.96 E.02588
G1 X183.707 Y159.094 E.35244
G1 X184.143 Y158.858 E.0248
G1 X184.574 Y158.475 E.02882
G1 X187.691 Y152.96 E.31691
G1 X188.208 Y152.96 E.02588
G1 X185.235 Y158.222 E.30234
G1 X185.572 Y158.54 E.02321
G1 X188.726 Y152.96 E.32065
G1 X189.243 Y152.96 E.02588
G1 X185.909 Y158.859 E.33896
G1 X185.949 Y158.897 E.00276
G1 X185.815 Y159.136 E.0137
G1 X186.211 Y159.24 E.02052
G1 X189.875 Y152.758 E.37248
M106 S0
; WIPE_START
G1 X188.891 Y154.499 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X181.289 Y153.809 Z2.52 F60000
G1 X169.697 Y152.758 Z2.52
G1 Z2.12
G1 E.8 F1800
M106 S178.5
G1 F1500
M204 S8000
G1 X165.415 Y160.335 E.43538
G1 X165.059 Y160.384 E.018
G1 X166.625 Y157.613 E.15926
G1 X166.445 Y157.597 E.00906
G1 X169.065 Y152.96 E.26647
G1 X168.548 Y152.96 E.02588
G1 X165.951 Y157.556 E.2641
G1 X165.856 Y157.548 E.00474
G1 X165.395 Y157.623 E.02337
G1 X168.031 Y152.96 E.26796
G1 X167.513 Y152.96 E.02588
G1 X164.684 Y157.966 E.28766
G1 X164.389 Y158.14 E.01714
G1 X163.747 Y158.709 E.0429
G1 X166.996 Y152.96 E.33033
G1 X166.479 Y152.96 E.02588
G1 X162.953 Y159.198 E.35846
G1 X162.788 Y159.259 E.00878
G1 X162.394 Y159.272 E.01974
G1 X165.961 Y152.96 E.36269
G1 X165.444 Y152.96 E.02588
G1 X161.927 Y159.184 E.3576
G1 X161.52 Y158.988 E.02258
G1 X164.926 Y152.96 E.34638
G1 X164.409 Y152.96 E.02588
G1 X161.162 Y158.706 E.33015
G1 X160.826 Y158.385 E.02324
G1 X163.892 Y152.96 E.31173
G1 X163.374 Y152.96 E.02588
G1 X160.483 Y158.076 E.29398
G1 X160.116 Y157.81 E.02268
G1 X162.857 Y152.96 E.27866
G1 X162.34 Y152.96 E.02588
G1 X159.702 Y157.627 E.26817
G1 X159.324 Y157.46 E.0207
G1 X158.273 Y159.319 E.10681
G1 X158.685 Y159.427 E.0213
G1 X154.383 Y167.04 E.43743
G1 X154.9 Y167.04 E.02588
G1 X158.729 Y160.264 E.38933
G1 X158.934 Y160.461 E.0142
G1 X158.925 Y160.689 E.01142
G1 X159 Y160.701 E.00377
M73 P53 R6
G1 X155.417 Y167.04 E.36422
G1 X155.935 Y167.04 E.02588
G1 X159.474 Y160.778 E.35982
G1 X159.569 Y160.793 E.00482
G1 X159.905 Y160.931 E.01815
G1 X156.452 Y167.04 E.35103
G1 X156.969 Y167.04 E.02588
G1 X160.281 Y161.18 E.33672
G1 X160.624 Y161.489 E.02309
G1 X157.487 Y167.04 E.31896
G1 X158.004 Y167.04 E.02588
G1 X160.96 Y161.81 E.30051
G1 X161.309 Y162.107 E.02294
G1 X158.522 Y167.04 E.28345
G1 X159.039 Y167.04 E.02588
G1 X161.707 Y162.318 E.2713
G1 X161.774 Y162.353 E.00375
G1 X162.163 Y162.428 E.01982
G1 X159.556 Y167.04 E.26501
G1 X160.074 Y167.04 E.02588
G1 X162.68 Y162.428 E.265
G1 X162.898 Y162.413 E.01095
G1 X163.282 Y162.278 E.02033
G1 X160.591 Y167.04 E.2736
G1 X161.108 Y167.04 E.02588
G1 X164.101 Y161.745 E.30427
G1 X164.631 Y161.292 E.03489
G1 X165.017 Y161.04 E.02303
G1 X161.626 Y167.04 E.34477
G1 X162.143 Y167.04 E.02588
G1 X170.1 Y152.96 E.80904
G1 X170.618 Y152.96 E.02588
G1 X162.661 Y167.04 E.80904
G1 X163.178 Y167.04 E.02588
G1 X171.135 Y152.96 E.80904
G1 X171.652 Y152.96 E.02588
G1 X163.695 Y167.04 E.80904
G1 X164.213 Y167.04 E.02588
G1 X172.17 Y152.96 E.80904
G1 X172.687 Y152.96 E.02588
G1 X164.73 Y167.04 E.80904
G1 X165.247 Y167.04 E.02588
G1 X173.204 Y152.96 E.80904
G1 X173.722 Y152.96 E.02588
G1 X165.765 Y167.04 E.80904
G1 X166.282 Y167.04 E.02588
G1 X174.239 Y152.96 E.80904
G1 X174.757 Y152.96 E.02588
M73 P54 R6
G1 X166.8 Y167.04 E.80904
G1 X167.317 Y167.04 E.02588
G1 X175.274 Y152.96 E.80904
G1 X175.791 Y152.96 E.02588
G1 X167.834 Y167.04 E.80904
G1 X168.352 Y167.04 E.02588
G1 X176.309 Y152.96 E.80904
G1 X176.826 Y152.96 E.02588
G1 X168.869 Y167.04 E.80904
G1 X169.386 Y167.04 E.02588
G1 X177.343 Y152.96 E.80904
G1 X177.861 Y152.96 E.02588
G1 X169.904 Y167.04 E.80904
G1 X170.421 Y167.04 E.02588
G1 X178.378 Y152.96 E.80904
G1 X178.895 Y152.96 E.02588
G1 X170.938 Y167.04 E.80904
G1 X171.456 Y167.04 E.02588
G1 X179.413 Y152.96 E.80904
G1 X179.93 Y152.96 E.02588
G1 X171.973 Y167.04 E.80904
G1 X172.491 Y167.04 E.02588
G1 X180.448 Y152.96 E.80904
G1 X180.965 Y152.96 E.02588
G1 X173.008 Y167.04 E.80904
G1 X173.525 Y167.04 E.02588
M73 P55 R6
G1 X181.482 Y152.96 E.80904
G1 X182 Y152.96 E.02588
G1 X173.928 Y167.242 E.82067
M106 S0
; WIPE_START
G1 X174.912 Y165.501 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X167.306 Y166.127 Z2.52 F60000
G1 X153.751 Y167.242 Z2.52
G1 Z2.12
G1 E.8 F1800
M106 S178.5
G1 F1500
M204 S8000
G1 X161.822 Y152.96 E.82067
G1 X161.305 Y152.96 E.02588
G1 X153.348 Y167.04 E.80904
G1 X152.831 Y167.04 E.02588
G1 X160.788 Y152.96 E.80904
G1 X160.27 Y152.96 E.02588
G1 X152.313 Y167.04 E.80904
G1 X151.796 Y167.04 E.02588
G1 X159.753 Y152.96 E.80904
G1 X159.235 Y152.96 E.02588
G1 X151.278 Y167.04 E.80904
G1 X150.761 Y167.04 E.02588
G1 X158.718 Y152.96 E.80904
G1 X158.201 Y152.96 E.02588
G1 X150.244 Y167.04 E.80904
G1 X149.726 Y167.04 E.02588
G1 X157.683 Y152.96 E.80904
G1 X157.166 Y152.96 E.02588
G1 X149.209 Y167.04 E.80904
G1 X148.692 Y167.04 E.02588
M73 P56 R6
G1 X156.649 Y152.96 E.80904
G1 X156.131 Y152.96 E.02588
G1 X148.174 Y167.04 E.80904
G1 X147.657 Y167.04 E.02588
G1 X155.614 Y152.96 E.80904
G1 X155.096 Y152.96 E.02588
G1 X147.139 Y167.04 E.80904
G1 X146.622 Y167.04 E.02588
G1 X154.579 Y152.96 E.80904
G1 X154.062 Y152.96 E.02588
G1 X146.105 Y167.04 E.80904
G1 X145.587 Y167.04 E.02588
G1 X153.544 Y152.96 E.80904
G1 X153.027 Y152.96 E.02588
G1 X145.07 Y167.04 E.80904
G1 X144.553 Y167.04 E.02588
G1 X152.51 Y152.96 E.80904
G1 X151.992 Y152.96 E.02588
G1 X144.035 Y167.04 E.80904
G1 X143.518 Y167.04 E.02588
G1 X151.475 Y152.96 E.80904
G1 X150.957 Y152.96 E.02588
G1 X143 Y167.04 E.80904
G1 X142.483 Y167.04 E.02588
G1 X150.44 Y152.96 E.80904
G1 X149.923 Y152.96 E.02588
M73 P57 R6
G1 X145.77 Y160.308 E.42224
G1 X145.596 Y160.26 E.00903
G1 X146.662 Y158.373 E.10842
G1 X146.662 Y157.948 E.02126
G1 X146.605 Y157.915 E.0033
G1 X149.405 Y152.96 E.28471
G1 X148.888 Y152.96 E.02588
G1 X146.212 Y157.696 E.2721
G1 X145.765 Y157.571 E.02322
G1 X148.371 Y152.96 E.26497
G1 X147.853 Y152.96 E.02588
G1 X145.256 Y157.555 E.26405
G1 X145.157 Y157.554 E.00499
G1 X144.657 Y157.7 E.02601
G1 X147.336 Y152.96 E.27233
G1 X146.818 Y152.96 E.02588
G1 X143.848 Y158.217 E.30204
G1 X142.931 Y158.924 E.05796
G1 X146.301 Y152.96 E.34271
G1 X145.784 Y152.96 E.02588
G1 X142.228 Y159.252 E.36151
G1 X142.125 Y159.277 E.00534
G1 X141.712 Y159.25 E.0207
G1 X145.266 Y152.96 E.36144
G1 X144.749 Y152.96 E.02588
G1 X141.267 Y159.121 E.35399
G1 X140.877 Y158.896 E.02253
G1 X144.232 Y152.96 E.34106
G1 X143.714 Y152.96 E.02588
G1 X140.525 Y158.603 E.32423
G1 X140.192 Y158.278 E.0233
G1 X143.197 Y152.96 E.30556
G1 X142.68 Y152.96 E.02588
G1 X139.842 Y157.981 E.28849
G1 X139.464 Y157.734 E.02258
G1 X142.162 Y152.96 E.27431
G1 X141.645 Y152.96 E.02588
G1 X133.688 Y167.04 E.80904
G1 X134.205 Y167.04 E.02588
G1 X138.618 Y159.231 E.44873
G1 X138.899 Y159.304 E.01453
G1 X138.525 Y159.968 E.03813
G1 X138.628 Y160.129 E.00954
G1 X134.723 Y167.04 E.39713
G1 X135.24 Y167.04 E.02588
G1 X138.807 Y160.729 E.36266
G1 X139.241 Y160.875 E.02295
M73 P57 R5
G1 X135.757 Y167.04 E.35426
G1 X136.275 Y167.04 E.02588
G1 X139.636 Y161.092 E.34178
G1 X139.991 Y161.38 E.02286
G1 X136.792 Y167.04 E.32522
G1 X137.309 Y167.04 E.02588
G1 X140.322 Y161.709 E.30632
G1 X140.667 Y162.014 E.02304
G1 X137.827 Y167.04 E.28878
G1 X138.344 Y167.04 E.02588
M73 P58 R5
G1 X141.052 Y162.248 E.27535
G1 X141.117 Y162.286 E.00374
G1 X141.487 Y162.394 E.0193
G1 X138.861 Y167.04 E.26693
G1 X139.379 Y167.04 E.02588
G1 X141.977 Y162.443 E.26413
G1 X142.185 Y162.45 E.01042
G1 X142.546 Y162.351 E.01873
G1 X139.896 Y167.04 E.26942
G1 X140.414 Y167.04 E.02588
G1 X143.28 Y161.969 E.2914
G1 X143.773 Y161.616 E.03034
G1 X144.185 Y161.283 E.0265
G1 X140.931 Y167.04 E.33081
G1 X141.448 Y167.04 E.02588
G1 X144.98 Y160.791 E.35907
G1 X145.227 Y160.722 E.01281
G1 X145.527 Y160.739 E.01502
G1 X141.851 Y167.242 E.37369
M106 S0
; WIPE_START
G1 X142.835 Y165.501 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X135.281 Y166.593 Z2.52 F60000
G1 X133.258 Y166.886 Z2.52
G1 Z2.12
G1 E.8 F1800
M106 S178.5
G1 F1500
M204 S8000
G1 X141.127 Y152.96 E.80017
G1 X140.61 Y152.96 E.02588
G1 X133.46 Y165.612 E.72698
G1 X133.46 Y164.696 E.0458
G1 X140.093 Y152.96 E.67438
G1 X139.575 Y152.96 E.02588
G1 X133.46 Y163.781 E.62177
G1 X133.46 Y162.865 E.0458
G1 X139.058 Y152.96 E.56917
G1 X138.541 Y152.96 E.02588
G1 X133.46 Y161.95 E.51656
G1 X133.46 Y161.034 E.0458
G1 X138.023 Y152.96 E.46396
G1 X137.506 Y152.96 E.02588
G1 X133.46 Y160.119 E.41135
G1 X133.46 Y159.203 E.0458
G1 X136.988 Y152.96 E.35875
G1 X136.471 Y152.96 E.02588
G1 X133.46 Y158.288 E.30615
G1 X133.46 Y157.373 E.0458
G1 X135.954 Y152.96 E.25354
G1 X135.436 Y152.96 E.02588
G1 X133.46 Y156.457 E.20094
G1 X133.46 Y155.542 E.0458
G1 X134.919 Y152.96 E.14833
G1 X134.402 Y152.96 E.02588
G1 X133.46 Y154.626 E.09573
G1 X133.46 Y153.711 E.0458
G1 X133.999 Y152.758 E.05476
M106 S0
; CHANGE_LAYER
; Z_HEIGHT: 2.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F1500
G1 X133.46 Y153.711 E-.41597
G1 X133.46 Y154.616 E-.34403
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 10/47
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.52 I-.26 J1.189 P1  F60000
G1 X191.907 Y167.407 Z2.52
G1 Z2.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
M73 P59 R5
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X191 Y167.247 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X191.581 Y166.666 E.02887
G1 X191.581 Y166.144 E.01836
G1 X190.644 Y167.081 E.04658
G1 X190.123 Y167.081 E.01836
G1 X191.581 Y165.623 E.07254
G1 X191.581 Y165.101 E.01836
G1 X189.601 Y167.081 E.09851
G1 X189.079 Y167.081 E.01836
G1 X191.581 Y164.579 E.12447
G1 X191.581 Y164.057 E.01836
G1 X188.557 Y167.081 E.15043
G1 X188.035 Y167.081 E.01836
G1 X191.581 Y163.535 E.1764
G1 X191.581 Y163.013 E.01836
G1 X187.513 Y167.081 E.20236
G1 X186.992 Y167.081 E.01836
G1 X191.581 Y162.492 E.22832
G1 X191.581 Y161.97 E.01836
G1 X186.47 Y167.081 E.25429
G1 X185.948 Y167.081 E.01836
G1 X191.581 Y161.448 E.28025
G1 X191.581 Y160.926 E.01836
G1 X185.426 Y167.081 E.30621
G1 X184.904 Y167.081 E.01836
G1 X191.581 Y160.404 E.33218
G1 X191.581 Y159.882 E.01836
G1 X184.382 Y167.081 E.35814
G1 X183.86 Y167.081 E.01836
G1 X191.581 Y159.36 E.3841
G1 X191.581 Y158.839 E.01836
G1 X183.339 Y167.081 E.41007
G1 X182.817 Y167.081 E.01836
G1 X191.581 Y158.317 E.43603
G1 X191.581 Y157.795 E.01836
G1 X186.972 Y162.404 E.22931
G1 X186.972 Y161.882 E.01836
G1 X191.581 Y157.273 E.22931
G1 X191.581 Y156.751 E.01836
G1 X186.972 Y161.36 E.22931
G1 X186.972 Y160.838 E.01836
G1 X191.581 Y156.229 E.22931
G1 X191.581 Y155.708 E.01836
G1 X186.972 Y160.317 E.22931
G1 X186.972 Y159.795 E.01836
G1 X191.581 Y155.186 E.22931
G1 X191.581 Y154.664 E.01836
G1 X186.972 Y159.273 E.22931
G1 X186.972 Y158.751 E.01836
G1 X191.581 Y154.142 E.22931
G1 X191.581 Y153.62 E.01836
G1 X186.972 Y158.229 E.22931
G1 X186.972 Y157.707 E.01836
G1 X191.581 Y153.098 E.22931
G1 X191.581 Y152.919 E.0063
G1 X191.238 Y152.919 E.01206
G1 X186.914 Y157.244 E.21515
G1 X186.773 Y157.103 E.00698
G1 X186.532 Y157.103 E.00848
G1 X190.716 Y152.919 E.20816
G1 X190.194 Y152.919 E.01836
G1 X186.01 Y157.103 E.20816
G1 X185.488 Y157.103 E.01836
G1 X189.672 Y152.919 E.20816
G1 X189.15 Y152.919 E.01836
G1 X184.967 Y157.103 E.20816
G1 X184.445 Y157.103 E.01836
G1 X188.629 Y152.919 E.20816
G1 X188.107 Y152.919 E.01836
G1 X183.923 Y157.103 E.20816
G1 X183.401 Y157.103 E.01836
G1 X187.585 Y152.919 E.20816
G1 X187.063 Y152.919 E.01836
G1 X182.879 Y157.103 E.20816
G1 X182.357 Y157.103 E.01836
G1 X186.541 Y152.919 E.20816
G1 X186.019 Y152.919 E.01836
G1 X181.835 Y157.103 E.20816
G1 X181.314 Y157.103 E.01836
G1 X185.498 Y152.919 E.20816
G1 X184.976 Y152.919 E.01836
G1 X180.792 Y157.103 E.20816
G1 X180.27 Y157.103 E.01836
G1 X184.454 Y152.919 E.20816
G1 X183.932 Y152.919 E.01836
G1 X179.748 Y157.103 E.20816
G1 X179.226 Y157.103 E.01836
G1 X183.41 Y152.919 E.20816
G1 X182.888 Y152.919 E.01836
G1 X178.704 Y157.103 E.20816
G1 X178.227 Y157.103 E.0168
G1 X178.028 Y157.302 E.00988
G1 X178.028 Y157.779 E.0168
G1 X168.727 Y167.081 E.46277
G1 X169.249 Y167.081 E.01836
G1 X178.028 Y158.301 E.4368
G1 X178.028 Y158.823 E.01836
G1 X169.771 Y167.081 E.41084
G1 X170.293 Y167.081 E.01836
G1 X178.028 Y159.345 E.38488
G1 X178.028 Y159.867 E.01836
G1 X170.814 Y167.081 E.35891
G1 X171.336 Y167.081 E.01836
G1 X178.028 Y160.389 E.33295
G1 X178.028 Y160.91 E.01836
G1 X171.858 Y167.081 E.30699
G1 X172.38 Y167.081 E.01836
G1 X178.028 Y161.432 E.28103
G1 X178.028 Y161.954 E.01836
G1 X172.902 Y167.081 E.25506
G1 X173.424 Y167.081 E.01836
G1 X178.028 Y162.476 E.2291
G1 X178.028 Y162.698 E.00782
G1 X178.178 Y162.848 E.00745
G1 X173.945 Y167.081 E.21059
G1 X174.467 Y167.081 E.01836
G1 X178.651 Y162.897 E.20816
G1 X179.173 Y162.897 E.01836
G1 X174.989 Y167.081 E.20816
G1 X175.511 Y167.081 E.01836
G1 X179.695 Y162.897 E.20816
G1 X180.217 Y162.897 E.01836
G1 X176.033 Y167.081 E.20816
G1 X176.555 Y167.081 E.01836
G1 X180.739 Y162.897 E.20816
G1 X181.26 Y162.897 E.01836
G1 X177.076 Y167.081 E.20816
G1 X177.598 Y167.081 E.01836
G1 X181.782 Y162.897 E.20816
G1 X182.304 Y162.897 E.01836
G1 X178.12 Y167.081 E.20816
G1 X178.642 Y167.081 E.01836
G1 X182.826 Y162.897 E.20816
G1 X183.348 Y162.897 E.01836
G1 X179.164 Y167.081 E.20816
G1 X179.686 Y167.081 E.01836
G1 X183.87 Y162.897 E.20816
G1 X184.392 Y162.897 E.01836
G1 X180.208 Y167.081 E.20816
G1 X180.729 Y167.081 E.01836
G1 X184.913 Y162.897 E.20816
G1 X185.435 Y162.897 E.01836
G1 X181.251 Y167.081 E.20816
G1 X181.773 Y167.081 E.01836
G1 X185.957 Y162.897 E.20816
G1 X186.479 Y162.897 E.01836
G1 X182.129 Y167.246 E.21641
; WIPE_START
G1 X183.543 Y165.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.588 Y162.425 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X186.588 Y160.831 E.06056
G1 X186.444 Y160.752 E.00625
G1 X185.588 Y160.533 E.03354
G1 X185.161 Y160.579 E.01634
G1 X184.733 Y160.897 E.02025
G1 X183.878 Y162.073 E.05525
G1 X183.451 Y162.436 E.02129
G1 X183.308 Y162.513 E.00616
G1 X181.305 Y162.513 E.0761
G1 X180.458 Y161.347 E.05477
G1 X180.03 Y160.985 E.02129
G1 X179.603 Y160.752 E.01849
G1 X178.747 Y160.533 E.03354
G1 X178.412 Y160.569 E.01282
G1 X178.412 Y158.388 E.08285
G1 X178.747 Y157.927 E.02168
G1 X179.175 Y157.564 E.02129
G1 X179.318 Y157.487 E.00616
G1 X181.32 Y157.487 E.07609
G1 X182.168 Y158.653 E.05477
G1 X182.595 Y159.015 E.02129
G1 X183.023 Y159.248 E.01849
G1 X183.878 Y159.467 E.03354
G1 X184.306 Y159.421 E.01634
G1 X184.733 Y159.103 E.02025
G1 X185.588 Y157.927 E.05525
G1 X186.016 Y157.564 E.02129
G1 X186.159 Y157.487 E.00616
G1 X184.565 Y157.487 E.06056
; WIPE_START
G1 X186.159 Y157.487 E-.60572
G1 X186.016 Y157.564 E-.06165
G1 X185.83 Y157.722 E-.09263
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.058 Y154.202 Z2.76 F60000
G1 X176.27 Y152.753 Z2.76
G1 Z2.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X167.022 Y162.002 E.46014
G1 X167.022 Y161.48 E.01836
G1 X175.583 Y152.919 E.42592
G1 X175.061 Y152.919 E.01836
G1 X167.022 Y160.958 E.39996
G1 X167.022 Y160.436 E.01836
G1 X174.539 Y152.919 E.374
G1 X174.017 Y152.919 E.01836
G1 X167.022 Y159.915 E.34803
G1 X167.022 Y159.393 E.01836
G1 X173.495 Y152.919 E.32207
G1 X172.973 Y152.919 E.01836
G1 X167.022 Y158.871 E.29611
G1 X167.022 Y158.349 E.01836
G1 X172.451 Y152.919 E.27014
G1 X171.93 Y152.919 E.01836
G1 X167.022 Y157.827 E.24418
G1 X167.022 Y157.305 E.01836
G1 X171.408 Y152.919 E.21822
G1 X170.886 Y152.919 E.01836
G1 X166.702 Y157.103 E.20816
G1 X166.18 Y157.103 E.01836
M73 P60 R5
G1 X170.364 Y152.919 E.20816
G1 X169.842 Y152.919 E.01836
G1 X165.658 Y157.103 E.20816
G1 X165.136 Y157.103 E.01836
G1 X169.32 Y152.919 E.20816
G1 X168.799 Y152.919 E.01836
G1 X164.615 Y157.103 E.20816
G1 X164.093 Y157.103 E.01836
G1 X168.277 Y152.919 E.20816
G1 X167.755 Y152.919 E.01836
G1 X163.571 Y157.103 E.20816
G1 X163.049 Y157.103 E.01836
G1 X167.233 Y152.919 E.20816
G1 X166.711 Y152.919 E.01836
G1 X162.527 Y157.103 E.20816
G1 X162.005 Y157.103 E.01836
G1 X166.189 Y152.919 E.20816
G1 X165.667 Y152.919 E.01836
G1 X161.484 Y157.103 E.20816
G1 X160.962 Y157.103 E.01836
G1 X165.146 Y152.919 E.20816
G1 X164.624 Y152.919 E.01836
G1 X160.44 Y157.103 E.20816
G1 X159.918 Y157.103 E.01836
G1 X164.102 Y152.919 E.20816
G1 X163.58 Y152.919 E.01836
G1 X159.396 Y157.103 E.20816
G1 X158.874 Y157.103 E.01836
G1 X163.058 Y152.919 E.20816
G1 X162.536 Y152.919 E.01836
G1 X148.375 Y167.081 E.70457
G1 X148.897 Y167.081 E.01836
G1 X157.978 Y157.999 E.45183
G1 X157.978 Y158.521 E.01836
G1 X149.419 Y167.081 E.42586
G1 X149.941 Y167.081 E.01836
G1 X157.978 Y159.043 E.3999
G1 X157.978 Y159.565 E.01836
G1 X150.462 Y167.081 E.37394
G1 X150.984 Y167.081 E.01836
G1 X157.978 Y160.087 E.34797
G1 X157.978 Y160.609 E.01836
G1 X151.506 Y167.081 E.32201
G1 X152.028 Y167.081 E.01836
G1 X157.978 Y161.13 E.29605
G1 X157.978 Y161.652 E.01836
G1 X152.55 Y167.081 E.27008
G1 X153.072 Y167.081 E.01836
G1 X157.978 Y162.174 E.24412
G1 X157.978 Y162.696 E.01836
G1 X153.593 Y167.081 E.21816
G1 X154.115 Y167.081 E.01836
G1 X158.299 Y162.897 E.20816
G1 X158.821 Y162.897 E.01836
G1 X154.637 Y167.081 E.20816
G1 X155.159 Y167.081 E.01836
G1 X159.343 Y162.897 E.20816
G1 X159.865 Y162.897 E.01836
G1 X155.681 Y167.081 E.20816
G1 X156.203 Y167.081 E.01836
G1 X160.387 Y162.897 E.20816
G1 X160.909 Y162.897 E.01836
G1 X156.725 Y167.081 E.20816
G1 X157.246 Y167.081 E.01836
G1 X161.43 Y162.897 E.20816
G1 X161.952 Y162.897 E.01836
G1 X157.768 Y167.081 E.20816
G1 X158.29 Y167.081 E.01836
G1 X162.474 Y162.897 E.20816
G1 X162.996 Y162.897 E.01836
G1 X158.812 Y167.081 E.20816
G1 X159.334 Y167.081 E.01836
G1 X163.518 Y162.897 E.20816
G1 X164.04 Y162.897 E.01836
G1 X159.856 Y167.081 E.20816
G1 X160.377 Y167.081 E.01836
G1 X164.561 Y162.897 E.20816
G1 X165.083 Y162.897 E.01836
G1 X160.899 Y167.081 E.20816
G1 X161.421 Y167.081 E.01836
G1 X165.605 Y162.897 E.20816
G1 X166.127 Y162.897 E.01836
G1 X161.943 Y167.081 E.20816
G1 X162.465 Y167.081 E.01836
G1 X176.626 Y152.919 E.70457
G1 X177.148 Y152.919 E.01836
G1 X162.987 Y167.081 E.70457
G1 X163.509 Y167.081 E.01836
G1 X177.67 Y152.919 E.70457
G1 X178.192 Y152.919 E.01836
G1 X164.03 Y167.081 E.70457
G1 X164.552 Y167.081 E.01836
G1 X178.714 Y152.919 E.70457
G1 X179.235 Y152.919 E.01836
G1 X165.074 Y167.081 E.70457
G1 X165.596 Y167.081 E.01836
G1 X179.757 Y152.919 E.70457
G1 X180.279 Y152.919 E.01836
G1 X166.118 Y167.081 E.70457
G1 X166.64 Y167.081 E.01836
G1 X180.801 Y152.919 E.70457
G1 X181.323 Y152.919 E.01836
G1 X167.161 Y167.081 E.70457
G1 X167.683 Y167.081 E.01836
G1 X181.845 Y152.919 E.70457
G1 X182.367 Y152.919 E.01836
G1 X168.039 Y167.247 E.71282
; WIPE_START
G1 X169.454 Y165.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.327 Y162.513 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.638 Y162.513 E.01183
G1 X166.638 Y161.231 E.04873
G1 X166.348 Y160.985 E.01444
G1 X165.921 Y160.752 E.01849
G1 X165.065 Y160.533 E.03354
G1 X164.638 Y160.579 E.01634
G1 X164.21 Y160.897 E.02025
G1 X163.355 Y162.073 E.05525
G1 X162.928 Y162.436 E.02129
G1 X162.785 Y162.513 E.00616
G1 X160.782 Y162.513 E.0761
G1 X159.935 Y161.347 E.05477
G1 X159.507 Y160.985 E.02129
G1 X159.08 Y160.752 E.01849
G1 X158.362 Y160.568 E.02815
G1 X158.362 Y157.81 E.10479
G1 X158.652 Y157.564 E.01445
G1 X158.794 Y157.487 E.00616
G1 X160.797 Y157.487 E.07609
G1 X161.645 Y158.653 E.05477
G1 X162.072 Y159.015 E.02129
G1 X162.5 Y159.248 E.01849
G1 X163.355 Y159.467 E.03354
G1 X163.783 Y159.421 E.01634
G1 X164.21 Y159.103 E.02025
G1 X165.065 Y157.927 E.05525
G1 X165.493 Y157.564 E.02129
G1 X165.636 Y157.487 E.00616
G1 X164.042 Y157.487 E.06056
; WIPE_START
G1 X165.636 Y157.487 E-.60572
G1 X165.493 Y157.564 E-.06165
G1 X165.307 Y157.722 E-.09263
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X157.675 Y157.64 Z2.76 F60000
G1 X143.519 Y157.487 Z2.76
G1 Z2.36
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X145.112 Y157.487 E.06056
G1 X144.97 Y157.564 E.00616
G1 X144.542 Y157.927 E.02129
G1 X143.687 Y159.103 E.05525
G1 X143.26 Y159.421 E.02025
G1 X142.832 Y159.467 E.01634
G1 X141.977 Y159.248 E.03354
G1 X141.549 Y159.015 E.01849
G1 X141.122 Y158.653 E.02129
G1 X140.274 Y157.487 E.05477
G1 X138.312 Y157.487 E.07456
G1 X138.312 Y160.69 E.12169
G1 X138.556 Y160.752 E.00959
G1 X138.984 Y160.985 E.01849
G1 X139.412 Y161.347 E.02129
G1 X140.259 Y162.513 E.05477
G1 X142.262 Y162.513 E.0761
G1 X142.405 Y162.436 E.00616
G1 X142.832 Y162.073 E.02129
G1 X143.687 Y160.897 E.05525
G1 X144.115 Y160.579 E.02025
G1 X144.542 Y160.533 E.01634
G1 X145.398 Y160.752 E.03354
G1 X145.825 Y160.985 E.01849
G1 X146.253 Y161.347 E.02129
G1 X146.688 Y161.946 E.02814
G1 X146.688 Y160.352 E.06056
; WIPE_START
G1 X146.688 Y161.946 E-.60572
G1 X146.449 Y161.618 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.687 Y167.247 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X162.015 Y152.919 E.71282
G1 X161.493 Y152.919 E.01836
G1 X147.331 Y167.081 E.70457
G1 X146.809 Y167.081 E.01836
G1 X160.971 Y152.919 E.70457
G1 X160.449 Y152.919 E.01836
G1 X146.288 Y167.081 E.70457
G1 X145.766 Y167.081 E.01836
G1 X159.927 Y152.919 E.70457
G1 X159.405 Y152.919 E.01836
G1 X145.244 Y167.081 E.70457
G1 X144.722 Y167.081 E.01836
G1 X158.883 Y152.919 E.70457
G1 X158.362 Y152.919 E.01836
G1 X144.2 Y167.081 E.70457
G1 X143.678 Y167.081 E.01836
G1 X157.84 Y152.919 E.70457
G1 X157.318 Y152.919 E.01836
G1 X143.157 Y167.081 E.70457
G1 X142.635 Y167.081 E.01836
G1 X156.796 Y152.919 E.70457
G1 X156.274 Y152.919 E.01836
G1 X147.072 Y162.122 E.45785
G1 X147.072 Y161.6 E.01836
G1 X155.752 Y152.919 E.43189
G1 X155.231 Y152.919 E.01836
G1 X147.072 Y161.078 E.40593
G1 X147.072 Y160.556 E.01836
G1 X154.709 Y152.919 E.37996
G1 X154.187 Y152.919 E.01836
G1 X147.072 Y160.035 E.354
G1 X147.072 Y159.513 E.01836
G1 X153.665 Y152.919 E.32804
G1 X153.143 Y152.919 E.01836
G1 X147.072 Y158.991 E.30207
G1 X147.072 Y158.469 E.01836
G1 X152.621 Y152.919 E.27611
G1 X152.1 Y152.919 E.01836
G1 X147.072 Y157.947 E.25015
G1 X147.072 Y157.425 E.01836
G1 X151.578 Y152.919 E.22418
G1 X151.056 Y152.919 E.01836
G1 X146.872 Y157.103 E.20816
G1 X146.35 Y157.103 E.01836
G1 X150.534 Y152.919 E.20816
G1 X150.012 Y152.919 E.01836
G1 X145.828 Y157.103 E.20816
M73 P61 R5
G1 X145.306 Y157.103 E.01836
G1 X149.49 Y152.919 E.20816
G1 X148.968 Y152.919 E.01836
G1 X144.784 Y157.103 E.20816
G1 X144.263 Y157.103 E.01836
G1 X148.447 Y152.919 E.20816
G1 X147.925 Y152.919 E.01836
G1 X143.741 Y157.103 E.20816
G1 X143.219 Y157.103 E.01836
G1 X147.403 Y152.919 E.20816
G1 X146.881 Y152.919 E.01836
G1 X142.697 Y157.103 E.20816
G1 X142.175 Y157.103 E.01836
G1 X146.359 Y152.919 E.20816
G1 X145.837 Y152.919 E.01836
G1 X141.653 Y157.103 E.20816
G1 X141.132 Y157.103 E.01836
G1 X145.316 Y152.919 E.20816
G1 X144.794 Y152.919 E.01836
G1 X140.61 Y157.103 E.20816
G1 X140.088 Y157.103 E.01836
G1 X144.272 Y152.919 E.20816
G1 X143.75 Y152.919 E.01836
G1 X139.566 Y157.103 E.20816
G1 X139.044 Y157.103 E.01836
G1 X143.228 Y152.919 E.20816
G1 X142.706 Y152.919 E.01836
G1 X138.522 Y157.103 E.20816
G1 X138.127 Y157.103 E.01392
G1 X137.928 Y157.302 E.00988
G1 X137.928 Y157.697 E.01392
G1 X133.419 Y162.206 E.22433
G1 X133.419 Y162.728 E.01836
G1 X137.928 Y158.219 E.22433
G1 X137.928 Y158.741 E.01836
G1 X133.419 Y163.25 E.22433
G1 X133.419 Y163.772 E.01836
G1 X137.928 Y159.263 E.22433
G1 X137.928 Y159.785 E.01836
G1 X133.419 Y164.294 E.22433
G1 X133.419 Y164.816 E.01836
G1 X137.928 Y160.307 E.22433
G1 X137.928 Y160.828 E.01836
G1 X133.419 Y165.337 E.22433
G1 X133.419 Y165.859 E.01836
G1 X137.928 Y161.35 E.22433
G1 X137.928 Y161.872 E.01836
G1 X133.419 Y166.381 E.22433
G1 X133.419 Y166.903 E.01836
G1 X137.928 Y162.394 E.22433
G1 X137.928 Y162.698 E.0107
G1 X138.037 Y162.807 E.00541
G1 X133.763 Y167.081 E.21263
G1 X134.285 Y167.081 E.01836
G1 X138.469 Y162.897 E.20816
G1 X138.991 Y162.897 E.01836
G1 X134.807 Y167.081 E.20816
G1 X135.329 Y167.081 E.01836
G1 X139.513 Y162.897 E.20816
G1 X140.035 Y162.897 E.01836
G1 X135.851 Y167.081 E.20816
G1 X136.373 Y167.081 E.01836
G1 X140.557 Y162.897 E.20816
G1 X141.078 Y162.897 E.01836
G1 X136.894 Y167.081 E.20816
G1 X137.416 Y167.081 E.01836
G1 X141.6 Y162.897 E.20816
G1 X142.122 Y162.897 E.01836
G1 X137.938 Y167.081 E.20816
G1 X138.46 Y167.081 E.01836
G1 X142.644 Y162.897 E.20816
G1 X143.166 Y162.897 E.01836
G1 X138.982 Y167.081 E.20816
G1 X139.504 Y167.081 E.01836
G1 X143.688 Y162.897 E.20816
G1 X144.209 Y162.897 E.01836
G1 X140.025 Y167.081 E.20816
G1 X140.547 Y167.081 E.01836
G1 X144.731 Y162.897 E.20816
G1 X145.253 Y162.897 E.01836
G1 X141.069 Y167.081 E.20816
G1 X141.591 Y167.081 E.01836
G1 X145.775 Y162.897 E.20816
G1 X146.297 Y162.897 E.01836
G1 X141.947 Y167.247 E.21641
; WIPE_START
G1 X143.361 Y165.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X136.26 Y163.035 Z2.76 F60000
G1 X133.253 Y161.85 Z2.76
G1 Z2.36
G1 E.8 F1800
G1 F12195.123
M204 S8000
G1 X142.184 Y152.919 E.44434
G1 X141.663 Y152.919 E.01836
G1 X133.419 Y161.163 E.41013
G1 X133.419 Y160.641 E.01836
G1 X141.141 Y152.919 E.38416
G1 X140.619 Y152.919 E.01836
G1 X133.419 Y160.119 E.3582
G1 X133.419 Y159.597 E.01836
G1 X140.097 Y152.919 E.33224
G1 X139.575 Y152.919 E.01836
G1 X133.419 Y159.075 E.30627
G1 X133.419 Y158.553 E.01836
G1 X139.053 Y152.919 E.28031
G1 X138.532 Y152.919 E.01836
G1 X133.419 Y158.032 E.25435
G1 X133.419 Y157.51 E.01836
G1 X138.01 Y152.919 E.22838
G1 X137.488 Y152.919 E.01836
G1 X133.419 Y156.988 E.20242
G1 X133.419 Y156.466 E.01836
G1 X136.966 Y152.919 E.17646
G1 X136.444 Y152.919 E.01836
G1 X133.419 Y155.944 E.15049
G1 X133.419 Y155.422 E.01836
G1 X135.922 Y152.919 E.12453
G1 X135.4 Y152.919 E.01836
G1 X133.419 Y154.9 E.09857
G1 X133.419 Y154.379 E.01836
G1 X134.879 Y152.919 E.0726
G1 X134.357 Y152.919 E.01836
G1 X133.419 Y153.857 E.04664
G1 X133.419 Y153.335 E.01836
G1 X134.001 Y152.753 E.02893
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12195.123
G1 X133.419 Y153.335 E-.31247
G1 X133.419 Y153.857 E-.1983
G1 X133.883 Y153.393 E-.24923
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 11/47
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.76 I-.286 J1.183 P1  F60000
G1 X191.907 Y167.407 Z2.76
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X191.746 Y162.371 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X186.972 Y157.596 E.23755
G1 X186.972 Y158.118 E.01836
G1 X191.581 Y162.727 E.2293
G1 X191.581 Y163.249 E.01836
G1 X186.972 Y158.64 E.2293
G1 X186.972 Y159.162 E.01836
G1 X191.581 Y163.771 E.2293
G1 X191.581 Y164.293 E.01836
G1 X186.972 Y159.684 E.2293
G1 X186.972 Y160.206 E.01836
G1 X191.581 Y164.814 E.2293
G1 X191.581 Y165.336 E.01836
G1 X186.972 Y160.727 E.2293
G1 X186.972 Y161.249 E.01836
G1 X191.581 Y165.858 E.2293
G1 X191.581 Y166.38 E.01836
G1 X186.972 Y161.771 E.2293
G1 X186.972 Y162.293 E.01836
G1 X191.581 Y166.902 E.2293
G1 X191.581 Y167.081 E.00629
G1 X191.238 Y167.081 E.01207
G1 X186.914 Y162.757 E.21513
G1 X186.773 Y162.897 E.00698
G1 X186.532 Y162.897 E.00849
G1 X190.716 Y167.081 E.20815
G1 X190.194 Y167.081 E.01836
G1 X186.01 Y162.897 E.20815
G1 X185.488 Y162.897 E.01836
G1 X189.672 Y167.081 E.20815
G1 X189.15 Y167.081 E.01836
G1 X184.966 Y162.897 E.20815
G1 X184.445 Y162.897 E.01836
G1 X188.628 Y167.081 E.20815
G1 X188.107 Y167.081 E.01836
G1 X183.923 Y162.897 E.20815
G1 X183.401 Y162.897 E.01836
G1 X187.585 Y167.081 E.20815
G1 X187.063 Y167.081 E.01836
G1 X182.879 Y162.897 E.20815
G1 X182.357 Y162.897 E.01836
G1 X186.541 Y167.081 E.20815
G1 X186.019 Y167.081 E.01836
G1 X181.835 Y162.897 E.20815
G1 X181.314 Y162.897 E.01836
G1 X185.497 Y167.081 E.20815
G1 X184.975 Y167.081 E.01836
G1 X180.792 Y162.897 E.20815
G1 X180.27 Y162.897 E.01836
G1 X184.454 Y167.081 E.20815
G1 X183.932 Y167.081 E.01836
G1 X179.748 Y162.897 E.20815
G1 X179.226 Y162.897 E.01836
G1 X183.41 Y167.081 E.20815
G1 X182.888 Y167.081 E.01836
G1 X178.704 Y162.897 E.20815
G1 X178.227 Y162.897 E.0168
G1 X178.028 Y162.698 E.00988
G1 X178.028 Y162.221 E.0168
G1 X168.727 Y152.919 E.46277
G1 X169.249 Y152.919 E.01836
G1 X178.028 Y161.699 E.4368
G1 X178.028 Y161.177 E.01836
G1 X169.771 Y152.919 E.41084
G1 X170.292 Y152.919 E.01836
M73 P62 R5
G1 X178.028 Y160.655 E.38488
G1 X178.028 Y160.133 E.01836
G1 X170.814 Y152.919 E.35891
G1 X171.336 Y152.919 E.01836
G1 X178.028 Y159.612 E.33295
G1 X178.028 Y159.09 E.01836
G1 X171.858 Y152.919 E.30699
G1 X172.38 Y152.919 E.01836
G1 X178.028 Y158.568 E.28102
G1 X178.028 Y158.046 E.01836
G1 X172.902 Y152.919 E.25506
G1 X173.423 Y152.919 E.01836
G1 X178.028 Y157.524 E.2291
G1 X178.028 Y157.302 E.00782
G1 X178.178 Y157.152 E.00745
G1 X173.945 Y152.919 E.21058
G1 X174.467 Y152.919 E.01836
G1 X178.651 Y157.103 E.20815
G1 X179.173 Y157.103 E.01836
G1 X174.989 Y152.919 E.20815
G1 X175.511 Y152.919 E.01836
G1 X179.695 Y157.103 E.20815
G1 X180.216 Y157.103 E.01836
G1 X176.033 Y152.919 E.20815
G1 X176.555 Y152.919 E.01836
G1 X180.738 Y157.103 E.20815
G1 X181.26 Y157.103 E.01836
G1 X177.076 Y152.919 E.20815
G1 X177.598 Y152.919 E.01836
G1 X181.782 Y157.103 E.20815
G1 X182.304 Y157.103 E.01836
G1 X178.12 Y152.919 E.20815
G1 X178.642 Y152.919 E.01836
G1 X182.826 Y157.103 E.20815
G1 X183.348 Y157.103 E.01836
G1 X179.164 Y152.919 E.20815
G1 X179.686 Y152.919 E.01836
G1 X183.869 Y157.103 E.20815
G1 X184.391 Y157.103 E.01836
G1 X180.207 Y152.919 E.20815
G1 X180.729 Y152.919 E.01836
G1 X184.913 Y157.103 E.20815
G1 X185.435 Y157.103 E.01836
G1 X181.251 Y152.919 E.20815
G1 X181.773 Y152.919 E.01836
G1 X185.957 Y157.103 E.20815
G1 X186.479 Y157.103 E.01836
G1 X182.295 Y152.919 E.20815
G1 X182.817 Y152.919 E.01836
G1 X191.581 Y161.683 E.43603
G1 X191.581 Y161.161 E.01836
G1 X183.339 Y152.919 E.41006
G1 X183.86 Y152.919 E.01836
G1 X191.581 Y160.64 E.3841
G1 X191.581 Y160.118 E.01836
G1 X184.382 Y152.919 E.35814
G1 X184.904 Y152.919 E.01836
G1 X191.581 Y159.596 E.33217
G1 X191.581 Y159.074 E.01836
G1 X185.426 Y152.919 E.30621
G1 X185.948 Y152.919 E.01836
G1 X191.581 Y158.552 E.28025
G1 X191.581 Y158.03 E.01836
G1 X186.47 Y152.919 E.25429
G1 X186.991 Y152.919 E.01836
G1 X191.581 Y157.509 E.22832
G1 X191.581 Y156.987 E.01836
G1 X187.513 Y152.919 E.20236
G1 X188.035 Y152.919 E.01836
G1 X191.581 Y156.465 E.1764
G1 X191.581 Y155.943 E.01836
G1 X188.557 Y152.919 E.15043
G1 X189.079 Y152.919 E.01836
G1 X191.581 Y155.421 E.12447
G1 X191.581 Y154.899 E.01836
G1 X189.601 Y152.919 E.09851
G1 X190.123 Y152.919 E.01836
G1 X191.581 Y154.377 E.07254
G1 X191.581 Y153.856 E.01836
G1 X190.644 Y152.919 E.04658
G1 X191.166 Y152.919 E.01836
G1 X191.746 Y153.5 E.02887
; WIPE_START
G1 X191.166 Y152.919 E-.3118
G1 X190.644 Y152.919 E-.1983
G1 X191.109 Y153.384 E-.2499
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X184.624 Y157.409 Z3 F60000
G1 X184.498 Y157.487 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X186.092 Y157.487 E.06056
G1 X185.705 Y157.862 E.02048
G1 X185.419 Y158.29 E.01954
G1 X185.065 Y159.145 E.03517
G1 X184.965 Y159.572 E.01668
G1 X185.118 Y160 E.01725
G1 X186.017 Y160.428 E.03783
G1 X186.588 Y160.765 E.02521
G1 X186.588 Y162.513 E.06643
G1 X183.375 Y162.513 E.12209
G1 X183.762 Y162.138 E.02048
G1 X184.047 Y161.71 E.01954
G1 X184.402 Y160.855 E.03517
G1 X184.502 Y160.428 E.01668
G1 X184.349 Y160 E.01725
G1 X183.45 Y159.572 E.03783
G1 X182.725 Y159.145 E.03196
G1 X182.285 Y158.717 E.02333
G1 X181.999 Y158.29 E.01954
G1 X181.666 Y157.487 E.03303
G1 X179.251 Y157.487 E.09174
G1 X178.864 Y157.862 E.02048
G1 X178.578 Y158.29 E.01954
G1 X178.412 Y158.691 E.01651
G1 X178.412 Y160.064 E.05217
G1 X179.176 Y160.428 E.03214
G1 X179.9 Y160.855 E.03196
G1 X180.341 Y161.283 E.02333
G1 X180.627 Y161.71 E.01954
G1 X180.96 Y162.513 E.03303
G1 X179.366 Y162.513 E.06056
; WIPE_START
G1 X180.96 Y162.513 E-.60572
G1 X180.804 Y162.138 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.532 Y167.246 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X168.205 Y152.919 E.71281
G1 X167.683 Y152.919 E.01836
G1 X181.844 Y167.081 E.70456
G1 X181.323 Y167.081 E.01836
G1 X167.161 Y152.919 E.70456
G1 X166.64 Y152.919 E.01836
G1 X180.801 Y167.081 E.70456
G1 X180.279 Y167.081 E.01836
G1 X166.118 Y152.919 E.70456
G1 X165.596 Y152.919 E.01836
G1 X179.757 Y167.081 E.70456
G1 X179.235 Y167.081 E.01836
G1 X165.074 Y152.919 E.70456
G1 X164.552 Y152.919 E.01836
G1 X178.713 Y167.081 E.70456
G1 X178.191 Y167.081 E.01836
G1 X164.03 Y152.919 E.70456
G1 X163.508 Y152.919 E.01836
G1 X177.67 Y167.081 E.70456
G1 X177.148 Y167.081 E.01836
G1 X162.987 Y152.919 E.70456
G1 X162.465 Y152.919 E.01836
G1 X176.626 Y167.081 E.70456
G1 X176.104 Y167.081 E.01836
G1 X167.022 Y157.998 E.45187
G1 X167.022 Y158.52 E.01836
G1 X175.582 Y167.081 E.4259
G1 X175.06 Y167.081 E.01836
G1 X167.022 Y159.042 E.39994
G1 X167.022 Y159.564 E.01836
G1 X174.539 Y167.081 E.37398
G1 X174.017 Y167.081 E.01836
G1 X167.022 Y160.086 E.34802
G1 X167.022 Y160.608 E.01836
G1 X173.495 Y167.081 E.32205
G1 X172.973 Y167.081 E.01836
G1 X167.022 Y161.129 E.29609
G1 X167.022 Y161.651 E.01836
G1 X172.451 Y167.081 E.27013
G1 X171.929 Y167.081 E.01836
G1 X167.022 Y162.173 E.24416
G1 X167.022 Y162.695 E.01836
G1 X171.407 Y167.081 E.2182
G1 X170.886 Y167.081 E.01836
G1 X166.702 Y162.897 E.20815
G1 X166.18 Y162.897 E.01836
G1 X170.364 Y167.081 E.20815
G1 X169.842 Y167.081 E.01836
G1 X165.658 Y162.897 E.20815
G1 X165.136 Y162.897 E.01836
G1 X169.32 Y167.081 E.20815
G1 X168.798 Y167.081 E.01836
G1 X164.614 Y162.897 E.20815
G1 X164.093 Y162.897 E.01836
G1 X168.276 Y167.081 E.20815
G1 X167.755 Y167.081 E.01836
G1 X163.571 Y162.897 E.20815
G1 X163.049 Y162.897 E.01836
G1 X167.233 Y167.081 E.20815
G1 X166.711 Y167.081 E.01836
G1 X162.527 Y162.897 E.20815
G1 X162.005 Y162.897 E.01836
G1 X166.189 Y167.081 E.20815
G1 X165.667 Y167.081 E.01836
G1 X161.483 Y162.897 E.20815
G1 X160.962 Y162.897 E.01836
G1 X165.145 Y167.081 E.20815
G1 X164.624 Y167.081 E.01836
G1 X160.44 Y162.897 E.20815
G1 X159.918 Y162.897 E.01836
G1 X164.102 Y167.081 E.20815
G1 X163.58 Y167.081 E.01836
G1 X159.396 Y162.897 E.20815
G1 X158.874 Y162.897 E.01836
G1 X163.058 Y167.081 E.20815
G1 X162.536 Y167.081 E.01836
G1 X148.375 Y152.919 E.70456
G1 X148.897 Y152.919 E.01836
G1 X157.978 Y162.001 E.45182
G1 X157.978 Y161.479 E.01836
G1 X149.419 Y152.919 E.42586
G1 X149.94 Y152.919 E.01836
G1 X157.978 Y160.957 E.3999
G1 X157.978 Y160.435 E.01836
G1 X150.462 Y152.919 E.37393
G1 X150.984 Y152.919 E.01836
G1 X157.978 Y159.913 E.34797
G1 X157.978 Y159.392 E.01836
G1 X151.506 Y152.919 E.32201
G1 X152.028 Y152.919 E.01836
G1 X157.978 Y158.87 E.29605
G1 X157.978 Y158.348 E.01836
G1 X152.55 Y152.919 E.27008
G1 X153.072 Y152.919 E.01836
G1 X157.978 Y157.826 E.24412
G1 X157.978 Y157.304 E.01836
G1 X153.593 Y152.919 E.21816
G1 X154.115 Y152.919 E.01836
G1 X158.299 Y157.103 E.20815
G1 X158.821 Y157.103 E.01836
G1 X154.637 Y152.919 E.20815
G1 X155.159 Y152.919 E.01836
G1 X159.343 Y157.103 E.20815
G1 X159.865 Y157.103 E.01836
G1 X155.681 Y152.919 E.20815
G1 X156.203 Y152.919 E.01836
G1 X160.386 Y157.103 E.20815
G1 X160.908 Y157.103 E.01836
G1 X156.724 Y152.919 E.20815
M73 P63 R5
G1 X157.246 Y152.919 E.01836
G1 X161.43 Y157.103 E.20815
G1 X161.952 Y157.103 E.01836
G1 X157.768 Y152.919 E.20815
G1 X158.29 Y152.919 E.01836
G1 X162.474 Y157.103 E.20815
G1 X162.996 Y157.103 E.01836
G1 X158.812 Y152.919 E.20815
G1 X159.334 Y152.919 E.01836
G1 X163.517 Y157.103 E.20815
G1 X164.039 Y157.103 E.01836
G1 X159.856 Y152.919 E.20815
G1 X160.377 Y152.919 E.01836
G1 X164.561 Y157.103 E.20815
G1 X165.083 Y157.103 E.01836
G1 X160.899 Y152.919 E.20815
G1 X161.421 Y152.919 E.01836
G1 X165.605 Y157.103 E.20815
G1 X166.127 Y157.103 E.01836
G1 X161.777 Y152.754 E.2164
; WIPE_START
G1 X163.191 Y154.168 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.638 Y158.012 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.638 Y157.487 E.01994
G1 X165.569 Y157.487 E.04062
G1 X165.182 Y157.862 E.02048
G1 X164.896 Y158.29 E.01954
G1 X164.542 Y159.145 E.03517
G1 X164.441 Y159.572 E.01668
G1 X164.595 Y160 E.01725
G1 X165.494 Y160.428 E.03783
G1 X166.218 Y160.855 E.03196
G1 X166.638 Y161.263 E.02223
G1 X166.638 Y162.513 E.04752
G1 X166.295 Y162.513 E.01304
; WIPE_START
G1 X166.638 Y162.513 E-.13046
G1 X166.638 Y161.263 E-.47526
G1 X166.347 Y160.98 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.18 Y167.246 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X147.853 Y152.919 E.71281
G1 X147.331 Y152.919 E.01836
G1 X161.492 Y167.081 E.70456
G1 X160.971 Y167.081 E.01836
G1 X146.809 Y152.919 E.70456
G1 X146.288 Y152.919 E.01836
G1 X160.449 Y167.081 E.70456
G1 X159.927 Y167.081 E.01836
G1 X145.766 Y152.919 E.70456
G1 X145.244 Y152.919 E.01836
G1 X159.405 Y167.081 E.70456
G1 X158.883 Y167.081 E.01836
G1 X144.722 Y152.919 E.70456
G1 X144.2 Y152.919 E.01836
G1 X158.361 Y167.081 E.70456
G1 X157.84 Y167.081 E.01836
G1 X143.678 Y152.919 E.70456
G1 X143.156 Y152.919 E.01836
G1 X157.318 Y167.081 E.70456
G1 X156.796 Y167.081 E.01836
G1 X142.635 Y152.919 E.70456
G1 X142.113 Y152.919 E.01836
G1 X146.297 Y157.103 E.20815
G1 X145.775 Y157.103 E.01836
G1 X141.591 Y152.919 E.20815
G1 X141.069 Y152.919 E.01836
G1 X145.253 Y157.103 E.20815
G1 X144.731 Y157.103 E.01836
G1 X140.547 Y152.919 E.20815
G1 X140.025 Y152.919 E.01836
G1 X144.209 Y157.103 E.20815
G1 X143.687 Y157.103 E.01836
G1 X139.504 Y152.919 E.20815
G1 X138.982 Y152.919 E.01836
G1 X143.165 Y157.103 E.20815
G1 X142.644 Y157.103 E.01836
G1 X138.46 Y152.919 E.20815
G1 X137.938 Y152.919 E.01836
G1 X142.122 Y157.103 E.20815
G1 X141.6 Y157.103 E.01836
G1 X137.416 Y152.919 E.20815
G1 X136.894 Y152.919 E.01836
G1 X141.078 Y157.103 E.20815
G1 X140.556 Y157.103 E.01836
G1 X136.373 Y152.919 E.20815
G1 X135.851 Y152.919 E.01836
G1 X140.034 Y157.103 E.20815
G1 X139.513 Y157.103 E.01836
G1 X135.329 Y152.919 E.20815
G1 X134.807 Y152.919 E.01836
G1 X138.991 Y157.103 E.20815
G1 X138.469 Y157.103 E.01836
G1 X134.285 Y152.919 E.20815
G1 X133.763 Y152.919 E.01836
G1 X138.037 Y157.193 E.21262
G1 X137.928 Y157.302 E.00541
G1 X137.928 Y157.606 E.01071
G1 X133.419 Y153.097 E.22432
G1 X133.419 Y153.619 E.01836
G1 X137.928 Y158.128 E.22432
G1 X137.928 Y158.65 E.01836
G1 X133.419 Y154.141 E.22432
G1 X133.419 Y154.663 E.01836
G1 X137.928 Y159.172 E.22432
G1 X137.928 Y159.694 E.01836
G1 X133.419 Y155.185 E.22432
G1 X133.419 Y155.707 E.01836
G1 X137.928 Y160.215 E.22432
G1 X137.928 Y160.737 E.01836
G1 X133.419 Y156.228 E.22432
G1 X133.419 Y156.75 E.01836
G1 X137.928 Y161.259 E.22432
G1 X137.928 Y161.781 E.01836
G1 X133.419 Y157.272 E.22432
G1 X133.419 Y157.794 E.01836
G1 X137.928 Y162.303 E.22432
G1 X137.928 Y162.698 E.01391
G1 X138.127 Y162.897 E.00988
G1 X138.522 Y162.897 E.01391
G1 X142.706 Y167.081 E.20815
G1 X143.228 Y167.081 E.01836
G1 X139.044 Y162.897 E.20815
G1 X139.566 Y162.897 E.01836
G1 X143.75 Y167.081 E.20815
G1 X144.272 Y167.081 E.01836
G1 X140.088 Y162.897 E.20815
G1 X140.61 Y162.897 E.01836
G1 X144.793 Y167.081 E.20815
G1 X145.315 Y167.081 E.01836
G1 X141.131 Y162.897 E.20815
G1 X141.653 Y162.897 E.01836
G1 X145.837 Y167.081 E.20815
G1 X146.359 Y167.081 E.01836
G1 X142.175 Y162.897 E.20815
G1 X142.697 Y162.897 E.01836
G1 X146.881 Y167.081 E.20815
G1 X147.403 Y167.081 E.01836
G1 X143.219 Y162.897 E.20815
G1 X143.741 Y162.897 E.01836
G1 X147.924 Y167.081 E.20815
G1 X148.446 Y167.081 E.01836
G1 X144.263 Y162.897 E.20815
G1 X144.784 Y162.897 E.01836
G1 X148.968 Y167.081 E.20815
G1 X149.49 Y167.081 E.01836
G1 X145.306 Y162.897 E.20815
G1 X145.828 Y162.897 E.01836
G1 X150.012 Y167.081 E.20815
G1 X150.534 Y167.081 E.01836
G1 X146.35 Y162.897 E.20815
G1 X146.872 Y162.897 E.01836
G1 X151.056 Y167.081 E.20815
G1 X151.577 Y167.081 E.01836
G1 X147.072 Y162.575 E.22417
G1 X147.072 Y162.053 E.01836
G1 X152.099 Y167.081 E.25013
G1 X152.621 Y167.081 E.01836
G1 X147.072 Y161.531 E.27609
G1 X147.072 Y161.009 E.01836
G1 X153.143 Y167.081 E.30206
G1 X153.665 Y167.081 E.01836
G1 X147.072 Y160.488 E.32802
G1 X147.072 Y159.966 E.01836
G1 X154.187 Y167.081 E.35398
G1 X154.708 Y167.081 E.01836
G1 X147.072 Y159.444 E.37995
G1 X147.072 Y158.922 E.01836
G1 X155.23 Y167.081 E.40591
G1 X155.752 Y167.081 E.01836
G1 X147.072 Y158.4 E.43187
G1 X147.072 Y157.878 E.01836
G1 X156.44 Y167.246 E.46608
; WIPE_START
G1 X155.026 Y165.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.362 Y161.883 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.362 Y160.289 E.06056
G1 X158.653 Y160.428 E.01224
G1 X159.377 Y160.855 E.03196
G1 X159.818 Y161.283 E.02333
G1 X160.104 Y161.71 E.01954
G1 X160.437 Y162.513 E.03303
G1 X162.852 Y162.513 E.09174
G1 X163.238 Y162.138 E.02048
G1 X163.524 Y161.71 E.01954
G1 X163.879 Y160.855 E.03517
G1 X163.979 Y160.428 E.01668
G1 X163.826 Y160 E.01725
G1 X162.927 Y159.572 E.03783
G1 X162.202 Y159.145 E.03196
G1 X161.762 Y158.717 E.02333
G1 X161.476 Y158.29 E.01954
G1 X161.143 Y157.487 E.03303
G1 X158.728 Y157.487 E.09174
G1 X158.362 Y157.842 E.01939
G1 X158.362 Y159.436 E.06056
; WIPE_START
G1 X158.362 Y157.842 E-.60572
G1 X158.653 Y157.559 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.038 Y158.077 Z3 F60000
G1 X138.312 Y158.941 Z3
G1 Z2.6
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X138.312 Y160.535 E.06056
G1 X138.854 Y160.855 E.02393
G1 X139.295 Y161.283 E.02333
G1 X139.581 Y161.71 E.01954
G1 X139.914 Y162.513 E.03303
G1 X142.329 Y162.513 E.09174
G1 X142.715 Y162.138 E.02048
G1 X143.001 Y161.71 E.01954
G1 X143.356 Y160.855 E.03517
G1 X143.456 Y160.428 E.01668
G1 X143.303 Y160 E.01725
G1 X142.404 Y159.572 E.03783
G1 X141.679 Y159.145 E.03196
G1 X141.239 Y158.717 E.02333
G1 X140.953 Y158.29 E.01954
G1 X140.62 Y157.487 E.03303
G1 X145.046 Y157.487 E.16817
G1 X144.659 Y157.862 E.02048
G1 X144.373 Y158.29 E.01954
G1 X144.019 Y159.145 E.03517
G1 X143.918 Y159.572 E.01668
G1 X144.072 Y160 E.01725
G1 X144.971 Y160.428 E.03783
G1 X145.695 Y160.855 E.03196
G1 X146.136 Y161.283 E.02333
G1 X146.422 Y161.71 E.01954
G1 X146.688 Y162.353 E.02642
G1 X146.688 Y162.513 E.0061
G1 X145.255 Y162.513 E.05446
; WIPE_START
G1 X146.688 Y162.513 E-.54467
G1 X146.688 Y162.353 E-.06104
G1 X146.533 Y161.978 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X142.35 Y167.246 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X133.419 Y158.316 E.44432
G1 X133.419 Y158.838 E.01836
G1 X141.662 Y167.081 E.41011
G1 X141.14 Y167.081 E.01836
G1 X133.419 Y159.36 E.38415
G1 X133.419 Y159.881 E.01836
G1 X140.619 Y167.081 E.35818
G1 X140.097 Y167.081 E.01836
G1 X133.419 Y160.403 E.33222
G1 X133.419 Y160.925 E.01836
G1 X139.575 Y167.081 E.30626
G1 X139.053 Y167.081 E.01836
G1 X133.419 Y161.447 E.28029
G1 X133.419 Y161.969 E.01836
G1 X138.531 Y167.081 E.25433
G1 X138.009 Y167.081 E.01836
G1 X133.419 Y162.491 E.22837
G1 X133.419 Y163.012 E.01836
G1 X137.488 Y167.081 E.2024
G1 X136.966 Y167.081 E.01836
M73 P64 R5
G1 X133.419 Y163.534 E.17644
G1 X133.419 Y164.056 E.01836
G1 X136.444 Y167.081 E.15048
G1 X135.922 Y167.081 E.01836
G1 X133.419 Y164.578 E.12451
G1 X133.419 Y165.1 E.01836
G1 X135.4 Y167.081 E.09855
G1 X134.878 Y167.081 E.01836
G1 X133.419 Y165.622 E.07259
G1 X133.419 Y166.143 E.01836
G1 X134.357 Y167.081 E.04662
G1 X133.835 Y167.081 E.01836
G1 X133.254 Y166.5 E.02891
; CHANGE_LAYER
; Z_HEIGHT: 2.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12195.123
G1 X133.835 Y167.081 E-.31227
G1 X134.357 Y167.081 E-.1983
G1 X133.892 Y166.616 E-.24943
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 12/47
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3 I-.017 J1.217 P1  F60000
G1 X191.907 Y167.407 Z3
G1 Z2.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X133.093 Y167.407 E2.23446
G1 X133.093 Y152.593 E.56279
G1 X191.907 Y152.593 E2.23446
G1 X191.907 Y167.347 E.56051
; COOLING_NODE: 0
M204 S250
G1 X192.29 Y167.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X191 Y167.246 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X191.581 Y166.666 E.02887
G1 X191.581 Y166.144 E.01836
G1 X190.644 Y167.081 E.04658
G1 X190.123 Y167.081 E.01836
G1 X191.581 Y165.623 E.07254
G1 X191.581 Y165.101 E.01836
G1 X189.601 Y167.081 E.09851
G1 X189.079 Y167.081 E.01836
G1 X191.581 Y164.579 E.12447
G1 X191.581 Y164.057 E.01836
G1 X188.557 Y167.081 E.15043
G1 X188.035 Y167.081 E.01836
G1 X191.581 Y163.535 E.1764
G1 X191.581 Y163.013 E.01836
G1 X187.513 Y167.081 E.20236
G1 X186.991 Y167.081 E.01836
G1 X191.581 Y162.491 E.22832
G1 X191.581 Y161.97 E.01836
G1 X186.47 Y167.081 E.25429
G1 X185.948 Y167.081 E.01836
G1 X191.581 Y161.448 E.28025
G1 X191.581 Y160.926 E.01836
G1 X185.426 Y167.081 E.30621
G1 X184.904 Y167.081 E.01836
G1 X191.581 Y160.404 E.33218
G1 X191.581 Y159.882 E.01836
G1 X184.382 Y167.081 E.35814
G1 X183.86 Y167.081 E.01836
G1 X191.581 Y159.36 E.3841
G1 X191.581 Y158.839 E.01836
G1 X183.339 Y167.081 E.41007
G1 X182.817 Y167.081 E.01836
G1 X191.581 Y158.317 E.43603
G1 X191.581 Y157.795 E.01836
G1 X186.972 Y162.404 E.2293
G1 X186.972 Y161.882 E.01836
G1 X191.581 Y157.273 E.2293
G1 X191.581 Y156.751 E.01836
G1 X186.972 Y161.36 E.2293
G1 X186.972 Y160.838 E.01836
G1 X191.581 Y156.229 E.2293
G1 X191.581 Y155.707 E.01836
G1 X186.972 Y160.316 E.2293
G1 X186.972 Y159.794 E.01836
G1 X191.581 Y155.186 E.2293
G1 X191.581 Y154.664 E.01836
G1 X186.972 Y159.273 E.2293
G1 X186.972 Y158.751 E.01836
G1 X191.581 Y154.142 E.2293
G1 X191.581 Y153.62 E.01836
G1 X186.972 Y158.229 E.2293
G1 X186.972 Y157.707 E.01836
G1 X191.581 Y153.098 E.2293
G1 X191.581 Y152.919 E.00629
G1 X191.238 Y152.919 E.01207
G1 X186.914 Y157.243 E.21513
G1 X186.773 Y157.103 E.00698
G1 X186.532 Y157.103 E.00849
G1 X190.716 Y152.919 E.20815
G1 X190.194 Y152.919 E.01836
G1 X186.01 Y157.103 E.20815
G1 X185.488 Y157.103 E.01836
G1 X189.672 Y152.919 E.20815
G1 X189.15 Y152.919 E.01836
G1 X184.966 Y157.103 E.20815
G1 X184.445 Y157.103 E.01836
G1 X188.628 Y152.919 E.20815
G1 X188.107 Y152.919 E.01836
G1 X183.923 Y157.103 E.20815
G1 X183.401 Y157.103 E.01836
G1 X187.585 Y152.919 E.20815
G1 X187.063 Y152.919 E.01836
G1 X182.879 Y157.103 E.20815
G1 X182.357 Y157.103 E.01836
G1 X186.541 Y152.919 E.20815
G1 X186.019 Y152.919 E.01836
G1 X181.835 Y157.103 E.20815
G1 X181.314 Y157.103 E.01836
G1 X185.497 Y152.919 E.20815
G1 X184.975 Y152.919 E.01836
G1 X180.792 Y157.103 E.20815
G1 X180.27 Y157.103 E.01836
G1 X184.454 Y152.919 E.20815
G1 X183.932 Y152.919 E.01836
G1 X179.748 Y157.103 E.20815
G1 X179.226 Y157.103 E.01836
G1 X183.41 Y152.919 E.20815
G1 X182.888 Y152.919 E.01836
G1 X178.704 Y157.103 E.20815
G1 X178.227 Y157.103 E.0168
G1 X178.028 Y157.302 E.00988
G1 X178.028 Y157.779 E.0168
G1 X168.727 Y167.081 E.46277
G1 X169.249 Y167.081 E.01836
G1 X178.028 Y158.301 E.4368
G1 X178.028 Y158.823 E.01836
G1 X169.771 Y167.081 E.41084
G1 X170.292 Y167.081 E.01836
G1 X178.028 Y159.345 E.38488
G1 X178.028 Y159.867 E.01836
G1 X170.814 Y167.081 E.35891
G1 X171.336 Y167.081 E.01836
G1 X178.028 Y160.388 E.33295
G1 X178.028 Y160.91 E.01836
G1 X171.858 Y167.081 E.30699
G1 X172.38 Y167.081 E.01836
G1 X178.028 Y161.432 E.28102
G1 X178.028 Y161.954 E.01836
G1 X172.902 Y167.081 E.25506
G1 X173.423 Y167.081 E.01836
G1 X178.028 Y162.476 E.2291
G1 X178.028 Y162.698 E.00782
G1 X178.178 Y162.848 E.00745
G1 X173.945 Y167.081 E.21058
G1 X174.467 Y167.081 E.01836
G1 X178.651 Y162.897 E.20815
G1 X179.173 Y162.897 E.01836
G1 X174.989 Y167.081 E.20815
G1 X175.511 Y167.081 E.01836
G1 X179.695 Y162.897 E.20815
G1 X180.216 Y162.897 E.01836
G1 X176.033 Y167.081 E.20815
G1 X176.555 Y167.081 E.01836
G1 X180.738 Y162.897 E.20815
G1 X181.26 Y162.897 E.01836
G1 X177.076 Y167.081 E.20815
G1 X177.598 Y167.081 E.01836
G1 X181.782 Y162.897 E.20815
G1 X182.304 Y162.897 E.01836
G1 X178.12 Y167.081 E.20815
G1 X178.642 Y167.081 E.01836
G1 X182.826 Y162.897 E.20815
G1 X183.348 Y162.897 E.01836
G1 X179.164 Y167.081 E.20815
G1 X179.686 Y167.081 E.01836
G1 X183.869 Y162.897 E.20815
G1 X184.391 Y162.897 E.01836
M73 P64 R4
G1 X180.207 Y167.081 E.20815
G1 X180.729 Y167.081 E.01836
G1 X184.913 Y162.897 E.20815
G1 X185.435 Y162.897 E.01836
G1 X181.251 Y167.081 E.20815
G1 X181.773 Y167.081 E.01836
G1 X185.957 Y162.897 E.20815
G1 X186.479 Y162.897 E.01836
G1 X182.129 Y167.246 E.2164
; WIPE_START
G1 X183.543 Y165.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.104 Y162.513 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X180.698 Y162.513 E.06056
G1 X180.539 Y161.71 E.0311
G1 X180.328 Y161.283 E.01812
G1 X179.993 Y160.855 E.02061
G1 X178.915 Y160 E.05229
G1 X178.579 Y159.572 E.02066
G1 X178.496 Y159.145 E.01655
G1 X178.666 Y158.29 E.03312
G1 X178.878 Y157.862 E.01812
G1 X179.171 Y157.487 E.0181
G1 X181.927 Y157.487 E.10472
G1 X182.087 Y158.29 E.0311
G1 X182.298 Y158.717 E.01812
G1 X182.632 Y159.145 E.02062
G1 X183.71 Y160 E.05229
G1 X184.046 Y160.428 E.02066
G1 X184.129 Y160.855 E.01655
G1 X183.959 Y161.71 E.03312
G1 X183.748 Y162.138 E.01812
G1 X183.455 Y162.513 E.0181
G1 X186.588 Y162.513 E.11905
G1 X186.588 Y160.66 E.07041
G1 X185.756 Y160 E.04034
G1 X185.42 Y159.572 E.02066
G1 X185.338 Y159.145 E.01655
G1 X185.507 Y158.29 E.03312
G1 X185.719 Y157.862 E.01812
G1 X186.012 Y157.487 E.0181
G1 X184.418 Y157.487 E.06056
; WIPE_START
G1 X186.012 Y157.487 E-.60572
G1 X185.762 Y157.807 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.025 Y154.22 Z3.24 F60000
G1 X176.27 Y152.754 Z3.24
G1 Z2.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X167.022 Y162.002 E.46012
G1 X167.022 Y161.48 E.01836
G1 X175.582 Y152.919 E.4259
G1 X175.06 Y152.919 E.01836
M73 P65 R4
G1 X167.022 Y160.958 E.39994
G1 X167.022 Y160.436 E.01836
G1 X174.539 Y152.919 E.37398
G1 X174.017 Y152.919 E.01836
G1 X167.022 Y159.914 E.34801
G1 X167.022 Y159.392 E.01836
G1 X173.495 Y152.919 E.32205
G1 X172.973 Y152.919 E.01836
G1 X167.022 Y158.871 E.29609
G1 X167.022 Y158.349 E.01836
G1 X172.451 Y152.919 E.27012
G1 X171.929 Y152.919 E.01836
G1 X167.022 Y157.827 E.24416
G1 X167.022 Y157.305 E.01836
G1 X171.407 Y152.919 E.2182
G1 X170.886 Y152.919 E.01836
G1 X166.702 Y157.103 E.20815
G1 X166.18 Y157.103 E.01836
G1 X170.364 Y152.919 E.20815
G1 X169.842 Y152.919 E.01836
G1 X165.658 Y157.103 E.20815
G1 X165.136 Y157.103 E.01836
G1 X169.32 Y152.919 E.20815
G1 X168.798 Y152.919 E.01836
G1 X164.614 Y157.103 E.20815
G1 X164.093 Y157.103 E.01836
G1 X168.276 Y152.919 E.20815
G1 X167.755 Y152.919 E.01836
G1 X163.571 Y157.103 E.20815
G1 X163.049 Y157.103 E.01836
G1 X167.233 Y152.919 E.20815
G1 X166.711 Y152.919 E.01836
G1 X162.527 Y157.103 E.20815
G1 X162.005 Y157.103 E.01836
G1 X166.189 Y152.919 E.20815
G1 X165.667 Y152.919 E.01836
G1 X161.483 Y157.103 E.20815
G1 X160.962 Y157.103 E.01836
G1 X165.145 Y152.919 E.20815
G1 X164.623 Y152.919 E.01836
G1 X160.44 Y157.103 E.20815
G1 X159.918 Y157.103 E.01836
G1 X164.102 Y152.919 E.20815
G1 X163.58 Y152.919 E.01836
G1 X159.396 Y157.103 E.20815
G1 X158.874 Y157.103 E.01836
G1 X163.058 Y152.919 E.20815
G1 X162.536 Y152.919 E.01836
G1 X148.375 Y167.081 E.70456
G1 X148.897 Y167.081 E.01836
G1 X157.978 Y157.999 E.45182
G1 X157.978 Y158.521 E.01836
G1 X149.419 Y167.081 E.42586
G1 X149.94 Y167.081 E.01836
G1 X157.978 Y159.043 E.3999
G1 X157.978 Y159.565 E.01836
G1 X150.462 Y167.081 E.37394
G1 X150.984 Y167.081 E.01836
G1 X157.978 Y160.087 E.34797
G1 X157.978 Y160.608 E.01836
G1 X151.506 Y167.081 E.32201
G1 X152.028 Y167.081 E.01836
G1 X157.978 Y161.13 E.29605
G1 X157.978 Y161.652 E.01836
G1 X152.55 Y167.081 E.27008
G1 X153.072 Y167.081 E.01836
G1 X157.978 Y162.174 E.24412
G1 X157.978 Y162.696 E.01836
G1 X153.593 Y167.081 E.21816
G1 X154.115 Y167.081 E.01836
G1 X158.299 Y162.897 E.20815
G1 X158.821 Y162.897 E.01836
G1 X154.637 Y167.081 E.20815
G1 X155.159 Y167.081 E.01836
G1 X159.343 Y162.897 E.20815
G1 X159.865 Y162.897 E.01836
G1 X155.681 Y167.081 E.20815
G1 X156.203 Y167.081 E.01836
G1 X160.386 Y162.897 E.20815
G1 X160.908 Y162.897 E.01836
G1 X156.724 Y167.081 E.20815
G1 X157.246 Y167.081 E.01836
G1 X161.43 Y162.897 E.20815
G1 X161.952 Y162.897 E.01836
G1 X157.768 Y167.081 E.20815
G1 X158.29 Y167.081 E.01836
G1 X162.474 Y162.897 E.20815
G1 X162.996 Y162.897 E.01836
G1 X158.812 Y167.081 E.20815
G1 X159.334 Y167.081 E.01836
G1 X163.517 Y162.897 E.20815
G1 X164.039 Y162.897 E.01836
G1 X159.856 Y167.081 E.20815
G1 X160.377 Y167.081 E.01836
G1 X164.561 Y162.897 E.20815
G1 X165.083 Y162.897 E.01836
G1 X160.899 Y167.081 E.20815
G1 X161.421 Y167.081 E.01836
G1 X165.605 Y162.897 E.20815
G1 X166.127 Y162.897 E.01836
G1 X161.943 Y167.081 E.20815
G1 X162.465 Y167.081 E.01836
G1 X176.626 Y152.919 E.70456
G1 X177.148 Y152.919 E.01836
G1 X162.987 Y167.081 E.70456
G1 X163.508 Y167.081 E.01836
G1 X177.67 Y152.919 E.70456
G1 X178.191 Y152.919 E.01836
G1 X164.03 Y167.081 E.70456
G1 X164.552 Y167.081 E.01836
G1 X178.713 Y152.919 E.70456
G1 X179.235 Y152.919 E.01836
G1 X165.074 Y167.081 E.70456
G1 X165.596 Y167.081 E.01836
G1 X179.757 Y152.919 E.70456
G1 X180.279 Y152.919 E.01836
G1 X166.118 Y167.081 E.70456
G1 X166.639 Y167.081 E.01836
G1 X180.801 Y152.919 E.70456
G1 X181.323 Y152.919 E.01836
G1 X167.161 Y167.081 E.70456
G1 X167.683 Y167.081 E.01836
G1 X181.844 Y152.919 E.70456
G1 X182.366 Y152.919 E.01836
G1 X168.039 Y167.246 E.71281
; WIPE_START
G1 X169.453 Y165.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.892 Y158.642 Z3.24 F60000
G1 X166.638 Y157.931 Z3.24
G1 Z2.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.638 Y157.487 E.01689
G1 X165.489 Y157.487 E.04367
G1 X165.196 Y157.862 E.0181
G1 X164.984 Y158.29 E.01812
G1 X164.814 Y159.145 E.03312
G1 X164.897 Y159.572 E.01655
G1 X165.233 Y160 E.02066
G1 X166.311 Y160.855 E.05229
G1 X166.638 Y161.273 E.02016
G1 X166.638 Y162.513 E.04711
G1 X162.932 Y162.513 E.14082
G1 X163.225 Y162.138 E.0181
G1 X163.436 Y161.71 E.01812
G1 X163.606 Y160.855 E.03312
G1 X163.523 Y160.428 E.01655
G1 X163.187 Y160 E.02066
G1 X162.109 Y159.145 E.05229
G1 X161.775 Y158.717 E.02062
G1 X161.564 Y158.29 E.01812
G1 X161.404 Y157.487 E.0311
G1 X158.648 Y157.487 E.10472
G1 X158.362 Y157.853 E.01765
G1 X158.362 Y159.961 E.0801
G1 X159.47 Y160.855 E.05411
G1 X159.805 Y161.283 E.02061
G1 X160.016 Y161.71 E.01812
G1 X160.175 Y162.513 E.0311
G1 X158.581 Y162.513 E.06056
; WIPE_START
G1 X160.175 Y162.513 E-.60571
G1 X160.096 Y162.115 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X152.752 Y164.192 Z3.24 F60000
G1 X141.947 Y167.246 Z3.24
G1 Z2.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X146.297 Y162.897 E.2164
G1 X145.775 Y162.897 E.01836
G1 X141.591 Y167.081 E.20815
G1 X141.069 Y167.081 E.01836
G1 X145.253 Y162.897 E.20815
G1 X144.731 Y162.897 E.01836
G1 X140.547 Y167.081 E.20815
G1 X140.025 Y167.081 E.01836
G1 X144.209 Y162.897 E.20815
G1 X143.687 Y162.897 E.01836
G1 X139.504 Y167.081 E.20815
G1 X138.982 Y167.081 E.01836
G1 X143.165 Y162.897 E.20815
G1 X142.644 Y162.897 E.01836
G1 X138.46 Y167.081 E.20815
G1 X137.938 Y167.081 E.01836
G1 X142.122 Y162.897 E.20815
G1 X141.6 Y162.897 E.01836
G1 X137.416 Y167.081 E.20815
G1 X136.894 Y167.081 E.01836
G1 X141.078 Y162.897 E.20815
G1 X140.556 Y162.897 E.01836
G1 X136.372 Y167.081 E.20815
G1 X135.851 Y167.081 E.01836
G1 X140.034 Y162.897 E.20815
G1 X139.513 Y162.897 E.01836
G1 X135.329 Y167.081 E.20815
G1 X134.807 Y167.081 E.01836
G1 X138.991 Y162.897 E.20815
G1 X138.469 Y162.897 E.01836
G1 X134.285 Y167.081 E.20815
G1 X133.763 Y167.081 E.01836
G1 X138.037 Y162.807 E.21262
G1 X137.928 Y162.698 E.00541
G1 X137.928 Y162.394 E.01071
G1 X133.419 Y166.903 E.22432
G1 X133.419 Y166.381 E.01836
G1 X137.928 Y161.872 E.22432
G1 X137.928 Y161.35 E.01836
G1 X133.419 Y165.859 E.22432
G1 X133.419 Y165.337 E.01836
G1 X137.928 Y160.828 E.22432
G1 X137.928 Y160.306 E.01836
G1 X133.419 Y164.815 E.22432
G1 X133.419 Y164.293 E.01836
G1 X137.928 Y159.785 E.22432
G1 X137.928 Y159.263 E.01836
G1 X133.419 Y163.772 E.22432
G1 X133.419 Y163.25 E.01836
G1 X137.928 Y158.741 E.22432
G1 X137.928 Y158.219 E.01836
G1 X133.419 Y162.728 E.22432
G1 X133.419 Y162.206 E.01836
G1 X137.928 Y157.697 E.22432
G1 X137.928 Y157.302 E.01391
G1 X138.127 Y157.103 E.00988
G1 X138.522 Y157.103 E.01391
G1 X142.706 Y152.919 E.20815
G1 X143.228 Y152.919 E.01836
G1 X139.044 Y157.103 E.20815
G1 X139.566 Y157.103 E.01836
G1 X143.75 Y152.919 E.20815
G1 X144.272 Y152.919 E.01836
G1 X140.088 Y157.103 E.20815
G1 X140.61 Y157.103 E.01836
G1 X144.793 Y152.919 E.20815
G1 X145.315 Y152.919 E.01836
G1 X141.131 Y157.103 E.20815
G1 X141.653 Y157.103 E.01836
G1 X145.837 Y152.919 E.20815
M73 P66 R4
G1 X146.359 Y152.919 E.01836
G1 X142.175 Y157.103 E.20815
G1 X142.697 Y157.103 E.01836
G1 X146.881 Y152.919 E.20815
G1 X147.403 Y152.919 E.01836
G1 X143.219 Y157.103 E.20815
G1 X143.741 Y157.103 E.01836
G1 X147.924 Y152.919 E.20815
G1 X148.446 Y152.919 E.01836
G1 X144.263 Y157.103 E.20815
G1 X144.784 Y157.103 E.01836
G1 X148.968 Y152.919 E.20815
G1 X149.49 Y152.919 E.01836
G1 X145.306 Y157.103 E.20815
G1 X145.828 Y157.103 E.01836
G1 X150.012 Y152.919 E.20815
G1 X150.534 Y152.919 E.01836
G1 X146.35 Y157.103 E.20815
G1 X146.872 Y157.103 E.01836
G1 X151.056 Y152.919 E.20815
G1 X151.577 Y152.919 E.01836
G1 X147.072 Y157.425 E.22417
G1 X147.072 Y157.947 E.01836
G1 X152.099 Y152.919 E.25013
G1 X152.621 Y152.919 E.01836
G1 X147.072 Y158.469 E.27609
G1 X147.072 Y158.991 E.01836
G1 X153.143 Y152.919 E.30205
G1 X153.665 Y152.919 E.01836
G1 X147.072 Y159.512 E.32802
G1 X147.072 Y160.034 E.01836
G1 X154.187 Y152.919 E.35398
G1 X154.708 Y152.919 E.01836
G1 X147.072 Y160.556 E.37994
G1 X147.072 Y161.078 E.01836
G1 X155.23 Y152.919 E.40591
G1 X155.752 Y152.919 E.01836
G1 X147.072 Y161.6 E.43187
G1 X147.072 Y162.122 E.01836
G1 X156.274 Y152.919 E.45783
G1 X156.796 Y152.919 E.01836
G1 X142.635 Y167.081 E.70456
G1 X143.156 Y167.081 E.01836
G1 X157.318 Y152.919 E.70456
G1 X157.84 Y152.919 E.01836
G1 X143.678 Y167.081 E.70456
G1 X144.2 Y167.081 E.01836
G1 X158.361 Y152.919 E.70456
G1 X158.883 Y152.919 E.01836
G1 X144.722 Y167.081 E.70456
G1 X145.244 Y167.081 E.01836
G1 X159.405 Y152.919 E.70456
G1 X159.927 Y152.919 E.01836
G1 X145.766 Y167.081 E.70456
G1 X146.288 Y167.081 E.01836
G1 X160.449 Y152.919 E.70456
G1 X160.971 Y152.919 E.01836
G1 X146.809 Y167.081 E.70456
G1 X147.331 Y167.081 E.01836
G1 X161.492 Y152.919 E.70456
G1 X162.014 Y152.919 E.01836
G1 X147.687 Y167.246 E.71281
; WIPE_START
G1 X149.101 Y165.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.688 Y161.114 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.688 Y162.513 E.05315
G1 X146.493 Y162.513 E.00741
G1 X146.334 Y161.71 E.0311
G1 X146.123 Y161.283 E.01812
G1 X145.788 Y160.855 E.02061
G1 X144.71 Y160 E.05229
G1 X144.374 Y159.572 E.02066
G1 X144.291 Y159.145 E.01655
G1 X144.461 Y158.29 E.03312
G1 X144.673 Y157.862 E.01812
G1 X144.966 Y157.487 E.0181
G1 X140.881 Y157.487 E.15518
G1 X141.041 Y158.29 E.0311
G1 X141.252 Y158.717 E.01812
G1 X141.586 Y159.145 E.02062
G1 X142.664 Y160 E.05229
G1 X143 Y160.428 E.02066
G1 X143.083 Y160.855 E.01655
G1 X142.913 Y161.71 E.03312
G1 X142.702 Y162.138 E.01812
G1 X142.409 Y162.513 E.0181
G1 X139.652 Y162.513 E.10473
G1 X139.493 Y161.71 E.0311
G1 X139.281 Y161.283 E.01812
G1 X138.947 Y160.855 E.02061
G1 X138.312 Y160.351 E.03082
G1 X138.312 Y158.757 E.06056
; WIPE_START
G1 X138.312 Y160.351 E-.60571
G1 X138.63 Y160.603 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X133.254 Y161.85 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.420504
G1 F12195.123
M204 S8000
G1 X142.184 Y152.919 E.44432
G1 X141.662 Y152.919 E.01836
G1 X133.419 Y161.162 E.41011
G1 X133.419 Y160.64 E.01836
G1 X141.14 Y152.919 E.38414
G1 X140.619 Y152.919 E.01836
G1 X133.419 Y160.119 E.35818
G1 X133.419 Y159.597 E.01836
G1 X140.097 Y152.919 E.33222
G1 X139.575 Y152.919 E.01836
G1 X133.419 Y159.075 E.30625
G1 X133.419 Y158.553 E.01836
G1 X139.053 Y152.919 E.28029
G1 X138.531 Y152.919 E.01836
G1 X133.419 Y158.031 E.25433
G1 X133.419 Y157.509 E.01836
G1 X138.009 Y152.919 E.22836
G1 X137.488 Y152.919 E.01836
G1 X133.419 Y156.988 E.2024
G1 X133.419 Y156.466 E.01836
G1 X136.966 Y152.919 E.17644
G1 X136.444 Y152.919 E.01836
G1 X133.419 Y155.944 E.15048
G1 X133.419 Y155.422 E.01836
G1 X135.922 Y152.919 E.12451
G1 X135.4 Y152.919 E.01836
G1 X133.419 Y154.9 E.09855
G1 X133.419 Y154.378 E.01836
G1 X134.878 Y152.919 E.07259
G1 X134.356 Y152.919 E.01836
G1 X133.419 Y153.856 E.04662
G1 X133.419 Y153.335 E.01836
G1 X134 Y152.754 E.02891
; CHANGE_LAYER
; Z_HEIGHT: 3.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12195.123
G1 X133.419 Y153.335 E-.31226
G1 X133.419 Y153.856 E-.1983
G1 X133.884 Y153.392 E-.24944
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 13/47
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.24 I-.336 J1.17 P1  F60000
G1 X167.057 Y162.932 Z3.24
G1 Z3.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X157.943 Y162.932 E.34624
G1 X157.943 Y157.068 E.22276
G1 X167.057 Y157.068 E.34624
G1 X167.057 Y162.872 E.22048
; COOLING_NODE: 0
; WIPE_START
G1 X165.057 Y162.885 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X172.689 Y162.901 Z3.48 F60000
G1 X187.007 Y162.932 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X177.993 Y162.932 E.34244
G1 X177.993 Y157.068 E.22276
G1 X187.007 Y157.068 E.34244
G1 X187.007 Y162.872 E.22048
; COOLING_NODE: 0
; WIPE_START
G1 X185.007 Y162.885 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.374 Y162.894 Z3.48 F60000
G1 X147.107 Y162.932 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X137.893 Y162.932 E.35004
G1 X137.893 Y157.068 E.22276
G1 X147.107 Y157.068 E.35004
G1 X147.107 Y162.872 E.22048
; COOLING_NODE: 0
; WIPE_START
G1 X145.107 Y162.885 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X152.698 Y163.674 Z3.48 F60000
G1 X192.29 Y167.79 Z3.48
G1 Z3.08
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X132.71 Y167.79 E2.09319
G1 X132.71 Y152.21 E.54736
G1 X192.29 Y152.21 E2.09319
G1 X192.29 Y167.73 E.54526
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

; WIPE_START
M204 S8000
G1 X190.29 Y167.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X187.549 Y160.609 Z3.48 F60000
G1 X186.666 Y158.312 Z3.48
G1 Z3.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X186.666 Y157.409 E.03428
G1 X185.974 Y157.409 E.02628
G1 X185.701 Y157.862 E.02009
G1 X185.561 Y158.29 E.01709
G1 X185.547 Y159.145 E.03249
G1 X185.721 Y159.572 E.01755
G1 X186.085 Y160 E.02132
G1 X186.666 Y160.582 E.03123
G1 X186.666 Y162.591 E.07632
G1 X183.493 Y162.591 E.12055
G1 X183.765 Y162.138 E.02008
G1 X183.905 Y161.71 E.01709
G1 X183.92 Y160.855 E.03249
G1 X183.745 Y160.428 E.01755
G1 X183.382 Y160 E.02132
G1 X182.528 Y159.145 E.0459
G1 X182.281 Y158.717 E.01877
G1 X182.141 Y158.29 E.01709
G1 X182.137 Y157.409 E.03345
G1 X179.133 Y157.409 E.11412
G1 X178.86 Y157.862 E.02009
G1 X178.72 Y158.29 E.01709
G1 X178.706 Y159.145 E.03249
G1 X178.88 Y159.572 E.01755
G1 X179.244 Y160 E.02132
G1 X180.097 Y160.855 E.0459
G1 X180.345 Y161.283 E.01877
G1 X180.485 Y161.71 E.01709
G1 X180.499 Y162.565 E.03249
G1 X180.489 Y162.591 E.00104
G1 X178.895 Y162.591 E.06056
; WIPE_START
G1 X180.489 Y162.591 E-.60572
G1 X180.499 Y162.565 E-.01039
G1 X180.493 Y162.187 E-.1439
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.727 Y163.131 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.391504
G1 F13235.295
M204 S8000
G1 X177.738 Y163.187 E.00184
G1 X177.794 Y163.198 E.00184
G1 X187.206 Y163.198 E.3051
G1 X187.261 Y163.131 E.0028
G1 X187.261 Y156.869 E.20299
G1 X187.243 Y156.807 E.00209
M73 P67 R4
G1 X177.738 Y156.813 E.3081
G1 X177.727 Y163.071 E.20284
; WIPE_START
G1 X177.731 Y161.071 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.425 Y158.861 Z3.48 F60000
G1 X166.716 Y157.739 Z3.48
G1 Z3.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.716 Y157.409 E.01251
G1 X165.451 Y157.409 E.04805
G1 X165.178 Y157.862 E.02009
G1 X165.038 Y158.29 E.01709
G1 X165.024 Y159.145 E.03249
G1 X165.198 Y159.572 E.01755
G1 X165.562 Y160 E.02132
G1 X166.415 Y160.855 E.0459
G1 X166.663 Y161.283 E.01877
G1 X166.716 Y161.444 E.00646
G1 X166.716 Y162.591 E.04356
G1 X162.97 Y162.591 E.14232
G1 X163.242 Y162.138 E.02008
G1 X163.382 Y161.71 E.01709
G1 X163.397 Y160.855 E.03249
G1 X163.222 Y160.428 E.01755
G1 X162.859 Y160 E.02132
G1 X162.005 Y159.145 E.0459
G1 X161.758 Y158.717 E.01877
G1 X161.618 Y158.29 E.01709
G1 X161.614 Y157.409 E.03345
G1 X158.61 Y157.409 E.11412
G1 X158.337 Y157.862 E.02009
G1 X158.284 Y158.024 E.00647
G1 X158.284 Y159.394 E.05203
G1 X158.357 Y159.572 E.00734
G1 X158.721 Y160 E.02132
G1 X159.574 Y160.855 E.0459
G1 X159.822 Y161.283 E.01877
G1 X159.962 Y161.71 E.01709
G1 X159.976 Y162.565 E.03249
G1 X159.966 Y162.591 E.00104
G1 X158.372 Y162.591 E.06056
; WIPE_START
G1 X159.966 Y162.591 E-.60571
G1 X159.976 Y162.565 E-.01039
G1 X159.97 Y162.187 E-.1439
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X157.757 Y156.802 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.391504
G1 F13235.295
M204 S8000
G1 X167.256 Y156.802 E.30793
G1 X167.293 Y156.807 E.00122
G1 X167.311 Y156.869 E.00209
G1 X167.311 Y163.131 E.20299
G1 X167.268 Y163.198 E.00257
G1 X157.817 Y163.198 E.30636
; WIPE_START
G1 X159.817 Y163.198 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X152.25 Y162.201 Z3.48 F60000
G1 X146.766 Y161.478 Z3.48
G1 Z3.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.766 Y162.591 E.04226
G1 X146.284 Y162.591 E.0183
G1 X146.28 Y161.71 E.03345
G1 X146.14 Y161.283 E.01709
G1 X145.892 Y160.855 E.01877
G1 X145.039 Y160 E.0459
G1 X144.675 Y159.572 E.02132
G1 X144.501 Y159.145 E.01755
G1 X144.515 Y158.29 E.03249
G1 X144.655 Y157.862 E.01709
G1 X144.928 Y157.409 E.02009
G1 X141.091 Y157.409 E.14579
G1 X141.095 Y158.29 E.03345
G1 X141.235 Y158.717 E.01709
G1 X141.482 Y159.145 E.01877
G1 X142.336 Y160 E.0459
G1 X142.699 Y160.428 E.02132
G1 X142.874 Y160.855 E.01755
G1 X142.859 Y161.71 E.03249
G1 X142.719 Y162.138 E.01709
G1 X142.447 Y162.591 E.02008
G1 X139.443 Y162.591 E.11412
G1 X139.439 Y161.71 E.03345
G1 X139.299 Y161.283 E.01709
G1 X139.051 Y160.855 E.01877
G1 X138.308 Y160.11 E.03999
G1 X138.308 Y158.516 E.06056
; WIPE_START
G1 X138.308 Y160.11 E-.60571
G1 X138.595 Y160.397 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X137.807 Y156.802 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.391504
G1 F13235.295
M204 S8000
G1 X147.306 Y156.802 E.30793
G1 X147.343 Y156.807 E.00121
G1 X147.361 Y156.869 E.00209
G1 X147.361 Y163.131 E.20299
G1 X147.318 Y163.198 E.00257
G1 X137.857 Y163.198 E.30666
; WIPE_START
G1 X139.857 Y163.198 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.327 Y161.631 Z3.48 F60000
G1 X191.263 Y152.414 Z3.48
G1 Z3.08
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X192.086 Y153.237 E.04421
G1 X192.229 Y153.38
G1 X192.229 Y153.944
G1 X192.086 Y153.8
G1 X190.7 Y152.414 E.07449
G1 X190.556 Y152.271
G1 X189.993 Y152.271
G1 X190.136 Y152.414
G1 X192.086 Y154.364 E.10477
G1 X192.229 Y154.507
G1 X192.229 Y155.071
G1 X192.086 Y154.928
G1 X189.572 Y152.414 E.13505
G1 X189.429 Y152.271
G1 X188.866 Y152.271
G1 X189.009 Y152.414
G1 X192.086 Y155.491 E.16532
G1 X192.229 Y155.634
G1 X192.229 Y156.198
G1 X192.086 Y156.055
G1 X188.445 Y152.414 E.1956
G1 X188.302 Y152.271
G1 X187.739 Y152.271
G1 X187.882 Y152.414
G1 X192.086 Y156.618 E.22588
G1 X192.229 Y156.761
G1 X192.229 Y157.325
G1 X192.086 Y157.182
G1 X187.318 Y152.414 E.25616
G1 X187.175 Y152.271
G1 X186.611 Y152.271
G1 X186.755 Y152.414
G1 X192.086 Y157.745 E.28644
G1 X192.229 Y157.889
G1 X192.229 Y158.452
G1 X192.086 Y158.309
G1 X186.191 Y152.414 E.31672
G1 X186.048 Y152.271
G1 X185.484 Y152.271
G1 X185.628 Y152.414
G1 X192.086 Y158.872 E.347
G1 X192.229 Y159.016
G1 X192.229 Y159.579
G1 X192.086 Y159.436
G1 X185.064 Y152.414 E.37728
G1 X184.921 Y152.271
G1 X184.357 Y152.271
G1 X184.5 Y152.414
G1 X192.086 Y160 E.40756
G1 X192.229 Y160.143
G1 X192.229 Y160.706
G1 X192.086 Y160.563
G1 X183.937 Y152.414 E.43784
G1 X183.794 Y152.271
G1 X183.23 Y152.271
G1 X183.373 Y152.414
G1 X192.086 Y161.127 E.46812
G1 X192.229 Y161.27
G1 X192.229 Y161.833
G1 X192.086 Y161.69
G1 X187.335 Y156.939 E.25526
G1 X187.192 Y156.796
G1 X187.192 Y157.36
G1 X187.335 Y157.503
G1 X192.086 Y162.254 E.25526
G1 X192.229 Y162.397
G1 X192.229 Y162.96
G1 X192.086 Y162.817
G1 X187.335 Y158.067 E.25526
G1 X187.192 Y157.923
G1 X187.192 Y158.487
G1 X187.335 Y158.63
G1 X192.086 Y163.381 E.25526
G1 X192.229 Y163.524
G1 X192.229 Y164.088
G1 X192.086 Y163.944
G1 X187.335 Y159.194 E.25526
G1 X187.192 Y159.05
G1 X187.192 Y159.614
G1 X187.335 Y159.757
G1 X192.086 Y164.508 E.25526
G1 X192.229 Y164.651
G1 X192.229 Y165.215
G1 X192.086 Y165.071
G1 X187.335 Y160.321 E.25526
G1 X187.192 Y160.178
G1 X187.192 Y160.741
G1 X187.335 Y160.884
G1 X192.086 Y165.635 E.25526
G1 X192.229 Y165.778
G1 X192.229 Y166.342
G1 X192.086 Y166.199
G1 X187.335 Y161.448 E.25526
G1 X187.192 Y161.305
G1 X187.192 Y161.868
G1 X187.335 Y162.011
G1 X192.086 Y166.762 E.25526
G1 X192.229 Y166.905
G1 X192.229 Y167.469
G1 X192.086 Y167.326
G1 X187.335 Y162.575 E.25526
G1 X187.192 Y162.432
G1 X187.192 Y162.995
G1 X187.335 Y163.138
G1 X191.782 Y167.586 E.23895
G1 X191.926 Y167.729
G1 X191.362 Y167.729
G1 X191.219 Y167.586
G1 X186.918 Y163.285 E.23109
G1 X186.775 Y163.142
G1 X186.211 Y163.142
G1 X186.354 Y163.285
G1 X190.655 Y167.586 E.23109
G1 X190.799 Y167.729
G1 X190.235 Y167.729
G1 X190.092 Y167.586
G1 X185.791 Y163.285 E.23109
G1 X185.648 Y163.142
G1 X185.084 Y163.142
G1 X185.227 Y163.285
G1 X189.528 Y167.586 E.23109
G1 X189.671 Y167.729
G1 X189.108 Y167.729
G1 X188.965 Y167.586
G1 X184.664 Y163.285 E.23109
G1 X184.521 Y163.142
G1 X183.957 Y163.142
G1 X184.1 Y163.285
G1 X188.401 Y167.586 E.23109
G1 X188.544 Y167.729
G1 X187.981 Y167.729
G1 X187.838 Y167.586
G1 X183.537 Y163.285 E.23109
G1 X183.393 Y163.142
G1 X182.83 Y163.142
G1 X182.973 Y163.285
G1 X187.274 Y167.586 E.23109
G1 X187.417 Y167.729
G1 X186.854 Y167.729
G1 X186.71 Y167.586
G1 X182.409 Y163.285 E.23109
G1 X182.266 Y163.142
G1 X181.703 Y163.142
G1 X181.846 Y163.285
G1 X186.147 Y167.586 E.23109
G1 X186.29 Y167.729
G1 X185.727 Y167.729
G1 X185.583 Y167.586
G1 X181.282 Y163.285 E.23109
G1 X181.139 Y163.142
G1 X180.576 Y163.142
G1 X180.719 Y163.285
G1 X185.02 Y167.586 E.23109
G1 X185.163 Y167.729
G1 X184.599 Y167.729
G1 X184.456 Y167.586
G1 X180.155 Y163.285 E.23109
G1 X180.012 Y163.142
G1 X179.449 Y163.142
G1 X179.592 Y163.285
G1 X183.893 Y167.586 E.23109
G1 X184.036 Y167.729
G1 X183.472 Y167.729
G1 X183.329 Y167.586
G1 X179.028 Y163.285 E.23109
G1 X178.885 Y163.142
G1 X178.321 Y163.142
G1 X178.465 Y163.285
G1 X182.766 Y167.586 E.23109
G1 X182.909 Y167.729
G1 X182.345 Y167.729
G1 X182.202 Y167.586
G1 X177.901 Y163.285 E.23109
; WIPE_START
M204 S8000
G1 X179.315 Y164.699 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X184.647 Y159.238 Z3.48 F60000
G1 X187.111 Y156.715 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S2000
G1 X182.81 Y152.414 E.23109
G1 X182.667 Y152.271
G1 X182.103 Y152.271
G1 X182.246 Y152.414
G1 X186.547 Y156.715 E.23109
G1 X186.69 Y156.858
G1 X186.127 Y156.858
G1 X185.984 Y156.715
G1 X181.683 Y152.414 E.23109
G1 X181.54 Y152.271
G1 X180.976 Y152.271
G1 X181.119 Y152.414
G1 X185.42 Y156.715 E.23109
G1 X185.563 Y156.858
G1 X185 Y156.858
G1 X184.857 Y156.715
G1 X180.556 Y152.414 E.23109
G1 X180.412 Y152.271
G1 X179.849 Y152.271
G1 X179.992 Y152.414
G1 X184.293 Y156.715 E.23109
G1 X184.436 Y156.858
G1 X183.873 Y156.858
G1 X183.73 Y156.715
G1 X179.429 Y152.414 E.23109
G1 X179.285 Y152.271
G1 X178.722 Y152.271
G1 X178.865 Y152.414
G1 X183.166 Y156.715 E.23109
G1 X183.309 Y156.858
G1 X182.746 Y156.858
G1 X182.602 Y156.715
G1 X178.301 Y152.414 E.23109
G1 X178.158 Y152.271
G1 X177.595 Y152.271
G1 X177.738 Y152.414
G1 X182.039 Y156.715 E.23109
G1 X182.182 Y156.858
G1 X181.618 Y156.858
G1 X181.475 Y156.715
G1 X177.174 Y152.414 E.23109
G1 X177.031 Y152.271
G1 X176.468 Y152.271
M73 P68 R4
G1 X176.611 Y152.414
G1 X180.912 Y156.715 E.23109
G1 X181.055 Y156.858
G1 X180.491 Y156.858
G1 X180.348 Y156.715
G1 X176.047 Y152.414 E.23109
G1 X175.904 Y152.271
G1 X175.34 Y152.271
G1 X175.484 Y152.414
G1 X179.785 Y156.715 E.23109
G1 X179.928 Y156.858
G1 X179.364 Y156.858
G1 X179.221 Y156.715
G1 X174.92 Y152.414 E.23109
G1 X174.777 Y152.271
G1 X174.213 Y152.271
G1 X174.357 Y152.414
G1 X178.658 Y156.715 E.23109
G1 X178.801 Y156.858
G1 X178.237 Y156.858
G1 X178.094 Y156.715
G1 X173.793 Y152.414 E.23109
G1 X173.65 Y152.271
G1 X173.086 Y152.271
G1 X173.229 Y152.414
G1 X177.64 Y156.825 E.23699
G1 X177.783 Y156.968
G1 X177.783 Y157.532
G1 X177.64 Y157.388
G1 X172.666 Y152.414 E.26727
G1 X172.523 Y152.271
G1 X171.959 Y152.271
G1 X172.102 Y152.414
G1 X177.64 Y157.952 E.29755
G1 X177.783 Y158.095
G1 X177.783 Y158.659
G1 X177.64 Y158.516
G1 X171.539 Y152.414 E.32783
G1 X171.396 Y152.271
G1 X170.832 Y152.271
G1 X170.975 Y152.414
G1 X177.64 Y159.079 E.3581
G1 X177.783 Y159.222
G1 X177.783 Y159.786
G1 X177.64 Y159.643
G1 X170.412 Y152.414 E.38838
G1 X170.269 Y152.271
G1 X169.705 Y152.271
G1 X169.848 Y152.414
G1 X177.64 Y160.206 E.41866
G1 X177.783 Y160.349
G1 X177.783 Y160.913
G1 X177.64 Y160.77
G1 X169.285 Y152.414 E.44894
G1 X169.141 Y152.271
G1 X168.578 Y152.271
G1 X168.721 Y152.414
G1 X177.64 Y161.333 E.47922
G1 X177.783 Y161.476
G1 X177.783 Y162.04
G1 X177.64 Y161.897
G1 X168.158 Y152.414 E.5095
G1 X168.014 Y152.271
G1 X167.451 Y152.271
G1 X167.594 Y152.414
G1 X177.64 Y162.46 E.53978
G1 X177.783 Y162.604
G1 X177.783 Y163.167
G1 X177.64 Y163.024
G1 X167.03 Y152.414 E.57006
G1 X166.887 Y152.271
G1 X166.324 Y152.271
G1 X166.467 Y152.414
G1 X181.639 Y167.586 E.81517
G1 X181.782 Y167.729
G1 X181.218 Y167.729
G1 X181.075 Y167.586
G1 X165.903 Y152.414 E.81517
G1 X165.76 Y152.271
G1 X165.197 Y152.271
G1 X165.34 Y152.414
G1 X180.511 Y167.586 E.81517
G1 X180.655 Y167.729
G1 X180.091 Y167.729
G1 X179.948 Y167.586
G1 X164.776 Y152.414 E.81517
G1 X164.633 Y152.271
G1 X164.069 Y152.271
G1 X164.213 Y152.414
G1 X179.384 Y167.586 E.81517
G1 X179.528 Y167.729
G1 X178.964 Y167.729
G1 X178.821 Y167.586
G1 X163.649 Y152.414 E.81517
G1 X163.506 Y152.271
G1 X162.942 Y152.271
G1 X163.086 Y152.414
G1 X178.257 Y167.586 E.81517
G1 X178.4 Y167.729
G1 X177.837 Y167.729
G1 X177.694 Y167.586
G1 X167.385 Y157.277 E.55388
G1 X167.242 Y157.134
G1 X167.242 Y157.698
G1 X167.385 Y157.841
G1 X177.13 Y167.586 E.5236
G1 X177.273 Y167.729
G1 X176.71 Y167.729
G1 X176.567 Y167.586
G1 X167.385 Y158.404 E.49332
G1 X167.242 Y158.261
G1 X167.242 Y158.825
G1 X167.385 Y158.968
G1 X176.003 Y167.586 E.46304
G1 X176.146 Y167.729
G1 X175.583 Y167.729
G1 X175.439 Y167.586
G1 X167.385 Y159.531 E.43276
G1 X167.242 Y159.388
G1 X167.242 Y159.952
G1 X167.385 Y160.095
G1 X174.876 Y167.586 E.40248
G1 X175.019 Y167.729
G1 X174.456 Y167.729
G1 X174.312 Y167.586
G1 X167.385 Y160.659 E.3722
G1 X167.242 Y160.515
G1 X167.242 Y161.079
G1 X167.385 Y161.222
G1 X173.749 Y167.586 E.34192
G1 X173.892 Y167.729
G1 X173.328 Y167.729
G1 X173.185 Y167.586
G1 X167.385 Y161.786 E.31164
G1 X167.242 Y161.642
G1 X167.242 Y162.206
G1 X167.385 Y162.349
G1 X172.622 Y167.586 E.28136
G1 X172.765 Y167.729
G1 X172.201 Y167.729
G1 X172.058 Y167.586
G1 X167.385 Y162.913 E.25108
G1 X167.242 Y162.77
G1 X167.05 Y163.142
G1 X167.194 Y163.285
G1 X171.495 Y167.586 E.23109
G1 X171.638 Y167.729
G1 X171.074 Y167.729
G1 X170.931 Y167.586
G1 X166.63 Y163.285 E.23109
G1 X166.487 Y163.142
G1 X165.923 Y163.142
G1 X166.067 Y163.285
G1 X170.368 Y167.586 E.23109
G1 X170.511 Y167.729
G1 X169.947 Y167.729
G1 X169.804 Y167.586
G1 X165.503 Y163.285 E.23109
G1 X165.36 Y163.142
G1 X164.796 Y163.142
G1 X164.939 Y163.285
G1 X169.24 Y167.586 E.23109
G1 X169.384 Y167.729
G1 X168.82 Y167.729
G1 X168.677 Y167.586
G1 X164.376 Y163.285 E.23109
G1 X164.233 Y163.142
G1 X163.669 Y163.142
G1 X163.812 Y163.285
G1 X168.113 Y167.586 E.23109
G1 X168.257 Y167.729
G1 X167.693 Y167.729
G1 X167.55 Y167.586
G1 X163.249 Y163.285 E.23109
G1 X163.106 Y163.142
G1 X162.542 Y163.142
G1 X162.685 Y163.285
G1 X166.986 Y167.586 E.23109
G1 X167.129 Y167.729
G1 X166.566 Y167.729
G1 X166.423 Y167.586
G1 X162.122 Y163.285 E.23109
G1 X161.979 Y163.142
G1 X161.415 Y163.142
G1 X161.558 Y163.285
G1 X165.859 Y167.586 E.23109
G1 X166.002 Y167.729
G1 X165.439 Y167.729
G1 X165.296 Y167.586
G1 X160.995 Y163.285 E.23109
G1 X160.851 Y163.142
G1 X160.288 Y163.142
G1 X160.431 Y163.285
G1 X164.732 Y167.586 E.23109
G1 X164.875 Y167.729
G1 X164.312 Y167.729
G1 X164.168 Y167.586
G1 X159.867 Y163.285 E.23109
G1 X159.724 Y163.142
G1 X159.161 Y163.142
G1 X159.304 Y163.285
G1 X163.605 Y167.586 E.23109
G1 X163.748 Y167.729
G1 X163.185 Y167.729
G1 X163.041 Y167.586
G1 X158.74 Y163.285 E.23109
G1 X158.597 Y163.142
G1 X158.034 Y163.142
G1 X158.177 Y163.285
G1 X162.478 Y167.586 E.23109
; WIPE_START
M204 S8000
G1 X161.064 Y166.172 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.034 Y159.653 Z3.48 F60000
G1 X166.823 Y156.715 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S2000
G1 X162.522 Y152.414 E.23109
G1 X162.379 Y152.271
G1 X161.815 Y152.271
G1 X161.958 Y152.414
G1 X166.259 Y156.715 E.23109
G1 X166.403 Y156.858
G1 X165.839 Y156.858
G1 X165.696 Y156.715
G1 X161.395 Y152.414 E.23109
G1 X161.252 Y152.271
G1 X160.688 Y152.271
G1 X160.831 Y152.414
G1 X165.132 Y156.715 E.23109
G1 X165.276 Y156.858
G1 X164.712 Y156.858
G1 X164.569 Y156.715
G1 X160.268 Y152.414 E.23109
G1 X160.125 Y152.271
G1 X159.561 Y152.271
G1 X159.704 Y152.414
G1 X164.005 Y156.715 E.23109
G1 X164.148 Y156.858
G1 X163.585 Y156.858
G1 X163.442 Y156.715
G1 X159.141 Y152.414 E.23109
G1 X158.998 Y152.271
G1 X158.434 Y152.271
G1 X158.577 Y152.414
G1 X162.878 Y156.715 E.23109
G1 X163.021 Y156.858
G1 X162.458 Y156.858
G1 X162.315 Y156.715
G1 X158.014 Y152.414 E.23109
G1 X157.87 Y152.271
G1 X157.307 Y152.271
G1 X157.45 Y152.414
G1 X161.751 Y156.715 E.23109
G1 X161.894 Y156.858
G1 X161.331 Y156.858
G1 X161.188 Y156.715
G1 X156.887 Y152.414 E.23109
G1 X156.743 Y152.271
G1 X156.18 Y152.271
G1 X156.323 Y152.414
G1 X160.624 Y156.715 E.23109
G1 X160.767 Y156.858
G1 X160.204 Y156.858
G1 X160.06 Y156.715
G1 X155.759 Y152.414 E.23109
G1 X155.616 Y152.271
G1 X155.053 Y152.271
G1 X155.196 Y152.414
M73 P69 R4
G1 X159.497 Y156.715 E.23109
G1 X159.64 Y156.858
G1 X159.077 Y156.858
G1 X158.933 Y156.715
G1 X154.632 Y152.414 E.23109
G1 X154.489 Y152.271
G1 X153.926 Y152.271
G1 X154.069 Y152.414
G1 X158.37 Y156.715 E.23109
G1 X158.513 Y156.858
G1 X157.949 Y156.858
G1 X157.806 Y156.715
G1 X153.505 Y152.414 E.23109
G1 X153.362 Y152.271
G1 X152.798 Y152.271
G1 X152.942 Y152.414
G1 X157.668 Y157.14 E.25392
G1 X157.811 Y157.283
G1 X157.811 Y157.847
G1 X157.668 Y157.704
G1 X152.378 Y152.414 E.2842
G1 X152.235 Y152.271
G1 X151.671 Y152.271
G1 X151.815 Y152.414
G1 X157.668 Y158.267 E.31448
G1 X157.811 Y158.41
G1 X157.811 Y158.974
G1 X157.668 Y158.831
G1 X151.251 Y152.414 E.34476
G1 X151.108 Y152.271
G1 X150.544 Y152.271
G1 X150.687 Y152.414
G1 X157.668 Y159.394 E.37504
G1 X157.811 Y159.537
G1 X157.811 Y160.101
G1 X157.668 Y159.958
G1 X150.124 Y152.414 E.40532
G1 X149.981 Y152.271
G1 X149.417 Y152.271
G1 X149.56 Y152.414
G1 X157.668 Y160.521 E.4356
G1 X157.811 Y160.665
G1 X157.811 Y161.228
G1 X157.668 Y161.085
G1 X148.997 Y152.414 E.46587
G1 X148.854 Y152.271
G1 X148.29 Y152.271
G1 X148.433 Y152.414
G1 X157.668 Y161.648 E.49615
G1 X157.811 Y161.792
G1 X157.811 Y162.355
G1 X157.668 Y162.212
G1 X147.87 Y152.414 E.52643
G1 X147.727 Y152.271
G1 X147.163 Y152.271
G1 X147.306 Y152.414
G1 X157.668 Y162.776 E.55671
; WIPE_START
M204 S8000
G1 X156.253 Y161.361 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.389 Y167.008 Z3.48 F60000
G1 X161.914 Y167.586 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S2000
G1 X146.743 Y152.414 E.81517
G1 X146.599 Y152.271
G1 X146.036 Y152.271
G1 X146.179 Y152.414
G1 X161.351 Y167.586 E.81517
G1 X161.494 Y167.729
G1 X160.93 Y167.729
G1 X160.787 Y167.586
G1 X145.616 Y152.414 E.81517
G1 X145.472 Y152.271
G1 X144.909 Y152.271
G1 X145.052 Y152.414
G1 X160.224 Y167.586 E.81517
G1 X160.367 Y167.729
G1 X159.803 Y167.729
G1 X159.66 Y167.586
G1 X144.488 Y152.414 E.81517
G1 X144.345 Y152.271
G1 X143.782 Y152.271
G1 X143.925 Y152.414
G1 X159.097 Y167.586 E.81517
G1 X159.24 Y167.729
G1 X158.676 Y167.729
G1 X158.533 Y167.586
G1 X143.361 Y152.414 E.81517
G1 X143.218 Y152.271
G1 X142.655 Y152.271
G1 X142.798 Y152.414
G1 X147.099 Y156.715 E.23109
G1 X147.242 Y156.858
G1 X146.678 Y156.858
G1 X146.535 Y156.715
G1 X142.234 Y152.414 E.23109
G1 X142.091 Y152.271
G1 X141.527 Y152.271
G1 X141.671 Y152.414
G1 X145.972 Y156.715 E.23109
G1 X146.115 Y156.858
G1 X145.551 Y156.858
G1 X145.408 Y156.715
G1 X141.107 Y152.414 E.23109
G1 X140.964 Y152.271
G1 X140.4 Y152.271
G1 X140.544 Y152.414
G1 X144.845 Y156.715 E.23109
G1 X144.988 Y156.858
G1 X144.424 Y156.858
G1 X144.281 Y156.715
G1 X139.98 Y152.414 E.23109
G1 X139.837 Y152.271
G1 X139.273 Y152.271
G1 X139.416 Y152.414
G1 X143.717 Y156.715 E.23109
G1 X143.861 Y156.858
G1 X143.297 Y156.858
G1 X143.154 Y156.715
G1 X138.853 Y152.414 E.23109
G1 X138.71 Y152.271
G1 X138.146 Y152.271
G1 X138.289 Y152.414
G1 X142.59 Y156.715 E.23109
G1 X142.734 Y156.858
G1 X142.17 Y156.858
G1 X142.027 Y156.715
G1 X137.726 Y152.414 E.23109
G1 X137.583 Y152.271
G1 X137.019 Y152.271
G1 X137.162 Y152.414
G1 X141.463 Y156.715 E.23109
G1 X141.606 Y156.858
G1 X141.043 Y156.858
G1 X140.9 Y156.715
G1 X136.599 Y152.414 E.23109
G1 X136.456 Y152.271
G1 X135.892 Y152.271
G1 X136.035 Y152.414
G1 X140.336 Y156.715 E.23109
G1 X140.479 Y156.858
G1 X139.916 Y156.858
G1 X139.773 Y156.715
G1 X135.472 Y152.414 E.23109
G1 X135.328 Y152.271
G1 X134.765 Y152.271
G1 X134.908 Y152.414
G1 X139.209 Y156.715 E.23109
G1 X139.352 Y156.858
G1 X138.789 Y156.858
G1 X138.646 Y156.715
G1 X134.345 Y152.414 E.23109
G1 X134.201 Y152.271
G1 X133.638 Y152.271
G1 X133.781 Y152.414
G1 X138.082 Y156.715 E.23109
G1 X138.225 Y156.858
G1 X137.801 Y156.998
G1 X137.658 Y156.855
G1 X133.217 Y152.414 E.23858
G1 X133.074 Y152.271
G1 X132.771 Y152.531
G1 X132.914 Y152.674
G1 X137.618 Y157.378 E.25271
G1 X137.761 Y157.521
G1 X137.761 Y158.085
G1 X137.618 Y157.941
G1 X132.914 Y153.238 E.25271
G1 X132.771 Y153.095
G1 X132.771 Y153.658
G1 X132.914 Y153.802
G1 X137.618 Y158.505 E.25271
G1 X137.761 Y158.648
G1 X137.761 Y159.212
G1 X137.618 Y159.068
G1 X132.914 Y154.365 E.25271
G1 X132.771 Y154.222
G1 X132.771 Y154.785
G1 X132.914 Y154.929
G1 X137.618 Y159.632 E.25271
G1 X137.761 Y159.775
G1 X137.761 Y160.339
G1 X137.618 Y160.196
G1 X132.914 Y155.492 E.25271
G1 X132.771 Y155.349
G1 X132.771 Y155.913
G1 X132.914 Y156.056
G1 X137.618 Y160.759 E.25271
G1 X137.761 Y160.902
G1 X137.761 Y161.466
G1 X137.618 Y161.323
G1 X132.914 Y156.619 E.25271
G1 X132.771 Y156.476
G1 X132.771 Y157.04
G1 X132.914 Y157.183
G1 X137.618 Y161.886 E.25271
G1 X137.761 Y162.029
G1 X137.761 Y162.593
G1 X137.618 Y162.45
G1 X132.914 Y157.746 E.25271
G1 X132.771 Y157.603
G1 X132.771 Y158.167
G1 X132.914 Y158.31
G1 X137.618 Y163.013 E.25271
; WIPE_START
M204 S8000
G1 X136.203 Y161.599 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X143.278 Y158.735 Z3.48 F60000
G1 X147.435 Y157.051 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S2000
G1 X157.969 Y167.586 E.56601
G1 X158.113 Y167.729
G1 X157.549 Y167.729
G1 X157.406 Y167.586
G1 X147.435 Y157.615 E.53573
G1 X147.292 Y157.472
G1 X147.292 Y158.035
G1 X147.435 Y158.179
G1 X156.842 Y167.586 E.50545
G1 X156.986 Y167.729
G1 X156.422 Y167.729
G1 X156.279 Y167.586
G1 X147.435 Y158.742 E.47517
G1 X147.292 Y158.599
G1 X147.292 Y159.162
G1 X147.435 Y159.306
G1 X155.715 Y167.586 E.44489
G1 X155.858 Y167.729
G1 X155.295 Y167.729
G1 X155.152 Y167.586
G1 X147.435 Y159.869 E.41461
G1 X147.292 Y159.726
G1 X147.292 Y160.29
G1 X147.435 Y160.433
G1 X154.588 Y167.586 E.38433
G1 X154.731 Y167.729
G1 X154.168 Y167.729
G1 X154.025 Y167.586
G1 X147.435 Y160.996 E.35405
G1 X147.292 Y160.853
G1 X147.292 Y161.417
G1 X147.435 Y161.56
G1 X153.461 Y167.586 E.32377
G1 X153.604 Y167.729
G1 X153.041 Y167.729
G1 X152.897 Y167.586
G1 X147.435 Y162.123 E.2935
G1 X147.292 Y161.98
G1 X147.292 Y162.544
G1 X147.435 Y162.687
G1 X152.334 Y167.586 E.26322
G1 X152.477 Y167.729
G1 X151.914 Y167.729
G1 X151.77 Y167.586
G1 X147.435 Y163.25 E.23294
G1 X147.292 Y163.107
G1 X146.763 Y163.142
G1 X146.906 Y163.285
G1 X151.207 Y167.586 E.23109
G1 X151.35 Y167.729
G1 X150.786 Y167.729
G1 X150.643 Y167.586
M73 P70 R4
G1 X146.342 Y163.285 E.23109
G1 X146.199 Y163.142
G1 X145.636 Y163.142
G1 X145.779 Y163.285
G1 X150.08 Y167.586 E.23109
G1 X150.223 Y167.729
G1 X149.659 Y167.729
G1 X149.516 Y167.586
G1 X145.215 Y163.285 E.23109
G1 X145.072 Y163.142
G1 X144.508 Y163.142
G1 X144.652 Y163.285
G1 X148.953 Y167.586 E.23109
G1 X149.096 Y167.729
G1 X148.532 Y167.729
G1 X148.389 Y167.586
G1 X144.088 Y163.285 E.23109
G1 X143.945 Y163.142
G1 X143.381 Y163.142
G1 X143.525 Y163.285
G1 X147.826 Y167.586 E.23109
G1 X147.969 Y167.729
G1 X147.405 Y167.729
G1 X147.262 Y167.586
G1 X142.961 Y163.285 E.23109
G1 X142.818 Y163.142
G1 X142.254 Y163.142
G1 X142.397 Y163.285
G1 X146.698 Y167.586 E.23109
G1 X146.842 Y167.729
G1 X146.278 Y167.729
G1 X146.135 Y167.586
G1 X141.834 Y163.285 E.23109
G1 X141.691 Y163.142
G1 X141.127 Y163.142
G1 X141.27 Y163.285
G1 X145.571 Y167.586 E.23109
G1 X145.715 Y167.729
G1 X145.151 Y167.729
G1 X145.008 Y167.586
G1 X140.707 Y163.285 E.23109
G1 X140.564 Y163.142
G1 X140 Y163.142
G1 X140.143 Y163.285
G1 X144.444 Y167.586 E.23109
G1 X144.587 Y167.729
G1 X144.024 Y167.729
G1 X143.881 Y167.586
G1 X139.58 Y163.285 E.23109
G1 X139.437 Y163.142
G1 X138.873 Y163.142
G1 X139.016 Y163.285
G1 X143.317 Y167.586 E.23109
G1 X143.46 Y167.729
G1 X142.897 Y167.729
G1 X142.754 Y167.586
G1 X138.453 Y163.285 E.23109
G1 X138.309 Y163.142
G1 X137.746 Y163.142
G1 X137.889 Y163.285
G1 X142.19 Y167.586 E.23109
G1 X142.333 Y167.729
G1 X141.77 Y167.729
G1 X141.626 Y167.586
G1 X132.914 Y158.873 E.46811
G1 X132.771 Y158.73
G1 X132.771 Y159.294
G1 X132.914 Y159.437
G1 X141.063 Y167.586 E.43783
G1 X141.206 Y167.729
G1 X140.643 Y167.729
G1 X140.499 Y167.586
G1 X132.914 Y160.001 E.40755
G1 X132.771 Y159.857
G1 X132.771 Y160.421
G1 X132.914 Y160.564
G1 X139.936 Y167.586 E.37727
G1 X140.079 Y167.729
G1 X139.515 Y167.729
G1 X139.372 Y167.586
G1 X132.914 Y161.128 E.34699
G1 X132.771 Y160.985
G1 X132.771 Y161.548
G1 X132.914 Y161.691
G1 X138.809 Y167.586 E.31671
G1 X138.952 Y167.729
G1 X138.388 Y167.729
G1 X138.245 Y167.586
G1 X132.914 Y162.255 E.28643
G1 X132.771 Y162.112
G1 X132.771 Y162.675
G1 X132.914 Y162.818
G1 X137.682 Y167.586 E.25616
G1 X137.825 Y167.729
G1 X137.261 Y167.729
G1 X137.118 Y167.586
G1 X132.914 Y163.382 E.22588
G1 X132.771 Y163.239
G1 X132.771 Y163.802
G1 X132.914 Y163.945
G1 X136.555 Y167.586 E.1956
G1 X136.698 Y167.729
G1 X136.134 Y167.729
G1 X135.991 Y167.586
G1 X132.914 Y164.509 E.16532
G1 X132.771 Y164.366
G1 X132.771 Y164.929
G1 X132.914 Y165.073
G1 X135.427 Y167.586 E.13504
G1 X135.571 Y167.729
G1 X135.007 Y167.729
G1 X134.864 Y167.586
G1 X132.914 Y165.636 E.10476
G1 X132.771 Y165.493
G1 X132.771 Y166.056
G1 X132.914 Y166.2
G1 X134.3 Y167.586 E.07448
G1 X134.444 Y167.729
G1 X133.88 Y167.729
G1 X133.737 Y167.586
G1 X132.914 Y166.763 E.0442
; CHANGE_LAYER
; Z_HEIGHT: 3.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
M204 S8000
G1 X133.737 Y167.586 E-.44209
G1 X133.88 Y167.729 E-.07695
G1 X134.444 Y167.729 E-.21415
G1 X134.394 Y167.679 E-.02682
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 14/47
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z3.48 I.12 J1.211 P1  F60000
G1 X177.518 Y163.407 Z3.48
G1 Z3.32
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X187.482 Y156.593 E.37852
G1 X187.482 Y163.407 E.25885
G1 X177.578 Y163.407 E.37624
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X187.865 Y156.21 E.37697
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X177.195 Y163.79 E.37486
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.89 Y156.758 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.40976
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X177.89 Y163.04 E.32911
G1 X178.35 Y163.04 E.02408
G1 X178.35 Y156.96 E.3185
G1 X178.81 Y156.96 E.02408
G1 X178.81 Y163.04 E.3185
G1 X179.269 Y163.04 E.02408
G1 X179.269 Y156.96 E.3185
G1 X179.729 Y156.96 E.02408
G1 X179.729 Y163.04 E.3185
G1 X180.189 Y163.04 E.02408
G1 X180.189 Y156.96 E.3185
G1 X180.649 Y156.96 E.02408
G1 X180.649 Y163.04 E.3185
G1 X181.108 Y163.04 E.02408
G1 X181.108 Y156.96 E.3185
G1 X181.568 Y156.96 E.02408
G1 X181.568 Y163.04 E.3185
G1 X182.028 Y163.04 E.02408
G1 X182.028 Y156.96 E.3185
G1 X182.488 Y156.96 E.02408
G1 X182.488 Y163.04 E.3185
G1 X182.947 Y163.04 E.02408
G1 X182.947 Y156.96 E.3185
G1 X183.407 Y156.96 E.02408
G1 X183.407 Y163.04 E.3185
G1 X183.867 Y163.04 E.02408
G1 X183.867 Y156.96 E.3185
G1 X184.327 Y156.96 E.02408
G1 X184.327 Y163.04 E.3185
G1 X184.786 Y163.04 E.02408
G1 X184.786 Y156.96 E.3185
G1 X185.246 Y156.96 E.02408
G1 X185.246 Y163.04 E.3185
G1 X185.706 Y163.04 E.02408
M73 P71 R4
G1 X185.706 Y156.96 E.3185
G1 X186.166 Y156.96 E.02408
G1 X186.166 Y163.04 E.3185
G1 X186.625 Y163.04 E.02408
G1 X186.625 Y156.96 E.3185
G1 X187.085 Y156.96 E.02408
G1 X187.085 Y163.242 E.32911
M106 S0
; COOLING_NODE: 7
; WIPE_START
G1 X187.085 Y161.242 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.01 Y155.542 Z3.72 F60000
G1 X180.295 Y153.616 Z3.72
G1 Z3.32
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.379456
; LAYER_HEIGHT: 0.24
G1 F12000
M204 S5000
G1 X180.279 Y153.614 E.0005
G1 X180.295 Y153.535 E.00253
G1 X180.295 Y153.556 E.00066
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X180.279 Y153.614 E-.28265
G1 X180.295 Y153.535 E-.37869
G1 X180.295 Y153.556 E-.09866
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X174.253 Y158.219 Z3.72 F60000
G1 X167.532 Y163.407 Z3.72
G1 Z3.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X157.468 Y163.407 E.38232
G1 X157.468 Y156.593 E.25885
G1 X167.532 Y156.593 E.38232
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X157.085 Y163.79 E.38048
G1 X157.085 Y156.21 E.2663
G1 X167.915 Y156.21 E.38048
G1 X167.915 Y163.73 E.2642
M204 S10000
G1 X167.135 Y163.242 F60000
; FEATURE: Bridge
; LINE_WIDTH: 0.41073
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X167.135 Y156.96 E.33067
G1 X166.674 Y156.96 E.02425
G1 X166.674 Y163.04 E.32001
G1 X166.213 Y163.04 E.02425
G1 X166.213 Y156.96 E.32001
G1 X165.753 Y156.96 E.02425
G1 X165.753 Y163.04 E.32001
G1 X165.292 Y163.04 E.02425
G1 X165.292 Y156.96 E.32001
G1 X164.831 Y156.96 E.02425
G1 X164.831 Y163.04 E.32001
G1 X164.37 Y163.04 E.02425
G1 X164.37 Y156.96 E.32001
G1 X163.91 Y156.96 E.02425
G1 X163.91 Y163.04 E.32001
G1 X163.449 Y163.04 E.02425
G1 X163.449 Y156.96 E.32001
G1 X162.988 Y156.96 E.02425
G1 X162.988 Y163.04 E.32001
G1 X162.527 Y163.04 E.02425
G1 X162.527 Y156.96 E.32001
G1 X162.067 Y156.96 E.02425
G1 X162.067 Y163.04 E.32001
G1 X161.606 Y163.04 E.02425
G1 X161.606 Y156.96 E.32001
G1 X161.145 Y156.96 E.02425
G1 X161.145 Y163.04 E.32001
G1 X160.685 Y163.04 E.02425
G1 X160.685 Y156.96 E.32001
G1 X160.224 Y156.96 E.02425
G1 X160.224 Y163.04 E.32001
G1 X159.763 Y163.04 E.02425
G1 X159.763 Y156.96 E.32001
G1 X159.302 Y156.96 E.02425
G1 X159.302 Y163.04 E.32001
G1 X158.842 Y163.04 E.02425
G1 X158.842 Y156.96 E.32001
G1 X158.381 Y156.96 E.02425
G1 X158.381 Y163.04 E.32001
G1 X157.92 Y163.04 E.02425
G1 X157.92 Y156.758 E.33067
M106 S0
; COOLING_NODE: 5
; WIPE_START
M73 P71 R3
G1 X157.92 Y158.758 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.104 Y154.57 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.379456
; LAYER_HEIGHT: 0.24
G1 F12000
M204 S5000
G1 X162.91 Y154.301 E.01037
G1 X163.104 Y154.242 E.00633
G1 X163.104 Y154.51 E.00839
; COOLING_NODE: 4
; WIPE_START
M204 S8000
G1 X162.91 Y154.301 E-.28666
G1 X163.104 Y154.242 E-.20356
G1 X163.104 Y154.51 E-.26977
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.3 Y153.637 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
G1 F12000
M204 S5000
G1 X160.278 Y153.622 E.00083
M73 P72 R3
G1 X160.295 Y153.535 E.00279
G1 X160.295 Y153.578 E.00134
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X160.278 Y153.622 E-.20216
G1 X160.295 Y153.535 E-.37699
G1 X160.295 Y153.578 E-.18085
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.257 Y158.246 Z3.72 F60000
G1 X147.581 Y163.407 Z3.72
G1 Z3.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.38612
G1 X137.418 Y156.593 E.25885
G1 X147.581 Y156.593 E.38612
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.384
G1 X137.035 Y156.21 E.2663
G1 X147.965 Y156.21 E.384
G1 X147.965 Y163.73 E.2642
M204 S10000
G1 X147.185 Y163.242 F60000
; FEATURE: Bridge
; LINE_WIDTH: 0.41073
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X147.185 Y156.96 E.33067
G1 X146.724 Y156.96 E.02425
G1 X146.724 Y163.04 E.32001
G1 X146.263 Y163.04 E.02425
G1 X146.263 Y156.96 E.32001
G1 X145.803 Y156.96 E.02425
G1 X145.803 Y163.04 E.32001
G1 X145.342 Y163.04 E.02425
G1 X145.342 Y156.96 E.32001
G1 X144.881 Y156.96 E.02425
G1 X144.881 Y163.04 E.32001
G1 X144.42 Y163.04 E.02425
G1 X144.42 Y156.96 E.32001
G1 X143.96 Y156.96 E.02425
G1 X143.96 Y163.04 E.32001
G1 X143.499 Y163.04 E.02425
G1 X143.499 Y156.96 E.32001
G1 X143.038 Y156.96 E.02425
G1 X143.038 Y163.04 E.32001
G1 X142.577 Y163.04 E.02425
G1 X142.577 Y156.96 E.32001
G1 X142.117 Y156.96 E.02425
G1 X142.117 Y163.04 E.32001
G1 X141.656 Y163.04 E.02425
G1 X141.656 Y156.96 E.32001
G1 X141.195 Y156.96 E.02425
G1 X141.195 Y163.04 E.32001
G1 X140.735 Y163.04 E.02425
G1 X140.735 Y156.96 E.32001
G1 X140.274 Y156.96 E.02425
G1 X140.274 Y163.04 E.32001
G1 X139.813 Y163.04 E.02425
G1 X139.813 Y156.96 E.32001
G1 X139.352 Y156.96 E.02425
G1 X139.352 Y163.04 E.32001
G1 X138.892 Y163.04 E.02425
G1 X138.892 Y156.96 E.32001
G1 X138.431 Y156.96 E.02425
G1 X138.431 Y163.04 E.32001
G1 X137.97 Y163.04 E.02425
G1 X137.97 Y156.758 E.33067
M106 S0
; WIPE_START
G1 X137.97 Y158.758 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X137.679 Y163.146 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.391504
; LAYER_HEIGHT: 0.24
G1 F13235.295
M204 S8000
G1 X137.679 Y156.914 E.20203
; COOLING_NODE: 2
; WIPE_START
G1 X137.679 Y158.914 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.295 Y153.616 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.379456
G1 F12000
M204 S5000
G1 X140.279 Y153.614 E.0005
G1 X140.295 Y153.535 E.00253
G1 X140.295 Y153.556 E.00066
; CHANGE_LAYER
; Z_HEIGHT: 3.56
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X140.279 Y153.614 E-.2825
G1 X140.295 Y153.535 E-.37868
G1 X140.295 Y153.556 E-.09883
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 15/47
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z3.72 I-.311 J1.176 P1  F60000
G1 X177.518 Y163.407 Z3.72
G1 Z3.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X187.482 Y156.593 E.37852
G1 X187.482 Y163.407 E.25885
G1 X177.578 Y163.407 E.37624
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X187.865 Y156.21 E.37697
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X177.195 Y163.79 E.37486
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.679 Y162.499 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.421234
G1 F12171.045
M204 S8000
G1 X178.261 Y163.081 E.02902
G1 X178.783 Y163.081 E.01843
G1 X177.844 Y162.142 E.04682
G1 X177.844 Y161.619 E.01843
G1 X179.306 Y163.081 E.07288
G1 X179.829 Y163.081 E.01843
G1 X177.844 Y161.096 E.09895
G1 X177.844 Y160.573 E.01843
G1 X180.352 Y163.081 E.12501
G1 X180.875 Y163.081 E.01843
G1 X177.844 Y160.05 E.15108
G1 X177.844 Y159.527 E.01843
G1 X181.398 Y163.081 E.17715
G1 X181.921 Y163.081 E.01843
G1 X177.844 Y159.004 E.20321
G1 X177.844 Y158.481 E.01843
G1 X182.444 Y163.081 E.22928
G1 X182.966 Y163.081 E.01843
G1 X177.844 Y157.959 E.25534
G1 X177.844 Y157.436 E.01843
G1 X183.489 Y163.081 E.28141
G1 X184.012 Y163.081 E.01843
G1 X177.851 Y156.919 E.30715
G1 X178.374 Y156.919 E.01843
M73 P73 R3
G1 X184.535 Y163.081 E.30715
G1 X185.058 Y163.081 E.01843
G1 X178.897 Y156.919 E.30715
G1 X179.419 Y156.919 E.01843
G1 X185.581 Y163.081 E.30715
G1 X186.104 Y163.081 E.01843
G1 X179.942 Y156.919 E.30715
G1 X180.465 Y156.919 E.01843
G1 X186.627 Y163.081 E.30715
G1 X187.149 Y163.081 E.01843
G1 X180.988 Y156.919 E.30715
G1 X181.511 Y156.919 E.01843
G1 X187.156 Y162.564 E.28139
G1 X187.156 Y162.041 E.01843
G1 X182.034 Y156.919 E.25533
G1 X182.557 Y156.919 E.01843
G1 X187.156 Y161.518 E.22926
G1 X187.156 Y160.995 E.01843
G1 X183.08 Y156.919 E.2032
G1 X183.603 Y156.919 E.01843
G1 X187.156 Y160.472 E.17713
G1 X187.156 Y159.95 E.01843
G1 X184.125 Y156.919 E.15106
G1 X184.648 Y156.919 E.01843
G1 X187.156 Y159.427 E.125
G1 X187.156 Y158.904 E.01843
G1 X185.171 Y156.919 E.09893
G1 X185.694 Y156.919 E.01843
G1 X187.156 Y158.381 E.07287
G1 X187.156 Y157.858 E.01843
G1 X186.217 Y156.919 E.0468
G1 X186.74 Y156.919 E.01843
G1 X187.322 Y157.501 E.029
; COOLING_NODE: 7
; WIPE_START
G1 X186.74 Y156.919 E-.31263
G1 X186.217 Y156.919 E-.19869
G1 X186.68 Y157.382 E-.24868
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X180.303 Y153.637 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.379456
G1 F12000
M204 S5000
G1 X180.278 Y153.62 E.00095
G1 X180.291 Y153.536 E.00268
G1 X180.296 Y153.578 E.00132
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X180.278 Y153.62 E-.20281
G1 X180.291 Y153.536 E-.37352
G1 X180.296 Y153.578 E-.18367
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X174.249 Y158.234 Z3.96 F60000
G1 X167.532 Y163.407 Z3.96
G1 Z3.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X157.468 Y163.407 E.38232
G1 X157.468 Y156.593 E.25885
G1 X167.532 Y156.593 E.38232
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X157.085 Y163.79 E.38048
G1 X157.085 Y156.21 E.2663
G1 X167.915 Y156.21 E.38048
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.915 Y163.741 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X167.372 Y157.506 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.423524
G1 F12096.124
M204 S8000
G1 X166.785 Y156.919 E.02942
G1 X166.259 Y156.919 E.01866
G1 X167.206 Y157.866 E.0475
G1 X167.206 Y158.392 E.01866
G1 X165.733 Y156.919 E.07389
G1 X165.207 Y156.919 E.01866
G1 X167.206 Y158.918 E.10028
G1 X167.206 Y159.445 E.01866
G1 X164.68 Y156.919 E.12667
G1 X164.154 Y156.919 E.01866
G1 X167.206 Y159.971 E.15306
G1 X167.206 Y160.497 E.01866
G1 X163.628 Y156.919 E.17945
G1 X163.102 Y156.919 E.01866
G1 X167.206 Y161.023 E.20584
G1 X167.206 Y161.549 E.01866
G1 X162.576 Y156.919 E.23223
G1 X162.05 Y156.919 E.01866
G1 X167.206 Y162.075 E.25862
G1 X167.206 Y162.601 E.01866
G1 X161.524 Y156.919 E.28501
G1 X160.998 Y156.919 E.01866
G1 X167.159 Y163.081 E.30905
G1 X166.633 Y163.081 E.01866
G1 X160.472 Y156.919 E.30905
G1 X159.945 Y156.919 E.01866
G1 X166.107 Y163.081 E.30905
G1 X165.581 Y163.081 E.01866
G1 X159.419 Y156.919 E.30905
G1 X158.893 Y156.919 E.01866
G1 X165.055 Y163.081 E.30905
G1 X164.528 Y163.081 E.01866
G1 X158.367 Y156.919 E.30905
G1 X157.841 Y156.919 E.01866
G1 X164.002 Y163.081 E.30905
G1 X163.476 Y163.081 E.01866
G1 X157.794 Y157.399 E.285
G1 X157.794 Y157.925 E.01866
G1 X162.95 Y163.081 E.25861
G1 X162.424 Y163.081 E.01866
G1 X157.794 Y158.451 E.23222
G1 X157.794 Y158.977 E.01866
G1 X161.898 Y163.081 E.20583
G1 X161.372 Y163.081 E.01866
G1 X157.794 Y159.503 E.17944
G1 X157.794 Y160.029 E.01866
G1 X160.846 Y163.081 E.15305
G1 X160.319 Y163.081 E.01866
G1 X157.794 Y160.555 E.12666
G1 X157.794 Y161.082 E.01866
G1 X159.793 Y163.081 E.10027
G1 X159.267 Y163.081 E.01866
G1 X157.794 Y161.608 E.07388
G1 X157.794 Y162.134 E.01866
G1 X158.741 Y163.081 E.04749
G1 X158.215 Y163.081 E.01866
G1 X157.628 Y162.494 E.02942
; COOLING_NODE: 5
; WIPE_START
G1 X158.215 Y163.081 E-.31521
G1 X158.741 Y163.081 E-.19992
G1 X158.286 Y162.625 E-.24487
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.204 Y156.075 Z3.96 F60000
G1 X163.104 Y154.57 Z3.96
G1 Z3.56
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.379456
G1 F12000
M204 S5000
G1 X162.91 Y154.301 E.01037
G1 X163.104 Y154.242 E.00633
G1 X163.104 Y154.51 E.00839
; COOLING_NODE: 4
; WIPE_START
M204 S8000
G1 X162.91 Y154.301 E-.28666
G1 X163.104 Y154.242 E-.20357
G1 X163.104 Y154.51 E-.26977
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.291 Y153.536 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
G1 F12000
M204 S5000
G1 X160.303 Y153.637 E.0032
G1 X160.278 Y153.62 E.00095
G1 X160.282 Y153.595 E.00081
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X160.303 Y153.637 E-.34753
G1 X160.278 Y153.62 E-.22307
G1 X160.282 Y153.595 E-.18941
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.242 Y158.261 Z3.96 F60000
G1 X147.581 Y163.407 Z3.96
G1 Z3.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.38612
G1 X137.418 Y156.593 E.25885
G1 X147.581 Y156.593 E.38612
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.384
G1 X137.035 Y156.21 E.2663
G1 X147.965 Y156.21 E.384
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.965 Y163.741 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.421 Y157.511 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.425804
G1 F12022.442
M204 S8000
G1 X146.83 Y156.919 E.02985
G1 X146.301 Y156.919 E.01889
G1 X147.256 Y157.874 E.04819
G1 X147.256 Y158.404 E.01889
G1 X145.771 Y156.919 E.07491
G1 X145.242 Y156.919 E.01889
G1 X147.256 Y158.933 E.10162
G1 X147.256 Y159.462 E.01889
G1 X144.713 Y156.919 E.12834
G1 X144.183 Y156.919 E.01889
G1 X147.256 Y159.992 E.15505
G1 X147.256 Y160.521 E.01889
G1 X143.654 Y156.919 E.18177
G1 X143.125 Y156.919 E.01889
G1 X147.256 Y161.05 E.20848
G1 X147.256 Y161.58 E.01889
G1 X142.595 Y156.919 E.2352
G1 X142.066 Y156.919 E.01889
G1 X147.256 Y162.109 E.26191
G1 X147.256 Y162.638 E.01889
G1 X141.537 Y156.919 E.28862
G1 X141.007 Y156.919 E.01889
G1 X147.169 Y163.081 E.31095
G1 X146.639 Y163.081 E.01889
G1 X140.478 Y156.919 E.31095
G1 X139.949 Y156.919 E.01889
G1 X146.11 Y163.081 E.31095
G1 X145.581 Y163.081 E.01889
G1 X139.419 Y156.919 E.31095
G1 X138.89 Y156.919 E.01889
G1 X145.051 Y163.081 E.31095
G1 X144.522 Y163.081 E.01889
G1 X138.361 Y156.919 E.31095
G1 X137.831 Y156.919 E.01889
G1 X143.993 Y163.081 E.31095
G1 X143.463 Y163.081 E.01889
G1 X137.744 Y157.362 E.28862
G1 X137.744 Y157.891 E.01889
G1 X142.934 Y163.081 E.26191
G1 X142.405 Y163.081 E.01889
G1 X137.744 Y158.42 E.23519
G1 X137.744 Y158.95 E.01889
G1 X141.875 Y163.081 E.20848
G1 X141.346 Y163.081 E.01889
G1 X137.744 Y159.479 E.18176
G1 X137.744 Y160.008 E.01889
G1 X140.817 Y163.081 E.15505
G1 X140.287 Y163.081 E.01889
G1 X137.744 Y160.538 E.12834
G1 X137.744 Y161.067 E.01889
G1 X139.758 Y163.081 E.10162
G1 X139.229 Y163.081 E.01889
G1 X137.744 Y161.596 E.07491
G1 X137.744 Y162.126 E.01889
G1 X138.699 Y163.081 E.04819
G1 X138.17 Y163.081 E.01889
G1 X137.578 Y162.489 E.02985
; COOLING_NODE: 2
; WIPE_START
G1 X138.17 Y163.081 E-.31781
G1 X138.699 Y163.081 E-.20115
G1 X138.251 Y162.632 E-.24104
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.921 Y155.185 Z3.96 F60000
G1 X140.291 Y153.536 Z3.96
G1 Z3.56
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.379456
G1 F12000
M204 S5000
G1 X140.303 Y153.637 E.00319
G1 X140.278 Y153.62 E.00095
G1 X140.282 Y153.595 E.0008
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X140.303 Y153.637 E-.34753
G1 X140.278 Y153.62 E-.22314
G1 X140.282 Y153.595 E-.18932
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 16/47
; update layer progress
M73 L16
M991 S0 P15 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 1
M204 S10000
G17
G3 Z3.96 I-.976 J.726 P1  F60000
G1 X147.581 Y163.407 Z3.96
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.38612
G1 X137.418 Y156.593 E.25885
G1 X147.581 Y156.593 E.38612
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.384
G1 X137.035 Y156.21 E.2663
G1 X147.965 Y156.21 E.384
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.965 Y163.741 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.953 Y163.066 Z4.2 F60000
M73 P74 R3
G1 Z3.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.359 Y163.066 E.06056
G1 X145.875 Y162.565 E.0273
G1 X146.135 Y162.138 E.01902
G1 X146.286 Y161.71 E.01723
G1 X146.325 Y160.855 E.03252
G1 X146.163 Y160.428 E.01737
G1 X145.802 Y160 E.02124
G1 X145.106 Y159.325 E.03684
G1 X145.106 Y157.731 E.06056
; WIPE_START
G1 X145.106 Y159.325 E-.60571
G1 X145.398 Y159.608 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X142.5 Y160.8 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.443784
G1 F11471.399
M204 S8000
G1 X142.5 Y159.26 E.05761
M204 S10000
G1 X142.88 Y159.2 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X142.88 Y158.819 E.01336
G1 X142.12 Y158.819 E.02673
G1 X142.12 Y161.181 E.08295
G1 X142.88 Y161.181 E.02673
G1 X142.88 Y159.26 E.06748
M204 S10000
G1 X143.249 Y159.2 F60000
G1 F12212.001
M204 S8000
G1 X143.249 Y158.451 E.02631
G1 X141.751 Y158.451 E.05262
G1 X141.751 Y161.549 E.10884
G1 X143.249 Y161.549 E.05262
G1 X143.249 Y159.26 E.08043
M204 S10000
G1 X143.617 Y159.2 F60000
G1 F12212.001
M204 S8000
G1 X143.617 Y158.082 E.03925
G1 X141.383 Y158.082 E.07851
G1 X141.383 Y161.918 E.13474
G1 X143.617 Y161.918 E.07851
G1 X143.617 Y159.26 E.09337
M204 S10000
G1 X143.986 Y159.2 F60000
G1 F12212.001
M204 S8000
G1 X143.986 Y157.714 E.0522
G1 X141.014 Y157.714 E.1044
G1 X141.014 Y162.286 E.16063
G1 X143.986 Y162.286 E.1044
G1 X143.986 Y159.26 E.10632
M204 S10000
G1 X144.354 Y159.2 F60000
G1 F12212.001
M204 S8000
G1 X144.354 Y157.345 E.06515
G1 X140.646 Y157.345 E.13029
G1 X140.646 Y162.655 E.18652
G1 X144.354 Y162.655 E.13029
G1 X144.354 Y159.26 E.11927
M204 S10000
G1 X144.723 Y159.2 F60000
G1 F12212.001
M204 S8000
G1 X144.723 Y156.977 E.07809
G1 X140.277 Y156.977 E.15618
G1 X140.277 Y163.023 E.21241
G1 X144.723 Y163.023 E.15618
G1 X144.723 Y159.26 E.13221
; WIPE_START
G1 X144.723 Y161.26 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.894 Y162.848 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X139.894 Y163.066 E.00828
G1 X138.518 Y163.066 E.05228
G1 X139.034 Y162.565 E.0273
G1 X139.294 Y162.138 E.01902
G1 X139.445 Y161.71 E.01723
G1 X139.484 Y160.855 E.03252
G1 X139.322 Y160.428 E.01737
G1 X138.961 Y160 E.02124
G1 X138.079 Y159.145 E.04667
G1 X137.819 Y158.717 E.01902
G1 X137.759 Y158.549 E.00677
G1 X137.759 Y156.955 E.06056
; COOLING_NODE: 3
; WIPE_START
G1 X137.759 Y158.549 E-.60571
G1 X137.819 Y158.717 E-.0677
G1 X137.937 Y158.912 E-.08659
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X145.483 Y160.058 Z4.2 F60000
G1 X167.532 Y163.407 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X157.468 Y163.407 E.38232
G1 X157.468 Y156.593 E.25885
G1 X167.532 Y156.593 E.38232
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X157.085 Y163.79 E.38048
G1 X157.085 Y156.21 E.2663
G1 X167.915 Y156.21 E.38048
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.915 Y163.741 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X167.191 Y162.78 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X167.191 Y163.066 E.01083
G1 X165.882 Y163.066 E.04973
G1 X166.398 Y162.565 E.0273
G1 X166.658 Y162.138 E.01902
G1 X166.809 Y161.71 E.01723
G1 X166.848 Y160.855 E.03252
G1 X166.686 Y160.428 E.01737
G1 X166.325 Y160 E.02124
G1 X165.443 Y159.145 E.04667
G1 X165.183 Y158.717 E.01902
G1 X165.032 Y158.29 E.01723
G1 X165 Y157.415 E.03324
G1 X165.155 Y157.007 E.01659
G1 X165.216 Y156.934 E.00361
G1 X166.81 Y156.934 E.06056
; WIPE_START
G1 X165.216 Y156.934 E-.60571
G1 X165.155 Y157.007 E-.0361
G1 X165.045 Y157.298 E-.11819
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.729 Y159.094 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.510294
G1 F9808.409
M204 S8000
G1 X162.729 Y158.865 E.01003
G1 X162.271 Y158.865 E.02007
G1 X162.271 Y161.135 E.09933
G1 X162.729 Y161.135 E.02007
G1 X162.729 Y159.154 E.08667
M204 S10000
G1 X163.143 Y159.094 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X163.143 Y158.451 E.02259
G1 X161.857 Y158.451 E.04518
G1 X161.857 Y161.549 E.10884
G1 X163.143 Y161.549 E.04518
G1 X163.143 Y159.154 E.08415
M204 S10000
G1 X163.512 Y159.094 F60000
G1 F12212.001
M204 S8000
G1 X163.512 Y158.082 E.03554
G1 X161.488 Y158.082 E.07107
G1 X161.488 Y161.918 E.13474
G1 X163.512 Y161.918 E.07107
G1 X163.512 Y159.154 E.09709
M204 S10000
G1 X163.88 Y159.094 F60000
G1 F12212.001
M204 S8000
G1 X163.88 Y157.714 E.04848
G1 X161.12 Y157.714 E.09697
G1 X161.12 Y162.286 E.16063
G1 X163.88 Y162.286 E.09697
G1 X163.88 Y159.154 E.11004
M204 S10000
G1 X164.249 Y159.094 F60000
G1 F12212.001
M204 S8000
G1 X164.249 Y157.345 E.06143
G1 X160.751 Y157.345 E.12286
G1 X160.751 Y162.655 E.18652
G1 X164.249 Y162.655 E.12286
G1 X164.249 Y159.154 E.12298
M204 S10000
G1 X164.617 Y159.094 F60000
G1 F12212.001
M204 S8000
G1 X164.617 Y156.977 E.07437
G1 X160.383 Y156.977 E.14875
G1 X160.383 Y163.023 E.21241
G1 X164.617 Y163.023 E.14875
G1 X164.617 Y159.154 E.13593
; WIPE_START
G1 X164.617 Y161.154 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X157.809 Y157.962 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X157.809 Y156.934 E.03905
G1 X158.375 Y156.934 E.02151
G1 X158.314 Y157.007 E.00361
G1 X158.152 Y157.435 E.01737
G1 X158.191 Y158.29 E.03252
G1 X158.342 Y158.717 E.01723
G1 X158.602 Y159.145 E.01902
G1 X159.484 Y160 E.04667
G1 X159.845 Y160.428 E.02124
G1 X160 Y160.836 E.01659
G1 X159.968 Y161.71 E.03324
G1 X159.817 Y162.138 E.01723
G1 X159.557 Y162.565 E.01902
G1 X159.041 Y163.066 E.0273
G1 X157.809 Y163.066 E.04678
G1 X157.809 Y162.703 E.01378
; COOLING_NODE: 6
; WIPE_START
G1 X157.809 Y163.066 E-.13781
G1 X159.041 Y163.066 E-.4679
G1 X159.332 Y162.783 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.96 Y163.044 Z4.2 F60000
G1 X177.518 Y163.407 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X187.482 Y156.593 E.37852
G1 X187.482 Y163.407 E.25885
G1 X177.578 Y163.407 E.37624
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X187.865 Y156.21 E.37697
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X177.195 Y163.79 E.37486
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.426 Y156.753 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.421244
G1 F12170.715
M204 S8000
G1 X177.844 Y157.335 E.02902
G1 X177.844 Y157.858 E.01843
G1 X178.783 Y156.919 E.04682
G1 X179.306 Y156.919 E.01843
G1 X177.844 Y158.381 E.07288
G1 X177.844 Y158.904 E.01843
G1 X179.829 Y156.919 E.09895
G1 X180.352 Y156.919 E.01843
G1 X177.844 Y159.427 E.12502
G1 X177.844 Y159.95 E.01843
G1 X180.875 Y156.919 E.15109
G1 X181.398 Y156.919 E.01843
G1 X177.844 Y160.473 E.17715
G1 X177.844 Y160.996 E.01843
G1 X181.921 Y156.919 E.20322
G1 X182.444 Y156.919 E.01843
G1 X177.844 Y161.519 E.22929
G1 X177.844 Y162.041 E.01843
G1 X182.966 Y156.919 E.25536
G1 X183.489 Y156.919 E.01843
G1 X177.844 Y162.564 E.28142
G1 X177.844 Y163.081 E.01821
G1 X184.012 Y156.919 E.30733
G1 X184.535 Y156.919 E.01843
G1 X178.374 Y163.081 E.30717
G1 X178.896 Y163.081 E.01843
G1 X185.058 Y156.919 E.30717
G1 X185.581 Y156.919 E.01843
G1 X179.419 Y163.081 E.30717
G1 X179.942 Y163.081 E.01843
G1 X186.104 Y156.919 E.30717
G1 X186.627 Y156.919 E.01843
G1 X180.465 Y163.081 E.30717
G1 X180.988 Y163.081 E.01843
G1 X187.156 Y156.919 E.30733
G1 X187.156 Y157.436 E.01821
G1 X181.511 Y163.081 E.28141
G1 X182.034 Y163.081 E.01843
G1 X187.156 Y157.959 E.25534
G1 X187.156 Y158.482 E.01843
G1 X182.557 Y163.081 E.22928
G1 X183.08 Y163.081 E.01843
G1 X187.156 Y159.005 E.20321
G1 X187.156 Y159.527 E.01843
G1 X183.602 Y163.081 E.17714
G1 X184.125 Y163.081 E.01843
G1 X187.156 Y160.05 E.15107
G1 X187.156 Y160.573 E.01843
G1 X184.648 Y163.081 E.12501
G1 X185.171 Y163.081 E.01843
G1 X187.156 Y161.096 E.09894
G1 X187.156 Y161.619 E.01843
G1 X185.694 Y163.081 E.07287
G1 X186.217 Y163.081 E.01843
G1 X187.156 Y162.142 E.0468
G1 X187.156 Y162.665 E.01843
G1 X186.574 Y163.247 E.029
; CHANGE_LAYER
; Z_HEIGHT: 4.04
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12170.715
G1 X187.156 Y162.665 E-.31264
G1 X187.156 Y162.142 E-.1987
G1 X186.693 Y162.605 E-.24866
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 17/47
; update layer progress
M73 L17
M991 S0 P16 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 1
M204 S10000
G17
G3 Z4.2 I-.025 J-1.217 P1  F60000
G1 X147.581 Y163.407 Z4.2
G1 Z4.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.38612
G1 X137.418 Y156.593 E.25885
G1 X147.581 Y156.593 E.38612
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.384
G1 X137.035 Y156.21 E.2663
G1 X147.965 Y156.21 E.384
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.965 Y163.741 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.422 Y157.511 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.425814
G1 F12022.122
M204 S8000
G1 X146.83 Y156.919 E.02985
M73 P75 R3
G1 X146.301 Y156.919 E.01889
G1 X147.256 Y157.874 E.0482
G1 X147.256 Y158.404 E.01889
G1 X145.771 Y156.919 E.07491
G1 X145.242 Y156.919 E.01889
G1 X147.256 Y158.933 E.10163
G1 X147.256 Y159.462 E.01889
G1 X144.713 Y156.919 E.12834
G1 X144.183 Y156.919 E.01889
G1 X147.256 Y159.992 E.15506
G1 X147.256 Y160.521 E.01889
G1 X143.654 Y156.919 E.18178
G1 X143.125 Y156.919 E.01889
G1 X147.256 Y161.05 E.20849
G1 X147.256 Y161.58 E.01889
G1 X142.595 Y156.919 E.23521
G1 X142.066 Y156.919 E.01889
G1 X147.256 Y162.109 E.26192
G1 X147.256 Y162.638 E.01889
G1 X141.537 Y156.919 E.28864
G1 X141.007 Y156.919 E.01889
G1 X147.169 Y163.081 E.31097
G1 X146.639 Y163.081 E.01889
G1 X140.478 Y156.919 E.31097
G1 X139.949 Y156.919 E.01889
G1 X146.11 Y163.081 E.31097
G1 X145.581 Y163.081 E.01889
G1 X139.419 Y156.919 E.31097
G1 X138.89 Y156.919 E.01889
G1 X145.051 Y163.081 E.31097
G1 X144.522 Y163.081 E.01889
G1 X138.36 Y156.919 E.31097
G1 X137.831 Y156.919 E.01889
G1 X143.993 Y163.081 E.31097
G1 X143.463 Y163.081 E.01889
G1 X137.744 Y157.362 E.28864
G1 X137.744 Y157.891 E.01889
G1 X142.934 Y163.081 E.26192
G1 X142.405 Y163.081 E.01889
G1 X137.744 Y158.42 E.2352
G1 X137.744 Y158.95 E.01889
G1 X141.875 Y163.081 E.20849
G1 X141.346 Y163.081 E.01889
G1 X137.744 Y159.479 E.18177
G1 X137.744 Y160.008 E.01889
G1 X140.817 Y163.081 E.15506
G1 X140.287 Y163.081 E.01889
G1 X137.744 Y160.538 E.12834
G1 X137.744 Y161.067 E.01889
G1 X139.758 Y163.081 E.10162
G1 X139.228 Y163.081 E.01889
G1 X137.744 Y161.597 E.07491
G1 X137.744 Y162.126 E.01889
G1 X138.699 Y163.081 E.04819
G1 X138.17 Y163.081 E.01889
G1 X137.578 Y162.489 E.02985
; COOLING_NODE: 3
; WIPE_START
G1 X138.17 Y163.081 E-.31781
G1 X138.699 Y163.081 E-.20116
G1 X138.251 Y162.632 E-.24103
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X145.88 Y162.834 Z4.44 F60000
G1 X167.532 Y163.407 Z4.44
G1 Z4.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X157.468 Y163.407 E.38232
G1 X157.468 Y156.593 E.25885
G1 X167.532 Y156.593 E.38232
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X157.085 Y163.79 E.38048
G1 X157.085 Y156.21 E.2663
G1 X167.915 Y156.21 E.38048
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.915 Y163.741 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X167.372 Y157.506 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.423534
G1 F12095.8
M204 S8000
G1 X166.785 Y156.919 E.02943
G1 X166.259 Y156.919 E.01866
G1 X167.206 Y157.866 E.0475
G1 X167.206 Y158.392 E.01866
G1 X165.733 Y156.919 E.07389
G1 X165.207 Y156.919 E.01866
G1 X167.206 Y158.918 E.10028
G1 X167.206 Y159.445 E.01866
G1 X164.68 Y156.919 E.12667
G1 X164.154 Y156.919 E.01866
G1 X167.206 Y159.971 E.15306
G1 X167.206 Y160.497 E.01866
G1 X163.628 Y156.919 E.17946
G1 X163.102 Y156.919 E.01866
G1 X167.206 Y161.023 E.20585
G1 X167.206 Y161.549 E.01866
G1 X162.576 Y156.919 E.23224
G1 X162.05 Y156.919 E.01866
G1 X167.206 Y162.075 E.25863
G1 X167.206 Y162.601 E.01866
G1 X161.524 Y156.919 E.28502
G1 X160.998 Y156.919 E.01866
G1 X167.159 Y163.081 E.30907
G1 X166.633 Y163.081 E.01866
G1 X160.471 Y156.919 E.30907
G1 X159.945 Y156.919 E.01866
G1 X166.107 Y163.081 E.30907
G1 X165.581 Y163.081 E.01866
G1 X159.419 Y156.919 E.30907
G1 X158.893 Y156.919 E.01866
G1 X165.055 Y163.081 E.30907
G1 X164.528 Y163.081 E.01866
G1 X158.367 Y156.919 E.30907
G1 X157.841 Y156.919 E.01866
G1 X164.002 Y163.081 E.30907
G1 X163.476 Y163.081 E.01866
G1 X157.794 Y157.399 E.28502
G1 X157.794 Y157.925 E.01866
G1 X162.95 Y163.081 E.25863
G1 X162.424 Y163.081 E.01866
G1 X157.794 Y158.451 E.23223
G1 X157.794 Y158.977 E.01866
G1 X161.898 Y163.081 E.20584
G1 X161.372 Y163.081 E.01866
G1 X157.794 Y159.503 E.17945
G1 X157.794 Y160.029 E.01866
G1 X160.846 Y163.081 E.15306
G1 X160.319 Y163.081 E.01866
G1 X157.794 Y160.556 E.12667
G1 X157.794 Y161.082 E.01866
G1 X159.793 Y163.081 E.10028
G1 X159.267 Y163.081 E.01866
G1 X157.794 Y161.608 E.07389
G1 X157.794 Y162.134 E.01866
G1 X158.741 Y163.081 E.0475
G1 X158.215 Y163.081 E.01866
G1 X157.628 Y162.494 E.02942
; COOLING_NODE: 6
; WIPE_START
G1 X158.215 Y163.081 E-.31521
G1 X158.741 Y163.081 E-.19993
G1 X158.285 Y162.625 E-.24486
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.912 Y162.935 Z4.44 F60000
G1 X177.518 Y163.407 Z4.44
G1 Z4.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X187.482 Y156.593 E.37852
G1 X187.482 Y163.407 E.25885
G1 X177.578 Y163.407 E.37624
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X187.865 Y156.21 E.37697
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X177.195 Y163.79 E.37486
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.678 Y162.499 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.421244
G1 F12170.715
M204 S8000
G1 X178.26 Y163.081 E.02902
G1 X178.783 Y163.081 E.01843
G1 X177.844 Y162.142 E.04682
G1 X177.844 Y161.619 E.01843
G1 X179.306 Y163.081 E.07288
G1 X179.829 Y163.081 E.01843
G1 X177.844 Y161.096 E.09895
G1 X177.844 Y160.573 E.01843
G1 X180.352 Y163.081 E.12502
G1 X180.875 Y163.081 E.01843
G1 X177.844 Y160.05 E.15109
G1 X177.844 Y159.527 E.01843
G1 X181.398 Y163.081 E.17715
G1 X181.921 Y163.081 E.01843
G1 X177.844 Y159.004 E.20322
G1 X177.844 Y158.481 E.01843
G1 X182.444 Y163.081 E.22929
G1 X182.966 Y163.081 E.01843
G1 X177.844 Y157.959 E.25536
G1 X177.844 Y157.436 E.01843
G1 X183.489 Y163.081 E.28142
G1 X184.012 Y163.081 E.01843
G1 X177.851 Y156.919 E.30717
G1 X178.374 Y156.919 E.01843
G1 X184.535 Y163.081 E.30717
G1 X185.058 Y163.081 E.01843
G1 X178.896 Y156.919 E.30717
G1 X179.419 Y156.919 E.01843
G1 X185.581 Y163.081 E.30717
G1 X186.104 Y163.081 E.01843
G1 X179.942 Y156.919 E.30717
G1 X180.465 Y156.919 E.01843
G1 X186.627 Y163.081 E.30717
G1 X187.15 Y163.081 E.01843
G1 X180.988 Y156.919 E.30717
G1 X181.511 Y156.919 E.01843
G1 X187.156 Y162.564 E.28141
G1 X187.156 Y162.041 E.01843
G1 X182.034 Y156.919 E.25534
G1 X182.557 Y156.919 E.01843
G1 X187.156 Y161.518 E.22928
G1 X187.156 Y160.995 E.01843
G1 X183.08 Y156.919 E.20321
G1 X183.602 Y156.919 E.01843
G1 X187.156 Y160.473 E.17714
G1 X187.156 Y159.95 E.01843
G1 X184.125 Y156.919 E.15107
G1 X184.648 Y156.919 E.01843
G1 X187.156 Y159.427 E.12501
G1 X187.156 Y158.904 E.01843
G1 X185.171 Y156.919 E.09894
G1 X185.694 Y156.919 E.01843
G1 X187.156 Y158.381 E.07287
G1 X187.156 Y157.858 E.01843
G1 X186.217 Y156.919 E.0468
G1 X186.74 Y156.919 E.01843
G1 X187.322 Y157.501 E.029
; CHANGE_LAYER
; Z_HEIGHT: 4.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12170.715
G1 X186.74 Y156.919 E-.31264
G1 X186.217 Y156.919 E-.1987
G1 X186.68 Y157.382 E-.24866
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 18/47
; update layer progress
M73 L18
M991 S0 P17 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 1
M204 S10000
G17
G3 Z4.44 I-.185 J-1.203 P1  F60000
G1 X147.581 Y163.407 Z4.44
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X144.621 Y163.407 E.11246
G1 X144.621 Y156.593 E.25885
G1 X147.581 Y156.593 E.11246
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
; WIPE_START
G1 X145.582 Y163.387 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.378 Y163.407 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.11246
G1 X137.418 Y156.593 E.25885
G1 X140.378 Y156.593 E.11246
G1 X140.378 Y163.347 E.25657
; COOLING_NODE: 1
; WIPE_START
G1 X138.379 Y163.387 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.005 Y163.708 Z4.68 F60000
G1 X147.965 Y163.79 Z4.68
G1 Z4.28
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.384
M73 P76 R3
G1 X137.035 Y156.21 E.2663
G1 X147.965 Y156.21 E.384
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.965 Y163.741 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.101 Y161.927 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.402084
G1 F12835.873
M204 S8000
G1 X146.101 Y158.133 E.12678
M204 S10000
G1 X146.461 Y158.073 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X146.461 Y157.714 E.01263
G1 X145.742 Y157.714 E.02526
G1 X145.742 Y162.286 E.16063
G1 X146.461 Y162.286 E.02526
G1 X146.461 Y158.133 E.14589
M204 S10000
G1 X146.83 Y158.073 F60000
G1 F12212.001
M204 S8000
G1 X146.83 Y157.345 E.02558
G1 X145.373 Y157.345 E.05115
G1 X145.373 Y162.655 E.18652
G1 X146.83 Y162.655 E.05115
G1 X146.83 Y158.133 E.15883
M204 S10000
G1 X147.198 Y158.073 F60000
G1 F12212.001
M204 S8000
G1 X147.198 Y156.977 E.03852
G1 X145.005 Y156.977 E.07705
G1 X145.005 Y163.023 E.21241
G1 X147.198 Y163.023 E.07705
G1 X147.198 Y158.133 E.17178
; WIPE_START
G1 X147.198 Y160.133 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X144.402 Y163.164 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X143.98 Y163.586 E.02268
G1 X143.837 Y163.729
G1 X143.273 Y163.729
G1 X143.416 Y163.586
G1 X144.402 Y162.6 E.05296
G1 X144.545 Y162.457
G1 X144.545 Y161.893
G1 X144.402 Y162.037
G1 X142.853 Y163.586 E.08324
G1 X142.71 Y163.729
G1 X142.146 Y163.729
G1 X142.289 Y163.586
G1 X144.402 Y161.473 E.11352
G1 X144.545 Y161.33
G1 X144.545 Y160.766
G1 X144.402 Y160.909
G1 X141.726 Y163.586 E.1438
G1 X141.583 Y163.729
G1 X141.019 Y163.729
G1 X141.162 Y163.586
G1 X144.402 Y160.346 E.17408
G1 X144.545 Y160.203
G1 X144.545 Y159.639
G1 X144.402 Y159.782
G1 X140.599 Y163.586 E.20436
G1 X140.456 Y163.729
G1 X140.455 Y163.166
G1 X140.598 Y163.023
G1 X144.402 Y159.219 E.20441
G1 X144.545 Y159.076
G1 X144.545 Y158.512
G1 X144.402 Y158.655
G1 X140.598 Y162.46 E.20441
G1 X140.455 Y162.603
G1 X140.455 Y162.039
G1 X140.598 Y161.896
G1 X144.402 Y158.092 E.20441
G1 X144.545 Y157.949
G1 X144.545 Y157.385
G1 X144.402 Y157.528
G1 X140.598 Y161.333 E.20441
G1 X140.455 Y161.476
G1 X140.455 Y160.912
G1 X140.598 Y160.769
G1 X144.402 Y156.965 E.20441
G1 X144.545 Y156.821
G1 X144.532 Y156.271
G1 X144.389 Y156.414
G1 X140.598 Y160.205 E.20371
G1 X140.455 Y160.349
G1 X140.455 Y159.785
G1 X140.598 Y159.642
G1 X143.826 Y156.414 E.17343
G1 X143.969 Y156.271
G1 X143.405 Y156.271
G1 X143.262 Y156.414
G1 X140.598 Y159.078 E.14315
G1 X140.455 Y159.222
G1 X140.455 Y158.658
G1 X140.598 Y158.515
G1 X142.698 Y156.414 E.11287
G1 X142.842 Y156.271
G1 X142.278 Y156.271
G1 X142.135 Y156.414
G1 X140.598 Y157.951 E.08259
G1 X140.455 Y158.094
G1 X140.455 Y157.531
G1 X140.598 Y157.388
G1 X141.571 Y156.414 E.05231
G1 X141.715 Y156.271
G1 X141.151 Y156.271
G1 X141.008 Y156.414
G1 X140.598 Y156.824 E.02203
; WIPE_START
M204 S8000
G1 X141.008 Y156.414 E-.22035
G1 X141.151 Y156.271 E-.07695
G1 X141.715 Y156.271 E-.21415
G1 X141.571 Y156.414 E-.07695
G1 X141.252 Y156.734 E-.17162
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.898 Y161.927 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.402104
G1 F12835.14
M204 S8000
G1 X138.898 Y158.133 E.12679
M204 S10000
G1 X139.258 Y158.073 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X139.258 Y157.714 E.01263
G1 X138.539 Y157.714 E.02526
G1 X138.539 Y162.286 E.16063
G1 X139.258 Y162.286 E.02526
G1 X139.258 Y158.133 E.14589
M204 S10000
G1 X139.627 Y158.073 F60000
G1 F12212.001
M204 S8000
G1 X139.627 Y157.345 E.02558
G1 X138.17 Y157.345 E.05115
G1 X138.17 Y162.655 E.18652
G1 X139.627 Y162.655 E.05115
G1 X139.627 Y158.133 E.15883
M204 S10000
G1 X139.995 Y158.073 F60000
G1 F12212.001
M204 S8000
G1 X139.995 Y156.977 E.03852
G1 X137.802 Y156.977 E.07705
G1 X137.802 Y163.023 E.21241
G1 X139.995 Y163.023 E.07705
G1 X139.995 Y158.133 E.17178
; COOLING_NODE: 3
; WIPE_START
G1 X139.995 Y160.133 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.532 Y161.334 Z4.68 F60000
G1 X160.546 Y163.407 Z4.68
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X157.468 Y163.407 E.11692
G1 X157.468 Y156.593 E.25885
G1 X160.546 Y156.593 E.11692
G1 X160.546 Y163.347 E.25657
; COOLING_NODE: 3
; WIPE_START
G1 X158.546 Y163.386 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.179 Y163.403 Z4.68 F60000
G1 X167.532 Y163.407 Z4.68
G1 Z4.28
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X164.454 Y163.407 E.11692
G1 X164.454 Y156.593 E.25885
G1 X167.532 Y156.593 E.11692
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X157.085 Y163.79 E.38048
G1 X157.085 Y156.21 E.2663
G1 X167.915 Y156.21 E.38048
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.915 Y163.741 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.993 Y161.868 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.519604
G1 F9613.331
M204 S8000
G1 X165.993 Y158.192 E.16403
; WIPE_START
G1 X165.993 Y160.192 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.574 Y162.286 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.411 Y162.286 E.02939
G1 X166.411 Y157.714 E.16063
G1 X165.574 Y157.714 E.02939
G1 X165.574 Y162.226 E.15852
M204 S10000
G1 X165.206 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X166.78 Y162.655 E.05528
G1 X166.78 Y157.345 E.18652
G1 X165.206 Y157.345 E.05528
G1 X165.206 Y162.595 E.18441
M204 S10000
G1 X164.837 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.08117
G1 X167.148 Y156.977 E.21241
G1 X164.837 Y156.977 E.08117
G1 X164.837 Y162.963 E.2103
M204 S10000
G1 X164.235 Y163.055 F60000
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X163.704 Y163.586 E.0285
G1 X163.561 Y163.729
G1 X162.998 Y163.729
G1 X163.141 Y163.586
G1 X164.235 Y162.492 E.05878
G1 X164.378 Y162.349
G1 X164.378 Y161.785
G1 X164.235 Y161.928
G1 X162.577 Y163.586 E.08906
G1 X162.434 Y163.729
G1 X161.87 Y163.729
G1 X162.014 Y163.586
G1 X164.235 Y161.365 E.11934
G1 X164.378 Y161.222
G1 X164.378 Y160.658
G1 X164.235 Y160.801
G1 X161.45 Y163.586 E.14962
G1 X161.307 Y163.729
G1 X160.743 Y163.729
G1 X160.887 Y163.586
G1 X164.235 Y160.238 E.1799
G1 X164.378 Y160.094
G1 X164.378 Y159.531
G1 X164.235 Y159.674
G1 X160.765 Y163.144 E.18641
G1 X160.622 Y163.287
G1 X160.622 Y162.723
G1 X160.765 Y162.58
G1 X164.235 Y159.111 E.18641
G1 X164.378 Y158.967
G1 X164.378 Y158.404
G1 X164.235 Y158.547
G1 X160.765 Y162.016 E.18641
G1 X160.622 Y162.16
G1 X160.622 Y161.596
G1 X160.765 Y161.453
G1 X164.235 Y157.983 E.18641
G1 X164.378 Y157.84
G1 X164.378 Y157.277
G1 X164.235 Y157.42
G1 X160.765 Y160.889 E.18641
G1 X160.622 Y161.033
G1 X160.622 Y160.469
G1 X160.765 Y160.326
G1 X164.235 Y156.856 E.18641
G1 X164.378 Y156.713
G1 X164.257 Y156.271
G1 X164.113 Y156.414
G1 X160.765 Y159.762 E.17989
G1 X160.622 Y159.905
G1 X160.622 Y159.342
G1 X160.765 Y159.199
G1 X163.55 Y156.414 E.14961
G1 X163.693 Y156.271
G1 X163.129 Y156.271
G1 X162.986 Y156.414
G1 X160.765 Y158.635 E.11933
G1 X160.622 Y158.778
G1 X160.622 Y158.215
G1 X160.765 Y158.072
G1 X162.423 Y156.414 E.08905
G1 X162.566 Y156.271
G1 X162.002 Y156.271
G1 X161.859 Y156.414
G1 X160.765 Y157.508 E.05877
G1 X160.622 Y157.651
G1 X160.622 Y157.088
G1 X160.765 Y156.944
G1 X161.296 Y156.414 E.02849
; WIPE_START
M204 S8000
G1 X160.765 Y156.944 E-.28499
G1 X160.622 Y157.088 E-.07695
G1 X160.622 Y157.651 E-.21415
G1 X160.765 Y157.508 E-.07695
G1 X160.964 Y157.309 E-.10697
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.007 Y161.868 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.519584
G1 F9613.742
M204 S8000
G1 X159.007 Y158.192 E.16403
M204 S10000
G1 X159.426 Y158.132 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.426 Y157.714 E.0147
G1 X158.589 Y157.714 E.02939
G1 X158.589 Y162.286 E.16063
G1 X159.426 Y162.286 E.02939
G1 X159.426 Y158.192 E.14382
M204 S10000
G1 X159.794 Y158.132 F60000
G1 F12212.001
M204 S8000
G1 X159.794 Y157.345 E.02764
G1 X158.22 Y157.345 E.05528
G1 X158.22 Y162.655 E.18652
G1 X159.794 Y162.655 E.05528
G1 X159.794 Y158.192 E.15677
M204 S10000
G1 X160.162 Y158.132 F60000
G1 F12212.001
M204 S8000
G1 X160.162 Y156.977 E.04059
G1 X157.852 Y156.977 E.08117
G1 X157.852 Y163.023 E.21241
G1 X160.162 Y163.023 E.08117
G1 X160.162 Y158.192 E.16972
; COOLING_NODE: 6
; WIPE_START
G1 X160.162 Y160.192 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X167.667 Y161.582 Z4.68 F60000
G1 X177.518 Y163.407 Z4.68
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X180.75 Y156.593 E.12277
G1 X180.75 Y163.407 E.25885
G1 X177.578 Y163.407 E.12049
; COOLING_NODE: 6
; WIPE_START
G1 X177.561 Y161.407 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X184.25 Y163.407 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X184.25 Y156.593 E.25885
G1 X187.482 Y156.593 E.12277
G1 X187.482 Y163.407 E.25885
G1 X184.31 Y163.407 E.12049
; COOLING_NODE: 6
; WIPE_START
M73 P77 R3
G1 X184.293 Y161.407 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.135 Y163.79 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X187.865 Y156.21 E.37697
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X177.195 Y163.79 E.37486
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.979 Y161.946 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.362444
G1 F14472.246
M204 S8000
G1 X179.29 Y161.946 E.00922
G1 X179.29 Y158.054 E.1154
G1 X178.979 Y158.054 E.00922
G1 X178.979 Y161.886 E.11362
M204 S10000
G1 X178.639 Y162.286 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X179.629 Y162.286 E.03479
G1 X179.629 Y157.714 E.16063
G1 X178.639 Y157.714 E.03479
G1 X178.639 Y162.226 E.15852
M204 S10000
G1 X178.27 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X179.998 Y162.655 E.06069
G1 X179.998 Y157.345 E.18652
G1 X178.27 Y157.345 E.06069
G1 X178.27 Y162.595 E.18441
M204 S10000
G1 X177.902 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X180.366 Y163.023 E.08658
G1 X180.366 Y156.977 E.21241
G1 X177.902 Y156.977 E.08658
G1 X177.902 Y162.963 E.2103
; WIPE_START
G1 X177.902 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X184.031 Y162.983 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X183.429 Y163.586 E.03237
G1 X183.285 Y163.729
G1 X182.722 Y163.729
G1 X182.865 Y163.586
G1 X184.031 Y162.42 E.06265
G1 X184.174 Y162.277
G1 X184.174 Y161.713
G1 X184.031 Y161.856
G1 X182.301 Y163.586 E.09292
G1 X182.158 Y163.729
G1 X181.595 Y163.729
G1 X181.738 Y163.586
G1 X184.031 Y161.293 E.1232
G1 X184.174 Y161.15
G1 X184.174 Y160.586
G1 X184.031 Y160.729
G1 X181.174 Y163.586 E.15348
G1 X181.031 Y163.729
G1 X180.826 Y163.371
G1 X180.969 Y163.228
G1 X184.031 Y160.166 E.16451
G1 X184.174 Y160.023
G1 X184.174 Y159.459
G1 X184.031 Y159.602
G1 X180.969 Y162.664 E.16451
G1 X180.826 Y162.807
G1 X180.826 Y162.244
G1 X180.969 Y162.1
G1 X184.031 Y159.039 E.16451
G1 X184.174 Y158.895
G1 X184.174 Y158.332
G1 X184.031 Y158.475
G1 X180.969 Y161.537 E.16451
G1 X180.826 Y161.68
G1 X180.826 Y161.117
G1 X180.969 Y160.973
G1 X184.031 Y157.912 E.16451
G1 X184.174 Y157.768
G1 X184.174 Y157.205
G1 X184.031 Y157.348
G1 X180.969 Y160.41 E.16451
G1 X180.826 Y160.553
G1 X180.826 Y159.989
G1 X180.969 Y159.846
G1 X184.031 Y156.784 E.16451
G1 X184.174 Y156.641
G1 X183.981 Y156.271
G1 X183.838 Y156.414
G1 X180.969 Y159.283 E.15412
G1 X180.826 Y159.426
G1 X180.826 Y158.862
G1 X180.969 Y158.719
G1 X183.274 Y156.414 E.12384
G1 X183.417 Y156.271
G1 X182.854 Y156.271
G1 X182.71 Y156.414
G1 X180.969 Y158.156 E.09357
G1 X180.826 Y158.299
G1 X180.826 Y157.735
G1 X180.969 Y157.592
G1 X182.147 Y156.414 E.06329
G1 X182.29 Y156.271
G1 X181.727 Y156.271
G1 X181.583 Y156.414
G1 X180.969 Y157.028 E.03301
; WIPE_START
M204 S8000
G1 X181.583 Y156.414 E-.33013
G1 X181.727 Y156.271 E-.07695
G1 X182.29 Y156.271 E-.21415
G1 X182.147 Y156.414 E-.07695
G1 X182.032 Y156.529 E-.06184
; WIPE_END
G1 E-.03999 F1800
M204 S10000
G1 X185.71 Y161.946 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.362454
G1 F14471.781
M204 S8000
G1 X186.021 Y161.946 E.00922
G1 X186.021 Y158.054 E.1154
G1 X185.71 Y158.054 E.00922
G1 X185.71 Y161.886 E.11362
M204 S10000
G1 X185.371 Y162.286 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X186.361 Y162.286 E.03479
G1 X186.361 Y157.714 E.16063
G1 X185.371 Y157.714 E.03479
G1 X185.371 Y162.226 E.15852
M204 S10000
G1 X185.002 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X186.73 Y162.655 E.06069
G1 X186.73 Y157.345 E.18652
G1 X185.002 Y157.345 E.06069
G1 X185.002 Y162.595 E.18441
M204 S10000
G1 X184.634 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.08658
G1 X187.098 Y156.977 E.21241
G1 X184.634 Y156.977 E.08658
G1 X184.634 Y162.963 E.2103
; CHANGE_LAYER
; Z_HEIGHT: 4.52
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12212.001
G1 X184.634 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 19/47
; update layer progress
M73 L19
M991 S0 P18 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z4.68 I1.214 J.087 P1  F60000
G1 X184.947 Y156.593 Z4.68
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.0963
G1 X187.482 Y163.407 E.25885
G1 X184.947 Y163.407 E.0963
G1 X184.947 Y156.653 E.25657
; COOLING_NODE: 6
; WIPE_START
G1 X186.946 Y156.606 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.392 Y156.21 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.15715
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X183.392 Y163.79 E.15715
G1 X183.392 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X185.392 Y156.243 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X184.728 Y157.15 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X183.992 Y156.414 E.03952
G1 X183.849 Y156.271
G1 X183.453 Y156.438
G1 X183.596 Y156.582
G1 X184.728 Y157.713 E.0608
G1 X184.871 Y157.856
G1 X184.871 Y158.42
G1 X184.728 Y158.277
G1 X183.596 Y157.145 E.0608
G1 X183.453 Y157.002
G1 X183.453 Y157.566
G1 X183.596 Y157.709
G1 X184.728 Y158.84 E.0608
G1 X184.871 Y158.983
G1 X184.871 Y159.547
G1 X184.728 Y159.404
G1 X183.596 Y158.272 E.0608
G1 X183.453 Y158.129
G1 X183.453 Y158.693
G1 X183.596 Y158.836
G1 X184.728 Y159.967 E.0608
G1 X184.871 Y160.111
G1 X184.871 Y160.674
G1 X184.728 Y160.531
G1 X183.596 Y159.399 E.0608
G1 X183.453 Y159.256
G1 X183.453 Y159.82
G1 X183.596 Y159.963
G1 X184.728 Y161.095 E.0608
G1 X184.871 Y161.238
G1 X184.871 Y161.801
G1 X184.728 Y161.658
G1 X183.596 Y160.527 E.0608
G1 X183.453 Y160.383
G1 X183.453 Y160.947
G1 X183.596 Y161.09
G1 X184.728 Y162.222 E.0608
G1 X184.871 Y162.365
G1 X184.871 Y162.928
G1 X184.728 Y162.785
G1 X183.596 Y161.654 E.0608
G1 X183.453 Y161.51
G1 X183.453 Y162.074
G1 X183.596 Y162.217
G1 X184.728 Y163.349 E.0608
G1 X184.871 Y163.492
G1 X184.544 Y163.729
G1 X184.401 Y163.586
G1 X183.596 Y162.781 E.04326
; WIPE_START
M204 S8000
G1 X184.401 Y163.586 E-.43266
G1 X184.544 Y163.729 E-.07695
G1 X184.871 Y163.492 E-.15332
G1 X184.728 Y163.349 E-.07695
G1 X184.69 Y163.311 E-.02014
; WIPE_END
G1 E-.03999 F1800
M204 S10000
G1 X185.33 Y163.023 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.0621
G1 X187.098 Y156.977 E.21241
G1 X185.33 Y156.977 E.0621
G1 X185.33 Y162.963 E.2103
M204 S10000
G1 X185.699 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X186.73 Y162.655 E.03621
G1 X186.73 Y157.345 E.18652
G1 X185.699 Y157.345 E.03621
G1 X185.699 Y162.595 E.18441
M204 S10000
G1 X186.049 Y162.305 F60000
; LINE_WIDTH: 0.382604
G1 F13591.061
M204 S8000
G1 X186.38 Y162.305 E.01045
G1 X186.38 Y157.695 E.14551
G1 X186.049 Y157.695 E.01045
G1 X186.049 Y162.245 E.14362
; COOLING_NODE: 6
; WIPE_START
G1 X186.049 Y160.245 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.892 Y162.897 Z4.92 F60000
G1 X177.518 Y163.407 Z4.92
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X180.053 Y156.593 E.0963
G1 X180.053 Y163.407 E.25885
G1 X177.578 Y163.407 E.09402
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X181.608 Y156.21 E.15715
G1 X181.608 Y163.79 E.2663
G1 X177.195 Y163.79 E.15504
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.902 Y163.023 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X179.67 Y163.023 E.0621
G1 X179.67 Y156.977 E.21241
G1 X177.902 Y156.977 E.0621
G1 X177.902 Y162.963 E.2103
M204 S10000
G1 X178.27 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X179.301 Y162.655 E.03621
G1 X179.301 Y157.345 E.18652
G1 X178.27 Y157.345 E.03621
G1 X178.27 Y162.595 E.18441
M204 S10000
G1 X178.62 Y162.305 F60000
; LINE_WIDTH: 0.382604
G1 F13591.061
M204 S8000
G1 X178.951 Y162.305 E.01045
G1 X178.951 Y157.695 E.14551
G1 X178.62 Y157.695 E.01045
G1 X178.62 Y162.245 E.14362
; WIPE_START
G1 X178.62 Y160.245 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X181.404 Y157.207 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X180.611 Y156.414 E.04262
G1 X180.468 Y156.271
G1 X180.129 Y156.496
G1 X180.272 Y156.639
G1 X181.404 Y157.771 E.0608
G1 X181.547 Y157.914
G1 X181.547 Y158.478
G1 X181.404 Y158.334
G1 X180.272 Y157.203 E.0608
G1 X180.129 Y157.06
G1 X180.129 Y157.623
G1 X180.272 Y157.766
G1 X181.404 Y158.898 E.0608
G1 X181.547 Y159.041
G1 X181.547 Y159.605
G1 X181.404 Y159.462
G1 X180.272 Y158.33 E.0608
G1 X180.129 Y158.187
G1 X180.129 Y158.75
G1 X180.272 Y158.894
G1 X181.404 Y160.025 E.0608
G1 X181.547 Y160.168
G1 X181.547 Y160.732
G1 X181.404 Y160.589
G1 X180.272 Y159.457 E.0608
G1 X180.129 Y159.314
G1 X180.129 Y159.877
G1 X180.272 Y160.021
G1 X181.404 Y161.152 E.0608
G1 X181.547 Y161.295
G1 X181.547 Y161.859
G1 X181.404 Y161.716
G1 X180.272 Y160.584 E.0608
G1 X180.129 Y160.441
G1 X180.129 Y161.005
G1 X180.272 Y161.148
G1 X181.404 Y162.279 E.0608
G1 X181.547 Y162.422
G1 X181.547 Y162.986
G1 X181.404 Y162.843
G1 X180.272 Y161.711 E.0608
G1 X180.129 Y161.568
G1 X180.129 Y162.132
G1 X180.272 Y162.275
G1 X181.404 Y163.406 E.0608
G1 X181.547 Y163.55
G1 X181.163 Y163.729
G1 X181.02 Y163.586
M73 P78 R3
G1 X180.272 Y162.838 E.04016
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X181.02 Y163.586 E-.40168
G1 X181.163 Y163.729 E-.07695
G1 X181.547 Y163.55 E-.16111
G1 X181.404 Y163.406 E-.07695
G1 X181.323 Y163.326 E-.04333
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.691 Y163.37 Z4.92 F60000
G1 X167.532 Y163.407 Z4.92
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.979 Y163.407 E.13496
G1 X163.979 Y156.593 E.25885
G1 X167.532 Y156.593 E.13496
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X163.596 Y163.79 E.15175
G1 X163.596 Y156.21 E.2663
G1 X167.915 Y156.21 E.15175
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.915 Y163.758 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.52 Y161.866 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.522964
G1 F9544.819
M204 S8000
G1 X165.991 Y161.866 E.02119
G1 X165.991 Y158.134 E.16776
G1 X165.52 Y158.134 E.02119
G1 X165.52 Y161.806 E.16506
M204 S10000
G1 X165.1 Y162.286 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.411 Y162.286 E.04607
G1 X166.411 Y157.714 E.16063
G1 X165.1 Y157.714 E.04607
G1 X165.1 Y162.226 E.15852
M204 S10000
G1 X164.731 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X166.78 Y162.655 E.07196
G1 X166.78 Y157.345 E.18652
G1 X164.731 Y157.345 E.07196
G1 X164.731 Y162.595 E.18441
M204 S10000
G1 X164.363 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.09786
G1 X167.148 Y156.977 E.21241
G1 X164.363 Y156.977 E.09786
G1 X164.363 Y162.963 E.2103
; COOLING_NODE: 3
; WIPE_START
G1 X164.363 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.021 Y156.593 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X161.021 Y163.407 E.25885
G1 X157.468 Y163.407 E.13496
G1 X157.468 Y156.593 E.25885
G1 X160.961 Y156.593 E.13268
; COOLING_NODE: 3
M204 S250
G1 X161.404 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X161.404 Y163.79 E.2663
G1 X157.085 Y163.79 E.15175
G1 X157.085 Y156.21 E.2663
G1 X161.344 Y156.21 E.14964
; WIPE_START
M204 S8000
G1 X161.36 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.48 Y158.37 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.522974
G1 F9544.616
M204 S8000
G1 X159.48 Y158.134 E.0106
G1 X159.009 Y158.134 E.02119
G1 X159.009 Y161.866 E.16776
G1 X159.48 Y161.866 E.02119
G1 X159.48 Y158.43 E.15447
M204 S10000
G1 X159.9 Y158.37 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.9 Y157.714 E.02304
G1 X158.589 Y157.714 E.04607
G1 X158.589 Y162.286 E.16063
G1 X159.9 Y162.286 E.04607
G1 X159.9 Y158.43 E.13548
M204 S10000
G1 X160.269 Y158.37 F60000
G1 F12212.001
M204 S8000
G1 X160.269 Y157.345 E.03598
G1 X158.22 Y157.345 E.07196
G1 X158.22 Y162.655 E.18652
G1 X160.269 Y162.655 E.07196
G1 X160.269 Y158.43 E.14843
M204 S10000
G1 X160.637 Y158.37 F60000
G1 F12212.001
M204 S8000
G1 X160.637 Y156.977 E.04893
G1 X157.852 Y156.977 E.09786
G1 X157.852 Y163.023 E.21241
G1 X160.637 Y163.023 E.09786
G1 X160.637 Y158.43 E.16137
; COOLING_NODE: 1
; WIPE_START
G1 X160.637 Y160.43 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X153.196 Y162.126 Z4.92 F60000
G1 X147.581 Y163.407 Z4.92
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X144.147 Y163.407 E.1305
G1 X144.147 Y156.593 E.25885
G1 X147.581 Y156.593 E.1305
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X143.763 Y163.79 E.14762
G1 X143.763 Y156.21 E.2663
G1 X147.965 Y156.21 E.14762
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.965 Y163.759 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.07 Y158.311 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.464224
G1 F10903.276
M204 S8000
G1 X146.07 Y158.105 E.00812
G1 X145.658 Y158.105 E.01624
G1 X145.658 Y161.895 E.14917
G1 X146.07 Y161.895 E.01624
G1 X146.07 Y158.371 E.13869
M204 S10000
G1 X146.461 Y158.311 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X146.461 Y157.714 E.02097
G1 X145.267 Y157.714 E.04195
G1 X145.267 Y162.286 E.16063
G1 X146.461 Y162.286 E.04195
G1 X146.461 Y158.371 E.13755
M204 S10000
G1 X146.83 Y158.311 F60000
G1 F12212.001
M204 S8000
G1 X146.83 Y157.345 E.03392
G1 X144.899 Y157.345 E.06784
G1 X144.899 Y162.655 E.18652
G1 X146.83 Y162.655 E.06784
G1 X146.83 Y158.371 E.15049
M204 S10000
G1 X147.198 Y158.311 F60000
G1 F12212.001
M204 S8000
G1 X147.198 Y156.977 E.04686
G1 X144.53 Y156.977 E.09373
G1 X144.53 Y163.023 E.21241
G1 X147.198 Y163.023 E.09373
G1 X147.198 Y158.371 E.16344
; COOLING_NODE: 1
; WIPE_START
G1 X147.198 Y160.371 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.853 Y163.407 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.1305
G1 X137.418 Y156.593 E.25885
G1 X140.853 Y156.593 E.1305
G1 X140.853 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X141.237 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.14762
G1 X137.035 Y156.21 E.2663
G1 X141.237 Y156.21 E.14762
G1 X141.237 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X139.237 Y163.759 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.342 Y158.311 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.464224
G1 F10903.276
M204 S8000
G1 X139.342 Y158.105 E.00812
G1 X138.93 Y158.105 E.01624
G1 X138.93 Y161.895 E.14917
G1 X139.342 Y161.895 E.01624
G1 X139.342 Y158.371 E.13869
M204 S10000
G1 X139.733 Y158.311 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X139.733 Y157.714 E.02097
G1 X138.539 Y157.714 E.04195
G1 X138.539 Y162.286 E.16063
G1 X139.733 Y162.286 E.04195
G1 X139.733 Y158.371 E.13755
M204 S10000
G1 X140.101 Y158.311 F60000
G1 F12212.001
M204 S8000
G1 X140.101 Y157.345 E.03392
G1 X138.17 Y157.345 E.06784
G1 X138.17 Y162.655 E.18652
G1 X140.101 Y162.655 E.06784
G1 X140.101 Y158.371 E.15049
M204 S10000
G1 X140.47 Y158.311 F60000
G1 F12212.001
M204 S8000
G1 X140.47 Y156.977 E.04686
G1 X137.802 Y156.977 E.09373
G1 X137.802 Y163.023 E.21241
G1 X140.47 Y163.023 E.09373
G1 X140.47 Y158.371 E.16344
; CHANGE_LAYER
; Z_HEIGHT: 4.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12212.001
G1 X140.47 Y160.371 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 20/47
; update layer progress
M73 L20
M991 S0 P19 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z4.92 I.104 J1.213 P1  F60000
G1 X184.472 Y156.593 Z4.92
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.11434
G1 X187.482 Y163.407 E.25885
G1 X184.472 Y163.407 E.11434
G1 X184.472 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X184.089 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.13268
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X184.089 Y163.79 E.13268
G1 X184.089 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X186.088 Y156.238 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.977 Y161.902 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.451564
G1 F11248.313
M204 S8000
G1 X185.977 Y158.158 E.14279
; WIPE_START
G1 X185.977 Y160.158 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.593 Y162.286 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X186.361 Y162.286 E.027
G1 X186.361 Y157.714 E.16063
G1 X185.593 Y157.714 E.027
G1 X185.593 Y162.226 E.15852
M204 S10000
G1 X185.224 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X186.73 Y162.655 E.05289
G1 X186.73 Y157.345 E.18652
G1 X185.224 Y157.345 E.05289
G1 X185.224 Y162.595 E.18441
M204 S10000
G1 X184.856 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.07878
G1 X187.098 Y156.977 E.21241
G1 X184.856 Y156.977 E.07878
G1 X184.856 Y162.963 E.2103
; COOLING_NODE: 6
; WIPE_START
G1 X184.856 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.614 Y163.375 Z5.16 F60000
G1 X177.518 Y163.407 Z5.16
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X180.528 Y156.593 E.11434
G1 X180.528 Y163.407 E.25885
G1 X177.578 Y163.407 E.11206
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
M73 P78 R2
G1 X177.135 Y156.21 E.2663
G1 X180.911 Y156.21 E.13268
G1 X180.911 Y163.79 E.2663
G1 X177.195 Y163.79 E.13057
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.023 Y161.902 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.451564
G1 F11248.313
M204 S8000
G1 X179.023 Y158.158 E.14279
; WIPE_START
G1 X179.023 Y160.158 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.639 Y162.286 Z5.16 F60000
M73 P79 R2
G1 Z4.76
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X179.408 Y162.286 E.027
G1 X179.408 Y157.714 E.16063
G1 X178.639 Y157.714 E.027
G1 X178.639 Y162.226 E.15852
M204 S10000
G1 X178.27 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X179.776 Y162.655 E.05289
G1 X179.776 Y157.345 E.18652
G1 X178.27 Y157.345 E.05289
G1 X178.27 Y162.595 E.18441
M204 S10000
G1 X177.902 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X180.145 Y163.023 E.07878
G1 X180.145 Y156.977 E.21241
G1 X177.902 Y156.977 E.07878
G1 X177.902 Y162.963 E.2103
; COOLING_NODE: 3
; WIPE_START
G1 X177.902 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.473 Y162.713 Z5.16 F60000
G1 X167.532 Y163.407 Z5.16
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X164.582 Y163.407 E.11207
G1 X164.582 Y156.593 E.25885
G1 X167.532 Y156.593 E.11207
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X164.198 Y163.79 E.13058
G1 X164.198 Y156.21 E.2663
G1 X167.915 Y156.21 E.13058
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.915 Y163.762 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.057 Y161.932 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.391764
G1 F13225.182
M204 S8000
G1 X166.057 Y158.128 E.12338
; WIPE_START
G1 X166.057 Y160.128 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.702 Y162.286 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.411 Y162.286 E.0249
G1 X166.411 Y157.714 E.16063
G1 X165.702 Y157.714 E.0249
G1 X165.702 Y162.226 E.15852
M204 S10000
G1 X165.334 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X166.78 Y162.655 E.05079
G1 X166.78 Y157.345 E.18652
G1 X165.334 Y157.345 E.05079
G1 X165.334 Y162.595 E.18441
M204 S10000
G1 X164.965 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.07668
G1 X167.148 Y156.977 E.21241
G1 X164.965 Y156.977 E.07668
G1 X164.965 Y162.963 E.2103
; COOLING_NODE: 3
; WIPE_START
G1 X164.965 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.418 Y156.593 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.418 Y163.407 E.25885
G1 X157.468 Y163.407 E.11207
G1 X157.468 Y156.593 E.25885
G1 X160.358 Y156.593 E.10979
; COOLING_NODE: 3
M204 S250
G1 X160.802 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X160.802 Y163.79 E.2663
G1 X157.085 Y163.79 E.13058
G1 X157.085 Y156.21 E.2663
G1 X160.742 Y156.21 E.12847
; WIPE_START
M204 S8000
G1 X160.758 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.943 Y161.932 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.391784
G1 F13224.405
M204 S8000
G1 X158.943 Y158.128 E.12339
M204 S10000
G1 X159.298 Y158.068 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.298 Y157.714 E.01245
G1 X158.589 Y157.714 E.0249
G1 X158.589 Y162.286 E.16063
G1 X159.298 Y162.286 E.0249
G1 X159.298 Y158.128 E.14607
M204 S10000
G1 X159.666 Y158.068 F60000
G1 F12212.001
M204 S8000
G1 X159.666 Y157.345 E.0254
G1 X158.22 Y157.345 E.05079
G1 X158.22 Y162.655 E.18652
G1 X159.666 Y162.655 E.05079
G1 X159.666 Y158.128 E.15902
M204 S10000
G1 X160.035 Y158.068 F60000
G1 F12212.001
M204 S8000
G1 X160.035 Y156.977 E.03834
G1 X157.852 Y156.977 E.07668
G1 X157.852 Y163.023 E.21241
G1 X160.035 Y163.023 E.07668
G1 X160.035 Y158.128 E.17196
; COOLING_NODE: 1
; WIPE_START
G1 X160.035 Y160.128 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X152.654 Y162.071 Z5.16 F60000
G1 X147.581 Y163.407 Z5.16
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X144.688 Y163.407 E.10994
G1 X144.688 Y156.593 E.25885
G1 X147.581 Y156.593 E.10994
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X144.304 Y163.79 E.12861
G1 X144.304 Y156.21 E.2663
G1 X147.965 Y156.21 E.12861
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.965 Y163.763 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.39 Y158.04 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.562194
G1 F8811.609
M204 S8000
G1 X146.39 Y157.785 E.01243
G1 X145.879 Y157.785 E.02487
G1 X145.879 Y162.215 E.21569
G1 X146.39 Y162.215 E.02487
G1 X146.39 Y158.1 E.20034
M204 S10000
G1 X146.83 Y158.04 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X146.83 Y157.345 E.02441
G1 X145.44 Y157.345 E.04883
G1 X145.44 Y162.655 E.18652
G1 X146.83 Y162.655 E.04883
G1 X146.83 Y158.1 E.16
M204 S10000
G1 X147.198 Y158.04 F60000
G1 F12212.001
M204 S8000
G1 X147.198 Y156.977 E.03736
G1 X145.071 Y156.977 E.07472
G1 X145.071 Y163.023 E.21241
G1 X147.198 Y163.023 E.07472
G1 X147.198 Y158.1 E.17294
; COOLING_NODE: 1
; WIPE_START
G1 X147.198 Y160.1 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.318 Y163.404 Z5.16 F60000
G1 X140.312 Y163.407 Z5.16
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.10994
G1 X137.418 Y156.593 E.25885
G1 X140.312 Y156.593 E.10994
G1 X140.312 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X140.696 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.12861
G1 X137.035 Y156.21 E.2663
G1 X140.696 Y156.21 E.12861
G1 X140.696 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X138.696 Y163.763 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.121 Y158.04 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.562204
G1 F8811.436
M204 S8000
G1 X139.121 Y157.785 E.01243
G1 X138.61 Y157.785 E.02487
G1 X138.61 Y162.215 E.21569
G1 X139.121 Y162.215 E.02487
G1 X139.121 Y158.1 E.20034
M204 S10000
G1 X139.56 Y158.04 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X139.56 Y157.345 E.02441
G1 X138.17 Y157.345 E.04883
G1 X138.17 Y162.655 E.18652
G1 X139.56 Y162.655 E.04883
G1 X139.56 Y158.1 E.16
M204 S10000
G1 X139.929 Y158.04 F60000
G1 F12212.001
M204 S8000
G1 X139.929 Y156.977 E.03736
G1 X137.802 Y156.977 E.07472
G1 X137.802 Y163.023 E.21241
G1 X139.929 Y163.023 E.07472
G1 X139.929 Y158.1 E.17294
; CHANGE_LAYER
; Z_HEIGHT: 5
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12212.001
G1 X139.929 Y160.1 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 21/47
; update layer progress
M73 L21
M991 S0 P20 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z5.16 I.095 J1.213 P1  F60000
G1 X184.886 Y156.593 Z5.16
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.09859
G1 X187.482 Y163.407 E.25885
G1 X184.886 Y163.407 E.09859
G1 X184.886 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X184.503 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.11812
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X184.503 Y163.79 E.11812
G1 X184.503 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X186.503 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.27 Y163.023 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.06422
G1 X187.098 Y156.977 E.21241
G1 X185.27 Y156.977 E.06422
G1 X185.27 Y162.963 E.2103
M204 S10000
G1 X185.638 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X186.73 Y162.655 E.03833
G1 X186.73 Y157.345 E.18652
G1 X185.638 Y157.345 E.03833
G1 X185.638 Y162.595 E.18441
M204 S10000
G1 X186.003 Y162.29 F60000
; LINE_WIDTH: 0.412804
G1 F12455.024
M204 S8000
G1 X186.365 Y162.29 E.01245
G1 X186.365 Y157.71 E.15774
G1 X186.003 Y157.71 E.01245
G1 X186.003 Y162.23 E.15568
; COOLING_NODE: 6
; WIPE_START
G1 X186.003 Y160.23 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.855 Y162.906 Z5.4 F60000
G1 X177.518 Y163.407 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X180.114 Y156.593 E.09859
G1 X180.114 Y163.407 E.25885
G1 X177.578 Y163.407 E.09631
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X180.497 Y156.21 E.11812
G1 X180.497 Y163.79 E.2663
G1 X177.195 Y163.79 E.11601
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.902 Y163.023 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X179.73 Y163.023 E.06422
G1 X179.73 Y156.977 E.21241
G1 X177.902 Y156.977 E.06422
G1 X177.902 Y162.963 E.2103
M204 S10000
G1 X178.27 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X179.362 Y162.655 E.03833
G1 X179.362 Y157.345 E.18652
G1 X178.27 Y157.345 E.03833
G1 X178.27 Y162.595 E.18441
M204 S10000
G1 X178.635 Y162.29 F60000
; LINE_WIDTH: 0.412804
M73 P80 R2
G1 F12455.024
M204 S8000
G1 X178.997 Y162.29 E.01245
G1 X178.997 Y157.71 E.15774
G1 X178.635 Y157.71 E.01245
G1 X178.635 Y162.23 E.15568
; COOLING_NODE: 3
; WIPE_START
G1 X178.635 Y160.23 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.297 Y162.329 Z5.4 F60000
G1 X167.532 Y163.407 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X164.972 Y163.407 E.09723
G1 X164.972 Y156.593 E.25885
G1 X167.532 Y156.593 E.09723
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X164.589 Y163.79 E.11686
G1 X164.589 Y156.21 E.2663
G1 X167.915 Y156.21 E.11686
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.915 Y163.766 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.356 Y163.023 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.06297
G1 X167.148 Y156.977 E.21241
G1 X165.356 Y156.977 E.06297
G1 X165.356 Y162.963 E.2103
M204 S10000
G1 X165.724 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X166.78 Y162.655 E.03707
G1 X166.78 Y157.345 E.18652
G1 X165.724 Y157.345 E.03707
G1 X165.724 Y162.595 E.18441
M204 S10000
G1 X166.08 Y162.299 F60000
; LINE_WIDTH: 0.394904
G1 F13104.252
M204 S8000
G1 X166.424 Y162.299 E.01124
G1 X166.424 Y157.701 E.15051
G1 X166.08 Y157.701 E.01124
G1 X166.08 Y162.239 E.14855
; COOLING_NODE: 3
; WIPE_START
G1 X166.08 Y160.239 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.028 Y156.593 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.028 Y163.407 E.25885
G1 X157.468 Y163.407 E.09723
G1 X157.468 Y156.593 E.25885
G1 X159.968 Y156.593 E.09495
; COOLING_NODE: 3
M204 S250
G1 X160.411 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X160.411 Y163.79 E.2663
G1 X157.085 Y163.79 E.11686
G1 X157.085 Y156.21 E.2663
G1 X160.351 Y156.21 E.11475
; WIPE_START
M204 S8000
G1 X160.367 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.644 Y157.873 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.644 Y156.977 E.03148
G1 X157.852 Y156.977 E.06297
G1 X157.852 Y163.023 E.21241
G1 X159.644 Y163.023 E.06297
G1 X159.644 Y157.933 E.17882
M204 S10000
G1 X159.276 Y157.873 F60000
G1 F12212.001
M204 S8000
G1 X159.276 Y157.345 E.01854
G1 X158.22 Y157.345 E.03708
G1 X158.22 Y162.655 E.18652
G1 X159.276 Y162.655 E.03708
G1 X159.276 Y157.933 E.16587
M204 S10000
G1 X158.92 Y157.873 F60000
; LINE_WIDTH: 0.394914
G1 F13103.872
M204 S8000
G1 X158.92 Y157.701 E.00562
G1 X158.576 Y157.701 E.01124
G1 X158.576 Y162.299 E.15052
G1 X158.92 Y162.299 E.01124
G1 X158.92 Y157.933 E.14293
; COOLING_NODE: 1
; WIPE_START
G1 X158.92 Y159.933 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.622 Y162.169 Z5.4 F60000
G1 X147.581 Y163.407 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.058 Y163.407 E.09587
G1 X145.058 Y156.593 E.25885
G1 X147.581 Y156.593 E.09587
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X144.675 Y163.79 E.1156
G1 X144.675 Y156.21 E.2663
G1 X147.965 Y156.21 E.1156
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.965 Y163.766 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.198 Y157.855 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X147.198 Y156.977 E.03085
G1 X145.442 Y156.977 E.06171
G1 X145.442 Y163.023 E.21241
G1 X147.198 Y163.023 E.06171
G1 X147.198 Y157.915 E.17945
M204 S10000
G1 X146.83 Y157.855 F60000
G1 F12212.001
M204 S8000
G1 X146.83 Y157.345 E.01791
G1 X145.81 Y157.345 E.03582
G1 X145.81 Y162.655 E.18652
G1 X146.83 Y162.655 E.03582
G1 X146.83 Y157.915 E.1665
M204 S10000
G1 X146.483 Y157.855 F60000
; LINE_WIDTH: 0.377014
G1 F13824.461
M204 S8000
G1 X146.483 Y157.692 E.00505
G1 X146.157 Y157.692 E.0101
G1 X146.157 Y162.308 E.14323
G1 X146.483 Y162.308 E.0101
G1 X146.483 Y157.915 E.13631
; COOLING_NODE: 1
; WIPE_START
G1 X146.483 Y159.915 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.942 Y163.407 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.09587
G1 X137.418 Y156.593 E.25885
G1 X139.942 Y156.593 E.09587
G1 X139.942 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X140.325 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.1156
G1 X137.035 Y156.21 E.2663
G1 X140.325 Y156.21 E.1156
G1 X140.325 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X138.326 Y163.766 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.558 Y157.855 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X139.558 Y156.977 E.03085
G1 X137.802 Y156.977 E.06171
G1 X137.802 Y163.023 E.21241
G1 X139.558 Y163.023 E.06171
G1 X139.558 Y157.915 E.17945
M204 S10000
G1 X139.19 Y157.855 F60000
G1 F12212.001
M204 S8000
G1 X139.19 Y157.345 E.01791
G1 X138.17 Y157.345 E.03582
G1 X138.17 Y162.655 E.18652
G1 X139.19 Y162.655 E.03582
G1 X139.19 Y157.915 E.1665
M204 S10000
G1 X138.843 Y157.855 F60000
; LINE_WIDTH: 0.377004
G1 F13824.886
M204 S8000
G1 X138.843 Y157.692 E.00505
G1 X138.517 Y157.692 E.0101
G1 X138.517 Y162.308 E.14322
G1 X138.843 Y162.308 E.0101
G1 X138.843 Y157.915 E.13631
; CHANGE_LAYER
; Z_HEIGHT: 5.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13824.886
G1 X138.843 Y159.915 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 22/47
; update layer progress
M73 L22
M991 S0 P21 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z5.4 I.087 J1.214 P1  F60000
G1 X185.193 Y156.593 Z5.4
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.08693
G1 X187.482 Y163.407 E.25885
G1 X185.193 Y163.407 E.08693
G1 X185.193 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X184.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.10733
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X184.81 Y163.79 E.10733
G1 X184.81 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X186.81 Y156.231 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.338 Y162.263 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.467084
G1 F10828.242
M204 S8000
G1 X186.338 Y157.797 E.17691
; WIPE_START
G1 X186.338 Y159.797 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.945 Y162.655 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X186.73 Y162.655 E.02755
G1 X186.73 Y157.345 E.18652
G1 X185.945 Y157.345 E.02755
G1 X185.945 Y162.595 E.18441
M204 S10000
G1 X185.577 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.05344
G1 X187.098 Y156.977 E.21241
G1 X185.577 Y156.977 E.05344
G1 X185.577 Y162.963 E.2103
; COOLING_NODE: 6
; WIPE_START
G1 X185.577 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.273 Y163.178 Z5.64 F60000
G1 X177.518 Y163.407 Z5.64
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X179.807 Y156.593 E.08693
G1 X179.807 Y163.407 E.25885
G1 X177.578 Y163.407 E.08465
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X180.19 Y156.21 E.10733
G1 X180.19 Y163.79 E.2663
G1 X177.195 Y163.79 E.10522
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.663 Y162.263 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.467084
G1 F10828.242
M204 S8000
G1 X178.663 Y157.797 E.17691
; WIPE_START
G1 X178.663 Y159.797 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.27 Y162.655 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X179.055 Y162.655 E.02755
G1 X179.055 Y157.345 E.18652
G1 X178.27 Y157.345 E.02755
G1 X178.27 Y162.595 E.18441
M204 S10000
G1 X177.902 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X179.423 Y163.023 E.05344
G1 X179.423 Y156.977 E.21241
G1 X177.902 Y156.977 E.05344
G1 X177.902 Y162.963 E.2103
; COOLING_NODE: 3
; WIPE_START
G1 X177.902 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.473 Y162.713 Z5.64 F60000
G1 X167.532 Y163.407 Z5.64
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.269 Y163.407 E.08595
G1 X165.269 Y156.593 E.25885
G1 X167.532 Y156.593 E.08595
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X164.886 Y163.79 E.10643
G1 X164.886 Y156.21 E.2663
G1 X167.915 Y156.21 E.10643
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
M73 P81 R2
G1 X165.915 Y163.77 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.4 Y162.275 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.441384
G1 F11542.014
M204 S8000
G1 X166.4 Y157.785 E.16693
; WIPE_START
G1 X166.4 Y159.785 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.021 Y162.655 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.78 Y162.655 E.02664
G1 X166.78 Y157.345 E.18652
G1 X166.021 Y157.345 E.02664
G1 X166.021 Y162.595 E.18441
M204 S10000
G1 X165.653 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.05253
G1 X167.148 Y156.977 E.21241
G1 X165.653 Y156.977 E.05253
G1 X165.653 Y162.963 E.2103
; COOLING_NODE: 3
; WIPE_START
G1 X165.653 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.731 Y156.593 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.731 Y163.407 E.25885
G1 X157.468 Y163.407 E.08595
G1 X157.468 Y156.593 E.25885
G1 X159.671 Y156.593 E.08367
; COOLING_NODE: 3
M204 S250
G1 X160.114 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X160.114 Y163.79 E.2663
G1 X157.085 Y163.79 E.10643
G1 X157.085 Y156.21 E.2663
G1 X160.054 Y156.21 E.10432
; WIPE_START
M204 S8000
G1 X160.07 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.6 Y162.275 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.441404
G1 F11541.421
M204 S8000
G1 X158.6 Y157.785 E.16693
M204 S10000
G1 X158.979 Y157.725 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X158.979 Y157.345 E.01332
G1 X158.22 Y157.345 E.02664
G1 X158.22 Y162.655 E.18652
G1 X158.979 Y162.655 E.02664
G1 X158.979 Y157.785 E.17109
M204 S10000
G1 X159.347 Y157.725 F60000
G1 F12212.001
M204 S8000
G1 X159.347 Y156.977 E.02627
G1 X157.852 Y156.977 E.05254
G1 X157.852 Y163.023 E.21241
G1 X159.347 Y163.023 E.05254
G1 X159.347 Y157.785 E.18404
; COOLING_NODE: 1
; WIPE_START
G1 X159.347 Y159.785 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X152.053 Y162.03 Z5.64 F60000
G1 X147.581 Y163.407 Z5.64
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.342 Y163.407 E.08508
G1 X145.342 Y156.593 E.25885
G1 X147.581 Y156.593 E.08508
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X144.959 Y163.79 E.10562
G1 X144.959 Y156.21 E.2663
G1 X147.965 Y156.21 E.10562
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.965 Y163.77 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.462 Y162.287 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.418384
G1 F12265.591
M204 S8000
G1 X146.462 Y157.773 E.15788
M204 S10000
G1 X146.83 Y157.713 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X146.83 Y157.345 E.01292
G1 X146.094 Y157.345 E.02583
G1 X146.094 Y162.655 E.18652
G1 X146.83 Y162.655 E.02583
G1 X146.83 Y157.773 E.17149
M204 S10000
G1 X147.198 Y157.713 F60000
G1 F12212.001
M204 S8000
G1 X147.198 Y156.977 E.02586
G1 X145.726 Y156.977 E.05173
G1 X145.726 Y163.023 E.21241
G1 X147.198 Y163.023 E.05173
G1 X147.198 Y157.773 E.18444
; COOLING_NODE: 1
; WIPE_START
G1 X147.198 Y159.773 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.322 Y163.086 Z5.64 F60000
G1 X139.658 Y163.407 Z5.64
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.08508
G1 X137.418 Y156.593 E.25885
G1 X139.658 Y156.593 E.08508
G1 X139.658 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X140.041 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.10562
G1 X137.035 Y156.21 E.2663
G1 X140.041 Y156.21 E.10562
G1 X140.041 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X138.042 Y163.77 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.538 Y162.287 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.418384
G1 F12265.591
M204 S8000
G1 X138.538 Y157.773 E.15788
M204 S10000
G1 X138.906 Y157.713 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X138.906 Y157.345 E.01292
G1 X138.17 Y157.345 E.02583
G1 X138.17 Y162.655 E.18652
G1 X138.906 Y162.655 E.02583
G1 X138.906 Y157.773 E.17149
M204 S10000
G1 X139.274 Y157.713 F60000
G1 F12212.001
M204 S8000
G1 X139.274 Y156.977 E.02586
G1 X137.802 Y156.977 E.05173
G1 X137.802 Y163.023 E.21241
G1 X139.274 Y163.023 E.05173
G1 X139.274 Y157.773 E.18444
; CHANGE_LAYER
; Z_HEIGHT: 5.48
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12212.001
G1 X139.274 Y159.773 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 23/47
; update layer progress
M73 L23
M991 S0 P22 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z5.64 I.084 J1.214 P1  F60000
G1 X185.438 Y156.593 Z5.64
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.07765
G1 X187.482 Y163.407 E.25885
G1 X185.438 Y163.407 E.07765
G1 X185.438 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.054 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.09875
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.054 Y163.79 E.09875
G1 X185.054 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.054 Y156.227 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.821 Y163.023 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.04485
G1 X187.098 Y156.977 E.21241
G1 X185.821 Y156.977 E.04485
G1 X185.821 Y162.963 E.2103
M204 S10000
G1 X186.233 Y162.612 F60000
; LINE_WIDTH: 0.505624
G1 F9909.276
M204 S8000
G1 X186.687 Y162.612 E.01966
G1 X186.687 Y157.388 E.22615
G1 X186.233 Y157.388 E.01966
G1 X186.233 Y162.552 E.22356
; COOLING_NODE: 6
; WIPE_START
G1 X186.233 Y160.552 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.979 Y162.928 Z5.88 F60000
G1 X177.518 Y163.407 Z5.88
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X179.562 Y156.593 E.07765
G1 X179.562 Y163.407 E.25885
G1 X177.578 Y163.407 E.07537
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.946 Y156.21 E.09875
G1 X179.946 Y163.79 E.2663
G1 X177.195 Y163.79 E.09664
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.902 Y163.023 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X179.179 Y163.023 E.04485
G1 X179.179 Y156.977 E.21241
G1 X177.902 Y156.977 E.04485
G1 X177.902 Y162.963 E.2103
M204 S10000
G1 X178.313 Y162.612 F60000
; LINE_WIDTH: 0.505624
G1 F9909.276
M204 S8000
G1 X178.767 Y162.612 E.01966
G1 X178.767 Y157.388 E.22615
G1 X178.313 Y157.388 E.01966
G1 X178.313 Y162.552 E.22356
; COOLING_NODE: 3
; WIPE_START
G1 X178.313 Y160.552 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.935 Y162.505 Z5.88 F60000
G1 X167.532 Y163.407 Z5.88
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.506 Y163.407 E.07695
G1 X165.506 Y156.593 E.25885
G1 X167.532 Y156.593 E.07695
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.123 Y163.79 E.0981
G1 X165.123 Y156.21 E.2663
G1 X167.915 Y156.21 E.0981
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.915 Y163.773 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.89 Y163.023 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.04421
G1 X167.148 Y156.977 E.21241
G1 X165.89 Y156.977 E.04421
G1 X165.89 Y162.963 E.2103
M204 S10000
G1 X166.296 Y162.616 F60000
; LINE_WIDTH: 0.496474
G1 F10113.042
M204 S8000
G1 X166.741 Y162.616 E.01888
G1 X166.741 Y157.384 E.22199
G1 X166.296 Y157.384 E.01888
G1 X166.296 Y162.556 E.21944
; COOLING_NODE: 3
; WIPE_START
G1 X166.296 Y160.556 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.701 Y156.714 Z5.88 F60000
G1 X159.494 Y156.593 Z5.88
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.494 Y163.407 E.25885
G1 X157.468 Y163.407 E.07695
G1 X157.468 Y156.593 E.25885
G1 X159.434 Y156.593 E.07467
; COOLING_NODE: 3
M204 S250
G1 X159.877 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.877 Y163.79 E.2663
G1 X157.085 Y163.79 E.0981
G1 X157.085 Y156.21 E.2663
G1 X159.817 Y156.21 E.096
; WIPE_START
M204 S8000
G1 X159.833 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.11 Y157.606 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.11 Y156.977 E.02211
M73 P82 R2
G1 X157.852 Y156.977 E.04421
G1 X157.852 Y163.023 E.21241
G1 X159.11 Y163.023 E.04421
G1 X159.11 Y157.666 E.1882
M204 S10000
G1 X158.704 Y157.606 F60000
; LINE_WIDTH: 0.496474
G1 F10113.042
M204 S8000
G1 X158.704 Y157.384 E.00944
G1 X158.259 Y157.384 E.01888
G1 X158.259 Y162.616 E.22199
G1 X158.704 Y162.616 E.01888
G1 X158.704 Y157.666 E.21
; COOLING_NODE: 1
; WIPE_START
G1 X158.704 Y159.666 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.469 Y162.099 Z5.88 F60000
G1 X147.581 Y163.407 Z5.88
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.572 Y163.407 E.07636
G1 X145.572 Y156.593 E.25885
G1 X147.581 Y156.593 E.07636
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.188 Y163.79 E.09756
G1 X145.188 Y156.21 E.2663
G1 X147.965 Y156.21 E.09756
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.965 Y163.773 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.198 Y157.598 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X147.198 Y156.977 E.02183
G1 X145.955 Y156.977 E.04367
G1 X145.955 Y163.023 E.21241
G1 X147.198 Y163.023 E.04367
G1 X147.198 Y157.658 E.18847
M204 S10000
G1 X146.795 Y157.598 F60000
; LINE_WIDTH: 0.488734
G1 F10292.067
M204 S8000
G1 X146.795 Y157.38 E.00911
G1 X146.358 Y157.38 E.01823
G1 X146.358 Y162.62 E.21845
G1 X146.795 Y162.62 E.01823
G1 X146.795 Y157.658 E.20683
; COOLING_NODE: 1
; WIPE_START
G1 X146.795 Y159.658 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.993 Y163.119 Z5.88 F60000
G1 X139.428 Y163.407 Z5.88
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.07636
G1 X137.418 Y156.593 E.25885
G1 X139.428 Y156.593 E.07636
G1 X139.428 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.812 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.09756
G1 X137.035 Y156.21 E.2663
G1 X139.812 Y156.21 E.09756
G1 X139.812 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.812 Y163.773 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.045 Y157.598 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X139.045 Y156.977 E.02183
G1 X137.802 Y156.977 E.04367
G1 X137.802 Y163.023 E.21241
G1 X139.045 Y163.023 E.04367
G1 X139.045 Y157.658 E.18847
M204 S10000
G1 X138.642 Y157.598 F60000
; LINE_WIDTH: 0.488734
G1 F10292.067
M204 S8000
G1 X138.642 Y157.38 E.00911
G1 X138.205 Y157.38 E.01823
G1 X138.205 Y162.62 E.21845
G1 X138.642 Y162.62 E.01823
G1 X138.642 Y157.658 E.20683
; CHANGE_LAYER
; Z_HEIGHT: 5.72
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10292.067
G1 X138.642 Y159.658 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 24/47
; update layer progress
M73 L24
M991 S0 P23 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z5.88 I.079 J1.214 P1  F60000
G1 X185.636 Y156.593 Z5.88
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.07011
G1 X187.482 Y163.407 E.25885
G1 X185.636 Y163.407 E.07011
G1 X185.636 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.253 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.09178
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.253 Y163.79 E.09178
G1 X185.253 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.252 Y156.224 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.02 Y163.023 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.03789
G1 X187.098 Y156.977 E.21241
G1 X186.02 Y156.977 E.03789
G1 X186.02 Y162.963 E.2103
M204 S10000
G1 X186.381 Y162.661 F60000
; LINE_WIDTH: 0.406444
G1 F12678.2
M204 S8000
G1 X186.736 Y162.661 E.01201
G1 X186.736 Y157.339 E.18012
G1 X186.381 Y157.339 E.01201
G1 X186.381 Y162.601 E.17809
; COOLING_NODE: 6
; WIPE_START
G1 X186.381 Y160.601 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.105 Y162.904 Z6.12 F60000
G1 X177.518 Y163.407 Z6.12
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X179.364 Y156.593 E.07011
G1 X179.364 Y163.407 E.25885
G1 X177.578 Y163.407 E.06783
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.747 Y156.21 E.09178
G1 X179.747 Y163.79 E.2663
G1 X177.195 Y163.79 E.08967
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.902 Y163.023 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X178.98 Y163.023 E.03789
G1 X178.98 Y156.977 E.21241
G1 X177.902 Y156.977 E.03789
G1 X177.902 Y162.963 E.2103
M204 S10000
G1 X178.264 Y162.661 F60000
; LINE_WIDTH: 0.406454
G1 F12677.843
M204 S8000
G1 X178.619 Y162.661 E.01201
G1 X178.619 Y157.339 E.18012
G1 X178.264 Y157.339 E.01201
G1 X178.264 Y162.601 E.17809
; COOLING_NODE: 3
; WIPE_START
G1 X178.264 Y160.601 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.879 Y162.531 Z6.12 F60000
G1 X167.532 Y163.407 Z6.12
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.699 Y163.407 E.06962
G1 X165.699 Y156.593 E.25885
G1 X167.532 Y156.593 E.06962
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.315 Y163.79 E.09133
G1 X165.315 Y156.21 E.2663
G1 X167.915 Y156.21 E.09133
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.916 Y163.776 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.082 Y163.023 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.03744
G1 X167.148 Y156.977 E.21241
G1 X166.082 Y156.977 E.03744
G1 X166.082 Y162.963 E.2103
M204 S10000
G1 X166.441 Y162.665 F60000
; LINE_WIDTH: 0.400044
G1 F12911.002
M204 S8000
G1 X166.79 Y162.665 E.01158
G1 X166.79 Y157.335 E.17708
G1 X166.441 Y157.335 E.01158
G1 X166.441 Y162.605 E.17509
; COOLING_NODE: 3
; WIPE_START
G1 X166.441 Y160.605 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.787 Y156.866 Z6.12 F60000
G1 X159.301 Y156.593 Z6.12
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.301 Y163.407 E.25885
G1 X157.468 Y163.407 E.06962
G1 X157.468 Y156.593 E.25885
G1 X159.241 Y156.593 E.06734
; COOLING_NODE: 3
M204 S250
G1 X159.685 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.685 Y163.79 E.2663
G1 X157.085 Y163.79 E.09133
G1 X157.085 Y156.21 E.2663
G1 X159.625 Y156.21 E.08922
; WIPE_START
M204 S8000
G1 X159.64 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.918 Y157.51 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X158.918 Y156.977 E.01872
G1 X157.852 Y156.977 E.03744
G1 X157.852 Y163.023 E.21241
G1 X158.918 Y163.023 E.03744
G1 X158.918 Y157.57 E.19159
M204 S10000
G1 X158.559 Y157.51 F60000
; LINE_WIDTH: 0.400054
G1 F12910.63
M204 S8000
G1 X158.559 Y157.335 E.00579
G1 X158.21 Y157.335 E.01158
G1 X158.21 Y162.665 E.17709
G1 X158.559 Y162.665 E.01158
G1 X158.559 Y157.57 E.1693
; COOLING_NODE: 1
; WIPE_START
G1 X158.559 Y159.57 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.354 Y162.088 Z6.12 F60000
G1 X147.581 Y163.407 Z6.12
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.76 Y163.407 E.06919
G1 X145.76 Y156.593 E.25885
G1 X147.581 Y156.593 E.06919
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.377 Y163.79 E.09092
G1 X145.377 Y156.21 E.2663
G1 X147.965 Y156.21 E.09092
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.966 Y163.776 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.198 Y157.504 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X147.198 Y156.977 E.01852
G1 X146.144 Y156.977 E.03703
G1 X146.144 Y163.023 E.21241
G1 X147.198 Y163.023 E.03703
G1 X147.198 Y157.564 E.19179
M204 S10000
G1 X146.842 Y157.504 F60000
; LINE_WIDTH: 0.394304
G1 F13127.189
M204 S8000
G1 X146.842 Y157.333 E.0056
G1 X146.5 Y157.333 E.0112
G1 X146.5 Y162.667 E.17435
G1 X146.842 Y162.667 E.0112
G1 X146.842 Y157.564 E.16679
; COOLING_NODE: 1
; WIPE_START
G1 X146.842 Y159.564 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.03 Y163.007 Z6.12 F60000
G1 X139.24 Y163.407 Z6.12
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.06919
G1 X137.418 Y156.593 E.25885
G1 X139.24 Y156.593 E.06919
G1 X139.24 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.623 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.09092
G1 X137.035 Y156.21 E.2663
G1 X139.623 Y156.21 E.09092
G1 X139.623 Y163.73 E.2642
; WIPE_START
M204 S8000
M73 P83 R2
G1 X137.624 Y163.776 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.856 Y157.504 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X138.856 Y156.977 E.01852
G1 X137.802 Y156.977 E.03703
G1 X137.802 Y163.023 E.21241
G1 X138.856 Y163.023 E.03703
G1 X138.856 Y157.564 E.19179
M204 S10000
G1 X138.5 Y157.504 F60000
; LINE_WIDTH: 0.394304
G1 F13127.189
M204 S8000
G1 X138.5 Y157.333 E.0056
G1 X138.158 Y157.333 E.0112
G1 X138.158 Y162.667 E.17435
G1 X138.5 Y162.667 E.0112
G1 X138.5 Y157.564 E.16679
; CHANGE_LAYER
; Z_HEIGHT: 5.96
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13127.189
G1 X138.5 Y159.564 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 25/47
; update layer progress
M73 L25
M991 S0 P24 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z6.12 I.076 J1.215 P1  F60000
G1 X185.799 Y156.593 Z6.12
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.06393
G1 X187.482 Y163.407 E.25885
G1 X185.799 Y163.407 E.06393
G1 X185.799 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.415 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.08606
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.415 Y163.79 E.08606
G1 X185.415 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.415 Y156.221 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.182 Y163.023 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.03217
G1 X187.098 Y156.977 E.21241
G1 X186.182 Y156.977 E.03217
G1 X186.182 Y162.963 E.2103
M204 S10000
G1 X186.64 Y162.565 F60000
; LINE_WIDTH: 0.598724
G1 F8223.384
M204 S8000
G1 X186.64 Y157.495 E.26453
; COOLING_NODE: 6
; WIPE_START
G1 X186.64 Y159.495 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.626 Y162.503 Z6.36 F60000
G1 X177.518 Y163.407 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X179.201 Y156.593 E.06393
G1 X179.201 Y163.407 E.25885
G1 X177.578 Y163.407 E.06165
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.585 Y156.21 E.08606
G1 X179.585 Y163.79 E.2663
G1 X177.195 Y163.79 E.08396
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.902 Y163.023 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X178.818 Y163.023 E.03217
G1 X178.818 Y156.977 E.21241
G1 X177.902 Y156.977 E.03217
G1 X177.902 Y162.963 E.2103
M204 S10000
G1 X178.36 Y162.565 F60000
; LINE_WIDTH: 0.598744
G1 F8223.084
M204 S8000
G1 X178.36 Y157.495 E.26454
; COOLING_NODE: 3
; WIPE_START
G1 X178.36 Y159.495 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.181 Y162.088 Z6.36 F60000
G1 X167.532 Y163.407 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.857 Y163.407 E.0636
G1 X165.857 Y156.593 E.25885
G1 X167.532 Y156.593 E.0636
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.474 Y163.79 E.08576
G1 X165.474 Y156.21 E.2663
G1 X167.915 Y156.21 E.08576
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.916 Y163.779 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.241 Y163.023 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.03187
G1 X167.148 Y156.977 E.21241
G1 X166.241 Y156.977 E.03187
G1 X166.241 Y162.963 E.2103
M204 S10000
G1 X166.695 Y162.57 F60000
; LINE_WIDTH: 0.590084
G1 F8355.305
M204 S8000
G1 X166.695 Y157.49 E.2608
; COOLING_NODE: 3
; WIPE_START
G1 X166.695 Y159.49 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.568 Y156.757 Z6.36 F60000
G1 X159.143 Y156.593 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.143 Y163.407 E.25885
G1 X157.468 Y163.407 E.0636
G1 X157.468 Y156.593 E.25885
G1 X159.083 Y156.593 E.06132
; COOLING_NODE: 3
M204 S250
G1 X159.526 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.526 Y163.79 E.2663
G1 X157.085 Y163.79 E.08576
G1 X157.085 Y156.21 E.2663
G1 X159.466 Y156.21 E.08365
; WIPE_START
M204 S8000
G1 X159.482 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.759 Y157.43 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X158.759 Y156.977 E.01593
G1 X157.852 Y156.977 E.03187
G1 X157.852 Y163.023 E.21241
G1 X158.759 Y163.023 E.03187
G1 X158.759 Y157.49 E.19437
; WIPE_START
G1 X158.759 Y159.49 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.305 Y162.57 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; LINE_WIDTH: 0.590064
G1 F8355.616
M204 S8000
G1 X158.305 Y157.49 E.26079
; COOLING_NODE: 1
; WIPE_START
G1 X158.305 Y159.49 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.136 Y162.109 Z6.36 F60000
G1 X147.581 Y163.407 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.916 Y163.407 E.06327
G1 X145.916 Y156.593 E.25885
G1 X147.581 Y156.593 E.06327
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.533 Y163.79 E.08545
G1 X145.533 Y156.21 E.2663
G1 X147.965 Y156.21 E.08545
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.966 Y163.779 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.198 Y157.426 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X147.198 Y156.977 E.01578
G1 X146.3 Y156.977 E.03156
G1 X146.3 Y163.023 E.21241
G1 X147.198 Y163.023 E.03156
G1 X147.198 Y157.486 E.19452
; WIPE_START
G1 X147.198 Y159.486 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.749 Y162.574 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; LINE_WIDTH: 0.581424
G1 F8491.849
M204 S8000
G1 X146.749 Y157.486 E.25704
; COOLING_NODE: 1
; WIPE_START
G1 X146.749 Y159.486 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.954 Y162.962 Z6.36 F60000
G1 X139.084 Y163.407 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.06327
G1 X137.418 Y156.593 E.25885
G1 X139.084 Y156.593 E.06327
G1 X139.084 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.467 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.08545
G1 X137.035 Y156.21 E.2663
G1 X139.467 Y156.21 E.08545
G1 X139.467 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.468 Y163.779 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.7 Y157.426 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X138.7 Y156.977 E.01578
G1 X137.802 Y156.977 E.03156
G1 X137.802 Y163.023 E.21241
G1 X138.7 Y163.023 E.03156
G1 X138.7 Y157.486 E.19452
; WIPE_START
G1 X138.7 Y159.486 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.251 Y162.574 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; LINE_WIDTH: 0.581404
G1 F8492.168
M204 S8000
G1 X138.251 Y157.486 E.25703
; CHANGE_LAYER
; Z_HEIGHT: 6.2
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F8492.168
G1 X138.251 Y159.486 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 26/47
; update layer progress
M73 L26
M991 S0 P25 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z6.36 I.074 J1.215 P1  F60000
G1 X185.932 Y156.593 Z6.36
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.05885
G1 X187.482 Y163.407 E.25885
G1 X185.932 Y163.407 E.05885
G1 X185.932 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.549 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.08137
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.549 Y163.79 E.08137
G1 X185.549 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.548 Y156.218 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.316 Y163.023 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.02748
G1 X187.098 Y156.977 E.21241
G1 X186.316 Y156.977 E.02748
G1 X186.316 Y162.963 E.2103
M204 S10000
G1 X186.707 Y162.632 F60000
; LINE_WIDTH: 0.465124
G1 F10879.552
M204 S8000
G1 X186.707 Y157.428 E.20522
; COOLING_NODE: 6
; WIPE_START
G1 X186.707 Y159.428 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.703 Y162.461 Z6.6 F60000
G1 X177.518 Y163.407 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X179.068 Y156.593 E.05885
M73 P84 R2
G1 X179.068 Y163.407 E.25885
G1 X177.578 Y163.407 E.05657
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.451 Y156.21 E.08137
G1 X179.451 Y163.79 E.2663
G1 X177.195 Y163.79 E.07926
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.902 Y163.023 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X178.684 Y163.023 E.02748
G1 X178.684 Y156.977 E.21241
G1 X177.902 Y156.977 E.02748
G1 X177.902 Y162.963 E.2103
M204 S10000
G1 X178.293 Y162.632 F60000
; LINE_WIDTH: 0.465124
G1 F10879.552
M204 S8000
G1 X178.293 Y157.428 E.20522
; COOLING_NODE: 3
; WIPE_START
G1 X178.293 Y159.428 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.134 Y162.075 Z6.6 F60000
G1 X167.532 Y163.407 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.988 Y163.407 E.05864
G1 X165.988 Y156.593 E.25885
G1 X167.532 Y156.593 E.05864
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.604 Y163.79 E.08117
G1 X165.604 Y156.21 E.2663
G1 X167.915 Y156.21 E.08117
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.916 Y163.782 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.371 Y163.023 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.02728
G1 X167.148 Y156.977 E.21241
G1 X166.371 Y156.977 E.02728
G1 X166.371 Y162.963 E.2103
M204 S10000
G1 X166.76 Y162.635 F60000
; LINE_WIDTH: 0.459584
G1 F11027.25
M204 S8000
G1 X166.76 Y157.425 E.20268
; COOLING_NODE: 3
; WIPE_START
G1 X166.76 Y159.425 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.591 Y156.805 Z6.6 F60000
G1 X159.012 Y156.593 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.012 Y163.407 E.25885
G1 X157.468 Y163.407 E.05864
G1 X157.468 Y156.593 E.25885
G1 X158.952 Y156.593 E.05636
; COOLING_NODE: 3
M204 S250
G1 X159.396 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.396 Y163.79 E.2663
G1 X157.085 Y163.79 E.08117
G1 X157.085 Y156.21 E.2663
G1 X159.336 Y156.21 E.07907
; WIPE_START
M204 S8000
G1 X159.351 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.629 Y157.365 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X158.629 Y156.977 E.01364
G1 X157.852 Y156.977 E.02728
G1 X157.852 Y163.023 E.21241
G1 X158.629 Y163.023 E.02728
G1 X158.629 Y157.425 E.19666
; WIPE_START
G1 X158.629 Y159.425 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.24 Y162.635 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; LINE_WIDTH: 0.459584
G1 F11027.25
M204 S8000
G1 X158.24 Y157.425 E.20268
; COOLING_NODE: 1
; WIPE_START
G1 X158.24 Y159.425 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.09 Y162.096 Z6.6 F60000
G1 X147.581 Y163.407 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.043 Y163.407 E.05843
G1 X146.043 Y156.593 E.25885
G1 X147.581 Y156.593 E.05843
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.66 Y163.79 E.08098
G1 X145.66 Y156.21 E.2663
G1 X147.965 Y156.21 E.08098
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.966 Y163.782 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.198 Y157.362 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X147.198 Y156.977 E.01354
G1 X146.427 Y156.977 E.02709
G1 X146.427 Y163.023 E.21241
G1 X147.198 Y163.023 E.02709
G1 X147.198 Y157.422 E.19676
; WIPE_START
G1 X147.198 Y159.422 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.812 Y162.638 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; LINE_WIDTH: 0.454024
G1 F11179.569
M204 S8000
G1 X146.812 Y157.422 E.20014
; COOLING_NODE: 1
; WIPE_START
G1 X146.812 Y159.422 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.005 Y162.875 Z6.6 F60000
G1 X138.956 Y163.407 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.05843
G1 X137.418 Y156.593 E.25885
G1 X138.956 Y156.593 E.05843
G1 X138.956 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.34 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.08098
G1 X137.035 Y156.21 E.2663
G1 X139.34 Y156.21 E.08098
G1 X139.34 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.341 Y163.782 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.573 Y157.362 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X138.573 Y156.977 E.01354
G1 X137.802 Y156.977 E.02709
G1 X137.802 Y163.023 E.21241
G1 X138.573 Y163.023 E.02709
G1 X138.573 Y157.422 E.19676
; WIPE_START
G1 X138.573 Y159.422 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.187 Y162.638 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; LINE_WIDTH: 0.454044
G1 F11179.014
M204 S8000
G1 X138.187 Y157.422 E.20015
; CHANGE_LAYER
; Z_HEIGHT: 6.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11179.014
G1 X138.187 Y159.422 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 27/47
; update layer progress
M73 L27
M991 S0 P26 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z6.6 I.072 J1.215 P1  F60000
G1 X186.041 Y156.593 Z6.6
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.05474
G1 X187.482 Y163.407 E.25885
G1 X186.041 Y163.407 E.05474
G1 X186.041 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.657 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.07756
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.657 Y163.79 E.07756
G1 X185.657 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.657 Y156.216 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.424 Y163.023 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X187.098 Y163.023 E.02367
G1 X187.098 Y156.977 E.21241
G1 X186.424 Y156.977 E.02367
G1 X186.424 Y162.963 E.2103
M204 S10000
G1 X186.761 Y162.686 F60000
; LINE_WIDTH: 0.356804
G1 F14739.601
M204 S8000
G1 X186.761 Y157.374 E.15463
; COOLING_NODE: 6
; WIPE_START
G1 X186.761 Y159.374 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.766 Y162.426 Z6.84 F60000
G1 X177.518 Y163.407 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X178.959 Y156.593 E.05474
G1 X178.959 Y163.407 E.25885
G1 X177.578 Y163.407 E.05246
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.343 Y156.21 E.07756
G1 X179.343 Y163.79 E.2663
G1 X177.195 Y163.79 E.07546
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.902 Y163.023 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X178.576 Y163.023 E.02367
G1 X178.576 Y156.977 E.21241
G1 X177.902 Y156.977 E.02367
G1 X177.902 Y162.963 E.2103
M204 S10000
G1 X178.239 Y162.686 F60000
; LINE_WIDTH: 0.356804
G1 F14739.601
M204 S8000
G1 X178.239 Y157.374 E.15463
; COOLING_NODE: 3
; WIPE_START
G1 X178.239 Y159.374 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.096 Y162.064 Z6.84 F60000
G1 X167.532 Y163.407 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.095 Y163.407 E.05459
G1 X166.095 Y156.593 E.25885
G1 X167.532 Y156.593 E.05459
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.711 Y163.79 E.07743
G1 X165.711 Y156.21 E.2663
G1 X167.915 Y156.21 E.07743
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.916 Y163.784 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.478 Y163.023 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X167.148 Y163.023 E.02353
G1 X167.148 Y156.977 E.21241
G1 X166.478 Y156.977 E.02353
G1 X166.478 Y162.963 E.2103
M204 S10000
G1 X166.813 Y162.688 F60000
; LINE_WIDTH: 0.352884
G1 F14931.318
M204 S8000
G1 X166.813 Y157.372 E.15275
; COOLING_NODE: 3
; WIPE_START
G1 X166.813 Y159.372 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.612 Y156.842 Z6.84 F60000
G1 X158.905 Y156.593 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.905 Y163.407 E.25885
G1 X157.468 Y163.407 E.05459
G1 X157.468 Y156.593 E.25885
G1 X158.845 Y156.593 E.05231
; COOLING_NODE: 3
M204 S250
M73 P85 R2
G1 X159.289 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.289 Y163.79 E.2663
G1 X157.085 Y163.79 E.07743
G1 X157.085 Y156.21 E.2663
G1 X159.229 Y156.21 E.07532
; WIPE_START
M204 S8000
G1 X159.245 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.522 Y157.312 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X158.522 Y156.977 E.01177
G1 X157.852 Y156.977 E.02353
G1 X157.852 Y163.023 E.21241
G1 X158.522 Y163.023 E.02353
G1 X158.522 Y157.372 E.19854
; WIPE_START
G1 X158.522 Y159.372 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.187 Y162.688 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; LINE_WIDTH: 0.352864
G1 F14932.309
M204 S8000
G1 X158.187 Y157.372 E.15274
; COOLING_NODE: 1
; WIPE_START
G1 X158.187 Y159.372 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.053 Y162.086 Z6.84 F60000
G1 X147.581 Y163.407 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.148 Y163.407 E.05447
G1 X146.148 Y156.593 E.25885
G1 X147.581 Y156.593 E.05447
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.764 Y163.79 E.07731
G1 X145.764 Y156.21 E.2663
G1 X147.965 Y156.21 E.07731
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.966 Y163.785 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.123 Y157.31 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.569054
G1 F8694.812
M204 S8000
G1 X147.123 Y157.051 E.01277
G1 X146.606 Y157.051 E.02554
G1 X146.606 Y162.949 E.29098
G1 X147.123 Y162.949 E.02554
G1 X147.123 Y157.37 E.27525
; COOLING_NODE: 1
; WIPE_START
G1 X147.123 Y159.37 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.264 Y162.717 Z6.84 F60000
G1 X138.852 Y163.407 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.05447
G1 X137.418 Y156.593 E.25885
G1 X138.852 Y156.593 E.05447
G1 X138.852 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.236 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.07731
G1 X137.035 Y156.21 E.2663
G1 X139.236 Y156.21 E.07731
G1 X139.236 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.236 Y163.785 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.394 Y157.31 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.569054
G1 F8694.812
M204 S8000
G1 X138.394 Y157.051 E.01277
G1 X137.876 Y157.051 E.02554
G1 X137.876 Y162.949 E.29098
G1 X138.394 Y162.949 E.02554
G1 X138.394 Y157.37 E.27525
; CHANGE_LAYER
; Z_HEIGHT: 6.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F8694.812
G1 X138.394 Y159.37 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 28/47
; update layer progress
M73 L28
M991 S0 P27 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z6.84 I.071 J1.215 P1  F60000
G1 X186.125 Y156.593 Z6.84
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.05153
G1 X187.482 Y163.407 E.25885
G1 X186.125 Y163.407 E.05153
G1 X186.125 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.742 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.0746
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.742 Y163.79 E.0746
G1 X185.742 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.741 Y156.213 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.564 Y162.968 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.530454
G1 F9395.552
M204 S8000
G1 X187.043 Y162.968 E.02187
G1 X187.043 Y157.032 E.27104
G1 X186.564 Y157.032 E.02187
G1 X186.564 Y162.908 E.2683
; COOLING_NODE: 6
; WIPE_START
G1 X186.564 Y160.908 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.207 Y162.94 Z7.08 F60000
G1 X177.518 Y163.407 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X178.875 Y156.593 E.05153
G1 X178.875 Y163.407 E.25885
G1 X177.578 Y163.407 E.04925
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.258 Y156.21 E.0746
G1 X179.258 Y163.79 E.2663
G1 X177.195 Y163.79 E.07249
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.957 Y162.968 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.530464
G1 F9395.358
M204 S8000
G1 X178.436 Y162.968 E.02187
G1 X178.436 Y157.032 E.27104
G1 X177.957 Y157.032 E.02187
G1 X177.957 Y162.908 E.26831
; COOLING_NODE: 3
; WIPE_START
G1 X177.957 Y160.908 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.535 Y162.687 Z7.08 F60000
G1 X167.532 Y163.407 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.177 Y163.407 E.05144
G1 X166.177 Y156.593 E.25885
G1 X167.532 Y156.593 E.05144
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.794 Y163.79 E.07452
G1 X165.794 Y156.21 E.2663
G1 X167.915 Y156.21 E.07452
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.916 Y163.787 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.616 Y162.968 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.529284
G1 F9418.561
M204 S8000
G1 X167.093 Y162.968 E.02176
G1 X167.093 Y157.032 E.27043
G1 X166.616 Y157.032 E.02176
G1 X166.616 Y162.908 E.2677
; COOLING_NODE: 3
; WIPE_START
G1 X166.616 Y160.908 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.938 Y157.211 Z7.08 F60000
G1 X158.823 Y156.593 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.823 Y163.407 E.25885
G1 X157.468 Y163.407 E.05144
G1 X157.468 Y156.593 E.25885
G1 X158.763 Y156.593 E.04916
; COOLING_NODE: 3
M204 S250
G1 X159.206 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.206 Y163.79 E.2663
G1 X157.085 Y163.79 E.07452
G1 X157.085 Y156.21 E.2663
G1 X159.146 Y156.21 E.07241
; WIPE_START
M204 S8000
G1 X159.162 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.384 Y157.27 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.529274
G1 F9418.758
M204 S8000
G1 X158.384 Y157.032 E.01088
G1 X157.907 Y157.032 E.02176
G1 X157.907 Y162.968 E.27043
G1 X158.384 Y162.968 E.02176
G1 X158.384 Y157.33 E.25681
; COOLING_NODE: 1
; WIPE_START
G1 X158.384 Y159.33 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.243 Y162.025 Z7.08 F60000
G1 X147.581 Y163.407 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.23 Y163.407 E.05135
G1 X146.23 Y156.593 E.25885
G1 X147.581 Y156.593 E.05135
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.846 Y163.79 E.07443
G1 X145.846 Y156.21 E.2663
G1 X147.965 Y156.21 E.07443
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.966 Y163.787 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.144 Y157.269 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.528094
G1 F9442.079
M204 S8000
G1 X147.144 Y157.031 E.01083
G1 X146.667 Y157.031 E.02166
G1 X146.667 Y162.969 E.26981
G1 X147.144 Y162.969 E.02166
G1 X147.144 Y157.329 E.25626
; COOLING_NODE: 1
; WIPE_START
G1 X147.144 Y159.329 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.282 Y162.671 Z7.08 F60000
G1 X138.77 Y163.407 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.05135
G1 X137.418 Y156.593 E.25885
G1 X138.77 Y156.593 E.05135
G1 X138.77 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.154 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.07443
G1 X137.035 Y156.21 E.2663
G1 X139.154 Y156.21 E.07443
G1 X139.154 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.154 Y163.787 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.333 Y157.269 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.528104
G1 F9441.88
M204 S8000
G1 X138.333 Y157.031 E.01083
G1 X137.856 Y157.031 E.02166
G1 X137.856 Y162.969 E.26982
G1 X138.333 Y162.969 E.02166
G1 X138.333 Y157.329 E.25626
; CHANGE_LAYER
; Z_HEIGHT: 6.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9441.88
M73 P85 R1
G1 X138.333 Y159.329 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 29/47
; update layer progress
M73 L29
M991 S0 P28 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z7.08 I.069 J1.215 P1  F60000
G1 X186.19 Y156.593 Z7.08
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
M73 P86 R1
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.04907
G1 X187.482 Y163.407 E.25885
G1 X186.19 Y163.407 E.04907
G1 X186.19 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.806 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.07232
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.806 Y163.79 E.07232
G1 X185.806 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.806 Y156.212 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.613 Y162.984 Z7.32 F60000
G1 Z6.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.498024
G1 F10077.937
M204 S8000
G1 X187.059 Y162.984 E.01901
G1 X187.059 Y157.016 E.25407
G1 X186.613 Y157.016 E.01901
G1 X186.613 Y162.924 E.25151
; COOLING_NODE: 6
; WIPE_START
G1 X186.613 Y160.924 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.249 Y162.934 Z7.32 F60000
G1 X177.518 Y163.407 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X178.81 Y156.593 E.04907
G1 X178.81 Y163.407 E.25885
G1 X177.578 Y163.407 E.04679
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.194 Y156.21 E.07232
G1 X179.194 Y163.79 E.2663
G1 X177.195 Y163.79 E.07021
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.941 Y162.984 Z7.32 F60000
G1 Z6.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.498024
G1 F10077.937
M204 S8000
G1 X178.388 Y162.984 E.01901
G1 X178.388 Y157.016 E.25407
G1 X177.941 Y157.016 E.01901
G1 X177.941 Y162.924 E.25151
; COOLING_NODE: 3
; WIPE_START
G1 X177.941 Y160.924 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.517 Y162.695 Z7.32 F60000
G1 X167.532 Y163.407 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.241 Y163.407 E.04903
G1 X166.241 Y156.593 E.25885
G1 X167.532 Y156.593 E.04903
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.858 Y163.79 E.07228
G1 X165.858 Y156.21 E.2663
G1 X167.915 Y156.21 E.07228
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.916 Y163.788 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.663 Y162.984 Z7.32 F60000
G1 Z6.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.497514
G1 F10089.46
M204 S8000
G1 X167.109 Y162.984 E.01897
G1 X167.109 Y157.016 E.2538
G1 X166.663 Y157.016 E.01897
G1 X166.663 Y162.924 E.25125
; COOLING_NODE: 3
; WIPE_START
G1 X166.663 Y160.924 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.97 Y157.257 Z7.32 F60000
G1 X158.759 Y156.593 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.759 Y163.407 E.25885
G1 X157.468 Y163.407 E.04903
G1 X157.468 Y156.593 E.25885
G1 X158.699 Y156.593 E.04675
; COOLING_NODE: 3
M204 S250
G1 X159.142 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.142 Y163.79 E.2663
G1 X157.085 Y163.79 E.07228
G1 X157.085 Y156.21 E.2663
G1 X159.082 Y156.21 E.07018
; WIPE_START
M204 S8000
G1 X159.098 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.337 Y157.239 Z7.32 F60000
G1 Z6.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.497514
G1 F10089.46
M204 S8000
G1 X158.337 Y157.016 E.00948
G1 X157.891 Y157.016 E.01897
G1 X157.891 Y162.984 E.2538
G1 X158.337 Y162.984 E.01897
G1 X158.337 Y157.299 E.24177
; COOLING_NODE: 1
; WIPE_START
G1 X158.337 Y159.299 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.207 Y162.022 Z7.32 F60000
G1 X147.581 Y163.407 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.292 Y163.407 E.04899
G1 X146.292 Y156.593 E.25885
G1 X147.581 Y156.593 E.04899
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.909 Y163.79 E.07225
G1 X145.909 Y156.21 E.2663
G1 X147.965 Y156.21 E.07225
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.966 Y163.788 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.159 Y157.238 Z7.32 F60000
G1 Z6.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.497004
G1 F10101.01
M204 S8000
G1 X147.159 Y157.015 E.00946
G1 X146.714 Y157.015 E.01892
G1 X146.714 Y162.985 E.25353
G1 X147.159 Y162.985 E.01892
G1 X147.159 Y157.298 E.24152
; COOLING_NODE: 1
; WIPE_START
G1 X147.159 Y159.298 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.295 Y162.635 Z7.32 F60000
G1 X138.708 Y163.407 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.04899
G1 X137.418 Y156.593 E.25885
G1 X138.708 Y156.593 E.04899
G1 X138.708 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.091 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.07225
G1 X137.035 Y156.21 E.2663
G1 X139.091 Y156.21 E.07225
G1 X139.091 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.092 Y163.788 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.286 Y157.238 Z7.32 F60000
G1 Z6.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.497004
G1 F10101.01
M204 S8000
G1 X138.286 Y157.015 E.00946
G1 X137.84 Y157.015 E.01892
G1 X137.84 Y162.985 E.25353
G1 X138.286 Y162.985 E.01892
G1 X138.286 Y157.298 E.24152
; CHANGE_LAYER
; Z_HEIGHT: 7.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10101.01
G1 X138.286 Y159.298 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 30/47
; update layer progress
M73 L30
M991 S0 P29 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z7.32 I.069 J1.215 P1  F60000
G1 X186.234 Y156.593 Z7.32
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.04739
G1 X187.482 Y163.407 E.25885
G1 X186.234 Y163.407 E.04739
G1 X186.234 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.851 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.07077
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.851 Y163.79 E.07077
G1 X185.851 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.85 Y156.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.646 Y162.995 Z7.56 F60000
G1 Z7.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.475974
G1 F10601.457
M204 S8000
G1 X187.07 Y162.995 E.01718
G1 X187.07 Y157.005 E.24241
G1 X186.646 Y157.005 E.01718
G1 X186.646 Y162.935 E.23999
; COOLING_NODE: 6
; WIPE_START
G1 X186.646 Y160.935 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.278 Y162.93 Z7.56 F60000
G1 X177.518 Y163.407 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X178.766 Y156.593 E.04739
G1 X178.766 Y163.407 E.25885
G1 X177.578 Y163.407 E.04511
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.149 Y156.21 E.07077
G1 X179.149 Y163.79 E.2663
G1 X177.195 Y163.79 E.06866
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.93 Y162.995 Z7.56 F60000
G1 Z7.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.475974
G1 F10601.457
M204 S8000
G1 X178.354 Y162.995 E.01718
G1 X178.354 Y157.005 E.24241
G1 X177.93 Y157.005 E.01718
G1 X177.93 Y162.935 E.23999
; COOLING_NODE: 3
; WIPE_START
G1 X177.93 Y160.935 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.504 Y162.7 Z7.56 F60000
G1 X167.532 Y163.407 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.285 Y163.407 E.04737
G1 X166.285 Y156.593 E.25885
G1 X167.532 Y156.593 E.04737
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.901 Y163.79 E.07075
G1 X165.901 Y156.21 E.2663
G1 X167.915 Y156.21 E.07075
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.916 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.696 Y162.995 Z7.56 F60000
G1 Z7.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.475684
G1 F10608.704
M204 S8000
G1 X167.12 Y162.995 E.01715
G1 X167.12 Y157.005 E.24226
G1 X166.696 Y157.005 E.01715
G1 X166.696 Y162.935 E.23983
; COOLING_NODE: 3
; WIPE_START
G1 X166.696 Y160.935 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.991 Y157.288 Z7.56 F60000
G1 X158.715 Y156.593 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.715 Y163.407 E.25885
G1 X157.468 Y163.407 E.04737
G1 X157.468 Y156.593 E.25885
G1 X158.655 Y156.593 E.04509
; COOLING_NODE: 3
M204 S250
M73 P87 R1
G1 X159.099 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.099 Y163.79 E.2663
G1 X157.085 Y163.79 E.07075
G1 X157.085 Y156.21 E.2663
G1 X159.039 Y156.21 E.06864
; WIPE_START
M204 S8000
G1 X159.055 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.304 Y157.217 Z7.56 F60000
G1 Z7.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.475694
G1 F10608.455
M204 S8000
G1 X158.304 Y157.005 E.00858
G1 X157.88 Y157.005 E.01716
G1 X157.88 Y162.995 E.24227
G1 X158.304 Y162.995 E.01716
G1 X158.304 Y157.277 E.23126
; COOLING_NODE: 1
; WIPE_START
G1 X158.304 Y159.277 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.182 Y162.02 Z7.56 F60000
G1 X147.581 Y163.407 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.335 Y163.407 E.04735
G1 X146.335 Y156.593 E.25885
G1 X147.581 Y156.593 E.04735
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.952 Y163.79 E.07073
G1 X145.952 Y156.21 E.2663
G1 X147.965 Y156.21 E.07073
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.966 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.17 Y157.217 Z7.56 F60000
G1 Z7.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.475404
G1 F10615.712
M204 S8000
G1 X147.17 Y157.005 E.00857
G1 X146.746 Y157.005 E.01713
G1 X146.746 Y162.995 E.24211
G1 X147.17 Y162.995 E.01713
G1 X147.17 Y157.277 E.23112
; COOLING_NODE: 1
; WIPE_START
G1 X147.17 Y159.277 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.304 Y162.61 Z7.56 F60000
G1 X138.665 Y163.407 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.04735
G1 X137.418 Y156.593 E.25885
G1 X138.665 Y156.593 E.04735
G1 X138.665 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.048 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.07073
G1 X137.035 Y156.21 E.2663
G1 X139.048 Y156.21 E.07073
G1 X139.048 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.049 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.254 Y157.217 Z7.56 F60000
G1 Z7.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.475404
G1 F10615.712
M204 S8000
G1 X138.254 Y157.005 E.00857
G1 X137.83 Y157.005 E.01713
G1 X137.83 Y162.995 E.24211
G1 X138.254 Y162.995 E.01713
G1 X138.254 Y157.277 E.23112
; CHANGE_LAYER
; Z_HEIGHT: 7.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10615.712
G1 X138.254 Y159.277 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 31/47
; update layer progress
M73 L31
M991 S0 P30 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z7.56 I.068 J1.215 P1  F60000
G1 X186.26 Y156.593 Z7.56
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.482 Y156.593 E.0464
G1 X187.482 Y163.407 E.25885
G1 X186.26 Y163.407 E.0464
G1 X186.26 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.877 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.06985
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.877 Y163.79 E.06985
G1 X185.877 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.865 Y156.21 E-.75587
G1 X187.865 Y156.221 E-.00413
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.665 Y163.002 Z7.8 F60000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.462874
G1 F10939.058
M204 S8000
G1 X187.077 Y163.002 E.01613
G1 X187.077 Y156.998 E.23545
G1 X186.665 Y156.998 E.01613
G1 X186.665 Y162.942 E.23309
; COOLING_NODE: 6
; WIPE_START
G1 X186.665 Y160.942 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.296 Y162.928 Z7.8 F60000
G1 X177.518 Y163.407 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.518 Y156.593 E.25885
G1 X178.74 Y156.593 E.0464
G1 X178.74 Y163.407 E.25885
G1 X177.578 Y163.407 E.04412
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.123 Y156.21 E.06985
G1 X179.123 Y163.79 E.2663
G1 X177.195 Y163.79 E.06774
; WIPE_START
M204 S8000
G1 X177.179 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.923 Y163.002 Z7.8 F60000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.462874
G1 F10939.058
M204 S8000
G1 X178.335 Y163.002 E.01613
G1 X178.335 Y156.998 E.23545
G1 X177.923 Y156.998 E.01613
G1 X177.923 Y162.942 E.23309
; COOLING_NODE: 3
; WIPE_START
G1 X177.923 Y160.942 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.497 Y162.703 Z7.8 F60000
G1 X167.532 Y163.407 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.31 Y163.407 E.0464
G1 X166.31 Y156.593 E.25885
G1 X167.532 Y156.593 E.0464
G1 X167.532 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.927 Y163.79 E.06985
G1 X165.927 Y156.21 E.2663
G1 X167.915 Y156.21 E.06985
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.927 Y163.79 E-.75585
G1 X165.927 Y163.779 E-.00415
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.715 Y163.002 Z7.8 F60000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.462854
G1 F10939.59
M204 S8000
G1 X167.127 Y163.002 E.01613
G1 X167.127 Y156.998 E.23544
G1 X166.715 Y156.998 E.01613
G1 X166.715 Y162.942 E.23308
; COOLING_NODE: 3
; WIPE_START
G1 X166.715 Y160.942 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.004 Y157.306 Z7.8 F60000
G1 X158.69 Y156.593 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.69 Y163.407 E.25885
G1 X157.468 Y163.407 E.0464
G1 X157.468 Y156.593 E.25885
G1 X158.63 Y156.593 E.04412
; COOLING_NODE: 3
M204 S250
G1 X159.073 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.073 Y163.79 E.2663
G1 X157.085 Y163.79 E.06985
G1 X157.085 Y156.21 E.2663
G1 X159.013 Y156.21 E.06774
; WIPE_START
M204 S8000
G1 X159.029 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.285 Y157.204 Z7.8 F60000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.462854
G1 F10939.59
M204 S8000
G1 X158.285 Y156.998 E.00807
G1 X157.873 Y156.998 E.01613
G1 X157.873 Y163.002 E.23544
G1 X158.285 Y163.002 E.01613
G1 X158.285 Y157.264 E.22502
; COOLING_NODE: 1
; WIPE_START
G1 X158.285 Y159.264 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.167 Y162.019 Z7.8 F60000
G1 X147.581 Y163.407 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.36 Y163.407 E.04639
G1 X146.36 Y156.593 E.25885
G1 X147.581 Y156.593 E.04639
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.977 Y163.79 E.06985
G1 X145.977 Y156.21 E.2663
G1 X147.965 Y156.21 E.06985
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.977 Y163.79 E-.75583
G1 X145.977 Y163.779 E-.00418
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.177 Y157.204 Z7.8 F60000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.462824
G1 F10940.388
M204 S8000
G1 X147.177 Y156.998 E.00807
G1 X146.765 Y156.998 E.01613
G1 X146.765 Y163.002 E.23542
G1 X147.177 Y163.002 E.01613
G1 X147.177 Y157.264 E.225
; COOLING_NODE: 1
; WIPE_START
G1 X147.177 Y159.264 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.31 Y162.596 Z7.8 F60000
G1 X138.64 Y163.407 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.418 Y163.407 E.04639
G1 X137.418 Y156.593 E.25885
G1 X138.64 Y156.593 E.04639
G1 X138.64 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.023 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.06985
G1 X137.035 Y156.21 E.2663
G1 X139.023 Y156.21 E.06985
G1 X139.023 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.035 Y163.79 E-.75583
G1 X137.035 Y163.779 E-.00418
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.235 Y157.204 Z7.8 F60000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.462824
G1 F10940.388
M204 S8000
G1 X138.235 Y156.998 E.00807
G1 X137.823 Y156.998 E.01613
G1 X137.823 Y163.002 E.23542
G1 X138.235 Y163.002 E.01613
G1 X138.235 Y157.264 E.225
; CHANGE_LAYER
; Z_HEIGHT: 7.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10940.388
G1 X138.235 Y159.264 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 32/47
; update layer progress
M73 L32
M991 S0 P31 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z7.8 I.068 J1.215 P1  F60000
G1 X186.268 Y156.593 Z7.8
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.481 Y156.593 E.0461
G1 X187.481 Y163.407 E.25885
G1 X186.268 Y163.407 E.0461
G1 X186.268 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.884 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.865 Y156.21 E.06958
M73 P88 R1
G1 X187.865 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.884 Y163.79 E.06958
G1 X185.884 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.865 Y156.21 E-.7529
G1 X187.865 Y156.229 E-.0071
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.671 Y163.004 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.458974
G1 F11043.758
M204 S8000
G1 X187.078 Y163.004 E.01583
G1 X187.078 Y156.996 E.23337
G1 X186.671 Y156.996 E.01583
G1 X186.671 Y162.944 E.23104
; COOLING_NODE: 6
; WIPE_START
G1 X186.671 Y160.944 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.3 Y162.927 Z8.04 F60000
G1 X177.519 Y163.407 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.519 Y156.593 E.25885
G1 X178.732 Y156.593 E.0461
G1 X178.732 Y163.407 E.25885
G1 X177.579 Y163.407 E.04382
; COOLING_NODE: 6
M204 S250
G1 X177.135 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.135 Y156.21 E.2663
G1 X179.116 Y156.21 E.06958
G1 X179.116 Y163.79 E.2663
G1 X177.195 Y163.79 E.06747
; WIPE_START
M204 S8000
G1 X177.18 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.922 Y163.004 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.458984
G1 F11043.487
M204 S8000
G1 X178.329 Y163.004 E.01583
G1 X178.329 Y156.996 E.23337
G1 X177.922 Y156.996 E.01583
G1 X177.922 Y162.944 E.23104
; COOLING_NODE: 3
; WIPE_START
G1 X177.922 Y160.944 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.495 Y162.704 Z8.04 F60000
G1 X167.531 Y163.407 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.318 Y163.407 E.0461
G1 X166.318 Y156.593 E.25885
G1 X167.531 Y156.593 E.0461
G1 X167.531 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.934 Y163.79 E.06958
G1 X165.934 Y156.21 E.2663
G1 X167.915 Y156.21 E.06958
G1 X167.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.934 Y163.79 E-.75291
G1 X165.934 Y163.771 E-.00709
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.721 Y163.004 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.458984
G1 F11043.487
M204 S8000
G1 X167.128 Y163.004 E.01583
G1 X167.128 Y156.996 E.23337
G1 X166.721 Y156.996 E.01583
G1 X166.721 Y162.944 E.23104
; COOLING_NODE: 3
; WIPE_START
G1 X166.721 Y160.944 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.008 Y157.311 Z8.04 F60000
G1 X158.682 Y156.593 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.682 Y163.407 E.25885
G1 X157.469 Y163.407 E.0461
G1 X157.469 Y156.593 E.25885
G1 X158.622 Y156.593 E.04382
; COOLING_NODE: 3
M204 S250
G1 X159.066 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.066 Y163.79 E.2663
G1 X157.085 Y163.79 E.06958
G1 X157.085 Y156.21 E.2663
G1 X159.006 Y156.21 E.06747
; WIPE_START
M204 S8000
G1 X159.022 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.279 Y157.2 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.458984
G1 F11043.487
M204 S8000
G1 X158.279 Y156.996 E.00792
G1 X157.872 Y156.996 E.01583
G1 X157.872 Y163.004 E.23337
G1 X158.279 Y163.004 E.01583
G1 X158.279 Y157.26 E.22313
; COOLING_NODE: 1
; WIPE_START
G1 X158.279 Y159.26 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.163 Y162.018 Z8.04 F60000
G1 X147.581 Y163.407 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.368 Y163.407 E.0461
G1 X146.368 Y156.593 E.25885
G1 X147.581 Y156.593 E.0461
G1 X147.581 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.965 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.984 Y163.79 E.06958
G1 X145.984 Y156.21 E.2663
G1 X147.965 Y156.21 E.06958
G1 X147.965 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.984 Y163.79 E-.75292
G1 X145.984 Y163.771 E-.00709
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.178 Y157.2 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.458994
G1 F11043.216
M204 S8000
G1 X147.178 Y156.996 E.00792
G1 X146.771 Y156.996 E.01583
G1 X146.771 Y163.004 E.23338
G1 X147.178 Y163.004 E.01583
G1 X147.178 Y157.26 E.22313
; COOLING_NODE: 1
; WIPE_START
G1 X147.178 Y159.26 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.311 Y162.592 Z8.04 F60000
G1 X138.632 Y163.407 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.419 Y163.407 E.0461
G1 X137.419 Y156.593 E.25885
G1 X138.632 Y156.593 E.0461
G1 X138.632 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.016 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.035 Y163.79 E.06958
G1 X137.035 Y156.21 E.2663
G1 X139.016 Y156.21 E.06958
G1 X139.016 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.035 Y163.79 E-.75292
G1 X137.035 Y163.771 E-.00709
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.229 Y157.2 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.458994
G1 F11043.216
M204 S8000
G1 X138.229 Y156.996 E.00792
G1 X137.822 Y156.996 E.01583
G1 X137.822 Y163.004 E.23338
G1 X138.229 Y163.004 E.01583
G1 X138.229 Y157.26 E.22313
; CHANGE_LAYER
; Z_HEIGHT: 7.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11043.216
G1 X138.229 Y159.26 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 33/47
; update layer progress
M73 L33
M991 S0 P32 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z8.04 I.067 J1.215 P1  F60000
G1 X186.257 Y156.593 Z8.04
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.475 Y156.593 E.04628
G1 X187.475 Y163.407 E.25885
G1 X186.257 Y163.407 E.04628
G1 X186.257 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.874 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.859 Y156.21 E.06974
G1 X187.859 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.874 Y163.79 E.06974
G1 X185.874 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.859 Y156.21 E-.75471
G1 X187.859 Y156.224 E-.00529
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.661 Y163.002 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.461354
G1 F10979.627
M204 S8000
G1 X187.071 Y163.002 E.01602
G1 X187.071 Y156.998 E.23464
G1 X186.661 Y156.998 E.01602
G1 X186.661 Y162.942 E.23229
; COOLING_NODE: 6
; WIPE_START
G1 X186.661 Y160.942 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.292 Y162.93 Z8.28 F60000
G1 X177.525 Y163.407 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.525 Y156.593 E.25885
G1 X178.743 Y156.593 E.04628
G1 X178.743 Y163.407 E.25885
G1 X177.585 Y163.407 E.044
; COOLING_NODE: 6
M204 S250
G1 X177.141 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.141 Y156.21 E.2663
G1 X179.126 Y156.21 E.06974
G1 X179.126 Y163.79 E.2663
G1 X177.201 Y163.79 E.06764
; WIPE_START
M204 S8000
G1 X177.185 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.929 Y163.002 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.461354
G1 F10979.627
M204 S8000
G1 X178.339 Y163.002 E.01602
G1 X178.339 Y156.998 E.23464
G1 X177.929 Y156.998 E.01602
G1 X177.929 Y162.942 E.23229
; COOLING_NODE: 3
; WIPE_START
G1 X177.929 Y160.942 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.502 Y162.701 Z8.28 F60000
G1 X167.525 Y163.407 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.307 Y163.407 E.04627
G1 X166.307 Y156.593 E.25885
G1 X167.525 Y156.593 E.04627
G1 X167.525 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.909 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.924 Y163.79 E.06974
G1 X165.924 Y156.21 E.2663
G1 X167.909 Y156.21 E.06974
G1 X167.909 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.924 Y163.79 E-.75463
G1 X165.924 Y163.776 E-.00537
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.711 Y163.002 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.461244
G1 F10982.575
M204 S8000
G1 X167.121 Y163.002 E.01601
G1 X167.121 Y156.998 E.23458
G1 X166.711 Y156.998 E.01601
G1 X166.711 Y162.942 E.23223
; COOLING_NODE: 3
; WIPE_START
G1 X166.711 Y160.942 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.002 Y157.304 Z8.28 F60000
G1 X158.693 Y156.593 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.693 Y163.407 E.25885
G1 X157.475 Y163.407 E.04627
G1 X157.475 Y156.593 E.25885
G1 X158.633 Y156.593 E.04399
; COOLING_NODE: 3
M204 S250
G1 X159.076 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.076 Y163.79 E.2663
G1 X157.091 Y163.79 E.06974
G1 X157.091 Y156.21 E.2663
G1 X159.016 Y156.21 E.06763
; WIPE_START
M204 S8000
G1 X159.032 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
M73 P89 R1
G1 X158.289 Y157.202 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.461254
G1 F10982.307
M204 S8000
G1 X158.289 Y156.998 E.008
G1 X157.879 Y156.998 E.01601
G1 X157.879 Y163.002 E.23458
G1 X158.289 Y163.002 E.01601
G1 X158.289 Y157.262 E.22424
; COOLING_NODE: 1
; WIPE_START
G1 X158.289 Y159.262 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.17 Y162.016 Z8.28 F60000
G1 X147.575 Y163.407 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.358 Y163.407 E.04627
G1 X146.358 Y156.593 E.25885
G1 X147.575 Y156.593 E.04627
G1 X147.575 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.959 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.974 Y163.79 E.06973
G1 X145.974 Y156.21 E.2663
G1 X147.959 Y156.21 E.06973
G1 X147.959 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.974 Y163.79 E-.75455
G1 X145.974 Y163.776 E-.00546
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.171 Y157.202 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.461144
G1 F10985.256
M204 S8000
G1 X147.171 Y156.998 E.008
G1 X146.762 Y156.998 E.016
G1 X146.762 Y163.002 E.23452
G1 X147.171 Y163.002 E.016
G1 X147.171 Y157.262 E.22418
; COOLING_NODE: 1
; WIPE_START
G1 X147.171 Y159.262 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.306 Y162.598 Z8.28 F60000
G1 X138.642 Y163.407 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.425 Y163.407 E.04627
G1 X137.425 Y156.593 E.25885
G1 X138.642 Y156.593 E.04627
G1 X138.642 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.026 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.041 Y163.79 E.06973
G1 X137.041 Y156.21 E.2663
G1 X139.026 Y156.21 E.06973
G1 X139.026 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.041 Y163.79 E-.75455
G1 X137.041 Y163.776 E-.00546
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.238 Y157.202 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.461144
G1 F10985.256
M204 S8000
G1 X138.238 Y156.998 E.008
G1 X137.829 Y156.998 E.016
G1 X137.829 Y163.002 E.23452
G1 X138.238 Y163.002 E.016
G1 X138.238 Y157.262 E.22418
; CHANGE_LAYER
; Z_HEIGHT: 8.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10985.256
G1 X138.238 Y159.262 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 34/47
; update layer progress
M73 L34
M991 S0 P33 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z8.28 I.068 J1.215 P1  F60000
G1 X186.228 Y156.593 Z8.28
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.458 Y156.593 E.04674
G1 X187.458 Y163.407 E.25885
G1 X186.228 Y163.407 E.04674
G1 X186.228 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.845 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.842 Y156.21 E.07017
G1 X187.842 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.845 Y163.79 E.07017
G1 X185.845 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.842 Y156.21 E-.75931
G1 X187.842 Y156.212 E-.00069
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.635 Y162.999 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.467404
G1 F10819.909
M204 S8000
G1 X187.051 Y162.999 E.01649
G1 X187.051 Y157.001 E.23786
G1 X186.635 Y157.001 E.01649
G1 X186.635 Y162.939 E.23548
; COOLING_NODE: 6
; WIPE_START
G1 X186.635 Y160.939 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.269 Y162.938 Z8.52 F60000
G1 X177.542 Y163.407 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.542 Y156.593 E.25885
G1 X178.772 Y156.593 E.04674
G1 X178.772 Y163.407 E.25885
G1 X177.602 Y163.407 E.04446
; COOLING_NODE: 6
M204 S250
G1 X177.158 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.158 Y156.21 E.2663
G1 X179.155 Y156.21 E.07017
G1 X179.155 Y163.79 E.2663
G1 X177.218 Y163.79 E.06806
; WIPE_START
M204 S8000
G1 X177.202 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.949 Y162.999 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.467404
G1 F10819.909
M204 S8000
G1 X178.365 Y162.999 E.01649
G1 X178.365 Y157.001 E.23786
G1 X177.949 Y157.001 E.01649
G1 X177.949 Y162.939 E.23548
; COOLING_NODE: 3
; WIPE_START
G1 X177.949 Y160.939 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.521 Y162.695 Z8.52 F60000
G1 X167.509 Y163.407 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.279 Y163.407 E.04673
G1 X166.279 Y156.593 E.25885
G1 X167.509 Y156.593 E.04673
G1 X167.509 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.892 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.895 Y163.79 E.07015
G1 X165.895 Y156.21 E.2663
G1 X167.892 Y156.21 E.07015
G1 X167.892 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.895 Y163.79 E-.75915
G1 X165.895 Y163.788 E-.00085
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.686 Y162.999 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.467204
G1 F10825.115
M204 S8000
G1 X167.101 Y162.999 E.01648
G1 X167.101 Y157.001 E.23775
G1 X166.686 Y157.001 E.01648
G1 X166.686 Y162.939 E.23538
; COOLING_NODE: 3
; WIPE_START
G1 X166.686 Y160.939 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.986 Y157.283 Z8.52 F60000
G1 X158.721 Y156.593 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.721 Y163.407 E.25885
G1 X157.491 Y163.407 E.04673
G1 X157.491 Y156.593 E.25885
G1 X158.661 Y156.593 E.04445
; COOLING_NODE: 3
M204 S250
G1 X159.105 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.105 Y163.79 E.2663
G1 X157.108 Y163.79 E.07015
G1 X157.108 Y156.21 E.2663
G1 X159.045 Y156.21 E.06805
; WIPE_START
M204 S8000
G1 X159.061 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.314 Y157.208 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.467204
G1 F10825.115
M204 S8000
G1 X158.314 Y157.001 E.00824
G1 X157.899 Y157.001 E.01648
G1 X157.899 Y162.999 E.23775
G1 X158.314 Y162.999 E.01648
G1 X158.314 Y157.268 E.22714
; COOLING_NODE: 1
; WIPE_START
G1 X158.314 Y159.268 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.191 Y162.009 Z8.52 F60000
G1 X147.559 Y163.407 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.329 Y163.407 E.04671
G1 X146.329 Y156.593 E.25885
G1 X147.559 Y156.593 E.04671
G1 X147.559 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.942 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.946 Y163.79 E.07014
G1 X145.946 Y156.21 E.2663
G1 X147.942 Y156.21 E.07014
G1 X147.942 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.946 Y163.79 E-.759
G1 X145.946 Y163.787 E-.001
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.152 Y157.208 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.467004
G1 F10830.326
M204 S8000
G1 X147.152 Y157 E.00823
G1 X146.736 Y157 E.01646
G1 X146.736 Y163 E.23765
G1 X147.152 Y163 E.01646
G1 X147.152 Y157.268 E.22704
; COOLING_NODE: 1
; WIPE_START
G1 X147.152 Y159.268 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.292 Y162.615 Z8.52 F60000
G1 X138.671 Y163.407 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.441 Y163.407 E.04671
G1 X137.441 Y156.593 E.25885
G1 X138.671 Y156.593 E.04671
G1 X138.671 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.054 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.058 Y163.79 E.07014
G1 X137.058 Y156.21 E.2663
G1 X139.054 Y156.21 E.07014
G1 X139.054 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.058 Y163.79 E-.759
G1 X137.058 Y163.787 E-.001
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.264 Y157.208 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.466994
G1 F10830.586
M204 S8000
G1 X138.264 Y157 E.00823
G1 X137.848 Y157 E.01646
G1 X137.848 Y163 E.23764
G1 X138.264 Y163 E.01646
G1 X138.264 Y157.268 E.22704
; CHANGE_LAYER
; Z_HEIGHT: 8.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10830.586
G1 X138.264 Y159.268 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 35/47
; update layer progress
M73 L35
M991 S0 P34 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z8.52 I.068 J1.215 P1  F60000
G1 X186.18 Y156.593 Z8.52
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.431 Y156.593 E.04753
G1 X187.431 Y163.407 E.25885
G1 X186.18 Y163.407 E.04753
G1 X186.18 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.804 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.815 Y156.21 E.07065
G1 X187.815 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.804 Y163.79 E.07065
G1 X185.797 Y163.79 E.00024
G1 X185.797 Y156.263 E.26444
; WIPE_START
M204 S8000
G1 X187.796 Y156.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.593 Y162.994 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.477744
G1 F10557.433
M204 S8000
M73 P90 R1
G1 X187.019 Y162.994 E.01732
G1 X187.019 Y157.006 E.24335
G1 X186.593 Y157.006 E.01732
G1 X186.593 Y162.934 E.24091
; COOLING_NODE: 6
; WIPE_START
G1 X186.593 Y160.934 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.231 Y162.951 Z8.76 F60000
G1 X177.569 Y163.407 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.569 Y156.593 E.25885
G1 X178.82 Y156.593 E.04753
G1 X178.82 Y163.407 E.25885
G1 X177.629 Y163.407 E.04525
; COOLING_NODE: 6
M204 S250
G1 X177.185 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.185 Y156.21 E.2663
G1 X179.196 Y156.21 E.07065
G1 X179.203 Y156.21 E.00024
G1 X179.203 Y163.79 E.2663
G1 X179.196 Y163.79 E.00024
G1 X177.245 Y163.79 E.06854
; WIPE_START
M204 S8000
G1 X177.23 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.981 Y162.994 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.477744
G1 F10557.433
M204 S8000
G1 X178.407 Y162.994 E.01732
G1 X178.407 Y157.006 E.24335
G1 X177.981 Y157.006 E.01732
G1 X177.981 Y162.934 E.24091
; COOLING_NODE: 3
; WIPE_START
G1 X177.981 Y160.934 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.552 Y162.684 Z8.76 F60000
G1 X167.482 Y163.407 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.232 Y163.407 E.04748
G1 X166.232 Y156.593 E.25885
G1 X167.482 Y156.593 E.04748
G1 X167.482 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.865 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.854 Y163.79 E.07065
G1 X165.848 Y163.79 E.00021
G1 X165.848 Y156.21 E.2663
G1 X165.854 Y156.21 E.00021
G1 X167.865 Y156.21 E.07065
G1 X167.865 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.866 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.644 Y162.994 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.477154
G1 F10572.066
M204 S8000
G1 X167.069 Y162.994 E.01727
G1 X167.069 Y157.006 E.24304
G1 X166.644 Y157.006 E.01727
G1 X166.644 Y162.934 E.24061
; COOLING_NODE: 3
; WIPE_START
G1 X166.644 Y160.934 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.96 Y157.25 Z8.76 F60000
G1 X158.768 Y156.593 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.768 Y163.407 E.25885
G1 X157.518 Y163.407 E.04748
G1 X157.518 Y156.593 E.25885
G1 X158.708 Y156.593 E.0452
; COOLING_NODE: 3
M204 S250
G1 X159.146 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.152 Y156.21 E.00021
G1 X159.152 Y163.79 E.2663
G1 X159.146 Y163.79 E.00021
G1 X157.135 Y163.79 E.07065
G1 X157.135 Y156.21 E.2663
G1 X159.086 Y156.21 E.06854
; WIPE_START
M204 S8000
G1 X159.152 Y156.21 E-.02505
G1 X159.152 Y158.144 E-.73495
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.356 Y157.218 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.477154
G1 F10572.066
M204 S8000
G1 X158.356 Y157.006 E.00864
G1 X157.931 Y157.006 E.01727
G1 X157.931 Y162.994 E.24304
G1 X158.356 Y162.994 E.01727
G1 X158.356 Y157.278 E.23197
; COOLING_NODE: 1
; WIPE_START
G1 X158.356 Y159.278 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.225 Y161.998 Z8.76 F60000
G1 X147.532 Y163.407 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.283 Y163.407 E.04744
G1 X146.283 Y156.593 E.25885
G1 X147.532 Y156.593 E.04744
G1 X147.532 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.915 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.905 Y163.79 E.07064
G1 X145.9 Y163.79 E.00017
G1 X145.9 Y156.21 E.2663
G1 X145.905 Y156.21 E.00017
G1 X147.915 Y156.21 E.07064
G1 X147.915 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.916 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.12 Y157.218 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.476564
G1 F10586.741
M204 S8000
G1 X147.12 Y157.005 E.00861
G1 X146.695 Y157.005 E.01723
G1 X146.695 Y162.995 E.24273
G1 X147.12 Y162.995 E.01723
G1 X147.12 Y157.278 E.23168
; COOLING_NODE: 1
; WIPE_START
G1 X147.12 Y159.278 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.27 Y162.643 Z8.76 F60000
G1 X138.717 Y163.407 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.468 Y163.407 E.04744
G1 X137.468 Y156.593 E.25885
G1 X138.717 Y156.593 E.04744
G1 X138.717 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.095 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.085 Y163.79 E.07064
G1 X137.085 Y156.21 E.2663
G1 X139.095 Y156.21 E.07064
G1 X139.1 Y156.21 E.00017
G1 X139.1 Y163.735 E.26437
; WIPE_START
M204 S8000
G1 X137.101 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.305 Y157.218 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.476564
G1 F10586.741
M204 S8000
G1 X138.305 Y157.005 E.00861
G1 X137.88 Y157.005 E.01723
G1 X137.88 Y162.995 E.24273
G1 X138.305 Y162.995 E.01723
G1 X138.305 Y157.278 E.23168
; CHANGE_LAYER
; Z_HEIGHT: 8.6
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F10586.741
G1 X138.305 Y159.278 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 36/47
; update layer progress
M73 L36
M991 S0 P35 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z8.76 I.068 J1.215 P1  F60000
G1 X186.113 Y156.593 Z8.76
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.393 Y156.593 E.04865
G1 X187.393 Y163.407 E.25885
G1 X186.113 Y163.407 E.04865
G1 X186.113 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.756 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.777 Y156.21 E.07101
G1 X187.777 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.756 Y163.79 E.07101
G1 X185.73 Y163.79 E.00092
G1 X185.73 Y156.244 E.26512
; WIPE_START
M204 S8000
G1 X187.729 Y156.211 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.533 Y162.987 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.492444
G1 F10205.471
M204 S8000
G1 X186.974 Y162.987 E.01854
G1 X186.974 Y157.013 E.25113
G1 X186.533 Y157.013 E.01854
G1 X186.533 Y162.927 E.24861
; COOLING_NODE: 6
; WIPE_START
G1 X186.533 Y160.927 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.179 Y162.97 Z9 F60000
G1 X177.607 Y163.407 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.607 Y156.593 E.25885
G1 X178.887 Y156.593 E.04865
G1 X178.887 Y163.407 E.25885
G1 X177.667 Y163.407 E.04637
; COOLING_NODE: 6
M204 S250
G1 X177.223 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.223 Y156.21 E.2663
G1 X179.244 Y156.21 E.07101
G1 X179.27 Y156.21 E.00092
G1 X179.27 Y163.79 E.2663
G1 X179.244 Y163.79 E.00092
G1 X177.283 Y163.79 E.0689
; WIPE_START
M204 S8000
G1 X177.267 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.026 Y162.987 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.492444
G1 F10205.471
M204 S8000
G1 X178.467 Y162.987 E.01854
G1 X178.467 Y157.013 E.25113
G1 X178.026 Y157.013 E.01854
G1 X178.026 Y162.927 E.24861
; COOLING_NODE: 3
; WIPE_START
G1 X178.026 Y160.927 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.595 Y162.668 Z9 F60000
G1 X167.444 Y163.407 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.165 Y163.407 E.04859
G1 X166.165 Y156.593 E.25885
G1 X167.444 Y156.593 E.04859
G1 X167.444 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.828 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.807 Y163.79 E.07098
G1 X165.782 Y163.79 E.00089
G1 X165.782 Y156.21 E.2663
G1 X165.807 Y156.21 E.00089
G1 X167.828 Y156.21 E.07098
G1 X167.828 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.828 Y163.789 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.585 Y162.987 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.491674
G1 F10223.324
M204 S8000
G1 X167.025 Y162.987 E.01847
G1 X167.025 Y157.013 E.25072
G1 X166.585 Y157.013 E.01847
G1 X166.585 Y162.927 E.2482
; COOLING_NODE: 3
; WIPE_START
G1 X166.585 Y160.927 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.923 Y157.202 Z9 F60000
G1 X158.835 Y156.593 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.835 Y163.407 E.25885
G1 X157.556 Y163.407 E.04859
G1 X157.556 Y156.593 E.25885
G1 X158.775 Y156.593 E.04631
; COOLING_NODE: 3
M204 S250
G1 X159.193 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.218 Y156.21 E.00089
G1 X159.218 Y163.79 E.2663
G1 X159.193 Y163.79 E.00089
G1 X157.172 Y163.79 E.07098
G1 X157.172 Y156.21 E.2663
G1 X159.133 Y156.21 E.06887
; WIPE_START
M204 S8000
G1 X159.218 Y156.21 E-.03247
G1 X159.218 Y158.125 E-.72753
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.415 Y157.233 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.491674
G1 F10223.324
M204 S8000
G1 X158.415 Y157.013 E.00924
G1 X157.975 Y157.013 E.01847
G1 X157.975 Y162.987 E.25072
G1 X158.415 Y162.987 E.01847
G1 X158.415 Y157.293 E.23897
; COOLING_NODE: 1
; WIPE_START
G1 X158.415 Y159.293 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.273 Y161.983 Z9 F60000
G1 X147.495 Y163.407 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
M73 P91 R1
G1 X146.217 Y163.407 E.04853
G1 X146.217 Y156.593 E.25885
G1 X147.495 Y156.593 E.04853
G1 X147.495 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.878 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.859 Y163.79 E.07095
G1 X145.834 Y163.79 E.00087
G1 X145.834 Y156.21 E.2663
G1 X145.859 Y156.21 E.00087
G1 X147.878 Y156.21 E.07095
G1 X147.878 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.879 Y163.789 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.076 Y157.232 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.490894
G1 F10241.472
M204 S8000
G1 X147.076 Y157.012 E.0092
G1 X146.636 Y157.012 E.01841
G1 X146.636 Y162.988 E.25031
G1 X147.076 Y162.988 E.01841
G1 X147.076 Y157.292 E.23859
; COOLING_NODE: 1
; WIPE_START
G1 X147.076 Y159.292 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.239 Y162.684 Z9 F60000
G1 X138.782 Y163.407 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.505 Y163.407 E.04853
G1 X137.505 Y156.593 E.25885
G1 X138.782 Y156.593 E.04853
G1 X138.782 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.141 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.122 Y163.79 E.07095
G1 X137.122 Y156.21 E.2663
G1 X139.141 Y156.21 E.07095
G1 X139.166 Y156.21 E.00087
G1 X139.166 Y163.755 E.26507
; WIPE_START
M204 S8000
G1 X137.166 Y163.789 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.364 Y157.232 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.490894
G1 F10241.472
M204 S8000
G1 X138.364 Y157.012 E.0092
G1 X137.924 Y157.012 E.01841
G1 X137.924 Y162.988 E.25031
G1 X138.364 Y162.988 E.01841
G1 X138.364 Y157.292 E.23859
; CHANGE_LAYER
; Z_HEIGHT: 8.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10241.472
G1 X138.364 Y159.292 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 37/47
; update layer progress
M73 L37
M991 S0 P36 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z9 I.069 J1.215 P1  F60000
G1 X186.024 Y156.593 Z9
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.345 Y156.593 E.0502
G1 X187.345 Y163.407 E.25885
G1 X186.024 Y163.407 E.0502
G1 X186.024 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.689 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.728 Y156.21 E.07167
G1 X187.728 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X186.489 Y163.79 E.04356
G1 X186.089 Y163.79 E.01405
G1 F11458.794
G1 X185.689 Y163.79 E.01405
G1 F10170.518
G1 X185.64 Y163.79 E.0017
G1 F10020
G1 X185.64 Y156.222 E.2659
; WIPE_START
M204 S8000
G1 X187.64 Y156.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.454 Y162.977 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.512874
G1 F9753.561
M204 S8000
G1 X186.915 Y162.977 E.02029
G1 X186.915 Y157.023 E.26186
G1 X186.454 Y157.023 E.02029
G1 X186.454 Y162.917 E.25923
; COOLING_NODE: 6
; WIPE_START
G1 X186.454 Y160.917 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.11 Y162.995 Z9.24 F60000
G1 X177.655 Y163.407 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.655 Y156.593 E.25885
G1 X178.976 Y156.593 E.0502
G1 X178.976 Y163.407 E.25885
G1 X177.715 Y163.407 E.04792
; COOLING_NODE: 6
M204 S250
G1 X177.272 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.272 Y156.21 E.2663
G1 X178.511 Y156.21 E.04356
G1 X178.911 Y156.21 E.01405
G1 F11458.828
G1 X179.311 Y156.21 E.01405
G1 F10170.549
G1 X179.36 Y156.21 E.0017
G1 F10020
G1 X179.36 Y163.79 E.2663
G1 F10170.549
G1 X179.311 Y163.79 E.0017
G1 F11458.828
G1 X178.911 Y163.79 E.01405
G1 F12000
G1 X178.511 Y163.79 E.01405
G1 X177.332 Y163.79 E.04145
; WIPE_START
M204 S8000
G1 X177.316 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.085 Y162.977 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.512874
G1 F9753.561
M204 S8000
G1 X178.546 Y162.977 E.02029
G1 X178.546 Y157.023 E.26186
G1 X178.085 Y157.023 E.02029
G1 X178.085 Y162.917 E.25923
; COOLING_NODE: 3
; WIPE_START
G1 X178.085 Y160.917 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.652 Y162.648 Z9.24 F60000
G1 X167.396 Y163.407 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.078 Y163.407 E.05008
G1 X166.078 Y156.593 E.25885
G1 X167.396 Y156.593 E.05008
G1 X167.396 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.78 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X166.141 Y163.79 E.05757
G1 X165.741 Y163.79 E.01405
G1 F11161.564
G1 X165.694 Y163.79 E.00163
G1 F11010
G1 X165.694 Y156.21 E.2663
G1 F11161.564
G1 X165.741 Y156.21 E.00163
G1 F12000
G1 X166.141 Y156.21 E.01405
G1 X167.78 Y156.21 E.05757
G1 X167.78 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X166.141 Y163.79 E-.62315
G1 X165.781 Y163.79 E-.13685
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.507 Y162.977 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.511384
G1 F9785.162
M204 S8000
G1 X166.967 Y162.977 E.02016
G1 X166.967 Y157.023 E.26108
G1 X166.507 Y157.023 E.02016
G1 X166.507 Y162.917 E.25845
; COOLING_NODE: 3
; WIPE_START
G1 X166.507 Y160.917 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.876 Y157.137 Z9.24 F60000
G1 X158.922 Y156.593 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.922 Y163.407 E.25885
G1 X157.604 Y163.407 E.05008
G1 X157.604 Y156.593 E.25885
G1 X158.862 Y156.593 E.0478
; COOLING_NODE: 3
M204 S250
G1 X159.259 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11161.564
M204 S5000
G1 X159.306 Y156.21 E.00163
G1 F11010
G1 X159.306 Y163.79 E.2663
G1 F11161.564
G1 X159.259 Y163.79 E.00163
G1 F12000
G1 X158.859 Y163.79 E.01405
G1 X157.22 Y163.79 E.05757
G1 X157.22 Y156.21 E.2663
G1 X159.199 Y156.21 E.06952
; WIPE_START
M204 S8000
G1 X159.306 Y156.21 E-.04045
G1 X159.306 Y158.104 E-.71955
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.493 Y157.253 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.511384
G1 F9785.162
M204 S8000
G1 X158.493 Y157.023 E.01008
G1 X158.033 Y157.023 E.02016
G1 X158.033 Y162.977 E.26108
G1 X158.493 Y162.977 E.02016
G1 X158.493 Y157.313 E.24837
; COOLING_NODE: 1
; WIPE_START
G1 X158.493 Y159.313 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.336 Y161.965 Z9.24 F60000
G1 X147.447 Y163.407 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.132 Y163.407 E.04997
G1 X146.132 Y156.593 E.25885
G1 X147.447 Y156.593 E.04997
G1 X147.447 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.831 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X146.193 Y163.79 E.05754
G1 X145.793 Y163.79 E.01405
G1 F11155.345
G1 X145.748 Y163.79 E.00157
G1 F11010
G1 X145.748 Y156.21 E.2663
G1 F11155.345
G1 X145.793 Y156.21 E.00157
G1 F12000
G1 X146.193 Y156.21 E.01405
G1 X147.831 Y156.21 E.05754
G1 X147.831 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X146.193 Y163.79 E-.62273
G1 X145.832 Y163.79 E-.13727
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.019 Y157.251 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.509884
G1 F9817.183
M204 S8000
G1 X147.019 Y157.022 E.01002
G1 X146.56 Y157.022 E.02003
G1 X146.56 Y162.978 E.2603
G1 X147.019 Y162.978 E.02003
G1 X147.019 Y157.311 E.24766
; COOLING_NODE: 1
; WIPE_START
G1 X147.019 Y159.311 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.199 Y162.738 Z9.24 F60000
G1 X138.868 Y163.407 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.553 Y163.407 E.04997
G1 X137.553 Y156.593 E.25885
G1 X138.868 Y156.593 E.04997
G1 X138.868 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.207 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.169 Y163.79 E.07159
G1 X137.169 Y156.21 E.2663
G1 X138.807 Y156.21 E.05754
G1 X139.207 Y156.21 E.01405
G1 F11155.345
G1 X139.252 Y156.21 E.00157
G1 F11010
G1 X139.252 Y163.775 E.26576
; WIPE_START
M204 S8000
G1 X137.252 Y163.789 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.44 Y157.251 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.509894
G1 F9816.968
M204 S8000
G1 X138.44 Y157.022 E.01002
G1 X137.981 Y157.022 E.02003
G1 X137.981 Y162.978 E.2603
G1 X138.44 Y162.978 E.02003
G1 X138.44 Y157.311 E.24767
; CHANGE_LAYER
; Z_HEIGHT: 9.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9816.968
G1 X138.44 Y159.311 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 38/47
; update layer progress
M73 L38
M991 S0 P37 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z9.24 I.07 J1.215 P1  F60000
G1 X185.912 Y156.593 Z9.24
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.285 Y156.593 E.05217
G1 X187.285 Y163.407 E.25885
G1 X185.912 Y163.407 E.05217
G1 X185.912 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.599 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.669 Y156.21 E.07271
G1 X187.669 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X187.199 Y163.79 E.0165
G1 F10758.74
G1 X186.799 Y163.79 E.01405
G1 F9511.628
G1 X186.399 Y163.79 E.01405
G1 F8341.315
G1 X185.999 Y163.79 E.01405
G1 F7247.803
G1 X185.599 Y163.79 E.01405
G1 F6231.09
G1 X185.529 Y163.79 E.00247
G1 F6060
G1 X185.529 Y156.21 E.2663
G1 F6085.207
G1 X185.539 Y156.21 E.00037
; WIPE_START
M204 S8000
G1 X187.539 Y156.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.355 Y162.964 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.538814
G1 F9234.369
M204 S8000
G1 X186.842 Y162.964 E.02264
G1 X186.842 Y157.036 E.27538
G1 X186.355 Y157.036 E.02264
G1 X186.355 Y162.904 E.2726
; COOLING_NODE: 6
; WIPE_START
G1 X186.355 Y160.904 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.024 Y163.027 Z9.48 F60000
G1 X177.715 Y163.407 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.715 Y156.593 E.25885
G1 X179.088 Y156.593 E.05217
G1 X179.088 Y163.407 E.25885
G1 X177.775 Y163.407 E.04989
; COOLING_NODE: 6
M204 S250
M73 P92 R1
G1 X177.331 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.331 Y156.21 E.2663
G1 X177.801 Y156.21 E.0165
G1 F10758.772
G1 X178.201 Y156.21 E.01405
G1 F9511.658
G1 X178.601 Y156.21 E.01405
G1 F8341.343
G1 X179.001 Y156.21 E.01405
G1 F7247.829
G1 X179.401 Y156.21 E.01405
G1 F6231.114
G1 X179.471 Y156.21 E.00248
G1 F6060
G1 X179.471 Y163.79 E.2663
G1 F6231.114
G1 X179.401 Y163.79 E.00248
G1 F7247.829
G1 X179.001 Y163.79 E.01405
G1 F8341.343
G1 X178.601 Y163.79 E.01405
G1 F9511.658
G1 X178.201 Y163.79 E.01405
G1 F10758.772
G1 X177.801 Y163.79 E.01405
G1 F12000
G1 X177.391 Y163.79 E.01439
; WIPE_START
M204 S8000
G1 X177.375 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.158 Y162.964 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.538814
G1 F9234.369
M204 S8000
G1 X178.645 Y162.964 E.02264
G1 X178.645 Y157.036 E.27538
G1 X178.158 Y157.036 E.02264
G1 X178.158 Y162.904 E.2726
; COOLING_NODE: 3
; WIPE_START
G1 X178.158 Y160.904 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.721 Y162.624 Z9.48 F60000
G1 X167.337 Y163.407 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.969 Y163.407 E.05198
G1 X165.969 Y156.593 E.25885
G1 X167.337 Y156.593 E.05198
G1 X167.337 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.721 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.253 Y163.79 E.01642
G1 X166.853 Y163.79 E.01405
G1 F10733.986
G1 X166.453 Y163.79 E.01405
G1 F9488.353
G1 X166.053 Y163.79 E.01405
G1 F8319.52
G1 X165.653 Y163.79 E.01405
G1 F7227.488
G1 X165.586 Y163.79 E.00238
G1 F7050
G1 X165.586 Y156.21 E.2663
G1 F7227.488
G1 X165.653 Y156.21 E.00238
G1 F8319.52
G1 X166.053 Y156.21 E.01405
G1 F9488.353
G1 X166.453 Y156.21 E.01405
G1 F10733.986
G1 X166.853 Y156.21 E.01405
G1 F12000
G1 X167.253 Y156.21 E.01405
G1 X167.721 Y156.21 E.01642
G1 X167.721 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X167.253 Y163.79 E-.17902
G1 X166.853 Y163.79 E-.152
G1 X166.453 Y163.79 E-.152
G1 X166.053 Y163.79 E-.152
G1 X165.724 Y163.79 E-.12498
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.411 Y162.965 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.536304
G1 F9282.179
M204 S8000
G1 X166.895 Y162.965 E.02241
G1 X166.895 Y157.035 E.27408
G1 X166.411 Y157.035 E.02241
G1 X166.411 Y162.905 E.27131
; COOLING_NODE: 3
; WIPE_START
G1 X166.411 Y160.905 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.82 Y157.055 Z9.48 F60000
G1 X159.031 Y156.593 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.031 Y163.407 E.25885
G1 X157.663 Y163.407 E.05198
G1 X157.663 Y156.593 E.25885
G1 X158.971 Y156.593 E.0497
; COOLING_NODE: 3
M204 S250
G1 X159.347 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7227.488
M204 S5000
G1 X159.414 Y156.21 E.00238
G1 F7050
G1 X159.414 Y163.79 E.2663
G1 F7227.488
G1 X159.347 Y163.79 E.00238
G1 F8319.52
G1 X158.947 Y163.79 E.01405
G1 F9488.353
G1 X158.547 Y163.79 E.01405
G1 F10733.986
G1 X158.147 Y163.79 E.01405
G1 F12000
G1 X157.747 Y163.79 E.01405
G1 X157.279 Y163.79 E.01642
G1 X157.279 Y156.21 E.2663
G1 X159.287 Y156.21 E.07052
; WIPE_START
M204 S8000
G1 X159.414 Y156.21 E-.04856
G1 X159.414 Y158.082 E-.71144
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.589 Y157.278 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.536304
G1 F9282.179
M204 S8000
G1 X158.589 Y157.035 E.0112
G1 X158.105 Y157.035 E.02241
G1 X158.105 Y162.965 E.27408
G1 X158.589 Y162.965 E.02241
G1 X158.589 Y157.338 E.2601
; COOLING_NODE: 1
; WIPE_START
G1 X158.589 Y159.338 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.416 Y161.944 Z9.48 F60000
G1 X147.389 Y163.407 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.024 Y163.407 E.05183
G1 X146.024 Y156.593 E.25885
G1 X147.389 Y156.593 E.05183
G1 X147.389 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.772 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.307 Y163.79 E.01633
G1 X146.907 Y163.79 E.01405
G1 F10729.685
G1 X146.507 Y163.79 E.01405
G1 F9484.309
G1 X146.107 Y163.79 E.01405
G1 F8315.734
G1 X145.707 Y163.79 E.01405
G1 F7223.958
G1 X145.641 Y163.79 E.00233
G1 F7050
G1 X145.641 Y156.21 E.2663
G1 F7223.958
G1 X145.707 Y156.21 E.00233
G1 F8315.734
G1 X146.107 Y156.21 E.01405
G1 F9484.309
G1 X146.507 Y156.21 E.01405
G1 F10729.685
G1 X146.907 Y156.21 E.01405
G1 F12000
G1 X147.307 Y156.21 E.01405
G1 X147.772 Y156.21 E.01633
G1 X147.772 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.307 Y163.79 E-.17811
G1 X146.907 Y163.79 E-.152
G1 X146.507 Y163.79 E-.152
G1 X146.107 Y163.79 E-.152
G1 X145.776 Y163.79 E-.12589
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.948 Y157.276 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.534424
G1 F9318.314
M204 S8000
G1 X146.948 Y157.034 E.01112
G1 X146.465 Y157.034 E.02223
G1 X146.465 Y162.966 E.2731
G1 X146.948 Y162.966 E.02223
G1 X146.948 Y157.336 E.25922
; COOLING_NODE: 1
; WIPE_START
G1 X146.948 Y159.336 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.151 Y162.807 Z9.48 F60000
G1 X138.975 Y163.407 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.611 Y163.407 E.05183
G1 X137.611 Y156.593 E.25885
G1 X138.975 Y156.593 E.05183
G1 X138.975 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.293 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.228 Y163.79 E.07254
G1 X137.228 Y156.21 E.2663
G1 X137.693 Y156.21 E.01633
G1 X138.093 Y156.21 E.01405
G1 F10729.621
G1 X138.493 Y156.21 E.01405
G1 F9484.249
G1 X138.893 Y156.21 E.01405
G1 F8315.677
G1 X139.293 Y156.21 E.01405
G1 F7223.906
G1 X139.359 Y156.21 E.00233
G1 F7050
G1 X139.359 Y163.79 E.2663
G1 F7066.764
G1 X139.353 Y163.79 E.00023
; WIPE_START
M204 S8000
G1 X137.353 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.535 Y157.276 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.534424
G1 F9318.314
M204 S8000
G1 X138.535 Y157.034 E.01112
G1 X138.052 Y157.034 E.02223
G1 X138.052 Y162.966 E.2731
G1 X138.535 Y162.966 E.02223
G1 X138.535 Y157.336 E.25922
; CHANGE_LAYER
; Z_HEIGHT: 9.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9318.314
G1 X138.535 Y159.336 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 39/47
; update layer progress
M73 L39
M991 S0 P38 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z9.48 I.071 J1.215 P1  F60000
G1 X185.775 Y156.593 Z9.48
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.214 Y156.593 E.05469
G1 X187.214 Y163.407 E.25885
G1 X185.775 Y163.407 E.05469
G1 X185.775 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.488 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.598 Y156.21 E.07413
G1 X187.598 Y161.79 E.19604
G1 X187.598 Y162.19 E.01405
G1 F10982.485
G1 X187.598 Y162.59 E.01405
G1 F9722.074
G1 X187.598 Y162.99 E.01405
G1 F8538.463
G1 X187.598 Y163.39 E.01405
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 F7431.652
G1 X187.598 Y163.79 E.01405
G1 F6401.641
G1 X187.088 Y163.79 E.01792
G1 F5199.56
G1 X186.688 Y163.79 E.01405
G1 F4344.287
G1 X186.288 Y163.79 E.01405
G1 F3565.813
G1 X185.888 Y163.79 E.01405
G1 F2864.14
G1 X185.488 Y163.79 E.01405
G1 F2239.266
G1 X185.391 Y163.79 E.00339
G1 F2100
G1 X185.391 Y156.21 E.2663
G1 F2152.159
G1 X185.428 Y156.21 E.00128
; WIPE_START
M204 S8000
G1 X187.428 Y156.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.158 Y163.023 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X186.831 Y163.023 E.02363
G1 X186.831 Y156.977 E.21241
G1 X186.158 Y156.977 E.02363
G1 X186.158 Y162.963 E.2103
M204 S10000
G1 X186.495 Y162.687 F60000
; LINE_WIDTH: 0.355644
G1 F14795.818
M204 S8000
G1 X186.495 Y157.373 E.15407
; COOLING_NODE: 6
; WIPE_START
G1 X186.495 Y159.373 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.569 Y162.581 Z9.72 F60000
G1 X177.786 Y163.407 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.786 Y156.593 E.25885
G1 X179.225 Y156.593 E.05469
G1 X179.225 Y163.407 E.25885
G1 X177.846 Y163.407 E.05242
; COOLING_NODE: 6
M204 S250
G1 X177.402 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.402 Y158.21 E.19604
G1 X177.402 Y157.81 E.01405
G1 F10982.485
G1 X177.402 Y157.41 E.01405
G1 F9722.074
G1 X177.402 Y157.01 E.01405
G1 F8538.463
G1 X177.402 Y156.61 E.01405
G1 F7431.652
G1 X177.402 Y156.21 E.01405
G1 F6401.641
G1 X177.912 Y156.21 E.01792
G1 F5199.583
G1 X178.312 Y156.21 E.01405
G1 F4344.307
G1 X178.712 Y156.21 E.01405
G1 F3565.832
G1 X179.112 Y156.21 E.01405
G1 F2864.156
G1 X179.512 Y156.21 E.01405
G1 F2239.281
G1 X179.609 Y156.21 E.00339
G1 F2100
G1 X179.609 Y163.79 E.2663
G1 F2239.281
G1 X179.512 Y163.79 E.00339
G1 F2864.156
G1 X179.112 Y163.79 E.01405
G1 F3565.832
G1 X178.712 Y163.79 E.01405
G1 F4344.307
G1 X178.312 Y163.79 E.01405
G1 F5199.583
G1 X177.912 Y163.79 E.01405
G1 F6253.764
G1 X177.462 Y163.79 E.01581
; WIPE_START
M204 S8000
G1 X177.441 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.169 Y163.023 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X178.842 Y163.023 E.02363
G1 X178.842 Y156.977 E.21241
G1 X178.169 Y156.977 E.02363
G1 X178.169 Y162.963 E.2103
M204 S10000
G1 X178.505 Y162.687 F60000
; LINE_WIDTH: 0.355644
G1 F14795.818
M204 S8000
G1 X178.505 Y157.373 E.15407
; COOLING_NODE: 3
; WIPE_START
G1 X178.505 Y159.373 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.322 Y161.951 Z9.72 F60000
G1 X167.267 Y163.407 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.833 Y163.407 E.05447
G1 X165.833 Y156.593 E.25885
G1 X167.267 Y156.593 E.05447
G1 X167.267 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.65 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6386.949
M204 S5000
G1 X167.145 Y163.79 E.01777
G1 F5195.919
G1 X166.745 Y163.79 E.01405
G1 F4340.959
G1 X166.345 Y163.79 E.01405
G1 F3562.798
G1 X165.945 Y163.79 E.01405
G1 F2861.437
G1 X165.545 Y163.79 E.01405
G1 F2236.877
G1 X165.45 Y163.79 E.00333
G1 F2100
G1 X165.45 Y156.21 E.2663
G1 F2236.877
G1 X165.545 Y156.21 E.00333
G1 F2861.437
G1 X165.945 Y156.21 E.01405
G1 F3562.798
G1 X166.345 Y156.21 E.01405
G1 F4340.959
G1 X166.745 Y156.21 E.01405
G1 F5195.919
G1 X167.145 Y156.21 E.01405
G1 F6386.949
G1 X167.65 Y156.21 E.01777
G1 F7415.821
G1 X167.65 Y156.61 E.01405
G1 F8521.494
G1 X167.65 Y157.01 E.01405
G1 F9703.966
G1 X167.65 Y157.41 E.01405
G1 F10963.238
G1 X167.65 Y157.81 E.01405
G1 F12000
G1 X167.65 Y158.21 E.01405
G1 X167.65 Y163.73 E.19393
; WIPE_START
M204 S8000
G1 X167.145 Y163.79 E-.19355
G1 X166.745 Y163.79 E-.152
G1 X166.345 Y163.79 E-.152
G1 X165.945 Y163.79 E-.152
G1 X165.654 Y163.79 E-.11045
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.291 Y162.948 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.569104
G1 F8693.973
M204 S8000
G1 X166.809 Y162.948 E.02554
G1 X166.809 Y157.052 E.291
G1 X166.291 Y157.052 E.02554
G1 X166.291 Y162.888 E.28804
; COOLING_NODE: 3
; WIPE_START
G1 X166.291 Y160.888 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.755 Y156.948 Z9.72 F60000
G1 X159.167 Y156.593 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.167 Y163.407 E.25885
G1 X157.733 Y163.407 E.05447
G1 X157.733 Y156.593 E.25885
G1 X159.107 Y156.593 E.05219
; COOLING_NODE: 3
M204 S250
G1 X159.455 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2236.877
M204 S5000
G1 X159.55 Y156.21 E.00333
G1 F2100
G1 X159.55 Y163.79 E.2663
G1 F2236.877
G1 X159.455 Y163.79 E.00333
G1 F2861.437
G1 X159.055 Y163.79 E.01405
G1 F3562.798
G1 X158.655 Y163.79 E.01405
G1 F4340.959
G1 X158.255 Y163.79 E.01405
G1 F5195.919
G1 X157.855 Y163.79 E.01405
G1 F6386.949
G1 X157.35 Y163.79 E.01777
G1 F7415.821
G1 X157.35 Y163.39 E.01405
G1 F8521.494
M73 P93 R1
G1 X157.35 Y162.99 E.01405
G1 F9703.966
G1 X157.35 Y162.59 E.01405
G1 F10963.238
G1 X157.35 Y162.19 E.01405
G1 F12000
G1 X157.35 Y161.79 E.01405
G1 X157.35 Y156.21 E.19604
G1 X159.395 Y156.21 E.07187
; WIPE_START
M204 S8000
G1 X159.55 Y156.21 E-.05885
G1 X159.55 Y158.055 E-.70115
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.709 Y157.31 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.569104
G1 F8693.973
M204 S8000
M73 P93 R0
G1 X158.709 Y157.052 E.01277
G1 X158.191 Y157.052 E.02554
G1 X158.191 Y162.948 E.291
G1 X158.709 Y162.948 E.02554
G1 X158.709 Y157.37 E.27527
; COOLING_NODE: 1
; WIPE_START
G1 X158.709 Y159.37 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.515 Y161.92 Z9.72 F60000
G1 X147.319 Y163.407 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.892 Y163.407 E.05424
G1 X145.892 Y156.593 E.25885
G1 X147.319 Y156.593 E.05424
G1 X147.319 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.703 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8026.133
M204 S5000
G1 X147.2 Y163.79 E.01766
G1 F6691.234
G1 X146.8 Y163.79 E.01405
G1 F5715.843
G1 X146.4 Y163.79 E.01405
G1 F4817.251
G1 X146 Y163.79 E.01405
G1 F3995.459
G1 X145.6 Y163.79 E.01405
G1 F3250.468
G1 X145.508 Y163.79 E.00323
G1 F3090
G1 X145.508 Y156.21 E.2663
G1 F3250.468
G1 X145.6 Y156.21 E.00323
G1 F3995.459
G1 X146 Y156.21 E.01405
G1 F4817.251
G1 X146.4 Y156.21 E.01405
G1 F5715.843
G1 X146.8 Y156.21 E.01405
G1 F6691.234
G1 X147.2 Y156.21 E.01405
G1 F8026.133
G1 X147.703 Y156.21 E.01766
G1 F9174.855
G1 X147.703 Y156.61 E.01405
G1 F10400.376
G1 X147.703 Y157.01 E.01405
G1 F11702.698
G1 X147.703 Y157.41 E.01405
G1 F12000
G1 X147.703 Y157.81 E.01405
G1 X147.703 Y163.73 E.20798
; WIPE_START
M204 S8000
G1 X147.2 Y163.79 E-.1924
G1 X146.8 Y163.79 E-.152
G1 X146.4 Y163.79 E-.152
G1 X146 Y163.79 E-.152
G1 X145.706 Y163.79 E-.11159
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.863 Y157.307 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.566144
G1 F8743.977
M204 S8000
G1 X146.863 Y157.05 E.01263
G1 X146.348 Y157.05 E.02525
G1 X146.348 Y162.95 E.28949
G1 X146.863 Y162.95 E.02525
G1 X146.863 Y157.367 E.27392
; COOLING_NODE: 1
; WIPE_START
G1 X146.863 Y159.367 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.094 Y162.893 Z9.72 F60000
G1 X139.108 Y163.407 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.681 Y163.407 E.05424
G1 X137.681 Y156.593 E.25885
G1 X139.108 Y156.593 E.05424
G1 X139.108 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.4 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.297 Y163.79 E.07388
G1 X137.297 Y157.81 E.21009
G1 X137.297 Y157.41 E.01405
G1 F11702.698
G1 X137.297 Y157.01 E.01405
G1 F10400.376
G1 X137.297 Y156.61 E.01405
G1 F9174.855
G1 X137.297 Y156.21 E.01405
G1 F8026.133
G1 X137.8 Y156.21 E.01766
G1 F6691.209
G1 X138.2 Y156.21 E.01405
G1 F5715.819
G1 X138.6 Y156.21 E.01405
G1 F4817.229
G1 X139 Y156.21 E.01405
G1 F3995.44
G1 X139.4 Y156.21 E.01405
G1 F3250.45
G1 X139.492 Y156.21 E.00323
G1 F3090
G1 X139.492 Y163.79 E.2663
G1 F3145.325
G1 X139.46 Y163.79 E.00112
; WIPE_START
M204 S8000
G1 X137.46 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.652 Y157.307 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.566144
G1 F8743.977
M204 S8000
G1 X138.652 Y157.05 E.01263
G1 X138.137 Y157.05 E.02525
G1 X138.137 Y162.95 E.28949
G1 X138.652 Y162.95 E.02525
G1 X138.652 Y157.367 E.27392
; CHANGE_LAYER
; Z_HEIGHT: 9.56
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F8743.977
G1 X138.652 Y159.367 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 40/47
; update layer progress
M73 L40
M991 S0 P39 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z9.72 I.072 J1.215 P1  F60000
G1 X185.617 Y156.593 Z9.72
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.131 Y156.593 E.05753
G1 X187.131 Y163.407 E.25885
G1 X185.617 Y163.407 E.05753
G1 X185.617 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.35 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.515 Y156.21 E.07605
G1 X187.515 Y161.79 E.19604
G1 X187.515 Y162.19 E.01405
G1 F11226.475
G1 X187.515 Y162.59 E.01405
G1 F9951.716
G1 X187.515 Y162.99 E.01405
G1 F8753.757
G1 X187.515 Y163.39 E.01405
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 F7632.598
G1 X187.515 Y163.79 E.01405
G1 F6588.239
G1 X186.95 Y163.79 E.01984
G1 F5244.699
G1 X186.55 Y163.79 E.01405
G1 F4385.555
G1 X186.15 Y163.79 E.01405
G1 F3603.21
G1 X185.75 Y163.79 E.01405
G1 F2897.666
G1 X185.35 Y163.79 E.01405
G1 F2268.922
G1 X185.234 Y163.79 E.0041
G1 F2100
G1 X185.234 Y156.21 E.2663
G1 F2181.234
G1 X185.29 Y156.21 E.00199
; WIPE_START
M204 S8000
G1 X187.29 Y156.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.001 Y163.023 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X186.748 Y163.023 E.02626
G1 X186.748 Y156.977 E.21241
G1 X186.001 Y156.977 E.02626
G1 X186.001 Y162.963 E.2103
M204 S10000
G1 X186.374 Y162.649 F60000
; LINE_WIDTH: 0.430384
G1 F11877.113
M204 S8000
G1 X186.374 Y157.411 E.18924
; COOLING_NODE: 6
; WIPE_START
G1 X186.374 Y159.411 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.466 Y162.656 Z9.96 F60000
G1 X177.869 Y163.407 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.869 Y156.593 E.25885
G1 X179.383 Y156.593 E.05753
G1 X179.383 Y163.407 E.25885
G1 X177.929 Y163.407 E.05525
; COOLING_NODE: 6
M204 S250
G1 X177.485 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.485 Y158.21 E.19604
G1 X177.485 Y157.81 E.01405
G1 F11226.508
G1 X177.485 Y157.41 E.01405
G1 F9951.747
G1 X177.485 Y157.01 E.01405
G1 F8753.786
G1 X177.485 Y156.61 E.01405
G1 F7632.625
G1 X177.485 Y156.21 E.01405
G1 F6588.264
G1 X178.05 Y156.21 E.01984
G1 F5244.744
G1 X178.45 Y156.21 E.01405
G1 F4385.596
G1 X178.85 Y156.21 E.01405
G1 F3603.248
G1 X179.25 Y156.21 E.01405
G1 F2897.699
G1 X179.65 Y156.21 E.01405
G1 F2268.951
G1 X179.766 Y156.21 E.0041
G1 F2100
G1 X179.766 Y163.79 E.2663
G1 F2268.951
G1 X179.65 Y163.79 E.0041
G1 F2897.699
G1 X179.25 Y163.79 E.01405
G1 F3603.248
G1 X178.85 Y163.79 E.01405
G1 F4385.596
G1 X178.45 Y163.79 E.01405
G1 F5244.744
G1 X178.05 Y163.79 E.01405
G1 F6438.234
G1 X177.545 Y163.79 E.01773
; WIPE_START
M204 S8000
G1 X177.524 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.252 Y163.023 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X178.999 Y163.023 E.02626
G1 X178.999 Y156.977 E.21241
G1 X178.252 Y156.977 E.02626
G1 X178.252 Y162.963 E.2103
M204 S10000
G1 X178.626 Y162.649 F60000
; LINE_WIDTH: 0.430404
G1 F11876.485
M204 S8000
G1 X178.626 Y157.411 E.18925
; COOLING_NODE: 3
; WIPE_START
G1 X178.626 Y159.411 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.42 Y161.927 Z9.96 F60000
G1 X167.185 Y163.407 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.675 Y163.407 E.05735
G1 X165.675 Y156.593 E.25885
G1 X167.185 Y156.593 E.05735
G1 X167.185 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.568 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6575.897
M204 S5000
G1 X167.009 Y163.79 E.01966
G1 F5245.036
G1 X166.609 Y163.79 E.01405
G1 F4385.863
G1 X166.209 Y163.79 E.01405
G1 F3603.489
G1 X165.809 Y163.79 E.01405
G1 F2897.916
G1 X165.409 Y163.79 E.01405
G1 F2269.143
G1 X165.292 Y163.79 E.0041
G1 F2100
G1 X165.292 Y156.21 E.2663
G1 F2269.143
G1 X165.409 Y156.21 E.0041
G1 F2897.916
G1 X165.809 Y156.21 E.01405
G1 F3603.489
G1 X166.209 Y156.21 E.01405
G1 F4385.863
G1 X166.609 Y156.21 E.01405
G1 F5245.036
G1 X167.009 Y156.21 E.01405
G1 F6575.897
G1 X167.568 Y156.21 E.01966
G1 F7619.313
G1 X167.568 Y156.61 E.01405
G1 F8739.529
G1 X167.568 Y157.01 E.01405
G1 F9936.546
G1 X167.568 Y157.41 E.01405
G1 F11210.362
G1 X167.568 Y157.81 E.01405
G1 F12000
G1 X167.568 Y158.21 E.01405
G1 X167.568 Y163.73 E.19393
; WIPE_START
M204 S8000
G1 X167.009 Y163.79 E-.21387
G1 X166.609 Y163.79 E-.152
G1 X166.209 Y163.79 E-.152
G1 X165.809 Y163.79 E-.152
G1 X165.571 Y163.79 E-.09014
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.059 Y163.023 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.801 Y163.023 E.02608
G1 X166.801 Y156.977 E.21241
G1 X166.059 Y156.977 E.02608
G1 X166.059 Y162.963 E.2103
M204 S10000
G1 X166.43 Y162.652 F60000
; LINE_WIDTH: 0.425464
G1 F12033.373
M204 S8000
G1 X166.43 Y157.408 E.18695
; COOLING_NODE: 3
; WIPE_START
G1 X166.43 Y159.408 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y156.597 Z9.96 F60000
G1 X159.325 Y156.593 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.325 Y163.407 E.25885
G1 X157.815 Y163.407 E.05735
G1 X157.815 Y156.593 E.25885
G1 X159.265 Y156.593 E.05507
; COOLING_NODE: 3
M204 S250
G1 X159.591 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2269.143
M204 S5000
G1 X159.708 Y156.21 E.0041
G1 F2100
G1 X159.708 Y163.79 E.2663
G1 F2269.143
G1 X159.591 Y163.79 E.0041
G1 F2897.916
G1 X159.191 Y163.79 E.01405
G1 F3603.489
G1 X158.791 Y163.79 E.01405
G1 F4385.863
G1 X158.391 Y163.79 E.01405
G1 F5245.036
G1 X157.991 Y163.79 E.01405
G1 F6575.897
G1 X157.432 Y163.79 E.01966
G1 F7619.313
G1 X157.432 Y163.39 E.01405
G1 F8739.529
G1 X157.432 Y162.99 E.01405
G1 F9936.546
G1 X157.432 Y162.59 E.01405
G1 F11210.362
G1 X157.432 Y162.19 E.01405
G1 F12000
G1 X157.432 Y161.79 E.01405
G1 X157.432 Y156.21 E.19604
G1 X159.531 Y156.21 E.07376
; WIPE_START
M204 S8000
G1 X159.708 Y156.21 E-.06719
G1 X159.708 Y158.033 E-.69281
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.941 Y157.348 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X158.941 Y156.977 E.01304
G1 X158.199 Y156.977 E.02608
G1 X158.199 Y163.023 E.21241
G1 X158.941 Y163.023 E.02608
G1 X158.941 Y157.408 E.19726
; WIPE_START
G1 X158.941 Y159.408 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.57 Y162.652 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; LINE_WIDTH: 0.425484
G1 F12032.73
M204 S8000
G1 X158.57 Y157.408 E.18696
; COOLING_NODE: 1
; WIPE_START
G1 X158.57 Y159.408 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.372 Y161.948 Z9.96 F60000
G1 X147.238 Y163.407 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.734 Y163.407 E.05714
G1 X145.734 Y156.593 E.25885
G1 X147.238 Y156.593 E.05714
G1 X147.238 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.622 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6562.236
M204 S5000
G1 X147.067 Y163.79 E.01948
G1 F5244.183
G1 X146.667 Y163.79 E.01405
G1 F4385.083
G1 X146.267 Y163.79 E.01405
G1 F3602.783
G1 X145.867 Y163.79 E.01405
G1 F2897.283
G1 X145.467 Y163.79 E.01405
G1 F2268.582
G1 X145.351 Y163.79 E.00409
G1 F2100
G1 X145.351 Y156.21 E.2663
G1 F2268.582
G1 X145.467 Y156.21 E.00409
G1 F2897.283
G1 X145.867 Y156.21 E.01405
G1 F3602.783
G1 X146.267 Y156.21 E.01405
G1 F4385.083
G1 X146.667 Y156.21 E.01405
G1 F5244.183
G1 X147.067 Y156.21 E.01405
G1 F6562.236
G1 X147.622 Y156.21 E.01948
G1 F7604.608
G1 X147.622 Y156.61 E.01405
G1 F8723.779
G1 X147.622 Y157.01 E.01405
G1 F9919.751
G1 X147.622 Y157.41 E.01405
G1 F11192.523
G1 X147.622 Y157.81 E.01405
G1 F12000
G1 X147.622 Y158.21 E.01405
G1 X147.622 Y163.73 E.19393
; WIPE_START
M204 S8000
G1 X147.067 Y163.79 E-.21196
G1 X146.667 Y163.79 E-.152
G1 X146.267 Y163.79 E-.152
G1 X145.867 Y163.79 E-.152
G1 X145.625 Y163.79 E-.09204
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.855 Y157.345 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X146.855 Y156.977 E.01295
G1 X146.118 Y156.977 E.02589
G1 X146.118 Y163.023 E.21241
G1 X146.855 Y163.023 E.02589
G1 X146.855 Y157.405 E.19736
; WIPE_START
G1 X146.855 Y159.405 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.486 Y162.655 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; LINE_WIDTH: 0.420024
G1 F12211.007
M204 S8000
G1 X146.486 Y157.405 E.18442
; COOLING_NODE: 1
; WIPE_START
G1 X146.486 Y159.405 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.81 Y163.105 Z9.96 F60000
M73 P94 R0
G1 X139.266 Y163.407 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.762 Y163.407 E.05714
G1 X137.762 Y156.593 E.25885
G1 X139.266 Y156.593 E.05714
G1 X139.266 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.533 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.378 Y163.79 E.07569
G1 X137.378 Y158.21 E.19604
G1 X137.378 Y157.81 E.01405
G1 F11192.523
G1 X137.378 Y157.41 E.01405
G1 F9919.751
G1 X137.378 Y157.01 E.01405
G1 F8723.779
G1 X137.378 Y156.61 E.01405
G1 F7604.608
G1 X137.378 Y156.21 E.01405
G1 F6562.236
G1 X137.933 Y156.21 E.01948
G1 F5244.161
G1 X138.333 Y156.21 E.01405
G1 F4385.062
G1 X138.733 Y156.21 E.01405
G1 F3602.764
G1 X139.133 Y156.21 E.01405
G1 F2897.266
G1 X139.533 Y156.21 E.01405
G1 F2268.568
G1 X139.649 Y156.21 E.00409
G1 F2100
G1 X139.649 Y163.79 E.2663
G1 F2180.887
G1 X139.593 Y163.79 E.00198
; WIPE_START
M204 S8000
G1 X137.593 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.882 Y157.345 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X138.882 Y156.977 E.01295
G1 X138.145 Y156.977 E.02589
G1 X138.145 Y163.023 E.21241
G1 X138.882 Y163.023 E.02589
G1 X138.882 Y157.405 E.19736
; WIPE_START
G1 X138.882 Y159.405 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.514 Y162.655 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; LINE_WIDTH: 0.420044
G1 F12210.344
M204 S8000
G1 X138.514 Y157.405 E.18443
; CHANGE_LAYER
; Z_HEIGHT: 9.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12210.344
G1 X138.514 Y159.405 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 41/47
; update layer progress
M73 L41
M991 S0 P40 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z9.96 I.073 J1.215 P1  F60000
G1 X185.513 Y156.593 Z9.96
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X187.036 Y156.593 E.05786
G1 X187.036 Y163.407 E.25885
G1 X185.513 Y163.407 E.05786
G1 X185.513 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.193 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.419 Y156.21 E.07823
G1 X187.419 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X186.793 Y163.79 E.02202
G1 X186.393 Y163.79 E.01405
G1 F11931.844
G1 X185.993 Y163.79 E.01405
G1 F10616.46
G1 X185.593 Y163.79 E.01405
G1 F9377.876
G1 X185.193 Y163.79 E.01405
G1 F8216.092
G1 X185.13 Y163.79 E.00221
G1 F8040
G1 X185.13 Y156.21 E.2663
G1 F8048.448
G1 X185.133 Y156.21 E.00011
; WIPE_START
M204 S8000
G1 X187.133 Y156.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.897 Y163.023 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X186.652 Y163.023 E.02656
G1 X186.652 Y156.977 E.21241
G1 X185.897 Y156.977 E.02656
G1 X185.897 Y162.963 E.2103
M204 S10000
G1 X186.274 Y162.645 F60000
; LINE_WIDTH: 0.438944
G1 F11614.703
M204 S8000
G1 X186.274 Y157.415 E.19319
; COOLING_NODE: 6
; WIPE_START
G1 X186.274 Y159.415 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.394 Y162.719 Z10.2 F60000
G1 X177.964 Y163.407 Z10.2
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.964 Y156.593 E.25885
G1 X179.487 Y156.593 E.05786
G1 X179.487 Y163.407 E.25885
G1 X178.024 Y163.407 E.05558
; COOLING_NODE: 6
M204 S250
G1 X177.581 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.581 Y156.21 E.2663
G1 X178.207 Y156.21 E.02202
G1 X178.607 Y156.21 E.01405
G1 F11931.844
G1 X179.007 Y156.21 E.01405
G1 F10616.46
G1 X179.407 Y156.21 E.01405
G1 F9377.876
G1 X179.807 Y156.21 E.01405
G1 F8216.092
G1 X179.87 Y156.21 E.00221
G1 F8040
G1 X179.87 Y163.79 E.2663
G1 F8216.092
G1 X179.807 Y163.79 E.00221
G1 F9377.876
G1 X179.407 Y163.79 E.01405
G1 F10616.46
G1 X179.007 Y163.79 E.01405
G1 F11931.844
G1 X178.607 Y163.79 E.01405
G1 F12000
G1 X178.207 Y163.79 E.01405
G1 X177.641 Y163.79 E.01991
; WIPE_START
M204 S8000
G1 X177.625 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.348 Y163.023 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X179.104 Y163.023 E.02656
G1 X179.104 Y156.977 E.21241
G1 X178.348 Y156.977 E.02656
G1 X178.348 Y162.963 E.2103
M204 S10000
G1 X178.726 Y162.645 F60000
; LINE_WIDTH: 0.438944
G1 F11614.703
M204 S8000
G1 X178.726 Y157.415 E.19319
; COOLING_NODE: 3
; WIPE_START
G1 X178.726 Y159.415 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.506 Y161.892 Z10.2 F60000
G1 X167.09 Y163.407 Z10.2
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.563 Y163.407 E.05803
G1 X165.563 Y156.593 E.25885
G1 X167.09 Y156.593 E.05803
G1 X167.09 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.474 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.251 Y163.79 E.00783
G1 X166.851 Y163.79 E.01405
G1 F10761.536
G1 X166.451 Y163.79 E.01405
G1 F9514.257
G1 X166.051 Y163.79 E.01405
G1 F8343.777
G1 X165.651 Y163.79 E.01405
G1 F7250.098
G1 X165.251 Y163.79 E.01405
G1 F6233.218
G1 X165.18 Y163.79 E.00251
G1 F6060
G1 X165.18 Y156.21 E.2663
G1 F6233.218
G1 X165.251 Y156.21 E.00251
G1 F7250.098
G1 X165.651 Y156.21 E.01405
G1 F8343.777
G1 X166.051 Y156.21 E.01405
G1 F9514.257
G1 X166.451 Y156.21 E.01405
G1 F10761.536
G1 X166.851 Y156.21 E.01405
G1 F12000
G1 X167.251 Y156.21 E.01405
G1 X167.474 Y156.21 E.00783
G1 X167.474 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X167.251 Y163.79 E-.08774
G1 X166.851 Y163.79 E-.152
G1 X166.451 Y163.79 E-.152
G1 X166.051 Y163.79 E-.152
G1 X165.651 Y163.79 E-.152
G1 X165.482 Y163.79 E-.06426
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.947 Y163.023 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.707 Y163.023 E.02671
G1 X166.707 Y156.977 E.21241
G1 X165.947 Y156.977 E.02671
G1 X165.947 Y162.963 E.2103
M204 S10000
G1 X166.327 Y162.643 F60000
; LINE_WIDTH: 0.443324
G1 F11484.866
M204 S8000
G1 X166.327 Y157.417 E.19521
; COOLING_NODE: 3
; WIPE_START
G1 X166.327 Y159.417 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.437 Y156.593 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.437 Y163.407 E.25885
G1 X157.91 Y163.407 E.05803
G1 X157.91 Y156.593 E.25885
G1 X159.377 Y156.593 E.05575
; COOLING_NODE: 3
M204 S250
G1 X159.749 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6233.218
M204 S5000
G1 X159.82 Y156.21 E.00251
G1 F6060
G1 X159.82 Y163.79 E.2663
G1 F6233.218
G1 X159.749 Y163.79 E.00251
G1 F7250.098
G1 X159.349 Y163.79 E.01405
G1 F8343.777
G1 X158.949 Y163.79 E.01405
G1 F9514.257
G1 X158.549 Y163.79 E.01405
G1 F10761.536
G1 X158.149 Y163.79 E.01405
G1 F12000
G1 X157.749 Y163.79 E.01405
G1 X157.526 Y163.79 E.00783
G1 X157.526 Y156.21 E.2663
G1 X159.689 Y156.21 E.07599
; WIPE_START
M204 S8000
G1 X159.82 Y156.21 E-.0499
G1 X159.82 Y158.079 E-.7101
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.053 Y157.357 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.053 Y156.977 E.01336
G1 X158.293 Y156.977 E.02671
G1 X158.293 Y163.023 E.21241
G1 X159.053 Y163.023 E.02671
G1 X159.053 Y157.417 E.19695
; WIPE_START
G1 X159.053 Y159.417 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.673 Y162.643 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; LINE_WIDTH: 0.443344
G1 F11484.28
M204 S8000
G1 X158.673 Y157.417 E.19522
; COOLING_NODE: 1
; WIPE_START
G1 X158.673 Y159.417 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.461 Y161.913 Z10.2 F60000
G1 X147.145 Y163.407 Z10.2
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.614 Y163.407 E.05815
G1 X145.614 Y156.593 E.25885
G1 X147.145 Y156.593 E.05815
G1 X147.145 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.528 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11405.557
M204 S5000
G1 X147.31 Y163.79 E.00768
G1 F10693.908
G1 X146.91 Y163.79 E.01405
G1 F9450.674
G1 X146.51 Y163.79 E.01405
G1 F8284.241
G1 X146.11 Y163.79 E.01405
G1 F7194.607
G1 X145.71 Y163.79 E.01405
G1 F6181.774
G1 X145.31 Y163.79 E.01405
G1 F5245.741
G1 X145.231 Y163.79 E.00277
G1 F5070
G1 X145.231 Y156.21 E.2663
G1 F5245.741
G1 X145.31 Y156.21 E.00277
G1 F6181.774
G1 X145.71 Y156.21 E.01405
G1 F7194.607
G1 X146.11 Y156.21 E.01405
G1 F8284.241
G1 X146.51 Y156.21 E.01405
G1 F9450.674
G1 X146.91 Y156.21 E.01405
G1 F10693.908
G1 X147.31 Y156.21 E.01405
G1 F11405.557
G1 X147.528 Y156.21 E.00768
G1 F12000
G1 X147.528 Y156.61 E.01405
G1 X147.528 Y163.73 E.25014
; WIPE_START
M204 S8000
G1 X147.31 Y163.79 E-.08611
G1 X146.91 Y163.79 E-.152
G1 X146.51 Y163.79 E-.152
G1 X146.11 Y163.79 E-.152
G1 X145.71 Y163.79 E-.152
G1 X145.536 Y163.79 E-.06588
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.761 Y157.359 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X146.761 Y156.977 E.01341
G1 X145.998 Y156.977 E.02683
G1 X145.998 Y163.023 E.21241
G1 X146.761 Y163.023 E.02683
G1 X146.761 Y157.419 E.19689
; WIPE_START
G1 X146.761 Y159.419 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.379 Y162.641 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; LINE_WIDTH: 0.446564
G1 F11390.675
M204 S8000
G1 X146.379 Y157.419 E.19671
; COOLING_NODE: 1
; WIPE_START
G1 X146.379 Y159.419 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.749 Y163.199 Z10.2 F60000
G1 X139.386 Y163.407 Z10.2
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.855 Y163.407 E.05815
G1 X137.855 Y156.593 E.25885
G1 X139.386 Y156.593 E.05815
G1 X139.386 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.69 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.472 Y163.79 E.07794
G1 X137.472 Y156.61 E.25225
G1 X137.472 Y156.21 E.01405
G1 F11405.557
G1 X137.69 Y156.21 E.00768
G1 F10693.876
G1 X138.09 Y156.21 E.01405
G1 F9450.644
G1 X138.49 Y156.21 E.01405
G1 F8284.213
G1 X138.89 Y156.21 E.01405
G1 F7194.581
G1 X139.29 Y156.21 E.01405
G1 F6181.75
G1 X139.69 Y156.21 E.01405
G1 F5245.718
G1 X139.769 Y156.21 E.00277
G1 F5070
G1 X139.769 Y163.79 E.2663
G1 F5111.937
G1 X139.75 Y163.79 E.00067
; WIPE_START
M204 S8000
G1 X137.75 Y163.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.002 Y157.359 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X139.002 Y156.977 E.01341
G1 X138.239 Y156.977 E.02683
G1 X138.239 Y163.023 E.21241
G1 X139.002 Y163.023 E.02683
G1 X139.002 Y157.419 E.19689
; WIPE_START
G1 X139.002 Y159.419 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.621 Y162.641 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; LINE_WIDTH: 0.446564
G1 F11390.675
M204 S8000
G1 X138.621 Y157.419 E.19671
; CHANGE_LAYER
; Z_HEIGHT: 10.04
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11390.675
G1 X138.621 Y159.419 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 42/47
; update layer progress
M73 L42
M991 S0 P41 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z10.2 I.073 J1.215 P1  F60000
G1 X185.465 Y156.593 Z10.2
G1 Z10.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X186.927 Y156.593 E.05556
G1 X186.927 Y163.407 E.25885
G1 X185.465 Y163.407 E.05556
G1 X185.465 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.089 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.311 Y156.21 E.07807
G1 X187.311 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.089 Y163.79 E.07807
G1 X185.081 Y163.79 E.00026
G1 X185.081 Y156.263 E.26445
; WIPE_START
M204 S8000
G1 X187.081 Y156.215 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.848 Y163.023 Z10.44 F60000
M73 P95 R0
G1 Z10.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X186.544 Y163.023 E.02443
G1 X186.544 Y156.977 E.21241
G1 X185.848 Y156.977 E.02443
G1 X185.848 Y162.963 E.2103
M204 S10000
G1 X186.196 Y162.675 F60000
; LINE_WIDTH: 0.378484
G1 F13762.311
M204 S8000
G1 X186.196 Y157.385 E.16493
; COOLING_NODE: 6
; WIPE_START
G1 X186.196 Y159.385 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.356 Y162.771 Z10.44 F60000
G1 X178.073 Y163.407 Z10.44
G1 Z10.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X178.073 Y156.593 E.25885
G1 X179.535 Y156.593 E.05556
G1 X179.535 Y163.407 E.25885
G1 X178.133 Y163.407 E.05328
; COOLING_NODE: 6
M204 S250
G1 X177.689 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.689 Y156.21 E.2663
G1 X179.911 Y156.21 E.07807
G1 X179.919 Y156.21 E.00026
G1 X179.919 Y163.79 E.2663
G1 X179.911 Y163.79 E.00026
G1 X177.749 Y163.79 E.07596
; WIPE_START
M204 S8000
G1 X177.734 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.456 Y163.023 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X179.152 Y163.023 E.02443
G1 X179.152 Y156.977 E.21241
G1 X178.456 Y156.977 E.02443
G1 X178.456 Y162.963 E.2103
M204 S10000
G1 X178.804 Y162.675 F60000
; LINE_WIDTH: 0.378484
G1 F13762.311
M204 S8000
G1 X178.804 Y157.385 E.16493
; COOLING_NODE: 3
; WIPE_START
G1 X178.804 Y159.385 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.578 Y161.843 Z10.44 F60000
G1 X166.983 Y163.407 Z10.44
G1 Z10.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.508 Y163.407 E.05602
G1 X165.508 Y156.593 E.25885
G1 X166.983 Y156.593 E.05602
G1 X166.983 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.366 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.139 Y163.79 E.07826
G1 X165.125 Y163.79 E.00048
G1 X165.125 Y156.21 E.2663
G1 X165.139 Y156.21 E.00048
G1 X167.366 Y156.21 E.07826
G1 X167.366 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.367 Y163.784 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.892 Y163.023 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.599 Y163.023 E.02485
G1 X166.599 Y156.977 E.21241
G1 X165.892 Y156.977 E.02485
G1 X165.892 Y162.963 E.2103
M204 S10000
G1 X166.246 Y162.669 F60000
; LINE_WIDTH: 0.390464
G1 F13275.904
M204 S8000
G1 X166.246 Y157.391 E.17059
; COOLING_NODE: 3
; WIPE_START
G1 X166.246 Y159.391 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.492 Y156.593 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.492 Y163.407 E.25885
G1 X158.017 Y163.407 E.05602
G1 X158.017 Y156.593 E.25885
G1 X159.432 Y156.593 E.05374
; COOLING_NODE: 3
M204 S250
G1 X159.861 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.875 Y156.21 E.00048
G1 X159.875 Y163.79 E.2663
G1 X159.861 Y163.79 E.00048
G1 X157.634 Y163.79 E.07826
G1 X157.634 Y156.21 E.2663
G1 X159.801 Y156.21 E.07616
; WIPE_START
M204 S8000
G1 X159.875 Y156.21 E-.02801
G1 X159.875 Y158.136 E-.73199
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.108 Y157.331 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.108 Y156.977 E.01243
G1 X158.401 Y156.977 E.02485
G1 X158.401 Y163.023 E.21241
G1 X159.108 Y163.023 E.02485
G1 X159.108 Y157.391 E.19788
; WIPE_START
G1 X159.108 Y159.391 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.754 Y162.669 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; LINE_WIDTH: 0.390484
G1 F13275.121
M204 S8000
G1 X158.754 Y157.391 E.1706
; COOLING_NODE: 1
; WIPE_START
G1 X158.754 Y159.391 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.534 Y161.865 Z10.44 F60000
G1 X147.038 Y163.407 Z10.44
G1 Z10.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.553 Y163.407 E.05642
G1 X145.553 Y156.593 E.25885
G1 X147.038 Y156.593 E.05642
G1 X147.038 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.422 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.19 Y163.79 E.07842
G1 X145.17 Y163.79 E.0007
G1 X145.17 Y156.21 E.2663
G1 X145.19 Y156.21 E.0007
G1 X147.422 Y156.21 E.07842
G1 X147.422 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.422 Y163.784 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.655 Y157.336 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X146.655 Y156.977 E.01261
G1 X145.937 Y156.977 E.02523
G1 X145.937 Y163.023 E.21241
G1 X146.655 Y163.023 E.02523
G1 X146.655 Y157.396 E.19769
; WIPE_START
G1 X146.655 Y159.396 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.296 Y162.664 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; LINE_WIDTH: 0.401084
G1 F12872.591
M204 S8000
G1 X146.296 Y157.396 E.17558
; COOLING_NODE: 1
; WIPE_START
G1 X146.296 Y159.396 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.709 Y163.253 Z10.44 F60000
G1 X139.447 Y163.407 Z10.44
G1 Z10.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X137.962 Y163.407 E.05642
G1 X137.962 Y156.593 E.25885
G1 X139.447 Y156.593 E.05642
G1 X139.447 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.578 Y163.79 E.07842
G1 X137.578 Y156.21 E.2663
G1 X139.81 Y156.21 E.07842
G1 X139.83 Y156.21 E.0007
G1 X139.83 Y163.75 E.2649
; WIPE_START
M204 S8000
G1 X137.831 Y163.786 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.063 Y157.336 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X139.063 Y156.977 E.01261
G1 X138.345 Y156.977 E.02523
G1 X138.345 Y163.023 E.21241
G1 X139.063 Y163.023 E.02523
G1 X139.063 Y157.396 E.19769
; WIPE_START
G1 X139.063 Y159.396 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.704 Y162.664 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; LINE_WIDTH: 0.401084
G1 F12872.591
M204 S8000
G1 X138.704 Y157.396 E.17558
; CHANGE_LAYER
; Z_HEIGHT: 10.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12872.591
G1 X138.704 Y159.396 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 43/47
; update layer progress
M73 L43
M991 S0 P42 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z10.44 I.073 J1.215 P1  F60000
G1 X185.466 Y156.593 Z10.44
G1 Z10.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X186.804 Y156.593 E.05086
G1 X186.804 Y163.407 E.25885
G1 X185.466 Y163.407 E.05086
G1 X185.466 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.082 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.188 Y156.21 E.07398
G1 X187.188 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.082 Y163.79 E.07398
G1 X185.082 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.081 Y156.213 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.9 Y162.972 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.521584
G1 F9572.838
M204 S8000
G1 X186.37 Y162.972 E.02107
G1 X186.37 Y157.028 E.26642
G1 X185.9 Y157.028 E.02107
G1 X185.9 Y162.912 E.26373
; COOLING_NODE: 6
; WIPE_START
G1 X185.9 Y160.912 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.639 Y163.263 Z10.68 F60000
G1 X178.196 Y163.407 Z10.68
G1 Z10.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X178.196 Y156.593 E.25885
G1 X179.534 Y156.593 E.05086
G1 X179.534 Y163.407 E.25885
G1 X178.256 Y163.407 E.04858
; COOLING_NODE: 6
M204 S250
G1 X177.812 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.812 Y156.21 E.2663
G1 X179.918 Y156.21 E.07398
G1 X179.918 Y163.79 E.2663
G1 X177.872 Y163.79 E.07187
; WIPE_START
M204 S8000
G1 X177.856 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.63 Y162.972 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.521584
G1 F9572.838
M204 S8000
G1 X179.1 Y162.972 E.02107
G1 X179.1 Y157.028 E.26642
G1 X178.63 Y157.028 E.02107
G1 X178.63 Y162.912 E.26373
; COOLING_NODE: 3
; WIPE_START
G1 X178.63 Y160.912 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.163 Y162.495 Z10.68 F60000
G1 X166.861 Y163.407 Z10.68
G1 Z10.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.503 Y163.407 E.05159
G1 X165.503 Y156.593 E.25885
G1 X166.861 Y156.593 E.05159
G1 X166.861 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.245 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.12 Y163.79 E.07465
G1 X165.12 Y156.21 E.2663
G1 X167.245 Y156.21 E.07465
G1 X167.245 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.245 Y163.786 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.942 Y162.967 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.531194
G1 F9381.059
M204 S8000
G1 X166.422 Y162.967 E.02194
G1 X166.422 Y157.033 E.27143
G1 X165.942 Y157.033 E.02194
G1 X165.942 Y162.907 E.26868
; COOLING_NODE: 3
; WIPE_START
G1 X165.942 Y160.907 E-.76
; WIPE_END
M73 P96 R0
G1 E-.04 F1800
M204 S10000
G1 X159.599 Y156.662 Z10.68 F60000
G1 X159.497 Y156.593 Z10.68
G1 Z10.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.497 Y163.407 E.25885
G1 X158.139 Y163.407 E.05159
G1 X158.139 Y156.593 E.25885
G1 X159.437 Y156.593 E.04931
; COOLING_NODE: 3
M204 S250
G1 X159.88 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.88 Y163.79 E.2663
G1 X157.755 Y163.79 E.07465
G1 X157.755 Y156.21 E.2663
G1 X159.82 Y156.21 E.07254
; WIPE_START
M204 S8000
G1 X159.836 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.058 Y157.272 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.531194
G1 F9381.059
M204 S8000
G1 X159.058 Y157.033 E.01097
G1 X158.578 Y157.033 E.02194
G1 X158.578 Y162.967 E.27143
G1 X159.058 Y162.967 E.02194
G1 X159.058 Y157.332 E.25771
; COOLING_NODE: 1
; WIPE_START
G1 X159.058 Y159.332 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.822 Y161.761 Z10.68 F60000
G1 X146.918 Y163.407 Z10.68
G1 Z10.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.542 Y163.407 E.05226
G1 X145.542 Y156.593 E.25885
G1 X146.918 Y156.593 E.05226
G1 X146.918 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.302 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.159 Y163.79 E.07528
G1 X145.159 Y156.21 E.2663
G1 X147.302 Y156.21 E.07528
G1 X147.302 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.302 Y163.786 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.475 Y157.281 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.540094
G1 F9210.177
M204 S8000
G1 X146.475 Y157.037 E.01138
G1 X145.986 Y157.037 E.02276
G1 X145.986 Y162.963 E.27605
G1 X146.475 Y162.963 E.02276
G1 X146.475 Y157.341 E.26187
; COOLING_NODE: 1
; WIPE_START
G1 X146.475 Y159.341 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.87 Y163.167 Z10.68 F60000
G1 X139.458 Y163.407 Z10.68
G1 Z10.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X138.082 Y163.407 E.05226
G1 X138.082 Y156.593 E.25885
G1 X139.458 Y156.593 E.05226
G1 X139.458 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.841 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.698 Y163.79 E.07528
G1 X137.698 Y156.21 E.2663
G1 X139.841 Y156.21 E.07528
G1 X139.841 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.842 Y163.786 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.014 Y157.281 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.540084
G1 F9210.366
M204 S8000
G1 X139.014 Y157.037 E.01138
G1 X138.525 Y157.037 E.02276
G1 X138.525 Y162.963 E.27604
G1 X139.014 Y162.963 E.02276
G1 X139.014 Y157.341 E.26187
; CHANGE_LAYER
; Z_HEIGHT: 10.52
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F9210.366
G1 X139.014 Y159.341 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 44/47
; update layer progress
M73 L44
M991 S0 P43 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z10.68 I.072 J1.215 P1  F60000
G1 X185.516 Y156.593 Z10.68
G1 Z10.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X186.666 Y156.593 E.0437
G1 X186.666 Y163.407 E.25885
G1 X185.516 Y163.407 E.0437
G1 X185.516 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.132 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X187.05 Y156.21 E.06736
G1 X187.05 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.132 Y163.79 E.06736
G1 X185.132 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X187.05 Y156.21 E-.72891
G1 X187.05 Y156.292 E-.03109
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.903 Y163.019 Z10.92 F60000
G1 Z10.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.427394
G1 F11971.588
M204 S8000
G1 X186.279 Y163.019 E.01347
G1 X186.279 Y156.981 E.21641
G1 X185.903 Y156.981 E.01347
G1 X185.903 Y162.959 E.21426
; COOLING_NODE: 6
; WIPE_START
G1 X185.903 Y160.959 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.641 Y163.307 Z10.92 F60000
G1 X178.334 Y163.407 Z10.92
G1 Z10.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X178.334 Y156.593 E.25885
G1 X179.484 Y156.593 E.0437
G1 X179.484 Y163.407 E.25885
G1 X178.394 Y163.407 E.04142
; COOLING_NODE: 6
M204 S250
G1 X177.95 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X177.95 Y156.21 E.2663
G1 X179.868 Y156.21 E.06736
G1 X179.868 Y163.79 E.2663
G1 X178.01 Y163.79 E.06525
; WIPE_START
M204 S8000
G1 X177.995 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.721 Y163.019 Z10.92 F60000
G1 Z10.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.427394
G1 F11971.588
M204 S8000
G1 X179.097 Y163.019 E.01347
G1 X179.097 Y156.981 E.21641
G1 X178.721 Y156.981 E.01347
G1 X178.721 Y162.959 E.21426
; COOLING_NODE: 3
; WIPE_START
G1 X178.721 Y160.959 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.243 Y162.485 Z10.92 F60000
G1 X166.725 Y163.407 Z10.92
G1 Z10.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.547 Y163.407 E.04472
G1 X165.547 Y156.593 E.25885
G1 X166.725 Y156.593 E.04472
G1 X166.725 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X167.108 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.164 Y163.79 E.0683
G1 X165.164 Y156.21 E.2663
G1 X167.108 Y156.21 E.0683
G1 X167.108 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X165.164 Y163.79 E-.73912
G1 X165.164 Y163.735 E-.02088
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.941 Y163.013 Z10.92 F60000
G1 Z10.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.440834
G1 F11558.318
M204 S8000
G1 X166.331 Y163.013 E.01445
G1 X166.331 Y156.987 E.22365
G1 X165.941 Y156.987 E.01445
G1 X165.941 Y162.953 E.22142
; COOLING_NODE: 3
; WIPE_START
G1 X165.941 Y160.953 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.606 Y156.696 Z10.92 F60000
G1 X159.453 Y156.593 Z10.92
G1 Z10.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.453 Y163.407 E.25885
G1 X158.275 Y163.407 E.04472
G1 X158.275 Y156.593 E.25885
G1 X159.393 Y156.593 E.04244
; COOLING_NODE: 3
M204 S250
G1 X159.836 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.836 Y163.79 E.2663
G1 X157.892 Y163.79 E.0683
G1 X157.892 Y156.21 E.2663
G1 X159.776 Y156.21 E.06619
; WIPE_START
M204 S8000
G1 X159.792 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.059 Y157.182 Z10.92 F60000
G1 Z10.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.440834
G1 F11558.318
M204 S8000
G1 X159.059 Y156.987 E.00723
G1 X158.669 Y156.987 E.01445
G1 X158.669 Y163.013 E.22365
G1 X159.059 Y163.013 E.01445
G1 X159.059 Y157.242 E.2142
; COOLING_NODE: 1
; WIPE_START
G1 X159.059 Y159.242 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.831 Y161.694 Z10.92 F60000
G1 X146.783 Y163.407 Z10.92
G1 Z10.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.58 Y163.407 E.04569
G1 X145.58 Y156.593 E.25885
G1 X146.783 Y156.593 E.04569
G1 X146.783 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.167 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.197 Y163.79 E.0692
G1 X145.197 Y156.21 E.2663
G1 X147.167 Y156.21 E.0692
G1 X147.167 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.197 Y163.79 E-.74883
G1 X145.197 Y163.761 E-.01117
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.383 Y157.195 Z10.92 F60000
G1 Z10.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.453614
G1 F11190.968
M204 S8000
G1 X146.383 Y156.994 E.00771
G1 X145.981 Y156.994 E.01542
G1 X145.981 Y163.006 E.2305
G1 X146.383 Y163.006 E.01542
G1 X146.383 Y157.255 E.22049
; COOLING_NODE: 1
; WIPE_START
G1 X146.383 Y159.255 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.827 Y163.164 Z10.92 F60000
G1 X139.42 Y163.407 Z10.92
G1 Z10.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X138.217 Y163.407 E.04569
G1 X138.217 Y156.593 E.25885
G1 X139.42 Y156.593 E.04569
G1 X139.42 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.803 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.833 Y163.79 E.0692
G1 X137.833 Y156.21 E.2663
G1 X139.803 Y156.21 E.0692
G1 X139.803 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.833 Y163.79 E-.74883
G1 X137.833 Y163.761 E-.01117
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.019 Y157.195 Z10.92 F60000
G1 Z10.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.453614
G1 F11190.968
M204 S8000
G1 X139.019 Y156.994 E.00771
G1 X138.617 Y156.994 E.01542
G1 X138.617 Y163.006 E.2305
G1 X139.019 Y163.006 E.01542
G1 X139.019 Y157.255 E.22049
; CHANGE_LAYER
; Z_HEIGHT: 10.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11190.968
G1 X139.019 Y159.255 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 45/47
; update layer progress
M73 L45
M991 S0 P44 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z10.92 I.069 J1.215 P1  F60000
G1 X185.622 Y156.593 Z10.92
G1 Z10.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
M73 P97 R0
G1 X186.511 Y156.593 E.03378
G1 X186.511 Y163.407 E.25885
G1 X185.622 Y163.407 E.03378
G1 X185.622 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.239 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X186.895 Y156.21 E.05819
G1 X186.895 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.239 Y163.79 E.05819
G1 X185.239 Y156.27 E.2642
M204 S10000
G1 X186.067 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.542254
G1 F9169.638
M204 S8000
G1 X186.067 Y163.207 E.30013
; COOLING_NODE: 6
; WIPE_START
G1 X186.067 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.737 Y163.335 Z11.16 F60000
G1 X178.489 Y163.407 Z11.16
G1 Z10.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X178.489 Y156.593 E.25885
G1 X179.378 Y156.593 E.03378
G1 X179.378 Y163.407 E.25885
G1 X178.549 Y163.407 E.0315
; COOLING_NODE: 6
M204 S250
G1 X178.105 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X178.105 Y156.21 E.2663
G1 X179.761 Y156.21 E.05819
G1 X179.761 Y163.79 E.2663
G1 X178.165 Y163.79 E.05608
M204 S10000
G1 X178.933 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.542244
G1 F9169.826
M204 S8000
G1 X178.933 Y156.793 E.30012
; COOLING_NODE: 3
; WIPE_START
G1 X178.933 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.783 Y161.462 Z11.16 F60000
G1 X166.572 Y163.407 Z11.16
G1 Z10.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.647 Y163.407 E.03514
G1 X165.647 Y156.593 E.25885
G1 X166.572 Y156.593 E.03514
G1 X166.572 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X166.955 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.263 Y163.79 E.05944
G1 X165.263 Y156.21 E.2663
G1 X166.955 Y156.21 E.05944
G1 X166.955 Y163.73 E.2642
M204 S10000
G1 X166.109 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.577814
G1 F8550.095
M204 S8000
G1 X166.109 Y156.793 E.32187
; COOLING_NODE: 3
; WIPE_START
G1 X166.109 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.353 Y156.593 Z11.16 F60000
G1 Z10.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.353 Y163.407 E.25885
G1 X158.428 Y163.407 E.03514
G1 X158.428 Y156.593 E.25885
G1 X159.293 Y156.593 E.03286
; COOLING_NODE: 3
M204 S250
G1 X159.737 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.737 Y163.79 E.2663
G1 X158.045 Y163.79 E.05944
G1 X158.045 Y156.21 E.2663
G1 X159.677 Y156.21 E.05733
M204 S10000
G1 X158.891 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.577814
G1 F8550.095
M204 S8000
G1 X158.891 Y163.207 E.32187
; COOLING_NODE: 1
; WIPE_START
G1 X158.891 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.378 Y162.555 Z11.16 F60000
G1 X146.632 Y163.407 Z11.16
G1 Z10.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.672 Y163.407 E.03647
G1 X145.672 Y156.593 E.25885
G1 X146.632 Y156.593 E.03647
G1 X146.632 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X147.015 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.289 Y163.79 E.06067
G1 X145.289 Y156.21 E.2663
G1 X147.015 Y156.21 E.06067
G1 X147.015 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X145.289 Y163.79 E-.65663
G1 X145.289 Y163.518 E-.10337
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.152 Y163.207 Z11.16 F60000
G1 Z10.76
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.612964
G1 F8014.82
M204 S8000
G1 X146.152 Y156.793 E.34337
; COOLING_NODE: 1
; WIPE_START
G1 X146.152 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.829 Y163.068 Z11.16 F60000
G1 X139.328 Y163.407 Z11.16
G1 Z10.76
M73 P98 R0
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X138.368 Y163.407 E.03647
G1 X138.368 Y156.593 E.25885
G1 X139.328 Y156.593 E.03647
G1 X139.328 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.711 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X137.985 Y163.79 E.06067
G1 X137.985 Y156.21 E.2663
G1 X139.711 Y156.21 E.06067
G1 X139.711 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X137.985 Y163.79 E-.65663
G1 X137.985 Y163.518 E-.10337
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X138.848 Y163.207 Z11.16 F60000
G1 Z10.76
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.612964
G1 F8014.82
M204 S8000
G1 X138.848 Y156.793 E.34337
; CHANGE_LAYER
; Z_HEIGHT: 11
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F8014.82
G1 X138.848 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 46/47
; update layer progress
M73 L46
M991 S0 P45 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z11.16 I.057 J1.216 P1  F60000
G1 X185.806 Y156.593 Z11.16
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X186.324 Y156.593 E.01968
G1 X186.324 Y163.407 E.25885
G1 X185.806 Y163.407 E.01968
G1 X185.806 Y156.653 E.25657
; COOLING_NODE: 6
M204 S250
G1 X185.423 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X186.708 Y156.21 E.04514
G1 X186.708 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.423 Y163.79 E.04514
G1 X185.423 Y156.27 E.2642
M204 S10000
G1 X186.065 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.170934
G1 F15000
M204 S8000
G1 X186.065 Y163.207 E.07304
; COOLING_NODE: 6
; WIPE_START
G1 X186.065 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.75 Y163.385 Z11.4 F60000
G1 X178.676 Y163.407 Z11.4
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X178.676 Y156.593 E.25885
G1 X179.194 Y156.593 E.01968
G1 X179.194 Y163.407 E.25885
G1 X178.736 Y163.407 E.0174
; COOLING_NODE: 6
M204 S250
G1 X178.292 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X178.292 Y156.21 E.2663
G1 X179.577 Y156.21 E.04514
G1 X179.577 Y163.79 E.2663
G1 X178.352 Y163.79 E.04303
M204 S10000
G1 X178.935 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.170944
G1 F15000
M204 S8000
G1 X178.935 Y156.793 E.07305
; COOLING_NODE: 3
; WIPE_START
G1 X178.935 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.772 Y161.428 Z11.4 F60000
G1 X166.392 Y163.407 Z11.4
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.82 Y163.407 E.02177
G1 X165.82 Y156.593 E.25885
G1 X166.392 Y156.593 E.02177
G1 X166.392 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X166.776 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.436 Y163.79 E.04708
G1 X165.436 Y156.21 E.2663
G1 X166.776 Y156.21 E.04708
G1 X166.776 Y163.73 E.2642
M204 S10000
G1 X166.106 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.225974
G1 F15000
M204 S8000
G1 X166.106 Y156.793 E.1067
; COOLING_NODE: 3
; WIPE_START
G1 X166.106 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.18 Y156.593 Z11.4 F60000
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.18 Y163.407 E.25885
G1 X158.608 Y163.407 E.02177
G1 X158.608 Y156.593 E.25885
G1 X159.12 Y156.593 E.01949
; COOLING_NODE: 3
M204 S250
G1 X159.564 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.564 Y163.79 E.2663
G1 X158.224 Y163.79 E.04708
G1 X158.224 Y156.21 E.2663
G1 X159.504 Y156.21 E.04497
M204 S10000
G1 X158.894 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.225974
G1 F15000
M204 S8000
G1 X158.894 Y163.207 E.1067
; COOLING_NODE: 1
; WIPE_START
G1 X158.894 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.378 Y162.537 Z11.4 F60000
G1 X146.46 Y163.407 Z11.4
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X145.834 Y163.407 E.02376
G1 X145.834 Y156.593 E.25885
G1 X146.46 Y156.593 E.02376
G1 X146.46 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X146.843 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.451 Y163.79 E.04892
G1 X145.451 Y156.21 E.2663
G1 X146.843 Y156.21 E.04892
G1 X146.843 Y163.73 E.2642
M204 S10000
G1 X146.147 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.278384
G1 F15000
M204 S8000
G1 X146.147 Y156.793 E.13875
; COOLING_NODE: 1
; WIPE_START
G1 X146.147 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X139.779 Y163.001 Z11.4 F60000
G1 X139.166 Y163.407 Z11.4
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X138.54 Y163.407 E.02376
G1 X138.54 Y156.593 E.25885
G1 X139.166 Y156.593 E.02376
G1 X139.166 Y163.347 E.25657
; COOLING_NODE: 1
M204 S250
G1 X139.549 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X138.157 Y163.79 E.04892
G1 X138.157 Y156.21 E.2663
G1 X139.549 Y156.21 E.04892
G1 X139.549 Y163.73 E.2642
M204 S10000
G1 X138.853 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.278384
G1 F15000
M204 S8000
G1 X138.853 Y156.793 E.13875
; CHANGE_LAYER
; Z_HEIGHT: 11.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F15000
G1 X138.853 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 47/47
; update layer progress
M73 L47
M991 S0 P46 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 6
M204 S10000
G17
G3 Z11.4 I.067 J1.215 P1  F60000
G1 X185.761 Y156.21 Z11.4
G1 Z11.24
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X186.369 Y156.21 E.02134
G1 X186.369 Y163.79 E.2663
;===== machine: H2C timelapse =====
;======== date: 20260731 ========

; SKIPPABLE_START
; SKIPTYPE: timelapse

M1002 judge_flag timelapse_record_flag
M622 J1
    

    
        
    

    
        M971 S11 C10 O0
        M1004 S5 P1  ; external shutter
    

    
        
    
    
    
M623
; SKIPPABLE_END

G1 X185.761 Y163.79 E.02134
G1 X185.761 Y156.27 E.2642
M204 S10000
G1 X186.065 Y156.402 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.275364
G1 F15000
M204 S8000
G1 X186.065 Y163.598 E.15359
; COOLING_NODE: 6
; WIPE_START
G1 X186.065 Y161.598 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.744 Y163.757 Z11.64 F60000
G1 X178.631 Y163.79 Z11.64
G1 Z11.24
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X178.631 Y156.21 E.2663
G1 X179.239 Y156.21 E.02134
G1 X179.239 Y163.79 E.2663
G1 X178.691 Y163.79 E.01923
M204 S10000
G1 X178.935 Y163.598 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.275364
G1 F15000
M204 S8000
G1 X178.935 Y156.402 E.15359
; COOLING_NODE: 3
; WIPE_START
G1 X178.935 Y158.402 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.929 Y161.43 Z11.64 F60000
G1 X166.467 Y163.79 Z11.64
G1 Z11.24
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X165.745 Y163.79 E.02536
G1 X165.745 Y156.21 E.2663
G1 X166.467 Y156.21 E.02536
G1 X166.467 Y163.73 E.2642
M204 S10000
G1 X166.106 Y163.598 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.389764
G1 F13303.376
M204 S8000
G1 X166.106 Y156.402 E.23209
; COOLING_NODE: 3
; WIPE_START
G1 X166.106 Y158.402 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.255 Y156.21 Z11.64 F60000
G1 Z11.24
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.255 Y163.79 E.2663
G1 X158.533 Y163.79 E.02536
G1 X158.533 Y156.21 E.2663
G1 X159.195 Y156.21 E.02325
M204 S10000
G1 X158.894 Y156.402 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.389764
G1 F13303.376
M204 S8000
G1 X158.894 Y163.598 E.23209
; COOLING_NODE: 1
; WIPE_START
G1 X158.894 Y161.598 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.379 Y162.933 Z11.64 F60000
G1 X146.558 Y163.79 Z11.64
G1 Z11.24
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.735 Y163.79 E.02891
G1 X145.735 Y156.21 E.2663
G1 X146.558 Y156.21 E.02891
G1 X146.558 Y163.73 E.2642
M204 S10000
G1 X146.147 Y163.598 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.490984
G1 F10239.375
M204 S8000
G1 X146.147 Y156.402 E.30154
; COOLING_NODE: 1
; WIPE_START
G1 X146.147 Y158.402 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.137 Y163.107 Z11.64 F60000
G1 X139.265 Y163.79 Z11.64
G1 Z11.24
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X138.442 Y163.79 E.02891
G1 X138.442 Y156.21 E.2663
G1 X139.265 Y156.21 E.02891
G1 X139.265 Y163.73 E.2642
M204 S10000
G1 X138.853 Y163.598 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.490984
G1 F10239.375
M204 S8000
G1 X138.853 Y156.402 E.30154
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F10239.375
G1 X138.853 Y158.402 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z11.64 I1.217 J0 P1  F60000
M106 S0
M106 P2 S0
M981 S0 P20000 ; close spaghetti detector
; FEATURE: Custom
; MACHINE_END_GCODE_START
; filament end gcode 
;===== machine: H2C end =====
;====== date: 20260729 ======

M1003 S0
M73 P100 R0

G392 S0 ;turn off nozzle clog detect
M993 A0 B0 C0 ; nozzle cam detection not allowed.

M400 ; wait for buffer to clear
G92 E0 ; zero the extruder
M211 Z1
M640.2 R0

G90
G1 Z11.64 F900 ; lower z a little
M1002 judge_flag timelapse_record_flag
M622 J1
    G150.3
    M400 ; wait all motion done
    M991 S0 P-1 ;end smooth timelapse at safe pos
    M400 S5 ;wait for last picture to be taken
M623  ;end of "timelapse_record_flag"

G90
G1 Z21.24 F900 ; lower z a little

G90
M141 S0 ; turn off chamber heating
M140 S0 ; turn off bed
M106 S0 ; turn off fan
M106 P2 S0 ; turn off remote part cooling fan
M106 P3 S0 ; turn off chamber cooling fan
M106 P9 S0 ; turn off ext toodhead cooling fan

; pull back filament to AMS
M620 S65535

M620.11 P1 I0 B-1 E-14 F449.008



M620.11 K1 I0 B-1 R10 F449.008


M620.11 P1 I0 B-1 E-14
T65535
G150.2
M621 S65535

M620 S65279
T65279
G150.2
M621 S65279

G150.3

M104 S0 T0; turn off hotend
M104 S0 T1; turn off hotend

M400 ; wait all motion done
M17 S
M17 Z0.4 ; lower z motor current to reduce impact if there is something in the bottom

    
        G1 Z105.62 F600
        G1 Z103.62
    

M400 P100
M17 R ; restore z current

M220 S100  ; Reset feedrate magnitude
M201.2 K1.0 ; Reset acc magnitude
M73.2   R1.0 ;Reset left time magnitude
M1002 set_gcode_claim_speed_level : 0

M1015.4 S0 K0 ;disable air printing detect


;=====printer finish air purification=========
M622.1 S0
M1002 judge_flag print_finish_air_filt_flag

M622 J1
M1002 gcode_claim_action : 66
M145 P1
M106 P6 S255
M400 S180
M106 P6 S0
M623

M622 J2
M1002 gcode_claim_action : 66
M145 P0
M106 P3 S127
M400 S180
M106 P3 S0
M623
;=====printer finish air purification=========

;=====printer finish  sound=========
M17
M400 S1
M1006 S1
M1006 A53 B10 L99 C53 D10 M99 E53 F10 N99
M1006 A57 B10 L99 C57 D10 M99 E57 F10 N99
M1006 A0 B15 L0 C0 D15 M0 E0 F15 N0
M1006 A53 B10 L99 C53 D10 M99 E53 F10 N99
M1006 A57 B10 L99 C57 D10 M99 E57 F10 N99
M1006 A0 B15 L0 C0 D15 M0 E0 F15 N0
M1006 A48 B10 L99 C48 D10 M99 E48 F10 N99
M1006 A0 B15 L0 C0 D15 M0 E0 F15 N0
M1006 A60 B10 L99 C60 D10 M99 E60 F10 N99
M1006 W
;=====printer finish  sound=========
M400
M18

M73 P100 R0
; EXECUTABLE_BLOCK_END

