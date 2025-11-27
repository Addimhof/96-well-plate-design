import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import *
import csv
from datetime import datetime
import matplotlib.pyplot as plt

#Rows and columns going from A-H(row) 8x12 grid (Can change the size w/ this)
rows = 8
columns = 12
row_labels = [chr(i) for i in range(65, 65+rows)]
well_data = {}
buttons = {}
button_states = {}
round_number = 1
sample_names = {}
well_history = {}

#This is the window and its design
window = Tk()

pressed = False
window.title("96 Well Plate")
icon = PhotoImage(file='Ecoli.png')
window.iconphoto(True, icon)
window.config(background="white")

timer_label = tk.Label(window, text="Timer: 0 seconds")
timer_label.grid(row=rows, column=0, columnspan=12, pady=10)
seconds_passed = 0

def open_data_entry(well_name):
    popup = tk.Toplevel(window)
    popup.title(f"Enter data for {well_name}")

    tk.Label(popup, text=f"Data for {well_name}", font=("Times New Roman", 12)).pack(pady=5)

    tk.Label(popup, text="Sample Name:").pack(anchor="w", padx=10)
    entry_sample = tk.Entry(popup,width=25)
    sample_value = well_data.get(well_name,{}).get("sample", "")
    entry_sample.insert(0, sample_value)
    
    if round_number > 1:
        entry_sample.config(state="disabled")
    entry_sample.pack(padx=10, pady=10)


    tk.Label(popup, text="OD:").pack(anchor="w", padx=5)
    entry_OD = tk.Entry(popup, width=25)
    entry_OD.insert(0, well_data.get(well_name,{}).get("OD",""))
    entry_OD.pack(padx=10,pady=10)

    tk.Label(popup, text="RFU:").pack(anchor="w", padx=5)
    entry_RFU = tk.Entry(popup, width=25)
    entry_RFU.insert(0, well_data.get(well_name,{}).get("RFU",""))
    entry_RFU.pack(padx=10,pady=10)

    def save_and_close(open_next=True):
        sample = entry_sample.get()
        od = entry_OD.get()
        rfu = entry_RFU.get()

        well_data[well_name] = {
            "sample": entry_sample.get(),
            "od": entry_OD.get(),
            "rfu": entry_RFU.get()
        }
        if round_number == 1:
            sample_names[well_name] = sample

        popup.destroy()
        if open_next:
            next_well = get_next_well(well_name)
            if next_well:
                open_data_entry(next_well)
            else:
                save_plate_to_csv()
        else:
            save_plate_to_csv()
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
    global round_number
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"plate_data_round_{round_number}_{timestamp}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        header = [str(i+1) for i in range(columns)]
        writer.writerow([""]+header)
        for r in range(rows):
            row_label=row_labels[r]
            row_values = []
            for c in range(columns):
                well_name = f"{row_label}{c+1}"
                data = well_data.get(well_name, {})
                value = f"{data.get('sample','')}|{data.get('od', '')}|{data.get('rfu','')}"
                row_values.append(value)
            writer.writerow([row_label] + row_values)
save_button = tk.Button(window, text= "Save Curretn Data", command=save_plate_to_csv)
save_button.grid(row=rows+2, column=0, columnspan=12, pady=5)

def start_round():
    global round_number, well_data
    if round_number > 1:
        save_plate_to_csv()
        for w, data in well_data.items():
            if w not in well_history:
                well_history[w] = {"sample": data["sample"], "OD": [], "RFU": []}
            try:
                well_history[w]["OD"].append(float(data["od"]) if data['od'] else 0)
            except ValueError:
                well_history[w]["OD"].append(0)
            try:       
                well_history[w]["RFU"].append(float(data["rfu"]) if data['rfu'] else 0)
            except ValueError:
                well_history[w]["RFU"].append(0)
    for r in row_labels:
        for c in range(columns):
            w = f"{r}{c+1}"
            if w not in well_data:
                well_data[w] = {"sample": "", "od": "", "rfu": ""}
    
    for w in well_data:
        well_data[w]["od"] = ""
        well_data[w]["rfu"] = ""
   
    round_number += 1
    messagebox.showinfo("New Round", f"Round {round_number} started. Enter new values.")

round_button = tk.Button(window, text="Start New Round", command=start_round)
round_button.grid(row=rows+2, column=0, columnspan=12, pady=5)

def update_timer():
    global seconds_passed
    seconds_passed += 1
    timer_label.config(text=f"Timer: {seconds_passed} seconds")
    window.after(1000, update_timer)

def plot_well_history():
    for well, history in well_history.items():
        rounds= list(range(1, len(history["OD"]) + 1))
        plt.figure(figsize=(6,4))
        plt.plot(rounds, history["OD"], marker= 'o', label="OD")
        plt.plot(rounds, history["RFU"], marker='x', label='RFU')
        plt.title(f"Well {well} ({history['sample']})")
        plt.xlabel("Round")
        plt.ylabel("Value")
        plt.legend()
        plt.show()
plot_button = tk.Button(window, text="Plot Well History", command=plot_well_history)

plot_button.grid(row=rows+1, column=0, columnspan=12, pady=10)


update_timer()
window.mainloop()