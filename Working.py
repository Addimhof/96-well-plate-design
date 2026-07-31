import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
# Go to Pylance Settings, then Python > Analysis: Extra Paths,
# Copy your working directory (where this file is) as text and paste it into the field. Pylance will complain otherwise.
import cluster_plate as cp
import os
#Libraries^^

DEV_MODE = True # Debug flag. Treat as constant. DO NOT change in any function.
CSV_FOLDER = "plate_test_rounds_native" # Points to file for csv to do stuff with. Treat as constant. DO NOT change in any function.
def load_all_rounds_from_folder(folder):
    """
    Desc: First function that should be called in main. Loads csv well data from a file path and documents everything in global well history

    Pre: Needs a string file path called folder.

    Post: well_data, well_history, and round_number are all global variables to be accessed later.
    """  
    global well_data, well_history, round_number
    # well_data: dictionary for associating wells with the data they store. Most recent data.
    # well_history: dictionary for associating wells with the data they store. Past data.
    # round_number: Tracks how many CSV files have been imported. Increments each time an import occurs following sorting.

    well_data = {}
    well_history = {}
    round_number = 0
    # A sorted list of all CSV filenames within the folder name string passed to this function.

    csv_files = sorted([f for f in os.listdir(folder) if f.endswith(".csv")]) #Declare file path to open for csv_file. Probably a String but technically Any.

    for csv_file in csv_files:
        
        round_number += 1
        path = os.path.join(folder, csv_file) # Declare file path to open for csv_file. Probably a String but technically Any.

        with open(path, newline="") as f:
            # Every instance of f is a file being opened here.
            reader = csv.reader(f) # Instance of a parsed csv file.
            next(reader) 
            for row in reader:
                row_label = row[0] # First element for every row. A string for diffrientiating rows.
                for i, cell in enumerate(row[1:]): # Loop to do things per cell.
                    well = f"{row_label}{i+1}" # Construct a well title. "A1", "A2", etc.
                    promoter, ahl, od, rfu = cell.split("|")
                    # promoter: Promoter type. Anderson mutants for where we are now. "J23###"
                    # ahl: AHL concentration.
                    # od: Optical Density. Estimated density of bacteria.
                    # rfu: Relative Fluorescence Units. DV.

                    od_val = float(od) if od else 0
                    rfu_val = float(rfu) if rfu else 0
                    # od_val, rfu_val: make these floats bc python sucks

                    # labelling for wells with non-existant data. Null values to not cause errors when we graph things.
                    if well not in well_history:
                        well_history[well] = {
                            "promoter": promoter,
                            "ahl": ahl,
                            "od": [],
                            "rfu": []
                        }
                    # Associate the float values that do exist for the well_history with their appropriate wells.
                    well_history[well]["od"].append(od_val)
                    well_history[well]["rfu"].append(rfu_val)

                    # Label EVERYTHING for wells that exist
                    well_data[well] = {
                        "promoter": promoter,
                        "ahl": ahl,
                        "od": od_val,
                        "rfu": rfu_val
                    }

    print(f"✅ Loaded {round_number} rounds from folder '{folder}'")

# Rows and columns going from A-H(row) 8x12 grid (Can change the size w/ this)
rows = 8 # Number of rows
columns = 12 # Number of columns
row_labels = [chr(i) for i in range(65, 65+rows)] # Chr referesneces ASCII index for uppercase A. Iterates from there for rows. > 26 rows means funny results.
well_data = {} # Dictionary for associating wells with the data they store. Most recent data.
buttons = {} # Dictionary of buttons. Each I believe corresponds with a well in the GUI.
button_states = {} # Holds all states associated with the buttons.
round_number = 1 # Initial round number. Associated with CSVs imported.
well_history = {} # Dictionary for associating wells with the data they store. Past data.

if DEV_MODE:
    load_all_rounds_from_folder(CSV_FOLDER)

# This is the window and its design
window = tk.Tk() # Tkinter window template/object. It may be useful to roll all of the params into this constructor.

pressed = False
window.title("96 Well Plate") # Window display title. Reads at the top.
icon = tk.PhotoImage(file='Ecoli.png') # Filepath for Window icon. Shows up in top-left and task bar.
window.iconphoto(True, icon) # Set the window icon to display.
window.config(background="white") # Background window color. Maybe tone this down from straight #ffffff.

# CHANGED: Give the main root window permission to grow rows and columns dynamically
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

# Top-level notebook — two main tabs
main_notebook = ttk.Notebook(window)
# CHANGED: Use grid configuration on parent layouts instead of pack to pass structural weights safely
main_notebook.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

plate_tab = ttk.Frame(main_notebook)
main_notebook.add(plate_tab, text="  🧫  96 Well Plate  ")

analysis_tab = ttk.Frame(main_notebook)
main_notebook.add(analysis_tab, text="  📊  Analysis  ")

# CHANGED: Force the analysis tab container layout to grow horizontally and vertically
analysis_tab.rowconfigure(0, weight=1)
analysis_tab.columnconfigure(0, weight=1)

# As a note, well_name is not actually any variable modified outside of a function. It's another way of referring to well_history[well].
# TODO: Pick well_name or well as the variable to reference individual wells.
def open_data_entry(well_name):
    """
    Desc: A popup window that handles editing of the well_data referenced in the passed param. Also includes definitions to save data.

    Pre: Called with a well/well_name to reference.

    Post: This function acts as a w included save_and_close(), see that function for more details.
    """  
    popup = tk.Toplevel(window) #Precisely what it sounds like. Creates a popup layered on top of the main window.
    popup.title(f"Enter data for {well_name}") #Pass the well title here. The popup also has a name.
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
        if key in ("promoter", "ahl") and round_number > 1 and well_name in well_data:
            entry.config(state="disabled")
        entry.pack(padx=14, pady=(0, 6))
        fields[key] = entry

    # Data edits be here
    def save_and_close(open_next=True):
        """
        Desc: Assigns the changes made in the open_data_entry() popup to the wells and csv data.

        Pre: The open_next param, true by default, opens the next well entry recursively depending on user input.

        Post: save_plate_to_csv() will always eventually be called. This by extension has file I/O output.
        """  
        # Make some variables equal to the inputs gained from the tk Entries
        well_data[well_name] = {k: v.get() for k, v in fields.items()}
        if well_name not in well_history:
            well_history[well_name] = {
                "promoter": fields["promoter"].get(),
                "ahl": fields["ahl"].get(),
                "od": [],
                "rfu": []
            }

        # Kill the window.
        popup.destroy()
        # Below is recursive calling that if the open_next param is true, will allow for consecutive data entry.
        if open_next:
            next_well = get_next_well(well_name)
            if next_well:
                open_data_entry(next_well)
            else:
                # If there's no more data to enter, save everything.
                save_plate_to_csv()
        else:
            save_plate_to_csv()
    #The Enter (Return) key should save the data and close the window
    popup.bind("<Return>", lambda e: save_and_close(True))
    # Two more buttons for saving. Done is recursive. Finish is not.
    # MAYBE TODO: "Done" should be "Done (Open Next)" for user-friendliness.
    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Next →", command=lambda: save_and_close(True), width=10).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Finish", command=lambda: save_and_close(False), width=10).pack(side="left", padx=4)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def get_next_well(current_well):
    """
    Desc: Fetches the next well accounting for rows of columns.

    Pre: Called with a current_well to index.

    Post: Gets the index of the next well if it exists, otherwise returns None.
    """  
    all_wells = [f"{r}{c+1}" for r in row_labels for c in range(columns)] #A 2D list of ALL the wells.
    # Error handling? In my GUI?
    try:
        # An index is grabbed from the the current_well passed, from its position in all_wells.
        index = all_wells.index(current_well)
        return all_wells[index + 1] if index + 1 < len(all_wells) else None
        # If there's a well following, return the index of the next well. Or else return None.
    except ValueError:
        # If there's not an applicable value return none.
        return None

#This shows the well being hovered over on the title line of the window
def on_hover(well_name):
    """
    Desc: Very simple function. Changes the window title when called to reference a specific well button label.

    Pre: Called with a well/well_name to reference.

    Post: Changes the tkinter window title to reference the well/well_name.
    """  
    window.title(f"Hovering over {well_name}")

#Changes the look of the button so the user knows whats been pressed
def button_pressed(row, col):
    """
    Desc: Also simple GUI handling. Assigns a True button_state and changes its appearance if clicked.

    Pre: Called with a row and column for the button, assuming they are in a 2D matrix.

    Post: Changes the button_state and its appearance to reflect clicking on it.
    """  
    if not button_states[(row, col)]:
            button_states[(row, col)] = True
            button = buttons[(row, col)]
            button.config(relief="sunken", bg="#9ecae1")


def save_plate_to_csv():
    """
    Desc: Saves the current plate state into a CSV file AND appends OD/RFU values to the well_history.

    Pre: 
    - well_data must be populated with current well values.
    - round_number must be initialized.
    - columns, rows, and row_labels must be defined.

    Post:
    - A timestamped CSV file is created.
    - well_history is updated with the new OD/RFU values for each well.
    """

    global round_number, well_history
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Unique timestamp for file naming
    filename = f"plate_data_round_{round_number}_{timestamp}.csv"  # Output the CSV filename

    for well, data in well_data.items():  # Iterate through all wells

        # Initialize history entry if it doesn't exist
        if well not in well_history:
            well_history[well] = {
                "promoter": data.get("promoter", ""),  # Promoter
                "ahl": data.get("ahl", ""),  # AHL concentration
                "od": [],  # OD history list
                "rfu": []  # RFU history list
            }

        # Convert OD safely to float
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

        header = [str(i+1) for i in range(columns)]  # Column labels (1–12)
        writer.writerow([""] + header)  # First row (empty corner + column numbers)

        for r in range(rows):
            row_label = row_labels[r]  # Row label (A–H)
            row_values = []  # Stores all the cell values for this row

            for c in range(columns):
                well_name = f"{row_label}{c+1}"  # Construct well ID
                data = well_data.get(well_name, {})  # Fetch well data (default empty dict)

                # Format cell as "promoter|ahl|od|rfu"
                value = f"{data.get('promoter','')}|{data.get('ahl','')}|{data.get('od','')}|{data.get('rfu','')}"
                row_values.append(value)

            writer.writerow([row_label] + row_values)  # Write row to CSV

    messagebox.showinfo("Saved", f"Data saved to {filename}")


def start_round():
    """
    Desc: Saves current round data, clears OD/RFU values, and increments round number.

    Pre:
    - well_data must exist and contain wells.
    - save_plate_to_csv must be functional.

    Post:
    - Current data is saved to CSV.
    - OD and RFU values are reset for all wells.
    - round_number increments by 1.
    - User is notified with a popup.
    """

    global round_number, well_data
    save_plate_to_csv()  # Save current round before clearing

    # Reset OD and RFU values for next round
    for w in well_data:
        well_data[w]["od"] = ""  # Clear OD
        well_data[w]["rfu"] = ""  # Clear RFU

    round_number += 1  # Move to next round

    messagebox.showinfo("New Round", f"Round {round_number} started. Enter new OD/RFU values.")


def update_timer():
    """
    Desc: Updates a running timer every second and displays it in the UI.

    Pre:
    - window must exist.
    - seconds_passed must be initialized globally.
    - timer_label must be a valid Tkinter label.

    Post:
    - seconds_passed increments by 1 every second.
    - timer_label text updates continuously.
    """

    global seconds_passed
    if not window.winfo_exists():  # Prevent updates if window is closed
        return

    seconds_passed += 1  # Increment timer

    timer_label.config(text=f"Timer: {seconds_passed} seconds")  # Update label

    window.after(1000, update_timer)  # Schedule next update (1 second)


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
# CHANGED: Use grid with sticky options on the sub-tab panel so it handles full-screen resizing forces
analysis_inner.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

well_select_tab = ttk.Frame(analysis_inner)
analysis_inner.add(well_select_tab, text="  Well Selection  ")

# CHANGED: Give well_select_tab explicit layout scaling parameters so its contents fill up screen space
well_select_tab.rowconfigure(1, weight=1)
well_select_tab.columnconfigure(0, weight=1)

standard_options_tab = ttk.Frame(analysis_inner)
analysis_inner.add(standard_options_tab, text="  Standard Graph  ")

cluster_options_tab = ttk.Frame(analysis_inner)
analysis_inner.add(cluster_options_tab, text="  Cluster Options  ")

# CHANGED: Created the variables immediately before building the UI widgets to prevent scoping NameErrors
# Instantiating the state variables directly inline before the sub-tab configuration layout items
std_group_by_condition = tk.BooleanVar(value=False) # Local indicator for averaging well groups by metadata
std_show_legend_var = tk.BooleanVar(value=True) # Local indicator for popping up a legend window from the Standard Graph tab, independent of the Cluster Options tab
std_show_groups_var = tk.BooleanVar(value=False) # Local indicator for popping up a window listing which wells landed in which promoter+AHL group

# CHANGED: Added interactive configuration elements directly inside the "Standard Graph" tab
# Set up interactive buttons and layout directly inside the standard graph options tab
tk.Label(standard_options_tab, text="Standard Graph Settings", font=("Courier", 12, "bold")).pack(pady=(8, 4))
tk.Checkbutton(standard_options_tab, text="Group by Condition (Mean ± SD)", variable=std_group_by_condition).pack(anchor="w", padx=20, pady=2) # Combine identical experimental environments
tk.Checkbutton(standard_options_tab, text="Separate Window Legend", variable=std_show_legend_var).pack(anchor="w", padx=20, pady=2) # Toggle popup legend window for the standard graph
tk.Checkbutton(standard_options_tab, text="Show Group Membership (Group by Condition only)", variable=std_show_groups_var).pack(anchor="w", padx=20, pady=2) # Toggle popup showing which wells landed in which promoter+AHL group

# CHANGED: Declared the shared clustering configurations and placed elements directly inside the "Cluster Options" tab
# Set up interactive variables and container frames inside the cluster options tab
show_legend_var = tk.BooleanVar(value=True) # Checkbutton state for popping up an isolated legend window
cluster_od_var = tk.BooleanVar(value=True) # Checkbutton state to run calculation matrices on OD data
cluster_rfu_var = tk.BooleanVar(value=True) # Checkbutton state to run calculation matrices on RFU data
include_promoter_var = tk.BooleanVar(value=False) # Checkbutton state to index promoter types in algorithm matrix
include_ahl_var = tk.BooleanVar(value=False) # Checkbutton state to index chemical concentration in algorithm matrix
cluster_mode_var = tk.StringVar(value="auto") # Radiobutton selection for automatic vs fixed quantity clustering groups

tk.Label(cluster_options_tab, text="Cluster Analysis Settings", font=("Courier", 12, "bold")).pack(pady=(8, 4))
tk.Checkbutton(cluster_options_tab, text="Cluster on OD measurements", variable=cluster_od_var).pack(anchor="w", padx=20, pady=2)
tk.Checkbutton(cluster_options_tab, text="Cluster on RFU measurements", variable=cluster_rfu_var).pack(anchor="w", padx=20, pady=2)
tk.Checkbutton(cluster_options_tab, text="Include Promoter Data", variable=include_promoter_var).pack(anchor="w", padx=20, pady=2)
tk.Checkbutton(cluster_options_tab, text="Include AHL Concentration", variable=include_ahl_var).pack(anchor="w", padx=20, pady=2)
tk.Checkbutton(cluster_options_tab, text="Separate Window Legend", variable=show_legend_var).pack(anchor="w", padx=20, pady=2)

cluster_feat_frame = tk.LabelFrame(cluster_options_tab, text="Signal Features to Cluster") # Group box component for layout spacing
cluster_feat_frame.pack(fill="x", padx=20, pady=5)
cluster_feature_vars = {} # Dictionary mapping for feature mathematical tracking keys
for feat in ["total", "peak", "ending"]:
    var = tk.BooleanVar(value=True)
    cluster_feature_vars[feat] = var
    tk.Checkbutton(cluster_feat_frame, text=feat.capitalize(), variable=var).pack(anchor="w", padx=10) # Construct check buttons dynamically for geometric calculations

mode_frame = tk.LabelFrame(cluster_options_tab, text="Clustering Mode") # Group box component for user options boundary layout
mode_frame.pack(fill="x", padx=20, pady=5)
tk.Radiobutton(mode_frame, text="Automatic Clustering", variable=cluster_mode_var, value="auto").pack(anchor="w", padx=10)
tk.Radiobutton(mode_frame, text="Specify Number of Clusters", variable=cluster_mode_var, value="manual").pack(anchor="w", padx=10)
num_clusters_entry = tk.Entry(mode_frame, width=5) # Data entry field to specify k-means clusters manually
num_clusters_entry.insert(0, "4") # Initialize layout input box with an integer fallback
num_clusters_entry.pack(anchor="w", padx=30, pady=(0, 4))


# ── Well Selection sub-tab ──────────────────

# CHANGED: Switched title label configuration to grid to avoid blending layout managers
tk.Label(well_select_tab, text="Select Wells to Plot",
         font=("Courier", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(8, 4), sticky="w")

ws_canvas = tk.Canvas(well_select_tab, height=340)
ws_scrollbar = tk.Scrollbar(well_select_tab, orient="vertical", command=ws_canvas.yview)
ws_frame = tk.Frame(ws_canvas)

# CHANGED: Use grid configuration to pack the canvas and scrollbar dynamically inside well_select_tab
ws_canvas.grid(row=1, column=0, sticky="nsew", padx=(6, 0))
ws_scrollbar.grid(row=1, column=1, sticky="ns")

ws_frame.bind("<Configure>", lambda e: ws_canvas.configure(scrollregion=ws_canvas.bbox("all")))

# CHANGED: Capture the window configuration mapping element id to programmatically stretch it on resize
canvas_window = ws_canvas.create_window((0, 0), window=ws_frame, anchor="nw")

# CHANGED: Explicitly force the checkbox layout grid frame to match full canvas sizing during full-screen switches
def _configure_canvas_width(event):
    ws_canvas.itemconfig(canvas_window, width=event.width)
ws_canvas.bind("<Configure>", _configure_canvas_width)

ws_canvas.configure(yscrollcommand=ws_scrollbar.set)
well_vars = {}

# "Select All" checkbox
select_all_var = tk.BooleanVar(value=False)

def plot_well_history():
    """
    Desc: Generates plots of OD and RFU values over rounds for each well with valid data.

    Pre:
    - well_history must be populated with OD and RFU lists.

    Post:
    - A matplotlib plot is displayed for each well containing non-zero data.
    """

    for well, history in well_history.items():

        # Skip wells with no meaningful data
        if not (any(v != 0 for v in history["od"]) or any(v != 0 for v in history["rfu"])):
            continue

        rounds = list(range(1, len(history["od"]) + 1))  # X-axis values (round numbers)

        plt.figure(figsize=(6,4))

        plt.plot(rounds, history["od"], marker='o', label="od")  # OD curve
        plt.plot(rounds, history["rfu"], marker='x', label='rfu')  # RFU curve

        plt.title(f"Well {well} ({history['promoter']} | {history['ahl']})")
        plt.xlabel("Round")
        plt.ylabel("Value")
        plt.legend()

        plt.show()  # Display plot


def trim_empties(values):
    """
    Desc: Removes trailing empty or None values from a list.

    Pre:
    - values must be a list.

    Post:
    - List is modified in-place with trailing empty elements removed.
    - Returns the cleaned list.
    """

    while values and (values[-1] == "" or values[-1] is None):
        values.pop()  # Remove last element if empty

    return values  # Return cleaned list

def group_wells_by(field):
    """
    Desc: Constructs a reverse-lookup map (dict) that ties well names to the qualitative variables stored for each well, 
    used with AHL and Promoters.

    Pre: Takes a string-based key to select values to pull from well_history. Currently only used with "ahl" and "promoter" qualitative vars.

    Post: Returns the reverse-lookup map as a dict.
    """
    #groups: reverse-lookup map in question.  
    groups = {}
    #Iterates through all wells in well_history, enumerated with the data values associated with well name keys
    for well, data in well_history.items():
        #Get the qualitative var.
        key = data.get(field)
        #Filter out null variables.
        if key:
            #If the qualitative variable is unique, create a new list for it, otherwise append the well reference to the key in the hash map.
            if key not in groups:
                groups[key] = []
            groups[key].append(well)
    return groups


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
                # CHANGED: Added sticky="nsew" so cells grow dynamically when scaling the grid window
                tk.Checkbutton(ws_frame, text=label_text, variable=var,
                               font=("Courier", 8)
                               ).grid(row=6 + r_i, column=c - 1, padx=2, pady=1, sticky="nsew")

# CHANGED: Added layout grid configuration loops to handle proportional sizing horizontally and vertically
    # Force the grid columns to distribute horizontal window expansion evenly
    for c_idx in range(columns):
        ws_frame.grid_columnconfigure(c_idx, weight=1)
    # Force the grid rows containing checkboxes to distribute vertical window expansion evenly
    for r_idx in range(len(row_labels)):
        ws_frame.grid_rowconfigure(6 + r_idx, weight=1)

refresh_well_selector()

# ── Standard Graph sub-tab ──────────────────

def _embed_figure(parent, fig):
    """Embed a matplotlib figure into a tkinter frame."""
    canvas_plot = FigureCanvasTkAgg(fig, master=parent)
    canvas_plot.draw()
    canvas_plot.get_tk_widget().pack(fill="both", expand=True)


def show_group_membership(groups):
    """
    Desc: Opens a popup window listing exactly which wells were bucketed into
    each promoter+AHL group, so grouping can be sanity-checked against the
    plate data (e.g. spotting accidental string mismatches like "10nM" vs "10 nM").

    Pre: groups must be a dict mapping (promoter, ahl) tuples to lists of well names.

    Post: Displays a read-only, scrollable Toplevel window with the breakdown.
    """
    membership_win = tk.Toplevel(window)
    membership_win.title("Group Membership")
    membership_win.geometry("480x420")

    text_frame = tk.Frame(membership_win)
    text_frame.pack(fill="both", expand=True, padx=8, pady=8)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    text_box = tk.Text(text_frame, wrap="word", font=("Courier", 9), yscrollcommand=scrollbar.set)
    text_box.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_box.yview)

    for (promoter, ahl), wells_in_group in groups.items():
        text_box.insert("end", f"Promoter: {promoter}   AHL: {ahl}   (n={len(wells_in_group)})\n")
        text_box.insert("end", f"    Wells: {', '.join(sorted(wells_in_group))}\n\n")

    text_box.config(state="disabled")


def select_and_plot_wells():
    """
    Desc: This function is a main for all graphing operations, separated into four broad steps with a final matplotlib graph within a popup window.

    Pre: Presumably uses globals since there are no arguments. Outside of this function a button is needed to call from GUI, done with plot_selected_button below.

    Post: Produces matplotlib figures in windows created and handled within the function.
    """  
    import cluster_plate as cp  # Ensure cluster_plate.py is in the same folder

    selected_wells = [w for w, var in well_vars.items() if var.get()]
    if not selected_wells:
        messagebox.showwarning("No wells selected", "Please select at least one well.")
        return

    # --- Step 4: Standard plotting function (NEW) ---
    def plot_standard(selected_wells, show_legend=True):
        """
        Desc: This function is called by graph_type_popup when the user calls for a standard graph, represented by tk StringVar value "all" when a graphing
        method is chosen by the program. selected_wells is iterated through for to construct lines for each included well via matplotlib's functions 
        and the resulting graph, alongside a legend for each of the lines, is displayed in a GUI to the user. 

        Pre: A dictionary called selected_wells must be passed to this function. It is the dataset we do plt operations on.

        Post: show() calls are made to display the data with a GUI.
        """
        # FIXED: Added explicit global markers here so the local scope safely resolves the Tkinter control flags
        global std_group_by_condition

        show_od = True
        show_rfu = True
        group_by_condition = std_group_by_condition.get()

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

            if std_show_groups_var.get():
                show_group_membership(groups)

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
                    ax1.errorbar(rounds, mean_od, yerr=std_od, marker="o", linestyle="-",
                                 label=f"{lbl} OD", color=color, capsize=4)

                if show_rfu:
                    padded_rfu = [
                        np.pad(well_history[w]["rfu"],
                               (0, max_rounds - len(well_history[w]["rfu"])),
                               constant_values=np.nan)
                        for w in wells_in_group
                    ]
                    mean_rfu = np.nanmean(padded_rfu, axis=0)
                    std_rfu  = np.nanstd(padded_rfu, axis=0)
                    ax2.errorbar(rounds, mean_rfu, yerr=std_rfu, marker="x", linestyle="--",
                                 label=f"{lbl} RFU", color=color, capsize=4)

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

        fig_std.tight_layout()

        _embed_figure(std_tab, fig_std)

        # ── Tab: OD over Rounds (per well) ─────
        if show_od:
            od_tab = ttk.Frame(notebook)
            notebook.add(od_tab, text="  OD — All Wells  ")

            fig_od, ax_od = plt.subplots(figsize=(9, 5))

            if group_by_condition:
                for i, ((promoter, ahl), wells_in_group) in enumerate(groups.items()):
                    lbl = f"{promoter} | AHL={ahl} (n={len(wells_in_group)})"
                    color = colors[i % len(colors)]
                    padded_od = [
                        np.pad(well_history[w]["od"],
                               (0, max_rounds - len(well_history[w]["od"])),
                               constant_values=np.nan)
                        for w in wells_in_group
                    ]
                    mean_od = np.nanmean(padded_od, axis=0)
                    std_od  = np.nanstd(padded_od, axis=0)
                    ax_od.errorbar(rounds, mean_od, yerr=std_od, marker="o", linestyle="-",
                                   label=lbl, color=color, capsize=4)
                ax_od.set_title("OD — Grouped by Promoter + AHL — Mean ± SD")
            else:
                for i, well in enumerate(selected_wells):
                    history = well_history[well]
                    r_vals = list(range(1, len(history["od"]) + 1))
                    ax_od.plot(r_vals, history["od"], marker="o",
                               label=f"{well} ({history['promoter']})",
                               color=colors[i % len(colors)])
                ax_od.set_title("OD — All Selected Wells")

            ax_od.set_xlabel("Round")
            ax_od.set_ylabel("OD")
            fig_od.tight_layout()
            _embed_figure(od_tab, fig_od)

        # ── Tab: RFU over Rounds (per well) ────
        if show_rfu:
            rfu_tab = ttk.Frame(notebook)
            notebook.add(rfu_tab, text="  RFU — All Wells  ")

            fig_rfu, ax_rfu = plt.subplots(figsize=(9, 5))

            if group_by_condition:
                for i, ((promoter, ahl), wells_in_group) in enumerate(groups.items()):
                    lbl = f"{promoter} | AHL={ahl} (n={len(wells_in_group)})"
                    color = colors[i % len(colors)]
                    padded_rfu = [
                        np.pad(well_history[w]["rfu"],
                               (0, max_rounds - len(well_history[w]["rfu"])),
                               constant_values=np.nan)
                        for w in wells_in_group
                    ]
                    mean_rfu = np.nanmean(padded_rfu, axis=0)
                    std_rfu  = np.nanstd(padded_rfu, axis=0)
                    ax_rfu.errorbar(rounds, mean_rfu, yerr=std_rfu, marker="x", linestyle="--",
                                    label=lbl, color=color, capsize=4)
                ax_rfu.set_title("RFU — Grouped by Promoter + AHL — Mean ± SD")
            else:
                for i, well in enumerate(selected_wells):
                    history = well_history[well]
                    r_vals = list(range(1, len(history["rfu"]) + 1))
                    ax_rfu.plot(r_vals, history["rfu"], marker="x", linestyle="--",
                                label=f"{well} ({history['promoter']})",
                                color=colors[i % len(colors)])
                ax_rfu.set_title("RFU — All Selected Wells")

            ax_rfu.set_xlabel("Round")
            ax_rfu.set_ylabel("RFU")
            fig_rfu.tight_layout()
            _embed_figure(rfu_tab, fig_rfu)

        # ── Separate legend window ─────────────
        if show_legend:
            handles1, labels1 = ax1.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels()
            lines = handles1 + handles2
            labels = labels1 + labels2
            legend_fig = plt.figure("Legend Window", figsize=(6, max(4, len(labels) * 0.35)))
            legend_ax = legend_fig.add_subplot(111)
            legend_ax.axis("off")
            ncols = max(1, len(labels) // 15)
            legend_ax.legend(lines, labels, loc="center", ncol=ncols, frameon=True)
            legend_ax.set_title("Legend")
            legend_fig.show()

# CHANGED: Moved the tab checking logic directly under the function definition so it targets plot_standard sequentially
    # Check which sub-tab is currently active under the Analysis section to determine whether to run standard plotting or cluster operations
    active_tab_index = analysis_inner.index(analysis_inner.select()) # Read active notebook frame integer position

    if active_tab_index == 1:
        # User has the 'Standard Graph' sub-tab active, run standard generation routine directly
        plot_standard(selected_wells, show_legend=std_show_legend_var.get())
    elif active_tab_index == 2:
        # User has the 'Cluster Options' sub-tab active, prepare feature dicts and run cluster validation routine directly
        
        # Build active data metric flags from the sub-tab selection state variables
        signals_selected = {"OD": cluster_od_var.get(), "RFU": cluster_rfu_var.get()}
        if not any(signals_selected.values()):
            messagebox.showwarning("No measurement selected", "Select at least OD or RFU in the options tab.")
            return

        # Collect checked computational signal metrics from tracking map objects
        features_selected = [f for f, var in cluster_feature_vars.items() if var.get()]
        if not features_selected:
            messagebox.showwarning("No features selected", "Select at least one feature for clustering in the options tab.")
            return

        # Establish fixed target cluster integer parameters or run adaptive density estimations
        n_clusters = None
        if cluster_mode_var.get() == "manual":
            try:
                n_clusters = int(num_clusters_entry.get())
                if n_clusters < 1: raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid input", "Enter a valid number of clusters in the options tab.")
                return

        # Direct execution of data pipeline mapping vectors into the matplotlib cluster graph frame
        plot_clusters_gui(
            selected_wells=selected_wells,
            features_selected=features_selected,
            signals_selected=signals_selected,
            include_promoter=include_promoter_var.get(),
            include_ahl=include_ahl_var.get(),
            clustering_mode="kmeans" if n_clusters else "auto",
            n_clusters=n_clusters if n_clusters else 4,
            show_legend=show_legend_var.get()
        )
    else:
        # Prompt user to navigate out of the base 'Well Selection' view to evaluate plots
        messagebox.showinfo("Select an Options Tab", "Please select either the 'Standard Graph' or 'Cluster Options' tab to configure your output layout.")

# This is now part of the main window rather than a defined function. If we could somehow reorganize this to not be as out of the way, that would be useful.
# plot_selected_button acts as a way for a user to call select_and_plot_wells from gui.
plot_selected_button = tk.Button(
    analysis_tab,
    text="Plot Selected Wells",
    command=select_and_plot_wells)

# CHANGED: Switched from .pack() to .grid() to align geometry managers and prevent the TclError crash.
# This positions the button directly below the notebook in row 1, and lets it span horizontally.
plot_selected_button.grid(row=1, column=0, pady=10, sticky="ew", padx=10)

def plot_clusters_gui(selected_wells, features_selected, signals_selected,
                      include_promoter=False, include_ahl=False,
                      clustering_mode="kmeans", n_clusters=4, dbscan_eps=0.5, show_legend=True):
    """
    Desc:  

    Pre: For a list of all of the parameters passed to the function, look below in its own section for a description of each.

    Post: Creates a configurable tkinter window that houses a matplotlib canvas_plot displaying the cluster map built by this function.

    Parameters (Included since there's quite a few):
        -selected_wells: Iterable of well identifiers. Specified during go_to_graph_type().
        
        -features_selected: User chooses these during plot_clusters().

        -signals_selected: An iterable of every OD and RFU data point.

        -include_promoter: tk Boolval to include promoter mutants as a clustering factor

        -include_ahl: tk Boolval to include AHL levels as a clustering factor

        -clustering_mode: Clustering algorithm selector ("kmeans", "auto", etc.). kmeans partions observations into a set number of clusters
        specified by n_clusters.

        -n_clusters: Number of clusters for k-means (if applicable). Specified by user in plot_clusters().

        -dbscan_eps: Maximum distance during DBSCAN algorithim that points can be from each other while still being neighbors.
    """
    #cluster plate functions are used specifically for this function.
    import cluster_plate as cp
    from matplotlib.lines import Line2D

    # Ensure all OD/RFU are lists of floating point or string values.
    for w in selected_wells:
        if isinstance(well_history[w]["od"], (float, str)):
            well_history[w]["od"] = [float(well_history[w]["od"])]
        if isinstance(well_history[w]["rfu"], (float, str)):
            well_history[w]["rfu"] = [float(well_history[w]["rfu"])]

    # --- Create plot window ---
    # It should be noted, that compared to plot_standard() this function embeds the matplotlib graphs into tkinter windows, as opposed to using matplotlib's built-in
    # GUI handling.
    plot_window = tk.Toplevel()
    plot_window.title("Clustered Wells Plot")
    # fig is the figure/plot we inevitably show to the user.
    # ax_od is the Y-axis for OD.
    # ax_rfu is the Y-axis for RFU, cloned initially from ax1.
    fig, ax_od = plt.subplots(figsize=(9,6))
    # Our color table is borrowed from matplotlib's built-in color maps, allowing for automatic assignment.
    ax_rfu = ax_od.twinx()
    # color_index simply acts as a way to access the colormap to make datasets look distinct.
    colors = plt.cm.tab10.colors

    max_rounds = max(len(well_history[w]["od"]) for w in selected_wells)
    rounds = list(range(1, max_rounds + 1))

    legend_items = []  # List to collect info for legend.

    # OD clustering
    # It should also be noted that nearly all of the functions from cluster_plate are utilized in these sections.
    if signals_selected.get("OD", False):
        # X_od, labels_od are enumerated returns for the vector features and well labels built by build_feature_matrix.
        X_od, labels_od = cp.build_feature_matrix(well_history,"od",features_selected,selected_wells,include_promoter,include_ahl)
        # od_cluster_ids using the clustering_mode specified, builds a list of cluster features and returns a numpy array reference to each
        od_cluster_ids = cp.cluster_signal(X_od, clustering_mode, n_clusters, dbscan_eps)
        # od_clusters is a dict allowing for labels_od references to return cluster ids. We iterate through this for the next steps.
        od_clusters = cp.build_cluster_map(labels_od, od_cluster_ids)
        for cid, wells in od_clusters.items():
            # First collect time series from the numpy array, stored in mean_od
            mean_od = np.array([well_history[w]["od"] for w in wells], dtype=object)
            # Then get the mean od value, now stored in mean_od
            mean_od = np.mean([np.pad(v, (0, max_rounds - len(v)), 'constant', constant_values=np.nan) for v in mean_od], axis=0)
            # line is used to store the plotting data drawn from the clustering data collected.
            line = ax_od.plot(rounds, mean_od, color=colors[cid % len(colors)],
                              linestyle="-", linewidth=2, label=f"Cluster {cid} OD (n={len(wells)})")
            # Make a legend for each signal. Formatted in the style "Cluster {cluster Id} OD (n={number of clusters})
            legend_items.append((line[0], f"Cluster {cid} OD (n={len(wells)})"))

    # RFU clustering. Copied in structure from OD clustering. We could make this an embedded function called with OD or RFU as a parameter.
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

    # These commands simply set labels for ax_od and ax_rfu that are viewable by the user.
    ax_od.set_xlabel("Round")
    ax_od.set_ylabel("OD")
    ax_rfu.set_ylabel("RFU")
    ax_od.set_title("Clustered Mean OD and RFU Curves")

    # Embed the resultant plot in GUI with FigureCanvasTkAgg, draw it and return it to the window
    canvas_plot = FigureCanvasTkAgg(fig, master=plot_window)
    canvas_plot.draw()
    canvas_plot.get_tk_widget().pack(fill="both", expand=True)

    # --- Create separate legend window ---
    if show_legend:
        # legend_window: popup window with name "Legend"
        legend_window = tk.Toplevel()
        legend_window.title("Legend")
        fig_legend, ax_legend = plt.subplots(figsize=(6, max(4, len(legend_items)*0.35)))
        ax_legend.axis("off")

        # Create dummy lines for legend
        lines = [Line2D([0], [0], color=l.get_color(), linestyle=l.get_linestyle(), linewidth=l.get_linewidth())
                for l, _ in legend_items]
        labels = [label for _, label in legend_items]

        # ncols and next lines center everything based on how many labels are needed
        ncols = max(1, len(labels)//15)
        ax_legend.legend(lines, labels, loc="center", ncol=ncols, frameon=True)
        ax_legend.set_title("Legend")

        # Embed the legend in GUI with FigureCanvasTkAgg, draw it and return it to the window
        canvas_legend = FigureCanvasTkAgg(fig_legend, master=legend_window)
        canvas_legend.draw()
        canvas_legend.get_tk_widget().pack(fill="both", expand=True)

# ─────────────────────────────────────────────
#  START
# ─────────────────────────────────────────────
#Update the program timer for each program execution/tick.
#Potentially may be useful to include delta-time implementation for update_timer()
update_timer()
#Update tkinter's window handling for each program excution/tick.
window.mainloop()