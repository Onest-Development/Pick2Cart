from machine import Pin, I2C
import ssd1306
import time

i2c = I2C(scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

segmentos = {
    0:[1, 1, 1, 1, 1, 1, 0],
    1:[0, 1, 1, 0, 0, 0, 0],
    2:[1, 1, 0, 1, 1, 0, 1],
    3:[1, 1, 1, 1, 0, 0, 1],
    4:[0, 1, 1, 0, 0, 1, 1],
    5:[1, 0, 1, 1, 0, 1, 1],
    6:[1, 0, 1, 1, 1, 1, 1],
    7:[1, 1, 1, 0, 0, 0, 0],
    8:[1, 1, 1, 1, 1, 1, 1],
    9: [1, 1, 1, 1, 0, 1, 1]
}

def onoff(val):
    if val == "on":oled.poweron()
    else: oled.poweroff()
    

def dibujar_digito(x, y, num):
    """Dibuja un único dígito gigante de 45x60 píxeles usando rectángulos"""
    seg = segmentos[num]
    w = 40  # Ancho del dígito
    h = 60  # Alto del dígito
    t = 6   # Grosor de las líneas
    
    # Segmento A (Top)
    if seg[0]: oled.fill_rect(x, y, w, t, 1)
    # Segmento B (Arriba Derecha)
    if seg[1]: oled.fill_rect(x + w - t, y, t, h // 2, 1)
    # Segmento C (Abajo Derecha)
    if seg[2]: oled.fill_rect(x + w - t, y + h // 2, t, h // 2, 1)
    # Segmento D (Bottom)
    if seg[3]: oled.fill_rect(x, y + h - t, w, t, 1)
    # Segmento E (Abajo Izquierda)
    if seg[4]: oled.fill_rect(x, y + h // 2, t, h // 2, 1)
    # Segmento F (Arriba Izquierda)
    if seg[5]: oled.fill_rect(x, y, t, h // 2, 1)
    # Segmento G (Centro)
    if seg[6]: oled.fill_rect(x, y + (h // 2) - (t // 2), w, t, 1)

def mostrar_dos_digitos(numero):
    """Divide un número de dos dígitos y los renderiza en la pantalla"""
    oled.fill(0)    
    # Asegurar que el número esté entre 00 y 99
    numero = max(0, min(99, numero))
    decena = numero // 10
    unidad = numero % 10
    # Dibujar primer dígito (X=15, Y=2)
    dibujar_digito(15, 2, decena)
    # Dibujar segundo dígito (X=73, Y=2)
    dibujar_digito(73, 2, unidad)
    oled.show()
