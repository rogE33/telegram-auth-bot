# telegram_auth.py
import os
import time
import hmac
import hashlib
import urllib.parse
from flask import Flask, request, redirect, render_template_string
import telebot

# ====== Настройки ======
BOT_TOKEN = "7996753569:AAFu1k4_ybkkpFj2183oNE0ITSt6ayuTezc"
CHANNEL = "@SchoolAwards"
RENDER_BASE_URL = "https://schoolawars-auth.onrender.com"  # ← сюда вставь свой Render-домен
# ========================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# HTML-страница авторизации
START_HTML = """
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Авторизация через Telegram</title>
<style>
.center { display:flex; align-items:center; justify-content:center; height:100vh; }
.card { text-align:center; padding:20px; border-radius:8px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.small { color:#666; font-size:14px; margin-top:8px; }
</style>
</head>
<body>
<div class="center">
  <div class="card">
    <h2>Авторизация через Telegram</h2>
    <div id="telegram-login-widget"></div>
    <div class="small">После входа вы попадёте на нужную страницу, если подписаны на канал.</div>
  </div>
</div>

<script async src="https://telegram.org/js/telegram-widget.js?22"
    data-telegram-login="{{bot_username}}"
    data-size="large"
    data-userpic="false"
    data-auth-url="{{auth_url}}"
    data-request-access="write">
</script>
</body>
</html>
"""

# Проверка подписи Telegram
def verify_telegram_auth(data: dict) -> bool:
    if "hash" not in data:
        return False
    received_hash = data["hash"]
    check_list = [f"{k}={data[k]}" for k in sorted(data.keys()) if k != "hash"]
    check_string = "\n".join(check_list)
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    hmac_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return hmac_hash == received_hash

# --- /start_auth ---
@app.route("/start_auth", methods=["GET"])
def start_auth():
    next_url = request.args.get("next", "https://a1183826.xsph.ru/")
    auth_url = f"{RENDER_BASE_URL}/auth?next={urllib.parse.quote_plus(next_url)}"
    try:
        me = bot.get_me()
        bot_username = me.username
    except Exception:
        bot_username = "SchoolAwards_bot"
    return render_template_string(START_HTML, auth_url=auth_url, bot_username=bot_username)

# --- /auth ---
@app.route("/auth", methods=["GET"])
def auth():
    data = request.args.to_dict(flat=True)
    next_url = request.args.get("next", "https://a1183826.xsph.ru/")

    if not verify_telegram_auth(data):
        return "<h3>Ошибка проверки подписи Telegram.</h3>", 400

    auth_date = int(data.get("auth_date", "0") or 0)
    if auth_date and time.time() - auth_date > 300:
        return "<h3>Сессия устарела. Пожалуйста, попробуйте снова.</h3>", 400

    user_id = int(data.get("id"))
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        status = getattr(member, "status", None)

        if status in ("member", "administrator", "creator"):
            return redirect(next_url, code=302)
        else:
            chan = CHANNEL.lstrip("@")
            return f"""
            <h3>Доступ запрещён — нужно быть подписанным на канал @{chan}</h3>
            <p><a href="https://t.me/{chan}" target="_blank">Перейти на канал</a></p>
            <p>После подписки вернитесь и повторите авторизацию.</p>
            """, 403

    except Exception as e:
        return f"<h3>Ошибка при проверке подписки: {e}</h3>", 500

# --- Запуск ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
