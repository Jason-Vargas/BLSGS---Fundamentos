import tkinter as tk
import threading
import server
import platform
import time
import json
from login import *

ARCHIVO_USUARIOS = "usuarios.json"

# Sonido en Windows
if platform.system() == "Windows":
    import winsound
else:
    winsound = None

def guardar_puntaje(usuario, puntaje):
    usuarios = leer_usuarios()

    if usuario in usuarios:
        if isinstance(usuarios[usuario], str):
            usuarios[usuario] = {"clave": usuarios[usuario], "puntaje": 0}
        usuarios[usuario]["puntaje"] = puntaje
    else:
        usuarios[usuario] = {"clave": "", "puntaje": puntaje}

    with open(ARCHIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)

def ventana_juego(usuario):
    juego = tk.Toplevel()
    juego.title("Interfaz del Juego")
    juego.geometry("300x480")  # un poco más alto para el display
    juego.configure(bg="white")

    etiqueta = tk.Label(juego, text=f"Jugador: {usuario}", font=("Arial", 14), bg="white")
    etiqueta.pack(pady=10)

    puntaje = tk.IntVar(value=0)

    label_puntaje = tk.Label(juego, text=f"Puntaje: {puntaje.get()}", font=("Arial", 14), fg="green", bg="white")
    label_puntaje.pack(pady=5)

    def actualizar_puntaje(*args):
        label_puntaje.config(text=f"Puntaje: {puntaje.get()}")
    puntaje.trace_add("write", actualizar_puntaje)

    # Etiqueta para mostrar el valor actual del display 7 segmentos
    display_valor = tk.StringVar(value="0")
    label_display = tk.Label(juego, textvariable=display_valor, font=("Arial", 48), fg="blue", bg="white")
    label_display.pack(pady=20)

    status_label = tk.Label(juego, text="", font=("Arial", 12), fg="red", bg="white")
    status_label.pack(pady=10)

    def enviar_boton(n):
        if server.client_socket_global:
            try:
                mensaje = f"boton{n}"
                server.client_socket_global.send(mensaje.encode())
                print(f"Enviado: {mensaje}")
            except:
                print("Error al enviar comando.")

    def mostrar_error_y_salir():
        def animar_error():
            for _ in range(1):
                status_label.config(text="❌ Botón incorrecto", fg="red")
                if winsound:
                    winsound.Beep(500, 150)
                juego.update()
                time.sleep(0.3)
                status_label.config(text="")
                juego.update()
                time.sleep(0.3)
            guardar_puntaje(usuario, puntaje.get())
            juego.destroy()  # cerrar ventana tras error

        threading.Thread(target=animar_error, daemon=True).start()

    def escuchar_mensajes():
        sock = server.client_socket_global
        while True:
            if sock:
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    mensaje = data.decode().strip()
                    print("Mensaje recibido en GUI:", mensaje)

                    if mensaje == "error":
                        mostrar_error_y_salir()
                        break
                    elif mensaje == "acierto":
                        puntaje.set(puntaje.get() + 1)
                    elif mensaje.startswith("display:"):
                        valor = mensaje.split(":", 1)[1].strip()
                        display_valor.set(valor)
                except Exception as e:
                    print("Error al recibir mensaje en GUI:", e)
                    break
            else:
                break

    for i in range(1, 5):
        boton = tk.Button(juego, text=f"Botón {i}", font=("Arial", 12),
                            command=lambda n=i: enviar_boton(n), width=15)
        boton.pack(pady=5)

    btn_cerrar = tk.Button(juego, text="Cerrar", font=("Arial", 11),
                            command=lambda: [guardar_puntaje(usuario, puntaje.get()), juego.destroy()])
    btn_cerrar.pack(pady=10)

    threading.Thread(target=escuchar_mensajes, daemon=True).start()

