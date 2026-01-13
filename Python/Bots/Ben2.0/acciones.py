# acciones.py
import os, webbrowser, pywhatkit
from datetime import datetime

def reproducir_youtube(query):
    pywhatkit.playonyt(query)

def abrir_url(url):
    webbrowser.open(url)

def abrir_programa_windows(nombre):
    os.system(f"start {nombre}")

def obtener_hora():
    return datetime.now().strftime("%H:%M")