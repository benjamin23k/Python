# bot_mail_tm.py
import os
import json
import uuid
import logging
import requests
from typing import Dict, Any, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes, CallbackQueryHandler,
    MessageHandler, filters
)

# ------------- CONFIG -------------
TOKEN = "7847516394:AAEy-AtqfWURynEI76PtwqN0-ByrKPdfo3g"  
API_BASE = "https://api.mail.tm"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "emails.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# Estructuras en memoria
# user_emails: { user_id:int : [ {email, password, token, active:bool, alias:str, last_id:str|None}, ... ] }
# user_settings: { user_id:int : { "preferred_domain": str|None } }
user_emails: Dict[int, List[Dict[str, Any]]] = {}
user_settings: Dict[int, Dict[str, Any]] = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mailtm-bot")

# ------------- UTIL PERSISTENCIA -------------
def _keys_to_str(d: dict) -> dict:
    return {str(k): v for k, v in d.items()}

def _keys_to_int(d: dict) -> dict:
    out = {}
    for k, v in d.items():
        try:
            out[int(k)] = v
        except Exception:
            pass
    return out

def guardar_datos() -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(_keys_to_str(user_emails), f, ensure_ascii=False, indent=2)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(_keys_to_str(user_settings), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception("Error guardando datos: %s", e)

def cargar_datos() -> None:
    global user_emails, user_settings
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                user_emails = _keys_to_int(json.load(f))
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                user_settings = _keys_to_int(json.load(f))
    except Exception as e:
        logger.exception("Error cargando datos: %s", e)

# ------------- MENÚS -------------
def menu_principal() -> InlineKeyboardMarkup:
    botones = [
        [InlineKeyboardButton("📧 Generar aleatorio", callback_data="generar_cuenta"),
         InlineKeyboardButton("✍️ Crear correo custom", callback_data="crear_custom")],
        [InlineKeyboardButton("🌐 Elegir dominio", callback_data="elegir_dominio"),
         InlineKeyboardButton("📥 Ver bandeja", callback_data="ver_bandeja")],
        [InlineKeyboardButton("✉️ Seleccionar correo", callback_data="seleccionar_correo"),
         InlineKeyboardButton("🏷️ Renombrar", callback_data="renombrar_correo")],
        [InlineKeyboardButton("🗑️ Eliminar correo", callback_data="eliminar_correo"),
         InlineKeyboardButton("📊 Mis correos", callback_data="listar_correos")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="info")]
    ]
    return InlineKeyboardMarkup(botones)

def menu_volver() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al menú", callback_data="menu")]])

# ------------- HELPERS -------------
def _sanear_username(u: str) -> str:
    u = u.strip().lower()
    permitido = "abcdefghijklmnopqrstuvwxyz0123456789._-"
    return "".join(ch for ch in u if ch in permitido)

def obtener_dominio_para(user_id: int) -> str:
    preferred = user_settings.get(user_id, {}).get("preferred_domain")
    try:
        r = requests.get(f"{API_BASE}/domains", timeout=15)
        r.raise_for_status()
        domains = r.json().get("hydra:member", [])
        if not domains:
            raise RuntimeError("Sin dominios disponibles")
        if preferred and any(d.get("domain") == preferred for d in domains):
            return preferred
        return domains[0]["domain"]
    except Exception:
        # Fallback conocido de mail.tm
        return "tmpmail.org"

def _get_active_email(user_id: int) -> Dict[str, Any] | None:
    for e in user_emails.get(user_id, []):
        if e.get("active"):
            return e
    return None

# ------------- COMANDOS -------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot de *correos temporales* (Mail.tm).\n"
        "Puedes generar correos aleatorios o *custom*, elegir dominio, ver bandeja, renombrar y más.\n",
        parse_mode="Markdown",
        reply_markup=menu_principal(),
    )

async def info_from_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await _send_info(q.message.reply_text, q.from_user.id)

async def info_from_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_info(update.message.reply_text, update.effective_user.id)

async def _send_info(send, user_id: int):
    correos_user = user_emails.get(user_id, [])
    activos = [e for e in correos_user if e.get("active")]
    activo = activos[0] if activos else None
    label_activo = (activo.get("alias") or activo["email"]) if activo else "—"
    preferred = user_settings.get(user_id, {}).get("preferred_domain") or "auto"

    await send(
        "ℹ️ *Información de tu sesión:*\n"
        f"• Correos totales: *{len(correos_user)}*\n"
        f"• Correo activo: `{label_activo}`\n"
        f"• Dominio preferido: *{preferred}*\n"
        "• Notificaciones: *ON* (revisión cada 2 min)\n"
        "• Persistencia: *ON* (emails.json, settings.json)\n",
        parse_mode="Markdown",
        reply_markup=menu_volver()
    )

# ------------- CREAR CUENTAS -------------
async def nuevo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        send = update.message.reply_text
        user_id = update.effective_user.id
    else:
        send = update.callback_query.message.reply_text
        user_id = update.callback_query.from_user.id
        await update.callback_query.answer()

    try:
        domain = obtener_dominio_para(user_id)
        username = str(uuid.uuid4())[:8]
        password = str(uuid.uuid4())
        email = f"{username}@{domain}"

        payload = {"address": email, "password": password}
        r = requests.post(f"{API_BASE}/accounts", json=payload, timeout=20)
        if r.status_code != 201:
            await send(f"❌ Error creando correo temporal: {r.text}", reply_markup=menu_volver())
            return

        login = requests.post(f"{API_BASE}/token", json=payload, timeout=20).json()
        token = login.get("token")
        if not token:
            await send("❌ No se pudo obtener el token de acceso.", reply_markup=menu_volver())
            return

        if user_id not in user_emails:
            user_emails[user_id] = []
        # Desactivar todos
        for e in user_emails[user_id]:
            e["active"] = False

        user_emails[user_id].append({
            "email": email,
            "password": password,
            "token": token,
            "active": True,
            "alias": "",
            "last_id": None
        })
        guardar_datos()

        await send(
            f"📧 Nuevo correo creado:\n`{email}`\n🔑 `{password}`",
            parse_mode="Markdown",
            reply_markup=menu_volver()
        )
    except Exception as e:
        logger.exception("Error creando cuenta: %s", e)
        await send(f"⚠️ Error: {e}", reply_markup=menu_volver())

async def crear_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["awaiting_custom_name"] = True
    await q.message.reply_text(
        "✍️ Escribe el *nombre* para tu correo (antes de la @). Ej.: `miusuario`",
        parse_mode="Markdown"
    )

async def crear_custom_desde_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    # Router de texto (flags)
    if context.user_data.get("awaiting_custom_name"):
        context.user_data["awaiting_custom_name"] = False
        username = _sanear_username(text)
        if not username:
            await update.message.reply_text("❌ Nombre inválido. Usa letras/números/._-")
            return
        try:
            domain = obtener_dominio_para(user_id)
            email = f"{username}@{domain}"
            password = str(uuid.uuid4())

            payload = {"address": email, "password": password}
            r = requests.post(f"{API_BASE}/accounts", json=payload, timeout=20)
            if r.status_code != 201:
                await update.message.reply_text(f"❌ No se pudo crear el correo: {r.text}")
                return

            login = requests.post(f"{API_BASE}/token", json=payload, timeout=20).json()
            token = login.get("token")
            if not token:
                await update.message.reply_text("❌ No se pudo obtener el token de acceso.")
                return

            if user_id not in user_emails:
                user_emails[user_id] = []
            for e in user_emails[user_id]:
                e["active"] = False
            user_emails[user_id].append({
                "email": email, "password": password, "token": token,
                "active": True, "alias": "", "last_id": None
            })
            guardar_datos()

            await update.message.reply_text(
                f"✅ Correo *custom* creado:\n`{email}`\n🔑 `{password}`",
                parse_mode="Markdown",
                reply_markup=menu_volver()
            )
        except Exception as e:
            logger.exception("Error custom: %s", e)
            await update.message.reply_text(f"⚠️ Error: {e}", reply_markup=menu_volver())
        return

    if "renaming_idx" in context.user_data:
        idx = context.user_data.pop("renaming_idx")
        try:
            correo = user_emails[user_id][idx]
            correo["alias"] = text.strip()
            guardar_datos()
            await update.message.reply_text("✅ Alias actualizado.", reply_markup=menu_volver())
        except Exception:
            await update.message.reply_text("❌ No se pudo renombrar.", reply_markup=menu_volver())
        return

    # Si llegó texto sin estar en modo especial, mostramos ayuda rápida
    await update.message.reply_text(
        "Escribe /start para abrir el menú o usa los botones.",
        reply_markup=menu_principal()
    )

# ------------- BANDEJA / LISTADOS -------------
async def ver_bandeja(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    correos_user = user_emails.get(user_id, [])
    if not correos_user:
        await q.message.reply_text("❌ Aún no tienes correos creados.", reply_markup=menu_volver())
        return

    activo = _get_active_email(user_id)
    if not activo:
        await q.message.reply_text("❌ No tienes un correo activo seleccionado.", reply_markup=menu_volver())
        return

    try:
        headers = {"Authorization": f"Bearer {activo['token']}"}
        r = requests.get(f"{API_BASE}/messages", headers=headers, timeout=20)
        r.raise_for_status()
        mensajes = r.json().get("hydra:member", [])
        if not mensajes:
            await q.message.reply_text("📬 No tienes mensajes nuevos.", reply_markup=menu_volver())
            return

        # Mostramos hasta 10 últimos
        salida = [f"📬 *Bandeja de* `{activo.get('alias') or activo['email']}`:\n"]
        for msg in mensajes[:10]:
            from_address = msg.get("from", {}).get("address", "Desconocido")
            subject = msg.get("subject") or "(Sin asunto)"
            salida.append(f"• 👤 {from_address}\n  ✉️ {subject}\n")
        await q.message.reply_text("\n".join(salida), parse_mode="Markdown", reply_markup=menu_volver())
    except Exception as e:
        logger.exception("Error bandeja: %s", e)
        await q.message.reply_text(f"⚠️ Error al obtener la bandeja: {e}", reply_markup=menu_volver())

async def listar_correos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    correos_user = user_emails.get(user_id, [])
    if not correos_user:
        await q.message.reply_text("❌ Aún no tienes correos creados.", reply_markup=menu_volver())
        return

    msg = ["📧 *Tus correos:*"]
    for i, e in enumerate(correos_user, start=1):
        alias = f" ({e['alias']})" if e.get("alias") else ""
        activo = "✅" if e.get("active") else "⚪"
        msg.append(f"{activo} {i}. `{e['email']}`{alias}")
    await q.message.reply_text("\n".join(msg), parse_mode="Markdown", reply_markup=menu_volver())

# ------------- CALLBACKS -------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    data = q.data

    try:
        if data == "menu":
            await q.message.reply_text("📋 Menú principal:", reply_markup=menu_principal())

        elif data == "info":
            await _send_info(q.message.reply_text, user_id)

        elif data == "generar_cuenta":
            await nuevo(update, context)

        elif data == "crear_custom":
            await crear_custom(update, context)

        elif data == "elegir_dominio":
            try:
                r = requests.get(f"{API_BASE}/domains", timeout=15)
                r.raise_for_status()
                domains = r.json().get("hydra:member", [])
                if not domains:
                    await q.message.reply_text("❌ No hay dominios disponibles.", reply_markup=menu_volver())
                else:
                    buttons = [[InlineKeyboardButton(d["domain"], callback_data=f"set_domain_{d['domain']}")]
                               for d in domains]
                    await q.message.reply_text("Selecciona un dominio:", reply_markup=InlineKeyboardMarkup(buttons))
            except Exception:
                await q.message.reply_text("❌ No se pudieron obtener los dominios.", reply_markup=menu_volver())

        elif data.startswith("set_domain_"):
            domain = data.removeprefix("set_domain_")
            if user_id not in user_settings:
                user_settings[user_id] = {}
            user_settings[user_id]["preferred_domain"] = domain
            guardar_datos()
            await q.message.reply_text(f"✅ Dominio *{domain}* elegido exitosamente.", parse_mode="Markdown",
                                       reply_markup=menu_volver())

        elif data == "seleccionar_correo":
            correos_user = user_emails.get(user_id, [])
            if not correos_user:
                await q.message.reply_text("❌ No tienes correos creados aún.", reply_markup=menu_volver())
                return
            buttons = [[InlineKeyboardButton(
                f"{('[ACTIVO] ' if c.get('active') else '')}{c.get('alias') or c['email']}",
                callback_data=f"set_active_{idx}")]
                for idx, c in enumerate(correos_user)]
            await q.message.reply_text("Selecciona el correo activo:", reply_markup=InlineKeyboardMarkup(buttons))

        elif data.startswith("set_active_"):
            idx = int(data.split("_")[-1])
            correos_user = user_emails.get(user_id, [])
            if 0 <= idx < len(correos_user):
                for i, e in enumerate(correos_user):
                    e["active"] = (i == idx)
                guardar_datos()
                label = correos_user[idx].get("alias") or correos_user[idx]["email"]
                pwd = correos_user[idx]["password"]
                await q.message.reply_text(
                    f"✅ Correo activo cambiado a:\n📧 `{label}`\n🔑 `{pwd}`",
                    parse_mode="Markdown",
                    reply_markup=menu_volver()
                )
            else:
                await q.message.reply_text("❌ Índice inválido.", reply_markup=menu_volver())

        elif data == "renombrar_correo":
            correos_user = user_emails.get(user_id, [])
            if not correos_user:
                await q.message.reply_text("❌ No tienes correos creados.", reply_markup=menu_volver())
                return
            buttons = [[InlineKeyboardButton(
                f"{c.get('alias') or c['email']}", callback_data=f"rename_idx_{i}")]
                for i, c in enumerate(correos_user)]
            await q.message.reply_text("¿Cuál quieres renombrar?", reply_markup=InlineKeyboardMarkup(buttons))

        elif data.startswith("rename_idx_"):
            idx = int(data.split("_")[-1])
            if user_id not in user_emails or idx >= len(user_emails[user_id]):
                await q.message.reply_text("❌ Selección inválida.", reply_markup=menu_volver())
                return
            context.user_data["renaming_idx"] = idx
            await q.message.reply_text("✍️ Escribe el *nuevo alias* para ese correo.", parse_mode="Markdown")

        elif data == "eliminar_correo":
            correos_user = user_emails.get(user_id, [])
            if not correos_user:
                await q.message.reply_text("❌ No tienes correos creados.", reply_markup=menu_volver())
                return
            buttons = [[InlineKeyboardButton(
                f"🗑️ {c.get('alias') or c['email']}", callback_data=f"del_yes_{i}")]
                for i, c in enumerate(correos_user)]
            buttons.append([InlineKeyboardButton("Cancelar", callback_data="del_no")])
            await q.message.reply_text("Selecciona el correo a eliminar:", reply_markup=InlineKeyboardMarkup(buttons))

        elif data.startswith("del_yes_"):
            idx = int(data.split("_")[-1])
            correos_user = user_emails.get(user_id, [])
            if 0 <= idx < len(correos_user):
                eliminado = correos_user.pop(idx)
                # si eliminamos el activo, dejamos el primero (si existe) como activo
                if eliminado.get("active") and correos_user:
                    correos_user[0]["active"] = True
                guardar_datos()
                await q.message.reply_text(
                    f"🗑️ Correo `{eliminado['email']}` eliminado.",
                    parse_mode="Markdown",
                    reply_markup=menu_volver()
                )
            else:
                await q.message.reply_text("❌ Índice inválido.", reply_markup=menu_volver())

        elif data == "del_no":
            await q.message.reply_text("Eliminación cancelada.", reply_markup=menu_volver())

        elif data == "ver_bandeja":
            await ver_bandeja(update, context)

        elif data == "listar_correos":
            await listar_correos(update, context)

        else:
            await q.message.reply_text("Acción no reconocida.", reply_markup=menu_volver())

    except Exception as e:
        logger.exception("Error en callback: %s", e)
        await q.message.reply_text("⚠️ Ocurrió un error procesando tu acción.", reply_markup=menu_volver())

# ------------- NOTIFICACIONES (cada 2 min) -------------
async def check_inbox_job(context: ContextTypes.DEFAULT_TYPE):
    # Revisa nuevos mensajes y notifica
    try:
        for user_id, lista in list(user_emails.items()):
            for e in lista:
                if not e.get("active"):
                    continue
                try:
                    headers = {"Authorization": f"Bearer {e['token']}"}
                    r = requests.get(f"{API_BASE}/messages", headers=headers, timeout=20)
                    mensajes = r.json().get("hydra:member", [])
                    if mensajes:
                        ultimo = mensajes[0]
                        ultimo_id = ultimo.get("id")
                        if ultimo_id and ultimo_id != e.get("last_id"):
                            # Primera vez: si last_id es None, solo marcamos, no spameamos
                            if e.get("last_id") is not None:
                                from_address = ultimo.get("from", {}).get("address", "¿?")
                                subject = ultimo.get("subject") or "(Sin asunto)"
                                await context.bot.send_message(
                                    chat_id=user_id,
                                    text=f"📬 Nuevo correo en *{e.get('alias') or e['email']}*\n"
                                         f"👤 {from_address}\n"
                                         f"✉️ {subject}",
                                    parse_mode="Markdown"
                                )
                            e["last_id"] = ultimo_id
                            guardar_datos()
                except Exception:
                    continue
    except Exception as e:
        logger.exception("Error en job de revisión: %s", e)

# ------------- ERRORES GLOBALES -------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Excepción no controlada", exc_info=context.error)
    try:
        if isinstance(update, Update) and update.effective_chat:
            await context.bot.send_message(update.effective_chat.id, "⚠️ Ocurrió un error inesperado. Intenta de nuevo.")
    except Exception:
        pass

# ------------- MAIN -------------
def main():
    cargar_datos()
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info_from_cmd))

    # Buttons / callbacks
    app.add_handler(CallbackQueryHandler(button_callback))

    # Mensajes de texto: router para custom/rename
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, crear_custom_desde_texto))

    # Job de notificaciones cada 2 min
    app.job_queue.run_repeating(check_inbox_job, interval=120, first=10)

    # Error global
    app.add_error_handler(error_handler)

    print("✅ Bot en ejecución…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
