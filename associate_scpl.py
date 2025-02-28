import csv
import tkinter as tk
from tkinter import filedialog

# Initialiser tkinter
root = tk.Tk()
root.withdraw()  # Masquer la fenêtre principale

# Ouvrir une boîte de dialogue pour sélectionner le fichier CSV de base
input_csv_path = filedialog.askopenfilename(
    title="Sélectionnez le fichier CSV de base",
    filetypes=[("CSV files", "*.csv")]
)

# Vérifier si un fichier a été sélectionné
if not input_csv_path:
    print("Aucun fichier sélectionné.")
    exit()

# Chemin vers le fichier CSV final
output_csv_path = 'C:/Users/ramal/OneDrive - RAGNI SAS/Bureau/Technique/Scripts_off_inté/Final/Kheiron_Seve_MassLink_Final.csv'

# Lire le fichier CSV de base
with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

# Vérifier combien de lignes sont lues
print(f"Nombre de lignes lues dans le fichier CSV de base : {len(rows)}")

# Supprimer les doublons (si nécessaire)
rows = [dict(t) for t in {tuple(d.items()) for d in rows}]

# Vérifier à nouveau combien de lignes après avoir supprimé les doublons
print(f"Nombre de lignes après suppression des doublons : {len(rows)}")

# Filtrer les lignes vides ou invalides
rows = [row for row in rows if any(value.strip() for value in row.values())]

# Vérifier à nouveau après nettoyage des lignes vides
print(f"Nombre de lignes après nettoyage : {len(rows)}")

# Créer le fichier CSV final avec le modèle spécifié
with open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
    fieldnames = [
        "Device_Identifiant", "Device_Nom", "DTwinTemplateId", "DecoderBindingReference",
        "DTwinName", "DTwinDesc", "TimeZoneInfoId", "UpdateDataTime", "AccessGroupIds",
        "NotificationGroupIds", "GroupIds", "RetentionPolicyId", "PlanReference",
        "PricingPeriod", "AutoRenew"
    ]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in rows:
        device_id = row.get("Identification")
        GroupIds = (row["groupe"] + "/null") if row["groupe"] != "" else ""
        new_row = {
            "Device_Identifiant": device_id,
            "Device_Nom": device_id,
            "DTwinTemplateId": "atp-1",
            "DecoderBindingReference": "92155369-a06c-4aa0-9aad-2ccd0cfc8c1e",
            "DTwinName": device_id,
            "DTwinDesc": device_id,
            "TimeZoneInfoId": "Romance Standard Time",
            "UpdateDataTime": "True",
            "AccessGroupIds": "rag-2, rag-3",
            "NotificationGroupIds": "ant-1, ant-2",
            "GroupIds": GroupIds,
            "RetentionPolicyId": "arp-1",
            "PlanReference": "KSP KHEIRON Service Platform M",
            "PricingPeriod": "Yearly",
            "AutoRenew": "True"
        }
        writer.writerow(new_row)

print(f"Le fichier CSV final a été créé avec succès : {output_csv_path}")