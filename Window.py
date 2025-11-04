import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import *
import csv
from datetime import datetime

#Rows and columns going from A-H(row) 8x12 grid (Can change the size w/ this)
rows = 8
columns = 12
row_labels = [chr(i) for i in range(65, 65+rows)]
well_data = {}
buttons = {}
button_states = {}

#This is the window and its design
window = Tk()

pressed = False
window.title("96 Well Plate")
icon = PhotoImage(file='Ecoli.png')
window.iconphoto(True, icon)
window.config(background="white")

def open_data_entry(well_name):
    popup = tk.Toplevel(window)
    popup.title(f"Enter data for {well_name}")

    tk.Label(popup, text=f"Data for {well_name}", font=("Times New Roman", 12)).pack(pady=5)

    tk.Label(popup, text="Sample Name:").pack(anchor="w", padx=10)
    entry_sample = tk.Entry(popup,width=25)
    entry_sample.insert(0, well_data.get(well_name,{}).get("sample",""))
    entry_sample.pack(padx=10, pady=10)

    tk.Label(popup, text="Concentration:").pack(anchor="w", padx=5)
    entry_concentration = tk.Entry(popup, width=25)
    entry_concentration.insert(0, well_data.get(well_name,{}).get("concentration",""))
    entry_concentration.pack(padx=10,pady=10)

    def save_and_close(open_next=True):
        well_data[well_name] = {
            "sample": entry_sample.get(),
            "concentration": entry_concentration.get()
            }

        popup.destroy()
        save_plate_to_csv()
     
        if open_next:
            next_well = get_next_well(well_name)
            if next_well:
                open_data_entry(next_well)

    popup.bind("<Return>", lambda e: save_and_close(True))
    tk.Button(popup, text="Done", command=lambda: save_and_close(True)).pack(pady=5)
    tk.Button(popup, text="Finish", command= lambda: save_and_close(False)).pack(pady=5)

def get_next_well(current_well):
    all_wells = [f"{r}{c+1}" for r in row_labels for c in range(columns)]
    try:
        index = all_wells.index(current_well)
        if index + 1 < len(all_wells):
            return all_wells[index+1]
        else:
            return None
    except ValueError:
        return None

def on_hover(well_name):
    window.title(f"Hovering over {well_name}")

def button_pressed(row, col):
       if not button_states[(row, col)]:
            button_states[(row, col)] = True
            button = buttons[(row, col)]
            button.config(relief="sunken", bg="dark grey")

for r in range(rows):
    for c in range(columns):
        button_states [(r, c)] = False
        well_name = f"{row_labels[r]}{c+1}"

        button = tk.Button(window,
                           text=well_name,
                           width=6, height=2,
                           bg="lightgrey",
                           command=lambda r=r, c=c: button_pressed(r, c,)
        )
        button.grid(row=r, column=c, padx=2, pady=2)
        buttons[(r, c)] = button

        button.bind("<Enter>", lambda e, w=well_name: on_hover(w))
        button.bind("<Button-1>", lambda e, r=r, c=c, w=well_name: (
            button_pressed(r, c),
            open_data_entry(w)
        ))

def save_plate_to_csv():
    with open("plate_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        header = [str(i+1) for i in range(columns)]
        writer.writerow([""]+header)
        for r in range(rows):
            row_label=row_labels[r]
            row_values = []
            for c in range(columns):
                well_name = f"{row_label}{c+1}"
                data = well_data.get(well_name, {})
                value = f"{data.get('sample','')}|{data.get('concentration', '')}"
                row_values.append(value)
            writer.writerow([row_label] + row_values)

window.mainloop()