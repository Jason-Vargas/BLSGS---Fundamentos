import pygame
import threading

def reproducir_musica():
    def _musica_en_bucle():
        pygame.mixer.init()
        pygame.mixer.music.load("Sonidos//fondo.mp3")  # Asegúrate de que esté en la misma carpeta
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(loops=-1)  # Repetir indefinidamente

    threading.Thread(target=_musica_en_bucle, daemon=True).start()