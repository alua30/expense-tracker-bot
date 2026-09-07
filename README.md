# 💸 Expense Tracker Bot

Telegram-бот для учёта личных расходов на **Python + aiogram 3 + SQLite**.

## Возможности

- ➕ Добавление расходов: сумма → категория → комментарий (FSM-диалог)
- 📊 Статистика по категориям за день / неделю / месяц / всё время
- 📁 Экспорт всех расходов в CSV (открывается в Excel)
- ↩️ Отмена последней записи
- 👥 Мультипользовательность — каждый видит только свои данные

## Быстрый старт

```bash
git clone https://github.com/<твой-ник>/expense-tracker-bot.git
cd expense-tracker-bot

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env  # впиши токен от @BotFather
python bot.py
```

## Стек

| Технология | Зачем |
|---|---|
| aiogram 3 | Telegram Bot API, FSM, клавиатуры |
| aiosqlite | асинхронная работа с SQLite |
| pytest + pytest-asyncio | тесты |

## Структура

```
bot.py        — точка входа, запуск polling
config.py     — конфигурация из .env
database.py   — слой работы с БД (инициализация, CRUD, статистика)
handlers.py   — обработчики команд и FSM-сценарий добавления расхода
keyboards.py  — reply/inline клавиатуры
tests/        — тесты слоя БД
```

## Тесты

```bash
pytest -v
```

## Roadmap

- [ ] Лимиты по категориям с уведомлениями
- [ ] Графики расходов (matplotlib)
- [ ] Перевод на PostgreSQL + Docker
- [ ] Напоминания о ежедневном учёте
