from machine import UART, Pin
import time

#Librerias
from num_grande import mostrar_dos_digitos, onoff
from control_leds import controlar_led

push = Pin(8, Pin.IN, Pin.PULL_UP)

uart = UART(0, baudrate=115200)
print("Listo para recibir mensajes por UART...")

my_name = "A"
ln = 30
li = 0
#APAGADO
for i in range(0, 60): controlar_led(i, 0, 0, 0)
onoff("off")


#PROCESOS
while True:
    data = uart.read()
    if data != None:
        str_val = str(data)
        val = str_val[2:-1]
        print(val)
        if val == "MALA_UBIC":
            for i in range(li,ln): controlar_led(i, 255, 0, 0) #ROJO
        elif val == "REGRESA":
            for i in range(li, ln):controlar_led(i, 0, 0, 255) #AZUL
        elif val == "OFFER":
            for i in range(0, 60):controlar_led(i, 0, 0, 0) #AZUL
        elif len(val)>4 and val[0] == my_name and val[1].isdigit():
            onoff("on")
            for i in range(0, 60):controlar_led(i, 200, 50, 200)
            mostrar_dos_digitos(int(val[1]))
            while True: 
                push_value = push.value()
                if push_value == 0:
                    time.sleep(0.3)
                    onoff("off")
                    for i in range(0,60): controlar_led(i, 0, 0, 0)
                    break

            
        else:
            try:
                name = val[0]
                pzas = int(val[1:3])
                
                if name != my_name:
                    for i in range(0, 60): controlar_led(i, 0, 0, 0)
                    onoff("off")
                if name == my_name:
                    onoff("on")
                    mostrar_dos_digitos(pzas)
                    for i in range(li,ln): controlar_led(i, 0, 255, 0) #VERDE
                    
                    cont_skus = 0
                    confirm = False
                    while confirm == False:
                        data = uart.read()
                        if cont_skus == pzas:
                            print("confirma")
                            for i in range(li, ln):controlar_led(i, 0, 0, 255) #AZUL
                            push_value = push.value()
                            if push_value == 0:
                                confirm = True
                                time.sleep(0.3)
                                uart.write(f'{my_name}CONFIRM'.encode('utf-8'))
                                print("envie", 'ACONFIRM')
                                onoff("off")
                                data = ""
                                for i in range(0,60): controlar_led(i, 0, 0, 0)
                            
                        if data != None:
                            str_val = str(data)
                            val = str_val[2:-1]
                            if len(val) > 5 and cont_skus < pzas: cont_skus += 1
                            
                else:
                    data = ""
            except: pass

