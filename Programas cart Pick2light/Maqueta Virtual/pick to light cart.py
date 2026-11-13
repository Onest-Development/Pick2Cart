import customtkinter as ctk

# Configuración del tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Interfaz CustomTkinter")
        self.geometry("700x700")
        self.resizable(False, False)

        # Configuración del Grid Principal (2 filas x 1 columna)
        self.grid_rowconfigure(0, weight=1)  # Frame superior
        self.grid_rowconfigure(1, weight=3)  # Frame inferior (matriz)
        self.grid_columnconfigure(0, weight=1)

        # ==========================================
        # 1. FRAME SUPERIOR
        # ==========================================
        self.frame_superior = ctk.CTkFrame(self, corner_radius=10)
        self.frame_superior.grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="nsew"
        )

        self.lbl_titulo = ctk.CTkLabel(
            self.frame_superior,
            text="Panel de Control",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.lbl_titulo.pack(pady=(15, 2))

        # Subtítulo (Modificable)
        self.lbl_subtitulo = ctk.CTkLabel(
            self.frame_superior,
            text="Subtítulo editable desde código",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="gray",
        )
        self.lbl_subtitulo.pack(pady=(0, 10))

        # Entrada de datos
        self.entry_datos = ctk.CTkEntry(
            self.frame_superior,
            placeholder_text="Escribe tus datos aquí...",
            width=350,
        )
        self.entry_datos.pack(pady=(0, 15))

        # ==========================================
        # 2. FRAME INFERIOR (Matriz 2x2)
        # ==========================================
        self.frame_inferior = ctk.CTkFrame(self, corner_radius=10)
        self.frame_inferior.grid(
            row=1, column=0, padx=20, pady=(10, 20), sticky="nsew"
        )

        # Configuración del Grid 2x2 uniforme
        self.frame_inferior.grid_rowconfigure((0, 1), weight=1)
        self.frame_inferior.grid_columnconfigure((0, 1), weight=1)

        # Diccionario para guardar referencias a las entradas de cada celda
        self.controles = {}

        # Construir las 4 celdas usando un bucle
        posiciones = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for i, (fila, col) in enumerate(posiciones, start=1):
            self.crear_celda_matriz(fila, col, id_celda=f"Sección {i}")

    def crear_celda_matriz(self, fila, col, id_celda):
        """Crea el contenedor de la celda y el pequeño frame superior con entrada y botón."""

        # Frame contenedor de la casilla
        celda = ctk.CTkFrame(self.frame_inferior, corner_radius=8)
        celda.grid(row=fila, column=col, padx=10, pady=10, sticky="nsew")

        # --- PEQUEÑO FRAME SUPERIOR DE CONTROLES ---
        sub_frame = ctk.CTkFrame(celda, fg_color=("gray85", "gray20"), height=40)
        sub_frame.pack(fill="x", padx=5, pady=5)

        # Entrada numérica
        entry_num = ctk.CTkEntry(sub_frame, width=60, placeholder_text="0")
        entry_num.insert(0, "0")  # Valor por defecto
        entry_num.pack(side="left", padx=(8, 5), pady=5)

        # Botón de confirmación (utiliza 'lambda' enviando la clave única)
        btn_confirmar = ctk.CTkButton(
            sub_frame,
            text="✓",
            width=30,
            command=lambda c=id_celda: self.confirmar_numero(c),
        )
        btn_confirmar.pack(side="left", padx=(0, 8), pady=5)

        # Título de la sección
        lbl_titulo_seccion = ctk.CTkLabel(
            sub_frame, text=id_celda, font=ctk.CTkFont(size=12, weight="bold")
        )
        lbl_titulo_seccion.pack(side="right", padx=10)

        # --- ÁREA INFERIOR DE LA CELDA ---
        lbl_resultado = ctk.CTkLabel(
            celda,
            text="Valor: 0",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        lbl_resultado.pack(expand=True, pady=10)

        # Guardar referencias para acceder dinámicamente más tarde
        self.controles[id_celda] = {
            "entry": entry_num,
            "label": lbl_resultado,
        }

    def confirmar_numero(self, id_celda):
        """Acción que se ejecuta al presionar el botón de confirmación en cualquier celda."""
        valor = self.controles[id_celda]["entry"].get()
        self.controles[id_celda]["label"].configure(
            text=f"Valor guardado: {valor}", text_color="#1f538d"
        )
        print(f"[{id_celda}] Nuevo valor ingresado: {valor}")

    def actualizar_subtitulo(self, nuevo_texto: str):
        """Método público para editar el subtítulo del frame superior."""
        self.lbl_subtitulo.configure(text=nuevo_texto)


if __name__ == "__main__":
    app = App()
    app.mainloop()