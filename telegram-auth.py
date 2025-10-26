from flask import Flask, request, redirect
import telebot

BOT_TOKEN = "7996753569:AAFu1k4_ybkkpFj2183oNE0ITSt6ayuTezc"
CHANNEL = "@SchoolAwards"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route("/telegram-auth", methods=["GET"])
def telegram_auth():
    user_id = request.args.get("id")
    next_page = request.args.get("next", "https://a1183826.xsph.ru/")  # ссылка по умолчанию

    if not user_id:
        # Если пользователь открыл ссылку напрямую
        return """
        <h3>Нужно авторизоваться через Telegram</h3>
        <a href="https://t.me/SchoolAwards_bot?start=login">Авторизация через Telegram</a>
        """

    try:
        member = bot.get_chat_member(CHANNEL, int(user_id))
        if member.status in ["member", "administrator", "creator"]:
            # Редирект на WordPress страницу
            return redirect(next_page)
        else:
            return f"""
            <h3>❌ Подпишитесь на канал <a href='https://t.me/{CHANNEL[1:]}'>{CHANNEL}</a></h3>
            """
    except Exception as e:
        return f"<h3>Ошибка проверки подписки: {e}</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
