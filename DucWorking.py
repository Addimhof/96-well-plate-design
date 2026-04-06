import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import *
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import cluster_plate as cp
import os


DEV_MODE = True
CSV_FOLDER = "plate_test_rounds_native"

def load_all_rounds_from_folder(folder):
    global well_data, well_history, round_number

    well_data = {}
    well_history = {}
    round_number = 0

    csv_files = sorted([f for f in os.listdir(folder) if f.endswith(".csv")])
    for csv_file in csv_files:
        round_number += 1
        path = os.path.join(folder, csv_file)

        with open(path, newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                row_label = row[0]
                for i, cell in enumerate(row[1:]):
                    well = f"{row_label}{i+1}"
                    promoter, ahl, od, rfu = cell.split("|")

                    od_val = float(od) if od else 0
                    rfu_val = float(rfu) if rfu else 0

                    if well not in well_history:
                        well_history[well] = {
                            "promoter": promoter,
                            "ahl": ahl,
                            "od": [],
                            "rfu": []
                        }

                    well_history[well]["od"].append(od_val)
                    well_history[well]["rfu"].append(rfu_val)

                    well_data[well] = {
                        "promoter": promoter,
                        "ahl": ahl,
                        "od": od_val,
                        "rfu": rfu_val
                    }

    print(f"✅ Loaded {round_number} rounds from folder '{folder}'")

#Rows and columns going from A-H(row) 8x12 grid (Can change the size w/ this)
rows = 8
columns = 12
row_labels = [chr(i) for i in range(65, 65+rows)]
well_data = {}
buttons = {}
button_states = {}
round_number = 1
well_history = {}
DEV_MODE = True

if DEV_MODE:
    load_all_rounds_from_folder(CSV_FOLDER)

#This is the window and its design
window = Tk()
#window.state("zoomed")     // Use this line if you want to automatically full screen when it pop up.

pressed = False
window.title("96 Well Plate")
icon = PhotoImage(file = 'Ecoli.png')
window.iconphoto(True, icon)
window.config(background = "white")

timer_label = tk.Label(window, text="Timer: 0 seconds")
timer_label.grid(row = rows, column = 0, columnspan = 12, pady = 10)
seconds_passed = 0

for extra_row in range(rows, rows + 6):
    window.grid_rowconfigure(extra_row, weight = 0)

def open_data_entry(well_name):
    popup = tk.Toplevel(window)
    popup.title(f"Enter data for {well_name}")

    tk.Label(popup, text=f"Data for {well_name}", font=("Times New Roman", 12)).pack(pady=5)

    tk.Label(popup, text="Promoter:").pack(anchor="w", padx=10)
    entry_promoter = tk.Entry(popup, width=25)
    entry_promoter.insert(0, well_data.get(well_name, {}).get("promoter", ""))

    if round_number > 1:
        entry_promoter.config(state="disabled")

    entry_promoter.pack(padx=10, pady=5)


    tk.Label(popup, text="AHL Concentration:").pack(anchor="w", padx=10)
    entry_ahl = tk.Entry(popup, width=25)
    entry_ahl.insert(0, well_data.get(well_name, {}).get("ahl", ""))

    if round_number > 1:
        entry_ahl.config(state="disabled")

    entry_ahl.pack(padx=10, pady=5)



    tk.Label(popup, text="OD:").pack(anchor="w", padx=5)
    entry_od = tk.Entry(popup, width=25)
    entry_od.insert(0, well_data.get(well_name,{}).get("od",""))
    entry_od.pack(padx=10,pady=10)

    tk.Label(popup, text="RFU:").pack(anchor="w", padx=5)
    entry_rfu = tk.Entry(popup, width=25)
    entry_rfu.insert(0, well_data.get(well_name,{}).get("rfu",""))
    entry_rfu.pack(padx=10,pady=10)

    def save_and_close(open_next=True):
        promoter = entry_promoter.get()
        ahl = entry_ahl.get()
        od = entry_od.get()
        rfu = entry_rfu.get()

        well_data[well_name] = {
            "promoter": promoter,
            "ahl": ahl,
            "od": entry_od.get(),
            "rfu": entry_rfu.get()
        }
        if well_name not in well_history:
            well_history[well_name] = {
                "promoter": promoter,
                "ahl": ahl, 
                "od": [], 
                "rfu": []
            }   

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
    window.grid_rowconfigure(r, weight = 1)
    for c in range(columns):
        window.grid_columnconfigure(c, weight = 1)
        button_states [(r, c)] = False
        well_name = f"{row_labels[r]}{c+1}"

        button = tk.Button(window,
                           text=well_name,
                           #width=6, height=2,
                           bg="lightgrey",
                           command=lambda r=r, c=c: button_pressed(r, c,)
        )
        button.grid(row=r, column=c, padx=2, pady=2, sticky = "nsew")
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
            well_history[well] = {
                "promoter": data.get("promoter", ""),
                "ahl": data.get("ahl", ""),
                "od": [],
                "rfu": []
            }
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
                value = f"{data.get('promoter','')}|{data.get('ahl','')}|{data.get('od','')}|{data.get('rfu','')}"
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
    if not window.winfo_exists():  # window is destroyed
        return
    seconds_passed += 1
    timer_label.config(text=f"Timer: {seconds_passed} seconds")
    window.after(1000, update_timer)

def plot_well_history():
    for well, history in well_history.items():
        if not(any(v != 0 for v in history["od"]) or any(v !=0 for v in history["rfu"])):
            continue
        rounds= list(range(1, len(history["od"]) + 1))

        plt.figure(figsize=(6,4))
        plt.plot(rounds, history["od"], marker= 'o', label="od")
        plt.plot(rounds, history["rfu"], marker='x', label='rfu')
        plt.title(f"Well {well} ({history['promoter']} | {history['ahl']})")
        plt.xlabel("Round")
        plt.ylabel("Value")
        plt.legend()
        plt.show()

def trim_empties(values):
    while values and (values[-1] == "" or values[-1] is None):
        values.pop()
    return values

def group_wells_by(field):
    groups = {}
    for well, data in well_history.items():
        key = data.get(field)
        if key:
            if key not in groups:
                groups[key] = []
            groups[key].append(well)
    return groups

def plot_rfu_od_vs_ahl():
    from collections import defaultdict

    ahl_ratios = defaultdict(list)

    for well, history in well_history.items():
        ahl = history.get("ahl", "").strip()
        if not ahl:
            continue
        try:
            ahl_float = float(ahl)
        except ValueError:
            continue

        od_vals = np.array(history["od"], dtype = float)
        rfu_vals = np.array(history["rfu"], dtype = float)

        mean_od = np.mean(od_vals)
        mean_rfu = np.mean(rfu_vals)

        if mean_od > 0:
            ahl_ratios[ahl_float].append(mean_rfu / mean_od)

    if not ahl_ratios:
        messagebox.showwarning("No Data", "No valid AHL/OD/RFU data found to plot.")
        return

    sorted_ahls = sorted(ahl_ratios.keys())

    means = [np.mean(ahl_ratios[a]) for a in sorted_ahls]
    stds  = [np.std(ahl_ratios[a])  for a in sorted_ahls]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.errorbar(
        sorted_ahls, means, yerr=stds,
        fmt='o-',
        color='steelblue',
        ecolor='lightsteelblue',
        elinewidth=1.5,
        capsize=4,
        linewidth=2,
        markersize=7,
        label="Mean RFU/OD ± SD"
    )

    ax.set_xscale("log")
    ax.set_xlabel("AHL Concentration (log scale)", fontsize = 12)
    ax.set_ylabel("RFU / OD", fontsize = 12)
    ax.set_title("Normalized Fluorescence (RFU/OD) vs AHL Concentration", fontsize = 13)
    ax.legend(fontsize=10)
    ax.grid(True, which = "both", linestyle = "--", alpha = 0.4)

    plt.tight_layout()
    plt.show(block = True)


def select_and_plot_wells():
    import cluster_plate as cp  # Ensure cluster_plate.py is in the same folder

    # --- Step 1: Well selection popup ---
    well_popup = tk.Toplevel(window)
    well_popup.title("Select Wells to Plot")

    canvas = tk.Canvas(well_popup, height = 300)
    v_scrollbar = tk.Scrollbar(well_popup, orient = "vertical", command = canvas.yview)
    frame = tk.Frame(canvas)

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=v_scrollbar.set)

    canvas.grid(row = 0, column = 0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    well_popup.grid_rowconfigure(0, weight=1)
    well_popup.grid_columnconfigure(0, weight=1)

    tk.Label(frame, text="Select wells to plot").grid(row=0, column=0, columnspan=columns, pady=5)

    well_vars = {}
    promoter_groups = group_wells_by("promoter")
    ahl_groups = group_wells_by("ahl")

    def select_group(well_list):
        for w in well_list:
            if w in well_vars:
                well_vars[w].set(True)

    select_all_var = tk.BooleanVar(value=False)
    def toggle_select_all():
        for var in well_vars.values():
            var.set(select_all_var.get())
    tk.Checkbutton(frame, text="Select All Wells", variable=select_all_var, command=toggle_select_all).grid(row=1, column=0, columnspan=columns, pady=5)
    tk.Label(frame, text="Select by Promoter").grid(row=2, column=0, columnspan=columns, pady=5)

    row_offset = 3
    for i, promoter in enumerate(promoter_groups):
        tk.Button(frame, text=f"Select Promoter: {promoter}",
                  command=lambda p=promoter: select_group(promoter_groups[p])
        ).grid(row=row_offset+i, column=0, columnspan=columns//2, sticky="w")

    for i, ahl in enumerate(ahl_groups):
        tk.Button(frame, text=f"Select AHL: {ahl}",
                  command=lambda a=ahl: select_group(ahl_groups[a])
        ).grid(row=row_offset+i, column=columns//2, columnspan=columns//2, sticky="w")

    # --- Individual wells ---
    row_index = 6 + len(promoter_groups)
    for r_i, r in enumerate(row_labels):
        for c in range(1, columns+1):
            well = f"{r}{c}"
            history = well_history.get(well, None)
            if history and (any(v != 0 for v in history["od"]) or any(v != 0 for v in history["rfu"])):
                var = tk.BooleanVar()
                well_vars[well] = var
                cb = tk.Checkbutton(frame, text = f"{well} ({history['promoter']} | {history['ahl']})", variable = var)
                cb.grid(row = row_index+r_i, column = c-1, padx = 3, pady = 3)
    
    next_button_row = row_index + len(row_labels) + 1

    def go_to_graph_type():
        well_popup.destroy()
        selected_wells = [w for w, var in well_vars.items() if var.get()]
        if not selected_wells:
            messagebox.showwarning("No wells selected", "Please select at least one well.")
            return
        graph_type_popup(selected_wells)

    tk.Button(frame, text = "Next", command = go_to_graph_type).grid(row = next_button_row, column = 0, columnspan = columns, pady = 10)

    # --- Step 2: Graph type selection popup ---
    def graph_type_popup(selected_wells):
        popup = tk.Toplevel(window)
        popup.title("Select Graph Type")

        tk.Label(popup, text="Select graph type:").pack(pady = 5)
        graph_type_var = tk.StringVar(value = "all")
        tk.Radiobutton(popup, text = "Standard Graph", variable=graph_type_var, value = "all").pack(anchor = "w", padx = 10)
        tk.Radiobutton(popup, text = "Clustered Graph", variable=graph_type_var, value = "clustered").pack(anchor = "w", padx = 10)

        def go_next():
            popup.destroy()
            if graph_type_var.get() == "all":
                plot_standard(selected_wells)
            else:
                cluster_options_popup(selected_wells)

        tk.Button(popup, text = "Next", command = go_next).pack(pady = 10)

    # --- Step 3: Cluster options popup ---
    def cluster_options_popup(selected_wells):
        popup = tk.Toplevel(window)
        popup.title("Cluster Options")

        tk.Label(popup, text="Select measurement(s) to cluster:").pack(pady=5)
        od_var = tk.BooleanVar(value = True)
        rfu_var = tk.BooleanVar(value = True)
        tk.Checkbutton(popup, text = "OD", variable = od_var).pack(anchor = "w", padx = 10)
        tk.Checkbutton(popup, text = "RFU", variable = rfu_var).pack(anchor = "w", padx = 10)

        tk.Label(popup, text="Select signal features:").pack(pady = 5)
        feature_vars = {}
        for feat in ["total", "peak", "ending"]:
            var = tk.BooleanVar(value = True)
            feature_vars[feat] = var
            tk.Checkbutton(popup, text=feat.capitalize(), variable=var).pack(anchor="w", padx=10)

        tk.Label(popup, text="Include categorical features:").pack(pady=5)
        include_promoter_var = tk.BooleanVar(value=False)
        include_ahl_var = tk.BooleanVar(value=False)

        tk.Checkbutton(popup, text="Promoter", variable=include_promoter_var).pack(anchor="w", padx=10)
        tk.Checkbutton(popup, text="AHL Concentration", variable=include_ahl_var).pack(anchor="w", padx=10)

        tk.Label(popup, text="Select clustering mode:").pack(pady=5)
        cluster_mode_var = tk.StringVar(value="auto")
        tk.Radiobutton(popup, text="Automatic Clustering", variable=cluster_mode_var, value="auto").pack(anchor="w", padx=10)
        tk.Radiobutton(popup, text="Specify Number of Clusters", variable=cluster_mode_var, value="manual").pack(anchor="w", padx=10)

        num_clusters_entry = tk.Entry(popup, width=5)
        num_clusters_entry.pack(anchor="w", padx=20)

        def plot_clusters():
            signals_selected = {"OD": od_var.get(), "RFU": rfu_var.get()}
            if not any(signals_selected.values()):
                messagebox.showwarning("No measurement selected","Select at least OD or RFU.")
                return
            features_selected = [f for f,var in feature_vars.items() if var.get()]
            if not features_selected:
                messagebox.showwarning("No features selected","Select at least one feature for clustering.")
                return

            n_clusters = None
            if cluster_mode_var.get()=="manual":
                try:
                    n_clusters = int(num_clusters_entry.get())
                    if n_clusters<1: raise ValueError
                except ValueError:
                    messagebox.showwarning("Invalid input","Enter a valid number of clusters.")
                    return

            popup.destroy()
            plot_clusters_gui(
                selected_wells=selected_wells,
                features_selected=features_selected,
                signals_selected=signals_selected,
                include_promoter=include_promoter_var.get(),
                include_ahl=include_ahl_var.get(),
                clustering_mode="kmeans" if n_clusters else "auto",
                n_clusters=n_clusters if n_clusters else 4
            )

        tk.Button(popup, text="Plot", command=plot_clusters).pack(pady=10)

    # --- Step 4: Standard plotting function (NEW) ---
    def plot_standard(selected_wells):
        fig, ax1 = plt.subplots(figsize=(8,5))
        ax2 = ax1.twinx()
        colors = plt.cm.tab10.colors
        color_index = 0

        for well in selected_wells:
            history = well_history[well]
            rounds = list(range(1, len(history["od"])+1))
            ax1.plot(rounds, history["od"], marker='o', linestyle='-', label=f"{history['promoter']} ({history['ahl']}) OD", color=colors[color_index % len(colors)])
            ax2.plot(rounds, history["rfu"], marker='x', linestyle='--', label=f"{history['promoter']} ({history['ahl']}) RFU", color=colors[color_index % len(colors)])
            color_index += 1

        ax1.set_xlabel("Round")
        ax1.set_ylabel("OD")
        ax2.set_ylabel("RFU")
        ax1.set_title("Selected Wells OD & RFU")

        # --- Show main graph ---
        lines = ax1.get_lines() + ax2.get_lines()
        labels = [l.get_label() for l in lines]
        fig.show()

        plt.show(block = False)

        # --- Separate legend window ---
        legend_fig = plt.figure("Legend Window", figsize=(6, max(4,len(labels)*0.35)))
        legend_ax = legend_fig.add_subplot(111)
        legend_ax.axis("off")
        ncols = max(1,len(labels)//15)
        legend_ax.legend(lines, labels, loc="center", ncol=ncols, frameon=True)
        legend_ax.set_title("Legend")
        legend_fig.show()

        plt.show(block = False)

        # RFU/OD vs AHL concentration 
        plot_rfu_od_vs_ahl()




plot_selected_button = tk.Button(
    window,
    text="Plot Selected Wells",
    command=select_and_plot_wells)
plot_selected_button.grid(row=rows+3, column=0, columnspan=12, pady=10)

def plot_clusters_gui(selected_wells, features_selected, signals_selected,
                      include_promoter=False, include_ahl=False,
                      clustering_mode="kmeans", n_clusters=4, dbscan_eps=0.5):
    import cluster_plate as cp
    from matplotlib.lines import Line2D

    # Ensure all OD/RFU are lists
    for w in selected_wells:
        if isinstance(well_history[w]["od"], (float, str)):
            well_history[w]["od"] = [float(well_history[w]["od"])]
        if isinstance(well_history[w]["rfu"], (float, str)):
            well_history[w]["rfu"] = [float(well_history[w]["rfu"])]

    # --- Create plot window ---
    plot_window = tk.Toplevel()
    plot_window.title("Clustered Wells Plot")
    fig, ax_od = plt.subplots(figsize=(9,6))
    ax_rfu = ax_od.twinx()
    colors = plt.cm.tab10.colors

    max_rounds = max(len(well_history[w]["od"]) for w in selected_wells)
    rounds = list(range(1, max_rounds + 1))

    legend_items = []  # Collect info for legend

    # OD clustering
    if signals_selected.get("OD", False):
        X_od, labels_od = cp.build_feature_matrix(well_history,"od",features_selected,selected_wells,include_promoter,include_ahl)
        od_cluster_ids = cp.cluster_signal(X_od, clustering_mode, n_clusters, dbscan_eps)
        od_clusters = cp.build_cluster_map(labels_od, od_cluster_ids)
        for cid, wells in od_clusters.items():
            mean_od = np.array([well_history[w]["od"] for w in wells], dtype=object)
            mean_od = np.mean([np.pad(v, (0, max_rounds - len(v)), 'constant', constant_values=np.nan) for v in mean_od], axis=0)
            line = ax_od.plot(rounds, mean_od, color=colors[cid % len(colors)],
                              linestyle="-", linewidth=2, label=f"Cluster {cid} OD (n={len(wells)})")
            legend_items.append((line[0], f"Cluster {cid} OD (n={len(wells)})"))

    # RFU clustering
    if signals_selected.get("RFU", False):
        X_rfu, labels_rfu = cp.build_feature_matrix(well_history,"rfu",features_selected,selected_wells,include_promoter,include_ahl)
        rfu_cluster_ids = cp.cluster_signal(X_rfu, clustering_mode, n_clusters, dbscan_eps)
        rfu_clusters = cp.build_cluster_map(labels_rfu, rfu_cluster_ids)
        for cid, wells in rfu_clusters.items():
            mean_rfu = np.array([well_history[w]["rfu"] for w in wells], dtype=object)
            mean_rfu = np.mean([np.pad(v, (0, max_rounds - len(v)), 'constant', constant_values=np.nan) for v in mean_rfu], axis=0)
            line = ax_rfu.plot(rounds, mean_rfu, color=colors[cid % len(colors)],
                               linestyle="--", linewidth=2, label=f"Cluster {cid} RFU (n={len(wells)})")
            legend_items.append((line[0], f"Cluster {cid} RFU (n={len(wells)})"))

    ax_od.set_xlabel("Round")
    ax_od.set_ylabel("OD")
    ax_rfu.set_ylabel("RFU")
    ax_od.set_title("Clustered Mean OD and RFU Curves")

    # Display plot in its window
    canvas_plot = FigureCanvasTkAgg(fig, master=plot_window)
    canvas_plot.draw()
    canvas_plot.get_tk_widget().pack(fill="both", expand=True)

    # --- Create separate legend window ---
    legend_window = tk.Toplevel()
    legend_window.title("Legend")
    fig_legend, ax_legend = plt.subplots(figsize=(6, max(4, len(legend_items)*0.35)))
    ax_legend.axis("off")

    # Create dummy lines for legend
    lines = [Line2D([0], [0], color=l.get_color(), linestyle=l.get_linestyle(), linewidth=l.get_linewidth())
             for l, _ in legend_items]
    labels = [label for _, label in legend_items]

    ncols = max(1, len(labels)//15)
    ax_legend.legend(lines, labels, loc="center", ncol=ncols, frameon=True)
    ax_legend.set_title("Legend")

    canvas_legend = FigureCanvasTkAgg(fig_legend, master=legend_window)
    canvas_legend.draw()
    canvas_legend.get_tk_widget().pack(fill="both", expand=True)

update_timer()
window.mainloop()