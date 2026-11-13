import customtkinter as ctk
import serial

# Configuración del tema visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success

        # --- TÍTULO ---
        self.lbl_titulo = ctk.CTkLabel(
            self,
            text="ACCESO AL SISTEMA",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.lbl_titulo.pack(pady=(40, 20))

        # --- ENTRADA DE EMPLEADO ---
        self.lbl_instruccion = ctk.CTkLabel(
            self,
            text="Ingrese No. de Empleado (12+ dígitos):",
            font=ctk.CTkFont(size=14),
        )
        self.lbl_instruccion.pack(pady=5)

        self.entry_empleado = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            font=ctk.CTkFont(size=16),
            justify="center",
            placeholder_text="Ej. 123456789012",
        )
        self.entry_empleado.pack(pady=10)
        self.entry_empleado.bind("<Return>", self.validar_empleado)
        self.entry_empleado.focus_set()

        # --- BOTÓN DE INGRESO ---
        self.btn_ingresar = ctk.CTkButton(
            self,
            text="Ingresar",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=200,
            command=self.validar_empleado,
        )
        self.btn_ingresar.pack(pady=15)

        # --- MENSAJE DE ERROR ---
        self.lbl_error = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#EF4444",
        )
        self.lbl_error.pack(pady=10)

    def validar_empleado(self, event=None):
        entrada = self.entry_empleado.get().strip()

        # Validar que sea puramente numérico y que contenga 12 o más dígitos
        if entrada.isdigit() and len(entrada) >= 11:
            self.lbl_error.configure(text="")
            self.on_login_success()  # Callback hacia la app principal
        else:
            self.lbl_error.configure(text="NSS incorrecto")
            self.entry_empleado.delete(0, "end")
            self.entry_empleado.focus_set()


class PickToLightCartApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Sistema Pick to Light Cart - Fase 2 (UART)")
        self.geometry("600x480")
        self.resizable(False, False)

        # Ubicación asignada / requerida
        self.ubicacion_objetivo = "A-01-02-C"

        # --- CONFIGURACIÓN UART / SERIAL ---
        self.puerto_com = "COM9"
        self.baudrate = 115200
        self.serial_port = None
        self.inicializar_serial()

        # Configurar cierre de puerto al salir de la app
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Cargar pantalla de Login al iniciar
        self.frame_login = LoginFrame(
            self, on_login_success=self.mostrar_interfaz_picking
        )
        self.frame_login.pack(fill="both", expand=True)

    def inicializar_serial(self):
        """Intenta abrir la comunicación serial en COM9."""
        try:
            self.serial_port = serial.Serial(
                port=self.puerto_com,
                baudrate=self.baudrate,
                timeout=1,
            )
            print(f"Puerto {self.puerto_com} conectado correctamente.")
        except serial.SerialException as e:
            print(f"Error al abrir {self.puerto_com}: {e}")
            self.serial_port = None

    def mostrar_interfaz_picking(self):
        """Destruye el frame de login e inicializa los widgets de Picking."""
        self.frame_login.destroy()

        # --- SECCIÓN: UBICACIÓN REQUERIDA ---
        self.lbl_titulo_target = ctk.CTkLabel(
            self,
            text="UBICACIÓN A PICKAEAR:",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.lbl_titulo_target.pack(pady=(25, 5))

        self.lbl_target = ctk.CTkLabel(
            self,
            text=self.ubicacion_objetivo,
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color="#3B82F6",
        )
        self.lbl_target.pack(pady=(0, 15))

        # --- SECCIÓN: ENTRADA DEL ESCÁNER ---
        self.lbl_instruccion = ctk.CTkLabel(
            self,
            text="Escanee el código de confirmación:",
            font=ctk.CTkFont(size=14),
        )
        self.lbl_instruccion.pack(pady=5)

        self.entry_escaner = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            font=ctk.CTkFont(size=20),
            justify="center",
            placeholder_text="Esperando lectura...",
        )
        self.entry_escaner.pack(pady=10)
        self.entry_escaner.bind("<Return>", self.validar_ubicacion)
        self.entry_escaner.focus_set()

        # --- SECCIÓN: MENSAJE DE ESTADO / CONFIRMACIÓN ---
        self.lbl_resultado = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=28, weight="bold"),
            corner_radius=8,
            width=350,
            height=60,
        )
        self.lbl_resultado.pack(pady=20)

    def enviar_uart(self, mensaje):
        """Envía una cadena formateada codificada en UTF-8 por el puerto UART."""
        if self.serial_port and self.serial_port.is_open:
            try:
                trama = f"{mensaje}\n".encode("utf-8")
                self.serial_port.write(trama)
                print(f"Tx -> {mensaje}")
            except Exception as e:
                print(f"Error al transmitir por UART: {e}")
        else:
            print(f"Simulación UART (Puerto cerrado) Tx -> {mensaje}")

    def validar_ubicacion(self, event=None):
        codigo_escaneado = self.entry_escaner.get().strip().upper()

        if codigo_escaneado == self.ubicacion_objetivo:
            msg = "OFFER"
            self.lbl_resultado.configure(
                text=msg,
                fg_color="#10B981",
                text_color="white",
            )
        else:
            msg = "MALA_UBIC"
            self.lbl_resultado.configure(
                text=msg,
                fg_color="#EF4444",
                text_color="white",
            )

        # Transmisión por el puerto serie COM9
        self.enviar_uart(msg)

        # Limpiar entrada y reenfocar
        self.entry_escaner.delete(0, "end")
        self.entry_escaner.focus_set()

    def on_closing(self):
        """Cierra el puerto serie limpiamente al cerrar la interfaz."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Puerto serial cerrado.")
        self.destroy()


if __name__ == "__main__":
    app = PickToLightCartApp()
    app.mainloop()