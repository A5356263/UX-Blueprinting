from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from packages.route_decision import run_route_decision_options


class RouteDecisionOptionsTests(unittest.TestCase):
    def test_options_lists_refs_without_recommendation_language(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = run_route_decision_options("demo")

        output = buffer.getvalue()
        self.assertEqual(result, 0)
        self.assertIn("可用 complexity refs：", output)
        self.assertIn("可用 business summary refs：", output)
        self.assertIn("可用 guideline summary refs：", output)
        self.assertNotIn("建议", output)
        self.assertNotIn("必须读取", output)
        self.assertNotIn("自动选择", output)


if __name__ == "__main__":
    unittest.main()
