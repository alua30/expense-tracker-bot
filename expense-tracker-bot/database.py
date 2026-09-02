from datetime import date, datetime

import aiosqlite

from config import DB_PATH

DEFAULT_CATEGORIES = [
    "Еда",
    "Транспорт",
    "Жильё",
    "Развлечения",
    "Здоровье",
    "Одежда",
    "Другое",
]


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_expenses_user_date "
            "ON expenses (user_id, created_at)"
        )
        await db.commit()


async def add_expense(user_id: int, amount: float, category: str, note: str | None = None) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO expenses (user_id, amount, category, note, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, note, datetime.now().isoformat(timespec="seconds")),
        )
        await db.commit()


async def delete_last_expense(user_id: int) -> tuple[float, str] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, amount, category FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        await db.execute("DELETE FROM expenses WHERE id = ?", (row[0],))
        await db.commit()
        return row[1], row[2]


async def get_stats(user_id: int, start: date, end: date) -> list[tuple[str, float]]:
    """Sum per category between two dates (inclusive)."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT category, SUM(amount) FROM expenses
            WHERE user_id = ? AND date(created_at) BETWEEN ? AND ?
            GROUP BY category ORDER BY SUM(amount) DESC
            """,
            (user_id, start.isoformat(), end.isoformat()),
        )
        return await cursor.fetchall()


async def get_expenses(user_id: int) -> list[tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT amount, category, note, created_at FROM expenses WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        return await cursor.fetchall()
