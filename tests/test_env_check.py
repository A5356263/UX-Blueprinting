from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.env_check.core import run_env_check


class EnvCheckTests(unittest.TestCase):
    def test_env_check_writes_latest_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            report_path = Path(td) / "env-check-report.json"
            passing_check = {"check_id": "demo", "status": "passed", "message": "ok", "fixable": False, "details": {}}
            with (
                patch("packages.env_check.core.get_env_check_report_path", return_value=report_path),
                patch("packages.env_check.core._check_required_roots", return_value=passing_check),
                patch("packages.env_check.core._check_release_layout", return_value=passing_check),
                patch("packages.env_check.core._check_platform_match", return_value=passing_check),
                patch("packages.env_check.core._check_tmp_roundtrip", return_value=passing_check),
                patch("packages.env_check.core._check_projects_writable", return_value=passing_check),
                patch("packages.env_check.core._check_cli_entrypoint", return_value=passing_check),
                patch("packages.env_check.core._check_capability_listing", return_value=passing_check),
                patch("packages.env_check.core._check_run_script", return_value=passing_check),
                patch("packages.env_check.core._check_smoke_project", return_value=passing_check),
            ):
                exit_code = run_env_check()

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())

            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("mode"), "package_runtime")
            self.assertEqual(payload.get("status"), "passed")
            self.assertIn("checks", payload)
            self.assertIsInstance(payload["checks"], list)
            self.assertGreaterEqual(len(payload["checks"]), 1)

    def test_env_check_fails_when_runtime_root_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            report_path = Path(td) / "env-check-report.json"
            with (
                patch("packages.env_check.core.get_env_check_report_path", return_value=report_path),
                patch(
                    "packages.env_check.core._check_required_roots",
                    return_value={
                        "check_id": "required_roots",
                        "status": "failed",
                        "message": "Release runtime roots are missing; the package cannot run stably on this machine.",
                        "fixable": False,
                        "details": {"missing": {"templates_root": "/missing"}},
                    },
                ),
                patch("packages.env_check.core._check_release_layout", return_value={"check_id": "demo", "status": "passed", "message": "ok", "fixable": False, "details": {}}),
                patch("packages.env_check.core._check_platform_match", return_value={"check_id": "demo", "status": "passed", "message": "ok", "fixable": False, "details": {}}),
                patch("packages.env_check.core._check_tmp_roundtrip", return_value={"check_id": "demo", "status": "passed", "message": "ok", "fixable": False, "details": {}}),
                patch("packages.env_check.core._check_projects_writable", return_value={"check_id": "demo", "status": "passed", "message": "ok", "fixable": False, "details": {}}),
                patch("packages.env_check.core._check_cli_entrypoint", return_value={"check_id": "demo", "status": "passed", "message": "ok", "fixable": False, "details": {}}),
                patch("packages.env_check.core._check_capability_listing", return_value={"check_id": "demo", "status": "passed", "message": "ok", "fixable": False, "details": {}}),
                patch("packages.env_check.core._check_run_script", return_value={"check_id": "demo", "status": "passed", "message": "ok", "fixable": False, "details": {}}),
                patch("packages.env_check.core._check_smoke_project", return_value={"check_id": "demo", "status": "passed", "message": "ok", "fixable": False, "details": {}}),
            ):
                exit_code = run_env_check()

            self.assertEqual(exit_code, 1)
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("status"), "failed")
            errors = payload.get("errors", [])
            self.assertTrue(any("Release runtime roots are missing" in str(item) for item in errors))


if __name__ == "__main__":
    unittest.main()
