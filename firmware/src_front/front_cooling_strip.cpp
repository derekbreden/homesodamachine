#include "front_cooling_strip.h"
#include <string.h>

namespace {

constexpr lv_coord_t gearY = -40;
constexpr lv_coord_t activityY = 39;
constexpr lv_coord_t quietShift = 18;
constexpr lv_coord_t timeX = 32;
constexpr lv_coord_t hourglassX = 16;
constexpr lv_coord_t readingInset = 4;

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

void hourglass(const Mark &m, uint16_t seconds, lv_color_t ice) {
  m.line(-8, -11, 8, -11, 2, ice);
  m.line(-8, 11, 8, 11, 2, ice);
  for (int side = -1; side <= 1; side += 2) {
    m.line(side * 6, -10, side * 6, -7, 2, ice);
    m.line(side * 6, -7, 0, 0, 2, ice);
    m.line(0, 0, side * 6, 7, 2, ice);
    m.line(side * 6, 7, side * 6, 10, 2, ice);
  }
  if (seconds == 0) return;  // The controller also reports restart holds with no duration.
  constexpr unsigned duration = machine_policy::kMinOffMs / 1000;
  const unsigned remaining = seconds < duration ? seconds : duration;
  const int top = (5 * remaining + duration / 2) / duration;
  m.sand(-2 - top, top, -2, ice);
  m.sand(9, 5 - top, 4 + top, ice);
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

lv_obj_t *stripLabel(lv_obj_t *parent, const char *value, const lv_font_t *font, lv_color_t ink) {
  lv_obj_t *label = lv_label_create(parent);
  lv_label_set_text(label, value);
  lv_obj_set_style_text_font(label, font, 0);
  lv_obj_set_style_text_color(label, ink, 0);
  lv_obj_clear_flag(label, LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE);
  return label;
}

// Wide signed temperatures and long timers keep their units and final digit on the glass.
void fitReading(lv_obj_t *label, const char *text, lv_coord_t width,
                const lv_font_t *normal, const lv_font_t *smaller) {
  if (strcmp(lv_label_get_text(label), text) == 0) return;
  const size_t length = strlen(text);
  const lv_font_t *font = normal;
  if (lv_txt_get_width(text, length, font, 0, LV_TEXT_FLAG_NONE) > width) {
    font = smaller;
    if (lv_txt_get_width(text, length, font, 0, LV_TEXT_FLAG_NONE) > width)
      font = &lv_font_montserrat_20;
  }
  lv_obj_set_style_text_font(label, font, 0);
  lv_label_set_text(label, text);
}

}  // namespace

namespace front_ui {

void CoolingStrip::build(lv_obj_t *button, lv_coord_t railWidth, lv_color_t ice, lv_color_t warning) {
  button_ = button;
  railWidth_ = railWidth;
  ice_ = ice;
  warning_ = warning;
  gear_ = stripLabel(button, LV_SYMBOL_SETTINGS, &lv_font_montserrat_28, lv_color_white());
  temperature_ = stripLabel(button, "--°F", &lv_font_montserrat_36, lv_color_white());
  positionReadings();
  countdown_ = stripLabel(button, "", &lv_font_montserrat_28, ice);
  lv_obj_align(countdown_, LV_ALIGN_LEFT_MID, timeX, activityY);
  lv_obj_add_event_cb(button, draw, LV_EVENT_DRAW_MAIN_END, this);
}

void CoolingStrip::positionReadings() {
  // With no activity mark, center the gear and temperature as a pair.
  const lv_coord_t shift = state_ == CoolingState::Idle || state_ == CoolingState::Unavailable ? quietShift : 0;
  lv_obj_align(gear_, LV_ALIGN_CENTER, 0, gearY + shift);
  lv_obj_align(temperature_, LV_ALIGN_CENTER, 0, shift);
}

void CoolingStrip::update(const char *reading, CoolingState state, uint16_t seconds) {
  fitReading(temperature_, reading, railWidth_ - 2 * readingInset, &lv_font_montserrat_36, &lv_font_montserrat_28);
  if (state != CoolingState::StartupWait) seconds = 0;
  if (state == state_ && seconds == seconds_) return;
  if (seconds != seconds_) {
    char time[12] = {};
    if (seconds) formatHoldTime(time, sizeof(time), seconds);
    fitReading(countdown_, time, railWidth_ - timeX - readingInset, &lv_font_montserrat_28, &lv_font_montserrat_24);
  }
  if (state != state_) {
    state_ = state;
    positionReadings();
  }
  seconds_ = seconds;
  lv_obj_invalidate(button_);
}

void CoolingStrip::draw(lv_event_t *event) {
  const auto &strip = *static_cast<CoolingStrip *>(lv_event_get_user_data(event));
  lv_area_t area;
  lv_obj_get_content_coords(strip.button_, &area);
  const lv_coord_t y = (area.y1 + area.y2 + 1) / 2 + activityY;
  const lv_coord_t x = strip.seconds_ ? area.x1 + hourglassX : (area.x1 + area.x2 + 1) / 2;
  lv_draw_ctx_t *ctx = lv_event_get_draw_ctx(event);
  const Mark activity{ctx, x, y};
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
