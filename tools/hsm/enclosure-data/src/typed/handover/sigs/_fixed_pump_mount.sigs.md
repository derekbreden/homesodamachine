# _fixed_pump_mount: observed signatures (17 live compiled functions)

## datums  (python datums:26; compiled line 42)
- `e`: NS
- `box`: R:Box
- returns: D{flange_z:F,bearing_z:F,retainer_top_z:F,bottom_z:F,x0:F,x1:F,y0:F,y1:F,head_y:F,motor_y:F}
- steps: enclosure, enclosure-assembly

## fasteners  (python fasteners:44; compiled line 54)
- `e`: NS
- `box`: R:Box
- returns: T()
- steps: bom-masses

## snap_datums  (python snap_datums:53; compiled line 86)
- `e`: NS
- `box`: R:Box
- returns: D{S:F}
- steps: enclosure

## snap_receivers  (python snap_receivers:81; compiled line 271)
- `e`: NS
- `box`: R:Box
- `piece`: R:_Shape
- returns: R:_Shape
- steps: enclosure

## stock  (python stock:109; compiled line 294)
- `e`: NS
- `box`: R:Box
- returns: R:_Shape
- steps: enclosure

## loading_opening  (python loading_opening:117; compiled line 392)
- `e`: NS
- `box`: R:Box
- returns: R:_Shape
- steps: enclosure

## wiring_passages  (python wiring_passages:124; compiled line 459)
- `e`: NS
- `box`: R:Box
- returns: D{front-top-electrical:D{points_mm:L[T(~,~,~)],diamond_half_span_mm:F},front-top-pump-cross:D{points_mm:L[T(~,~,~)],roof_half_span_mm:F,floor_z_mm:F},front-top-display-chimney:D{points_mm:L[T(~,~,~)],bounds_mm:L[F]},front-top-display-link:D{points_mm:L[T(~,~,~)],terminal_entry_mm:T(F,F,F),diamond_half_span_mm:F}}
- steps: enclosure, enclosure-assembly

## _corridor_profile  (python _corridor_profile:162; compiled line 565)
- `vertices`: L[T(F,F,F)]
- returns: T(T(F,F),L[T(F,F)])
- steps: enclosure

## turn  (python _corridor_profile.<locals>.turn:165; compiled line 567)
- `a`: T(F,F)
- `b`: T(F,F)
- `c`: T(F,F)
- returns: F
- steps: enclosure

## chain  (python _corridor_profile.<locals>.chain:167; compiled line 570)
- `sequence`: L[T(F,F)]
- returns: L[T(F,F)]
- steps: enclosure

## fixed_cuts  (python fixed_cuts:288; compiled line 925)
- `e`: NS
- `box`: R:Box
- returns: L[R:_Shape]
- steps: enclosure

## lower_voids  (python lower_voids:299; compiled line 1087)
- `e`: NS
- `box`: R:Box
- returns: L[R:_Shape]
- steps: enclosure

## wing_profile  (python wing_profile:330; compiled line 1437)
- `e`: NS
- `box`: R:Box
- `side`: F
- `spread`: F
- returns: D{span:T(F,F),segments:L[D{cubic:T(~,~,~,~)}|D{line:T(~,~)}]}
- steps: enclosure

## deflection  (python wing_profile.<locals>.deflection:339; compiled line 1441)
- `z`: F
- returns: F
- steps: enclosure

## slope  (python wing_profile.<locals>.slope:342; compiled line 1445)
- `z`: F
- returns: F
- steps: enclosure

## retainer  (python retainer:394; compiled line 1492)
- `e`: NS
- `box`: R:Box
- `seated`: B
- returns: R:_Shape
- steps: enclosure

## figures  (python figures:410; compiled line 1508)
- `e`: NS
- `box`: R:Box
- returns: D{S:S}
- steps: enclosure

