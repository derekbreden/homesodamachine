# _enclosure_panel: observed signatures (36 live compiled functions)

## _Shape.__init__  (python _Shape.__init__:16; compiled line 32)
- `self`: R:_ReadingShape | R:_Shape
- `graph`: R:_Graph | R:_Questions
- `index`: I
- `bounds`: N | R:list | T(F,F,F,F,F,F) | T(F,F,F,F,F,I) | T(F,F,I,F,F,F)
- returns: N
- steps: enclosure, enclosure-assembly, enclosure-box

## _Shape._boolean  (python _Shape._boolean:19; compiled line 48)
- `self`: R:_ReadingShape | R:_Shape
- `op`: S
- `others`: T() | T(R:_ReadingShape) | T(R:_ReadingShape,R:_ReadingShape) | T(R:_Shape) | T(R:_Shape,R:_Shape) | T(R:_Shape,R:_Shape,R:_Shape) | T(R:_Shape,R:_Shape,R:_Shape,R:_Shape) | T(R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape) | T(R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape) | T(R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape,R:_Shape) | T10[R:_ReadingShape] | T11[R:_ReadingShape] | T20[R:_ReadingShape]
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly, enclosure-box

## ?71  (python ?; compiled line 71)
- `self`: R:_ReadingShape | R:_Shape
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly, enclosure-box

## ?103  (python ?; compiled line 103)
- `self`: R:_ReadingShape | R:_Shape
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly, enclosure-box

## ?135  (python ?; compiled line 135)
- `self`: R:_ReadingShape | R:_Shape
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly, enclosure-box

## _Shape.translate  (python _Shape.translate:48; compiled line 167)
- `self`: R:_ReadingShape | R:_Shape
- `delta`: R:list | T(F,F,F)
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## _Shape.rotate  (python _Shape.rotate:53; compiled line 267)
- `self`: R:_Shape
- `origin`: T(F,F,F) | T(I,I,I)
- `end`: T(F,F,F) | T(I,I,I)
- `angle`: F | I
- returns: R:_Shape
- steps: enclosure

## point  (python _Shape.rotate.<locals>.point:60; compiled line 274)
- `p`: T(F,F,F)
- returns: L[F]
- steps: enclosure

## _Shape.mirror  (python _Shape.mirror:74; compiled line 289)
- `self`: R:_Shape
- `plane`: S
- returns: R:_Shape
- steps: enclosure

## _Shape.clean  (python _Shape.clean:81; compiled line 393)
- `self`: R:_Shape
- returns: R:_Shape
- steps: enclosure

## _Shape.val  (python _Shape.val:84; compiled line 405)
- `self`: R:_ReadingShape | R:_Shape
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly

## _Shape.BoundingBox  (python _Shape.BoundingBox:87; compiled line 417)
- `self`: R:_Shape
- returns: R:SimpleNamespace
- steps: enclosure

## _Shape.Solids  (python _Shape.Solids:94; compiled line 532)
- `self`: R:_Shape
- returns: L[R:_Shape]
- steps: enclosure

## _Graph.__init__  (python _Graph.__init__:99; compiled line 549)
- `self`: R:_Graph | R:_Questions
- returns: N
- steps: enclosure, enclosure-assembly, enclosure-box

## _Graph.add  (python _Graph.add:102; compiled line 577)
- `self`: R:_Graph | R:_Questions
- `op`: S
- `inputs`: R:list | T()
- `bounds`: N | R:list | T(F,F,F,F,F,F) | T(F,F,F,F,F,I) | T(F,F,I,F,F,F)
- returns: R:_Shape
- steps: enclosure, enclosure-assembly, enclosure-box

## _Graph.box  (python _Graph.box:118; compiled line 668)
- `self`: R:_Graph | R:_Questions
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly, enclosure-box

## _Graph.cylinder  (python _Graph.cylinder:121; compiled line 702)
- `self`: R:_Graph | R:_Questions
- `axis`: I
- `radius`: F
- `a`: F
- `b`: F
- `lo`: F
- `hi`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly, enclosure-box

## _Graph.prism  (python _Graph.prism:130; compiled line 880)
- `self`: R:_Graph | R:_Questions
- `axis`: I
- `lo`: F
- `hi`: F | I
- `section`: R:list | T(T(F,F),T(F,F),T(F,F)) | T(T(F,F),T(F,F),T(F,F),T(F,F)) | T(T(F,F),T(F,F),T(F,F),T(F,F),T(F,F)) | T(T(F,F),T(F,F),T(F,F),T(F,F),T(F,F),T(F,F)) | T(T(F,I),T(F,F),T(F,F)) | T(T(F,I),T(F,I),T(F,F),T(F,F)) | T9[T(F,F)]
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure

## _Graph.rounded  (python _Graph.rounded:140; compiled line 1102)
- `self`: R:_Graph | R:_Questions
- `shape`: R:_ReadingShape | R:_Shape
- `radius`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-box

## _Graph.document  (python _Graph.document:147; compiled line 1172)
- `self`: R:_Graph
- `result`: R:_Shape
- `extras`: N | R:dict
- returns: D{nodes:L[D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,radius:F,centre:T(~,~),span:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~)}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~),radius:F,corners:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~)}|..],result:I} | D{nodes:L[D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,radius:F,centre:T(~,~),span:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~),radius:F,corners:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~)}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~,~,~,~,~),radius:F,corners:L[~]}|..],result:I,extras:D{receiver_field:I}} | D{nodes:L[D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,radius:F,centre:T(~,~),span:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},box:T(~,~,~,~,~,~),radius:F}|D{op:S,inputs:L[],source:D{path:~,line:~},box:T(~,~,~,~,~,~)}|D{op:S,inputs:L[],source:D{path:~,line:~}}|..],result:I} | D{nodes:L[D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,radius:F,centre:T(~,~),span:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},box:T(~,~,~,~,~,~)}|D{op:S,inputs:L[~],source:D{path:~,line:~}}],result:I} | D{nodes:L[D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,radius:F,centre:T(~,~),span:T(~,~),stations:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~)}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~,~,~,~,~)}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T38[~]}|..],result:I}
- steps: enclosure

## visit  (python _Graph.document.<locals>.visit:149; compiled line 1194)
- `index`: I
- returns: N
- steps: enclosure

## _record  (python _record:168; compiled line 1432)
- `shell`: NS
- `graph`: R:_Graph | R:_Questions
- `structure`: N | R:_Shape
- returns: NS
- steps: enclosure, enclosure-assembly, enclosure-box

## teardrop_y  (python _record.<locals>.teardrop_y:170; compiled line 1436)
- `radius`: F
- `x`: F
- `z`: F
- `y0`: F
- `y1`: F
- `up`: F
- returns: R:_Shape
- steps: enclosure

## handhold_cutter  (python _record.<locals>.handhold_cutter:182; compiled line 1445)
- `inner`: T(F,F,F,F,F,F)
- `x_ext`: F
- `sx`: F
- returns: R:_Shape
- steps: enclosure

## handhold_finish  (python _record.<locals>.handhold_finish:192; compiled line 1452)
- `inner`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1460)
- `r`: F
- `x`: F
- `y`: F
- `z0`: F
- `z1`: F
- returns: R:_ReadingShape | R:_Shape
- steps: enclosure, enclosure-assembly, enclosure-box

## <lambda>  (python ?; compiled line 1461)
- `x0`: F
- `x1`: F
- `section`: L[T(F,F)] | T(T(F,F),T(F,F),T(F,F)) | T(T(F,F),T(F,F),T(F,F),T(F,F)) | T(T(F,F),T(F,F),T(F,F),T(F,F),T(F,F)) | T(T(F,F),T(F,F),T(F,F),T(F,F),T(F,F),T(F,F))
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1462)
- `y0`: F
- `y1`: F
- `section`: L[T(F,F)] | T(T(F,F),T(F,F),T(F,F)) | T(T(F,F),T(F,F),T(F,F),T(F,F))
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1463)
- `z0`: F
- `z1`: F
- `section`: L[T(F,F)] | T(T(F,F),T(F,F),T(F,F))
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1464)
- `outer`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1465)
- `outer`: T(F,F,F,F,F,F)
- returns: R:_Shape
- steps: enclosure

## <lambda>  (python ?; compiled line 1466)
- `shape`: R:_Shape
- returns: R:_Shape
- steps: enclosure

## numbers  (python numbers:236; compiled line 1479)
- `shell`: NS
- `box`: R:Box
- returns: D{angle:F,outer:T(F,F,F,F,F,F),profile:D{end:T(F,F),foot:T(F,F),front_mid:T(F,F),normal:T(F,F,F),origin:T(F,F,F),roof:T(F,F),start:T(F,F),top_mid:T(F,F)},roof_fill_sections:T(T34[D{~:~}],T34[D{~:~}]),roof_transition:D{foot:F,height:F,outward_per_height:F},side_radius:F,standing_radius:F,color:T(F,F,F),panel:R:dict}
- steps: enclosure

## print_numbers  (python print_numbers:273; compiled line 1516)
- `shell`: NS
- `box`: R:Box
- returns: D{S:D{across:F,along:F,margin:F,overrun:F,plan_tol:F,face_tol:F,pitch:F,width:F,depth:F,rise:F}|D{end:T(F,F),foot:T(F,F),front_mid:T(F,F),normal:T(F,F,F),origin:T(F,F,F),roof:T(F,F),start:T(F,F),top_mid:T(F,F)}|D{foot:F,height:F,outward_per_height:F}|D{panel_top:F,receiver_pad_floor:F,other_bounds:L[T(~,~,~,~,~,~)]}|..}
- steps: enclosure

## <lambda>  (python ?; compiled line 1539)
- `s`: F
- returns: T(T(F,F),T(F,F))
- steps: enclosure

## cut  (python _Shape.cut:42, cut:319; compiled line 1559)
- `shell`: NS
- `box`: R:Box
- `directory`: P
- returns: R:dict
- steps: enclosure

