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

/* Fonts: 20 is the smallest built, and the theme default, so nothing on this panel
 * renders below it. A standing user reads it at arm's length across a countertop. */
#define LV_FONT_MONTSERRAT_20 1
#define LV_FONT_MONTSERRAT_28 1
#define LV_FONT_MONTSERRAT_40 1
#define LV_FONT_MONTSERRAT_48 1
#define LV_FONT_DEFAULT &lv_font_montserrat_20

/* A pressed button keeps its size and arrives at its colour in one step. The default theme
 * gives every lv_btn a `grow` style on LV_STATE_PRESSED — transform_width and
 * transform_height of lv_disp_dpx(3), which is 2 px a side at LV_DPI_DEF 130 — and
 * interpolates colour, transform and translate over 80 ms, which is shorter than one
 * repaint of this panel. */
#define LV_THEME_DEFAULT_GROW 0
#define LV_THEME_DEFAULT_TRANSITION_TIME 0

/* Disable debug monitors */
#define LV_USE_PERF_MONITOR 0
#define LV_USE_MEM_MONITOR 0

#endif /* LV_CONF_H */
#endif /* End of #if 1 */
