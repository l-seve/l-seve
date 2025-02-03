import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        columns = list(df.columns)
        show_columns_in_text(columns, df, file_path)

def show_columns_in_text(columns, df, original_path):
    columns_text.delete(1.0, tk.END)
    selected_columns = []
    
    for col in columns:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(columns_text, text=col, variable=var)
        columns_text.window_create(tk.END, window=chk)
        columns_text.insert(tk.END, "\n")
        selected_columns.append((col, var))
    
    def save_selected_columns():
        selected = [col for col, var in selected_columns if var.get()]
        new_df = df[selected]
        base, ext = os.path.splitext(original_path)
        save_path = base + "_copie" + ext
        new_df.to_csv(save_path, index=False)
        messagebox.showinfo("File Saved", f"File saved at: {save_path}")
        root.destroy()
    
    save_button = tk.Button(root, text="Save Selected Columns", command=save_selected_columns)
    save_button.pack()

root = tk.Tk()
root.title("CSV Column Selector")
root.geometry("800x600")

select_button = tk.Button(root, text="Select CSV File", command=select_file)
select_button.pack()

columns_text = tk.Text(root, height=20, width=80)
columns_text.pack()

root.mainloop()
