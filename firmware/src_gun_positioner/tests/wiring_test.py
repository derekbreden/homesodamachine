"""DC UART design-envelope calculation; no port, pin or physical waveform test."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NETWORK = json.loads((ROOT / "hardware/gun-positioner/wiring-manifest.json").read_text())["uart_network"]


def dc_envelope():
    n = NETWORK["nodes_per_bus"]
    up = NETWORK["bus_pullup_ohm"]
    series = NETWORK["tx_series_ohm"]
    tol = NETWORK["resistor_tolerance_fraction"]
    module_pd = NETWORK["received_module_R6_pulldown_ohm"]
    # Conservative 5% module R6 range; chip pin pulls 132..200k and
    # ±10uA leakage from TMC2209 §20.2. Two Pico pins add ±1uA each.
    g_min = n / (module_pd * 1.05) + n / 200_000
    g_max = n / (module_pd * 0.95) + n / 132_000
    leak = n * 10e-6 + 2e-6
    up_min, up_max = up * (1 - tol), up * (1 + tol)
    series_max = series * (1 + tol)
    vlo, vhi = NETWORK["VIO_nominal_V"] * .95, NETWORK["VIO_nominal_V"] * 1.05
    idle = (vlo / up_max - leak) / (1 / up_max + g_max)
    lows, highs = [], []
    for v in (vlo, vhi):
        # RP2040 3.3V GPIO table: VOL<=0.5V, VOH>=2.62V at selected
        # 4mA strength. VIO±5% with the same conservative voltage drops is
        # a design-screening assumption, checked by received hardware.
        low = (v / up_min + .5 / series_max + leak) / (1 / up_min + 1 / series_max + g_min)
        high = (v / up_max + (v - .68) / series_max - leak) / (1 / up_max + 1 / series_max + g_max)
        lows.append(v * .3 - low)
        highs.append(high - v * .7)
    return dict(idle_V=idle, idle_high_margin_V=idle - vlo * .7,
                request_low_margin_V=min(lows), request_high_margin_V=min(highs),
                reply_sink_upper_A=vhi / up_min + leak,
                reply_low_V=.2, reply_high_lower_V=vlo - .2)


class WiringTests(unittest.TestCase):
    def test_both_directions_have_dc_margin(self):
        result = dc_envelope()
        for key in ("idle_high_margin_V", "request_low_margin_V", "request_high_margin_V"):
            self.assertGreater(result[key], 0, key)
        self.assertLess(result["reply_sink_upper_A"], .002)
        self.assertLess(result["reply_low_V"], .8) # Pico RX low threshold.
        self.assertGreater(result["reply_high_lower_V"], 2) # Pico RX high threshold.


if __name__ == "__main__":
    print(json.dumps(dc_envelope(), sort_keys=True))
    unittest.main()
