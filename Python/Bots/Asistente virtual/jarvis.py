# =================== JARVIS PRO 3.3 CINEMATIC ULTIMATE ===================

import json, os, pyttsx3, pywhatkit, pyautogui
import speech_recognition as sr
from datetime import datetime, date, timedelta
from time import sleep
from PyPDF2 import PdfReader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import cv2, numpy as np, pytesseract
import google.generativeai as genai

# IA local
try:
    from gpt4all import GPT4All
    local_model = GPT4All("ggml-gpt4all-j-v1.3-groovy.bin")
except: local_model=None

# Módulos locales
try: import spoty, AVMYT as yt
except: spoty=None; yt=None

from config import TOKEN_GOOGLE, MODEL_NAME
genai.configure(api_key=TOKEN_GOOGLE)

# ---------------- CONFIG ----------------
NAME = "benjamin"
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
if voices: engine.setProperty('voice', voices[0].id)
engine.setProperty('rate',178)
engine.setProperty('volume',0.7)

SPOTIFY_KEYS_PATH = r"C:\\Users\\wilson\\Desktop\\Programar\\Full Stack\\Python\\Asistente virtual\\spotify_keys.json"
MEMORIA_PATH = "memoria_jarvis.json"
HISTORIAL_ACCIONES = "acciones_jarvis.json"

with open(SPOTIFY_KEYS_PATH,"r") as f: keys=json.load(f)

try:
    day_es=[line.rstrip('\n') for line in open('day_es.txt')]
    day_en=[line.rstrip('\n') for line in open('day_en.txt')]
except: 
    day_en=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    day_es=['lunes','martes','miercoles','jueves','viernes','sabado','domingo']

# ---------------- FUNCIONES BASE ----------------
def speak(text, emotion="neutral"):
    try:
        if emotion=="happy": engine.setProperty('rate',200)
        elif emotion=="sad": engine.setProperty('rate',150)
        else: engine.setProperty('rate',178)
        engine.say(str(text))
        engine.runAndWait()
    except Exception as e: print(f"TTS error: {e}")

def guardar_memoria(clave, valor):
    try: 
        with open(MEMORIA_PATH,"r") as f: data=json.load(f)
    except: data={}
    data[clave]=valor
    with open(MEMORIA_PATH,"w") as f: json.dump(data,f,indent=4,ensure_ascii=False)

def cargar_memoria(clave):
    try:
        with open(MEMORIA_PATH,"r") as f: data=json.load(f)
        return data.get(clave,"")
    except: return ""

def guardar_historial_conversacion(mensaje, respuesta):
    historial = cargar_memoria("historial_conversacion") or []
    historial.append({"pregunta": mensaje, "respuesta": respuesta, "fecha": str(datetime.now())})
    guardar_memoria("historial_conversacion", historial)

def guardar_accion(accion, detalles=""):
    try:
        with open(HISTORIAL_ACCIONES,"r") as f: data=json.load(f)
    except: data=[]
    data.append({"fecha":str(datetime.now()), "accion":accion, "detalles":detalles})
    with open(HISTORIAL_ACCIONES,"w") as f: json.dump(data,f,indent=4,ensure_ascii=False)

# ---------------- AUDIO ----------------
def get_audio(phrase_time_limit=8):
    r=sr.Recognizer(); rec=""; status=False
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source,duration=1)
            audio=r.listen(source,timeout=5,phrase_time_limit=phrase_time_limit)
            try:
                rec=r.recognize_google(audio,language='es-ES').lower()
                rec=rec.translate(str.maketrans("áéíóú","aeiou"))
                if NAME in rec: rec=rec.replace(f"{NAME} ","")
                status=True
            except: pass
    except Exception as e: print(f"Mic error: {e}")
    return {'text':rec,'status':status}

# ---------------- IA HIBRIDA ----------------
def generar_respuesta(prompt: str, intentos=2):
    historial = cargar_memoria("historial_conversacion") or []
    contexto = "\n".join([f"Usuario: {h['pregunta']}\nJarvis: {h['respuesta']}" for h in historial[-10:]])
    full_prompt = f"{contexto}\nUsuario: {prompt}\nJarvis:"
    for i in range(intentos):
        if local_model:
            try:
                texto = local_model.generate(full_prompt)
                if texto: 
                    guardar_historial_conversacion(prompt, texto)
                    return texto
            except: pass
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            resp = model.generate_content(full_prompt)
            texto = getattr(resp, 'text', None)
            if texto: 
                guardar_historial_conversacion(prompt, texto)
                return texto
        except: pass
        sleep(1)
    return "No entendí, pero sigo escuchando. ¿Puedes repetirlo de otra forma?"

# ---------------- VISIÓN CINEMÁTICA ----------------
def analizar_pantalla_cinematica():
    screenshot=pyautogui.screenshot()
    frame=cv2.cvtColor(np.array(screenshot),cv2.COLOR_RGB2BGR)
    texto_detectado=pytesseract.image_to_string(frame)
    elementos_detectados=[]
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    _,thresh=cv2.threshold(gray,200,255,cv2.THRESH_BINARY)
    contours,_=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        x,y,w,h=cv2.boundingRect(cnt)
        if w>50 and h>20: elementos_detectados.append((x,y,w,h))
    return texto_detectado, elementos_detectados

# ---------------- CONTROL SISTEMA ----------------
def ejecutar_app(nombre_app):
    try: os.startfile(nombre_app); guardar_accion("Abrir app",nombre_app)
    except: speak(f"No pude abrir {nombre_app}")

def controlar_volumen(valor):
    pyautogui.press("volumeup" if valor>0 else "volumedown",presses=abs(valor))
    guardar_accion("Control volumen",str(valor))

# ---------------- LOOP ULTIMATE ----------------
def loop_ultimate():
    speak("Jarvis PRO 3.3 Cinematic Ultimate activo. Escuchando y aprendiendo continuamente.")
    while True:
        try:
            rec_json = get_audio(phrase_time_limit=15)
            rec = rec_json['text']
            status = rec_json['status']

            # Analiza pantalla constantemente
            texto_pantalla, elementos = analizar_pantalla_cinematica()
            contexto_visual = f"Texto en pantalla: {texto_pantalla[:200]}..." if texto_pantalla else ""
            contexto_visual += f" Elementos detectados: {len(elementos)}" if elementos else ""

            if not status or not rec:
                sleep(1)
                continue

            if 'adios' in rec or 'termina' in rec:
                speak("Hasta luego, cierro la conversación.", emotion="happy")
                break

            # ---- COMANDOS ----
            elif 'abre' in rec: ejecutar_app(rec.replace('abre','').strip())
            elif 'sube volumen' in rec: controlar_volumen(1)
            elif 'baja volumen' in rec: controlar_volumen(-1)

            # ---- MÚSICA ----
            elif 'reproduce' in rec:
                music = rec.replace('reproduce','').strip()
                if 'spotify' in rec and spoty:
                    resultado = spoty.play(keys.get("spoty_client_id"), keys.get("spoty_client_secret"), music)
                    if resultado.get('success'): speak(f"Reproduciendo {resultado.get('name','desconocida')} en Spotify")
                    else: pywhatkit.playonyt(music)
                else: pywhatkit.playonyt(music)
                guardar_accion("Reproducir música", music)

            # ---- RESPUESTA IA CON CONTEXTO VISUAL ----
            else:
                prompt = f"{rec}\nInformación visual: {contexto_visual}"
                resp = generar_respuesta(prompt)
                speak(resp)
                guardar_accion("Conversación Cinemática Ultimate", rec)

        except Exception as e:
            print(f"Error loop ultimate: {e}")
            speak("Ocurrió un error, pero sigo escuchando...")
            continue

# ---------------- INICIAR ----------------
if __name__=="__main__":
    loop_ultimate()
