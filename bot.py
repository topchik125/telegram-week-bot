
import json
import os
import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

DATA_FILE = "week.json"
NEXT_WEEK_FILE = "next_week.json"

DAYS = [
    "понедельник", "вторник", "среда",
    "четверг", "пятница", "суббота", "воскресенье"
]

def load_data(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {day: [] for day in DAYS}

def save_data(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def reset_week_if_needed():
    today = datetime.datetime.now().weekday()  # 0 - понедельник
    if today == 0:
        data = {day: [] for day in DAYS}
        save_data(data, DATA_FILE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["/list", "/next"], ["/help"]]
    await update.message.reply_text(
        "Привет! Просто отправь сообщение в формате: Фамилия ДеньНедели Пример: Иванов понедельник",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Формат ввода:
Иванов понедельник

Команды:
/list – текущая неделя
/next – следующая неделя"
    )

async def list_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_week_if_needed()
    data = load_data(DATA_FILE)
    result = "Текущая неделя:

"
    for day in DAYS:
        names = data.get(day, [])
        if names:
            result += f"{day.upper()}:
" + ''.join(f"- {name}
" for name in names) + "
"
        else:
            result += f"{day.upper()}:
- (пусто)

"
    await update.message.reply_text(result)

async def list_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data(NEXT_WEEK_FILE)
    result = "Следующая неделя:

"
    for day in DAYS:
        names = data.get(day, [])
        if names:
            result += f"{day.upper()}:
" + ''.join(f"- {name}
" for name in names) + "
"
        else:
            result += f"{day.upper()}:
- (пусто)

"
    await update.message.reply_text(result)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = text.split()
    if len(parts) != 2:
        await update.message.reply_text("Неверный формат. Пример: Иванов понедельник")
        return

    name, day = parts
    day = day.lower()
    if day.endswith("*"):  # Если указывает на следующую неделю (например, "понедельник*")
        day = day[:-1]
        target_file = NEXT_WEEK_FILE
    else:
        target_file = DATA_FILE

    if day not in DAYS:
        await update.message.reply_text("Неверный день недели.")
        return

    data = load_data(target_file)
    data[day].append(name)
    save_data(data, target_file)
    await update.message.reply_text(f"Добавлено: {name} → {day.title()}")

def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_all))
    app.add_handler(CommandHandler("next", list_next))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
