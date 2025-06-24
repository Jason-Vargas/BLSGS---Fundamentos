"""Salón de la Fama"""

import tkinter as tk

def salon_fama():
    ventana_fama = tk.Tk()
    ventana_fama.title("Salón de la Fama")
    ventana_fama.geometry("600x400")
    ventana_fama.configure(bg="lightgreen")

    etiqueta_titulo = tk.Label(ventana_fama, text="Salón de la Fama", font=("Arial", 24), bg="lightgreen")
    etiqueta_titulo.pack(pady=20)

    # Aquí podrías agregar una lista o tabla con los nombres y puntajes
    etiqueta_instrucciones = tk.Label(ventana_fama, text="Próximamente...", font=("Arial", 16), bg="lightgreen")
    etiqueta_instrucciones.pack(pady=10)

    ventana_fama.mainloop()