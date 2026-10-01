; HEADER_BLOCK_START
; H2C left fixed 0.4 mm PET-GF purge-and-wipe maintenance v1
; No printable geometry. Explicit chute purge: 45 mm filament at 280 C.
; Source: BambuStudio 02.08.02.61 native H2C job; details in source.json.
; model printing time: 0s; total estimated time: 6m
; total layer number: 0
; total filament length [mm] : 45.00
; total filament volume [cm^3] : 0.10824
; total filament weight [g] : 0.14
; filament_density: 1.29
; filament_diameter: 1.75
; max_z_height: 0
; filament: 1
; HEADER_BLOCK_END

; EXECUTABLE_BLOCK_START
M73 P0 R6
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
    M140 S0 ; maintenance: no bed heating

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

M73 P60 R2



    G150.3
    M106 P1 S0
    M400 S2
    M109 S280 ; wait tmpr to extrude
    M83
    
        G1 E45 F449.008
    
    G1 E-3 F1800
    M400 P500
    G150.2
    G150.1


G91
G1 Y-16 F12000 ; move away from the trash bin
G90

M400
;M73 P99

;===== wipe right nozzle start =====

M1002 gcode_claim_action : 14
    G150 T265
    
M106 S255 ; turn on fan to cool the nozzle

;===== wipe left nozzle end =====

;===== maintenance cleanup (no model, no unload) =====
M400
M73 P95 R0
M1003 S0
G392 S0
M993 A0 B0 C0
G92 E0
M211 X1 Y1 Z1
M640.2 R0
G90
G150.3
M400
M1002 judge_flag timelapse_record_flag
M622 J1
    M991 S0 P-1
    M400 S5
M623
M104 S0 T0
M104 S0 T1
M141 S0
M140 S0
M106 S0
M106 P2 S0
M106 P3 S0
M106 P9 S0
G29.2 S1
M220 S100
M201.2 K1.0
M73.2 R1.0
M1002 set_gcode_claim_speed_level : 0
M1002 gcode_claim_action : 0
M400
M18
M73 P100 R0
; EXECUTABLE_BLOCK_END
