#pragma once
#include <cstdint>

namespace pgfun_positioner {
inline uint8_t tmc_crc(const uint8_t *p, unsigned size) {
    uint8_t crc = 0;
    for (unsigned i = 0; i < size; ++i) {
        uint8_t byte = p[i];
        for (unsigned b = 0; b < 8; ++b) {
            crc = ((crc >> 7) ^ (byte & 1)) ? uint8_t((crc << 1) ^ 7) : uint8_t(crc << 1);
            byte >>= 1;
        }
    }
    return crc;
}
class TmcReply {
    uint8_t bytes_[8]{};
    unsigned have_ = 0;
public:
    bool feed(uint8_t byte, uint8_t reg, uint32_t &value) {
        if (have_ < 8) bytes_[have_++] = byte;
        else {
            for (unsigned i = 0; i < 7; ++i) bytes_[i] = bytes_[i + 1];
            bytes_[7] = byte;
        }
        if (have_ != 8 || bytes_[0] != 0x05 || bytes_[1] != 0xff ||
            bytes_[2] != reg || tmc_crc(bytes_, 7) != bytes_[7]) return false;
        value = uint32_t(bytes_[3]) << 24 | uint32_t(bytes_[4]) << 16 |
                uint32_t(bytes_[5]) << 8 | bytes_[6];
        return true;
    }
};
} // namespace pgfun_positioner
