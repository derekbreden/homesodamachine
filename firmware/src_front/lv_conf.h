#if 1 /* Enable LVGL config */
#ifndef LV_CONF_H
#define LV_CONF_H

#include <stdint.h>

/* Color: 16-bit RGB565, no byte swap (the RGB panel takes native RGB565) */
#define LV_COLOR_DEPTH 16
#define LV_COLOR_16_SWAP 0

/* Use system malloc so LVGL draw buffers can land in PSRAM (ps_malloc) and
 * the fixed pool never caps us on this 8 MB-PSRAM board. */
#define LV_MEM_CUSTOM 1
#define LV_MEM_CUSTOM_INCLUDE <stdlib.h>
#define LV_MEM_CUSTOM_ALLOC malloc
#define LV_MEM_CUSTOM_FREE free
#define LV_MEM_CUSTOM_REALLOC realloc

/* Tick: use Arduino millis() */
#define LV_TICK_CUSTOM 1
#define LV_TICK_CUSTOM_INCLUDE "Arduino.h"
#define LV_TICK_CUSTOM_SYS_TIME_EXPR (millis())

/* Display DPI (LVGL's recommended default; sizes are set explicitly) */
#define LV_DPI_DEF 130

/* Fonts: only the theme default (the foundation UI is image-only) */
#define LV_FONT_MONTSERRAT_14 1

/* Disable debug monitors */
#define LV_USE_PERF_MONITOR 0
#define LV_USE_MEM_MONITOR 0

#endif /* LV_CONF_H */
#endif /* End of #if 1 */
