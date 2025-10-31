from flask import Flask, request, send_from_directory, jsonify
import telebot
import sqlite3
import os
import random
import time
from datetime import date

# ====== CONFIG ======
TOKEN = os.environ.get("BOT_TOKEN")  # Railway Variables’da BOT_TOKEN sifatida qo‘shasiz
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://notcoin-production.up.railway.app")  # Railway domening

MAX_ENERGY = 10
ENERGY_REGEN_SECONDS = 300
MIN_CLICK_REWARD = 1
MAX_CLICK_REWARD = 5
DAILY_BONUS_COINS = 50

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ====== DATABASE ======
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    energy INTEGER DEFAULT 10,
    last_energy_ts INTEGER DEFAULT 0,
    last_daily TEXT DEFAULT NULL
)
""")
conn.commit()

def ensure_user(uid):
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, coins, energy, last_energy_ts) VALUES (?, ?, ?, ?)",
                       (uid, 0, MAX_ENERGY, int(time.time())))
        conn.commit()

def get_user(uid):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    row = cursor.fetchone()
    if not row:
        return None
    return {"user_id": row[0], "coins": row[1], "energy": row[2], "last_energy_ts": row[3], "last_daily": row[4]}

def regen_energy(user):
    now = int(time.time())
    elapsed = now - user["last_energy_ts"]
    gained = elapsed // ENERGY_REGEN_SECONDS
    if gained > 0:
        new_energy = min(MAX_ENERGY, user["energy"] + gained)
        cursor.execute("UPDATE users SET energy = ?, last_energy_ts = ? WHERE user_id = ?",
                       (new_energy, now, user["user_id"]))
        conn.commit()

# ====== TELEGRAM HANDLERS ======
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    ensure_user(uid)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🎮 O‘yin", web_app=telebot.types.WebAppInfo(WEBAPP_URL)))
    bot.send_message(uid, "Salom! Coin yig‘ishni boshlang 💰", reply_markup=markup)

# ====== FLASK API ======
@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('web', path)

@app.route('/add_coin', methods=['POST'])
def add_coin():
    data = request.json
    uid = data.get("user_id")
    ensure_user(uid)
    user = get_user(uid)
    regen_energy(user)
    user = get_user(uid)

    if user['energy'] <= 0:
        return jsonify({"error": "no_energy"}), 403

    new_energy = user['energy'] - 1
    added = random.randint(MIN_CLICK_REWARD, MAX_CLICK_REWARD)
    cursor.execute("UPDATE users SET energy = ?, coins = coins + ?, last_energy_ts = ? WHERE user_id = ?",
                   (new_energy, added, int(time.time()), uid))
    conn.commit()
    user = get_user(uid)
    return jsonify({"coins": user["coins"], "energy": user["energy"], "added": added})

@app.route('/daily_bonus', methods=['POST'])
def daily_bonus():
    data = request.json
    uid = data.get("user_id")
    ensure_user(uid)
    user = get_user(uid)
    today = date.today().isoformat()
    if user["last_daily"] == today:
        return jsonify({"error": "already_claimed"}), 403
    cursor.execute("UPDATE users SET coins = coins + ?, last_daily = ? WHERE user_id = ?",
                   (DAILY_BONUS_COINS, today, uid))
    conn.commit()
    return jsonify({"bonus": DAILY_BONUS_COINS})

# ====== TELEGRAM WEBHOOK ======
@app.route("/" + TOKEN, methods=['POST'])
def webhook_update():
    json_str = request.stream.read().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/setwebhook")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBAPP_URL}/{TOKEN}")
    return "Webhook set successfully!", 200

# ====== RUN APP ======

