from django.test import TestCase

from .views import map_prefect_state_to_exec_status, parse_prefect_state_name


class PrefectStateMappingTests(TestCase):
    def test_parse_prefect_state_name_state_name_field(self):
        payload = {"state_name": "Completed"}
        self.assertEqual(parse_prefect_state_name(payload), "COMPLETED")

    def test_parse_prefect_state_name_nested_state(self):
        payload = {"state": {"name": "Failed"}}
        self.assertEqual(parse_prefect_state_name(payload), "FAILED")

    def test_parse_prefect_state_name_unknown(self):
        payload = {}
        self.assertEqual(parse_prefect_state_name(payload), "UNKNOWN")

    def test_map_completed(self):
        self.assertEqual(map_prefect_state_to_exec_status("COMPLETED"), "COMPLETED")
        self.assertEqual(map_prefect_state_to_exec_status("SUCCESS"), "COMPLETED")

    def test_map_failed(self):
        self.assertEqual(map_prefect_state_to_exec_status("FAILED"), "FAILED")
        self.assertEqual(map_prefect_state_to_exec_status("CRASHED"), "FAILED")

    def test_map_cancelled(self):
        self.assertEqual(map_prefect_state_to_exec_status("CANCELLED"), "CANCELLED")
        self.assertEqual(map_prefect_state_to_exec_status("CANCELED"), "CANCELLED")

    def test_map_pending(self):
        self.assertEqual(map_prefect_state_to_exec_status("PENDING"), "PENDING")
        self.assertEqual(map_prefect_state_to_exec_status("SCHEDULED"), "PENDING")

    def test_map_other_defaults_to_running(self):
        self.assertEqual(map_prefect_state_to_exec_status("RUNNING"), "RUNNING")
        self.assertEqual(map_prefect_state_to_exec_status("PAUSED"), "RUNNING")
        self.assertEqual(map_prefect_state_to_exec_status(""), "RUNNING")
        self.assertEqual(map_prefect_state_to_exec_status(None), "RUNNING")
