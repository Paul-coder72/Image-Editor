﻿import tkinter as tk
from tkinter import filedialog, Menu, Canvas, messagebox
from PIL import Image, ImageTk
import struct
from math import sin, cos, tan, pi, sqrt
import os
import ctypes



filtre_actif = None
image_orig = None  
image = None       
photo = None
current_zoom = 1.0 

def set_filtre(filtre):
    global filtre_actif
    filtre_actif = filtre
    appliquer_filtre()

def filtre_inversé(triplet):
    r, v, b = triplet
    return (255 - r, 255 - v, 255 - b)

def filtre_niveau_de_gris(triplet):
    r, v, b = triplet
    gris = int(0.3 * r + 0.59 * v + 0.11 * b)
    return (gris, gris, gris)

def filtre_noir_et_blanc(triplet):
    r, v, b = triplet
    gris = int(0.3 * r + 0.59 * v + 0.11 * b)
    seuil = 128
    return (255, 255, 255) if gris > seuil else (0, 0, 0)

def filtre_sinus(triplet):
    r, v, b = triplet
    r = int(128 + 127 * sin(r / 255 * 2 * pi))
    v = int(128 + 127 * sin(v / 255 * 2 * pi))
    b = int(128 + 127 * sin(b / 255 * 2 * pi))
    return (r, v, b)

def filtre_cosinus(triplet):
    r, v, b = triplet
    r = int(128 + 127 * cos(r / 255 * 2 * pi))
    v = int(128 + 127 * cos(v / 255 * 2 * pi))
    b = int(128 + 127 * cos(b / 255 * 2 * pi))
    return (r, v, b)

def filtre_tangente(triplet):
    r, v, b = triplet
    r = int(128 + 127 * tan(r / 255 * 2 * pi))
    v = int(128 + 127 * tan(v / 255 * 2 * pi))
    b = int(128 + 127 * tan(b / 255 * 2 * pi))
    return (r, v, b)

def filtre_sepia(triplet):
    r, v, b = triplet
    r_new = int(r * 0.393 + v * 0.769 + b * 0.189)
    v_new = int(r * 0.349 + v * 0.686 + b * 0.168)
    b_new = int(r * 0.272 + v * 0.534 + b * 0.131)
    
    r_new = min(255, max(0, r_new))
    v_new = min(255, max(0, v_new))
    b_new = min(255, max(0, b_new))

    return (r_new, v_new, b_new)

def filtre_contraste(triplet):
    r, v, b = triplet
    facteur = 1.5  
    moyenne = (r + v + b) / 3 
    r_new = int((r - moyenne) * facteur + moyenne)
    v_new = int((v - moyenne) * facteur + moyenne)
    b_new = int((b - moyenne) * facteur + moyenne)

    return (min(255, max(0, r_new)), min(255, max(0, v_new)), min(255, max(0, b_new)))

def filtre_lumineux(triplet):
    r, v, b = triplet
    facteur = 1.2  
    return (
        min(255, int(r * facteur)),
        min(255, int(v * facteur)),
        min(255, int(b * facteur))
    )

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
    r, v, b = triplet
    r_new = fast_inverse_sqrt(r)
    v_new = fast_inverse_sqrt(v)
    b_new = fast_inverse_sqrt(b)

    return (r_new, v_new, b_new)

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

def enregistrer_image():
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

def a_propos():
    try:
        with open("version.md", "r") as f:
            version = f.read()
    except Exception as e:
        version = "Inconnue"
    messagebox.showinfo("À propos", 
                        "Éditeur d'image\n"
                        f"Version {version}"
                        "© 2025 ")

def help():
    messagebox.showinfo("Contrôles", 
                        "Ouvrir une image: Fichier > Ouvrir\n"
                        "Enregistrer une image: Fichier > Enregistrer\n"
                        "Quitter: Fichier > Quitter\n"
                        "--------------------------------------------\n"
                        "Ajouter un filtre: Menu Filtres\n"
                        "Aucun filtre: Filtres > Aucun\n"
                        "--------------------------------------------\n"
                        "Zoom: Utilisez la molette de la souris")

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
    canvas.update() 
    center_x = canvas.winfo_width() // 2
    center_y = canvas.winfo_height() // 2
    canvas.create_image(center_x, center_y, anchor=tk.CENTER, image=photo)
    canvas.image = photo

def appliquer_filtre():
    global image, photo
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

def resize_image(zoom_factor):
    global current_zoom
    if image_orig is None:
        return
    current_zoom *= zoom_factor
    update_canvas(image)

root = tk.Tk()
root.geometry("800x600")
root.title("Éditeur d'image")

myappid = 'paul.imageeditor.121'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

icon = Image.open("icon.ico")
icon = ImageTk.PhotoImage(icon)
 
root.iconphoto(True, icon)

icon_path = "icon.ico"
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

canvas = Canvas(root, width=800, height=600)
canvas.pack(fill=tk.BOTH, expand=True)
root.update() 


menubar = Menu(root)

menu_file = Menu(menubar, tearoff=0)
menu_file.add_command(label="Ouvrir", command=ouvrir_image)
menu_file.add_command(label="Enregistrer", command=enregistrer_image)
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

menu_help = Menu(menubar, tearoff=0) 
menu_help.add_command(label="À propos", command=a_propos)
menu_help.add_command(label="Help", command=help)
menubar.add_cascade(label="Aide", menu=menu_help)

root.config(menu=menubar)


root.bind("<MouseWheel>", lambda event: resize_image(1.1) if event.delta > 0 else resize_image(0.9))
root.bind("<Button-4>", lambda event: resize_image(1.1))  # Pour Linux
root.bind("<Button-5>", lambda event: resize_image(0.9))  # Pour Linux

root.mainloop()
