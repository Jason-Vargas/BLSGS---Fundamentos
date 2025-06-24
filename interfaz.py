import tkinter as tk
import threading
import server  # Importas el módulo, no la función

def interfaz():
    ventana = tk.Tk()
    ventana.title("Fundamentos de Sistemas")
    ventana.geometry("800x800")
    ventana.configure(bg="lightblue")

    etiqueta = tk.Label(ventana, text="¡Hola, bienvenido!", font=("Arial", 16), bg="lightblue")
    etiqueta.pack(pady=20)

    def iniciar_servidor():
        hilo = threading.Thread(target=server.server, daemon=True)
        hilo.start()

    boton_conectar = tk.Button(ventana, text="Iniciar Servidor", command=iniciar_servidor)
    boton_conectar.pack(pady=10)

    entrada_mensaje = tk.Entry(ventana, width=40)
    entrada_mensaje.pack(pady=10)

    def enviar_mensaje():
        mensaje = entrada_mensaje.get()
        if server.client_socket_global:
            try:
                server.client_socket_global.sendall(mensaje.encode())
                print("Mensaje enviado:", mensaje)
            except Exception as e:
                print("Error al enviar mensaje:", e)
        else:
            print("No hay cliente conectado")

    boton_enviar = tk.Button(ventana, text="Enviar mensaje al cliente", command=enviar_mensaje)
    boton_enviar.pack(pady=10)

    ventana.mainloop()
