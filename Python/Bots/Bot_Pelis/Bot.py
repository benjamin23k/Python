import logging
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🚨 Configura tus tokens y APIs
TELEGRAM_TOKEN = ""
TMDB_API_KEY = ""
OMDB_API_KEY = ""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Funciones de búsqueda ---
def buscar_jikan(query):
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=5"
    try:
        resp = requests.get(url).json()
        return [(a["title"], a["url"]) for a in resp.get("data", [])]
    except Exception as e:
        logger.error(f"Error en Jikan: {e}")
        return []

def buscar_anilist(query):
    url = "https://graphql.anilist.co"
    query_str = """
    query ($search: String) {
      Page(perPage: 5) {
        media(search: $search, type: ANIME) {
          title { romaji english }
          siteUrl
        }
      }
    }
    """
    try:
        variables = {"search": query}
        resp = requests.post(url, json={"query": query_str, "variables": variables}).json()
        results = []
        for anime in resp.get("data", {}).get("Page", {}).get("media", []):
            titulo = anime["title"]["romaji"] or anime["title"].get("english")
            results.append((titulo, anime["siteUrl"]))
        return results
    except Exception as e:
        logger.error(f"Error en AniList: {e}")
        return []

def buscar_kitsu(query):
    url = f"https://kitsu.io/api/edge/anime?filter[text]={query}"
    try:
        resp = requests.get(url).json()
        results = []
        for a in resp.get("data", [])[:5]:
            titulo = a["attributes"]["titles"].get("en_jp", "Sin título")
            link = f"https://kitsu.io/anime/{a['id']}"
            results.append((titulo, link))
        return results
    except Exception as e:
        logger.error(f"Error en Kitsu: {e}")
        return []

def buscar_tmdb(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    try:
        resp = requests.get(url).json()
        results = []
        for peli in resp.get("results", [])[:5]:
            titulo = peli["title"]
            url_detalle = f"https://www.themoviedb.org/movie/{peli['id']}"
            trailer = None
            vids = requests.get(
                f"https://api.themoviedb.org/3/movie/{peli['id']}/videos?api_key={TMDB_API_KEY}"
            ).json()
            for v in vids.get("results", []):
                if v["site"] == "YouTube" and v["type"] == "Trailer":
                    trailer = f"https://www.youtube.com/watch?v={v['key']}"
                    break
            results.append((titulo, url_detalle, trailer))
        return results
    except Exception as e:
        logger.error(f"Error en TMDb: {e}")
        return []

def buscar_omdb(query):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
    try:
        resp = requests.get(url).json()
        return [
            (p["Title"], f"https://www.imdb.com/title/{p['imdbID']}/")
            for p in resp.get("Search", [])[:5]
        ]
    except Exception as e:
        logger.error(f"Error en OMDb: {e}")
        return []

def buscar_trakt(query):
    url = f"https://api.trakt.tv/search/movie,show?query={query}&limit=5"
    headers = {"Content-Type": "application/json", "trakt-api-version": "2", "trakt-api-key": "YOUR_TRAKT_API_KEY"}
    try:
        resp = requests.get(url, headers=headers).json()
        results = []
        for r in resp:
            if "movie" in r:
                title = r["movie"]["title"]
                link = f"https://trakt.tv/movies/{r['movie']['ids']['slug']}"
                results.append((title, link))
            elif "show" in r:
                title = r["show"]["title"]
                link = f"https://trakt.tv/shows/{r['show']['ids']['slug']}"
                results.append((title, link))
        return results
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en Trakt: {e}")
        return []

# --- Comandos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Buscar", callback_data="help_buscar")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="info")],
    ]
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot de películas, series y anime.\nElige una opción:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# Información de comandos
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📖 *Comandos disponibles:*\n\n"
        "👉 /buscar <nombre> — Buscar en múltiples fuentes (Jikan, AniList, Kitsu, etc.)\n"
        "👉 /start — Mostrar menú inicial\n"
        "👉 /info — Mostrar esta ayuda\n"
    )
    if update.message:
        await update.message.reply_text(texto, parse_mode="Markdown")
    else:
        await update.callback_query.message.reply_text(texto, parse_mode="Markdown")

# Función para buscar
async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else update.message.text.strip()

    if not query:
        await update.message.reply_text("⚠️ Usa: /buscar <nombre> o escribe el nombre directo del anime o película.")
        return

    # Crear los botones para elegir donde realizar la búsqueda (cada uno va con su callback_data)
    keyboard = [
        [InlineKeyboardButton("🎌 Buscar en Jikan", callback_data=f"jikan|{query}")],
        [InlineKeyboardButton("🌸 Buscar en AniList", callback_data=f"anilist|{query}")],
        [InlineKeyboardButton("🍥 Buscar en Kitsu", callback_data=f"kitsu|{query}")],
        [InlineKeyboardButton("🎬 Buscar en TMDb", callback_data=f"tmdb|{query}")],
        [InlineKeyboardButton("🎥 Buscar en OMDb", callback_data=f"omdb|{query}")],
        [InlineKeyboardButton("📺 Buscar en Trakt", callback_data=f"trakt|{query}")],
    ]
    
    # Responder con las opciones de búsqueda
    await update.message.reply_text(
        f"🔍 ¿Dónde quieres buscar *{query}*?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# Botón para manejar los resultados de las búsquedas
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Si la `query.data` no tiene el formato esperado, maneja botones simples
    if "|" not in query.data:
        if query.data == "help_buscar":
            await query.edit_message_text("Por favor, escribe el nombre de la película o anime para buscar.")
        elif query.data == "info":
            # Mostrar comandos cuando se hace clic en el botón Info
            await query.edit_message_text("📖 *Comandos disponibles:*\n\n"
                                          "👉 /buscar <nombre> — Buscar en múltiples fuentes (Jikan, AniList, Kitsu, etc.)\n"
                                          "👉 /start — Mostrar menú inicial\n"
                                          "👉 /info — Mostrar esta ayuda\n")
        return

    # Si `query.data` tiene el formato `fuente|texto`
    fuente, texto = query.data.split("|", 1)  # Dividimos la data del botón

    # Ejecutamos las búsquedas dependiendo de la fuente seleccionada
    if fuente == "jikan":
        resultados = buscar_jikan(texto)
    elif fuente == "anilist":
        resultados = buscar_anilist(texto)
    elif fuente == "kitsu":
        resultados = buscar_kitsu(texto)
    elif fuente == "tmdb":
        resultados = buscar_tmdb(texto)
    elif fuente == "omdb":
        resultados = buscar_omdb(texto)
    elif fuente == "trakt":
        resultados = buscar_trakt(texto)
    else:
        resultados = []

    if not resultados:
        await query.edit_message_text(f"❌ No se encontró nada para *{texto}*.")
        return

    # Crear los botones para mostrar los resultados
    botones = []
    for r in resultados:
        if len(r) == 3:  # TMDb con tráiler
            titulo, link, trailer = r
            row = [InlineKeyboardButton(titulo, url=link)]
            if trailer:
                row.append(InlineKeyboardButton("🎬 Ver tráiler", url=trailer))
            botones.append(row)
        else:
            titulo, link = r
            botones.append([InlineKeyboardButton(titulo, url=link)])

    # Mostrar los resultados al usuario
    await query.edit_message_text(
        f"📌 Resultados de *{texto}* en {fuente.upper()}:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(botones),
    )

# --- Main ---
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("buscar", buscar))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()

