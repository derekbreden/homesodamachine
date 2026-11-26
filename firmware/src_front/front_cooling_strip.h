#pragma once

#include <lvgl.h>
#include "front_cooling.h"

namespace front_ui {

// The machine button pairs the gear with the tank reading and the current cooling activity.
class CoolingStrip {
public:
  void build(lv_obj_t *button, lv_coord_t railWidth, lv_color_t ice, lv_color_t warning);
  void update(const char *fahrenheit, int16_t tankCx10, CoolingState state, uint16_t seconds);

private:
  static void draw(lv_event_t *event);

  lv_obj_t *button_ = nullptr;
  lv_obj_t *temperature_ = nullptr;
  lv_obj_t *countdown_ = nullptr;
  lv_coord_t railWidth_ = 0;
  lv_color_t ice_{}, warning_{};
  CoolingState state_ = CoolingState::Unavailable;
  int column_ = -1;
  uint16_t seconds_ = 0;
};

}  // namespace front_ui
