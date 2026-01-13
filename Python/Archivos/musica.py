import pygame
import pyfiglet
import time
import os
import random
import shutil
from colorama import init, Fore, Style

# --- INICIALIZACIÓN ---
init(autoreset=True)
pygame.mixer.init()

# ================= CONFIGURACIÓN =================

NOMBRE_CANCION = r"C:\Users\wilson\Desktop\Programar\Full Stack\Lenguajes Programacion\Python\Archivos\Consume.mp3"


SEGUNDO_INICIO = 0.0  # Desde el principio
DURACION_CLIP = 50.0  # Duración suficiente para todo el verso

BPM_SIMULADO = 0.08  
FUENTE_ASCII = 'slant' 

COLORES = [
    Fore.RED, Fore.LIGHTRED_EX, Fore.YELLOW, Fore.LIGHTYELLOW_EX, 
    Fore.GREEN, Fore.LIGHTGREEN_EX, Fore.CYAN, Fore.LIGHTCYAN_EX, 
    Fore.BLUE, Fore.LIGHTBLUE_EX, Fore.MAGENTA, Fore.LIGHTMAGENTA_EX
]

# ================= FUNCIONES =================

def obtener_ancho_terminal():
    try:
        columnas, _ = shutil.get_terminal_size()
        return columnas
    except:
        return 80

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def generar_barras_audio(frame):
    niveles = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    ancho = obtener_ancho_terminal()
    visual = ""
    for i in range(int(ancho / 2)): 
        altura = random.randint(0, 7)
        visual += niveles[altura] + " "
    return visual

def centrar_ascii(texto_ascii):
    lineas = texto_ascii.split('\n')
    ancho_terminal = obtener_ancho_terminal()
    texto_centrado = []
    for linea in lineas:
        padding = max(0, (ancho_terminal - len(linea)) // 2)
        texto_centrado.append(" " * padding + linea)
    return "\n".join(texto_centrado)

def imprimir_letra(texto, color_actual):
    try:
        ascii_art = pyfiglet.figlet_format(texto, font=FUENTE_ASCII)
        ascii_art_centrado = centrar_ascii(ascii_art)
        print(color_actual + Style.BRIGHT + ascii_art_centrado)
    except:
        print(color_actual + texto.center(obtener_ancho_terminal()))

def reproducir_con_letras(letras_tiempos):
    try:
        print(Fore.CYAN + "Iniciando reproducción...")
        pygame.mixer.music.load(NOMBRE_CANCION)
        pygame.mixer.music.play(start=SEGUNDO_INICIO)
    except Exception as e:
        print(Fore.RED + f"ERROR: No encuentro la canción en:\n{NOMBRE_CANCION}")
        return

    inicio = time.time()
    indice_letra = 0
    texto_a_mostrar = "..."
    frame_count = 0 

    while pygame.mixer.music.get_busy():
        tiempo_actual = time.time() - inicio
        
        if tiempo_actual > DURACION_CLIP:
            break

        limpiar_pantalla()
        
        # Visualizador Rainbow
        color_vis = COLORES[frame_count % len(COLORES)]
        print(color_vis + generar_barras_audio(frame_count))
        print(Style.DIM + Fore.WHITE + "-" * (obtener_ancho_terminal() - 1))

        # Sincronización
        while indice_letra < len(letras_tiempos) and tiempo_actual >= letras_tiempos[indice_letra][0]:
            texto_a_mostrar = letras_tiempos[indice_letra][1]
            indice_letra += 1

        # Mostrar Letra
        color_letra = COLORES[int(tiempo_actual * 2) % len(COLORES)]
        if texto_a_mostrar:
            print("\n" * 2) 
            imprimir_letra(texto_a_mostrar, color_letra)
            print("\n" * 2)

        # Barra de tiempo
        print(Fore.WHITE + Style.DIM + f"Tiempo: {tiempo_actual:.1f}s")

        frame_count += 1
        time.sleep(BPM_SIMULADO)

# ================= LETRA =================
letras = [
    (0.5,  "Voices in my head"),
    (1.5,  "SCREAMING"),
    (2.8,  "RUN NOW!"),
    (4.0,  "I'm praying"),
    (5.0,  "They are HUMAN"),
    
    (7.8,  "Alright..."),
    (8.5,  "ALRIGHT WOAH"),
    
    (9.8,  "Love you but..."),
    (10.8, "Cannot spend"),
    (11.5, "THE NIGHT"),
    
    (12.8, "I've been alone"),
    (14.0, "Almost all my life"),
    
    (15.5, "Shit like that"),
    (16.5, "Don't change up"),
    (17.2, "OVERNIGHT"),
    
    (18.5, "I let you sleep"),
    (19.5, "In my TEE"),
    
    (20.8, "Tell me the things"),
    (22.0, "You dont tweet"),
    
    (23.5, "Acid and LSD"),
    (25.0, "Smoking Blunts"),
    (26.5, "On the BEACH"),
    
    (28.0, "69 down 69"),
    (29.5, "So we both"),
    (30.2, "GET A PIECE"),
    
    # -- Aquí empieza la parte rápida --
    (31.5, "Cutting corners"),
    (32.8, "Like my whole life"),
    
    (34.0, "Backstabbing"),
    (35.0, "BITCHES"),
    (36.0, "With the whole knife"),
    
    (37.5, "Day I die"),
    (38.5, "Only day..."),
    (39.2, "I GHOSTWRITE"),
    
    (40.5, "When I go"),
    (41.5, "Treat me like GOD"),
    (43.0, "If shit goes right")
]

if __name__ == "__main__":
    os.system("mode con: cols=110 lines=35") 
    try:
        reproducir_con_letras(letras)
    except KeyboardInterrupt:
        pygame.mixer.music.stop()