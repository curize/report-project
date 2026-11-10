"""Генератор отчетов по данным из JSON."""
import argparse
import json
import sys

REPORT_TITLE = "Report"


def load_data(path):
    """Читает JSON-файл и возвращает словарь с ключом items (список)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("Ожидается JSON-объект с ключом items (список)")
    return data


def build_parser():
    parser = argparse.ArgumentParser(description="Генератор отчетов")
    parser.add_argument("data", help="Входной JSON-файл")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        data = load_data(args.data)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"{REPORT_TITLE}: {len(data['items'])} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
