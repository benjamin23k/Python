import tkinter as tk
from tkinter import font
from config import COLOR_BARRA_lateral, COLOR_BARRA_SUPERIOR, COLOR_CUERPO_PRINCIPAL, COLOR_MENU_CURSOR_ENCIMA
import util.util_ventana as util_ventana
import util.util_imagenes as util_imagenes

class FormularioMaestro(tk.Tk): 



    def __init__(self):
        print("Formulario maestro inicializado")
        super().__init__()
        self.logo = util_imagenes.leer_imagen("proyecto/imagenes/logo.png", (5600, 136))
        self.perfil = util_imagenes.leer_imagen("proyecto/imagenes/perfil.png", (100, 100))
    

    def config_window(self):
        self.title("WOX")
        self.iconbitmap("proyecto/imagenes/icono.ico")
        w, h =1024 , 600
        self.geometry("%dx%d+0+0" % (w, h))
        util_ventana.centrar_ventana(self, w, h)

        


        