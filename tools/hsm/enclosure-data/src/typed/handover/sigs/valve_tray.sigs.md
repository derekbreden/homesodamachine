# valve_tray: observed signatures (8 live compiled functions)

## _source  (python _source:74; compiled line 261)
- returns: D{wall:F,socket_floor_z:F,socket_radius:F,seat_half_y:F,seat_top_z:F,port_air:F,corner_inset_x:F,corner_inset_y:F,socket_depth:F,port_center_z:F,port_radius:F}
- steps: bom-masses, enclosure, enclosure-assembly, enclosure-box, enclosure-dimensions, enclosure-mechanical-sync, internal-plumbing-sync, tee-valve-bow-trial …

## _data  (python _data:86; compiled line 388)
- `op`: S
- returns: F | R:dict | R:list
- steps: enclosure, enclosure-box, tee-valve-bow-trial, valve-tray

## height  (python height:97; compiled line 491)
- `seats`: T(T(F,F),T(F,F),T(F,F),T(F,F))
- returns: F
- steps: enclosure

## wall_root_floors  (python wall_root_floors:102; compiled line 517)
- `seats`: T(T(F,F),T(F,F),T(F,F),T(F,F))
- returns: T(F,F)
- steps: enclosure, enclosure-box

## trays_of_machine  (python trays_of_machine:326; compiled line 968)
- `facts`: R:Facts
- returns: R:dict
- steps: valve-tray

## tray_stock_numbers  (python tray_stock_numbers:342; compiled line 1013)
- `width`: F
- `seats`: T(T(F,F))
- returns: R:dict
- steps: tee-valve-bow-trial

## numbers  (python numbers:347; compiled line 1040)
- `trays`: R:dict
- returns: R:dict
- steps: valve-tray

## main  (python main:353; compiled line 1071)
- returns: N
- steps: valve-tray

