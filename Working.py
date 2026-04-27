import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import cluster_plate as cp
import os
#Libraries^^

#Load Csvs From Folder For Plotting
DEV_MODE = True
CSV_FOLDER = "plate_test_rounds_native"

rows = 8
columns = 12
row_labels = [chr(i) for i in range(65, 65 + rows)]

well_data = {}
buttons = {}
button_states = {}
round_number = 1
well_history = {}


# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────
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
            next(reader)  # skip header
            for row in reader:
                row_label = row[0]
                for i, cell in enumerate(row[1:]):
                    well = f"{row_label}{i + 1}"
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

#Rows and columns is adjustable for the plate size
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
pressed = False
window.title("96 Well Plate")
icon = PhotoImage(file='Ecoli.png')
window.iconphoto(True, icon)
window.config(background="white")

#This is the time it's not currently shown (3/5/26) i'm not currently seeing a purpose for it.
timer_label = tk.Label(window, text="Timer: 0 seconds")
timer_label.grid(row=rows, column=0, columnspan=12, pady=10)
seconds_passed = 0


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

# Top-level notebook — two main tabs
main_notebook = ttk.Notebook(window)
main_notebook.pack(fill="both", expand=True, padx=6, pady=6)

plate_tab = ttk.Frame(main_notebook)
main_notebook.add(plate_tab, text="  🧫  96 Well Plate  ")

analysis_tab = ttk.Frame(main_notebook)
main_notebook.add(analysis_tab, text="  📊  Analysis  ")


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def get_next_well(current_well):
    all_wells = [f"{r}{c + 1}" for r in row_labels for c in range(columns)]
    try:
        index = all_wells.index(current_well)
        return all_wells[index + 1] if index + 1 < len(all_wells) else None
    except ValueError:
        return None

#This shows the well being hovered over on the title line of the window
def on_hover(well_name):
    window.title(f"Hovering over {well_name}")

#Changes the look of the button so the user knows whats been pressed
def button_pressed(row, col):
       if not button_states[(row, col)]:
            button_states[(row, col)] = True
            button = buttons[(row, col)]
            button.config(relief="sunken", bg="dark grey")

for r in range(rows):
    for c in range(columns):
        button_states [(r, c)] = False
        well_name = f"{row_labels[r]}{c+1}"

        button = tk.Button(window, text=well_name, width=6, height=2, bg="lightgrey", command=lambda r=r, c=c: button_pressed(r, c,))
        button.grid(row=r, column=c, padx=2, pady=2)
        buttons[(r, c)] = button

        button.bind("<Enter>", lambda e, w=well_name: on_hover(w))
        button.bind("<Button-1>", lambda e, r=r, c=c, w=well_name: (button_pressed(r, c), open_data_entry(w)))

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
            od_value = float(data["od"]) if data["od"] else 0
        except (ValueError, KeyError):
            od_value = 0
        try:
            rfu_value = float(data["rfu"]) if data["rfu"] else 0
        except (ValueError, KeyError):
            rfu_value = 0

        well_history[well]["od"].append(od_value)
        well_history[well]["rfu"].append(rfu_value)

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([""] + [str(i + 1) for i in range(columns)])
        for r in range(rows):
            row_label = row_labels[r]
            row_values = []
            for c in range(columns):
                well_name = f"{row_label}{c + 1}"
                data = well_data.get(well_name, {})
                value = (
                    f"{data.get('promoter', '')}|"
                    f"{data.get('ahl', '')}|"
                    f"{data.get('od', '')}|"
                    f"{data.get('rfu', '')}"
                )
                row_values.append(value)
            writer.writerow([row_label] + row_values)

    messagebox.showinfo("Saved", f"Data saved to {filename}")


def start_round():
    global round_number, well_data
    save_plate_to_csv()
    for w in well_data:
        well_data[w]["od"] = ""
        well_data[w]["rfu"] = ""
    round_number += 1
    messagebox.showinfo("New Round", f"Round {round_number} started. Enter new OD/RFU values.")


# ─────────────────────────────────────────────
#  TAB 1 — 96 WELL PLATE
# ─────────────────────────────────────────────

# Timer
seconds_passed = 0
timer_label = tk.Label(plate_tab, text="Timer: 0 seconds", font=("Courier", 10))
timer_label.grid(row=0, column=0, columnspan=columns, pady=(6, 2))

# Round label
round_label = tk.Label(plate_tab, text=f"Round: {round_number}", font=("Courier", 10, "bold"))
round_label.grid(row=1, column=0, columnspan=columns, pady=(0, 4))


def update_timer():
    global seconds_passed
    if not window.winfo_exists():
        return
    seconds_passed += 1
    timer_label.config(text=f"Timer: {seconds_passed} seconds")
    window.after(1000, update_timer)


def on_hover(well_name):
    window.title(f"Hovering: {well_name}")


def button_pressed(r, c):
    if not button_states[(r, c)]:
        button_states[(r, c)] = True
        buttons[(r, c)].config(relief="sunken", bg="#9ecae1")


def open_data_entry(well_name):
    popup = tk.Toplevel(window)
    popup.title(f"Data Entry — {well_name}")
    popup.resizable(False, False)

    tk.Label(popup, text=f"Well: {well_name}", font=("Courier", 13, "bold")).pack(pady=(10, 4))

    fields = {}
    for label_text, key in [
        ("Promoter", "promoter"),
        ("AHL Concentration", "ahl"),
        ("OD", "od"),
        ("RFU", "rfu"),
    ]:
        tk.Label(popup, text=label_text + ":", anchor="w").pack(fill="x", padx=14)
        entry = tk.Entry(popup, width=28)
        entry.insert(0, well_data.get(well_name, {}).get(key, ""))
        if key in ("promoter", "ahl") and round_number > 1:
            entry.config(state="disabled")
        entry.pack(padx=14, pady=(0, 6))
        fields[key] = entry

    def save_and_close(open_next=True):
        well_data[well_name] = {k: v.get() for k, v in fields.items()}
        if well_name not in well_history:
            well_history[well_name] = {
                "promoter": fields["promoter"].get(),
                "ahl": fields["ahl"].get(),
                "od": [],
                "rfu": []
            }
        popup.destroy()
        if open_next:
            nxt = get_next_well(well_name)
            if nxt:
                open_data_entry(nxt)
            else:
                save_plate_to_csv()
        else:
            save_plate_to_csv()

    popup.bind("<Return>", lambda e: save_and_close(True))
    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Next →", command=lambda: save_and_close(True), width=10).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Finish", command=lambda: save_and_close(False), width=10).pack(side="left", padx=4)


# Well grid — starts at row 2 in plate_tab
for r in range(rows):
    for c in range(columns):
        button_states[(r, c)] = False
        well_name = f"{row_labels[r]}{c + 1}"

        btn = tk.Button(
            plate_tab,
            text=well_name,
            width=5, height=2,
            bg="#d9edf7",
            font=("Courier", 8),
            relief="raised"
        )
        btn.grid(row=r + 2, column=c, padx=2, pady=2)
        buttons[(r, c)] = btn

        btn.bind("<Enter>", lambda e, w=well_name: on_hover(w))
        btn.bind("<Button-1>", lambda e, r=r, c=c, w=well_name: (
            button_pressed(r, c),
            open_data_entry(w)
        ))

# Bottom controls for plate tab
ctrl_frame = tk.Frame(plate_tab, bg="#f0f0f0")
ctrl_frame.grid(row=rows + 2, column=0, columnspan=columns, pady=8)

tk.Button(ctrl_frame, text="💾  Save Current Data", command=save_plate_to_csv,
          width=20).pack(side="left", padx=6)
tk.Button(ctrl_frame, text="🔁  Start New Round", command=start_round,
          width=20).pack(side="left", padx=6)


# ─────────────────────────────────────────────
#  TAB 2 — ANALYSIS
# ─────────────────────────────────────────────

analysis_inner = ttk.Notebook(analysis_tab)
analysis_inner.pack(fill="both", expand=True, padx=6, pady=6)

well_select_tab = ttk.Frame(analysis_inner)
analysis_inner.add(well_select_tab, text="  Well Selection  ")

standard_options_tab = ttk.Frame(analysis_inner)
analysis_inner.add(standard_options_tab, text="  Standard Graph  ")

cluster_options_tab = ttk.Frame(analysis_inner)
analysis_inner.add(cluster_options_tab, text="  Cluster Options  ")

# ── Well Selection sub-tab ──────────────────

tk.Label(well_select_tab, text="Select Wells to Plot",
         font=("Courier", 12, "bold")).pack(pady=(8, 4))

ws_canvas = tk.Canvas(well_select_tab, height=340)
ws_scrollbar = tk.Scrollbar(well_select_tab, orient="vertical", command=ws_canvas.yview)
ws_frame = tk.Frame(ws_canvas)
ws_frame.bind("<Configure>", lambda e: ws_canvas.configure(scrollregion=ws_canvas.bbox("all")))
ws_canvas.create_window((0, 0), window=ws_frame, anchor="nw")
ws_canvas.configure(yscrollcommand=ws_scrollbar.set)
ws_canvas.pack(side="left", fill="both", expand=True, padx=(6, 0))
ws_scrollbar.pack(side="right", fill="y")

well_vars = {}

# "Select All" checkbox
select_all_var = tk.BooleanVar(value=False)


def toggle_select_all():
    for var in well_vars.values():
        var.set(select_all_var.get())


tk.Checkbutton(ws_frame, text="☑  Select All Wells",
               variable=select_all_var, command=toggle_select_all,
               font=("Courier", 10, "bold")).grid(row=0, column=0, columnspan=6, pady=4, sticky="w")


def select_group(well_list):
    for w in well_list:
        if w in well_vars:
            well_vars[w].set(True)


def refresh_well_selector():
    """Re-populate well checkboxes (call after loading data)."""
    for widget in ws_frame.winfo_children():
        widget.destroy()

    tk.Checkbutton(ws_frame, text="☑  Select All Wells",
                   variable=select_all_var, command=toggle_select_all,
                   font=("Courier", 10, "bold")).grid(row=0, column=0, columnspan=6, pady=4, sticky="w")

    # Group buttons
    promoter_groups = group_wells_by("promoter")
    ahl_groups = group_wells_by("ahl")

    tk.Label(ws_frame, text="Quick-select by Promoter:",
             font=("Courier", 9, "italic")).grid(row=1, column=0, columnspan=6, sticky="w", padx=4)
    for i, prom in enumerate(promoter_groups):
        tk.Button(ws_frame, text=f"Promoter: {prom}", font=("Courier", 8),
                  command=lambda p=prom: select_group(promoter_groups[p])
                  ).grid(row=2, column=i % 6, padx=2, pady=1, sticky="w")

    tk.Label(ws_frame, text="Quick-select by AHL:",
             font=("Courier", 9, "italic")).grid(row=3, column=0, columnspan=6, sticky="w", padx=4)
    for i, ahl in enumerate(ahl_groups):
        tk.Button(ws_frame, text=f"AHL: {ahl}", font=("Courier", 8),
                  command=lambda a=ahl: select_group(ahl_groups[a])
                  ).grid(row=4, column=i % 6, padx=2, pady=1, sticky="w")

    # Individual well checkboxes
    tk.Label(ws_frame, text="─" * 60).grid(row=5, column=0, columnspan=12, pady=4)
    well_vars.clear()
    for r_i, r in enumerate(row_labels):
        for c in range(1, columns + 1):
            well = f"{r}{c}"
            history = well_history.get(well)
            if history and (any(v != 0 for v in history["od"]) or any(v != 0 for v in history["rfu"])):
                var = tk.BooleanVar()
                well_vars[well] = var
                label_text = f"{well} ({history['promoter']} | {history['ahl']})"
                tk.Checkbutton(ws_frame, text=label_text, variable=var,
                               font=("Courier", 8)
                               ).grid(row=6 + r_i, column=c - 1, padx=2, pady=1, sticky="w")


refresh_well_selector()

# ── Standard Graph sub-tab ──────────────────

        show_legend_var = tk.BooleanVar(value=True)
        tk.Checkbutton(popup, text="Show Legend Window", variable=show_legend_var).pack(anchor="w", padx=10)
        
        def go_next():
            popup.destroy()
            if graph_type_var.get() == "all":
                plot_standard(selected_wells, show_legend_var.get())
            else:
                cluster_options_popup(selected_wells, show_legend_var.get())

        tk.Button(popup, text="Next", command=go_next).pack(pady=10)

    # --- Step 3: Cluster options popup ---
    def cluster_options_popup(selected_wells, show_legend):
        popup = tk.Toplevel(window)
        popup.title("Cluster Options")

        tk.Label(popup, text="Select measurement(s) to cluster:").pack(pady=5)
        od_var = tk.BooleanVar(value=True)
        rfu_var = tk.BooleanVar(value=True)
        tk.Checkbutton(popup, text="OD", variable=od_var).pack(anchor="w", padx=10)
        tk.Checkbutton(popup, text="RFU", variable=rfu_var).pack(anchor="w", padx=10)

        tk.Label(popup, text="Select signal features:").pack(pady=5)
        feature_vars = {}
        for feat in ["total","peak","ending"]:
            var = tk.BooleanVar(value=True)
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
                n_clusters=n_clusters if n_clusters else 4,
                show_legend=show_legend
            )

std_show_od = tk.BooleanVar(value=True)
std_show_rfu = tk.BooleanVar(value=True)
std_group_by_condition = tk.BooleanVar(value=False)

    # --- Step 4: Standard plotting function (NEW) ---
    def plot_standard(selected_wells, show_legend=True):
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

        # --- Separate legend window ---
        if show_legend:
            legend_fig = plt.figure("Legend Window", figsize=(6, max(4,len(labels)*0.35)))
            legend_ax = legend_fig.add_subplot(111)
            legend_ax.axis("off")
            ncols = max(1,len(labels)//15)
            legend_ax.legend(lines, labels, loc="center", ncol=ncols, frameon=True)
            legend_ax.set_title("Legend")
            legend_fig.show()




plot_selected_button = tk.Button(
    window,
    text="Plot Selected Wells",
    command=select_and_plot_wells)
plot_selected_button.grid(row=rows+3, column=0, columnspan=12, pady=10)

def plot_clusters_gui(selected_wells, features_selected, signals_selected,
                      include_promoter=False, include_ahl=False,
                      clustering_mode="kmeans", n_clusters=4, dbscan_eps=0.5, show_legend=True):
    import cluster_plate as cp
    from matplotlib.lines import Line2D

    # Ensure all OD/RFU are lists
    for w in selected_wells:
        if isinstance(well_history[w]["od"], (float, str)):
            well_history[w]["od"] = [float(well_history[w]["od"])]
        if isinstance(well_history[w]["rfu"], (float, str)):
            well_history[w]["rfu"] = [float(well_history[w]["rfu"])]

    max_rounds = max(len(well_history[w]["od"]) for w in selected_wells)
    rounds = list(range(1, max_rounds + 1))
    colors = plt.cm.tab10.colors

    graph_win = tk.Toplevel(window)
    graph_win.title("Graph Results")
    graph_win.geometry("1050x720")
    graph_win.lift()
    graph_win.attributes("-topmost", True)
    graph_win.after(800, lambda: graph_win.attributes("-topmost", False))

    notebook = ttk.Notebook(graph_win)
    notebook.pack(fill="both", expand=True)

    # ── Tab: Standard Graph ─────────────────
    std_tab = ttk.Frame(notebook)
    notebook.add(std_tab, text="  Standard Graph  ")

    fig_std, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    if group_by_condition:
        # Group wells that share the same (promoter, AHL) pair and average them
        groups = {}
        for well in selected_wells:
            h = well_history[well]
            key = (h["promoter"], h["ahl"])
            groups.setdefault(key, []).append(well)

        for i, ((promoter, ahl), wells_in_group) in enumerate(groups.items()):
            lbl = f"{promoter} | AHL={ahl} (n={len(wells_in_group)})"
            color = colors[i % len(colors)]

            if show_od:
                padded_od = [
                    np.pad(well_history[w]["od"],
                           (0, max_rounds - len(well_history[w]["od"])),
                           constant_values=np.nan)
                    for w in wells_in_group
                ]
                mean_od = np.nanmean(padded_od, axis=0)
                std_od  = np.nanstd(padded_od, axis=0)
                ax1.plot(rounds, mean_od, marker="o", linestyle="-",
                         label=f"{lbl} OD", color=color)
                ax1.fill_between(rounds,
                                 mean_od - std_od,
                                 mean_od + std_od,
                                 alpha=0.15, color=color)

            if show_rfu:
                padded_rfu = [
                    np.pad(well_history[w]["rfu"],
                           (0, max_rounds - len(well_history[w]["rfu"])),
                           constant_values=np.nan)
                    for w in wells_in_group
                ]
                mean_rfu = np.nanmean(padded_rfu, axis=0)
                std_rfu  = np.nanstd(padded_rfu, axis=0)
                ax2.plot(rounds, mean_rfu, marker="x", linestyle="--",
                         label=f"{lbl} RFU", color=color)
                ax2.fill_between(rounds,
                                 mean_rfu - std_rfu,
                                 mean_rfu + std_rfu,
                                 alpha=0.10, color=color)

        ax1.set_title("Grouped by Promoter + AHL — Mean ± SD")

    else:
        # Individual well lines
        for i, well in enumerate(selected_wells):
            history = well_history[well]
            r_vals = list(range(1, len(history["od"]) + 1))
            lbl = f"{history['promoter']} ({history['ahl']}) — {well}"
            if show_od:
                ax1.plot(r_vals, history["od"], marker="o", linestyle="-",
                         label=f"{lbl} OD", color=colors[i % len(colors)])
            if show_rfu:
                ax2.plot(r_vals, history["rfu"], marker="x", linestyle="--",
                         label=f"{lbl} RFU", color=colors[i % len(colors)])

        ax1.set_title("Selected Wells — OD & RFU over Rounds")

    ax1.set_xlabel("Round")
    ax1.set_ylabel("OD")
    ax2.set_ylabel("RFU")

    # Combined legend
    all_lines  = ax1.get_lines() + ax2.get_lines()
    all_labels = [l.get_label() for l in all_lines]
    fig_std.legend(all_lines, all_labels, loc="lower center",
                   ncol=max(1, len(all_labels) // 6),
                   fontsize=7, bbox_to_anchor=(0.5, -0.02))
    fig_std.tight_layout(rect=[0, 0.08, 1, 1])

    _embed_figure(std_tab, fig_std)

    # ── Tab: OD over Rounds (per well) ─────
    if show_od:
        od_tab = ttk.Frame(notebook)
        notebook.add(od_tab, text="  OD — All Wells  ")

        fig_od, ax_od = plt.subplots(figsize=(9, 5))
        for i, well in enumerate(selected_wells):
            history = well_history[well]
            r_vals = list(range(1, len(history["od"]) + 1))
            ax_od.plot(r_vals, history["od"], marker="o",
                       label=f"{well} ({history['promoter']})",
                       color=colors[i % len(colors)])
        ax_od.set_xlabel("Round")
        ax_od.set_ylabel("OD")
        ax_od.set_title("OD — All Selected Wells")
        ax_od.legend(fontsize=7, ncol=max(1, len(selected_wells) // 10),
                     bbox_to_anchor=(1, 1), loc="upper left")
        fig_od.tight_layout()
        _embed_figure(od_tab, fig_od)

    # ── Tab: RFU over Rounds (per well) ────
    if show_rfu:
        rfu_tab = ttk.Frame(notebook)
        notebook.add(rfu_tab, text="  RFU — All Wells  ")

        fig_rfu, ax_rfu = plt.subplots(figsize=(9, 5))
        for i, well in enumerate(selected_wells):
            history = well_history[well]
            r_vals = list(range(1, len(history["rfu"]) + 1))
            ax_rfu.plot(r_vals, history["rfu"], marker="x", linestyle="--",
                        label=f"{well} ({history['promoter']})",
                        color=colors[i % len(colors)])
        ax_rfu.set_xlabel("Round")
        ax_rfu.set_ylabel("RFU")
        ax_rfu.set_title("RFU — All Selected Wells")
        ax_rfu.legend(fontsize=7, ncol=max(1, len(selected_wells) // 10),
                      bbox_to_anchor=(1, 1), loc="upper left")
        fig_rfu.tight_layout()
        _embed_figure(rfu_tab, fig_rfu)

    # ── Clustered tabs (only if requested) ─
    if graph_mode == "clustered" and features_selected:
        od_clusters = {}
        rfu_clusters = {}

        if signals_selected.get("OD", False):
            X_od, labels_od = cp.build_feature_matrix(
                well_history, "od", features_selected, selected_wells,
                include_promoter, include_ahl
            )
            od_ids = cp.cluster_signal(X_od, clustering_mode, n_clusters, dbscan_eps)
            od_clusters = cp.build_cluster_map(labels_od, od_ids)

        if signals_selected.get("RFU", False):
            X_rfu, labels_rfu = cp.build_feature_matrix(
                well_history, "rfu", features_selected, selected_wells,
                include_promoter, include_ahl
            )
            rfu_ids = cp.cluster_signal(X_rfu, clustering_mode, n_clusters, dbscan_eps)
            rfu_clusters = cp.build_cluster_map(labels_rfu, rfu_ids)

        # One tab per OD cluster
        for cid, wells in od_clusters.items():
            c_tab = ttk.Frame(notebook)
            notebook.add(c_tab, text=f"  OD Cluster {cid}  ")

            fig_c, ax_c = plt.subplots(figsize=(8, 5))
            mean_od = np.mean([
                np.pad(well_history[w]["od"],
                       (0, max_rounds - len(well_history[w]["od"])),
                       constant_values=np.nan)
                for w in wells
            ], axis=0)
            ax_c.plot(rounds, mean_od, color=colors[cid % len(colors)],
                      linestyle="-", linewidth=2, marker="o")
            ax_c.set_title(f"OD Cluster {cid} — Mean Signal")
            ax_c.set_xlabel("Round")
            ax_c.set_ylabel("OD")
            fig_c.tight_layout()

            tk.Label(c_tab, text=f"Wells in cluster: {', '.join(wells)}",
                     font=("Courier", 8), wraplength=900).pack(pady=4)
            _embed_figure(c_tab, fig_c)

        # One tab per RFU cluster
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
    if show_legend:
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

# ─────────────────────────────────────────────
#  START
# ─────────────────────────────────────────────
update_timer()
window.mainloop()
