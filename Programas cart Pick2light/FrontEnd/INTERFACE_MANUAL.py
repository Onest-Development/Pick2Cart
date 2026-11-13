import customtkinter as ctk
import serial
import threading
import queue
import time

# Configuración del tema de CustomTkinter
ctk.set_appearance_mode("Dark")  # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"


class PickToLightGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pick-to-Light System - 4 Slots (COM9 @ 115200)")
        self.geometry("750x550")
        self.minsize(700, 500)

        # Configuración del puerto serial
        self.port = "COM9"
        self.baudrate = 115200
        self.ser = None
        self.is_running = False

        # Cola de mensajes para comunicación Hilo -> GUI
        self.msg_queue = queue.Queue()

        # Diccionario de estado para los 4 slots
        self.slots = {
            1: {"qty_var": ctk.StringVar(value="0"), "status_lbl": None, "card": None},
            2: {"qty_var": ctk.StringVar(value="0"), "status_lbl": None, "card": None},
            3: {"qty_var": ctk.StringVar(value="0"), "status_lbl": None, "card": None},
            4: {"qty_var": ctk.StringVar(value="0"), "status_lbl": None, "card": None},
        }

        self._crear_interfaz()
        self.conectar_serial()

        # Chequeo periódico de la cola de mensajes
        self.after(100, self._procesar_cola_mensajes)

    def _crear_interfaz(self):
        # ----------------- Header / Estado de Conexión -----------------
        self.header_frame = ctk.CTkFrame(self, corner_radius=10)
        self.header_frame.pack(fill="x", padx=15, pady=(15, 5))

        self.lbl_conexion = ctk.CTkLabel(
            self.header_frame,
            text="Estado Serial: Desconectado",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#E74C3C",
        )
        self.lbl_conexion.pack(side="left", padx=15, pady=10)

        self.btn_reconectar = ctk.CTkButton(
            self.header_frame,
            text="Reconectar COM9",
            width=130,
            command=self.conectar_serial,
        )
        self.btn_reconectar.pack(side="right", padx=15, pady=10)

        # ----------------- Grid Principal (2x2 Slots) -----------------
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=15, pady=10)

        positions = [(1, 0, 0), (2, 0, 1), (3, 1, 0), (4, 1, 1)]

        for slot_id, r, c in positions:
            # Tarjeta/Contenedor de cada Slot
            card = ctk.CTkFrame(self.grid_frame, corner_radius=12)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

            self.grid_frame.rowconfigure(r, weight=1)
            self.grid_frame.columnconfigure(c, weight=1)

            # Título del Slot
            lbl_title = ctk.CTkLabel(
                card,
                text=f"SLOT {slot_id}",
                font=ctk.CTkFont(size=18, weight="bold"),
            )
            lbl_title.pack(pady=(12, 5))

            # Contenedor de Cantidad (Entry con botones +/-)
            qty_frame = ctk.CTkFrame(card, fg_color="transparent")
            qty_frame.pack(pady=5)

            btn_dec = ctk.CTkButton(
                qty_frame,
                text="-",
                width=30,
                height=30,
                command=lambda s=slot_id: self._modificar_cantidad(s, -1),
            )
            btn_dec.pack(side="left", padx=2)

            entry_qty = ctk.CTkEntry(
                qty_frame,
                textvariable=self.slots[slot_id]["qty_var"],
                width=50,
                justify="center",
                font=ctk.CTkFont(size=16, weight="bold"),
            )
            entry_qty.pack(side="left", padx=5)

            btn_inc = ctk.CTkButton(
                qty_frame,
                text="+",
                width=30,
                height=30,
                command=lambda s=slot_id: self._modificar_cantidad(s, 1),
            )
            btn_inc.pack(side="left", padx=2)

            # Botón Activar / Enviar Orden
            btn_enviar = ctk.CTkButton(
                card,
                text="Enviar Orden",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda s=slot_id: self.enviar_orden_slot(s),
            )
            btn_enviar.pack(pady=8, padx=20, fill="x")

            # Banner / Indicador de Estado Visual
            lbl_status = ctk.CTkLabel(
                card,
                text="INACTIVO",
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#3B3B3B",
                corner_radius=8,
                height=32,
            )
            lbl_status.pack(pady=(5, 12), padx=15, fill="x")

            # Guardar referencias
            self.slots[slot_id]["status_lbl"] = lbl_status
            self.slots[slot_id]["card"] = card

    def _modificar_cantidad(self, slot_id, cambio):
        """Incrementa o decrementa la cantidad del spinbox improvisado."""
        try:
            val = int(self.slots[slot_id]["qty_var"].get()) + cambio
            val = max(0, min(99, val))  # Límite entre 0 y 99
            self.slots[slot_id]["qty_var"].set(str(val))
        except ValueError:
            self.slots[slot_id]["qty_var"].set("0")

    # ----------------- COMUNICACIÓN UART -----------------

    def conectar_serial(self):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()

            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self.is_running = True

            # Hilo secundario de lectura continua
            self.rx_thread = threading.Thread(target=self._escuchar_hardware, daemon=True)
            self.rx_thread.start()

            self.lbl_conexion.configure(
                text=f"Conectado: {self.port} @ {self.baudrate} bps",
                text_color="#2ECC71",
            )
        except Exception as e:
            self.lbl_conexion.configure(
                text=f"Error en {self.port}: Puerto no disponible",
                text_color="#E74C3C",
            )

    def enviar_orden_slot(self, slot_id):
        """Envía comando UART (Formato: S<ID>:<CANTIDAD>\n)"""
        if not self.ser or not self.ser.is_open:
            return

        try:
            qty = int(self.slots[slot_id]["qty_var"].get())
            if qty <= 0:
                return

            trama_tx = f"S{slot_id}:{qty:03d}\n"
            self.ser.write(trama_tx.encode("utf-8"))

            # Actualizar GUI a modo espera de confirmación
            self.slots[slot_id]["status_lbl"].configure(
                text=f"PICKING ({qty})", fg_color="#E67E22"
            )
        except ValueError:
            pass

    def _escuchar_hardware(self):
        """Lectura en hilo secundario de los eventos devueltos por el microcontrolador"""
        while self.is_running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    linea = self.ser.readline().decode("utf-8", errors="ignore").strip()
                    if linea:
                        self.msg_queue.put(linea)
            except Exception:
                break
            time.sleep(0.01)

    def _procesar_cola_mensajes(self):
        """Atiende las respuestas del microcontrolador sin congelar la GUI"""
        while not self.msg_queue.empty():
            msg = self.msg_queue.get()

            # Trama de confirmación esperada: ACK:S1, ACK:S2, etc.
            if msg.startswith("ACK:S"):
                try:
                    slot_id = int(msg.split("S")[1])
                    if slot_id in self.slots:
                        # Evento de pickeo correcto por el operador
                        self.slots[slot_id]["status_lbl"].configure(
                            text="PICK OK", fg_color="#2ECC71"
                        )
                        self.slots[slot_id]["qty_var"].set("0")

                        # Regresar a estado INACTIVO tras 1.5 segundos
                        self.after(
                            1500,
                            lambda s=slot_id: self.slots[s]["status_lbl"].configure(
                                text="INACTIVO", fg_color="#3B3B3B"
                            ),
                        )
                except ValueError:
                    pass

        self.after(50, self._procesar_cola_mensajes)

    def destroy(self):
        self.is_running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        super().destroy()


if __name__ == "__main__":
    app = PickToLightGUI()
    app.mainloop()