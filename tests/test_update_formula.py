import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/update_formula.py"
SPEC = importlib.util.spec_from_file_location("update_formula", SCRIPT)
update_formula = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(update_formula)


class UpdateFormulaTests(unittest.TestCase):
    def test_version_is_derived_from_tag(self):
        self.assertEqual(update_formula.version_from_tag("v2.4.1"), "2.4.1")
        self.assertEqual(update_formula.version_from_tag("1.2"), "1.2")

    def test_rejects_non_numeric_release_tags(self):
        with self.assertRaises(update_formula.UpdateError):
            update_formula.version_from_tag("v2.0-rc1")

    def test_rewrites_only_the_release_fields(self):
        formula = (SCRIPT.parents[2] / "Formula/minfwm.rb").read_text(encoding="utf-8")
        checksum = "a" * 64

        updated = update_formula.render_formula(formula, "v1.2", checksum)

        self.assertIn('url "https://github.com/snusxd/minfwm/archive/refs/tags/v1.2.tar.gz"', updated)
        self.assertIn('version "1.2"', updated)
        self.assertIn(f'sha256 "{checksum}"', updated)
        self.assertIn('license :cannot_represent', updated)

    def test_rejects_invalid_checksum(self):
        formula = (SCRIPT.parents[2] / "Formula/minfwm.rb").read_text(encoding="utf-8")
        with self.assertRaises(update_formula.UpdateError):
            update_formula.render_formula(formula, "v1.2", "not-a-checksum")


if __name__ == "__main__":
    unittest.main()
