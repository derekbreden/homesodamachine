#include <Arduino.h>
#include <esp_system.h>
#include <esp_heap_caps.h>
#include <Wire.h>
#include <lvgl.h>
#include "esp_lcd_panel_rgb.h"
#include "esp_lcd_panel_ops.h"
#include "freertos/semphr.h"
#include "fw_version.h"

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
// This is the foundation only: it brings up the RGB panel + LVGL and runs
// the animated loading logo centered on the theme background. The interaction UX is
// deliberately not built yet. Two integration seams are marked below but not
// implemented:
//   • Touch (GT911 on the shared I2C bus; reset already released via CH422G).
//   • The RS485/UART link to the base ESP32 (state sync, config) — this board
//     is the appliance's front-face config + interaction surface.

// ── Theme (matches faucet display / config display / iOS app) ──
#define THEME_BG  lv_color_hex(0x1a1a2e)

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
#define GT911_REG_POINT1 0x8150  // first touch point (8 bytes: id, xL,xH, yL,yH, ...)

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

// ── UI objects ──
static lv_obj_t *logoImg;
static lv_img_dsc_t frameDsc[NUM_ANIM_FRAMES];
static lv_timer_t *animTimer = nullptr;
static uint8_t animFrameIdx = 0;

// ── Idle dimming (matches the faucet display) ──
// The backlight is a digital line on the CH422G (no PWM), so instead of fading
// the backlight we fade the rendered content: a black layer over everything
// whose opacity ramps up to a dim glow after inactivity. The first touch snaps
// back to full and is consumed (it only wakes). Mirrors the faucet's gradual-
// dim / instant-wake behavior.
#define DIM_TIMEOUT_MS 60000  // inactivity before dimming (same as the faucet)
#define DIM_OPA        216    // dim-glow level: mostly black, logo still faintly visible
#define DIM_FADE_STEP  12     // opacity per fade pass; fade spans DIM_OPA/STEP passes

static unsigned long lastInputTime = 0;
static bool dimmed = false;
static uint8_t dimOpa = 0;        // current black-overlay opacity (0 = full bright)
static uint8_t dimTarget = 0;     // where dimOpa is heading

// ── Touch (GT911) ──
static uint8_t gt911Addr = 0;     // probed at init (0 = not found)
static uint32_t touchCount = 0;   // diagnostics: presses seen since last GET_DIAG

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
  // to PSRAM (the render) can no longer starve the live scanline. 10 lines.
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
static bool gt911ReadTouch(uint16_t *x, uint16_t *y) {
  if (!gt911Addr) return false;
  uint8_t status;
  if (!gt911ReadBytes(GT911_REG_STATUS, &status, 1)) return false;
  if (!(status & 0x80)) return false;  // buffer not ready yet
  bool touched = false;
  if ((status & 0x0F) > 0) {
    uint8_t p[8];
    if (gt911ReadBytes(GT911_REG_POINT1, p, 8)) {
      *x = (uint16_t)p[1] | ((uint16_t)p[2] << 8);
      *y = (uint16_t)p[3] | ((uint16_t)p[4] << 8);
      touched = true;
    }
  }
  gt911WriteByte(GT911_REG_STATUS, 0);  // clear buffer-ready for the next frame
  return touched;
}

// The dim overlay rides LVGL's top layer (above all content); its opacity is
// what we fade. 0 = full bright, DIM_OPA = dim glow.
static void applyDim() {
  lv_obj_set_style_bg_color(lv_layer_top(), lv_color_black(), 0);
  lv_obj_set_style_bg_opa(lv_layer_top(), dimOpa, 0);
}

// Snap back to full brightness and resume the animation (instant, like the
// faucet's wake). Always resets the idle timer.
static void wake() {
  lastInputTime = millis();
  if (dimmed || dimOpa != 0) {
    dimmed = false;
    dimTarget = 0;
    dimOpa = 0;
    applyDim();
    if (animTimer) lv_timer_resume(animTimer);
  }
}

// LVGL pointer indev: any touch wakes and resets the idle timer. While dimmed,
// the first touch is consumed (wake only) so it can't trip future UI.
static void touchpadRead(lv_indev_drv_t *drv, lv_indev_data_t *data) {
  static bool prevTouch = false;
  uint16_t x = 0, y = 0;
  bool now = gt911ReadTouch(&x, &y);
  if (now) {
    if (!prevTouch) touchCount++;  // count press edges
    bool wasDimmed = dimmed || dimOpa != 0;
    wake();
    data->point.x = x;
    data->point.y = y;
    data->state = wasDimmed ? LV_INDEV_STATE_RELEASED : LV_INDEV_STATE_PRESSED;
  } else {
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

  logoImg = lv_img_create(scr);
  lv_img_set_src(logoImg, &frameDsc[0]);
  lv_obj_align(logoImg, LV_ALIGN_CENTER, 0, 0);
}

// ════════════════════════════════════════════════════════════
//  USB serial text commands (bring-up / diagnostics)
// ════════════════════════════════════════════════════════════

static void processTextLine(const char *line) {
  if (strcmp(line, "GET_VERSION") == 0) {
    Serial.printf("VERSION:FRONT=%s\n", FW_VERSION);
  } else if (strcmp(line, "GET_DIAG") == 0) {
    Serial.printf("DIAG:heap=%lu,minHeap=%lu,psram=%lu,freePsram=%lu,bl=%d,"
                  "frame=%u,gt911=0x%02X,touch=%lu,dim=%d,dimOpa=%u,"
                  "maxLoopMs=%lu,uptime=%lus\n",
                  (unsigned long)ESP.getFreeHeap(),
                  (unsigned long)ESP.getMinFreeHeap(),
                  (unsigned long)ESP.getPsramSize(),
                  (unsigned long)ESP.getFreePsram(),
                  backlightOn ? 1 : 0,
                  (unsigned)animFrameIdx,
                  gt911Addr,
                  (unsigned long)touchCount,
                  dimmed ? 1 : 0,
                  (unsigned)dimOpa,
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
  } else if (strncmp(line, "DIM:", 4) == 0) {
    // Force the idle-dim state for testing (bypasses the 60 s timeout).
    if (line[4] == '1') {
      dimmed = true; dimTarget = DIM_OPA;
      Serial.println("OK:DIM=1");
    } else if (line[4] == '0') {
      wake();
      Serial.println("OK:DIM=0");
    } else {
      Serial.println("ERR:DIM expects 0 or 1");
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
  applyDim();  // initialize the dim overlay (transparent at first)

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

  // Seam: service the RS485/UART link to the base ESP32 here.

  // Idle dimming: after inactivity, gradually fade the content to a dim glow
  // (waking is instant, handled in wake()). Once fully dimmed, pause the
  // animation so the idle screen stops repainting. Mirrors the faucet.
  if (displayReady) {
    if (!dimmed && millis() - lastInputTime >= DIM_TIMEOUT_MS) {
      dimmed = true;
      dimTarget = DIM_OPA;
    }
    if (dimOpa != dimTarget) {
      int next = (int)dimOpa + DIM_FADE_STEP;
      if (next > (int)dimTarget) next = dimTarget;
      dimOpa = (uint8_t)next;
      applyDim();
      if (dimmed && dimOpa == dimTarget && animTimer) lv_timer_pause(animTimer);
    }
  }

  if (displayReady) lv_timer_handler();

  unsigned long loopMs = millis() - loopStart;
  if (loopMs > maxLoopMs) maxLoopMs = loopMs;

  delay(5);
}
