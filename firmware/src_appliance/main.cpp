#include <Arduino.h>

#include "fw_version.h"
#include "fw_build_time.h"   // churns every build; the banner is what reads it
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
// Runs on the controller PCBA's ESP32-WROOM-32E (U1). The board is
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
//   2. Relay #2 (IO2) de-energized while a dispense is open. The board
//      peaks at 3.33 A and the SeaFlo at 5 A on one 6.7 A supply. The
//      carbonator's low reed asserts mid-pour, so the refill it queues
//      waits for the dispense window to close.
//   3. GPPU written on both MCP23017s. No loom carries a resistor and
//      the board pulls none of the reed inputs, so a reed with no
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
// One flavor pump turns, held from the glass or bounded from the console.
// Both MCP23017s boot with every output verified low and every reed input on
// its internal pull-up; status reads those inputs on explicit request. No
// operation opens a valve or runs the fan, neither relay is ever driven, and
// a clean cycle is answered MSG_ERR_UNSUPPORTED.

static void console(const String &line);

void setup() {
    machineBegin();   // actuators parked before anything else runs — including U8's coil

    Serial.begin(115200);
    while (!Serial && millis() < 2000) {}
    Serial.printf("\nhomesodamachine appliance  %s  (%s)\n", FW_VERSION, FW_BUILD_TIME);

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
    Serial.printf("J9 up on IO%d/IO%d @ %ld — the display's prime hold arrives here\n",
                  PIN_485_DI, PIN_485_RO, RS485_BAUD);
    Serial.println("idle — actuators dark; valves have no runtime command");
    Serial.println("type 'help' for what this build answers to\n");
    Serial.print("> ");

    // The machine waking up. Every actuator is already parked by the time this
    // sounds, so it says the controller reached the end of setup() and nothing
    // else — which on a line is how a unit is heard coming up without being
    // watched, and in a kitchen is just the machine saying hello.
    soundPlay(machineIoReady() ? SND_WELCOME : SND_FAULT);
}

void loop() {
    linkService();      // frames in, replies out
    machineService();   // the deadlines a held pump is measured against
    soundService();     // U8's step boundaries — nothing here blocks, and it must
                        // run every pass: LEDC keeps oscillating on its own, so a
                        // sequencer that stops being serviced holds the coil on.

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
    Serial.println("  link              J9 frames, bytes, echo");
    Serial.println("  ping              put a frame on the pair and read its echo back");
    Serial.println("  display usb       make the externally-powered display reattach to USB");
    Serial.println("  sound <name>      play one of the machine's sounds; 'sound list' names them");
    Serial.println("  volume [0-100]    how loud everything but the alarm is (persisted)");
    Serial.println("  quiet [on|off] [start] [end] [pct]   quiet hours, off the DS3231 (persisted)");
    Serial.println("  rtc [set <YYYY-MM-DD> <HH:MM:SS>]    the clock quiet hours reads");
    Serial.println("  help              this");
    Serial.println("\n  A prime is the display's: hold the pad and the pump turns under it. It");
    Serial.println("  arrives as MSG_PRIME_START and stops on the lift, on a stale tick, or at");
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

static void console(const String &line) {
    if (line == "help")        { help(); return; }
    if (line == "status")      { status(); return; }
    if (line == "link")        { linkReport(); return; }
    if (line == "ping")        { linkPing(); return; }
    if (line == "display usb") { linkDisplayUsbReattach(); return; }
    if (line == "stop")        { machineStop(); return; }
    if (line.startsWith("sound"))  { cmdSound(line);  return; }
    if (line.startsWith("volume")) { cmdVolume(line); return; }
    if (line.startsWith("quiet"))  { cmdQuiet(line);  return; }
    if (line.startsWith("rtc"))    { cmdRtc(line);    return; }

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
