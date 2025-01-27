import pandas as pd
import re
from tkinter import Tk, Label, Button, Listbox, MULTIPLE, END, filedialog, messagebox, Frame
import os
import webbrowser
import json
from tkhtmlview import HTMLLabel

class ExcelToCSVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel to CSV Converter")
        self.root.geometry("800x600")  # Set the window size to 800x600
        
        self.label = Label(root, text="Sélectionnez un fichier Excel à convertir en CSV")
        self.label.pack(pady=10)
        
        self.button_frame = Frame(root)
        self.button_frame.pack(pady=5)
        
        self.select_button = Button(self.button_frame, text="Sélectionner un fichier Excel", command=self.select_file)
        self.select_button.pack(side="left", padx=10)
        
        self.map_button = Button(self.button_frame, text="Afficher sur la carte", command=self.select_csv_and_display_map)
        self.map_button.pack(side="left", padx=10)
        
        self.listbox = Listbox(root, selectmode=MULTIPLE)
        self.listbox.pack(fill="both", expand=True, pady=10)
        
        self.save_button = Button(root, text="Enregistrer les colonnes sélectionnées", command=self.save_selected_columns)
        self.save_button.pack(pady=5)
        
        self.df = None
        self.output_csv_path = None

    def select_file(self):
        input_excel_path = filedialog.askopenfilename(title="Sélectionnez le fichier Excel", filetypes=[("Excel files", "*.xlsx *.xls")])
        if not input_excel_path:
            messagebox.showwarning("Avertissement", "Aucun fichier sélectionné.")
            return
        
        self.output_csv_path = input_excel_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
        self.read_excel_and_convert_to_csv(input_excel_path, self.output_csv_path)
        
    def read_excel_and_convert_to_csv(self, input_excel_path, output_csv_path):
        try:
            # Lire le fichier Excel
            self.df = pd.read_excel(input_excel_path)
            
            # Convertir le fichier Excel en CSV
            self.df.to_csv(output_csv_path, index=False)
            print(f"Fichier Excel converti en CSV : {output_csv_path}")
            
            # Lire le fichier CSV converti
            self.df = pd.read_csv(output_csv_path)
            
            # Afficher les noms de colonnes pour diagnostic
            print("Noms de colonnes dans le fichier CSV :", self.df.columns)
            
            # Nettoyer les noms de colonnes en enlevant les espaces et les caractères invisibles
            self.df.columns = self.df.columns.str.strip().str.replace(r'\s+', ' ', regex=True).str.replace('"', '')
            
            # Afficher les noms de colonnes après nettoyage
            print("Noms de colonnes après nettoyage :", self.df.columns)
            
            # Remplacer les virgules par des points et supprimer les lettres dans les colonnes Latitude et Longitude
            if 'longitude' in self.df.columns:
                self.df['longitude'] = self.df['longitude'].astype(str).str.replace(',', '.').apply(lambda x: re.sub(r'[A-Za-z]', '', x))
            if 'latitude' in self.df.columns:
                self.df['latitude'] = self.df['latitude'].astype(str).str.replace(',', '.').apply(lambda x: re.sub(r'[A-Za-z]', '', x))
            
            # Proposer les colonnes à garder
            self.populate_listbox()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier Excel ou de la conversion en CSV : {e}")

    def populate_listbox(self):
        self.listbox.delete(0, END)
        for col in self.df.columns:
            self.listbox.insert(END, col)

    def save_selected_columns(self):
        selected_indices = self.listbox.curselection()
        selected_columns = [self.df.columns[i] for i in selected_indices]
        df_selected = self.df[selected_columns]
        df_selected.to_csv(self.output_csv_path, index=False)
        messagebox.showinfo("Succès", f"Fichier CSV avec colonnes sélectionnées enregistré : {self.output_csv_path}")
        self.show_options_popup()

    def show_options_popup(self):
        options_popup = Tk()
        options_popup.title("Options")

        Label(options_popup, text="Que voulez-vous faire ?").pack(pady=10)

        Button(options_popup, text="Ouvrir le fichier", command=lambda: self.open_file(options_popup)).pack(pady=5)
        Button(options_popup, text="Afficher sur la carte", command=lambda: self.display_map(options_popup)).pack(pady=5)

        options_popup.mainloop()

    def open_file(self, popup):
        popup.destroy()
        os.startfile(self.output_csv_path)
        self.root.destroy()

    def generate_map_html(self, markers):
        map_html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Positionnements definitifs</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <style>
                #map {{
                    height: 100vh;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <script>
                var map = L.map('map').setView([46.603354, 1.888334], 6); // Coordonnées pour centrer sur la France

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }}).addTo(map);

                var markers = {json.dumps(markers)};
                markers.forEach(function(marker) {{
                    L.circleMarker([marker.lat, marker.lng], {{
                        color: 'green',
                        fillColor: 'green',
                        fillOpacity: 1,
                        radius: 5
                    }}).bindPopup('ID: ' + marker.id + '<br>Latitude: ' + marker.lat + '<br>Longitude: ' + marker.lng).addTo(map);
                }});
            </script>
        </body>
        </html>
        """
        with open('map.html', 'w') as f:
            f.write(map_html_content)

    def display_map(self, popup):
        try:
            popup.destroy()
            markers = []
            if 'latitude' in self.df.columns and 'longitude' in self.df.columns and 'identification' in self.df.columns:
                for _, row in self.df.iterrows():
                    markers.append({
                        'id': row['identification'],
                        'lat': float(row['latitude']),
                        'lng': float(row['longitude'])
                    })
            self.generate_map_html(markers)
            webbrowser.open('map.html')
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage de la carte : {e}")

    def select_csv_and_display_map(self):
        csv_file = filedialog.askopenfilename(title="Sélectionnez le fichier CSV", filetypes=[("CSV files", "*.csv")])
        if not csv_file:
            messagebox.showwarning("Avertissement", "Aucun fichier sélectionné.")
            return
        
        try:
            self.df = pd.read_csv(csv_file)
            self.display_map(Tk())
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier CSV : {e}")

if __name__ == "__main__":
    root = Tk()
    app = ExcelToCSVApp(root)
    root.mainloop()