# bot_mail_tm.py
import os
import json
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================== CONFIG ==================
TOKEN = "7847516394:AAEy-AtqfWURynEI76PtwqN0-ByrKPdfo3g"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "emails.json")
API_BASE = "https://api.mail.tm"

logging.basicConfig(level=logging.INFO)

# ================== FUNCIONES DE ARCHIVO ==================
def cargar_emails():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def guardar_emails(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ================== FUNCIONES DE CORREO ==================
def generar_nombre_usuario():
    nombres = ["user", "test", "bot", "mail", "temp"]
    return random.choice(nombres) + str(random.randint(1000, 9999))

def obtener_dominios():
    try:
        resp = requests.get(f"{API_BASE}/domains?page=1")
        if resp.status_code == 200:
            return resp.json()["hydra:member"]
    except Exception:
        return []
    return []

def crear_email_custom(usuario, dominio):
    try:
        payload = {"address": f"{usuario}@{dominio}", "password": "123456"}
        resp = requests.post(f"{API_BASE}/accounts", json=payload)
        if resp.status_code == 201:
            return payload["address"]
        elif resp.status_code == 422:
            return None  # ya existe
    except Exception:
        return None
    return None

def obtener_mensajes(address, password="123456"):
    try:
        login = requests.post(f"{API_BASE}/token", json={"address": address, "password": password})
        if login.status_code != 200:
            return []
        token = login.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_BASE}/messages", headers=headers)
        if resp.status_code == 200:
            return resp.json()["hydra:member"]
    except Exception:
        return []
    return []

# ================== HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botones = [
        [InlineKeyboardButton("📩 Crear correo", callback_data="crear_correo")],
        [InlineKeyboardButton("📬 Mis correos", callback_data="mis_correos")],
        [InlineKeyboardButton("📥 Ver bandeja", callback_data="ver_bandeja")]
    ]
    await update.message.reply_text("👋 Bienvenido a tu bot de correos temporales", 
                                    reply_markup=InlineKeyboardMarkup(botones))

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Este bot genera correos temporales usando mail.tm")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(query.from_user.id)

    emails = cargar_emails()

    # Crear correo
    if data == "crear_correo":
        dominios = obtener_dominios()
        if not dominios:
            await query.message.reply_text("❌ No se pudieron obtener dominios.")
            return
        dom = random.choice(dominios)["domain"]
        usuario = generar_nombre_usuario()
        email = crear_email_custom(usuario, dom)
        if email:
            emails[user_id] = {"address": email, "password": "123456"}
            guardar_emails(emails)
            await query.message.reply_text(f"✅ Correo creado: `{email}`", parse_mode="Markdown")
        else:
            await query.message.reply_text("⚠️ Ese correo ya existe, intenta de nuevo.")

    # Mis correos
    elif data == "mis_correos":
        if user_id not in emails:
            await query.message.reply_text("📭 Aún no tienes correos creados.")
        else:
            correo = emails[user_id]["address"]
            await query.message.reply_text(f"📩 Tu correo actual es: `{correo}`", parse_mode="Markdown")

    # Ver bandeja
    elif data == "ver_bandeja":
        if user_id not in emails:
            await query.message.reply_text("📭 Aún no tienes correos creados.")
            return
        correo = emails[user_id]["address"]
        mensajes = obtener_mensajes(correo)
        if not mensajes:
            await query.message.reply_text("📭 No tienes mensajes nuevos en la bandeja.")
        else:
            texto = "📥 **Bandeja de entrada:**\n\n"
            for m in mensajes[:5]:
                texto += f"🔹 *De:* {m.get('from', {}).get('address','?')}\n"
                texto += f"   *Asunto:* {m.get('subject','(sin asunto)')}\n\n"
            await query.message.reply_text(texto, parse_mode="Markdown")

# ================== MAIN ==================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("✅ Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
