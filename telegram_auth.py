from flask import Flask, redirect, request, jsonify
import telebot
import os

# === Настройки ===
BOT_TOKEN = "7996753569:AAFu1k4_ybkkpFj2183oNE0ITSt6ayuTezc"  # вставь сюда токен своего бота
CHANNEL_USERNAME = "@SchoolAwards"  # название канала
REDIRECT_URL = "http://a1183826.xsph.ru/?p=111"  # куда отправлять после проверки

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

# === Проверка подписки ===
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        print("Ошибка при проверке:", e)
        return False

# === Главная страница (кнопка авторизации) ===
@app.route("/")
def home():
    return """
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial;
                background: #f9f9f9;
                text-align: center;
                padding-top: 100px;
            }
            a.button {
                display: inline-block;
                padding: 15px 40px;
                background: white;
                color: black;
                text-decoration: none;
                border-radius: 40px;
                font-weight: bold;
                transition: background 0.3s;
                border: 2px solid #B39298;
            }
            a.button:hover {
                background: #B39298;
                color: white;
            }
        </style>
    </head>
    <body>
        <a class="button" href="/start_auth">Голосовать</a>
    </body>
    </html>
    """

# === Начало авторизации ===
@app.route("/start_auth")
def start_auth():
    telegram_login = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
    return f"""
    <html><body style='font-family: Arial; text-align: center; padding-top: 100px;'>
    <p>Для продолжения подпишитесь на наш Telegram-канал:</p>
    <a href="{telegram_login}" target="_blank">Перейти в Telegram</a><br><br>
    <form action="/check_subscription" method="get">
        <input type="number" name="user_id" placeholder="Введите ваш Telegram ID" required>
        <button type="submit">Проверить</button>
    </form>
    </body></html>
    """

# === Проверка подписки ===
@app.route("/check_subscription")
def check():
    user_id = request.args.get("user_id")
    if not user_id:
        return "Ошибка: не указан Telegram ID."

    try:
        user_id = int(user_id)
    except ValueError:
        return "Некорректный ID."

    if check_subscription(user_id):
        return redirect(REDIRECT_URL)
    else:
        return "❌ Вы не подписаны на канал. Подпишитесь и попробуйте снова."

# === Запуск ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
