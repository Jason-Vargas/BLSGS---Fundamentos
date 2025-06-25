"""Interfaz Principal"""

import tkinter as tk
import threading
import server
from fama import salon_fama
from juego import ventana_juego

def interfaz(usuario):
    ventana = tk.Tk()
    ventana.title("Fundamentos de Sistemas")
    ventana.geometry("400x400")
    ventana.configure(bg="lightblue")

    saludo = f"¡Hola, {usuario}!"
    etiqueta = tk.Label(ventana, text=saludo, font=("Arial", 16), bg="lightblue")
    etiqueta.pack(pady=10)

    def iniciar_servidor():
        hilo = threading.Thread(target=server.server, daemon=True)
        hilo.start()

    boton_conectar = tk.Button(ventana, text="Iniciar Servidor", command=iniciar_servidor)
    boton_conectar.pack(pady=10)

    # Etiqueta de estado de conexión
    estado_conexion = tk.Label(ventana, text="🔴 No hay conexión con la Raspberry", fg="red", font=("Arial", 12), bg="lightblue")
    estado_conexion.pack(pady=5)

    # Botón de Jugar (inicialmente desactivado)
    boton_jugar = tk.Button(ventana, text="Jugar", state="disabled", command=lambda: ventana_juego(usuario))

    boton_jugar.pack(pady=10)

    boton_salon_fama = tk.Button(ventana, text="Salón de la Fama", command=salon_fama)
    boton_salon_fama.pack(pady=10)

    boton_salir = tk.Button(ventana, text="Salir", command=ventana.quit)
    boton_salir.pack(pady=10)

    def verificar_conexion():
        if server.client_socket_global:
            try:
                server.client_socket_global.send(b"ping")
                boton_jugar.config(state="normal")
                estado_conexion.config(text="🟢 Conectado con la Raspberry", fg="green")
            except:
                boton_jugar.config(state="disabled")
                estado_conexion.config(text="🔴 No hay conexión con la Raspberry", fg="red")
        else:
            boton_jugar.config(state="disabled")
            estado_conexion.config(text="🔴 No hay conexión con la Raspberry", fg="red")

        ventana.after(1000, verificar_conexion)  # revisa cada segundo

    verificar_conexion()  # Llama al inicio

    ventana.mainloop()
