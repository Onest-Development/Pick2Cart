import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PickToLightCartSim(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Pick to Light Cart - Simulación WMS/Cart")
        self.geometry("850x780")
        #self.resizable(False, False)

        # =========================================================================
        # PASO 1: CONCENTRADO DE OLEADA Y OPTIMIZACIÓN DE RUTA
        # =========================================================================
        raw_items = [
            {
                "pasillo": "P01",
                "lado": "L1",
                "fondo": "F02",
                "piso": "N1",
                "sku": "SKU-B10",
                "pedido": "Ped-01",
                "pos_cart": "Sección 1",
                "cant": 2,
            },
            {
                "pasillo": "P01",
                "lado": "L1",
                "fondo": "F01",
                "piso": "N1",
                "sku": "SKU-A01",
                "pedido": "Ped-01",
                "pos_cart": "Sección 1",
                "cant": 1,
            },
            {
                "pasillo": "P01",
                "lado": "L1",
                "fondo": "F01",
                "piso": "N1",
                "sku": "SKU-A01",
                "pedido": "Ped-02",
                "pos_cart": "Sección 2",
                "cant": 3,
            },
            {
                "pasillo": "P02",
                "lado": "L2",
                "fondo": "F03",
                "piso": "N2",
                "sku": "SKU-C30",
                "pedido": "Ped-03",
                "pos_cart": "Sección 3",
                "cant": 1,
            },
        ]

        # 1.1, 1.2 y 1.3: Ordenamiento estricto por Pasillo -> Lado -> Fondo -> Piso
        self.ruta_recoleccion = sorted(
            raw_items,
            key=lambda x: (x["pasillo"], x["lado"], x["fondo"], x["piso"]),
        )

        self.indice_item = 0
        self.sub_paso = (
            "CONFIRMAR_UBICACION"  # 'CONFIRMAR_UBICACION' o 'CONFIRMAR_SKU'
        )
        self.piezas_escaneadas = 0  # Contador de piezas escaneadas

        # Configuración del Grid Principal
        self.grid_rowconfigure(0, weight=1)  # Frame superior
        self.grid_rowconfigure(1, weight=3)  # Frame inferior (Cart / Put-Wall)
        self.grid_columnconfigure(0, weight=1)

        # ==========================================
        # FRAME SUPERIOR (Interface Cart)
        # ==========================================
        self.frame_superior = ctk.CTkFrame(self, corner_radius=10)
        self.frame_superior.grid(
            row=0, column=0, padx=20, pady=(15, 10), sticky="nsew"
        )

        self.lbl_titulo = ctk.CTkLabel(
            self.frame_superior,
            text="CART PICK-TO-LIGHT — OLEADA #2026",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#3B82F6",
        )
        self.lbl_titulo.pack(pady=(10, 2))

        # 2.1, 2.2 y 2.3: Despliegue de Pasillo, Pedido y Ubicación
        self.lbl_info_ruta = ctk.CTkLabel(
            self.frame_superior, text="", font=ctk.CTkFont(size=14)
        )
        self.lbl_info_ruta.pack(pady=2)

        self.lbl_instruccion = ctk.CTkLabel(
            self.frame_superior,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#F59E0B",
        )
        self.lbl_instruccion.pack(pady=4)

        # Controles de Entrada (Escáner de Ubicación / SKU)
        frame_input = ctk.CTkFrame(self.frame_superior, fg_color="transparent")
        frame_input.pack(pady=(5, 10))

        self.entry_datos = ctk.CTkEntry(
            frame_input,
            placeholder_text="Escanear...",
            width=260,
            font=ctk.CTkFont(size=13),
        )
        self.entry_datos.pack(side="left", padx=5)
        self.entry_datos.bind("<Return>", lambda e: self.procesar_escaner())

        self.btn_accion = ctk.CTkButton(
            frame_input,
            text="Confirmar",
            width=100,
            command=self.procesar_escaner,
        )
        self.btn_accion.pack(side="left", padx=5)

        # ==========================================
        # FRAME INFERIOR (Matriz 2x2 - Carrito 4 Cajas)
        # ==========================================
        self.frame_inferior = ctk.CTkFrame(self, corner_radius=10)
        self.frame_inferior.grid(
            row=1, column=0, padx=20, pady=(10, 15), sticky="nsew"
        )

        self.frame_inferior.grid_rowconfigure((0, 1), weight=1)
        self.frame_inferior.grid_columnconfigure((0, 1), weight=1)

        self.celdas = {}
        posiciones = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for i, (fila, col) in enumerate(posiciones, start=1):
            id_celda = f"Sección {i}"
            self.crear_celda_cart(fila, col, id_celda)

        # Inicializar Paso 2
        self.actualizar_interfaz_cart()

    def crear_celda_cart(self, fila, col, id_celda):
        """Crea cada sección del carrito de recolección."""
        celda_frame = ctk.CTkFrame(
            self.frame_inferior,
            corner_radius=8,
            border_width=2,
            border_color="#333333",
        )
        celda_frame.grid(row=fila, column=col, padx=10, pady=10, sticky="nsew")

        # Mini Frame Superior dentro de la Celda
        sub_frame = ctk.CTkFrame(
            celda_frame, fg_color=("gray85", "gray20"), height=35
        )
        sub_frame.pack(fill="x", padx=5, pady=5)

        lbl_id = ctk.CTkLabel(
            sub_frame,
            text=id_celda,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        lbl_id.pack(side="left", padx=8)

        # Indicador LED Display
        lbl_num_display = ctk.CTkLabel(
            sub_frame,
            text="0",
            width=35,
            fg_color="#1E293B",
            text_color="#94A3B8",
            corner_radius=4,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        lbl_num_display.pack(side="right", padx=5, pady=4)

        # Botón para entrega final (Modo Paso 6)
        btn_entrega = ctk.CTkButton(
            sub_frame,
            text="Entregar",
            width=65,
            state="disabled",
        )

        # Centro de la celda
        lbl_contenido = ctk.CTkLabel(
            celda_frame,
            text="VACÍO",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        lbl_contenido.pack(expand=True)

        # BOTÓN FÍSICO EN UBICACIÓN (Paso 4.1): Se ubica en la parte inferior de la celda
        btn_fisico_ubicacion = ctk.CTkButton(
            celda_frame,
            text="🔘 Botón Ubicación (4.1)",
            fg_color="#D97706",
            hover_color="#B45309",
            state="disabled",
            command=lambda c=id_celda: self.confirmar_boton_ubicacion(c),
        )

        self.celdas[id_celda] = {
            "frame": celda_frame,
            "display": lbl_num_display,
            "btn_entrega": btn_entrega,
            "btn_fisico": btn_fisico_ubicacion,
            "label": lbl_contenido,
            "sub_frame": sub_frame,
        }

    # =========================================================================
    # LÓGICA PASO A PASO
    # =========================================================================

    def actualizar_interfaz_cart(self):
        """PASO 2: Muestra Pasillo (2.1), Pedido (2.2) y Ubicación (2.3)"""

        if self.indice_item >= len(self.ruta_recoleccion):
            self.paso_5_oleada_terminada()
            return

        item = self.ruta_recoleccion[self.indice_item]
        ubicacion_str = f"{item['pasillo']}-{item['lado']}-{item['fondo']}-{item['piso']}"

        self.lbl_info_ruta.configure(
            text=f"Pasillo: [{item['pasillo']}]  |  Ubicación: [{ubicacion_str}]  |  Pedido: [{item['pedido']}]"
        )

        if self.sub_paso == "CONFIRMAR_UBICACION":
            self.lbl_instruccion.configure(
                text=f"PASO 3: Confirma la Ubicación escaneando: '{ubicacion_str}'",
                text_color="#F59E0B",
            )
            self.entry_datos.configure(state="normal")
            self.btn_accion.configure(state="normal")

        elif self.sub_paso == "CONFIRMAR_SKU":
            self.lbl_instruccion.configure(
                text=f"PASO 3.3: Escanea SKU [{item['sku']}] ({self.piezas_escaneadas}/{item['cant']} pzs escaneadas)",
                text_color="#3B82F6",
            )
            self.entry_datos.configure(state="normal")
            self.btn_accion.configure(state="normal")

    def procesar_escaner(self):
        entrada = self.entry_datos.get().strip().upper()
        if not entrada:
            return

        item = self.ruta_recoleccion[self.indice_item]
        ubicacion_str = f"{item['pasillo']}-{item['lado']}-{item['fondo']}-{item['piso']}"

        # 3. CONFIRMAR UBICACIÓN
        if self.sub_paso == "CONFIRMAR_UBICACION":
            if entrada == ubicacion_str:
                self.sub_paso = "CONFIRMAR_SKU"
                self.piezas_escaneadas = 0
                self.entry_datos.delete(0, "end")
                self.actualizar_interfaz_cart()
            else:
                self.lbl_instruccion.configure(
                    text=f"❌ Ubicación Incorrecta. Escanea: '{ubicacion_str}'",
                    text_color="#EF4444",
                )

        # 3.3: ESPERA CONFIRMACIÓN DE SKUS CON ESCÁNER (UN CONTEO POR CADA PIEZA)
        elif self.sub_paso == "CONFIRMAR_SKU":
            if entrada == item["sku"]:
                self.piezas_escaneadas += 1
                self.entry_datos.delete(0, "end")

                # 3.2: ILUMINAR LED DE LA POSICIÓN CORRESPONDIENTE
                self.encender_led_cart(
                    item["pos_cart"],
                    self.piezas_escaneadas,
                    item["cant"],
                    item["sku"],
                )

                # SI AÚN FALTAN PIEZAS POR ESCANEAR
                if self.piezas_escaneadas < item["cant"]:
                    self.lbl_instruccion.configure(
                        text=f"✔ Pieza registrada. Escanea SKU [{item['sku']}] ({self.piezas_escaneadas}/{item['cant']} pzs)",
                        text_color="#3B82F6",
                    )
                else:
                    # TODAS LAS PIEZAS FUERON ESCANEEADAS: ACTIVAR BOTÓN FÍSICO EN LA UBICACIÓN
                    self.entry_datos.configure(state="disabled")
                    self.btn_accion.configure(state="disabled")

                    celda = self.celdas[item["pos_cart"]]
                    celda["btn_fisico"].pack(pady=(0, 8))
                    celda["btn_fisico"].configure(
                        state="normal",
                        fg_color="#D97706",
                        hover_color="#B45309",
                    )

                    self.lbl_instruccion.configure(
                        text=f"PASO 4: Conteo completo ({item['cant']}/{item['cant']}). Presiona el Botón de Ubicación en la {item['pos_cart']}",
                        text_color="#10B981",
                    )
            else:
                self.lbl_instruccion.configure(
                    text=f"❌ SKU Incorrecto. Escanea: '{item['sku']}'",
                    text_color="#EF4444",
                )

    def encender_led_cart(self, pos_cart, escaneadas, total, sku):
        """3.2 Cart muestra con leds verde la posición donde colocar SKU"""
        celda = self.celdas[pos_cart]
        celda["frame"].configure(fg_color="#15803D", border_color="#22C55E")
        celda["display"].configure(
            text=f"{escaneadas}/{total}", fg_color="#22C55E", text_color="black"
        )
        celda["label"].configure(
            text=f"{sku}\n({escaneadas}/{total} PZS)", text_color="white"
        )

    def confirmar_boton_ubicacion(self, id_celda):
        """4.1 Confirmar con botón en ubicación"""
        item = self.ruta_recoleccion[self.indice_item]

        # Ocultar y desactivar el botón físico de ubicación
        celda = self.celdas[id_celda]
        celda["btn_fisico"].pack_forget()
        celda["btn_fisico"].configure(state="disabled")

        # Restaurar apariencia del cart
        celda["frame"].configure(
            fg_color=("gray85", "gray17"), border_color="#333333"
        )
        celda["display"].configure(
            text="0", fg_color="#1E293B", text_color="#94A3B8"
        )

        # EVALUACIÓN DE BUCLES (Paso 4):
        self.indice_item += 1

        if self.indice_item < len(self.ruta_recoleccion):
            item_siguiente = self.ruta_recoleccion[self.indice_item]

            # Si la siguiente tarea es en la misma ubicación exacta
            if (
                    item["pasillo"] == item_siguiente["pasillo"]
                    and item["lado"] == item_siguiente["lado"]
                    and item["fondo"] == item_siguiente["fondo"]
                    and item["piso"] == item_siguiente["piso"]
            ):
                self.sub_paso = "CONFIRMAR_SKU"
            else:
                self.sub_paso = "CONFIRMAR_UBICACION"

            self.piezas_escaneadas = 0
            self.actualizar_interfaz_cart()
        else:
            self.paso_5_oleada_terminada()

    # =========================================================================
    # PASO 5, 6 Y 7: OLEADA TERMINADA Y ÁREA DE ENTREGA
    # =========================================================================

    def paso_5_oleada_terminada(self):
        """5. Oleada terminada: Iluminación Azul Completa"""
        self.lbl_info_ruta.configure(
            text="¡RECOLECCIÓN COMPLETA!",
            font=ctk.CTkFont(size=16, weight="bold"),
        )

        self.lbl_instruccion.configure(
            text="PASO 5.1 & 5.3: Dirígete al área de entrega y confirma llegada.",
            text_color="#60A5FA",
        )

        self.entry_datos.configure(state="disabled")
        self.btn_accion.configure(
            text="Llegada a Entrega",
            state="normal",
            command=self.paso_6_area_entrega,
        )

        # 5.2 Cart se ilumina por completo con color azul
        for celda in self.celdas.values():
            celda["btn_fisico"].pack_forget()
            celda["frame"].configure(fg_color="#1E3A8A", border_color="#3B82F6")
            celda["display"].configure(
                fg_color="#3B82F6", text_color="white", text="OK"
            )

    def paso_6_area_entrega(self):
        """6. Área de Entrega: Códigos de barras y descarga"""
        self.lbl_titulo.configure(
            text="ÁREA DE ENTREGA DE PEDIDOS", text_color="#10B981"
        )
        self.lbl_info_ruta.configure(
            text="Entrega los pedidos escaneando o confirmando cada posición"
        )
        self.lbl_instruccion.configure(
            text="PASO 6.2: Pedidos listos para entrega (Ubicaciones iluminadas)",
            text_color="#10B981",
        )

        self.btn_accion.pack_forget()
        self.entry_datos.pack_forget()

        # 6.1 Muestra pedidos con Barcodes e ilumina ubicación
        for id_celda, celda in self.celdas.items():
            if celda["label"].cget("text") != "VACÍO":
                celda["btn_entrega"].pack(side="right", padx=5, pady=4)
                celda["frame"].configure(
                    fg_color="#065F46", border_color="#10B981"
                )
                celda["display"].configure(
                    text="||||", fg_color="#10B981", text_color="black"
                )
                celda["btn_entrega"].configure(
                    state="normal",
                    fg_color="#10B981",
                    text_color="black",
                    command=lambda c=id_celda: self.entregar_pedido_celda(c),
                )

    def entregar_pedido_celda(self, id_celda):
        """6.3 Entregados todos los pedidos. Cart Vacío"""
        celda = self.celdas[id_celda]
        celda["btn_entrega"].pack_forget()
        celda["frame"].configure(
            fg_color=("gray85", "gray17"), border_color="#333333"
        )
        celda["display"].configure(
            text="0", fg_color="#1E293B", text_color="#94A3B8"
        )
        celda["label"].configure(text="VACÍO", text_color="gray")

        # Verificar si todas las celdas quedaron vacías
        todas_vacias = all(
            c["label"].cget("text") == "VACÍO" for c in self.celdas.values()
        )
        if todas_vacias:
            self.lbl_instruccion.configure(
                text="PASO 6.3 & 7: Cart Vacío. Reiniciando sistema...",
                text_color="#3B82F6",
            )
            self.after(2500, self.reiniciar_cart)

    def reiniciar_cart(self):
        """7. Reinicio de la aplicación"""
        self.destroy()
        app = PickToLightCartSim()
        app.mainloop()


if __name__ == "__main__":
    app = PickToLightCartSim()
    app.mainloop()