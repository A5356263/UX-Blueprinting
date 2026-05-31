from __future__ import annotations

import unittest
from unittest.mock import patch

from packages.validate.core import run_coverage_for_current_mode, run_validate_for_current_mode


class ValidateModeRoutingTests(unittest.TestCase):
    @patch("packages.validate.core.run_validate_outputs", return_value=11)
    @patch("packages.validate.core.run_validate_lite", return_value=22)
    @patch("packages.validate.core._final_check_execution_mode", return_value="full")
    def test_validate_dispatches_full_mode(
        self,
        _mode,
        validate_lite,
        validate_full,
    ) -> None:
        result = run_validate_for_current_mode("demo")
        self.assertEqual(result, 11)
        validate_full.assert_called_once_with("demo")
        validate_lite.assert_not_called()

    @patch("packages.validate.core.run_validate_outputs", return_value=11)
    @patch("packages.validate.core.run_validate_lite", return_value=22)
    @patch("packages.validate.core._final_check_execution_mode", return_value="standard")
    def test_validate_dispatches_lite_mode(
        self,
        _mode,
        validate_lite,
        validate_full,
    ) -> None:
        result = run_validate_for_current_mode("demo")
        self.assertEqual(result, 22)
        validate_lite.assert_called_once_with("demo")
        validate_full.assert_not_called()

    @patch("packages.validate.core.run_coverage_check", return_value=33)
    @patch("packages.validate.core.run_coverage_lite", return_value=44)
    @patch("packages.validate.core._final_check_execution_mode", return_value="fast")
    def test_coverage_dispatches_lite_mode(
        self,
        _mode,
        coverage_lite,
        coverage_full,
    ) -> None:
        result = run_coverage_for_current_mode("demo")
        self.assertEqual(result, 44)
        coverage_lite.assert_called_once_with("demo")
        coverage_full.assert_not_called()


if __name__ == "__main__":
    unittest.main()
