#include "front_cooling_strip.h"
#include <string.h>

namespace {

// All marks use the same optical center as the panel's numeric labels.
struct Mark {
  lv_draw_ctx_t *ctx;
  lv_coord_t x, y;

  lv_point_t point(int dx, int dy) const {
    return {lv_coord_t(x + dx), lv_coord_t(y + dy)};
  }

  void line(int x1, int y1, int x2, int y2, int width, lv_color_t color) const {
    lv_draw_line_dsc_t style;
    lv_draw_line_dsc_init(&style);
    style.color = color;
    style.width = width;
    style.round_start = style.round_end = true;
    const lv_point_t a = point(x1, y1), b = point(x2, y2);
    lv_draw_line(ctx, &style, &a, &b);
  }

  void disc(int dx, int dy, int radius, lv_color_t color) const {
    lv_draw_rect_dsc_t style;
    lv_draw_rect_dsc_init(&style);
    style.bg_color = color;
    style.radius = LV_RADIUS_CIRCLE;
    lv_area_t area = {lv_coord_t(x + dx - radius), lv_coord_t(y + dy - radius),
                      lv_coord_t(x + dx + radius), lv_coord_t(y + dy + radius)};
    lv_draw_rect(ctx, &style, &area);
  }

  void sand(int baseY, int halfWidth, int tipY, lv_color_t color) const {
    if (halfWidth == 0) return;
    lv_draw_rect_dsc_t style;
    lv_draw_rect_dsc_init(&style);
    style.bg_color = color;
    const lv_point_t points[] = {point(-halfWidth, baseY), point(halfWidth, baseY), point(0, tipY)};
    lv_draw_triangle(ctx, &style, points);
  }
};

void thermometer(const Mark &m, int column, lv_color_t ice, lv_color_t background) {
  m.line(0, -15, 0, 8, 11, ice);
  m.disc(0, 11, 8, ice);
  m.line(0, -15, 0, 9, 6, background);
  m.disc(0, 11, 5, background);
  m.line(8, -10, 11, -10, 2, ice);
  m.line(8, -2, 10, -2, 2, ice);
  if (column >= 0) {
    m.line(0, 8 - column, 0, 10, 3, ice);
    m.disc(0, 11, 3, ice);
  }
}

void hourglass(const Mark &m, uint16_t seconds, lv_color_t ice) {
  m.line(-10, -14, 10, -14, 3, ice);
  m.line(-10, 14, 10, 14, 3, ice);
  for (int side = -1; side <= 1; side += 2) {
    m.line(side * 8, -13, side * 8, -9, 3, ice);
    m.line(side * 8, -9, side, -1, 3, ice);
    m.line(side, -1, side, 1, 3, ice);
    m.line(side, 1, side * 8, 9, 3, ice);
    m.line(side * 8, 9, side * 8, 13, 3, ice);
  }
  if (seconds == 0) return;  // The controller also reports restart holds with no duration.
  constexpr unsigned duration = machine_policy::kMinOffMs / 1000;
  const unsigned remaining = seconds < duration ? seconds : duration;
  const int top = (7 * remaining + duration / 2) / duration;
  m.sand(-2 - top, top, -2, ice);
  m.sand(11, 7 - top, 4 + top, ice);
}

void snowflake(const Mark &m, lv_color_t ice) {
  // One shaft and one pair of branches, repeated around the center.
  for (int angle = 30; angle < 390; angle += 60) {
    const int cosA = lv_trigo_cos(angle), sinA = lv_trigo_sin(angle);
    auto rotated = [&](int along, int across) -> lv_point_t {
      return {lv_coord_t((along * cosA - across * sinA) / LV_TRIGO_SIN_MAX),
              lv_coord_t((along * sinA + across * cosA) / LV_TRIGO_SIN_MAX)};
    };
    const lv_point_t tip = rotated(15, 0), fork = rotated(7, 0);
    m.line(0, 0, tip.x, tip.y, 3, ice);
    for (int side = -1; side <= 1; side += 2) {
      const lv_point_t branch = rotated(11, side * 4);
      m.line(fork.x, fork.y, branch.x, branch.y, 3, ice);
    }
  }
}

void warningTriangle(const Mark &m, lv_color_t color) {
  m.line(0, -13, 14, 12, 3, color);
  m.line(14, 12, -14, 12, 3, color);
  m.line(-14, 12, 0, -13, 3, color);
  m.line(0, -4, 0, 2, 3, color);
  m.disc(0, 7, 1, color);
}

lv_obj_t *stripLabel(lv_obj_t *parent, int x, const char *value, const lv_font_t *font, lv_color_t ink) {
  lv_obj_t *label = lv_label_create(parent);
  lv_label_set_text(label, value);
  lv_obj_set_style_text_font(label, font, 0);
  lv_obj_set_style_text_color(label, ink, 0);
  lv_obj_align(label, LV_ALIGN_LEFT_MID, x, 0);
  return label;
}

}  // namespace

namespace front_ui {

void CoolingStrip::build(lv_obj_t *button, lv_coord_t railWidth, lv_color_t ice, lv_color_t warning) {
  button_ = button;
  railWidth_ = railWidth;
  ice_ = ice;
  warning_ = warning;
  lv_obj_t *gear = stripLabel(button, 0, LV_SYMBOL_SETTINGS, &lv_font_montserrat_32, lv_color_white());
  lv_obj_set_width(gear, railWidth);
  lv_obj_set_style_text_align(gear, LV_TEXT_ALIGN_CENTER, 0);
  temperature_ = stripLabel(button, railWidth + 29, "--", &lv_font_montserrat_32, lv_color_white());
  countdown_ = stripLabel(button, railWidth + 154, "", &lv_font_montserrat_28, ice);
  lv_obj_add_event_cb(button, draw, LV_EVENT_DRAW_MAIN_END, this);
}

void CoolingStrip::update(const char *fahrenheit, int16_t tankCx10, CoolingState state, uint16_t seconds) {
  if (strcmp(lv_label_get_text(temperature_), fahrenheit) != 0)
    lv_label_set_text(temperature_, fahrenheit);
  // The bulb is empty without a reading. Its column spans freezing to room temperature.
  const int column = tankCx10 == TEMP_UNREAD ? -1 : LV_CLAMP(0, int(tankCx10), 200) * 23 / 200;
  if (state != CoolingState::StartupWait) seconds = 0;
  if (state == state_ && column == column_ && seconds == seconds_) return;
  if (seconds != seconds_) {
    char time[12] = {};
    if (seconds) formatHoldTime(time, sizeof(time), seconds);
    lv_label_set_text(countdown_, time);
  }
  state_ = state;
  column_ = column;
  seconds_ = seconds;
  if (lv_obj_get_width(button_) > railWidth_) lv_obj_invalidate(button_);
}

void CoolingStrip::draw(lv_event_t *event) {
  const auto &strip = *static_cast<CoolingStrip *>(lv_event_get_user_data(event));
  if (lv_obj_get_width(strip.button_) <= strip.railWidth_) return;
  lv_area_t area;
  lv_obj_get_content_coords(strip.button_, &area);
  const lv_coord_t y = (area.y1 + area.y2 + 1) / 2;
  const lv_coord_t railEnd = area.x1 + strip.railWidth_;
  lv_draw_ctx_t *ctx = lv_event_get_draw_ctx(event);
  const Mark temperature{ctx, lv_coord_t(railEnd + 9), y};
  thermometer(temperature, strip.column_, strip.ice_, lv_obj_get_style_bg_color(strip.button_, LV_PART_MAIN));
  const Mark activity{ctx, lv_coord_t(railEnd + 134), y};
  switch (strip.state_) {
    case CoolingState::StartupWait:
    case CoolingState::RestartHold:
      hourglass(activity, strip.seconds_, strip.ice_);
      break;
    case CoolingState::Running:
      snowflake(activity, strip.ice_);
      break;
    case CoolingState::ProbeFault:
    case CoolingState::FreezeProtection:
    case CoolingState::Paused:
      warningTriangle(activity, strip.warning_);
      break;
    case CoolingState::Unavailable:
    case CoolingState::Idle:
      break;
  }
}

}  // namespace front_ui
