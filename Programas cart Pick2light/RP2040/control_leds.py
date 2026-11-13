#control leds
import neopixel, time, machine

PIN_DATOS = 2
NUM_LEDS = 60
tira = neopixel.NeoPixel(machine.Pin(PIN_DATOS), NUM_LEDS)

def apagados():
    tira.fill((0, 0, 0))
    tira.write()
    
def prender_por(info):
    for led in info:
        controlar_led(led, 0, 255, 0)

def controlar_led(indice, r, g, b):
    """Controla un LED específico por su índice (empezando desde 0)"""
    if 0 <= indice < NUM_LEDS:
        tira[indice] = (r, g, b)  
        tira.write()
