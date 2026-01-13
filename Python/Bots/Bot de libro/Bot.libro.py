import requests
import sqlite3
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
)
import google.generativeai as genai
from telegram.helpers import escape_markdown
import re

# ===== CONFIG =====
TOKEN = "8341820198:AAHUjnzM7nekvYdQjr74mSnHfFMUAgRfrcM"
GEMINI_API_KEY = "AIzaSyAG5rGKgFZ36DiVIa_e7OJ6Vp9h-IzzmjA"
genai.configure(api_key=GEMINI_API_KEY)

# ===== BASE DE DATOS (solo usuarios, opcional) =====
conn = sqlite3.connect("biblioteca_cultural.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()

def registrar_usuario(user_id):
    cursor.execute("INSERT OR IGNORE INTO usuarios(user_id) VALUES (?)", (user_id,))
    conn.commit()

# ===== FUNCIONES MULTIFUENTE =====
def buscar_openlibrary(query, limite=5):
    r = requests.get(f"https://openlibrary.org/search.json?q={query}&limit={limite}").json()
    return r.get("docs", [])

def buscar_gutenberg(query, limite=5):
    r = requests.get(f"https://gutendex.com/books?search={query}").json()
    return r.get("results", [])[:limite]

def buscar_googlebooks(query, limite=3):
    r = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={limite}").json()
    return r.get("items", [])

def buscar_libros_multifuente(query, limite_total=10):
    resultados = []
    titulos_vistos = set()

    for libro in buscar_openlibrary(query, limite=5):
        titulo = libro.get("title")
        if not titulo or titulo in titulos_vistos: continue
        titulos_vistos.add(titulo)
        resultados.append({
            "titulo": titulo,
            "autor": ", ".join(libro.get("author_name", ["Desconocido"])),
            "portada": f"http://covers.openlibrary.org/b/id/{libro['cover_i']}-L.jpg" if "cover_i" in libro else None,
            "sinopsis": libro.get("first_sentence", ["Sinopsis no disponible"])[0],
            "enlace": f"https://openlibrary.org{libro['key']}"
        })
        if len(resultados) >= limite_total: return resultados

    for libro in buscar_gutenberg(query, limite=5):
        titulo = libro.get("title")
        if not titulo or titulo in titulos_vistos: continue
        titulos_vistos.add(titulo)
        formatos = libro.get("formats", {})
        resultados.append({
            "titulo": titulo,
            "autor": ", ".join([a.get("name","") for a in libro.get("authors",[])]),
            "portada": formatos.get("image/jpeg"),
            "sinopsis": "Clásico dominio público (Project Gutenberg).",
            "enlace": f"https://www.gutenberg.org/ebooks/{libro['id']}"
        })
        if len(resultados) >= limite_total: return resultados

    for libro in buscar_googlebooks(query, limite=3):
        vol = libro.get("volumeInfo", {})
        titulo = vol.get("title")
        if not titulo or titulo in titulos_vistos: continue
        titulos_vistos.add(titulo)
        resultados.append({
            "titulo": titulo,
            "autor": ", ".join(vol.get("authors", [])) if "authors" in vol else "Desconocido",
            "portada": vol.get("imageLinks", {}).get("thumbnail"),
            "sinopsis": vol.get("description", "Sinopsis no disponible")[:400],
            "enlace": vol.get("previewLink", "")
        })
        if len(resultados) >= limite_total: return resultados

    return resultados

# ===== GEMINI AI =====
def validar_entrada(texto):
    return bool(re.match(r'^[\w\sáéíóúÁÉÍÓÚñÑ]+$', texto))

def generar_recomendacion_ai(prompt_usuario):
    if not validar_entrada(prompt_usuario):
        return "No se pudo generar recomendación."
    try:
        modelo = genai.GenerativeModel("gemini-pro")
        prompt = f"Eres un asistente que recomienda libros. Usuario dice: {prompt_usuario}. Responde solo con un género o tema corto."
        respuesta = modelo.generate_content(prompt)
        return respuesta.text.strip()
    except Exception:
        return "Error generando la recomendación."

# ===== MOSTRAR LIBRO =====
async def mostrar_libro(update: Update, context: ContextTypes.DEFAULT_TYPE, indice):
    resultados = context.user_data.get("resultados_libros", [])
    if indice >= len(resultados) or indice < 0:
        await update.message.reply_text("✅ Has llegado al final o inicio de los resultados.")
        return

    context.user_data["indice_libro"] = indice
    libro = resultados[indice]

    # Botones principales del libro
    botones = [[InlineKeyboardButton("📖 Leer online", url=libro.get("enlace", "#"))],
               [InlineKeyboardButton("🔄 Buscar otro libro", callback_data="buscar")]]  # <-- agregado

    # Botones de navegación entre libros
    nav_botones = []
    if indice > 0:
        nav_botones.append(InlineKeyboardButton("⬅️ Libro anterior", callback_data="anterior_libro"))
    if indice + 1 < len(resultados):
        nav_botones.append(InlineKeyboardButton("➡️ Siguiente libro", callback_data="siguiente_libro"))
    if nav_botones:
        botones.append(nav_botones)

    teclado = InlineKeyboardMarkup(botones)
    titulo = escape_markdown(libro.get("titulo", "Sin título"), version=2)
    autor = escape_markdown(libro.get("autor", "Desconocido"), version=2)
    sinopsis = escape_markdown(libro.get("sinopsis", "Sinopsis no disponible"), version=2)

    caption = f"*{titulo}*\n👤 {autor}\n📖 {sinopsis}"

    if update.callback_query:
        if libro.get("portada"):
            await update.callback_query.message.edit_media(
                media=InputMediaPhoto(media=libro["portada"], caption=caption),
                reply_markup=teclado
            )
        else:
            await update.callback_query.message.edit_caption(
                caption=caption,
                parse_mode="MarkdownV2",
                reply_markup=teclado
            )
    else:
        if libro.get("portada"):
            await update.message.reply_photo(photo=libro["portada"], caption=caption, parse_mode="MarkdownV2", reply_markup=teclado)
        else:
            await update.message.reply_text(caption, parse_mode="MarkdownV2", reply_markup=teclado)


# ===== MENSAJES DE USUARIO =====
async def mensaje_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    if not texto:
        await update.message.reply_text("❌ No escribiste ningún texto.")
        return

    modo = context.user_data.get("modo")
    try:
        if modo == "buscar":
            resultados = buscar_libros_multifuente(texto)
        elif modo == "recomendar":
            tema = generar_recomendacion_ai(texto)
            resultados = buscar_libros_multifuente(tema)
        else:
            resultados = buscar_libros_multifuente(texto)
    except Exception as e:
        await update.message.reply_text("❌ Ocurrió un error al buscar libros.")
        print("Error:", e)
        return

    if not resultados:
        await update.message.reply_text("❌ No encontré libros para eso.")
        return

    context.user_data["resultados_libros"] = resultados
    await mostrar_libro(update, context, 0)

# ===== CALLBACK =====
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    resultados = context.user_data.get("resultados_libros", [])
    indice = context.user_data.get("indice_libro", 0)

    if data == "siguiente_libro":
        if indice + 1 < len(resultados):
            await mostrar_libro(update, context, indice + 1)
        else:
            await query.message.reply_text("✅ Has llegado al final de los resultados.")
    elif data == "anterior_libro":
        if indice - 1 >= 0:
            await mostrar_libro(update, context, indice - 1)
        else:
            await query.message.reply_text("✅ Estás en el primer libro.")
    elif data == "buscar":
        # Cambiamos el modo para que el siguiente mensaje del usuario inicie una nueva búsqueda
        context.user_data["modo"] = "buscar"
        await query.message.reply_text("✏️ Escribe el título o tema que deseas buscar:")
# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    registrar_usuario(user_id)
    botones = [
        [InlineKeyboardButton("🔎 Buscar libro", callback_data="buscar")],
        [InlineKeyboardButton("✨ Recomendación personalizada", callback_data="recomendar")]
    ]
    await update.message.reply_text(
        escape_markdown("📚 Bienvenido a tu *Biblioteca de Libros*.\nSelecciona una opción 👇", version=2),
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup(botones)
    )

# ===== MAIN =====
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_usuario))
    print("🤖 Bot en ejecución...")
    app.run_polling()

if __name__ == "__main__":
    main()
