# Report generator

Учебный генератор отчетов по данным из JSON-файла.

## Запуск

    python report.py data.json              # сводка в виде словаря
    python report.py data.json --text       # текстовая сводка
    python report.py data.json -o report.json   # запись отчета в JSON

## Формат данных

Файл `data.json` (в репозитории хранится только шаблон `data.json.example`):

    {"items": [{"name": "Notebook", "qty": 3, "price": 120.5}]}

Рабочие файлы `data.json` и `report.json` в репозиторий не попадают (см. `.gitignore`).
