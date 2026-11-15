#include <Arduino.h>
#include <esp_system.h>
#include <Arduino_GFX_Library.h>
#include <lvgl.h>
#include <Preferences.h>
#include <Wire.h>
#include "axs5106l.h"
#include "base_link.h"
#include "image_store.h"
#include "ble_image.h"
#include "ble_link.h"
#include "phone_trust.h"
#include "trust_text.h"
#include "fw_version.h"

// ════════════════════════════════════════════════════════════
//  ESP32-S3 Faucet Display — Flavor Selector + Prime Control
// ════════════════════════════════════════════════════════════
//
// Waveshare ESP32-S3-Touch-LCD-1.47 (172x320 IPS, JD9853 panel,
// AXS5106L capacitive touch) mounted at the end of the gooseneck.
// The selected flavor's logo fills the screen; a tap anywhere toggles
// it. The selection persists in NVS across power cycles.
//
// The logo changes locally on touch-down. J3 then carries that absolute
// selection to the main board, whose persisted value is authoritative;
// this board's NVS value is the immediate boot-logo cache.
// The glass shows one thing at a time and it fills the glass: the logo, or what
// the machine display has open (Prime's hold target, Ratio's two buttons), or a
// phone's trust ask, or why there is no soda. The machine display opens and
// closes Prime and Ratio; this glass follows.

// ── Big Blue service surfaces; flavor portraits fill the resting display ──
#define THEME_BG  lv_color_hex(0x1749d1)
#define COL_CARD   0x10319c
#define COL_CARD_ON 0x315fdb
#define COL_ACCENT 0xff9152
#define COL_TEXT   0xffffff
#define COL_DIM    0xdce6ff
#define COL_INK    0x153383
#define COL_GOOD   0x37c98b
#define COL_WARN   0xf0a83c
#define COL_OFF    0x6287e0

// ── The service surfaces' type ──
// LINE_DY_n is how far below the top of a line of size n in the faucet design LVGL's label
// of that size starts, so the two baselines meet.
#define LINE_DY_16       0
#define LINE_DY_20       1
#define LINE_DY_36       0

// ── Flavors ──
static const char *FLAVOR_NAMES[2] = {"Flavor 1", "Flavor 2"};
static uint8_t flavorArt[2] = {0, 1};
static lv_img_dsc_t flavorLogos[FLAVOR_ART_COUNT];

static uint8_t activeFlavor = 0;
static Preferences prefs;
static bool flavorStoreOpen = false;

// Persist is debounced off the tap path: NVS writes go to flash (and
// occasionally trigger page GC), so the tap handler only marks dirty.
static bool flavorDirty = false;
static bool flavorPersistError = false;
static unsigned long flavorChangedAt = 0;
static unsigned long flavorPersistAttemptAt = 0;
#define FLAVOR_PERSIST_DELAY_MS 2000

// ── Diagnostics (read via GET_DIAG) ──
static uint32_t maxLoopMs = 0;
static uint32_t toggleCount = 0;

// ── Main-board-owned prime-ready session ──
static PrimeSessionStatePayload primeSession = {};
static bool primeSessionKnown = false;
static bool primeVisible = false;
static bool primePressed = false;
static bool primeStopPending = false;
static bool primeLinkLost = false;
static uint32_t primeTokenState = 1;
static uint32_t primeHoldToken = 0;
static uint32_t primeHoldSessionToken = 0;
static uint32_t primeStopRevision = 0;
static bool primeStopRevisionKnown = false;
static uint8_t primeHoldChannel = 0;
static uint32_t primeElapsedShown = 0;
static uint32_t primeBaseGeneration = 0;
static unsigned long primeElapsedAnchorAt = 0;
static unsigned long primeStateAt = 0;
static unsigned long primeControlSentAt = 0;
static unsigned long primeLastUiAt = 0;

#define PRIME_CONTROL_RETRY_MS 500
#define PRIME_STATE_STALE_MS  1800

// ── Ratio, open on the machine display for one flavor ──
// The main board says which visit to the machine display's Ratio page stands and what both
// channels pour at. This glass steps the visit's flavor; the machine display opens and
// closes it. A step shows at once and stands against older truth until the main board
// answers it.
static RatioSessionStatePayload ratioSession = {};
static bool ratioSessionKnown = false;
static bool ratioLinkUp = false;
static unsigned long ratioSessionAt = 0;
static uint8_t ratioShown[2] = {FLAVOR_RATIO_DEFAULT, FLAVOR_RATIO_DEFAULT};
static bool ratioStepWanted = false;      // pressed, waiting for J3 to take it
static uint8_t ratioStepChannel = 0;
static uint8_t ratioStepValue = 0;
static uint8_t ratioStepsOwed = 0;        // taken by J3, not yet answered
static unsigned long ratioStepSentAt = 0;
static uint32_t ratioSaidToken = 0;       // the visit whose layout the console heard

#define RATIO_REPLY_MS        2500
#define RATIO_STALE_MS        1800

// ── Backlight / idle dimming ──
// Full brightness while the appliance considers anyone present, fading to a
// glanceable dim level when the main board says both glasses are done. The
// quiet stretch is counted there, across both, so this head does not dim while
// a hand is at the enclosure. While dimmed, the first tap only wakes the screen
// (consumed in onTap); serial flavor commands wake and apply.
#define BL_FULL_DUTY   255
#define BL_DIM_DUTY    8    // idle glow — soft but clearly visible in a dark room; 0 is off
#define BL_FADE_STEP   4    // duty per loop pass; fade spans (FULL-DIM)/STEP passes

static uint8_t blDuty = BL_FULL_DUTY;
static uint8_t blTarget = BL_FULL_DUTY;
static bool dimmed = false;
static bool idleAsleepWanted = false;   // what the main board last said
static unsigned long lastInputTime = 0;

// A finger here is presence the main board keeps for both glasses, and J3 takes
// MSG_TOUCH without owing an acknowledgement for it — a full TinyProto window or
// a link a moment from reconnecting drops one silently. Left dropped, the main
// board stays asleep, the enclosure stays dark through every tap on this glass,
// and the idle heartbeat dims this one back down under the finger that just woke
// it. So the touch is repeated until an idle state comes back agreeing the
// machine is awake, and the dim is held off while that is outstanding.
static unsigned long touchUnconfirmedSince = 0;
static unsigned long touchConfirmRetryMs = 0;
#define TOUCH_CONFIRM_RETRY_MS   750
#define TOUCH_CONFIRM_GIVEUP_MS  10000

// ── Pin assignments (fixed by Waveshare ESP32-S3-Touch-LCD-1.47) ──

// Display SPI (JD9853, 172x320, driven via the ST7789 command set)
#define LCD_DC    45
#define LCD_CS    21
#define LCD_SCK   38
#define LCD_MOSI  39
#define LCD_RST   40
#define LCD_BL    46

// Touch (AXS5106L)
#define TOUCH_SDA 42
#define TOUCH_SCL 41
#define TOUCH_RST 47
#define TOUCH_INT 48

#define SCREEN_W  172
#define SCREEN_H  320
#define ROTATION  0  // USB connector points down on the faucet mount

// ── Hardware objects ──
Arduino_DataBus *bus = new Arduino_ESP32SPI(
    LCD_DC, LCD_CS, LCD_SCK, LCD_MOSI, GFX_NOT_DEFINED, FSPI, true);

// The JD9853 speaks the ST7789 command set for addressing; panel-specific
// registers are programmed in lcdRegInit() after begin().
Arduino_GFX *gfx = new Arduino_ST7789(
    bus, LCD_RST, 0 /* rotation */, false /* IPS */,
    SCREEN_W, SCREEN_H,
    34 /* col offset 1 */, 0 /* row offset 1 */,
    34 /* col offset 2 */, 0 /* row offset 2 */);

AXS5106L touch(TOUCH_RST, TOUCH_INT);

// ── LVGL display buffer ──
static lv_disp_draw_buf_t draw_buf;
static lv_color_t *lvgl_buf;
#define LVGL_BUF_LINES 40

// ── UI objects ──
static lv_obj_t *logoImg;
static lv_obj_t *primeLayer;
static lv_obj_t *otaLayer, *otaTitle, *otaFill, *otaPct;
static lv_obj_t *primeHoldBtn;
static lv_obj_t *primeFlavorLbl, *primeHoldLbl, *primeStatusLbl;
static lv_obj_t *ratioLayer, *ratioMoreBtn, *ratioMoreMark, *ratioMoreLbl;
static lv_obj_t *ratioLighterBtn, *ratioLighterMark, *ratioLighterLbl;
static lv_obj_t *ratioFlavorLbl, *ratioValueLbl;
static lv_obj_t *trustLayer, *trustTitleLbl, *trustBodyLbl;
static uint8_t   trustShownAsk = 0;   // the ask standing; 0 while none is
static lv_obj_t *noticeLayer, *noticeTitleLbl, *noticeBodyLbl, *noticeTrack, *noticeFill;
static uint8_t   noticeKind = NOTICE_NONE;   // what the main board says stops the soda
static uint8_t   noticeProgress = 0;         // a sweep's count, percent
static bool      noticeFlowing = false;      // the meter is turning now
static bool      noticeBelow = false;        // a move: the float has passed the low reed
static uint8_t   noticeFace = 0xFF;          // which words the notice wears, NOTICE_FACE_*; none yet
static uint8_t   noticeFaceSaid = 0xFF;      // the face whose layout the console last heard
static bool trustPressed = false;

// What fills the glass, one at a time; an update stands over all of them on its own layer.
enum : uint8_t { FACE_LOGO, FACE_NOTICE, FACE_RATIO, FACE_PRIME, FACE_TRUST };
static uint8_t faceShown = FACE_LOGO;
static bool touchIsDown = false;
static lv_indev_t *touchInput = nullptr;

// ════════════════════════════════════════════════════════════
//  JD9853 panel init (register sequence published by Waveshare)
// ════════════════════════════════════════════════════════════

static void lcdRegInit() {
  static const uint8_t init_operations[] = {
      BEGIN_WRITE,
      WRITE_COMMAND_8, 0x11,  // Sleep out
      END_WRITE,
      DELAY, 120,

      BEGIN_WRITE,
      WRITE_C8_D16, 0xDF, 0x98, 0x53,
      WRITE_C8_D8, 0xB2, 0x23,

      WRITE_COMMAND_8, 0xB7,
      WRITE_BYTES, 4,
      0x00, 0x47, 0x00, 0x6F,

      WRITE_COMMAND_8, 0xBB,
      WRITE_BYTES, 6,
      0x1C, 0x1A, 0x55, 0x73, 0x63, 0xF0,

      WRITE_C8_D16, 0xC0, 0x44, 0xA4,
      WRITE_C8_D8, 0xC1, 0x16,

      WRITE_COMMAND_8, 0xC3,
      WRITE_BYTES, 8,
      0x7D, 0x07, 0x14, 0x06, 0xCF, 0x71, 0x72, 0x77,

      WRITE_COMMAND_8, 0xC4,
      WRITE_BYTES, 12,
      0x00, 0x00, 0xA0, 0x79, 0x0B, 0x0A, 0x16, 0x79, 0x0B, 0x0A, 0x16, 0x82,

      WRITE_COMMAND_8, 0xC8,
      WRITE_BYTES, 32,
      0x3F, 0x32, 0x29, 0x29, 0x27, 0x2B, 0x27, 0x28, 0x28, 0x26, 0x25, 0x17,
      0x12, 0x0D, 0x04, 0x00, 0x3F, 0x32, 0x29, 0x29, 0x27, 0x2B, 0x27, 0x28,
      0x28, 0x26, 0x25, 0x17, 0x12, 0x0D, 0x04, 0x00,

      WRITE_COMMAND_8, 0xD0,
      WRITE_BYTES, 5,
      0x04, 0x06, 0x6B, 0x0F, 0x00,

      WRITE_C8_D16, 0xD7, 0x00, 0x30,
      WRITE_C8_D8, 0xE6, 0x14,
      WRITE_C8_D8, 0xDE, 0x01,

      WRITE_COMMAND_8, 0xB7,
      WRITE_BYTES, 5,
      0x03, 0x13, 0xEF, 0x35, 0x35,

      WRITE_COMMAND_8, 0xC1,
      WRITE_BYTES, 3,
      0x14, 0x15, 0xC0,

      WRITE_C8_D16, 0xC2, 0x06, 0x3A,
      WRITE_C8_D16, 0xC4, 0x72, 0x12,
      WRITE_C8_D8, 0xBE, 0x00,
      WRITE_C8_D8, 0xDE, 0x02,

      WRITE_COMMAND_8, 0xE5,
      WRITE_BYTES, 3,
      0x00, 0x02, 0x00,

      WRITE_COMMAND_8, 0xE5,
      WRITE_BYTES, 3,
      0x01, 0x02, 0x00,

      WRITE_C8_D8, 0xDE, 0x00,
      WRITE_C8_D8, 0x35, 0x00,  // Tearing effect on
      WRITE_C8_D8, 0x3A, 0x05,  // RGB565

      WRITE_COMMAND_8, 0x2A,
      WRITE_BYTES, 4,
      0x00, 0x22, 0x00, 0xCD,

      WRITE_COMMAND_8, 0x2B,
      WRITE_BYTES, 4,
      0x00, 0x00, 0x01, 0x3F,

      WRITE_C8_D8, 0xDE, 0x02,

      WRITE_COMMAND_8, 0xE5,
      WRITE_BYTES, 3,
      0x00, 0x02, 0x00,

      WRITE_C8_D8, 0xDE, 0x00,
      WRITE_C8_D8, 0x36, 0x00,  // MADCTL
      WRITE_COMMAND_8, 0x21,    // Inversion on
      END_WRITE,

      DELAY, 10,

      BEGIN_WRITE,
      WRITE_COMMAND_8, 0x29,  // Display on
      END_WRITE,
  };
  bus->batchOperation(init_operations, sizeof(init_operations));
}

// ════════════════════════════════════════════════════════════
//  LVGL callbacks
// ════════════════════════════════════════════════════════════

static void lvglFlush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
  uint32_t w = area->x2 - area->x1 + 1;
  uint32_t h = area->y2 - area->y1 + 1;
  gfx->draw16bitRGBBitmap(area->x1, area->y1, (uint16_t *)&color_p->full, w, h);
  lv_disp_flush_ready(disp);
}

static void touchpadRead(lv_indev_drv_t *drv, lv_indev_data_t *data) {
  uint16_t x, y;
  if (touch.getTouch(&x, &y)) {
    touchIsDown = true;
    lastInputTime = millis();
    data->point.x = x;
    data->point.y = y;
    data->state = LV_INDEV_STATE_PRESSED;
  } else {
    touchIsDown = false;
    data->state = LV_INDEV_STATE_RELEASED;
  }
}

// ════════════════════════════════════════════════════════════
//  The service surfaces' parts
// ════════════════════════════════════════════════════════════

#define BAR_W (SCREEN_W - 32)
#define BAR_H 8

// The design sets two lines of a size as far apart as its line box, which is taller than
// LVGL's line at every size but the largest.
static lv_coord_t designLineSpace(const lv_font_t *font) {
  return font == &lv_font_montserrat_36 ? 0 : 2;
}

// A line of the glass's type, or two, centered across the whole width with its top at y.
static lv_obj_t *lineLabel(lv_obj_t *parent, lv_coord_t y, const lv_font_t *font,
                           uint32_t color, const char *text) {
  lv_obj_t *label = lv_label_create(parent);
  lv_obj_set_width(label, SCREEN_W);
  lv_obj_set_pos(label, 0, y);
  lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_set_style_text_font(label, font, 0);
  lv_obj_set_style_text_color(label, lv_color_hex(color), 0);
  lv_obj_set_style_text_line_space(label, designLineSpace(font), 0);
  lv_label_set_text(label, text);
  return label;
}

// A bar on the glass's blue: the track in the off blue, the count in white.
static lv_obj_t *barTrack(lv_obj_t *parent, lv_coord_t y, lv_obj_t **fill) {
  lv_obj_t *track = lv_obj_create(parent);
  lv_obj_remove_style_all(track);
  lv_obj_set_pos(track, (SCREEN_W - BAR_W) / 2, y);
  lv_obj_set_size(track, BAR_W, BAR_H);
  lv_obj_set_style_radius(track, BAR_H / 2, 0);
  lv_obj_set_style_bg_color(track, lv_color_hex(COL_OFF), 0);
  lv_obj_set_style_bg_opa(track, LV_OPA_COVER, 0);
  lv_obj_clear_flag(track, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);

  *fill = lv_obj_create(track);
  lv_obj_remove_style_all(*fill);
  lv_obj_set_pos(*fill, 0, 0);
  lv_obj_set_size(*fill, 0, BAR_H);
  lv_obj_set_style_radius(*fill, BAR_H / 2, 0);
  lv_obj_set_style_bg_color(*fill, lv_color_hex(COL_TEXT), 0);
  lv_obj_set_style_bg_opa(*fill, LV_OPA_COVER, 0);
  lv_obj_clear_flag(*fill, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
  return track;
}

// A layer the size of the glass, in one colour, that takes a press nothing on it takes.
static lv_obj_t *wholeGlass(lv_obj_t *scr, lv_color_t bg, lv_event_cb_t cb, lv_event_code_t code) {
  lv_obj_t *layer = lv_obj_create(scr);
  lv_obj_remove_style_all(layer);
  lv_obj_set_pos(layer, 0, 0);
  lv_obj_set_size(layer, SCREEN_W, SCREEN_H);
  lv_obj_set_style_bg_color(layer, bg, 0);
  lv_obj_set_style_bg_opa(layer, LV_OPA_COVER, 0);
  lv_obj_clear_flag(layer, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_add_flag(layer, LV_OBJ_FLAG_CLICKABLE);
  if (cb) lv_obj_add_event_cb(layer, cb, code, NULL);
  lv_obj_add_flag(layer, LV_OBJ_FLAG_HIDDEN);
  return layer;
}

// ════════════════════════════════════════════════════════════
//  Flavor state
// ════════════════════════════════════════════════════════════

// Which logo an index actually resolves to. A custom index whose slot is empty
// falls back to the factory logo of the same channel rather than drawing
// nothing: a picture can be removed while a channel is still wearing it.
static uint8_t resolveArt(uint8_t art, uint8_t channel) {
  const uint8_t slot = (art < FLAVOR_ART_FACTORY) ? flavorArtFactorySlot(art)
                                                  : flavorArtCustomSlot(art);
  if (art >= FLAVOR_ART_FACTORY && slot >= FLAVOR_ART_CUSTOM) return (uint8_t)(channel & 1);
  if (imageStorePixels(slot, 0)) return art;
  return (uint8_t)(channel & 1);
}

// Every descriptor, rebound. The custom ones point straight into mapped flash,
// so this costs a pointer each and has to be redone whenever the store moves —
// a written or erased slot remaps the partition underneath these.
static void bindLogos() {
  for (uint8_t i = 0; i < FLAVOR_ART_COUNT; i++) {
    flavorLogos[i].header.cf = LV_IMG_CF_TRUE_COLOR;
    flavorLogos[i].header.always_zero = 0;
    flavorLogos[i].header.w = SCREEN_W;
    flavorLogos[i].header.h = SCREEN_H;
    flavorLogos[i].data_size = SCREEN_W * SCREEN_H * sizeof(uint16_t);
    // This glass draws the largest rendition; the store keeps all three, so a
    // machine display can be re-provisioned from here with no phone in the room.
    const uint8_t slot = (i < FLAVOR_ART_FACTORY) ? flavorArtFactorySlot(i)
                                                  : flavorArtCustomSlot(i);
    const uint16_t *px = imageStorePixels(slot, 0);
    if (!px) px = imageStorePixels(flavorArtFactorySlot(0), 0);
    flavorLogos[i].data = (const uint8_t *)px;
  }
}

static void applyFlavorUi() {
  const uint8_t ch = activeFlavor & 1;
  lv_img_set_src(logoImg, &flavorLogos[resolveArt(flavorArt[ch], ch)]);
}

// The main board's resulting truth for the pair. Rendered immediately when the
// channel on screen is one whose logo moved.
// What the main board currently says each channel wears, for the phone.
void faucetReadFlavorArt(uint8_t out[2]) { out[0] = flavorArt[0]; out[1] = flavorArt[1]; }

void faucetApplyFlavorArt(const uint8_t art[2]) {
  bool moved = false;
  for (uint8_t i = 0; i < 2; i++) {
    if (art[i] < FLAVOR_ART_COUNT && flavorArt[i] != art[i]) {
      flavorArt[i] = art[i];
      moved = true;
    }
  }
  if (moved && logoImg) applyFlavorUi();
  // A phone watching the machine should see a change made on either glass as
  // fast as one it made itself.
  if (moved) bleImagePublishArt();
}

// Every finger on this glass, and nothing else. wakeBacklight() alone will not
// do: the main board's own idle publication and an arriving transfer both wake
// this screen, and neither is a touch to report back.
static void faucetTouched() {
  if (!touchUnconfirmedSince) {
    touchUnconfirmedSince = millis() ? millis() : 1;
    touchConfirmRetryMs = millis();
  }
  baseLinkTouched();
}

static void wakeBacklight() {
  // The main board is being told a finger landed. Take the awake state now, or
  // the loop re-dims against the sleep it last published before the answer.
  idleAsleepWanted = false;
  dimmed = false;
  blDuty = blTarget = BL_FULL_DUTY;
  ledcWrite(LCD_BL, blDuty);
  Serial.println("Backlight wake");
}

static void applyFlavor(uint8_t f) {
  if (f > 1 || f == activeFlavor) return;
  lastInputTime = millis();
  if (dimmed) wakeBacklight();
  activeFlavor = f;
  applyFlavorUi();
  flavorDirty = true;
  flavorPersistError = !flavorStoreOpen;
  flavorChangedAt = millis();
}

static void selectFlavorLocally(uint8_t f) {
  if (f > 1 || f == activeFlavor) return;
  applyFlavor(f);
  toggleCount++;
  Serial.printf("Flavor -> %d (%s)\n", activeFlavor + 1, FLAVOR_NAMES[activeFlavor]);
  baseLinkSelect(activeFlavor, true);
}

static void acceptBaseFlavor(uint8_t f) {
  if (f > 1 || f == activeFlavor) return;
  applyFlavor(f);
  Serial.printf("Main board flavor -> %d (%s)\n",
                activeFlavor + 1, FLAVOR_NAMES[activeFlavor]);
}

static void onTap(lv_event_t *e) {
  if (dimmed) {  // a tap on a dimmed screen only wakes it
    lastInputTime = millis();
    wakeBacklight();
    faucetTouched();
    return;
  }
  const uint8_t before = activeFlavor;
  selectFlavorLocally(activeFlavor ^ 1);
  // A tap that changed nothing sent nothing, and is still a finger.
  if (activeFlavor == before) faucetTouched();
}

// ════════════════════════════════════════════════════════════
//  Shared prime-ready mode
// ════════════════════════════════════════════════════════════

static uint32_t nextPrimeToken() {
  primeTokenState += 0x9E3779B9u;
  if (primeTokenState == 0) ++primeTokenState;
  return primeTokenState;
}

static void primeMarkStopPending() {
  if (primeStopPending) return;
  primeStopPending = true;
  primeStopRevisionKnown = primeSessionKnown && primeHoldSessionToken != 0 &&
                           primeSession.sessionToken == primeHoldSessionToken;
  primeStopRevision = primeStopRevisionKnown ? primeSession.revision : 0;
}

static void primeClearStopPending() {
  primeStopPending = false;
  primeStopRevisionKnown = false;
  primeStopRevision = 0;
}

static uint32_t displayedPrimeElapsed() {
  uint32_t elapsed = primeSession.elapsedMs;
  if (primeSession.phase == PRIME_SESSION_RUNNING && !primeLinkLost) {
    elapsed += millis() - primeElapsedAnchorAt;
    if (elapsed < primeElapsedShown) elapsed = primeElapsedShown;
  }
  if (elapsed > PRIME_MAX_MS) elapsed = PRIME_MAX_MS;
  return elapsed;
}

// How the last hold ended, in the words under the target. The ceiling says its own time.
static const char *primeOutcomeName(uint8_t outcome) {
  switch (outcome) {
    case PRIME_OUTCOME_STOPPED:       return "Stopped";
    case PRIME_OUTCOME_TIMEOUT:       return "Hold lost";
    case PRIME_OUTCOME_REFUSED:       return "Refused";
    case PRIME_OUTCOME_CANCELED:      return "Canceled";
    case PRIME_OUTCOME_LEASE_EXPIRED: return "Session lost";
    default:                          return "";
  }
}

#define BULLET " \xE2\x80\xA2 "

static void refreshPrimeStatus(bool force = false) {
  if (!primeVisible || !primeStatusLbl) return;

  const uint32_t elapsed = displayedPrimeElapsed();
  if (!force && primeSession.phase == PRIME_SESSION_RUNNING &&
      elapsed / 100 == primeElapsedShown / 100) return;
  primeElapsedShown = elapsed;

  const unsigned long whole = (unsigned long)elapsed / 1000;
  const unsigned long tenth = ((unsigned long)elapsed % 1000) / 100;
  char status[40];
  if (primeLinkLost) {
    snprintf(status, sizeof(status), "Link lost");
  } else if (primeStopPending) {
    status[0] = '\0';
  } else if (primeSession.phase == PRIME_SESSION_RUNNING) {
    snprintf(status, sizeof(status), "%s" BULLET "%lu.%lu s",
             primeSession.owner == PRIME_OWNER_FAUCET ? "Here" : "Machine", whole, tenth);
  } else if (primeSession.outcome == PRIME_OUTCOME_LIMIT) {
    snprintf(status, sizeof(status), "%lu s limit", (unsigned long)(PRIME_MAX_MS / 1000));
  } else if (primeSession.outcome != PRIME_OUTCOME_NONE) {
    snprintf(status, sizeof(status), "%s" BULLET "%lu.%lu s",
             primeOutcomeName(primeSession.outcome), whole, tenth);
  } else {
    status[0] = '\0';
  }
  if (strcmp(lv_label_get_text(primeStatusLbl), status) != 0)
    lv_label_set_text(primeStatusLbl, status);
}

static void renderPrime(bool force = false) {
  if (!primeVisible || !primeHoldLbl || !primeHoldBtn) return;
  static uint8_t shownPhase = 0xFF;
  static uint8_t shownOwner = 0xFF;
  static uint8_t shownOutcome = 0xFF;
  static bool shownPressed = false;
  static bool shownStop = false;
  static bool shownLost = false;

  const bool changed = force || shownPhase != primeSession.phase ||
                       shownOwner != primeSession.owner ||
                       shownOutcome != primeSession.outcome ||
                       shownPressed != primePressed ||
                       shownStop != primeStopPending ||
                       shownLost != primeLinkLost;
  if (!changed) return;
  shownPhase = primeSession.phase;
  shownOwner = primeSession.owner;
  shownOutcome = primeSession.outcome;
  shownPressed = primePressed;
  shownStop = primeStopPending;
  shownLost = primeLinkLost;

  if (primeLinkLost) {
    lv_label_set_text(primeHoldLbl, "Reconnecting");
    lv_obj_set_style_bg_color(primeHoldBtn, lv_color_hex(COL_DIM), 0);
  } else if (primeStopPending) {
    lv_label_set_text(primeHoldLbl, "Stopping");
    lv_obj_set_style_bg_color(primeHoldBtn, lv_color_hex(COL_DIM), 0);
  } else if (primeSession.phase == PRIME_SESSION_RUNNING) {
    lv_label_set_text(primeHoldLbl, "Priming");
    lv_obj_set_style_bg_color(primeHoldBtn, lv_color_hex(COL_GOOD), 0);
  } else if (primePressed) {
    lv_label_set_text(primeHoldLbl, "Starting");
    lv_obj_set_style_bg_color(primeHoldBtn, lv_color_hex(COL_ACCENT), 0);
  } else {
    lv_label_set_text(primeHoldLbl, "Hold to prime");
    lv_obj_set_style_bg_color(primeHoldBtn, lv_color_hex(COL_ACCENT), 0);
  }
  lv_label_set_text(primeFlavorLbl, FLAVOR_NAMES[primeSession.channel & 1]);
  // LV_STATE_PRESSED otherwise hides the authoritative green state beneath
  // the generic touch color for the entire time the user's finger is down.
  const bool blocked = primeLinkLost || primeStopPending;
  lv_obj_set_style_bg_color(
      primeHoldBtn,
      lv_color_hex(blocked ? COL_DIM
                   : primeSession.phase == PRIME_SESSION_RUNNING ? COL_GOOD : COL_ACCENT),
      LV_STATE_PRESSED);
  refreshPrimeStatus(true);
}

static void faceService(lv_timer_t *);

// Whether the main board's Prime session is up; which face has the glass is faceService's.
static void setPrimeVisible(bool visible) {
  if (!primeLayer || visible == primeVisible) return;
  primeVisible = visible;
  if (visible) renderPrime(true);
  faceService(nullptr);
}

// An image is arriving over J3. esp_ota_write stalls this board for whole
// seconds at a time and LVGL only runs between chunks, so the panel is painted
// once here and then only its percentage changes — a screen that says what is
// happening rather than one that looks hung.
// A picture arriving is not firmware arriving: this board stays up, keeps its
// link and comes back to the same screen. Only the wording differs.
void faucetApplyImage(bool active, uint8_t percent) {
  faucetApplyOta(active, percent);
}

// Every logo descriptor points into the mapped store, and writing a slot
// remaps it. Rebinding is a pointer each.
void faucetRebindLogos() {
  bindLogos();
  if (logoImg) applyFlavorUi();
}

void faucetApplyOta(bool active, uint8_t percent) {
  if (!otaLayer) {
    otaLayer = lv_obj_create(lv_scr_act());
    lv_obj_remove_style_all(otaLayer);
    lv_obj_set_pos(otaLayer, 0, 0);
    lv_obj_set_size(otaLayer, SCREEN_W, SCREEN_H);
    lv_obj_set_style_bg_color(otaLayer, THEME_BG, 0);
    lv_obj_set_style_bg_opa(otaLayer, LV_OPA_COVER, 0);
    lv_obj_clear_flag(otaLayer, LV_OBJ_FLAG_SCROLLABLE);

    otaTitle = lineLabel(otaLayer, 118 + LINE_DY_20, &lv_font_montserrat_20, COL_TEXT, "Updating");
    barTrack(otaLayer, 156, &otaFill);
    otaPct = lineLabel(otaLayer, 176 + LINE_DY_16, &lv_font_montserrat_16, COL_DIM, "");
  }

  // Nothing dims or sleeps mid-transfer, and the screen must be lit to be read
  // — including on the call that says it finished. The last thing a transfer
  // does is report inactive at 100%, so waking below the return here is what
  // put the glass back to sleep at the one moment there was something new on
  // it to look at.
  lastInputTime = millis();
  wakeBacklight();

  if (!active) {
    lv_obj_add_flag(otaLayer, LV_OBJ_FLAG_HIDDEN);
    return;
  }
  lv_label_set_text_fmt(otaPct, "%u%%", (unsigned)percent);
  lv_obj_set_width(otaFill, (lv_coord_t)(BAR_W * (uint32_t)(percent > 100 ? 100 : percent) / 100));
  lv_obj_move_foreground(otaLayer);
  lv_obj_clear_flag(otaLayer, LV_OBJ_FLAG_HIDDEN);
  lv_timer_handler();
}

void faucetApplyIdle(bool asleep) {
  idleAsleepWanted = asleep;
  // Awake is the main board answering for a reported finger — it leaves sleep
  // for nothing else. Asleep says only that it has not heard ours yet.
  if (!asleep) touchUnconfirmedSince = 0;
  if (!asleep && dimmed) {
    lastInputTime = millis();
    wakeBacklight();
  }
}

// A press on a dimmed service surface only wakes it.
static bool touchWakesOnly() {
  if (!dimmed) return false;
  lastInputTime = millis();
  wakeBacklight();
  faucetTouched();
  // Waking consumes the whole physical touch, even if the finger slides from
  // one target into another before it lifts.
  if (touchInput) lv_indev_wait_release(touchInput);
  return true;
}

static void onPrimeHold(lv_event_t *e) {
  const lv_event_code_t code = lv_event_get_code(e);
  if (code == LV_EVENT_PRESSED) {
    if (touchWakesOnly() || !primeVisible || primeLinkLost || primeStopPending ||
        primeSession.phase != PRIME_SESSION_READY) return;
    lastInputTime = millis();
    primePressed = true;
    primeClearStopPending();
    primeHoldToken = nextPrimeToken();
    primeHoldChannel = primeSession.channel;
    primeHoldSessionToken = primeSession.sessionToken;
    baseLinkPrimeHoldStart(primeHoldChannel, primeHoldSessionToken, primeHoldToken);
    primeControlSentAt = millis();
    renderPrime(true);
  } else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
    if (primePressed) {
      primePressed = false;
      primeMarkStopPending();
      baseLinkPrimeHoldStop(primeHoldChannel, primeHoldSessionToken, primeHoldToken);
      primeControlSentAt = millis();
      renderPrime(true);
    }
    if (code == LV_EVENT_PRESS_LOST) {
      // LVGL otherwise re-hit-tests this still-pressed sample and can deliver a
      // fresh PRESSED to whatever lies under the finger.
      lv_indev_t *indev = lv_indev_get_act();
      if (indev) {
        lv_indev_wait_release(indev);
        lv_indev_reset(indev, nullptr);
      }
    }
  }
}

static void acceptBasePrime(const PrimeSessionStatePayload &state, uint32_t generation) {
  if (state.phase > PRIME_SESSION_RUNNING || state.channel > PUMP_CHANNEL_B ||
      state.owner > PRIME_OWNER_FAUCET || state.outcome > PRIME_OUTCOME_LEASE_EXPIRED) return;

  if (generation != primeBaseGeneration) {
    // TinyProto's connection epoch is the faucet's proof that a lower revision
    // can belong to a rebooted main board rather than an out-of-order frame.
    primeBaseGeneration = generation;
    if (primePressed) {
      primePressed = false;
      // Capture the old same-session revision before forgetting the previous
      // connection epoch, so a later READY/H2 can supersede a lost STOP/H1.
      primeMarkStopPending();
    }
    primeSessionKnown = false;
  }

  if (primeSessionKnown) {
    const int32_t revisionDelta = (int32_t)(state.revision - primeSession.revision);
    if (revisionDelta < 0) return;
    if (revisionDelta == 0) {
      primeStateAt = millis();
      const bool recovered = primeLinkLost;
      primeLinkLost = false;
      if (state.phase != PRIME_SESSION_RUNNING ||
          primeSession.phase != PRIME_SESSION_RUNNING ||
          state.sessionToken != primeSession.sessionToken ||
          state.holdToken != primeSession.holdToken ||
          state.owner != primeSession.owner || state.elapsedMs < primeSession.elapsedMs) {
        if (recovered) renderPrime(true);
        return;
      }
      primeSession.elapsedMs = state.elapsedMs;
      primeElapsedAnchorAt = millis();
      if (recovered) renderPrime(true);
      return;
    }
  }

  // A retry belongs to the exact session in which the physical gesture began.
  // If OFF was coalesced and the next accepted snapshot is already a new
  // session, never retarget an old hold to that new main board token.
  const bool holdRetargeted = (primePressed || primeStopPending) &&
                              state.sessionToken != primeHoldSessionToken;
  if (holdRetargeted) {
    baseLinkPrimeDiscard();
    primePressed = false;
    primeClearStopPending();
    primeHoldToken = 0;
    primeHoldSessionToken = 0;
  }

  const bool wasKnown = primeSessionKnown;
  const PrimeSessionStatePayload previous = primeSession;
  primeSession = state;
  primeSessionKnown = true;
  primeStateAt = primeElapsedAnchorAt = millis();
  primeLinkLost = false;

  if (state.phase == PRIME_SESSION_OFF) {
    primePressed = false;
    primeClearStopPending();
    primeHoldToken = 0;
    primeHoldSessionToken = 0;
    primeElapsedShown = state.elapsedMs;
    setPrimeVisible(false);
    return;
  }

  const bool entering = !wasKnown || previous.phase == PRIME_SESSION_OFF ||
                        previous.sessionToken != state.sessionToken;
  const bool runStarted = state.phase == PRIME_SESSION_RUNNING &&
                          (!wasKnown || previous.phase != PRIME_SESSION_RUNNING ||
                           previous.holdToken != state.holdToken);
  const bool runEnded = wasKnown && previous.phase == PRIME_SESSION_RUNNING &&
                        state.phase != PRIME_SESSION_RUNNING;
  if (entering || runStarted || runEnded) {
    lastInputTime = millis();
    if (dimmed) wakeBacklight();
  }
  setPrimeVisible(true);

  if (state.phase == PRIME_SESSION_RUNNING) {
    const bool ourRun = state.owner == PRIME_OWNER_FAUCET &&
                        state.sessionToken == primeHoldSessionToken &&
                        state.holdToken == primeHoldToken;
    if (primePressed && !ourRun) {
      // The enclosure won a simultaneous press. Retire any unsent local START
      // with an absolute STOP before dropping the local held state.
      primePressed = false;
      primeMarkStopPending();
      baseLinkPrimeHoldStop(primeHoldChannel, primeHoldSessionToken, primeHoldToken);
      primeControlSentAt = millis();
    }
  } else {
    if (state.sessionToken == primeHoldSessionToken &&
        state.holdToken == primeHoldToken && state.outcome != PRIME_OUTCOME_NONE) {
      primePressed = false;
      primeClearStopPending();
      primeHoldToken = 0;
      primeHoldSessionToken = 0;
    }
  }

  primeElapsedShown = state.elapsedMs;
  renderPrime(true);
  // A hold starting or ending decides whether a trust ask may have the glass.
  faceService(nullptr);
}

static void primeService(const BaseLinkStatus &link) {
  if (!primeVisible) return;
  const unsigned long now = millis();

  const bool stale = !link.connected || !primeStateAt ||
                     now - primeStateAt >= PRIME_STATE_STALE_MS;
  if (stale) {
    if (primePressed) {
      primePressed = false;
      primeMarkStopPending();
      baseLinkPrimeHoldStop(primeHoldChannel, primeHoldSessionToken, primeHoldToken);
      primeControlSentAt = now;
    }
    if (!primeLinkLost) {
      primeLinkLost = true;
      lastInputTime = now;
      renderPrime(true);
    }
  }

  if (!link.connected) return;

  if (primeStopPending) {
    const bool sameRun = primeSession.phase == PRIME_SESSION_RUNNING &&
                         primeSession.owner == PRIME_OWNER_FAUCET &&
                         primeSession.sessionToken == primeHoldSessionToken &&
                         primeSession.holdToken == primeHoldToken;
    const bool otherRun = primeSession.phase == PRIME_SESSION_RUNNING && !sameRun;
    const bool terminalReady = primeSession.phase == PRIME_SESSION_READY &&
                               primeSession.sessionToken == primeHoldSessionToken &&
                               primeSession.holdToken == primeHoldToken &&
                               primeSession.outcome >= PRIME_OUTCOME_STOPPED &&
                               primeSession.outcome <= PRIME_OUTCOME_REFUSED;
    // A newer H2 state in this same session supersedes a lost terminal reply
    // for H1 just as conclusively as receiving READY/H1 itself.
    const bool superseded = primeStopRevisionKnown &&
                            primeStateSupersedesPendingStop(
                                primeSession, primeHoldSessionToken,
                                primeHoldToken, PRIME_OWNER_FAUCET,
                                primeStopRevision);
    if (otherRun || terminalReady || superseded) {
      primeClearStopPending();
      primeHoldToken = 0;
      primeHoldSessionToken = 0;
      renderPrime(true);
    } else if (now - primeControlSentAt >= PRIME_CONTROL_RETRY_MS) {
      baseLinkPrimeHoldStop(primeHoldChannel, primeHoldSessionToken, primeHoldToken);
      primeControlSentAt = now;
    }
    return;
  }

  if (primePressed && !primeLinkLost && now - primeControlSentAt >= PRIME_TICK_MS) {
    const bool acknowledged = primeSession.phase == PRIME_SESSION_RUNNING &&
                              primeSession.owner == PRIME_OWNER_FAUCET &&
                              primeSession.sessionToken == primeHoldSessionToken &&
                              primeSession.holdToken == primeHoldToken;
    if (acknowledged) {
      baseLinkPrimeHoldTick(primeHoldChannel, primeHoldSessionToken, primeHoldToken);
    } else {
      baseLinkPrimeHoldStart(primeHoldChannel, primeHoldSessionToken, primeHoldToken);
    }
    primeControlSentAt = now;
  }

  if (primeSession.phase == PRIME_SESSION_RUNNING && !primeLinkLost &&
      now - primeLastUiAt >= 100) {
    primeLastUiAt = now;
    refreshPrimeStatus();
  }
}

// ════════════════════════════════════════════════════════════
//  Ratio, open on the machine display
// ════════════════════════════════════════════════════════════
//
// While the machine display has a flavor's Ratio page up, this glass shows two buttons on
// its blue: More flavor under a minus above the flavor and its ratio, and Lighter under a
// plus below them, the signs the machine display's own stepper wears. A step goes to the
// main board as the ratio it stepped to.

#define RATIO_BTN_X        8
#define RATIO_BTN_W      (SCREEN_W - 2 * RATIO_BTN_X)
#define RATIO_BTN_H      104
#define RATIO_MORE_Y       8
#define RATIO_LIGHTER_Y  208
#define RATIO_MARK_Y      23   // the sign's line, down from the button's top
#define RATIO_WORD_Y      66   // the word's line, down from the button's top

// Up while the main board's fresh word is that a visit stands.
static bool ratioWanted() {
  return ratioSessionKnown && ratioLinkUp && ratioSession.open &&
         millis() - ratioSessionAt < RATIO_STALE_MS;
}

// The visit's flavor and ratio, and whether each button has a step left in it. A button at
// the end of the range is dimmed and takes no press of its own.
static void renderRatio() {
  static int16_t shown = -1;
  const uint8_t ch = ratioSession.channel & 1;
  const uint8_t ratio = ratioShown[ch];
  const int16_t now = (int16_t)((ch << 8) | ratio);
  if (now == shown) return;
  shown = now;
  lv_label_set_text(ratioFlavorLbl, FLAVOR_NAMES[ch]);
  lv_label_set_text_fmt(ratioValueLbl, "1 : %u", (unsigned)ratio);
  struct { lv_obj_t *btn; lv_obj_t *mark; lv_obj_t *label; bool on; } buttons[2] = {
      {ratioMoreBtn, ratioMoreMark, ratioMoreLbl, ratio > FLAVOR_RATIO_MIN},
      {ratioLighterBtn, ratioLighterMark, ratioLighterLbl, ratio < FLAVOR_RATIO_MAX}};
  for (auto &b : buttons) {
    lv_obj_set_style_bg_color(b.btn, lv_color_hex(b.on ? COL_DIM : COL_CARD_ON), 0);
    lv_obj_set_style_text_color(b.mark, lv_color_hex(b.on ? COL_INK : COL_OFF), 0);
    lv_obj_set_style_text_color(b.label, lv_color_hex(b.on ? COL_INK : COL_OFF), 0);
    if (b.on) lv_obj_add_flag(b.btn, LV_OBJ_FLAG_CLICKABLE);
    else lv_obj_clear_flag(b.btn, LV_OBJ_FLAG_CLICKABLE);
  }
}

static void adoptRatios(const uint8_t ratio[2]) {
  for (uint8_t i = 0; i < 2; i++)
    if (ratio[i] >= FLAVOR_RATIO_MIN && ratio[i] <= FLAVOR_RATIO_MAX) ratioShown[i] = ratio[i];
  if (faceShown == FACE_RATIO) renderRatio();
}

void faucetApplyRatioSession(const RatioSessionStatePayload &state) {
  if (state.channel > PUMP_CHANNEL_B) return;
  const bool entering = state.open && (!ratioSessionKnown || !ratioSession.open ||
                                       ratioSession.token != state.token);
  ratioSession = state;
  ratioSessionKnown = true;
  ratioLinkUp = true;
  ratioSessionAt = millis();
  if (!ratioStepWanted && !ratioStepsOwed) adoptRatios(state.ratio);
  if (entering) {
    lastInputTime = millis();
    if (dimmed) wakeBacklight();
  }
  faceService(nullptr);
}

void faucetApplyRatio(const RatioPayload &ratio) {
  if (ratioStepsOwed) --ratioStepsOwed;
  if (!ratioStepWanted && !ratioStepsOwed) adoptRatios(ratio.ratio);
}

// The blue between the buttons, and a button at the end of its range: a finger, and nothing
// more.
static void onRatioLayerTouch(lv_event_t *e) {
  (void)e;
  if (touchWakesOnly()) return;
  lastInputTime = millis();
  faucetTouched();
}

static void onRatioStep(lv_event_t *e) {
  if (touchWakesOnly() || faceShown != FACE_RATIO) return;
  lastInputTime = millis();
  const uint8_t ch = ratioSession.channel & 1;
  const int next = (int)ratioShown[ch] + (int)(intptr_t)lv_event_get_user_data(e);
  if (next < FLAVOR_RATIO_MIN || next > FLAVOR_RATIO_MAX) {
    faucetTouched();
    return;
  }
  ratioShown[ch] = (uint8_t)next;
  ratioStepChannel = ch;
  ratioStepValue = (uint8_t)next;
  ratioStepWanted = true;
  renderRatio();
}

// A press's step goes out once J3 takes it, so it ticks once.
static void ratioService(const BaseLinkStatus &link) {
  const unsigned long now = millis();
  ratioLinkUp = link.connected;
  if (ratioStepsOwed && now - ratioStepSentAt >= RATIO_REPLY_MS) ratioStepsOwed = 0;
  if (ratioStepWanted && baseLinkRatioSet(ratioStepChannel, ratioStepValue)) {
    ratioStepWanted = false;
    ++ratioStepsOwed;
    ratioStepSentAt = now;
  }

  // This glass has no camera on it. What the screen laid out goes to the main board's
  // console, once for each visit it shows.
  if (faceShown == FACE_RATIO && ratioSaidToken != ratioSession.token) {
    ratioSaidToken = ratioSession.token;
    lv_obj_update_layout(ratioLayer);
    const char *value = lv_label_get_text(ratioValueLbl);
    char line[96];
    snprintf(line, sizeof(line), "ratio up: %s at %s, %d px wide; buttons at %d and %d, %d tall",
             lv_label_get_text(ratioFlavorLbl), value,
             (int)lv_txt_get_width(value, strlen(value), &lv_font_montserrat_36, 0, LV_TEXT_FLAG_NONE),
             (int)lv_obj_get_y(ratioMoreBtn), (int)lv_obj_get_y(ratioLighterBtn),
             (int)lv_obj_get_height(ratioLighterBtn));
    baseLinkSay(line);
  }
}

// A step button, inset on the glass's blue: its sign, as the machine display's stepper draws
// one, over its word.
static lv_obj_t *ratioButton(lv_obj_t *parent, lv_coord_t y, const char *sign, const char *text,
                             int step, lv_obj_t **mark, lv_obj_t **label) {
  lv_obj_t *btn = lv_btn_create(parent);
  lv_obj_remove_style_all(btn);
  lv_obj_set_pos(btn, RATIO_BTN_X, y);
  lv_obj_set_size(btn, RATIO_BTN_W, RATIO_BTN_H);
  lv_obj_set_style_bg_color(btn, lv_color_hex(COL_DIM), 0);
  lv_obj_set_style_bg_opa(btn, LV_OPA_COVER, 0);
  lv_obj_add_flag(btn, LV_OBJ_FLAG_PRESS_LOCK);
  lv_obj_clear_flag(btn, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_add_event_cb(btn, onRatioStep, LV_EVENT_PRESSED, (void *)(intptr_t)step);

  *mark = lv_label_create(btn);
  lv_obj_set_style_text_font(*mark, &lv_font_montserrat_28, 0);
  lv_obj_set_style_text_color(*mark, lv_color_hex(COL_INK), 0);
  lv_label_set_text(*mark, sign);
  lv_obj_align(*mark, LV_ALIGN_TOP_MID, 0, RATIO_MARK_Y);

  *label = lv_label_create(btn);
  lv_obj_set_width(*label, RATIO_BTN_W);
  lv_obj_set_pos(*label, 0, RATIO_WORD_Y + LINE_DY_16);
  lv_obj_set_style_text_align(*label, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_set_style_text_font(*label, &lv_font_montserrat_16, 0);
  lv_obj_set_style_text_color(*label, lv_color_hex(COL_INK), 0);
  lv_label_set_text(*label, text);
  return btn;
}

static void buildRatioLayer(lv_obj_t *scr) {
  ratioLayer = wholeGlass(scr, THEME_BG, onRatioLayerTouch, LV_EVENT_PRESSED);
  ratioMoreBtn = ratioButton(ratioLayer, RATIO_MORE_Y, LV_SYMBOL_MINUS, "More flavor", -1,
                             &ratioMoreMark, &ratioMoreLbl);
  ratioFlavorLbl = lineLabel(ratioLayer, 126 + LINE_DY_16, &lv_font_montserrat_16, COL_DIM,
                             FLAVOR_NAMES[0]);
  ratioValueLbl = lineLabel(ratioLayer, 148 + LINE_DY_36, &lv_font_montserrat_36, COL_TEXT, "");
  ratioLighterBtn = ratioButton(ratioLayer, RATIO_LIGHTER_Y, LV_SYMBOL_PLUS, "Lighter", 1,
                                &ratioLighterMark, &ratioLighterLbl);
}

// ════════════════════════════════════════════════════════════
//  UI
// ════════════════════════════════════════════════════════════

static void buildTrustLayer(lv_obj_t *scr);
static void buildNoticeLayer(lv_obj_t *scr);

static void buildUi() {
  bindLogos();

  lv_obj_t *scr = lv_scr_act();
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);
  lv_obj_clear_flag(scr, LV_OBJ_FLAG_SCROLLABLE);

  // Flavor logo fills the panel
  logoImg = lv_img_create(scr);
  lv_obj_align(logoImg, LV_ALIGN_CENTER, 0, 0);

  // Full-screen tap target on top. Strip all theme styles — the theme's
  // pressed-state transition would otherwise animate this (invisible)
  // object on every tap, forcing extra full-screen redraws.
  lv_obj_t *overlay = lv_obj_create(scr);
  lv_obj_remove_style_all(overlay);
  lv_obj_set_size(overlay, LV_PCT(100), LV_PCT(100));
  lv_obj_clear_flag(overlay, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_add_flag(overlay, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_add_event_cb(overlay, onTap, LV_EVENT_PRESSED, NULL);

  // Prime-ready replaces the logo with one hold target the size of the glass: the
  // flavor, what the hold is doing, and how it stands.
  primeLayer = wholeGlass(scr, THEME_BG, nullptr, LV_EVENT_ALL);

  primeHoldBtn = lv_btn_create(primeLayer);
  lv_obj_remove_style_all(primeHoldBtn);
  lv_obj_set_pos(primeHoldBtn, 0, 0);
  lv_obj_set_size(primeHoldBtn, SCREEN_W, SCREEN_H);
  lv_obj_set_style_bg_color(primeHoldBtn, lv_color_hex(COL_ACCENT), 0);
  lv_obj_set_style_bg_opa(primeHoldBtn, LV_OPA_COVER, 0);
  lv_obj_set_style_bg_color(primeHoldBtn, lv_color_hex(COL_ACCENT), LV_STATE_PRESSED);
  lv_obj_add_flag(primeHoldBtn, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_clear_flag(primeHoldBtn, LV_OBJ_FLAG_PRESS_LOCK | LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_add_event_cb(primeHoldBtn, onPrimeHold, LV_EVENT_ALL, NULL);

  primeFlavorLbl = lineLabel(primeHoldBtn, 112 + LINE_DY_16, &lv_font_montserrat_16, COL_INK,
                             FLAVOR_NAMES[0]);
  primeHoldLbl = lineLabel(primeHoldBtn, 140 + LINE_DY_20, &lv_font_montserrat_20, COL_INK,
                           "Hold to prime");
  primeStatusLbl = lineLabel(primeHoldBtn, 174 + LINE_DY_16, &lv_font_montserrat_16, COL_INK, "");

  buildRatioLayer(scr);
  buildTrustLayer(scr);
  buildNoticeLayer(scr);
  applyFlavorUi();
}

// ════════════════════════════════════════════════════════════
//  Trusting a phone
// ════════════════════════════════════════════════════════════
//
// A phone that wants to change the machine asks here and on the enclosure at
// once. A tap on either answers for both; phone_trust.cpp closes this one when
// the ask ends anywhere else.

static void onTrust(lv_event_t *e) {
  if (trustShownAsk) phoneTrustAnswer(trustShownAsk, true);
}

static void onDontTrust(lv_event_t *e) {
  if (trustShownAsk) phoneTrustAnswer(trustShownAsk, false);
}

static void trustTouch(lv_event_t *e) {
  const lv_event_code_t code = lv_event_get_code(e);
  if (code == LV_EVENT_PRESSED) trustPressed = true;
  else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) trustPressed = false;
}

static lv_obj_t *trustButton(lv_obj_t *parent, lv_coord_t x, lv_coord_t y,
                             lv_coord_t w, lv_coord_t h, uint32_t bg,
                             uint32_t fg, const char *text, lv_event_cb_t cb) {
  lv_obj_t *btn = lv_btn_create(parent);
  lv_obj_remove_style_all(btn);
  lv_obj_set_pos(btn, x, y);
  lv_obj_set_size(btn, w, h);
  lv_obj_set_style_bg_color(btn, lv_color_hex(bg), 0);
  lv_obj_set_style_bg_opa(btn, LV_OPA_COVER, 0);
  lv_obj_set_style_bg_color(btn, lv_color_hex(COL_OFF), LV_STATE_PRESSED);
  lv_obj_clear_flag(btn, LV_OBJ_FLAG_PRESS_LOCK);
  lv_obj_add_event_cb(btn, trustTouch, LV_EVENT_ALL, NULL);
  lv_obj_add_event_cb(btn, cb, LV_EVENT_CLICKED, NULL);
  lv_obj_t *lbl = lv_label_create(btn);
  lv_label_set_text(lbl, text);
  lv_obj_set_style_text_font(lbl, &lv_font_montserrat_20, 0);
  lv_obj_set_style_text_color(lbl, lv_color_hex(fg), 0);
  lv_obj_set_style_text_align(lbl, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_center(lbl);
  return btn;
}

// ════════════════════════════════════════════════════════════
//  One face at a time
// ════════════════════════════════════════════════════════════
//
// The glass shows one thing and it fills the glass, the first of: a trust ask, unless a hold
// is in progress, which keeps the glass until it ends; Prime; Ratio; why there is no soda;
// and the flavor's picture. An update stands over all of them on its own layer.

// A hold here or at the machine, or one of this glass's starting or stopping.
static bool primeHeld() {
  return primePressed || primeStopPending ||
         (primeSessionKnown && primeSession.phase == PRIME_SESSION_RUNNING);
}

static uint8_t faceWanted() {
  if (trustShownAsk && !(primeVisible && primeHeld())) return FACE_TRUST;
  if (primeVisible) return FACE_PRIME;
  if (ratioWanted()) return FACE_RATIO;
  if (noticeKind != NOTICE_NONE) return FACE_NOTICE;
  return FACE_LOGO;
}

static void showIf(lv_obj_t *obj, bool show) {
  if (show) lv_obj_clear_flag(obj, LV_OBJ_FLAG_HIDDEN);
  else lv_obj_add_flag(obj, LV_OBJ_FLAG_HIDDEN);
}

static void faceService(lv_timer_t *) {
  if (!trustLayer || !noticeLayer || !ratioLayer || !primeLayer) return;
  if (!touchIsDown) trustPressed = false;
  const uint8_t face = faceWanted();
  if (face != faceShown) {
    // A finger already on the glass is not a press on whatever appears under it.
    if (touchInput) lv_indev_wait_release(touchInput);
    faceShown = face;
    if (face == FACE_PRIME) renderPrime(true);
    if (face == FACE_RATIO) renderRatio();
    else ratioStepWanted = false;   // a step belongs to the screen it was pressed on
    if (face == FACE_NOTICE) noticeFaceSaid = 0xFF;
    showIf(trustLayer, face == FACE_TRUST);
    showIf(primeLayer, face == FACE_PRIME);
    showIf(ratioLayer, face == FACE_RATIO);
    showIf(noticeLayer, face == FACE_NOTICE);
  }
  // This glass has no camera on it. What it laid out goes to the main board's console, once
  // for each face a notice wears while it is up.
  if (face == FACE_NOTICE && noticeFace != noticeFaceSaid) {
    noticeFaceSaid = noticeFace;
    lv_obj_update_layout(noticeLayer);
    char line[112];
    snprintf(line, sizeof(line),
             "notice %u.%u up: title %dx%d at %d, body %dx%d at %d, bar %d at %d",
             (unsigned)noticeKind, (unsigned)noticeFace,
             (int)lv_obj_get_width(noticeTitleLbl), (int)lv_obj_get_height(noticeTitleLbl),
             (int)lv_obj_get_y(noticeTitleLbl),
             (int)lv_obj_get_width(noticeBodyLbl), (int)lv_obj_get_height(noticeBodyLbl),
             (int)lv_obj_get_y(noticeBodyLbl),
             lv_obj_has_flag(noticeTrack, LV_OBJ_FLAG_HIDDEN) ? 0 : (int)lv_obj_get_width(noticeTrack),
             (int)lv_obj_get_y(noticeTrack));
    baseLinkSay(line);
  }
}

// The ask's title, the device it names on a line of its own, then what trusting allows, and
// the two answers one above the other.
#define TRUST_TITLE_PITCH 26

static void buildTrustLayer(lv_obj_t *scr) {
  trustLayer = wholeGlass(scr, lv_color_hex(COL_CARD), trustTouch, LV_EVENT_ALL);
  trustTitleLbl = lineLabel(trustLayer, 28 + LINE_DY_20, &lv_font_montserrat_20, COL_TEXT, "");
  lv_obj_set_style_text_line_space(trustTitleLbl,
                                   TRUST_TITLE_PITCH - lv_font_montserrat_20.line_height, 0);
  trustBodyLbl = lineLabel(trustLayer, 96 + LINE_DY_16, &lv_font_montserrat_16, COL_DIM, "");

  trustButton(trustLayer, 8, 148, SCREEN_W - 16, 72, 0x1749d1, COL_TEXT, "Don't Trust", onDontTrust);
  trustButton(trustLayer, 8, 232, SCREEN_W - 16, 72, COL_ACCENT, COL_INK, "Trust", onTrust);

  lv_timer_create(faceService, 50, nullptr);
}

// ════════════════════════════════════════════════════════════
//  Why there is no soda
// ════════════════════════════════════════════════════════════
//
// A refill that spent its pumping ceiling stands latched until someone has
// looked at the machine. This glass is at the sink and the machine is not, so
// it says only that there is no water and where to go: the machine's own
// display says what to check and is where Try again is.
//
// A sweep is the other way round. The lever beside this glass is what lets
// the dry tank's air out, so the hand and the eyes are here: the glass asks
// for the lever, shows the main board's count as a bar while gas is moving,
// and says when to let go.
//
// A move is at the lever too. The machine's display has told the person to
// shut the supplies and empty the tank here, so the glass says to hold the
// lever until nothing comes out. The main board cannot tell an empty tank: it
// says only whether the meter is turning and whether the float has passed
// the low reed, and once it has and the flow has stopped the glass asks.
enum : uint8_t {
  NOTICE_FACE_NO_WATER,
  NOTICE_FACE_SWEEP_ASK,     // nothing counted yet
  NOTICE_FACE_SWEEP_HOLD,    // gas is moving
  NOTICE_FACE_SWEEP_AGAIN,   // the lever was let go short of the target
  NOTICE_FACE_SWEEP_DONE,
  NOTICE_FACE_MOVE_ASK,      // nothing is leaving
  NOTICE_FACE_MOVE_HOLD,     // the meter is turning
  NOTICE_FACE_MOVE_STOPPED,  // the float is below the low reed and nothing is leaving
};

// A finger on the notice is a finger: it wakes the glass and is reported, and
// reaches nothing beneath.
static void onNoticeTouch(lv_event_t *e) {
  (void)e;
  lastInputTime = millis();
  if (dimmed) wakeBacklight();
  faucetTouched();
}

static void buildNoticeLayer(lv_obj_t *scr) {
  noticeLayer = wholeGlass(scr, lv_color_hex(COL_CARD), onNoticeTouch, LV_EVENT_PRESSED);
  noticeTitleLbl = lineLabel(noticeLayer, 0, &lv_font_montserrat_20, COL_WARN, "No water");
  noticeBodyLbl = lineLabel(noticeLayer, 0, &lv_font_montserrat_16, COL_TEXT,
                            "See the display\non the machine.");
  noticeTrack = barTrack(noticeLayer, 140, &noticeFill);
  lv_obj_add_flag(noticeTrack, LV_OBJ_FLAG_HIDDEN);
}

// The words for what the main board last said.
static void noticeDress() {
  uint8_t face = NOTICE_FACE_NO_WATER;
  if (noticeKind == NOTICE_SWEEP_DONE) face = NOTICE_FACE_SWEEP_DONE;
  else if (noticeKind == NOTICE_SWEEP)
    face = noticeFlowing    ? NOTICE_FACE_SWEEP_HOLD
         : noticeProgress   ? NOTICE_FACE_SWEEP_AGAIN
                            : NOTICE_FACE_SWEEP_ASK;
  else if (noticeKind == NOTICE_MOVE)
    face = noticeFlowing    ? NOTICE_FACE_MOVE_HOLD
         : noticeBelow      ? NOTICE_FACE_MOVE_STOPPED
                            : NOTICE_FACE_MOVE_ASK;

  // Only a sweep has a count to show, and its bar stands between the title and the words.
  const bool sweep = face >= NOTICE_FACE_SWEEP_ASK && face <= NOTICE_FACE_SWEEP_DONE;
  lv_obj_set_width(noticeFill, (lv_coord_t)(BAR_W * (uint32_t)noticeProgress / 100));
  if (face == noticeFace) return;
  noticeFace = face;

  const char *title = "No water";
  const char *body  = "See the display\non the machine.";
  uint32_t color = COL_WARN;
  switch (face) {
    case NOTICE_FACE_SWEEP_ASK:
      title = "Hold the lever";
      body  = "Gas will hiss until\nthis says Done.";
      color = COL_TEXT;
      break;
    case NOTICE_FACE_SWEEP_HOLD:
      title = "Keep holding";
      body  = "The tank is\nclearing its air.";
      color = COL_ACCENT;
      break;
    case NOTICE_FACE_SWEEP_AGAIN:
      title = "Hold the lever";
      body  = "Not done yet.\nHold it down again.";
      color = COL_TEXT;
      break;
    case NOTICE_FACE_SWEEP_DONE:
      title = "Done";
      body  = "Let go. The machine\nfills itself now.";
      color = COL_GOOD;
      break;
    case NOTICE_FACE_MOVE_ASK:
      title = "Draining";
      body  = "Hold the lever until\nnothing comes out.";
      color = COL_TEXT;
      break;
    case NOTICE_FACE_MOVE_HOLD:
      title = "Keep holding";
      body  = "Until water and\nhissing stop.";
      color = COL_ACCENT;
      break;
    case NOTICE_FACE_MOVE_STOPPED:
      title = "Nothing more?";
      body  = "Then unplug\nthe machine.";
      color = COL_TEXT;
      break;
    default:
      break;
  }
  lv_label_set_text(noticeTitleLbl, title);
  lv_label_set_text(noticeBodyLbl, body);
  lv_obj_set_style_text_color(noticeTitleLbl, lv_color_hex(color), 0);
  lv_obj_set_y(noticeTitleLbl, (sweep ? 100 : 112) + LINE_DY_20);
  lv_obj_set_y(noticeBodyLbl, (sweep ? 166 : 152) + LINE_DY_16);
  if (sweep) lv_obj_clear_flag(noticeTrack, LV_OBJ_FLAG_HIDDEN);
  else lv_obj_add_flag(noticeTrack, LV_OBJ_FLAG_HIDDEN);
}

void faucetApplyNotice(const NoticePayload &notice) {
  // A reason this glass has no words for is not shown as one it has.
  uint8_t kind = notice.kind;
  if (kind != NOTICE_NO_WATER && kind != NOTICE_SWEEP && kind != NOTICE_SWEEP_DONE && kind != NOTICE_MOVE)
    kind = NOTICE_NONE;
  const uint8_t progress = kind == NOTICE_SWEEP_DONE ? 100
                         : kind != NOTICE_SWEEP      ? 0
                         : notice.progress > 100     ? 100
                                                     : notice.progress;
  const bool flowing = (kind == NOTICE_SWEEP || kind == NOTICE_MOVE) && (notice.flags & NOTICE_F_FLOWING);
  const bool below   = kind == NOTICE_MOVE && (notice.flags & NOTICE_F_BELOW);
  if (kind == noticeKind && progress == noticeProgress && flowing == noticeFlowing && below == noticeBelow)
    return;
  noticeKind     = kind;
  noticeProgress = progress;
  noticeFlowing  = flowing;
  noticeBelow    = below;
  if (kind != NOTICE_NONE) noticeDress();
  faceService(nullptr);
}

void faucetTrustShow(const TrustShowPayload &ask) {
  if (trustShownAsk == ask.askId) return;
  // The device the ask names stands on a line of its own.
  char title[32];
  snprintf(title, sizeof(title), "%s", trustTitle(ask.kind));
  char *space = strrchr(title, ' ');
  if (space) *space = '\n';
  lv_label_set_text(trustTitleLbl, title);
  lv_label_set_text(trustBodyLbl, "Settings + cycles");
  trustShownAsk = ask.askId;
  faceService(nullptr);
  lastInputTime = millis();
  wakeBacklight();
}

void faucetTrustHide() {
  if (trustPressed && touchInput) lv_indev_wait_release(touchInput);
  trustShownAsk = 0;
  faceService(nullptr);
}

// ════════════════════════════════════════════════════════════
//  USB serial text commands (testing / diagnostics)
// ════════════════════════════════════════════════════════════

static void processTextLine(const char *line) {
  if (strcmp(line, "GET_VERSION") == 0) {
    Serial.printf("VERSION:FAUCET=%s\n", FW_VERSION);
  } else if (strcmp(line, "GET_STATE") == 0) {
    BaseLinkStatus link;
    baseLinkReadStatus(link);
    Serial.printf("STATE:FLAVOR=%d,SYNC=%d,BASE=%d,PERSISTED=%d,PENDING=%u,DURABILITYPENDING=%d,CACHEPENDING=%d,PRIME=%u,OWNER=%u\n",
                  activeFlavor, link.synchronized ? 1 : 0, link.mainBoardFlavor,
                  link.mainBoardPersisted ? 1 : 0, (unsigned)link.pending,
                  link.durabilityPending ? 1 : 0,
                  flavorDirty ? 1 : 0,
                  primeSessionKnown ? (unsigned)primeSession.phase : 0,
                  primeSessionKnown ? (unsigned)primeSession.owner : 0);
  } else if (strcmp(line, "GET_DIAG") == 0) {
    BaseLinkStatus link;
    baseLinkReadStatus(link);
    Serial.printf("DIAG:heap=%lu,minHeap=%lu,touchInts=%lu,toggles=%lu,"
                  "maxLoopMs=%lu,dim=%d,bl=%u,localPersistErr=%d,"
                  "base=%s,sync=%d,baseFlavor=%u,basePersisted=%d,basePersistErr=%d,durabilityPending=%d,"
                  "pending=%u,linkRx=%lu,linkTx=%lu,retries=%lu,qDrop=%lu,staleResp=%lu,truthSync=%lu,"
                  "lastAckMs=%lu,maxAckMs=%lu,maxLinkUs=%lu,primeQ=%u,primeDrop=%lu,"
                  "art=%u/%u,showing=%u,idle=%d,uptime=%lus\n",
                  (unsigned long)ESP.getFreeHeap(),
                  (unsigned long)ESP.getMinFreeHeap(),
                  (unsigned long)touch.intCount(),
                  (unsigned long)toggleCount,
                  (unsigned long)maxLoopMs, dimmed ? 1 : 0, blDuty,
                  flavorPersistError ? 1 : 0,
                  link.connected ? "up" : "down", link.synchronized ? 1 : 0,
                  (unsigned)link.mainBoardFlavor,
                  link.mainBoardPersisted ? 1 : 0,
                  link.mainBoardPersistError ? 1 : 0,
                  link.durabilityPending ? 1 : 0,
                  (unsigned)link.pending,
                  (unsigned long)link.framesRx, (unsigned long)link.framesTx,
                  (unsigned long)link.retries, (unsigned long)link.queueDrops,
                  (unsigned long)link.staleResponses,
                  (unsigned long)link.authoritativeReconciliations,
                  (unsigned long)link.lastAckMs, (unsigned long)link.maxAckMs,
                  (unsigned long)link.maxServiceUs,
                  (unsigned)link.primePending, (unsigned long)link.primeQueueDrops,
                  (unsigned)flavorArt[0], (unsigned)flavorArt[1],
                  (unsigned)flavorArt[activeFlavor & 1],
                  idleAsleepWanted ? 1 : 0,
                  millis() / 1000);
    Serial.printf("DIAG_PRIME:visible=%d,known=%d,phase=%u,owner=%u,outcome=%u,"
                  "pressed=%d,stop=%d,lost=%d,session=%08lX,hold=%08lX,"
                  "revision=%lu,elapsed=%lu,epoch=%lu\n",
                  primeVisible ? 1 : 0, primeSessionKnown ? 1 : 0,
                  primeSessionKnown ? (unsigned)primeSession.phase : 0,
                  primeSessionKnown ? (unsigned)primeSession.owner : 0,
                  primeSessionKnown ? (unsigned)primeSession.outcome : 0,
                  primePressed ? 1 : 0, primeStopPending ? 1 : 0,
                  primeLinkLost ? 1 : 0,
                  (unsigned long)primeSession.sessionToken,
                  (unsigned long)primeHoldToken,
                  primeSessionKnown ? (unsigned long)primeSession.revision : 0,
                  primeSessionKnown ? (unsigned long)displayedPrimeElapsed() : 0,
                  (unsigned long)link.connectionGeneration);
    maxLoopMs = 0;  // high-water mark since last query
  } else if (strcmp(line, "TOGGLE") == 0) {
    selectFlavorLocally(activeFlavor ^ 1);
    Serial.printf("OK:FLAVOR=%d\n", activeFlavor);
  } else if (strncmp(line, "BL:", 3) == 0) {
    // Raw backlight poke (bring-up/demo). Holds until input or wake.
    const char *value = line + 3;
    char *end = nullptr;
    const long parsed = strtol(value, &end, 10);
    if (value[0] == '\0' || end == value || *end != '\0' || parsed < 0 || parsed > 255) {
      Serial.println("ERR:BL expects 0-255");
    } else {
      int duty = static_cast<int>(parsed);
      blDuty = blTarget = (uint8_t)duty;
      dimmed = duty < BL_FULL_DUTY;  // a tap on a poked-dim screen wakes, not toggles
      lastInputTime = millis();
      ledcWrite(LCD_BL, blDuty);
      Serial.printf("OK:BL=%d\n", duty);
    }
  } else if (strncmp(line, "FLAVOR:", 7) == 0) {
    const char *value = line + 7;
    char *end = nullptr;
    const long parsed = strtol(value, &end, 10);
    if (value[0] == '\0' || end == value || *end != '\0' || parsed < 0 || parsed > 1) {
      Serial.println("ERR:FLAVOR out of range");
    } else {
      const uint8_t f = static_cast<uint8_t>(parsed);
      selectFlavorLocally(f);
      Serial.printf("OK:FLAVOR=%d\n", activeFlavor);
    }
  } else {
    Serial.printf("ERR:unknown command '%s'\n", line);
  }
}

// ════════════════════════════════════════════════════════════
//  Setup / loop
// ════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  // Never block on USB writes: the HWCDC TX buffer only drains while a host
  // is reading the port. With the default 100ms timeout, every print stalls
  // the loop once the buffer fills — felt as tap lag. 0 = drop instead.
  Serial.setTxTimeoutMs(0);
  delay(500);
  Serial.println("ESP32-S3 Faucet Display starting...");

  esp_reset_reason_t reason = esp_reset_reason();
  Serial.printf("Boot — firmware %s, heap=%lu, reset=%d\n",
                FW_VERSION, (unsigned long)ESP.getFreeHeap(), (int)reason);

  // Persisted flavor selection
  flavorStoreOpen = prefs.begin("faucet");
  flavorPersistError = !flavorStoreOpen;
  activeFlavor = flavorStoreOpen ? prefs.getUChar("flavor", 0) : 0;
  if (activeFlavor > 1) {
    activeFlavor = 0;
    flavorDirty = true;
    flavorChangedAt = millis();
  }

  // Display hardware init
  if (!gfx->begin()) {
    Serial.println("gfx->begin() failed!");
  }
  lcdRegInit();
  gfx->setRotation(ROTATION);
  gfx->fillScreen(RGB565_BLACK);

  // Backlight on after the panel is initialized (avoids boot flash).
  // LEDC PWM so idle dimming can fade it.
  ledcAttach(LCD_BL, 5000, 8);
  ledcWrite(LCD_BL, blDuty);

  // Touch
  Wire.begin(TOUCH_SDA, TOUCH_SCL);
  touch.begin(Wire, ROTATION, gfx->width(), gfx->height());

  // LVGL init
  lv_init();
  lvgl_buf = (lv_color_t *)malloc(SCREEN_W * LVGL_BUF_LINES * sizeof(lv_color_t));
  if (!lvgl_buf) {
    Serial.println("FATAL: failed to allocate LVGL buffer!");
    while (1) delay(1000);
  }
  lv_disp_draw_buf_init(&draw_buf, lvgl_buf, NULL, SCREEN_W * LVGL_BUF_LINES);

  static lv_disp_drv_t disp_drv;
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = gfx->width();
  disp_drv.ver_res = gfx->height();
  disp_drv.flush_cb = lvglFlush;
  disp_drv.draw_buf = &draw_buf;
  lv_disp_drv_register(&disp_drv);

  static lv_indev_drv_t indev_drv;
  lv_indev_drv_init(&indev_drv);
  indev_drv.type = LV_INDEV_TYPE_POINTER;
  indev_drv.read_cb = touchpadRead;
  touchInput = lv_indev_drv_register(&indev_drv);

  // The user's own pictures, before anything binds a pointer into them: the UI
  // builds its logo descriptors once, and a store opened after that leaves
  // every custom face bound to nothing and falling back to a factory one —
  // which looks exactly like a picture that failed to arrive.
  {
    static ImageSize kSizes[IMAGE_BUNDLE_COUNT];
    for (uint8_t i = 0; i < IMAGE_BUNDLE_COUNT; i++) {
      kSizes[i].w = IMAGE_BUNDLE[i].w;
      kSizes[i].h = IMAGE_BUNDLE[i].h;
      kSizes[i].offset = 0;
    }
    // The master copy: every size either glass draws, not only this one's. An
    // enclosure display can be replaced and re-provisioned from here with no
    // phone in the room.
    imageStoreBegin("spiffs", kSizes, IMAGE_BUNDLE_COUNT);
  }

  buildUi();

  // P1 is the official Waveshare pinout: GPIO43 TX / GPIO44 RX. The main board's
  // J3 crosses them to IO35 RX / IO33 TX over the full-duplex TTL umbilical.
  primeTokenState = esp_random();
  if (primeTokenState == 0) primeTokenState = 1;
  // The user's own pictures, mapped out of the partition nothing else uses.
  // Opened after the link so the line it reports on already exists.
  baseLinkBegin(activeFlavor, acceptBaseFlavor, acceptBasePrime);

  {
    char line[96];
    if (imageStoreCapacity()) {
      snprintf(line, sizeof(line), "images: %u slots, %lu B each, %u held",
               imageStoreCapacity(), (unsigned long)imageStoreBundleBytes(),
               imageStoreHeld());
    } else {
      snprintf(line, sizeof(line), "images: no store");
    }
    baseLinkSayOnConnect(line);
  }

  bleLinkBegin();

  lastInputTime = millis();
  Serial.printf("Ready — flavor %d (%s). Tap to switch.\n",
                activeFlavor + 1, FLAVOR_NAMES[activeFlavor]);
}

void loop() {
  unsigned long loopStart = millis();

  // USB serial commands (debug/test)
  static char usbBuf[64];
  static uint8_t usbPos = 0;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (usbPos > 0) {
        usbBuf[usbPos] = '\0';
        processTextLine(usbBuf);
        usbPos = 0;
      }
    } else if (usbPos < sizeof(usbBuf) - 1) {
      usbBuf[usbPos++] = c;
    }
  }

  // RX before LVGL keeps main board reconciliation prompt. A second service
  // after LVGL transmits a touch-down selection without putting UART or NVS in
  // the touch callback itself.
  baseLinkService();
  bleLinkService();
  BaseLinkStatus liveLink;
  baseLinkReadStatus(liveLink);
  primeService(liveLink);
  ratioService(liveLink);

  // Debounced flavor persist (off the tap path)
  if (flavorDirty && millis() - flavorChangedAt >= FLAVOR_PERSIST_DELAY_MS &&
      millis() - flavorPersistAttemptAt >= FLAVOR_PERSIST_DELAY_MS) {
    flavorPersistAttemptAt = millis();
    if (flavorStoreOpen && prefs.putUChar("flavor", activeFlavor) == sizeof(uint8_t)) {
      flavorDirty = false;
      flavorPersistError = false;
      Serial.printf("Cached main board flavor %d\n", activeFlavor + 1);
    } else {
      flavorPersistError = true;
      Serial.println("Faucet flavor cache write failed — main board remains authoritative");
    }
  }

  // Idle dimming: take the dim target when the appliance says both glasses are
  // done, then fade toward it. Waking snaps to full (wakeBacklight), so the
  // stepper only walks down. A live hold is this head's own business and holds
  // the dark off regardless.
  // Say it again until it is heard, then stop. A window that was full when the
  // finger landed has room a moment later, and a link that was reconnecting is
  // connected — neither is worth a lost tap.
  if (touchUnconfirmedSince) {
    if (millis() - touchUnconfirmedSince >= TOUCH_CONFIRM_GIVEUP_MS) {
      touchUnconfirmedSince = 0;   // J3 is past a retry's help
    } else if (millis() - touchConfirmRetryMs >= TOUCH_CONFIRM_RETRY_MS) {
      touchConfirmRetryMs = millis();
      baseLinkTouched();
    }
  }

  const bool primeRunning = primeSessionKnown && !primeLinkLost &&
                            primeSession.phase == PRIME_SESSION_RUNNING;
  if (!dimmed && idleAsleepWanted && !primePressed && !primeRunning &&
      !touchUnconfirmedSince) {
    dimmed = true;
    blTarget = BL_DIM_DUTY;
    Serial.println("Backlight dim (appliance idle)");
  }
  if (blDuty != blTarget) {
    int next = (int)blDuty - BL_FADE_STEP;
    if (next < (int)blTarget) next = blTarget;
    blDuty = (uint8_t)next;
    ledcWrite(LCD_BL, blDuty);
  }

  lv_timer_handler();
  baseLinkService();
  bleLinkService();

  unsigned long loopMs = millis() - loopStart;
  if (loopMs > maxLoopMs) maxLoopMs = loopMs;

  delay(5);
}
