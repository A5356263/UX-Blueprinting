from __future__ import annotations

import json
import unittest

from packages.common import sanitize_json_text


class SanitizeJsonTextTests(unittest.TestCase):
    def test_preserves_curly_quotes_inside_valid_json_strings(self) -> None:
        raw = '{\n  "message": "业务提示包含“中文引号”与普通文本"\n}'

        sanitized = sanitize_json_text(raw)
        payload = json.loads(sanitized)

        self.assertEqual(payload["message"], "业务提示包含“中文引号”与普通文本")
        self.assertEqual(sanitized, raw)

    def test_normalizes_curly_quote_delimiters(self) -> None:
        raw = '{\n  “status”： “passed”，\n  “stage”： “facts”，\n}'

        sanitized = sanitize_json_text(raw)
        payload = json.loads(sanitized)

        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["stage"], "facts")


if __name__ == "__main__":
    unittest.main()
