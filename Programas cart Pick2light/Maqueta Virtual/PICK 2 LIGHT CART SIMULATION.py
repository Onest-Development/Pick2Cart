import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PickToLightSim(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema Pick to Light - Simulación")
        self.geometry("750x700")
        self.resizable(False, False)

        # -------------------------------------------------------------
        # DATOS DE LA SIMULACIÓN (Oleada de Trabajo)
        # -------------------------------------------------------------
        self.oleada_actual = "Oleada #104 - Pedidos Express"
        self.tareas = [
            {"ubicacion": "P-01", "sku": "SKU-101", "destino": "Sección 1", "cantidad": 3},
            {"ubicacion": "P-04", "sku": "SKU-205", "destino": "Sección 3", "cantidad": 1},
            {"ubicacion": "P-02", "sku": "SKU-309", "destino": "Sección 2", "cantidad": 5},
            {"ubicacion": "P-03", "sku": "SKU-404", "destino": "Sección 4", "cantidad": 2},
        ]
        self.indice_tarea = 0
        self.paso_actual = "UBICACION"  # Estados: "UBICACION" o "SKU"

        # Grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_columnconfigure(0, weight=1)

        # ==========================================
        # 1. FRAME SUPERIOR (Instrucciones)
        # ==========================================
        self.frame_superior = ctk.CTkFrame(self, corner_radius=10)
        self.frame_superior.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

        # Mensaje de Bienvenida / Oleada
        self.lbl_bienvenida = ctk.CTkLabel(
            self.frame_superior,
            text="¡Bienvenido al Sistema Pick to Light!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#3B82F6"
        )
        self.lbl_bienvenida.pack(pady=(12, 2))

        # Subtítulo (Ubicación / Instrucción)
        self.lbl_subtitulo = ctk.CTkLabel(
            self.frame_superior,
            text="Iniciando...",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_subtitulo.pack(pady=(0, 10))

        # Entrada de datos (Escáner)
        frame_input = ctk.CTkFrame(self.frame_superior, fg_color="transparent")
        frame_input.pack(pady=(0, 15))

        self.entry_datos = ctk.CTkEntry(
            frame_input,
            placeholder_text="Escanea o escribe aquí...",
            width=280,
            font=ctk.CTkFont(size=13)
        )
        self.entry_datos.pack(side="left", padx=5)
        self.entry_datos.bind("<Return>", lambda event: self.procesar_escaneo())

        self.btn_validar = ctk.CTkButton(
            frame_input,
            text="Confirmar",
            width=90,
            command=self.procesar_escaneo
        )
        self.btn_validar.pack(side="left", padx=5)

        # ==========================================
        # 2. FRAME INFERIOR (Matriz 2x2 Put-Wall)
        # ==========================================
        self.frame_inferior = ctk.CTkFrame(self, corner_radius=10)
        self.frame_inferior.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")

        self.frame_inferior.grid_rowconfigure((0, 1), weight=1)
        self.frame_inferior.grid_columnconfigure((0, 1), weight=1)

        self.celdas = {}
        posiciones = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for i, (fila, col) in enumerate(posiciones, start=1):
            id_celda = f"Sección {i}"
            self.crear_celda_matriz(fila, col, id_celda)

        # Iniciar la primera instrucción
        self.actualizar_instruccion()

    def crear_celda_matriz(self, fila, col, id_celda):
        """Crea el contenedor de cada posición del Put-Wall."""
        celda_frame = ctk.CTkFrame(self.frame_inferior, corner_radius=8, border_width=2, border_color="#333333")
        celda_frame.grid(row=fila, column=col, padx=10, pady=10, sticky="nsew")

        # Sub-frame superior de controles
        sub_frame = ctk.CTkFrame(celda_frame, fg_color=("gray85", "gray20"), height=35)
        sub_frame.pack(fill="x", padx=5, pady=5)

        lbl_id = ctk.CTkLabel(sub_frame, text=id_celda, font=ctk.CTkFont(size=12, weight="bold"))
        lbl_id.pack(side="left", padx=10)

        # Indicador numérico (Display de luz)
        lbl_num_display = ctk.CTkLabel(
            sub_frame,
            text="0",
            width=40,
            fg_color="#1E293B",
            text_color="#94A3B8",
            corner_radius=5,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        lbl_num_display.pack(side="right", padx=(0, 5), pady=4)

        btn_confirmar = ctk.CTkButton(
            sub_frame,
            text="✓ Put",
            width=50,
            state="disabled",
            command=lambda c=id_celda: self.confirmar_deposito(c)
        )
        btn_confirmar.pack(side="right", padx=5, pady=4)

        # Área central de la celda
        lbl_estado = ctk.CTkLabel(
            celda_frame,
            text="ESPERANDO...",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        lbl_estado.pack(expand=True)

        self.celdas[id_celda] = {
            "frame": celda_frame,
            "display": lbl_num_display,
            "boton": btn_confirmar,
            "estado": lbl_estado
        }

    # ==========================================
    # LÓGICA DE CONTROL DEL FLUJO
    # ==========================================

    def actualizar_instruccion(self):
        """Actualiza los avisos del frame superior según el avance."""
        if self.indice_tarea >= len(self.tareas):
            self.lbl_bienvenida.configure(text=f"¡{self.oleada_actual} Finalizada!", text_color="#10B981")
            self.lbl_subtitulo.configure(text="Sin tareas pendientes. Buen trabajo.", text_color="gray")
            self.entry_datos.configure(state="disabled")
            self.btn_validar.configure(state="disabled")
            return

        tarea = self.tareas[self.indice_tarea]
        self.lbl_bienvenida.configure(text=f"Trabajando en: {self.oleada_actual}", text_color="#3B82F6")

        if self.paso_actual == "UBICACION":
            self.lbl_subtitulo.configure(
                text=f"1. Dirígete a Ubicación: [{tarea['ubicacion']}] e ingrésala para confirmar",
                text_color="#F59E0B"
            )
        elif self.paso_actual == "SKU":
            self.lbl_subtitulo.configure(
                text=f"2. Ubicación OK. Escanea el SKU: [{tarea['sku']}]",
                text_color="#3B82F6"
            )

    def procesar_escaneo(self):
        """Valida lo que el usuario escribió en la entrada superior."""
        entrada = self.entry_datos.get().strip().upper()
        if not entrada:
            return

        tarea = self.tareas[self.indice_tarea]

        # VALIDAR PASO 1: UBICACIÓN
        if self.paso_actual == "UBICACION":
            if entrada == tarea["ubicacion"]:
                self.paso_actual = "SKU"
                self.entry_datos.delete(0, 'end')
                self.actualizar_instruccion()
            else:
                self.lbl_subtitulo.configure(
                    text=f"❌ Ubicación Incorrecta. Ve a: [{tarea['ubicacion']}]",
                    text_color="#EF4444"
                )

        # VALIDAR PASO 2: SKU
        elif self.paso_actual == "SKU":
            if entrada == tarea["sku"]:
                self.entry_datos.delete(0, 'end')
                self.encender_luz_matriz(tarea["destino"], tarea["cantidad"])
            else:
                self.lbl_subtitulo.configure(
                    text=f"❌ SKU Incorrecto. Debe ser: [{tarea['sku']}]",
                    text_color="#EF4444"
                )

    def encender_luz_matriz(self, destino, cantidad):
        """Activa la celda verde (Pick to Light) correspondiente."""
        celda = self.celdas[destino]

        # Efecto visual Pick To Light (Verde Encendido)
        celda["frame"].configure(fg_color="#15803D", border_color="#22C55E")
        celda["display"].configure(text=str(cantidad), fg_color="#22C55E", text_color="black")
        celda["estado"].configure(text=f"COLOCAR {cantidad} PZS", text_color="white")
        celda["boton"].configure(state="normal", fg_color="#22C55E", text_color="black", hover_color="#16A34A")

        self.lbl_subtitulo.configure(
            text=f"Luz encendida en [{destino}]. Coloca {cantidad} pzs y presiona '✓ Put'",
            text_color="#22C55E"
        )
        self.entry_datos.configure(state="disabled")
        self.btn_validar.configure(state="disabled")

    def confirmar_deposito(self, id_celda):
        """Apaga la luz y avanza a la siguiente tarea de la oleada."""
        celda = self.celdas[id_celda]

        # Resetear celda a estado normal (Apagado)
        celda["frame"].configure(fg_color=("gray85", "gray17"), border_color="#333333")
        celda["display"].configure(text="0", fg_color="#1E293B", text_color="#94A3B8")
        celda["estado"].configure(text="COMPLETADO", text_color="#10B981")
        celda["boton"].configure(state="disabled", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

        # Avanzar en la cola de tareas
        self.indice_tarea += 1
        self.paso_actual = "UBICACION"

        self.entry_datos.configure(state="normal")
        self.btn_validar.configure(state="normal")
        self.actualizar_instruccion()


if __name__ == "__main__":
    app = PickToLightSim()
    app.mainloop()