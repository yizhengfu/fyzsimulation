import os
import tkinter as tk
from tkinter import filedialog

def create_folders_and_copy_content(input_file, output_folder):
    with open(input_file, 'r') as file:
        content = file.readlines()

    timestep_indices = [i for i, line in enumerate(content) if "ITEM: TIMESTEP" in line]

    for i in range(len(timestep_indices) - 1):
        start_index = timestep_indices[i]
        end_index = timestep_indices[i + 2] if i + 2 < len(timestep_indices) else len(content)

        folder_name = str(i + 1)
        output_folder_path = os.path.join(output_folder, folder_name)
        os.makedirs(output_folder_path, exist_ok=True)

        output_file_path = os.path.join(output_folder_path, 'trj.txt')
        with open(output_file_path, 'w') as output_file:
            output_file.writelines(content[start_index:end_index])

def browse_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_path)

def browse_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, folder_path)

def process_files():
    input_file = input_file_entry.get()
    output_folder = output_folder_entry.get()
    create_folders_and_copy_content(input_file, output_folder)
    tk.messagebox.showinfo("Success", "Processing completed!")

# GUI setup
app = tk.Tk()
app.title("Text File Processor")

# Input file
tk.Label(app, text="Input File:").grid(row=0, column=0, padx=10, pady=5)
input_file_entry = tk.Entry(app, width=50)
input_file_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(app, text="Browse", command=browse_input_file).grid(row=0, column=2, padx=10, pady=5)

# Output folder
tk.Label(app, text="Output Folder:").grid(row=1, column=0, padx=10, pady=5)
output_folder_entry = tk.Entry(app, width=50)
output_folder_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(app, text="Browse", command=browse_output_folder).grid(row=1, column=2, padx=10, pady=5)

# Process button
tk.Button(app, text="Process Files", command=process_files).grid(row=2, column=0, columnspan=3, pady=10)

app.mainloop()
