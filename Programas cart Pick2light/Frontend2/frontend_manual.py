import customtkinter as ctk
from tkinter import messagebox
import serial, time

#libreria a quitar
import one_descarga

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pick to Light Cart - Simulación WMS/Cart")
        self.geometry("500x350")
        self.resizable(False, False)

        #COMUNICACION UART
        self.puerto_serial = 'COM9'
        self.baudios = 115200


        #VARIABLES GENERALES
        self.oleada = None
        self.compartimiento = ["A", "B", "C", "D"]
        self.doc = {"trabajador":""}
        self.skus_conts = 0
        self.scan = 0
        self.turn_doc = 0

        #PROCESO
        self.comunicacion()
        self.frame_nss()

    def comunicacion(self, mensaje="OFFER"):
        self.esp = serial.Serial(self.puerto_serial, self.baudios, timeout=1)
        self.esp.write(mensaje.encode('utf-8'))

        respuesta = self.esp.readline().decode('utf-8').strip()
        if respuesta:
            print(f"Respuesta del ESP8266: {respuesta}")

        self.esp.close()

    def frame_nss(self):
        self.frame_trabajador = ctk.CTkFrame(self,fg_color="green")
        self.frame_trabajador.pack(fill="both", expand=True, padx=5, pady=5)

        msg="PICK 2 LIGHT CART\n\nEscanea tu NSS\n"
        self.title_label = ctk.CTkLabel(self.frame_trabajador, text=msg)
        self.title_label.pack(expand = True)

        self.entry_trabajador = ctk.CTkEntry(self.frame_trabajador)
        self.entry_trabajador.pack(expand = True)
        self.entry_trabajador.bind("<Return>", self.evento_enter)

    def evento_enter(self, event):
        no_trabajador = self.entry_trabajador.get()
        print(no_trabajador)
        self.entry_trabajador.delete(0, 'end')
        #AQUI TRABAJAMOS EL EVENTO

        if len(no_trabajador) <= 10:
            msg = "Numero de Seguro Social incorrecto\nIntente nuevamente"
            messagebox.showwarning(title="WARNING NSS", message=msg)
        else:
            self.frame_trabajador.pack_forget()
            self.frame_general = ctk.CTkFrame(self,fg_color="Blue")
            self.frame_general.pack(fill="both", expand=True)

            self.descargar_oleadas()

    #PROCESO OLEADA
    def descargar_oleadas(self):
        oleada = one_descarga.QA()
        if oleada:
            self.oleada = oleada
            self.nombre_oleada = self.oleada['Oleada']
            self.orden_compartimiento = {}
            for i in range(0,4):
                pedido = oleada['Pedidos'][i]['Pedido']
                comp = self.compartimiento[i]
                self.orden_compartimiento[pedido]=comp
                #print(comp,pedido)
            self.looper()

    #CONTROL DE FRAMES
    def looper(self):
        print("LOOPER")
        print(self.skus_conts, len(self.oleada['Recorrido']))
        if self.skus_conts >= len(self.oleada['Recorrido']):
            self.frame_general.pack_forget()
            self.entregar()

        else:
            print(self.orden_compartimiento)
            print("AQUI ES DONDE TRABAJAMOS DE JSON")
            self.oneBone = self.oleada['Recorrido'][self.skus_conts]
            pick = self.oneBone
            pedido = self.oneBone['Pedido']
            ubic = pick['pasillo']+pick['lado']+pick['nivel']+pick['fondo']
            p = pick['pasillo']
            l = pick['lado']
            x = pick['fondo']
            y = pick['nivel']

            print(ubic, pick)
            self.frame_proceso_pick(pedido, p, l, x, y)

    #PROCESO DE PASILLO
    def frame_proceso_pick(self,pedido, p, l, x, y):
        #Trabajo superior
        pedido=pedido
        self.pasillo=p
        self.ubic = f"P{self.pasillo}L{l}X{x}Y{y}"
        self.ubic_show = f"P{self.pasillo}-L{l}-Fondo{x}-Nivel{y}"
        msg=f"Pedido {pedido}\nPASILLO {self.pasillo}\n\nUbic: {self.ubic_show}"
        self.titulo1 = ctk.CTkLabel(self.frame_general,text=msg, fg_color="transparent")
        self.titulo1.pack(fill="both", expand=True, pady=10)

        #trabajo entry ubicacion
        self.entry_ubic = ctk.CTkEntry(self.frame_general)
        self.entry_ubic.pack(expand=True)
        self.entry_ubic.bind("<Return>", self.evento_ubic)

    def evento_ubic(self, event):
        ubic = self.entry_ubic.get()
        self.entry_ubic.delete(0, 'end')
        print(ubic)
        #AQUI TRABAJAMOS EL EVENTO
        if str(ubic) != self.ubic:
            print(self.ubic)
            self.comunicacion(mensaje="MALA_UBIC")
            msg = "Ubicacion erronea"
            messagebox.showwarning(title="WARNING UBICACION", message=msg)
        else:
            self.entry_ubic.destroy()
            self.comunicacion()
            print("AHORA HAY QUE ESCANEAR LOS SKUS")
            self.skus()

    def skus(self):
        print("AQUI HAY QUE MANDAR INFO DE EN DONDE DEBE DE IR EL")
        self.art = self.oleada['Recorrido'][self.skus_conts]
        self.sku = self.art['sku']
        self.cart_pos = self.orden_compartimiento[self.art['Pedido']]
        self.pzas = self.art['CANT_PED']
        #ENVIO A CART
        self.comunicacion(mensaje=f"{self.cart_pos}{self.pzas}")
        msg = f" SKU: {self.sku}\nPZAS: {self.pzas}  SCAN: {self.scan}"
        self.titulo_sku= ctk.CTkLabel(self.frame_general,text=msg)
        self.titulo_sku.pack(expand=True,pady=2)

        self.entry_sku=ctk.CTkEntry(self.frame_general)
        self.entry_sku.pack(fill='both',expand=True, padx=1, pady=1)
        self.entry_sku.bind("<Return>", self.evento_sku)


    def evento_sku(self, event):
        sku_read = self.entry_sku.get()
        self.entry_sku.delete(0, 'end')

        #AQUI TRABAJAMOS EL EVENTO
        if str(sku_read) == str(self.sku):
            self.scan += 1
            msg = f" SKU: {self.sku}    PZAS: {self.pzas}  SCAN: {self.scan}"
            self.titulo_sku.configure(text=msg)
            self.comunicacion(mensaje=f"{sku_read}")

        if int(self.scan) == self.pzas:
            self.scan = 0
            self.comunicacion(mensaje="OFFER")
            self.titulo1.pack_forget()
            self.titulo_sku.pack_forget()
            self.entry_sku.pack_forget()
            self.actualizar()

    def actualizar(self):
        print("Aqui actualizamos secciones")
        self.skus_conts += 1
        self.looper()

    #PROCESO DE ENTREGA
    def entregar(self):
        time.sleep(8)
        self.comunicacion(mensaje="REGRESA")

        self.frame_entrega = ctk.CTkFrame(self, fg_color="purple")
        self.frame_entrega.pack(fill="both", expand=True, padx=5, pady=5)

        self.mesa = "MESAP2CCTA01"
        msg = f"OLEADA {self.oleada["Oleada"]}\n\nDirigete a la mesa de entrega\n{self.mesa}"
        self.entrega_label = ctk.CTkLabel(self.frame_entrega, text=f"{msg}")
        self.entrega_label.pack(expand=True)

        self.mesa_entry = ctk.CTkEntry(self.frame_entrega)
        self.mesa_entry.pack(pady=5)
        self.mesa_entry.bind("<Return>", self.evento_bc_mesa)

    def evento_bc_mesa(self, event):
        mesa_scan = self.mesa_entry.get()
        self.mesa_entry.delete(0, 'end')
        if mesa_scan == self.mesa:
            self.comunicacion()
            self.entregar_docs()
        else:
            msg = f"MESA INCORRECTA\n\nDirigete a la mesa de entrega\n{self.mesa}"
            self.entrega_label.configure(text=msg)
            self.comunicacion(mensaje="MALA_UBIC")

    def entregar_docs(self):
        self.mesa_entry.pack_forget()

        self.pedidos = self.oleada['Pedidos'][self.turn_doc]
        self.nombre_pedido = self.pedidos["Pedido"]
        self.detalle_pzas = len(self.pedidos["detalle"])

        msg=f"ENTREGAMOS PEDIDO\n{self.nombre_pedido}    Pzas={self.detalle_pzas}"
        self.entrega_label.configure(text=msg)

        self.mesa_entry2 = ctk.CTkEntry(self.frame_entrega)
        self.mesa_entry2.pack(pady=3)
        self.mesa_entry2.bind("<Return>",self.continuar_entrega)

        self.frame_bc_image = ctk.CTkFrame(self.frame_entrega)
        self.frame_bc_image.pack(fill="both", expand=True, padx=5, pady=5)

        #CREAR IMAGEN Y MOSTRARLA
        img = one_descarga.generate_and_show_barcode(f"{self.nombre_pedido}")
        try:
            my_image = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(200, 200)
            )
            self.label_imagen = ctk.CTkLabel(self.frame_bc_image, image=my_image, text="")
            self.label_imagen.pack()
        except:
            self.label_imagen = ctk.CTkLabel(self.frame_bc_image, text="ERROR EN IMAGEN")
            self.label_imagen.pack()
        #########################

        letra = self.orden_compartimiento[self.nombre_pedido]
        self.comunicacion(mensaje=f"{letra}{self.detalle_pzas}ENTREGA")

    def continuar_entrega(self, event):
        self.turn_doc += 1
        mesa_scan = self.mesa_entry2.get()
        self.mesa_entry2.delete(0, 'end')

        if mesa_scan == self.mesa and self.turn_doc < 4:
            self.frame_bc_image.pack_forget()
            self.mesa_entry2.pack_forget()
            self.entregar_docs()

        else:
            self.oleada = None
            self.compartimiento = ["A", "B", "C", "D"]
            self.doc = {"trabajador":""}
            self.skus_conts = 0
            self.scan = 0
            self.turn_doc = 0

            self.frame_entrega.pack_forget()
            self.comunicacion()
            self.frame_nss()



if __name__ == "__main__":
    app = App()
    app.mainloop()

