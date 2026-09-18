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
#include "front_ui_policy.h"
#include "proto_link.h"
#include <driver/gpio.h>
#include <esp_sleep.h>
#include "soc/gpio_reg.h"
#include "soc/io_mux_reg.h"

// Implemented by esp_lcd_panel_rgb_local.c, this tree's copy of the ESP-IDF
// v5.5.4 RGB driver. It increments only when an actual bounce-buffer shortfall
// requires scan recovery; a PANEL:REALIGN resets the same way and is not
// counted, and normal wake cycles must leave it unchanged.
extern "C" uint32_t home_soda_rgb_restart_count(void);
// The selected On tap faucet mark, with a pulsing orange dot. Sixteen native
// 360x360 RGB565 frames share the Big Blue background and live in mapped art.
// tools/gen_animation_frames.py renders the canonical brand/mark.svg.
#include "ota_receiver.h"
#include "logos_sink.h"
#include "board_art.h"
#include "wifi_bench.h"
#include "image_store.h"

#define NUM_ANIM_FRAMES  16
#define ANIM_FRAME_MS    100   // ~10 fps, matches the config display
#define LOGO_SIZE        360
// ── A logo is one shape, at three scales ──
// EVERY FACE ON THIS PANEL IS THE FAUCET'S GLASS. A picture reaches the machine
// as one tall rectangle, and a square thumbnail cut from a different window
// would answer a question nobody asked: what a photograph looks like somewhere
// it will never be shown. So the anchor is the faucet's own rendition, the card
// is it at three quarters and the tile at half — 43:80 all the way down, so
// choosing on this glass is choosing for that one.
#define FLAVOR_ANCHOR_W    (43 * 4)   // 172x320, and what the faucet wears
#define FLAVOR_ANCHOR_H    (80 * 4)
#define FLAVOR_CARD_W      (43 * 3)   // 129x240
#define FLAVOR_CARD_H      (80 * 3)
#define FLAVOR_TILE_W      (43 * 2)   //  86x160
#define FLAVOR_TILE_H      (80 * 2)
// Logos a channel can be given: FLAVOR_ART_FACTORY compiled in and permanent,
// the rest the user's own out of this board's image store. proto_msg.h holds
// the split, because the main board is what says which one a channel wears.
#define FLAVOR_IMAGE_COUNT   FLAVOR_ART_COUNT
#define FLAVOR_FACTORY_COUNT FLAVOR_ART_FACTORY

// ════════════════════════════════════════════════════════════
//  ESP32-S3 Enclosure Display — foundation
// ════════════════════════════════════════════════════════════
//
// Waveshare ESP32-S3-Touch-LCD-4.3B: 800x480 IPS RGB parallel panel,
// GT911 capacitive touch, CH422G I/O expander, ESP32-S3-WROOM-1-N16R8
// (16 MB flash / 8 MB octal PSRAM). Mounts in the enclosure's front face,
// angled up toward a standing user.
//
// Big Blue keeps both flavors in a left rail, the selected portrait beside it,
// and Fill, Prime, Clean above the task pane. Settings occupies the whole area
// right of the rail. The main board owns selection, operations and prime sessions;
// holding either glass's prime pad renews the same tokenized session.

// ── Big Blue ──
#define COL_BLUE     0x1749d1
#define THEME_BG     lv_color_hex(COL_BLUE)
#define COL_CARD     0x10319c
#define COL_CARD_ON  0x315fdb
#define COL_ACCENT   0xff9152
#define COL_TEXT     0xffffff
#define COL_DIM      0xdce6ff
#define COL_INK      0x153383
#define COL_GOOD     COL_ACCENT
#define COL_WARN     0xffb183
#define COL_OFF      0x6287e0

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
#define RS485_BAUD 460800
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
// LVGL's two draw buffers ARE the two panel framebuffers, so a flush is a page
// flip and copies nothing; no separate draw buffer is allocated. setup() runs
// them in direct_mode, which clips a repaint to the area that changed.
static lv_disp_draw_buf_t draw_buf;
static uint32_t flushCount = 0;   // frame submissions completed, per GET_DIAG
static volatile uint32_t vsyncCount = 0;
static volatile uint32_t frameDoneCount = 0;
static uint32_t panelDrawErrors = 0;
static uint32_t frameDoneTimeouts = 0;

// ── Big Blue geometry: persistent flavors, selected portrait, task ──
#define RAIL_W          104
#define HERO_W          234
#define TASK_X          (RAIL_W + HERO_W)
#define TASK_W          (SCREEN_W - TASK_X)
#define HEADER_H         62
#define PANE_PAD         25
#define PANE_W          TASK_W
#define PANE_H          (SCREEN_H - HEADER_H - 2 * PANE_PAD)
#define DETAIL_W        (PANE_W - 2 * PANE_PAD)
#define SETTINGS_BTN     64
#define TEXT_H_20        22
#define TEXT_H_28        30
#define TEXT_H_40        44
#define STATUS_REEDS     10
#define RATIO_MIN        FLAVOR_RATIO_MIN
#define RATIO_MAX        FLAVOR_RATIO_MAX
#define TILE_BTN_W       95
#define TILE_BTN_H      194
#define TILE_GAP         10
#define TILE_STRIP_W    DETAIL_W
#define TILE_STRIP_Y     87
static_assert(RAIL_W + HERO_W + TASK_W == SCREEN_W, "Big Blue fills the display");
static_assert(4 * TILE_BTN_W + 3 * TILE_GAP <= DETAIL_W, "four whole portraits per page");

// ── Pages ──
// Every page is built once and lives for the life of the firmware; switching hides one and
// shows another. Sub-views inside a page work the same way.
enum Page { PAGE_HOME, PAGE_FLAVOR, PAGE_SERVICE, PAGE_SETUP, PAGE_COUNT };

enum FlavorView  { FLV_DETAIL, FLV_IMAGES, FLV_COUNT };
enum ServiceView { SVC_PRIME_PICK, SVC_PRIME_HOLD, SVC_CLEAN_PICK,
                   SVC_CLEAN_CONFIRM, SVC_FILL_PICK, SVC_FILL_CONFIRM, SVC_COUNT };
// Settings lands on the system status; each area beside it is a view of its own.
enum SettingsView { SET_STATUS, SET_PUMP, SET_COUNT };

// Stable diagnostic destination IDs. The live rail contains flavor images;
// the three service destinations are the tabs above the task pane.
enum RailPage { RAIL_CHOOSE, RAIL_PRIME, RAIL_FILL, RAIL_CLEAN,
                RAIL_PAGE_COUNT };

static lv_obj_t *pageObj[PAGE_COUNT];
static lv_obj_t *railBtn[RAIL_PAGE_COUNT] = {};
static lv_obj_t *railLabel[RAIL_PAGE_COUNT] = {};
static lv_obj_t *flavorRail, *heroPanel, *heroImage, *heroCaption;
static lv_obj_t *taskHeader, *systemTitle, *doneBtn;
static lv_obj_t *homeTitle, *homeGauge, *homeLevelCaption;
static lv_obj_t *homeLevelSegments[LEVEL_SEGMENTS];
static lv_obj_t *flvTilePosition;
static lv_obj_t *flvTileMark[FLAVOR_IMAGE_COUNT] = {};
static uint8_t imagePage = 0;
static bool operationLockMachine = false;
static bool operationResultVisible = false;
static lv_obj_t *flvView[FLV_COUNT];
static lv_obj_t *svcView[SVC_COUNT];
static lv_obj_t *setView[SET_COUNT];
static Page activePage = PAGE_HOME;
static ServiceView activeSvc = SVC_PRIME_PICK;
static FlavorView  activeFlv = FLV_DETAIL;
static SettingsView activeSet = SET_STATUS;
static RailPage activeRail = RAIL_CHOOSE;
static bool uiReady = false;

static void showPage(Page p);
static void showRail(RailPage p);
static void setRailSelection(RailPage p);
static void showFlavor(FlavorView v);
static void refreshFlavorImages();
static void bindFlavorLogos();
static void tileStripAffordance();
static void tilePickService();
static void tileDisarm();
static void showService(ServiceView v);
static void showSettings(SettingsView v);
static void animRun(bool on);
static void idleReset(uint8_t stage);
static void refreshHomeSelection();
static void refreshHomeLevel();
static void refreshShell();
static bool primeLinkOwnsJ9();
static void primeSessionService();
static void lockScreenShow(const char *kicker, const char *title, const char *body);
static void lockScreenHide();

// ── UI objects ──
static lv_obj_t *lockScreen, *lockLogoImg, *lockKicker, *lockTitle, *lockBody;
static lv_obj_t *lockModal, *lockAccent, *lockFace, *lockBar, *lockNote, *lockStop;
// The camera's test screen: above every page and the lock, for the seconds the main board asked.
static lv_obj_t *testScreen;
static bool testActive = false;
static unsigned long testUntilMs = 0;
static void testScreenShow(uint16_t seconds);
static void testScreenHide();
// Frame pixels live in the `art` partition, mapped through the MMU at boot —
// see firmware/lib/board_art. Null means the partition is absent or holds something this
// build does not recognise, and the lock screen then carries its text alone.
static const uint16_t *animBase = nullptr;
static inline const uint16_t *animFrame(uint8_t i) {
  return animBase ? animBase + (size_t)i * LOGO_SIZE * LOGO_SIZE : nullptr;
}
static lv_img_dsc_t frameDsc[NUM_ANIM_FRAMES];
static lv_timer_t *animTimer = nullptr;
static uint8_t animFrameIdx = 0;
static bool lockActive = false;
static bool bootLockActive = false;

// The lock's modal: the boot lock's own width, and the wider one a channel
// operation takes, out to the animation's edge.
#define LOCK_MODAL_W       360
#define LOCK_MODAL_H       238
#define LOCK_MODAL_MARGIN   26
#define LOCK_MODAL_FILL_W  (SCREEN_W - LOCK_MODAL_MARGIN - (18 + LOGO_SIZE))
#define LOCK_PAD_L          32
#define LOCK_PAD_R          28
#define LOCK_PAD_T          30
#define LOCK_PAD_B          28
#define LOCK_FILL_PAD_L     24
#define LOCK_FACE_GAP       16
#define LOCK_COL_X         (FLAVOR_TILE_W + LOCK_FACE_GAP)
#define LOCK_COL_W         (LOCK_MODAL_FILL_W - LOCK_FILL_PAD_L - LOCK_PAD_R - LOCK_COL_X)
#define LOCK_TITLE_Y        30
#define LOCK_BAR_Y         (LOCK_TITLE_Y + TEXT_H_40 + 14)
#define LOCK_NOTE_Y        (LOCK_BAR_Y + 10 + 8)
#define LOCK_STOP_W        110
#define LOCK_STOP_H         44
static_assert(LOCK_MODAL_FILL_W >= LOCK_MODAL_W, "the channel modal is the wider one");
static_assert(LOCK_MODAL_H - LOCK_PAD_T - LOCK_PAD_B >= FLAVOR_TILE_H, "a face must fit the modal");
static_assert(LOCK_NOTE_Y + TEXT_H_20 <= LOCK_MODAL_H - LOCK_PAD_T - LOCK_PAD_B - LOCK_STOP_H,
              "the note must clear STOP");
static void lockFillLayout(bool on);
static void operationResultShow();
static void pendingOperationShow(const char *kicker, bool machine);
static void fillStopCb(lv_event_t *e);
static void cleanStopCb(lv_event_t *e);
static void airStopCb(lv_event_t *e);
static void lockStopCb(lv_event_t *e);
static unsigned long bootLockMinUntil = 0;
static unsigned long bootLockMaxUntil = 0;

// Which logo each channel wears. Display-local, like the ratio beside it: this
// panel scans an 800x480 framebuffer out of PSRAM, and a flash write suspends
// the cache PSRAM is reached through, so the DMA refilling its bounce buffer
// faults. Nothing on this board writes NVS while the panel runs. The durable
// home for the choice is the main board, which is where the faucet's own
// selection already lives.
static uint8_t flavorImage[2] = {0, 1};
static bool flavorArtAsked = false;

static lv_img_dsc_t flavorAnchor[FLAVOR_IMAGE_COUNT];
static lv_img_dsc_t flavorCard[FLAVOR_IMAGE_COUNT];
static lv_img_dsc_t flavorTile[FLAVOR_IMAGE_COUNT];
static lv_img_dsc_t flavorRailArt[FLAVOR_IMAGE_COUNT];
static lv_img_dsc_t flavorHeroArt[FLAVOR_IMAGE_COUNT];
static lv_img_dsc_t flavorPickerArt[FLAVOR_IMAGE_COUNT];
static uint16_t *scaledPixels[3][FLAVOR_IMAGE_COUNT] = {};

static void bindBigBlueArt() {
  const uint16_t width[3] = {64, 183, 78};
  const uint16_t height[3] = {119, 340, 145};
  lv_img_dsc_t *sets[3] = {flavorRailArt, flavorHeroArt, flavorPickerArt};
  for (uint8_t size = 0; size < 3; ++size) {
    for (uint8_t art = 0; art < FLAVOR_IMAGE_COUNT; ++art) {
      const lv_img_dsc_t &source = flavorAnchor[art];
      const size_t bytes = (size_t)width[size] * height[size] * sizeof(uint16_t);
      uint16_t *&pixels = scaledPixels[size][art];
      if (!pixels) pixels = (uint16_t *)heap_caps_malloc(bytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
      // Retain a complete smaller portrait if PSRAM cannot fit a rendition.
      if (!pixels) { sets[size][art] = flavorTile[art]; continue; }
      const uint16_t *src = (const uint16_t *)source.data;
      for (uint16_t y = 0; y < height[size]; ++y) {
        const uint32_t sy = (uint32_t)y * source.header.h / height[size];
        for (uint16_t x = 0; x < width[size]; ++x)
          pixels[(size_t)y * width[size] + x] =
              src[sy * source.header.w + (uint32_t)x * source.header.w / width[size]];
      }
      sets[size][art] = {};
      sets[size][art].header.cf = LV_IMG_CF_TRUE_COLOR;
      sets[size][art].header.w = width[size];
      sets[size][art].header.h = height[size];
      sets[size][art].data_size = bytes;
      sets[size][art].data = (const uint8_t *)pixels;
      lv_img_cache_invalidate_src(&sets[size][art]);
    }
  }
}
// Every wire rendition is retained, in the shared IMAGE_BUNDLE order. The Big
// Blue display cache is derived after binding and draws without runtime scaling.
static const ImageSize kLogoSizes[] = {
    {FLAVOR_ANCHOR_W, FLAVOR_ANCHOR_H, 0},
    {FLAVOR_CARD_W,   FLAVOR_CARD_H,   0},
    {FLAVOR_TILE_W,   FLAVOR_TILE_H,   0},
};
enum { LOGO_ANCHOR = 0, LOGO_CARD = 1, LOGO_TILE = 2 };

// A picture arrives as one run of bytes and is cut up by this order. Draw order
// and wire order are the same list, so a mismatch is a build error rather than a
// card wearing the bytes of a tile.
static_assert(IMAGE_BUNDLE_COUNT == 3, "this board draws every rendition the bundle carries");
static_assert(IMAGE_BUNDLE[LOGO_ANCHOR].w == FLAVOR_ANCHOR_W &&
              IMAGE_BUNDLE[LOGO_ANCHOR].h == FLAVOR_ANCHOR_H, "anchor");
static_assert(IMAGE_BUNDLE[LOGO_CARD].w == FLAVOR_CARD_W &&
              IMAGE_BUNDLE[LOGO_CARD].h == FLAVOR_CARD_H, "card");
static_assert(IMAGE_BUNDLE[LOGO_TILE].w == FLAVOR_TILE_W &&
              IMAGE_BUNDLE[LOGO_TILE].h == FLAVOR_TILE_H, "tile");

// One rendition of one logo, factory or custom, out of the store. Both kinds are
// slots; which range they sit in is the only difference.
static const uint16_t *flavorArtPixels(uint8_t art, uint8_t rendition) {
  const uint8_t slot = (art < FLAVOR_FACTORY_COUNT) ? flavorArtFactorySlot(art)
                                                    : flavorArtCustomSlot(art);
  if (art >= FLAVOR_FACTORY_COUNT && slot >= FLAVOR_ART_CUSTOM) return nullptr;
  return imageStorePixels(slot, rendition);
}

// Which logo an index resolves to. A custom index whose slot is empty falls
// back to the factory logo of the same channel: a picture can be removed from
// the phone while a channel is still wearing it, and that is a state rather
// than an error.
static uint8_t resolveFlavorArt(uint8_t art, uint8_t channel) {
  if (flavorArtPixels(art, LOGO_ANCHOR)) return art;
  return (uint8_t)(channel & 1);
}

// Whether an index has a picture behind it at all: the factory four while the
// store holds them, a custom one while the phone has put something in its slot.
static bool flavorArtAvailable(uint8_t art) {
  return flavorArtPixels(art, LOGO_ANCHOR) != nullptr;
}

// Every descriptor, at every size. Factory entries point at .rodata; custom
// entries point straight into mapped flash. Both cost a pointer and neither
// costs RAM — and both have to be rebound whenever a slot is written or
// erased, because that remaps the partition underneath them.
// What a descriptor points at while its store slot is empty.
static const uint16_t kNoLogoW = 2, kNoLogoH = 2;
static const uint16_t kNoLogo[kNoLogoW * kNoLogoH] = {0, 0, 0, 0};

static void bindFlavorLogos() {
  struct Bound {
    lv_img_dsc_t *dsc;
    lv_coord_t    w;
    lv_coord_t    h;
    uint8_t       rendition;
  };
  const Bound bound[] = {
      {flavorAnchor, FLAVOR_ANCHOR_W, FLAVOR_ANCHOR_H, LOGO_ANCHOR},
      {flavorCard,   FLAVOR_CARD_W,   FLAVOR_CARD_H,   LOGO_CARD},
      {flavorTile,   FLAVOR_TILE_W,   FLAVOR_TILE_H,   LOGO_TILE},
  };

  for (const Bound &b : bound) {
    for (uint8_t i = 0; i < FLAVOR_IMAGE_COUNT; ++i) {
      b.dsc[i].header.cf = LV_IMG_CF_TRUE_COLOR;
      b.dsc[i].header.always_zero = 0;
      const uint16_t *px = flavorArtPixels(i, b.rendition);
      if (!px) px = flavorArtPixels(0, b.rendition);
      // Every descriptor carries pixels LVGL can read. A store with no face in
      // it yet gets the placeholder's own geometry, not the rendition's, so
      // nothing reads past the four words behind it.
      if (px) {
        b.dsc[i].header.w = b.w;
        b.dsc[i].header.h = b.h;
        b.dsc[i].data_size = (uint32_t)b.w * b.h * sizeof(uint16_t);
        b.dsc[i].data = (const uint8_t *)px;
      } else {
        b.dsc[i].header.w = kNoLogoW;
        b.dsc[i].header.h = kNoLogoH;
        b.dsc[i].data_size = sizeof(kNoLogo);
        b.dsc[i].data = (const uint8_t *)kNoLogo;
      }
    }
  }
  bindBigBlueArt();
}

// A channel is named by the logo it wears. Some images always show one
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
static lv_obj_t *flvTileBtn[FLAVOR_IMAGE_COUNT];
static lv_obj_t *flvTileStrip = NULL;
static lv_obj_t *flvTileLeft = NULL, *flvTileRight = NULL;
static lv_obj_t *flvTileLeftMark = NULL, *flvTileRightMark = NULL;
static lv_obj_t *flvTileTrack = NULL, *flvTileThumb = NULL;
static lv_obj_t *homeFlavorCard[2];
static lv_obj_t *homeFlavorRatio[2];

// ── Reservoir level, as the main board reads it ──
// Status carries both reed-derived levels. On tap shows the selected reservoir.
static lv_obj_t *homeFlavorLevelCap[2];
static lv_obj_t *homeFlavorLevelSeg[2][LEVEL_SEGMENTS];
// A pour at the faucet: the card of the channel injecting says so over its
// ratio for as long as the water flows.
static lv_obj_t *homeFlavorRatioCap[2];
static int8_t    pouringShown = -1;
static uint8_t   levelSegments[2] = {LEVEL_UNKNOWN, LEVEL_UNKNOWN};
static bool      levelValid = false;

// What each channel pours at is the main board's: a step here states the
// pair and takes back what it holds; while that answer is owed, the status
// poll's copy is not allowed to put the old number back.
static unsigned long ratioSentMs = 0;
#define RATIO_REPLY_MS 2500
static lv_obj_t *homeFlavorBadge[2];
static lv_obj_t *homeFlavorBadgeText[2];

// Render selection only when it changes. Routine main-board replies leave the
// rail, portrait and gauge's cached visible state alone.
static int8_t homeFlavorShown = -2;

static lv_obj_t *flvDetailRatio;
static lv_obj_t *flvRatioMinus = NULL, *flvRatioPlus = NULL;
static lv_obj_t *flvRatioMinusMark = NULL, *flvRatioPlusMark = NULL;
static lv_obj_t *primePad, *primePadLbl, *primeMsg;
static lv_indev_t *touchInput = nullptr;
static lv_obj_t *cleanMsg, *fillMsg;

// ── The funnel fill, as this glass shows it ──
// The main board owns the run; this holds its last word about it, and the lock
// it is shown on. START is answered with the state it produced, and while the
// lock is up the state is asked for again every FILL_QUERY_MS, so the ending
// cannot be missed and a fill the console started is shown the same way.
static FillStatePayload fillState = {};
static bool          fillKnown = false;         // fillState is a main board answer
static bool          fillLockShown = false;     // the operation lock is up for a fill
static bool          fillStopSent = false;      // STOP is out; the pad says so
static unsigned long fillAnchorMs = 0;          // when fillState.elapsedMs was true
static unsigned long fillStartSentMs = 0;       // nonzero: START is out and unanswered
static unsigned long fillQueryMs = 0;
static unsigned long fillUiMs = 0;
static unsigned long fillCardUntilMs = 0;       // nonzero: the closing card is up until then
#define FILL_QUERY_MS        500
#define FILL_START_REPLY_MS  2500
#define FILL_CARD_MS         6000

// ── The clean cycle, as this glass shows it ──
// The same shape as the fill: the main board owns the cycle, this holds its
// last word about it and the lock it is shown on, and asks again every
// CLEAN_QUERY_MS while the lock is up.
static CleanStatePayload cleanState = {};
static bool          cleanKnown = false;
static bool          cleanLockShown = false;
static bool          cleanStopSent = false;
static unsigned long cleanAnchorMs = 0;         // when cleanState's elapsed and left were true
static unsigned long cleanStartSentMs = 0;      // nonzero: START is out and unanswered
static unsigned long cleanQueryMs = 0;
static unsigned long cleanUiMs = 0;
static unsigned long cleanCardUntilMs = 0;      // nonzero: the closing card is up until then
#define CLEAN_QUERY_MS        FILL_QUERY_MS
#define CLEAN_START_REPLY_MS  FILL_START_REPLY_MS
#define CLEAN_CARD_MS         FILL_CARD_MS

// ── The air cycles, as this glass shows it ──
// Dry is started from Settings before a pump replacement; a purge is the
// console's. Both are shown on the lock the way the clean cycle is.
static AirStatePayload airState = {};
static bool          airKnown = false;
static bool          airLockShown = false;
static bool          airStopSent = false;
static unsigned long airAnchorMs = 0;
static unsigned long airStartSentMs = 0;
static unsigned long airQueryMs = 0;
static unsigned long airUiMs = 0;
static unsigned long airCardUntilMs = 0;
static lv_obj_t *settingsMsg = NULL;   // the pump service card's own message line
static lv_obj_t *settingsBtn;      // bottom of the persistent flavor rail

// ── System status, as this glass shows it ──
// Ten reeds on the machine's own side profile: reservoir A's four, reservoir
// B's four, the carbonator's low and high. Each is a ring until the main board
// says it is closed, then a filled disc. Index 0..3 is reservoir A's empty..full
// reed, 4..7 reservoir B's, 8 the carbonator's low reed and 9 its high one.
static lv_obj_t *statusReed[STATUS_REEDS];
static lv_obj_t *statusNote = NULL;    // under the card: that nothing is being read, else empty
static bool statusSimShown = false;
static uint16_t  statusShown = 0;      // the closed set the diagram is drawn with
static bool      statusFreshShown = false;
#define STATUS_ANSWER_MS 1500          // a status poll unanswered this long is a main board not reading

// The bytes of StatusPayload every main board sends, whatever else it appends.
#define STATUS_CORE_BYTES 32

// ── The cold loop and the refill, in the column beside the profile ──
// Two probes on the 1-wire bus — the carbonator wall and the coil's suction end
// — the state each of the two loops stands in, and how many devices answered
// the bus. Five lines, label and value, filling the card's right-hand column.
#define STATUS_THERMAL_ROWS 5
static lv_obj_t *statusThermalValue[STATUS_THERMAL_ROWS] = {NULL};

// The reading the column is drawn with. `drawn` is false until the first pass,
// so the placeholders the builder leaves are replaced on the first answer.
static struct {
  int16_t tank;
  int16_t coil;
  uint8_t cold;
  uint8_t refill;
  uint8_t probes;
  bool    fresh;
  bool    drawn;
} statusThermalShown = {};

// Both ratios are mirrored from the main board's persistent configuration.
static uint8_t flavorRatio[2] = {20, 20};
static uint8_t flavorSel = PUMP_CHANNEL_B;   // which flavor the detail and hold pages act on

// The flavor used for dispensing is separate from flavorSel above, which is
// only the target currently open in a service/configuration view. The
// main board owns this value; the enclosure applies a press optimistically and
// reconciles it from MSG_RESP_FLAVOR_STATE.
static uint8_t activeFlavor = PUMP_CHANNEL_A;
static bool flavorSynchronized = false;
static bool flavorMainBoardPersisted = false;
static bool flavorMainBoardPersistError = false;
static bool flavorRequestPending = false;
static bool flavorQueryOutstanding = false;
static unsigned long idleAskedMs = 0;
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
#define IDLE_REASK_MS               5000
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
// The quiet stretch before dark is the main board's, counted across both
// glasses. Nothing here runs a timer of its own.
#define KEEP_VIEW_MS     120000   // dark -> the root of the page you were on
#define KEEP_AREA_MS     600000   // dark -> Choose

static unsigned long lastInputTime = 0;
static unsigned long darkSince = 0;
static bool idleAsleepKnown = false;   // the main board has said, at least once
static bool idleAsleepWanted = false;  // what it last said
static uint32_t idleWindowMs = 0;      // the window it is counting against
static uint8_t idleStage = 0;    // 0 lit · 1 dark · 2 at the page's root · 3 Choose
static bool screenIdle = false;  // true while asleep (backlight off via idle)

// A finger here is presence the main board has to hear. It keeps the one clock
// for both glasses, so a touch it never learns of leaves the other glass dark
// and this one about to follow it back down. MSG_TOUCH is a single frame into a
// half-duplex pair that may be mid-repair, so it is retried rather than sent
// once — and until an idle publication comes back agreeing this board is awake,
// the dark is held off. Otherwise the sleep the main board published before it
// heard the touch arrives afterward and undoes the wake, which reads at the
// glass as a screen that turns itself off a few seconds after being tapped.
static unsigned long touchUnconfirmedSince = 0;   // 0 when the main board agrees
static unsigned long touchConfirmRetryMs = 0;
#define TOUCH_CONFIRM_RETRY_MS   750
#define TOUCH_CONFIRM_GIVEUP_MS  10000

// ── Touch (GT911) ──
static uint8_t gt911Addr = 0;     // probed at init (0 = not found)
static uint32_t touchCount = 0;   // diagnostics: presses seen since last GET_DIAG
static uint16_t lastTouchX = 0, lastTouchY = 0;  // where the last press landed
// Where the finger is now, and whether it is still down. The press point alone
// cannot tell a tap from the beginning of a drag, and inside a scrollable strip
// that is the whole difference between choosing a picture and looking at the
// next one.
static uint16_t curTouchX = 0, curTouchY = 0;
static bool     touchIsDown = false;
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
// VSYNC_END starts the 8-line back porch, about 410 us at the panel timing.
// The shared I2C bus runs at 400 kHz, so keep the CH422G write inside the first
// 300 us and retry next frame if the task did not start promptly.
#define PANEL_VSYNC_ACTION_WINDOW_US 300
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
  if (result != 0) exioWriteErrors = exioWriteErrors + 1;
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
  Wire.setClock(400000);  // CH422G and GT911 both support Fast-mode I2C
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
    panelVsyncActionsQueued = panelVsyncActionsQueued + 1;
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
      panelVsyncLateRetries = panelVsyncLateRetries + 1;
      continue;
    }

    // Waiting here would make an expander write land after the blank. Give the
    // touch transaction the current frame, then retry at the next VSYNC.
    if (!i2cTake(0)) {
      panelVsyncBusRetries = panelVsyncBusRetries + 1;
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
      panelVsyncLateRetries = panelVsyncLateRetries + 1;
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
      panelVsyncWriteErrors = panelVsyncWriteErrors + 1;
      continue;
    }

    portENTER_CRITICAL(&panelVsyncActionMux);
    if (panelVsyncAction == action) {
      panelVsyncAction = PANEL_VSYNC_NONE;
      panelVsyncActionDone = true;
      panelVsyncActionsDone = panelVsyncActionsDone + 1;
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
  // Waveshare's 800x480 ST7262 timing. HSYNC and VSYNC idle high (their zeroed
  // flag state), while pixels are latched on the falling PCLK edge.
  cfg.timings.pclk_hz = 16 * 1000 * 1000;
  cfg.timings.h_res = SCREEN_W;
  cfg.timings.v_res = SCREEN_H;
  cfg.timings.hsync_pulse_width = 4;
  cfg.timings.hsync_back_porch  = 8;
  cfg.timings.hsync_front_porch = 8;
  cfg.timings.vsync_pulse_width = 4;
  cfg.timings.vsync_back_porch  = 8;
  cfg.timings.vsync_front_porch = 8;
  cfg.timings.flags.pclk_active_neg = 1;  // 4.3B: data latched on the falling edge
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

// This tree's local RGB driver preserves DMA state through normal VSYNCs. Buffer
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
  // A finger has landed and the main board is being told. Take the awake state
  // now rather than holding the sleep it last published: waiting out that round
  // trip lets the loop below put the panel straight back into the dark this
  // call just left, and the answer then arrives as a second wake.
  idleAsleepWanted = false;
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

// Every press edge, including one that only wakes the glass or lands on nothing.
// The main board keeps the clock for both glasses; this is what it counts.
static bool touchPending = false;

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
      touchPending = true;
      touchWakesOnly = screenIdle || !backlightOn;
      lastTouchX = x;
      lastTouchY = y;
      Serial.printf("[touch] x=%u y=%u  status=0x%02X raw=%02X %02X %02X %02X %02X %02X %02X %02X%s\n",
                    x, y, lastStatus, lastRaw[0], lastRaw[1], lastRaw[2], lastRaw[3],
                    lastRaw[4], lastRaw[5], lastRaw[6], lastRaw[7],
                    touchWakesOnly ? " (dark — wakes only)" : "");
    }
    bridgedRun = 0;
    curTouchX = x;
    curTouchY = y;
    touchIsDown = true;
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
    touchIsDown = false;
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
  if (!animBase) return;   // no art partition: the lock screen is its text
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
// The main board answers a frame the instant it lands — from inside its receive
// callback — so a second frame sent from here before that answer has come back
// lands on top of it. The main board hears its own transmissions (U7's /RE is
// grounded on the main board) and cancels them by matching the echo; a frame of ours
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
              "main board prime replay ledger must cover the complete J9 queue");

static OutFrame      outQ[OUT_Q_DEPTH];
static uint8_t       outHead = 0, outTail = 0, outCount = 0;
static uint8_t       outHighWater = 0;
static uint32_t      outDropped = 0;
static unsigned long lastTxMs = 0;
static bool          awaitingAnswer = false;

// The pair goes quiet while this glass is dark, and dark is when the main board
// most needs it: it never speaks unprompted, so everything it has to say waits
// for a turn this board's poll gives it. A transport that fails while nobody is
// looking therefore silences the machine rather than only this screen — the
// faucet can be touched, the flavor changed, the idle clock run out and back,
// and none of it arrives. Nothing here recovers on its own either, because a
// dark glass is not being asked to.
//
// So the watchdog is armed by a transmission rather than by a screen: the first
// frame sent into a silence starts the clock, anything arriving stops it. What
// is being polled, and whether the backlight is on, stop mattering.
static unsigned long j9SilentSinceMs = 0;   // 0 when the far end is answering
#define J9_SILENT_MS 3000

static bool          holding = false;

// ── Firmware arriving over J9 ─────────────────────────────────────────────
// This board cannot write its own flash with the panel running. The scan-out
// DMA refills its bounce buffer from PSRAM, a flash write suspends the cache
// PSRAM is reached through, and the refill then faults — the same reason the
// logo choice is kept on the main board rather than in local NVS.
//
// So an update here is deliberately a blind operation: the glass says what is
// about to happen, the panel is stopped, the image comes down dark, and the
// board reboots whatever the outcome. A failed transfer costs a reboot into
// the image it was already running, which is the same image it would have kept
// anyway.
static OtaReceiver ota;
// The factory logos go into store slots rather than into a partition of their
// own, so they are taken by a sink of their own. One session uses one of the two.
static LogosSink logos;
static bool otaIsLogos = false;

static inline bool     otaAnyActive()  { return otaIsLogos ? logos.active() : ota.active(); }
static inline uint32_t otaAnyNext()    { return otaIsLogos ? logos.nextOffset() : ota.nextOffset(); }
static inline uint32_t otaAnyExpected(){ return otaIsLogos ? logos.expected : ota.expected; }
static inline bool     otaAnyWrite(uint32_t off, const uint8_t *d, uint16_t n) {
  return otaIsLogos ? logos.write(off, d, n) : ota.write(off, d, n);
}
static inline void otaAnyFinish() { if (otaIsLogos) logos.finish(); else ota.finish(); }
static inline void otaAnyAbort()  { if (otaIsLogos) logos.abort();  else ota.abort(); }
static inline void otaAnyFill(OtaStatePayload &st) {
  if (otaIsLogos) logos.fill(st); else ota.fill(st);
}

static unsigned long otaAskedAtMs = 0;
static bool otaPanelStopped = false;
static bool otaRebootPending = false;
static unsigned long otaRebootAtMs = 0;
static const unsigned long OTA_REASK_MS = 40;
static unsigned long otaLastDataMs = 0;
// When a byte of the image last arrived. otaLastDataMs below is reset by this
// end's own recovery, so it measures the asking rather than the transfer; this
// one is moved only by the relay, and is what says the source still exists.
static unsigned long otaLastProgressMs = 0;
// How long a transfer may carry nothing before this board stops waiting on it.
//
// Longer than the 600 s the relay holds a session for, so a session that is
// still alive always ends from that end: the relay gives up, sends the abort,
// and this board reboots on it. What is left for this clock is the session that
// died with its board, where no abort is ever coming and nothing else would
// turn the panel back on.
//
// A source can go quiet for minutes and still return — a phone that answered
// again after 184 s is what set this number — and a clock shorter than the
// relay's turns one of those into a failed update.
static const unsigned long OTA_SILENCE_MS = 900000;

static void j9Post(uint8_t type, const void *data, uint8_t len);
static bool setBacklight(bool on);
static void j9Reinit(const char *why);

static void otaStopPanel() {
  if (otaPanelStopped) return;
  otaPanelStopped = true;
  setBacklight(false);
  // Deleted, not blanked. disp_on_off only stops light reaching the glass; the
  // scan-out DMA keeps refilling its bounce buffer out of PSRAM, and a flash
  // erase suspends the cache that reaches PSRAM. Tearing the panel down stops
  // the DMA and its ISR. Nothing draws after this — the board reboots either
  // way — so there is nothing to restore.
  if (panel) {
    esp_lcd_panel_del(panel);
    panel = nullptr;
  }
}

// The radio bench takes the panel down through here. Same teardown an arriving
// image uses and for the same reason, with its own banner: this glass is dark
// for the length of the run and comes back on the reboot that ends it.
// A picture that just landed remapped the partition every logo descriptor
// points into.
void wifiBenchRebind() {
  bindFlavorLogos();
}

// This is the last thing anyone sees before the glass goes dark, so it says
// what is about to happen in the words of whoever caused it. Someone who just
// chose a photograph on their phone is not looking at a radio bench.
void wifiBenchPanelStop(bool forPicture) {
  if (lockTitle) {
    lockActive = true;
    if (lockScreen) lv_obj_move_foreground(lockScreen);
    lv_label_set_text(lockTitle, forPicture ? "NEW PICTURE" : "RADIO BENCH");
    if (lockBody)
      lv_label_set_text(lockBody,
                        forPicture
                            ? "Saving the picture you chose.\nThe screen comes back on its own."
                            : "The screen goes dark while the radio is up.\nIt restarts on its own when the run ends.");
    if (lockScreen) lv_obj_clear_flag(lockScreen, LV_OBJ_FLAG_HIDDEN);
    for (int i = 0; i < 24; i++) { lv_timer_handler(); delay(25); }
  }
  otaStopPanel();
}

static void otaAsk() {
  OtaReqPayload req{otaAnyNext()};
  j9Post(MSG_OTA_REQ, &req, sizeof(req));
  otaAskedAtMs = millis();
}

static void otaReport() {
  OtaStatePayload st;
  otaAnyFill(st);
  j9Post(MSG_RESP_OTA, &st, sizeof(st));
}

static void otaBanner() {
  if (!lockTitle) return;
  lockActive = true;
  if (lockScreen) lv_obj_move_foreground(lockScreen);
  lv_label_set_text(lockTitle, "UPDATING");
  if (lockBody) lv_label_set_text(lockBody, "The screen goes dark while the new firmware is written.\nDo not cut power. It restarts on its own.");
  if (lockScreen) lv_obj_clear_flag(lockScreen, LV_OBJ_FLAG_HIDDEN);
  for (int i = 0; i < 40; i++) { lv_timer_handler(); delay(25); }   // let it render and be read
}

static void otaOnFrame(uint8_t type, const uint8_t *payload, uint16_t plen) {
  if (type == MSG_OTA_ABORT) { otaAnyAbort(); otaRebootPending = true; otaRebootAtMs = millis() + 200; return; }

  if (type == MSG_OTA_BEGIN && plen >= sizeof(OtaBeginPayload)) {
    OtaBeginPayload b;
    memcpy(&b, payload, sizeof(b));
    otaBanner();
    otaStopPanel();
    otaLastDataMs = otaLastProgressMs = millis();
    otaIsLogos = (b.kind == OTA_KIND_LOGOS);
    if (otaIsLogos) logos.begin(b.size, b.crc32);
    else            ota.begin(b.size, b.crc32, b.kind);
    otaReport();
    if (otaAnyActive()) otaAsk();
    else { otaRebootPending = true; otaRebootAtMs = millis() + 200; }
    return;
  }

  if (type == MSG_OTA_DATA && plen >= 4 && otaAnyActive()) {
    otaLastDataMs = otaLastProgressMs = millis();
    uint32_t offset;
    memcpy(&offset, payload, 4);
    if (!otaAnyWrite(offset, payload + 4, (uint16_t)(plen - 4))) {
      otaReport();
      otaRebootPending = true;
      otaRebootAtMs = millis() + 200;
      return;
    }
    if (otaAnyNext() < otaAnyExpected()) { otaAsk(); return; }
    otaAnyFinish();
    otaReport();
    otaRebootPending = true;
    otaRebootAtMs = millis() + 600;   // let the reply clear the pair
    return;
  }
}

static void otaService() {
  if (otaRebootPending && (long)(millis() - otaRebootAtMs) >= 0) esp_restart();
  if (!otaAnyActive()) return;

  // A source that has stopped existing. The recovery below sets its own clock
  // each time it fires, so on its own it asks a dead pair forever, with the
  // panel torn down and the backlight off. The abort that ends a transfer is
  // sent only by a relay session that still holds one.
  if (millis() - otaLastProgressMs >= OTA_SILENCE_MS) {
    otaAnyAbort();
    otaRebootPending = true;
    otaRebootAtMs = millis();
    return;
  }

  // A transfer owns the loop, which means it also owns the link's recovery.
  // The pair can wedge mid-session with this end still sending — the failure
  // j9Reinit exists for — and the poll that normally notices is one of the
  // things being skipped. Without this the transfer simply stops, with the
  // main board still holding the chunk nobody asks for any more.
  if (millis() - otaLastDataMs >= 2000) {
    otaLastDataMs = millis();
    j9Reinit("no OTA data for 2s");
    otaAsk();
    return;
  }

  if (millis() - otaAskedAtMs >= OTA_REASK_MS) otaAsk();
}

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
  // The first frame into a silence dates it. Later ones do not move the mark:
  // the question is how long the far end has been unreachable, not how much
  // has been said into it since.
  if (!j9SilentSinceMs) j9SilentSinceMs = lastTxMs ? lastTxMs : 1;
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

  flavorMainBoardPersisted = (state.flags & FLAVOR_STATE_F_PERSISTED) != 0;
  flavorMainBoardPersistError = (state.flags & FLAVOR_STATE_F_PERSIST_ERROR) != 0;
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

  // A changed faucet selection dismisses flavor tasks and leaves machine pages open.
  if (changed && !lockActive) {
    if (front_ui::dismissForFaucetChange(activePage == PAGE_SETUP, changed, lockActive)) {
      showPage(PAGE_HOME);
    }
    if (screenIdle) wake();
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
  // The artwork is asked for once: the main board republishes every change to
  // it, and a change is a thing someone did rather than a clock running out.
  if (!flavorArtAsked) {
    j9Post(MSG_FLAVOR_ART_QUERY, nullptr, 0);
    flavorArtAsked = true;
  }
  // Idle is asked for again, slowly and forever. It is the one piece of main
  // board truth that moves with no one touching anything, and the announcement
  // carrying it has to win a turn against a four-deep queue and a pair that may
  // be under repair. Missing one is how a lit pair goes dark, or a dark one
  // stays dark through a finger on the other glass; asking again is what puts a
  // ceiling on how long either lasts.
  if (now - idleAskedMs >= IDLE_REASK_MS) {
    idleAskedMs = now;
    j9Post(MSG_IDLE_QUERY, nullptr, 0);
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
// Whether the last frame carried the thermal tail. A main board sending the
// 32-byte core alone reports no cold loop, which is not the same as a cold loop
// reading Off with no probes.
static bool ctrlStatusThermal = false;

static uint32_t linkReinits = 0;
static uint32_t padMux[2] = {0, 0}, padOut[2] = {0, 0};

// A prime hold: the finger is down on the pad and ticks are going out under it. holdAckMs
// stays 0 until MSG_RESP_PRIME{RUNNING} lands, which is the difference between a motor
// turning and a frame sent into a bus with nothing on it.
static unsigned long holdStartMs = 0, holdTickMs = 0, holdAckMs = 0;
static bool holdRetried = false;

// Prime-ready is an appliance session, not a page-local pump command. The
// main board owns this complete state and mirrors it to both pieces of glass.
// This display owns only its desired session state and one physical press.
static PrimeSessionStatePayload primeSession = {};
static bool primeSessionKnown = false;
static bool primeSessionDesired = false;
static bool primeSessionCancelPending = false;
static bool primeBootDiscovery = true;
static bool primeStopPending = false;
static bool primeAuthoritativeNavigation = false;
static bool primeUsbStartPending = false;
// A press that arrives while the session is still opening. No hold frame
// leaves until the main board answers READY; this is the press that waits.
static bool primeTouchStartPending = false;
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
static void applyFillState(const FillStatePayload &state);
static void applyCleanState(const CleanStatePayload &state);
static void applyAirState(const AirStatePayload &state);
static void setSettingsMsg(const char *s);
static void refreshHomeLevel();
static void refreshStatusReeds();
static void refreshStatusThermal();
static void refreshFlavorText();
static bool uiShow(const UiShowPayload &req);

static void j9OnMessage(HdlcLink *link, const uint8_t *frame, uint16_t len) {
  awaitingAnswer = false;   // the main board has spoken; the wire is ours again


  (void)link;
  uint8_t type = msgType(frame);
  const uint8_t *payload = msgPayload(frame);
  uint16_t plen = msgPayloadLen(len);
  char buf[64];

  j9SilentSinceMs = 0;   // anything arriving says the far end is still hearing us

  if (type == MSG_OTA_BEGIN || type == MSG_OTA_DATA || type == MSG_OTA_ABORT) {
    otaOnFrame(type, payload, plen);
    return;
  }

  // The main board assembles what the whole machine is running; this is this
  // board's line of it.
  if (type == MSG_VERSION_QUERY) {
    VersionPayload v{OTA_TGT_ENCLOSURE, {0}, 0, FW_BUILD_EPOCH};
    strncpy(v.version, FW_VERSION, FW_VERSION_MAX);
    BoardArtHeader h;
    if (boardArtHeader(h) && h.magic == BOARD_ART_MAGIC) v.artCrc32 = h.crc32;
    j9Post(MSG_RESP_VERSION, &v, sizeof(v));
    return;
  }

  // The radio bench. This board is the sink; the answer goes out in the same
  // turn, because the main board asked for it and is waiting on that reply.
  if (type == MSG_WIFI_BENCH_AP && plen >= sizeof(WifiApPayload)) {
    WifiApPayload ap;
    memcpy(&ap, payload, sizeof(ap));
    // 0 drops it, 1 raises it with the panel taken down, 2 only asks,
    // 3 raises it with the panel left running, 4 raises it for a picture —
    // same teardown as 1, and the banner someone who chose a photograph reads.
    switch (ap.on) {
      case 0: wifiBenchApSet(false, ap.channel, false); break;
      case 1: wifiBenchApSet(true,  ap.channel, false); break;
      case 3: wifiBenchApSet(true,  ap.channel, true);  break;
      case 4: wifiBenchApSet(true,  ap.channel, false, true); break;
      default: break;   // 2 asks without moving it
    }
    WifiApStatePayload st;
    wifiBenchFill(st);
    j9Post(MSG_RESP_WIFI_AP, &st, sizeof(st));
    // This board has no console inside the appliance, so how far the radio got
    // rides back on the pair beside the state it produced.
    if (!st.up) {
      char diag[40];
      wifiBenchDiag(diag, sizeof(diag));
      j9Post(MSG_TEXT, diag, (uint8_t)strlen(diag));
    }
    return;
  }

  if (type == MSG_IMAGE_ERASE && plen >= sizeof(ImageSlotPayload)) {
    ImageSlotPayload req;
    memcpy(&req, payload, sizeof(req));
    if (imageStoreErase(req.slot)) {
      bindFlavorLogos();
      if (uiReady) refreshFlavorImages();
    }
    return;
  }

  if (type == MSG_IMAGES_QUERY) {
    const bool verbose = plen >= sizeof(ImagesQueryPayload) ? payload[0] != 0 : true;
    ImagesPayload im{};
    im.board = OTA_TGT_ENCLOSURE;
    im.slots = imageStoreCapacity() < FLAVOR_ART_CUSTOM
                   ? imageStoreCapacity() : FLAVOR_ART_CUSTOM;
    im.bundleBytes = imageStoreBundleBytes();
    for (uint8_t i = 0; i < im.slots; i++) {
      if (imageStoreOccupied(i)) { im.occupancy |= (uint8_t)(1u << i); ++im.held; }
      im.crc[i] = imageStoreCrc(i);   // what this board's copy actually is
    }
    j9Post(MSG_RESP_IMAGES, &im, sizeof(im));
    if (!verbose) return;
    // This board has no console; how the last picture landed rides back beside
    // the count, which is the question anyone asking the count actually has.
    char diag[40];
    wifiBenchPictureDiag(diag, sizeof(diag));
    j9Post(MSG_TEXT, diag, (uint8_t)strlen(diag));
    return;
  }

  if (type == MSG_RESP_FILL && plen >= sizeof(FillStatePayload)) {
    FillStatePayload st;
    memcpy(&st, payload, sizeof(st));
    applyFillState(st);
    return;
  }

  if (type == MSG_RESP_CLEAN && plen >= sizeof(CleanStatePayload)) {
    CleanStatePayload st;
    memcpy(&st, payload, sizeof(st));
    applyCleanState(st);
    return;
  }

  if (type == MSG_RESP_AIR && plen >= sizeof(AirStatePayload)) {
    AirStatePayload st;
    memcpy(&st, payload, sizeof(st));
    applyAirState(st);
    return;
  }

  if (type == MSG_UI_SHOW && plen >= sizeof(UiShowPayload)) {
    UiShowPayload req;
    memcpy(&req, payload, sizeof(req));
    const bool shown = uiShow(req);
    link->sendResponse(MSG_RESP_UI_SHOW, shown ? 1 : 0);
    return;
  }

  if (type == MSG_TEST_SCREEN && plen >= sizeof(TestScreenPayload)) {
    TestScreenPayload req;
    memcpy(&req, payload, sizeof(req));
    if (uiReady) testScreenShow(req.seconds);
    link->sendResponse(MSG_RESP_TEST_SCREEN, uiReady && req.seconds ? 1 : 0);
    return;
  }

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

  if (type == MSG_RESP_IDLE && plen >= sizeof(IdlePayload)) {
    IdlePayload idle;
    memcpy(&idle, payload, sizeof(idle));
    idleAsleepKnown = true;
    idleWindowMs = idle.windowMs;
    idleAsleepWanted = idle.asleep != 0;
    // An awake state is the main board answering for the touch: it only leaves
    // sleep when a finger has been reported to it, on either glass. A sleep
    // state proves nothing about ours, so it does not close the question.
    if (!idleAsleepWanted) touchUnconfirmedSince = 0;
    // Waking is immediate; going dark waits for the loop, where a live hold or
    // an operation lock can still hold it off.
    if (!idleAsleepWanted && screenIdle) wake();
    return;
  }

  if (type == MSG_RESP_RATIO && plen >= sizeof(RatioPayload)) {
    RatioPayload r;
    memcpy(&r, payload, sizeof(r));
    ratioSentMs = 0;
    bool moved = false;
    for (uint8_t i = 0; i < 2; i++) {
      if (r.ratio[i] >= RATIO_MIN && r.ratio[i] <= RATIO_MAX && flavorRatio[i] != r.ratio[i]) {
        flavorRatio[i] = r.ratio[i];
        moved = true;
      }
    }
    if (moved && uiReady) refreshFlavorText();
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
  // though the production service UI uses the main-board-owned session above.
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
      case PRIME_TIMEOUT: snprintf(buf, sizeof(buf), "main board lost the hold"); break;
      case PRIME_LIMIT:   snprintf(buf, sizeof(buf), "stopped at the %lu s ceiling",
                                   (unsigned long)(PRIME_MAX_MS / 1000)); break;
      default:            snprintf(buf, sizeof(buf), "main board refused"); break;
    }
    setPrimeMsg(buf);
    return;
  }

  // The frame carries the 32-byte core every main board has always sent, and
  // whatever a newer one appends after it. A frame at or above that core is
  // read: the bytes that arrived are taken, the fields behind them stand at
  // zero, and the two temperatures stand at TEMP_UNREAD rather than at 0 C. The
  // gauges, the reed diagram, the ratio mirror and the pouring caption are all
  // in the core, so a main board that has not grown the tail still draws them.
  if (type == MSG_RESP_STATUS && plen >= STATUS_CORE_BYTES) {
    ctrlStatus = StatusPayload{};
    const size_t taken = plen < sizeof(ctrlStatus) ? (size_t)plen : sizeof(ctrlStatus);
    memcpy(&ctrlStatus, payload, taken);
    if (taken < offsetof(StatusPayload, coldState)) {
      ctrlStatus.tankCx10 = TEMP_UNREAD;
      ctrlStatus.coilCx10 = TEMP_UNREAD;
    }
    ctrlStatusThermal = taken >= sizeof(ctrlStatus);
    ctrlStatusMs = millis();
    // The gauges, and — unless a step of this glass's is still unanswered —
    // what each channel pours at.
    const bool valid = (ctrlStatus.levelFlags & LEVEL_F_VALID) != 0;
    if (valid != levelValid || ctrlStatus.level[0] != levelSegments[0] ||
        ctrlStatus.level[1] != levelSegments[1]) {
      levelValid = valid;
      levelSegments[0] = ctrlStatus.level[0];
      levelSegments[1] = ctrlStatus.level[1];
      refreshHomeLevel();
    }
    refreshStatusReeds();
    refreshStatusThermal();
    if (!ratioSentMs) {
      bool moved = false;
      for (uint8_t i = 0; i < 2; i++) {
        const uint8_t r = ctrlStatus.ratio[i];
        if (r >= RATIO_MIN && r <= RATIO_MAX && flavorRatio[i] != r) { flavorRatio[i] = r; moved = true; }
      }
      if (moved && uiReady) refreshFlavorText();
    }
    const int8_t pouring = (ctrlStatus.flags & STATUS_F_POURING) ? (int8_t)(ctrlStatus.primeChannel & 1) : -1;
    if (pouring != pouringShown) {
      pouringShown = pouring;
      for (uint8_t i = 0; i < 2; i++) {
        if (!homeFlavorRatioCap[i]) continue;
        const bool on = pouring == (int8_t)i;
        lv_label_set_text(homeFlavorRatioCap[i], on ? "Pouring." : "On tap.");
        lv_obj_set_style_text_color(homeFlavorRatioCap[i], lv_color_hex(on ? COL_ACCENT : COL_DIM), 0);
      }
    }
    refreshHomeLevel();
    // A fill this glass did not start — the console's, or one whose answer
    // lost its turn — is still the machine being busy, and is shown as such.
    if ((ctrlStatus.flags & STATUS_F_FILLING) && !fillLockShown && !fillStartSentMs)
      j9Post(MSG_FILL_QUERY, nullptr, 0);
    if ((ctrlStatus.flags & STATUS_F_CLEANING) && !cleanLockShown && !cleanStartSentMs)
      j9Post(MSG_CLEAN_QUERY, nullptr, 0);
    if ((ctrlStatus.flags & STATUS_F_AIRING) && !airLockShown && !airStartSentMs)
      j9Post(MSG_AIR_QUERY, nullptr, 0);
    return;
  }

  if (type == MSG_ERR_UNSUPPORTED) {
    // The commissioning main board explicitly refuses the requested subsystem.
    if (fillStartSentMs) {
      fillStartSentMs = 0;
      lockScreenHide();
      setFillMsg("this main board has no fill");
    } else if (cleanStartSentMs) {
      cleanStartSentMs = 0;
      lockScreenHide();
      setCleanMsg("this main board has no clean cycle");
    } else if (airStartSentMs) {
      airStartSentMs = 0;
      lockScreenHide();
      setSettingsMsg("this main board has no air cycle");
    }
    Serial.println("[J9] MSG_ERR_UNSUPPORTED");
    return;
  }

  if (type == MSG_ERR_BUSY) {
    setPrimeMsg("main board busy");
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
  // 8 KB, because the loop does not always come back quickly: a flash sector
  // erase inside esp_ota_write blocks for tens of milliseconds, and at these
  // rates that is thousands of bytes arriving with nobody draining them. The
  // default 256-byte ring overflows and the frame is simply lost — which
  // looks exactly like a link that has stopped talking.
  Serial1.setRxBufferSize(8192);
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
  j9SilentSinceMs = 0;
  awaitingAnswer = false;   // the wire this was waiting on no longer exists
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
// This panel has no sounder. The machine's one voice is U8 on the main
// board, so a finger landing on this glass becomes a sound only by crossing J9 —
// which is why it is sent on PRESSED rather than on the click: the round trip
// hides inside the finger's own dwell, and the tick lands where the finger did
// rather than where it lifted.
//
// It says "your touch registered", NOT "that worked". If only success made a
// sound, silence would mean both "you missed" and "the machine refused you", and
// on a capacitive panel with no travel those are exactly the two a user cannot
// otherwise tell apart. Outcomes get their own sounds, from the main board.
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
  lv_obj_set_style_radius(b, 0, 0);
  lv_obj_set_style_pad_all(b, 0, 0);
  lv_obj_set_style_border_width(b, 0, 0);
  lv_obj_set_style_shadow_width(b, 0, 0);
  lv_obj_set_style_bg_color(b, lv_color_hex(bg), 0);
  lv_obj_set_style_bg_color(b, lv_color_hex(bg == COL_ACCENT ? COL_DIM : bg == COL_DIM ? COL_TEXT : COL_CARD_ON), LV_STATE_PRESSED);
  lv_obj_set_style_color_filter_opa(b, LV_OPA_TRANSP, LV_STATE_PRESSED);
  lv_obj_add_flag(b, LV_OBJ_FLAG_PRESS_LOCK);
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

// An assignment updates the rail, selected portrait and picker selection.
// The main board owns the pair and persists it; this states what the glass now
// wants and takes back whatever the main board ends up holding.
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

static uint8_t availableImageOrder(uint8_t (&order)[FLAVOR_IMAGE_COUNT]) {
  static_assert(FLAVOR_IMAGE_COUNT == 8 && FLAVOR_FACTORY_COUNT == 4,
                "image picker order follows the shared artwork slots");
  uint8_t available = 0;
  for (uint8_t i = FLAVOR_FACTORY_COUNT; i < FLAVOR_IMAGE_COUNT; ++i)
    if (flavorArtAvailable(i)) available |= 1u << i;
  return front_ui::imageOrder(available, order);
}

static void refreshFlavorImages() {
  tileDisarm();
  for (uint8_t i = 0; i < 2; ++i)
    if (homeFlavorArtObj[i]) lv_img_set_src(homeFlavorArtObj[i],
        &flavorRailArt[resolveFlavorArt(flavorImage[i], i)]);
  for (uint8_t i = 0; i < chanImgCount; ++i)
    lv_img_set_src(chanImg[i], &chanImgSet[i][resolveFlavorArt(flavorImage[chanImgCh[i]], chanImgCh[i])]);
  for (uint8_t i = 0; i < selImgCount; ++i)
    lv_img_set_src(selImg[i], &selImgSet[i][resolveFlavorArt(flavorImage[flavorSel], flavorSel)]);
  if (heroImage) lv_img_set_src(heroImage, &flavorHeroArt[resolveFlavorArt(flavorImage[flavorSel], flavorSel)]);
  uint8_t order[FLAVOR_IMAGE_COUNT];
  const uint8_t count = availableImageOrder(order);
  const uint8_t pages = front_ui::imagePages(count);
  if (imagePage >= pages) { tileDisarm(); imagePage = pages - 1; }
  for (uint8_t i = 0; i < FLAVOR_IMAGE_COUNT; ++i) {
    if (!flvTileBtn[i]) continue;
    lv_obj_add_flag(flvTileBtn[i], LV_OBJ_FLAG_HIDDEN);
    const bool selected = i == flavorImage[flavorSel];
    lv_obj_set_style_border_color(flvTileBtn[i], lv_color_hex(selected ? COL_ACCENT : COL_CARD), 0);
    if (flvTileMark[i]) lv_label_set_text(flvTileMark[i], selected ? LV_SYMBOL_OK : "");
  }
  for (uint8_t pos = imagePage * 4; pos < count && pos < (imagePage + 1) * 4; ++pos) {
    lv_obj_t *tile = flvTileBtn[order[pos]];
    if (!tile) continue;
    lv_obj_set_pos(tile, (pos % 4) * (TILE_BTN_W + TILE_GAP), 0);
    lv_obj_clear_flag(tile, LV_OBJ_FLAG_HIDDEN);
  }
  tileStripAffordance();
}

static void refreshFlavorText() {
  char r[2][16];
  for (uint8_t i = 0; i < 2; i++) {
    snprintf(r[i], sizeof(r[i]), "1 : %u", flavorRatio[i]);
    if (homeFlavorRatio[i]) lv_label_set_text(homeFlavorRatio[i], r[i]);
  }
  if (flvDetailRatio) lv_label_set_text(flvDetailRatio, r[flavorSel & 1]);

  // A STEPPER AT THE END OF ITS RANGE SAYS SO. Silently clamping a press is a
  // control that answers, sounds like it answered, and changed nothing — so
  // these stop the way every spent control on this panel stops: sunk into the
  // card they sit on, their mark dim, and not clickable. Not LV_STATE_DISABLED,
  // whose theme style would light them brighter than the live one.
  const uint8_t ratio = flavorRatio[flavorSel & 1];
  struct { lv_obj_t *b; lv_obj_t *mark; bool on; } steps[2] = {
      {flvRatioMinus, flvRatioMinusMark, ratio > RATIO_MIN},
      {flvRatioPlus,  flvRatioPlusMark,  ratio < RATIO_MAX}};
  for (auto &t : steps) {
    if (!t.b) continue;
    if (t.on) lv_obj_add_flag(t.b, LV_OBJ_FLAG_CLICKABLE);
    else      lv_obj_clear_flag(t.b, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_bg_color(t.b, lv_color_hex(t.on ? COL_DIM : COL_CARD_ON), LV_PART_MAIN);
    if (t.mark)
      lv_obj_set_style_text_color(t.mark, lv_color_hex(t.on ? COL_INK : COL_OFF), LV_PART_MAIN);
  }
}

static void refreshHomeSelection() {
  if (!homeFlavorCard[0]) return;
  const bool known = flavorSynchronized || flavorRequestPending;
  const int8_t selected = known ? (int8_t)activeFlavor : -1;
  if (selected != homeFlavorShown) {
    homeFlavorShown = selected;
    for (uint8_t i = 0; i < 2; ++i) {
      const bool on = selected == i;
      lv_obj_set_style_bg_color(homeFlavorCard[i], lv_color_hex(on ? 0x214bb5 : 0x0a267f), 0);
      lv_obj_set_style_border_color(homeFlavorCard[i], lv_color_hex(on ? COL_ACCENT : 0x0a267f), 0);
      lv_label_set_text_fmt(homeFlavorBadgeText[i], on ? LV_SYMBOL_OK " %u" : "%u", (unsigned)(i + 1));
    }
  }
  if (activePage == PAGE_HOME || activePage == PAGE_SETUP) flavorSel = activeFlavor;
  static int8_t shownKnown = -1;
  const uint8_t art = resolveFlavorArt(flavorImage[flavorSel], flavorSel);
  if (heroCaption && shownKnown != (int8_t)known) {
    shownKnown = known;
    lv_label_set_text(heroCaption, known ? LV_SYMBOL_OK " Selected" : "Connecting");
  }
  if (heroImage && lv_img_get_src(heroImage) != &flavorHeroArt[art]) {
    lv_img_set_src(heroImage, &flavorHeroArt[art]);
  }
  refreshHomeLevel();
}

// ── Prime-ready session — shared main board truth and one local hold ──

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

static const char *primeOutcomeText(uint8_t outcome) {
  switch (outcome) {
    case PRIME_OUTCOME_STOPPED:       return "hold released";
    case PRIME_OUTCOME_TIMEOUT:       return "main board lost the hold";
    case PRIME_OUTCOME_LIMIT:         return "60 second limit reached";
    case PRIME_OUTCOME_REFUSED:       return "main board refused the hold";
    case PRIME_OUTCOME_CANCELED:      return "prime mode exited";
    case PRIME_OUTCOME_LEASE_EXPIRED: return "prime screen connection lost";
    default:                          return "";
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
  static bool shownPending = false;

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
                            shownLost != primeLinkLost ||
                            shownPending != primeTouchStartPending;
  if (!modelChanged) return;
  refreshShell();
  shownPhase = phase;
  shownOwner = owner;
  shownOutcome = outcome;
  shownChannel = flavorSel;
  shownDesired = primeSessionDesired;
  shownCancel = primeSessionCancelPending;
  shownHolding = holding;
  shownStop = primeStopPending;
  shownLost = primeLinkLost;
  shownPending = primeTouchStartPending;

  if (primeSessionCancelPending) {
    lv_label_set_text(primePadLbl, "Exiting prime");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_DIM), 0);
    setPrimeMsg("waiting for the main board");
  } else if (primeLinkLost) {
    lv_label_set_text(primePadLbl, "Reconnecting");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_DIM), 0);
    setPrimeMsg("prime connection lost");
  } else if (primeStopPending) {
    lv_label_set_text(primePadLbl, "Stopping");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_DIM), 0);
    setPrimeMsg("waiting for the main board");
  } else if (!primeSessionDesired) {
    lv_label_set_text(primePadLbl, "Connecting");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_DIM), 0);
    setPrimeMsg("");
  } else if (phase == PRIME_SESSION_RUNNING) {
    lv_label_set_text(primePadLbl, "Release to stop");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_GOOD), 0);
    setPrimeMsg(owner == PRIME_OWNER_FAUCET ? "held at the faucet" : "pump turning");
  } else if (holding || primeTouchStartPending) {
    lv_label_set_text(primePadLbl, "Starting");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_ACCENT), 0);
    setPrimeMsg("waiting for the main board");
  } else {
    lv_label_set_text(primePadLbl, "Hold to prime");
    lv_obj_set_style_bg_color(primePad, lv_color_hex(COL_ACCENT), 0);
    setPrimeMsg(primeOutcomeText(outcome));
  }
  // The navy label stays legible in both held and waiting states.
  const bool blocked = primeSessionCancelPending || primeLinkLost ||
                       primeStopPending || !primeSessionDesired;
  lv_obj_set_style_bg_color(
      primePad,
      lv_color_hex(blocked ? COL_DIM : COL_ACCENT),
      LV_STATE_PRESSED);
}

static void primeSessionActivate() {
  primeTouchStartPending = false;
  if (primeSessionCancelPending) {
    clickPending = false;
    primeRender(true);
    return;
  }
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
  // The accepted ACTIVATE itself makes the main board's one entry tick.
  clickPending = false;
  primeRender(true);
  Serial.printf("[J9] prime session activate ch=%u token=%08lX\n",
                flavorSel, (unsigned long)primeSessionToken);
}

static void primeSessionCancel() {
  primeTouchStartPending = false;
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
    // the token that never became main board truth.
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

static bool primeHoldBegin() {
  const bool ready = primeSessionDesired && !primeSessionCancelPending &&
                     primeSessionKnown &&
                     primeSession.sessionToken == primeSessionToken &&
                     primeSession.phase == PRIME_SESSION_READY;
  if (holding || primeStopPending || !ready || primeLinkLost) return false;

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
  return true;
}

static void applyPrimeSessionState(const PrimeSessionStatePayload &state) {
  if (state.phase > PRIME_SESSION_RUNNING || state.channel > PUMP_CHANNEL_B ||
      state.owner > PRIME_OWNER_FAUCET || state.outcome > PRIME_OUTCOME_LEASE_EXPIRED) return;

  // This exact tuple is the main board's power-on epoch marker. J9 is an
  // ordered, bounded single-sender link, so it is safe to accept even when a
  // surviving display has cached a numerically higher pre-reset revision.
  const bool mainBoardResetOff = state.phase == PRIME_SESSION_OFF &&
                                  state.owner == PRIME_OWNER_NONE &&
                                  state.revision == 0 &&
                                  state.sessionToken == 0;
  const bool cancelAnsweredOff = primeSessionCancelPending &&
                                 primeSessionToken != 0 &&
                                 state.phase == PRIME_SESSION_OFF &&
                                 state.sessionToken == primeSessionToken;
  if (primeSessionKnown) {
    // A main board reboot restarts its revision counter. The fresh session
    // token this display just chose is an epoch proof stronger than the cached
    // number: only an accepted ACTIVATE can echo it, and no queued old state can.
    const bool acceptedFreshEpoch = primeSessionDesired &&
                                    state.sessionToken == primeSessionToken &&
                                    state.sessionToken != 0 &&
                                    state.sessionToken != primeSession.sessionToken;
    const int32_t revisionDelta = (int32_t)(state.revision - primeSession.revision);
    if (revisionDelta < 0 && !acceptedFreshEpoch && !mainBoardResetOff &&
        !cancelAnsweredOff) {
      Serial.printf("[J9] stale prime session rev=%lu < %lu\n",
                    (unsigned long)state.revision,
                    (unsigned long)primeSession.revision);
      return;
    }
    if (revisionDelta == 0 && !acceptedFreshEpoch && !mainBoardResetOff &&
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
    // Main board truth supersedes any unsent control for the local token. In
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
  const bool resetNeedsCancel = mainBoardResetOff && primeSessionToken != 0 &&
                                (primeSessionDesired || primeSessionCancelPending);
  const bool completedOff = (!resetNeedsCancel && mainBoardResetOff) ||
                            cancelAnsweredOff ||
                            (state.phase == PRIME_SESSION_OFF && tokenMatches);
  if (resetNeedsCancel) {
    j9DiscardQueuedPrimeFeeds(true);
    primeSessionDesired = false;
    primeSessionCancelPending = true;
    primeUsbStartPending = false;
    primeTouchStartPending = false;
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
    primeTouchStartPending = false;
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
    const bool ourRun = state.owner == PRIME_OWNER_ENCLOSURE && tokenMatches &&
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
    if (adoptActive || (remoteStarted && state.owner != PRIME_OWNER_ENCLOSURE)) {
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
    if (tokenMatches && (primeUsbStartPending || primeTouchStartPending) &&
        state.outcome == PRIME_OUTCOME_NONE) {
      primeUsbStartPending = false;
      primeTouchStartPending = false;
      primeHoldBegin();
    }
    // A session that comes back with an outcome is not going to take this hold.
    if (tokenMatches && state.outcome != PRIME_OUTCOME_NONE) {
      primeTouchStartPending = false;
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
  if (uiReady) refreshFlavorImages();
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
                         primeSession.owner == PRIME_OWNER_ENCLOSURE &&
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
                                PRIME_OWNER_ENCLOSURE, primeStopRevision);
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
                              primeSession.owner == PRIME_OWNER_ENCLOSURE &&
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
      setPrimeMsg("link reset - retrying");
    }
    if (!acknowledged && heldMs > PRIME_SESSION_STALE_MS) {
      setPrimeMsg("no answer from the main board");
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
    if (!primeHoldBegin()) {
      primeTouchStartPending = primeSessionDesired && !primeSessionCancelPending &&
                               !primeStopPending && !primeLinkLost;
      if (primeTouchStartPending) primeRender(true);
    }
  } else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
    const bool wasPending = primeTouchStartPending;
    primeTouchStartPending = false;
    primeHoldEnd();
    if (wasPending) primeRender(true);
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
static void railCb(lv_event_t *e) {
  const RailPage page = (RailPage)(intptr_t)lv_event_get_user_data(e);
  if (page == RAIL_PRIME && activePage == PAGE_SERVICE && activeSvc == SVC_PRIME_HOLD) return;
  if (!front_ui::allows(front_ui::Action::Task, lockActive, holding)) return;
  if (!flavorSynchronized || flavorRequestPending) return;
  flavorSel = activeFlavor;
  showRail(page);
}

static void flavorBackCb(lv_event_t *e) {
  (void)e;
  if (!front_ui::allows(front_ui::Action::Dismiss, lockActive, holding)) return;
  showPage(PAGE_HOME);
}

static void svcBackCb(lv_event_t *e) {
  showService((ServiceView)(intptr_t)lv_event_get_user_data(e));
}

static void homeFlavorPickCb(lv_event_t *e) {
  if (!front_ui::allows(front_ui::Action::SelectFlavor, lockActive, holding)) return;
  const uint8_t flavor = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  // Queue a causal cancellation before any new dispensing selection.
  showPage(PAGE_HOME);
  if (selectActiveFlavor(flavor)) clickPending = false;
  else { clickPending = false; sendSound(SND_WIRE_TICK); }
  flavorSel = flavor;
  refreshFlavorImages();
  refreshHomeLevel();
}

static void primePickCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  showService(SVC_PRIME_HOLD);
}

// On tap opens either the selected flavor's ratio or its image picker.
static void homeSettingsCb(lv_event_t *e) {
  if (!front_ui::allows(front_ui::Action::Settings, lockActive, holding)) return;
  flavorSel = activeFlavor;
  showPage(PAGE_FLAVOR);
  showFlavor((FlavorView)(intptr_t)lv_event_get_user_data(e));
}

// Available artwork fills each page; the range and arrows describe that list.
static void tileStripAffordance() {
  if (!flvTilePosition) return;
  uint8_t order[FLAVOR_IMAGE_COUNT];
  const uint8_t count = availableImageOrder(order);
  const uint8_t end = (imagePage + 1) * 4 < count ? (imagePage + 1) * 4 : count;
  lv_label_set_text_fmt(flvTilePosition, "%u-%u of %u",
                        (unsigned)(imagePage * 4 + 1), (unsigned)end, (unsigned)count);
  lv_obj_t *buttons[2] = {flvTileLeft, flvTileRight};
  lv_obj_t *marks[2] = {flvTileLeftMark, flvTileRightMark};
  for (uint8_t i = 0; i < 2; ++i) {
    const bool enabled = i == 0 ? imagePage > 0 : imagePage + 1 < front_ui::imagePages(count);
    if (enabled) lv_obj_add_flag(buttons[i], LV_OBJ_FLAG_CLICKABLE);
    else lv_obj_clear_flag(buttons[i], LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_text_color(marks[i], lv_color_hex(enabled ? COL_TEXT : COL_OFF), 0);
    lv_obj_set_style_border_color(buttons[i], lv_color_hex(enabled ? 0x7d9eed : COL_OFF), 0);
  }
}

static void tileStripScrolledCb(lv_event_t *e) {
  (void)e;
  tileStripAffordance();
}

static void tileStripPageCb(lv_event_t *e) {
  if (lockActive) return;
  uint8_t order[FLAVOR_IMAGE_COUNT];
  const uint8_t count = availableImageOrder(order);
  const int next = imagePage + (int)(intptr_t)lv_event_get_user_data(e);
  if (next < 0 || next >= front_ui::imagePages(count)) { clickPending = false; return; }
  tileDisarm();
  imagePage = (uint8_t)next;
  refreshFlavorImages();
}

// True when this put a frame on J9, which is then the press's one sound.
static bool imagePick(uint8_t img) {
  if (lockActive || img >= FLAVOR_IMAGE_COUNT || flavorImage[flavorSel] == img) return false;
  // An empty custom slot is a place a picture can go, not a picture. Tapping
  // one does nothing rather than putting a fallback face on a channel.
  if (!flavorArtAvailable(img)) return false;
  flavorImage[flavorSel] = img;
  refreshFlavorImages();
  sendFlavorArt();
  return true;
}

// ── A tap, told apart from the start of a drag ────────────────────────────
// EVERY OTHER TARGET ON THIS PANEL FIRES ON THE FIRST TOUCH, and should: waiting
// for a release that has to land back on the same object is what made the stock
// behaviour feel slack. But a tile lives inside something that is dragged, and
// firing on the first touch there means every drag also chooses whatever it
// started on — the strip moved and the picture changed with it.
//
// So a tile alone arms instead of acting, and the gesture decides:
//
//   the finger lifts without having moved   → chosen, which is the whole of a tap
//   it is still there and still after 150 ms → chosen, so a deliberate press does
//                                              not wait for a lift
//   it moves, or the strip moves under it    → a drag, and nothing is chosen
//
// The strip's own offset is watched as well as the finger, because a press that
// arrests a coasting fling has not moved either, and stopping the strip is what
// that press was for.
#define TILE_TAP_MS   150
#define TILE_TAP_SLOP  12   // px of travel that is still a tap, not a drag

static int16_t  tileArmed = -1;        // the tile a finger is down on, or none
static uint32_t tileArmedAtMs = 0;
static uint16_t tileArmedX = 0;
static lv_coord_t tileArmedScroll = 0;

static void tileDisarm() { tileArmed = -1; }

static void imagePickCb(lv_event_t *e) {
  // The press has not spoken yet and must not sound as though it had. mkBtn
  // arms a click on every press, and one fired here is a beep for a gesture
  // that will not be known to be a choice for another 150 ms — which is how a
  // chosen picture came with two beeps and a drag came with one.
  clickPending = false;
  tileArmed = (int16_t)(intptr_t)lv_event_get_user_data(e);
  tileArmedAtMs = millis();
  tileArmedX = lastTouchX;
  tileArmedScroll = flvTileStrip ? lv_obj_get_scroll_x(flvTileStrip) : 0;
}

// Called every pass, because the answer is a thing that stops happening rather
// than a thing that happens: no further event arrives to say a finger held
// still.
static void tilePickService() {
  if (tileArmed < 0) return;

  const int32_t moved = (int32_t)curTouchX - (int32_t)tileArmedX;
  const lv_coord_t scroll = flvTileStrip ? lv_obj_get_scroll_x(flvTileStrip) : 0;
  if ((moved > TILE_TAP_SLOP || moved < -TILE_TAP_SLOP) || scroll != tileArmedScroll) {
    tileDisarm();
    return;
  }
  if (!touchIsDown || millis() - tileArmedAtMs >= TILE_TAP_MS) {
    const uint8_t img = (uint8_t)tileArmed;
    tileDisarm();
    // One press, one sound, and it happens where the press is finally answered.
    // A choice speaks for itself on J9; pressing the face already worn is still
    // a press and owns an ordinary tick. A drag reaches neither, which is right
    // — the strip moving is the whole of its feedback.
    if (!imagePick(img)) sendSound(SND_WIRE_TICK);
  }
}

static void cleanPickCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  showService(SVC_CLEAN_CONFIRM);
}

static void cleanStartCb(lv_event_t *e) {
  (void)e;
  if (lockActive || cleanStartSentMs || fillStartSentMs || airStartSentMs) return;
  ChannelPayload p{flavorSel};
  j9Post(MSG_CLEAN_START, &p, sizeof(p));
  cleanStartSentMs = millis() ? millis() : 1;
  setCleanMsg("starting");
  cleanStopSent = false;
  pendingOperationShow("CLEAN THIS FLAVOR", false);
}

static void fillPickCb(lv_event_t *e) {
  flavorSel = (uint8_t)(intptr_t)lv_event_get_user_data(e);
  showService(SVC_FILL_CONFIRM);
}

static void fillStartCb(lv_event_t *e) {
  (void)e;
  if (lockActive || fillStartSentMs || cleanStartSentMs || airStartSentMs) return;
  ChannelPayload p{flavorSel};
  j9Post(MSG_FILL_START, &p, sizeof(p));
  fillStartSentMs = millis() ? millis() : 1;
  setFillMsg("starting");
  fillStopSent = false;
  pendingOperationShow("FILL THIS FLAVOR", false);
}

static void ratioStepCb(lv_event_t *e) {
  if (lockActive) return;
  int r = flavorRatio[flavorSel] + (int)(intptr_t)lv_event_get_user_data(e);
  if (r < RATIO_MIN) r = RATIO_MIN;
  if (r > RATIO_MAX) r = RATIO_MAX;
  flavorRatio[flavorSel] = (uint8_t)r;
  refreshFlavorText();
  // The press's one frame: the pair as this glass now wants it. The main
  // board's answer is what it holds, and the tick is made off this frame.
  RatioPayload p{{flavorRatio[0], flavorRatio[1]}};
  j9Post(MSG_RATIO_SET, &p, sizeof(p));
  ratioSentMs = millis() ? millis() : 1;
}

static void ratioService() {
  if (ratioSentMs && millis() - ratioSentMs >= RATIO_REPLY_MS) ratioSentMs = 0;
}

// The gauge on each Choose card: lit segments in the reservoir's colour,
// the rest sunk into the card; the caption says EMPTY at the empty reed and
// stays a caption while nothing has been seen.
static void refreshHomeLevel() {
  if (!homeGauge) return;
  const uint8_t channel = activeFlavor & 1;
  const uint8_t n = levelSegments[channel];
  const bool fresh = front_ui::readingFresh(ctrlStatusMs, millis(), STATUS_ANSWER_MS);
  const bool known = n != LEVEL_UNKNOWN && levelValid && fresh;
  const bool pouring = fresh && pouringShown == channel;
  static int16_t shown = -1;
  const int16_t reading = (channel << 8) | (known ? n : 15) | (pouring ? 0x20 : 0);
  if (reading == shown) return;
  shown = reading;
  for (uint8_t k = 0; k < LEVEL_SEGMENTS; ++k)
    lv_obj_set_style_bg_color(homeLevelSegments[k], lv_color_hex(known && k < n ? COL_ACCENT : COL_OFF), 0);
  lv_label_set_text(homeLevelCaption, known ? (n == 0 ? "Reservoir empty" : "Reservoir") : "No level reading");
  if (homeTitle) lv_label_set_text(homeTitle, pouring ? "Pouring." : "On tap.");
}

// The reeds on the Settings landing. A reed the main board reads closed is a
// filled disc; every other one is a ring. A poll the main board has not answered
// for STATUS_ANSWER_MS, or a reading it says is stale, empties the diagram and
// says so under it, so a ring never stands for a reed nobody has looked at.
static void refreshStatusReeds() {
  if (!statusNote) return;
  const bool answered = ctrlStatusMs != 0 &&
                        ((long)(ctrlStatusMs - statusAskedMs) >= 0 ||
                         millis() - statusAskedMs < STATUS_ANSWER_MS);
  const bool fresh = answered && front_ui::readingFresh(ctrlStatusMs, millis(), STATUS_ANSWER_MS) &&
                     (ctrlStatus.levelFlags & LEVEL_F_VALID) != 0;
  uint16_t closed = 0;
  if (fresh) {
    closed = (uint16_t)(ctrlStatus.reeds[0] & 0x0F)
           | (uint16_t)((ctrlStatus.reeds[1] & 0x0F) << 4)
           | ((ctrlStatus.levelFlags & LEVEL_F_CARB_LOW)  ? (uint16_t)(1u << 8) : 0)
           | ((ctrlStatus.levelFlags & LEVEL_F_CARB_HIGH) ? (uint16_t)(1u << 9) : 0);
  }
  if (closed == statusShown && fresh == statusFreshShown) return;
  for (uint8_t i = 0; i < STATUS_REEDS; i++) {
    if (!statusReed[i]) continue;
    const bool lit = ((closed ^ statusShown) >> i) & 1;
    if (!lit) continue;
    const bool on = (closed >> i) & 1;
    lv_obj_set_style_bg_color(statusReed[i], lv_color_hex(on ? COL_ACCENT : COL_BLUE), 0);
    lv_obj_set_style_border_color(statusReed[i], lv_color_hex(on ? COL_GOOD : COL_DIM), 0);
  }
  const bool simulated = (ctrlStatus.levelFlags & LEVEL_F_SIMULATED) != 0;
  if (fresh != statusFreshShown || simulated != statusSimShown)
    lv_label_set_text(statusNote, !fresh      ? "Not reading the sensors"
                                 : simulated  ? "Simulated readings, injected from the console"
                                              : "");
  statusSimShown = simulated;
  statusShown = closed;
  statusFreshShown = fresh;
}

// Tenths of a degree as the column says it: one decimal, and a sign that
// survives a reading between 0 and -1 C. A probe that did not read, and a bus
// with no devices on it, both give "--".
static void statusTempText(char *out, size_t n, int16_t cx10, bool read) {
  if (!read || cx10 == TEMP_UNREAD) { snprintf(out, n, "--"); return; }
  const int tenths = cx10 < 0 ? -(int)cx10 : (int)cx10;
  snprintf(out, n, "%s%d.%d C", cx10 < 0 ? "-" : "", tenths / 10, tenths % 10);
}

// The column beside the profile: the carbonator wall and the coil's suction end,
// the state each of the two loops stands in, and how many devices answered the
// 1-wire bus. A main board that has not answered for STATUS_ANSWER_MS, and one
// that sends the core with no thermal tail, leave every line at "--".
static void refreshStatusThermal() {
  if (!statusThermalValue[0]) return;
  const bool answered = ctrlStatusMs != 0 &&
                        ((long)(ctrlStatusMs - statusAskedMs) >= 0 ||
                         millis() - statusAskedMs < STATUS_ANSWER_MS);
  const bool fresh = answered && ctrlStatusThermal &&
                     front_ui::readingFresh(ctrlStatusMs, millis(), STATUS_ANSWER_MS);
  if (statusThermalShown.drawn && fresh == statusThermalShown.fresh &&
      ctrlStatus.tankCx10 == statusThermalShown.tank &&
      ctrlStatus.coilCx10 == statusThermalShown.coil &&
      ctrlStatus.coldState == statusThermalShown.cold &&
      ctrlStatus.refillState == statusThermalShown.refill &&
      ctrlStatus.probeCount == statusThermalShown.probes) return;
  statusThermalShown.drawn  = true;
  statusThermalShown.fresh  = fresh;
  statusThermalShown.tank   = ctrlStatus.tankCx10;
  statusThermalShown.coil   = ctrlStatus.coilCx10;
  statusThermalShown.cold   = ctrlStatus.coldState;
  statusThermalShown.refill = ctrlStatus.refillState;
  statusThermalShown.probes = ctrlStatus.probeCount;

  // machine_policy::ColdState and ::RefillState, low value first. Cooling is
  // ColdState::On, Hold is ColdState::Holding, and the loop running and the
  // pump drawing are the two states that carry the accent.
  static const char *const coldWord[5]      = {"Fault", "Off", "Hold", "Cooling", "Freeze"};
  static const uint32_t     coldColour[5]   = {COL_WARN, COL_TEXT, COL_TEXT, COL_ACCENT, COL_WARN};
  static const char *const refillWord[5]    = {"Idle", "Queued", "Filling", "Timeout", "Fault"};
  static const uint32_t     refillColour[5] = {COL_TEXT, COL_TEXT, COL_ACCENT, COL_WARN, COL_WARN};
  const uint8_t cold   = ctrlStatus.coldState;
  const uint8_t refill = ctrlStatus.refillState;
  // TEMP_UNREAD is what the main board sends for a probe that did not read.
  const bool probed = fresh;

  char v[12];
  statusTempText(v, sizeof(v), ctrlStatus.tankCx10, probed);
  lv_label_set_text(statusThermalValue[0], v);
  statusTempText(v, sizeof(v), ctrlStatus.coilCx10, probed);
  lv_label_set_text(statusThermalValue[1], v);
  lv_label_set_text(statusThermalValue[2], fresh && cold < 5 ? coldWord[cold] : "--");
  lv_obj_set_style_text_color(statusThermalValue[2],
                              lv_color_hex(fresh && cold < 5 ? coldColour[cold] : COL_TEXT), 0);
  lv_label_set_text(statusThermalValue[3], fresh && refill < 5 ? refillWord[refill] : "--");
  lv_obj_set_style_text_color(statusThermalValue[3],
                              lv_color_hex(fresh && refill < 5 ? refillColour[refill] : COL_TEXT), 0);
  if (fresh) snprintf(v, sizeof(v), "%u", ctrlStatus.probeCount);
  else       snprintf(v, sizeof(v), "--");
  lv_label_set_text(statusThermalValue[4], v);
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
  if (animBase) lv_img_set_src(lockLogoImg, &frameDsc[0]);
  else lv_obj_add_flag(lockLogoImg, LV_OBJ_FLAG_HIDDEN);
  lv_obj_align(lockLogoImg, LV_ALIGN_LEFT_MID, 18, 0);

  lockModal = mkCard(lockScreen, LOCK_MODAL_W, LOCK_MODAL_H);
  lv_obj_align(lockModal, LV_ALIGN_RIGHT_MID, -LOCK_MODAL_MARGIN, 0);
  lv_obj_set_style_pad_left(lockModal, LOCK_PAD_L, 0);
  lv_obj_set_style_pad_right(lockModal, LOCK_PAD_R, 0);
  lv_obj_set_style_pad_top(lockModal, LOCK_PAD_T, 0);
  lv_obj_set_style_pad_bottom(lockModal, LOCK_PAD_B, 0);

  lockAccent = lv_obj_create(lockModal);
  lv_obj_set_size(lockAccent, 6, 178);
  lv_obj_align(lockAccent, LV_ALIGN_LEFT_MID, -18, 0);
  lv_obj_set_style_bg_color(lockAccent, lv_color_hex(COL_ACCENT), 0);
  lv_obj_set_style_border_width(lockAccent, 0, 0);
  lv_obj_set_style_radius(lockAccent, 3, 0);
  lv_obj_set_style_pad_all(lockAccent, 0, 0);
  lv_obj_clear_flag(lockAccent, LV_OBJ_FLAG_SCROLLABLE);

  lockKicker = mkText(lockModal, "HOME SODA MACHINE", &lv_font_montserrat_20, COL_ACCENT);
  lv_obj_align(lockKicker, LV_ALIGN_TOP_LEFT, 0, 0);
  lockTitle = mkText(lockModal, "Powering on", &lv_font_montserrat_40, COL_TEXT);
  lv_obj_align(lockTitle, LV_ALIGN_LEFT_MID, 0, -8);
  lockBody = mkText(lockModal, "Getting everything ready.", &lv_font_montserrat_20, COL_DIM);
  lv_obj_align(lockBody, LV_ALIGN_BOTTOM_LEFT, 0, 0);

  // What an operation on one channel adds: that channel's face where the
  // accent bar stood, at the size the picker previews it; a bar that fills as
  // the run runs; how long is left; and the one way out. All hidden until a
  // fill puts them up.
  lockFace = lv_img_create(lockModal);
  lv_img_set_src(lockFace, &flavorTile[0]);
  lv_obj_clear_flag(lockFace, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
  lv_obj_align(lockFace, LV_ALIGN_LEFT_MID, 0, 0);

  lockBar = lv_bar_create(lockModal);
  lv_obj_set_size(lockBar, LOCK_COL_W, 10);
  lv_bar_set_range(lockBar, 0, 1000);
  lv_bar_set_value(lockBar, 0, LV_ANIM_OFF);
  lv_obj_set_style_bg_color(lockBar, lv_color_hex(COL_OFF), LV_PART_MAIN);
  lv_obj_set_style_bg_opa(lockBar, LV_OPA_COVER, LV_PART_MAIN);
  lv_obj_set_style_radius(lockBar, 5, LV_PART_MAIN);
  lv_obj_set_style_bg_color(lockBar, lv_color_hex(COL_GOOD), LV_PART_INDICATOR);
  lv_obj_set_style_bg_opa(lockBar, LV_OPA_COVER, LV_PART_INDICATOR);
  lv_obj_set_style_radius(lockBar, 5, LV_PART_INDICATOR);
  lv_obj_align(lockBar, LV_ALIGN_TOP_LEFT, LOCK_COL_X, LOCK_BAR_Y);

  lockNote = mkText(lockModal, "", &lv_font_montserrat_20, COL_DIM);
  lv_obj_align(lockNote, LV_ALIGN_TOP_LEFT, LOCK_COL_X, LOCK_NOTE_Y);

  lockStop = mkBtn(lockModal, LOCK_STOP_W, LOCK_STOP_H, COL_CARD_ON);
  lv_obj_align(lockStop, LV_ALIGN_BOTTOM_RIGHT, 0, 0);
  lv_obj_clear_flag(lockStop, LV_OBJ_FLAG_PRESS_LOCK);   // slide off to change your mind
  lv_obj_add_event_cb(lockStop, lockStopCb, LV_EVENT_CLICKED, NULL);
  lv_obj_center(mkText(lockStop, "Stop", &lv_font_montserrat_24, COL_INK));

  lockFillLayout(false);
  lv_obj_add_flag(lockScreen, LV_OBJ_FLAG_HIDDEN);
}

static void lockScreenShow(const char *kicker, const char *title, const char *body) {
  if (!lockScreen) return;
  lv_obj_set_pos(lockScreen, 0, 0);
  lv_obj_set_size(lockScreen, SCREEN_W, SCREEN_H);
  operationResultVisible = false;
  lockFillLayout(false);
  lv_label_set_text(lockKicker, kicker);
  lv_label_set_text(lockTitle, title);
  lv_label_set_text(lockBody, body);
  lv_obj_clear_flag(lockScreen, LV_OBJ_FLAG_HIDDEN);
  lv_obj_move_foreground(lockScreen);
  lockActive = true;
  refreshShell();
  if (screenIdle) wake();
  animRun(true);
}

static void lockScreenHide() {
  if (!lockScreen) return;
  lv_obj_add_flag(lockScreen, LV_OBJ_FLAG_HIDDEN);
  lockActive = false;
  refreshShell();
  animRun(false);
  lastInputTime = millis();
}

// ── The funnel fill, on the lock ──────────────────────────────────────────
// The main board runs it and this shows it: the operation lock, with the
// channel's face where the modal's accent bar stands, a bar that fills as the
// draw runs, how long is left, and STOP. When the run ends the same modal says
// how — filled, full, stopped, or a fault — for FILL_CARD_MS, and the pane
// returns to the fill page it was started from.
//
// A channel operation's modal is wider, out to the animation's edge, because a
// face standing in the column leaves the words less room than the boot lock
// has. The plain layout is the boot lock's own.
static void lockFillLayout(bool on) {
  if (!lockModal) return;
  lv_obj_set_style_bg_opa(lockScreen, on ? LV_OPA_TRANSP : LV_OPA_COVER, 0);
  if (on) {
    const lv_coord_t x = operationLockMachine ? RAIL_W : TASK_X;
    const lv_coord_t w = SCREEN_W - x;
    lv_obj_set_size(lockModal, w, SCREEN_H - HEADER_H);
    lv_obj_set_pos(lockModal, x, HEADER_H);
    lv_obj_set_style_pad_all(lockModal, PANE_PAD, 0);
    lv_obj_set_style_radius(lockModal, 0, 0);
    lv_obj_set_style_bg_color(lockModal, THEME_BG, 0);
    lv_obj_align(lockKicker, LV_ALIGN_TOP_LEFT, 0, 0);
    lv_obj_set_width(lockTitle, w - 2 * PANE_PAD);
    lv_obj_align(lockTitle, LV_ALIGN_TOP_LEFT, 0, 38);
    lv_obj_set_width(lockBody, w - 2 * PANE_PAD);
    lv_obj_align(lockBody, LV_ALIGN_TOP_LEFT, 0, 138);
    lv_obj_set_size(lockBar, w - 2 * PANE_PAD, 12);
    lv_obj_align(lockBar, LV_ALIGN_TOP_LEFT, 0, 181);
    lv_obj_set_width(lockNote, w - 2 * PANE_PAD);
    lv_obj_align(lockNote, LV_ALIGN_TOP_LEFT, 0, 211);
    lv_obj_set_size(lockStop, w - 2 * PANE_PAD, 66);
    lv_obj_align(lockStop, LV_ALIGN_BOTTOM_LEFT, 0, -5);
    lv_obj_set_style_bg_color(lockStop, lv_color_hex(COL_ACCENT), 0);
    lv_obj_set_style_bg_color(lockStop, lv_color_hex(COL_DIM), LV_STATE_PRESSED);
    lv_obj_add_flag(lockLogoImg, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(lockAccent, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(lockFace, LV_OBJ_FLAG_HIDDEN);
    lv_obj_clear_flag(lockBar, LV_OBJ_FLAG_HIDDEN);
    lv_obj_clear_flag(lockNote, LV_OBJ_FLAG_HIDDEN);
    lv_obj_clear_flag(lockStop, LV_OBJ_FLAG_HIDDEN);
    animRun(false);
  } else {
    lv_obj_set_size(lockModal, LOCK_MODAL_W, LOCK_MODAL_H);
    lv_obj_align(lockModal, LV_ALIGN_RIGHT_MID, -LOCK_MODAL_MARGIN, 0);
    lv_obj_set_style_pad_left(lockModal, LOCK_PAD_L, 0);
    lv_obj_set_style_pad_right(lockModal, LOCK_PAD_R, 0);
    lv_obj_set_style_pad_top(lockModal, LOCK_PAD_T, 0);
    lv_obj_set_style_pad_bottom(lockModal, LOCK_PAD_B, 0);
    lv_obj_set_style_radius(lockModal, 0, 0);
    lv_obj_set_style_bg_color(lockModal, lv_color_hex(COL_CARD), 0);
    lv_obj_align(lockKicker, LV_ALIGN_TOP_LEFT, 0, 0);
    lv_obj_set_width(lockTitle, LV_SIZE_CONTENT);
    lv_obj_align(lockTitle, LV_ALIGN_LEFT_MID, 0, -8);
    lv_obj_set_width(lockBody, LV_SIZE_CONTENT);
    lv_obj_align(lockBody, LV_ALIGN_BOTTOM_LEFT, 0, 0);
    lv_obj_clear_flag(lockBody, LV_OBJ_FLAG_HIDDEN);
    lv_obj_clear_flag(lockAccent, LV_OBJ_FLAG_HIDDEN);
    if (animBase) lv_obj_clear_flag(lockLogoImg, LV_OBJ_FLAG_HIDDEN);
    lv_obj_t *ops[] = {lockFace, lockBar, lockNote, lockStop};
    for (lv_obj_t *o : ops) lv_obj_add_flag(o, LV_OBJ_FLAG_HIDDEN);
  }
}

static void pendingOperationShow(const char *kicker, bool machine) {
  operationLockMachine = machine;
  lockScreenShow(kicker, "Starting...", "");
  lockFillLayout(true);
  lv_obj_add_flag(lockBar, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockBody, LV_OBJ_FLAG_HIDDEN);
  lv_label_set_text(lockNote, "Waiting for the main board");
}

// Completed operations keep their outcome in the task pane while Done, the
// flavor rail and tabs become available immediately.
static void operationResultShow() {
  const lv_coord_t x = operationLockMachine ? RAIL_W : TASK_X;
  lv_obj_set_pos(lockScreen, x, HEADER_H);
  lv_obj_set_size(lockScreen, SCREEN_W - x, SCREEN_H - HEADER_H);
  lv_obj_set_pos(lockModal, 0, 0);
  operationResultVisible = true;
  lockActive = false;
  refreshShell();
}

// What the main board has drawn so far, smoothed between its answers.
static uint32_t fillDisplayedElapsed() {
  if (!fillKnown) return 0;
  uint32_t elapsed = fillState.elapsedMs;
  if (fillState.phase == FILL_PHASE_RUNNING) elapsed += millis() - fillAnchorMs;
  if (elapsed > fillState.plannedMs) elapsed = fillState.plannedMs;
  return elapsed;
}

// Only the bar and the note move, and only when a whole permille or second has.
// What the lock last showed, so a repaint is a change; a show starts them over.
static int32_t  lockShownPermille = -1;
static uint32_t lockShownSeconds  = 0xFFFFFFFF;
static uint16_t lockShownStep     = 0xFFFF;
static uint32_t lockShownMinutes  = 0xFFFFFFFF;
static void lockProgressReset() {
  lockShownPermille = -1;
  lockShownSeconds  = 0xFFFFFFFF;
  lockShownStep     = 0xFFFF;
  lockShownMinutes  = 0xFFFFFFFF;
}

static void fillLockProgress() {
  int32_t &shownPermille = lockShownPermille;
  uint32_t &shownSecondsLeft = lockShownSeconds;
  if (!fillLockShown || fillCardUntilMs) return;
  const uint32_t elapsed = fillDisplayedElapsed();
  const uint32_t planned = fillState.plannedMs ? fillState.plannedMs : 1;
  const int32_t permille = (int32_t)((uint64_t)elapsed * 1000 / planned);
  if (permille != shownPermille) {
    shownPermille = permille;
    lv_bar_set_value(lockBar, permille, LV_ANIM_OFF);
  }
  const uint32_t left = (planned - elapsed + 999) / 1000;
  if (fillStopSent) {
    if (shownSecondsLeft != 0xFFFFFFFE) {
      shownSecondsLeft = 0xFFFFFFFE;
      lv_label_set_text(lockNote, "stopping");
    }
  } else if (left != shownSecondsLeft) {
    shownSecondsLeft = left;
    if (left > 1) lv_label_set_text_fmt(lockNote, "%lu s left", (unsigned long)left);
    else          lv_label_set_text(lockNote, "almost done");
  }
}

static void fillLockShow() {
  operationLockMachine = false;
  flavorSel = fillState.channel & 1;
  showPage(PAGE_SERVICE);
  showService(SVC_FILL_CONFIRM);
  lockScreenShow("FILL THIS FLAVOR", "Drawing in\nconcentrate.", "");
  lv_img_set_src(lockFace, &flavorTile[flavorImage[fillState.channel & 1]]);
  lockFillLayout(true);
  lv_obj_add_flag(lockBody, LV_OBJ_FLAG_HIDDEN);
  lv_obj_set_style_bg_color(lockStop, lv_color_hex(COL_ACCENT), 0);
  fillLockShown = true;
  fillStopSent = false;
  fillCardUntilMs = 0;
  fillQueryMs = millis();
  lockProgressReset();
  fillLockProgress();
}

// The closing card: the same modal, with the ending in place of the bar.
static void fillLockCard(uint8_t outcome) {
  const char *title = "Stopped";
  const char *body = "";
  switch (outcome) {
    case FILL_OUTCOME_DONE:
      title = "Filled";
      body = "What you poured is in\nthe reservoir.";
      break;
    case FILL_OUTCOME_FULL:
      title = "Full";
      body = "The reservoir is full.\nWhat is left stays in\nthe funnel.";
      break;
    case FILL_OUTCOME_STOPPED:
      body = "Stopped early. The rest\nstays in the funnel.";
      break;
    case FILL_OUTCOME_GAS:
      body = "Gas alarm. Everything\nis switched off.";
      break;
    default:
      body = "A valve did not answer.\nEverything is switched off.";
      break;
  }
  lv_label_set_text(lockTitle, title);
  lv_label_set_text(lockBody, body);
  lv_obj_clear_flag(lockBody, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockBar, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockNote, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockStop, LV_OBJ_FLAG_HIDDEN);
  fillCardUntilMs = millis() + FILL_CARD_MS;
  if (!fillCardUntilMs) fillCardUntilMs = 1;
  operationResultShow();
}

static void fillLockClose() {
  fillLockShown = false;
  fillCardUntilMs = 0;
  fillStopSent = false;
  lockScreenHide();
  // Return to this flavor's Fill instructions after its outcome was read.
  if (activePage == PAGE_SERVICE &&
      (activeSvc == SVC_FILL_CONFIRM || activeSvc == SVC_FILL_PICK)) {
    showService(SVC_FILL_CONFIRM);
  }
}

static const char *fillRefusalText(uint8_t outcome) {
  switch (outcome) {
    case FILL_OUTCOME_BUSY:  return "the machine is busy";
    case FILL_OUTCOME_NO_IO: return "the valves are not answering";
    case FILL_OUTCOME_FAULT: return "a valve did not answer";
    case FILL_OUTCOME_GAS:   return "gas alarm - nothing runs";
    case FILL_OUTCOME_FULL:  return "the reservoir is already full";
    default:                 return "the main board declined";
  }
}

// Every word the main board says about the fill lands here.
static void applyFillState(const FillStatePayload &st) {
  fillState = st;
  fillKnown = true;
  fillAnchorMs = millis();
  const bool running = st.phase == FILL_PHASE_RUNNING;

  if (fillStartSentMs) {
    const bool stopping = fillStopSent;
    fillStartSentMs = 0;
    if (running) {
      setFillMsg("");
      fillLockShow();
      if (stopping) fillStopCb(nullptr);
    } else {
      fillStopSent = false;
      lockScreenHide();
      setFillMsg(stopping ? "Stopped" : fillRefusalText(st.outcome));
    }
    return;
  }

  if (running) {
    if (!fillLockShown) fillLockShow();   // the console's, or a lost turn's
    else fillLockProgress();
    return;
  }
  if (fillLockShown && !fillCardUntilMs) fillLockCard(st.outcome);
}

static void fillStopCb(lv_event_t *e) {
  (void)e;
  if ((!fillLockShown && !fillStartSentMs) || fillCardUntilMs || fillStopSent) return;
  j9Post(MSG_FILL_STOP, nullptr, 0);
  fillStopSent = true;
  lv_obj_set_style_bg_color(lockStop, lv_color_hex(COL_OFF), 0);
  if (fillStartSentMs) lv_label_set_text(lockNote, "Stopping - waiting for the main board");
  else fillLockProgress();
}

// From loop(): the answer START is owed, the state the lock is showing, and
// the card's own clock.
static void fillService() {
  const unsigned long now = millis();
  if (fillStartSentMs) {
    if (now - fillQueryMs >= FILL_QUERY_MS && outCount < OUT_Q_DEPTH / 2) {
      fillQueryMs = now;
      if (now - fillStartSentMs >= FILL_START_REPLY_MS &&
          strcmp(lv_label_get_text(lockNote), fillStopSent ? "Stopping - reconnecting" : "Reconnecting to the main board") != 0)
        lv_label_set_text(lockNote, fillStopSent ? "Stopping - reconnecting" : "Reconnecting to the main board");
      j9Post(fillStopSent ? MSG_FILL_STOP : MSG_FILL_QUERY, nullptr, 0);
    }
    return;
  }
  if (!fillLockShown) return;
  if (fillCardUntilMs) {
    if ((long)(now - fillCardUntilMs) >= 0) fillLockClose();
    return;
  }
  if (now - fillUiMs >= 100) {
    fillUiMs = now;
    fillLockProgress();
  }
  if (now - fillQueryMs >= FILL_QUERY_MS && outCount < OUT_Q_DEPTH / 2) {
    fillQueryMs = now;
    j9Post(fillStopSent ? MSG_FILL_STOP : MSG_FILL_QUERY, nullptr, 0);
  }
}

// ── The clean cycle, on the lock ──────────────────────────────────────────
// The same lock the fill runs on: the channel's face, a bar that fills across
// the whole cycle, a note saying which round and which way the water is going,
// and STOP. The kicker carries how long is left. When the cycle ends the same
// modal says how — clean, stopped, or a fault — for CLEAN_CARD_MS, and the
// pane returns to the clean page it was started from.

// The step's elapsed and the cycle's remaining time, smoothed between answers.
static uint32_t cleanDisplayedStepElapsed() {
  if (!cleanKnown) return 0;
  uint32_t elapsed = cleanState.stepElapsedMs;
  if (cleanState.phase == CLEAN_PHASE_RUNNING) elapsed += millis() - cleanAnchorMs;
  if (elapsed > cleanState.stepPlannedMs) elapsed = cleanState.stepPlannedMs;
  return elapsed;
}

static uint32_t cleanDisplayedLeft() {
  if (!cleanKnown || cleanState.phase != CLEAN_PHASE_RUNNING) return 0;
  const uint32_t since = millis() - cleanAnchorMs;
  return since >= cleanState.cycleLeftMs ? 0 : cleanState.cycleLeftMs - since;
}

// Only the bar, the note and the kicker move, and only when a whole permille,
// step or minute has.
static void cleanLockProgress() {
  int32_t &shownPermille = lockShownPermille;
  uint16_t &shownStep = lockShownStep;
  uint32_t &shownMinutes = lockShownMinutes;
  if (!cleanLockShown || cleanCardUntilMs) return;
  const uint32_t steps = cleanState.rounds ? (uint32_t)cleanState.rounds * 2 : 1;
  const uint32_t stepIndex = (uint32_t)(cleanState.round ? cleanState.round - 1 : 0) * 2 +
                             (cleanState.step == CLEAN_STEP_FLUSH ? 1 : 0);
  const uint32_t planned = cleanState.stepPlannedMs ? cleanState.stepPlannedMs : 1;
  const uint32_t stepPermille = (uint32_t)((uint64_t)cleanDisplayedStepElapsed() * 1000 / planned);
  int32_t permille = (int32_t)((stepIndex * 1000 + stepPermille) / steps);
  if (permille > 1000) permille = 1000;
  if (permille != shownPermille) {
    shownPermille = permille;
    lv_bar_set_value(lockBar, permille, LV_ANIM_OFF);
  }
  const uint16_t stepKey = (uint16_t)((cleanState.round << 8) | cleanState.step | (cleanStopSent ? 0x80 : 0));
  if (stepKey != shownStep) {
    shownStep = stepKey;
    if (cleanStopSent) {
      lv_label_set_text(lockNote, "stopping");
    } else {
      lv_label_set_text_fmt(lockNote, "%u of %u \xE2\x80\xA2 water %s",
                            (unsigned)cleanState.round, (unsigned)cleanState.rounds,
                            cleanState.step == CLEAN_STEP_FLUSH ? "out" : "in");
    }
  }
  const uint32_t left = cleanDisplayedLeft();
  const uint32_t minutes = left < 60000 ? 0 : (left + 30000) / 60000;
  if (minutes != shownMinutes) {
    shownMinutes = minutes;
    if (minutes == 0) lv_label_set_text(lockKicker, "UNDER 1 MIN LEFT");
    else              lv_label_set_text_fmt(lockKicker, "%lu MIN LEFT", (unsigned long)minutes);
  }
}

static void cleanLockShow() {
  operationLockMachine = false;
  flavorSel = cleanState.channel & 1;
  showPage(PAGE_SERVICE);
  showService(SVC_CLEAN_CONFIRM);
  lockScreenShow("CLEAN THIS FLAVOR", "Flushing.", "");
  lv_img_set_src(lockFace, &flavorTile[flavorImage[cleanState.channel & 1]]);
  lockFillLayout(true);
  lv_obj_add_flag(lockBody, LV_OBJ_FLAG_HIDDEN);
  lv_obj_set_style_bg_color(lockStop, lv_color_hex(COL_ACCENT), 0);
  cleanLockShown = true;
  cleanStopSent = false;
  cleanCardUntilMs = 0;
  cleanQueryMs = millis();
  lockProgressReset();
  cleanLockProgress();
}

// The closing card: the same modal, with the ending in place of the bar.
static void cleanLockCard(uint8_t outcome) {
  static char body[96];
  const char *title = "Stopped";
  switch (outcome) {
    case CLEAN_OUTCOME_DONE:
      title = "Clean";
      if (cleanState.rounds == 1) snprintf(body, sizeof(body), "Rinsed once with\ntap water.\nReady to fill.");
      else snprintf(body, sizeof(body), "Rinsed %u times with\ntap water.\nReady to fill.",
                    (unsigned)cleanState.rounds);
      break;
    case CLEAN_OUTCOME_STOPPED:
      snprintf(body, sizeof(body), "Stopped early. Water\nmay be left in the\nreservoir.");
      break;
    case CLEAN_OUTCOME_GAS:
      snprintf(body, sizeof(body), "Gas alarm. Everything\nis switched off.");
      break;
    default:
      snprintf(body, sizeof(body), "A valve did not answer.\nEverything is switched off.");
      break;
  }
  lv_label_set_text(lockKicker, "CLEAN CYCLE");
  lv_label_set_text(lockTitle, title);
  lv_label_set_text(lockBody, body);
  lv_obj_clear_flag(lockBody, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockBar, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockNote, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockStop, LV_OBJ_FLAG_HIDDEN);
  cleanCardUntilMs = millis() + CLEAN_CARD_MS;
  if (!cleanCardUntilMs) cleanCardUntilMs = 1;
  operationResultShow();
}

static void cleanLockClose() {
  cleanLockShown = false;
  cleanCardUntilMs = 0;
  cleanStopSent = false;
  lockScreenHide();
  if (activePage == PAGE_SERVICE &&
      (activeSvc == SVC_CLEAN_CONFIRM || activeSvc == SVC_CLEAN_PICK)) {
    showService(SVC_CLEAN_CONFIRM);
  }
}

static const char *cleanRefusalText(uint8_t outcome) {
  switch (outcome) {
    case CLEAN_OUTCOME_BUSY:  return "the machine is busy";
    case CLEAN_OUTCOME_NO_IO: return "the valves are not answering";
    case CLEAN_OUTCOME_FAULT: return "a valve did not answer";
    case CLEAN_OUTCOME_GAS:   return "gas alarm \xE2\x80\xA2 nothing runs";
    default:                  return "the main board declined";
  }
}

// Every word the main board says about the clean cycle lands here.
static void applyCleanState(const CleanStatePayload &st) {
  cleanState = st;
  cleanKnown = true;
  cleanAnchorMs = millis();
  const bool running = st.phase == CLEAN_PHASE_RUNNING;

  if (cleanStartSentMs) {
    const bool stopping = cleanStopSent;
    cleanStartSentMs = 0;
    if (running) {
      setCleanMsg("");
      cleanLockShow();
      if (stopping) cleanStopCb(nullptr);
    } else {
      cleanStopSent = false;
      lockScreenHide();
      setCleanMsg(stopping ? "Stopped" : cleanRefusalText(st.outcome));
    }
    return;
  }

  if (running) {
    if (!cleanLockShown) cleanLockShow();   // the console's, or a lost turn's
    else cleanLockProgress();
    return;
  }
  if (cleanLockShown && !cleanCardUntilMs) cleanLockCard(st.outcome);
}

static void cleanStopCb(lv_event_t *e) {
  (void)e;
  if ((!cleanLockShown && !cleanStartSentMs) || cleanCardUntilMs || cleanStopSent) return;
  j9Post(MSG_CLEAN_STOP, nullptr, 0);
  cleanStopSent = true;
  lv_obj_set_style_bg_color(lockStop, lv_color_hex(COL_OFF), 0);
  if (cleanStartSentMs) lv_label_set_text(lockNote, "Stopping - waiting for the main board");
  else cleanLockProgress();
}

// ── The air cycles, on the lock ───────────────────────────────────────────
// Dry — before a pump replacement — is asked for from Settings; a purge is the
// console's. The lock shows either the way it shows the clean cycle: the face
// of the channel whose pump is turning, a bar across the whole cycle, a note
// with the step and which way the air is going, STOP, and the time left.
static uint32_t airDisplayedStepElapsed() {
  if (!airKnown) return 0;
  uint32_t elapsed = airState.stepElapsedMs;
  if (airState.phase == AIR_PHASE_RUNNING) elapsed += millis() - airAnchorMs;
  if (elapsed > airState.stepPlannedMs) elapsed = airState.stepPlannedMs;
  return elapsed;
}

static uint32_t airDisplayedLeft() {
  if (!airKnown || airState.phase != AIR_PHASE_RUNNING) return 0;
  const uint32_t since = millis() - airAnchorMs;
  return since >= airState.cycleLeftMs ? 0 : airState.cycleLeftMs - since;
}

static void airLockProgress() {
  int32_t &shownPermille = lockShownPermille;
  uint16_t &shownStep = lockShownStep;
  uint32_t &shownMinutes = lockShownMinutes;
  if (!airLockShown || airCardUntilMs) return;
  const uint32_t steps = airState.steps ? airState.steps : 1;
  const uint32_t planned = airState.stepPlannedMs ? airState.stepPlannedMs : 1;
  const uint32_t stepPermille = (uint32_t)((uint64_t)airDisplayedStepElapsed() * 1000 / planned);
  int32_t permille = (int32_t)(((uint32_t)airState.stepIndex * 1000 + stepPermille) / steps);
  if (permille > 1000) permille = 1000;
  if (permille != shownPermille) {
    shownPermille = permille;
    lv_bar_set_value(lockBar, permille, LV_ANIM_OFF);
  }
  const uint16_t stepKey = (uint16_t)((airState.stepIndex << 8) | airState.channel | (airStopSent ? 0x80 : 0));
  if (stepKey != shownStep) {
    shownStep = stepKey;
    lv_img_set_src(lockFace, &flavorTile[flavorImage[airState.channel & 1]]);
    if (airStopSent) {
      lv_label_set_text(lockNote, "stopping");
    } else {
      lv_label_set_text_fmt(lockNote, "%u of %u \xE2\x80\xA2 air %s",
                            (unsigned)(airState.stepIndex + 1), (unsigned)airState.steps,
                            airState.step == AIR_STEP_IN ? "in" : "out");
    }
  }
  const uint32_t left = airDisplayedLeft();
  const uint32_t minutes = left < 60000 ? 0 : (left + 30000) / 60000;
  if (minutes != shownMinutes) {
    shownMinutes = minutes;
    if (minutes == 0) lv_label_set_text(lockKicker, "UNDER 1 MIN LEFT");
    else              lv_label_set_text_fmt(lockKicker, "%lu MIN LEFT", (unsigned long)minutes);
  }
}

static void airLockShow() {
  operationLockMachine = true;
  showPage(PAGE_SETUP);
  showSettings(SET_PUMP);
  lockScreenShow(airState.mode == AIR_MODE_PURGE ? "AIR PURGE" : "PUMP SERVICE",
                 airState.mode == AIR_MODE_PURGE ? "Purging" : "Drying", "");
  lv_img_set_src(lockFace, &flavorTile[flavorImage[airState.channel & 1]]);
  lockFillLayout(true);
  lv_obj_add_flag(lockBody, LV_OBJ_FLAG_HIDDEN);
  lv_obj_set_style_bg_color(lockStop, lv_color_hex(COL_ACCENT), 0);
  airLockShown = true;
  airStopSent = false;
  airCardUntilMs = 0;
  airQueryMs = millis();
  lockProgressReset();
  airLockProgress();
}

static void airLockCard(uint8_t outcome) {
  const bool purge = airState.mode == AIR_MODE_PURGE;
  const char *title = "Stopped";
  const char *body;
  switch (outcome) {
    case AIR_OUTCOME_DONE:
      title = purge ? "Purged" : "Dry";
      body = purge ? "The reservoir is\nempty and the line\nis clear."
                   : "The lines are dry.\nPull the pump\ncartridge.";
      break;
    case AIR_OUTCOME_STOPPED:
      body = "Stopped early. The\nlines may not be\nclear.";
      break;
    case AIR_OUTCOME_GAS:
      body = "Gas alarm. Everything\nis switched off.";
      break;
    default:
      body = "A valve did not answer.\nEverything is switched off.";
      break;
  }
  lv_label_set_text(lockKicker, purge ? "AIR PURGE" : "PUMP SERVICE");
  lv_label_set_text(lockTitle, title);
  lv_label_set_text(lockBody, body);
  lv_obj_clear_flag(lockBody, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockBar, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockNote, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(lockStop, LV_OBJ_FLAG_HIDDEN);
  airCardUntilMs = millis() + CLEAN_CARD_MS;
  if (!airCardUntilMs) airCardUntilMs = 1;
  operationResultShow();
}

static void airLockClose() {
  airLockShown = false;
  airCardUntilMs = 0;
  airStopSent = false;
  lockScreenHide();
}

static const char *airRefusalText(uint8_t outcome) {
  switch (outcome) {
    case AIR_OUTCOME_BUSY:  return "the machine is busy";
    case AIR_OUTCOME_NO_IO: return "the valves are not answering";
    case AIR_OUTCOME_FAULT: return "a valve did not answer";
    case AIR_OUTCOME_GAS:   return "gas alarm \xE2\x80\xA2 nothing runs";
    default:                return "the main board declined";
  }
}

static void applyAirState(const AirStatePayload &st) {
  airState = st;
  airKnown = true;
  airAnchorMs = millis();
  const bool running = st.phase == AIR_PHASE_RUNNING;

  if (airStartSentMs) {
    const bool stopping = airStopSent;
    airStartSentMs = 0;
    if (running) {
      setSettingsMsg("");
      airLockShow();
      if (stopping) airStopCb(nullptr);
    } else {
      airStopSent = false;
      lockScreenHide();
      setSettingsMsg(stopping ? "Stopped" : airRefusalText(st.outcome));
    }
    return;
  }

  if (running) {
    if (!airLockShown) airLockShow();   // the console's, or a lost turn's
    else airLockProgress();
    return;
  }
  if (airLockShown && !airCardUntilMs) airLockCard(st.outcome);
}

static void airStopCb(lv_event_t *e) {
  (void)e;
  if ((!airLockShown && !airStartSentMs) || airCardUntilMs || airStopSent) return;
  j9Post(MSG_AIR_STOP, nullptr, 0);
  airStopSent = true;
  lv_obj_set_style_bg_color(lockStop, lv_color_hex(COL_OFF), 0);
  if (airStartSentMs) lv_label_set_text(lockNote, "Stopping - waiting for the main board");
  else airLockProgress();
}

// Settings' one commitment: dry the lines before the pump cartridge is pulled.
static void dryStartCb(lv_event_t *e) {
  (void)e;
  if (lockActive || airStartSentMs || fillStartSentMs || cleanStartSentMs) return;
  AirRequestPayload p{AIR_MODE_DRY, 0};
  j9Post(MSG_AIR_START, &p, sizeof(p));
  airStartSentMs = millis() ? millis() : 1;
  setSettingsMsg("starting");
  airStopSent = false;
  pendingOperationShow("PUMP SERVICE", true);
}

static void airService() {
  const unsigned long now = millis();
  if (airStartSentMs) {
    if (now - airQueryMs >= CLEAN_QUERY_MS && outCount < OUT_Q_DEPTH / 2) {
      airQueryMs = now;
      if (now - airStartSentMs >= FILL_START_REPLY_MS &&
          strcmp(lv_label_get_text(lockNote), airStopSent ? "Stopping - reconnecting" : "Reconnecting to the main board") != 0)
        lv_label_set_text(lockNote, airStopSent ? "Stopping - reconnecting" : "Reconnecting to the main board");
      j9Post(airStopSent ? MSG_AIR_STOP : MSG_AIR_QUERY, nullptr, 0);
    }
    return;
  }
  if (!airLockShown) return;
  if (airCardUntilMs) {
    if ((long)(now - airCardUntilMs) >= 0) airLockClose();
    return;
  }
  if (now - airUiMs >= 100) {
    airUiMs = now;
    airLockProgress();
  }
  if (now - airQueryMs >= CLEAN_QUERY_MS && outCount < OUT_Q_DEPTH / 2) {
    airQueryMs = now;
    j9Post(airStopSent ? MSG_AIR_STOP : MSG_AIR_QUERY, nullptr, 0);
  }
}

// One STOP on the lock, for whichever operation is up on it.
static void lockStopCb(lv_event_t *e) {
  if (fillLockShown || fillStartSentMs) fillStopCb(e);
  else if (cleanLockShown || cleanStartSentMs) cleanStopCb(e);
  else if (airLockShown || airStartSentMs) airStopCb(e);
}

static void cleanService() {
  const unsigned long now = millis();
  if (cleanStartSentMs) {
    if (now - cleanQueryMs >= CLEAN_QUERY_MS && outCount < OUT_Q_DEPTH / 2) {
      cleanQueryMs = now;
      if (now - cleanStartSentMs >= FILL_START_REPLY_MS &&
          strcmp(lv_label_get_text(lockNote), cleanStopSent ? "Stopping - reconnecting" : "Reconnecting to the main board") != 0)
        lv_label_set_text(lockNote, cleanStopSent ? "Stopping - reconnecting" : "Reconnecting to the main board");
      j9Post(cleanStopSent ? MSG_CLEAN_STOP : MSG_CLEAN_QUERY, nullptr, 0);
    }
    return;
  }
  if (!cleanLockShown) return;
  if (cleanCardUntilMs) {
    if ((long)(now - cleanCardUntilMs) >= 0) cleanLockClose();
    return;
  }
  if (now - cleanUiMs >= 100) {
    cleanUiMs = now;
    cleanLockProgress();
  }
  if (now - cleanQueryMs >= CLEAN_QUERY_MS && outCount < OUT_Q_DEPTH / 2) {
    cleanQueryMs = now;
    j9Post(cleanStopSent ? MSG_CLEAN_STOP : MSG_CLEAN_QUERY, nullptr, 0);
  }
}

// ── The camera's test screen ──────────────────────────────────────────────
// A bench camera reads this panel and maps its photograph back onto the panel's own 800×480
// grid. What it needs is a known picture: a 2 px white frame on the outermost pixels, four 32 px
// white fiducials whose centres sit at (32, 32), (768, 32), (32, 448) and (768, 448) in
// continuous panel coordinates (pixel i spans [i, i+1)), and a 1 px cross through (400, 240) that
// is left out of the fit as its check, in a black band of its own. Above it: an eight-step gray
// wedge from 0 to 255, six saturated colours, and every colour the interface draws with a 50%
// gray — the flat patches a camera-to-panel colour fit is made from. Below it: 1 px vertical
// stripes, 1 px horizontal stripes and a 2 px checkerboard, each 64×64. Everything is on black,
// the panel's own.
static lv_obj_t *mkFlat(lv_obj_t *parent, lv_coord_t x, lv_coord_t y, lv_coord_t w, lv_coord_t h,
                        lv_color_t c) {
  lv_obj_t *o = lv_obj_create(parent);
  lv_obj_set_size(o, w, h);
  lv_obj_set_pos(o, x, y);
  lv_obj_set_style_bg_color(o, c, 0);
  lv_obj_set_style_bg_opa(o, LV_OPA_COVER, 0);
  lv_obj_set_style_border_width(o, 0, 0);
  lv_obj_set_style_radius(o, 0, 0);
  lv_obj_set_style_pad_all(o, 0, 0);
  lv_obj_clear_flag(o, LV_OBJ_FLAG_SCROLLABLE);
  return o;
}

static lv_img_dsc_t testPatDsc[3];

static void buildTestScreen(lv_obj_t *scr) {
  testScreen = mkFlat(scr, 0, 0, SCREEN_W, SCREEN_H, lv_color_black());
  lv_obj_add_flag(testScreen, LV_OBJ_FLAG_CLICKABLE);   // a finger here reaches no page beneath

  // The frame is its own object: a border on the parent would move every child in by its width.
  lv_obj_t *frame = mkFlat(testScreen, 0, 0, SCREEN_W, SCREEN_H, lv_color_black());
  lv_obj_set_style_bg_opa(frame, LV_OPA_TRANSP, 0);
  lv_obj_set_style_border_width(frame, 2, 0);
  lv_obj_set_style_border_color(frame, lv_color_white(), 0);

  static const lv_coord_t fx[2] = {16, SCREEN_W - 48}, fy[2] = {16, SCREEN_H - 48};
  for (int i = 0; i < 2; i++)
    for (int j = 0; j < 2; j++) mkFlat(testScreen, fx[i], fy[j], 32, 32, lv_color_white());
  mkFlat(testScreen, SCREEN_W / 2, SCREEN_H / 2 - 10, 1, 20, lv_color_white());
  mkFlat(testScreen, SCREEN_W / 2 - 10, SCREEN_H / 2, 20, 1, lv_color_white());

  for (int k = 0; k < 8; k++) {
    const uint8_t v = (uint8_t)((k * 255 + 3) / 7);
    mkFlat(testScreen, 144 + 64 * k, 56, 64, 48, lv_color_make(v, v, v));
  }
  static const uint32_t swatch[6] = {0xff0000, 0x00ff00, 0x0000ff, 0x00ffff, 0xff00ff, 0xffff00};
  for (int k = 0; k < 6; k++) mkFlat(testScreen, 208 + 64 * k, 112, 64, 48, lv_color_hex(swatch[k]));
  static const uint32_t palette[10] = {COL_BLUE, COL_CARD, COL_CARD_ON, COL_ACCENT, COL_TEXT,
                                       COL_DIM, COL_OFF, COL_GOOD, COL_WARN, 0x808080};
  for (int k = 0; k < 10; k++) mkFlat(testScreen, 80 + 64 * k, 168, 64, 48, lv_color_hex(palette[k]));

  for (int p = 0; p < 3; p++) {
    uint16_t *px = (uint16_t *)malloc(64 * 64 * sizeof(uint16_t));
    if (!px) break;
    for (int y = 0; y < 64; y++)
      for (int x = 0; x < 64; x++) {
        const bool on = p == 0 ? (x & 1) : p == 1 ? (y & 1) : (((x >> 1) + (y >> 1)) & 1);
        px[y * 64 + x] = on ? 0xffff : 0x0000;
      }
    testPatDsc[p].header.cf = LV_IMG_CF_TRUE_COLOR;
    testPatDsc[p].header.always_zero = 0;
    testPatDsc[p].header.w = 64;
    testPatDsc[p].header.h = 64;
    testPatDsc[p].data_size = 64 * 64 * sizeof(uint16_t);
    testPatDsc[p].data = (const uint8_t *)px;
    lv_obj_t *img = lv_img_create(testScreen);
    lv_img_set_src(img, &testPatDsc[p]);
    lv_obj_set_pos(img, 240 + 128 * p, 268);
  }

  lv_obj_t *t = mkText(testScreen, "PANELCAM TEST", &lv_font_montserrat_28, 0xffffff);
  lv_obj_align(t, LV_ALIGN_TOP_MID, 0, 344);
  lv_obj_t *v = mkText(testScreen, FW_VERSION, &lv_font_montserrat_20, COL_DIM);
  lv_obj_align(v, LV_ALIGN_TOP_MID, 0, 384);

  lv_obj_add_flag(testScreen, LV_OBJ_FLAG_HIDDEN);
}

static void testScreenShow(uint16_t seconds) {
  if (!testScreen) return;
  if (seconds == 0) { testScreenHide(); return; }
  lv_obj_clear_flag(testScreen, LV_OBJ_FLAG_HIDDEN);
  lv_obj_move_foreground(testScreen);
  testActive = true;
  testUntilMs = millis() + seconds * 1000UL;
  if (screenIdle) wake();
}

static void testScreenHide() {
  if (!testScreen || !testActive) return;
  lv_obj_add_flag(testScreen, LV_OBJ_FLAG_HIDDEN);
  testActive = false;
  lastInputTime = millis();
}

static void buildRail(lv_obj_t *scr) {
  flavorRail = mkFlat(scr, 0, 0, RAIL_W, SCREEN_H, lv_color_hex(COL_CARD));
  lv_obj_add_flag(flavorRail, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_add_event_cb(flavorRail, flavorBackCb, ACT_EVENT, NULL);
  for (uint8_t i = 0; i < 2; ++i) {
    lv_obj_t *b = mkBtn(flavorRail, 84, 173, 0x0a267f);
    lv_obj_set_pos(b, 10, 19 + i * 189);
    lv_obj_set_style_border_width(b, 2, 0);
    lv_obj_set_style_border_color(b, lv_color_hex(0x0a267f), 0);
    lv_obj_add_event_cb(b, homeFlavorPickCb, ACT_EVENT, (void *)(intptr_t)i);
    homeFlavorCard[i] = b;
    lv_obj_t *art = lv_img_create(b);
    lv_img_set_src(art, &flavorRailArt[resolveFlavorArt(flavorImage[i], i)]);
    lv_obj_align(art, LV_ALIGN_TOP_MID, 0, 8);
    lv_obj_clear_flag(art, LV_OBJ_FLAG_CLICKABLE);
    homeFlavorArtObj[i] = art;
    homeFlavorBadgeText[i] = mkText(b, "", &lv_font_montserrat_20, COL_TEXT);
    lv_obj_align(homeFlavorBadgeText[i], LV_ALIGN_BOTTOM_MID, 0, -5);
  }
  heroPanel = mkBtn(scr, HERO_W, SCREEN_H, COL_DIM);
  lv_obj_set_pos(heroPanel, RAIL_W, 0);
  lv_obj_set_style_bg_color(heroPanel, lv_color_hex(COL_DIM), LV_STATE_PRESSED);
  lv_obj_add_event_cb(heroPanel, flavorBackCb, ACT_EVENT, NULL);
  heroImage = lv_img_create(heroPanel);
  lv_img_set_src(heroImage, &flavorHeroArt[resolveFlavorArt(flavorImage[flavorSel], flavorSel)]);
  lv_obj_align(heroImage, LV_ALIGN_TOP_MID, 0, 64);
  lv_obj_clear_flag(heroImage, LV_OBJ_FLAG_CLICKABLE);
  heroCaption = mkText(heroPanel, LV_SYMBOL_OK " Selected", &lv_font_montserrat_20, COL_INK);
  lv_obj_align(heroCaption, LV_ALIGN_TOP_MID, 0, 424);
}

static void settingsCb(lv_event_t *e) {
  (void)e;
  if (!front_ui::allows(front_ui::Action::Settings, lockActive, holding)) return;
  showPage(PAGE_SETUP);
}

static void buildSettingsButton(lv_obj_t *scr) {
  settingsBtn = mkBtn(scr, RAIL_W, SETTINGS_BTN, COL_CARD);
  lv_obj_set_pos(settingsBtn, 0, SCREEN_H - SETTINGS_BTN);
  lv_obj_set_style_border_width(settingsBtn, 1, 0);
  lv_obj_set_style_border_side(settingsBtn, LV_BORDER_SIDE_TOP, 0);
  lv_obj_set_style_border_color(settingsBtn, lv_color_hex(0x5675c9), 0);
  lv_obj_add_event_cb(settingsBtn, settingsCb, ACT_EVENT, NULL);
  lv_obj_center(mkText(settingsBtn, LV_SYMBOL_SETTINGS, &lv_font_montserrat_40, COL_TEXT));

  taskHeader = mkFlat(scr, TASK_X, 0, TASK_W, HEADER_H, THEME_BG);
  static const RailPage pages[3] = {RAIL_FILL, RAIL_PRIME, RAIL_CLEAN};
  static const char *labels[3] = {"Fill", "Prime", "Clean"};
  for (uint8_t i = 0; i < 3; ++i) {
    const RailPage page = pages[i];
    railBtn[page] = mkBtn(taskHeader, i == 2 ? 120 : 119, HEADER_H, COL_BLUE);
    lv_obj_set_pos(railBtn[page], i * 119, 0);
    lv_obj_set_style_border_width(railBtn[page], 1, 0);
    lv_obj_set_style_border_side(railBtn[page], LV_BORDER_SIDE_RIGHT | LV_BORDER_SIDE_BOTTOM, 0);
    lv_obj_set_style_border_color(railBtn[page], lv_color_hex(0x7096ef), 0);
    lv_obj_add_event_cb(railBtn[page], railCb, ACT_EVENT, (void *)(intptr_t)page);
    railLabel[page] = mkText(railBtn[page], labels[i], &lv_font_montserrat_24, COL_TEXT);
    lv_obj_center(railLabel[page]);
  }
  systemTitle = mkText(taskHeader, "System status", &lv_font_montserrat_28, COL_TEXT);
  lv_obj_align(systemTitle, LV_ALIGN_LEFT_MID, PANE_PAD, 0);
  doneBtn = mkBtn(taskHeader, 104, HEADER_H, COL_DIM);
  lv_obj_align(doneBtn, LV_ALIGN_TOP_RIGHT, 0, 0);
  lv_obj_add_event_cb(doneBtn, flavorBackCb, ACT_EVENT, NULL);
  lv_obj_center(mkText(doneBtn, "Done", &lv_font_montserrat_24, COL_INK));
}

static void refreshShell() {
  if (!taskHeader) return;
  const bool machine = activePage == PAGE_SETUP;
  if (machine) lv_obj_add_flag(heroPanel, LV_OBJ_FLAG_HIDDEN);
  else lv_obj_clear_flag(heroPanel, LV_OBJ_FLAG_HIDDEN);
  lv_obj_set_pos(taskHeader, machine ? RAIL_W : TASK_X, 0);
  lv_obj_set_width(taskHeader, machine ? SCREEN_W - RAIL_W : TASK_W);
  for (int i = 1; i < RAIL_PAGE_COUNT; ++i) {
    if (!railBtn[i]) continue;
    if (machine) lv_obj_add_flag(railBtn[i], LV_OBJ_FLAG_HIDDEN);
    else lv_obj_clear_flag(railBtn[i], LV_OBJ_FLAG_HIDDEN);
    const bool selected = i == activeRail;
    lv_obj_set_style_bg_color(railBtn[i], lv_color_hex(selected ? COL_ACCENT : COL_BLUE), 0);
    lv_obj_set_style_text_color(railLabel[i], lv_color_hex(selected ? COL_INK : COL_TEXT), 0);
    lv_obj_set_style_bg_color(railBtn[i], lv_color_hex(selected ? COL_DIM : COL_CARD_ON), LV_STATE_PRESSED);
    lv_obj_set_style_opa(railBtn[i], lockActive || holding ? LV_OPA_50 : LV_OPA_COVER, 0);
  }
  if (machine) {
    lv_obj_clear_flag(systemTitle, LV_OBJ_FLAG_HIDDEN);
    lv_label_set_text(systemTitle, activeSet == SET_PUMP ? "Pump service" : "System status");
  } else lv_obj_add_flag(systemTitle, LV_OBJ_FLAG_HIDDEN);
  if (front_ui::showDone(activePage == PAGE_HOME, lockActive)) lv_obj_clear_flag(doneBtn, LV_OBJ_FLAG_HIDDEN);
  else lv_obj_add_flag(doneBtn, LV_OBJ_FLAG_HIDDEN);
  lv_obj_set_style_bg_color(settingsBtn, lv_color_hex(machine ? COL_ACCENT : COL_CARD), 0);
  lv_obj_set_style_text_color(lv_obj_get_child(settingsBtn, 0), lv_color_hex(machine ? COL_INK : COL_TEXT), 0);
  lv_obj_set_style_bg_color(settingsBtn, lv_color_hex(machine ? COL_DIM : COL_CARD_ON), LV_STATE_PRESSED);
  lv_obj_set_style_opa(settingsBtn, lockActive || holding ? LV_OPA_50 : LV_OPA_COVER, 0);
}

static void setRailSelection(RailPage page) {
  activeRail = page;
  refreshShell();
}

static lv_obj_t *buildPane(lv_obj_t *scr) {
  lv_obj_t *o = mkView(scr);
  lv_obj_set_size(o, TASK_W, SCREEN_H - HEADER_H);
  lv_obj_set_pos(o, TASK_X, HEADER_H);
  lv_obj_set_style_pad_all(o, PANE_PAD, 0);
  return o;
}

static void buildHome(lv_obj_t *page) {
  homeTitle = mkText(page, "On tap.", &lv_font_montserrat_40, COL_TEXT);
  lv_obj_set_pos(homeTitle, 0, 0);
  homeGauge = mkView(page);
  lv_obj_set_size(homeGauge, DETAIL_W, 64);
  lv_obj_align(homeGauge, LV_ALIGN_BOTTOM_LEFT, 0, -68);
  homeLevelCaption = mkText(homeGauge, "No level reading", &lv_font_montserrat_24, COL_TEXT);
  lv_obj_align(homeLevelCaption, LV_ALIGN_LEFT_MID, 0, -5);
  for (uint8_t i = 0; i < LEVEL_SEGMENTS; ++i) {
    homeLevelSegments[i] = mkFlat(homeGauge, DETAIL_W - 142 + i * 37, 18, 31, 17, lv_color_hex(COL_OFF));
  }
  mkFlat(page, 0, PANE_H - 69, DETAIL_W, 1, lv_color_hex(0x7699ed));
  lv_obj_t *image = mkBtn(page, 280, 58, COL_BLUE);
  lv_obj_align(image, LV_ALIGN_BOTTOM_LEFT, 0, 0);
  lv_obj_add_event_cb(image, homeSettingsCb, ACT_EVENT, (void *)(intptr_t)FLV_IMAGES);
  lv_obj_align(mkText(image, "Change image " LV_SYMBOL_RIGHT, &lv_font_montserrat_24, COL_TEXT), LV_ALIGN_LEFT_MID, 0, 0);
  lv_obj_t *ratio = mkBtn(page, 120, 58, COL_BLUE);
  lv_obj_align(ratio, LV_ALIGN_BOTTOM_RIGHT, 0, 0);
  lv_obj_add_event_cb(ratio, homeSettingsCb, ACT_EVENT, (void *)(intptr_t)FLV_DETAIL);
  lv_obj_align(mkText(ratio, "Ratio " LV_SYMBOL_RIGHT, &lv_font_montserrat_24, COL_DIM), LV_ALIGN_RIGHT_MID, 0, 0);
}

static void buildFlavor(lv_obj_t *page) {
  lv_obj_t *ratio = mkView(page);
  lv_obj_set_pos(mkText(ratio, "MIXING RATIO", &lv_font_montserrat_20, COL_DIM), 0, 0);
  lv_obj_t *title = mkText(ratio, "Concentrate : water", &lv_font_montserrat_32, COL_TEXT);
  lv_obj_set_pos(title, 0, 36);
  flvRatioMinus = mkBtn(ratio, 66, 66, COL_DIM);
  lv_obj_set_pos(flvRatioMinus, 0, 130);
  lv_obj_add_event_cb(flvRatioMinus, ratioStepCb, ACT_EVENT, (void *)(intptr_t)-1);
  flvRatioMinusMark = mkText(flvRatioMinus, LV_SYMBOL_MINUS, &lv_font_montserrat_28, COL_INK);
  lv_obj_center(flvRatioMinusMark);
  flvRatioPlus = mkBtn(ratio, 66, 66, COL_DIM);
  lv_obj_set_pos(flvRatioPlus, DETAIL_W - 66, 130);
  lv_obj_add_event_cb(flvRatioPlus, ratioStepCb, ACT_EVENT, (void *)(intptr_t)1);
  flvRatioPlusMark = mkText(flvRatioPlus, LV_SYMBOL_PLUS, &lv_font_montserrat_28, COL_INK);
  lv_obj_center(flvRatioPlusMark);
  flvDetailRatio = mkText(ratio, "1 : 20", &lv_font_montserrat_48, COL_TEXT);
  lv_obj_align(flvDetailRatio, LV_ALIGN_TOP_MID, 0, 136);
  lv_obj_set_pos(mkText(ratio, "More flavor", &lv_font_montserrat_20, COL_DIM), 0, 208);
  lv_obj_align(mkText(ratio, "Lighter", &lv_font_montserrat_20, COL_DIM), LV_ALIGN_TOP_RIGHT, 0, 208);
  flvView[FLV_DETAIL] = ratio;

  lv_obj_t *images = mkView(page);
  lv_obj_set_pos(mkText(images, "Choose an image.", &lv_font_montserrat_32, COL_TEXT), 0, 0);
  lv_obj_set_pos(mkText(images, "For the selected flavor", &lv_font_montserrat_20, COL_DIM), 0, 47);
  flvTileStrip = mkView(images);
  lv_obj_set_size(flvTileStrip, DETAIL_W, TILE_BTN_H);
  lv_obj_set_pos(flvTileStrip, 0, TILE_STRIP_Y);
  for (uint8_t i = 0; i < FLAVOR_IMAGE_COUNT; ++i) {
    lv_obj_t *tile = mkBtn(flvTileStrip, TILE_BTN_W, TILE_BTN_H, COL_CARD);
    lv_obj_set_pos(tile, (i % 4) * (TILE_BTN_W + TILE_GAP), 0);
    lv_obj_set_style_border_width(tile, 2, 0);
    lv_obj_set_style_border_color(tile, lv_color_hex(COL_CARD), 0);
    lv_obj_add_event_cb(tile, imagePickCb, ACT_EVENT, (void *)(intptr_t)i);
    lv_obj_t *img = lv_img_create(tile);
    lv_img_set_src(img, &flavorPickerArt[i]);
    lv_obj_align(img, LV_ALIGN_TOP_MID, 0, 5);
    lv_obj_clear_flag(img, LV_OBJ_FLAG_CLICKABLE);
    flvTileMark[i] = mkText(tile, "", &lv_font_montserrat_20, COL_TEXT);
    lv_obj_align(flvTileMark[i], LV_ALIGN_BOTTOM_MID, 0, -7);
    flvTileBtn[i] = tile;
  }
  flvTileLeft = mkBtn(images, 60, 53, COL_BLUE);
  flvTileRight = mkBtn(images, 60, 53, COL_BLUE);
  lv_obj_align(flvTileLeft, LV_ALIGN_BOTTOM_LEFT, 0, 0);
  lv_obj_align(flvTileRight, LV_ALIGN_BOTTOM_RIGHT, 0, 0);
  lv_obj_set_style_border_width(flvTileLeft, 1, 0);
  lv_obj_set_style_border_width(flvTileRight, 1, 0);
  lv_obj_add_event_cb(flvTileLeft, tileStripPageCb, ACT_EVENT, (void *)(intptr_t)-1);
  lv_obj_add_event_cb(flvTileRight, tileStripPageCb, ACT_EVENT, (void *)(intptr_t)1);
  flvTileLeftMark = mkText(flvTileLeft, LV_SYMBOL_LEFT, &lv_font_montserrat_28, COL_TEXT);
  flvTileRightMark = mkText(flvTileRight, LV_SYMBOL_RIGHT, &lv_font_montserrat_28, COL_TEXT);
  lv_obj_center(flvTileLeftMark); lv_obj_center(flvTileRightMark);
  flvTilePosition = mkText(images, "", &lv_font_montserrat_20, COL_TEXT);
  lv_obj_set_style_text_align(flvTilePosition, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_align(flvTilePosition, LV_ALIGN_BOTTOM_MID, 0, -2);
  flvView[FLV_IMAGES] = images;
}

static lv_obj_t *buildTask(lv_obj_t *page, const char *kicker, const char *title,
                           const char *body, const char *action, lv_event_cb_t cb,
                           lv_obj_t **msg, lv_obj_t **button = nullptr) {
  lv_obj_t *view = mkView(page);
  lv_obj_set_pos(mkText(view, kicker, &lv_font_montserrat_20, COL_DIM), 0, 0);
  lv_obj_t *heading = mkText(view, title, &lv_font_montserrat_36, COL_TEXT);
  lv_obj_set_width(heading, DETAIL_W);
  lv_obj_set_pos(heading, 0, 36);
  lv_obj_t *instructions = mkText(view, body, &lv_font_montserrat_24, COL_TEXT);
  lv_obj_set_width(instructions, DETAIL_W);
  lv_obj_set_style_text_line_space(instructions, 6, 0);
  lv_obj_set_pos(instructions, 0, 108);
  lv_obj_t *go = mkBtn(view, DETAIL_W, 66, COL_ACCENT);
  lv_obj_align(go, LV_ALIGN_BOTTOM_LEFT, 0, -5);
  lv_obj_clear_flag(go, LV_OBJ_FLAG_PRESS_LOCK);
  lv_obj_add_event_cb(go, cb, cb == primePadCb ? LV_EVENT_ALL : LV_EVENT_CLICKED, NULL);
  lv_obj_t *label = mkText(go, action, &lv_font_montserrat_24, COL_INK);
  lv_obj_center(label);
  if (button) { *button = go; primePadLbl = label; }
  *msg = mkText(view, "", &lv_font_montserrat_20, COL_WARN);
  lv_obj_set_width(*msg, DETAIL_W);
  lv_obj_set_pos(*msg, 0, 247);
  return view;
}

static void buildService(lv_obj_t *page) {
  // Numeric service IDs remain stable for the serial/J9 diagnostic contract.
  svcView[SVC_PRIME_PICK] = mkView(page);
  svcView[SVC_CLEAN_PICK] = mkView(page);
  svcView[SVC_FILL_PICK] = mkView(page);
  svcView[SVC_PRIME_HOLD] = buildTask(page, "PRIME THIS FLAVOR", "Ready the line.",
      "Place a glass under the faucet.", "Hold to prime", primePadCb, &primeMsg, &primePad);
  svcView[SVC_FILL_CONFIRM] = buildTask(page, "FILL THIS FLAVOR", "Top it up.",
      "Pour concentrate into the top funnel.", "Start filling " LV_SYMBOL_RIGHT,
      fillStartCb, &fillMsg);
  svcView[SVC_CLEAN_CONFIRM] = buildTask(page, "CLEAN THIS FLAVOR", "Time to rinse.",
      "Place a pitcher under the faucet.\n\n3 rinse cycles", "Start cleaning " LV_SYMBOL_RIGHT,
      cleanStartCb, &cleanMsg);
}

static void setSettingsMsg(const char *s) { if (settingsMsg) lv_label_set_text(settingsMsg, s); }

static void settingsAreaCb(lv_event_t *e) {
  showSettings((SettingsView)(intptr_t)lv_event_get_user_data(e));
}
static void settingsBackCb(lv_event_t *e) { (void)e; showSettings(SET_STATUS); }

// A plain outline: a border and nothing inside it.
static lv_obj_t *mkOutline(lv_obj_t *parent, lv_coord_t x, lv_coord_t y, lv_coord_t w,
                           lv_coord_t h, lv_coord_t radius) {
  lv_obj_t *o = lv_obj_create(parent);
  lv_obj_set_size(o, w, h);
  lv_obj_set_pos(o, x, y);
  lv_obj_set_style_bg_opa(o, LV_OPA_TRANSP, 0);
  lv_obj_set_style_border_width(o, 2, 0);
  lv_obj_set_style_border_color(o, lv_color_hex(0x7296e8), 0);
  lv_obj_set_style_radius(o, radius, 0);
  lv_obj_set_style_pad_all(o, 0, 0);
  lv_obj_clear_flag(o, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
  return o;
}

// ── The machine's side profile, with every reed on it ──
// The enclosure seen along X: 462 mm deep, 361 mm tall, the display's 45°
// facet taking 61.9 mm off the top-front arris — the front on the left. The
// cold core stands at the back of the floor, 283 mm long from 173 mm behind the
// front face to its cap at 253.4 mm; the carbonator's tube stands in the middle
// of it and a reservoir pocket at either end, B's forward and A's aft. Each
// reed is drawn at its own station: the four of a column at 57.5, 102.5, 147.5
// and 192.5 mm up the shell on the pocket's outer wall, the carbonator's low and
// high at 99.1 and 127.3 mm on the tube's aft wall. Every figure is in
// millimetres of the machine, scaled once to the card.
#define STATUS_MM_D      462.0f
#define STATUS_MM_H      361.0f
#define STATUS_MM_FACET   61.87f   // 87.5 mm of facet at 45°, on each edge
#define STATUS_MM_CORE_Y0 173.0f
#define STATUS_MM_CORE_Y1 456.0f
#define STATUS_MM_CORE_Z0   6.0f
#define STATUS_MM_CORE_Z1 259.4f
#define STATUS_MM_MID    (STATUS_MM_CORE_Y0 + 141.5f)   // the core's centre, the tube's axis
#define STATUS_MM_REED_DOT 14
#define STATUS_MARGIN      2

// Draws the profile `w` wide at `top` in the card and returns the height it took.
static lv_coord_t buildStatusDiagram(lv_obj_t *card, lv_coord_t w, lv_coord_t top) {
  const float s = (float)(w - 2 * STATUS_MARGIN) / STATUS_MM_D;
  const lv_coord_t h = STATUS_MARGIN * 2 + (lv_coord_t)(STATUS_MM_H * s + 0.5f);
  #define PX(d) (lv_coord_t)(STATUS_MARGIN + (d) * s + 0.5f)
  #define PZ(z) (lv_coord_t)(STATUS_MARGIN + (STATUS_MM_H - (z)) * s + 0.5f)

  lv_obj_t *diag = mkView(card);
  lv_obj_set_size(diag, w, h);
  lv_obj_set_pos(diag, 0, top);

  // The profile, front on the left, the facet at its top-front corner.
  static lv_point_t outline[6];
  outline[0] = {PX(0), PZ(0)};
  outline[1] = {PX(0), PZ(STATUS_MM_H - STATUS_MM_FACET)};
  outline[2] = {PX(STATUS_MM_FACET), PZ(STATUS_MM_H)};
  outline[3] = {PX(STATUS_MM_D), PZ(STATUS_MM_H)};
  outline[4] = {PX(STATUS_MM_D), PZ(0)};
  outline[5] = outline[0];
  lv_obj_t *line = lv_line_create(diag);
  lv_line_set_points(line, outline, 6);
  lv_obj_set_size(line, w, h);
  lv_obj_set_pos(line, 0, 0);
  lv_obj_set_style_pad_all(line, 0, 0);
  lv_obj_set_style_line_width(line, 3, 0);
  lv_obj_set_style_line_color(line, lv_color_hex(COL_DIM), 0);
  lv_obj_set_style_line_rounded(line, true, 0);
  lv_obj_clear_flag(line, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);

  // The cold core, the carbonator's tube in the middle of it, a pocket at each end.
  mkOutline(diag, PX(STATUS_MM_CORE_Y0), PZ(STATUS_MM_CORE_Z1),
            PX(STATUS_MM_CORE_Y1) - PX(STATUS_MM_CORE_Y0),
            PZ(STATUS_MM_CORE_Z0) - PZ(STATUS_MM_CORE_Z1), 4);
  mkOutline(diag, PX(STATUS_MM_MID - 63.5f), PZ(STATUS_MM_CORE_Z0 + 32.0f + 152.4f),
            PX(STATUS_MM_MID + 63.5f) - PX(STATUS_MM_MID - 63.5f),
            PZ(STATUS_MM_CORE_Z0 + 32.0f) - PZ(STATUS_MM_CORE_Z0 + 32.0f + 152.4f), 10);
  static const float kPocket[2] = {+1.0f, -1.0f};   // A aft, B forward
  for (uint8_t i = 0; i < 2; i++) {
    const float y0 = STATUS_MM_MID + kPocket[i] * 78.5f, y1 = STATUS_MM_MID + kPocket[i] * 131.5f;
    const lv_coord_t x0 = PX(y0 < y1 ? y0 : y1), x1 = PX(y0 < y1 ? y1 : y0);
    mkOutline(diag, x0, PZ(STATUS_MM_CORE_Z0 + 213.4f), x1 - x0,
              PZ(STATUS_MM_CORE_Z0 + 2.0f) - PZ(STATUS_MM_CORE_Z0 + 213.4f), 6);
  }

  // The reeds: a column on each pocket's outer wall, a pair on the tube's aft wall.
  static const float kReedZ[4] = {57.5f, 102.5f, 147.5f, 192.5f};
  static const float kCarbZ[2] = {99.1f, 127.3f};
  for (uint8_t i = 0; i < STATUS_REEDS; i++) {
    float d, z;
    if (i < 8) { d = STATUS_MM_MID + (i < 4 ? +134.5f : -134.5f); z = STATUS_MM_CORE_Z0 + kReedZ[i & 3]; }
    else       { d = STATUS_MM_MID + 64.75f;                        z = STATUS_MM_CORE_Z0 + kCarbZ[i - 8]; }
    lv_obj_t *dot = lv_obj_create(diag);
    lv_obj_set_size(dot, STATUS_MM_REED_DOT, STATUS_MM_REED_DOT);
    lv_obj_set_pos(dot, PX(d) - STATUS_MM_REED_DOT / 2, PZ(z) - STATUS_MM_REED_DOT / 2);
    lv_obj_set_style_radius(dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(dot, THEME_BG, 0);
    lv_obj_set_style_border_width(dot, 2, 0);
    lv_obj_set_style_border_color(dot, lv_color_hex(COL_DIM), 0);
    lv_obj_set_style_pad_all(dot, 0, 0);
    lv_obj_clear_flag(dot, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    statusReed[i] = dot;
  }
  #undef PX
  #undef PZ
  return h;
}

// Settings lands on the system status — the machine's profile with every reed on
// it — and the areas a person can go into stand in a column beside it. One so
// far: pump service, which carries the one thing a person does to this machine
// that is not a drink, drying the lines before the pump cartridge is pulled
// (hardware/service/pump-replacement.md). A container goes under the faucet
// first; the button is the commitment, and the lock shows the cycle.
static void buildSettings(lv_obj_t *page) {
  lv_obj_set_pos(page, RAIL_W, HEADER_H);
  lv_obj_set_width(page, SCREEN_W - RAIL_W);
  lv_obj_t *status = mkView(page);
  lv_obj_set_height(status, PANE_H + 8);
  const lv_coord_t diagramHeight = buildStatusDiagram(status, 436, 5);
  statusNote = mkText(status, "Not reading the sensors", &lv_font_montserrat_20, COL_WARN);
  lv_obj_set_pos(statusNote, 0, diagramHeight + 10);
  lv_obj_t *service = mkBtn(status, 186, 64, COL_CARD_ON);
  lv_obj_set_pos(service, 460, 5);
  lv_obj_set_style_border_width(service, 1, 0);
  lv_obj_set_style_border_color(service, lv_color_hex(0x8eacef), 0);
  lv_obj_add_event_cb(service, settingsAreaCb, ACT_EVENT, (void *)(intptr_t)SET_PUMP);
  lv_obj_center(mkText(service, "Pump service " LV_SYMBOL_RIGHT, &lv_font_montserrat_20, COL_TEXT));
  // The cold loop and the refill, in the column under the pump service button:
  // a dim label at the column's left edge and its value beside it, five rows.
  static const char *const thermalLabel[STATUS_THERMAL_ROWS] = {"Tank", "Coil", "Cold", "Refill", "Probes"};
  for (uint8_t i = 0; i < STATUS_THERMAL_ROWS; i++) {
    const lv_coord_t y = 80 + i * 34;
    lv_obj_set_pos(mkText(status, thermalLabel[i], &lv_font_montserrat_20, COL_DIM), 460, y);
    statusThermalValue[i] = mkText(status, "--", &lv_font_montserrat_20, COL_TEXT);
    lv_obj_set_pos(statusThermalValue[i], 548, y);
  }
  setView[SET_STATUS] = status;

  lv_obj_t *pump = mkView(page);
  lv_obj_set_pos(mkText(pump, "Dry the lines.", &lv_font_montserrat_40, COL_TEXT), 0, 0);
  lv_obj_t *body = mkText(pump, "Before pulling the pump cartridge, set a container under the faucet and dry the lines.",
                           &lv_font_montserrat_24, COL_TEXT);
  lv_obj_set_width(body, 580);
  lv_obj_set_style_text_line_space(body, 8, 0);
  lv_obj_set_pos(body, 0, 73);
  lv_obj_t *back = mkBtn(pump, 200, 66, COL_BLUE);
  lv_obj_align(back, LV_ALIGN_BOTTOM_LEFT, 0, -5);
  lv_obj_add_event_cb(back, settingsBackCb, ACT_EVENT, NULL);
  lv_obj_align(mkText(back, LV_SYMBOL_LEFT " Settings", &lv_font_montserrat_24, COL_TEXT), LV_ALIGN_LEFT_MID, 0, 0);
  lv_obj_t *go = mkBtn(pump, 300, 66, COL_ACCENT);
  lv_obj_align(go, LV_ALIGN_BOTTOM_RIGHT, 0, -5);
  lv_obj_clear_flag(go, LV_OBJ_FLAG_PRESS_LOCK);
  lv_obj_add_event_cb(go, dryStartCb, LV_EVENT_CLICKED, NULL);
  lv_obj_center(mkText(go, "Dry the lines " LV_SYMBOL_RIGHT, &lv_font_montserrat_24, COL_INK));
  settingsMsg = mkText(pump, "", &lv_font_montserrat_20, COL_WARN);
  lv_obj_set_width(settingsMsg, 646);
  lv_obj_set_pos(settingsMsg, 0, 245);
  setView[SET_PUMP] = pump;
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
  if (on && !wakeQuiet && !lv_obj_has_flag(lockLogoImg, LV_OBJ_FLAG_HIDDEN)) lv_timer_resume(animTimer);
  else lv_timer_pause(animTimer);
}

static void showFlavor(FlavorView v) {
  activeFlv = v;
  imagePage = 0;
  showOnly(flvView, FLV_COUNT, v);
  refreshFlavorText();
  refreshFlavorImages();
  refreshShell();
  tileDisarm();
}

static void showSettings(SettingsView v) {
  activeSet = v;
  showOnly(setView, SET_COUNT, v);
  if (v == SET_STATUS) { refreshStatusReeds(); refreshStatusThermal(); }
  if (v == SET_PUMP)   setSettingsMsg("");
  refreshShell();
}

static void showService(ServiceView v) {
  if (v == SVC_PRIME_PICK || v == SVC_FILL_PICK || v == SVC_CLEAN_PICK) {
    showPage(PAGE_HOME);
    return;
  }
  const ServiceView previous = activeSvc;
  if (previous == SVC_PRIME_HOLD && v != SVC_PRIME_HOLD &&
      !primeAuthoritativeNavigation) {
    primeSessionCancel();
  }
  // Every one of these views is reached by picking a channel, and each carries
  // that channel's logo forward. The pick moves flavorSel, so the images it
  // stands in front of are repointed here rather than in each caller.
  if (uiReady) refreshFlavorImages();
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
        // the session and let the main board's short lease close it silently;
        // sending CANCEL here would make the sleeping appliance tick.
        primeSessionDesired = false;
        primeSessionCancelPending = false;
        primeUsbStartPending = false;
        primeTouchStartPending = false;
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
    else if (activePage == PAGE_SETUP)  showSettings(SET_STATUS);
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
  tileDisarm();
  if (operationResultVisible) {
    operationResultVisible = false;
    fillLockShown = cleanLockShown = airLockShown = false;
    fillCardUntilMs = cleanCardUntilMs = airCardUntilMs = 0;
    lockScreenHide();
  }
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
  if (p == PAGE_SERVICE) { activeSvc = SVC_PRIME_PICK; showOnly(svcView, SVC_COUNT, -1); }
  if (p == PAGE_SETUP)   showSettings(SET_STATUS);
  refreshFlavorImages();
  refreshShell();
}

static void showRail(RailPage p) {
  switch (p) {
    case RAIL_CHOOSE:
      showPage(PAGE_HOME);
      break;
    case RAIL_PRIME:
      showPage(PAGE_SERVICE);
      showService(SVC_PRIME_HOLD);
      break;
    case RAIL_FILL:
      showPage(PAGE_SERVICE);
      showService(SVC_FILL_CONFIRM);
      break;
    case RAIL_CLEAN:
      showPage(PAGE_SERVICE);
      showService(SVC_CLEAN_CONFIRM);
      break;
    default:
      showPage(PAGE_HOME);
      break;
  }
}

// A customer page, asked for by the main board's console: the same handlers a
// finger reaches, so what the bench camera photographs is the real path.
static bool uiShow(const UiShowPayload &req) {
  if (!uiReady || lockActive || holding) return false;
  const bool hasChannel = req.channel != UI_CHANNEL_NONE;
  const uint8_t channel = req.channel & 1;
  if (screenIdle) wake();
  flavorSel = hasChannel ? channel : activeFlavor;
  switch (req.rail) {
    case UI_RAIL_CHOOSE:
      if (hasChannel) { flavorSel = channel; showPage(PAGE_FLAVOR); showFlavor(req.act ? FLV_IMAGES : FLV_DETAIL); }
      else showRail(RAIL_CHOOSE);
      return true;
    case UI_RAIL_PRIME:
      showRail(RAIL_PRIME);
      if (hasChannel) { flavorSel = channel; showService(SVC_PRIME_HOLD); }
      return true;
    case UI_RAIL_FILL:
      showRail(RAIL_FILL);
      if (hasChannel) {
        flavorSel = channel;
        showService(SVC_FILL_CONFIRM);
        if (req.act) fillStartCb(nullptr);
      }
      return true;
    case UI_RAIL_CLEAN:
      showRail(RAIL_CLEAN);
      if (hasChannel) {
        flavorSel = channel;
        showService(SVC_CLEAN_CONFIRM);
        if (req.act) cleanStartCb(nullptr);
      }
      return true;
    case UI_RAIL_SETTINGS:
      showPage(PAGE_SETUP);
      if (req.act) { showSettings(SET_PUMP); dryStartCb(nullptr); }
      return true;
    case UI_RAIL_PUMP_SERVICE:
      showPage(PAGE_SETUP);
      showSettings(SET_PUMP);
      if (req.act) dryStartCb(nullptr);
      return true;
    default:
      return false;
  }
}

static void buildUi() {
  // The user's own pictures, mapped out of the partition nothing else uses.
  // Opened before the descriptors bind, because a custom slot is a pointer
  // into it. A board with no store still has its four factory faces.
  imageStoreBegin("spiffs", kLogoSizes,
                  (uint8_t)(sizeof(kLogoSizes) / sizeof(kLogoSizes[0])));

  animBase = boardArtMap(NUM_ANIM_FRAMES, LOGO_SIZE, LOGO_SIZE);
  for (uint8_t i = 0; i < NUM_ANIM_FRAMES; i++) {
    frameDsc[i].header.cf = LV_IMG_CF_TRUE_COLOR;
    frameDsc[i].header.always_zero = 0;
    frameDsc[i].header.w = LOGO_SIZE;
    frameDsc[i].header.h = LOGO_SIZE;
    frameDsc[i].data_size = LOGO_SIZE * LOGO_SIZE * sizeof(uint16_t);
    frameDsc[i].data = (const uint8_t *)animFrame(i);
  }
  bindFlavorLogos();
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
  buildTestScreen(scr);   // above the lock: the camera reads it through anything

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
    Serial.printf("VERSION:ENCLOSURE=%s\n", FW_VERSION);
  } else if (strcmp(line, "GET_STATE") == 0) {
    Serial.printf("STATE:FLAVOR=%u,SYNC=%d,PERSISTED=%d,PERSISTERR=%d,PENDING=%d,LOCK=%d,IDLE=%d,PAGE=%d,PRIME=%u,PRIMECH=%u,OWNER=%u\n",
                  (unsigned)activeFlavor,
                  flavorSynchronized ? 1 : 0,
                  flavorMainBoardPersisted ? 1 : 0,
                  flavorMainBoardPersistError ? 1 : 0,
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
    Serial.printf("DIAG:page=%d,svc=%d,flv=%d,lock=%d,stage=%u,idle=%d,told=%d,asleep=%d,window=%lu,holding=%d,"
                  "gt911=0x%02X,reinits=%lu,sendErr=%d,outQ=%u/%u,outDrop=%lu,"
                  "link=%s,ctrlRx=%lu,ctrlTurnMax=%u,ctrlTurnOver=%lu,"
                  "flushes=%lu,maxLoopMs=%lu,heap=%lu,minHeap=%lu\n",
                  (int)activeRail, (int)activeSvc, (int)activeFlv,
                  lockActive ? 1 : 0, (unsigned)idleStage, screenIdle ? 1 : 0,
                  idleAsleepKnown ? 1 : 0, idleAsleepWanted ? 1 : 0,
                  (unsigned long)idleWindowMs,
                  holding ? 1 : 0, gt911Addr, (unsigned long)linkReinits,
                  lastSendErr, (unsigned)outCount, (unsigned)outHighWater,
                  (unsigned long)outDropped, j9.framesRx ? "rx" : "silent",
                  (unsigned long)ctrlStatus.framesRx,
                  (unsigned)ctrlStatus.j9ReplyHighWater,
                  (unsigned long)ctrlStatus.j9ReplyOverruns,
                  (unsigned long)flushCount, (unsigned long)maxLoopMs,
                  (unsigned long)ESP.getFreeHeap(), (unsigned long)ESP.getMinFreeHeap());
    Serial.printf("DIAG_UI:set=%d,images=%u,selected=%u,flavorSync=%d,flavorSaved=%d,flavorPending=%d,flavorRetries=%lu,"
                  "flavorStale=%lu,bridged=%lu,stale=%lu,touch=%lu,lastXY=%u/%u\n",
                  (int)activeSet, (unsigned)imagePage, (unsigned)activeFlavor, flavorSynchronized ? 1 : 0,
                  flavorMainBoardPersisted ? 1 : 0, flavorRequestPending ? 1 : 0,
                  (unsigned long)flavorRetries, (unsigned long)flavorStaleResponses,
                  (unsigned long)touchBridged, (unsigned long)gt911Stale,
                  (unsigned long)touchCount, (unsigned)lastTouchX, (unsigned)lastTouchY);
    Serial.printf("DIAG_SYS:silentMs=%lu,psram=%lu,freePsram=%lu,bl=%d,frame=%u,uptime=%lus\n",
                  j9SilentSinceMs ? (unsigned long)(millis() - j9SilentSinceMs) : 0UL,
                  (unsigned long)ESP.getPsramSize(),
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
  } else if (strncmp(line, "TEST:", 5) == 0) {
    testScreenShow((uint16_t)atoi(line + 5));
    Serial.printf("OK:TEST=%d\n", testActive ? 1 : 0);
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
    // and keeps a number here anyway, so a bring-up script can still reach it;
    // 5 is its pump service area.
    int p = atoi(line + 5);
    if (p == RAIL_PAGE_COUNT) { showPage(PAGE_SETUP); Serial.printf("OK:PAGE=%d\n", p); }
    else if (p == RAIL_PAGE_COUNT + 1) {
      showPage(PAGE_SETUP); showSettings(SET_PUMP); Serial.printf("OK:PAGE=%d\n", p);
    }
    else if (p < 0 || p > RAIL_PAGE_COUNT + 1) Serial.println("ERR:PAGE expects 0..5");
    else { showRail((RailPage)p); Serial.printf("OK:PAGE=%d\n", p); }
  } else if (strncmp(line, "CLICK:", 6) == 0) {
    if (line[6] != '0' && line[6] != '1') Serial.println("ERR:CLICK expects 0 or 1");
    else { clickSend = (line[6] == '1'); Serial.printf("OK:CLICK=%d\n", clickSend ? 1 : 0); }
  } else if (strncmp(line, "SOUND:", 6) == 0) {
    // The click's whole path, without a finger on the glass. This panel has no
    // sounder, so anything heard after this is the frame having crossed J9 and
    // reached U8 on the main board — which is the one direction a touch travels,
    // and the one a line test cannot otherwise exercise without an operator.
    int id = atoi(line + 6);
    if (id < 1 || id > SND_WIRE_ALARM) Serial.printf("ERR:SOUND expects 1..%d\n", SND_WIRE_ALARM);
    else { sendSound((uint8_t)id); Serial.printf("OK:SOUND=%d\n", id); }
  } else if (strncmp(line, "FILL:START:", 11) == 0) {
    // The confirm page's START, without a finger on the glass: same frame,
    // same answer, same lock.
    int f = atoi(line + 11);
    if (f != 1 && f != 2) { Serial.println("ERR:FILL:START expects 1 or 2"); }
    else {
      flavorSel = (uint8_t)(f - 1);
      showRail(RAIL_FILL);
      showService(SVC_FILL_CONFIRM);
      fillStartCb(nullptr);
      Serial.printf("OK:FILL:START=%d\n", f);
    }
  } else if (strcmp(line, "FILL:STOP") == 0) {
    fillStopCb(nullptr);
    Serial.println("OK:FILL:STOP");
  } else if (strncmp(line, "CLEAN:START:", 12) == 0) {
    // The confirm page's START CLEAN CYCLE, without a finger on the glass.
    int f = atoi(line + 12);
    if (f != 1 && f != 2) { Serial.println("ERR:CLEAN:START expects 1 or 2"); }
    else {
      flavorSel = (uint8_t)(f - 1);
      showRail(RAIL_CLEAN);
      showService(SVC_CLEAN_CONFIRM);
      cleanStartCb(nullptr);
      Serial.printf("OK:CLEAN:START=%d\n", f);
    }
  } else if (strcmp(line, "CLEAN:STOP") == 0) {
    cleanStopCb(nullptr);
    Serial.println("OK:CLEAN:STOP");
  } else if (strcmp(line, "AIR:DRY") == 0) {
    // Settings' PUMP SERVICE → DRY THE LINES, without a finger on the glass.
    showPage(PAGE_SETUP);
    showSettings(SET_PUMP);
    dryStartCb(nullptr);
    Serial.println("OK:AIR:DRY");
  } else if (strcmp(line, "AIR:STOP") == 0) {
    airStopCb(nullptr);
    Serial.println("OK:AIR:STOP");
  } else if (strncmp(line, "PRIME:START:", 12) == 0) {
    // Enter the shared session, then start the same tokenized hold as soon as
    // the main board's READY answer lands. PRIME:STOP releases that synthetic
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
  } else if (strcmp(line, "ART") == 0) {
    BoardArtHeader h;
    if (!boardArtHeader(h)) {
      Serial.println("ART:none — no art partition, or it could not be mapped");
    } else {
      Serial.printf("ART:magic=%08lX format=%lu count=%lu %ux%u crc=%08lX mapped=%d\n",
                    (unsigned long)h.magic, (unsigned long)h.format,
                    (unsigned long)h.count, h.w, h.h, (unsigned long)h.crc32,
                    animBase ? 1 : 0);
    }
  } else if (strcmp(line, "ART:VERIFY") == 0) {
    // Walks 3.96 MB, so it is asked for rather than done at boot.
    Serial.printf("ART:VERIFY=%s\n", boardArtVerify() ? "PASS" : "FAIL");
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
  Serial.println("ESP32-S3 Enclosure Display starting...");

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

  // An update owns the board once it starts: the panel is already stopped and
  // nothing else should be drawing, polling, or sleeping it.
  otaService();
  if (wifiBenchRebootWanted()) esp_restart();
  if (otaAnyActive() || otaRebootPending) {
    j9.service();
    j9Pump();
    delay(1);   // the loop owns the CPU here; the idle task still has to run
    return;
  }

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

  // A press that spoke for itself needs no click frame: the main board ticks on
  // the command it received. Only a press that said nothing else sends one, and
  // it goes out here rather than from inside the LVGL callback, so one press can
  // never put two frames on the pair back to back. The main board reads either
  // frame as presence, so only a silent press has to report itself.
  const bool pressSpoke = clickPending;
  if (clickPending) {
    clickPending = false;
    if (j9.framesTx == framesTxAtPress) sendSound(SND_WIRE_TICK);
  }
  if (touchPending) {
    touchPending = false;
    if (!pressSpoke) j9Post(MSG_TOUCH, nullptr, 0);
    // Whichever frame carried it, the main board owes an awake idle state back.
    // Arming on the press rather than on the send covers the command path too:
    // a flavor select is presence, and one that is lost is presence lost.
    if (!touchUnconfirmedSince) {
      touchUnconfirmedSince = millis() ? millis() : 1;
      touchConfirmRetryMs = millis();
    }
  }

  // Say it again until it is heard, then stop. A pair being rebuilt under the
  // watchdog loses the frames in flight across the rebuild; this is what makes
  // a tap survive that rather than needing a second tap.
  if (touchUnconfirmedSince) {
    if (millis() - touchUnconfirmedSince >= TOUCH_CONFIRM_GIVEUP_MS) {
      touchUnconfirmedSince = 0;   // the link is past a retry's help
    } else if (millis() - touchConfirmRetryMs >= TOUCH_CONFIRM_RETRY_MS) {
      touchConfirmRetryMs = millis();
      j9Post(MSG_TOUCH, nullptr, 0);
    }
  }

  tilePickService();   // a tile chosen only once its gesture is not a drag
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

  // RUNNING elapsed is anchored to the main board's heartbeat and smoothed
  // locally between answers. Only the small readout and bar move at 10 Hz.
  if (primeSessionKnown && primeSessionToken != 0 &&
      primeSession.sessionToken == primeSessionToken &&
      primeSession.phase == PRIME_SESSION_RUNNING &&
      activePage == PAGE_SERVICE && activeSvc == SVC_PRIME_HOLD &&
      millis() - primeLastUiMs >= 100) {
    primeLastUiMs = millis();
  }

  fillService();
  cleanService();
  airService();
  ratioService();

  // The status request keeps main board truth fresh once a second whenever a
  // shared prime hold does not own the pair.
  if (uiReady && !screenIdle && !primeLinkOwnsJ9()) {
    // The main board no longer speaks unprompted — a prime that timed out or a
    // pump that finished waits for a frame to answer. This poll is what collects
    // those, so it is the ceiling on how stale news from the base can be. A poll
    // pair is ~50 bytes; at 460800 that is a quarter of a percent of the pair.
    if (millis() - statusAskedMs >= 1000) {
      statusAskedMs = millis();
      j9Post(MSG_STATUS_REQ, nullptr, 0);
    }
  }

  // Recovery is the link's own business, so it runs on every pass rather than
  // beside the poll that used to notice — the background flavor query keeps the
  // pair busy while this glass is dark, and that is exactly when a wedge here
  // makes the whole machine unreachable rather than only this screen. Shares the
  // prime backoff clock: both reinit the same transport, and one that has just
  // been rebuilt deserves longer than this window to answer.
  if (j9SilentSinceMs && millis() - j9SilentSinceMs >= J9_SILENT_MS &&
      millis() - primeLastReinitMs >= PRIME_REINIT_BACKOFF_MS) {
    primeLastReinitMs = millis();
    j9Reinit("no answer for 3s");
  }

  // Choose's cached refresh does no LVGL work while the main board's selection
  // and persistence state are unchanged; this timer lets a stale link cross
  // the two-second threshold without a standing diagnostic on the glass.
  if (uiReady && !screenIdle) {
    static unsigned long lastSlow = 0;
    if (millis() - lastSlow >= 1000) {
      lastSlow = millis();
      padWatch();
      if (activePage == PAGE_HOME)   refreshHomeSelection();
      if (activePage == PAGE_SETUP)  { refreshStatusReeds(); refreshStatusThermal(); }
  refreshHomeLevel();
    }
  }

  // Going dark is the main board's call, made across both glasses at once — see
  // applyIdleState(). An active operation lock and a live hold still hold it off
  // here, because those are this panel's own business.
  if (testActive && (long)(millis() - testUntilMs) >= 0) testScreenHide();

  if (displayReady && !screenIdle && idleAsleepKnown && idleAsleepWanted &&
      !holding && !lockActive && !testActive && !touchUnconfirmedSince) {
    const bool primeRunning = primeSessionKnown && !primeLinkLost &&
                              primeSession.phase == PRIME_SESSION_RUNNING;
    if (!primeRunning) {
      screenIdle = true;
      idleStage = 1;
      darkSince = millis();
      setBacklight(false);
      if (animTimer) lv_timer_pause(animTimer);
    }
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
