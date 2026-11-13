import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PickToLightCartSim(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Pick to Light Cart - Simulación WMS/Cart")
        self.geometry("850x780")
        self.resizable(False, False)

        # =========================================================================
        # PASO 1: CONCENTRADO DE OLEADA Y OPTIMIZACIÓN DE RUTA
        # =========================================================================
        # Datos brutos de la oleada
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
        self.sku_confirmado = False

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

        # Controles de Entrada (Escáner de Ubicación / SKU / Confirmaciones)
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

        # Botón auxiliar para el Paso 4.1 (Confirmación con Botón Físico en Ubicación)
        self.btn_boton_ubicacion = ctk.CTkButton(
            self.frame_superior,
            text="🔘 Presionar Botón Físico de Ubicación (Paso 4.1)",
            fg_color="#D97706",
            hover_color="#B45309",
            command=self.confirmar_boton_ubicacion,
        )

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

        # Mini Frame Superior
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

        # Botón de Confirmación en Carro (Confirmar Put)
        btn_confirmar = ctk.CTkButton(
            sub_frame,
            text="✓ Put",
            width=45,
            state="disabled",
            command=lambda c=id_celda: self.confirmar_put_cart(c),
        )
        btn_confirmar.pack(side="right", padx=3, pady=4)

        # Centro de la celda
        lbl_contenido = ctk.CTkLabel(
            celda_frame,
            text="VACÍO",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        lbl_contenido.pack(expand=True)

        self.celdas[id_celda] = {
            "frame": celda_frame,
            "display": lbl_num_display,
            "boton": btn_confirmar,
            "label": lbl_contenido,
            "sub_frame": sub_frame,
        }

    # =========================================================================
    # LÓGICA PASO A PASO
    # =========================================================================

    def actualizar_interfaz_cart(self):
        """PASO 2: Muestra Pasillo (2.1), Pedido (2.2) y Ubicación (2.3)"""

        # Ocultar botón de confirmación de ubicación por defecto
        self.btn_boton_ubicacion.pack_forget()

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
            # PASO 3.1: Muestra Cantidad de SKUs
            self.lbl_instruccion.configure(
                text=f"PASO 3.3: Escanea el SKU [{item['sku']}] (Req: {item['cant']} pzs)",
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
                self.entry_datos.delete(0, "end")
                self.actualizar_interfaz_cart()
            else:
                self.lbl_instruccion.configure(
                    text=f"❌ Ubicación Incorrecta. Escanea: '{ubicacion_str}'",
                    text_color="#EF4444",
                )

        # 3.3: ESPERA CONFIRMACIÓN DE SKUS CON ESCÁNER
        elif self.sub_paso == "CONFIRMAR_SKU":
            if entrada == item["sku"]:
                self.entry_datos.delete(0, "end")
                self.entry_datos.configure(state="disabled")
                self.btn_accion.configure(state="disabled")

                # 3.2: CART MUESTRA CON LEDS DONDE COLOCAR SKU
                self.encender_led_cart(
                    item["pos_cart"], item["cant"], item["sku"]
                )

                # PASO 4: Mostrar botón de confirmación en ubicación
                self.lbl_instruccion.configure(
                    text=f"PASO 4: Coloca {item['cant']} pzs en [{item['pos_cart']}]. ¿Están completos los SKUs en ubicación?",
                    text_color="#10B981",
                )
                self.btn_boton_ubicacion.pack(pady=(0, 10))
            else:
                self.lbl_instruccion.configure(
                    text=f"❌ SKU Incorrecto. Escanea: '{item['sku']}'",
                    text_color="#EF4444",
                )

    def encender_led_cart(self, pos_cart, cantidad, sku):
        """3.2 Cart muestra con leds verde la posición donde colocar SKU"""
        celda = self.celdas[pos_cart]
        celda["frame"].configure(fg_color="#15803D", border_color="#22C55E")
        celda["display"].configure(
            text=str(cantidad), fg_color="#22C55E", text_color="black"
        )
        celda["label"].configure(
            text=f"{sku}\n({cantidad} PZS)", text_color="white"
        )
        celda["boton"].configure(
            state="normal",
            fg_color="#22C55E",
            text_color="black",
            hover_color="#16A34A",
        )

    def confirmar_boton_ubicacion(self):
        """4.1 Confirmar con botón en ubicación"""
        self.btn_boton_ubicacion.pack_forget()
        item = self.ruta_recoleccion[self.indice_item]

        # Apagar la alerta verde del cart al confirmar en ubicación
        celda = self.celdas[item["pos_cart"]]
        celda["frame"].configure(
            fg_color=("gray85", "gray17"), border_color="#333333"
        )
        celda["display"].configure(
            text="0", fg_color="#1E293B", text_color="#94A3B8"
        )
        celda["boton"].configure(state="disabled")

        # EVALUACIÓN DE BUCLES (Paso 4):
        # ¿Hay más pedidos/SKUs en la misma ubicación, pasillo o siguientes?
        self.indice_item += 1

        if self.indice_item < len(self.ruta_recoleccion):
            item_siguiente = self.ruta_recoleccion[self.indice_item]

            # Si es la misma ubicación
            if (
                    item["pasillo"] == item_siguiente["pasillo"]
                    and item["lado"] == item_siguiente["lado"]
                    and item["fondo"] == item_siguiente["fondo"]
                    and item["piso"] == item_siguiente["piso"]
            ):
                self.sub_paso = "CONFIRMAR_SKU"  # Permanece en la ubicación, actualiza pedido
            else:
                self.sub_paso = (
                    "CONFIRMAR_UBICACION"  # Cambia ubicación o pasillo
                )

            self.actualizar_interfaz_cart()
        else:
            self.paso_5_oleada_terminada()

    def confirmar_put_cart(self, id_celda):
        """Acción física opcional del usuario en el carrito."""
        pass

    # =========================================================================
    # PASO 5, 6 Y 7: OLEADA TERMINADA Y ÁREA DE ENTREGA
    # =========================================================================

    def paso_5_oleada_terminada(self):
        """5. Oleada terminada: Iluminación Azul Completa"""
        self.lbl_info_ruta.configure(
            text="¡RECOLECCIÓN COMPLETA!",
            font=ctk.CTkFont(size=16, weight="bold"),
        )

        # 5.1 Dirigirse al área de entrega
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
                celda["frame"].configure(
                    fg_color="#065F46", border_color="#10B981"
                )
                celda["display"].configure(
                    text="||||", fg_color="#10B981", text_color="black"
                )
                celda["boton"].configure(
                    text="Entregar",
                    state="normal",
                    fg_color="#10B981",
                    text_color="black",
                    command=lambda c=id_celda: self.entregar_pedido_celda(c),
                )

    def entregar_pedido_celda(self, id_celda):
        """6.3 Entregados todos los pedidos. Cart Vacío"""
        celda = self.celdas[id_celda]
        celda["frame"].configure(
            fg_color=("gray85", "gray17"), border_color="#333333"
        )
        celda["display"].configure(
            text="0", fg_color="#1E293B", text_color="#94A3B8"
        )
        celda["label"].configure(text="VACÍO", text_color="gray")
        celda["boton"].configure(state="disabled")

        # Verificar si todas las celdas quedaron vacías
        todas_vacias = all(
            c["label"].cget("text") == "VACÍO" for c in self.celdas.values()
        )
        if todas_vacias:
            # 7. Cart reinicia y está listo para un nuevo concentrado
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