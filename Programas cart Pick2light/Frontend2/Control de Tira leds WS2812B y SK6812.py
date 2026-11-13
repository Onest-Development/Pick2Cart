import machine
import neopixel
import time

#tiras leds WS2812B y SK6812
# Configuración de hardware
PIN_DATOS = 2     # Pin GPIO donde se conecta el DIN de la tira (ej. GPIO14)
NUM_LEDS = 30      # Número total de LEDs en tu tira

# Inicializa la tira LED
tira = neopixel.NeoPixel(machine.Pin(PIN_DATOS), NUM_LEDS)

def controlar_led(indice, r, g, b):
    """Controla un LED específico por su índice (empezando desde 0)"""
    if 0 <= indice < NUM_LEDS:
        tira[indice] = (r, g, b)  # Asigna el color en formato (R, G, B)
        tira.write()              # Envía la señal física a la tira

# Limpiar todos los LEDs al arrancar
tira.fill((0, 0, 0))
tira.write()

# Bucle principal de ejemplo
while True:
    # Ejemplo 1: Encender el primer LED (índice 0) en Rojo
    controlar_led(0, 255, 0, 0)
    time.sleep(0.5)
    
    # Ejemplo 2: Encender el sexto LED (índice 5) en Verde
    controlar_led(5, 0, 255, 0)
    time.sleep(0.5)
    
    # Ejemplo 3: Encender el décimo LED (índice 9) en Azul
    controlar_led(9, 0, 0, 255)
    time.sleep(2)
    
    # Apagar los LEDs configurados antes de reiniciar el bucle
    controlar_led(0, 0, 0, 0)
    controlar_led(5, 0, 0, 0)
    controlar_led(9, 0, 0, 0)
    time.sleep(1)