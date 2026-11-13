import customtkinter as ctk
import serial, time, datetime

# Librería mock/externa
import one_descarga

# Configuración del Tema Industrial Moderno
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Constantes de Paleta
BG_CARD = ("#2B2B2B", "#1E1E1E")
ACCENT_BLUE = "#1F6AA5"
ACCENT_GREEN = "#2B8A3E"
ACCENT_RED = "#C92A2A"
TEXT_MUTED = "#A0A0A0"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pick to Light Cart System v2.0")
        self.geometry("640x480")
        #self.resizable(False, False)

        # COMUNICACIÓN UART
        self.puerto_serial = 'COM9'
        self.baudios = 115200

        # VARIABLES GENERALES
        self.oleada = None
        self.compartimiento = ["A", "B", "C", "D"]
        self.doc = {"trabajador": "",
                    "inicial":"",
                    "final":"",
                    "doc":None}
        self.skus_conts = 0
        self.scan = 0
        self.turn_doc = 0

        # CONTENEDOR PRINCIPAL DÉ CORTE PROFESIONAL
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Barra de estado superior
        self.build_header_bar()

        # Frame dinámico para etapas del proceso
        self.current_frame = None

        # INICIALIZACIÓN
        self.comunicacion()
        self.show_frame_nss()
    #mandar a traer cada vez que sea llamado
    def cronos(self):
        today = datetime.datetime.now()
        D,M,Y = today.day, today.month, today.year
        hh, mm, ss = today.hour, today.minute, today.second
        if D<10: D=f"0{D}"
        if M<10: M=f"0{M}"
        if Y<10: Y=f"0{Y}"
        if hh<10: hh=f"0{hh}"
        if mm<10: mm=f"0{mm}"

        return D,M,Y, hh, mm, ss

    def build_header_bar(self):
        """Barra de encabezado superior persistente con indicador de estado."""
        header = ctk.CTkFrame(self.main_container, height=45, fg_color=BG_CARD, corner_radius=10)
        header.pack(fill="x", pady=(0, 15))
        header.pack_propagate(False)

        title_lbl = ctk.CTkLabel(
            header,
            text="PICK TO LIGHT CART",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_lbl.pack(side="left", padx=15)

        self.status_badge = ctk.CTkLabel(
            header,
            text="● UART COM9: OK",
            text_color="#40C057",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.status_badge.pack(side="right", padx=15)

    def clear_current_frame(self):
        """Limpia el contenedor activo para evitar acumulación de widgets."""
        if self.current_frame is not None:
            self.current_frame.destroy()

    def comunicacion(self, mensaje="OFFER"):
        try:
            self.esp = serial.Serial(self.puerto_serial, self.baudios, timeout=1)
            self.esp.write(mensaje.encode('utf-8'))
            respuesta = self.esp.readline().decode('utf-8').strip()
            if respuesta:
                print(f"Respuesta del ESP8266: {respuesta}")
            self.esp.close()
            if hasattr(self, 'status_badge'):
                self.status_badge.configure(text="● UART COM9: OK", text_color="#40C057")
        except Exception as e:
            print(f"Error Serial: {e}")
            if hasattr(self, 'status_badge'):
                self.status_badge.configure(text="● UART DISCONNECTED", text_color=ACCENT_RED)

    # ------------------------------------------------------------------
    # ETAPA 1: REGISTRO DE NSS
    # ------------------------------------------------------------------
    def show_frame_nss(self):
        self.clear_current_frame()

        self.current_frame = ctk.CTkFrame(self.main_container, fg_color=BG_CARD, corner_radius=12)
        self.current_frame.pack(fill="both", expand=True)

        card = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        card.pack(expand=True)

        ctk.CTkLabel(
            card,
            text="Registro de Operador",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 5))

        self.nss_labbel = ctk.CTkLabel(
            card,
            text="Escanee su Número de Seguro Social (NSS) para iniciar",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 20))

        self.entry_trabajador = ctk.CTkEntry(
            card,
            width=280,
            height=40,
            placeholder_text="Escanear NSS...",
            justify="center",
            font=ctk.CTkFont(size=14)
        )
        self.entry_trabajador.pack(pady=10)
        self.entry_trabajador.bind("<Return>", self.evento_enter)
        self.entry_trabajador.focus()

    def evento_enter(self, event):
        no_trabajador = self.entry_trabajador.get().strip()

        if len(no_trabajador) <= 10:
            self.nss_labbel.configure(
                text="NUMERO NO VALIDO\nEscanee su Número de Seguro Social (NSS) para iniciar")
        else:
            self.doc["trabajador"] = no_trabajador
            self.entry_trabajador.delete(0, 'end')

            print(self.doc["trabajador"])
            D,M,Y, hh, mm, ss = self.cronos()
            datos = f"{D}-{M}-{Y} {hh}:{mm}"
            self.doc["inicial"] = datos
            print(self.doc["inicial"])
            self.descargar_oleadas()

    # ------------------------------------------------------------------
    # PROCESO OLEADA & LOOPER
    # ------------------------------------------------------------------
    def descargar_oleadas(self):
        oleada = one_descarga.QA()
        if oleada:
            self.oleada = oleada
            self.nombre_oleada = self.oleada['Oleada']
            self.orden_compartimiento = {}
            for i in range(0, len(oleada['Pedidos'])):
                pedido = oleada['Pedidos'][i]['Pedido']
                comp = self.compartimiento[i]
                self.orden_compartimiento[pedido] = comp
            self.looper()

    def looper(self):
        if self.skus_conts >= len(self.oleada['Recorrido']):
            self.entregar()
        else:
            self.oneBone = self.oleada['Recorrido'][self.skus_conts]
            pick = self.oneBone
            pedido = pick['Pedido']
            p = pick['pasillo']
            l = pick['lado']
            x = pick['fondo']
            y = pick['nivel']
            self.show_frame_pick(pedido, p, l, x, y)

    # ------------------------------------------------------------------
    # ETAPA 2: PROCESO DE PICKING (UBICACIÓN Y SKUS)
    # ------------------------------------------------------------------
    def show_frame_pick(self, pedido, p, l, x, y):
        self.clear_current_frame()

        self.ubic = f"P{p}L{l}X{x}Y{y}"
        self.ubic_show = f"P{p} - L{l} - Fondo {x} - Nivel {y}"

        self.current_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.current_frame.pack(fill="both", expand=True)

        # Panel de Encabezado de Tarea
        info_card = ctk.CTkFrame(self.current_frame, fg_color=BG_CARD, corner_radius=12)
        info_card.pack(fill="x", pady=(0, 15), ipady=10)

        ctk.CTkLabel(
            info_card,
            text=f"PEDIDO: {pedido}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_BLUE
        ).pack(anchor="w", padx=20, pady=(10, 0))

        ctk.CTkLabel(
            info_card,
            text=f"DIRÍGASE A: PASILLO {p}",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=20)

        ctk.CTkLabel(
            info_card,
            text=f"Ubicación Target: {self.ubic_show}",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=20)

        # Panel de Acción / Lectura
        self.action_card = ctk.CTkFrame(self.current_frame, fg_color=BG_CARD, corner_radius=12)
        self.action_card.pack(fill="both", expand=True)

        self.lbl_instruction = ctk.CTkLabel(
            self.action_card,
            text="Escanee la Ubicación para Confirmar",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.lbl_instruction.pack(pady=(25, 10))

        self.entry_ubic = ctk.CTkEntry(
            self.action_card,
            width=300,
            height=42,
            placeholder_text="Esperando scanner de ubicación...",
            justify="center",
            font=ctk.CTkFont(size=14)
        )
        self.entry_ubic.pack(pady=10)
        self.entry_ubic.bind("<Return>", self.evento_ubic)
        self.entry_ubic.focus()

    def evento_ubic(self, event):
        ubic = self.entry_ubic.get().strip()
        self.entry_ubic.delete(0, 'end')

        if str(ubic) != self.ubic:
            self.comunicacion(mensaje="MALA_UBIC")
            msg_error="UBICACION EQUIVOCADA\nEscanee la Ubicación para Confirmar"
            self.lbl_instruction.configure(
                text=msg_error,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            #messagebox.showwarning(title="Ubicación Errónea", message=f"Ubicación escaneada incorrecta.\nSe esperaba: {self.ubic}")
        else:
            self.comunicacion()
            self.skus()

    def skus(self):
        # Transición visual a modo lectura de SKU
        self.lbl_instruction.configure(text="Confirmación de Ubicación Exitosa", text_color="#40C057")
        self.entry_ubic.destroy()

        self.art = self.oleada['Recorrido'][self.skus_conts]
        self.sku = self.art['sku']
        self.cart_pos = self.orden_compartimiento[self.art['Pedido']]
        self.pzas = self.art['CANT_PED']

        self.comunicacion(mensaje=f"{self.cart_pos}{self.pzas}")

        # Sub-panel de métricas del SKU
        sku_frame = ctk.CTkFrame(self.action_card, fg_color="#252525", corner_radius=8)
        sku_frame.pack(fill="x", padx=30, pady=10, ipady=5)

        self.lbl_sku_data = ctk.CTkLabel(
            sku_frame,
            text=f"SKU: {self.sku}   |   POSICIÓN EN CARRO: [{self.cart_pos}]",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sku_data.pack(pady=5)

        self.progress_lbl = ctk.CTkLabel(
            sku_frame,
            text=f"Piezas: {self.scan} / {self.pzas}",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        self.progress_lbl.pack(pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(sku_frame, width=280)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        self.entry_sku = ctk.CTkEntry(
            self.action_card,
            width=300,
            height=42,
            placeholder_text="Escanear Código de Barras SKU...",
            justify="center",
            font=ctk.CTkFont(size=14)
        )
        self.entry_sku.pack(pady=15)
        self.entry_sku.bind("<Return>", self.evento_sku)
        self.entry_sku.focus()

    def evento_sku(self, event):
        sku_read = self.entry_sku.get().strip()
        self.entry_sku.delete(0, 'end')

        if str(sku_read) == str(self.sku):
            self.scan += 1
            self.progress_lbl.configure(text=f"Piezas: {self.scan} / {self.pzas}")
            self.progress_bar.set(self.scan / self.pzas)
            self.comunicacion(mensaje=f"{sku_read}")

        if int(self.scan) == self.pzas:
            self.scan = 0
            self.comunicacion(mensaje="OFFER")
            self.skus_conts += 1
            self.looper()

    # ------------------------------------------------------------------
    # ETAPA 3: ENTREGA EN MESA Y DOCUMENTACIÓN
    # ------------------------------------------------------------------
    def entregar(self):
        time.sleep(8)
        self.comunicacion(mensaje="REGRESA")
        self.clear_current_frame()

        self.current_frame = ctk.CTkFrame(self.main_container, fg_color=BG_CARD, corner_radius=12)
        self.current_frame.pack(fill="both", expand=True)

        self.mesa = "MESAP2CCTA01"

        card = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        card.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            card,
            text=f"OLEADA {self.oleada['Oleada']} COMPLETADA",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#40C057"
        ).pack(pady=(10, 5))

        self.entrega_label = ctk.CTkLabel(
            card,
            text=f"Diríjase e ingrese la mesa de entrega:\n{self.mesa}",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_MUTED
        )
        self.entrega_label.pack(pady=10)

        self.mesa_entry = ctk.CTkEntry(
            card,
            width=280,
            height=40,
            placeholder_text="Escanear Mesa...",
            justify="center",
            font=ctk.CTkFont(size=14)
        )
        self.mesa_entry.pack(pady=10)
        self.mesa_entry.bind("<Return>", self.evento_bc_mesa)
        self.mesa_entry.focus()

    def evento_bc_mesa(self, event):
        mesa_scan = self.mesa_entry.get().strip()
        self.mesa_entry.delete(0, 'end')

        if mesa_scan == self.mesa:
            self.comunicacion()
            self.mesa_entry.destroy()
            self.entregar_docs()
        else:
            self.entrega_label.configure(
                text=f"MESA INCORRECTA\nDiríjase a la mesa de entrega: {self.mesa}",
                text_color=ACCENT_RED
            )
            self.comunicacion(mensaje="MALA_UBIC")

    def entregar_docs(self):
        self.pedidos = self.oleada['Pedidos'][self.turn_doc]
        self.nombre_pedido = self.pedidos["Pedido"]
        self.detalle_pzas = 0
        try:
            for skus in self.pedidos["detalle"]:
                pzas = int(skus['CANT_PED'])
                self.detalle_pzas += pzas
        except:
            self.detalle_pzas = len(self.pedidos["detalle"])
        self.entrega_label.configure(
            text=f"ENTREGA DE PEDIDO: {self.nombre_pedido}\nPiezas Totales: {self.detalle_pzas}",
            text_color="white"
        )

        # Marco para desplegar la imagen del código de barras
        self.frame_bc_image = ctk.CTkFrame(self.current_frame, fg_color="#1A1A1A", corner_radius=10)
        self.frame_bc_image.pack(fill="both", expand=True, padx=40, pady=10)

        try:
            img = one_descarga.generate_and_show_barcode(f"{self.nombre_pedido}")
            my_image = ctk.CTkImage(light_image=img, dark_image=img, size=(220, 100))
            self.label_imagen = ctk.CTkLabel(self.frame_bc_image, image=my_image, text="")
            self.label_imagen.pack(expand=True)
        except Exception:
            self.label_imagen = ctk.CTkLabel(self.frame_bc_image, text="[ CÓDIGO DE BARRAS GENERADO ]", font=ctk.CTkFont(size=12))
            self.label_imagen.pack(expand=True)

        self.mesa_entry2 = ctk.CTkEntry(
            self.current_frame,
            width=280,
            height=40,
            placeholder_text="Confirmar entrega (Re-escanear Mesa)...",
            justify="center"
        )
        self.mesa_entry2.pack(pady=(5, 20))
        self.mesa_entry2.bind("<Return>", self.continuar_entrega)
        self.mesa_entry2.focus()

        letra = self.orden_compartimiento[self.nombre_pedido]
        self.comunicacion(mensaje=f"{letra}{self.detalle_pzas}ENTREGA")

    def continuar_entrega(self, event):
        self.turn_doc += 1
        mesa_scan = self.mesa_entry2.get().strip()
        self.mesa_entry2.delete(0, 'end')

        if mesa_scan == self.mesa and self.turn_doc < len(self.oleada['Pedidos']):
            self.frame_bc_image.destroy()
            self.mesa_entry2.destroy()
            self.entregar_docs()
        else:
            D,M,Y, hh, mm, ss = self.cronos()
            datos = f"{D}-{M}-{Y} {hh}:{mm}"
            print(datos)
            self.doc["final"] = datos
            self.entregar_cart()

    # ------------------------------------------------------------------
    # ETAPA 4: ENTREGAR Y MOSTRAR TRABAJOS
    # ------------------------------------------------------------------
    def entregar_cart(self):
        self.comunicacion(mensaje="REGRESA")

        self.clear_current_frame()

        self.current_frame = ctk.CTkFrame(self.main_container, fg_color=BG_CARD, corner_radius=12)
        self.current_frame.pack(fill="both", expand=True)

        card = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        card.pack(expand=True)
        msg_end = (f"PTL CART VACIO\n\nOLEADA {self.oleada['Oleada']} CONCLUIDA\n\nTrabajador: {self.doc['trabajador']} \n "
                   f"Tiempo de Inicio:{self.doc['inicial']}     Tiempo Final: {self.doc['final']}\n\n")
        ctk.CTkLabel(
            card,
            text=msg_end,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 5))

        self.nss_labbel2 = ctk.CTkLabel(
            card,
            text="Escanee su Número de Seguro Social (NSS) para Terminar el Proceso",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 20))

        self.entry_trabajador2 = ctk.CTkEntry(
            card,
            width=280,
            height=40,
            placeholder_text="Escanear NSS...",
            justify="center",
            font=ctk.CTkFont(size=14)
        )
        self.entry_trabajador2.pack(pady=10)
        self.entry_trabajador2.bind("<Return>", self.evento_final_entregar)
        self.entry_trabajador2.focus()

    def evento_final_entregar(self, event):
        no_trabajador2 = self.entry_trabajador2.get().strip()
        self.entry_trabajador2.delete(0, 'end')
        print(type(no_trabajador2), no_trabajador2, type(self.doc["trabajador"]), self.doc["trabajador"])
        if no_trabajador2 == self.doc["trabajador"]:self.reinicio()


    def reinicio(self):
        # RESET DEL CICLO COMPLETO
        self.oleada = None
        self.compartimiento = ["A", "B", "C", "D"]
        self.doc = {"trabajador": "",
                    "inicial":"",
                    "final":"",
                    "doc":None}
        self.skus_conts = 0
        self.scan = 0
        self.turn_doc = 0

        self.comunicacion()
        self.show_frame_nss()


if __name__ == "__main__":
    app = App()
    app.mainloop()