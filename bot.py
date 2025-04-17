import os
import json
import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

DAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
DATA_FILE = "schedule.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current": {}, "next": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("/список")], [KeyboardButton("/следующая")]]
    await update.message.reply_text("Привет! Напиши фамилию и день недели (например: Иванов понедельник).", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def list_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    result = "Текущая неделя:
"
    for day in DAYS:
        entries = data["current"].get(day, [])
        result += f"{day.title()}: {', '.join(entries) if entries else '—'}
"
    await update.message.reply_text(result)

async def list_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    result = "Следующая неделя:
"
    for day in DAYS:
        entries = data["next"].get(day, [])
        result += f"{day.title()}: {', '.join(entries) if entries else '—'}
"
    await update.message.reply_text(result)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    data = load_data()
    parts = text.split()
    if len(parts) != 2:
        await update.message.reply_text("Формат: Фамилия ДеньНедели. Пример: Иванов понедельник")
        return
    name, day = parts
    if day not in DAYS:
        await update.message.reply_text(f"Неизвестный день недели: {day}")
        return
    week = "next" if "следующая" in text else "current"
    data[week].setdefault(day, []).append(name.capitalize())
    save_data(data)
    await update.message.reply_text(f"Добавлено: {name.capitalize()} в {day.title()} ({'следующая' if week == 'next' else 'текущая'} неделя)")

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("список", list_all))
    app.add_handler(CommandHandler("следующая", list_next))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()