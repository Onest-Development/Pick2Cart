import serial, time

PUERTO = "COM9"
BAUDRATE = 115200


puerto_serie = serial.Serial(PUERTO, BAUDRATE)
print(f"Escuchando en {PUERTO} a {BAUDRATE} baudios... (Ctrl+C para salir)\n")

# Bucle de lectura
while True:

    #mensaje_a_enviar = input("Escribe algo\n")
    #puerto_serie.write(mensaje_a_enviar.encode('utf-8'))

    if puerto_serie.in_waiting > 0:
        #while True:
        datos = puerto_serie.readline(6)
        if datos:
            print(f"Recibido: {datos}")



