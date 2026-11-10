import json
import tempfile
import unittest
from pathlib import Path

from report import load_data, summarize, write_report


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


class SummarizeTest(unittest.TestCase):
    def test_count_total_average_top(self):
        data = {"items": [{"name": "A", "qty": 2, "price": 10}, {"name": "B", "qty": 1, "price": 5}]}
        self.assertEqual(
            summarize(data),
            {"count": 2, "total": 25.0, "average": 12.5, "top": "A"},
        )

    def test_empty_items(self):
        self.assertEqual(
            summarize({"items": []}),
            {"count": 0, "total": 0.0, "average": 0.0, "top": None},
        )

    def test_rounding_to_cents(self):
        data = {"items": [{"name": "A", "qty": 3, "price": 0.1}]}
        self.assertEqual(summarize(data)["total"], 0.3)


class WriteReportTest(TempDirCase):
    def test_write_and_read_back(self):
        summary = {"count": 1, "total": 2.0, "average": 2.0, "top": "Тетрадь"}
        path = self.dir / "r.json"
        write_report(path, summary, "Заголовок")
        saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved["title"], "Заголовок")
        self.assertEqual(saved["summary"], summary)

    def test_file_is_utf8(self):
        path = self.dir / "r.json"
        write_report(path, {"top": "Тетрадь"}, "Отчёт")
        self.assertIn("Тетрадь", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
