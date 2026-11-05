# _enclosure_rust_driver: observed signatures (12 live compiled functions)

## load  (python load:13; compiled line 48)
- returns: NS
- steps: enclosure, enclosure-assembly, enclosure-box

## box_from_document  (python box_from_document:18; compiled line 68)
- `document`: D{bounds:L[D{detail:D{__hsm_list__:~},id:S,label:S,ok:B,target:S,value:S}],box:D{column_reliefs:L[L[~]],inner:L[F],outer:L[F],pack:D{__hsm_namedtuple__:S,fields:L[~],values:L[~]},pump_bay:L[F],splits:L[F],y_joint:F,z_seam_passes:L[B]},box_fields:L[S],schema:I} | R:dict
- returns: T(NS,R:Box,L[R:Bound])
- steps: enclosure, enclosure-assembly

## _model_instance  (python _model_instance:31; compiled line 76)
- `model`: P
- `name`: S
- `transform`: N | T(T(F,F,F,F),T(F,F,F,F),T(F,F,F,F))
- `indices`: L[I] | N
- `color`: L[F] | N | T(F,F,F)
- `split_components`: B
- returns: D{model:S,name:S,color:L[F]} | D{model:S,name:S,transform:T(T(F,F,F,F),T(F,F,F,F),T(F,F,F,F)),color:L[F]} | D{model:S,name:S,transform:T(T(F,F,F,F),T(F,F,F,F),T(F,F,F,F)),indices:L[I],color:L[F],split_components:B} | D{model:S,name:S,transform:T(T(F,F,F,F),T(F,F,F,F),T(F,F,F,F)),indices:L[I],color:L[F]} | D{model:S,name:S,transform:T(T(F,F,F,F),T(F,F,F,F),T(F,F,F,F)),indices:L[I],split_components:B} | D{model:S,name:S,transform:T(T(F,F,F,F),T(F,F,F,F),T(F,F,F,F)),indices:L[I]} | D{model:S,name:S}
- steps: enclosure, enclosure-assembly

## _translation  (python _translation:47; compiled line 101)
- `point`: T(F,F,F)
- returns: T(T(F,F,F,F),T(F,F,F,F),T(F,F,F,F))
- steps: enclosure-assembly

## cut_pieces  (python cut_pieces:52; compiled line 150)
- `shell`: NS
- `box`: R:Box
- `directory`: P
- returns: T(D{front-bottom:P,front-top:P,back-bottom:P,back-top:P,pump-retainer:P},P)
- steps: enclosure

## _dock_recipe  (python _dock_recipe:76; compiled line 337)
- `shell`: NS
- `graph`: R:_Graph
- returns: NS
- steps: enclosure

## <lambda>  (python ?; compiled line 367)
- `r`: F
- `x`: F
- `z`: F
- `y0`: F
- `y1`: F
- returns: R:_Shape
- steps: enclosure

## cut_tube_setting_jig  (python cut_tube_setting_jig:87; compiled line 408)
- `shell`: NS
- `box`: R:Box
- `directory`: P
- returns: N
- steps: enclosure

## installed_instances  (python installed_instances:105; compiled line 422)
- `box_document`: R:dict
- `directory`: R:PosixPath
- returns: D{instances:L[D{model:S,name:S,transform:T(~,~,~),color:L[~]}|D{model:S,name:S,transform:T(~,~,~),indices:L[~],color:L[~],split_components:B}|D{model:S,name:S,transform:T(~,~,~),indices:L[~],color:L[~]}|D{model:S,name:S,transform:T(~,~,~),indices:L[~],split_components:B}|..],datums:D{funnel_frame_fasteners:T(D{~:~},D{~:~},D{~:~},D{~:~}),funnel_centre:T(F,F),funnel_seat:F,funnel_frame_floor:F,y_stack_rods:T(T(~,~,~,~,~,~,~),T(~,~,~,~,~,~,~))}}
- steps: enclosure-assembly

## box_from_plan  (python box_from_plan:158; compiled line 458)
- `plan`: R:dict
- returns: T(NS,R:Box)
- steps: enclosure-box

## stations  (python box_from_plan.<locals>.stations:170; compiled line 469)
- `value`: D{-22.35:D{axis:L[F],point:L[F],valve:S},-82.1:D{axis:L[F],point:L[F],valve:S},22.35:D{axis:L[F],point:L[F],valve:S},82.1:D{axis:L[F],point:L[F],valve:S}} | D{axis:L[F],point:L[F],valve:S} | F | I | L[F] | L[F|I|L[L[F]]] | L[L[F]] | L[L[F|I|L[L[~]]]] | N | R:dict | R:list | S
- returns: D{-22.35:D{axis:T(F,F,F),point:T(F,F,F),valve:S},-82.1:D{axis:T(F,F,F),point:T(F,F,F),valve:S},22.35:D{axis:T(F,F,F),point:T(F,F,F),valve:S},82.1:D{axis:T(F,F,F),point:T(F,F,F),valve:S}} | D{S:D{-22.35:D{axis:T(~,~,~),point:T(~,~,~),valve:S},-82.1:D{axis:T(~,~,~),point:T(~,~,~),valve:S},22.35:D{axis:T(~,~,~),point:T(~,~,~),valve:S},82.1:D{axis:T(~,~,~),point:T(~,~,~),valve:S}}|F|S|T(T(F,F),T(F,F),T(F,F),T(F,F))|..} | D{S:T(T(F,F,F),T(F,F,F))} | D{axis:T(F,F,F),point:T(F,F,F),valve:S} | F | I | N | S | T() | T(F,F) | T(F,F,F) | T(F,F,F,F) | T(F,F,F,F,F,F) | T(F,F,F,T(T(F,F,F),T(F,F,F))) | T(F,I,T(T(F,F),T(F,F),T(F,F),T(F,F))) | T(S,F,F,F,F,F) | T(S,F,F,F,F,F,F) | T(T(F,F),T(F,F),T(F,F),T(F,F)) | T(T(F,F,F)) | T(T(F,F,F),T(F,F,F)) | T(T(F,F,F,F),T(F,F,F,F)) | T(T(F,F,F,F),T(F,F,F,F),T(F,F,F,F),T(F,F,F,F)) | T(T(F,F,F,F,F,F),T(F,F,F,F,F,F)) | T(T(F,I,T(T(~,~),T(~,~),T(~,~),T(~,~))),T(F,I,T(T(~,~),T(~,~),T(~,~),T(~,~)))) | T(T(S,F,F,F,F,F),T(S,F,F,F,F,F)) | T(T(S,F,F,F,F,F,F),T(S,F,F,F,F,F,F))
- steps: enclosure-box

## main  (python main:199; compiled line 505)
- `box_path`: N
- `directory`: N
- returns: D{models:D{front-bottom:P,front-top:P,back-bottom:P,back-top:P,pump-retainer:P},installed_retainer:P,checks:D{bounds:L[R:Bound],checks:L[D{id:~,label:~,kind:~,status:~,value:~,target:~,detail:~,active:~}],slides:D{front:T(~,~,~,~),back:T(~,~,~,~)},vents:D{F:D{slots:~,mullions:~,runs:~,tallest:~,open_mm2:~,band:~}},piece_bounds:D{front-bottom:L[~],front-top:L[~],back-bottom:L[~],back-top:L[~],pump-retainer:L[~]}}}
- steps: enclosure

