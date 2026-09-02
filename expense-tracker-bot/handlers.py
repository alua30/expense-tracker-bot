import csv
import io
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from database import add_expense, delete_last_expense, get_expenses, get_stats
from keyboards import categories_keyboard, main_keyboard, stats_keyboard

router = Router()


class AddExpense(StatesGroup):
    amount = State()
    category = State()
    note = State()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот для учёта расходов 💸\n\n"
        "• «➕ Добавить расход» — записать трату\n"
        "• «📊 Статистика» — расходы по категориям\n"
        "• «📁 Экспорт CSV» — выгрузить все данные",
        reply_markup=main_keyboard(),
    )


@router.message(F.text == "➕ Добавить расход")
async def start_add(message: Message, state: FSMContext) -> None:
    await state.set_state(AddExpense.amount)
    await message.answer("Введи сумму расхода (например, 450 или 1299.90):")


@router.message(AddExpense.amount)
async def process_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer("Это не похоже на сумму. Введи положительное число:")
        return
    await state.update_data(amount=amount)
    await state.set_state(AddExpense.category)
    await message.answer("Выбери категорию:", reply_markup=categories_keyboard())


@router.callback_query(AddExpense.category, F.data.startswith("cat:"))
async def process_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.split(":", 1)[1]
    if category == "cancel":
        await state.clear()
        await callback.message.edit_text("Отменено.")
        await callback.answer()
        return
    await state.update_data(category=category)
    await state.set_state(AddExpense.note)
    await callback.message.edit_text("Добавь комментарий или отправь «-», чтобы пропустить:")
    await callback.answer()


@router.message(AddExpense.note)
async def process_note(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    note = None if message.text.strip() == "-" else message.text.strip()
    await add_expense(message.from_user.id, data["amount"], data["category"], note)
    await state.clear()
    await message.answer(
        f"✅ Записано: {data['amount']:.2f} — {data['category']}",
        reply_markup=main_keyboard(),
    )


@router.message(F.text == "📊 Статистика")
async def stats_menu(message: Message) -> None:
    await message.answer("За какой период показать статистику?", reply_markup=stats_keyboard())


@router.callback_query(F.data.startswith("stats:"))
async def show_stats(callback: CallbackQuery) -> None:
    period = callback.data.split(":")[1]
    today = date.today()
    start, title = {
        "today": (today, "сегодня"),
        "week": (today - timedelta(days=today.weekday()), "эту неделю"),
        "month": (today.replace(day=1), "этот месяц"),
        "all": (date(1970, 1, 1), "всё время"),
    }[period]

    rows = await get_stats(callback.from_user.id, start, today)
    if not rows:
        await callback.message.edit_text(f"За {title} расходов нет.")
        await callback.answer()
        return

    total = sum(amount for _, amount in rows)
    lines = [f"📊 Расходы за {title}:\n"]
    for category, amount in rows:
        lines.append(f"• {category}: {amount:.2f}")
    lines.append(f"\n💰 Итого: {total:.2f}")
    await callback.message.edit_text("\n".join(lines))
    await callback.answer()


@router.message(F.text == "📁 Экспорт CSV")
async def export_csv(message: Message) -> None:
    rows = await get_expenses(message.from_user.id)
    if not rows:
        await message.answer("Пока нечего экспортировать — расходов нет.")
        return

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["amount", "category", "note", "created_at"])
    writer.writerows(rows)

    file = BufferedInputFile(buffer.getvalue().encode("utf-8-sig"), filename="expenses.csv")
    await message.answer_document(file, caption=f"Все расходы ({len(rows)} записей)")


@router.message(F.text == "↩️ Отменить последнюю запись")
async def undo_last(message: Message) -> None:
    deleted = await delete_last_expense(message.from_user.id)
    if deleted:
        await message.answer(f"🗑 Удалено: {deleted[0]:.2f} — {deleted[1]}")
    else:
        await message.answer("Нечего удалять — записей нет.")
