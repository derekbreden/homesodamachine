#include <Arduino.h>

#include "fw_version.h"
#include "fw_build_time.h"   // churns every build; the banner is what reads it
#include "faucet_link.h"
#include "flavor.h"
#include "identity.h"
#include "versions.h"
#include "idle.h"
#include "link.h"
#include "machine.h"
#include "pins.h"
#include "rtc.h"
#include "sound.h"
#include "proto_msg.h"   // the channel numbers and the prime ceiling the glass uses

// ════════════════════════════════════════════════════════════
//  Home Soda Machine — appliance controller
// ════════════════════════════════════════════════════════════
//
// Runs on the main board's ESP32-WROOM-32E (U1). That board is
// hardware/pcb/pcba/pcba.tsx, drawn as hardware/wiring/esp32-pinout.mmd,
// and hardware/assembly/firmware-and-commissioning.md is the procedure
// this answers to.
//
// Three limits the parts impose, each one the firmware's alone to hold —
// §9 of that procedure queries all three per unit:
//
//   1. At most 3 solenoid valves energized at once. Eight coils on
//      MANIFOLD A draw past J1's COM contact rating and land in one
//      TBD62083. hardware/wiring/ac-wiring-schedule.md, "Solenoid COM
//      current budget".
//   2. Relay #2 (IO2) de-energized while a dispense is open. The main board
//      peaks at 3.33 A and the SeaFlo at 5 A on one 6.7 A supply. The
//      carbonator's low reed asserts mid-pour, so the refill it queues
//      waits for the dispense window to close.
//   3. GPPU written on both MCP23017s. No loom carries a resistor and
//      the main board pulls none of the reed inputs, so a reed with no
//      pull-up floats.
//
// machine.cpp and its pcba_expanders driver hold all three, and machine.cpp owns
// every request that can reach a load. The
// commissioning and service commands (firmware-and-commissioning.md §6, §7,
// §9) ask it for a thing — `selftest valves` walks the census — and so does
// the glass. The surface that writes a pin directly is src_pcba_bench, which
// runs on a bare board with the manifold unplugged.
//
// ── What this build does ──────────────────────────────────────────────
// One flavor pump turns, held from either display inside an enclosure-opened
// prime session or bounded from the console.
// Both MCP23017s boot with every output verified low and every reed input on
// its internal pull-up; status reads those inputs on explicit request. No
// operation opens a valve or runs the fan, neither relay is ever driven, and
// a clean cycle is answered MSG_ERR_UNSUPPORTED.

#include "ota.h"

static void console(const String &line);

void setup() {
    machineBegin();   // actuators parked before anything else runs — including U8's coil

    // The console carries whole firmware images during an update, and at the
    // rate a transfer raises it to, the default 256-byte ring empties in under
    // three milliseconds — less than one pass of this loop. Anything dropped
    // there is a chunk that never arrives and a transfer that stops dead.
    Serial.setRxBufferSize(8192);
    Serial.begin(115200);
    while (!Serial && millis() < 2000) {}
    Serial.printf("\nhomesodamachine appliance  %s  (%s)\n", FW_VERSION, FW_BUILD_TIME);

    identityBegin();
    versionsBegin();
    flavorBegin();
    idleBegin();

    // The clock quiet hours reads. Without it soundInQuietHours() is false for
    // good — a machine that guessed the hour would go quiet at the wrong one.
    rtcBegin();
    soundSetClock(rtcHour);
    {
        char when[48];
        rtcStamp(when, sizeof(when));
        Serial.printf("U6 DS3231: %s\n", when);
    }
    Serial.printf("sound: volume %u%%, quiet hours %s%s\n", soundVolume(),
                  soundQuietOn() ? "on" : "off",
                  soundInQuietHours() ? " — in force now" : "");

    Serial.printf("U2/U3 MCP23017: %s\n",
                  machineIoReady()
                      ? "outputs parked low, reed pull-ups enabled"
                      : "FAULT — outputs could not be verified parked");

    linkBegin();
    Serial.printf("J9 up on IO%d/IO%d @ %ld — enclosure prime sessions arrive here\n",
                  PIN_485_DI, PIN_485_RO, RS485_BAUD);
    faucetLinkBegin();
    Serial.printf("J3 up on IO%d/IO%d @ %ld — faucet flavor and prime controls\n",
                  PIN_FAUCET_TX, PIN_FAUCET_RX, FAUCET_BAUD);
    Serial.println("idle — actuators dark; valves have no runtime command");
    Serial.println("type 'help' for what this build answers to\n");
    Serial.print("> ");

    // The machine waking up. Every actuator is already parked by the time this
    // sounds, so it says the main board reached the end of setup() and nothing
    // else — which on a line is how a unit is heard coming up without being
    // watched, and in a kitchen is just the machine saying hello.
    soundPlay(machineIoReady() ? SND_WELCOME : SND_FAULT);
}

static void relayOwe(uint8_t slot);
static void relayService();
static void reconcileService();
static void removePicture(uint8_t slot, bool tellFaucet);

void loop() {
    // Expired heartbeat/session deadlines are terminal before either transport
    // may apply buffered input. A tick that sat behind a >2 s scheduler stall
    // cannot revive an already-overdue energized pump.
    machineService();   // the deadlines a held pump is measured against
    linkService();      // J9 frames in, replies out
    faucetLinkService();// J3 frames in, replies out
    versionsService();  // ask each display what it is running
    soundService();     // U8's step boundaries — nothing here blocks, and it must
                        // run every pass: LEDC keeps oscillating on its own, so a
                        // sequencer that stops being serviced holds the coil on.

    // Preferences can occasionally compact a flash page. Keep that work out of
    // every pump deadline and sound step; the logo already changed locally.
    if (machineState() == ST_IDLE && !soundBusy()) flavorService();

    // A picture the faucet has taken in, carried the last hop. This blocks for
    // seconds and takes the enclosure's panel down with it, so it waits for a
    // dark machine and for the sounder to finish — and the phone is long gone
    // by then, because nothing about the upload waited on this.
    if (machineState() == ST_IDLE && !soundBusy()) {
        const uint8_t slot = faucetLinkTakeRelayRequest();
        if (slot != 0xFF) relayOwe(slot);
        relayService();
    }

    // A picture removed from the phone. The faucet has dropped its own copy and
    // told the machine; the rest of the removal is the machine's.
    if (machineState() == ST_IDLE) {
        const uint8_t gone = faucetLinkTakeEraseRequest();
        if (gone != 0xFF) removePicture(gone, false);
    }

    // And whatever the two stores were never told, or were told while nobody
    // was listening.
    reconcileService();

    // Presence crosses both links, so a change is published to whichever glass
    // gives the main board its next turn.
    if (idleService()) {
        // An offered action is withdrawn with the light. Both glasses learn of
        // the sleep and the closed session from the same pair of publications.
        if (idleAsleep()) {
            MachinePrimeSessionState prime;
            machineReadPrimeSessionState(prime);
            if (prime.phase != PRIME_SESSION_OFF)
                machinePrimeSessionCancel(prime.sessionToken);
        }
        linkPublishIdle();
        faucetLinkPublishIdle();
        Serial.printf("\n[idle] %s\n", idleAsleep() ? "asleep" : "awake");
    }

    otaService();

    // While a transfer is open the console is a byte pipe, not a line reader:
    // the host owes an exact count and those bytes are not text.
    if (otaAwaitingHostBytes()) { otaFeedHostBytes(); return; }

    static String line;
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\r' || c == '\n') {
            if (line.length()) { console(line); Serial.print("\n> "); }
            line = "";
        } else if (line.length() < 64) {
            line += c;
        }
    }
}

// ── Console ───────────────────────────────────────────────────────────────
// The same intents the glass reaches, from a keyboard. Every one of them goes
// through machine.h; there is no command here that writes a pin.

static void help() {
    Serial.println("\n  pump <a|b> [ms]   run one flavor pump, bounded (default 2000, ceiling 60000)");
    Serial.println("  stop              end whatever is running");
    Serial.println("  status            machine state, uptime, heap");
    Serial.println("  flavor [a|b]      selected flavor (main-board-owned and persisted)");
    Serial.println("  link              J9 enclosure display and J3 faucet links");
    Serial.println("  ping              put a frame on the pair and read its echo back");
    Serial.println("  display usb       make the externally-powered display reattach to USB");
    Serial.println("  wake              light both glasses, as a finger on either would");
    Serial.println("  sound <name>      play one of the machine's sounds; 'sound list' names them");
    Serial.println("  volume [0-100]    how loud everything but the alarm is (persisted)");
    Serial.println("  quiet [on|off] [start] [end] [pct]   quiet hours, off the DS3231 (persisted)");
    Serial.println("  rtc [set <YYYY-MM-DD> <HH:MM:SS>]    the clock quiet hours reads");
    Serial.println("  ota [<self|faucet|enclosure> <size> <crc32>]   firmware over the link");
    Serial.println("  help              this");
    Serial.println("\n  The enclosure opens prime mode for one flavor. Either display can then");
    Serial.println("  own the held pump; it stops on lift, a stale hold/session, disconnect, or at");
    Serial.printf("  the %lu s ceiling.\n", (unsigned long)(PRIME_MAX_MS / 1000));
}

static void status() {
    Serial.printf("\n%s  %s\n", FW_VERSION, FW_BUILD_TIME);
    Serial.printf("  state    %s", machineStateName());
    if (machineState() == ST_PUMPING)
        Serial.printf(" — pump %s, %lu ms in%s", machinePumpName(machinePumpChannel()),
                      (unsigned long)machinePumpElapsedMs(),
                      machineIsPriming() ? " (held from the glass)" : "");
    Serial.printf("\n  uptime   %lu s\n", millis() / 1000);
    Serial.printf("  heap     %lu bytes free\n", (unsigned long)ESP.getFreeHeap());
    Serial.printf("  flavor   %s — %s%s\n", machinePumpName(flavorSelected()),
                  flavorEstablished() ? "main-board-owned" : "awaiting first faucet sync",
                  flavorPersisted() ? ", persisted" : ", persistence pending");
    MachineIoStatus io;
    const bool ioHealthy = machineReadIoStatus(io);
    Serial.printf("  expanders %s — cfg=%s, plan=%s, parked=%s, OLATA=%02X/%02X, GPPUB=%02X/%02X\n",
                  ioHealthy ? "healthy" : "FAULT",
                  io.configurationVerified ? "ok" : "bad",
                  io.outputsMatchPlan ? "ok" : "bad",
                  io.outputsKnownParked ? "yes" : "NO",
                  io.outputLatchA20, io.outputLatchA21, io.pullupsB20, io.pullupsB21);
    if (io.reedsValid) {
        Serial.printf("  reeds    raw=%02X/%02X, closed A=%X B=%X, carbonator low=%s high=%s\n",
                      io.rawReedsA, io.rawReedsB,
                      io.reservoirAClosedMask, io.reservoirBClosedMask,
                      io.carbonatorLowClosed ? "yes" : "no",
                      io.carbonatorHighClosed ? "yes" : "no");
    } else {
        Serial.printf("  io fault %s at 0x%02X register 0x%02X\n",
                      machineIoFaultName(io.fault), io.faultAddress, io.faultRegister);
    }
    Serial.println("  valves   parked — no runtime valve/fan command in this image");
    Serial.println("  relays   unimplemented — IO2 and IO19 parked as inputs");

    char when[48];
    rtcStamp(when, sizeof(when));
    Serial.printf("  clock    %s\n", when);
    Serial.printf("  gas      %s (%u mV on the divided DOUT)\n",
                  machineGasTripped() ? "TRIPPED — alarm sounding" : "clear",
                  (unsigned)analogReadMilliVolts(PIN_GAS_DOUT));
    Serial.printf("  volume   %u%%", soundVolume());
    if (soundQuietOn())
        Serial.printf(", quiet hours %02u:00-%02u:00 at %u%%%s",
                      soundQuietStart(), soundQuietEnd(), soundQuietVolume(),
                      soundInQuietHours() ? " — IN FORCE" : "");
    else
        Serial.print(", quiet hours off");
    Serial.println();
    if (soundBusy()) {
        const Sound *sp = soundInfo(soundPlaying());
        Serial.printf("  sounding %s\n", sp ? sp->name : "?");
    }
}

// ── Sound ─────────────────────────────────────────────────────────────────
static SoundId soundByName(const String &name) {
    for (uint8_t i = 1; i < SND_COUNT; i++) {
        const Sound *sp = soundInfo((SoundId)i);
        if (sp && name.equalsIgnoreCase(sp->name)) return (SoundId)i;
    }
    return SND_NONE;
}

// What each sound is worth, spelled out: the priority that decides whether it
// survives a collision, and the level it would actually play at right now — which
// is 0 for everything but the alarm once volume reaches 0.
static void soundList() {
    Serial.println("\n  name     priority  plays at  notes");
    static const char *kPrio[] = {"ui", "event", "fault", "ALARM"};
    for (uint8_t i = 1; i < SND_COUNT; i++) {
        const Sound *sp = soundInfo((SoundId)i);
        if (!sp) continue;
        uint8_t lvl = soundLevelFor((SoundId)i);
        Serial.printf("  %-8s %-9s %4u%%     %s%s\n", sp->name, kPrio[sp->priority], lvl,
                      (sp->flags & SND_F_UNSILENCEABLE) ? "cannot be silenced" : "",
                      sp->repeats == SOUND_FOREVER ? " — loops until stopped" : "");
    }
    Serial.println("\n  A request below what is already sounding is dropped, not queued:");
    Serial.println("  there is one coil, and a tick arriving mid-chime is worth less than");
    Serial.println("  the chime finishing.");
}

static void cmdSound(const String &line) {
    String rest = line.substring(5); rest.trim();
    if (!rest.length() || rest == "list") { soundList(); return; }
    if (rest == "stop") { soundStop(); Serial.println("\nstopped"); return; }
    SoundId id = soundByName(rest);
    if (id == SND_NONE) { Serial.printf("\nno sound called '%s' — 'sound list'\n", rest.c_str()); return; }
    uint8_t lvl = soundLevelFor(id);
    Serial.printf("\n%s at %u%%%s\n", rest.c_str(), lvl,
                  lvl ? "" : " — silenced, so nothing will be heard");
    soundPlay(id);
}

static void cmdVolume(const String &line) {
    String rest = line.substring(6); rest.trim();
    if (rest.length()) {
        int v = rest.toInt();
        if (v < 0 || v > 100) { Serial.println("\nusage: volume <0-100>"); return; }
        soundSetVolume((uint8_t)v);
        soundPlay(SND_ACK);   // heard at the level just set, which is the point
    }
    Serial.printf("\nvolume %u%% (persisted)%s\n", soundVolume(),
                  soundVolume() ? "" : " — muted; the gas alarm still sounds");
}

static void cmdQuiet(const String &line) {
    String rest = line.substring(5); rest.trim();
    if (rest.length()) {
        // quiet <on|off> [startHour] [endHour] [pct]
        int sp1 = rest.indexOf(' ');
        String onOff = sp1 < 0 ? rest : rest.substring(0, sp1);
        onOff.toLowerCase();
        if (onOff != "on" && onOff != "off") {
            Serial.println("\nusage: quiet <on|off> [startHour] [endHour] [pct]");
            return;
        }
        uint8_t st = soundQuietStart(), en = soundQuietEnd(), pc = soundQuietVolume();
        if (sp1 >= 0) {
            String tail = rest.substring(sp1 + 1); tail.trim();
            int a = -1, b = -1, c = -1, n = sscanf(tail.c_str(), "%d %d %d", &a, &b, &c);
            if (n >= 1 && a >= 0 && a <= 23) st = (uint8_t)a;
            if (n >= 2 && b >= 0 && b <= 23) en = (uint8_t)b;
            if (n >= 3 && c >= 0 && c <= 100) pc = (uint8_t)c;
        }
        soundSetQuiet(onOff == "on", st, en, pc);
    }
    Serial.printf("\nquiet hours %s, %02u:00-%02u:00 at %u%% (persisted)\n",
                  soundQuietOn() ? "on" : "off", soundQuietStart(), soundQuietEnd(),
                  soundQuietVolume());
    if (soundQuietOn() && !rtcValid())
        Serial.println("  the clock is unset, so they will never engage — 'rtc set' first");
    else if (soundInQuietHours())
        Serial.println("  in force right now");
}

static void cmdRtc(const String &line) {
    String rest = line.substring(3); rest.trim();
    if (rest.startsWith("set")) {
        int y, mo, d, h, mi, se;
        if (sscanf(rest.c_str() + 3, "%d-%d-%d %d:%d:%d", &y, &mo, &d, &h, &mi, &se) != 6) {
            Serial.println("\nusage: rtc set <YYYY-MM-DD> <HH:MM:SS>");
            return;
        }
        Serial.println(rtcSet(y, mo, d, h, mi, se)
                       ? "\nset — OSF cleared, EOSC cleared so it runs on BT1"
                       : "\nrefused — out of range, or the RTC did not answer");
    }
    char when[48];
    rtcStamp(when, sizeof(when));
    float t;
    Serial.printf("\nU6 DS3231 at 0x68: %s\n", when);
    if (rtcTemp(&t)) Serial.printf("  die temp %.2f C — the oscillator block is powered\n", t);
    Serial.printf("  quiet hours %s read this clock\n", rtcValid() ? "can" : "CANNOT");
}

// ── The radio bench ───────────────────────────────────────────────────────
// Both displays carry a WiFi radio that no product path uses, and the wired
// links carry every image the machine has to move. This measures the one
// against the other: the enclosure sinks, the faucet sends, and the main board
// is not on the path it is timing.
static void cmdWifi(const String &line) {
    String rest = line.substring(4);
    rest.trim();

    // Raising the AP is a main-board-originated frame on J9 and it retries, so
    // this call can hold the loop for seconds. Nothing that stops a pump runs
    // in that window, so the bench is only available with the machine dark.
    if (machineState() != ST_IDLE) {
        Serial.printf("\nrefused — the machine is %s\n", machineStateName());
        return;
    }

    if (rest == "off") { linkWifiAp(false); return; }
    if (rest == "on")   { linkWifiAp(true);   return; }
    if (rest == "live") { linkWifiApMode(3);  return; }

    // A trailing q takes BLE off the air for the run. Advertising through one
    // is the honest case; what it costs is only visible against a run without it.
    bool quiet = rest.endsWith("q");
    if (quiet) { rest = rest.substring(0, rest.length() - 1); rest.trim(); }

    uint32_t kb = rest.length() ? (uint32_t)rest.toInt() : 1024;
    if (kb < 1 || kb > 16384) { Serial.println("\nusage: wifi [on|off|<KB>[q]]"); return; }
    const uint32_t bytes = kb * 1024UL;

    if (!linkWifiAp(true)) return;
    delay(300);   // let the AP settle before anyone probes for it

    Serial.printf("\nWIFI:PUSH %lu KB%s — the faucet joins and sends; the answer prints when it lands\n",
                  (unsigned long)kb, quiet ? ", BLE off the air" : ", BLE advertising");
    if (!faucetLinkWifiPush(bytes, quiet)) {
        Serial.println("J3 would not take the request");
        linkWifiAp(false);
        return;
    }
}

// Removing a picture is three things, and doing only the first is what left
// one glass showing a face the machine no longer had: drop it from each store
// that holds a copy, and move any channel that was wearing it onto something
// that still exists. The reassignment publishes to both glasses and back out to
// the phone the way every other art change does.
//
// `tellFaucet` is false when the faucet is the one that asked — it has already
// dropped its own copy, and telling it again would be an erase of an empty slot.
static void removePicture(uint8_t slot, bool tellFaucet) {
    if (slot >= FLAVOR_ART_CUSTOM) return;
    const uint8_t art = (uint8_t)(FLAVOR_ART_FACTORY + slot);
    uint8_t a0 = flavorArt(0), a1 = flavorArt(1);
    if (a0 == art) a0 = 0;
    if (a1 == art) a1 = 1;
    flavorArtSet(a0, a1);
    if (tellFaucet) faucetLinkImageErase(slot);
    linkImageErase(slot);
    Serial.printf("\nremoved picture %u — both displays told, artwork %u/%u\n",
                  slot, a0, a1);
}

// What J3 carries with nothing taking turns on it — the wire's ceiling, which
// is not what the OTA pull measures. Blocks for the length of the run, so it
// takes the same dark-machine guard the radio bench does.
// ── Carrying one picture to the enclosure ─────────────────────────────────
// Three steps that each block, so this runs from the loop rather than from
// inside the frame that asked for it: stand the enclosure's radio up (its
// panel comes down for that), tell the faucet to send, and take the radio back
// down — which is the reboot that puts the glass back with the new face on it.
//
// The main board is not on the path it is sequencing. The bytes go faucet to
// enclosure directly, which is the only reason this is seconds rather than the
// minutes the wire would take.
// THE HOP ENDS WHEN THE FAUCET SAYS SO. It takes a second or two; waiting a
// fixed minute for it spent that whole minute with the enclosure's panel down,
// because the panel only comes back on the reboot that follows the radio going
// away. So this waits on the outcome and stops.
//
// AND THE OUTCOME IS READ RATHER THAN ASSUMED. The sink now answers with what
// it did — one byte back down the same socket — so a picture that arrived short
// is a failure here instead of an announcement that the enclosure has a new
// picture it never kept. One retry, because the loss that produces it is the
// tail of a transfer and not a property of the picture.
static bool relayImageOnce(uint8_t slot) {
    // Mode 4 is mode 1 with the banner someone who just chose a photograph
    // reads, rather than the one the radio bench leaves up.
    if (!linkWifiApMode(4)) return false;

    faucetLinkForgetPushResult();
    if (!faucetLinkImageRelayGo(slot)) {
        Serial.println("J3 would not take it");
        linkWifiAp(false);
        return false;
    }

    WifiPushResultPayload r{};
    bool answered = false;
    const unsigned long until = millis() + 90000;
    while ((long)(millis() - until) < 0) {
        linkService();
        faucetLinkService();
        if (faucetLinkTakePushResult(r)) { answered = true; break; }
        delay(2);
    }
    linkWifiAp(false);

    if (!answered) {
        Serial.println("relay: the faucet never reported — the picture may not have crossed");
        return false;
    }
    if (!r.ok) {
        Serial.printf("relay: the enclosure did not keep it — %s\n", faucetLinkPushError(r.err));
        return false;
    }
    Serial.printf("relay: the enclosure kept %lu bytes and reboots into them\n",
                  (unsigned long)r.bytes);
    return true;
}

// A PICTURE THE ENCLOSURE DOES NOT HAVE YET IS STILL OWED IT. A hop that fails
// leaves the two boards disagreeing about what the machine holds, and nothing
// but a console command used to bring them back together — so what is owed is
// remembered and tried again rather than announced as lost. Between attempts
// the loop runs normally: the enclosure reboots whenever its panel came down,
// and asking a board that is still in its bootloader is how a transient failure
// becomes a permanent one.
constexpr uint8_t  RELAY_TRIES    = 4;
constexpr uint32_t RELAY_RETRY_MS = 20000;

static uint8_t relayOwed = 0;                       // bit per custom slot
static uint8_t relayTries[FLAVOR_ART_CUSTOM] = {0};
static unsigned long relayDueAt = 0;

static void relayOwe(uint8_t slot) {
    if (slot >= FLAVOR_ART_CUSTOM) return;
    relayOwed |= (uint8_t)(1u << slot);
    relayTries[slot] = 0;
    relayDueAt = millis();
}

// ── The two stores telling the same story ─────────────────────────────────
// EVERY MESSAGE THAT CHANGES THIS MACHINE CAN BE LOST. A picture removed from
// the phone reaches the faucet over the radio and the enclosure over J9, and
// the second leg goes through a board that may be flashing, dispensing or
// simply not listening in that pass. When it is missed, nothing tries again:
// the faucet has three pictures, the enclosure has four, and it stays that way
// until a person notices and runs a console command.
//
// So the state is reconciled rather than only announced. The two boards are
// asked what they hold, and where they disagree the difference is acted on. The
// immediate path stays exactly as it was — a removal still goes straight
// through — because this is a floor under it, not a replacement for it.
//
// THE FAUCET IS THE MASTER COPY. It holds every rendition and it is the board
// the phone reaches, so a difference is always resolved in its favour: the
// enclosure is sent what it is missing and stripped of what the machine no
// longer has.
constexpr uint32_t RECONCILE_MS     = 30000;
constexpr uint32_t RECONCILE_MAX_MS = 1800000;   // where the backing off stops

static ImagesPayload seenFaucet{}, seenEnclosure{};
static bool haveFaucet = false, haveEnclosure = false;
static unsigned long reconcileAt = 0;
static unsigned long reconcileAskedAt = 0;
static uint8_t imagesPrintOwed = 0;   // reports a person asked for

// A REPAIR THAT DOES NOT STICK MUST NOT BE ATTEMPTED FOREVER. Sending the
// enclosure a picture takes its panel down and reboots it; a slot it cannot
// keep — a store that will not erase, a picture it refuses — would otherwise
// blank the glass every half minute for the life of the machine, which is worse
// than the difference it is trying to close. So the same repair, needed again,
// waits twice as long each time, and anything that finally agrees puts it back.
static uint8_t reconcileSlot = 0xFF;   // what the last pass repaired
static uint8_t reconcileTried = 0;     // times in a row it has needed repairing

static void reconcileRepaired(uint8_t slot) {
    if (slot == reconcileSlot && reconcileTried < 8) ++reconcileTried;
    else if (slot != reconcileSlot) { reconcileSlot = slot; reconcileTried = 1; }
    uint32_t wait = RECONCILE_MS << (uint8_t)(reconcileTried - 1);
    if (wait > RECONCILE_MAX_MS || wait < RECONCILE_MS) wait = RECONCILE_MAX_MS;
    reconcileAt = millis() + wait;
    if (reconcileTried == 4)
        Serial.printf("reconcile: picture %u will not settle — trying more slowly\n", slot);
}

// Both links land here. Printing is what the console asked for; the reconcile
// asks far more often than anyone wants to read.
void imagesReport(const ImagesPayload &im) {
    if (im.board == OTA_TGT_FAUCET) { seenFaucet = im; haveFaucet = true; }
    else                            { seenEnclosure = im; haveEnclosure = true; }

    if (!imagesPrintOwed) return;
    --imagesPrintOwed;
    char bits[FLAVOR_ART_CUSTOM + 1];
    for (uint8_t i = 0; i < FLAVOR_ART_CUSTOM; i++)
        bits[i] = (i < im.slots) ? ((im.occupancy & (1u << i)) ? 'X' : '.') : ' ';
    bits[FLAVOR_ART_CUSTOM] = '\0';
    Serial.printf("\n%-10s %u custom slots [%s], %u held, %lu B each\n",
                  im.board == OTA_TGT_FAUCET ? "faucet" : "enclosure",
                  im.slots, bits, im.held, (unsigned long)im.bundleBytes);
    Serial.printf("           enclosure copy %08lX %08lX %08lX %08lX\n",
                  (unsigned long)im.crc[0], (unsigned long)im.crc[1],
                  (unsigned long)im.crc[2], (unsigned long)im.crc[3]);
}

static void imagesAsk(bool verbose) {
    haveFaucet = haveEnclosure = false;
    if (verbose) imagesPrintOwed = 2;
    ImagesQueryPayload q{(uint8_t)(verbose ? 1 : 0)};
    faucetLinkImagesQuery(q.verbose);
    linkImagesQuery(q.verbose);
}

static void reconcileService() {
    // A hop already owed is the same repair by another name; let it finish.
    if (relayOwed || machineState() != ST_IDLE || soundBusy()) return;
    // AND NOT WHILE EITHER BOARD IS BEING FLASHED. A repair brings the faucet's
    // radio up and takes the enclosure's panel down — over the same J3 an OTA is
    // running at 921600, to the same two boards. A difference the machine sees
    // mid-update is one it is about to be told a new answer for anyway, so the
    // repair costs a firmware image and buys nothing.
    if (otaBusy()) return;
    if ((long)(millis() - reconcileAt) < 0) return;

    if (!reconcileAskedAt) {
        reconcileAskedAt = millis();
        imagesAsk(false);
        return;
    }
    if (!haveFaucet || !haveEnclosure) {
        // One of them did not answer. Nothing is wrong that this can see, so it
        // waits rather than acting on half a picture of the machine.
        if (millis() - reconcileAskedAt > 5000) {
            reconcileAskedAt = 0;
            reconcileAt = millis() + RECONCILE_MS;
        }
        return;
    }
    reconcileAskedAt = 0;
    reconcileAt = millis() + RECONCILE_MS;

    // One difference per pass. Each repair is a transfer and a reboot, and the
    // next pass finds whatever is still wrong.
    for (uint8_t slot = 0; slot < FLAVOR_ART_CUSTOM; slot++) {
        const bool onFaucet = (seenFaucet.occupancy & (1u << slot)) != 0;
        const bool onGlass  = (seenEnclosure.occupancy & (1u << slot)) != 0;
        if (onFaucet && (!onGlass || seenEnclosure.crc[slot] != seenFaucet.crc[slot])) {
            Serial.printf("\nreconcile: the enclosure is %s picture %u — sending it\n",
                          onGlass ? "holding a different" : "missing", slot);
            relayOwe(slot);
            reconcileRepaired(slot);
            return;
        }
        if (!onFaucet && onGlass) {
            Serial.printf("\nreconcile: the enclosure holds picture %u the machine gave up\n",
                          slot);
            linkImageErase(slot);
            reconcileRepaired(slot);
            return;
        }
    }

    // Nothing to repair: whatever was hard is not hard any more.
    reconcileSlot = 0xFF;
    reconcileTried = 0;

    // And no channel may go on wearing a face that is not there. removePicture
    // does this when it is told; this catches the removal it never heard about.
    uint8_t a0 = flavorArt(0), a1 = flavorArt(1);
    const uint8_t s0 = flavorArtCustomSlot(a0), s1 = flavorArtCustomSlot(a1);
    if (s0 < FLAVOR_ART_CUSTOM && !(seenFaucet.occupancy & (1u << s0))) a0 = 0;
    if (s1 < FLAVOR_ART_CUSTOM && !(seenFaucet.occupancy & (1u << s1))) a1 = 1;
    if (a0 != flavorArt(0) || a1 != flavorArt(1)) {
        Serial.printf("\nreconcile: a channel was wearing a picture that is gone — artwork %u/%u\n",
                      a0, a1);
        flavorArtSet(a0, a1);
    }
}

static void relayService() {
    if (!relayOwed || (long)(millis() - relayDueAt) < 0) return;

    uint8_t slot = 0;
    while (slot < FLAVOR_ART_CUSTOM && !(relayOwed & (1u << slot))) ++slot;
    if (slot >= FLAVOR_ART_CUSTOM) { relayOwed = 0; return; }

    Serial.printf("\nrelay slot %u: standing the enclosure's radio up\n", slot);
    if (relayImageOnce(slot)) {
        relayOwed &= (uint8_t)~(1u << slot);
        relayDueAt = millis();
        return;
    }

    if (++relayTries[slot] >= RELAY_TRIES) {
        relayOwed &= (uint8_t)~(1u << slot);
        Serial.printf("relay slot %u FAILED after %u tries — the enclosure is still on its old "
                      "picture. 'images relay %u' asks again.\n",
                      slot, relayTries[slot], slot);
        return;
    }
    relayDueAt = millis() + RELAY_RETRY_MS;
    Serial.printf("relay slot %u: try %u did not take — again in %lu s\n",
                  slot, relayTries[slot], (unsigned long)(RELAY_RETRY_MS / 1000));
}

static void cmdBench(const String &line) {
    String rest = line.substring(5);
    rest.trim();
    if (!rest.startsWith("j3")) { Serial.println("\nusage: bench j3 [<KB>]"); return; }
    if (machineState() != ST_IDLE) {
        Serial.printf("\nrefused — the machine is %s\n", machineStateName());
        return;
    }
    rest = rest.substring(2);
    rest.trim();
    uint32_t kb = rest.length() ? (uint32_t)rest.toInt() : 512;
    if (kb < 1 || kb > 8192) { Serial.println("\nusage: bench j3 [<KB>]"); return; }

    Serial.printf("\nJ3:BENCH pushing %lu KB\n", (unsigned long)kb);
    if (!faucetLinkBenchPush(kb * 1024UL))
        Serial.println("J3 would not take it");
}

static void console(const String &line) {
    if (line == "help")        { help(); return; }
    if (line == "status")      { status(); return; }
    if (line == "link")        { linkReport(); faucetLinkReport(); return; }
    if (line == "ping")        { linkPing(); return; }
    if (line == "display usb") { linkDisplayUsbReattach(); return; }
    if (line == "wake") {
        // The same entry a reported touch takes. idleService() publishes the change to both
        // glasses on its next pass, so this says what it asked for, not what is on the panel.
        idleTouched();
        Serial.printf("\n[idle] awake asked for — the quiet window is %lu s\n",
                      (unsigned long)(idleWindowMs() / 1000));
        return;
    }
    if (line == "stop")        { machineStop(); return; }
    if (line.startsWith("sound"))  { cmdSound(line);  return; }
    if (line.startsWith("volume")) { cmdVolume(line); return; }
    if (line.startsWith("quiet"))  { cmdQuiet(line);  return; }
    if (line.startsWith("rtc"))    { cmdRtc(line);    return; }
    if (line.startsWith("ota"))    { otaConsole(line); return; }
    if (line.startsWith("identity")) { identityConsole(line); return; }
    if (line == "ble")             { faucetLinkBleReport(); return; }
    if (line.startsWith("images erase")) {
        String rest = line.substring(12); rest.trim();
        const uint8_t slot = rest.length() ? (uint8_t)rest.toInt() : 0xFF;
        if (slot >= FLAVOR_ART_CUSTOM) {
            Serial.printf("\nusage: images erase <0..%u>\n", FLAVOR_ART_CUSTOM - 1);
            return;
        }
        removePicture(slot, true);
        return;
    }
    if (line.startsWith("images relay")) {
        String rest = line.substring(12); rest.trim();
        const uint8_t slot = rest.length() ? (uint8_t)rest.toInt() : 0;
        if (slot >= FLAVOR_ART_CUSTOM) {
            Serial.printf("\nusage: images relay <0..%u>\n", FLAVOR_ART_CUSTOM - 1);
            return;
        }
        if (machineState() != ST_IDLE) {
            Serial.printf("\nrefused — the machine is %s\n", machineStateName());
            return;
        }
        relayOwe(slot);
        relayService();
        return;
    }
    if (line.startsWith("images test")) {
        String rest = line.substring(11); rest.trim();
        const uint8_t slot = rest.length() ? (uint8_t)rest.toInt() : 0;
        if (slot >= FLAVOR_ART_CUSTOM) {
            Serial.printf("\nusage: images test <0..%u>\n", FLAVOR_ART_CUSTOM - 1);
            return;
        }
        Serial.printf("\nasking the faucet to make itself a picture in slot %u\n", slot);
        if (!faucetLinkImageSynth(slot)) Serial.println("J3 would not take it");
        return;
    }
    if (line == "images")          {
        // Neither display has a console. Both answer where they are.
        Serial.println("\nasking both displays what they hold");
        imagesAsk(true);
        return;
    }
    if (line == "images sync") {
        Serial.println("\nreconciling now");
        reconcileAskedAt = 0;
        reconcileSlot = 0xFF;   // a person asking clears whatever it had given up on
        reconcileTried = 0;
        reconcileAt = millis();
        return;
    }
    if (line.startsWith("wifi"))   { cmdWifi(line); return; }
    if (line.startsWith("bench"))  { cmdBench(line); return; }
    if (line == "versions")        { versionsConsole(); return; }

    if (line.startsWith("flavor")) {
        String rest = line.substring(6); rest.trim();
        if (rest.length()) {
            char which = rest[0] | 0x20;
            if (which != 'a' && which != 'b') {
                Serial.println("\nusage: flavor [a|b]");
                return;
            }
            flavorSelect(which == 'a' ? PUMP_CHANNEL_A : PUMP_CHANNEL_B);
        }
        Serial.printf("\nflavor %s%s, artwork %u/%u\n", machinePumpName(flavorSelected()),
                      flavorPersisted() ? " (persisted)" : " (persistence pending)",
                      flavorArt(0), flavorArt(1));
        return;
    }

    if (line == "idle") {
        Serial.printf("\nidle %s — quiet %lus of %lus\n",
                      idleAsleep() ? "asleep" : "awake",
                      (unsigned long)(idleQuietMs() / 1000),
                      (unsigned long)(idleWindowMs() / 1000));
        return;
    }

    if (line.startsWith("art")) {
        String rest = line.substring(3); rest.trim();
        if (rest.length()) {
            const int sp = rest.indexOf(' ');
            if (sp < 0) { Serial.println("\nusage: art <a> <b>"); return; }
            const int a = rest.substring(0, sp).toInt();
            const int b = rest.substring(sp + 1).toInt();
            if (!flavorArtSet((uint8_t)a, (uint8_t)b)) {
                Serial.printf("\nusage: art <0..%d> <0..%d>\n",
                              FLAVOR_ART_COUNT - 1, FLAVOR_ART_COUNT - 1);
                return;
            }
        }
        Serial.printf("\nartwork %u/%u\n", flavorArt(0), flavorArt(1));
        return;
    }

    if (line.startsWith("pump")) {
        String rest = line.substring(4); rest.trim();
        if (!rest.length()) { Serial.println("\nusage: pump <a|b> [ms]"); return; }
        char which = rest[0] | 0x20;
        if (which != 'a' && which != 'b') { Serial.println("\nusage: pump <a|b> [ms]"); return; }
        String msArg = rest.substring(1); msArg.trim();
        uint32_t ms = msArg.length() ? (uint32_t)msArg.toInt() : 2000;
        if (!machinePumpRun(which == 'a' ? PUMP_CHANNEL_A : PUMP_CHANNEL_B, ms))
            Serial.printf("\nrefused — the machine is %s\n", machineStateName());
        return;
    }

    Serial.printf("\nunknown: '%s' — 'help' for the list\n", line.c_str());
}
