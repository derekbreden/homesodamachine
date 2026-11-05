# _rust_enclosure_checks: observed signatures (35 live compiled functions)

## _Vector.__init__  (python _Vector.__init__:24; compiled line 36)
- `self`: R:_Vector
- returns: N
- steps: enclosure

## _Vector.__iter__  (python _Vector.__iter__:28; compiled line 100)
- `self`: R:_Vector
- returns: T(F,F,F)
- steps: enclosure

## _Vector.__sub__  (python _Vector.__sub__:37; compiled line 120)
- `self`: R:_Vector
- `other`: R:_Vector
- returns: R:_Vector
- steps: enclosure

## _Vector.dot  (python _Vector.dot:40; compiled line 128)
- `self`: R:_Vector
- `other`: R:_Vector
- returns: F
- steps: enclosure

## _Vector.Length  (python _Vector.Length:44; compiled line 179)
- `self`: R:_Vector
- returns: F
- steps: enclosure

## _bounds  (python _bounds:48; compiled line 214)
- `lower`: N | R:list | T(F,F,F)
- `upper`: N | R:list | T(F,F,F)
- returns: R:SimpleNamespace
- steps: enclosure

## _ScalarFace.__init__  (python _ScalarFace.__init__:58; compiled line 226)
- `self`: R:_ScalarFace
- `row`: R:dict
- returns: N
- steps: enclosure

## _ScalarFace.Area  (python _ScalarFace.Area:61; compiled line 239)
- `self`: R:_ScalarFace
- returns: F
- steps: enclosure

## _ScalarFace.Center  (python _ScalarFace.Center:64; compiled line 251)
- `self`: R:_ScalarFace
- returns: R:_Vector
- steps: enclosure

## _ScalarFace.normalAt  (python _ScalarFace.normalAt:67; compiled line 280)
- `self`: R:_ScalarFace
- returns: R:_Vector
- steps: enclosure

## _ScalarFace.BoundingBox  (python _ScalarFace.BoundingBox:70; compiled line 309)
- `self`: R:_ScalarFace
- returns: R:SimpleNamespace
- steps: enclosure

## _ScalarFace.geomType  (python _ScalarFace.geomType:73; compiled line 334)
- `self`: R:_ScalarFace
- returns: S
- steps: enclosure

## _ScalarComponent.__init__  (python _ScalarComponent.__init__:78; compiled line 350)
- `self`: R:_ScalarComponent
- `row`: R:dict
- returns: N
- steps: enclosure

## _ScalarComponent.BoundingBox  (python _ScalarComponent.BoundingBox:81; compiled line 363)
- `self`: R:_ScalarComponent
- returns: R:SimpleNamespace
- steps: enclosure

## _ReadingShape.translate  (python _ReadingShape.translate:91; compiled line 407)
- `self`: R:_ReadingShape
- `delta`: R:_Vector | R:list
- returns: R:_ReadingShape
- steps: enclosure

## _ReadingShape.Volume  (python _ReadingShape.Volume:94; compiled line 451)
- `self`: R:_ReadingShape
- returns: F
- steps: enclosure, enclosure-assembly

## _ReadingShape.BoundingBox  (python _ReadingShape.BoundingBox:97; compiled line 476)
- `self`: R:_ReadingShape
- returns: R:SimpleNamespace
- steps: enclosure

## _ReadingShape.Solids  (python _ReadingShape.Solids:107; compiled line 610)
- `self`: R:_ReadingShape
- returns: L[R:_ScalarComponent] | L[]
- steps: enclosure

## _ReadingShape.isValid  (python _ReadingShape.isValid:111; compiled line 679)
- `self`: R:_ReadingShape
- returns: B
- steps: enclosure

## _ReadingShape.Faces  (python _ReadingShape.Faces:114; compiled line 718)
- `self`: R:_ReadingShape
- returns: L[R:_ScalarFace] | L[]
- steps: enclosure

## _Questions.__init__  (python _Questions.__init__:120; compiled line 775)
- `self`: R:_Questions
- `answers`: N | R:dict
- returns: N
- steps: enclosure, enclosure-assembly, enclosure-box

## _Questions.add  (python _Questions.add:126; compiled line 830)
- `self`: R:_Questions
- `op`: S
- `inputs`: R:list | T()
- `bounds`: N | R:list | T(F,F,F,F,F,F)
- returns: R:_ReadingShape
- steps: enclosure, enclosure-assembly, enclosure-box

## _Questions.model  (python _Questions.model:132; compiled line 893)
- `self`: R:_Questions
- `value`: R:PosixPath | R:dict | R:list
- returns: R:_ReadingShape
- steps: enclosure, enclosure-assembly, enclosure-box

## _Questions.identity  (python _Questions.identity:141; compiled line 901)
- `self`: R:_Questions
- `index`: I
- returns: S
- steps: enclosure, enclosure-assembly, enclosure-box

## _Questions.reading  (python _Questions.reading:150; compiled line 921)
- `self`: R:_Questions
- `shape`: R:_ReadingShape
- `kind`: S
- `components`: B
- `valid`: B
- returns: D{volume_mm3:F,min:N,max:N,components:L[],valid:B} | L[] | R:dict | R:list
- steps: enclosure, enclosure-assembly, enclosure-box

## _Questions.document  (python _Questions.document:167; compiled line 1092)
- `self`: R:_Questions
- returns: D{nodes:L[D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,radius:F,centre:T(~,~),span:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},box:T(~,~,~,~,~,~),radius:F}|D{op:S,inputs:L[],source:D{path:~,line:~},box:T(~,~,~,~,~,~)}|D{op:S,inputs:L[~],source:D{path:~,line:~}}],queries:L[D{key:S,node:I,kind:S}]} | D{nodes:L[D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,radius:F,centre:T(~,~),span:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},box:T(~,~,~,~,~,~)}|D{op:S,inputs:L[],source:D{path:~,line:~},reference:D{model:~,indices:~}}|D{op:S,inputs:L[~],source:D{path:~,line:~}}],queries:L[D{key:S,node:I,kind:S}]} | D{nodes:L[D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~),radius:F,corners:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~)}|D{op:S,inputs:L[],source:D{path:~,line:~},axis:I,span:L[~],section:T(~,~,~,~,~,~,~,~),radius:F,corners:L[~]}|D{op:S,inputs:L[],source:D{path:~,line:~},box:T(~,~,~,~,~,~)}|..],queries:L[D{key:S,node:I,kind:S,components:B,valid:B}|D{key:S,node:I,kind:S}]}
- steps: enclosure, enclosure-assembly, enclosure-box

## visit  (python _Questions.document.<locals>.visit:170; compiled line 1094)
- `k`: I
- returns: N
- steps: enclosure, enclosure-assembly, enclosure-box

## _numeric  (python _numeric:186; compiled line 1113)
- `shell`: NS
- `graph`: R:_Questions
- `box`: N | R:Box
- returns: NS
- steps: enclosure, enclosure-assembly, enclosure-box

## _measure  (python _measure:201; compiled line 1134)
- `graph`: R:_Questions
- returns: R:dict
- steps: enclosure, enclosure-assembly, enclosure-box

## check_rows  (python check_rows:206; compiled line 1174)
- `bounds`: L[R:Bound]
- returns: L[D{id:S,label:S,kind:S,status:S,value:S,target:S,detail:R:list,active:B}]
- steps: enclosure

## _piece_reports  (python _piece_reports:213; compiled line 1218)
- `shell`: NS
- `box`: R:Box
- `models`: D{front-bottom:P,front-top:P,back-bottom:P,back-top:P,pump-retainer:P}
- `installed_retainer`: P
- `core`: N
- `graph`: R:_Questions
- returns: D{bounds:L[R:Bound],checks:L[D{id:S,label:S,kind:S,status:S,value:S,target:S,detail:R:list,active:B}],slides:D{front:T(T(~,~),F,I,F),back:T(T(~,~),F,I,F)},vents:D{F:D{slots:L[~],mullions:L[~],runs:L[~],tallest:F,open_mm2:F,band:T(~,~)}},piece_bounds:D{front-bottom:L[F],front-top:L[F],back-bottom:L[F],back-top:L[F],pump-retainer:L[F]}} | D{bounds:L[R:Bound],checks:L[D{id:S,label:S,kind:S,status:S,value:S,target:S,detail:R:list,active:B}],slides:D{},vents:D{F:D{slots:L[],mullions:L[],runs:L[],tallest:F,open_mm2:F,band:T(~,~)}},piece_bounds:D{}}
- steps: enclosure

## record  (python _piece_reports.<locals>.record:219; compiled line 1224)
- `row`: R:Bound
- returns: R:Bound
- steps: enclosure

## check_pieces  (python check_pieces:266; compiled line 1289)
- `shell`: NS
- `box`: R:Box
- `models`: D{front-bottom:P,front-top:P,back-bottom:P,back-top:P,pump-retainer:P}
- `installed_retainer`: P
- `core`: N
- returns: D{bounds:L[R:Bound],checks:L[D{id:S,label:S,kind:S,status:S,value:S,target:S,detail:R:list,active:B}],slides:D{front:T(T(~,~),F,I,F),back:T(T(~,~),F,I,F)},vents:D{F:D{slots:L[~],mullions:L[~],runs:L[~],tallest:F,open_mm2:F,band:T(~,~)}},piece_bounds:D{front-bottom:L[F],front-top:L[F],back-bottom:L[F],back-top:L[F],pump-retainer:L[F]}}
- steps: enclosure

## box_readings  (python box_readings:283; compiled line 1443)
- `shell`: NS
- `pack`: R:Pack
- `bounds`: D{S:R:list}
- `references`: R:dict
- returns: R:BoxReadings
- steps: enclosure-box

## ask  (python box_readings.<locals>.ask:285; compiled line 1444)
- `graph`: R:_Questions
- returns: R:BoxReadings
- steps: enclosure-box

