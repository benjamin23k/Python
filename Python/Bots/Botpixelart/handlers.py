import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import apis
import database as db

# 🎭 Lista de géneros válidos (pelis y animes mezclados)
GENEROS = [
    "acción", "aventura", "comedia", "drama", "terror", "romance",
    "sci-fi", "fantasía", "shonen", "seinen", "isekai", "mecha"
]

# 🟢 Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.guardar_usuario(update.effective_user.id, update.effective_user.username)
    keyboard = [
        [InlineKeyboardButton("🔍 Buscar", callback_data="menu_buscar")],
        [InlineKeyboardButton("🎲 Random", callback_data="menu_random")],
        [InlineKeyboardButton("⭐ Favoritos", callback_data="menu_fav")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="menu_info")],
    ]
    await update.message.reply_text(
        "👋 ¡Bienvenido! Soy tu bot de películas y anime.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# 🟢 Info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📖 *Comandos:*\n\n"
        "👉 /buscar <nombre> — Buscar en múltiples fuentes\n"
        "👉 /random <género> — Te sugiero algo random\n"
        "👉 /favoritos — Ver tu lista de favoritos\n\n"
        "🎭 *Géneros válidos:* " + ", ".join(GENEROS)
    )
    if update.message:
        await update.message.reply_text(texto, parse_mode="Markdown")
    else:
        await update.callback_query.message.reply_text(texto, parse_mode="Markdown")

# 🟢 Buscar
async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else update.message.text.strip()
    if not query:
        await update.message.reply_text("⚠️ Usa: /buscar <nombre>")
        return
    keyboard = [
        [InlineKeyboardButton("🎌 Jikan", callback_data=f"jikan|{query}")],
        [InlineKeyboardButton("🌸 AniList", callback_data=f"anilist|{query}")],
        [InlineKeyboardButton("🍙 Kitsu", callback_data=f"kitsu|{query}")],
        [InlineKeyboardButton("🎬 TMDb", callback_data=f"tmdb|{query}")],
        [InlineKeyboardButton("🎥 OMDb", callback_data=f"omdb|{query}")],
        [InlineKeyboardButton("📺 Trakt", callback_data=f"trakt|{query}")],
        [InlineKeyboardButton("🎞 IMDb", callback_data=f"imdb|{query}")],
        [InlineKeyboardButton("🍿 JustWatch", callback_data=f"justwatch|{query}")],
    ]
    await update.message.reply_text(
        f"🔍 ¿Dónde buscar *{query}*?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# 🟢 Botón Callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # Detectar de qué API viene la búsqueda
    if q.data.startswith("jikan|"):
        resultados = apis.buscar_jikan(q.data.split("|", 1)[1])
    elif q.data.startswith("anilist|"):
        resultados = apis.buscar_anilist(q.data.split("|", 1)[1])
    elif q.data.startswith("kitsu|"):
        resultados = apis.buscar_kitsu(q.data.split("|", 1)[1])
    elif q.data.startswith("tmdb|"):
        resultados = apis.buscar_tmdb(q.data.split("|", 1)[1])
    elif q.data.startswith("omdb|"):
        resultados = apis.buscar_omdb(q.data.split("|", 1)[1])
    elif q.data.startswith("trakt|"):
        resultados = apis.buscar_trakt(q.data.split("|", 1)[1])
    elif q.data.startswith("imdb|"):
        resultados = apis.buscar_imdb(q.data.split("|", 1)[1])
    elif q.data.startswith("justwatch|"):
        resultados = apis.buscar_justwatch(q.data.split("|", 1)[1])
    else:
        resultados = []

    if not resultados:
        await q.edit_message_text("❌ No se encontró nada.")
        return

    # Construcción de botones con opción de tráiler
    botones = []
    for r in resultados:
        if len(r) == 3:  # con tráiler
            botones.append([
                InlineKeyboardButton(r[0], url=r[1]),
                InlineKeyboardButton("🎬 Tráiler", url=r[2])
            ])
        else:
            botones.append([InlineKeyboardButton(r[0], url=r[1])])

    await q.edit_message_text("📌 Resultados:", reply_markup=InlineKeyboardMarkup(botones))

# 🟢 Random
async def random_recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    genero = " ".join(context.args).lower() if context.args else random.choice(GENEROS)

    if genero not in [g.lower() for g in GENEROS]:
        await update.message.reply_text(
            "⚠️ Género no válido.\n\n"
            "👉 Usa uno de estos: " + ", ".join(GENEROS)
        )
        return

    await update.message.reply_text(f"🎲 Buscando algo random de *{genero}*...", parse_mode="Markdown")

    # Ahora podríamos mezclar entre TMDb (pelis/series) y AniList/Jikan (anime)
    resultados = apis.buscar_tmdb(genero) or apis.buscar_anilist(genero) or apis.buscar_jikan(genero)

    if resultados:
        elegido = random.choice(resultados)
        if len(elegido) == 3:  # título, link, tráiler
            titulo, link, trailer = elegido
            await update.message.reply_text(
                f"👉 Te recomiendo: [{titulo}]({link}) 🎬",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Ver tráiler 🎬", url=trailer)]])
            )
        else:
            titulo, link = elegido
            await update.message.reply_text(
                f"👉 Te recomiendo: [{titulo}]({link})",
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text("⚠️ No encontré nada para ese género.")
