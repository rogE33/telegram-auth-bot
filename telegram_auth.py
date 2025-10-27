from flask import Flask, request, redirect, render_template_string
import requests
import hmac
import hashlib
import time
import os

TOKEN = "7996753569:AAFu1k4_ybkkpFj2183oNE0ITSt6ayuTezc"
CHANNEL_ID = "@SchoolAwards"
REDIRECT_URL = "http://a1183826.xsph.ru/?p=111"

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Авторизация Telegram</title>
    <style>
        body {
            font-family: Arial;
            text-align: center;
            background-color: #fff;
            margin-top: 15%;
        }
        button {
            background-color: white;
            color: black;
            border: 2px solid #B39298;
            padding: 12px 30px;
            border-radius: 30px;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            background-color: #B39298;
            color: white;
        }
    </style>
</head>
<body>
    <h2>Авторизация через Telegram</h2>
    <script async src="https://telegram.org/js/telegram-widget.js?7"
        data-telegram-login="SchoolAwards_bot"
        data-size="large"
        data-userpic="false"
        data-auth-url="https://schoolawards-auth.onrender.com/auth"
        data-request-access="write">
    </script>
</body>
</html>
"""

def check_signature(data_dict, token):
    auth_data = {k: v for k, v in data_dict.items() if k != 'hash'}
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(auth_data.items())])
    secret_key = hashlib.sha256(token.encode()).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return h == data_dict.get('hash')

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/auth')
def auth():
    data = request.args.to_dict()
    if not check_signature(data, TOKEN):
        return "Ошибка проверки подписи Telegram."

    user_id = data.get('id')
    status = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/getChatMember",
        params={"chat_id": CHANNEL_ID, "user_id": user_id}
    ).json()

    if status.get("ok"):
        member_status = status["result"]["status"]
        if member_status in ("member", "administrator", "creator"):
            return redirect(REDIRECT_URL)
        else:
            return "❌ Вы не подписаны на канал @SchoolAwards."
    else:
        return "Не удалось получить данные о подписке."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
