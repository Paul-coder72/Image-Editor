import tkinter as tk
from tkinter import filedialog, Menu, Canvas, messagebox, colorchooser, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageColor
import struct
from math import sin, cos, tan, pi, sqrt
import os
import ctypes

filtre_actif = None
image_orig = None  
image = None       
photo = None
current_zoom = 1.0 
drawing = False
draw_color = "black"
draw_thickness = 5
erasing = False
last_x = None
last_y = None
offset_x = 0
offset_y = 0
pan_start_x = None
pan_start_y = None

def filtre_inversé(triplet):
    r, g, b = triplet
    return (255 - r, 255 - g, 255 - b)

def filtre_niveau_de_gris(triplet):
    r, g, b = triplet
    gris = int(0.3 * r + 0.59 * g + 0.11 * b)
    return (gris, gris, gris)

def filtre_noir_et_blanc(triplet):
    r, g, b = triplet
    gris = int(0.3 * r + 0.59 * g + 0.11 * b)
    seuil = 128
    return (255, 255, 255) if gris > seuil else (0, 0, 0)

def filtre_sinus(triplet):
    r, g, b = triplet
    r = int(128 + 127 * sin(r / 255 * 2 * pi))
    g = int(128 + 127 * sin(g / 255 * 2 * pi))
    b = int(128 + 127 * sin(b / 255 * 2 * pi))
    return (r, g, b)

def filtre_cosinus(triplet):
    r, g, b = triplet
    r = int(128 + 127 * cos(r / 255 * 2 * pi))
    g = int(128 + 127 * cos(g / 255 * 2 * pi))
    b = int(128 + 127 * cos(b / 255 * 2 * pi))
    return (r, g, b)

def filtre_tangente(triplet):
    r, g, b = triplet
    r = int(128 + 127 * tan(r / 255 * 2 * pi))
    g = int(128 + 127 * tan(g / 255 * 2 * pi))
    b = int(128 + 127 * tan(b / 255 * 2 * pi))
    return (r, g, b)

def filtre_sepia(triplet):
    r, g, b = triplet
    r_new = int(r * 0.393 + g * 0.769 + b * 0.189)
    g_new = int(r * 0.349 + g * 0.686 + b * 0.168)
    b_new = int(r * 0.272 + g * 0.534 + b * 0.131)
    r_new = min(255, max(0, r_new))
    g_new = min(255, max(0, g_new))
    b_new = min(255, max(0, b_new))
    return (r_new, g_new, b_new)

def filtre_contraste(triplet):
    r, g, b = triplet
    facteur = 1.5  
    moyenne = (r + g + b) / 3 
    r_new = int((r - moyenne) * facteur + moyenne)
    g_new = int((g - moyenne) * facteur + moyenne)
    b_new = int((b - moyenne) * facteur + moyenne)
    return (min(255, max(0, r_new)), min(255, max(0, g_new)), min(255, max(0, b_new)))

def filtre_lumineux(triplet):
    r, g, b = triplet
    facteur = 1.2  
    return (min(255, int(r * facteur)),
            min(255, int(g * facteur)),
            min(255, int(b * facteur)))

def fast_inverse_sqrt(x):
    if x <= 0:
        return 0 
    threehalfs = 1.5
    x2 = x * 0.5
    packed_x = struct.pack('f', float(x))
    i = struct.unpack('I', packed_x)[0]
    i = 0x5f3759df - (i >> 1)
    packed_i = struct.pack('I', i)
    y = struct.unpack('f', packed_i)[0]
    y = y * (threehalfs - (x2 * y * y))
    return max(0, min(255, int(abs(y) * 255)))

def filtre_inverse_sqrt(triplet):
    r, g, b = triplet
    r_new = fast_inverse_sqrt(r)
    g_new = fast_inverse_sqrt(g)
    b_new = fast_inverse_sqrt(b)
    return (r_new, g_new, b_new)

def appliquer_filtre():
    global image, photo, image_orig
    if image_orig is None:
        return
    if filtre_actif == "défaut":
        image = image_orig.copy()
    else:
        image = image_orig.copy()
        pixels = image.load()
        for i in range(image.width):
            for j in range(image.height):
                pixel = pixels[i, j]
                if filtre_actif == "inverser":
                    pixels[i, j] = filtre_inversé(pixel)
                elif filtre_actif == "gris":
                    pixels[i, j] = filtre_niveau_de_gris(pixel)
                elif filtre_actif == "noir_et_blanc":
                    pixels[i, j] = filtre_noir_et_blanc(pixel)
                elif filtre_actif == "sinus":
                    pixels[i, j] = filtre_sinus(pixel)
                elif filtre_actif == "cosinus":
                    pixels[i, j] = filtre_cosinus(pixel)
                elif filtre_actif == "tangente":
                    pixels[i, j] = filtre_tangente(pixel)
                elif filtre_actif == "sepia":
                    pixels[i, j] = filtre_sepia(pixel)
                elif filtre_actif == "contraste":
                    pixels[i, j] = filtre_contraste(pixel)
                elif filtre_actif == "lumineux":
                    pixels[i, j] = filtre_lumineux(pixel)
                elif filtre_actif == "inverse_sqrt":
                    pixels[i, j] = filtre_inverse_sqrt(pixel)
    update_canvas(image)

def set_filtre(filtre):
    global filtre_actif
    filtre_actif = filtre
    appliquer_filtre()

def ouvrir_image():
    global image, image_orig, photo, filename, current_zoom
    filename = filedialog.askopenfilename(
        title="Ouvrir une image",
        filetypes=[("Fichiers images", "*.bmp *.jpg *.png")]
    )
    if filename:
        try:
            image_orig = Image.open(filename).convert("RGB")
        except Exception as e:
            print("Erreur lors de l'ouverture de l'image :", e)
            return
        current_zoom = 1.0 
        image = image_orig.copy()
        update_canvas(image)

def enregistrer_image_sous():
    if image:
        filename_save = filedialog.asksaveasfilename(
            title="Enregistrer l'image",
            defaultextension=".png",
            filetypes=[("Fichiers images", "*.bmp *.jpg *.png")]
        )
        if filename_save:
            try:
                image.save(filename_save)
                messagebox.showinfo("Enregistrement", "Image enregistrée avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement de l'image : {e}")

def enregistrer_image():
    global image
    if image is None:
        return
    if filename:
        try:
            image.save(filename)
            messagebox.showinfo("Enregistrement", "Image enregistrée avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement de l'image : {e}")
    else:
        enregistrer_image_sous()

def rotate_image(angle):
    global image, image_orig, current_zoom
    if image is None:
        return
    image = image.rotate(angle, expand=True)
    image_orig = image.copy()
    update_canvas(image)

def on_right_button_press(event):
    global pan_start_x, pan_start_y
    pan_start_x = event.x
    pan_start_y = event.y

def on_right_button_drag(event):
    global offset_x, offset_y, pan_start_x, pan_start_y
    if pan_start_x is not None and pan_start_y is not None:
        dx = event.x - pan_start_x
        dy = event.y - pan_start_y
        offset_x += dx
        offset_y += dy
        pan_start_x = event.x
        pan_start_y = event.y
        update_canvas(image)


def a_propos():
    try:
        with open("version.md", "r") as f:
            version = f.read()
    except Exception as e:
        version = "Inconnue"
    messagebox.showinfo("À propos", 
                        "Éditeur d'image\n"
                        f"Version {version}\n"
                        "© 2025")

def help():
    messagebox.showinfo("Contrôles", 
                        "Ouvrir une image: Fichier > Ouvrir\n"
                        "Enregistrer une image: Fichier > Enregistrer\n"
                        "Quitter: Fichier > Quitter\n"
                        "--------------------------------------------\n"
                        "Ajouter un filtre: Filtres > (Nom du filtre)\n"
                        "Aucun filtre: Filtres > Aucun\n"
                        "--------------------------------------------\n"
                        "Zoom: Utilisez la molette de la souris\n"
                        "Déplacer l'image: Clic droit + déplacer\n"
                        "--------------------------------------------\n"
                        "Dessin: Activez le mode dessin dans le menu Dessin"
                        "Gomme: Activez la gomme dans le menu Dessin"
                        "Couleur et taille: Menu Dessin\n"
                        )

def creer_image(nom):
    global image, image_orig, photo, current_zoom
    tailles = {
        "carré 16": (16, 16),
        "carré 32": (32, 32),
        "carré 64": (64, 64),
        "carré 128": (128, 128),
        "carré 256": (256, 256),
        "carré 512": (512, 512),
        "carré 1024": (1024, 1024),
        "carré 2048": (2048, 2048),
        "rectangle 9:16": (1080, 1920)
    }
    if nom in tailles:
        image = Image.new("RGB", tailles[nom], (255, 255, 255))
        image_orig = image.copy()
        update_canvas(image)

def creer_image_custom():
    global image, image_orig, photo, current_zoom
    x = simpledialog.askinteger("Largeur", "Entrez la largeur de l'image")
    y = simpledialog.askinteger("Hauteur", "Entrez la hauteur de l'image")
    if x and y:
        image = Image.new("RGB", (x, y), (255, 255, 255))
        image_orig = image.copy()
        update_canvas(image)

def draw_mode():
    global drawing
    drawing = not drawing

def erase_mode():
    global erasing
    erasing = not erasing

def pen_color_func():
    global draw_color
    color = colorchooser.askcolor()[1]
    if color:
        draw_color = color

def pen_thickness():
    global draw_thickness
    thickness = simpledialog.askinteger("Épaisseur", "Entrez l'épaisseur du crayon (1-50):", minvalue=1, maxvalue=50)
    if thickness:
        draw_thickness = thickness

def clear_drawing():
    global image, image_orig
    if image is not None:
        image = image_orig.copy()
        update_canvas(image)

def canvas_to_image_coords(x, y):
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    center_x = canvas_width / 2 + offset_x
    center_y = canvas_height / 2 + offset_y
    dx = x - center_x
    dy = y - center_y
    img_x = image.width / 2 + dx / current_zoom
    img_y = image.height / 2 + dy / current_zoom
    return img_x, img_y


def on_button_press(event):
    global last_x, last_y
    last_x, last_y = canvas_to_image_coords(event.x, event.y)

def on_button_release(event):
    global last_x, last_y
    last_x = None
    last_y = None

def draw(event):
    global image, draw_color, draw_thickness, erasing, last_x, last_y
    if image is not None and drawing:
        x_img, y_img = canvas_to_image_coords(event.x, event.y)
        draw_tool = ImageDraw.Draw(image)
        color_used = "white" if erasing else draw_color
        if last_x is not None and last_y is not None:
            draw_tool.line((last_x, last_y, x_img, y_img), fill=color_used, width=draw_thickness)
        else:
            draw_tool.ellipse((x_img - draw_thickness // 2, y_img - draw_thickness // 2,
                               x_img + draw_thickness // 2, y_img + draw_thickness // 2),
                              fill=color_used)
        update_canvas(image)
        last_x, last_y = x_img, y_img

def update_canvas(img):
    global photo, current_zoom
    if img is None:
        return
    new_width = int(img.width * current_zoom)
    new_height = int(img.height * current_zoom)
    if new_width <= 0 or new_height <= 0:
        return
    zoomed_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(zoomed_img)
    canvas.delete("all")
    cx = canvas.winfo_width() // 2 + offset_x
    cy = canvas.winfo_height() // 2 + offset_y
    canvas.create_image(cx, cy, anchor=tk.CENTER, image=photo)

    canvas.image = photo

def resize_image(zoom_factor):
    global current_zoom
    if image_orig is None:
        return
    current_zoom *= zoom_factor
    update_canvas(image)

root = tk.Tk()
root.geometry("800x600")
root.title("Éditeur d'image")

myappid = 'paul.imageeditor.200'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

try:
    icon = Image.open("icon.ico")
    icon = ImageTk.PhotoImage(icon)
    root.iconphoto(True, icon)
    if os.path.exists("icon.ico"):
        root.iconbitmap("icon.ico")
except Exception as e:
    print("Erreur lors du chargement de l'icône:", e)

canvas = Canvas(root, width=800, height=600)
canvas.pack(fill=tk.BOTH, expand=True)
canvas.bind("<ButtonPress-1>", on_button_press)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<ButtonRelease-1>", on_button_release)
root.update()

image = Image.new("RGB", (800, 600), "white")
image_orig = image.copy()
update_canvas(image)

menubar = Menu(root)

menu_file = Menu(menubar, tearoff=0)
menu_file.add_command(label="Ouvrir", command=ouvrir_image)
menu_file.add_command(label="Enregistrer", command=enregistrer_image)
menu_file.add_command(label="Enregistrer sous", command=enregistrer_image_sous)
menu_file.add_separator()
menu_file.add_command(label="Quitter", command=root.quit)
menubar.add_cascade(label="Fichier", menu=menu_file)

menu_filter = Menu(menubar, tearoff=0)
menu_filter.add_command(label="Aucun", command=lambda: set_filtre("défaut"))
menu_filter.add_separator()
menu_filter.add_command(label="Inverser", command=lambda: set_filtre("inverser"))
menu_filter.add_separator()
menu_filter.add_command(label="Sinus", command=lambda: set_filtre("sinus"))
menu_filter.add_command(label="Cosinus", command=lambda: set_filtre("cosinus"))
menu_filter.add_command(label="Tangente", command=lambda: set_filtre("tangente"))
menu_filter.add_command(label="Inverse sqrt", command=lambda: set_filtre("inverse_sqrt"))
menu_filter.add_separator()
menu_filter.add_command(label="Niveaux de gris", command=lambda: set_filtre("gris"))
menu_filter.add_command(label="Noir et blanc", command=lambda: set_filtre("noir_et_blanc"))
menu_filter.add_command(label="Sépia", command=lambda: set_filtre("sepia"))
menu_filter.add_separator()
menu_filter.add_command(label="Contraste", command=lambda: set_filtre("contraste"))
menu_filter.add_command(label="Luminosité", command=lambda: set_filtre("lumineux"))
menubar.add_cascade(label="Filtres", menu=menu_filter)

menu_new = Menu(menubar, tearoff=0)
menu_new.add_command(label="Personnalisé", command=creer_image_custom)
menu_new.add_separator()
menu_new.add_command(label="32x32", command=lambda: creer_image("carré 32"))
menu_new.add_command(label="64x64", command=lambda: creer_image("carré 64"))
menu_new.add_command(label="128x128", command=lambda: creer_image("carré 128"))
menu_new.add_command(label="256x256", command=lambda: creer_image("carré 256"))
menu_new.add_command(label="512x512", command=lambda: creer_image("carré 512"))
menu_new.add_command(label="1024x1024", command=lambda: creer_image("carré 1024"))
menu_new.add_command(label="2048x2048", command=lambda: creer_image("carré 2048"))
menu_new.add_separator()
menu_new.add_command(label="9:16", command=lambda: creer_image("rectangle 9:16"))
menubar.add_cascade(label="Nouveau", menu=menu_new)

menu_draw = Menu(menubar, tearoff=0)
menu_draw.add_command(label="Activer/désactiver le mode dessin", command=draw_mode)
menu_draw.add_command(label="Activer/désactiver la gomme", command=erase_mode)
menu_draw.add_separator()
menu_draw.add_command(label="Couleur du crayon", command=pen_color_func)
menu_draw.add_command(label="Épaisseur du crayon", command=pen_thickness)
menu_draw.add_separator()
menu_draw.add_command(label="Effacer le dessin", command=clear_drawing)
menubar.add_cascade(label="Dessin", menu=menu_draw)

menu_view = Menu(menubar, tearoff=0)
menu_view.add_command(label="Pivoter à droite", command=lambda: rotate_image(-90))
menu_view.add_command(label="Pivoter à gauche", command=lambda: rotate_image(90))
menubar.add_cascade(label="Affichage", menu=menu_view)

menu_help = Menu(menubar, tearoff=0)
menu_help.add_command(label="À propos", command=a_propos)
menu_help.add_command(label="Guide d'utilisation", command=help)
menubar.add_cascade(label="Aide", menu=menu_help)

root.config(menu=menubar)

root.bind("<MouseWheel>", lambda event: resize_image(1.1) if event.delta > 0 else resize_image(0.9))
root.bind("<Button-4>", lambda event: resize_image(1.1))
root.bind("<Button-5>", lambda event: resize_image(0.9))

canvas.bind("<ButtonPress-3>", on_right_button_press)
canvas.bind("<B3-Motion>", on_right_button_drag)


root.mainloop()
