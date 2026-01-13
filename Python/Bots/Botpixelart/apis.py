import requests

# 🚨 Configura tus API KEYS
TMDB_API_KEY = "5fe9d8979f59ac1491bf662e320259b7"
OMDB_API_KEY = "ba962c53"
TRAKT_CLIENT_ID = "41cb73dd1b7ad79c68ec5fb871797fb0da46df4e7aec9296ff9110f32ecc8123"

# --- ANIME ---
def buscar_jikan(query):
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=5"
    resp = requests.get(url).json()
    resultados = []
    for a in resp.get("data", []):
        resultados.append((a["title"], a["url"], None))
    return resultados


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
    resp = requests.post(url, json={"query": query_str, "variables": {"search": query}}).json()
    resultados = []
    for m in resp.get("data", {}).get("Page", {}).get("media", []):
        titulo = m["title"]["romaji"] or m["title"].get("english")
        resultados.append((titulo, m["siteUrl"], None))
    return resultados


def buscar_kitsu(query):
    url = f"https://kitsu.io/api/edge/anime?filter[text]={query}"
    resp = requests.get(url).json()
    resultados = []
    for a in resp.get("data", [])[:5]:
        resultados.append((a["attributes"]["canonicalTitle"], f"https://kitsu.io/anime/{a['id']}", None))
    return resultados


# --- PELÍCULAS / SERIES ---
def buscar_tmdb(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    resp = requests.get(url).json()
    resultados = []
    for peli in resp.get("results", [])[:5]:
        trailer = f"https://www.youtube.com/results?search_query={peli['title']} trailer"
        resultados.append((peli["title"], f"https://www.themoviedb.org/movie/{peli['id']}", trailer))
    return resultados


def buscar_omdb(query):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
    resp = requests.get(url).json()
    resultados = []
    for m in resp.get("Search", [])[:5]:
        resultados.append((m["Title"], f"https://www.imdb.com/title/{m['imdbID']}/", None))
    return resultados


def buscar_trakt(query):
    url = f"https://api.trakt.tv/search/movie,show?query={query}"
    headers = {
        "Content-Type": "application/json",
        "trakt-api-version": "2",
        "trakt-api-key": TRAKT_CLIENT_ID,
        "User-Agent": "MiBot/1.0"
    }
    resp = requests.get(url, headers=headers).json()
    resultados = []
    for r in resp[:5]:
        if "movie" in r:
            resultados.append((r["movie"]["title"], f"https://trakt.tv/movies/{r['movie']['ids']['slug']}", None))
        elif "show" in r:
            resultados.append((r["show"]["title"], f"https://trakt.tv/shows/{r['show']['ids']['slug']}", None))
    return resultados


def buscar_imdb(query):
    return [("Búsqueda en IMDb", f"https://www.imdb.com/find?q={query.replace(' ', '+')}", None)]


def buscar_justwatch(query):
    return [("Dónde ver", f"https://www.justwatch.com/search?q={query.replace(' ', '+')}", None)]


# --- Buscar en todas ---
def buscar_en_todas(query):
    resultados = []
    apis = [
        ("🎬 Trakt", buscar_trakt),
        ("🎥 TMDb", buscar_tmdb),
        ("📀 OMDb", buscar_omdb),
        ("🎌 Jikan", buscar_jikan),
        ("🌸 AniList", buscar_anilist),
        ("🍥 Kitsu", buscar_kitsu),
        ("📺 JustWatch", buscar_justwatch),
    ]
    for nombre, funcion in apis:
        try:
            res = funcion(query)
            if res:
                for titulo, link, trailer in res:
                    resultados.append((f"{titulo} ({nombre})", link, trailer))
        except Exception as e:
            print(f"⚠️ Error en {nombre}: {e}")

    if not resultados:
        resultados.append(("❌ No se encontró nada en ninguna API", "https://www.google.com", None))

    return resultados
