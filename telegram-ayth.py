from flask import Flask, request, redirect
import hashlib, hmac
from aiogram import Bot
import asyncio

app = Flask(__name__)

# Твой токен от BotFather
TOKEN = "7996753569:AAFu1k4_ybkkpFj2183oNE0ITSt6ayuTezc"
CHANNEL = "@SchoolAwards"

bot = Bot(token=TOKEN)

def check_hash(data):
    auth_data = dict(data)
    received_hash = auth_data.pop('hash')
    check_string = '\n'.join([f"{k}={v}" for k, v in sorted(auth_data.items())])
    secret_key = hashlib.sha256(TOKEN.encode()).digest()
    h = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return h == received_hash

@app.route("/telegram-auth")
def auth():
    data = request.args
    if not check_hash(data):
        return "Ошибка проверки подписи."

    user_id = int(data.get("id"))
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        member = loop.run_until_complete(bot.get_chat_member(CHANNEL, user_id))
        if member.status in ("member", "administrator", "creator"):
            return f"✅ Добро пожаловать, {data.get('first_name')}!"
        else:
            return redirect("https://t.me/SchoolAwards")
    except Exception as e:
        return f"Ошибка проверки подписки: {e}"

if name == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
