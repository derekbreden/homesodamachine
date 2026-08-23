#include <Arduino.h>
#include <esp_system.h>
#include <esp_heap_caps.h>
#include <esp_cpu.h>
#include <Wire.h>
#include <lvgl.h>
#include "esp_lcd_panel_rgb.h"
#include "esp_lcd_panel_ops.h"
#include "freertos/semphr.h"
#include "fw_version.h"
#include "proto_link.h"
#include <driver/gpio.h>
#include <esp_sleep.h>
#include "soc/gpio_reg.h"
#include "soc/io_mux_reg.h"

// Implemented by the front-local ESP-IDF v5.5.4 RGB driver configuration.
// It increments only when an actual bounce-buffer shortfall requires scan
// recovery; normal wake cycles must leave it unchanged.
extern "C" uint32_t home_soda_rgb_restart_count(void);
// Static Font Awesome icons keep the customer rail and full-card actions crisp
// without asking LVGL to transform text at runtime.
extern "C" const lv_font_t front_icons_48;

// Animated loading logo — the 16-frame glass/bubbles loop (the same animation
// the config display uses), rendered natively at 360x360 RGB565 by
// tools/gen_animation_frames.py from the app-icon artwork. Each frame's
// background is THEME_BG, so the centered image blends into the screen fill.
#include "images/anim_00.h"
#include "images/anim_01.h"
#include "images/anim_02.h"
#include "images/anim_03.h"
#include "images/anim_04.h"
#include "images/anim_05.h"
#include "images/anim_06.h"
#include "images/anim_07.h"
#include "images/anim_08.h"
#include "images/anim_09.h"
#include "images/anim_10.h"
#include "images/anim_11.h"
#include "images/anim_12.h"
#include "images/anim_13.h"
#include "images/anim_14.h"
#include "images/anim_15.h"

// The flavor marks are deliberately static artwork. Choose's selection refresh
// changes only on actual controller state transitions, so these do not
// participate in the background link polling that formerly disturbed a card.
// Every logo is carried at both sizes: the 240 a Choose card shows, and the 96
// the picker grid shows, baked rather than scaled under LVGL at draw time.
#include "../src_config/images/flavor0_240.h"
#include "../src_config/images/flavor1_240.h"
#include "../src_config/images/flavor2_240.h"
#include "../src_config/images/flavor3_240.h"
#include "images/flavor0_thumb.h"
#include "images/flavor1_thumb.h"
#include "images/flavor2_thumb.h"
#include "images/flavor3_thumb.h"
#include "images/flavor0_mid.h"
#include "images/flavor1_mid.h"
#include "images/flavor2_mid.h"
#include "images/flavor3_mid.h"
#include "images/flavor0_head.h"
#include "images/flavor1_head.h"
#include "images/flavor2_head.h"
#include "images/flavor3_head.h"

static const uint16_t *animFrames[] = {
    anim_00, anim_01, anim_02, anim_03, anim_04, anim_05, anim_06, anim_07,
    anim_08, anim_09, anim_10, anim_11, anim_12, anim_13, anim_14, anim_15,
};
#define NUM_ANIM_FRAMES  16
#define ANIM_FRAME_MS    100   // ~10 fps, matches the config display
#define LOGO_SIZE        360
#define FLAVOR_ART_SIZE    240
#define FLAVOR_THUMB_SIZE   96
#define FLAVOR_HEAD_SIZE    60
#define FLAVOR_MID_SIZE    120
#define FLAVOR_IMAGE_COUNT   4   // logos a channel can be given

// ════════════════════════════════════════════════════════════
//  ESP32-S3 Front-Face Display — foundation
// ════════════════════════════════════════════════════════════
//
// Waveshare ESP32-S3-Touch-LCD-4.3B: 800x480 IPS RGB parallel panel,
// GT911 capacitive touch, CH422G I/O expander, ESP32-S3-WROOM-1-N16R8
// (16 MB flash / 8 MB octal PSRAM). Mounts in the appliance front face,
// angled up toward a standing user.
//
// The screen is a rail of five icons down the left edge and a pane to their right: Choose,
// Ratio, Prime, Clean, and Settings. Flavor selection follows the controller; a Prime
// flavor opens the shared hold pad, and the base board runs the selected pump only while
// the finger stays down.

// ── Theme (matches faucet display / config display / iOS app) ──
#define THEME_BG  lv_color_hex(0x1a1a2e)

#define COL_CARD     0x242440   // panel behind a group of controls
#define COL_CARD_ON  0x33335c   // the same panel, pressed or selected
#define COL_ACCENT   0xe94560   // the app icon's liquid, and every primary action
#define COL_TEXT     0xe8e8f2
#define COL_DIM      0x8888aa
#define COL_GOOD     0x37c98b
#define COL_WARN     0xf0a83c
#define COL_OFF      0x3a3a55   // a control at the end of its travel

// What a target answers to. START CLEAN CYCLE answers to LV_EVENT_CLICKED instead.
#define ACT_EVENT LV_EVENT_PRESSED

// ════════════════════════════════════════════════════════════
//  Pin map — fixed by the Waveshare ESP32-S3-Touch-LCD-4.3B
// ════════════════════════════════════════════════════════════
// Verified against the Waveshare wiki, the Arduino_GFX board example, and a
// working ESPHome config. The RGB data/sync lines drive the panel directly
// off the ESP32-S3 LCD peripheral; several are strapping/special pins
// (GPIO0/3/45/46) committed to the panel — do not repurpose them.

// RGB panel (ST7262-class, 16-bit parallel — 5R/6G/5B RGB565)
#define LCD_DE     5
#define LCD_VSYNC  3
#define LCD_HSYNC  46
#define LCD_PCLK   7
#define LCD_R0  1
#define LCD_R1  2
#define LCD_R2  42
#define LCD_R3  41
#define LCD_R4  40
#define LCD_G0  39
#define LCD_G1  0
#define LCD_G2  45
#define LCD_G3  48
#define LCD_G4  47
#define LCD_G5  21
#define LCD_B0  14
#define LCD_B1  38
#define LCD_B2  18
#define LCD_B3  17
#define LCD_B4  10

#define SCREEN_W  800
#define SCREEN_H  480
#define ROTATION  0   // landscape; USB/terminals on the long edge

// Shared I2C bus — CH422G I/O expander + GT911 touch + onboard RTC all live here
#define I2C_SDA  8
#define I2C_SCL  9

// GT911 capacitive touch — on the shared I2C bus; reset is on CH422G (EXIO1),
// released during ch422gBringUp(). INT is a plain GPIO input here. The address
// is 0x5D or 0x14 depending on reset timing, so it is probed at init.
#define TOUCH_INT   4
#define GT911_ADDR_A 0x5D
#define GT911_ADDR_B 0x14
#define GT911_REG_STATUS 0x814E  // buffer-status / touch-count
#define GT911_REG_POINT1 0x8150  // point 1: xL,xH, yL,yH, sizeL,sizeH (the track ID is 0x814F)

// ── RS485 to the base ESP32 (J9 / SIG-7) ──────────────────────
// Onboard SP3485, automatic direction switching — no DE line. Its 120R termination is
// a DIP switch, off as shipped; the base end carries R6 across the pair.
//
// Waveshare wires GPIO43 to RS485_RXD and GPIO44 to RS485_TXD. Those are opposite
// the ROM's fixed UART0 direction (43 TX, 44 RX), so the ROM neither receives from
// nor transmits onto the A/B pair. `RS485:SWAP` exchanges the application mapping and
// reports which way round it is now running.
#define RS485_BAUD 115200
static int rs485Rx = 43;
static int rs485Tx = 44;

// ── CH422G I/O expander ───────────────────────────────────────
// Not a normal single-register expander: each "register" is its own 7-bit
// I2C address, and you write one bare data byte to it (no register pointer).
//   • write 0x01 to MODE (0x24)  -> EXIO0..7 become push-pull outputs
//   • write a byte to WR_IO (0x38) -> sets EXIO0..7 levels, where EXIO_n = bit n
// On this board the backlight and both resets hang off the expander, so the
// panel stays dark until these are driven.
#define CH422G_MODE   0x24   // system/mode register (output-enable)
#define CH422G_WR_IO  0x38   // EXIO0..7 output byte
#define EXIO_TP_RST   (1 << 1)  // EXIO1 — GT911 touch reset
#define EXIO_BL       (1 << 2)  // EXIO2 — LCD backlight enable (DISP)
#define EXIO_LCD_RST  (1 << 3)  // EXIO3 — RGB panel reset
#define EXIO_SD_CS    (1 << 4)  // EXIO4 — microSD chip select (held high = deselected)

// Shadow of the EXIO output byte so backlight toggles don't disturb the
// reset / SD-CS lines.
static volatile uint8_t exioState = 0;

// ── RGB panel (esp_lcd, double framebuffer) ──
// The panel has no controller of its own — the ESP32-S3 streams pixels from a
// PSRAM framebuffer by DMA. With a single framebuffer, writing it (the
// animation) while the DMA scans it starves the DMA FIFO and shears the image.
// Two framebuffers fix this structurally: LVGL renders one while the bounce path
// copies the other, then the full-frame completion swaps their roles. We drive
// esp_lcd directly because Arduino_GFX's RGB display hardcodes one framebuffer.
static esp_lcd_panel_handle_t panel = nullptr;
static SemaphoreHandle_t frameDoneSem = nullptr;
static void *fb0 = nullptr, *fb1 = nullptr;

// ── LVGL display buffer ──
// In full-refresh double-buffer mode LVGL's two draw buffers ARE the two panel
// framebuffers (zero-copy: flush submits the just-drawn one), so no separate draw
// buffer is allocated.
static lv_disp_draw_buf_t draw_buf;
static uint32_t flushCount = 0;   // frame submissions completed, per GET_DIAG
static volatile uint32_t vsyncCount = 0;
static volatile uint32_t frameDoneCount = 0;
static uint32_t panelDrawErrors = 0;
static uint32_t frameDoneTimeouts = 0;

// ── Shell geometry ──
// The rail fills the screen height between its 8 px top and bottom rims; the
// pane takes the remaining 76% of the width.
#define RAIL_W          190
#define RAIL_INSET_Y      8
#define RAIL_ITEM_GAP     8
#define RAIL_ITEM_H     110
#define RAIL_ITEM_PAD     6
// The word sits on the floor of the target; the icon centres in what is left,
// so growing or shrinking a target keeps the pair together rather than pulling
// it apart. Icon heights are the glyph box the font was built at.
#define RAIL_ICON_TOP(h) ((RAIL_ITEM_H - 2 * RAIL_ITEM_PAD - TEXT_H_20 - (h)) / 2)
#define PANE_W    (SCREEN_W - RAIL_W)
#define PANE_H    (SCREEN_H - 2 * PANE_PAD)

// Settings is not a customer destination and holds no rail slot. It is one
// square in the screen's top-right corner, over every page.
#define SETTINGS_BTN  64
#define SETTINGS_GAP  14

// The settings square floats over every pane from the screen root, so it is not
// in any pane's layout and every pane has to keep its own top band clear of it.
// A pane titles itself in that band and starts its body below it.
#define PANE_HEAD_H   SETTINGS_BTN
#define PANE_BODY_Y   (PANE_HEAD_H + 12)

// Heights LVGL actually renders these at, so a row can be centred against a
// number rather than an estimate of one.
#define TEXT_H_20   22
#define TEXT_H_28   30
#define TEXT_H_40   44

// Choose gives each card a settings target under it. The badge only reports the
// selection — the whole card is the target that changes it — so it takes the
// height of its own text rather than a finger's.
#define HOME_GEAR_H    56
#define HOME_GEAR_GAP  16
#define HOME_BADGE_H   44
#define HOME_CARD_H    (PANE_H - PANE_BODY_Y - HOME_GEAR_H - HOME_GEAR_GAP)

// The flavor's own page: ratio, then every logo it could wear.
#define RATIO_CARD_H  130
#define THUMB_BTN     104
#define THUMB_GAP      10
#define THUMB_PER_ROW   5
#define IMAGE_LABEL_Y (PANE_BODY_Y + RATIO_CARD_H + 12)
#define THUMB_GRID_Y  (IMAGE_LABEL_Y + TEXT_H_20 + 8)
#define PANE_PAD  16

// ── Pages ──
// Every page is built once and lives for the life of the firmware; switching hides one and
// shows another. Sub-views inside a page work the same way.
enum Page { PAGE_HOME, PAGE_FLAVOR, PAGE_SERVICE, PAGE_SETUP, PAGE_COUNT };

enum FlavorView  { FLV_DETAIL, FLV_COUNT };
enum ServiceView { SVC_PRIME_PICK, SVC_PRIME_HOLD, SVC_CLEAN_PICK,
                   SVC_CLEAN_CONFIRM, SVC_FILL_PICK, SVC_FILL_CONFIRM, SVC_COUNT };

// The left rail names the customer-facing destinations. Choose is the drink;
// Fill, Prime and Clean are a flavor's life in the machine, in the order it is
// lived — pour concentrate into the hopper, push it out to the nozzle, and
// eventually flush it back out. The three share their controller/session
// machinery beneath the glass, but each is its own place in the interaction,
// asking for the flavor it acts on. What one flavor pours at, and which logo it
// wears, belong to that flavor rather than to the machine, and are reached from
// its own card on Choose.
enum RailPage { RAIL_CHOOSE, RAIL_FILL, RAIL_PRIME, RAIL_CLEAN,
                RAIL_PAGE_COUNT };

static_assert(2 * RAIL_INSET_Y + RAIL_PAGE_COUNT * RAIL_ITEM_H +
                  (RAIL_PAGE_COUNT - 1) * RAIL_ITEM_GAP == SCREEN_H,
              "customer rail must fill the screen height");

static lv_obj_t *pageObj[PAGE_COUNT];
static lv_obj_t *railBtn[RAIL_PAGE_COUNT];
static lv_obj_t *flvView[FLV_COUNT];
static lv_obj_t *svcView[SVC_COUNT];
static Page activePage = PAGE_HOME;
static ServiceView activeSvc = SVC_PRIME_PICK;
static FlavorView  activeFlv = FLV_DETAIL;
static RailPage activeRail = RAIL_CHOOSE;
static bool uiReady = false;

static void showPage(Page p);
static void showRail(RailPage p);
static void setRailSelection(RailPage p);
static void showFlavor(FlavorView v);
static void refreshFlavorImages();
static void showService(ServiceView v);
static void animRun(bool on);
static void idleReset(uint8_t stage);
static void refreshHomeSelection();
static bool primeLinkOwnsJ9();
static void primeSessionService();
static void lockScreenShow(const char *kicker, const char *title, const char *body);
static void lockScreenHide();

// ── UI objects ──
static lv_obj_t *lockScreen, *lockLogoImg, *lockKicker, *lockTitle, *lockBody;
static lv_img_dsc_t frameDsc[NUM_ANIM_FRAMES];
static lv_timer_t *animTimer = nullptr;
static uint8_t animFrameIdx = 0;
static bool lockActive = false;
static bool bootLockActive = false;
static unsigned long bootLockMinUntil = 0;
static unsigned long bootLockMaxUntil = 0;

// Which logo each channel wears. Display-local, like the ratio beside it: this
// panel scans an 800x480 framebuffer out of PSRAM, and a flash write suspends
// the cache PSRAM is reached through, so the DMA refilling its bounce buffer
// faults. Nothing on this board writes NVS while the panel runs. The durable
// home for the choice is the controller, which is where the faucet's own
// selection already lives.
static uint8_t flavorImage[2] = {0, 1};
static bool flavorArtAsked = false;

static lv_img_dsc_t flavorArt[FLAVOR_IMAGE_COUNT];
static lv_img_dsc_t flavorThumb[FLAVOR_IMAGE_COUNT];
static lv_img_dsc_t flavorHead[FLAVOR_IMAGE_COUNT];
static lv_img_dsc_t flavorMid[FLAVOR_IMAGE_COUNT];
static const uint16_t *flavorArtPixels[FLAVOR_IMAGE_COUNT] = {
    flavor0_240, flavor1_240, flavor2_240, flavor3_240,
};
static const uint16_t *flavorThumbPixels[FLAVOR_IMAGE_COUNT] = {
    flavor0_thumb, flavor1_thumb, flavor2_thumb, flavor3_thumb,
};
static const uint16_t *flavorHeadPixels[FLAVOR_IMAGE_COUNT] = {
    flavor0_head, flavor1_head, flavor2_head, flavor3_head,
};
static const uint16_t *flavorMidPixels[FLAVOR_IMAGE_COUNT] = {
    flavor0_mid, flavor1_mid, flavor2_mid, flavor3_mid,
};

// A channel is named by its logo rather than by a number, so every surface that
// used to print one registers the image standing in for it. Some always show one
// particular channel; the rest follow whichever channel the screen is acting on.
#define FLAVOR_IMG_SLOTS 8
static lv_obj_t *chanImg[FLAVOR_IMG_SLOTS];
static uint8_t   chanImgCh[FLAVOR_IMG_SLOTS];
static const lv_img_dsc_t *chanImgSet[FLAVOR_IMG_SLOTS];
static uint8_t   chanImgCount = 0;
static lv_obj_t *selImg[FLAVOR_IMG_SLOTS];
static const lv_img_dsc_t *selImgSet[FLAVOR_IMG_SLOTS];
static uint8_t   selImgCount = 0;
static lv_obj_t *homeFlavorArtObj[2];
static lv_obj_t *flvThumbBtn[FLAVOR_IMAGE_COUNT];
static lv_obj_t *homeFlavorCard[2];
static lv_obj_t *homeFlavorBadge[2];
static lv_obj_t *homeFlavorBadgeText[2];
static lv_obj_t *homeSyncLabel;

// Choose receives the controller's flavor state four times a second while lit.
// Keep the rendered model separate from the replicated model so a routine,
// unchanged answer does not invalidate a large card and flip the RGB panel's
// framebuffer. Negative sentinels guarantee one complete initial render.
enum HomeSyncVisual : uint8_t {
  HOME_SYNC_CONNECTING,
  HOME_SYNC_SAVING,
  HOME_SYNC_ERROR,
  HOME_SYNC_HEALTHY,
};
static int8_t homeFlavorShown = -2;
static int8_t homeSyncShown = -1;

static lv_obj_t *flvDetailRatio;
static lv_obj_t *primePad, *primePadLbl, *primeElapsed, *primeBar, *primeMsg;
static lv_indev_t *touchInput = nullptr;
static lv_obj_t *cleanMsg, *fillMsg;
static lv_obj_t *settingsBtn;      // top-right of the screen, outside the pane

// Flavor 1 and 2 as this panel holds them. The base carries no config store, so a ratio
// changed here is this display's own until one sends it somewhere.
static uint8_t flavorRatio[2] = {20, 20};
static uint8_t flavorSel = PUMP_CHANNEL_B;   // which flavor the detail and hold pages act on

// The flavor used for dispensing is separate from flavorSel above, which is
// only the target currently open in a service/configuration view. The
// controller owns this value; the enclosure applies a press optimistically and
// reconciles it from MSG_RESP_FLAVOR_STATE.
static uint8_t activeFlavor = PUMP_CHANNEL_A;
static bool flavorSynchronized = false;
static bool flavorControllerPersisted = false;
static bool flavorControllerPersistError = false;
static bool flavorRequestPending = false;
static bool flavorQueryOutstanding = false;
static uint32_t flavorRequestToken = 0;
static uint32_t flavorTokenState = 1;
static unsigned long flavorRequestStartedMs = 0;
static unsigned long flavorRequestLastQueuedMs = 0;
static unsigned long flavorQueryQueuedMs = 0;
static unsigned long flavorStateMs = 0;
static uint32_t flavorRetries = 0;
static uint32_t flavorStaleResponses = 0;

#define FLAVOR_QUERY_ACTIVE_MS      250
#define FLAVOR_QUERY_BACKGROUND_MS  500
#define FLAVOR_RESPONSE_TIMEOUT_MS  600
#define FLAVOR_AUDIBLE_FRESH_MS     300
#define BOOT_LOCK_MIN_MS            (NUM_ANIM_FRAMES * ANIM_FRAME_MS * 2)
#define BOOT_LOCK_MAX_MS            6000

// ── Idle backlight-off (the faucet's idle behavior, adapted to this board) ──
// The backlight is a digital line on the CH422G (on/off only — no PWM), so the
// idle state is simply the backlight off. Normal pages are static; an active
// operation lock is deliberately exempt from idle. Instant off / instant on.
// Three timers, and the last two run from the moment the screen goes dark so that changing
// how long it stays lit does not move them.
//
// Someone who stepped away for the flavor bottle comes back to the pad they were holding.
// Someone back after a few minutes comes back to the area they were working in, without
// the view inside it that would have acted on a tap — a confirm, a hold pad, a stepper.
// Someone back much later arrives at Choose, because by then they may not be the same person.
#define IDLE_TIMEOUT_MS   90000   // touch -> dark
#define KEEP_VIEW_MS     120000   // dark -> the root of the page you were on
#define KEEP_AREA_MS     600000   // dark -> Choose

static unsigned long lastInputTime = 0;
static unsigned long darkSince = 0;
static uint8_t idleStage = 0;    // 0 lit · 1 dark · 2 at the page's root · 3 Choose
static bool screenIdle = false;  // true while asleep (backlight off via idle)

// ── Touch (GT911) ──
static uint8_t gt911Addr = 0;     // probed at init (0 = not found)
static uint32_t touchCount = 0;   // diagnostics: presses seen since last GET_DIAG
static uint16_t lastTouchX = 0, lastTouchY = 0;  // where the last press landed
static uint8_t lastRaw[8] = {0};                 // the GT911's own bytes for that press
static uint8_t lastStatus = 0;

// ── Diagnostics (read via GET_DIAG) ──
static uint32_t maxLoopMs = 0;
static volatile bool backlightOn = false;
static bool displayReady = false;  // false if the panel failed to init
static bool usbReattachPending = false;
static unsigned long usbReattachAt = 0;
static volatile uint32_t exioWriteErrors = 0;

// The touch controller and CH422G share one I2C controller.  The panel's reset
// and DISP lines must change during vertical blank, so the VSYNC task takes this
// mutex only if the bus is idle; otherwise it waits for the next blank rather
// than writing a display-control edge late in an active scan.
static SemaphoreHandle_t i2cMutex = nullptr;

enum PanelVsyncAction : uint8_t {
  PANEL_VSYNC_NONE,
  PANEL_VSYNC_RELEASE_RESET,
  PANEL_VSYNC_ENABLE_DISPLAY,
};

static portMUX_TYPE panelVsyncActionMux = portMUX_INITIALIZER_UNLOCKED;
static TaskHandle_t panelVsyncTaskHandle = nullptr;
static volatile PanelVsyncAction panelVsyncAction = PANEL_VSYNC_NONE;
static volatile bool panelVsyncActionDone = false;
static volatile uint32_t panelVsyncCycleAt = 0;
static volatile uint32_t panelVsyncActionsQueued = 0;
static volatile uint32_t panelVsyncActionsDone = 0;
static volatile uint32_t panelVsyncBusRetries = 0;
static volatile uint32_t panelVsyncLateRetries = 0;
static volatile uint32_t panelVsyncWriteErrors = 0;

// The board runs at a fixed 240 MHz (PM is disabled in this firmware core).
// VSYNC_END starts a 32-line back porch, about 1.95 ms at the panel timing.
// Reserve its latter half for the 100-kHz CH422G transfer instead of gambling
// that a task delayed by an interrupt can still finish before active pixels.
#define PANEL_VSYNC_ACTION_WINDOW_US 900
#define PANEL_CPU_CYCLES_PER_US       240
#define PANEL_VSYNC_ACTION_WINDOW_CYCLES \
  (PANEL_VSYNC_ACTION_WINDOW_US * PANEL_CPU_CYCLES_PER_US)

// ════════════════════════════════════════════════════════════
//  CH422G expander
// ════════════════════════════════════════════════════════════

static bool i2cTake(TickType_t wait) {
  return !i2cMutex || xSemaphoreTake(i2cMutex, wait) == pdTRUE;
}

static void i2cGive() {
  if (i2cMutex) xSemaphoreGive(i2cMutex);
}

static bool ch422gWriteLocked(uint8_t addr, uint8_t val) {
  Wire.beginTransmission(addr);  // addr is the 7-bit "register"/command address
  Wire.write(val);               // single data byte, no register pointer
  const uint8_t result = Wire.endTransmission();
  if (result != 0) exioWriteErrors++;
  return result == 0;
}

static bool ch422gWrite(uint8_t addr, uint8_t val) {
  if (!i2cTake(portMAX_DELAY)) return false;
  const bool ok = ch422gWriteLocked(addr, val);
  i2cGive();
  return ok;
}

static bool exioApplyLocked() { return ch422gWriteLocked(CH422G_WR_IO, exioState); }

static bool exioApply() {
  if (!i2cTake(portMAX_DELAY)) return false;
  const bool ok = exioApplyLocked();
  i2cGive();
  return ok;
}

static bool setBacklightLocked(bool on) {
  if (on) exioState |= EXIO_BL; else exioState &= ~EXIO_BL;
  if (!exioApplyLocked()) return false;
  backlightOn = on;
  return true;
}

static bool setBacklight(bool on) {
  if (!i2cTake(portMAX_DELAY)) return false;
  const bool ok = setBacklightLocked(on);
  i2cGive();
  return ok;
}

static bool panelSetDarkAndReset() {
  if (!i2cTake(portMAX_DELAY)) return false;
  exioState &= ~(EXIO_BL | EXIO_LCD_RST);
  const bool ok = exioApplyLocked();
  if (ok) backlightOn = false;
  i2cGive();
  return ok;
}

// This is only the timeout fallback for a missing VSYNC task. Normal wakes use
// panelVsyncTask(), which changes this line in the next vertical blank.
static bool panelReleaseResetNow() {
  if (!i2cTake(portMAX_DELAY)) return false;
  exioState |= EXIO_LCD_RST;
  const bool ok = exioApplyLocked();
  i2cGive();
  return ok;
}

// Bring up the expander and pulse the panel + touch resets. Leaves the
// backlight OFF (turned on after the first frame is drawn, to avoid a boot
// flash of uninitialized framebuffer).
static void ch422gBringUp() {
  Wire.begin(I2C_SDA, I2C_SCL);
  ch422gWrite(CH422G_MODE, 0x01);  // EXIO0..7 -> push-pull output

  // Assert both resets low (SD held deselected), then release high.
  exioState = EXIO_SD_CS;
  exioApply();
  delay(20);
  exioState = EXIO_SD_CS | EXIO_LCD_RST | EXIO_TP_RST;  // backlight still off
  exioApply();
  delay(120);  // panel reset-recovery
}

// ════════════════════════════════════════════════════════════
//  RGB panel (esp_lcd)
// ════════════════════════════════════════════════════════════

// The RGB driver performs an underflow-only scan recovery after this callback.
// The only work done here is count the edge and wake the higher-priority task
// that owns the CH422G transition; I2C itself is never touched from an ISR.
static bool IRAM_ATTR onVsync(esp_lcd_panel_handle_t p,
                              const esp_lcd_rgb_panel_event_data_t *e, void *ctx) {
  (void)p; (void)e; (void)ctx;
  panelVsyncCycleAt = esp_cpu_get_cycle_count();
  __atomic_add_fetch(&vsyncCount, 1, __ATOMIC_RELAXED);
  BaseType_t hp = pdFALSE;
  portENTER_CRITICAL_ISR(&panelVsyncActionMux);
  if (panelVsyncAction != PANEL_VSYNC_NONE && panelVsyncTaskHandle) {
    vTaskNotifyGiveFromISR(panelVsyncTaskHandle, &hp);
  }
  portEXIT_CRITICAL_ISR(&panelVsyncActionMux);
  return hp == pdTRUE;
}

// With a bounce buffer, VSYNC is not the point at which the previous framebuffer
// is safe for LVGL to reuse. The RGB driver raises this after it has copied one
// complete framebuffer through the bounce buffers and selected the next one.
// Keep the ISR callback to a counter and a semaphore; LVGL itself runs in loop().
static bool IRAM_ATTR onFrameDone(esp_lcd_panel_handle_t p,
                        const esp_lcd_rgb_panel_event_data_t *e, void *ctx) {
  (void)p; (void)e; (void)ctx;
  __atomic_add_fetch(&frameDoneCount, 1, __ATOMIC_RELAXED);
  BaseType_t hp = pdFALSE;
  xSemaphoreGiveFromISR(frameDoneSem, &hp);
  return hp == pdTRUE;
}

// Queue exactly one panel-control transition for the next vertical blank. The
// queue stays occupied until the write completed, so a contended I2C bus causes
// a retry at a later blank rather than a late edge in the current visible frame.
static bool panelQueueVsyncAction(PanelVsyncAction action) {
  if (!panelVsyncTaskHandle) return false;
  bool queued = false;
  portENTER_CRITICAL(&panelVsyncActionMux);
  if (panelVsyncAction == PANEL_VSYNC_NONE) {
    panelVsyncAction = action;
    panelVsyncActionDone = false;
    panelVsyncActionsQueued++;
    queued = true;
  }
  portEXIT_CRITICAL(&panelVsyncActionMux);
  return queued;
}

static bool panelVsyncActionFinished() {
  bool done;
  portENTER_CRITICAL(&panelVsyncActionMux);
  done = panelVsyncActionDone;
  portEXIT_CRITICAL(&panelVsyncActionMux);
  return done;
}

static void panelCancelVsyncAction() {
  // Taking the I2C lock first makes cancellation wait for an in-flight
  // expander transfer. Conversely, panelVsyncTask rechecks the action after
  // acquiring that same lock, so a cancellation that wins the race cannot
  // leave a stale DISP/reset write behind.
  if (!i2cTake(portMAX_DELAY)) return;
  portENTER_CRITICAL(&panelVsyncActionMux);
  panelVsyncAction = PANEL_VSYNC_NONE;
  panelVsyncActionDone = false;
  portEXIT_CRITICAL(&panelVsyncActionMux);
  i2cGive();
}

static void panelVsyncTask(void *arg) {
  (void)arg;
  for (;;) {
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

    PanelVsyncAction action;
    portENTER_CRITICAL(&panelVsyncActionMux);
    action = panelVsyncAction;
    portEXIT_CRITICAL(&panelVsyncActionMux);
    if (action == PANEL_VSYNC_NONE) continue;

    if ((uint32_t)(esp_cpu_get_cycle_count() - panelVsyncCycleAt) >
        PANEL_VSYNC_ACTION_WINDOW_CYCLES) {
      panelVsyncLateRetries++;
      continue;
    }

    // Waiting here would make an expander write land after the blank. Give the
    // touch transaction the current frame, then retry at the next VSYNC.
    if (!i2cTake(0)) {
      panelVsyncBusRetries++;
      continue;
    }

    bool stillPending;
    portENTER_CRITICAL(&panelVsyncActionMux);
    stillPending = panelVsyncAction == action;
    portEXIT_CRITICAL(&panelVsyncActionMux);
    if (!stillPending) {
      i2cGive();
      continue;
    }

    if ((uint32_t)(esp_cpu_get_cycle_count() - panelVsyncCycleAt) >
        PANEL_VSYNC_ACTION_WINDOW_CYCLES) {
      i2cGive();
      panelVsyncLateRetries++;
      continue;
    }

    bool ok = false;
    if (action == PANEL_VSYNC_RELEASE_RESET) {
      exioState |= EXIO_LCD_RST;
      ok = exioApplyLocked();
    } else if (action == PANEL_VSYNC_ENABLE_DISPLAY) {
      ok = setBacklightLocked(true);
    }
    i2cGive();

    if (!ok) {
      panelVsyncWriteErrors++;
      continue;
    }

    portENTER_CRITICAL(&panelVsyncActionMux);
    if (panelVsyncAction == action) {
      panelVsyncAction = PANEL_VSYNC_NONE;
      panelVsyncActionDone = true;
      panelVsyncActionsDone++;
    }
    portEXIT_CRITICAL(&panelVsyncActionMux);
  }
}

// Returns false (never hangs/aborts) on any failure, so a panel problem leaves
// the board responsive on serial rather than wedged.
static bool panelInit() {
  frameDoneSem = xSemaphoreCreateBinary();
  if (!frameDoneSem) return false;

  esp_lcd_rgb_panel_config_t cfg = {};
  cfg.clk_src = LCD_CLK_SRC_DEFAULT;
  // 16 MHz. The porches below are the panel's, and it does not lock to them at 14: the
  // repaint measured 105 ms instead of 117 and the screen stayed blank, backlight lit and
  // LVGL still cycling frames into a buffer nothing was drawing.
  cfg.timings.pclk_hz = 16 * 1000 * 1000;
  cfg.timings.h_res = SCREEN_W;
  cfg.timings.v_res = SCREEN_H;
  cfg.timings.hsync_pulse_width = 48;
  cfg.timings.hsync_back_porch  = 88;
  cfg.timings.hsync_front_porch = 40;
  cfg.timings.vsync_pulse_width = 3;
  cfg.timings.vsync_back_porch  = 32;
  cfg.timings.vsync_front_porch = 13;
  cfg.timings.flags.pclk_active_neg = 1;  // 4.3B: data latched on the falling edge
  cfg.timings.flags.hsync_idle_low  = 1;  // polarity 0
  cfg.timings.flags.vsync_idle_low  = 1;
  cfg.data_width = 16;
  cfg.bits_per_pixel = 16;
  cfg.num_fbs = 2;                  // double framebuffer — kills content tearing
  // Bounce buffer: the scan-out DMA reads pixels from this small internal-SRAM
  // buffer (refilled from the PSRAM framebuffer in the background) instead of
  // straight from PSRAM. That's what stops the horizontal shearing: CPU writes
  // to PSRAM (the render) can no longer starve the live scanline. 10 lines: at 20
  // the refill work costs 1.3 fps on Choose and 28 ms on a full pane repaint, and a frame
  // the DMA has fallen behind on is what esp_lcd_rgb_panel_restart() is for.
  cfg.bounce_buffer_size_px = SCREEN_W * 10;
  cfg.dma_burst_size = 64;
  cfg.hsync_gpio_num = LCD_HSYNC;
  cfg.vsync_gpio_num = LCD_VSYNC;
  cfg.de_gpio_num    = LCD_DE;
  cfg.pclk_gpio_num  = LCD_PCLK;
  cfg.disp_gpio_num  = GPIO_NUM_NC;
  // Little-endian RGB565 data order (B0..B4, G0..G5, R0..R4).
  const int data[16] = {LCD_B0, LCD_B1, LCD_B2, LCD_B3, LCD_B4,
                        LCD_G0, LCD_G1, LCD_G2, LCD_G3, LCD_G4, LCD_G5,
                        LCD_R0, LCD_R1, LCD_R2, LCD_R3, LCD_R4};
  for (int i = 0; i < 16; i++) cfg.data_gpio_nums[i] = data[i];
  cfg.flags.fb_in_psram = 1;
  cfg.flags.double_fb = 1;
  cfg.flags.bb_invalidate_cache = 0;

  if (esp_lcd_new_rgb_panel(&cfg, &panel) != ESP_OK) return false;

  esp_lcd_rgb_panel_event_callbacks_t cbs = {};
  cbs.on_vsync = onVsync;
  cbs.on_frame_buf_complete = onFrameDone;
  if (esp_lcd_rgb_panel_register_event_callbacks(panel, &cbs, nullptr) != ESP_OK) return false;

  if (esp_lcd_panel_reset(panel) != ESP_OK) return false;
  if (esp_lcd_panel_init(panel)  != ESP_OK) return false;
  if (esp_lcd_rgb_panel_get_frame_buffer(panel, 2, &fb0, &fb1) != ESP_OK) return false;

  // Clear both buffers so nothing garbage shows before the first frame.
  memset(fb0, 0, (size_t)SCREEN_W * SCREEN_H * sizeof(uint16_t));
  memset(fb1, 0, (size_t)SCREEN_W * SCREEN_H * sizeof(uint16_t));
  return true;
}

// panelInit() runs on its own task so that if esp_lcd ever blocks during init
// (the bounce-buffer path wedged this core once via Arduino_GFX), setup() can
// time out and return — loop() keeps servicing serial, so the board stays
// flashable without a manual BOOT-button recovery.
static volatile bool panelInitDone = false;
static volatile bool panelInitOk = false;
static void panelInitTask(void *arg) {
  panelInitOk = panelInit();
  panelInitDone = true;
  vTaskDelete(nullptr);
}

// ════════════════════════════════════════════════════════════
//  Touch (GT911) + idle dimming
// ════════════════════════════════════════════════════════════

// The three routines below are called with i2cMutex held. Keeping a GT911
// status/read/ack sequence together also leaves the VSYNC task one clean place
// to decide whether this frame's blank has enough bus time for EXIO.
static bool gt911ReadBytes(uint16_t reg, uint8_t *buf, size_t len) {
  Wire.beginTransmission(gt911Addr);
  Wire.write(reg >> 8);
  Wire.write(reg & 0xFF);
  if (Wire.endTransmission(false) != 0) return false;  // repeated start
  size_t got = Wire.requestFrom((int)gt911Addr, (int)len);
  for (size_t i = 0; i < len && Wire.available(); i++) buf[i] = Wire.read();
  return got == len;
}

static void gt911WriteByte(uint16_t reg, uint8_t val) {
  Wire.beginTransmission(gt911Addr);
  Wire.write(reg >> 8);
  Wire.write(reg & 0xFF);
  Wire.write(val);
  Wire.endTransmission();
}

// Probe the two possible GT911 addresses; returns the one that ACKs (0 = none).
static uint8_t gt911Probe() {
  if (!i2cTake(portMAX_DELAY)) return 0;
  const uint8_t addrs[2] = {GT911_ADDR_A, GT911_ADDR_B};
  uint8_t found = 0;
  for (int i = 0; i < 2; i++) {
    Wire.beginTransmission(addrs[i]);
    if (Wire.endTransmission() == 0) {
      found = addrs[i];
      break;
    }
  }
  i2cGive();
  return found;
}

// Reads the first touch point. Returns true if a finger is down; fills x,y.
//
// Bit 7 of 0x814E is raised when the GT911 has a NEW frame and cleared by the read below.
// Between frames the last one stands, so a poll that finds the flag clear — or that fails
// on the bus — has learned nothing, and answers with the state it last read. A tap needs
// one PRESSED sample and survives either reading; a hold is PRESSED across every poll it
// spans, and reporting "no finger" on the polls that carry no news ends it.
static uint16_t heldX = 0, heldY = 0;
static bool     heldDown = false;
static uint32_t gt911Stale = 0;   // polls that carried no new frame

static bool gt911ReadTouch(uint16_t *x, uint16_t *y) {
  *x = heldX; *y = heldY;
  if (!gt911Addr) return false;
  if (!i2cTake(portMAX_DELAY)) { gt911Stale++; return heldDown; }
  uint8_t status;
  if (!gt911ReadBytes(GT911_REG_STATUS, &status, 1)) {
    gt911Stale++;
    i2cGive();
    return heldDown;
  }
  if (!(status & 0x80)) {
    gt911Stale++;
    i2cGive();
    return heldDown;
  }

  if ((status & 0x0F) > 0) {
    uint8_t p[8];
    if (gt911ReadBytes(GT911_REG_POINT1, p, 8)) {
      memcpy(lastRaw, p, 8);
      lastStatus = status;
      // 0x814F is the track ID; POINT1 (0x8150) is already X-low, so the coordinates
      // start at p[0] — x low/high, then y low/high, then a 16-bit touch size.
      heldX = *x = (uint16_t)p[0] | ((uint16_t)p[1] << 8);
      heldY = *y = (uint16_t)p[2] | ((uint16_t)p[3] << 8);
      heldDown = true;
    } else {
      gt911Stale++;   // the frame was there and the point read failed — keep the state
    }
  } else {
    heldDown = false;
  }
  gt911WriteByte(GT911_REG_STATUS, 0);  // clear buffer-ready for the next frame
  i2cGive();
  return heldDown;
}

// The front-local RGB driver preserves DMA state through normal VSYNCs. Buffer
// reuse is synchronized from on_frame_buf_complete instead. A panel wake stays
// dark until reset and DISP have each crossed a real vertical blank and complete
// frames have crossed while the panel re-acquires the stream.
#define WAKE_QUIET_MS 200
#define WAKE_RESET_LOW_MS 20
#define WAKE_RESET_RECOVERY_MS 120
#define WAKE_FRAME_COUNT 4
#define WAKE_FRAME_WAIT_MS 500
static unsigned long animResumeDue = 0;

// LCD_RST is the ST7262's, on CH422G EXIO3. EXIO2 is both panel DISP and the
// LED driver. A wake releases reset and later asserts DISP from panelVsyncTask(),
// so neither panel-control edge can land in an active RGB frame. The esp_lcd
// framebuffers remain bound.
//
// Staged from loop() rather than run inline: wake() is reached from the indev read, inside
// lv_timer_handler, which is no place to block while the reset and full frames cross.
static uint8_t kickStage = 0;
static unsigned long kickAt = 0;
static unsigned long kickDeadline = 0;
static uint32_t kickVsyncBase = 0;
static uint32_t kickFrameBase = 0;
static uint32_t kickStarted = 0;
static uint32_t kickCompleted = 0;
static uint32_t kickFrameTimeouts = 0;
static bool kickTimedOut = false;
static bool kickResetQueued = false;
static bool kickDisplayQueued = false;

static void panelKickEnterRecovery(unsigned long now) {
  kickVsyncBase = vsyncCount;
  kickFrameBase = frameDoneCount;
  kickAt = now + WAKE_RESET_RECOVERY_MS;
  kickDeadline = now + WAKE_FRAME_WAIT_MS;
  kickTimedOut = false;
  kickStage = 3;
}

static void panelKickComplete(unsigned long now) {
  animResumeDue = now + WAKE_QUIET_MS;
  kickStage = 0;
  kickCompleted++;
}

static void panelKick() {
  if (kickStage) return;
  // A tap can arrive during the short boot-DISP handoff. A wake owns the next
  // panel transition, so discard that stale request before asserting reset.
  panelCancelVsyncAction();
  kickStage = 1;
  kickAt = millis();
  kickStarted++;
  kickTimedOut = false;
  kickResetQueued = false;
  kickDisplayQueued = false;
  animResumeDue = 0;
  animRun(false);
}

static void panelRealign() {
  if (!panel) return;
  Serial.printf("PANEL: restart=%d\n", (int)esp_lcd_rgb_panel_restart(panel));
}

// Turn the backlight back on and preserve whichever view the dark retained. Always resets
// the idle timer. A tap calls this — "tap to bring the backlight back on."
static void wake() {
  lastInputTime = millis();
  if (screenIdle || !backlightOn) {
    if (kickStage) return;   // a wake is already on its way through the stages
    screenIdle = false;
    idleStage = 0;
    // Whatever the dark decided to keep or throw away is already on screen — waking shows
    // it rather than moving to it. The light comes back once the panel has been reset.
    if (uiReady) panelKick();
    else { setBacklight(true); if (animTimer) lv_timer_resume(animTimer); }
  }
}

// LVGL pointer indev: any touch wakes and resets the idle timer. A touch that begins on a
// dark screen wakes it and reaches no widget — the whole press is withheld, not just the
// sample the wake happened on. wake() clears screenIdle at once, so a finger still resting
// on the glass looks like a fresh press within a few milliseconds; the latch holds until
// that finger lifts. Every widget on this panel inherits it from here.
static bool touchWakesOnly = false;

// A lift has to be reported for this long before it reaches a widget. One poll finding no
// finger, between two that do, is a dropped report — every widget on this panel inherits
// the bridge from here, the same way it inherits the wake suppression above.
// A lift is bridged only once a press has outlasted a tap. Bridging exists so one dropped
// report cannot end a hold; on a tap it is pure delay, and an expensive one — LVGL sees the
// release this much later, and the click and its repaint follow that.
#define TOUCH_RELEASE_MS 150
#define TOUCH_TAP_MS     300   // a press shorter than this is a tap, and lifts at once

static uint32_t touchBridged = 0;   // polls carried across a dropped report

// The live point goes to LVGL, so a drag is still a drag. Which objects hold a press that
// slides off them is LV_OBJ_FLAG_PRESS_LOCK's job, per object — see mkBtn().
static void touchpadRead(lv_indev_drv_t *drv, lv_indev_data_t *data) {
  static bool prevTouch = false;
  static unsigned long lastDownMs = 0, pressStartMs = 0;
  static uint32_t bridgedRun = 0;
  uint16_t x = 0, y = 0;
  bool now = gt911ReadTouch(&x, &y);
  bool wasHeld = pressStartMs && (lastDownMs - pressStartMs) >= TOUCH_TAP_MS;

  if (now) {
    lastDownMs = millis();
    if (!prevTouch && bridgedRun == 0) {
      pressStartMs = lastDownMs;
      touchCount++;  // count press edges
      touchWakesOnly = screenIdle || !backlightOn;
      lastTouchX = x;
      lastTouchY = y;
      Serial.printf("[touch] x=%u y=%u  status=0x%02X raw=%02X %02X %02X %02X %02X %02X %02X %02X%s\n",
                    x, y, lastStatus, lastRaw[0], lastRaw[1], lastRaw[2], lastRaw[3],
                    lastRaw[4], lastRaw[5], lastRaw[6], lastRaw[7],
                    touchWakesOnly ? " (dark — wakes only)" : "");
    }
    bridgedRun = 0;
    wake();
    data->point.x = x;
    data->point.y = y;
    data->state = touchWakesOnly ? LV_INDEV_STATE_RELEASED : LV_INDEV_STATE_PRESSED;
  } else if (wasHeld && millis() - lastDownMs < TOUCH_RELEASE_MS) {
    // gt911ReadTouch leaves x,y at the last point it actually saw. lastTouchX/Y is where
    // the press began, which a tap never leaves and a drag leaves entirely: reporting it
    // here teleports the finger back to the start of the drag, and the scroll follows.
    bridgedRun++;
    touchBridged++;
    data->point.x = x;
    data->point.y = y;
    data->state = touchWakesOnly ? LV_INDEV_STATE_RELEASED : LV_INDEV_STATE_PRESSED;
  } else {
    if (lastDownMs) {
      Serial.printf("[touch] up after %lu ms  (%lu poll(s) bridged, %lu stale)\n",
                    (unsigned long)(lastDownMs - pressStartMs),
                    (unsigned long)bridgedRun, (unsigned long)gt911Stale);
      lastDownMs = 0;
      pressStartMs = 0;
      bridgedRun = 0;
    }
    touchWakesOnly = false;   // finger lifted — the next press is the user's own
    data->state = LV_INDEV_STATE_RELEASED;
  }
  prevTouch = now;
}

// ════════════════════════════════════════════════════════════
//  LVGL callbacks
// ════════════════════════════════════════════════════════════

// direct_mode: LVGL draws straight into the back framebuffer at absolute
// coordinates, and only inside the areas that actually changed. It calls this
// once per such area, so most calls have nothing to do — the frame is not
// finished and LVGL has not rotated the buffers yet. Only the last call in a
// refresh submits. In bounce-buffer mode, VSYNC does not prove the old source
// buffer is reusable; on_frame_buf_complete does, after a whole frame has been
// copied and the driver has selected color_p for the next one.
//
// The 100 ms timeout (not portMAX) means a missed completion degrades, never deadlocks.
static void lvglFlush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
  if (!lv_disp_flush_is_last(disp)) { lv_disp_flush_ready(disp); return; }
  const esp_err_t drawn = esp_lcd_panel_draw_bitmap(panel, 0, 0, SCREEN_W, SCREEN_H, color_p);
  if (drawn != ESP_OK) {
    panelDrawErrors++;
    lv_disp_flush_ready(disp);
    return;
  }
  // Drain after submission. If completion raced the call, deliberately wait for
  // one more complete frame; reusing a framebuffer late is safe, early is not.
  xSemaphoreTake(frameDoneSem, 0);
  if (xSemaphoreTake(frameDoneSem, pdMS_TO_TICKS(100)) == pdTRUE) flushCount++;
  else frameDoneTimeouts++;
  lv_disp_flush_ready(disp);
}

// ════════════════════════════════════════════════════════════
//  UI
// ════════════════════════════════════════════════════════════

static void animTimerCb(lv_timer_t *t) {
  (void)t;
  animFrameIdx = (animFrameIdx + 1) % NUM_ANIM_FRAMES;
  if (lockLogoImg) lv_img_set_src(lockLogoImg, &frameDsc[animFrameIdx]);
}

// ════════════════════════════════════════════════════════════
//  RS485 link to the base ESP32
// ════════════════════════════════════════════════════════════

// The transport is the one the appliance already runs between boards: TinyProto Fd over
// the UART, typed frames through ProtoLink. This board's transceiver gates its receiver
// off while driving, so nothing it sends returns and there is no echo to cancel here —
// the base's U7 keeps receiving and cancels its own, a layer below its ProtoLink.
static int lastSendErr = 0;   // last refused send, surfaced by GET_DIAG

static HdlcLink j9;

// ── Taking turns on J9 ────────────────────────────────────────────────────
// The pair is one differential pair, half-duplex, and nothing arbitrates it.
// The controller answers a frame the instant it lands — from inside its receive
// callback — so a second frame sent from here before that answer has come back
// lands on top of it. The controller hears its own transmissions (U7's /RE is
// grounded on the PCBA) and cancels them by matching the echo; a frame of ours
// colliding with its reply destroys that echo, and the frame that gets lost is
// ours. That is what a START that never arrives actually is.
//
// So nothing sends directly. Everything is posted here, and exactly one frame
// is on the wire at a time: the next goes out once the answer has come back, or
// once the turnaround window lapses if that answer is never coming. Order is
// preserved, and a burst — a stepper pushing config and asking for a beep in
// the same breath — is spaced instead of stacked.
struct OutFrame { uint8_t type; uint8_t len; uint8_t data[40]; };
static const uint8_t  OUT_Q_DEPTH   = PRIME_J9_APP_QUEUE_DEPTH;
static const unsigned TURNAROUND_MS = 30;   // a reply is ~2 ms; this is the giving-up point
static_assert(PRIME_HOLD_REPLAY_HISTORY >
                  OUT_Q_DEPTH + PRIME_J9_IN_FLIGHT_DEPTH,
              "controller prime replay ledger must cover the complete J9 queue");

static OutFrame      outQ[OUT_Q_DEPTH];
static uint8_t       outHead = 0, outTail = 0, outCount = 0;
static uint8_t       outHighWater = 0;
static uint32_t      outDropped = 0;
static unsigned long lastTxMs = 0;
static bool          awaitingAnswer = false;
static bool          holding = false;

static void j9Post(uint8_t type, const void *data, uint8_t len) {
  if (len > sizeof(outQ[0].data)) len = sizeof(outQ[0].data);
  if (outCount >= OUT_Q_DEPTH) {
    // The far end has stopped answering. Dropping the OLDEST keeps the newest
    // intent — a finger that just moved matters more than one that already did.
    outTail = (uint8_t)((outTail + 1) % OUT_Q_DEPTH);
    outCount--;
    outDropped++;
  }
  OutFrame &f = outQ[outHead];
  f.type = type;
  f.len  = len;
  if (len && data) memcpy(f.data, data, len);
  outHead = (uint8_t)((outHead + 1) % OUT_Q_DEPTH);
  outCount++;
  if (outCount > outHighWater) outHighWater = outCount;
}

static void j9DiscardQueuedPrimeFeeds(bool endingSession = false) {
  OutFrame kept[OUT_Q_DEPTH];
  uint8_t keptCount = 0;
  for (uint8_t i = 0; i < outCount; ++i) {
    const OutFrame &frame = outQ[(outTail + i) % OUT_Q_DEPTH];
    if (frame.type == MSG_PRIME_SESSION_HOLD_START ||
        frame.type == MSG_PRIME_SESSION_HOLD_TICK) continue;
    if (endingSession && frame.type >= MSG_PRIME_SESSION_SET &&
        frame.type <= MSG_PRIME_SESSION_HOLD_STOP) continue;
    kept[keptCount++] = frame;
  }
  for (uint8_t i = 0; i < keptCount; ++i) outQ[i] = kept[i];
  outTail = 0;
  outHead = keptCount % OUT_Q_DEPTH;
  outCount = keptCount;
}

// Called every loop, before j9.service() drains the wire.
static void j9Pump() {
  if (!outCount) return;
  if (awaitingAnswer && millis() - lastTxMs < TURNAROUND_MS) return;
  OutFrame &f = outQ[outTail];
  int r = j9.send(f.type, f.len ? f.data : nullptr, f.len);
  if (r < 0) { lastSendErr = r; Serial.printf("[J9] send(0x%02X) = %d\n", f.type, r); }
  outTail = (uint8_t)((outTail + 1) % OUT_Q_DEPTH);
  outCount--;
  lastTxMs = millis();
  awaitingAnswer = true;
}

static uint32_t nextFlavorToken() {
  flavorTokenState += 0x9E3779B9u;
  if (flavorTokenState == 0) ++flavorTokenState;
  return flavorTokenState;
}

static void postFlavorSelection(bool audible) {
  FlavorRequestPayload request{
      activeFlavor,
      static_cast<uint8_t>(audible ? FLAVOR_REQ_F_AUDIBLE : 0),
      flavorRequestToken,
  };
  j9Post(MSG_FLAVOR_SELECT, &request, sizeof(request));
  flavorRequestLastQueuedMs = millis();
}

// Local-first, just like the faucet: repaint before the pair is serviced. The
// token and absolute value make the later retry harmless.
static bool selectActiveFlavor(uint8_t flavor) {
  if (flavor > PUMP_CHANNEL_B) return false;
  if (flavorSynchronized && !flavorRequestPending && flavor == activeFlavor) return false;

  activeFlavor = flavor;
  flavorRequestPending = true;
  flavorQueryOutstanding = false;
  flavorRequestToken = nextFlavorToken();
  flavorRequestStartedMs = millis();
  postFlavorSelection(true);
  refreshHomeSelection();
  return true;
}

static void applyFlavorState(const FlavorStatePayload &state) {
  if (state.flavor > PUMP_CHANNEL_B) return;

  flavorControllerPersisted = (state.flags & FLAVOR_STATE_F_PERSISTED) != 0;
  flavorControllerPersistError = (state.flags & FLAVOR_STATE_F_PERSIST_ERROR) != 0;
  flavorStateMs = millis();
  flavorQueryOutstanding = false;

  if (state.token != 0) {
    if (!flavorRequestPending || state.token != flavorRequestToken) {
      ++flavorStaleResponses;
      if (flavorRequestPending) return;
    } else {
      flavorRequestPending = false;
    }
  } else if (flavorRequestPending) {
    // This may be the answer to a query already on the wire when the user
    // pressed a card. The tokenized selection answer is the ordering point.
    return;
  }

  if ((state.flags & FLAVOR_STATE_F_ESTABLISHED) == 0) {
    flavorSynchronized = false;
    refreshHomeSelection();
    return;
  }

  const bool changed = !flavorSynchronized || activeFlavor != state.flavor;
  activeFlavor = state.flavor;
  flavorSynchronized = true;
  refreshHomeSelection();

  // A flavor chosen at the faucet is a real appliance interaction. If this
  // panel was dark, wake it directly onto the mirrored home selection.
  if (changed && screenIdle && !lockActive) {
    showPage(PAGE_HOME);
    wake();
  }
}

static void flavorLinkService() {
  if (primeLinkOwnsJ9()) return;  // prime-ready owns this half-duplex turn
  const unsigned long now = millis();

  if (flavorRequestPending) {
    if (now - flavorRequestLastQueuedMs >= FLAVOR_RESPONSE_TIMEOUT_MS) {
      // A tick detached from its touch is not useful. Only the first, fresh
      // transmission asks for sound; retries preserve state silently.
      postFlavorSelection(now - flavorRequestStartedMs <= FLAVOR_AUDIBLE_FRESH_MS);
      ++flavorRetries;
    }
    return;
  }

  if (flavorQueryOutstanding) {
    if (now - flavorQueryQueuedMs < FLAVOR_RESPONSE_TIMEOUT_MS) return;
    flavorQueryOutstanding = false;
  }

  const unsigned long interval = screenIdle ? FLAVOR_QUERY_BACKGROUND_MS
                                             : FLAVOR_QUERY_ACTIVE_MS;
  if (now - flavorQueryQueuedMs < interval || outCount >= OUT_Q_DEPTH / 2) return;
  j9Post(MSG_FLAVOR_QUERY, nullptr, 0);
  // Asked once per link session; the controller republishes on every change,
  // so a second ask would only crowd a pair that is already telling us.
  if (!flavorArtAsked) {
    j9Post(MSG_FLAVOR_ART_QUERY, nullptr, 0);
    flavorArtAsked = true;
  }
  flavorQueryQueuedMs = now;
  flavorQueryOutstanding = true;
}

// Fire and forget: an ack would double the traffic in order to acknowledge a
// tick, and a tick that arrives late is worse than one that never arrives. A
// refusal is worth knowing about though — this is the one send whose return
// nothing else would ever look at.
static void sendSound(uint8_t id) {
  SoundPlayPayload p{id};
  j9Post(MSG_SOUND_PLAY, &p, sizeof(p));
}

// The base's last StatusPayload remains available to USB diagnostics. It is not
// a standing customer-facing screen.
static StatusPayload ctrlStatus = {};
static unsigned long ctrlStatusMs = 0;
static unsigned long statusAskedMs = 0;

static uint32_t linkReinits = 0;
static uint8_t  unanswered = 0;      // status polls sent since a frame last arrived
static uint32_t padMux[2] = {0, 0}, padOut[2] = {0, 0};

// A prime hold: the finger is down on the pad and ticks are going out under it. holdAckMs
// stays 0 until MSG_RESP_PRIME{RUNNING} lands, which is the difference between a motor
// turning and a frame sent into a bus with nothing on it.
static unsigned long holdStartMs = 0, holdTickMs = 0, holdAckMs = 0;
static bool holdRetried = false;

// Prime-ready is an appliance session, not a page-local pump command. The
// controller owns this complete state and mirrors it to both pieces of glass.
// This display owns only its desired session state and one physical press.
static PrimeSessionStatePayload primeSession = {};
static bool primeSessionKnown = false;
static bool primeSessionDesired = false;
static bool primeSessionCancelPending = false;
static bool primeBootDiscovery = true;
static bool primeStopPending = false;
static bool primeAuthoritativeNavigation = false;
static bool primeUsbStartPending = false;
static bool primeLinkLost = false;
static uint32_t primeTokenState = 1;
static uint32_t primeSessionToken = 0;
static uint32_t primeHoldToken = 0;
static uint32_t primeStopRevision = 0;
static bool primeStopRevisionKnown = false;
static unsigned long primeControlQueuedMs = 0;
static unsigned long primeStateMs = 0;
static unsigned long primeElapsedAnchorAt = 0;
static unsigned long primeLastUiMs = 0;
static unsigned long primeLastReinitMs = 0;
static uint32_t primeElapsedShown = 0;
static uint32_t primeStaleReinits = 0;

#define PRIME_SESSION_POLL_ACTIVE_MS 250
#define PRIME_SESSION_POLL_DARK_MS   500
#define PRIME_SESSION_RETRY_MS      600
#define PRIME_BOOT_SNAPSHOT_RETRY_MS 500
#define PRIME_SESSION_STALE_MS     1800
#define PRIME_REINIT_BACKOFF_MS     2000

static void setPrimeMsg(const char *s);
static void setCleanMsg(const char *s);
static void setFillMsg(const char *s);
static void applyPrimeSessionState(const PrimeSessionStatePayload &state);

static void j9OnMessage(HdlcLink *link, const uint8_t *frame, uint16_t len) {
  awaitingAnswer = false;   // the controller has spoken; the wire is ours again

  (void)link;
  uint8_t type = msgType(frame);
  const uint8_t *payload = msgPayload(frame);
  uint16_t plen = msgPayloadLen(len);
  char buf[64];

  unanswered = 0;   // anything arriving says the far end is still hearing us

  if (type == MSG_DISPLAY_USB_REATTACH) {
    // Answer while the pair is still ours, then leave enough time for the UART to
    // put the frame on the wire. Deep sleep is intentional here rather than
    // ESP.restart(): Espressif documents that deep sleep powers down the S3's USB
    // Serial/JTAG PHY and drops D+, so timer wake presents a real detach/attach to
    // a host even though J9 keeps VIN standing.
    link->sendResponse(MSG_RESP_DISPLAY_USB_REATTACH, 0);
    usbReattachPending = true;
    usbReattachAt = millis() + 100;
    Serial.println("[J9] USB reattach accepted — deep-sleep detach in 100 ms");
    return;
  }

  if (type == MSG_RESP_FLAVOR_ART && plen >= sizeof(FlavorArtPayload)) {
    FlavorArtPayload art;
    memcpy(&art, payload, sizeof(art));
    bool moved = false;
    for (uint8_t i = 0; i < 2; i++) {
      if (art.art[i] < FLAVOR_IMAGE_COUNT && flavorImage[i] != art.art[i]) {
        flavorImage[i] = art.art[i];
        moved = true;
      }
    }
    if (moved && uiReady) refreshFlavorImages();
    return;
  }

  if (type == MSG_RESP_FLAVOR_STATE && plen >= sizeof(FlavorStatePayload)) {
    FlavorStatePayload state;
    memcpy(&state, payload, sizeof(state));
    applyFlavorState(state);
    // Queries arrive four times a second while lit. Their answers are routine
    // state replication, not a serial event; logging all of them can crowd out
    // an explicit USB diagnostic response. Tokenized selection answers remain
    // useful and rare enough to report.
    if (state.token != 0) {
      Serial.printf("[J9] flavor=%u token=%08lX flags=%02X%s\n",
                    state.flavor + 1, (unsigned long)state.token, state.flags,
                    flavorRequestPending ? " pending" : "");
    }
    return;
  }

  if (type == MSG_RESP_PUMP_DONE && plen >= sizeof(ResponsePayload)) {
    Serial.printf("[J9] MSG_RESP_PUMP_DONE ch=%u\n", payload[0]);
    return;
  }

  if (type == MSG_RESP_PRIME_SESSION && plen >= sizeof(PrimeSessionStatePayload)) {
    PrimeSessionStatePayload state;
    memcpy(&state, payload, sizeof(state));
    applyPrimeSessionState(state);
    return;
  }

  // Legacy commissioning/pcba_bench prime responses remain understood even
  // though the production service UI uses the controller-owned session above.
  if (type == MSG_RESP_PRIME && plen >= sizeof(PrimeStatePayload)) {
    if (primeSessionDesired || primeSessionKnown) return;
    PrimeStatePayload st;
    memcpy(&st, payload, sizeof(st));
    Serial.printf("[J9] MSG_RESP_PRIME state=%u ch=%u ms=%lu\n",
                  st.state, st.channel, (unsigned long)st.ms);
    switch (st.state) {
      case PRIME_RUNNING: holdAckMs = millis(); snprintf(buf, sizeof(buf), "pump turning"); break;
      case PRIME_STOPPED: snprintf(buf, sizeof(buf), "stopped after %lu.%lu s",
                                   (unsigned long)st.ms / 1000, ((unsigned long)st.ms % 1000) / 100); break;
      case PRIME_TIMEOUT: snprintf(buf, sizeof(buf), "controller lost the hold"); break;
      case PRIME_LIMIT:   snprintf(buf, sizeof(buf), "stopped at the %lu s ceiling",
                                   (unsigned long)(PRIME_MAX_MS / 1000)); break;
      default:            snprintf(buf, sizeof(buf), "controller refused"); break;
    }
    setPrimeMsg(buf);
    return;
  }

  if (type == MSG_RESP_STATUS && plen >= sizeof(StatusPayload)) {
    memcpy(&ctrlStatus, payload, sizeof(ctrlStatus));
    ctrlStatus.version[sizeof(ctrlStatus.version) - 1] = '\0';
    ctrlStatusMs = millis();
    return;
  }

  if (type == MSG_ERR_UNSUPPORTED) {
    // Fill and Clean both reach the valve manifold and both can be refused. The
    // refusal has to land on the pane the user is actually looking at.
    if (activeSvc == SVC_FILL_PICK || activeSvc == SVC_FILL_CONFIRM) {
      setFillMsg("this controller drives no valves");
    } else {
      setCleanMsg("this controller drives no valves");
    }
    Serial.println("[J9] MSG_ERR_UNSUPPORTED");
    return;
  }

  if (type == MSG_ERR_BUSY) {
    setPrimeMsg("controller busy");
    return;
  }

  Serial.printf("[J9] type 0x%02X, %u byte(s)\n", type, plen);
}

static void j9Begin() {
  // GPIO43 is U0TXD and the bootloader leaves UART0 holding the RX pad, driving it. UART1
  // maps it as its RX all the same, and then reads the pad's own output instead of the
  // transceiver: measured as zero bytes arriving, below HDLC, while the base was
  // replying. gpio_reset_pin hands both pads back to the matrix first, and the same
  // reply then reads `7E 16 01 8F DF 7E` — flag, MSG_RESP_PUMP_DONE, channel, CRC, flag.
  gpio_reset_pin((gpio_num_t)rs485Rx);
  gpio_reset_pin((gpio_num_t)rs485Tx);
  Serial1.begin(RS485_BAUD, SERIAL_8N1, rs485Rx, rs485Tx);
  j9.onMessage = j9OnMessage;
  j9.begin(Serial1, "J9");
  Serial.printf("RS485: rx=GPIO%d tx=GPIO%d @ %d\n", rs485Rx, rs485Tx, RS485_BAUD);
}

// ── The link's own watchdog ───────────────────────────────────────────────
// Measured on the bench: mid-session the base's HDLC stops seeing anything from this board
// while bytesTx keeps climbing 8 per frame and base→display keeps arriving; the base's own
// loopback still reads 6/6. A gpio_reset_pin on both pads and a Serial1 restart recovers
// it, and the first frame or two after that recovery are still lost.
//
// GPIO43/44 are U0TXD/U0RXD. padWatch() samples the IO MUX and GPIO matrix entries for
// both and prints when either changes, which names whatever reclaims them.
static const uint32_t kPadMuxReg[2] = {IO_MUX_GPIO43_REG, IO_MUX_GPIO44_REG};
static const uint32_t kPadOutReg[2] = {GPIO_FUNC43_OUT_SEL_CFG_REG, GPIO_FUNC44_OUT_SEL_CFG_REG};

static void padSample(uint32_t *mux, uint32_t *out) {
  for (int i = 0; i < 2; i++) {
    mux[i] = REG_READ(kPadMuxReg[i]);
    out[i] = REG_READ(kPadOutReg[i]);
  }
}

static void j9Reinit(const char *why) {
  linkReinits++;
  Serial.printf("[J9] reinit #%lu (%s)\n", (unsigned long)linkReinits, why);
  j9.end();
  Serial1.end();
  j9Begin();
  padSample(padMux, padOut);
  unanswered = 0;
}

static void padWatch() {
  uint32_t mux[2], out[2];
  padSample(mux, out);
  for (int i = 0; i < 2; i++) {
    if (mux[i] != padMux[i] || out[i] != padOut[i]) {
      Serial.printf("[J9] GPIO%d re-routed: mux %08lX -> %08lX, outsel %08lX -> %08lX\n",
                    43 + i,
                    (unsigned long)padMux[i], (unsigned long)mux[i],
                    (unsigned long)padOut[i], (unsigned long)out[i]);
      padMux[i] = mux[i];
      padOut[i] = out[i];
    }
  }
}

// One MSG_PUMP_RUN naming the channel and the run length. The base answers
// MSG_RESP_PUMP_DONE once the run has finished.
static void sendPumpRun(uint8_t channel, uint16_t ms) {
  PumpRunPayload req{channel, ms};
  int r = 0; j9Post(MSG_PUMP_RUN, &req, sizeof(req));
  Serial.printf("[J9] MSG_PUMP_RUN ch=%u ms=%u -> send()=%d, bytesTx=%lu bytesRx=%lu\n",
                req.channel, req.ms, r,
                (unsigned long)j9.bytesTx, (unsigned long)j9.bytesRx);
}

// ════════════════════════════════════════════════════════════
//  UI — a rail of pages, and a pane that changes shape
// ════════════════════════════════════════════════════════════

static lv_obj_t *mkText(lv_obj_t *parent, const char *s, const lv_font_t *font, uint32_t color) {
  lv_obj_t *l = lv_label_create(parent);
  lv_label_set_text(l, s);
  lv_obj_set_style_text_font(l, font, 0);
  lv_obj_set_style_text_color(l, lv_color_hex(color), 0);
  return l;
}

// A flat panel. LVGL's default object carries a border and a shadow; neither reads well
// against a dark background at arm's length.
static lv_obj_t *mkCard(lv_obj_t *parent, lv_coord_t w, lv_coord_t h) {
  lv_obj_t *o = lv_obj_create(parent);
  lv_obj_set_size(o, w, h);
  lv_obj_set_style_bg_color(o, lv_color_hex(COL_CARD), 0);
  lv_obj_set_style_border_width(o, 0, 0);
  lv_obj_set_style_radius(o, 14, 0);
  lv_obj_set_style_pad_all(o, 14, 0);
  lv_obj_clear_flag(o, LV_OBJ_FLAG_SCROLLABLE);
  return o;
}

// LVGL re-searches under the finger on every poll while pressed, so a press that slides off
// its target is lost — no click, and inside a scrollable parent the slide scrolls instead.
// PRESS_LOCK stops the re-search: the press stays on the object it began on and a release
// anywhere fires its click. Every button here takes it, and the two that commit something —
// START CLEAN CYCLE — give it back, so sliding off it still cancels.
// ── The click ──
// This panel has no sounder. The machine's one voice is U8 on the controller
// PCBA, so a finger landing on this glass becomes a sound only by crossing J9 —
// which is why it is sent on PRESSED rather than on the click: the round trip
// hides inside the finger's own dwell, and the tick lands where the finger did
// rather than where it lifted.
//
// It says "your touch registered", NOT "that worked". If only success made a
// sound, silence would mean both "you missed" and "the machine refused you", and
// on a capacitive panel with no travel those are exactly the two a user cannot
// otherwise tell apart. Outcomes get their own sounds, from the controller.
//
// A touch that begins on a dark screen is withheld from every widget (see the
// wake latch above), so waking the panel does not tick.
static void sendSound(uint8_t id);

// A press records an INTENT to click; loop() decides whether it needs a frame.
// Sending here would put the click on the pair immediately ahead of whatever the
// button itself sends, and two frames back to back from one press is what makes
// the far end's echo canceller collide with its own reply — see rs485_echo.h.
// One press is one frame on J9, always.
//
// CLICK:0 / CLICK:1 on this board's console takes the click out of the path
// entirely, which is how it gets bisected out of any future latency question.
bool clickSend = true;
static bool     clickPending = false;
static uint32_t framesTxAtPress = 0;

static void clickCb(lv_event_t *e) {
  (void)e;
  if (!clickSend) return;
  clickPending    = true;
  framesTxAtPress = j9.framesTx;   // if this moves, the button spoke for itself
}

// Every button on this panel is made here, so the click is hooked here and
// nowhere else — one hook, and any button added later gets it without anyone
// having to remember. It is added before the caller's own callback, so the
// frame is on the wire before a page rebuild can delay it.
static lv_obj_t *mkBtn(lv_obj_t *parent, lv_coord_t w, lv_coord_t h, uint32_t bg) {
  lv_obj_t *b = lv_btn_create(parent);
  lv_obj_add_event_cb(b, clickCb, LV_EVENT_PRESSED, NULL);
  lv_obj_set_size(b, w, h);
  lv_obj_set_style_radius(b, 14, 0);
  lv_obj_set_style_shadow_width(b, 0, 0);
  lv_obj_set_style_bg_color(b, lv_color_hex(bg), 0);
  lv_obj_set_style_bg_color(b, lv_color_hex(COL_CARD_ON), LV_PART_MAIN | LV_STATE_PRESSED);
  lv_obj_add_flag(b, LV_OBJ_FLAG_PRESS_LOCK);
  return b;
}

// A card-sized target with an icon over a word.
static void mkRailIcon(lv_obj_t *parent, RailPage page) {
  switch (page) {
    case RAIL_CHOOSE:
      lv_obj_align(mkText(parent, "\xEF\x89\x9A", &front_icons_48, COL_TEXT),
                   LV_ALIGN_TOP_MID, 0, RAIL_ICON_TOP(48));
      break;
    case RAIL_FILL:
      lv_obj_align(mkText(parent, "\xEF\x82\xB0", &front_icons_48, COL_TEXT),
                   LV_ALIGN_TOP_MID, 0, RAIL_ICON_TOP(48));
      break;
    case RAIL_PRIME:
      lv_obj_align(mkText(parent, "\xEF\x81\x83", &front_icons_48, COL_TEXT),
                   LV_ALIGN_TOP_MID, 0, RAIL_ICON_TOP(48));
      break;
    case RAIL_CLEAN:
      lv_obj_align(mkText(parent, "\xEE\x81\xAD", &front_icons_48, COL_TEXT),
                   LV_ALIGN_TOP_MID, 0, RAIL_ICON_TOP(48));
      break;
    default: break;
  }
}

static lv_obj_t *mkBack(lv_obj_t *parent, lv_event_cb_t cb, void *user) {
  lv_obj_t *b = mkBtn(parent, 150, 58, COL_CARD);
  lv_obj_align(b, LV_ALIGN_TOP_LEFT, 0, (PANE_HEAD_H - 58) / 2);
  lv_obj_add_event_cb(b, cb, ACT_EVENT, user);
  lv_obj_center(mkText(b, LV_SYMBOL_LEFT "  BACK", &lv_font_montserrat_20, COL_TEXT));
  return b;
}

// A full-bleed layer inside a page. One of a page's views is visible at a time.
static lv_obj_t *mkView(lv_obj_t *parent) {
  lv_obj_t *o = lv_obj_create(parent);
  lv_obj_set_size(o, LV_PCT(100), LV_PCT(100));
  lv_obj_set_style_bg_opa(o, LV_OPA_TRANSP, 0);
  lv_obj_set_style_border_width(o, 0, 0);
  lv_obj_set_style_pad_all(o, 0, 0);
  lv_obj_clear_flag(o, LV_OBJ_FLAG_SCROLLABLE);
  return o;
}

static void showOnly(lv_obj_t **objs, int n, int which) {
  for (int i = 0; i < n; i++) {
    if (i == which) lv_obj_clear_flag(objs[i], LV_OBJ_FLAG_HIDDEN);
    else            lv_obj_add_flag(objs[i], LV_OBJ_FLAG_HIDDEN);
  }
}

// ── Text the link writes into ──
static void setPrimeMsg(const char *s) { if (primeMsg) lv_label_set_text(primeMsg, s); }
static void setCleanMsg(const char *s) { if (cleanMsg) lv_label_set_text(cleanMsg, s); }
static void setFillMsg(const char *s)  { if (fillMsg)  lv_label_set_text(fillMsg, s); }

// Both surfaces a logo choice reaches: the Choose card that wears it, and the
// grid marking which one this flavor is on.
// The controller owns the pair and persists it; this states what the glass now
// wants and takes back whatever the controller ends up holding.
static void sendFlavorArt() {
  FlavorArtPayload art{{flavorImage[0], flavorImage[1]}};
  j9Post(MSG_FLAVOR_ART_SET, &art, sizeof(art));
}

// An image standing for one particular channel, wherever that channel is offered.
static lv_obj_t *mkChannelImg(lv_obj_t *parent, uint8_t channel,
                              const lv_img_dsc_t *set) {
  lv_obj_t *o = lv_img_create(parent);
  lv_img_set_src(o, &set[flavorImage[channel]]);
  lv_obj_clear_flag(o, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
  if (chanImgCount < FLAVOR_IMG_SLOTS) {
    chanImg[chanImgCount] = o;
    chanImgCh[chanImgCount] = channel;
    chanImgSet[chanImgCount] = set;
    chanImgCount++;
  }
  return o;
}

// An image standing for whichever channel the screen is acting on — what carries
// a selection forward once a flavor has been picked.
static lv_obj_t *mkSelectedImg(lv_obj_t *parent, const lv_img_dsc_t *set) {
  lv_obj_t *o = lv_img_create(parent);
  lv_img_set_src(o, &set[flavorImage[flavorSel]]);
  lv_obj_clear_flag(o, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
  if (selImgCount < FLAVOR_IMG_SLOTS) {
    selImg[selImgCount] = o;
    selImgSet[selImgCount] = set;
    selImgCount++;
  }
  return o;
}

static void refreshFlavorImages() {
  for (uint8_t i = 0; i < 2; i++) {
    if (homeFlavorArtObj[i]) lv_img_set_src(homeFlavorArtObj[i], &flavorArt[flavorImage[i]]);
  }
  for (uint8_t i = 0; i < chanImgCount; i++) {
    lv_img_set_src(chanImg[i], &chanImgSet[i][flavorImage[chanImgCh[i]]]);
  }
  for (uint8_t i = 0; i < selImgCount; i++) {
    lv_img_set_src(selImg[i], &selImgSet[i][flavorImage[flavorSel]]);
  }
  for (int i = 0; i < FLAVOR_IMAGE_COUNT; i++) {
    if (!flvThumbBtn[i]) continue;
    lv_obj_set_style_bg_color(
        flvThumbBtn[i],
        lv_color_hex(i == flavorImage[flavorSel] ? COL_ACCENT : COL_CARD), 0);
  }
}

static void refreshFlavorText() {
  char a[16], b[16];
  snprintf(a, sizeof(a), "1:%u", flavorRatio[0]);
  snprintf(b, sizeof(b), "1:%u", flavorRatio[1]);
  if (flvDetailRatio) lv_label_set_text(flvDetailRatio, flavorSel ? b : a);
}

static void refreshHomeSelection() {
  if (!homeSyncLabel) return;
  const bool selectionKnown = flavorSynchronized || flavorRequestPending;
  const int8_t selectedFlavor = selectionKnown ? static_cast<int8_t>(activeFlavor) : -1;
  if (selectedFlavor != homeFlavorShown) {
    homeFlavorShown = selectedFlavor;
    for (uint8_t i = 0; i < 2; ++i) {
      const bool selected = selectedFlavor == static_cast<int8_t>(i);
      lv_obj_set_style_bg_color(homeFlavorCard[i],
                                lv_color_hex(selected ? COL_CARD_ON : COL_CARD), 0);
      // A border consumes a button's inner box. Keep its 1 px layout edge
      // constant and put the retained-selection emphasis outside it, so the
      // artwork and badge never jump when selection changes.
      lv_obj_set_style_border_width(homeFlavorCard[i], 1, 0);
      lv_obj_set_style_border_color(homeFlavorCard[i],
                                    lv_color_hex(selected ? COL_ACCENT : COL_OFF), 0);
      lv_obj_set_style_outline_width(homeFlavorCard[i], selected ? 3 : 0, 0);
      lv_obj_set_style_outline_color(homeFlavorCard[i], lv_color_hex(COL_ACCENT), 0);
      lv_obj_set_style_outline_opa(homeFlavorCard[i], LV_OPA_COVER, 0);
      lv_obj_set_style_outline_pad(homeFlavorCard[i], 0, 0);

      // The card marks and header already explain that both cards are choices.
      // Keep only the retained selection badge; the inactive card stays calm.
      if (selected) {
        lv_obj_set_style_bg_color(homeFlavorBadge[i], lv_color_hex(COL_ACCENT), 0);
        lv_label_set_text(homeFlavorBadgeText[i], LV_SYMBOL_OK);
        lv_obj_set_style_text_color(homeFlavorBadgeText[i], lv_color_hex(COL_TEXT), 0);
        lv_obj_clear_flag(homeFlavorBadge[i], LV_OBJ_FLAG_HIDDEN);
      } else {
        lv_obj_add_flag(homeFlavorBadge[i], LV_OBJ_FLAG_HIDDEN);
      }
    }
  }

  const bool stale = flavorStateMs && millis() - flavorStateMs > 2000;
  HomeSyncVisual syncVisual;
  if (flavorControllerPersistError) {
    syncVisual = HOME_SYNC_ERROR;
  } else if (flavorRequestPending || (flavorSynchronized && !flavorControllerPersisted)) {
    syncVisual = HOME_SYNC_SAVING;
  } else if (!flavorSynchronized || stale) {
    syncVisual = HOME_SYNC_CONNECTING;
  } else {
    syncVisual = HOME_SYNC_HEALTHY;
  }

  if (static_cast<int8_t>(syncVisual) == homeSyncShown) return;
  homeSyncShown = static_cast<int8_t>(syncVisual);

  // Synchronization is infrastructure, not a standing user task. Say nothing
  // when it is healthy; surface only a state that deserves attention or time.
  if (syncVisual == HOME_SYNC_HEALTHY) {
    lv_obj_add_flag(homeSyncLabel, LV_OBJ_FLAG_HIDDEN);
    return;
  }

  lv_obj_clear_flag(homeSyncLabel, LV_OBJ_FLAG_HIDDEN);
  if (syncVisual == HOME_SYNC_ERROR) {
    lv_label_set_text(homeSyncLabel, LV_SYMBOL_WARNING "  NOT SAVED");
    lv_obj_set_style_text_color(homeSyncLabel, lv_color_hex(COL_WARN), 0);
  } else if (syncVisual == HOME_SYNC_SAVING) {
    lv_label_set_text(homeSyncLabel, "SAVING...");
    lv_obj_set_style_text_color(homeSyncLabel, lv_color_hex(COL_ACCENT), 0);
  } else {
    lv_label_set_text(homeSyncLabel, LV_SYMBOL_REFRESH "  CONNECTING");
    lv_obj_set_style_text_color(homeSyncLabel, lv_color_hex(COL_WARN), 0);
  }
}

// ── Prime-ready session — shared controller truth and one local hold ──

static uint32_t nextPrimeToken() {
  primeTokenState += 0x9E3779B9u;
  if (primeTokenState == 0) ++primeTokenState;
  return primeTokenState;
}

static bool primeStateActive() {
  return primeSessionKnown && primeSession.phase != PRIME_SESSION_OFF;
}

static void primeMarkStopPending() {
  if (primeStopPending) return;
  primeStopPending = true;
  primeStopRevisionKnown = primeSessionKnown && primeSessionToken != 0 &&
                           primeSession.sessionToken == primeSessionToken;
  primeStopRevision = primeStopRevisionKnown ? primeSession.revision : 0;
}

static void primeClearStopPending() {
  primeStopPending = false;
  primeStopRevisionKnown = false;
  primeStopRevision = 0;
}

static bool primeLinkOwnsJ9() {
  return primeSessionDesired || primeSessionCancelPending ||
         (primeBootDiscovery && !primeSessionKnown);
}

static void primePostSession(uint8_t action) {
  if (primeSessionToken == 0) return;
  if (action == PRIME_SESSION_CANCEL) j9DiscardQueuedPrimeFeeds(true);
  PrimeSessionRequestPayload request{action, flavorSel, primeSessionToken};
  j9Post(MSG_PRIME_SESSION_SET, &request, sizeof(request));
  primeControlQueuedMs = millis();
}

static void primePostQuery() {
  if (primeSessionToken == 0) return;
  PrimeSessionQueryPayload query{primeSessionToken};
  j9Post(MSG_PRIME_SESSION_QUERY, &query, sizeof(query));
  primeControlQueuedMs = millis();
}

static void primePostBootSnapshotQuery() {
  PrimeSessionQueryPayload query{0};
  j9Post(MSG_PRIME_SESSION_QUERY, &query, sizeof(query));
  primeControlQueuedMs = millis();
}

static void primePostHold(uint8_t type) {
  if (primeSessionToken == 0 || primeHoldToken == 0) return;
  if (type == MSG_PRIME_SESSION_HOLD_STOP) j9DiscardQueuedPrimeFeeds();
  PrimeHoldPayload hold{flavorSel, primeSessionToken, primeHoldToken};
  j9Post(type, &hold, sizeof(hold));
  primeControlQueuedMs = millis();
}

static uint32_t primeDisplayedElapsed() {
  if (!primeSessionKnown || primeSessionToken == 0 ||
      primeSession.sessionToken != primeSessionToken) return 0;
  uint32_t elapsed = primeSession.elapsedMs;
  if (primeSession.phase == PRIME_SESSION_RUNNING && !primeLinkLost) {
    elapsed += millis() - primeElapsedAnchorAt;
    if (elapsed < primeElapsedShown) elapsed = primeElapsedShown;
  }
  if (elapsed > PRIME_MAX_MS) elapsed = PRIME_MAX_MS;
  return elapsed;
}

static void primeRefreshElapsed(bool force = false) {
  if (!primeElapsed || !primeBar) return;
  const uint32_t elapsed = primeDisplayedElapsed();
  if (!force && elapsed / 100 == primeElapsedShown / 100) return;
  primeElapsedShown = elapsed;
  char buf[16];
  snprintf(buf, sizeof(buf), "%lu.%lu s", (unsigned long)elapsed / 1000,
           ((unsigned long)elapsed % 1000) / 100);
  lv_label_set_text(primeElapsed, buf);
  lv_bar_set_value(primeBar, (int32_t)elapsed, LV_ANIM_OFF);
}

static const char *primeOutcomeText(uint8_t outcome) {
  switch (outcome) {
    case PRIME_OUTCOME_STOPPED:       return "hold released";
    case PRIME_OUTCOME_TIMEOUT:       return "controller lost the hold";
    case PRIME_OUTCOME_LIMIT:         return "60 second limit reached";
    case PRIME_OUTCOME_REFUSED:       return "controller refused the hold";
    case PRIME_OUTCOME_CANCELED:      return "prime mode exited";
    case PRIME_OUTCOME_LEASE_EXPIRED: return "prime screen connection lost";
    default:                          return "ready on either display";
  }
}

static void primeRender(bool force = false) {
  if (!primePad || !primePadLbl) return;

  static uint8_t shownPhase = 0xFF;
  static uint8_t shownOwner = 0xFF;
  static uint8_t shownOutcome = 0xFF;
  static uint8_t shownChannel = 0xFF;
  static bool shownDesired = false;
  static bool shownCancel = false;
  static bool shownHolding = false;
  static bool shownStop = false;
  static bool shownLost = false;

  const bool matching = primeSessionKnown &&
                        primeSession.sessionToken == primeSessionToken;
  const uint8_t phase = matching ? primeSession.phase : PRIME_SESSION_OFF;
  const uint8_t owner = matching ? primeSession.owner : PRIME_OWNER_NONE;
  const uint8_t outcome = matching ? primeSession.outcome : PRIME_OUTCOME_NONE;
  const bool modelChanged = force || shownPhase != phase || shownOwner != owner ||
                            shownOutcome != outcome || shownChannel != flavorSel ||
                            shownDesired != primeSessionDesired ||
                            shownCancel != primeSessionCancelPending ||
                            shownHolding != holding || shownStop != primeStopPending ||
                            shownLost != primeLinkLost;
  if (!modelChanged) return;
  shownPhase = phase;
  shownOwner = owner;
  shownOutcome = outcome;
  shownChannel = flavorSel;
  shownDesired = primeSessionDesired;
  shownCancel = primeSessionCancelPending;
  shownHolding = holding;
  shownStop = primeStopPending;
  shownLost = primeLinkLost;

  if (primeSessionCancelPending) {
    lv_label_set_text(primePadLbl, "EXITING PRIME");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_OFF), 0);
    setPrimeMsg("waiting for the controller");
  } else if (primeLinkLost) {
    lv_label_set_text(primePadLbl, "RECONNECTING");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_OFF), 0);
    setPrimeMsg("prime connection lost");
  } else if (primeStopPending) {
    lv_label_set_text(primePadLbl, "STOPPING");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_OFF), 0);
    setPrimeMsg("waiting for the controller");
  } else if (!primeSessionDesired || !matching || phase == PRIME_SESSION_OFF) {
    lv_label_set_text(primePadLbl, "CONNECTING");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_OFF), 0);
    setPrimeMsg("opening prime mode on both displays");
  } else if (phase == PRIME_SESSION_RUNNING) {
    lv_label_set_text(primePadLbl, "PRIMING");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_GOOD), 0);
    setPrimeMsg(owner == PRIME_OWNER_FAUCET ? "held at the faucet" : "pump turning");
  } else if (holding) {
    lv_label_set_text(primePadLbl, "STARTING");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_ACCENT), 0);
    setPrimeMsg("waiting for the controller");
  } else {
    lv_label_set_text(primePadLbl, "HOLD TO PRIME");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_ACCENT), 0);
    setPrimeMsg(primeOutcomeText(outcome));
  }
  // The pressed-state style has greater specificity than the default color.
  // Keep an acknowledged held run visibly green under the user's finger; a
  // blocked control remains dark instead of flashing the generic button color.
  const bool blocked = primeSessionCancelPending || primeLinkLost ||
                       primeStopPending || !primeSessionDesired || !matching ||
                       phase == PRIME_SESSION_OFF;
  lv_obj_set_style_bg_color(
      primePad,
      lv_color_hex(blocked ? COL_OFF
                   : phase == PRIME_SESSION_RUNNING ? COL_GOOD : COL_CARD_ON),
      LV_PART_MAIN | LV_STATE_PRESSED);
  primeRefreshElapsed(true);
}

static void primeSessionActivate() {
  primeBootDiscovery = false;
  primeSessionDesired = true;
  primeSessionCancelPending = false;
  primeClearStopPending();
  primeLinkLost = false;
  holding = false;
  holdAckMs = 0;
  primeHoldToken = 0;
  primeElapsedShown = 0;
  primeSessionToken = nextPrimeToken();
  primeStateMs = millis();
  primePostSession(PRIME_SESSION_ACTIVATE);
  // The accepted ACTIVATE itself makes the controller's one entry tick.
  clickPending = false;
  primeRender(true);
  Serial.printf("[J9] prime session activate ch=%u token=%08lX\n",
                flavorSel, (unsigned long)primeSessionToken);
}

static void primeSessionCancel() {
  if (primeSessionCancelPending) {
    clickPending = false;
    return;
  }
  if (!primeSessionDesired && !primeSessionCancelPending && !primeStateActive()) return;
  if (primeStateActive() &&
      (primeSessionToken == 0 ||
       primeSessionToken != primeSession.sessionToken)) {
    // If our attempted ACTIVATE lost a race with an older authoritative
    // session, EXIT means exit that real session—not retry CANCEL forever for
    // the token that never became controller truth.
    primeSessionToken = primeSession.sessionToken;
    flavorSel = primeSession.channel;
  }
  if (primeSessionToken == 0) return;

  primeSessionDesired = false;
  primeSessionCancelPending = true;
  primeClearStopPending();
  primeUsbStartPending = false;
  holding = false;
  // Give this absolute CANCEL its own response window. primeStateMs otherwise
  // describes the last READY/RUNNING heartbeat, which may already be stale.
  primeStateMs = millis();
  primePostSession(PRIME_SESSION_CANCEL);
  // The accepted CANCEL supplies this navigation press's one sound.
  clickPending = false;
  primeRender(true);
  Serial.printf("[J9] prime session cancel token=%08lX\n",
                (unsigned long)primeSessionToken);
}

static void primeHoldEnd() {
  if (!holding) return;
  holding = false;
  primeMarkStopPending();
  primePostHold(MSG_PRIME_SESSION_HOLD_STOP);
  primeRender(true);
  setPrimeMsg(holdAckMs ? "stopping" : "hold released");
  Serial.printf("[J9] prime hold stop ch=%u token=%08lX after %lu ms\n",
                flavorSel, (unsigned long)primeHoldToken, millis() - holdStartMs);
}

static void primeHoldBegin() {
  const bool ready = primeSessionDesired && !primeSessionCancelPending &&
                     primeSessionKnown &&
                     primeSession.sessionToken == primeSessionToken &&
                     primeSession.phase == PRIME_SESSION_READY;
  if (holding || primeStopPending || !ready || primeLinkLost) return;

  holding = true;
  primeClearStopPending();
  primeHoldToken = nextPrimeToken();
  holdStartMs = holdTickMs = millis();
  holdAckMs = 0;
  holdRetried = false;
  primePostHold(MSG_PRIME_SESSION_HOLD_START);
  // START owns the engage/refuse sound, including idempotent retries.
  clickPending = false;
  primeRender(true);
  Serial.printf("[J9] prime hold start ch=%u session=%08lX hold=%08lX\n",
                flavorSel, (unsigned long)primeSessionToken,
                (unsigned long)primeHoldToken);
}

static void applyPrimeSessionState(const PrimeSessionStatePayload &state) {
  if (state.phase > PRIME_SESSION_RUNNING || state.channel > PUMP_CHANNEL_B ||
      state.owner > PRIME_OWNER_FAUCET || state.outcome > PRIME_OUTCOME_LEASE_EXPIRED) return;

  // This exact tuple is the controller's power-on epoch marker. J9 is an
  // ordered, bounded single-sender link, so it is safe to accept even when a
  // surviving display has cached a numerically higher pre-reset revision.
  const bool controllerResetOff = state.phase == PRIME_SESSION_OFF &&
                                  state.owner == PRIME_OWNER_NONE &&
                                  state.revision == 0 &&
                                  state.sessionToken == 0;
  const bool cancelAnsweredOff = primeSessionCancelPending &&
                                 primeSessionToken != 0 &&
                                 state.phase == PRIME_SESSION_OFF &&
                                 state.sessionToken == primeSessionToken;
  if (primeSessionKnown) {
    // A controller reboot restarts its revision counter. The fresh session
    // token this display just chose is an epoch proof stronger than the cached
    // number: only an accepted ACTIVATE can echo it, and no queued old state can.
    const bool acceptedFreshEpoch = primeSessionDesired &&
                                    state.sessionToken == primeSessionToken &&
                                    state.sessionToken != 0 &&
                                    state.sessionToken != primeSession.sessionToken;
    const int32_t revisionDelta = (int32_t)(state.revision - primeSession.revision);
    if (revisionDelta < 0 && !acceptedFreshEpoch && !controllerResetOff &&
        !cancelAnsweredOff) {
      Serial.printf("[J9] stale prime session rev=%lu < %lu\n",
                    (unsigned long)state.revision,
                    (unsigned long)primeSession.revision);
      return;
    }
    if (revisionDelta == 0 && !acceptedFreshEpoch && !controllerResetOff &&
        !cancelAnsweredOff) {
      // A RUNNING heartbeat advances authoritative elapsed without advancing
      // the state revision. Everything else at the same revision is a no-op.
      primeStateMs = millis();
      const bool recovered = primeLinkLost;
      primeLinkLost = false;
      if (state.phase != PRIME_SESSION_RUNNING ||
          primeSession.phase != PRIME_SESSION_RUNNING ||
          state.sessionToken != primeSession.sessionToken ||
          state.holdToken != primeSession.holdToken ||
          state.owner != primeSession.owner ||
          state.elapsedMs < primeSession.elapsedMs) {
        if (recovered) primeRender(true);
        return;
      }
      primeSession.elapsedMs = state.elapsedMs;
      primeElapsedAnchorAt = millis();
      if (recovered) primeRender(true);
      return;
    }
  }

  const PrimeSessionStatePayload previous = primeSession;
  const bool wasKnown = primeSessionKnown;
  const bool wasBootDiscovery = primeBootDiscovery;
  primeSession = state;
  primeSessionKnown = true;
  primeBootDiscovery = false;
  primeStateMs = primeElapsedAnchorAt = millis();
  primeLinkLost = false;

  const bool authoritativeActive = state.phase != PRIME_SESSION_OFF &&
                                   state.sessionToken != 0;
  const bool differentToken = authoritativeActive &&
                              state.sessionToken != primeSessionToken;
  const bool retargetCancel = primeSessionCancelPending && differentToken;
  const bool adoptActive = !primeSessionCancelPending && differentToken &&
                           (wasBootDiscovery || primeSessionDesired ||
                            state.phase == PRIME_SESSION_RUNNING);
  if (retargetCancel || adoptActive) {
    // Controller truth supersedes any unsent control for the local token. In
    // particular, an old queued START must never trail a newly observed run.
    j9DiscardQueuedPrimeFeeds(true);
    holding = false;
    primeClearStopPending();
    primeUsbStartPending = false;
    primeHoldToken = 0;
    primeSessionToken = state.sessionToken;
    flavorSel = state.channel;
    if (retargetCancel) {
      primeSessionDesired = false;
      primeStateMs = millis();
      primePostSession(PRIME_SESSION_CANCEL);
    } else {
      // Only the enclosure can have created this live session. A booting panel,
      // a panel whose ACTIVATE met an existing session, or a real remote RUNNING
      // transition resumes its lease without synthesizing a physical hold.
      primeSessionDesired = true;
    }
  }

  const bool tokenMatches = state.sessionToken != 0 &&
                            state.sessionToken == primeSessionToken;

  // A reset-OFF answer can arrive after an ACTIVATE has already left outQ and
  // entered the ordered UART transport. Retain that exact local token and put
  // CANCEL behind it: the cancel closes an accepted/in-flight activation and
  // harmlessly no-ops when the activation was only queued and is purged here.
  const bool resetNeedsCancel = controllerResetOff && primeSessionToken != 0 &&
                                (primeSessionDesired || primeSessionCancelPending);
  const bool completedOff = (!resetNeedsCancel && controllerResetOff) ||
                            cancelAnsweredOff ||
                            (state.phase == PRIME_SESSION_OFF && tokenMatches);
  if (resetNeedsCancel) {
    j9DiscardQueuedPrimeFeeds(true);
    primeSessionDesired = false;
    primeSessionCancelPending = true;
    primeUsbStartPending = false;
    holding = false;
    primeClearStopPending();
    primeHoldToken = 0;
    primeStateMs = millis();
    primePostSession(PRIME_SESSION_CANCEL);
  } else if (completedOff) {
    j9DiscardQueuedPrimeFeeds(true);
    primeSessionDesired = false;
    primeSessionCancelPending = false;
    primeUsbStartPending = false;
    holding = false;
    primeClearStopPending();
    primeSessionToken = 0;
    primeHoldToken = 0;
    if (activePage == PAGE_SERVICE && activeSvc == SVC_PRIME_HOLD) {
      if (touchInput) lv_indev_wait_release(touchInput);
      primeAuthoritativeNavigation = true;
      showService(SVC_PRIME_PICK);
      primeAuthoritativeNavigation = false;
    }
  }
  if (tokenMatches && state.phase != PRIME_SESSION_OFF &&
      !primeSessionCancelPending) {
    primeSessionDesired = true;
    flavorSel = state.channel;
  }

  if (state.phase == PRIME_SESSION_RUNNING) {
    const bool ourRun = state.owner == PRIME_OWNER_FRONT && tokenMatches &&
                        state.holdToken == primeHoldToken;
    if (ourRun && holding) {
      holdAckMs = millis();
    } else if (holding) {
      // A racing hold from the other glass won. Purge the unsent local feed and
      // put its causal STOP behind anything already in flight before dropping
      // the physical press state.
      holding = false;
      primeMarkStopPending();
      primePostHold(MSG_PRIME_SESSION_HOLD_STOP);
    }

    const bool remoteStarted = !wasKnown || previous.phase != PRIME_SESSION_RUNNING ||
                               previous.sessionToken != state.sessionToken ||
                               previous.holdToken != state.holdToken;
    if (adoptActive || (remoteStarted && state.owner != PRIME_OWNER_FRONT)) {
      if (touchInput) lv_indev_wait_release(touchInput);
      primeAuthoritativeNavigation = true;
      if (activePage != PAGE_SERVICE) showPage(PAGE_SERVICE);
      if (activeSvc != SVC_PRIME_HOLD) showService(SVC_PRIME_HOLD);
      primeAuthoritativeNavigation = false;
      if (screenIdle) wake();
    }
  } else if (state.phase == PRIME_SESSION_READY) {
    if (wasKnown && previous.phase == PRIME_SESSION_RUNNING) {
      // Leave the terminal outcome readable for a normal idle interval after a
      // remote or local run instead of sleeping in the same loop it arrives.
      lastInputTime = millis();
    }
    if (holding && state.holdToken == primeHoldToken &&
        state.outcome != PRIME_OUTCOME_NONE) holding = false;
    if (state.holdToken == primeHoldToken && state.outcome != PRIME_OUTCOME_NONE)
      primeClearStopPending();
    if (tokenMatches && primeSessionDesired && activePage == PAGE_SERVICE &&
        activeSvc == SVC_PRIME_HOLD) {
      flavorSel = state.channel;
    }
    if (tokenMatches && primeUsbStartPending &&
        state.outcome == PRIME_OUTCOME_NONE) {
      primeUsbStartPending = false;
      primeHoldBegin();
    }
    if (adoptActive) {
      if (touchInput) lv_indev_wait_release(touchInput);
      primeAuthoritativeNavigation = true;
      if (activePage != PAGE_SERVICE) showPage(PAGE_SERVICE);
      if (activeSvc != SVC_PRIME_HOLD) showService(SVC_PRIME_HOLD);
      primeAuthoritativeNavigation = false;
      if (screenIdle) wake();
    }
  }

  primeElapsedShown = state.elapsedMs;
  primeRender(true);
  Serial.printf("[J9] prime session phase=%u owner=%u outcome=%u ch=%u "
                "elapsed=%lu rev=%lu session=%08lX hold=%08lX\n",
                state.phase, state.owner, state.outcome, state.channel,
                (unsigned long)state.elapsedMs, (unsigned long)state.revision,
                (unsigned long)state.sessionToken, (unsigned long)state.holdToken);
}

static void primeSessionService() {
  if (!primeLinkOwnsJ9()) return;
  const unsigned long now = millis();

  if (primeBootDiscovery && !primeSessionKnown) {
    if (now - primeControlQueuedMs >= PRIME_BOOT_SNAPSHOT_RETRY_MS)
      primePostBootSnapshotQuery();
    return;
  }

  if (primeSessionCancelPending) {
    if (now - primeStateMs >= PRIME_SESSION_STALE_MS) {
      if (!primeLinkLost) {
        primeLinkLost = true;
        lastInputTime = now;
        primeRender(true);
      }
      if (now - primeLastReinitMs >= PRIME_REINIT_BACKOFF_MS) {
        primeLastReinitMs = now;
        ++primeStaleReinits;
        j9Reinit("prime session cancel unanswered");
        primePostSession(PRIME_SESSION_CANCEL);
        return;
      }
    }
    if (now - primeControlQueuedMs >= PRIME_SESSION_RETRY_MS) {
      primePostSession(PRIME_SESSION_CANCEL);
    }
    return;
  }

  const bool matchingActive = primeSessionKnown &&
                              primeSession.phase != PRIME_SESSION_OFF &&
                              primeSession.sessionToken == primeSessionToken;
  if (!matchingActive) {
    if (now - primeStateMs >= PRIME_SESSION_STALE_MS) {
      if (!primeLinkLost) {
        primeLinkLost = true;
        lastInputTime = now;
        primeRender(true);
      }
      if (now - primeLastReinitMs >= PRIME_REINIT_BACKOFF_MS) {
        primeLastReinitMs = now;
        ++primeStaleReinits;
        j9Reinit("prime session activate unanswered");
        primePostSession(PRIME_SESSION_ACTIVATE);
        return;
      }
    }
    if (now - primeControlQueuedMs >= PRIME_SESSION_RETRY_MS) {
      primePostSession(PRIME_SESSION_ACTIVATE);
    }
    return;
  }

  if (now - primeStateMs >= PRIME_SESSION_STALE_MS) {
    if (holding) {
      holding = false;
      primeMarkStopPending();
      primePostHold(MSG_PRIME_SESSION_HOLD_STOP);
    }
    if (!primeLinkLost) {
      primeLinkLost = true;
      lastInputTime = now;
      primeRender(true);
    }
    if (now - primeLastReinitMs >= PRIME_REINIT_BACKOFF_MS) {
      primeLastReinitMs = now;
      ++primeStaleReinits;
      j9Reinit("prime session responses stale");
      if (primeStopPending) primePostHold(MSG_PRIME_SESSION_HOLD_STOP);
      else                  primePostQuery();
    }
    if (!primeStopPending) return;
  }

  if (primeStopPending) {
    const bool sameRun = primeSession.phase == PRIME_SESSION_RUNNING &&
                         primeSession.owner == PRIME_OWNER_FRONT &&
                         primeSession.holdToken == primeHoldToken;
    const bool otherRun = primeSession.phase == PRIME_SESSION_RUNNING && !sameRun;
    const bool terminalReady = primeSession.phase == PRIME_SESSION_READY &&
                               primeSession.holdToken == primeHoldToken &&
                               primeSession.outcome >= PRIME_OUTCOME_STOPPED &&
                               primeSession.outcome <= PRIME_OUTCOME_REFUSED;
    // If our exact H1 terminal reply was lost, READY/RUNNING for a later H2 in
    // the same session is still authoritative proof that H1 is no longer live.
    const bool superseded = primeStopRevisionKnown &&
                            primeStateSupersedesPendingStop(
                                primeSession, primeSessionToken, primeHoldToken,
                                PRIME_OWNER_FRONT, primeStopRevision);
    if (otherRun || terminalReady || superseded) {
      primeClearStopPending();
      primeRender(true);
    } else if (now - primeControlQueuedMs >= PRIME_TICK_MS) {
      primePostHold(MSG_PRIME_SESSION_HOLD_STOP);
    }
    return;
  }

  if (holding) {
    const bool acknowledged = primeSession.phase == PRIME_SESSION_RUNNING &&
                              primeSession.owner == PRIME_OWNER_FRONT &&
                              primeSession.holdToken == primeHoldToken;
    if (now - holdTickMs >= PRIME_TICK_MS) {
      primePostHold(acknowledged ? MSG_PRIME_SESSION_HOLD_TICK
                                 : MSG_PRIME_SESSION_HOLD_START);
      holdTickMs = now;
    }

    const unsigned long heldMs = now - holdStartMs;
    if (!acknowledged && heldMs > 700 && !holdRetried) {
      holdRetried = true;
      j9Reinit("prime session start unanswered");
      primePostHold(MSG_PRIME_SESSION_HOLD_START);
      holdTickMs = now;
      setPrimeMsg("link reset — retrying");
    }
    if (!acknowledged && heldMs > PRIME_SESSION_STALE_MS) {
      setPrimeMsg("no answer from the controller");
    }
    return;
  }

  const unsigned long pollMs = screenIdle ? PRIME_SESSION_POLL_DARK_MS
                                           : PRIME_SESSION_POLL_ACTIVE_MS;
  if (now - primeControlQueuedMs >= pollMs) primePostQuery();
}

// The pad answers the press and the lift, not the click. PRESS_LOST is the finger sliding
// off the pad, which ends the hold the same way lifting it does.
static void primePadCb(lv_event_t *e) {
  lv_event_code_t code = lv_event_get_code(e);
  if (code == LV_EVENT_PRESSED) {
    primeHoldBegin();
  } else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
    primeHoldEnd();
    if (code == LV_EVENT_PRESS_LOST) {
      // Abort this LVGL input pass after recording STOP. Without reset_query,
      // the same still-pressed sample can target the adjacent Back control.
      lv_indev_t *indev = lv_indev_get_act();
      if (indev) {
        lv_indev_wait_release(indev);
        lv_indev_reset(indev, nullptr);
      }
    }
  }
}

// ── Navigation ──
static void railCb(lv_event_t *e)     { showRail((RailPage)(intptr_t)lv_event_get_user_data(e)); }

static void flavorBackCb(lv_event_t *e) { (void)e; showPage(PAGE_HOME); }

static void homeFlavorPickCb(lv_event_t *e) {
  const uint8_t flavor = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  if (selectActiveFlavor(flavor)) {
    // MSG_FLAVOR_SELECT carries the fresh-touch audible bit. Suppress mkBtn's
    // generic click frame so this one press remains one frame on J9.
    clickPending = false;
  } else {
    // Pressing the already-selected card is still tactile feedback, but it is
    // not a state request and therefore owns one ordinary click frame.
    clickPending = false;
    sendSound(SND_WIRE_TICK);
  }
}

static void primePickCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  showService(SVC_PRIME_HOLD);
}

// Choose's per-card gear: the flavor it sits under becomes the one being
// edited, and the page it opens is that flavor's own.
static void homeSettingsCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  showPage(PAGE_FLAVOR);
  showFlavor(FLV_DETAIL);
}

static void imagePickCb(lv_event_t *e) {
  const uint8_t img = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  if (img >= FLAVOR_IMAGE_COUNT || flavorImage[flavorSel] == img) return;
  flavorImage[flavorSel] = img;
  refreshFlavorImages();
  sendFlavorArt();
}

static void cleanPickCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  showService(SVC_CLEAN_CONFIRM);
}

static void cleanStartCb(lv_event_t *e) {
  (void)e;
  ChannelPayload p{flavorSel};
  j9Post(MSG_CLEAN_START, &p, sizeof(p));
  setCleanMsg("Starting clean cycle...");
}

static void fillPickCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  showService(SVC_FILL_CONFIRM);
}

static void fillStartCb(lv_event_t *e) {
  (void)e;
  ChannelPayload p{flavorSel};
  j9Post(MSG_FILL_START, &p, sizeof(p));
  setFillMsg("Drawing from the hopper...");
}

static void ratioStepCb(lv_event_t *e) {
  int r = flavorRatio[flavorSel] + (int)(intptr_t)lv_event_get_user_data(e);
  if (r < 6)  r = 6;    // the range the base's SET:Fn_RATIO accepts
  if (r > 24) r = 24;
  flavorRatio[flavorSel] = (uint8_t)r;
  refreshFlavorText();
}

// ── Page builders ──

// A full-screen appliance lock. The animation belongs here: it communicates
// that the machine is deliberately busy while the modal names the reason. The
// object is built once and reused by boot, filling, cleaning, and any future
// operation that must withhold the rest of the UI.
static void buildLockScreen(lv_obj_t *scr) {
  lockScreen = lv_obj_create(scr);
  lv_obj_set_size(lockScreen, SCREEN_W, SCREEN_H);
  lv_obj_set_pos(lockScreen, 0, 0);
  lv_obj_set_style_bg_color(lockScreen, THEME_BG, 0);
  lv_obj_set_style_bg_opa(lockScreen, LV_OPA_COVER, 0);
  lv_obj_set_style_border_width(lockScreen, 0, 0);
  lv_obj_set_style_radius(lockScreen, 0, 0);
  lv_obj_set_style_pad_all(lockScreen, 0, 0);
  lv_obj_clear_flag(lockScreen, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_add_flag(lockScreen, LV_OBJ_FLAG_CLICKABLE);

  lockLogoImg = lv_img_create(lockScreen);
  lv_img_set_src(lockLogoImg, &frameDsc[0]);
  lv_obj_align(lockLogoImg, LV_ALIGN_LEFT_MID, 18, 0);

  lv_obj_t *modal = mkCard(lockScreen, 360, 238);
  lv_obj_align(modal, LV_ALIGN_RIGHT_MID, -26, 0);
  lv_obj_set_style_pad_left(modal, 32, 0);
  lv_obj_set_style_pad_right(modal, 28, 0);
  lv_obj_set_style_pad_top(modal, 30, 0);
  lv_obj_set_style_pad_bottom(modal, 28, 0);

  lv_obj_t *accent = lv_obj_create(modal);
  lv_obj_set_size(accent, 6, 178);
  lv_obj_align(accent, LV_ALIGN_LEFT_MID, -18, 0);
  lv_obj_set_style_bg_color(accent, lv_color_hex(COL_ACCENT), 0);
  lv_obj_set_style_border_width(accent, 0, 0);
  lv_obj_set_style_radius(accent, 3, 0);
  lv_obj_set_style_pad_all(accent, 0, 0);
  lv_obj_clear_flag(accent, LV_OBJ_FLAG_SCROLLABLE);

  lockKicker = mkText(modal, "HOME SODA MACHINE", &lv_font_montserrat_20, COL_ACCENT);
  lv_obj_align(lockKicker, LV_ALIGN_TOP_LEFT, 0, 0);
  lockTitle = mkText(modal, "Powering on", &lv_font_montserrat_40, COL_TEXT);
  lv_obj_align(lockTitle, LV_ALIGN_LEFT_MID, 0, -8);
  lockBody = mkText(modal, "Getting everything ready.", &lv_font_montserrat_20, COL_DIM);
  lv_obj_align(lockBody, LV_ALIGN_BOTTOM_LEFT, 0, 0);

  lv_obj_add_flag(lockScreen, LV_OBJ_FLAG_HIDDEN);
}

static void lockScreenShow(const char *kicker, const char *title, const char *body) {
  if (!lockScreen) return;
  lv_label_set_text(lockKicker, kicker);
  lv_label_set_text(lockTitle, title);
  lv_label_set_text(lockBody, body);
  lv_obj_clear_flag(lockScreen, LV_OBJ_FLAG_HIDDEN);
  lv_obj_move_foreground(lockScreen);
  lockActive = true;
  if (screenIdle) wake();
  animRun(true);
}

static void lockScreenHide() {
  if (!lockScreen) return;
  lv_obj_add_flag(lockScreen, LV_OBJ_FLAG_HIDDEN);
  lockActive = false;
  animRun(false);
  lastInputTime = millis();
}

static void buildRail(lv_obj_t *scr) {
  static const char *kRail[RAIL_PAGE_COUNT] = {
      "CHOOSE",
      "FILL",
      "PRIME",
      "CLEAN",
  };
  for (int i = 0; i < RAIL_PAGE_COUNT; i++) {
    lv_obj_t *b = mkBtn(scr, RAIL_W - 12, RAIL_ITEM_H, COL_CARD);
    lv_obj_set_pos(b, 6, RAIL_INSET_Y + i * (RAIL_ITEM_H + RAIL_ITEM_GAP));
    lv_obj_set_style_pad_all(b, RAIL_ITEM_PAD, 0);
    // These carry a selected colour, so a press goes straight to it. A shade in between
    // reads as a slow tween toward a colour the button is about to take anyway, rather
    // than as confirmation — the buttons with nothing to become keep mkBtn's press shade.
    lv_obj_set_style_bg_color(b, lv_color_hex(COL_ACCENT), LV_PART_MAIN | LV_STATE_PRESSED);
    lv_obj_set_style_color_filter_opa(b, LV_OPA_TRANSP, LV_PART_MAIN | LV_STATE_PRESSED);
    lv_obj_add_event_cb(b, railCb, ACT_EVENT, (void *)(intptr_t)i);
    mkRailIcon(b, (RailPage)i);
    lv_obj_align(mkText(b, kRail[i], &lv_font_montserrat_20, COL_TEXT), LV_ALIGN_BOTTOM_MID, 0, 0);
    railBtn[i] = b;
  }
}

// Settings is not a customer destination and does not earn a rail slot beside
// the five that are. It sits in the screen's top-right corner instead, on the
// root rather than in any pane, so one object serves every page. Every pane
// puts its title top-left and its content lower, which is what leaves this
// corner free; Home's synchronization label is the one thing that shares the
// band, and it is aligned to clear this square.
static void settingsCb(lv_event_t *e) { (void)e; showPage(PAGE_SETUP); }

static void buildSettingsButton(lv_obj_t *scr) {
  lv_obj_t *b = mkBtn(scr, SETTINGS_BTN, SETTINGS_BTN, COL_CARD);
  lv_obj_set_pos(b, SCREEN_W - PANE_PAD - SETTINGS_BTN, PANE_PAD);
  lv_obj_set_style_pad_all(b, 0, 0);
  lv_obj_set_style_bg_color(b, lv_color_hex(COL_ACCENT), LV_PART_MAIN | LV_STATE_PRESSED);
  lv_obj_set_style_color_filter_opa(b, LV_OPA_TRANSP, LV_PART_MAIN | LV_STATE_PRESSED);
  lv_obj_add_event_cb(b, settingsCb, ACT_EVENT, NULL);
  lv_obj_center(mkText(b, LV_SYMBOL_SETTINGS, &lv_font_montserrat_28, COL_TEXT));
  settingsBtn = b;
}

// RAIL_PAGE_COUNT means no rail destination is current — which is how Settings
// reads, since it lives in the corner rather than on the rail. The loop then
// matches nothing and the corner takes the selection instead.
static void setRailSelection(RailPage page) {
  activeRail = page;
  for (int i = 0; i < RAIL_PAGE_COUNT; i++) {
    lv_obj_set_style_bg_color(railBtn[i],
                              lv_color_hex(i == page ? COL_ACCENT : COL_CARD), 0);
  }
  if (settingsBtn) {
    lv_obj_set_style_bg_color(
        settingsBtn, lv_color_hex(page == RAIL_PAGE_COUNT ? COL_ACCENT : COL_CARD), 0);
  }
}

// The screen behind it is already THEME_BG, and a second opaque fill of the pane is
// 586 KB written to PSRAM against a bus the scan-out DMA is reading continuously.
// Under direct_mode that cost is only paid where something changed, but a pane that
// fills itself makes every change inside it dirty the whole pane.
static lv_obj_t *buildPane(lv_obj_t *scr) {
  lv_obj_t *o = lv_obj_create(scr);
  lv_obj_set_size(o, PANE_W, SCREEN_H);
  lv_obj_set_pos(o, RAIL_W, 0);
  lv_obj_set_style_bg_opa(o, LV_OPA_TRANSP, 0);
  lv_obj_set_style_border_width(o, 0, 0);
  lv_obj_set_style_radius(o, 0, 0);
  lv_obj_set_style_pad_all(o, PANE_PAD, 0);
  lv_obj_clear_flag(o, LV_OBJ_FLAG_SCROLLABLE);
  return o;
}

// The appliance's default interaction: two clear, whole-card choices. The
// flavor marks make the cards recognizable at a glance; their static image
// objects do not redraw during routine controller heartbeats.
static void buildHome(lv_obj_t *page) {
  const lv_coord_t cw = (PANE_W - 2 * PANE_PAD - 16) / 2;
  lv_obj_align(mkText(page, "CHOOSE A FLAVOR", &lv_font_montserrat_28, COL_DIM),
               LV_ALIGN_TOP_LEFT, 0, (PANE_HEAD_H - TEXT_H_28) / 2);
  homeSyncLabel = mkText(page, LV_SYMBOL_REFRESH "  CONNECTING",
                         &lv_font_montserrat_20, COL_WARN);
  // Right-aligned but held clear of the settings square, which overlaps this
  // band from the screen root and is not part of the pane's own layout.
  lv_obj_align(homeSyncLabel, LV_ALIGN_TOP_RIGHT,
               -(SETTINGS_BTN + SETTINGS_GAP - PANE_PAD),
               (PANE_HEAD_H - TEXT_H_20) / 2);

  // The card is the whole selection target, so its settings live beside it
  // rather than inside it — a sibling, where no press can reach the card under it.
  for (uint8_t i = 0; i < 2; ++i) {
    lv_obj_t *card = mkBtn(page, cw, HOME_CARD_H, COL_CARD);
    lv_obj_align(card, LV_ALIGN_TOP_LEFT, i * (cw + 16), PANE_BODY_Y);
    lv_obj_set_style_pad_all(card, 12, 0);
    lv_obj_add_event_cb(card, homeFlavorPickCb, ACT_EVENT, (void *)(intptr_t)i);

    lv_obj_t *gear = mkBtn(page, cw, HOME_GEAR_H, COL_CARD);
    lv_obj_align(gear, LV_ALIGN_BOTTOM_LEFT, i * (cw + 16), 0);
    lv_obj_add_event_cb(gear, homeSettingsCb, ACT_EVENT, (void *)(intptr_t)i);
    lv_obj_center(mkText(gear, LV_SYMBOL_SETTINGS "  SETTINGS",
                         &lv_font_montserrat_20, COL_DIM));

    lv_obj_t *art = lv_img_create(card);
    lv_img_set_src(art, &flavorArt[flavorImage[i]]);
    lv_obj_center(art);
    lv_obj_clear_flag(art, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    homeFlavorArtObj[i] = art;

    lv_obj_t *badge = lv_obj_create(card);
    // The card's own accent outline already carries the selection; this only
    // has to name it. Riding the artwork's corner keeps it out of the column,
    // which is what leaves the settings target under the card its full height.
    lv_obj_set_size(badge, HOME_BADGE_H, HOME_BADGE_H);
    lv_obj_align_to(badge, art, LV_ALIGN_TOP_RIGHT, -8, 8);
    lv_obj_set_style_border_width(badge, 0, 0);
    lv_obj_set_style_radius(badge, HOME_BADGE_H / 2, 0);
    lv_obj_set_style_pad_all(badge, 0, 0);
    lv_obj_clear_flag(badge, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_clear_flag(badge, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_t *badgeText = mkText(badge, LV_SYMBOL_OK, &lv_font_montserrat_20, COL_TEXT);
    lv_obj_center(badgeText);

    homeFlavorCard[i] = card;
    homeFlavorBadge[i] = badge;
    homeFlavorBadgeText[i] = badgeText;
  }
}

// One flavor's own page: what it pours at, and which logo it wears. Reached from
// that flavor's card on Choose, which is where Back returns to.
static void buildFlavor(lv_obj_t *page) {
  lv_obj_t *det = mkView(page);
  mkBack(det, flavorBackCb, NULL);
  lv_obj_align(mkSelectedImg(det, flavorHead), LV_ALIGN_TOP_MID, 0,
               (PANE_HEAD_H - FLAVOR_HEAD_SIZE) / 2);

  lv_obj_t *row = mkCard(det, PANE_W - 2 * PANE_PAD, RATIO_CARD_H);
  lv_obj_align(row, LV_ALIGN_TOP_MID, 0, PANE_BODY_Y);
  lv_obj_align(mkText(row, "RATIO", &lv_font_montserrat_20, COL_DIM), LV_ALIGN_TOP_LEFT, 0, 0);
  lv_obj_t *minus = mkBtn(row, 84, 72, COL_CARD_ON);
  lv_obj_align(minus, LV_ALIGN_BOTTOM_LEFT, 0, 0);
  lv_obj_add_event_cb(minus, ratioStepCb, ACT_EVENT, (void *)(intptr_t)-1);
  lv_obj_center(mkText(minus, LV_SYMBOL_MINUS, &lv_font_montserrat_28, COL_TEXT));
  lv_obj_t *plus = mkBtn(row, 84, 72, COL_CARD_ON);
  lv_obj_align(plus, LV_ALIGN_BOTTOM_RIGHT, 0, 0);
  lv_obj_add_event_cb(plus, ratioStepCb, ACT_EVENT, (void *)(intptr_t)1);
  lv_obj_center(mkText(plus, LV_SYMBOL_PLUS, &lv_font_montserrat_28, COL_TEXT));
  flvDetailRatio = mkText(row, "1:12", &lv_font_montserrat_48, COL_TEXT);
  lv_obj_align(flvDetailRatio, LV_ALIGN_BOTTOM_MID, 0, -12);

  lv_obj_align(mkText(det, "IMAGE", &lv_font_montserrat_20, COL_DIM),
               LV_ALIGN_TOP_LEFT, 0, IMAGE_LABEL_Y);

  // A wrapping row of logos, two rows deep before it scrolls. Positions are set
  // here rather than by a layout, the way every other surface on this panel is.
  lv_obj_t *grid = lv_obj_create(det);
  lv_obj_set_size(grid, PANE_W - 2 * PANE_PAD, PANE_H - THUMB_GRID_Y);
  lv_obj_align(grid, LV_ALIGN_TOP_MID, 0, THUMB_GRID_Y);
  lv_obj_set_style_bg_opa(grid, LV_OPA_TRANSP, 0);
  lv_obj_set_style_border_width(grid, 0, 0);
  lv_obj_set_style_pad_all(grid, 0, 0);
  lv_obj_set_scroll_dir(grid, LV_DIR_VER);
  lv_obj_set_scrollbar_mode(grid, LV_SCROLLBAR_MODE_AUTO);

  const lv_coord_t rowW = THUMB_PER_ROW * THUMB_BTN + (THUMB_PER_ROW - 1) * THUMB_GAP;
  const lv_coord_t x0 = (PANE_W - 2 * PANE_PAD - rowW) / 2;
  for (int i = 0; i < FLAVOR_IMAGE_COUNT; i++) {
    lv_obj_t *t = mkBtn(grid, THUMB_BTN, THUMB_BTN, COL_CARD);
    lv_obj_set_pos(t, x0 + (i % THUMB_PER_ROW) * (THUMB_BTN + THUMB_GAP),
                      (i / THUMB_PER_ROW) * (THUMB_BTN + THUMB_GAP));
    lv_obj_set_style_pad_all(t, 4, 0);
    lv_obj_add_event_cb(t, imagePickCb, ACT_EVENT, (void *)(intptr_t)i);
    lv_obj_t *img = lv_img_create(t);
    lv_img_set_src(img, &flavorThumb[i]);
    lv_obj_center(img);
    lv_obj_clear_flag(img, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    flvThumbBtn[i] = t;
  }

  flvView[FLV_DETAIL] = det;
}

// Two flavor targets, side by side, under a title. A channel is named by the
// logo it wears — the same artwork Choose shows, at the same size — over the
// mark for what this screen is about to do to it.
static void buildFlavorPicker(lv_obj_t *view, const char *title,
                              const char *icon, const lv_font_t *iconFont,
                              lv_event_cb_t cb) {
  const lv_coord_t cw = (PANE_W - 2 * PANE_PAD - 16) / 2;
  const lv_coord_t ch = PANE_H - PANE_BODY_Y;
  const lv_coord_t top = (ch - (48 + 16 + FLAVOR_ART_SIZE)) / 2;
  lv_obj_align(mkText(view, title, &lv_font_montserrat_28, COL_DIM),
               LV_ALIGN_TOP_LEFT, 0, (PANE_HEAD_H - TEXT_H_28) / 2);
  for (int i = 0; i < 2; i++) {
    lv_obj_t *b = mkBtn(view, cw, ch, COL_CARD);
    lv_obj_align(b, LV_ALIGN_TOP_LEFT, i * (cw + 16), PANE_BODY_Y);
    lv_obj_add_event_cb(b, cb, ACT_EVENT, (void *)(intptr_t)i);
    lv_obj_align(mkText(b, icon, iconFont, COL_ACCENT), LV_ALIGN_TOP_MID, 0, top);
    lv_obj_align(mkChannelImg(b, (uint8_t)i, flavorArt),
                 LV_ALIGN_TOP_MID, 0, top + 48 + 16);
  }
}

// A named flavor, what the machine is about to do to it, and one wide target to
// say go. Fill and Clean are the same shape: both commit an open-ended manifold
// operation the controller sequences, so both ask once, plainly, before sending.
// The word for what is about to happen, and the logo of the channel it happens
// to — the same mark that was tapped to get here, carried forward so the screen
// never has to be read to know which one is committed.
static void mkFlavorHead(lv_obj_t *v, const char *word) {
  lv_obj_t *w = mkText(v, word, &lv_font_montserrat_28, COL_DIM);
  lv_obj_align(w, LV_ALIGN_TOP_LEFT, 0, (PANE_HEAD_H - TEXT_H_28) / 2);
  lv_obj_t *img = mkSelectedImg(v, flavorHead);
  lv_obj_align_to(img, w, LV_ALIGN_OUT_RIGHT_MID, 16, 0);
}

static lv_obj_t *buildConfirm(lv_obj_t *page, const char *word, const char *body,
                              const char *action, lv_event_cb_t cb,
                              lv_obj_t **msgOut) {
  const lv_coord_t fw = PANE_W - 2 * PANE_PAD;
  lv_obj_t *v = mkView(page);
  lv_obj_align(mkText(v, word, &lv_font_montserrat_28, COL_DIM),
               LV_ALIGN_TOP_LEFT, 0, (PANE_HEAD_H - TEXT_H_28) / 2);

  lv_obj_align(mkSelectedImg(v, flavorMid), LV_ALIGN_TOP_MID, 0, PANE_BODY_Y);

  lv_obj_t *b = mkText(v, body, &lv_font_montserrat_20, COL_DIM);
  lv_obj_set_style_text_align(b, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_align(b, LV_ALIGN_TOP_MID, 0, PANE_BODY_Y + FLAVOR_MID_SIZE + 16);

  lv_obj_t *go = mkBtn(v, fw, 96, COL_ACCENT);
  lv_obj_align(go, LV_ALIGN_TOP_MID, 0,
               PANE_BODY_Y + FLAVOR_MID_SIZE + 16 + 2 * TEXT_H_20 + 32);
  lv_obj_clear_flag(go, LV_OBJ_FLAG_PRESS_LOCK);   // slide off to change your mind
  lv_obj_add_event_cb(go, cb, LV_EVENT_CLICKED, NULL);
  lv_obj_center(mkText(go, action, &lv_font_montserrat_28, COL_TEXT));

  *msgOut = mkText(v, "", &lv_font_montserrat_20, COL_WARN);
  lv_obj_align(*msgOut, LV_ALIGN_BOTTOM_MID, 0, 0);
  return v;
}

static void buildService(lv_obj_t *page) {
  const lv_coord_t fw = PANE_W - 2 * PANE_PAD;

  lv_obj_t *pick = mkView(page);
  buildFlavorPicker(pick, "PRIME A FLAVOR", "\xEF\x81\x83", &front_icons_48,
                    primePickCb);
  svcView[SVC_PRIME_PICK] = pick;

  // The hold pad. It fills the pane because it is meant to be found without looking.
  lv_obj_t *hold = mkView(page);
  mkFlavorHead(hold, "PRIME");

  primePad = mkBtn(hold, fw, 200, COL_ACCENT);
  lv_obj_align(primePad, LV_ALIGN_TOP_MID, 0, PANE_BODY_Y);
  // A slide out of the large hold target is a lost press and must stop the
  // pump just like a lift; ordinary navigation buttons keep PRESS_LOCK.
  lv_obj_clear_flag(primePad, LV_OBJ_FLAG_PRESS_LOCK);
  lv_obj_add_event_cb(primePad, primePadCb, LV_EVENT_ALL, NULL);
  primePadLbl = mkText(primePad, "HOLD TO PRIME", &lv_font_montserrat_48, COL_TEXT);
  lv_obj_center(primePadLbl);

  primeElapsed = mkText(hold, "0.0 s", &lv_font_montserrat_48, COL_TEXT);
  lv_obj_align(primeElapsed, LV_ALIGN_TOP_MID, 0, PANE_BODY_Y + 218);

  primeBar = lv_bar_create(hold);
  lv_obj_set_size(primeBar, fw, 18);
  lv_obj_align(primeBar, LV_ALIGN_TOP_MID, 0, PANE_BODY_Y + 290);
  lv_bar_set_range(primeBar, 0, (int32_t)PRIME_MAX_MS);
  lv_bar_set_value(primeBar, 0, LV_ANIM_OFF);
  lv_obj_set_style_bg_color(primeBar, lv_color_hex(COL_CARD), LV_PART_MAIN);
  lv_obj_set_style_bg_color(primeBar, lv_color_hex(COL_ACCENT), LV_PART_INDICATOR);

  primeMsg = mkText(hold, "idle", &lv_font_montserrat_20, COL_DIM);
  lv_obj_align(primeMsg, LV_ALIGN_BOTTOM_MID, 0, 0);
  svcView[SVC_PRIME_HOLD] = hold;

  lv_obj_t *cpick = mkView(page);
  buildFlavorPicker(cpick, "CLEAN A FLAVOR", "\xEE\x81\xAD", &front_icons_48,
                    cleanPickCb);
  svcView[SVC_CLEAN_PICK] = cpick;

  svcView[SVC_CLEAN_CONFIRM] = buildConfirm(
      page, "CLEAN", "Three rounds: fill the line with water,\n"
                     "then pump it through to the nozzle.",
      "START CLEAN CYCLE", cleanStartCb, &cleanMsg);

  lv_obj_t *fpick = mkView(page);
  buildFlavorPicker(fpick, "FILL A FLAVOR", "\xEF\x82\xB0", &front_icons_48,
                    fillPickCb);
  svcView[SVC_FILL_PICK] = fpick;

  svcView[SVC_FILL_CONFIRM] = buildConfirm(
      page, "FILL", "Pour concentrate into the funnel on top,\n"
                    "then this draws it down to the reservoir.",
      "START FILL", fillStartCb, &fillMsg);
}

static void buildSettings(lv_obj_t *page) {
  lv_obj_align(mkText(page, "SETTINGS", &lv_font_montserrat_28, COL_DIM),
               LV_ALIGN_TOP_LEFT, 0, (PANE_HEAD_H - TEXT_H_28) / 2);

  // Customer controls earn their place here when there is a clear reason to
  // change them. Keep the first shipping settings surface deliberately quiet
  // instead of exposing build, transport, memory, or touch diagnostics.
  lv_obj_t *card = mkCard(page, PANE_W - 2 * PANE_PAD, 156);
  lv_obj_align(card, LV_ALIGN_TOP_MID, 0, PANE_BODY_Y);
  lv_obj_align(mkText(card, "NOTHING TO ADJUST YET", &lv_font_montserrat_20, COL_DIM),
               LV_ALIGN_TOP_LEFT, 0, 0);
  lv_obj_t *body = mkText(card, "Useful preferences will appear here\nwhen they are ready.",
                           &lv_font_montserrat_28, COL_TEXT);
  lv_obj_align(body, LV_ALIGN_LEFT_MID, 0, 28);
}

// GPIO43 reads RS485_RXD on Waveshare's table and is the S3's U0TXD. The pair is a
// variable and this exchanges it; the base answering is what settles which way it runs.
static void rs485Swap() {
  int t = rs485Rx; rs485Rx = rs485Tx; rs485Tx = t;
  j9.end();
  Serial1.end();
  j9Begin();
}

// ── Page switching ──

static void animRun(bool on) {
  if (!animTimer) return;
  const bool wakeQuiet = kickStage ||
                         (animResumeDue && (long)(millis() - animResumeDue) < 0);
  if (on && !wakeQuiet) lv_timer_resume(animTimer);
  else lv_timer_pause(animTimer);
}

static void showFlavor(FlavorView v) {
  activeFlv = v;
  showOnly(flvView, FLV_COUNT, v);
  refreshFlavorText();
  refreshFlavorImages();
}

static void showService(ServiceView v) {
  const ServiceView previous = activeSvc;
  if (previous == SVC_PRIME_HOLD && v != SVC_PRIME_HOLD &&
      !primeAuthoritativeNavigation) {
    primeSessionCancel();
  }
  activeSvc = v;
  if (v == SVC_PRIME_PICK || v == SVC_PRIME_HOLD) setRailSelection(RAIL_PRIME);
  if (v == SVC_CLEAN_PICK || v == SVC_CLEAN_CONFIRM) setRailSelection(RAIL_CLEAN);
  if (v == SVC_FILL_PICK  || v == SVC_FILL_CONFIRM)  setRailSelection(RAIL_FILL);
  showOnly(svcView, SVC_COUNT, v);
  if (v == SVC_PRIME_HOLD) {
    if (previous != SVC_PRIME_HOLD && !primeAuthoritativeNavigation) {
      primeSessionActivate();
    }
    primeRender(true);
  } else if (v == SVC_CLEAN_CONFIRM) {
    setCleanMsg("");
  } else if (v == SVC_FILL_CONFIRM) {
    setFillMsg("");
  }
}

// Where a service flow rests when it is sent back to its start: the pick page of
// whichever rail destination the user is standing on.
static ServiceView pickViewForRail() {
  switch (activeRail) {
    case RAIL_FILL:  return SVC_FILL_PICK;
    case RAIL_CLEAN: return SVC_CLEAN_PICK;
    default:         return SVC_PRIME_PICK;
  }
}

// The rungs the dark climbs. Done while the screen is off, so a wake shows the answer
// rather than jumping to it under the user's eyes.
static void idleReset(uint8_t stage) {
  if (!uiReady) return;
  if (stage == 2) {
    if (activePage == PAGE_SERVICE) {
      if (activeSvc == SVC_PRIME_HOLD) {
        // This is unattended housekeeping, not a glass press. Stop renewing
        // the session and let the controller's short lease close it silently;
        // sending CANCEL here would make the sleeping appliance tick.
        primeSessionDesired = false;
        primeSessionCancelPending = false;
        primeUsbStartPending = false;
        holding = false;
        primeClearStopPending();
        j9DiscardQueuedPrimeFeeds(true);
        primeSessionToken = 0;
        primeHoldToken = 0;
        primeAuthoritativeNavigation = true;
        showService(pickViewForRail());
        primeAuthoritativeNavigation = false;
      } else {
        showService(pickViewForRail());
      }
    }
    else if (activePage == PAGE_FLAVOR) showPage(PAGE_HOME);
  } else if (stage == 3) {
    showPage(PAGE_HOME);
  }
}

static RailPage railForPage(Page p) {
  switch (p) {
    case PAGE_HOME:    return RAIL_CHOOSE;
    case PAGE_FLAVOR:  return RAIL_CHOOSE;
    case PAGE_SERVICE: return RAIL_PRIME;
    case PAGE_SETUP:   return RAIL_PAGE_COUNT;   // the corner, not the rail
    default:           return RAIL_CHOOSE;
  }
}

static void showPage(Page p) {
  if (activePage == PAGE_SERVICE && activeSvc == SVC_PRIME_HOLD &&
      !primeAuthoritativeNavigation) {
    primeSessionCancel();
  }
  showOnly(pageObj, PAGE_COUNT, p);
  activePage = p;
  setRailSelection(railForPage(p));
  // The animation belongs only to the full-screen operation lock. Ordinary
  // pages invalidate only when their cached visible state actually changes.
  animRun(lockActive && !screenIdle);
  if (p == PAGE_HOME)    refreshHomeSelection();
  if (p == PAGE_FLAVOR)  showFlavor(FLV_DETAIL);
  if (p == PAGE_SERVICE) showService(SVC_PRIME_PICK);
}

static void showRail(RailPage p) {
  switch (p) {
    case RAIL_CHOOSE:
      showPage(PAGE_HOME);
      break;
    case RAIL_FILL:
      showPage(PAGE_SERVICE);
      showService(SVC_FILL_PICK);
      break;
    case RAIL_PRIME:
      showPage(PAGE_SERVICE);
      showService(SVC_PRIME_PICK);
      break;
    case RAIL_CLEAN:
      showPage(PAGE_SERVICE);
      showService(SVC_CLEAN_PICK);
      break;
    default:
      showPage(PAGE_HOME);
      break;
  }
}

static void buildUi() {
  for (uint8_t i = 0; i < NUM_ANIM_FRAMES; i++) {
    frameDsc[i].header.cf = LV_IMG_CF_TRUE_COLOR;
    frameDsc[i].header.always_zero = 0;
    frameDsc[i].header.w = LOGO_SIZE;
    frameDsc[i].header.h = LOGO_SIZE;
    frameDsc[i].data_size = LOGO_SIZE * LOGO_SIZE * sizeof(uint16_t);
    frameDsc[i].data = (const uint8_t *)animFrames[i];
  }
  for (uint8_t i = 0; i < FLAVOR_IMAGE_COUNT; ++i) {
    flavorArt[i].header.cf = LV_IMG_CF_TRUE_COLOR;
    flavorArt[i].header.always_zero = 0;
    flavorArt[i].header.w = FLAVOR_ART_SIZE;
    flavorArt[i].header.h = FLAVOR_ART_SIZE;
    flavorArt[i].data_size = FLAVOR_ART_SIZE * FLAVOR_ART_SIZE * sizeof(uint16_t);
    flavorArt[i].data = (const uint8_t *)flavorArtPixels[i];

    flavorThumb[i].header.cf = LV_IMG_CF_TRUE_COLOR;
    flavorThumb[i].header.always_zero = 0;
    flavorThumb[i].header.w = FLAVOR_THUMB_SIZE;
    flavorThumb[i].header.h = FLAVOR_THUMB_SIZE;
    flavorThumb[i].data_size = FLAVOR_THUMB_SIZE * FLAVOR_THUMB_SIZE * sizeof(uint16_t);
    flavorThumb[i].data = (const uint8_t *)flavorThumbPixels[i];

    flavorHead[i].header.cf = LV_IMG_CF_TRUE_COLOR;
    flavorHead[i].header.always_zero = 0;
    flavorHead[i].header.w = FLAVOR_HEAD_SIZE;
    flavorHead[i].header.h = FLAVOR_HEAD_SIZE;
    flavorHead[i].data_size = FLAVOR_HEAD_SIZE * FLAVOR_HEAD_SIZE * sizeof(uint16_t);
    flavorHead[i].data = (const uint8_t *)flavorHeadPixels[i];

    flavorMid[i].header.cf = LV_IMG_CF_TRUE_COLOR;
    flavorMid[i].header.always_zero = 0;
    flavorMid[i].header.w = FLAVOR_MID_SIZE;
    flavorMid[i].header.h = FLAVOR_MID_SIZE;
    flavorMid[i].data_size = FLAVOR_MID_SIZE * FLAVOR_MID_SIZE * sizeof(uint16_t);
    flavorMid[i].data = (const uint8_t *)flavorMidPixels[i];
  }
  lv_obj_t *scr = lv_scr_act();
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);
  lv_obj_clear_flag(scr, LV_OBJ_FLAG_SCROLLABLE);

  buildRail(scr);
  for (int i = 0; i < PAGE_COUNT; i++) pageObj[i] = buildPane(scr);
  buildHome(pageObj[PAGE_HOME]);
  buildFlavor(pageObj[PAGE_FLAVOR]);
  buildService(pageObj[PAGE_SERVICE]);
  buildSettings(pageObj[PAGE_SETUP]);
  // After the panes so it draws above them, before the lock so that still covers it.
  buildSettingsButton(scr);
  buildLockScreen(scr);

  uiReady = true;
  refreshFlavorText();
  refreshHomeSelection();
  showPage(PAGE_HOME);
  lockScreenShow("HOME SODA MACHINE", "Powering on", "Getting everything ready.");
}

// ════════════════════════════════════════════════════════════
//  USB serial text commands (bring-up / diagnostics)
// ════════════════════════════════════════════════════════════

static void processTextLine(const char *line) {
  if (strcmp(line, "GET_VERSION") == 0) {
    Serial.printf("VERSION:FRONT=%s\n", FW_VERSION);
  } else if (strcmp(line, "GET_STATE") == 0) {
    Serial.printf("STATE:FLAVOR=%u,SYNC=%d,PERSISTED=%d,PERSISTERR=%d,PENDING=%d,LOCK=%d,IDLE=%d,PAGE=%d,PRIME=%u,PRIMECH=%u,OWNER=%u\n",
                  (unsigned)activeFlavor,
                  flavorSynchronized ? 1 : 0,
                  flavorControllerPersisted ? 1 : 0,
                  flavorControllerPersistError ? 1 : 0,
                  flavorRequestPending ? 1 : 0,
                  lockActive ? 1 : 0,
                  screenIdle ? 1 : 0,
                  (int)activeRail,
                  primeSessionKnown ? (unsigned)primeSession.phase : 0,
                  primeSessionKnown ? (unsigned)primeSession.channel : 0,
                  primeSessionKnown ? (unsigned)primeSession.owner : 0);
  } else if (strcmp(line, "GET_DIAG") == 0) {
    // HWCDC has a finite packet buffer. Keep the primary health record below
    // one packet so a host can never mistake a partial line for a complete
    // response; the less frequently used detail follows on bounded lines.
    Serial.printf("DIAG:page=%d,svc=%d,flv=%d,lock=%d,stage=%u,idle=%d,holding=%d,"
                  "gt911=0x%02X,reinits=%lu,sendErr=%d,outQ=%u/%u,outDrop=%lu,"
                  "link=%s,ctrlRx=%lu,ctrlTurnMax=%u,ctrlTurnOver=%lu,"
                  "flushes=%lu,maxLoopMs=%lu,heap=%lu,minHeap=%lu\n",
                  (int)activeRail, (int)activeSvc, (int)activeFlv,
                  lockActive ? 1 : 0, (unsigned)idleStage, screenIdle ? 1 : 0,
                  holding ? 1 : 0, gt911Addr, (unsigned long)linkReinits,
                  lastSendErr, (unsigned)outCount, (unsigned)outHighWater,
                  (unsigned long)outDropped, j9.framesRx ? "rx" : "silent",
                  (unsigned long)ctrlStatus.framesRx,
                  (unsigned)ctrlStatus.j9ReplyHighWater,
                  (unsigned long)ctrlStatus.j9ReplyOverruns,
                  (unsigned long)flushCount, (unsigned long)maxLoopMs,
                  (unsigned long)ESP.getFreeHeap(), (unsigned long)ESP.getMinFreeHeap());
    Serial.printf("DIAG_UI:selected=%u,flavorSync=%d,flavorSaved=%d,flavorPending=%d,flavorRetries=%lu,"
                  "flavorStale=%lu,bridged=%lu,stale=%lu,touch=%lu,lastXY=%u/%u\n",
                  (unsigned)activeFlavor, flavorSynchronized ? 1 : 0,
                  flavorControllerPersisted ? 1 : 0, flavorRequestPending ? 1 : 0,
                  (unsigned long)flavorRetries, (unsigned long)flavorStaleResponses,
                  (unsigned long)touchBridged, (unsigned long)gt911Stale,
                  (unsigned long)touchCount, (unsigned)lastTouchX, (unsigned)lastTouchY);
    Serial.printf("DIAG_SYS:unanswered=%u,psram=%lu,freePsram=%lu,bl=%d,frame=%u,uptime=%lus\n",
                  (unsigned)unanswered, (unsigned long)ESP.getPsramSize(),
                  (unsigned long)ESP.getFreePsram(), backlightOn ? 1 : 0,
                  (unsigned)animFrameIdx, millis() / 1000);
    Serial.printf("DIAG_PRIME:known=%d,desired=%d,cancel=%d,stop=%d,lost=%d,phase=%u,owner=%u,outcome=%u,"
                  "session=%08lX,hold=%08lX,revision=%lu,elapsed=%lu,stateAgeMs=%lu,staleReinits=%lu\n",
                  primeSessionKnown ? 1 : 0, primeSessionDesired ? 1 : 0,
                  primeSessionCancelPending ? 1 : 0,
                  primeStopPending ? 1 : 0,
                  primeLinkLost ? 1 : 0,
                  primeSessionKnown ? (unsigned)primeSession.phase : 0,
                  primeSessionKnown ? (unsigned)primeSession.owner : 0,
                  primeSessionKnown ? (unsigned)primeSession.outcome : 0,
                  (unsigned long)primeSessionToken, (unsigned long)primeHoldToken,
                  primeSessionKnown ? (unsigned long)primeSession.revision : 0,
                  primeSessionKnown ? (unsigned long)primeDisplayedElapsed() : 0,
                  primeStateMs ? (unsigned long)(millis() - primeStateMs) : 0,
                  (unsigned long)primeStaleReinits);
    maxLoopMs = 0;  // high-water mark since last query
  } else if (strcmp(line, "GET_PANEL") == 0) {
    Serial.printf("PANEL:vsync=%lu,frameDone=%lu,flushes=%lu,drawErr=%lu,frameTimeout=%lu,"
                  "kickStart=%lu,kickDone=%lu,kickStage=%u,kickTimeout=%lu,"
                  "phaseQ=%lu,phaseDone=%lu,phaseRetry=%lu,phaseLate=%lu,phaseErr=%lu,"
                  "scanRecover=%lu,exioErr=%lu,bl=%d\n",
                  (unsigned long)vsyncCount, (unsigned long)frameDoneCount,
                  (unsigned long)flushCount,
                  (unsigned long)panelDrawErrors, (unsigned long)frameDoneTimeouts,
                  (unsigned long)kickStarted, (unsigned long)kickCompleted,
                  (unsigned)kickStage, (unsigned long)kickFrameTimeouts,
                  (unsigned long)panelVsyncActionsQueued,
                  (unsigned long)panelVsyncActionsDone,
                  (unsigned long)panelVsyncBusRetries,
                  (unsigned long)panelVsyncLateRetries,
                  (unsigned long)panelVsyncWriteErrors,
                  (unsigned long)home_soda_rgb_restart_count(),
                  (unsigned long)exioWriteErrors, backlightOn ? 1 : 0);
  } else if (strncmp(line, "FLAVOR:", 7) == 0) {
    if ((line[7] != '0' && line[7] != '1') || line[8] != '\0') {
      Serial.println("ERR:FLAVOR expects 0 or 1");
    } else {
      const uint8_t flavor = (uint8_t)(line[7] - '0');
      selectActiveFlavor(flavor);
      Serial.printf("OK:FLAVOR=%u\n", (unsigned)activeFlavor);
    }
  } else if (strncmp(line, "EDIT:", 5) == 0) {
    // A flavor's own page, and the artwork it wears, without a finger on the
    // glass: the same handlers the gear and a thumbnail tap reach.
    int f = atoi(line + 5);
    const char *comma = strchr(line + 5, ',');
    if (f != 1 && f != 2) {
      Serial.println("ERR:EDIT expects 1 or 2, optionally ,<image 0..3>");
    } else {
      flavorSel = (uint8_t)(f - 1);
      showPage(PAGE_FLAVOR);
      showFlavor(FLV_DETAIL);
      if (comma) {
        int img = atoi(comma + 1);
        if (img < 0 || img >= FLAVOR_IMAGE_COUNT) {
          Serial.printf("ERR:EDIT image expects 0..%d\n", FLAVOR_IMAGE_COUNT - 1);
          return;
        }
        flavorImage[flavorSel] = (uint8_t)img;
        refreshFlavorImages();
        sendFlavorArt();
      }
      Serial.printf("OK:EDIT=%d,img=%u\n", f, flavorImage[flavorSel]);
    }
  } else if (strcmp(line, "LOCK:SHOW") == 0) {
    bootLockActive = false;
    lockScreenShow("HOME SODA MACHINE", "Powering on", "Getting everything ready.");
    Serial.println("OK:LOCK=1");
  } else if (strcmp(line, "LOCK:HIDE") == 0) {
    bootLockActive = false;
    lockScreenHide();
    Serial.println("OK:LOCK=0");
  } else if (strncmp(line, "BL:", 3) == 0) {
    if (line[3] != '0' && line[3] != '1') {
      Serial.println("ERR:BL expects 0 or 1");
    } else {
      setBacklight(line[3] == '1');
      Serial.printf("OK:BL=%d\n", backlightOn ? 1 : 0);
    }
  } else if (strncmp(line, "IDLE:", 5) == 0) {
    // Walk the idle ladder without waiting it out. 0 wakes; 1 goes dark; 2 and 3 take the
    // rungs the dark would have taken at KEEP_VIEW_MS and KEEP_AREA_MS.
    char s = line[5];
    if (s == '0') {
      wake();
      Serial.println("OK:IDLE=0");
    } else if (s >= '1' && s <= '3') {
      screenIdle = true;
      idleStage = (uint8_t)(s - '0');
      darkSince = millis();
      setBacklight(false);
      if (animTimer) lv_timer_pause(animTimer);
      if (idleStage >= 2) idleReset(2);
      if (idleStage >= 3) idleReset(3);
      Serial.printf("OK:IDLE=%c page=%d\n", s, (int)activeRail);
    } else {
      Serial.println("ERR:IDLE expects 0..3");
    }
  } else if (strcmp(line, "PUMP") == 0) {
    sendPumpRun(PUMP_CHANNEL_B, 1000);
    Serial.println("OK:PUMP");
  } else if (strncmp(line, "PAGE:", 5) == 0) {
    // 0..3 are the rail, in rail order. Settings left the rail for the corner
    // and keeps a number here anyway, so a bring-up script can still reach it.
    int p = atoi(line + 5);
    if (p == RAIL_PAGE_COUNT) { showPage(PAGE_SETUP); Serial.printf("OK:PAGE=%d\n", p); }
    else if (p < 0 || p > RAIL_PAGE_COUNT) Serial.println("ERR:PAGE expects 0..4");
    else { showRail((RailPage)p); Serial.printf("OK:PAGE=%d\n", p); }
  } else if (strncmp(line, "CLICK:", 6) == 0) {
    if (line[6] != '0' && line[6] != '1') Serial.println("ERR:CLICK expects 0 or 1");
    else { clickSend = (line[6] == '1'); Serial.printf("OK:CLICK=%d\n", clickSend ? 1 : 0); }
  } else if (strncmp(line, "SOUND:", 6) == 0) {
    // The click's whole path, without a finger on the glass. This panel has no
    // sounder, so anything heard after this is the frame having crossed J9 and
    // reached U8 on the controller — which is the one direction a touch travels,
    // and the one a line test cannot otherwise exercise without an operator.
    int id = atoi(line + 6);
    if (id < 1 || id > SND_WIRE_ALARM) Serial.printf("ERR:SOUND expects 1..%d\n", SND_WIRE_ALARM);
    else { sendSound((uint8_t)id); Serial.printf("OK:SOUND=%d\n", id); }
  } else if (strncmp(line, "PRIME:START:", 12) == 0) {
    // Enter the shared session, then start the same tokenized hold as soon as
    // the controller's READY answer lands. PRIME:STOP releases that synthetic
    // hold; PRIME:EXIT closes the ready session on both displays.
    int f = atoi(line + 12);
    if (f != 1 && f != 2) { Serial.println("ERR:PRIME:START expects 1 or 2"); }
    else {
      flavorSel = (uint8_t)(f - 1);
      showRail(RAIL_PRIME);
      showService(SVC_PRIME_HOLD);
      primeUsbStartPending = true;
      Serial.printf("OK:PRIME:START=%d\n", f);
    }
  } else if (strcmp(line, "PRIME:STOP") == 0) {
    primeUsbStartPending = false;
    primeHoldEnd();
    Serial.println("OK:PRIME:STOP");
  } else if (strcmp(line, "PRIME:EXIT") == 0) {
    primeSessionCancel();
    Serial.println("OK:PRIME:EXIT");
  } else if (strcmp(line, "PANEL:REALIGN") == 0) {
    panelRealign();
    Serial.println("OK:PANEL:REALIGN");
  } else if (strcmp(line, "PANEL:KICK") == 0) {
    panelKick();                  // the wake sequence, without waiting for a sleep
    Serial.println("OK:PANEL:KICK");
  } else if (strcmp(line, "STATUS") == 0) {
    j9Post(MSG_STATUS_REQ, nullptr, 0);
    Serial.println("OK:STATUS requested");
  } else if (strcmp(line, "LINK") == 0) {
    Serial.printf("LINK:rx=GPIO%d,tx=GPIO%d,framesRx=%lu,framesTx=%lu,%s\n", rs485Rx, rs485Tx,
                  (unsigned long)j9.framesRx, (unsigned long)j9.framesTx,
                  j9.framesRx ? "frames seen" : "nothing received yet");
  } else if (strcmp(line, "RS485:RAW") == 0) {
    // Below HDLC: whatever the UART hands over for 4 s, printed as it arrives.
    Serial.println("RAW:listening 4s");
    unsigned long t0 = millis();
    uint32_t n = 0;
    while (millis() - t0 < 4000) {
      while (Serial1.available()) { Serial.printf(" %02X", Serial1.read()); n++; }
      delay(2);
    }
    Serial.printf("\nRAW:%lu byte(s)\n", (unsigned long)n);
  } else if (strcmp(line, "RS485:REINIT") == 0) {
    // GPIO43/44 are U0TXD/U0RXD and carry whatever the bootloader left on the pads.
    // Hand them back to the GPIO matrix before UART1 claims them again.
    j9.end();
    Serial1.end();
    gpio_reset_pin((gpio_num_t)rs485Rx);
    gpio_reset_pin((gpio_num_t)rs485Tx);
    j9Begin();
    Serial.println("OK:REINIT");
  } else if (strcmp(line, "RS485:LOOP") == 0) {
    // The transceiver receives while it drives, so a line sent here returns on this
    // board's own RX. Nothing is swallowed and nothing need be attached to the pair.
    while (Serial1.available()) Serial1.read();
    static const char *probe = "LOOPTEST";
    Serial1.write((const uint8_t *)probe, strlen(probe));
    Serial1.write('\n');
    Serial1.flush();
    char got[32];
    uint8_t n = 0;
    unsigned long t0 = millis();
    while (millis() - t0 < 200 && n < sizeof(got) - 1) {
      if (Serial1.available()) {
        char c = Serial1.read();
        if (c == '\n' || c == '\r') break;
        got[n++] = c;
      }
    }
    got[n] = '\0';
    Serial.printf("OK:LOOP rx=GPIO%d tx=GPIO%d got='%s' %s\n", rs485Rx, rs485Tx, got,
                  strcmp(got, probe) == 0 ? "closes" : "no echo");
  } else if (strcmp(line, "RS485:SWAP") == 0) {
    rs485Swap();
    Serial.printf("OK:RS485 rx=GPIO%d tx=GPIO%d\n", rs485Rx, rs485Tx);
  } else if (strncmp(line, "RS485:", 6) == 0) {
    int r = 0; j9Post(MSG_TEXT, line + 6, (uint8_t)strlen(line + 6));
    Serial.printf("OK:sendText('%s')=%d\n", line + 6, r);
  } else {
    Serial.printf("ERR:unknown command '%s'\n", line);
  }
}

// ════════════════════════════════════════════════════════════
//  Setup / loop
// ════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  // Never block on USB writes: the native-USB CDC TX buffer only drains while
  // a host is reading. 0 = drop instead of stalling the loop.
  Serial.setTxTimeoutMs(0);
  delay(500);
  Serial.println("ESP32-S3 Front-Face Display starting...");

  esp_reset_reason_t reason = esp_reset_reason();
  Serial.printf("Boot — firmware %s, heap=%lu, psram=%lu, reset=%d\n",
                FW_VERSION, (unsigned long)ESP.getFreeHeap(),
                (unsigned long)ESP.getPsramSize(), (int)reason);


  // Expander + panel/touch resets, then the RGB panel itself — initialized on a
  // separate task with a timeout. If esp_lcd ever blocks, setup() still returns
  // and loop() keeps serial alive (board stays flashable, no BOOT-button dance).
  j9Begin();

  i2cMutex = xSemaphoreCreateMutex();
  if (!i2cMutex) {
    Serial.println("I2C mutex allocation failed — panel wake falls back to timeout recovery");
  }
  ch422gBringUp();
  if (i2cMutex &&
      xTaskCreatePinnedToCore(panelVsyncTask, "panelvsync", 4096, nullptr, 6,
                              &panelVsyncTaskHandle, 1) != pdPASS) {
    panelVsyncTaskHandle = nullptr;
    Serial.println("panel VSYNC task allocation failed — panel wake falls back to timeout recovery");
  }
  xTaskCreatePinnedToCore(panelInitTask, "panelinit", 8192, nullptr, 5, nullptr, 1);
  unsigned long initStart = millis();
  while (!panelInitDone && millis() - initStart < 6000) delay(50);
  if (!panelInitDone) {
    Serial.println("panelInit TIMED OUT — panel disabled, serial still responsive");
    return;
  }
  if (!panelInitOk) {
    Serial.println("panelInit FAILED — panel disabled, serial still responsive");
    return;
  }
  Serial.println("panelInit OK (double FB + bounce buffer)");

  // LVGL — the two draw buffers ARE the two panel framebuffers, so the flush is a
  // page flip and copies nothing. No separate buffer allocated.
  lv_init();
  lv_disp_draw_buf_init(&draw_buf, fb0, fb1, (uint32_t)SCREEN_W * SCREEN_H);

  static lv_disp_drv_t disp_drv;
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = SCREEN_W;
  disp_drv.ver_res = SCREEN_H;
  disp_drv.flush_cb = lvglFlush;
  disp_drv.draw_buf = &draw_buf;
  // direct_mode, not full_refresh. Both draw at absolute coordinates into a
  // screen-sized buffer, and the difference is the clip: full_refresh clips to
  // the whole display and so repaints all 800x480 — 768 KB into PSRAM — however
  // little changed, which on this panel is ~90 ms of the ~115 ms loop. A prime
  // hold ticking its elapsed label once per 100 ms was paying that in full for a
  // few hundred pixels of text. direct_mode clips to the invalidated area, so
  // the cost tracks what actually moved.
  //
  // With two buffers that needs the pair kept consistent, since a frame renders
  // into whichever one is off-screen and the other still holds the frame before
  // it. LVGL does that itself here — it records each frame's invalid areas and
  // copies them across in refr_sync_areas() before drawing the next — but only
  // because both buf1 and buf2 are set. A single-buffer direct_mode would tear.
  disp_drv.direct_mode = 1;
  lv_disp_drv_register(&disp_drv);

  // Touch — GT911 on the shared I2C bus (reset already released via CH422G
  // EXIO1). Probe its address, then register an LVGL pointer indev.
  pinMode(TOUCH_INT, INPUT);
  gt911Addr = gt911Probe();
  Serial.printf("GT911 %s (addr 0x%02X)\n", gt911Addr ? "found" : "NOT FOUND", gt911Addr);
  static lv_indev_drv_t indev_drv;
  lv_indev_drv_init(&indev_drv);
  indev_drv.type = LV_INDEV_TYPE_POINTER;
  indev_drv.read_cb = touchpadRead;
  touchInput = lv_indev_drv_register(&indev_drv);

  buildUi();

  // Render the first frame, then assert DISP/backlight in a vertical blank.
  lv_timer_handler();
  if (!panelQueueVsyncAction(PANEL_VSYNC_ENABLE_DISPLAY)) setBacklight(true);

  // Start the lock-screen animation (~10 fps). The boot lock stays visible for
  // two complete cycles and, when J9 is healthy, opens on authoritative flavor
  // state rather than a guessed selection.
  animTimer = lv_timer_create(animTimerCb, ANIM_FRAME_MS, NULL);
  bootLockActive = true;
  bootLockMinUntil = millis() + BOOT_LOCK_MIN_MS;
  bootLockMaxUntil = millis() + BOOT_LOCK_MAX_MS;
  flavorTokenState = esp_random();
  if (flavorTokenState == 0) flavorTokenState = 1;
  primeTokenState = esp_random();
  if (primeTokenState == 0) primeTokenState = 1;

  lastInputTime = millis();
  displayReady = true;
  Serial.println("Ready — boot lock running; Choose is the synchronized flavor selector.");
}

void loop() {
  unsigned long loopStart = millis();

  // USB serial commands (bring-up / diagnostics)
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

  // A press that spoke for itself needs no click frame: the controller ticks on
  // the command it received. Only a press that said nothing else sends one, and
  // it goes out here rather than from inside the LVGL callback, so one press can
  // never put two frames on the pair back to back.
  if (clickPending) {
    clickPending = false;
    if (j9.framesTx == framesTxAtPress) sendSound(SND_WIRE_TICK);
  }

  primeSessionService();
  flavorLinkService();
  j9Pump();      // at most one frame on the wire at a time
  j9.service();

  if (usbReattachPending && (long)(millis() - usbReattachAt) >= 0) {
    // 500 ms is long beside USB's detach debounce and short beside this panel's
    // normal startup. The timer wake is a reset, so nothing below returns.
    setBacklight(false);
    esp_sleep_enable_timer_wakeup(500000);
    esp_deep_sleep_start();
  }

  // Keep the panel dark through reset and complete scan-outs. Both LCD_RST and
  // EXIO2/DISP are changed by panelVsyncTask() in a vertical blank; the loop only
  // advances the non-blocking state machine after those writes have completed.
  if (kickStage) {
    unsigned long now = millis();
    if (kickStage == 1 && (long)(now - kickAt) >= 0) {
      if (panelSetDarkAndReset()) {
        kickVsyncBase = vsyncCount;
        kickFrameBase = frameDoneCount;
        kickAt = now + WAKE_RESET_LOW_MS;
        kickDeadline = now + WAKE_FRAME_WAIT_MS;
        kickStage = 2;
      } else kickAt = now + 10;
    } else if (kickStage == 2 && (long)(now - kickAt) >= 0) {
      const bool timedOut = (long)(now - kickDeadline) >= 0;
      if (!kickResetQueued && !timedOut) {
        kickResetQueued = panelQueueVsyncAction(PANEL_VSYNC_RELEASE_RESET);
      }
      if (kickResetQueued && panelVsyncActionFinished()) {
        panelKickEnterRecovery(now);
      } else if (timedOut) {
        if (!kickTimedOut) {
          kickFrameTimeouts++;
          kickTimedOut = true;
        }
        // Preserve a responsive display if the RGB clock itself has stopped.
        // This is deliberately the last-resort path; a working panel takes the
        // queued action at VSYNC above.
        panelCancelVsyncAction();
        kickResetQueued = false;
        if (panelReleaseResetNow()) {
          panelKickEnterRecovery(now);
        } else kickAt = now + 10;
      }
    } else if (kickStage == 3) {
      const bool recoveredForMinimum = (long)(now - kickAt) >= 0;
      const bool crossedCleanFrames =
          (uint32_t)(vsyncCount - kickVsyncBase) >= WAKE_FRAME_COUNT &&
          (uint32_t)(frameDoneCount - kickFrameBase) >= WAKE_FRAME_COUNT;
      const bool timedOut = (long)(now - kickDeadline) >= 0;
      if ((recoveredForMinimum && crossedCleanFrames) || timedOut) {
        if (timedOut && !crossedCleanFrames && !kickTimedOut) {
          kickFrameTimeouts++;
          kickTimedOut = true;
        }
        if (!kickDisplayQueued && !timedOut) {
          kickDisplayQueued = panelQueueVsyncAction(PANEL_VSYNC_ENABLE_DISPLAY);
        }
        if (kickDisplayQueued && panelVsyncActionFinished()) {
          panelKickComplete(now);
        } else if (timedOut) {
          panelCancelVsyncAction();
          kickDisplayQueued = false;
          if (setBacklight(true)) panelKickComplete(now);
          else kickAt = now + 10;
        }
      }
    }
  }

  if (animResumeDue && millis() >= animResumeDue) {
    animResumeDue = 0;
    animRun(lockActive);
  }

  if (bootLockActive) {
    const unsigned long now = millis();
    if ((long)(now - bootLockMinUntil) >= 0 &&
        (flavorSynchronized || (long)(now - bootLockMaxUntil) >= 0)) {
      bootLockActive = false;
      lockScreenHide();
    }
  }

  // RUNNING elapsed is anchored to the controller's heartbeat and smoothed
  // locally between answers. Only the small readout and bar move at 10 Hz.
  if (primeSessionKnown && primeSessionToken != 0 &&
      primeSession.sessionToken == primeSessionToken &&
      primeSession.phase == PRIME_SESSION_RUNNING &&
      activePage == PAGE_SERVICE && activeSvc == SVC_PRIME_HOLD &&
      millis() - primeLastUiMs >= 100) {
    primeLastUiMs = millis();
    primeRefreshElapsed();
  }

  // The status request keeps controller truth fresh once a second whenever a
  // shared prime hold does not own the pair. Three unanswered turns recover the
  // transport before the next customer action depends on it.
  if (uiReady && !screenIdle && !primeLinkOwnsJ9()) {
    // The controller no longer speaks unprompted — a prime that timed out or a
    // pump that finished waits for a frame to answer. This poll is what collects
    // those, so it is the ceiling on how stale news from the base can be. A poll
    // pair is ~50 bytes; at 115200 that is 1% of the pair at this interval.
    if (millis() - statusAskedMs >= 1000) {
      statusAskedMs = millis();
      if (unanswered >= 3) j9Reinit("3 status polls unanswered");
      else                 unanswered++;
      j9Post(MSG_STATUS_REQ, nullptr, 0);
    }
  }

  // Choose's cached refresh does no LVGL work while the controller's selection
  // and persistence state are unchanged; this timer lets a stale link cross
  // the two-second threshold without a standing diagnostic on the glass.
  if (uiReady && !screenIdle) {
    static unsigned long lastSlow = 0;
    if (millis() - lastSlow >= 1000) {
      lastSlow = millis();
      padWatch();
      if (activePage == PAGE_HOME)   refreshHomeSelection();
    }
  }

  // Idle: after inactivity, turn the backlight off. An active operation lock is
  // exempt; a touch wakes an ordinary page — see wake().
  const bool primeRunning = primeSessionKnown && !primeLinkLost &&
                            primeSession.phase == PRIME_SESSION_RUNNING;
  if (displayReady && !screenIdle && !holding && !primeRunning && !lockActive &&
      millis() - lastInputTime >= IDLE_TIMEOUT_MS) {
    screenIdle = true;
    idleStage = 1;
    darkSince = millis();
    setBacklight(false);
    if (animTimer) lv_timer_pause(animTimer);
  }

  if (screenIdle) {
    unsigned long dark = millis() - darkSince;
    if (idleStage < 2 && dark >= KEEP_VIEW_MS) { idleStage = 2; idleReset(2); }
    if (idleStage < 3 && dark >= KEEP_AREA_MS) { idleStage = 3; idleReset(3); }
  }

  if (displayReady) lv_timer_handler();

  // Again, on the far side of the render. lv_timer_handler() is the long pole in
  // this loop — a touch is dispatched inside it, and a frame posted from there
  // would otherwise wait out the rest of the pass before the top of the next one
  // ever looked at the queue. Servicing here as well halves that wait, and costs
  // nothing when the queue is empty.
  j9Pump();
  j9.service();

  unsigned long loopMs = millis() - loopStart;
  if (loopMs > maxLoopMs) maxLoopMs = loopMs;

  delay(5);
}
