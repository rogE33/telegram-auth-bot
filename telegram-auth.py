import os
from flask import Flask, request
import telebot

# === Настройки ===
BOT_TOKEN = "7996753569:AAFu1k4_ybkkpFj2183oNE0ITSt6ayuTezc"
CHANNEL = "@SchoolAwards"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === Flask: проверка работы сервера ===
@app.route("/")
def home():
    return "✅ Бот SchoolAwards работает!"

# === Flask: авторизация через Telegram ===
@app.route("/telegram-auth", methods=["GET"])
def telegram_auth():
    user_id = request.args.get("id")
    first_name = request.args.get("first_name", "")
    username = request.args.get("username", "")

    if not user_id:
        return "Ошибка: не удалось получить данные пользователя.", 400

    try:
        member = bot.get_chat_member(CHANNEL, int(user_id))
        if member.status in ["member", "administrator", "creator"]:
            return f"✅ Добро пожаловать, {first_name or username}! Вы успешно авторизовались через Telegram."
        else:
            return f"❌ Пожалуйста, подпишитесь на канал <a href='https://t.me/{CHANNEL[1:]}'>{CHANNEL}</a> и попробуйте снова.", 403
    except Exception as e:
        return f"Ошибка проверки подписки: {e}", 500

# === Telegram: команда /start ===
@bot.message_handler(commands=["start"])
def cmd_start(message):
    text = (
        "👋 Привет! Это бот авторизации для School Awards.\n\n"
        "Чтобы авторизоваться на сайте, нажми кнопку ниже 👇"
    )
    button_url = f"https://a1183826.xsph.ru/.onrender.com/telegram-auth"
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton("Войти через Telegram", url=button_url)
    markup.add(button)
    bot.send_message(message.chat.id, text, reply_markup=markup)

# === Запуск Flask + бота ===
if __name__ == "__main__":
    import threading

    # Запускаем Telegram-бота в отдельном потоке
    bot_thread = threading.Thread(target=bot.infinity_polling, daemon=True)
    bot_thread.start()

    # Запускаем Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
