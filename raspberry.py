from machine import Pin, PWM
import time
import random
import network
import socket
import _thread

# ----------- Configura tu WiFi y servidor aquí -------------
SSID = "Josue"
PASSWORD = "cam2510pos"
SERVER_IP = '192.168.0.17'
PORT = 8001

# -------------------- Variables de estado --------------------
juego_activo = True
reiniciar_pendiente = False
client_socket = None

# Control centralizado para LEDs binarios
modo_leds = 'sets'  # Puede ser 'sets', 'nivel', 'aciertos'
valor_leds = 0

# -------------------- Conexión WiFi --------------------
def connectToWifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Conectando a WiFi...")
        time.sleep(1)
    print("Conectado a WiFi. IP:", wlan.ifconfig()[0])

# -------------------- Conexión al servidor --------------------
def connectToPC():
    global client_socket, juego_activo, reiniciar_pendiente
    try:
        client_socket = socket.socket()
        client_socket.connect((SERVER_IP, PORT))
        print("Conectado al servidor")

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            mensaje = data.decode().strip()
            print("Mensaje recibido:", mensaje)

            if mensaje.startswith("boton"):
                n = int(mensaje[-1]) - 1
                simular_boton_virtual(n)
            elif mensaje == "reiniciar":
                reiniciar_pendiente = True
                juego_activo = False
            elif mensaje.startswith("error"):
                sonar_error()
    except Exception as e:
        print("Error de conexión:", e)

# -------------------- LEDs y botones --------------------
leds = [
    {"led": Pin(15, Pin.OUT), "boton": Pin(12, Pin.IN, Pin.PULL_DOWN)},
    {"led": Pin(20, Pin.OUT), "boton": Pin(19, Pin.IN, Pin.PULL_DOWN)},
    {"led": Pin(14, Pin.OUT), "boton": Pin(10, Pin.IN, Pin.PULL_DOWN)},
    {"led": Pin(18, Pin.OUT), "boton": Pin(21, Pin.IN, Pin.PULL_DOWN)},
]
for item in leds:
    item["led"].off()

# -------------------- Display y binario --------------------
val_led = Pin(5, Pin.OUT)#bit de validacíon
bin_leds = [Pin(28, Pin.OUT), Pin(27, Pin.OUT), Pin(26, Pin.OUT)]
data = Pin(16, Pin.OUT)
clock = Pin(17, Pin.OUT)
digits = [
    "1111101", "0110000", "1101110", "1111010", "0110011",
    "1011011", "1011111", "1110000", "1111111", "1111011",
    "1110111", "0011111", "1001110", "0111101", "1001111", "1000111"
]

def mostrar_binario_simple(valor):
    for i in range(3):
        bit = (valor >> i) & 1
        bin_leds[i].value(bit)

def shift_out_string(bits):
    for bit in reversed(bits):
        data.value(int(bit))
        clock.on()
        clock.off()

def mostrar_digito_simple(n):
    shift_out_string(digits[n % 16])
    try:
        client_socket.send(f"display:{hex(n)[2:].upper()}\n".encode())
    except:
        pass

def actualizar_leds():
    global modo_leds, valor_leds
    # Aplica Exceso-3 solo a los 3 bits menos significativos
    valor_exceso3 = (valor_leds % 8 + 3) % 8
    habilitacion = random.randint(0, 1)  # bit de habilitación aleatorio
    if habilitacion:
        val_led.value(1)  # LED de validación encendido
    else:
        valor_exceso3 = 0
        val_led.value(0)  # LED de validación apagado

    for i in range(3):
        bit = (valor_exceso3 >> i) & 1
        bin_leds[i].value(bit)
# -------------------- Buzzer --------------------
buzzer = PWM(Pin(7))
buzzer.duty_u16(0)

def sonar_buzzer():
    for freq in (523, 659, 784, 1047):
        buzzer.freq(freq)
        buzzer.duty_u16(60000)
        time.sleep(0.1)
    buzzer.duty_u16(0)

def sonar_error():
    for freq, dur in zip((330, 262, 196), (0.2, 0.2, 0.4)):
        buzzer.freq(freq)
        buzzer.duty_u16(50000)
        time.sleep(dur)
    buzzer.duty_u16(0)

def sonar_inicio():
    for freq in (523, 659, 784):
        buzzer.freq(freq)
        buzzer.duty_u16(60000)
        time.sleep(0.15)
    buzzer.duty_u16(0)

# -------------------- Pines de nivel --------------------
niveles = {1: 1000, 2: 500, 3: 200}
nivel_1 = Pin(3, Pin.IN, Pin.PULL_UP)
nivel_2 = Pin(2, Pin.IN, Pin.PULL_UP)
nivel_3 = Pin(0, Pin.IN, Pin.PULL_UP)

def leer_nivel_manual():
    if not nivel_1.value():
        return 1
    if not nivel_2.value():
        return 2
    if not nivel_3.value():
        return 3
    return 0

def parpadear_leds_final():
    for _ in range(6):
        for led in bin_leds:
            led.toggle()
        time.sleep(0.25)
    mostrar_binario_simple(0)

# -------------------- Botones virtuales --------------------
botones_virtuales = [False] * 4

def simular_boton_virtual(idx):
    botones_virtuales[idx] = True

# -------------------- Lógica del juego --------------------
def juego_loop():
    global juego_activo, reiniciar_pendiente, botones_virtuales, modo_leds, valor_leds

    while True:
        if reiniciar_pendiente:
            reiniciar_pendiente = False
            print("Reiniciando juego...")

        juego_activo = True
        nivel = 1
        sets = 0
        aciertos = 0

        # Mostrar sets en display y LEDs
        mostrar_digito_simple(sets)
        modo_leds = 'sets'
        valor_leds = sets
        actualizar_leds()

        sonar_inicio()

        while juego_activo:
            nivel_manual = leer_nivel_manual()
            if nivel_manual and nivel_manual != nivel:
                nivel = nivel_manual
                sets = aciertos = 0
                mostrar_digito_simple(sets)
                modo_leds = 'sets'
                valor_leds = sets
                actualizar_leds()
                sonar_inicio()

            tiempo_max = niveles[nivel]

            if nivel == 3:
                i1 = random.randint(0, 3)
                i2 = i1
                while i2 == i1:
                    i2 = random.randint(0, 3)
                seleccionados = [leds[i1], leds[i2]]
                idxs = [i1, i2]
            else:
                idx = random.randint(0, 3)
                seleccionados = [leds[idx]]
                idxs = [idx]

            for s in seleccionados:
                s["led"].on()

            inicio = time.ticks_ms()
            presionado = False
            error = False

            while time.ticks_diff(time.ticks_ms(), inicio) < tiempo_max:
                for i, l in enumerate(leds):
                    if i in idxs and l["boton"].value():
                        presionado = True
                        break
                    if i not in idxs and l["boton"].value():
                        error = True
                        sonar_error()
                        time.sleep(0.5)
                        break

                for i in idxs:
                    if botones_virtuales[i]:
                        presionado = True
                        botones_virtuales[i] = False

                for i in range(4):
                    if i not in idxs and botones_virtuales[i]:
                        error = True
                        botones_virtuales[i] = False
                        sonar_error()

                if presionado or error:
                    break

            for s in seleccionados:
                s["led"].off()

            if error:
                try:
                    client_socket.send("error".encode())
                except:
                    pass
                sets = 0
                mostrar_digito_simple(sets)
                modo_leds = 'sets'
                valor_leds = sets
                actualizar_leds()
                juego_activo = False
                break

            if presionado:
                aciertos += 1
                try:
                    client_socket.send("acierto".encode())
                except:
                    pass
                sonar_buzzer()
                print("Aciertos:", aciertos)
                time.sleep(0.2)

            if aciertos > 0 and aciertos % 5 == 0:
                sets += 1
                aciertos = 0
                mostrar_digito_simple(sets)
                modo_leds = 'sets'
                valor_leds = sets
                actualizar_leds()
                parpadear_leds_final()
                sonar_inicio()
                time.sleep(0.5)

                if nivel == 1 and sets == 5:
                    nivel = 2
                elif nivel == 2 and sets == 7:
                    nivel = 3
                elif nivel == 3 and sets == 3:
                    nivel = 1
                sonar_inicio()

            # Actualizar LEDs según modo y valor actuales
            actualizar_leds()

            time.sleep(0.5)

# -------------------- Iniciar --------------------
connectToWifi()
_thread.start_new_thread(connectToPC, ())
sonar_inicio()
juego_loop()
