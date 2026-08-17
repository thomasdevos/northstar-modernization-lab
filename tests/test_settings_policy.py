import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SettingsPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))

    def test_default_deny_and_no_bypass(self):
        permissions = self.settings["permissions"]
        self.assertEqual("dontAsk", permissions["defaultMode"])
        self.assertNotIn("bypassPermissions", json.dumps(self.settings))

    def test_no_bare_read_search_allow(self):
        allowed = self.settings["permissions"]["allow"]
        self.assertTrue({"Read", "Glob", "Grep"}.isdisjoint(allowed))

    def test_mandatory_sandbox(self):
        sandbox = self.settings["sandbox"]
        self.assertTrue(sandbox["enabled"])
        self.assertTrue(sandbox["failIfUnavailable"])
        self.assertFalse(sandbox["allowUnsandboxedCommands"])

    def test_protected_write_boundaries(self):
        deny = set(self.settings["permissions"]["deny"])
        for tree in ("legacy_app/**", "fixtures/golden-master/**"):
            self.assertIn(f"Edit({tree})", deny)
            self.assertNotIn(f"Write({tree})", deny)
        deny_write = set(self.settings["sandbox"]["filesystem"]["denyWrite"])
        self.assertEqual({"./legacy_app/", "./fixtures/golden-master/"}, deny_write)
        self.assertTrue(all(path.startswith("./") for path in deny_write))

    def test_write_is_covered_by_direct_file_hook(self):
        entries = self.settings["hooks"]["PreToolUse"]
        matchers = [set(entry["matcher"].split("|")) for entry in entries]
        self.assertIn({"Edit", "Write"}, matchers)
        self.assertTrue(all("Bash" not in matcher for matcher in matchers))

    def test_companion_readme_does_not_claim_bash_hook_enforcement(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("Edit|Write|Bash", readme)
        self.assertNotIn("rejects literal Bash commands", readme)
        self.assertIn("deliberately does not inspect Bash strings", readme)
        self.assertIn("sandbox", readme.lower())


if __name__ == "__main__":
    unittest.main()