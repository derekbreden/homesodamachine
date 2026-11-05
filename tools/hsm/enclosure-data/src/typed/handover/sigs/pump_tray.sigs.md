# pump_tray: observed signatures (10 live compiled functions)

## _pump_source  (python _pump_source:44; compiled line 183)
- returns: D{S:F}
- steps: bom-masses, enclosure, enclosure-assembly, enclosure-box, enclosure-dimensions, enclosure-mechanical-sync, internal-plumbing-sync, pump-tray

## _data  (python _data:80; compiled line 318)
- `op`: S
- returns: F | R:dict | R:list
- steps: enclosure, enclosure-assembly, enclosure-box, pump-tray

## depth  (python depth:85; compiled line 381)
- returns: F
- steps: enclosure, enclosure-assembly, enclosure-box

## half_width  (python half_width:91; compiled line 406)
- returns: F
- steps: enclosure, enclosure-assembly, enclosure-box

## outlet_fore_miter  (python outlet_fore_miter:126; compiled line 503)
- `air`: F
- returns: T(F,F,F,F)
- steps: enclosure

## outlet_under_tangent  (python outlet_under_tangent:135; compiled line 541)
- `air`: F
- returns: T(F,F,F,F)
- steps: enclosure

## outlet_passage_start_y  (python outlet_passage_start_y:168; compiled line 729)
- `air`: F
- returns: F
- steps: enclosure

## trays_of_machine  (python trays_of_machine:289; compiled line 1010)
- `facts`: R:Facts
- returns: R:dict
- steps: pump-tray

## numbers  (python numbers:298; compiled line 1023)
- `trays`: R:dict
- returns: R:dict
- steps: pump-tray

## main  (python main:368; compiled line 1110)
- returns: N
- steps: pump-tray

