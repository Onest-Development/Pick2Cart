import serial, time

puerto_serial = 'COM9'
baudios = 115200

try:
    esp = serial.Serial(puerto_serial, baudios, timeout=1)
    while True:
        mensaje_a_enviar = input("Escribe algo\n")

        if mensaje_a_enviar == "CERRAR": break
        esp.write(mensaje_a_enviar.encode('utf-8'))
        print(f"Mensaje enviado: {mensaje_a_enviar.strip()}")

        if len(mensaje_a_enviar) > 5:
            print("entramos a loop")
            while True:
                #if esp.in_waiting > 0:
                datos = esp.readline(8).decode("utf-8")
                print(datos)
                if datos:

                    break
    esp.close()

except serial.SerialException as e:
    print(f"Error de conexión: {e}")