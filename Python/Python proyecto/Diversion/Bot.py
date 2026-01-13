import logging
import requests
import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# 🚨 Configura tus tokens y APIs
TELEGRAM_TOKEN = "8495110555:AAFNjCnvCZBQQbUJmcVr-GG4rPY6IFp-QXk"
TMDB_API_KEY = "5fe9d8979f59ac1491bf662e320259b7"
OMDB_API_KEY = "ba962c53 "

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Listas de géneros ---
GENRES_MOVIES = {
    "Acción": 28,
    "Aventura": 12,
    "Animación": 16,
    "Comedia": 35,
    "Crimen": 80,
    "Documental": 99,
    "Drama": 18,
    "Familia": 10751,
    "Fantasía": 14,
    "Historia": 36,
    "Terror": 27,
    "Música": 10402,
    "Misterio": 9648,
    "Romance": 10749,
    "Ciencia Ficción": 878,
    "Película de TV": 10770,
    "Thriller": 53,
    "Bélica": 10752,
    "Western": 37
}

GENRES_TV = {
    "Acción & Aventura": 10759,
    "Animación": 16,
    "Comedia": 35,
    "Crimen": 80,
    "Documental": 99,
    "Drama": 18,
    "Familia": 10751,
    "Infantil": 10762,
    "Misterio": 9648,
    "Noticias": 10763,
    "Realidad": 10764,
    "Ciencia Ficción & Fantasía": 10765,
    "Telenovela": 10766,
    "Talk Show": 10767,
    "Guerra & Política": 10768,
    "Western": 37
}


# --- Funciones de búsqueda ---
def buscar_jikan(query):
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=5"
    resp = requests.get(url).json()
    return [(a["title"], a["url"]) for a in resp.get("data", [])]


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
    variables = {"search": query}
    resp = requests.post(url, json={"query": query_str, "variables": variables}).json()
    results = []
    for anime in resp.get("data", {}).get("Page", {}).get("media", []):
        titulo = anime["title"]["romaji"] or anime["title"].get("english")
        results.append((titulo, anime["siteUrl"]))
    return results


def buscar_kitsu(query):
    url = f"https://kitsu.io/api/edge/anime?filter[text]={query}"
    resp = requests.get(url).json()
    results = []
    for a in resp.get("data", [])[:5]:
        titulo = a["attributes"]["titles"].get("en_jp", "Sin título")
        link = f"https://kitsu.io/anime/{a['id']}"
        results.append((titulo, link))
    return results


def buscar_tmdb(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    resp = requests.get(url).json()
    results = []
    for peli in resp.get("results", [])[:5]:
        titulo = peli["title"]
        url_detalle = f"https://www.themoviedb.org/movie/{peli['id']}"
        trailer = None
        # Intentar buscar tráiler
        vids = requests.get(
            f"https://api.themoviedb.org/3/movie/{peli['id']}/videos?api_key={TMDB_API_KEY}"
        ).json()
        for v in vids.get("results", []):
            if v["site"] == "YouTube" and v["type"] == "Trailer":
                trailer = f"https://www.youtube.com/watch?v={v['key']}"
                break
        results.append((titulo, url_detalle, trailer))
    return results


def buscar_omdb(query):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
    resp = requests.get(url).json()
    return [
        (p["Title"], f"https://www.imdb.com/title/{p['imdbID']}/")
        for p in resp.get("Search", [])[:5]
    ]


def buscar_trakt(query):
    url = f"https://api.trakt.tv/search/movie,show?query={query}&limit=5"
    headers = {"Content-Type": "application/json", "trakt-api-version": "2"}
    resp = requests.get(url, headers=headers).json()
    results = []
    for r in resp:
        title = r.get("movie", r.get("show", {})).get("title", "Sin título")
        slug = r.get("movie", r.get("show", {})).get("ids", {}).get("slug", "")
        link = f"https://trakt.tv/{'movies' if 'movie' in r else 'shows'}/{slug}"
        results.append((title, link))
    return results


def buscar_justwatch(query):
    # Dummy: JustWatch oficial requiere scraping/SDK externo
    return [(f"{query} en JustWatch", f"https://www.justwatch.com/search?q={query}")]


# --- Sugerencias ---
def sugerir_por_genero(genero, tipo="movie"):
    lista = GENRES_MOVIES if tipo == "movie" else GENRES_TV
    genero_id = None
    for g, gid in lista.items():
        if g.lower() == genero.lower():
            genero_id = gid
            break
    if not genero_id:
        return None

    url = f"https://api.themoviedb.org/3/discover/{tipo}?api_key={TMDB_API_KEY}&with_genres={genero_id}"
    resp = requests.get(url).json()
    if not resp.get("results"):
        return []

    eleccion = random.choice(resp["results"])
    titulo = eleccion.get("title") or eleccion.get("name")
    link = f"https://www.themoviedb.org/{tipo}/{eleccion['id']}"
    return [(titulo, link)]


# --- Comandos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Buscar", callback_data="help_buscar")],
        [InlineKeyboardButton("🎲 Sugerir algo", callback_data="help_sugerir")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="info")],
    ]
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot de películas, series y anime.\nElige una opción:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📖 *Comandos disponibles:*\n\n"
        "👉 /buscar <nombre> — Buscar en múltiples fuentes\n"
        "👉 /sugerir <género> — Recomendar algo random\n"
        "👉 /generos — Mostrar lista de géneros\n"
        "👉 /start — Mostrar menú inicial\n"
        "👉 /info — Mostrar esta ayuda\n"
    )
    if update.message:
        await update.message.reply_text(texto, parse_mode="Markdown")
    else:
        await update.callback_query.message.reply_text(texto, parse_mode="Markdown")


async def generos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = "🎬 *Géneros disponibles para películas:*\n" + ", ".join(GENRES_MOVIES.keys())
    texto += "\n\n📺 *Géneros disponibles para series:*\n" + ", ".join(GENRES_TV.keys())
    await update.message.reply_text(texto, parse_mode="Markdown")


async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else update.message.text.strip()
    if not query:
        await update.message.reply_text("⚠️ Usa: /buscar <nombre> o escribe el nombre directo.")
        return

    keyboard = [
        [InlineKeyboardButton("🎌 Jikan", callback_data=f"jikan|{query}")],
        [InlineKeyboardButton("🌸 AniList", callback_data=f"anilist|{query}")],
        [InlineKeyboardButton("🍥 Kitsu", callback_data=f"kitsu|{query}")],
        [InlineKeyboardButton("🎬 TMDb", callback_data=f"tmdb|{query}")],
        [InlineKeyboardButton("🎥 OMDb", callback_data=f"omdb|{query}")],
        [InlineKeyboardButton("📺 Trakt", callback_data=f"trakt|{query}")],
        [InlineKeyboardButton("🌍 JustWatch", callback_data=f"justwatch|{query}")],
    ]
    await update.message.reply_text(
        f"🔍 ¿Dónde quieres buscar *{query}*?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def sugerir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usa: /sugerir <género> (ej: /sugerir Acción)")
        return
    genero = " ".join(context.args)
    resultados = sugerir_por_genero(genero, "movie")
    if not resultados:
        await update.message.reply_text("❌ Género no válido o sin resultados.")
        return

    botones = [InlineKeyboardButton(resultados[0][0], url=resultados[0][1])]
    await update.message.reply_text(
        f"🎲 Te sugiero ver algo del género *{genero}*:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([botones]),
    )


# --- Botones ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "info":
        await info(update, context)
        return
    if query.data == "help_buscar":
        await query.edit_message_text("Escribe `/buscar <nombre>` o solo el nombre en el chat.")
        return
    if query.data == "help_sugerir":
        await query.edit_message_text("Usa `/sugerir <género>` para recibir una recomendación random.")
        return

    fuente, texto = query.data.split("|", 1)
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
    elif fuente == "justwatch":
        resultados = buscar_justwatch(texto)
    else:
        resultados = []

    if not resultados:
        await query.edit_message_text("❌ No se encontró nada.")
        return

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
    app.add_handler(CommandHandler("sugerir", sugerir))
    app.add_handler(CommandHandler("generos", generos))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buscar))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot corriendo...")
    app.run_polling()


if __name__ == "__main__":
    main()
