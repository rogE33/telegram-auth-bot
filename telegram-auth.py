import os
import asyncio
from flask import Flask, request, redirect
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramBadRequest

# === Настройки ===
BOT_TOKEN = "7996753569:AAFu1k4_ybkkpFj2183oNE0ITSt6ayuTezc"
CHANNEL = "@SchoolAwards"

# === Инициализация ===
session = AiohttpSession()
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher(bot)

app = Flask(__name__)

# === Flask: проверка работы сервера ===
@app.route('/')
def home():
    return "✅ Бот SchoolAwards работает!"

# === Flask: авторизация через Telegram ===
@app.route('/telegram-auth', methods=['GET'])
async def telegram_auth():
    user_id = request.args.get('id')
    first_name = request.args.get('first_name', '')
    username = request.args.get('username', '')

    if not user_id:
        return "Ошибка: не удалось получить данные пользователя.", 400

    try:
        member = await bot.get_chat_member(CHANNEL, int(user_id))
        if member.status in ["member", "administrator", "creator"]:
            return f"✅ Добро пожаловать, {first_name or username}! Вы успешно авторизовались через Telegram."
        else:
            return f"❌ Пожалуйста, подпишитесь на канал <a href='https://t.me/{CHANNEL[1:]}'>{CHANNEL}</a> и попробуйте снова.", 403
    except TelegramBadRequest as e:
        return f"Ошибка проверки подписки: {e}", 500
    except Exception as e:
        return f"Произошла ошибка: {e}", 500

# === Aiogram: команда /start ===
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    text = (
        "👋 Привет! Это бот авторизации для School Awards.\n\n"
        "Чтобы авторизоваться на сайте, нажми кнопку ниже 👇"
    )
    button = types.InlineKeyboardButton(
        "Войти через Telegram",
        url=f"https://a1183826.xsph.ru/.onrender.com/telegram-auth"
    )
    keyboard = types.InlineKeyboardMarkup().add(button)
    await message.answer(text, reply_markup=keyboard)

# === Запуск Aiogram бота в отдельном asyncio loop ===
async def main():
    await dp.start_polling()

# === Запуск Flask + Aiogram через asyncio ===
if name == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    port = int(os.environ.get("PORT", 5000))
    # Flask запускается в стандартном режиме, но поддерживает async view
    app.run(host="0.0.0.0", port=port)
