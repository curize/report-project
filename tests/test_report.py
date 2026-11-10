import json
import tempfile
import unittest
from pathlib import Path

from report import load_data


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def write(self, name, text):
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        return path


class LoadDataTest(TempDirCase):
    def test_load_valid(self):
        path = self.write("d.json", json.dumps({"items": [{"name": "A", "qty": 1, "price": 2.0}]}))
        self.assertEqual(len(load_data(path)["items"]), 1)

    def test_missing_file(self):
        with self.assertRaises(OSError):
            load_data(self.dir / "nope.json")

    def test_broken_json(self):
        path = self.write("d.json", "{broken")
        with self.assertRaises(ValueError):
            load_data(path)

    def test_no_items_key(self):
        path = self.write("d.json", "{}")
        with self.assertRaises(ValueError):
            load_data(path)

    def test_unicode(self):
        text = json.dumps({"items": [{"name": "Тетрадь", "qty": 1, "price": 1}]}, ensure_ascii=False)
        path = self.write("d.json", text)
        self.assertEqual(load_data(path)["items"][0]["name"], "Тетрадь")


if __name__ == "__main__":
    unittest.main()
