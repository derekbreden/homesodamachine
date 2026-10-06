#pragma once
#include <cstdint>
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include "pico/time.h"
#include "pins.h"
#include "tmc_protocol.h"
#include "driver_profile.h"

namespace pgfun_positioner {
inline bool tmc_read(uart_inst_t *bus, uint8_t address, uint8_t reg, uint32_t &value) {
    const uint8_t tx_pin = kUartTxPin[bus == uart0 ? 0 : 1];
    gpio_set_oeover(tx_pin, GPIO_OVERRIDE_NORMAL);
    while (uart_is_readable(bus)) (void)uart_getc(bus);
    uint8_t request[4] = {0x05, address, reg, 0};
    request[3] = tmc_crc(request, 3);
    uart_write_blocking(bus, request, 4);
    uart_tx_wait_blocking(bus);
    // Release the on-board single-wire UART TX during the slave response.
    // SENDDELAY>=2 provides 24 bit times after the request to release TX.
    gpio_set_oeover(tx_pin, GPIO_OVERRIDE_LOW);
    TmcReply response;
    const uint64_t deadline = time_us_64() + 4000;
    while (time_us_64() < deadline) {
        if (!uart_is_readable(bus)) continue;
        const uint8_t byte = uart_getc(bus);
        // Sliding window rejects echoed request bytes and checks complete reply.
        if (response.feed(byte, reg, value)) {
            gpio_set_oeover(tx_pin, GPIO_OVERRIDE_NORMAL);
            return true;
        }
    }
    gpio_set_oeover(tx_pin, GPIO_OVERRIDE_NORMAL);
    return false;
}
inline void tmc_write(uart_inst_t *bus, uint8_t address, uint8_t reg, uint32_t value) {
    gpio_set_oeover(kUartTxPin[bus == uart0 ? 0 : 1], GPIO_OVERRIDE_NORMAL);
    uint8_t request[8] = {0x05, address, uint8_t(reg | 0x80), uint8_t(value >> 24),
                          uint8_t(value >> 16), uint8_t(value >> 8), uint8_t(value), 0};
    request[7] = tmc_crc(request, 7);
    uart_write_blocking(bus, request, 8);
    uart_tx_wait_blocking(bus);
    busy_wait_us_32(150); // Twelve bit times between independent transactions.
}
inline bool tmc_configure(uart_inst_t *bus, uint8_t address, uint32_t current_scale, uint32_t chopconf) {
    uint32_t io = 0, before = 0, after = 0, readback = 0, gstat = 0;
    if (!tmc_read(bus, address, 0x02, before)) return false;
    // SENDDELAY=2 (24 bit times); 0/1 are not allowed on a multi-slave bus.
    tmc_write(bus, address, 0x03, 2u << 8);
    if (!tmc_read(bus, address, 0x06, io) || (io >> 24) != 0x21) return false;
    tmc_write(bus, address, 0x00, kGconf);
    tmc_write(bus, address, 0x6c, chopconf);
    tmc_write(bus, address, 0x10, current_scale | (current_scale << 8) | (6u << 16));
    tmc_write(bus, address, 0x11, 20); // TPOWERDOWN (hold current remains equal).
    tmc_write(bus, address, 0x13, 0);  // TPWMTHRS, no mode switching.
    tmc_write(bus, address, 0x14, 0);  // TCOOLTHRS, no sensorless limits/CoolStep.
    tmc_write(bus, address, 0x22, 0);  // VACTUAL, no autonomous pulse generator.
    tmc_write(bus, address, 0x42, 0);  // COOLCONF, fixed current.
    tmc_write(bus, address, 0x01, 7);  // Clear latched GSTAT after configuration.
    if (!tmc_read(bus, address, 0x02, after) || uint8_t(after - before) != 10) return false;
    if (!tmc_read(bus, address, 0x00, readback) || readback != kGconf) return false;
    if (!tmc_read(bus, address, 0x6c, readback) || readback != chopconf) return false;
    if (!tmc_read(bus, address, 0x01, gstat) || (gstat & 7)) return false;
    // IHOLD_IRUN is write-only; IFCNT verifies its write, not analogue coil current.
    return true;
}
}
