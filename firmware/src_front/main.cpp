#include <Arduino.h>
#include <esp_system.h>
#include <esp_heap_caps.h>
#include <Wire.h>
#include <lvgl.h>
#include "esp_lcd_panel_rgb.h"
#include "esp_lcd_panel_ops.h"
#include "freertos/semphr.h"
#include "fw_version.h"
#include "proto_link.h"
#include <driver/gpio.h>
#include "soc/gpio_reg.h"
#include "soc/io_mux_reg.h"

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

static const uint16_t *animFrames[] = {
    anim_00, anim_01, anim_02, anim_03, anim_04, anim_05, anim_06, anim_07,
    anim_08, anim_09, anim_10, anim_11, anim_12, anim_13, anim_14, anim_15,
};
#define NUM_ANIM_FRAMES  16
#define ANIM_FRAME_MS    100   // ~10 fps, matches the config display
#define LOGO_SIZE        360

// ════════════════════════════════════════════════════════════
//  ESP32-S3 Front-Face Display — foundation
// ════════════════════════════════════════════════════════════
//
// Waveshare ESP32-S3-Touch-LCD-4.3B: 800x480 IPS RGB parallel panel,
// GT911 capacitive touch, CH422G I/O expander, ESP32-S3-WROOM-1-N16R8
// (16 MB flash / 8 MB octal PSRAM). Mounts in the appliance front face,
// angled up toward a standing user.
//
// The screen is a rail of five icons down the left edge and a pane to their right. The
// pane changes shape with the page: a picture and two numbers, a split of two cards, a
// grid, a scrolling column. Service → Prime → a flavor → hold the pad, and the pump on
// the base board turns for as long as the finger stays down.

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
// GPIO43 and GPIO44 are U0TXD and U0RXD, so the ROM and the 2nd-stage bootloader print
// on this bus at every reset.
//
// Waveshare's table reads GPIO43 RS485_RXD, GPIO44 RS485_TXD. `RS485:SWAP` exchanges
// the two and reports which way round it is now running.
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
static uint8_t exioState = 0;

// ── RGB panel (esp_lcd, double framebuffer) ──
// The panel has no controller of its own — the ESP32-S3 streams pixels from a
// PSRAM framebuffer by DMA. With a single framebuffer, writing it (the
// animation) while the DMA scans it starves the DMA FIFO and shears the image.
// Two framebuffers fix this structurally: LVGL renders the back buffer while
// the panel scans the front, and esp_lcd flips them at the vertical blank, so
// the DMA never reads a buffer being written. We drive esp_lcd directly because
// Arduino_GFX's RGB display hardcodes a single framebuffer.
static esp_lcd_panel_handle_t panel = nullptr;
static SemaphoreHandle_t vsyncSem = nullptr;
static void *fb0 = nullptr, *fb1 = nullptr;

// ── LVGL display buffer ──
// In full-refresh double-buffer mode LVGL's two draw buffers ARE the two panel
// framebuffers (zero-copy: flush submits the just-drawn one and the panel flips
// to it), so no separate draw buffer is allocated.
static lv_disp_draw_buf_t draw_buf;

// ── Shell geometry ──
// The rail holds five 82 px targets with a link indicator in its foot; the pane takes the
// remaining 76% of the width.
#define RAIL_W    190
#define RAIL_ITEM_H 82
#define PANE_W    (SCREEN_W - RAIL_W)
#define PANE_PAD  16

// ── Pages ──
// Every page is built once and lives for the life of the firmware; switching hides one and
// shows another. Sub-views inside a page work the same way.
enum Page { PAGE_HOME, PAGE_FLAVOR, PAGE_SERVICE, PAGE_STATUS, PAGE_SETUP, PAGE_COUNT };

enum FlavorView  { FLV_BOTH, FLV_DETAIL, FLV_COUNT };
enum ServiceView { SVC_MENU, SVC_PRIME_PICK, SVC_PRIME_HOLD,
                   SVC_CLEAN_PICK, SVC_CLEAN_CONFIRM, SVC_COUNT };

static lv_obj_t *pageObj[PAGE_COUNT];
static lv_obj_t *railBtn[PAGE_COUNT];
static lv_obj_t *flvView[FLV_COUNT];
static lv_obj_t *svcView[SVC_COUNT];
static Page activePage = PAGE_HOME;
static bool uiReady = false;

static void showPage(Page p);
static void showFlavor(FlavorView v);
static void showService(ServiceView v);
static void animRun(bool on);
static void idleReset(uint8_t stage);

// ── UI objects ──
static lv_obj_t *logoImg;
static lv_img_dsc_t frameDsc[NUM_ANIM_FRAMES];
static lv_timer_t *animTimer = nullptr;
static uint8_t animFrameIdx = 0;

static lv_obj_t *linkDot;          // rail foot — J9 heard from, or not
static lv_obj_t *homeFlavorLine;   // HOME's two ratios
static lv_obj_t *flvCardLbl[2];    // the two FLAVOR cards' ratio text
static lv_obj_t *flvDetailName, *flvDetailRatio;
static lv_obj_t *primeTitle, *primePad, *primePadLbl, *primeElapsed, *primeBar, *primeMsg;
static lv_obj_t *cleanTitle, *cleanMsg;
static lv_obj_t *statUptime, *statHeap, *statGas, *statGasBar, *statFrames, *statFoot;
static lv_obj_t *setupCtrlVer, *setupTouch, *setupLinkPins, *setupFrames, *setupReinits;
static lv_obj_t *setupTouchCnt, *setupHeap, *setupPsram, *setupLoop, *setupUptime;
static lv_obj_t *setupCol, *setupUp, *setupDown, *setupTrack, *setupThumb;
static lv_obj_t *setupUpLbl, *setupDownLbl;

// Flavor 1 and 2 as this panel holds them. The base carries no config store, so a ratio
// changed here is this display's own until one sends it somewhere.
static uint8_t flavorRatio[2] = {20, 20};
static uint8_t flavorSel = PUMP_CHANNEL_B;   // which flavor the detail and hold pages act on
static const char *kFlavorName[2] = {"FLAVOR 1", "FLAVOR 2"};

// ── Idle backlight-off (the faucet's idle behavior, adapted to this board) ──
// The backlight is a digital line on the CH422G (on/off only — no PWM), so the
// idle state is simply the backlight off and the animation paused. The first
// touch turns it back on and resumes. Instant off / instant on.
// Three timers, and the last two run from the moment the screen goes dark so that changing
// how long it stays lit does not move them.
//
// Someone who stepped away for the flavor bottle comes back to the pad they were holding.
// Someone back after a few minutes comes back to the area they were working in, without
// the view inside it that would have acted on a tap — a confirm, a hold pad, a stepper.
// Someone back much later arrives at HOME, because by then they may not be the same person.
#define IDLE_TIMEOUT_MS   90000   // touch -> dark
#define KEEP_VIEW_MS     120000   // dark -> the root of the page you were on
#define KEEP_AREA_MS     600000   // dark -> HOME

static unsigned long lastInputTime = 0;
static unsigned long darkSince = 0;
static uint8_t idleStage = 0;    // 0 lit · 1 dark · 2 at the page's root · 3 home
static bool screenIdle = false;  // true while asleep (backlight off via idle)

// ── Touch (GT911) ──
static uint8_t gt911Addr = 0;     // probed at init (0 = not found)
static uint32_t touchCount = 0;   // diagnostics: presses seen since last GET_DIAG
static uint16_t lastTouchX = 0, lastTouchY = 0;  // where the last press landed
static uint8_t lastRaw[8] = {0};                 // the GT911's own bytes for that press
static uint8_t lastStatus = 0;

// ── Diagnostics (read via GET_DIAG) ──
static uint32_t maxLoopMs = 0;
static bool backlightOn = false;
static bool displayReady = false;  // false if the panel failed to init

// ════════════════════════════════════════════════════════════
//  CH422G expander
// ════════════════════════════════════════════════════════════

static void ch422gWrite(uint8_t addr, uint8_t val) {
  Wire.beginTransmission(addr);  // addr is the 7-bit "register"/command address
  Wire.write(val);               // single data byte, no register pointer
  Wire.endTransmission();
}

static void exioApply() { ch422gWrite(CH422G_WR_IO, exioState); }

static void setBacklight(bool on) {
  if (on) exioState |= EXIO_BL; else exioState &= ~EXIO_BL;
  exioApply();
  backlightOn = on;
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

// Fires when a framebuffer flip completes (VSYNC). Kept trivial and flash-
// resident on purpose: CONFIG_LCD_RGB_ISR_IRAM_SAFE is off in this core, so
// the only safe ISR work is signalling — no LVGL calls, no IRAM_ATTR.
static bool onVsync(esp_lcd_panel_handle_t p,
                                   const esp_lcd_rgb_panel_event_data_t *e, void *ctx) {
  BaseType_t hp = pdFALSE;
  xSemaphoreGiveFromISR(vsyncSem, &hp);
  return hp == pdTRUE;
}

// Returns false (never hangs/aborts) on any failure, so a panel problem leaves
// the board responsive on serial rather than wedged.
static bool panelInit() {
  vsyncSem = xSemaphoreCreateBinary();
  if (!vsyncSem) return false;

  esp_lcd_rgb_panel_config_t cfg = {};
  cfg.clk_src = LCD_CLK_SRC_DEFAULT;
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
  // the refill work costs 1.3 fps on HOME and 28 ms on SETUP's repaint, and a frame
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
  esp_lcd_rgb_panel_register_event_callbacks(panel, &cbs, nullptr);

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
  const uint8_t addrs[2] = {GT911_ADDR_A, GT911_ADDR_B};
  for (int i = 0; i < 2; i++) {
    Wire.beginTransmission(addrs[i]);
    if (Wire.endTransmission() == 0) return addrs[i];
  }
  return 0;
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
  uint8_t status;
  if (!gt911ReadBytes(GT911_REG_STATUS, &status, 1)) { gt911Stale++; return heldDown; }
  if (!(status & 0x80))                              { gt911Stale++; return heldDown; }

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
  return heldDown;
}

// When the scan-out DMA cannot keep up with the panel, it does not recover its place: the
// whole image sits shifted right and down by however far it fell behind, and stays there.
// esp_lcd_rgb_panel_restart() sets a flag the driver acts on at the next VSYNC, which puts
// the DMA back at the top of the frame. Derek saw the shift twice on waking, so a wake asks
// for one — and again once the animation has been running a moment, which is where the
// PSRAM write burst that starves it actually lands.
static unsigned long panelRestartDue = 0;

static void panelRealign() {
  if (panel) esp_lcd_rgb_panel_restart(panel);
}

// Turn the backlight back on (instant) and put the panel back on HOME. Always resets the
// idle timer. A tap calls this — "tap to bring the backlight back on."
static void wake() {
  lastInputTime = millis();
  if (screenIdle || !backlightOn) {
    screenIdle = false;
    idleStage = 0;
    setBacklight(true);
    panelRealign();
    panelRestartDue = millis() + 800;
    // Whatever the dark decided to keep or throw away is already on screen — waking shows
    // it rather than moving to it.
    if (uiReady) animRun(activePage == PAGE_HOME);
    else if (animTimer) lv_timer_resume(animTimer);
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
#define TOUCH_RELEASE_MS 150

static uint32_t touchBridged = 0;   // polls carried across a dropped report

// The live point goes to LVGL, so a drag is still a drag. Which objects hold a press that
// slides off them is LV_OBJ_FLAG_PRESS_LOCK's job, per object — see mkBtn().
static void touchpadRead(lv_indev_drv_t *drv, lv_indev_data_t *data) {
  static bool prevTouch = false;
  static unsigned long lastDownMs = 0;
  static uint32_t bridgedRun = 0;
  uint16_t x = 0, y = 0;
  bool now = gt911ReadTouch(&x, &y);

  if (now) {
    lastDownMs = millis();
    if (!prevTouch && bridgedRun == 0) {
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
  } else if (lastDownMs && millis() - lastDownMs < TOUCH_RELEASE_MS) {
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
      Serial.printf("[touch] up  (%lu poll(s) bridged, %lu stale)\n",
                    (unsigned long)bridgedRun, (unsigned long)gt911Stale);
      lastDownMs = 0;
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

// full_refresh mode: color_p is the whole back framebuffer LVGL just rendered.
// Submit it (the panel flips to it at VSYNC), then wait for that flip before
// releasing LVGL, so it never starts drawing the buffer still being scanned.
// The 100 ms timeout (not portMAX) means a missed VSYNC degrades, never deadlocks.
static void lvglFlush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
  esp_lcd_panel_draw_bitmap(panel, 0, 0, SCREEN_W, SCREEN_H, color_p);
  xSemaphoreTake(vsyncSem, 0);                      // drop a stale token
  xSemaphoreTake(vsyncSem, pdMS_TO_TICKS(100));     // wait for the flip
  lv_disp_flush_ready(disp);
}

// ════════════════════════════════════════════════════════════
//  UI
// ════════════════════════════════════════════════════════════

static void animTimerCb(lv_timer_t *t) {
  (void)t;
  animFrameIdx = (animFrameIdx + 1) % NUM_ANIM_FRAMES;
  lv_img_set_src(logoImg, &frameDsc[animFrameIdx]);
}

// ════════════════════════════════════════════════════════════
//  RS485 link to the base ESP32
// ════════════════════════════════════════════════════════════

// The transport is the one the appliance already runs between boards: TinyProto Fd over
// the UART, typed frames through ProtoLink. This board's transceiver gates its receiver
// off while driving, so nothing it sends returns and there is no echo to cancel here —
// the base's U7 keeps receiving and cancels its own, a layer below its ProtoLink.
static HdlcLink j9;

// The base's last StatusPayload, and when it landed. Nothing else on this board knows the
// controller's uptime or its build.
static StatusPayload ctrlStatus = {};
static unsigned long ctrlStatusMs = 0;
static unsigned long statusAskedMs = 0;

static uint32_t linkReinits = 0;
static uint8_t  unanswered = 0;      // status polls sent since a frame last arrived
static uint32_t padMux[2] = {0, 0}, padOut[2] = {0, 0};

// A prime hold: the finger is down on the pad and ticks are going out under it. holdAckMs
// stays 0 until MSG_RESP_PRIME{RUNNING} lands, which is the difference between a motor
// turning and a frame sent into a bus with nothing on it.
static bool holding = false;
static unsigned long holdStartMs = 0, holdTickMs = 0, holdAckMs = 0;

static void setPrimeMsg(const char *s);
static void setCleanMsg(const char *s);
static void refreshStatusPage();
static void refreshLinkDot();

static void j9OnMessage(HdlcLink *link, const uint8_t *frame, uint16_t len) {
  (void)link;
  uint8_t type = msgType(frame);
  const uint8_t *payload = msgPayload(frame);
  uint16_t plen = msgPayloadLen(len);
  char buf[64];

  unanswered = 0;   // anything arriving says the far end is still hearing us

  if (type == MSG_RESP_PUMP_DONE && plen >= sizeof(ResponsePayload)) {
    Serial.printf("[J9] MSG_RESP_PUMP_DONE ch=%u\n", payload[0]);
    return;
  }

  if (type == MSG_RESP_PRIME && plen >= sizeof(PrimeStatePayload)) {
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
    refreshStatusPage();
    refreshLinkDot();
    return;
  }

  if (type == MSG_ERR_UNSUPPORTED) {
    setCleanMsg("this controller drives no valves");
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
  // GPIO43 is U0TXD and the bootloader leaves UART0 holding the pad, driving it. UART1
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
  int r = j9.send(MSG_PUMP_RUN, &req, sizeof(req));
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
// START CLEAN CYCLE and RESTART DISPLAY — give it back, so sliding off those still cancels.
static lv_obj_t *mkBtn(lv_obj_t *parent, lv_coord_t w, lv_coord_t h, uint32_t bg) {
  lv_obj_t *b = lv_btn_create(parent);
  lv_obj_set_size(b, w, h);
  lv_obj_set_style_radius(b, 14, 0);
  lv_obj_set_style_shadow_width(b, 0, 0);
  lv_obj_set_style_bg_color(b, lv_color_hex(bg), 0);
  lv_obj_set_style_bg_color(b, lv_color_hex(COL_CARD_ON), LV_PART_MAIN | LV_STATE_PRESSED);
  lv_obj_add_flag(b, LV_OBJ_FLAG_PRESS_LOCK);
  return b;
}

// A card-sized target with an icon over a word.
static lv_obj_t *mkTapCard(lv_obj_t *parent, lv_coord_t w, lv_coord_t h,
                           const char *icon, const char *label,
                           lv_event_cb_t cb, void *user) {
  lv_obj_t *b = mkBtn(parent, w, h, COL_CARD);
  lv_obj_add_event_cb(b, cb, LV_EVENT_CLICKED, user);
  lv_obj_t *ic = mkText(b, icon, &lv_font_montserrat_48, COL_ACCENT);
  lv_obj_align(ic, LV_ALIGN_CENTER, 0, -34);
  lv_obj_t *lb = mkText(b, label, &lv_font_montserrat_28, COL_TEXT);
  lv_obj_align(lb, LV_ALIGN_CENTER, 0, 26);
  return b;
}

static lv_obj_t *mkBack(lv_obj_t *parent, lv_event_cb_t cb, void *user) {
  lv_obj_t *b = mkBtn(parent, 150, 58, COL_CARD);
  lv_obj_align(b, LV_ALIGN_TOP_LEFT, 0, 0);
  lv_obj_add_event_cb(b, cb, LV_EVENT_CLICKED, user);
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

static void refreshLinkDot() {
  static int shown = -1;
  if (!linkDot) return;
  int ok = (j9.framesRx > 0 && millis() - j9.lastRxMs < 30000) ? 1 : 0;
  if (ok == shown) return;
  shown = ok;
  lv_label_set_text(linkDot, ok ? LV_SYMBOL_OK "  J9" : LV_SYMBOL_WARNING "  J9");
  lv_obj_set_style_text_color(linkDot, lv_color_hex(ok ? COL_GOOD : COL_WARN), 0);
}

static void refreshFlavorText() {
  char a[16], b[16];
  snprintf(a, sizeof(a), "1:%u", flavorRatio[0]);
  snprintf(b, sizeof(b), "1:%u", flavorRatio[1]);
  if (flvCardLbl[0]) lv_label_set_text(flvCardLbl[0], a);
  if (flvCardLbl[1]) lv_label_set_text(flvCardLbl[1], b);
  if (homeFlavorLine) {
    char line[64];
    snprintf(line, sizeof(line), "FLAVOR 1  %s        FLAVOR 2  %s", a, b);
    lv_label_set_text(homeFlavorLine, line);
  }
  if (flvDetailName)  lv_label_set_text(flvDetailName, kFlavorName[flavorSel]);
  if (flvDetailRatio) lv_label_set_text(flvDetailRatio, flavorSel ? b : a);
}

// SETUP is read-outs, so it is repainted from here rather than from the widgets.
static void refreshSetupPage() {
  if (!setupFrames) return;
  char b[40];
  snprintf(b, sizeof(b), "%d / %d", rs485Rx, rs485Tx);
  lv_label_set_text(setupLinkPins, b);
  snprintf(b, sizeof(b), "%lu / %lu", (unsigned long)j9.framesRx, (unsigned long)j9.framesTx);
  lv_label_set_text(setupFrames, b);
  snprintf(b, sizeof(b), "%lu", (unsigned long)linkReinits);
  lv_label_set_text(setupReinits, b);
  snprintf(b, sizeof(b), "%lu / %lu", (unsigned long)touchBridged, (unsigned long)gt911Stale);
  lv_label_set_text(setupTouchCnt, b);
  snprintf(b, sizeof(b), "%u / %u", lastTouchX, lastTouchY);
  lv_label_set_text(setupTouch, b);
  snprintf(b, sizeof(b), "%lu K", (unsigned long)ESP.getFreeHeap() / 1024);
  lv_label_set_text(setupHeap, b);
  snprintf(b, sizeof(b), "%lu K", (unsigned long)ESP.getFreePsram() / 1024);
  lv_label_set_text(setupPsram, b);
  snprintf(b, sizeof(b), "%lu ms", (unsigned long)maxLoopMs);
  lv_label_set_text(setupLoop, b);
  unsigned long up = millis() / 1000;
  snprintf(b, sizeof(b), "%lu:%02lu", up / 60, up % 60);
  lv_label_set_text(setupUptime, b);
  lv_label_set_text(setupCtrlVer, ctrlStatusMs ? ctrlStatus.version : "--");
}

static void refreshStatusPage() {
  if (!statUptime) return;
  char buf[48];
  unsigned long up = ctrlStatus.uptimeS;
  if (up < 3600) snprintf(buf, sizeof(buf), "%lu:%02lu", up / 60, up % 60);
  else           snprintf(buf, sizeof(buf), "%luh %lum", up / 3600, (up % 3600) / 60);
  lv_label_set_text(statUptime, buf);

  snprintf(buf, sizeof(buf), "%lu K", (unsigned long)ctrlStatus.freeHeap / 1024);
  lv_label_set_text(statHeap, buf);

  snprintf(buf, sizeof(buf), "%u mV", ctrlStatus.gasMv);
  lv_label_set_text(statGas, buf);
  lv_bar_set_value(statGasBar, ctrlStatus.gasMv, LV_ANIM_OFF);

  snprintf(buf, sizeof(buf), "%lu / %lu", (unsigned long)ctrlStatus.framesRx,
           (unsigned long)ctrlStatus.framesTx);
  lv_label_set_text(statFrames, buf);

  if (ctrlStatusMs == 0) {
    lv_label_set_text(statFoot, "controller has not answered");
    lv_obj_set_style_text_color(statFoot, lv_color_hex(COL_WARN), 0);
  } else {
    snprintf(buf, sizeof(buf), "build %s   ·   read %lu s ago", ctrlStatus.version,
             (millis() - ctrlStatusMs) / 1000);
    lv_label_set_text(statFoot, buf);
    lv_obj_set_style_text_color(statFoot, lv_color_hex(COL_DIM), 0);
  }
  if (setupCtrlVer) lv_label_set_text(setupCtrlVer, ctrlStatusMs ? ctrlStatus.version : "--");
}

// ── Prime — the hold, and the ticks under it ──
static int lastSendErr = 0;

static void primeSend(uint8_t type) {
  ChannelPayload p{flavorSel};
  int r = j9.send(type, &p, sizeof(p));
  if (r < 0) {
    lastSendErr = r;
    Serial.printf("[J9] send(type 0x%02X) = %d\n", type, r);
  }
}

static void primeHoldEnd() {
  if (!holding) return;
  holding = false;
  primeSend(MSG_PRIME_STOP);
  lv_label_set_text(primePadLbl, "HOLD TO PRIME");
  lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_ACCENT), 0);
  // MSG_RESP_PRIME{STOPPED} overwrites this with the length the controller measured.
  if (!holdAckMs) setPrimeMsg("no answer from the controller");
  else            setPrimeMsg("lifted");
  Serial.printf("[J9] MSG_PRIME_STOP ch=%u after %lu ms\n",
                flavorSel, millis() - holdStartMs);
}

static bool holdRetried = false;

static void primeHoldBegin() {
  if (holding) return;
  holding = true;
  holdStartMs = holdTickMs = millis();
  holdAckMs = 0;
  holdRetried = false;
  primeSend(MSG_PRIME_START);
  lv_label_set_text(primePadLbl, "PRIMING");
  lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_GOOD), 0);
  setPrimeMsg("holding");
  Serial.printf("[J9] MSG_PRIME_START ch=%u\n", flavorSel);
}

// The pad answers the press and the lift, not the click. PRESS_LOST is the finger sliding
// off the pad, which ends the hold the same way lifting it does.
static void primePadCb(lv_event_t *e) {
  lv_event_code_t code = lv_event_get_code(e);
  if (code == LV_EVENT_PRESSED)                                       primeHoldBegin();
  else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST)  primeHoldEnd();
}

// ── Navigation ──
static void railCb(lv_event_t *e)     { showPage((Page)(intptr_t)lv_event_get_user_data(e)); }
static void flvViewCb(lv_event_t *e)  { showFlavor((FlavorView)(intptr_t)lv_event_get_user_data(e)); }
static void svcViewCb(lv_event_t *e)  { showService((ServiceView)(intptr_t)lv_event_get_user_data(e)); }

static void flavorPickCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  refreshFlavorText();
  showFlavor(FLV_DETAIL);
}

static void primePickCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  showService(SVC_PRIME_HOLD);
}

static void cleanPickCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  showService(SVC_CLEAN_CONFIRM);
}

static void flavorToPrimeCb(lv_event_t *e) {
  (void)e;
  showPage(PAGE_SERVICE);
  showService(SVC_PRIME_HOLD);
}

static void cleanStartCb(lv_event_t *e) {
  (void)e;
  ChannelPayload p{flavorSel};
  j9.send(MSG_CLEAN_START, &p, sizeof(p));
  setCleanMsg("asked the controller ...");
}

static void ratioStepCb(lv_event_t *e) {
  int r = flavorRatio[flavorSel] + (int)(intptr_t)lv_event_get_user_data(e);
  if (r < 6)  r = 6;    // the range the base's SET:Fn_RATIO accepts
  if (r > 24) r = 24;
  flavorRatio[flavorSel] = (uint8_t)r;
  refreshFlavorText();
}

// ── Page builders ──

static void buildRail(lv_obj_t *scr) {
  static const struct { const char *icon; const char *label; } kRail[PAGE_COUNT] = {
      {LV_SYMBOL_HOME,     "HOME"},
      {LV_SYMBOL_TINT,     "FLAVOR"},
      {LV_SYMBOL_LOOP,     "SERVICE"},
      {LV_SYMBOL_CHARGE,   "STATUS"},
      {LV_SYMBOL_SETTINGS, "SETUP"},
  };
  for (int i = 0; i < PAGE_COUNT; i++) {
    lv_obj_t *b = mkBtn(scr, RAIL_W - 12, RAIL_ITEM_H, COL_CARD);
    lv_obj_set_pos(b, 6, 8 + i * (RAIL_ITEM_H + 6));
    lv_obj_set_style_pad_all(b, 6, 0);
    lv_obj_add_event_cb(b, railCb, LV_EVENT_CLICKED, (void *)(intptr_t)i);
    lv_obj_align(mkText(b, kRail[i].icon, &lv_font_montserrat_28, COL_TEXT), LV_ALIGN_TOP_MID, 0, 2);
    lv_obj_align(mkText(b, kRail[i].label, &lv_font_montserrat_20, COL_TEXT), LV_ALIGN_BOTTOM_MID, 0, 0);
    railBtn[i] = b;
  }
  linkDot = mkText(scr, LV_SYMBOL_WARNING "  J9", &lv_font_montserrat_20, COL_WARN);
  lv_obj_set_width(linkDot, RAIL_W);
  lv_obj_set_style_text_align(linkDot, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_set_pos(linkDot, 0, 8 + PAGE_COUNT * (RAIL_ITEM_H + 6) + 4);
}

// The screen behind it is already THEME_BG. LVGL repaints the whole 800x480 every frame
// (full_refresh), so a second opaque fill of the pane is 586 KB written to PSRAM per frame
// against a bus the scan-out DMA is reading continuously.
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

// A picture and two numbers.
static void buildHome(lv_obj_t *page) {
  lv_obj_align(mkText(page, "READY", &lv_font_montserrat_40, COL_TEXT), LV_ALIGN_TOP_MID, 0, 0);
  logoImg = lv_img_create(page);
  lv_img_set_src(logoImg, &frameDsc[0]);
  lv_obj_align(logoImg, LV_ALIGN_TOP_MID, 0, 50);
  homeFlavorLine = mkText(page, "", &lv_font_montserrat_20, COL_DIM);
  lv_obj_align(homeFlavorLine, LV_ALIGN_BOTTOM_MID, 0, 0);
}

// A split of two, and a drill-down behind each.
static void buildFlavor(lv_obj_t *page) {
  const lv_coord_t cw = (PANE_W - 2 * PANE_PAD - 16) / 2;

  lv_obj_t *both = mkView(page);
  lv_obj_align(mkText(both, "FLAVORS", &lv_font_montserrat_28, COL_DIM), LV_ALIGN_TOP_LEFT, 0, 0);
  for (int i = 0; i < 2; i++) {
    lv_obj_t *b = mkBtn(both, cw, 360, COL_CARD);
    lv_obj_align(b, LV_ALIGN_BOTTOM_LEFT, i * (cw + 16), 0);
    lv_obj_add_event_cb(b, flavorPickCb, LV_EVENT_CLICKED, (void *)(intptr_t)i);
    lv_obj_align(mkText(b, LV_SYMBOL_TINT, &lv_font_montserrat_48, COL_ACCENT), LV_ALIGN_TOP_MID, 0, 20);
    lv_obj_align(mkText(b, kFlavorName[i], &lv_font_montserrat_28, COL_TEXT), LV_ALIGN_CENTER, 0, -10);
    flvCardLbl[i] = mkText(b, "1:12", &lv_font_montserrat_48, COL_TEXT);
    lv_obj_align(flvCardLbl[i], LV_ALIGN_CENTER, 0, 60);
    lv_obj_align(mkText(b, "LEVEL  --", &lv_font_montserrat_20, COL_DIM), LV_ALIGN_BOTTOM_MID, 0, -8);
  }
  flvView[FLV_BOTH] = both;

  lv_obj_t *det = mkView(page);
  mkBack(det, flvViewCb, (void *)(intptr_t)FLV_BOTH);
  flvDetailName = mkText(det, "FLAVOR 2", &lv_font_montserrat_40, COL_TEXT);
  lv_obj_align(flvDetailName, LV_ALIGN_TOP_MID, 0, 8);

  lv_obj_t *row = mkCard(det, PANE_W - 2 * PANE_PAD, 130);
  lv_obj_align(row, LV_ALIGN_TOP_MID, 0, 90);
  lv_obj_align(mkText(row, "RATIO", &lv_font_montserrat_20, COL_DIM), LV_ALIGN_TOP_LEFT, 0, 0);
  lv_obj_t *minus = mkBtn(row, 84, 72, COL_CARD_ON);
  lv_obj_align(minus, LV_ALIGN_BOTTOM_LEFT, 0, 0);
  lv_obj_add_event_cb(minus, ratioStepCb, LV_EVENT_CLICKED, (void *)(intptr_t)-1);
  lv_obj_center(mkText(minus, LV_SYMBOL_MINUS, &lv_font_montserrat_28, COL_TEXT));
  lv_obj_t *plus = mkBtn(row, 84, 72, COL_CARD_ON);
  lv_obj_align(plus, LV_ALIGN_BOTTOM_RIGHT, 0, 0);
  lv_obj_add_event_cb(plus, ratioStepCb, LV_EVENT_CLICKED, (void *)(intptr_t)1);
  lv_obj_center(mkText(plus, LV_SYMBOL_PLUS, &lv_font_montserrat_28, COL_TEXT));
  flvDetailRatio = mkText(row, "1:12", &lv_font_montserrat_48, COL_TEXT);
  lv_obj_align(flvDetailRatio, LV_ALIGN_BOTTOM_MID, 0, -12);

  lv_obj_t *lvl = mkCard(det, PANE_W - 2 * PANE_PAD, 92);
  lv_obj_align(lvl, LV_ALIGN_TOP_MID, 0, 234);
  lv_obj_align(mkText(lvl, "LEVEL", &lv_font_montserrat_20, COL_DIM), LV_ALIGN_TOP_LEFT, 0, 0);
  lv_obj_align(mkText(lvl, "--", &lv_font_montserrat_40, COL_DIM), LV_ALIGN_BOTTOM_LEFT, 0, 0);

  lv_obj_t *pr = mkBtn(det, PANE_W - 2 * PANE_PAD, 82, COL_ACCENT);
  lv_obj_align(pr, LV_ALIGN_BOTTOM_MID, 0, 0);
  lv_obj_add_event_cb(pr, flavorToPrimeCb, LV_EVENT_CLICKED, NULL);
  lv_obj_center(mkText(pr, "PRIME THIS FLAVOR", &lv_font_montserrat_28, COL_TEXT));
  flvView[FLV_DETAIL] = det;
}

// Two flavor targets, side by side, under a title.
static void buildFlavorPicker(lv_obj_t *view, const char *title, lv_event_cb_t cb) {
  const lv_coord_t cw = (PANE_W - 2 * PANE_PAD - 16) / 2;
  lv_obj_align(mkText(view, title, &lv_font_montserrat_28, COL_DIM), LV_ALIGN_TOP_RIGHT, 0, 14);
  for (int i = 0; i < 2; i++) {
    lv_obj_t *b = mkTapCard(view, cw, 300, LV_SYMBOL_TINT, kFlavorName[i], cb, (void *)(intptr_t)i);
    lv_obj_align(b, LV_ALIGN_BOTTOM_LEFT, i * (cw + 16), 0);
  }
}

static void buildService(lv_obj_t *page) {
  const lv_coord_t cw = (PANE_W - 2 * PANE_PAD - 16) / 2;
  const lv_coord_t fw = PANE_W - 2 * PANE_PAD;

  lv_obj_t *menu = mkView(page);
  lv_obj_align(mkText(menu, "SERVICE", &lv_font_montserrat_28, COL_DIM), LV_ALIGN_TOP_LEFT, 0, 0);
  lv_obj_align(mkTapCard(menu, cw, 360, LV_SYMBOL_TINT, "PRIME", svcViewCb,
                         (void *)(intptr_t)SVC_PRIME_PICK), LV_ALIGN_BOTTOM_LEFT, 0, 0);
  lv_obj_align(mkTapCard(menu, cw, 360, LV_SYMBOL_LOOP, "CLEAN", svcViewCb,
                         (void *)(intptr_t)SVC_CLEAN_PICK), LV_ALIGN_BOTTOM_RIGHT, 0, 0);
  svcView[SVC_MENU] = menu;

  lv_obj_t *pick = mkView(page);
  mkBack(pick, svcViewCb, (void *)(intptr_t)SVC_MENU);
  buildFlavorPicker(pick, "PRIME WHICH", primePickCb);
  svcView[SVC_PRIME_PICK] = pick;

  // The hold pad. It fills the pane because it is meant to be found without looking.
  lv_obj_t *hold = mkView(page);
  mkBack(hold, svcViewCb, (void *)(intptr_t)SVC_PRIME_PICK);
  primeTitle = mkText(hold, "PRIME FLAVOR 2", &lv_font_montserrat_28, COL_DIM);
  lv_obj_align(primeTitle, LV_ALIGN_TOP_RIGHT, 0, 14);

  primePad = mkBtn(hold, fw, 200, COL_ACCENT);
  lv_obj_align(primePad, LV_ALIGN_TOP_MID, 0, 78);
  lv_obj_add_event_cb(primePad, primePadCb, LV_EVENT_ALL, NULL);
  primePadLbl = mkText(primePad, "HOLD TO PRIME", &lv_font_montserrat_48, COL_TEXT);
  lv_obj_center(primePadLbl);

  primeElapsed = mkText(hold, "0.0 s", &lv_font_montserrat_48, COL_TEXT);
  lv_obj_align(primeElapsed, LV_ALIGN_TOP_MID, 0, 294);

  primeBar = lv_bar_create(hold);
  lv_obj_set_size(primeBar, fw, 18);
  lv_obj_align(primeBar, LV_ALIGN_TOP_MID, 0, 366);
  lv_bar_set_range(primeBar, 0, (int32_t)PRIME_MAX_MS);
  lv_bar_set_value(primeBar, 0, LV_ANIM_OFF);
  lv_obj_set_style_bg_color(primeBar, lv_color_hex(COL_CARD), LV_PART_MAIN);
  lv_obj_set_style_bg_color(primeBar, lv_color_hex(COL_ACCENT), LV_PART_INDICATOR);

  primeMsg = mkText(hold, "idle", &lv_font_montserrat_20, COL_DIM);
  lv_obj_align(primeMsg, LV_ALIGN_BOTTOM_MID, 0, 0);
  svcView[SVC_PRIME_HOLD] = hold;

  lv_obj_t *cpick = mkView(page);
  mkBack(cpick, svcViewCb, (void *)(intptr_t)SVC_MENU);
  buildFlavorPicker(cpick, "CLEAN WHICH", cleanPickCb);
  svcView[SVC_CLEAN_PICK] = cpick;

  lv_obj_t *conf = mkView(page);
  mkBack(conf, svcViewCb, (void *)(intptr_t)SVC_CLEAN_PICK);
  cleanTitle = mkText(conf, "CLEAN FLAVOR 2", &lv_font_montserrat_40, COL_TEXT);
  lv_obj_align(cleanTitle, LV_ALIGN_TOP_MID, 0, 84);
  lv_obj_t *body = mkText(conf, "Three rounds: fill the line with water,\n"
                                "then pump it through to the nozzle.",
                          &lv_font_montserrat_20, COL_DIM);
  lv_obj_set_style_text_align(body, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_align(body, LV_ALIGN_TOP_MID, 0, 150);
  lv_obj_t *go = mkBtn(conf, fw, 96, COL_ACCENT);
  lv_obj_align(go, LV_ALIGN_TOP_MID, 0, 240);
  lv_obj_clear_flag(go, LV_OBJ_FLAG_PRESS_LOCK);   // slide off to change your mind
  lv_obj_add_event_cb(go, cleanStartCb, LV_EVENT_CLICKED, NULL);
  lv_obj_center(mkText(go, "START CLEAN CYCLE", &lv_font_montserrat_28, COL_TEXT));
  cleanMsg = mkText(conf, "", &lv_font_montserrat_20, COL_WARN);
  lv_obj_align(cleanMsg, LV_ALIGN_BOTTOM_MID, 0, 0);
  svcView[SVC_CLEAN_CONFIRM] = conf;
}

// Numbers and a bar, all of it read off the controller.
static lv_obj_t *statTile(lv_obj_t *page, const char *cap, lv_coord_t w, lv_coord_t h,
                          lv_coord_t x, lv_coord_t y, lv_obj_t **out) {
  lv_obj_t *c = mkCard(page, w, h);
  lv_obj_align(c, LV_ALIGN_TOP_LEFT, x, y);
  lv_obj_align(mkText(c, cap, &lv_font_montserrat_20, COL_DIM), LV_ALIGN_TOP_LEFT, 0, 0);
  *out = mkText(c, "--", &lv_font_montserrat_40, COL_TEXT);
  lv_obj_align(*out, LV_ALIGN_LEFT_MID, 0, 8);
  return c;
}

static void buildStatusPage(lv_obj_t *page) {
  const lv_coord_t cw = (PANE_W - 2 * PANE_PAD - 14) / 2;
  lv_obj_align(mkText(page, "CONTROLLER", &lv_font_montserrat_28, COL_DIM), LV_ALIGN_TOP_LEFT, 0, 0);
  statTile(page, "UPTIME",     cw, 150, 0,       46,  &statUptime);
  statTile(page, "FREE HEAP",  cw, 150, cw + 14, 46,  &statHeap);
  lv_obj_t *gas = statTile(page, "GAS SENSOR", cw, 150, 0, 210, &statGas);
  statGasBar = lv_bar_create(gas);
  lv_obj_set_size(statGasBar, cw - 28, 14);
  lv_obj_align(statGasBar, LV_ALIGN_BOTTOM_LEFT, 0, 0);
  lv_bar_set_range(statGasBar, 0, 3300);
  lv_obj_set_style_bg_color(statGasBar, lv_color_hex(COL_CARD_ON), LV_PART_MAIN);
  lv_obj_set_style_bg_color(statGasBar, lv_color_hex(COL_GOOD), LV_PART_INDICATOR);
  statTile(page, "J9 FRAMES RX / TX", cw, 150, cw + 14, 210, &statFrames);
  statFoot = mkText(page, "controller has not answered", &lv_font_montserrat_20, COL_WARN);
  lv_obj_align(statFoot, LV_ALIGN_BOTTOM_LEFT, 0, 0);
}

// The one page tall enough to scroll. It is read-outs and one restart; a control that
// changes how the appliance behaves belongs on the page for the thing it changes.
#define SETUP_STRIP_W 92     // the scroll column: two targets with a track between them
#define SETUP_BTN_H   104
#define SETUP_PAGE_PX 340    // one press of UP or DOWN

static lv_obj_t *setupRow(lv_obj_t *col, const char *cap, lv_obj_t **valueOut) {
  lv_obj_t *c = mkCard(col, LV_PCT(100), 80);
  lv_obj_align(mkText(c, cap, &lv_font_montserrat_20, COL_DIM), LV_ALIGN_LEFT_MID, 0, 0);
  if (valueOut) {
    *valueOut = mkText(c, "--", &lv_font_montserrat_28, COL_TEXT);
    lv_obj_align(*valueOut, LV_ALIGN_RIGHT_MID, 0, 0);
  }
  return c;
}

static void restartCb(lv_event_t *e) { (void)e; ESP.restart(); }

static void setupScrollRefresh() {
  if (!setupCol) return;
  lv_coord_t above = lv_obj_get_scroll_top(setupCol);
  lv_coord_t below = lv_obj_get_scroll_bottom(setupCol);
  lv_coord_t view  = lv_obj_get_height(setupCol);
  lv_coord_t total = above + below + view;
  if (total < view) total = view;

  lv_coord_t trackH = lv_obj_get_height(setupTrack);
  lv_coord_t thumbH = (lv_coord_t)((int32_t)trackH * view / total);
  if (thumbH < 56) thumbH = 56;
  if (thumbH > trackH) thumbH = trackH;
  lv_coord_t span = trackH - thumbH;
  lv_coord_t off = (above + below) > 0 ? (lv_coord_t)((int32_t)span * above / (above + below)) : 0;
  lv_obj_set_height(setupThumb, thumbH);
  lv_obj_align(setupThumb, LV_ALIGN_TOP_MID, 0, off);

  // A target at the end of its travel sinks into the background and its arrow goes dark.
  // Not LV_STATE_DISABLED: the default theme styles that state itself, at a higher state
  // weight than a colour set here for LV_STATE_DEFAULT, so the theme's grey is what shows.
  // Clearing CLICKABLE stops the press without handing the look to anyone else.
  struct { lv_obj_t *b; lv_obj_t *l; bool on; } ends[2] =
      {{setupUp, setupUpLbl, above > 0}, {setupDown, setupDownLbl, below > 0}};
  for (auto &e : ends) {
    if (e.on) lv_obj_add_flag(e.b, LV_OBJ_FLAG_CLICKABLE);
    else      lv_obj_clear_flag(e.b, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_bg_color(e.b, e.on ? lv_color_hex(COL_CARD_ON) : THEME_BG, LV_PART_MAIN);
    lv_obj_set_style_text_color(e.l, lv_color_hex(e.on ? COL_TEXT : COL_OFF), LV_PART_MAIN);
  }
}

// Bounded: lv_obj_scroll_by moves what it is asked to and keeps going past the ends, so a
// page step taken with less than a page of travel left lands off the column.
static void setupScrollCb(lv_event_t *e) {
  int dir = (int)(intptr_t)lv_event_get_user_data(e);
  lv_obj_scroll_by_bounded(setupCol, 0, -dir * SETUP_PAGE_PX, LV_ANIM_ON);
}

// The scroll animation moves the column without going through setupScrollCb, and a drag
// does not go through it at all, so the track follows the scroll itself.
static void setupScrolledCb(lv_event_t *e) { (void)e; setupScrollRefresh(); }

static void buildSetup(lv_obj_t *page) {
  const lv_coord_t paneW = PANE_W - 2 * PANE_PAD;
  const lv_coord_t colW  = paneW - SETUP_STRIP_W - 14;

  setupCol = lv_obj_create(page);
  lv_obj_set_size(setupCol, colW, LV_PCT(100));
  lv_obj_align(setupCol, LV_ALIGN_TOP_LEFT, 0, 0);
  lv_obj_set_style_bg_opa(setupCol, LV_OPA_TRANSP, 0);
  lv_obj_set_style_border_width(setupCol, 0, 0);
  lv_obj_set_style_pad_all(setupCol, 0, 0);
  lv_obj_set_style_pad_row(setupCol, 12, 0);
  lv_obj_set_flex_flow(setupCol, LV_FLEX_FLOW_COLUMN);
  lv_obj_set_scroll_dir(setupCol, LV_DIR_VER);
  lv_obj_set_scrollbar_mode(setupCol, LV_SCROLLBAR_MODE_OFF);
  lv_obj_add_event_cb(setupCol, setupScrolledCb, LV_EVENT_SCROLL, NULL);

  lv_obj_t *v;
  setupRow(setupCol, "DISPLAY BUILD", &v);
  lv_label_set_text(v, FW_VERSION);
  setupRow(setupCol, "CONTROLLER BUILD", &setupCtrlVer);
  setupRow(setupCol, "RS485 PINS", &setupLinkPins);
  setupRow(setupCol, "J9 FRAMES RX / TX", &setupFrames);
  setupRow(setupCol, "LINK REINITS", &setupReinits);
  setupRow(setupCol, "TOUCH BRIDGED / STALE", &setupTouchCnt);
  setupRow(setupCol, "LAST TOUCH", &setupTouch);
  setupRow(setupCol, "FREE HEAP", &setupHeap);
  setupRow(setupCol, "FREE PSRAM", &setupPsram);
  setupRow(setupCol, "LOOP HIGH-WATER", &setupLoop);
  setupRow(setupCol, "UPTIME", &setupUptime);

  lv_obj_t *r = mkBtn(setupCol, LV_PCT(100), 80, COL_CARD);
  lv_obj_clear_flag(r, LV_OBJ_FLAG_PRESS_LOCK);   // a drag that started here scrolls, and
  lv_obj_add_event_cb(r, restartCb, LV_EVENT_CLICKED, NULL);
  lv_obj_center(mkText(r, LV_SYMBOL_POWER "   RESTART DISPLAY", &lv_font_montserrat_28, COL_ACCENT));

  // The scroll column, right of the rows: a page up, a track that shows where you are,
  // a page down.
  setupUp = mkBtn(page, SETUP_STRIP_W, SETUP_BTN_H, COL_CARD_ON);
  lv_obj_align(setupUp, LV_ALIGN_TOP_RIGHT, 0, 0);
  lv_obj_add_event_cb(setupUp, setupScrollCb, LV_EVENT_CLICKED, (void *)(intptr_t)-1);
  setupUpLbl = mkText(setupUp, LV_SYMBOL_UP, &lv_font_montserrat_40, COL_TEXT);
  lv_obj_center(setupUpLbl);

  setupDown = mkBtn(page, SETUP_STRIP_W, SETUP_BTN_H, COL_CARD_ON);
  lv_obj_align(setupDown, LV_ALIGN_BOTTOM_RIGHT, 0, 0);
  lv_obj_add_event_cb(setupDown, setupScrollCb, LV_EVENT_CLICKED, (void *)(intptr_t)1);
  setupDownLbl = mkText(setupDown, LV_SYMBOL_DOWN, &lv_font_montserrat_40, COL_TEXT);
  lv_obj_center(setupDownLbl);

  setupTrack = lv_obj_create(page);
  lv_obj_set_size(setupTrack, 22, 448 - 2 * SETUP_BTN_H - 24);
  lv_obj_align(setupTrack, LV_ALIGN_TOP_RIGHT, -(SETUP_STRIP_W - 22) / 2, SETUP_BTN_H + 12);
  lv_obj_set_style_bg_color(setupTrack, lv_color_hex(COL_CARD), 0);
  lv_obj_set_style_border_width(setupTrack, 0, 0);
  lv_obj_set_style_radius(setupTrack, 11, 0);
  lv_obj_set_style_pad_all(setupTrack, 0, 0);
  lv_obj_clear_flag(setupTrack, LV_OBJ_FLAG_SCROLLABLE);

  setupThumb = lv_obj_create(setupTrack);
  lv_obj_set_width(setupThumb, 22);
  lv_obj_set_style_bg_color(setupThumb, lv_color_hex(COL_ACCENT), 0);
  lv_obj_set_style_border_width(setupThumb, 0, 0);
  lv_obj_set_style_radius(setupThumb, 11, 0);
  lv_obj_clear_flag(setupThumb, LV_OBJ_FLAG_SCROLLABLE);
}

// GPIO43 reads RS485_RXD on Waveshare's table and is the S3's U0TXD. The pair is a
// variable and this exchanges it; the base answering is what settles which way it runs.
static void rs485Swap() {
  int t = rs485Rx; rs485Rx = rs485Tx; rs485Tx = t;
  j9.end();
  Serial1.end();
  j9Begin();
  if (setupLinkPins) {
    char b[24];
    snprintf(b, sizeof(b), "%d / %d", rs485Rx, rs485Tx);
    lv_label_set_text(setupLinkPins, b);
  }
}

// ── Page switching ──

static void animRun(bool on) {
  if (!animTimer) return;
  if (on) lv_timer_resume(animTimer); else lv_timer_pause(animTimer);
}

static void showFlavor(FlavorView v) {
  showOnly(flvView, FLV_COUNT, v);
  refreshFlavorText();
}

static void showService(ServiceView v) {
  if (v != SVC_PRIME_HOLD) primeHoldEnd();
  showOnly(svcView, SVC_COUNT, v);
  if (v == SVC_PRIME_HOLD) {
    char b[32];
    snprintf(b, sizeof(b), "PRIME %s", kFlavorName[flavorSel]);
    lv_label_set_text(primeTitle, b);
    lv_label_set_text(primeElapsed, "0.0 s");
    lv_bar_set_value(primeBar, 0, LV_ANIM_OFF);
    setPrimeMsg("idle");
  } else if (v == SVC_CLEAN_CONFIRM) {
    char b[32];
    snprintf(b, sizeof(b), "CLEAN %s", kFlavorName[flavorSel]);
    lv_label_set_text(cleanTitle, b);
    setCleanMsg("");
  }
}

// The rungs the dark climbs. Done while the screen is off, so a wake shows the answer
// rather than jumping to it under the user's eyes.
static void idleReset(uint8_t stage) {
  if (!uiReady) return;
  if (stage == 2) {
    if (activePage == PAGE_SERVICE)     showService(SVC_MENU);
    else if (activePage == PAGE_FLAVOR) showFlavor(FLV_BOTH);
    else if (activePage == PAGE_SETUP)  { lv_obj_scroll_to_y(setupCol, 0, LV_ANIM_OFF); setupScrollRefresh(); }
  } else if (stage == 3) {
    showPage(PAGE_HOME);
  }
}

static void showPage(Page p) {
  primeHoldEnd();
  showOnly(pageObj, PAGE_COUNT, p);
  for (int i = 0; i < PAGE_COUNT; i++)
    lv_obj_set_style_bg_color(railBtn[i], lv_color_hex(i == p ? COL_ACCENT : COL_CARD), 0);
  activePage = p;
  // Nothing repaints a page that is not on screen — the animation is the only thing on
  // this panel that invalidates on its own.
  animRun(p == PAGE_HOME && !screenIdle);
  if (p == PAGE_FLAVOR)  showFlavor(FLV_BOTH);
  if (p == PAGE_SERVICE) showService(SVC_MENU);
  if (p == PAGE_STATUS)  { statusAskedMs = 0; refreshStatusPage(); }
  if (p == PAGE_SETUP) {
    refreshSetupPage();
    lv_obj_update_layout(setupCol);   // the scroll extents are only real once laid out
    setupScrollRefresh();
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

  lv_obj_t *scr = lv_scr_act();
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);
  lv_obj_clear_flag(scr, LV_OBJ_FLAG_SCROLLABLE);

  buildRail(scr);
  for (int i = 0; i < PAGE_COUNT; i++) pageObj[i] = buildPane(scr);
  buildHome(pageObj[PAGE_HOME]);
  buildFlavor(pageObj[PAGE_FLAVOR]);
  buildService(pageObj[PAGE_SERVICE]);
  buildStatusPage(pageObj[PAGE_STATUS]);
  buildSetup(pageObj[PAGE_SETUP]);

  uiReady = true;
  refreshFlavorText();
  {
    char b[24];
    snprintf(b, sizeof(b), "%d / %d", rs485Rx, rs485Tx);
    lv_label_set_text(setupLinkPins, b);
  }
  showPage(PAGE_HOME);
}

// ════════════════════════════════════════════════════════════
//  USB serial text commands (bring-up / diagnostics)
// ════════════════════════════════════════════════════════════

static void processTextLine(const char *line) {
  if (strcmp(line, "GET_VERSION") == 0) {
    Serial.printf("VERSION:FRONT=%s\n", FW_VERSION);
  } else if (strcmp(line, "GET_DIAG") == 0) {
    Serial.printf("DIAG:scrollTop=%d,scrollBot=%d,scrollY=%d,"
                  "page=%d,holding=%d,reinits=%lu,unanswered=%u,"
                  "bridged=%lu,stale=%lu,sendErr=%d,"
                  "heap=%lu,minHeap=%lu,psram=%lu,freePsram=%lu,bl=%d,"
                  "frame=%u,gt911=0x%02X,touch=%lu,lastXY=%u/%u,idle=%d,"
                  "link=%s,maxLoopMs=%lu,uptime=%lus\n",
                  setupCol ? (int)lv_obj_get_scroll_top(setupCol) : -1,
                  setupCol ? (int)lv_obj_get_scroll_bottom(setupCol) : -1,
                  setupCol ? (int)lv_obj_get_scroll_y(setupCol) : -1,
                  (int)activePage, holding ? 1 : 0,
                  (unsigned long)linkReinits, (unsigned)unanswered,
                  (unsigned long)touchBridged, (unsigned long)gt911Stale, lastSendErr,
                  (unsigned long)ESP.getFreeHeap(),
                  (unsigned long)ESP.getMinFreeHeap(),
                  (unsigned long)ESP.getPsramSize(),
                  (unsigned long)ESP.getFreePsram(),
                  backlightOn ? 1 : 0,
                  (unsigned)animFrameIdx,
                  gt911Addr,
                  (unsigned long)touchCount,
                  (unsigned)lastTouchX, (unsigned)lastTouchY,
                  screenIdle ? 1 : 0,
                  j9.framesRx ? "rx" : "silent",
                  (unsigned long)maxLoopMs,
                  millis() / 1000);
    maxLoopMs = 0;  // high-water mark since last query
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
      Serial.printf("OK:IDLE=%c page=%d\n", s, (int)activePage);
    } else {
      Serial.println("ERR:IDLE expects 0..3");
    }
  } else if (strcmp(line, "PUMP") == 0) {
    sendPumpRun(PUMP_CHANNEL_B, 1000);
    Serial.println("OK:PUMP");
  } else if (strncmp(line, "PAGE:", 5) == 0) {
    int p = atoi(line + 5);
    if (p < 0 || p >= PAGE_COUNT) Serial.println("ERR:PAGE expects 0..4");
    else { showPage((Page)p); Serial.printf("OK:PAGE=%d\n", p); }
  } else if (strncmp(line, "PRIME:START:", 12) == 0) {
    // The pad's own handlers, without a finger on the glass — same frames, same ticks.
    int f = atoi(line + 12);
    if (f != 1 && f != 2) { Serial.println("ERR:PRIME:START expects 1 or 2"); }
    else {
      flavorSel = (uint8_t)(f - 1);
      showPage(PAGE_SERVICE);
      showService(SVC_PRIME_HOLD);
      primeHoldBegin();
      Serial.printf("OK:PRIME:START=%d\n", f);
    }
  } else if (strcmp(line, "PRIME:STOP") == 0) {
    primeHoldEnd();
    Serial.println("OK:PRIME:STOP");
  } else if (strcmp(line, "PANEL:REALIGN") == 0) {
    panelRealign();
    Serial.println("OK:PANEL:REALIGN");
  } else if (strcmp(line, "STATUS") == 0) {
    j9.send(MSG_STATUS_REQ, nullptr, 0);
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
    int r = j9.send(MSG_TEXT, line + 6, strlen(line + 6));
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

  ch422gBringUp();
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

  // LVGL — the two draw buffers ARE the two panel framebuffers (full-refresh
  // double-buffer page-flip; zero-copy flush). No separate buffer allocated.
  lv_init();
  lv_disp_draw_buf_init(&draw_buf, fb0, fb1, (uint32_t)SCREEN_W * SCREEN_H);

  static lv_disp_drv_t disp_drv;
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = SCREEN_W;
  disp_drv.ver_res = SCREEN_H;
  disp_drv.flush_cb = lvglFlush;
  disp_drv.draw_buf = &draw_buf;
  disp_drv.full_refresh = 1;  // repaint the whole back buffer each frame, then flip
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
  lv_indev_drv_register(&indev_drv);

  buildUi();

  // Render the first frame, then light the backlight (no boot flash).
  lv_timer_handler();
  setBacklight(true);

  // Start the loading animation (~10 fps).
  animTimer = lv_timer_create(animTimerCb, ANIM_FRAME_MS, NULL);

  lastInputTime = millis();
  displayReady = true;
  Serial.println("Ready — animated loading logo running.");
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

  j9.service();

  if (panelRestartDue && millis() >= panelRestartDue) {
    panelRestartDue = 0;
    panelRealign();
  }

  // A held pad feeds the controller a tick under it, and moves its own readouts at 10 Hz.
  if (holding) {
    unsigned long now = millis();
    if (now - holdTickMs >= PRIME_TICK_MS) { primeSend(MSG_PRIME_TICK); holdTickMs = now; }
    static unsigned long lastHoldUi = 0;
    if (now - lastHoldUi >= 100) {
      lastHoldUi = now;
      unsigned long el = now - holdStartMs;
      char b[16];
      snprintf(b, sizeof(b), "%lu.%lu s", el / 1000, (el % 1000) / 100);
      lv_label_set_text(primeElapsed, b);
      lv_bar_set_value(primeBar, (int32_t)(el > PRIME_MAX_MS ? PRIME_MAX_MS : el), LV_ANIM_OFF);
      // A START that goes unanswered is this board's TX having stopped reaching the wire.
      // One reset of the pads, one more START, and the hold carries on under the finger.
      if (!holdAckMs && el > 700 && !holdRetried) {
        holdRetried = true;
        j9Reinit("prime start unanswered");
        primeSend(MSG_PRIME_START);
        setPrimeMsg("link reset — retrying");
      }
      if (!holdAckMs && el > 1800) setPrimeMsg("no answer from the controller");
    }
  }

  // The status request is the only traffic this board starts on its own: every 2 s while
  // STATUS is up, every 10 s otherwise, and never while a hold owns the pair. Three in a
  // row with nothing back is the same failure, found before a finger meets the glass.
  if (uiReady && !screenIdle && !holding) {
    uint32_t every = (activePage == PAGE_STATUS) ? 2000 : 10000;
    if (millis() - statusAskedMs >= every) {
      statusAskedMs = millis();
      if (unanswered >= 3) j9Reinit("3 status polls unanswered");
      else                 unanswered++;
      j9.send(MSG_STATUS_REQ, nullptr, 0);
    }
  }

  // Once a second: the rail's link indicator, and whichever page shows something live.
  if (uiReady && !screenIdle) {
    static unsigned long lastSlow = 0;
    if (millis() - lastSlow >= 1000) {
      lastSlow = millis();
      padWatch();
      refreshLinkDot();
      if (activePage == PAGE_STATUS) refreshStatusPage();
      if (activePage == PAGE_SETUP)  refreshSetupPage();
    }
  }

  // Idle: after inactivity, turn the backlight off and pause the animation (no point
  // repainting a dark screen). A touch wakes it — see wake().
  if (displayReady && !screenIdle && !holding && millis() - lastInputTime >= IDLE_TIMEOUT_MS) {
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

  unsigned long loopMs = millis() - loopStart;
  if (loopMs > maxLoopMs) maxLoopMs = loopMs;

  delay(5);
}
