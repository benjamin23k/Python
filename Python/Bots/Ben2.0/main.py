# main.py
import time
from voz import grabar_audio_seg, guardar_wav, verificar_voz_por_audio, transcribir_de_wav, hablar
from lenguaje import enviar_a_llm
from avatar import Avatar
from acciones import reproducir_youtube, abrir_url, obtener_hora
from imagenes import generar_imagen

import threading

# Inicializa avatar en hilo aparte (para que la UI siga)
avatar = Avatar("avatar.png")

def avatar_thread():
    while True:
        avatar.loop_once()

t = threading.Thread(target=avatar_thread, daemon=True)
t.start()

print("Ben 2.0 activo. Listo para escucharte (solo responderá si reconoce tu voz).")

try:
    while True:
        audio, fs = grabar_audio_seg(duracion=4)
        # Verificar voiceprint
        score = verificar_voz_por_audio(audio)
        print(f"Similitud voz: {score:.3f}")
        if score >= 0.78:
            fname = guardar_wav(audio, fs, "temp_input.wav")
            texto = transcribir_de_wav("temp_input.wav")
            texto = texto.lower().strip()
            print("Transcripción:", texto)
            if not texto:
                hablar("No escuché nada claro.")
                continue

            # Comandos locales simples
            if "reproduce" in texto or "reproducir" in texto:
                # ejemplo: "reproduce canción nombre"
                q = texto.replace("reproduce", "").replace("reproducir", "").strip()
                if q:
                    hablar(f"Reproduciendo {q}")
                    reproducir_youtube(q)
                else:
                    hablar("¿Qué quieres que reproduzca?")
                continue

            if "hora" in texto:
                h = obtener_hora()
                hablar(f"Son las {h}")
                continue

            if "abre" in texto and "google" in texto:
                hablar("Abriendo Google")
                abrir_url("https://www.google.com")
                continue

            # Generación de imagen
            if "imagen" in texto or "dibujar" in texto or "genera" in texto:
                prompt_img = texto.replace("dibujar","").replace("imagen","").replace("genera","").strip()
                hablar("Generando la imagen, espera un momento")
                ok, res = generar_imagen(prompt_img)
                if ok:
                    hablar("Imagen generada")
                    # opcional: abrirla con el visor predeterminado
                    abrir_url(res)
                else:
                    hablar("No pude generar la imagen: " + res)
                continue

            # Si no es comando local, mandamos al LLM
            hablar("Procesando tu consulta")
            respuesta = enviar_a_llm(texto)
            if respuesta:
                hablar(respuesta)
            else:
                hablar("No obtuve respuesta del modelo.")
        else:
            print("Voz no reconocida. Ignorando audio.")
        # pequeño delay para evitar loops superrápidos
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Saliendo...")
