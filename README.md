Burcenco Anatoli
# quest-cli

Текстовый квест для терминала на **Click** с хранением данных в **SQLite** через **SQLAlchemy** (ORM).

История — граф сцен (4 концовки). Прогресс сохраняется после каждого шага, а при повторном запуске игра продолжается с того же места. Достигнутые концовки копятся в базе, по ним строится статистика.

## Установка

Требуется Python 3.10+.

```bash
git clone <URL-репозитория>
cd quest-cli
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .                 # только утилита
pip install -e ".[dev]"          # + pytest и ruff для разработки
```

Альтернатива: `pip install -r requirements.txt` (все зависимости, включая dev).

## Использование

```bash
quest play            # играть; продолжает с сохранённой сцены
quest play --new      # начать заново, забыв сохранение
quest stats           # статистика концовок: оба вида сразу
quest stats --view abs   # только числа
quest stats --view rel   # только проценты
quest --help
```

Также работает `python -m quest ...`.

Пример:

```
$ quest play

Вы стоите на опушке тёмного леса. ...
Ваш выбор (north, south): north
...
$ quest stats
treasure: 5 (62.5%)
dragon: 3 (37.5%)
village: 0 (0.0%)
waterfall: 0 (0.0%)
$ quest stats --view rel
treasure: 62.5%
dragon: 37.5%
...
```

Ожидаемые ошибки (неверное значение `--view`, недоступная база или лог-файл) выводятся понятным сообщением, команда завершается с ненулевым кодом (`1` — ошибка выполнения, `2` — неверное использование).

## Файлы данных и настройки

| Что | По умолчанию | Переопределение |
| --- | --- | --- |
| База SQLite | `stats.db` в текущей папке | переменная `QUEST_DB_URL`, например `sqlite:///other.db` |
| Лог | `app.log` в текущей папке | переменная `QUEST_LOG_FILE` |

В лог пишутся начало/продолжение игры, каждый выбор, достигнутые концовки и ошибки (включая откаты транзакций).

## Структура

```
quest/
  story.py          # граф сцен, next_node, is_ending, list_endings
  db.py             # модели Progress/Ending, save/load_progress, record_ending, count_endings
  stats.py          # format_stat, format_endings_stats
  logging_config.py # логирование в app.log
  cli.py            # тонкие обработчики Click (group, play, stats)
tests/
  test_quest.py     # next_node, is_ending, проверка графа истории
  test_db.py        # save/load_progress, record_ending, count_endings, откат транзакций
  test_stats.py     # format_stat, format_endings_stats
  test_cli.py       # команды play/stats через CliRunner, ошибки, логирование
```

## Тесты и проверки

```bash
pytest                 # тесты (SQLite в памяти / во временных файлах)
ruff format --check .  # форматирование
ruff check .           # линтинг
```
