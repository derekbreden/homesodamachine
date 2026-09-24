"""Acceptance and repeat-send checks; these tests never contact a printer."""
import copy
import unittest

from bambu_print import accepted, may_retry, selected_options, verify_spools, PrintError


class PrintAcceptance(unittest.TestCase):
    def setUp(self):
        self.before = {"job_id": "10", "gcode_state": "FINISH", "subtask_name": "old.gcode.3mf",
                       "print_error": 0, "hms": [], "upload": {"status": "idle"},
                       "nozzle_target_temper": 0, "bed_target_temper": 0}

    def test_new_job_name_and_printer_state_are_required(self):
        reading = dict(self.before, subtask_name="next.gcode.3mf", gcode_state="RUNNING")
        self.assertFalse(accepted(self.before, reading, "next.gcode.3mf"))
        reading["job_id"] = 11
        self.assertTrue(accepted(self.before, reading, "next.gcode.3mf"))
        reading["print_error"] = 123
        self.assertFalse(accepted(self.before, reading, "next.gcode.3mf"))

    def test_same_job_id_as_int_is_not_a_new_job(self):
        reading = dict(self.before, job_id=10, gcode_state="RUNNING")
        self.assertFalse(accepted(self.before, reading, "old.gcode.3mf"))

    def test_only_an_unchanged_idle_printer_can_be_retried(self):
        self.assertTrue(may_retry(self.before, self.before, False, "Finished"))
        for update in ({"job_id": "11"}, {"gcode_state": "PAUSE"},
                       {"upload": {"status": "uploading"}}, {"nozzle_target_temper": 200},
                       {"bed_target_temper": 80}, {"print_error": 7}, {"hms": [{"code": 8}]}):
            with self.subTest(update=update):
                self.assertFalse(may_retry(self.before, dict(self.before, **update), False, ""))

    def test_a_fleeting_upload_or_command_reply_prevents_retry(self):
        self.assertFalse(may_retry(self.before, self.before, True, "Finished"))

    def test_ui_transfer_blocks_retry_before_printer_status_changes(self):
        for page in ("Downloading... 100%", "Sending", "Uploading"):
            self.assertFalse(may_retry(self.before, self.before, False, page))

    def test_a_completed_late_job_prevents_duplicate_print(self):
        reading = dict(self.before, job_id="11", gcode_state="FINISH", subtask_name="next.gcode.3mf")
        self.assertFalse(may_retry(self.before, reading, False, "Finished"))

    def test_both_external_spool_colours_must_match_the_archive(self):
        details = {"slots": {1: {"type": "PET-CF", "colour": "000000"},
                             2: {"type": "PET-CF", "colour": "FFFFFF"}}}
        reading = {"vir_slot": [{"id": "254", "tray_type": "PET-CF", "tray_color": "000000FF"},
                                {"id": "255", "tray_type": "PET-CF", "tray_color": "FFFFFFFF"}]}
        verify_spools(details, reading)
        wrong = copy.deepcopy(reading)
        wrong["vir_slot"][1]["tray_color"] = "000000FF"
        with self.assertRaises(PrintError):
            verify_spools(details, wrong)

    def test_selected_radio_mark_can_be_a_sibling_in_the_native_tree(self):
        nodes = [{"id": 38, "parent": 37, "role": "AXStaticText", "label": "Timelapse"},
                 {"id": 41, "parent": 40, "role": "AXRadioButton", "label": "On"},
                 {"id": 42, "parent": 40, "role": "AXImage", "label": "radio"},
                 {"id": 46, "parent": 45, "role": "AXRadioButton", "label": "Off"}]
        self.assertEqual(selected_options(nodes), {"Timelapse": "On"})


if __name__ == "__main__":
    unittest.main()
