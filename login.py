"""Sistema de Login"""

import tkinter as tk
from tkinter import messagebox
import os
import json

ARCHIVO_USUARIOS = "usuarios.json"

def leer_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        return {}
    with open(ARCHIVO_USUARIOS, "r") as f:
        return json.load(f)

def guardar_usuario(usuario, clave):
    usuarios = leer_usuarios()
    usuarios[usuario] = {"clave": clave, "puntaje": 0}
    with open(ARCHIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)


def ventana_login(callback_al_loguear):
    def mostrar_registro():
        login.destroy()
        ventana_registro(callback_al_loguear)

    def seleccionar_icono(valor):
        icono_seleccionado.set(valor)
        for boton in botones_icono.values():
            boton.config(relief=tk.RAISED)
        botones_icono[valor].config(relief=tk.SUNKEN)


    def verificar_login():
        usuario = entrada_usuario.get()
        clave = entrada_clave.get()
        usuarios = leer_usuarios()

        if usuario in usuarios and usuarios[usuario]["clave"] == clave:
            messagebox.showinfo("Éxito", f"Inicio de sesión exitoso con ícono '{icono_seleccionado.get()}'")
            login.destroy()
            callback_al_loguear(usuario)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    login = tk.Tk()
    login.title("Login")
    login.geometry("300x280")
    login.configure(bg="#e0f7fa")

    tk.Label(login, text="Usuario:", bg="#e0f7fa").pack(pady=5)
    entrada_usuario = tk.Entry(login)
    entrada_usuario.pack()

    tk.Label(login, text="Contraseña:", bg="#e0f7fa").pack(pady=5)
    entrada_clave = tk.Entry(login, show="*")
    entrada_clave.pack()

    # Selección de ícono
    tk.Label(login, text="Selecciona un ícono:", bg="#e0f7fa").pack(pady=5)
    icono_seleccionado = tk.StringVar(value="🙂")
    frame_iconos = tk.Frame(login, bg="#e0f7fa")
    frame_iconos.pack()

    iconos = ["🙂", "🐱", "🚀"]
    botones_icono = {}

    for icono in iconos:
        btn = tk.Button(frame_iconos, text=icono, font=("Arial", 16), width=4,
                        command=lambda i=icono: seleccionar_icono(i))
        btn.pack(side=tk.LEFT, padx=5)
        botones_icono[icono] = btn

    # Botones de acción
    tk.Button(login, text="Iniciar sesión", command=verificar_login).pack(pady=10)
    tk.Button(login, text="Registrarse", command=mostrar_registro).pack(pady=5)

    login.mainloop()

def ventana_registro(callback_al_registrar):
    def registrar_usuario():
        usuario = entrada_usuario.get()
        clave = entrada_clave.get()
        usuarios = leer_usuarios()

        if usuario in usuarios:
            messagebox.showerror("Error", "El usuario ya existe")
        elif not usuario or not clave:
            messagebox.showerror("Error", "Usuario y contraseña requeridos")
        else:
            guardar_usuario(usuario, clave)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            registro.destroy()
            callback_al_registrar(usuario)

    registro = tk.Tk()
    registro.title("Registro")
    registro.geometry("300x200")
    registro.configure(bg="#fce4ec")

    tk.Label(registro, text="Nuevo usuario:", bg="#fce4ec").pack(pady=5)
    entrada_usuario = tk.Entry(registro)
    entrada_usuario.pack()

    tk.Label(registro, text="Nueva contraseña:", bg="#fce4ec").pack(pady=5)
    entrada_clave = tk.Entry(registro, show="*")
    entrada_clave.pack()

    tk.Button(registro, text="Registrar", command=registrar_usuario).pack(pady=10)
