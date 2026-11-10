import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from report import get_title, load_data, main, summarize, text_summary, write_report


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


class TextSummaryTest(unittest.TestCase):
    def setUp(self):
        self.summary = {"count": 3, "total": 760.5, "average": 253.5, "top": "Pen"}

    def test_lines(self):
        lines = text_summary(self.summary, "Title").splitlines()
        self.assertEqual(lines, [
            "Title",
            "Items: 3",
            "Total: 760.50",
            "Average: 253.50",
            "Top item: Pen",
        ])

    def test_custom_title_is_first_line(self):
        self.assertEqual(text_summary(self.summary, "Отчёт").splitlines()[0], "Отчёт")


class CliTextTest(TempDirCase):
    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(list(args))
        return code, out.getvalue()

    def test_text_option(self):
        data = self.write("d.json", json.dumps({"items": [{"name": "A", "qty": 2, "price": 10}]}))
        code, output = self.run_main(str(data), "--text")
        self.assertEqual(code, 0)
        self.assertIn("Items: 1", output)
        self.assertIn("Total: 20.00", output)

    def test_missing_file_returns_2(self):
        code, _ = self.run_main(str(self.dir / "nope.json"), "--text")
        self.assertEqual(code, 2)


class TitleTest(unittest.TestCase):
    def test_english(self):
        self.assertEqual(get_title("en"), "Sales report")

    def test_russian(self):
        self.assertEqual(get_title("ru"), "Отчёт о продажах")

    def test_default_is_english(self):
        self.assertEqual(get_title(), "Sales report")

    def test_unsupported_language(self):
        with self.assertRaises(ValueError):
            get_title("de")


class CliLangTest(TempDirCase):
    def test_lang_ru_in_text(self):
        data = self.write("d.json", json.dumps({"items": [{"name": "A", "qty": 1, "price": 1}]}))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([str(data), "--text", "--lang", "ru"])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().splitlines()[0], "Отчёт о продажах")


if __name__ == "__main__":
    unittest.main()
