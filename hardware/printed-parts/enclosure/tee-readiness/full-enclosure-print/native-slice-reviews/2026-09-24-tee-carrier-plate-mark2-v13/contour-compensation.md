# Contour compensation by height

The installed Bambu Studio release, **02.08.02.61**, provides **X–Y contour compensation**
under Quality / Precision. A positive value expands the outside outline; a negative value
contracts it. The option is intended for small dimensional corrections.
[Option definition](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp#L6345-L6353).

It is a whole-object setting, not a height-range or modifier setting in this release.
`xy_contour_compensation` belongs to `PrintObjectConfig`, while the layer-range settings
contain `layer_height` plus `PrintRegionConfig` keys. The layer-range application also copies
only region settings, so adding the option to a range in the archive is not a working override.
[Configuration classes](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.hpp#L947-L1063),
[settings panels](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/slic3r/GUI/Tab.cpp#L4273-L4303),
[range application](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintObject.cpp#L3069-L3124).

A local, smoothly varying outward allowance could instead be modeled into a print variant.
Its usefulness would depend on measured, repeatable edge retreat. An abrupt outward step
can reduce the landing overlap precisely where it is already failing; any compensation
would need to build gradually through the preceding layers and return smoothly as the
curve steepens, while preserving mating surfaces. This is a possible geometric experiment,
not a demonstrated remedy. The steady-cooling trial uses the unchanged carrier geometry.
