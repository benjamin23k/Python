import random
from apis import buscar_tmdb, buscar_anilist, buscar_jikan

# Lista de géneros válidos
GENEROS_PELIS = ["accion", "aventura", "comedia", "drama", "terror", "ciencia ficcion", "romance", "fantasia", "animacion"]
GENEROS_ANIMES = ["shonen", "shoujo", "seinen", "josei", "isekai", "mecha", "fantasia", "accion", "comedia", "drama"]

def random_por_genero(genero, tipo="pelicula"):
    """Devuelve algo random segun genero y tipo (pelicula/anime)."""
    resultados = []

    if tipo == "pelicula":
        resultados = buscar_tmdb(genero)
    elif tipo == "anime":
        resultados = buscar_anilist(genero) + buscar_jikan(genero)

    if not resultados:
        return [("❌ No se encontró nada para ese género", "https://www.google.com")]

    return [random.choice(resultados)]
