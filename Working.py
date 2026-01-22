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
    entry_od = tk.Entry(popup, width=25)
    entry_od.insert(0, well_data.get(well_name,{}).get("od",""))
    entry_od.pack(padx=10,pady=10)

    tk.Label(popup, text="RFU:").pack(anchor="w", padx=5)
    entry_rfu = tk.Entry(popup, width=25)
    entry_rfu.insert(0, well_data.get(well_name,{}).get("rfu",""))
    entry_rfu.pack(padx=10,pady=10)

    def save_and_close(open_next=True):
        sample = entry_sample.get()
        od = entry_od.get()
        rfu = entry_rfu.get()

        well_data[well_name] = {
            "sample": entry_sample.get(),
            "od": entry_od.get(),
            "rfu": entry_rfu.get()
        }
        if well_name not in well_history:
            well_history[well_name] = {
                "sample": sample, 
                "od": [], 
                "rfu": []
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
    global round_number, well_history
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"plate_data_round_{round_number}_{timestamp}.csv"
    for well, data in well_data.items():
        if well not in well_history:
            well_history[well] = {"sample": data["sample"], "od": [], "rfu": []}
    
        try:
            od_value = float(data["od"]) if data ["od"] else 0
        except ValueError:
            od_value = 0
        well_history[well]["od"].append(od_value)
        try:
            rfu_value = float(data["rfu"]) if data ["rfu"] else 0
        except ValueError:
            rfu_value = 0
        well_history[well]["rfu"].append(rfu_value)
   
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
    save_plate_to_csv()
    
    for w in well_data:
        well_data[w]["od"] = ""
        well_data[w]["rfu"] = ""
   
    round_number += 1
    messagebox.showinfo("New Round", f"Round {round_number} started. Enter new values.")

round_button = tk.Button(window, text="Start New Round", command=start_round)
round_button.grid(row=rows+2, column=0, columnspan=12, pady=5)

def update_timer():
    global seconds_passed
    try:
        seconds_passed += 1
        timer_label.config(text=f"Timer: {seconds_passed} seconds")
        window.after(1000, update_timer)
    except:
        pass

def plot_well_history():
    for well, history in well_history.items():
        if not(any(v != 0 for v in history["od"]) or any(v !=0 for v in history["rfu"])):
            continue
        rounds= list(range(1, len(history["od"]) + 1))

        plt.figure(figsize=(6,4))
        plt.plot(rounds, history["od"], marker= 'o', label="od")
        plt.plot(rounds, history["rfu"], marker='x', label='rfu')
        plt.title(f"Well {well} ({history['sample']})")
        plt.xlabel("Round")
        plt.ylabel("Value")
        plt.legend()
        plt.show()

def trim_empties(values):
    while values and (values[-1] =="" or values[-1] is None):
        values.pop()
    return values

def select_and_plot_wells():
    popup = tk.Toplevel(window)
    popup.title("Select Wells to Plot")

    canvas = tk.Canvas(popup, height=300)
    v_scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
    h_scrollbar = tk.Scrollbar(popup, orient="horizontal", command=canvas.xview)
   
    frame = tk.Frame(canvas)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
   
    canvas.create_window((0,0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
   
    canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    
    popup.grid_rowconfigure(0, weight=1)
    popup.grid_columnconfigure(0, weight=1)

    tk.Label(frame, text="Select wells to plot").grid(row=0, column=0, columnspan=columns, pady=5)

    well_vars = {}

    row_index = 1
    for r_i, r in enumerate(row_labels):
        for c in range(1, columns + 1):
            well = f"{r}{c}"
            history = well_history.get(well, None)

            if history and (any(v !="" for v in history["od"]) or
                            any(v != "" for v in history ["rfu"])):
                var = tk.BooleanVar()
                well_vars[well] = var
                cb = tk.Checkbutton(frame, text=f"{well} ({history['sample']})", variable=var)
                cb.grid(row=row_index + r_i, column=c-1, padx=3, pady=3)

    def plot_selected():
        plt.figure(figsize=(8,5))
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        colors = plt.cm.tab10.colors
        color_index = 0

        for well, var in well_vars.items():
            if var.get():
                history = well_history[well]
                rounds = list(range(1, len(history["od"]) + 1))
                
                od_values = [float(v) if v != "" else None for v in history["od"]]
                rfu_values = [float(v) if v != "" else None for v in history["rfu"]]
               
                od_values = trim_empties(od_values)
                rfu_values = trim_empties(rfu_values)
               
                color = colors[color_index % len(colors)]
                color_index += 1

                ax1.plot(rounds, od_values, color=color, marker = 'o', linestyle='-', label=f"{history['sample']} OD")
                ax2.plot(rounds, rfu_values, color=color, marker = 'x', linestyle='--', label=f"{history['sample']} RFU")
        ax1.set_xlabel("Round")
        ax1.set_ylabel("OD")
        ax2.set_ylabel("RFU")
        
        lns = ax1.get_lines() + ax2.get_lines()
        labels = [l.get_label() for l in lns]
        ax1.legend(lns, labels, loc='upper left', bbox_to_anchor=(1,1))
       
        plt.title("Selected Wells OD & RFU")
        plt.tight_layout()
        plt.show()
        popup.destroy()
    tk.Button(frame, text="Plot Selected", command=plot_selected).grid(row=rows+2, column=0, columnspan=columns, pady=10)
plot_selected_button = tk.Button(window, text="Plot Selected Wells", command=select_and_plot_wells)
plot_selected_button.grid(row=rows+3, column=0, columnspan=12, pady=10)

update_timer()
window.mainloop()