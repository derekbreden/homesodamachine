# pump_case: observed signatures (8 live compiled functions)

## offset_polygon  (python offset_polygon:49; compiled line 409)
- `pts`: L[L[F]]
- `distance`: F
- returns: L[T(F,F)]
- steps: enclosure

## split_skirt_profile  (python split_skirt_profile:60; compiled line 530)
- `wide_half_extent`: F
- `wide_radius`: F
- `narrow_half_extent`: F
- `narrow_radius`: F
- `transition_y_plus`: F
- `transition_y_minus`: F
- `wide_half_extent_y`: F
- `narrow_half_extent_y`: F
- `n`: I
- returns: L[T(F,F)]
- steps: enclosure

## _skirt_profile_set  (python _skirt_profile_set:74; compiled line 592)
- `wall_offset`: F
- returns: L[L[T(F,F)]]
- steps: enclosure

## _lower_profile_set  (python _lower_profile_set:228; compiled line 783)
- `wall_offset`: F
- returns: L[L[T(F,F)]]
- steps: enclosure

## lower_z_steps  (python lower_z_steps:244; compiled line 881)
- returns: L[F]
- steps: enclosure

## _stack_levels  (python _stack_levels:386; compiled line 1789)
- returns: L[F]
- steps: enclosure

## _stack_profiles  (python _stack_profiles:399; compiled line 1862)
- `offset`: F
- returns: L[L[T(F,F)]]
- steps: enclosure

## main  (python main:553; compiled line 2343)
- returns: N
- steps: pump-case

