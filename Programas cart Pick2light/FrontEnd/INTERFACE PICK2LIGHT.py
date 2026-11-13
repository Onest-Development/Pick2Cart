from PIL import Image
import customtkinter as ctk

# Configuración básica del tema
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Crear ventana principal
app = ctk.CTk()
app.title("Ejemplo Simplificado con Imagen")
app.geometry("450x320")


def imprimir_hola():
    print("hola")


# Cargar la imagen usando CTkImage nativo
img = Image.open("media\\logo3.jpg")
mi_imagen = ctk.CTkImage(light_image=img, dark_image=img, size=(35, 35))

# --- FRAME 1: TÍTULO ---
frame_titulo = ctk.CTkFrame(app)
frame_titulo.pack(pady=10, padx=20, fill="x")

# Colocar en el Label
label_imagen = ctk.CTkLabel(frame_titulo, image=mi_imagen, text="")
label_imagen.pack(side="left", padx=10)

label_titulo = ctk.CTkLabel(frame_titulo,
    text="Mi Título con Imagen",
    font=ctk.CTkFont(size=18, weight="bold"),
)
label_titulo.pack(side="left", padx=10, pady=10)


# --- FRAME 2: CONTENIDO CON BOTÓN ---
frame_contenido = ctk.CTkFrame(app)
frame_contenido.pack(pady=10, padx=20, fill="both", expand=True)

boton_hola = ctk.CTkEntry(frame_contenido)
boton_hola.pack(expand=True)

app.mainloop()