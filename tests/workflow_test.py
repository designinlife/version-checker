import unittest
from pathlib import Path


class GithubActionsWorkflowTestCase(unittest.TestCase):
    def test_build_job_has_30_minute_timeout(self):
        workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

        self.assertIn("    timeout-minutes: 30", workflow)
