"""Salón de la Fama"""

import tkinter as tk
import json
import os

ARCHIVO_USUARIOS = "usuarios.json"

def obtener_top_usuarios(n=5):
    if not os.path.exists(ARCHIVO_USUARIOS):
        return []

    with open(ARCHIVO_USUARIOS, "r") as f:
        usuarios = json.load(f)

    # Convierte a tuplas (usuario, puntaje), omite los que no tengan puntaje válido
    lista_usuarios = []
    for usuario, datos in usuarios.items():
        try:
            puntaje = datos["puntaje"] if isinstance(datos, dict) else 0
            lista_usuarios.append((usuario, puntaje))
        except:
            continue

    # Ordena por puntaje descendente y retorna los top n
    lista_usuarios.sort(key=lambda x: x[1], reverse=True)
    return lista_usuarios[:n]

def salon_fama():
    ventana_fama = tk.Tk()
    ventana_fama.title("Salón de la Fama")
    ventana_fama.geometry("400x350")
    ventana_fama.configure(bg="lightgreen")

    etiqueta_titulo = tk.Label(ventana_fama, text="Salón de la Fama", font=("Arial", 20, "bold"), bg="lightgreen")
    etiqueta_titulo.pack(pady=15)

    top_usuarios = obtener_top_usuarios()

    if top_usuarios:
        for idx, (usuario, puntaje) in enumerate(top_usuarios, start=1):
            texto = f"{idx}. {usuario} - {puntaje} puntos"
            tk.Label(ventana_fama, text=texto, font=("Arial", 14), bg="lightgreen").pack(pady=4)
    else:
        tk.Label(ventana_fama, text="No hay registros aún.", font=("Arial", 14), bg="lightgreen").pack(pady=20)

    tk.Button(ventana_fama, text="Cerrar", command=ventana_fama.destroy).pack(pady=15)

    ventana_fama.mainloop()
