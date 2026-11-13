import json
import customtkinter as ctk
import serial

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- DATOS DEL CONCENTRADO ---
DATOS_CONCENTRADO = {
    "concentrado_id": "CONC-88401",
    "total_pedidos": 4,
    "ruta_optimizada": [
        {
            "paso": 1,
            "ubicacion_codigo": "P1-L1-F1-N1",
            "pedido_id": "PED-001",
            "compartimiento": "A",
            "sku": "SKU-1001",
            "cantidad": 3,
        },
        {
            "paso": 2,
            "ubicacion_codigo": "P1-L1-F2-N3",
            "pedido_id": "PED-003",
            "compartimiento": "C",
            "sku": "SKU-3002",
            "cantidad": 1,
        },
        {
            "paso": 3,
            "ubicacion_codigo": "P1-L2-F1-N1",
            "pedido_id": "PED-002",
            "compartimiento": "B",
            "sku": "SKU-2005",
            "cantidad": 5,
        },
        {
            "paso": 4,
            "ubicacion_codigo": "P2-L1-F3-N2",
            "pedido_id": "PED-004",
            "compartimiento": "D",
            "sku": "SKU-4001",
            "cantidad": 2,
        },
    ],
}


class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success

        self.lbl_titulo = ctk.CTkLabel(
            self,
            text="ACCESO AL SISTEMA",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.lbl_titulo.pack(pady=(40, 20))

        self.lbl_instruccion = ctk.CTkLabel(
            self, text="Ingrese No. de Empleado (11+ dígitos):"
        )
        self.lbl_instruccion.pack(pady=5)

        self.entry_empleado = ctk.CTkEntry(
            self, width=300, height=40, justify="center"
        )
        self.entry_empleado.pack(pady=10)
        self.entry_empleado.bind("<Return>", self.validar_empleado)
        self.entry_empleado.focus_set()

        self.btn_ingresar = ctk.CTkButton(
            self,
            text="Ingresar",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.validar_empleado,
        )
        self.btn_ingresar.pack(pady=15)

        self.lbl_error = ctk.CTkLabel(
            self, text="", text_color="#EF4444", font=ctk.CTkFont(weight="bold")
        )
        self.lbl_error.pack(pady=10)

    def validar_empleado(self, event=None):
        entrada = self.entry_empleado.get().strip()
        if entrada.isdigit() and len(entrada) >= 11:
            self.lbl_error.configure(text="")
            self.on_login_success()
        else:
            self.lbl_error.configure(text="NSS incorrecto")
            self.entry_empleado.delete(0, "end")


class PickToLightCartApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema Pick to Light Cart - Control de Concentrado")
        self.geometry("650x550")
        self.resizable(False, False)

        # Configuración UART
        self.puerto_com = "COM9"
        self.baudrate = 115200
        self.serial_port = None
        self.inicializar_serial()

        # Control del flujo de picking
        self.concentrado = DATOS_CONCENTRADO
        self.ruta = self.concentrado["ruta_optimizada"]
        self.indice_paso_actual = 0

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Iniciar en Login
        self.frame_login = LoginFrame(
            self, on_login_success=self.mostrar_interfaz_picking
        )
        self.frame_login.pack(fill="both", expand=True)

    def inicializar_serial(self):
        try:
            self.serial_port = serial.Serial(
                port=self.puerto_com, baudrate=self.baudrate, timeout=1
            )
            print(f"Puerto {self.puerto_com} conectado.")
        except serial.SerialException:
            print(f"Modo Simulación: {self.puerto_com} no disponible.")
            self.serial_port = None

    def mostrar_interfaz_picking(self):
        self.frame_login.destroy()

        # Header Concentrado
        self.lbl_conc = ctk.CTkLabel(
            self,
            text=f"CONCENTRADO: {self.concentrado['concentrado_id']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#9CA3AF",
        )
        self.lbl_conc.pack(pady=(15, 0))

        # Indicador de Progreso
        self.lbl_paso = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_paso.pack(pady=(0, 10))

        # Target Ubicación
        self.lbl_titulo_target = ctk.CTkLabel(
            self,
            text="UBICACIÓN SIGUIENTE:",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.lbl_titulo_target.pack(pady=2)

        self.lbl_target = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color="#3B82F6",
        )
        self.lbl_target.pack(pady=5)

        # Detalles del Pick
        self.lbl_detalles = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=16)
        )
        self.lbl_detalles.pack(pady=5)

        # Entrada para Escáner
        self.entry_escaner = ctk.CTkEntry(
            self,
            width=340,
            height=45,
            font=ctk.CTkFont(size=18),
            justify="center",
            placeholder_text="Escanee ubicación...",
        )
        self.entry_escaner.pack(pady=10)
        self.entry_escaner.bind("<Return>", self.validar_escaneo)

        # Estado/Respuesta
        self.lbl_resultado = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=22, weight="bold"),
            corner_radius=8,
            width=420,
            height=50,
        )
        self.lbl_resultado.pack(pady=15)

        # Cargar el primer paso
        self.cargar_paso_actual()

    def cargar_paso_actual(self):
        """Carga en los widgets los datos exactos del paso activo."""
        if self.indice_paso_actual < len(self.ruta):
            item = self.ruta[self.indice_paso_actual]

            self.lbl_paso.configure(
                text=f"PASO {item['paso']} DE {len(self.ruta)}"
            )
            self.lbl_target.configure(text=item["ubicacion_codigo"])
            self.lbl_detalles.configure(
                text=f"SKU: {item['sku']}  |  Compartimento: {item['compartimiento']}  |  Cant: {item['cantidad']} pcs"
            )

            self.entry_escaner.delete(0, "end")
            self.entry_escaner.focus_set()
        else:
            self.lbl_target.configure(
                text="¡CONCENTRADO COMPLETO!", text_color="#10B981"
            )
            self.lbl_detalles.configure(
                text="Todos los pedidos han sido recolectados."
            )
            self.entry_escaner.configure(state="disabled")

    def enviar_uart(self, compartimiento, cantidad):
        """Formatea la trama exacta [COMPARTIMIENTO][CANTIDAD]\n Ex: A3\n"""
        if cantidad == 0:
            trama_str = f"{compartimiento}"
        else:
            trama_str = f"{compartimiento}{cantidad}"

        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(trama_str.encode("utf-8"))
                print(f"UART Tx -> {trama_str.strip()}")
            except Exception as e:
                print(f"Error UART: {e}")
        else:
            print(f"Simulación UART Tx -> {trama_str.strip()}")

    def validar_escaneo(self, event=None):
        codigo_escaneado = self.entry_escaner.get().strip().upper()
        # Se obtiene el elemento activo ANTES de cualquier modificación
        item_actual = self.ruta[self.indice_paso_actual]

        if codigo_escaneado == item_actual["ubicacion_codigo"]:
            comp = item_actual["compartimiento"]
            cant = item_actual["cantidad"]
            sku = item_actual["sku"]

            # 1. Mostrar confirmación con datos 100% sincrónicos
            self.lbl_resultado.configure(
                text=f"CORRECTO: Depositar {cant} Pcs de {sku} en [{comp}]",
                fg_color="#10B981",
                text_color="white",
            )

            # 2. Enviar trama por UART (ejemplo: A3\n)
            self.enviar_uart(comp, cant)

            # 3. Incrementar el contador y pasar al siguiente en 1.5s
            self.indice_paso_actual += 1
            self.after(1500, self.limpiar_y_siguiente)
        else:
            self.lbl_resultado.configure(
                text="UBICACIÓN INCORRECTA",
                fg_color="#EF4444",
                text_color="white",
            )
            self.entry_escaner.delete(0, "end")
            self.enviar_uart("MALA_UBIC", 0)

    def limpiar_y_siguiente(self):
        self.lbl_resultado.configure(text="", fg_color="transparent")
        self.cargar_paso_actual()

    def on_closing(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.destroy()


if __name__ == "__main__":
    app = PickToLightCartApp()
    app.mainloop()