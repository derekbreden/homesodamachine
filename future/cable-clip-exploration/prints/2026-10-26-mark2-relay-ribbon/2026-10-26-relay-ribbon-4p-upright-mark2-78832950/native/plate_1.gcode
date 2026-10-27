; HEADER_BLOCK_START
; BambuStudio 02.08.02.61
; model printing time: 4m 50s; total estimated time: 10m 0s
; total layer number: 107
; total filament length [mm] : 697.53
; total filament volume [cm^3] : 1677.75
; total filament weight [g] : 2.16
; filament_density: 1.29
; filament_diameter: 1.75
; max_z_height: 25.64
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
; brim_type = no_brim
; brim_width = 0
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
M73 P0 R10
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
    
M73 P0 R9
        G1 E45 F449.008
    
M73 P2 R9
    G1 E-3 F1800
    M400 P500
    G150.2
    G150.1


G91
M73 P4 R9
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
M73 P5 R9
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
M73 P49 R5
G1 X175 Y160 F30000

M622 J1
    M1002 gcode_claim_action : 1
    G29.20 A3
    G29 A1 O X158.4 Y148 I8.20001 J24 R
    M400
M623

M622 J2
    M1002 gcode_claim_action : 1
    
        G29.20 A4
        G29 A2 O X158.4 Y148 I8.20001 J24 R
    
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
    G1 Z0.8 F1200
    G90
M73 P50 R5
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
; layer num/total_layer_count: 1/107
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
; OBJECT_ID: 1901
M73 P50 R4
G1 X160.543 Y148.857 F60000
M204 S6000
M73 P51 R4
G1 Z.4
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X160.543 Y171.143 E.80931
G1 X159.257 Y171.143 E.0467
G1 X159.257 Y148.857 E.80931
G1 X160.483 Y148.857 E.04452
M204 S6000
G1 X161 Y148.4 F60000
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X161 Y171.6 E.84251
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

G1 X158.8 Y171.6 E.07989
G1 X158.8 Y148.4 E.84251
G1 X160.94 Y148.4 E.07771
; WIPE_START
M73 P52 R4
G1 X160.945 Y150.4 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X159.44 Y149.057 Z.6 F60000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50621
G1 F6300
M204 S500
G1 X160.154 Y149.771 E.03719
G1 X160.154 Y150.427 E.02412
G1 X159.646 Y149.918 E.02649
G1 X159.646 Y150.573 E.02412
G1 X160.154 Y151.082 E.02649
G1 X160.154 Y151.737 E.02412
G1 X159.646 Y151.228 E.02649
G1 X159.646 Y151.883 E.02412
G1 X160.154 Y152.392 E.02649
G1 X160.154 Y153.047 E.02412
G1 X159.646 Y152.538 E.02649
G1 X159.646 Y153.194 E.02412
G1 X160.154 Y153.702 E.02649
G1 X160.154 Y154.358 E.02412
G1 X159.646 Y153.849 E.02649
G1 X159.646 Y154.504 E.02412
G1 X160.154 Y155.013 E.02649
G1 X160.154 Y155.668 E.02412
G1 X159.646 Y155.159 E.02649
G1 X159.646 Y155.814 E.02412
G1 X160.154 Y156.323 E.02649
G1 X160.154 Y156.978 E.02412
G1 X159.646 Y156.47 E.02649
G1 X159.646 Y157.125 E.02412
G1 X160.154 Y157.634 E.02649
G1 X160.154 Y158.289 E.02412
G1 X159.646 Y157.78 E.02649
G1 X159.646 Y158.435 E.02412
G1 X160.154 Y158.944 E.02649
G1 X160.154 Y159.599 E.02412
G1 X159.646 Y159.09 E.02649
G1 X159.646 Y159.746 E.02412
G1 X160.154 Y160.254 E.02649
G1 X160.154 Y160.91 E.02412
G1 X159.646 Y160.401 E.02649
G1 X159.646 Y161.056 E.02412
G1 X160.154 Y161.565 E.02649
G1 X160.154 Y162.22 E.02412
G1 X159.646 Y161.711 E.02649
G1 X159.646 Y162.366 E.02412
G1 X160.154 Y162.875 E.02649
G1 X160.154 Y163.53 E.02412
G1 X159.646 Y163.022 E.02649
G1 X159.646 Y163.677 E.02412
G1 X160.154 Y164.186 E.02649
G1 X160.154 Y164.841 E.02412
G1 X159.646 Y164.332 E.02649
G1 X159.646 Y164.987 E.02412
G1 X160.154 Y165.496 E.02649
G1 X160.154 Y166.151 E.02412
G1 X159.646 Y165.642 E.02649
G1 X159.646 Y166.297 E.02412
G1 X160.154 Y166.806 E.02649
G1 X160.154 Y167.461 E.02412
G1 X159.646 Y166.953 E.02649
G1 X159.646 Y167.608 E.02412
G1 X160.154 Y168.117 E.02649
G1 X160.154 Y168.772 E.02412
G1 X159.646 Y168.263 E.02649
G1 X159.646 Y168.918 E.02412
G1 X160.154 Y169.427 E.02649
G1 X160.154 Y170.082 E.02412
G1 X159.646 Y169.573 E.02649
G1 X159.646 Y170.229 E.02412
G1 X160.36 Y170.943 E.03719
; CHANGE_LAYER
; Z_HEIGHT: 0.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F6300
G1 X159.646 Y170.229 E-.38399
G1 X159.646 Y169.573 E-.24897
G1 X159.882 Y169.81 E-.12704
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 2/107
; update layer progress
M73 L2
M991 S0 P1 ;notify layer change
; open powerlost recovery
M1003 S1
M104 S280 ; set nozzle temperature
; OBJECT_ID: 1901
M204 S10000
G17
G3 Z.6 I1.216 J.053 P1  F60000
G1 X160.806 Y148.593 Z.6
G1 Z.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.423 Y149.5 Z.84 F60000
G1 Z.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X160.423 Y148.977 E.01838
G1 X159.377 Y148.977 E.03675
G1 X159.377 Y171.023 E.77452
G1 X160.423 Y171.023 E.03675
G1 X160.423 Y149.56 E.75404
M204 S10000
G1 X160.069 Y149.5 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X160.069 Y149.331 E.00547
G1 X159.731 Y149.331 E.01094
G1 X159.731 Y170.669 E.68923
G1 X160.069 Y170.669 E.01094
G1 X160.069 Y149.56 E.68182
; CHANGE_LAYER
; Z_HEIGHT: 0.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X160.069 Y151.56 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 3/107
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z.84 I1.181 J.293 P1  F60000
G1 X160.806 Y148.593 Z.84
G1 Z.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
M73 P53 R4
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8407
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.423 Y149.5 Z1.08 F60000
G1 Z.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X160.423 Y148.977 E.01838
G1 X159.377 Y148.977 E.03675
G1 X159.377 Y171.023 E.77452
G1 X160.423 Y171.023 E.03675
G1 X160.423 Y149.56 E.75404
M204 S10000
G1 X160.069 Y149.5 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X160.069 Y149.331 E.00547
G1 X159.731 Y149.331 E.01094
G1 X159.731 Y170.669 E.68923
G1 X160.069 Y170.669 E.01094
G1 X160.069 Y149.56 E.68182
; CHANGE_LAYER
; Z_HEIGHT: 0.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X160.069 Y151.56 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 4/107
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.08 I1.181 J.293 P1  F60000
G1 X160.806 Y148.593 Z1.08
G1 Z.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8405
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8405
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y149.008 Z1.32 F60000
G1 Z.92
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8405
M204 S8000
G1 X159.334 Y150.602 E.06056
G1 X159.507 Y150.714 E.00781
G1 X159.935 Y151.14 E.02292
G1 X160.362 Y151.825 E.03068
G1 X160.466 Y152.021 E.00843
G1 X160.466 Y153.516 E.0568
G1 X160.362 Y153.464 E.0044
G1 X159.935 Y153.529 E.01643
G1 X159.334 Y153.76 E.02443
G1 X159.334 Y157.443 E.13994
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
G1 X160.362 Y165.507 E.03068
G1 X160.466 Y165.703 E.00843
G1 X160.466 Y167.198 E.0568
G1 X160.362 Y167.146 E.0044
G1 X159.935 Y167.211 E.01643
G1 X159.334 Y167.442 E.02443
G1 X159.334 Y169.036 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.442 E-.60571
G1 X159.713 Y167.296 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 5/107
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.32 I1.215 J.071 P1  F60000
G1 X160.806 Y148.593 Z1.32
G1 Z1.16
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8629
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8406
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y149.048 Z1.56 F60000
G1 Z1.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8629
M204 S8000
G1 X159.334 Y150.642 E.06056
G1 X159.507 Y150.723 E.00725
G1 X159.935 Y151.045 E.02034
G1 X160.466 Y151.692 E.03179
G1 X160.466 Y153.972 E.08662
G1 X160.362 Y153.89 E.00502
G1 X159.935 Y153.793 E.01666
G1 X159.334 Y153.897 E.02315
G1 X159.334 Y157.483 E.13622
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
G1 X160.466 Y167.654 E.08662
G1 X160.362 Y167.572 E.00502
G1 X159.935 Y167.475 E.01666
G1 X159.334 Y167.579 E.02315
G1 X159.334 Y169.173 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.579 E-.60571
G1 X159.734 Y167.51 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 6/107
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.56 I1.215 J.069 P1  F60000
G1 X160.806 Y148.593 Z1.56
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8704
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8406
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
M73 P54 R4
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y149.055 Z1.8 F60000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8704
M204 S8000
G1 X159.334 Y150.649 E.06056
G1 X159.507 Y150.702 E.00686
G1 X159.935 Y150.94 E.01858
G1 X160.466 Y151.457 E.02815
G1 X160.466 Y154.268 E.10681
G1 X160.362 Y154.179 E.00517
G1 X159.935 Y153.995 E.01768
G1 X159.507 Y153.947 E.01635
G1 X159.334 Y153.965 E.0066
G1 X159.334 Y157.49 E.13394
G1 X159.507 Y157.543 E.00686
G1 X159.935 Y157.781 E.01858
G1 X160.466 Y158.298 E.02815
G1 X160.466 Y161.109 E.10681
G1 X160.362 Y161.021 E.00517
G1 X159.935 Y160.837 E.01768
G1 X159.507 Y160.788 E.01635
G1 X159.334 Y160.806 E.0066
G1 X159.334 Y164.331 E.13394
G1 X159.507 Y164.384 E.00686
G1 X159.935 Y164.622 E.01858
G1 X160.466 Y165.139 E.02815
G1 X160.466 Y167.95 E.10681
G1 X160.362 Y167.862 E.00517
G1 X159.935 Y167.678 E.01768
G1 X159.507 Y167.629 E.01635
G1 X159.334 Y167.647 E.0066
G1 X159.334 Y169.241 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.647 E-.60571
G1 X159.507 Y167.629 E-.06596
G1 X159.738 Y167.655 E-.08832
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 7/107
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.8 I1.215 J.068 P1  F60000
G1 X160.806 Y148.593 Z1.8
G1 Z1.64
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8778
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8406
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y149.036 Z2.04 F60000
G1 Z1.64
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8778
M204 S8000
G1 X159.334 Y150.63 E.06056
G1 X159.507 Y150.655 E.00663
G1 X159.935 Y150.818 E.01738
G1 X160.362 Y151.111 E.01968
G1 X160.466 Y151.209 E.00543
G1 X160.466 Y154.504 E.12516
G1 X160.362 Y154.41 E.00531
G1 X159.935 Y154.157 E.01886
G1 X159.507 Y154.036 E.01688
G1 X159.334 Y154.027 E.00657
G1 X159.334 Y157.471 E.13085
G1 X159.507 Y157.496 E.00663
G1 X159.935 Y157.659 E.01738
G1 X160.362 Y157.952 E.01968
G1 X160.466 Y158.051 E.00543
G1 X160.466 Y161.345 E.12516
G1 X160.362 Y161.251 E.00531
G1 X159.935 Y160.999 E.01886
G1 X159.507 Y160.877 E.01688
G1 X159.334 Y160.868 E.00657
G1 X159.334 Y164.312 E.13085
G1 X159.507 Y164.337 E.00663
G1 X159.935 Y164.5 E.01738
G1 X160.362 Y164.793 E.01968
G1 X160.466 Y164.892 E.00543
G1 X160.466 Y168.186 E.12516
G1 X160.362 Y168.092 E.00531
G1 X159.935 Y167.84 E.01886
G1 X159.507 Y167.718 E.01688
G1 X159.334 Y167.709 E.00657
G1 X159.334 Y169.303 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.709 E-.60571
G1 X159.507 Y167.718 E-.0657
G1 X159.731 Y167.782 E-.08859
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 8/107
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.04 I1.215 J.068 P1  F60000
G1 X160.806 Y148.593 Z2.04
G1 Z1.88
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8764
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8405
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y149.396 Z2.28 F60000
G1 Z1.88
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8764
M204 S8000
G1 X160.466 Y150.99 E.06056
G1 X160.362 Y150.898 E.00524
G1 X159.935 Y150.674 E.01835
G1 X159.507 Y150.582 E.01661
G1 X159.334 Y150.584 E.00656
G1 X159.334 Y154.062 E.13212
G1 X159.507 Y154.098 E.00671
G1 X159.935 Y154.291 E.01782
G1 X160.362 Y154.615 E.02037
G1 X160.466 Y154.718 E.00554
G1 X160.466 Y157.831 E.11828
G1 X160.362 Y157.74 E.00524
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
G1 X159.334 Y167.744 E.13212
G1 X159.507 Y167.781 E.00671
G1 X159.935 Y167.973 E.01782
G1 X160.362 Y168.297 E.02037
G1 X160.466 Y168.4 E.00554
G1 X160.466 Y169.994 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 2.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y168.4 E-.60571
G1 X160.362 Y168.297 E-.05545
G1 X160.155 Y168.14 E-.09884
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 9/107
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.28 I1.216 J.041 P1  F60000
G1 X160.806 Y148.593 Z2.28
G1 Z2.12
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8970
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8404
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y149.141 Z2.52 F60000
G1 Z2.12
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8970
M204 S8000
G1 X160.466 Y150.735 E.06056
G1 X160.362 Y150.649 E.00512
G1 X159.935 Y150.497 E.01724
G1 X159.334 Y150.537 E.02285
G1 X159.334 Y154.07 E.13423
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
G1 X159.334 Y167.752 E.13423
G1 X159.507 Y167.817 E.007
G1 X159.935 Y168.088 E.01923
G1 X160.466 Y168.65 E.02938
G1 X160.466 Y171.066 E.09177
G1 X160.063 Y171.066 E.01529
G1 X159.935 Y171.02 E.00518
G1 X159.334 Y171.06 E.02285
M73 P55 R4
G1 X159.334 Y169.466 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 2.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y171.06 E-.60572
G1 X159.74 Y171.033 E-.15428
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 10/107
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.52 I1.216 J.058 P1  F60000
G1 X160.806 Y148.593 Z2.52
G1 Z2.36
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8954
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8403
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y151.988 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8954
M204 S8000
G1 X160.466 Y150.394 E.06056
G1 X160.362 Y150.317 E.00489
G1 X159.935 Y150.272 E.01634
G1 X159.334 Y150.426 E.02354
G1 X159.334 Y154.05 E.1377
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
G1 X160.466 Y162.078 E.0343
G1 X160.466 Y164.076 E.07593
G1 X160.362 Y163.999 E.00489
G1 X159.935 Y163.954 E.01634
G1 X159.334 Y164.108 E.02354
G1 X159.334 Y167.732 E.1377
G1 X159.507 Y167.826 E.00747
G1 X159.935 Y168.188 E.02129
G1 X160.466 Y168.919 E.0343
G1 X160.466 Y170.917 E.07593
G1 X160.362 Y170.84 E.00489
G1 X159.935 Y170.795 E.01634
G1 X159.334 Y170.949 E.02354
G1 X159.334 Y169.355 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y170.949 E-.60572
G1 X159.728 Y170.848 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 11/107
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.76 I1.216 J.059 P1  F60000
G1 X160.806 Y148.593 Z2.76
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8842
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8401
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y151.165 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8842
M204 S8000
G1 X160.466 Y149.571 E.06056
G1 X160.405 Y149.738 E.00677
G1 X159.506 Y150.166 E.03783
G1 X159.334 Y150.267 E.00758
G1 X159.334 Y153.989 E.14139
G1 X159.818 Y154.442 E.02517
G1 X160.104 Y154.869 E.01954
G1 X160.458 Y155.724 E.03517
G1 X160.466 Y156.412 E.02612
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
G1 X159.334 Y163.95 E.00758
G1 X159.334 Y167.671 E.14139
G1 X159.818 Y168.124 E.02517
G1 X160.104 Y168.551 E.01954
G1 X160.458 Y169.406 E.03517
G1 X160.466 Y170.094 E.02612
G1 X160.405 Y170.262 E.00677
G1 X159.506 Y170.689 E.03783
G1 X159.334 Y170.791 E.00758
G1 X159.334 Y169.197 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 2.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y170.791 E-.60572
G1 X159.506 Y170.689 E-.07579
G1 X159.693 Y170.6 E-.0785
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 12/107
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3 I1.215 J.062 P1  F60000
G1 X160.806 Y148.593 Z3
G1 Z2.84
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8748
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8400
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y150.239 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8748
M204 S8000
G1 X160.466 Y148.934 E.04955
G1 X160.176 Y148.934 E.01101
G1 X160.103 Y149.311 E.01457
G1 X159.767 Y149.738 E.02066
G1 X159.334 Y150.081 E.02097
G1 X159.334 Y153.906 E.14532
G1 X159.47 Y154.014 E.00659
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
G1 X159.334 Y163.764 E.02097
G1 X159.334 Y167.588 E.14532
G1 X159.47 Y167.696 E.00659
G1 X159.805 Y168.124 E.02062
G1 X160.016 Y168.551 E.01812
G1 X160.186 Y169.406 E.03312
G1 X160.103 Y169.834 E.01655
G1 X159.767 Y170.262 E.02066
G1 X159.334 Y170.605 E.02097
G1 X159.334 Y171.066 E.01751
G1 X160.466 Y171.064 E.04297
; CHANGE_LAYER
; Z_HEIGHT: 3.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y171.066 E-.42981
G1 X159.334 Y170.605 E-.17518
G1 X159.654 Y170.351 E-.155
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 13/107
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.24 I1.215 J.064 P1  F60000
G1 X160.806 Y148.593 Z3.24
G1 Z3.08
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8684
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8398
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
M73 P56 R4
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y150.018 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8684
M204 S8000
G1 X160.466 Y148.934 E.04118
G1 X159.955 Y148.934 E.01938
G1 X159.802 Y149.311 E.01545
G1 X159.334 Y149.842 E.02688
G1 X159.334 Y153.774 E.14936
G1 X159.574 Y154.014 E.01291
G1 X159.822 Y154.442 E.01877
G1 X159.962 Y154.869 E.01709
G1 X159.976 Y155.724 E.03249
G1 X159.802 Y156.152 E.01755
G1 X159.334 Y156.683 E.02688
G1 X159.334 Y160.615 E.14936
G1 X159.574 Y160.855 E.01291
G1 X159.822 Y161.283 E.01877
G1 X159.962 Y161.71 E.01709
G1 X159.976 Y162.565 E.03249
G1 X159.802 Y162.993 E.01755
G1 X159.334 Y163.524 E.02688
G1 X159.334 Y167.456 E.14936
G1 X159.574 Y167.696 E.01291
G1 X159.822 Y168.124 E.01877
G1 X159.962 Y168.551 E.01709
G1 X159.976 Y169.406 E.03249
G1 X159.802 Y169.834 E.01755
G1 X159.334 Y170.365 E.02688
G1 X159.334 Y171.066 E.0266
G1 X160.228 Y171.066 E.03396
; CHANGE_LAYER
; Z_HEIGHT: 3.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y171.066 E-.33966
G1 X159.334 Y170.365 E-.26605
G1 X159.603 Y170.061 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 14/107
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.48 I1.215 J.068 P1  F60000
G1 X160.806 Y148.593 Z3.48
G1 Z3.32
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8644
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8398
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y149.844 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8644
M204 S8000
G1 X160.466 Y148.934 E.03455
G1 X159.781 Y148.934 E.02601
G1 X159.566 Y149.311 E.01647
G1 X159.334 Y149.568 E.01314
G1 X159.334 Y153.527 E.15042
G1 X159.694 Y154.014 E.02299
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
G1 X159.334 Y167.209 E.15043
G1 X159.694 Y167.696 E.02299
G1 X159.866 Y168.124 E.01751
G1 X159.937 Y168.551 E.01647
G1 X159.922 Y168.979 E.01625
G1 X159.81 Y169.406 E.01679
G1 X159.566 Y169.834 E.0187
G1 X159.334 Y170.091 E.01314
G1 X159.334 Y171.066 E.03703
G1 X159.954 Y171.066 E.02353
; CHANGE_LAYER
; Z_HEIGHT: 3.56
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y171.066 E-.23533
G1 X159.334 Y170.091 E-.37038
G1 X159.566 Y169.834 E-.13141
G1 X159.596 Y169.782 E-.02287
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 15/107
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.72 I1.215 J.069 P1  F60000
G1 X160.806 Y148.593 Z3.72
G1 Z3.56
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8624
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8403
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y149.698 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8624
M204 S8000
G1 X160.466 Y148.934 E.02903
G1 X159.636 Y148.934 E.03153
G1 X159.334 Y149.336 E.01908
G1 X159.334 Y153.287 E.15011
G1 X159.602 Y153.587 E.01525
G1 X159.835 Y154.014 E.0185
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
G1 X159.334 Y166.969 E.15011
G1 X159.602 Y167.269 E.01525
G1 X159.835 Y167.696 E.0185
G1 X159.935 Y168.124 E.01669
G1 X159.939 Y168.551 E.01624
G1 X159.857 Y168.979 E.01654
G1 X159.673 Y169.406 E.01768
G1 X159.334 Y169.859 E.02148
G1 X159.334 Y171.066 E.04583
G1 X159.722 Y171.066 E.01473
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y171.066 E-.14736
G1 X159.334 Y169.859 E-.45836
G1 X159.578 Y169.534 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 16/107
; update layer progress
M73 L16
M991 S0 P15 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.96 I1.215 J.071 P1  F60000
G1 X160.806 Y148.593 Z3.96
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8354
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8354
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y151.42 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8354
M204 S8000
G1 X159.334 Y153.014 E.06056
G1 X159.484 Y153.159 E.00794
G1 X159.845 Y153.587 E.02124
G1 X160.007 Y154.014 E.01737
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
M73 P57 R4
G1 X159.334 Y162.781 E.01176
G1 X159.334 Y166.696 E.14873
G1 X159.484 Y166.841 E.00794
G1 X159.845 Y167.269 E.02124
G1 X160.007 Y167.696 E.01737
G1 X159.968 Y168.551 E.03252
G1 X159.817 Y168.979 E.01723
G1 X159.557 Y169.406 E.01902
G1 X159.334 Y169.622 E.01176
G1 X159.334 Y171.066 E.05485
G1 X159.485 Y171.066 E.00571
; CHANGE_LAYER
; Z_HEIGHT: 4.04
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y171.066 E-.05713
G1 X159.334 Y169.622 E-.54859
G1 X159.557 Y169.406 E-.1176
G1 X159.607 Y169.324 E-.03669
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 17/107
; update layer progress
M73 L17
M991 S0 P16 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z4.2 I1.215 J.07 P1  F60000
G1 X160.806 Y148.593 Z4.2
G1 Z4.04
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8400
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8400
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y151.186 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8400
M204 S8000
G1 X159.334 Y152.78 E.06056
G1 X159.835 Y153.159 E.02384
G1 X160.162 Y153.587 E.02045
G1 X160.225 Y154.014 E.01642
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
G1 X159.334 Y166.463 E.1446
G1 X159.835 Y166.841 E.02384
G1 X160.162 Y167.269 E.02045
G1 X160.225 Y167.696 E.01642
G1 X160.028 Y168.551 E.03334
G1 X159.804 Y168.979 E.01832
G1 X159.455 Y169.406 E.02099
G1 X159.334 Y169.497 E.00573
G1 X159.334 Y171.066 E.05958
G1 X159.36 Y171.066 E.00098
; CHANGE_LAYER
; Z_HEIGHT: 4.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y171.066 E-.00983
G1 X159.334 Y169.497 E-.59589
G1 X159.455 Y169.406 E-.05729
G1 X159.616 Y169.209 E-.09699
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 18/107
; update layer progress
M73 L18
M991 S0 P17 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z4.44 I1.215 J.07 P1  F60000
G1 X160.806 Y148.593 Z4.44
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8518
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8485
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y151.007 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8518
M204 S8000
G1 X159.334 Y152.6 E.06056
G1 X159.935 Y152.868 E.02497
G1 X160.362 Y153.009 E.0171
G1 X160.466 Y153.012 E.00393
G1 X160.466 Y154.122 E.04218
G1 X160.362 Y154.386 E.01074
G1 X159.935 Y155.156 E.03347
G1 X159.507 Y155.612 E.02375
G1 X159.334 Y155.731 E.00797
G1 X159.334 Y159.442 E.14096
G1 X159.935 Y159.709 E.02497
G1 X160.362 Y159.85 E.0171
G1 X160.466 Y159.853 E.00393
G1 X160.466 Y160.963 E.04218
G1 X160.362 Y161.227 E.01074
G1 X159.935 Y161.997 E.03347
G1 X159.507 Y162.453 E.02375
G1 X159.334 Y162.572 E.00797
G1 X159.334 Y166.283 E.14096
G1 X159.935 Y166.55 E.02497
G1 X160.362 Y166.691 E.0171
G1 X160.466 Y166.694 E.00393
G1 X160.466 Y167.804 E.04218
G1 X160.362 Y168.068 E.01074
G1 X159.935 Y168.838 E.03347
G1 X159.507 Y169.294 E.02375
G1 X159.334 Y169.413 E.00797
G1 X159.334 Y171.007 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 4.52
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y169.413 E-.60571
G1 X159.507 Y169.294 E-.07973
G1 X159.641 Y169.151 E-.07456
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 19/107
; update layer progress
M73 L19
M991 S0 P18 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z4.68 I1.215 J.069 P1  F60000
G1 X160.806 Y148.593 Z4.68
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8625
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8534
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y150.857 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8625
M204 S8000
G1 X159.334 Y152.451 E.06056
G1 X159.935 Y152.585 E.02337
G1 X160.362 Y152.518 E.01644
G1 X160.466 Y152.438 E.00495
G1 X160.466 Y154.554 E.08037
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
G1 X159.334 Y166.133 E.13711
G1 X159.935 Y166.267 E.02337
G1 X160.362 Y166.2 E.01644
G1 X160.466 Y166.12 E.00495
G1 X160.466 Y168.236 E.08037
G1 X159.935 Y168.93 E.03321
G1 X159.507 Y169.276 E.0209
G1 X159.334 Y169.365 E.00738
G1 X159.334 Y170.959 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 4.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y169.365 E-.60571
G1 X159.507 Y169.276 E-.07381
G1 X159.672 Y169.143 E-.08048
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 20/107
; update layer progress
M73 L20
M991 S0 P19 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z4.92 I1.215 J.067 P1  F60000
G1 X160.806 Y148.593 Z4.92
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8696
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8588
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
M73 P58 R4
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y150.752 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8696
M204 S8000
G1 X159.334 Y152.346 E.06056
G1 X159.935 Y152.369 E.02282
G1 X160.362 Y152.204 E.01741
G1 X160.466 Y152.117 E.00514
G1 X160.466 Y154.807 E.1022
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
G1 X160.466 Y168.489 E.1022
G1 X159.935 Y169.032 E.02886
G1 X159.507 Y169.29 E.01896
G1 X159.334 Y169.35 E.00694
G1 X159.334 Y170.944 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 5
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y169.35 E-.60571
G1 X159.507 Y169.29 E-.06946
G1 X159.698 Y169.175 E-.08483
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 21/107
; update layer progress
M73 L21
M991 S0 P20 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z5.16 I1.215 J.065 P1  F60000
G1 X160.806 Y148.593 Z5.16
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8772
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8642
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y150.71 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8772
M204 S8000
G1 X159.334 Y152.304 E.06056
G1 X159.507 Y152.302 E.00656
G1 X159.935 Y152.198 E.01671
G1 X160.362 Y151.963 E.01855
G1 X160.466 Y151.87 E.00527
G1 X160.466 Y155.055 E.121
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
G1 X160.466 Y165.553 E.00527
G1 X160.466 Y168.737 E.121
G1 X160.362 Y168.838 E.00549
G1 X159.935 Y169.149 E.02009
G1 X159.507 Y169.331 E.01764
G1 X159.334 Y169.363 E.00667
G1 X159.334 Y170.957 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 5.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y169.363 E-.60571
G1 X159.507 Y169.331 E-.06674
G1 X159.719 Y169.241 E-.08755
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 22/107
; update layer progress
M73 L22
M991 S0 P21 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z5.4 I1.215 J.064 P1  F60000
G1 X160.806 Y148.593 Z5.4
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8784
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8698
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y150.06 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8784
M204 S8000
G1 X160.466 Y151.654 E.06056
G1 X160.362 Y151.754 E.00547
G1 X159.935 Y152.058 E.01994
G1 X159.507 Y152.233 E.01755
G1 X159.334 Y152.263 E.00666
G1 X159.334 Y155.72 E.13135
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
G1 X159.334 Y169.402 E.13135
G1 X159.507 Y169.397 E.00656
G1 X159.935 Y169.287 E.01677
G1 X160.362 Y169.046 E.01866
G1 X160.466 Y168.953 E.00528
G1 X160.466 Y170.547 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 5.48
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y168.953 E-.60571
G1 X160.362 Y169.046 E-.05281
G1 X160.13 Y169.177 E-.10148
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 23/107
; update layer progress
M73 L23
M991 S0 P22 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z5.64 I1.216 J.04 P1  F60000
G1 X160.806 Y148.593 Z5.64
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8745
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8745
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y149.812 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8745
M204 S8000
G1 X160.466 Y151.406 E.06056
G1 X159.935 Y151.94 E.0286
G1 X159.507 Y152.19 E.01882
G1 X159.334 Y152.247 E.00691
G1 X159.334 Y155.759 E.13341
G1 X159.935 Y155.773 E.02281
G1 X160.362 Y155.601 E.01751
G1 X160.466 Y155.513 E.00515
G1 X160.466 Y158.247 E.10387
G1 X159.935 Y158.781 E.0286
G1 X159.507 Y159.031 E.01882
G1 X159.334 Y159.089 E.00691
G1 X159.334 Y162.6 E.13341
G1 X159.935 Y162.614 E.02281
G1 X160.362 Y162.442 E.01751
G1 X160.466 Y162.354 E.00515
G1 X160.466 Y165.088 E.10387
G1 X159.935 Y165.622 E.0286
G1 X159.507 Y165.872 E.01882
G1 X159.334 Y165.93 E.00691
G1 X159.334 Y169.441 E.13341
G1 X159.935 Y169.455 E.02281
M73 P59 R4
G1 X160.362 Y169.283 E.01751
G1 X160.466 Y169.195 E.00515
G1 X160.466 Y170.789 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 5.72
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y169.195 E-.60571
G1 X160.362 Y169.283 E-.0515
G1 X160.111 Y169.384 E-.10279
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 24/107
; update layer progress
M73 L24
M991 S0 P23 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z5.88 I1.216 J.041 P1  F60000
G1 X160.806 Y148.593 Z5.88
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8955
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8821
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y150.613 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8955
M204 S8000
G1 X159.334 Y149.019 E.06056
G1 X159.935 Y149.143 E.02328
G1 X160.362 Y149.064 E.01652
G1 X160.466 Y148.984 E.00498
G1 X160.466 Y151.16 E.08268
G1 X159.935 Y151.836 E.03267
G1 X159.507 Y152.174 E.0207
G1 X159.334 Y152.26 E.00733
G1 X159.334 Y155.86 E.13679
G1 X159.935 Y155.984 E.02328
G1 X160.362 Y155.905 E.01652
G1 X160.466 Y155.825 E.00498
G1 X160.466 Y158.001 E.08268
G1 X159.935 Y158.677 E.03267
G1 X159.507 Y159.015 E.0207
G1 X159.334 Y159.101 E.00733
G1 X159.334 Y162.702 E.13679
G1 X159.935 Y162.825 E.02328
G1 X160.362 Y162.746 E.01652
G1 X160.466 Y162.666 E.00498
G1 X160.466 Y164.842 E.08268
G1 X159.935 Y165.518 E.03267
G1 X159.507 Y165.856 E.0207
G1 X159.334 Y165.942 E.00733
G1 X159.334 Y169.543 E.13679
G1 X159.935 Y169.666 E.02328
G1 X160.362 Y169.588 E.01652
G1 X160.466 Y169.507 E.00498
G1 X160.466 Y167.913 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 5.96
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y169.507 E-.60572
G1 X160.362 Y169.588 E-.04983
G1 X160.092 Y169.637 E-.10445
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 25/107
; update layer progress
M73 L25
M991 S0 P24 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z6.12 I1.216 J.041 P1  F60000
G1 X160.806 Y148.593 Z6.12
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8870
M204 S8000
G1 X160.806 Y171.407 E.86673
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8870
M204 S5000
G1 X161.19 Y171.79 E.82842
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.135 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y150.758 Z6.36 F60000
G1 Z5.96
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8870
M204 S8000
G1 X159.334 Y149.164 E.06056
G1 X159.935 Y149.419 E.02476
G1 X160.362 Y149.53 E.01678
G1 X160.466 Y149.5 E.00409
G1 X160.466 Y150.781 E.04867
G1 X160.362 Y151.006 E.00944
G1 X159.935 Y151.743 E.03237
G1 X159.507 Y152.188 E.02345
G1 X159.334 Y152.305 E.00791
G1 X159.334 Y156.005 E.14059
G1 X159.935 Y156.26 E.02477
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
G1 X159.334 Y169.687 E.14059
G1 X159.935 Y169.942 E.02477
G1 X160.362 Y170.053 E.01678
G1 X160.466 Y170.023 E.00409
G1 X160.466 Y168.429 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 6.2
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y170.023 E-.60572
G1 X160.362 Y170.053 E-.04089
G1 X160.073 Y169.978 E-.11339
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 26/107
; update layer progress
M73 L26
M991 S0 P25 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z6.36 I1.216 J.042 P1  F60000
G1 X160.806 Y148.593 Z6.36
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8835
M204 S8000
G1 X160.806 Y156.593 E.30394
G1 X160.886 Y156.593 E.00304
G1 X160.886 Y163.407 E.25885
G1 X160.806 Y163.407 E.00304
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.746 Y148.593 E.0666
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y148.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8835
M204 S5000
G1 X161.19 Y156.21 E.28106
G1 X161.231 Y156.21 E.00144
G1 X161.27 Y156.21 E.00137
G1 X161.27 Y163.79 E.2663
G1 X161.231 Y163.79 E.00137
G1 X161.19 Y163.79 E.00144
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.13 Y148.21 E.08853
; WIPE_START
G1 F12000
M204 S8000
G1 X161.145 Y150.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y150.934 Z6.6 F60000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8835
M204 S8000
G1 X159.334 Y149.34 E.06056
G1 X159.876 Y149.738 E.02552
G1 X160.197 Y150.166 E.02032
G1 X160.247 Y150.594 E.01636
G1 X160.034 Y151.449 E.03348
G1 X159.805 Y151.876 E.01844
G1 X159.446 Y152.304 E.0212
G1 X159.334 Y152.386 E.00527
G1 X159.334 Y156.181 E.1442
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
G1 X159.334 Y166.068 E.00527
G1 X159.334 Y169.864 E.1442
G1 X159.876 Y170.262 E.02552
G1 X160.197 Y170.689 E.02032
G1 X160.241 Y171.066 E.0144
G1 X160.466 Y171.066 E.00852
G1 X160.466 Y169.696 E.05204
; CHANGE_LAYER
; Z_HEIGHT: 6.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y171.066 E-.52052
G1 X160.241 Y171.066 E-.0852
G1 X160.197 Y170.689 E-.14402
G1 X160.181 Y170.668 E-.01026
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 27/107
; update layer progress
M73 L27
M991 S0 P26 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z6.6 I1.214 J.082 P1  F60000
G1 X161.126 Y156.593 Z6.6
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X161.126 Y163.407 E.25884
G1 X160.806 Y163.407 E.01216
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X161.067 Y156.593 E.00988
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2275.317
M204 S5000
M73 P60 R4
G1 X161.311 Y156.21 E.00425
G1 F2100
G1 X161.51 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X161.51 Y163.79 E.2663
M106 S0
G1 F2100
G1 X161.311 Y163.79 E.00699
G1 F2275.317
G1 X161.19 Y163.79 E.00425
G1 F2904.892
G1 X161.19 Y164.19 E.01405
G1 F3611.268
G1 X161.19 Y164.59 E.01405
G1 F4394.444
G1 X161.19 Y164.99 E.01405
G1 F5254.419
G1 X161.19 Y165.39 E.01405
G1 F6191.195
G1 X161.19 Y165.79 E.01405
G1 F7204.771
G1 X161.19 Y166.19 E.01405
G1 F8295.146
G1 X161.19 Y166.59 E.01405
G1 F9129
G1 X161.19 Y166.99 E.01405
G1 X161.19 Y167.39 E.01405
G1 X161.19 Y167.79 E.01405
G1 X161.19 Y171.79 E.14053
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.15 E.27895
; WIPE_START
G1 F12000
M204 S8000
G1 X161.311 Y156.21 E-.05132
G1 X161.51 Y156.21 E-.07562
G1 X161.51 Y157.876 E-.63306
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.757 Y163.037 Z6.84 F60000
G1 Z6.44
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.391504
G1 F12000
M204 S8000
M73 P60 R3
G1 X160.757 Y157.023 E.19497
; WIPE_START
G1 X160.757 Y159.023 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.406 Y151.398 Z6.84 F60000
G1 X160.292 Y148.934 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y148.934 E.03639
G1 X159.334 Y149.571 E.02417
G1 X159.511 Y149.738 E.00926
G1 X159.869 Y150.166 E.0212
G1 X160.024 Y150.594 E.01728
G1 X159.972 Y151.449 E.03255
G1 X159.815 Y151.876 E.01731
G1 X159.547 Y152.304 E.01917
G1 X159.334 Y152.506 E.01114
G1 X159.334 Y156.412 E.14838
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
G1 X159.334 Y166.188 E.01114
G1 X159.334 Y170.094 E.14838
G1 X159.511 Y170.262 E.00926
G1 X159.869 Y170.689 E.0212
G1 X160.006 Y171.066 E.01521
G1 X160.466 Y171.066 E.01747
G1 X160.466 Y169.931 E.04309
; CHANGE_LAYER
; Z_HEIGHT: 6.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y171.066 E-.43103
G1 X160.006 Y171.066 E-.17469
G1 X159.869 Y170.689 E-.15213
G1 X159.866 Y170.685 E-.00215
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 28/107
; update layer progress
M73 L28
M991 S0 P27 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z6.84 I1.207 J.156 P1  F60000
G1 X160.806 Y163.407 Z6.84
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X161.366 Y156.593 E.02128
G1 X161.366 Y163.407 E.25885
G1 X160.866 Y163.407 E.019
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9271
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y152.21 E.14053
G1 X161.19 Y152.61 E.01405
G1 X161.19 Y153.01 E.01405
G1 X161.19 Y153.41 E.01405
G1 F8986.236
G1 X161.19 Y153.81 E.01405
G1 F7849.78
G1 X161.19 Y154.21 E.01405
G1 F6790.124
G1 X161.19 Y154.61 E.01405
G1 F5807.269
G1 X161.19 Y155.01 E.01405
G1 F4901.213
G1 X161.19 Y155.41 E.01405
G1 F4071.958
G1 X161.19 Y155.81 E.01405
G1 F3319.502
G1 X161.19 Y156.21 E.01405
G1 F2643.846
G1 X161.551 Y156.21 E.01268
G1 F2100
G1 X161.75 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X161.75 Y163.79 E.2663
M106 S0
G1 F2100
G1 X161.551 Y163.79 E.00699
G1 F2549.122
G1 X161.25 Y163.79 E.01057
M204 S10000
G1 X160.917 Y162.957 F60000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551464
G1 F9000.721
M204 S8000
G1 X160.917 Y157.103 E.27907
; WIPE_START
G1 X160.917 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.247 Y151.5 Z7.08 F60000
G1 X160.021 Y148.934 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y148.934 E.02607
G1 X159.334 Y149.842 E.03449
G1 X159.622 Y150.166 E.01644
G1 X159.849 Y150.594 E.01839
G1 X159.943 Y151.021 E.01663
G1 X159.941 Y151.449 E.01624
G1 X159.852 Y151.876 E.01659
G1 X159.662 Y152.304 E.01778
G1 X159.334 Y152.738 E.02067
G1 X159.334 Y156.683 E.14988
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
G1 X159.334 Y166.42 E.02067
G1 X159.334 Y170.365 E.14988
G1 X159.622 Y170.689 E.01644
G1 X159.822 Y171.066 E.01619
G1 X160.466 Y171.066 E.02447
G1 X160.466 Y170.116 E.03609
; CHANGE_LAYER
; Z_HEIGHT: 6.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y171.066 E-.361
G1 X159.822 Y171.066 E-.24472
G1 X159.631 Y170.707 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 29/107
; update layer progress
M73 L29
M991 S0 P28 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z7.08 I1.201 J.193 P1  F60000
G1 X160.806 Y163.407 Z7.08
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X161.606 Y156.593 E.03039
G1 X161.606 Y163.407 E.25885
G1 X160.866 Y163.407 E.02811
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9421
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y152.61 E.15458
G1 X161.19 Y153.01 E.01405
G1 X161.19 Y153.41 E.01405
G1 X161.19 Y153.81 E.01405
G1 F8522.438
G1 X161.19 Y154.21 E.01405
G1 F7416.702
G1 X161.19 Y154.61 E.01405
G1 F6387.766
G1 X161.19 Y155.01 E.01405
G1 F5435.631
G1 X161.19 Y155.41 E.01405
G1 F4560.295
G1 X161.19 Y155.81 E.01405
G1 F3761.759
G1 X161.19 Y156.21 E.01405
G1 F3040.024
G1 X161.391 Y156.21 E.00706
G1 F2706.344
G1 X161.791 Y156.21 E.01405
G1 F2100
G1 X161.99 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X161.99 Y163.79 E.2663
M106 S0
G1 F2100
G1 X161.791 Y163.79 E.00699
G1 F2938.387
G1 X161.25 Y163.79 E.01901
M204 S10000
G1 X161.157 Y162.957 F60000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551464
G1 F9000.721
M204 S8000
G1 X161.157 Y157.103 E.27907
; WIPE_START
G1 X161.157 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.13 Y151.54 Z7.32 F60000
G1 X159.776 Y148.934 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y148.934 E.01677
G1 X159.334 Y150.087 E.04379
G1 X159.41 Y150.166 E.00416
G1 X159.705 Y150.594 E.01974
G1 X159.871 Y151.021 E.01742
G1 X159.936 Y151.449 E.01643
G1 X159.915 Y151.876 E.01626
G1 X159.797 Y152.304 E.01686
G1 X159.547 Y152.731 E.01882
G1 X159.334 Y152.965 E.012
G1 X159.334 Y156.928 E.15056
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
G1 X159.547 Y166.414 E.01882
G1 X159.334 Y166.647 E.012
G1 X159.334 Y170.61 E.15056
G1 X159.41 Y170.689 E.00416
G1 X159.67 Y171.066 E.01738
G1 X160.466 Y171.066 E.03022
G1 X160.466 Y170.267 E.03034
; CHANGE_LAYER
; Z_HEIGHT: 7.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X160.466 Y171.066 E-.30342
G1 X159.67 Y171.066 E-.3023
G1 X159.439 Y170.731 E-.15428
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 30/107
; update layer progress
M73 L30
M991 S0 P29 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z7.32 I1.196 J.223 P1  F60000
G1 X160.806 Y163.407 Z7.32
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X161.846 Y156.593 E.03951
M73 P61 R3
G1 X161.846 Y163.407 E.25885
G1 X160.866 Y163.407 E.03723
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9570
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y152.61 E.15458
G1 X161.19 Y153.01 E.01405
G1 X161.19 Y153.41 E.01405
G1 X161.19 Y153.81 E.01405
G1 F9222.743
G1 X161.19 Y154.21 E.01405
G1 F8070.927
G1 X161.19 Y154.61 E.01405
G1 F6995.912
G1 X161.19 Y155.01 E.01405
G1 F5997.696
G1 X161.19 Y155.41 E.01405
G1 F5076.28
G1 X161.19 Y155.81 E.01405
G1 F4231.665
G1 X161.19 Y156.21 E.01405
G1 F3463.849
G1 X161.631 Y156.21 E.01549
G1 F2706.344
G1 X162.031 Y156.21 E.01405
G1 F2100
G1 X162.23 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X162.23 Y163.79 E.2663
M106 S0
G1 F2100
G1 X162.031 Y163.79 E.00699
G1 F2706.344
G1 X161.631 Y163.79 E.01405
G1 F3355.301
G1 X161.25 Y163.79 E.01339
M204 S10000
G1 X161.397 Y162.957 F60000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551464
G1 F9000.721
M204 S8000
G1 X161.397 Y157.103 E.27907
; WIPE_START
G1 X161.397 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.015 Y151.597 Z7.56 F60000
G1 X159.524 Y148.934 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y148.934 E.00721
G1 X159.334 Y150.339 E.05335
G1 X159.584 Y150.594 E.01356
G1 X159.825 Y151.021 E.01863
G1 X159.958 Y151.449 E.01702
G1 X160.006 Y151.876 E.01634
G1 X159.96 Y152.304 E.01634
G1 X159.778 Y152.731 E.01765
G1 X159.334 Y153.239 E.02563
G1 X159.334 Y157.18 E.14971
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
G1 X159.778 Y166.414 E.01765
G1 X159.334 Y166.921 E.02563
G1 X159.334 Y168.515 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 7.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y166.921 E-.60571
G1 X159.602 Y166.616 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 31/107
; update layer progress
M73 L31
M991 S0 P30 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z7.56 I1.139 J.428 P1  F60000
G1 X160.806 Y163.407 Z7.56
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X162.086 Y156.593 E.04863
G1 X162.086 Y163.407 E.25885
G1 X160.866 Y163.407 E.04635
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9714
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y153.01 E.16864
G1 X161.19 Y153.41 E.01405
G1 X161.19 Y153.81 E.01405
G1 X161.19 Y154.21 E.01405
G1 F8752.801
G1 X161.19 Y154.61 E.01405
G1 F7631.705
G1 X161.19 Y155.01 E.01405
G1 F6587.409
G1 X161.19 Y155.41 E.01405
G1 F5619.914
G1 X161.19 Y155.81 E.01405
G1 F4729.218
G1 X161.19 Y156.21 E.01405
G1 F3915.322
G1 X161.471 Y156.21 E.00987
G1 F3389.487
G1 X161.871 Y156.21 E.01405
G1 F2706.344
G1 X162.271 Y156.21 E.01405
G1 F2100
G1 X162.47 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X162.47 Y163.79 E.2663
M106 S0
G1 F2100
G1 X162.271 Y163.79 E.00699
G1 F2706.344
G1 X161.871 Y163.79 E.01405
G1 F3389.487
G1 X161.471 Y163.79 E.01405
G1 F3799.862
G1 X161.25 Y163.79 E.00776
M204 S10000
G1 X161.637 Y162.957 F60000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551464
G1 F9000.721
M204 S8000
G1 X161.637 Y157.103 E.27907
; WIPE_START
G1 X161.637 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.988 Y151.651 Z7.8 F60000
G1 X159.387 Y148.934 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y148.934 E.002
G1 X159.334 Y150.476 E.05856
G1 X159.479 Y150.594 E.00709
G1 X159.805 Y151.021 E.02042
G1 X160.01 Y151.449 E.01801
G1 X160.165 Y152.304 E.03302
G1 X160.071 Y152.731 E.01662
G1 X159.732 Y153.159 E.02075
G1 X159.334 Y153.482 E.01945
G1 X159.334 Y157.317 E.1457
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
G1 X160.071 Y166.414 E.01663
G1 X159.732 Y166.841 E.02075
G1 X159.334 Y167.164 E.01945
G1 X159.334 Y168.758 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 7.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.164 E-.60571
G1 X159.649 Y166.908 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 32/107
; update layer progress
M73 L32
M991 S0 P31 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z7.8 I1.156 J.382 P1  F60000
G1 X160.806 Y163.407 Z7.8
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X162.327 Y156.593 E.05775
G1 X162.327 Y163.407 E.25885
G1 X160.866 Y163.407 E.05547
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9852
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y153.41 E.18269
G1 X161.19 Y153.81 E.01405
G1 X161.19 Y154.21 E.01405
G1 F9462.322
G1 X161.19 Y154.61 E.01405
G1 F8295.146
G1 X161.19 Y155.01 E.01405
G1 F7204.771
G1 X161.19 Y155.41 E.01405
G1 F6191.195
G1 X161.19 Y155.81 E.01405
G1 F5254.419
G1 X161.19 Y156.21 E.01405
G1 F4394.444
G1 X161.711 Y156.21 E.0183
G1 F3389.487
G1 X162.111 Y156.21 E.01405
G1 F2706.344
G1 X162.511 Y156.21 E.01405
G1 F2100
G1 X162.71 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X162.71 Y163.79 E.2663
M106 S0
G1 F2100
G1 X162.511 Y163.79 E.00699
G1 F2706.344
G1 X162.111 Y163.79 E.01405
G1 F3389.487
G1 X161.711 Y163.79 E.01405
G1 F4272.071
G1 X161.25 Y163.79 E.0162
M204 S10000
G1 X161.335 Y163.066 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X161.428 Y163.066 E.00354
G1 X161.428 Y161.565 E.05702
G1 X161.149 Y160.855 E.02897
G1 X161.074 Y160.428 E.01649
G1 X161.276 Y160 E.01797
G1 X161.428 Y159.922 E.00648
G1 X161.428 Y158.328 E.06056
; WIPE_START
G1 X161.428 Y159.922 E-.60571
G1 X161.276 Y160 E-.06479
G1 X161.176 Y160.213 E-.0895
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.877 Y162.957 Z8.04 F60000
G1 Z7.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551484
G1 F9000.361
M204 S8000
G1 X161.877 Y157.103 E.27908
; WIPE_START
G1 X161.877 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.02 Y151.7 Z8.04 F60000
G1 X159.334 Y148.968 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y150.562 E.06056
G1 X159.385 Y150.594 E.00227
G1 X159.815 Y151.021 E.02304
G1 X160.094 Y151.449 E.0194
G1 X160.431 Y152.304 E.03491
G1 X160.466 Y152.503 E.00768
G1 X160.466 Y152.816 E.0119
G1 X160.303 Y153.159 E.01441
G1 X159.334 Y153.67 E.0416
G1 X159.334 Y157.403 E.14186
G1 X159.385 Y157.435 E.00227
G1 X159.815 Y157.862 E.02304
G1 X160.094 Y158.29 E.0194
G1 X160.431 Y159.145 E.03491
G1 X160.506 Y159.572 E.01649
G1 X160.303 Y160 E.01797
G1 X159.334 Y160.511 E.0416
G1 X159.334 Y164.244 E.14186
G1 X159.385 Y164.276 E.00227
G1 X159.815 Y164.703 E.02304
G1 X160.094 Y165.131 E.0194
G1 X160.431 Y165.986 E.03491
G1 X160.466 Y166.185 E.00768
G1 X160.466 Y166.498 E.0119
G1 X160.303 Y166.841 E.01441
G1 X159.334 Y167.352 E.0416
G1 X159.334 Y168.946 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 7.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.352 E-.60571
G1 X159.694 Y167.162 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 33/107
; update layer progress
M73 L33
M991 S0 P32 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z8.04 I1.167 J.346 P1  F60000
G1 X160.806 Y163.407 Z8.04
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
M73 P62 R3
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X162.567 Y156.593 E.06687
G1 X162.567 Y163.407 E.25885
G1 X160.866 Y163.407 E.06459
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9982
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y153.41 E.18269
G1 X161.19 Y153.81 E.01405
G1 X161.19 Y154.21 E.01405
G1 X161.19 Y154.61 E.01405
G1 F8986.236
G1 X161.19 Y155.01 E.01405
G1 F7849.78
G1 X161.19 Y155.41 E.01405
G1 F6790.124
G1 X161.19 Y155.81 E.01405
G1 F5807.269
G1 X161.19 Y156.21 E.01405
G1 F4901.213
G1 X161.551 Y156.21 E.01268
G1 F4149.431
G1 X161.951 Y156.21 E.01405
G1 F3389.487
G1 X162.351 Y156.21 E.01405
G1 F2706.344
G1 X162.751 Y156.21 E.01405
G1 F2100
G1 X162.95 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X162.95 Y163.79 E.2663
M106 S0
G1 F2100
G1 X162.751 Y163.79 E.00699
G1 F2706.344
G1 X162.351 Y163.79 E.01405
G1 F3389.487
G1 X161.951 Y163.79 E.01405
G1 F4149.431
G1 X161.551 Y163.79 E.01405
G1 F4771.929
G1 X161.25 Y163.79 E.01057
; WIPE_START
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.117 Y162.957 Z8.28 F60000
G1 Z7.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551484
G1 F9000.361
M204 S8000
G1 X162.117 Y157.103 E.27908
; WIPE_START
G1 X162.117 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.084 Y151.746 Z8.28 F60000
G1 X159.334 Y149.032 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y150.626 E.06056
G1 X159.507 Y150.723 E.00751
G1 X159.935 Y151.094 E.02152
G1 X160.466 Y151.847 E.03499
G1 X160.466 Y153.776 E.0733
G1 X160.362 Y153.701 E.00485
G1 X159.935 Y153.669 E.01629
G1 X159.334 Y153.834 E.02365
G1 X159.334 Y157.467 E.13803
G1 X159.507 Y157.564 E.00751
G1 X159.935 Y157.935 E.02152
G1 X160.79 Y159.147 E.05636
G1 X161.14 Y159.43 E.01711
G1 X161.491 Y159.497 E.01355
G1 X161.668 Y159.465 E.00684
G1 X161.668 Y162.073 E.09906
G1 X161.491 Y161.885 E.00982
G1 X160.79 Y160.853 E.0474
G1 X160.362 Y160.542 E.02008
G1 X159.935 Y160.51 E.01629
G1 X159.334 Y160.675 E.02365
G1 X159.334 Y164.308 E.13803
G1 X159.507 Y164.405 E.00751
G1 X159.935 Y164.776 E.02152
G1 X160.466 Y165.529 E.03499
G1 X160.466 Y167.458 E.0733
G1 X160.362 Y167.383 E.00485
G1 X159.935 Y167.351 E.01629
G1 X159.334 Y167.516 E.02365
G1 X159.334 Y169.11 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 8.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.516 E-.60571
G1 X159.726 Y167.408 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 34/107
; update layer progress
M73 L34
M991 S0 P33 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z8.28 I1.175 J.317 P1  F60000
G1 X160.806 Y163.407 Z8.28
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X162.807 Y156.593 E.07599
G1 X162.807 Y163.407 E.25885
G1 X160.866 Y163.407 E.07371
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10105
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y153.81 E.19674
G1 X161.19 Y154.21 E.01405
G1 X161.19 Y154.61 E.01405
G1 F9704.973
G1 X161.19 Y155.01 E.01405
G1 F8522.438
G1 X161.19 Y155.41 E.01405
G1 F7416.702
G1 X161.19 Y155.81 E.01405
G1 F6387.766
G1 X161.19 Y156.21 E.01405
G1 F5435.631
G1 X161.391 Y156.21 E.00706
G1 F4986.175
G1 X161.791 Y156.21 E.01405
G1 F4149.431
G1 X162.191 Y156.21 E.01405
G1 F3389.487
G1 X162.591 Y156.21 E.01405
G1 F2706.344
G1 X162.991 Y156.21 E.01405
G1 F2100
G1 X163.19 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X163.19 Y163.79 E.2663
M106 S0
G1 F2100
G1 X162.991 Y163.79 E.00699
G1 F2706.344
G1 X162.591 Y163.79 E.01405
G1 F3389.487
G1 X162.191 Y163.79 E.01405
G1 F4149.431
G1 X161.791 Y163.79 E.01405
G1 F5299.434
G1 X161.25 Y163.79 E.01901
; WIPE_START
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.357 Y162.957 Z8.52 F60000
G1 Z8.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551504
G1 F9000
M204 S8000
G1 X162.357 Y157.103 E.27909
; WIPE_START
G1 X162.357 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.158 Y151.794 Z8.52 F60000
G1 X159.334 Y149.055 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y150.649 E.06056
G1 X159.507 Y150.716 E.00704
G1 X159.935 Y150.995 E.01939
G1 X160.466 Y151.568 E.02969
G1 X160.466 Y154.13 E.09732
G1 X160.362 Y154.044 E.00511
G1 X159.935 Y153.899 E.01715
G1 X159.334 Y153.949 E.02288
G1 X159.334 Y157.49 E.13453
G1 X159.507 Y157.557 E.00704
G1 X159.935 Y157.836 E.01939
G1 X160.79 Y158.76 E.04783
G1 X161.14 Y159.068 E.01775
G1 X161.491 Y159.227 E.01462
G1 X161.908 Y159.244 E.01587
G1 X161.908 Y162.309 E.11645
G1 X161.491 Y162.029 E.01909
G1 X160.79 Y161.24 E.04008
G1 X160.362 Y160.885 E.02113
G1 X159.935 Y160.74 E.01715
G1 X159.334 Y160.79 E.02288
G1 X159.334 Y164.331 E.13453
G1 X159.507 Y164.398 E.00704
G1 X159.935 Y164.677 E.01939
G1 X160.466 Y165.25 E.02969
G1 X160.466 Y167.812 E.09732
G1 X160.362 Y167.726 E.00511
G1 X159.935 Y167.581 E.01715
G1 X159.334 Y167.631 E.02288
G1 X159.334 Y169.225 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 8.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.631 E-.60571
G1 X159.739 Y167.598 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 35/107
; update layer progress
M73 L35
M991 S0 P34 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z8.52 I1.179 J.3 P1  F60000
G1 X160.806 Y163.407 Z8.52
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X163.047 Y156.593 E.0851
G1 X163.047 Y163.407 E.25885
G1 X160.866 Y163.407 E.08283
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10219
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y153.81 E.19674
G1 X161.19 Y154.21 E.01405
G1 X161.19 Y154.61 E.01405
G1 X161.19 Y155.01 E.01405
G1 F9222.743
G1 X161.19 Y155.41 E.01405
G1 F8070.927
G1 X161.19 Y155.81 E.01405
G1 F6995.912
G1 X161.19 Y156.21 E.01405
G1 F5997.696
G1 X161.631 Y156.21 E.01549
G1 F4986.175
G1 X162.031 Y156.21 E.01405
G1 F4149.431
G1 X162.431 Y156.21 E.01405
G1 F3389.487
G1 X162.831 Y156.21 E.01405
G1 F2706.344
G1 X163.231 Y156.21 E.01405
G1 F2100
G1 X163.43 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X163.43 Y163.79 E.2663
M106 S0
G1 F2100
G1 X163.231 Y163.79 E.00699
G1 F2706.344
G1 X162.831 Y163.79 E.01405
G1 F3389.487
G1 X162.431 Y163.79 E.01405
G1 F4149.431
G1 X162.031 Y163.79 E.01405
G1 F4986.175
G1 X161.631 Y163.79 E.01405
G1 F5854.588
G1 X161.25 Y163.79 E.01339
; WIPE_START
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.597 Y162.957 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551484
G1 F9000.361
M204 S8000
G1 X162.597 Y157.103 E.27908
; WIPE_START
M73 P63 R3
G1 X162.597 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.241 Y151.843 Z8.76 F60000
G1 X159.334 Y149.049 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y150.643 E.06056
G1 X159.507 Y150.682 E.00673
G1 X159.935 Y150.882 E.01793
G1 X160.362 Y151.212 E.02053
G1 X160.466 Y151.316 E.00557
G1 X160.466 Y154.39 E.11676
G1 X160.362 Y154.299 E.00523
G1 X159.935 Y154.08 E.01824
G1 X159.507 Y153.995 E.01656
G1 X159.334 Y153.999 E.00656
G1 X159.334 Y157.484 E.1324
G1 X159.507 Y157.523 E.00673
G1 X159.935 Y157.723 E.01793
G1 X160.362 Y158.053 E.02053
G1 X160.79 Y158.484 E.02306
G1 X161.491 Y159.018 E.03348
G1 X162.148 Y159.16 E.02555
G1 X162.148 Y162.492 E.12657
G1 X161.491 Y162.174 E.02774
G1 X160.362 Y161.14 E.05816
G1 X159.935 Y160.921 E.01824
G1 X159.507 Y160.836 E.01656
G1 X159.334 Y160.84 E.00656
G1 X159.334 Y164.325 E.1324
G1 X159.507 Y164.364 E.00673
G1 X159.935 Y164.564 E.01793
G1 X160.362 Y164.894 E.02053
G1 X160.466 Y164.998 E.00557
G1 X160.466 Y168.072 E.11676
G1 X160.362 Y167.981 E.00523
G1 X159.935 Y167.762 E.01824
G1 X159.507 Y167.677 E.01656
G1 X159.334 Y167.681 E.00656
G1 X159.334 Y169.275 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 8.6
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.681 E-.60571
G1 X159.507 Y167.677 E-.06562
G1 X159.736 Y167.722 E-.08867
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 36/107
; update layer progress
M73 L36
M991 S0 P35 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z8.76 I1.181 J.293 P1  F60000
G1 X160.806 Y163.407 Z8.76
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X163.287 Y156.593 E.09422
G1 X163.287 Y163.407 E.25885
G1 X160.866 Y163.407 E.09194
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10326
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y154.21 E.21079
G1 X161.19 Y154.61 E.01405
G1 X161.19 Y155.01 E.01405
G1 F9950.696
G1 X161.19 Y155.41 E.01405
G1 F8752.801
G1 X161.19 Y155.81 E.01405
G1 F7631.705
G1 X161.19 Y156.21 E.01405
G1 F6587.409
G1 X161.471 Y156.21 E.00987
G1 F5899.718
G1 X161.871 Y156.21 E.01405
G1 F4986.175
G1 X162.271 Y156.21 E.01405
G1 F4149.431
G1 X162.671 Y156.21 E.01405
G1 F3389.487
G1 X163.071 Y156.21 E.01405
G1 F2706.344
G1 X163.471 Y156.21 E.01405
G1 F2100
G1 X163.67 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X163.67 Y163.79 E.2663
M106 S0
G1 F2100
G1 X163.471 Y163.79 E.00699
G1 F2706.344
G1 X163.071 Y163.79 E.01405
G1 F3389.487
G1 X162.671 Y163.79 E.01405
G1 F4149.431
G1 X162.271 Y163.79 E.01405
G1 F4986.175
G1 X161.871 Y163.79 E.01405
G1 F5899.718
G1 X161.471 Y163.79 E.01405
G1 F6437.389
G1 X161.25 Y163.79 E.00776
; WIPE_START
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.837 Y162.957 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X162.837 Y157.103 E.27906
; WIPE_START
G1 X162.837 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.333 Y151.893 Z9 F60000
G1 X159.334 Y149.017 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y150.611 E.06056
G1 X159.507 Y150.622 E.00657
G1 X159.935 Y150.75 E.01695
G1 X160.362 Y151.008 E.01898
G1 X160.466 Y151.103 E.00532
G1 X160.466 Y154.611 E.13327
G1 X160.362 Y154.513 E.00541
G1 X159.935 Y154.227 E.01955
G1 X159.507 Y154.07 E.0173
G1 X159.334 Y154.047 E.00662
G1 X159.334 Y157.452 E.12933
G1 X159.507 Y157.463 E.00657
G1 X159.935 Y157.591 E.01695
G1 X160.362 Y157.849 E.01898
G1 X161.217 Y158.646 E.0444
G1 X161.645 Y158.932 E.01955
G1 X162.072 Y159.089 E.0173
G1 X162.388 Y159.131 E.0121
G1 X162.388 Y162.558 E.13023
G1 X162.072 Y162.537 E.01202
G1 X161.645 Y162.409 E.01695
G1 X161.217 Y162.151 E.01898
G1 X160.362 Y161.354 E.0444
G1 X159.935 Y161.068 E.01955
G1 X159.507 Y160.911 E.0173
G1 X159.334 Y160.888 E.00662
G1 X159.334 Y164.293 E.12933
G1 X159.507 Y164.305 E.00657
G1 X159.935 Y164.432 E.01695
G1 X160.362 Y164.69 E.01898
G1 X160.466 Y164.785 E.00532
G1 X160.466 Y168.293 E.13327
G1 X160.362 Y168.195 E.00541
G1 X159.935 Y167.909 E.01955
G1 X159.507 Y167.752 E.0173
G1 X159.334 Y167.73 E.00662
G1 X159.334 Y169.324 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 8.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.73 E-.60571
G1 X159.507 Y167.752 E-.06618
G1 X159.725 Y167.832 E-.08811
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 37/107
; update layer progress
M73 L37
M991 S0 P36 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9 I1.182 J.289 P1  F60000
G1 X160.806 Y163.407 Z9
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X163.527 Y156.593 E.10334
G1 X163.527 Y163.407 E.25885
G1 X160.866 Y163.407 E.10106
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10425
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y154.61 E.22485
G1 X161.19 Y155.01 E.01405
G1 X161.19 Y155.41 E.01405
G1 F9462.322
G1 X161.19 Y155.81 E.01405
G1 F8295.146
G1 X161.19 Y156.21 E.01405
G1 F7204.771
G1 X161.711 Y156.21 E.0183
G1 F5899.718
G1 X162.111 Y156.21 E.01405
G1 F4986.175
G1 X162.511 Y156.21 E.01405
G1 F4149.431
G1 X162.911 Y156.21 E.01405
G1 F3389.487
G1 X163.311 Y156.21 E.01405
G1 F2706.344
G1 X163.711 Y156.21 E.01405
G1 F2100
G1 X163.91 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X163.91 Y163.79 E.2663
M106 S0
G1 F2100
G1 X163.711 Y163.79 E.00699
G1 F2706.344
G1 X163.311 Y163.79 E.01405
G1 F3389.487
G1 X162.911 Y163.79 E.01405
G1 F4149.431
G1 X162.511 Y163.79 E.01405
G1 F4986.175
G1 X162.111 Y163.79 E.01405
G1 F5899.718
G1 X161.711 Y163.79 E.01405
G1 F7047.838
G1 X161.25 Y163.79 E.0162
; WIPE_START
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.077 Y162.957 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551464
G1 F9000.721
M204 S8000
G1 X163.077 Y157.103 E.27907
; WIPE_START
G1 X163.077 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.436 Y151.942 Z9.24 F60000
G1 X159.334 Y148.957 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y150.551 E.06056
G1 X159.507 Y150.536 E.00659
G1 X159.935 Y150.591 E.01638
G1 X160.362 Y150.781 E.01778
G1 X160.466 Y150.87 E.00518
G1 X160.466 Y154.858 E.15151
G1 X159.935 Y154.35 E.02792
G1 X159.507 Y154.12 E.01845
G1 X159.334 Y154.069 E.00683
G1 X159.334 Y157.392 E.12625
G1 X159.507 Y157.377 E.00659
G1 X159.935 Y157.432 E.01638
G1 X160.362 Y157.622 E.01778
G1 X160.79 Y157.99 E.02143
G1 X161.645 Y158.809 E.04497
G1 X162.072 Y159.039 E.01845
G1 X162.5 Y159.164 E.01692
G1 X162.628 Y159.176 E.00489
G1 X162.628 Y162.547 E.12809
G1 X162.5 Y162.585 E.00507
G1 X162.072 Y162.624 E.01631
G1 X161.645 Y162.568 E.01638
G1 X161.217 Y162.378 E.01778
G1 X160.79 Y162.01 E.02143
G1 X159.935 Y161.191 E.04497
G1 X159.507 Y160.961 E.01845
G1 X159.334 Y160.91 E.00683
G1 X159.334 Y164.233 E.12625
G1 X159.507 Y164.218 E.00659
G1 X159.935 Y164.273 E.01638
G1 X160.362 Y164.464 E.01778
G1 X160.466 Y164.552 E.00518
G1 X160.466 Y168.54 E.15151
G1 X159.935 Y168.032 E.02792
G1 X159.507 Y167.802 E.01845
G1 X159.334 Y167.751 E.00683
G1 X159.334 Y169.345 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 9.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y167.751 E-.60571
G1 X159.507 Y167.802 E-.06834
G1 X159.706 Y167.909 E-.08594
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 38/107
; update layer progress
M73 L38
M991 S0 P37 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9.24 I1.182 J.289 P1  F60000
G1 X160.806 Y163.407 Z9.24
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X163.767 Y156.593 E.11246
G1 X163.767 Y163.407 E.25885
G1 X160.866 Y163.407 E.11018
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10515
M204 S5000
M73 P64 R3
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y154.61 E.22485
G1 X161.19 Y155.01 E.01405
G1 X161.19 Y155.41 E.01405
G1 F10199.491
G1 X161.19 Y155.81 E.01405
G1 F8986.236
G1 X161.19 Y156.21 E.01405
G1 F7849.78
G1 X161.551 Y156.21 E.01268
G1 F6890.062
G1 X161.951 Y156.21 E.01405
G1 F5899.718
G1 X162.351 Y156.21 E.01405
G1 F4986.175
G1 X162.751 Y156.21 E.01405
G1 F4149.431
G1 X163.151 Y156.21 E.01405
G1 F3389.487
G1 X163.551 Y156.21 E.01405
G1 F2706.344
G1 X163.951 Y156.21 E.01405
G1 F2100
G1 X164.15 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X164.15 Y163.79 E.2663
M106 S0
G1 F2100
G1 X163.951 Y163.79 E.00699
G1 F2706.344
G1 X163.551 Y163.79 E.01405
G1 F3389.487
G1 X163.151 Y163.79 E.01405
G1 F4149.431
G1 X162.751 Y163.79 E.01405
G1 F4986.175
G1 X162.351 Y163.79 E.01405
G1 F5899.718
G1 X161.951 Y163.79 E.01405
G1 F6890.062
G1 X161.551 Y163.79 E.01405
G1 F7685.936
G1 X161.25 Y163.79 E.01057
; WIPE_START
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y165.858 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y164.264 E.06056
G1 X160.362 Y164.181 E.00504
G1 X159.935 Y164.074 E.01674
G1 X159.334 Y164.169 E.02308
G1 X159.334 Y160.905 E.124
G1 X159.507 Y160.984 E.00721
G1 X159.935 Y161.298 E.02015
G1 X160.79 Y162.316 E.0505
G1 X161.217 Y162.66 E.02086
G1 X161.645 Y162.767 E.01674
G1 X162.5 Y162.632 E.03289
G1 X162.868 Y162.464 E.01538
G1 X162.868 Y159.27 E.12136
G1 X162.5 Y159.212 E.01416
G1 X162.072 Y159.016 E.01786
G1 X161.645 Y158.702 E.02015
G1 X160.79 Y157.685 E.0505
G1 X160.362 Y157.34 E.02086
G1 X159.935 Y157.233 E.01674
G1 X159.334 Y157.328 E.02308
G1 X159.334 Y154.064 E.124
G1 X159.507 Y154.143 E.00721
G1 X159.935 Y154.457 E.02015
G1 X160.466 Y155.089 E.03135
G1 X160.466 Y150.582 E.17121
G1 X160.362 Y150.499 E.00504
G1 X159.935 Y150.392 E.01674
G1 X159.334 Y150.487 E.02308
G1 X159.334 Y148.934 E.05898
G1 X159.376 Y148.934 E.00158
; WIPE_START
G1 X159.334 Y148.934 E-.01581
G1 X159.334 Y150.487 E-.58991
G1 X159.736 Y150.424 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.833 Y157.762 Z9.48 F60000
G1 X163.317 Y162.957 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X163.317 Y157.103 E.27906
; WIPE_START
G1 X163.317 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.563 Y165.748 Z9.48 F60000
G1 X159.334 Y166.152 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.746 E.06056
G1 X159.507 Y167.825 E.00721
G1 X159.935 Y168.139 E.02015
G1 X160.466 Y168.771 E.03135
G1 X160.466 Y171.066 E.08718
G1 X160.417 Y171.066 E.00184
G1 X160.362 Y171.022 E.00266
G1 X159.935 Y170.916 E.01674
G1 X159.334 Y171.01 E.02308
G1 X159.334 Y169.416 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 9.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y171.01 E-.60572
G1 X159.736 Y170.947 E-.15428
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 39/107
; update layer progress
M73 L39
M991 S0 P38 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9.48 I1.205 J.171 P1  F60000
G1 X160.806 Y163.407 Z9.48
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X164.007 Y156.593 E.12158
G1 X164.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.1193
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10597
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y155.01 E.2389
G1 X161.19 Y155.41 E.01405
G1 X161.19 Y155.81 E.01405
G1 F9704.973
G1 X161.19 Y156.21 E.01405
G1 F8522.438
G1 X161.391 Y156.21 E.00706
G1 F7957.206
G1 X161.791 Y156.21 E.01405
G1 F6890.062
G1 X162.191 Y156.21 E.01405
G1 F5899.718
G1 X162.591 Y156.21 E.01405
G1 F4986.175
G1 X162.991 Y156.21 E.01405
G1 F4149.431
G1 X163.391 Y156.21 E.01405
G1 F3389.487
G1 X163.791 Y156.21 E.01405
G1 F2706.344
G1 X164.191 Y156.21 E.01405
G1 F2100
G1 X164.39 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X164.39 Y163.79 E.2663
M106 S0
G1 F2100
G1 X164.191 Y163.79 E.00699
G1 F2706.344
G1 X163.791 Y163.79 E.01405
G1 F3389.487
G1 X163.391 Y163.79 E.01405
G1 F4149.431
G1 X162.991 Y163.79 E.01405
G1 F4986.175
G1 X162.591 Y163.79 E.01405
G1 F5899.718
G1 X162.191 Y163.79 E.01405
G1 F6890.062
G1 X161.791 Y163.79 E.01405
G1 F8351.681
G1 X161.25 Y163.79 E.01901
; WIPE_START
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y165.427 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y163.833 E.06056
G1 X160.362 Y163.774 E.00453
G1 X159.935 Y163.818 E.01633
G1 X159.334 Y164.036 E.02427
G1 X159.334 Y160.869 E.12033
G1 X159.507 Y160.978 E.00775
G1 X159.935 Y161.393 E.02265
G1 X160.362 Y162.053 E.02987
G1 X160.79 Y162.822 E.03343
G1 X161.214 Y163.066 E.01858
G1 X161.645 Y163.024 E.01646
G1 X162.5 Y162.712 E.03457
G1 X162.928 Y162.443 E.0192
G1 X163.108 Y162.268 E.00956
G1 X163.108 Y159.513 E.10465
G1 X162.5 Y159.292 E.02458
G1 X162.072 Y159.022 E.0192
G1 X161.645 Y158.607 E.02265
G1 X161.217 Y157.947 E.02987
G1 X160.79 Y157.178 E.03343
G1 X160.362 Y156.933 E.01873
G1 X159.935 Y156.977 E.01633
G1 X159.334 Y157.195 E.02427
G1 X159.334 Y154.028 E.12033
G1 X159.507 Y154.137 E.00775
G1 X159.935 Y154.552 E.02265
G1 X160.466 Y155.398 E.03793
G1 X160.466 Y150.151 E.19934
G1 X160.362 Y150.091 E.00453
G1 X159.935 Y150.135 E.01633
G1 X159.334 Y150.354 E.02427
G1 X159.334 Y148.934 E.05393
G1 X159.509 Y148.934 E.00663
; WIPE_START
G1 X159.334 Y148.934 E-.0663
G1 X159.334 Y150.354 E-.53941
G1 X159.716 Y150.215 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.919 Y157.523 Z9.72 F60000
G1 X163.557 Y162.957 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X163.557 Y157.103 E.27906
; WIPE_START
G1 X163.557 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.62 Y165.641 Z9.72 F60000
G1 X159.334 Y166.116 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.71 E.06056
G1 X159.507 Y167.819 E.00775
G1 X159.935 Y168.234 E.02265
G1 X160.466 Y169.08 E.03793
G1 X160.466 Y170.674 E.06057
G1 X160.362 Y170.615 E.00453
G1 X159.935 Y170.659 E.01633
G1 X159.334 Y170.877 E.02427
G1 X159.334 Y169.283 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 9.56
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F11292.473
G1 X159.334 Y170.877 E-.60572
G1 X159.716 Y170.738 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 40/107
; update layer progress
M73 L40
M991 S0 P39 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9.72 I1.204 J.179 P1  F60000
G1 X160.806 Y163.407 Z9.72
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X164.247 Y156.593 E.1307
G1 X164.247 Y163.407 E.25885
G1 X160.866 Y163.407 E.12842
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10670
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y155.01 E.2389
G1 X161.19 Y155.41 E.01405
G1 X161.19 Y155.81 E.01405
G1 F10451.359
G1 X161.19 Y156.21 E.01405
G1 F9222.743
G1 X161.631 Y156.21 E.01549
G1 F7957.206
G1 X162.031 Y156.21 E.01405
G1 F6890.062
G1 X162.431 Y156.21 E.01405
G1 F5899.718
G1 X162.831 Y156.21 E.01405
G1 F4986.175
G1 X163.231 Y156.21 E.01405
G1 F4149.431
G1 X163.631 Y156.21 E.01405
G1 F3389.487
G1 X164.031 Y156.21 E.01405
G1 F2706.344
G1 X164.431 Y156.21 E.01405
G1 F2100
G1 X164.63 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X164.63 Y163.79 E.2663
M106 S0
G1 F2100
G1 X164.431 Y163.79 E.00699
G1 F2706.344
M73 P65 R3
G1 X164.031 Y163.79 E.01405
G1 F3389.487
G1 X163.631 Y163.79 E.01405
G1 F4149.431
G1 X163.231 Y163.79 E.01405
G1 F4986.175
G1 X162.831 Y163.79 E.01405
G1 F5899.718
G1 X162.431 Y163.79 E.01405
G1 F6890.062
G1 X162.031 Y163.79 E.01405
G1 F7957.206
G1 X161.631 Y163.79 E.01405
G1 F9045.075
G1 X161.25 Y163.79 E.01339
; WIPE_START
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.348 Y162.719 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X163.348 Y163.066 E.01318
G1 X162.101 Y163.066 E.04738
G1 X162.843 Y162.565 E.03399
G1 X163.228 Y162.138 E.02185
G1 X163.348 Y161.93 E.00912
G1 X163.348 Y159.948 E.07532
G1 X162.157 Y159.145 E.05457
G1 X161.773 Y158.717 E.02185
G1 X161.524 Y158.29 E.01879
G1 X161.266 Y157.435 E.03394
G1 X161.277 Y157.007 E.01625
G1 X161.328 Y156.934 E.00336
G1 X162.922 Y156.934 E.06056
; WIPE_START
G1 X161.328 Y156.934 E-.60571
G1 X161.277 Y157.007 E-.03363
G1 X161.269 Y157.325 E-.12066
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.797 Y162.957 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X163.797 Y157.103 E.27906
; WIPE_START
G1 X163.797 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.075 Y151.972 Z9.96 F60000
G1 X160.466 Y150.375 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y148.934 E.05474
G1 X160.312 Y148.934 E.00582
G1 X160.302 Y149.311 E.01431
G1 X160.005 Y149.738 E.01978
G1 X159.334 Y150.191 E.03073
G1 X159.334 Y153.955 E.14301
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
G1 X159.334 Y167.637 E.14301
G1 X159.422 Y167.696 E.00403
G1 X159.807 Y168.124 E.02185
G1 X160.055 Y168.551 E.01879
G1 X160.314 Y169.406 E.03394
G1 X160.302 Y169.834 E.01625
G1 X160.005 Y170.262 E.01978
G1 X159.334 Y170.714 E.03073
G1 X159.334 Y169.12 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 9.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y170.714 E-.60572
G1 X159.671 Y170.487 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 41/107
; update layer progress
M73 L41
M991 S0 P40 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z9.96 I1.202 J.193 P1  F60000
G1 X160.806 Y163.407 Z9.96
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X164.487 Y156.593 E.13981
G1 X164.487 Y163.407 E.25885
G1 X160.866 Y163.407 E.13753
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10736
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y155.41 E.25295
G1 X161.19 Y155.81 E.01405
G1 X161.19 Y156.21 E.01405
G1 F9950.696
G1 X161.471 Y156.21 E.00987
G1 F9101.149
G1 X161.871 Y156.21 E.01405
G1 F7957.206
G1 X162.271 Y156.21 E.01405
G1 F6890.062
G1 X162.671 Y156.21 E.01405
G1 F5899.718
G1 X163.071 Y156.21 E.01405
G1 F4986.175
G1 X163.471 Y156.21 E.01405
G1 F4149.431
G1 X163.871 Y156.21 E.01405
G1 F3389.487
G1 X164.271 Y156.21 E.01405
G1 F2706.344
G1 X164.671 Y156.21 E.01405
G1 F2100
G1 X164.87 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X164.87 Y163.79 E.2663
M106 S0
G1 F2100
G1 X164.671 Y163.79 E.00699
G1 F2706.344
G1 X164.271 Y163.79 E.01405
G1 F3389.487
G1 X163.871 Y163.79 E.01405
G1 F4149.431
G1 X163.471 Y163.79 E.01405
G1 F4986.175
G1 X163.071 Y163.79 E.01405
G1 F5899.718
G1 X162.671 Y163.79 E.01405
G1 F6890.062
G1 X162.271 Y163.79 E.01405
G1 F7957.206
G1 X161.871 Y163.79 E.01405
G1 F9101.149
G1 X161.471 Y163.79 E.01405
G1 F9766.116
G1 X161.25 Y163.79 E.00776
M204 S10000
G1 X160.791 Y163.066 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X162.385 Y163.066 E.06056
G1 X162.941 Y162.565 E.02841
G1 X163.23 Y162.138 E.01961
G1 X163.406 Y161.71 E.01756
G1 X163.496 Y160.855 E.03267
G1 X163.362 Y160.428 E.01702
G1 X163.01 Y160 E.02106
G1 X162.059 Y159.145 E.04858
G1 X161.77 Y158.717 E.01961
G1 X161.595 Y158.29 E.01756
G1 X161.504 Y157.435 E.03267
G1 X161.638 Y157.007 E.01702
G1 X161.698 Y156.934 E.00358
G1 X160.466 Y156.934 E.04681
G1 X160.466 Y148.934 E.30394
G1 X160.059 Y148.934 E.01543
G1 X159.942 Y149.311 E.01499
G1 X159.589 Y149.738 E.02106
G1 X159.334 Y149.968 E.01302
G1 X159.334 Y153.847 E.14738
G1 X159.52 Y154.014 E.0095
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
G1 X159.334 Y167.529 E.14738
G1 X159.52 Y167.696 E.0095
G1 X159.81 Y168.124 E.01961
G1 X159.985 Y168.551 E.01756
G1 X160.075 Y169.406 E.03267
G1 X159.942 Y169.834 E.01702
G1 X159.589 Y170.262 E.02106
G1 X159.334 Y170.491 E.01302
G1 X159.334 Y171.066 E.02183
G1 X160.354 Y171.066 E.03873
; WIPE_START
G1 X159.334 Y171.066 E-.38733
G1 X159.334 Y170.491 E-.21839
G1 X159.589 Y170.262 E-.13026
G1 X159.63 Y170.213 E-.02403
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.592 Y163.69 Z10.2 F60000
G1 X164.037 Y162.957 Z10.2
G1 Z9.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X164.037 Y157.103 E.27906
; CHANGE_LAYER
; Z_HEIGHT: 10.04
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9001.081
G1 X164.037 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 42/107
; update layer progress
M73 L42
M991 S0 P41 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z10.2 I-.973 J-.731 P1  F60000
G1 X160.806 Y163.407 Z10.2
G1 Z10.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X164.727 Y156.593 E.14893
G1 X164.727 Y163.407 E.25885
G1 X160.866 Y163.407 E.14665
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10795
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y155.81 E.26701
G1 X161.19 Y156.21 E.01405
G1 F10706.33
G1 X161.711 Y156.21 E.0183
G1 F9101.149
G1 X162.111 Y156.21 E.01405
G1 F7957.206
G1 X162.511 Y156.21 E.01405
G1 F6890.062
G1 X162.911 Y156.21 E.01405
G1 F5899.718
G1 X163.311 Y156.21 E.01405
G1 F4986.175
G1 X163.711 Y156.21 E.01405
G1 F4149.431
G1 X164.111 Y156.21 E.01405
G1 F3389.487
G1 X164.511 Y156.21 E.01405
G1 F2706.344
G1 X164.911 Y156.21 E.01405
G1 F2100
G1 X165.11 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X165.11 Y163.79 E.2663
M106 S0
G1 F2100
G1 X164.911 Y163.79 E.00699
G1 F2706.344
G1 X164.511 Y163.79 E.01405
G1 F3389.487
G1 X164.111 Y163.79 E.01405
G1 F4149.431
G1 X163.711 Y163.79 E.01405
G1 F4986.175
G1 X163.311 Y163.79 E.01405
G1 F5899.718
G1 X162.911 Y163.79 E.01405
G1 F6890.062
G1 X162.511 Y163.79 E.01405
G1 F7957.206
G1 X162.111 Y163.79 E.01405
G1 F9101.149
G1 X161.711 Y163.79 E.01405
G1 F10514.805
G1 X161.25 Y163.79 E.0162
M204 S10000
G1 X161.043 Y163.066 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X162.637 Y163.066 E.06056
G1 X163.052 Y162.565 E.02469
G1 X163.261 Y162.138 E.01808
G1 X163.367 Y161.71 E.01673
G1 X163.386 Y161.283 E.01626
G1 X163.31 Y160.855 E.0165
G1 X163.1 Y160.428 E.0181
G1 X162.726 Y160 E.02157
G1 X162.289 Y159.572 E.02324
G1 X161.948 Y159.145 E.02077
G1 X161.739 Y158.717 E.01808
G1 X161.634 Y158.29 E.01673
G1 X161.614 Y157.862 E.01626
G1 X161.69 Y157.435 E.0165
G1 X161.9 Y157.007 E.0181
G1 X161.964 Y156.934 E.00367
G1 X160.466 Y156.934 E.05692
G1 X160.466 Y148.934 E.30394
G1 X159.864 Y148.934 E.02284
G1 X159.679 Y149.311 E.01594
G1 X159.334 Y149.706 E.01992
G1 X159.334 Y153.641 E.14953
G1 X159.631 Y154.014 E.0181
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
G1 X159.334 Y167.324 E.14953
G1 X159.631 Y167.696 E.0181
G1 X159.84 Y168.124 E.01808
G1 X159.946 Y168.551 E.01673
G1 X159.965 Y168.979 E.01626
G1 X159.889 Y169.406 E.0165
G1 X159.679 Y169.834 E.0181
G1 X159.334 Y170.229 E.01992
G1 X159.334 Y171.066 E.03179
G1 X160.092 Y171.066 E.02877
; WIPE_START
G1 X159.334 Y171.066 E-.28777
G1 X159.334 Y170.229 E-.31795
G1 X159.602 Y169.923 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.855 Y163.586 Z10.44 F60000
G1 X164.277 Y162.957 Z10.44
G1 Z10.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X164.277 Y157.103 E.27906
; CHANGE_LAYER
; Z_HEIGHT: 10.28
; LAYER_HEIGHT: 0.24
; WIPE_START
M73 P66 R3
G1 F9001.081
G1 X164.277 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 43/107
; update layer progress
M73 L43
M991 S0 P42 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z10.44 I-.947 J-.764 P1  F60000
G1 X160.806 Y163.407 Z10.44
G1 Z10.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X164.967 Y156.593 E.15805
G1 X164.967 Y163.407 E.25885
G1 X160.866 Y163.407 E.15577
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10846
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y155.81 E.26701
G1 X161.19 Y156.21 E.01405
G1 X161.551 Y156.21 E.01268
G1 F10321.893
G1 X161.951 Y156.21 E.01405
G1 F9101.149
G1 X162.351 Y156.21 E.01405
G1 F7957.206
G1 X162.751 Y156.21 E.01405
G1 F6890.062
G1 X163.151 Y156.21 E.01405
G1 F5899.718
G1 X163.551 Y156.21 E.01405
G1 F4986.175
G1 X163.951 Y156.21 E.01405
G1 F4149.431
G1 X164.351 Y156.21 E.01405
G1 F3389.487
G1 X164.751 Y156.21 E.01405
G1 F2706.344
G1 X165.151 Y156.21 E.01405
G1 F2100
G1 X165.35 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X165.35 Y163.79 E.2663
M106 S0
G1 F2100
G1 X165.151 Y163.79 E.00699
G1 F2706.344
G1 X164.751 Y163.79 E.01405
G1 F3389.487
G1 X164.351 Y163.79 E.01405
G1 F4149.431
G1 X163.951 Y163.79 E.01405
G1 F4986.175
G1 X163.551 Y163.79 E.01405
G1 F5899.718
G1 X163.151 Y163.79 E.01405
G1 F6890.062
G1 X162.751 Y163.79 E.01405
G1 F7957.206
G1 X162.351 Y163.79 E.01405
G1 F9101.149
G1 X161.951 Y163.79 E.01405
G1 F10321.893
G1 X161.551 Y163.79 E.01405
G1 F10846
G1 X161.25 Y163.79 E.01057
M204 S10000
G1 X161.253 Y163.066 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X162.847 Y163.066 E.06056
G1 X162.914 Y162.993 E.00376
G1 X163.181 Y162.565 E.01915
G1 X163.317 Y162.138 E.01705
G1 X163.355 Y161.71 E.01631
G1 X163.307 Y161.283 E.01635
G1 X163.16 Y160.855 E.01718
G1 X162.882 Y160.428 E.01937
G1 X162.086 Y159.572 E.04439
G1 X161.819 Y159.145 E.01915
G1 X161.683 Y158.717 E.01705
G1 X161.645 Y158.29 E.01631
G1 X161.693 Y157.862 E.01635
G1 X161.84 Y157.435 E.01718
G1 X162.118 Y157.007 E.01937
G1 X162.186 Y156.934 E.00378
G1 X160.466 Y156.934 E.06537
G1 X160.466 Y148.934 E.30394
G1 X159.706 Y148.934 E.02886
G1 X159.462 Y149.311 E.01705
G1 X159.334 Y149.447 E.00707
G1 X159.334 Y153.415 E.15076
G1 X159.493 Y153.587 E.0089
G1 X159.76 Y154.014 E.01915
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
G1 X159.334 Y167.097 E.15076
G1 X159.493 Y167.269 E.0089
G1 X159.76 Y167.696 E.01915
G1 X159.897 Y168.124 E.01705
G1 X159.935 Y168.551 E.01631
G1 X159.886 Y168.979 E.01635
G1 X159.739 Y169.406 E.01718
G1 X159.462 Y169.834 E.01937
G1 X159.334 Y169.97 E.00707
G1 X159.334 Y171.066 E.04163
G1 X159.833 Y171.066 E.01893
; WIPE_START
G1 X159.334 Y171.066 E-.18932
G1 X159.334 Y169.97 E-.41639
G1 X159.462 Y169.834 E-.07068
G1 X159.581 Y169.649 E-.08361
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.112 Y163.507 Z10.68 F60000
G1 X164.517 Y162.957 Z10.68
G1 Z10.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X164.517 Y157.103 E.27906
; CHANGE_LAYER
; Z_HEIGHT: 10.52
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F9001.081
G1 X164.517 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 44/107
; update layer progress
M73 L44
M991 S0 P43 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z10.68 I-.922 J-.795 P1  F60000
G1 X160.806 Y163.407 Z10.68
G1 Z10.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X165.207 Y156.593 E.16717
G1 X165.207 Y163.407 E.25885
G1 X160.866 Y163.407 E.16489
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10891
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X161.391 Y156.21 E.00706
G1 X161.791 Y156.21 E.01405
G1 F10321.893
G1 X162.191 Y156.21 E.01405
G1 F9101.149
G1 X162.591 Y156.21 E.01405
G1 F7957.206
G1 X162.991 Y156.21 E.01405
G1 F6890.062
G1 X163.391 Y156.21 E.01405
G1 F5899.718
G1 X163.791 Y156.21 E.01405
G1 F4986.175
G1 X164.191 Y156.21 E.01405
G1 F4149.431
G1 X164.591 Y156.21 E.01405
G1 F3389.487
G1 X164.991 Y156.21 E.01405
G1 F2706.344
G1 X165.391 Y156.21 E.01405
G1 F2100
G1 X165.59 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X165.59 Y163.79 E.2663
M106 S0
G1 F2100
G1 X165.391 Y163.79 E.00699
G1 F2706.344
G1 X164.991 Y163.79 E.01405
G1 F3389.487
G1 X164.591 Y163.79 E.01405
G1 F4149.431
G1 X164.191 Y163.79 E.01405
G1 F4986.175
G1 X163.791 Y163.79 E.01405
G1 F5899.718
G1 X163.391 Y163.79 E.01405
G1 F6890.062
G1 X162.991 Y163.79 E.01405
G1 F7957.206
G1 X162.591 Y163.79 E.01405
G1 F9101.149
G1 X162.191 Y163.79 E.01405
G1 F10321.893
G1 X161.791 Y163.79 E.01405
G1 F10891
G1 X161.25 Y163.79 E.01901
M204 S10000
G1 X161.48 Y163.066 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X163.074 Y163.066 E.06056
G1 X163.137 Y162.993 E.00365
G1 X163.336 Y162.565 E.01792
G1 X163.401 Y162.138 E.01643
G1 X163.371 Y161.71 E.01628
G1 X163.254 Y161.283 E.01683
G1 X163.034 Y160.855 E.01828
G1 X162.68 Y160.428 E.02108
G1 X162.234 Y160 E.02348
G1 X161.864 Y159.572 E.02149
G1 X161.664 Y159.145 E.01792
G1 X161.599 Y158.717 E.01643
G1 X161.629 Y158.29 E.01628
G1 X161.746 Y157.862 E.01683
G1 X161.966 Y157.435 E.01828
G1 X162.396 Y156.934 E.02504
G1 X160.466 Y156.934 E.07333
G1 X160.466 Y148.934 E.30394
G1 X159.571 Y148.934 E.03399
G1 X159.334 Y149.221 E.01411
G1 X159.334 Y153.148 E.14923
G1 X159.716 Y153.587 E.02208
G1 X159.915 Y154.014 E.01792
G1 X159.98 Y154.442 E.01643
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
G1 X159.334 Y166.83 E.14923
G1 X159.716 Y167.269 E.02208
G1 X159.915 Y167.696 E.01792
G1 X159.98 Y168.124 E.01643
G1 X159.95 Y168.551 E.01628
G1 X159.834 Y168.979 E.01683
G1 X159.613 Y169.406 E.01828
G1 X159.334 Y169.744 E.01662
G1 X159.334 Y171.066 E.05022
G1 X159.607 Y171.066 E.01034
; WIPE_START
G1 X159.334 Y171.066 E-.10343
G1 X159.334 Y169.744 E-.50229
G1 X159.593 Y169.431 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.353 Y163.464 Z10.92 F60000
G1 X164.757 Y162.957 Z10.92
G1 Z10.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X164.757 Y157.103 E.27906
; CHANGE_LAYER
; Z_HEIGHT: 10.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9001.081
G1 X164.757 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 45/107
; update layer progress
M73 L45
M991 S0 P44 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z10.92 I-.897 J-.823 P1  F60000
G1 X160.806 Y163.407 Z10.92
G1 Z10.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X165.447 Y156.593 E.17629
G1 X165.447 Y163.407 E.25885
G1 X160.866 Y163.407 E.17401
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10930
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X161.631 Y156.21 E.01549
G1 X162.031 Y156.21 E.01405
G1 F10321.893
G1 X162.431 Y156.21 E.01405
G1 F9101.149
G1 X162.831 Y156.21 E.01405
G1 F7957.206
G1 X163.231 Y156.21 E.01405
G1 F6890.062
G1 X163.631 Y156.21 E.01405
G1 F5899.718
G1 X164.031 Y156.21 E.01405
G1 F4986.175
G1 X164.431 Y156.21 E.01405
G1 F4149.431
G1 X164.831 Y156.21 E.01405
G1 F3389.487
G1 X165.231 Y156.21 E.01405
G1 F2706.344
G1 X165.631 Y156.21 E.01405
G1 F2100
G1 X165.83 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X165.83 Y163.79 E.2663
M106 S0
G1 F2100
G1 X165.631 Y163.79 E.00699
G1 F2706.344
M73 P67 R3
G1 X165.231 Y163.79 E.01405
G1 F3389.487
G1 X164.831 Y163.79 E.01405
G1 F4149.431
G1 X164.431 Y163.79 E.01405
G1 F4986.175
G1 X164.031 Y163.79 E.01405
G1 F5899.718
G1 X163.631 Y163.79 E.01405
G1 F6890.062
G1 X163.231 Y163.79 E.01405
G1 F7957.206
G1 X162.831 Y163.79 E.01405
G1 F9101.149
G1 X162.431 Y163.79 E.01405
G1 F10321.893
G1 X162.031 Y163.79 E.01405
G1 F10930
G1 X161.631 Y163.79 E.01405
G1 X161.25 Y163.79 E.01339
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.997 Y162.957 Z11.16 F60000
G1 Z10.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X164.997 Y157.103 E.27906
; WIPE_START
G1 X164.997 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.058 Y156.934 Z11.16 F60000
G1 Z10.76
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X162.652 Y156.934 E.06056
G1 X162.075 Y157.435 E.02901
G1 X161.772 Y157.862 E.0199
G1 X161.586 Y158.29 E.01772
G1 X161.471 Y159.145 E.03278
G1 X161.591 Y159.572 E.01686
G1 X161.939 Y160 E.02096
G1 X162.925 Y160.855 E.04959
G1 X163.228 Y161.283 E.0199
G1 X163.414 Y161.71 E.01772
G1 X163.529 Y162.565 E.03278
G1 X163.409 Y162.993 E.01686
G1 X163.35 Y163.066 E.00356
G1 X160.466 Y163.066 E.1096
G1 X160.466 Y171.066 E.30394
G1 X159.334 Y171.066 E.04297
G1 X159.334 Y169.554 E.05743
G1 X159.505 Y169.406 E.00856
G1 X159.807 Y168.979 E.0199
G1 X159.994 Y168.551 E.01772
G1 X160.108 Y167.696 E.03278
G1 X159.989 Y167.269 E.01686
G1 X159.64 Y166.841 E.02096
G1 X159.334 Y166.576 E.01539
G1 X159.334 Y162.713 E.14675
G1 X159.505 Y162.565 E.00856
G1 X159.807 Y162.138 E.0199
G1 X159.994 Y161.71 E.01772
G1 X160.108 Y160.855 E.03278
G1 X159.989 Y160.428 E.01686
G1 X159.64 Y160 E.02096
G1 X159.334 Y159.735 E.01539
G1 X159.334 Y155.872 E.14675
G1 X159.505 Y155.724 E.00856
G1 X159.807 Y155.297 E.0199
G1 X159.994 Y154.869 E.01772
G1 X160.108 Y154.014 E.03278
G1 X159.989 Y153.587 E.01686
G1 X159.64 Y153.159 E.02096
G1 X159.334 Y152.894 E.01539
G1 X159.334 Y151.3 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 11
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y152.894 E-.60571
G1 X159.64 Y153.159 E-.15392
G1 X159.641 Y153.16 E-.00037
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 46/107
; update layer progress
M73 L46
M991 S0 P45 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z11.16 I-1.209 J.138 P1  F60000
G1 X160.806 Y163.407 Z11.16
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X165.687 Y156.593 E.18541
G1 X165.687 Y163.407 E.25885
G1 X160.866 Y163.407 E.18313
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10964
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X161.471 Y156.21 E.00987
G1 X161.871 Y156.21 E.01405
G1 X162.271 Y156.21 E.01405
G1 F10321.893
G1 X162.671 Y156.21 E.01405
G1 F9101.149
G1 X163.071 Y156.21 E.01405
G1 F7957.206
G1 X163.471 Y156.21 E.01405
G1 F6890.062
G1 X163.871 Y156.21 E.01405
G1 F5899.718
G1 X164.271 Y156.21 E.01405
G1 F4986.175
G1 X164.671 Y156.21 E.01405
G1 F4149.431
G1 X165.071 Y156.21 E.01405
G1 F3389.487
G1 X165.471 Y156.21 E.01405
G1 F2706.344
G1 X165.871 Y156.21 E.01405
G1 F2100
G1 X166.07 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X166.07 Y163.79 E.2663
M106 S0
G1 F2100
G1 X165.871 Y163.79 E.00699
G1 F2706.344
G1 X165.471 Y163.79 E.01405
G1 F3389.487
G1 X165.071 Y163.79 E.01405
G1 F4149.431
G1 X164.671 Y163.79 E.01405
G1 F4986.175
G1 X164.271 Y163.79 E.01405
G1 F5899.718
G1 X163.871 Y163.79 E.01405
G1 F6890.062
G1 X163.471 Y163.79 E.01405
G1 F7957.206
G1 X163.071 Y163.79 E.01405
G1 F9101.149
G1 X162.671 Y163.79 E.01405
G1 F10321.893
G1 X162.271 Y163.79 E.01405
G1 F10964
G1 X161.871 Y163.79 E.01405
G1 X161.471 Y163.79 E.01405
G1 X161.25 Y163.79 E.00776
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.153 Y163.066 Z11.4 F60000
G1 Z11
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X163.747 Y163.066 E.06056
G1 X163.794 Y162.993 E.00327
G1 X163.777 Y162.565 E.01626
G1 X163.49 Y161.71 E.03427
G1 X163.23 Y161.283 E.01901
G1 X162.829 Y160.855 E.02228
G1 X162.201 Y160.428 E.02886
G1 X161.48 Y160 E.03184
G1 X161.206 Y159.572 E.01929
G1 X161.223 Y159.145 E.01626
G1 X161.51 Y158.29 E.03427
G1 X161.77 Y157.862 E.01901
G1 X162.171 Y157.435 E.02228
G1 X162.922 Y156.934 E.03426
G1 X164.673 Y156.934 E.06654
G1 X164.627 Y157.007 E.00328
G1 X164.644 Y157.435 E.01626
G1 X164.788 Y157.865 E.01724
G1 X164.788 Y159.459 E.06056
; WIPE_START
G1 X164.788 Y157.865 E-.60572
G1 X164.659 Y157.48 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.237 Y162.957 Z11.4 F60000
G1 Z11
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X165.237 Y157.103 E.27906
; WIPE_START
G1 X165.237 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.704 Y152.962 Z11.4 F60000
G1 X159.334 Y151.107 Z11.4
G1 Z11
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y152.701 E.06056
G1 X160.1 Y153.159 E.03387
G1 X160.373 Y153.587 E.01929
G1 X160.356 Y154.014 E.01626
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
G1 X159.334 Y166.383 E.14315
G1 X160.1 Y166.841 E.03387
G1 X160.373 Y167.269 E.01929
G1 X160.356 Y167.696 E.01626
G1 X160.069 Y168.551 E.03427
G1 X159.809 Y168.979 E.01901
G1 X159.408 Y169.406 E.02228
G1 X159.334 Y169.457 E.00339
G1 X159.334 Y171.051 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 11.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y169.457 E-.60571
G1 X159.408 Y169.406 E-.03389
G1 X159.625 Y169.175 E-.1204
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 47/107
; update layer progress
M73 L47
M991 S0 P46 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z11.4 I1.192 J.244 P1  F60000
G1 X160.806 Y163.407 Z11.4
G1 Z11.24
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X165.927 Y156.593 E.19452
G1 X165.927 Y163.407 E.25885
G1 X160.866 Y163.407 E.19224
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10993
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X161.711 Y156.21 E.0183
G1 X162.111 Y156.21 E.01405
G1 X162.511 Y156.21 E.01405
G1 F10321.893
G1 X162.911 Y156.21 E.01405
G1 F9101.149
G1 X163.311 Y156.21 E.01405
G1 F7957.206
G1 X163.711 Y156.21 E.01405
G1 F6890.062
G1 X164.111 Y156.21 E.01405
G1 F5899.718
G1 X164.511 Y156.21 E.01405
G1 F4986.175
G1 X164.911 Y156.21 E.01405
G1 F4149.431
G1 X165.311 Y156.21 E.01405
G1 F3389.487
G1 X165.711 Y156.21 E.01405
G1 F2706.344
G1 X166.111 Y156.21 E.01405
G1 F2100
G1 X166.31 Y156.21 E.00699
M106 S178.5
G1 F1950
G1 X166.31 Y163.79 E.2663
M106 S0
G1 F2100
G1 X166.111 Y163.79 E.00699
G1 F2706.344
G1 X165.711 Y163.79 E.01405
G1 F3389.487
G1 X165.311 Y163.79 E.01405
G1 F4149.431
G1 X164.911 Y163.79 E.01405
G1 F4986.175
G1 X164.511 Y163.79 E.01405
G1 F5899.718
G1 X164.111 Y163.79 E.01405
G1 F6890.062
G1 X163.711 Y163.79 E.01405
G1 F7957.206
G1 X163.311 Y163.79 E.01405
G1 F9101.149
G1 X162.911 Y163.79 E.01405
G1 F10321.893
G1 X162.511 Y163.79 E.01405
G1 F10993
G1 X162.111 Y163.79 E.01405
G1 X161.711 Y163.79 E.01405
G1 X161.25 Y163.79 E.0162
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.608 Z11.64 F60000
G1 Z11.24
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y166.202 E.06056
G1 X159.935 Y166.4 E.02401
G1 X160.362 Y166.412 E.01625
G1 X160.466 Y166.344 E.00469
G1 X160.466 Y168.055 E.065
G1 X159.935 Y168.883 E.03736
G1 X159.507 Y169.281 E.0222
G1 X159.334 Y169.385 E.00766
G1 X159.334 Y170.979 E.06056
; WIPE_START
G1 X159.334 Y169.385 E-.60571
G1 X159.507 Y169.281 E-.07661
G1 X159.657 Y169.141 E-.07768
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.573 Y162.59 Z11.64 F60000
G1 X165.028 Y160.157 Z11.64
G1 Z11.24
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X165.028 Y158.563 E.06056
G1 X164.21 Y157.288 E.05755
G1 X163.783 Y157.009 E.01939
G1 X163.355 Y157.021 E.01625
G1 X162.5 Y157.302 E.03421
G1 X162.072 Y157.56 E.01897
G1 X161.645 Y157.959 E.0222
G1 X160.79 Y159.292 E.06017
G1 X160.362 Y159.57 E.01939
G1 X159.935 Y159.559 E.01625
G1 X159.334 Y159.361 E.02401
M73 P68 R3
G1 X159.334 Y162.544 E.12092
G1 X159.507 Y162.44 E.00766
G1 X159.935 Y162.041 E.0222
G1 X160.79 Y160.708 E.06017
G1 X161.217 Y160.43 E.01939
G1 X161.645 Y160.441 E.01625
G1 X162.5 Y160.723 E.03421
G1 X162.928 Y160.981 E.01897
G1 X163.355 Y161.379 E.0222
G1 X164.21 Y162.712 E.06017
G1 X164.638 Y162.991 E.01939
G1 X165.028 Y162.98 E.01483
G1 X165.028 Y161.386 E.06056
; WIPE_START
G1 X165.028 Y162.98 E-.60572
G1 X164.638 Y162.991 E-.14835
G1 X164.625 Y162.982 E-.00594
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.477 Y162.957 Z11.64 F60000
G1 Z11.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551444
G1 F9001.081
M204 S8000
G1 X165.477 Y157.103 E.27906
; WIPE_START
G1 X165.477 Y159.103 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y157.297 Z11.64 F60000
G1 Z11.24
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y155.703 E.06056
G1 X159.507 Y155.599 E.00766
G1 X159.935 Y155.2 E.0222
G1 X160.466 Y154.373 E.03736
G1 X160.466 Y152.662 E.065
G1 X160.362 Y152.729 E.00469
G1 X159.935 Y152.718 E.01625
G1 X159.334 Y152.52 E.02401
G1 X159.334 Y150.926 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 11.48
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y152.52 E-.60571
G1 X159.72 Y152.647 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 48/107
; update layer progress
M73 L48
M991 S0 P47 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z11.64 I-1.211 J.122 P1  F60000
G1 X160.806 Y163.407 Z11.64
G1 Z11.48
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11019
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.351 Y156.21 E.18132
G1 X166.39 Y156.21 E.00137
G1 X166.39 Y163.79 E.2663
G1 X166.351 Y163.79 E.00137
G1 X161.25 Y163.79 E.17921
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.482 Z11.88 F60000
G1 Z11.48
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y166.076 E.06056
G1 X159.935 Y166.153 E.02299
G1 X160.362 Y166.032 E.01689
G1 X160.466 Y165.947 E.00507
G1 X160.466 Y168.371 E.09209
G1 X159.935 Y168.979 E.03067
G1 X159.507 Y169.279 E.01985
G1 X159.334 Y169.354 E.00714
G1 X159.334 Y170.948 E.06056
; WIPE_START
G1 X159.334 Y169.354 E-.60571
G1 X159.507 Y169.279 E-.07145
G1 X159.685 Y169.154 E-.08284
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.008 Y163.684 Z11.88 F60000
G1 X165.637 Y163.037 Z11.88
G1 Z11.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.391504
G1 F13235.295
M204 S8000
G1 X165.637 Y157.023 E.19497
M204 S10000
G1 X165.268 Y157.266 F60000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.268 Y158.86 E.06056
G1 X165.065 Y158.718 E.00941
G1 X164.21 Y157.738 E.0494
G1 X163.783 Y157.389 E.02098
G1 X163.355 Y157.267 E.01689
G1 X162.5 Y157.377 E.03276
G1 X162.072 Y157.562 E.01769
G1 X161.645 Y157.862 E.01985
G1 X160.79 Y158.841 E.0494
G1 X160.362 Y159.191 E.02097
G1 X159.935 Y159.312 E.01689
G1 X159.334 Y159.235 E.02299
G1 X159.334 Y162.513 E.12453
G1 X159.507 Y162.438 E.00714
G1 X159.935 Y162.138 E.01985
G1 X160.79 Y161.159 E.0494
G1 X161.217 Y160.81 E.02097
G1 X161.645 Y160.688 E.01689
G1 X162.5 Y160.798 E.03276
G1 X162.928 Y160.982 E.01769
G1 X163.355 Y161.282 E.01985
G1 X164.21 Y162.262 E.0494
G1 X164.638 Y162.611 E.02097
G1 X165.065 Y162.733 E.01689
G1 X165.268 Y162.707 E.00776
G1 X165.268 Y163.066 E.01363
G1 X164.033 Y163.066 E.04693
; WIPE_START
G1 X165.268 Y163.066 E-.4694
G1 X165.268 Y162.707 E-.13631
G1 X165.065 Y162.733 E-.07765
G1 X164.871 Y162.678 E-.07664
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.413 Y157.343 Z11.88 F60000
G1 X159.334 Y157.266 Z11.88
G1 Z11.48
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X159.334 Y155.672 E.06056
G1 X159.507 Y155.597 E.00714
G1 X159.935 Y155.297 E.01985
G1 X160.466 Y154.689 E.03067
G1 X160.466 Y152.265 E.09209
G1 X160.362 Y152.35 E.00507
G1 X159.935 Y152.471 E.01689
G1 X159.334 Y152.394 E.02299
G1 X159.334 Y150.8 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 11.72
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F11292.473
G1 X159.334 Y152.394 E-.60571
G1 X159.737 Y152.446 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 49/107
; update layer progress
M73 L49
M991 S0 P48 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z11.88 I-1.211 J.118 P1  F60000
G1 X160.806 Y163.407 Z11.88
G1 Z11.72
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11044
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.423 Z12.12 F60000
G1 Z11.72
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y166.017 E.06056
G1 X159.507 Y166.029 E.00657
G1 X159.935 Y165.962 E.01644
G1 X160.362 Y165.761 E.01795
G1 X160.466 Y165.671 E.0052
G1 X160.466 Y168.63 E.11241
G1 X160.362 Y168.737 E.00566
G1 X159.935 Y169.088 E.02102
G1 X159.507 Y169.307 E.01824
G1 X159.334 Y169.353 E.00679
G1 X159.334 Y170.947 E.06056
; WIPE_START
G1 X159.334 Y169.353 E-.60571
G1 X159.507 Y169.307 E-.06791
G1 X159.709 Y169.203 E-.08638
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.43 Y163.206 Z12.12 F60000
G1 X164.54 Y163.066 Z12.12
G1 Z11.72
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X165.666 Y163.066 E.04275
G1 X165.666 Y162.597 E.01781
G1 X165.493 Y162.608 E.00657
G1 X165.065 Y162.541 E.01644
G1 X164.638 Y162.34 E.01796
G1 X164.21 Y161.969 E.02151
G1 X163.783 Y161.524 E.02344
G1 X163.355 Y161.173 E.02102
G1 X162.928 Y160.955 E.01824
G1 X162.5 Y160.84 E.01681
G1 X162.072 Y160.812 E.01628
G1 X161.645 Y160.879 E.01644
G1 X161.217 Y161.08 E.01796
G1 X160.79 Y161.451 E.02151
G1 X160.362 Y161.896 E.02344
G1 X159.935 Y162.247 E.02102
G1 X159.507 Y162.466 E.01824
G1 X159.334 Y162.512 E.00679
G1 X159.334 Y159.176 E.12673
G1 X159.507 Y159.188 E.00657
G1 X159.935 Y159.121 E.01644
G1 X160.362 Y158.92 E.01795
G1 X160.79 Y158.549 E.02151
G1 X161.217 Y158.104 E.02344
G1 X161.645 Y157.753 E.02102
G1 X162.072 Y157.534 E.01824
G1 X162.5 Y157.42 E.01682
G1 X162.928 Y157.392 E.01628
G1 X163.355 Y157.459 E.01644
G1 X163.783 Y157.66 E.01795
G1 X164.21 Y158.031 E.02151
G1 X164.638 Y158.476 E.02344
G1 X165.065 Y158.827 E.02102
G1 X165.493 Y159.045 E.01824
G1 X165.666 Y159.091 E.00679
G1 X165.666 Y157.497 E.06056
; WIPE_START
G1 X165.666 Y159.091 E-.60571
G1 X165.493 Y159.045 E-.06789
G1 X165.291 Y158.942 E-.0864
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y157.265 Z12.12 F60000
G1 Z11.72
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X159.334 Y155.671 E.06056
G1 X159.507 Y155.625 E.00679
G1 X159.935 Y155.406 E.01824
G1 X160.362 Y155.055 E.02102
G1 X160.466 Y154.948 E.00566
G1 X160.466 Y151.989 E.11241
G1 X160.362 Y152.079 E.0052
G1 X159.935 Y152.28 E.01795
G1 X159.507 Y152.347 E.01644
G1 X159.334 Y152.335 E.00657
G1 X159.334 Y150.741 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 11.96
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y152.335 E-.60571
G1 X159.507 Y152.347 E-.06575
G1 X159.737 Y152.311 E-.08854
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 50/107
; update layer progress
M73 L50
M991 S0 P49 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z12.12 I-1.211 J.117 P1  F60000
G1 X160.806 Y163.407 Z12.12
G1 Z11.96
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
M73 P69 R3
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11072
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y164.368 Z12.36 F60000
G1 Z11.96
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y165.962 E.06056
G1 X159.507 Y165.946 E.00659
G1 X159.935 Y165.808 E.01707
G1 X160.362 Y165.539 E.01919
G1 X160.466 Y165.443 E.00535
G1 X160.466 Y168.843 E.12915
G1 X160.362 Y168.939 E.00537
G1 X159.935 Y169.215 E.01933
G1 X159.507 Y169.36 E.01716
G1 X159.334 Y169.379 E.0066
G1 X159.334 Y170.973 E.06056
; WIPE_START
G1 X159.334 Y169.379 E-.60571
G1 X159.507 Y169.36 E-.06599
G1 X159.727 Y169.285 E-.0883
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.431 Y163.275 Z12.36 F60000
G1 X164.595 Y163.066 Z12.36
G1 Z11.96
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X165.666 Y163.066 E.04066
G1 X165.666 Y162.542 E.0199
G1 X165.493 Y162.526 E.00659
G1 X165.065 Y162.387 E.01707
G1 X164.638 Y162.118 E.01919
G1 X163.783 Y161.323 E.04438
G1 X163.355 Y161.047 E.01933
G1 X162.928 Y160.902 E.01716
G1 X162.5 Y160.855 E.01634
G1 X162.072 Y160.895 E.01631
G1 X161.645 Y161.033 E.01707
G1 X161.217 Y161.302 E.01919
G1 X160.362 Y162.098 E.04438
G1 X159.935 Y162.374 E.01933
G1 X159.507 Y162.519 E.01716
G1 X159.334 Y162.538 E.0066
G1 X159.334 Y159.121 E.1298
G1 X159.507 Y159.105 E.00659
G1 X159.935 Y158.967 E.01707
G1 X160.362 Y158.698 E.01919
G1 X161.217 Y157.902 E.04438
G1 X161.645 Y157.626 E.01933
G1 X162.072 Y157.481 E.01716
G1 X162.5 Y157.435 E.01634
G1 X162.928 Y157.474 E.01631
G1 X163.355 Y157.613 E.01707
G1 X163.783 Y157.882 E.01919
G1 X164.638 Y158.678 E.04438
G1 X165.065 Y158.953 E.01933
G1 X165.493 Y159.099 E.01716
G1 X165.666 Y159.117 E.0066
G1 X165.666 Y157.523 E.06056
; WIPE_START
G1 X165.666 Y159.117 E-.60571
G1 X165.493 Y159.099 E-.06597
G1 X165.273 Y159.024 E-.08832
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y157.291 Z12.36 F60000
G1 Z11.96
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X159.334 Y155.697 E.06056
G1 X159.507 Y155.678 E.0066
G1 X159.935 Y155.533 E.01716
G1 X160.362 Y155.257 E.01933
G1 X160.466 Y155.16 E.00537
G1 X160.466 Y151.761 E.12915
G1 X160.362 Y151.857 E.00535
G1 X159.935 Y152.126 E.01919
G1 X159.507 Y152.264 E.01707
G1 X159.334 Y152.28 E.00659
G1 X159.334 Y150.686 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 12.2
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y152.28 E-.60571
G1 X159.507 Y152.264 E-.06589
G1 X159.728 Y152.193 E-.0884
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 51/107
; update layer progress
M73 L51
M991 S0 P50 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z12.36 I-1.211 J.116 P1  F60000
G1 X160.806 Y163.407 Z12.36
G1 Z12.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11029
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11029
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y171.025 Z12.6 F60000
G1 Z12.2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11029
M204 S8000
G1 X159.334 Y169.431 E.06056
G1 X159.507 Y169.44 E.00657
G1 X159.935 Y169.366 E.01649
G1 X160.362 Y169.158 E.01807
G1 X160.466 Y169.068 E.00521
G1 X160.466 Y165.23 E.14579
G1 X160.362 Y165.337 E.00563
G1 X159.935 Y165.679 E.02082
G1 X159.507 Y165.89 E.01812
G1 X159.334 Y165.934 E.00676
G1 X159.334 Y162.59 E.12703
G1 X159.507 Y162.599 E.00657
G1 X159.935 Y162.525 E.01649
G1 X160.362 Y162.317 E.01807
G1 X160.79 Y161.944 E.02156
G1 X161.217 Y161.505 E.02328
G1 X161.645 Y161.162 E.02082
G1 X162.072 Y160.951 E.01812
G1 X162.5 Y160.843 E.01675
G1 X162.928 Y160.822 E.01626
G1 X163.355 Y160.896 E.01649
G1 X163.783 Y161.104 E.01807
G1 X164.21 Y161.477 E.02156
G1 X164.638 Y161.916 E.02328
G1 X165.065 Y162.259 E.02082
G1 X165.493 Y162.47 E.01812
G1 X165.666 Y162.513 E.00676
G1 X165.666 Y159.17 E.12703
G1 X165.493 Y159.178 E.00657
G1 X165.065 Y159.104 E.01649
G1 X164.638 Y158.896 E.01807
G1 X164.21 Y158.523 E.02156
G1 X163.783 Y158.084 E.02328
G1 X163.355 Y157.741 E.02082
G1 X162.928 Y157.53 E.01812
G1 X162.5 Y157.423 E.01675
G1 X162.072 Y157.401 E.01626
G1 X161.645 Y157.475 E.01649
G1 X161.217 Y157.683 E.01807
G1 X160.79 Y158.056 E.02156
G1 X160.362 Y158.495 E.02328
G1 X159.935 Y158.838 E.02082
G1 X159.507 Y159.049 E.01812
G1 X159.334 Y159.093 E.00676
G1 X159.334 Y155.749 E.12703
G1 X159.507 Y155.758 E.00657
G1 X159.935 Y155.684 E.01649
G1 X160.362 Y155.476 E.01807
G1 X160.466 Y155.386 E.00521
G1 X160.466 Y151.548 E.14579
G1 X160.362 Y151.654 E.00563
G1 X159.935 Y151.997 E.02082
G1 X159.507 Y152.208 E.01812
G1 X159.334 Y152.252 E.00676
G1 X159.334 Y150.658 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 12.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y152.252 E-.60571
G1 X159.507 Y152.208 E-.06765
G1 X159.712 Y152.107 E-.08664
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 52/107
; update layer progress
M73 L52
M991 S0 P51 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z12.6 I-1.211 J.117 P1  F60000
G1 X160.806 Y163.407 Z12.6
G1 Z12.44
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11152
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.843 Y158.168 Z12.84 F60000
G1 X160.78 Y156.934 Z12.84
G1 Z12.44
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y156.934 E.01195
G1 X160.466 Y155.655 E.04861
G1 X160.362 Y155.74 E.00508
G1 X159.935 Y155.871 E.01699
G1 X159.334 Y155.805 E.02294
G1 X159.334 Y159.091 E.12486
G1 X159.507 Y159.019 E.0071
G1 X159.935 Y158.728 E.01966
G1 X160.79 Y157.771 E.04875
G1 X161.217 Y157.419 E.02104
G1 X161.645 Y157.288 E.01699
G1 X162.5 Y157.383 E.03269
G1 X162.928 Y157.56 E.01759
G1 X163.355 Y157.852 E.01966
M73 P70 R3
G1 X164.21 Y158.809 E.04875
G1 X164.638 Y159.16 E.02104
G1 X165.065 Y159.291 E.01699
G1 X165.666 Y159.225 E.02294
G1 X165.666 Y162.512 E.12486
G1 X165.493 Y162.44 E.0071
G1 X165.065 Y162.148 E.01966
G1 X164.21 Y161.192 E.04875
G1 X163.783 Y160.84 E.02104
G1 X163.355 Y160.709 E.01699
G1 X162.5 Y160.803 E.03269
G1 X162.072 Y160.981 E.01759
G1 X161.645 Y161.272 E.01966
G1 X160.79 Y162.229 E.04875
G1 X160.362 Y162.581 E.02104
G1 X159.935 Y162.712 E.01699
G1 X159.334 Y162.646 E.02294
G1 X159.334 Y165.932 E.12486
G1 X159.507 Y165.86 E.0071
G1 X159.935 Y165.569 E.01966
G1 X160.466 Y164.975 E.03027
G1 X160.466 Y169.337 E.16573
G1 X160.362 Y169.422 E.00508
G1 X159.935 Y169.553 E.01699
G1 X159.334 Y169.487 E.02294
G1 X159.334 Y171.066 E.05999
G1 X159.349 Y171.066 E.00057
; WIPE_START
G1 X159.334 Y171.066 E-.0057
G1 X159.334 Y169.487 E-.60001
G1 X159.738 Y169.531 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.542 Y161.901 Z12.84 F60000
G1 X159.334 Y153.844 Z12.84
G1 Z12.44
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X159.334 Y152.25 E.06056
G1 X159.507 Y152.178 E.0071
G1 X159.935 Y151.887 E.01966
G1 X160.466 Y151.293 E.03027
G1 X160.466 Y148.934 E.0896
G1 X160.246 Y148.934 E.00833
G1 X159.935 Y149.03 E.01238
G1 X159.334 Y148.963 E.02294
G1 X159.334 Y150.557 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 12.68
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F11292.473
G1 X159.334 Y148.963 E-.60572
G1 X159.738 Y149.008 E-.15429
; WIPE_END
M73 P70 R2
G1 E-.04 F1800
; layer num/total_layer_count: 53/107
; update layer progress
M73 L53
M991 S0 P52 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z12.84 I-1.214 J.09 P1  F60000
G1 X160.806 Y163.407 Z12.84
G1 Z12.68
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11203
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.471 Y171.066 Z13.08 F60000
G1 Z12.68
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y171.066 E.00519
G1 X159.334 Y169.608 E.05537
G1 X159.935 Y169.793 E.02386
G1 X160.362 Y169.786 E.01625
G1 X160.466 Y169.715 E.00476
G1 X160.466 Y164.675 E.19148
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
G1 X163.355 Y157.95 E.05854
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
; WIPE_START
G1 X160.466 Y156.033 E-.60571
G1 X160.362 Y156.104 E-.04763
G1 X160.082 Y156.109 E-.10666
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y153.872 Z13.08 F60000
G1 Z12.68
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X159.334 Y152.278 E.06056
G1 X159.507 Y152.177 E.0076
G1 X159.935 Y151.789 E.02193
G1 X160.466 Y150.993 E.03634
G1 X160.466 Y149.192 E.06842
G1 X160.362 Y149.263 E.00476
G1 X159.935 Y149.27 E.01625
G1 X159.334 Y149.085 E.02386
G1 X159.334 Y150.679 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 12.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y149.085 E-.60572
G1 X159.722 Y149.205 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 54/107
; update layer progress
M73 L54
M991 S0 P53 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z13.08 I-1.213 J.093 P1  F60000
G1 X160.806 Y163.407 Z13.08
G1 Z12.92
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11257
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.348 Y166.807 Z13.32 F60000
G1 Z12.92
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.391504
G1 F12000
M204 S8000
G1 X159.348 Y163.876 E.09503
G1 X159.437 Y163.417 E.01515
G1 X159.348 Y163.253 E.00605
G1 X159.348 Y155.375 E.25536
; WIPE_START
G1 X159.348 Y157.375 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.452 Y154.103 Z13.32 F60000
G1 Z12.92
G1 E.8 F1800
; LINE_WIDTH: 0.392088
G1 F12000
M204 S8000
G1 X160.452 Y156.793 E.08734
G1 X160.478 Y156.922 E.00427
G1 X160.607 Y156.948 E.00427
G1 X165.496 Y156.948 E.15875
G1 X165.625 Y156.975 E.00427
G1 X165.652 Y157.104 E.00427
G1 X165.652 Y162.896 E.18808
G1 X165.625 Y163.025 E.00427
G1 X165.496 Y163.052 E.00427
G1 X160.607 Y163.052 E.15875
G1 X160.478 Y163.078 E.00427
G1 X160.452 Y163.207 E.00427
G1 X160.452 Y166.018 E.09125
; WIPE_START
G1 X160.452 Y164.018 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y170.526 Z13.32 F60000
G1 Z12.92
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y171.066 E.02049
G1 X160.389 Y171.066 E.04007
G1 X160.423 Y170.689 E.01436
G1 X160.17 Y170.262 E.01887
G1 X159.334 Y169.783 E.03658
G1 X159.334 Y167.242 E.09654
G1 X159.703 Y166.998 E.01679
G1 X159.703 Y165.671 E.05043
G1 X159.811 Y165.558 E.00594
G1 X160.097 Y165.08 E.02116
G1 X160.097 Y163.379 E.06462
G1 X159.703 Y163.157 E.01719
G1 X159.703 Y158.83 E.16441
G1 X159.811 Y158.717 E.00594
G1 X160.079 Y158.29 E.01916
G1 X160.385 Y157.435 E.0345
G1 X160.396 Y157.303 E.00502
G1 X160.097 Y157.303 E.01137
G1 X160.097 Y156.538 E.02905
G1 X159.703 Y156.316 E.01719
G1 X159.703 Y154.398 E.07286
G1 X159.334 Y154.803 E.0208
G1 X159.334 Y152.346 E.09335
G1 X159.399 Y152.304 E.00294
G1 X159.811 Y151.876 E.02257
G1 X160.079 Y151.449 E.01916
G1 X160.385 Y150.594 E.0345
G1 X160.423 Y150.166 E.01631
G1 X160.17 Y149.738 E.01887
G1 X159.334 Y149.26 E.03658
G1 X159.334 Y150.854 E.06056
; WIPE_START
G1 X159.334 Y149.26 E-.60572
G1 X159.687 Y149.462 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.502 Y156.072 Z13.32 F60000
G1 X164.213 Y157.303 Z13.32
G1 Z12.92
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X162.619 Y157.303 E.06056
G1 X162.82 Y157.435 E.00913
M73 P71 R2
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
G1 X161.183 Y162.697 E.00502
G1 X165.297 Y162.697 E.15629
G1 X165.297 Y162.31 E.01471
G1 X164.921 Y161.71 E.02688
G1 X164.615 Y160.855 E.0345
G1 X164.578 Y160.428 E.01631
G1 X164.83 Y160 E.01887
G1 X165.297 Y159.682 E.02145
G1 X165.297 Y158.088 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 13.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X165.297 Y159.682 E-.60571
G1 X164.961 Y159.911 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 55/107
; update layer progress
M73 L55
M991 S0 P54 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z13.32 I-.783 J-.931 P1  F60000
G1 X160.806 Y163.407 Z13.32
G1 Z13.16
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11311
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.642 Y165.167 Z13.56 F60000
G1 Z13.16
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.41935
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X159.36 Y166.575 E.1045
G1 X159.36 Y165.878 E.03825
G1 X160.44 Y164.692 E.08799
G1 X160.44 Y163.995 E.03825
G1 X159.36 Y165.181 E.08799
G1 X159.36 Y164.484 E.03825
G1 X165.64 Y157.586 E.51181
G1 X165.64 Y158.283 E.03825
G1 X161.309 Y163.04 E.35295
G1 X161.944 Y163.04 E.03482
G1 X165.64 Y158.98 E.30122
G1 X165.64 Y159.677 E.03825
G1 X162.579 Y163.04 E.24949
G1 X163.213 Y163.04 E.03482
G1 X165.64 Y160.374 E.19776
G1 X165.64 Y161.072 E.03825
G1 X163.848 Y163.04 E.14603
G1 X164.483 Y163.04 E.03482
G1 X165.64 Y161.769 E.0943
G1 X165.64 Y162.466 E.03825
G1 X164.933 Y163.242 E.05759
M106 S0
; WIPE_START
G1 X165.64 Y162.466 E-.39889
G1 X165.64 Y161.769 E-.26494
G1 X165.469 Y161.956 E-.09617
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.372 Y168.396 Z13.56 F60000
G1 X160.466 Y169.82 Z13.56
G1 Z13.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
; LAYER_HEIGHT: 0.24
G1 F11292.473
M204 S8000
G1 X160.466 Y171.066 E.0473
G1 X160.117 Y171.066 E.01326
G1 X160.02 Y170.689 E.01476
G1 X159.675 Y170.262 E.02088
G1 X159.334 Y169.973 E.01695
G1 X159.334 Y168.379 E.06056
; WIPE_START
G1 X159.334 Y169.973 E-.60572
G1 X159.644 Y170.236 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.158 Y164.009 Z13.56 F60000
G1 Z13.16
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.41935
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X165.574 Y156.96 E.52299
G1 X164.94 Y156.96 E.03482
G1 X159.36 Y163.089 E.45476
G1 X159.36 Y162.392 E.03825
G1 X164.305 Y156.96 E.40302
G1 X163.67 Y156.96 E.03482
G1 X159.36 Y161.695 E.35129
G1 X159.36 Y160.998 E.03825
G1 X163.036 Y156.96 E.29956
G1 X162.401 Y156.96 E.03482
G1 X159.36 Y160.3 E.24783
G1 X159.36 Y159.603 E.03825
G1 X161.766 Y156.96 E.1961
G1 X161.132 Y156.96 E.03482
G1 X159.36 Y158.906 E.14437
G1 X159.36 Y158.209 E.03825
M73 P72 R2
G1 X160.497 Y156.96 E.09264
G1 X160.44 Y156.96 E.00313
G1 X160.44 Y156.326 E.03482
G1 X159.36 Y157.512 E.08799
G1 X159.36 Y156.814 E.03825
G1 X160.44 Y155.628 E.08799
G1 X160.44 Y154.931 E.03825
G1 X159.36 Y156.117 E.08799
G1 X159.36 Y155.42 E.03825
G1 X160.642 Y154.012 E.1045
M106 S0
; WIPE_START
G1 X159.36 Y155.42 E-.72372
G1 X159.36 Y155.515 E-.03628
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y154.033 Z13.56 F60000
G1 Z13.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
; LAYER_HEIGHT: 0.24
G1 F11292.473
M204 S8000
G1 X159.334 Y152.439 E.06056
G1 X159.495 Y152.304 E.00797
G1 X159.806 Y151.876 E.0201
G1 X160 Y151.449 E.01783
G1 X160.13 Y150.594 E.03286
G1 X160.02 Y150.166 E.01677
G1 X159.675 Y149.738 E.02088
G1 X159.334 Y149.45 E.01695
G1 X159.334 Y148.934 E.0196
G1 X160.412 Y148.934 E.04096
; CHANGE_LAYER
; Z_HEIGHT: 13.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y148.934 E-.40966
G1 X159.334 Y149.45 E-.19606
G1 X159.644 Y149.713 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 56/107
; update layer progress
M73 L56
M991 S0 P55 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z13.56 I-1.213 J.103 P1  F60000
G1 X160.806 Y163.407 Z13.56
G1 Z13.4
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11363
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y170.028 Z13.8 F60000
G1 Z13.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y171.066 E.03943
G1 X159.909 Y171.066 E.02113
G1 X159.74 Y170.689 E.01568
G1 X159.334 Y170.223 E.02349
G1 X159.334 Y166.267 E.15029
G1 X159.602 Y165.986 E.01473
G1 X159.83 Y165.558 E.01841
G1 X159.913 Y165.27 E.01142
G1 X159.913 Y164.233 E.03939
G1 X159.74 Y163.848 E.01603
G1 X159.334 Y163.382 E.02349
G1 X159.334 Y159.426 E.15029
G1 X159.602 Y159.145 E.01473
G1 X159.83 Y158.717 E.01841
G1 X159.913 Y158.429 E.01142
G1 X159.913 Y157.392 E.03939
G1 X159.74 Y157.007 E.01603
G1 X159.334 Y156.541 E.02349
G1 X159.334 Y152.585 E.15029
G1 X159.602 Y152.304 E.01473
G1 X159.83 Y151.876 E.01841
G1 X159.953 Y151.449 E.0169
G1 X159.99 Y151.021 E.0163
G1 X159.932 Y150.594 E.01639
G1 X159.74 Y150.166 E.01781
G1 X159.334 Y149.699 E.02349
G1 X159.334 Y148.934 E.02907
G1 X160.163 Y148.934 E.03149
; WIPE_START
G1 X159.334 Y148.934 E-.31499
G1 X159.334 Y149.699 E-.29073
G1 X159.601 Y150.006 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.36 Y154.72 Z13.8 F60000
G1 Z13.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.546304
G1 F9094.583
M204 S8000
G1 X160.36 Y156.776 E.09699
; WIPE_START
G1 X160.36 Y154.776 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.623 Y159.64 Z13.8 F60000
G1 Z13.4
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y156.977 E.09356
G1 X160.607 Y156.977 E.17621
; LINE_WIDTH: 0.441669
G1 F11533.582
G1 X160.525 Y156.93 E.00351
; LINE_WIDTH: 0.485019
G1 F10380.264
G1 X160.444 Y156.883 E.0039
; LINE_WIDTH: 0.528369
G1 F9436.634
G1 X160.362 Y156.836 E.00429
G1 X160.34 Y156.986 E.00692
; LINE_WIDTH: 0.485019
G1 F10380.264
G1 X160.318 Y157.137 E.00629
; LINE_WIDTH: 0.420586
G1 F12192.44
G1 X160.297 Y157.288 E.00535
G1 X160.297 Y162.712 E.1909
; LINE_WIDTH: 0.441046
G1 F11552.038
G1 X160.318 Y162.877 E.00618
; LINE_WIDTH: 0.483149
G1 F10425.235
G1 X160.339 Y163.042 E.00684
; LINE_WIDTH: 0.525253
G1 F9498.715
G1 X160.36 Y163.207 E.00751
G1 X160.442 Y163.146 E.00464
; LINE_WIDTH: 0.483149
G1 F10425.235
G1 X160.525 Y163.084 E.00423
; LINE_WIDTH: 0.420251
G1 F12203.51
G1 X160.607 Y163.023 E.00361
G1 X165.623 Y163.023 E.17634
G1 X165.623 Y159.7 E.11682
M204 S10000
G1 X165.255 Y159.64 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.255 Y157.345 E.08062
G1 X160.665 Y157.345 E.16123
G1 X160.665 Y162.655 E.18652
G1 X165.255 Y162.655 E.16123
G1 X165.255 Y159.7 E.10379
M204 S10000
G1 X164.886 Y159.64 F60000
G1 F12212.001
M204 S8000
G1 X164.886 Y157.714 E.06767
G1 X161.034 Y157.714 E.13534
G1 X161.034 Y162.286 E.16063
G1 X164.886 Y162.286 E.13534
G1 X164.886 Y159.7 E.09085
M204 S10000
G1 X164.518 Y159.64 F60000
G1 F12212.001
M204 S8000
G1 X164.518 Y158.082 E.05473
G1 X161.402 Y158.082 E.10945
G1 X161.402 Y161.918 E.13474
G1 X164.518 Y161.918 E.10945
G1 X164.518 Y159.7 E.0779
M204 S10000
G1 X164.149 Y159.64 F60000
G1 F12212.001
M204 S8000
G1 X164.149 Y158.451 E.04178
G1 X161.771 Y158.451 E.08356
G1 X161.771 Y161.549 E.10884
G1 X164.149 Y161.549 E.08356
G1 X164.149 Y159.7 E.06496
; WIPE_START
G1 X164.149 Y161.549 E-.7026
G1 X163.998 Y161.549 E-.0574
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.96 Y160.36 Z13.8 F60000
G1 Z13.4
G1 E.8 F1800
; LINE_WIDTH: 0.587484
G1 F8395.836
M204 S8000
G1 X162.96 Y159.7 E.03371
; WIPE_START
G1 X162.96 Y160.36 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.508 Y160.812 Z13.8 F60000
G1 Z13.4
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X163.412 Y160.812 E.03178
G1 X163.412 Y159.188 E.05706
G1 X162.508 Y159.188 E.03178
G1 X162.508 Y160.752 E.05495
M204 S10000
G1 X162.139 Y161.181 F60000
G1 F12212.001
M204 S8000
G1 X163.781 Y161.181 E.05767
G1 X163.781 Y158.819 E.08295
G1 X162.139 Y158.819 E.05767
G1 X162.139 Y161.121 E.08085
; WIPE_START
G1 X162.139 Y159.121 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.36 Y165.28 Z13.8 F60000
G1 Z13.4
G1 E.8 F1800
; LINE_WIDTH: 0.546304
G1 F9094.583
M204 S8000
G1 X160.36 Y163.267 E.09496
; CHANGE_LAYER
; Z_HEIGHT: 13.64
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F9094.583
G1 X160.36 Y165.267 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 57/107
; update layer progress
M73 L57
M991 S0 P56 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z13.8 I1.183 J.284 P1  F60000
G1 X160.806 Y163.407 Z13.8
G1 Z13.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11412
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
M73 P73 R2
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y170.194 Z14.04 F60000
G1 Z13.64
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y171.066 E.03312
G1 X159.743 Y171.066 E.02744
G1 X159.514 Y170.689 E.01674
G1 X159.334 Y170.493 E.01009
G1 X159.334 Y166.527 E.15071
G1 X159.441 Y166.414 E.00592
G1 X159.726 Y165.986 E.01951
G1 X159.88 Y165.558 E.01727
G1 X159.913 Y165.301 E.00986
G1 X159.904 Y164.703 E.02271
G1 X159.774 Y164.276 E.01697
G1 X159.514 Y163.848 E.01902
G1 X159.334 Y163.652 E.01009
G1 X159.334 Y159.686 E.15071
G1 X159.441 Y159.572 E.00592
G1 X159.726 Y159.145 E.01951
G1 X159.88 Y158.717 E.01727
G1 X159.913 Y158.46 E.00986
G1 X159.904 Y157.862 E.02271
G1 X159.774 Y157.435 E.01697
G1 X159.514 Y157.007 E.01902
G1 X159.334 Y156.811 E.01009
G1 X159.334 Y152.845 E.15071
G1 X159.441 Y152.731 E.00592
G1 X159.726 Y152.304 E.01951
G1 X159.88 Y151.876 E.01727
G1 X159.935 Y151.449 E.01638
G1 X159.904 Y151.021 E.01629
G1 X159.774 Y150.594 E.01697
G1 X159.514 Y150.166 E.01902
G1 X159.334 Y149.97 E.01009
G1 X159.334 Y148.934 E.03936
G1 X159.892 Y148.934 E.0212
; WIPE_START
G1 X159.334 Y148.934 E-.21206
G1 X159.334 Y149.97 E-.39365
G1 X159.514 Y150.166 E-.10094
G1 X159.587 Y150.286 E-.05334
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.36 Y154.72 Z14.04 F60000
G1 Z13.64
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.546304
G1 F9094.583
M204 S8000
G1 X160.36 Y156.776 E.09699
; WIPE_START
G1 X160.36 Y154.776 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.623 Y159.64 Z14.04 F60000
G1 Z13.64
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12000
M204 S8000
G1 X165.623 Y156.977 E.09356
G1 X160.607 Y156.977 E.17621
; LINE_WIDTH: 0.441669
G1 F11533.582
G1 X160.525 Y156.93 E.00351
; LINE_WIDTH: 0.485019
G1 F10380.264
G1 X160.444 Y156.883 E.0039
; LINE_WIDTH: 0.528369
G1 F9436.634
G1 X160.362 Y156.836 E.00429
G1 X160.34 Y156.986 E.00692
; LINE_WIDTH: 0.485019
G1 F10380.264
G1 X160.318 Y157.137 E.00629
; LINE_WIDTH: 0.420586
G1 F12000
G1 X160.297 Y157.288 E.00535
G1 X160.297 Y162.712 E.1909
; LINE_WIDTH: 0.441046
G1 F11552.038
G1 X160.318 Y162.877 E.00618
; LINE_WIDTH: 0.483149
G1 F10425.235
G1 X160.339 Y163.042 E.00684
; LINE_WIDTH: 0.525253
G1 F9498.715
G1 X160.36 Y163.207 E.00751
G1 X160.442 Y163.146 E.00464
; LINE_WIDTH: 0.483149
G1 F10425.235
G1 X160.525 Y163.084 E.00423
; LINE_WIDTH: 0.420251
G1 F12000
G1 X160.607 Y163.023 E.00361
G1 X165.623 Y163.023 E.17634
G1 X165.623 Y159.7 E.11682
M204 S10000
G1 X165.255 Y159.64 F60000
; LINE_WIDTH: 0.419994
G1 F12000
M204 S8000
G1 X165.255 Y157.345 E.08062
G1 X160.665 Y157.345 E.16123
G1 X160.665 Y162.655 E.18652
G1 X165.255 Y162.655 E.16123
G1 X165.255 Y159.7 E.10379
M204 S10000
G1 X164.886 Y159.64 F60000
G1 F12000
M204 S8000
G1 X164.886 Y157.714 E.06767
G1 X161.034 Y157.714 E.13534
G1 X161.034 Y162.286 E.16063
G1 X164.886 Y162.286 E.13534
G1 X164.886 Y159.7 E.09085
M204 S10000
G1 X164.518 Y159.64 F60000
G1 F12000
M204 S8000
G1 X164.518 Y158.082 E.05473
G1 X161.402 Y158.082 E.10945
G1 X161.402 Y161.918 E.13474
G1 X164.518 Y161.918 E.10945
G1 X164.518 Y159.7 E.0779
M204 S10000
G1 X164.149 Y159.64 F60000
G1 F12000
M204 S8000
G1 X164.149 Y158.451 E.04178
G1 X161.771 Y158.451 E.08356
G1 X161.771 Y161.549 E.10884
G1 X164.149 Y161.549 E.08356
G1 X164.149 Y159.7 E.06496
M204 S10000
G1 X163.781 Y159.64 F60000
G1 F12000
M204 S8000
G1 X163.781 Y158.819 E.02883
G1 X162.139 Y158.819 E.05767
G1 X162.139 Y161.181 E.08295
G1 X163.781 Y161.181 E.05767
G1 X163.781 Y159.7 E.05201
M204 S10000
G1 X163.412 Y159.64 F60000
G1 F12000
M204 S8000
G1 X163.412 Y159.188 E.01589
G1 X162.508 Y159.188 E.03178
G1 X162.508 Y160.812 E.05706
G1 X163.412 Y160.812 E.03178
G1 X163.412 Y159.7 E.03907
M204 S10000
G1 X162.96 Y160.36 F60000
; LINE_WIDTH: 0.587484
G1 F8395.836
M204 S8000
G1 X162.96 Y159.7 E.03371
; WIPE_START
G1 X162.96 Y160.36 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.36 Y165.28 Z14.04 F60000
G1 Z13.64
G1 E.8 F1800
; LINE_WIDTH: 0.546304
G1 F9094.583
M204 S8000
G1 X160.36 Y163.267 E.09496
; CHANGE_LAYER
; Z_HEIGHT: 13.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9094.583
G1 X160.36 Y165.267 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 58/107
; update layer progress
M73 L58
M991 S0 P57 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z14.04 I1.183 J.284 P1  F60000
G1 X160.806 Y163.407 Z14.04
G1 Z13.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.30394
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y156.593 E.30394
G1 X166.007 Y156.593 E.19756
G1 X166.007 Y163.407 E.25885
G1 X160.866 Y163.407 E.19528
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11459
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y170.334 Z14.28 F60000
G1 Z13.88
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y171.066 E.0278
G1 X159.603 Y171.066 E.03276
G1 X159.334 Y170.72 E.01663
G1 X159.334 Y166.78 E.14969
G1 X159.657 Y166.414 E.01854
G1 X159.873 Y165.986 E.01821
G1 X159.956 Y165.558 E.01655
G1 X159.956 Y165.534 E.00094
G1 X159.913 Y165.491 E.00228
G1 X159.913 Y164.999 E.01869
G1 X159.845 Y164.703 E.01154
G1 X159.643 Y164.276 E.01796
G1 X159.334 Y163.879 E.0191
G1 X159.334 Y159.939 E.14969
G1 X159.657 Y159.572 E.01854
G1 X159.873 Y159.145 E.01821
G1 X159.913 Y158.94 E.00794
G1 X159.913 Y158.158 E.0297
G1 X159.845 Y157.862 E.01154
G1 X159.643 Y157.435 E.01796
G1 X159.334 Y157.038 E.0191
G1 X159.334 Y153.098 E.14969
G1 X159.657 Y152.731 E.01854
G1 X159.873 Y152.304 E.01821
G1 X159.956 Y151.876 E.01655
G1 X159.944 Y151.449 E.01625
G1 X159.845 Y151.021 E.01667
G1 X159.643 Y150.594 E.01796
G1 X159.334 Y150.197 E.0191
G1 X159.334 Y148.934 E.04796
G1 X159.666 Y148.934 E.0126
; WIPE_START
G1 X159.334 Y148.934 E-.126
G1 X159.334 Y150.197 E-.47972
G1 X159.584 Y150.517 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.36 Y154.72 Z14.28 F60000
G1 Z13.88
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.546304
G1 F9094.583
M204 S8000
G1 X160.36 Y156.776 E.09699
; WIPE_START
G1 X160.36 Y154.776 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.623 Y159.64 Z14.28 F60000
G1 Z13.88
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12000
M204 S8000
G1 X165.623 Y156.977 E.09356
G1 X160.607 Y156.977 E.17621
; LINE_WIDTH: 0.441669
G1 F11533.582
G1 X160.525 Y156.93 E.00351
; LINE_WIDTH: 0.485019
G1 F10380.264
G1 X160.444 Y156.883 E.0039
; LINE_WIDTH: 0.528369
G1 F9436.634
G1 X160.362 Y156.836 E.00429
G1 X160.34 Y156.986 E.00692
; LINE_WIDTH: 0.485019
G1 F10380.264
G1 X160.318 Y157.137 E.00629
; LINE_WIDTH: 0.420586
G1 F12000
G1 X160.297 Y157.288 E.00535
G1 X160.297 Y162.712 E.1909
; LINE_WIDTH: 0.441046
G1 F11552.038
G1 X160.318 Y162.877 E.00618
; LINE_WIDTH: 0.483149
G1 F10425.235
G1 X160.339 Y163.042 E.00684
; LINE_WIDTH: 0.525253
G1 F9498.715
G1 X160.36 Y163.207 E.00751
G1 X160.442 Y163.146 E.00464
; LINE_WIDTH: 0.483149
G1 F10425.235
G1 X160.525 Y163.084 E.00423
; LINE_WIDTH: 0.420251
G1 F12000
G1 X160.607 Y163.023 E.00361
G1 X165.623 Y163.023 E.17634
G1 X165.623 Y159.7 E.11682
M204 S10000
G1 X165.255 Y159.64 F60000
; LINE_WIDTH: 0.419994
G1 F12000
M204 S8000
G1 X165.255 Y157.345 E.08062
G1 X160.665 Y157.345 E.16123
G1 X160.665 Y162.655 E.18652
G1 X165.255 Y162.655 E.16123
G1 X165.255 Y159.7 E.10379
M204 S10000
G1 X164.886 Y159.64 F60000
G1 F12000
M204 S8000
G1 X164.886 Y157.714 E.06767
G1 X161.034 Y157.714 E.13534
G1 X161.034 Y162.286 E.16063
G1 X164.886 Y162.286 E.13534
G1 X164.886 Y159.7 E.09085
M204 S10000
G1 X164.518 Y159.64 F60000
G1 F12000
M204 S8000
G1 X164.518 Y158.082 E.05473
G1 X161.402 Y158.082 E.10945
G1 X161.402 Y161.918 E.13474
G1 X164.518 Y161.918 E.10945
G1 X164.518 Y159.7 E.0779
M204 S10000
G1 X164.149 Y159.64 F60000
G1 F12000
M204 S8000
G1 X164.149 Y158.451 E.04178
G1 X161.771 Y158.451 E.08356
G1 X161.771 Y161.549 E.10884
G1 X164.149 Y161.549 E.08356
G1 X164.149 Y159.7 E.06496
M204 S10000
G1 X163.781 Y159.64 F60000
M73 P74 R2
G1 F12000
M204 S8000
G1 X163.781 Y158.819 E.02883
G1 X162.139 Y158.819 E.05767
G1 X162.139 Y161.181 E.08295
G1 X163.781 Y161.181 E.05767
G1 X163.781 Y159.7 E.05201
M204 S10000
G1 X163.412 Y159.64 F60000
G1 F12000
M204 S8000
G1 X163.412 Y159.188 E.01589
G1 X162.508 Y159.188 E.03178
G1 X162.508 Y160.812 E.05706
G1 X163.412 Y160.812 E.03178
G1 X163.412 Y159.7 E.03907
M204 S10000
G1 X162.96 Y160.36 F60000
; LINE_WIDTH: 0.587484
G1 F8395.836
M204 S8000
G1 X162.96 Y159.7 E.03371
; WIPE_START
G1 X162.96 Y160.36 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.36 Y165.28 Z14.28 F60000
G1 Z13.88
G1 E.8 F1800
; LINE_WIDTH: 0.546304
G1 F9094.583
M204 S8000
G1 X160.36 Y163.267 E.09496
; CHANGE_LAYER
; Z_HEIGHT: 14.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F9094.583
G1 X160.36 Y165.267 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 59/107
; update layer progress
M73 L59
M991 S0 P58 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z14.28 I.92 J.797 P1  F60000
G1 X164.668 Y160.291 Z14.28
G1 Z14.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X164.668 Y156.593 E.14046
G1 X166.007 Y156.593 E.05084
G1 X166.007 Y163.407 E.25885
G1 X164.668 Y163.407 E.05084
G1 X164.668 Y160.351 E.1161
; COOLING_NODE: 0
; WIPE_START
G1 X164.668 Y158.351 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.332 Y162.932 Z14.52 F60000
G1 Z14.12
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X160.332 Y165.308 E.0903
G1 X160.806 Y165.308 E.01804
G1 X160.806 Y171.407 E.23168
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y154.692 E.23168
G1 X160.332 Y154.692 E.01804
G1 X160.332 Y162.872 E.31078
; COOLING_NODE: 0
; WIPE_START
G1 X160.332 Y164.872 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.19 Y163.79 Z14.52 F60000
G1 Z14.12
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11503
M204 S5000
G1 X161.19 Y171.79 E.28106
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y156.21 E.28106
G1 X166.39 Y156.21 E.18269
G1 X166.39 Y163.79 E.2663
G1 X161.25 Y163.79 E.18058
; WIPE_START
G1 F12000
M204 S8000
G1 X161.235 Y165.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.103 Y162.972 Z14.52 F60000
G1 Z14.12
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.521354
G1 F9577.525
M204 S8000
G1 X165.572 Y162.972 E.02105
G1 X165.572 Y157.028 E.2663
G1 X165.103 Y157.028 E.02105
G1 X165.103 Y162.912 E.26361
; WIPE_START
G1 X165.103 Y160.912 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.449 Y157.159 Z14.52 F60000
G1 Z14.12
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X163.704 Y156.414 E.04002
G1 X163.561 Y156.271
G1 X162.998 Y156.271
G1 X163.141 Y156.414
G1 X164.449 Y157.722 E.0703
G1 X164.592 Y157.866
G1 X164.592 Y158.429
G1 X164.449 Y158.286
G1 X162.577 Y156.414 E.10058
G1 X162.434 Y156.271
G1 X161.87 Y156.271
G1 X162.014 Y156.414
G1 X164.449 Y158.85 E.13085
G1 X164.592 Y158.993
G1 X164.592 Y159.556
G1 X164.449 Y159.413
G1 X161.45 Y156.414 E.16113
G1 X160.986 Y155.95
G1 X160.551 Y155.515 E.02337
G1 X160.408 Y155.372
G1 X160.408 Y155.935
G1 X160.551 Y156.079
G1 X164.449 Y159.977 E.20944
G1 X164.592 Y160.12
G1 X164.592 Y160.683
G1 X164.449 Y160.54
G1 X160.551 Y156.642 E.20944
G1 X160.408 Y156.499
G1 X160.408 Y157.062
G1 X160.551 Y157.206
G1 X164.449 Y161.104 E.20944
G1 X164.592 Y161.247
G1 X164.592 Y161.811
G1 X164.449 Y161.667
G1 X160.551 Y157.769 E.20944
G1 X160.408 Y157.626
G1 X160.408 Y158.19
G1 X160.551 Y158.333
G1 X164.449 Y162.231 E.20944
G1 X164.592 Y162.374
G1 X164.592 Y162.938
G1 X164.449 Y162.794
G1 X160.551 Y158.896 E.20944
G1 X160.408 Y158.753
G1 X160.408 Y159.317
G1 X160.551 Y159.46
G1 X164.449 Y163.358 E.20944
G1 X164.592 Y163.501
G1 X164.257 Y163.729
G1 X164.113 Y163.586
G1 X160.551 Y160.023 E.19141
G1 X160.408 Y159.88
G1 X160.408 Y160.444
G1 X160.551 Y160.587
G1 X163.55 Y163.586 E.16113
G1 X163.693 Y163.729
G1 X163.129 Y163.729
G1 X162.986 Y163.586
G1 X160.551 Y161.151 E.13085
G1 X160.408 Y161.007
G1 X160.408 Y161.571
G1 X160.551 Y161.714
G1 X162.423 Y163.586 E.10057
G1 X162.566 Y163.729
G1 X162.002 Y163.729
G1 X161.859 Y163.586
G1 X160.551 Y162.278 E.07029
G1 X160.408 Y162.134
G1 X160.408 Y162.698
G1 X160.551 Y162.841
G1 X161.296 Y163.586 E.04001
G1 X161.439 Y163.729
G1 X161.129 Y163.983
G1 X160.986 Y163.84
G1 X160.551 Y163.405 E.02337
G1 X160.408 Y163.262
G1 X160.408 Y163.825
G1 X160.551 Y163.968
G1 X160.986 Y164.403 E.02337
M204 S10000
G1 X160.913 Y164.663 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.215072
G1 F15000
M204 S8000
G1 X160.531 Y164.379 E.00743
M204 S10000
G1 X161.006 Y164.538 F60000
; LINE_WIDTH: 0.203808
G1 F15000
M204 S8000
G1 X160.894 Y164.593 E.00181
; LINE_WIDTH: 0.174176
G1 X160.615 Y164.555 E.0033
; WIPE_START
G1 X160.894 Y164.593 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y168.641 Z14.52 F60000
G1 Z14.12
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.047 E.06056
G1 X159.558 Y166.841 E.01154
G1 X159.913 Y166.414 E.02111
G1 X160.055 Y165.986 E.01712
G1 X160.025 Y165.649 E.01284
G1 X159.991 Y165.649 E.00132
G1 X159.98 Y165.131 E.01971
G1 X159.811 Y164.703 E.01746
G1 X159.531 Y164.276 E.01943
G1 X159.334 Y164.095 E.01013
G1 X159.334 Y160.206 E.14777
G1 X159.558 Y160 E.01154
G1 X159.913 Y159.572 E.02111
G1 X159.991 Y159.339 E.00936
G1 X159.98 Y158.29 E.03985
G1 X159.811 Y157.862 E.01746
G1 X159.531 Y157.435 E.01943
G1 X159.334 Y157.254 E.01013
G1 X159.334 Y153.365 E.14777
G1 X159.558 Y153.159 E.01154
G1 X159.913 Y152.731 E.02111
G1 X160.055 Y152.304 E.01712
G1 X159.98 Y151.449 E.03261
G1 X159.811 Y151.021 E.01746
G1 X159.531 Y150.594 E.01943
G1 X159.334 Y150.413 E.01013
G1 X159.334 Y148.934 E.05618
G1 X159.45 Y148.934 E.00438
; CHANGE_LAYER
; Z_HEIGHT: 14.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X159.334 Y148.934 E-.04381
G1 X159.334 Y150.413 E-.5619
G1 X159.531 Y150.594 E-.10132
G1 X159.607 Y150.71 E-.05297
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 60/107
; update layer progress
M73 L60
M991 S0 P59 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z14.52 I-1.207 J.156 P1  F60000
G1 X160.806 Y160 Z14.52
G1 Z14.36
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11545
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
M73 P75 R2
G1 X160.36 Y165.28 Z14.76 F60000
G1 Z14.36
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.546404
G1 F9092.747
M204 S8000
G1 X160.36 Y154.78 E.49546
; WIPE_START
G1 X160.36 Y156.78 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.373 Y149.211 Z14.76 F60000
G1 X159.337 Y148.934 Z14.76
G1 Z14.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y150.526 E.06046
G1 X159.432 Y150.594 E.0045
G1 X159.806 Y151.021 E.02159
G1 X160.047 Y151.449 E.01865
G1 X160.287 Y152.304 E.03375
G1 X160.259 Y152.731 E.01628
G1 X159.951 Y153.159 E.02002
G1 X159.334 Y153.59 E.02859
G1 X159.334 Y157.367 E.14349
G1 X159.432 Y157.435 E.0045
G1 X159.806 Y157.862 E.02159
G1 X159.913 Y158.053 E.0083
G1 X159.913 Y160.027 E.075
G1 X159.334 Y160.431 E.02682
G1 X159.334 Y164.208 E.14349
G1 X159.432 Y164.276 E.0045
G1 X159.806 Y164.703 E.02159
G1 X159.913 Y164.894 E.0083
G1 X159.913 Y165.491 E.0227
G1 X160.149 Y165.727 E.01267
G1 X160.214 Y165.727 E.00249
G1 X160.287 Y165.986 E.01022
G1 X160.259 Y166.414 E.01628
G1 X159.951 Y166.841 E.02002
G1 X159.334 Y167.272 E.02859
G1 X159.334 Y168.866 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y167.272 E-.60571
G1 X159.667 Y167.04 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.702 Y160.036 Z14.76 F60000
G1 X164.193 Y156.593 Z14.76
G1 Z14.36
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11545
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z14.76 F60000
G1 Z14.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 14.6
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 61/107
; update layer progress
M73 L61
M991 S0 P60 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z14.76 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z14.76
G1 Z14.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11585
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.36 Y165.28 Z15 F60000
G1 Z14.6
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.546404
G1 F9092.747
M204 S8000
G1 X160.36 Y154.78 E.49546
; WIPE_START
G1 X160.36 Y156.78 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.361 Y149.213 Z15 F60000
G1 X159.334 Y149.008 Z15
G1 Z14.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y150.602 E.06056
G1 X159.507 Y150.714 E.00781
G1 X159.935 Y151.14 E.02295
G1 X160.362 Y151.828 E.03076
G1 X160.466 Y152.026 E.00847
G1 X160.466 Y153.51 E.05641
G1 X160.362 Y153.459 E.00439
G1 X159.935 Y153.527 E.01645
G1 X159.334 Y153.759 E.02445
G1 X159.334 Y157.443 E.13997
G1 X159.507 Y157.555 E.00781
G1 X159.913 Y157.96 E.0218
G1 X159.913 Y160.376 E.09178
G1 X159.334 Y160.6 E.02358
G1 X159.334 Y164.284 E.13997
G1 X159.507 Y164.396 E.00781
G1 X159.913 Y164.801 E.0218
G1 X159.913 Y165.491 E.02621
G1 X160.149 Y165.727 E.01267
G1 X160.466 Y165.727 E.01203
G1 X160.466 Y167.192 E.05568
G1 X160.362 Y167.141 E.00439
G1 X159.935 Y167.209 E.01645
G1 X159.334 Y167.441 E.02445
G1 X159.334 Y169.035 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y167.441 E-.60571
G1 X159.713 Y167.294 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.661 Y160.254 Z15 F60000
G1 X164.193 Y156.593 Z15
G1 Z14.6
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11585
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z15 F60000
G1 Z14.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 14.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 62/107
; update layer progress
M73 L62
M991 S0 P61 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z15
G1 Z14.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11622
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y169.172 Z15.24 F60000
G1 Z14.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.578 E.06056
G1 X159.935 Y167.473 E.02315
G1 X160.362 Y167.569 E.01665
G1 X160.466 Y167.651 E.00502
G1 X160.466 Y165.377 E.08642
G1 X159.935 Y164.728 E.03183
G1 X159.507 Y164.405 E.02036
G1 X159.334 Y164.323 E.00726
M73 P76 R2
G1 X159.334 Y160.737 E.13625
G1 X159.935 Y160.632 E.02315
G1 X160.362 Y160.728 E.01665
G1 X160.466 Y160.81 E.00502
G1 X160.466 Y158.536 E.08642
G1 X159.935 Y157.887 E.03183
G1 X159.507 Y157.564 E.02036
G1 X159.334 Y157.482 E.00726
G1 X159.334 Y153.896 E.13625
G1 X159.935 Y153.791 E.02315
G1 X160.362 Y153.887 E.01665
G1 X160.466 Y153.969 E.00502
G1 X160.466 Y151.695 E.08642
G1 X159.935 Y151.046 E.03183
G1 X159.507 Y150.723 E.02036
G1 X159.334 Y150.641 E.00726
G1 X159.334 Y149.047 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y150.641 E-.60571
G1 X159.507 Y150.723 E-.0726
G1 X159.679 Y150.853 E-.08169
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z15.24 F60000
G1 Z14.84
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11622
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z15.24 F60000
G1 Z14.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 15.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 63/107
; update layer progress
M73 L63
M991 S0 P62 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15.24 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z15.24
G1 Z15.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11656
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y169.24 Z15.48 F60000
G1 Z15.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.646 E.06056
G1 X159.507 Y167.628 E.0066
G1 X159.935 Y167.676 E.01635
G1 X160.362 Y167.859 E.01768
G1 X160.466 Y167.948 E.00517
G1 X160.466 Y165.141 E.10665
G1 X159.935 Y164.623 E.02817
G1 X159.507 Y164.385 E.01859
G1 X159.334 Y164.332 E.00686
G1 X159.334 Y160.805 E.13397
G1 X159.507 Y160.787 E.0066
G1 X159.935 Y160.835 E.01635
G1 X160.362 Y161.018 E.01768
G1 X160.466 Y161.107 E.00517
G1 X160.466 Y158.3 E.10665
G1 X159.935 Y157.782 E.02817
G1 X159.507 Y157.544 E.01859
G1 X159.334 Y157.49 E.00686
G1 X159.334 Y153.964 E.13397
G1 X159.507 Y153.946 E.0066
G1 X159.935 Y153.994 E.01635
G1 X160.362 Y154.177 E.01768
G1 X160.466 Y154.266 E.00517
G1 X160.466 Y151.459 E.10665
G1 X159.935 Y150.941 E.02817
G1 X159.507 Y150.703 E.01859
G1 X159.334 Y150.649 E.00686
G1 X159.334 Y149.055 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y150.649 E-.60571
G1 X159.507 Y150.703 E-.06865
G1 X159.704 Y150.812 E-.08564
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z15.48 F60000
G1 Z15.08
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11656
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z15.48 F60000
G1 Z15.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 15.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 64/107
; update layer progress
M73 L64
M991 S0 P63 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15.48 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z15.48
G1 Z15.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11689
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y169.303 Z15.72 F60000
G1 Z15.32
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.709 E.06056
G1 X159.507 Y167.718 E.00657
G1 X159.935 Y167.838 E.01688
G1 X160.362 Y168.09 E.01885
G1 X160.466 Y168.184 E.00531
G1 X160.466 Y164.893 E.12502
G1 X160.362 Y164.795 E.00543
G1 X159.935 Y164.501 E.0197
G1 X159.507 Y164.338 E.01739
G1 X159.334 Y164.312 E.00663
G1 X159.334 Y160.868 E.13088
G1 X159.507 Y160.877 E.00657
G1 X159.935 Y160.997 E.01688
G1 X160.362 Y161.249 E.01885
G1 X160.466 Y161.343 E.00531
G1 X160.466 Y158.052 E.12502
G1 X160.362 Y157.954 E.00543
G1 X159.935 Y157.66 E.0197
G1 X159.507 Y157.497 E.01739
G1 X159.334 Y157.471 E.00663
G1 X159.334 Y154.026 E.13088
G1 X159.507 Y154.036 E.00657
G1 X159.935 Y154.156 E.01688
G1 X160.362 Y154.408 E.01885
G1 X160.466 Y154.502 E.00531
G1 X160.466 Y151.211 E.12502
G1 X160.362 Y151.113 E.00543
G1 X159.935 Y150.819 E.0197
G1 X159.507 Y150.656 E.01739
G1 X159.334 Y150.63 E.00663
G1 X159.334 Y149.036 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y150.63 E-.60571
G1 X159.507 Y150.656 E-.06632
G1 X159.723 Y150.739 E-.08797
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z15.72 F60000
G1 Z15.32
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11689
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
M73 P77 R2
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z15.72 F60000
G1 Z15.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 15.56
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 65/107
; update layer progress
M73 L65
M991 S0 P64 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15.72 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z15.72
G1 Z15.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11718
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.506 Y169.542 Z15.96 F60000
G1 X160.466 Y169.992 Z15.96
G1 Z15.56
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y168.398 E.06056
G1 X160.362 Y168.295 E.00554
G1 X159.935 Y167.972 E.02035
G1 X159.507 Y167.78 E.01781
G1 X159.334 Y167.744 E.0067
G1 X159.334 Y164.267 E.1321
G1 X159.507 Y164.265 E.00656
G1 X159.935 Y164.357 E.01662
G1 X160.362 Y164.583 E.01836
G1 X160.466 Y164.674 E.00524
G1 X160.466 Y161.557 E.11842
G1 X160.362 Y161.454 E.00554
G1 X159.935 Y161.131 E.02035
G1 X159.507 Y160.939 E.01781
G1 X159.334 Y160.903 E.0067
G1 X159.334 Y157.426 E.1321
G1 X159.507 Y157.424 E.00656
G1 X159.935 Y157.516 E.01662
G1 X160.362 Y157.741 E.01836
G1 X160.466 Y157.833 E.00524
G1 X160.466 Y154.716 E.11842
G1 X160.362 Y154.613 E.00554
G1 X159.935 Y154.29 E.02035
G1 X159.507 Y154.098 E.01781
G1 X159.334 Y154.062 E.0067
G1 X159.334 Y150.585 E.1321
G1 X159.507 Y150.583 E.00656
G1 X159.935 Y150.675 E.01662
G1 X160.362 Y150.9 E.01836
G1 X160.466 Y150.992 E.00524
G1 X160.466 Y149.398 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y150.992 E-.60572
G1 X160.362 Y150.9 E-.05244
G1 X160.125 Y150.776 E-.10184
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z15.96 F60000
G1 Z15.56
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11718
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z15.96 F60000
G1 Z15.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 15.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 66/107
; update layer progress
M73 L66
M991 S0 P65 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z15.96 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z15.96
G1 Z15.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11746
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.363 Y169.351 Z16.2 F60000
G1 X159.334 Y169.467 Z16.2
G1 Z15.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y171.061 E.06056
G1 X159.935 Y171.022 E.02285
G1 X160.058 Y171.066 E.00497
G1 X160.466 Y171.066 E.01549
G1 X160.466 Y168.648 E.09184
G1 X159.935 Y168.087 E.02935
G1 X159.507 Y167.817 E.01922
G1 X159.334 Y167.752 E.007
G1 X159.334 Y164.22 E.1342
G1 X159.935 Y164.181 E.02285
G1 X160.362 Y164.333 E.01725
G1 X160.466 Y164.42 E.00512
G1 X160.466 Y161.807 E.09926
G1 X159.935 Y161.246 E.02935
G1 X159.507 Y160.976 E.01922
G1 X159.334 Y160.911 E.007
G1 X159.334 Y157.379 E.1342
G1 X159.935 Y157.34 E.02285
G1 X160.362 Y157.492 E.01725
G1 X160.466 Y157.579 E.00512
G1 X160.466 Y154.966 E.09926
G1 X159.935 Y154.405 E.02935
G1 X159.507 Y154.135 E.01922
G1 X159.334 Y154.07 E.007
G1 X159.334 Y150.538 E.1342
G1 X159.935 Y150.498 E.02285
G1 X160.362 Y150.651 E.01725
G1 X160.466 Y150.738 E.00512
G1 X160.466 Y149.144 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y150.738 E-.60572
G1 X160.362 Y150.651 E-.0512
G1 X160.107 Y150.56 E-.10309
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z16.2 F60000
G1 Z15.8
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11746
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z16.2 F60000
G1 Z15.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 16.04
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 67/107
; update layer progress
M73 L67
M991 S0 P66 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
M73 P78 R2
G3 Z16.2 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z16.2
G1 Z16.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11772
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.636 Y154.328 Z16.44 F60000
G1 X160.466 Y151.992 Z16.44
G1 Z16.04
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y150.398 E.06056
G1 X160.362 Y150.321 E.0049
G1 X159.935 Y150.274 E.01634
G1 X159.334 Y150.427 E.02353
G1 X159.334 Y154.05 E.13767
G1 X159.507 Y154.144 E.00746
G1 X159.935 Y154.505 E.02127
G1 X160.466 Y155.234 E.03424
G1 X160.466 Y157.239 E.07618
G1 X160.362 Y157.162 E.0049
G1 X159.935 Y157.115 E.01634
G1 X159.334 Y157.268 E.02353
G1 X159.334 Y160.891 E.13767
G1 X159.507 Y160.985 E.00746
G1 X159.935 Y161.346 E.02127
G1 X160.466 Y162.075 E.03424
G1 X160.466 Y164.08 E.07618
G1 X160.362 Y164.003 E.0049
G1 X159.935 Y163.956 E.01634
G1 X159.334 Y164.109 E.02353
G1 X159.334 Y167.732 E.13767
G1 X159.507 Y167.826 E.00746
G1 X159.935 Y168.187 E.02127
G1 X160.466 Y168.916 E.03424
G1 X160.466 Y170.921 E.07618
G1 X160.362 Y170.844 E.0049
G1 X159.935 Y170.797 E.01634
G1 X159.334 Y170.95 E.02353
G1 X159.334 Y169.356 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y170.95 E-.60572
G1 X159.728 Y170.85 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.009 Y163.566 Z16.44 F60000
G1 X164.193 Y156.593 Z16.44
G1 Z16.04
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11772
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z16.44 F60000
G1 Z16.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 16.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 68/107
; update layer progress
M73 L68
M991 S0 P67 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z16.44 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z16.44
G1 Z16.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11795
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.677 Y154.325 Z16.68 F60000
G1 X160.466 Y151.191 Z16.68
G1 Z16.28
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y149.597 E.06056
G1 X160.417 Y149.738 E.00567
G1 X159.51 Y150.166 E.0381
G1 X159.334 Y150.269 E.00773
G1 X159.334 Y153.989 E.14134
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
G1 X160.466 Y162.584 E.0359
G1 X160.466 Y163.279 E.02644
G1 X160.417 Y163.421 E.00567
G1 X159.51 Y163.848 E.0381
G1 X159.334 Y163.951 E.00773
G1 X159.334 Y167.671 E.14134
G1 X159.818 Y168.124 E.02516
G1 X160.105 Y168.551 E.01955
G1 X160.466 Y169.425 E.0359
G1 X160.466 Y170.12 E.02644
G1 X160.417 Y170.262 E.00567
G1 X159.51 Y170.689 E.0381
G1 X159.334 Y170.792 E.00773
G1 X159.334 Y169.198 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y170.792 E-.60572
G1 X159.51 Y170.689 E-.07734
G1 X159.693 Y170.603 E-.07694
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.027 Y163.336 Z16.68 F60000
G1 X164.193 Y156.593 Z16.68
G1 Z16.28
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11795
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z16.68 F60000
G1 Z16.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 16.52
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 69/107
; update layer progress
M73 L69
M991 S0 P68 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z16.68 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z16.68
G1 Z16.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11817
M204 S5000
G1 X161.19 Y171.79 E.41421
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

M73 P79 R2
G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y169.012 Z16.92 F60000
G1 Z16.52
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y170.606 E.06056
G1 X159.77 Y170.262 E.02112
G1 X160.106 Y169.834 E.02065
G1 X160.188 Y169.406 E.01654
G1 X160.016 Y168.551 E.03313
G1 X159.804 Y168.124 E.01813
G1 X159.47 Y167.696 E.02063
G1 X159.334 Y167.589 E.00655
G1 X159.334 Y163.765 E.14528
G1 X159.77 Y163.421 E.02112
G1 X160.106 Y162.993 E.02065
G1 X160.188 Y162.565 E.01654
G1 X160.016 Y161.71 E.03313
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
G1 X159.334 Y153.907 E.00655
G1 X159.334 Y150.083 E.14528
G1 X159.77 Y149.738 E.02112
G1 X160.106 Y149.311 E.02065
G1 X160.178 Y148.934 E.01456
G1 X160.466 Y148.934 E.01093
G1 X160.466 Y150.241 E.04963
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y148.934 E-.49641
G1 X160.178 Y148.934 E-.10931
G1 X160.106 Y149.311 E-.14567
G1 X160.092 Y149.329 E-.00862
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.844 Y155.975 Z16.92 F60000
G1 X164.193 Y156.593 Z16.92
G1 Z16.52
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11817
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z16.92 F60000
G1 Z16.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 16.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 70/107
; update layer progress
M73 L70
M991 S0 P69 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z16.92 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z16.92
G1 Z16.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11836
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.727 Y154.322 Z17.16 F60000
G1 X160.466 Y150.02 Z17.16
G1 Z16.76
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y148.934 E.04125
G1 X159.957 Y148.934 E.01931
G1 X159.804 Y149.311 E.01544
G1 X159.334 Y149.845 E.027
G1 X159.334 Y153.775 E.14933
G1 X159.573 Y154.014 E.01284
G1 X159.822 Y154.442 E.01878
G1 X159.962 Y154.869 E.0171
G1 X159.978 Y155.724 E.03249
G1 X159.804 Y156.152 E.01754
G1 X159.334 Y156.686 E.027
G1 X159.334 Y160.616 E.14933
G1 X159.573 Y160.855 E.01284
G1 X159.822 Y161.283 E.01878
G1 X159.962 Y161.71 E.0171
G1 X159.978 Y162.565 E.03249
G1 X159.804 Y162.993 E.01754
G1 X159.334 Y163.527 E.027
G1 X159.334 Y167.457 E.14933
G1 X159.573 Y167.696 E.01284
G1 X159.822 Y168.124 E.01878
G1 X159.962 Y168.551 E.0171
G1 X159.978 Y169.406 E.03249
G1 X159.804 Y169.834 E.01754
G1 X159.334 Y170.368 E.027
G1 X159.334 Y171.066 E.02651
G1 X160.231 Y171.066 E.03405
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.34052
G1 X159.334 Y170.368 E-.2652
G1 X159.603 Y170.063 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.065 Y162.838 Z17.16 F60000
G1 X164.193 Y156.593 Z17.16
G1 Z16.76
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11836
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z17.16 F60000
G1 Z16.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 17
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 71/107
; update layer progress
M73 L71
M991 S0 P70 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z17.16 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z17.16
G1 Z17
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11854
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.734 Y154.321 Z17.4 F60000
G1 X160.466 Y149.845 Z17.4
G1 Z17
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y148.934 E.0346
M73 P80 R2
G1 X159.782 Y148.934 E.02596
G1 X159.568 Y149.311 E.01646
G1 X159.334 Y149.57 E.01325
G1 X159.334 Y153.529 E.15041
G1 X159.693 Y154.014 E.02291
G1 X159.865 Y154.442 E.01752
G1 X159.937 Y154.869 E.01647
G1 X159.923 Y155.297 E.01625
G1 X159.811 Y155.724 E.01679
G1 X159.568 Y156.152 E.01869
G1 X159.334 Y156.411 E.01325
G1 X159.334 Y160.37 E.15041
G1 X159.693 Y160.855 E.02291
G1 X159.865 Y161.283 E.01752
G1 X159.937 Y161.71 E.01647
G1 X159.923 Y162.138 E.01625
G1 X159.811 Y162.565 E.01679
G1 X159.568 Y162.993 E.01869
G1 X159.334 Y163.252 E.01325
G1 X159.334 Y167.211 E.15041
G1 X159.693 Y167.696 E.02291
G1 X159.865 Y168.124 E.01752
G1 X159.937 Y168.551 E.01647
G1 X159.923 Y168.979 E.01625
G1 X159.811 Y169.406 E.01679
G1 X159.568 Y169.834 E.01869
G1 X159.334 Y170.093 E.01325
G1 X159.334 Y171.066 E.03695
G1 X159.956 Y171.066 E.02361
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.23619
G1 X159.334 Y170.093 E-.36953
G1 X159.568 Y169.834 E-.13252
G1 X159.596 Y169.784 E-.02176
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.108 Y162.577 Z17.4 F60000
G1 X164.193 Y156.593 Z17.4
G1 Z17
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
M73 P80 R1
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11854
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z17.4 F60000
G1 Z17
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 17.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 72/107
; update layer progress
M73 L72
M991 S0 P71 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z17.4 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z17.4
G1 Z17.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11870
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.739 Y154.321 Z17.64 F60000
G1 X160.466 Y149.7 Z17.64
G1 Z17.24
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y148.934 E.02907
G1 X159.637 Y148.934 E.03149
G1 X159.334 Y149.338 E.01916
G1 X159.334 Y153.289 E.15012
G1 X159.6 Y153.587 E.01513
G1 X159.833 Y154.014 E.01851
G1 X159.935 Y154.442 E.01669
G1 X159.939 Y154.869 E.01625
G1 X159.857 Y155.297 E.01654
G1 X159.674 Y155.724 E.01767
G1 X159.334 Y156.179 E.02156
G1 X159.334 Y160.13 E.15012
G1 X159.6 Y160.428 E.01513
G1 X159.833 Y160.855 E.01851
G1 X159.935 Y161.283 E.01669
G1 X159.939 Y161.71 E.01625
G1 X159.857 Y162.138 E.01654
G1 X159.674 Y162.565 E.01767
G1 X159.334 Y163.02 E.02156
G1 X159.334 Y166.972 E.15012
G1 X159.6 Y167.269 E.01513
G1 X159.833 Y167.696 E.01851
G1 X159.935 Y168.124 E.01669
G1 X159.939 Y168.551 E.01624
G1 X159.857 Y168.979 E.01654
G1 X159.674 Y169.406 E.01767
G1 X159.334 Y169.861 E.02156
G1 X159.334 Y171.066 E.04576
G1 X159.724 Y171.066 E.0148
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.14804
G1 X159.334 Y169.861 E-.45768
G1 X159.577 Y169.536 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.141 Y162.347 Z17.64 F60000
G1 X164.193 Y156.593 Z17.64
G1 Z17.24
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11870
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z17.64 F60000
G1 Z17.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 17.48
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 73/107
; update layer progress
M73 L73
M991 S0 P72 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z17.64 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z17.64
G1 Z17.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11885
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.864 Y154.424 Z17.88 F60000
G1 X159.334 Y151.422 Z17.88
G1 Z17.48
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y153.016 E.06056
G1 X159.482 Y153.159 E.00781
G1 X159.842 Y153.587 E.02125
G1 X160.005 Y154.014 E.01738
G1 X159.968 Y154.869 E.03252
G1 X159.817 Y155.297 E.01722
G1 X159.558 Y155.724 E.01901
G1 X159.334 Y155.941 E.01182
G1 X159.334 Y159.857 E.14877
G1 X159.482 Y160 E.00781
G1 X159.842 Y160.428 E.02125
G1 X160.005 Y160.855 E.01738
G1 X159.968 Y161.71 E.03252
G1 X159.817 Y162.138 E.01722
G1 X159.558 Y162.565 E.01901
G1 X159.334 Y162.782 E.01182
G1 X159.334 Y166.698 E.14877
G1 X159.482 Y166.841 E.00781
G1 X159.842 Y167.269 E.02125
G1 X160.005 Y167.696 E.01738
G1 X159.968 Y168.551 E.03252
G1 X159.817 Y168.979 E.01722
G1 X159.558 Y169.406 E.01901
G1 X159.334 Y169.623 E.01182
G1 X159.334 Y171.066 E.0548
G1 X159.486 Y171.066 E.00576
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.05762
G1 X159.334 Y169.623 E-.5481
G1 X159.558 Y169.406 E-.1182
G1 X159.607 Y169.325 E-.03609
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.194 Y162.145 Z17.88 F60000
G1 X164.193 Y156.593 Z17.88
G1 Z17.48
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
M73 P81 R1
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11885
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z17.88 F60000
G1 Z17.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 17.72
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 74/107
; update layer progress
M73 L74
M991 S0 P73 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z17.88 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z17.88
G1 Z17.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11898
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.892 Y154.419 Z18.12 F60000
G1 X159.334 Y151.188 Z18.12
G1 Z17.72
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y152.782 E.06056
G1 X159.831 Y153.159 E.02368
G1 X160.159 Y153.587 E.02047
G1 X160.223 Y154.014 E.01642
G1 X160.027 Y154.869 E.03333
G1 X159.804 Y155.297 E.01831
G1 X159.456 Y155.724 E.02097
G1 X159.334 Y155.816 E.00577
G1 X159.334 Y159.623 E.14464
G1 X159.831 Y160 E.02368
G1 X160.159 Y160.428 E.02047
G1 X160.223 Y160.855 E.01642
G1 X160.027 Y161.71 E.03333
G1 X159.804 Y162.138 E.01831
G1 X159.456 Y162.565 E.02097
G1 X159.334 Y162.657 E.00577
G1 X159.334 Y166.464 E.14464
G1 X159.831 Y166.841 E.02368
G1 X160.159 Y167.269 E.02047
G1 X160.223 Y167.696 E.01642
G1 X160.027 Y168.551 E.03333
G1 X159.804 Y168.979 E.01831
G1 X159.456 Y169.406 E.02097
G1 X159.334 Y169.498 E.00577
G1 X159.334 Y171.066 E.05954
G1 X159.361 Y171.066 E.00102
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.01016
G1 X159.334 Y169.498 E-.59556
G1 X159.456 Y169.406 E-.05774
G1 X159.616 Y169.21 E-.09654
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.219 Y162.035 Z18.12 F60000
G1 X164.193 Y156.593 Z18.12
G1 Z17.72
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11898
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z18.12 F60000
G1 Z17.72
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 17.96
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 75/107
; update layer progress
M73 L75
M991 S0 P74 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z18.12 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z18.12
G1 Z17.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11910
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.913 Y154.415 Z18.36 F60000
G1 X159.334 Y151.008 Z18.36
G1 Z17.96
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y152.602 E.06056
G1 X159.935 Y152.871 E.02499
G1 X160.362 Y153.015 E.01714
G1 X160.466 Y153.026 E.00395
G1 X160.466 Y154.11 E.04119
G1 X160.362 Y154.381 E.01103
G1 X159.935 Y155.155 E.03359
G1 X159.507 Y155.612 E.02378
G1 X159.334 Y155.732 E.00798
G1 X159.334 Y159.443 E.141
G1 X159.935 Y159.712 E.02499
G1 X160.362 Y159.856 E.01714
G1 X160.466 Y159.867 E.00395
G1 X160.466 Y160.951 E.04119
G1 X160.362 Y161.222 E.01103
G1 X159.935 Y161.996 E.03359
G1 X159.507 Y162.453 E.02378
G1 X159.334 Y162.573 E.00798
G1 X159.334 Y166.284 E.141
G1 X159.935 Y166.553 E.02499
G1 X160.362 Y166.697 E.01714
G1 X160.466 Y166.708 E.00395
G1 X160.466 Y167.792 E.04119
G1 X160.362 Y168.063 E.01103
G1 X159.935 Y168.837 E.03359
G1 X159.507 Y169.294 E.02378
G1 X159.334 Y169.414 E.00798
G1 X159.334 Y171.008 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y169.414 E-.60571
G1 X159.507 Y169.294 E-.07979
G1 X159.641 Y169.151 E-.0745
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.242 Y161.976 Z18.36 F60000
G1 X164.193 Y156.593 Z18.36
G1 Z17.96
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11910
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z18.36 F60000
G1 Z17.96
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
M73 P82 R1
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 18.2
; LAYER_HEIGHT: 0.240002
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 76/107
; update layer progress
M73 L76
M991 S0 P75 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z18.36 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z18.36
G1 Z18.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11921
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.93 Y154.412 Z18.6 F60000
G1 X159.334 Y150.858 Z18.6
G1 Z18.2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y152.452 E.06056
G1 X159.935 Y152.587 E.02338
G1 X160.362 Y152.521 E.01644
G1 X160.466 Y152.442 E.00495
G1 X160.466 Y154.551 E.08014
G1 X159.935 Y155.247 E.03326
G1 X159.507 Y155.594 E.02092
G1 X159.334 Y155.683 E.00738
G1 X159.334 Y159.293 E.13714
G1 X159.935 Y159.428 E.02338
G1 X160.362 Y159.362 E.01644
G1 X160.466 Y159.283 E.00495
G1 X160.466 Y161.392 E.08014
G1 X159.935 Y162.088 E.03326
G1 X159.507 Y162.435 E.02092
G1 X159.334 Y162.524 E.00738
G1 X159.334 Y166.134 E.13714
G1 X159.935 Y166.269 E.02338
G1 X160.362 Y166.203 E.01644
G1 X160.466 Y166.124 E.00495
G1 X160.466 Y168.233 E.08014
G1 X159.935 Y168.929 E.03326
G1 X159.507 Y169.276 E.02092
G1 X159.334 Y169.365 E.00738
G1 X159.334 Y170.959 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y169.365 E-.60571
G1 X159.507 Y169.276 E-.07385
G1 X159.671 Y169.143 E-.08044
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.259 Y161.962 Z18.6 F60000
G1 X164.193 Y156.593 Z18.6
G1 Z18.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11921
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z18.6 F60000
G1 Z18.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 18.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 77/107
; update layer progress
M73 L77
M991 S0 P76 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z18.6 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z18.6
G1 Z18.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11931
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.941 Y154.41 Z18.84 F60000
G1 X159.334 Y150.753 Z18.84
G1 Z18.44
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y152.347 E.06056
G1 X159.935 Y152.371 E.02282
G1 X160.362 Y152.207 E.0174
G1 X160.466 Y152.119 E.00514
G1 X160.466 Y154.805 E.10203
G1 X159.935 Y155.349 E.02889
G1 X159.507 Y155.608 E.01898
G1 X159.334 Y155.668 E.00695
G1 X159.334 Y159.188 E.13373
G1 X159.935 Y159.212 E.02282
G1 X160.362 Y159.048 E.0174
G1 X160.466 Y158.96 E.00514
G1 X160.466 Y161.646 E.10203
G1 X159.935 Y162.19 E.02889
G1 X159.507 Y162.449 E.01898
G1 X159.334 Y162.509 E.00695
G1 X159.334 Y166.029 E.13373
G1 X159.935 Y166.053 E.02282
G1 X160.362 Y165.889 E.0174
G1 X160.466 Y165.801 E.00514
G1 X160.466 Y168.487 E.10203
G1 X159.935 Y169.031 E.02889
G1 X159.507 Y169.29 E.01898
G1 X159.334 Y169.35 E.00695
G1 X159.334 Y170.944 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y169.35 E-.60571
G1 X159.507 Y169.29 E-.06949
G1 X159.698 Y169.174 E-.0848
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.266 Y161.987 Z18.84 F60000
G1 X164.193 Y156.593 Z18.84
G1 Z18.44
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11931
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z18.84 F60000
G1 Z18.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 18.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 78/107
; update layer progress
M73 L78
M991 S0 P77 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z18.84 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z18.84
G1 Z18.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11939
M204 S5000
M73 P83 R1
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.946 Y154.41 Z19.08 F60000
G1 X159.334 Y150.711 Z19.08
G1 Z18.68
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y152.305 E.06056
G1 X159.507 Y152.302 E.00656
G1 X159.935 Y152.2 E.01671
G1 X160.362 Y151.965 E.01853
G1 X160.466 Y151.872 E.00526
G1 X160.466 Y155.053 E.12085
G1 X160.362 Y155.155 E.0055
G1 X159.935 Y155.466 E.0201
G1 X159.507 Y155.648 E.01765
G1 X159.334 Y155.68 E.00667
G1 X159.334 Y159.146 E.13165
G1 X159.507 Y159.143 E.00656
G1 X159.935 Y159.041 E.01671
G1 X160.362 Y158.806 E.01853
G1 X160.466 Y158.713 E.00526
G1 X160.466 Y161.894 E.12085
G1 X160.362 Y161.996 E.0055
G1 X159.935 Y162.307 E.0201
G1 X159.507 Y162.489 E.01765
G1 X159.334 Y162.522 E.00667
G1 X159.334 Y165.987 E.13165
G1 X159.507 Y165.984 E.00656
G1 X159.935 Y165.882 E.01671
G1 X160.362 Y165.647 E.01854
G1 X160.466 Y165.554 E.00526
G1 X160.466 Y168.735 E.12085
G1 X160.362 Y168.837 E.0055
G1 X159.935 Y169.148 E.0201
G1 X159.507 Y169.33 E.01765
G1 X159.334 Y169.363 E.00667
G1 X159.334 Y170.957 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y169.363 E-.60571
G1 X159.507 Y169.33 E-.06675
G1 X159.719 Y169.24 E-.08754
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.265 Y162.045 Z19.08 F60000
G1 X164.193 Y156.593 Z19.08
G1 Z18.68
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11939
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z19.08 F60000
G1 Z18.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 18.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 79/107
; update layer progress
M73 L79
M991 S0 P78 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z19.08 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z19.08
G1 Z18.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11947
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.725 Y154.322 Z19.32 F60000
G1 X160.466 Y150.062 Z19.32
G1 Z18.92
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y151.655 E.06056
G1 X160.362 Y151.756 E.00547
G1 X159.935 Y152.059 E.01993
G1 X159.507 Y152.233 E.01754
G1 X159.334 Y152.263 E.00665
G1 X159.334 Y155.719 E.13132
G1 X159.507 Y155.714 E.00656
G1 X159.935 Y155.604 E.01678
G1 X160.362 Y155.362 E.01867
G1 X160.466 Y155.269 E.00528
G1 X160.466 Y158.497 E.12263
G1 X160.362 Y158.597 E.00547
G1 X159.935 Y158.9 E.01993
G1 X159.507 Y159.074 E.01754
G1 X159.334 Y159.104 E.00665
G1 X159.334 Y162.56 E.13132
G1 X159.507 Y162.555 E.00656
G1 X159.935 Y162.445 E.01678
G1 X160.362 Y162.203 E.01867
G1 X160.466 Y162.11 E.00528
G1 X160.466 Y165.338 E.12263
G1 X160.362 Y165.438 E.00547
G1 X159.935 Y165.741 E.01993
G1 X159.507 Y165.915 E.01754
G1 X159.334 Y165.945 E.00665
G1 X159.334 Y169.401 E.13132
G1 X159.507 Y169.396 E.00656
G1 X159.935 Y169.286 E.01678
G1 X160.362 Y169.044 E.01867
G1 X160.466 Y168.951 E.00528
G1 X160.466 Y170.545 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y168.951 E-.60571
G1 X160.362 Y169.044 E-.05282
G1 X160.13 Y169.175 E-.10146
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.476 Y161.912 Z19.32 F60000
G1 X164.193 Y156.593 Z19.32
G1 Z18.92
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11947
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z19.32 F60000
G1 Z18.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 19.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 80/107
; update layer progress
M73 L80
M991 S0 P79 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z19.32 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z19.32
G1 Z19.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11954
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.735 Y154.321 Z19.56 F60000
G1 X160.466 Y149.814 Z19.56
G1 Z19.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
M73 P84 R1
G1 F11292.473
M204 S8000
G1 X160.466 Y151.408 E.06056
G1 X159.935 Y151.941 E.02857
G1 X159.507 Y152.19 E.01881
G1 X159.334 Y152.247 E.00691
G1 X159.334 Y155.758 E.13338
G1 X159.935 Y155.771 E.02281
G1 X160.362 Y155.599 E.01752
G1 X160.466 Y155.511 E.00515
G1 X160.466 Y158.249 E.10402
G1 X159.935 Y158.782 E.02857
G1 X159.507 Y159.031 E.01881
G1 X159.334 Y159.089 E.00691
G1 X159.334 Y162.599 E.13338
G1 X159.935 Y162.612 E.02281
G1 X160.362 Y162.44 E.01752
G1 X160.466 Y162.352 E.00515
G1 X160.466 Y165.09 E.10403
G1 X159.935 Y165.623 E.02857
G1 X159.507 Y165.872 E.01881
G1 X159.334 Y165.93 E.00691
G1 X159.334 Y169.44 E.13338
G1 X159.935 Y169.453 E.02281
G1 X160.362 Y169.281 E.01752
G1 X160.466 Y169.193 E.00515
G1 X160.466 Y170.787 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y169.193 E-.60571
G1 X160.362 Y169.281 E-.05151
G1 X160.111 Y169.382 E-.10278
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.432 Y162.111 Z19.56 F60000
G1 X164.193 Y156.593 Z19.56
G1 Z19.16
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11954
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z19.56 F60000
G1 Z19.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 19.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 81/107
; update layer progress
M73 L81
M991 S0 P80 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z19.56 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z19.56
G1 Z19.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11960
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y167.91 Z19.8 F60000
G1 Z19.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y169.504 E.06056
G1 X160.362 Y169.584 E.00498
G1 X159.935 Y169.664 E.01652
G1 X159.334 Y169.541 E.02327
G1 X159.334 Y165.942 E.13676
G1 X159.507 Y165.856 E.00733
G1 X159.935 Y165.519 E.02068
G1 X160.466 Y164.844 E.03262
G1 X160.466 Y162.663 E.0829
G1 X160.362 Y162.743 E.00498
G1 X159.935 Y162.823 E.01652
G1 X159.334 Y162.7 E.02327
G1 X159.334 Y159.101 E.13676
G1 X159.507 Y159.015 E.00733
G1 X159.935 Y158.678 E.02068
G1 X160.466 Y158.003 E.03262
G1 X160.466 Y155.821 E.0829
G1 X160.362 Y155.902 E.00498
G1 X159.935 Y155.982 E.01652
G1 X159.334 Y155.859 E.02327
G1 X159.334 Y152.26 E.13676
G1 X159.507 Y152.174 E.00733
G1 X159.935 Y151.837 E.02068
G1 X160.466 Y151.162 E.03262
G1 X160.466 Y148.98 E.0829
G1 X160.362 Y149.061 E.00498
G1 X159.935 Y149.141 E.01652
G1 X159.334 Y149.018 E.02327
G1 X159.334 Y150.612 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y149.018 E-.60572
G1 X159.732 Y149.1 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.636 Y155.658 Z19.8 F60000
G1 X164.193 Y156.593 Z19.8
G1 Z19.4
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11960
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z19.8 F60000
G1 Z19.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 19.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 82/107
; update layer progress
M73 L82
M991 S0 P81 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z19.8 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z19.8
G1 Z19.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11965
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.466 Y168.422 Z20.04 F60000
G1 Z19.64
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y170.016 E.06056
G1 X160.362 Y170.047 E.00411
G1 X159.935 Y169.939 E.01676
G1 X159.334 Y169.686 E.02475
G1 X159.334 Y165.986 E.14056
G1 X159.507 Y165.87 E.00791
G1 X159.935 Y165.426 E.02342
G1 X160.362 Y164.692 E.03227
G1 X160.466 Y164.469 E.00936
G1 X160.466 Y163.174 E.04917
G1 X160.362 Y163.206 E.00411
G1 X159.935 Y163.098 E.01676
G1 X159.334 Y162.845 E.02475
G1 X159.334 Y159.145 E.14056
G1 X159.507 Y159.029 E.00791
G1 X159.935 Y158.585 E.02342
G1 X160.362 Y157.851 E.03227
G1 X160.466 Y157.628 E.00936
G1 X160.466 Y156.333 E.04917
G1 X160.362 Y156.365 E.00411
G1 X159.935 Y156.257 E.01676
G1 X159.334 Y156.004 E.02475
G1 X159.334 Y152.304 E.14056
G1 X159.507 Y152.188 E.00791
G1 X159.935 Y151.744 E.02342
G1 X160.362 Y151.01 E.03227
G1 X160.466 Y150.787 E.00936
G1 X160.466 Y149.492 E.04917
G1 X160.362 Y149.524 E.00411
G1 X159.935 Y149.416 E.01676
G1 X159.334 Y149.163 E.02475
G1 X159.334 Y150.757 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y149.163 E-.60572
G1 X159.709 Y149.321 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.715 Y155.817 Z20.04 F60000
G1 X164.193 Y156.593 Z20.04
G1 Z19.64
M73 P85 R1
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11965
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z20.04 F60000
G1 Z19.64
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 19.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 83/107
; update layer progress
M73 L83
M991 S0 P82 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z20.04 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z20.04
G1 Z19.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11970
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.921 Y154.414 Z20.28 F60000
G1 X159.334 Y150.933 Z20.28
G1 Z19.88
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y149.339 E.06056
G1 X159.88 Y149.738 E.02569
G1 X160.2 Y150.166 E.0203
G1 X160.25 Y150.594 E.01635
G1 X160.035 Y151.449 E.03349
G1 X159.805 Y151.876 E.01845
G1 X159.445 Y152.304 E.02122
G1 X159.334 Y152.385 E.00522
G1 X159.334 Y156.18 E.14416
G1 X159.88 Y156.58 E.02569
G1 X160.2 Y157.007 E.0203
G1 X160.25 Y157.435 E.01635
G1 X160.035 Y158.29 E.03349
G1 X159.805 Y158.717 E.01845
G1 X159.445 Y159.145 E.02122
G1 X159.334 Y159.226 E.00522
G1 X159.334 Y163.021 E.14416
G1 X159.88 Y163.421 E.02569
G1 X160.2 Y163.848 E.0203
G1 X160.25 Y164.276 E.01635
G1 X160.035 Y165.131 E.03349
G1 X159.805 Y165.558 E.01845
G1 X159.445 Y165.986 E.02122
G1 X159.334 Y166.067 E.00522
G1 X159.334 Y169.862 E.14416
G1 X159.88 Y170.262 E.02569
G1 X160.2 Y170.689 E.0203
G1 X160.244 Y171.066 E.01439
G1 X160.466 Y171.066 E.00843
G1 X160.466 Y169.693 E.05213
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y171.066 E-.52141
G1 X160.244 Y171.066 E-.0843
G1 X160.2 Y170.689 E-.14397
G1 X160.184 Y170.667 E-.01031
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.275 Y163.327 Z20.28 F60000
G1 X164.193 Y156.593 Z20.28
G1 Z19.88
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11970
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z20.28 F60000
G1 Z19.88
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 20.12
; LAYER_HEIGHT: 0.240002
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 84/107
; update layer progress
M73 L84
M991 S0 P83 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z20.28 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z20.28
G1 Z20.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11974
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.501 Y169.541 Z20.52 F60000
G1 X160.466 Y169.929 Z20.52
G1 Z20.12
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y171.066 E.04316
G1 X160.008 Y171.066 E.0174
G1 X159.872 Y170.689 E.0152
G1 X159.514 Y170.262 E.02119
G1 X159.334 Y170.092 E.00938
G1 X159.334 Y166.187 E.14835
G1 X159.546 Y165.986 E.01109
G1 X159.815 Y165.558 E.01918
G1 X159.973 Y165.131 E.01732
G1 X160.026 Y164.276 E.03255
G1 X159.872 Y163.848 E.01727
G1 X159.514 Y163.421 E.02119
G1 X159.334 Y163.251 E.00938
G1 X159.334 Y159.346 E.14835
G1 X159.546 Y159.145 E.01109
G1 X159.815 Y158.717 E.01918
G1 X159.973 Y158.29 E.01732
G1 X160.026 Y157.435 E.03255
G1 X159.872 Y157.007 E.01727
G1 X159.514 Y156.58 E.02119
G1 X159.334 Y156.409 E.00938
G1 X159.334 Y152.505 E.14835
G1 X159.546 Y152.304 E.01109
G1 X159.815 Y151.876 E.01918
G1 X159.973 Y151.449 E.01732
G1 X160.026 Y150.594 E.03255
G1 X159.872 Y150.166 E.01727
G1 X159.514 Y149.738 E.02119
G1 X159.334 Y149.568 E.00938
G1 X159.334 Y148.934 E.02409
G1 X160.294 Y148.934 E.03647
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y148.934 E-.3648
G1 X159.334 Y149.568 E-.24092
G1 X159.514 Y149.738 E-.09385
G1 X159.616 Y149.86 E-.06043
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.907 Y156.172 Z20.52 F60000
G1 X164.193 Y156.593 Z20.52
G1 Z20.12
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11974
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z20.52 F60000
G1 Z20.12
M73 P86 R1
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 20.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 85/107
; update layer progress
M73 L85
M991 S0 P84 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z20.52 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z20.52
G1 Z20.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11977
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.516 Y169.543 Z20.76 F60000
G1 X160.466 Y170.114 Z20.76
G1 Z20.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y171.066 E.03615
G1 X159.823 Y171.066 E.02441
G1 X159.624 Y170.689 E.01618
G1 X159.334 Y170.363 E.01656
G1 X159.334 Y166.419 E.14986
G1 X159.661 Y165.986 E.02059
G1 X159.852 Y165.558 E.01779
G1 X159.941 Y165.131 E.01659
G1 X159.944 Y164.703 E.01624
G1 X159.85 Y164.276 E.01663
G1 X159.624 Y163.848 E.01838
G1 X159.334 Y163.522 E.01656
G1 X159.334 Y159.578 E.14986
G1 X159.661 Y159.145 E.02059
G1 X159.852 Y158.717 E.01779
G1 X159.941 Y158.29 E.01659
G1 X159.944 Y157.862 E.01624
G1 X159.85 Y157.435 E.01663
G1 X159.624 Y157.007 E.01838
G1 X159.334 Y156.681 E.01656
G1 X159.334 Y152.737 E.14986
G1 X159.661 Y152.304 E.02059
G1 X159.852 Y151.876 E.01779
G1 X159.941 Y151.449 E.01659
G1 X159.944 Y151.021 E.01624
G1 X159.85 Y150.594 E.01663
G1 X159.624 Y150.166 E.01838
G1 X159.334 Y149.84 E.01656
G1 X159.334 Y148.934 E.0344
G1 X160.023 Y148.934 E.02616
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y148.934 E-.26162
G1 X159.334 Y149.84 E-.34409
G1 X159.604 Y150.144 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.029 Y156.362 Z20.76 F60000
G1 X164.193 Y156.593 Z20.76
G1 Z20.36
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11977
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z20.76 F60000
G1 Z20.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 20.6
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 86/107
; update layer progress
M73 L86
M991 S0 P85 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z20.76 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z20.76
G1 Z20.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11980
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.528 Y169.544 Z21 F60000
G1 X160.466 Y170.266 Z21
G1 Z20.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y171.066 E.03038
G1 X159.671 Y171.066 E.03018
G1 X159.412 Y170.689 E.01737
G1 X159.334 Y170.608 E.00426
G1 X159.334 Y166.645 E.15057
G1 X159.545 Y166.414 E.01189
G1 X159.795 Y165.986 E.01883
G1 X159.915 Y165.558 E.01686
G1 X159.936 Y165.131 E.01626
G1 X159.871 Y164.703 E.01643
G1 X159.706 Y164.276 E.01741
G1 X159.412 Y163.848 E.01973
G1 X159.334 Y163.767 E.00426
G1 X159.334 Y159.804 E.15057
G1 X159.545 Y159.572 E.01189
G1 X159.795 Y159.145 E.01883
G1 X159.915 Y158.717 E.01686
G1 X159.936 Y158.29 E.01626
G1 X159.871 Y157.862 E.01643
G1 X159.706 Y157.435 E.01741
G1 X159.412 Y157.007 E.01973
G1 X159.334 Y156.926 E.00426
G1 X159.334 Y152.963 E.15057
G1 X159.545 Y152.731 E.01189
G1 X159.795 Y152.304 E.01883
G1 X159.915 Y151.876 E.01686
G1 X159.936 Y151.449 E.01626
G1 X159.871 Y151.021 E.01643
G1 X159.706 Y150.594 E.01741
G1 X159.412 Y150.166 E.01973
G1 X159.334 Y150.085 E.00426
G1 X159.334 Y148.934 E.04372
G1 X159.778 Y148.934 E.01684
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y148.934 E-.16844
G1 X159.334 Y150.085 E-.43728
G1 X159.412 Y150.166 E-.04256
G1 X159.579 Y150.408 E-.11173
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.143 Y156.526 Z21 F60000
G1 X164.193 Y156.593 Z21
G1 Z20.6
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11980
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z21 F60000
G1 Z20.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 20.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 87/107
; update layer progress
M73 L87
M991 S0 P86 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z21 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z21
G1 Z20.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P87 R1
G1 F11983
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y168.513 Z21.24 F60000
G1 Z20.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y166.919 E.06056
G1 X159.776 Y166.414 E.02551
G1 X159.958 Y165.986 E.01765
G1 X160.005 Y165.558 E.01634
G1 X159.958 Y165.131 E.01634
G1 X159.825 Y164.703 E.01701
G1 X159.585 Y164.276 E.01862
G1 X159.334 Y164.019 E.01363
G1 X159.334 Y160.078 E.14974
G1 X159.776 Y159.572 E.02551
G1 X159.958 Y159.145 E.01765
G1 X160.005 Y158.717 E.01634
G1 X159.958 Y158.29 E.01634
G1 X159.825 Y157.862 E.01701
G1 X159.585 Y157.435 E.01862
G1 X159.334 Y157.178 E.01363
G1 X159.334 Y153.237 E.14974
G1 X159.776 Y152.731 E.02551
G1 X159.958 Y152.304 E.01765
G1 X160.005 Y151.876 E.01634
G1 X159.958 Y151.449 E.01634
G1 X159.825 Y151.021 E.01701
G1 X159.585 Y150.594 E.01862
G1 X159.334 Y150.337 E.01363
G1 X159.334 Y148.934 E.0533
G1 X159.526 Y148.934 E.00726
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y148.934 E-.07264
G1 X159.334 Y150.337 E-.53308
G1 X159.585 Y150.594 E-.13632
G1 X159.608 Y150.635 E-.01796
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z21.24 F60000
G1 Z20.84
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11983
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z21.24 F60000
G1 Z20.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 21.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 88/107
; update layer progress
M73 L88
M991 S0 P87 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z21.24 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z21.24
G1 Z21.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11986
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y168.756 Z21.48 F60000
G1 Z21.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.162 E.06056
G1 X159.728 Y166.841 E.01931
G1 X160.068 Y166.414 E.02076
G1 X160.163 Y165.986 E.01663
G1 X160.009 Y165.131 E.03301
G1 X159.805 Y164.703 E.018
G1 X159.48 Y164.276 E.0204
G1 X159.334 Y164.157 E.00714
G1 X159.334 Y160.321 E.14574
G1 X159.728 Y160 E.01931
G1 X160.068 Y159.572 E.02076
G1 X160.163 Y159.145 E.01663
G1 X160.009 Y158.29 E.03301
G1 X159.805 Y157.862 E.018
G1 X159.48 Y157.435 E.0204
G1 X159.334 Y157.316 E.00714
G1 X159.334 Y153.48 E.14574
G1 X159.728 Y153.159 E.01931
G1 X160.068 Y152.731 E.02076
G1 X160.163 Y152.304 E.01663
G1 X160.009 Y151.449 E.03301
G1 X159.805 Y151.021 E.018
G1 X159.48 Y150.594 E.0204
G1 X159.334 Y150.475 E.00714
G1 X159.334 Y148.934 E.05853
G1 X159.388 Y148.934 E.00203
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y148.934 E-.02033
G1 X159.334 Y150.475 E-.58538
G1 X159.48 Y150.594 E-.07142
G1 X159.612 Y150.767 E-.08287
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z21.48 F60000
G1 Z21.08
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11986
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z21.48 F60000
G1 Z21.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 21.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 89/107
; update layer progress
M73 L89
M991 S0 P88 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z21.48 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z21.48
G1 Z21.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11988
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y168.944 Z21.72 F60000
G1 Z21.32
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.35 E.06056
G1 X160.295 Y166.841 E.04128
G1 X160.466 Y166.486 E.01496
G1 X160.466 Y166.207 E.01062
G1 X160.428 Y165.986 E.00851
M73 P88 R1
G1 X160.093 Y165.131 E.03489
G1 X159.815 Y164.703 E.01938
G1 X159.386 Y164.276 E.02301
G1 X159.334 Y164.244 E.00231
G1 X159.334 Y160.509 E.1419
G1 X160.295 Y160 E.04128
G1 X160.466 Y159.645 E.01496
G1 X160.466 Y159.366 E.01062
G1 X160.428 Y159.145 E.00851
G1 X160.093 Y158.29 E.03489
G1 X159.815 Y157.862 E.01938
G1 X159.386 Y157.435 E.02301
G1 X159.334 Y157.403 E.00231
G1 X159.334 Y153.668 E.1419
G1 X160.295 Y153.159 E.04128
G1 X160.466 Y152.804 E.01496
G1 X160.466 Y152.525 E.01062
G1 X160.428 Y152.304 E.00851
G1 X160.093 Y151.449 E.03489
G1 X159.815 Y151.021 E.01938
G1 X159.386 Y150.594 E.02301
G1 X159.334 Y150.562 E.00231
G1 X159.334 Y148.968 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y150.562 E-.60571
G1 X159.386 Y150.594 E-.02307
G1 X159.631 Y150.837 E-.13123
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z21.72 F60000
G1 Z21.32
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11988
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z21.72 F60000
G1 Z21.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 21.56
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 90/107
; update layer progress
M73 L90
M991 S0 P89 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z21.72 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z21.72
G1 Z21.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11989
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y169.109 Z21.96 F60000
G1 Z21.56
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.515 E.06056
G1 X159.935 Y167.349 E.02366
G1 X160.362 Y167.379 E.01629
G1 X160.466 Y167.454 E.00485
G1 X160.466 Y165.532 E.07304
G1 X159.935 Y164.777 E.03506
G1 X159.507 Y164.405 E.02154
G1 X159.334 Y164.308 E.00752
G1 X159.334 Y160.674 E.13807
G1 X159.935 Y160.508 E.02366
G1 X160.362 Y160.538 E.01629
G1 X160.466 Y160.613 E.00485
G1 X160.466 Y158.691 E.07304
G1 X159.935 Y157.936 E.03506
G1 X159.507 Y157.564 E.02154
G1 X159.334 Y157.467 E.00752
G1 X159.334 Y153.833 E.13807
G1 X159.935 Y153.667 E.02366
G1 X160.362 Y153.697 E.01629
G1 X160.466 Y153.772 E.00485
G1 X160.466 Y151.85 E.07304
G1 X159.935 Y151.095 E.03506
G1 X159.507 Y150.723 E.02154
G1 X159.334 Y150.626 E.00752
G1 X159.334 Y149.032 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y150.626 E-.60571
G1 X159.507 Y150.723 E-.07521
G1 X159.664 Y150.859 E-.07908
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z21.96 F60000
G1 Z21.56
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11989
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z21.96 F60000
G1 Z21.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 21.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 91/107
; update layer progress
M73 L91
M991 S0 P90 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z21.96 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z21.96
G1 Z21.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11991
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y169.224 Z22.2 F60000
G1 Z21.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.63 E.06056
G1 X159.935 Y167.58 E.02288
G1 X160.362 Y167.723 E.01714
G1 X160.466 Y167.809 E.0051
G1 X160.466 Y165.252 E.09714
G1 X159.935 Y164.678 E.02972
G1 X159.507 Y164.399 E.0194
G1 X159.334 Y164.331 E.00704
G1 X159.334 Y160.789 E.13456
G1 X159.935 Y160.739 E.02289
G1 X160.362 Y160.882 E.01714
G1 X160.466 Y160.968 E.0051
G1 X160.466 Y158.411 E.09714
G1 X159.935 Y157.837 E.02972
G1 X159.507 Y157.557 E.0194
G1 X159.334 Y157.49 E.00704
G1 X159.334 Y153.948 E.13456
G1 X159.935 Y153.898 E.02289
G1 X160.362 Y154.041 E.01714
G1 X160.466 Y154.127 E.0051
G1 X160.466 Y151.57 E.09714
G1 X159.935 Y150.996 E.02972
G1 X159.507 Y150.716 E.0194
G1 X159.334 Y150.649 E.00704
G1 X159.334 Y149.055 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y150.649 E-.60571
G1 X159.507 Y150.716 E-.07043
G1 X159.692 Y150.837 E-.08386
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z22.2 F60000
G1 Z21.8
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11991
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
M73 P89 R1
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z22.2 F60000
G1 Z21.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 22.04
; LAYER_HEIGHT: 0.240002
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 92/107
; update layer progress
M73 L92
M991 S0 P91 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z22.2 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z22.2
G1 Z22.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11992
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y169.275 Z22.44 F60000
G1 Z22.04
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y167.681 E.06056
G1 X159.507 Y167.676 E.00656
G1 X159.935 Y167.761 E.01656
G1 X160.362 Y167.979 E.01823
G1 X160.466 Y168.07 E.00523
G1 X160.466 Y165 E.11661
G1 X160.362 Y164.896 E.00558
G1 X159.935 Y164.565 E.02055
G1 X159.507 Y164.365 E.01794
G1 X159.334 Y164.325 E.00673
G1 X159.334 Y160.84 E.13243
G1 X159.507 Y160.835 E.00656
G1 X159.935 Y160.92 E.01656
G1 X160.362 Y161.138 E.01823
G1 X160.466 Y161.229 E.00523
G1 X160.466 Y158.159 E.11661
G1 X160.362 Y158.055 E.00558
G1 X159.935 Y157.724 E.02054
G1 X159.507 Y157.524 E.01794
G1 X159.334 Y157.484 E.00673
G1 X159.334 Y153.999 E.13243
G1 X159.507 Y153.994 E.00656
G1 X159.935 Y154.079 E.01656
G1 X160.362 Y154.297 E.01823
G1 X160.466 Y154.387 E.00523
G1 X160.466 Y151.318 E.11661
G1 X160.362 Y151.214 E.00558
G1 X159.935 Y150.883 E.02054
G1 X159.507 Y150.683 E.01794
G1 X159.334 Y150.643 E.00673
G1 X159.334 Y149.049 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y150.643 E-.60571
G1 X159.507 Y150.683 E-.06729
G1 X159.714 Y150.78 E-.087
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.193 Y156.593 Z22.44 F60000
G1 Z22.04
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.06888
G1 X166.007 Y163.407 E.25885
G1 X164.193 Y163.407 E.06888
G1 X164.193 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.81 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11992
M204 S5000
G1 X166.39 Y156.21 E.09064
G1 X166.39 Y163.79 E.2663
G1 X163.81 Y163.79 E.09064
G1 X163.81 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.809 Y156.223 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.577 Y163.023 Z22.44 F60000
G1 Z22.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.03675
G1 X165.623 Y156.977 E.21241
G1 X164.577 Y156.977 E.03675
G1 X164.577 Y162.963 E.2103
M204 S10000
G1 X164.931 Y162.669 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X165.269 Y162.669 E.01094
G1 X165.269 Y157.331 E.17244
G1 X164.931 Y157.331 E.01094
G1 X164.931 Y162.609 E.1705
; CHANGE_LAYER
; Z_HEIGHT: 22.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13282.957
G1 X164.931 Y160.609 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 93/107
; update layer progress
M73 L93
M991 S0 P92 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z22.44 I.178 J-1.204 P1  F60000
G1 X160.806 Y160 Z22.44
G1 Z22.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11994
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.497 Y169.541 Z22.68 F60000
G1 X160.466 Y169.885 Z22.68
G1 Z22.28
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y168.291 E.06056
G1 X160.362 Y168.193 E.0054
G1 X159.935 Y167.908 E.01954
G1 X159.507 Y167.752 E.01729
G1 X159.334 Y167.729 E.00662
G1 X159.334 Y164.293 E.13055
G1 X159.507 Y164.305 E.00658
G1 X159.935 Y164.433 E.01696
G1 X160.362 Y164.692 E.01899
G1 X160.466 Y164.787 E.00532
G1 X160.466 Y161.45 E.12678
G1 X160.362 Y161.352 E.0054
G1 X159.935 Y161.067 E.01954
G1 X159.507 Y160.911 E.01729
G1 X159.334 Y160.888 E.00662
G1 X159.334 Y157.452 E.13055
G1 X159.507 Y157.464 E.00658
G1 X159.935 Y157.592 E.01696
G1 X160.362 Y157.851 E.01899
G1 X160.466 Y157.946 E.00532
G1 X160.466 Y154.609 E.12678
G1 X160.362 Y154.511 E.0054
G1 X159.935 Y154.226 E.01954
G1 X159.507 Y154.07 E.01729
G1 X159.334 Y154.047 E.00662
G1 X159.334 Y150.611 E.13055
G1 X159.507 Y150.623 E.00658
G1 X159.935 Y150.751 E.01696
G1 X160.362 Y151.01 E.01899
G1 X160.466 Y151.105 E.00532
G1 X160.466 Y149.511 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y151.105 E-.60572
G1 X160.362 Y151.01 E-.05326
G1 X160.135 Y150.872 E-.10103
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z22.68 I-1.05 J.616 P1  F60000
G1 X163.491 Y156.593 Z22.68
G1 Z22.28
G1 E.8 F1800
; FEATURE: Inner wall
G1 F2100
M204 S8000
G1 X163.782 Y156.593 E.01108
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
G1 X166.007 Y160.607 E.07648
G1 X166.007 Y161.007 E.0152
G1 F10278.275
G1 X166.007 Y161.407 E.0152
G1 F9060.195
G1 X166.007 Y161.807 E.0152
G1 F7918.914
G1 X166.007 Y162.207 E.0152
G1 F6854.434
G1 X166.007 Y162.607 E.0152
G1 F5866.753
G1 X166.007 Y163.007 E.0152
G1 F4955.873
G1 X166.007 Y163.407 E.0152
G1 F4121.792
G1 X165.782 Y163.407 E.00851
G1 F3688.197
G1 X165.382 Y163.407 E.0152
G1 F2973.931
G1 X164.982 Y163.407 E.0152
G1 F2336.464
G1 X164.582 Y163.407 E.0152
G1 F1775.797
G1 X164.182 Y163.407 E.0152
G1 F1291.931
G1 X163.782 Y163.407 E.0152
G1 F884.864
G1 X163.443 Y163.407 E.01288
M106 S178.5
G1 F600
G1 X163.443 Y156.606 E.25836
M106 S0
; COOLING_NODE: 0
M204 S250
G1 X163.491 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M106 S178.5
G1 F2100
M204 S5000
G1 X163.769 Y156.21 E.00978
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
M73 P90 R1
G1 X166.39 Y156.21 E.00776
G1 F8579.769
G1 X166.39 Y156.61 E.01405
G1 F9766.147
G1 X166.39 Y157.01 E.01405
G1 F11029.324
G1 X166.39 Y157.41 E.01405
G1 F11994
G1 X166.39 Y157.81 E.01405
G1 X166.39 Y160.99 E.11172
G1 X166.39 Y161.39 E.01405
G1 F11663.26
G1 X166.39 Y161.79 E.01405
G1 F10363.199
G1 X166.39 Y162.19 E.01405
G1 F9139.939
G1 X166.39 Y162.59 E.01405
G1 F7993.478
G1 X166.39 Y162.99 E.01405
G1 F6923.818
G1 X166.39 Y163.39 E.01405
G1 F5930.957
G1 X166.39 Y163.79 E.01405
G1 F5014.896
G1 X166.169 Y163.79 E.00776
G1 F4541.69
G1 X165.769 Y163.79 E.01405
G1 F3744.863
G1 X165.369 Y163.79 E.01405
G1 F3024.837
G1 X164.969 Y163.79 E.01405
G1 F2381.61
G1 X164.569 Y163.79 E.01405
G1 F1815.183
G1 X164.169 Y163.79 E.01405
G1 F1325.557
G1 X163.769 Y163.79 E.01405
M106 S178.5
G1 F912.73
G1 X163.4 Y163.79 E.01296
M106 S0
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45
M106 S178.5
G1 F600
G1 X163.06 Y163.79 E.01292
G1 X163.06 Y156.21 E.28798
G1 X163.4 Y156.21 E.01292
M106 S0
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M106 S178.5
G1 F623.565
G1 X163.431 Y156.21 E.00108
M106 S0
M204 S10000
M73 P90 R0
G1 X163.806 Y156.754 F60000
; FEATURE: Bridge
; LINE_WIDTH: 0.493694
M106 S178.5
G1 F1500
M204 S8000
G1 X163.806 Y163.081 E.26674
G1 X164.249 Y163.081 E.01864
G1 X164.249 Y156.919 E.25975
G1 X164.691 Y156.919 E.01864
G1 X164.691 Y163.246 E.26674
M106 S0
M204 S10000
G1 X165.188 Y163.001 F60000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.464374
G1 F10899.315
M204 S8000
G1 X165.601 Y163.001 E.01625
G1 X165.601 Y156.999 E.23625
G1 X165.188 Y156.999 E.01625
G1 X165.188 Y162.941 E.23388
; CHANGE_LAYER
; Z_HEIGHT: 22.52
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10899.315
G1 X165.188 Y160.941 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 94/107
; update layer progress
M73 L94
M991 S0 P93 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z22.68 I.256 J-1.19 P1  F60000
G1 X160.806 Y160 Z22.68
G1 Z22.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11994
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.518 Y169.543 Z22.92 F60000
G1 X160.466 Y170.133 Z22.92
G1 Z22.52
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y168.539 E.06056
G1 X159.935 Y168.031 E.0279
G1 X159.507 Y167.801 E.01844
G1 X159.334 Y167.751 E.00683
G1 X159.334 Y164.234 E.13363
G1 X159.507 Y164.219 E.00659
G1 X159.935 Y164.275 E.01638
G1 X160.362 Y164.466 E.01779
G1 X160.466 Y164.555 E.00518
G1 X160.466 Y161.698 E.10855
G1 X159.935 Y161.19 E.0279
G1 X159.507 Y160.96 E.01844
G1 X159.334 Y160.91 E.00683
G1 X159.334 Y157.393 E.13363
G1 X159.507 Y157.377 E.00659
G1 X159.935 Y157.434 E.01638
G1 X160.362 Y157.625 E.01779
G1 X160.466 Y157.714 E.00518
G1 X160.466 Y154.856 E.10855
G1 X159.935 Y154.349 E.0279
G1 X159.507 Y154.119 E.01844
G1 X159.334 Y154.069 E.00683
G1 X159.334 Y150.552 E.13363
G1 X159.507 Y150.536 E.00659
G1 X159.935 Y150.592 E.01638
G1 X160.362 Y150.784 E.01779
G1 X160.466 Y150.873 E.00518
G1 X160.466 Y149.279 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y150.873 E-.60571
G1 X160.362 Y150.784 E-.0518
G1 X160.116 Y150.674 E-.10248
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z22.92 I-1.061 J.596 P1  F60000
G1 X163.443 Y156.593 Z22.92
G1 Z22.52
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11994
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z22.92 I-1.197 J-.217 P1  F60000
G1 X163.827 Y163.023 Z22.92
G1 Z22.52
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
; Z_HEIGHT: 22.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 95/107
; update layer progress
M73 L95
M991 S0 P94 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z22.92 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z22.92
G1 Z22.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11995
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.625 Y154.328 Z23.16 F60000
G1 X160.466 Y152.179 Z23.16
G1 Z22.76
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y150.585 E.06056
M73 P91 R0
G1 X160.362 Y150.502 E.00504
G1 X159.935 Y150.394 E.01675
G1 X159.334 Y150.488 E.02308
G1 X159.334 Y154.064 E.13588
G1 X159.507 Y154.143 E.00721
G1 X159.935 Y154.456 E.02014
G1 X160.466 Y155.086 E.03131
G1 X160.466 Y157.426 E.08889
G1 X160.362 Y157.343 E.00504
G1 X159.935 Y157.235 E.01675
G1 X159.334 Y157.329 E.02308
G1 X159.334 Y160.905 E.13588
G1 X159.507 Y160.984 E.00721
G1 X159.935 Y161.297 E.02014
G1 X160.466 Y161.927 E.03131
G1 X160.466 Y164.267 E.08889
G1 X160.362 Y164.184 E.00504
G1 X159.935 Y164.076 E.01675
G1 X159.334 Y164.17 E.02308
G1 X159.334 Y167.746 E.13588
G1 X159.507 Y167.825 E.00721
G1 X159.935 Y168.138 E.02014
G1 X160.466 Y168.769 E.03131
G1 X160.466 Y171.066 E.08727
G1 X160.414 Y171.066 E.00196
G1 X160.362 Y171.025 E.0025
G1 X159.935 Y170.917 E.01675
G1 X159.334 Y171.011 E.02308
G1 X159.334 Y169.417 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.011 E-.60572
G1 X159.736 Y170.948 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.644 Y163.559 Z23.16 F60000
G1 X163.443 Y156.593 Z23.16
G1 Z22.76
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11995
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z23.16 F60000
G1 Z22.76
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
; Z_HEIGHT: 23
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 96/107
; update layer progress
M73 L96
M991 S0 P95 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z23.16 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z23.16
G1 Z23
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11996
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.649 Y154.327 Z23.4 F60000
G1 X160.466 Y151.75 Z23.4
G1 Z23
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y150.156 E.06056
G1 X160.362 Y150.096 E.00454
G1 X159.935 Y150.138 E.01632
G1 X159.334 Y150.355 E.02425
G1 X159.334 Y154.028 E.13955
G1 X159.507 Y154.137 E.00775
G1 X159.935 Y154.551 E.02262
G1 X160.466 Y155.394 E.03783
G1 X160.466 Y156.997 E.06091
G1 X160.362 Y156.937 E.00454
G1 X159.935 Y156.979 E.01632
G1 X159.334 Y157.196 E.02425
G1 X159.334 Y160.869 E.13955
G1 X159.507 Y160.978 E.00775
G1 X159.935 Y161.392 E.02262
G1 X160.466 Y162.235 E.03783
G1 X160.466 Y163.838 E.06091
G1 X160.362 Y163.778 E.00454
G1 X159.935 Y163.82 E.01632
G1 X159.334 Y164.037 E.02425
G1 X159.334 Y167.71 E.13955
G1 X159.507 Y167.819 E.00775
G1 X159.935 Y168.233 E.02262
G1 X160.466 Y169.076 E.03783
G1 X160.466 Y170.679 E.06091
G1 X160.362 Y170.619 E.00454
G1 X159.935 Y170.661 E.01632
G1 X159.334 Y170.878 E.02425
G1 X159.334 Y169.284 E.06056
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y170.878 E-.60572
G1 X159.716 Y170.74 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.661 Y163.36 Z23.4 F60000
G1 X163.443 Y156.593 Z23.4
G1 Z23
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11996
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z23.4 F60000
G1 Z23
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
; Z_HEIGHT: 23.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 97/107
; update layer progress
M73 L97
M991 S0 P96 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z23.4 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z23.4
G1 Z23.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11997
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.334 Y169.122 Z23.64 F60000
G1 Z23.24
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y170.716 E.06056
G1 X160.01 Y170.262 E.03092
G1 X160.306 Y169.834 E.01976
G1 X160.316 Y169.406 E.01625
G1 X160.056 Y168.551 E.03395
G1 X159.807 Y168.124 E.0188
G1 X159.422 Y167.696 E.02187
G1 X159.334 Y167.638 E.00399
G1 X159.334 Y163.875 E.14297
M73 P92 R0
G1 X160.01 Y163.421 E.03092
G1 X160.306 Y162.993 E.01976
G1 X160.316 Y162.565 E.01625
G1 X160.056 Y161.71 E.03395
G1 X159.807 Y161.283 E.0188
G1 X159.422 Y160.855 E.02187
G1 X159.334 Y160.797 E.00399
G1 X159.334 Y157.034 E.14297
G1 X160.01 Y156.58 E.03092
G1 X160.306 Y156.152 E.01976
G1 X160.316 Y155.724 E.01625
G1 X160.056 Y154.869 E.03395
G1 X159.807 Y154.442 E.0188
G1 X159.422 Y154.014 E.02187
G1 X159.334 Y153.956 E.00399
G1 X159.334 Y150.192 E.14297
G1 X160.01 Y149.738 E.03092
G1 X160.306 Y149.311 E.01976
G1 X160.315 Y148.934 E.01431
G1 X160.466 Y148.934 E.00573
G1 X160.466 Y150.378 E.05483
; COOLING_NODE: 0
; WIPE_START
G1 X160.466 Y148.934 E-.54843
G1 X160.315 Y148.934 E-.05729
G1 X160.306 Y149.311 E-.14311
G1 X160.289 Y149.335 E-.01118
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.331 Y156.335 Z23.64 F60000
G1 X163.443 Y156.593 Z23.64
G1 Z23.24
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11997
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z23.64 F60000
G1 Z23.24
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
; Z_HEIGHT: 23.48
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 98/107
; update layer progress
M73 L98
M991 S0 P97 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z23.64 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z23.64
G1 Z23.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11997
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.723 Y154.322 Z23.88 F60000
G1 X160.466 Y150.124 Z23.88
G1 Z23.48
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y148.934 E.0452
G1 X160.061 Y148.934 E.01536
G1 X159.945 Y149.311 E.01498
G1 X159.592 Y149.738 E.02105
G1 X159.334 Y149.97 E.01316
G1 X159.334 Y153.848 E.14734
G1 X159.519 Y154.014 E.00945
G1 X159.809 Y154.442 E.01963
G1 X159.985 Y154.869 E.01757
G1 X160.077 Y155.724 E.03267
G1 X159.945 Y156.152 E.01701
G1 X159.592 Y156.58 E.02105
G1 X159.334 Y156.811 E.01316
G1 X159.334 Y160.689 E.14734
G1 X159.519 Y160.855 E.00945
G1 X159.809 Y161.283 E.01963
G1 X159.985 Y161.71 E.01757
G1 X160.077 Y162.565 E.03267
G1 X159.945 Y162.993 E.01701
G1 X159.592 Y163.421 E.02105
G1 X159.334 Y163.652 E.01316
G1 X159.334 Y167.53 E.14734
G1 X159.519 Y167.696 E.00945
G1 X159.809 Y168.124 E.01963
G1 X159.985 Y168.551 E.01757
G1 X160.077 Y169.406 E.03267
G1 X159.945 Y169.834 E.01701
G1 X159.592 Y170.262 E.02105
G1 X159.334 Y170.493 E.01316
G1 X159.334 Y171.066 E.02176
G1 X160.356 Y171.066 E.0388
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.38811
G1 X159.334 Y170.493 E-.2176
G1 X159.592 Y170.262 E-.13158
G1 X159.63 Y170.216 E-.02271
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.688 Y162.866 Z23.88 F60000
G1 X163.443 Y156.593 Z23.88
G1 Z23.48
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11997
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z23.88 F60000
G1 Z23.48
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
; Z_HEIGHT: 23.72
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 99/107
; update layer progress
M73 L99
M991 S0 P98 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z23.88 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z23.88
G1 Z23.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.73 Y154.321 Z24.12 F60000
G1 X160.466 Y149.929 Z24.12
G1 Z23.72
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y148.934 E.03778
G1 X159.866 Y148.934 E.02278
G1 X159.681 Y149.311 E.01593
G1 X159.334 Y149.708 E.02004
G1 X159.334 Y153.644 E.14951
G1 X159.63 Y154.014 E.01802
G1 X159.84 Y154.442 E.01809
G1 X159.946 Y154.869 E.01674
G1 X159.966 Y155.297 E.01626
G1 X159.891 Y155.724 E.01649
G1 X159.681 Y156.152 E.01809
G1 X159.334 Y156.549 E.02004
G1 X159.334 Y160.485 E.14951
G1 X159.63 Y160.855 E.01802
G1 X159.84 Y161.283 E.01809
G1 X159.946 Y161.71 E.01674
G1 X159.966 Y162.138 E.01626
G1 X159.891 Y162.565 E.01649
G1 X159.681 Y162.993 E.01809
G1 X159.334 Y163.39 E.02004
G1 X159.334 Y167.326 E.14951
G1 X159.63 Y167.696 E.01802
G1 X159.84 Y168.124 E.01809
G1 X159.946 Y168.551 E.01674
G1 X159.966 Y168.979 E.01626
M73 P93 R0
G1 X159.891 Y169.406 E.01649
G1 X159.681 Y169.834 E.01809
G1 X159.334 Y170.231 E.02004
G1 X159.334 Y171.066 E.03169
G1 X160.094 Y171.066 E.02887
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.28873
G1 X159.334 Y170.231 E-.31699
G1 X159.602 Y169.926 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.715 Y162.592 Z24.12 F60000
G1 X163.443 Y156.593 Z24.12
G1 Z23.72
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z24.12 F60000
G1 Z23.72
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
; Z_HEIGHT: 23.96
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 100/107
; update layer progress
M73 L100
M991 S0 P99 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z24.12 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z24.12
G1 Z23.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.736 Y154.321 Z24.36 F60000
G1 X160.466 Y149.77 Z24.36
G1 Z23.96
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y148.934 E.03175
G1 X159.707 Y148.934 E.02881
G1 X159.463 Y149.311 E.01704
G1 X159.334 Y149.449 E.00717
G1 X159.334 Y153.417 E.15076
G1 X159.492 Y153.587 E.00879
G1 X159.759 Y154.014 E.01916
G1 X159.896 Y154.442 E.01706
G1 X159.935 Y154.869 E.01631
G1 X159.887 Y155.297 E.01634
G1 X159.74 Y155.724 E.01718
G1 X159.463 Y156.152 E.01935
G1 X159.334 Y156.29 E.00717
G1 X159.334 Y160.258 E.15076
G1 X159.492 Y160.428 E.00879
G1 X159.759 Y160.855 E.01916
G1 X159.896 Y161.283 E.01706
G1 X159.935 Y161.71 E.01631
G1 X159.887 Y162.138 E.01634
G1 X159.74 Y162.565 E.01718
G1 X159.463 Y162.993 E.01935
G1 X159.334 Y163.131 E.00717
G1 X159.334 Y167.099 E.15076
G1 X159.492 Y167.269 E.00879
G1 X159.759 Y167.696 E.01916
G1 X159.896 Y168.124 E.01706
G1 X159.935 Y168.551 E.01631
G1 X159.887 Y168.979 E.01635
G1 X159.74 Y169.406 E.01717
G1 X159.463 Y169.834 E.01935
G1 X159.334 Y169.972 E.00717
G1 X159.334 Y171.066 E.04155
G1 X159.835 Y171.066 E.01901
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.19009
G1 X159.334 Y169.972 E-.41563
G1 X159.463 Y169.834 E-.0717
G1 X159.581 Y169.652 E-.08259
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.746 Y162.333 Z24.36 F60000
G1 X163.443 Y156.593 Z24.36
G1 Z23.96
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z24.36 F60000
G1 Z23.96
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
; Z_HEIGHT: 24.2
; LAYER_HEIGHT: 0.240002
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 101/107
; update layer progress
M73 L101
M991 S0 P100 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z24.36 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z24.36
G1 Z24.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.741 Y154.321 Z24.6 F60000
G1 X160.466 Y149.635 Z24.6
G1 Z24.2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.466 Y148.934 E.02662
G1 X159.572 Y148.934 E.03394
G1 X159.334 Y149.223 E.01419
G1 X159.334 Y153.151 E.14923
G1 X159.714 Y153.587 E.02196
G1 X159.914 Y154.014 E.01793
G1 X159.979 Y154.442 E.01643
G1 X159.95 Y154.869 E.01628
G1 X159.834 Y155.297 E.01683
G1 X159.614 Y155.724 E.01827
G1 X159.334 Y156.064 E.0167
G1 X159.334 Y159.992 E.14923
G1 X159.714 Y160.428 E.02196
G1 X159.914 Y160.855 E.01793
G1 X159.979 Y161.283 E.01643
G1 X159.95 Y161.71 E.01628
G1 X159.834 Y162.138 E.01683
G1 X159.614 Y162.565 E.01827
G1 X159.334 Y162.905 E.0167
G1 X159.334 Y166.833 E.14923
G1 X159.714 Y167.269 E.02196
G1 X159.914 Y167.696 E.01793
G1 X159.979 Y168.124 E.01643
G1 X159.95 Y168.551 E.01628
G1 X159.834 Y168.979 E.01683
G1 X159.614 Y169.406 E.01827
G1 X159.334 Y169.746 E.01671
G1 X159.334 Y171.066 E.05015
G1 X159.609 Y171.066 E.01041
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.10416
G1 X159.334 Y169.746 E-.50155
G1 X159.593 Y169.432 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.785 Y162.122 Z24.6 F60000
G1 X163.443 Y156.593 Z24.6
G1 Z24.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
M73 P94 R0
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z24.6 F60000
G1 Z24.2
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
; Z_HEIGHT: 24.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 102/107
; update layer progress
M73 L102
M991 S0 P101 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z24.6 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z24.6
G1 Z24.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.879 Y154.421 Z24.84 F60000
G1 X159.334 Y151.302 Z24.84
G1 Z24.44
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.334 Y152.896 E.06056
G1 X159.637 Y153.159 E.01525
G1 X159.986 Y153.587 E.02096
G1 X160.106 Y154.014 E.01687
G1 X159.993 Y154.869 E.03277
G1 X159.807 Y155.297 E.01771
G1 X159.505 Y155.724 E.01989
G1 X159.334 Y155.873 E.00861
G1 X159.334 Y159.737 E.14679
G1 X159.637 Y160 E.01525
G1 X159.986 Y160.428 E.02096
G1 X160.106 Y160.855 E.01687
G1 X159.993 Y161.71 E.03277
G1 X159.807 Y162.138 E.01771
G1 X159.505 Y162.565 E.01989
G1 X159.334 Y162.714 E.00861
G1 X159.334 Y166.578 E.14679
G1 X159.637 Y166.841 E.01525
G1 X159.986 Y167.269 E.02096
G1 X160.106 Y167.696 E.01687
G1 X159.993 Y168.551 E.03277
G1 X159.807 Y168.979 E.01771
G1 X159.505 Y169.406 E.01989
G1 X159.334 Y169.555 E.00861
G1 X159.334 Y171.066 E.05739
G1 X159.418 Y171.066 E.00317
; COOLING_NODE: 0
; WIPE_START
G1 X159.334 Y171.066 E-.03175
G1 X159.334 Y169.555 E-.57397
G1 X159.505 Y169.406 E-.08611
G1 X159.609 Y169.26 E-.06818
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.82 Y161.955 Z24.84 F60000
G1 X163.443 Y156.593 Z24.84
G1 Z24.44
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z24.84 F60000
G1 Z24.44
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
; Z_HEIGHT: 24.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 103/107
; update layer progress
M73 L103
M991 S0 P102 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z24.84 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z24.84
G1 Z24.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.739 Y154.321 Z25.08 F60000
G1 X160.423 Y148.977 Z25.08
G1 Z24.68
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.419994
G1 F12000
M204 S8000
G1 X159.377 Y148.977 E.03675
G1 X159.377 Y171.023 E.77452
G1 X160.423 Y171.023 E.03675
G1 X160.423 Y149.037 E.77241
M204 S10000
G1 X160.069 Y149.5 F60000
; LINE_WIDTH: 0.390284
G1 F12000
M204 S8000
G1 X160.069 Y149.331 E.00547
G1 X159.731 Y149.331 E.01094
G1 X159.731 Y170.669 E.68923
G1 X160.069 Y170.669 E.01094
G1 X160.069 Y149.56 E.68182
; COOLING_NODE: 0
; WIPE_START
G1 X160.069 Y151.56 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y156.593 Z25.08 F60000
G1 Z24.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
M73 P95 R0
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z25.08 F60000
G1 Z24.68
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
; Z_HEIGHT: 24.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 104/107
; update layer progress
M73 L104
M991 S0 P103 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z25.08 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z25.08
G1 Z24.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.72 Y154.322 Z25.32 F60000
G1 X160.423 Y149.5 Z25.32
G1 Z24.92
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X160.423 Y148.977 E.01838
G1 X159.377 Y148.977 E.03675
G1 X159.377 Y171.023 E.77452
G1 X160.423 Y171.023 E.03675
G1 X160.423 Y149.56 E.75404
M204 S10000
G1 X160.069 Y149.5 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X160.069 Y149.331 E.00547
G1 X159.731 Y149.331 E.01094
G1 X159.731 Y170.669 E.68923
G1 X160.069 Y170.669 E.01094
G1 X160.069 Y149.56 E.68182
; COOLING_NODE: 0
; WIPE_START
G1 X160.069 Y151.56 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.443 Y156.593 Z25.32 F60000
G1 Z24.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09738
G1 X166.007 Y163.407 E.25885
G1 X163.443 Y163.407 E.09738
G1 X163.443 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.06 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X166.39 Y156.21 E.11699
G1 X166.39 Y163.79 E.2663
G1 X163.06 Y163.79 E.11699
G1 X163.06 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.06 Y156.234 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.827 Y163.023 Z25.32 F60000
G1 Z24.92
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
; Z_HEIGHT: 25.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F13032.524
G1 X164.552 Y160.238 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 105/107
; update layer progress
M73 L105
M991 S0 P104 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z25.32 I.077 J-1.215 P1  F60000
G1 X160.806 Y160 Z25.32
G1 Z25.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.72 Y154.322 Z25.56 F60000
G1 X160.423 Y149.5 Z25.56
G1 Z25.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X160.423 Y148.977 E.01838
G1 X159.377 Y148.977 E.03675
G1 X159.377 Y171.023 E.77452
G1 X160.423 Y171.023 E.03675
G1 X160.423 Y149.56 E.75404
M204 S10000
G1 X160.069 Y149.5 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X160.069 Y149.331 E.00547
G1 X159.731 Y149.331 E.01094
G1 X159.731 Y170.669 E.68923
G1 X160.069 Y170.669 E.01094
G1 X160.069 Y149.56 E.68182
; COOLING_NODE: 0
; WIPE_START
G1 X160.069 Y151.56 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.533 Y156.593 Z25.56 F60000
G1 Z25.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.09396
G1 X166.007 Y163.407 E.25885
G1 X163.533 Y163.407 E.09396
G1 X163.533 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.15 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P96 R0
G1 F11999
M204 S5000
G1 X166.39 Y156.21 E.11383
G1 X166.39 Y163.79 E.2663
G1 X163.15 Y163.79 E.11383
G1 X163.15 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.15 Y156.233 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.917 Y163.023 Z25.56 F60000
G1 Z25.16
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.05994
G1 X165.623 Y156.977 E.21241
G1 X163.917 Y156.977 E.05994
G1 X163.917 Y162.963 E.2103
M204 S10000
G1 X164.285 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X165.255 Y162.655 E.03405
G1 X165.255 Y157.345 E.18652
G1 X164.285 Y157.345 E.03405
G1 X164.285 Y162.595 E.18441
M204 S10000
G1 X164.62 Y162.32 F60000
; LINE_WIDTH: 0.351794
G1 F14985.516
M204 S8000
G1 X164.92 Y162.32 E.0086
G1 X164.92 Y157.68 E.13285
G1 X164.62 Y157.68 E.0086
G1 X164.62 Y162.26 E.13113
; CHANGE_LAYER
; Z_HEIGHT: 25.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F14985.516
G1 X164.62 Y160.26 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 106/107
; update layer progress
M73 L106
M991 S0 P105 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z25.56 I.083 J-1.214 P1  F60000
G1 X160.806 Y160 Z25.56
G1 Z25.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.806 Y171.407 E.43336
G1 X158.993 Y171.407 E.06888
G1 X158.993 Y148.593 E.86673
G1 X160.806 Y148.593 E.06888
G1 X160.806 Y159.94 E.43108
; COOLING_NODE: 0
M204 S250
G1 X161.19 Y160 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X160.72 Y154.322 Z25.8 F60000
G1 X160.423 Y149.5 Z25.8
G1 Z25.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X160.423 Y148.977 E.01838
G1 X159.377 Y148.977 E.03675
G1 X159.377 Y171.023 E.77452
G1 X160.423 Y171.023 E.03675
G1 X160.423 Y149.56 E.75404
M204 S10000
G1 X160.069 Y149.5 F60000
; LINE_WIDTH: 0.390284
G1 F13282.957
M204 S8000
G1 X160.069 Y149.331 E.00547
G1 X159.731 Y149.331 E.01094
G1 X159.731 Y170.669 E.68923
G1 X160.069 Y170.669 E.01094
G1 X160.069 Y149.56 E.68182
; COOLING_NODE: 0
; WIPE_START
G1 X160.069 Y151.56 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.773 Y156.593 Z25.8 F60000
G1 Z25.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.007 Y156.593 E.08484
G1 X166.007 Y163.407 E.25885
G1 X163.773 Y163.407 E.08484
G1 X163.773 Y156.653 E.25657
; COOLING_NODE: 0
M204 S250
G1 X163.39 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X166.39 Y156.21 E.1054
G1 X166.39 Y163.79 E.2663
G1 X163.39 Y163.79 E.1054
G1 X163.39 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.39 Y156.23 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.157 Y163.023 Z25.8 F60000
G1 Z25.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.623 Y163.023 E.05151
G1 X165.623 Y156.977 E.21241
G1 X164.157 Y156.977 E.05151
G1 X164.157 Y162.963 E.2103
M204 S10000
G1 X164.525 Y162.655 F60000
G1 F12212.001
M204 S8000
G1 X165.255 Y162.655 E.02561
G1 X165.255 Y157.345 E.18652
G1 X164.525 Y157.345 E.02561
G1 X164.525 Y162.595 E.18441
M204 S10000
G1 X164.89 Y162.29 F60000
; LINE_WIDTH: 0.412084
G1 F12479.894
M204 S8000
G1 X164.89 Y157.77 E.15539
; CHANGE_LAYER
; Z_HEIGHT: 25.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12479.894
G1 X164.89 Y159.77 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 107/107
; update layer progress
M73 L107
M991 S0 P106 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z25.8 I-.076 J-1.215 P1  F60000
G1 X161.19 Y160 Z25.8
G1 Z25.64
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X161.19 Y171.79 E.41421
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

G1 X158.61 Y171.79 E.09064
G1 X158.61 Y148.21 E.82842
G1 X161.19 Y148.21 E.09064
G1 X161.19 Y159.94 E.4121
; WIPE_START
G1 F12000
M204 S8000
G1 X161.19 Y161.94 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.068 Y154.309 Z26.04 F60000
G1 X160.986 Y149.187 Z26.04
G1 Z25.64
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X160.213 Y148.414 E.04154
G1 X160.069 Y148.271
G1 X159.506 Y148.271
G1 X159.649 Y148.414
G1 X160.986 Y149.751 E.07182
G1 X161.129 Y149.894
G1 X161.129 Y150.458
G1 X160.986 Y150.314
G1 X159.086 Y148.414 E.1021
G1 X158.942 Y148.271
G1 X158.671 Y148.563
G1 X158.814 Y148.706
G1 X160.986 Y150.878 E.11668
G1 X161.129 Y151.021
G1 X161.129 Y151.585
G1 X160.986 Y151.442
G1 X158.814 Y149.27 E.11668
G1 X158.671 Y149.127
G1 X158.671 Y149.69
G1 X158.814 Y149.833
G1 X160.986 Y152.005 E.11668
G1 X161.129 Y152.148
G1 X161.129 Y152.712
G1 X160.986 Y152.569
G1 X158.814 Y150.397 E.11668
G1 X158.671 Y150.254
G1 X158.671 Y150.817
G1 X158.814 Y150.96
G1 X160.986 Y153.132 E.11668
G1 X161.129 Y153.275
G1 X161.129 Y153.839
G1 X160.986 Y153.696
G1 X158.814 Y151.524 E.11668
G1 X158.671 Y151.381
G1 X158.671 Y151.944
G1 X158.814 Y152.088
G1 X160.986 Y154.259 E.11668
G1 X161.129 Y154.402
G1 X161.129 Y154.966
G1 X160.986 Y154.823
G1 X158.814 Y152.651 E.11668
G1 X158.671 Y152.508
G1 X158.671 Y153.072
G1 X158.814 Y153.215
G1 X160.986 Y155.386 E.11668
G1 X161.129 Y155.53
G1 X161.129 Y156.093
G1 X160.986 Y155.95
G1 X158.814 Y153.778 E.11668
G1 X158.671 Y153.635
G1 X158.671 Y154.199
G1 X158.814 Y154.342
G1 X160.986 Y156.513 E.11668
G1 X161.129 Y156.657
G1 X161.129 Y157.22
G1 X160.986 Y157.077
G1 X158.814 Y154.905 E.11668
G1 X158.671 Y154.762
G1 X158.671 Y155.326
G1 X158.814 Y155.469
G1 X160.986 Y157.641 E.11668
G1 X161.129 Y157.784
M73 P97 R0
G1 X161.129 Y158.347
G1 X160.986 Y158.204
G1 X158.814 Y156.032 E.11668
G1 X158.671 Y155.889
G1 X158.671 Y156.453
G1 X158.814 Y156.596
G1 X160.986 Y158.768 E.11668
G1 X161.129 Y158.911
G1 X161.129 Y159.474
G1 X160.986 Y159.331
G1 X158.814 Y157.16 E.11668
G1 X158.671 Y157.016
G1 X158.671 Y157.58
G1 X158.814 Y157.723
G1 X160.986 Y159.895 E.11668
G1 X161.129 Y160.038
G1 X161.129 Y160.601
G1 X160.986 Y160.458
G1 X158.814 Y158.287 E.11668
G1 X158.671 Y158.143
G1 X158.671 Y158.707
G1 X158.814 Y158.85
G1 X160.986 Y161.022 E.11668
G1 X161.129 Y161.165
G1 X161.129 Y161.729
G1 X160.986 Y161.585
G1 X158.814 Y159.414 E.11668
G1 X158.671 Y159.271
G1 X158.671 Y159.834
G1 X158.814 Y159.977
G1 X160.986 Y162.149 E.11668
G1 X161.129 Y162.292
G1 X161.129 Y162.856
G1 X160.986 Y162.713
G1 X158.814 Y160.541 E.11668
G1 X158.671 Y160.398
G1 X158.671 Y160.961
G1 X158.814 Y161.104
G1 X160.986 Y163.276 E.11668
G1 X161.129 Y163.419
G1 X161.129 Y163.983
G1 X160.986 Y163.84
G1 X158.814 Y161.668 E.11668
G1 X158.671 Y161.525
G1 X158.671 Y162.088
G1 X158.814 Y162.231
G1 X160.986 Y164.403 E.11668
G1 X161.129 Y164.546
G1 X161.129 Y165.11
G1 X160.986 Y164.967
G1 X158.814 Y162.795 E.11668
G1 X158.671 Y162.652
G1 X158.671 Y163.215
G1 X158.814 Y163.359
G1 X160.986 Y165.53 E.11668
G1 X161.129 Y165.673
G1 X161.129 Y166.237
G1 X160.986 Y166.094
G1 X158.814 Y163.922 E.11668
G1 X158.671 Y163.779
G1 X158.671 Y164.343
G1 X158.814 Y164.486
G1 X160.986 Y166.657 E.11668
G1 X161.129 Y166.801
G1 X161.129 Y167.364
G1 X160.986 Y167.221
G1 X158.814 Y165.049 E.11668
G1 X158.671 Y164.906
G1 X158.671 Y165.47
G1 X158.814 Y165.613
G1 X160.986 Y167.784 E.11668
G1 X161.129 Y167.928
G1 X161.129 Y168.491
G1 X160.986 Y168.348
G1 X158.814 Y166.176 E.11668
G1 X158.671 Y166.033
G1 X158.671 Y166.597
G1 X158.814 Y166.74
G1 X160.986 Y168.912 E.11668
G1 X161.129 Y169.055
G1 X161.129 Y169.618
G1 X160.986 Y169.475
G1 X158.814 Y167.303 E.11668
G1 X158.671 Y167.16
G1 X158.671 Y167.724
G1 X158.814 Y167.867
G1 X160.986 Y170.039 E.11668
G1 X161.129 Y170.182
M73 P98 R0
G1 X161.129 Y170.745
G1 X160.986 Y170.602
G1 X158.814 Y168.431 E.11668
G1 X158.671 Y168.287
G1 X158.671 Y168.851
G1 X158.814 Y168.994
G1 X160.986 Y171.166 E.11668
G1 X161.129 Y171.309
G1 X160.986 Y171.729
G1 X160.842 Y171.586
G1 X158.814 Y169.558 E.10897
G1 X158.671 Y169.414
G1 X158.671 Y169.978
G1 X158.814 Y170.121
G1 X160.279 Y171.586 E.07869
G1 X160.422 Y171.729
G1 X159.858 Y171.729
G1 X159.715 Y171.586
G1 X158.814 Y170.685 E.04842
; COOLING_NODE: 0
; WIPE_START
M204 S8000
G1 X159.715 Y171.586 E-.48425
G1 X159.858 Y171.729 E-.07695
G1 X160.382 Y171.729 E-.19881
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.945 Y164.258 Z26.04 F60000
G1 X163.63 Y156.21 Z26.04
G1 Z25.64
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X166.39 Y156.21 E.09697
G1 X166.39 Y163.79 E.2663
G1 X163.63 Y163.79 E.09697
G1 X163.63 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X165.63 Y156.227 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.186 Y157.205 Z26.04 F60000
G1 Z25.64
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X165.395 Y156.414 E.0425
G1 X165.252 Y156.271
G1 X164.688 Y156.271
G1 X164.831 Y156.414
G1 X166.186 Y157.769 E.07278
G1 X166.329 Y157.912
G1 X166.329 Y158.475
G1 X166.186 Y158.332
G1 X164.268 Y156.414 E.10305
G1 X164.125 Y156.271
G1 X163.691 Y156.401
G1 X163.834 Y156.544
G1 X166.186 Y158.896 E.12635
G1 X166.329 Y159.039
G1 X166.329 Y159.602
G1 X166.186 Y159.459
G1 X163.834 Y157.108 E.12635
G1 X163.691 Y156.964
G1 X163.691 Y157.528
G1 X163.834 Y157.671
G1 X166.186 Y160.023 E.12635
G1 X166.329 Y160.166
G1 X166.329 Y160.73
G1 X166.186 Y160.586
G1 X163.834 Y158.235 E.12635
G1 X163.691 Y158.092
G1 X163.691 Y158.655
G1 X163.834 Y158.798
G1 X166.186 Y161.15 E.12635
G1 X166.329 Y161.293
G1 X166.329 Y161.857
G1 X166.186 Y161.713
G1 X163.834 Y159.362 E.12635
G1 X163.691 Y159.219
G1 X163.691 Y159.782
G1 X163.834 Y159.925
G1 X166.186 Y162.277 E.12635
G1 X166.329 Y162.42
G1 X166.329 Y162.984
G1 X166.186 Y162.841
G1 X163.834 Y160.489 E.12635
G1 X163.691 Y160.346
G1 X163.691 Y160.909
G1 X163.834 Y161.052
G1 X166.186 Y163.404 E.12635
G1 X166.329 Y163.547
G1 X165.947 Y163.729
G1 X165.804 Y163.586
G1 X163.834 Y161.616 E.10584
G1 X163.691 Y161.473
G1 X163.691 Y162.036
G1 X163.834 Y162.18
G1 X165.24 Y163.586 E.07556
G1 X165.384 Y163.729
G1 X164.82 Y163.729
G1 X164.677 Y163.586
G1 X163.834 Y162.743 E.04528
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F11292.473
M204 S8000
G1 X164.677 Y163.586 E-.45288
G1 X164.82 Y163.729 E-.07695
G1 X165.384 Y163.729 E-.21415
G1 X165.354 Y163.699 E-.01603
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z26.04 I1.217 J0 P1  F60000
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
G1 Z26.04 F900 ; lower z a little
M1002 judge_flag timelapse_record_flag
M622 J1
    G150.3
    M400 ; wait all motion done
    M991 S0 P-1 ;end smooth timelapse at safe pos
    M400 S5 ;wait for last picture to be taken
M623  ;end of "timelapse_record_flag"

G90
G1 Z35.64 F900 ; lower z a little

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

    
        G1 Z112.82 F600
        G1 Z110.82
    

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

