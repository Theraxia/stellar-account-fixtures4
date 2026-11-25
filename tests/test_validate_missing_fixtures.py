#!/usr/bin/env python3
"""Pin the programmatic validate() contract when the fixtures directory is absent.

The CLI refuses an unreadable corpus root before it calls validate(), so only a direct
caller sees this branch. That caller gets one structured problem naming the missing path
and an empty report, never an exception from iterdir(). An exception escaping any case
below fails the test with its own traceback, so no case wraps the call in try/except.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import validate  # noqa: E402


class MissingFixturesDirectory(unittest.TestCase):
    def setUp(self) -> None:
        stage = tempfile.TemporaryDirectory(prefix="missing-fixtures-")
        self.addCleanup(stage.cleanup)
        self.root = Path(stage.name)

    def test_an_absent_fixtures_directory_is_one_clean_problem(self) -> None:
        self.assertFalse((self.root / "fixtures").exists())

        problems, report = validate.validate(self.root)

        expected = f"{self.root / 'fixtures'}: no fixtures directory"
        self.assertEqual(problems, [expected])
        self.assertIn("fixtures: no fixtures directory", problems[0])
        self.assertEqual(report, [])

    def test_report_mode_still_returns_an_empty_report(self) -> None:
        problems, report = validate.validate(self.root, report=True)

        self.assertEqual(len(problems), 1)
        self.assertEqual(report, [])

    def test_a_file_named_fixtures_is_not_a_directory(self) -> None:
        (self.root / "fixtures").write_text("not a directory\n", encoding="utf-8")

        problems, report = validate.validate(self.root, report=True)

        self.assertEqual(problems, [f"{self.root / 'fixtures'}: no fixtures directory"])
        self.assertEqual(report, [])
