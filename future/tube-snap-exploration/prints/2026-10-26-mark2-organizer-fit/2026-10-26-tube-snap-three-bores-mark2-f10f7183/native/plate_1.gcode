; HEADER_BLOCK_START
; BambuStudio 02.08.02.61
; model printing time: 6m 56s; total estimated time: 12m 7s
; total layer number: 44
; total filament length [mm] : 967.90
; total filament volume [cm^3] : 2328.08
; total filament weight [g] : 3.00
; filament_density: 1.29
; filament_diameter: 1.75
; max_z_height: 10.52
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
M73 P0 R12
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
    
M73 P2 R11
    G1 E-3 F1800
    M400 P500
    G150.2
    G150.1


G91
M73 P4 R11
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
M73 P40 R7
G1 X175 Y160 F30000

M622 J1
    M1002 gcode_claim_action : 1
    G29.20 A3
    G29 A1 O X135.5 Y153 I54 J14 R
    M400
M623

M622 J2
    M1002 gcode_claim_action : 1
    
        G29.20 A4
        G29 A2 O X135.5 Y153 I54 J14 R
    
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
M73 P41 R7
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
; layer num/total_layer_count: 1/44
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
; OBJECT_ID: 1901
G1 X188.643 Y166.143 F60000
M204 S6000
M73 P42 R6
G1 Z.4
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X136.357 Y166.143 E1.89876
G1 X136.357 Y153.857 E.44616
G1 X188.643 Y153.857 E1.89876
G1 X188.643 Y166.083 E.44398
M204 S6000
G1 X189.1 Y166.6 F60000
; FEATURE: Outer wall
G1 F3000
M204 S500
M73 P43 R6
G1 X135.9 Y166.6 E1.93196
G1 X135.9 Y153.4 E.47936
G1 X189.1 Y153.4 E1.93196
G1 X189.1 Y166.54 E.47718
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
G1 X187.1 Y166.542 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X187.361 Y158.914 Z.6 F60000
G1 X187.527 Y154.04 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50421
G1 F6300
M204 S500
G1 X188.254 Y154.767 E.03769
G1 X188.254 Y155.419 E.02391
G1 X187.081 Y154.246 E.06084
G1 X186.428 Y154.246 E.02391
G1 X188.254 Y156.072 E.09466
G1 X188.254 Y156.724 E.02391
G1 X185.776 Y154.246 E.12847
G1 X185.123 Y154.246 E.02391
G1 X188.254 Y157.377 E.16228
G1 X188.254 Y158.029 E.02391
G1 X184.471 Y154.246 E.19609
G1 X183.819 Y154.246 E.02391
G1 X188.254 Y158.681 E.2299
G1 X188.254 Y159.334 E.02391
G1 X183.166 Y154.246 E.26372
G1 X182.514 Y154.246 E.02391
G1 X188.254 Y159.986 E.29753
G1 X188.254 Y160.638 E.02391
G1 X181.862 Y154.246 E.33134
G1 X181.209 Y154.246 E.02391
G1 X188.254 Y161.291 E.36515
G1 X188.254 Y161.943 E.02391
G1 X180.557 Y154.246 E.39896
G1 X179.905 Y154.246 E.02391
G1 X188.254 Y162.595 E.43278
G1 X188.254 Y163.248 E.02391
G1 X179.252 Y154.246 E.46659
G1 X178.6 Y154.246 E.02391
G1 X188.254 Y163.9 E.5004
G1 X188.254 Y164.553 E.02391
G1 X177.947 Y154.246 E.53421
M73 P44 R6
G1 X177.295 Y154.246 E.02391
G1 X188.254 Y165.205 E.56803
G1 X188.254 Y165.754 E.02014
G1 X188.152 Y165.754 E.00377
G1 X176.643 Y154.246 E.59651
G1 X175.99 Y154.246 E.02391
G1 X187.499 Y165.754 E.59651
G1 X186.847 Y165.754 E.02391
G1 X175.338 Y154.246 E.59651
G1 X174.686 Y154.246 E.02391
G1 X186.194 Y165.754 E.59651
G1 X185.542 Y165.754 E.02391
G1 X174.033 Y154.246 E.59651
G1 X173.381 Y154.246 E.02391
G1 X184.89 Y165.754 E.59651
G1 X184.237 Y165.754 E.02391
G1 X172.729 Y154.246 E.59651
G1 X172.076 Y154.246 E.02391
G1 X183.585 Y165.754 E.59651
G1 X182.933 Y165.754 E.02391
G1 X171.424 Y154.246 E.59651
G1 X170.771 Y154.246 E.02391
G1 X182.28 Y165.754 E.59651
G1 X181.628 Y165.754 E.02391
G1 X170.119 Y154.246 E.59651
G1 X169.467 Y154.246 E.02391
G1 X180.976 Y165.754 E.59651
G1 X180.323 Y165.754 E.02391
G1 X168.814 Y154.246 E.59651
G1 X168.162 Y154.246 E.02391
G1 X179.671 Y165.754 E.59651
G1 X179.018 Y165.754 E.02391
G1 X167.51 Y154.246 E.59651
G1 X166.857 Y154.246 E.02391
G1 X178.366 Y165.754 E.59651
G1 X177.714 Y165.754 E.02391
G1 X166.205 Y154.246 E.59651
G1 X165.553 Y154.246 E.02391
G1 X177.061 Y165.754 E.59651
G1 X176.409 Y165.754 E.02391
M73 P45 R6
G1 X164.9 Y154.246 E.59651
G1 X164.248 Y154.246 E.02391
G1 X175.757 Y165.754 E.59651
G1 X175.104 Y165.754 E.02391
G1 X163.595 Y154.246 E.59651
G1 X162.943 Y154.246 E.02391
G1 X174.452 Y165.754 E.59651
G1 X173.8 Y165.754 E.02391
G1 X162.291 Y154.246 E.59651
G1 X161.638 Y154.246 E.02391
G1 X173.147 Y165.754 E.59651
G1 X172.495 Y165.754 E.02391
G1 X160.986 Y154.246 E.59651
G1 X160.334 Y154.246 E.02391
G1 X171.843 Y165.754 E.59651
G1 X171.19 Y165.754 E.02391
G1 X159.681 Y154.246 E.59651
G1 X159.029 Y154.246 E.02391
G1 X170.538 Y165.754 E.59651
G1 X169.885 Y165.754 E.02391
G1 X158.377 Y154.246 E.59651
G1 X157.724 Y154.246 E.02391
G1 X169.233 Y165.754 E.59651
G1 X168.581 Y165.754 E.02391
G1 X157.072 Y154.246 E.59651
G1 X156.419 Y154.246 E.02391
G1 X167.928 Y165.754 E.59651
G1 X167.276 Y165.754 E.02391
G1 X155.767 Y154.246 E.59651
G1 X155.115 Y154.246 E.02391
G1 X166.624 Y165.754 E.59651
G1 X165.971 Y165.754 E.02391
G1 X154.462 Y154.246 E.59651
G1 X153.81 Y154.246 E.02391
G1 X165.319 Y165.754 E.59651
G1 X164.667 Y165.754 E.02391
G1 X153.158 Y154.246 E.59651
G1 X152.505 Y154.246 E.02391
G1 X164.014 Y165.754 E.59651
G1 X163.362 Y165.754 E.02391
M73 P46 R6
G1 X151.853 Y154.246 E.59651
G1 X151.201 Y154.246 E.02391
G1 X162.709 Y165.754 E.59651
G1 X162.057 Y165.754 E.02391
G1 X150.548 Y154.246 E.59651
G1 X149.896 Y154.246 E.02391
G1 X161.405 Y165.754 E.59651
G1 X160.752 Y165.754 E.02391
G1 X149.243 Y154.246 E.59651
G1 X148.591 Y154.246 E.02391
G1 X160.1 Y165.754 E.59651
G1 X159.448 Y165.754 E.02391
G1 X147.939 Y154.246 E.59651
G1 X147.286 Y154.246 E.02391
G1 X158.795 Y165.754 E.59651
G1 X158.143 Y165.754 E.02391
G1 X146.634 Y154.246 E.59651
G1 X145.982 Y154.246 E.02391
G1 X157.491 Y165.754 E.59651
G1 X156.838 Y165.754 E.02391
G1 X145.329 Y154.246 E.59651
G1 X144.677 Y154.246 E.02391
G1 X156.186 Y165.754 E.59651
G1 X155.533 Y165.754 E.02391
G1 X144.025 Y154.246 E.59651
G1 X143.372 Y154.246 E.02391
G1 X154.881 Y165.754 E.59651
G1 X154.229 Y165.754 E.02391
G1 X142.72 Y154.246 E.59651
G1 X142.068 Y154.246 E.02391
G1 X153.576 Y165.754 E.59651
G1 X152.924 Y165.754 E.02391
G1 X141.415 Y154.246 E.59651
G1 X140.763 Y154.246 E.02391
G1 X152.272 Y165.754 E.59651
G1 X151.619 Y165.754 E.02391
G1 X140.11 Y154.246 E.59651
G1 X139.458 Y154.246 E.02391
M73 P47 R6
G1 X150.967 Y165.754 E.59651
G1 X150.315 Y165.754 E.02391
G1 X138.806 Y154.246 E.59651
G1 X138.153 Y154.246 E.02391
G1 X149.662 Y165.754 E.59651
G1 X149.01 Y165.754 E.02391
G1 X137.501 Y154.246 E.59651
G1 X136.849 Y154.246 E.02391
G1 X148.357 Y165.754 E.59651
G1 X147.705 Y165.754 E.02391
G1 X136.746 Y154.795 E.56804
G1 X136.746 Y155.447 E.02391
G1 X147.053 Y165.754 E.53422
G1 X146.4 Y165.754 E.02391
G1 X136.746 Y156.1 E.50041
G1 X136.746 Y156.752 E.02391
G1 X145.748 Y165.754 E.4666
G1 X145.096 Y165.754 E.02391
G1 X136.746 Y157.404 E.43279
G1 X136.746 Y158.057 E.02391
G1 X144.443 Y165.754 E.39897
G1 X143.791 Y165.754 E.02391
G1 X136.746 Y158.709 E.36516
G1 X136.746 Y159.361 E.02391
G1 X143.139 Y165.754 E.33135
G1 X142.486 Y165.754 E.02391
G1 X136.746 Y160.014 E.29754
G1 X136.746 Y160.666 E.02391
G1 X141.834 Y165.754 E.26373
G1 X141.181 Y165.754 E.02391
G1 X136.746 Y161.319 E.22991
G1 X136.746 Y161.971 E.02391
G1 X140.529 Y165.754 E.1961
G1 X139.877 Y165.754 E.02391
G1 X136.746 Y162.623 E.16229
G1 X136.746 Y163.276 E.02391
G1 X139.224 Y165.754 E.12848
G1 X138.572 Y165.754 E.02391
G1 X136.746 Y163.928 E.09467
G1 X136.746 Y164.58 E.02391
G1 X137.92 Y165.754 E.06085
G1 X137.267 Y165.754 E.02391
G1 X136.54 Y165.027 E.0377
; CHANGE_LAYER
; Z_HEIGHT: 0.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F6300
G1 X137.267 Y165.754 E-.39091
G1 X137.92 Y165.754 E-.2479
G1 X137.694 Y165.529 E-.1212
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 2/44
; update layer progress
M73 L2
M991 S0 P1 ;notify layer change
; open powerlost recovery
M1003 S1
M104 S280 ; set nozzle temperature
; OBJECT_ID: 1901
M204 S10000
G17
G3 Z.6 I-.021 J1.217 P1  F60000
G1 X188.907 Y166.407 Z.6
G1 Z.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
M204 S250
M73 P48 R6
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X187.996 Y166.246 Z.84 F60000
G1 Z.44
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422494
G1 F12129.707
M204 S8000
G1 X188.581 Y165.662 E.02923
G1 X188.581 Y165.137 E.01856
G1 X187.637 Y166.081 E.04718
G1 X187.113 Y166.081 E.01856
G1 X188.581 Y164.613 E.07343
G1 X188.581 Y164.088 E.01856
G1 X186.588 Y166.081 E.09967
G1 X186.063 Y166.081 E.01856
G1 X188.581 Y163.563 E.12591
G1 X188.581 Y163.039 E.01856
G1 X185.539 Y166.081 E.15216
G1 X185.014 Y166.081 E.01856
G1 X188.581 Y162.514 E.1784
G1 X188.581 Y161.989 E.01856
G1 X184.489 Y166.081 E.20465
G1 X183.965 Y166.081 E.01856
G1 X188.581 Y161.465 E.23089
G1 X188.581 Y160.94 E.01856
G1 X183.44 Y166.081 E.25713
G1 X182.915 Y166.081 E.01856
G1 X188.581 Y160.415 E.28338
G1 X188.581 Y159.891 E.01856
G1 X182.391 Y166.081 E.30962
G1 X181.866 Y166.081 E.01856
G1 X188.581 Y159.366 E.33587
G1 X188.581 Y158.841 E.01856
G1 X181.341 Y166.081 E.36211
G1 X180.817 Y166.081 E.01856
G1 X188.581 Y158.317 E.38835
G1 X188.581 Y157.792 E.01856
G1 X180.292 Y166.081 E.4146
G1 X179.767 Y166.081 E.01856
G1 X188.581 Y157.267 E.44084
G1 X188.581 Y156.743 E.01856
G1 X179.243 Y166.081 E.46709
G1 X178.718 Y166.081 E.01856
G1 X188.581 Y156.218 E.49333
G1 X188.581 Y155.693 E.01856
G1 X178.193 Y166.081 E.51957
G1 X177.669 Y166.081 E.01856
G1 X188.581 Y155.169 E.54582
G1 X188.581 Y154.644 E.01856
G1 X177.144 Y166.081 E.57206
G1 X176.619 Y166.081 E.01856
G1 X188.581 Y154.12 E.59831
G1 X188.581 Y153.919 E.00708
G1 X188.256 Y153.919 E.01148
G1 X176.095 Y166.081 E.60832
G1 X175.57 Y166.081 E.01856
G1 X187.731 Y153.919 E.60832
G1 X187.207 Y153.919 E.01856
G1 X175.046 Y166.081 E.60832
G1 X174.521 Y166.081 E.01856
G1 X186.682 Y153.919 E.60832
G1 X186.157 Y153.919 E.01856
G1 X173.996 Y166.081 E.60832
G1 X173.472 Y166.081 E.01856
G1 X185.633 Y153.919 E.60832
G1 X185.108 Y153.919 E.01856
G1 X172.947 Y166.081 E.60832
G1 X172.422 Y166.081 E.01856
G1 X184.583 Y153.919 E.60832
G1 X184.059 Y153.919 E.01856
G1 X171.898 Y166.081 E.60832
G1 X171.373 Y166.081 E.01856
G1 X183.534 Y153.919 E.60832
G1 X183.009 Y153.919 E.01856
G1 X170.848 Y166.081 E.60832
G1 X170.324 Y166.081 E.01856
G1 X182.485 Y153.919 E.60832
G1 X181.96 Y153.919 E.01856
G1 X169.799 Y166.081 E.60832
G1 X169.274 Y166.081 E.01856
G1 X181.435 Y153.919 E.60832
G1 X180.911 Y153.919 E.01856
G1 X168.75 Y166.081 E.60832
G1 X168.225 Y166.081 E.01856
G1 X180.386 Y153.919 E.60832
G1 X179.861 Y153.919 E.01856
G1 X167.7 Y166.081 E.60832
G1 X167.176 Y166.081 E.01856
G1 X179.337 Y153.919 E.60832
G1 X178.812 Y153.919 E.01856
G1 X166.651 Y166.081 E.60832
G1 X166.126 Y166.081 E.01856
G1 X178.287 Y153.919 E.60832
G1 X177.763 Y153.919 E.01856
G1 X165.602 Y166.081 E.60832
G1 X165.077 Y166.081 E.01856
G1 X177.238 Y153.919 E.60832
G1 X176.714 Y153.919 E.01856
G1 X164.552 Y166.081 E.60832
G1 X164.028 Y166.081 E.01856
G1 X176.189 Y153.919 E.60832
G1 X175.664 Y153.919 E.01856
G1 X163.503 Y166.081 E.60832
G1 X162.978 Y166.081 E.01856
G1 X175.14 Y153.919 E.60832
G1 X174.615 Y153.919 E.01856
G1 X162.454 Y166.081 E.60832
G1 X161.929 Y166.081 E.01856
G1 X174.09 Y153.919 E.60832
G1 X173.566 Y153.919 E.01856
G1 X161.404 Y166.081 E.60832
G1 X160.88 Y166.081 E.01856
G1 X173.041 Y153.919 E.60832
G1 X172.516 Y153.919 E.01856
G1 X160.355 Y166.081 E.60832
G1 X159.83 Y166.081 E.01856
G1 X171.992 Y153.919 E.60832
G1 X171.467 Y153.919 E.01856
G1 X159.306 Y166.081 E.60832
G1 X158.781 Y166.081 E.01856
M73 P49 R6
G1 X170.942 Y153.919 E.60832
G1 X170.418 Y153.919 E.01856
G1 X158.256 Y166.081 E.60832
G1 X157.732 Y166.081 E.01856
G1 X169.893 Y153.919 E.60832
G1 X169.368 Y153.919 E.01856
G1 X157.207 Y166.081 E.60832
G1 X156.682 Y166.081 E.01856
G1 X168.844 Y153.919 E.60832
G1 X168.319 Y153.919 E.01856
G1 X156.158 Y166.081 E.60832
G1 X155.633 Y166.081 E.01856
G1 X167.794 Y153.919 E.60832
G1 X167.27 Y153.919 E.01856
G1 X155.108 Y166.081 E.60832
G1 X154.584 Y166.081 E.01856
G1 X166.745 Y153.919 E.60832
G1 X166.22 Y153.919 E.01856
G1 X154.059 Y166.081 E.60832
G1 X153.534 Y166.081 E.01856
G1 X165.696 Y153.919 E.60832
G1 X165.171 Y153.919 E.01856
G1 X153.01 Y166.081 E.60832
G1 X152.485 Y166.081 E.01856
G1 X164.646 Y153.919 E.60832
G1 X164.122 Y153.919 E.01856
G1 X151.961 Y166.081 E.60832
G1 X151.436 Y166.081 E.01856
G1 X163.597 Y153.919 E.60832
G1 X163.072 Y153.919 E.01856
G1 X150.911 Y166.081 E.60832
G1 X150.387 Y166.081 E.01856
G1 X162.548 Y153.919 E.60832
G1 X162.023 Y153.919 E.01856
G1 X149.862 Y166.081 E.60832
G1 X149.337 Y166.081 E.01856
G1 X161.498 Y153.919 E.60832
G1 X160.974 Y153.919 E.01856
G1 X148.813 Y166.081 E.60832
G1 X148.288 Y166.081 E.01856
G1 X160.449 Y153.919 E.60832
G1 X159.924 Y153.919 E.01856
G1 X147.763 Y166.081 E.60832
G1 X147.239 Y166.081 E.01856
G1 X159.4 Y153.919 E.60832
G1 X158.875 Y153.919 E.01856
G1 X146.714 Y166.081 E.60832
G1 X146.189 Y166.081 E.01856
G1 X158.35 Y153.919 E.60832
G1 X157.826 Y153.919 E.01856
G1 X145.665 Y166.081 E.60832
G1 X145.14 Y166.081 E.01856
G1 X157.301 Y153.919 E.60832
G1 X156.776 Y153.919 E.01856
G1 X144.615 Y166.081 E.60832
G1 X144.091 Y166.081 E.01856
G1 X156.252 Y153.919 E.60832
G1 X155.727 Y153.919 E.01856
G1 X143.566 Y166.081 E.60832
G1 X143.041 Y166.081 E.01856
G1 X155.202 Y153.919 E.60832
G1 X154.678 Y153.919 E.01856
G1 X142.517 Y166.081 E.60832
G1 X141.992 Y166.081 E.01856
G1 X154.153 Y153.919 E.60832
G1 X153.629 Y153.919 E.01856
G1 X141.467 Y166.081 E.60832
G1 X140.943 Y166.081 E.01856
G1 X153.104 Y153.919 E.60832
G1 X152.579 Y153.919 E.01856
G1 X140.418 Y166.081 E.60832
G1 X139.893 Y166.081 E.01856
G1 X152.055 Y153.919 E.60832
G1 X151.53 Y153.919 E.01856
G1 X139.369 Y166.081 E.60832
G1 X138.844 Y166.081 E.01856
G1 X151.005 Y153.919 E.60832
G1 X150.481 Y153.919 E.01856
G1 X138.319 Y166.081 E.60832
G1 X137.795 Y166.081 E.01856
G1 X149.956 Y153.919 E.60832
G1 X149.431 Y153.919 E.01856
G1 X137.27 Y166.081 E.60832
G1 X136.745 Y166.081 E.01856
G1 X148.907 Y153.919 E.60832
G1 X148.382 Y153.919 E.01856
G1 X136.419 Y165.882 E.59838
G1 X136.419 Y165.357 E.01856
G1 X147.857 Y153.919 E.57213
G1 X147.333 Y153.919 E.01856
G1 X136.419 Y164.833 E.54589
G1 X136.419 Y164.308 E.01856
G1 X146.808 Y153.919 E.51965
G1 X146.283 Y153.919 E.01856
G1 X136.419 Y163.783 E.4934
G1 X136.419 Y163.259 E.01856
G1 X145.759 Y153.919 E.46716
G1 X145.234 Y153.919 E.01856
G1 X136.419 Y162.734 E.44091
G1 X136.419 Y162.209 E.01856
G1 X144.709 Y153.919 E.41467
G1 X144.185 Y153.919 E.01856
G1 X136.419 Y161.685 E.38843
G1 X136.419 Y161.16 E.01856
G1 X143.66 Y153.919 E.36218
G1 X143.135 Y153.919 E.01856
G1 X136.419 Y160.635 E.33594
G1 X136.419 Y160.111 E.01856
G1 X142.611 Y153.919 E.30969
G1 X142.086 Y153.919 E.01856
G1 X136.419 Y159.586 E.28345
G1 X136.419 Y159.061 E.01856
G1 X141.561 Y153.919 E.25721
G1 X141.037 Y153.919 E.01856
G1 X136.419 Y158.537 E.23096
G1 X136.419 Y158.012 E.01856
G1 X140.512 Y153.919 E.20472
G1 X139.987 Y153.919 E.01856
G1 X136.419 Y157.487 E.17847
G1 X136.419 Y156.963 E.01856
G1 X139.463 Y153.919 E.15223
G1 X138.938 Y153.919 E.01856
G1 X136.419 Y156.438 E.12599
G1 X136.419 Y155.913 E.01856
G1 X138.413 Y153.919 E.09974
G1 X137.889 Y153.919 E.01856
G1 X136.419 Y155.389 E.0735
G1 X136.419 Y154.864 E.01856
G1 X137.364 Y153.919 E.04725
G1 X136.839 Y153.919 E.01856
G1 X136.254 Y154.505 E.0293
; CHANGE_LAYER
; Z_HEIGHT: 0.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12129.707
G1 X136.839 Y153.919 E-.31483
G1 X137.364 Y153.919 E-.19937
M73 P50 R6
G1 X136.907 Y154.377 E-.2458
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 3/44
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z.84 I-.274 J1.186 P1  F60000
G1 X188.907 Y166.407 Z.84
G1 Z.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X188.193 Y159.153 Z1.08 F60000
G1 X188.746 Y154.504 Z1.08
G1 Z.68
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422494
G1 F12129.707
M204 S8000
G1 X188.162 Y153.919 E.02923
G1 X187.637 Y153.919 E.01856
G1 X188.581 Y154.863 E.04718
G1 X188.581 Y155.387 E.01856
G1 X187.113 Y153.919 E.07343
G1 X186.588 Y153.919 E.01856
G1 X188.581 Y155.912 E.09967
G1 X188.581 Y156.437 E.01856
G1 X186.063 Y153.919 E.12591
G1 X185.539 Y153.919 E.01856
G1 X188.581 Y156.961 E.15216
G1 X188.581 Y157.486 E.01856
G1 X185.014 Y153.919 E.1784
G1 X184.489 Y153.919 E.01856
G1 X188.581 Y158.011 E.20465
G1 X188.581 Y158.535 E.01856
G1 X183.965 Y153.919 E.23089
G1 X183.44 Y153.919 E.01856
G1 X188.581 Y159.06 E.25713
G1 X188.581 Y159.585 E.01856
G1 X182.915 Y153.919 E.28338
G1 X182.391 Y153.919 E.01856
G1 X188.581 Y160.109 E.30962
G1 X188.581 Y160.634 E.01856
G1 X181.866 Y153.919 E.33587
G1 X181.341 Y153.919 E.01856
G1 X188.581 Y161.159 E.36211
G1 X188.581 Y161.683 E.01856
G1 X180.817 Y153.919 E.38835
G1 X180.292 Y153.919 E.01856
G1 X188.581 Y162.208 E.4146
G1 X188.581 Y162.733 E.01856
G1 X179.767 Y153.919 E.44084
G1 X179.243 Y153.919 E.01856
G1 X188.581 Y163.257 E.46709
G1 X188.581 Y163.782 E.01856
G1 X178.718 Y153.919 E.49333
G1 X178.193 Y153.919 E.01856
G1 X188.581 Y164.307 E.51957
G1 X188.581 Y164.831 E.01856
G1 X177.669 Y153.919 E.54582
G1 X177.144 Y153.919 E.01856
G1 X188.581 Y165.356 E.57206
G1 X188.581 Y165.881 E.01856
G1 X176.619 Y153.919 E.59831
G1 X176.095 Y153.919 E.01856
G1 X188.256 Y166.081 E.60832
G1 X187.731 Y166.081 E.01856
G1 X175.57 Y153.919 E.60832
G1 X175.046 Y153.919 E.01856
G1 X187.207 Y166.081 E.60832
G1 X186.682 Y166.081 E.01856
G1 X174.521 Y153.919 E.60832
G1 X173.996 Y153.919 E.01856
M73 P50 R5
G1 X186.157 Y166.081 E.60832
G1 X185.633 Y166.081 E.01856
G1 X173.472 Y153.919 E.60832
G1 X172.947 Y153.919 E.01856
G1 X185.108 Y166.081 E.60832
G1 X184.583 Y166.081 E.01856
G1 X172.422 Y153.919 E.60832
G1 X171.898 Y153.919 E.01856
G1 X184.059 Y166.081 E.60832
G1 X183.534 Y166.081 E.01856
G1 X171.373 Y153.919 E.60832
G1 X170.848 Y153.919 E.01856
G1 X183.009 Y166.081 E.60832
G1 X182.485 Y166.081 E.01856
G1 X170.324 Y153.919 E.60832
G1 X169.799 Y153.919 E.01856
G1 X181.96 Y166.081 E.60832
G1 X181.435 Y166.081 E.01856
G1 X169.274 Y153.919 E.60832
G1 X168.75 Y153.919 E.01856
G1 X180.911 Y166.081 E.60832
G1 X180.386 Y166.081 E.01856
G1 X168.225 Y153.919 E.60832
G1 X167.7 Y153.919 E.01856
G1 X179.861 Y166.081 E.60832
G1 X179.337 Y166.081 E.01856
G1 X167.176 Y153.919 E.60832
G1 X166.651 Y153.919 E.01856
G1 X178.812 Y166.081 E.60832
G1 X178.287 Y166.081 E.01856
G1 X166.126 Y153.919 E.60832
G1 X165.602 Y153.919 E.01856
G1 X177.763 Y166.081 E.60832
G1 X177.238 Y166.081 E.01856
G1 X165.077 Y153.919 E.60832
G1 X164.552 Y153.919 E.01856
G1 X176.714 Y166.081 E.60832
G1 X176.189 Y166.081 E.01856
G1 X164.028 Y153.919 E.60832
G1 X163.503 Y153.919 E.01856
G1 X175.664 Y166.081 E.60832
G1 X175.14 Y166.081 E.01856
G1 X162.978 Y153.919 E.60832
G1 X162.454 Y153.919 E.01856
G1 X174.615 Y166.081 E.60832
G1 X174.09 Y166.081 E.01856
G1 X161.929 Y153.919 E.60832
G1 X161.404 Y153.919 E.01856
G1 X173.566 Y166.081 E.60832
G1 X173.041 Y166.081 E.01856
M73 P51 R5
G1 X160.88 Y153.919 E.60832
G1 X160.355 Y153.919 E.01856
G1 X172.516 Y166.081 E.60832
G1 X171.992 Y166.081 E.01856
G1 X159.83 Y153.919 E.60832
G1 X159.306 Y153.919 E.01856
G1 X171.467 Y166.081 E.60832
G1 X170.942 Y166.081 E.01856
G1 X158.781 Y153.919 E.60832
G1 X158.256 Y153.919 E.01856
G1 X170.418 Y166.081 E.60832
G1 X169.893 Y166.081 E.01856
G1 X157.732 Y153.919 E.60832
G1 X157.207 Y153.919 E.01856
G1 X169.368 Y166.081 E.60832
G1 X168.844 Y166.081 E.01856
G1 X156.682 Y153.919 E.60832
G1 X156.158 Y153.919 E.01856
G1 X168.319 Y166.081 E.60832
G1 X167.794 Y166.081 E.01856
G1 X155.633 Y153.919 E.60832
G1 X155.108 Y153.919 E.01856
G1 X167.27 Y166.081 E.60832
G1 X166.745 Y166.081 E.01856
G1 X154.584 Y153.919 E.60832
G1 X154.059 Y153.919 E.01856
G1 X166.22 Y166.081 E.60832
G1 X165.696 Y166.081 E.01856
G1 X153.534 Y153.919 E.60832
G1 X153.01 Y153.919 E.01856
G1 X165.171 Y166.081 E.60832
G1 X164.646 Y166.081 E.01856
G1 X152.485 Y153.919 E.60832
G1 X151.961 Y153.919 E.01856
G1 X164.122 Y166.081 E.60832
G1 X163.597 Y166.081 E.01856
G1 X151.436 Y153.919 E.60832
G1 X150.911 Y153.919 E.01856
G1 X163.072 Y166.081 E.60832
G1 X162.548 Y166.081 E.01856
G1 X150.387 Y153.919 E.60832
G1 X149.862 Y153.919 E.01856
G1 X162.023 Y166.081 E.60832
G1 X161.498 Y166.081 E.01856
G1 X149.337 Y153.919 E.60832
G1 X148.813 Y153.919 E.01856
G1 X160.974 Y166.081 E.60832
G1 X160.449 Y166.081 E.01856
G1 X148.288 Y153.919 E.60832
G1 X147.763 Y153.919 E.01856
G1 X159.924 Y166.081 E.60832
G1 X159.4 Y166.081 E.01856
G1 X147.239 Y153.919 E.60832
G1 X146.714 Y153.919 E.01856
G1 X158.875 Y166.081 E.60832
G1 X158.35 Y166.081 E.01856
G1 X146.189 Y153.919 E.60832
G1 X145.665 Y153.919 E.01856
G1 X157.826 Y166.081 E.60832
G1 X157.301 Y166.081 E.01856
G1 X145.14 Y153.919 E.60832
G1 X144.615 Y153.919 E.01856
G1 X156.776 Y166.081 E.60832
G1 X156.252 Y166.081 E.01856
G1 X144.091 Y153.919 E.60832
G1 X143.566 Y153.919 E.01856
G1 X155.727 Y166.081 E.60832
G1 X155.202 Y166.081 E.01856
G1 X143.041 Y153.919 E.60832
G1 X142.517 Y153.919 E.01856
G1 X154.678 Y166.081 E.60832
G1 X154.153 Y166.081 E.01856
G1 X141.992 Y153.919 E.60832
G1 X141.467 Y153.919 E.01856
G1 X153.629 Y166.081 E.60832
G1 X153.104 Y166.081 E.01856
G1 X140.943 Y153.919 E.60832
G1 X140.418 Y153.919 E.01856
G1 X152.579 Y166.081 E.60832
G1 X152.055 Y166.081 E.01856
G1 X139.893 Y153.919 E.60832
G1 X139.369 Y153.919 E.01856
G1 X151.53 Y166.081 E.60832
G1 X151.005 Y166.081 E.01856
G1 X138.844 Y153.919 E.60832
G1 X138.319 Y153.919 E.01856
G1 X150.481 Y166.081 E.60832
G1 X149.956 Y166.081 E.01856
G1 X137.795 Y153.919 E.60832
G1 X137.27 Y153.919 E.01856
G1 X149.431 Y166.081 E.60832
G1 X148.907 Y166.081 E.01856
G1 X136.745 Y153.919 E.60832
G1 X136.419 Y153.919 E.01153
G1 X136.419 Y154.118 E.00703
G1 X148.382 Y166.081 E.59838
G1 X147.857 Y166.081 E.01856
G1 X136.419 Y154.643 E.57213
G1 X136.419 Y155.167 E.01856
G1 X147.333 Y166.081 E.54589
G1 X146.808 Y166.081 E.01856
G1 X136.419 Y155.692 E.51965
G1 X136.419 Y156.217 E.01856
G1 X146.283 Y166.081 E.4934
G1 X145.759 Y166.081 E.01856
G1 X136.419 Y156.741 E.46716
G1 X136.419 Y157.266 E.01856
G1 X145.234 Y166.081 E.44091
G1 X144.709 Y166.081 E.01856
G1 X136.419 Y157.791 E.41467
G1 X136.419 Y158.315 E.01856
G1 X144.185 Y166.081 E.38843
G1 X143.66 Y166.081 E.01856
G1 X136.419 Y158.84 E.36218
G1 X136.419 Y159.365 E.01856
G1 X143.135 Y166.081 E.33594
G1 X142.611 Y166.081 E.01856
G1 X136.419 Y159.889 E.30969
G1 X136.419 Y160.414 E.01856
G1 X142.086 Y166.081 E.28345
G1 X141.561 Y166.081 E.01856
G1 X136.419 Y160.939 E.25721
G1 X136.419 Y161.463 E.01856
G1 X141.037 Y166.081 E.23096
M73 P52 R5
G1 X140.512 Y166.081 E.01856
G1 X136.419 Y161.988 E.20472
G1 X136.419 Y162.513 E.01856
G1 X139.987 Y166.081 E.17847
G1 X139.463 Y166.081 E.01856
G1 X136.419 Y163.037 E.15223
G1 X136.419 Y163.562 E.01856
G1 X138.938 Y166.081 E.12599
G1 X138.413 Y166.081 E.01856
G1 X136.419 Y164.087 E.09974
G1 X136.419 Y164.611 E.01856
G1 X137.889 Y166.081 E.0735
G1 X137.364 Y166.081 E.01856
G1 X136.419 Y165.136 E.04725
G1 X136.419 Y165.661 E.01856
G1 X137.005 Y166.246 E.0293
; CHANGE_LAYER
; Z_HEIGHT: 0.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12129.707
G1 X136.419 Y165.661 E-.31483
G1 X136.419 Y165.136 E-.19937
G1 X136.877 Y165.593 E-.2458
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 4/44
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.08 I-.019 J1.217 P1  F60000
G1 X188.907 Y166.407 Z1.08
G1 Z.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.658 Y166.632 Z1.32 F60000
G1 X136.688 Y166.066 Z1.32
G1 Z.92
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X136.434 Y166.066 E.00963
G1 X136.434 Y164.725 E.05093
G1 X136.846 Y163.942 E.0336
G1 X137.274 Y163.725 E.01822
G1 X137.701 Y163.791 E.01643
G1 X138.556 Y164.12 E.03481
G1 X138.984 Y164.396 E.01934
G1 X139.412 Y164.822 E.02292
G1 X140.172 Y166.066 E.05539
G1 X142.095 Y166.066 E.07306
G1 X142.405 Y165.866 E.014
G1 X142.832 Y165.44 E.02292
G1 X143.26 Y164.755 E.03068
G1 X143.687 Y163.942 E.03489
G1 X144.115 Y163.725 E.01822
G1 X144.542 Y163.791 E.01643
G1 X145.398 Y164.12 E.03481
G1 X145.825 Y164.396 E.01934
G1 X146.253 Y164.822 E.02292
G1 X147.013 Y166.066 E.05539
G1 X148.936 Y166.066 E.07306
G1 X149.246 Y165.866 E.014
G1 X149.673 Y165.44 E.02292
G1 X150.101 Y164.755 E.03068
G1 X150.528 Y163.942 E.03489
G1 X150.956 Y163.725 E.01822
G1 X151.383 Y163.791 E.01643
G1 X152.239 Y164.12 E.03481
G1 X152.666 Y164.396 E.01934
G1 X153.094 Y164.822 E.02292
G1 X153.854 Y166.066 E.05539
G1 X155.777 Y166.066 E.07306
G1 X156.087 Y165.866 E.014
G1 X156.514 Y165.44 E.02292
G1 X156.942 Y164.755 E.03068
G1 X157.369 Y163.942 E.03489
G1 X157.797 Y163.725 E.01822
G1 X158.224 Y163.791 E.01643
G1 X159.08 Y164.12 E.03481
G1 X159.507 Y164.396 E.01934
G1 X159.935 Y164.822 E.02292
G1 X160.695 Y166.066 E.05539
G1 X162.618 Y166.066 E.07306
G1 X162.928 Y165.866 E.014
G1 X163.355 Y165.44 E.02292
G1 X163.783 Y164.755 E.03068
G1 X164.21 Y163.942 E.03489
G1 X164.638 Y163.725 E.01822
G1 X165.066 Y163.791 E.01643
G1 X165.921 Y164.12 E.03481
G1 X166.348 Y164.396 E.01934
G1 X166.776 Y164.822 E.02292
G1 X167.536 Y166.066 E.05539
G1 X169.459 Y166.066 E.07306
G1 X169.769 Y165.866 E.014
G1 X170.196 Y165.44 E.02292
G1 X170.624 Y164.755 E.03068
G1 X171.051 Y163.942 E.03489
G1 X171.479 Y163.725 E.01822
G1 X171.907 Y163.791 E.01643
G1 X172.762 Y164.12 E.03481
G1 X173.189 Y164.396 E.01934
G1 X173.617 Y164.822 E.02292
G1 X174.377 Y166.066 E.05539
G1 X176.3 Y166.066 E.07306
G1 X176.61 Y165.866 E.014
G1 X177.037 Y165.44 E.02292
G1 X177.465 Y164.755 E.03068
G1 X177.892 Y163.942 E.03489
G1 X178.32 Y163.725 E.01822
G1 X178.748 Y163.791 E.01643
G1 X179.603 Y164.12 E.03481
G1 X180.03 Y164.396 E.01934
G1 X180.458 Y164.822 E.02292
G1 X181.218 Y166.066 E.05539
G1 X183.141 Y166.066 E.07306
G1 X183.451 Y165.866 E.014
G1 X183.878 Y165.44 E.02292
G1 X184.306 Y164.755 E.03068
G1 X184.734 Y163.942 E.03489
G1 X185.161 Y163.725 E.01822
G1 X185.589 Y163.791 E.01643
G1 X186.444 Y164.12 E.03481
G1 X186.871 Y164.396 E.01934
G1 X187.299 Y164.822 E.02292
G1 X188.059 Y166.066 E.05539
G1 X188.566 Y166.066 E.01923
G1 X188.566 Y161.304 E.18091
G1 X188.154 Y160.522 E.03358
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
G1 X148.39 Y162.445 E.01934
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
G1 X138.556 Y160.699 E.03481
G1 X138.129 Y160.975 E.01934
G1 X137.701 Y161.401 E.02292
G1 X137.274 Y162.086 E.03068
G1 X136.846 Y162.899 E.03489
G1 X136.434 Y163.108 E.01755
G1 X136.434 Y157.884 E.19848
G1 X136.846 Y157.101 E.0336
G1 X137.274 Y156.884 E.01822
G1 X137.701 Y156.95 E.01643
G1 X138.556 Y157.279 E.03481
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
G1 X188.566 Y159.687 E.01753
G1 X188.566 Y154.463 E.19849
G1 X188.288 Y153.934 E.02269
G1 X186.326 Y153.934 E.07453
G1 X186.016 Y154.134 E.014
G1 X185.589 Y154.56 E.02292
G1 X185.161 Y155.245 E.03068
G1 X184.734 Y156.058 E.03489
G1 X184.306 Y156.275 E.01822
G1 X183.878 Y156.209 E.01643
G1 X183.023 Y155.88 E.03481
G1 X182.596 Y155.604 E.01934
G1 X182.168 Y155.178 E.02292
G1 X181.741 Y154.493 E.03068
G1 X181.447 Y153.934 E.02399
G1 X179.485 Y153.934 E.07453
G1 X179.175 Y154.134 E.014
G1 X178.748 Y154.56 E.02292
G1 X178.32 Y155.245 E.03068
G1 X177.892 Y156.058 E.03489
G1 X177.465 Y156.275 E.01822
G1 X177.037 Y156.209 E.01643
G1 X176.182 Y155.88 E.03481
G1 X175.755 Y155.604 E.01934
G1 X175.327 Y155.178 E.02292
G1 X174.9 Y154.493 E.03068
G1 X174.605 Y153.934 E.02399
G1 X172.644 Y153.934 E.07453
G1 X172.334 Y154.134 E.014
G1 X171.907 Y154.56 E.02292
G1 X171.479 Y155.245 E.03068
G1 X171.051 Y156.058 E.03489
G1 X170.624 Y156.275 E.01822
G1 X170.196 Y156.209 E.01643
G1 X169.341 Y155.88 E.03481
G1 X168.914 Y155.604 E.01934
G1 X168.486 Y155.178 E.02292
G1 X168.058 Y154.493 E.03068
G1 X167.764 Y153.934 E.02399
G1 X165.803 Y153.934 E.07453
G1 X165.493 Y154.134 E.014
G1 X165.066 Y154.56 E.02292
G1 X164.638 Y155.245 E.03068
G1 X164.21 Y156.058 E.03489
G1 X163.783 Y156.275 E.01822
G1 X163.355 Y156.209 E.01643
G1 X162.5 Y155.88 E.03481
G1 X162.073 Y155.604 E.01934
G1 X161.645 Y155.178 E.02292
G1 X161.217 Y154.493 E.03068
G1 X160.923 Y153.934 E.02399
G1 X158.962 Y153.934 E.07453
G1 X158.652 Y154.134 E.014
G1 X158.224 Y154.56 E.02292
G1 X157.797 Y155.245 E.03068
G1 X157.369 Y156.058 E.03489
G1 X156.942 Y156.275 E.01822
G1 X156.514 Y156.209 E.01643
G1 X155.659 Y155.88 E.03481
G1 X155.232 Y155.604 E.01934
G1 X154.804 Y155.178 E.02292
G1 X154.376 Y154.493 E.03068
G1 X154.082 Y153.934 E.02399
G1 X152.121 Y153.934 E.07453
G1 X151.811 Y154.134 E.014
G1 X151.383 Y154.56 E.02292
G1 X150.956 Y155.245 E.03068
G1 X150.528 Y156.058 E.03489
G1 X150.101 Y156.275 E.01822
G1 X149.673 Y156.209 E.01643
G1 X148.818 Y155.88 E.03481
G1 X148.39 Y155.604 E.01934
G1 X147.963 Y155.178 E.02292
G1 X147.535 Y154.493 E.03068
G1 X147.241 Y153.934 E.02399
G1 X145.28 Y153.934 E.07453
G1 X144.97 Y154.134 E.014
G1 X144.542 Y154.56 E.02292
G1 X144.115 Y155.245 E.03068
G1 X143.687 Y156.058 E.03489
G1 X143.26 Y156.275 E.01822
G1 X142.832 Y156.209 E.01643
G1 X141.977 Y155.88 E.03481
G1 X141.549 Y155.604 E.01934
G1 X141.122 Y155.178 E.02292
G1 X140.694 Y154.493 E.03068
G1 X140.4 Y153.934 E.02399
G1 X138.438 Y153.934 E.07453
G1 X138.129 Y154.134 E.014
G1 X137.701 Y154.56 E.02292
G1 X137.274 Y155.245 E.03068
G1 X136.846 Y156.058 E.03489
G1 X136.434 Y156.267 E.01755
G1 X136.434 Y154.673 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X136.434 Y156.267 E-.60571
G1 X136.796 Y156.083 E-.15429
; WIPE_END
M73 P53 R5
G1 E-.04 F1800
; layer num/total_layer_count: 5/44
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.32 I-.236 J1.194 P1  F60000
G1 X188.907 Y166.407 Z1.32
G1 Z1.16
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X186.931 Y166.066 Z1.56 F60000
G1 Z1.16
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X188.525 Y166.066 E.06056
G1 X188.154 Y165.769 E.01805
G1 X187.299 Y164.727 E.05121
G1 X186.871 Y164.405 E.02034
G1 X186.444 Y164.203 E.01797
G1 X185.589 Y164.054 E.03298
G1 X185.161 Y164.151 E.01666
G1 X184.734 Y164.492 E.02078
G1 X183.878 Y165.534 E.05121
G1 X183.451 Y165.856 E.02034
G1 X182.982 Y166.066 E.01949
G1 X181.684 Y166.066 E.04931
G1 X181.313 Y165.769 E.01805
G1 X180.458 Y164.727 E.05121
G1 X180.03 Y164.405 E.02034
G1 X179.603 Y164.203 E.01797
G1 X178.748 Y164.054 E.03298
G1 X178.32 Y164.151 E.01666
G1 X177.892 Y164.492 E.02078
G1 X177.037 Y165.534 E.05121
G1 X176.61 Y165.856 E.02034
G1 X176.141 Y166.066 E.01949
G1 X174.843 Y166.066 E.04931
G1 X174.472 Y165.769 E.01805
G1 X173.617 Y164.727 E.05121
G1 X173.189 Y164.405 E.02034
G1 X172.762 Y164.203 E.01797
G1 X171.907 Y164.054 E.03298
G1 X171.479 Y164.151 E.01666
G1 X171.051 Y164.492 E.02078
G1 X170.196 Y165.534 E.05121
G1 X169.769 Y165.856 E.02034
G1 X169.3 Y166.066 E.01949
G1 X168.002 Y166.066 E.04931
G1 X167.631 Y165.769 E.01805
G1 X166.776 Y164.727 E.05121
G1 X166.348 Y164.405 E.02034
G1 X165.921 Y164.203 E.01797
G1 X165.066 Y164.054 E.03298
G1 X164.638 Y164.151 E.01666
G1 X164.21 Y164.492 E.02078
G1 X163.355 Y165.534 E.05121
G1 X162.928 Y165.856 E.02034
G1 X162.459 Y166.066 E.01949
G1 X161.161 Y166.066 E.04931
G1 X160.79 Y165.769 E.01805
G1 X159.935 Y164.727 E.05121
G1 X159.507 Y164.405 E.02034
G1 X159.08 Y164.203 E.01797
G1 X158.224 Y164.054 E.03298
G1 X157.797 Y164.151 E.01666
G1 X157.369 Y164.492 E.02078
G1 X156.514 Y165.534 E.05121
G1 X156.087 Y165.856 E.02034
G1 X155.618 Y166.066 E.01949
G1 X154.32 Y166.066 E.04931
G1 X153.949 Y165.769 E.01805
G1 X153.094 Y164.727 E.05121
G1 X152.666 Y164.405 E.02034
G1 X152.239 Y164.203 E.01797
G1 X151.383 Y164.054 E.03298
G1 X150.956 Y164.151 E.01666
G1 X150.528 Y164.492 E.02078
G1 X149.673 Y165.534 E.05121
G1 X149.246 Y165.856 E.02034
G1 X148.818 Y166.058 E.01797
G1 X147.479 Y166.066 E.05087
G1 X147.108 Y165.769 E.01805
G1 X146.253 Y164.727 E.05121
G1 X145.825 Y164.405 E.02034
G1 X145.398 Y164.203 E.01797
G1 X144.542 Y164.054 E.03298
G1 X144.115 Y164.151 E.01666
G1 X143.687 Y164.492 E.02078
G1 X142.832 Y165.534 E.05121
G1 X142.405 Y165.856 E.02034
G1 X141.936 Y166.066 E.01949
G1 X140.638 Y166.066 E.04931
G1 X140.267 Y165.769 E.01805
G1 X139.412 Y164.727 E.05121
G1 X138.984 Y164.405 E.02034
G1 X138.556 Y164.203 E.01797
G1 X137.701 Y164.054 E.03298
G1 X137.274 Y164.151 E.01666
G1 X136.846 Y164.492 E.02078
G1 X136.434 Y164.994 E.02466
G1 X136.434 Y162.677 E.08802
G1 X136.846 Y162.349 E.02002
G1 X137.701 Y161.307 E.05121
G1 X138.129 Y160.985 E.02034
G1 X138.556 Y160.783 E.01797
G1 X139.412 Y160.634 E.03298
G1 X139.839 Y160.731 E.01666
G1 X140.267 Y161.072 E.02078
G1 X141.122 Y162.114 E.05121
G1 X141.549 Y162.436 E.02034
G1 X141.977 Y162.638 E.01797
G1 X142.832 Y162.787 E.03298
G1 X143.26 Y162.69 E.01666
G1 X143.687 Y162.349 E.02078
G1 X144.542 Y161.307 E.05121
G1 X144.97 Y160.985 E.02034
G1 X145.398 Y160.783 E.01797
G1 X146.253 Y160.634 E.03298
G1 X146.68 Y160.731 E.01666
G1 X147.108 Y161.072 E.02078
G1 X147.963 Y162.114 E.05121
G1 X148.39 Y162.436 E.02034
G1 X148.818 Y162.638 E.01797
G1 X149.673 Y162.787 E.03298
G1 X150.101 Y162.69 E.01666
G1 X150.528 Y162.349 E.02078
G1 X151.383 Y161.307 E.05121
G1 X151.811 Y160.985 E.02034
G1 X152.239 Y160.783 E.01797
G1 X153.094 Y160.634 E.03298
G1 X153.521 Y160.731 E.01666
G1 X153.949 Y161.072 E.02078
G1 X154.804 Y162.114 E.05121
G1 X155.232 Y162.436 E.02034
G1 X155.659 Y162.638 E.01797
G1 X156.514 Y162.787 E.03298
G1 X156.942 Y162.69 E.01666
G1 X157.369 Y162.349 E.02078
G1 X158.224 Y161.307 E.05121
G1 X158.652 Y160.985 E.02034
G1 X159.08 Y160.783 E.01797
G1 X159.935 Y160.634 E.03298
G1 X160.362 Y160.731 E.01666
G1 X160.79 Y161.072 E.02078
G1 X161.645 Y162.114 E.05121
G1 X162.073 Y162.436 E.02034
G1 X162.5 Y162.638 E.01797
G1 X163.355 Y162.787 E.03298
G1 X163.783 Y162.69 E.01666
G1 X164.21 Y162.349 E.02078
G1 X165.066 Y161.307 E.05121
G1 X165.493 Y160.985 E.02034
G1 X165.921 Y160.783 E.01797
G1 X166.776 Y160.634 E.03298
G1 X167.203 Y160.731 E.01666
G1 X167.631 Y161.072 E.02078
G1 X168.486 Y162.114 E.05121
G1 X168.914 Y162.436 E.02034
G1 X169.341 Y162.638 E.01797
G1 X170.196 Y162.787 E.03298
G1 X170.624 Y162.69 E.01666
G1 X171.051 Y162.349 E.02078
G1 X171.907 Y161.307 E.05121
G1 X172.334 Y160.985 E.02034
G1 X172.762 Y160.783 E.01797
G1 X173.617 Y160.634 E.03298
G1 X174.044 Y160.731 E.01666
G1 X174.472 Y161.072 E.02078
G1 X175.327 Y162.114 E.05121
G1 X175.755 Y162.436 E.02034
G1 X176.182 Y162.638 E.01797
G1 X177.037 Y162.787 E.03298
G1 X177.465 Y162.69 E.01666
G1 X177.892 Y162.349 E.02078
G1 X178.748 Y161.307 E.05121
G1 X179.175 Y160.985 E.02034
G1 X179.603 Y160.783 E.01797
G1 X180.458 Y160.634 E.03298
G1 X180.885 Y160.731 E.01666
G1 X181.313 Y161.072 E.02078
G1 X182.168 Y162.114 E.05121
G1 X182.596 Y162.436 E.02034
G1 X183.023 Y162.638 E.01797
G1 X183.878 Y162.787 E.03298
G1 X184.306 Y162.69 E.01666
G1 X184.734 Y162.349 E.02078
G1 X185.589 Y161.307 E.05121
G1 X186.016 Y160.985 E.02034
G1 X186.444 Y160.783 E.01797
G1 X187.299 Y160.634 E.03298
G1 X187.726 Y160.731 E.01666
G1 X188.154 Y161.072 E.02078
G1 X188.566 Y161.573 E.02464
G1 X188.566 Y159.257 E.08802
G1 X188.154 Y158.928 E.02
G1 X187.299 Y157.886 E.05121
G1 X186.871 Y157.564 E.02034
G1 X186.444 Y157.362 E.01797
G1 X185.589 Y157.213 E.03298
G1 X185.161 Y157.31 E.01666
G1 X184.734 Y157.651 E.02078
G1 X183.878 Y158.693 E.05121
G1 X183.451 Y159.015 E.02034
G1 X183.023 Y159.217 E.01797
G1 X182.168 Y159.366 E.03298
G1 X181.741 Y159.269 E.01666
G1 X181.313 Y158.928 E.02078
G1 X180.458 Y157.886 E.05121
G1 X180.03 Y157.564 E.02034
G1 X179.603 Y157.362 E.01797
G1 X178.748 Y157.213 E.03298
G1 X178.32 Y157.31 E.01666
G1 X177.892 Y157.651 E.02078
G1 X177.037 Y158.693 E.05121
G1 X176.61 Y159.015 E.02034
G1 X176.182 Y159.217 E.01797
G1 X175.327 Y159.366 E.03298
G1 X174.9 Y159.269 E.01666
G1 X174.472 Y158.928 E.02078
G1 X173.617 Y157.886 E.05121
G1 X173.189 Y157.564 E.02034
G1 X172.762 Y157.362 E.01797
G1 X171.907 Y157.213 E.03298
G1 X171.479 Y157.31 E.01666
G1 X171.051 Y157.651 E.02078
G1 X170.196 Y158.693 E.05121
G1 X169.769 Y159.015 E.02034
G1 X169.341 Y159.217 E.01797
G1 X168.486 Y159.366 E.03298
G1 X168.058 Y159.269 E.01666
G1 X167.631 Y158.928 E.02078
G1 X166.776 Y157.886 E.05121
G1 X166.348 Y157.564 E.02034
G1 X165.921 Y157.362 E.01797
G1 X165.066 Y157.213 E.03298
G1 X164.638 Y157.31 E.01666
G1 X164.21 Y157.651 E.02078
G1 X163.355 Y158.693 E.05121
G1 X162.928 Y159.015 E.02034
G1 X162.5 Y159.217 E.01797
G1 X161.645 Y159.366 E.03298
G1 X161.217 Y159.269 E.01666
G1 X160.79 Y158.928 E.02078
G1 X159.935 Y157.886 E.05121
G1 X159.507 Y157.564 E.02034
G1 X159.08 Y157.362 E.01797
G1 X158.224 Y157.213 E.03298
G1 X157.797 Y157.31 E.01666
G1 X157.369 Y157.651 E.02078
G1 X156.514 Y158.693 E.05121
G1 X156.087 Y159.015 E.02034
G1 X155.659 Y159.217 E.01797
G1 X154.804 Y159.366 E.03298
G1 X154.376 Y159.269 E.01666
G1 X153.949 Y158.928 E.02078
G1 X153.094 Y157.886 E.05121
G1 X152.666 Y157.564 E.02034
G1 X152.239 Y157.362 E.01797
G1 X151.383 Y157.213 E.03298
G1 X150.956 Y157.31 E.01666
G1 X150.528 Y157.651 E.02078
G1 X149.673 Y158.693 E.05121
G1 X149.246 Y159.015 E.02034
G1 X148.818 Y159.217 E.01797
G1 X147.963 Y159.366 E.03298
G1 X147.535 Y159.269 E.01666
G1 X147.108 Y158.928 E.02078
G1 X146.253 Y157.886 E.05121
G1 X145.825 Y157.564 E.02034
G1 X145.398 Y157.362 E.01797
G1 X144.542 Y157.213 E.03298
G1 X144.115 Y157.31 E.01666
G1 X143.687 Y157.651 E.02078
G1 X142.832 Y158.693 E.05121
G1 X142.405 Y159.015 E.02034
G1 X141.977 Y159.217 E.01797
G1 X141.122 Y159.366 E.03298
G1 X140.694 Y159.269 E.01666
G1 X140.267 Y158.928 E.02078
G1 X139.412 Y157.886 E.05121
G1 X138.984 Y157.564 E.02034
G1 X138.556 Y157.362 E.01797
G1 X137.701 Y157.213 E.03298
G1 X137.274 Y157.31 E.01666
G1 X136.846 Y157.651 E.02078
G1 X136.434 Y158.153 E.02466
G1 X136.434 Y155.836 E.08802
G1 X136.846 Y155.508 E.02002
G1 X137.701 Y154.466 E.05121
G1 X138.129 Y154.144 E.02034
G1 X138.598 Y153.934 E.01951
G1 X139.895 Y153.934 E.0493
G1 X140.267 Y154.231 E.01805
G1 X141.122 Y155.273 E.05121
G1 X141.549 Y155.595 E.02034
G1 X141.977 Y155.797 E.01797
G1 X142.832 Y155.946 E.03298
G1 X143.26 Y155.849 E.01666
G1 X143.687 Y155.508 E.02078
G1 X144.542 Y154.466 E.05121
G1 X144.97 Y154.144 E.02034
G1 X145.439 Y153.934 E.01951
G1 X146.736 Y153.934 E.0493
G1 X147.108 Y154.231 E.01805
G1 X147.963 Y155.273 E.05121
G1 X148.39 Y155.595 E.02034
G1 X148.818 Y155.797 E.01797
G1 X149.673 Y155.946 E.03298
G1 X150.101 Y155.849 E.01666
G1 X150.528 Y155.508 E.02078
G1 X151.383 Y154.466 E.05121
G1 X151.811 Y154.144 E.02034
G1 X152.239 Y153.942 E.01797
G1 X153.577 Y153.934 E.05087
G1 X153.949 Y154.231 E.01805
G1 X154.804 Y155.273 E.05121
G1 X155.232 Y155.595 E.02034
G1 X155.659 Y155.797 E.01797
G1 X156.514 Y155.946 E.03298
G1 X156.942 Y155.849 E.01666
G1 X157.369 Y155.508 E.02078
G1 X158.224 Y154.466 E.05121
G1 X158.652 Y154.144 E.02034
G1 X159.121 Y153.934 E.01951
G1 X160.418 Y153.934 E.0493
G1 X160.79 Y154.231 E.01805
G1 X161.645 Y155.273 E.05121
G1 X162.073 Y155.595 E.02034
G1 X162.5 Y155.797 E.01797
G1 X163.355 Y155.946 E.03298
G1 X163.783 Y155.849 E.01666
G1 X164.21 Y155.508 E.02078
G1 X165.066 Y154.466 E.05121
G1 X165.493 Y154.144 E.02034
G1 X165.962 Y153.934 E.01951
G1 X167.259 Y153.934 E.0493
G1 X167.631 Y154.231 E.01805
G1 X168.486 Y155.273 E.05121
G1 X168.914 Y155.595 E.02034
G1 X169.341 Y155.797 E.01797
G1 X170.196 Y155.946 E.03298
G1 X170.624 Y155.849 E.01666
G1 X171.051 Y155.508 E.02078
G1 X171.907 Y154.466 E.05121
G1 X172.334 Y154.144 E.02034
G1 X172.803 Y153.934 E.01951
G1 X174.101 Y153.934 E.0493
G1 X174.472 Y154.231 E.01805
G1 X175.327 Y155.273 E.05121
G1 X175.755 Y155.595 E.02034
G1 X176.182 Y155.797 E.01797
G1 X177.037 Y155.946 E.03298
G1 X177.465 Y155.849 E.01666
G1 X177.892 Y155.508 E.02078
G1 X178.748 Y154.466 E.05121
G1 X179.175 Y154.144 E.02034
G1 X179.644 Y153.934 E.01951
G1 X180.942 Y153.934 E.0493
G1 X181.313 Y154.231 E.01805
G1 X182.168 Y155.273 E.05121
G1 X182.596 Y155.595 E.02034
G1 X183.023 Y155.797 E.01797
G1 X183.878 Y155.946 E.03298
G1 X184.306 Y155.849 E.01666
G1 X184.734 Y155.508 E.02078
G1 X185.589 Y154.466 E.05121
G1 X186.016 Y154.144 E.02034
G1 X186.485 Y153.934 E.01951
G1 X187.783 Y153.934 E.0493
G1 X188.154 Y154.231 E.01805
G1 X188.566 Y154.732 E.02464
G1 X188.566 Y156.326 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X188.566 Y154.732 E-.60572
G1 X188.308 Y154.418 E-.15428
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 6/44
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.56 I-1.215 J.061 P1  F60000
G1 X188.907 Y166.407 Z1.56
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
M73 P54 R5
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X187.23 Y166.066 Z1.8 F60000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X188.566 Y166.066 E.05073
G1 X188.566 Y165.807 E.00983
G1 X188.154 Y165.454 E.02058
G1 X187.299 Y164.622 E.04535
G1 X186.871 Y164.384 E.01858
G1 X186.444 Y164.253 E.01699
G1 X186.016 Y164.208 E.01633
G1 X185.589 Y164.257 E.01635
G1 X185.161 Y164.441 E.01768
G1 X184.734 Y164.807 E.02139
G1 X183.878 Y165.64 E.04535
G1 X183.451 Y165.877 E.01858
G1 X183.023 Y166.008 E.01699
G1 X182.596 Y166.053 E.01633
G1 X182.168 Y166.005 E.01635
G1 X181.741 Y165.821 E.01768
G1 X181.313 Y165.454 E.02139
G1 X180.458 Y164.622 E.04535
G1 X180.03 Y164.384 E.01858
G1 X179.603 Y164.253 E.01699
G1 X179.175 Y164.208 E.01633
G1 X178.748 Y164.257 E.01635
G1 X178.32 Y164.441 E.01768
G1 X177.892 Y164.807 E.02139
G1 X177.037 Y165.64 E.04535
G1 X176.61 Y165.877 E.01858
G1 X176.182 Y166.008 E.01699
G1 X175.755 Y166.053 E.01633
G1 X175.327 Y166.005 E.01635
G1 X174.9 Y165.821 E.01768
G1 X174.472 Y165.454 E.02139
G1 X173.617 Y164.622 E.04535
G1 X173.189 Y164.384 E.01858
G1 X172.762 Y164.253 E.01699
G1 X172.334 Y164.208 E.01633
G1 X171.907 Y164.257 E.01635
G1 X171.479 Y164.441 E.01768
G1 X171.051 Y164.807 E.02139
G1 X170.196 Y165.64 E.04535
G1 X169.769 Y165.877 E.01858
G1 X169.341 Y166.008 E.01699
G1 X168.914 Y166.053 E.01633
G1 X168.486 Y166.005 E.01635
G1 X168.058 Y165.821 E.01768
G1 X167.631 Y165.454 E.02139
G1 X166.776 Y164.622 E.04535
G1 X166.348 Y164.384 E.01858
G1 X165.921 Y164.253 E.01699
G1 X165.493 Y164.208 E.01633
G1 X165.066 Y164.257 E.01635
G1 X164.638 Y164.441 E.01768
G1 X164.21 Y164.807 E.02139
G1 X163.355 Y165.64 E.04535
G1 X162.928 Y165.877 E.01858
G1 X162.5 Y166.008 E.01699
G1 X162.073 Y166.053 E.01633
G1 X161.645 Y166.005 E.01635
G1 X161.217 Y165.821 E.01768
G1 X160.79 Y165.454 E.02139
G1 X159.935 Y164.622 E.04535
G1 X159.507 Y164.384 E.01858
G1 X159.08 Y164.253 E.01699
G1 X158.652 Y164.208 E.01633
G1 X158.224 Y164.257 E.01635
G1 X157.797 Y164.441 E.01768
G1 X157.369 Y164.807 E.02139
G1 X156.514 Y165.64 E.04535
G1 X156.087 Y165.877 E.01858
G1 X155.659 Y166.008 E.01699
G1 X155.232 Y166.053 E.01633
G1 X154.804 Y166.005 E.01635
G1 X154.376 Y165.821 E.01768
G1 X153.949 Y165.454 E.02139
G1 X153.094 Y164.622 E.04535
G1 X152.666 Y164.384 E.01858
G1 X152.239 Y164.253 E.01699
G1 X151.811 Y164.208 E.01633
G1 X151.383 Y164.257 E.01635
G1 X150.956 Y164.441 E.01768
G1 X150.528 Y164.807 E.02139
G1 X149.673 Y165.64 E.04535
G1 X149.246 Y165.877 E.01858
G1 X148.818 Y166.008 E.01699
G1 X148.39 Y166.053 E.01633
G1 X147.963 Y166.005 E.01635
G1 X147.535 Y165.821 E.01768
G1 X147.108 Y165.454 E.02139
G1 X146.253 Y164.622 E.04535
G1 X145.825 Y164.384 E.01858
G1 X145.398 Y164.253 E.01699
G1 X144.97 Y164.208 E.01633
G1 X144.542 Y164.257 E.01635
G1 X144.115 Y164.441 E.01768
G1 X143.687 Y164.807 E.02139
G1 X142.832 Y165.64 E.04535
G1 X142.405 Y165.877 E.01858
G1 X141.977 Y166.008 E.01699
G1 X141.549 Y166.053 E.01633
G1 X141.122 Y166.005 E.01635
G1 X140.694 Y165.821 E.01768
G1 X140.267 Y165.454 E.02139
G1 X139.412 Y164.622 E.04535
G1 X138.984 Y164.384 E.01858
G1 X138.556 Y164.253 E.01699
G1 X138.129 Y164.208 E.01633
G1 X137.701 Y164.257 E.01635
G1 X137.274 Y164.441 E.01768
G1 X136.846 Y164.807 E.02139
G1 X136.434 Y165.208 E.02184
G1 X136.434 Y162.387 E.1072
G1 X136.846 Y162.034 E.0206
G1 X137.701 Y161.201 E.04535
G1 X138.129 Y160.964 E.01858
G1 X138.556 Y160.833 E.01699
G1 X138.984 Y160.788 E.01633
G1 X139.412 Y160.836 E.01635
G1 X139.839 Y161.02 E.01768
G1 X140.267 Y161.387 E.02139
G1 X141.122 Y162.219 E.04535
G1 X141.549 Y162.457 E.01858
G1 X141.977 Y162.588 E.01699
G1 X142.405 Y162.633 E.01633
G1 X142.832 Y162.584 E.01635
G1 X143.26 Y162.4 E.01768
G1 X143.687 Y162.034 E.02139
G1 X144.542 Y161.201 E.04535
G1 X144.97 Y160.964 E.01858
G1 X145.398 Y160.833 E.01699
G1 X145.825 Y160.788 E.01633
G1 X146.253 Y160.836 E.01635
G1 X146.68 Y161.02 E.01768
G1 X147.108 Y161.387 E.02139
G1 X147.963 Y162.219 E.04535
G1 X148.39 Y162.457 E.01858
G1 X148.818 Y162.588 E.01699
G1 X149.246 Y162.633 E.01633
G1 X149.673 Y162.584 E.01635
G1 X150.101 Y162.4 E.01768
G1 X150.528 Y162.034 E.02139
G1 X151.383 Y161.201 E.04535
G1 X151.811 Y160.964 E.01858
G1 X152.239 Y160.833 E.01699
G1 X152.666 Y160.788 E.01633
G1 X153.094 Y160.836 E.01635
G1 X153.521 Y161.02 E.01768
G1 X153.949 Y161.387 E.02139
G1 X154.804 Y162.219 E.04535
G1 X155.232 Y162.457 E.01858
G1 X155.659 Y162.588 E.01699
G1 X156.087 Y162.633 E.01633
G1 X156.514 Y162.584 E.01635
G1 X156.942 Y162.4 E.01768
G1 X157.369 Y162.034 E.02139
G1 X158.224 Y161.201 E.04535
G1 X158.652 Y160.964 E.01858
G1 X159.08 Y160.833 E.01699
G1 X159.507 Y160.788 E.01633
G1 X159.935 Y160.836 E.01635
G1 X160.362 Y161.02 E.01768
G1 X160.79 Y161.387 E.02139
G1 X161.645 Y162.219 E.04535
G1 X162.073 Y162.457 E.01858
G1 X162.5 Y162.588 E.01699
G1 X162.928 Y162.633 E.01633
G1 X163.355 Y162.584 E.01635
G1 X163.783 Y162.4 E.01768
G1 X164.21 Y162.034 E.02139
G1 X165.066 Y161.201 E.04535
G1 X165.493 Y160.964 E.01858
G1 X165.921 Y160.833 E.01699
G1 X166.348 Y160.788 E.01633
G1 X166.776 Y160.836 E.01635
G1 X167.203 Y161.02 E.01768
G1 X167.631 Y161.387 E.02139
G1 X168.486 Y162.219 E.04535
G1 X168.914 Y162.457 E.01858
G1 X169.341 Y162.588 E.01699
G1 X169.769 Y162.633 E.01633
G1 X170.196 Y162.584 E.01635
G1 X170.624 Y162.4 E.01768
G1 X171.051 Y162.034 E.02139
G1 X171.907 Y161.201 E.04535
G1 X172.334 Y160.964 E.01858
G1 X172.762 Y160.833 E.01699
G1 X173.189 Y160.788 E.01633
G1 X173.617 Y160.836 E.01635
G1 X174.044 Y161.02 E.01768
G1 X174.472 Y161.387 E.02139
G1 X175.327 Y162.219 E.04535
G1 X175.755 Y162.457 E.01858
G1 X176.182 Y162.588 E.01699
G1 X176.61 Y162.633 E.01633
G1 X177.037 Y162.584 E.01635
G1 X177.465 Y162.4 E.01768
G1 X177.892 Y162.034 E.02139
G1 X178.748 Y161.201 E.04535
G1 X179.175 Y160.964 E.01858
G1 X179.603 Y160.833 E.01699
G1 X180.03 Y160.788 E.01633
G1 X180.458 Y160.836 E.01635
G1 X180.885 Y161.02 E.01768
G1 X181.313 Y161.387 E.02139
G1 X182.168 Y162.219 E.04535
G1 X182.596 Y162.457 E.01858
G1 X183.023 Y162.588 E.01699
G1 X183.451 Y162.633 E.01633
G1 X183.878 Y162.584 E.01635
G1 X184.306 Y162.4 E.01768
G1 X184.734 Y162.034 E.02139
G1 X185.589 Y161.201 E.04535
G1 X186.016 Y160.964 E.01858
G1 X186.444 Y160.833 E.01699
G1 X186.871 Y160.788 E.01633
G1 X187.299 Y160.836 E.01635
G1 X187.726 Y161.02 E.01768
G1 X188.154 Y161.387 E.02139
G1 X188.566 Y161.787 E.02182
G1 X188.566 Y158.966 E.1072
G1 X188.154 Y158.613 E.02058
G1 X187.299 Y157.781 E.04535
G1 X186.871 Y157.543 E.01858
G1 X186.444 Y157.412 E.01699
G1 X186.016 Y157.367 E.01633
G1 X185.589 Y157.416 E.01635
G1 X185.161 Y157.6 E.01768
G1 X184.734 Y157.966 E.02139
G1 X183.878 Y158.799 E.04535
G1 X183.451 Y159.036 E.01858
G1 X183.023 Y159.167 E.01699
G1 X182.596 Y159.212 E.01633
G1 X182.168 Y159.164 E.01635
G1 X181.741 Y158.98 E.01768
G1 X181.313 Y158.613 E.02139
G1 X180.458 Y157.781 E.04535
G1 X180.03 Y157.543 E.01858
G1 X179.603 Y157.412 E.01699
G1 X179.175 Y157.367 E.01633
G1 X178.748 Y157.416 E.01635
G1 X178.32 Y157.6 E.01768
G1 X177.892 Y157.966 E.02139
G1 X177.037 Y158.799 E.04535
G1 X176.61 Y159.036 E.01858
G1 X176.182 Y159.167 E.01699
G1 X175.755 Y159.212 E.01633
G1 X175.327 Y159.164 E.01635
G1 X174.9 Y158.98 E.01768
G1 X174.472 Y158.613 E.02139
G1 X173.617 Y157.781 E.04535
G1 X173.189 Y157.543 E.01858
G1 X172.762 Y157.412 E.01699
G1 X172.334 Y157.367 E.01633
G1 X171.907 Y157.416 E.01635
G1 X171.479 Y157.6 E.01768
G1 X171.051 Y157.966 E.02139
G1 X170.196 Y158.799 E.04535
G1 X169.769 Y159.036 E.01858
G1 X169.341 Y159.167 E.01699
G1 X168.914 Y159.212 E.01633
G1 X168.486 Y159.164 E.01635
G1 X168.058 Y158.98 E.01768
G1 X167.631 Y158.613 E.02139
G1 X166.776 Y157.781 E.04535
G1 X166.348 Y157.543 E.01858
G1 X165.921 Y157.412 E.01699
G1 X165.493 Y157.367 E.01633
G1 X165.066 Y157.416 E.01635
G1 X164.638 Y157.6 E.01768
G1 X164.21 Y157.966 E.02139
G1 X163.355 Y158.799 E.04535
G1 X162.928 Y159.036 E.01858
G1 X162.5 Y159.167 E.01699
G1 X162.073 Y159.212 E.01633
G1 X161.645 Y159.164 E.01635
G1 X161.217 Y158.98 E.01768
G1 X160.79 Y158.613 E.02139
G1 X159.935 Y157.781 E.04535
G1 X159.507 Y157.543 E.01858
G1 X159.08 Y157.412 E.01699
G1 X158.652 Y157.367 E.01633
G1 X158.224 Y157.416 E.01635
G1 X157.797 Y157.6 E.01768
G1 X157.369 Y157.966 E.02139
G1 X156.514 Y158.799 E.04535
G1 X156.087 Y159.036 E.01858
G1 X155.659 Y159.167 E.01699
G1 X155.232 Y159.212 E.01633
G1 X154.804 Y159.164 E.01635
G1 X154.376 Y158.98 E.01768
G1 X153.949 Y158.613 E.02139
G1 X153.094 Y157.781 E.04535
G1 X152.666 Y157.543 E.01858
G1 X152.239 Y157.412 E.01699
G1 X151.811 Y157.367 E.01633
G1 X151.383 Y157.416 E.01635
G1 X150.956 Y157.6 E.01768
G1 X150.528 Y157.966 E.02139
G1 X149.673 Y158.799 E.04535
G1 X149.246 Y159.036 E.01858
G1 X148.818 Y159.167 E.01699
G1 X148.39 Y159.212 E.01633
G1 X147.963 Y159.164 E.01635
G1 X147.535 Y158.98 E.01768
G1 X147.108 Y158.613 E.02139
G1 X146.253 Y157.781 E.04535
G1 X145.825 Y157.543 E.01858
G1 X145.398 Y157.412 E.01699
G1 X144.97 Y157.367 E.01633
G1 X144.542 Y157.416 E.01635
G1 X144.115 Y157.6 E.01768
G1 X143.687 Y157.966 E.02139
G1 X142.832 Y158.799 E.04535
G1 X142.405 Y159.036 E.01858
G1 X141.977 Y159.167 E.01699
G1 X141.549 Y159.212 E.01633
G1 X141.122 Y159.164 E.01635
G1 X140.694 Y158.98 E.01768
G1 X140.267 Y158.613 E.02139
G1 X139.412 Y157.781 E.04535
G1 X138.984 Y157.543 E.01858
G1 X138.556 Y157.412 E.01699
G1 X138.129 Y157.367 E.01633
G1 X137.701 Y157.416 E.01635
G1 X137.274 Y157.6 E.01768
G1 X136.846 Y157.966 E.02139
G1 X136.434 Y158.367 E.02184
G1 X136.434 Y155.546 E.1072
G1 X136.846 Y155.193 E.0206
G1 X137.701 Y154.36 E.04535
G1 X138.129 Y154.123 E.01858
G1 X138.556 Y153.992 E.01699
G1 X138.984 Y153.947 E.01633
G1 X139.412 Y153.995 E.01635
G1 X139.839 Y154.179 E.01768
G1 X140.267 Y154.546 E.02139
G1 X141.122 Y155.378 E.04535
G1 X141.549 Y155.616 E.01858
G1 X141.977 Y155.747 E.01699
G1 X142.405 Y155.792 E.01633
G1 X142.832 Y155.743 E.01635
G1 X143.26 Y155.559 E.01768
G1 X143.687 Y155.193 E.02139
G1 X144.542 Y154.36 E.04535
G1 X144.97 Y154.123 E.01858
G1 X145.398 Y153.992 E.01699
G1 X145.825 Y153.947 E.01633
G1 X146.253 Y153.995 E.01635
G1 X146.68 Y154.179 E.01768
G1 X147.108 Y154.546 E.02139
G1 X147.963 Y155.378 E.04535
G1 X148.39 Y155.616 E.01858
G1 X148.818 Y155.747 E.01699
G1 X149.246 Y155.792 E.01633
G1 X149.673 Y155.743 E.01635
G1 X150.101 Y155.559 E.01768
G1 X150.528 Y155.193 E.02139
G1 X151.383 Y154.36 E.04535
G1 X151.811 Y154.123 E.01858
G1 X152.239 Y153.992 E.01699
G1 X152.666 Y153.947 E.01633
G1 X153.094 Y153.995 E.01635
G1 X153.521 Y154.179 E.01768
G1 X153.949 Y154.546 E.02139
G1 X154.804 Y155.378 E.04535
G1 X155.232 Y155.616 E.01858
G1 X155.659 Y155.747 E.01699
G1 X156.087 Y155.792 E.01633
G1 X156.514 Y155.743 E.01635
G1 X156.942 Y155.559 E.01768
G1 X157.369 Y155.193 E.02139
G1 X158.224 Y154.36 E.04535
G1 X158.652 Y154.123 E.01858
G1 X159.08 Y153.992 E.01699
G1 X159.507 Y153.947 E.01633
G1 X159.935 Y153.995 E.01635
G1 X160.362 Y154.179 E.01768
G1 X160.79 Y154.546 E.02139
G1 X161.645 Y155.378 E.04535
G1 X162.073 Y155.616 E.01858
G1 X162.5 Y155.747 E.01699
G1 X162.928 Y155.792 E.01633
G1 X163.355 Y155.743 E.01635
G1 X163.783 Y155.559 E.01768
G1 X164.21 Y155.193 E.02139
G1 X165.066 Y154.36 E.04535
G1 X165.493 Y154.123 E.01858
G1 X165.921 Y153.992 E.01699
G1 X166.348 Y153.947 E.01633
G1 X166.776 Y153.995 E.01635
G1 X167.203 Y154.179 E.01768
G1 X167.631 Y154.546 E.02139
G1 X168.486 Y155.378 E.04535
G1 X168.914 Y155.616 E.01858
G1 X169.341 Y155.747 E.01699
G1 X169.769 Y155.792 E.01633
G1 X170.196 Y155.743 E.01635
G1 X170.624 Y155.559 E.01768
G1 X171.051 Y155.193 E.02139
G1 X171.907 Y154.36 E.04535
G1 X172.334 Y154.123 E.01858
G1 X172.762 Y153.992 E.01699
G1 X173.189 Y153.947 E.01633
G1 X173.617 Y153.995 E.01635
G1 X174.044 Y154.179 E.01768
G1 X174.472 Y154.546 E.02139
G1 X175.327 Y155.378 E.04535
G1 X175.755 Y155.616 E.01858
G1 X176.182 Y155.747 E.01699
G1 X176.61 Y155.792 E.01633
G1 X177.037 Y155.743 E.01635
G1 X177.465 Y155.559 E.01768
G1 X177.892 Y155.193 E.02139
G1 X178.748 Y154.36 E.04535
G1 X179.175 Y154.123 E.01858
G1 X179.603 Y153.992 E.01699
G1 X180.03 Y153.947 E.01633
G1 X180.458 Y153.995 E.01635
G1 X180.885 Y154.179 E.01768
G1 X181.313 Y154.546 E.02139
G1 X182.168 Y155.378 E.04535
G1 X182.596 Y155.616 E.01858
G1 X183.023 Y155.747 E.01699
G1 X183.451 Y155.792 E.01633
G1 X183.878 Y155.743 E.01635
G1 X184.306 Y155.559 E.01768
G1 X184.734 Y155.193 E.02139
G1 X185.589 Y154.36 E.04535
G1 X186.016 Y154.123 E.01858
G1 X186.444 Y153.992 E.01699
G1 X186.871 Y153.947 E.01633
G1 X187.299 Y153.995 E.01635
G1 X187.726 Y154.179 E.01768
G1 X188.154 Y154.546 E.02139
G1 X188.566 Y154.946 E.02182
G1 X188.566 Y156.54 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X188.566 Y154.946 E-.60572
G1 X188.275 Y154.663 E-.15428
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 7/44
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z1.8 I-1.215 J.065 P1  F60000
G1 X188.907 Y166.407 Z1.8
G1 Z1.64
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X187.461 Y166.066 Z2.04 F60000
G1 Z1.64
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X188.566 Y166.066 E.04195
G1 X188.566 Y165.576 E.01861
G1 X187.726 Y164.793 E.0436
G1 X187.299 Y164.5 E.01968
G1 X186.871 Y164.337 E.01738
G1 X186.444 Y164.275 E.01642
G1 X186.016 Y164.298 E.01627
G1 X185.589 Y164.419 E.01688
G1 X185.161 Y164.671 E.01886
G1 X184.306 Y165.469 E.04442
G1 X183.878 Y165.761 E.01968
G1 X183.451 Y165.924 E.01738
G1 X183.023 Y165.987 E.01642
G1 X182.596 Y165.964 E.01627
G1 X182.168 Y165.843 E.01688
G1 X181.741 Y165.59 E.01886
G1 X180.885 Y164.793 E.04442
G1 X180.458 Y164.5 E.01968
G1 X180.03 Y164.337 E.01738
G1 X179.603 Y164.275 E.01642
G1 X179.175 Y164.298 E.01627
G1 X178.748 Y164.419 E.01688
G1 X178.32 Y164.671 E.01886
G1 X177.465 Y165.469 E.04442
G1 X177.037 Y165.761 E.01968
G1 X176.61 Y165.924 E.01738
G1 X176.182 Y165.987 E.01642
G1 X175.755 Y165.964 E.01627
G1 X175.327 Y165.843 E.01688
G1 X174.9 Y165.59 E.01886
G1 X174.044 Y164.793 E.04442
G1 X173.617 Y164.5 E.01968
G1 X173.189 Y164.337 E.01738
G1 X172.762 Y164.275 E.01642
G1 X172.334 Y164.298 E.01627
G1 X171.907 Y164.419 E.01688
M73 P55 R5
G1 X171.479 Y164.671 E.01886
G1 X170.624 Y165.469 E.04442
G1 X170.196 Y165.761 E.01968
G1 X169.769 Y165.924 E.01738
G1 X169.341 Y165.987 E.01642
G1 X168.914 Y165.964 E.01627
G1 X168.486 Y165.843 E.01688
G1 X168.058 Y165.59 E.01886
G1 X167.203 Y164.793 E.04442
G1 X166.776 Y164.5 E.01968
G1 X166.348 Y164.337 E.01738
G1 X165.921 Y164.275 E.01642
G1 X165.493 Y164.298 E.01627
G1 X165.066 Y164.419 E.01688
G1 X164.638 Y164.671 E.01886
G1 X163.783 Y165.469 E.04442
G1 X163.355 Y165.761 E.01968
G1 X162.928 Y165.924 E.01738
G1 X162.5 Y165.987 E.01642
G1 X162.073 Y165.964 E.01627
G1 X161.645 Y165.843 E.01688
G1 X161.217 Y165.59 E.01886
G1 X160.362 Y164.793 E.04442
G1 X159.935 Y164.5 E.01968
G1 X159.507 Y164.337 E.01738
G1 X159.08 Y164.275 E.01642
G1 X158.652 Y164.298 E.01627
G1 X158.224 Y164.419 E.01688
G1 X157.797 Y164.671 E.01886
G1 X156.942 Y165.469 E.04442
G1 X156.514 Y165.761 E.01968
G1 X156.087 Y165.924 E.01738
G1 X155.659 Y165.987 E.01642
G1 X155.232 Y165.964 E.01627
G1 X154.804 Y165.843 E.01688
G1 X154.376 Y165.59 E.01886
G1 X153.521 Y164.793 E.04442
G1 X153.094 Y164.5 E.01968
G1 X152.666 Y164.337 E.01738
G1 X152.239 Y164.275 E.01642
G1 X151.811 Y164.298 E.01627
G1 X151.383 Y164.419 E.01688
G1 X150.956 Y164.671 E.01886
G1 X150.101 Y165.469 E.04442
G1 X149.673 Y165.761 E.01968
G1 X149.246 Y165.924 E.01738
G1 X148.818 Y165.987 E.01642
G1 X148.39 Y165.964 E.01627
G1 X147.963 Y165.843 E.01688
G1 X147.535 Y165.59 E.01886
G1 X146.68 Y164.793 E.04442
G1 X146.253 Y164.5 E.01968
G1 X145.825 Y164.337 E.01738
G1 X145.398 Y164.275 E.01642
G1 X144.97 Y164.298 E.01627
G1 X144.542 Y164.419 E.01688
G1 X144.115 Y164.671 E.01886
G1 X143.26 Y165.469 E.04442
G1 X142.832 Y165.761 E.01968
G1 X142.405 Y165.924 E.01738
G1 X141.977 Y165.987 E.01642
G1 X141.549 Y165.964 E.01627
G1 X141.122 Y165.843 E.01688
G1 X140.694 Y165.59 E.01886
G1 X139.839 Y164.793 E.04442
G1 X139.412 Y164.5 E.01968
G1 X138.984 Y164.337 E.01738
G1 X138.556 Y164.275 E.01642
G1 X138.129 Y164.298 E.01627
G1 X137.701 Y164.419 E.01688
G1 X137.274 Y164.671 E.01886
G1 X136.434 Y165.454 E.04359
G1 X136.434 Y162.155 E.12531
G1 X137.274 Y161.372 E.04361
G1 X137.701 Y161.08 E.01968
G1 X138.129 Y160.917 E.01738
G1 X138.556 Y160.854 E.01642
G1 X138.984 Y160.877 E.01627
G1 X139.412 Y160.998 E.01688
G1 X139.839 Y161.251 E.01886
G1 X140.694 Y162.048 E.04442
G1 X141.122 Y162.341 E.01968
G1 X141.549 Y162.504 E.01738
G1 X141.977 Y162.567 E.01642
G1 X142.405 Y162.543 E.01627
G1 X142.832 Y162.422 E.01688
G1 X143.26 Y162.17 E.01886
G1 X144.115 Y161.372 E.04442
G1 X144.542 Y161.08 E.01968
G1 X144.97 Y160.917 E.01738
G1 X145.398 Y160.854 E.01642
G1 X145.825 Y160.877 E.01627
G1 X146.253 Y160.998 E.01688
G1 X146.68 Y161.251 E.01886
G1 X147.535 Y162.048 E.04442
G1 X147.963 Y162.341 E.01968
G1 X148.39 Y162.504 E.01738
G1 X148.818 Y162.567 E.01642
G1 X149.246 Y162.543 E.01627
G1 X149.673 Y162.422 E.01688
G1 X150.101 Y162.17 E.01886
G1 X150.956 Y161.372 E.04442
G1 X151.383 Y161.08 E.01968
G1 X151.811 Y160.917 E.01738
G1 X152.239 Y160.854 E.01642
G1 X152.666 Y160.877 E.01627
G1 X153.094 Y160.998 E.01688
G1 X153.521 Y161.251 E.01886
G1 X154.376 Y162.048 E.04442
G1 X154.804 Y162.341 E.01968
G1 X155.232 Y162.504 E.01738
G1 X155.659 Y162.567 E.01642
G1 X156.087 Y162.543 E.01627
G1 X156.514 Y162.422 E.01688
G1 X156.942 Y162.17 E.01886
G1 X157.797 Y161.372 E.04442
G1 X158.224 Y161.08 E.01968
G1 X158.652 Y160.917 E.01738
G1 X159.08 Y160.854 E.01642
G1 X159.507 Y160.877 E.01627
G1 X159.935 Y160.998 E.01688
G1 X160.362 Y161.251 E.01886
G1 X161.217 Y162.048 E.04442
G1 X161.645 Y162.341 E.01968
G1 X162.073 Y162.504 E.01738
G1 X162.5 Y162.567 E.01642
G1 X162.928 Y162.543 E.01627
G1 X163.355 Y162.422 E.01688
G1 X163.783 Y162.17 E.01886
G1 X164.638 Y161.372 E.04442
G1 X165.066 Y161.08 E.01968
G1 X165.493 Y160.917 E.01738
G1 X165.921 Y160.854 E.01642
G1 X166.348 Y160.877 E.01627
G1 X166.776 Y160.998 E.01688
G1 X167.203 Y161.251 E.01886
G1 X168.058 Y162.048 E.04442
G1 X168.486 Y162.341 E.01968
G1 X168.914 Y162.504 E.01738
G1 X169.341 Y162.567 E.01642
G1 X169.769 Y162.543 E.01627
G1 X170.196 Y162.422 E.01688
G1 X170.624 Y162.17 E.01886
G1 X171.479 Y161.372 E.04442
G1 X171.907 Y161.08 E.01968
G1 X172.334 Y160.917 E.01738
G1 X172.762 Y160.854 E.01642
G1 X173.189 Y160.877 E.01627
G1 X173.617 Y160.998 E.01688
G1 X174.044 Y161.251 E.01886
G1 X174.9 Y162.048 E.04442
G1 X175.327 Y162.341 E.01968
G1 X175.755 Y162.504 E.01738
G1 X176.182 Y162.567 E.01642
G1 X176.61 Y162.543 E.01627
G1 X177.037 Y162.422 E.01688
G1 X177.465 Y162.17 E.01886
G1 X178.32 Y161.372 E.04442
G1 X178.748 Y161.08 E.01968
G1 X179.175 Y160.917 E.01738
G1 X179.603 Y160.854 E.01642
G1 X180.03 Y160.877 E.01627
G1 X180.458 Y160.998 E.01688
G1 X180.885 Y161.251 E.01886
G1 X181.741 Y162.048 E.04442
G1 X182.168 Y162.341 E.01968
G1 X182.596 Y162.504 E.01738
G1 X183.023 Y162.567 E.01642
G1 X183.451 Y162.543 E.01627
G1 X183.878 Y162.422 E.01688
G1 X184.306 Y162.17 E.01886
G1 X185.161 Y161.372 E.04442
G1 X185.589 Y161.08 E.01968
G1 X186.016 Y160.917 E.01738
G1 X186.444 Y160.854 E.01642
G1 X186.871 Y160.877 E.01627
G1 X187.299 Y160.998 E.01688
G1 X187.726 Y161.251 E.01886
G1 X188.566 Y162.033 E.04358
G1 X188.566 Y158.735 E.12531
G1 X187.726 Y157.952 E.0436
G1 X187.299 Y157.659 E.01968
G1 X186.871 Y157.496 E.01738
G1 X186.444 Y157.433 E.01642
G1 X186.016 Y157.457 E.01627
G1 X185.589 Y157.578 E.01688
G1 X185.161 Y157.83 E.01886
G1 X184.306 Y158.628 E.04442
G1 X183.878 Y158.92 E.01968
G1 X183.451 Y159.083 E.01738
G1 X183.023 Y159.146 E.01642
G1 X182.596 Y159.123 E.01627
G1 X182.168 Y159.002 E.01688
G1 X181.741 Y158.749 E.01886
G1 X180.885 Y157.952 E.04442
G1 X180.458 Y157.659 E.01968
G1 X180.03 Y157.496 E.01738
G1 X179.603 Y157.433 E.01642
G1 X179.175 Y157.457 E.01627
G1 X178.748 Y157.578 E.01688
G1 X178.32 Y157.83 E.01886
G1 X177.465 Y158.628 E.04442
G1 X177.037 Y158.92 E.01968
G1 X176.61 Y159.083 E.01738
G1 X176.182 Y159.146 E.01642
G1 X175.755 Y159.123 E.01627
G1 X175.327 Y159.002 E.01688
G1 X174.9 Y158.749 E.01886
G1 X174.044 Y157.952 E.04442
G1 X173.617 Y157.659 E.01968
G1 X173.189 Y157.496 E.01738
G1 X172.762 Y157.433 E.01642
G1 X172.334 Y157.457 E.01627
G1 X171.907 Y157.578 E.01688
G1 X171.479 Y157.83 E.01886
G1 X170.624 Y158.628 E.04442
G1 X170.196 Y158.92 E.01968
G1 X169.769 Y159.083 E.01738
G1 X169.341 Y159.146 E.01642
G1 X168.914 Y159.123 E.01627
G1 X168.486 Y159.002 E.01688
G1 X168.058 Y158.749 E.01886
G1 X167.203 Y157.952 E.04442
G1 X166.776 Y157.659 E.01968
G1 X166.348 Y157.496 E.01738
G1 X165.921 Y157.433 E.01642
G1 X165.493 Y157.457 E.01627
G1 X165.066 Y157.578 E.01688
G1 X164.638 Y157.83 E.01886
G1 X163.783 Y158.628 E.04442
G1 X163.355 Y158.92 E.01968
G1 X162.928 Y159.083 E.01738
G1 X162.5 Y159.146 E.01642
G1 X162.073 Y159.123 E.01627
G1 X161.645 Y159.002 E.01688
G1 X161.217 Y158.749 E.01886
G1 X160.362 Y157.952 E.04442
G1 X159.935 Y157.659 E.01968
G1 X159.507 Y157.496 E.01738
G1 X159.08 Y157.433 E.01642
G1 X158.652 Y157.457 E.01627
G1 X158.224 Y157.578 E.01688
G1 X157.797 Y157.83 E.01886
G1 X156.942 Y158.628 E.04442
G1 X156.514 Y158.92 E.01968
G1 X156.087 Y159.083 E.01738
G1 X155.659 Y159.146 E.01642
G1 X155.232 Y159.123 E.01627
G1 X154.804 Y159.002 E.01688
G1 X154.376 Y158.749 E.01886
G1 X153.521 Y157.952 E.04442
G1 X153.094 Y157.659 E.01968
G1 X152.666 Y157.496 E.01738
G1 X152.239 Y157.433 E.01642
G1 X151.811 Y157.457 E.01627
G1 X151.383 Y157.578 E.01688
G1 X150.956 Y157.83 E.01886
G1 X150.101 Y158.628 E.04442
G1 X149.673 Y158.92 E.01968
G1 X149.246 Y159.083 E.01738
G1 X148.818 Y159.146 E.01642
G1 X148.39 Y159.123 E.01627
G1 X147.963 Y159.002 E.01688
G1 X147.535 Y158.749 E.01886
G1 X146.68 Y157.952 E.04442
G1 X146.253 Y157.659 E.01968
G1 X145.825 Y157.496 E.01738
G1 X145.398 Y157.433 E.01642
G1 X144.97 Y157.457 E.01627
G1 X144.542 Y157.578 E.01688
G1 X144.115 Y157.83 E.01886
G1 X143.26 Y158.628 E.04442
G1 X142.832 Y158.92 E.01968
G1 X142.405 Y159.083 E.01738
G1 X141.977 Y159.146 E.01642
G1 X141.549 Y159.123 E.01627
G1 X141.122 Y159.002 E.01688
G1 X140.694 Y158.749 E.01886
G1 X139.839 Y157.952 E.04442
G1 X139.412 Y157.659 E.01968
G1 X138.984 Y157.496 E.01738
G1 X138.556 Y157.433 E.01642
G1 X138.129 Y157.457 E.01627
G1 X137.701 Y157.578 E.01688
G1 X137.274 Y157.83 E.01886
G1 X136.434 Y158.613 E.04359
G1 X136.434 Y155.314 E.12531
G1 X137.274 Y154.531 E.04361
G1 X137.701 Y154.239 E.01968
G1 X138.129 Y154.076 E.01738
G1 X138.556 Y154.013 E.01642
G1 X138.984 Y154.036 E.01627
G1 X139.412 Y154.157 E.01688
G1 X139.839 Y154.41 E.01886
G1 X140.694 Y155.207 E.04442
G1 X141.122 Y155.5 E.01968
G1 X141.549 Y155.663 E.01738
G1 X141.977 Y155.726 E.01642
G1 X142.405 Y155.702 E.01627
G1 X142.832 Y155.581 E.01688
G1 X143.26 Y155.329 E.01886
G1 X144.115 Y154.531 E.04442
G1 X144.542 Y154.239 E.01968
G1 X144.97 Y154.076 E.01738
G1 X145.398 Y154.013 E.01642
G1 X145.825 Y154.036 E.01627
G1 X146.253 Y154.157 E.01688
G1 X146.68 Y154.41 E.01886
G1 X147.535 Y155.207 E.04442
G1 X147.963 Y155.5 E.01968
G1 X148.39 Y155.663 E.01738
G1 X148.818 Y155.726 E.01642
G1 X149.246 Y155.702 E.01627
G1 X149.673 Y155.581 E.01688
G1 X150.101 Y155.329 E.01886
G1 X150.956 Y154.531 E.04442
G1 X151.383 Y154.239 E.01968
G1 X151.811 Y154.076 E.01738
G1 X152.239 Y154.013 E.01642
G1 X152.666 Y154.036 E.01627
G1 X153.094 Y154.157 E.01688
G1 X153.521 Y154.41 E.01886
G1 X154.376 Y155.207 E.04442
G1 X154.804 Y155.5 E.01968
G1 X155.232 Y155.663 E.01738
G1 X155.659 Y155.726 E.01642
G1 X156.087 Y155.702 E.01627
G1 X156.514 Y155.581 E.01688
G1 X156.942 Y155.329 E.01886
G1 X157.797 Y154.531 E.04442
G1 X158.224 Y154.239 E.01968
G1 X158.652 Y154.076 E.01738
G1 X159.08 Y154.013 E.01642
G1 X159.507 Y154.036 E.01627
G1 X159.935 Y154.157 E.01688
G1 X160.362 Y154.41 E.01886
G1 X161.217 Y155.207 E.04442
G1 X161.645 Y155.5 E.01968
G1 X162.073 Y155.663 E.01738
G1 X162.5 Y155.726 E.01642
G1 X162.928 Y155.702 E.01627
G1 X163.355 Y155.581 E.01688
G1 X163.783 Y155.329 E.01886
G1 X164.638 Y154.531 E.04442
G1 X165.066 Y154.239 E.01968
G1 X165.493 Y154.076 E.01738
G1 X165.921 Y154.013 E.01642
G1 X166.348 Y154.036 E.01627
G1 X166.776 Y154.157 E.01688
G1 X167.203 Y154.41 E.01886
G1 X168.058 Y155.207 E.04442
G1 X168.486 Y155.5 E.01968
G1 X168.914 Y155.663 E.01738
G1 X169.341 Y155.726 E.01642
G1 X169.769 Y155.702 E.01627
G1 X170.196 Y155.581 E.01688
G1 X170.624 Y155.329 E.01886
G1 X171.479 Y154.531 E.04442
G1 X171.907 Y154.239 E.01968
G1 X172.334 Y154.076 E.01738
G1 X172.762 Y154.013 E.01642
G1 X173.189 Y154.036 E.01627
G1 X173.617 Y154.157 E.01688
G1 X174.044 Y154.41 E.01886
G1 X174.9 Y155.207 E.04442
G1 X175.327 Y155.5 E.01968
G1 X175.755 Y155.663 E.01738
G1 X176.182 Y155.726 E.01642
G1 X176.61 Y155.702 E.01627
G1 X177.037 Y155.581 E.01688
G1 X177.465 Y155.329 E.01886
G1 X178.32 Y154.531 E.04442
G1 X178.748 Y154.239 E.01968
G1 X179.175 Y154.076 E.01738
G1 X179.603 Y154.013 E.01642
G1 X180.03 Y154.036 E.01627
G1 X180.458 Y154.157 E.01688
G1 X180.885 Y154.41 E.01886
G1 X181.741 Y155.207 E.04442
G1 X182.168 Y155.5 E.01968
G1 X182.596 Y155.663 E.01738
G1 X183.023 Y155.726 E.01642
G1 X183.451 Y155.702 E.01627
G1 X183.878 Y155.581 E.01688
G1 X184.306 Y155.329 E.01886
G1 X185.161 Y154.531 E.04442
G1 X185.589 Y154.239 E.01968
G1 X186.016 Y154.076 E.01738
G1 X186.444 Y154.013 E.01642
G1 X186.871 Y154.036 E.01627
G1 X187.299 Y154.157 E.01688
G1 X187.726 Y154.41 E.01886
G1 X188.566 Y155.192 E.04358
G1 X188.566 Y156.786 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 1.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X188.566 Y155.192 E-.60572
G1 X188.269 Y154.915 E-.15428
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 8/44
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.04 I-1.215 J.067 P1  F60000
G1 X188.907 Y166.407 Z2.04
G1 Z1.88
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X188.396 Y166.052 Z2.28 F60000
G1 Z1.88
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.391605
G1 F12000
M204 S8000
G1 X188.525 Y166.025 E.00427
G1 X188.552 Y165.896 E.00427
G1 X188.552 Y154.104 E.38237
G1 X188.525 Y153.975 E.00427
G1 X188.396 Y153.948 E.00427
G1 X136.604 Y153.948 E1.67938
G1 X136.475 Y153.975 E.00427
G1 X136.448 Y154.104 E.00427
G1 X136.448 Y165.896 E.38237
G1 X136.475 Y166.025 E.00427
G1 X136.604 Y166.052 E.00427
G1 X188.336 Y166.052 E1.67744
; WIPE_START
G1 X186.336 Y166.052 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.704 Y165.996 Z2.28 F60000
G1 X138.041 Y165.697 Z2.28
G1 Z1.88
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X136.803 Y165.697 E.04703
G1 X136.803 Y165.341 E.01353
G1 X137.274 Y164.876 E.02513
G1 X137.701 Y164.553 E.02037
G1 X138.129 Y164.36 E.01782
G1 X138.556 Y164.269 E.01661
G1 X138.984 Y164.264 E.01625
G1 X139.412 Y164.356 E.01661
G1 X139.839 Y164.581 E.01835
G1 X140.267 Y164.959 E.02169
G1 X140.694 Y165.385 E.02294
G1 X141.106 Y165.697 E.01963
G1 X143.229 Y165.697 E.08066
G1 X143.687 Y165.303 E.02296
G1 X144.115 Y164.876 E.02294
G1 X144.542 Y164.553 E.02037
G1 X144.97 Y164.36 E.01782
G1 X145.398 Y164.269 E.01661
G1 X145.825 Y164.264 E.01625
G1 X146.253 Y164.356 E.01661
G1 X146.68 Y164.581 E.01835
G1 X147.108 Y164.959 E.02169
G1 X147.535 Y165.385 E.02294
G1 X147.947 Y165.697 E.01963
G1 X150.07 Y165.697 E.08066
G1 X150.528 Y165.303 E.02296
G1 X150.956 Y164.876 E.02294
G1 X151.383 Y164.553 E.02037
G1 X151.811 Y164.36 E.01782
G1 X152.239 Y164.269 E.01661
G1 X152.666 Y164.264 E.01625
G1 X153.094 Y164.356 E.01661
G1 X153.521 Y164.581 E.01835
G1 X153.949 Y164.959 E.02169
G1 X154.376 Y165.385 E.02294
G1 X154.788 Y165.697 E.01963
G1 X156.912 Y165.697 E.08066
G1 X157.369 Y165.303 E.02296
G1 X157.797 Y164.876 E.02294
G1 X158.224 Y164.553 E.02037
G1 X158.652 Y164.36 E.01782
G1 X159.08 Y164.269 E.01661
G1 X159.507 Y164.264 E.01625
G1 X159.935 Y164.356 E.01661
G1 X160.362 Y164.581 E.01835
G1 X160.79 Y164.959 E.02169
G1 X161.217 Y165.385 E.02294
G1 X161.63 Y165.697 E.01963
G1 X163.753 Y165.697 E.08066
G1 X164.21 Y165.303 E.02296
G1 X164.638 Y164.876 E.02294
G1 X165.066 Y164.553 E.02037
G1 X165.493 Y164.36 E.01782
G1 X165.921 Y164.269 E.01661
G1 X166.348 Y164.264 E.01625
G1 X166.776 Y164.356 E.01661
G1 X167.203 Y164.581 E.01835
G1 X167.631 Y164.959 E.02169
G1 X168.058 Y165.385 E.02294
G1 X168.471 Y165.697 E.01963
G1 X170.594 Y165.697 E.08066
G1 X171.051 Y165.303 E.02296
G1 X171.479 Y164.876 E.02294
G1 X171.907 Y164.553 E.02037
G1 X172.334 Y164.36 E.01782
G1 X172.762 Y164.269 E.01661
G1 X173.189 Y164.264 E.01625
G1 X173.617 Y164.356 E.01661
G1 X174.044 Y164.581 E.01835
G1 X174.472 Y164.959 E.02169
G1 X174.9 Y165.385 E.02294
G1 X175.312 Y165.697 E.01963
G1 X177.435 Y165.697 E.08066
G1 X177.892 Y165.303 E.02296
G1 X178.32 Y164.876 E.02294
G1 X178.748 Y164.553 E.02037
M73 P56 R5
G1 X179.175 Y164.36 E.01782
G1 X179.603 Y164.269 E.01661
G1 X180.03 Y164.264 E.01625
G1 X180.458 Y164.356 E.01661
G1 X180.885 Y164.581 E.01835
G1 X181.313 Y164.959 E.02169
G1 X181.741 Y165.385 E.02294
G1 X182.153 Y165.697 E.01963
G1 X184.276 Y165.697 E.08066
G1 X184.734 Y165.303 E.02296
G1 X185.161 Y164.876 E.02294
G1 X185.589 Y164.553 E.02037
G1 X186.016 Y164.36 E.01782
G1 X186.444 Y164.269 E.01661
G1 X186.871 Y164.264 E.01625
G1 X187.299 Y164.356 E.01661
G1 X187.726 Y164.581 E.01835
G1 X188.197 Y165.002 E.02399
G1 X188.197 Y161.92 E.11708
G1 X187.726 Y161.456 E.02512
G1 X187.299 Y161.132 E.02037
G1 X186.871 Y160.939 E.01782
G1 X186.444 Y160.849 E.01661
G1 X186.016 Y160.844 E.01625
G1 X185.589 Y160.935 E.01661
G1 X185.161 Y161.16 E.01835
G1 X184.734 Y161.538 E.02169
G1 X184.306 Y161.965 E.02294
G1 X183.878 Y162.288 E.02037
G1 X183.451 Y162.481 E.01782
G1 X183.023 Y162.572 E.01661
G1 X182.596 Y162.577 E.01625
G1 X182.168 Y162.485 E.01661
G1 X181.741 Y162.261 E.01835
G1 X181.313 Y161.882 E.02169
G1 X180.885 Y161.456 E.02294
G1 X180.458 Y161.132 E.02037
G1 X180.03 Y160.939 E.01782
G1 X179.603 Y160.849 E.01661
G1 X179.175 Y160.844 E.01625
G1 X178.748 Y160.935 E.01661
G1 X178.32 Y161.16 E.01835
G1 X177.892 Y161.538 E.02169
G1 X177.465 Y161.965 E.02294
G1 X177.037 Y162.288 E.02037
G1 X176.61 Y162.481 E.01782
G1 X176.182 Y162.572 E.01661
G1 X175.755 Y162.577 E.01625
G1 X175.327 Y162.485 E.01661
G1 X174.9 Y162.261 E.01835
G1 X174.472 Y161.882 E.02169
G1 X174.044 Y161.456 E.02294
G1 X173.617 Y161.132 E.02037
G1 X173.189 Y160.939 E.01782
G1 X172.762 Y160.849 E.01661
G1 X172.334 Y160.844 E.01625
G1 X171.907 Y160.935 E.01661
G1 X171.479 Y161.16 E.01835
G1 X171.051 Y161.538 E.02169
G1 X170.624 Y161.965 E.02294
G1 X170.196 Y162.288 E.02037
G1 X169.769 Y162.481 E.01782
G1 X169.341 Y162.572 E.01661
G1 X168.914 Y162.577 E.01625
G1 X168.486 Y162.485 E.01661
G1 X168.058 Y162.261 E.01835
G1 X167.631 Y161.882 E.02169
G1 X167.203 Y161.456 E.02294
G1 X166.776 Y161.132 E.02037
G1 X166.348 Y160.939 E.01782
G1 X165.921 Y160.849 E.01661
G1 X165.493 Y160.844 E.01625
G1 X165.066 Y160.935 E.01661
G1 X164.638 Y161.16 E.01835
G1 X164.21 Y161.538 E.02169
G1 X163.783 Y161.965 E.02294
G1 X163.355 Y162.288 E.02037
G1 X162.928 Y162.481 E.01782
G1 X162.5 Y162.572 E.01661
G1 X162.073 Y162.577 E.01625
G1 X161.645 Y162.485 E.01661
G1 X161.217 Y162.261 E.01835
G1 X160.79 Y161.882 E.02169
G1 X160.362 Y161.456 E.02294
G1 X159.935 Y161.132 E.02037
G1 X159.507 Y160.939 E.01782
G1 X159.08 Y160.849 E.01661
G1 X158.652 Y160.844 E.01625
G1 X158.224 Y160.935 E.01661
G1 X157.797 Y161.16 E.01835
G1 X157.369 Y161.538 E.02169
G1 X156.942 Y161.965 E.02294
G1 X156.514 Y162.288 E.02037
G1 X156.087 Y162.481 E.01782
G1 X155.659 Y162.572 E.01661
G1 X155.232 Y162.577 E.01625
G1 X154.804 Y162.485 E.01661
G1 X154.376 Y162.261 E.01835
G1 X153.949 Y161.882 E.02169
G1 X153.521 Y161.456 E.02294
G1 X153.094 Y161.132 E.02037
G1 X152.666 Y160.939 E.01782
G1 X152.239 Y160.849 E.01661
G1 X151.811 Y160.844 E.01625
G1 X151.383 Y160.935 E.01661
G1 X150.956 Y161.16 E.01835
G1 X150.528 Y161.538 E.02169
G1 X150.101 Y161.965 E.02294
G1 X149.673 Y162.288 E.02037
G1 X149.246 Y162.481 E.01782
G1 X148.818 Y162.572 E.01661
G1 X148.39 Y162.577 E.01625
G1 X147.963 Y162.485 E.01661
G1 X147.535 Y162.261 E.01835
G1 X147.108 Y161.882 E.02169
G1 X146.68 Y161.456 E.02294
G1 X146.253 Y161.132 E.02037
G1 X145.825 Y160.939 E.01782
G1 X145.398 Y160.849 E.01661
G1 X144.97 Y160.844 E.01625
G1 X144.542 Y160.935 E.01661
G1 X144.115 Y161.16 E.01835
G1 X143.687 Y161.538 E.02169
G1 X143.26 Y161.965 E.02294
G1 X142.832 Y162.288 E.02037
G1 X142.405 Y162.481 E.01782
G1 X141.977 Y162.572 E.01661
G1 X141.549 Y162.577 E.01625
G1 X141.122 Y162.485 E.01661
G1 X140.694 Y162.261 E.01835
G1 X140.267 Y161.882 E.02169
G1 X139.839 Y161.456 E.02294
G1 X139.412 Y161.132 E.02037
G1 X138.984 Y160.939 E.01782
G1 X138.556 Y160.849 E.01661
G1 X138.129 Y160.844 E.01625
G1 X137.701 Y160.935 E.01661
G1 X137.274 Y161.16 E.01835
G1 X136.803 Y161.582 E.02401
G1 X136.803 Y158.5 E.11708
G1 X137.274 Y158.035 E.02513
G1 X137.701 Y157.712 E.02037
G1 X138.129 Y157.519 E.01782
G1 X138.556 Y157.428 E.01661
G1 X138.984 Y157.423 E.01625
G1 X139.412 Y157.515 E.01661
G1 X139.839 Y157.739 E.01835
G1 X140.267 Y158.118 E.02169
G1 X140.694 Y158.544 E.02294
G1 X141.122 Y158.868 E.02037
G1 X141.549 Y159.061 E.01782
G1 X141.977 Y159.152 E.01661
G1 X142.405 Y159.156 E.01625
G1 X142.832 Y159.065 E.01661
G1 X143.26 Y158.84 E.01835
G1 X143.687 Y158.462 E.02169
G1 X144.115 Y158.035 E.02294
G1 X144.542 Y157.712 E.02037
G1 X144.97 Y157.519 E.01782
G1 X145.398 Y157.428 E.01661
G1 X145.825 Y157.423 E.01625
G1 X146.253 Y157.515 E.01661
G1 X146.68 Y157.739 E.01835
G1 X147.108 Y158.118 E.02169
G1 X147.535 Y158.544 E.02294
G1 X147.963 Y158.868 E.02037
G1 X148.39 Y159.061 E.01782
G1 X148.818 Y159.152 E.01661
G1 X149.246 Y159.156 E.01625
G1 X149.673 Y159.065 E.01661
G1 X150.101 Y158.84 E.01835
G1 X150.528 Y158.462 E.02169
G1 X150.956 Y158.035 E.02294
G1 X151.383 Y157.712 E.02037
G1 X151.811 Y157.519 E.01782
G1 X152.239 Y157.428 E.01661
G1 X152.666 Y157.423 E.01625
G1 X153.094 Y157.515 E.01661
G1 X153.521 Y157.739 E.01835
G1 X153.949 Y158.118 E.02169
G1 X154.376 Y158.544 E.02294
G1 X154.804 Y158.868 E.02037
G1 X155.232 Y159.061 E.01782
G1 X155.659 Y159.152 E.01661
G1 X156.087 Y159.156 E.01625
G1 X156.514 Y159.065 E.01661
G1 X156.942 Y158.84 E.01835
G1 X157.369 Y158.462 E.02169
G1 X157.797 Y158.035 E.02294
G1 X158.224 Y157.712 E.02037
G1 X158.652 Y157.519 E.01782
G1 X159.08 Y157.428 E.01661
G1 X159.507 Y157.423 E.01625
G1 X159.935 Y157.515 E.01661
G1 X160.362 Y157.739 E.01835
G1 X160.79 Y158.118 E.02169
G1 X161.217 Y158.544 E.02294
G1 X161.645 Y158.868 E.02037
G1 X162.073 Y159.061 E.01782
G1 X162.5 Y159.152 E.01661
G1 X162.928 Y159.156 E.01625
G1 X163.355 Y159.065 E.01661
G1 X163.783 Y158.84 E.01835
G1 X164.21 Y158.462 E.02169
G1 X164.638 Y158.035 E.02294
G1 X165.066 Y157.712 E.02037
G1 X165.493 Y157.519 E.01782
G1 X165.921 Y157.428 E.01661
G1 X166.348 Y157.423 E.01625
G1 X166.776 Y157.515 E.01661
G1 X167.203 Y157.739 E.01835
G1 X167.631 Y158.118 E.02169
G1 X168.058 Y158.544 E.02294
G1 X168.486 Y158.868 E.02037
G1 X168.914 Y159.061 E.01782
G1 X169.341 Y159.152 E.01661
G1 X169.769 Y159.156 E.01625
G1 X170.196 Y159.065 E.01661
G1 X170.624 Y158.84 E.01835
G1 X171.051 Y158.462 E.02169
G1 X171.479 Y158.035 E.02294
G1 X171.907 Y157.712 E.02037
G1 X172.334 Y157.519 E.01782
G1 X172.762 Y157.428 E.01661
G1 X173.189 Y157.423 E.01625
G1 X173.617 Y157.515 E.01661
G1 X174.044 Y157.739 E.01835
G1 X174.472 Y158.118 E.02169
G1 X174.9 Y158.544 E.02294
G1 X175.327 Y158.868 E.02037
G1 X175.755 Y159.061 E.01782
G1 X176.182 Y159.152 E.01661
G1 X176.61 Y159.156 E.01625
G1 X177.037 Y159.065 E.01661
G1 X177.465 Y158.84 E.01835
G1 X177.892 Y158.462 E.02169
G1 X178.32 Y158.035 E.02294
G1 X178.748 Y157.712 E.02037
G1 X179.175 Y157.519 E.01782
G1 X179.603 Y157.428 E.01661
G1 X180.03 Y157.423 E.01625
G1 X180.458 Y157.515 E.01661
G1 X180.885 Y157.739 E.01835
G1 X181.313 Y158.118 E.02169
G1 X181.741 Y158.544 E.02294
G1 X182.168 Y158.868 E.02037
G1 X182.596 Y159.061 E.01782
G1 X183.023 Y159.152 E.01661
G1 X183.451 Y159.156 E.01625
G1 X183.878 Y159.065 E.01661
G1 X184.306 Y158.84 E.01835
G1 X184.734 Y158.462 E.02169
G1 X185.161 Y158.035 E.02294
G1 X185.589 Y157.712 E.02037
G1 X186.016 Y157.519 E.01782
G1 X186.444 Y157.428 E.01661
G1 X186.871 Y157.423 E.01625
G1 X187.299 Y157.515 E.01661
G1 X187.726 Y157.739 E.01835
G1 X188.197 Y158.161 E.02399
G1 X188.197 Y155.079 E.11708
G1 X187.726 Y154.615 E.02512
G1 X187.314 Y154.303 E.01963
G1 X185.191 Y154.303 E.08065
G1 X184.734 Y154.697 E.02296
G1 X184.306 Y155.124 E.02294
G1 X183.878 Y155.447 E.02037
G1 X183.451 Y155.64 E.01782
G1 X183.023 Y155.731 E.01661
G1 X182.596 Y155.736 E.01625
G1 X182.168 Y155.644 E.01661
G1 X181.741 Y155.42 E.01835
G1 X181.313 Y155.041 E.02169
G1 X180.885 Y154.615 E.02294
G1 X180.473 Y154.303 E.01963
G1 X178.35 Y154.303 E.08065
G1 X177.892 Y154.697 E.02296
G1 X177.465 Y155.124 E.02294
G1 X177.037 Y155.447 E.02037
G1 X176.61 Y155.64 E.01782
G1 X176.182 Y155.731 E.01661
G1 X175.755 Y155.736 E.01625
G1 X175.327 Y155.644 E.01661
G1 X174.9 Y155.42 E.01835
G1 X174.472 Y155.041 E.02169
G1 X174.044 Y154.615 E.02294
G1 X173.632 Y154.303 E.01963
G1 X171.509 Y154.303 E.08065
G1 X171.051 Y154.697 E.02296
G1 X170.624 Y155.124 E.02294
G1 X170.196 Y155.447 E.02037
G1 X169.769 Y155.64 E.01782
G1 X169.341 Y155.731 E.01661
G1 X168.914 Y155.736 E.01625
G1 X168.486 Y155.644 E.01661
G1 X168.058 Y155.42 E.01835
G1 X167.631 Y155.041 E.02169
G1 X167.203 Y154.615 E.02294
G1 X166.791 Y154.303 E.01963
G1 X164.668 Y154.303 E.08065
G1 X164.21 Y154.697 E.02296
G1 X163.783 Y155.124 E.02294
G1 X163.355 Y155.447 E.02037
G1 X162.928 Y155.64 E.01782
G1 X162.5 Y155.731 E.01661
G1 X162.073 Y155.736 E.01625
G1 X161.645 Y155.644 E.01661
G1 X161.217 Y155.42 E.01835
G1 X160.79 Y155.041 E.02169
G1 X160.362 Y154.615 E.02294
G1 X159.95 Y154.303 E.01963
G1 X157.827 Y154.303 E.08065
G1 X157.369 Y154.697 E.02296
G1 X156.942 Y155.124 E.02294
G1 X156.514 Y155.447 E.02037
G1 X156.087 Y155.64 E.01782
G1 X155.659 Y155.731 E.01661
G1 X155.232 Y155.736 E.01625
G1 X154.804 Y155.644 E.01661
G1 X154.376 Y155.42 E.01835
G1 X153.949 Y155.041 E.02169
G1 X153.521 Y154.615 E.02294
G1 X153.109 Y154.303 E.01963
G1 X150.986 Y154.303 E.08065
G1 X150.528 Y154.697 E.02296
G1 X150.101 Y155.124 E.02294
G1 X149.673 Y155.447 E.02037
G1 X149.246 Y155.64 E.01782
G1 X148.818 Y155.731 E.01661
G1 X148.39 Y155.736 E.01625
G1 X147.963 Y155.644 E.01661
G1 X147.535 Y155.42 E.01835
G1 X147.108 Y155.041 E.02169
G1 X146.68 Y154.615 E.02294
G1 X146.268 Y154.303 E.01963
G1 X144.145 Y154.303 E.08065
G1 X143.687 Y154.697 E.02296
G1 X143.26 Y155.124 E.02294
G1 X142.832 Y155.447 E.02037
G1 X142.405 Y155.64 E.01782
G1 X141.977 Y155.731 E.01661
G1 X141.549 Y155.736 E.01625
G1 X141.122 Y155.644 E.01661
G1 X140.694 Y155.42 E.01835
G1 X140.267 Y155.041 E.02169
G1 X139.839 Y154.615 E.02294
G1 X139.427 Y154.303 E.01963
G1 X137.304 Y154.303 E.08065
G1 X136.803 Y154.74 E.02527
G1 X136.803 Y156.334 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 2.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X136.803 Y154.74 E-.60572
G1 X137.109 Y154.473 E-.15428
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 9/44
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.28 I-.273 J1.186 P1  F60000
G1 X188.907 Y166.407 Z2.28
G1 Z2.12
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.147 Y166.242 Z2.52 F60000
G1 Z2.12
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.40238
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X178.555 Y160.849 E.32732
G1 X178.926 Y160.748 E.01938
G1 X179.032 Y160.749 E.00539
G1 X182.556 Y166.04 E.32111
G1 X183.099 Y166.04 E.02746
G1 X179.626 Y160.825 E.31653
G1 X180.019 Y160.952 E.02086
G1 X180.555 Y161.403 E.03538
G1 X183.643 Y166.04 E.28142
G1 X184.186 Y166.04 E.02746
G1 X181.605 Y162.164 E.23527
G1 X182.116 Y162.423 E.02897
G1 X182.331 Y162.437 E.01086
G1 X184.73 Y166.04 E.21865
G1 X185.273 Y166.04 E.02746
G1 X182.878 Y162.443 E.2183
G1 X183.291 Y162.365 E.02124
G1 X183.352 Y162.338 E.00335
G1 X185.817 Y166.04 E.22466
G1 X186.36 Y166.04 E.02746
G1 X183.77 Y162.151 E.23605
G1 X183.802 Y162.136 E.00178
G1 X183.802 Y161.605 E.02684
G1 X182.644 Y159.866 E.10557
G1 X182.726 Y159.766 E.0065
G1 X186.904 Y166.04 E.38075
G1 X187.447 Y166.04 E.02746
M73 P57 R5
G1 X179.403 Y153.96 E.73316
G1 X178.859 Y153.96 E.02746
G1 X181.845 Y158.443 E.27207
G1 X181.133 Y157.828 E.04748
G1 X180.815 Y157.713 E.01711
G1 X178.316 Y153.96 E.22777
G1 X177.772 Y153.96 E.02746
G1 X180.159 Y157.544 E.21753
G1 X179.739 Y157.548 E.02124
G1 X179.636 Y157.575 E.00535
G1 X177.229 Y153.96 E.21939
G1 X176.685 Y153.96 E.02746
G1 X179.179 Y157.705 E.22729
G1 X178.773 Y157.911 E.02301
G1 X176.142 Y153.96 E.23981
G1 X175.598 Y153.96 E.02746
G1 X178.412 Y158.185 E.25641
G1 X178.083 Y158.508 E.02327
G1 X175.055 Y153.96 E.27602
G1 X174.511 Y153.96 E.02746
G1 X177.747 Y158.819 E.29489
G1 X177.38 Y159.084 E.02287
G1 X173.968 Y153.96 E.31097
G1 X173.424 Y153.96 E.02746
G1 X181.469 Y166.04 E.73316
G1 X180.925 Y166.04 E.02746
G1 X172.881 Y153.96 E.73316
G1 X172.337 Y153.96 E.02746
G1 X180.382 Y166.04 E.73316
G1 X179.838 Y166.04 E.02746
G1 X171.794 Y153.96 E.73316
G1 X171.25 Y153.96 E.02746
G1 X179.295 Y166.04 E.73316
G1 X178.751 Y166.04 E.02746
G1 X170.707 Y153.96 E.73316
G1 X170.163 Y153.96 E.02746
G1 X178.208 Y166.04 E.73316
G1 X177.664 Y166.04 E.02746
G1 X169.62 Y153.96 E.73316
G1 X169.076 Y153.96 E.02746
M73 P58 R5
G1 X177.121 Y166.04 E.73316
G1 X176.577 Y166.04 E.02746
G1 X168.532 Y153.96 E.73316
G1 X167.989 Y153.96 E.02746
G1 X176.034 Y166.04 E.73316
G1 X175.49 Y166.04 E.02746
G1 X167.445 Y153.96 E.73316
G1 X166.902 Y153.96 E.02746
G1 X174.947 Y166.04 E.73316
G1 X174.403 Y166.04 E.02746
G1 X166.358 Y153.96 E.73316
G1 X165.815 Y153.96 E.02746
G1 X173.86 Y166.04 E.73316
G1 X173.316 Y166.04 E.02746
G1 X165.271 Y153.96 E.73316
G1 X164.728 Y153.96 E.02746
G1 X172.772 Y166.04 E.73316
G1 X172.229 Y166.04 E.02746
G1 X164.184 Y153.96 E.73316
G1 X163.641 Y153.96 E.02746
M73 P58 R4
G1 X171.685 Y166.04 E.73316
G1 X171.142 Y166.04 E.02746
G1 X163.097 Y153.96 E.73316
G1 X162.554 Y153.96 E.02746
M73 P59 R4
G1 X170.598 Y166.04 E.73316
G1 X170.055 Y166.04 E.02746
G1 X162.01 Y153.96 E.73316
G1 X161.467 Y153.96 E.02746
G1 X164.457 Y158.451 E.27256
G1 X164.124 Y158.766 E.02318
G1 X160.923 Y153.96 E.29167
G1 X160.38 Y153.96 E.02746
G1 X163.765 Y159.043 E.30851
G1 X163.481 Y159.187 E.01608
G1 X163.335 Y159.213 E.00751
G1 X159.836 Y153.96 E.31882
G1 X159.293 Y153.96 E.02746
G1 X162.808 Y159.239 E.32038
G1 X162.551 Y159.215 E.01304
G1 X162.122 Y159.024 E.02376
G1 X158.749 Y153.96 E.30734
G1 X158.206 Y153.96 E.02746
G1 X161.058 Y158.243 E.25995
G1 X160.719 Y158.551 E.02311
G1 X157.662 Y153.96 E.27861
G1 X157.119 Y153.96 E.02746
G1 X165.163 Y166.04 E.73316
G1 X164.62 Y166.04 E.02746
G1 X156.575 Y153.96 E.73316
G1 X156.032 Y153.96 E.02746
G1 X164.076 Y166.04 E.73316
G1 X163.533 Y166.04 E.02746
G1 X155.488 Y153.96 E.73316
G1 X154.945 Y153.96 E.02746
G1 X162.989 Y166.04 E.73316
G1 X162.446 Y166.04 E.02746
G1 X154.401 Y153.96 E.73316
G1 X153.858 Y153.96 E.02746
G1 X161.902 Y166.04 E.73316
G1 X161.359 Y166.04 E.02746
M73 P60 R4
G1 X153.314 Y153.96 E.73316
G1 X152.771 Y153.96 E.02746
G1 X160.815 Y166.04 E.73316
G1 X160.272 Y166.04 E.02746
G1 X152.227 Y153.96 E.73316
G1 X151.684 Y153.96 E.02746
G1 X159.728 Y166.04 E.73316
G1 X159.185 Y166.04 E.02746
G1 X151.14 Y153.96 E.73316
G1 X150.597 Y153.96 E.02746
G1 X158.641 Y166.04 E.73316
G1 X158.098 Y166.04 E.02746
G1 X150.053 Y153.96 E.73316
G1 X149.509 Y153.96 E.02746
G1 X157.554 Y166.04 E.73316
G1 X157.011 Y166.04 E.02746
G1 X148.966 Y153.96 E.73316
G1 X148.422 Y153.96 E.02746
G1 X156.467 Y166.04 E.73316
G1 X155.924 Y166.04 E.02746
G1 X147.879 Y153.96 E.73316
G1 X147.335 Y153.96 E.02746
G1 X155.38 Y166.04 E.73316
G1 X154.837 Y166.04 E.02746
M73 P61 R4
G1 X146.792 Y153.96 E.73316
G1 X146.248 Y153.96 E.02746
G1 X154.293 Y166.04 E.73316
G1 X153.75 Y166.04 E.02746
G1 X145.705 Y153.96 E.73316
G1 X145.161 Y153.96 E.02746
G1 X153.206 Y166.04 E.73316
G1 X152.662 Y166.04 E.02746
G1 X144.618 Y153.96 E.73316
G1 X144.074 Y153.96 E.02746
G1 X152.119 Y166.04 E.73316
G1 X151.575 Y166.04 E.02746
G1 X143.396 Y153.758 E.74545
M106 S0
; WIPE_START
G1 X144.505 Y155.422 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X145.365 Y163.006 Z2.52 F60000
G1 X145.732 Y166.242 Z2.52
G1 Z2.12
G1 E.8 F1800
M106 S178.5
G1 F1500
M204 S8000
G1 X142.923 Y162.025 E.25599
G1 X143.26 Y161.715 E.02313
G1 X146.14 Y166.04 E.26248
G1 X146.684 Y166.04 E.02746
G1 X143.595 Y161.402 E.28151
G1 X143.937 Y161.098 E.02307
G1 X147.227 Y166.04 E.29991
G1 X147.771 Y166.04 E.02746
G1 X144.322 Y160.861 E.31433
G1 X144.416 Y160.813 E.00535
G1 X144.789 Y160.747 E.01915
G1 X148.314 Y166.04 E.32125
G1 X148.858 Y166.04 E.02746
G1 X145.363 Y160.792 E.3185
G1 X146.05 Y161.098 E.03798
G1 X146.19 Y161.218 E.00933
G1 X149.401 Y166.04 E.29265
G1 X149.945 Y166.04 E.02746
G1 X146.508 Y160.879 E.31323
G1 X146.81 Y160.516 E.02385
M73 P62 R4
G1 X150.488 Y166.04 E.33527
G1 X151.032 Y166.04 E.02746
G1 X142.987 Y153.96 E.73316
G1 X142.444 Y153.96 E.02746
G1 X144.947 Y157.719 E.22813
G1 X144.684 Y157.834 E.01448
G1 X144.547 Y157.934 E.0086
G1 X141.9 Y153.96 E.24119
G1 X141.357 Y153.96 E.02746
G1 X144.19 Y158.214 E.25819
G1 X143.855 Y158.527 E.02316
G1 X140.813 Y153.96 E.27718
G1 X140.27 Y153.96 E.02746
G1 X143.516 Y158.835 E.29587
G1 X143.295 Y159.016 E.01443
G1 X143.143 Y159.091 E.00856
G1 X139.726 Y153.96 E.31141
G1 X139.183 Y153.96 E.02746
G1 X142.694 Y159.232 E.31996
G1 X142.517 Y159.261 E.00906
G1 X142.145 Y159.225 E.01886
G1 X138.639 Y153.96 E.31951
G1 X138.096 Y153.96 E.02746
G1 X141.563 Y159.167 E.316
G1 X141.297 Y159.14 E.01348
G1 X141.297 Y159.584 E.02242
G1 X137.552 Y153.96 E.34133
G1 X137.009 Y153.96 E.02746
G1 X145.053 Y166.04 E.73316
G1 X144.51 Y166.04 E.02746
G1 X136.465 Y153.96 E.73316
G1 X136.46 Y154.769 E.04084
G1 X143.966 Y166.04 E.68408
G1 X143.423 Y166.04 E.02746
G1 X136.46 Y155.585 E.63455
G1 X136.46 Y156.401 E.04123
G1 X142.879 Y166.04 E.58502
G1 X142.336 Y166.04 E.02746
G1 X136.46 Y157.217 E.53548
G1 X136.46 Y158.033 E.04123
G1 X141.792 Y166.04 E.48595
G1 X141.249 Y166.04 E.02746
G1 X136.46 Y158.849 E.43641
G1 X136.46 Y159.665 E.04123
M73 P63 R4
G1 X140.705 Y166.04 E.38688
G1 X140.162 Y166.04 E.02746
G1 X136.46 Y160.482 E.33735
G1 X136.46 Y161.298 E.04123
G1 X139.618 Y166.04 E.28781
G1 X139.075 Y166.04 E.02746
G1 X136.46 Y162.114 E.23828
G1 X136.46 Y162.93 E.04123
G1 X138.531 Y166.04 E.18875
G1 X137.988 Y166.04 E.02746
G1 X136.46 Y163.746 E.13921
G1 X136.46 Y164.562 E.04123
G1 X137.444 Y166.04 E.08968
G1 X136.901 Y166.04 E.02746
G1 X136.258 Y165.074 E.0586
M106 S0
; WIPE_START
G1 X136.901 Y166.04 E-.44081
G1 X137.444 Y166.04 E-.20653
G1 X137.28 Y165.793 E-.11266
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X144.832 Y164.688 Z2.52 F60000
G1 X163.033 Y162.024 Z2.52
G1 Z2.12
G1 E.8 F1800
M106 S178.5
G1 F1500
M204 S8000
G1 X165.707 Y166.04 E.24372
G1 X166.25 Y166.04 E.02746
G1 X163.521 Y161.942 E.24873
G1 X163.864 Y161.641 E.02305
G1 X166.794 Y166.04 E.267
G1 X167.337 Y166.04 E.02746
G1 X164.198 Y161.326 E.28611
G1 X164.545 Y161.031 E.02301
G1 X167.881 Y166.04 E.30402
G1 X168.424 Y166.04 E.02746
G1 X164.945 Y160.815 E.31711
G1 X165.432 Y160.73 E.02497
G1 X168.968 Y166.04 E.32227
G1 X169.511 Y166.04 E.02746
G1 X165.246 Y159.635 E.38871
M106 S0
; WIPE_START
G1 X166.355 Y161.3 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.013 Y157.568 Z2.52 F60000
G1 X179.811 Y153.758 Z2.52
G1 Z2.12
G1 E.8 F1800
M106 S178.5
G1 F1500
M204 S8000
G1 X187.991 Y166.04 E.74545
G1 X188.534 Y166.04 E.02746
G1 X180.49 Y153.96 E.73316
G1 X181.033 Y153.96 E.02746
G1 X188.54 Y165.232 E.68412
G1 X188.54 Y164.416 E.04123
G1 X181.577 Y153.96 E.63459
G1 X182.12 Y153.96 E.02746
G1 X188.54 Y163.6 E.58506
G1 X188.54 Y162.784 E.04123
G1 X182.664 Y153.96 E.53552
G1 X183.207 Y153.96 E.02746
M73 P64 R4
G1 X188.54 Y161.967 E.48599
G1 X188.54 Y161.151 E.04123
G1 X183.751 Y153.96 E.43645
G1 X184.294 Y153.96 E.02746
G1 X188.54 Y160.335 E.38692
G1 X188.54 Y159.519 E.04123
G1 X184.838 Y153.96 E.33739
G1 X185.381 Y153.96 E.02746
G1 X188.54 Y158.703 E.28785
G1 X188.54 Y157.887 E.04123
G1 X185.925 Y153.96 E.23832
G1 X186.468 Y153.96 E.02746
G1 X188.54 Y157.071 E.18879
G1 X188.54 Y156.254 E.04123
G1 X187.012 Y153.96 E.13925
G1 X187.555 Y153.96 E.02746
G1 X188.54 Y155.438 E.08972
G1 X188.54 Y154.622 E.04123
G1 X187.964 Y153.758 E.05247
M106 S0
; CHANGE_LAYER
; Z_HEIGHT: 2.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F1500
G1 X188.54 Y154.622 E-.39473
G1 X188.54 Y155.438 E-.31013
G1 X188.459 Y155.318 E-.05514
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 10/44
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.52 I-1.216 J.049 P1  F60000
G1 X188.907 Y166.407 Z2.52
G1 Z2.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X187.996 Y166.247 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422504
G1 F12129.381
M204 S8000
G1 X188.581 Y165.662 E.02924
G1 X188.581 Y165.137 E.01856
G1 X187.637 Y166.081 E.04719
G1 X187.113 Y166.081 E.01856
G1 X188.581 Y164.613 E.07343
G1 X188.581 Y164.088 E.01856
G1 X186.588 Y166.081 E.09968
G1 X186.063 Y166.081 E.01856
G1 X188.581 Y163.563 E.12592
G1 X188.581 Y163.039 E.01856
G1 X185.539 Y166.081 E.15217
G1 X185.014 Y166.081 E.01856
G1 X188.581 Y162.514 E.17841
G1 X188.581 Y161.989 E.01856
G1 X184.489 Y166.081 E.20466
G1 X183.965 Y166.081 E.01856
G1 X188.581 Y161.465 E.2309
G1 X188.581 Y160.94 E.01856
G1 X183.44 Y166.081 E.25715
G1 X182.915 Y166.081 E.01856
G1 X188.581 Y160.415 E.28339
G1 X188.581 Y159.891 E.01856
G1 X182.391 Y166.081 E.30964
G1 X181.866 Y166.081 E.01856
G1 X188.581 Y159.366 E.33589
G1 X188.581 Y158.841 E.01856
G1 X181.341 Y166.081 E.36213
G1 X180.817 Y166.081 E.01856
G1 X188.581 Y158.317 E.38838
G1 X188.581 Y157.792 E.01856
G1 X184.212 Y162.161 E.21855
G1 X184.212 Y161.636 E.01856
G1 X188.581 Y157.267 E.21855
G1 X188.581 Y156.743 E.01856
G1 X184.212 Y161.112 E.21855
G1 X184.212 Y160.587 E.01856
G1 X188.581 Y156.218 E.21855
G1 X188.581 Y155.693 E.01856
G1 X184.212 Y160.062 E.21855
G1 X184.212 Y159.538 E.01856
G1 X188.581 Y155.169 E.21855
G1 X188.581 Y154.644 E.01856
G1 X184.212 Y159.013 E.21855
G1 X184.212 Y158.488 E.01856
G1 X188.581 Y154.119 E.21855
G1 X188.581 Y153.919 E.00707
G1 X188.256 Y153.919 E.01149
G1 X184.212 Y157.964 E.2023
G1 X184.212 Y157.439 E.01856
G1 X187.731 Y153.919 E.17606
G1 X187.207 Y153.919 E.01856
G1 X184.018 Y157.108 E.15951
G1 X183.498 Y157.103 E.01839
G1 X186.682 Y153.919 E.15927
G1 X186.157 Y153.919 E.01856
G1 X182.973 Y157.103 E.15927
G1 X182.449 Y157.103 E.01856
G1 X185.633 Y153.919 E.15927
G1 X185.108 Y153.919 E.01856
G1 X181.924 Y157.103 E.15927
G1 X181.399 Y157.103 E.01856
G1 X184.583 Y153.919 E.15927
G1 X184.059 Y153.919 E.01856
G1 X180.875 Y157.103 E.15927
G1 X180.35 Y157.103 E.01856
M73 P65 R4
G1 X183.534 Y153.919 E.15927
G1 X183.009 Y153.919 E.01856
G1 X179.825 Y157.103 E.15927
G1 X179.301 Y157.103 E.01856
G1 X182.485 Y153.919 E.15927
G1 X181.96 Y153.919 E.01856
G1 X178.776 Y157.103 E.15927
G1 X178.251 Y157.103 E.01856
G1 X181.435 Y153.919 E.15927
G1 X180.911 Y153.919 E.01856
G1 X177.561 Y157.269 E.16756
M204 S10000
G1 X176.954 Y157.876 F60000
G1 F12129.381
M204 S8000
G1 X168.749 Y166.081 E.41043
G1 X169.274 Y166.081 E.01856
G1 X176.788 Y158.566 E.37589
G1 X176.788 Y159.091 E.01856
G1 X169.799 Y166.081 E.34965
G1 X170.323 Y166.081 E.01856
G1 X176.788 Y159.616 E.3234
G1 X176.788 Y160.14 E.01856
G1 X170.848 Y166.081 E.29716
G1 X171.373 Y166.081 E.01856
G1 X176.788 Y160.665 E.27091
G1 X176.788 Y161.19 E.01856
G1 X171.897 Y166.081 E.24467
G1 X172.422 Y166.081 E.01856
G1 X176.788 Y161.714 E.21842
G1 X176.788 Y162.239 E.01856
G1 X172.947 Y166.081 E.19217
G1 X173.471 Y166.081 E.01856
G1 X176.821 Y162.731 E.16756
G1 X176.987 Y162.897 E.00829
G1 X177.18 Y162.897 E.00683
G1 X173.996 Y166.081 E.15927
G1 X174.521 Y166.081 E.01856
G1 X177.705 Y162.897 E.15927
G1 X178.229 Y162.897 E.01856
G1 X175.045 Y166.081 E.15927
G1 X175.57 Y166.081 E.01856
G1 X178.754 Y162.897 E.15927
G1 X179.279 Y162.897 E.01856
G1 X176.095 Y166.081 E.15927
G1 X176.619 Y166.081 E.01856
G1 X179.803 Y162.897 E.15927
G1 X180.328 Y162.897 E.01856
G1 X177.144 Y166.081 E.15927
G1 X177.669 Y166.081 E.01856
G1 X180.853 Y162.897 E.15927
G1 X181.377 Y162.897 E.01856
G1 X178.193 Y166.081 E.15927
G1 X178.718 Y166.081 E.01856
G1 X181.902 Y162.897 E.15927
G1 X182.427 Y162.897 E.01856
G1 X179.243 Y166.081 E.15927
G1 X179.767 Y166.081 E.01856
G1 X182.951 Y162.897 E.15927
G1 X183.476 Y162.897 E.01856
G1 X180.126 Y166.247 E.16756
; WIPE_START
G1 X181.54 Y164.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.828 Y160.522 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X183.828 Y162.116 E.06056
G1 X183.451 Y162.436 E.0188
G1 X183.308 Y162.513 E.00616
G1 X181.305 Y162.513 E.0761
G1 X180.458 Y161.347 E.05477
G1 X180.03 Y160.985 E.02129
G1 X179.603 Y160.752 E.01849
G1 X178.747 Y160.533 E.03354
G1 X178.32 Y160.579 E.01634
G1 X177.892 Y160.897 E.02025
G1 X177.172 Y161.888 E.04655
G1 X177.172 Y159.453 E.09253
G1 X177.465 Y159.421 E.01119
G1 X177.892 Y159.103 E.02025
G1 X178.747 Y157.927 E.05525
G1 X179.175 Y157.564 E.02129
G1 X179.318 Y157.487 E.00616
G1 X181.32 Y157.487 E.07609
G1 X182.168 Y158.653 E.05477
G1 X182.595 Y159.015 E.02129
G1 X183.023 Y159.248 E.01849
G1 X183.828 Y159.454 E.03158
G1 X183.828 Y157.86 E.06056
; WIPE_START
G1 X183.828 Y159.454 E-.60571
G1 X183.435 Y159.353 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.47 Y162.475 Z2.76 F60000
G1 X168.059 Y166.246 Z2.76
G1 Z2.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422504
G1 F12129.381
M204 S8000
G1 X180.386 Y153.919 E.61664
G1 X179.861 Y153.919 E.01856
G1 X167.7 Y166.081 E.60834
G1 X167.175 Y166.081 E.01856
G1 X179.337 Y153.919 E.60834
G1 X178.812 Y153.919 E.01856
G1 X166.65 Y166.081 E.60834
G1 X166.126 Y166.081 E.01856
G1 X178.287 Y153.919 E.60834
G1 X177.762 Y153.919 E.01856
G1 X165.601 Y166.081 E.60834
G1 X165.076 Y166.081 E.01856
G1 X177.238 Y153.919 E.60834
G1 X176.713 Y153.919 E.01856
G1 X164.552 Y166.081 E.60834
G1 X164.027 Y166.081 E.01856
G1 X176.188 Y153.919 E.60834
G1 X175.664 Y153.919 E.01856
G1 X163.502 Y166.081 E.60834
G1 X162.978 Y166.081 E.01856
G1 X175.139 Y153.919 E.60834
G1 X174.614 Y153.919 E.01856
G1 X166.162 Y162.372 E.42283
G1 X166.162 Y161.847 E.01856
G1 X174.09 Y153.919 E.39658
G1 X173.565 Y153.919 E.01856
G1 X166.162 Y161.323 E.37034
G1 X166.162 Y160.798 E.01856
G1 X173.04 Y153.919 E.34409
G1 X172.516 Y153.919 E.01856
G1 X166.162 Y160.273 E.31784
G1 X166.162 Y159.749 E.01856
G1 X171.991 Y153.919 E.2916
G1 X171.466 Y153.919 E.01856
G1 X166.162 Y159.224 E.26535
G1 X166.162 Y158.699 E.01856
G1 X170.942 Y153.919 E.23911
G1 X170.417 Y153.919 E.01856
G1 X166.162 Y158.175 E.21286
G1 X166.162 Y157.65 E.01856
G1 X169.892 Y153.919 E.18662
G1 X169.368 Y153.919 E.01856
G1 X166.073 Y157.214 E.16479
G1 X165.963 Y157.103 E.00552
G1 X165.659 Y157.103 E.01076
G1 X168.843 Y153.919 E.15927
G1 X168.318 Y153.919 E.01856
G1 X165.134 Y157.103 E.15927
G1 X164.61 Y157.103 E.01856
G1 X167.794 Y153.919 E.15927
G1 X167.269 Y153.919 E.01856
G1 X164.085 Y157.103 E.15927
G1 X163.56 Y157.103 E.01856
G1 X166.744 Y153.919 E.15927
G1 X166.22 Y153.919 E.01856
G1 X163.036 Y157.103 E.15927
G1 X162.511 Y157.103 E.01856
G1 X165.695 Y153.919 E.15927
G1 X165.17 Y153.919 E.01856
G1 X161.986 Y157.103 E.15927
G1 X161.462 Y157.103 E.01856
G1 X164.646 Y153.919 E.15927
G1 X164.121 Y153.919 E.01856
G1 X160.937 Y157.103 E.15927
G1 X160.412 Y157.103 E.01856
G1 X163.596 Y153.919 E.15927
G1 X163.072 Y153.919 E.01856
G1 X159.888 Y157.103 E.15927
G1 X159.363 Y157.103 E.01856
G1 X162.547 Y153.919 E.15927
G1 X162.022 Y153.919 E.01856
G1 X149.861 Y166.081 E.60834
G1 X150.386 Y166.081 E.01856
G1 X158.838 Y157.628 E.42282
G1 X158.838 Y158.153 E.01856
G1 X150.91 Y166.081 E.39658
G1 X151.435 Y166.081 E.01856
G1 X158.838 Y158.677 E.37033
G1 X158.838 Y159.202 E.01856
G1 X151.96 Y166.081 E.34409
G1 X152.484 Y166.081 E.01856
G1 X158.838 Y159.727 E.31784
G1 X158.838 Y160.251 E.01856
G1 X153.009 Y166.081 E.2916
G1 X153.534 Y166.081 E.01856
G1 X158.838 Y160.776 E.26535
G1 X158.838 Y161.301 E.01856
G1 X154.058 Y166.081 E.23911
G1 X154.583 Y166.081 E.01856
G1 X158.838 Y161.825 E.21286
G1 X158.838 Y162.35 E.01856
G1 X155.108 Y166.081 E.18661
G1 X155.632 Y166.081 E.01856
G1 X158.927 Y162.786 E.16478
G1 X159.037 Y162.897 E.00552
G1 X159.341 Y162.897 E.01076
G1 X156.157 Y166.081 E.15927
G1 X156.682 Y166.081 E.01856
G1 X159.866 Y162.897 E.15927
G1 X160.39 Y162.897 E.01856
G1 X157.206 Y166.081 E.15927
G1 X157.731 Y166.081 E.01856
G1 X160.915 Y162.897 E.15927
G1 X161.44 Y162.897 E.01856
G1 X158.256 Y166.081 E.15927
G1 X158.78 Y166.081 E.01856
G1 X161.964 Y162.897 E.15927
G1 X162.489 Y162.897 E.01856
G1 X159.305 Y166.081 E.15927
G1 X159.83 Y166.081 E.01856
G1 X163.014 Y162.897 E.15927
G1 X163.538 Y162.897 E.01856
G1 X160.354 Y166.081 E.15927
G1 X160.879 Y166.081 E.01856
G1 X164.063 Y162.897 E.15927
G1 X164.588 Y162.897 E.01856
G1 X161.404 Y166.081 E.15927
G1 X161.928 Y166.081 E.01856
G1 X165.112 Y162.897 E.15927
G1 X165.637 Y162.897 E.01856
M73 P66 R4
G1 X162.287 Y166.247 E.16756
; WIPE_START
G1 X163.701 Y164.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X162.391 Y157.487 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.797 Y157.487 E.06056
G1 X161.645 Y158.653 E.05477
G1 X162.072 Y159.015 E.02129
G1 X162.5 Y159.248 E.01849
G1 X163.355 Y159.467 E.03354
G1 X163.783 Y159.421 E.01634
G1 X164.21 Y159.103 E.02025
G1 X165.065 Y157.927 E.05525
G1 X165.493 Y157.564 E.02129
G1 X165.636 Y157.487 E.00616
G1 X165.778 Y157.487 E.00542
G1 X165.778 Y160.716 E.12268
G1 X165.065 Y160.533 E.02795
G1 X164.638 Y160.579 E.01634
G1 X164.21 Y160.897 E.02025
G1 X163.355 Y162.073 E.05525
G1 X162.928 Y162.436 E.02129
G1 X162.785 Y162.513 E.00616
G1 X160.782 Y162.513 E.0761
G1 X159.935 Y161.347 E.05477
G1 X159.507 Y160.985 E.02129
G1 X159.222 Y160.83 E.01233
G1 X159.222 Y159.236 E.06056
; WIPE_START
G1 X159.222 Y160.83 E-.60571
G1 X159.507 Y160.985 E-.12335
G1 X159.569 Y161.037 E-.03093
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X156.538 Y154.033 Z2.76 F60000
G1 X156.417 Y153.753 Z2.76
G1 Z2.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422504
G1 F12129.381
M204 S8000
G1 X148.112 Y162.059 E.41544
G1 X148.112 Y161.534 E.01856
G1 X155.726 Y153.919 E.3809
G1 X155.202 Y153.919 E.01856
G1 X148.112 Y161.009 E.35465
G1 X148.112 Y160.484 E.01856
G1 X154.677 Y153.919 E.32841
G1 X154.152 Y153.919 E.01856
G1 X148.112 Y159.96 E.30216
G1 X148.112 Y159.435 E.01856
G1 X153.628 Y153.919 E.27592
G1 X153.103 Y153.919 E.01856
G1 X148.112 Y158.91 E.24967
G1 X148.112 Y158.386 E.01856
G1 X152.578 Y153.919 E.22342
G1 X152.054 Y153.919 E.01856
G1 X148.112 Y157.861 E.19718
G1 X148.112 Y157.336 E.01856
G1 X151.529 Y153.919 E.17093
G1 X151.004 Y153.919 E.01856
G1 X147.82 Y157.103 E.15927
G1 X147.296 Y157.103 E.01856
G1 X150.479 Y153.919 E.15927
G1 X149.955 Y153.919 E.01856
G1 X146.771 Y157.103 E.15927
G1 X146.246 Y157.103 E.01856
G1 X149.43 Y153.919 E.15927
G1 X148.905 Y153.919 E.01856
G1 X145.722 Y157.103 E.15927
G1 X145.197 Y157.103 E.01856
G1 X148.381 Y153.919 E.15927
G1 X147.856 Y153.919 E.01856
G1 X144.672 Y157.103 E.15927
G1 X144.147 Y157.103 E.01856
G1 X147.331 Y153.919 E.15927
G1 X146.807 Y153.919 E.01856
G1 X143.623 Y157.103 E.15927
G1 X143.098 Y157.103 E.01856
G1 X146.282 Y153.919 E.15927
G1 X145.757 Y153.919 E.01856
G1 X142.573 Y157.103 E.15927
G1 X142.049 Y157.103 E.01856
G1 X145.233 Y153.919 E.15927
G1 X144.708 Y153.919 E.01856
G1 X141.524 Y157.103 E.15927
G1 X141.087 Y157.103 E.01547
G1 X140.888 Y157.302 E.00993
G1 X140.888 Y157.739 E.01547
G1 X136.419 Y162.208 E.22355
G1 X136.419 Y162.733 E.01856
G1 X140.888 Y158.264 E.22355
G1 X140.888 Y158.788 E.01856
G1 X136.419 Y163.257 E.22355
G1 X136.419 Y163.782 E.01856
G1 X140.888 Y159.313 E.22355
G1 X140.888 Y159.838 E.01856
G1 X136.419 Y164.307 E.22355
G1 X136.419 Y164.831 E.01856
G1 X140.888 Y160.362 E.22355
G1 X140.888 Y160.887 E.01856
G1 X136.419 Y165.356 E.22355
G1 X136.419 Y165.881 E.01856
G1 X140.888 Y161.412 E.22355
G1 X140.888 Y161.936 E.01856
G1 X136.744 Y166.081 E.2073
G1 X137.269 Y166.081 E.01856
G1 X140.888 Y162.461 E.18106
G1 X140.888 Y162.698 E.00838
G1 X141.032 Y162.842 E.00719
G1 X137.793 Y166.081 E.16201
G1 X138.318 Y166.081 E.01856
G1 X141.502 Y162.897 E.15927
G1 X142.027 Y162.897 E.01856
G1 X138.843 Y166.081 E.15927
G1 X139.367 Y166.081 E.01856
G1 X142.551 Y162.897 E.15927
G1 X143.076 Y162.897 E.01856
G1 X139.892 Y166.081 E.15927
G1 X140.417 Y166.081 E.01856
G1 X143.601 Y162.897 E.15927
G1 X144.125 Y162.897 E.01856
G1 X140.941 Y166.081 E.15927
G1 X141.466 Y166.081 E.01856
G1 X144.65 Y162.897 E.15927
G1 X145.175 Y162.897 E.01856
G1 X141.991 Y166.081 E.15927
G1 X142.515 Y166.081 E.01856
G1 X145.699 Y162.897 E.15927
G1 X146.224 Y162.897 E.01856
G1 X143.04 Y166.081 E.15927
G1 X143.565 Y166.081 E.01856
G1 X146.749 Y162.897 E.15927
G1 X147.273 Y162.897 E.01856
G1 X144.09 Y166.081 E.15927
G1 X144.614 Y166.081 E.01856
G1 X156.776 Y153.919 E.60834
G1 X157.3 Y153.919 E.01856
G1 X145.139 Y166.081 E.60834
G1 X145.664 Y166.081 E.01856
G1 X157.825 Y153.919 E.60834
G1 X158.35 Y153.919 E.01856
G1 X146.188 Y166.081 E.60834
G1 X146.713 Y166.081 E.01856
G1 X158.874 Y153.919 E.60834
G1 X159.399 Y153.919 E.01856
G1 X147.238 Y166.081 E.60834
G1 X147.762 Y166.081 E.01856
G1 X159.924 Y153.919 E.60834
G1 X160.448 Y153.919 E.01856
G1 X148.287 Y166.081 E.60834
G1 X148.812 Y166.081 E.01856
G1 X160.973 Y153.919 E.60834
G1 X161.498 Y153.919 E.01856
G1 X149.17 Y166.247 E.61664
; WIPE_START
G1 X150.585 Y164.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X145.506 Y162.513 Z2.76 F60000
G1 Z2.36
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X147.1 Y162.513 E.06056
G1 X146.253 Y161.347 E.05477
G1 X145.825 Y160.985 E.02129
G1 X145.398 Y160.752 E.01849
G1 X144.542 Y160.533 E.03354
G1 X144.115 Y160.579 E.01634
G1 X143.687 Y160.897 E.02025
G1 X142.832 Y162.073 E.05525
G1 X142.405 Y162.436 E.02129
G1 X142.262 Y162.513 E.00616
G1 X141.272 Y162.513 E.03762
G1 X141.272 Y158.78 E.14183
G1 X141.549 Y159.015 E.01382
G1 X141.977 Y159.248 E.01849
G1 X142.832 Y159.467 E.03354
G1 X143.26 Y159.421 E.01634
G1 X143.687 Y159.103 E.02025
G1 X144.542 Y157.927 E.05525
G1 X144.97 Y157.564 E.02129
G1 X145.112 Y157.487 E.00616
G1 X147.115 Y157.487 E.07609
G1 X147.728 Y158.33 E.0396
G1 X147.728 Y159.924 E.06056
; WIPE_START
G1 X147.728 Y158.33 E-.60572
G1 X147.489 Y158.001 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.269 Y160.474 Z2.76 F60000
G1 X136.253 Y161.849 Z2.76
G1 Z2.36
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422504
G1 F12129.381
M204 S8000
G1 X144.183 Y153.919 E.39667
G1 X143.659 Y153.919 E.01856
G1 X136.419 Y161.159 E.36213
G1 X136.419 Y160.634 E.01856
G1 X143.134 Y153.919 E.33589
G1 X142.609 Y153.919 E.01856
G1 X136.419 Y160.109 E.30964
G1 X136.419 Y159.585 E.01856
G1 X142.085 Y153.919 E.2834
G1 X141.56 Y153.919 E.01856
G1 X136.419 Y159.06 E.25715
G1 X136.419 Y158.535 E.01856
G1 X141.035 Y153.919 E.23091
G1 X140.511 Y153.919 E.01856
G1 X136.419 Y158.011 E.20466
G1 X136.419 Y157.486 E.01856
G1 X139.986 Y153.919 E.17842
G1 X139.461 Y153.919 E.01856
G1 X136.419 Y156.961 E.15217
G1 X136.419 Y156.437 E.01856
G1 X138.937 Y153.919 E.12592
G1 X138.412 Y153.919 E.01856
G1 X136.419 Y155.912 E.09968
G1 X136.419 Y155.387 E.01856
G1 X137.887 Y153.919 E.07343
G1 X137.363 Y153.919 E.01856
G1 X136.419 Y154.863 E.04719
G1 X136.419 Y154.338 E.01856
G1 X137.004 Y153.753 E.02924
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12129.381
G1 X136.419 Y154.338 E-.31411
G1 X136.419 Y154.863 E-.19937
G1 X136.878 Y154.404 E-.24652
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 11/44
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z2.76 I-.274 J1.186 P1  F60000
G1 X188.907 Y166.407 Z2.76
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
M73 P67 R4
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
M73 P67 R3
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X188.746 Y162.374 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422494
G1 F12129.707
M204 S8000
G1 X184.212 Y157.839 E.22682
G1 X184.212 Y158.364 E.01856
G1 X188.581 Y162.733 E.21853
G1 X188.581 Y163.257 E.01856
G1 X184.212 Y158.888 E.21853
G1 X184.212 Y159.413 E.01856
G1 X188.581 Y163.782 E.21853
G1 X188.581 Y164.307 E.01856
G1 X184.212 Y159.938 E.21853
G1 X184.212 Y160.462 E.01856
G1 X188.581 Y164.831 E.21853
G1 X188.581 Y165.356 E.01856
G1 X184.212 Y160.987 E.21853
G1 X184.212 Y161.512 E.01856
G1 X188.581 Y165.881 E.21853
G1 X188.581 Y166.081 E.00708
G1 X188.256 Y166.081 E.01148
G1 X184.212 Y162.036 E.20229
G1 X184.212 Y162.561 E.01856
G1 X187.731 Y166.081 E.17605
G1 X187.207 Y166.081 E.01856
G1 X184.018 Y162.892 E.1595
G1 X183.498 Y162.897 E.01839
G1 X186.682 Y166.081 E.15926
G1 X186.157 Y166.081 E.01856
G1 X182.974 Y162.897 E.15926
G1 X182.449 Y162.897 E.01856
G1 X185.633 Y166.081 E.15926
G1 X185.108 Y166.081 E.01856
G1 X181.924 Y162.897 E.15926
G1 X181.4 Y162.897 E.01856
G1 X184.583 Y166.081 E.15926
G1 X184.059 Y166.081 E.01856
G1 X180.875 Y162.897 E.15926
G1 X180.35 Y162.897 E.01856
G1 X183.534 Y166.081 E.15926
G1 X183.009 Y166.081 E.01856
G1 X179.826 Y162.897 E.15926
G1 X179.301 Y162.897 E.01856
G1 X182.485 Y166.081 E.15926
G1 X181.96 Y166.081 E.01856
G1 X178.776 Y162.897 E.15926
G1 X178.252 Y162.897 E.01856
G1 X181.435 Y166.081 E.15926
G1 X180.911 Y166.081 E.01856
G1 X177.561 Y162.731 E.16755
M204 S10000
G1 X176.954 Y162.124 F60000
G1 F12129.707
M204 S8000
G1 X168.75 Y153.919 E.41039
G1 X169.274 Y153.919 E.01856
G1 X176.788 Y161.433 E.37586
G1 X176.788 Y160.909 E.01856
G1 X169.799 Y153.919 E.34961
G1 X170.324 Y153.919 E.01856
G1 X176.788 Y160.384 E.32337
G1 X176.788 Y159.859 E.01856
G1 X170.848 Y153.919 E.29712
G1 X171.373 Y153.919 E.01856
G1 X176.788 Y159.335 E.27088
G1 X176.788 Y158.81 E.01856
G1 X171.898 Y153.919 E.24464
G1 X172.422 Y153.919 E.01856
G1 X176.788 Y158.285 E.21839
G1 X176.788 Y157.761 E.01856
G1 X172.947 Y153.919 E.19215
G1 X173.472 Y153.919 E.01856
G1 X176.821 Y157.269 E.16755
G1 X176.987 Y157.103 E.00829
G1 X177.18 Y157.103 E.00683
G1 X173.996 Y153.919 E.15926
G1 X174.521 Y153.919 E.01856
G1 X177.705 Y157.103 E.15926
G1 X178.229 Y157.103 E.01856
G1 X175.046 Y153.919 E.15926
G1 X175.57 Y153.919 E.01856
G1 X178.754 Y157.103 E.15926
G1 X179.279 Y157.103 E.01856
G1 X176.095 Y153.919 E.15926
G1 X176.619 Y153.919 E.01856
G1 X179.803 Y157.103 E.15926
G1 X180.328 Y157.103 E.01856
G1 X177.144 Y153.919 E.15926
G1 X177.669 Y153.919 E.01856
G1 X180.853 Y157.103 E.15926
G1 X181.377 Y157.103 E.01856
G1 X178.193 Y153.919 E.15926
G1 X178.718 Y153.919 E.01856
G1 X181.902 Y157.103 E.15926
G1 X182.427 Y157.103 E.01856
G1 X179.243 Y153.919 E.15926
G1 X179.767 Y153.919 E.01856
G1 X182.951 Y157.103 E.15926
G1 X183.476 Y157.103 E.01856
G1 X180.292 Y153.919 E.15926
G1 X180.817 Y153.919 E.01856
G1 X188.581 Y161.683 E.38835
G1 X188.581 Y161.159 E.01856
G1 X181.341 Y153.919 E.36211
G1 X181.866 Y153.919 E.01856
G1 X188.581 Y160.634 E.33587
G1 X188.581 Y160.109 E.01856
G1 X182.391 Y153.919 E.30962
G1 X182.915 Y153.919 E.01856
G1 X188.581 Y159.585 E.28338
G1 X188.581 Y159.06 E.01856
G1 X183.44 Y153.919 E.25713
G1 X183.965 Y153.919 E.01856
G1 X188.581 Y158.535 E.23089
G1 X188.581 Y158.011 E.01856
G1 X184.489 Y153.919 E.20465
G1 X185.014 Y153.919 E.01856
G1 X188.581 Y157.486 E.1784
G1 X188.581 Y156.961 E.01856
G1 X185.539 Y153.919 E.15216
G1 X186.063 Y153.919 E.01856
G1 X188.581 Y156.437 E.12591
G1 X188.581 Y155.912 E.01856
G1 X186.588 Y153.919 E.09967
G1 X187.113 Y153.919 E.01856
G1 X188.581 Y155.387 E.07343
G1 X188.581 Y154.863 E.01856
G1 X187.637 Y153.919 E.04718
G1 X188.162 Y153.919 E.01856
G1 X188.746 Y154.504 E.02923
; WIPE_START
G1 X188.162 Y153.919 E-.31406
G1 X187.637 Y153.919 E-.19937
G1 X188.096 Y154.378 E-.24657
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X180.901 Y156.926 Z3 F60000
G1 X177.172 Y158.246 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X177.172 Y159.84 E.06056
G1 X177.508 Y160 E.01414
G1 X177.661 Y160.428 E.01725
G1 X177.561 Y160.855 E.01668
G1 X177.172 Y161.762 E.03749
G1 X177.172 Y162.513 E.02855
G1 X180.96 Y162.513 E.14392
G1 X180.627 Y161.71 E.03303
G1 X180.341 Y161.283 E.01954
G1 X179.9 Y160.855 E.02333
G1 X179.176 Y160.428 E.03196
G1 X178.277 Y160 E.03783
G1 X178.123 Y159.572 E.01725
G1 X178.224 Y159.145 E.01668
G1 X178.578 Y158.29 E.03517
G1 X178.864 Y157.862 E.01954
G1 X179.251 Y157.487 E.02048
G1 X181.666 Y157.487 E.09174
G1 X181.999 Y158.29 E.03303
G1 X182.285 Y158.717 E.01954
G1 X182.725 Y159.145 E.02333
G1 X183.45 Y159.572 E.03196
G1 X183.828 Y159.752 E.01592
G1 X183.828 Y162.038 E.08684
G1 X183.762 Y162.138 E.00456
G1 X183.375 Y162.513 E.02048
G1 X181.781 Y162.513 E.06056
; WIPE_START
G1 X183.375 Y162.513 E-.60572
G1 X183.666 Y162.231 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X180.552 Y166.246 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422494
G1 F12129.707
M204 S8000
G1 X168.225 Y153.919 E.61661
G1 X167.7 Y153.919 E.01856
G1 X179.861 Y166.081 E.60832
G1 X179.337 Y166.081 E.01856
G1 X167.176 Y153.919 E.60832
G1 X166.651 Y153.919 E.01856
G1 X178.812 Y166.081 E.60832
G1 X178.287 Y166.081 E.01856
G1 X166.126 Y153.919 E.60832
G1 X165.602 Y153.919 E.01856
G1 X177.763 Y166.081 E.60832
G1 X177.238 Y166.081 E.01856
G1 X165.077 Y153.919 E.60832
G1 X164.552 Y153.919 E.01856
G1 X176.714 Y166.081 E.60832
G1 X176.189 Y166.081 E.01856
G1 X164.028 Y153.919 E.60832
G1 X163.503 Y153.919 E.01856
G1 X175.664 Y166.081 E.60832
G1 X175.14 Y166.081 E.01856
M73 P68 R3
G1 X162.978 Y153.919 E.60832
G1 X162.454 Y153.919 E.01856
G1 X165.637 Y157.103 E.15926
G1 X165.113 Y157.103 E.01856
G1 X161.929 Y153.919 E.15926
G1 X161.404 Y153.919 E.01856
G1 X164.588 Y157.103 E.15926
G1 X164.063 Y157.103 E.01856
G1 X160.88 Y153.919 E.15926
G1 X160.355 Y153.919 E.01856
G1 X163.539 Y157.103 E.15926
G1 X163.014 Y157.103 E.01856
G1 X159.83 Y153.919 E.15926
G1 X159.306 Y153.919 E.01856
G1 X162.49 Y157.103 E.15926
G1 X161.965 Y157.103 E.01856
G1 X158.781 Y153.919 E.15926
G1 X158.256 Y153.919 E.01856
G1 X161.44 Y157.103 E.15926
G1 X160.916 Y157.103 E.01856
G1 X157.732 Y153.919 E.15926
G1 X157.207 Y153.919 E.01856
G1 X160.391 Y157.103 E.15926
G1 X159.866 Y157.103 E.01856
G1 X156.682 Y153.919 E.15926
G1 X156.158 Y153.919 E.01856
G1 X159.342 Y157.103 E.15926
G1 X159.037 Y157.103 E.01078
G1 X158.927 Y157.213 E.0055
G1 X155.633 Y153.919 E.16475
G1 X155.108 Y153.919 E.01856
G1 X158.838 Y157.649 E.18656
G1 X158.838 Y158.174 E.01856
G1 X154.584 Y153.919 E.21281
G1 X154.059 Y153.919 E.01856
G1 X158.838 Y158.698 E.23905
G1 X158.838 Y159.223 E.01856
G1 X153.534 Y153.919 E.2653
G1 X153.01 Y153.919 E.01856
G1 X158.838 Y159.748 E.29154
G1 X158.838 Y160.272 E.01856
G1 X152.485 Y153.919 E.31778
G1 X151.961 Y153.919 E.01856
G1 X158.838 Y160.797 E.34403
G1 X158.838 Y161.322 E.01856
G1 X151.436 Y153.919 E.37027
G1 X150.911 Y153.919 E.01856
G1 X158.838 Y161.846 E.39652
G1 X158.838 Y162.371 E.01856
G1 X150.387 Y153.919 E.42276
G1 X149.862 Y153.919 E.01856
G1 X162.023 Y166.081 E.60832
G1 X162.548 Y166.081 E.01856
G1 X159.364 Y162.897 E.15926
G1 X159.889 Y162.897 E.01856
G1 X163.072 Y166.081 E.15926
G1 X163.597 Y166.081 E.01856
G1 X160.413 Y162.897 E.15926
G1 X160.938 Y162.897 E.01856
G1 X164.122 Y166.081 E.15926
G1 X164.646 Y166.081 E.01856
G1 X161.463 Y162.897 E.15926
G1 X161.987 Y162.897 E.01856
G1 X165.171 Y166.081 E.15926
G1 X165.696 Y166.081 E.01856
G1 X162.512 Y162.897 E.15926
G1 X163.037 Y162.897 E.01856
G1 X166.22 Y166.081 E.15926
G1 X166.745 Y166.081 E.01856
G1 X163.561 Y162.897 E.15926
G1 X164.086 Y162.897 E.01856
G1 X167.27 Y166.081 E.15926
G1 X167.794 Y166.081 E.01856
G1 X164.611 Y162.897 E.15926
G1 X165.135 Y162.897 E.01856
G1 X168.319 Y166.081 E.15926
G1 X168.844 Y166.081 E.01856
G1 X165.66 Y162.897 E.15926
G1 X165.963 Y162.897 E.01073
G1 X166.074 Y162.786 E.00553
G1 X169.368 Y166.081 E.16479
G1 X169.893 Y166.081 E.01856
G1 X166.162 Y162.349 E.18664
G1 X166.162 Y161.825 E.01856
G1 X170.418 Y166.081 E.21288
G1 X170.942 Y166.081 E.01856
G1 X166.162 Y161.3 E.23912
G1 X166.162 Y160.775 E.01856
G1 X171.467 Y166.081 E.26537
G1 X171.992 Y166.081 E.01856
G1 X166.162 Y160.251 E.29161
G1 X166.162 Y159.726 E.01856
G1 X172.516 Y166.081 E.31786
G1 X173.041 Y166.081 E.01856
G1 X166.162 Y159.202 E.3441
G1 X166.162 Y158.677 E.01856
G1 X173.566 Y166.081 E.37034
G1 X174.09 Y166.081 E.01856
G1 X166.162 Y158.152 E.39659
G1 X166.162 Y157.628 E.01856
G1 X174.781 Y166.246 E.43113
; WIPE_START
G1 X173.366 Y164.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.281 Y161.995 Z3 F60000
G1 X159.222 Y159.169 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.222 Y160.763 E.06056
G1 X159.377 Y160.855 E.00686
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
G1 X165.569 Y157.487 E.16817
G1 X165.182 Y157.862 E.02048
G1 X164.896 Y158.29 E.01954
G1 X164.542 Y159.145 E.03517
G1 X164.441 Y159.572 E.01668
G1 X164.595 Y160 E.01725
G1 X165.494 Y160.428 E.03783
G1 X165.778 Y160.595 E.01255
G1 X165.778 Y162.189 E.06056
; WIPE_START
G1 X165.778 Y160.595 E-.60571
G1 X165.494 Y160.428 E-.12548
G1 X165.425 Y160.395 E-.02881
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.664 Y166.246 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422494
G1 F12129.707
M204 S8000
G1 X149.337 Y153.919 E.61661
G1 X148.813 Y153.919 E.01856
G1 X160.974 Y166.081 E.60832
G1 X160.449 Y166.081 E.01856
G1 X148.288 Y153.919 E.60832
G1 X147.763 Y153.919 E.01856
G1 X159.924 Y166.081 E.60832
G1 X159.4 Y166.081 E.01856
G1 X147.239 Y153.919 E.60832
G1 X146.714 Y153.919 E.01856
G1 X158.875 Y166.081 E.60832
G1 X158.35 Y166.081 E.01856
G1 X146.189 Y153.919 E.60832
G1 X145.665 Y153.919 E.01856
G1 X157.826 Y166.081 E.60832
G1 X157.301 Y166.081 E.01856
G1 X145.14 Y153.919 E.60832
G1 X144.615 Y153.919 E.01856
G1 X156.776 Y166.081 E.60832
G1 X156.252 Y166.081 E.01856
G1 X148.112 Y157.941 E.40717
G1 X148.112 Y158.465 E.01856
G1 X155.727 Y166.081 E.38093
G1 X155.202 Y166.081 E.01856
G1 X148.112 Y158.99 E.35469
G1 X148.112 Y159.515 E.01856
G1 X154.678 Y166.081 E.32844
G1 X154.153 Y166.081 E.01856
G1 X148.112 Y160.039 E.3022
G1 X148.112 Y160.564 E.01856
G1 X153.629 Y166.081 E.27595
G1 X153.104 Y166.081 E.01856
G1 X148.112 Y161.089 E.24971
G1 X148.112 Y161.613 E.01856
G1 X152.579 Y166.081 E.22346
G1 X152.055 Y166.081 E.01856
G1 X148.112 Y162.138 E.19722
G1 X148.112 Y162.662 E.01856
G1 X151.53 Y166.081 E.17098
G1 X151.005 Y166.081 E.01856
G1 X147.821 Y162.897 E.15925
G1 X147.297 Y162.897 E.01856
G1 X150.481 Y166.081 E.15925
G1 X149.956 Y166.081 E.01856
G1 X146.772 Y162.897 E.15925
G1 X146.247 Y162.897 E.01856
G1 X149.431 Y166.081 E.15926
G1 X148.907 Y166.081 E.01856
G1 X145.723 Y162.897 E.15926
G1 X145.198 Y162.897 E.01856
G1 X148.382 Y166.081 E.15926
G1 X147.857 Y166.081 E.01856
G1 X144.674 Y162.897 E.15926
G1 X144.149 Y162.897 E.01856
G1 X147.333 Y166.081 E.15926
G1 X146.808 Y166.081 E.01856
G1 X143.624 Y162.897 E.15926
G1 X143.1 Y162.897 E.01856
G1 X146.283 Y166.081 E.15926
G1 X145.759 Y166.081 E.01856
G1 X142.575 Y162.897 E.15926
G1 X142.05 Y162.897 E.01856
G1 X145.234 Y166.081 E.15926
G1 X144.709 Y166.081 E.01856
G1 X141.526 Y162.897 E.15926
G1 X141.087 Y162.897 E.01552
G1 X140.888 Y162.698 E.00993
G1 X140.888 Y162.259 E.01552
G1 X136.419 Y157.791 E.22353
G1 X136.419 Y157.266 E.01856
G1 X140.888 Y161.735 E.22353
G1 X140.888 Y161.21 E.01856
G1 X136.419 Y156.741 E.22353
G1 X136.419 Y156.217 E.01856
M73 P69 R3
G1 X140.888 Y160.685 E.22353
G1 X140.888 Y160.161 E.01856
G1 X136.419 Y155.692 E.22353
G1 X136.419 Y155.167 E.01856
G1 X140.888 Y159.636 E.22353
G1 X140.888 Y159.111 E.01856
G1 X136.419 Y154.643 E.22353
G1 X136.419 Y154.118 E.01856
G1 X140.888 Y158.587 E.22353
G1 X140.888 Y158.062 E.01856
G1 X136.745 Y153.919 E.20723
G1 X137.27 Y153.919 E.01856
G1 X140.888 Y157.538 E.18098
G1 X140.888 Y157.302 E.00834
G1 X141.033 Y157.157 E.00723
G1 X137.795 Y153.919 E.16196
G1 X138.319 Y153.919 E.01856
G1 X141.503 Y157.103 E.15926
G1 X142.028 Y157.103 E.01856
G1 X138.844 Y153.919 E.15926
G1 X139.369 Y153.919 E.01856
G1 X142.552 Y157.103 E.15926
G1 X143.077 Y157.103 E.01856
G1 X139.893 Y153.919 E.15926
G1 X140.418 Y153.919 E.01856
G1 X143.602 Y157.103 E.15926
G1 X144.126 Y157.103 E.01856
G1 X140.943 Y153.919 E.15926
G1 X141.467 Y153.919 E.01856
G1 X144.651 Y157.103 E.15926
G1 X145.176 Y157.103 E.01856
G1 X141.992 Y153.919 E.15926
G1 X142.517 Y153.919 E.01856
G1 X145.7 Y157.103 E.15926
G1 X146.225 Y157.103 E.01856
G1 X143.041 Y153.919 E.15925
G1 X143.566 Y153.919 E.01856
G1 X146.75 Y157.103 E.15925
G1 X147.274 Y157.103 E.01856
G1 X143.925 Y153.754 E.16755
; WIPE_START
G1 X145.339 Y155.168 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X141.603 Y157.487 Z3 F60000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X141.272 Y157.487 E.01258
G1 X141.272 Y158.75 E.04798
G1 X141.679 Y159.145 E.02157
G1 X142.404 Y159.572 E.03196
G1 X143.303 Y160 E.03783
G1 X143.456 Y160.428 E.01725
G1 X143.356 Y160.855 E.01668
G1 X143.001 Y161.71 E.03517
G1 X142.715 Y162.138 E.01954
G1 X142.329 Y162.513 E.02048
G1 X146.755 Y162.513 E.16817
G1 X146.422 Y161.71 E.03303
G1 X146.136 Y161.283 E.01954
G1 X145.695 Y160.855 E.02333
G1 X144.971 Y160.428 E.03196
G1 X144.072 Y160 E.03783
G1 X143.918 Y159.572 E.01725
G1 X144.019 Y159.145 E.01668
G1 X144.373 Y158.29 E.03517
G1 X144.659 Y157.862 E.01954
G1 X145.046 Y157.487 E.02048
G1 X147.461 Y157.487 E.09174
G1 X147.728 Y158.132 E.02652
G1 X147.728 Y159.726 E.06056
; WIPE_START
G1 X147.728 Y158.132 E-.60572
G1 X147.573 Y157.757 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X144.864 Y164.892 Z3 F60000
G1 X144.35 Y166.246 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422494
G1 F12129.707
M204 S8000
G1 X136.419 Y158.315 E.39672
G1 X136.419 Y158.84 E.01856
G1 X143.66 Y166.081 E.36218
G1 X143.135 Y166.081 E.01856
G1 X136.419 Y159.365 E.33594
G1 X136.419 Y159.889 E.01856
G1 X142.611 Y166.081 E.30969
G1 X142.086 Y166.081 E.01856
G1 X136.419 Y160.414 E.28345
G1 X136.419 Y160.939 E.01856
G1 X141.561 Y166.081 E.25721
G1 X141.037 Y166.081 E.01856
G1 X136.419 Y161.463 E.23096
G1 X136.419 Y161.988 E.01856
G1 X140.512 Y166.081 E.20472
G1 X139.987 Y166.081 E.01856
G1 X136.419 Y162.513 E.17847
G1 X136.419 Y163.037 E.01856
G1 X139.463 Y166.081 E.15223
G1 X138.938 Y166.081 E.01856
G1 X136.419 Y163.562 E.12599
G1 X136.419 Y164.087 E.01856
G1 X138.413 Y166.081 E.09974
G1 X137.889 Y166.081 E.01856
G1 X136.419 Y164.611 E.0735
G1 X136.419 Y165.136 E.01856
G1 X137.364 Y166.081 E.04725
G1 X136.839 Y166.081 E.01856
G1 X136.254 Y165.495 E.0293
; CHANGE_LAYER
; Z_HEIGHT: 2.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12129.707
G1 X136.839 Y166.081 E-.31483
G1 X137.364 Y166.081 E-.19937
G1 X136.907 Y165.623 E-.2458
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 12/44
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3 I-.018 J1.217 P1  F60000
G1 X188.907 Y166.407 Z3
G1 Z2.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X136.093 Y166.407 E2.00651
G1 X136.093 Y153.593 E.4868
G1 X188.907 Y153.593 E2.00651
G1 X188.907 Y166.347 E.48452
; COOLING_NODE: 0
M204 S250
G1 X189.29 Y166.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X187.996 Y166.247 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422504
G1 F12129.381
M204 S8000
G1 X188.581 Y165.662 E.02924
G1 X188.581 Y165.137 E.01856
G1 X187.637 Y166.081 E.04719
G1 X187.113 Y166.081 E.01856
G1 X188.581 Y164.613 E.07343
G1 X188.581 Y164.088 E.01856
G1 X186.588 Y166.081 E.09968
G1 X186.063 Y166.081 E.01856
G1 X188.581 Y163.563 E.12592
G1 X188.581 Y163.039 E.01856
G1 X185.539 Y166.081 E.15217
G1 X185.014 Y166.081 E.01856
G1 X188.581 Y162.514 E.17841
G1 X188.581 Y161.989 E.01856
G1 X184.489 Y166.081 E.20466
G1 X183.965 Y166.081 E.01856
G1 X188.581 Y161.465 E.2309
G1 X188.581 Y160.94 E.01856
G1 X183.44 Y166.081 E.25715
G1 X182.915 Y166.081 E.01856
G1 X188.581 Y160.415 E.28339
G1 X188.581 Y159.891 E.01856
G1 X182.391 Y166.081 E.30964
G1 X181.866 Y166.081 E.01856
G1 X188.581 Y159.366 E.33589
G1 X188.581 Y158.841 E.01856
G1 X181.341 Y166.081 E.36213
G1 X180.817 Y166.081 E.01856
G1 X188.581 Y158.317 E.38838
G1 X188.581 Y157.792 E.01856
G1 X184.212 Y162.161 E.21855
G1 X184.212 Y161.636 E.01856
G1 X188.581 Y157.267 E.21855
G1 X188.581 Y156.743 E.01856
G1 X184.212 Y161.112 E.21855
G1 X184.212 Y160.587 E.01856
G1 X188.581 Y156.218 E.21855
G1 X188.581 Y155.693 E.01856
G1 X184.212 Y160.062 E.21855
G1 X184.212 Y159.538 E.01856
G1 X188.581 Y155.169 E.21855
G1 X188.581 Y154.644 E.01856
G1 X184.212 Y159.013 E.21855
G1 X184.212 Y158.488 E.01856
G1 X188.581 Y154.119 E.21855
G1 X188.581 Y153.919 E.00707
G1 X188.256 Y153.919 E.01149
G1 X184.212 Y157.964 E.2023
G1 X184.212 Y157.439 E.01856
G1 X187.731 Y153.919 E.17606
G1 X187.207 Y153.919 E.01856
G1 X184.018 Y157.108 E.15951
G1 X183.498 Y157.103 E.01839
G1 X186.682 Y153.919 E.15927
G1 X186.157 Y153.919 E.01856
G1 X182.973 Y157.103 E.15927
G1 X182.449 Y157.103 E.01856
G1 X185.633 Y153.919 E.15927
G1 X185.108 Y153.919 E.01856
G1 X181.924 Y157.103 E.15927
G1 X181.399 Y157.103 E.01856
G1 X184.583 Y153.919 E.15927
G1 X184.059 Y153.919 E.01856
G1 X180.875 Y157.103 E.15927
G1 X180.35 Y157.103 E.01856
G1 X183.534 Y153.919 E.15927
G1 X183.009 Y153.919 E.01856
G1 X179.825 Y157.103 E.15927
G1 X179.301 Y157.103 E.01856
G1 X182.485 Y153.919 E.15927
G1 X181.96 Y153.919 E.01856
G1 X178.776 Y157.103 E.15927
G1 X178.251 Y157.103 E.01856
M73 P70 R3
G1 X181.435 Y153.919 E.15927
G1 X180.911 Y153.919 E.01856
G1 X177.561 Y157.269 E.16756
M204 S10000
G1 X176.954 Y157.876 F60000
G1 F12129.381
M204 S8000
G1 X168.749 Y166.081 E.41043
G1 X169.274 Y166.081 E.01856
G1 X176.788 Y158.566 E.37589
G1 X176.788 Y159.091 E.01856
G1 X169.799 Y166.081 E.34965
G1 X170.323 Y166.081 E.01856
G1 X176.788 Y159.616 E.3234
G1 X176.788 Y160.14 E.01856
G1 X170.848 Y166.081 E.29716
G1 X171.373 Y166.081 E.01856
G1 X176.788 Y160.665 E.27091
G1 X176.788 Y161.19 E.01856
G1 X171.897 Y166.081 E.24467
G1 X172.422 Y166.081 E.01856
G1 X176.788 Y161.714 E.21842
G1 X176.788 Y162.239 E.01856
G1 X172.947 Y166.081 E.19217
G1 X173.471 Y166.081 E.01856
G1 X176.821 Y162.731 E.16756
G1 X176.987 Y162.897 E.00829
G1 X177.18 Y162.897 E.00683
G1 X173.996 Y166.081 E.15927
G1 X174.521 Y166.081 E.01856
G1 X177.705 Y162.897 E.15927
G1 X178.229 Y162.897 E.01856
G1 X175.045 Y166.081 E.15927
G1 X175.57 Y166.081 E.01856
G1 X178.754 Y162.897 E.15927
G1 X179.279 Y162.897 E.01856
G1 X176.095 Y166.081 E.15927
G1 X176.619 Y166.081 E.01856
G1 X179.803 Y162.897 E.15927
G1 X180.328 Y162.897 E.01856
G1 X177.144 Y166.081 E.15927
G1 X177.669 Y166.081 E.01856
G1 X180.853 Y162.897 E.15927
G1 X181.377 Y162.897 E.01856
G1 X178.193 Y166.081 E.15927
G1 X178.718 Y166.081 E.01856
G1 X181.902 Y162.897 E.15927
G1 X182.427 Y162.897 E.01856
G1 X179.243 Y166.081 E.15927
G1 X179.767 Y166.081 E.01856
G1 X182.951 Y162.897 E.15927
G1 X183.476 Y162.897 E.01856
G1 X180.126 Y166.247 E.16756
; WIPE_START
G1 X181.54 Y164.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X181.861 Y162.513 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X183.455 Y162.513 E.06056
G1 X183.748 Y162.138 E.01809
G1 X183.828 Y161.976 E.00687
G1 X183.828 Y160.15 E.06937
G1 X183.71 Y160 E.00724
G1 X182.632 Y159.145 E.05229
G1 X182.298 Y158.717 E.02062
G1 X182.087 Y158.29 E.01812
G1 X181.927 Y157.487 E.0311
G1 X179.171 Y157.487 E.10473
G1 X178.878 Y157.862 E.0181
G1 X178.666 Y158.29 E.01812
G1 X178.496 Y159.145 E.03312
G1 X178.579 Y159.572 E.01655
G1 X178.915 Y160 E.02066
G1 X179.993 Y160.855 E.05229
G1 X180.328 Y161.283 E.02061
G1 X180.539 Y161.71 E.01812
G1 X180.698 Y162.513 E.0311
G1 X177.172 Y162.513 E.13397
G1 X177.172 Y161.44 E.04077
G1 X177.288 Y160.855 E.02265
G1 X177.205 Y160.428 E.01655
G1 X177.172 Y160.385 E.00205
G1 X177.172 Y158.791 E.06056
; WIPE_START
G1 X177.172 Y160.385 E-.60571
G1 X177.205 Y160.428 E-.02051
G1 X177.272 Y160.773 E-.13378
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X170.103 Y163.392 Z3.24 F60000
G1 X162.287 Y166.247 Z3.24
G1 Z2.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422504
G1 F12129.381
M204 S8000
G1 X165.637 Y162.897 E.16756
G1 X165.112 Y162.897 E.01856
G1 X161.928 Y166.081 E.15927
G1 X161.404 Y166.081 E.01856
G1 X164.588 Y162.897 E.15927
G1 X164.063 Y162.897 E.01856
G1 X160.879 Y166.081 E.15927
G1 X160.354 Y166.081 E.01856
G1 X163.538 Y162.897 E.15927
G1 X163.014 Y162.897 E.01856
G1 X159.83 Y166.081 E.15927
G1 X159.305 Y166.081 E.01856
G1 X162.489 Y162.897 E.15927
G1 X161.964 Y162.897 E.01856
G1 X158.78 Y166.081 E.15927
G1 X158.256 Y166.081 E.01856
G1 X161.44 Y162.897 E.15927
G1 X160.915 Y162.897 E.01856
G1 X157.731 Y166.081 E.15927
G1 X157.206 Y166.081 E.01856
G1 X160.39 Y162.897 E.15927
G1 X159.866 Y162.897 E.01856
G1 X156.682 Y166.081 E.15927
G1 X156.157 Y166.081 E.01856
G1 X159.341 Y162.897 E.15927
G1 X159.037 Y162.897 E.01076
G1 X158.927 Y162.786 E.00552
G1 X155.632 Y166.081 E.16478
G1 X155.108 Y166.081 E.01856
G1 X158.838 Y162.35 E.18661
G1 X158.838 Y161.825 E.01856
G1 X154.583 Y166.081 E.21286
G1 X154.058 Y166.081 E.01856
G1 X158.838 Y161.301 E.23911
G1 X158.838 Y160.776 E.01856
G1 X153.534 Y166.081 E.26535
G1 X153.009 Y166.081 E.01856
G1 X158.838 Y160.251 E.2916
G1 X158.838 Y159.727 E.01856
G1 X152.484 Y166.081 E.31784
G1 X151.96 Y166.081 E.01856
G1 X158.838 Y159.202 E.34409
G1 X158.838 Y158.677 E.01856
G1 X151.435 Y166.081 E.37033
G1 X150.91 Y166.081 E.01856
G1 X158.838 Y158.153 E.39658
G1 X158.838 Y157.628 E.01856
G1 X150.386 Y166.081 E.42282
G1 X149.861 Y166.081 E.01856
G1 X162.022 Y153.919 E.60834
G1 X162.547 Y153.919 E.01856
G1 X159.363 Y157.103 E.15927
G1 X159.888 Y157.103 E.01856
G1 X163.072 Y153.919 E.15927
G1 X163.596 Y153.919 E.01856
G1 X160.412 Y157.103 E.15927
G1 X160.937 Y157.103 E.01856
G1 X164.121 Y153.919 E.15927
G1 X164.646 Y153.919 E.01856
G1 X161.462 Y157.103 E.15927
G1 X161.986 Y157.103 E.01856
G1 X165.17 Y153.919 E.15927
G1 X165.695 Y153.919 E.01856
G1 X162.511 Y157.103 E.15927
G1 X163.036 Y157.103 E.01856
G1 X166.22 Y153.919 E.15927
G1 X166.744 Y153.919 E.01856
G1 X163.56 Y157.103 E.15927
G1 X164.085 Y157.103 E.01856
G1 X167.269 Y153.919 E.15927
G1 X167.794 Y153.919 E.01856
G1 X164.61 Y157.103 E.15927
G1 X165.134 Y157.103 E.01856
G1 X168.318 Y153.919 E.15927
G1 X168.843 Y153.919 E.01856
G1 X165.659 Y157.103 E.15927
G1 X165.963 Y157.103 E.01076
G1 X166.073 Y157.214 E.00552
G1 X169.368 Y153.919 E.16479
G1 X169.892 Y153.919 E.01856
G1 X166.162 Y157.65 E.18662
G1 X166.162 Y158.175 E.01856
G1 X170.417 Y153.919 E.21286
G1 X170.942 Y153.919 E.01856
G1 X166.162 Y158.699 E.23911
G1 X166.162 Y159.224 E.01856
G1 X171.466 Y153.919 E.26535
G1 X171.991 Y153.919 E.01856
G1 X166.162 Y159.749 E.2916
G1 X166.162 Y160.273 E.01856
G1 X172.516 Y153.919 E.31784
G1 X173.04 Y153.919 E.01856
G1 X166.162 Y160.798 E.34409
G1 X166.162 Y161.323 E.01856
G1 X173.565 Y153.919 E.37034
G1 X174.09 Y153.919 E.01856
G1 X166.162 Y161.847 E.39658
G1 X166.162 Y162.372 E.01856
G1 X174.614 Y153.919 E.42283
G1 X175.139 Y153.919 E.01856
G1 X162.978 Y166.081 E.60834
G1 X163.502 Y166.081 E.01856
G1 X175.664 Y153.919 E.60834
G1 X176.188 Y153.919 E.01856
G1 X164.027 Y166.081 E.60834
G1 X164.552 Y166.081 E.01856
G1 X176.713 Y153.919 E.60834
G1 X177.238 Y153.919 E.01856
G1 X165.076 Y166.081 E.60834
G1 X165.601 Y166.081 E.01856
G1 X177.762 Y153.919 E.60834
G1 X178.287 Y153.919 E.01856
G1 X166.126 Y166.081 E.60834
G1 X166.65 Y166.081 E.01856
G1 X178.812 Y153.919 E.60834
G1 X179.337 Y153.919 E.01856
G1 X167.175 Y166.081 E.60834
G1 X167.7 Y166.081 E.01856
G1 X179.861 Y153.919 E.60834
G1 X180.386 Y153.919 E.01856
G1 X168.059 Y166.246 E.61664
; WIPE_START
G1 X169.473 Y164.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.778 Y162.026 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X165.778 Y160.432 E.06056
M73 P71 R3
G1 X165.233 Y160 E.02642
G1 X164.897 Y159.572 E.02066
G1 X164.814 Y159.145 E.01655
G1 X164.984 Y158.29 E.03312
G1 X165.196 Y157.862 E.01812
G1 X165.489 Y157.487 E.0181
G1 X161.404 Y157.487 E.15518
G1 X161.564 Y158.29 E.0311
G1 X161.775 Y158.717 E.01812
G1 X162.109 Y159.145 E.02062
G1 X163.187 Y160 E.05229
G1 X163.523 Y160.428 E.02066
G1 X163.606 Y160.855 E.01655
G1 X163.436 Y161.71 E.03312
G1 X163.225 Y162.138 E.01812
G1 X162.932 Y162.513 E.01809
G1 X160.175 Y162.513 E.10473
G1 X160.016 Y161.71 E.0311
G1 X159.805 Y161.283 E.01812
G1 X159.47 Y160.855 E.02061
G1 X159.222 Y160.658 E.01205
G1 X159.222 Y159.064 E.06056
; WIPE_START
G1 X159.222 Y160.658 E-.60571
G1 X159.47 Y160.855 E-.12056
G1 X159.525 Y160.925 E-.03373
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X156.49 Y153.922 Z3.24 F60000
G1 X156.417 Y153.753 Z3.24
G1 Z2.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422504
G1 F12129.381
M204 S8000
G1 X148.112 Y162.059 E.41544
G1 X148.112 Y161.534 E.01856
G1 X155.726 Y153.919 E.3809
G1 X155.202 Y153.919 E.01856
G1 X148.112 Y161.009 E.35465
G1 X148.112 Y160.484 E.01856
G1 X154.677 Y153.919 E.32841
G1 X154.152 Y153.919 E.01856
G1 X148.112 Y159.96 E.30216
G1 X148.112 Y159.435 E.01856
G1 X153.628 Y153.919 E.27592
G1 X153.103 Y153.919 E.01856
G1 X148.112 Y158.91 E.24967
G1 X148.112 Y158.386 E.01856
G1 X152.578 Y153.919 E.22342
G1 X152.054 Y153.919 E.01856
G1 X148.112 Y157.861 E.19718
G1 X148.112 Y157.336 E.01856
G1 X151.529 Y153.919 E.17093
G1 X151.004 Y153.919 E.01856
G1 X147.82 Y157.103 E.15927
G1 X147.296 Y157.103 E.01856
G1 X150.479 Y153.919 E.15927
G1 X149.955 Y153.919 E.01856
G1 X146.771 Y157.103 E.15927
G1 X146.246 Y157.103 E.01856
G1 X149.43 Y153.919 E.15927
G1 X148.905 Y153.919 E.01856
G1 X145.722 Y157.103 E.15927
G1 X145.197 Y157.103 E.01856
G1 X148.381 Y153.919 E.15927
G1 X147.856 Y153.919 E.01856
G1 X144.672 Y157.103 E.15927
G1 X144.147 Y157.103 E.01856
G1 X147.331 Y153.919 E.15927
G1 X146.807 Y153.919 E.01856
G1 X143.623 Y157.103 E.15927
G1 X143.098 Y157.103 E.01856
G1 X146.282 Y153.919 E.15927
G1 X145.757 Y153.919 E.01856
G1 X142.573 Y157.103 E.15927
G1 X142.049 Y157.103 E.01856
G1 X145.233 Y153.919 E.15927
G1 X144.708 Y153.919 E.01856
G1 X141.524 Y157.103 E.15927
G1 X141.087 Y157.103 E.01547
G1 X140.888 Y157.302 E.00993
G1 X140.888 Y157.739 E.01547
G1 X136.419 Y162.208 E.22355
G1 X136.419 Y162.733 E.01856
G1 X140.888 Y158.264 E.22355
G1 X140.888 Y158.788 E.01856
G1 X136.419 Y163.257 E.22355
G1 X136.419 Y163.782 E.01856
G1 X140.888 Y159.313 E.22355
G1 X140.888 Y159.838 E.01856
G1 X136.419 Y164.307 E.22355
G1 X136.419 Y164.831 E.01856
G1 X140.888 Y160.362 E.22355
G1 X140.888 Y160.887 E.01856
G1 X136.419 Y165.356 E.22355
G1 X136.419 Y165.881 E.01856
G1 X140.888 Y161.412 E.22355
G1 X140.888 Y161.936 E.01856
G1 X136.744 Y166.081 E.2073
G1 X137.269 Y166.081 E.01856
G1 X140.888 Y162.461 E.18106
G1 X140.888 Y162.698 E.00838
G1 X141.032 Y162.842 E.00719
G1 X137.793 Y166.081 E.16201
G1 X138.318 Y166.081 E.01856
G1 X141.502 Y162.897 E.15927
G1 X142.027 Y162.897 E.01856
G1 X138.843 Y166.081 E.15927
G1 X139.367 Y166.081 E.01856
G1 X142.551 Y162.897 E.15927
G1 X143.076 Y162.897 E.01856
G1 X139.892 Y166.081 E.15927
G1 X140.417 Y166.081 E.01856
G1 X143.601 Y162.897 E.15927
G1 X144.125 Y162.897 E.01856
G1 X140.941 Y166.081 E.15927
G1 X141.466 Y166.081 E.01856
G1 X144.65 Y162.897 E.15927
G1 X145.175 Y162.897 E.01856
G1 X141.991 Y166.081 E.15927
G1 X142.515 Y166.081 E.01856
G1 X145.699 Y162.897 E.15927
G1 X146.224 Y162.897 E.01856
G1 X143.04 Y166.081 E.15927
G1 X143.565 Y166.081 E.01856
G1 X146.749 Y162.897 E.15927
G1 X147.273 Y162.897 E.01856
G1 X144.09 Y166.081 E.15927
G1 X144.614 Y166.081 E.01856
G1 X156.776 Y153.919 E.60834
G1 X157.3 Y153.919 E.01856
G1 X145.139 Y166.081 E.60834
G1 X145.664 Y166.081 E.01856
G1 X157.825 Y153.919 E.60834
G1 X158.35 Y153.919 E.01856
G1 X146.188 Y166.081 E.60834
G1 X146.713 Y166.081 E.01856
G1 X158.874 Y153.919 E.60834
G1 X159.399 Y153.919 E.01856
G1 X147.238 Y166.081 E.60834
G1 X147.762 Y166.081 E.01856
G1 X159.924 Y153.919 E.60834
G1 X160.448 Y153.919 E.01856
G1 X148.287 Y166.081 E.60834
G1 X148.812 Y166.081 E.01856
G1 X160.973 Y153.919 E.60834
G1 X161.498 Y153.919 E.01856
G1 X149.17 Y166.247 E.61664
; WIPE_START
G1 X150.585 Y164.832 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X146.917 Y158.139 Z3.24 F60000
G1 X146.56 Y157.487 Z3.24
G1 Z2.84
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X144.966 Y157.487 E.06056
G1 X144.673 Y157.862 E.0181
G1 X144.461 Y158.29 E.01812
G1 X144.291 Y159.145 E.03312
G1 X144.374 Y159.572 E.01655
G1 X144.71 Y160 E.02066
G1 X145.788 Y160.855 E.05229
G1 X146.123 Y161.283 E.02061
G1 X146.334 Y161.71 E.01812
G1 X146.493 Y162.513 E.0311
G1 X142.409 Y162.513 E.15518
G1 X142.702 Y162.138 E.01809
G1 X142.913 Y161.71 E.01812
G1 X143.083 Y160.855 E.03312
G1 X143 Y160.428 E.01655
G1 X142.664 Y160 E.02066
G1 X141.586 Y159.145 E.05229
G1 X141.272 Y158.743 E.01939
G1 X141.272 Y157.487 E.04771
G1 X141.61 Y157.487 E.01284
; WIPE_START
G1 X141.272 Y157.487 E-.12847
G1 X141.272 Y158.743 E-.47724
G1 X141.522 Y159.063 E-.15429
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X137.004 Y153.753 Z3.24 F60000
G1 Z2.84
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422504
G1 F12129.381
M204 S8000
G1 X136.419 Y154.338 E.02924
G1 X136.419 Y154.863 E.01856
G1 X137.363 Y153.919 E.04719
G1 X137.887 Y153.919 E.01856
G1 X136.419 Y155.387 E.07343
G1 X136.419 Y155.912 E.01856
G1 X138.412 Y153.919 E.09968
G1 X138.937 Y153.919 E.01856
G1 X136.419 Y156.437 E.12592
G1 X136.419 Y156.961 E.01856
G1 X139.461 Y153.919 E.15217
G1 X139.986 Y153.919 E.01856
G1 X136.419 Y157.486 E.17842
G1 X136.419 Y158.011 E.01856
G1 X140.511 Y153.919 E.20466
G1 X141.035 Y153.919 E.01856
G1 X136.419 Y158.535 E.23091
G1 X136.419 Y159.06 E.01856
G1 X141.56 Y153.919 E.25715
G1 X142.085 Y153.919 E.01856
G1 X136.419 Y159.585 E.2834
G1 X136.419 Y160.109 E.01856
G1 X142.609 Y153.919 E.30964
G1 X143.134 Y153.919 E.01856
G1 X136.419 Y160.634 E.33589
G1 X136.419 Y161.159 E.01856
G1 X143.659 Y153.919 E.36213
G1 X144.183 Y153.919 E.01856
G1 X136.253 Y161.849 E.39667
; CHANGE_LAYER
; Z_HEIGHT: 3.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12129.381
G1 X137.668 Y160.435 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 13/44
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 0
M204 S10000
G17
G3 Z3.24 I-.106 J1.212 P1  F60000
G1 X166.197 Y162.932 Z3.24
G1 Z3.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.803 Y162.932 E.28089
G1 X158.803 Y157.068 E.22276
G1 X166.197 Y157.068 E.28089
G1 X166.197 Y162.872 E.22048
; COOLING_NODE: 0
; WIPE_START
G1 X164.197 Y162.888 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X171.829 Y162.905 Z3.48 F60000
G1 X184.247 Y162.932 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X176.753 Y162.932 E.28469
G1 X176.753 Y157.068 E.22276
G1 X184.247 Y157.068 E.28469
G1 X184.247 Y162.872 E.22048
; COOLING_NODE: 0
; WIPE_START
G1 X182.247 Y162.888 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X174.614 Y162.898 Z3.48 F60000
M73 P72 R3
G1 X148.147 Y162.932 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X140.853 Y162.932 E.27709
G1 X140.853 Y157.068 E.22276
G1 X148.147 Y157.068 E.27709
G1 X148.147 Y162.872 E.22048
; COOLING_NODE: 0
; WIPE_START
G1 X146.147 Y162.888 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X153.748 Y163.576 Z3.48 F60000
G1 X189.29 Y166.79 Z3.48
G1 Z3.08
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X135.71 Y166.79 E1.8824
G1 X135.71 Y153.21 E.4771
G1 X189.29 Y153.21 E1.8824
G1 X189.29 Y166.73 E.47499
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
G1 X187.29 Y166.732 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X180.744 Y162.807 Z3.48 F60000
G1 X180.677 Y162.767 Z3.48
G1 Z3.08
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.40821
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X183.88 Y162.134 E.16974
G1 X183.88 Y161.667 E.02428
G1 X179.34 Y162.565 E.24061
G1 X177.12 Y162.565 E.11541
G1 X177.12 Y162.537 E.00145
G1 X183.88 Y161.2 E.35826
G1 X183.88 Y160.733 E.02428
G1 X177.12 Y162.07 E.35826
G1 X177.12 Y161.603 E.02428
G1 X183.88 Y160.265 E.35826
G1 X183.88 Y159.798 E.02428
G1 X177.12 Y161.136 E.35826
G1 X177.12 Y160.669 E.02428
G1 X183.88 Y159.331 E.35826
G1 X183.88 Y158.864 E.02428
G1 X177.12 Y160.202 E.35826
G1 X177.12 Y159.735 E.02428
G1 X183.88 Y158.397 E.35826
G1 X183.88 Y157.93 E.02428
G1 X177.12 Y159.267 E.35826
G1 X177.12 Y158.8 E.02428
G1 X183.88 Y157.463 E.35826
G1 X183.88 Y157.435 E.00145
G1 X181.66 Y157.435 E.11542
G1 X177.12 Y158.333 E.2406
G1 X177.12 Y157.866 E.02428
G1 X180.323 Y157.233 E.16973
M106 S0
; WIPE_START
G1 X178.361 Y157.621 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X185.391 Y154.651 Z3.48 F60000
G1 X188.318 Y153.414 Z3.48
G1 Z3.08
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
; LAYER_HEIGHT: 0.24
G1 F11292.473
M204 S2000
G1 X189.086 Y154.182 E.04124
G1 X189.229 Y154.325
G1 X189.229 Y154.889
G1 X189.086 Y154.745
G1 X187.755 Y153.414 E.07152
G1 X187.611 Y153.271
G1 X187.048 Y153.271
G1 X187.191 Y153.414
G1 X189.086 Y155.309 E.1018
G1 X189.229 Y155.452
G1 X189.229 Y156.016
G1 X189.086 Y155.872
G1 X186.628 Y153.414 E.13208
G1 X186.484 Y153.271
G1 X185.921 Y153.271
G1 X186.064 Y153.414
G1 X189.086 Y156.436 E.16236
G1 X189.229 Y156.579
G1 X189.229 Y157.143
G1 X189.086 Y157
G1 X185.5 Y153.414 E.19264
G1 X185.357 Y153.271
G1 X184.794 Y153.271
G1 X184.937 Y153.414
G1 X189.086 Y157.563 E.22292
G1 X189.229 Y157.706
G1 X189.229 Y158.27
G1 X189.086 Y158.127
G1 X184.373 Y153.414 E.2532
G1 X184.23 Y153.271
G1 X183.667 Y153.271
G1 X183.81 Y153.414
G1 X189.086 Y158.69 E.28348
G1 X189.229 Y158.833
G1 X189.229 Y159.397
G1 X189.086 Y159.254
G1 X183.246 Y153.414 E.31376
G1 X183.103 Y153.271
G1 X182.54 Y153.271
G1 X182.683 Y153.414
G1 X189.086 Y159.817 E.34404
G1 X189.229 Y159.96
G1 X189.229 Y160.524
G1 X189.086 Y160.381
G1 X182.119 Y153.414 E.37432
G1 X181.976 Y153.271
G1 X181.412 Y153.271
G1 X181.556 Y153.414
G1 X189.086 Y160.944 E.4046
G1 X189.229 Y161.088
G1 X189.229 Y161.651
G1 X189.086 Y161.508
G1 X184.522 Y156.945 E.24519
G1 X184.379 Y156.801
G1 X184.379 Y157.365
G1 X184.522 Y157.508
G1 X189.086 Y162.071 E.24519
G1 X189.229 Y162.215
G1 X189.229 Y162.778
G1 X189.086 Y162.635
G1 X184.522 Y158.072 E.24519
G1 X184.379 Y157.928
G1 X184.379 Y158.492
G1 X184.522 Y158.635
G1 X189.086 Y163.199 E.24519
G1 X189.229 Y163.342
G1 X189.229 Y163.905
G1 X189.086 Y163.762
M73 P73 R3
G1 X184.522 Y159.199 E.24519
G1 X184.379 Y159.056
G1 X184.379 Y159.619
G1 X184.522 Y159.762
G1 X189.086 Y164.326 E.24519
G1 X189.229 Y164.469
G1 X189.229 Y165.032
G1 X189.086 Y164.889
G1 X184.522 Y160.326 E.24519
G1 X184.379 Y160.183
G1 X184.379 Y160.746
G1 X184.522 Y160.889
G1 X189.086 Y165.453 E.24519
G1 X189.229 Y165.596
G1 X189.229 Y166.16
G1 X189.086 Y166.016
G1 X184.522 Y161.453 E.24519
G1 X184.379 Y161.31
G1 X184.379 Y161.873
G1 X184.522 Y162.016
G1 X189.086 Y166.58 E.24519
G1 X189.229 Y166.723
G1 X188.671 Y166.729
G1 X188.528 Y166.586
G1 X184.522 Y162.58 E.21523
G1 X184.379 Y162.437
G1 X184.36 Y162.981
G1 X184.503 Y163.124
G1 X187.965 Y166.586 E.18598
G1 X188.108 Y166.729
G1 X187.544 Y166.729
G1 X187.401 Y166.586
G1 X184.023 Y163.207 E.18152
G1 X183.88 Y163.064
G1 X183.316 Y163.064
G1 X183.459 Y163.207
G1 X186.838 Y166.586 E.18152
G1 X186.981 Y166.729
G1 X186.417 Y166.729
G1 X186.274 Y166.586
G1 X182.896 Y163.207 E.18152
G1 X182.752 Y163.064
G1 X182.132 Y163.008
G1 X182.276 Y163.151
G1 X185.71 Y166.586 E.18456
G1 X185.854 Y166.729
G1 X185.29 Y166.729
G1 X185.147 Y166.586
G1 X181.757 Y163.196 E.18214
G1 X181.614 Y163.053
G1 X181.062 Y163.064
G1 X181.205 Y163.207
G1 X184.583 Y166.586 E.18152
G1 X184.727 Y166.729
G1 X184.163 Y166.729
G1 X184.02 Y166.586
G1 X180.585 Y163.151 E.18456
G1 X180.442 Y163.008
G1 X179.878 Y163.008
G1 X180.021 Y163.151
G1 X183.456 Y166.586 E.18456
G1 X183.599 Y166.729
G1 X183.036 Y166.729
G1 X182.893 Y166.586
G1 X179.514 Y163.207 E.18152
G1 X179.371 Y163.064
G1 X178.751 Y163.008
G1 X178.894 Y163.151
G1 X182.329 Y166.586 E.18456
G1 X182.472 Y166.729
G1 X181.909 Y166.729
G1 X181.766 Y166.586
G1 X178.387 Y163.207 E.18152
G1 X178.244 Y163.064
G1 X177.681 Y163.064
G1 X177.824 Y163.207
G1 X181.202 Y166.586 E.18152
G1 X181.345 Y166.729
G1 X180.782 Y166.729
G1 X180.639 Y166.586
G1 X177.26 Y163.207 E.18152
G1 X177.117 Y163.064
G1 X176.553 Y163.064
G1 X176.697 Y163.207
G1 X180.075 Y166.586 E.18152
; WIPE_START
M204 S8000
G1 X178.661 Y165.172 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.959 Y158.864 Z3.48 F60000
G1 X184.37 Y156.793 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S2000
G1 X180.992 Y153.414 E.18152
G1 X180.849 Y153.271
G1 X180.285 Y153.271
G1 X180.429 Y153.414
G1 X183.807 Y156.793 E.18152
G1 X183.95 Y156.936
G1 X183.387 Y156.936
G1 X183.243 Y156.793
G1 X179.865 Y153.414 E.18152
G1 X179.722 Y153.271
G1 X179.158 Y153.271
G1 X179.301 Y153.414
G1 X182.68 Y156.793 E.18152
G1 X182.823 Y156.936
G1 X182.316 Y156.992
G1 X182.173 Y156.849
G1 X178.738 Y153.414 E.18456
G1 X178.595 Y153.271
G1 X178.031 Y153.271
G1 X178.174 Y153.414
G1 X181.553 Y156.793 E.18152
G1 X181.696 Y156.936
G1 X181.189 Y156.992
G1 X181.046 Y156.849
G1 X177.611 Y153.414 E.18456
G1 X177.468 Y153.271
G1 X176.904 Y153.271
G1 X177.047 Y153.414
G1 X180.482 Y156.849 E.18456
G1 X180.625 Y156.992
G1 X180.062 Y156.992
G1 X179.919 Y156.849
G1 X176.484 Y153.414 E.18456
G1 X176.34 Y153.271
G1 X175.777 Y153.271
G1 X175.92 Y153.414
G1 X179.298 Y156.793 E.18152
G1 X179.442 Y156.936
G1 X178.935 Y156.992
G1 X178.791 Y156.849
G1 X175.357 Y153.414 E.18456
G1 X175.213 Y153.271
G1 X174.65 Y153.271
G1 X174.793 Y153.414
G1 X178.171 Y156.793 E.18152
G1 X178.315 Y156.936
G1 X177.751 Y156.936
G1 X177.608 Y156.793
G1 X174.229 Y153.414 E.18152
G1 X174.086 Y153.271
G1 X173.523 Y153.271
G1 X173.666 Y153.414
G1 X177.044 Y156.793 E.18152
G1 X177.187 Y156.936
G1 X176.674 Y156.985
G1 X176.53 Y156.842
G1 X173.102 Y153.414 E.18418
G1 X172.959 Y153.271
G1 X172.396 Y153.271
G1 X172.539 Y153.414
G1 X176.478 Y157.353 E.21163
G1 X176.621 Y157.496
G1 X176.621 Y158.06
G1 X176.478 Y157.916
G1 X171.975 Y153.414 E.24191
G1 X171.832 Y153.271
G1 X171.269 Y153.271
G1 X171.412 Y153.414
G1 X176.478 Y158.48 E.27219
G1 X176.621 Y158.623
G1 X176.621 Y159.187
G1 X176.478 Y159.044
G1 X170.848 Y153.414 E.30247
G1 X170.705 Y153.271
G1 X170.141 Y153.271
G1 X170.285 Y153.414
G1 X176.478 Y159.607 E.33275
G1 X176.621 Y159.75
G1 X176.621 Y160.314
G1 X176.478 Y160.171
G1 X169.721 Y153.414 E.36303
G1 X169.578 Y153.271
G1 X169.014 Y153.271
G1 X169.158 Y153.414
G1 X176.478 Y160.734 E.3933
G1 X176.621 Y160.877
G1 X176.621 Y161.441
G1 X176.478 Y161.298
G1 X168.594 Y153.414 E.42358
G1 X168.451 Y153.271
G1 X167.887 Y153.271
G1 X168.03 Y153.414
G1 X176.478 Y161.861 E.45386
G1 X176.621 Y162.005
G1 X176.621 Y162.568
G1 X176.478 Y162.425
G1 X167.467 Y153.414 E.48414
G1 X167.324 Y153.271
G1 X166.76 Y153.271
G1 X166.903 Y153.414
G1 X176.478 Y162.988 E.51442
; WIPE_START
M204 S8000
G1 X175.063 Y161.574 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.511 Y166.586 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S2000
G1 X166.34 Y153.414 E.70771
G1 X166.197 Y153.271
G1 X165.633 Y153.271
G1 X165.776 Y153.414
G1 X178.948 Y166.586 E.70771
G1 X179.091 Y166.729
G1 X178.528 Y166.729
G1 X178.384 Y166.586
G1 X165.213 Y153.414 E.70771
G1 X165.069 Y153.271
G1 X164.506 Y153.271
G1 X164.649 Y153.414
G1 X177.821 Y166.586 E.70771
G1 X177.964 Y166.729
G1 X177.4 Y166.729
G1 X177.257 Y166.586
G1 X164.086 Y153.414 E.70771
G1 X163.942 Y153.271
G1 X163.379 Y153.271
G1 X163.522 Y153.414
G1 X176.694 Y166.586 E.70771
G1 X176.837 Y166.729
G1 X176.273 Y166.729
G1 X176.13 Y166.586
G1 X166.55 Y157.006 E.51475
G1 X166.407 Y156.862
G1 X166.407 Y157.426
G1 X166.55 Y157.569
G1 X175.567 Y166.586 E.48447
G1 X175.71 Y166.729
G1 X175.146 Y166.729
G1 X175.003 Y166.586
G1 X166.55 Y158.133 E.45419
G1 X166.407 Y157.989
G1 X166.407 Y158.553
G1 X166.55 Y158.696
G1 X174.439 Y166.586 E.42391
G1 X174.583 Y166.729
G1 X174.019 Y166.729
G1 X173.876 Y166.586
G1 X166.55 Y159.26 E.39363
G1 X166.407 Y159.117
G1 X166.407 Y159.68
G1 X166.55 Y159.823
M73 P74 R3
G1 X173.312 Y166.586 E.36335
G1 X173.456 Y166.729
G1 X172.892 Y166.729
G1 X172.749 Y166.586
G1 X166.55 Y160.387 E.33307
G1 X166.407 Y160.244
G1 X166.407 Y160.807
G1 X166.55 Y160.95
G1 X172.185 Y166.586 E.30279
G1 X172.328 Y166.729
G1 X171.765 Y166.729
G1 X171.622 Y166.586
G1 X166.55 Y161.514 E.27251
G1 X166.407 Y161.371
G1 X166.407 Y161.934
G1 X166.55 Y162.077
G1 X171.058 Y166.586 E.24223
G1 X171.201 Y166.729
G1 X170.638 Y166.729
G1 X170.495 Y166.586
G1 X166.55 Y162.641 E.21195
G1 X166.407 Y162.498
G1 X166.407 Y163.061
G1 X166.55 Y163.205
G1 X169.931 Y166.586 E.18167
G1 X170.074 Y166.729
G1 X169.511 Y166.729
G1 X169.368 Y166.586
G1 X166.067 Y163.285 E.17736
G1 X165.923 Y163.142
G1 X165.36 Y163.142
G1 X165.503 Y163.285
G1 X168.804 Y166.586 E.17736
G1 X168.947 Y166.729
G1 X168.384 Y166.729
G1 X168.24 Y166.586
G1 X164.939 Y163.285 E.17736
G1 X164.796 Y163.142
G1 X164.233 Y163.142
G1 X164.376 Y163.285
G1 X167.677 Y166.586 E.17736
G1 X167.82 Y166.729
G1 X167.257 Y166.729
G1 X167.113 Y166.586
G1 X163.812 Y163.285 E.17736
G1 X163.669 Y163.142
G1 X163.106 Y163.142
G1 X163.249 Y163.285
G1 X166.55 Y166.586 E.17736
G1 X166.693 Y166.729
G1 X166.129 Y166.729
G1 X165.986 Y166.586
G1 X162.685 Y163.285 E.17736
G1 X162.542 Y163.142
G1 X161.979 Y163.142
G1 X162.122 Y163.285
G1 X165.423 Y166.586 E.17736
G1 X165.566 Y166.729
G1 X165.002 Y166.729
G1 X164.859 Y166.586
G1 X161.558 Y163.285 E.17736
G1 X161.415 Y163.142
G1 X160.851 Y163.142
G1 X160.995 Y163.285
G1 X164.296 Y166.586 E.17736
G1 X164.439 Y166.729
G1 X163.875 Y166.729
G1 X163.732 Y166.586
G1 X160.431 Y163.285 E.17736
G1 X160.288 Y163.142
G1 X159.724 Y163.142
G1 X159.867 Y163.285
G1 X163.168 Y166.586 E.17736
G1 X163.312 Y166.729
G1 X162.748 Y166.729
G1 X162.605 Y166.586
G1 X159.304 Y163.285 E.17736
G1 X159.161 Y163.142
G1 X158.597 Y163.142
G1 X158.74 Y163.285
G1 X162.041 Y166.586 E.17736
; WIPE_START
M204 S8000
G1 X160.627 Y165.172 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X164.88 Y158.833 Z3.48 F60000
G1 X166.284 Y156.74 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S2000
G1 X162.958 Y153.414 E.17869
G1 X162.815 Y153.271
G1 X162.252 Y153.271
G1 X162.395 Y153.414
G1 X165.721 Y156.74 E.17869
G1 X165.864 Y156.883
G1 X165.3 Y156.883
G1 X165.157 Y156.74
G1 X161.831 Y153.414 E.17869
G1 X161.688 Y153.271
G1 X161.125 Y153.271
G1 X161.268 Y153.414
G1 X164.594 Y156.74 E.17869
G1 X164.737 Y156.883
G1 X164.173 Y156.883
G1 X164.03 Y156.74
G1 X160.704 Y153.414 E.17869
G1 X160.561 Y153.271
G1 X159.998 Y153.271
G1 X160.141 Y153.414
G1 X163.466 Y156.74 E.17869
G1 X163.61 Y156.883
G1 X163.046 Y156.883
G1 X162.903 Y156.74
G1 X159.577 Y153.414 E.17869
G1 X159.434 Y153.271
G1 X158.87 Y153.271
G1 X159.014 Y153.414
G1 X162.339 Y156.74 E.17869
G1 X162.483 Y156.883
G1 X161.919 Y156.883
G1 X161.776 Y156.74
G1 X158.45 Y153.414 E.17869
G1 X158.307 Y153.271
G1 X157.743 Y153.271
G1 X157.887 Y153.414
G1 X161.212 Y156.74 E.17869
G1 X161.355 Y156.883
G1 X160.792 Y156.883
G1 X160.649 Y156.74
G1 X157.323 Y153.414 E.17869
G1 X157.18 Y153.271
G1 X156.616 Y153.271
G1 X156.759 Y153.414
G1 X160.085 Y156.74 E.17869
G1 X160.228 Y156.883
G1 X159.665 Y156.883
G1 X159.522 Y156.74
G1 X156.196 Y153.414 E.17869
G1 X156.053 Y153.271
G1 X155.489 Y153.271
G1 X155.632 Y153.414
G1 X158.958 Y156.74 E.17869
G1 X159.101 Y156.883
G1 X158.593 Y156.939
G1 X158.45 Y156.796
G1 X155.069 Y153.414 E.18168
G1 X154.926 Y153.271
G1 X154.362 Y153.271
G1 X154.505 Y153.414
G1 X158.45 Y157.359 E.21196
G1 X158.593 Y157.502
G1 X158.593 Y158.066
G1 X158.45 Y157.923
G1 X153.942 Y153.414 E.24224
G1 X153.798 Y153.271
G1 X153.235 Y153.271
G1 X153.378 Y153.414
G1 X158.45 Y158.486 E.27252
G1 X158.593 Y158.629
G1 X158.593 Y159.193
G1 X158.45 Y159.05
G1 X152.815 Y153.414 E.3028
G1 X152.671 Y153.271
G1 X152.108 Y153.271
G1 X152.251 Y153.414
G1 X158.45 Y159.613 E.33308
G1 X158.593 Y159.756
G1 X158.593 Y160.32
G1 X158.45 Y160.177
G1 X151.687 Y153.414 E.36336
G1 X151.544 Y153.271
G1 X150.981 Y153.271
G1 X151.124 Y153.414
G1 X158.45 Y160.74 E.39364
G1 X158.593 Y160.884
G1 X158.593 Y161.447
G1 X158.45 Y161.304
G1 X150.56 Y153.414 E.42392
G1 X150.417 Y153.271
G1 X149.854 Y153.271
G1 X149.997 Y153.414
G1 X158.45 Y161.867 E.45419
G1 X158.593 Y162.011
G1 X158.593 Y162.574
G1 X158.45 Y162.431
G1 X149.433 Y153.414 E.48447
G1 X149.29 Y153.271
G1 X148.727 Y153.271
G1 X148.87 Y153.414
G1 X158.45 Y162.995 E.51475
; WIPE_START
M204 S8000
G1 X157.036 Y161.58 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X161.478 Y166.586 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S2000
G1 X148.306 Y153.414 E.70771
G1 X148.163 Y153.271
G1 X147.599 Y153.271
G1 X147.743 Y153.414
G1 X160.914 Y166.586 E.70771
G1 X161.057 Y166.729
G1 X160.494 Y166.729
G1 X160.351 Y166.586
G1 X147.179 Y153.414 E.70771
G1 X147.036 Y153.271
G1 X146.472 Y153.271
G1 X146.616 Y153.414
G1 X159.787 Y166.586 E.70771
G1 X159.93 Y166.729
G1 X159.367 Y166.729
G1 X159.224 Y166.586
G1 X146.052 Y153.414 E.70771
G1 X145.909 Y153.271
G1 X145.345 Y153.271
G1 X145.488 Y153.414
G1 X158.66 Y166.586 E.70771
G1 X158.803 Y166.729
G1 X158.24 Y166.729
G1 X158.097 Y166.586
G1 X148.5 Y156.989 E.51563
G1 X148.357 Y156.846
G1 X148.357 Y157.409
G1 X148.5 Y157.553
G1 X157.533 Y166.586 E.48535
G1 X157.676 Y166.729
G1 X157.113 Y166.729
G1 X156.969 Y166.586
G1 X148.5 Y158.116 E.45507
G1 X148.357 Y157.973
G1 X148.357 Y158.537
G1 X148.5 Y158.68
G1 X156.406 Y166.586 E.42479
G1 X156.549 Y166.729
G1 X155.986 Y166.729
G1 X155.842 Y166.586
G1 X148.5 Y159.243 E.39451
G1 X148.357 Y159.1
G1 X148.357 Y159.664
G1 X148.5 Y159.807
G1 X155.279 Y166.586 E.36423
G1 X155.422 Y166.729
G1 X154.858 Y166.729
G1 X154.715 Y166.586
M73 P75 R3
G1 X148.5 Y160.37 E.33395
G1 X148.357 Y160.227
G1 X148.357 Y160.791
G1 X148.5 Y160.934
G1 X154.152 Y166.586 E.30367
G1 X154.295 Y166.729
G1 X153.731 Y166.729
G1 X153.588 Y166.586
G1 X148.5 Y161.497 E.2734
G1 X148.357 Y161.354
G1 X148.357 Y161.918
G1 X148.5 Y162.061
G1 X153.025 Y166.586 E.24312
G1 X153.168 Y166.729
G1 X152.604 Y166.729
G1 X152.461 Y166.586
G1 X148.5 Y162.625 E.21284
G1 X148.357 Y162.481
G1 X148.357 Y163.045
G1 X148.5 Y163.188
G1 X151.897 Y166.586 E.18256
G1 X152.041 Y166.729
G1 X151.477 Y166.729
G1 X151.334 Y166.586
G1 X148.033 Y163.285 E.17736
G1 X147.89 Y163.142
G1 X147.326 Y163.142
G1 X147.469 Y163.285
G1 X150.77 Y166.586 E.17736
G1 X150.914 Y166.729
G1 X150.35 Y166.729
G1 X150.207 Y166.586
G1 X146.906 Y163.285 E.17736
G1 X146.763 Y163.142
G1 X146.199 Y163.142
G1 X146.342 Y163.285
G1 X149.643 Y166.586 E.17736
G1 X149.786 Y166.729
G1 X149.223 Y166.729
G1 X149.08 Y166.586
G1 X145.779 Y163.285 E.17736
G1 X145.636 Y163.142
G1 X145.072 Y163.142
G1 X145.215 Y163.285
G1 X148.516 Y166.586 E.17736
G1 X148.659 Y166.729
G1 X148.096 Y166.729
G1 X147.953 Y166.586
G1 X144.652 Y163.285 E.17736
G1 X144.508 Y163.142
G1 X143.945 Y163.142
G1 X144.088 Y163.285
G1 X147.389 Y166.586 E.17736
G1 X147.532 Y166.729
G1 X146.969 Y166.729
G1 X146.826 Y166.586
G1 X143.525 Y163.285 E.17736
G1 X143.381 Y163.142
G1 X142.818 Y163.142
G1 X142.961 Y163.285
G1 X146.262 Y166.586 E.17736
G1 X146.405 Y166.729
G1 X145.842 Y166.729
G1 X145.698 Y166.586
G1 X142.397 Y163.285 E.17736
G1 X142.254 Y163.142
G1 X141.691 Y163.142
G1 X141.834 Y163.285
G1 X145.135 Y166.586 E.17736
G1 X145.278 Y166.729
G1 X144.715 Y166.729
G1 X144.571 Y166.586
G1 X141.27 Y163.285 E.17736
G1 X141.127 Y163.142
G1 X140.564 Y163.142
G1 X140.707 Y163.285
G1 X144.008 Y166.586 E.17736
; WIPE_START
M204 S8000
G1 X142.594 Y165.172 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X144.078 Y157.685 Z3.48 F60000
G1 X144.925 Y153.414 Z3.48
G1 Z3.08
G1 E.8 F1800
G1 F11292.473
M204 S2000
G1 X148.251 Y156.74 E.17869
G1 X148.394 Y156.883
G1 X147.83 Y156.883
G1 X147.687 Y156.74
M73 P75 R2
G1 X144.361 Y153.414 E.17869
G1 X144.218 Y153.271
G1 X143.655 Y153.271
G1 X143.798 Y153.414
G1 X147.124 Y156.74 E.17869
G1 X147.267 Y156.883
G1 X146.703 Y156.883
G1 X146.56 Y156.74
G1 X143.234 Y153.414 E.17869
G1 X143.091 Y153.271
G1 X142.527 Y153.271
G1 X142.671 Y153.414
G1 X145.996 Y156.74 E.17869
G1 X146.14 Y156.883
G1 X145.576 Y156.883
G1 X145.433 Y156.74
G1 X142.107 Y153.414 E.17869
G1 X141.964 Y153.271
G1 X141.4 Y153.271
G1 X141.544 Y153.414
G1 X144.869 Y156.74 E.17869
G1 X145.012 Y156.883
G1 X144.449 Y156.883
G1 X144.306 Y156.74
G1 X140.98 Y153.414 E.17869
G1 X140.837 Y153.271
G1 X140.273 Y153.271
G1 X140.416 Y153.414
G1 X143.742 Y156.74 E.17869
G1 X143.885 Y156.883
G1 X143.322 Y156.883
G1 X143.179 Y156.74
G1 X139.853 Y153.414 E.17869
G1 X139.71 Y153.271
G1 X139.146 Y153.271
G1 X139.289 Y153.414
G1 X142.615 Y156.74 E.17869
G1 X142.758 Y156.883
G1 X142.195 Y156.883
G1 X142.052 Y156.74
G1 X138.726 Y153.414 E.17869
G1 X138.583 Y153.271
G1 X138.019 Y153.271
G1 X138.162 Y153.414
G1 X141.488 Y156.74 E.17869
G1 X141.631 Y156.883
G1 X141.068 Y156.883
G1 X140.924 Y156.74
G1 X137.599 Y153.414 E.17869
G1 X137.456 Y153.271
G1 X136.892 Y153.271
G1 X137.035 Y153.414
G1 X140.5 Y156.879 E.18617
G1 X140.643 Y157.022
G1 X140.643 Y157.586
G1 X140.5 Y157.443
G1 X136.472 Y153.414 E.21645
G1 X136.328 Y153.271
G1 X135.771 Y153.277
G1 X135.914 Y153.42
G1 X140.5 Y158.006 E.2464
G1 X140.643 Y158.149
G1 X140.643 Y158.713
G1 X140.5 Y158.57
G1 X135.914 Y153.984 E.2464
G1 X135.771 Y153.841
G1 X135.771 Y154.404
G1 X135.914 Y154.547
G1 X140.5 Y159.133 E.2464
G1 X140.643 Y159.277
G1 X140.643 Y159.84
G1 X140.5 Y159.697
G1 X135.914 Y155.111 E.2464
G1 X135.771 Y154.968
G1 X135.771 Y155.531
G1 X135.914 Y155.674
G1 X140.5 Y160.26 E.2464
G1 X140.643 Y160.404
G1 X140.643 Y160.967
G1 X140.5 Y160.824
G1 X135.914 Y156.238 E.2464
G1 X135.771 Y156.095
G1 X135.771 Y156.658
G1 X135.914 Y156.802
G1 X140.5 Y161.388 E.2464
G1 X140.643 Y161.531
G1 X140.643 Y162.094
G1 X140.5 Y161.951
G1 X135.914 Y157.365 E.2464
G1 X135.771 Y157.222
G1 X135.771 Y157.785
G1 X135.914 Y157.929
G1 X140.5 Y162.515 E.2464
G1 X140.643 Y162.658
G1 X140.643 Y163.221
G1 X140.5 Y163.078
G1 X135.914 Y158.492 E.2464
G1 X135.771 Y158.349
G1 X135.771 Y158.913
G1 X135.914 Y159.056
G1 X143.444 Y166.586 E.40459
G1 X143.587 Y166.729
G1 X143.024 Y166.729
G1 X142.881 Y166.586
G1 X135.914 Y159.619 E.37431
G1 X135.771 Y159.476
G1 X135.771 Y160.04
G1 X135.914 Y160.183
G1 X142.317 Y166.586 E.34403
G1 X142.46 Y166.729
G1 X141.897 Y166.729
G1 X141.754 Y166.586
G1 X135.914 Y160.746 E.31375
G1 X135.771 Y160.603
G1 X135.771 Y161.167
G1 X135.914 Y161.31
G1 X141.19 Y166.586 E.28347
G1 X141.333 Y166.729
G1 X140.77 Y166.729
G1 X140.626 Y166.586
G1 X135.914 Y161.873 E.25319
G1 X135.771 Y161.73
G1 X135.771 Y162.294
G1 X135.914 Y162.437
G1 X140.063 Y166.586 E.22291
G1 X140.206 Y166.729
G1 X139.643 Y166.729
G1 X139.499 Y166.586
G1 X135.914 Y163.001 E.19263
G1 X135.771 Y162.857
G1 X135.771 Y163.421
G1 X135.914 Y163.564
G1 X138.936 Y166.586 E.16235
G1 X139.079 Y166.729
G1 X138.515 Y166.729
G1 X138.372 Y166.586
G1 X135.914 Y164.128 E.13207
G1 X135.771 Y163.985
G1 X135.771 Y164.548
G1 X135.914 Y164.691
G1 X137.809 Y166.586 E.1018
G1 X137.952 Y166.729
G1 X137.388 Y166.729
G1 X137.245 Y166.586
G1 X135.914 Y165.255 E.07152
G1 X135.771 Y165.112
G1 X135.771 Y165.675
G1 X135.914 Y165.818
G1 X136.682 Y166.586 E.04124
; WIPE_START
M204 S8000
G1 X135.914 Y165.818 E-.41244
G1 X135.771 Y165.675 E-.07695
G1 X135.771 Y165.112 E-.21415
G1 X135.876 Y165.217 E-.05646
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X141.194 Y160.188 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Sparse infill
G1 F11292.473
M204 S8000
G1 X141.194 Y158.594 E.06056
G1 X141.235 Y158.717 E.00494
G1 X141.482 Y159.145 E.01877
G1 X142.336 Y160 E.0459
G1 X142.699 Y160.428 E.02132
G1 X142.874 Y160.855 E.01755
G1 X142.859 Y161.71 E.03249
G1 X142.719 Y162.138 E.01709
G1 X142.447 Y162.591 E.02008
G1 X146.284 Y162.591 E.14579
G1 X146.28 Y161.71 E.03345
G1 X146.14 Y161.283 E.01709
G1 X145.892 Y160.855 E.01877
G1 X145.039 Y160 E.0459
G1 X144.675 Y159.572 E.02132
G1 X144.501 Y159.145 E.01755
G1 X144.515 Y158.29 E.03249
G1 X144.655 Y157.862 E.01709
G1 X144.928 Y157.409 E.02009
G1 X146.522 Y157.409 E.06056
; WIPE_START
G1 X144.928 Y157.409 E-.60572
G1 X144.718 Y157.757 E-.15428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.413 Y156.869 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.391504
G1 F13235.295
M204 S8000
G1 X148.408 Y156.832 E.00122
G1 X148.346 Y156.814 E.00208
G1 X140.654 Y156.814 E.24934
G1 X140.592 Y156.832 E.00208
G1 X140.598 Y163.187 E.20599
G1 X148.401 Y163.187 E.25294
G1 X148.413 Y156.929 E.20284
; WIPE_START
G1 X148.409 Y158.929 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.883 Y157.379 Z3.48 F60000
G1 X158.604 Y156.814 Z3.48
G1 Z3.08
G1 E.8 F1800
M73 P76 R2
G1 F13235.295
M204 S8000
G1 X158.542 Y156.832 E.00208
G1 X158.537 Y156.869 E.00121
G1 X158.548 Y163.187 E.20479
G1 X166.452 Y163.187 E.25618
G1 X166.458 Y156.832 E.20599
G1 X166.396 Y156.814 E.00208
G1 X158.664 Y156.814 E.25064
; WIPE_START
G1 X160.664 Y156.814 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.144 Y158.83 Z3.48 F60000
G1 Z3.08
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.144 Y160.424 E.06056
G1 X159.574 Y160.855 E.02313
G1 X159.822 Y161.283 E.01877
G1 X159.962 Y161.71 E.01709
G1 X159.966 Y162.591 E.03345
G1 X162.97 Y162.591 E.11412
G1 X163.242 Y162.138 E.02008
G1 X163.382 Y161.71 E.01709
G1 X163.397 Y160.855 E.03249
G1 X163.222 Y160.428 E.01755
G1 X162.859 Y160 E.02132
G1 X162.005 Y159.145 E.0459
G1 X161.758 Y158.717 E.01877
G1 X161.618 Y158.29 E.01709
G1 X161.614 Y157.409 E.03345
G1 X165.451 Y157.409 E.14579
G1 X165.178 Y157.862 E.02009
G1 X165.038 Y158.29 E.01709
G1 X165.024 Y159.145 E.03249
G1 X165.198 Y159.572 E.01755
G1 X165.562 Y160 E.02132
G1 X165.856 Y160.294 E.0158
G1 X165.856 Y161.888 E.06056
; CHANGE_LAYER
; Z_HEIGHT: 3.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
G1 X165.856 Y160.294 E-.60571
G1 X165.569 Y160.007 E-.15429
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 14/44
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 1
M204 S10000
G17
G3 Z3.48 I-.368 J1.16 P1  F60000
G1 X176.278 Y163.407 Z3.48
G1 Z3.32
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X184.722 Y156.593 E.32077
G1 X184.722 Y163.407 E.25885
G1 X176.338 Y163.407 E.31849
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5828
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X185.105 Y156.21 E.32357
G1 X185.105 Y163.79 E.2663
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

G1 X175.955 Y163.79 E.32146
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.439 Y157.504 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422464
G1 F12130.689
M204 S8000
G1 X177.023 Y156.919 E.02924
G1 X177.548 Y156.919 E.01855
G1 X176.604 Y157.863 E.04719
G1 X176.604 Y158.387 E.01855
G1 X178.072 Y156.919 E.07342
G1 X178.597 Y156.919 E.01855
G1 X176.604 Y158.912 E.09966
G1 X176.604 Y159.437 E.01855
G1 X179.122 Y156.919 E.1259
G1 X179.646 Y156.919 E.01855
G1 X176.604 Y159.961 E.15214
G1 X176.604 Y160.486 E.01855
G1 X180.171 Y156.919 E.17838
G1 X180.695 Y156.919 E.01855
G1 X176.604 Y161.01 E.20462
G1 X176.604 Y161.535 E.01855
G1 X181.22 Y156.919 E.23086
G1 X181.745 Y156.919 E.01855
G1 X176.604 Y162.06 E.2571
G1 X176.604 Y162.584 E.01855
G1 X182.269 Y156.919 E.28334
G1 X182.794 Y156.919 E.01855
G1 X176.633 Y163.081 E.30817
G1 X177.157 Y163.081 E.01855
G1 X183.319 Y156.919 E.30817
G1 X183.843 Y156.919 E.01855
G1 X177.682 Y163.081 E.30817
G1 X178.206 Y163.081 E.01855
G1 X184.368 Y156.919 E.30817
G1 X184.396 Y156.919 E.00099
G1 X184.396 Y157.416 E.01757
G1 X178.731 Y163.081 E.28333
G1 X179.256 Y163.081 E.01855
G1 X184.396 Y157.941 E.25709
G1 X184.396 Y158.465 E.01855
G1 X179.78 Y163.081 E.23085
G1 X180.305 Y163.081 E.01855
G1 X184.396 Y158.99 E.20461
G1 X184.396 Y159.514 E.01855
G1 X180.829 Y163.081 E.17837
G1 X181.354 Y163.081 E.01855
G1 X184.396 Y160.039 E.15213
G1 X184.396 Y160.564 E.01855
G1 X181.879 Y163.081 E.12589
G1 X182.403 Y163.081 E.01855
G1 X184.396 Y161.088 E.09965
G1 X184.396 Y161.613 E.01855
G1 X182.928 Y163.081 E.07341
G1 X183.453 Y163.081 E.01855
G1 X184.396 Y162.138 E.04717
G1 X184.396 Y162.662 E.01855
G1 X183.811 Y163.247 E.02923
; COOLING_NODE: 2
; WIPE_START
G1 X184.396 Y162.662 E-.31404
G1 X184.396 Y162.138 E-.19935
G1 X183.937 Y162.596 E-.24661
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.728 Y160.09 Z3.72 F60000
G1 X166.672 Y156.593 Z3.72
G1 Z3.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X158.328 Y163.407 E.31697
G1 X158.328 Y156.593 E.25885
G1 X166.612 Y156.593 E.3147
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X157.945 Y163.79 E.32006
G1 X157.945 Y156.21 E.2663
G1 X166.995 Y156.21 E.31795
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.455 Y157.13 Z3.72 F60000
G1 X158.493 Y156.992 Z3.72
G1 Z3.32
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.41464
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X166.305 Y156.992 E.41906
G1 X166.305 Y157.457 E.02492
G1 X158.695 Y157.457 E.4082
G1 X158.695 Y157.922 E.02492
G1 X166.305 Y157.922 E.4082
G1 X166.305 Y158.386 E.02492
G1 X158.695 Y158.386 E.4082
G1 X158.695 Y158.851 E.02492
G1 X166.305 Y158.851 E.4082
G1 X166.305 Y159.315 E.02492
G1 X158.695 Y159.315 E.4082
G1 X158.695 Y159.78 E.02492
G1 X166.305 Y159.78 E.4082
G1 X166.305 Y160.245 E.02492
G1 X158.695 Y160.245 E.4082
G1 X158.695 Y160.709 E.02492
G1 X166.305 Y160.709 E.4082
G1 X166.305 Y161.174 E.02492
G1 X158.695 Y161.174 E.4082
G1 X158.695 Y161.639 E.02492
M73 P77 R2
G1 X166.305 Y161.639 E.4082
G1 X166.305 Y162.103 E.02492
G1 X158.695 Y162.103 E.4082
G1 X158.695 Y162.568 E.02492
G1 X166.305 Y162.568 E.4082
G1 X166.305 Y163.033 E.02492
G1 X158.493 Y163.033 E.41906
M106 S0
; COOLING_NODE: 3
; WIPE_START
G1 X160.493 Y163.033 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X152.864 Y163.273 Z3.72 F60000
G1 X148.621 Y163.407 Z3.72
G1 Z3.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
; LAYER_HEIGHT: 0.24
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.31317
G1 X140.378 Y156.593 E.25885
G1 X148.621 Y156.593 E.31317
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.31654
G1 X139.995 Y156.21 E.2663
G1 X149.005 Y156.21 E.31654
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.005 Y163.743 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X140.543 Y163.033 Z3.72 F60000
G1 Z3.32
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.41464
; LAYER_HEIGHT: 0.4
M106 S178.5
G1 F1500
M204 S8000
G1 X148.255 Y163.033 E.4137
G1 X148.255 Y162.568 E.02492
G1 X140.745 Y162.568 E.40283
G1 X140.745 Y162.103 E.02492
G1 X148.255 Y162.103 E.40283
G1 X148.255 Y161.639 E.02492
G1 X140.745 Y161.639 E.40283
G1 X140.745 Y161.174 E.02492
G1 X148.255 Y161.174 E.40283
G1 X148.255 Y160.709 E.02492
G1 X140.745 Y160.709 E.40283
G1 X140.745 Y160.245 E.02492
G1 X148.255 Y160.245 E.40283
G1 X148.255 Y159.78 E.02492
G1 X140.745 Y159.78 E.40283
G1 X140.745 Y159.315 E.02492
G1 X148.255 Y159.315 E.40283
G1 X148.255 Y158.851 E.02492
G1 X140.745 Y158.851 E.40283
G1 X140.745 Y158.386 E.02492
G1 X148.255 Y158.386 E.40283
G1 X148.255 Y157.922 E.02492
G1 X140.745 Y157.922 E.40283
G1 X140.745 Y157.457 E.02492
G1 X148.255 Y157.457 E.40283
G1 X148.255 Y156.992 E.02492
G1 X140.543 Y156.992 E.4137
M106 S0
; CHANGE_LAYER
; Z_HEIGHT: 3.56
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F1500
G1 X142.543 Y156.992 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 15/44
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 1
M204 S10000
G17
M73 P78 R2
G3 Z3.72 I-.227 J1.196 P1  F60000
G1 X176.278 Y163.407 Z3.72
G1 Z3.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X184.722 Y156.593 E.32077
G1 X184.722 Y163.407 E.25885
G1 X176.338 Y163.407 E.31849
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5795
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X185.105 Y156.21 E.32357
G1 X185.105 Y163.79 E.2663
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

G1 X175.955 Y163.79 E.32146
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.189 Y163.247 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422464
G1 F12130.689
M204 S8000
G1 X176.604 Y162.662 E.02924
G1 X176.604 Y162.137 E.01855
G1 X177.548 Y163.081 E.04718
G1 X178.072 Y163.081 E.01855
G1 X176.604 Y161.613 E.07342
G1 X176.604 Y161.088 E.01855
G1 X178.597 Y163.081 E.09966
G1 X179.122 Y163.081 E.01855
G1 X176.604 Y160.563 E.1259
G1 X176.604 Y160.039 E.01855
G1 X179.646 Y163.081 E.15214
G1 X180.171 Y163.081 E.01855
G1 X176.604 Y159.514 E.17838
G1 X176.604 Y158.99 E.01855
G1 X180.695 Y163.081 E.20462
G1 X181.22 Y163.081 E.01855
G1 X176.604 Y158.465 E.23086
G1 X176.604 Y157.94 E.01855
G1 X181.745 Y163.081 E.2571
G1 X182.269 Y163.081 E.01855
G1 X176.604 Y157.416 E.28334
G1 X176.604 Y156.919 E.01756
G1 X176.633 Y156.919 E.001
G1 X182.794 Y163.081 E.30817
G1 X183.319 Y163.081 E.01855
G1 X177.157 Y156.919 E.30817
G1 X177.682 Y156.919 E.01855
G1 X183.843 Y163.081 E.30817
G1 X184.368 Y163.081 E.01855
G1 X178.206 Y156.919 E.30817
G1 X178.731 Y156.919 E.01855
G1 X184.396 Y162.584 E.28333
G1 X184.396 Y162.059 E.01855
G1 X179.256 Y156.919 E.25709
G1 X179.78 Y156.919 E.01855
G1 X184.396 Y161.535 E.23085
G1 X184.396 Y161.01 E.01855
G1 X180.305 Y156.919 E.20461
G1 X180.829 Y156.919 E.01855
G1 X184.396 Y160.486 E.17837
G1 X184.396 Y159.961 E.01855
G1 X181.354 Y156.919 E.15213
G1 X181.879 Y156.919 E.01855
G1 X184.396 Y159.436 E.12589
G1 X184.396 Y158.912 E.01855
G1 X182.403 Y156.919 E.09965
G1 X182.928 Y156.919 E.01855
G1 X184.396 Y158.387 E.07341
G1 X184.396 Y157.862 E.01855
G1 X183.453 Y156.919 E.04717
G1 X183.977 Y156.919 E.01855
G1 X184.562 Y157.504 E.02923
; COOLING_NODE: 2
; WIPE_START
G1 X183.977 Y156.919 E-.31403
G1 X183.453 Y156.919 E-.19935
G1 X183.911 Y157.378 E-.24662
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.287 Y157.031 Z3.96 F60000
G1 X166.672 Y156.593 Z3.96
G1 Z3.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X158.328 Y163.407 E.31697
G1 X158.328 Y156.593 E.25885
G1 X166.612 Y156.593 E.3147
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X157.945 Y163.79 E.32006
G1 X157.945 Y156.21 E.2663
G1 X166.995 Y156.21 E.31795
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.512 Y157.527 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.433594
G1 F11777.33
M204 S8000
G1 X165.904 Y156.919 E.03132
G1 X165.363 Y156.919 E.01968
G1 X166.346 Y157.902 E.05062
G1 X166.346 Y158.442 E.01968
G1 X164.823 Y156.919 E.07845
G1 X164.282 Y156.919 E.01968
G1 X166.346 Y158.983 E.10629
G1 X166.346 Y159.523 E.01968
G1 X163.742 Y156.919 E.13413
G1 X163.202 Y156.919 E.01968
G1 X166.346 Y160.063 E.16197
G1 X166.346 Y160.604 E.01968
G1 X162.661 Y156.919 E.18981
G1 X162.121 Y156.919 E.01968
G1 X166.346 Y161.144 E.21764
G1 X166.346 Y161.684 E.01968
G1 X161.581 Y156.919 E.24548
G1 X161.04 Y156.919 E.01968
G1 X166.346 Y162.225 E.27332
G1 X166.346 Y162.765 E.01968
G1 X160.5 Y156.919 E.30116
G1 X159.96 Y156.919 E.01968
G1 X166.121 Y163.081 E.31742
G1 X165.581 Y163.081 E.01968
G1 X159.419 Y156.919 E.31742
G1 X158.879 Y156.919 E.01968
G1 X165.04 Y163.081 E.31742
G1 X164.5 Y163.081 E.01968
G1 X158.654 Y157.235 E.30115
G1 X158.654 Y157.775 E.01968
G1 X163.96 Y163.081 E.27332
G1 X163.419 Y163.081 E.01968
G1 X158.654 Y158.316 E.24548
G1 X158.654 Y158.856 E.01968
G1 X162.879 Y163.081 E.21764
G1 X162.338 Y163.081 E.01968
G1 X158.654 Y159.396 E.1898
G1 X158.654 Y159.937 E.01968
G1 X161.798 Y163.081 E.16196
G1 X161.258 Y163.081 E.01968
G1 X158.654 Y160.477 E.13413
G1 X158.654 Y161.018 E.01968
G1 X160.717 Y163.081 E.10629
G1 X160.177 Y163.081 E.01968
G1 X158.654 Y161.558 E.07845
G1 X158.654 Y162.098 E.01968
G1 X159.637 Y163.081 E.05061
G1 X159.096 Y163.081 E.01968
G1 X158.488 Y162.473 E.03132
; COOLING_NODE: 3
; WIPE_START
G1 X159.096 Y163.081 E-.32667
G1 X159.637 Y163.081 E-.20534
G1 X159.212 Y162.656 E-.228
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.599 Y163.196 Z3.96 F60000
G1 X148.621 Y163.407 Z3.96
G1 Z3.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.31317
G1 X140.378 Y156.593 E.25885
G1 X148.621 Y156.593 E.31317
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.31654
G1 X139.995 Y156.21 E.2663
G1 X149.005 Y156.21 E.31654
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.005 Y163.743 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.461 Y157.522 Z3.96 F60000
G1 Z3.56
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.430974
G1 F11858.645
M204 S8000
G1 X147.859 Y156.919 E.03082
G1 X147.322 Y156.919 E.01942
G1 X148.296 Y157.893 E.04979
G1 X148.296 Y158.429 E.01942
G1 X146.786 Y156.919 E.07725
G1 X146.249 Y156.919 E.01942
G1 X148.296 Y158.966 E.10471
G1 X148.296 Y159.502 E.01942
G1 X145.712 Y156.919 E.13217
G1 X145.176 Y156.919 E.01942
G1 X148.296 Y160.039 E.15962
G1 X148.296 Y160.576 E.01942
G1 X144.639 Y156.919 E.18708
G1 X144.102 Y156.919 E.01942
G1 X148.296 Y161.112 E.21454
G1 X148.296 Y161.649 E.01942
G1 X143.566 Y156.919 E.242
G1 X143.029 Y156.919 E.01942
G1 X148.296 Y162.186 E.26945
G1 X148.296 Y162.722 E.01942
G1 X142.493 Y156.919 E.29691
G1 X141.956 Y156.919 E.01942
G1 X148.117 Y163.081 E.31524
G1 X147.581 Y163.081 E.01942
G1 X141.419 Y156.919 E.31524
G1 X140.883 Y156.919 E.01942
G1 X147.044 Y163.081 E.31524
G1 X146.507 Y163.081 E.01942
G1 X140.704 Y157.278 E.29691
G1 X140.704 Y157.814 E.01942
G1 X145.971 Y163.081 E.26945
G1 X145.434 Y163.081 E.01942
G1 X140.704 Y158.351 E.24199
G1 X140.704 Y158.888 E.01942
G1 X144.897 Y163.081 E.21454
G1 X144.361 Y163.081 E.01942
M73 P79 R2
G1 X140.704 Y159.424 E.18708
G1 X140.704 Y159.961 E.01942
G1 X143.824 Y163.081 E.15962
G1 X143.287 Y163.081 E.01942
G1 X140.704 Y160.498 E.13216
G1 X140.704 Y161.034 E.01942
G1 X142.751 Y163.081 E.10471
G1 X142.214 Y163.081 E.01942
G1 X140.704 Y161.571 E.07725
G1 X140.704 Y162.108 E.01942
G1 X141.677 Y163.081 E.04979
G1 X141.141 Y163.081 E.01942
G1 X140.538 Y162.478 E.03082
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11858.645
G1 X141.141 Y163.081 E-.32368
G1 X141.677 Y163.081 E-.20393
G1 X141.245 Y162.648 E-.23239
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 16/44
; update layer progress
M73 L16
M991 S0 P15 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 1
M204 S10000
G17
G3 Z3.96 I-.026 J1.217 P1  F60000
G1 X176.278 Y163.407 Z3.96
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X184.722 Y156.593 E.32077
G1 X184.722 Y163.407 E.25885
G1 X176.338 Y163.407 E.31849
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5763
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X185.105 Y156.21 E.32357
G1 X185.105 Y163.79 E.2663
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

G1 X175.955 Y163.79 E.32146
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.439 Y157.504 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422464
G1 F12130.689
M204 S8000
G1 X177.023 Y156.919 E.02924
G1 X177.548 Y156.919 E.01855
G1 X176.604 Y157.863 E.04719
G1 X176.604 Y158.387 E.01855
G1 X178.072 Y156.919 E.07342
G1 X178.597 Y156.919 E.01855
G1 X176.604 Y158.912 E.09966
G1 X176.604 Y159.437 E.01855
G1 X179.122 Y156.919 E.1259
G1 X179.646 Y156.919 E.01855
G1 X176.604 Y159.961 E.15214
G1 X176.604 Y160.486 E.01855
G1 X180.171 Y156.919 E.17838
G1 X180.695 Y156.919 E.01855
G1 X176.604 Y161.01 E.20462
G1 X176.604 Y161.535 E.01855
G1 X181.22 Y156.919 E.23086
G1 X181.745 Y156.919 E.01855
G1 X176.604 Y162.06 E.2571
G1 X176.604 Y162.584 E.01855
G1 X182.269 Y156.919 E.28334
G1 X182.794 Y156.919 E.01855
G1 X176.633 Y163.081 E.30817
G1 X177.157 Y163.081 E.01855
G1 X183.319 Y156.919 E.30817
G1 X183.843 Y156.919 E.01855
G1 X177.682 Y163.081 E.30817
G1 X178.206 Y163.081 E.01855
G1 X184.368 Y156.919 E.30817
G1 X184.396 Y156.919 E.00099
G1 X184.396 Y157.416 E.01757
G1 X178.731 Y163.081 E.28333
G1 X179.256 Y163.081 E.01855
G1 X184.396 Y157.941 E.25709
G1 X184.396 Y158.465 E.01855
G1 X179.78 Y163.081 E.23085
G1 X180.305 Y163.081 E.01855
G1 X184.396 Y158.99 E.20461
G1 X184.396 Y159.514 E.01855
G1 X180.829 Y163.081 E.17837
G1 X181.354 Y163.081 E.01855
G1 X184.396 Y160.039 E.15213
G1 X184.396 Y160.564 E.01855
G1 X181.879 Y163.081 E.12589
G1 X182.403 Y163.081 E.01855
G1 X184.396 Y161.088 E.09965
G1 X184.396 Y161.613 E.01855
G1 X182.928 Y163.081 E.07341
G1 X183.453 Y163.081 E.01855
G1 X184.396 Y162.138 E.04717
G1 X184.396 Y162.662 E.01855
G1 X183.811 Y163.247 E.02923
; COOLING_NODE: 2
; WIPE_START
G1 X184.396 Y162.662 E-.31404
G1 X184.396 Y162.138 E-.19935
G1 X183.937 Y162.596 E-.24661
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.728 Y160.09 Z4.2 F60000
G1 X166.672 Y156.593 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X158.328 Y163.407 E.31697
G1 X158.328 Y156.593 E.25885
G1 X166.612 Y156.593 E.3147
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X157.945 Y163.79 E.32006
G1 X157.945 Y156.21 E.2663
G1 X166.995 Y156.21 E.31795
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.738 Y163.246 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.433594
G1 F11777.33
M204 S8000
G1 X166.346 Y162.639 E.03132
G1 X166.346 Y162.098 E.01968
G1 X165.363 Y163.081 E.05062
G1 X164.823 Y163.081 E.01968
G1 X166.346 Y161.558 E.07845
G1 X166.346 Y161.017 E.01968
G1 X164.282 Y163.081 E.10629
G1 X163.742 Y163.081 E.01968
G1 X166.346 Y160.477 E.13413
G1 X166.346 Y159.937 E.01968
G1 X163.202 Y163.081 E.16197
G1 X162.661 Y163.081 E.01968
G1 X166.346 Y159.396 E.18981
G1 X166.346 Y158.856 E.01968
G1 X162.121 Y163.081 E.21764
G1 X161.581 Y163.081 E.01968
G1 X166.346 Y158.316 E.24548
G1 X166.346 Y157.775 E.01968
G1 X161.04 Y163.081 E.27332
G1 X160.5 Y163.081 E.01968
G1 X166.346 Y157.235 E.30116
G1 X166.346 Y156.919 E.0115
G1 X166.121 Y156.919 E.00819
G1 X159.96 Y163.081 E.31742
G1 X159.419 Y163.081 E.01968
G1 X165.581 Y156.919 E.31742
G1 X165.04 Y156.919 E.01968
G1 X158.879 Y163.081 E.31742
G1 X158.654 Y163.081 E.00818
G1 X158.654 Y162.765 E.0115
G1 X164.5 Y156.919 E.30115
G1 X163.96 Y156.919 E.01968
G1 X158.654 Y162.225 E.27332
G1 X158.654 Y161.684 E.01968
G1 X163.419 Y156.919 E.24548
G1 X162.879 Y156.919 E.01968
G1 X158.654 Y161.144 E.21764
G1 X158.654 Y160.604 E.01968
G1 X162.338 Y156.919 E.1898
G1 X161.798 Y156.919 E.01968
G1 X158.654 Y160.063 E.16196
G1 X158.654 Y159.523 E.01968
G1 X161.258 Y156.919 E.13413
G1 X160.717 Y156.919 E.01968
G1 X158.654 Y158.982 E.10629
G1 X158.654 Y158.442 E.01968
G1 X160.177 Y156.919 E.07845
G1 X159.637 Y156.919 E.01968
G1 X158.654 Y157.902 E.05061
G1 X158.654 Y157.361 E.01968
G1 X159.262 Y156.753 E.03132
; COOLING_NODE: 3
; WIPE_START
G1 X158.654 Y157.361 E-.32667
G1 X158.654 Y157.902 E-.20533
G1 X159.079 Y157.477 E-.228
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X152.439 Y161.242 Z4.2 F60000
G1 X148.621 Y163.407 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.31317
G1 X140.378 Y156.593 E.25885
G1 X148.621 Y156.593 E.31317
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.31654
G1 X139.995 Y156.21 E.2663
G1 X149.005 Y156.21 E.31654
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.005 Y163.743 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.693 Y163.247 Z4.2 F60000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.430974
G1 F11858.645
M204 S8000
G1 X148.296 Y162.644 E.03082
G1 X148.296 Y162.107 E.01942
G1 X147.322 Y163.081 E.0498
G1 X146.786 Y163.081 E.01942
G1 X148.296 Y161.571 E.07725
G1 X148.296 Y161.034 E.01942
G1 X146.249 Y163.081 E.10471
G1 X145.712 Y163.081 E.01942
G1 X148.296 Y160.497 E.13217
G1 X148.296 Y159.961 E.01942
G1 X145.176 Y163.081 E.15963
G1 X144.639 Y163.081 E.01942
G1 X148.296 Y159.424 E.18708
G1 X148.296 Y158.888 E.01942
G1 X144.102 Y163.081 E.21454
G1 X143.566 Y163.081 E.01942
G1 X148.296 Y158.351 E.242
G1 X148.296 Y157.814 E.01942
G1 X143.029 Y163.081 E.26946
G1 X142.493 Y163.081 E.01942
G1 X148.296 Y157.278 E.29691
G1 X148.296 Y156.919 E.01296
G1 X148.117 Y156.919 E.00645
G1 X141.956 Y163.081 E.31524
G1 X141.419 Y163.081 E.01942
M73 P80 R2
G1 X147.581 Y156.919 E.31524
G1 X147.044 Y156.919 E.01942
G1 X140.883 Y163.081 E.31524
G1 X140.704 Y163.081 E.00645
G1 X140.704 Y162.722 E.01297
G1 X146.507 Y156.919 E.29691
G1 X145.971 Y156.919 E.01942
G1 X140.704 Y162.186 E.26945
G1 X140.704 Y161.649 E.01942
G1 X145.434 Y156.919 E.24199
G1 X144.897 Y156.919 E.01942
G1 X140.704 Y161.112 E.21454
G1 X140.704 Y160.576 E.01942
G1 X144.361 Y156.919 E.18708
G1 X143.824 Y156.919 E.01942
G1 X140.704 Y160.039 E.15962
G1 X140.704 Y159.502 E.01942
G1 X143.287 Y156.919 E.13216
G1 X142.751 Y156.919 E.01942
G1 X140.704 Y158.966 E.10471
G1 X140.704 Y158.429 E.01942
G1 X142.214 Y156.919 E.07725
G1 X141.677 Y156.919 E.01942
G1 X140.704 Y157.892 E.04979
G1 X140.704 Y157.356 E.01942
G1 X141.307 Y156.753 E.03082
; CHANGE_LAYER
; Z_HEIGHT: 4.04
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11858.645
G1 X140.704 Y157.356 E-.32369
G1 X140.704 Y157.892 E-.20393
G1 X141.137 Y157.46 E-.23239
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 17/44
; update layer progress
M73 L17
M991 S0 P16 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 1
M204 S10000
G17
G3 Z4.2 I-.203 J1.2 P1  F60000
G1 X176.278 Y163.407 Z4.2
G1 Z4.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X178.95 Y156.593 E.1015
G1 X178.95 Y163.407 E.25885
G1 X176.338 Y163.407 E.09922
; COOLING_NODE: 1
; WIPE_START
G1 X176.321 Y161.407 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.05 Y163.407 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X182.05 Y156.593 E.25885
G1 X184.722 Y156.593 E.1015
G1 X184.722 Y163.407 E.25885
G1 X182.11 Y163.407 E.09922
; COOLING_NODE: 1
; WIPE_START
G1 X182.092 Y161.407 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X175.895 Y163.79 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5723
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X185.105 Y156.21 E.32357
G1 X185.105 Y163.79 E.2663
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

G1 X175.955 Y163.79 E.32146
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.415 Y162.271 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.451074
G1 F11262.107
M204 S8000
G1 X177.814 Y162.271 E.01522
G1 X177.814 Y157.729 E.17299
G1 X177.415 Y157.729 E.01522
G1 X177.415 Y162.211 E.17071
M204 S10000
G1 X177.03 Y162.655 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X178.198 Y162.655 E.04102
G1 X178.198 Y157.345 E.18652
G1 X177.03 Y157.345 E.04102
G1 X177.03 Y162.595 E.18441
M204 S10000
G1 X176.662 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X178.567 Y163.023 E.06691
G1 X178.567 Y156.977 E.21241
G1 X176.662 Y156.977 E.06691
G1 X176.662 Y162.963 E.2103
; WIPE_START
G1 X176.662 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.186 Y162.271 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; LINE_WIDTH: 0.451074
G1 F11262.107
M204 S8000
G1 X183.586 Y162.271 E.01522
G1 X183.586 Y157.729 E.17299
G1 X183.186 Y157.729 E.01522
G1 X183.186 Y162.211 E.17071
M204 S10000
G1 X182.802 Y162.655 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X183.97 Y162.655 E.04102
G1 X183.97 Y157.345 E.18652
G1 X182.802 Y157.345 E.04102
G1 X182.802 Y162.595 E.18441
M204 S10000
G1 X182.433 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X184.338 Y163.023 E.06691
G1 X184.338 Y156.977 E.21241
G1 X182.433 Y156.977 E.06691
G1 X182.433 Y162.963 E.2103
; WIPE_START
G1 X182.433 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X181.174 Y156.414 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X181.831 Y157.07 E.03526
G1 X181.974 Y157.214
G1 X181.974 Y157.777
G1 X181.831 Y157.634
G1 X180.611 Y156.414 E.06554
G1 X180.468 Y156.271
G1 X179.904 Y156.271
G1 X180.047 Y156.414
G1 X181.831 Y158.198 E.09582
G1 X181.974 Y158.341
G1 X181.974 Y158.904
G1 X181.831 Y158.761
G1 X179.484 Y156.414 E.1261
G1 X179.34 Y156.271
G1 X179.026 Y156.52
G1 X179.169 Y156.663
G1 X181.831 Y159.325 E.14299
G1 X181.974 Y159.468
G1 X181.974 Y160.031
G1 X181.831 Y159.888
G1 X179.169 Y157.227 E.14299
G1 X179.026 Y157.084
G1 X179.026 Y157.647
G1 X179.169 Y157.79
G1 X181.831 Y160.452 E.14299
G1 X181.974 Y160.595
G1 X181.974 Y161.159
G1 X181.831 Y161.015
G1 X179.169 Y158.354 E.14299
G1 X179.026 Y158.211
G1 X179.026 Y158.774
G1 X179.169 Y158.918
G1 X181.831 Y161.579 E.14299
G1 X181.974 Y161.722
G1 X181.974 Y162.286
G1 X181.831 Y162.142
G1 X179.169 Y159.481 E.14299
G1 X179.026 Y159.338
G1 X179.026 Y159.902
G1 X179.169 Y160.045
G1 X181.831 Y162.706 E.14299
G1 X181.974 Y162.849
G1 X181.974 Y163.413
G1 X181.831 Y163.27
G1 X179.169 Y160.608 E.14299
G1 X179.026 Y160.465
G1 X179.026 Y161.029
G1 X179.169 Y161.172
G1 X181.583 Y163.586 E.12971
G1 X181.727 Y163.729
G1 X181.163 Y163.729
G1 X181.02 Y163.586
G1 X179.169 Y161.735 E.09943
G1 X179.026 Y161.592
G1 X179.026 Y162.156
G1 X179.169 Y162.299
G1 X180.456 Y163.586 E.06915
G1 X180.599 Y163.729
G1 X180.036 Y163.729
G1 X179.893 Y163.586
G1 X179.169 Y162.862 E.03887
; COOLING_NODE: 2
; WIPE_START
M204 S8000
G1 X179.893 Y163.586 E-.38875
G1 X180.036 Y163.729 E-.07695
G1 X180.599 Y163.729 E-.21415
G1 X180.456 Y163.586 E-.07695
G1 X180.45 Y163.58 E-.00322
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.643 Y160.128 Z4.44 F60000
G1 X166.672 Y156.593 Z4.44
G1 Z4.04
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X158.328 Y163.407 E.31697
G1 X158.328 Y156.593 E.25885
G1 X166.612 Y156.593 E.3147
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X157.945 Y163.79 E.32006
G1 X157.945 Y156.21 E.2663
G1 X166.995 Y156.21 E.31795
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.512 Y157.527 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.433594
G1 F11777.33
M204 S8000
G1 X165.904 Y156.919 E.03132
G1 X165.363 Y156.919 E.01968
G1 X166.346 Y157.902 E.05062
G1 X166.346 Y158.442 E.01968
G1 X164.823 Y156.919 E.07845
G1 X164.282 Y156.919 E.01968
G1 X166.346 Y158.983 E.10629
G1 X166.346 Y159.523 E.01968
G1 X163.742 Y156.919 E.13413
G1 X163.202 Y156.919 E.01968
G1 X166.346 Y160.063 E.16197
G1 X166.346 Y160.604 E.01968
G1 X162.661 Y156.919 E.18981
G1 X162.121 Y156.919 E.01968
G1 X166.346 Y161.144 E.21764
G1 X166.346 Y161.684 E.01968
G1 X161.581 Y156.919 E.24548
G1 X161.04 Y156.919 E.01968
G1 X166.346 Y162.225 E.27332
G1 X166.346 Y162.765 E.01968
G1 X160.5 Y156.919 E.30116
G1 X159.96 Y156.919 E.01968
G1 X166.121 Y163.081 E.31742
G1 X165.581 Y163.081 E.01968
G1 X159.419 Y156.919 E.31742
G1 X158.879 Y156.919 E.01968
G1 X165.04 Y163.081 E.31742
G1 X164.5 Y163.081 E.01968
G1 X158.654 Y157.235 E.30115
G1 X158.654 Y157.775 E.01968
G1 X163.96 Y163.081 E.27332
G1 X163.419 Y163.081 E.01968
G1 X158.654 Y158.316 E.24548
G1 X158.654 Y158.856 E.01968
G1 X162.879 Y163.081 E.21764
G1 X162.338 Y163.081 E.01968
G1 X158.654 Y159.396 E.1898
G1 X158.654 Y159.937 E.01968
G1 X161.798 Y163.081 E.16196
G1 X161.258 Y163.081 E.01968
G1 X158.654 Y160.477 E.13413
G1 X158.654 Y161.018 E.01968
G1 X160.717 Y163.081 E.10629
G1 X160.177 Y163.081 E.01968
M73 P81 R2
G1 X158.654 Y161.558 E.07845
G1 X158.654 Y162.098 E.01968
G1 X159.637 Y163.081 E.05061
G1 X159.096 Y163.081 E.01968
G1 X158.488 Y162.473 E.03132
; COOLING_NODE: 3
; WIPE_START
G1 X159.096 Y163.081 E-.32667
G1 X159.637 Y163.081 E-.20534
G1 X159.212 Y162.656 E-.228
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.599 Y163.196 Z4.44 F60000
G1 X148.621 Y163.407 Z4.44
G1 Z4.04
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.31317
G1 X140.378 Y156.593 E.25885
G1 X148.621 Y156.593 E.31317
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.31654
G1 X139.995 Y156.21 E.2663
G1 X149.005 Y156.21 E.31654
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.005 Y163.743 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.461 Y157.522 Z4.44 F60000
G1 Z4.04
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.430974
G1 F11858.645
M204 S8000
G1 X147.859 Y156.919 E.03082
G1 X147.322 Y156.919 E.01942
G1 X148.296 Y157.893 E.04979
G1 X148.296 Y158.429 E.01942
G1 X146.786 Y156.919 E.07725
G1 X146.249 Y156.919 E.01942
G1 X148.296 Y158.966 E.10471
G1 X148.296 Y159.502 E.01942
G1 X145.712 Y156.919 E.13217
G1 X145.176 Y156.919 E.01942
G1 X148.296 Y160.039 E.15962
G1 X148.296 Y160.576 E.01942
G1 X144.639 Y156.919 E.18708
G1 X144.102 Y156.919 E.01942
G1 X148.296 Y161.112 E.21454
G1 X148.296 Y161.649 E.01942
G1 X143.566 Y156.919 E.242
G1 X143.029 Y156.919 E.01942
G1 X148.296 Y162.186 E.26945
G1 X148.296 Y162.722 E.01942
G1 X142.493 Y156.919 E.29691
G1 X141.956 Y156.919 E.01942
G1 X148.117 Y163.081 E.31524
G1 X147.581 Y163.081 E.01942
G1 X141.419 Y156.919 E.31524
G1 X140.883 Y156.919 E.01942
G1 X147.044 Y163.081 E.31524
G1 X146.507 Y163.081 E.01942
G1 X140.704 Y157.278 E.29691
G1 X140.704 Y157.814 E.01942
G1 X145.971 Y163.081 E.26945
G1 X145.434 Y163.081 E.01942
G1 X140.704 Y158.351 E.24199
G1 X140.704 Y158.888 E.01942
G1 X144.897 Y163.081 E.21454
G1 X144.361 Y163.081 E.01942
G1 X140.704 Y159.424 E.18708
G1 X140.704 Y159.961 E.01942
G1 X143.824 Y163.081 E.15962
G1 X143.287 Y163.081 E.01942
G1 X140.704 Y160.498 E.13216
G1 X140.704 Y161.034 E.01942
G1 X142.751 Y163.081 E.10471
G1 X142.214 Y163.081 E.01942
G1 X140.704 Y161.571 E.07725
G1 X140.704 Y162.108 E.01942
G1 X141.677 Y163.081 E.04979
G1 X141.141 Y163.081 E.01942
G1 X140.538 Y162.478 E.03082
; CHANGE_LAYER
; Z_HEIGHT: 4.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11858.645
G1 X141.141 Y163.081 E-.32368
G1 X141.677 Y163.081 E-.20393
G1 X141.245 Y162.648 E-.23239
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 18/44
; update layer progress
M73 L18
M991 S0 P17 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z4.44 I-.124 J1.211 P1  F60000
G1 X148.621 Y163.407 Z4.44
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.623 Y163.407 E.07592
G1 X146.623 Y156.593 E.25885
G1 X148.621 Y156.593 E.07592
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
; WIPE_START
G1 X146.623 Y163.407 E-.75972
G1 X146.623 Y163.406 E-.00028
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X142.377 Y163.407 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.07592
G1 X140.378 Y156.593 E.25885
G1 X142.377 Y156.593 E.07592
G1 X142.377 Y163.347 E.25657
; COOLING_NODE: 3
; WIPE_START
G1 X140.378 Y163.407 E-.75973
G1 X140.378 Y163.406 E-.00027
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.003 Y163.745 Z4.68 F60000
G1 X149.005 Y163.79 Z4.68
G1 Z4.28
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.31654
G1 X139.995 Y156.21 E.2663
G1 X149.005 Y156.21 E.31654
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.005 Y163.743 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X145.671 Y163.586 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X146.404 Y162.853 E.03939
G1 X146.547 Y162.709
G1 X146.547 Y162.146
G1 X146.404 Y162.289
G1 X145.107 Y163.586 E.06967
G1 X144.964 Y163.729
G1 X144.4 Y163.729
G1 X144.544 Y163.586
G1 X146.404 Y161.726 E.09995
G1 X146.547 Y161.582
G1 X146.547 Y161.019
G1 X146.404 Y161.162
G1 X143.98 Y163.586 E.13023
G1 X143.837 Y163.729
G1 X143.273 Y163.729
G1 X143.416 Y163.586
G1 X146.404 Y160.598 E.16051
G1 X146.547 Y160.455
G1 X146.547 Y159.892
G1 X146.404 Y160.035
G1 X142.853 Y163.586 E.19079
G1 X142.71 Y163.729
G1 X142.453 Y163.422
G1 X142.596 Y163.279
G1 X146.404 Y159.471 E.20459
G1 X146.547 Y159.328
G1 X146.547 Y158.765
G1 X146.404 Y158.908
G1 X142.596 Y162.716 E.20459
G1 X142.453 Y162.859
G1 X142.453 Y162.295
G1 X142.596 Y162.152
G1 X146.404 Y158.344 E.20459
G1 X146.547 Y158.201
G1 X146.547 Y157.638
G1 X146.404 Y157.781
G1 X142.596 Y161.588 E.20459
G1 X142.453 Y161.732
G1 X142.453 Y161.168
G1 X142.596 Y161.025
G1 X146.404 Y157.217 E.20459
G1 X146.547 Y157.074
G1 X146.547 Y156.51
G1 X146.404 Y156.654
G1 X142.596 Y160.461 E.20459
G1 X142.453 Y160.605
G1 X142.453 Y160.041
G1 X142.596 Y159.898
G1 X146.08 Y156.414 E.18717
G1 X146.223 Y156.271
G1 X145.659 Y156.271
G1 X145.516 Y156.414
G1 X142.596 Y159.334 E.15689
G1 X142.453 Y159.477
G1 X142.453 Y158.914
G1 X142.596 Y158.771
G1 X144.953 Y156.414 E.12661
G1 X145.096 Y156.271
G1 X144.532 Y156.271
G1 X144.389 Y156.414
G1 X142.596 Y158.207 E.09633
G1 X142.453 Y158.35
G1 X142.453 Y157.787
G1 X142.596 Y157.644
G1 X143.826 Y156.414 E.06606
G1 X143.969 Y156.271
G1 X143.405 Y156.271
G1 X143.262 Y156.414
G1 X142.596 Y157.08 E.03578
M204 S10000
G1 X141.993 Y157.593 F60000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X141.993 Y156.977 E.02163
G1 X140.762 Y156.977 E.04326
G1 X140.762 Y163.023 E.21241
G1 X141.993 Y163.023 E.04326
G1 X141.993 Y157.653 E.18867
M204 S10000
G1 X141.593 Y157.593 F60000
; LINE_WIDTH: 0.482964
G1 F10429.704
M204 S8000
G1 X141.593 Y157.377 E.00887
G1 X141.162 Y157.377 E.01775
G1 X141.162 Y162.623 E.2158
G1 X141.593 Y162.623 E.01775
G1 X141.593 Y157.653 E.20446
; WIPE_START
G1 X141.593 Y159.653 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.238 Y157.593 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X148.238 Y156.977 E.02163
G1 X147.007 Y156.977 E.04326
G1 X147.007 Y163.023 E.21241
G1 X148.238 Y163.023 E.04326
G1 X148.238 Y157.653 E.18867
M204 S10000
G1 X147.838 Y157.593 F60000
; LINE_WIDTH: 0.482954
G1 F10429.947
M204 S8000
G1 X147.838 Y157.377 E.00887
G1 X147.407 Y157.377 E.01775
G1 X147.407 Y162.623 E.2158
G1 X147.838 Y162.623 E.01775
G1 X147.838 Y157.653 E.20446
; COOLING_NODE: 2
; WIPE_START
G1 X147.838 Y159.653 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.248 Y157.823 Z4.68 F60000
G1 X160.23 Y156.593 Z4.68
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.23 Y163.407 E.25885
G1 X158.328 Y163.407 E.07226
G1 X158.328 Y156.593 E.25885
G1 X160.17 Y156.593 E.06998
; COOLING_NODE: 2
; WIPE_START
G1 X160.188 Y158.593 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.672 Y156.593 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X164.77 Y163.407 E.07226
G1 X164.77 Y156.593 E.25885
G1 X166.612 Y156.593 E.06998
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X157.945 Y163.79 E.32006
G1 X157.945 Y156.21 E.2663
G1 X166.995 Y156.21 E.31795
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
M73 P82 R2
G1 E-.04 F1800
M204 S10000
G1 X165.153 Y163.023 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.288 Y163.023 E.03987
G1 X166.288 Y156.977 E.21241
G1 X165.153 Y156.977 E.03987
G1 X165.153 Y162.963 E.2103
M204 S10000
G1 X165.529 Y162.647 F60000
; LINE_WIDTH: 0.434694
G1 F11743.522
M204 S8000
G1 X165.912 Y162.647 E.014
G1 X165.912 Y157.353 E.19342
G1 X165.529 Y157.353 E.014
G1 X165.529 Y162.587 E.19123
; WIPE_START
G1 X165.529 Y160.587 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X163.704 Y163.586 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X164.55 Y162.74 E.04546
G1 X164.694 Y162.597
G1 X164.694 Y162.033
G1 X164.55 Y162.176
G1 X163.141 Y163.586 E.07574
G1 X162.998 Y163.729
G1 X162.434 Y163.729
G1 X162.577 Y163.586
G1 X164.55 Y161.613 E.10602
G1 X164.694 Y161.469
G1 X164.694 Y160.906
G1 X164.55 Y161.049
G1 X162.014 Y163.586 E.1363
G1 X161.87 Y163.729
G1 X161.307 Y163.729
G1 X161.45 Y163.586
G1 X164.55 Y160.486 E.16658
G1 X164.694 Y160.342
G1 X164.694 Y159.779
G1 X164.55 Y159.922
G1 X160.887 Y163.586 E.19686
G1 X160.743 Y163.729
G1 X160.306 Y163.602
G1 X160.45 Y163.459
G1 X164.55 Y159.358 E.22033
G1 X164.694 Y159.215
G1 X164.694 Y158.652
G1 X164.55 Y158.795
G1 X160.45 Y162.896 E.22033
G1 X160.306 Y163.039
G1 X160.306 Y162.475
G1 X160.45 Y162.332
G1 X164.55 Y158.231 E.22033
G1 X164.694 Y158.088
G1 X164.694 Y157.525
G1 X164.55 Y157.668
G1 X160.45 Y161.769 E.22033
G1 X160.306 Y161.912
G1 X160.306 Y161.348
G1 X160.45 Y161.205
G1 X164.55 Y157.104 E.22033
G1 X164.694 Y156.961
G1 X164.694 Y156.397
G1 X164.55 Y156.541
G1 X160.45 Y160.641 E.22033
G1 X160.306 Y160.785
G1 X160.306 Y160.221
G1 X160.45 Y160.078
G1 X164.113 Y156.414 E.19685
G1 X164.257 Y156.271
G1 X163.693 Y156.271
G1 X163.55 Y156.414
G1 X160.45 Y159.514 E.16657
G1 X160.306 Y159.658
G1 X160.306 Y159.094
G1 X160.45 Y158.951
G1 X162.986 Y156.414 E.13629
G1 X163.129 Y156.271
G1 X162.566 Y156.271
G1 X162.423 Y156.414
G1 X160.45 Y158.387 E.10601
G1 X160.306 Y158.53
G1 X160.306 Y157.967
G1 X160.45 Y157.824
G1 X161.859 Y156.414 E.07573
G1 X162.002 Y156.271
G1 X161.439 Y156.271
G1 X161.296 Y156.414
G1 X160.45 Y157.26 E.04545
M204 S10000
G1 X159.847 Y157.544 F60000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.847 Y156.977 E.01994
G1 X158.712 Y156.977 E.03987
G1 X158.712 Y163.023 E.21241
G1 X159.847 Y163.023 E.03987
G1 X159.847 Y157.604 E.19037
M204 S10000
G1 X159.471 Y157.544 F60000
; LINE_WIDTH: 0.434694
G1 F11743.522
M204 S8000
G1 X159.471 Y157.353 E.007
G1 X159.088 Y157.353 E.014
G1 X159.088 Y162.647 E.19342
G1 X159.471 Y162.647 E.014
G1 X159.471 Y157.604 E.18423
; COOLING_NODE: 1
; WIPE_START
G1 X159.471 Y159.604 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.915 Y161.288 Z4.68 F60000
G1 X176.278 Y163.407 Z4.68
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X178.099 Y156.593 E.06915
G1 X178.099 Y163.407 E.25885
G1 X176.338 Y163.407 E.06687
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5674
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X179.808 Y156.21 E.13749
G1 X179.808 Y163.79 E.2663
G1 X175.955 Y163.79 E.13538
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.662 Y163.023 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X177.715 Y163.023 E.037
G1 X177.715 Y156.977 E.21241
G1 X176.662 Y156.977 E.037
G1 X176.662 Y162.963 E.2103
M204 S10000
G1 X177.017 Y162.668 F60000
; LINE_WIDTH: 0.393844
G1 F13144.827
M204 S8000
G1 X177.36 Y162.668 E.01117
G1 X177.36 Y157.332 E.17414
G1 X177.017 Y157.332 E.01117
G1 X177.017 Y162.608 E.17218
; WIPE_START
G1 X177.017 Y160.608 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X179.604 Y162.902 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X178.92 Y163.586 E.03676
G1 X178.777 Y163.729
G1 X178.213 Y163.729
G1 X178.357 Y163.586
G1 X179.604 Y162.338 E.06704
G1 X179.747 Y162.195
G1 X179.747 Y161.631
G1 X179.604 Y161.775
G1 X178.318 Y163.061 E.06911
G1 X178.175 Y163.204
G1 X178.175 Y162.641
G1 X178.318 Y162.497
G1 X179.604 Y161.211 E.06911
G1 X179.747 Y161.068
G1 X179.747 Y160.504
G1 X179.604 Y160.648
G1 X178.318 Y161.934 E.06911
G1 X178.175 Y162.077
G1 X178.175 Y161.513
G1 X178.318 Y161.37
G1 X179.604 Y160.084 E.06911
G1 X179.747 Y159.941
G1 X179.747 Y159.377
G1 X179.604 Y159.52
G1 X178.318 Y160.807 E.06911
G1 X178.175 Y160.95
G1 X178.175 Y160.386
G1 X178.318 Y160.243
G1 X179.604 Y158.957 E.06911
G1 X179.747 Y158.814
G1 X179.747 Y158.25
G1 X179.604 Y158.393
G1 X178.318 Y159.68 E.06911
G1 X178.175 Y159.823
G1 X178.175 Y159.259
G1 X178.318 Y159.116
G1 X179.604 Y157.83 E.06911
G1 X179.747 Y157.687
G1 X179.747 Y157.123
G1 X179.604 Y157.266
G1 X178.318 Y158.553 E.06911
G1 X178.175 Y158.696
G1 X178.175 Y158.132
G1 X178.318 Y157.989
G1 X179.604 Y156.703 E.06911
G1 X179.747 Y156.559
G1 X179.472 Y156.271
G1 X179.329 Y156.414
G1 X178.318 Y157.425 E.05434
G1 X178.175 Y157.569
G1 X178.175 Y157.005
G1 X178.318 Y156.862
G1 X178.766 Y156.414 E.02406
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X178.318 Y156.862 E-.24061
G1 X178.175 Y157.005 E-.07695
G1 X178.175 Y157.569 E-.21415
G1 X178.318 Y157.425 E-.07695
G1 X178.6 Y157.144 E-.15135
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.901 Y156.593 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.06915
G1 X184.722 Y163.407 E.25885
G1 X182.901 Y163.407 E.06915
G1 X182.901 Y156.653 E.25657
; COOLING_NODE: 1
; WIPE_START
G1 X184.722 Y156.593 E-.69204
G1 X184.722 Y156.772 E-.06797
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X181.192 Y156.21 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5674
M204 S5000
G1 X185.105 Y156.21 E.13749
G1 X185.105 Y163.79 E.2663
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

G1 X181.192 Y163.79 E.13749
G1 X181.192 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X183.191 Y156.239 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.285 Y163.023 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X184.338 Y163.023 E.037
G1 X184.338 Y156.977 E.21241
G1 X183.285 Y156.977 E.037
G1 X183.285 Y162.963 E.2103
M204 S10000
G1 X183.64 Y162.668 F60000
; LINE_WIDTH: 0.393844
G1 F13144.827
M204 S8000
G1 X183.983 Y162.668 E.01117
G1 X183.983 Y157.332 E.17414
G1 X183.64 Y157.332 E.01117
G1 X183.64 Y162.608 E.17218
; WIPE_START
G1 X183.64 Y160.608 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.301 Y163.586 Z4.68 F60000
G1 Z4.28
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S2000
G1 X182.682 Y163.205 E.02045
G1 X182.825 Y163.062
G1 X182.825 Y162.498
G1 X182.682 Y162.642
G1 X181.738 Y163.586 E.05073
G1 X181.595 Y163.729
G1 X181.253 Y163.508
G1 X181.396 Y163.364
G1 X182.682 Y162.078 E.06911
G1 X182.825 Y161.935
G1 X182.825 Y161.371
G1 X182.682 Y161.515
G1 X181.396 Y162.801 E.06911
G1 X181.253 Y162.944
G1 X181.253 Y162.38
G1 X181.396 Y162.237
G1 X182.682 Y160.951 E.06911
G1 X182.825 Y160.808
G1 X182.825 Y160.244
G1 X182.682 Y160.387
G1 X181.396 Y161.674 E.06911
G1 X181.253 Y161.817
G1 X181.253 Y161.253
G1 X181.396 Y161.11
G1 X182.682 Y159.824 E.06911
G1 X182.825 Y159.681
G1 X182.825 Y159.117
G1 X182.682 Y159.26
G1 X181.396 Y160.547 E.06911
G1 X181.253 Y160.69
G1 X181.253 Y160.126
G1 X181.396 Y159.983
G1 X182.682 Y158.697 E.06911
G1 X182.825 Y158.554
G1 X182.825 Y157.99
G1 X182.682 Y158.133
G1 X181.396 Y159.42 E.06911
G1 X181.253 Y159.563
G1 X181.253 Y158.999
G1 X181.396 Y158.856
G1 X182.682 Y157.57 E.06911
G1 X182.825 Y157.426
G1 X182.825 Y156.863
G1 X182.682 Y157.006
G1 X181.396 Y158.292 E.06911
G1 X181.253 Y158.436
M73 P83 R2
G1 X181.253 Y157.872
G1 X181.396 Y157.729
G1 X182.682 Y156.443 E.06911
G1 X182.825 Y156.299
G1 X182.29 Y156.271
G1 X182.147 Y156.414
G1 X181.396 Y157.165 E.04036
; CHANGE_LAYER
; Z_HEIGHT: 4.52
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F11292.473
M204 S8000
G1 X182.147 Y156.414 E-.40369
G1 X182.29 Y156.271 E-.07695
G1 X182.825 Y156.299 E-.20364
G1 X182.684 Y156.44 E-.07573
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 19/44
; update layer progress
M73 L19
M991 S0 P18 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z4.68 I-.21 J-1.199 P1  F60000
G1 X142.852 Y163.407 Z4.68
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.09396
G1 X140.378 Y156.593 E.25885
G1 X142.852 Y156.593 E.09396
G1 X142.852 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X143.235 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.11384
G1 X139.995 Y156.21 E.2663
G1 X143.235 Y156.21 E.11384
G1 X143.235 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X141.236 Y163.767 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X142.468 Y157.83 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X142.468 Y156.977 E.02997
G1 X140.762 Y156.977 E.05994
G1 X140.762 Y163.023 E.21241
G1 X142.468 Y163.023 E.05994
G1 X142.468 Y157.89 E.18033
M204 S10000
G1 X142.1 Y157.83 F60000
G1 F12212.001
M204 S8000
G1 X142.1 Y157.345 E.01703
G1 X141.13 Y157.345 E.03405
G1 X141.13 Y162.655 E.18652
G1 X142.1 Y162.655 E.03405
G1 X142.1 Y157.89 E.16739
M204 S10000
G1 X141.765 Y157.83 F60000
; LINE_WIDTH: 0.351894
G1 F14980.526
M204 S8000
G1 X141.765 Y157.68 E.0043
G1 X141.465 Y157.68 E.0086
G1 X141.465 Y162.32 E.13289
G1 X141.765 Y162.32 E.0086
G1 X141.765 Y157.89 E.12687
; COOLING_NODE: 3
; WIPE_START
G1 X141.765 Y159.89 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.557 Y163.373 Z4.92 F60000
G1 X148.621 Y163.407 Z4.92
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.148 Y163.407 E.09396
G1 X146.148 Y156.593 E.25885
G1 X148.621 Y156.593 E.09396
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X145.765 Y163.79 E.11384
G1 X145.765 Y156.21 E.2663
G1 X149.005 Y156.21 E.11384
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.005 Y163.767 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.238 Y157.83 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X148.238 Y156.977 E.02997
G1 X146.532 Y156.977 E.05994
G1 X146.532 Y163.023 E.21241
G1 X148.238 Y163.023 E.05994
G1 X148.238 Y157.89 E.18033
M204 S10000
G1 X147.87 Y157.83 F60000
G1 F12212.001
M204 S8000
G1 X147.87 Y157.345 E.01703
G1 X146.9 Y157.345 E.03405
G1 X146.9 Y162.655 E.18652
G1 X147.87 Y162.655 E.03405
G1 X147.87 Y157.89 E.16739
M204 S10000
G1 X147.535 Y157.83 F60000
; LINE_WIDTH: 0.351894
G1 F14980.526
M204 S8000
G1 X147.535 Y157.68 E.0043
G1 X147.235 Y157.68 E.0086
G1 X147.235 Y162.32 E.13289
G1 X147.535 Y162.32 E.0086
G1 X147.535 Y157.89 E.12687
; COOLING_NODE: 2
; WIPE_START
G1 X147.535 Y159.89 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.835 Y157.661 Z4.92 F60000
G1 X158.328 Y156.593 Z4.92
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.705 Y156.593 E.0903
G1 X160.705 Y163.407 E.25885
G1 X158.328 Y163.407 E.0903
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X161.089 Y156.21 E.11044
G1 X161.089 Y163.79 E.2663
G1 X157.945 Y163.79 E.11044
G1 X157.945 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X159.945 Y156.232 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.517 Y162.218 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.555744
G1 F8924.322
M204 S8000
G1 X159.517 Y157.842 E.21039
M204 S10000
G1 X159.953 Y157.782 F60000
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.953 Y157.345 E.01533
G1 X159.08 Y157.345 E.03066
G1 X159.08 Y162.655 E.18652
G1 X159.953 Y162.655 E.03066
G1 X159.953 Y157.842 E.16908
M204 S10000
G1 X160.322 Y157.782 F60000
G1 F12212.001
M204 S8000
G1 X160.322 Y156.977 E.02828
G1 X158.712 Y156.977 E.05655
G1 X158.712 Y163.023 E.21241
G1 X160.322 Y163.023 E.05655
G1 X160.322 Y157.842 E.18203
; COOLING_NODE: 2
; WIPE_START
G1 X160.322 Y159.842 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.672 Y156.593 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
M73 P83 R1
G1 X164.295 Y163.407 E.0903
G1 X164.295 Y156.593 E.25885
G1 X166.612 Y156.593 E.08802
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X163.911 Y163.79 E.11044
G1 X163.911 Y156.21 E.2663
G1 X166.995 Y156.21 E.10834
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.483 Y162.218 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.555744
G1 F8924.322
M204 S8000
G1 X165.483 Y157.842 E.21039
; WIPE_START
G1 X165.483 Y159.842 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.047 Y162.655 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X165.92 Y162.655 E.03066
G1 X165.92 Y157.345 E.18652
G1 X165.047 Y157.345 E.03066
G1 X165.047 Y162.595 E.18441
M204 S10000
G1 X164.678 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X166.288 Y163.023 E.05655
G1 X166.288 Y156.977 E.21241
G1 X164.678 Y156.977 E.05655
G1 X164.678 Y162.963 E.2103
; COOLING_NODE: 1
; WIPE_START
G1 X164.678 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X172.147 Y162.536 Z4.92 F60000
G1 X176.278 Y163.407 Z4.92
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X178.573 Y156.593 E.08719
G1 X178.573 Y163.407 E.25885
G1 X176.338 Y163.407 E.08491
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5618
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X178.957 Y156.21 E.10757
G1 X178.957 Y163.79 E.2663
G1 X175.955 Y163.79 E.10547
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.426 Y162.259 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.474064
G1 F10649.376
M204 S8000
G1 X177.426 Y157.801 E.1796
; WIPE_START
G1 X177.426 Y159.801 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X177.03 Y162.655 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X177.822 Y162.655 E.02779
G1 X177.822 Y157.345 E.18652
G1 X177.03 Y157.345 E.02779
G1 X177.03 Y162.595 E.18441
M204 S10000
G1 X176.662 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X178.19 Y163.023 E.05368
G1 X178.19 Y156.977 E.21241
G1 X176.662 Y156.977 E.05368
G1 X176.662 Y162.963 E.2103
; COOLING_NODE: 1
; WIPE_START
G1 X176.662 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.427 Y156.593 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.08719
G1 X184.722 Y163.407 E.25885
G1 X182.427 Y163.407 E.08719
G1 X182.427 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X182.043 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5618
M204 S5000
G1 X185.105 Y156.21 E.10757
G1 X185.105 Y163.79 E.2663
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

G1 X182.043 Y163.79 E.10757
G1 X182.043 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
M73 P84 R1
G1 X184.043 Y156.231 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.574 Y162.259 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.474044
G1 F10649.88
M204 S8000
G1 X183.574 Y157.801 E.17959
; WIPE_START
G1 X183.574 Y159.801 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.179 Y162.655 Z4.92 F60000
G1 Z4.52
G1 E.8 F1800
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X183.97 Y162.655 E.02779
G1 X183.97 Y157.345 E.18652
G1 X183.179 Y157.345 E.02779
G1 X183.179 Y162.595 E.18441
M204 S10000
G1 X182.81 Y163.023 F60000
G1 F12212.001
M204 S8000
G1 X184.338 Y163.023 E.05368
G1 X184.338 Y156.977 E.21241
G1 X182.81 Y156.977 E.05368
G1 X182.81 Y162.963 E.2103
; CHANGE_LAYER
; Z_HEIGHT: 4.76
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12212.001
G1 X182.81 Y160.963 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 20/44
; update layer progress
M73 L20
M991 S0 P19 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z4.92 I-.073 J-1.215 P1  F60000
G1 X142.312 Y163.407 Z4.92
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.07347
G1 X140.378 Y156.593 E.25885
G1 X142.312 Y156.593 E.07347
G1 X142.312 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X142.696 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.09488
G1 X139.995 Y156.21 E.2663
G1 X142.696 Y156.21 E.09488
G1 X142.696 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X140.696 Y163.774 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X141.929 Y157.56 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X141.929 Y156.977 E.0205
G1 X140.762 Y156.977 E.04099
G1 X140.762 Y163.023 E.21241
G1 X141.929 Y163.023 E.04099
G1 X141.929 Y157.62 E.18981
M204 S10000
G1 X141.545 Y157.56 F60000
; LINE_WIDTH: 0.450674
G1 F11273.393
M204 S8000
G1 X141.545 Y157.361 E.0076
G1 X141.146 Y157.361 E.01519
G1 X141.146 Y162.639 E.20088
G1 X141.545 Y162.639 E.01519
G1 X141.545 Y157.62 E.191
; COOLING_NODE: 3
; WIPE_START
G1 X141.545 Y159.62 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.275 Y163.221 Z5.16 F60000
G1 X148.621 Y163.407 Z5.16
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X146.688 Y163.407 E.07347
G1 X146.688 Y156.593 E.25885
G1 X148.621 Y156.593 E.07347
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X146.304 Y163.79 E.09488
G1 X146.304 Y156.21 E.2663
G1 X149.005 Y156.21 E.09488
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.005 Y163.774 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.238 Y157.56 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X148.238 Y156.977 E.0205
G1 X147.071 Y156.977 E.04099
G1 X147.071 Y163.023 E.21241
G1 X148.238 Y163.023 E.04099
G1 X148.238 Y157.62 E.18981
M204 S10000
G1 X147.854 Y157.56 F60000
; LINE_WIDTH: 0.450674
G1 F11273.393
M204 S8000
G1 X147.854 Y157.361 E.0076
G1 X147.455 Y157.361 E.01519
G1 X147.455 Y162.639 E.20088
G1 X147.854 Y162.639 E.01519
G1 X147.854 Y157.62 E.191
; COOLING_NODE: 2
; WIPE_START
G1 X147.854 Y159.62 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.187 Y157.501 Z5.16 F60000
G1 X158.328 Y156.593 Z5.16
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X160.212 Y156.593 E.07156
G1 X160.212 Y163.407 E.25885
G1 X158.328 Y163.407 E.07156
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X160.595 Y156.21 E.09312
G1 X160.595 Y163.79 E.2663
G1 X157.945 Y163.79 E.09312
G1 X157.945 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X159.944 Y156.225 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.828 Y157.535 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.828 Y156.977 E.01961
G1 X158.712 Y156.977 E.03923
G1 X158.712 Y163.023 E.21241
G1 X159.828 Y163.023 E.03923
G1 X159.828 Y157.595 E.19069
M204 S10000
G1 X159.457 Y157.535 F60000
; LINE_WIDTH: 0.425524
G1 F12031.444
M204 S8000
G1 X159.457 Y157.348 E.00667
G1 X159.083 Y157.348 E.01334
G1 X159.083 Y162.652 E.18912
G1 X159.457 Y162.652 E.01334
G1 X159.457 Y157.595 E.18031
; COOLING_NODE: 2
; WIPE_START
G1 X159.457 Y159.595 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.504 Y156.663 Z5.16 F60000
G1 X166.672 Y156.593 Z5.16
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X164.788 Y163.407 E.07156
G1 X164.788 Y156.593 E.25885
G1 X166.612 Y156.593 E.06928
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X164.405 Y163.79 E.09312
G1 X164.405 Y156.21 E.2663
G1 X166.995 Y156.21 E.09101
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.172 Y163.023 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.288 Y163.023 E.03923
G1 X166.288 Y156.977 E.21241
G1 X165.172 Y156.977 E.03923
G1 X165.172 Y162.963 E.2103
M204 S10000
G1 X165.543 Y162.652 F60000
; LINE_WIDTH: 0.425514
G1 F12031.764
M204 S8000
G1 X165.917 Y162.652 E.01334
G1 X165.917 Y157.348 E.18912
G1 X165.543 Y157.348 E.01334
G1 X165.543 Y162.592 E.18698
; COOLING_NODE: 1
; WIPE_START
G1 X165.543 Y160.592 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X172.926 Y162.527 Z5.16 F60000
G1 X176.278 Y163.407 Z5.16
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X178.116 Y156.593 E.06981
G1 X178.116 Y163.407 E.25885
G1 X176.338 Y163.407 E.06753
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5554
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X178.499 Y156.21 E.0915
G1 X178.499 Y163.79 E.2663
G1 X175.955 Y163.79 E.08939
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.662 Y163.023 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X177.733 Y163.023 E.03761
G1 X177.733 Y156.977 E.21241
G1 X176.662 Y156.977 E.03761
G1 X176.662 Y162.963 E.2103
M204 S10000
G1 X177.022 Y162.663 F60000
; LINE_WIDTH: 0.402514
G1 F12820.148
M204 S8000
G1 X177.373 Y162.663 E.01175
G1 X177.373 Y157.337 E.17826
G1 X177.022 Y157.337 E.01175
G1 X177.022 Y162.603 E.17625
; COOLING_NODE: 1
; WIPE_START
G1 X177.022 Y160.603 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.884 Y156.593 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.06981
G1 X184.722 Y163.407 E.25885
G1 X182.884 Y163.407 E.06981
G1 X182.884 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X182.501 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5554
M204 S5000
G1 X185.105 Y156.21 E.0915
G1 X185.105 Y163.79 E.2663
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

G1 X182.501 Y163.79 E.0915
G1 X182.501 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X184.5 Y156.224 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.268 Y163.023 Z5.16 F60000
G1 Z4.76
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X184.338 Y163.023 E.03761
G1 X184.338 Y156.977 E.21241
G1 X183.268 Y156.977 E.03761
G1 X183.268 Y162.963 E.2103
M204 S10000
M73 P85 R1
G1 X183.627 Y162.663 F60000
; LINE_WIDTH: 0.402514
G1 F12820.148
M204 S8000
G1 X183.978 Y162.663 E.01175
G1 X183.978 Y157.337 E.17826
G1 X183.627 Y157.337 E.01175
G1 X183.627 Y162.603 E.17625
; CHANGE_LAYER
; Z_HEIGHT: 5
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12820.148
G1 X183.627 Y160.603 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 21/44
; update layer progress
M73 L21
M991 S0 P20 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z5.16 I-.082 J-1.214 P1  F60000
G1 X141.943 Y163.407 Z5.16
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.05945
G1 X140.378 Y156.593 E.25885
G1 X141.943 Y156.593 E.05945
G1 X141.943 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X142.327 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.08192
G1 X139.995 Y156.21 E.2663
G1 X142.327 Y156.21 E.08192
G1 X142.327 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X140.327 Y163.781 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X141.56 Y157.376 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X141.56 Y156.977 E.01401
G1 X140.762 Y156.977 E.02803
G1 X140.762 Y163.023 E.21241
G1 X141.56 Y163.023 E.02803
G1 X141.56 Y157.436 E.19629
; WIPE_START
G1 X141.56 Y159.436 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X141.161 Y162.624 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; LINE_WIDTH: 0.480744
G1 F10483.646
M204 S8000
G1 X141.161 Y157.436 E.21233
; COOLING_NODE: 3
; WIPE_START
G1 X141.161 Y159.436 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.898 Y163.022 Z5.4 F60000
G1 X148.621 Y163.407 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X147.057 Y163.407 E.05945
G1 X147.057 Y156.593 E.25885
G1 X148.621 Y156.593 E.05945
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X146.673 Y163.79 E.08192
G1 X146.673 Y156.21 E.2663
G1 X149.005 Y156.21 E.08192
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.006 Y163.781 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.238 Y157.376 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X148.238 Y156.977 E.01401
G1 X147.44 Y156.977 E.02803
G1 X147.44 Y163.023 E.21241
G1 X148.238 Y163.023 E.02803
G1 X148.238 Y157.436 E.19629
; WIPE_START
G1 X148.238 Y159.436 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.839 Y162.624 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; LINE_WIDTH: 0.480744
G1 F10483.646
M204 S8000
G1 X147.839 Y157.436 E.21233
; COOLING_NODE: 2
; WIPE_START
G1 X147.839 Y159.436 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.206 Y157.44 Z5.4 F60000
G1 X158.328 Y156.593 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.86 Y156.593 E.0582
G1 X159.86 Y163.407 E.25885
G1 X158.328 Y163.407 E.0582
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X160.244 Y156.21 E.08077
G1 X160.244 Y163.79 E.2663
G1 X157.945 Y163.79 E.08077
G1 X157.945 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X159.944 Y156.218 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.477 Y157.359 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X159.477 Y156.977 E.01344
G1 X158.712 Y156.977 E.02688
G1 X158.712 Y163.023 E.21241
G1 X159.477 Y163.023 E.02688
G1 X159.477 Y157.419 E.19687
; WIPE_START
G1 X159.477 Y159.419 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.094 Y162.641 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; LINE_WIDTH: 0.447984
G1 F11349.88
M204 S8000
G1 X159.094 Y157.419 E.19736
; COOLING_NODE: 2
; WIPE_START
G1 X159.094 Y159.419 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.246 Y156.752 Z5.4 F60000
G1 X166.672 Y156.593 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X165.14 Y163.407 E.0582
G1 X165.14 Y156.593 E.25885
G1 X166.612 Y156.593 E.05592
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X164.756 Y163.79 E.08077
G1 X164.756 Y156.21 E.2663
G1 X166.995 Y156.21 E.07866
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.523 Y163.023 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X166.288 Y163.023 E.02688
G1 X166.288 Y156.977 E.21241
G1 X165.523 Y156.977 E.02688
G1 X165.523 Y162.963 E.2103
M204 S10000
G1 X165.906 Y162.641 F60000
; LINE_WIDTH: 0.447984
G1 F11349.88
M204 S8000
G1 X165.906 Y157.419 E.19736
; COOLING_NODE: 1
; WIPE_START
G1 X165.906 Y159.419 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.03 Y162.158 Z5.4 F60000
G1 X176.278 Y163.407 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X177.78 Y156.593 E.05706
G1 X177.78 Y163.407 E.25885
G1 X176.338 Y163.407 E.05478
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5482
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X178.164 Y156.21 E.07971
G1 X178.164 Y163.79 E.2663
G1 X175.955 Y163.79 E.07761
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.662 Y163.023 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X177.397 Y163.023 E.02582
G1 X177.397 Y156.977 E.21241
G1 X176.662 Y156.977 E.02582
G1 X176.662 Y162.963 E.2103
M204 S10000
G1 X177.029 Y162.656 F60000
; LINE_WIDTH: 0.418004
G1 F12278.309
M204 S8000
G1 X177.029 Y157.404 E.18348
; COOLING_NODE: 1
; WIPE_START
G1 X177.029 Y159.404 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.22 Y156.593 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.05706
G1 X184.722 Y163.407 E.25885
G1 X183.22 Y163.407 E.05706
G1 X183.22 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X182.836 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5482
M204 S5000
G1 X185.105 Y156.21 E.07971
G1 X185.105 Y163.79 E.2663
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

G1 X182.836 Y163.79 E.07971
G1 X182.836 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X184.835 Y156.217 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.603 Y163.023 Z5.4 F60000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.419994
G1 F12212.001
M204 S8000
G1 X184.338 Y163.023 E.02582
G1 X184.338 Y156.977 E.21241
G1 X183.603 Y156.977 E.02582
G1 X183.603 Y162.963 E.2103
M204 S10000
G1 X183.971 Y162.656 F60000
; LINE_WIDTH: 0.418004
G1 F12278.309
M204 S8000
G1 X183.971 Y157.404 E.18348
; CHANGE_LAYER
; Z_HEIGHT: 5.24
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12278.309
G1 X183.971 Y159.404 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 22/44
; update layer progress
M73 L22
M991 S0 P21 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z5.4 I-.115 J-1.212 P1  F60000
G1 X141.658 Y163.407 Z5.4
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.0486
G1 X140.378 Y156.593 E.25885
G1 X141.658 Y156.593 E.0486
G1 X141.658 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X142.041 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.07189
G1 X139.995 Y156.21 E.2663
M73 P86 R1
G1 X142.041 Y156.21 E.07189
G1 X142.041 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X140.042 Y163.789 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X141.238 Y157.233 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.491874
G1 F10218.68
M204 S8000
G1 X141.238 Y157.013 E.00924
G1 X140.798 Y157.013 E.01849
G1 X140.798 Y162.987 E.25083
G1 X141.238 Y162.987 E.01849
G1 X141.238 Y157.293 E.23906
; COOLING_NODE: 3
; WIPE_START
G1 X141.238 Y159.293 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.906 Y163.008 Z5.64 F60000
G1 X148.621 Y163.407 Z5.64
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X147.342 Y163.407 E.0486
G1 X147.342 Y156.593 E.25885
G1 X148.621 Y156.593 E.0486
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X146.959 Y163.79 E.07189
G1 X146.959 Y156.21 E.2663
G1 X149.005 Y156.21 E.07189
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.006 Y163.789 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.202 Y157.233 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.491874
G1 F10218.68
M204 S8000
G1 X148.202 Y157.013 E.00924
G1 X147.762 Y157.013 E.01849
G1 X147.762 Y162.987 E.25083
G1 X148.202 Y162.987 E.01849
G1 X148.202 Y157.293 E.23906
; COOLING_NODE: 2
; WIPE_START
G1 X148.202 Y159.293 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.577 Y157.327 Z5.64 F60000
G1 X158.328 Y156.593 Z5.64
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.585 Y156.593 E.04773
G1 X159.585 Y163.407 E.25885
G1 X158.328 Y163.407 E.04773
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.968 Y156.21 E.07108
G1 X159.968 Y163.79 E.2663
G1 X157.945 Y163.79 E.07108
G1 X157.945 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X159.944 Y156.211 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.171 Y157.222 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.480384
G1 F10492.446
M204 S8000
G1 X159.171 Y157.007 E.00877
G1 X158.742 Y157.007 E.01754
G1 X158.742 Y162.993 E.24475
G1 X159.171 Y162.993 E.01754
G1 X159.171 Y157.282 E.23353
; COOLING_NODE: 2
; WIPE_START
G1 X159.171 Y159.282 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.356 Y156.707 Z5.64 F60000
G1 X166.672 Y156.593 Z5.64
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X165.415 Y163.407 E.04773
G1 X165.415 Y156.593 E.25885
G1 X166.612 Y156.593 E.04545
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X165.032 Y163.79 E.07108
G1 X165.032 Y156.21 E.2663
G1 X166.995 Y156.21 E.06897
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.829 Y162.993 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.480384
G1 F10492.446
M204 S8000
G1 X166.258 Y162.993 E.01754
G1 X166.258 Y157.007 E.24475
G1 X165.829 Y157.007 E.01754
G1 X165.829 Y162.933 E.2423
; COOLING_NODE: 1
; WIPE_START
G1 X165.829 Y160.933 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.256 Y162.691 Z5.64 F60000
G1 X176.278 Y163.407 Z5.64
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X177.514 Y156.593 E.04696
G1 X177.514 Y163.407 E.25885
G1 X176.338 Y163.407 E.04468
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5402
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X177.898 Y156.21 E.07037
G1 X177.898 Y163.79 E.2663
G1 X175.955 Y163.79 E.06826
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.687 Y162.998 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.470234
G1 F10746.782
M204 S8000
G1 X177.106 Y162.998 E.01672
G1 X177.106 Y157.002 E.23937
G1 X176.687 Y157.002 E.01672
G1 X176.687 Y162.938 E.23697
; COOLING_NODE: 1
; WIPE_START
G1 X176.687 Y160.938 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.119 Y156.828 Z5.64 F60000
G1 X183.486 Y156.593 Z5.64
G1 Z5.24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.04696
G1 X184.722 Y163.407 E.25885
G1 X183.486 Y163.407 E.04696
G1 X183.486 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.102 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5402
M204 S5000
G1 X185.105 Y156.21 E.07037
G1 X185.105 Y163.79 E.2663
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

G1 X183.102 Y163.79 E.07037
G1 X183.102 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X185.101 Y156.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.894 Y162.998 Z5.64 F60000
G1 Z5.24
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.470234
G1 F10746.782
M204 S8000
G1 X184.313 Y162.998 E.01672
G1 X184.313 Y157.002 E.23936
G1 X183.894 Y157.002 E.01672
G1 X183.894 Y162.938 E.23697
; CHANGE_LAYER
; Z_HEIGHT: 5.48
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10746.782
G1 X183.894 Y160.938 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 23/44
; update layer progress
M73 L23
M991 S0 P22 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z5.64 I-.071 J-1.215 P1  F60000
G1 X141.428 Y163.407 Z5.64
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.03988
G1 X140.378 Y156.593 E.25885
G1 X141.428 Y156.593 E.03988
G1 X141.428 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.812 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.06382
G1 X139.995 Y156.21 E.2663
G1 X141.812 Y156.21 E.06382
G1 X141.812 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X139.995 Y163.79 E-.69066
G1 X139.995 Y163.608 E-.06934
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X141.066 Y157.118 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.377034
G1 F13823.611
M204 S8000
G1 X141.066 Y156.955 E.00505
G1 X140.74 Y156.955 E.0101
G1 X140.74 Y163.045 E.18898
G1 X141.066 Y163.045 E.0101
G1 X141.066 Y157.178 E.18207
; COOLING_NODE: 3
; WIPE_START
G1 X141.066 Y159.178 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.726 Y162.906 Z5.88 F60000
G1 X148.621 Y163.407 Z5.88
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X147.572 Y163.407 E.03987
G1 X147.572 Y156.593 E.25885
G1 X148.621 Y156.593 E.03987
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.188 Y163.79 E.06382
G1 X147.188 Y156.21 E.2663
G1 X149.005 Y156.21 E.06382
G1 X149.005 Y163.73 E.2642
; WIPE_START
M204 S8000
G1 X147.188 Y163.79 E-.69065
G1 X147.188 Y163.608 E-.06935
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.259 Y157.118 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.377024
G1 F13824.037
M204 S8000
G1 X148.259 Y156.955 E.00505
G1 X147.934 Y156.955 E.0101
G1 X147.934 Y163.045 E.18897
G1 X148.259 Y163.045 E.0101
G1 X148.259 Y157.178 E.18206
; COOLING_NODE: 2
; WIPE_START
G1 X148.259 Y159.178 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.652 Y157.28 Z5.88 F60000
G1 X158.328 Y156.593 Z5.88
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.362 Y156.593 E.03926
G1 X159.362 Y163.407 E.25885
M73 P87 R1
G1 X158.328 Y163.407 E.03926
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.745 Y156.21 E.06325
G1 X159.745 Y163.79 E.2663
G1 X157.945 Y163.79 E.06325
G1 X157.945 Y156.27 E.2642
; WIPE_START
M204 S8000
G1 X159.745 Y156.21 E-.68455
G1 X159.745 Y156.409 E-.07545
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X158.845 Y156.793 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.686484
G1 F7086.838
M204 S8000
G1 X158.845 Y163.207 E.38833
; COOLING_NODE: 2
; WIPE_START
G1 X158.845 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.42 Y157.331 Z5.88 F60000
G1 X166.672 Y156.593 Z5.88
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X165.638 Y163.407 E.03926
G1 X165.638 Y156.593 E.25885
G1 X166.612 Y156.593 E.03698
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X165.255 Y163.79 E.06325
G1 X165.255 Y156.21 E.2663
G1 X166.995 Y156.21 E.06115
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.155 Y156.793 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.686484
G1 F7086.838
M204 S8000
G1 X166.155 Y163.207 E.38833
; COOLING_NODE: 1
; WIPE_START
G1 X166.155 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.613 Y162.828 Z5.88 F60000
G1 X176.278 Y163.407 Z5.88
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X177.298 Y156.593 E.03872
G1 X177.298 Y163.407 E.25885
G1 X176.338 Y163.407 E.03645
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5316
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X177.681 Y156.21 E.06276
G1 X177.681 Y163.79 E.2663
G1 X175.955 Y163.79 E.06065
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.788 Y163.207 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.672284
G1 F7248.945
M204 S8000
G1 X176.788 Y156.793 E.37965
; COOLING_NODE: 1
; WIPE_START
G1 X176.788 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.702 Y156.593 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.03872
G1 X184.722 Y163.407 E.25885
G1 X183.702 Y163.407 E.03872
G1 X183.702 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.319 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5316
M204 S5000
G1 X185.105 Y156.21 E.06276
G1 X185.105 Y163.79 E.2663
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

G1 X183.319 Y163.79 E.06276
G1 X183.319 Y156.27 E.2642
; WIPE_START
G1 F12000
M204 S8000
G1 X185.105 Y156.21 E-.67916
G1 X185.105 Y156.423 E-.08085
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X184.212 Y156.793 Z5.88 F60000
G1 Z5.48
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.672284
G1 F7248.945
M204 S8000
G1 X184.212 Y163.207 E.37965
; CHANGE_LAYER
; Z_HEIGHT: 5.72
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F7248.945
G1 X184.212 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 24/44
; update layer progress
M73 L24
M991 S0 P23 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z5.88 I-.062 J-1.215 P1  F60000
G1 X141.24 Y163.407 Z5.88
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.03273
G1 X140.378 Y156.593 E.25885
G1 X141.24 Y156.593 E.03273
G1 X141.24 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.623 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.05721
G1 X139.995 Y156.21 E.2663
G1 X141.623 Y156.21 E.05721
G1 X141.623 Y163.73 E.2642
M204 S10000
G1 X140.809 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.514464
G1 F9720.062
M204 S8000
G1 X140.809 Y156.793 E.28313
; COOLING_NODE: 3
; WIPE_START
G1 X140.809 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.381 Y162.674 Z6.12 F60000
G1 X148.621 Y163.407 Z6.12
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X147.76 Y163.407 E.03273
G1 X147.76 Y156.593 E.25885
G1 X148.621 Y156.593 E.03273
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.377 Y163.79 E.05721
G1 X147.377 Y156.21 E.2663
G1 X149.005 Y156.21 E.05721
G1 X149.005 Y163.73 E.2642
M204 S10000
G1 X148.191 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.514464
G1 F9720.062
M204 S8000
G1 X148.191 Y156.793 E.28313
; COOLING_NODE: 2
; WIPE_START
G1 X148.191 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.65 Y157.175 Z6.12 F60000
G1 X158.328 Y156.593 Z6.12
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.179 Y156.593 E.0323
G1 X159.179 Y163.407 E.25885
G1 X158.328 Y163.407 E.0323
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.562 Y156.21 E.05682
G1 X159.562 Y163.79 E.2663
G1 X157.945 Y163.79 E.05682
G1 X157.945 Y156.27 E.2642
M204 S10000
G1 X158.754 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.503264
G1 F9961.042
M204 S8000
G1 X158.754 Y163.207 E.27628
; COOLING_NODE: 2
; WIPE_START
G1 X158.754 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.348 Y157.365 Z6.12 F60000
G1 X166.672 Y156.593 Z6.12
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X165.821 Y163.407 E.0323
G1 X165.821 Y156.593 E.25885
G1 X166.612 Y156.593 E.03002
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X165.438 Y163.79 E.05682
G1 X165.438 Y156.21 E.2663
G1 X166.995 Y156.21 E.05471
M204 S10000
G1 X166.246 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.503264
G1 F9961.042
M204 S8000
G1 X166.246 Y163.207 E.27628
; COOLING_NODE: 1
; WIPE_START
G1 X166.246 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.702 Y162.842 Z6.12 F60000
G1 X176.278 Y163.407 Z6.12
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X177.118 Y156.593 E.03191
G1 X177.118 Y163.407 E.25885
G1 X176.338 Y163.407 E.02963
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5222
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X177.502 Y156.21 E.05645
G1 X177.502 Y163.79 E.2663
G1 X175.955 Y163.79 E.05435
M204 S10000
G1 X176.698 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.492934
G1 F10194.142
M204 S8000
G1 X176.698 Y156.793 E.26996
; COOLING_NODE: 1
; WIPE_START
G1 X176.698 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.882 Y156.593 Z6.12 F60000
G1 Z5.72
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.03191
G1 X184.722 Y163.407 E.25885
G1 X183.882 Y163.407 E.03191
G1 X183.882 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.498 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5222
M204 S5000
G1 X185.105 Y156.21 E.05645
G1 X185.105 Y163.79 E.2663
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

G1 X183.498 Y163.79 E.05645
G1 X183.498 Y156.27 E.2642
M204 S10000
G1 X184.302 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.492934
G1 F10194.142
M204 S8000
M73 P88 R1
G1 X184.302 Y163.207 E.26996
; CHANGE_LAYER
; Z_HEIGHT: 5.96
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F10194.142
G1 X184.302 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 25/44
; update layer progress
M73 L25
M991 S0 P24 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z6.12 I-.062 J-1.215 P1  F60000
G1 X141.085 Y163.407 Z6.12
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.02683
G1 X140.378 Y156.593 E.25885
G1 X141.085 Y156.593 E.02683
G1 X141.085 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.468 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.05175
G1 X139.995 Y156.21 E.2663
G1 X141.468 Y156.21 E.05175
G1 X141.468 Y163.73 E.2642
M204 S10000
G1 X140.731 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.359084
G1 F14630.341
M204 S8000
G1 X140.731 Y156.793 E.18811
; COOLING_NODE: 3
; WIPE_START
G1 X140.731 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.32 Y162.646 Z6.36 F60000
G1 X148.621 Y163.407 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X147.915 Y163.407 E.02683
G1 X147.915 Y156.593 E.25885
G1 X148.621 Y156.593 E.02683
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.532 Y163.79 E.05175
G1 X147.532 Y156.21 E.2663
G1 X149.005 Y156.21 E.05175
G1 X149.005 Y163.73 E.2642
M204 S10000
G1 X148.268 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.359084
G1 F14630.341
M204 S8000
G1 X148.268 Y156.793 E.18811
; COOLING_NODE: 2
; WIPE_START
G1 X148.268 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.725 Y157.163 Z6.36 F60000
G1 X158.328 Y156.593 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.027 Y156.593 E.02653
G1 X159.027 Y163.407 E.25885
G1 X158.328 Y163.407 E.02653
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.41 Y156.21 E.05148
G1 X159.41 Y163.79 E.2663
G1 X157.945 Y163.79 E.05148
G1 X157.945 Y156.27 E.2642
M204 S10000
G1 X158.678 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.351264
G1 F15000
M204 S8000
G1 X158.678 Y163.207 E.18332
; COOLING_NODE: 2
; WIPE_START
G1 X158.678 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.288 Y157.392 Z6.36 F60000
G1 X166.672 Y156.593 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X165.973 Y163.407 E.02653
G1 X165.973 Y156.593 E.25885
G1 X166.612 Y156.593 E.02425
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X165.59 Y163.79 E.05148
G1 X165.59 Y156.21 E.2663
G1 X166.995 Y156.21 E.04937
M204 S10000
G1 X166.322 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.351264
G1 F15000
M204 S8000
G1 X166.322 Y163.207 E.18332
; COOLING_NODE: 1
; WIPE_START
G1 X166.322 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.775 Y162.854 Z6.36 F60000
G1 X176.278 Y163.407 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X176.969 Y156.593 E.02623
G1 X176.969 Y163.407 E.25885
G1 X176.338 Y163.407 E.02395
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5122
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X177.352 Y156.21 E.0512
G1 X177.352 Y163.79 E.2663
G1 X175.955 Y163.79 E.04909
M204 S10000
G1 X176.624 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.343294
G1 F15000
M204 S8000
G1 X176.624 Y156.793 E.17845
; COOLING_NODE: 1
; WIPE_START
G1 X176.624 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.94 Y156.62 Z6.36 F60000
G1 X184.031 Y156.593 Z6.36
G1 Z5.96
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.02623
G1 X184.722 Y163.407 E.25885
G1 X184.031 Y163.407 E.02623
G1 X184.031 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.648 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5122
M204 S5000
G1 X185.105 Y156.21 E.0512
G1 X185.105 Y163.79 E.2663
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

G1 X183.648 Y163.79 E.0512
G1 X183.648 Y156.27 E.2642
M204 S10000
G1 X184.376 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.343294
G1 F15000
M204 S8000
G1 X184.376 Y163.207 E.17845
; CHANGE_LAYER
; Z_HEIGHT: 6.2
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F15000
G1 X184.376 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 26/44
; update layer progress
M73 L26
M991 S0 P25 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z6.36 I-.062 J-1.215 P1  F60000
G1 X140.956 Y163.407 Z6.36
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.02194
G1 X140.378 Y156.593 E.25885
G1 X140.956 Y156.593 E.02194
G1 X140.956 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.34 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.04724
G1 X139.995 Y156.21 E.2663
G1 X141.34 Y156.21 E.04724
G1 X141.34 Y163.73 E.2642
M204 S10000
G1 X140.667 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230594
G1 F15000
M204 S8000
G1 X140.667 Y156.793 E.10953
; COOLING_NODE: 3
; WIPE_START
G1 X140.667 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.269 Y162.622 Z6.6 F60000
G1 X148.621 Y163.407 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.044 Y163.407 E.02194
G1 X148.044 Y156.593 E.25885
G1 X148.621 Y156.593 E.02194
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.66 Y163.79 E.04724
G1 X147.66 Y156.21 E.2663
G1 X149.005 Y156.21 E.04724
G1 X149.005 Y163.73 E.2642
M204 S10000
G1 X148.333 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230594
G1 F15000
M204 S8000
G1 X148.333 Y156.793 E.10953
; COOLING_NODE: 2
; WIPE_START
G1 X148.333 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.787 Y157.153 Z6.6 F60000
G1 X158.328 Y156.593 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.9 Y156.593 E.02173
G1 X158.9 Y163.407 E.25885
G1 X158.328 Y163.407 E.02173
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.284 Y156.21 E.04704
G1 X159.284 Y163.79 E.2663
G1 X157.945 Y163.79 E.04704
G1 X157.945 Y156.27 E.2642
M204 S10000
G1 X158.614 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.224984
G1 F15000
M204 S8000
G1 X158.614 Y163.207 E.10609
; COOLING_NODE: 2
; WIPE_START
G1 X158.614 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.238 Y157.414 Z6.6 F60000
G1 X166.672 Y156.593 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X166.1 Y163.407 E.02173
G1 X166.1 Y156.593 E.25885
G1 X166.612 Y156.593 E.01945
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X165.716 Y163.79 E.04704
G1 X165.716 Y156.21 E.2663
G1 X166.995 Y156.21 E.04493
M204 S10000
G1 X166.386 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.224984
G1 F15000
M204 S8000
G1 X166.386 Y163.207 E.10609
; COOLING_NODE: 1
; WIPE_START
G1 X166.386 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.836 Y162.864 Z6.6 F60000
G1 X176.278 Y163.407 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X176.845 Y156.593 E.02154
G1 X176.845 Y163.407 E.25885
G1 X176.338 Y163.407 E.01926
; COOLING_NODE: 1
M204 S250
M73 P89 R1
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5015
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X177.229 Y156.21 E.04687
G1 X177.229 Y163.79 E.2663
G1 X175.955 Y163.79 E.04476
M204 S10000
G1 X176.562 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.220004
G1 F15000
M204 S8000
G1 X176.562 Y156.793 E.10305
; COOLING_NODE: 1
; WIPE_START
G1 X176.562 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.893 Y156.669 Z6.6 F60000
G1 X184.155 Y156.593 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.02154
G1 X184.722 Y163.407 E.25885
G1 X184.155 Y163.407 E.02154
G1 X184.155 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.771 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5015
M204 S5000
G1 X185.105 Y156.21 E.04687
G1 X185.105 Y163.79 E.2663
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

G1 X183.771 Y163.79 E.04687
G1 X183.771 Y156.27 E.2642
M204 S10000
G1 X184.438 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.220004
G1 F15000
M204 S8000
G1 X184.438 Y163.207 E.10305
; CHANGE_LAYER
; Z_HEIGHT: 6.44
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F15000
G1 X184.438 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 27/44
; update layer progress
M73 L27
M991 S0 P26 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z6.6 I-.061 J-1.215 P1  F60000
G1 X140.852 Y163.407 Z6.6
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.018
G1 X140.378 Y156.593 E.25885
G1 X140.852 Y156.593 E.018
G1 X140.852 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.236 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.04359
G1 X139.995 Y156.21 E.2663
G1 X141.236 Y156.21 E.04359
G1 X141.236 Y163.73 E.2642
M204 S10000
G1 X140.615 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.126674
G1 F15000
M204 S8000
G1 X140.615 Y156.793 E.04597
; COOLING_NODE: 3
; WIPE_START
G1 X140.615 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.228 Y162.604 Z6.84 F60000
G1 X148.621 Y163.407 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.148 Y163.407 E.018
G1 X148.148 Y156.593 E.25885
G1 X148.621 Y156.593 E.018
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.764 Y163.79 E.04359
G1 X147.764 Y156.21 E.2663
G1 X149.005 Y156.21 E.04359
G1 X149.005 Y163.73 E.2642
M204 S10000
G1 X148.385 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.126674
G1 F15000
M204 S8000
G1 X148.385 Y156.793 E.04597
; COOLING_NODE: 2
; WIPE_START
G1 X148.385 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.837 Y157.144 Z6.84 F60000
G1 X158.328 Y156.593 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.799 Y156.593 E.01787
G1 X158.799 Y163.407 E.25885
G1 X158.328 Y163.407 E.01787
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.182 Y156.21 E.04347
G1 X159.182 Y163.79 E.2663
G1 X157.945 Y163.79 E.04347
G1 X157.945 Y156.27 E.2642
M204 S10000
G1 X158.564 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.123424
G1 F15000
M204 S8000
G1 X158.564 Y163.207 E.04398
; COOLING_NODE: 2
; WIPE_START
G1 X158.564 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.197 Y157.432 Z6.84 F60000
G1 X166.672 Y156.593 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X166.201 Y163.407 E.01787
G1 X166.201 Y156.593 E.25885
G1 X166.612 Y156.593 E.01559
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X165.818 Y163.79 E.04347
G1 X165.818 Y156.21 E.2663
G1 X166.995 Y156.21 E.04136
M204 S10000
G1 X166.436 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.123424
G1 F15000
M204 S8000
G1 X166.436 Y163.207 E.04398
; COOLING_NODE: 1
; WIPE_START
G1 X166.436 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.885 Y162.872 Z6.84 F60000
G1 X176.278 Y163.407 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X176.746 Y156.593 E.01774
G1 X176.746 Y163.407 E.25885
G1 X176.338 Y163.407 E.01547
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4902
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X177.129 Y156.21 E.04335
G1 X177.129 Y163.79 E.2663
G1 X175.955 Y163.79 E.04125
M204 S10000
G1 X176.512 Y163.207 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.120074
G1 F15000
M204 S8000
G1 X176.512 Y156.793 E.04194
; COOLING_NODE: 1
; WIPE_START
G1 X176.512 Y158.793 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.854 Y156.707 Z6.84 F60000
G1 X184.254 Y156.593 Z6.84
G1 Z6.44
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.01774
G1 X184.722 Y163.407 E.25885
G1 X184.254 Y163.407 E.01774
G1 X184.254 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.871 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4902
M204 S5000
G1 X185.105 Y156.21 E.04335
G1 X185.105 Y163.79 E.2663
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

G1 X183.871 Y163.79 E.04335
G1 X183.871 Y156.27 E.2642
M204 S10000
G1 X184.488 Y156.793 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.120074
G1 F15000
M204 S8000
G1 X184.488 Y163.207 E.04194
; CHANGE_LAYER
; Z_HEIGHT: 6.68
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F15000
G1 X184.488 Y161.207 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 28/44
; update layer progress
M73 L28
M991 S0 P27 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z6.84 I-.061 J-1.215 P1  F60000
G1 X140.77 Y163.407 Z6.84
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.01489
G1 X140.378 Y156.593 E.25885
G1 X140.77 Y156.593 E.01489
G1 X140.77 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.154 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.04071
G1 X139.995 Y156.21 E.2663
G1 X141.154 Y156.21 E.04071
G1 X141.154 Y163.73 E.2642
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X139.995 Y163.79 E-.44093
G1 X139.995 Y162.95 E-.31907
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.617 Y163.353 Z7.08 F60000
G1 X148.621 Y163.407 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.23 Y163.407 E.01489
G1 X148.23 Y156.593 E.25885
G1 X148.621 Y156.593 E.01489
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.846 Y163.79 E.04071
G1 X147.846 Y156.21 E.2663
G1 X149.005 Y156.21 E.04071
G1 X149.005 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
M204 S8000
G1 X147.846 Y163.79 E-.44093
G1 X147.846 Y162.95 E-.31907
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.372 Y158.993 Z7.08 F60000
G1 X158.328 Y156.593 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.718 Y156.593 E.01479
G1 X158.718 Y163.407 E.25885
G1 X158.328 Y163.407 E.01479
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.101 Y156.21 E.04063
G1 X159.101 Y163.79 E.2663
G1 X157.945 Y163.79 E.04063
G1 X157.945 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
M204 S8000
G1 X159.101 Y156.21 E-.44001
G1 X159.101 Y157.052 E-.31999
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.672 Y156.593 Z7.08 F60000
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X166.282 Y163.407 E.01479
M73 P90 R1
G1 X166.282 Y156.593 E.25885
G1 X166.612 Y156.593 E.01251
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X165.899 Y163.79 E.04063
G1 X165.899 Y156.21 E.2663
G1 X166.995 Y156.21 E.03852
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.668 Y161.943 Z7.08 F60000
G1 X176.278 Y163.407 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X176.666 Y156.593 E.01471
G1 X176.666 Y163.407 E.25885
G1 X176.338 Y163.407 E.01243
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4784
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X177.049 Y156.21 E.04054
G1 X177.049 Y163.79 E.2663
G1 X175.955 Y163.79 E.03844
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.429 Y157.773 Z7.08 F60000
G1 X184.334 Y156.593 Z7.08
G1 Z6.68
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.01471
G1 X184.722 Y163.407 E.25885
G1 X184.334 Y163.407 E.01471
G1 X184.334 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.951 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4784
M204 S5000
G1 X185.105 Y156.21 E.04054
G1 X185.105 Y163.79 E.2663
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

G1 X183.951 Y163.79 E.04054
G1 X183.951 Y156.27 E.2642
; CHANGE_LAYER
; Z_HEIGHT: 6.92
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X185.105 Y156.21 E-.43914
G1 X185.105 Y157.054 E-.32087
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 29/44
; update layer progress
M73 L29
M991 S0 P28 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z7.08 I-.172 J-1.205 P1  F60000
G1 X140.708 Y163.407 Z7.08
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.0125
G1 X140.378 Y156.593 E.25885
G1 X140.708 Y156.593 E.0125
G1 X140.708 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.091 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.03851
G1 X139.995 Y156.21 E.2663
G1 X141.091 Y156.21 E.03851
G1 X141.091 Y163.73 E.2642
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X139.995 Y163.79 E-.41712
G1 X139.995 Y162.888 E-.34288
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.614 Y163.346 Z7.32 F60000
G1 X148.621 Y163.407 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.292 Y163.407 E.0125
G1 X148.292 Y156.593 E.25885
G1 X148.621 Y156.593 E.0125
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.909 Y163.79 E.03851
G1 X147.909 Y156.21 E.2663
G1 X149.005 Y156.21 E.03851
G1 X149.005 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
M204 S8000
G1 X147.909 Y163.79 E-.41712
G1 X147.909 Y162.888 E-.34288
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.442 Y158.941 Z7.32 F60000
G1 X158.328 Y156.593 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.657 Y156.593 E.01248
G1 X158.657 Y163.407 E.25885
G1 X158.328 Y163.407 E.01248
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X159.04 Y156.21 E.03848
G1 X159.04 Y163.79 E.2663
G1 X157.945 Y163.79 E.03848
G1 X157.945 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
M204 S8000
G1 X159.04 Y156.21 E-.41688
G1 X159.04 Y157.113 E-.34312
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.655 Y156.595 Z7.32 F60000
G1 X166.672 Y156.593 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X166.343 Y163.407 E.01248
G1 X166.343 Y156.593 E.25885
G1 X166.612 Y156.593 E.0102
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X165.96 Y163.79 E.03848
G1 X165.96 Y156.21 E.2663
G1 X166.995 Y156.21 E.03638
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.668 Y161.943 Z7.32 F60000
G1 X176.278 Y163.407 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X176.606 Y156.593 E.01244
G1 X176.606 Y163.407 E.25885
G1 X176.338 Y163.407 E.01016
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4659
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X176.989 Y156.21 E.03845
G1 X176.989 Y163.79 E.2663
G1 X175.955 Y163.79 E.03634
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.442 Y157.794 Z7.32 F60000
G1 X184.394 Y156.593 Z7.32
G1 Z6.92
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.01244
G1 X184.722 Y163.407 E.25885
G1 X184.394 Y163.407 E.01244
G1 X184.394 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X184.011 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4659
M204 S5000
G1 X185.105 Y156.21 E.03845
G1 X185.105 Y163.79 E.2663
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

G1 X184.011 Y163.79 E.03845
G1 X184.011 Y156.27 E.2642
; CHANGE_LAYER
; Z_HEIGHT: 7.16
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X185.105 Y156.21 E-.41648
G1 X185.105 Y157.114 E-.34352
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 30/44
; update layer progress
M73 L30
M991 S0 P29 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z7.32 I-.171 J-1.205 P1  F60000
G1 X140.665 Y163.407 Z7.32
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.01088
G1 X140.378 Y156.593 E.25885
G1 X140.665 Y156.593 E.01088
G1 X140.665 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.048 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.03701
G1 X139.995 Y156.21 E.2663
G1 X141.048 Y156.21 E.03701
G1 X141.048 Y163.73 E.2642
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X139.995 Y163.79 E-.40096
G1 X139.995 Y162.845 E-.35904
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.611 Y163.341 Z7.56 F60000
G1 X148.621 Y163.407 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.335 Y163.407 E.01088
G1 X148.335 Y156.593 E.25885
G1 X148.621 Y156.593 E.01088
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.952 Y163.79 E.03701
G1 X147.952 Y156.21 E.2663
G1 X149.005 Y156.21 E.03701
G1 X149.005 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
M204 S8000
G1 X147.952 Y163.79 E-.40096
G1 X147.952 Y162.845 E-.35904
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.489 Y158.906 Z7.56 F60000
G1 X158.328 Y156.593 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.614 Y156.593 E.01085
G1 X158.614 Y163.407 E.25885
G1 X158.328 Y163.407 E.01085
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X158.998 Y156.21 E.03698
G1 X158.998 Y163.79 E.2663
G1 X157.945 Y163.79 E.03698
G1 X157.945 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
M204 S8000
G1 X158.998 Y156.21 E-.40063
G1 X158.998 Y157.156 E-.35937
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.61 Y156.598 Z7.56 F60000
G1 X166.672 Y156.593 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
M73 P91 R1
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X166.386 Y163.407 E.01085
G1 X166.386 Y156.593 E.25885
G1 X166.612 Y156.593 E.00857
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X166.002 Y163.79 E.03698
G1 X166.002 Y156.21 E.2663
G1 X166.995 Y156.21 E.03487
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.668 Y161.943 Z7.56 F60000
G1 X176.278 Y163.407 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X176.564 Y156.593 E.01084
G1 X176.564 Y163.407 E.25885
G1 X176.338 Y163.407 E.00856
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4529
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X176.947 Y156.21 E.03697
G1 X176.947 Y163.79 E.2663
G1 X175.955 Y163.79 E.03486
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.45 Y157.808 Z7.56 F60000
G1 X184.436 Y156.593 Z7.56
G1 Z7.16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.01084
G1 X184.722 Y163.407 E.25885
G1 X184.436 Y163.407 E.01084
G1 X184.436 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X184.053 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4529
M204 S5000
G1 X185.105 Y156.21 E.03697
G1 X185.105 Y163.79 E.2663
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

G1 X184.053 Y163.79 E.03697
G1 X184.053 Y156.27 E.2642
; CHANGE_LAYER
; Z_HEIGHT: 7.4
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X185.105 Y156.21 E-.40049
G1 X185.105 Y157.156 E-.35951
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 31/44
; update layer progress
M73 L31
M991 S0 P30 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z7.56 I-.169 J-1.205 P1  F60000
G1 X140.639 Y163.407 Z7.56
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.378 Y163.407 E.00991
G1 X140.378 Y156.593 E.25885
G1 X140.639 Y156.593 E.00991
G1 X140.639 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.023 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X139.995 Y163.79 E.03611
G1 X139.995 Y156.21 E.2663
G1 X141.023 Y156.21 E.03611
G1 X141.023 Y163.73 E.2642
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X139.995 Y163.79 E-.39121
G1 X139.995 Y162.82 E-.36879
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.61 Y163.338 Z7.8 F60000
G1 X148.621 Y163.407 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.361 Y163.407 E.00991
G1 X148.361 Y156.593 E.25885
G1 X148.621 Y156.593 E.00991
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X147.977 Y163.79 E.03611
G1 X147.977 Y156.21 E.2663
G1 X149.005 Y156.21 E.03611
G1 X149.005 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
M204 S8000
G1 X147.977 Y163.79 E-.39121
G1 X147.977 Y162.82 E-.36879
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.518 Y158.886 Z7.8 F60000
G1 X158.328 Y156.593 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.59 Y156.593 E.00993
G1 X158.59 Y163.407 E.25885
G1 X158.328 Y163.407 E.00993
G1 X158.328 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X158.973 Y156.21 E.03613
G1 X158.973 Y163.79 E.2663
G1 X157.945 Y163.79 E.03613
G1 X157.945 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
M204 S8000
G1 X158.973 Y156.21 E-.39141
G1 X158.973 Y157.18 E-.3686
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.584 Y156.6 Z7.8 F60000
G1 X166.672 Y156.593 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.672 Y163.407 E.25885
G1 X166.41 Y163.407 E.00993
G1 X166.41 Y156.593 E.25885
G1 X166.612 Y156.593 E.00765
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X166.027 Y163.79 E.03613
G1 X166.027 Y156.21 E.2663
G1 X166.995 Y156.21 E.03402
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X167.011 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.668 Y161.943 Z7.8 F60000
G1 X176.278 Y163.407 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.278 Y156.593 E.25885
G1 X176.539 Y156.593 E.00991
G1 X176.539 Y163.407 E.25885
G1 X176.338 Y163.407 E.00763
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4395
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X176.923 Y156.21 E.03611
G1 X176.923 Y163.79 E.2663
G1 X175.955 Y163.79 E.03401
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X175.939 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.456 Y157.816 Z7.8 F60000
G1 X184.461 Y156.593 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.722 Y156.593 E.00991
G1 X184.722 Y163.407 E.25885
G1 X184.461 Y163.407 E.00991
G1 X184.461 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X184.077 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4395
M204 S5000
G1 X185.105 Y156.21 E.03611
G1 X185.105 Y163.79 E.2663
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

G1 X184.077 Y163.79 E.03611
G1 X184.077 Y156.27 E.2642
; CHANGE_LAYER
; Z_HEIGHT: 7.64
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X185.105 Y156.21 E-.39127
G1 X185.105 Y157.18 E-.36873
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 32/44
; update layer progress
M73 L32
M991 S0 P31 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z7.8 I-.169 J-1.205 P1  F60000
G1 X140.633 Y163.407 Z7.8
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.379 Y163.407 E.00963
G1 X140.379 Y156.593 E.25885
G1 X140.633 Y156.593 E.00963
G1 X140.633 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.016 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X139.995 Y163.79 E.03585
G1 X139.995 Y156.21 E.2663
G1 X141.016 Y156.21 E.03585
G1 X141.016 Y163.73 E.2642
; COOLING_NODE: 3
; WIPE_START
G1 F12000
M204 S8000
M73 P91 R0
G1 X139.995 Y163.79 E-.38847
G1 X139.995 Y162.812 E-.37153
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.61 Y163.337 Z8.04 F60000
G1 X148.621 Y163.407 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.367 Y163.407 E.00963
G1 X148.367 Y156.593 E.25885
G1 X148.621 Y156.593 E.00963
G1 X148.621 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X149.005 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X147.984 Y163.79 E.03585
G1 X147.984 Y156.21 E.2663
G1 X149.005 Y156.21 E.03585
G1 X149.005 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X147.984 Y163.79 E-.38847
G1 X147.984 Y162.812 E-.37153
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.525 Y158.88 Z8.04 F60000
G1 X158.329 Y156.593 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.582 Y156.593 E.00961
G1 X158.582 Y163.407 E.25885
G1 X158.329 Y163.407 E.00961
G1 X158.329 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.945 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X158.965 Y156.21 E.03583
G1 X158.965 Y163.79 E.2663
G1 X157.945 Y163.79 E.03583
G1 X157.945 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X158.965 Y156.21 E-.38823
G1 X158.965 Y157.188 E-.37177
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.575 Y156.601 Z8.04 F60000
G1 X166.671 Y156.593 Z8.04
M73 P92 R0
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.671 Y163.407 E.25885
G1 X166.418 Y163.407 E.00961
G1 X166.418 Y156.593 E.25885
G1 X166.611 Y156.593 E.00733
; COOLING_NODE: 2
M204 S250
G1 X167.055 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11999
M204 S5000
G1 X167.055 Y163.79 E.2663
G1 X166.035 Y163.79 E.03583
G1 X166.035 Y156.21 E.2663
G1 X166.995 Y156.21 E.03372
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X167.01 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.668 Y161.943 Z8.04 F60000
G1 X176.279 Y163.407 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.279 Y156.593 E.25885
G1 X176.533 Y156.593 E.00963
G1 X176.533 Y163.407 E.25885
G1 X176.339 Y163.407 E.00735
; COOLING_NODE: 1
M204 S250
G1 X175.895 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4255
M204 S5000
G1 X175.895 Y156.21 E.2663
G1 X176.916 Y156.21 E.03585
G1 X176.916 Y163.79 E.2663
G1 X175.955 Y163.79 E.03375
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X175.94 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.457 Y157.818 Z8.04 F60000
G1 X184.467 Y156.593 Z8.04
G1 Z7.64
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.721 Y156.593 E.00963
G1 X184.721 Y163.407 E.25885
G1 X184.467 Y163.407 E.00963
G1 X184.467 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X184.084 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4255
M204 S5000
G1 X185.105 Y156.21 E.03585
G1 X185.105 Y163.79 E.2663
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

G1 X184.084 Y163.79 E.03585
G1 X184.084 Y156.27 E.2642
; CHANGE_LAYER
; Z_HEIGHT: 7.88
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X185.105 Y156.21 E-.38847
G1 X185.105 Y157.188 E-.37153
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 33/44
; update layer progress
M73 L33
M991 S0 P32 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z8.04 I-.169 J-1.205 P1  F60000
G1 X140.642 Y163.407 Z8.04
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.386 Y163.407 E.00972
G1 X140.386 Y156.593 E.25885
G1 X140.642 Y156.593 E.00972
G1 X140.642 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.026 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X140.003 Y163.79 E.03594
G1 X140.003 Y156.21 E.2663
G1 X141.026 Y156.21 E.03594
G1 X141.026 Y163.73 E.2642
; COOLING_NODE: 3
; WIPE_START
G1 F12000
M204 S8000
G1 X140.003 Y163.79 E-.38939
G1 X140.003 Y162.815 E-.37061
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.617 Y163.338 Z8.28 F60000
G1 X148.614 Y163.407 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.358 Y163.407 E.00972
G1 X148.358 Y156.593 E.25885
G1 X148.614 Y156.593 E.00972
G1 X148.614 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X148.997 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X147.974 Y163.79 E.03594
G1 X147.974 Y156.21 E.2663
G1 X148.997 Y156.21 E.03594
G1 X148.997 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X147.974 Y163.79 E-.38939
G1 X147.974 Y162.815 E-.37061
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.518 Y158.886 Z8.28 F60000
G1 X158.336 Y156.593 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.593 Y156.593 E.00974
G1 X158.593 Y163.407 E.25885
G1 X158.336 Y163.407 E.00974
G1 X158.336 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.953 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X158.976 Y156.21 E.03595
G1 X158.976 Y163.79 E.2663
G1 X157.953 Y163.79 E.03595
G1 X157.953 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X158.976 Y156.21 E-.38954
G1 X158.976 Y157.185 E-.37046
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.586 Y156.599 Z8.28 F60000
G1 X166.664 Y156.593 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.664 Y163.407 E.25885
G1 X166.407 Y163.407 E.00974
G1 X166.407 Y156.593 E.25885
G1 X166.604 Y156.593 E.00746
; COOLING_NODE: 2
M204 S250
G1 X167.047 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11998
M204 S5000
G1 X167.047 Y163.79 E.2663
G1 X166.024 Y163.79 E.03595
G1 X166.024 Y156.21 E.2663
G1 X166.987 Y156.21 E.03385
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X167.003 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.663 Y161.938 Z8.28 F60000
G1 X176.286 Y163.407 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.286 Y156.593 E.25885
G1 X176.542 Y156.593 E.00972
G1 X176.542 Y163.407 E.25885
G1 X176.346 Y163.407 E.00744
; COOLING_NODE: 1
M204 S250
G1 X175.903 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4111
M204 S5000
G1 X175.903 Y156.21 E.2663
G1 X176.925 Y156.21 E.03593
G1 X176.925 Y163.79 E.2663
G1 X175.963 Y163.79 E.03382
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X175.947 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.461 Y157.813 Z8.28 F60000
G1 X184.458 Y156.593 Z8.28
G1 Z7.88
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.714 Y156.593 E.00972
G1 X184.714 Y163.407 E.25885
G1 X184.458 Y163.407 E.00972
G1 X184.458 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X184.075 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4111
M204 S5000
G1 X185.097 Y156.21 E.03593
G1 X185.097 Y163.79 E.2663
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

G1 X184.075 Y163.79 E.03593
G1 X184.075 Y156.27 E.2642
; CHANGE_LAYER
; Z_HEIGHT: 8.12
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X185.097 Y156.21 E-.38929
G1 X185.097 Y157.186 E-.37071
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 34/44
; update layer progress
M73 L34
M991 S0 P33 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z8.28 I-.169 J-1.205 P1  F60000
G1 X140.671 Y163.407 Z8.28
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.406 Y163.407 E.01006
G1 X140.406 Y156.593 E.25885
G1 X140.671 Y156.593 E.01006
G1 X140.671 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.054 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11994
M204 S5000
G1 X140.022 Y163.79 E.03625
G1 X140.022 Y156.21 E.2663
G1 X141.054 Y156.21 E.03625
G1 X141.054 Y163.73 E.2642
; COOLING_NODE: 3
; WIPE_START
G1 F12000
M204 S8000
G1 X140.022 Y163.79 E-.39277
G1 X140.022 Y162.824 E-.36723
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.637 Y163.341 Z8.52 F60000
G1 X148.594 Y163.407 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.329 Y163.407 E.01006
G1 X148.329 Y156.593 E.25885
G1 X148.594 Y156.593 E.01006
G1 X148.594 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X148.978 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11994
M204 S5000
G1 X147.946 Y163.79 E.03625
G1 X147.946 Y156.21 E.2663
G1 X148.978 Y156.21 E.03625
G1 X148.978 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X147.946 Y163.79 E-.39277
G1 X147.946 Y162.824 E-.36723
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.495 Y158.904 Z8.52 F60000
G1 X158.356 Y156.593 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.619 Y156.593 E.01001
G1 X158.619 Y163.407 E.25885
G1 X158.356 Y163.407 E.01001
G1 X158.356 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X157.972 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11994
M204 S5000
G1 X159.003 Y156.21 E.03621
G1 X159.003 Y163.79 E.2663
G1 X157.972 Y163.79 E.03621
G1 X157.972 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X159.003 Y156.21 E-.39228
G1 X159.003 Y157.178 E-.36772
; WIPE_END
M73 P93 R0
G1 E-.04 F1800
M204 S10000
G1 X166.613 Y156.596 Z8.52 F60000
G1 X166.644 Y156.593 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.644 Y163.407 E.25885
G1 X166.381 Y163.407 E.01001
G1 X166.381 Y156.593 E.25885
G1 X166.584 Y156.593 E.00773
; COOLING_NODE: 2
M204 S250
G1 X167.028 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11994
M204 S5000
G1 X167.028 Y163.79 E.2663
G1 X165.997 Y163.79 E.03621
G1 X165.997 Y156.21 E.2663
G1 X166.968 Y156.21 E.0341
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X166.983 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.65 Y161.926 Z8.52 F60000
G1 X176.305 Y163.407 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.305 Y156.593 E.25885
G1 X176.57 Y156.593 E.01005
G1 X176.57 Y163.407 E.25885
G1 X176.365 Y163.407 E.00777
; COOLING_NODE: 1
M204 S250
G1 X175.922 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3964
M204 S5000
G1 X175.922 Y156.21 E.2663
G1 X176.953 Y156.21 E.03624
G1 X176.953 Y163.79 E.2663
G1 X175.982 Y163.79 E.03413
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X175.966 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.47 Y157.797 Z8.52 F60000
G1 X184.43 Y156.593 Z8.52
G1 Z8.12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.695 Y156.593 E.01005
G1 X184.695 Y163.407 E.25885
G1 X184.43 Y163.407 E.01005
G1 X184.43 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X184.047 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3964
M204 S5000
G1 X185.078 Y156.21 E.03624
G1 X185.078 Y163.79 E.2663
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

G1 X184.047 Y163.79 E.03624
G1 X184.047 Y156.27 E.2642
; CHANGE_LAYER
; Z_HEIGHT: 8.36
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X185.078 Y156.21 E-.39261
G1 X185.078 Y157.177 E-.36739
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 35/44
; update layer progress
M73 L35
M991 S0 P34 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z8.52 I-.169 J-1.205 P1  F60000
G1 X140.717 Y163.407 Z8.52
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.438 Y163.407 E.01059
G1 X140.438 Y156.593 E.25885
G1 X140.717 Y156.593 E.01059
G1 X140.717 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.095 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11986
M204 S5000
G1 X140.055 Y163.79 E.03657
G1 X140.055 Y156.21 E.2663
G1 X141.095 Y156.21 E.03657
G1 X141.1 Y156.21 E.00017
G1 X141.1 Y163.735 E.26437
; COOLING_NODE: 3
; WIPE_START
G1 F12000
M204 S8000
G1 X140.055 Y163.79 E-.3979
G1 X140.055 Y162.837 E-.36211
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.67 Y163.347 Z8.76 F60000
G1 X148.562 Y163.407 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.283 Y163.407 E.01059
G1 X148.283 Y156.593 E.25885
G1 X148.562 Y156.593 E.01059
G1 X148.562 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X148.945 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11986
M204 S5000
G1 X147.905 Y163.79 E.03657
G1 X147.9 Y163.79 E.00017
G1 X147.9 Y156.21 E.2663
G1 X147.905 Y156.21 E.00017
G1 X148.945 Y156.21 E.03657
G1 X148.945 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X147.905 Y163.79 E-.39616
G1 X147.9 Y163.79 E-.00184
G1 X147.9 Y162.837 E-.362
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.458 Y158.933 Z8.76 F60000
G1 X158.387 Y156.593 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.666 Y156.593 E.01058
G1 X158.666 Y163.407 E.25885
G1 X158.387 Y163.407 E.01058
G1 X158.387 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X158.004 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11986
M204 S5000
G1 X159.044 Y156.21 E.03653
G1 X159.049 Y156.21 E.00019
G1 X159.049 Y163.79 E.2663
G1 X159.044 Y163.79 E.00019
G1 X158.004 Y163.79 E.03653
G1 X158.004 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X159.044 Y156.21 E-.39581
G1 X159.049 Y156.21 E-.00211
G1 X159.049 Y157.163 E-.36209
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.612 Y156.593 Z8.76 F60000
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.612 Y163.407 E.25885
G1 X166.334 Y163.407 E.01058
G1 X166.334 Y156.593 E.25885
G1 X166.552 Y156.593 E.0083
; COOLING_NODE: 2
M204 S250
G1 X166.996 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11986
M204 S5000
G1 X166.996 Y163.79 E.2663
G1 X165.956 Y163.79 E.03653
G1 X165.951 Y163.79 E.00019
G1 X165.951 Y156.21 E.2663
G1 X165.956 Y156.21 E.00019
G1 X166.936 Y156.21 E.03443
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X166.952 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.629 Y161.907 Z8.76 F60000
G1 X176.337 Y163.407 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.337 Y156.593 E.25885
G1 X176.614 Y156.593 E.01053
G1 X176.614 Y163.407 E.25885
G1 X176.397 Y163.407 E.00825
; COOLING_NODE: 1
M204 S250
G1 X175.953 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3812
M204 S5000
G1 X175.953 Y156.21 E.2663
G1 X176.994 Y156.21 E.03658
G1 X176.997 Y163.79 E.2663
G1 X176.994 Y163.79 E.0001
G1 X176.013 Y163.79 E.03447
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X175.997 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.486 Y157.771 Z8.76 F60000
G1 X184.386 Y156.593 Z8.76
G1 Z8.36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.663 Y156.593 E.01053
G1 X184.663 Y163.407 E.25885
G1 X184.386 Y163.407 E.01053
G1 X184.386 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X184.006 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3812
M204 S5000
G1 X185.047 Y156.21 E.03658
G1 X185.047 Y163.79 E.2663
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

G1 X184.006 Y163.79 E.03658
G1 X184.006 Y156.27 E.2642
; CHANGE_LAYER
; Z_HEIGHT: 8.6
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F12000
M204 S8000
G1 X185.047 Y156.21 E-.39627
G1 X185.047 Y157.167 E-.36373
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 36/44
; update layer progress
M73 L36
M991 S0 P35 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z8.76 I-.17 J-1.205 P1  F60000
G1 X140.783 Y163.407 Z8.76
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.483 Y163.407 E.01139
G1 X140.483 Y156.593 E.25885
G1 X140.783 Y156.593 E.01139
G1 X140.783 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.141 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11968
M204 S5000
G1 X140.099 Y163.79 E.03661
G1 X140.099 Y156.21 E.2663
G1 X141.141 Y156.21 E.03661
G1 X141.166 Y156.21 E.00088
G1 X141.166 Y163.755 E.26507
; COOLING_NODE: 3
; WIPE_START
G1 F12000
M204 S8000
G1 X140.099 Y163.79 E-.40563
G1 X140.099 Y162.857 E-.35438
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.715 Y163.354 Z9 F60000
G1 X148.517 Y163.407 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.217 Y163.407 E.01139
G1 X148.217 Y156.593 E.25885
G1 X148.517 Y156.593 E.01139
G1 X148.517 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X148.901 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11968
M204 S5000
G1 X147.859 Y163.79 E.03661
G1 X147.834 Y163.79 E.00088
G1 X147.834 Y156.21 E.2663
G1 X147.859 Y156.21 E.00088
G1 X148.901 Y156.21 E.03661
G1 X148.901 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X147.859 Y163.79 E-.39659
G1 X147.834 Y163.79 E-.00948
G1 X147.834 Y162.859 E-.35394
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.404 Y158.974 Z9 F60000
G1 X158.432 Y156.593 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.729 Y156.593 E.01131
G1 X158.729 Y163.407 E.25885
G1 X158.432 Y163.407 E.01131
G1 X158.432 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X158.048 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11968
M204 S5000
G1 X159.09 Y156.21 E.03662
G1 X159.113 Y156.21 E.00079
G1 X159.113 Y163.79 E.2663
G1 X159.09 Y163.79 E.00079
G1 X158.048 Y163.79 E.03662
G1 X158.048 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
M73 P94 R0
G1 F12000
M204 S8000
G1 X159.09 Y156.21 E-.39673
G1 X159.113 Y156.21 E-.00855
G1 X159.113 Y157.143 E-.35473
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.568 Y156.593 Z9 F60000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.568 Y163.407 E.25885
G1 X166.271 Y163.407 E.01131
G1 X166.271 Y156.593 E.25885
G1 X166.508 Y156.593 E.00904
; COOLING_NODE: 2
M204 S250
G1 X166.952 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11968
M204 S5000
G1 X166.952 Y163.79 E.2663
G1 X165.91 Y163.79 E.03662
G1 X165.887 Y163.79 E.00079
G1 X165.887 Y156.21 E.2663
G1 X165.91 Y156.21 E.00079
G1 X166.892 Y156.21 E.03451
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X166.908 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.599 Y161.881 Z9 F60000
G1 X176.38 Y163.407 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.38 Y156.593 E.25885
G1 X176.678 Y156.593 E.01131
G1 X176.678 Y163.407 E.25885
G1 X176.44 Y163.407 E.00903
; COOLING_NODE: 1
M204 S250
G1 X175.997 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3658
M204 S5000
G1 X175.997 Y156.21 E.2663
G1 X177.038 Y156.21 E.03658
G1 X177.062 Y156.21 E.00082
G1 X177.062 Y163.79 E.2663
G1 X177.038 Y163.79 E.00082
G1 X176.057 Y163.79 E.03447
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X176.041 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.506 Y157.733 Z9 F60000
G1 X184.322 Y156.593 Z9
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.62 Y156.593 E.01131
G1 X184.62 Y163.407 E.25885
G1 X184.322 Y163.407 E.01131
G1 X184.322 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.962 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3658
M204 S5000
G1 X185.003 Y156.21 E.03658
G1 X185.003 Y163.79 E.2663
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

G1 X183.962 Y163.79 E.03658
G1 X183.938 Y163.79 E.00082
G1 X183.938 Y156.247 E.26501
; CHANGE_LAYER
; Z_HEIGHT: 8.84
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X185.003 Y156.21 E-.40477
G1 X185.003 Y157.145 E-.35524
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 37/44
; update layer progress
M73 L37
M991 S0 P36 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z9 I-.171 J-1.205 P1  F60000
G1 X140.867 Y163.407 Z9
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.54 Y163.407 E.01242
G1 X140.54 Y156.593 E.25885
G1 X140.867 Y156.593 E.01242
G1 X140.867 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.207 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11936
M204 S5000
G1 X140.157 Y163.79 E.03689
G1 X140.157 Y156.21 E.2663
G1 X140.807 Y156.21 E.02284
G1 X141.207 Y156.21 E.01405
G1 F11152.564
G1 X141.251 Y156.21 E.00154
G1 F11010
G1 X141.251 Y163.774 E.26573
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X140.157 Y163.79 E-.41571
G1 X140.157 Y162.884 E-.3443
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.774 Y163.363 Z9.24 F60000
G1 X148.46 Y163.407 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.133 Y163.407 E.01242
G1 X148.133 Y156.593 E.25885
G1 X148.46 Y156.593 E.01242
G1 X148.46 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X148.843 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11936
M204 S5000
G1 X148.193 Y163.79 E.02284
G1 X147.793 Y163.79 E.01405
G1 F11152.596
G1 X147.749 Y163.79 E.00154
G1 F11010
G1 X147.749 Y156.21 E.2663
G1 F11152.596
G1 X147.793 Y156.21 E.00154
G1 F11936
G1 X148.193 Y156.21 E.01405
G1 X148.843 Y156.21 E.02284
G1 X148.843 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X148.193 Y163.79 E-.2481
G1 X147.793 Y163.79 E-.152
G1 X147.749 Y163.79 E-.01661
G1 X147.749 Y162.887 E-.34329
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.334 Y159.028 Z9.24 F60000
G1 X158.489 Y156.593 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.815 Y156.593 E.01239
G1 X158.815 Y163.407 E.25885
G1 X158.489 Y163.407 E.01239
G1 X158.489 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X158.105 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11936
M204 S5000
G1 X158.754 Y156.21 E.0228
G1 X159.154 Y156.21 E.01405
G1 F11153.807
G1 X159.198 Y156.21 E.00155
G1 F11010
G1 X159.198 Y163.79 E.2663
G1 F11153.807
G1 X159.154 Y163.79 E.00155
G1 F11936
G1 X158.754 Y163.79 E.01405
G1 X158.105 Y163.79 E.0228
G1 X158.105 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X158.754 Y156.21 E-.24763
G1 X159.154 Y156.21 E-.152
G1 X159.198 Y156.21 E-.01675
G1 X159.198 Y157.114 E-.34362
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.511 Y156.593 Z9.24 F60000
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.511 Y163.407 E.25885
G1 X166.185 Y163.407 E.01239
G1 X166.185 Y156.593 E.25885
G1 X166.451 Y156.593 E.01011
; COOLING_NODE: 2
M204 S250
G1 X166.895 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11936
M204 S5000
G1 X166.895 Y163.79 E.2663
G1 X166.246 Y163.79 E.0228
G1 X165.846 Y163.79 E.01405
G1 F11153.807
G1 X165.802 Y163.79 E.00155
G1 F11010
G1 X165.802 Y156.21 E.2663
G1 F11153.807
G1 X165.846 Y156.21 E.00155
G1 F11936
G1 X166.246 Y156.21 E.01405
G1 X166.835 Y156.21 E.02069
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X166.851 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.561 Y161.847 Z9.24 F60000
G1 X176.437 Y163.407 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.437 Y156.593 E.25885
G1 X176.76 Y156.593 E.01227
G1 X176.76 Y163.407 E.25885
G1 X176.497 Y163.407 E.00999
; COOLING_NODE: 1
M204 S250
G1 X176.053 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3500
M204 S5000
G1 X176.053 Y156.21 E.2663
G1 X177.102 Y156.21 E.03686
G1 X177.143 Y156.21 E.00144
G1 X177.143 Y163.79 E.2663
G1 X177.102 Y163.79 E.00144
G1 X176.113 Y163.79 E.03475
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X176.098 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.531 Y157.684 Z9.24 F60000
G1 X184.24 Y156.593 Z9.24
G1 Z8.84
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.563 Y156.593 E.01227
G1 X184.563 Y163.407 E.25885
G1 X184.24 Y163.407 E.01227
G1 X184.24 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.897 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3500
M204 S5000
G1 X184.947 Y156.21 E.03686
G1 X184.947 Y163.79 E.2663
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

G1 X183.897 Y163.79 E.03686
G1 X183.857 Y163.79 E.00144
G1 X183.857 Y156.229 E.26563
; CHANGE_LAYER
; Z_HEIGHT: 9.08
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X184.947 Y156.21 E-.41425
G1 X184.947 Y157.12 E-.34575
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 38/44
; update layer progress
M73 L38
M991 S0 P37 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z9.24 I-.172 J-1.205 P1  F60000
G1 X140.976 Y163.407 Z9.24
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.612 Y163.407 E.01384
G1 X140.612 Y156.593 E.25885
G1 X140.976 Y156.593 E.01384
G1 X140.976 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.292 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11883
M204 S5000
G1 X140.228 Y163.79 E.03737
G1 X140.228 Y157.01 E.2382
G1 X140.228 Y156.61 E.01405
G1 F11596.64
G1 X140.228 Y156.21 E.01405
G1 F10300.407
G1 X140.492 Y156.21 E.00926
G1 F9488.112
G1 X140.892 Y156.21 E.01405
G1 F8319.294
G1 X141.292 Y156.21 E.01405
G1 F7227.277
G1 X141.36 Y156.21 E.00238
G1 F7050
G1 X141.36 Y163.79 E.2663
G1 F7070.098
G1 X141.352 Y163.79 E.00027
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X140.228 Y163.79 E-.42698
G1 X140.228 Y162.914 E-.33302
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.847 Y163.374 Z9.48 F60000
G1 X148.388 Y163.407 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X148.024 Y163.407 E.01384
G1 X148.024 Y156.593 E.25885
G1 X148.388 Y156.593 E.01384
G1 X148.388 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X148.772 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10300.407
M204 S5000
G1 X148.508 Y163.79 E.00926
G1 F9488.142
G1 X148.108 Y163.79 E.01405
G1 F8319.322
G1 X147.708 Y163.79 E.01405
G1 F7227.303
G1 X147.64 Y163.79 E.00238
G1 F7050
G1 X147.64 Y156.21 E.2663
G1 F7227.303
G1 X147.708 Y156.21 E.00238
G1 F8319.322
G1 X148.108 Y156.21 E.01405
G1 F9488.142
G1 X148.508 Y156.21 E.01405
G1 F10300.407
G1 X148.772 Y156.21 E.00926
G1 F11596.64
G1 X148.772 Y156.61 E.01405
G1 F11883
G1 X148.772 Y157.01 E.01405
G1 X148.772 Y163.73 E.23609
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X148.508 Y163.79 E-.10273
G1 X148.108 Y163.79 E-.152
G1 X147.708 Y163.79 E-.152
G1 X147.64 Y163.79 E-.02574
G1 X147.64 Y162.928 E-.32753
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.242 Y159.098 Z9.48 F60000
G1 X158.559 Y156.593 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X158.919 Y156.593 E.01371
G1 X158.919 Y163.407 E.25885
G1 X158.559 Y163.407 E.01371
G1 X158.559 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X158.175 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P95 R0
G1 F11478.685
M204 S5000
G1 X158.439 Y156.21 E.00927
G1 F10619.269
G1 X158.839 Y156.21 E.01405
G1 F9380.516
G1 X159.239 Y156.21 E.01405
G1 F8218.563
G1 X159.303 Y156.21 E.00225
G1 F8040
G1 X159.303 Y163.79 E.2663
G1 F8218.563
G1 X159.239 Y163.79 E.00225
G1 F9380.516
G1 X158.839 Y163.79 E.01405
G1 F10619.269
G1 X158.439 Y163.79 E.01405
G1 F11478.685
G1 X158.175 Y163.79 E.00927
G1 F11883
G1 X158.175 Y163.39 E.01405
G1 X158.175 Y156.27 E.25014
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X158.439 Y156.21 E-.10285
G1 X158.839 Y156.21 E-.152
G1 X159.239 Y156.21 E-.152
G1 X159.303 Y156.21 E-.02429
G1 X159.303 Y157.075 E-.32886
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.441 Y156.593 Z9.48 F60000
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.441 Y163.407 E.25885
G1 X166.081 Y163.407 E.01371
G1 X166.081 Y156.593 E.25885
G1 X166.381 Y156.593 E.01143
; COOLING_NODE: 2
M204 S250
G1 X166.825 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11883
M204 S5000
G1 X166.825 Y163.39 E.25225
G1 X166.825 Y163.79 E.01405
G1 F11478.685
G1 X166.561 Y163.79 E.00927
G1 F10619.269
G1 X166.161 Y163.79 E.01405
G1 F9380.516
G1 X165.761 Y163.79 E.01405
G1 F8218.563
G1 X165.697 Y163.79 E.00225
G1 F8040
G1 X165.697 Y156.21 E.2663
G1 F8218.563
G1 X165.761 Y156.21 E.00225
G1 F9380.516
G1 X166.161 Y156.21 E.01405
G1 F10619.269
G1 X166.561 Y156.21 E.01405
G1 F11280.375
G1 X166.765 Y156.21 E.00716
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X166.782 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.513 Y161.807 Z9.48 F60000
G1 X176.507 Y163.407 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.507 Y156.593 E.25885
G1 X176.865 Y156.593 E.01361
G1 X176.865 Y163.407 E.25885
G1 X176.567 Y163.407 E.01133
; COOLING_NODE: 1
M204 S250
G1 X176.123 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3341
M204 S5000
G1 X176.123 Y156.61 E.25225
G1 X176.123 Y156.21 E.01405
G1 X176.384 Y156.21 E.00918
G1 X176.784 Y156.21 E.01405
G1 X177.184 Y156.21 E.01405
G1 X177.248 Y156.21 E.00224
G1 X177.248 Y163.79 E.2663
G1 X177.184 Y163.79 E.00224
G1 X176.784 Y163.79 E.01405
G1 X176.384 Y163.79 E.01405
G1 X176.183 Y163.79 E.00707
; COOLING_NODE: 1
; WIPE_START
G1 F11271.623
M204 S8000
G1 X176.166 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.56 Y157.621 Z9.48 F60000
G1 X184.135 Y156.593 Z9.48
G1 Z9.08
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.493 Y156.593 E.01361
G1 X184.493 Y163.407 E.25885
G1 X184.135 Y163.407 E.01361
G1 X184.135 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.816 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3341
M204 S5000
G1 X184.877 Y156.21 E.03729
G1 X184.877 Y163.39 E.25225
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

G1 X184.877 Y163.79 E.01405
G1 X184.616 Y163.79 E.00918
G1 X184.216 Y163.79 E.01405
G1 X183.816 Y163.79 E.01405
G1 X183.752 Y163.79 E.00224
G1 X183.752 Y156.21 E.2663
G1 X183.756 Y156.21 E.00014
; CHANGE_LAYER
; Z_HEIGHT: 9.32
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F8050.839
M204 S8000
G1 X184.877 Y156.21 E-.42609
G1 X184.877 Y157.089 E-.33391
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 39/44
; update layer progress
M73 L39
M991 S0 P38 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z9.48 I-.174 J-1.204 P1  F60000
G1 X141.105 Y163.407 Z9.48
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.697 Y163.407 E.0155
G1 X140.697 Y156.593 E.25885
G1 X141.105 Y156.593 E.0155
G1 X141.105 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.401 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11803
M204 S5000
G1 X140.313 Y163.79 E.03819
G1 X140.313 Y158.61 E.18199
G1 X140.313 Y158.21 E.01405
G1 F10977.274
G1 X140.313 Y157.81 E.01405
G1 F9717.172
G1 X140.313 Y157.41 E.01405
G1 F8533.869
G1 X140.313 Y157.01 E.01405
G1 F7427.366
G1 X140.313 Y156.61 E.01405
G1 F6397.663
G1 X140.313 Y156.21 E.01405
G1 F5444.761
G1 X140.601 Y156.21 E.01008
G1 F4808.288
G1 X141.001 Y156.21 E.01405
G1 F3987.297
G1 X141.401 Y156.21 E.01405
G1 F3243.105
G1 X141.488 Y156.21 E.00309
G1 F3090
G1 X141.488 Y163.79 E.2663
G1 F3138.101
G1 X141.461 Y163.79 E.00098
; COOLING_NODE: 3
; WIPE_START
M204 S8000
G1 X140.313 Y163.79 E-.43588
G1 X140.313 Y162.937 E-.32412
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.933 Y163.385 Z9.72 F60000
G1 X148.303 Y163.407 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X147.895 Y163.407 E.0155
G1 X147.895 Y156.593 E.25885
G1 X148.303 Y156.593 E.0155
G1 X148.303 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X148.687 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5444.761
M204 S5000
G1 X148.399 Y163.79 E.01008
G1 F4808.309
G1 X147.999 Y163.79 E.01405
G1 F3987.316
G1 X147.599 Y163.79 E.01405
G1 F3243.123
G1 X147.512 Y163.79 E.00309
G1 F3090
G1 X147.512 Y156.21 E.2663
G1 F3243.123
G1 X147.599 Y156.21 E.00309
G1 F3987.316
G1 X147.999 Y156.21 E.01405
G1 F4808.309
G1 X148.399 Y156.21 E.01405
G1 F5444.761
G1 X148.687 Y156.21 E.01008
G1 F6397.663
G1 X148.687 Y156.61 E.01405
G1 F7427.366
G1 X148.687 Y157.01 E.01405
G1 F8533.869
G1 X148.687 Y157.41 E.01405
G1 F9717.172
G1 X148.687 Y157.81 E.01405
G1 F10977.274
G1 X148.687 Y158.21 E.01405
G1 F11803
G1 X148.687 Y158.61 E.01405
G1 X148.687 Y163.73 E.17988
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X148.399 Y163.79 E-.11143
G1 X147.999 Y163.79 E-.152
G1 X147.599 Y163.79 E-.152
G1 X147.512 Y163.79 E-.03338
G1 X147.512 Y162.971 E-.3112
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.134 Y159.177 Z9.72 F60000
G1 X158.642 Y156.593 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.05 Y156.593 E.01549
G1 X159.05 Y163.407 E.25885
G1 X158.642 Y163.407 E.01549
G1 X158.642 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X158.259 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5444.098
M204 S5000
G1 X158.544 Y156.21 E.01002
G1 F4811.919
G1 X158.944 Y156.21 E.01405
G1 F3990.604
G1 X159.344 Y156.21 E.01405
G1 F3246.088
G1 X159.433 Y156.21 E.00314
G1 F3090
G1 X159.433 Y163.79 E.2663
G1 F3246.088
G1 X159.344 Y163.79 E.00314
G1 F3990.604
G1 X158.944 Y163.79 E.01405
G1 F4811.919
G1 X158.544 Y163.79 E.01405
G1 F5444.12
G1 X158.259 Y163.79 E.01002
G1 F6396.969
G1 X158.259 Y163.39 E.01405
G1 F7426.618
G1 X158.259 Y162.99 E.01405
G1 F8533.067
G1 X158.259 Y162.59 E.01405
G1 F9716.316
G1 X158.259 Y162.19 E.01405
G1 F10976.365
G1 X158.259 Y161.79 E.01405
G1 F11803
G1 X158.259 Y161.39 E.01405
G1 X158.259 Y156.27 E.17988
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X158.544 Y156.21 E-.1107
G1 X158.944 Y156.21 E-.152
G1 X159.344 Y156.21 E-.152
G1 X159.433 Y156.21 E-.03401
G1 X159.433 Y157.029 E-.31129
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.358 Y156.593 Z9.72 F60000
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.358 Y163.407 E.25885
G1 X165.95 Y163.407 E.01549
G1 X165.95 Y156.593 E.25885
G1 X166.298 Y156.593 E.01321
; COOLING_NODE: 2
M204 S250
G1 X166.741 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11803
M204 S5000
G1 X166.741 Y161.39 E.18199
G1 X166.741 Y161.79 E.01405
G1 F10976.365
G1 X166.741 Y162.19 E.01405
G1 F9716.316
G1 X166.741 Y162.59 E.01405
G1 F8533.067
G1 X166.741 Y162.99 E.01405
G1 F7426.618
G1 X166.741 Y163.39 E.01405
G1 F6396.969
G1 X166.741 Y163.79 E.01405
G1 F5444.12
G1 X166.456 Y163.79 E.01002
G1 F4811.919
G1 X166.056 Y163.79 E.01405
G1 F3990.604
G1 X165.656 Y163.79 E.01405
G1 F3246.088
G1 X165.567 Y163.79 E.00314
G1 F3090
G1 X165.567 Y156.21 E.2663
G1 F3246.088
G1 X165.656 Y156.21 E.00314
G1 F3990.604
G1 X166.056 Y156.21 E.01405
G1 F4811.919
G1 X166.456 Y156.21 E.01405
G1 F5307.795
G1 X166.681 Y156.21 E.00791
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X166.704 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.46 Y161.761 Z9.72 F60000
G1 X176.59 Y163.407 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.59 Y156.593 E.25885
G1 X176.991 Y156.593 E.01525
G1 X176.991 Y163.407 E.25885
G1 X176.65 Y163.407 E.01297
; COOLING_NODE: 1
M204 S250
G1 X176.207 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3178
M204 S5000
G1 X176.207 Y158.21 E.19604
G1 X176.207 Y157.81 E.01405
G1 X176.207 Y157.41 E.01405
G1 X176.207 Y157.01 E.01405
G1 X176.207 Y156.61 E.01405
G1 X176.207 Y156.21 E.01405
G1 X176.489 Y156.21 E.00993
G1 X176.889 Y156.21 E.01405
G1 X177.289 Y156.21 E.01405
G1 X177.375 Y156.21 E.00301
G1 X177.375 Y163.79 E.2663
G1 X177.289 Y163.79 E.00301
G1 X176.889 Y163.79 E.01405
G1 X176.489 Y163.79 E.01405
G1 X176.267 Y163.79 E.00783
; COOLING_NODE: 1
; WIPE_START
G1 F6568.652
M204 S8000
G1 X176.245 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.588 Y157.545 Z9.72 F60000
G1 X184.009 Y156.593 Z9.72
G1 Z9.32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.41 Y156.593 E.01525
G1 X184.41 Y163.407 E.25885
G1 X184.009 Y163.407 E.01525
G1 X184.009 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.711 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3178
M204 S5000
G1 X184.793 Y156.21 E.03804
G1 X184.793 Y161.79 E.19604
G1 X184.793 Y162.19 E.01405
G1 X184.793 Y162.59 E.01405
G1 X184.793 Y162.99 E.01405
G1 X184.793 Y163.39 E.01405
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

G1 X184.793 Y163.79 E.01405
G1 X184.511 Y163.79 E.00994
G1 X184.111 Y163.79 E.01405
G1 X183.711 Y163.79 E.01405
G1 X183.625 Y163.79 E.00301
G1 X183.625 Y156.21 E.2663
G1 X183.651 Y156.21 E.0009
; CHANGE_LAYER
; Z_HEIGHT: 9.56
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F4130.961
M204 S8000
G1 X184.793 Y156.21 E-.43426
G1 X184.793 Y157.067 E-.32574
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 40/44
; update layer progress
M73 L40
M991 S0 P39 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z9.72 I-.175 J-1.204 P1  F60000
G1 X141.177 Y163.407 Z9.72
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.797 Y163.407 E.01442
G1 X140.797 Y156.593 E.25885
G1 X141.177 Y156.593 E.01442
G1 X141.177 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.529 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11695
M204 S5000
G1 X140.414 Y163.79 E.0392
G1 X140.414 Y156.21 E.2663
G1 X141.529 Y156.21 E.0392
G1 X141.56 Y156.21 E.00108
G1 X141.56 Y163.761 E.26527
; COOLING_NODE: 3
; WIPE_START
G1 F12000
M204 S8000
G1 X140.414 Y163.79 E-.43578
G1 X140.414 Y162.937 E-.32422
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.032 Y163.396 Z9.96 F60000
G1 X148.203 Y163.407 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X147.823 Y163.407 E.01442
M73 P96 R0
G1 X147.823 Y156.593 E.25885
G1 X148.203 Y156.593 E.01442
G1 X148.203 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X148.586 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11695
M204 S5000
G1 X147.471 Y163.79 E.0392
G1 X147.44 Y163.79 E.00108
G1 X147.44 Y156.21 E.2663
G1 X147.471 Y156.21 E.00108
G1 X148.586 Y156.21 E.0392
G1 X148.586 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X147.471 Y163.79 E-.42459
G1 X147.44 Y163.79 E-.01166
G1 X147.44 Y162.938 E-.32375
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.095 Y159.202 Z9.96 F60000
G1 X158.742 Y156.593 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.159 Y156.593 E.01584
G1 X159.159 Y163.407 E.25885
G1 X158.742 Y163.407 E.01584
G1 X158.742 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X158.358 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10465.969
M204 S5000
G1 X158.674 Y156.21 E.0111
G1 F9488.081
G1 X159.074 Y156.21 E.01405
G1 F8319.266
G1 X159.474 Y156.21 E.01405
G1 F7227.25
G1 X159.542 Y156.21 E.00238
G1 F7050
G1 X159.542 Y163.79 E.2663
G1 F7227.25
G1 X159.474 Y163.79 E.00238
G1 F8319.266
G1 X159.074 Y163.79 E.01405
G1 F9488.081
G1 X158.674 Y163.79 E.01405
G1 F10465.969
G1 X158.358 Y163.79 E.0111
G1 F11695
G1 X158.358 Y163.39 E.01405
G1 X158.358 Y162.99 E.01405
G1 X158.358 Y156.27 E.23609
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X158.674 Y156.21 E-.12225
G1 X159.074 Y156.21 E-.152
G1 X159.474 Y156.21 E-.152
G1 X159.542 Y156.21 E-.02573
G1 X159.542 Y157.021 E-.30802
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.258 Y156.593 Z9.96 F60000
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.258 Y163.407 E.25885
G1 X165.841 Y163.407 E.01584
G1 X165.841 Y156.593 E.25885
G1 X166.198 Y156.593 E.01356
; COOLING_NODE: 2
M204 S250
G1 X166.642 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11695
M204 S5000
G1 X166.642 Y162.99 E.2382
G1 X166.642 Y163.39 E.01405
G1 X166.642 Y163.79 E.01405
G1 F10465.969
G1 X166.326 Y163.79 E.0111
G1 F9488.081
G1 X165.926 Y163.79 E.01405
G1 F8319.266
G1 X165.526 Y163.79 E.01405
G1 F7227.25
G1 X165.458 Y163.79 E.00238
G1 F7050
G1 X165.458 Y156.21 E.2663
G1 F7227.25
G1 X165.526 Y156.21 E.00238
G1 F8319.266
G1 X165.926 Y156.21 E.01405
G1 F9488.081
G1 X166.326 Y156.21 E.01405
G1 F10276.648
G1 X166.582 Y156.21 E.009
; COOLING_NODE: 1
; WIPE_START
M204 S8000
G1 X166.599 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.384 Y161.705 Z9.96 F60000
G1 X176.688 Y163.407 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.688 Y156.593 E.25885
G1 X177.127 Y156.593 E.01669
G1 X177.127 Y163.407 E.25885
G1 X176.748 Y163.407 E.01441
; COOLING_NODE: 1
M204 S250
G1 X176.304 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3014
M204 S5000
G1 X176.304 Y159.41 E.15388
G1 X176.304 Y159.01 E.01405
G1 X176.304 Y158.61 E.01405
G1 X176.304 Y158.21 E.01405
G1 X176.304 Y157.81 E.01405
G1 X176.304 Y157.41 E.01405
G1 X176.304 Y157.01 E.01405
G1 X176.304 Y156.61 E.01405
G1 X176.304 Y156.21 E.01405
G1 X176.616 Y156.21 E.01095
G1 X177.016 Y156.21 E.01405
G1 F2861.156
G1 X177.416 Y156.21 E.01405
G1 F2236.628
G1 X177.511 Y156.21 E.00333
G1 F2100
G1 X177.511 Y163.79 E.2663
G1 F2236.628
G1 X177.416 Y163.79 E.00333
G1 F2861.156
G1 X177.016 Y163.79 E.01405
G1 F3014
G1 X176.616 Y163.79 E.01405
G1 X176.364 Y163.79 E.00884
; COOLING_NODE: 1
; WIPE_START
G1 F4043.044
M204 S8000
G1 X176.337 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.62 Y157.457 Z9.96 F60000
G1 X183.873 Y156.593 Z9.96
G1 Z9.56
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.312 Y156.593 E.01669
G1 X184.312 Y163.407 E.25885
G1 X183.873 Y163.407 E.01669
G1 X183.873 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.584 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3014
M204 S5000
G1 X184.696 Y156.21 E.03905
G1 X184.696 Y160.59 E.15388
G1 X184.696 Y160.99 E.01405
G1 X184.696 Y161.39 E.01405
G1 X184.696 Y161.79 E.01405
G1 X184.696 Y162.19 E.01405
G1 X184.696 Y162.59 E.01405
G1 X184.696 Y162.99 E.01405
G1 X184.696 Y163.39 E.01405
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

G1 X184.696 Y163.79 E.01405
G1 X184.384 Y163.79 E.01095
G1 X183.984 Y163.79 E.01405
G1 F2861.139
G1 X183.584 Y163.79 E.01405
G1 F2236.613
G1 X183.489 Y163.79 E.00333
G1 F2100
G1 X183.489 Y156.21 E.2663
G1 F2149.558
G1 X183.524 Y156.21 E.00122
; CHANGE_LAYER
; Z_HEIGHT: 9.8
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F2149.558
M204 S8000
G1 X184.696 Y156.21 E-.44523
G1 X184.696 Y157.038 E-.31477
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 41/44
; update layer progress
M73 L41
M991 S0 P40 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z9.96 I-.176 J-1.204 P1  F60000
G1 X141.164 Y163.407 Z9.96
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X140.913 Y163.407 E.00954
G1 X140.913 Y156.593 E.25885
G1 X141.164 Y156.593 E.00954
G1 X141.164 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X141.548 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11567
M204 S5000
G1 X140.529 Y163.79 E.03577
G1 X140.529 Y156.21 E.2663
G1 X141.548 Y156.21 E.03577
G1 X141.548 Y163.73 E.2642
; COOLING_NODE: 3
; WIPE_START
G1 F12000
M204 S8000
G1 X140.529 Y163.79 E-.38756
G1 X140.529 Y162.81 E-.37245
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X148.087 Y163.407 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X147.836 Y163.407 E.00954
G1 X147.836 Y156.593 E.25885
G1 X148.087 Y156.593 E.00954
G1 X148.087 Y163.347 E.25657
; COOLING_NODE: 3
M204 S250
G1 X148.471 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11567
M204 S5000
G1 X147.452 Y163.79 E.03577
G1 X147.452 Y156.21 E.2663
G1 X148.471 Y156.21 E.03577
G1 X148.471 Y163.73 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X147.452 Y163.79 E-.38756
G1 X147.452 Y162.81 E-.37245
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X154.154 Y159.157 Z10.2 F60000
G1 X158.858 Y156.593 Z10.2
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X159.179 Y156.593 E.0122
G1 X159.179 Y163.407 E.25885
G1 X158.858 Y163.407 E.0122
G1 X158.858 Y156.653 E.25657
; COOLING_NODE: 2
M204 S250
G1 X158.474 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11567
M204 S5000
G1 X159.562 Y156.21 E.03823
G1 X159.562 Y163.79 E.2663
G1 X158.474 Y163.79 E.03823
G1 X158.474 Y156.27 E.2642
; COOLING_NODE: 2
; WIPE_START
G1 F12000
M204 S8000
G1 X159.562 Y156.21 E-.41412
G1 X159.562 Y157.12 E-.34588
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X166.142 Y156.593 Z10.2 F60000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X166.142 Y163.407 E.25885
G1 X165.821 Y163.407 E.0122
G1 X165.821 Y156.593 E.25885
G1 X166.082 Y156.593 E.00992
; COOLING_NODE: 2
M204 S250
G1 X166.526 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11567
M204 S5000
G1 X166.526 Y163.79 E.2663
G1 X165.438 Y163.79 E.03823
G1 X165.438 Y156.21 E.2663
G1 X166.466 Y156.21 E.03612
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X166.482 Y158.21 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.299 Y161.643 Z10.2 F60000
G1 X176.801 Y163.407 Z10.2
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X176.801 Y156.593 E.25885
G1 X177.181 Y156.593 E.01442
G1 X177.181 Y163.407 E.25885
G1 X176.861 Y163.407 E.01214
; COOLING_NODE: 1
M204 S250
G1 X176.417 Y163.79 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2849
M204 S5000
G1 X176.417 Y156.21 E.2663
G1 X177.552 Y156.21 E.03985
G1 X177.564 Y156.21 E.00043
G1 X177.564 Y163.79 E.2663
G1 X177.552 Y163.79 E.00043
G1 X176.477 Y163.79 E.03774
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X176.462 Y161.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X182.696 Y157.387 Z10.2 F60000
G1 X183.82 Y156.593 Z10.2
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F11292.473
M204 S8000
G1 X184.199 Y156.593 E.01442
G1 X184.199 Y163.407 E.25885
G1 X183.82 Y163.407 E.01442
G1 X183.82 Y156.653 E.25657
; COOLING_NODE: 1
M204 S250
G1 X183.448 Y156.21 F60000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2849
M204 S5000
G1 X184.583 Y156.21 E.03985
G1 X184.583 Y163.79 E.2663
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

G1 X183.448 Y163.79 E.03985
G1 X183.436 Y163.79 E.00043
G1 X183.436 Y156.258 E.26463
; CHANGE_LAYER
; Z_HEIGHT: 10.04
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F12000
M204 S8000
G1 X184.583 Y156.21 E-.43606
G1 X184.583 Y157.062 E-.32394
; WIPE_END
M73 P97 R0
G1 E-.04 F1800
; layer num/total_layer_count: 42/44
; update layer progress
M73 L42
M991 S0 P41 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 3
M204 S10000
G17
G3 Z10.2 I-.188 J-1.202 P1  F60000
G1 X141.445 Y163.79 Z10.2
G1 Z10.04
G1 E.8 F1800
G1 F11435
M204 S5000
G1 X140.664 Y163.79 E.02743
G1 X140.664 Y156.21 E.2663
G1 X141.445 Y156.21 E.02743
G1 X141.445 Y163.73 E.2642
M204 S10000
G1 X141.055 Y163.598 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.448844
G1 F11325.314
M204 S8000
G1 X141.055 Y156.402 E.27262
; COOLING_NODE: 3
; WIPE_START
G1 X141.055 Y158.402 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X147.19 Y162.942 Z10.44 F60000
G1 X148.335 Y163.79 Z10.44
G1 Z10.04
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11435
M204 S5000
G1 X147.555 Y163.79 E.02743
G1 X147.555 Y156.21 E.2663
G1 X148.335 Y156.21 E.02743
G1 X148.335 Y163.73 E.2642
M204 S10000
G1 X147.945 Y163.598 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.448844
G1 F11325.314
M204 S8000
G1 X147.945 Y156.402 E.27262
; COOLING_NODE: 2
; WIPE_START
G1 X147.945 Y158.402 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X155.421 Y156.865 Z10.44 F60000
G1 X158.607 Y156.21 Z10.44
G1 Z10.04
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11435
M204 S5000
G1 X159.499 Y156.21 E.03136
G1 X159.499 Y163.79 E.2663
G1 X158.607 Y163.79 E.03136
G1 X158.607 Y156.27 E.2642
M204 S10000
G1 X159.053 Y156.402 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560614
G1 F8838.955
M204 S8000
G1 X159.053 Y163.598 E.34931
; COOLING_NODE: 2
; WIPE_START
G1 X159.053 Y161.598 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X165.206 Y157.082 Z10.44 F60000
G1 X166.393 Y156.21 Z10.44
G1 Z10.04
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11435
M204 S5000
G1 X166.393 Y163.79 E.2663
G1 X165.501 Y163.79 E.03136
G1 X165.501 Y156.21 E.2663
G1 X166.333 Y156.21 E.02925
M204 S10000
G1 X165.947 Y156.402 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560614
G1 F8838.955
M204 S8000
G1 X165.947 Y163.598 E.34931
; COOLING_NODE: 1
; WIPE_START
G1 X165.947 Y161.598 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X173.421 Y163.144 Z10.44 F60000
G1 X176.548 Y163.79 Z10.44
G1 Z10.04
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2688
M204 S5000
G1 X176.548 Y156.21 E.2663
G1 X177.535 Y156.21 E.03467
G1 X177.535 Y163.79 E.2663
G1 X176.608 Y163.79 E.03257
M204 S10000
G1 X177.041 Y163.598 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.654974
G1 F7456.875
M204 S8000
M73 P98 R0
G1 X177.041 Y156.402 E.41405
; COOLING_NODE: 1
; WIPE_START
G1 X177.041 Y158.402 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X183.465 Y156.21 Z10.44 F60000
G1 Z10.04
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2688
M204 S5000
G1 X184.452 Y156.21 E.03467
G1 X184.452 Y163.79 E.2663
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

G1 X183.465 Y163.79 E.03467
G1 X183.465 Y156.27 E.2642
M204 S10000
G1 X183.959 Y156.402 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.654974
G1 F7456.875
M204 S8000
G1 X183.959 Y163.598 E.41405
; CHANGE_LAYER
; Z_HEIGHT: 10.28
; LAYER_HEIGHT: 0.24
; WIPE_START
G1 F7456.875
G1 X183.959 Y161.598 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 43/44
; update layer progress
M73 L43
M991 S0 P42 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 1
M204 S10000
G17
G3 Z10.44 I1.214 J-.083 P1  F60000
G1 X183.59 Y156.21 Z10.44
G1 Z10.28
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2540
M204 S5000
G1 X184.3 Y156.21 E.02494
G1 X184.3 Y163.79 E.2663
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

G1 X183.59 Y163.79 E.02494
G1 X183.59 Y156.27 E.2642
M204 S10000
G1 X183.945 Y156.402 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.378004
G1 F11167
M204 S8000
G1 X183.945 Y163.598 E.22402
; COOLING_NODE: 1
; WIPE_START
G1 F13782.542
G1 X183.945 Y161.598 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X176.7 Y163.79 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2540
M204 S5000
G1 X176.7 Y156.21 E.2663
G1 X177.41 Y156.21 E.02494
G1 X177.41 Y163.79 E.2663
G1 X176.76 Y163.79 E.02284
M204 S10000
G1 X177.055 Y163.598 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.378004
G1 F11167
M204 S8000
G1 X177.055 Y156.402 E.22402
; COOLING_NODE: 2
; WIPE_START
G1 F13782.542
G1 X177.055 Y158.402 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X169.574 Y156.89 Z10.68 F60000
G1 X166.211 Y156.21 Z10.68
G1 Z10.28
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11167
M204 S5000
G1 X166.211 Y163.79 E.2663
G1 X165.679 Y163.79 E.01869
G1 X165.679 Y156.21 E.2663
G1 X166.151 Y156.21 E.01659
M204 S10000
G1 X165.945 Y156.402 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.200114
G1 F11167
M204 S8000
G1 X165.945 Y163.598 E.10196
; COOLING_NODE: 2
; WIPE_START
G1 F15000
G1 X165.945 Y161.598 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X159.848 Y157.007 Z10.68 F60000
G1 X158.789 Y156.21 Z10.68
G1 Z10.28
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11167
M204 S5000
G1 X159.321 Y156.21 E.01869
G1 X159.321 Y163.79 E.2663
G1 X158.789 Y163.79 E.01869
G1 X158.789 Y156.27 E.2642
M204 S10000
G1 X159.055 Y156.402 F60000
; FEATURE: Gap infill
; LINE_WIDTH: 0.200114
G1 F11167
M204 S8000
G1 X159.055 Y163.598 E.10196
; COOLING_NODE: 3
; WIPE_START
G1 F15000
G1 X159.055 Y161.598 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X151.573 Y163.108 Z10.68 F60000
G1 X148.09 Y163.81 Z10.68
G1 Z10.28
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.379456
G1 F11167
M204 S5000
G1 X147.8 Y163.81 E.00908
G1 X147.8 Y156.19 E.23827
G1 X148.09 Y156.19 E.00908
G1 X148.09 Y163.75 E.2364
; COOLING_NODE: 3
; WIPE_START
G1 F12000
M204 S8000
G1 X147.8 Y163.81 E-.11274
G1 X147.8 Y162.107 E-.64726
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X141.2 Y163.81 Z10.68 F60000
G1 Z10.28
G1 E.8 F1800
G1 F11167
M204 S5000
G1 X140.91 Y163.81 E.00908
G1 X140.91 Y156.19 E.23827
G1 X141.2 Y156.19 E.00908
G1 X141.2 Y163.75 E.2364
; CHANGE_LAYER
; Z_HEIGHT: 10.52
; LAYER_HEIGHT: 0.240001
; WIPE_START
G1 F12000
M204 S8000
G1 X140.91 Y163.81 E-.11274
G1 X140.91 Y162.107 E-.64726
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 44/44
; update layer progress
M73 L44
M991 S0 P43 ;notify layer change
; OBJECT_ID: 1901
; COOLING_NODE: 1
M204 S10000
G17
G3 Z10.68 I.166 J1.206 P1  F60000
G1 X183.917 Y156.19 Z10.68
G1 Z10.52
G1 E.8 F1800
G1 F2240
M204 S5000
G1 X183.973 Y156.19 E.00175
G1 X183.973 Y163.81 E.23827
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

G1 X183.917 Y163.81 E.00175
G1 X183.917 Y156.25 E.2364
; COOLING_NODE: 1
; WIPE_START
G1 F12000
M204 S8000
G1 X183.973 Y156.19 E-.03117
G1 X183.973 Y158.108 E-.72884
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X178.074 Y162.951 Z10.92 F60000
G1 X177.027 Y163.81 Z10.92
G1 Z10.52
G1 E.8 F1800
G1 F2240
M204 S5000
G1 X177.027 Y156.19 E.23827
G1 X177.083 Y156.19 E.00175
G1 X177.083 Y163.806 E.23814
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F12000
M204 S8000
G1 X177.068 Y161.806 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z10.92 I1.217 J0 P1  F60000
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
G1 Z10.92 F900 ; lower z a little
M1002 judge_flag timelapse_record_flag
M622 J1
    G150.3
    M400 ; wait all motion done
    M991 S0 P-1 ;end smooth timelapse at safe pos
    M400 S5 ;wait for last picture to be taken
M623  ;end of "timelapse_record_flag"

G90
G1 Z20.52 F900 ; lower z a little

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

    
        G1 Z105.26 F600
        G1 Z103.26
    

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

