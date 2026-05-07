import unittest
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from script_registry import list_categories, list_scripts  # noqa: E402


class TestScriptRegistry(unittest.TestCase):
    def test_registry_not_empty(self) -> None:
        self.assertGreater(len(list_scripts()), 0)

    def test_required_fields_exist(self) -> None:
        required_fields = {
            "script",
            "category",
            "purpose",
            "inputs",
            "outputs",
            "dependencies",
            "order",
        }
        for item in list_scripts():
            self.assertTrue(required_fields.issubset(item.keys()))

    def test_categories_exist(self) -> None:
        categories = list_categories()
        self.assertIn("analysis", categories)
        self.assertIn("data_processing", categories)
        self.assertIn("reporting", categories)


if __name__ == "__main__":
    unittest.main()
