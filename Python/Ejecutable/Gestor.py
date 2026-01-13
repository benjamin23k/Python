import os
import sqlite3
import random
from cryptography.fernet import Fernet
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, Toplevel

# Generar o cargar clave de cifrado
KEY_FILE = "secret.key"

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()

cipher = Fernet(key)

# Conectar a la base de datos SQLite
conn = sqlite3.connect("password_manager.db")
cursor = conn.cursor()

# Crear tabla de usuarios y contraseñas si no existen
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    service TEXT NOT NULL,
    encrypted_password TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users(username)
)
""")
conn.commit()


# Función para generar OTP
def generate_otp():
    return str(random.randint(100000, 999999))


# Interfaz gráfica (Tkinter)
class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Contraseñas")
        self.root.geometry("400x250")

        Label(root, text="Usuario:").pack()
        self.username_entry = Entry(root)
        self.username_entry.pack()

        Label(root, text="Contraseña:").pack()
        self.password_entry = Entry(root, show="*")
        self.password_entry.pack()

        Button(root, text="Registrar", command=self.register_user).pack()
        Button(root, text="Iniciar Sesión", command=self.login_user).pack()

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "El usuario ya existe")
            return

        encrypted_password = cipher.encrypt(password.encode()).decode()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, encrypted_password))
        conn.commit()
        messagebox.showinfo("Éxito", "Usuario registrado correctamente")

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()

        if result:
            encrypted_password = result[0]
            decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()

            if decrypted_password == password:
                otp = generate_otp()
                messagebox.showinfo("Código OTP", f"Tu código OTP es: {otp}")
                self.verify_otp(username, otp)
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    def verify_otp(self, username, otp):
        otp_window = Toplevel(self.root)
        otp_window.title("Verificar OTP")
        otp_window.geometry("300x150")

        Label(otp_window, text="Introduce el código OTP:").pack()
        otp_var = StringVar()
        Entry(otp_window, textvariable=otp_var).pack()
        Button(otp_window, text="Verificar", command=lambda: self.validate_otp(username, otp, otp_var.get(), otp_window)).pack()

    def validate_otp(self, username, generated_otp, entered_otp, otp_window):
        if generated_otp == entered_otp:
            messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
            otp_window.destroy()
            self.open_dashboard(username)
        else:
            messagebox.showerror("Error", "Código OTP incorrecto")

    def open_dashboard(self, username):
        dashboard = Toplevel(self.root)
        dashboard.title("Gestor de Contraseñas")
        dashboard.geometry("400x300")

        Label(dashboard, text=f"Bienvenido, {username}").pack()
        Label(dashboard, text="Servicio:").pack()
        service_entry = Entry(dashboard)
        service_entry.pack()

        Label(dashboard, text="Contraseña:").pack()
        password_entry = Entry(dashboard, show="*")
        password_entry.pack()

        Button(dashboard, text="Guardar Contraseña", command=lambda: self.save_password(username, service_entry.get(), password_entry.get())).pack()
        Button(dashboard, text="Mostrar Contraseñas", command=lambda: self.show_passwords(username)).pack()

    def save_password(self, username, service, password):
        if not service or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        encrypted_password = cipher.encrypt(password.encode()).decode()
        cursor.execute("INSERT INTO passwords (username, service, encrypted_password) VALUES (?, ?, ?)", (username, service, encrypted_password))
        conn.commit()
        messagebox.showinfo("Éxito", "Contraseña guardada correctamente")

    def show_passwords(self, username):
        cursor.execute("SELECT service, encrypted_password FROM passwords WHERE username=?", (username,))
        passwords = cursor.fetchall()

        if not passwords:
            messagebox.showinfo("Información", "No tienes contraseñas guardadas")
            return

        passwords_window = Toplevel(self.root)
        passwords_window.title("Contraseñas Guardadas")
        passwords_window.geometry("400x300")

        for service, encrypted_password in passwords:
            decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()
            Label(passwords_window, text=f"{service}: {decrypted_password}").pack()


# Ejecutar la aplicación
if __name__ == "__main__":
    root = Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
