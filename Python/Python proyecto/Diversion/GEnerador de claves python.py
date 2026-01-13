import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import random
import hashlib
import datetime  # Importar para obtener el año actual

letras = "qwertyuiopasdfghjklzxcvbnm"
numeros = "1234567890"
simbolos = "!@#$%^&*()"

# Base de datos
def inicializar_base_datos():
    """Inicializa la base de datos SQLite para almacenar contraseñas y usuarios."""
    conexion = sqlite3.connect("gestor_contrasenas.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contrasenas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servicio TEXT NOT NULL,
            usuario TEXT NOT NULL,
            contrasena TEXT NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()

def encriptar_contrasena(contrasena):
    """Encripta una contraseña utilizando SHA-256."""
    return hashlib.sha256(contrasena.encode()).hexdigest()

def registrar_usuario(usuario, contrasena):
    """Registra un nuevo usuario en la base de datos."""
    conexion = sqlite3.connect("gestor_contrasenas.db")
    cursor = conexion.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", 
                       (usuario, encriptar_contrasena(contrasena)))
        conexion.commit()
        messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El usuario ya existe.")
    finally:
        conexion.close()

def verificar_usuario(usuario, contrasena):
    """Verifica si las credenciales del usuario son correctas."""
    conexion = sqlite3.connect("gestor_contrasenas.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT contrasena FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conexion.close()
    if resultado and resultado[0] == encriptar_contrasena(contrasena):
        return True
    return False

def mostrar_login():
    """Muestra la ventana de inicio de sesión con un diseño moderno y ajustable."""
    def iniciar_sesion():
        usuario = usuario_entry.get().strip()
        contrasena = contrasena_entry.get().strip()
        if verificar_usuario(usuario, contrasena):
            login_ventana.destroy()
            mostrar_aplicacion()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def registrar():
        """Registra un nuevo usuario si los campos no están vacíos y el usuario no existe."""
        usuario = usuario_entry.get().strip()
        contrasena = contrasena_entry.get().strip()
        if usuario and contrasena:  # Verificar que ambos campos no estén vacíos
            if verificar_usuario(usuario, contrasena):
                messagebox.showerror("Error", "El usuario ya existe.")
            else:
                registrar_usuario(usuario, contrasena)
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

    # Crear ventana de login
    login_ventana = tk.Tk()
    login_ventana.title("Inicio de Sesión")
    login_ventana.geometry("600x450")  # Tamaño inicial ajustado para mostrar todas las opciones
    login_ventana.resizable(True, True)  # Permitir cambiar tamaño
    login_ventana.config(bg="#e6e6e6")  # Fondo gris claro

    # Contenedor principal
    frame_principal = tk.Frame(login_ventana, bg="#ffffff", padx=20, pady=20, relief="groove", bd=2)
    frame_principal.pack(expand=True, fill="both", padx=50, pady=50)

    # Título
    titulo_label = tk.Label(frame_principal, text="Inicio de Sesión", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333")
    titulo_label.pack(pady=20)

    # Campo de usuario
    ttk.Label(frame_principal, text="Usuario:", background="#ffffff").pack(pady=5, anchor="w")
    usuario_entry = ttk.Entry(frame_principal, font=("Arial", 14))
    usuario_entry.pack(pady=5, fill="x")

    # Campo de contraseña
    ttk.Label(frame_principal, text="Contraseña:", background="#ffffff").pack(pady=5, anchor="w")
    contrasena_entry = ttk.Entry(frame_principal, show="*", font=("Arial", 14))
    contrasena_entry.pack(pady=5, fill="x")

    # Botones de acción
    boton_iniciar = ttk.Button(frame_principal, text="Iniciar Sesión", command=iniciar_sesion)
    boton_iniciar.pack(pady=15, fill="x")

    boton_registrar = ttk.Button(frame_principal, text="Registrar", command=registrar)
    boton_registrar.pack(pady=5, fill="x")

    # Pie de página con el año actual
    anio_actual = datetime.datetime.now().year
    pie_label = tk.Label(frame_principal, text=f"© {anio_actual} Gestor de Contraseñas", font=("Arial", 10), bg="#ffffff", fg="#666666")
    pie_label.pack(pady=20)

    login_ventana.mainloop()

def mostrar_todas_las_contrasenas():
    """Muestra todas las contraseñas guardadas en una ventana separada."""
    ventana_contrasenas = tk.Toplevel()
    ventana_contrasenas.title("Todas las Contraseñas")
    ventana_contrasenas.geometry("600x400")
    ventana_contrasenas.resizable(False, False)

    columnas = ("ID", "Servicio", "Usuario", "Contraseña")
    tree = ttk.Treeview(ventana_contrasenas, columns=columnas, show="headings")
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def cargar_contrasenas():
        """Carga todas las contraseñas en el Treeview."""
        conexion = sqlite3.connect("gestor_contrasenas.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, servicio, usuario, contrasena FROM contrasenas")
        contrasenas = cursor.fetchall()
        conexion.close()

        for item in tree.get_children():
            tree.delete(item)

        for id_, servicio, usuario, contrasena in contrasenas:
            tree.insert("", "end", values=(id_, servicio, usuario, contrasena))

    cargar_contrasenas()

def mostrar_aplicacion():
    """Muestra la ventana principal de la aplicación."""
    ventana = tk.Tk()
    ventana.geometry("700x600")
    ventana.title("Administrador y Gestor de Contraseñas")

    # Crear menú
    menu_bar = tk.Menu(ventana)
    ventana.config(menu=menu_bar)

    menu_opciones = tk.Menu(menu_bar, tearoff=0)
    menu_opciones.add_command(label="Ver todas las contraseñas", command=mostrar_todas_las_contrasenas)
    menu_bar.add_cascade(label="Opciones", menu=menu_opciones)

    # Frame para generar contraseñas
    frame_generar = ttk.LabelFrame(ventana, text="Generar Contraseña")
    frame_generar.pack(fill="x", padx=10, pady=10)

    ttk.Label(frame_generar, text="Longitud:").grid(row=0, column=0, padx=5, pady=5)
    numero_letras = ttk.Entry(frame_generar)
    numero_letras.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_generar, text="Solo letras:").grid(row=1, column=0, padx=5, pady=5)
    solo_letras_var = tk.BooleanVar()
    solo_letras_check = ttk.Checkbutton(frame_generar, variable=solo_letras_var)
    solo_letras_check.grid(row=1, column=1, padx=5, pady=5)

    def generar_clave():
        """Genera una contraseña aleatoria."""
        try:
            longitud = numero_letras.get().strip()
            longitud = int(longitud) if longitud else 8  # Longitud predeterminada de 8 si no se ingresa nada
            if longitud <= 0:
                raise ValueError("La longitud debe ser un número positivo.")
            if longitud > 100:  # Limitar la longitud máxima a 100 caracteres
                raise ValueError("La longitud máxima permitida es 100 caracteres.")
            caracteres = letras if solo_letras_var.get() else letras + numeros + simbolos
            clave = "".join(random.choice(caracteres) for _ in range(longitud))
            resultado_label.config(text="Clave generada: " + clave)
            boton_copiar.config(state=tk.NORMAL)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    boton_generar = ttk.Button(frame_generar, text="Generar", command=generar_clave)
    boton_generar.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    resultado_label = ttk.Label(frame_generar, text="")
    resultado_label.grid(row=3, column=0, columnspan=3, pady=5)

    def copiar_clave():
        """Copia la clave generada al portapapeles."""
        clave = resultado_label.cget("text").replace("Clave generada: ", "").strip()
        if clave:
            ventana.clipboard_clear()
            ventana.clipboard_append(clave)
            ventana.update()
            messagebox.showinfo("Éxito", "Clave copiada al portapapeles.")
        else:
            messagebox.showwarning("Advertencia", "No hay ninguna clave generada para copiar.")

    boton_copiar = ttk.Button(frame_generar, text="Copiar", command=copiar_clave, state=tk.DISABLED)
    boton_copiar.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    # Frame para guardar contraseñas
    frame_guardar = ttk.LabelFrame(ventana, text="Guardar Contraseña")
    frame_guardar.pack(fill="x", padx=10, pady=10)

    ttk.Label(frame_guardar, text="Servicio:").grid(row=0, column=0, padx=5, pady=5)
    servicio_entry = ttk.Entry(frame_guardar)
    servicio_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_guardar, text="Usuario:").grid(row=1, column=0, padx=5, pady=5)
    usuario_entry = ttk.Entry(frame_guardar)
    usuario_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frame_guardar, text="Contraseña:").grid(row=2, column=0, padx=5, pady=5)
    contrasena_entry = ttk.Entry(frame_guardar)
    contrasena_entry.grid(row=2, column=1, padx=5, pady=5)

    def guardar_contrasena():
        """Guarda una contraseña en la base de datos."""
        servicio = servicio_entry.get().strip()
        usuario = usuario_entry.get().strip()
        contrasena = contrasena_entry.get().strip()
        if servicio and usuario and contrasena:
            conexion = sqlite3.connect("gestor_contrasenas.db")
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO contrasenas (servicio, usuario, contrasena) VALUES (?, ?, ?)", 
                           (servicio, usuario, contrasena))
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", "Contraseña guardada exitosamente.")
            servicio_entry.delete(0, tk.END)
            usuario_entry.delete(0, tk.END)
            contrasena_entry.delete(0, tk.END)
            ver_contrasenas()  # Actualizar el Treeview
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

    boton_guardar = ttk.Button(frame_guardar, text="Guardar", command=guardar_contrasena)
    boton_guardar.grid(row=3, column=0, columnspan=2, pady=10)

    # Frame para ver y eliminar contraseñas
    frame_ver = ttk.LabelFrame(ventana, text="Contraseñas Guardadas")
    frame_ver.pack(fill="both", expand=True, padx=10, pady=10)

    columnas = ("ID", "Servicio", "Usuario", "Contraseña")
    tree = ttk.Treeview(frame_ver, columns=columnas, show="headings")
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True, pady=10)

    def ver_contrasenas():
        """Muestra todas las contraseñas almacenadas en el Treeview."""
        conexion = sqlite3.connect("gestor_contrasenas.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, servicio, usuario, contrasena FROM contrasenas")
        contrasenas = cursor.fetchall()
        conexion.close()
        
        for item in tree.get_children():
            tree.delete(item)
        
        for id_, servicio, usuario, contrasena in contrasenas:
            tree.insert("", "end", values=(id_, servicio, usuario, contrasena))

    def eliminar_contrasena():
        """Elimina una contraseña seleccionada en el Treeview."""
        seleccion = tree.selection()
        if seleccion:
            id_contrasena = tree.item(seleccion[0], "values")[0]  # Obtener el ID de la contraseña seleccionada
            conexion = sqlite3.connect("gestor_contrasenas.db")
            cursor = conexion.cursor()
            try:
                cursor.execute("DELETE FROM contrasenas WHERE id = ?", (id_contrasena,))
                conexion.commit()
                conexion.close()
                messagebox.showinfo("Éxito", "Contraseña eliminada exitosamente.")
                ver_contrasenas()  # Actualizar el Treeview
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la contraseña: {e}")
        else:
            messagebox.showwarning("Advertencia", "Selecciona una contraseña para eliminar.")

    boton_eliminar = ttk.Button(frame_ver, text="Eliminar Seleccionada", command=eliminar_contrasena)
    boton_eliminar.pack(pady=5)

    ver_contrasenas()  # Cargar contraseñas al iniciar
    ventana.mainloop()

# Mostrar la ventana de inicio de sesión
inicializar_base_datos()
mostrar_login()
