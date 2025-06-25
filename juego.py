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

def guardar_puntaje(usuario, puntaje_nuevo):
    usuarios = leer_usuarios()

    if usuario in usuarios:
        if isinstance(usuarios[usuario], str):
            usuarios[usuario] = {"clave": usuarios[usuario], "puntaje": 0}
        puntaje_actual = usuarios[usuario].get("puntaje", 0)
        if puntaje_nuevo > puntaje_actual:
            usuarios[usuario]["puntaje"] = puntaje_nuevo
    else:
        usuarios[usuario] = {"clave": "", "puntaje": puntaje_nuevo}

    with open(ARCHIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)

def ventana_juego(usuario):
    juego = tk.Toplevel()
    juego.title("Interfaz del Juego")
    juego.geometry("300x480")
    juego.configure(bg="white")

    etiqueta = tk.Label(juego, text=f"Jugador: {usuario}", font=("Arial", 14), bg="white")
    etiqueta.pack(pady=10)

    puntaje = tk.IntVar(value=0)

    label_puntaje = tk.Label(juego, text=f"Puntaje: {puntaje.get()}", font=("Arial", 14), fg="green", bg="white")
    label_puntaje.pack(pady=5)

    def actualizar_puntaje(*args):
        if label_puntaje.winfo_exists():
            label_puntaje.config(text=f"Puntaje: {puntaje.get()}")

    trace_id = puntaje.trace_add("write", actualizar_puntaje)

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

    detener_escucha = threading.Event()

    def mostrar_error_y_salir():
        def animar_error():
            if status_label.winfo_exists():
                status_label.config(text="❌ Botón incorrecto", fg="red")
            if winsound:
                winsound.Beep(500, 150)
            time.sleep(0.3)
            if status_label.winfo_exists():
                status_label.config(text="")
            time.sleep(0.3)
            guardar_puntaje(usuario, puntaje.get())
            detener_escucha.set()
            if juego.winfo_exists():
                juego.destroy()

        threading.Thread(target=animar_error, daemon=True).start()

    def escuchar_mensajes():
        sock = server.client_socket_global
        while not detener_escucha.is_set():
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

    frame_botones = tk.Frame(juego, bg="white")
    frame_botones.pack(pady=10)

    for i in range(4):
        fila = i // 2
        col = i % 2
        boton = tk.Button(frame_botones, text=f"Botón {i+1}", font=("Arial", 12),
                          command=lambda n=i+1: enviar_boton(n), width=10, height=2)
        boton.grid(row=fila, column=col, padx=10, pady=10)

    def cerrar_ventana():
        puntaje.trace_remove("write", trace_id)
        guardar_puntaje(usuario, puntaje.get())
        detener_escucha.set()
        juego.destroy()

    btn_cerrar = tk.Button(juego, text="Cerrar", font=("Arial", 11), command=cerrar_ventana)
    btn_cerrar.pack(pady=10)

    threading.Thread(target=escuchar_mensajes, daemon=True).start()

    def manejar_tecla(event):
        if event.char in "1234":
            enviar_boton(int(event.char))

    juego.bind("<Key>", manejar_tecla)
    juego.focus_set()

