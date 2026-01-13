import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import openai
import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image

def inicializar_sistema():
    """Inicializa Firebase y carga variables de entorno."""
    print("Inicializando el sistema...")
    load_dotenv()
    
    # Ruta al archivo de credenciales
    credenciales_path = "c:/Users/wilson/Desktop/Aprender a Programar/Python/credenciales.json"
    print(f"Ruta de credenciales: {credenciales_path}")
    
    # Verificar si el archivo de credenciales existe
    if not os.path.exists(credenciales_path):
        raise FileNotFoundError(f"El archivo de credenciales no se encontró en: {credenciales_path}")
    else:
        print("El archivo de credenciales fue encontrado.")
    
    # Inicializar Firebase
    try:
        cred = credentials.Certificate(credenciales_path)
        firebase_admin.initialize_app(cred)
        print("Firebase inicializado correctamente.")
        return firestore.client()
    except Exception as e:
        raise RuntimeError(f"Error al inicializar Firebase: {e}")

try:
    db = inicializar_sistema()
    openai_api_key = os.getenv("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")  # Carga la clave desde el archivo .env
    if not openai_api_key:
        raise ValueError("La clave de OpenAI no está configurada en las variables de entorno.")
    else:
        print("Clave de OpenAI cargada correctamente.")
    openai.api_key = openai_api_key
except Exception as e:
    print(f"Error crítico durante la inicialización: {e}")
    exit(1)

def guardar_en_nube(coleccion, datos):
    """Guarda los datos en Firestore."""
    print(f"Guardando en la nube: {datos}")
    try:
        db.collection(coleccion).add(datos)
        print("Datos guardados en la nube.")
    except Exception as e:
        print(f"Error al guardar en Firestore: {e}")

def procesar_texto(texto):
    """Procesa el texto usando OpenAI."""
    print(f"Procesando texto: {texto}")
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": texto}]
        )
        return respuesta["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error al procesar texto con OpenAI: {e}")
        return "Lo siento, ocurrió un error al procesar tu solicitud."

def clasificar_imagen(ruta_imagen):
    """Clasifica una imagen usando un modelo de visión artificial."""
    try:
        modelo = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
        modelo.eval()
        transformacion = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        imagen = Image.open(ruta_imagen).convert('RGB')
        imagen = transformacion(imagen).unsqueeze(0)
        with torch.no_grad():
            salida = modelo(imagen)
        clase = torch.argmax(salida).item()
        print(f"La imagen ha sido clasificada con la clase: {clase}")
        guardar_en_nube("imagenes", {"ruta": ruta_imagen, "clase": clase})
        return clase
    except Exception as e:
        print(f"Error al clasificar la imagen: {e}")

def asistente_virtual():
    """Ejecuta un asistente virtual interactivo con procesamiento de texto e imágenes."""
    print("Asistente Virtual: Hola, ¿en qué puedo ayudarte hoy?")
    while True:
        entrada_usuario = input("Tú: ")
        if entrada_usuario.lower() in ["salir", "exit", "adiós"]:
            print("Asistente Virtual: ¡Hasta luego!")
            break
        elif entrada_usuario.lower().startswith("imagen "):
            ruta_imagen = entrada_usuario.split(" ", 1)[1]
            clasificar_imagen(ruta_imagen)
        else:
            respuesta_ia = procesar_texto(entrada_usuario)
            print("Asistente Virtual:", respuesta_ia)
            guardar_en_nube("conversaciones", {"usuario": entrada_usuario, "respuesta": respuesta_ia})

# Ejecutar el asistente virtual
if __name__ == "__main__":
    print("Iniciando el asistente virtual...")
    asistente_virtual()
