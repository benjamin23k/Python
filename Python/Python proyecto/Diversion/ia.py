import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import openai

# Cargar variables de entorno
load_dotenv()

# Inicializar Firebase
cred = credentials.Certificate("ruta/al/archivo/credenciales.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Configurar API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def guardar_en_nube(coleccion, datos):
    """Guarda los datos en Firestore."""
    doc_ref = db.collection(coleccion).add(datos)
    print("Datos guardados en la nube.")

def procesar_texto(texto):
    """Procesa el texto usando OpenAI."""
    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": texto}]
    )
    return respuesta["choices"][0]["message"]["content"]

# Ejemplo de uso
if __name__ == "__main__":
    entrada_usuario = input("Escribe algo: ")
    respuesta_ia = procesar_texto(entrada_usuario)
    print("IA:", respuesta_ia)
    
    # Guardar en la nube
    guardar_en_nube("respuestas", {"entrada": entrada_usuario, "respuesta": respuesta_ia})
