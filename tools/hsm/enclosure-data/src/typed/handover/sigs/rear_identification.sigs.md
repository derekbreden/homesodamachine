# rear_identification: observed signatures (9 live compiled functions)

## nameplate_plan  (python nameplate_plan:45; compiled line 27)
- returns: R:dict
- steps: enclosure, enclosure-assembly

## nameplate_station  (python nameplate_station:51; compiled line 30)
- returns: R:Nameplate
- steps: enclosure

## stations  (python stations:63; compiled line 37)
- returns: T(R:dict,R:dict,R:dict,R:dict,R:dict,R:dict)
- steps: enclosure-assembly

## channel_bounds  (python channel_bounds:76; compiled line 46)
- returns: T(T(F,F,F,F,F,F),T(F,F,F,F,F,F))
- steps: enclosure

## _colour  (python _colour:106; compiled line 63)
- `rgb`: T(F,F,F) | T(I,I,I)
- returns: R:Color
- steps: enclosure-assembly, rear-identification

## rail_bounds  (python rail_bounds:172; compiled line 104)
- returns: T(T(F,F,F,F,F,F),T(F,F,F,F,F,F),T(F,F,F,F,F,F))
- steps: enclosure

## rail_roots  (python rail_roots:177; compiled line 107)
- returns: T(T(F,F,F,F,F,F),T(F,F,F,F,F,F),T(F,F,F,F,F,F))
- steps: enclosure

## numbers  (python numbers:208; compiled line 127)
- returns: R:dict
- steps: enclosure-assembly, rear-identification

## main  (python main:222; compiled line 135)
- returns: N
- steps: rear-identification

