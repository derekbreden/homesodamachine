; HEADER_BLOCK_START
; BambuStudio 02.08.02.61
; model printing time: 3m 25s; total estimated time: 8m 35s
; total layer number: 82
; total filament length [mm] : 414.99
; total filament volume [cm^3] : 998.17
; total filament weight [g] : 1.29
; filament_density: 1.29
; filament_diameter: 1.75
; max_z_height: 19.64
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
M73 P0 R8
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
    
M73 P3 R8
    G1 E-3 F1800
    M400 P500
    G150.2
    G150.1


G91
M73 P5 R8
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
M73 P6 R8
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
M73 P57 R3
G1 X175 Y160 F30000

M622 J1
    M1002 gcode_claim_action : 1
    G29.20 A3
    G29 A1 O X158.4 Y153 I8.20001 J14 R
    M400
M623

M622 J2
    M1002 gcode_claim_action : 1
    
        G29.20 A4
        G29 A2 O X158.4 Y153 I8.20001 J14 R
    
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
M73 P58 R3
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
; layer num/total_layer_count: 1/82
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
; OBJECT_ID: 1901
M73 P59 R3
G1 X160.543 Y153.857 F60000
M204 S6000
M73 P60 R3
G1 Z.4
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X160.543 Y166.143 E.44616
G1 X159.257 Y166.143 E.0467
G1 X159.257 Y153.857 E.44616
G1 X160.483 Y153.857 E.04452
M204 S6000
G1 X161 Y153.4 F60000
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X161 Y166.6 E.47936
G1 X158.8 Y166.6 E.07989
G1 X158.8 Y153.4 E.47936
G1 X160.94 Y153.4 E.07771
; WIPE_START
G1 X160.949 Y155.4 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X159.44 Y154.044 Z.6 F60000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50014
G1 F6300
M204 S500
G1 X160.155 Y154.758 E.03672
G1 X160.155 Y155.405 E.02349
G1 X159.645 Y154.896 E.02615
G1 X159.645 Y155.543 E.02349
G1 X160.155 Y156.052 E.02615
G1 X160.155 Y156.698 E.02349
G1 X159.645 Y156.189 E.02615
G1 X159.645 Y156.836 E.02349
G1 X160.155 Y157.345 E.02615
G1 X160.155 Y157.991 E.02349
G1 X159.645 Y157.482 E.02615
G1 X159.645 Y158.129 E.02349
G1 X160.155 Y158.638 E.02615
G1 X160.155 Y159.285 E.02349
G1 X159.645 Y158.776 E.02615
G1 X159.645 Y159.422 E.02349
G1 X160.155 Y159.931 E.02615
G1 X160.155 Y160.578 E.02349
G1 X159.645 Y160.069 E.02615
G1 X159.645 Y160.715 E.02349
G1 X160.155 Y161.224 E.02615
G1 X160.155 Y161.871 E.02349
G1 X159.645 Y161.362 E.02615
G1 X159.645 Y162.009 E.02349
G1 X160.155 Y162.518 E.02615
G1 X160.155 Y163.164 E.02349
G1 X159.645 Y162.655 E.02615
G1 X159.645 Y163.302 E.02349
G1 X160.155 Y163.811 E.02615
G1 X160.155 Y164.457 E.02349
G1 X159.645 Y163.948 E.02615
G1 X159.645 Y164.595 E.02349
G1 X160.155 Y165.104 E.02615
G1 X160.155 Y165.751 E.02349
G1 X159.44 Y165.036 E.03672
; WIPE_START
G1 X160.155 Y165.751 E-.38409
G1 X160.155 Y165.104 E-.24571
G1 X159.912 Y164.862 E-.1302
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X164.357 Y163.143 Z.6 F60000
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X164.357 Y156.857 E.22827
G1 X165.743 Y156.857 E.05033
G1 X165.743 Y163.143 E.22827
G1 X164.417 Y163.143 E.04815
M204 S6000
M73 P61 R3
G1 X163.9 Y163.6 F60000
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X163.9 Y156.4 E.26147
G1 X166.2 Y156.4 E.08352
G1 X166.2 Y163.6 E.26147
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

G1 X163.96 Y163.6 E.08135
; WIPE_START
G1 X163.943 Y161.6 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X164.551 Y157.04 Z.6 F60000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.54017
G1 F6300
M204 S500
G1 X165.355 Y157.843 E.04489
G1 X165.355 Y158.547 E.02778
G1 X164.745 Y157.937 E.03403
G1 X164.745 Y158.641 E.02778
G1 X165.355 Y159.25 E.03403
G1 X165.355 Y159.953 E.02778
G1 X164.745 Y159.344 E.03403
G1 X164.745 Y160.047 E.02778
G1 X165.355 Y160.656 E.03403
G1 X165.355 Y161.359 E.02778
G1 X164.745 Y160.75 E.03403
G1 X164.745 Y161.454 E.02778
G1 X165.355 Y162.063 E.03403
G1 X165.355 Y162.755 E.02734
G1 X164.54 Y161.951 E.0452
; CHANGE_LAYER
; Z_HEIGHT: 0.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F6300
G1 X165.355 Y162.755 E-.4348
G1 X165.355 Y162.063 E-.26293
G1 X165.239 Y161.947 E-.06227
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 2/82
; update layer progress
M73 L2
M991 S0 P1 ;notify layer change
; open powerlost recovery
M1003 S1
M104 S280 ; set nozzle temperature
; OBJECT_ID: 1901
M204 S10000
G17
G3 Z.6 I1.075 J-.57 P1  F60000
G1 X160.806 Y153.593 Z.6
G1 Z.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.423 Y154.5 Z.84 F60000
G1 Z.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X160.423 Y153.977 E.01838
G1 X159.377 Y153.977 E.03675
G1 X159.377 Y166.023 E.4232
G1 X160.423 Y166.023 E.03675
G1 X160.423 Y154.56 E.40272
M204 S10000
G1 X160.069 Y154.5 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X160.069 Y154.331 E.00547
G1 X159.731 Y154.331 E.01094
G1 X159.731 Y165.669 E.36624
G1 X160.069 Y165.669 E.01094
G1 X160.069 Y154.56 E.35883
; WIPE_START
G1 X160.069 Y156.56 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.776 Y163.232 Z.84 F60000
G1 X163.873 Y163.407 Z.84
G1 Z.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X163.873 Y156.593 E.25885
G1 X166.007 Y156.593 E.08104
G1 X166.007 Y163.407 E.25885
G1 X163.933 Y163.407 E.07876
M204 S250
G1 X163.49 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2100
M204 S5000
G1 X163.49 Y156.21 E.2663
G1 F2361.845
G1 X163.669 Y156.21 E.00629
G1 F3002.556
G1 X164.069 Y156.21 E.01405
G1 F3720.068
G1 X164.469 Y156.21 E.01405
G1 F4514.38
G1 X164.869 Y156.21 E.01405
G1 F5385.491
G1 X165.269 Y156.21 E.01405
G1 F6333.403
G1 X165.669 Y156.21 E.01405
G1 F7358.115
G1 X166.069 Y156.21 E.01405
G1 F8236.048
G1 X166.39 Y156.21 E.01128
G1 F9399.195
G1 X166.39 Y156.61 E.01405
G1 F10639.143
G1 X166.39 Y157.01 E.01405
G1 F11955.89
G1 X166.39 Y157.41 E.01405
G1 F12000
G1 X166.39 Y157.81 E.01405
G1 X166.39 Y162.99 E.18199
G1 X166.39 Y163.39 E.01405
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

G1 F10803.191
G1 X166.39 Y163.79 E.01405
G1 F9553.426
G1 X166.069 Y163.79 E.01128
G1 F8605.978
G1 X165.669 Y163.79 E.01405
G1 F7494.648
G1 X165.269 Y163.79 E.01405
G1 F6460.118
G1 X164.869 Y163.79 E.01405
G1 F5502.389
G1 X164.469 Y163.79 E.01405
G1 F4621.459
G1 X164.069 Y163.79 E.01405
G1 F3817.33
G1 X163.669 Y163.79 E.01405
G1 F3090
G1 X163.55 Y163.79 E.00418
; WIPE_START
M204 S8000
G1 X163.534 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.257 Y163.023 Z.84 F60000
G1 Z.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.04799
G1 X165.623 Y156.977 E.21241
G1 X164.257 Y156.977 E.04799
G1 X164.257 Y162.963 E.2103
M204 S10000
G1 X164.691 Y162.589 F60000
; LINE_WIDTH: 0.550284
G1 F9022.014
M204 S8000
G1 X165.189 Y162.589 E.02372
G1 X165.189 Y157.411 E.24627
G1 X164.691 Y157.411 E.02372
G1 X164.691 Y162.529 E.24342
; CHANGE_LAYER
; Z_HEIGHT: 0.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9022.014
G1 X164.691 Y160.529 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 3/82
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z.84 I1.062 J-.595 P1  F60000
G1 X160.806 Y153.593 Z.84
G1 Z.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10620
M204 S5000
M73 P62 R3
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.423 Y154.5 Z1.08 F60000
G1 Z.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X160.423 Y153.977 E.01838
G1 X159.377 Y153.977 E.03675
G1 X159.377 Y166.023 E.4232
G1 X160.423 Y166.023 E.03675
G1 X160.423 Y154.56 E.40272
M204 S10000
G1 X160.069 Y154.5 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X160.069 Y154.331 E.00547
G1 X159.731 Y154.331 E.01094
G1 X159.731 Y165.669 E.36624
G1 X160.069 Y165.669 E.01094
G1 X160.069 Y154.56 E.35883
; COOLING_NODE: 0
; WIPE_START
G1 X160.069 Y156.56 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.594 Y163.33 Z1.08 F60000
G1 X163.633 Y163.407 Z1.08
G1 Z.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X163.633 Y156.593 E.25885
G1 X166.007 Y156.593 E.09016
G1 X166.007 Y163.407 E.25885
G1 X163.693 Y163.407 E.08788
; COOLING_NODE: 0
M204 S250
G1 X163.449 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2100
M204 S5000
G1 X163.25 Y163.79 E.00699
G1 F1950
G1 X163.25 Y156.21 E.2663
G1 F2100
G1 X163.449 Y156.21 E.00699
G1 F2706.344
G1 X163.849 Y156.21 E.01405
G1 F3389.487
G1 X164.249 Y156.21 E.01405
G1 F4149.431
G1 X164.649 Y156.21 E.01405
G1 F4986.175
G1 X165.049 Y156.21 E.01405
G1 F5899.718
G1 X165.449 Y156.21 E.01405
G1 F6890.062
G1 X165.849 Y156.21 E.01405
G1 F8351.71
G1 X166.39 Y156.21 E.01901
G1 F9522.727
G1 X166.39 Y156.61 E.01405
G1 F10620
G1 X166.39 Y157.01 E.01405
G1 X166.39 Y157.41 E.01405
G1 X166.39 Y163.79 E.22415
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

G1 X163.509 Y163.79 E.10122
; WIPE_START
G1 F12000
M204 S8000
G1 X163.25 Y163.79 E-.09842
G1 X163.25 Y162.049 E-.66158
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.82 Y162.22 Z1.08 F60000
G1 Z.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.552084
G1 F8989.572
M204 S8000
G1 X164.82 Y157.84 E.20904
; WIPE_START
G1 X164.82 Y159.84 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.385 Y162.655 Z1.08 F60000
G1 Z.68
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.255 Y162.655 E.03053
G1 X165.255 Y157.345 E.18652
G1 X164.385 Y157.345 E.03053
G1 X164.385 Y162.595 E.18441
M204 S10000
G1 X164.017 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.05642
G1 X165.623 Y156.977 E.21241
G1 X164.017 Y156.977 E.05642
G1 X164.017 Y162.963 E.2103
; CHANGE_LAYER
; Z_HEIGHT: 0.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12212.001
G1 X164.017 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 4/82
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.08 I1.116 J-.486 P1  F60000
G1 X160.806 Y153.593 Z1.08
G1 Z.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10609
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.849 Z1.32 F60000
G1 Z.92
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y157.443 E.06056
G1 X159.507 Y157.555 E.00781
G1 X159.935 Y157.981 E.02292
G1 X160.362 Y158.666 E.03068
G1 X160.466 Y158.862 E.00843
G1 X160.466 Y160.357 E.0568
G1 X160.362 Y160.305 E.0044
G1 X159.935 Y160.37 E.01643
G1 X159.334 Y160.601 E.02443
G1 X159.334 Y164.284 E.13994
G1 X159.507 Y164.396 E.00781
G1 X159.935 Y164.822 E.02292
G1 X160.466 Y165.68 E.03834
G1 X160.466 Y164.086 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y165.68 E-.60572
G1 X160.252 Y165.335 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z1.32 I.629 J1.042 P1  F60000
G1 X163.443 Y163.407 Z1.32
G1 Z.92
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2100
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 F2316.887
G1 X163.209 Y156.21 E.00523
G1 F2951.839
G1 X163.609 Y156.21 E.01405
G1 F3663.591
G1 X164.009 Y156.21 E.01405
G1 F4452.142
G1 X164.409 Y156.21 E.01405
G1 F5317.494
G1 X164.809 Y156.21 E.01405
G1 F6259.646
G1 X165.209 Y156.21 E.01405
G1 F7278.597
G1 X165.609 Y156.21 E.01405
G1 F8374.349
G1 X166.009 Y156.21 E.01405
G1 F9489.527
G1 X166.39 Y156.21 E.01339
G1 F10609
G1 X166.39 Y156.61 E.01405
G1 X166.39 Y157.01 E.01405
G1 X166.39 Y163.79 E.2382
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

G1 X165.609 Y163.79 E.02744
G1 X165.209 Y163.79 E.01405
G1 X164.809 Y163.79 E.01405
G1 F10533.552
G1 X164.409 Y163.79 E.01405
G1 F9299.964
G1 X164.009 Y163.79 E.01405
G1 F8143.176
G1 X163.609 Y163.79 E.01405
G1 F7063.188
G1 X163.209 Y163.79 E.01405
G1 F6060
G1 X163.12 Y163.79 E.00313
; WIPE_START
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z1.32 I-1.05 J.615 P1  F60000
G1 X163.827 Y163.023 Z1.32
G1 Z.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F13032.524
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 1.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 5/82
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.32 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z1.32
M73 P63 R3
G1 Z1.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10598
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.889 Z1.56 F60000
G1 Z1.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y157.483 E.06056
G1 X159.507 Y157.564 E.00725
G1 X159.935 Y157.886 E.02034
G1 X160.466 Y158.533 E.03179
G1 X160.466 Y160.813 E.08662
G1 X160.362 Y160.731 E.00502
G1 X159.935 Y160.634 E.01666
G1 X159.334 Y160.738 E.02315
G1 X159.334 Y164.324 E.13622
G1 X159.507 Y164.405 E.00725
G1 X159.935 Y164.727 E.02034
G1 X160.466 Y165.374 E.03179
G1 X160.466 Y163.78 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y165.374 E-.60572
G1 X160.208 Y165.06 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z1.56 F60000
G1 Z1.16
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10598
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z1.56 F60000
G1 Z1.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F11614
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F11614
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F11614
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 6/82
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.56 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z1.56
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10585
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y155.862 Z1.8 F60000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y154.268 E.06056
G1 X160.362 Y154.179 E.00517
G1 X159.935 Y153.995 E.01768
G1 X159.507 Y153.947 E.01635
G1 X159.334 Y153.965 E.0066
G1 X159.334 Y157.49 E.13394
G1 X159.507 Y157.543 E.00686
G1 X159.935 Y157.781 E.01858
G1 X160.466 Y158.298 E.02815
G1 X160.466 Y161.109 E.10681
G1 X160.362 Y161.02 E.00517
G1 X159.935 Y160.836 E.01768
G1 X159.507 Y160.788 E.01635
G1 X159.334 Y160.806 E.0066
G1 X159.334 Y164.331 E.13394
G1 X159.507 Y164.384 E.00686
G1 X159.935 Y164.622 E.01858
G1 X160.466 Y165.139 E.02815
G1 X160.466 Y163.545 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y165.139 E-.60572
G1 X160.175 Y164.856 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z1.8 F60000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10585
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z1.8 F60000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F13032.524
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 1.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 7/82
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.8 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z1.8
G1 Z1.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P64 R3
G1 F10570
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y156.098 Z2.04 F60000
G1 Z1.64
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y154.504 E.06056
G1 X160.362 Y154.41 E.00531
G1 X159.935 Y154.157 E.01886
G1 X159.507 Y154.036 E.01688
G1 X159.334 Y154.027 E.00657
G1 X159.334 Y157.471 E.13085
G1 X159.507 Y157.496 E.00663
G1 X159.935 Y157.659 E.01738
G1 X160.362 Y157.952 E.01968
G1 X160.466 Y158.05 E.00543
G1 X160.466 Y161.345 E.12516
G1 X160.362 Y161.251 E.00531
G1 X159.935 Y160.998 E.01886
G1 X159.507 Y160.877 E.01688
G1 X159.334 Y160.868 E.00657
G1 X159.334 Y164.312 E.13085
G1 X159.507 Y164.337 E.00663
G1 X159.935 Y164.5 E.01738
G1 X160.362 Y164.793 E.01968
G1 X160.466 Y164.892 E.00543
G1 X160.466 Y166.066 E.04461
G1 X160.046 Y166.066 E.01595
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y166.066 E-.15957
G1 X160.466 Y164.892 E-.44614
G1 X160.362 Y164.793 E-.05429
G1 X160.145 Y164.644 E-.09999
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z2.04 F60000
G1 Z1.64
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10570
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z2.04 F60000
G1 Z1.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F13032.524
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 1.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 8/82
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.04 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z2.04
G1 Z1.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10552
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.656 Z2.28 F60000
G1 Z1.88
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y154.062 E.06056
G1 X159.507 Y154.098 E.00671
G1 X159.935 Y154.291 E.01782
G1 X160.362 Y154.615 E.02037
G1 X160.466 Y154.718 E.00554
G1 X160.466 Y157.831 E.11828
G1 X160.362 Y157.739 E.00524
G1 X159.935 Y157.515 E.01835
G1 X159.507 Y157.423 E.01661
G1 X159.334 Y157.425 E.00656
G1 X159.334 Y160.903 E.13212
G1 X159.507 Y160.939 E.00671
G1 X159.935 Y161.132 E.01782
G1 X160.362 Y161.456 E.02037
G1 X160.466 Y161.559 E.00554
G1 X160.466 Y164.672 E.11828
G1 X160.362 Y164.581 E.00524
G1 X159.935 Y164.356 E.01835
G1 X159.507 Y164.264 E.01661
G1 X159.334 Y164.266 E.00656
G1 X159.334 Y165.86 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y164.266 E-.60571
G1 X159.507 Y164.264 E-.06561
G1 X159.735 Y164.313 E-.08868
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z2.28 F60000
G1 Z1.88
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10552
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z2.28 F60000
G1 Z1.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F13032.524
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 2.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 9/82
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.28 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z2.28
G1 Z2.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10532
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
M73 P65 R3
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.664 Z2.52 F60000
G1 Z2.12
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y154.07 E.06056
G1 X159.507 Y154.135 E.007
G1 X159.935 Y154.406 E.01923
G1 X160.466 Y154.968 E.02938
G1 X160.466 Y157.576 E.09909
G1 X160.362 Y157.49 E.00512
G1 X159.935 Y157.338 E.01724
G1 X159.334 Y157.378 E.02285
G1 X159.334 Y160.911 E.13423
G1 X159.507 Y160.976 E.007
G1 X159.935 Y161.247 E.01923
G1 X160.466 Y161.809 E.02938
G1 X160.466 Y164.417 E.09909
G1 X160.362 Y164.331 E.00512
G1 X159.935 Y164.179 E.01724
G1 X159.334 Y164.219 E.02285
G1 X159.334 Y165.813 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y164.219 E-.60571
G1 X159.74 Y164.192 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z2.52 F60000
G1 Z2.12
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10532
M204 S5000
G1 X163.06 Y156.21 E.2663
M73 P65 R2
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z2.52 F60000
G1 Z2.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F12669
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 2.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 10/82
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.52 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z2.52
G1 Z2.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10510
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.644 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y154.05 E.06056
G1 X159.507 Y154.144 E.00747
G1 X159.935 Y154.506 E.02129
G1 X160.466 Y155.236 E.0343
G1 X160.466 Y157.235 E.07593
G1 X160.362 Y157.158 E.00489
G1 X159.935 Y157.113 E.01634
G1 X159.334 Y157.267 E.02354
G1 X159.334 Y160.891 E.1377
G1 X159.507 Y160.985 E.00747
G1 X159.935 Y161.347 E.02129
G1 X160.466 Y162.077 E.0343
G1 X160.466 Y164.076 E.07593
G1 X160.362 Y163.999 E.00489
G1 X159.935 Y163.954 E.01634
G1 X159.334 Y164.108 E.02354
G1 X159.334 Y165.702 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y164.108 E-.60571
G1 X159.728 Y164.007 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10510
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12069
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F12069
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F12069
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 11/82
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.76 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z2.76
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10486
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
M73 P66 R2
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.583 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y153.989 E.06056
G1 X159.818 Y154.442 E.02517
G1 X160.104 Y154.869 E.01954
G1 X160.466 Y155.755 E.03634
G1 X160.466 Y156.412 E.02497
G1 X160.405 Y156.58 E.00677
G1 X159.506 Y157.007 E.03783
G1 X159.334 Y157.108 E.00758
G1 X159.334 Y160.83 E.14139
G1 X159.818 Y161.283 E.02517
G1 X160.104 Y161.71 E.01954
G1 X160.458 Y162.565 E.03517
G1 X160.466 Y163.253 E.02612
G1 X160.405 Y163.421 E.00677
G1 X159.506 Y163.848 E.03783
G1 X159.334 Y163.949 E.00758
G1 X159.334 Y165.543 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y163.949 E-.60571
G1 X159.506 Y163.848 E-.07579
G1 X159.693 Y163.759 E-.0785
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10486
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F11860
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F11860
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F11860
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 2.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 12/82
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z3
G1 Z2.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10461
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.493 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y153.934 E.05921
G1 X159.37 Y153.934 E.00135
G1 X159.47 Y154.014 E.00487
G1 X159.805 Y154.442 E.02061
G1 X160.016 Y154.869 E.01812
G1 X160.186 Y155.724 E.03312
G1 X160.103 Y156.152 E.01655
G1 X159.767 Y156.58 E.02066
G1 X159.334 Y156.922 E.02097
G1 X159.334 Y160.747 E.14532
G1 X159.47 Y160.855 E.00659
G1 X159.805 Y161.283 E.02061
G1 X160.016 Y161.71 E.01812
G1 X160.186 Y162.565 E.03312
G1 X160.103 Y162.993 E.01655
G1 X159.767 Y163.421 E.02066
G1 X159.334 Y163.763 E.02097
G1 X159.334 Y165.357 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y163.763 E-.60571
G1 X159.653 Y163.511 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10461
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F11718
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F11718
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F11718
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 3.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 13/82
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.24 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z3.24
G1 Z3.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10433
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y154.558 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y153.934 E.02368
G1 X159.495 Y153.934 E.03688
G1 X159.574 Y154.014 E.00428
G1 X159.822 Y154.442 E.01877
G1 X159.962 Y154.869 E.01709
G1 X159.976 Y155.724 E.03249
G1 X159.802 Y156.152 E.01755
G1 X159.334 Y156.683 E.02688
G1 X159.334 Y160.615 E.14936
M73 P67 R2
G1 X159.574 Y160.855 E.01291
G1 X159.822 Y161.283 E.01877
G1 X159.962 Y161.71 E.01709
G1 X159.976 Y162.565 E.03249
G1 X159.802 Y162.993 E.01755
G1 X159.334 Y163.524 E.02688
G1 X159.334 Y165.118 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y163.524 E-.60571
G1 X159.603 Y163.219 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10433
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F11615
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F11615
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F11615
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 3.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 14/82
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.48 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z3.48
G1 Z3.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10404
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y154.7 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y153.934 E.0291
G1 X159.637 Y153.934 E.03146
G1 X159.694 Y154.014 E.00371
G1 X159.866 Y154.442 E.01751
G1 X159.937 Y154.869 E.01647
G1 X159.922 Y155.297 E.01625
G1 X159.81 Y155.724 E.01679
G1 X159.566 Y156.152 E.0187
G1 X159.334 Y156.409 E.01314
G1 X159.334 Y160.368 E.15042
G1 X159.694 Y160.855 E.02299
G1 X159.866 Y161.283 E.01751
G1 X159.937 Y161.71 E.01647
G1 X159.922 Y162.138 E.01625
G1 X159.81 Y162.565 E.01679
G1 X159.566 Y162.993 E.0187
G1 X159.334 Y163.25 E.01314
G1 X159.334 Y164.844 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y163.25 E-.60571
G1 X159.566 Y162.993 E-.13142
G1 X159.596 Y162.941 E-.02287
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10404
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F11556
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F11556
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F11556
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 3.56
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 15/82
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.72 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z3.72
G1 Z3.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10373
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y154.854 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y153.934 E.03494
G1 X159.791 Y153.934 E.02562
G1 X159.835 Y154.014 E.00345
G1 X159.935 Y154.442 E.01669
G1 X159.939 Y154.869 E.01625
G1 X159.857 Y155.297 E.01654
G1 X159.673 Y155.724 E.01768
G1 X159.334 Y156.177 E.02148
G1 X159.334 Y160.128 E.15011
G1 X159.602 Y160.428 E.01525
G1 X159.835 Y160.855 E.0185
G1 X159.935 Y161.283 E.01669
G1 X159.939 Y161.71 E.01625
G1 X159.857 Y162.138 E.01654
G1 X159.673 Y162.565 E.01768
G1 X159.334 Y163.018 E.02148
G1 X159.334 Y164.612 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y163.018 E-.60571
G1 X159.578 Y162.693 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y163.407 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X163.443 Y156.593 E.25885
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.503 Y163.407 E.0951
; COOLING_NODE: 0
M204 S250
M73 P68 R2
G1 X163.06 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10373
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F11521
M204 S8000
G1 X165.623 Y163.023 E.0631
G1 X165.623 Y156.977 E.21241
G1 X163.827 Y156.977 E.0631
G1 X163.827 Y162.963 E.2103
M204 S10000
G1 X164.195 Y162.655 F60000
G1 F11521
M204 S8000
G1 X165.255 Y162.655 E.03721
G1 X165.255 Y157.345 E.18652
G1 X164.195 Y157.345 E.03721
G1 X164.195 Y162.595 E.18441
M204 S10000
G1 X164.552 Y162.298 F60000
; LINE_WIDTH: 0.396794
G1 F11521
M204 S8000
G1 X164.898 Y162.298 E.01137
G1 X164.898 Y157.702 E.15128
G1 X164.552 Y157.702 E.01137
G1 X164.552 Y162.238 E.1493
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 16/82
; update layer progress
M73 L16
M991 S0 P15 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.96 I1.06 J-.598 P1  F60000
G1 X160.806 Y153.593 Z3.96
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10341
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y155.04 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y153.934 E.04199
G1 X159.977 Y153.934 E.01857
G1 X160.007 Y154.014 E.00324
G1 X159.968 Y154.869 E.03252
G1 X159.817 Y155.297 E.01723
G1 X159.557 Y155.724 E.01902
G1 X159.334 Y155.94 E.01176
G1 X159.334 Y159.855 E.14873
G1 X159.484 Y160 E.00794
G1 X159.845 Y160.428 E.02124
G1 X160.007 Y160.855 E.01737
G1 X159.968 Y161.71 E.03252
G1 X159.817 Y162.138 E.01723
G1 X159.557 Y162.565 E.01902
G1 X159.334 Y162.781 E.01176
G1 X159.334 Y164.375 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y162.781 E-.60571
G1 X159.557 Y162.565 E-.1176
G1 X159.607 Y162.483 E-.03669
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.668 Y163.407 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X164.668 Y156.593 E.25885
G1 X166.007 Y156.593 E.05084
G1 X166.007 Y163.407 E.25885
G1 X164.728 Y163.407 E.04856
; COOLING_NODE: 0
; WIPE_START
G1 X164.711 Y161.407 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.06 Y163.79 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10341
M204 S5000
G1 X163.06 Y156.21 E.2663
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
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

G1 X163.12 Y163.79 E.11488
; WIPE_START
G1 F12000
M204 S8000
G1 X163.104 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.449 Y162.841 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X163.704 Y163.586 E.04002
G1 X163.561 Y163.729
G1 X163.121 Y163.606
G1 X163.264 Y163.462
G1 X164.449 Y162.278 E.06366
G1 X164.592 Y162.134
G1 X164.592 Y161.571
G1 X164.449 Y161.714
G1 X163.264 Y162.899 E.06366
G1 X163.121 Y163.042
G1 X163.121 Y162.478
G1 X163.264 Y162.335
G1 X164.449 Y161.15 E.06366
G1 X164.592 Y161.007
G1 X164.592 Y160.444
G1 X164.449 Y160.587
G1 X163.264 Y161.772 E.06366
G1 X163.121 Y161.915
G1 X163.121 Y161.351
G1 X163.264 Y161.208
G1 X164.449 Y160.023 E.06366
G1 X164.592 Y159.88
G1 X164.592 Y159.317
G1 X164.449 Y159.46
G1 X163.264 Y160.645 E.06366
G1 X163.121 Y160.788
G1 X163.121 Y160.224
G1 X163.264 Y160.081
G1 X164.449 Y158.896 E.06366
G1 X164.592 Y158.753
G1 X164.592 Y158.189
G1 X164.449 Y158.333
G1 X163.264 Y159.518 E.06366
G1 X163.121 Y159.661
G1 X163.121 Y159.097
G1 X163.264 Y158.954
G1 X164.449 Y157.769 E.06366
G1 X164.592 Y157.626
G1 X164.592 Y157.062
G1 X164.449 Y157.206
G1 X163.264 Y158.39 E.06366
G1 X163.121 Y158.534
G1 X163.121 Y157.97
G1 X163.264 Y157.827
G1 X164.449 Y156.642 E.06366
G1 X164.592 Y156.499
G1 X164.257 Y156.271
G1 X164.113 Y156.414
G1 X163.264 Y157.263 E.04563
; WIPE_START
M204 S8000
G1 X164.113 Y156.414 E-.45634
G1 X164.257 Y156.271 E-.07695
G1 X164.592 Y156.499 E-.15418
G1 X164.457 Y156.634 E-.07253
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.103 Y162.972 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.521354
G1 F9577.525
M204 S8000
G1 X165.572 Y162.972 E.02105
G1 X165.572 Y157.028 E.2663
G1 X165.103 Y157.028 E.02105
G1 X165.103 Y162.912 E.26361
; CHANGE_LAYER
; Z_HEIGHT: 4.04
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9577.525
G1 X165.103 Y160.912 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 17/82
; update layer progress
M73 L17
M991 S0 P16 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z4.2 I1.05 J-.616 P1  F60000
G1 X160.806 Y153.593 Z4.2
G1 Z4.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10332
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10306
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y155.276 Z4.44 F60000
G1 Z4.04
M73 P69 R2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10332
M204 S8000
G1 X160.466 Y153.934 E.05097
G1 X160.213 Y153.934 E.00959
G1 X160.225 Y154.014 E.00306
G1 X160.028 Y154.869 E.03334
G1 X159.804 Y155.297 E.01832
G1 X159.455 Y155.724 E.02099
G1 X159.334 Y155.815 E.00573
G1 X159.334 Y159.621 E.1446
G1 X159.835 Y160 E.02384
G1 X160.162 Y160.428 E.02045
G1 X160.225 Y160.855 E.01642
G1 X160.028 Y161.71 E.03334
G1 X159.804 Y162.138 E.01832
G1 X159.455 Y162.565 E.02099
G1 X159.334 Y162.656 E.00573
G1 X159.334 Y164.25 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y162.656 E-.60571
G1 X159.455 Y162.565 E-.05729
G1 X159.616 Y162.368 E-.097
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10332
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10306
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10332
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10332
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 4.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 18/82
; update layer progress
M73 L18
M991 S0 P17 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z4.44 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z4.44
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10320
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10270
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y154.209 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10320
M204 S8000
G1 X159.334 Y153.934 E.01045
G1 X160.466 Y153.934 E.04297
G1 X160.466 Y154.122 E.00714
G1 X160.362 Y154.386 E.01074
G1 X159.935 Y155.156 E.03347
G1 X159.507 Y155.612 E.02375
G1 X159.334 Y155.731 E.00797
G1 X159.334 Y159.441 E.14096
G1 X159.935 Y159.709 E.02497
G1 X160.362 Y159.85 E.0171
G1 X160.466 Y159.853 E.00393
G1 X160.466 Y160.963 E.04218
G1 X160.362 Y161.227 E.01074
G1 X159.935 Y161.997 E.03347
G1 X159.507 Y162.453 E.02375
G1 X159.334 Y162.572 E.00797
G1 X159.334 Y164.166 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y162.572 E-.60571
G1 X159.507 Y162.453 E-.07973
G1 X159.641 Y162.31 E-.07456
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10320
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10270
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10320
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10320
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 4.52
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 19/82
; update layer progress
M73 L19
M991 S0 P18 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z4.68 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z4.68
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10317
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10233
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y156.148 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10317
M204 S8000
G1 X160.466 Y154.554 E.06056
G1 X159.935 Y155.248 E.03321
G1 X159.507 Y155.594 E.0209
G1 X159.334 Y155.683 E.00738
G1 X159.334 Y159.292 E.13711
G1 X159.935 Y159.426 E.02337
G1 X160.362 Y159.359 E.01644
G1 X160.466 Y159.279 E.00495
G1 X160.466 Y161.395 E.08037
G1 X159.935 Y162.089 E.03321
G1 X159.507 Y162.435 E.0209
G1 X159.334 Y162.524 E.00738
G1 X159.334 Y164.118 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y162.524 E-.60571
G1 X159.507 Y162.435 E-.07381
G1 X159.672 Y162.302 E-.08048
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10317
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10233
M204 S5000
G1 X163.81 Y156.21 E.2663
M73 P70 R2
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10317
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10317
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 4.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 20/82
; update layer progress
M73 L20
M991 S0 P19 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z4.92 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z4.92
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10677
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10193
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y156.401 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10677
M204 S8000
G1 X160.466 Y154.807 E.06056
G1 X159.935 Y155.35 E.02886
G1 X159.507 Y155.608 E.01896
G1 X159.334 Y155.668 E.00694
G1 X159.334 Y159.187 E.1337
G1 X159.935 Y159.21 E.02282
G1 X160.362 Y159.045 E.01741
G1 X160.466 Y158.958 E.00514
G1 X160.466 Y161.648 E.1022
G1 X159.935 Y162.191 E.02886
G1 X159.507 Y162.449 E.01896
G1 X159.334 Y162.509 E.00694
G1 X159.334 Y166.028 E.1337
G1 X159.935 Y166.051 E.02282
G1 X160.362 Y165.886 E.01741
G1 X160.466 Y165.799 E.00514
G1 X160.466 Y164.205 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y165.799 E-.60572
G1 X160.362 Y165.886 E-.05139
G1 X160.11 Y165.984 E-.10289
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10677
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10193
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10677
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10677
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 5
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 21/82
; update layer progress
M73 L21
M991 S0 P20 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z5.16 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z5.16
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10696
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10151
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.992 Y153.934 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10696
M204 S8000
G1 X160.466 Y153.934 E.01798
G1 X160.466 Y155.055 E.04258
G1 X160.362 Y155.156 E.00549
G1 X159.935 Y155.467 E.02009
G1 X159.507 Y155.648 E.01764
G1 X159.334 Y155.681 E.00667
G1 X159.334 Y159.145 E.13162
G1 X159.507 Y159.143 E.00656
G1 X159.935 Y159.039 E.01671
G1 X160.362 Y158.804 E.01855
G1 X160.466 Y158.711 E.00527
G1 X160.466 Y161.896 E.121
G1 X160.362 Y161.997 E.00549
G1 X159.935 Y162.308 E.02009
G1 X159.507 Y162.489 E.01764
G1 X159.334 Y162.522 E.00667
G1 X159.334 Y165.986 E.13162
G1 X159.507 Y165.984 E.00656
G1 X159.935 Y165.88 E.01671
G1 X160.362 Y165.645 E.01855
G1 X160.466 Y165.552 E.00527
G1 X160.466 Y163.958 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y165.552 E-.60572
G1 X160.362 Y165.645 E-.05267
G1 X160.128 Y165.774 E-.10161
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10696
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10151
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10696
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
M73 P71 R2
G1 F10696
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 5.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 22/82
; update layer progress
M73 L22
M991 S0 P21 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z5.4 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z5.4
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10690
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10107
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y154.126 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10690
M204 S8000
G1 X159.334 Y155.72 E.06056
G1 X159.507 Y155.715 E.00656
G1 X159.935 Y155.605 E.01677
G1 X160.362 Y155.364 E.01866
G1 X160.466 Y155.271 E.00528
G1 X160.466 Y158.495 E.12249
G1 X160.362 Y158.595 E.00547
G1 X159.935 Y158.899 E.01994
G1 X159.507 Y159.074 E.01755
G1 X159.334 Y159.104 E.00666
G1 X159.334 Y162.561 E.13135
G1 X159.507 Y162.556 E.00656
G1 X159.935 Y162.446 E.01677
G1 X160.362 Y162.205 E.01866
G1 X160.466 Y162.112 E.00528
G1 X160.466 Y165.336 E.12249
G1 X160.362 Y165.436 E.00547
G1 X159.935 Y165.74 E.01994
G1 X159.507 Y165.915 E.01755
G1 X159.334 Y165.945 E.00666
G1 X159.334 Y164.351 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y165.945 E-.60572
G1 X159.507 Y165.915 E-.06657
G1 X159.721 Y165.828 E-.08771
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10690
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10107
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10690
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10690
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 5.48
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 23/82
; update layer progress
M73 L23
M991 S0 P22 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z5.64 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z5.64
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10633
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10060
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y154.165 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10633
M204 S8000
G1 X159.334 Y155.759 E.06056
G1 X159.935 Y155.773 E.02281
G1 X160.362 Y155.601 E.01751
G1 X160.466 Y155.513 E.00515
G1 X160.466 Y158.247 E.10387
G1 X159.935 Y158.781 E.0286
G1 X159.507 Y159.031 E.01882
G1 X159.334 Y159.088 E.00691
G1 X159.334 Y162.6 E.13341
G1 X159.935 Y162.614 E.02281
G1 X160.362 Y162.442 E.01751
G1 X160.466 Y162.354 E.00515
G1 X160.466 Y165.088 E.10387
G1 X159.935 Y165.622 E.0286
G1 X159.507 Y165.872 E.01882
G1 X159.334 Y165.93 E.00691
G1 X159.334 Y164.336 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y165.93 E-.60572
G1 X159.507 Y165.872 E-.06915
G1 X159.7 Y165.759 E-.08514
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10633
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10060
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10633
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10633
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 5.72
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 24/82
; update layer progress
M73 L24
M991 S0 P23 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z5.88 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z5.88
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10579
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10011
M204 S5000
M73 P72 R2
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y154.266 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10579
M204 S8000
G1 X159.334 Y155.86 E.06056
G1 X159.935 Y155.984 E.02328
G1 X160.362 Y155.905 E.01652
G1 X160.466 Y155.825 E.00498
G1 X160.466 Y158.001 E.08268
G1 X159.935 Y158.677 E.03267
G1 X159.507 Y159.015 E.0207
G1 X159.334 Y159.101 E.00733
G1 X159.334 Y162.701 E.13679
G1 X159.935 Y162.825 E.02328
G1 X160.362 Y162.746 E.01652
G1 X160.466 Y162.666 E.00498
G1 X160.466 Y164.842 E.08268
G1 X159.935 Y165.518 E.03267
G1 X159.507 Y165.856 E.0207
G1 X159.334 Y165.942 E.00733
G1 X159.334 Y164.348 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y165.942 E-.60572
G1 X159.507 Y165.856 E-.07335
G1 X159.674 Y165.724 E-.08094
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10579
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10011
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10579
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10579
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 5.96
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 25/82
; update layer progress
M73 L25
M991 S0 P24 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z6.12 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z6.12
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10506
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9960
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y154.411 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10506
M204 S8000
G1 X159.334 Y156.005 E.06056
G1 X159.935 Y156.26 E.02476
G1 X160.362 Y156.371 E.01678
G1 X160.466 Y156.341 E.00409
G1 X160.466 Y157.622 E.04867
G1 X160.362 Y157.847 E.00944
G1 X159.935 Y158.584 E.03237
G1 X159.507 Y159.029 E.02345
G1 X159.334 Y159.146 E.00791
G1 X159.334 Y162.846 E.14059
G1 X159.935 Y163.101 E.02477
G1 X160.362 Y163.212 E.01678
G1 X160.466 Y163.182 E.00409
G1 X160.466 Y164.463 E.04867
G1 X160.362 Y164.688 E.00944
G1 X159.935 Y165.425 E.03237
G1 X159.507 Y165.87 E.02345
G1 X159.334 Y165.987 E.00791
G1 X159.334 Y164.393 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y165.987 E-.60572
G1 X159.507 Y165.87 E-.07914
G1 X159.644 Y165.728 E-.07514
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10506
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9960
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10506
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10506
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 6.2
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 26/82
; update layer progress
M73 L26
M991 S0 P25 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z6.36 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z6.36
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10409
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9905
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y154.587 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10409
M204 S8000
G1 X159.334 Y156.181 E.06056
M73 P73 R2
G1 X159.876 Y156.58 E.02552
G1 X160.197 Y157.007 E.02032
G1 X160.247 Y157.435 E.01636
G1 X160.034 Y158.29 E.03348
G1 X159.805 Y158.717 E.01844
G1 X159.446 Y159.145 E.0212
G1 X159.334 Y159.227 E.00527
G1 X159.334 Y163.023 E.1442
G1 X159.876 Y163.421 E.02552
G1 X160.197 Y163.848 E.02032
G1 X160.247 Y164.276 E.01636
G1 X160.034 Y165.131 E.03348
G1 X159.805 Y165.558 E.01844
G1 X159.446 Y165.986 E.0212
G1 X159.338 Y166.066 E.00511
G1 X159.334 Y164.475 E.06043
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.338 Y166.066 E-.60444
G1 X159.446 Y165.986 E-.05107
G1 X159.623 Y165.775 E-.10449
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10409
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9905
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10409
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10409
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 6.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 27/82
; update layer progress
M73 L27
M991 S0 P26 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z6.6 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z6.6
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10351
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9848
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y154.818 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10351
M204 S8000
G1 X159.334 Y156.412 E.06056
G1 X159.511 Y156.58 E.00926
G1 X159.869 Y157.007 E.0212
G1 X160.024 Y157.435 E.01728
G1 X159.972 Y158.29 E.03255
G1 X159.815 Y158.717 E.01731
G1 X159.547 Y159.145 E.01917
G1 X159.334 Y159.347 E.01114
G1 X159.334 Y163.253 E.14838
G1 X159.511 Y163.421 E.00926
G1 X159.869 Y163.848 E.0212
G1 X160.024 Y164.276 E.01728
G1 X159.972 Y165.131 E.03255
G1 X159.815 Y165.558 E.01731
G1 X159.547 Y165.986 E.01917
G1 X159.463 Y166.066 E.00439
G1 X160.466 Y166.066 E.03808
G1 X160.466 Y165.474 E.02248
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y166.066 E-.22485
G1 X159.463 Y166.066 E-.38087
G1 X159.547 Y165.986 E-.0439
G1 X159.701 Y165.74 E-.11039
; WIPE_END
G1 E-.03999 F1800
M204 S10000
G1 X164.193 Y163.407 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10351
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9848
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10351
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10351
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 6.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 28/82
; update layer progress
M73 L28
M991 S0 P27 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z6.84 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z6.84
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10313
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9787
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.089 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10313
M204 S8000
G1 X159.334 Y156.683 E.06056
G1 X159.622 Y157.007 E.01644
G1 X159.849 Y157.435 E.01839
G1 X159.943 Y157.862 E.01663
G1 X159.941 Y158.29 E.01624
G1 X159.852 Y158.717 E.01659
G1 X159.662 Y159.145 E.01778
G1 X159.334 Y159.579 E.02067
G1 X159.334 Y163.524 E.14988
G1 X159.622 Y163.848 E.01644
G1 X159.849 Y164.276 E.01839
G1 X159.943 Y164.703 E.01663
G1 X159.941 Y165.131 E.01624
G1 X159.852 Y165.558 E.01659
G1 X159.662 Y165.986 E.01778
G1 X159.602 Y166.066 E.00378
G1 X160.466 Y166.066 E.0328
G1 X160.466 Y165.335 E.02776
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y166.066 E-.27763
G1 X159.602 Y166.066 E-.32808
G1 X159.662 Y165.986 E-.03782
G1 X159.786 Y165.706 E-.11647
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10313
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9787
M204 S5000
M73 P74 R2
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10313
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10313
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 6.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 29/82
; update layer progress
M73 L29
M991 S0 P28 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z7.08 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z7.08
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10290
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9724
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.334 Z7.32 F60000
G1 Z6.92
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10290
M204 S8000
G1 X159.334 Y156.928 E.06056
G1 X159.41 Y157.007 E.00416
G1 X159.705 Y157.435 E.01974
G1 X159.871 Y157.862 E.01742
G1 X159.936 Y158.29 E.01643
G1 X159.915 Y158.717 E.01626
G1 X159.797 Y159.145 E.01686
G1 X159.547 Y159.572 E.01882
G1 X159.334 Y159.806 E.012
G1 X159.334 Y163.769 E.15056
G1 X159.41 Y163.848 E.00416
G1 X159.705 Y164.276 E.01974
G1 X159.871 Y164.703 E.01742
G1 X159.936 Y165.131 E.01643
G1 X159.915 Y165.558 E.01626
G1 X159.797 Y165.986 E.01686
G1 X159.75 Y166.066 E.0035
G1 X160.466 Y166.066 E.02718
G1 X160.466 Y165.187 E.03338
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y166.066 E-.33385
G1 X159.75 Y166.066 E-.27187
G1 X159.797 Y165.986 E-.03505
G1 X159.88 Y165.684 E-.11924
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z7.32 F60000
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10290
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9724
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z7.32 F60000
G1 Z6.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10290
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10290
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 7.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 30/82
; update layer progress
M73 L30
M991 S0 P29 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z7.32 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z7.32
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10277
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9656
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.586 Z7.56 F60000
G1 Z7.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10277
M204 S8000
G1 X159.334 Y157.18 E.06056
G1 X159.584 Y157.435 E.01356
G1 X159.825 Y157.862 E.01863
G1 X159.958 Y158.29 E.01702
G1 X160.006 Y158.717 E.01634
G1 X159.96 Y159.145 E.01634
G1 X159.778 Y159.572 E.01765
G1 X159.334 Y160.08 E.02563
G1 X159.334 Y164.021 E.14971
G1 X159.584 Y164.276 E.01356
G1 X159.825 Y164.703 E.01863
G1 X159.958 Y165.131 E.01702
G1 X160.006 Y165.558 E.01634
G1 X159.96 Y165.986 E.01634
G1 X159.926 Y166.066 E.00329
G1 X160.466 Y166.066 E.02049
G1 X160.466 Y165.011 E.04007
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y166.066 E-.40073
G1 X159.926 Y166.066 E-.20499
G1 X159.96 Y165.986 E-.03287
G1 X159.994 Y165.668 E-.12142
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z7.56 F60000
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10277
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9656
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z7.56 F60000
G1 Z7.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10277
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10277
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 7.4
; LAYER_HEIGHT: 0.24
; WIPE_START
M73 P75 R2
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 31/82
; update layer progress
M73 L31
M991 S0 P30 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z7.56 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z7.56
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10281
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9586
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.723 Z7.8 F60000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10281
M204 S8000
G1 X159.334 Y157.317 E.06056
G1 X159.479 Y157.435 E.00709
G1 X159.805 Y157.862 E.02042
G1 X160.01 Y158.29 E.01801
G1 X160.165 Y159.145 E.03302
G1 X160.071 Y159.572 E.01662
G1 X159.732 Y160 E.02075
G1 X159.334 Y160.323 E.01945
G1 X159.334 Y164.158 E.1457
G1 X159.479 Y164.276 E.00709
G1 X159.805 Y164.703 E.02042
G1 X160.01 Y165.131 E.01801
G1 X160.165 Y165.986 E.03302
G1 X160.147 Y166.066 E.0031
G1 X160.466 Y166.066 E.01209
G1 X160.466 Y164.79 E.04847
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y166.066 E-.48475
G1 X160.147 Y166.066 E-.12096
G1 X160.165 Y165.986 E-.03097
G1 X160.107 Y165.667 E-.12332
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z7.8 F60000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10281
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9586
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z7.8 F60000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10281
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10281
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 7.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 32/82
; update layer progress
M73 L32
M991 S0 P31 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z7.8 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z7.8
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10311
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9512
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.809 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10311
M204 S8000
G1 X159.334 Y157.403 E.06056
G1 X159.385 Y157.435 E.00227
G1 X159.815 Y157.862 E.02304
G1 X160.094 Y158.29 E.0194
G1 X160.431 Y159.145 E.03491
G1 X160.466 Y159.344 E.00768
G1 X160.466 Y159.657 E.0119
G1 X160.303 Y160 E.01441
G1 X159.334 Y160.511 E.0416
G1 X159.334 Y164.244 E.14186
G1 X159.385 Y164.276 E.00227
G1 X159.815 Y164.703 E.02304
G1 X160.094 Y165.131 E.0194
G1 X160.431 Y165.986 E.03491
G1 X160.445 Y166.066 E.00307
G1 X159.334 Y166.066 E.04218
G1 X159.334 Y165.582 E.01838
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y166.066 E-.18386
G1 X160.445 Y166.066 E-.42186
G1 X160.431 Y165.986 E-.03072
G1 X160.312 Y165.683 E-.12356
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10311
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9512
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10311
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10311
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 7.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 33/82
; update layer progress
M73 L33
M991 S0 P32 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z8.04 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z8.04
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10320
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9434
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
M73 P76 R2
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.873 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10320
M204 S8000
G1 X159.334 Y157.467 E.06056
G1 X159.507 Y157.564 E.00751
G1 X159.935 Y157.935 E.02152
G1 X160.466 Y158.688 E.03499
G1 X160.466 Y160.617 E.0733
G1 X160.362 Y160.542 E.00485
G1 X159.935 Y160.51 E.01629
G1 X159.334 Y160.675 E.02365
G1 X159.334 Y164.308 E.13803
G1 X159.507 Y164.405 E.00751
G1 X159.935 Y164.776 E.02152
G1 X160.466 Y165.529 E.03499
G1 X160.466 Y163.935 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y165.529 E-.60572
G1 X160.231 Y165.197 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10320
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9434
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10320
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10320
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 8.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 34/82
; update layer progress
M73 L34
M991 S0 P33 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z8.28 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z8.28
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10662
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9353
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y155.724 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10662
M204 S8000
G1 X160.466 Y154.13 E.06056
G1 X160.362 Y154.044 E.00511
G1 X160.039 Y153.934 E.01297
G1 X159.334 Y153.934 E.02676
G1 X159.334 Y157.49 E.13509
G1 X159.507 Y157.557 E.00704
G1 X159.935 Y157.836 E.01939
G1 X160.466 Y158.409 E.02969
G1 X160.466 Y160.971 E.09732
G1 X160.362 Y160.885 E.00511
G1 X159.935 Y160.74 E.01715
G1 X159.334 Y160.79 E.02288
G1 X159.334 Y164.331 E.13453
G1 X159.507 Y164.398 E.00704
G1 X159.935 Y164.677 E.01939
G1 X160.466 Y165.25 E.02969
G1 X160.466 Y163.656 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y165.25 E-.60572
G1 X160.19 Y164.952 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10662
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9353
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10662
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10662
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 8.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 35/82
; update layer progress
M73 L35
M991 S0 P34 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z8.52 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z8.52
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10675
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
M73 P76 R1
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9269
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y155.983 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10675
M204 S8000
G1 X160.466 Y154.389 E.06056
G1 X160.362 Y154.299 E.00523
G1 X159.935 Y154.08 E.01824
G1 X159.507 Y153.995 E.01656
G1 X159.334 Y153.999 E.00656
G1 X159.334 Y157.484 E.1324
G1 X159.507 Y157.523 E.00673
G1 X159.935 Y157.723 E.01793
G1 X160.362 Y158.053 E.02053
G1 X160.466 Y158.157 E.00557
G1 X160.466 Y161.231 E.11676
G1 X160.362 Y161.14 E.00523
G1 X159.935 Y160.921 E.01824
G1 X159.507 Y160.836 E.01656
M73 P77 R1
G1 X159.334 Y160.84 E.00656
G1 X159.334 Y164.325 E.1324
G1 X159.507 Y164.364 E.00673
G1 X159.935 Y164.564 E.01793
G1 X160.362 Y164.894 E.02053
G1 X160.466 Y164.998 E.00557
G1 X160.466 Y166.066 E.04054
G1 X159.939 Y166.066 E.02002
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X160.466 Y166.066 E-.20019
G1 X160.466 Y164.998 E-.40552
G1 X160.362 Y164.894 E-.05574
G1 X160.157 Y164.736 E-.09855
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10675
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9269
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10675
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10675
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 8.6
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 36/82
; update layer progress
M73 L36
M991 S0 P35 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z8.76 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z8.76
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10694
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9180
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.641 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10694
M204 S8000
G1 X159.334 Y154.047 E.06056
G1 X159.507 Y154.07 E.00662
G1 X159.935 Y154.227 E.0173
G1 X160.362 Y154.513 E.01955
G1 X160.466 Y154.611 E.00541
G1 X160.466 Y157.944 E.12664
G1 X160.362 Y157.849 E.00532
G1 X159.935 Y157.591 E.01898
G1 X159.507 Y157.463 E.01695
G1 X159.334 Y157.452 E.00657
G1 X159.334 Y160.888 E.13057
G1 X159.507 Y160.911 E.00662
G1 X159.935 Y161.068 E.0173
G1 X160.362 Y161.354 E.01955
G1 X160.466 Y161.452 E.00541
G1 X160.466 Y164.785 E.12664
G1 X160.362 Y164.69 E.00532
G1 X159.935 Y164.432 E.01898
G1 X159.507 Y164.304 E.01695
G1 X159.334 Y164.293 E.00657
G1 X159.334 Y165.887 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y164.293 E-.60571
G1 X159.507 Y164.304 E-.06576
G1 X159.73 Y164.371 E-.08853
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10694
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9180
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10694
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10694
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 8.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 37/82
; update layer progress
M73 L37
M991 S0 P36 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z9
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10638
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9089
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.663 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10638
M204 S8000
G1 X159.334 Y154.069 E.06056
G1 X159.507 Y154.12 E.00683
G1 X159.935 Y154.35 E.01845
G1 X160.466 Y154.858 E.02792
G1 X160.466 Y157.711 E.1084
G1 X160.362 Y157.622 E.00518
G1 X159.935 Y157.432 E.01778
G1 X159.507 Y157.377 E.01638
G1 X159.334 Y157.392 E.00659
G1 X159.334 Y160.91 E.13366
G1 X159.507 Y160.961 E.00683
G1 X159.935 Y161.191 E.01845
G1 X160.466 Y161.699 E.02792
G1 X160.466 Y164.552 E.1084
G1 X160.362 Y164.463 E.00518
G1 X159.935 Y164.273 E.01778
G1 X159.507 Y164.218 E.01638
G1 X159.334 Y164.233 E.00659
G1 X159.334 Y165.827 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y164.233 E-.60571
G1 X159.507 Y164.218 E-.06587
G1 X159.738 Y164.247 E-.08842
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10638
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9089
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
M73 P78 R1
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10638
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10638
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 9.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 38/82
; update layer progress
M73 L38
M991 S0 P37 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9.24 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z9.24
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10584
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8993
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.658 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10584
M204 S8000
G1 X159.334 Y154.064 E.06056
G1 X159.507 Y154.143 E.00721
G1 X159.935 Y154.457 E.02015
G1 X160.466 Y155.089 E.03135
G1 X160.466 Y157.423 E.0887
G1 X160.362 Y157.34 E.00504
G1 X159.935 Y157.233 E.01674
G1 X159.334 Y157.328 E.02308
G1 X159.334 Y160.905 E.13591
G1 X159.507 Y160.984 E.00721
G1 X159.935 Y161.298 E.02015
G1 X160.466 Y161.93 E.03135
G1 X160.466 Y164.264 E.0887
G1 X160.362 Y164.181 E.00504
G1 X159.935 Y164.074 E.01674
G1 X159.334 Y164.169 E.02308
G1 X159.334 Y165.763 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y164.169 E-.60571
G1 X159.736 Y164.106 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10584
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8993
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10584
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10584
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 9.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 39/82
; update layer progress
M73 L39
M991 S0 P38 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9.48 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z9.48
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10520
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8895
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.622 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10520
M204 S8000
G1 X159.334 Y154.028 E.06056
G1 X159.507 Y154.137 E.00775
G1 X159.935 Y154.552 E.02265
G1 X160.466 Y155.398 E.03793
G1 X160.466 Y156.992 E.06057
G1 X160.362 Y156.932 E.00453
G1 X159.935 Y156.976 E.01633
G1 X159.334 Y157.195 E.02427
G1 X159.334 Y160.869 E.13958
G1 X159.507 Y160.978 E.00775
G1 X159.935 Y161.393 E.02265
G1 X160.466 Y162.239 E.03793
G1 X160.466 Y163.833 E.06057
G1 X160.362 Y163.774 E.00453
G1 X159.935 Y163.818 E.01633
G1 X159.334 Y164.036 E.02427
G1 X159.334 Y165.63 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y164.036 E-.60571
G1 X159.716 Y163.897 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10520
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8895
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10520
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10520
M204 S8000
M73 P79 R1
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 9.56
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 40/82
; update layer progress
M73 L40
M991 S0 P39 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9.72 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z9.72
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10417
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8793
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.549 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10417
M204 S8000
G1 X159.334 Y153.955 E.06056
G1 X159.422 Y154.014 E.00403
G1 X159.807 Y154.442 E.02185
G1 X160.055 Y154.869 E.01879
G1 X160.314 Y155.724 E.03394
G1 X160.302 Y156.152 E.01625
G1 X160.005 Y156.58 E.01978
G1 X159.334 Y157.032 E.03073
G1 X159.334 Y160.796 E.14301
G1 X159.422 Y160.855 E.00403
G1 X159.807 Y161.283 E.02185
G1 X160.055 Y161.71 E.01879
G1 X160.314 Y162.565 E.03394
G1 X160.302 Y162.993 E.01625
G1 X160.005 Y163.421 E.01978
G1 X159.334 Y163.873 E.03073
G1 X159.334 Y165.467 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y163.873 E-.60571
G1 X159.671 Y163.646 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10417
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8793
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10417
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10417
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 9.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 41/82
; update layer progress
M73 L41
M991 S0 P40 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9.96 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z9.96
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10348
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8687
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y154.495 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10348
M204 S8000
G1 X160.466 Y153.934 E.02129
G1 X159.432 Y153.934 E.03927
G1 X159.52 Y154.014 E.00453
G1 X159.81 Y154.442 E.01961
G1 X159.985 Y154.869 E.01756
G1 X160.075 Y155.724 E.03267
G1 X159.942 Y156.152 E.01702
G1 X159.589 Y156.58 E.02106
G1 X159.334 Y156.809 E.01302
G1 X159.334 Y160.688 E.14738
G1 X159.52 Y160.855 E.0095
G1 X159.81 Y161.283 E.01961
G1 X159.985 Y161.71 E.01756
G1 X160.075 Y162.565 E.03267
G1 X159.942 Y162.993 E.01702
G1 X159.589 Y163.421 E.02106
G1 X159.334 Y163.65 E.01302
G1 X159.334 Y165.244 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y163.65 E-.60571
G1 X159.589 Y163.421 E-.13026
G1 X159.63 Y163.372 E-.02403
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10348
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8687
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10348
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10348
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 10.04
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 42/82
; update layer progress
M73 L42
M991 S0 P41 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z10.2 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z10.2
G1 Z10.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10308
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8579
M204 S5000
M73 P80 R1
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y154.631 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10308
M204 S8000
G1 X160.466 Y153.934 E.02645
G1 X159.568 Y153.934 E.03411
G1 X159.631 Y154.014 E.00387
G1 X159.84 Y154.442 E.01808
G1 X159.946 Y154.869 E.01673
G1 X159.965 Y155.297 E.01626
G1 X159.889 Y155.724 E.0165
G1 X159.679 Y156.152 E.0181
G1 X159.334 Y156.547 E.01992
G1 X159.334 Y160.482 E.14953
G1 X159.631 Y160.855 E.0181
G1 X159.84 Y161.283 E.01808
G1 X159.946 Y161.71 E.01673
G1 X159.965 Y162.138 E.01626
G1 X159.889 Y162.565 E.0165
G1 X159.679 Y162.993 E.0181
G1 X159.334 Y163.388 E.01992
G1 X159.334 Y164.982 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y163.388 E-.60571
G1 X159.602 Y163.082 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10308
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8579
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10308
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10308
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 10.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 43/82
; update layer progress
M73 L43
M991 S0 P42 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z10.44 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z10.44
G1 Z10.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10281
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8468
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y154.773 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10281
M204 S8000
G1 X160.466 Y153.934 E.03188
G1 X159.711 Y153.934 E.02868
G1 X159.76 Y154.014 E.00357
G1 X159.897 Y154.442 E.01705
G1 X159.935 Y154.869 E.01631
G1 X159.886 Y155.297 E.01635
G1 X159.739 Y155.724 E.01718
G1 X159.462 Y156.152 E.01936
G1 X159.334 Y156.288 E.00707
G1 X159.334 Y160.256 E.15076
G1 X159.493 Y160.428 E.0089
G1 X159.76 Y160.855 E.01915
G1 X159.897 Y161.283 E.01705
G1 X159.935 Y161.71 E.01631
G1 X159.886 Y162.138 E.01635
G1 X159.739 Y162.565 E.01718
G1 X159.462 Y162.993 E.01936
G1 X159.334 Y163.129 E.00707
G1 X159.334 Y164.723 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y163.129 E-.60571
G1 X159.462 Y162.993 E-.07068
G1 X159.581 Y162.808 E-.08361
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10281
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8468
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10281
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10281
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 10.52
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 44/82
; update layer progress
M73 L44
M991 S0 P43 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z10.68 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z10.68
G1 Z10.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10266
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8355
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y154.941 Z10.92 F60000
G1 Z10.52
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10266
M204 S8000
G1 X160.466 Y153.934 E.03825
G1 X159.878 Y153.934 E.02231
G1 X159.915 Y154.014 E.00334
G1 X159.98 Y154.442 E.01643
M73 P81 R1
G1 X159.95 Y154.869 E.01628
G1 X159.834 Y155.297 E.01683
G1 X159.613 Y155.724 E.01828
G1 X159.334 Y156.062 E.01662
G1 X159.334 Y159.989 E.14923
G1 X159.716 Y160.428 E.02208
G1 X159.915 Y160.855 E.01792
G1 X159.98 Y161.283 E.01643
G1 X159.95 Y161.71 E.01628
G1 X159.834 Y162.138 E.01683
G1 X159.613 Y162.565 E.01828
G1 X159.334 Y162.903 E.01662
G1 X159.334 Y164.497 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y162.903 E-.60571
G1 X159.593 Y162.59 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z10.92 F60000
G1 Z10.52
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10266
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8355
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z10.92 F60000
G1 Z10.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10266
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10266
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 10.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 45/82
; update layer progress
M73 L45
M991 S0 P44 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z10.92 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z10.92
G1 Z10.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10265
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8239
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y155.149 Z11.16 F60000
G1 Z10.76
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10265
M204 S8000
G1 X160.466 Y153.934 E.04614
G1 X160.086 Y153.934 E.01442
G1 X160.108 Y154.014 E.00314
G1 X159.994 Y154.869 E.03278
G1 X159.807 Y155.297 E.01772
G1 X159.505 Y155.724 E.0199
G1 X159.334 Y155.872 E.00856
G1 X159.334 Y159.735 E.14675
G1 X159.64 Y160 E.01539
G1 X159.989 Y160.428 E.02096
G1 X160.108 Y160.855 E.01686
G1 X159.994 Y161.71 E.03278
G1 X159.807 Y162.138 E.01772
G1 X159.505 Y162.565 E.0199
G1 X159.334 Y162.713 E.00856
G1 X159.334 Y164.307 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y162.713 E-.60571
G1 X159.505 Y162.565 E-.08558
G1 X159.609 Y162.418 E-.06871
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z11.16 F60000
G1 Z10.76
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10265
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8239
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z11.16 F60000
G1 Z10.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10265
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10265
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 11
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 46/82
; update layer progress
M73 L46
M991 S0 P45 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z11.16 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z11.16
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10304
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8121
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y154.503 Z11.4 F60000
G1 Z11
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10304
M204 S8000
G1 X159.334 Y153.934 E.02162
G1 X160.359 Y153.934 E.03894
G1 X160.356 Y154.014 E.00303
G1 X160.069 Y154.869 E.03427
G1 X159.809 Y155.297 E.01901
G1 X159.408 Y155.724 E.02228
G1 X159.334 Y155.775 E.00339
G1 X159.334 Y159.542 E.14315
G1 X160.1 Y160 E.03387
G1 X160.373 Y160.428 E.01929
G1 X160.356 Y160.855 E.01626
G1 X160.069 Y161.71 E.03427
G1 X159.809 Y162.138 E.01901
G1 X159.408 Y162.565 E.02228
G1 X159.334 Y162.616 E.00339
G1 X159.334 Y164.21 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y162.616 E-.60571
G1 X159.408 Y162.565 E-.03389
G1 X159.625 Y162.334 E-.1204
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z11.4 F60000
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10304
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8121
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
M73 P82 R1
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z11.4 F60000
G1 Z11
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10304
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10304
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 11.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 47/82
; update layer progress
M73 L47
M991 S0 P46 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z11.4 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z11.4
G1 Z11.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10312
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8001
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y155.967 Z11.64 F60000
G1 Z11.24
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10312
M204 S8000
G1 X160.466 Y154.373 E.06056
G1 X159.935 Y155.2 E.03736
G1 X159.507 Y155.599 E.0222
G1 X159.334 Y155.703 E.00766
G1 X159.334 Y159.361 E.13899
G1 X159.935 Y159.559 E.02401
G1 X160.362 Y159.57 E.01625
G1 X160.466 Y159.503 E.00469
G1 X160.466 Y161.214 E.065
G1 X159.935 Y162.041 E.03736
G1 X159.507 Y162.44 E.0222
G1 X159.334 Y162.544 E.00766
G1 X159.334 Y164.138 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y162.544 E-.60571
G1 X159.507 Y162.44 E-.07661
G1 X159.657 Y162.3 E-.07768
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z11.64 F60000
G1 Z11.24
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10312
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8001
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z11.64 F60000
G1 Z11.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10312
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10312
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 11.48
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 48/82
; update layer progress
M73 L48
M991 S0 P47 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z11.64 I1.049 J-.617 P1  F60000
G1 X160.806 Y153.593 Z11.64
G1 Z11.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10323
M204 S8000
G1 X160.806 Y166.407 E.4868
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.746 Y153.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y153.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7879
M204 S5000
G1 X161.19 Y166.79 E.4771
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.13 Y153.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.139 Y155.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y156.283 Z11.88 F60000
G1 Z11.48
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10323
M204 S8000
G1 X160.466 Y154.689 E.06056
G1 X159.935 Y155.297 E.03067
G1 X159.507 Y155.597 E.01985
G1 X159.334 Y155.672 E.00714
G1 X159.334 Y159.235 E.13538
G1 X159.935 Y159.312 E.02299
G1 X160.362 Y159.191 E.01689
G1 X160.466 Y159.106 E.00507
G1 X160.466 Y161.53 E.09209
G1 X159.935 Y162.138 E.03067
G1 X159.507 Y162.438 E.01985
G1 X159.334 Y162.513 E.00714
G1 X159.334 Y164.107 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 F11292.473
G1 X159.334 Y162.513 E-.60571
G1 X159.507 Y162.438 E-.07145
G1 X159.685 Y162.313 E-.08284
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y163.407 Z11.88 F60000
G1 Z11.48
G1 E.8 F1800
; FEATURE: Inner wall
G1 F10323
M204 S8000
G1 X164.193 Y156.593 E.25885
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.253 Y163.407 E.0666
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7879
M204 S5000
G1 X163.81 Y156.21 E.2663
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
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

G1 X163.87 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X163.854 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z11.88 F60000
G1 Z11.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F10323
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F10323
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 11.72
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F13282.957
M73 P83 R1
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 49/82
; update layer progress
M73 L49
M991 S0 P48 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z11.88 I-.683 J-1.007 P1  F60000
G1 X160.806 Y163.407 Z11.88
G1 Z11.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.006 Y153.593 E.03849
G1 X160.406 Y153.593 E.0152
G1 F10752.706
G1 X160.806 Y153.593 E.0152
G1 F9505.954
G1 X160.806 Y153.793 E.0076
G1 F8911.378
G1 X160.806 Y154.193 E.0152
G1 F7779.826
G1 X160.806 Y154.593 E.0152
G1 F6725.074
G1 X160.806 Y154.993 E.0152
G1 F5747.122
G1 X160.806 Y155.393 E.0152
G1 F4845.97
G1 X160.806 Y155.793 E.0152
G1 F4021.618
G1 X160.806 Y156.193 E.0152
G1 F3274.066
G1 X160.806 Y156.593 E.0152
G1 F2603.314
G1 X161.217 Y156.593 E.01561
M106 S178.5
G1 F1994.114
G1 X161.6 Y156.593 E.01453
M106 S0
; FEATURE: Overhang wall
M106 S178.5
G1 F1500
M204 S5000
G1 X163.4 Y156.593 E.06839
M106 S0
; FEATURE: Inner wall
M106 S178.5
G1 F2100
M204 S8000
G1 X163.782 Y156.593 E.01453
M106 S0
G1 F2706.344
G1 X164.182 Y156.593 E.0152
G1 F3389.487
G1 X164.582 Y156.593 E.0152
G1 F4149.431
G1 X164.982 Y156.593 E.0152
G1 F4986.175
G1 X165.382 Y156.593 E.0152
G1 F5899.718
G1 X165.782 Y156.593 E.0152
G1 F6444.924
G1 X166.007 Y156.593 E.00851
G1 F7478.281
G1 X166.007 Y156.993 E.0152
G1 F8588.438
G1 X166.007 Y157.393 E.0152
G1 F9775.396
G1 X166.007 Y157.793 E.0152
G1 F11039.153
G1 X166.007 Y158.193 E.0152
G1 F11292.473
G1 X166.007 Y158.593 E.0152
G1 X166.007 Y161.407 E.10688
G1 X166.007 Y161.807 E.0152
G1 F10794.611
G1 X166.007 Y162.207 E.0152
G1 F9545.357
G1 X166.007 Y162.607 E.0152
G1 F8372.903
G1 X166.007 Y163.007 E.0152
G1 F7277.249
G1 X166.007 Y163.407 E.0152
G1 F6258.396
G1 X165.782 Y163.407 E.00851
G1 F5721.314
G1 X165.382 Y163.407 E.0152
G1 F4822.273
G1 X164.982 Y163.407 E.0152
G1 F4000.034
G1 X164.582 Y163.407 E.0152
G1 F3254.594
G1 X164.182 Y163.407 E.0152
G1 F2585.954
G1 X163.782 Y163.407 E.0152
M106 S178.5
G1 F1994.114
G1 X163.4 Y163.407 E.01453
M106 S0
; FEATURE: Overhang wall
M106 S178.5
G1 F1500
M204 S5000
G1 X161.6 Y163.407 E.06839
M106 S0
; FEATURE: Inner wall
M106 S178.5
G1 F2100
M204 S8000
G1 X161.217 Y163.407 E.01453
M106 S0
G1 F2627.939
G1 X160.866 Y163.407 E.01334
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7757
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X159.99 Y153.21 E.04848
G1 X160.39 Y153.21 E.01405
G1 X160.79 Y153.21 E.01405
G1 X161.19 Y153.21 E.01405
G1 X161.19 Y153.41 E.00703
G1 X161.19 Y153.81 E.01405
G1 F6767.064
G1 X161.19 Y154.21 E.01405
G1 F5785.944
G1 X161.19 Y154.61 E.01405
G1 F4881.624
G1 X161.19 Y155.01 E.01405
G1 F4054.104
G1 X161.19 Y155.41 E.01405
G1 F3303.384
G1 X161.19 Y155.81 E.01405
G1 F2629.464
G1 X161.19 Y156.21 E.01405
G1 F2032.344
G1 X161.231 Y156.21 E.00144
M106 S178.5
G1 F1975.479
G1 X161.6 Y156.21 E.01296
M106 S0
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45
M106 S178.5
G1 F1500
G1 X163.4 Y156.21 E.06839
M106 S0
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M106 S178.5
G1 F2100
G1 X163.769 Y156.21 E.01296
M106 S0
G1 F2706.344
G1 X164.169 Y156.21 E.01405
G1 F3389.487
G1 X164.569 Y156.21 E.01405
G1 F4149.431
G1 X164.969 Y156.21 E.01405
G1 F4986.175
G1 X165.369 Y156.21 E.01405
G1 F5899.718
G1 X165.769 Y156.21 E.01405
G1 F6890.062
G1 X166.169 Y156.21 E.01405
G1 F7470.191
G1 X166.39 Y156.21 E.00776
G1 F7757
G1 X166.39 Y156.61 E.01405
G1 X166.39 Y157.01 E.01405
G1 X166.39 Y157.41 E.01405
G1 X166.39 Y157.81 E.01405
G1 X166.39 Y162.19 E.15388
G1 X166.39 Y162.59 E.01405
G1 X166.39 Y162.99 E.01405
G1 X166.39 Y163.39 E.01405
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

G1 X166.39 Y163.79 E.01405
G1 F7233.65
G1 X166.169 Y163.79 E.00776
G1 F6662.967
G1 X165.769 Y163.79 E.01405
G1 F5689.719
G1 X165.369 Y163.79 E.01405
G1 F4793.271
G1 X164.969 Y163.79 E.01405
G1 F3973.623
G1 X164.569 Y163.79 E.01405
G1 F3230.775
G1 X164.169 Y163.79 E.01405
G1 F2564.727
G1 X163.769 Y163.79 E.01405
M106 S178.5
G1 F1975.479
G1 X163.4 Y163.79 E.01296
M106 S0
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45
M106 S178.5
G1 F1500
G1 X161.6 Y163.79 E.06839
M106 S0
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M106 S178.5
G1 F2100
G1 X161.25 Y163.79 E.0123
M106 S0
M204 S10000
G1 X160.466 Y164.077 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y165.671 E.06056
G1 X160.362 Y165.761 E.0052
G1 X159.935 Y165.962 E.01795
G1 X159.507 Y166.029 E.01644
G1 X159.334 Y166.017 E.00657
G1 X159.334 Y162.512 E.13318
G1 X159.507 Y162.466 E.00679
G1 X159.935 Y162.247 E.01824
G1 X160.388 Y161.869 E.02243
G1 X160.388 Y158.897 E.11292
G1 X159.935 Y159.121 E.01921
G1 X159.507 Y159.188 E.01644
G1 X159.334 Y159.176 E.00657
G1 X159.334 Y155.671 E.13318
G1 X159.507 Y155.625 E.00679
G1 X159.935 Y155.406 E.01824
G1 X160.362 Y155.055 E.02102
G1 X160.466 Y154.948 E.00566
G1 X160.466 Y156.542 E.06056
; WIPE_START
G1 X160.466 Y154.948 E-.60572
G1 X160.362 Y155.055 E-.05665
G1 X160.164 Y155.218 E-.09764
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z12.12 I-.481 J1.118 P1  F60000
G1 X164.963 Y157.282 Z12.12
G1 Z11.72
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.439804
M106 S178.5
G1 F1500
M204 S8000
G1 X160.772 Y157.282 E.15517
G1 X160.772 Y157.67 E.01438
G1 X164.797 Y157.67 E.14903
G1 X164.797 Y158.059 E.01438
G1 X160.772 Y158.059 E.14903
G1 X160.772 Y158.447 E.01438
G1 X164.797 Y158.447 E.14903
G1 X164.797 Y158.835 E.01438
G1 X160.772 Y158.835 E.14903
G1 X160.772 Y159.223 E.01438
G1 X164.797 Y159.223 E.14903
G1 X164.797 Y159.612 E.01438
G1 X160.772 Y159.612 E.14903
G1 X160.772 Y160 E.01438
G1 X164.797 Y160 E.14903
G1 X164.797 Y160.388 E.01438
G1 X160.772 Y160.388 E.14903
G1 X160.772 Y160.777 E.01438
G1 X164.797 Y160.777 E.14903
G1 X164.797 Y161.165 E.01438
G1 X160.772 Y161.165 E.14903
G1 X160.772 Y161.553 E.01438
G1 X164.797 Y161.553 E.14903
G1 X164.797 Y161.942 E.01438
G1 X160.772 Y161.942 E.14903
G1 X160.772 Y162.33 E.01438
G1 X164.797 Y162.33 E.14903
G1 X164.797 Y162.718 E.01438
G1 X160.606 Y162.718 E.15517
M106 S0
; WIPE_START
G1 X162.606 Y162.718 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z12.12 I-.132 J1.21 P1  F60000
G1 X165.188 Y163.001 Z12.12
G1 Z11.72
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.464374
G1 F10899.315
M204 S8000
G1 X165.601 Y163.001 E.01625
G1 X165.601 Y156.999 E.23625
G1 X165.188 Y156.999 E.01625
G1 X165.188 Y162.941 E.23388
; CHANGE_LAYER
; Z_HEIGHT: 11.96
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10899.315
G1 X165.188 Y160.941 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 50/82
; update layer progress
M73 L50
M991 S0 P49 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z12.12 I-.597 J-1.061 P1  F60000
G1 X160.806 Y163.407 Z12.12
M73 P84 R1
G1 Z11.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7639
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
M204 S10000
G1 X160.466 Y163.849 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y165.443 E.06056
G1 X160.362 Y165.539 E.00535
G1 X159.935 Y165.808 E.01919
G1 X159.507 Y165.946 E.01707
G1 X159.334 Y165.962 E.00659
G1 X159.334 Y162.538 E.13011
G1 X159.507 Y162.519 E.0066
G1 X159.935 Y162.374 E.01716
G1 X160.388 Y162.074 E.02065
G1 X160.388 Y158.674 E.12917
G1 X159.935 Y158.967 E.0205
G1 X159.507 Y159.105 E.01707
G1 X159.334 Y159.121 E.00659
G1 X159.334 Y155.697 E.13011
G1 X159.507 Y155.678 E.0066
G1 X159.935 Y155.533 E.01716
G1 X160.362 Y155.257 E.01933
G1 X160.466 Y155.16 E.00537
G1 X160.466 Y153.934 E.04658
G1 X160.098 Y153.934 E.01398
; WIPE_START
G1 X160.466 Y153.934 E-.13983
G1 X160.466 Y155.16 E-.46589
G1 X160.362 Y155.257 E-.05374
G1 X160.14 Y155.4 E-.10055
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z12.36 I-.717 J.983 P1  F60000
G1 X165.623 Y159.403 Z12.36
G1 Z11.96
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.419994
G1 F12000
M204 S8000
G1 X165.623 Y156.977 E.08522
G1 X160.772 Y156.977 E.17044
G1 X160.772 Y163.023 E.21241
G1 X165.623 Y163.023 E.17044
G1 X165.623 Y159.463 E.12508
M204 S10000
G1 X165.255 Y159.403 F60000
G1 F12000
M204 S8000
G1 X165.255 Y157.345 E.07228
G1 X161.14 Y157.345 E.14455
G1 X161.14 Y162.655 E.18652
G1 X165.255 Y162.655 E.14455
G1 X165.255 Y159.463 E.11214
M204 S10000
G1 X164.886 Y159.403 F60000
G1 F12000
M204 S8000
G1 X164.886 Y157.714 E.05933
G1 X161.509 Y157.714 E.11866
G1 X161.509 Y162.286 E.16063
G1 X164.886 Y162.286 E.11866
G1 X164.886 Y159.463 E.09919
M204 S10000
G1 X164.518 Y159.403 F60000
G1 F12000
M204 S8000
G1 X164.518 Y158.082 E.04638
G1 X161.877 Y158.082 E.09277
G1 X161.877 Y161.918 E.13474
G1 X164.518 Y161.918 E.09277
G1 X164.518 Y159.463 E.08624
M204 S10000
G1 X164.149 Y159.403 F60000
G1 F12000
M204 S8000
G1 X164.149 Y158.451 E.03344
G1 X162.245 Y158.451 E.06688
G1 X162.245 Y161.549 E.10884
G1 X164.149 Y161.549 E.06688
G1 X164.149 Y159.463 E.0733
M204 S10000
G1 X163.781 Y159.403 F60000
G1 F12000
M204 S8000
G1 X163.781 Y158.819 E.02049
G1 X162.614 Y158.819 E.04099
G1 X162.614 Y161.181 E.08295
G1 X163.781 Y161.181 E.04099
G1 X163.781 Y159.463 E.06035
M204 S10000
G1 X163.397 Y159.403 F60000
; LINE_WIDTH: 0.450564
G1 F11276.501
M204 S8000
G1 X163.397 Y159.203 E.00759
G1 X162.998 Y159.203 E.01518
G1 X162.998 Y160.797 E.06063
G1 X163.397 Y160.797 E.01518
G1 X163.397 Y159.463 E.05076
; CHANGE_LAYER
; Z_HEIGHT: 12.2
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11276.501
G1 X163.397 Y160.797 E-.50697
G1 X162.998 Y160.797 E-.15165
G1 X162.998 Y160.53 E-.10138
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 51/82
; update layer progress
M73 L51
M991 S0 P50 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z12.36 I-.968 J-.737 P1  F60000
G1 X160.806 Y163.407 Z12.36
G1 Z12.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7533
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
M204 S10000
G1 X160.466 Y163.636 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y165.23 E.06056
G1 X160.362 Y165.336 E.00563
G1 X159.935 Y165.679 E.02082
G1 X159.507 Y165.89 E.01812
G1 X159.334 Y165.934 E.00676
G1 X159.334 Y162.59 E.12703
G1 X159.507 Y162.599 E.00657
G1 X159.935 Y162.525 E.01649
G1 X160.362 Y162.317 E.01807
G1 X161.105 Y161.64 E.03816
G1 X161.105 Y160.046 E.06056
; WIPE_START
G1 X161.105 Y161.64 E-.60572
G1 X160.805 Y161.914 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y160.687 Z12.6 F60000
G1 Z12.2
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X159.334 Y159.093 E.06056
G1 X159.507 Y159.049 E.00676
G1 X159.935 Y158.838 E.01812
G1 X160.362 Y158.495 E.02082
G1 X160.79 Y158.056 E.02328
G1 X161.105 Y157.821 E.01495
G1 X161.105 Y156.934 E.03367
G1 X160.466 Y156.934 E.02429
G1 X160.466 Y155.386 E.05885
G1 X160.362 Y155.476 E.00521
G1 X159.935 Y155.684 E.01807
G1 X159.507 Y155.758 E.01649
G1 X159.334 Y155.749 E.00657
G1 X159.334 Y154.155 E.06056
; WIPE_START
G1 X159.334 Y155.749 E-.60571
G1 X159.507 Y155.758 E-.06569
G1 X159.737 Y155.718 E-.0886
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.351 Y161.16 Z12.6 F60000
G1 Z12.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.460594
G1 F11000.026
M204 S8000
G1 X163.76 Y161.16 E.01596
G1 X163.76 Y158.84 E.09051
G1 X163.351 Y158.84 E.01596
G1 X163.351 Y161.1 E.08817
M204 S10000
G1 X162.962 Y161.549 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X164.149 Y161.549 E.04169
G1 X164.149 Y158.451 E.10884
G1 X162.962 Y158.451 E.04169
G1 X162.962 Y161.489 E.10674
M204 S10000
G1 X162.594 Y161.918 F60000
G1 F12212.001
M204 S8000
G1 X164.518 Y161.918 E.06758
G1 X164.518 Y158.082 E.13474
G1 X162.594 Y158.082 E.06758
G1 X162.594 Y161.858 E.13263
M204 S10000
G1 X162.225 Y162.286 F60000
G1 F12212.001
M204 S8000
G1 X164.886 Y162.286 E.09347
G1 X164.886 Y157.714 E.16063
G1 X162.225 Y157.714 E.09347
G1 X162.225 Y162.226 E.15852
M204 S10000
G1 X161.857 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X165.255 Y162.655 E.11936
M73 P85 R1
G1 X165.255 Y157.345 E.18652
G1 X161.857 Y157.345 E.11936
G1 X161.857 Y162.595 E.18441
M204 S10000
G1 X161.488 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.14526
G1 X165.623 Y156.977 E.21241
G1 X161.488 Y156.977 E.14526
G1 X161.488 Y162.963 E.2103
; CHANGE_LAYER
; Z_HEIGHT: 12.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12212.001
G1 X161.488 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 52/82
; update layer progress
M73 L52
M991 S0 P51 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z12.6 I-1.172 J-.327 P1  F60000
G1 X160.806 Y163.407 Z12.6
G1 Z12.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7235
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7235
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
M204 S10000
G1 X160.466 Y163.381 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7235
M204 S8000
G1 X160.466 Y164.975 E.06056
G1 X159.935 Y165.569 E.03027
G1 X159.507 Y165.86 E.01966
G1 X159.334 Y165.932 E.0071
G1 X159.334 Y162.646 E.12486
G1 X159.935 Y162.712 E.02294
G1 X160.362 Y162.581 E.01699
G1 X160.79 Y162.229 E.02104
G1 X161.645 Y161.272 E.04875
G1 X162.072 Y160.981 E.01966
G1 X162.5 Y160.803 E.01759
G1 X163.355 Y160.709 E.03269
G1 X163.783 Y160.84 E.01699
G1 X164.21 Y161.192 E.02104
G1 X165.065 Y162.148 E.04875
G1 X165.493 Y162.44 E.01966
G1 X165.666 Y162.512 E.0071
G1 X165.666 Y159.225 E.12486
G1 X165.065 Y159.291 E.02294
G1 X164.638 Y159.16 E.01699
G1 X164.21 Y158.809 E.02104
G1 X163.355 Y157.852 E.04875
G1 X162.928 Y157.56 E.01966
G1 X162.5 Y157.383 E.01759
G1 X161.645 Y157.288 E.03269
G1 X161.217 Y157.419 E.01699
G1 X160.79 Y157.771 E.02104
G1 X159.935 Y158.728 E.04875
G1 X159.507 Y159.019 E.01966
G1 X159.334 Y159.091 E.0071
G1 X159.334 Y155.804 E.12486
G1 X159.935 Y155.871 E.02294
G1 X160.362 Y155.74 E.01699
G1 X160.466 Y155.655 E.00508
G1 X160.466 Y156.934 E.04861
G1 X160.78 Y156.934 E.01195
; CHANGE_LAYER
; Z_HEIGHT: 12.68
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F11292.473
G1 X160.466 Y156.934 E-.11949
G1 X160.466 Y155.655 E-.48623
G1 X160.362 Y155.74 E-.05085
G1 X160.102 Y155.82 E-.10343
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 53/82
; update layer progress
M73 L53
M991 S0 P52 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z12.84 I-1.212 J.113 P1  F60000
G1 X160.806 Y163.407 Z12.84
G1 Z12.68
G1 E.8 F1800
; FEATURE: Inner wall
G1 F7711
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7396
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.262 Y166.066 Z13.08 F60000
G1 Z12.68
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7711
M204 S8000
G1 X160.466 Y166.066 E.00774
G1 X160.466 Y164.675 E.05282
G1 X159.935 Y165.471 E.03634
G1 X159.507 Y165.859 E.02193
G1 X159.334 Y165.96 E.0076
G1 X159.334 Y162.767 E.1213
G1 X159.935 Y162.952 E.02386
G1 X160.362 Y162.945 E.01625
G1 X160.79 Y162.652 E.01971
G1 X161.645 Y161.37 E.05854
G1 X162.072 Y160.982 E.02193
G1 X162.5 Y160.732 E.01883
G1 X163.355 Y160.469 E.03399
G1 X163.783 Y160.475 E.01625
G1 X164.21 Y160.769 E.01971
G1 X165.065 Y162.051 E.05854
G1 X165.493 Y162.438 E.02193
G1 X165.666 Y162.539 E.0076
G1 X165.666 Y159.347 E.1213
G1 X165.065 Y159.531 E.02386
G1 X164.638 Y159.525 E.01625
G1 X164.21 Y159.231 E.01971
G1 X163.355 Y157.949 E.05854
G1 X162.928 Y157.562 E.02193
G1 X162.5 Y157.311 E.01883
G1 X161.645 Y157.048 E.03399
G1 X161.217 Y157.055 E.01625
G1 X160.79 Y157.348 E.01971
G1 X159.935 Y158.63 E.05854
G1 X159.507 Y159.018 E.02193
G1 X159.334 Y159.119 E.0076
G1 X159.334 Y155.926 E.1213
G1 X159.935 Y156.111 E.02386
G1 X160.362 Y156.104 E.01625
G1 X160.466 Y156.033 E.00476
G1 X160.466 Y154.439 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 12.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y156.033 E-.60571
G1 X160.362 Y156.104 E-.04763
G1 X160.082 Y156.109 E-.10666
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 54/82
; update layer progress
M73 L54
M991 S0 P53 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z13.08 I-1.211 J.12 P1  F60000
G1 X160.806 Y163.407 Z13.08
G1 Z12.92
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8349
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7363
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.434 Z13.32 F60000
G1 Z12.92
M73 P86 R1
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8349
M204 S8000
G1 X159.334 Y166.028 E.06056
G1 X159.399 Y165.986 E.00294
G1 X159.811 Y165.558 E.02257
G1 X160.079 Y165.131 E.01916
G1 X160.385 Y164.276 E.0345
G1 X160.423 Y163.848 E.01631
G1 X160.17 Y163.421 E.01887
G1 X159.334 Y162.942 E.03658
G1 X159.334 Y159.187 E.14265
G1 X159.399 Y159.145 E.00294
G1 X159.811 Y158.717 E.02257
G1 X160.079 Y158.29 E.01916
G1 X160.385 Y157.435 E.0345
G1 X160.423 Y157.007 E.01631
G1 X160.17 Y156.58 E.01887
G1 X159.334 Y156.101 E.03658
G1 X159.334 Y154.507 E.06056
; WIPE_START
G1 F11292.473
G1 X159.334 Y156.101 E-.60571
G1 X159.687 Y156.303 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.632 Y156.934 Z13.32 F60000
G1 Z12.92
G1 E.8 F1800
G1 F8349
M204 S8000
G1 X162.039 Y156.934 E.06056
G1 X162.82 Y157.435 E.03524
G1 X163.232 Y157.862 E.02257
G1 X163.499 Y158.29 E.01916
G1 X163.805 Y159.145 E.0345
G1 X163.843 Y159.572 E.01631
G1 X163.59 Y160 E.01887
G1 X162.833 Y160.428 E.03304
G1 X162.18 Y160.855 E.02964
G1 X161.768 Y161.283 E.02257
G1 X161.501 Y161.71 E.01916
G1 X161.195 Y162.565 E.0345
G1 X161.157 Y162.993 E.01631
G1 X161.2 Y163.066 E.0032
G1 X165.666 Y163.066 E.16966
G1 X165.666 Y162.608 E.01739
G1 X165.601 Y162.565 E.00294
G1 X165.189 Y162.138 E.02257
G1 X164.921 Y161.71 E.01916
G1 X164.615 Y160.855 E.0345
G1 X164.578 Y160.428 E.01631
G1 X164.83 Y160 E.01887
G1 X165.666 Y159.521 E.03657
G1 X165.666 Y157.927 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 13.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X165.666 Y159.521 E-.60571
G1 X165.313 Y159.723 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 55/82
; update layer progress
M73 L55
M991 S0 P54 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z13.32 I-.77 J-.942 P1  F60000
G1 X160.806 Y163.407 Z13.32
G1 Z13.16
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8041
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7343
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y165.537 Z13.56 F60000
G1 Z13.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8041
M204 S8000
G1 X160.466 Y166.066 E.0201
G1 X159.4 Y166.066 E.04046
G1 X159.495 Y165.986 E.00468
G1 X159.806 Y165.558 E.0201
G1 X160 Y165.131 E.01783
G1 X160.13 Y164.276 E.03286
G1 X160.02 Y163.848 E.01677
G1 X159.675 Y163.421 E.02088
G1 X159.334 Y163.132 E.01695
G1 X159.334 Y159.28 E.14635
G1 X159.495 Y159.145 E.00797
G1 X159.806 Y158.717 E.0201
G1 X160 Y158.29 E.01783
G1 X160.13 Y157.435 E.03286
G1 X160.02 Y157.007 E.01677
G1 X159.675 Y156.58 E.02088
G1 X159.334 Y156.291 E.01695
G1 X159.334 Y153.934 E.08955
G1 X160.466 Y153.934 E.04297
G1 X160.466 Y156.934 E.11398
G1 X162.324 Y156.934 E.07061
G1 X162.915 Y157.435 E.02942
G1 X163.227 Y157.862 E.0201
G1 X163.42 Y158.29 E.01783
G1 X163.55 Y159.145 E.03286
G1 X163.441 Y159.572 E.01677
G1 X163.095 Y160 E.02088
G1 X162.085 Y160.855 E.05029
G1 X161.773 Y161.283 E.0201
G1 X161.58 Y161.71 E.01783
G1 X161.45 Y162.565 E.03286
G1 X161.559 Y162.993 E.01677
G1 X161.618 Y163.066 E.00355
G1 X165.666 Y163.066 E.15378
G1 X165.666 Y162.701 E.01385
G1 X165.505 Y162.565 E.00797
G1 X165.194 Y162.138 E.0201
G1 X165 Y161.71 E.01783
G1 X164.87 Y160.855 E.03286
G1 X164.98 Y160.428 E.01677
G1 X165.325 Y160 E.02088
G1 X165.666 Y159.712 E.01694
G1 X165.666 Y158.118 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 13.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X165.666 Y159.712 E-.60571
G1 X165.356 Y159.974 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 56/82
; update layer progress
M73 L56
M991 S0 P55 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z13.56 I-.733 J-.971 P1  F60000
G1 X160.806 Y163.407 Z13.56
G1 Z13.4
G1 E.8 F1800
; FEATURE: Inner wall
G1 F7969
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7327
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y165.411 Z13.8 F60000
G1 Z13.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7969
M204 S8000
G1 X160.466 Y166.066 E.02486
G1 X159.526 Y166.066 E.0357
G1 X159.602 Y165.986 E.00418
G1 X159.83 Y165.558 E.01841
G1 X159.953 Y165.131 E.0169
G1 X159.99 Y164.703 E.0163
G1 X159.932 Y164.276 E.01639
G1 X159.74 Y163.848 E.01781
G1 X159.334 Y163.382 E.02349
G1 X159.334 Y159.426 E.15029
G1 X159.602 Y159.145 E.01473
G1 X159.83 Y158.717 E.01841
G1 X159.953 Y158.29 E.0169
G1 X159.99 Y157.862 E.0163
G1 X159.932 Y157.435 E.01639
G1 X159.74 Y157.007 E.01781
G1 X159.334 Y156.541 E.02349
G1 X159.334 Y153.934 E.09901
G1 X160.466 Y153.934 E.04297
G1 X160.466 Y156.934 E.11398
G1 X162.546 Y156.934 E.07904
G1 X163.022 Y157.435 E.02624
G1 X163.251 Y157.862 E.01841
G1 X163.374 Y158.29 E.0169
G1 X163.41 Y158.717 E.0163
G1 X163.353 Y159.145 E.01639
G1 X163.161 Y159.572 E.01781
G1 X162.792 Y160 E.02144
G1 X161.978 Y160.855 E.04486
G1 X161.749 Y161.283 E.01841
G1 X161.626 Y161.71 E.0169
G1 X161.59 Y162.138 E.0163
G1 X161.647 Y162.565 E.01639
G1 X161.84 Y162.993 E.01781
G1 X161.902 Y163.066 E.00364
G1 X165.666 Y163.066 E.14299
G1 X165.666 Y162.846 E.00834
G1 X165.398 Y162.565 E.01473
G1 X165.17 Y162.138 E.01841
G1 X165.047 Y161.71 E.0169
G1 X165.01 Y161.283 E.0163
G1 X165.068 Y160.855 E.01639
G1 X165.26 Y160.428 E.01781
G1 X165.666 Y159.961 E.02348
G1 X165.666 Y158.367 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 13.64
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F11292.473
G1 X165.666 Y159.961 E-.60571
G1 X165.399 Y160.268 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 57/82
; update layer progress
M73 L57
M991 S0 P56 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z13.8 I-.687 J-1.005 P1  F60000
G1 X160.806 Y163.407 Z13.8
G1 Z13.64
G1 E.8 F1800
; FEATURE: Inner wall
G1 F7925
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
M73 P87 R1
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7311
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y165.264 Z14.04 F60000
G1 Z13.64
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7925
M204 S8000
G1 X160.466 Y166.066 E.03044
G1 X159.673 Y166.066 E.03012
G1 X159.726 Y165.986 E.00363
G1 X159.88 Y165.558 E.01727
G1 X159.935 Y165.131 E.01638
G1 X159.904 Y164.703 E.01629
G1 X159.774 Y164.276 E.01697
G1 X159.514 Y163.848 E.01902
G1 X159.334 Y163.652 E.01009
G1 X159.334 Y159.686 E.15071
G1 X159.441 Y159.572 E.00592
G1 X159.726 Y159.145 E.01951
G1 X159.88 Y158.717 E.01727
G1 X159.935 Y158.29 E.01638
G1 X159.904 Y157.862 E.01629
G1 X159.774 Y157.435 E.01697
G1 X159.514 Y157.007 E.01902
G1 X159.334 Y156.811 E.01009
G1 X159.334 Y153.934 E.1093
G1 X160.466 Y153.934 E.04297
G1 X160.466 Y156.934 E.11398
G1 X162.793 Y156.934 E.08844
G1 X162.862 Y157.007 E.0038
G1 X163.146 Y157.435 E.01951
G1 X163.301 Y157.862 E.01727
G1 X163.356 Y158.29 E.01638
G1 X163.324 Y158.717 E.01629
G1 X163.195 Y159.145 E.01697
G1 X162.935 Y159.572 E.01902
G1 X162.138 Y160.428 E.0444
G1 X161.854 Y160.855 E.01951
G1 X161.699 Y161.283 E.01727
G1 X161.644 Y161.71 E.01638
G1 X161.676 Y162.138 E.01629
G1 X161.805 Y162.565 E.01697
G1 X162.065 Y162.993 E.01902
G1 X162.132 Y163.066 E.00374
G1 X165.627 Y163.066 E.13279
G1 X165.559 Y162.993 E.00379
G1 X165.274 Y162.565 E.01951
G1 X165.12 Y162.138 E.01727
G1 X165.065 Y161.71 E.01638
G1 X165.096 Y161.283 E.01629
G1 X165.226 Y160.855 E.01697
G1 X165.486 Y160.428 E.01902
G1 X165.666 Y160.232 E.01009
G1 X165.666 Y158.638 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 13.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X165.666 Y160.232 E-.60571
G1 X165.486 Y160.428 E-.10091
G1 X165.413 Y160.548 E-.05338
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 58/82
; update layer progress
M73 L58
M991 S0 P57 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z14.04 I-.642 J-1.034 P1  F60000
G1 X160.806 Y163.407 Z14.04
G1 Z13.88
G1 E.8 F1800
; FEATURE: Inner wall
G1 F7895
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7294
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y165.104 Z14.28 F60000
G1 Z13.88
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7895
M204 S8000
G1 X160.466 Y166.066 E.03653
G1 X159.833 Y166.066 E.02403
G1 X159.873 Y165.986 E.00339
G1 X159.956 Y165.558 E.01655
G1 X159.944 Y165.131 E.01625
G1 X159.845 Y164.703 E.01667
G1 X159.643 Y164.276 E.01796
G1 X159.334 Y163.879 E.0191
G1 X159.334 Y159.939 E.14969
G1 X159.657 Y159.572 E.01854
G1 X159.873 Y159.145 E.01821
G1 X159.956 Y158.717 E.01655
G1 X159.944 Y158.29 E.01625
G1 X159.845 Y157.862 E.01667
G1 X159.643 Y157.435 E.01796
G1 X159.334 Y157.038 E.0191
G1 X159.334 Y153.934 E.11791
G1 X160.466 Y153.934 E.04297
G1 X160.466 Y156.934 E.11398
G1 X163.013 Y156.934 E.09679
G1 X163.077 Y157.007 E.00367
G1 X163.294 Y157.435 E.01821
G1 X163.377 Y157.862 E.01655
G1 X163.364 Y158.29 E.01625
G1 X163.265 Y158.717 E.01667
G1 X163.064 Y159.145 E.01796
G1 X162.731 Y159.572 E.02058
G1 X162.299 Y160 E.0231
G1 X161.923 Y160.428 E.02163
G1 X161.706 Y160.855 E.01821
G1 X161.623 Y161.283 E.01655
G1 X161.636 Y161.71 E.01625
G1 X161.735 Y162.138 E.01667
G1 X161.936 Y162.565 E.01796
G1 X162.342 Y163.066 E.02447
G1 X165.407 Y163.066 E.11644
G1 X165.343 Y162.993 E.00367
G1 X165.127 Y162.565 E.01821
G1 X165.044 Y162.138 E.01655
G1 X165.056 Y161.71 E.01625
G1 X165.155 Y161.283 E.01667
G1 X165.357 Y160.855 E.01796
G1 X165.666 Y160.458 E.0191
G1 X165.666 Y158.864 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 14.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X165.666 Y160.458 E-.60571
G1 X165.416 Y160.779 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 59/82
; update layer progress
M73 L59
M991 S0 P58 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z14.28 I-.603 J-1.057 P1  F60000
G1 X160.806 Y163.407 Z14.28
G1 Z14.12
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7274
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y164.908 Z14.52 F60000
G1 Z14.12
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y166.066 E.04396
G1 X160.029 Y166.066 E.0166
G1 X160.055 Y165.986 E.00319
G1 X159.98 Y165.131 E.03261
G1 X159.811 Y164.703 E.01746
G1 X159.531 Y164.276 E.01943
G1 X159.334 Y164.095 E.01013
G1 X159.334 Y160.206 E.14777
G1 X159.558 Y160 E.01154
G1 X159.913 Y159.572 E.02111
G1 X160.055 Y159.145 E.01712
G1 X159.98 Y158.29 E.03261
G1 X159.811 Y157.862 E.01746
G1 X159.531 Y157.435 E.01943
G1 X159.334 Y157.254 E.01013
G1 X159.334 Y153.934 E.12612
G1 X160.466 Y153.934 E.04297
G1 X160.466 Y156.934 E.11398
G1 X163.273 Y156.934 E.10667
G1 X163.333 Y157.007 E.00359
G1 X163.476 Y157.435 E.01712
G1 X163.4 Y158.29 E.03261
G1 X163.232 Y158.717 E.01746
G1 X162.951 Y159.145 E.01943
G1 X162.022 Y160 E.04799
G1 X161.667 Y160.428 E.02111
G1 X161.524 Y160.855 E.01712
G1 X161.6 Y161.71 E.03261
G1 X161.768 Y162.138 E.01746
G1 X162.049 Y162.565 E.01943
G1 X162.593 Y163.066 E.02807
G1 X165.128 Y163.066 E.09633
G1 X165.087 Y162.993 E.00317
G1 X164.945 Y162.565 E.01712
G1 X165.02 Y161.71 E.03261
G1 X165.128 Y161.436 E.01119
G1 X165.128 Y159.842 E.06056
; WIPE_START
G1 X165.128 Y161.436 E-.60572
G1 X165.02 Y161.71 E-.11188
G1 X165.01 Y161.821 E-.04241
; WIPE_END
M73 P88 R1
G1 E-.04 F1800
M204 S10000
G1 X165.567 Y162.967 Z14.52 F60000
G1 Z14.12
G1 E.8 F1800
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.531444
G1 F1500;_EXTRUDE_SET_SPEED
M204 S8000
G1 X165.567 Y157.093 E.26881
; Slow Down End
; CHANGE_LAYER
; Z_HEIGHT: 14.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F1500
G1 X165.567 Y159.093 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 60/82
; update layer progress
M73 L60
M991 S0 P59 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z14.52 I-.817 J-.902 P1  F60000
G1 X160.806 Y163.407 Z14.52
G1 Z14.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10075
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7254
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y164.655 Z14.76 F60000
G1 Z14.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10075
M204 S8000
G1 X160.466 Y166.066 E.05359
G1 X160.282 Y166.066 E.00697
G1 X160.287 Y165.986 E.00303
G1 X160.047 Y165.131 E.03375
G1 X159.806 Y164.703 E.01865
G1 X159.432 Y164.276 E.02159
G1 X159.334 Y164.208 E.0045
G1 X159.334 Y160.431 E.14349
G1 X159.951 Y160 E.02859
G1 X160.259 Y159.572 E.02002
G1 X160.287 Y159.145 E.01628
G1 X160.047 Y158.29 E.03375
G1 X159.806 Y157.862 E.01865
G1 X159.432 Y157.435 E.02159
G1 X159.334 Y157.367 E.0045
G1 X159.334 Y153.934 E.1304
G1 X160.466 Y153.934 E.04297
G1 X160.466 Y156.934 E.11398
G1 X163.628 Y156.934 E.12014
G1 X163.68 Y157.007 E.0034
G1 X163.708 Y157.435 E.01628
G1 X163.467 Y158.29 E.03375
G1 X163.226 Y158.717 E.01865
G1 X162.852 Y159.145 E.02159
G1 X161.628 Y160 E.05672
G1 X161.32 Y160.428 E.02002
G1 X161.292 Y160.855 E.01628
G1 X161.533 Y161.71 E.03375
G1 X161.774 Y162.138 E.01865
G1 X162.148 Y162.565 E.02159
G1 X162.864 Y163.066 E.03318
G1 X164.793 Y163.066 E.07329
G1 X164.741 Y162.993 E.0034
G1 X164.713 Y162.565 E.01628
G1 X164.888 Y161.942 E.02461
G1 X164.888 Y160.348 E.06056
; WIPE_START
G1 F11292.473
G1 X164.888 Y161.942 E-.60572
G1 X164.778 Y162.333 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.267 Y163.027 Z14.76 F60000
G1 Z14.36
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.411474
G1 F10075
M204 S8000
G1 X165.627 Y163.027 E.01235
M73 P88 R0
G1 X165.627 Y156.973 E.20779
G1 X165.267 Y156.973 E.01235
G1 X165.267 Y162.967 E.20573
; CHANGE_LAYER
; Z_HEIGHT: 14.6
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F12000
G1 X165.267 Y160.967 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 61/82
; update layer progress
M73 L61
M991 S0 P60 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z14.76 I-.584 J-1.068 P1  F60000
G1 X160.806 Y163.407 Z14.76
G1 Z14.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8644
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7232
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.18058
M204 S10000
G1 X160.466 Y164.089 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8644
M204 S8000
G1 X160.466 Y165.683 E.06056
G1 X159.935 Y164.823 E.0384
G1 X159.507 Y164.396 E.02295
G1 X159.334 Y164.284 E.00781
G1 X159.334 Y162.69 E.06056
; WIPE_START
G1 F11292.473
G1 X159.334 Y164.284 E-.60572
G1 X159.507 Y164.396 E-.07816
G1 X159.649 Y164.537 E-.07613
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.567 Y162.967 Z15 F60000
G1 Z14.6
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.531484
G1 F8644
M204 S8000
G1 X165.567 Y157.033 E.27158
G1 X165.087 Y157.033 E.02196
G1 X165.087 Y162.967 E.27158
G1 X165.507 Y162.967 E.01922
; WIPE_START
G1 F9375.391
G1 X165.087 Y162.967 E-.15959
G1 X165.087 Y161.387 E-.60041
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.648 Y160.479 Z15 F60000
G1 Z14.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8644
M204 S8000
G1 X164.648 Y162.073 E.06056
G1 X164.21 Y162.907 E.03579
G1 X163.893 Y163.066 E.01347
G1 X163.355 Y163.053 E.02045
G1 X162.5 Y162.722 E.03483
G1 X162.072 Y162.445 E.01935
G1 X161.645 Y162.019 E.02295
G1 X161.217 Y161.331 E.03076
G1 X160.79 Y160.513 E.03505
G1 X160.362 Y160.3 E.01816
G1 X159.935 Y160.368 E.01645
G1 X159.334 Y160.6 E.02445
G1 X159.334 Y157.443 E.11994
G1 X159.507 Y157.555 E.00781
G1 X159.935 Y157.981 E.02295
G1 X160.362 Y158.669 E.03076
G1 X160.79 Y159.487 E.03505
G1 X161.217 Y159.7 E.01816
G1 X161.645 Y159.632 E.01645
G1 X162.5 Y159.302 E.03483
G1 X162.928 Y159.025 E.01935
G1 X163.355 Y158.598 E.02295
G1 X163.783 Y157.911 E.03076
G1 X164.21 Y157.093 E.03505
G1 X164.527 Y156.934 E.01347
G1 X162.933 Y156.934 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 14.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X164.527 Y156.934 E-.60572
G1 X164.21 Y157.093 E-.13474
G1 X164.186 Y157.139 E-.01955
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 62/82
; update layer progress
M73 L62
M991 S0 P61 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15 I-1.071 J-.578 P1  F60000
G1 X160.806 Y163.407 Z15
G1 Z14.84
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8429
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X165.787 Y156.593 E.1892
G1 X165.787 Y163.407 E.25885
G1 X160.866 Y163.407 E.18692
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P89 R0
G1 F7209
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X166.17 Y156.21 E.17496
G1 X166.17 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.17285
M204 S10000
G1 X160.466 Y163.783 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8429
M204 S8000
G1 X160.466 Y165.377 E.06056
G1 X159.935 Y164.728 E.03183
G1 X159.507 Y164.405 E.02036
G1 X159.334 Y164.323 E.00726
G1 X159.334 Y162.729 E.06056
; WIPE_START
G1 F11292.473
G1 X159.334 Y164.323 E-.60572
G1 X159.507 Y164.405 E-.0726
G1 X159.679 Y164.535 E-.08169
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.408 Y160.516 Z15.24 F60000
G1 Z14.84
G1 E.8 F1800
G1 F8429
M204 S8000
G1 X164.408 Y162.11 E.06056
G1 X164.21 Y162.352 E.01186
G1 X163.783 Y162.693 E.02078
G1 X163.355 Y162.789 E.01665
G1 X162.5 Y162.638 E.03299
G1 X162.072 Y162.436 E.01798
G1 X161.645 Y162.113 E.02036
G1 X160.79 Y161.069 E.05128
G1 X160.362 Y160.728 E.02078
G1 X159.935 Y160.632 E.01665
G1 X159.334 Y160.737 E.02315
G1 X159.334 Y157.482 E.12366
G1 X159.507 Y157.564 E.00726
G1 X159.935 Y157.887 E.02036
G1 X160.79 Y158.931 E.05128
G1 X161.217 Y159.272 E.02077
G1 X161.645 Y159.368 E.01665
G1 X162.5 Y159.218 E.03299
G1 X162.928 Y159.015 E.01798
G1 X163.355 Y158.692 E.02036
G1 X164.21 Y157.648 E.05128
G1 X164.408 Y157.49 E.00961
G1 X164.408 Y156.934 E.02112
G1 X163.37 Y156.934 E.03944
; WIPE_START
G1 F11292.473
G1 X164.408 Y156.934 E-.39445
G1 X164.408 Y157.49 E-.21126
G1 X164.21 Y157.648 E-.09613
G1 X164.113 Y157.766 E-.05816
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.342 Y157.283 Z15.24 F60000
G1 Z14.84
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541484
G1 F8429
M204 S8000
G1 X165.342 Y157.038 E.01144
G1 X164.852 Y157.038 E.02289
G1 X164.852 Y162.962 E.27677
G1 X165.342 Y162.962 E.02289
G1 X165.342 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 15.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9184.049
G1 X165.342 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 63/82
; update layer progress
M73 L63
M991 S0 P62 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15.24 I-.812 J-.906 P1  F60000
G1 X160.806 Y163.407 Z15.24
G1 Z15.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F9138
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X165.547 Y156.593 E.18009
G1 X165.547 Y163.407 E.25885
G1 X160.866 Y163.407 E.17781
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7185
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X165.93 Y156.21 E.16653
G1 X165.93 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.16442
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y165.925 Z15.48 F60000
G1 Z15.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F9138
M204 S8000
G1 X159.334 Y164.331 E.06056
G1 X159.507 Y164.385 E.00686
G1 X159.935 Y164.623 E.01859
G1 X160.466 Y165.141 E.02817
G1 X160.466 Y163.066 E.07884
G1 X164.168 Y163.066 E.14067
G1 X164.168 Y162.072 E.03773
G1 X163.783 Y162.402 E.01927
G1 X163.355 Y162.586 E.01768
G1 X162.928 Y162.634 E.01635
G1 X162.5 Y162.588 E.01634
G1 X162.072 Y162.456 E.017
G1 X161.645 Y162.218 E.01859
G1 X160.79 Y161.384 E.04538
G1 X160.362 Y161.018 E.02138
G1 X159.935 Y160.835 E.01768
G1 X159.507 Y160.787 E.01635
G1 X159.334 Y160.805 E.0066
G1 X159.334 Y157.49 E.12594
G1 X159.507 Y157.544 E.00686
G1 X159.935 Y157.782 E.01859
G1 X160.79 Y158.616 E.04538
G1 X161.217 Y158.982 E.02138
G1 X161.645 Y159.165 E.01768
G1 X162.072 Y159.213 E.01635
G1 X162.5 Y159.168 E.01634
G1 X162.928 Y159.036 E.017
G1 X163.355 Y158.798 E.01859
G1 X164.168 Y158.005 E.04314
G1 X164.168 Y156.934 E.04067
G1 X160.466 Y156.934 E.14067
G1 X160.466 Y154.266 E.10139
G1 X160.362 Y154.177 E.00517
G1 X159.935 Y153.994 E.01768
G1 X159.507 Y153.946 E.01635
G1 X159.334 Y153.964 E.0066
G1 X159.334 Y155.558 E.06056
; WIPE_START
G1 F11292.473
G1 X159.334 Y153.964 E-.60572
G1 X159.507 Y153.946 E-.06597
G1 X159.738 Y153.972 E-.08831
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.102 Y157.283 Z15.48 F60000
G1 Z15.08
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541474
G1 F9138
M204 S8000
G1 X165.102 Y157.038 E.01144
G1 X164.612 Y157.038 E.02289
G1 X164.612 Y162.962 E.27676
G1 X165.102 Y162.962 E.02289
G1 X165.102 Y157.343 E.26251
; CHANGE_LAYER
; Z_HEIGHT: 15.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9184.235
G1 X165.102 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 64/82
; update layer progress
M73 L64
M991 S0 P63 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15.48 I-.836 J-.884 P1  F60000
G1 X160.806 Y163.407 Z15.48
G1 Z15.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8973
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X165.307 Y156.593 E.17097
G1 X165.307 Y163.407 E.25885
G1 X160.866 Y163.407 E.16869
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7159
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X165.69 Y156.21 E.1581
G1 X165.69 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.15599
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y165.906 Z15.72 F60000
G1 Z15.32
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8973
M204 S8000
G1 X159.334 Y164.312 E.06056
G1 X159.507 Y164.338 E.00663
G1 X159.935 Y164.501 E.01739
G1 X160.362 Y164.795 E.0197
G1 X160.466 Y164.893 E.00543
G1 X160.466 Y163.066 E.06944
G1 X163.928 Y163.066 E.13155
G1 X163.928 Y162.039 E.03899
G1 X163.783 Y162.172 E.00746
G1 X163.355 Y162.423 E.01885
G1 X162.928 Y162.544 E.01688
G1 X162.5 Y162.567 E.01627
M73 P90 R0
G1 X162.072 Y162.503 E.01642
G1 X161.645 Y162.34 E.01739
G1 X161.217 Y162.046 E.0197
G1 X160.362 Y161.249 E.04442
G1 X159.935 Y160.997 E.01885
G1 X159.507 Y160.877 E.01688
G1 X159.334 Y160.867 E.00657
G1 X159.334 Y157.471 E.12903
G1 X159.507 Y157.497 E.00663
G1 X159.935 Y157.66 E.01739
G1 X160.362 Y157.954 E.0197
G1 X161.217 Y158.751 E.04442
G1 X161.645 Y159.003 E.01885
G1 X162.072 Y159.123 E.01688
G1 X162.5 Y159.146 E.01627
G1 X162.928 Y159.083 E.01642
G1 X163.355 Y158.919 E.01739
G1 X163.783 Y158.626 E.0197
G1 X163.928 Y158.487 E.00764
G1 X163.928 Y156.934 E.05899
G1 X160.466 Y156.934 E.13155
G1 X160.466 Y154.502 E.09242
G1 X160.362 Y154.408 E.00531
G1 X159.935 Y154.156 E.01885
G1 X159.507 Y154.036 E.01688
G1 X159.334 Y154.026 E.00657
G1 X159.334 Y155.62 E.06056
; WIPE_START
G1 F11292.473
G1 X159.334 Y154.026 E-.60572
G1 X159.507 Y154.036 E-.0657
G1 X159.731 Y154.099 E-.08859
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.862 Y157.283 Z15.72 F60000
G1 Z15.32
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541484
G1 F8973
M204 S8000
G1 X164.862 Y157.038 E.01144
G1 X164.372 Y157.038 E.02289
G1 X164.372 Y162.962 E.27677
G1 X164.862 Y162.962 E.02289
G1 X164.862 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 15.56
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F9184.049
G1 X164.862 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 65/82
; update layer progress
M73 L65
M991 S0 P64 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15.72 I-.861 J-.86 P1  F60000
G1 X160.806 Y163.407 Z15.72
G1 Z15.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8356
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X165.067 Y156.593 E.16185
G1 X165.067 Y163.407 E.25885
G1 X160.866 Y163.407 E.15957
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7132
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X165.45 Y156.21 E.14966
G1 X165.45 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.14756
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y163.08 Z15.96 F60000
G1 Z15.56
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8356
M204 S8000
G1 X160.466 Y164.674 E.06056
G1 X160.362 Y164.582 E.00524
G1 X159.935 Y164.357 E.01836
G1 X159.507 Y164.265 E.01662
G1 X159.334 Y164.267 E.00656
G1 X159.334 Y160.903 E.12781
G1 X159.507 Y160.939 E.0067
G1 X159.935 Y161.131 E.01781
G1 X160.362 Y161.454 E.02035
G1 X160.79 Y161.88 E.02293
G1 X161.217 Y162.259 E.0217
G1 X161.645 Y162.484 E.01836
G1 X162.072 Y162.576 E.01662
G1 X162.5 Y162.572 E.01625
G1 X162.928 Y162.482 E.0166
G1 X163.355 Y162.289 E.01781
G1 X163.688 Y162.038 E.01585
G1 X163.688 Y158.888 E.11968
G1 X163.355 Y159.063 E.0143
G1 X162.928 Y159.156 E.01662
G1 X162.5 Y159.151 E.01624
G1 X162.072 Y159.061 E.0166
G1 X161.645 Y158.869 E.01781
G1 X161.217 Y158.546 E.02035
G1 X160.79 Y158.12 E.02293
G1 X160.362 Y157.741 E.0217
G1 X159.935 Y157.516 E.01836
G1 X159.507 Y157.424 E.01662
G1 X159.334 Y157.426 E.00656
G1 X159.334 Y154.061 E.12781
G1 X159.507 Y154.098 E.0067
G1 X159.935 Y154.29 E.01781
G1 X160.362 Y154.613 E.02035
G1 X160.466 Y154.716 E.00554
G1 X160.466 Y156.31 E.06056
; WIPE_START
G1 F11292.473
G1 X160.466 Y154.716 E-.60572
G1 X160.362 Y154.613 E-.05542
G1 X160.155 Y154.456 E-.09886
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.622 Y157.283 Z15.96 F60000
G1 Z15.56
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541484
G1 F8356
M204 S8000
G1 X164.622 Y157.038 E.01144
G1 X164.132 Y157.038 E.02289
G1 X164.132 Y162.962 E.27677
G1 X164.622 Y162.962 E.02289
G1 X164.622 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 15.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9184.049
G1 X164.622 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 66/82
; update layer progress
M73 L66
M991 S0 P65 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15.96 I-.887 J-.833 P1  F60000
G1 X160.806 Y163.407 Z15.96
G1 Z15.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7821
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X164.827 Y156.593 E.15273
G1 X164.827 Y163.407 E.25885
G1 X160.866 Y163.407 E.15045
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7104
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X165.21 Y156.21 E.14123
G1 X165.21 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.13912
M204 S10000
G1 X160.705 Y163.066 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7821
M204 S8000
G1 X160.466 Y163.066 E.00911
G1 X160.466 Y164.42 E.05145
G1 X160.362 Y164.333 E.00512
G1 X159.935 Y164.181 E.01725
G1 X159.334 Y164.22 E.02285
G1 X159.334 Y160.911 E.12571
G1 X159.507 Y160.976 E.007
G1 X159.935 Y161.246 E.01922
G1 X160.79 Y162.15 E.04728
G1 X161.217 Y162.508 E.02118
G1 X161.645 Y162.661 E.01725
G1 X162.5 Y162.604 E.03256
G1 X162.928 Y162.445 E.01734
G1 X163.355 Y162.175 E.01922
G1 X163.448 Y162.077 E.00514
G1 X163.448 Y159.207 E.10903
G1 X163.355 Y159.24 E.00375
G1 X162.5 Y159.184 E.03256
G1 X162.072 Y159.024 E.01734
G1 X161.645 Y158.754 E.01922
G1 X160.79 Y157.85 E.04728
G1 X160.362 Y157.492 E.02118
G1 X159.935 Y157.339 E.01725
G1 X159.334 Y157.379 E.02285
G1 X159.334 Y154.07 E.12571
G1 X159.507 Y154.135 E.007
G1 X159.935 Y154.405 E.01922
G1 X160.466 Y154.966 E.02935
G1 X160.466 Y156.56 E.06056
; WIPE_START
G1 F11292.473
G1 X160.466 Y154.966 E-.60572
G1 X160.187 Y154.671 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.382 Y157.283 Z16.2 F60000
G1 Z15.8
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541484
G1 F7821
M204 S8000
G1 X164.382 Y157.038 E.01144
G1 X163.892 Y157.038 E.02289
G1 X163.892 Y162.962 E.27677
G1 X164.382 Y162.962 E.02289
G1 X164.382 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 16.04
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F9184.049
G1 X164.382 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 67/82
; update layer progress
M73 L67
M991 S0 P66 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z16.2 I-.914 J-.804 P1  F60000
G1 X160.806 Y163.407 Z16.2
G1 Z16.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8143
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X164.587 Y156.593 E.14361
G1 X164.587 Y163.407 E.25885
G1 X160.866 Y163.407 E.14133
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7074
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
M73 P91 R0
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X164.97 Y156.21 E.1328
G1 X164.97 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.13069
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y165.674 Z16.44 F60000
G1 Z16.04
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8143
M204 S8000
G1 X160.466 Y164.08 E.06056
G1 X160.362 Y164.003 E.0049
G1 X159.935 Y163.956 E.01634
G1 X159.334 Y164.109 E.02353
G1 X159.334 Y160.891 E.12224
G1 X159.507 Y160.985 E.00746
G1 X159.935 Y161.346 E.02127
G1 X160.79 Y162.519 E.05515
G1 X161.217 Y162.839 E.02027
G1 X161.645 Y162.885 E.01634
G1 X162.5 Y162.667 E.03353
G1 X162.928 Y162.436 E.01848
G1 X163.208 Y162.199 E.01395
G1 X163.208 Y159.427 E.10529
G1 X162.5 Y159.247 E.02776
G1 X162.072 Y159.015 E.01848
G1 X161.645 Y158.654 E.02127
G1 X160.79 Y157.481 E.05515
G1 X160.362 Y157.162 E.02027
G1 X159.935 Y157.115 E.01634
G1 X159.334 Y157.268 E.02353
G1 X159.334 Y154.05 E.12224
G1 X159.507 Y154.144 E.00746
G1 X159.935 Y154.505 E.02127
G1 X160.466 Y155.234 E.03424
G1 X160.466 Y153.934 E.04936
G1 X160.171 Y153.934 E.0112
; WIPE_START
G1 F11292.473
G1 X160.466 Y153.934 E-.11205
G1 X160.466 Y155.234 E-.49367
G1 X160.226 Y154.905 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.142 Y157.283 Z16.44 F60000
G1 Z16.04
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541484
G1 F8143
M204 S8000
G1 X164.142 Y157.038 E.01144
G1 X163.652 Y157.038 E.02289
G1 X163.652 Y162.962 E.27677
G1 X164.142 Y162.962 E.02289
G1 X164.142 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 16.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9184.049
G1 X164.142 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 68/82
; update layer progress
M73 L68
M991 S0 P67 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z16.44 I-.941 J-.772 P1  F60000
G1 X160.806 Y163.407 Z16.44
G1 Z16.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8710
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X164.347 Y156.593 E.1345
G1 X164.347 Y163.407 E.25885
G1 X160.866 Y163.407 E.13222
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7043
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X164.73 Y156.21 E.12437
G1 X164.73 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.12226
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.968 Y162.599 Z16.68 F60000
G1 Z16.28
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8710
M204 S8000
G1 X162.968 Y163.066 E.01772
G1 X161.916 Y163.066 E.03999
G1 X162.07 Y162.993 E.00647
G1 X162.797 Y162.565 E.03206
G1 X162.968 Y162.4 E.00904
G1 X162.968 Y159.618 E.10567
G1 X162.93 Y159.572 E.00226
G1 X162.203 Y159.145 E.03206
G1 X161.761 Y158.717 E.02336
G1 X161.475 Y158.29 E.01955
G1 X161.118 Y157.435 E.0352
G1 X161.016 Y157.007 E.01671
G1 X161.041 Y156.934 E.00292
G1 X162.635 Y156.934 E.06056
; WIPE_START
G1 F11292.473
G1 X161.041 Y156.934 E-.60571
G1 X161.016 Y157.007 E-.02919
G1 X161.093 Y157.327 E-.1251
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.902 Y157.283 Z16.68 F60000
G1 Z16.28
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541484
G1 F8710
M204 S8000
G1 X163.902 Y157.038 E.01144
G1 X163.412 Y157.038 E.02289
G1 X163.412 Y162.962 E.27677
G1 X163.902 Y162.962 E.02289
G1 X163.902 Y157.343 E.26252
; WIPE_START
G1 F9184.049
G1 X163.902 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y155.583 Z16.68 F60000
G1 Z16.28
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8710
M204 S8000
G1 X159.334 Y153.989 E.06056
G1 X159.818 Y154.442 E.02516
G1 X160.105 Y154.869 E.01955
G1 X160.466 Y155.742 E.0359
G1 X160.466 Y156.438 E.02644
G1 X160.417 Y156.58 E.00567
G1 X159.51 Y157.007 E.0381
G1 X159.334 Y157.11 E.00773
G1 X159.334 Y160.83 E.14134
G1 X159.818 Y161.283 E.02516
G1 X160.105 Y161.71 E.01955
G1 X160.461 Y162.565 E.0352
G1 X160.564 Y162.993 E.01671
G1 X160.539 Y163.066 E.00292
G1 X160.466 Y163.066 E.00279
G1 X160.466 Y163.279 E.00812
G1 X160.417 Y163.421 E.00567
G1 X159.51 Y163.848 E.0381
G1 X159.334 Y163.951 E.00773
G1 X159.334 Y165.545 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 16.52
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y163.951 E-.60571
G1 X159.51 Y163.848 E-.07734
G1 X159.693 Y163.762 E-.07694
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 69/82
; update layer progress
M73 L69
M991 S0 P68 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z16.68 I.37 J1.159 P1  F60000
G1 X160.806 Y163.407 Z16.68
G1 Z16.52
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8311
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X164.107 Y156.593 E.12538
G1 X164.107 Y163.407 E.25885
G1 X160.866 Y163.407 E.1231
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7011
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X164.49 Y156.21 E.11594
G1 X164.49 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.11383
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.558 Y158.277 Z16.92 F60000
G1 X162.728 Y157.331 Z16.92
G1 Z16.52
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8311
M204 S8000
G1 X162.728 Y156.934 E.01507
G1 X161.531 Y156.934 E.04549
G1 X161.474 Y157.007 E.00351
G1 X161.392 Y157.435 E.01654
G1 X161.563 Y158.29 E.03313
G1 X161.775 Y158.717 E.01813
G1 X162.11 Y159.145 E.02063
G1 X162.728 Y159.634 E.02995
G1 X162.728 Y162.694 E.11624
G1 X162.258 Y163.066 E.02278
G1 X160.466 Y163.066 E.0681
G1 X160.466 Y166.066 E.11398
G1 X159.334 Y166.066 E.04297
G1 X159.334 Y163.765 E.08739
G1 X159.77 Y163.421 E.02112
G1 X160.106 Y162.993 E.02065
G1 X160.188 Y162.565 E.01654
G1 X160.016 Y161.71 E.03313
M73 P92 R0
G1 X159.804 Y161.283 E.01813
G1 X159.47 Y160.855 E.02063
G1 X159.334 Y160.748 E.00655
G1 X159.334 Y156.924 E.14528
G1 X159.77 Y156.58 E.02112
G1 X160.106 Y156.152 E.02065
G1 X160.188 Y155.724 E.01654
G1 X160.016 Y154.869 E.03313
G1 X159.804 Y154.442 E.01813
G1 X159.47 Y154.014 E.02063
G1 X159.369 Y153.934 E.00488
G1 X159.334 Y153.934 E.00131
G1 X159.334 Y155.494 E.05925
; WIPE_START
G1 F11292.473
G1 X159.334 Y153.934 E-.59264
G1 X159.369 Y153.934 E-.01308
G1 X159.47 Y154.014 E-.04881
G1 X159.641 Y154.233 E-.10548
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.662 Y157.283 Z16.92 F60000
G1 Z16.52
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541484
G1 F8311
M204 S8000
G1 X163.662 Y157.038 E.01144
G1 X163.172 Y157.038 E.02289
G1 X163.172 Y162.962 E.27677
G1 X163.662 Y162.962 E.02289
G1 X163.662 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 16.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9184.049
G1 X163.662 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 70/82
; update layer progress
M73 L70
M991 S0 P69 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z16.92 I-.996 J-.7 P1  F60000
G1 X160.806 Y163.407 Z16.92
G1 Z16.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7716
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X163.867 Y156.593 E.11626
G1 X163.867 Y163.407 E.25885
G1 X160.866 Y163.407 E.11398
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6979
M204 S5000
G1 X161.19 Y166.79 E.1054
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X164.25 Y156.21 E.10751
G1 X164.25 Y163.79 E.2663
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

G1 X161.25 Y163.79 E.1054
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y165.121 Z17.16 F60000
G1 Z16.76
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7716
M204 S8000
G1 X159.334 Y163.527 E.06056
G1 X159.804 Y162.993 E.027
G1 X159.978 Y162.565 E.01754
G1 X159.962 Y161.71 E.03249
G1 X159.822 Y161.283 E.0171
G1 X159.573 Y160.855 E.01878
G1 X159.334 Y160.616 E.01284
G1 X159.334 Y156.686 E.14933
G1 X159.804 Y156.152 E.027
G1 X159.978 Y155.724 E.01754
G1 X159.962 Y154.869 E.03249
G1 X159.822 Y154.442 E.0171
G1 X159.573 Y154.014 E.01878
G1 X159.494 Y153.934 E.00428
G1 X160.466 Y153.934 E.03692
G1 X160.466 Y156.934 E.11398
G1 X161.837 Y156.934 E.05212
G1 X161.776 Y157.007 E.00362
G1 X161.602 Y157.435 E.01754
G1 X161.617 Y158.29 E.03249
G1 X161.758 Y158.717 E.0171
G1 X162.006 Y159.145 E.01878
G1 X162.488 Y159.627 E.0259
G1 X162.488 Y161.221 E.06056
; WIPE_START
G1 F11292.473
G1 X162.488 Y159.627 E-.60571
G1 X162.201 Y159.34 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.422 Y157.283 Z17.16 F60000
G1 Z16.76
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541484
G1 F7716
M204 S8000
G1 X163.422 Y157.038 E.01144
G1 X162.932 Y157.038 E.02289
G1 X162.932 Y162.962 E.27677
G1 X163.422 Y162.962 E.02289
G1 X163.422 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 17
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9184.049
G1 X163.422 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 71/82
; update layer progress
M73 L71
M991 S0 P70 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z17.16 I-1.023 J-.659 P1  F60000
G1 X160.806 Y163.407 Z17.16
G1 Z17
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7617
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X163.627 Y156.593 E.10714
G1 X163.627 Y163.407 E.25885
G1 X160.866 Y163.407 E.10486
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6945
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X164.01 Y156.21 E.09907
G1 X164.01 Y163.79 E.2663
G1 X161.25 Y163.79 E.09697
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.846 Z17.4 F60000
G1 Z17
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7617
M204 S8000
G1 X159.334 Y163.252 E.06056
G1 X159.568 Y162.993 E.01325
G1 X159.811 Y162.565 E.01869
G1 X159.923 Y162.138 E.01679
G1 X159.937 Y161.71 E.01625
G1 X159.865 Y161.283 E.01647
G1 X159.693 Y160.855 E.01752
G1 X159.334 Y160.37 E.02291
G1 X159.334 Y156.411 E.15041
G1 X159.568 Y156.152 E.01325
G1 X159.811 Y155.724 E.01869
G1 X159.923 Y155.297 E.01679
G1 X159.937 Y154.869 E.01625
G1 X159.865 Y154.442 E.01647
G1 X159.693 Y154.014 E.01752
G1 X159.636 Y153.934 E.00371
G1 X160.466 Y153.934 E.03151
G1 X160.466 Y156.934 E.11398
G1 X162.077 Y156.934 E.06123
G1 X162.012 Y157.007 E.00372
G1 X161.768 Y157.435 E.01869
G1 X161.657 Y157.862 E.01679
G1 X161.642 Y158.29 E.01625
G1 X161.714 Y158.717 E.01647
G1 X161.887 Y159.145 E.01752
G1 X162.248 Y159.633 E.02307
G1 X162.248 Y161.227 E.06056
; WIPE_START
G1 F11292.473
G1 X162.248 Y159.633 E-.60571
G1 X162.007 Y159.307 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.182 Y157.283 Z17.4 F60000
G1 Z17
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541484
G1 F7617
M204 S8000
G1 X163.182 Y157.038 E.01144
G1 X162.692 Y157.038 E.02289
G1 X162.692 Y162.962 E.27677
G1 X163.182 Y162.962 E.02289
G1 X163.182 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 17.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9184.049
G1 X163.182 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 72/82
; update layer progress
M73 L72
M991 S0 P71 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z17.4 I-1.051 J-.614 P1  F60000
G1 X160.806 Y163.407 Z17.4
G1 Z17.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7506
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X163.387 Y156.593 E.09802
G1 X163.387 Y163.407 E.25885
G1 X160.866 Y163.407 E.09574
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6910
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X163.77 Y156.21 E.09064
M73 P93 R0
G1 X163.77 Y163.79 E.2663
G1 X161.25 Y163.79 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.614 Z17.64 F60000
G1 Z17.24
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7506
M204 S8000
G1 X159.334 Y163.02 E.06056
G1 X159.674 Y162.565 E.02156
G1 X159.857 Y162.138 E.01767
G1 X159.939 Y161.71 E.01654
G1 X159.935 Y161.283 E.01625
G1 X159.833 Y160.855 E.01669
G1 X159.6 Y160.428 E.01851
G1 X159.334 Y160.13 E.01513
G1 X159.334 Y156.179 E.15012
G1 X159.674 Y155.724 E.02156
G1 X159.857 Y155.297 E.01767
G1 X159.939 Y154.869 E.01654
G1 X159.935 Y154.442 E.01625
G1 X159.833 Y154.014 E.01669
G1 X159.79 Y153.934 E.00345
G1 X160.466 Y153.934 E.02567
G1 X160.466 Y156.934 E.11398
G1 X162.008 Y156.934 E.0586
G1 X162.008 Y157.281 E.01318
G1 X161.905 Y157.435 E.00701
G1 X161.722 Y157.862 E.01767
G1 X161.641 Y158.29 E.01654
G1 X161.645 Y158.717 E.01624
G1 X161.746 Y159.145 E.01669
G1 X162.008 Y159.629 E.02092
G1 X162.008 Y161.223 E.06056
; WIPE_START
G1 F11292.473
G1 X162.008 Y159.629 E-.60572
G1 X161.815 Y159.272 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.942 Y157.283 Z17.64 F60000
G1 Z17.24
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541504
G1 F7506
M204 S8000
G1 X162.942 Y157.038 E.01145
G1 X162.452 Y157.038 E.02289
G1 X162.452 Y162.962 E.27678
G1 X162.942 Y162.962 E.02289
G1 X162.942 Y157.343 E.26253
; CHANGE_LAYER
; Z_HEIGHT: 17.48
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9183.673
G1 X162.942 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 73/82
; update layer progress
M73 L73
M991 S0 P72 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z17.64 I-1.077 J-.566 P1  F60000
G1 X160.806 Y163.407 Z17.64
G1 Z17.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7392
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X163.147 Y156.593 E.0889
G1 X163.147 Y163.407 E.25885
G1 X160.866 Y163.407 E.08662
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6875
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X163.53 Y156.21 E.08221
G1 X163.53 Y163.79 E.2663
G1 X161.25 Y163.79 E.0801
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.376 Z17.88 F60000
G1 Z17.48
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7392
M204 S8000
G1 X159.334 Y162.782 E.06056
G1 X159.558 Y162.565 E.01182
G1 X159.817 Y162.138 E.01901
G1 X159.968 Y161.71 E.01722
G1 X160.005 Y160.855 E.03252
G1 X159.842 Y160.428 E.01738
G1 X159.482 Y160 E.02125
G1 X159.334 Y159.857 E.00781
G1 X159.334 Y155.941 E.14877
G1 X159.558 Y155.724 E.01182
G1 X159.817 Y155.297 E.01901
G1 X159.968 Y154.869 E.01722
G1 X160.005 Y154.014 E.03252
G1 X159.975 Y153.934 E.00324
G1 X160.466 Y153.934 E.01864
G1 X160.466 Y156.934 E.11398
G1 X161.768 Y156.934 E.04949
G1 X161.768 Y157.853 E.03488
G1 X161.612 Y158.29 E.01764
G1 X161.574 Y159.145 E.03252
G1 X161.737 Y159.572 E.01738
G1 X161.768 Y159.609 E.00182
G1 X161.768 Y161.203 E.06056
; WIPE_START
G1 F11292.473
G1 X161.768 Y159.609 E-.60571
G1 X161.737 Y159.572 E-.01822
G1 X161.61 Y159.238 E-.13606
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.702 Y157.283 Z17.88 F60000
G1 Z17.48
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541504
G1 F7392
M204 S8000
G1 X162.702 Y157.038 E.01145
G1 X162.212 Y157.038 E.02289
G1 X162.212 Y162.962 E.27678
G1 X162.702 Y162.962 E.02289
G1 X162.702 Y157.343 E.26253
; CHANGE_LAYER
; Z_HEIGHT: 17.72
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9183.673
G1 X162.702 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 74/82
; update layer progress
M73 L74
M991 S0 P73 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z17.88 I-1.103 J-.514 P1  F60000
G1 X160.806 Y163.407 Z17.88
G1 Z17.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7308
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X162.907 Y156.593 E.07979
G1 X162.907 Y163.407 E.25885
G1 X160.866 Y163.407 E.07751
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6840
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X163.29 Y156.21 E.07378
G1 X163.29 Y163.79 E.2663
G1 X161.25 Y163.79 E.07167
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.251 Z18.12 F60000
G1 Z17.72
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7308
M204 S8000
G1 X159.334 Y162.657 E.06056
G1 X159.456 Y162.565 E.00577
G1 X159.804 Y162.138 E.02097
G1 X160.027 Y161.71 E.01831
G1 X160.223 Y160.855 E.03333
G1 X160.159 Y160.428 E.01642
G1 X159.831 Y160 E.02047
G1 X159.334 Y159.623 E.02368
G1 X159.334 Y155.816 E.14464
G1 X159.456 Y155.724 E.00577
G1 X159.804 Y155.297 E.02097
G1 X160.027 Y154.869 E.01831
G1 X160.223 Y154.014 E.03333
G1 X160.211 Y153.934 E.00306
G1 X160.466 Y153.934 E.00968
G1 X160.466 Y156.934 E.11398
G1 X161.528 Y156.934 E.04037
G1 X161.528 Y158.397 E.05558
G1 X161.357 Y159.145 E.02914
G1 X161.421 Y159.572 E.01642
G1 X161.528 Y159.713 E.00671
G1 X161.528 Y161.307 E.06056
; WIPE_START
G1 F11292.473
G1 X161.528 Y159.713 E-.60571
G1 X161.421 Y159.572 E-.06708
G1 X161.387 Y159.345 E-.08721
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.462 Y157.283 Z18.12 F60000
G1 Z17.72
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541504
G1 F7308
M204 S8000
G1 X162.462 Y157.038 E.01145
G1 X161.972 Y157.038 E.02289
G1 X161.972 Y162.962 E.27678
G1 X162.462 Y162.962 E.02289
G1 X162.462 Y157.343 E.26253
; CHANGE_LAYER
; Z_HEIGHT: 17.96
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9183.673
G1 X162.462 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 75/82
; update layer progress
M73 L75
M991 S0 P74 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z18.12 I-1.127 J-.459 P1  F60000
G1 X160.806 Y163.407 Z18.12
G1 Z17.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7159
M204 S8000
G1 X160.806 Y166.407 E.11398
M73 P94 R0
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X162.667 Y156.593 E.07067
G1 X162.667 Y163.407 E.25885
G1 X160.866 Y163.407 E.06839
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6805
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X163.05 Y156.21 E.06535
G1 X163.05 Y163.79 E.2663
G1 X161.25 Y163.79 E.06324
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.288 Y161.789 Z18.36 F60000
G1 Z17.96
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7159
M204 S8000
G1 X161.288 Y160.195 E.06056
G1 X160.79 Y160.099 E.01928
G1 X160.362 Y161.222 E.04566
G1 X159.935 Y161.996 E.03359
G1 X159.507 Y162.453 E.02378
G1 X159.334 Y162.573 E.00798
G1 X159.334 Y159.443 E.11891
G1 X159.935 Y159.712 E.02499
G1 X160.362 Y159.856 E.01714
G1 X160.79 Y159.901 E.01633
G1 X161.14 Y158.965 E.03795
G1 X161.288 Y158.658 E.01297
G1 X161.288 Y157.064 E.06056
M204 S10000
G1 X162.222 Y157.283 F60000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541494
G1 F7159
M204 S8000
G1 X162.222 Y157.038 E.01145
G1 X161.732 Y157.038 E.02289
G1 X161.732 Y162.962 E.27677
G1 X162.222 Y162.962 E.02289
G1 X162.222 Y157.343 E.26252
; WIPE_START
G1 F9183.861
G1 X162.222 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y157.326 Z18.36 F60000
G1 Z17.96
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7159
M204 S8000
G1 X159.334 Y155.732 E.06056
G1 X159.507 Y155.612 E.00798
G1 X159.935 Y155.155 E.02378
G1 X160.362 Y154.381 E.03359
G1 X160.466 Y154.11 E.01103
G1 X160.466 Y153.934 E.00667
G1 X159.334 Y153.934 E.04297
G1 X159.334 Y154.222 E.01092
; CHANGE_LAYER
; Z_HEIGHT: 18.2
; LAYER_HEIGHT: 0.240002
; WIPE_START
G1 F11292.473
G1 X159.334 Y153.934 E-.10922
G1 X160.466 Y153.934 E-.42981
G1 X160.466 Y154.11 E-.06669
G1 X160.362 Y154.381 E-.11035
G1 X160.306 Y154.483 E-.04394
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 76/82
; update layer progress
M73 L76
M991 S0 P75 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z18.36 I-1.215 J.068 P1  F60000
G1 X160.806 Y163.407 Z18.36
G1 Z18.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F6837
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X162.427 Y156.593 E.06155
G1 X162.427 Y163.407 E.25885
G1 X160.866 Y163.407 E.05927
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6776
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X162.81 Y156.21 E.05691
G1 X162.81 Y163.79 E.2663
G1 X161.25 Y163.79 E.05481
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.118 Z18.6 F60000
G1 Z18.2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F6837
M204 S8000
G1 X159.334 Y162.524 E.06056
G1 X159.507 Y162.435 E.00738
G1 X159.935 Y162.088 E.02092
G1 X160.79 Y160.967 E.05357
G1 X161.048 Y160.741 E.01304
G1 X161.048 Y158.678 E.07837
G1 X160.79 Y159.033 E.01668
G1 X160.362 Y159.362 E.02049
G1 X159.935 Y159.428 E.01644
G1 X159.334 Y159.293 E.02338
G1 X159.334 Y155.683 E.13714
G1 X159.507 Y155.594 E.00738
G1 X159.935 Y155.247 E.02092
G1 X160.466 Y154.551 E.03326
G1 X160.466 Y156.145 E.06056
; WIPE_START
G1 F11292.473
G1 X160.466 Y154.551 E-.60572
G1 X160.219 Y154.874 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.982 Y157.283 Z18.6 F60000
G1 Z18.2
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541494
G1 F6837
M204 S8000
G1 X161.982 Y157.038 E.01144
G1 X161.492 Y157.038 E.02289
G1 X161.492 Y162.962 E.27677
G1 X161.982 Y162.962 E.02289
G1 X161.982 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 18.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9183.861
G1 X161.982 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 77/82
; update layer progress
M73 L77
M991 S0 P76 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z18.6 I-1.169 J-.338 P1  F60000
G1 X160.806 Y163.407 Z18.6
G1 Z18.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6681
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X162.187 Y156.593 E.05243
G1 X162.187 Y163.407 E.25885
G1 X160.866 Y163.407 E.05015
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6681
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X162.57 Y156.21 E.04848
G1 X162.57 Y163.79 E.2663
G1 X161.25 Y163.79 E.04638
M204 S10000
G1 X160.466 Y164.207 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F6681
M204 S8000
G1 X160.466 Y165.801 E.06056
G1 X160.362 Y165.889 E.00514
G1 X159.935 Y166.053 E.0174
G1 X159.334 Y166.029 E.02282
G1 X159.334 Y162.509 E.13373
G1 X159.507 Y162.449 E.00695
G1 X159.935 Y162.19 E.01898
G1 X160.808 Y161.297 E.04747
G1 X160.808 Y158.666 E.09995
G1 X160.362 Y159.048 E.02229
G1 X159.935 Y159.212 E.0174
G1 X159.334 Y159.188 E.02282
G1 X159.334 Y155.668 E.13373
G1 X159.507 Y155.608 E.00695
G1 X159.935 Y155.349 E.01898
G1 X160.466 Y154.805 E.02889
G1 X160.466 Y156.399 E.06056
; WIPE_START
G1 F11292.473
G1 X160.466 Y154.805 E-.60572
G1 X160.182 Y155.096 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.742 Y157.283 Z18.84 F60000
G1 Z18.44
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.541494
G1 F6681
M204 S8000
G1 X161.742 Y157.038 E.01145
G1 X161.252 Y157.038 E.02289
G1 X161.252 Y162.962 E.27677
G1 X161.742 Y162.962 E.02289
G1 X161.742 Y157.343 E.26252
; CHANGE_LAYER
; Z_HEIGHT: 18.68
; LAYER_HEIGHT: 0.24
; WIPE_START
M73 P95 R0
G1 F9183.861
G1 X161.742 Y159.343 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 78/82
; update layer progress
M73 L78
M991 S0 P77 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z18.84 I-1.186 J-.273 P1  F60000
G1 X160.806 Y163.407 Z18.84
G1 Z18.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X161.946 Y156.593 E.04331
G1 X161.946 Y163.407 E.25885
G1 X160.866 Y163.407 E.04103
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6740
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X162.33 Y156.21 E.04005
G1 X162.33 Y163.79 E.2663
G1 X161.25 Y163.79 E.03794
M204 S10000
G1 X161.563 Y163.023 F60000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.419994
G1 F11895
M204 S8000
G1 X161.563 Y156.977 E.21241
G1 X160.607 Y156.977 E.03358
G1 X160.485 Y156.93 E.0046
G1 X160.423 Y156.793 E.0053
G1 X160.423 Y153.977 E.09892
G1 X159.377 Y153.977 E.03675
G1 X159.377 Y166.023 E.4232
G1 X160.423 Y166.023 E.03675
G1 X160.423 Y163.207 E.09892
G1 X160.485 Y163.07 E.0053
G1 X160.607 Y163.023 E.0046
G1 X161.503 Y163.023 E.03147
M204 S10000
G1 X161.195 Y162.655 F60000
; LINE_WIDTH: 0.406217
G1 F11895
M204 S8000
G1 X161.195 Y157.345 E.17955
G1 X160.607 Y157.345 E.01986
G1 X160.24 Y157.206 E.01329
G1 X160.075 Y156.886 E.01216
G1 X160.069 Y154.331 E.08642
G1 X159.731 Y154.331 E.01146
G1 X159.745 Y157.428 E.10474
G1 X159.731 Y165.669 E.27872
G1 X160.069 Y165.669 E.01146
G1 X160.069 Y163.207 E.08326
G1 X160.24 Y162.794 E.01511
G1 X160.607 Y162.655 E.01329
G1 X161.135 Y162.655 E.01783
; WIPE_START
G1 F12000
G1 X160.607 Y162.655 E-.20036
G1 X160.24 Y162.794 E-.14935
G1 X160.069 Y163.207 E-.16979
G1 X160.069 Y163.84 E-.24049
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.826 Y157.933 Z19.08 F60000
G1 Z18.68
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F11895
M204 S8000
G1 X160.826 Y157.714 E.00769
G1 X160.508 Y157.709 E.01117
G1 X160.114 Y157.534 E.01515
G1 X160.114 Y162.466 E.17329
G1 X160.508 Y162.291 E.01515
G1 X160.826 Y162.286 E.01117
G1 X160.826 Y157.993 E.15083
; WIPE_START
G1 F12000
G1 X160.826 Y159.993 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.47 Y161.937 Z19.08 F60000
G1 Z18.68
G1 E.8 F1800
; Slow Down Start
; LINE_WIDTH: 0.395104
G1 F1500;_EXTRUDE_SET_SPEED
M204 S8000
G1 X160.47 Y158.123 E.12497
; Slow Down End
; CHANGE_LAYER
; Z_HEIGHT: 18.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F1500
G1 X160.47 Y160.123 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 79/82
; update layer progress
M73 L79
M991 S0 P78 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z19.08 I-1.211 J.124 P1  F60000
G1 X160.806 Y163.407 Z19.08
G1 Z18.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F9913
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X161.706 Y156.593 E.03419
G1 X161.706 Y163.407 E.25885
G1 X160.866 Y163.407 E.03191
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6735
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X162.09 Y156.21 E.03162
G1 X162.09 Y163.79 E.2663
G1 X161.25 Y163.79 E.02951
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.56 Y162.265 Z19.32 F60000
G1 Z18.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.471794
G1 F9913
M204 S8000
G1 X160.56 Y157.735 E.18156
G1 X160.397 Y157.716 E.00659
G1 X160.14 Y157.446 E.01494
G1 X160.14 Y162.606 E.20676
G1 X160.397 Y162.284 E.01651
G1 X160.501 Y162.272 E.00419
; WIPE_START
G1 F10706.893
G1 X160.397 Y162.284 E-.0397
G1 X160.14 Y162.606 E-.15653
G1 X160.14 Y161.122 E-.56377
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.955 Y157.693 Z19.32 F60000
G1 Z18.92
G1 E.8 F1800
; LINE_WIDTH: 0.4051
G1 F9913
M204 S8000
G1 X160.955 Y157.345 E.01171
G1 X160.484 Y157.332 E.01586
G1 X160.075 Y156.886 E.0204
G1 X160.069 Y154.331 E.08615
G1 X159.731 Y154.331 E.01142
G1 X159.745 Y157.921 E.12104
G1 X159.731 Y165.669 E.26121
G1 X160.069 Y165.669 E.01142
G1 X160.069 Y163.207 E.083
G1 X160.484 Y162.668 E.02293
G1 X160.955 Y162.655 E.01586
G1 X160.955 Y157.753 E.16525
M204 S10000
G1 X161.323 Y157.693 F60000
; LINE_WIDTH: 0.419994
G1 F9913
M204 S8000
G1 X161.323 Y156.977 E.02515
G1 X160.607 Y156.977 E.02515
G1 X160.426 Y156.825 E.00833
G1 X160.423 Y153.977 E.10004
G1 X159.377 Y153.977 E.03675
G1 X159.377 Y166.023 E.4232
G1 X160.423 Y166.023 E.03675
G1 X160.423 Y163.207 E.09892
G1 X160.566 Y163.028 E.00807
G1 X161.323 Y163.023 E.02659
G1 X161.323 Y157.753 E.18516
; CHANGE_LAYER
; Z_HEIGHT: 19.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12212.001
G1 X161.323 Y159.753 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 80/82
; update layer progress
M73 L80
M991 S0 P79 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z19.32 I-1.205 J-.17 P1  F60000
G1 X160.806 Y163.407 Z19.32
G1 Z19.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8910
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X161.466 Y156.593 E.02508
G1 X161.466 Y163.407 E.25885
G1 X160.866 Y163.407 E.0228
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6734
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
M73 P96 R0
G1 X161.19 Y156.21 E.1054
G1 X161.85 Y156.21 E.02319
G1 X161.85 Y163.79 E.2663
G1 X161.25 Y163.79 E.02108
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.38 Y162.363 Z19.56 F60000
G1 Z19.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.351794
G1 F8910
M204 S8000
G1 X160.38 Y157.637 E.1353
G1 X160.285 Y157.619 E.00278
G1 X160.08 Y157.369 E.00925
G1 X160.08 Y162.681 E.15207
G1 X160.285 Y162.381 E.01039
G1 X160.321 Y162.374 E.00107
; WIPE_START
G1 F14985.516
G1 X160.285 Y162.381 E-.01414
G1 X160.08 Y162.681 E-.13795
G1 X160.08 Y161.081 E-.60791
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.715 Y157.453 Z19.56 F60000
G1 Z19.16
G1 E.8 F1800
; LINE_WIDTH: 0.405045
G1 F8910
M204 S8000
G1 X160.715 Y157.345 E.00362
G1 X160.406 Y157.308 E.01047
G1 X160.075 Y156.886 E.01807
G1 X160.069 Y154.331 E.08614
G1 X159.731 Y154.331 E.01142
G1 X159.745 Y157.759 E.11556
G1 X159.731 Y165.669 E.26664
G1 X160.069 Y165.669 E.01142
G1 X160.069 Y163.207 E.08299
G1 X160.406 Y162.692 E.02074
G1 X160.715 Y162.655 E.01047
G1 X160.715 Y157.513 E.17331
M204 S10000
G1 X161.083 Y157.453 F60000
; LINE_WIDTH: 0.419994
G1 F8910
M204 S8000
G1 X161.083 Y156.977 E.01671
G1 X160.54 Y156.964 E.01907
G1 X160.423 Y156.793 E.0073
G1 X160.423 Y153.977 E.09892
G1 X159.377 Y153.977 E.03675
G1 X159.377 Y166.023 E.4232
G1 X160.423 Y166.023 E.03675
G1 X160.423 Y163.207 E.09892
G1 X160.54 Y163.036 E.0073
G1 X161.083 Y163.023 E.01907
G1 X161.083 Y157.513 E.19359
; CHANGE_LAYER
; Z_HEIGHT: 19.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12212.001
G1 X161.083 Y159.513 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 81/82
; update layer progress
M73 L81
M991 S0 P80 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z19.56 I-1.214 J-.086 P1  F60000
G1 X160.806 Y163.407 Z19.56
G1 Z19.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8915
M204 S8000
G1 X160.806 Y166.407 E.11398
G1 X158.993 Y166.407 E.06888
G1 X158.993 Y153.593 E.4868
G1 X160.806 Y153.593 E.06888
G1 X160.806 Y156.593 E.11398
G1 X161.226 Y156.593 E.01596
G1 X161.226 Y163.407 E.25885
G1 X160.866 Y163.407 E.01368
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6734
M204 S5000
G1 X161.19 Y166.79 E.1054
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

G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X161.61 Y156.21 E.01476
G1 X161.61 Y163.79 E.2663
G1 X161.25 Y163.79 E.01265
; WIPE_START
G1 F12000
M204 S8000
G1 X161.21 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.884 Y158.164 Z19.8 F60000
G1 X160.843 Y157.213 Z19.8
G1 Z19.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F8915
M204 S8000
G1 X160.843 Y156.977 E.00828
G1 X160.507 Y156.948 E.01184
M73 P97 R0
G1 X160.423 Y156.793 E.00619
G1 X160.423 Y153.977 E.09892
G1 X159.377 Y153.977 E.03675
G1 X159.377 Y166.023 E.4232
G1 X160.423 Y166.023 E.03675
G1 X160.423 Y163.207 E.09892
G1 X160.507 Y163.052 E.00619
G1 X160.843 Y163.023 E.01184
G1 X160.843 Y157.273 E.20202
; WIPE_START
G1 F12212.001
G1 X160.843 Y159.273 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.11 Y162.437 Z19.8 F60000
G1 Z19.4
G1 E.8 F1800
; LINE_WIDTH: 0.412084
G1 F8915
M204 S8000
G1 X160.11 Y157.623 E.16546
; WIPE_START
G1 F12479.894
G1 X160.11 Y159.623 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.475 Y162.694 Z19.8 F60000
G1 Z19.4
G1 E.8 F1800
; LINE_WIDTH: 0.405155
G1 F8915
M204 S8000
G1 X160.475 Y157.306 E.18164
G1 X160.308 Y157.257 E.00587
G1 X160.075 Y156.886 E.01477
G1 X160.069 Y154.331 E.08616
G1 X159.731 Y154.331 E.01142
G1 X159.745 Y157.563 E.10901
G1 X159.731 Y165.669 E.27331
G1 X160.069 Y165.669 E.01142
G1 X160.069 Y163.207 E.08302
G1 X160.308 Y162.743 E.0176
G1 X160.417 Y162.711 E.00384
; CHANGE_LAYER
; Z_HEIGHT: 19.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12724.429
G1 X160.308 Y162.743 E-.04333
G1 X160.069 Y163.207 E-.19836
G1 X160.069 Y164.571 E-.51831
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 82/82
; update layer progress
M73 L82
M991 S0 P81 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z19.8 I-1.086 J.549 P1  F60000
G1 X161.19 Y166.79 Z19.8
G1 Z19.64
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6735
M204 S5000
G1 X158.61 Y166.79 E.09064
G1 X158.61 Y153.21 E.4771
G1 X161.19 Y153.21 E.09064
G1 X161.19 Y156.21 E.1054
G1 X161.37 Y156.21 E.00632
G1 X161.37 Y163.79 E.2663
G1 X161.19 Y163.79 E.00632
G1 X161.19 Y166.73 E.10329
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
G1 F12000
M204 S8000
G1 X159.191 Y166.776 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.141 Y166.586 Z20.04 F60000
G1 Z19.64
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F9110
M204 S2000
G1 X160.986 Y165.741 E.04541
G1 X161.129 Y165.598
G1 X161.129 Y165.034
G1 X160.986 Y165.177
G1 X159.577 Y166.586 E.07569
G1 X159.434 Y166.729
G1 X158.87 Y166.729
G1 X159.014 Y166.586
G1 X160.986 Y164.614 E.10597
G1 X161.129 Y164.47
G1 X161.129 Y163.907
G1 X160.986 Y164.05
G1 X158.814 Y166.222 E.11668
G1 X158.671 Y166.365
G1 X158.671 Y165.801
G1 X158.814 Y165.658
G1 X161.166 Y163.307 E.12635
G1 X161.309 Y163.163
G1 X161.309 Y162.6
G1 X161.166 Y162.743
G1 X158.814 Y165.095 E.12635
G1 X158.671 Y165.238
G1 X158.671 Y164.674
G1 X158.814 Y164.531
G1 X161.166 Y162.179 E.12635
G1 X161.309 Y162.036
G1 X161.309 Y161.473
G1 X161.166 Y161.616
G1 X158.814 Y163.968 E.12635
G1 X158.671 Y164.111
G1 X158.671 Y163.547
G1 X158.814 Y163.404
G1 X161.166 Y161.052 E.12635
G1 X161.309 Y160.909
G1 X161.309 Y160.346
G1 X161.166 Y160.489
G1 X158.814 Y162.84 E.12635
G1 X158.671 Y162.984
G1 X158.671 Y162.42
G1 X158.814 Y162.277
G1 X161.166 Y159.925 E.12635
G1 X161.309 Y159.782
G1 X161.309 Y159.219
G1 X161.166 Y159.362
G1 X158.814 Y161.713 E.12635
G1 X158.671 Y161.857
G1 X158.671 Y161.293
G1 X158.814 Y161.15
M73 P98 R0
G1 X161.166 Y158.798 E.12635
G1 X161.309 Y158.655
G1 X161.309 Y158.091
G1 X161.166 Y158.235
G1 X158.814 Y160.586 E.12635
G1 X158.671 Y160.729
G1 X158.671 Y160.166
G1 X158.814 Y160.023
G1 X161.166 Y157.671 E.12635
G1 X161.309 Y157.528
G1 X161.309 Y156.964
G1 X161.166 Y157.107
G1 X158.814 Y159.459 E.12635
G1 X158.671 Y159.602
G1 X158.671 Y159.039
G1 X158.814 Y158.896
G1 X161.166 Y156.544 E.12635
G1 X161.309 Y156.401
G1 X161.129 Y156.017
G1 X160.986 Y156.16
G1 X158.814 Y158.332 E.11668
G1 X158.671 Y158.475
G1 X158.671 Y157.912
G1 X158.814 Y157.768
G1 X160.986 Y155.597 E.11668
G1 X161.129 Y155.454
G1 X161.129 Y154.89
G1 X160.986 Y155.033
G1 X158.814 Y157.205 E.11668
G1 X158.671 Y157.348
G1 X158.671 Y156.785
G1 X158.814 Y156.641
G1 X160.986 Y154.47 E.11668
G1 X161.129 Y154.327
G1 X161.129 Y153.763
G1 X160.986 Y153.906
G1 X158.814 Y156.078 E.11668
G1 X158.671 Y156.221
G1 X158.671 Y155.657
G1 X158.814 Y155.514
G1 X160.914 Y153.414 E.11284
G1 X161.057 Y153.271
G1 X160.494 Y153.271
G1 X160.351 Y153.414
G1 X158.814 Y154.951 E.08256
G1 X158.671 Y155.094
G1 X158.671 Y154.53
G1 X158.814 Y154.387
G1 X159.787 Y153.414 E.05228
G1 X159.93 Y153.271
G1 X159.367 Y153.271
G1 X159.224 Y153.414
G1 X158.814 Y153.824 E.022
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F11292.473
M204 S8000
G1 X159.224 Y153.414 E-.22006
G1 X159.367 Y153.271 E-.07695
G1 X159.93 Y153.271 E-.21415
G1 X159.787 Y153.414 E-.07695
G1 X159.467 Y153.734 E-.1719
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z20.04 I1.217 J0 P1  F60000
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
G1 Z20.04 F900 ; lower z a little
M1002 judge_flag timelapse_record_flag
M622 J1
    G150.3
    M400 ; wait all motion done
    M991 S0 P-1 ;end smooth timelapse at safe pos
    M400 S5 ;wait for last picture to be taken
M623  ;end of "timelapse_record_flag"

G90
G1 Z29.64 F900 ; lower z a little

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

    
        G1 Z109.82 F600
        G1 Z107.82
    

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

