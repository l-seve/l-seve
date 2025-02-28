import requests
import json
import time
import logging
import os
import base64
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

# 🔹 Configuration du logger (fichier pour enregistrer les erreurs)
LOG_FILE = "errors_TTN.log"
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# 🔐 Tokens API pour les clients
CLIENT_TOKENS = {
    "SophiaTech": {
        "token": "NNSXS.AF6P5ZHYJE4QJTG3VDDFX2O5GCJAUMQCLXJTGDQ.HSOVIXQ4WBF625T6T5E7TR42BODTLQB3AWAUC2XHBKYYLMUV3JQA",
        "application_id": "seve"
    },
    "Seve": {
        "token": "NNSXS.L6OZI3USDIIX237PFVIZYCUQOUMQTULL3Y5P7UA.VXBSN2KCWMLEIXNG2G7232HSV6PXTVLU44E6B4VESVHMFVD5UENA",
        "application_id": "seve-1"
    }
}

# ⏳ Nombre maximum de tentatives en cas d’échec
MAX_RETRIES = 2

# 🎯 Paramètres du downlink
DOWNLINK_DATA = {
    "f_port": 50,  # Port utilisé par le device
    "frm_payload": "",  # Payload en Base64 (sera mis à jour dynamiquement)
    "priority": "HIGH"
}

# Payload prédéfinie pour le port 51
PREDEFINED_PAYLOADS = {
    51: "FE"  # Reboot
}

# Liste des f_port disponibles
F_PORTS = [50, 51, 60]

# 🔄 Fonction pour convertir une payload hexadécimale en Base64
def hex_to_base64(hex_payload):
    binary_payload = bytes.fromhex(hex_payload)
    base64_payload = base64.b64encode(binary_payload).decode('utf-8')
    return base64_payload

# Variable globale pour contrôler l'arrêt des requêtes
stop_requests = False

# Fonction pour arrêter les requêtes
def stop_requests_func():
    global stop_requests
    stop_requests = True
    log_message("🛑 Requêtes arrêtées par l'utilisateur.")

# 🔄 Fonction pour envoyer un downlink avec retries
def send_downlink(device_id, hex_payload, auth_token, application_id):
    global stop_requests
    url = f"https://eu1.cloud.thethings.network/api/v3/as/applications/{application_id}/devices/{device_id}/down/push"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Convertir la payload hexadécimale en Base64
    DOWNLINK_DATA["frm_payload"] = hex_to_base64(hex_payload)
    data = {"downlinks": [DOWNLINK_DATA]}

    for attempt in range(1, MAX_RETRIES + 1):
        if stop_requests:
            log_message("🛑 Requêtes arrêtées.")
            return

        try:
            log_message(f"🔄 Tentative {attempt} d'envoi de downlink à {device_id} avec payload {hex_payload}")
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                log_message(f"✅ Downlink envoyé à {device_id} avec payload {hex_payload}")
                return True  # Succès, on sort de la boucle

            else:
                error_msg = f"❌ Erreur {response.status_code} pour {device_id}: {response.text}"
                log_message(error_msg)
                logging.error(error_msg)  # Ajout de l'erreur au log

        except requests.exceptions.RequestException as e:
            error_msg = f"⚠️ Erreur réseau pour {device_id} (Tentative {attempt}/{MAX_RETRIES}): {e}"
            log_message(error_msg)
            logging.error(error_msg)  # Ajout de l'erreur au log
        
        time.sleep(5)  # Pause avant la prochaine tentative

    log_message(f"🚨 Échec d'envoi après {MAX_RETRIES} tentatives pour {device_id}")
    messagebox.showerror("Échec", f"🚨 Échec d'envoi après {MAX_RETRIES} tentatives pour {device_id}")

# Fonction pour sélectionner le fichier JSON contenant les device IDs
def select_device_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        file_name_label.config(text=f"Fichier sélectionné: {os.path.basename(file_path)}")
        with open(file_path, 'r') as file:
            devices = json.load(file)
            device_ids = [device["device_id"] for device in devices]
            device_id_var.set("choisir")  # Sélectionner "choisir" par défaut
            device_id_menu['menu'].delete(0, 'end')
            device_id_menu['menu'].add_command(label="tout", command=lambda: display_all_device_ids(device_ids))
            for device_id in device_ids:
                device_id_menu['menu'].add_command(label=device_id, command=lambda v=device_id: device_id_var.set(v))

# Fonction pour afficher tous les device IDs dans le widget de log
def display_all_device_ids(device_ids):
    device_id_var.set("tout")
    log_text.config(state=tk.NORMAL)
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "Tous les device IDs:\n")
    for device_id in device_ids:
        log_text.insert(tk.END, f"{device_id}\n")
    log_text.config(state=tk.DISABLED)

# Fonction pour gérer l'envoi depuis l'interface graphique
def send_downlink_from_gui():
    global stop_requests
    stop_requests = False
    stop_button.grid(row=5, columnspan=2, pady=10)  # Afficher le bouton "Stop requests"
    client = client_var.get()
    device_id = device_id_var.get()
    f_port = int(f_port_var.get())
    hex_payload = payload_entry.get()

    log_message(f"🔄 Début de l'envoi de downlink pour le client {client} sur le port {f_port}")

    # Utiliser la payload prédéfinie si le port est 51
    if f_port == 51:
        hex_payload = PREDEFINED_PAYLOADS[f_port]  # Reboot
        payload_entry.delete(0, tk.END)
        payload_entry.insert(0, hex_payload)

    DOWNLINK_DATA["f_port"] = f_port  # Mettre à jour le f_port sélectionné
    client_info = CLIENT_TOKENS.get(client)
    if client_info:
        auth_token = client_info["token"]
        application_id = client_info["application_id"]
        if device_id == "tout":
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if file_path:
                log_message(f"📂 Fichier sélectionné: {os.path.basename(file_path)}")
                with open(file_path, 'r') as file:
                    devices = json.load(file)
                    for device in devices:
                        if stop_requests:
                            break
                        send_downlink(device["device_id"], hex_payload, auth_token, application_id)
                        time.sleep(60)  # Pause de 1 minute entre chaque downlink
        else:
            send_downlink(device_id, hex_payload, auth_token, application_id)
    else:
        messagebox.showerror("Erreur", "Client non valide ou token non trouvé.")
    stop_button.grid_remove()  # Masquer le bouton "Stop requests" après l'exécution
    log_message("🔄 Fin de l'envoi de downlink")

# Fonction pour mettre à jour le token en fonction du client sélectionné
def update_auth_token(*args):
    client = client_var.get()
    global AUTH_TOKEN
    AUTH_TOKEN = CLIENT_TOKENS.get(client)["token"]

# Fonction pour mettre à jour la payload en fonction du port sélectionné
def update_payload(*args):
    f_port = int(f_port_var.get())
    if f_port == 51:
        payload_entry.delete(0, tk.END)
        payload_entry.insert(0, PREDEFINED_PAYLOADS[f_port])
    else:
        payload_entry.delete(0, tk.END)

# Fonction pour ajouter un message au log
def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, f"{timestamp} - {message}\n")
    log_text.config(state=tk.DISABLED)
    log_text.see(tk.END)

# Création de la fenêtre principale
root = tk.Tk()
root.title("TTN Downlink Sender")

# Création des widgets
tk.Label(root, text="Client:").grid(row=0, column=0, padx=10, pady=10)
client_var = tk.StringVar(root)
client_var.set("choisir")  # Valeur par défaut
client_menu = tk.OptionMenu(root, client_var, *CLIENT_TOKENS.keys())
client_menu.grid(row=0, column=1, padx=10, pady=10)
client_var.trace("w", update_auth_token)  # Appeler update_auth_token lorsque la sélection change

tk.Label(root, text="Device ID:").grid(row=1, column=0, padx=10, pady=10)
device_id_var = tk.StringVar(root)
device_id_menu = tk.OptionMenu(root, device_id_var, "")
device_id_menu.grid(row=1, column=1, padx=10, pady=10)
select_file_button = tk.Button(root, text="Sélectionner fichier JSON", command=select_device_file)
select_file_button.grid(row=1, column=2, padx=10, pady=10)

# Ajout du label pour afficher le nom du fichier sélectionné
file_name_label = tk.Label(root, text="")
file_name_label.grid(row=2, column=2, padx=10, pady=10)

device_id_var.set("choisir")  # Valeur par défaut

tk.Label(root, text="F Port:").grid(row=2, column=0, padx=10, pady=10)
f_port_var = tk.StringVar(root)
f_port_var.set("choisir")  # Valeur par défaut
f_port_menu = tk.OptionMenu(root, f_port_var, *F_PORTS)
f_port_menu.grid(row=2, column=1, padx=10, pady=10)
f_port_var.trace("w", update_payload)  # Appeler update_payload lorsque la sélection change

tk.Label(root, text="Payload (Hex):").grid(row=3, column=0, padx=10, pady=10)
payload_entry = tk.Entry(root)
payload_entry.grid(row=3, column=1, padx=10, pady=10)

send_button = tk.Button(root, text="Envoyer Downlink", command=send_downlink_from_gui)
send_button.grid(row=4, columnspan=2, pady=10)

# Ajout du bouton "Stop requests"
stop_button = tk.Button(root, text="Stop requests", command=stop_requests_func)
stop_button.grid(row=5, columnspan=2, pady=10)
stop_button.grid_remove()  # Masquer le bouton au démarrage

# Ajout du widget de log
log_text = tk.Text(root, state=tk.DISABLED, height=10, wrap=tk.WORD)
log_text.grid(row=6, columnspan=3, padx=10, pady=10)

# Lancement de la boucle principale de l'interface graphique
root.mainloop()