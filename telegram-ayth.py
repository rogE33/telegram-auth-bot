import os
import threading
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import ChatNotFound, Unauthorized

# === Настройки ===
BOT_TOKEN = "7996753569:AAFu1k4_ybkkpFj2183oNE0ITSt6ayuTezc"
CHANNEL = "@SchoolAwards"  # Канал, на который должен быть подписан пользователь

# === Инициализация ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

# === Flask: проверка работы сайта ===
@app.route('/')
def home():
    return "✅ Бот SchoolAwards работает!"

# === Flask: страница авторизации через Telegram ===
@app.route('/telegram-auth', methods=['GET'])
def telegram_auth():
    # Проверяем, есть ли данные от Telegram
    user_id = request.args.get('id')
    first_name = request.args.get('first_name', '')
    username = request.args.get('username', '')

    if not user_id:
        return "Ошибка: не удалось получить данные пользователя.", 400

    # Проверка подписки на канал
    try:
        member = bot.get_chat_member(CHANNEL, int(user_id))
        if member and member.status in ["member", "administrator", "creator"]:
            return f"✅ Добро пожаловать, {first_name or username}! Вы успешно авторизовались через Telegram."
        else:
            return f"❌ Пожалуйста, подпишитесь на канал <a href='https://t.me/{CHANNEL[1:]}'>{CHANNEL}</a> и попробуйте снова.", 403
    except ChatNotFound:
        return "Ошибка: канал не найден. Проверь название канала.", 500
    except Unauthorized:
        return "Ошибка: бот не добавлен в канал или не имеет прав для проверки подписчиков.", 500
    except Exception as e:
        return f"Ошибка при проверке подписки: {e}", 500

# === Aiogram: приветственное сообщение в Telegram ===
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    text = (
        "👋 Привет! Это бот авторизации для School Awards.\n\n"
        "Чтобы авторизоваться на сайте, нажми кнопку ниже 👇"
    )
    # Создаем кнопку входа через Telegram
    button = types.InlineKeyboardButton(
        "Войти через Telegram",
        url="https://http://a1183826.xsph.ru/.onrender.com/telegram-auth"
    )
    keyboard = types.InlineKeyboardMarkup().add(button)
    await message.answer(text, reply_markup=keyboard)

# === Функция запуска бота ===
def run_bot():
    executor.start_polling(dp, skip_updates=True)

# === Запуск Flask + Aiogram в двух потоках ===
if name == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
