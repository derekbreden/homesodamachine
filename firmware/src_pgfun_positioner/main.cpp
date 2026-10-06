#include <array>
#include <cerrno>
#include <cinttypes>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "hardware/adc.h"
#include "hardware/gpio.h"
#include "hardware/sync.h"
#include "hardware/uart.h"
#include "hardware/watchdog.h"
#include "pico/rand.h"
#include "pico/stdlib.h"
#include "command_input.h"
#include "motion_policy.h"
#include "pins.h"
#include "safety_policy.h"
#include "tmc_uart.h"

using namespace pgfun_positioner;
namespace {
MotionPolicy motion;
volatile DriverVerification verification;
volatile uint32_t tick_progress = 0;
volatile uint16_t supply_raw = 0;
TickLiveness liveness;
uint32_t driver_status[kAxes]{};
uint32_t driver_gstat[kAxes]{};
uint32_t driver_chopconf[kAxes]{};
volatile bool driver_sample_valid[kAxes]{};
uint64_t driver_poll_us[kAxes]{};
uint32_t boot_token = 0;
uart_inst_t *buses[2] = {uart0, uart1};

bool motor_supply_ok() { return supply_raw >= 2701 && supply_raw <= 3311; }
void feed_if_live() {
    if (liveness.can_feed_watchdog(tick_progress)) watchdog_update();
}
void invalidate_samples() {
    for (unsigned i = 0; i < kAxes; ++i) driver_sample_valid[i] = false;
}
Health health() {
    Health h;
    const uint32_t inputs = gpio_get_all();
    h.stop_closed = !(inputs & (1u << kStopPin));
    h.open_limit_mask = 0;
    for (unsigned i = 0; i < kAxes; ++i)
        if (inputs & (1u << kLimitPin[i])) h.open_limit_mask |= 1u << i;
    // TH0 has a 4.7k pull-up to 3.3V. External VM->8x4.7k->TH0,
    // TH0->3.3k->GND yields ADC2702..3310 at VM18..28V.
    h.motor_supply_ok = motor_supply_ok();
    h.drivers_ok = verification.ready();
    h.pedal_pressed = !(inputs & (1u << kPedalPin));
    return h;
}
void outputs() {
    for (const auto pin : kEnablePin) gpio_put(pin, !motion.enabled()); // TMC ENN high = disabled.
    if (!motion.enabled()) gpio_put_masked(kStepMask, 0);
}
bool tick(repeating_timer_t *) {
    supply_raw = adc_read();
    if (verification.sample_supply(motor_supply_ok())) {
        invalidate_samples(); motion.fail(Fault::Supply);
    }
    const uint8_t mask = motion.tick(time_us_64(), health());
    outputs();
    if (mask) {
        uint32_t gpio_mask = 0;
        for (unsigned i = 0; i < kAxes; ++i)
            if (mask & (1u << i)) gpio_mask |= 1u << kStepPin[i];
        for(unsigned i=0;i<kAxes;++i)if(mask&(1u<<i))gpio_put(kDirPin[i],(motion.delta[i]>0)!=kDirInvert[i]);
        busy_wait_us_32(2); // DIR setup, including curve reversals.
        gpio_put_masked(kStepMask, gpio_mask); // One common rising edge for due axes.
        busy_wait_us_32(3);
        gpio_put_masked(kStepMask, 0);
    }
    ++tick_progress; // Only a completed input/pulse/output cycle counts as live.
    return true;
}
void print_status(const char *kind, uint32_t seq = 0, const char *error = nullptr, const char *op = nullptr) {
    const uint32_t irq = save_and_disable_interrupts();
    const MotionPolicy snapshot = motion;
    const Health h = health();
    const uint16_t vm = supply_raw;
    const uint32_t epoch = verification.epoch();
    const uint32_t progress = tick_progress;
    const uint64_t now = time_us_64();
    restore_interrupts(irq);
    printf("{\"type\":\"%s\",\"boot\":\"%08" PRIx32 "\",\"seq\":%" PRIu32
           ",\"last_seq\":%" PRIu32 ",\"time_us\":%" PRIu64
           ",\"state\":\"%s\",\"fault\":\"%s\",\"referenced\":%s,"
           "\"count\":[%" PRId32 ",%" PRId32 "],"
           "\"completed_seq\":%" PRIu32 ",\"completed_us\":%" PRIu64
           ",\"stop_closed\":%s,\"open_limit_mask\":%u,\"supply_adc\":%u,\"drivers_ok\":%s,"
           "\"profile\":\"%s\",\"counts_per_rev\":%d,\"max_rate\":%u,"
           "\"vm_epoch\":%" PRIu32 ",\"timer_ticks\":%" PRIu32,
           kind, boot_token, seq, snapshot.last_sequence, now, state_name(snapshot.state),
           fault_name(snapshot.fault), snapshot.referenced() ? "true" : "false",
           snapshot.count[0], snapshot.count[1], snapshot.completed_sequence,
           snapshot.completed_us, h.stop_closed ? "true" : "false", h.open_limit_mask,
           vm, h.drivers_ok ? "true" : "false", kProfileName,
           static_cast<int>(kCountsPerRev), static_cast<unsigned>(kMaxRate), epoch, progress);
    printf(",\"pedal_pressed\":%s,\"playback_waiting\":%s,\"playback_active\":%s,\"playback_started_us\":%" PRIu64 ",\"loaded_knots\":%u",h.pedal_pressed?"true":"false",snapshot.playback_waiting?"true":"false",snapshot.playback_active?"true":"false",snapshot.playback_started_us,snapshot.loaded_knots);
    printf(",\"geometry_sha256\":\"%s\",\"current_scales\":[", kGeometrySha256);
    for (unsigned i = 0; i < kAxes; ++i) printf("%s%u", i ? "," : "", static_cast<unsigned>(kCurrentScales[i]));
    printf("],\"configured_vsense\":[");
    for (unsigned i = 0; i < kAxes; ++i) printf("%s%u", i ? "," : "", static_cast<unsigned>(kVsense[i]));
    printf("],\"vsense\":[");
    for (unsigned i = 0; i < kAxes; ++i) {
        printf("%s", i ? "," : "");
        if (h.drivers_ok && driver_sample_valid[i]) printf("%u", static_cast<unsigned>((driver_chopconf[i] >> 17) & 1));
        else printf("null");
    }
    printf("],\"microsteps\":[");
    for (unsigned i = 0; i < kAxes; ++i) {
        printf("%s", i ? "," : "");
        const unsigned mres = (driver_chopconf[i] >> 24) & 15;
        if (h.drivers_ok && driver_sample_valid[i] && mres <= 8) printf("%u", 256u >> mres);
        else printf("null");
    }
    printf("]");
    if (op) printf(",\"op\":\"%s\"", op);
    if (error) printf(",\"error\":\"%s\"", error);
    printf("}\n");
}
bool read_driver(unsigned i, DriverSnapshot &s) {
    const uint32_t epoch = verification.epoch();
    const bool read = tmc_read(buses[kDriverBus[i]], kDriverAddress[i], 0x01, s.gstat) &&
                      tmc_read(buses[kDriverBus[i]], kDriverAddress[i], 0x6f, s.drv_status) &&
                      tmc_read(buses[kDriverBus[i]], kDriverAddress[i], 0x00, s.gconf) &&
                      tmc_read(buses[kDriverBus[i]], kDriverAddress[i], 0x6c, s.chopconf);
    const bool valid = read && motor_supply_ok() && epoch == verification.epoch();
    driver_sample_valid[i] = valid;
    if (valid) {
        driver_gstat[i] = s.gstat;
        driver_status[i] = s.drv_status;
        driver_chopconf[i] = s.chopconf;
        driver_poll_us[i] = time_us_64();
    }
    feed_if_live();
    return valid;
}
bool verify_drivers(uint32_t epoch) {
    const uint64_t started = time_us_64();
    const bool read = check_two_drivers(read_driver, kGconf, kChopconfs);
    const uint32_t irq = save_and_disable_interrupts();
    // A final direct sample closes the UART-check-to-enable sampling window.
    supply_raw = adc_read();
    if (verification.sample_supply(motor_supply_ok())) {
        invalidate_samples(); motion.fail(Fault::Supply);
    }
    const bool ok = read && time_us_64() - started <= 50000 && verification.finish(epoch);
    if (!ok) verification.invalidate();
    restore_interrupts(irq);
    return ok;
}
bool configure_drivers() {
    verification.invalidate();
    for (const auto pin : kEnablePin) gpio_put(pin, 1);
    if (!health().motor_supply_ok) return false;
    const uint32_t epoch = verification.epoch();
    // Prime every node's turnaround before any multi-node read. The following
    // measured configuration includes another SLAVECONF write in IFCNT's +10.
    for (unsigned i = 0; i < kAxes; ++i)
        tmc_write(buses[kDriverBus[i]], kDriverAddress[i], 0x03, 2u << 8);
    for (unsigned i = 0; i < kAxes; ++i) {
        if (!tmc_configure(buses[kDriverBus[i]], kDriverAddress[i], kCurrentScales[i], kChopconfs[i])) return false;
        feed_if_live();
    }
    return verify_drivers(epoch);
}
bool integer(const char *s, int64_t &out) {
    if (!s || !*s) return false;
    errno = 0;
    char *end = nullptr;
    out = strtoll(s, &end, 10);
    return !errno && *end == '\0';
}
void inhibit() {
    const uint32_t irq = save_and_disable_interrupts();
    motion.fail(Fault::UserStop); outputs();
    restore_interrupts(irq);
}
const char *protocol_op(const char *name) {
    for (const char *op : {"CLEAR", "REF", "ARM", "PING", "DISARM", "MOVE2", "STATUS", "DRIVERS", "LOAD2", "KNOT", "PLAY"})
        if (!strcmp(name, op)) return op;
    return "unknown";
}
void command(char *line) {
    if (stop_prefix(line)) { inhibit(); print_status("stopped", 0, nullptr, "STOP"); return; }
    char *token[12]{};
    unsigned n = 0;
    char *save = nullptr;
    for (char *p = strtok_r(line, " \t\r", &save); p; p = strtok_r(nullptr, " \t\r", &save)) {
        if (n == 12) { print_status("error", 0, "too_many_tokens"); return; }
        token[n++] = p;
    }
    if (!n) return;
    if (n == 1 && !strcmp(token[0], "STATUS")) { print_status("status"); return; }
    if (n == 1 && !strcmp(token[0], "DRIVERS")) {
        for (unsigned i = 0; i < kAxes; ++i) {
            printf("{\"type\":\"driver\",\"axis\":%u,\"gstat\":%" PRIu32
                   ",\"drv_status\":%" PRIu32 ",\"bus\":%u,\"address\":%u,"
                   "\"cs_actual\":%u,\"configured_cs\":%u,\"configured_vsense\":%u,\"sample_valid\":%s,\"sample_us\":%" PRIu64,
                   i, driver_gstat[i], driver_status[i], kDriverBus[i], kDriverAddress[i],
                   static_cast<unsigned>((driver_status[i] >> 16) & 0x1f), static_cast<unsigned>(kCurrentScales[i]),
                   static_cast<unsigned>(kVsense[i]),
                   driver_sample_valid[i] ? "true" : "false", driver_poll_us[i]);
            const unsigned mres = (driver_chopconf[i] >> 24) & 15;
            if (driver_sample_valid[i] && mres <= 8)
                printf(",\"microsteps\":%u,\"vsense\":%u}\n", 256u >> mres,
                       static_cast<unsigned>((driver_chopconf[i] >> 17) & 1));
            else printf(",\"microsteps\":null,\"vsense\":null}\n");
        }
        return;
    }
    const char *op = protocol_op(token[0]);
    char expected[9];
    snprintf(expected, sizeof(expected), "%08" PRIx32, boot_token);
    int64_t seq64 = 0;
    if (n < 3 || strcmp(token[1], expected) || !integer(token[2], seq64) ||
        seq64 <= 0 || seq64 > UINT32_MAX) {
        print_status("error", 0, "boot_or_sequence_format", op); return;
    }
    const uint32_t seq = seq64;
    bool known = false;
    const bool move = !strcmp(token[0], "MOVE2");
    if(!strcmp(token[0],"LOAD2") || !strcmp(token[0],"KNOT") || !strcmp(token[0],"PLAY")) {
        const unsigned arity=!strcmp(token[0],"LOAD2")?5:!strcmp(token[0],"KNOT")?6:3;
        int64_t values[3]{};
        if(n!=arity) { print_status("error",seq,"arity",op);return; }
        for(unsigned i=3;i<n;++i)if(!integer(token[i],values[i-3]) || values[i-3]<INT32_MIN || values[i-3]>INT32_MAX) {
            print_status("error",seq,"integer_range",op);return;
        }
        const uint32_t irq=save_and_disable_interrupts();bool ok=false;const auto now=time_us_64();
        if(!strcmp(token[0],"LOAD2"))ok=motion.load(seq,now,values[0],values[1]);
        else if(!strcmp(token[0],"KNOT"))ok=motion.knot(seq,now,values[0],values[1],values[2]);
        else ok=motion.play(seq,now,health());
        const char *why=motion.error;restore_interrupts(irq);
        print_status(ok?"ack":"error",seq,ok?nullptr:why,op);return;
    }
    if ((move && n != 6) || (!move && n != 3)) {
        print_status("error", seq, "arity", op); return;
    }
    std::array<int32_t, kAxes> delta{};
    int64_t duration = 0;
    if (move) {
        if (!integer(token[3], duration) || duration < 0 || duration > UINT32_MAX) {
            print_status("error", seq, "duration_format", op); return;
        }
        for (unsigned i = 0; i < kAxes; ++i) {
            int64_t value = 0;
            if (!integer(token[i + 4], value) || value < INT32_MIN || value > INT32_MAX) {
                print_status("error", seq, "delta_format", op); return;
            }
            delta[i] = value;
        }
    }
    if (!strcmp(token[0], "CLEAR")) {
        // UART transactions run outside the pulse ISR and never with a live move.
        const uint32_t irq = save_and_disable_interrupts();
        const bool can = !motion.enabled() && motion.sequence(seq);
        restore_interrupts(irq);
        if (!can) { print_status("error", seq, "clear_state_or_sequence", op); return; }
        configure_drivers();
    }
    if (!strcmp(token[0], "ARM")) {
        const uint32_t irq = save_and_disable_interrupts();
        const bool can = motion.state == State::Referenced && motion.sequence(seq) && motion.healthy(health());
        const uint32_t epoch = verification.epoch();
        restore_interrupts(irq);
        if (!can) { print_status("error", seq, "arm_requires_healthy_reference", op); return; }
        // ENN stays HIGH throughout a fresh two-driver read. No cached poll can arm.
        if (!verify_drivers(epoch)) {
            const uint32_t irq2 = save_and_disable_interrupts();
            motion.fail(Fault::Driver); outputs();
            restore_interrupts(irq2);
            print_status("error", seq, "arm_driver_verification", op); return;
        }
    }
    const uint32_t irq = save_and_disable_interrupts();
    const uint64_t now = time_us_64();
    const Health h = health();
    bool ok = false;
    if (!strcmp(token[0], "PING")) { known = true; ok = motion.ping(seq, now); }
    else if (!strcmp(token[0], "CLEAR")) { known = true; ok = motion.clear(seq, now, h); }
    else if (!strcmp(token[0], "REF")) { known = true; ok = motion.reference(seq, now, h); }
    else if (!strcmp(token[0], "ARM")) { known = true; ok = motion.arm(seq, now, h); }
    else if (!strcmp(token[0], "DISARM")) { known = true; ok = motion.disarm(seq, now); }
    else if (move) {
        known = true; ok = motion.move(seq, now, duration, delta, h);
        if (ok) for (unsigned i = 0; i < kAxes; ++i)
            gpio_put(kDirPin[i], (delta[i] > 0) != kDirInvert[i]);
    }
    outputs();
    const char *error = known ? motion.error : "unknown_command";
    restore_interrupts(irq);
    print_status(ok ? "ack" : "error", seq, ok ? nullptr : error, op);
}
} // namespace

int main() {
    for (const auto pin : kAllEnablePin) { gpio_init(pin); gpio_put(pin, 1); gpio_set_dir(pin, GPIO_OUT); }
    for (const auto pin : {17,18,20,21,23,29}) { gpio_init(pin); gpio_put(pin, 0); gpio_set_dir(pin, GPIO_OUT); }
    gpio_put(20, 1); // FAN3, 24V active cooling while supply is present.
    for (unsigned i = 0; i < kAxes; ++i) {
        gpio_init(kStepPin[i]); gpio_put(kStepPin[i], 0); gpio_set_dir(kStepPin[i], GPIO_OUT);
        gpio_init(kDirPin[i]); gpio_put(kDirPin[i], 0); gpio_set_dir(kDirPin[i], GPIO_OUT);
        gpio_init(kLimitPin[i]); gpio_set_dir(kLimitPin[i], GPIO_IN); gpio_pull_up(kLimitPin[i]);
    }
    gpio_init(kPedalPin);gpio_set_dir(kPedalPin,GPIO_IN);gpio_pull_up(kPedalPin);
    gpio_init(kStopPin); gpio_set_dir(kStopPin, GPIO_IN); gpio_pull_up(kStopPin);
    adc_init(); adc_gpio_init(kSupplyPin); adc_select_input(1); supply_raw = adc_read();
    for (unsigned i = 1; i < 2; ++i) {
        uart_init(buses[i], 115200);
        gpio_set_function(kUartTxPin[i], GPIO_FUNC_UART);
        gpio_set_function(kUartRxPin[i], GPIO_FUNC_UART);
        gpio_disable_pulls(kUartTxPin[i]);
        gpio_disable_pulls(kUartRxPin[i]);
        gpio_set_drive_strength(kUartTxPin[i], GPIO_DRIVE_STRENGTH_4MA);
        uart_set_format(buses[i], 8, 1, UART_PARITY_NONE);
        uart_set_hw_flow(buses[i], false, false);
    }
    stdio_init_all();
    boot_token = get_rand_32();
    repeating_timer_t timer;
    if (!add_repeating_timer_us(-int64_t(kTickUs), tick, nullptr, &timer)) {
        motion.fail(Fault::Timing); outputs();
    }
    watchdog_enable(250, true); // A stuck foreground loop resets to ENN pulled high.
    configure_drivers();
    CommandInput input;
    State reported_state = motion.state;
    uint32_t reported_completion = 0;
    unsigned poll_axis = 0;
    uint64_t next_poll = time_us_64() + 50000;
    while (true) {
        feed_if_live();
        int ch;
        for (unsigned served = 0; served < 32 && (ch = getchar_timeout_us(0)) != PICO_ERROR_TIMEOUT; ++served) {
            const auto result = input.feed(ch);
            if (result == CommandInput::Result::Invalid) inhibit();
            if (result == CommandInput::Result::InvalidLine) {
                inhibit(); print_status("error", 0, "invalid_input_inhibited", "INPUT"); break;
            }
            if (result == CommandInput::Result::Command) { command(input.line); break; }
        }
        if (time_us_64() >= next_poll) {
            next_poll = time_us_64() + 50000;
            if (verification.ready() && health().motor_supply_ok) {
                const unsigned i = poll_axis++ % kAxes;
                DriverSnapshot snapshot;
                if (!read_driver(i, snapshot) || !driver_snapshot_ok(snapshot, kGconf, kChopconfs[i])) {
                    verification.invalidate();
                    const uint32_t irq = save_and_disable_interrupts();
                    motion.fail(Fault::Driver);
                    outputs(); restore_interrupts(irq);
                }
            }
        }
        const uint32_t irq = save_and_disable_interrupts();
        const State state = motion.state;
        const uint32_t done = motion.completed_sequence;
        restore_interrupts(irq);
        if (state != reported_state || done != reported_completion) {
            reported_state = state; reported_completion = done;
            print_status("event", done);
        }
        tight_loop_contents();
    }
}
