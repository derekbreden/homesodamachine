"""OTA version verification without opening a port or waiting on a clock.

    ~/.platformio/penv/bin/python -m unittest discover -s tools -p test_ota.py
"""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import ota


WANTED = "2026.09.15 123456789+"
OLD = "2026.09.14 abcdef012"


class Clock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class Console:
    """A byte stream scheduled on the test clock; no serial device is created."""

    def __init__(self, clock, replies):
        self.clock = clock
        self.replies = list(replies)
        self.writes = []
        self.closed = False

    @property
    def in_waiting(self):
        if self.replies and self.replies[0][0] <= self.clock.now:
            return len(self.replies[0][1])
        return 0

    def read(self, count):
        if not self.in_waiting:
            return b""
        at, data = self.replies.pop(0)
        if len(data) > count:
            self.replies.insert(0, (at, data[count:]))
        return data[:count]

    def write(self, data):
        self.writes.append((self.clock.now, data))

    def flush(self):
        pass

    def close(self):
        self.closed = True


class VersionParsing(unittest.TestCase):
    def test_cached_table_extracts_each_target_and_enclosure_art_metadata(self):
        table = (f"main board  {WANTED}\r\n"
                 f"faucet      {OLD}\r\n"
                 f"enclosure   {WANTED}  art crc 5FD3C89E\r\n> ").encode()
        for target, expected in (("self", WANTED), ("faucet", OLD), ("enclosure", WANTED)):
            with self.subTest(target=target):
                reports, tail = ota.consume_version_reports(table, target)
                self.assertEqual(reports, [expected])
                self.assertEqual(tail, b"> ")

    def test_async_reports_accept_whitespace_and_art_metadata(self):
        self.assertEqual(ota.version_report(f" VERSION enclosure = {WANTED}\r", "enclosure"), WANTED)
        self.assertEqual(ota.version_report(f"VERSION faucet = {WANTED}", "faucet"), WANTED)
        self.assertEqual(ota.version_report(f"VERSION enclosure = {WANTED}  art crc 5fd3c89e", "enclosure"), WANTED)

    def test_unanswered_and_other_board_reports_do_not_count(self):
        for line in ("enclosure   (unanswered)  art crc 00000000",
                     "VERSION enclosure = (unanswered)",
                     f"VERSION faucet = {WANTED}",
                     f"enclosure-extra {WANTED}",
                     "versions", "[J9] enclosure booting", "enclosure   "):
            with self.subTest(line=line):
                self.assertIsNone(ota.version_report(line, "enclosure"))

    def test_partial_version_and_metadata_wait_for_newline(self):
        chunks = [b"enclos", f"ure   {WANTED}".encode(), b"  art crc 5FD3", b"C89E\r", b"\n"]
        tail = b""
        for chunk in chunks[:-1]:
            reports, tail = ota.consume_version_reports(tail + chunk, "enclosure")
            self.assertEqual(reports, [])
        reports, tail = ota.consume_version_reports(tail + chunks[-1], "enclosure")
        self.assertEqual(reports, [WANTED])
        self.assertEqual(tail, b"")

    def test_completed_lines_are_consumed_once_and_partial_async_is_retained(self):
        first = f"enclosure {OLD}  art crc 00000000\nVERSION enclosure = 2026.".encode()
        reports, tail = ota.consume_version_reports(first, "enclosure")
        self.assertEqual(reports, [OLD])
        reports, tail = ota.consume_version_reports(tail + b"09.15 123456789+\n", "enclosure")
        self.assertEqual(reports, [WANTED])
        self.assertEqual(tail, b"")


class Confirmation(unittest.TestCase):
    def confirm(self, replies, target="enclosure"):
        clock = Clock()
        console = Console(clock, replies)
        output = io.StringIO()
        with patch.object(ota, "expected_version", return_value=WANTED), \
             patch.object(ota, "open_console", return_value=console) as opened, \
             patch.object(ota.time, "monotonic", side_effect=clock.monotonic), \
             patch.object(ota.time, "sleep", side_effect=clock.sleep), \
             redirect_stdout(output):
            result = ota.confirm_version("test-port", target)
        opened.assert_called_once_with("test-port")
        self.assertTrue(console.closed)
        self.assertTrue(all(data == b"versions\n" for _, data in console.writes))
        return result, output.getvalue(), clock, console

    def test_cached_table_alone_confirms_without_async_change_notification(self):
        result, output, clock, _ = self.confirm([(8, f"enclosure {WANTED} art crc 5FD3C89E\n".encode())])
        self.assertEqual(result, 0)
        self.assertIn(f"confirmed: enclosure is running {WANTED}", output)
        self.assertLess(clock.now, 9)

    def test_stale_table_waits_for_rebooted_display_and_keeps_partial_line_across_poll(self):
        result, output, clock, console = self.confirm([
            (8, f"enclosure {OLD} art crc 00000000\n".encode()),
            (12, f"VERSION enclosure = {WANTED}".encode()),
            (15, b"\n"),
        ])
        self.assertEqual(result, 0)
        self.assertGreaterEqual(clock.now, 15)
        self.assertGreaterEqual(len(console.writes), 2)
        self.assertNotIn("WRONG IMAGE", output)

    def test_stale_version_is_reported_as_mismatch_only_after_deadline(self):
        result, output, clock, console = self.confirm([(8, f"enclosure {OLD} art crc 00000000\n".encode())])
        self.assertEqual(result, 1)
        self.assertGreaterEqual(clock.now, 83)
        self.assertGreaterEqual(len(console.writes), 14)
        self.assertIn(f"WRONG IMAGE: enclosure reports {OLD!r}", output)

    def test_incomplete_matching_report_cannot_confirm_at_deadline(self):
        result, output, clock, _ = self.confirm([(8, f"VERSION enclosure = {WANTED}".encode())])
        self.assertEqual(result, 1)
        self.assertGreaterEqual(clock.now, 83)
        self.assertIn("it did not answer", output)
        self.assertNotIn("WRONG IMAGE", output)

    def test_main_board_table_confirmation_uses_same_complete_line_path(self):
        result, output, _, _ = self.confirm([(8, f"main board  {WANTED}\n".encode())], target="self")
        self.assertEqual(result, 0)
        self.assertIn(f"confirmed: self is running {WANTED}", output)


if __name__ == "__main__":
    unittest.main()
