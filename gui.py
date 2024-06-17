import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from tkinter import ttk
from tkinter import font as tkFont
from main import main, stop_process, cleanup
from PIL import ImageFont, Image, ImageDraw
import os
from debug import setup_logger
from text_handler import TextHandler
import threading


STOP_FLAG = False
stop_event = threading.Event()


def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if file_path:
        excel_path.set(file_path)
        log_text.insert(tk.END, f"Fichier sélectionné: {file_path}\n")


def run_script():
    global STOP_FLAG
    STOP_FLAG = False
    stop_event.clear()
    file_path = excel_path.get()
    mode = processing_mode.get()
    if not file_path:
        messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Excel.")
        return
    log_text.insert(tk.END, "Démarrage du script...\n")
    run_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    thread = threading.Thread(target=run_main, args=(file_path, mode))
    thread.start()


def run_main(file_path, mode):
    try:
        main(file_path, mode, progress_callback=update_progress)
        log_text.insert(tk.END, "Script terminé.\n")
    except Exception as e:
        log_text.insert(tk.END, f"Erreur: {e}\n")
    finally:
        run_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)


def stop_script():
    stop_process()
    log_text.insert(tk.END, "Arrêt du script demandé...\n")


def update_progress(value):
    progress['value'] = value
    root.update_idletasks()


# Création de la fenêtre principale
root = tk.Tk()
root.title("RPA GUI")
root.geometry("800x600")
root.configure(bg="#003049")


# Charger les polices Play
regular_font_path = os.path.join("data", "Play", "Play-Regular.ttf")
bold_font_path = os.path.join("data", "Play", "Play-Bold.ttf")


# Charger les polices avec PIL
play_regular = tkFont.Font(family="Play", size=12)
play_bold = tkFont.Font(family="Play", size=12, weight="bold")


# Enregistrer les polices avec les noms corrects pour les utiliser dans ttk.Style
tkFont.nametofont("TkDefaultFont").configure(size=12, family="Play")
root.option_add("*TButton*Font", "Play-Bold")
root.option_add("*TLabel*Font", "Play-Regular")


# Appliquer un style
style = ttk.Style()
style.theme_use('clam')


# Personnaliser les styles
style.configure('TButton', foreground='#ffffff', background='#7289da', padding=10, borderwidth=1)
style.map('TButton', background=[('active', '#99aab5')])
style.configure('TLabel', background='#2c2f33', foreground='#ffffff', padding=10)
style.configure('TFrame', background='#23272a')
style.configure('TText', background='#2c2f33', foreground='#ffffff')
style.configure('TEntry', background='#2c2f33', foreground='#ffffff', insertbackground='#ffffff')


# Créer un cadre principal
main_frame = ttk.Frame(root, padding="20 20 20 20", style="TFrame")
main_frame.pack(fill=tk.BOTH, expand=True)


# Variable pour stocker le chemin du fichier Excel
excel_path = tk.StringVar()
processing_mode = tk.StringVar(value="multi")


# Label d'instruction
instruction_label = ttk.Label(main_frame, text="Sélectionnez le fichier Excel :", style="TLabel")
instruction_label.grid(column=0, row=0, pady=10, padx=10, sticky="W")


# Bouton pour sélectionner le fichier
select_button = ttk.Button(main_frame, text="Sélectionner le fichier Excel", command=select_file)
select_button.grid(column=1, row=0, pady=10, padx=10, sticky="E")


# Radio buttons pour choisir le mode de traitement
single_mode_radio = ttk.Radiobutton(main_frame, text="Single Traitement", variable=processing_mode, value="single")
single_mode_radio.grid(column=0, row=1, pady=10, padx=10, sticky="W")
multi_mode_radio = ttk.Radiobutton(main_frame, text="Multi Traitement", variable=processing_mode, value="multi")
multi_mode_radio.grid(column=1, row=1, pady=10, padx=10, sticky="W")


# Zone de texte pour afficher les logs
log_text = scrolledtext.ScrolledText(main_frame, width=80, height=20, font=play_regular, bg='#23272a', fg='#ffffff', insertbackground='#ffffff')
log_text.grid(column=0, row=2, pady=10, padx=10, columnspan=2)


# Configurez le logger pour utiliser le TextHandler
text_handler = TextHandler(log_text)
logger = setup_logger(text_handler)


# Bouton pour lancer le script
run_button = ttk.Button(main_frame, text="Lancer le script", command=run_script)
run_button.grid(column=0, row=3, pady=10, padx=10, columnspan=2)


# Bouton pour arrêter le script
stop_button = ttk.Button(main_frame, text="Arrêter le script", command=stop_script)
stop_button.grid(column=0, row=4, pady=10, padx=10, columnspan=2)
stop_button.config(state=tk.DISABLED)


# Ajout d'une barre de progression
progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
progress.grid(column=0, row=5, pady=10, padx=10, columnspan=2)


root.mainloop()



