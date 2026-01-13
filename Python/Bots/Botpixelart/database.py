import sqlite3

DB_NAME = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS favoritos (user_id INTEGER, titulo TEXT, link TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS historial (user_id INTEGER, consulta TEXT)")
    conn.commit()
    conn.close()

def guardar_usuario(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?,?)", (user_id, username))
    conn.commit()
    conn.close()

def agregar_favorito(user_id, titulo, link):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO favoritos (user_id, titulo, link) VALUES (?,?,?)", (user_id, titulo, link))
    conn.commit()
    conn.close()

def ver_favoritos(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT titulo, link FROM favoritos WHERE user_id=?", (user_id,))
    data = c.fetchall()
    conn.close()
    return data
