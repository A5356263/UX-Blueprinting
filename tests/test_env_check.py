from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.common import get_repo_root
from packages.env_check.core import run_env_check


class EnvCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = get_repo_root()

    def test_env_check_writes_latest_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            report_path = Path(td) / "env-check-report.json"
            with patch("packages.env_check.core.get_env_check_report_path", return_value=report_path):
                exit_code = run_env_check()

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())

            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertIn(payload.get("status"), {"passed", "warning"})
            self.assertIn("checks", payload)
            self.assertIsInstance(payload["checks"], list)
            self.assertGreaterEqual(len(payload["checks"]), 4)

    @patch("packages.env_check.core.get_templates_root_dir")
    def test_env_check_fails_when_required_root_is_missing(self, mocked_templates_root) -> None:
        mocked_templates_root.return_value = self.repo_root / "__missing_env_check_templates__"

        with tempfile.TemporaryDirectory() as td:
            report_path = Path(td) / "env-check-report.json"
            with patch("packages.env_check.core.get_env_check_report_path", return_value=report_path):
                exit_code = run_env_check()

            self.assertEqual(exit_code, 1)
            self.assertTrue(report_path.exists())

            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("status"), "failed")
            errors = payload.get("errors", [])
            self.assertTrue(any("关键目录缺失" in str(item) for item in errors))


if __name__ == "__main__":
    unittest.main()
