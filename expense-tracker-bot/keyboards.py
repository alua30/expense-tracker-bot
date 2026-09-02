from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from database import DEFAULT_CATEGORIES


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить расход")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📁 Экспорт CSV")],
            [KeyboardButton(text="↩️ Отменить последнюю запись")],
        ],
        resize_keyboard=True,
    )


def categories_keyboard() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=cat, callback_data=f"cat:{cat}") for cat in DEFAULT_CATEGORIES]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cat:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def stats_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сегодня", callback_data="stats:today")],
            [InlineKeyboardButton(text="Эта неделя", callback_data="stats:week")],
            [InlineKeyboardButton(text="Этот месяц", callback_data="stats:month")],
            [InlineKeyboardButton(text="Всё время", callback_data="stats:all")],
        ]
    )
