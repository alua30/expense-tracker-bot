from datetime import date, timedelta

import pytest
import pytest_asyncio

import database


@pytest_asyncio.fixture(autouse=True)
async def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    await database.init_db()
    yield


@pytest.mark.asyncio
async def test_add_and_stats():
    await database.add_expense(1, 100.0, "Еда")
    await database.add_expense(1, 50.0, "Транспорт")
    await database.add_expense(1, 200.0, "Еда")

    rows = await database.get_stats(1, date.today() - timedelta(days=1), date.today())
    assert dict(rows) == {"Еда": 300.0, "Транспорт": 50.0}


@pytest.mark.asyncio
async def test_users_are_isolated():
    await database.add_expense(1, 100.0, "Еда")
    await database.add_expense(2, 999.0, "Еда")

    rows = await database.get_stats(1, date.today(), date.today())
    assert dict(rows) == {"Еда": 100.0}


@pytest.mark.asyncio
async def test_delete_last():
    await database.add_expense(1, 100.0, "Еда")
    await database.add_expense(1, 50.0, "Транспорт")

    deleted = await database.delete_last_expense(1)
    assert deleted == (50.0, "Транспорт")

    rows = await database.get_expenses(1)
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_delete_last_empty():
    assert await database.delete_last_expense(1) is None
