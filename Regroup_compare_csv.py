import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, MULTIPLE, END, Scrollbar
import os

class CSVMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fusion de fichiers CSV")
        self.root.geometry("800x600")  # Set the window size to 800x600
        
        self.csv_files = []
        
        self.select_button = tk.Button(root, text="Sélectionner les fichiers CSV", command=self.select_files)
        self.select_button.pack(pady=10)
        
        self.listbox_frame = tk.Frame(root)
        self.listbox_frame.pack(fill="both", expand=True, pady=10)
        
        self.listbox = Listbox(self.listbox_frame, selectmode=MULTIPLE)
        self.listbox.pack(side="left", fill="both", expand=True)
        
        self.v_scrollbar = Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox.yview)
        self.v_scrollbar.pack(side="right", fill="y")
        
        self.h_scrollbar = Scrollbar(root, orient="horizontal", command=self.listbox.xview)
        self.h_scrollbar.pack(fill="x")
        
        self.listbox.config(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.merge_button = tk.Button(root, text="Fusionner les fichiers CSV", command=self.merge_files)
        self.merge_button.pack(pady=10)
    
    def select_files(self):
        selected_files = filedialog.askopenfilenames(title="Sélectionnez les fichiers CSV", filetypes=[("CSV files", "*.csv")])
        if selected_files:
            self.csv_files.extend(selected_files)
            self.listbox.delete(0, END)
            for file in self.csv_files:
                self.listbox.insert(END, file)
    
    def merge_files(self):
        if not self.csv_files:
            messagebox.showwarning("Avertissement", "Aucun fichier sélectionné.")
            return
        
        dfs = [pd.read_csv(file, dtype=str) for file in self.csv_files]
        merged_df = pd.concat(dfs)
        merged_df = merged_df.drop_duplicates(keep='first')
        
        output_csv_path = filedialog.asksaveasfilename(title="Enregistrer le fichier fusionné", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        
        if not output_csv_path:
            messagebox.showwarning("Avertissement", "Chemin de sortie non spécifié.")
            return
        
        merged_df.to_csv(output_csv_path, index=False)
        messagebox.showinfo("Succès", f"Fichier CSV fusionné et sans doublons enregistré : {output_csv_path}")
        
        if messagebox.askyesno("Afficher le fichier", "Voulez-vous afficher le fichier CSV avant de fermer la fenêtre ?"):
            os.startfile(output_csv_path)
        
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVMergerApp(root)
    root.mainloop()