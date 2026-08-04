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
// It brings up the RGB panel + LVGL and runs the animated loading logo centered on
// the theme background. The interaction UX is not built yet; what stands in for it is
// one bench button that runs a pump on the base board over RS485, which is there to
// prove the link end to end rather than to be the product's UX.

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

// ── UI objects ──
static lv_obj_t *logoImg;
static lv_img_dsc_t frameDsc[NUM_ANIM_FRAMES];
static lv_timer_t *animTimer = nullptr;
static uint8_t animFrameIdx = 0;
static lv_obj_t *statusLabel = nullptr;   // last line off the J9 link

static void setStatus(const char *s) {
  if (statusLabel) lv_label_set_text(statusLabel, s);
}

// ── Idle backlight-off (the faucet's idle behavior, adapted to this board) ──
// The backlight is a digital line on the CH422G (on/off only — no PWM), so the
// idle state is simply the backlight off and the animation paused. The first
// touch turns it back on and resumes. Instant off / instant on.
#define IDLE_TIMEOUT_MS 60000  // inactivity before the backlight turns off

static unsigned long lastInputTime = 0;
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
      memcpy(lastRaw, p, 8);
      lastStatus = status;
      // 0x814F is the track ID; POINT1 (0x8150) is already X-low, so the coordinates
      // start at p[0] — x low/high, then y low/high, then a 16-bit touch size.
      *x = (uint16_t)p[0] | ((uint16_t)p[1] << 8);
      *y = (uint16_t)p[2] | ((uint16_t)p[3] << 8);
      touched = true;
    }
  }
  gt911WriteByte(GT911_REG_STATUS, 0);  // clear buffer-ready for the next frame
  return touched;
}

// Turn the backlight back on and resume the animation (instant). Always resets
// the idle timer. A tap calls this — "tap to bring the backlight back on."
static void wake() {
  lastInputTime = millis();
  if (screenIdle || !backlightOn) {
    screenIdle = false;
    setBacklight(true);
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
    if (!prevTouch) {
      touchCount++;  // count press edges
      Serial.printf("[touch] x=%u y=%u  status=0x%02X raw=%02X %02X %02X %02X %02X %02X %02X %02X%s\n",
                    x, y, lastStatus, lastRaw[0], lastRaw[1], lastRaw[2], lastRaw[3],
                    lastRaw[4], lastRaw[5], lastRaw[6], lastRaw[7],
                    screenIdle ? " (idle — consumed)" : "");
      lastTouchX = x;
      lastTouchY = y;
    }
    bool wasIdle = screenIdle;
    wake();
    data->point.x = x;
    data->point.y = y;
    // While idle, consume the first touch (wake only) so it can't trip future UI.
    data->state = wasIdle ? LV_INDEV_STATE_RELEASED : LV_INDEV_STATE_PRESSED;
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

// ════════════════════════════════════════════════════════════
//  RS485 link to the base ESP32
// ════════════════════════════════════════════════════════════

// The transport is the one the appliance already runs between boards: TinyProto Fd over
// the UART, typed frames through ProtoLink. This board's transceiver gates its receiver
// off while driving, so nothing it sends returns and there is no echo to cancel here —
// the base's U7 keeps receiving and cancels its own, a layer below its ProtoLink.
static HdlcLink j9;

static void j9OnMessage(HdlcLink *link, const uint8_t *frame, uint16_t len) {
  (void)link;
  uint8_t type = msgType(frame);
  const uint8_t *payload = msgPayload(frame);
  uint16_t plen = msgPayloadLen(len);

  if (type == MSG_RESP_PUMP_DONE && plen >= sizeof(ResponsePayload)) {
    char buf[48];
    snprintf(buf, sizeof(buf), "pump %c ran", payload[0] == 1 ? 'B' : 'A');
    Serial.printf("[J9] MSG_RESP_PUMP_DONE ch=%u\n", payload[0]);
    setStatus(buf);
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

// The bench button. One MSG_PUMP_RUN naming the channel, the duty and the run length —
// the base answers MSG_RESP_PUMP_DONE once the run has finished, so the label changes
// after the motor stops rather than when the press lands.
static void pumpBtnCb(lv_event_t *e) {
  (void)e;
  // Full power for a second. A Kamoer head does not break away part-throttle — the
  // appliance meters flavor by how long the pump is on, not by how hard it is driven.
  PumpRunPayload req{PUMP_CHANNEL_B, 100, 1000};
  int r = j9.send(MSG_PUMP_RUN, &req, sizeof(req));
  Serial.printf("[J9] MSG_PUMP_RUN ch=%u duty=%u ms=%u -> send()=%d, bytesTx=%lu bytesRx=%lu\n",
                req.channel, req.duty, req.ms, r,
                (unsigned long)j9.bytesTx, (unsigned long)j9.bytesRx);
  setStatus(r >= 0 ? "pump B requested" : "send failed");
}

static void buildStatus(lv_obj_t *scr) {
  statusLabel = lv_label_create(scr);
  lv_obj_set_style_text_color(statusLabel, lv_color_hex(0x8888aa), 0);
  lv_label_set_text(statusLabel, "J9 idle");
  lv_obj_align(statusLabel, LV_ALIGN_BOTTOM_MID, 0, -24);

  lv_obj_t *btn = lv_btn_create(scr);
  lv_obj_set_size(btn, 320, 96);
  lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -64);
  lv_obj_set_style_bg_color(btn, lv_color_hex(0xe94560), 0);
  lv_obj_add_event_cb(btn, pumpBtnCb, LV_EVENT_CLICKED, NULL);

  lv_obj_t *lbl = lv_label_create(btn);
  lv_label_set_text(lbl, "RUN PUMP B");
  lv_obj_center(lbl);
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
  lv_obj_align(logoImg, LV_ALIGN_CENTER, 0, -80);

  buildStatus(scr);
}

// ════════════════════════════════════════════════════════════
//  USB serial text commands (bring-up / diagnostics)
// ════════════════════════════════════════════════════════════

static void processTextLine(const char *line) {
  if (strcmp(line, "GET_VERSION") == 0) {
    Serial.printf("VERSION:FRONT=%s\n", FW_VERSION);
  } else if (strcmp(line, "GET_DIAG") == 0) {
    Serial.printf("DIAG:heap=%lu,minHeap=%lu,psram=%lu,freePsram=%lu,bl=%d,"
                  "frame=%u,gt911=0x%02X,touch=%lu,lastXY=%u/%u,idle=%d,"
                  "link=%s,maxLoopMs=%lu,uptime=%lus\n",
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
    // Force the idle state for testing (bypasses the 60 s timeout):
    // IDLE:1 = backlight off + pause animation; IDLE:0 = wake.
    if (line[5] == '1') {
      screenIdle = true;
      setBacklight(false);
      if (animTimer) lv_timer_pause(animTimer);
      Serial.println("OK:IDLE=1");
    } else if (line[5] == '0') {
      wake();
      Serial.println("OK:IDLE=0");
    } else {
      Serial.println("ERR:IDLE expects 0 or 1");
    }
  } else if (strcmp(line, "PUMP") == 0) {
    pumpBtnCb(nullptr);           // the button's own frame, without a finger on the glass
    Serial.println("OK:PUMP");
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
    int t = rs485Rx; rs485Rx = rs485Tx; rs485Tx = t;
    j9.end();
    Serial1.end();
    j9Begin();
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

  // Idle: after inactivity, turn the backlight off and pause the animation
  // (no point repainting a dark screen). A touch wakes it — see wake().
  if (displayReady && !screenIdle && millis() - lastInputTime >= IDLE_TIMEOUT_MS) {
    screenIdle = true;
    setBacklight(false);
    if (animTimer) lv_timer_pause(animTimer);
  }

  if (displayReady) lv_timer_handler();

  unsigned long loopMs = millis() - loopStart;
  if (loopMs > maxLoopMs) maxLoopMs = loopMs;

  delay(5);
}
