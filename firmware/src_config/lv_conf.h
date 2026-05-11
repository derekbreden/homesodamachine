#if 1 /* Enable LVGL config */
#ifndef LV_CONF_H
#define LV_CONF_H

#include <stdint.h>

/* Color: 16-bit RGB565, no byte swap (Arduino_GFX handles SPI byte order) */
#define LV_COLOR_DEPTH 16
#define LV_COLOR_16_SWAP 0

/* Use system malloc instead of LVGL's fixed memory pool */
#define LV_MEM_CUSTOM 1
#define LV_MEM_CUSTOM_INCLUDE <stdlib.h>
#define LV_MEM_CUSTOM_ALLOC malloc
#define LV_MEM_CUSTOM_FREE free
#define LV_MEM_CUSTOM_REALLOC realloc

/* Tick: use Arduino millis() */
#define LV_TICK_CUSTOM 1
#define LV_TICK_CUSTOM_INCLUDE "Arduino.h"
#define LV_TICK_CUSTOM_SYS_TIME_EXPR (millis())

/* Display DPI (240px / 1.28" ≈ 188, but 130 is LVGL's recommended default) */
#define LV_DPI_DEF 130

/* Fonts: Montserrat with kerning at sizes we need */
#define LV_FONT_MONTSERRAT_14 1
#define LV_FONT_MONTSERRAT_16 1
#define LV_FONT_MONTSERRAT_28 1
#define LV_FONT_MONTSERRAT_48 1

/* Disable debug monitors */
#define LV_USE_PERF_MONITOR 0
#define LV_USE_MEM_MONITOR 0

#endif /* LV_CONF_H */
#endif /* End of #if 1 */
