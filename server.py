"""Sistema de conexión de servidor"""
import socket

client_socket_global = None  # Este será accesible desde fuera

def server():
    global client_socket_global
    server_address = ('192.168.0.17', 8001)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind(server_address)
        server_socket.listen(1)
        print("Servidor iniciado. Escuchando en {}:{}".format(*server_address))
    except OSError as e:
        print("Error al iniciar el servidor:", e)
        return

    while True:
        try:
            print("Esperando conexiones entrantes...")
            client_socket, client_address = server_socket.accept()
            client_socket_global = client_socket  # Guardamos el socket globalmente
            print("Conexión establecida desde {}".format(client_address))

            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                print("Mensaje recibido:", data.decode())
                # Aquí puedes responder automáticamente si querés

        except Exception as e:
            print("Error:", e)
            break

    server_socket.close()