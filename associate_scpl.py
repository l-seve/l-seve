import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Variable pour stocker le dossier de sortie
output_dir = ""

def browse_template_file():
    path = filedialog.askopenfilename(
        title="Sélectionnez le fichier modèle",
        filetypes=[("CSV files", "*.csv")]
    )
    template_entry.delete(0, tk.END)
    template_entry.insert(0, path)

def browse_identifiants_file():
    path = filedialog.askopenfilename(
        title="Sélectionnez le fichier des identifiants",
        filetypes=[("CSV files", "*.csv")]
    )
    ident_entry.delete(0, tk.END)
    ident_entry.insert(0, path)

def generate_masslink_file():
    template_path = template_entry.get()
    ident_path = ident_entry.get()

    if not template_path or not ident_path:
        messagebox.showwarning("Champs manquants", "Veuillez sélectionner les deux fichiers.")
        return

    try:
        with open(template_path, mode='r', newline='', encoding='utf-8') as template_file:
            reader = csv.DictReader(template_file)
            fieldnames = reader.fieldnames
            template_row = next(reader, None)
        if not template_row:
            messagebox.showerror("Erreur", "Le fichier modèle est vide ou mal formaté.")
            return
    except Exception as e:
        messagebox.showerror("Erreur de lecture du modèle", str(e))
        return

    try:
        with open(ident_path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except Exception as e:
        messagebox.showerror("Erreur de lecture des identifiants", str(e))
        return

    unique_rows = []
    seen = set()
    for row in rows:
        row_str = str(sorted((str(k), str(v)) for k, v in row.items()))
        if row_str not in seen:
            seen.add(row_str)
            unique_rows.append(row)

    rows = [row for row in unique_rows if any(value.strip() for value in row.values())]

    # Générer le chemin de sortie avec le dossier sélectionné
    filename = "Kheiron_Seve_MassLink_Final.csv"
    output_path = os.path.join(output_dir, filename)

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in rows:
                device_id = row.get("identification", "").strip()
                group_val = row.get("groupe", "").strip()
                group_ids = (group_val + "/null") if group_val else ""

                new_row = template_row.copy()
                new_row["Device_Identifiant"] = device_id
                new_row["Device_Nom"] = device_id
                new_row["DTwinName"] = device_id
                new_row["DTwinDesc"] = device_id
                new_row["GroupIds"] = group_ids

                writer.writerow(new_row)

        messagebox.showinfo("Succès", f"✅ Fichier généré avec succès :\n{output_path}")
        root.destroy()
    except Exception as e:
        messagebox.showerror("Erreur d'écriture", str(e))

# -------- Interface graphique --------
root = tk.Tk()
root.title("Générateur MassLink")
root.geometry("600x200")
root.resizable(False, False)

# Sélectionner le dossier de sortie au démarrage
output_dir = filedialog.askdirectory(title="Sélectionnez le dossier où enregistrer le fichier final")
if not output_dir:
    messagebox.showinfo("Info", "Aucun dossier sélectionné. Fermeture du script.")
    root.destroy()
    exit()

# Fichier modèle
tk.Label(root, text="Fichier modèle :").pack(anchor='w', padx=10, pady=(10, 0))
template_frame = tk.Frame(root)
template_frame.pack(fill='x', padx=10)
template_entry = tk.Entry(template_frame, width=60)
template_entry.pack(side='left', expand=True, fill='x')
tk.Button(template_frame, text="Parcourir...", command=browse_template_file).pack(side='left', padx=5)

# Fichier d'identifiants
tk.Label(root, text="Fichier des identifiants :").pack(anchor='w', padx=10, pady=(10, 0))
ident_frame = tk.Frame(root)
ident_frame.pack(fill='x', padx=10)
ident_entry = tk.Entry(ident_frame, width=60)
ident_entry.pack(side='left', expand=True, fill='x')
tk.Button(ident_frame, text="Parcourir...", command=browse_identifiants_file).pack(side='left', padx=5)

# Bouton générer
tk.Button(root, text="Générer le fichier final MassLink", command=generate_masslink_file,
          bg="green", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

root.mainloop()
