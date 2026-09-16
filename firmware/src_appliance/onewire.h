#pragma once

#include <stdint.h>

// ════════════════════════════════════════════════════════════
//  The 1-wire temperature bus — J4 pin 5, IO26
// ════════════════════════════════════════════════════════════
//
// Two probes share one wire. R9, a 4.7k to 3V3 on the main board, is the only
// thing that pulls it high; every device and this driver can do nothing but let
// go or pull it down. Both probes take 3V3 and GND from the same J4 loom, so
// nothing here holds the line high to power a conversion.
//
// The two are told apart by family code, never by a ROM written down per unit:
//
//   0x28  DS18B20, 12-bit — the carbonator wall. The tank temperature the
//                           compressor cycles on.
//   0x10  DS18S20,  9-bit — the evaporator suction line. The freeze cutoff.
//
// Exactly one of each is expected. Two of a family, or a family missing, is a
// wrong part or a probe mounted in the wrong place, and commissioning step 6
// reads the counts here as that — hardware/assembly/firmware-and-commissioning.md.
//
// A 12-bit conversion takes 750 ms. No call here waits one out: oneWireService()
// runs a state machine that issues CONVERT T to the whole bus at once and then
// reads one scratchpad per later call. The longest a single call holds the CPU
// is one search pass or one scratchpad read — around 14 ms of bit-banged slots.

void oneWireBegin();

// The clock and the wire. One search pass, one CONVERT T, or one scratchpad
// read per call, whichever the state machine is owed.
void oneWireService(uint32_t now_ms);

// The newest believable reading of each family. Valid is false when that
// family is absent from the bus or its last scratchpad failed CRC; the
// temperature is NAN there.
void oneWireRead(float &tankC, bool &tankValid, float &coilC, bool &coilValid);

uint8_t  oneWireDeviceCount();                 // devices found by the last search
uint8_t  oneWireFamilyCount(uint8_t family);   // how many of one family
uint32_t oneWireCrcErrors();                   // ROMs and scratchpads together
uint32_t oneWireLastReadMs();                  // millis() of the last good scratchpad

// Every ROM on the bus with its family, its last temperature, and whether its
// last scratchpad carried a good CRC — to Serial, for the commissioning log.
void oneWireDump();
