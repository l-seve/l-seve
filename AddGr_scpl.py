import csv
import unicodedata
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

def normalize_string(s):
    """ Normalise une chaîne : suppression des accents, mise en minuscule et suppression des espaces inutiles. """
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower().strip()) if unicodedata.category(c) != 'Mn')

def load_model_file(model_file_path):
    """ Charge le fichier modèle et crée un dictionnaire {nom de groupe normalisé : GroupId}. """
    model_data = {}
    with open(model_file_path, mode='r', encoding='utf-8-sig') as file:  # 'utf-8-sig' pour éviter les problèmes d'encodage
        reader = csv.DictReader(file)
        
        # Vérification des en-têtes
        print(f"En-têtes du fichier modèle : {reader.fieldnames}")
        if 'GroupName' not in reader.fieldnames or 'GroupId' not in reader.fieldnames:
            raise KeyError("Les en-têtes 'GroupName' et 'GroupId' doivent être présents dans le fichier modèle.")

        for row in reader:
            group_name_normalized = normalize_string(row['GroupName'])
            model_data[group_name_normalized] = row['GroupId']
            print(f"Ajouté dans le modèle : '{group_name_normalized}' -> '{row['GroupId']}'")

    return model_data

def update_target_file(target_file_path, model_data):
    """ Met à jour le fichier cible en remplaçant les noms de groupe par les GroupId correspondants. """
    updated_rows = []
    
    with open(target_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # Vérification des en-têtes du fichier cible
        fieldnames = reader.fieldnames
        print(f"En-têtes du fichier cible : {fieldnames}")

        if 'groupe' not in fieldnames:
            raise KeyError("L'en-tête 'groupe' doit être présent dans le fichier cible.")

        for row in reader:
            group_normalized = normalize_string(row['groupe'])
            print(f"Valeur normalisée du fichier cible : '{row['groupe']}' -> '{group_normalized}'")

            if group_normalized in model_data:
                print(f"✔ Correspondance trouvée : {group_normalized} -> {model_data[group_normalized]}")
                row['groupe'] = model_data[group_normalized]
            else:
                print(f"❌ Aucune correspondance trouvée pour : {group_normalized}")

            # Ajout du préfixe "agr-" si la valeur de groupe est numérique
            if row['groupe'].isdigit():
                row['groupe'] = f"agr-{row['groupe']}"
                print(f"🔹 Ajout du préfixe : {row['groupe']}")

            updated_rows.append(row)

    # Création du nouveau fichier avec "_mis_à_jour"
    new_file_path = os.path.join(
        os.path.dirname(target_file_path),
        os.path.splitext(os.path.basename(target_file_path))[0] + '_mis_à_jour.csv'
    )

    with open(new_file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"✅ Le fichier mis à jour a été enregistré : {new_file_path}")

def main():
    """ Fonction principale permettant de sélectionner les fichiers et d'effectuer la mise à jour. """
    Tk().withdraw()  # Cacher la fenêtre Tkinter
    model_file_path = askopenfilename(title="Sélectionnez le fichier modèle", filetypes=[("CSV files", "*.csv")])
    target_file_path = askopenfilename(title="Sélectionnez le fichier cible", filetypes=[("CSV files", "*.csv")])

    if model_file_path and target_file_path:
        try:
            model_data = load_model_file(model_file_path)
            update_target_file(target_file_path, model_data)
        except KeyError as e:
            print(f"Erreur: {e}")
    else:
        print("❌ Sélection de fichier annulée.")

if __name__ == "__main__":
    main()
